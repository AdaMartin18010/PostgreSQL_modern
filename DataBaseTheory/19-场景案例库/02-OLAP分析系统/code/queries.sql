-- OLAP分析系统 - 典型查询
-- PostgreSQL 18.x

SET search_path TO dw;

-- Q1: 多维销售分析
SELECT 
    t.year,
    t.quarter,
    p.category_l1,
    SUM(s.amount) as total_sales,
    SUM(s.profit) as total_profit,
    COUNT(*) as tx_count,
    COUNT(DISTINCT s.customer_key) as unique_customers
FROM fact_sales s
JOIN dim_time t ON s.date_key = t.date_key
JOIN dim_product p ON s.product_key = p.product_key
WHERE t.year IN (2024, 2025)
GROUP BY CUBE (t.year, t.quarter, p.category_l1)
ORDER BY total_sales DESC NULLS LAST;

-- Q2: 同比环比分析
WITH current_year AS (
    SELECT 
        t.month,
        p.category_l1,
        SUM(s.amount) as amount
    FROM fact_sales s
    JOIN dim_time t ON s.date_key = t.date_key
    JOIN dim_product p ON s.product_key = p.product_key
    WHERE t.year = 2025
    GROUP BY t.month, p.category_l1
),
last_year AS (
    SELECT 
        t.month,
        p.category_l1,
        SUM(s.amount) as amount
    FROM fact_sales s
    JOIN dim_time t ON s.date_key = t.date_key
    JOIN dim_product p ON s.product_key = p.product_key
    WHERE t.year = 2024
    GROUP BY t.month, p.category_l1
)
SELECT 
    c.month,
    c.category_l1,
    c.amount as current_amount,
    l.amount as last_year_amount,
    ROUND((c.amount - l.amount) * 100.0 / l.amount, 2) as yoy_growth_pct
FROM current_year c
LEFT JOIN last_year l USING (month, category_l1)
ORDER BY c.month, c.category_l1;

-- Q3: Top-N商品排行
SELECT 
    p.product_name,
    p.category_l1,
    SUM(s.amount) as total_sales,
    SUM(s.quantity) as total_quantity,
    RANK() OVER (PARTITION BY p.category_l1 ORDER BY SUM(s.amount) DESC) as rank_in_category
FROM fact_sales s
JOIN dim_product p ON s.product_key = p.product_key
JOIN dim_time t ON s.date_key = t.date_key
WHERE t.year = 2025 AND t.quarter = 4
GROUP BY p.product_key, p.product_name, p.category_l1
HAVING SUM(s.amount) > 100000
ORDER BY total_sales DESC
LIMIT 100;

-- Q4: 客户RFM分析
WITH customer_rfm AS (
    SELECT 
        customer_key,
        MAX(transaction_time) as last_purchase,
        COUNT(*) as frequency,
        SUM(amount) as monetary
    FROM fact_sales
    WHERE transaction_time > NOW() - INTERVAL '1 year'
    GROUP BY customer_key
)
SELECT 
    customer_key,
    EXTRACT(DAY FROM NOW() - last_purchase) as recency_days,
    frequency,
    monetary,
    NTILE(5) OVER (ORDER BY EXTRACT(DAY FROM NOW() - last_purchase) DESC) as r_score,
    NTILE(5) OVER (ORDER BY frequency) as f_score,
    NTILE(5) OVER (ORDER BY monetary) as m_score
FROM customer_rfm;

-- Q5: 使用聚合表的快速查询
SELECT 
    t.full_date,
    p.product_name,
    a.amount,
    a.quantity
FROM agg_sales_daily a
JOIN dim_time t ON a.date_key = t.date_key
JOIN dim_product p ON a.product_key = p.product_key
WHERE t.year = 2025 AND t.month = 12
ORDER BY a.amount DESC
LIMIT 100;

-- ⭐ PostgreSQL 18优化：
-- 1. 并行查询（自动）
-- 2. 分区裁剪
-- 3. 多变量统计（准确估计）
-- 4. 计划缓存

