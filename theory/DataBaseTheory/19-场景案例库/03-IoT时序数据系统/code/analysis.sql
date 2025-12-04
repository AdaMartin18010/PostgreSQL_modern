-- IoT时序数据系统 - 分析查询
-- PostgreSQL 18.x

-- 1. 异常检测
CREATE OR REPLACE FUNCTION detect_sensor_anomalies(
    p_device_id INT,
    p_time_range INTERVAL DEFAULT '1 hour'
) RETURNS TABLE (
    timestamp TIMESTAMPTZ,
    metric_name TEXT,
    value DOUBLE PRECISION,
    z_score DOUBLE PRECISION,
    is_anomaly BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT 
            s.metric_id,
            AVG(s.value) as mean,
            STDDEV(s.value) as stddev
        FROM sensor_data s
        WHERE s.device_id = p_device_id
          AND s.timestamp > NOW() - p_time_range
        GROUP BY s.metric_id
    )
    SELECT 
        s.timestamp,
        m.metric_name,
        s.value,
        ABS((s.value - st.mean) / NULLIF(st.stddev, 0)) as z_score,
        ABS((s.value - st.mean) / NULLIF(st.stddev, 0)) > 3 as is_anomaly
    FROM sensor_data s
    JOIN metrics m ON s.metric_id = m.metric_id
    JOIN stats st ON s.metric_id = st.metric_id
    WHERE s.device_id = p_device_id
      AND s.timestamp > NOW() - p_time_range
    ORDER BY s.timestamp DESC;
END;
$$ LANGUAGE plpgsql;

-- 2. 趋势预测（线性回归）
CREATE OR REPLACE FUNCTION predict_sensor_trend(
    p_device_id INT,
    p_metric_id SMALLINT,
    p_hours_ahead INT DEFAULT 24
) RETURNS TABLE (
    future_timestamp TIMESTAMPTZ,
    predicted_value DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    WITH data AS (
        SELECT 
            EXTRACT(EPOCH FROM timestamp) as x,
            value as y
        FROM sensor_data
        WHERE device_id = p_device_id
          AND metric_id = p_metric_id
          AND timestamp > NOW() - INTERVAL '7 days'
    ),
    regression AS (
        SELECT 
            regr_slope(y, x) as slope,
            regr_intercept(y, x) as intercept
        FROM data
    )
    SELECT 
        NOW() + (i || ' hours')::INTERVAL as future_timestamp,
        r.slope * EXTRACT(EPOCH FROM NOW() + (i || ' hours')::INTERVAL) + r.intercept
    FROM generate_series(1, p_hours_ahead) i,
         regression r;
END;
$$ LANGUAGE plpgsql;

-- 3. 设备对比分析
CREATE OR REPLACE VIEW device_comparison AS
SELECT 
    d.device_name,
    m.metric_name,
    AVG(s.value) as avg_value,
    MIN(s.value) as min_value,
    MAX(s.value) as max_value,
    STDDEV(s.value) as stddev_value,
    COUNT(*) as sample_count
FROM sensor_data s
JOIN devices d ON s.device_id = d.device_id
JOIN metrics m ON s.metric_id = m.metric_id
WHERE s.timestamp > NOW() - INTERVAL '24 hours'
GROUP BY d.device_name, m.metric_name
ORDER BY d.device_name, m.metric_name;

-- 4. 按小时聚合统计
CREATE MATERIALIZED VIEW hourly_stats AS
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    device_id,
    metric_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count
FROM sensor_data
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('hour', timestamp), device_id, metric_id;

CREATE INDEX idx_hourly_stats_device ON hourly_stats(device_id, hour);

-- 5. 数据质量监控
CREATE VIEW data_quality_report AS
SELECT 
    d.device_name,
    m.metric_name,
    COUNT(*) as total_samples,
    SUM(CASE WHEN quality < 50 THEN 1 ELSE 0 END) as poor_quality_samples,
    ROUND(AVG(quality), 2) as avg_quality,
    COUNT(*) FILTER (WHERE timestamp > NOW() - INTERVAL '1 hour') as recent_samples
FROM sensor_data s
JOIN devices d ON s.device_id = d.device_id
JOIN metrics m ON s.metric_id = m.metric_id
WHERE s.timestamp > NOW() - INTERVAL '24 hours'
GROUP BY d.device_name, m.metric_name
HAVING AVG(quality) < 80
ORDER BY avg_quality;
