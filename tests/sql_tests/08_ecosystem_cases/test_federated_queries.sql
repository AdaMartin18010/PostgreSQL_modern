-- TEST: 联邦查询功能测试
-- DESCRIPTION: 测试Foreign Data Wrapper (FDW)功能
-- EXPECTED: 外部表创建和跨库查询正常工作
-- TAGS: fdw, foreign-data-wrapper, cross-database

-- SETUP
-- 创建postgres_fdw扩展
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
        CREATE EXTENSION postgres_fdw;
    END IF;
END $$;

-- 创建本地测试表（模拟远程数据源）
CREATE TABLE local_users (
    id serial PRIMARY KEY,
    username text NOT NULL UNIQUE,
    email text NOT NULL,
    created_at timestamptz DEFAULT now()
);

CREATE TABLE local_orders (
    id serial PRIMARY KEY,
    user_id int NOT NULL,
    amount numeric(10,2) NOT NULL,
    status text DEFAULT 'pending',
    created_at timestamptz DEFAULT now()
);

-- 插入测试数据
INSERT INTO local_users (username, email) VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com');

INSERT INTO local_orders (user_id, amount, status) VALUES
    (1, 100.00, 'completed'),
    (1, 200.00, 'pending'),
    (2, 150.00, 'completed'),
    (3, 300.00, 'completed');

-- 创建外部服务器（指向本地数据库，用于测试）
CREATE SERVER test_foreign_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'localhost', dbname current_database(), port '5432');

-- 创建用户映射
CREATE USER MAPPING FOR CURRENT_USER
    SERVER test_foreign_server
    OPTIONS (user CURRENT_USER);

-- 创建外部表
CREATE FOREIGN TABLE foreign_users (
    id int,
    username text,
    email text,
    created_at timestamptz
)
SERVER test_foreign_server
OPTIONS (schema_name 'public', table_name 'local_users');

CREATE FOREIGN TABLE foreign_orders (
    id int,
    user_id int,
    amount numeric(10,2),
    status text,
    created_at timestamptz
)
SERVER test_foreign_server
OPTIONS (schema_name 'public', table_name 'local_orders');

-- TEST_BODY
-- 测试1：查询外部表
SELECT COUNT(*) FROM foreign_users;  -- EXPECT_VALUE: 3

-- 测试2：外部表数据正确性
SELECT COUNT(*) FROM foreign_users
WHERE email LIKE '%@example.com';  -- EXPECT_VALUE: 3

-- 测试3：跨表JOIN（本地表 + 外部表）
SELECT COUNT(*)
FROM local_users u
JOIN foreign_orders o ON u.id = o.user_id;  -- EXPECT_VALUE: 4

-- 测试4：联邦聚合查询
SELECT 
    fu.username,
    COUNT(fo.id) AS order_count,
    SUM(fo.amount) AS total_amount
FROM foreign_users fu
JOIN foreign_orders fo ON fu.id = fo.user_id
GROUP BY fu.username
ORDER BY total_amount DESC;  -- EXPECT_ROWS: 3

-- 测试5：WHERE条件下推（predicate pushdown）
EXPLAIN (COSTS OFF)
SELECT username FROM foreign_users
WHERE id = 1;
-- 应该看到 "Foreign Scan on foreign_users"
-- 并且WHERE条件应该被推送到远程服务器

-- 测试6：外部表写入（如果权限允许）
-- 注意：通常外部表是只读的，但也可以配置为可写
BEGIN;
INSERT INTO foreign_users (id, username, email)
VALUES (99, 'test_user', 'test@example.com');

-- 验证写入（通过本地表查询）
SELECT COUNT(*) FROM local_users WHERE username = 'test_user';  -- EXPECT_VALUE: 1
ROLLBACK;

-- 测试7：复杂联邦查询（多个外部表）
SELECT 
    fu.username,
    fo.amount,
    fo.status
FROM foreign_users fu
JOIN foreign_orders fo ON fu.id = fo.user_id
WHERE fo.status = 'completed'
  AND fo.amount > 100
ORDER BY fo.amount DESC;  -- EXPECT_ROWS: 2

-- 测试8：验证外部服务器配置
SELECT 
    srvname,
    srvoptions
FROM pg_foreign_server
WHERE srvname = 'test_foreign_server';  -- EXPECT_ROWS: 1

-- 测试9：验证外部表定义
SELECT 
    foreign_table_schema,
    foreign_table_name,
    foreign_server_name
FROM information_schema.foreign_tables
WHERE foreign_table_name IN ('foreign_users', 'foreign_orders');  -- EXPECT_ROWS: 2

-- 测试10：用户映射验证
SELECT 
    COUNT(*) 
FROM pg_user_mappings
WHERE srvname = 'test_foreign_server';  -- EXPECT_VALUE: 1

-- TEARDOWN
-- 清理外部表和服务器
DROP FOREIGN TABLE IF EXISTS foreign_orders;
DROP FOREIGN TABLE IF EXISTS foreign_users;
DROP USER MAPPING IF EXISTS FOR CURRENT_USER SERVER test_foreign_server;
DROP SERVER IF EXISTS test_foreign_server;

-- 清理本地测试表
DROP TABLE IF EXISTS local_orders;
DROP TABLE IF EXISTS local_users;

