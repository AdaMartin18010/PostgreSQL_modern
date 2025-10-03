-- PostgreSQL 17 新特性性能测试脚本
-- 版本：PostgreSQL 17+
-- 用途：测试和验证PostgreSQL 17新特性的性能表现
-- 运行前：确保已创建测试数据库和必要的扩展

-- 设置测试环境
\set ON_ERROR_STOP on
\echo '=== PostgreSQL 17 新特性性能测试 ==='
\echo '测试时间: ' `date`
\echo ''

-- 创建测试模式
CREATE SCHEMA IF NOT EXISTS pg17_test;
SET search_path = pg17_test, public;

-- 1. JSON_TABLE() 性能测试
\echo '=== 1. JSON_TABLE() 性能测试 ==='

-- 创建测试表
CREATE TABLE IF NOT EXISTS json_test_data (
    id SERIAL PRIMARY KEY,
    log_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 插入测试数据（模拟API日志）
INSERT INTO json_test_data (log_data)
SELECT jsonb_build_object(
    'request_id', 'req_' || generate_series,
    'timestamp', NOW() - (random() * interval '30 days'),
    'user_id', floor(random() * 10000)::int,
    'action', (ARRAY['login', 'logout', 'purchase', 'view', 'search'])[floor(random() * 5) + 1],
    'metadata', jsonb_build_object(
        'ip_address', '192.168.1.' || floor(random() * 255)::int,
        'user_agent', 'Mozilla/5.0...',
        'response_time', floor(random() * 1000)::int,
        'status_code', (ARRAY[200, 201, 400, 401, 404, 500])[floor(random() * 6) + 1]
    ),
    'items', jsonb_build_array(
        jsonb_build_object('id', floor(random() * 1000)::int, 'name', 'item_' || floor(random() * 1000)::int),
        jsonb_build_object('id', floor(random() * 1000)::int, 'name', 'item_' || floor(random() * 1000)::int)
    )
)
FROM generate_series(1, 100000);

-- 创建GIN索引
CREATE INDEX IF NOT EXISTS idx_json_test_gin ON json_test_data USING GIN (log_data);

-- 测试JSON_TABLE性能
\echo '测试JSON_TABLE查询性能...'
\timing on

EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT 
    u.user_id,
    u.action,
    u.response_time,
    u.status_code,
    COUNT(*) as action_count
FROM json_test_data,
JSON_TABLE(
    log_data,
    '$.metadata'
    COLUMNS (
        user_id INT PATH '$.user_id',
        action TEXT PATH '$.action',
        response_time INT PATH '$.response_time',
        status_code INT PATH '$.status_code'
    )
) AS u
WHERE log_data @> '{"metadata": {"status_code": 200}}'
GROUP BY u.user_id, u.action, u.response_time, u.status_code
ORDER BY action_count DESC
LIMIT 20;

\timing off

-- 2. VACUUM内存管理优化测试
\echo ''
\echo '=== 2. VACUUM内存管理优化测试 ==='

-- 创建测试表（模拟高更新频率的表）
CREATE TABLE IF NOT EXISTS vacuum_test (
    id SERIAL PRIMARY KEY,
    data TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 插入测试数据
INSERT INTO vacuum_test (data)
SELECT 'test_data_' || generate_series || '_' || md5(random()::text)
FROM generate_series(1, 1000000);

-- 模拟大量更新操作（产生死元组）
\echo '模拟大量更新操作...'
DO $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 1..100000 LOOP
        UPDATE vacuum_test 
        SET data = 'updated_' || i || '_' || md5(random()::text),
            updated_at = NOW()
        WHERE id = floor(random() * 1000000)::int + 1;
        
        IF i % 10000 = 0 THEN
            RAISE NOTICE '已更新 % 条记录', i;
        END IF;
    END LOOP;
END $$;

-- 检查膨胀情况
\echo '检查表膨胀情况...'
SELECT 
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    ROUND((n_dead_tup::NUMERIC / (n_live_tup + n_dead_tup)::NUMERIC) * 100, 2) as bloat_ratio
FROM pg_stat_user_tables 
WHERE tablename = 'vacuum_test';

-- 测试VACUUM性能
\echo '测试VACUUM性能...'
\timing on
VACUUM ANALYZE vacuum_test;
\timing off

-- 3. 流式I/O顺序读取测试
\echo ''
\echo '=== 3. 流式I/O顺序读取测试 ==='

-- 创建大表进行顺序扫描测试
CREATE TABLE IF NOT EXISTS sequential_scan_test (
    id BIGSERIAL PRIMARY KEY,
    data1 TEXT,
    data2 TEXT,
    data3 TEXT,
    data4 TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 插入大量数据
\echo '插入测试数据...'
INSERT INTO sequential_scan_test (data1, data2, data3, data4)
SELECT 
    'data1_' || generate_series,
    'data2_' || generate_series,
    'data3_' || generate_series,
    'data4_' || generate_series
FROM generate_series(1, 5000000);

-- 测试顺序扫描性能
\echo '测试顺序扫描性能...'
\timing on

EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT COUNT(*), AVG(LENGTH(data1)), MAX(created_at)
FROM sequential_scan_test
WHERE created_at > NOW() - interval '1 day';

\timing off

-- 4. 高并发写入测试
\echo ''
\echo '=== 4. 高并发写入测试 ==='

-- 创建并发测试表
CREATE TABLE IF NOT EXISTS concurrent_write_test (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER,
    data TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_concurrent_write_thread ON concurrent_write_test (thread_id);

-- 测试并发写入性能（使用pgbench脚本）
\echo '创建pgbench测试脚本...'
\copy (SELECT 'INSERT INTO pg17_test.concurrent_write_test (thread_id, data) VALUES (' || floor(random() * 10)::int || ', ''concurrent_data_' || generate_series || ''');') TO 'concurrent_write.sql'

\echo '运行并发写入测试...'
\timing on
\! pgbench -n -M prepared -T 30 -c 16 -j 4 -f concurrent_write.sql postgres
\timing off

-- 5. B-tree索引多值搜索测试
\echo ''
\echo '=== 5. B-tree索引多值搜索测试 ==='

-- 创建多值搜索测试表
CREATE TABLE IF NOT EXISTS multi_value_search_test (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20),
    age INTEGER,
    city VARCHAR(50),
    salary NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 插入测试数据
INSERT INTO multi_value_search_test (status, age, city, salary)
SELECT 
    (ARRAY['active', 'inactive', 'pending', 'suspended'])[floor(random() * 4) + 1],
    floor(random() * 50)::int + 18,
    (ARRAY['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Hangzhou', 'Nanjing', 'Wuhan', 'Chengdu'])[floor(random() * 8) + 1],
    floor(random() * 50000)::numeric + 30000
FROM generate_series(1, 1000000);

-- 创建复合索引
CREATE INDEX IF NOT EXISTS idx_multi_search ON multi_value_search_test (status, age, city);

-- 测试多值搜索性能
\echo '测试多值搜索性能...'
\timing on

EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT COUNT(*), AVG(salary), MAX(created_at)
FROM multi_value_search_test 
WHERE status = 'active' 
  AND age BETWEEN 25 AND 35 
  AND city IN ('Beijing', 'Shanghai', 'Guangzhou')
  AND salary > 50000;

\timing off

-- 6. 连接优化测试（sslnegotiation=direct）
\echo ''
\echo '=== 6. 连接优化测试 ==='

-- 测试连接建立时间
\echo '测试连接建立时间...'
\timing on
\! for i in {1..10}; do psql -c "SELECT 1;" > /dev/null 2>&1; done
\timing off

-- 7. 性能测试总结
\echo ''
\echo '=== 性能测试总结 ==='
\echo '测试完成时间: ' `date`
\echo ''
\echo '测试项目:'
\echo '1. JSON_TABLE() 函数性能'
\echo '2. VACUUM内存管理优化'
\echo '3. 流式I/O顺序读取'
\echo '4. 高并发写入吞吐量'
\echo '5. B-tree索引多值搜索'
\echo '6. 连接建立优化'
\echo ''
\echo '建议:'
\echo '- 对比PostgreSQL 16的性能数据'
\echo '- 在生产环境中验证这些改进'
\echo '- 根据实际负载调整相关参数'
\echo '- 监控长期性能趋势'

-- 清理测试数据（可选）
-- DROP SCHEMA IF EXISTS pg17_test CASCADE;
