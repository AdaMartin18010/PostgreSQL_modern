-- PostgreSQL 高可用与复制监控SQL
-- 版本：PostgreSQL 12+
-- 用途：复制状态监控、高可用性检查、故障检测
-- 执行环境：主从复制环境

-- =====================
-- 1. 复制状态监控
-- =====================

-- 1.1 基础复制状态
SELECT 
    application_name,
    client_addr,
    client_port,
    backend_start,
    state,
    sync_state,
    sync_priority,
    sync_commit,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS byte_lag,
    write_lag,
    flush_lag,
    replay_lag,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS lag_size
FROM pg_stat_replication
ORDER BY byte_lag DESC;

-- 1.2 复制延迟详细分析
SELECT 
    application_name,
    client_addr,
    state,
    sync_state,
    -- 字节延迟
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS byte_lag,
    -- 时间延迟
    CASE 
        WHEN replay_lag IS NOT NULL THEN replay_lag
        WHEN write_lag IS NOT NULL THEN write_lag
        WHEN flush_lag IS NOT NULL THEN flush_lag
        ELSE NULL
    END AS time_lag,
    -- 延迟状态评估
    CASE 
        WHEN pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) > 1024*1024*1024 THEN 'HIGH'  -- > 1GB
        WHEN pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) > 100*1024*1024 THEN 'MEDIUM'  -- > 100MB
        ELSE 'LOW'
    END AS lag_severity
FROM pg_stat_replication
ORDER BY byte_lag DESC;

-- 1.3 复制连接健康检查
SELECT 
    application_name,
    client_addr,
    state,
    backend_start,
    now() - backend_start AS connection_duration,
    CASE 
        WHEN state = 'streaming' THEN 'HEALTHY'
        WHEN state = 'catchup' THEN 'CATCHING_UP'
        ELSE 'UNHEALTHY'
    END AS health_status
FROM pg_stat_replication;

-- =====================
-- 2. 复制槽管理
-- =====================

-- 2.1 复制槽状态
SELECT 
    slot_name,
    plugin,
    slot_type,
    datoid,
    database,
    active,
    xmin,
    catalog_xmin,
    restart_lsn,
    confirmed_flush_lsn,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS slot_lag
FROM pg_replication_slots
ORDER BY slot_lag DESC;

-- 2.2 复制槽使用情况
SELECT 
    slot_name,
    slot_type,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal_size,
    CASE 
        WHEN pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 1024*1024*1024 THEN 'HIGH_RETENTION'
        WHEN pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 100*1024*1024 THEN 'MEDIUM_RETENTION'
        ELSE 'LOW_RETENTION'
    END AS retention_level
FROM pg_replication_slots
WHERE slot_type = 'logical'
ORDER BY pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) DESC;

-- 2.3 复制槽清理建议
SELECT 
    slot_name,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal_size,
    CASE 
        WHEN NOT active AND pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 1024*1024*1024 
        THEN 'CONSIDER_DROPPING'
        WHEN NOT active 
        THEN 'INACTIVE_SLOT'
        ELSE 'ACTIVE_SLOT'
    END AS recommendation
FROM pg_replication_slots
ORDER BY pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) DESC;

-- =====================
-- 3. WAL 监控
-- =====================

-- 3.1 WAL 产生速率监控
-- 注意：需要定期执行此查询来监控WAL产生速率
CREATE OR REPLACE FUNCTION monitor_wal_generation()
RETURNS TABLE(
    current_time timestamptz,
    current_lsn pg_lsn,
    wal_files_generated bigint,
    estimated_wal_rate_mb_per_hour numeric
) AS $$
DECLARE
    current_lsn_val pg_lsn;
    current_time_val timestamptz;
BEGIN
    current_lsn_val := pg_current_wal_lsn();
    current_time_val := now();
    
    RETURN QUERY
    SELECT 
        current_time_val,
        current_lsn_val,
        (current_lsn_val - '0/0') / (16 * 1024 * 1024) as wal_files_generated,
        -- 这里需要与之前的值比较来计算实际速率
        0::numeric as estimated_wal_rate_mb_per_hour;
END;
$$ LANGUAGE plpgsql;

-- 3.2 WAL 文件统计
SELECT 
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0')) AS total_wal_generated,
    pg_current_wal_lsn() AS current_lsn,
    pg_walfile_name(pg_current_wal_lsn()) AS current_wal_file;

-- 3.3 WAL 归档状态（如果启用）
SELECT 
    archived_count,
    last_archived_wal,
    last_archived_time,
    failed_count,
    last_failed_wal,
    last_failed_time,
    stats_reset
FROM pg_stat_archiver;

-- =====================
-- 4. 冲突监控
-- =====================

-- 4.1 数据库冲突统计
SELECT 
    datname,
    confl_tablespace,
    confl_lock,
    confl_snapshot,
    confl_bufferpin,
    confl_deadlock,
    confl_snapshot + confl_bufferpin + confl_deadlock + confl_lock + confl_tablespace AS total_conflicts
FROM pg_stat_database_conflicts
WHERE datname IS NOT NULL
ORDER BY total_conflicts DESC;

-- 4.2 冲突趋势分析
SELECT 
    datname,
    confl_tablespace,
    confl_lock,
    confl_snapshot,
    confl_bufferpin,
    confl_deadlock,
    CASE 
        WHEN confl_snapshot + confl_bufferpin + confl_deadlock + confl_lock + confl_tablespace > 100 
        THEN 'HIGH_CONFLICTS'
        WHEN confl_snapshot + confl_bufferpin + confl_deadlock + confl_lock + confl_tablespace > 10 
        THEN 'MEDIUM_CONFLICTS'
        ELSE 'LOW_CONFLICTS'
    END AS conflict_level
FROM pg_stat_database_conflicts
WHERE datname IS NOT NULL
ORDER BY total_conflicts DESC;

-- =====================
-- 5. 主从切换监控
-- =====================

-- 5.1 主库状态检查
SELECT 
    'PRIMARY' as role,
    pg_is_in_recovery() as is_in_recovery,
    pg_current_wal_lsn() as current_lsn,
    pg_walfile_name(pg_current_wal_lsn()) as current_wal_file,
    count(*) as replica_count
FROM pg_stat_replication;

-- 5.2 从库状态检查
SELECT 
    'STANDBY' as role,
    pg_is_in_recovery() as is_in_recovery,
    pg_last_wal_receive_lsn() as last_receive_lsn,
    pg_last_wal_replay_lsn() as last_replay_lsn,
    pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) as replay_lag_bytes
WHERE pg_is_in_recovery();

-- 5.3 切换准备检查
SELECT 
    application_name,
    client_addr,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS byte_lag,
    CASE 
        WHEN sync_state = 'sync' AND pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) < 1024*1024 
        THEN 'READY_FOR_FAILOVER'
        WHEN sync_state = 'async' AND pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) < 10*1024*1024 
        THEN 'POTENTIALLY_READY'
        ELSE 'NOT_READY'
    END AS failover_readiness
FROM pg_stat_replication
ORDER BY byte_lag;

-- =====================
-- 6. 性能监控
-- =====================

-- 6.1 复制性能指标
SELECT 
    application_name,
    client_addr,
    state,
    -- 复制延迟
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS byte_lag,
    -- 时间延迟
    replay_lag,
    -- 复制速度估算（需要定期采样）
    CASE 
        WHEN replay_lag IS NOT NULL AND replay_lag > interval '0 seconds'
        THEN pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) / 
                           extract(epoch from replay_lag) * 3600) || '/hour'
        ELSE 'N/A'
    END AS estimated_replay_rate
FROM pg_stat_replication
ORDER BY byte_lag DESC;

-- 6.2 网络延迟监控
SELECT 
    application_name,
    client_addr,
    state,
    backend_start,
    now() - backend_start AS connection_duration,
    -- 简单的网络延迟估算（基于复制延迟）
    CASE 
        WHEN replay_lag IS NOT NULL 
        THEN extract(epoch from replay_lag) * 1000  -- 转换为毫秒
        ELSE NULL
    END AS estimated_network_latency_ms
FROM pg_stat_replication
ORDER BY estimated_network_latency_ms DESC NULLS LAST;

-- =====================
-- 7. 告警查询
-- =====================

-- 7.1 复制延迟告警
SELECT 
    'REPLICATION_LAG_ALERT' as alert_type,
    application_name,
    client_addr,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS byte_lag,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS lag_size
FROM pg_stat_replication
WHERE pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) > 100*1024*1024  -- > 100MB
ORDER BY byte_lag DESC;

-- 7.2 复制连接断开告警
SELECT 
    'REPLICATION_DISCONNECTED' as alert_type,
    slot_name,
    'No active replication connection' as message
FROM pg_replication_slots
WHERE active = false AND slot_type = 'physical';

-- 7.3 复制槽积压告警
SELECT 
    'REPLICATION_SLOT_BACKLOG' as alert_type,
    slot_name,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal_size
FROM pg_replication_slots
WHERE pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 1024*1024*1024  -- > 1GB
ORDER BY pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) DESC;

-- 7.4 高冲突率告警
SELECT 
    'HIGH_CONFLICT_RATE' as alert_type,
    datname,
    confl_tablespace + confl_lock + confl_snapshot + confl_bufferpin + confl_deadlock AS total_conflicts
FROM pg_stat_database_conflicts
WHERE datname IS NOT NULL 
  AND confl_tablespace + confl_lock + confl_snapshot + confl_bufferpin + confl_deadlock > 100
ORDER BY total_conflicts DESC;

-- =====================
-- 8. 维护建议
-- =====================

-- 8.1 复制槽维护建议
SELECT 
    slot_name,
    slot_type,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal_size,
    CASE 
        WHEN NOT active THEN 'Consider dropping inactive slot: DROP REPLICATION SLOT ' || slot_name || ';'
        WHEN pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 1024*1024*1024 
        THEN 'High WAL retention, monitor disk space'
        ELSE 'Slot is healthy'
    END AS maintenance_recommendation
FROM pg_replication_slots
ORDER BY pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) DESC;

-- 8.2 复制配置优化建议
SELECT 
    'CONFIGURATION_CHECK' as check_type,
    CASE 
        WHEN count(*) = 0 THEN 'No replication configured'
        WHEN count(*) = 1 AND bool_and(sync_state = 'sync') THEN 'Single synchronous replica - consider adding async replicas for high availability'
        WHEN count(*) > 1 AND bool_and(sync_state = 'sync') THEN 'Multiple synchronous replicas - consider async replicas for better performance'
        ELSE 'Mixed sync/async configuration'
    END AS recommendation
FROM pg_stat_replication;

-- =====================
-- 9. 历史趋势分析
-- =====================

-- 9.1 创建复制监控历史表
CREATE TABLE IF NOT EXISTS replication_monitoring_history (
    id bigserial PRIMARY KEY,
    check_time timestamptz DEFAULT now(),
    application_name text,
    client_addr inet,
    state text,
    sync_state text,
    byte_lag bigint,
    replay_lag interval,
    write_lag interval,
    flush_lag interval
);

-- 9.2 插入当前监控数据
INSERT INTO replication_monitoring_history (
    application_name, client_addr, state, sync_state, 
    byte_lag, replay_lag, write_lag, flush_lag
)
SELECT 
    application_name, client_addr, state, sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn),
    replay_lag, write_lag, flush_lag
FROM pg_stat_replication;

-- 9.3 查询历史趋势
SELECT 
    application_name,
    date_trunc('hour', check_time) as hour,
    avg(byte_lag) as avg_byte_lag,
    max(byte_lag) as max_byte_lag,
    avg(extract(epoch from replay_lag)) as avg_replay_lag_seconds
FROM replication_monitoring_history
WHERE check_time >= now() - interval '24 hours'
GROUP BY application_name, date_trunc('hour', check_time)
ORDER BY hour DESC, application_name;


