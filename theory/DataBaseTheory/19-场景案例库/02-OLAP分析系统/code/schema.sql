-- OLAP分析系统 - Schema定义
-- PostgreSQL 18.x

-- 创建schema
CREATE SCHEMA dw;
SET search_path TO dw;

-- 事实表（按月分区）
CREATE TABLE fact_sales (
    sale_id BIGINT,
    date_key INT NOT NULL,
    product_key INT NOT NULL,
    customer_key INT NOT NULL,
    store_key INT NOT NULL,
    quantity NUMERIC(12,2),
    amount NUMERIC(15,2),
    cost NUMERIC(15,2),
    discount NUMERIC(15,2),
    profit NUMERIC(15,2) GENERATED ALWAYS AS (amount - cost - discount) STORED,
    transaction_time TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (sale_id, transaction_time)
) PARTITION BY RANGE (transaction_time);

-- 批量创建分区
DO $$
DECLARE
    start_date DATE;
    end_date DATE;
BEGIN
    FOR i IN 0..35 LOOP
        start_date := DATE '2023-01-01' + (i || ' months')::INTERVAL;
        end_date := start_date + INTERVAL '1 month';
        EXECUTE FORMAT(
            'CREATE TABLE fact_sales_%s PARTITION OF fact_sales FOR VALUES FROM (%L) TO (%L)',
            TO_CHAR(start_date, 'YYYY_MM'), start_date, end_date
        );
    END LOOP;
END $$;

-- 维度表
CREATE TABLE dim_time (
    date_key INT PRIMARY KEY,
    full_date DATE UNIQUE,
    year INT, quarter INT, month INT, day INT,
    day_of_week INT, day_name VARCHAR(10),
    is_weekend BOOLEAN, is_holiday BOOLEAN
);

CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50),
    product_name VARCHAR(200),
    category_l1 VARCHAR(100),
    category_l2 VARCHAR(100),
    brand VARCHAR(100),
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT true
);

CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE,
    customer_name VARCHAR(200),
    city VARCHAR(100),
    province VARCHAR(100)
);

CREATE TABLE dim_store (
    store_key SERIAL PRIMARY KEY,
    store_id VARCHAR(50) UNIQUE,
    store_name VARCHAR(200),
    city VARCHAR(100)
);

-- 索引
CREATE INDEX idx_fact_sales_date ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);

-- ⭐ PostgreSQL 18：多变量统计
CREATE STATISTICS fact_sales_stats (dependencies, ndistinct)
ON date_key, product_key, store_key FROM fact_sales;

-- 聚合表
CREATE MATERIALIZED VIEW agg_sales_daily AS
SELECT 
    date_key, product_key, store_key,
    SUM(amount) as amount,
    SUM(quantity) as quantity,
    COUNT(*) as tx_count
FROM fact_sales
GROUP BY date_key, product_key, store_key;

CREATE UNIQUE INDEX ON agg_sales_daily (date_key, product_key, store_key);

ANALYZE fact_sales;
