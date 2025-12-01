-- PostgreSQL 17.x EXPLAIN MEMORY 功能测试
-- 版本：PostgreSQL 17+
-- 用途：测试EXPLAIN扩展功能，包括内存使用分析
-- 执行环境：PostgreSQL 17+ 或兼容版本

-- =====================
-- 1. 环境准备
-- =====================

-- 1.1 检查PostgreSQL版本
SELECT version();

-- 1.2 创建测试环境
CREATE SCHEMA IF NOT EXISTS ft_explain;
SET search_path TO ft_explain, public;

-- 创建测试表
DROP TABLE IF EXISTS test_data CASCADE;
CREATE TABLE test_data (
    id bigserial PRIMARY KEY,
    name text NOT NULL,
    category text NOT NULL,
    value numeric(10,2) NOT NULL,
    created_at timestamptz DEFAULT now(),
    metadata jsonb
);

-- 创建索引
CREATE INDEX idx_test_data_category ON test_data (category);
CREATE INDEX idx_test_data_value ON test_data (value);
CREATE INDEX idx_test_data_gin ON test_data USING gin (metadata);

-- 插入测试数据
INSERT INTO test_data (name, category, value, metadata)
SELECT 
    'Product_' || i,
    CASE (i % 5)
        WHEN 0 THEN 'Electronics'
        WHEN 1 THEN 'Books'
        WHEN 2 THEN 'Clothing'
        WHEN 3 THEN 'Home'
        ELSE 'Sports'
    END,
    (random() * 1000)::numeric(10,2),
    jsonb_build_object(
        'tags', ARRAY['tag' || (i % 10), 'category' || (i % 5)],
        'rating', (random() * 5)::numeric(3,2),
        'in_stock', (random() > 0.3)
    )
FROM generate_series(1, 10000) AS i;

-- 更新统计信息
ANALYZE test_data;

-- =====================
-- 2. 基础EXPLAIN功能测试
-- =====================

-- 2.1 标准EXPLAIN
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM test_data WHERE category = 'Electronics' LIMIT 100;

-- 2.2 EXPLAIN with VERBOSE
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT TEXT)
SELECT 
    category,
    count(*) as count,
    avg(value) as avg_value,
    max(value) as max_value
FROM test_data 
GROUP BY category 
ORDER BY count DESC;

-- 2.3 EXPLAIN with COSTS
EXPLAIN (ANALYZE, BUFFERS, COSTS, FORMAT TEXT)
SELECT t1.*, t2.name as related_name
FROM test_data t1
JOIN test_data t2 ON t1.category = t2.category
WHERE t1.value > 500
ORDER BY t1.value DESC
LIMIT 50;

-- =====================
-- 3. 内存分析功能测试
-- =====================

-- 3.1 测试EXPLAIN MEMORY支持（如果可用）
DO $$
BEGIN
    -- 尝试使用EXPLAIN MEMORY
    BEGIN
        EXECUTE 'EXPLAIN (ANALYZE, BUFFERS, MEMORY, FORMAT TEXT) 
                 SELECT * FROM test_data WHERE category = ''Electronics'' LIMIT 100';
        RAISE NOTICE 'EXPLAIN MEMORY is supported in this version';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'EXPLAIN MEMORY not supported: %', SQLERRM;
    END;
END $$;

-- 3.2 内存使用分析（兼容性方案）
-- 使用pg_stat_statements分析内存使用
DO $$
BEGIN
    -- 检查pg_stat_statements扩展
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
        RAISE NOTICE 'pg_stat_statements extension is available';
        
        -- 显示内存使用统计
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            rows,
            100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
        FROM pg_stat_statements 
        WHERE query LIKE '%test_data%'
        ORDER BY total_time DESC
        LIMIT 5;
    ELSE
        RAISE NOTICE 'pg_stat_statements extension not available';
    END IF;
END $$;

-- =====================
-- 4. 复杂查询性能分析
-- =====================

-- 4.1 聚合查询分析
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT 
    category,
    count(*) as product_count,
    avg(value) as avg_value,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY value) as median_value,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY value) as p95_value
FROM test_data
WHERE created_at >= '2023-01-01'
GROUP BY category
HAVING count(*) > 100
ORDER BY avg_value DESC;

-- 4.2 JSON查询分析
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT 
    category,
    count(*) as total_products,
    count(*) FILTER (WHERE metadata->>'in_stock' = 'true') as in_stock_count,
    avg((metadata->>'rating')::numeric) as avg_rating
FROM test_data
WHERE metadata ? 'rating'
GROUP BY category
ORDER BY avg_rating DESC;

-- 4.3 窗口函数分析
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT 
    name,
    category,
    value,
    rank() OVER (PARTITION BY category ORDER BY value DESC) as category_rank,
    lag(value) OVER (PARTITION BY category ORDER BY value DESC) as prev_value,
    value - lag(value) OVER (PARTITION BY category ORDER BY value DESC) as value_diff
FROM test_data
WHERE category IN ('Electronics', 'Books')
ORDER BY category, value DESC
LIMIT 100;

-- =====================
-- 5. 索引使用分析
-- =====================

-- 5.1 索引扫描分析
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM test_data 
WHERE category = 'Electronics' 
  AND value BETWEEN 100 AND 500
ORDER BY value DESC
LIMIT 50;

-- 5.2 GIN索引分析
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM test_data 
WHERE metadata @> '{"in_stock": true}'
  AND metadata ? 'rating'
ORDER BY (metadata->>'rating')::numeric DESC
LIMIT 20;

-- 5.3 复合条件分析
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT 
    category,
    count(*) as count,
    avg(value) as avg_value
FROM test_data
WHERE category IN ('Electronics', 'Books', 'Clothing')
  AND value > 200
  AND metadata->>'in_stock' = 'true'
GROUP BY category
ORDER BY avg_value DESC;

-- =====================
-- 6. 内存优化建议
-- =====================

-- 6.1 工作内存设置检查
SELECT 
    name,
    setting,
    unit,
    context,
    short_desc
FROM pg_settings 
WHERE name IN (
    'work_mem',
    'maintenance_work_mem',
    'shared_buffers',
    'effective_cache_size',
    'random_page_cost',
    'seq_page_cost'
);

-- 6.2 当前连接内存使用
SELECT 
    pid,
    usename,
    application_name,
    state,
    query_start,
    state_change,
    client_addr,
    backend_start
FROM pg_stat_activity 
WHERE state = 'active'
ORDER BY query_start;

-- 6.3 表大小和统计信息
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation,
    most_common_vals,
    most_common_freqs
FROM pg_stats 
WHERE schemaname = 'ft_explain'
  AND tablename = 'test_data'
ORDER BY attname;

-- =====================
-- 7. 性能基准测试
-- =====================

-- 7.1 简单查询基准
\timing on

-- 基准测试1：索引扫描
SELECT count(*) FROM test_data WHERE category = 'Electronics';

-- 基准测试2：范围查询
SELECT count(*) FROM test_data WHERE value BETWEEN 100 AND 500;

-- 基准测试3：JSON查询
SELECT count(*) FROM test_data WHERE metadata @> '{"in_stock": true}';

-- 基准测试4：聚合查询
SELECT category, count(*), avg(value) 
FROM test_data 
GROUP BY category;

\timing off

-- =====================
-- 8. 内存使用监控
-- =====================

-- 8.1 数据库大小
SELECT 
    pg_size_pretty(pg_database_size(current_database())) as database_size,
    pg_size_pretty(pg_total_relation_size('test_data')) as table_size,
    pg_size_pretty(pg_indexes_size('test_data')) as indexes_size;

-- 8.2 缓存命中率
SELECT 
    'Buffer Cache Hit Ratio' as metric,
    round(
        (sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read))), 2
    ) as percentage
FROM pg_stat_database 
WHERE datname = current_database();

-- 8.3 表统计信息
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables 
WHERE schemaname = 'ft_explain';

-- =====================
-- 9. 清理和总结
-- =====================

-- 9.1 显示测试结果摘要
SELECT 
    'EXPLAIN MEMORY Test Summary' AS test_name,
    count(*) AS total_records,
    count(DISTINCT category) AS unique_categories,
    min(value) AS min_value,
    max(value) AS max_value,
    avg(value) AS avg_value
FROM test_data;

-- 9.2 清理测试数据
-- DROP SCHEMA IF EXISTS ft_explain CASCADE;

-- =====================
-- 10. 最佳实践建议
-- =====================

/*
EXPLAIN MEMORY 使用建议：

1. 内存分析：
   - 使用 EXPLAIN (ANALYZE, BUFFERS, MEMORY) 分析内存使用
   - 关注 Hash Join、Sort、Hash Aggregate 的内存消耗
   - 监控 work_mem 设置是否合适

2. 性能优化：
   - 根据查询模式调整 work_mem
   - 使用适当的索引减少内存使用
   - 考虑分区表减少单次查询数据量

3. 监控指标：
   - 缓存命中率应保持在 95% 以上
   - 临时文件使用应最小化
   - 内存使用应合理分配

4. 故障排除：
   - 内存不足时考虑增加 work_mem
   - 大量临时文件时检查排序和哈希操作
   - 缓存命中率低时检查索引使用情况
*/