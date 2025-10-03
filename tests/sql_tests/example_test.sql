-- TEST: 示例测试 - 创建和查询表
-- DESCRIPTION: 演示测试框架的基本用法
-- EXPECTED: 成功创建表并插入数据，查询返回正确结果
-- TAGS: smoke, example

-- SETUP
-- 创建测试表
CREATE TABLE IF NOT EXISTS test_users (
    id serial PRIMARY KEY,
    username text NOT NULL UNIQUE,
    email text NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- TEST_BODY
-- 插入测试数据
INSERT INTO test_users (username, email) VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com');

-- 查询数据
SELECT COUNT(*) AS user_count FROM test_users;  -- EXPECT_VALUE: 3

-- 验证约束
SELECT 
    COUNT(*) AS total_users,
    COUNT(DISTINCT username) AS unique_usernames
FROM test_users;  -- EXPECT_ROWS: 1

-- 测试唯一约束（应该失败）
-- INSERT INTO test_users (username, email) VALUES ('alice', 'alice2@example.com');  -- EXPECT_ERROR

-- TEARDOWN
-- 清理测试数据
DROP TABLE IF EXISTS test_users;

