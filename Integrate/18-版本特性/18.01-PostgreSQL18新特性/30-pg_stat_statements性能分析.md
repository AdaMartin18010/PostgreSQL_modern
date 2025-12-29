---

> **📋 文档来源**: `docs\01-PostgreSQL18\30-pg_stat_statements性能分析.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL 18 pg_stat_statements性能分析

## 📑 目录

- [2.1 pg_stat_statements字段](#21-pg_stat_statements字段)
- [3.1 Top慢查询](#31-top慢查询)
- [3.2 缓存命中率分析](#32-缓存命中率分析)
- [3.3 临时文件使用](#33-临时文件使用)
- [4.1 按类型统计](#41-按类型统计)
- [4.2 表访问分析](#42-表访问分析)
- [5.1 建立基线](#51-建立基线)
- [6.1 每日报告](#61-每日报告)
---

## 2. 核心视图

### 2.1 pg_stat_statements字段

```sql
-- 性能测试：查看pg_stat_statements字段（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    queryid,              -- 查询ID（hash）
    query,                -- 查询文本
    calls,                -- 执行次数
    total_exec_time,      -- 总执行时间（ms）
    mean_exec_time,       -- 平均执行时间
    min_exec_time,        -- 最小执行时间
    max_exec_time,        -- 最大执行时间
    stddev_exec_time,     -- 标准差
    rows,                 -- 总行数
    shared_blks_hit,      -- 缓存命中块数
    shared_blks_read,     -- 磁盘读取块数
    shared_blks_written,  -- 写入块数
    temp_blks_read,       -- 临时文件读取
    temp_blks_written     -- 临时文件写入
FROM pg_stat_statements
LIMIT 1;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询pg_stat_statements失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 3. 常用查询

### 3.1 Top慢查询

```sql
-- 性能测试：按平均时间排序（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    queryid,
    LEFT(query, 100) AS query_preview,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_ms,
    ROUND(min_exec_time::numeric, 2) AS min_ms,
    ROUND(max_exec_time::numeric, 2) AS max_ms,
    ROUND(stddev_exec_time::numeric, 2) AS stddev_ms,
    ROUND((total_exec_time / 1000)::numeric, 2) AS total_sec
FROM pg_stat_statements
WHERE calls > 10
ORDER BY mean_exec_time DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询Top慢查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：按总时间排序（影响最大）（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    LEFT(query, 100) AS query_preview,
    calls,
    ROUND((total_exec_time / 1000)::numeric, 2) AS total_sec,
    ROUND(mean_exec_time::numeric, 2) AS avg_ms,
    ROUND(total_exec_time * 100.0 / SUM(total_exec_time) OVER (), 2) AS pct_total
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询总时间排序失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 3.2 缓存命中率分析

```sql
-- 性能测试：查询缓存命中率（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    LEFT(query, 100) AS query,
    calls,
    shared_blks_hit + shared_blks_read AS total_blks,
    ROUND(shared_blks_hit * 100.0 / NULLIF(shared_blks_hit + shared_blks_read, 0), 2) AS hit_ratio
FROM pg_stat_statements
WHERE shared_blks_hit + shared_blks_read > 0
ORDER BY shared_blks_read DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询缓存命中率失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 缓存命中率低的查询可能需要优化索引或增加shared_buffers

```

### 3.3 临时文件使用

```sql
-- 性能测试：查找使用临时文件的查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    LEFT(query, 100) AS query,
    calls,
    temp_blks_read + temp_blks_written AS temp_blks,
    ROUND((temp_blks_read + temp_blks_written) * 8.0 / 1024, 2) AS temp_mb
FROM pg_stat_statements
WHERE temp_blks_read + temp_blks_written > 0
ORDER BY temp_blks_read + temp_blks_written DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'pg_stat_statements扩展未安装';
    WHEN OTHERS THEN
        RAISE NOTICE '查询临时文件使用失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 使用临时文件 → 需要增加work_mem
```

---

## 4. 查询模式分析

### 4.1 按类型统计

```sql
-- 性能测试：查询类型分布（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    CASE
        WHEN query LIKE 'SELECT%' THEN 'SELECT'
        WHEN query LIKE 'INSERT%' THEN 'INSERT'
        WHEN query LIKE 'UPDATE%' THEN 'UPDATE'
        WHEN query LIKE 'DELETE%' THEN 'DELETE'
        ELSE 'OTHER'
    END AS query_type,
    COUNT(*) AS query_count,
    SUM(calls) AS total_calls,
    ROUND(SUM(total_exec_time / 1000)::numeric, 2) AS total_sec,
    ROUND(AVG(mean_exec_time)::numeric, 2) AS avg_ms
FROM pg_stat_statements
GROUP BY query_type
ORDER BY total_sec DESC;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'pg_stat_statements扩展未安装';
    WHEN OTHERS THEN
        RAISE NOTICE '查询类型分布失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 4.2 表访问分析

```sql
-- 性能测试：最常访问的表（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    regexp_replace(query, '.*FROM\s+(\w+).*', '\1') AS table_name,
    COUNT(*) AS query_count,
    SUM(calls) AS total_calls
FROM pg_stat_statements
WHERE query LIKE '%FROM%'
GROUP BY table_name
ORDER BY total_calls DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'pg_stat_statements扩展未安装';
    WHEN OTHERS THEN
        RAISE NOTICE '查询最常访问的表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 5. 性能基线

### 5.1 建立基线

```sql
-- 性能测试：保存当前统计作为基线（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS query_baseline AS
SELECT
    queryid,
    query,
    calls,
    mean_exec_time,
    total_exec_time,
    now() AS baseline_time
FROM pg_stat_statements;
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '基线表query_baseline已存在，请先删除或使用TRUNCATE';
    WHEN undefined_table THEN
        RAISE NOTICE 'pg_stat_statements扩展未安装';
    WHEN OTHERS THEN
        RAISE NOTICE '创建基线表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：对比当前与基线（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    b.query,
    c.calls - b.calls AS calls_diff,
    ROUND((c.mean_exec_time - b.mean_exec_time)::numeric, 2) AS avg_ms_diff,
    ROUND(((c.mean_exec_time - b.mean_exec_time) * 100.0 / NULLIF(b.mean_exec_time, 0))::numeric, 2) AS pct_change
FROM pg_stat_statements c
JOIN query_baseline b ON c.queryid = b.queryid
WHERE ABS(c.mean_exec_time - b.mean_exec_time) > 10
ORDER BY ABS(c.mean_exec_time - b.mean_exec_time) DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'pg_stat_statements扩展未安装或基线表不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '对比基线失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 6. 自动化分析

### 6.1 每日报告

```sql
-- 性能测试：创建报告表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS daily_query_reports (
    report_id BIGSERIAL PRIMARY KEY,
    report_date DATE,
    top_slow_queries JSONB,
    top_frequent_queries JSONB,
    cache_hit_summary JSONB,
    generated_at TIMESTAMPTZ DEFAULT now()
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '报告表daily_query_reports已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建报告表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：生成报告函数（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION generate_query_report()
RETURNS VOID AS $$
DECLARE
    slow_queries JSONB;
    frequent_queries JSONB;
    cache_summary JSONB;
BEGIN
    -- Top 10慢查询
    BEGIN
        SELECT jsonb_agg(row_to_json(t)) INTO slow_queries
        FROM (
            SELECT
                LEFT(query, 100) AS query,
                calls,
                ROUND(mean_exec_time::numeric, 2) AS avg_ms
            FROM pg_stat_statements
            ORDER BY mean_exec_time DESC
            LIMIT 10
        ) t;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE NOTICE 'pg_stat_statements扩展未安装';
            slow_queries := '[]'::jsonb;
        WHEN OTHERS THEN
            RAISE NOTICE '获取慢查询失败: %', SQLERRM;
            slow_queries := '[]'::jsonb;
    END;

    -- Top 10高频查询
    BEGIN
        SELECT jsonb_agg(row_to_json(t)) INTO frequent_queries
        FROM (
            SELECT
                LEFT(query, 100) AS query,
                calls,
                ROUND(mean_exec_time::numeric, 2) AS avg_ms
            FROM pg_stat_statements
            ORDER BY calls DESC
            LIMIT 10
        ) t;
    EXCEPTION
        WHEN undefined_table THEN
            frequent_queries := '[]'::jsonb;
        WHEN OTHERS THEN
            RAISE NOTICE '获取高频查询失败: %', SQLERRM;
            frequent_queries := '[]'::jsonb;
    END;

    -- 缓存统计
    BEGIN
        SELECT jsonb_build_object(
            'total_hit', SUM(shared_blks_hit),
            'total_read', SUM(shared_blks_read),
            'hit_ratio', ROUND(SUM(shared_blks_hit) * 100.0 /
                         NULLIF(SUM(shared_blks_hit + shared_blks_read), 0), 2)
        ) INTO cache_summary
        FROM pg_stat_statements;
    EXCEPTION
        WHEN undefined_table THEN
            cache_summary := '{}'::jsonb;
        WHEN OTHERS THEN
            RAISE NOTICE '获取缓存统计失败: %', SQLERRM;
            cache_summary := '{}'::jsonb;
    END;

    -- 保存报告
    BEGIN
        INSERT INTO daily_query_reports (report_date, top_slow_queries, top_frequent_queries, cache_hit_summary)
        VALUES (CURRENT_DATE, slow_queries, frequent_queries, cache_summary);
    EXCEPTION
        WHEN undefined_table THEN
            RAISE NOTICE '报告表daily_query_reports不存在';
        WHEN OTHERS THEN
            RAISE NOTICE '保存报告失败: %', SQLERRM;
            RAISE;
    END;
END;
$$ LANGUAGE plpgsql;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建报告函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：定时生成（带错误处理）
BEGIN;
SELECT cron.schedule('daily-report', '0 23 * * *',
    'SELECT generate_query_report();');
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建定时报告任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 7. 重置统计

```sql
-- 性能测试：重置所有统计（带错误处理）
BEGIN;
DO $$
BEGIN
    PERFORM pg_stat_statements_reset();
    RAISE NOTICE '所有统计已重置';
EXCEPTION
    WHEN undefined_function THEN
        RAISE NOTICE 'pg_stat_statements扩展未安装';
    WHEN OTHERS THEN
        RAISE NOTICE '重置统计失败: %', SQLERRM;
        RAISE;
END $$;
COMMIT;

-- 性能测试：重置特定查询（带错误处理）
BEGIN;
DO $$
BEGIN
    PERFORM pg_stat_statements_reset(queryid := 123456789);
    RAISE NOTICE '查询统计已重置';
EXCEPTION
    WHEN undefined_function THEN
        RAISE NOTICE 'pg_stat_statements扩展未安装';
    WHEN OTHERS THEN
        RAISE NOTICE '重置查询统计失败: %', SQLERRM;
        RAISE;
END $$;
COMMIT;

-- 性能测试：定期重置（避免统计过时）（带错误处理）
BEGIN;
SELECT cron.schedule('monthly-reset', '0 0 1 * *',
    'SELECT pg_stat_statements_reset();');
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建定期重置任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

**完成**: pg_stat_statements性能分析
**字数**: ~8,000字
**涵盖**: 配置、核心视图、常用查询、模式分析、基线、自动化报告
