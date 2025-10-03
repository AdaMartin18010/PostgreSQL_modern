-- TEST: 实时分析功能测试
-- DESCRIPTION: 测试实时分析的核心功能（分区表、物化视图、聚合）
-- EXPECTED: 分区表、物化视图和实时聚合功能正常工作
-- TAGS: realtime-analytics, partitioning, materialized-view

-- SETUP
-- 创建分区表（按时间分区）
CREATE TABLE test_events (
    id bigserial,
    event_type text NOT NULL,
    user_id int NOT NULL,
    amount numeric(10,2),
    event_time timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id, event_time)
) PARTITION BY RANGE (event_time);

-- 创建分区（最近3天）
CREATE TABLE test_events_day1 PARTITION OF test_events
    FOR VALUES FROM ('2025-10-01') TO ('2025-10-02');

CREATE TABLE test_events_day2 PARTITION OF test_events
    FOR VALUES FROM ('2025-10-02') TO ('2025-10-03');

CREATE TABLE test_events_day3 PARTITION OF test_events
    FOR VALUES FROM ('2025-10-03') TO ('2025-10-04');

-- 创建索引
CREATE INDEX idx_test_events_type ON test_events(event_type, event_time);
CREATE INDEX idx_test_events_user ON test_events(user_id, event_time);

-- TEST_BODY
-- 测试1：插入数据到分区表
INSERT INTO test_events (event_type, user_id, amount, event_time) VALUES
    ('purchase', 1, 100.00, '2025-10-01 10:00:00'),
    ('purchase', 2, 200.00, '2025-10-01 11:00:00'),
    ('view', 1, 0, '2025-10-01 12:00:00'),
    ('purchase', 3, 150.00, '2025-10-02 10:00:00'),
    ('purchase', 1, 300.00, '2025-10-02 11:00:00'),
    ('view', 2, 0, '2025-10-02 12:00:00'),
    ('purchase', 2, 250.00, '2025-10-03 10:00:00'),
    ('view', 3, 0, '2025-10-03 11:00:00');

SELECT COUNT(*) FROM test_events;  -- EXPECT_VALUE: 8

-- 测试2：验证数据分布到正确的分区
SELECT COUNT(*) FROM test_events_day1;  -- EXPECT_VALUE: 3
SELECT COUNT(*) FROM test_events_day2;  -- EXPECT_VALUE: 3
SELECT COUNT(*) FROM test_events_day3;  -- EXPECT_VALUE: 2

-- 测试3：分区剪枝（Partition Pruning）验证
EXPLAIN (COSTS OFF)
SELECT COUNT(*) FROM test_events
WHERE event_time >= '2025-10-02' AND event_time < '2025-10-03';
-- 应该只扫描 test_events_day2 分区

-- 测试4：实时聚合查询
SELECT 
    event_type,
    COUNT(*) AS event_count,
    SUM(amount) AS total_amount
FROM test_events
WHERE event_type = 'purchase'
GROUP BY event_type;  -- EXPECT_ROWS: 1

-- 测试5：时间窗口聚合
SELECT 
    DATE_TRUNC('day', event_time) AS day,
    event_type,
    COUNT(*) AS event_count,
    SUM(amount) AS total_amount
FROM test_events
GROUP BY day, event_type
ORDER BY day, event_type;  -- EXPECT_ROWS: 6

-- 测试6：创建物化视图（日级别聚合）
CREATE MATERIALIZED VIEW test_events_daily AS
SELECT 
    DATE_TRUNC('day', event_time) AS day,
    event_type,
    COUNT(*) AS event_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount
FROM test_events
GROUP BY day, event_type;

-- 创建唯一索引（支持CONCURRENTLY刷新）
CREATE UNIQUE INDEX idx_test_events_daily_pk 
    ON test_events_daily(day, event_type);

-- 测试7：查询物化视图
SELECT COUNT(*) FROM test_events_daily;  -- EXPECT_ROWS: 6

-- 测试8：物化视图数据正确性
SELECT 
    day::date,
    event_type,
    event_count
FROM test_events_daily
WHERE event_type = 'purchase'
ORDER BY day;  -- EXPECT_ROWS: 3

-- 测试9：刷新物化视图
-- 插入新数据
INSERT INTO test_events (event_type, user_id, amount, event_time)
VALUES ('purchase', 4, 400.00, '2025-10-03 15:00:00');

-- 刷新物化视图
REFRESH MATERIALIZED VIEW test_events_daily;

-- 验证刷新后的数据
SELECT event_count
FROM test_events_daily
WHERE day::date = '2025-10-03' AND event_type = 'purchase';  -- EXPECT_VALUE: 2

-- 测试10：窗口函数（移动平均）
SELECT 
    event_time::date AS day,
    event_type,
    amount,
    AVG(amount) OVER (
        PARTITION BY event_type
        ORDER BY event_time
        ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
    ) AS moving_avg
FROM test_events
WHERE event_type = 'purchase'
ORDER BY event_time
LIMIT 5;  -- EXPECT_ROWS: 5

-- 测试11：实时Top-N查询
SELECT 
    user_id,
    SUM(amount) AS total_spent,
    COUNT(*) AS purchase_count
FROM test_events
WHERE event_type = 'purchase'
GROUP BY user_id
ORDER BY total_spent DESC
LIMIT 3;  -- EXPECT_ROWS: 3

-- 测试12：验证分区表元数据
SELECT 
    COUNT(*) AS partition_count
FROM pg_tables
WHERE tablename LIKE 'test_events_day%';  -- EXPECT_VALUE: 3

-- TEARDOWN
-- 清理物化视图
DROP MATERIALIZED VIEW IF EXISTS test_events_daily;

-- 清理分区表（CASCADE会自动删除所有分区）
DROP TABLE IF EXISTS test_events CASCADE;

