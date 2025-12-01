-- PostgreSQL 列存储查询优化示例
-- 创建日期：2025-01-15
-- 版本：PostgreSQL 18.x

-- ============================================
-- 1. 准备数据
-- ============================================

-- 假设已经创建了列存储表 sales_columnar
-- 参考 01-cstore-fdw列存储.sql

-- ============================================
-- 2. 优化技巧1：只查询需要的列
-- ============================================

-- ✅ 优化：只查询需要的列
-- 列存储优势：只扫描需要的列，I/O减少50-90%
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    product_id,
    SUM(amount) as total_amount,
    SUM(quantity) as total_quantity
FROM sales_columnar_pglz
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY product_id;

-- ❌ 不优化：查询所有列
-- 列存储优势不明显，甚至可能更慢
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM sales_columnar_pglz
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
LIMIT 100;

-- ============================================
-- 3. 优化技巧2：利用列存储聚合优势
-- ============================================

-- ✅ 优化：列存储适合聚合查询
-- 列数据可批量处理，聚合性能提升10-100倍
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    DATE_TRUNC('month', sale_date) as month,
    product_id,
    COUNT(*) as sale_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    MAX(amount) as max_amount,
    MIN(amount) as min_amount,
    STDDEV(amount) as stddev_amount
FROM sales_columnar_pglz
WHERE sale_date >= '2024-01-01'
GROUP BY DATE_TRUNC('month', sale_date), product_id
ORDER BY month, total_amount DESC;

-- ============================================
-- 4. 优化技巧3：列级过滤优化
-- ============================================

-- ✅ 优化：在列存储上使用过滤条件
-- 列存储支持列级过滤，减少I/O
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    product_id,
    SUM(amount) as total_amount,
    COUNT(*) as sale_count
FROM sales_columnar_pglz
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND amount > 1000      -- 列级过滤
  AND quantity > 5       -- 列级过滤
  AND customer_id < 5000 -- 列级过滤
GROUP BY product_id
HAVING SUM(amount) > 10000
ORDER BY total_amount DESC;

-- ============================================
-- 5. 优化技巧4：避免不必要的JOIN
-- ============================================

-- ✅ 优化：在列存储上直接查询，避免JOIN
-- 如果只需要列存储表的数据，避免与行存储表JOIN
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    product_id,
    SUM(amount) as total_amount
FROM sales_columnar_pglz
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY product_id;

-- ❌ 不优化：与行存储表JOIN
-- JOIN会降低列存储查询性能
-- EXPLAIN (ANALYZE, BUFFERS)
-- SELECT 
--     p.product_name,
--     SUM(s.amount) as total_amount
-- FROM sales_columnar_pglz s
-- JOIN products_row p ON s.product_id = p.product_id
-- WHERE s.sale_date BETWEEN '2024-01-01' AND '2024-12-31'
-- GROUP BY p.product_name;

-- ============================================
-- 6. 优化技巧5：使用合适的压缩算法
-- ============================================

-- pglz压缩：平衡压缩率和速度（推荐）
-- 适合大多数场景
SELECT 
    product_id,
    SUM(amount) as total_amount
FROM sales_columnar_pglz  -- pglz压缩
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY product_id;

-- zstd压缩：最高压缩率
-- 适合存储空间受限的场景
SELECT 
    product_id,
    SUM(amount) as total_amount
FROM sales_columnar_zstd  -- zstd压缩
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY product_id;

-- ============================================
-- 7. 优化技巧6：批量查询优化
-- ============================================

-- ✅ 优化：批量查询，减少查询次数
-- 一次查询获取多个维度的聚合结果
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    'by_product' as dimension,
    product_id::TEXT as dimension_value,
    SUM(amount) as total_amount,
    COUNT(*) as sale_count
FROM sales_columnar_pglz
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY product_id

UNION ALL

SELECT 
    'by_store' as dimension,
    store_id::TEXT as dimension_value,
    SUM(amount) as total_amount,
    COUNT(*) as sale_count
FROM sales_columnar_pglz
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY store_id;

-- ============================================
-- 8. 性能监控
-- ============================================

-- 查看列存储表统计信息
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
    seq_scan,
    seq_tup_read,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
WHERE tablename LIKE '%columnar%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
