-- 基准测试监控 SQL 脚本
-- 版本：PostgreSQL 12+
-- 用途：基准测试期间的性能监控和指标收集
-- 执行环境：PostgreSQL 12+ 或兼容版本

-- =====================
-- 1. 基准测试前系统状态
-- =====================

-- 1.1 系统配置概览
SELECT
    'System Configuration' AS category,
    name,
    setting,
    unit,
    context,
    source
FROM pg_settings
WHERE name IN (
    'shared_buffers',
    'work_mem',
    'maintenance_work_mem',
    'effective_cache_size',
    'max_connections',
    'max_parallel_workers',
    'max_parallel_workers_per_gather',
    'checkpoint_timeout',
    'max_wal_size',
    'wal_buffers'
)
ORDER BY name;

-- 1.2 数据库大小和对象统计
SELECT
    'Database Size' AS category,
    pg_size_pretty(pg_database_size(current_database())) AS database_size,
    (SELECT count(*) FROM pg_tables WHERE schemaname = 'public') AS table_count,
    (SELECT count(*) FROM pg_indexes WHERE schemaname = 'public') AS index_count;

-- 1.3 表大小统计（Top 10）
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- =====================
-- 2. 基准测试期间监控
-- =====================

-- 2.1 当前活跃连接和查询
SELECT
    pid,
    usename,
    datname,
    application_name,
    state,
    query_start,
    now() - query_start AS query_duration,
    wait_event_type,
    wait_event,
    LEFT(query, 100) AS query_preview
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- 2.2 连接数统计
SELECT
    'Connection Statistics' AS category,
    count(*) AS total_connections,
    count(*) FILTER (WHERE state = 'active') AS active_connections,
    count(*) FILTER (WHERE state = 'idle') AS idle_connections,
    count(*) FILTER (WHERE state = 'idle in transaction') AS idle_in_transaction,
    max_conn AS max_connections,
    round(100.0 * count(*) / max_conn, 2) AS connection_usage_pct
FROM pg_stat_activity
CROSS JOIN (SELECT setting::int AS max_conn FROM pg_settings WHERE name = 'max_connections') mc
GROUP BY max_conn;

-- 2.3 缓存命中率
SELECT
    'Cache Hit Ratio' AS category,
    round(100.0 * sum(blks_hit) / NULLIF(sum(blks_hit) + sum(blks_read), 0), 2) AS buffer_hit_ratio,
    sum(blks_hit) AS blocks_hit,
    sum(blks_read) AS blocks_read
FROM pg_stat_database
WHERE datname = current_database();

-- 2.4 索引使用统计（Top 10）
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC
LIMIT 10;

-- =====================
-- 3. 基准测试后性能分析
-- =====================

-- 3.1 慢查询统计（需要启用 pg_stat_statements）
SELECT
    'Slow Queries' AS category,
    queryid,
    LEFT(query, 100) AS query_preview,
    calls,
    round(total_exec_time::numeric, 2) AS total_time_ms,
    round(mean_exec_time::numeric, 2) AS mean_time_ms,
    round(stddev_exec_time::numeric, 2) AS stddev_ms,
    round(min_exec_time::numeric, 2) AS min_time_ms,
    round(max_exec_time::numeric, 2) AS max_time_ms,
    rows,
    round(100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0), 2) AS cache_hit_pct
FROM pg_stat_statements
WHERE calls > 10
ORDER BY mean_exec_time DESC
LIMIT 20;

-- 3.2 表扫描统计
SELECT
    schemaname,
    tablename,
    seq_scan AS sequential_scans,
    seq_tup_read AS seq_tuples_read,
    idx_scan AS index_scans,
    idx_tup_fetch AS idx_tuples_fetched,
    round(100.0 * idx_scan / NULLIF(seq_scan + idx_scan, 0), 2) AS index_usage_pct
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY seq_scan DESC
LIMIT 10;

-- 3.3 IO 统计（PostgreSQL 17+）
SELECT
    'IO Statistics' AS category,
    object,
    context,
    reads,
    writes,
    extends,
    fsyncs,
    op_bytes,
    reads * op_bytes AS total_bytes_read,
    writes * op_bytes AS total_bytes_written
FROM pg_stat_io
WHERE object = 'relation'
ORDER BY total_bytes_written DESC
LIMIT 10;

-- 3.4 等待事件统计
SELECT
    wait_event_type,
    wait_event,
    count(*) AS wait_count,
    sum(EXTRACT(EPOCH FROM (now() - state_change))) AS total_wait_time_seconds
FROM pg_stat_activity
WHERE wait_event IS NOT NULL
GROUP BY wait_event_type, wait_event
ORDER BY total_wait_time_seconds DESC
LIMIT 10;

-- =====================
-- 4. 基准测试对比查询
-- =====================

-- 4.1 创建基准测试结果表（可选）
CREATE TABLE IF NOT EXISTS benchmark_results (
    id bigserial PRIMARY KEY,
    test_name text NOT NULL,
    test_time timestamptz DEFAULT now(),
    tps numeric,
    avg_latency_ms numeric,
    tp50_ms numeric,
    tp95_ms numeric,
    tp99_ms numeric,
    connection_count int,
    buffer_hit_ratio numeric,
    notes text
);

-- 4.2 插入基准测试结果
-- INSERT INTO benchmark_results (test_name, tps, avg_latency_ms, tp50_ms, tp95_ms, tp99_ms, connection_count, buffer_hit_ratio, notes)
-- VALUES (
--     'baseline_test',
--     412.567,
--     77.234,
--     65.12,
--     123.45,
--     189.23,
--     32,
--     98.5,
--     'Baseline test with default configuration'
-- );

-- 4.3 查询基准测试历史
SELECT
    test_name,
    test_time,
    tps,
    avg_latency_ms,
    tp50_ms,
    tp95_ms,
    tp99_ms,
    connection_count,
    buffer_hit_ratio,
    notes
FROM benchmark_results
ORDER BY test_time DESC;

-- =====================
-- 5. 性能基线对比
-- =====================

-- 5.1 对比不同测试的 TPS
SELECT
    test_name,
    tps,
    avg_latency_ms,
    tp95_ms,
    round(100.0 * (tps - LAG(tps) OVER (ORDER BY test_time)) / LAG(tps) OVER (ORDER BY test_time), 2) AS tps_change_pct
FROM benchmark_results
ORDER BY test_time;

-- 5.2 对比延迟变化
SELECT
    test_name,
    avg_latency_ms,
    tp95_ms,
    tp99_ms,
    round(100.0 * (avg_latency_ms - LAG(avg_latency_ms) OVER (ORDER BY test_time)) / LAG(avg_latency_ms) OVER (ORDER BY test_time), 2) AS latency_change_pct
FROM benchmark_results
ORDER BY test_time;
