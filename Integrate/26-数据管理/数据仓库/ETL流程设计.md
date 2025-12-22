# ETL流程设计指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级

---

## 📋 目录

- [ETL流程设计指南](#etl流程设计指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. 提取（Extract）](#2-提取extract)
    - [2.1 全量提取](#21-全量提取)
    - [2.2 增量提取](#22-增量提取)
    - [2.3 提取策略](#23-提取策略)
  - [3. 转换（Transform）](#3-转换transform)
    - [3.1 数据清洗](#31-数据清洗)
    - [3.2 数据转换](#32-数据转换)
    - [3.3 数据验证](#33-数据验证)
  - [4. 加载（Load）](#4-加载load)
    - [4.1 批量加载](#41-批量加载)
    - [4.2 增量加载](#42-增量加载)
    - [4.3 加载策略](#43-加载策略)
  - [5. ETL架构设计](#5-etl架构设计)
    - [5.1 三层架构](#51-三层架构)
    - [5.2 ETL流程函数](#52-etl流程函数)
  - [6. 最佳实践](#6-最佳实践)
    - [✅ 推荐做法](#-推荐做法)
    - [❌ 避免做法](#-避免做法)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

ETL（Extract, Transform, Load）是数据仓库的核心流程：

- **提取（Extract）** - 从源系统提取数据
- **转换（Transform）** - 清洗、转换、验证数据
- **加载（Load）** - 加载到目标系统

---

## 2. 提取（Extract）

### 2.1 全量提取

```sql
-- 全量提取
INSERT INTO staging_area
SELECT * FROM source_system.table_name;
```

### 2.2 增量提取

```sql
-- 增量提取（基于时间戳）
INSERT INTO staging_area
SELECT * FROM source_system.table_name
WHERE updated_at > (SELECT MAX(updated_at) FROM staging_area);

-- 增量提取（基于变更日志）
INSERT INTO staging_area
SELECT * FROM source_system.change_log
WHERE change_type IN ('INSERT', 'UPDATE');
```

### 2.3 提取策略

- **全量提取** - 适合小表或首次加载
- **增量提取** - 适合大表或频繁更新
- **CDC（变更数据捕获）** - 实时提取变更

---

## 3. 转换（Transform）

### 3.1 数据清洗

```sql
-- 清洗NULL值
UPDATE staging_area
SET column_name = COALESCE(column_name, 'Unknown')
WHERE column_name IS NULL;

-- 清洗重复数据
DELETE FROM staging_area a
USING staging_area b
WHERE a.id < b.id
  AND a.business_key = b.business_key;
```

### 3.2 数据转换

```sql
-- 数据类型转换
ALTER TABLE staging_area
ALTER COLUMN amount TYPE NUMERIC(12,2)
USING amount::NUMERIC(12,2);

-- 数据格式转换
UPDATE staging_area
SET date_column = TO_DATE(date_string, 'YYYY-MM-DD');
```

### 3.3 数据验证

```sql
-- 验证数据质量
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE column_name IS NOT NULL) AS non_null_rows,
    COUNT(DISTINCT business_key) AS unique_keys
FROM staging_area;
```

---

## 4. 加载（Load）

### 4.1 批量加载

```sql
-- 批量插入
INSERT INTO fact_sales
SELECT * FROM staging_area;

-- 使用COPY（更快）
COPY fact_sales FROM '/path/to/file.csv' WITH CSV HEADER;
```

### 4.2 增量加载

```sql
-- 增量插入
INSERT INTO fact_sales
SELECT * FROM staging_area s
WHERE NOT EXISTS (
    SELECT 1 FROM fact_sales f
    WHERE f.business_key = s.business_key
);

-- 增量更新
UPDATE fact_sales f
SET column_name = s.column_name
FROM staging_area s
WHERE f.business_key = s.business_key;
```

### 4.3 加载策略

- **全量加载** - 删除后重新加载
- **增量加载** - 只加载新数据
- **更新加载** - 更新现有数据

---

## 5. ETL架构设计

### 5.1 三层架构

```sql
-- 1. 暂存区（Staging Area）
CREATE TABLE staging_sales (
    source_id TEXT,
    raw_data JSONB,
    extracted_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 转换区（Transform Area）
CREATE TABLE transformed_sales (
    time_id INT,
    product_id INT,
    customer_id INT,
    sales_amount NUMERIC(12,2),
    transformed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 数据仓库（Data Warehouse）
CREATE TABLE fact_sales (
    time_id INT,
    product_id INT,
    customer_id INT,
    sales_amount NUMERIC(12,2)
);
```

### 5.2 ETL流程函数

```sql
-- ETL流程函数
CREATE OR REPLACE FUNCTION etl_sales()
RETURNS VOID AS $$
BEGIN
    -- 1. 提取
    INSERT INTO staging_sales (source_id, raw_data)
    SELECT id, row_to_json(t)::jsonb
    FROM source_system.sales t;

    -- 2. 转换
    INSERT INTO transformed_sales (time_id, product_id, customer_id, sales_amount)
    SELECT
        (raw_data->>'date')::date,
        (raw_data->>'product_id')::int,
        (raw_data->>'customer_id')::int,
        (raw_data->>'amount')::numeric
    FROM staging_sales
    WHERE transformed_at IS NULL;

    -- 3. 加载
    INSERT INTO fact_sales
    SELECT time_id, product_id, customer_id, sales_amount
    FROM transformed_sales
    WHERE loaded_at IS NULL;

    -- 标记完成
    UPDATE staging_sales SET transformed_at = NOW() WHERE transformed_at IS NULL;
    UPDATE transformed_sales SET loaded_at = NOW() WHERE loaded_at IS NULL;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. 最佳实践

### ✅ 推荐做法

1. **使用暂存区** - 分离提取和加载
2. **增量处理** - 使用增量提取和加载
3. **数据验证** - 在转换阶段验证数据
4. **错误处理** - 记录和处理错误
5. **监控ETL** - 监控ETL执行状态

### ❌ 避免做法

1. **直接加载** - 不经过暂存区
2. **忽略错误** - 不处理数据质量问题
3. **全量处理** - 大表使用全量处理
4. **不监控** - 无法发现ETL问题

---

## 📚 相关文档

- [数据仓库设计指南.md](./数据仓库设计指南.md) - 数据仓库设计
- [数据库数据集成模型-ETL流程与数据转换的形式化.md](./数据库数据集成模型-ETL流程与数据转换的形式化.md) - ETL理论
- [26-数据管理/README.md](../README.md) - 数据管理主题

---

**最后更新**: 2025年1月
