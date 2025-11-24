#!/bin/bash
# PostgreSQL MVCC事务监控脚本
# 监控事务状态、长事务、阻塞事务等
# 版本: PostgreSQL 17 & 18

set -e

# 配置参数
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-postgres}"
DB_USER="${DB_USER:-postgres}"
WARNING_THRESHOLD="${WARNING_THRESHOLD:-300}"  # 5分钟
CRITICAL_THRESHOLD="${CRITICAL_THRESHOLD:-600}"  # 10分钟

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}PostgreSQL MVCC事务监控${NC}"
echo "=================================="

# 监控活跃事务
monitor_active_transactions() {
    echo -e "${YELLOW}活跃事务监控...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT 
    pid,
    usename,
    datname,
    state,
    isolation_level,
    query_start,
    now() - query_start as duration,
    now() - state_change as state_duration,
    CASE 
        WHEN now() - query_start > interval '${CRITICAL_THRESHOLD} seconds' THEN 'CRITICAL'
        WHEN now() - query_start > interval '${WARNING_THRESHOLD} seconds' THEN 'WARNING'
        ELSE 'OK'
    END as status,
    left(query, 100) as query_preview
FROM pg_stat_activity
WHERE state != 'idle'
  AND pid != pg_backend_pid()
ORDER BY query_start;
EOF
}

# 监控长事务
monitor_long_transactions() {
    echo -e "${YELLOW}长事务监控...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT 
    pid,
    usename,
    datname,
    state,
    isolation_level,
    xact_start,
    now() - xact_start as transaction_duration,
    query_start,
    now() - query_start as query_duration,
    CASE 
        WHEN now() - xact_start > interval '${CRITICAL_THRESHOLD} seconds' THEN 'CRITICAL'
        WHEN now() - xact_start > interval '${WARNING_THRESHOLD} seconds' THEN 'WARNING'
        ELSE 'OK'
    END as status,
    left(query, 100) as query_preview
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND pid != pg_backend_pid()
ORDER BY xact_start;
EOF
}

# 监控阻塞事务
monitor_blocked_transactions() {
    echo -e "${YELLOW}阻塞事务监控...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    blocked_activity.state AS blocked_state,
    blocking_activity.state AS blocking_state,
    now() - blocked_activity.query_start AS blocked_duration,
    now() - blocking_activity.query_start AS blocking_duration
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

# 监控事务统计
monitor_transaction_stats() {
    echo -e "${YELLOW}事务统计监控...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT 
    datname,
    xact_commit as committed_transactions,
    xact_rollback as rolled_back_transactions,
    round(xact_rollback * 100.0 / NULLIF(xact_commit + xact_rollback, 0), 2) as rollback_ratio,
    deadlocks,
    blks_read,
    blks_hit,
    round(blks_hit * 100.0 / NULLIF(blks_read + blks_hit, 0), 2) as cache_hit_ratio,
    temp_files,
    temp_bytes,
    pg_size_pretty(temp_bytes) as temp_size
FROM pg_stat_database
WHERE datname = current_database();
EOF
}

# 监控MVCC相关统计
monitor_mvcc_stats() {
    echo -e "${YELLOW}MVCC统计监控...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT 
    schemaname,
    relname,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_tup_hot_upd as hot_updates,
    round(n_tup_hot_upd * 100.0 / NULLIF(n_tup_upd, 0), 2) as hot_update_ratio,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_ratio,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;
EOF
}

# 监控XID年龄
monitor_xid_age() {
    echo -e "${YELLOW}XID年龄监控...${NC}"
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT 
    datname,
    age(datfrozenxid) as xid_age,
    CASE 
        WHEN age(datfrozenxid) > 2000000000 THEN 'CRITICAL'
        WHEN age(datfrozenxid) > 1000000000 THEN 'WARNING'
        ELSE 'OK'
    END as status
FROM pg_database
WHERE datname = current_database();

SELECT 
    schemaname,
    relname,
    age(relfrozenxid) as xid_age,
    CASE 
        WHEN age(relfrozenxid) > 2000000000 THEN 'CRITICAL'
        WHEN age(relfrozenxid) > 1000000000 THEN 'WARNING'
        ELSE 'OK'
    END as status
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE relkind = 'r'
ORDER BY age(relfrozenxid) DESC
LIMIT 10;
EOF
}

# 主函数
main() {
    monitor_active_transactions
    echo ""
    
    monitor_long_transactions
    echo ""
    
    monitor_blocked_transactions
    echo ""
    
    monitor_transaction_stats
    echo ""
    
    monitor_mvcc_stats
    echo ""
    
    monitor_xid_age
    echo ""
    
    echo -e "${GREEN}事务监控完成！${NC}"
}

# 运行主函数
main "$@"
