-- TEST: Citus分布式数据库功能测试
-- DESCRIPTION: 测试Citus分布式表和分布式查询功能
-- EXPECTED: 分布式表创建和查询正常工作
-- TAGS: citus, distributed-database, sharding
-- NOTE: 需要安装Citus扩展，并配置worker节点

-- SETUP
-- 检查并创建Citus扩展
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'citus') THEN
        CREATE EXTENSION citus;
    END IF;
END $$;

-- 创建本地表
CREATE TABLE test_users (
    user_id bigint PRIMARY KEY,
    username text NOT NULL,
    email text NOT NULL,
    created_at timestamptz DEFAULT now()
);

CREATE TABLE test_events (
    event_id bigserial,
    user_id bigint NOT NULL,
    event_type text NOT NULL,
    event_data jsonb,
    created_at timestamptz DEFAULT now(),
    PRIMARY KEY (event_id, user_id)
);

-- TEST_BODY
-- 测试1：验证Citus扩展已安装
SELECT COUNT(*) FROM pg_extension WHERE extname = 'citus';  -- EXPECT_VALUE: 1

-- 测试2：将表转换为分布式表
SELECT create_distributed_table('test_users', 'user_id');
SELECT create_distributed_table('test_events', 'user_id');

-- 测试3：验证表已分布式化
SELECT COUNT(*) FROM citus_tables
WHERE table_name::text IN ('test_users', 'test_events');  -- EXPECT_VALUE: 2

-- 测试4：插入数据到分布式表
INSERT INTO test_users (user_id, username, email)
SELECT
    i,
    'user_' || i,
    'user' || i || '@example.com'
FROM generate_series(1, 100) i;

SELECT COUNT(*) FROM test_users;  -- EXPECT_VALUE: 100

-- 测试5：插入关联数据
INSERT INTO test_events (user_id, event_type, event_data)
SELECT
    (i % 100) + 1,
    (ARRAY['login', 'purchase', 'view'])[1 + (i % 3)],
    jsonb_build_object('amount', random() * 100, 'timestamp', now())
FROM generate_series(1, 500) i;

SELECT COUNT(*) FROM test_events;  -- EXPECT_VALUE: 500

-- 测试6：查询分布式表
SELECT COUNT(*) FROM test_users WHERE user_id > 50;  -- EXPECT_VALUE: 50

-- 测试7：分布式JOIN查询
SELECT COUNT(*) FROM test_users u
JOIN test_events e ON u.user_id = e.user_id;  -- EXPECT_VALUE: 500

-- 测试8：分布式聚合查询
SELECT 
    COUNT(DISTINCT user_id) AS unique_users
FROM test_events;  -- 应该返回数值

-- 测试9：分组聚合
SELECT COUNT(*) FROM (
    SELECT 
        event_type,
        COUNT(*) AS event_count
    FROM test_events
    GROUP BY event_type
) sub;  -- EXPECT_VALUE: 3

-- 测试10：复杂分布式查询
SELECT COUNT(*) FROM (
    SELECT 
        u.username,
        COUNT(e.event_id) AS event_count,
        SUM((e.event_data->>'amount')::numeric) AS total_amount
    FROM test_users u
    LEFT JOIN test_events e ON u.user_id = e.user_id
    GROUP BY u.username
    HAVING COUNT(e.event_id) > 0
) sub;  -- 应该有结果

-- 测试11：查看分片信息
SELECT COUNT(*) > 0 FROM citus_shards
WHERE table_name::text = 'test_users';  -- EXPECT_VALUE: true

-- 测试12：查看分片分布
SELECT COUNT(DISTINCT nodename) >= 0 FROM citus_shards
WHERE table_name::text = 'test_users';  -- EXPECT_VALUE: true

-- 测试13：分布式UPDATE
UPDATE test_users 
SET username = 'updated_' || username
WHERE user_id = 1;

SELECT username FROM test_users WHERE user_id = 1;  -- 应该包含'updated_'

-- 测试14：分布式DELETE
DELETE FROM test_events WHERE user_id = 100;

SELECT COUNT(*) FROM test_events WHERE user_id = 100;  -- EXPECT_VALUE: 0

-- 测试15：创建引用表（小表）
CREATE TABLE test_categories (
    category_id serial PRIMARY KEY,
    category_name text NOT NULL
);

-- 将小表转换为引用表（会在所有worker上复制）
SELECT create_reference_table('test_categories');

-- 验证引用表创建
SELECT COUNT(*) FROM citus_tables
WHERE table_name::text = 'test_categories' 
  AND citus_table_type = 'reference';  -- EXPECT_VALUE: 1

-- 测试16：插入引用表数据
INSERT INTO test_categories (category_name)
VALUES ('Category A'), ('Category B'), ('Category C');

SELECT COUNT(*) FROM test_categories;  -- EXPECT_VALUE: 3

-- 测试17：分布式表与引用表JOIN
SELECT COUNT(*) FROM test_users u
CROSS JOIN test_categories c;  -- EXPECT_VALUE: 300

-- 测试18：查看Citus配置
SHOW citus.shard_count;  -- 应该返回配置值

-- TEARDOWN
-- 清理分布式表（需要先删除才能DROP）
DO $$
BEGIN
    -- 删除分布式表
    BEGIN
        PERFORM undistribute_table('test_events');
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;
    
    BEGIN
        PERFORM undistribute_table('test_users');
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;
    
    BEGIN
        PERFORM undistribute_table('test_categories');
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;
END $$;

-- 清理表
DROP TABLE IF EXISTS test_events;
DROP TABLE IF EXISTS test_users;
DROP TABLE IF EXISTS test_categories;

