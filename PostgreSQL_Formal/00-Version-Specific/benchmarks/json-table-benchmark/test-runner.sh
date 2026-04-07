#!/bin/bash
# JSON_TABLE 性能基准测试运行脚本

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%H:%M:%S') - $1"
}

log_section() {
    echo -e "\n${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}\n"
}

# 初始化
init() {
    mkdir -p "$RESULTS_DIR"
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker 未安装${NC}"
        exit 1
    fi
}

# 启动环境
start_environment() {
    log_section "启动测试环境"
    
    cd "$SCRIPT_DIR"
    
    # 停止旧容器
    docker-compose down 2>/dev/null || true
    
    # 启动新容器
    docker-compose up -d
    
    # 等待 PostgreSQL 就绪
    log_info "等待 PostgreSQL 启动..."
    local retries=30
    while [ $retries -gt 0 ]; do
        if docker exec pg17-json-test pg_isready -U postgres > /dev/null 2>&1; then
            log_info "PostgreSQL 已就绪!"
            return 0
        fi
        sleep 2
        ((retries--))
    done
    
    echo -e "${RED}错误: PostgreSQL 启动超时${NC}"
    exit 1
}

# 运行基准测试
run_benchmark() {
    log_section "运行基准测试"
    
    log_info "执行 benchmark.sql..."
    
    # 运行基准测试 SQL
    docker exec -i pg17-json-test psql -U postgres -d json_benchmark < "$SCRIPT_DIR/benchmark.sql" 2>&1 | tee "$RESULTS_DIR/benchmark_${TIMESTAMP}.log"
    
    log_info "基准测试完成"
}

# 收集额外统计信息
collect_stats() {
    log_section "收集额外统计信息"
    
    log_info "收集数据库统计..."
    
    docker exec -i pg17-json-test psql -U postgres -d json_benchmark << EOF > "$RESULTS_DIR/db_stats_${TIMESTAMP}.txt"
-- 数据库信息
SELECT * FROM get_db_info();

-- 表统计
SELECT 
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size
FROM pg_stat_user_tables
WHERE relname LIKE 'json_test%';

-- 测试结果汇总
SELECT 
    method,
    complexity,
    row_count,
    COUNT(*) as test_count,
    ROUND(AVG(execution_time_ms), 2) as avg_exec_time_ms,
    ROUND(MIN(execution_time_ms), 2) as min_exec_time_ms,
    ROUND(MAX(execution_time_ms), 2) as max_exec_time_ms
FROM benchmark_results
GROUP BY method, complexity, row_count
ORDER BY complexity, row_count, method;
EOF
    
    log_info "统计信息已保存"
}

# 生成 Markdown 报告
generate_report() {
    log_section "生成测试报告"
    
    local report_file="$RESULTS_DIR/JSON_TABLE_BENCHMARK_REPORT_${TIMESTAMP}.md"
    
    cat > "$report_file" << 'EOF'
# JSON_TABLE 性能基准测试报告

## 测试概况

- **测试时间**: TIMESTAMP_PLACEHOLDER
- **PostgreSQL 版本**: 17.x
- **测试环境**: Docker

## 硬件配置

| 组件 | 配置 |
|------|------|
| CPU | Docker 宿主机可用核心 |
| 内存 | 4GB (容器限制) |
| 存储 | Docker 卷 |

## 数据库配置

| 参数 | 值 |
|------|-----|
| shared_buffers | 2GB |
| work_mem | 256MB |
| max_connections | 100 |

## 测试结果汇总

### 1. 简单 JSON 性能对比

| 数据量 | jsonb_to_recordset | JSON_TABLE | 性能提升 |
|--------|-------------------|------------|----------|
| 1K     | -- ms | -- ms | --% |
| 10K    | -- ms | -- ms | --% |
| 100K   | -- ms | -- ms | --% |

### 2. 中等复杂度 JSON

| 数据量 | 传统方法 | JSON_TABLE | 性能提升 |
|--------|----------|------------|----------|
| 1K     | -- ms | -- ms | --% |
| 10K    | -- ms | -- ms | --% |

### 3. 复杂嵌套 JSON

| 数据量 | 手动路径 | JSON_TABLE | 性能提升 |
|--------|----------|------------|----------|
| 1K     | -- ms | -- ms | --% |
| 10K    | -- ms | -- ms | --% |

### 4. 嵌套数组展开

| 数据量 | jsonb_to_recordset | JSON_TABLE (NESTED) | 性能提升 |
|--------|-------------------|---------------------|----------|
| 1K     | -- ms | -- ms | --% |

## 原始数据

详细测试结果保存在:
- `results/benchmark_TIMESTAMP_PLACEHOLDER.log`
- `results/db_stats_TIMESTAMP_PLACEHOLDER.txt`
- `results/benchmark_data.csv`

## 结论

1. **简单 JSON**: JSON_TABLE 相比 jsonb_to_recordset 性能提升约 XX%
2. **嵌套 JSON**: JSON_TABLE 语法更简洁，性能差异 XX%
3. **数组展开**: NESTED PATH 功能强大，适合处理复杂嵌套结构
4. **推荐使用场景**: 
   - 需要标准 SQL 语法的场景
   - 处理复杂嵌套 JSON
   - 需要 ERROR/NULL ON ERROR 处理的场景

## 参考

- PostgreSQL 17 文档: https://www.postgresql.org/docs/17/functions-json.html
- SQL:2016 JSON_TABLE 标准
EOF
    
    # 替换时间戳
    sed -i "s/TIMESTAMP_PLACEHOLDER/$TIMESTAMP/g" "$report_file"
    
    log_info "报告已生成: $report_file"
}

# 清理环境
cleanup() {
    log_section "清理环境"
    cd "$SCRIPT_DIR"
    docker-compose down
    log_info "环境已清理"
}

# 主函数
main() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║       JSON_TABLE 性能基准测试 - PostgreSQL 17                ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    
    init
    start_environment
    run_benchmark
    collect_stats
    generate_report
    
    log_section "测试完成!"
    log_info "所有结果保存在: $RESULTS_DIR"
    log_info "测试报告: JSON_TABLE_BENCHMARK_REPORT_${TIMESTAMP}.md"
}

# 捕获信号进行清理
trap cleanup EXIT INT TERM

# 运行
main "$@"
