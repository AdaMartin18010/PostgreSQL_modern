-- PostgreSQL 18 + TimescaleDB + pgvector 2.0 IoT异常检测示例
-- 最后更新: 2025-11-11
-- 特性：时序数据 + 向量特征 + 异常检测

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建设备表
CREATE TABLE devices (
    id bigserial PRIMARY KEY,
    device_name text NOT NULL,
    device_type text,
    location text,
    -- 设备特征向量（基于历史数据生成）
    feature_vector vector(128),
    created_at timestamptz DEFAULT now()
);

-- 创建时序数据表（TimescaleDB超表）
CREATE TABLE sensor_readings (
    time timestamptz NOT NULL,
    device_id bigint REFERENCES devices(id),
    temperature numeric(5,2),
    humidity numeric(5,2),
    pressure numeric(8,2),
    vibration numeric(8,4),
    -- 传感器读数向量（用于异常检测）
    reading_vector vector(128),
    -- 异常标记
    is_anomaly boolean DEFAULT false,
    anomaly_score numeric(5,4) DEFAULT 0.0
);

-- 转换为TimescaleDB超表（按时间分区）
SELECT create_hypertable('sensor_readings', 'time');

-- 创建时序索引
CREATE INDEX idx_readings_device_time ON sensor_readings (device_id, time DESC);
CREATE INDEX idx_readings_time ON sensor_readings (time DESC);

-- 创建向量索引（HNSW，PostgreSQL 18 异步 I/O 提升性能 2-3 倍）⭐
CREATE INDEX idx_readings_vector ON sensor_readings USING hnsw (reading_vector vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 创建异常检测索引
CREATE INDEX idx_readings_anomaly ON sensor_readings (device_id, time DESC) 
WHERE is_anomaly = true;

-- 插入示例设备
INSERT INTO devices (device_name, device_type, location, feature_vector) VALUES
('sensor-001', 'temperature', 'factory-floor-1', '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'::vector(128)),
('sensor-002', 'vibration', 'factory-floor-2', '[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1]'::vector(128)),
('sensor-003', 'pressure', 'factory-floor-3', '[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2]'::vector(128));

-- 插入示例时序数据
INSERT INTO sensor_readings (time, device_id, temperature, humidity, pressure, vibration, reading_vector) VALUES
(now() - INTERVAL '1 hour', 1, 25.5, 60.0, 1013.25, 0.0123, '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(128)),
(now() - INTERVAL '50 minutes', 1, 25.6, 60.1, 1013.26, 0.0124, '[0.16,0.26,0.36,0.46,0.56,0.66,0.76,0.86,0.96,0.06]'::vector(128)),
(now() - INTERVAL '40 minutes', 1, 25.7, 60.2, 1013.27, 0.0125, '[0.17,0.27,0.37,0.47,0.57,0.67,0.77,0.87,0.97,0.07]'::vector(128)),
(now() - INTERVAL '30 minutes', 1, 35.0, 70.0, 1020.00, 0.0500, '[0.50,0.60,0.70,0.80,0.90,1.00,0.10,0.20,0.30,0.40]'::vector(128)),  -- 异常值
(now() - INTERVAL '20 minutes', 1, 25.8, 60.3, 1013.28, 0.0126, '[0.18,0.28,0.38,0.48,0.58,0.68,0.78,0.88,0.98,0.08]'::vector(128)),
(now() - INTERVAL '10 minutes', 1, 25.9, 60.4, 1013.29, 0.0127, '[0.19,0.29,0.39,0.49,0.59,0.69,0.79,0.89,0.99,0.09]'::vector(128));

-- 注意：实际使用时，reading_vector应该是完整的128维向量
-- 这里仅作示例，实际向量需要从传感器数据特征提取生成

-- 异常检测函数：基于向量相似度和统计方法
CREATE OR REPLACE FUNCTION detect_anomalies(
    p_device_id bigint,
    p_time_window interval DEFAULT '1 hour',
    p_threshold numeric DEFAULT 0.8
)
RETURNS TABLE (
    time timestamptz,
    device_id bigint,
    temperature numeric,
    humidity numeric,
    pressure numeric,
    vibration numeric,
    anomaly_score numeric,
    is_anomaly boolean
) AS $$
BEGIN
    RETURN QUERY
    WITH 
    -- 计算正常模式（最近N条数据的平均向量）
    normal_pattern AS (
        SELECT AVG(reading_vector) AS avg_vector
        FROM sensor_readings
        WHERE device_id = p_device_id
          AND time >= now() - p_time_window
          AND is_anomaly = false
        HAVING COUNT(*) > 0
    ),
    -- 计算当前读数与正常模式的相似度
    similarity_scores AS (
        SELECT 
            sr.time,
            sr.device_id,
            sr.temperature,
            sr.humidity,
            sr.pressure,
            sr.vibration,
            sr.reading_vector,
            -- 相似度分数（1 - 距离）
            1 - (sr.reading_vector <=> np.avg_vector) AS similarity,
            -- 异常分数（距离越大，异常分数越高）
            (sr.reading_vector <=> np.avg_vector) AS anomaly_score
        FROM sensor_readings sr
        CROSS JOIN normal_pattern np
        WHERE sr.device_id = p_device_id
          AND sr.time >= now() - p_time_window
    )
    SELECT 
        ss.time,
        ss.device_id,
        ss.temperature,
        ss.humidity,
        ss.pressure,
        ss.vibration,
        ss.anomaly_score,
        (ss.anomaly_score > p_threshold) AS is_anomaly
    FROM similarity_scores ss
    WHERE ss.anomaly_score > p_threshold
    ORDER BY ss.anomaly_score DESC;
END;
$$ LANGUAGE plpgsql;

-- 批量标记异常
CREATE OR REPLACE FUNCTION mark_anomalies(
    p_device_id bigint,
    p_time_window interval DEFAULT '1 hour',
    p_threshold numeric DEFAULT 0.8
)
RETURNS int AS $$
DECLARE
    updated_count int;
BEGIN
    WITH anomaly_detection AS (
        SELECT time, device_id, anomaly_score
        FROM detect_anomalies(p_device_id, p_time_window, p_threshold)
    )
    UPDATE sensor_readings sr
    SET 
        is_anomaly = true,
        anomaly_score = ad.anomaly_score
    FROM anomaly_detection ad
    WHERE sr.time = ad.time 
      AND sr.device_id = ad.device_id;
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- 时序聚合查询（TimescaleDB连续聚合）
CREATE MATERIALIZED VIEW sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS hour,
    device_id,
    AVG(temperature) AS avg_temperature,
    AVG(humidity) AS avg_humidity,
    AVG(pressure) AS avg_pressure,
    AVG(vibration) AS avg_vibration,
    COUNT(*) FILTER (WHERE is_anomaly = true) AS anomaly_count
FROM sensor_readings
GROUP BY hour, device_id;
