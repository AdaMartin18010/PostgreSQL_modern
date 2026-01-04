# PostgreSQL列存实现

> **创建日期**: 2025年1月
> **来源**: PostgreSQL Citus + 列存扩展
> **状态**: ✅ 已完成
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
  - [6. 更多实际案例 / More Practical Examples](#6-更多实际案例--more-practical-examples)
    - [6.1 案例1: 销售分析系统](#61-案例1-销售分析系统)
    - [6.2 案例2: 用户行为分析系统](#62-案例2-用户行为分析系统)
    - [6.3 案例3: 财务分析系统](#63-案例3-财务分析系统)
  - [7. 性能优化与监控 / Performance Optimization and Monitoring](#7-性能优化与监控--performance-optimization-and-monitoring)
    - [7.1 列存性能优化](#71-列存性能优化)
    - [7.2 查询性能监控](#72-查询性能监控)
    - [7.3 存储空间监控](#73-存储空间监控)
  - [8. 常见问题解答 / FAQ](#8-常见问题解答--faq)
    - [Q1: 什么时候应该使用列存表？](#q1-什么时候应该使用列存表)
    - [Q2: 列存表和行存表如何选择？](#q2-列存表和行存表如何选择)
    - [Q3: HTAP架构如何实现？](#q3-htap架构如何实现)
    - [Q4: 列存表如何优化写入性能？](#q4-列存表如何优化写入性能)
    - [Q5: 列存表查询性能如何优化？](#q5-列存表查询性能如何优化)
  - [8. 相关资源 / Related Resources](#8-相关资源--related-resources)
    - [8.1 核心相关文档 / Core Related Documents](#81-核心相关文档--core-related-documents)
    - [8.2 理论基础 / Theoretical Foundation](#82-理论基础--theoretical-foundation)
    - [8.3 实践指南 / Practical Guides](#83-实践指南--practical-guides)
    - [8.4 应用案例 / Application Cases](#84-应用案例--application-cases)
    - [8.5 参考资源 / Reference Resources](#85-参考资源--reference-resources)

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

## 6. 更多实际案例 / More Practical Examples

### 6.1 案例1: 销售分析系统

**销售分析列存实现**:

```sql
-- 销售事实表（列存）
CREATE TABLE fact_sales_columnar (
    sale_date DATE NOT NULL,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    salesperson_id INT,
    quantity INT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    discount_amount NUMERIC(10,2) DEFAULT 0,
    shipping_cost NUMERIC(10,2) DEFAULT 0
) USING columnar;

-- 创建索引（列存表支持索引）
CREATE INDEX idx_sales_date ON fact_sales_columnar(sale_date);
CREATE INDEX idx_sales_product ON fact_sales_columnar(product_id);
CREATE INDEX idx_sales_customer ON fact_sales_columnar(customer_id);

-- 查询：销售分析
SELECT
    DATE_TRUNC('month', sale_date) AS month,
    product_id,
    SUM(quantity) AS total_quantity,
    SUM(total_amount) AS total_revenue,
    AVG(unit_price) AS avg_price
FROM fact_sales_columnar
WHERE sale_date >= '2024-01-01'
GROUP BY month, product_id
ORDER BY total_revenue DESC;
```

### 6.2 案例2: 用户行为分析系统

**用户行为分析列存实现**:

```sql
-- 用户行为事实表（列存）
CREATE TABLE fact_user_behavior_columnar (
    event_date TIMESTAMPTZ NOT NULL,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    page_url TEXT,
    session_id VARCHAR(100),
    duration_seconds INT,
    metadata JSONB
) USING columnar;

-- 分区（列存表支持分区）
CREATE TABLE fact_user_behavior_columnar_2024_01 PARTITION OF fact_user_behavior_columnar
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01') USING columnar;

-- 查询：用户行为分析
SELECT
    DATE_TRUNC('day', event_date) AS day,
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users,
    AVG(duration_seconds) AS avg_duration
FROM fact_user_behavior_columnar
WHERE event_date >= NOW() - INTERVAL '30 days'
GROUP BY day, event_type
ORDER BY day DESC, event_count DESC;
```

### 6.3 案例3: 财务分析系统

**财务分析列存实现**:

```sql
-- 财务交易事实表（列存）
CREATE TABLE fact_financial_transactions_columnar (
    transaction_date DATE NOT NULL,
    account_id INT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    category_id INT,
    description TEXT
) USING columnar;

-- 查询：财务分析
SELECT
    DATE_TRUNC('quarter', transaction_date) AS quarter,
    transaction_type,
    SUM(amount) AS total_amount,
    COUNT(*) AS transaction_count,
    AVG(amount) AS avg_amount
FROM fact_financial_transactions_columnar
WHERE transaction_date >= '2024-01-01'
GROUP BY quarter, transaction_type
ORDER BY quarter DESC, total_amount DESC;
```

---

## 7. 性能优化与监控 / Performance Optimization and Monitoring

### 7.1 列存性能优化

**压缩优化**:

```sql
-- 查看列存表压缩率
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename LIKE '%columnar%';

-- 手动压缩列存表
SELECT columnar.alter_columnar_table_set(
    'fact_sales_columnar',
    compression_level => 6  -- 0-9，数字越大压缩率越高
);
```

**查询优化**:

```sql
-- ✅ 优化：只查询需要的列
SELECT sale_date, product_id, total_amount
FROM fact_sales_columnar
WHERE sale_date >= '2024-01-01';
-- 列存只读取需要的列，性能更好

-- ❌ 未优化：查询所有列
SELECT * FROM fact_sales_columnar
WHERE sale_date >= '2024-01-01';
-- 读取所有列，性能较差
```

### 7.2 查询性能监控

**监控查询性能**:

```sql
-- 使用pg_stat_statements监控列存查询
SELECT
    LEFT(query, 100) AS query_preview,
    calls,
    mean_exec_time,
    max_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE query LIKE '%columnar%'
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 对比行存和列存查询性能
-- 行存查询
EXPLAIN ANALYZE
SELECT SUM(total_amount) FROM fact_sales_rowstore WHERE sale_date >= '2024-01-01';
-- Seq Scan: 5000ms

-- 列存查询
EXPLAIN ANALYZE
SELECT SUM(total_amount) FROM fact_sales_columnar WHERE sale_date >= '2024-01-01';
-- Columnar Scan: 500ms（快10倍）
```

### 7.3 存储空间监控

**存储空间对比**:

```sql
-- 对比行存和列存存储空间
SELECT
    'rowstore' AS storage_type,
    pg_size_pretty(pg_total_relation_size('fact_sales_rowstore')) AS size
UNION ALL
SELECT
    'columnar' AS storage_type,
    pg_size_pretty(pg_total_relation_size('fact_sales_columnar')) AS size;

-- 计算压缩率
SELECT
    pg_total_relation_size('fact_sales_rowstore')::NUMERIC /
    NULLIF(pg_total_relation_size('fact_sales_columnar'), 0) AS compression_ratio;
```

---

## 8. 常见问题解答 / FAQ

### Q1: 什么时候应该使用列存表？

**A**: 列存表适用场景：

- ✅ **OLAP查询**: 分析型查询，聚合计算
- ✅ **大表**: 表很大（GB级以上）
- ✅ **列式查询**: 查询只涉及部分列
- ✅ **低写入频率**: 写入频率低，主要是批量导入

**不适用场景**:

- ❌ **OLTP查询**: 事务型查询，单行查询
- ❌ **高写入频率**: 频繁的单行写入
- ❌ **全列查询**: 经常查询所有列

### Q2: 列存表和行存表如何选择？

**A**: 选择原则：

| 特性 | 行存表 | 列存表 |
|------|--------|--------|
| OLTP查询 | ✅ 优秀 | ❌ 较差 |
| OLAP查询 | ⚠️ 一般 | ✅ 优秀 |
| 写入性能 | ✅ 优秀 | ⚠️ 一般 |
| 压缩率 | ⚠️ 一般 | ✅ 优秀 |
| 单行查询 | ✅ 优秀 | ❌ 较差 |
| 聚合查询 | ⚠️ 一般 | ✅ 优秀 |

**建议**:

- OLTP场景 → 使用行存表
- OLAP场景 → 使用列存表
- HTAP场景 → 行存+列存混合

### Q3: HTAP架构如何实现？

**A**: HTAP实现策略：

```sql
-- 方案1：双表架构（行存+列存）
CREATE TABLE orders_rowstore (...);  -- OLTP查询
CREATE TABLE orders_columnar (...) USING columnar;  -- OLAP查询

-- 数据同步
INSERT INTO orders_columnar SELECT * FROM orders_rowstore WHERE order_date >= CURRENT_DATE - INTERVAL '1 day';

-- 方案2：使用物化视图
CREATE MATERIALIZED VIEW orders_olap AS
SELECT * FROM orders_rowstore;

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY orders_olap;
```

### Q4: 列存表如何优化写入性能？

**A**: 写入优化策略：

1. **批量写入**: 使用批量INSERT或COPY
2. **异步同步**: 使用ETL工具异步同步
3. **减少压缩**: 降低压缩级别（写入时）
4. **分区**: 使用分区表减少写入影响

```sql
-- ✅ 优化：批量写入
INSERT INTO fact_sales_columnar
SELECT * FROM staging_table;

-- ✅ 优化：使用COPY
COPY fact_sales_columnar FROM '/path/to/data.csv' WITH CSV HEADER;
```

### Q5: 列存表查询性能如何优化？

**A**: 查询优化策略：

1. **只查询需要的列**: 避免SELECT *
2. **使用索引**: 为WHERE条件创建索引
3. **分区剪枝**: 使用分区减少扫描范围
4. **聚合预计算**: 使用物化视图预计算聚合

```sql
-- ✅ 优化：只查询需要的列
SELECT sale_date, total_amount FROM fact_sales_columnar;

-- ✅ 优化：使用索引
CREATE INDEX idx_sales_date ON fact_sales_columnar(sale_date);
SELECT * FROM fact_sales_columnar WHERE sale_date >= '2024-01-01';
```

---

## 8. 相关资源 / Related Resources

### 8.1 核心相关文档 / Core Related Documents

- [维度建模基础](./维度建模基础.md) - OLAP维度建模基础
- [事实表技术](./事实表技术.md) - 事实表列存实现
- [维度表技术](./维度表技术.md) - 维度表设计
- [分区策略](../08-PostgreSQL建模实践/分区策略.md) - 列存表分区策略
- [索引策略](../08-PostgreSQL建模实践/索引策略.md) - 列存表索引设计
- [性能优化](../08-PostgreSQL建模实践/性能优化.md) - 列存查询性能优化

### 8.2 理论基础 / Theoretical Foundation

- [Kimball维度建模](../02-权威资源与标准/Kimball维度建模.md) - Kimball维度建模理论
- [范式理论](../01-数据建模理论基础/范式理论.md) - 数据库范式理论

### 8.3 实践指南 / Practical Guides

- [性能优化与监控](#7-性能优化与监控--performance-optimization-and-monitoring) - 本文档的性能监控章节
- [更多实际案例](#6-更多实际案例--more-practical-examples) - 本文档的应用案例章节

### 8.4 应用案例 / Application Cases

- [电商数据模型案例](../10-综合应用案例/电商数据模型案例.md) - 电商列存实现案例
- [金融数据模型案例](../10-综合应用案例/金融数据模型案例.md) - 金融列存实现案例

### 8.5 参考资源 / Reference Resources

- [权威资源索引](../00-导航与索引/权威资源索引.md) - 权威资源列表
- [术语对照表](../00-导航与索引/术语对照表.md) - 术语对照
- [快速查找指南](../00-导航与索引/快速查找指南.md) - 快速查找工具
- Citus官方文档: [Columnar Storage](https://docs.citusdata.com/en/stable/develop/reference_citus_sql.html#columnar-storage)
- PostgreSQL官方文档: [Table Storage](https://www.postgresql.org/docs/current/storage.html)

- [维度建模基础](./维度建模基础.md) - 维度建模指南
- [事实表技术](./事实表技术.md) - 事实表设计
- [Citus官方文档](https://docs.citusdata.com/) - Citus列存文档
- [PostgreSQL列存扩展](https://github.com/citusdata/citus) - Citus GitHub
- [性能优化](../08-PostgreSQL建模实践/性能优化.md) - 性能优化指南

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
