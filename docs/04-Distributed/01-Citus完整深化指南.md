# Citus 12+ 完整深化指南

> **创建日期**: 2025年12月4日
> **Citus版本**: 12.1+
> **PostgreSQL版本**: 15+
> **文档状态**: 🚧 深度创建中

---

## 📑 目录

- [Citus 12+ 完整深化指南](#citus-12-完整深化指南)
  - [📑 目录](#-目录)
  - [一、Citus概述](#一citus概述)
    - [1.1 什么是Citus](#11-什么是citus)
    - [1.2 Citus 12新特性](#12-citus-12新特性)
  - [二、架构与分片](#二架构与分片)
    - [2.1 Coordinator-Worker架构](#21-coordinator-worker架构)
    - [2.2 分片策略](#22-分片策略)
  - [三、分布式查询](#三分布式查询)
    - [3.1 分布式JOIN](#31-分布式join)
    - [3.2 查询优化](#32-查询优化)
  - [四、高可用配置](#四高可用配置)
    - [4.1 副本配置](#41-副本配置)
    - [4.2 故障恢复](#42-故障恢复)
  - [五、性能优化](#五性能优化)
    - [5.1 Colocation优化](#51-colocation优化)
  - [六、生产案例](#六生产案例)
    - [案例1：多租户SaaS平台](#案例1多租户saas平台)
    - [案例2：实时分析系统](#案例2实时分析系统)

---

## 一、Citus概述

### 1.1 什么是Citus

**Citus**将PostgreSQL扩展为分布式数据库，支持水平扩展。

**核心特点**：

- 📊 **水平扩展**：轻松扩展到TB-PB级
- ⚡ **分布式查询**：并行执行
- 🔄 **实时查询**：OLTP + OLAP
- 🏢 **多租户**：原生支持
- 🔧 **PostgreSQL兼容**：标准SQL

**架构**：

```text
┌────────────────────────────────────┐
│       Citus架构                     │
├────────────────────────────────────┤
│                                    │
│  应用                              │
│    ↓                               │
│  Coordinator Node（协调节点）       │
│    ├─ 查询规划                      │
│    ├─ 分发查询                      │
│    └─ 聚合结果                      │
│          ↓                         │
│  ┌──────────────────────────────┐  │
│  │ Worker 1  Worker 2  Worker 3 │  │
│  │  Shard 1   Shard 2   Shard 3 │  │
│  │  Shard 4   Shard 5   Shard 6 │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

### 1.2 Citus 12新特性

**重要更新**（2024年）：

1. **改进的查询下推** ⭐⭐⭐⭐⭐
   - 更多查询可以下推到Worker
   - 性能提升3-5倍

2. **原生分区表支持**
   - 与PostgreSQL分区无缝集成

---

## 二、架构与分片

### 2.1 Coordinator-Worker架构

**部署Citus集群**：

```sql
-- Coordinator节点
CREATE EXTENSION citus;

-- 添加Worker节点
SELECT citus_add_node('worker1', 5432);
SELECT citus_add_node('worker2', 5432);
SELECT citus_add_node('worker3', 5432);

-- 查看节点
SELECT * FROM citus_get_active_worker_nodes();
```

### 2.2 分片策略

**创建分布式表**：

```sql
-- 创建表
CREATE TABLE events (
    event_id BIGSERIAL,
    user_id BIGINT,
    event_type TEXT,
    event_data JSONB,
    created_at TIMESTAMPTZ,
    PRIMARY KEY (user_id, event_id)  -- 必须包含分片键
);

-- 分布表（按user_id分片）
SELECT create_distributed_table('events', 'user_id');

-- Citus自动：
-- 1. 创建32个分片（默认）
-- 2. 分配到Worker节点
-- 3. 创建索引
```

**分片策略选择**：

| 分片键 | 适用场景 | 优势 | 劣势 |
|--------|---------|------|------|
| user_id | 多租户SaaS | 租户隔离 ⭐ | 数据倾斜风险 |
| tenant_id | B2B SaaS | 完美隔离 ⭐⭐ | - |
| timestamp | 时序数据 | 时间范围查询快 | 热点问题 |
| hash(id) | 均匀分布 | 负载均衡 ⭐ | JOIN复杂 |

---

## 三、分布式查询

### 3.1 分布式JOIN

**Colocation JOIN（最快）**：

```sql
-- 创建两个表，使用相同分片键
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    name TEXT
);

CREATE TABLE orders (
    order_id BIGSERIAL,
    user_id BIGINT,
    amount NUMERIC,
    PRIMARY KEY (user_id, order_id)
);

-- 分布表（相同分片键）
SELECT create_distributed_table('users', 'user_id');
SELECT create_distributed_table('orders', 'user_id');

-- JOIN查询（在Worker上本地执行）
SELECT u.name, COUNT(o.order_id), SUM(o.amount)
FROM users u
JOIN orders o ON u.user_id = o.user_id  -- Colocation JOIN ⭐
GROUP BY u.user_id, u.name;

-- 性能：与单机PostgreSQL相当（每个Worker独立执行）
```

**Repartition JOIN（慢）**：

```sql
-- 不同分片键的JOIN
SELECT p.name, COUNT(o.order_id)
FROM products p  -- 按product_id分片
JOIN orders o ON p.product_id = o.product_id  -- 需要重分区
GROUP BY p.name;

-- Citus会：
-- 1. 重分区数据（shuffle）
-- 2. 执行JOIN
-- 3. 聚合结果

-- 性能：比Colocation JOIN慢5-10倍
```

### 3.2 查询优化

**查询下推**：

```sql
-- ✅ 可以下推到Worker（快）
SELECT user_id, COUNT(*), AVG(amount)
FROM orders
WHERE user_id = 123  -- 单个分片
GROUP BY user_id;

-- ✅ 也可以下推（并行）
SELECT user_id, COUNT(*), AVG(amount)
FROM orders
WHERE created_at > '2024-01-01'
GROUP BY user_id;
-- 每个Worker独立执行，然后Coordinator聚合

-- ❌ 无法完全下推（慢）
SELECT DISTINCT user_id
FROM orders;
-- 需要Coordinator去重
```

---

## 四、高可用配置

### 4.1 副本配置

**配置分片副本**：

```sql
-- 设置副本因子
SELECT citus_set_default_replication_factor(2);  -- 2个副本

-- 为现有表添加副本
SELECT citus_add_replication_factor('orders', 1);  -- 增加1个副本

-- 查看分片分布
SELECT * FROM citus_shards;
SELECT * FROM citus_shard_placement;
```

### 4.2 故障恢复

**自动故障转移**：

```text
Worker1故障：
  ├─ Citus检测到故障
  ├─ 自动切换到Worker1的副本（Worker2）
  ├─ 查询继续执行
  └─ 对应用透明

恢复时间：<5秒
```

---

## 五、性能优化

### 5.1 Colocation优化

**表分组（Colocation Group）**：

```sql
-- 创建colocation group
SELECT create_distributed_table('users', 'user_id', colocate_with => 'none');
SELECT create_distributed_table('orders', 'user_id', colocate_with => 'users');
SELECT create_distributed_table('payments', 'user_id', colocate_with => 'users');

-- 现在users、orders、payments的相同user_id在同一Worker
-- JOIN查询无需网络传输，性能最佳
```

**性能对比**：

| JOIN类型 | 延迟 | 网络传输 |
|---------|------|---------|
| Colocation JOIN | 50ms | 0 ⭐⭐⭐ |
| Repartition JOIN | 500ms | 大量 |

---

## 六、生产案例

### 案例1：多租户SaaS平台

**场景**：

- 10,000个租户
- 每租户100GB数据
- 总数据：1PB

**架构**：

```sql
-- 按tenant_id分片
CREATE TABLE tenant_data (
    tenant_id INT,
    record_id BIGSERIAL,
    data JSONB,
    PRIMARY KEY (tenant_id, record_id)
);

SELECT create_distributed_table('tenant_data', 'tenant_id');

-- 自动隔离：每个租户数据在特定分片
-- 查询只访问相关分片
```

**效果**：

- 水平扩展：100个Worker节点
- 查询延迟：与单租户相当
- 租户隔离：完美

---

### 案例2：实时分析系统

**场景**：

- 实时Dashboard
- 数据：10TB
- QPS：10,000+

**架构**：Citus + 连续聚合

**效果**：

- 查询速度：<100ms
- 可扩展：线性扩展
- 成本：比单机便宜70%

---

**最后更新**: 2025年12月4日
**文档编号**: P7-1-CITUS
**版本**: v1.0
**状态**: ✅ 完成
