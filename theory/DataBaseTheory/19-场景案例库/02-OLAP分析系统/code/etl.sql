-- OLAP分析系统 - ETL脚本
-- PostgreSQL 18.x

SET search_path TO dw;

-- 1. 增量ETL函数
CREATE OR REPLACE FUNCTION etl_daily_sales(p_date DATE)
RETURNS void AS $$
DECLARE
    v_row_count INT;
BEGIN
    -- 从staging表加载到事实表
    INSERT INTO fact_sales
    SELECT 
        s.order_id,
        t.date_key,
        p.product_key,
        c.customer_key,
        st.store_key,
        s.quantity,
        s.amount,
        s.cost,
        s.discount,
        s.transaction_time
    FROM staging.orders s
    JOIN dim_time t ON s.order_date = t.full_date
    JOIN dim_product p ON s.product_id = p.product_id AND p.is_current = true
    JOIN dim_customer c ON s.customer_id = c.customer_id
    JOIN dim_store st ON s.store_id = st.store_id
    WHERE s.order_date = p_date
    ON CONFLICT (sale_id, transaction_time) DO NOTHING;
    
    GET DIAGNOSTICS v_row_count = ROW_COUNT;
    
    RAISE NOTICE '加载 % 行数据，日期：%', v_row_count, p_date;
    
    -- 刷新聚合表
    REFRESH MATERIALIZED VIEW CONCURRENTLY agg_sales_daily;
    
    -- 清理staging
    DELETE FROM staging.orders WHERE order_date = p_date;
    
END;
$$ LANGUAGE plpgsql;

-- 2. 维度更新函数（SCD Type 2）
CREATE OR REPLACE FUNCTION update_product_dimension(
    p_product_id VARCHAR(50),
    p_product_name VARCHAR(200),
    p_category_l1 VARCHAR(100),
    p_brand VARCHAR(100)
) RETURNS void AS $$
BEGIN
    -- 关闭旧版本
    UPDATE dim_product
    SET expiry_date = CURRENT_DATE,
        is_current = false
    WHERE product_id = p_product_id
      AND is_current = true;
    
    -- 插入新版本
    INSERT INTO dim_product (
        product_id, product_name, category_l1, brand,
        effective_date, is_current
    ) VALUES (
        p_product_id, p_product_name, p_category_l1, p_brand,
        CURRENT_DATE, true
    );
END;
$$ LANGUAGE plpgsql;

-- 3. 自动ETL调度
SELECT cron.schedule('daily-etl', '0 2 * * *',
    $$SELECT etl_daily_sales(CURRENT_DATE - 1)$$
);

-- 4. 性能监控
CREATE VIEW etl_performance AS
SELECT 
    date_trunc('day', created_at) as etl_date,
    COUNT(*) as rows_loaded,
    pg_size_pretty(SUM(pg_column_size(ROW(*)))) as data_size
FROM fact_sales
GROUP BY date_trunc('day', created_at)
ORDER BY etl_date DESC;
