#!/bin/bash
# PostgreSQL MVCC性能测试脚本
# 测试不同隔离级别下的性能表现
# 版本: PostgreSQL 17 & 18

set -e

# 配置参数
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-postgres}"
DB_USER="${DB_USER:-postgres}"
CONCURRENT_USERS="${CONCURRENT_USERS:-10}"
TEST_DURATION="${TEST_DURATION:-60}"
ISOLATION_LEVEL="${ISOLATION_LEVEL:-READ COMMITTED}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}PostgreSQL MVCC性能测试${NC}"
echo "=================================="
echo "数据库: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
echo "并发用户: ${CONCURRENT_USERS}"
echo "测试时长: ${TEST_DURATION}秒"
echo "隔离级别: ${ISOLATION_LEVEL}"
echo "=================================="

# 创建测试表
create_test_table() {
    echo -e "${YELLOW}创建测试表...${NC}"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
CREATE TABLE IF NOT EXISTS perf_test (
    id SERIAL PRIMARY KEY,
    value INT NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
) WITH (fillfactor = 80);

CREATE INDEX IF NOT EXISTS idx_perf_test_status ON perf_test(status);
CREATE INDEX IF NOT EXISTS idx_perf_test_value ON perf_test(value);
EOF
}

# 初始化测试数据
init_test_data() {
    echo -e "${YELLOW}初始化测试数据...${NC}"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
TRUNCATE TABLE perf_test;
INSERT INTO perf_test (value) 
SELECT generate_series(1, 10000);
EOF
}

# 吞吐量测试
throughput_test() {
    echo -e "${YELLOW}吞吐量测试...${NC}"
    
    # 创建测试SQL文件
    cat > /tmp/throughput_test.sql <<EOF
SET TRANSACTION ISOLATION LEVEL ${ISOLATION_LEVEL};
BEGIN;
UPDATE perf_test SET value = value + 1, updated_at = NOW() WHERE id = (random() * 10000)::int + 1;
COMMIT;
EOF
    
    # 运行pgbench
    pgbench -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -c "$CONCURRENT_USERS" \
        -T "$TEST_DURATION" \
        -f /tmp/throughput_test.sql \
        -r \
        -P 5
    
    echo -e "${GREEN}吞吐量测试完成${NC}"
}

# 延迟测试
latency_test() {
    echo -e "${YELLOW}延迟测试...${NC}"
    
    # 创建测试SQL文件
    cat > /tmp/latency_test.sql <<EOF
SET TRANSACTION ISOLATION LEVEL ${ISOLATION_LEVEL};
BEGIN;
SELECT * FROM perf_test WHERE id = (random() * 10000)::int + 1;
UPDATE perf_test SET value = value + 1 WHERE id = (random() * 10000)::int + 1;
COMMIT;
EOF
    
    # 运行pgbench（单用户）
    pgbench -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -c 1 \
        -T "$TEST_DURATION" \
        -f /tmp/latency_test.sql \
        -r \
        -P 5
    
    echo -e "${GREEN}延迟测试完成${NC}"
}

# 并发测试
concurrency_test() {
    echo -e "${YELLOW}并发测试...${NC}"
    
    # 创建测试SQL文件
    cat > /tmp/concurrency_test.sql <<EOF
SET TRANSACTION ISOLATION LEVEL ${ISOLATION_LEVEL};
BEGIN;
SELECT COUNT(*) FROM perf_test WHERE status = 'active';
UPDATE perf_test SET status = 'updated' WHERE id = (random() * 10000)::int + 1;
COMMIT;
EOF
    
    # 运行pgbench
    pgbench -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -c "$CONCURRENT_USERS" \
        -T "$TEST_DURATION" \
        -f /tmp/concurrency_test.sql \
        -r \
        -P 5
    
    echo -e "${GREEN}并发测试完成${NC}"
}

# 压力测试
stress_test() {
    echo -e "${YELLOW}压力测试...${NC}"
    
    # 创建测试SQL文件
    cat > /tmp/stress_test.sql <<EOF
SET TRANSACTION ISOLATION LEVEL ${ISOLATION_LEVEL};
BEGIN;
INSERT INTO perf_test (value) VALUES ((random() * 1000000)::int);
UPDATE perf_test SET value = value + 1 WHERE id = (random() * 10000)::int + 1;
DELETE FROM perf_test WHERE id = (random() * 10000)::int + 1;
COMMIT;
EOF
    
    # 运行pgbench（高并发）
    pgbench -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -c $((CONCURRENT_USERS * 2)) \
        -T "$TEST_DURATION" \
        -f /tmp/stress_test.sql \
        -r \
        -P 5
    
    echo -e "${GREEN}压力测试完成${NC}"
}

# HOT更新率测试
hot_update_test() {
    echo -e "${YELLOW}HOT更新率测试...${NC}"
    
    # 创建测试SQL文件（不更新索引列）
    cat > /tmp/hot_update_test.sql <<EOF
SET TRANSACTION ISOLATION LEVEL ${ISOLATION_LEVEL};
BEGIN;
UPDATE perf_test SET value = value + 1 WHERE id = (random() * 10000)::int + 1;
COMMIT;
EOF
    
    # 运行pgbench
    pgbench -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -c "$CONCURRENT_USERS" \
        -T "$TEST_DURATION" \
        -f /tmp/hot_update_test.sql \
        -r \
        -P 5
    
    # 检查HOT更新率
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT 
    schemaname,
    relname,
    n_tup_hot_upd as hot_updates,
    n_tup_upd as total_updates,
    round(n_tup_hot_upd * 100.0 / NULLIF(n_tup_upd, 0), 2) as hot_ratio
FROM pg_stat_user_tables
WHERE relname = 'perf_test';
EOF
    
    echo -e "${GREEN}HOT更新率测试完成${NC}"
}

# 版本链长度测试
version_chain_test() {
    echo -e "${YELLOW}版本链长度测试...${NC}"
    
    # 创建测试表
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
CREATE TABLE IF NOT EXISTS version_chain_test (
    id INT PRIMARY KEY,
    value INT
);

TRUNCATE TABLE version_chain_test;
INSERT INTO version_chain_test (id, value) VALUES (1, 0);
EOF
    
    # 执行多次更新
    for i in {1..1000}; do
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SET TRANSACTION ISOLATION LEVEL ${ISOLATION_LEVEL};
BEGIN;
UPDATE version_chain_test SET value = value + 1 WHERE id = 1;
COMMIT;
EOF
    done
    
    # 检查版本链
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT 
    n_live_tup,
    n_dead_tup,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_ratio
FROM pg_stat_user_tables
WHERE relname = 'version_chain_test';
EOF
    
    echo -e "${GREEN}版本链长度测试完成${NC}"
}

# 主函数
main() {
    create_test_table
    init_test_data
    
    echo ""
    echo -e "${GREEN}开始性能测试...${NC}"
    echo ""
    
    throughput_test
    echo ""
    
    latency_test
    echo ""
    
    concurrency_test
    echo ""
    
    stress_test
    echo ""
    
    hot_update_test
    echo ""
    
    version_chain_test
    echo ""
    
    echo -e "${GREEN}所有性能测试完成！${NC}"
}

# 运行主函数
main "$@"
