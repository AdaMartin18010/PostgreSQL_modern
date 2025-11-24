#!/bin/bash
# PostgreSQL MVCC故障注入脚本
# 模拟各种故障场景，测试MVCC的健壮性
# 版本: PostgreSQL 17 & 18

set -e

# 配置参数
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-postgres}"
DB_USER="${DB_USER:-postgres}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}PostgreSQL MVCC故障注入测试${NC}"
echo "=================================="

# XID回卷模拟
simulate_xid_wraparound() {
    echo -e "${YELLOW}模拟XID回卷...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
-- 检查当前XID年龄
SELECT 
    datname,
    age(datfrozenxid) as xid_age,
    pg_size_pretty(pg_database_size(datname)) as db_size
FROM pg_database
WHERE datname = current_database();

-- 检查表XID年龄
SELECT 
    schemaname,
    relname,
    age(relfrozenxid) as xid_age,
    pg_size_pretty(pg_relation_size(schemaname||'.'||relname)) as table_size
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE relkind = 'r'
ORDER BY age(relfrozenxid) DESC
LIMIT 10;

-- 模拟接近XID回卷（警告阈值：2^31 - 1000000）
-- 注意：实际环境中不要手动修改XID，这里仅用于演示
SELECT 
    CASE 
        WHEN age(datfrozenxid) > 2000000000 THEN 'CRITICAL: XID回卷风险'
        WHEN age(datfrozenxid) > 1000000000 THEN 'WARNING: XID年龄过高'
        ELSE 'OK: XID年龄正常'
    END as xid_status
FROM pg_database
WHERE datname = current_database();
EOF
    
    echo -e "${GREEN}XID回卷模拟完成${NC}"
}

# 表膨胀模拟
simulate_table_bloat() {
    echo -e "${YELLOW}模拟表膨胀...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
-- 创建测试表
CREATE TABLE IF NOT EXISTS bloat_test (
    id SERIAL PRIMARY KEY,
    value INT,
    data TEXT
) WITH (fillfactor = 100);

-- 插入初始数据
TRUNCATE TABLE bloat_test;
INSERT INTO bloat_test (value, data) 
SELECT generate_series(1, 10000), repeat('x', 100);

-- 执行多次更新（产生版本链）
DO \$\$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..1000 LOOP
        UPDATE bloat_test SET value = value + 1 WHERE id = (random() * 10000)::int + 1;
    END LOOP;
END;
\$\$;

-- 检查表膨胀
SELECT 
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_ratio,
    pg_size_pretty(pg_relation_size(schemaname||'.'||relname)) as table_size
FROM pg_stat_user_tables
WHERE relname = 'bloat_test';

-- 执行VACUUM
VACUUM ANALYZE bloat_test;

-- 再次检查
SELECT 
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_ratio,
    pg_size_pretty(pg_relation_size(schemaname||'.'||relname)) as table_size
FROM pg_stat_user_tables
WHERE relname = 'bloat_test';
EOF
    
    echo -e "${GREEN}表膨胀模拟完成${NC}"
}

# 死锁模拟
simulate_deadlock() {
    echo -e "${YELLOW}模拟死锁...${NC}"
    
    # 创建测试表
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
CREATE TABLE IF NOT EXISTS deadlock_test (
    id INT PRIMARY KEY,
    value INT
);

TRUNCATE TABLE deadlock_test;
INSERT INTO deadlock_test (id, value) VALUES (1, 100), (2, 200);
EOF
    
    # 会话1：锁定id=1，然后尝试锁定id=2
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF &
SESSION1_PID=\$!
EOF
    
    # 会话2：锁定id=2，然后尝试锁定id=1（死锁）
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF &
SESSION2_PID=\$!
EOF
    
    echo -e "${YELLOW}死锁检测中...${NC}"
    sleep 5
    
    # 检查死锁统计
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT 
    datname,
    deadlocks
FROM pg_stat_database
WHERE datname = current_database();
EOF
    
    echo -e "${GREEN}死锁模拟完成${NC}"
}

# 长事务模拟
simulate_long_transaction() {
    echo -e "${YELLOW}模拟长事务...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
-- 创建测试表
CREATE TABLE IF NOT EXISTS long_trans_test (
    id SERIAL PRIMARY KEY,
    value INT
);

TRUNCATE TABLE long_trans_test;
INSERT INTO long_trans_test (value) VALUES (1);

-- 开始长事务
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM long_trans_test;

-- 在另一个会话中更新数据
-- 然后检查长事务的影响

-- 检查长事务
SELECT 
    pid,
    usename,
    datname,
    state,
    query_start,
    now() - query_start as duration,
    query
FROM pg_stat_activity
WHERE state = 'active'
  AND query NOT LIKE '%pg_stat_activity%'
ORDER BY query_start;
EOF
    
    echo -e "${GREEN}长事务模拟完成${NC}"
}

# 锁等待模拟
simulate_lock_wait() {
    echo -e "${YELLOW}模拟锁等待...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
-- 创建测试表
CREATE TABLE IF NOT EXISTS lock_wait_test (
    id INT PRIMARY KEY,
    value INT
);

TRUNCATE TABLE lock_wait_test;
INSERT INTO lock_wait_test (id, value) VALUES (1, 100);

-- 检查锁等待
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
EOF
    
    echo -e "${GREEN}锁等待模拟完成${NC}"
}

# 版本链过长模拟
simulate_long_version_chain() {
    echo -e "${YELLOW}模拟版本链过长...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
-- 创建测试表
CREATE TABLE IF NOT EXISTS version_chain_test (
    id INT PRIMARY KEY,
    value INT
) WITH (fillfactor = 100);

TRUNCATE TABLE version_chain_test;
INSERT INTO version_chain_test (id, value) VALUES (1, 0);

-- 执行大量更新（产生长版本链）
DO \$\$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..10000 LOOP
        UPDATE version_chain_test SET value = value + 1 WHERE id = 1;
    END LOOP;
END;
\$\$;

-- 检查版本链
SELECT 
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_ratio
FROM pg_stat_user_tables
WHERE relname = 'version_chain_test';

-- 检查索引膨胀
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE tablename = 'version_chain_test';
EOF
    
    echo -e "${GREEN}版本链过长模拟完成${NC}"
}

# 主函数
main() {
    echo ""
    simulate_xid_wraparound
    echo ""
    
    simulate_table_bloat
    echo ""
    
    simulate_deadlock
    echo ""
    
    simulate_long_transaction
    echo ""
    
    simulate_lock_wait
    echo ""
    
    simulate_long_version_chain
    echo ""
    
    echo -e "${GREEN}所有故障注入测试完成！${NC}"
}

# 运行主函数
main "$@"
