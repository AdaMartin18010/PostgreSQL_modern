# 数据湖与PostgreSQL集成指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级

---

## 📋 目录

- [数据湖与PostgreSQL集成指南](#数据湖与postgresql集成指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. 集成方式](#2-集成方式)
    - [2.1 FDW集成](#21-fdw集成)
    - [2.2 直接存储](#22-直接存储)
  - [3. 数据同步](#3-数据同步)
    - [3.1 批量同步](#31-批量同步)
    - [3.2 增量同步](#32-增量同步)
  - [4. 查询优化](#4-查询优化)
    - [4.1 物化视图](#41-物化视图)
    - [4.2 索引优化](#42-索引优化)
  - [5. 最佳实践](#5-最佳实践)
    - [✅ 推荐做法](#-推荐做法)
  - [6. FDW详细配置](#6-fdw详细配置)
    - [6.1 file\_fdw配置](#61-file_fdw配置)
    - [6.2 postgres\_fdw配置](#62-postgres_fdw配置)
    - [6.3 性能优化](#63-性能优化)
  - [7. 数据同步策略](#7-数据同步策略)
    - [7.1 批量同步](#71-批量同步)
    - [7.2 增量同步](#72-增量同步)
    - [7.3 同步监控](#73-同步监控)
  - [8. 数据一致性保证](#8-数据一致性保证)
    - [8.1 数据校验](#81-数据校验)
    - [8.2 数据修复](#82-数据修复)
  - [9. 性能优化](#9-性能优化)
    - [9.1 查询优化](#91-查询优化)
    - [9.2 并行查询优化](#92-并行查询优化)
  - [10. 监控和告警](#10-监控和告警)
    - [10.1 同步监控](#101-同步监控)
    - [10.2 告警配置](#102-告警配置)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

数据湖与PostgreSQL集成提供统一的数据访问接口。

**集成优势**:

- 统一查询接口
- 灵活数据访问
- 高性能查询
- 数据一致性

---

## 2. 集成方式

### 2.1 FDW集成

```sql
-- 使用file_fdw访问数据湖
CREATE FOREIGN TABLE lake_data (
    id INT,
    data JSONB
)
SERVER file_server
OPTIONS (filename '/data-lake/data.json', format 'json');
```

### 2.2 直接存储

```sql
-- 在PostgreSQL中存储数据湖数据
CREATE TABLE lake_storage (
    id SERIAL PRIMARY KEY,
    raw_data JSONB,
    metadata JSONB
);
```

---

## 3. 数据同步

### 3.1 批量同步

```sql
-- 从数据湖导入
INSERT INTO pg_table
SELECT * FROM lake_foreign_table
WHERE created_at > CURRENT_DATE - INTERVAL '1 day';
```

### 3.2 增量同步

```sql
-- 增量同步
INSERT INTO pg_table
SELECT * FROM lake_foreign_table l
WHERE NOT EXISTS (
    SELECT 1 FROM pg_table p
    WHERE p.id = l.id
);
```

---

## 4. 查询优化

### 4.1 物化视图

```sql
-- 创建物化视图
CREATE MATERIALIZED VIEW mv_lake_data AS
SELECT * FROM lake_foreign_table;

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_lake_data;
```

### 4.2 索引优化

```sql
-- 创建JSONB索引
CREATE INDEX idx_lake_data ON lake_storage USING GIN (raw_data);
```

---

## 5. 最佳实践

### ✅ 推荐做法

1. **使用物化视图** - 缓存常用数据
2. **批量同步** - 减少同步频率
3. **索引优化** - 提高查询性能
4. **元数据管理** - 维护数据目录

---

## 6. FDW详细配置

### 6.1 file_fdw配置

```sql
-- 安装file_fdw扩展
CREATE EXTENSION IF NOT EXISTS file_fdw;

-- 创建文件服务器
CREATE SERVER file_server
FOREIGN DATA WRAPPER file_fdw;

-- 创建外部表（CSV格式）
CREATE FOREIGN TABLE lake_csv_data (
    id INT,
    name TEXT,
    value NUMERIC,
    created_at TIMESTAMPTZ
)
SERVER file_server
OPTIONS (
    filename '/data-lake/data.csv',
    format 'csv',
    header 'true'
);

-- 创建外部表（JSON格式）
CREATE FOREIGN TABLE lake_json_data (
    id INT,
    data JSONB
)
SERVER file_server
OPTIONS (
    filename '/data-lake/data.json',
    format 'json'
);
```

### 6.2 postgres_fdw配置

```sql
-- 安装postgres_fdw扩展
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- 创建外部服务器
CREATE SERVER remote_lake_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    host 'remote-host',
    port '5432',
    dbname 'lake_db'
);

-- 创建用户映射
CREATE USER MAPPING FOR current_user
SERVER remote_lake_server
OPTIONS (
    user 'lake_user',
    password 'lake_password'
);

-- 创建外部表
CREATE FOREIGN TABLE remote_lake_data (
    id INT,
    data JSONB,
    created_at TIMESTAMPTZ
)
SERVER remote_lake_server
OPTIONS (
    schema_name 'public',
    table_name 'lake_data'
);
```

### 6.3 性能优化

```sql
-- 外部表性能优化（带错误处理和性能测试）
DO $$
DECLARE
    fdw_table_count INT;
BEGIN
    -- 检查外部表数量
    SELECT COUNT(*) INTO fdw_table_count
    FROM information_schema.foreign_tables;

    RAISE NOTICE '当前外部表数量: %', fdw_table_count;

    -- 如果外部表过多，考虑使用物化视图缓存
    IF fdw_table_count > 10 THEN
        RAISE NOTICE '建议：外部表数量较多，考虑使用物化视图缓存数据';
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查外部表失败: %', SQLERRM;
END $$;

-- 为外部表创建本地物化视图
CREATE MATERIALIZED VIEW mv_lake_data_cached AS
SELECT * FROM lake_foreign_table
WHERE created_at > CURRENT_DATE - INTERVAL '7 days';

-- 创建索引
CREATE INDEX idx_mv_lake_data_created ON mv_lake_data_cached (created_at);
CREATE INDEX idx_mv_lake_data_jsonb ON mv_lake_data_cached USING GIN (data);
```

---

## 7. 数据同步策略

### 7.1 批量同步

```sql
-- 批量同步函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION sync_lake_data_batch(
    p_start_date DATE DEFAULT CURRENT_DATE - INTERVAL '7 days',
    p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    synced_count BIGINT,
    sync_duration INTERVAL
) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    synced_rows BIGINT;
BEGIN
    start_time := clock_timestamp();

    -- 批量同步数据
    INSERT INTO pg_table (id, data, created_at)
    SELECT id, data, created_at
    FROM lake_foreign_table
    WHERE created_at::DATE BETWEEN p_start_date AND p_end_date
      AND NOT EXISTS (
          SELECT 1 FROM pg_table p
          WHERE p.id = lake_foreign_table.id
      );

    GET DIAGNOSTICS synced_rows = ROW_COUNT;
    end_time := clock_timestamp();

    RETURN QUERY SELECT
        synced_rows,
        end_time - start_time;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '批量同步失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行批量同步
SELECT * FROM sync_lake_data_batch();
```

### 7.2 增量同步

```sql
-- 增量同步函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION sync_lake_data_incremental()
RETURNS TABLE (
    inserted_count BIGINT,
    updated_count BIGINT,
    sync_duration INTERVAL
) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    inserted_rows BIGINT;
    updated_rows BIGINT;
    last_sync_time TIMESTAMPTZ;
BEGIN
    start_time := clock_timestamp();

    -- 获取上次同步时间
    SELECT MAX(created_at) INTO last_sync_time
    FROM pg_table;

    IF last_sync_time IS NULL THEN
        last_sync_time := '1970-01-01'::TIMESTAMPTZ;
    END IF;

    -- 增量插入
    INSERT INTO pg_table (id, data, created_at)
    SELECT id, data, created_at
    FROM lake_foreign_table
    WHERE created_at > last_sync_time
      AND NOT EXISTS (
          SELECT 1 FROM pg_table p
          WHERE p.id = lake_foreign_table.id
      );

    GET DIAGNOSTICS inserted_rows = ROW_COUNT;

    -- 增量更新
    UPDATE pg_table p
    SET data = l.data,
        created_at = l.created_at
    FROM lake_foreign_table l
    WHERE p.id = l.id
      AND l.created_at > last_sync_time
      AND p.data IS DISTINCT FROM l.data;

    GET DIAGNOSTICS updated_rows = ROW_COUNT;
    end_time := clock_timestamp();

    RETURN QUERY SELECT
        inserted_rows,
        updated_rows,
        end_time - start_time;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '增量同步失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行增量同步
SELECT * FROM sync_lake_data_incremental();
```

### 7.3 同步监控

```sql
-- 创建同步日志表
CREATE TABLE IF NOT EXISTS sync_log (
    id SERIAL PRIMARY KEY,
    sync_type TEXT,  -- 'BATCH', 'INCREMENTAL'
    synced_count BIGINT,
    sync_duration INTERVAL,
    sync_status TEXT,  -- 'SUCCESS', 'FAILED'
    error_message TEXT,
    sync_time TIMESTAMPTZ DEFAULT NOW()
);

-- 同步监控函数
CREATE OR REPLACE FUNCTION monitor_sync_status()
RETURNS TABLE (
    sync_type TEXT,
    last_sync_time TIMESTAMPTZ,
    avg_duration INTERVAL,
    success_rate NUMERIC,
    total_syncs BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sl.sync_type,
        MAX(sl.sync_time) AS last_sync_time,
        AVG(sl.sync_duration) AS avg_duration,
        ROUND(100.0 * SUM(CASE WHEN sl.sync_status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate,
        COUNT(*) AS total_syncs
    FROM sync_log sl
    WHERE sl.sync_time > NOW() - INTERVAL '30 days'
    GROUP BY sl.sync_type
    ORDER BY sl.sync_type;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '监控同步状态失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 查询同步监控
SELECT * FROM monitor_sync_status();
```

---

## 8. 数据一致性保证

### 8.1 数据校验

```sql
-- 数据一致性校验函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION validate_data_consistency()
RETURNS TABLE (
    table_name TEXT,
    source_count BIGINT,
    target_count BIGINT,
    consistency_status TEXT
) AS $$
DECLARE
    table_rec RECORD;
    source_row_count BIGINT;
    target_row_count BIGINT;
BEGIN
    FOR table_rec IN
        SELECT
            ft.foreign_table_name AS source_table,
            pt.table_name AS target_table
        FROM information_schema.foreign_tables ft
        JOIN pg_tables pt ON pt.tablename = ft.foreign_table_name || '_local'
    LOOP
        BEGIN
            -- 获取源表行数
            EXECUTE format('SELECT COUNT(*) FROM %I', table_rec.source_table)
            INTO source_row_count;

            -- 获取目标表行数
            EXECUTE format('SELECT COUNT(*) FROM %I', table_rec.target_table)
            INTO target_row_count;

            RETURN QUERY SELECT
                table_rec.target_table,
                source_row_count,
                target_row_count,
                CASE
                    WHEN source_row_count = target_row_count THEN '一致'
                    ELSE '不一致'
                END;

        EXCEPTION
            WHEN OTHERS THEN
                RETURN QUERY SELECT
                    table_rec.target_table,
                    NULL::BIGINT,
                    NULL::BIGINT,
                    format('校验失败: %', SQLERRM)::TEXT;
        END;
    END LOOP;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '数据一致性校验失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行数据一致性校验
SELECT * FROM validate_data_consistency();
```

### 8.2 数据修复

```sql
-- 数据修复函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION repair_data_inconsistency(
    p_table_name TEXT
)
RETURNS TABLE (
    repaired_count BIGINT,
    repair_duration INTERVAL
) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    repaired_rows BIGINT;
    source_table TEXT;
BEGIN
    start_time := clock_timestamp();

    -- 确定源表名
    source_table := p_table_name || '_source';

    -- 修复缺失数据
    EXECUTE format(
        'INSERT INTO %I SELECT * FROM %I WHERE id NOT IN (SELECT id FROM %I)',
        p_table_name,
        source_table,
        p_table_name
    );

    GET DIAGNOSTICS repaired_rows = ROW_COUNT;
    end_time := clock_timestamp();

    RETURN QUERY SELECT
        repaired_rows,
        end_time - start_time;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '数据修复失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行数据修复
SELECT * FROM repair_data_inconsistency('pg_table');
```

---

## 9. 性能优化

### 9.1 查询优化

```sql
-- 查询优化：使用物化视图缓存
CREATE MATERIALIZED VIEW mv_lake_query_cache AS
SELECT
    DATE_TRUNC('day', created_at) AS date,
    data->>'category' AS category,
    COUNT(*) AS record_count,
    SUM((data->>'amount')::numeric) AS total_amount
FROM lake_foreign_table
GROUP BY DATE_TRUNC('day', created_at), data->>'category';

-- 创建索引
CREATE INDEX idx_mv_lake_query_cache_date ON mv_lake_query_cache (date);
CREATE INDEX idx_mv_lake_query_cache_category ON mv_lake_query_cache (category);

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_lake_query_cache;
```

### 9.2 并行查询优化

```sql
-- 启用并行查询
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET parallel_workers = 4;

-- 并行查询外部表
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    data->>'category' AS category,
    COUNT(*) AS count,
    SUM((data->>'amount')::numeric) AS total
FROM lake_foreign_table
GROUP BY data->>'category';
```

---

## 10. 监控和告警

### 10.1 同步监控

```sql
-- 同步监控视图
CREATE OR REPLACE VIEW v_sync_monitoring AS
SELECT
    sync_type,
    sync_status,
    COUNT(*) AS sync_count,
    AVG(sync_duration) AS avg_duration,
    MAX(sync_time) AS last_sync_time
FROM sync_log
WHERE sync_time > NOW() - INTERVAL '7 days'
GROUP BY sync_type, sync_status
ORDER BY sync_type, sync_status;

-- 查询同步监控
SELECT * FROM v_sync_monitoring;
```

### 10.2 告警配置

```sql
-- 同步告警函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION check_sync_alerts()
RETURNS TABLE (
    alert_type TEXT,
    alert_message TEXT,
    alert_level TEXT
) AS $$
DECLARE
    failed_sync_count BIGINT;
    stale_sync_count BIGINT;
    last_sync_time TIMESTAMPTZ;
BEGIN
    -- 检查失败的同步
    SELECT COUNT(*) INTO failed_sync_count
    FROM sync_log
    WHERE sync_status = 'FAILED'
      AND sync_time > NOW() - INTERVAL '24 hours';

    IF failed_sync_count > 5 THEN
        RETURN QUERY SELECT
            'SYNC_FAILURE'::TEXT,
            format('过去24小时有 % 次同步失败', failed_sync_count)::TEXT,
            'CRITICAL'::TEXT;
    END IF;

    -- 检查过时的同步
    SELECT MAX(sync_time) INTO last_sync_time
    FROM sync_log
    WHERE sync_status = 'SUCCESS';

    IF last_sync_time IS NULL OR NOW() - last_sync_time > INTERVAL '24 hours' THEN
        RETURN QUERY SELECT
            'STALE_SYNC'::TEXT,
            format('上次成功同步时间: %', last_sync_time)::TEXT,
            'WARNING'::TEXT;
    END IF;

    RETURN;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '同步告警检查失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 查询告警
SELECT * FROM check_sync_alerts();
```

---

## 📚 相关文档

- [数据湖完整指南.md](./数据湖完整指南.md) - 数据湖完整指南
- [数据湖架构设计.md](./数据湖架构设计.md) - 数据湖架构设计
- [26-数据管理/README.md](../README.md) - 数据管理主题

---

**最后更新**: 2025年1月
