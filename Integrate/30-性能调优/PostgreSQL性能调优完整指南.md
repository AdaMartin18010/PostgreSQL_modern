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

```sql
-- postgresql.conf
shared_buffers = 8GB              -- 共享内存缓冲区（建议为总内存的25%）
effective_cache_size = 24GB      -- 有效缓存大小（建议为总内存的50-75%）
work_mem = 256MB                  -- 工作内存（用于排序、哈希等）
maintenance_work_mem = 2GB        -- 维护工作内存（用于VACUUM、CREATE INDEX等）
```

### 4.2 连接配置

```sql
-- 连接数配置
max_connections = 200              -- 最大连接数
superuser_reserved_connections = 3  -- 超级用户保留连接数

-- 连接池（推荐使用PgBouncer或PgPool-II）
```

### 4.3 并发控制

```sql
-- 并发控制参数
max_worker_processes = 8           -- 最大工作进程数
max_parallel_workers_per_gather = 4 -- 每个查询的最大并行工作进程数
max_parallel_workers = 8          -- 最大并行工作进程数
```

---

## 5. 查询级调优

### 5.1 SQL优化

```sql
-- ✅ 推荐：使用索引
SELECT * FROM users WHERE id = 123;

-- ❌ 避免：全表扫描
SELECT * FROM users WHERE name LIKE '%test%';

-- ✅ 推荐：使用LIMIT
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20;

-- ❌ 避免：返回大量数据
SELECT * FROM orders ORDER BY created_at DESC;
```

### 5.2 执行计划分析

```sql
-- 分析查询计划
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM orders
WHERE customer_id = 123
  AND order_date >= '2024-01-01';

-- 检查是否使用了索引
-- 检查是否有顺序扫描（Seq Scan）
-- 检查是否有索引扫描（Index Scan）
```

### 5.3 查询重写

```sql
-- 使用EXISTS代替IN（对于大表）
-- ❌ 不推荐
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);

-- ✅ 推荐
SELECT * FROM users WHERE EXISTS (SELECT 1 FROM orders WHERE orders.user_id = users.id);
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
-- 1. 为经常查询的列创建索引
CREATE INDEX idx_orders_customer_id ON orders (customer_id);

-- 2. 为WHERE子句中的列创建索引
CREATE INDEX idx_orders_date ON orders (order_date);

-- 3. 为JOIN条件创建索引
CREATE INDEX idx_orders_user_id ON orders (user_id);

-- 4. 使用复合索引
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);

-- 5. 使用部分索引（只索引部分数据）
CREATE INDEX idx_orders_active ON orders (order_date)
WHERE status = 'active';
```

### 6.3 索引维护

```sql
-- 定期VACUUM
VACUUM ANALYZE orders;

-- 重建索引（如果索引膨胀）
REINDEX INDEX idx_orders_customer_id;

-- 查看索引使用情况
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
-- 查询规划器参数
random_page_cost = 1.1            -- 随机页面成本（SSD建议1.1，HDD建议4.0）
effective_io_concurrency = 200   -- 有效I/O并发数（SSD建议200）

-- 自动清理参数
autovacuum = on                  -- 启用自动清理
autovacuum_max_workers = 3        -- 自动清理最大工作进程数
autovacuum_naptime = 1min        -- 自动清理检查间隔
```

### 7.2 日志配置

```sql
-- 慢查询日志
log_min_duration_statement = 1000  -- 记录执行时间>1秒的查询

-- 查询日志
log_statement = 'ddl'              -- 记录DDL语句
log_connections = on               -- 记录连接
log_disconnections = on            -- 记录断开
```

---

## 8. 性能监控

### 8.1 系统监控

```sql
-- 查看数据库大小
SELECT pg_size_pretty(pg_database_size('mydb'));

-- 查看表大小
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
-- 查看当前活动查询
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
```

### 8.3 慢查询分析

```sql
-- 使用pg_stat_statements扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查看最慢的查询
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
