#!/bin/bash
# PostgreSQL MVCC锁监控脚本
# 监控锁状态、锁等待、死锁等
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

echo -e "${GREEN}PostgreSQL MVCC锁监控${NC}"
echo "=================================="

# 监控所有锁
monitor_all_locks() {
    echo -e "${YELLOW}所有锁监控...${NC}"

    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT
    locktype,
    database,
    relation::regclass,
    page,
    tuple,
    virtualxid,
    transactionid,
    classid,
    objid,
    objsubid,
    virtualtransaction,
    pid,
    mode,
    granted
FROM pg_locks
ORDER BY locktype, granted, pid;
EOF
}

# 监控锁等待
monitor_lock_waits() {
    echo -e "${YELLOW}锁等待监控...${NC}"

    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    blocked_locks.locktype,
    blocked_locks.mode AS blocked_mode,
    blocking_locks.mode AS blocking_mode,
    blocked_locks.relation::regclass AS relation,
    now() - blocked_activity.query_start AS wait_duration
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
WHERE NOT blocked_locks.granted
ORDER BY blocked_activity.query_start;
EOF
}

# 监控表级锁
monitor_table_locks() {
    echo -e "${YELLOW}表级锁监控...${NC}"

    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT
    l.locktype,
    l.relation::regclass AS table_name,
    l.mode,
    l.granted,
    a.usename,
    a.query,
    a.query_start,
    age(now(), a.query_start) AS age
FROM pg_locks l
LEFT JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.locktype = 'relation'
ORDER BY a.query_start;
EOF
}

# 监控行级锁
monitor_row_locks() {
    echo -e "${YELLOW}行级锁监控...${NC}"

    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT
    l.locktype,
    l.relation::regclass AS table_name,
    l.page,
    l.tuple,
    l.mode,
    l.granted,
    a.usename,
    a.query,
    a.query_start
FROM pg_locks l
LEFT JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.locktype = 'tuple'
ORDER BY a.query_start;
EOF
}

# 监控事务锁
monitor_transaction_locks() {
    echo -e "${YELLOW}事务锁监控...${NC}"

    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT
    l.locktype,
    l.transactionid,
    l.mode,
    l.granted,
    a.usename,
    a.query,
    a.query_start
FROM pg_locks l
LEFT JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.locktype = 'transactionid'
ORDER BY a.query_start;
EOF
}

# 监控死锁统计
monitor_deadlock_stats() {
    echo -e "${YELLOW}死锁统计监控...${NC}"

    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT
    datname,
    deadlocks,
    round(deadlocks * 100.0 / NULLIF(xact_commit + xact_rollback, 0), 4) as deadlock_ratio
FROM pg_stat_database
WHERE datname = current_database();
EOF
}

# 监控锁模式统计
monitor_lock_mode_stats() {
    echo -e "${YELLOW}锁模式统计...${NC}"

    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT
    mode,
    locktype,
    COUNT(*) as lock_count,
    COUNT(*) FILTER (WHERE granted) as granted_count,
    COUNT(*) FILTER (WHERE NOT granted) as waiting_count
FROM pg_locks
GROUP BY mode, locktype
ORDER BY lock_count DESC;
EOF
}

# 主函数
main() {
    monitor_all_locks
    echo ""

    monitor_lock_waits
    echo ""

    monitor_table_locks
    echo ""

    monitor_row_locks
    echo ""

    monitor_transaction_locks
    echo ""

    monitor_deadlock_stats
    echo ""

    monitor_lock_mode_stats
    echo ""

    echo -e "${GREEN}锁监控完成！${NC}"
}

# 运行主函数
main "$@"
