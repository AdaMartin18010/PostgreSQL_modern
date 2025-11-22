# CDC 变更数据捕获：实时数据同步方案

> **更新时间**: 2025 年 1 月
> **技术版本**: PostgreSQL 17+ with CDC tools
> **文档编号**: 03-03-TREND-28

## 📑 概述

CDC（Change Data Capture）变更数据捕获是一种实时数据同步技术，可以捕获数据库的变更并实时同步到其他系统。
本文档介绍 PostgreSQL 的 CDC 方案，包括逻辑复制、Debezium、WAL 解析等实现方式。

## 🎯 核心价值

- **实时同步**：实时捕获和同步数据变更
- **低延迟**：毫秒级的数据同步延迟
- **可靠性**：基于 WAL 的可靠变更捕获
- **可扩展**：支持多个目标系统
- **生产就绪**：稳定可靠，适合生产环境

## 📚 目录

- [CDC 变更数据捕获：实时数据同步方案](#cdc-变更数据捕获实时数据同步方案)
  - [📑 概述](#-概述)
  - [🎯 核心价值](#-核心价值)
  - [📚 目录](#-目录)
  - [1. CDC 概述](#1-cdc-概述)
    - [1.1 什么是 CDC](#11-什么是-cdc)
    - [1.2 CDC 应用场景](#12-cdc-应用场景)
    - [1.3 PostgreSQL CDC 方案](#13-postgresql-cdc-方案)
  - [2. 逻辑复制 CDC](#2-逻辑复制-cdc)
    - [2.1 配置逻辑复制](#21-配置逻辑复制)
    - [2.2 订阅变更](#22-订阅变更)
    - [2.3 监控复制](#23-监控复制)
  - [3. Debezium CDC](#3-debezium-cdc)
    - [3.1 Debezium 架构](#31-debezium-架构)
    - [3.2 配置 Debezium](#32-配置-debezium)
    - [3.3 处理变更事件](#33-处理变更事件)
  - [4. WAL 解析 CDC](#4-wal-解析-cdc)
    - [4.1 使用 pg\_logical 扩展](#41-使用-pg_logical-扩展)
    - [4.2 自定义 WAL 解析](#42-自定义-wal-解析)
  - [5. CDC 最佳实践](#5-cdc-最佳实践)
    - [5.1 性能优化](#51-性能优化)
    - [5.2 错误处理](#52-错误处理)
  - [6. 实际案例](#6-实际案例)
    - [6.1 案例：实时数据仓库同步](#61-案例实时数据仓库同步)
    - [6.2 案例：事件驱动架构](#62-案例事件驱动架构)
  - [📊 总结](#-总结)

---

## 1. CDC 概述

### 1.1 什么是 CDC

CDC（Change Data Capture）是一种技术，用于捕获数据库中的数据变更（INSERT、UPDATE、DELETE），并将这些变更实时同步到其他系统。

### 1.2 CDC 应用场景

- **数据同步**：主库到从库的数据同步
- **数据仓库**：实时数据仓库更新
- **事件驱动架构**：基于数据变更的事件触发
- **微服务同步**：微服务之间的数据同步
- **缓存更新**：实时更新缓存

### 1.3 PostgreSQL CDC 方案

- **逻辑复制**：PostgreSQL 原生 CDC 方案
- **Debezium**：基于 Kafka Connect 的 CDC 方案
- **WAL 解析**：直接解析 WAL 文件的方案

---

## 2. 逻辑复制 CDC

### 2.1 配置逻辑复制

```sql
-- 配置 postgresql.conf
wal_level = logical
max_replication_slots = 10
max_wal_senders = 10

-- 创建复制槽
SELECT pg_create_logical_replication_slot('cdc_slot', 'pgoutput');

-- 创建发布
CREATE PUBLICATION cdc_publication FOR ALL TABLES;

-- 或者指定表
CREATE PUBLICATION cdc_publication FOR TABLE orders, customers;
```

### 2.2 订阅变更

```sql
-- 创建订阅
CREATE SUBSCRIPTION cdc_subscription
CONNECTION 'host=target_host dbname=target_db user=replicator'
PUBLICATION cdc_publication
WITH (
    copy_data = false,
    create_slot = true,
    enabled = true
);

-- 查看订阅状态
SELECT * FROM pg_subscription;
SELECT * FROM pg_replication_slots;
```

### 2.3 监控复制

```sql
-- 查看复制延迟
SELECT
    subname,
    pg_subscription_rel.srsubid,
    pg_stat_replication.lag
FROM pg_subscription
JOIN pg_subscription_rel ON pg_subscription.oid = pg_subscription_rel.srsubid
LEFT JOIN pg_stat_replication ON pg_subscription.subname = pg_stat_replication.application_name;

-- 查看复制槽状态
SELECT
    slot_name,
    slot_type,
    active,
    restart_lsn,
    confirmed_flush_lsn
FROM pg_replication_slots;
```

---

## 3. Debezium CDC

### 3.1 Debezium 架构

```text
PostgreSQL → Debezium Connector → Kafka → 目标系统
```

### 3.2 配置 Debezium

```json
{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres_host",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "password",
    "database.dbname": "mydb",
    "database.server.name": "postgres_server",
    "table.whitelist": "public.orders,public.customers",
    "plugin.name": "pgoutput",
    "slot.name": "debezium_slot",
    "publication.name": "debezium_publication"
  }
}
```

### 3.3 处理变更事件

```python
# Python 消费 Kafka 变更事件
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'postgres_server.public.orders',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    event = message.value
    op = event['op']  # 'c'=create, 'u'=update, 'd'=delete

    if op == 'c':
        # 处理插入
        print(f"Insert: {event['after']}")
    elif op == 'u':
        # 处理更新
        print(f"Update: {event['before']} -> {event['after']}")
    elif op == 'd':
        # 处理删除
        print(f"Delete: {event['before']}")
```

---

## 4. WAL 解析 CDC

### 4.1 使用 pg_logical 扩展

```sql
-- 安装 pg_logical 扩展
CREATE EXTENSION IF NOT EXISTS pg_logical;

-- 创建逻辑复制槽
SELECT pg_create_logical_replication_slot('wal_slot', 'pgoutput');

-- 解析 WAL
SELECT * FROM pg_logical_slot_get_changes('wal_slot', NULL, NULL);
```

### 4.2 自定义 WAL 解析

```python
# Python WAL 解析示例
import psycopg2
from psycopg2.extras import LogicalReplicationConnection

conn = psycopg2.connect(
    "dbname=mydb user=replicator",
    connection_factory=LogicalReplicationConnection
)

cur = conn.cursor()
cur.start_replication(slot_name='wal_slot', decode=True)

def consume(msg):
    print(f"LSN: {msg.data_start}")
    print(f"Payload: {msg.payload}")
    msg.cursor.send_feedback(flush_lsn=msg.data_start)

cur.consume_stream(consume)
```

---

## 5. CDC 最佳实践

### 5.1 性能优化

```sql
-- 1. 使用复制槽避免 WAL 丢失
SELECT pg_create_logical_replication_slot('cdc_slot', 'pgoutput');

-- 2. 监控复制延迟
SELECT * FROM pg_stat_replication;

-- 3. 定期清理旧的复制槽
SELECT pg_drop_replication_slot('old_slot');

-- 4. 配置合适的 WAL 保留
wal_keep_size = 1GB
max_wal_size = 4GB
```

### 5.2 错误处理

```sql
-- 监控复制错误
SELECT
    subname,
    subenabled,
    subslotname,
    subpublications
FROM pg_subscription
WHERE subenabled = false;

-- 重新同步表
ALTER SUBSCRIPTION cdc_subscription
REFRESH PUBLICATION;
```

---

## 6. 实际案例

### 6.1 案例：实时数据仓库同步

```sql
-- 场景：主库数据实时同步到数据仓库
-- 要求：低延迟，高可靠性

-- 步骤 1：配置主库
-- postgresql.conf
wal_level = logical
max_replication_slots = 5

-- 步骤 2：创建发布
CREATE PUBLICATION dw_publication FOR TABLE orders, customers, products;

-- 步骤 3：在数据仓库创建订阅
CREATE SUBSCRIPTION dw_subscription
CONNECTION 'host=dw_host dbname=dw_db user=replicator'
PUBLICATION dw_publication
WITH (
    copy_data = true,
    create_slot = true,
    enabled = true
);

-- 步骤 4：监控同步
SELECT
    subname,
    pg_stat_replication.lag
FROM pg_subscription
LEFT JOIN pg_stat_replication ON pg_subscription.subname = pg_stat_replication.application_name;
```

### 6.2 案例：事件驱动架构

```sql
-- 场景：基于数据变更触发事件
-- 要求：实时事件触发

-- 创建变更日志表
CREATE TABLE change_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建触发器记录变更
CREATE OR REPLACE FUNCTION log_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO change_log (table_name, operation, new_data)
        VALUES (TG_TABLE_NAME, 'INSERT', to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO change_log (table_name, operation, old_data, new_data)
        VALUES (TG_TABLE_NAME, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO change_log (table_name, operation, old_data)
        VALUES (TG_TABLE_NAME, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    END IF;
END;
$$;

-- 在表上创建触发器
CREATE TRIGGER orders_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION log_changes();

-- 使用逻辑复制同步变更日志
CREATE PUBLICATION event_publication FOR TABLE change_log;
```

---

## 📊 总结

CDC 变更数据捕获为 PostgreSQL 提供了强大的实时数据同步能力。
通过合理使用逻辑复制、Debezium、WAL 解析等方案，可以在生产环境中实现低延迟、高可靠的数据同步。
建议根据实际场景选择合适的 CDC 方案，并建立完善的监控和错误处理机制。

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
**文档编号**: 03-03-TREND-28
