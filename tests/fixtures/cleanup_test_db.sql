-- PostgreSQL测试数据库清理脚本
-- 在测试完成后执行此脚本

\c postgres_modern_test

-- 删除测试schema及其所有对象
DROP SCHEMA IF EXISTS test_schema CASCADE;

-- 清理扩展（可选，如果需要完全重置）
-- DROP EXTENSION IF EXISTS pg_trgm CASCADE;
-- DROP EXTENSION IF EXISTS btree_gin CASCADE;
-- DROP EXTENSION IF EXISTS pg_stat_statements CASCADE;

-- 重置统计信息
SELECT pg_stat_reset();

-- 打印确认信息
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL测试数据库清理完成';
END $$;

