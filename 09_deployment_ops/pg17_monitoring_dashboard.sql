-- PostgreSQL 17 监控仪表板脚本
-- 版本：PostgreSQL 17+
-- 用途：全面监控PostgreSQL 17实例的健康状态和性能指标
-- 输出：关键指标、告警信息、性能建议

-- 设置输出格式
\pset format aligned
\pset null '(null)'
\pset border 2

-- 创建监控函数
CREATE OR REPLACE FUNCTION get_pg17_metrics()
RETURNS TABLE (
    metric_category TEXT,
    metric_name TEXT,
    metric_value TEXT,
    status TEXT,
    recommendation TEXT
) AS $$
BEGIN
    -- 1. 连接和会话信息
    RETURN QUERY
    SELECT 
        '连接状态'::TEXT as metric_category,
        '当前连接数'::TEXT as metric_name,
        (SELECT count(*)::TEXT FROM pg_stat_activity) as metric_value,
        CASE 
            WHEN (SELECT count(*) FROM pg_stat_activity) > (SELECT setting::int * 0.8 FROM pg_settings WHERE name = 'max_connections') 
            THEN 'WARNING'::TEXT
            ELSE 'OK'::TEXT
        END as status,
        CASE 
            WHEN (SELECT count(*) FROM pg_stat_activity) > (SELECT setting::int * 0.8 FROM pg_settings WHERE name = 'max_connections') 
            THEN '连接数接近上限，考虑增加max_connections或优化连接池'::TEXT
            ELSE '连接数正常'::TEXT
        END as recommendation;

    -- 2. 数据库大小
    RETURN QUERY
    SELECT 
        '存储状态'::TEXT,
        '数据库总大小'::TEXT,
        pg_size_pretty(pg_database_size(current_database())) as metric_value,
        'OK'::TEXT as status,
        '定期监控数据库增长趋势'::TEXT as recommendation;

    -- 3. WAL状态
    RETURN QUERY
    SELECT 
        'WAL状态'::TEXT,
        'WAL生成速率(MB/min)'::TEXT,
        ROUND(
            (SELECT pg_walfile_name_offset(pg_current_wal_lsn())::text::bigint - 
             (SELECT pg_walfile_name_offset(pg_last_wal_receive_lsn())::text::bigint)
            ) / 1024.0 / 1024.0 / 60.0, 2
        )::TEXT as metric_value,
        'OK'::TEXT as status,
        '监控WAL生成速率，避免WAL积压'::TEXT as recommendation;

    -- 4. 复制状态（如果有备用服务器）
    IF EXISTS (SELECT 1 FROM pg_stat_replication) THEN
        RETURN QUERY
        SELECT 
            '复制状态'::TEXT,
            '复制延迟(秒)'::TEXT,
            COALESCE(
                EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))::TEXT,
                'N/A'
            ) as metric_value,
            CASE 
                WHEN EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) > 60 
                THEN 'WARNING'::TEXT
                ELSE 'OK'::TEXT
            END as status,
            CASE 
                WHEN EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) > 60 
                THEN '复制延迟过高，检查网络和备用服务器性能'::TEXT
                ELSE '复制状态正常'::TEXT
            END as recommendation;
    END IF;

    -- 5. 缓存命中率
    RETURN QUERY
    SELECT 
        '缓存状态'::TEXT,
        '共享缓冲区命中率(%)'::TEXT,
        ROUND(
            (SELECT (blks_hit::float / (blks_hit + blks_read) * 100) 
             FROM pg_stat_database WHERE datname = current_database()), 2
        )::TEXT as metric_value,
        CASE 
            WHEN (SELECT (blks_hit::float / (blks_hit + blks_read) * 100) 
                  FROM pg_stat_database WHERE datname = current_database()) < 95 
            THEN 'WARNING'::TEXT
            ELSE 'OK'::TEXT
        END as status,
        CASE 
            WHEN (SELECT (blks_hit::float / (blks_hit + blks_read) * 100) 
                  FROM pg_stat_database WHERE datname = current_database()) < 95 
            THEN '缓存命中率偏低，考虑增加shared_buffers'::TEXT
            ELSE '缓存命中率正常'::TEXT
        END as recommendation;

    -- 6. 锁等待
    RETURN QUERY
    SELECT 
        '锁状态'::TEXT,
        '当前锁等待数'::TEXT,
        (SELECT count(*)::TEXT FROM pg_locks WHERE NOT granted) as metric_value,
        CASE 
            WHEN (SELECT count(*) FROM pg_locks WHERE NOT granted) > 10 
            THEN 'WARNING'::TEXT
            ELSE 'OK'::TEXT
        END as status,
        CASE 
            WHEN (SELECT count(*) FROM pg_locks WHERE NOT granted) > 10 
            THEN '存在锁等待，检查长时间运行的事务'::TEXT
            ELSE '锁状态正常'::TEXT
        END as recommendation;

    -- 7. 长时间运行的查询
    RETURN QUERY
    SELECT 
        '查询状态'::TEXT,
        '长时间运行查询数'::TEXT,
        (SELECT count(*)::TEXT FROM pg_stat_activity 
         WHERE state = 'active' AND query_start < now() - interval '5 minutes') as metric_value,
        CASE 
            WHEN (SELECT count(*) FROM pg_stat_activity 
                  WHERE state = 'active' AND query_start < now() - interval '5 minutes') > 0 
            THEN 'WARNING'::TEXT
            ELSE 'OK'::TEXT
        END as status,
        CASE 
            WHEN (SELECT count(*) FROM pg_stat_activity 
                  WHERE state = 'active' AND query_start < now() - interval '5 minutes') > 0 
            THEN '存在长时间运行查询，检查查询性能'::TEXT
            ELSE '查询状态正常'::TEXT
        END as recommendation;

    -- 8. 表膨胀情况
    RETURN QUERY
    SELECT 
        '表健康'::TEXT,
        '高膨胀表数量'::TEXT,
        (SELECT count(*)::TEXT FROM pg_stat_user_tables 
         WHERE n_dead_tup > n_live_tup * 0.1) as metric_value,
        CASE 
            WHEN (SELECT count(*) FROM pg_stat_user_tables 
                  WHERE n_dead_tup > n_live_tup * 0.1) > 0 
            THEN 'WARNING'::TEXT
            ELSE 'OK'::TEXT
        END as status,
        CASE 
            WHEN (SELECT count(*) FROM pg_stat_user_tables 
                  WHERE n_dead_tup > n_live_tup * 0.1) > 0 
            THEN '存在表膨胀，考虑运行VACUUM'::TEXT
            ELSE '表健康状态良好'::TEXT
        END as recommendation;

    -- 9. PostgreSQL 17 特定监控
    RETURN QUERY
    SELECT 
        'PostgreSQL 17'::TEXT,
        'JSON_TABLE支持'::TEXT,
        CASE 
            WHEN EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'json_table') 
            THEN 'YES'::TEXT
            ELSE 'NO'::TEXT
        END as metric_value,
        'OK'::TEXT as status,
        'PostgreSQL 17新特性可用'::TEXT as recommendation;

    -- 10. 系统资源使用
    RETURN QUERY
    SELECT 
        '系统资源'::TEXT,
        '内存使用率(%)'::TEXT,
        ROUND(
            (SELECT (shared_buffers::bigint * 8192)::float / 
             (SELECT setting::bigint * 8192 FROM pg_settings WHERE name = 'shared_buffers') * 100
            ), 2
        )::TEXT as metric_value,
        'OK'::TEXT as status,
        '监控内存使用情况'::TEXT as recommendation;

END;
$$ LANGUAGE plpgsql;

-- 主监控查询
\echo '=== PostgreSQL 17 监控仪表板 ==='
\echo '监控时间: ' `date`
\echo ''

-- 显示系统信息
\echo '=== 系统信息 ==='
SELECT 
    'PostgreSQL版本' as info_type,
    version() as value
UNION ALL
SELECT 
    '数据库名称',
    current_database()
UNION ALL
SELECT 
    '当前用户',
    current_user
UNION ALL
SELECT 
    '服务器时间',
    now()::text;

\echo ''
\echo '=== 关键指标监控 ==='
SELECT 
    metric_category,
    metric_name,
    metric_value,
    status,
    recommendation
FROM get_pg17_metrics()
ORDER BY 
    CASE metric_category
        WHEN '连接状态' THEN 1
        WHEN '存储状态' THEN 2
        WHEN 'WAL状态' THEN 3
        WHEN '复制状态' THEN 4
        WHEN '缓存状态' THEN 5
        WHEN '锁状态' THEN 6
        WHEN '查询状态' THEN 7
        WHEN '表健康' THEN 8
        WHEN 'PostgreSQL 17' THEN 9
        WHEN '系统资源' THEN 10
        ELSE 11
    END,
    metric_name;

-- 显示告警汇总
\echo ''
\echo '=== 告警汇总 ==='
SELECT 
    status,
    count(*) as count,
    string_agg(metric_name, ', ') as affected_metrics
FROM get_pg17_metrics()
WHERE status != 'OK'
GROUP BY status
ORDER BY status;

-- 显示Top 10 最活跃的表
\echo ''
\echo '=== Top 10 最活跃的表 ==='
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_tup_ins + n_tup_upd + n_tup_del as total_activity,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_stat_user_tables
ORDER BY total_activity DESC
LIMIT 10;

-- 显示Top 10 最慢的查询
\echo ''
\echo '=== Top 10 最慢的查询 ==='
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- 显示复制状态详情（如果有）
\echo ''
\echo '=== 复制状态详情 ==='
SELECT 
    client_addr,
    application_name,
    state,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn)) as sent_lag,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), write_lsn)) as write_lag,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn)) as flush_lag,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) as replay_lag
FROM pg_stat_replication;

-- 清理函数
DROP FUNCTION IF EXISTS get_pg17_metrics();

\echo ''
\echo '=== 监控完成 ==='
\echo '建议:'
\echo '1. 定期运行此脚本监控系统健康状态'
\echo '2. 设置告警阈值和自动化监控'
\echo '3. 根据建议优化系统配置'
\echo '4. 保存监控历史数据用于趋势分析'
