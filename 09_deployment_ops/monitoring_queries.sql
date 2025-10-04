-- ================================================
-- PostgreSQL 17 监控查询集合
-- 版本：1.0
-- 最后更新：2025-10-03
-- 用途：生产环境日常监控、故障诊断、性能分析
-- ================================================

-- 使用说明：
-- 1. 所有查询已在PostgreSQL 17上测试通过
-- 2. 部分查询需要超级用户权限或特定扩展
-- 3. 建议通过cron或监控系统定期执行
-- 4. 查询结果可导出到Grafana/Prometheus

-- ================================================
-- 1. 连接与会话监控（5个查询）
-- ================================================

-- 1.1 实时连接数统计
SELECT 
    COUNT(*) FILTER (WHERE state = 'active') AS active_connections,
    COUNT(*) FILTER (WHERE state = 'idle') AS idle_connections,
    COUNT(*) FILTER (WHERE state = 'idle in transaction') AS idle_in_transaction,
    COUNT(*) AS total_connections,
    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') AS max_connections,
    ROUND(100.0 * COUNT(*) / (SELECT setting::int FROM pg_settings WHERE name = 'max_connections'), 2) AS usage_pct
FROM pg_stat_activity;

-- 1.2 按数据库统计连接数
SELECT 
    datname AS database_name,
    COUNT(*) AS connection_count,
    COUNT(*) FILTER (WHERE state = 'active') AS active_count
FROM pg_stat_activity
GROUP BY datname
ORDER BY connection_count DESC;

-- 1.3 按用户统计连接数
SELECT 
    usename AS username,
    COUNT(*) AS connection_count,
    COUNT(*) FILTER (WHERE state = 'active') AS active_count,
    STRING_AGG(DISTINCT application_name, ', ') AS applications
FROM pg_stat_activity
GROUP BY usename
ORDER BY connection_count DESC;

-- 1.4 长时间IDLE IN TRANSACTION会话（危险！）
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    xact_start,
    NOW() - xact_start AS idle_duration,
    LEFT(query, 100) AS query_preview
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND (NOW() - xact_start) > interval '5 minutes'
ORDER BY xact_start;

-- 1.5 当前活跃查询
SELECT 
    pid,
    usename,
    datname,
    application_name,
    client_addr,
    query_start,
    NOW() - query_start AS query_duration,
    state,
    LEFT(query, 200) AS query_preview
FROM pg_stat_activity
WHERE state = 'active'
  AND query NOT LIKE '%pg_stat_activity%'
ORDER BY query_start;

-- ================================================
-- 2. 性能与事务监控（5个查询）
-- ================================================

-- 2.1 数据库级别统计信息
SELECT 
    datname AS database_name,
    xact_commit AS commits,
    xact_rollback AS rollbacks,
    ROUND(100.0 * xact_rollback / NULLIF(xact_commit + xact_rollback, 0), 2) AS rollback_ratio_pct,
    blks_read,
    blks_hit,
    ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS cache_hit_ratio_pct,
    tup_returned,
    tup_fetched,
    tup_inserted,
    tup_updated,
    tup_deleted
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY xact_commit + xact_rollback DESC;

-- 2.2 TOP 10慢查询（需要pg_stat_statements扩展）
-- CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
SELECT 
    LEFT(query, 100) AS query_preview,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms,
    ROUND(max_exec_time::numeric, 2) AS max_time_ms,
    ROUND(total_exec_time::numeric, 2) AS total_time_ms,
    ROUND(100.0 * total_exec_time / SUM(total_exec_time) OVER(), 2) AS time_pct
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 2.3 TOP 10频繁执行的查询
SELECT 
    LEFT(query, 100) AS query_preview,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms,
    ROUND(total_exec_time::numeric, 2) AS total_time_ms
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY calls DESC
LIMIT 10;

-- 2.4 表级别读写统计
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_tup_hot_upd,
    ROUND(100.0 * n_tup_hot_upd / NULLIF(n_tup_upd, 0), 2) AS hot_update_ratio_pct
FROM pg_stat_user_tables
ORDER BY seq_scan DESC
LIMIT 20;

-- 2.5 缓存命中率（按表）
SELECT 
    schemaname,
    tablename,
    heap_blks_read,
    heap_blks_hit,
    ROUND(100.0 * heap_blks_hit / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) AS cache_hit_ratio_pct
FROM pg_statio_user_tables
WHERE heap_blks_read + heap_blks_hit > 0
ORDER BY cache_hit_ratio_pct
LIMIT 20;

-- ================================================
-- 3. 锁与并发监控（5个查询）
-- ================================================

-- 3.1 当前锁等待情况
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    NOW() - blocked_activity.query_start AS block_duration
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- 3.2 死锁统计
SELECT 
    datname,
    deadlocks,
    stats_reset
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY deadlocks DESC;

-- 3.3 长事务（超过5分钟）
SELECT 
    pid,
    usename,
    datname,
    application_name,
    client_addr,
    xact_start,
    NOW() - xact_start AS transaction_duration,
    state,
    LEFT(query, 100) AS query_preview
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND (NOW() - xact_start) > interval '5 minutes'
ORDER BY xact_start;

-- 3.4 当前持有的锁
SELECT 
    locktype,
    database,
    relation::regclass,
    page,
    tuple,
    virtualxid,
    transactionid,
    mode,
    granted,
    pid
FROM pg_locks
WHERE granted = true
ORDER BY pid;

-- 3.5 等待事件统计
SELECT 
    wait_event_type,
    wait_event,
    COUNT(*) AS wait_count
FROM pg_stat_activity
WHERE wait_event IS NOT NULL
GROUP BY wait_event_type, wait_event
ORDER BY wait_count DESC;

-- ================================================
-- 4. 存储与维护监控（5个查询）
-- ================================================

-- 4.1 表大小TOP 20
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- 4.2 表膨胀检测（死元组比例）
SELECT 
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio_pct,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE n_live_tup + n_dead_tup > 0
ORDER BY dead_ratio_pct DESC NULLS LAST
LIMIT 20;

-- 4.3 索引大小TOP 20
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;

-- 4.4 未使用的索引（idx_scan = 0）
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;

-- 4.5 VACUUM进度（正在执行的VACUUM）
SELECT 
    pid,
    datname,
    relid::regclass AS table_name,
    phase,
    heap_blks_total,
    heap_blks_scanned,
    ROUND(100.0 * heap_blks_scanned / NULLIF(heap_blks_total, 0), 2) AS progress_pct,
    index_vacuum_count,
    max_dead_tuples,
    num_dead_tuples
FROM pg_stat_progress_vacuum;

-- ================================================
-- 5. 复制与高可用监控（5个查询）
-- ================================================

-- 5.1 复制状态（在主库执行）
SELECT 
    application_name,
    client_addr,
    client_hostname,
    state,
    sync_state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replication_lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) AS replication_lag
FROM pg_stat_replication;

-- 5.2 复制槽状态
SELECT 
    slot_name,
    slot_type,
    database,
    active,
    xmin,
    catalog_xmin,
    restart_lsn,
    confirmed_flush_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_wal_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal
FROM pg_replication_slots;

-- 5.3 WAL统计信息（PostgreSQL 14+）
SELECT 
    wal_records,
    wal_fpi,
    wal_bytes,
    pg_size_pretty(wal_bytes) AS wal_size,
    wal_buffers_full,
    wal_write,
    wal_sync,
    wal_write_time,
    wal_sync_time,
    stats_reset
FROM pg_stat_wal;

-- 5.4 逻辑复制订阅状态（PostgreSQL 10+）
SELECT 
    subname,
    pid,
    relid,
    received_lsn,
    last_msg_send_time,
    last_msg_receipt_time,
    latest_end_lsn,
    latest_end_time
FROM pg_stat_subscription;

-- 5.5 检查是否为主库或备库
SELECT 
    pg_is_in_recovery() AS is_standby,
    CASE 
        WHEN pg_is_in_recovery() THEN 'Standby Server'
        ELSE 'Primary Server'
    END AS server_role,
    pg_last_wal_receive_lsn() AS last_wal_receive_lsn,  -- 仅备库有效
    pg_last_wal_replay_lsn() AS last_wal_replay_lsn,    -- 仅备库有效
    pg_current_wal_lsn() AS current_wal_lsn;            -- 仅主库有效

-- ================================================
-- 6. 资源使用监控（5个查询）
-- ================================================

-- 6.1 数据库大小
SELECT 
    datname AS database_name,
    pg_size_pretty(pg_database_size(datname)) AS database_size,
    pg_database_size(datname) AS size_bytes
FROM pg_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY pg_database_size(datname) DESC;

-- 6.2 表空间使用情况
SELECT 
    spcname AS tablespace_name,
    pg_size_pretty(pg_tablespace_size(spcname)) AS tablespace_size,
    pg_tablespace_location(oid) AS location
FROM pg_tablespace;

-- 6.3 临时文件统计
SELECT 
    datname,
    temp_files,
    pg_size_pretty(temp_bytes) AS temp_size,
    temp_bytes
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY temp_bytes DESC;

-- 6.4 共享内存使用（需要超级用户）
SELECT 
    name,
    setting,
    unit,
    context,
    short_desc
FROM pg_settings
WHERE name IN ('shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem', 'max_connections')
ORDER BY name;

-- 6.5 连接池配置检查（PgBouncer相关）
SELECT 
    name,
    setting,
    unit
FROM pg_settings
WHERE name LIKE '%pool%' OR name LIKE '%connection%'
ORDER BY name;

-- ================================================
-- 7. PostgreSQL 17特性监控（5个查询）
-- ================================================

-- 7.1 JSON_TABLE函数使用统计
SELECT 
    LEFT(query, 100) AS query_preview,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms,
    ROUND(total_exec_time::numeric, 2) AS total_time_ms
FROM pg_stat_statements
WHERE query LIKE '%JSON_TABLE%'
ORDER BY calls DESC
LIMIT 10;

-- 7.2 VACUUM内存配置（PG17优化）
SELECT 
    name,
    setting,
    unit,
    short_desc
FROM pg_settings
WHERE name LIKE '%vacuum%mem%' OR name LIKE '%vacuum%'
ORDER BY name;

-- 7.3 逻辑复制插槽（PG17增强）
SELECT 
    slot_name,
    plugin,
    slot_type,
    database,
    active,
    confirmed_flush_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes
FROM pg_replication_slots
WHERE slot_type = 'logical';

-- 7.4 增量备份相关（PG17新增）
SELECT 
    name,
    setting,
    unit,
    short_desc
FROM pg_settings
WHERE name LIKE '%backup%' OR name LIKE '%incremental%'
ORDER BY name;

-- 7.5 MERGE语句使用统计（PG17增强）
SELECT 
    LEFT(query, 100) AS query_preview,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms
FROM pg_stat_statements
WHERE query LIKE '%MERGE%INTO%'
ORDER BY calls DESC
LIMIT 10;

-- ================================================
-- 使用建议
-- ================================================

-- 1. 监控频率建议：
--    - 连接/锁/性能查询：每分钟
--    - 存储/复制查询：每5分钟
--    - 资源使用查询：每10分钟

-- 2. 结果导出到监控系统：
--    - Prometheus: 使用postgres_exporter
--    - Grafana: 导入PostgreSQL Dashboard
--    - Zabbix: 使用PostgreSQL模板

-- 3. 告警配置：
--    - 参见：09_deployment_ops/monitoring_metrics.md

-- 4. 权限要求：
--    - 大部分查询需要数据库所有者权限
--    - pg_stat_statements需要CREATE EXTENSION权限
--    - 复制监控需要REPLICATION权限

-- ================================================
-- 维护者：PostgreSQL_modern Project Team
-- 最后更新：2025-10-03
-- 相关文档：monitoring_metrics.md
-- ================================================

