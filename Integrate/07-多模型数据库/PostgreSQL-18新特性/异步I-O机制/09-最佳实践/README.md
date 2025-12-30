# 9. 最佳实践

> **章节编号**: 9
> **章节标题**: 最佳实践
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 9. 最佳实践

## 📑 目录

- [9. 最佳实践](#9-最佳实践)
  - [9. 最佳实践](#9-最佳实践-1)
  - [📑 目录](#-目录)
    - [9.1 批量操作](#91-批量操作)
    - [9.2 并发写入](#92-并发写入)
    - [9.3 性能监控](#93-性能监控)

---

---

### 9.1 批量操作

批量操作是充分利用异步 I/O 机制的关键实践，能够显著提升写入性能。

**批量插入优化**:

```sql
-- ❌ 不推荐：逐条插入
INSERT INTO table1 VALUES (...);
INSERT INTO table1 VALUES (...);
INSERT INTO table1 VALUES (...);

-- ✅ 推荐：批量插入
INSERT INTO table1 VALUES
    (...),
    (...),
    (...);
```

**批量更新优化**:

```sql
-- ✅ 使用批量更新
UPDATE table1
SET column1 = new_value1
WHERE id IN (1, 2, 3, ...);

-- ✅ 使用CTE批量更新
WITH updates AS (
    SELECT unnest(ARRAY[1, 2, 3]) AS id,
           unnest(ARRAY['val1', 'val2', 'val3']) AS value
)
UPDATE table1 t
SET column1 = u.value
FROM updates u
WHERE t.id = u.id;
```

**批量操作最佳实践**:

- **批量大小**: 建议每批1000-10000条记录
- **事务控制**: 合理控制事务大小，避免长事务
- **错误处理**: 实现批量操作的错误处理和重试机制

**性能对比**:

| 操作方式 | 性能 | 说明 |
|---------|------|------|
| **逐条插入** | 基准 | 性能最低 |
| **批量插入(100条)** | +150% | 性能提升明显 |
| **批量插入(1000条)** | +250% | 最佳性能 |

### 9.2 并发写入

合理利用并发写入能力，能够最大化异步 I/O 的性能优势。

**并发写入配置**:

```sql
-- 配置I/O并发数
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET wal_io_concurrency = 200;

-- 配置连接数
ALTER SYSTEM SET max_connections = 500;
```

**并发写入模式**:

1. **多连接并发**: 多个应用连接同时写入
2. **并行写入**: 单个查询内的并行写入
3. **批量并发**: 批量操作与并发结合

**并发写入示例**:

```python
# Python并发写入示例
import asyncio
import asyncpg

async def concurrent_write():
    # 创建连接池
    pool = await asyncpg.create_pool(
        host='localhost',
        database='testdb',
        min_size=10,
        max_size=50
    )

    # 并发写入任务
    async def write_batch(batch_data):
        async with pool.acquire() as conn:
            await conn.executemany(
                "INSERT INTO table1 VALUES ($1, $2, $3)",
                batch_data
            )

    # 创建多个并发任务
    tasks = [
        write_batch(batch1),
        write_batch(batch2),
        write_batch(batch3),
        # ... 更多批次
    ]

    await asyncio.gather(*tasks)
```

**并发控制**:

- **连接池大小**: 根据实际负载调整
- **并发度**: 避免过度并发导致资源竞争
- **锁竞争**: 监控锁竞争情况，优化表结构

### 9.3 性能监控

持续监控异步 I/O 性能，及时发现问题并优化配置。

**关键监控指标**:

```sql
-- 监控I/O统计
SELECT
    context,
    reads,
    writes,
    extends,
    fsyncs,
    stats_reset
FROM pg_stat_io
WHERE context LIKE '%async%';

-- 监控查询性能
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

**性能监控脚本**:

```sql
-- 完整的性能监控查询
WITH io_stats AS (
    SELECT
        context,
        SUM(reads) AS total_reads,
        SUM(writes) AS total_writes,
        SUM(extends) AS total_extends,
        SUM(fsyncs) AS total_fsyncs
    FROM pg_stat_io
    WHERE context LIKE '%async%'
    GROUP BY context
)
SELECT
    'I/O Statistics' AS metric,
    context,
    total_reads,
    total_writes,
    total_extends,
    total_fsyncs
FROM io_stats;
```

**监控最佳实践**:

- **定期监控**: 设置定期监控任务
- **告警机制**: 设置关键指标告警阈值
- **性能分析**: 定期分析性能趋势
- **优化调整**: 根据监控结果调整配置

**关键指标阈值**:

| 指标 | 正常范围 | 告警阈值 |
|------|---------|---------|
| **I/O等待时间** | <10% | >20% |
| **CPU利用率** | 60-80% | >90% |
| **查询延迟P99** | <100ms | >500ms |
| **连接数** | <80%最大连接数 | >90%最大连接数 |

### 9.4 索引优化

#### 9.4.1 JSONB索引优化

**GIN索引创建**：

```sql
-- 创建JSONB GIN索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'documents' AND indexname = 'idx_documents_metadata_gin'
    ) THEN
        CREATE INDEX CONCURRENTLY idx_documents_metadata_gin
        ON documents USING GIN (metadata);
        RAISE NOTICE '✅ JSONB GIN索引创建成功';
    ELSE
        RAISE NOTICE '索引已存在';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;
```

**索引使用优化**：

```sql
-- ✅ 推荐：使用索引的查询
SELECT * FROM documents
WHERE metadata @> '{"category": "tech"}'::jsonb;

-- ❌ 不推荐：不使用索引的查询
SELECT * FROM documents
WHERE metadata->>'category' = 'tech';
```

#### 9.4.2 索引维护

**索引维护最佳实践**：

```sql
-- 定期重建索引
REINDEX INDEX CONCURRENTLY idx_documents_metadata_gin;

-- 更新统计信息
ANALYZE documents;

-- 监控索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'documents'
ORDER BY idx_scan DESC;
```

### 9.5 查询优化

#### 9.5.1 查询性能优化

**查询优化技巧**：

```sql
-- ✅ 推荐：使用LIMIT限制结果集
SELECT * FROM documents
WHERE metadata @> '{"category": "tech"}'::jsonb
ORDER BY created_at DESC
LIMIT 100;

-- ❌ 不推荐：返回大量结果
SELECT * FROM documents
WHERE metadata @> '{"category": "tech"}'::jsonb;
-- 可能返回数万条记录
```

**查询计划优化**：

```sql
-- 分析查询计划
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM documents
WHERE metadata @> '{"category": "tech"}'::jsonb
ORDER BY created_at DESC
LIMIT 100;

-- 如果发现Seq Scan，考虑创建索引
CREATE INDEX idx_documents_created_at ON documents (created_at DESC);
```

#### 9.5.2 并行查询优化

**并行查询配置**：

```sql
-- 启用并行查询
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET parallel_workers = 4;

-- 设置并行查询阈值
ALTER SYSTEM SET min_parallel_table_scan_size = '8MB';
ALTER SYSTEM SET min_parallel_index_scan_size = '512KB';
```

**并行查询示例**：

```sql
-- 并行查询（自动使用并行计划）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*), category
FROM documents
WHERE created_at > NOW() - INTERVAL '1 day'
GROUP BY category;
```

### 9.6 资源管理

#### 9.6.1 内存管理

**内存配置优化**：

```sql
-- 共享缓冲区（影响I/O性能）
ALTER SYSTEM SET shared_buffers = '4GB';

-- 工作内存（影响查询性能）
ALTER SYSTEM SET work_mem = '64MB';

-- 维护工作内存（影响维护操作）
ALTER SYSTEM SET maintenance_work_mem = '1GB';

-- 有效缓存大小（影响查询计划）
ALTER SYSTEM SET effective_cache_size = '12GB';
```

**内存监控**：

```sql
-- 监控内存使用
SELECT
    name,
    setting,
    unit,
    CASE
        WHEN name = 'shared_buffers' THEN pg_size_pretty(setting::bigint)
        WHEN name = 'work_mem' THEN pg_size_pretty(setting::bigint)
        ELSE setting
    END AS formatted_value
FROM pg_settings
WHERE name IN (
    'shared_buffers',
    'work_mem',
    'maintenance_work_mem',
    'effective_cache_size'
);
```

#### 9.6.2 CPU管理

**CPU配置优化**：

```sql
-- 最大工作进程数
ALTER SYSTEM SET max_worker_processes = 16;

-- 并行工作线程数
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
```

**CPU监控**：

```sql
-- 监控CPU使用情况
SELECT
    pid,
    usename,
    application_name,
    state,
    query_start,
    NOW() - query_start AS duration,
    LEFT(query, 100) AS query_preview
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;
```

### 9.7 安全最佳实践

#### 9.7.1 权限管理

**权限配置**：

```sql
-- 创建专用用户
CREATE USER app_user WITH PASSWORD 'secure_password';

-- 授予必要权限
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- 启用行级安全
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 创建安全策略
CREATE POLICY documents_access_policy ON documents
FOR ALL
TO app_user
USING (true);
```

#### 9.7.2 审计日志

**审计日志配置**：

```sql
-- 启用审计日志
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_duration = on;

-- 重新加载配置
SELECT pg_reload_conf();
```

---

**返回**: [文档首页](../README.md) | [上一章节](../08-实际应用场景/README.md) | [下一章节](../10-监控和诊断/README.md)
