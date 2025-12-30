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
  - [7. ETL错误处理和重试](#7-etl错误处理和重试)
    - [7.1 错误日志表](#71-错误日志表)
    - [7.2 重试机制](#72-重试机制)
  - [8. ETL性能优化](#8-etl性能优化)
    - [8.1 批量处理优化](#81-批量处理优化)
    - [8.2 并行ETL处理](#82-并行etl处理)
  - [9. ETL监控和调度](#9-etl监控和调度)
    - [9.1 ETL执行日志](#91-etl执行日志)
    - [9.2 ETL调度](#92-etl调度)
  - [10. 数据质量保证](#10-数据质量保证)
    - [10.1 数据质量检查](#101-数据质量检查)
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

## 7. ETL错误处理和重试

### 7.1 错误日志表

```sql
-- 创建ETL错误日志表
CREATE TABLE IF NOT EXISTS etl_error_log (
    id SERIAL PRIMARY KEY,
    etl_job_name TEXT,
    error_type TEXT,
    error_message TEXT,
    error_data JSONB,
    failed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 错误处理函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION log_etl_error(
    p_job_name TEXT,
    p_error_type TEXT,
    p_error_message TEXT,
    p_error_data JSONB DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO etl_error_log (etl_job_name, error_type, error_message, error_data)
    VALUES (p_job_name, p_error_type, p_error_message, p_error_data);

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '记录ETL错误失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

### 7.2 重试机制

```sql
-- ETL重试函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION etl_with_retry(
    p_etl_function TEXT,
    p_max_retries INT DEFAULT 3
)
RETURNS TABLE (
    attempt_number INT,
    status TEXT,
    error_message TEXT
) AS $$
DECLARE
    attempt INT := 1;
    success BOOLEAN := FALSE;
    error_msg TEXT;
BEGIN
    WHILE attempt <= p_max_retries AND NOT success LOOP
        BEGIN
            EXECUTE format('SELECT %I()', p_etl_function);
            success := TRUE;
            RETURN QUERY SELECT attempt, 'SUCCESS'::TEXT, NULL::TEXT;
        EXCEPTION
            WHEN OTHERS THEN
                error_msg := SQLERRM;
                RETURN QUERY SELECT attempt, 'FAILED'::TEXT, error_msg;
                attempt := attempt + 1;

                IF attempt <= p_max_retries THEN
                    PERFORM pg_sleep(2 ^ attempt);  -- 指数退避
                END IF;
        END;
    END LOOP;

    IF NOT success THEN
        RAISE EXCEPTION 'ETL执行失败，已重试 % 次', p_max_retries;
    END IF;

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- 执行ETL重试
SELECT * FROM etl_with_retry('etl_sales', 3);
```

---

## 8. ETL性能优化

### 8.1 批量处理优化

```sql
-- 批量ETL处理函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION etl_batch_process(
    p_batch_size INT DEFAULT 10000,
    p_table_name TEXT
)
RETURNS TABLE (
    processed_count BIGINT,
    duration INTERVAL
) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    processed_rows BIGINT;
    offset_val INT := 0;
BEGIN
    start_time := clock_timestamp();

    LOOP
        -- 批量处理
        EXECUTE format(
            'INSERT INTO %I SELECT * FROM staging_area LIMIT %s OFFSET %s',
            p_table_name,
            p_batch_size,
            offset_val
        );

        GET DIAGNOSTICS processed_rows = ROW_COUNT;

        IF processed_rows = 0 THEN
            EXIT;
        END IF;

        offset_val := offset_val + p_batch_size;
    END LOOP;

    end_time := clock_timestamp();

    RETURN QUERY SELECT
        offset_val,
        end_time - start_time;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '批量ETL处理失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行批量ETL处理
SELECT * FROM etl_batch_process(10000, 'fact_sales');
```

### 8.2 并行ETL处理

```sql
-- 并行ETL处理（使用PostgreSQL并行查询）
SET max_parallel_workers_per_gather = 4;

-- 并行转换
EXPLAIN (ANALYZE, BUFFERS, TIMING)
INSERT INTO transformed_sales
SELECT
    (raw_data->>'date')::date AS time_id,
    (raw_data->>'product_id')::int AS product_id,
    (raw_data->>'customer_id')::int AS customer_id,
    (raw_data->>'amount')::numeric AS sales_amount
FROM staging_sales
WHERE transformed_at IS NULL;
```

---

## 9. ETL监控和调度

### 9.1 ETL执行日志

```sql
-- 创建ETL执行日志表
CREATE TABLE IF NOT EXISTS etl_execution_log (
    id SERIAL PRIMARY KEY,
    etl_job_name TEXT NOT NULL,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    duration INTERVAL,
    status TEXT,  -- 'RUNNING', 'SUCCESS', 'FAILED'
    records_processed BIGINT,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ETL执行监控函数
CREATE OR REPLACE FUNCTION monitor_etl_execution()
RETURNS TABLE (
    job_name TEXT,
    last_execution TIMESTAMPTZ,
    avg_duration INTERVAL,
    success_rate NUMERIC,
    avg_records_processed BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        eel.etl_job_name,
        MAX(eel.start_time) AS last_execution,
        AVG(eel.duration) AS avg_duration,
        ROUND(100.0 * SUM(CASE WHEN eel.status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate,
        AVG(eel.records_processed)::BIGINT AS avg_records_processed
    FROM etl_execution_log eel
    WHERE eel.start_time > NOW() - INTERVAL '30 days'
    GROUP BY eel.etl_job_name
    ORDER BY eel.etl_job_name;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '监控ETL执行失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 查询ETL执行监控
SELECT * FROM monitor_etl_execution();
```

### 9.2 ETL调度

```sql
-- 使用pg_cron调度ETL任务
-- 安装pg_cron扩展
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 调度每日ETL任务
SELECT cron.schedule(
    'daily-etl-sales',
    '0 2 * * *',  -- 每天凌晨2点执行
    'SELECT etl_sales();'
);

-- 调度每小时增量ETL
SELECT cron.schedule(
    'hourly-etl-incremental',
    '0 * * * *',  -- 每小时执行
    'SELECT etl_incremental_sales();'
);

-- 查看调度任务
SELECT * FROM cron.job;
```

---

## 10. 数据质量保证

### 10.1 数据质量检查

```sql
-- ETL数据质量检查函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION check_etl_data_quality(
    p_table_name TEXT
)
RETURNS TABLE (
    check_type TEXT,
    check_result TEXT,
    error_count BIGINT
) AS $$
DECLARE
    null_count BIGINT;
    duplicate_count BIGINT;
    range_error_count BIGINT;
BEGIN
    -- 检查NULL值
    EXECUTE format(
        'SELECT COUNT(*) FROM %I WHERE customer_id IS NULL',
        p_table_name
    ) INTO null_count;

    IF null_count > 0 THEN
        RETURN QUERY SELECT 'NULL_CHECK'::TEXT, 'FAIL'::TEXT, null_count;
    ELSE
        RETURN QUERY SELECT 'NULL_CHECK'::TEXT, 'PASS'::TEXT, 0::BIGINT;
    END IF;

    -- 检查重复值
    EXECUTE format(
        'SELECT COUNT(*) - COUNT(DISTINCT business_key) FROM %I',
        p_table_name
    ) INTO duplicate_count;

    IF duplicate_count > 0 THEN
        RETURN QUERY SELECT 'DUPLICATE_CHECK'::TEXT, 'FAIL'::TEXT, duplicate_count;
    ELSE
        RETURN QUERY SELECT 'DUPLICATE_CHECK'::TEXT, 'PASS'::TEXT, 0::BIGINT;
    END IF;

    -- 检查范围值
    EXECUTE format(
        'SELECT COUNT(*) FROM %I WHERE sales_amount < 0 OR sales_amount > 1000000',
        p_table_name
    ) INTO range_error_count;

    IF range_error_count > 0 THEN
        RETURN QUERY SELECT 'RANGE_CHECK'::TEXT, 'FAIL'::TEXT, range_error_count;
    ELSE
        RETURN QUERY SELECT 'RANGE_CHECK'::TEXT, 'PASS'::TEXT, 0::BIGINT;
    END IF;

    RETURN;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '数据质量检查失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行数据质量检查
SELECT * FROM check_etl_data_quality('fact_sales');
```

---

## 📚 相关文档

- [数据仓库设计指南.md](./数据仓库设计指南.md) - 数据仓库设计
- [数据库数据集成模型-ETL流程与数据转换的形式化.md](./数据库数据集成模型-ETL流程与数据转换的形式化.md) - ETL理论
- [26-数据管理/README.md](../README.md) - 数据管理主题

---

**最后更新**: 2025年1月
