#!/bin/bash
# VACUUM 内存优化基准测试脚本
# 支持 PostgreSQL 16 和 17 对比测试

set -euo pipefail

# 配置
PG16_IMAGE="postgres:16-alpine"
PG17_IMAGE="postgres:17-alpine"
TEST_DB="vacuum_benchmark"
RESULTS_DIR="./results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 测试参数
TABLE_SIZE_GB=${TABLE_SIZE_GB:-100}
DEAD_TUPLE_PERCENT=${DEAD_TUPLE_PERCENT:-50}
BUFFER_LIMITS=("128MB" "256MB" "512MB" "1GB" "2GB")

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 创建结果目录
mkdir -p "$RESULTS_DIR"

# 清理函数
cleanup() {
    log_info "清理 Docker 容器..."
    docker rm -f pg16-benchmark pg17-benchmark 2>/dev/null || true
    docker network rm pg-benchmark-net 2>/dev/null || true
}

trap cleanup EXIT

# 创建 Docker 网络
docker network create pg-benchmark-net 2>/dev/null || true

# 启动 PostgreSQL 容器
start_postgres() {
    local version=$1
    local image=$2
    local container_name="pg${version}-benchmark"
    
    log_info "启动 PostgreSQL $version 容器..."
    
    docker run -d \
        --name "$container_name" \
        --network pg-benchmark-net \
        -e POSTGRES_PASSWORD=benchmark \
        -e POSTGRES_DB="$TEST_DB" \
        -v "$(pwd)/setup.sql:/docker-entrypoint-initdb.d/setup.sql" \
        --shm-size=4g \
        --memory=8g \
        "$image" \
        -c shared_buffers=2GB \
        -c work_mem=256MB \
        -c maintenance_work_mem=1GB \
        -c max_connections=100 \
        -c logging_collector=on \
        -c log_directory='pg_log' \
        -c log_filename='postgresql-%Y-%m-%d_%H%M%S.log' \
        -c log_statement='none' \
        -c log_min_messages=warning \
        -c log_autovacuum_min_duration=0
    
    # 等待 PostgreSQL 启动
    log_info "等待 PostgreSQL $version 启动..."
    until docker exec "$container_name" pg_isready -U postgres > /dev/null 2>&1; do
        sleep 2
    done
    
    log_info "PostgreSQL $version 已就绪"
}

# 获取连接字符串
get_psql_cmd() {
    local version=$1
    echo "docker exec -i pg${version}-benchmark psql -U postgres -d $TEST_DB"
}

# 生成测试数据
generate_data() {
    local version=$1
    local psql_cmd=$(get_psql_cmd $version)
    
    log_info "PG $version: 生成 $TABLE_SIZE_GB GB 测试数据..."
    
    local start_time=$(date +%s)
    
    # 使用 SQL 生成数据
    $psql_cmd << EOF
\set ON_ERROR_STOP on
SELECT * FROM generate_test_data('large_test_table', $TABLE_SIZE_GB, 10000);
EOF
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "PG $version: 数据生成完成，耗时: ${duration} 秒"
    echo "data_generation_seconds=$duration" >> "$RESULTS_DIR/pg${version}_${TIMESTAMP}.txt"
}

# 创建 dead tuples
create_dead_tuples() {
    local version=$1
    local psql_cmd=$(get_psql_cmd $version)
    
    log_info "PG $version: 创建 $DEAD_TUPLE_PERCENT% dead tuples..."
    
    local start_time=$(date +%s)
    
    $psql_cmd << EOF
\set ON_ERROR_STOP on
SELECT create_dead_tuples('large_test_table', $DEAD_TUPLE_PERCENT);
SELECT * FROM get_table_info('large_test_table');
EOF
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "PG $version: Dead tuples 创建完成，耗时: ${duration} 秒"
    echo "dead_tuple_creation_seconds=$duration" >> "$RESULTS_DIR/pg${version}_${TIMESTAMP}.txt"
}

# 运行 VACUUM 测试
run_vacuum_test() {
    local version=$1
    local buffer_limit=$2
    local psql_cmd=$(get_psql_cmd $version)
    local container_name="pg${version}-benchmark"
    
    log_info "PG $version: 测试 vacuum_buffer_usage_limit=$buffer_limit"
    
    # 设置参数
    if [ "$version" -eq 17 ]; then
        docker exec "$container_name" psql -U postgres -c "ALTER SYSTEM SET vacuum_buffer_usage_limit = '$buffer_limit';"
        docker exec "$container_name" psql -U postgres -c "SELECT pg_reload_conf();"
    fi
    
    # 记录开始前的统计信息
    local start_stats=$($psql_cmd -tAc "SELECT jsonb_build_object(
        'table_size', pg_total_relation_size('large_test_table'),
        'dead_tuples', n_dead_tup,
        'live_tuples', n_live_tup
    ) FROM pg_stat_user_tables WHERE relname = 'large_test_table';")
    
    # 记录系统资源使用
    local start_mem=$(docker stats --no-stream --format "{{.MemUsage}}" "$container_name" | awk '{print $1}')
    
    # 运行 VACUUM VERBOSE
    local start_time=$(date +%s.%N)
    
    local vacuum_output=$($psql_cmd << EOF
\set ON_ERROR_STOP on
\timing on
VACUUM (VERBOSE, ANALYZE) large_test_table;
EOF
)
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    # 记录结束后的统计信息
    local end_mem=$(docker stats --no-stream --format "{{.MemUsage}}" "$container_name" | awk '{print $1}')
    local end_stats=$($psql_cmd -tAc "SELECT jsonb_build_object(
        'table_size', pg_total_relation_size('large_test_table'),
        'dead_tuples', n_dead_tup,
        'live_tuples', n_live_tup
    ) FROM pg_stat_user_tables WHERE relname = 'large_test_table';")
    
    # 获取 WAL 使用情况 (PG16+)
    local wal_bytes=$($psql_cmd -tAc "
        SELECT COALESCE(sum(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)), 0) 
        FROM pg_replication_slots;
    " 2>/dev/null || echo "N/A")
    
    # 保存结果
    local result_file="$RESULTS_DIR/pg${version}_${buffer_limit}_${TIMESTAMP}.json"
    cat > "$result_file" << EOF
{
    "version": $version,
    "buffer_limit": "$buffer_limit",
    "timestamp": "$TIMESTAMP",
    "table_size_gb": $TABLE_SIZE_GB,
    "dead_tuple_percent": $DEAD_TUPLE_PERCENT,
    "duration_seconds": $duration,
    "start_stats": $start_stats,
    "end_stats": $end_stats,
    "start_memory": "$start_mem",
    "end_memory": "$end_mem",
    "wal_bytes": "$wal_bytes",
    "vacuum_output": $(echo "$vacuum_output" | jq -R -s .)
}
EOF
    
    log_info "PG $version: VACUUM 完成，耗时: ${duration} 秒"
    echo "vacuum_${buffer_limit}_seconds=$duration" >> "$RESULTS_DIR/pg${version}_${TIMESTAMP}.txt"
}

# 运行单次完整测试
run_full_test() {
    local version=$1
    local iteration=$2
    
    log_info "========================================"
    log_info "开始 PG $version 第 $iteration 轮测试"
    log_info "========================================"
    
    # 清理并重新启动容器
    docker rm -f pg${version}-benchmark 2>/dev/null || true
    start_postgres $version $(eval echo "\$PG${version}_IMAGE")
    
    local psql_cmd=$(get_psql_cmd $version)
    
    # 等待数据库完全就绪
    sleep 5
    
    # 生成数据
    generate_data $version
    
    # 创建 dead tuples
    create_dead_tuples $version
    
    # 对于 PG17，测试不同 buffer limit
    if [ "$version" -eq 17 ]; then
        for limit in "${BUFFER_LIMITS[@]}"; do
            # 重新创建数据
            $psql_cmd -c "DROP TABLE IF EXISTS large_test_table CASCADE;"
            generate_data $version
            create_dead_tuples $version
            run_vacuum_test $version "$limit"
        done
    else
        # PG16 只运行一次基准测试
        run_vacuum_test $version "default"
    fi
    
    # 停止容器
    docker rm -f pg${version}-benchmark 2>/dev/null || true
}

# 生成对比报告
generate_report() {
    log_info "生成对比报告..."
    
    local report_file="$RESULTS_DIR/BENCHMARK_REPORT_${TIMESTAMP}.md"
    
    cat > "$report_file" << 'EOF'
# VACUUM 内存优化基准测试报告

## 测试环境

- 测试时间: TIMESTAMP
- PG16 镜像: PG16_IMAGE
- PG17 镜像: PG17_IMAGE
- 测试表大小: TABLE_SIZE_GB GB
- Dead Tuple 比例: DEAD_TUPLE_PERCENT%

## 测试结果汇总

EOF
    
    # 替换变量
    sed -i "s/TIMESTAMP/$TIMESTAMP/g" "$report_file"
    sed -i "s/PG16_IMAGE/$PG16_IMAGE/g" "$report_file"
    sed -i "s/PG17_IMAGE/$PG17_IMAGE/g" "$report_file"
    sed -i "s/TABLE_SIZE_GB/$TABLE_SIZE_GB/g" "$report_file"
    sed -i "s/DEAD_TUPLE_PERCENT/$DEAD_TUPLE_PERCENT/g" "$report_file"
    
    # 添加所有结果文件的内容
    echo "" >> "$report_file"
    echo "## 详细结果" >> "$report_file"
    echo "" >> "$report_file"
    echo "```" >> "$report_file"
    cat $RESULTS_DIR/pg16_${TIMESTAMP}.txt $RESULTS_DIR/pg17_${TIMESTAMP}.txt 2>/dev/null >> "$report_file" || true
    echo "```" >> "$report_file"
    
    log_info "报告已保存至: $report_file"
}

# 主函数
main() {
    log_info "VACUUM 内存优化基准测试开始"
    log_info "测试表大小: ${TABLE_SIZE_GB}GB, Dead Tuples: ${DEAD_TUPLE_PERCENT}%"
    
    # 检查依赖
    command -v docker >/dev/null 2>&1 || { log_error "需要 Docker 但未安装"; exit 1; }
    command -v jq >/dev/null 2>&1 || { log_warn "建议安装 jq 以便更好地处理 JSON 结果"; }
    
    # 清理旧容器
    cleanup
    
    # 运行测试迭代
    local iterations=${1:-1}
    
    for i in $(seq 1 $iterations); do
        log_info "开始第 $i/$iterations 轮测试"
        
        # 先测试 PG16
        run_full_test 16 $i
        
        # 再测试 PG17
        run_full_test 17 $i
    done
    
    # 生成报告
    generate_report
    
    log_info "测试完成！结果保存在: $RESULTS_DIR"
}

# 运行
main "$@"
