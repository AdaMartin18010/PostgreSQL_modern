# pg_partman 分区管理详解

> **更新时间**: 2025 年 1 月
> **技术版本**: PostgreSQL 17+ with pg_partman
> **文档编号**: 03-03-TREND-26

## 📑 概述

pg_partman 是 PostgreSQL 的分区管理扩展，提供了自动分区创建、维护、数据归档等功能，大大简化了分区表的管理工作。
它特别适合时间序列数据、日志数据等需要按时间分区的场景。

## 🎯 核心价值

- **自动分区**：自动创建和管理分区
- **数据归档**：自动归档旧数据
- **分区维护**：自动维护分区索引和统计信息
- **简化管理**：大大简化分区表管理
- **生产就绪**：稳定可靠，适合生产环境

## 📚 目录

- [pg\_partman 分区管理详解](#pg_partman-分区管理详解)
  - [📑 概述](#-概述)
  - [🎯 核心价值](#-核心价值)
  - [📚 目录](#-目录)
  - [1. pg\_partman 基础](#1-pg_partman-基础)
    - [1.1 什么是 pg\_partman](#11-什么是-pg_partman)
    - [1.2 主要功能](#12-主要功能)
  - [2. 安装和配置](#2-安装和配置)
    - [2.1 安装 pg\_partman](#21-安装-pg_partman)
    - [2.2 配置 pg\_partman](#22-配置-pg_partman)
  - [3. 自动分区管理](#3-自动分区管理)
    - [3.1 创建分区表](#31-创建分区表)
    - [3.2 分区类型](#32-分区类型)
    - [3.3 分区维护](#33-分区维护)
  - [4. 数据归档](#4-数据归档)
    - [4.1 配置数据归档](#41-配置数据归档)
    - [4.2 归档策略](#42-归档策略)
  - [5. 分区维护](#5-分区维护)
    - [5.1 自动维护任务](#51-自动维护任务)
    - [5.2 索引维护](#52-索引维护)
  - [6. 最佳实践](#6-最佳实践)
    - [6.1 分区策略](#61-分区策略)
    - [6.2 监控和维护](#62-监控和维护)
  - [7. 实际案例](#7-实际案例)
    - [7.1 案例：日志表自动分区](#71-案例日志表自动分区)
  - [📊 总结](#-总结)

---

## 1. pg_partman 基础

### 1.1 什么是 pg_partman

pg_partman 是 PostgreSQL 的扩展，提供了自动分区管理功能，可以自动创建、维护和归档分区。

### 1.2 主要功能

- **自动分区创建**：根据配置自动创建新分区
- **数据归档**：自动归档旧分区数据
- **分区维护**：自动维护分区索引和统计信息
- **分区删除**：自动删除过期分区

---

## 2. 安装和配置

### 2.1 安装 pg_partman

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS pg_partman;

-- 验证安装
SELECT * FROM pg_extension WHERE extname = 'pg_partman';
```

### 2.2 配置 pg_partman

```sql
-- 创建配置表
SELECT partman.create_parent(
    p_parent_table => 'public.orders',
    p_control => 'order_date',
    p_type => 'range',
    p_interval => 'monthly',
    p_premake => 3
);
```

---

## 3. 自动分区管理

### 3.1 创建分区表

```sql
-- 创建父表
CREATE TABLE orders (
    id SERIAL,
    order_date DATE NOT NULL,
    customer_id INTEGER,
    total_amount DECIMAL(10,2)
) PARTITION BY RANGE (order_date);

-- 使用 pg_partman 管理分区
SELECT partman.create_parent(
    p_parent_table => 'public.orders',
    p_control => 'order_date',
    p_type => 'range',
    p_interval => 'monthly',  -- 按月分区
    p_premake => 3            -- 提前创建 3 个月的分区
);
```

### 3.2 分区类型

```sql
-- 范围分区（按时间）
SELECT partman.create_parent(
    p_parent_table => 'public.orders',
    p_control => 'order_date',
    p_type => 'range',
    p_interval => 'monthly'
);

-- 范围分区（按整数）
SELECT partman.create_parent(
    p_parent_table => 'public.orders',
    p_control => 'id',
    p_type => 'range',
    p_interval => '1000'  -- 每 1000 个 ID 一个分区
);

-- 列表分区
SELECT partman.create_parent(
    p_parent_table => 'public.sales',
    p_control => 'region',
    p_type => 'list',
    p_interval => 'region'  -- 按区域分区
);
```

### 3.3 分区维护

```sql
-- 运行分区维护（创建新分区，删除旧分区）
SELECT partman.run_maintenance();

-- 查看分区配置
SELECT * FROM partman.part_config;

-- 查看分区信息
SELECT * FROM partman.show_partitions('public.orders');
```

---

## 4. 数据归档

### 4.1 配置数据归档

```sql
-- 创建归档表
CREATE TABLE orders_archive (LIKE orders INCLUDING ALL);

-- 配置归档
UPDATE partman.part_config
SET
    retention = '12 months',
    retention_keep_table = false,
    retention_keep_index = false
WHERE parent_table = 'public.orders';

-- 运行归档
SELECT partman.run_maintenance_proc('public.orders');
```

### 4.2 归档策略

```sql
-- 归档到另一个表
SELECT partman.archive_partition(
    p_parent_table => 'public.orders',
    p_archive_table => 'public.orders_archive',
    p_retention => '12 months'
);

-- 归档到文件
SELECT partman.archive_partition(
    p_parent_table => 'public.orders',
    p_archive_file => '/archive/orders_2024_01.csv',
    p_retention => '12 months'
);
```

---

## 5. 分区维护

### 5.1 自动维护任务

```sql
-- 配置自动维护（使用 pg_cron）
SELECT cron.schedule(
    'partition-maintenance',
    '0 2 * * *',  -- 每天凌晨 2 点
    'SELECT partman.run_maintenance();'
);
```

### 5.2 索引维护

```sql
-- 自动在分区上创建索引
SELECT partman.create_parent(
    p_parent_table => 'public.orders',
    p_control => 'order_date',
    p_type => 'range',
    p_interval => 'monthly',
    p_indexes => ARRAY[
        'CREATE INDEX ON {PARTITION} (customer_id)',
        'CREATE INDEX ON {PARTITION} (order_date)'
    ]
);
```

---

## 6. 最佳实践

### 6.1 分区策略

```sql
-- 时间序列数据：按月分区
SELECT partman.create_parent(
    p_parent_table => 'public.time_series_data',
    p_control => 'timestamp',
    p_type => 'range',
    p_interval => 'monthly',
    p_premake => 3
);

-- 日志数据：按天分区
SELECT partman.create_parent(
    p_parent_table => 'public.logs',
    p_control => 'log_date',
    p_type => 'range',
    p_interval => 'daily',
    p_premake => 7
);
```

### 6.2 监控和维护

```sql
-- 查看分区状态
SELECT
    parent_table,
    partition_type,
    partition_interval,
    premake,
    retention
FROM partman.part_config;

-- 查看分区列表
SELECT * FROM partman.show_partitions('public.orders');
```

---

## 7. 实际案例

### 7.1 案例：日志表自动分区

```sql
-- 场景：应用日志表，需要按天分区，自动归档
-- 要求：自动创建分区，自动归档 30 天前的数据

-- 步骤 1：创建日志表
CREATE TABLE app_logs (
    id BIGSERIAL,
    log_date TIMESTAMPTZ NOT NULL,
    level TEXT,
    message TEXT,
    metadata JSONB
) PARTITION BY RANGE (log_date);

-- 步骤 2：使用 pg_partman 管理分区
SELECT partman.create_parent(
    p_parent_table => 'public.app_logs',
    p_control => 'log_date',
    p_type => 'range',
    p_interval => 'daily',      -- 按天分区
    p_premake => 7,             -- 提前创建 7 天的分区
    p_start_partition => CURRENT_DATE::text
);

-- 步骤 3：配置归档
UPDATE partman.part_config
SET
    retention = '30 days',
    retention_keep_table = false
WHERE parent_table = 'public.app_logs';

-- 步骤 4：配置自动维护
SELECT cron.schedule(
    'app-logs-partition-maintenance',
    '0 1 * * *',  -- 每天凌晨 1 点
    'SELECT partman.run_maintenance_proc(''public.app_logs'');'
);

-- 性能结果：
-- - 自动创建分区：每天自动创建
-- - 自动归档：30 天前的数据自动归档
-- - 查询性能：只扫描相关分区
```

---

## 📊 总结

pg_partman 为 PostgreSQL 提供了强大的自动分区管理功能，大大简化了分区表的管理工作。通过合理配置分区策略、归档策略、自动维护等方法，可以在生产环境中实现高效的分区表管理。建议根据数据特征选择合适的分区策略，并定期监控分区状态。

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
**文档编号**: 03-03-TREND-26
