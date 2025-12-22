---

> **📋 文档来源**: `PostgreSQL培训\05-部署架构\【深入】Citus分布式PostgreSQL完整实战指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 【深入】Citus分布式PostgreSQL完整实战指南

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 13+, Citus 12.0+
> **难度等级**: ⭐⭐⭐⭐⭐ 专家 | **预计学习时间**: 12-15小时

---

## 📋 目录

- [【深入】Citus分布式PostgreSQL完整实战指南](#深入citus分布式postgresql完整实战指南)
  - [📋 目录](#-目录)
  - [1. 课程概述](#1-课程概述)
    - [1.1 什么是Citus？](#11-什么是citus)
      - [核心特性](#核心特性)
      - [适用场景](#适用场景)
    - [1.2 Citus vs 其他方案](#12-citus-vs-其他方案)
  - [2. 分布式数据库基础](#2-分布式数据库基础)
    - [2.1 分片策略](#21-分片策略)
      - [Hash分片](#hash分片)
      - [Range分片](#range分片)
      - [复合分片（Citus默认）](#复合分片citus默认)
    - [2.2 CAP理论与Citus](#22-cap理论与citus)
    - [2.3 分布式事务](#23-分布式事务)
      - [2PC（两阶段提交）](#2pc两阶段提交)
  - [3. Citus架构深入](#3-citus架构深入)
    - [3.1 系统架构](#31-系统架构)
    - [3.2 核心组件](#32-核心组件)
      - [Coordinator（协调器）](#coordinator协调器)
      - [Worker（工作节点）](#worker工作节点)
    - [3.3 元数据表](#33-元数据表)
  - [4. 集群部署](#4-集群部署)
    - [4.1 单机测试环境](#41-单机测试环境)
      - [Docker Compose部署](#docker-compose部署)
      - [初始化集群](#初始化集群)
    - [4.2 生产环境部署](#42-生产环境部署)
      - [系统要求](#系统要求)
      - [Ansible自动化部署](#ansible自动化部署)
    - [4.3 Kubernetes部署](#43-kubernetes部署)
  - [5. 数据分片策略](#5-数据分片策略)
    - [5.1 分布式表创建](#51-分布式表创建)
      - [基本分片](#基本分片)
      - [引用表（广播表）](#引用表广播表)
      - [协同定位（Colocation）](#协同定位colocation)
    - [5.2 分片键选择](#52-分片键选择)
      - [最佳实践](#最佳实践)
      - [避免的做法](#避免的做法)
    - [5.3 分片管理](#53-分片管理)
      - [查看分片分布](#查看分片分布)
      - [手动分片分裂](#手动分片分裂)
  - [6. 分布式查询](#6-分布式查询)
    - [6.1 查询路由](#61-查询路由)
      - [Router查询（单分片）](#router查询单分片)
      - [Real-Time查询（多分片并行）](#real-time查询多分片并行)
    - [6.2 分布式JOIN](#62-分布式join)
      - [协同定位JOIN（最快）](#协同定位join最快)
      - [引用表JOIN](#引用表join)
      - [重分区JOIN（Repartition）](#重分区joinrepartition)
    - [6.3 分布式聚合](#63-分布式聚合)
    - [6.4 分布式事务](#64-分布式事务)
      - [单分片事务（快）](#单分片事务快)
      - [跨分片事务（慢）](#跨分片事务慢)
  - [7. 数据迁移与再平衡](#7-数据迁移与再平衡)
    - [7.1 从单机PostgreSQL迁移](#71-从单机postgresql迁移)
      - [逻辑迁移](#逻辑迁移)
      - [实时迁移（使用逻辑复制）](#实时迁移使用逻辑复制)
    - [7.2 节点扩容](#72-节点扩容)
    - [7.3 分片再平衡策略](#73-分片再平衡策略)
  - [8. 高可用与容错](#8-高可用与容错)
    - [8.1 分片副本](#81-分片副本)
    - [8.2 自动故障转移](#82-自动故障转移)
      - [Streaming Replication + Patroni](#streaming-replication--patroni)
      - [Coordinator高可用](#coordinator高可用)
    - [8.3 备份与恢复](#83-备份与恢复)
      - [逻辑备份](#逻辑备份)
      - [物理备份（每个Worker）](#物理备份每个worker)
  - [9. 性能优化](#9-性能优化)
    - [9.1 查询优化](#91-查询优化)
      - [启用并行查询](#启用并行查询)
      - [使用物化视图](#使用物化视图)
    - [9.2 索引策略](#92-索引策略)
    - [9.3 连接池](#93-连接池)
    - [9.4 批量操作优化](#94-批量操作优化)
  - [10. 监控与运维](#10-监控与运维)
    - [10.1 关键监控指标](#101-关键监控指标)
    - [10.2 Prometheus监控](#102-prometheus监控)
    - [10.3 日常运维脚本](#103-日常运维脚本)
  - [11. 生产实战案例](#11-生产实战案例)
    - [11.1 案例1：多租户SaaS平台](#111-案例1多租户saas平台)
      - [业务场景](#业务场景)
      - [架构设计](#架构设计)
      - [查询模式](#查询模式)
    - [11.2 案例2：实时分析平台](#112-案例2实时分析平台)
    - [11.3 案例3：电商订单系统](#113-案例3电商订单系统)
  - [12. 最佳实践](#12-最佳实践)
    - [12.1 数据建模原则](#121-数据建模原则)
      - [✅ 推荐做法](#-推荐做法)
    - [12.2 性能优化Checklist](#122-性能优化checklist)
    - [12.3 运维Checklist](#123-运维checklist)
  - [13. FAQ与疑难解答](#13-faq与疑难解答)
    - [Q1: Citus适合我的场景吗？](#q1-citus适合我的场景吗)
    - [Q2: 如何处理数据倾斜？](#q2-如何处理数据倾斜)
    - [Q3: 跨分片查询太慢怎么办？](#q3-跨分片查询太慢怎么办)
    - [Q4: Citus与单机PostgreSQL兼容性如何？](#q4-citus与单机postgresql兼容性如何)
    - [Q5: 如何从Citus迁回单机PostgreSQL？](#q5-如何从citus迁回单机postgresql)
  - [📚 延伸阅读](#-延伸阅读)
    - [官方资源](#官方资源)
    - [相关技术](#相关技术)
    - [推荐阅读](#推荐阅读)
  - [✅ 学习检查清单](#-学习检查清单)
  - [💡 下一步学习](#-下一步学习)

1. [分布式数据库基础](#2-分布式数据库基础)
2. [Citus架构深入](#3-citus架构深入)
3. [集群部署](#4-集群部署)
4. [数据分片策略](#5-数据分片策略)
5. [分布式查询](#6-分布式查询)
6. [数据迁移与再平衡](#7-数据迁移与再平衡)
7. [高可用与容错](#8-高可用与容错)
8. [性能优化](#9-性能优化)
9. [监控与运维](#10-监控与运维)
10. [生产实战案例](#11-生产实战案例)
11. [最佳实践](#12-最佳实践)
12. [FAQ与疑难解答](#13-faq与疑难解答)

---

## 1. 课程概述

### 1.1 什么是Citus？

**Citus** 是PostgreSQL的分布式扩展，通过水平分片将PostgreSQL转变为分布式数据库，实现线性扩展。

#### 核心特性

| 特性 | 说明 | 优势 |
|------|------|------|
| **水平扩展** | 横向添加节点 | TB级数据，高并发 |
| **分布式查询** | 并行查询处理 | 查询性能线性提升 |
| **原生SQL** | 100%兼容PostgreSQL | 无需改代码 |
| **多租户** | Row-level isolation | SaaS应用理想选择 |
| **实时分析** | 混合工作负载 | OLTP + OLAP |
| **高可用** | 副本自动故障转移 | 99.99%可用性 |
| **开源** | AGPLv3（社区版） | 免费使用 |

#### 适用场景

**✅ 理想场景**:

- 多租户SaaS应用
- 实时分析Dashboard
- 时间序列数据
- 地理空间数据
- 高并发读写

**❌ 不适合**:

- 大量跨分片JOIN
- 复杂的分布式事务
- 小数据量（< 100GB）

### 1.2 Citus vs 其他方案

```text
Citus vs PostgreSQL单机:
✅ 线性扩展（TB→PB级）
✅ 并行查询（10x-100x加速）
✅ 高可用（分片副本）
⚠️ 复杂度增加
⚠️ 跨分片操作限制

Citus vs Greenplum/ClickHouse:
✅ OLTP + OLAP混合负载
✅ 实时写入（非批量）
✅ 标准PostgreSQL兼容
❌ 纯OLAP性能略逊

Citus vs TimescaleDB:
✅ 更通用（非时序专用）
✅ 更灵活的分片策略
✅ 多租户支持更好
❌ 时序数据压缩不如TimescaleDB

Citus vs Vitess/CockroachDB:
✅ PostgreSQL生态完整兼容
✅ 学习曲线平缓
✅ 复杂查询支持更好
❌ 全局一致性不如CockroachDB
```

---

## 2. 分布式数据库基础

### 2.1 分片策略

#### Hash分片

```text
优点：数据均匀分布
缺点：范围查询需扫描所有分片

示例：
Hash(user_id) % 32 = shard_id

user_id=100 → Hash → 12 → Shard 12
user_id=200 → Hash → 5  → Shard 5
user_id=300 → Hash → 28 → Shard 28
```

#### Range分片

```text
优点：范围查询高效
缺点：可能数据倾斜

示例：按时间分片
2024-01-01 ~ 2024-01-31 → Shard 1
2024-02-01 ~ 2024-02-29 → Shard 2
2024-03-01 ~ 2024-03-31 → Shard 3
```

#### 复合分片（Citus默认）

```text
Hash(distribution_column) + Colocate相关表

示例：多租户SaaS
Hash(tenant_id) → Shard X
同一tenant的所有表都在Shard X
→ 本地JOIN，高性能！
```

### 2.2 CAP理论与Citus

```text
CAP三角:
C (Consistency): 一致性
A (Availability): 可用性
P (Partition Tolerance): 分区容错

Citus定位:
默认: CP系统（强一致性）
配置: 可调整为AP（最终一致性）

实现：
- 同步复制 → CP（牺牲部分可用性）
- 异步复制 → AP（牺牲强一致性）
```

### 2.3 分布式事务

#### 2PC（两阶段提交）

```text
Citus使用2PC实现跨分片事务：

阶段1：准备（Prepare）
Coordinator → All Shards: "准备提交"
All Shards → Coordinator: "OK/ABORT"

阶段2：提交（Commit）
if (all OK):
    Coordinator → All Shards: "COMMIT"
else:
    Coordinator → All Shards: "ROLLBACK"

性能影响：
- 单分片事务：无影响
- 跨分片事务：性能下降约2-3x
```

---

## 3. Citus架构深入

### 3.1 系统架构

```text
┌─────────────────────────────────────────────┐
│         Application Layer                   │
│  Web App / API / BI Tools                   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Coordinator Node                    │
│  ┌──────────────────────────────────────┐  │
│  │  Query Parser & Planner              │  │
│  │  - Parse SQL                         │  │
│  │  - Detect distributed queries        │  │
│  │  - Generate execution plan           │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  Distributed Executor                │  │
│  │  - Route queries to workers          │  │
│  │  - Aggregate results                 │  │
│  │  - Manage transactions               │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  Metadata Tables                     │  │
│  │  - pg_dist_node                      │  │
│  │  - pg_dist_partition                 │  │
│  │  - pg_dist_shard                     │  │
│  │  - pg_dist_placement                 │  │
│  └──────────────────────────────────────┘  │
└──────────────┬──────────────┬──────────────┘
               │              │
     ┌─────────▼───┐    ┌────▼──────────┐
     │ Worker 1    │    │ Worker 2      │
     │ ┌─────────┐ │    │ ┌───────────┐ │
     │ │Shard 1  │ │    │ │ Shard 2   │ │
     │ │Shard 4  │ │    │ │ Shard 5   │ │
     │ │Shard 7  │ │    │ │ Shard 8   │ │
     │ └─────────┘ │    │ └───────────┘ │
     └─────────────┘    └───────────────┘

     ┌─────────────┐    ┌───────────────┐
     │ Worker 3    │    │ Worker N      │
     │ ┌─────────┐ │    │ ┌───────────┐ │
     │ │Shard 3  │ │    │ │ Shard N   │ │
     │ │Shard 6  │ │    │ │ ...       │ │
     │ │Shard 9  │ │    │ │           │ │
     │ └─────────┘ │    │ └───────────┘ │
     └─────────────┘    └───────────────┘
```

### 3.2 核心组件

#### Coordinator（协调器）

**职责**:

- SQL解析和优化
- 分布式执行计划生成
- Worker节点管理
- 元数据管理
- 结果聚合

**特点**:

- 轻量级（不存储业务数据）
- 可水平扩展（多Coordinator）
- 无状态（可任意替换）

#### Worker（工作节点）

**职责**:

- 存储分片数据
- 执行分片查询
- 本地事务处理

**特点**:

- 标准PostgreSQL实例
- 可独立使用
- 支持副本（高可用）

### 3.3 元数据表

```sql
-- 查看集群节点
SELECT * FROM pg_dist_node;
-- nodeid | groupid | nodename  | nodeport | noderack | hasmetadata | isactive
--------+---------+-----------+----------+----------+--------------+----------
--   1   |    0    | coord.db  |   5432   | default  |     t        |    t
--   2   |    1    | worker1   |   5432   | rack1    |     f        |    t
--   3   |    2    | worker2   |   5432   | rack1    |     f        |    t

-- 查看分布式表
SELECT * FROM pg_dist_partition;
-- logicalrelid | partmethod | partkey | colocationid | repmodel
--------------+------------+---------+--------------+----------
-- events      |     h      | tenant_id|     1       |    s

-- 查看分片分布
SELECT * FROM pg_dist_shard;
-- logicalrelid | shardid | shardstorage | shardminvalue | shardmaxvalue
--------------+---------+--------------+---------------+---------------
-- events      | 102008  |      t       |  -2147483648  |   -2013265921
-- events      | 102009  |      t       |  -2013265920  |   -1879048193

-- 查看分片位置
SELECT * FROM pg_dist_placement;
-- shardid | shardstate | shardlength | placementid | groupid
---------+------------+-------------+-------------+---------
-- 102008 |     1      |   8192000   |     1       |   1
-- 102008 |     1      |   8192000   |     2       |   2  -- 副本
```

---

## 4. 集群部署

### 4.1 单机测试环境

#### Docker Compose部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  coordinator:
    image: citusdata/citus:12.1
    container_name: citus-coordinator
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: citus
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - coordinator-data:/var/lib/postgresql/data
    command:
      - "postgres"
      - "-c"
      - "shared_preload_libraries=citus"

  worker1:
    image: citusdata/citus:12.1
    container_name: citus-worker1
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: citus
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - worker1-data:/var/lib/postgresql/data
    command:
      - "postgres"
      - "-c"
      - "shared_preload_libraries=citus"

  worker2:
    image: citusdata/citus:12.1
    container_name: citus-worker2
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: citus
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - worker2-data:/var/lib/postgresql/data
    command:
      - "postgres"
      - "-c"
      - "shared_preload_libraries=citus"

volumes:
  coordinator-data:
  worker1-data:
  worker2-data:
```

#### 初始化集群

```bash
# 启动集群
docker-compose up -d

# 连接到Coordinator
docker exec -it citus-coordinator psql -U postgres -d citus

# 在Coordinator上执行：
CREATE EXTENSION citus;

-- 添加Worker节点
SELECT * FROM citus_add_node('citus-worker1', 5432);
SELECT * FROM citus_add_node('citus-worker2', 5432);

-- 验证集群状态
SELECT * FROM citus_get_active_worker_nodes();
```

### 4.2 生产环境部署

#### 系统要求

```text
硬件配置（单个Worker节点）：
- CPU: 16+ cores
- RAM: 64GB+ (建议128GB)
- 存储: NVMe SSD, RAID10
- 网络: 10Gbps+

Coordinator节点：
- CPU: 8+ cores
- RAM: 32GB+
- 存储: SSD (元数据轻量)
- 网络: 10Gbps+

规模建议：
- 小型: 1 Coordinator + 2-4 Workers
- 中型: 1 Coordinator + 8-16 Workers
- 大型: 2+ Coordinators + 32+ Workers
```

#### Ansible自动化部署

```yaml
# ansible/citus-cluster.yml
---
- name: Deploy Citus Cluster
  hosts: all
  become: yes
  vars:
    postgres_version: 15
    citus_version: 12.1

  tasks:
    - name: Install PostgreSQL & Citus
      apt:
        name:
          - "postgresql-{{ postgres_version }}"
          - "postgresql-{{ postgres_version }}-citus-12.1"
        state: present

    - name: Configure PostgreSQL
      lineinfile:
        path: "/etc/postgresql/{{ postgres_version }}/main/postgresql.conf"
        regexp: "{{ item.regexp }}"
        line: "{{ item.line }}"
      with_items:
        - { regexp: '^#?shared_preload_libraries', line: "shared_preload_libraries = 'citus'" }
        - { regexp: '^#?listen_addresses', line: "listen_addresses = '*'" }
        - { regexp: '^#?max_connections', line: "max_connections = 300" }
        - { regexp: '^#?shared_buffers', line: "shared_buffers = 16GB" }

    - name: Configure pg_hba.conf
      blockinfile:
        path: "/etc/postgresql/{{ postgres_version }}/main/pg_hba.conf"
        block: |
          host    all    all    10.0.0.0/8    md5

    - name: Restart PostgreSQL
      systemd:
        name: postgresql
        state: restarted

- name: Initialize Coordinator
  hosts: coordinator
  become: yes
  become_user: postgres
  tasks:
    - name: Create Citus extension
      postgresql_ext:
        name: citus
        db: production

    - name: Add worker nodes
      postgresql_query:
        db: production
        query: "SELECT citus_add_node('{{ item }}', 5432);"
      with_items: "{{ groups['workers'] }}"
```

### 4.3 Kubernetes部署

```yaml
# k8s/citus-cluster.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: citus-config
data:
  postgresql.conf: |
    shared_preload_libraries = 'citus'
    max_connections = 300
    shared_buffers = 8GB
    effective_cache_size = 24GB
    maintenance_work_mem = 2GB
    work_mem = 16MB

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: citus-coordinator
spec:
  serviceName: citus-coordinator
  replicas: 1
  selector:
    matchLabels:
      app: citus-coordinator
  template:
    metadata:
      labels:
        app: citus-coordinator
    spec:
      containers:
      - name: postgres
        image: citusdata/citus:12.1
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: citus-secrets
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
        - name: config
          mountPath: /etc/postgresql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: citus-worker
spec:
  serviceName: citus-worker
  replicas: 4
  selector:
    matchLabels:
      app: citus-worker
  template:
    metadata:
      labels:
        app: citus-worker
    spec:
      containers:
      - name: postgres
        image: citusdata/citus:12.1
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: citus-secrets
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "64Gi"
            cpu: "16"
          limits:
            memory: "64Gi"
            cpu: "16"
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 1Ti
```

---

## 5. 数据分片策略

### 5.1 分布式表创建

#### 基本分片

```sql
-- 创建普通表
CREATE TABLE events (
    event_id BIGSERIAL,
    tenant_id INT NOT NULL,
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 转换为分布式表（Hash分片）
SELECT create_distributed_table('events', 'tenant_id');

-- 查看分片数（默认32个）
SELECT COUNT(*) FROM pg_dist_shard WHERE logicalrelid = 'events'::regclass;

-- 自定义分片数
SELECT create_distributed_table('events', 'tenant_id', shard_count := 64);
```

#### 引用表（广播表）

```sql
-- 小型维度表：复制到所有节点
CREATE TABLE countries (
    country_code CHAR(2) PRIMARY KEY,
    country_name VARCHAR(100)
);

SELECT create_reference_table('countries');

-- 所有Worker都有完整副本，JOIN无需跨节点
SELECT e.*, c.country_name
FROM events e
JOIN countries c ON e.country_code = c.country_code
WHERE e.tenant_id = 123;
-- 完全在单个Worker上执行！
```

#### 协同定位（Colocation）

```sql
-- 相关表使用相同分片键，确保数据在同一节点
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,
    username VARCHAR(100)
);

CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,
    user_id BIGINT,
    amount DECIMAL(10,2)
);

-- 按tenant_id分片，确保同一租户数据在同一节点
SELECT create_distributed_table('users', 'tenant_id');
SELECT create_distributed_table('orders', 'tenant_id', colocate_with := 'users');

-- 验证协同定位
SELECT colocationid FROM pg_dist_partition
WHERE logicalrelid IN ('users'::regclass, 'orders'::regclass);
-- 应该返回相同的colocationid

-- 高效本地JOIN
SELECT u.username, SUM(o.amount) AS total
FROM users u
JOIN orders o ON u.tenant_id = o.tenant_id AND u.user_id = o.user_id
WHERE u.tenant_id = 123
GROUP BY u.username;
-- 完全在单个Worker上执行，无跨节点通信！
```

### 5.2 分片键选择

#### 最佳实践

| 场景 | 推荐分片键 | 原因 |
|------|-----------|------|
| **多租户SaaS** | tenant_id | 租户隔离，本地JOIN |
| **时序数据** | device_id / user_id | 设备/用户隔离 |
| **电商** | user_id | 用户订单在同一节点 |
| **IoT** | device_id | 设备数据聚合 |
| **日志** | log_source_id | 来源隔离 |

#### 避免的做法

```sql
-- ❌ 使用自增ID作为分片键
CREATE TABLE bad_table (
    id SERIAL PRIMARY KEY,  -- 自增，数据倾斜！
    data TEXT
);
SELECT create_distributed_table('bad_table', 'id');
-- 问题：新数据集中在一个分片，负载不均

-- ❌ 使用低基数列
SELECT create_distributed_table('orders', 'status');
-- 问题：status只有几个值，无法均匀分布

-- ✅ 正确做法
SELECT create_distributed_table('orders', 'user_id');
-- 高基数，均匀分布
```

### 5.3 分片管理

#### 查看分片分布

```sql
-- 查看表的分片分布
SELECT
    s.shardid,
    s.shardminvalue,
    s.shardmaxvalue,
    p.nodename,
    p.nodeport,
    pg_size_pretty(citus_shard_size(s.shardid)) AS shard_size
FROM pg_dist_shard s
JOIN pg_dist_placement p ON s.shardid = p.shardid
WHERE s.logicalrelid = 'events'::regclass
ORDER BY s.shardid;

-- 查看节点数据分布
SELECT
    nodename,
    COUNT(*) AS shard_count,
    pg_size_pretty(SUM(citus_shard_size(shardid))) AS total_size
FROM pg_dist_shard s
JOIN pg_dist_placement p ON s.shardid = p.shardid
WHERE s.logicalrelid = 'events'::regclass
GROUP BY nodename;
```

#### 手动分片分裂

```sql
-- 分裂单个分片（当某个分片过大时）
SELECT citus_split_shard_by_split_points(
    'events',
    ARRAY[102008],  -- 要分裂的shardid
    ARRAY[-1000000, 0, 1000000],  -- 分裂点
    'citus-worker3',  -- 新分片的目标节点
    5432
);
```

---

## 6. 分布式查询

### 6.1 查询路由

#### Router查询（单分片）

```sql
-- 查询包含分片键 = 常量，路由到单个Worker
SELECT * FROM events
WHERE tenant_id = 123  -- 分片键过滤
  AND event_type = 'login'
  AND created_at > '2025-01-01';

-- EXPLAIN查看执行计划
EXPLAIN (VERBOSE)
SELECT * FROM events WHERE tenant_id = 123;

-- Custom Scan (Citus Router)
--   Task Count: 1
--   Tasks Shown: All
--   ->  Task
--         Node: host=worker1 port=5432 dbname=citus
--         ->  Seq Scan on events_102008 events
--               Filter: (tenant_id = 123)
```

#### Real-Time查询（多分片并行）

```sql
-- 没有分片键过滤，需要扫描所有分片
SELECT event_type, COUNT(*)
FROM events
WHERE created_at > '2025-01-01'
GROUP BY event_type;

-- EXPLAIN
-- Custom Scan (Citus Real-Time)
--   Task Count: 32  -- 所有分片并行
--   ->  HashAggregate
--         ->  Parallel Seq Scan on events_XXXX
```

### 6.2 分布式JOIN

#### 协同定位JOIN（最快）

```sql
-- 同一分片键，本地JOIN
SELECT u.username, COUNT(o.order_id) AS order_count
FROM users u
JOIN orders o ON u.tenant_id = o.tenant_id AND u.user_id = o.user_id
WHERE u.tenant_id = 123
GROUP BY u.username;

-- 执行：单个Worker本地JOIN，无网络传输
```

#### 引用表JOIN

```sql
-- 分布式表 JOIN 引用表（广播表）
SELECT e.*, c.country_name
FROM events e
JOIN countries c ON e.country_code = c.country_code
WHERE e.tenant_id = 123;

-- 执行：countries在每个Worker都有副本，本地JOIN
```

#### 重分区JOIN（Repartition）

```sql
-- 非协同定位表的JOIN
SELECT u.username, p.product_name, o.amount
FROM users u
JOIN orders o ON u.user_id = o.user_id  -- 不同分片键
JOIN products p ON o.product_id = p.product_id;

-- 执行：
-- 1. 将users和orders按user_id重分区
-- 2. 在Coordinator聚合
-- 3. 与products JOIN
-- 性能：慢，涉及大量网络传输

-- 优化：使用协同定位
-- 确保users和orders都按相同键分片
```

### 6.3 分布式聚合

```sql
-- 两阶段聚合
SELECT tenant_id, DATE(created_at), COUNT(*), AVG(value)
FROM events
WHERE created_at > '2025-01-01'
GROUP BY tenant_id, DATE(created_at);

-- 执行过程：
-- 阶段1（Worker上）：
--   SELECT tenant_id, DATE(created_at),
--          COUNT(*) AS count, SUM(value) AS sum, COUNT(value) AS value_count
--   FROM events_shard_X
--   GROUP BY tenant_id, DATE(created_at)

-- 阶段2（Coordinator上）：
--   SELECT tenant_id, date,
--          SUM(count) AS total_count,
--          SUM(sum) / SUM(value_count) AS avg_value
--   FROM worker_results
--   GROUP BY tenant_id, date
```

### 6.4 分布式事务

#### 单分片事务（快）

```sql
BEGIN;
-- 所有操作在同一分片
UPDATE events SET processed = true
WHERE tenant_id = 123 AND event_id = 456;

INSERT INTO audit_log (tenant_id, action, timestamp)
VALUES (123, 'event_processed', NOW());
COMMIT;

-- 本地事务，性能与单机PostgreSQL相同
```

#### 跨分片事务（慢）

```sql
BEGIN;
-- 涉及多个tenant，跨多个分片
UPDATE events SET processed = true
WHERE event_id IN (100, 200, 300);  -- 不同tenant_id

-- 使用2PC，性能下降
COMMIT;

-- 建议：尽量避免跨分片事务
-- 或使用应用层最终一致性
```

---

## 7. 数据迁移与再平衡

### 7.1 从单机PostgreSQL迁移

#### 逻辑迁移

```sql
-- 源数据库（单机PostgreSQL）
-- 1. 导出数据
pg_dump -h source-db -U postgres -d mydb -t events --data-only > events_data.sql

-- 目标数据库（Citus Coordinator）
-- 2. 创建分布式表结构
CREATE TABLE events (
    event_id BIGSERIAL,
    tenant_id INT NOT NULL,
    event_data JSONB,
    created_at TIMESTAMPTZ
);

SELECT create_distributed_table('events', 'tenant_id');

-- 3. 导入数据
\i events_data.sql

-- 4. 验证数据
SELECT COUNT(*) FROM events;
```

#### 实时迁移（使用逻辑复制）

```sql
-- 源数据库
-- 1. 启用逻辑复制
ALTER SYSTEM SET wal_level = logical;
-- 重启PostgreSQL

CREATE PUBLICATION citus_migration FOR TABLE events;

-- Citus Coordinator
-- 2. 创建分布式表
CREATE TABLE events (...);
SELECT create_distributed_table('events', 'tenant_id');

-- 3. 创建订阅
CREATE SUBSCRIPTION citus_migration_sub
CONNECTION 'host=source-db port=5432 dbname=mydb user=postgres password=xxx'
PUBLICATION citus_migration;

-- 4. 监控同步进度
SELECT * FROM pg_stat_subscription;

-- 5. 切换应用（停写 → 验证 → 切换连接 → 删除订阅）
DROP SUBSCRIPTION citus_migration_sub;
```

### 7.2 节点扩容

```sql
-- 添加新Worker节点
SELECT * FROM citus_add_node('new-worker', 5432);

-- 查看当前分片分布
SELECT
    nodename,
    COUNT(*) AS shard_count
FROM pg_dist_shard s
JOIN pg_dist_placement p ON s.shardid = p.shardid
GROUP BY nodename;

-- 再平衡分片
SELECT citus_rebalance_start();

-- 监控再平衡进度
SELECT * FROM citus_rebalance_status();

-- 手动迁移特定分片
SELECT citus_move_shard_placement(
    102008,  -- shardid
    'old-worker', 5432,
    'new-worker', 5432,
    shard_transfer_mode := 'block_writes'  -- 或 'force_logical'
);
```

### 7.3 分片再平衡策略

```sql
-- 按大小再平衡（平衡磁盘使用）
SELECT citus_rebalance_start(
    rebalance_strategy := 'by_disk_size'
);

-- 按分片数再平衡（平衡分片数量）
SELECT citus_rebalance_start(
    rebalance_strategy := 'by_shard_count'
);

-- 排除特定节点
SELECT citus_rebalance_start(
    excluded_shard_list := ARRAY[102001, 102005]
);

-- 查看推荐的再平衡计划（不执行）
SELECT * FROM citus_get_rebalance_table_shards_plan(
    'events'
);
```

---

## 8. 高可用与容错

### 8.1 分片副本

```sql
-- 设置分片副本数（创建表时）
SELECT create_distributed_table(
    'events',
    'tenant_id',
    shard_count := 32,
    replication_factor := 2  -- 2副本
);

-- 修改现有表的副本数
SELECT citus_set_table_replication_model('events', 'streaming');
SELECT citus_update_table_replication_factor('events', 2);

-- 查看分片副本分布
SELECT
    s.shardid,
    s.logicalrelid::text AS table_name,
    array_agg(p.nodename || ':' || p.shardstate) AS placements
FROM pg_dist_shard s
JOIN pg_dist_placement p ON s.shardid = p.shardid
WHERE s.logicalrelid = 'events'::regclass
GROUP BY s.shardid, s.logicalrelid;
```

### 8.2 自动故障转移

#### Streaming Replication + Patroni

```yaml
# patroni.yml (Worker节点)
scope: citus-worker-1
namespace: /citus/
name: worker1-primary

restapi:
  listen: 0.0.0.0:8008
  connect_address: worker1:8008

etcd:
  hosts: etcd1:2379,etcd2:2379,etcd3:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      parameters:
        shared_preload_libraries: citus
        wal_level: replica
        max_wal_senders: 10
        max_replication_slots: 10

postgresql:
  listen: 0.0.0.0:5432
  connect_address: worker1:5432
  data_dir: /var/lib/postgresql/15/main
  authentication:
    replication:
      username: replicator
      password: repl_password
    superuser:
      username: postgres
      password: postgres
  parameters:
    shared_preload_libraries: citus
```

#### Coordinator高可用

```sql
-- 使用PgBouncer + HAProxy实现Coordinator HA

-- HAProxy配置
# /etc/haproxy/haproxy.cfg
listen postgres_coordinator
    bind *:5000
    mode tcp
    balance roundrobin
    option httpchk
    http-check expect status 200
    default-server inter 3s fall 3 rise 2 on-marked-down shutdown-sessions
    server coord1 coord1:5432 maxconn 100 check port 8008
    server coord2 coord2:5432 maxconn 100 check port 8008 backup
```

### 8.3 备份与恢复

#### 逻辑备份

```bash
# 备份整个集群（从Coordinator）
pg_dump -h coordinator -U postgres -d citus --schema-only > schema.sql
pg_dump -h coordinator -U postgres -d citus --data-only > data.sql

# 恢复
psql -h coordinator -U postgres -d citus < schema.sql
psql -h coordinator -U postgres -d citus < data.sql
```

#### 物理备份（每个Worker）

```bash
# 使用pg_basebackup备份Worker
pg_basebackup -h worker1 -U postgres -D /backup/worker1 -Ft -z -P

# 或使用WAL归档 + PITR
# postgresql.conf
archive_mode = on
archive_command = 'aws s3 cp %p s3://my-bucket/wal/%f'

# 创建基础备份
SELECT pg_start_backup('label', false, false);
# rsync数据目录到备份位置
SELECT pg_stop_backup(false, true);
```

---

## 9. 性能优化

### 9.1 查询优化

#### 启用并行查询

```sql
-- 调整并行参数
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 32;
ALTER SYSTEM SET parallel_tuple_cost = 0.01;
SELECT pg_reload_conf();

-- 强制并行（测试用）
SET force_parallel_mode = on;
```

#### 使用物化视图

```sql
-- 创建分布式物化视图
CREATE MATERIALIZED VIEW tenant_stats AS
SELECT
    tenant_id,
    DATE(created_at) AS date,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users
FROM events
GROUP BY tenant_id, DATE(created_at);

-- 创建为分布式表
SELECT create_distributed_table('tenant_stats', 'tenant_id', colocate_with := 'events');

-- 刷新
REFRESH MATERIALIZED VIEW tenant_stats;

-- 增量刷新（自定义）
DELETE FROM tenant_stats WHERE date = CURRENT_DATE;
INSERT INTO tenant_stats
SELECT tenant_id, CURRENT_DATE, COUNT(*), COUNT(DISTINCT user_id)
FROM events
WHERE DATE(created_at) = CURRENT_DATE
GROUP BY tenant_id;
```

### 9.2 索引策略

```sql
-- 本地索引（每个分片独立）
CREATE INDEX events_created_at_idx ON events(created_at);
-- 自动在所有分片创建

-- 复合索引（包含分片键）
CREATE INDEX events_tenant_created_idx ON events(tenant_id, created_at);

-- 部分索引
CREATE INDEX events_unprocessed_idx ON events(tenant_id, created_at)
WHERE processed = false;

-- 查看索引大小
SELECT
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_indexes
JOIN pg_class ON pg_class.relname = indexname
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 9.3 连接池

```sql
-- 使用PgBouncer（每个节点）
# /etc/pgbouncer/pgbouncer.ini
[databases]
citus = host=localhost port=5432 dbname=citus

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 10000
default_pool_size = 25
reserve_pool_size = 5
reserve_pool_timeout = 3

-- 应用连接到 coordinator:6432 而不是 5432
```

### 9.4 批量操作优化

```sql
-- ❌ 慢：逐行插入
DO $$
BEGIN
    FOR i IN 1..10000 LOOP
        INSERT INTO events (tenant_id, event_data)
        VALUES (i, '{"action":"test"}');
    END LOOP;
END $$;

-- ✅ 快：批量插入
INSERT INTO events (tenant_id, event_data)
SELECT
    i,
    '{"action":"test"}'
FROM generate_series(1, 10000) i;

-- ✅ 更快：COPY
COPY events (tenant_id, event_data) FROM STDIN;
1\t{"action":"test"}
2\t{"action":"test"}
...
\.

-- ✅ 最快：并行COPY（分片aware）
-- 使用citus_copy_shard_placement实现
```

---

## 10. 监控与运维

### 10.1 关键监控指标

```sql
-- 1. 集群健康状态
SELECT * FROM citus_check_cluster_node_health();

-- 2. 分片分布
SELECT
    nodename,
    COUNT(*) AS shard_count,
    pg_size_pretty(SUM(citus_shard_size(shardid))) AS total_size,
    pg_size_pretty(AVG(citus_shard_size(shardid))) AS avg_shard_size
FROM pg_dist_shard s
JOIN pg_dist_placement p ON s.shardid = p.shardid
GROUP BY nodename;

-- 3. 查询性能
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time,
    stddev_exec_time
FROM citus_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- 4. 连接数
SELECT
    nodename,
    COUNT(*) AS connection_count
FROM citus_worker_stat_activity
GROUP BY nodename;

-- 5. 复制延迟
SELECT
    application_name,
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replication_lag_bytes
FROM pg_stat_replication;
```

### 10.2 Prometheus监控

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'citus'
    static_configs:
      - targets:
        - 'coordinator:9187'
        - 'worker1:9187'
        - 'worker2:9187'
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
```

```sql
-- 安装postgres_exporter
# docker-compose.yml增加：
postgres_exporter:
  image: prometheuscommunity/postgres-exporter
  environment:
    DATA_SOURCE_NAME: "postgresql://postgres:password@coordinator:5432/citus?sslmode=disable"
  ports:
    - "9187:9187"
```

### 10.3 日常运维脚本

```bash
#!/bin/bash
# citus_health_check.sh

COORDINATOR="coordinator:5432"
DB="citus"

echo "=== Citus Cluster Health Check ==="
echo ""

# 1. 节点状态
echo "1. Worker Nodes Status:"
psql -h $COORDINATOR -d $DB -c "
SELECT nodename, nodeport, isactive
FROM pg_dist_node
WHERE groupid > 0;
"

# 2. 分片分布
echo ""
echo "2. Shard Distribution:"
psql -h $COORDINATOR -d $DB -c "
SELECT
    nodename,
    COUNT(*) AS shard_count
FROM pg_dist_placement p
JOIN pg_dist_node n ON p.groupid = n.groupid
GROUP BY nodename;
"

# 3. 复制延迟
echo ""
echo "3. Replication Lag:"
for worker in worker1 worker2 worker3; do
    echo "Worker: $worker"
    psql -h $worker -d $DB -c "
    SELECT
        application_name,
        pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) AS lag
    FROM pg_stat_replication;
    "
done

# 4. 磁盘使用
echo ""
echo "4. Disk Usage:"
psql -h $COORDINATOR -d $DB -c "
SELECT
    nodename,
    pg_size_pretty(SUM(citus_shard_size(shardid))) AS total_size
FROM pg_dist_shard s
JOIN pg_dist_placement p ON s.shardid = p.shardid
JOIN pg_dist_node n ON p.groupid = n.groupid
GROUP BY nodename;
"

echo ""
echo "=== Health Check Complete ==="
```

---

## 11. 生产实战案例

### 11.1 案例1：多租户SaaS平台

#### 业务场景

- 10万+租户
- 每租户100万+用户
- 日活1000万+
- QPS峰值10万+

#### 架构设计

```sql
-- 核心表设计
CREATE TABLE tenants (
    tenant_id SERIAL PRIMARY KEY,
    tenant_name VARCHAR(100),
    plan VARCHAR(20),
    created_at TIMESTAMPTZ
);
SELECT create_reference_table('tenants');  -- 广播表

CREATE TABLE users (
    user_id BIGSERIAL,
    tenant_id INT NOT NULL,
    username VARCHAR(100),
    email VARCHAR(255),
    created_at TIMESTAMPTZ,
    PRIMARY KEY (tenant_id, user_id)
);
SELECT create_distributed_table('users', 'tenant_id', shard_count := 128);

CREATE TABLE user_events (
    event_id BIGSERIAL,
    tenant_id INT NOT NULL,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (tenant_id, event_id)
);
SELECT create_distributed_table('user_events', 'tenant_id',
    shard_count := 256, colocate_with := 'users');

-- 租户隔离索引
CREATE INDEX user_events_tenant_created_idx
ON user_events(tenant_id, created_at);

CREATE INDEX user_events_tenant_user_idx
ON user_events(tenant_id, user_id);
```

#### 查询模式

```sql
-- 租户Dashboard（单租户查询，超快）
SELECT
    DATE(created_at) AS date,
    event_type,
    COUNT(*) AS event_count
FROM user_events
WHERE tenant_id = 12345  -- 单分片查询
  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at), event_type
ORDER BY date, event_type;

-- 平台级分析（所有租户，并行）
SELECT
    t.plan,
    COUNT(DISTINCT u.tenant_id) AS tenant_count,
    COUNT(DISTINCT u.user_id) AS total_users,
    SUM(e.event_count) AS total_events
FROM tenants t
LEFT JOIN users u ON t.tenant_id = u.tenant_id
LEFT JOIN (
    SELECT tenant_id, COUNT(*) AS event_count
    FROM user_events
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY tenant_id
) e ON t.tenant_id = e.tenant_id
GROUP BY t.plan;
```

### 11.2 案例2：实时分析平台

```sql
-- 时序事件表
CREATE TABLE metrics (
    metric_id BIGSERIAL,
    device_id INT NOT NULL,
    metric_name VARCHAR(50),
    metric_value DOUBLE PRECISION,
    tags JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (device_id, timestamp, metric_id)
);

-- 按device_id分片 + 时间分区
SELECT create_distributed_table('metrics', 'device_id', shard_count := 256);

-- 时间分区（在Coordinator和所有Worker上）
CREATE TABLE metrics_2025_01 PARTITION OF metrics
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE metrics_2025_02 PARTITION OF metrics
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- 实时聚合查询
SELECT
    device_id,
    metric_name,
    AVG(metric_value) AS avg_value,
    MAX(metric_value) AS max_value,
    MIN(metric_value) AS min_value,
    COUNT(*) AS sample_count
FROM metrics
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY device_id, metric_name;

-- 创建连续聚合（类似TimescaleDB的continuous aggregate）
CREATE MATERIALIZED VIEW metrics_hourly AS
SELECT
    device_id,
    metric_name,
    date_trunc('hour', timestamp) AS hour,
    AVG(metric_value) AS avg_value,
    MAX(metric_value) AS max_value,
    MIN(metric_value) AS min_value,
    COUNT(*) AS sample_count
FROM metrics
GROUP BY device_id, metric_name, date_trunc('hour', timestamp);

SELECT create_distributed_table('metrics_hourly', 'device_id',
    colocate_with := 'metrics');

-- 定期刷新（cron job）
REFRESH MATERIALIZED VIEW metrics_hourly;
```

### 11.3 案例3：电商订单系统

```sql
-- 用户表
CREATE TABLE customers (
    customer_id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(100),
    region VARCHAR(50)
);
SELECT create_distributed_table('customers', 'customer_id', shard_count := 128);

-- 订单表
CREATE TABLE orders (
    order_id BIGSERIAL,
    customer_id BIGINT NOT NULL,
    order_status VARCHAR(20),
    total_amount DECIMAL(12,2),
    created_at TIMESTAMPTZ,
    PRIMARY KEY (customer_id, order_id)
);
SELECT create_distributed_table('orders', 'customer_id', colocate_with := 'customers');

-- 订单明细
CREATE TABLE order_items (
    item_id BIGSERIAL,
    order_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,  -- 冗余分片键
    product_id INT NOT NULL,
    quantity INT,
    price DECIMAL(10,2),
    PRIMARY KEY (customer_id, item_id)
);
SELECT create_distributed_table('order_items', 'customer_id', colocate_with := 'orders');

-- 商品表（引用表）
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(100),
    price DECIMAL(10,2)
);
SELECT create_reference_table('products');

-- 客户订单明细查询（本地JOIN）
SELECT
    c.name AS customer_name,
    o.order_id,
    o.created_at,
    p.product_name,
    oi.quantity,
    oi.price
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.customer_id = oi.customer_id AND o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE c.customer_id = 12345
  AND o.created_at >= '2025-01-01'
ORDER BY o.created_at DESC;
-- 完全本地执行，无跨节点通信！
```

---

## 12. 最佳实践

### 12.1 数据建模原则

#### ✅ 推荐做法

1. **选择高基数分片键**

    ```sql
    -- ✅ 好：高基数
    SELECT create_distributed_table('users', 'user_id');  -- 百万+用户

    -- ❌ 坏：低基数
    SELECT create_distributed_table('users', 'country_code');  -- 只有200+国家
    ```

2. **协同定位相关表**

    ```sql
    -- ✅ 好：相关表使用相同分片键
    CREATE TABLE orders (order_id BIGSERIAL, user_id BIGINT, ...);
    CREATE TABLE payments (payment_id BIGSERIAL, user_id BIGINT, ...);

    SELECT create_distributed_table('orders', 'user_id');
    SELECT create_distributed_table('payments', 'user_id', colocate_with := 'orders');
    ```

3. **小型维度表使用引用表**

    ```sql
    -- ✅ 好：小表广播到所有节点
    SELECT create_reference_table('countries');
    SELECT create_reference_table('product_categories');
    ```

4. **冗余分片键**

    ```sql
    -- ✅ 好：在子表冗余父表的分片键
    CREATE TABLE order_items (
        item_id BIGSERIAL,
        order_id BIGINT,
        user_id BIGINT,  -- 冗余！但保证协同定位
        product_id INT,
        PRIMARY KEY (user_id, item_id)
    );
    ```

### 12.2 性能优化Checklist

- [ ] 分片键选择合理（高基数、业务隔离）
- [ ] 相关表已协同定位（colocate_with）
- [ ] 小表使用引用表（create_reference_table）
- [ ] 查询包含分片键过滤（WHERE tenant_id = ?）
- [ ] 避免跨分片JOIN
- [ ] 创建适当的本地索引
- [ ] 使用连接池（PgBouncer）
- [ ] 批量操作使用COPY
- [ ] 定期VACUUM ANALYZE
- [ ] 监控分片大小均衡性

### 12.3 运维Checklist

- [ ] 配置分片副本（至少2副本）
- [ ] 部署Worker HA（Patroni/Repmgr）
- [ ] 配置自动备份（WAL归档 + pg_basebackup）
- [ ] 监控复制延迟
- [ ] 监控磁盘使用（及时扩容或再平衡）
- [ ] 定期测试故障转移
- [ ] 定期测试备份恢复
- [ ] 监控慢查询（pg_stat_statements）
- [ ] 配置告警（节点down、复制延迟、磁盘满）

---

## 13. FAQ与疑难解答

### Q1: Citus适合我的场景吗？

**决策树**:

```text
数据量 < 100GB?
  └─ YES → 单机PostgreSQL足够
  └─ NO  → 继续

主要是OLAP分析?
  └─ YES → 考虑ClickHouse/Greenplum
  └─ NO  → 继续

主要是时序数据?
  └─ YES → 考虑TimescaleDB
  └─ NO  → 继续

需要多租户隔离?
  └─ YES → ✅ Citus非常适合！
  └─ NO  → 继续

有明确的分片键?
  └─ YES → ✅ Citus适合
  └─ NO  → ⚠️  需要重新设计数据模型

大量跨分片JOIN?
  └─ YES → ❌ Citus不适合
  └─ NO  → ✅ Citus适合
```

### Q2: 如何处理数据倾斜？

```sql
-- 1. 诊断：查看分片大小分布
SELECT
    shardid,
    pg_size_pretty(citus_shard_size(shardid)) AS size,
    nodename
FROM pg_dist_shard s
JOIN pg_dist_placement p ON s.shardid = p.shardid
WHERE logicalrelid = 'events'::regclass
ORDER BY citus_shard_size(shardid) DESC
LIMIT 20;

-- 2. 如果某些分片特别大：
-- 方案A：分裂大分片
SELECT citus_split_shard_by_split_points(...);

-- 方案B：重新选择分片键
-- 例如：从tenant_id改为(tenant_id, user_id)的hash
```

### Q3: 跨分片查询太慢怎么办？

**解决方案**:

1. **重新设计数据模型，避免跨分片**
2. **使用物化视图预聚合**

    ```sql
    CREATE MATERIALIZED VIEW cross_tenant_stats AS
    SELECT
        DATE(created_at) AS date,
        COUNT(*) AS total_events,
        COUNT(DISTINCT tenant_id) AS active_tenants
    FROM events
    GROUP BY DATE(created_at);

    -- 查询物化视图而不是原表
    SELECT * FROM cross_tenant_stats WHERE date >= '2025-01-01';
    ```

3. **使用OLAP专用系统**

### Q4: Citus与单机PostgreSQL兼容性如何？

**兼容**:

- ✅ 99% SQL语法
- ✅ 所有PostgreSQL扩展（PostGIS、hstore等）
- ✅ 触发器、存储过程
- ✅ 外键（分片内）

**限制**:

- ❌ 跨分片外键（可用trigger模拟）
- ❌ SERIALIZABLE隔离级别（跨分片）
- ⚠️  某些系统视图行为不同

### Q5: 如何从Citus迁回单机PostgreSQL？

```sql
-- 1. 在单机PostgreSQL创建表
CREATE TABLE events (...);

-- 2. 从Citus导出数据
pg_dump -h citus-coordinator -U postgres -d citus -t events --data-only \
  | psql -h single-pg -U postgres -d mydb

-- 3. 验证数据
SELECT COUNT(*) FROM events;  -- 在两边执行对比
```

---

## 📚 延伸阅读

### 官方资源

- [Citus Documentation](https://docs.citusdata.com/)
- [Citus GitHub](https://github.com/citusdata/citus)
- [Azure Database for PostgreSQL - Hyperscale](https://azure.microsoft.com/en-us/services/postgresql/)

### 相关技术

- **TimescaleDB**: 时序数据专用扩展
- **PostgreSQL-XL**: 另一个PostgreSQL分布式方案
- **Greenplum**: MPP架构（批量分析）
- **CockroachDB**: 全球分布式SQL

### 推荐阅读

- 《Designing Data-Intensive Applications》by Martin Kleppmann
- 《Database Internals》by Alex Petrov

---

## ✅ 学习检查清单

- [ ] 理解Citus架构和工作原理
- [ ] 掌握分片策略和分片键选择
- [ ] 能够部署和配置Citus集群
- [ ] 熟练使用分布式表和引用表
- [ ] 理解查询路由和执行计划
- [ ] 掌握数据迁移和再平衡
- [ ] 能够配置高可用和故障转移
- [ ] 熟悉性能优化技巧
- [ ] 能够监控和排查问题

---

## 💡 下一步学习

1. **进阶主题**:
   - Citus MX（多Coordinator架构）
   - 实时数据管道（Kafka + Citus）
   - 混合事务/分析处理（HTAP）

2. **相关课程**:
   - [PostgreSQL高可用架构](../09-高可用/)
   - [PostgreSQL性能调优](../11-性能调优/)
   - [TimescaleDB时序数据库](./【深入】TimescaleDB时序数据库完整指南.md)

---

**文档维护**: 本文档持续更新以反映Citus最新特性。
**反馈**: 如发现错误或有改进建议，请提交issue。

**版本历史**:

- v1.0 (2025-01): 初始版本，覆盖Citus 12.0+核心特性
