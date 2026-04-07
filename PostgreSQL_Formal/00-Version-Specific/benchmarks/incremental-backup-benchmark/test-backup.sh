#!/bin/bash
# 增量备份基准测试脚本
# 测试 PostgreSQL 17 增量备份性能

set -euo pipefail

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/results"
DATA_DIR="${SCRIPT_DIR}/data"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 测试参数
DB_SIZE_GB=${DB_SIZE_GB:-100}
CHANGE_PERCENTS=${CHANGE_PERCENTS:-"5 10 20"}
ITERATIONS=${ITERATIONS:-3}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_section() {
    echo -e "${BLUE}[SECTION]${NC} $1"
    echo "========================================"
}

# 初始化目录
init_directories() {
    mkdir -p "$RESULTS_DIR" "$DATA_DIR/pg_data" "$DATA_DIR/backup"
    chmod 777 "$DATA_DIR/pg_data" "$DATA_DIR/backup" 2>/dev/null || true
}

# 检查 Docker 环境
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker 守护进程未运行"
        exit 1
    fi
    
    log_info "Docker 环境检查通过"
}

# 启动测试环境
start_environment() {
    log_section "启动测试环境"
    
    cd "$SCRIPT_DIR"
    docker-compose down -v 2>/dev/null || true
    docker-compose up -d postgres-primary
    
    # 等待 PostgreSQL 启动
    log_info "等待 PostgreSQL 启动..."
    local retries=30
    while [ $retries -gt 0 ]; do
        if docker exec pg17-backup-test pg_isready -U postgres > /dev/null 2>&1; then
            log_info "PostgreSQL 已就绪"
            return 0
        fi
        sleep 2
        ((retries--))
    done
    
    log_error "PostgreSQL 启动超时"
    exit 1
}

# 生成测试数据
generate_test_data() {
    local target_gb=$1
    log_section "生成测试数据: ${target_gb}GB"
    
    # 估算每行约 2KB，计算需要的行数
    local target_rows=$((target_gb * 1024 * 1024 / 2))
    
    log_info "目标行数: $target_rows"
    
    local start_time=$(date +%s)
    docker exec -i pg17-backup-test psql -U postgres -d backup_test << EOF
SELECT generate_random_data($target_rows);
SELECT * FROM get_database_info();
EOF
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "数据生成完成，耗时: $duration 秒"
    echo "$duration" > "$RESULTS_DIR/data_gen_time_${target_gb}gb.txt"
}

# 初始化 pgBackRest
init_pgbackrest() {
    log_section "初始化 pgBackRest"
    
    # 创建 pgBackRest 存储目录
    docker exec pg17-backup-test mkdir -p /backup/log /backup/archive
    
    # 初始化 stanza
    docker exec pg17-backup-test pgbackrest --stanza=demo stanza-create 2>/dev/null || true
    
    log_info "pgBackRest 初始化完成"
}

# 执行全量备份
run_full_backup() {
    log_section "执行全量备份"
    
    # 记录备份前状态
    local db_info=$(docker exec pg17-backup-test psql -U postgres -d backup_test -tAc "SELECT * FROM get_database_info();")
    log_info "备份前数据库状态: $db_info"
    
    local start_time=$(date +%s.%N)
    
    # 执行备份
    docker exec pg17-backup-test pgbackrest --stanza=demo backup \
        --type=full \
        --log-level-console=info 2>&1 | tee "$RESULTS_DIR/full_backup_${TIMESTAMP}.log"
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    # 获取备份大小
    local backup_size=$(docker exec pg17-backup-test du -sh /backup | cut -f1)
    
    log_info "全量备份完成，耗时: $duration 秒，大小: $backup_size"
    
    # 记录结果
    cat > "$RESULTS_DIR/full_backup_${TIMESTAMP}.json" << EOF
{
    "backup_type": "full",
    "timestamp": "$TIMESTAMP",
    "duration_seconds": $duration,
    "backup_size": "$backup_size",
    "database_info": "$db_info"
}
EOF
    
    echo "$duration" > "$RESULTS_DIR/full_backup_time.txt"
    echo "$backup_size" > "$RESULTS_DIR/full_backup_size.txt"
}

# 模拟数据变化
simulate_changes() {
    local percent=$1
    log_section "模拟 ${percent}% 数据变化"
    
    local start_time=$(date +%s)
    
    docker exec -i pg17-backup-test psql -U postgres -d backup_test << EOF
SELECT * FROM simulate_data_changes($percent);
SELECT * FROM get_database_info();
SELECT force_checkpoint();
EOF
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "数据变化模拟完成，耗时: $duration 秒"
    echo "$duration" > "$RESULTS_DIR/change_sim_time_${percent}pct.txt"
}

# 执行增量备份
run_incremental_backup() {
    local change_percent=$1
    log_section "执行增量备份 (${change_percent}% 变化)"
    
    local start_time=$(date +%s.%N)
    
    docker exec pg17-backup-test pgbackrest --stanza=demo backup \
        --type=incr \
        --log-level-console=info 2>&1 | tee "$RESULTS_DIR/incr_backup_${change_percent}pct_${TIMESTAMP}.log"
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    # 获取备份大小
    local backup_info=$(docker exec pg17-backup-test pgbackrest --stanza=demo info --output=json)
    
    log_info "增量备份完成，耗时: $duration 秒"
    
    # 记录结果
    cat > "$RESULTS_DIR/incr_backup_${change_percent}pct_${TIMESTAMP}.json" << EOF
{
    "backup_type": "incremental",
    "change_percent": $change_percent,
    "timestamp": "$TIMESTAMP",
    "duration_seconds": $duration,
    "backup_info": $backup_info
}
EOF
    
    echo "$duration" > "$RESULTS_DIR/incr_backup_time_${change_percent}pct.txt"
}

# 测试恢复性能
test_restore() {
    local backup_type=$1
    log_section "测试恢复性能: $backup_type"
    
    # 创建恢复目录
    mkdir -p "$DATA_DIR/restore_${backup_type}"
    
    local start_time=$(date +%s.%N)
    
    # 执行恢复
    docker exec pg17-backup-test pgbackrest --stanza=demo restore \
        --delta \
        --log-level-console=info 2>&1 | tee "$RESULTS_DIR/restore_${backup_type}_${TIMESTAMP}.log"
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    log_info "恢复完成，耗时: $duration 秒"
    
    cat > "$RESULTS_DIR/restore_${backup_type}_${TIMESTAMP}.json" << EOF
{
    "restore_type": "$backup_type",
    "timestamp": "$TIMESTAMP",
    "duration_seconds": $duration
}
EOF
    
    echo "$duration" > "$RESULTS_DIR/restore_time_${backup_type}.txt"
}

# 收集系统指标
collect_metrics() {
    log_section "收集系统指标"
    
    # 容器资源使用
    docker stats --no-stream pg17-backup-test > "$RESULTS_DIR/container_stats_${TIMESTAMP}.txt"
    
    # 数据库统计
    docker exec pg17-backup-test psql -U postgres -d backup_test << EOF > "$RESULTS_DIR/db_stats_${TIMESTAMP}.txt"
SELECT * FROM get_database_info();
SELECT * FROM backup_stats;
SELECT * FROM data_changes ORDER BY changed_at DESC LIMIT 10;
EOF
    
    log_info "系统指标收集完成"
}

# 生成报告
generate_report() {
    log_section "生成测试报告"
    
    local report_file="$RESULTS_DIR/BENCHMARK_REPORT_${TIMESTAMP}.md"
    
    cat > "$report_file" << EOF
# PostgreSQL 17 增量备份基准测试报告

## 测试概况

- 测试时间: $(date)
- 数据库大小: ${DB_SIZE_GB}GB
- 测试场景: 5%, 10%, 20% 数据变化
- 迭代次数: $ITERATIONS

## 测试结果汇总

### 1. 全量备份

| 指标 | 数值 |
|------|------|
| 备份时间 | $(cat $RESULTS_DIR/full_backup_time.txt 2>/dev/null || echo "N/A") 秒 |
| 备份大小 | $(cat $RESULTS_DIR/full_backup_size.txt 2>/dev/null || echo "N/A") |

### 2. 增量备份对比

| 数据变化 | 备份时间 | 相对于全量 | 备份大小 | 效率提升 |
|----------|----------|------------|----------|----------|
| 5% | $(cat $RESULTS_DIR/incr_backup_time_5pct.txt 2>/dev/null || echo "N/A") 秒 | - | - | - |
| 10% | $(cat $RESULTS_DIR/incr_backup_time_10pct.txt 2>/dev/null || echo "N/A") 秒 | - | - | - |
| 20% | $(cat $RESULTS_DIR/incr_backup_time_20pct.txt 2>/dev/null || echo "N/A") 秒 | - | - | - |

### 3. 恢复性能

| 恢复类型 | 恢复时间 |
|----------|----------|
| 全量恢复 | $(cat $RESULTS_DIR/restore_time_full.txt 2>/dev/null || echo "N/A") 秒 |
| 增量恢复 | $(cat $RESULTS_DIR/restore_time_incremental.txt 2>/dev/null || echo "N/A") 秒 |

## 详细日志

- 全量备份日志: full_backup_${TIMESTAMP}.log
- 增量备份日志: incr_backup_*pct_${TIMESTAMP}.log
- 恢复日志: restore_*_${TIMESTAMP}.log
- 容器统计: container_stats_${TIMESTAMP}.txt
- 数据库统计: db_stats_${TIMESTAMP}.txt

## 结论与建议

1. **备份时间**: 
2. **存储效率**: 
3. **恢复速度**: 
4. **最佳实践**: 
EOF
    
    log_info "报告已生成: $report_file"
}

# 清理环境
cleanup() {
    log_section "清理环境"
    cd "$SCRIPT_DIR"
    docker-compose down -v 2>/dev/null || true
    log_info "清理完成"
}

# 主测试流程
run_benchmark() {
    local iteration=$1
    log_section "开始第 $iteration 轮测试"
    
    # 启动环境
    start_environment
    
    # 初始化 pgBackRest
    init_pgbackrest
    
    # 生成测试数据
    generate_test_data $DB_SIZE_GB
    
    # 执行全量备份
    run_full_backup
    
    # 测试不同变化量的增量备份
    for percent in $CHANGE_PERCENTS; do
        # 模拟数据变化
        simulate_changes $percent
        
        # 执行增量备份
        run_incremental_backup $percent
    done
    
    # 收集指标
    collect_metrics
    
    # 可选: 测试恢复性能
    # test_restore "full"
    
    # 清理
    cleanup
}

# 主函数
main() {
    log_section "PostgreSQL 17 增量备份基准测试"
    
    # 初始化
    init_directories
    check_docker
    
    # 运行多轮测试
    for i in $(seq 1 $ITERATIONS); do
        run_benchmark $i
    done
    
    # 生成报告
    generate_report
    
    log_section "测试完成!"
    log_info "结果保存在: $RESULTS_DIR"
}

# 信号处理
trap cleanup EXIT

# 运行主函数
main "$@"
