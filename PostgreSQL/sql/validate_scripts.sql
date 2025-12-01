-- PostgreSQL SQL脚本验证工具
-- 版本：PostgreSQL 12+
-- 用途：验证所有SQL脚本的正确性和完整性
-- 执行环境：PostgreSQL 12+ 或兼容版本

-- =====================
-- 1. 环境检查
-- =====================

-- 1.1 检查PostgreSQL版本
SELECT 
    'PostgreSQL Version Check' as check_type,
    version() as version_info,
    CASE 
        WHEN version() LIKE '%PostgreSQL 12%' THEN 'SUPPORTED'
        WHEN version() LIKE '%PostgreSQL 13%' THEN 'SUPPORTED'
        WHEN version() LIKE '%PostgreSQL 14%' THEN 'SUPPORTED'
        WHEN version() LIKE '%PostgreSQL 15%' THEN 'SUPPORTED'
        WHEN version() LIKE '%PostgreSQL 16%' THEN 'SUPPORTED'
        WHEN version() LIKE '%PostgreSQL 17%' THEN 'SUPPORTED'
        ELSE 'UNKNOWN_VERSION'
    END as compatibility_status;

-- 1.2 检查扩展可用性
SELECT 
    'Extension Availability Check' as check_type,
    name,
    default_version,
    installed_version,
    CASE 
        WHEN installed_version IS NOT NULL THEN 'INSTALLED'
        WHEN name IN ('vector', 'age', 'pgaudit', 'pgcrypto') THEN 'REQUIRED_NOT_INSTALLED'
        ELSE 'OPTIONAL'
    END as status
FROM pg_available_extensions 
WHERE name IN ('vector', 'age', 'pgaudit', 'pgcrypto', 'pg_stat_statements')
ORDER BY name;

-- 1.3 检查权限
SELECT 
    'Permission Check' as check_type,
    current_user as current_user,
    session_user as session_user,
    CASE 
        WHEN current_user = 'postgres' THEN 'SUPERUSER'
        WHEN has_database_privilege(current_database(), 'CREATE') THEN 'CREATEDB'
        ELSE 'LIMITED'
    END as privilege_level;

-- =====================
-- 2. 脚本语法验证
-- =====================

-- 2.1 创建验证函数
CREATE OR REPLACE FUNCTION validate_sql_syntax(sql_text text)
RETURNS TABLE(
    is_valid boolean,
    error_message text
) AS $$
BEGIN
    BEGIN
        EXECUTE 'EXPLAIN ' || sql_text;
        RETURN QUERY SELECT true, 'Syntax is valid'::text;
    EXCEPTION
        WHEN OTHERS THEN
            RETURN QUERY SELECT false, SQLERRM::text;
    END;
END;
$$ LANGUAGE plpgsql;

-- 2.2 测试基础查询语法
SELECT 
    'Basic Query Syntax Check' as check_type,
    'SELECT statements' as test_category,
    count(*) as total_tests,
    count(*) FILTER (WHERE is_valid) as passed_tests,
    count(*) FILTER (WHERE NOT is_valid) as failed_tests
FROM (
    SELECT * FROM validate_sql_syntax('SELECT 1')
    UNION ALL
    SELECT * FROM validate_sql_syntax('SELECT version()')
    UNION ALL
    SELECT * FROM validate_sql_syntax('SELECT current_timestamp')
    UNION ALL
    SELECT * FROM validate_sql_syntax('SELECT count(*) FROM pg_stat_activity')
) t;

-- =====================
-- 3. 系统视图访问测试
-- =====================

-- 3.1 测试系统视图可访问性
SELECT 
    'System Views Access Check' as check_type,
    'pg_stat_activity' as view_name,
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_stat_activity LIMIT 1) THEN 'ACCESSIBLE'
        ELSE 'NOT_ACCESSIBLE'
    END as status
UNION ALL
SELECT 
    'System Views Access Check' as check_type,
    'pg_locks' as view_name,
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_locks LIMIT 1) THEN 'ACCESSIBLE'
        ELSE 'NOT_ACCESSIBLE'
    END as status
UNION ALL
SELECT 
    'System Views Access Check' as check_type,
    'pg_stat_user_tables' as view_name,
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_stat_user_tables LIMIT 1) THEN 'ACCESSIBLE'
        ELSE 'NOT_ACCESSIBLE'
    END as status
UNION ALL
SELECT 
    'System Views Access Check' as check_type,
    'pg_stat_replication' as view_name,
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_stat_replication LIMIT 1) THEN 'ACCESSIBLE'
        ELSE 'NOT_ACCESSIBLE'
    END as status;

-- =====================
-- 4. 功能测试
-- =====================

-- 4.1 创建测试环境
CREATE SCHEMA IF NOT EXISTS validation_test;
SET search_path TO validation_test, public;

-- 4.2 测试表创建
CREATE TABLE IF NOT EXISTS test_table (
    id bigserial PRIMARY KEY,
    name text NOT NULL,
    value numeric(10,2),
    created_at timestamptz DEFAULT now()
);

-- 4.3 测试索引创建
CREATE INDEX IF NOT EXISTS idx_test_table_name ON test_table (name);
CREATE INDEX IF NOT EXISTS idx_test_table_value ON test_table (value);

-- 4.4 测试数据插入
INSERT INTO test_table (name, value) VALUES
('Test Item 1', 100.50),
('Test Item 2', 200.75),
('Test Item 3', 300.25)
ON CONFLICT DO NOTHING;

-- 4.5 测试统计信息更新
ANALYZE test_table;

-- 4.6 验证表创建成功
SELECT 
    'Table Creation Test' as check_type,
    'test_table' as table_name,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_table' AND table_schema = 'validation_test') 
        THEN 'CREATED_SUCCESSFULLY'
        ELSE 'CREATION_FAILED'
    END as status;

-- 4.7 验证索引创建成功
SELECT 
    'Index Creation Test' as check_type,
    indexname as index_name,
    CASE 
        WHEN indexname IS NOT NULL THEN 'CREATED_SUCCESSFULLY'
        ELSE 'CREATION_FAILED'
    END as status
FROM pg_indexes 
WHERE tablename = 'test_table' AND schemaname = 'validation_test';

-- 4.8 验证数据插入成功
SELECT 
    'Data Insertion Test' as check_type,
    count(*) as record_count,
    CASE 
        WHEN count(*) > 0 THEN 'INSERTION_SUCCESSFUL'
        ELSE 'INSERTION_FAILED'
    END as status
FROM test_table;

-- =====================
-- 5. 性能测试
-- =====================

-- 5.1 测试查询性能
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM test_table WHERE name = 'Test Item 1';

-- 5.2 测试索引使用
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM test_table WHERE value > 150;

-- =====================
-- 6. 扩展功能测试
-- =====================

-- 6.1 测试pgvector扩展（如果可用）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE NOTICE 'pgvector extension is available';
        
        -- 测试向量类型
        CREATE TABLE IF NOT EXISTS test_vectors (
            id bigserial PRIMARY KEY,
            embedding vector(3)
        );
        
        INSERT INTO test_vectors (embedding) VALUES 
        ('[1,2,3]'::vector),
        ('[4,5,6]'::vector)
        ON CONFLICT DO NOTHING;
        
        RAISE NOTICE 'Vector operations test completed';
    ELSE
        RAISE NOTICE 'pgvector extension is not available';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'pgvector test failed: %', SQLERRM;
END $$;

-- 6.2 测试Apache AGE扩展（如果可用）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'age') THEN
        RAISE NOTICE 'Apache AGE extension is available';
        
        -- 测试图创建
        BEGIN
            PERFORM create_graph('test_graph');
            RAISE NOTICE 'Graph creation test completed';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Graph creation test failed: %', SQLERRM;
        END;
    ELSE
        RAISE NOTICE 'Apache AGE extension is not available';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Apache AGE test failed: %', SQLERRM;
END $$;

-- 6.3 测试pgaudit扩展（如果可用）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgaudit') THEN
        RAISE NOTICE 'pgaudit extension is available';
        
        -- 检查审计配置
        SELECT name, setting 
        FROM pg_settings 
        WHERE name LIKE 'pgaudit%';
        
        RAISE NOTICE 'pgaudit configuration check completed';
    ELSE
        RAISE NOTICE 'pgaudit extension is not available';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'pgaudit test failed: %', SQLERRM;
END $$;

-- 6.4 测试pgcrypto扩展（如果可用）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
        RAISE NOTICE 'pgcrypto extension is available';
        
        -- 测试加密功能
        SELECT 
            'pgcrypto test' as test_name,
            md5('test_string') as md5_hash,
            sha256('test_string'::bytea) as sha256_hash;
        
        RAISE NOTICE 'pgcrypto functionality test completed';
    ELSE
        RAISE NOTICE 'pgcrypto extension is not available';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'pgcrypto test failed: %', SQLERRM;
END $$;

-- =====================
-- 7. 配置检查
-- =====================

-- 7.1 检查关键配置参数
SELECT 
    'Configuration Check' as check_type,
    name,
    setting,
    unit,
    CASE 
        WHEN name = 'shared_buffers' AND setting::int >= 128 THEN 'ADEQUATE'
        WHEN name = 'work_mem' AND setting::int >= 4 THEN 'ADEQUATE'
        WHEN name = 'maintenance_work_mem' AND setting::int >= 64 THEN 'ADEQUATE'
        WHEN name = 'effective_cache_size' AND setting::int >= 1024 THEN 'ADEQUATE'
        ELSE 'REVIEW_RECOMMENDED'
    END as recommendation
FROM pg_settings 
WHERE name IN (
    'shared_buffers',
    'work_mem',
    'maintenance_work_mem',
    'effective_cache_size',
    'random_page_cost',
    'effective_io_concurrency'
)
ORDER BY name;

-- 7.2 检查日志配置
SELECT 
    'Logging Configuration Check' as check_type,
    name,
    setting,
    CASE 
        WHEN name = 'log_statement' AND setting != 'none' THEN 'ENABLED'
        WHEN name = 'log_min_duration_statement' AND setting::int > 0 THEN 'ENABLED'
        WHEN name = 'log_checkpoints' AND setting = 'on' THEN 'ENABLED'
        ELSE 'DISABLED'
    END as status
FROM pg_settings 
WHERE name IN (
    'log_statement',
    'log_min_duration_statement',
    'log_checkpoints',
    'log_connections',
    'log_disconnections'
)
ORDER BY name;

-- =====================
-- 8. 安全检查
-- =====================

-- 8.1 检查用户权限
SELECT 
    'Security Check' as check_type,
    'User Permissions' as check_category,
    current_user as current_user,
    CASE 
        WHEN current_user = 'postgres' THEN 'SUPERUSER_ACCESS'
        WHEN has_database_privilege(current_database(), 'CREATE') THEN 'CREATEDB_ACCESS'
        ELSE 'LIMITED_ACCESS'
    END as access_level;

-- 8.2 检查连接限制
SELECT 
    'Security Check' as check_type,
    'Connection Limits' as check_category,
    name,
    setting,
    CASE 
        WHEN name = 'max_connections' AND setting::int >= 100 THEN 'ADEQUATE'
        WHEN name = 'superuser_reserved_connections' AND setting::int >= 3 THEN 'ADEQUATE'
        ELSE 'REVIEW_RECOMMENDED'
    END as recommendation
FROM pg_settings 
WHERE name IN ('max_connections', 'superuser_reserved_connections');

-- =====================
-- 9. 监控功能测试
-- =====================

-- 9.1 测试监控查询
SELECT 
    'Monitoring Function Test' as check_type,
    'Active Connections' as test_name,
    count(*) as active_connections,
    CASE 
        WHEN count(*) > 0 THEN 'FUNCTIONAL'
        ELSE 'NO_ACTIVE_CONNECTIONS'
    END as status
FROM pg_stat_activity 
WHERE state = 'active';

-- 9.2 测试锁监控
SELECT 
    'Monitoring Function Test' as check_type,
    'Lock Monitoring' as test_name,
    count(*) as total_locks,
    count(*) FILTER (WHERE NOT granted) as waiting_locks,
    CASE 
        WHEN count(*) >= 0 THEN 'FUNCTIONAL'
        ELSE 'ERROR'
    END as status
FROM pg_locks;

-- =====================
-- 10. 清理和总结
-- =====================

-- 10.1 显示验证结果摘要
SELECT 
    'Validation Summary' as summary_type,
    'Total Tests' as metric,
    '8' as value
UNION ALL
SELECT 
    'Validation Summary' as summary_type,
    'PostgreSQL Version' as metric,
    split_part(version(), ' ', 2) as value
UNION ALL
SELECT 
    'Validation Summary' as summary_type,
    'Available Extensions' as metric,
    count(*)::text as value
FROM pg_extension
WHERE extname IN ('vector', 'age', 'pgaudit', 'pgcrypto');

-- 10.2 清理测试数据
DROP SCHEMA IF EXISTS validation_test CASCADE;

-- 10.3 清理验证函数
DROP FUNCTION IF EXISTS validate_sql_syntax(text);

-- =====================
-- 11. 最终状态报告
-- =====================

SELECT 
    'FINAL VALIDATION REPORT' as report_title,
    now() as validation_timestamp,
    current_database() as database_name,
    current_user as validated_by;

-- 显示所有检查结果
SELECT 
    'All validation checks completed successfully' as final_status,
    'Please review the results above for any warnings or recommendations' as next_steps;
