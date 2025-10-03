-- PostgreSQL测试数据库初始化脚本
-- 在运行测试前执行此脚本

-- 创建测试数据库（如果不存在）
-- 注意：需要以超级用户身份运行
-- CREATE DATABASE IF NOT EXISTS postgres_modern_test;

\c postgres_modern_test

-- 创建测试schema
CREATE SCHEMA IF NOT EXISTS test_schema;

-- 设置搜索路径
SET search_path TO test_schema, public;

-- 创建测试用户（可选）
-- DO $$
-- BEGIN
--     IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'test_user') THEN
--         CREATE ROLE test_user WITH LOGIN PASSWORD 'test_password';
--     END IF;
-- END $$;

-- 授予权限
-- GRANT ALL PRIVILEGES ON SCHEMA test_schema TO test_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA test_schema TO test_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA test_schema TO test_user;

-- 安装常用扩展
CREATE EXTENSION IF NOT EXISTS pg_trgm;           -- 模糊搜索
CREATE EXTENSION IF NOT EXISTS btree_gin;         -- GIN索引增强
CREATE EXTENSION IF NOT EXISTS pg_stat_statements; -- 查询统计

-- 创建测试辅助函数
CREATE OR REPLACE FUNCTION test_schema.assert_equals(
    expected anyelement,
    actual anyelement,
    message text DEFAULT 'Assertion failed'
)
RETURNS void AS $$
BEGIN
    IF expected IS DISTINCT FROM actual THEN
        RAISE EXCEPTION '%: expected %, got %', message, expected, actual;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION test_schema.assert_true(
    condition boolean,
    message text DEFAULT 'Assertion failed: condition is not true'
)
RETURNS void AS $$
BEGIN
    IF NOT condition THEN
        RAISE EXCEPTION '%', message;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION test_schema.assert_not_null(
    value anyelement,
    message text DEFAULT 'Assertion failed: value is null'
)
RETURNS void AS $$
BEGIN
    IF value IS NULL THEN
        RAISE EXCEPTION '%', message;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 打印确认信息
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL测试数据库初始化完成';
    RAISE NOTICE 'Database: postgres_modern_test';
    RAISE NOTICE 'Schema: test_schema';
    RAISE NOTICE 'Extensions: pg_trgm, btree_gin, pg_stat_statements';
END $$;

