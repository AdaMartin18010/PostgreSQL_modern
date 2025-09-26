-- 连续聚合示例
-- 先确保已启用 timescaledb 扩展，并创建 hypertable
-- SELECT create_hypertable('metrics', 'ts');

-- 1) 连续聚合视图
CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_5m
WITH (timescaledb.continuous)
AS
SELECT time_bucket('5 minutes', ts) AS bucket,
       device_id,
       avg(value) AS avg_value
FROM metrics
GROUP BY bucket, device_id;

-- 2) 刷新策略（可选，需使用 add_continuous_aggregate_policy）
-- SELECT add_continuous_aggregate_policy('metrics_5m',
--   start_offset => INTERVAL '7 days',
--   end_offset   => INTERVAL '1 hour',
--   schedule_interval => INTERVAL '15 minutes');
