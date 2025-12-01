-- PostgreSQL 常用诊断SQL清单
-- 版本：PostgreSQL 12+
-- 用途：日常运维诊断、性能分析、故障排查
-- 执行环境：建议在沙箱环境中测试

-- =====================
-- 1. 会话与连接诊断
-- =====================

-- 1.1 活跃会话监控
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    client_port,
    backend_start,
    query_start,
    state_change,
    wait_event_type,
    wait_event,
    state,
    query,
    backend_type
FROM pg_stat_activity 
WHERE state <> 'idle' 
ORDER BY query_start DESC;

-- 1.2 长时间运行的事务
SELECT 
    pid,
    usename,
    application_name,
    state,
    query_start,
    now() - query_start AS duration,
    query
FROM pg_stat_activity 
WHERE state = 'active' 
  AND query_start < now() - interval '5 minutes'
ORDER BY query_start;

-- 1.3 空闲事务监控
SELECT 
    pid,
    usename,
    application_name,
    state,
    query_start,
    state_change,
    now() - state_change AS idle_duration,
    query
FROM pg_stat_activity 
WHERE state = 'idle in transaction' 
  AND state_change < now() - interval '10 minutes'
ORDER BY state_change;

-- =====================
-- 2. 锁与等待诊断
-- =====================

-- 2.1 当前锁等待情况
SELECT 
    l.locktype,
    l.relation::regclass AS table_name,
    l.mode,
    l.granted,
    l.pid,
    a.usename,
    a.application_name,
    a.query,
    a.state
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT l.granted
ORDER BY l.pid;

-- 2.2 锁等待链分析
WITH RECURSIVE lock_chain AS (
    -- 基础查询：获取所有未授予的锁
    SELECT 
        l.pid,
        l.relation::regclass AS table_name,
        l.mode,
        a.usename,
        a.query,
        1 AS level,
        ARRAY[l.pid] AS wait_chain
    FROM pg_locks l
    JOIN pg_stat_activity a ON l.pid = a.pid
    WHERE NOT l.granted
    
    UNION ALL
    
    -- 递归查询：查找等待链
    SELECT 
        l.pid,
        l.relation::regclass AS table_name,
        l.mode,
        a.usename,
        a.query,
        lc.level + 1,
        lc.wait_chain || l.pid
    FROM pg_locks l
    JOIN pg_stat_activity a ON l.pid = a.pid
    JOIN lock_chain lc ON l.pid = ANY(lc.wait_chain)
    WHERE NOT l.granted AND l.pid != ALL(lc.wait_chain)
)
SELECT * FROM lock_chain ORDER BY level, pid;

-- =====================
-- 3. 表与索引使用统计
-- =====================

-- 3.1 表扫描统计
SELECT 
    schemaname,
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables 
ORDER BY (seq_scan + idx_scan) DESC;

-- 3.2 索引使用效率分析
SELECT 
    schemaname,
    relname,
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    CASE 
        WHEN idx_scan = 0 THEN '未使用'
        WHEN idx_scan < 100 THEN '使用较少'
        ELSE '正常使用'
    END AS usage_status
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;

-- 3.3 未使用的索引识别
SELECT 
    schemaname,
    relname,
    indexrelname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes 
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- =====================
-- 4. I/O 性能分析
-- =====================

-- 4.1 表I/O命中率
SELECT 
    schemaname,
    relname,
    heap_blks_read,
    heap_blks_hit,
    heap_blks_hit + heap_blks_read AS total_reads,
    round(100.0 * heap_blks_hit / nullif(heap_blks_hit + heap_blks_read, 0), 2) AS hit_ratio
FROM pg_statio_user_tables 
WHERE heap_blks_hit + heap_blks_read > 0
ORDER BY hit_ratio ASC NULLS LAST;

-- 4.2 索引I/O命中率
SELECT 
    schemaname,
    relname,
    indexrelname,
    idx_blks_read,
    idx_blks_hit,
    idx_blks_hit + idx_blks_read AS total_reads,
    round(100.0 * idx_blks_hit / nullif(idx_blks_hit + idx_blks_read, 0), 2) AS hit_ratio
FROM pg_statio_user_indexes 
WHERE idx_blks_hit + idx_blks_read > 0
ORDER BY hit_ratio ASC NULLS LAST;

-- =====================
-- 5. 慢查询分析（需要pg_stat_statements扩展）
-- =====================

-- 5.1 最耗时的查询
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    min_time,
    max_time,
    stddev_time,
    rows,
    round(100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0), 2) AS hit_percent,
    round(total_time / calls, 2) AS avg_time_per_call
FROM pg_stat_statements 
WHERE calls > 10
ORDER BY mean_time DESC 
LIMIT 20;

-- 5.2 最频繁的查询
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    round(total_time / calls, 2) AS avg_time_per_call
FROM pg_stat_statements 
ORDER BY calls DESC 
LIMIT 20;

-- 5.3 资源消耗最多的查询
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    shared_blks_hit,
    shared_blks_read,
    shared_blks_written,
    temp_blks_read,
    temp_blks_written,
    blk_read_time,
    blk_write_time
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 20;

-- =====================
-- 6. 数据库大小与增长趋势
-- =====================

-- 6.1 数据库大小统计
SELECT 
    datname,
    pg_size_pretty(pg_database_size(datname)) AS size,
    pg_database_size(datname) AS size_bytes
FROM pg_database 
WHERE datname NOT IN ('template0', 'template1')
ORDER BY pg_database_size(datname) DESC;

-- 6.2 表大小统计
SELECT 
    schemaname,
    relname,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size
FROM pg_stat_user_tables 
ORDER BY pg_total_relation_size(relid) DESC;

-- =====================
-- 7. 配置参数检查
-- =====================

-- 7.1 关键配置参数
SELECT 
    name,
    setting,
    unit,
    context,
    short_desc
FROM pg_settings 
WHERE name IN (
    'shared_buffers',
    'effective_cache_size',
    'work_mem',
    'maintenance_work_mem',
    'checkpoint_completion_target',
    'wal_buffers',
    'default_statistics_target',
    'random_page_cost',
    'effective_io_concurrency'
)
ORDER BY name;

-- =====================
-- 8. 扩展状态检查
-- =====================

-- 8.1 已安装的扩展
SELECT 
    extname,
    extversion,
    nspname AS schema_name
FROM pg_extension e
JOIN pg_namespace n ON e.extnamespace = n.oid
ORDER BY extname;

-- 8.2 可用的扩展
SELECT 
    name,
    default_version,
    installed_version,
    comment
FROM pg_available_extensions 
WHERE name IN ('pg_stat_statements', 'pgaudit', 'pgcrypto', 'vector', 'age')
ORDER BY name;


