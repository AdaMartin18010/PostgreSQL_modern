# PostgreSQL列存实现

> **创建日期**: 2025年1月
> **来源**: PostgreSQL Citus + 列存扩展
> **状态**: 待完善
> **文档编号**: 05-04

---

## 📑 目录

- [PostgreSQL列存实现](#postgresql列存实现)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. Citus列存](#2-citus列存)
    - [2.1 Citus列存特性](#21-citus列存特性)
    - [2.2 启用列存](#22-启用列存)
    - [2.3 列存表管理](#23-列存表管理)
  - [3. 列存表设计](#3-列存表设计)
    - [3.1 列存表设计原则](#31-列存表设计原则)
    - [3.2 列存表创建](#32-列存表创建)
    - [3.3 列存表索引](#33-列存表索引)
  - [4. 查询优化](#4-查询优化)
    - [4.1 列存查询特点](#41-列存查询特点)
    - [4.2 查询优化示例](#42-查询优化示例)
    - [4.3 列存表统计](#43-列存表统计)
  - [5. HTAP架构](#5-htap架构)
    - [5.1 HTAP概念](#51-htap概念)
    - [5.2 HTAP实现](#52-htap实现)
    - [5.3 HTAP查询路由](#53-htap查询路由)
  - [6. 相关资源](#6-相关资源)

---

## 1. 概述

PostgreSQL通过Citus扩展支持列式存储，适用于OLAP场景的大规模数据分析。
列式存储将数据按列组织，相比行式存储，在分析查询场景下具有显著的性能优势。

**核心优势**:

- **压缩率高**：相同类型数据压缩效果好
- **查询高效**：只读取需要的列
- **聚合快速**：列式数据便于聚合计算
- **适合分析**：OLAP查询性能优异

---

## 2. Citus列存

### 2.1 Citus列存特性

**Citus列存特点**:

- 基于PostgreSQL的列式存储扩展
- 支持分布式列存表
- 自动压缩和优化
- 兼容PostgreSQL SQL语法

### 2.2 启用列存

**安装和启用**:

```sql
-- 安装Citus扩展
CREATE EXTENSION IF NOT EXISTS citus;

-- 查看Citus版本
SELECT * FROM citus_version();

-- 创建列存表
CREATE TABLE sales_fact_columnar (
    sale_id BIGSERIAL,
    date_id INT NOT NULL,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    quantity INT NOT NULL,
    amount NUMERIC(10,2) NOT NULL
) USING columnar;

-- 或者使用ALTER TABLE转换
CREATE TABLE sales_fact_row AS SELECT * FROM sales_fact LIMIT 0;
ALTER TABLE sales_fact_row SET (columnar = true);
```

### 2.3 列存表管理

**列存表操作**:

```sql
-- 查看列存表信息
SELECT * FROM columnar.storage
WHERE relation_name = 'sales_fact_columnar';

-- 查看列存表统计
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE '%columnar%';

-- 列存表压缩
SELECT columnar.alter_columnar_table_set(
    'sales_fact_columnar',
    compression => 'pglz',
    compression_level => 1
);
```

---

## 3. 列存表设计

### 3.1 列存表设计原则

**设计建议**:

1. **宽表设计**：适合列存，减少JOIN
2. **列选择**：只包含分析需要的列
3. **数据类型**：选择压缩友好的类型
4. **分区策略**：结合时间分区使用

### 3.2 列存表创建

**完整列存表设计**:

```sql
-- 事实表：列存设计
CREATE TABLE fact_sales_columnar (
    sale_id BIGSERIAL,
    -- 时间维度
    sale_date DATE NOT NULL,
    sale_year INT NOT NULL,
    sale_month INT NOT NULL,
    sale_quarter INT NOT NULL,
    -- 维度键
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    store_id INT NOT NULL,
    -- 度量值
    quantity INT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    cost NUMERIC(10,2) NOT NULL,
    profit NUMERIC(10,2) GENERATED ALWAYS AS (amount - cost) STORED,
    -- 元数据
    created_at TIMESTAMPTZ DEFAULT NOW()
) USING columnar
PARTITION BY RANGE (sale_date);

-- 创建分区
CREATE TABLE fact_sales_columnar_2024
    PARTITION OF fact_sales_columnar
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
    USING columnar;

CREATE TABLE fact_sales_columnar_2025
    PARTITION OF fact_sales_columnar
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01')
    USING columnar;
```

### 3.3 列存表索引

**列存索引策略**:

```sql
-- 列存表不支持传统B-Tree索引
-- 但可以使用表达式索引和部分索引

-- 创建表达式索引（用于过滤）
CREATE INDEX idx_sales_date_year ON fact_sales_columnar(sale_year)
    WHERE sale_year = 2025;

-- 注意：列存表主要依赖列式扫描，索引使用有限
-- 设计时应考虑查询模式，合理选择分区键
```

---

## 4. 查询优化

### 4.1 列存查询特点

**列存查询优势**:

- 只读取需要的列
- 列式压缩减少I/O
- 向量化计算支持
- 适合聚合查询

### 4.2 查询优化示例

**优化查询模式**:

```sql
-- 列存表查询：只选择需要的列
SELECT
    sale_year,
    sale_month,
    SUM(amount) AS total_amount,
    SUM(quantity) AS total_quantity,
    COUNT(*) AS sale_count
FROM fact_sales_columnar
WHERE sale_year = 2025
  AND sale_month BETWEEN 1 AND 3
GROUP BY sale_year, sale_month
ORDER BY sale_year, sale_month;

-- 避免SELECT *，只查询需要的列
-- 列存表在SELECT *时性能不如行存表

-- 利用分区裁剪
EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, SUM(amount) AS total
FROM fact_sales_columnar
WHERE sale_date BETWEEN '2025-01-01' AND '2025-01-31'
GROUP BY product_id;
```

### 4.3 列存表统计

**更新统计信息**:

```sql
-- 列存表需要手动更新统计信息
ANALYZE fact_sales_columnar;

-- 查看列存表统计
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename = 'fact_sales_columnar';

-- 列存表压缩统计
SELECT
    relation_name,
    stripe_count,
    row_count,
    pg_size_pretty(total_size) AS total_size,
    pg_size_pretty(compressed_size) AS compressed_size,
    compression_ratio
FROM columnar.storage
WHERE relation_name = 'fact_sales_columnar';
```

---

## 5. HTAP架构

### 5.1 HTAP概念

**HTAP（Hybrid Transactional/Analytical Processing）**：混合事务/分析处理架构，同时支持OLTP和OLAP工作负载。

**架构特点**:

- OLTP：行存表处理事务
- OLAP：列存表支持分析
- 数据同步：ETL或CDC同步数据

### 5.2 HTAP实现

**HTAP架构设计**:

```sql
-- OLTP表：行存（事务处理）
CREATE TABLE orders_oltp (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date TIMESTAMPTZ DEFAULT NOW(),
    order_amount NUMERIC(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    -- 索引优化事务查询
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_date (order_date)
);

-- OLAP表：列存（分析处理）
CREATE TABLE orders_olap (
    order_id BIGINT,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    order_year INT NOT NULL,
    order_month INT NOT NULL,
    order_amount NUMERIC(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL
) USING columnar
PARTITION BY RANGE (order_date);

-- 数据同步：ETL过程
CREATE OR REPLACE FUNCTION sync_oltp_to_olap()
RETURNS VOID AS $$
BEGIN
    -- 增量同步（示例）
    INSERT INTO orders_olap (
        order_id, customer_id, order_date,
        order_year, order_month, order_amount, status
    )
    SELECT
        order_id,
        customer_id,
        order_date::DATE,
        EXTRACT(YEAR FROM order_date)::INT,
        EXTRACT(MONTH FROM order_date)::INT,
        order_amount,
        status
    FROM orders_oltp
    WHERE order_date > (
        SELECT MAX(order_date) FROM orders_olap
    );
END;
$$ LANGUAGE plpgsql;

-- 定时同步（使用pg_cron扩展）
-- SELECT cron.schedule('sync-orders', '0 * * * *', 'SELECT sync_oltp_to_olap();');
```

### 5.3 HTAP查询路由

**查询路由策略**:

```sql
-- OLTP查询：使用行存表
CREATE OR REPLACE FUNCTION get_order_details(p_order_id BIGINT)
RETURNS TABLE (
    order_id BIGINT,
    customer_id INT,
    order_date TIMESTAMPTZ,
    order_amount NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT o.order_id, o.customer_id, o.order_date, o.order_amount
    FROM orders_oltp o
    WHERE o.order_id = p_order_id;
END;
$$ LANGUAGE plpgsql;

-- OLAP查询：使用列存表
CREATE OR REPLACE FUNCTION get_sales_analytics(
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    order_year INT,
    order_month INT,
    total_amount NUMERIC,
    order_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        order_year,
        order_month,
        SUM(order_amount) AS total_amount,
        COUNT(*) AS order_count
    FROM orders_olap
    WHERE order_date BETWEEN p_start_date AND p_end_date
    GROUP BY order_year, order_month
    ORDER BY order_year, order_month;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. 相关资源

- [维度建模基础](./维度建模基础.md) - 维度建模指南
- [事实表技术](./事实表技术.md) - 事实表设计
- [Citus官方文档](https://docs.citusdata.com/) - Citus列存文档
- [PostgreSQL列存扩展](https://github.com/citusdata/citus) - Citus GitHub

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
