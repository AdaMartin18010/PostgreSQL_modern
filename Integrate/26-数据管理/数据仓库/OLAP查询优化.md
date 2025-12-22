# OLAP查询优化

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级

---

## 📋 目录

- [OLAP查询优化](#olap查询优化)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. OLAP操作优化](#2-olap操作优化)
    - [2.1 ROLLUP优化](#21-rollup优化)
    - [2.2 CUBE优化](#22-cube优化)
    - [2.3 GROUPING SETS优化](#23-grouping-sets优化)
  - [3. 聚合优化](#3-聚合优化)
    - [3.1 使用物化视图](#31-使用物化视图)
    - [3.2 并行聚合](#32-并行聚合)
  - [4. 物化视图优化](#4-物化视图优化)
    - [4.1 物化视图设计](#41-物化视图设计)
    - [4.2 增量刷新](#42-增量刷新)
  - [5. 分区优化](#5-分区优化)
    - [5.1 事实表分区](#51-事实表分区)
    - [5.2 分区裁剪](#52-分区裁剪)
  - [6. 最佳实践](#6-最佳实践)
    - [✅ 推荐做法](#-推荐做法)
    - [❌ 避免做法](#-避免做法)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

OLAP查询优化是数据仓库性能的关键。PostgreSQL提供了强大的OLAP功能：

- **GROUP BY扩展** - ROLLUP、CUBE、GROUPING SETS
- **窗口函数** - 支持复杂分析查询
- **物化视图** - 预计算聚合结果
- **并行查询** - 加速聚合计算

---

## 2. OLAP操作优化

### 2.1 ROLLUP优化

```sql
-- ROLLUP：层次聚合
SELECT
    t.year,
    t.quarter,
    t.month,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_time t ON f.time_id = t.time_id
WHERE t.year = 2024
GROUP BY ROLLUP(t.year, t.quarter, t.month)
ORDER BY t.year, t.quarter, t.month;

-- 优化：使用索引
CREATE INDEX idx_fact_sales_time ON fact_sales (time_id);
CREATE INDEX idx_dim_time_year_quarter_month ON dim_time (year, quarter, month);
```

### 2.2 CUBE优化

```sql
-- CUBE：所有维度组合
SELECT
    p.category_name,
    c.region_name,
    t.quarter,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_time t ON f.time_id = t.time_id
WHERE t.year = 2024
GROUP BY CUBE(p.category_name, c.region_name, t.quarter);

-- 优化：限制CUBE维度数量（避免组合爆炸）
```

### 2.3 GROUPING SETS优化

```sql
-- GROUPING SETS：指定聚合组合
SELECT
    p.category_name,
    c.region_name,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY GROUPING SETS (
    (p.category_name),
    (c.region_name),
    (p.category_name, c.region_name),
    ()
);
```

---

## 3. 聚合优化

### 3.1 使用物化视图

```sql
-- 创建物化视图预计算聚合
CREATE MATERIALIZED VIEW mv_sales_summary AS
SELECT
    t.year,
    t.quarter,
    p.category_name,
    SUM(f.sales_amount) AS total_sales,
    SUM(f.quantity) AS total_quantity,
    COUNT(*) AS transaction_count
FROM fact_sales f
JOIN dim_time t ON f.time_id = t.time_id
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY t.year, t.quarter, p.category_name;

-- 创建索引
CREATE INDEX mv_sales_summary_idx ON mv_sales_summary (year, quarter, category_name);

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sales_summary;
```

### 3.2 并行聚合

```sql
-- 启用并行查询
SET max_parallel_workers_per_gather = 4;

-- 并行聚合查询
EXPLAIN (ANALYZE)
SELECT
    t.year,
    p.category_name,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_time t ON f.time_id = t.time_id
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY t.year, p.category_name;
```

---

## 4. 物化视图优化

### 4.1 物化视图设计

```sql
-- 选择常用查询创建物化视图
CREATE MATERIALIZED VIEW mv_monthly_sales AS
SELECT
    t.year,
    t.month,
    p.category_name,
    c.region_name,
    SUM(f.sales_amount) AS total_sales,
    AVG(f.sales_amount) AS avg_sales,
    COUNT(*) AS transaction_count
FROM fact_sales f
JOIN dim_time t ON f.time_id = t.time_id
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY t.year, t.month, p.category_name, c.region_name;

-- 创建唯一索引（支持CONCURRENT刷新）
CREATE UNIQUE INDEX mv_monthly_sales_idx ON mv_monthly_sales
(year, month, category_name, region_name);
```

### 4.2 增量刷新

```sql
-- 增量刷新物化视图
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT
    t.date,
    p.category_name,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_time t ON f.time_id = t.time_id
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY t.date, p.category_name;

-- 增量刷新（只刷新最近7天）
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales
WHERE date >= CURRENT_DATE - INTERVAL '7 days';
```

---

## 5. 分区优化

### 5.1 事实表分区

```sql
-- 按时间分区事实表
CREATE TABLE fact_sales (
    time_id INT NOT NULL,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    sales_amount NUMERIC(12,2)
) PARTITION BY RANGE (time_id);

-- 按月分区
CREATE TABLE fact_sales_2024_01 PARTITION OF fact_sales
    FOR VALUES FROM (20240101) TO (20240201);
```

### 5.2 分区裁剪

```sql
-- 查询时自动分区裁剪
EXPLAIN (ANALYZE)
SELECT SUM(sales_amount)
FROM fact_sales f
JOIN dim_time t ON f.time_id = t.time_id
WHERE t.year = 2024 AND t.month = 1;
-- 只扫描fact_sales_2024_01分区
```

---

## 6. 最佳实践

### ✅ 推荐做法

1. **使用物化视图** - 预计算常用聚合
2. **合理分区** - 按时间分区事实表
3. **创建索引** - 为维度表和事实表创建索引
4. **使用并行查询** - 加速聚合计算
5. **定期刷新** - 保持物化视图最新

### ❌ 避免做法

1. **不使用物化视图** - 重复计算影响性能
2. **过度使用CUBE** - 组合爆炸影响性能
3. **忽略分区** - 大表不分区影响性能
4. **不刷新物化视图** - 数据过时

---

## 📚 相关文档

- [数据仓库设计指南.md](./数据仓库设计指南.md) - 数据仓库设计
- [数据库数据仓库模型-OLAP查询与多维分析的形式化.md](./数据库数据仓库模型-OLAP查询与多维分析的形式化.md) - OLAP理论
- [26-数据管理/README.md](../README.md) - 数据管理主题

---

**最后更新**: 2025年1月
