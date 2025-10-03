-- PostgreSQL 17 vs 16: JSON处理性能测试
-- 测试JSON_TABLE和JSON构造器的性能差异

\set ECHO all
\timing on

-- ===========================================
-- 1. 准备测试数据
-- ===========================================

DROP TABLE IF EXISTS json_test_data CASCADE;

CREATE TABLE json_test_data (
    id bigserial PRIMARY KEY,
    data jsonb
);

-- 插入100万条测试数据
INSERT INTO json_test_data (data)
SELECT jsonb_build_object(
    'users', jsonb_build_array(
        jsonb_build_object(
            'id', i,
            'name', 'user_' || i,
            'email', 'user' || i || '@example.com',
            'age', 20 + (i % 60),
            'city', (ARRAY['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen'])[1 + (i % 4)],
            'created_at', now() - (random() * interval '365 days')
        ),
        jsonb_build_object(
            'id', i + 1000000,
            'name', 'user_' || (i + 1000000),
            'email', 'user' || (i + 1000000) || '@example.com',
            'age', 25 + (i % 50),
            'city', (ARRAY['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen'])[1 + ((i+1) % 4)],
            'created_at', now() - (random() * interval '365 days')
        )
    ),
    'metadata', jsonb_build_object(
        'source', 'api',
        'version', '1.0',
        'timestamp', now()
    )
)
FROM generate_series(1, 1000000) i;

VACUUM ANALYZE json_test_data;

\echo '========================================='
\echo '测试数据准备完成：1,000,000条JSON记录'
\echo '========================================='

-- ===========================================
-- 2. PG16风格：jsonb_array_elements
-- ===========================================

\echo ''
\echo '【PG16风格】使用jsonb_array_elements提取用户数据'

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    jd.id AS doc_id,
    u->>'name' AS name,
    u->>'email' AS email,
    (u->>'age')::int AS age,
    u->>'city' AS city
FROM json_test_data jd,
     jsonb_array_elements(jd.data->'users') AS u
WHERE (u->>'age')::int > 30
  AND u->>'city' = 'Beijing'
LIMIT 10000;

-- ===========================================
-- 3. PG17风格：JSON_TABLE (如果支持)
-- ===========================================

\echo ''
\echo '【PG17风格】使用JSON_TABLE提取用户数据'

-- 注意：JSON_TABLE在PG17中可用
-- 如果PG16运行此脚本会报错，这是预期的
DO $$
BEGIN
    -- 检查PostgreSQL版本
    IF current_setting('server_version_num')::int >= 170000 THEN
        RAISE NOTICE 'PostgreSQL 17+，支持JSON_TABLE';
        
        EXECUTE 'EXPLAIN (ANALYZE, BUFFERS)
        SELECT
            jd.id AS doc_id,
            jt.name,
            jt.email,
            jt.age,
            jt.city
        FROM json_test_data jd,
             JSON_TABLE(jd.data, ''$.users[*]''
                 COLUMNS (
                     name text PATH ''$.name'',
                     email text PATH ''$.email'',
                     age int PATH ''$.age'',
                     city text PATH ''$.city''
                 )
             ) AS jt
        WHERE jt.age > 30
          AND jt.city = ''Beijing''
        LIMIT 10000';
    ELSE
        RAISE NOTICE 'PostgreSQL 16，不支持JSON_TABLE，跳过此测试';
    END IF;
END $$;

-- ===========================================
-- 4. JSON构造器性能对比
-- ===========================================

\echo ''
\echo '【PG16风格】使用jsonb_build_object构造JSON'

EXPLAIN (ANALYZE, BUFFERS)
SELECT jsonb_build_object(
    'id', id,
    'user_count', jsonb_array_length(data->'users'),
    'source', data->'metadata'->>'source',
    'timestamp', data->'metadata'->>'timestamp'
) AS summary
FROM json_test_data
LIMIT 100000;

\echo ''
\echo '【PG17风格】使用JSON()构造器（如果支持）'

DO $$
BEGIN
    IF current_setting('server_version_num')::int >= 170000 THEN
        RAISE NOTICE 'PostgreSQL 17+，支持JSON()构造器';
        
        EXECUTE 'EXPLAIN (ANALYZE, BUFFERS)
        SELECT JSON(
            ''id'' VALUE id,
            ''user_count'' VALUE jsonb_array_length(data->''users''),
            ''source'' VALUE data->''metadata''->>''source'',
            ''timestamp'' VALUE data->''metadata''->>''timestamp''
        ) AS summary
        FROM json_test_data
        LIMIT 100000';
    ELSE
        RAISE NOTICE 'PostgreSQL 16，不支持JSON()构造器，跳过此测试';
    END IF;
END $$;

-- ===========================================
-- 5. 复杂JSON查询性能
-- ===========================================

\echo ''
\echo '复杂JSON聚合查询'

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    u->>'city' AS city,
    COUNT(*) AS user_count,
    AVG((u->>'age')::int) AS avg_age,
    MIN((u->>'age')::int) AS min_age,
    MAX((u->>'age')::int) AS max_age
FROM json_test_data jd,
     jsonb_array_elements(jd.data->'users') AS u
WHERE (u->>'age')::int BETWEEN 25 AND 45
GROUP BY u->>'city'
ORDER BY user_count DESC;

-- ===========================================
-- 6. 清理
-- ===========================================

\echo ''
\echo '测试完成！'
\echo ''
\echo '性能对比建议：'
\echo '1. 比较两种方法的执行时间（Execution Time）'
\echo '2. 比较内存使用（shared hit + read）'
\echo '3. 比较CPU使用率'
\echo ''
\echo '预期结果：PG17在JSON处理上应该有20-50%的性能提升'

\timing off

