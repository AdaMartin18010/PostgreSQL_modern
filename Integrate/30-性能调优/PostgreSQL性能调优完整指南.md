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
#!/bin/bash
# 系统参数配置（带错误处理）
set -e
set -u

error_exit() {
    echo "错误: $1" >&2
    exit 1
}

# 检查是否有root权限
if [ "$EUID" -ne 0 ]; then
    error_exit "此脚本需要root权限运行"
fi

# 配置共享内存设置
SYSCTL_FILE="/etc/sysctl.conf"
if [ ! -f "$SYSCTL_FILE" ]; then
    error_exit "sysctl配置文件不存在: $SYSCTL_FILE"
fi

# 备份配置文件
cp "$SYSCTL_FILE" "${SYSCTL_FILE}.backup.$(date +%Y%m%d_%H%M%S)" || error_exit "备份配置文件失败"

# 添加共享内存设置（如果不存在）
if ! grep -q "kernel.shmmax" "$SYSCTL_FILE"; then
    echo "kernel.shmmax = 68719476736" >> "$SYSCTL_FILE"
    echo "kernel.shmall = 16777216" >> "$SYSCTL_FILE"
    echo "共享内存设置已添加到 $SYSCTL_FILE"
else
    echo "共享内存设置已存在，跳过"
fi

# 应用sysctl设置
sysctl -p || error_exit "应用sysctl设置失败"

# 文件描述符限制配置
LIMITS_FILE="/etc/security/limits.conf"
if [ ! -f "$LIMITS_FILE" ]; then
    error_exit "limits配置文件不存在: $LIMITS_FILE"
fi

# 备份配置文件
cp "$LIMITS_FILE" "${LIMITS_FILE}.backup.$(date +%Y%m%d_%H%M%S)" || error_exit "备份配置文件失败"

# 添加文件描述符限制（如果不存在）
if ! grep -q "postgres.*nofile" "$LIMITS_FILE"; then
    echo "postgres soft nofile 65536" >> "$LIMITS_FILE"
    echo "postgres hard nofile 65536" >> "$LIMITS_FILE"
    echo "文件描述符限制已添加到 $LIMITS_FILE"
else
    echo "文件描述符限制已存在，跳过"
fi

echo "系统参数配置完成"
```

### 3.2 硬件优化

- **CPU** - 多核CPU，支持并行查询
- **内存** - 足够的内存用于缓存
- **存储** - SSD存储，提升I/O性能
- **网络** - 低延迟网络

---

## 4. 数据库级调优

### 4.1 内存配置

```sql
-- 内存配置（postgresql.conf，带验证）
-- 注意：这些是配置参数示例，实际修改需要使用 ALTER SYSTEM 或在 postgresql.conf 中修改

-- 验证当前内存配置（带错误处理）
DO $$
DECLARE
    shared_buffers_setting TEXT;
    effective_cache_size_setting TEXT;
    work_mem_setting TEXT;
    maintenance_work_mem_setting TEXT;
BEGIN
    BEGIN
        -- 查询当前配置
        SELECT setting INTO shared_buffers_setting
        FROM pg_settings WHERE name = 'shared_buffers';

        SELECT setting INTO effective_cache_size_setting
        FROM pg_settings WHERE name = 'effective_cache_size';

        SELECT setting INTO work_mem_setting
        FROM pg_settings WHERE name = 'work_mem';

        SELECT setting INTO maintenance_work_mem_setting
        FROM pg_settings WHERE name = 'maintenance_work_mem';

        RAISE NOTICE '当前内存配置:';
        RAISE NOTICE '  shared_buffers: %', shared_buffers_setting;
        RAISE NOTICE '  effective_cache_size: %', effective_cache_size_setting;
        RAISE NOTICE '  work_mem: %', work_mem_setting;
        RAISE NOTICE '  maintenance_work_mem: %', maintenance_work_mem_setting;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询内存配置失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 推荐的配置值（根据总内存调整）:
-- shared_buffers = 8GB              -- 共享内存缓冲区（建议为总内存的25%）
-- effective_cache_size = 24GB      -- 有效缓存大小（建议为总内存的50-75%）
-- work_mem = 256MB                  -- 工作内存（用于排序、哈希等）
-- maintenance_work_mem = 2GB        -- 维护工作内存（用于VACUUM、CREATE INDEX等）
```

### 4.2 连接配置

```sql
-- 连接数配置验证（带错误处理）
DO $$
DECLARE
    max_conn_setting INT;
    superuser_reserved_setting INT;
    current_conn_count INT;
BEGIN
    BEGIN
        SELECT setting::INT INTO max_conn_setting
        FROM pg_settings WHERE name = 'max_connections';

        SELECT setting::INT INTO superuser_reserved_setting
        FROM pg_settings WHERE name = 'superuser_reserved_connections';

        SELECT COUNT(*) INTO current_conn_count
        FROM pg_stat_activity;

        RAISE NOTICE '连接配置:';
        RAISE NOTICE '  最大连接数: %', max_conn_setting;
        RAISE NOTICE '  超级用户保留连接数: %', superuser_reserved_setting;
        RAISE NOTICE '  当前连接数: %', current_conn_count;
        RAISE NOTICE '  可用连接数: %', max_conn_setting - current_conn_count - superuser_reserved_setting;

        IF current_conn_count > max_conn_setting * 0.8 THEN
            RAISE WARNING '当前连接数已超过最大连接数的80%%，建议考虑使用连接池';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询连接配置失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 推荐的配置值:
-- max_connections = 200              -- 最大连接数
-- superuser_reserved_connections = 3  -- 超级用户保留连接数
-- 注意：连接池（推荐使用PgBouncer或PgPool-II）可以更好地管理连接
```

### 4.3 并发控制

```sql
-- 并发控制参数验证（带错误处理）
DO $$
DECLARE
    max_worker_setting INT;
    max_parallel_per_gather_setting INT;
    max_parallel_workers_setting INT;
BEGIN
    BEGIN
        SELECT setting::INT INTO max_worker_setting
        FROM pg_settings WHERE name = 'max_worker_processes';

        SELECT setting::INT INTO max_parallel_per_gather_setting
        FROM pg_settings WHERE name = 'max_parallel_workers_per_gather';

        SELECT setting::INT INTO max_parallel_workers_setting
        FROM pg_settings WHERE name = 'max_parallel_workers';

        RAISE NOTICE '并发控制配置:';
        RAISE NOTICE '  max_worker_processes: %', max_worker_setting;
        RAISE NOTICE '  max_parallel_workers_per_gather: %', max_parallel_per_gather_setting;
        RAISE NOTICE '  max_parallel_workers: %', max_parallel_workers_setting;

        IF max_parallel_workers_setting > max_worker_setting THEN
            RAISE WARNING 'max_parallel_workers 不应大于 max_worker_processes';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询并发控制配置失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 推荐的配置值:
-- max_worker_processes = 8           -- 最大工作进程数
-- max_parallel_workers_per_gather = 4 -- 每个查询的最大并行工作进程数
-- max_parallel_workers = 8          -- 最大并行工作进程数
```

---

## 5. 查询级调优

### 5.1 SQL优化

```sql
-- ✅ 推荐：使用索引（带性能测试）
EXPLAIN ANALYZE
SELECT * FROM users WHERE id = 123;

-- ❌ 避免：全表扫描（带性能测试，展示问题）
EXPLAIN ANALYZE
SELECT * FROM users WHERE name LIKE '%test%';
-- 注意：此查询会导致全表扫描，性能较差

-- ✅ 推荐：使用LIMIT（带性能测试）
EXPLAIN ANALYZE
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20;

-- ❌ 避免：返回大量数据（带性能测试，展示问题）
EXPLAIN ANALYZE
SELECT * FROM orders ORDER BY created_at DESC;
-- 注意：此查询返回所有数据，可能导致性能问题
```

### 5.2 执行计划分析

```sql
-- 分析查询计划（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法分析查询计划';
            RETURN;
        END IF;

        RAISE NOTICE '开始分析查询计划...';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询计划分析准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 执行查询计划分析
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM orders
WHERE customer_id = 123
  AND order_date >= '2024-01-01';

-- 检查要点:
-- 1. 检查是否使用了索引（Index Scan / Index Only Scan）
-- 2. 检查是否有顺序扫描（Seq Scan，可能需要优化）
-- 3. 检查执行时间和缓冲区使用情况
-- 4. 检查是否有排序操作（Sort）
-- 5. 检查是否有并行执行（Parallel Seq Scan / Parallel Index Scan）
```

### 5.3 查询重写

```sql
-- 使用EXISTS代替IN（对于大表，带性能对比）
-- ❌ 不推荐：使用IN（带性能测试）
EXPLAIN ANALYZE
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);
-- 注意：IN子查询可能执行效率较低，特别是对于大表

-- ✅ 推荐：使用EXISTS（带性能测试）
EXPLAIN ANALYZE
SELECT * FROM users WHERE EXISTS (SELECT 1 FROM orders WHERE orders.user_id = users.id);
-- 注意：EXISTS通常在大多数情况下性能更好，因为它可以提前终止搜索
```

---

## 6. 索引调优

### 6.1 索引类型选择

| 索引类型 | 适用场景 | 优势 | 劣势 |
|---------|---------|------|------|
| **B-tree** | 大多数场景 | 通用、高效 | 不适合模糊查询 |
| **Hash** | 等值查询 | 等值查询快 | 不支持范围查询 |
| **GIN** | 全文搜索、数组 | 多值查询 | 更新慢 |
| **GiST** | 空间数据、全文搜索 | 灵活 | 查询较慢 |
| **BRIN** | 大表、时序数据 | 索引小 | 查询性能一般 |

### 6.2 索引设计原则

```sql
-- 1. 为经常查询的列创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_orders_customer_id') THEN
            RAISE NOTICE '索引 idx_orders_customer_id 已存在';
        ELSE
            CREATE INDEX idx_orders_customer_id ON orders (customer_id);
            RAISE NOTICE '索引 idx_orders_customer_id 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '索引 idx_orders_customer_id 已存在';
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 2. 为WHERE子句中的列创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_orders_date') THEN
            RAISE NOTICE '索引 idx_orders_date 已存在';
        ELSE
            CREATE INDEX idx_orders_date ON orders (order_date);
            RAISE NOTICE '索引 idx_orders_date 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '索引 idx_orders_date 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 3. 为JOIN条件创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_orders_user_id') THEN
            RAISE NOTICE '索引 idx_orders_user_id 已存在';
        ELSE
            CREATE INDEX idx_orders_user_id ON orders (user_id);
            RAISE NOTICE '索引 idx_orders_user_id 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '索引 idx_orders_user_id 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 4. 使用复合索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_orders_customer_date') THEN
            RAISE NOTICE '索引 idx_orders_customer_date 已存在';
        ELSE
            CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);
            RAISE NOTICE '复合索引 idx_orders_customer_date 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '索引 idx_orders_customer_date 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建复合索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 5. 使用部分索引（只索引部分数据，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_orders_active') THEN
            RAISE NOTICE '索引 idx_orders_active 已存在';
        ELSE
            CREATE INDEX idx_orders_active ON orders (order_date)
            WHERE status = 'active';
            RAISE NOTICE '部分索引 idx_orders_active 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '索引 idx_orders_active 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建部分索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 6.3 索引维护

```sql
-- 定期VACUUM（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在';
            RETURN;
        END IF;

        VACUUM ANALYZE orders;
        RAISE NOTICE 'VACUUM ANALYZE orders 执行成功';
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN OTHERS THEN
            RAISE WARNING 'VACUUM ANALYZE orders 执行失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 重建索引（如果索引膨胀，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_orders_customer_id') THEN
            RAISE WARNING '索引 idx_orders_customer_id 不存在';
            RETURN;
        END IF;

        REINDEX INDEX idx_orders_customer_id;
        RAISE NOTICE '索引 idx_orders_customer_id 重建成功';
    EXCEPTION
        WHEN undefined_object THEN
            RAISE WARNING '索引 idx_orders_customer_id 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '重建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查看索引使用情况（带错误处理和性能测试）
DO $$
DECLARE
    index_count INT;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在';
            RETURN;
        END IF;

        SELECT COUNT(*) INTO index_count
        FROM pg_stat_user_indexes
        WHERE tablename = 'orders';

        RAISE NOTICE '表 orders 共有 % 个索引', index_count;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询索引使用情况失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN ANALYZE
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
WHERE tablename = 'orders'
ORDER BY idx_scan DESC;
```

---

## 7. 参数调优

### 7.1 关键参数

```sql
-- 查询规划器参数验证（带错误处理）
DO $$
DECLARE
    random_page_cost_setting NUMERIC;
    effective_io_concurrency_setting INT;
BEGIN
    BEGIN
        SELECT setting::NUMERIC INTO random_page_cost_setting
        FROM pg_settings WHERE name = 'random_page_cost';

        SELECT setting::INT INTO effective_io_concurrency_setting
        FROM pg_settings WHERE name = 'effective_io_concurrency';

        RAISE NOTICE '查询规划器配置:';
        RAISE NOTICE '  random_page_cost: %', random_page_cost_setting;
        RAISE NOTICE '  effective_io_concurrency: %', effective_io_concurrency_setting;

        IF random_page_cost_setting > 2.0 THEN
            RAISE WARNING 'random_page_cost 较高，可能适合HDD存储，SSD建议设置为1.1';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询规划器参数验证失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 推荐的配置值:
-- random_page_cost = 1.1            -- 随机页面成本（SSD建议1.1，HDD建议4.0）
-- effective_io_concurrency = 200   -- 有效I/O并发数（SSD建议200）

-- 自动清理参数验证（带错误处理）
DO $$
DECLARE
    autovacuum_setting TEXT;
    autovacuum_max_workers_setting INT;
    autovacuum_naptime_setting TEXT;
BEGIN
    BEGIN
        SELECT setting INTO autovacuum_setting
        FROM pg_settings WHERE name = 'autovacuum';

        SELECT setting::INT INTO autovacuum_max_workers_setting
        FROM pg_settings WHERE name = 'autovacuum_max_workers';

        SELECT setting INTO autovacuum_naptime_setting
        FROM pg_settings WHERE name = 'autovacuum_naptime';

        RAISE NOTICE '自动清理配置:';
        RAISE NOTICE '  autovacuum: %', autovacuum_setting;
        RAISE NOTICE '  autovacuum_max_workers: %', autovacuum_max_workers_setting;
        RAISE NOTICE '  autovacuum_naptime: %', autovacuum_naptime_setting;

        IF autovacuum_setting = 'off' THEN
            RAISE WARNING '自动清理已禁用，建议启用';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询自动清理参数失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 推荐的配置值:
-- autovacuum = on                  -- 启用自动清理
-- autovacuum_max_workers = 3        -- 自动清理最大工作进程数
-- autovacuum_naptime = 1min        -- 自动清理检查间隔
```

### 7.2 日志配置

```sql
-- 日志配置验证（带错误处理）
DO $$
DECLARE
    log_min_duration_setting TEXT;
    log_statement_setting TEXT;
    log_connections_setting TEXT;
    log_disconnections_setting TEXT;
BEGIN
    BEGIN
        SELECT setting INTO log_min_duration_setting
        FROM pg_settings WHERE name = 'log_min_duration_statement';

        SELECT setting INTO log_statement_setting
        FROM pg_settings WHERE name = 'log_statement';

        SELECT setting INTO log_connections_setting
        FROM pg_settings WHERE name = 'log_connections';

        SELECT setting INTO log_disconnections_setting
        FROM pg_settings WHERE name = 'log_disconnections';

        RAISE NOTICE '日志配置:';
        RAISE NOTICE '  log_min_duration_statement: %', log_min_duration_setting;
        RAISE NOTICE '  log_statement: %', log_statement_setting;
        RAISE NOTICE '  log_connections: %', log_connections_setting;
        RAISE NOTICE '  log_disconnections: %', log_disconnections_setting;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询日志配置失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 推荐的配置值:
-- log_min_duration_statement = 1000  -- 记录执行时间>1秒的查询（毫秒）
-- log_statement = 'ddl'              -- 记录DDL语句
-- log_connections = on               -- 记录连接
-- log_disconnections = on            -- 记录断开
```

---

## 8. 性能监控

### 8.1 系统监控

```sql
-- 查看数据库大小（带错误处理和性能测试）
DO $$
DECLARE
    db_size BIGINT;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'mydb') THEN
            RAISE WARNING '数据库 mydb 不存在';
            RETURN;
        END IF;

        SELECT pg_database_size('mydb') INTO db_size;
        RAISE NOTICE '数据库 mydb 大小: %', pg_size_pretty(db_size);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询数据库大小失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN ANALYZE
SELECT pg_size_pretty(pg_database_size('mydb'));

-- 查看表大小（带错误处理和性能测试）
DO $$
DECLARE
    table_count INT;
BEGIN
    BEGIN
        SELECT COUNT(*) INTO table_count
        FROM pg_tables
        WHERE schemaname = 'public';

        RAISE NOTICE 'public schema 共有 % 个表', table_count;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询表大小失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN ANALYZE
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 8.2 查询监控

```sql
-- 查看当前活动查询（带错误处理和性能测试）
DO $$
DECLARE
    active_query_count INT;
BEGIN
    BEGIN
        SELECT COUNT(*) INTO active_query_count
        FROM pg_stat_activity
        WHERE state = 'active' AND pid != pg_backend_pid();

        RAISE NOTICE '当前活动查询数: %', active_query_count;

        IF active_query_count > 100 THEN
            RAISE WARNING '活动查询数较多，可能需要优化';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询活动查询失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN ANALYZE
SELECT
    pid,
    usename,
    application_name,
    state,
    query,
    query_start,
    now() - query_start AS duration
FROM pg_stat_activity
WHERE state = 'active' AND pid != pg_backend_pid()
ORDER BY query_start;
```

### 8.3 慢查询分析

```sql
-- 使用pg_stat_statements扩展（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
            CREATE EXTENSION pg_stat_statements;
            RAISE NOTICE 'pg_stat_statements 扩展创建成功';
        ELSE
            RAISE NOTICE 'pg_stat_statements 扩展已存在';
        END IF;
    EXCEPTION
        WHEN insufficient_privilege THEN
            RAISE WARNING '权限不足，无法创建 pg_stat_statements 扩展';
        WHEN OTHERS THEN
            RAISE WARNING '创建 pg_stat_statements 扩展失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查看最慢的查询（带错误处理和性能测试）
DO $$
DECLARE
    query_count INT;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
            RAISE WARNING 'pg_stat_statements 扩展不存在，无法查询慢查询';
            RETURN;
        END IF;

        SELECT COUNT(*) INTO query_count
        FROM pg_stat_statements;

        RAISE NOTICE 'pg_stat_statements 中共有 % 条查询记录', query_count;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING 'pg_stat_statements 视图不存在';
        WHEN OTHERS THEN
            RAISE WARNING '查询慢查询失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN ANALYZE
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
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
