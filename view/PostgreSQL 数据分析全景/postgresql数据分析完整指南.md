# PostgreSQL 数据分析完整指南

## 现代数据分析栈的核心引擎

---

**版本**: v1.0
**核心观点**: PostgreSQL 是当前数据分析领域最主流、最全面的选择
**适用场景**: 从初创公司到企业级的全场景数据分析

---

## 目录

- [PostgreSQL 数据分析完整指南](#postgresql-数据分析完整指南)
  - [现代数据分析栈的核心引擎](#现代数据分析栈的核心引擎)
  - [目录](#目录)
  - [1. PostgreSQL 的核心优势](#1-postgresql-的核心优势)
  - [1.1 为什么 PostgreSQL 是数据分析的首选](#11-为什么-postgresql-是数据分析的首选)
    - [核心优势矩阵](#核心优势矩阵)
    - [数据分析关键特性](#数据分析关键特性)
  - [2. 基于 PostgreSQL 的数据分析架构](#2-基于-postgresql-的数据分析架构)
  - [2.1 现代 PostgreSQL 数据分析栈](#21-现代-postgresql-数据分析栈)
  - [2.2 架构模式详解](#22-架构模式详解)
    - [模式一: 单体 PostgreSQL 数据仓库](#模式一-单体-postgresql-数据仓库)
    - [模式二: PostgreSQL + 数据湖 (Lakehouse)](#模式二-postgresql--数据湖-lakehouse)
    - [模式三: 分布式 PostgreSQL (Citus)](#模式三-分布式-postgresql-citus)
  - [3. SQL 全面建模能力](#3-sql-全面建模能力)
  - [3.1 维度建模 (Kimball 方法)](#31-维度建模-kimball-方法)
    - [星型模型实现](#星型模型实现)
    - [雪花模型实现](#雪花模型实现)
  - [3.2 Data Vault 2.0 建模](#32-data-vault-20-建模)
  - [3.3 宽表模型 (BigQuery/ClickHouse 风格)](#33-宽表模型-bigqueryclickhouse-风格)
  - [4. 应用场景深度分析](#4-应用场景深度分析)
  - [4.1 电商数据分析](#41-电商数据分析)
    - [核心指标计算](#核心指标计算)
  - [4.2 用户行为分析](#42-用户行为分析)
  - [4.3 实时分析 (结合 TimescaleDB)](#43-实时分析-结合-timescaledb)
  - [4.4 地理空间分析 (PostGIS)](#44-地理空间分析-postgis)
  - [5. 生态工具集成](#5-生态工具集成)
  - [5.1 dbt (数据构建工具)](#51-dbt-数据构建工具)
    - [dbt 项目结构](#dbt-项目结构)
    - [dbt 模型示例](#dbt-模型示例)
  - [5.2 数据可视化集成](#52-数据可视化集成)
    - [Apache Superset](#apache-superset)
    - [Metabase](#metabase)
  - [5.3 数据质量测试 (Great Expectations)](#53-数据质量测试-great-expectations)
- [6. 性能优化与扩展](#6-性能优化与扩展)
  - [6.1 索引策略](#61-索引策略)
  - [6.2 分区策略](#62-分区策略)
  - [6.3 查询优化](#63-查询优化)
  - [6.4 读写分离](#64-读写分离)
  - [7. 现代数据栈中的 PostgreSQL](#7-现代数据栈中的-postgresql)
  - [7.1 完整技术栈推荐](#71-完整技术栈推荐)
  - [7.2 云原生 PostgreSQL](#72-云原生-postgresql)
  - [7.3 PostgreSQL vs 专用数据仓库](#73-postgresql-vs-专用数据仓库)
  - [附录](#附录)
  - [A. 实用查询模板](#a-实用查询模板)
    - [A.1 数据探查](#a1-数据探查)
    - [A.2 维护脚本](#a2-维护脚本)
  - [B. 参考资源](#b-参考资源)

---

## 1. PostgreSQL 的核心优势

## 1.1 为什么 PostgreSQL 是数据分析的首选

### 核心优势矩阵

| 维度 | PostgreSQL | 其他数据库 | 优势说明 |
|-----|-----------|-----------|---------|
| **功能完整性** | ⭐⭐⭐⭐⭐ | MySQL: ⭐⭐⭐☆☆ | 窗口函数、CTE、复杂查询 |
| **标准兼容性** | ⭐⭐⭐⭐⭐ | Oracle: ⭐⭐⭐⭐☆ | 最符合 SQL 标准 |
| **扩展性** | ⭐⭐⭐⭐⭐ | SQL Server: ⭐⭐⭐☆☆ | 丰富扩展生态 |
| **成本效益** | ⭐⭐⭐⭐⭐ | 商业DB: ⭐⭐☆☆☆ | 开源免费 |
| **云原生支持** | ⭐⭐⭐⭐⭐ | 各种 | 所有主流云支持 |
| **JSON/半结构化** | ⭐⭐⭐⭐⭐ | MongoDB: ⭐⭐⭐⭐☆ | JSONB + 关系型双重优势 |

### 数据分析关键特性

```sql
-- 1. 强大的窗口函数
SELECT
    user_id,
    amount,
    SUM(amount) OVER (PARTITION BY user_id ORDER BY date) as running_total,
    AVG(amount) OVER (PARTITION BY user_id) as user_avg,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) as rank
FROM orders;

-- 2. 递归 CTE（层次分析）
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 0 as level
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree;

-- 3. 高级聚合
SELECT
    date_trunc('month', order_date) as month,
    user_id,
    array_agg(DISTINCT product_id) as products_bought,
    jsonb_object_agg(product_id, quantity) as product_quantities,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY amount) as median_amount
FROM orders
GROUP BY 1, 2;
```

---

## 2. 基于 PostgreSQL 的数据分析架构

## 2.1 现代 PostgreSQL 数据分析栈

```text
┌─────────────────────────────────────────────────────────────────┐
│                        数据消费层                                │
│    BI工具(Superset/Metabase) │ 报表系统 │ 数据API │ Jupyter    │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                        数据建模层 (dbt)                          │
│    数据源 → Staging → 维度模型 → 指标层 → 数据产品              │
│         (raw)      (dim/fact)   (marts)   (exposures)          │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                        核心存储层 (PostgreSQL)                    │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│    │   OLTP 库    │  │  数据仓库    │  │  数据集市    │        │
│    │  (业务数据)  │  │  (清洗整合)  │  │  (主题模型)  │        │
│    └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                  │
│    扩展: TimescaleDB(时序) │ PostGIS(地理) │ Citus(分布式)     │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                        数据采集层                                │
│    FDW(外部数据) │ CDC(Debezium) │ ETL(Airbyte/Meltano)        │
└─────────────────────────────────────────────────────────────────┘
```

## 2.2 架构模式详解

### 模式一: 单体 PostgreSQL 数据仓库

**适用**: 中小型企业，数据量 < 1TB

```sql
-- 数据库设计
CREATE DATABASE analytics_warehouse;

-- Schema 分层
CREATE SCHEMA raw;        -- 原始数据层
CREATE SCHEMA staging;    -- 清洗转换层
CREATE SCHEMA warehouse;  -- 维度模型层
CREATE SCHEMA marts;      -- 数据集市层

-- 用户权限管理
CREATE ROLE analyst WITH LOGIN PASSWORD 'secure_pass';
GRANT USAGE ON SCHEMA warehouse TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA warehouse TO analyst;
```

### 模式二: PostgreSQL + 数据湖 (Lakehouse)

**适用**: 大数据量，需要存原始数据

```sql
-- 使用 FDW 访问数据湖 (S3/MinIO)
CREATE EXTENSION parquet_fdw;

CREATE SERVER parquet_server FOREIGN DATA WRAPPER parquet_fdw;

CREATE FOREIGN TABLE raw.events (
    event_id UUID,
    user_id BIGINT,
    event_type TEXT,
    event_time TIMESTAMP,
    properties JSONB
)
SERVER parquet_server
OPTIONS (filename 's3://data-lake/events/*.parquet');

-- 物化视图加速
CREATE MATERIALIZED VIEW warehouse.daily_events AS
SELECT
    date_trunc('day', event_time) as day,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users
FROM raw.events
GROUP BY 1, 2;

CREATE INDEX idx_daily_events ON warehouse.daily_events(day, event_type);
```

### 模式三: 分布式 PostgreSQL (Citus)

**适用**: 海量数据，需要水平扩展

```sql
-- Citus 分布式表
SELECT create_distributed_table('events', 'user_id');

-- 分布式聚合查询
SELECT
    date_trunc('hour', event_time) as hour,
    event_type,
    COUNT(*) as cnt,
    COUNT(DISTINCT user_id) as uniq_users
FROM events
WHERE event_time >= NOW() - INTERVAL '7 days'
GROUP BY 1, 2
ORDER BY 1;
```

---

## 3. SQL 全面建模能力

## 3.1 维度建模 (Kimball 方法)

### 星型模型实现

```sql
-- 1. 日期维度表
CREATE TABLE warehouse.dim_date (
    date_key INTEGER PRIMARY KEY,  -- YYYYMMDD 格式
    full_date DATE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    day INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(10),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER
);

-- 生成日期维度数据
INSERT INTO warehouse.dim_date
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER as date_key,
    d as full_date,
    EXTRACT(YEAR FROM d) as year,
    EXTRACT(QUARTER FROM d) as quarter,
    EXTRACT(MONTH FROM d) as month,
    EXTRACT(DAY FROM d) as day,
    EXTRACT(DOW FROM d) as day_of_week,
    TO_CHAR(d, 'Day') as day_name,
    EXTRACT(DOW FROM d) IN (0, 6) as is_weekend,
    FALSE as is_holiday  -- 需单独维护节假日
FROM generate_series('2020-01-01'::DATE, '2030-12-31'::DATE, '1 day'::INTERVAL) d;

-- 2. 客户维度表 (SCD Type 2 - 缓慢变化维)
CREATE TABLE warehouse.dim_customer (
    customer_sk SERIAL PRIMARY KEY,  -- 代理键
    customer_id VARCHAR(50) NOT NULL, -- 业务主键
    customer_name VARCHAR(100),
    email VARCHAR(100),
    country VARCHAR(50),
    customer_segment VARCHAR(20),
    valid_from TIMESTAMP DEFAULT '1900-01-01',
    valid_to TIMESTAMP DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE,
    UNIQUE(customer_id, valid_from)
);

-- SCD Type 2 更新逻辑
CREATE OR REPLACE FUNCTION warehouse.update_customer_dim()
RETURNS TRIGGER AS $$
BEGIN
    -- 关闭旧记录
    UPDATE warehouse.dim_customer
    SET valid_to = CURRENT_TIMESTAMP,
        is_current = FALSE
    WHERE customer_id = NEW.customer_id
      AND is_current = TRUE;

    -- 插入新记录
    INSERT INTO warehouse.dim_customer (
        customer_id, customer_name, email, country,
        customer_segment, valid_from, is_current
    ) VALUES (
        NEW.customer_id, NEW.customer_name, NEW.email, NEW.country,
        NEW.segment, CURRENT_TIMESTAMP, TRUE
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. 订单事实表
CREATE TABLE warehouse.fact_orders (
    order_sk BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    date_key INTEGER REFERENCES warehouse.dim_date(date_key),
    customer_sk INTEGER REFERENCES warehouse.dim_customer(customer_sk),
    product_sk INTEGER,  -- 假设有产品维度
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    sales_amount DECIMAL(10,2),
    cost_amount DECIMAL(10,2),
    profit_amount DECIMAL(10,2),
    order_timestamp TIMESTAMP
);

-- 分区优化 (按月分区)
CREATE TABLE warehouse.fact_orders_2024_01 PARTITION OF warehouse.fact_orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- 4. 星型查询
SELECT
    d.year,
    d.month,
    c.country,
    c.customer_segment,
    COUNT(DISTINCT f.order_id) as order_count,
    SUM(f.sales_amount) as total_sales,
    SUM(f.profit_amount) as total_profit,
    AVG(f.sales_amount) as avg_order_value,
    SUM(f.sales_amount) / LAG(SUM(f.sales_amount)) OVER (
        PARTITION BY c.country ORDER BY d.year, d.month
    ) - 1 as mom_growth
FROM warehouse.fact_orders f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_customer c ON f.customer_sk = c.customer_sk
WHERE d.year = 2024
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2, total_sales DESC;
```

### 雪花模型实现

```sql
-- 产品类别维度 (标准化)
CREATE TABLE warehouse.dim_category (
    category_sk SERIAL PRIMARY KEY,
    category_id VARCHAR(20),
    category_name VARCHAR(50),
    department VARCHAR(50)
);

-- 产品维度 (引用类别)
CREATE TABLE warehouse.dim_product (
    product_sk SERIAL PRIMARY KEY,
    product_id VARCHAR(50),
    product_name VARCHAR(100),
    category_sk INTEGER REFERENCES warehouse.dim_category(category_sk),
    brand VARCHAR(50),
    unit_cost DECIMAL(10,2)
);

-- 雪花查询
SELECT
    c.department,
    c.category_name,
    p.brand,
    SUM(f.sales_amount) as sales
FROM warehouse.fact_orders f
JOIN warehouse.dim_product p ON f.product_sk = p.product_sk
JOIN warehouse.dim_category c ON p.category_sk = c.category_sk
GROUP BY 1, 2, 3;
```

## 3.2 Data Vault 2.0 建模

```sql
-- 1. Hub (业务主键)
CREATE TABLE warehouse.hub_customer (
    customer_hk UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- Hash Key
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_source VARCHAR(50)
);

-- 2. Link (关系)
CREATE TABLE warehouse.link_customer_order (
    link_hk UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_hk UUID REFERENCES warehouse.hub_customer(customer_hk),
    order_hk UUID,  -- 引用 hub_order
    load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_source VARCHAR(50),
    UNIQUE(customer_hk, order_hk)
);

-- 3. Satellite (属性)
CREATE TABLE warehouse.sat_customer_details (
    customer_hk UUID REFERENCES warehouse.hub_customer(customer_hk),
    load_date TIMESTAMP,
    load_end_date TIMESTAMP DEFAULT '9999-12-31',
    hash_diff UUID,  -- 检测变化
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    PRIMARY KEY (customer_hk, load_date)
);

-- Data Vault 查询 (Point-in-Time)
SELECT
    h.customer_id,
    s.customer_name,
    s.email,
    s.load_date as effective_date
FROM warehouse.hub_customer h
JOIN warehouse.sat_customer_details s ON h.customer_hk = s.customer_hk
WHERE s.load_date <= '2024-01-15'
  AND s.load_end_date > '2024-01-15';
```

## 3.3 宽表模型 (BigQuery/ClickHouse 风格)

```sql
-- 用户行为宽表 (反规范化，查询性能优先)
CREATE TABLE warehouse.user_behavior_wide (
    event_id UUID PRIMARY KEY,
    event_time TIMESTAMP,
    user_id BIGINT,
    session_id VARCHAR(50),

    -- 用户属性 (快照)
    user_country VARCHAR(50),
    user_segment VARCHAR(20),
    user_acquisition_channel VARCHAR(30),
    user_registration_date DATE,

    -- 事件属性
    event_type VARCHAR(30),
    page_url TEXT,
    referrer_url TEXT,

    -- 产品属性 (如果是产品相关事件)
    product_id BIGINT,
    product_category VARCHAR(50),
    product_brand VARCHAR(50),
    product_price DECIMAL(10,2),

    -- 订单属性 (如果是订单事件)
    order_id VARCHAR(50),
    order_amount DECIMAL(10,2),
    payment_method VARCHAR(20),

    -- 设备属性
    device_type VARCHAR(20),
    os VARCHAR(20),
    browser VARCHAR(20),

    -- 扩展属性 (JSONB)
    properties JSONB
);

-- 使用部分索引优化特定查询
CREATE INDEX idx_user_behavior_purchase
ON warehouse.user_behavior_wide(user_id, event_time)
WHERE event_type = 'purchase';

-- 宽表查询 (简单快速)
SELECT
    user_segment,
    product_category,
    COUNT(DISTINCT user_id) as buyers,
    SUM(order_amount) as revenue
FROM warehouse.user_behavior_wide
WHERE event_type = 'purchase'
  AND event_time >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY 1, 2;
```

---

## 4. 应用场景深度分析

## 4.1 电商数据分析

### 核心指标计算

```sql
-- GMV 分析
WITH daily_metrics AS (
    SELECT
        DATE_TRUNC('day', order_date) as day,
        COUNT(DISTINCT order_id) as order_count,
        COUNT(DISTINCT user_id) as buyer_count,
        SUM(order_amount) as gmv,
        SUM(order_amount) / COUNT(DISTINCT order_id) as avg_order_value,
        SUM(order_amount) / COUNT(DISTINCT user_id) as arpu
    FROM warehouse.fact_orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY 1
)
SELECT
    day,
    gmv,
    LAG(gmv) OVER (ORDER BY day) as prev_day_gmv,
    (gmv - LAG(gmv) OVER (ORDER BY day)) / LAG(gmv) OVER (ORDER BY day) * 100 as gmv_growth_pct,
    AVG(gmv) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as gmv_7d_avg
FROM daily_metrics
ORDER BY day DESC;

-- 留存分析 (Cohort Analysis)
WITH user_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', MIN(order_date)) as cohort_month
    FROM warehouse.fact_orders
    GROUP BY 1
),
user_activity AS (
    SELECT DISTINCT
        user_id,
        DATE_TRUNC('month', order_date) as activity_month
    FROM warehouse.fact_orders
),
cohort_retention AS (
    SELECT
        c.cohort_month,
        a.activity_month,
        COUNT(DISTINCT c.user_id) as active_users,
        COUNT(DISTINCT c.user_id) * 1.0 / FIRST_VALUE(COUNT(DISTINCT c.user_id)) OVER (
            PARTITION BY c.cohort_month ORDER BY a.activity_month
        ) as retention_rate
    FROM user_cohorts c
    JOIN user_activity a ON c.user_id = a.user_id
    GROUP BY 1, 2
)
SELECT
    cohort_month,
    activity_month,
    (EXTRACT(YEAR FROM activity_month) - EXTRACT(YEAR FROM cohort_month)) * 12 +
    (EXTRACT(MONTH FROM activity_month) - EXTRACT(MONTH FROM cohort_month)) as period_months,
    active_users,
    ROUND(retention_rate * 100, 2) as retention_pct
FROM cohort_retention
ORDER BY 1, 3;

-- RFM 分析
WITH rfm AS (
    SELECT
        user_id,
        CURRENT_DATE - MAX(order_date) as recency_days,
        COUNT(DISTINCT order_id) as frequency,
        SUM(order_amount) as monetary
    FROM warehouse.fact_orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '1 year'
    GROUP BY 1
),
rfm_scores AS (
    SELECT
        user_id,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC) as r_score,
        NTILE(5) OVER (ORDER BY frequency) as f_score,
        NTILE(5) OVER (ORDER BY monetary) as m_score
    FROM rfm
)
SELECT
    user_id,
    recency_days,
    frequency,
    ROUND(monetary, 2) as monetary,
    r_score,
    f_score,
    m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
        ELSE 'Others'
    END as rfm_segment
FROM rfm_scores;
```

## 4.2 用户行为分析

```sql
-- 漏斗分析
CREATE OR REPLACE FUNCTION warehouse.funnel_analysis(
    start_date DATE,
    end_date DATE,
    steps TEXT[]
)
RETURNS TABLE (
    step_number INTEGER,
    step_name TEXT,
    user_count BIGINT,
    conversion_rate NUMERIC
) AS $$
DECLARE
    total_users BIGINT;
BEGIN
    -- 获取第一步用户数
    SELECT COUNT(DISTINCT user_id) INTO total_users
    FROM warehouse.user_events
    WHERE event_date BETWEEN start_date AND end_date
      AND event_type = steps[1];

    RETURN QUERY
    WITH funnel AS (
        SELECT
            generate_series(1, array_length(steps, 1)) as step_num,
            unnest(steps) as step
    )
    SELECT
        f.step_num,
        f.step,
        COUNT(DISTINCT e.user_id) as cnt,
        ROUND(COUNT(DISTINCT e.user_id) * 100.0 / total_users, 2) as rate
    FROM funnel f
    LEFT JOIN warehouse.user_events e
        ON e.event_type = f.step
        AND e.event_date BETWEEN start_date AND end_date
    GROUP BY f.step_num, f.step
    ORDER BY f.step_num;
END;
$$ LANGUAGE plpgsql;

-- 路径分析 (Session 内事件序列)
WITH session_events AS (
    SELECT
        user_id,
        session_id,
        event_time,
        event_type,
        page_url,
        LAG(event_type) OVER (
            PARTITION BY session_id ORDER BY event_time
        ) as prev_event,
        LEAD(event_type) OVER (
            PARTITION BY session_id ORDER BY event_time
        ) as next_event
    FROM warehouse.user_events
    WHERE event_date = CURRENT_DATE - 1
)
SELECT
    prev_event,
    event_type,
    next_event,
    COUNT(*) as transition_count
FROM session_events
WHERE prev_event IS NOT NULL
GROUP BY 1, 2, 3
HAVING COUNT(*) > 100
ORDER BY transition_count DESC
LIMIT 20;

-- 热力图数据 (页面点击分布)
SELECT
    page_url,
    click_x_bucket,
    click_y_bucket,
    COUNT(*) as click_count
FROM (
    SELECT
        page_url,
        WIDTH_BUCKET(click_x, 0, 1920, 20) as click_x_bucket,
        WIDTH_BUCKET(click_y, 0, 1080, 15) as click_y_bucket
    FROM warehouse.click_events
    WHERE event_date >= CURRENT_DATE - INTERVAL '7 days'
) t
GROUP BY 1, 2, 3
ORDER BY click_count DESC;
```

## 4.3 实时分析 (结合 TimescaleDB)

```sql
-- 安装 TimescaleDB 扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建时序表
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT,
    metric_name TEXT,
    value DOUBLE PRECISION,
    tags JSONB
);

-- 转换为超表
SELECT create_hypertable('metrics', 'time', chunk_time_interval => INTERVAL '1 day');

-- 实时聚合 (连续聚合)
CREATE MATERIALIZED VIEW metrics_1min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) as bucket,
    device_id,
    metric_name,
    AVG(value) as avg_value,
    MAX(value) as max_value,
    MIN(value) as min_value,
    COUNT(*) as sample_count
FROM metrics
GROUP BY 1, 2, 3
WITH NO DATA;

-- 添加刷新策略
SELECT add_continuous_aggregate_policy('metrics_1min',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute'
);

-- 实时查询
SELECT
    time_bucket('5 minutes', time) as bucket,
    metric_name,
    AVG(value) as avg_value,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY value) as p95
FROM metrics
WHERE time >= NOW() - INTERVAL '1 hour'
GROUP BY 1, 2
ORDER BY 1 DESC;
```

## 4.4 地理空间分析 (PostGIS)

```sql
-- 安装 PostGIS
CREATE EXTENSION postgis;

-- 创建地理表
CREATE TABLE store_locations (
    store_id SERIAL PRIMARY KEY,
    store_name VARCHAR(100),
    location GEOGRAPHY(POINT, 4326),
    address TEXT,
    city VARCHAR(50),
    revenue DECIMAL(12,2)
);

-- 创建空间索引
CREATE INDEX idx_store_locations_geo ON store_locations USING GIST(location);

-- 查询附近门店
SELECT
    store_id,
    store_name,
    ST_Distance(location, ST_MakePoint(-74.006, 40.7128)::GEOGRAPHY) / 1000 as distance_km,
    revenue
FROM store_locations
WHERE ST_DWithin(location, ST_MakePoint(-74.006, 40.7128)::GEOGRAPHY, 10000)
ORDER BY distance_km;

-- 地理围栏分析
SELECT
    u.user_id,
    u.event_time,
    s.store_name,
    ST_Distance(u.location, s.location) as distance_meters
FROM user_locations u
JOIN store_locations s ON ST_DWithin(u.location, s.location, 100)
WHERE u.event_time >= CURRENT_DATE - INTERVAL '7 days';
```

---

## 5. 生态工具集成

## 5.1 dbt (数据构建工具)

### dbt 项目结构

```text
analytics/
├── models/
│   ├── staging/          # 原始数据清洗
│   │   ├── stg_orders.sql
│   │   └── stg_customers.sql
│   ├── warehouse/        # 维度模型
│   │   ├── dim_customers.sql
│   │   ├── dim_products.sql
│   │   └── fct_orders.sql
│   ├── marts/           # 数据集市
│   │   ├── marketing/
│   │   ├── product/
│   │   └── finance/
│   └── exposures/       # 数据产品
├── seeds/               # 静态数据
├── snapshots/           # SCD 管理
├── tests/               # 数据测试
└── macros/              # 自定义宏
```

### dbt 模型示例

```sql
-- models/staging/stg_orders.sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),
renamed AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        status,
        amount,
        created_at
    FROM source
)
SELECT * FROM renamed

-- models/warehouse/dim_customers.sql
{{ config(materialized='table') }}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),
orders_summary AS (
    SELECT
        customer_id,
        COUNT(*) as total_orders,
        SUM(amount) as lifetime_value,
        MAX(order_date) as last_order_date
    FROM {{ ref('stg_orders') }}
    GROUP BY 1
)
SELECT
    c.customer_id,
    c.customer_name,
    c.email,
    c.country,
    COALESCE(o.total_orders, 0) as total_orders,
    COALESCE(o.lifetime_value, 0) as lifetime_value,
    o.last_order_date,
    CASE
        WHEN o.last_order_date >= CURRENT_DATE - INTERVAL '30 days' THEN 'Active'
        WHEN o.last_order_date >= CURRENT_DATE - INTERVAL '90 days' THEN 'At Risk'
        ELSE 'Churned'
    END as customer_status
FROM customers c
LEFT JOIN orders_summary o ON c.customer_id = o.customer_id

-- models/warehouse/fct_orders.sql
{{ config(materialized='incremental', unique_key='order_id') }}

SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    _loaded_at
FROM {{ ref('stg_orders') }}
{% if is_incremental() %}
WHERE _loaded_at > (SELECT MAX(_loaded_at) FROM {{ this }})
{% endif %}

-- tests/schema.yml
version: 2

models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
```

## 5.2 数据可视化集成

### Apache Superset

```sql
-- 为 Superset 创建专用视图
CREATE VIEW superset.order_analytics AS
SELECT
    o.order_date,
    c.country,
    c.customer_segment,
    p.category_name,
    COUNT(*) as order_count,
    SUM(o.sales_amount) as revenue,
    SUM(o.profit_amount) as profit
FROM warehouse.fact_orders o
JOIN warehouse.dim_customers c ON o.customer_sk = c.customer_sk
JOIN warehouse.dim_products p ON o.product_sk = p.product_sk
GROUP BY 1, 2, 3, 4;

-- 创建物化视图加速
CREATE MATERIALIZED VIEW superset.mv_daily_metrics AS
SELECT
    date_trunc('day', order_date) as day,
    COUNT(DISTINCT order_id) as orders,
    COUNT(DISTINCT user_id) as customers,
    SUM(sales_amount) as revenue
FROM warehouse.fact_orders
GROUP BY 1;

CREATE INDEX idx_mv_daily_metrics ON superset.mv_daily_metrics(day);

-- 自动刷新
SELECT cron.schedule('refresh-daily-metrics', '0 1 * * *',
    'REFRESH MATERIALIZED VIEW superset.mv_daily_metrics');
```

### Metabase

```sql
-- Metabase 问题示例
-- 问题: 本月销售额前10的产品
SELECT
    p.product_name,
    SUM(f.sales_amount) as revenue,
    SUM(f.quantity) as units_sold
FROM warehouse.fact_orders f
JOIN warehouse.dim_products p ON f.product_sk = p.product_sk
JOIN warehouse.dim_date d ON f.date_key = d.date_key
WHERE d.year = EXTRACT(YEAR FROM CURRENT_DATE)
  AND d.month = EXTRACT(MONTH FROM CURRENT_DATE)
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10;
```

## 5.3 数据质量测试 (Great Expectations)

```sql
-- 数据质量检查视图
CREATE VIEW quality.checks AS

-- 1. 完整性检查
SELECT
    'fact_orders' as table_name,
    'order_id not null' as check_name,
    COUNT(*) as total_rows,
    COUNT(order_id) as non_null_rows,
    COUNT(*) - COUNT(order_id) as null_rows
FROM warehouse.fact_orders

UNION ALL

-- 2. 唯一性检查
SELECT
    'dim_customers' as table_name,
    'customer_id unique' as check_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT customer_id) as unique_rows,
    COUNT(*) - COUNT(DISTINCT customer_id) as duplicate_rows
FROM warehouse.dim_customers

UNION ALL

-- 3. 范围检查
SELECT
    'fact_orders' as table_name,
    'amount positive' as check_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN sales_amount > 0 THEN 1 END) as valid_rows,
    COUNT(CASE WHEN sales_amount <= 0 THEN 1 END) as invalid_rows
FROM warehouse.fact_orders

UNION ALL

-- 4. 参照完整性
SELECT
    'fact_orders' as table_name,
    'customer_sk exists in dim' as check_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN c.customer_sk IS NOT NULL THEN 1 END) as valid_rows,
    COUNT(CASE WHEN c.customer_sk IS NULL THEN 1 END) as orphan_rows
FROM warehouse.fact_orders f
LEFT JOIN warehouse.dim_customers c ON f.customer_sk = c.customer_sk;
```

---

# 6. 性能优化与扩展

## 6.1 索引策略

```sql
-- B-Tree 索引 (等值查询、范围查询)
CREATE INDEX idx_orders_date ON warehouse.fact_orders(date_key);
CREATE INDEX idx_orders_customer ON warehouse.fact_orders(customer_sk);

-- 复合索引
CREATE INDEX idx_orders_date_customer ON warehouse.fact_orders(date_key, customer_sk);

-- 部分索引 (只索引热点数据)
CREATE INDEX idx_orders_recent ON warehouse.fact_orders(order_date)
WHERE order_date >= CURRENT_DATE - INTERVAL '90 days';

-- 表达式索引
CREATE INDEX idx_orders_year_month ON warehouse.fact_orders(
    (EXTRACT(YEAR FROM order_date)),
    (EXTRACT(MONTH FROM order_date))
);

-- BRIN 索引 (大块数据，如时序)
CREATE INDEX idx_orders_brin ON warehouse.fact_orders USING BRIN(order_date);

-- GIN 索引 (JSONB、数组)
CREATE INDEX idx_events_properties ON events USING GIN(properties);
```

## 6.2 分区策略

```sql
-- 范围分区 (时间)
CREATE TABLE events (
    event_id UUID,
    event_time TIMESTAMP,
    user_id BIGINT,
    event_type TEXT,
    payload JSONB
) PARTITION BY RANGE (event_time);

-- 创建分区
CREATE TABLE events_2024_q1 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE events_2024_q2 PARTITION OF events
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- 自动分区管理
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_date := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    partition_name := 'events_' || TO_CHAR(partition_date, 'YYYY_MM');
    start_date := partition_date;
    end_date := partition_date + INTERVAL '1 month';

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF events FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;

-- 列表分区 (类别)
CREATE TABLE sales_by_region (
    sale_id SERIAL,
    region TEXT,
    amount DECIMAL(10,2)
) PARTITION BY LIST (region);

CREATE TABLE sales_north PARTITION OF sales_by_region FOR VALUES IN ('North', 'Northeast');
CREATE TABLE sales_south PARTITION OF sales_by_region FOR VALUES IN ('South', 'Southeast');
```

## 6.3 查询优化

```sql
-- 分析查询计划
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT
    d.year,
    c.country,
    SUM(f.sales_amount)
FROM warehouse.fact_orders f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_customer c ON f.customer_sk = c.customer_sk
WHERE d.year = 2024
GROUP BY 1, 2;

-- 并行查询
SET max_parallel_workers_per_gather = 4;

-- 内存配置
SET work_mem = '256MB';  -- 复杂排序、哈希操作
SET effective_cache_size = '8GB';  -- 查询规划器使用

-- 物化视图 (预聚合)
CREATE MATERIALIZED VIEW warehouse.mv_monthly_sales AS
SELECT
    date_trunc('month', order_date) as month,
    customer_sk,
    COUNT(*) as order_count,
    SUM(sales_amount) as total_sales
FROM warehouse.fact_orders
GROUP BY 1, 2;

CREATE UNIQUE INDEX idx_mv_monthly ON warehouse.mv_monthly_sales(month, customer_sk);

-- 增量刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY warehouse.mv_monthly_sales;
```

## 6.4 读写分离

```sql
-- 主库 (写入)
-- postgresql.conf
max_wal_senders = 10
max_replication_slots = 10
wal_level = replica
hot_standby = on

-- 创建复制槽
SELECT * FROM pg_create_physical_replication_slot('replica_1');

-- 只读副本配置
-- recovery.conf (PostgreSQL 12+)
primary_conninfo = 'host=primary port=5432 user=replicator'
primary_slot_name = 'replica_1'
hot_standby = on

-- 应用层路由
-- 写入: 连接主库
-- 读取: 连接副本
```

---

## 7. 现代数据栈中的 PostgreSQL

## 7.1 完整技术栈推荐

```text
数据采集层:
├── Debezium (CDC) → PostgreSQL
├── Airbyte/Meltano (ELT) → PostgreSQL
└── FDW (外部数据) → PostgreSQL

数据建模层:
└── dbt → PostgreSQL

数据存储层:
├── PostgreSQL (核心仓库)
├── TimescaleDB (时序数据)
├── PostGIS (地理数据)
└── Citus (分布式扩展)

数据消费层:
├── Superset/Metabase (BI)
├── Jupyter (数据科学)
├── PostgREST (自动API)
└── Graphile (GraphQL)

数据治理:
├── DataHub (数据目录)
├── Great Expectations (质量)
└── pgAudit (审计)
```

## 7.2 云原生 PostgreSQL

| 云服务 | 特点 | 适用场景 |
|-------|------|---------|
| **Amazon RDS/Aurora** | 托管、自动备份、只读副本 | 通用场景 |
| **Google Cloud SQL** | 与GCP生态集成 | GCP用户 |
| **Azure Database** | 与Azure生态集成 | Azure用户 |
| **Supabase** | 开源Firebase替代 | 快速开发 |
| **Neon** | Serverless、分支 | 开发测试 |
| **Timescale Cloud** | 时序优化 | IoT/监控 |

## 7.3 PostgreSQL vs 专用数据仓库

| 场景 | PostgreSQL | Snowflake/BigQuery | 建议 |
|-----|-----------|-------------------|------|
| < 1TB 数据 | ✅ 完美 | 过度设计 | PostgreSQL |
| 1-10TB | ✅ 可以 | ✅ 更好 | 取决于查询复杂度 |
| > 10TB | ⚠️ 需要优化 | ✅ 更适合 | 考虑混合架构 |
| 复杂ETL | ✅ dbt | ✅ 内置 | PostgreSQL + dbt |
| 即席查询 | ✅ 优秀 | ✅ 优秀 | 两者皆可 |
| 成本敏感 | ✅ 最低 | 较高 | PostgreSQL |

---

## 附录

## A. 实用查询模板

### A.1 数据探查

```sql
-- 表统计信息
SELECT
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_analyze
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

-- 列统计
SELECT
    attname as column_name,
    n_distinct,
    most_common_vals,
    most_common_freqs,
    correlation
FROM pg_stats
WHERE tablename = 'fact_orders';

-- 慢查询
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### A.2 维护脚本

```sql
-- 自动VACUUM配置
ALTER TABLE warehouse.fact_orders SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05
);

-- 手动维护
VACUUM ANALYZE warehouse.fact_orders;
REINDEX TABLE warehouse.fact_orders;

-- 监控锁
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

## B. 参考资源

1. **官方文档**: <https://www.postgresql.org/docs/>
2. **dbt 文档**: <https://docs.getdbt.com/>
3. **TimescaleDB**: <https://docs.timescale.com/>
4. **PostGIS**: <https://postgis.net/documentation/>
5. **Citus**: <https://docs.citusdata.com/>

---

**结论**: PostgreSQL 凭借其功能完整性、标准兼容性、扩展生态和成本效益，已成为现代数据分析栈的核心引擎。从初创公司到大型企业，PostgreSQL 都能提供满足需求的数据分析解决方案。
