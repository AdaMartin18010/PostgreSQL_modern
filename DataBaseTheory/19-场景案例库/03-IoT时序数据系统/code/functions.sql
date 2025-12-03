-- IoT时序数据系统 - 核心函数
-- PostgreSQL 18.x

SET search_path TO public;

-- 创建分区函数
CREATE OR REPLACE FUNCTION create_partition_if_not_exists(
    table_name TEXT,
    partition_date DATE
) RETURNS void AS $$
DECLARE
    partition_name TEXT;
BEGIN
    partition_name := table_name || '_' || TO_CHAR(partition_date, 'YYYY_MM_DD');
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = partition_name) THEN
        EXECUTE FORMAT(
            'CREATE TABLE %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
            partition_name, table_name, partition_date, partition_date + 1
        );
        RAISE NOTICE '创建分区: %', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 删除旧分区
CREATE OR REPLACE FUNCTION drop_old_partition(
    table_name TEXT,
    before_date DATE
) RETURNS void AS $$
DECLARE
    partition_name TEXT;
BEGIN
    FOR partition_name IN 
        SELECT tablename FROM pg_tables 
        WHERE tablename LIKE table_name || '_%'
        AND tablename < table_name || '_' || TO_CHAR(before_date, 'YYYY_MM_DD')
    LOOP
        EXECUTE FORMAT('DROP TABLE IF EXISTS %I CASCADE', partition_name);
        RAISE NOTICE '删除分区: %', partition_name;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 查询设备最新数据
CREATE OR REPLACE FUNCTION get_device_latest_data(
    p_device_id INT,
    p_limit INT DEFAULT 100
) RETURNS TABLE (
    timestamp TIMESTAMPTZ,
    metric_name TEXT,
    value DOUBLE PRECISION,
    quality SMALLINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.timestamp,
        m.metric_name,
        s.value,
        s.quality
    FROM sensor_data s
    JOIN metrics m ON s.metric_id = m.metric_id
    WHERE s.device_id = p_device_id
    ORDER BY s.timestamp DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- 异常检测
CREATE OR REPLACE FUNCTION detect_anomalies(
    time_range INTERVAL DEFAULT '1 hour'
) RETURNS TABLE (
    device_id INT,
    metric_id SMALLINT,
    timestamp TIMESTAMPTZ,
    value DOUBLE PRECISION,
    threshold_type VARCHAR(10)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.device_id,
        s.metric_id,
        s.timestamp,
        s.value,
        CASE 
            WHEN s.value < m.alert_min THEN 'LOW'
            WHEN s.value > m.alert_max THEN 'HIGH'
        END as threshold_type
    FROM sensor_data s
    JOIN metrics m ON s.metric_id = m.metric_id
    WHERE s.timestamp > NOW() - time_range
      AND (s.value < m.alert_min OR s.value > m.alert_max);
END;
$$ LANGUAGE plpgsql;

-- 设备统计
CREATE OR REPLACE FUNCTION get_device_stats(
    p_device_id INT,
    p_time_range INTERVAL DEFAULT '24 hours'
) RETURNS TABLE (
    metric_name TEXT,
    avg_value DOUBLE PRECISION,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    sample_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.metric_name,
        AVG(s.value),
        MIN(s.value),
        MAX(s.value),
        COUNT(*)
    FROM sensor_data s
    JOIN metrics m ON s.metric_id = m.metric_id
    WHERE s.device_id = p_device_id
      AND s.timestamp > NOW() - p_time_range
    GROUP BY m.metric_name;
END;
$$ LANGUAGE plpgsql;

-- 聚合刷新函数
CREATE OR REPLACE FUNCTION refresh_1min_aggregate()
RETURNS void AS $$
BEGIN
    INSERT INTO sensor_data_1min
    SELECT 
        device_id,
        metric_id,
        DATE_TRUNC('minute', timestamp) as minute,
        AVG(value), MIN(value), MAX(value),
        STDDEV(value), COUNT(*)
    FROM sensor_data
    WHERE timestamp > NOW() - INTERVAL '10 minutes'
    GROUP BY device_id, metric_id, DATE_TRUNC('minute', timestamp)
    ON CONFLICT (device_id, metric_id, minute) DO UPDATE SET
        avg_value = EXCLUDED.avg_value,
        min_value = EXCLUDED.min_value,
        max_value = EXCLUDED.max_value,
        stddev_value = EXCLUDED.stddev_value,
        sample_count = EXCLUDED.sample_count;
END;
$$ LANGUAGE plpgsql;

SELECT cron.schedule('refresh-1min-agg', '* * * * *',
    'SELECT refresh_1min_aggregate()');

