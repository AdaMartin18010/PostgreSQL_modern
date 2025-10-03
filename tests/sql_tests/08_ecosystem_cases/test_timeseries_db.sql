-- TEST: TimescaleDB时序数据库功能测试
-- DESCRIPTION: 测试TimescaleDB超表、连续聚合、压缩等核心功能
-- EXPECTED: 所有时序数据库功能正常工作
-- TAGS: timescaledb, hypertable, continuous-aggregate, compression
-- NOTE: 需要安装TimescaleDB扩展

-- SETUP
-- 检查并创建TimescaleDB扩展
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        CREATE EXTENSION timescaledb;
    END IF;
END $$;

-- 创建测试表
CREATE TABLE test_sensor_data (
    time timestamptz NOT NULL,
    sensor_id int NOT NULL,
    temperature double precision,
    humidity double precision,
    value double precision
);

-- 转换为超表
SELECT create_hypertable(
    'test_sensor_data',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- 创建索引
CREATE INDEX idx_test_sensor_id ON test_sensor_data (sensor_id, time DESC);

-- TEST_BODY
-- 测试1：插入数据到超表
INSERT INTO test_sensor_data (time, sensor_id, temperature, humidity, value)
SELECT
    now() - (i || ' minutes')::interval,
    (i % 10) + 1,
    20 + (random() * 10)::numeric(4,2),
    40 + (random() * 30)::numeric(4,2),
    random() * 100
FROM generate_series(1, 1000) i;

SELECT COUNT(*) FROM test_sensor_data;  -- EXPECT_VALUE: 1000

-- 测试2：验证超表创建
SELECT COUNT(*) FROM timescaledb_information.hypertables
WHERE hypertable_name = 'test_sensor_data';  -- EXPECT_VALUE: 1

-- 测试3：time_bucket聚合
SELECT COUNT(*) FROM (
    SELECT
        time_bucket('5 minutes', time) AS bucket,
        sensor_id,
        AVG(temperature) AS avg_temp
    FROM test_sensor_data
    GROUP BY bucket, sensor_id
) sub;  -- 应该有多行结果

-- 测试4：查看chunks
SELECT COUNT(*) > 0 FROM timescaledb_information.chunks
WHERE hypertable_name = 'test_sensor_data';  -- EXPECT_VALUE: true

-- 测试5：创建连续聚合视图
CREATE MATERIALIZED VIEW test_sensor_data_5min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS bucket,
    sensor_id,
    COUNT(*) AS data_points,
    AVG(temperature) AS avg_temperature,
    MIN(temperature) AS min_temperature,
    MAX(temperature) AS max_temperature
FROM test_sensor_data
GROUP BY bucket, sensor_id;

-- 验证连续聚合创建成功
SELECT COUNT(*) FROM timescaledb_information.continuous_aggregates
WHERE view_name = 'test_sensor_data_5min';  -- EXPECT_VALUE: 1

-- 测试6：查询连续聚合视图
SELECT COUNT(*) > 0 FROM test_sensor_data_5min;  -- EXPECT_VALUE: true

-- 测试7：验证聚合数据正确性
SELECT 
    COUNT(DISTINCT sensor_id) BETWEEN 1 AND 10
FROM test_sensor_data_5min;  -- EXPECT_VALUE: true

-- 测试8：添加刷新策略
SELECT add_continuous_aggregate_policy(
    'test_sensor_data_5min',
    start_offset => INTERVAL '10 minutes',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes'
);

-- 验证策略创建
SELECT COUNT(*) FROM timescaledb_information.jobs
WHERE proc_name = 'policy_refresh_continuous_aggregate';  -- 至少有1个

-- 测试9：数据压缩配置
ALTER TABLE test_sensor_data 
SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- 验证压缩设置
SELECT COUNT(*) FROM timescaledb_information.compression_settings
WHERE hypertable_name = 'test_sensor_data';  -- EXPECT_VALUE: 1

-- 测试10：手动压缩旧数据
-- 压缩1天前的数据
SELECT COUNT(*) >= 0 FROM (
    SELECT compress_chunk(i)
    FROM show_chunks('test_sensor_data', older_than => INTERVAL '1 day') i
) sub;

-- 测试11：查询压缩后的数据（应该仍然正常工作）
SELECT COUNT(*) FROM test_sensor_data
WHERE time > now() - interval '1 hour';  -- 应该返回结果

-- 测试12：时间窗口查询
SELECT 
    COUNT(*) AS recent_count
FROM test_sensor_data
WHERE time > now() - interval '30 minutes'
  AND sensor_id = 1;  -- EXPECT_VALUE类型：数值

-- TEARDOWN
-- 删除连续聚合策略
DO $$
DECLARE
    job_id int;
BEGIN
    FOR job_id IN 
        SELECT j.job_id 
        FROM timescaledb_information.jobs j
        WHERE j.proc_name = 'policy_refresh_continuous_aggregate'
          AND j.hypertable_name = 'test_sensor_data'
    LOOP
        PERFORM remove_continuous_aggregate_policy('test_sensor_data_5min', if_exists => true);
    END LOOP;
END $$;

-- 清理连续聚合视图
DROP MATERIALIZED VIEW IF EXISTS test_sensor_data_5min;

-- 清理超表（CASCADE会自动删除chunks）
DROP TABLE IF EXISTS test_sensor_data CASCADE;

