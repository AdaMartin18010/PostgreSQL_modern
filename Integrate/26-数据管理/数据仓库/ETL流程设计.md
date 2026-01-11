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
-- ETL提取阶段：准备源表和目标表

-- 1. 创建源表（模拟源系统）
CREATE TABLE IF NOT EXISTS source_system.table_name (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    amount NUMERIC(12,2),
    order_date DATE,
    status VARCHAR(50),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 创建暂存区（Staging Area）
CREATE TABLE IF NOT EXISTS staging_area (
    id INTEGER NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    amount NUMERIC(12,2),
    order_date DATE,
    status VARCHAR(50),
    updated_at TIMESTAMPTZ,
    etl_batch_id VARCHAR(100),
    etl_loaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 插入源数据示例
INSERT INTO source_system.table_name (customer_name, email, amount, order_date, status) VALUES
    ('Alice Johnson', 'alice@example.com', 299.99, '2024-01-15', 'completed'),
    ('Bob Smith', 'bob@example.com', 199.99, '2024-01-16', 'pending'),
    ('Charlie Brown', 'charlie@example.com', 399.99, '2024-01-17', 'completed')
ON CONFLICT DO NOTHING;

-- 4. 全量提取
INSERT INTO staging_area (id, customer_name, email, amount, order_date, status, updated_at, etl_batch_id)
SELECT
    id,
    customer_name,
    email,
    amount,
    order_date,
    status,
    updated_at,
    'BATCH_' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS')
FROM source_system.table_name;
```

### 2.2 增量提取

```sql
-- 1. 创建变更日志表
CREATE TABLE IF NOT EXISTS source_system.change_log (
    change_id SERIAL PRIMARY KEY,
    table_name VARCHAR(200) NOT NULL,
    record_id INTEGER NOT NULL,
    change_type VARCHAR(20) NOT NULL CHECK (change_type IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 增量提取（基于时间戳）
INSERT INTO staging_area (id, customer_name, email, amount, order_date, status, updated_at, etl_batch_id)
SELECT
    id,
    customer_name,
    email,
    amount,
    order_date,
    status,
    updated_at,
    'INCREMENTAL_' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS')
FROM source_system.table_name
WHERE updated_at > COALESCE(
    (SELECT MAX(updated_at) FROM staging_area WHERE etl_batch_id LIKE 'INCREMENTAL_%'),
    '1970-01-01'::TIMESTAMPTZ
);

-- 3. 增量提取（基于变更日志）
INSERT INTO staging_area (id, customer_name, email, amount, order_date, status, updated_at, etl_batch_id)
SELECT
    (new_data->>'id')::INTEGER,
    new_data->>'customer_name',
    new_data->>'email',
    (new_data->>'amount')::NUMERIC(12,2),
    (new_data->>'order_date')::DATE,
    new_data->>'status',
    changed_at,
    'CDC_' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS')
FROM source_system.change_log
WHERE table_name = 'table_name'
  AND change_type IN ('INSERT', 'UPDATE')
  AND changed_at > COALESCE(
      (SELECT MAX(updated_at) FROM staging_area WHERE etl_batch_id LIKE 'CDC_%'),
      '1970-01-01'::TIMESTAMPTZ
  );
```

### 2.3 提取策略

- **全量提取** - 适合小表或首次加载
- **增量提取** - 适合大表或频繁更新
- **CDC（变更数据捕获）** - 实时提取变更

---

## 3. 转换（Transform）

### 3.1 数据清洗

```sql
-- ETL转换阶段：数据清洗

-- 1. 添加业务键列（用于去重）
ALTER TABLE staging_area
ADD COLUMN IF NOT EXISTS business_key VARCHAR(200) GENERATED ALWAYS AS (customer_name || '|' || COALESCE(email, '')) STORED;

-- 2. 清洗NULL值
UPDATE staging_area
SET email = COALESCE(email, 'unknown@example.com')
WHERE email IS NULL;

UPDATE staging_area
SET status = COALESCE(status, 'unknown')
WHERE status IS NULL;

-- 3. 清洗重复数据（保留最新的记录）
DELETE FROM staging_area a
USING staging_area b
WHERE a.id < b.id
  AND a.business_key = b.business_key
  AND a.etl_batch_id = b.etl_batch_id;

-- 4. 数据标准化（统一格式）
UPDATE staging_area
SET customer_name = INITCAP(LOWER(TRIM(customer_name))),
    email = LOWER(TRIM(email));

-- 5. 数据验证和过滤无效数据
DELETE FROM staging_area
WHERE customer_name IS NULL
   OR LENGTH(customer_name) < 2
   OR amount < 0;
```

### 3.2 数据转换

```sql
-- ETL转换阶段：数据转换

-- 1. 数据类型转换（如果列类型不匹配）
-- 注意：如果staging_area的amount已经是NUMERIC类型，此步骤可以跳过
-- ALTER TABLE staging_area
-- ALTER COLUMN amount TYPE NUMERIC(12,2)
-- USING amount::NUMERIC(12,2);

-- 2. 数据格式转换和计算字段
ALTER TABLE staging_area
ADD COLUMN IF NOT EXISTS year_month VARCHAR(7) GENERATED ALWAYS AS (TO_CHAR(order_date, 'YYYY-MM')) STORED,
ADD COLUMN IF NOT EXISTS is_high_value BOOLEAN GENERATED ALWAYS AS (amount > 300) STORED;

-- 3. 日期格式标准化
UPDATE staging_area
SET order_date = COALESCE(order_date, CURRENT_DATE)
WHERE order_date IS NULL;

-- 4. 数据聚合和汇总（创建汇总表）
CREATE TABLE IF NOT EXISTS staging_summary (
    batch_id VARCHAR(100) PRIMARY KEY,
    record_count INTEGER NOT NULL,
    total_amount NUMERIC(15,2) NOT NULL,
    avg_amount NUMERIC(12,2) NOT NULL,
    min_date DATE,
    max_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO staging_summary (batch_id, record_count, total_amount, avg_amount, min_date, max_date)
SELECT
    etl_batch_id,
    COUNT(*) AS record_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    MIN(order_date) AS min_date,
    MAX(order_date) AS max_date
FROM staging_area
WHERE etl_loaded_at > NOW() - INTERVAL '1 hour'
GROUP BY etl_batch_id
ON CONFLICT (batch_id) DO UPDATE
SET record_count = EXCLUDED.record_count,
    total_amount = EXCLUDED.total_amount,
    avg_amount = EXCLUDED.avg_amount,
    min_date = EXCLUDED.min_date,
    max_date = EXCLUDED.max_date;
```

### 3.3 数据验证

```sql
-- ETL转换阶段：数据验证

-- 1. 验证数据质量（全面的质量检查）
SELECT
    etl_batch_id,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE customer_name IS NOT NULL) AS non_null_names,
    COUNT(*) FILTER (WHERE email IS NOT NULL) AS non_null_emails,
    COUNT(*) FILTER (WHERE amount IS NOT NULL) AS non_null_amounts,
    COUNT(*) FILTER (WHERE amount > 0) AS valid_amounts,
    COUNT(DISTINCT business_key) AS unique_keys,
    COUNT(*) - COUNT(DISTINCT business_key) AS duplicate_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    MIN(order_date) AS earliest_date,
    MAX(order_date) AS latest_date
FROM staging_area
GROUP BY etl_batch_id;

-- 2. 数据质量报告视图
CREATE OR REPLACE VIEW v_etl_quality_report AS
SELECT
    etl_batch_id,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE customer_name IS NULL OR email IS NULL) AS invalid_rows,
    ROUND(100.0 * COUNT(*) FILTER (WHERE customer_name IS NOT NULL AND email IS NOT NULL AND amount > 0) / NULLIF(COUNT(*), 0), 2) AS quality_score,
    COUNT(DISTINCT business_key) AS unique_records,
    COUNT(*) - COUNT(DISTINCT business_key) AS duplicates
FROM staging_area
GROUP BY etl_batch_id;

-- 3. 查询质量报告
SELECT * FROM v_etl_quality_report ORDER BY etl_batch_id DESC;
```

---

## 4. 加载（Load）

### 4.1 批量加载

```sql
-- ETL加载阶段：批量加载

-- 1. 确保目标表存在
CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    amount NUMERIC(12,2) NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(50),
    loaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 批量插入（从暂存区加载）
INSERT INTO fact_sales (customer_name, email, amount, order_date, status)
SELECT DISTINCT
    customer_name,
    email,
    amount,
    order_date,
    status
FROM staging_area
WHERE etl_batch_id = (SELECT MAX(etl_batch_id) FROM staging_area)
ON CONFLICT DO NOTHING;

-- 3. 使用COPY加载（从CSV文件，性能更好）
-- COPY fact_sales (customer_name, email, amount, order_date, status)
-- FROM '/path/to/file.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- 4. 验证加载结果
SELECT
    COUNT(*) AS loaded_rows,
    SUM(amount) AS total_amount,
    MIN(order_date) AS earliest_date,
    MAX(order_date) AS latest_date
FROM fact_sales
WHERE loaded_at > NOW() - INTERVAL '1 hour';
```

### 4.2 增量加载

```sql
-- ETL加载阶段：增量加载

-- 1. 增量插入（使用MERGE或UPSERT模式）
INSERT INTO fact_sales (customer_name, email, amount, order_date, status)
SELECT
    s.customer_name,
    s.email,
    s.amount,
    s.order_date,
    s.status
FROM staging_area s
WHERE s.etl_batch_id LIKE 'INCREMENTAL_%'
  AND NOT EXISTS (
      SELECT 1 FROM fact_sales f
      WHERE f.customer_name = s.customer_name
        AND f.email = s.email
        AND f.order_date = s.order_date
  )
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
