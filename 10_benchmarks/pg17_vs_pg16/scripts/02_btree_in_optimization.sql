-- PostgreSQL 17 vs 16: B-tree索引多值搜索性能测试
-- 测试IN子句的优化效果

\set ECHO all
\timing on

-- ===========================================
-- 1. 准备测试数据
-- ===========================================

DROP TABLE IF EXISTS products CASCADE;

CREATE TABLE products (
    id bigserial PRIMARY KEY,
    name text NOT NULL,
    category_id int NOT NULL,
    price numeric(10,2) NOT NULL,
    stock int NOT NULL DEFAULT 0,
    created_at timestamptz DEFAULT now()
);

-- 创建B-tree索引
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_price ON products(price);

-- 插入1000万条产品数据
INSERT INTO products (name, category_id, price, stock)
SELECT
    'Product ' || i,
    (random() * 1000)::int,  -- 1000个分类
    (random() * 1000)::numeric(10,2),  -- 价格0-1000
    (random() * 1000)::int  -- 库存0-1000
FROM generate_series(1, 10000000) i;

VACUUM ANALYZE products;

\echo '========================================='
\echo '测试数据准备完成：10,000,000条产品记录'
\echo '========================================='

-- ===========================================
-- 2. 测试1：小量IN值（10个）
-- ===========================================

\echo ''
\echo '【测试1】IN子句包含10个值'

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*), AVG(price), SUM(stock)
FROM products
WHERE category_id IN (1, 5, 10, 15, 20, 25, 30, 35, 40, 45);

-- ===========================================
-- 3. 测试2：中等IN值（50个）
-- ===========================================

\echo ''
\echo '【测试2】IN子句包含50个值'

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*), AVG(price), SUM(stock)
FROM products
WHERE category_id IN (
    SELECT unnest(ARRAY[
        1,2,3,4,5,6,7,8,9,10,
        11,12,13,14,15,16,17,18,19,20,
        21,22,23,24,25,26,27,28,29,30,
        31,32,33,34,35,36,37,38,39,40,
        41,42,43,44,45,46,47,48,49,50
    ])
);

-- ===========================================
-- 4. 测试3：大量IN值（200个）
-- ===========================================

\echo ''
\echo '【测试3】IN子句包含200个值'

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*), AVG(price), SUM(stock)
FROM products
WHERE category_id IN (
    SELECT generate_series(1, 200)
);

-- ===========================================
-- 5. 测试4：组合条件
-- ===========================================

\echo ''
\echo '【测试4】IN + 范围查询组合'

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    category_id,
    COUNT(*) AS product_count,
    AVG(price) AS avg_price,
    SUM(stock) AS total_stock
FROM products
WHERE category_id IN (SELECT generate_series(1, 100))
  AND price BETWEEN 100 AND 500
  AND stock > 100
GROUP BY category_id
ORDER BY product_count DESC
LIMIT 20;

-- ===========================================
-- 6. 测试5：JOIN with IN
-- ===========================================

\echo ''
\echo '【测试5】JOIN with IN子句'

-- 创建订单表
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    id bigserial PRIMARY KEY,
    product_id bigint NOT NULL,
    quantity int NOT NULL,
    order_date date DEFAULT current_date
);

-- 插入100万条订单
INSERT INTO orders (product_id, quantity)
SELECT
    (random() * 10000000)::bigint,
    (random() * 10)::int + 1
FROM generate_series(1, 1000000);

CREATE INDEX idx_orders_product ON orders(product_id);
VACUUM ANALYZE orders;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    p.category_id,
    p.name,
    COUNT(o.id) AS order_count,
    SUM(o.quantity) AS total_quantity
FROM products p
JOIN orders o ON p.id = o.product_id
WHERE p.category_id IN (SELECT generate_series(1, 50))
GROUP BY p.category_id, p.name
HAVING COUNT(o.id) > 10
ORDER BY order_count DESC
LIMIT 100;

-- ===========================================
-- 7. 性能统计分析
-- ===========================================

\echo ''
\echo '【索引使用统计】'

SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE tablename IN ('products', 'orders')
ORDER BY idx_scan DESC;

-- ===========================================
-- 8. 清理
-- ===========================================

\echo ''
\echo '测试完成！'
\echo ''
\echo '性能对比重点：'
\echo '1. PG17应该将多个IN值合并为单次B-tree扫描'
\echo '2. 查看执行计划中的"Index Scan"次数'
\echo '3. PG17预期有15-30%的性能提升'
\echo '4. 特别关注大量IN值（100+）的场景'

\timing off

