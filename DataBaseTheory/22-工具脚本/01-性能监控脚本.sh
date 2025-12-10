#!/bin/bash
# PostgreSQL 18性能监控脚本

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-postgres}"
DB_USER="${DB_USER:-postgres}"

PSQL="psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -A"

echo "=== PostgreSQL 18性能监控 ==="
echo "时间: $(date)"
echo ""

# 1. 数据库大小
echo "【数据库大小】"
$PSQL -c "
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY pg_database_size(datname) DESC;
" | column -t -s '|'
echo ""

# 2. 前10慢查询
echo "【Top 10慢查询】"
$PSQL -c "
SELECT
    LEFT(query, 80) as query,
    calls,
    ROUND(mean_exec_time::numeric, 2) as avg_ms,
    ROUND(total_exec_time::numeric, 2) as total_ms
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;
" | column -t -s '|'
echo ""

# 3. 连接状态
echo "【连接状态】"
$PSQL -c "
SELECT
    state,
    COUNT(*) as count
FROM pg_stat_activity
GROUP BY state
ORDER BY count DESC;
" | column -t -s '|'
echo ""

# 4. 表膨胀Top 10
echo "【表膨胀Top 10】"
$PSQL -c "
SELECT
    schemaname,
    tablename,
    n_live_tup as live,
    n_dead_tup as dead,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY dead_pct DESC
LIMIT 10;
" | column -t -s '|'
echo ""

# 5. 缓存命中率
echo "【缓存命中率】"
$PSQL -c "
SELECT
    'Buffer Cache Hit Ratio' as metric,
    ROUND(
        sum(heap_blks_hit) * 100.0 /
        NULLIF(sum(heap_blks_hit + heap_blks_read), 0),
        2
    )::text || '%' as value
FROM pg_statio_user_tables;
" | column -t -s '|'
echo ""

# 6. 锁等待
echo "【锁等待】"
LOCKS=$($PSQL -c "
SELECT COUNT(*)
FROM pg_locks
WHERE NOT granted;
")

if [ "$LOCKS" -gt 0 ]; then
    echo "⚠️  发现 $LOCKS 个锁等待"
    $PSQL -c "
    SELECT
        blocked.pid AS blocked_pid,
        blocking.pid AS blocking_pid,
        LEFT(blocked.query, 50) as blocked_query
    FROM pg_stat_activity blocked
    JOIN pg_locks blocked_lock ON blocked.pid = blocked_lock.pid
    JOIN pg_locks blocking_lock ON blocking_lock.locktype = blocked_lock.locktype
        AND blocking_lock.pid != blocked_lock.pid
    JOIN pg_stat_activity blocking ON blocking.pid = blocking_lock.pid
    WHERE NOT blocked_lock.granted
      AND blocking_lock.granted
    LIMIT 5;
    " | column -t -s '|'
else
    echo "✅ 无锁等待"
fi
echo ""

# 7. ⭐ PostgreSQL 18特性使用情况
echo "【PostgreSQL 18特性】"
$PSQL -c "
SELECT
    'Builtin Connection Pool' as feature,
    current_setting('enable_builtin_connection_pooling') as enabled
UNION ALL
SELECT
    'Async IO',
    current_setting('enable_async_io')
UNION ALL
SELECT
    'JIT',
    current_setting('jit');
" | column -t -s '|'
echo ""

echo "=== 监控完成 ==="
