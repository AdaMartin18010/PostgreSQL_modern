-- PostgreSQL cstore_fdw列存储示例
-- 创建日期：2025-01-15
-- 版本：PostgreSQL 18.x

-- ============================================
-- 1. 安装cstore_fdw扩展
-- ============================================

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS cstore_fdw;

-- 验证扩展安装
SELECT * FROM pg_extension WHERE extname = 'cstore_fdw';

-- ============================================
-- 2. 创建列存储服务器
-- ============================================

-- 创建列存储服务器
CREATE SERVER cstore_server
FOREIGN DATA WRAPPER cstore_fdw;

-- ============================================
-- 3. 创建测试数据（行存储表）
-- ============================================

-- 创建销售事实表（行存储）
CREATE TABLE sales_row (
    id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 插入测试数据
INSERT INTO sales_row (product_id, sale_date, amount, quantity, customer_id, store_id)
SELECT 
    (random() * 1000)::INTEGER + 1 as product_id,
    CURRENT_DATE - (random() * 365)::INTEGER as sale_date,
    (random() * 10000 + 100)::DECIMAL(10,2) as amount,
    (random() * 10 + 1)::INTEGER as quantity,
    (random() * 10000)::INTEGER + 1 as customer_id,
    (random() * 100)::INTEGER + 1 as store_id
FROM generate_series(1, 1000000);

-- 查看行存储表大小
SELECT 
    pg_size_pretty(pg_total_relation_size('sales_row')) as row_storage_size;

-- ============================================
-- 4. 创建列存储表
-- ============================================

-- 创建列存储表（使用pglz压缩）
CREATE FOREIGN TABLE sales_columnar_pglz (
    id BIGINT,
    product_id INTEGER,
    sale_date DATE,
    amount DECIMAL(10,2),
    quantity INTEGER,
    customer_id INTEGER,
    store_id INTEGER
) SERVER cstore_server
OPTIONS (
    compression 'pglz',  -- pglz压缩，压缩率70%
    stripe_row_count '150000'  -- 条带行数
);

-- 创建列存储表（使用zstd压缩）
CREATE FOREIGN TABLE sales_columnar_zstd (
    id BIGINT,
    product_id INTEGER,
    sale_date DATE,
    amount DECIMAL(10,2),
    quantity INTEGER,
    customer_id INTEGER,
    store_id INTEGER
) SERVER cstore_server
OPTIONS (
    compression 'zstd',  -- zstd压缩，压缩率80%
    stripe_row_count '150000'
);

-- ============================================
-- 5. 导入数据到列存储表
-- ============================================

-- 导入数据到pglz压缩的列存储表
INSERT INTO sales_columnar_pglz
SELECT id, product_id, sale_date, amount, quantity, customer_id, store_id
FROM sales_row
WHERE sale_date < CURRENT_DATE - INTERVAL '3 months';  -- 历史数据

-- 导入数据到zstd压缩的列存储表
INSERT INTO sales_columnar_zstd
SELECT id, product_id, sale_date, amount, quantity, customer_id, store_id
FROM sales_row
WHERE sale_date < CURRENT_DATE - INTERVAL '3 months';  -- 历史数据

-- ============================================
-- 6. 查看存储大小对比
-- ============================================

-- 查看行存储表大小
SELECT 
    '行存储' as storage_type,
    pg_size_pretty(pg_total_relation_size('sales_row')) as table_size
FROM sales_row
LIMIT 1;

-- 查看列存储表大小（pglz）
SELECT 
    '列存储(pglz)' as storage_type,
    pg_size_pretty(pg_total_relation_size('sales_columnar_pglz')) as table_size;

-- 查看列存储表大小（zstd）
SELECT 
    '列存储(zstd)' as storage_type,
    pg_size_pretty(pg_total_relation_size('sales_columnar_zstd')) as table_size;

-- ============================================
-- 7. 列存储查询示例
-- ============================================

-- 示例1：只查询需要的列（列存储优势）
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    product_id,
    SUM(amount) as total_amount,
    SUM(quantity) as total_quantity,
    COUNT(*) as sale_count
FROM sales_columnar_pglz
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY product_id
ORDER BY total_amount DESC
LIMIT 100;

-- 示例2：聚合查询（列存储优势）
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    DATE_TRUNC('month', sale_date) as month,
    product_id,
    COUNT(*) as sale_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    MAX(amount) as max_amount,
    MIN(amount) as min_amount
FROM sales_columnar_pglz
WHERE sale_date >= '2024-01-01'
GROUP BY DATE_TRUNC('month', sale_date), product_id
ORDER BY month, total_amount DESC;

-- 示例3：列级过滤（列存储优势）
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    product_id,
    SUM(amount) as total_amount
FROM sales_columnar_pglz
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND amount > 1000  -- 列级过滤
  AND quantity > 5   -- 列级过滤
GROUP BY product_id
HAVING SUM(amount) > 10000
ORDER BY total_amount DESC;

-- ============================================
-- 8. 性能对比
-- ============================================

-- 行存储查询（对比基准）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    product_id,
    SUM(amount) as total_amount,
    SUM(quantity) as total_quantity
FROM sales_row
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY product_id
ORDER BY total_amount DESC
LIMIT 100;

-- 列存储查询（性能对比）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    product_id,
    SUM(amount) as total_amount,
    SUM(quantity) as total_quantity
FROM sales_columnar_pglz
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY product_id
ORDER BY total_amount DESC
LIMIT 100;

-- ============================================
-- 9. 清理
-- ============================================

-- 删除列存储表
-- DROP FOREIGN TABLE IF EXISTS sales_columnar_pglz;
-- DROP FOREIGN TABLE IF EXISTS sales_columnar_zstd;

-- 删除行存储表
-- DROP TABLE IF EXISTS sales_row;

-- 删除列存储服务器
-- DROP SERVER IF EXISTS cstore_server;

-- 删除扩展
-- DROP EXTENSION IF EXISTS cstore_fdw;
