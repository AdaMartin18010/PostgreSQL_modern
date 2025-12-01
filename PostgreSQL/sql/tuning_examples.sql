-- PostgreSQL 性能调优示例SQL
-- 版本：PostgreSQL 12+
-- 用途：性能优化、索引调优、统计信息管理
-- 执行环境：建议在沙箱环境中测试

-- =====================
-- 1. 统计信息优化
-- =====================

-- 1.1 扩展统计信息创建
-- 创建多列依赖统计
CREATE STATISTICS IF NOT EXISTS stats_multi_deps (dependencies) 
ON customer_id, order_date, product_category 
FROM orders;

-- 创建多列表达式统计
CREATE STATISTICS IF NOT EXISTS stats_expr_deps (dependencies) 
ON (extract(year from created_at)), (extract(month from created_at))
FROM events;

-- 1.2 调整列统计目标
-- 提高统计精度（默认100，最大10000）
ALTER TABLE users ALTER COLUMN email SET STATISTICS 1000;
ALTER TABLE orders ALTER COLUMN order_date SET STATISTICS 2000;
ALTER TABLE products ALTER COLUMN category_id SET STATISTICS 500;

-- 1.3 手动更新统计信息
ANALYZE users;
ANALYZE orders;
ANALYZE products;

-- 批量更新所有表统计信息
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('ANALYZE %I.%I', r.schemaname, r.tablename);
    END LOOP;
END $$;

-- =====================
-- 2. 索引优化策略
-- =====================

-- 2.1 表达式索引
-- 邮箱小写索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_lower_email 
ON users (lower(email));

-- 日期函数索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_year_month 
ON orders (extract(year from order_date), extract(month from order_date));

-- 部分索引（条件索引）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_active 
ON orders (customer_id, order_date) 
WHERE status = 'active';

-- 2.2 复合索引优化
-- 多列索引（注意列顺序）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer_date_status 
ON orders (customer_id, order_date DESC, status);

-- 覆盖索引（包含列）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_covering 
ON orders (customer_id, order_date) 
INCLUDE (total_amount, status);

-- 2.3 索引使用分析
-- 检查索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- 识别未使用的索引
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes 
WHERE idx_scan = 0 
  AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- =====================
-- 3. 查询优化技巧
-- =====================

-- 3.1 查询重写示例
-- 原始查询（可能低效）
-- SELECT * FROM orders WHERE customer_id = 123 AND order_date >= '2023-01-01';

-- 优化后的查询
SELECT 
    order_id,
    customer_id,
    order_date,
    total_amount,
    status
FROM orders 
WHERE customer_id = 123 
  AND order_date >= '2023-01-01'
ORDER BY order_date DESC
LIMIT 100;

-- 3.2 使用EXISTS替代IN
-- 低效的IN查询
-- SELECT * FROM customers WHERE customer_id IN (SELECT customer_id FROM orders WHERE status = 'completed');

-- 高效的EXISTS查询
SELECT * FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.customer_id 
      AND o.status = 'completed'
);

-- 3.3 分页优化
-- 使用游标分页（避免OFFSET大数值）
SELECT * FROM orders 
WHERE order_id > 1000  -- 上一页最后一条记录的ID
ORDER BY order_id 
LIMIT 20;

-- =====================
-- 4. 锁与等待优化
-- =====================

-- 4.1 锁等待分析
SELECT 
    l.locktype,
    l.relation::regclass AS table_name,
    l.mode,
    l.granted,
    l.pid,
    a.usename,
    a.application_name,
    a.query,
    a.state,
    a.query_start,
    now() - a.query_start AS duration
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT l.granted
ORDER BY a.query_start;

-- 4.2 死锁检测
SELECT 
    pid,
    usename,
    application_name,
    state,
    query,
    query_start,
    now() - query_start AS duration
FROM pg_stat_activity 
WHERE state = 'active' 
  AND query_start < now() - interval '30 seconds'
ORDER BY query_start;

-- =====================
-- 5. 表维护与优化
-- =====================

-- 5.1 表膨胀处理
-- 检查表膨胀
SELECT 
    schemaname,
    relname,
    n_dead_tup,
    n_live_tup,
    round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables 
WHERE n_dead_tup > 1000
ORDER BY dead_ratio DESC;

-- 手动VACUUM
VACUUM (VERBOSE, ANALYZE) orders;
VACUUM (VERBOSE, ANALYZE) users;

-- 5.2 索引重建
-- 重建索引（解决膨胀）
REINDEX TABLE CONCURRENTLY orders;
REINDEX TABLE CONCURRENTLY users;

-- 重建特定索引
REINDEX INDEX CONCURRENTLY idx_orders_customer_date;

-- 5.3 表统计信息更新
-- 更新表统计信息
ANALYZE orders;
ANALYZE users;

-- =====================
-- 6. 配置参数调优
-- =====================

-- 6.1 内存参数优化
-- 查看当前配置
SELECT name, setting, unit, context, short_desc
FROM pg_settings 
WHERE name IN (
    'shared_buffers',
    'effective_cache_size',
    'work_mem',
    'maintenance_work_mem',
    'random_page_cost',
    'effective_io_concurrency'
);

-- 6.2 工作内存优化建议
-- 根据查询复杂度调整work_mem
-- 简单查询：4MB
-- 复杂查询：16MB
-- 大型排序/哈希：64MB

-- 示例配置建议（需要重启）
-- shared_buffers = 256MB          # 25% of RAM
-- effective_cache_size = 1GB      # 75% of RAM
-- work_mem = 4MB                  # 根据查询复杂度调整
-- maintenance_work_mem = 64MB     # 用于VACUUM, CREATE INDEX等
-- random_page_cost = 1.1          # SSD存储
-- effective_io_concurrency = 200  # SSD存储

-- =====================
-- 7. 查询计划分析
-- =====================

-- 7.1 执行计划分析
-- 基本执行计划
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM orders 
WHERE customer_id = 123 
  AND order_date >= '2023-01-01'
ORDER BY order_date DESC;

-- 详细执行计划
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT c.customer_name, COUNT(o.order_id) as order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2023-01-01'
GROUP BY c.customer_id, c.customer_name
ORDER BY order_count DESC;

-- 7.2 查询计划对比
-- 创建测试表
CREATE TEMP TABLE test_orders AS 
SELECT * FROM orders WHERE order_date >= '2023-01-01';

-- 对比不同查询方式的性能
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM test_orders WHERE customer_id = 123;

-- =====================
-- 8. 监控与告警
-- =====================

-- 8.1 性能监控查询
-- 慢查询监控
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    round(100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0), 2) AS hit_percent
FROM pg_stat_statements 
WHERE mean_time > 1000  -- 超过1秒的查询
ORDER BY mean_time DESC 
LIMIT 10;

-- 8.2 资源使用监控
-- 连接数监控
SELECT 
    state,
    count(*) as connection_count
FROM pg_stat_activity 
GROUP BY state
ORDER BY connection_count DESC;

-- 锁等待监控
SELECT 
    count(*) as waiting_connections
FROM pg_locks 
WHERE NOT granted;


