-- IoT时序数据系统 - 典型查询
-- PostgreSQL 18.x

-- Q1: 单设备最近数据
PREPARE get_recent_data (int, interval) AS
SELECT timestamp, value, quality
FROM sensor_data
WHERE device_id = $1
  AND timestamp > NOW() - $2
ORDER BY timestamp DESC;

EXECUTE get_recent_data(1001, '1 hour');

-- Q2: 多设备实时监控
SELECT 
    d.device_name,
    m.metric_name,
    s.value,
    s.timestamp,
    CASE 
        WHEN s.value < m.normal_min THEN 'LOW'
        WHEN s.value > m.normal_max THEN 'HIGH'
        ELSE 'NORMAL'
    END as status
FROM sensor_data s
JOIN devices d ON s.device_id = d.device_id
JOIN metrics m ON s.metric_id = m.metric_id
WHERE s.timestamp > NOW() - INTERVAL '5 minutes'
  AND s.device_id = ANY($1::int[])
ORDER BY s.timestamp DESC;

-- Q3: 设备聚合统计
SELECT 
    device_id,
    metric_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    STDDEV(value) as stddev_value,
    COUNT(*) as sample_count
FROM sensor_data
WHERE timestamp > NOW() - INTERVAL '24 hours'
  AND device_id BETWEEN 1 AND 1000
GROUP BY device_id, metric_id;

-- Q4: 异常检测
SELECT 
    d.device_name,
    m.metric_name,
    s.timestamp,
    s.value,
    m.alert_min,
    m.alert_max
FROM sensor_data s
JOIN devices d ON s.device_id = d.device_id
JOIN metrics m ON s.metric_id = m.metric_id
WHERE s.timestamp > NOW() - INTERVAL '1 hour'
  AND (s.value < m.alert_min OR s.value > m.alert_max)
ORDER BY s.timestamp DESC;

-- Q5: 使用预聚合查询
SELECT 
    d.device_name,
    m.metric_name,
    DATE_TRUNC('hour', a.minute) as hour,
    AVG(a.avg_value) as hourly_avg
FROM sensor_data_1min a
JOIN devices d ON a.device_id = d.device_id
JOIN metrics m ON a.metric_id = m.metric_id
WHERE a.minute >= NOW() - INTERVAL '24 hours'
  AND a.device_id = $1
GROUP BY d.device_name, m.metric_name, DATE_TRUNC('hour', a.minute)
ORDER BY hour;

-- Q6: 趋势分析（窗口函数）
SELECT 
    timestamp,
    value,
    AVG(value) OVER (ORDER BY timestamp ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) as moving_avg_60,
    value - LAG(value, 1) OVER (ORDER BY timestamp) as delta
FROM sensor_data
WHERE device_id = $1
  AND metric_id = $2
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp;

-- ⭐ PostgreSQL 18优化：
-- 1. BRIN索引快速定位
-- 2. 分区裁剪
-- 3. 计划缓存
-- 4. 增量排序

