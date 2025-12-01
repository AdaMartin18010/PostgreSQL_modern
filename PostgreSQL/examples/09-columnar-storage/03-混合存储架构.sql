-- PostgreSQL 混合存储架构示例
-- 创建日期：2025-01-15
-- 版本：PostgreSQL 18.x

-- ============================================
-- 1. 混合存储架构概述
-- ============================================

-- 混合存储架构：
-- - 热数据（最近3个月）→ 行存储表（支持更新）
-- - 温数据（3-12个月）→ 行存储分区表（只读）
-- - 冷数据（12个月+）→ 列存储表（分析查询）

-- ============================================
-- 2. 创建热数据表（行存储）
-- ============================================

-- 创建热数据表（最近3个月的数据）
CREATE TABLE sales_hot (
    id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_sales_hot_date ON sales_hot(sale_date);
CREATE INDEX idx_sales_hot_product ON sales_hot(product_id);
CREATE INDEX idx_sales_hot_customer ON sales_hot(customer_id);

-- ============================================
-- 3. 创建温数据表（行存储分区表）
-- ============================================

-- 创建温数据分区表（3-12个月的数据）
CREATE TABLE sales_warm (
    id BIGINT NOT NULL,
    product_id INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id, sale_date)
) PARTITION BY RANGE (sale_date);

-- 创建分区（按月分区）
CREATE TABLE sales_warm_2024_01 PARTITION OF sales_warm
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE sales_warm_2024_02 PARTITION OF sales_warm
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- ... 更多分区

-- 创建索引
CREATE INDEX idx_sales_warm_product ON sales_warm(product_id);
CREATE INDEX idx_sales_warm_customer ON sales_warm(customer_id);

-- ============================================
-- 4. 创建冷数据表（列存储）
-- ============================================

-- 确保cstore_fdw扩展已安装
CREATE EXTENSION IF NOT EXISTS cstore_fdw;

-- 创建列存储服务器
CREATE SERVER IF NOT EXISTS cstore_server
FOREIGN DATA WRAPPER cstore_fdw;

-- 创建冷数据列存储表（12个月以上的数据）
CREATE FOREIGN TABLE sales_cold (
    id BIGINT,
    product_id INTEGER,
    sale_date DATE,
    amount DECIMAL(10,2),
    quantity INTEGER,
    customer_id INTEGER,
    store_id INTEGER
) SERVER cstore_server
OPTIONS (
    compression 'pglz',
    stripe_row_count '150000'
);

-- ============================================
-- 5. 数据归档函数
-- ============================================

-- 创建数据归档函数
CREATE OR REPLACE FUNCTION archive_sales_data()
RETURNS void AS $$
DECLARE
    archive_date DATE;
BEGIN
    -- 计算归档日期（12个月前）
    archive_date := CURRENT_DATE - INTERVAL '12 months';
    
    -- 将热数据中超过12个月的数据归档到列存储
    INSERT INTO sales_cold
    SELECT id, product_id, sale_date, amount, quantity, customer_id, store_id
    FROM sales_hot
    WHERE sale_date < archive_date
      AND id NOT IN (SELECT id FROM sales_cold);
    
    -- 删除已归档的数据（可选）
    -- DELETE FROM sales_hot WHERE sale_date < archive_date;
    
    RAISE NOTICE 'Archived sales data before %', archive_date;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 6. 查询热数据（行存储）
-- ============================================

-- 查询最近数据（使用行存储）
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    product_id,
    SUM(amount) as total_amount,
    COUNT(*) as sale_count
FROM sales_hot
WHERE sale_date >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY product_id
ORDER BY total_amount DESC
LIMIT 100;

-- ============================================
-- 7. 查询温数据（行存储分区表）
-- ============================================

-- 查询温数据（使用行存储分区表）
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    product_id,
    SUM(amount) as total_amount,
    COUNT(*) as sale_count
FROM sales_warm
WHERE sale_date >= CURRENT_DATE - INTERVAL '12 months'
  AND sale_date < CURRENT_DATE - INTERVAL '3 months'
GROUP BY product_id
ORDER BY total_amount DESC
LIMIT 100;

-- ============================================
-- 8. 查询冷数据（列存储）
-- ============================================

-- 查询历史数据（使用列存储）
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    product_id,
    SUM(amount) as total_amount,
    COUNT(*) as sale_count
FROM sales_cold
WHERE sale_date < CURRENT_DATE - INTERVAL '12 months'
GROUP BY product_id
ORDER BY total_amount DESC
LIMIT 100;

-- ============================================
-- 9. 跨时间段查询（UNION ALL）
-- ============================================

-- 跨时间段查询（合并热数据、温数据、冷数据）
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    product_id,
    SUM(amount) as total_amount,
    COUNT(*) as sale_count,
    'hot' as data_source
FROM sales_hot
WHERE sale_date >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY product_id

UNION ALL

SELECT 
    product_id,
    SUM(amount) as total_amount,
    COUNT(*) as sale_count,
    'warm' as data_source
FROM sales_warm
WHERE sale_date >= CURRENT_DATE - INTERVAL '12 months'
  AND sale_date < CURRENT_DATE - INTERVAL '3 months'
GROUP BY product_id

UNION ALL

SELECT 
    product_id,
    SUM(amount) as total_amount,
    COUNT(*) as sale_count,
    'cold' as data_source
FROM sales_cold
WHERE sale_date < CURRENT_DATE - INTERVAL '12 months'
GROUP BY product_id;

-- ============================================
-- 10. 统一查询视图
-- ============================================

-- 创建统一查询视图
CREATE OR REPLACE VIEW sales_all AS
SELECT 
    id,
    product_id,
    sale_date,
    amount,
    quantity,
    customer_id,
    store_id,
    'hot' as data_source
FROM sales_hot
WHERE sale_date >= CURRENT_DATE - INTERVAL '3 months'

UNION ALL

SELECT 
    id,
    product_id,
    sale_date,
    amount,
    quantity,
    customer_id,
    store_id,
    'warm' as data_source
FROM sales_warm
WHERE sale_date >= CURRENT_DATE - INTERVAL '12 months'
  AND sale_date < CURRENT_DATE - INTERVAL '3 months'

UNION ALL

SELECT 
    id,
    product_id,
    sale_date,
    amount,
    quantity,
    customer_id,
    store_id,
    'cold' as data_source
FROM sales_cold
WHERE sale_date < CURRENT_DATE - INTERVAL '12 months';

-- 使用统一视图查询
SELECT 
    product_id,
    SUM(amount) as total_amount,
    COUNT(*) as sale_count
FROM sales_all
WHERE sale_date >= '2023-01-01'
GROUP BY product_id
ORDER BY total_amount DESC
LIMIT 100;

-- ============================================
-- 11. 定时归档任务（使用pg_cron扩展）
-- ============================================

-- 如果安装了pg_cron扩展，可以设置定时归档任务
-- SELECT cron.schedule(
--     'archive-sales-data',  -- 任务名
--     '0 2 * * *',  -- 每天凌晨2点执行
--     $$SELECT archive_sales_data()$$
-- );

-- ============================================
-- 12. 清理
-- ============================================

-- 删除视图
-- DROP VIEW IF EXISTS sales_all;

-- 删除函数
-- DROP FUNCTION IF EXISTS archive_sales_data();

-- 删除列存储表
-- DROP FOREIGN TABLE IF EXISTS sales_cold;

-- 删除分区表
-- DROP TABLE IF EXISTS sales_warm CASCADE;

-- 删除热数据表
-- DROP TABLE IF EXISTS sales_hot;
