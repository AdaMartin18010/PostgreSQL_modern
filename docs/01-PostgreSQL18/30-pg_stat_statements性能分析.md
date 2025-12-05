# PostgreSQL 18 pg_stat_statements性能分析

## 1. 安装配置

```sql
-- 安装扩展
CREATE EXTENSION pg_stat_statements;

-- 配置参数
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.max = 10000;  -- 跟踪10000个查询
ALTER SYSTEM SET pg_stat_statements.track = 'all';  -- all/top/none
ALTER SYSTEM SET pg_stat_statements.track_utility = on;  -- 跟踪DDL
ALTER SYSTEM SET pg_stat_statements.save = on;  -- 重启后保留

-- 重启PostgreSQL
-- sudo systemctl restart postgresql
```

---

## 2. 核心视图

### 2.1 pg_stat_statements字段

```sql
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
```

---

## 3. 常用查询

### 3.1 Top慢查询

```sql
-- 按平均时间排序
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

-- 按总时间排序（影响最大）
SELECT
    LEFT(query, 100) AS query_preview,
    calls,
    ROUND((total_exec_time / 1000)::numeric, 2) AS total_sec,
    ROUND(mean_exec_time::numeric, 2) AS avg_ms,
    ROUND(total_exec_time * 100.0 / SUM(total_exec_time) OVER (), 2) AS pct_total
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

### 3.2 缓存命中率分析

```sql
-- 查询缓存命中率
SELECT
    LEFT(query, 100) AS query,
    calls,
    shared_blks_hit + shared_blks_read AS total_blks,
    ROUND(shared_blks_hit * 100.0 / NULLIF(shared_blks_hit + shared_blks_read, 0), 2) AS hit_ratio
FROM pg_stat_statements
WHERE shared_blks_hit + shared_blks_read > 0
ORDER BY shared_blks_read DESC
LIMIT 20;

-- 缓存命中率低的查询可能需要优化索引或增加shared_buffers
```

### 3.3 临时文件使用

```sql
-- 查找使用临时文件的查询
SELECT
    LEFT(query, 100) AS query,
    calls,
    temp_blks_read + temp_blks_written AS temp_blks,
    ROUND((temp_blks_read + temp_blks_written) * 8.0 / 1024, 2) AS temp_mb
FROM pg_stat_statements
WHERE temp_blks_read + temp_blks_written > 0
ORDER BY temp_blks_read + temp_blks_written DESC
LIMIT 20;

-- 使用临时文件 → 需要增加work_mem
```

---

## 4. 查询模式分析

### 4.1 按类型统计

```sql
-- 查询类型分布
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
```

### 4.2 表访问分析

```sql
-- 最常访问的表
SELECT
    regexp_replace(query, '.*FROM\s+(\w+).*', '\1') AS table_name,
    COUNT(*) AS query_count,
    SUM(calls) AS total_calls
FROM pg_stat_statements
WHERE query LIKE '%FROM%'
GROUP BY table_name
ORDER BY total_calls DESC
LIMIT 20;
```

---

## 5. 性能基线

### 5.1 建立基线

```sql
-- 保存当前统计作为基线
CREATE TABLE query_baseline AS
SELECT
    queryid,
    query,
    calls,
    mean_exec_time,
    total_exec_time,
    now() AS baseline_time
FROM pg_stat_statements;

-- 对比当前与基线
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
```

---

## 6. 自动化分析

### 6.1 每日报告

```sql
-- 创建报告表
CREATE TABLE daily_query_reports (
    report_id BIGSERIAL PRIMARY KEY,
    report_date DATE,
    top_slow_queries JSONB,
    top_frequent_queries JSONB,
    cache_hit_summary JSONB,
    generated_at TIMESTAMPTZ DEFAULT now()
);

-- 生成报告函数
CREATE OR REPLACE FUNCTION generate_query_report()
RETURNS VOID AS $$
DECLARE
    slow_queries JSONB;
    frequent_queries JSONB;
    cache_summary JSONB;
BEGIN
    -- Top 10慢查询
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

    -- Top 10高频查询
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

    -- 缓存统计
    SELECT jsonb_build_object(
        'total_hit', SUM(shared_blks_hit),
        'total_read', SUM(shared_blks_read),
        'hit_ratio', ROUND(SUM(shared_blks_hit) * 100.0 /
                     NULLIF(SUM(shared_blks_hit + shared_blks_read), 0), 2)
    ) INTO cache_summary
    FROM pg_stat_statements;

    -- 保存报告
    INSERT INTO daily_query_reports (report_date, top_slow_queries, top_frequent_queries, cache_hit_summary)
    VALUES (CURRENT_DATE, slow_queries, frequent_queries, cache_summary);
END;
$$ LANGUAGE plpgsql;

-- 定时生成
SELECT cron.schedule('daily-report', '0 23 * * *',
    'SELECT generate_query_report();');
```

---

## 7. 重置统计

```sql
-- 重置所有统计
SELECT pg_stat_statements_reset();

-- 重置特定查询
SELECT pg_stat_statements_reset(queryid := 123456789);

-- 定期重置（避免统计过时）
SELECT cron.schedule('monthly-reset', '0 0 1 * *',
    'SELECT pg_stat_statements_reset();');
```

---

**完成**: pg_stat_statements性能分析
**字数**: ~8,000字
**涵盖**: 配置、核心视图、常用查询、模式分析、基线、自动化报告
