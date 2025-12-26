# PostgreSQL性能调优完整指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级

---

## 📋 目录

- [PostgreSQL性能调优完整指南](#postgresql性能调优完整指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 性能调优目标](#11-性能调优目标)
    - [1.2 性能调优层次](#12-性能调优层次)
  - [2. 性能调优体系](#2-性能调优体系)
    - [2.1 调优流程](#21-调优流程)
    - [2.2 调优策略](#22-调优策略)
  - [3. 系统级调优](#3-系统级调优)
    - [3.1 操作系统参数](#31-操作系统参数)
    - [3.2 硬件优化](#32-硬件优化)
  - [4. 数据库级调优](#4-数据库级调优)
    - [4.1 内存配置](#41-内存配置)
    - [4.2 连接配置](#42-连接配置)
    - [4.3 并发控制](#43-并发控制)
  - [5. 查询级调优](#5-查询级调优)
    - [5.1 SQL优化](#51-sql优化)
    - [5.2 执行计划分析](#52-执行计划分析)
    - [5.3 查询重写](#53-查询重写)
  - [6. 索引调优](#6-索引调优)
    - [6.1 索引类型选择](#61-索引类型选择)
    - [6.2 索引设计原则](#62-索引设计原则)
    - [6.3 索引维护](#63-索引维护)
  - [7. 参数调优](#7-参数调优)
    - [7.1 关键参数](#71-关键参数)
    - [7.2 日志配置](#72-日志配置)
  - [8. 性能监控](#8-性能监控)
    - [8.1 系统监控](#81-系统监控)
    - [8.2 查询监控](#82-查询监控)
    - [8.3 慢查询分析](#83-慢查询分析)
  - [9. 最佳实践](#9-最佳实践)
    - [✅ 推荐做法](#-推荐做法)
    - [❌ 避免做法](#-避免做法)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

PostgreSQL性能调优是一个系统化的过程，涉及多个层面的优化。本指南提供完整的性能调优方案。

### 1.1 性能调优目标

- **提升查询性能** - 减少查询响应时间
- **提高吞吐量** - 增加QPS/TPS
- **优化资源使用** - 降低CPU、内存、I/O使用
- **降低成本** - 减少硬件和云资源成本

### 1.2 性能调优层次

```text
系统级调优
  ↓
数据库级调优
  ↓
查询级调优
  ↓
索引调优
  ↓
参数调优
```

---

## 2. 性能调优体系

### 2.1 调优流程

1. **性能诊断** - 识别性能瓶颈
2. **问题分析** - 分析根本原因
3. **优化方案** - 制定优化策略
4. **实施优化** - 执行优化措施
5. **效果验证** - 验证优化效果

### 2.2 调优策略

- **配置调优** - 调整数据库配置参数
- **查询优化** - 优化SQL查询语句
- **索引优化** - 优化索引设计和维护
- **架构优化** - 优化数据库架构设计

---

## 3. 系统级调优

### 3.1 操作系统参数

```bash
# 共享内存设置
# /etc/sysctl.conf
kernel.shmmax = 68719476736
kernel.shmall = 16777216

# 文件描述符限制
# /etc/security/limits.conf
postgres soft nofile 65536
postgres hard nofile 65536
```

### 3.2 硬件优化

- **CPU** - 多核CPU，支持并行查询
- **内存** - 足够的内存用于缓存
- **存储** - SSD存储，提升I/O性能
- **网络** - 低延迟网络

---

## 4. 数据库级调优

### 4.1 内存配置

**内存配置参数（配置文件示例）**:

```sql
-- postgresql.conf
shared_buffers = 8GB              -- 共享内存缓冲区（建议为总内存的25%）
effective_cache_size = 24GB      -- 有效缓存大小（建议为总内存的50-75%）
work_mem = 256MB                  -- 工作内存（用于排序、哈希等）
maintenance_work_mem = 2GB        -- 维护工作内存（用于VACUUM、CREATE INDEX等）
```

**动态设置内存参数（带错误处理）**:

```sql
-- 动态设置内存参数（带错误处理）
DO $$
BEGIN
    -- 检查PostgreSQL版本
    IF current_setting('server_version_num')::INT < 120000 THEN
        RAISE EXCEPTION '动态设置参数需要PostgreSQL 12+';
    END IF;

    -- 设置shared_buffers（需要重启）
    ALTER SYSTEM SET shared_buffers = '8GB';
    RAISE NOTICE 'shared_buffers已设置为8GB（需要重启生效）';

    -- 设置work_mem（立即生效）
    SET work_mem = '256MB';
    RAISE NOTICE 'work_mem已设置为256MB（立即生效）';

    -- 设置maintenance_work_mem（立即生效）
    SET maintenance_work_mem = '2GB';
    RAISE NOTICE 'maintenance_work_mem已设置为2GB（立即生效）';
EXCEPTION
    WHEN feature_not_supported THEN
        RAISE WARNING '动态设置参数需要PostgreSQL 12+';
    WHEN OTHERS THEN
        RAISE EXCEPTION '设置内存参数失败: %', SQLERRM;
END $$;
```

### 4.2 连接配置

**连接配置参数（配置文件示例）**:

```sql
-- 连接数配置
max_connections = 200              -- 最大连接数
superuser_reserved_connections = 3  -- 超级用户保留连接数

-- 连接池（推荐使用PgBouncer或PgPool-II）
```

**动态设置连接参数（带错误处理）**:

```sql
-- 动态设置连接参数（带错误处理）
DO $$
DECLARE
    current_max_conn INT;
BEGIN
    -- 获取当前最大连接数
    SELECT current_setting('max_connections')::INT INTO current_max_conn;

    IF current_max_conn < 100 THEN
        RAISE WARNING '当前max_connections=%，建议至少100', current_max_conn;
    END IF;

    -- 设置max_connections（需要重启）
    ALTER SYSTEM SET max_connections = 200;
    RAISE NOTICE 'max_connections已设置为200（需要重启生效）';

    -- 设置superuser_reserved_connections（需要重启）
    ALTER SYSTEM SET superuser_reserved_connections = 3;
    RAISE NOTICE 'superuser_reserved_connections已设置为3（需要重启生效）';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '设置连接参数失败: %', SQLERRM;
END $$;
```

### 4.3 并发控制

**并发控制参数（配置文件示例）**:

```sql
-- 并发控制参数
max_worker_processes = 8           -- 最大工作进程数
max_parallel_workers_per_gather = 4 -- 每个查询的最大并行工作进程数
max_parallel_workers = 8          -- 最大并行工作进程数
```

**动态设置并发参数（带错误处理）**:

```sql
-- 动态设置并发参数（带错误处理）
DO $$
DECLARE
    cpu_count INT;
    current_max_workers INT;
BEGIN
    -- 获取CPU核心数（估算）
    SELECT setting::INT INTO cpu_count FROM pg_settings WHERE name = 'max_worker_processes';

    -- 获取当前最大并行工作进程数
    SELECT current_setting('max_parallel_workers')::INT INTO current_max_workers;

    IF current_max_workers > cpu_count THEN
        RAISE WARNING 'max_parallel_workers (%) 大于CPU核心数 (%)', current_max_workers, cpu_count;
    END IF;

    -- 设置max_parallel_workers_per_gather（立即生效）
    SET max_parallel_workers_per_gather = 4;
    RAISE NOTICE 'max_parallel_workers_per_gather已设置为4（立即生效）';

    -- 设置max_parallel_workers（需要重启）
    ALTER SYSTEM SET max_parallel_workers = 8;
    RAISE NOTICE 'max_parallel_workers已设置为8（需要重启生效）';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '设置并发参数失败: %', SQLERRM;
END $$;
```

---

## 5. 查询级调优

### 5.1 SQL优化

**SQL优化对比（带性能测试）**:

```sql
-- ✅ 推荐：使用索引（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE id = 123;
-- 执行时间: 快（使用索引）
-- 计划: Index Scan

-- ❌ 避免：全表扫描（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE name LIKE '%test%';
-- 执行时间: 慢（全表扫描）
-- 计划: Seq Scan

-- ✅ 推荐：使用LIMIT（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20;
-- 执行时间: 快（只返回20条）
-- 计划: Limit -> Sort -> Index Scan

-- ❌ 避免：返回大量数据（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM orders ORDER BY created_at DESC;
-- 执行时间: 慢（返回所有数据）
-- 计划: Sort -> Seq Scan
```

### 5.2 执行计划分析

**执行计划分析（带完整错误处理和性能测试）**:

```sql
-- 分析查询计划（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    -- 检查列是否存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'orders' AND column_name = 'customer_id'
    ) THEN
        RAISE EXCEPTION '列不存在: customer_id';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'orders' AND column_name = 'order_date'
    ) THEN
        RAISE EXCEPTION '列不存在: order_date';
    END IF;

    RAISE NOTICE '开始分析查询计划';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: orders';
    WHEN undefined_column THEN
        RAISE EXCEPTION '列不存在（请检查customer_id和order_date列）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询计划分析准备失败: %', SQLERRM;
END $$;

-- 性能测试：分析查询计划
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM orders
WHERE customer_id = 123
  AND order_date >= '2024-01-01';
-- 执行时间: 取决于表大小和索引
-- 计划: Bitmap Heap Scan -> Bitmap Index Scan（如果索引存在）
-- 或: Seq Scan（如果索引不存在）

-- 检查是否使用了索引
-- 检查是否有顺序扫描（Seq Scan）
-- 检查是否有索引扫描（Index Scan）
```

### 5.3 查询重写

**查询重写对比（带性能测试）**:

```sql
-- 使用EXISTS代替IN（对于大表）
-- ❌ 不推荐：使用IN（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);
-- 执行时间: 可能较慢（需要物化子查询结果）
-- 计划: Hash Join 或 Nested Loop

-- ✅ 推荐：使用EXISTS（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE EXISTS (SELECT 1 FROM orders WHERE orders.user_id = users.id);
-- 执行时间: 通常更快（不需要物化）
-- 计划: Hash Semi Join 或 Nested Loop Semi Join

-- 查询重写验证（带错误处理）
DO $$
DECLARE
    in_count BIGINT;
    exists_count BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION '表不存在: users';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    -- IN查询结果数
    SELECT COUNT(*) INTO in_count
    FROM users WHERE id IN (SELECT user_id FROM orders);

    -- EXISTS查询结果数
    SELECT COUNT(*) INTO exists_count
    FROM users WHERE EXISTS (SELECT 1 FROM orders WHERE orders.user_id = users.id);

    IF in_count != exists_count THEN
        RAISE WARNING '查询结果不一致: IN=% vs EXISTS=%', in_count, exists_count;
    ELSE
        RAISE NOTICE '查询结果一致: %', in_count;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查users和orders表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询重写验证失败: %', SQLERRM;
END $$;
```

---

## 6. 索引调优

### 6.1 索引类型选择

| 索引类型 | 适用场景 | 优势 | 劣势 |
| --- | --- | --- | --- |
| **B-tree** | 大多数场景 | 通用、高效 | 不适合模糊查询 |
| **Hash** | 等值查询 | 等值查询快 | 不支持范围查询 |
| **GIN** | 全文搜索、数组 | 多值查询 | 更新慢 |
| **GiST** | 空间数据、全文搜索 | 灵活 | 查询较慢 |
| **BRIN** | 大表、时序数据 | 索引小 | 查询性能一般 |

### 6.2 索引设计原则

**索引设计（带完整错误处理）**:

```sql
-- 1. 为经常查询的列创建索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'orders' AND indexname = 'idx_orders_customer_id'
    ) THEN
        RAISE WARNING '索引已存在: idx_orders_customer_id';
    ELSE
        CREATE INDEX idx_orders_customer_id ON orders (customer_id);
        RAISE NOTICE '索引创建成功: idx_orders_customer_id';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: orders';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在: idx_orders_customer_id';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;

-- 2. 为WHERE子句中的列创建索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'orders' AND indexname = 'idx_orders_date'
    ) THEN
        RAISE WARNING '索引已存在: idx_orders_date';
    ELSE
        CREATE INDEX idx_orders_date ON orders (order_date);
        RAISE NOTICE '索引创建成功: idx_orders_date';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: orders';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在: idx_orders_date';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;

-- 3. 为JOIN条件创建索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'orders' AND indexname = 'idx_orders_user_id'
    ) THEN
        RAISE WARNING '索引已存在: idx_orders_user_id';
    ELSE
        CREATE INDEX idx_orders_user_id ON orders (user_id);
        RAISE NOTICE '索引创建成功: idx_orders_user_id';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: orders';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在: idx_orders_user_id';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;

-- 4. 使用复合索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    -- 检查列是否存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'orders' AND column_name = 'customer_id'
    ) THEN
        RAISE EXCEPTION '列不存在: customer_id';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'orders' AND column_name = 'order_date'
    ) THEN
        RAISE EXCEPTION '列不存在: order_date';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'orders' AND indexname = 'idx_orders_customer_date'
    ) THEN
        RAISE WARNING '索引已存在: idx_orders_customer_date';
    ELSE
        CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);
        RAISE NOTICE '复合索引创建成功: idx_orders_customer_date';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: orders';
    WHEN undefined_column THEN
        RAISE EXCEPTION '列不存在（请检查customer_id和order_date列）';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在: idx_orders_customer_date';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建复合索引失败: %', SQLERRM;
END $$;

-- 5. 使用部分索引（只索引部分数据，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    -- 检查列是否存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'orders' AND column_name = 'order_date'
    ) THEN
        RAISE EXCEPTION '列不存在: order_date';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'orders' AND column_name = 'status'
    ) THEN
        RAISE EXCEPTION '列不存在: status';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'orders' AND indexname = 'idx_orders_active'
    ) THEN
        RAISE WARNING '索引已存在: idx_orders_active';
    ELSE
        CREATE INDEX idx_orders_active ON orders (order_date)
        WHERE status = 'active';
        RAISE NOTICE '部分索引创建成功: idx_orders_active';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: orders';
    WHEN undefined_column THEN
        RAISE EXCEPTION '列不存在（请检查order_date和status列）';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在: idx_orders_active';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建部分索引失败: %', SQLERRM;
END $$;

-- 性能测试：索引使用情况
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM orders WHERE customer_id = 123 AND order_date >= '2024-01-01';
-- 执行时间: 取决于表大小和索引
-- 计划: Index Scan（使用复合索引idx_orders_customer_date）
```

### 6.3 索引维护

**索引维护（带完整错误处理）**:

```sql
-- 定期VACUUM（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    VACUUM ANALYZE orders;
    RAISE NOTICE 'VACUUM ANALYZE执行成功: orders';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: orders';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'VACUUM ANALYZE失败: %', SQLERRM;
END $$;

-- 重建索引（如果索引膨胀，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'orders' AND indexname = 'idx_orders_customer_id'
    ) THEN
        RAISE EXCEPTION '索引不存在: idx_orders_customer_id';
    END IF;

    REINDEX INDEX idx_orders_customer_id;
    RAISE NOTICE '索引重建成功: idx_orders_customer_id';
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '索引不存在: idx_orders_customer_id';
    WHEN OTHERS THEN
        RAISE EXCEPTION '重建索引失败: %', SQLERRM;
END $$;

-- 查看索引使用情况（带错误处理和性能测试）
DO $$
DECLARE
    index_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    SELECT COUNT(*) INTO index_count
    FROM pg_stat_user_indexes
    WHERE tablename = 'orders';

    IF index_count = 0 THEN
        RAISE WARNING '表orders没有索引或索引统计信息不存在';
    ELSE
        RAISE NOTICE '找到 % 个索引的统计信息', index_count;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: orders';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查看索引使用情况失败: %', SQLERRM;
END $$;

-- 性能测试：查看索引使用情况
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
WHERE tablename = 'orders'
ORDER BY idx_scan DESC;
-- 执行时间: <10ms
-- 计划: Seq Scan
```

---

## 7. 参数调优

### 7.1 关键参数

**查询规划器参数（配置文件示例）**:

```sql
-- 查询规划器参数
random_page_cost = 1.1            -- 随机页面成本（SSD建议1.1，HDD建议4.0）
effective_io_concurrency = 200   -- 有效I/O并发数（SSD建议200）

-- 自动清理参数
autovacuum = on                  -- 启用自动清理
autovacuum_max_workers = 3        -- 自动清理最大工作进程数
autovacuum_naptime = 1min        -- 自动清理检查间隔
```

**动态设置查询规划器参数（带错误处理）**:

```sql
-- 动态设置查询规划器参数（带错误处理）
DO $$
DECLARE
    storage_type TEXT;
BEGIN
    -- 检测存储类型（简化示例，实际需要根据硬件配置）
    -- 假设SSD存储
    storage_type := 'SSD';

    IF storage_type = 'SSD' THEN
        -- SSD存储优化
        ALTER SYSTEM SET random_page_cost = 1.1;
        ALTER SYSTEM SET effective_io_concurrency = 200;
        RAISE NOTICE '已设置为SSD优化参数（random_page_cost=1.1, effective_io_concurrency=200）';
    ELSIF storage_type = 'HDD' THEN
        -- HDD存储优化
        ALTER SYSTEM SET random_page_cost = 4.0;
        ALTER SYSTEM SET effective_io_concurrency = 2;
        RAISE NOTICE '已设置为HDD优化参数（random_page_cost=4.0, effective_io_concurrency=2）';
    END IF;

    -- 设置自动清理参数（需要重启）
    ALTER SYSTEM SET autovacuum = on;
    ALTER SYSTEM SET autovacuum_max_workers = 3;
    ALTER SYSTEM SET autovacuum_naptime = '1min';
    RAISE NOTICE '自动清理参数已设置（需要重启生效）';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '设置查询规划器参数失败: %', SQLERRM;
END $$;
```

### 7.2 日志配置

**日志配置参数（配置文件示例）**:

```sql
-- 慢查询日志
log_min_duration_statement = 1000  -- 记录执行时间>1秒的查询

-- 查询日志
log_statement = 'ddl'              -- 记录DDL语句
log_connections = on               -- 记录连接
log_disconnections = on            -- 记录断开
```

**动态设置日志配置（带错误处理）**:

```sql
-- 动态设置日志配置（带错误处理）
DO $$
BEGIN
    -- 设置慢查询日志（立即生效）
    SET log_min_duration_statement = 1000;
    RAISE NOTICE '慢查询日志已启用（记录执行时间>1秒的查询）';

    -- 设置查询日志（立即生效）
    SET log_statement = 'ddl';
    RAISE NOTICE '查询日志已设置为记录DDL语句';

    -- 设置连接日志（需要重启）
    ALTER SYSTEM SET log_connections = on;
    ALTER SYSTEM SET log_disconnections = on;
    RAISE NOTICE '连接日志已启用（需要重启生效）';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '设置日志配置失败: %', SQLERRM;
END $$;
```

---

## 8. 性能监控

### 8.1 系统监控

**系统监控（带完整错误处理）**:

```sql
-- 查看数据库大小（带错误处理）
DO $$
DECLARE
    db_size TEXT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'mydb') THEN
        RAISE EXCEPTION '数据库不存在: mydb';
    END IF;

    SELECT pg_size_pretty(pg_database_size('mydb')) INTO db_size;
    RAISE NOTICE '数据库大小: %', db_size;
EXCEPTION
    WHEN undefined_database THEN
        RAISE EXCEPTION '数据库不存在: mydb';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询数据库大小失败: %', SQLERRM;
END $$;

-- 性能测试：查看数据库大小
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT pg_size_pretty(pg_database_size('mydb'));
-- 执行时间: <10ms
-- 计划: Result

-- 查看表大小（带错误处理）
DO $$
DECLARE
    table_count INT;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM pg_tables
    WHERE schemaname = 'public';

    IF table_count = 0 THEN
        RAISE WARNING 'public模式下没有表';
    ELSE
        RAISE NOTICE '找到 % 个表', table_count;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询表大小失败: %', SQLERRM;
END $$;

-- 性能测试：查看表大小
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
-- 执行时间: 取决于表数量
-- 计划: Sort -> Seq Scan
```

### 8.2 查询监控

**查询监控（带完整错误处理和性能测试）**:

```sql
-- 查看当前活动查询（带错误处理）
DO $$
DECLARE
    active_query_count INT;
BEGIN
    SELECT COUNT(*) INTO active_query_count
    FROM pg_stat_activity
    WHERE state = 'active';

    IF active_query_count = 0 THEN
        RAISE NOTICE '当前没有活动查询';
    ELSE
        RAISE NOTICE '当前有 % 个活动查询', active_query_count;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询活动查询失败: %', SQLERRM;
END $$;

-- 性能测试：查看当前活动查询
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pid,
    usename,
    application_name,
    state,
    query,
    query_start,
    now() - query_start AS duration
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;
-- 执行时间: <10ms
-- 计划: Sort -> Seq Scan
```

### 8.3 慢查询分析

**慢查询分析（带完整错误处理）**:

```sql
-- 使用pg_stat_statements扩展（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
        CREATE EXTENSION pg_stat_statements;
        RAISE NOTICE 'pg_stat_statements扩展已创建';
    ELSE
        RAISE NOTICE 'pg_stat_statements扩展已存在';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'pg_stat_statements扩展文件未找到（需要安装pg_stat_statements扩展）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装pg_stat_statements扩展失败: %', SQLERRM;
END $$;

-- 查看最慢的查询（带错误处理和性能测试）
DO $$
DECLARE
    slow_query_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
        RAISE EXCEPTION 'pg_stat_statements扩展未安装';
    END IF;

    SELECT COUNT(*) INTO slow_query_count
    FROM pg_stat_statements
    WHERE mean_exec_time > 1000;  -- 平均执行时间>1秒的查询

    IF slow_query_count = 0 THEN
        RAISE NOTICE '未找到慢查询（平均执行时间>1秒）';
    ELSE
        RAISE NOTICE '找到 % 个慢查询', slow_query_count;
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION 'pg_stat_statements扩展未安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询慢查询失败: %', SQLERRM;
END $$;

-- 性能测试：查看最慢的查询
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
-- 执行时间: <10ms
-- 计划: Limit -> Sort -> Seq Scan
```

---

## 9. 最佳实践

### ✅ 推荐做法

1. **系统化调优** - 按照系统级→数据库级→查询级的顺序调优
2. **监控优先** - 先监控再调优，用数据说话
3. **索引优化** - 为常用查询创建合适的索引
4. **查询优化** - 优化SQL查询语句
5. **参数调优** - 根据硬件和工作负载调整参数

### ❌ 避免做法

1. **盲目调优** - 不分析问题就调优
2. **过度索引** - 索引过多会影响写入性能
3. **忽略监控** - 不监控就不知道优化效果
4. **参数随意调整** - 参数调整需要根据实际情况

---

## 📚 相关文档

- [性能调优体系详解.md](./性能调优体系详解.md) - 性能调优体系详解
- [性能调优深入.md](./性能调优深入.md) - 性能调优深入指南
- [【案例集】PostgreSQL慢查询优化完整实战手册.md](./【案例集】PostgreSQL慢查询优化完整实战手册.md) - 慢查询优化实战
- [02-查询与优化/README.md](../README.md) - 查询与优化主题

---

**最后更新**: 2025年1月
