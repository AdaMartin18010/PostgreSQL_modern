-- PostgreSQL 监控仪表板查询集合
-- 版本：PostgreSQL 12+
-- 用途：实时监控、性能分析、告警配置
-- 执行环境：PostgreSQL 12+ 或兼容版本

-- =====================
-- 1. 系统概览仪表板
-- =====================

-- 1.1 系统状态概览
CREATE OR REPLACE VIEW system_overview AS
SELECT 
    'System Overview' as dashboard_section,
    'Database Status' as metric_category,
    'Active Connections' as metric_name,
    count(*)::text as current_value,
    'connections' as unit,
    CASE 
        WHEN count(*) > 100 THEN 'WARNING'
        WHEN count(*) > 200 THEN 'CRITICAL'
        ELSE 'OK'
    END as status
FROM pg_stat_activity 
WHERE state = 'active'
UNION ALL
SELECT 
    'System Overview' as dashboard_section,
    'Database Status' as metric_category,
    'Total Connections' as metric_name,
    count(*)::text as current_value,
    'connections' as unit,
    CASE 
        WHEN count(*) > 150 THEN 'WARNING'
        WHEN count(*) > 250 THEN 'CRITICAL'
        ELSE 'OK'
    END as status
FROM pg_stat_activity
UNION ALL
SELECT 
    'System Overview' as dashboard_section,
    'Database Status' as metric_category,
    'Database Size' as metric_name,
    pg_size_pretty(pg_database_size(current_database())) as current_value,
    'size' as unit,
    'OK' as status
UNION ALL
SELECT 
    'System Overview' as dashboard_section,
    'Database Status' as metric_category,
    'Uptime' as metric_name,
    (now() - pg_postmaster_start_time())::text as current_value,
    'duration' as unit,
    'OK' as status;

-- 1.2 查询系统概览
SELECT * FROM system_overview ORDER BY metric_category, metric_name;

-- =====================
-- 2. 性能监控仪表板
-- =====================

-- 2.1 性能指标概览
CREATE OR REPLACE VIEW performance_overview AS
SELECT 
    'Performance Metrics' as dashboard_section,
    'Query Performance' as metric_category,
    'Slow Queries (1s+)' as metric_name,
    count(*)::text as current_value,
    'queries' as unit,
    CASE 
        WHEN count(*) > 10 THEN 'WARNING'
        WHEN count(*) > 50 THEN 'CRITICAL'
        ELSE 'OK'
    END as status
FROM pg_stat_statements 
WHERE mean_time > 1000
UNION ALL
SELECT 
    'Performance Metrics' as dashboard_section,
    'Query Performance' as metric_category,
    'Total Query Calls' as metric_name,
    sum(calls)::text as current_value,
    'calls' as unit,
    'OK' as status
FROM pg_stat_statements
UNION ALL
SELECT 
    'Performance Metrics' as dashboard_section,
    'Cache Performance' as metric_category,
    'Buffer Hit Ratio' as metric_name,
    round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2)::text as current_value,
    '%' as unit,
    CASE 
        WHEN round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2) < 90 THEN 'WARNING'
        WHEN round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2) < 80 THEN 'CRITICAL'
        ELSE 'OK'
    END as status
FROM pg_stat_database
WHERE datname = current_database();

-- 2.2 查询性能概览
SELECT * FROM performance_overview ORDER BY metric_category, metric_name;

-- =====================
-- 3. 锁监控仪表板
-- =====================

-- 3.1 锁状态概览
CREATE OR REPLACE VIEW lock_overview AS
SELECT 
    'Lock Monitoring' as dashboard_section,
    'Lock Status' as metric_category,
    'Waiting Locks' as metric_name,
    count(*)::text as current_value,
    'locks' as unit,
    CASE 
        WHEN count(*) > 5 THEN 'WARNING'
        WHEN count(*) > 20 THEN 'CRITICAL'
        ELSE 'OK'
    END as status
FROM pg_locks 
WHERE NOT granted
UNION ALL
SELECT 
    'Lock Monitoring' as dashboard_section,
    'Lock Status' as metric_category,
    'Total Locks' as metric_name,
    count(*)::text as current_value,
    'locks' as unit,
    'OK' as status
FROM pg_locks
UNION ALL
SELECT 
    'Lock Monitoring' as dashboard_section,
    'Lock Status' as metric_category,
    'Deadlock Count' as metric_name,
    deadlocks::text as current_value,
    'deadlocks' as unit,
    CASE 
        WHEN deadlocks > 0 THEN 'WARNING'
        ELSE 'OK'
    END as status
FROM pg_stat_database
WHERE datname = current_database();

-- 3.2 查询锁概览
SELECT * FROM lock_overview ORDER BY metric_category, metric_name;

-- =====================
-- 4. 存储监控仪表板
-- =====================

-- 4.1 存储使用概览
CREATE OR REPLACE VIEW storage_overview AS
SELECT 
    'Storage Monitoring' as dashboard_section,
    'Table Sizes' as metric_category,
    'Largest Table' as metric_name,
    (SELECT relname FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 1) as current_value,
    'table' as unit,
    'OK' as status
UNION ALL
SELECT 
    'Storage Monitoring' as dashboard_section,
    'Table Sizes' as metric_category,
    'Largest Table Size' as metric_name,
    pg_size_pretty((SELECT pg_total_relation_size(relid) FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 1)) as current_value,
    'size' as unit,
    'OK' as status
UNION ALL
SELECT 
    'Storage Monitoring' as dashboard_section,
    'Table Sizes' as metric_category,
    'Total Tables' as metric_name,
    count(*)::text as current_value,
    'tables' as unit,
    'OK' as status
FROM pg_stat_user_tables
UNION ALL
SELECT 
    'Storage Monitoring' as dashboard_section,
    'Index Usage' as metric_category,
    'Unused Indexes' as metric_name,
    count(*)::text as current_value,
    'indexes' as unit,
    CASE 
        WHEN count(*) > 5 THEN 'WARNING'
        WHEN count(*) > 20 THEN 'CRITICAL'
        ELSE 'OK'
    END as status
FROM pg_stat_user_indexes 
WHERE idx_scan = 0;

-- 4.2 查询存储概览
SELECT * FROM storage_overview ORDER BY metric_category, metric_name;

-- =====================
-- 5. 复制监控仪表板
-- =====================

-- 5.1 复制状态概览
CREATE OR REPLACE VIEW replication_overview AS
SELECT 
    'Replication Monitoring' as dashboard_section,
    'Replication Status' as metric_category,
    'Replica Count' as metric_name,
    count(*)::text as current_value,
    'replicas' as unit,
    CASE 
        WHEN count(*) = 0 THEN 'WARNING'
        ELSE 'OK'
    END as status
FROM pg_stat_replication
UNION ALL
SELECT 
    'Replication Monitoring' as dashboard_section,
    'Replication Status' as metric_category,
    'Max Replication Lag' as metric_name,
    CASE 
        WHEN max(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) IS NULL THEN 'N/A'
        ELSE pg_size_pretty(max(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)))
    END as current_value,
    'bytes' as unit,
    CASE 
        WHEN max(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) > 1024*1024*1024 THEN 'CRITICAL'
        WHEN max(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) > 100*1024*1024 THEN 'WARNING'
        ELSE 'OK'
    END as status
FROM pg_stat_replication
UNION ALL
SELECT 
    'Replication Monitoring' as dashboard_section,
    'Replication Status' as metric_category,
    'Replication Slots' as metric_name,
    count(*)::text as current_value,
    'slots' as unit,
    'OK' as status
FROM pg_replication_slots;

-- 5.2 查询复制概览
SELECT * FROM replication_overview ORDER BY metric_category, metric_name;

-- =====================
-- 6. 告警配置
-- =====================

-- 6.1 创建告警表
CREATE TABLE IF NOT EXISTS alert_config (
    id bigserial PRIMARY KEY,
    alert_name text NOT NULL,
    alert_type text NOT NULL,
    threshold_value numeric,
    threshold_operator text,
    severity text NOT NULL,
    enabled boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 6.2 插入默认告警配置
INSERT INTO alert_config (alert_name, alert_type, threshold_value, threshold_operator, severity) VALUES
('High Connection Count', 'active_connections', 100, '>', 'WARNING'),
('Critical Connection Count', 'active_connections', 200, '>', 'CRITICAL'),
('Low Buffer Hit Ratio', 'buffer_hit_ratio', 90, '<', 'WARNING'),
('Critical Buffer Hit Ratio', 'buffer_hit_ratio', 80, '<', 'CRITICAL'),
('High Lock Wait Count', 'waiting_locks', 5, '>', 'WARNING'),
('Critical Lock Wait Count', 'waiting_locks', 20, '>', 'CRITICAL'),
('High Replication Lag', 'replication_lag_mb', 100, '>', 'WARNING'),
('Critical Replication Lag', 'replication_lag_mb', 1024, '>', 'CRITICAL')
ON CONFLICT DO NOTHING;

-- =====================
-- 7. 告警检查函数
-- =====================

-- 7.1 创建告警检查函数
CREATE OR REPLACE FUNCTION check_alerts()
RETURNS TABLE(
    alert_name text,
    current_value numeric,
    threshold_value numeric,
    severity text,
    status text
) AS $$
BEGIN
    -- 检查连接数告警
    RETURN QUERY
    SELECT 
        ac.alert_name,
        count(*)::numeric as current_value,
        ac.threshold_value,
        ac.severity,
        CASE 
            WHEN ac.threshold_operator = '>' AND count(*) > ac.threshold_value THEN 'TRIGGERED'
            WHEN ac.threshold_operator = '<' AND count(*) < ac.threshold_value THEN 'TRIGGERED'
            WHEN ac.threshold_operator = '=' AND count(*) = ac.threshold_value THEN 'TRIGGERED'
            ELSE 'OK'
        END as status
    FROM alert_config ac
    CROSS JOIN pg_stat_activity
    WHERE ac.alert_type = 'active_connections' 
      AND ac.enabled = true
      AND state = 'active'
    GROUP BY ac.alert_name, ac.threshold_value, ac.threshold_operator, ac.severity;
    
    -- 检查缓冲区命中率告警
    RETURN QUERY
    SELECT 
        ac.alert_name,
        round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2) as current_value,
        ac.threshold_value,
        ac.severity,
        CASE 
            WHEN ac.threshold_operator = '<' AND round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2) < ac.threshold_value THEN 'TRIGGERED'
            ELSE 'OK'
        END as status
    FROM alert_config ac
    CROSS JOIN pg_stat_database
    WHERE ac.alert_type = 'buffer_hit_ratio' 
      AND ac.enabled = true
      AND datname = current_database()
    GROUP BY ac.alert_name, ac.threshold_value, ac.threshold_operator, ac.severity;
    
    -- 检查锁等待告警
    RETURN QUERY
    SELECT 
        ac.alert_name,
        count(*)::numeric as current_value,
        ac.threshold_value,
        ac.severity,
        CASE 
            WHEN ac.threshold_operator = '>' AND count(*) > ac.threshold_value THEN 'TRIGGERED'
            ELSE 'OK'
        END as status
    FROM alert_config ac
    CROSS JOIN pg_locks
    WHERE ac.alert_type = 'waiting_locks' 
      AND ac.enabled = true
      AND NOT granted
    GROUP BY ac.alert_name, ac.threshold_value, ac.threshold_operator, ac.severity;
    
    -- 检查复制延迟告警
    RETURN QUERY
    SELECT 
        ac.alert_name,
        CASE 
            WHEN max(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) IS NULL THEN 0
            ELSE max(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) / (1024*1024)
        END as current_value,
        ac.threshold_value,
        ac.severity,
        CASE 
            WHEN ac.threshold_operator = '>' AND max(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) / (1024*1024) > ac.threshold_value THEN 'TRIGGERED'
            ELSE 'OK'
        END as status
    FROM alert_config ac
    CROSS JOIN pg_stat_replication
    WHERE ac.alert_type = 'replication_lag_mb' 
      AND ac.enabled = true
    GROUP BY ac.alert_name, ac.threshold_value, ac.threshold_operator, ac.severity;
END;
$$ LANGUAGE plpgsql;

-- =====================
-- 8. 实时监控查询
-- =====================

-- 8.1 当前告警状态
SELECT * FROM check_alerts() WHERE status = 'TRIGGERED' ORDER BY severity DESC;

-- 8.2 系统健康状态
SELECT 
    'System Health' as dashboard_section,
    'Overall Status' as metric_category,
    'Health Score' as metric_name,
    CASE 
        WHEN (SELECT count(*) FROM check_alerts() WHERE status = 'TRIGGERED' AND severity = 'CRITICAL') > 0 THEN 'CRITICAL'
        WHEN (SELECT count(*) FROM check_alerts() WHERE status = 'TRIGGERED' AND severity = 'WARNING') > 0 THEN 'WARNING'
        ELSE 'HEALTHY'
    END as current_value,
    'status' as unit,
    'OK' as status;

-- =====================
-- 9. 历史监控数据
-- =====================

-- 9.1 创建监控历史表
CREATE TABLE IF NOT EXISTS monitoring_history (
    id bigserial PRIMARY KEY,
    metric_name text NOT NULL,
    metric_value numeric NOT NULL,
    metric_unit text,
    recorded_at timestamptz DEFAULT now()
);

-- 9.2 插入当前监控数据
INSERT INTO monitoring_history (metric_name, metric_value, metric_unit)
SELECT 
    'active_connections',
    count(*)::numeric,
    'connections'
FROM pg_stat_activity 
WHERE state = 'active'
UNION ALL
SELECT 
    'buffer_hit_ratio',
    round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2),
    'percent'
FROM pg_stat_database
WHERE datname = current_database()
UNION ALL
SELECT 
    'waiting_locks',
    count(*)::numeric,
    'locks'
FROM pg_locks 
WHERE NOT granted;

-- =====================
-- 10. 监控报表
-- =====================

-- 10.1 生成监控报表
CREATE OR REPLACE FUNCTION generate_monitoring_report()
RETURNS TABLE(
    report_section text,
    metric_name text,
    current_value text,
    status text,
    recommendation text
) AS $$
BEGIN
    -- 系统概览
    RETURN QUERY
    SELECT 
        'System Overview' as report_section,
        'Active Connections' as metric_name,
        count(*)::text as current_value,
        CASE 
            WHEN count(*) > 100 THEN 'WARNING'
            WHEN count(*) > 200 THEN 'CRITICAL'
            ELSE 'OK'
        END as status,
        CASE 
            WHEN count(*) > 100 THEN 'Consider connection pooling or reducing connection timeout'
            WHEN count(*) > 200 THEN 'Immediate action required: check for connection leaks'
            ELSE 'Connection count is healthy'
        END as recommendation
    FROM pg_stat_activity 
    WHERE state = 'active'
    GROUP BY 1, 2;
    
    -- 性能概览
    RETURN QUERY
    SELECT 
        'Performance Overview' as report_section,
        'Buffer Hit Ratio' as metric_name,
        round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2)::text as current_value,
        CASE 
            WHEN round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2) < 90 THEN 'WARNING'
            WHEN round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2) < 80 THEN 'CRITICAL'
            ELSE 'OK'
        END as status,
        CASE 
            WHEN round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2) < 90 THEN 'Consider increasing shared_buffers or improving query patterns'
            WHEN round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2) < 80 THEN 'Critical: Review memory configuration and query optimization'
            ELSE 'Buffer hit ratio is healthy'
        END as recommendation
    FROM pg_stat_database
    WHERE datname = current_database()
    GROUP BY 1, 2;
    
    -- 锁概览
    RETURN QUERY
    SELECT 
        'Lock Overview' as report_section,
        'Waiting Locks' as metric_name,
        count(*)::text as current_value,
        CASE 
            WHEN count(*) > 5 THEN 'WARNING'
            WHEN count(*) > 20 THEN 'CRITICAL'
            ELSE 'OK'
        END as status,
        CASE 
            WHEN count(*) > 5 THEN 'Monitor for long-running transactions and consider query optimization'
            WHEN count(*) > 20 THEN 'Critical: Check for deadlocks and long-running transactions'
            ELSE 'Lock contention is minimal'
        END as recommendation
    FROM pg_locks 
    WHERE NOT granted
    GROUP BY 1, 2;
END;
$$ LANGUAGE plpgsql;

-- =====================
-- 11. 执行监控报表
-- =====================

-- 11.1 生成完整监控报表
SELECT * FROM generate_monitoring_report() ORDER BY report_section, metric_name;

-- 11.2 显示告警摘要
SELECT 
    'Alert Summary' as summary_type,
    severity,
    count(*) as alert_count
FROM check_alerts() 
WHERE status = 'TRIGGERED'
GROUP BY severity
ORDER BY 
    CASE severity 
        WHEN 'CRITICAL' THEN 1 
        WHEN 'WARNING' THEN 2 
        ELSE 3 
    END;

-- =====================
-- 12. 清理和维护
-- =====================

-- 12.1 清理历史数据（保留最近7天）
DELETE FROM monitoring_history 
WHERE recorded_at < now() - interval '7 days';

-- 12.2 更新告警配置时间戳
UPDATE alert_config 
SET updated_at = now() 
WHERE updated_at < now() - interval '1 day';

-- =====================
-- 13. 监控仪表板总结
-- =====================

SELECT 
    'MONITORING DASHBOARD SUMMARY' as report_title,
    now() as report_timestamp,
    current_database() as database_name,
    current_user as report_generated_by;

-- 显示所有监控视图
SELECT 
    'Available Monitoring Views' as view_category,
    schemaname,
    viewname,
    'Ready for use' as status
FROM pg_views 
WHERE viewname IN (
    'system_overview',
    'performance_overview', 
    'lock_overview',
    'storage_overview',
    'replication_overview'
)
ORDER BY viewname;
