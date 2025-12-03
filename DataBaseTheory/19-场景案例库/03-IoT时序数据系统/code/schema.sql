-- IoT时序数据系统 - Schema定义
-- PostgreSQL 18.x

CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 设备表
CREATE TABLE devices (
    device_id SERIAL PRIMARY KEY,
    device_code VARCHAR(50) UNIQUE,
    device_name VARCHAR(200),
    device_type VARCHAR(50),
    location VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active'
);

-- 指标表
CREATE TABLE metrics (
    metric_id SERIAL PRIMARY KEY,
    metric_code VARCHAR(50) UNIQUE,
    metric_name VARCHAR(100),
    unit VARCHAR(20),
    normal_min DOUBLE PRECISION,
    normal_max DOUBLE PRECISION
);

-- 传感器数据表（按天分区）
CREATE TABLE sensor_data (
    device_id INT NOT NULL,
    metric_id SMALLINT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    quality SMALLINT DEFAULT 100 CHECK (quality BETWEEN 0 AND 100),
    PRIMARY KEY (device_id, timestamp, metric_id)
) PARTITION BY RANGE (timestamp);

-- 批量创建365天分区
DO $$
BEGIN
    FOR i IN 0..364 LOOP
        EXECUTE FORMAT(
            'CREATE TABLE sensor_data_%s PARTITION OF sensor_data FOR VALUES FROM (%L) TO (%L)',
            TO_CHAR(CURRENT_DATE + i, 'YYYY_MM_DD'),
            CURRENT_DATE + i,
            CURRENT_DATE + i + 1
        );
    END LOOP;
END $$;

-- ⭐ BRIN索引（时序数据优化）
CREATE INDEX idx_sensor_data_time 
ON sensor_data USING BRIN (timestamp) 
WITH (pages_per_range = 128);

-- ⭐ PostgreSQL 18：LZ4压缩
ALTER TABLE sensor_data ALTER COLUMN value SET COMPRESSION lz4;

-- 1分钟聚合表
CREATE TABLE sensor_data_1min (
    device_id INT,
    metric_id SMALLINT,
    minute TIMESTAMPTZ,
    avg_value DOUBLE PRECISION,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    stddev_value DOUBLE PRECISION,
    sample_count INT,
    PRIMARY KEY (device_id, metric_id, minute)
) PARTITION BY RANGE (minute);

-- 创建7天分区
DO $$
BEGIN
    FOR i IN 0..6 LOOP
        EXECUTE FORMAT(
            'CREATE TABLE sensor_data_1min_%s PARTITION OF sensor_data_1min FOR VALUES FROM (%L) TO (%L)',
            TO_CHAR(CURRENT_DATE + i, 'YYYY_MM_DD'),
            CURRENT_DATE + i,
            CURRENT_DATE + i + 1
        );
    END LOOP;
END $$;

-- 自动分区管理
CREATE OR REPLACE FUNCTION manage_sensor_partitions()
RETURNS void AS $$
BEGIN
    -- 创建明天分区
    PERFORM create_partition_if_not_exists(
        'sensor_data',
        CURRENT_DATE + 1
    );
    
    -- 删除365天前分区
    PERFORM drop_old_partition(
        'sensor_data',
        CURRENT_DATE - 365
    );
END;
$$ LANGUAGE plpgsql;

SELECT cron.schedule('manage-partitions', '0 1 * * *',
    'SELECT manage_sensor_partitions()');

ANALYZE sensor_data;

