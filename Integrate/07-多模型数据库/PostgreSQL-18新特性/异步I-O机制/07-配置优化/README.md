> **章节编号**: 7
> **章节标题**: 配置优化
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

# 7. 配置优化

## 7. 配置优化

## 📑 目录

- [7. 配置优化](#7-配置优化)
  - [7. 配置优化](#7-配置优化-1)
  - [📑 目录](#-目录)
    - [7.1 I/O 线程配置](#71-io-线程配置)
      - [7.1.1 线程数配置](#711-线程数配置)
      - [7.1.2 负载调整](#712-负载调整)
      - [7.1.3 性能调优](#713-性能调优)
    - [7.2 内存配置](#72-内存配置)
      - [7.2.1 异步 I/O 缓冲区](#721-异步-io-缓冲区)
      - [7.2.2 共享缓冲区](#722-共享缓冲区)
      - [7.2.3 工作内存](#723-工作内存)
    - [7.3 监控配置](#73-监控配置)
      - [7.3.1 I/O 统计启用](#731-io-统计启用)
      - [7.3.2 异步 I/O 监控](#732-异步-io-监控)
      - [7.3.3 性能指标分析](#733-性能指标分析)

---

### 7.1 I/O 线程配置

#### 7.1.1 线程数配置

**线程数配置建议**:

```sql
-- 根据 CPU 核心数配置
-- 建议值: CPU 核心数 / 2
ALTER SYSTEM SET async_io_threads = 8;

-- 根据 I/O 负载调整
-- 高 I/O 负载: 增加线程数
ALTER SYSTEM SET async_io_threads = 16;

-- 低 I/O 负载: 减少线程数
ALTER SYSTEM SET async_io_threads = 4;
```

**配置建议**:

| CPU 核心数 | 建议线程数 | 说明       |
| ---------- | ---------- | ---------- |
| **4**      | 2          | 小型应用   |
| **8**      | 4          | 中型应用   |
| **16**     | 8          | 大型应用   |
| **32+**    | 16         | 高性能应用 |

#### 7.1.2 负载调整

**负载调整策略**:

| 负载类型   | 线程数配置 | 说明           |
| ---------- | ---------- | -------------- |
| **低负载** | 4          | 减少资源消耗   |
| **中负载** | 8          | 平衡性能和资源 |
| **高负载** | 16         | 最大化性能     |

#### 7.1.3 性能调优

**性能调优建议**:

1. **监控线程利用率**: 监控 I/O 线程使用情况
2. **动态调整**: 根据负载动态调整线程数
3. **避免过度配置**: 过多线程可能导致上下文切换开销

### 7.2 内存配置

#### 7.2.1 异步 I/O 缓冲区

**缓冲区配置**:

```sql
-- 异步 I/O 缓冲区大小
ALTER SYSTEM SET async_io_buffer_size = '256MB';
```

**配置建议**:

| 数据规模 | 缓冲区大小 | 说明           |
| -------- | ---------- | -------------- |
| **小型** | 64MB       | <100GB 数据    |
| **中型** | 256MB      | 100GB-1TB 数据 |
| **大型** | 512MB      | >1TB 数据      |

#### 7.2.2 共享缓冲区

**共享缓冲区配置**:

```sql
-- 共享缓冲区（影响 I/O 性能）
ALTER SYSTEM SET shared_buffers = '4GB';
```

**配置建议**:

| 内存大小  | shared_buffers | 说明     |
| --------- | -------------- | -------- |
| **16GB**  | 4GB            | 25% 内存 |
| **32GB**  | 8GB            | 25% 内存 |
| **64GB+** | 16GB           | 25% 内存 |

#### 7.2.3 工作内存

**工作内存配置**:

```sql
-- 工作内存（影响 JSONB 处理）
ALTER SYSTEM SET work_mem = '256MB';
```

**配置建议**:

| 场景           | work_mem | 说明         |
| -------------- | -------- | ------------ |
| **JSONB 写入** | 256MB    | 批量写入场景 |
| **查询优化**   | 128MB    | 一般查询场景 |

### 7.3 监控配置

#### 7.3.1 I/O 统计启用

**启用 I/O 统计**（完整配置脚本）:

```sql
-- 启用I/O统计和监控（带错误处理）
DO $$
BEGIN
    -- 1. 启用I/O时间跟踪
ALTER SYSTEM SET track_io_timing = ON;

    -- 2. 启用pg_stat_statements扩展（如果未启用）
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

    -- 3. 设置日志级别（记录慢查询）
    ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 记录超过1秒的查询

    -- 4. 重新加载配置
    PERFORM pg_reload_conf();

    RAISE NOTICE '✅ I/O统计和监控已启用';
    RAISE NOTICE '   - track_io_timing: ON';
    RAISE NOTICE '   - pg_stat_statements: 已启用';
    RAISE NOTICE '   - 慢查询日志: 已启用（>1秒）';

EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，需要超级用户权限';
    WHEN OTHERS THEN
        RAISE EXCEPTION '启用I/O统计失败: %', SQLERRM;
END $$;
```

#### 7.3.2 异步 I/O 监控

**完整监控查询脚本**（PostgreSQL 18实际监控方法）:

```sql
-- 1. 查看I/O统计（PostgreSQL 18新增pg_stat_io视图）
DO $$
DECLARE
    io_stats RECORD;
BEGIN
    RAISE NOTICE '=== PostgreSQL 18 I/O统计 ===';

    FOR io_stats IN
SELECT
            object,
            context,
            reads,
            writes,
            read_time,
            write_time,
            CASE
                WHEN reads > 0 THEN ROUND(read_time::numeric / reads, 2)
                ELSE 0
            END as avg_read_time_ms,
            CASE
                WHEN writes > 0 THEN ROUND(write_time::numeric / writes, 2)
                ELSE 0
            END as avg_write_time_ms
        FROM pg_stat_io
        WHERE reads > 0 OR writes > 0
        ORDER BY reads + writes DESC
        LIMIT 10
    LOOP
        RAISE NOTICE '对象: %, 上下文: %, 读取: %, 写入: %, 平均读取延迟: %ms, 平均写入延迟: %ms',
            io_stats.object,
            io_stats.context,
            io_stats.reads,
            io_stats.writes,
            io_stats.avg_read_time_ms,
            io_stats.avg_write_time_ms;
    END LOOP;

EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_stat_io视图不存在，可能需要PostgreSQL 18+';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询I/O统计失败: %', SQLERRM;
END $$;

-- 2. 查看数据库级I/O统计
SELECT
    datname,
    blk_read_time,
    blk_write_time,
    blks_read,
    blks_hit,
    CASE
        WHEN blks_read > 0 THEN ROUND(blk_read_time::numeric / blks_read, 2)
        ELSE 0
    END as avg_read_time_ms,
    CASE
        WHEN blks_hit > 0 THEN ROUND(100.0 * blks_hit / (blks_read + blks_hit), 2)
        ELSE 0
    END as cache_hit_ratio
FROM pg_stat_database
WHERE datname = current_database();

-- 3. 查看表级I/O统计
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    heap_blks_read,
    heap_blks_hit,
    CASE
        WHEN heap_blks_read + heap_blks_hit > 0
        THEN ROUND(100.0 * heap_blks_hit / (heap_blks_read + heap_blks_hit), 2)
        ELSE 0
    END as heap_cache_hit_ratio
FROM pg_stat_user_tables
ORDER BY seq_scan DESC
LIMIT 10;
```

#### 7.3.3 性能指标分析

**关键指标监控仪表板**:

```sql
-- 异步I/O性能监控仪表板（带错误处理）
DO $$
DECLARE
    io_direct_val TEXT;
    io_concurrency_val INTEGER;
    total_reads BIGINT;
    total_writes BIGINT;
    total_read_time NUMERIC;
    total_write_time NUMERIC;
    avg_read_time_ms NUMERIC;
    avg_write_time_ms NUMERIC;
BEGIN
    RAISE NOTICE '╔══════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║      PostgreSQL 18 异步I/O性能监控仪表板                  ║';
    RAISE NOTICE '╚══════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';

    -- 1. 配置检查
    SELECT setting INTO io_direct_val
    FROM pg_settings WHERE name = 'io_direct';

    SELECT setting::INTEGER INTO io_concurrency_val
    FROM pg_settings WHERE name = 'effective_io_concurrency';

    RAISE NOTICE '【配置状态】';
    RAISE NOTICE '  io_direct: %', io_direct_val;
    RAISE NOTICE '  effective_io_concurrency: %', io_concurrency_val;

    IF io_direct_val = 'off' THEN
        RAISE WARNING '  ⚠️  io_direct未启用，异步I/O可能未生效';
    ELSE
        RAISE NOTICE '  ✅ 异步I/O配置正确';
    END IF;

    RAISE NOTICE '';

    -- 2. I/O统计汇总
    SELECT
        COALESCE(SUM(reads), 0),
        COALESCE(SUM(writes), 0),
        COALESCE(SUM(read_time), 0),
        COALESCE(SUM(write_time), 0)
    INTO total_reads, total_writes, total_read_time, total_write_time
    FROM pg_stat_io;

    IF total_reads > 0 THEN
        avg_read_time_ms := ROUND(total_read_time::numeric / total_reads, 2);
    ELSE
        avg_read_time_ms := 0;
    END IF;

    IF total_writes > 0 THEN
        avg_write_time_ms := ROUND(total_write_time::numeric / total_writes, 2);
    ELSE
        avg_write_time_ms := 0;
    END IF;

    RAISE NOTICE '【I/O统计汇总】';
    RAISE NOTICE '  总读取次数: %', total_reads;
    RAISE NOTICE '  总写入次数: %', total_writes;
    RAISE NOTICE '  总读取时间: % ms', total_read_time;
    RAISE NOTICE '  总写入时间: % ms', total_write_time;
    RAISE NOTICE '  平均读取延迟: % ms', avg_read_time_ms;
    RAISE NOTICE '  平均写入延迟: % ms', avg_write_time_ms;

    -- 3. 性能评估
    RAISE NOTICE '';
    RAISE NOTICE '【性能评估】';

    IF avg_read_time_ms < 5 THEN
        RAISE NOTICE '  ✅ 读取性能: 优秀 (<5ms)';
    ELSIF avg_read_time_ms < 10 THEN
        RAISE NOTICE '  ⚠️  读取性能: 良好 (5-10ms)';
    ELSE
        RAISE NOTICE '  ❌ 读取性能: 需要优化 (>10ms)';
    END IF;

    IF avg_write_time_ms < 5 THEN
        RAISE NOTICE '  ✅ 写入性能: 优秀 (<5ms)';
    ELSIF avg_write_time_ms < 10 THEN
        RAISE NOTICE '  ⚠️  写入性能: 良好 (5-10ms)';
    ELSE
        RAISE NOTICE '  ❌ 写入性能: 需要优化 (>10ms)';
    END IF;

EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_stat_io视图不存在，可能需要PostgreSQL 18+';
    WHEN OTHERS THEN
        RAISE EXCEPTION '监控查询失败: %', SQLERRM;
END $$;
```

**关键指标参考值**:

| 指标                   | 优秀 | 良好 | 需优化 | 说明              |
| ---------------------- | ---- | ---- | ------ | ----------------- |
| **平均读取延迟**       | <5ms | 5-10ms | >10ms | I/O读取平均延迟    |
| **平均写入延迟**       | <5ms | 5-10ms | >10ms | I/O写入平均延迟    |
| **缓存命中率**         | >95% | 90-95% | <90%   | 数据缓存命中率    |
| **I/O吞吐量**          | >2000 ops/s | 1000-2000 ops/s | <1000 ops/s | I/O操作吞吐量 |
| **CPU利用率**          | 70-90% | 50-70% | <50%或>90% | CPU使用率（异步I/O后） |

---

**返回**: [文档首页](../README.md) | [上一章节](../06-性能分析/README.md) | [下一章节](../08-实际应用场景/README.md)
