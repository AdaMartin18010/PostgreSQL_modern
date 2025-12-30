> **章节编号**: 5
> **章节标题**: 使用指南
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

# 5. 使用指南

## 5. 使用指南

## 📑 目录

- [5. 使用指南](#5-使用指南)
  - [5. 使用指南](#5-使用指南-1)
  - [📑 目录](#-目录)
  - [5.1 启用异步 I/O](#51-启用异步-io)
    - [5.1.1 配置步骤](#511-配置步骤)
      - [5.1.2 验证配置](#512-验证配置)
      - [5.1.3 配置建议](#513-配置建议)
    - [5.2 JSONB 写入优化](#52-jsonb-写入优化)
      - [5.2.1 传统同步写入](#521-传统同步写入)
      - [5.2.2 异步写入优化](#522-异步写入优化)
      - [5.2.3 最佳实践](#523-最佳实践)
    - [5.3 批量写入示例](#53-批量写入示例)
      - [5.3.1 Python 批量插入](#531-python-批量插入)
      - [5.3.2 性能优化技巧](#532-性能优化技巧)
      - [5.3.3 错误处理](#533-错误处理)
    - [5.4 事务管理优化](#54-事务管理优化)
      - [5.4.1 事务大小控制](#541-事务大小控制)
      - [5.4.2 并发事务管理](#542-并发事务管理)
    - [5.5 连接池配置](#55-连接池配置)
      - [5.5.1 连接池大小](#551-连接池大小)
      - [5.5.2 连接池监控](#552-连接池监控)
    - [5.6 错误处理和重试](#56-错误处理和重试)
      - [5.6.1 错误处理策略](#561-错误处理策略)
      - [5.6.2 批量操作错误处理](#562-批量操作错误处理)

---

## 5.1 启用异步 I/O

### 5.1.1 配置步骤

**启用异步 I/O**（PostgreSQL 18 实际配置）:

```sql
-- PostgreSQL 18 异步I/O配置（带错误处理和验证）
DO $$
DECLARE
    io_direct_val TEXT;
    io_concurrency_val INTEGER;
    kernel_version TEXT;
BEGIN
    -- 1. 启用Direct I/O（绕过OS缓存，使用io_uring）
    ALTER SYSTEM SET io_direct = 'data,wal';

    -- 2. 配置I/O并发数（关键参数）
    -- SSD推荐: 200-300, HDD推荐: 50-100
    ALTER SYSTEM SET effective_io_concurrency = 200;
    ALTER SYSTEM SET maintenance_io_concurrency = 200;
    ALTER SYSTEM SET wal_io_concurrency = 200;

    -- 3. io_uring队列深度（Linux内核5.1+）
    ALTER SYSTEM SET io_uring_queue_depth = 256;

    -- 4. 重新加载配置
    PERFORM pg_reload_conf();

    -- 5. 验证配置
    SELECT setting INTO io_direct_val
    FROM pg_settings WHERE name = 'io_direct';

    SELECT setting::INTEGER INTO io_concurrency_val
    FROM pg_settings WHERE name = 'effective_io_concurrency';

    RAISE NOTICE '✅ io_direct: %', io_direct_val;
    RAISE NOTICE '✅ effective_io_concurrency: %', io_concurrency_val;
    RAISE NOTICE '✅ 异步I/O配置已启用';

EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，需要超级用户权限';
    WHEN OTHERS THEN
        RAISE EXCEPTION '配置异步I/O失败: %', SQLERRM;
END $$;
```

#### 5.1.2 验证配置

**验证配置**（完整检查脚本）:

```sql
-- 完整验证脚本（带错误处理）
DO $$
DECLARE
    pg_version TEXT;
    io_direct_val TEXT;
    io_concurrency_val INTEGER;
    wal_io_concurrency_val INTEGER;
    kernel_support BOOLEAN := FALSE;
BEGIN
    -- 1. 检查PostgreSQL版本
    SELECT version() INTO pg_version;
    IF pg_version NOT LIKE 'PostgreSQL 18%' THEN
        RAISE WARNING 'PostgreSQL 18+ required, current: %', pg_version;
    ELSE
        RAISE NOTICE '✅ PostgreSQL版本: %', pg_version;
    END IF;

    -- 2. 检查io_direct配置
    SELECT setting INTO io_direct_val
    FROM pg_settings WHERE name = 'io_direct';

    IF io_direct_val = 'off' THEN
        RAISE WARNING '❌ io_direct未启用，异步I/O可能未生效';
    ELSE
        RAISE NOTICE '✅ io_direct: %', io_direct_val;
    END IF;

    -- 3. 检查I/O并发数
    SELECT setting::INTEGER INTO io_concurrency_val
    FROM pg_settings WHERE name = 'effective_io_concurrency';

    IF io_concurrency_val <= 1 THEN
        RAISE WARNING '❌ effective_io_concurrency太低 (%), 建议设置为200+', io_concurrency_val;
    ELSE
        RAISE NOTICE '✅ effective_io_concurrency: %', io_concurrency_val;
    END IF;

    -- 4. 检查WAL I/O并发数
    SELECT setting::INTEGER INTO wal_io_concurrency_val
    FROM pg_settings WHERE name = 'wal_io_concurrency';

    RAISE NOTICE '✅ wal_io_concurrency: %', wal_io_concurrency_val;

    -- 5. 检查系统支持（需要系统级检查）
    RAISE NOTICE '📋 系统级检查:';
    RAISE NOTICE '   - Linux内核版本需要5.1+ (检查: uname -r)';
    RAISE NOTICE '   - io_uring支持 (检查: cat /boot/config-$(uname -r) | grep CONFIG_IO_URING)';
    RAISE NOTICE '   - 文件描述符限制 (检查: ulimit -n, 推荐65536+)';

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '验证配置失败: %', SQLERRM;
END $$;
```

#### 5.1.3 配置建议

**配置建议**（根据存储类型和负载）:

| 存储类型 | effective_io_concurrency | maintenance_io_concurrency | wal_io_concurrency | 说明 |
| ---------- | ----------------------- | -------------------------- | ------------------ | ---- |
| **HDD** | 50-100 | 50-100 | 50-100 | 机械硬盘，并发能力有限 |
| **SATA SSD** | 200 | 200 | 200 | SATA固态硬盘 |
| **NVMe SSD** | 200-300 | 200-300 | 200-300 | NVMe固态硬盘，推荐配置 |
| **NVMe RAID** | 300-500 | 300-500 | 300-500 | NVMe RAID阵列，高性能 |

**负载场景配置**:

| 场景 | effective_io_concurrency | wal_io_concurrency | io_uring_queue_depth | 说明 |
| ---- | ----------------------- | ------------------ | ------------------- | ---- |
| **OLTP低负载** | 100 | 100 | 128 | <100 TPS |
| **OLTP中负载** | 200 | 200 | 256 | 100-1000 TPS |
| **OLTP高负载** | 300 | 300 | 512 | >1000 TPS |
| **OLAP分析** | 500 | 500 | 512 | 大数据分析场景 |

### 5.2 JSONB 写入优化

#### 5.2.1 传统同步写入

**PostgreSQL 17 同步写入**:

```sql
-- 传统同步写入（PostgreSQL 17，带错误处理和性能测试）
DO $$
DECLARE
    insert_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
        RAISE EXCEPTION '表documents不存在，请先创建';
    END IF;

    INSERT INTO documents (content, metadata)
    VALUES
        ('{"title": "PostgreSQL", "body": "..."}', '{"author": "..."}'),
        ('{"title": "pgvector", "body": "..."}', '{"author": "..."}');

    GET DIAGNOSTICS insert_count = ROW_COUNT;
    RAISE NOTICE '同步写入完成: % 行', insert_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表documents不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '同步写入失败: %', SQLERRM;
END $$;

-- 每个 INSERT 必须等待 I/O 完成

```

#### 5.2.2 异步写入优化

**PostgreSQL 18 异步写入**:

```sql
-- PostgreSQL 18 异步写入（自动优化，带错误处理和性能测试）
DO $$
DECLARE
    insert_count INT;
    async_io_enabled BOOLEAN;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
        RAISE EXCEPTION '表documents不存在，请先创建';
    END IF;

    -- 检查异步I/O是否启用
    SELECT setting = 'on' INTO async_io_enabled
    FROM pg_settings
    WHERE name = 'async_io';

    IF NOT async_io_enabled THEN
        RAISE WARNING '异步I/O未启用，将使用同步I/O';
    ELSE
        RAISE NOTICE '异步I/O已启用，将自动优化写入';
    END IF;

    -- 相同 SQL，但内部使用异步 I/O
    INSERT INTO documents (content, metadata)
    VALUES
        ('{"title": "PostgreSQL", "body": "..."}', '{"author": "..."}'),
        ('{"title": "pgvector", "body": "..."}', '{"author": "..."}');

    GET DIAGNOSTICS insert_count = ROW_COUNT;
    RAISE NOTICE '异步写入完成: % 行', insert_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表documents不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '异步写入失败: %', SQLERRM;
END $$;
```

-- I/O 操作异步执行，不阻塞主线程

#### 5.2.3 最佳实践

**最佳实践**:

1. **批量插入**: 使用批量插入，充分利用异步 I/O
2. **事务管理**: 合理使用事务，减少提交次数
3. **连接池**: 使用连接池，提高并发写入能力

### 5.3 批量写入示例

#### 5.3.1 Python 批量插入

**批量插入示例**:

```python
import psycopg2
from psycopg2.extras import execute_values
import json

# 连接到 PostgreSQL 18
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="postgres",
    database="test_db"
)

cur = conn.cursor()

# 准备批量数据
documents = [
    {
        "title": f"Document {i}",
        "body": f"Content {i}",
        "metadata": {"id": i, "category": "test"}
    }
    for i in range(10000)
]

# 批量插入（PostgreSQL 18 自动使用异步 I/O）
execute_values(
    cur,
    """
    INSERT INTO documents (content, metadata)
    VALUES %s
    """,
    [
        (json.dumps(doc), json.dumps(doc["metadata"]))
        for doc in documents
    ]
)

conn.commit()
print("✅ 批量插入完成（异步 I/O 加速）")
```

#### 5.3.2 性能优化技巧

**优化技巧**:

| 技巧         | 说明                    | 性能提升  |
| ------------ | ----------------------- | --------- |
| **批量大小** | 建议批量大小 1000-10000 | **+50%**  |
| **并发写入** | 使用多线程并发写入      | **+200%** |
| **连接池**   | 使用连接池复用连接      | **+30%**  |

#### 5.3.3 错误处理

**错误处理**:

```python
try:
    execute_values(cur, sql, data)
    conn.commit()
except psycopg2.Error as e:
    conn.rollback()
    print(f"❌ 插入失败: {e}")
    raise
```

### 5.4 事务管理优化

#### 5.4.1 事务大小控制

**事务大小建议**：

```sql
-- ✅ 推荐：合理的事务大小（1000-10000条）
BEGIN;
INSERT INTO documents (content, metadata)
SELECT
    jsonb_build_object('id', i, 'data', repeat('x', 1000)),
    jsonb_build_object('batch', 1)
FROM generate_series(1, 5000) i;
COMMIT;

-- ❌ 不推荐：过大的事务（可能导致锁竞争）
BEGIN;
INSERT INTO documents (content, metadata)
SELECT
    jsonb_build_object('id', i, 'data', repeat('x', 1000)),
    jsonb_build_object('batch', 1)
FROM generate_series(1, 1000000) i;  -- 太大
COMMIT;
```

**事务性能对比**：

| 事务大小 | 性能 | 锁竞争风险 | 推荐度 |
|---------|------|-----------|--------|
| **<100条** | 基准 | 低 | ⭐⭐ |
| **1000条** | +50% | 低 | ⭐⭐⭐⭐ |
| **10000条** | +100% | 中 | ⭐⭐⭐⭐⭐ |
| **>100000条** | +150% | 高 | ⭐⭐ |

#### 5.4.2 并发事务管理

**并发事务配置**：

```sql
-- 配置最大连接数
ALTER SYSTEM SET max_connections = 500;

-- 配置工作内存（影响并发事务性能）
ALTER SYSTEM SET work_mem = '64MB';

-- 配置维护工作内存
ALTER SYSTEM SET maintenance_work_mem = '1GB';
```

**并发事务示例**：

```python
import asyncio
import asyncpg

async def concurrent_transactions():
    # 创建连接池
    pool = await asyncpg.create_pool(
        host='localhost',
        database='testdb',
        min_size=10,
        max_size=50
    )

    async def execute_transaction(conn_id):
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO documents (content, metadata)
                    VALUES ($1, $2)
                    """,
                    json.dumps({'id': conn_id}),
                    json.dumps({'batch': conn_id})
                )

    # 并发执行多个事务
    tasks = [execute_transaction(i) for i in range(100)]
    await asyncio.gather(*tasks)
```

### 5.5 连接池配置

#### 5.5.1 连接池大小

**连接池配置建议**：

| 应用类型 | 连接池大小 | 说明 |
|---------|-----------|------|
| **小型应用** | 10-20 | 低并发场景 |
| **中型应用** | 20-50 | 中等并发场景 |
| **大型应用** | 50-100 | 高并发场景 |
| **超大型应用** | 100-200 | 超高并发场景 |

**PgBouncer配置示例**：

```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 100
min_pool_size = 10
reserve_pool_size = 5
```

#### 5.5.2 连接池监控

**监控连接池使用情况**：

```sql
-- 查看当前连接数
SELECT
    COUNT(*) AS total_connections,
    COUNT(*) FILTER (WHERE state = 'active') AS active_connections,
    COUNT(*) FILTER (WHERE state = 'idle') AS idle_connections,
    (SELECT setting FROM pg_settings WHERE name = 'max_connections') AS max_connections
FROM pg_stat_activity
WHERE datname = current_database();

-- 查看连接等待情况
SELECT
    wait_event_type,
    wait_event,
    COUNT(*) AS wait_count
FROM pg_stat_activity
WHERE wait_event_type IS NOT NULL
GROUP BY wait_event_type, wait_event
ORDER BY wait_count DESC;
```

### 5.6 错误处理和重试

#### 5.6.1 错误处理策略

**错误处理示例**：

```python
import psycopg2
from psycopg2 import errors
import time

def insert_with_retry(conn, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO documents (content, metadata) VALUES (%s, %s)",
                (data['content'], data['metadata'])
            )
            conn.commit()
            return True
        except errors.DeadlockDetected:
            if attempt < max_retries - 1:
                time.sleep(0.1 * (2 ** attempt))  # 指数退避
                continue
            else:
                raise
        except errors.UniqueViolation:
            # 唯一约束冲突，不需要重试
            conn.rollback()
            return False
        except Exception as e:
            conn.rollback()
            raise
    return False
```

#### 5.6.2 批量操作错误处理

**批量操作错误处理**：

```python
def batch_insert_with_error_handling(conn, data_list):
    successful = []
    failed = []

    for data in data_list:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO documents (content, metadata) VALUES (%s, %s)",
                (data['content'], data['metadata'])
            )
            conn.commit()
            successful.append(data)
        except Exception as e:
            conn.rollback()
            failed.append({'data': data, 'error': str(e)})

    return successful, failed
```

---

**返回**: [文档首页](../README.md) | [上一章节](../04-架构设计/README.md) | [下一章节](../06-性能分析/README.md)
