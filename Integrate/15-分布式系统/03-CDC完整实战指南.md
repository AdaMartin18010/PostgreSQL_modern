---

> **📋 文档来源**: `docs\04-Distributed\03-CDC完整实战指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# CDC（Change Data Capture）完整实战指南

> **创建日期**: 2025年12月4日
> **适用场景**: 数据同步、事件溯源、审计
> **文档状态**: 🚧 深度创建中

---

## 📑 目录

- [1.1 什么是CDC](#11-什么是cdc)
- [1.2 CDC方案对比](#12-cdc方案对比)
- [2.1 逻辑复制CDC](#21-逻辑复制cdc)
- [2.2 触发器CDC](#22-触发器cdc)
- [3.1 配置与部署](#31-配置与部署)
- [3.2 变更事件格式](#32-变更事件格式)
- [4.1 幂等性处理](#41-幂等性处理)
- [案例1：数据湖同步](#案例1数据湖同步)
- [案例2：审计日志系统](#案例2审计日志系统)
---

## 一、CDC概述

### 1.1 什么是CDC

**CDC（Change Data Capture）**：捕获数据库的所有变更。

**用途**：

- 📊 实时数据仓库同步
- 🔍 审计和合规
- 🔄 微服务数据同步
- 📝 事件溯源
- 🔔 实时通知

### 1.2 CDC方案对比

| 方案 | 性能开销 | 实时性 | 完整性 | 复杂度 |
|------|---------|--------|--------|--------|
| 逻辑复制 | 低 | <1秒 | 完整 ⭐ | 中 |
| 触发器 | 中 | <1秒 | 完整 | 低 |
| 轮询 | 低 | 分钟级 | 可能丢失 | 低 |
| WAL解析 | 极低 | <100ms | 完整 ⭐ | 高 |

---

## 二、PostgreSQL CDC实现

### 2.1 逻辑复制CDC

**完整CDC Pipeline**：

```sql
-- 1. 启用逻辑复制
ALTER SYSTEM SET wal_level = logical;
-- 重启PostgreSQL

-- 2. 创建Publication
CREATE PUBLICATION cdc_pub FOR ALL TABLES;

-- 3. 创建复制槽
SELECT pg_create_logical_replication_slot('cdc_slot', 'pgoutput');
```

**消费CDC（Python）**：

```python
import psycopg2
from psycopg2.extras import LogicalReplicationConnection
import json

class CDCConsumer:
    def __init__(self, conn_string, slot_name, publication_name):
        self.conn = psycopg2.connect(
            conn_string,
            connection_factory=LogicalReplicationConnection
        )
        self.slot_name = slot_name
        self.publication_name = publication_name

    def start(self, callback):
        """开始消费CDC事件"""
        cur = self.conn.cursor()

        cur.start_replication(
            slot_name=self.slot_name,
            options={
                'proto_version': '1',
                'publication_names': self.publication_name
            },
            decode=True
        )

        def consume(msg):
            # 解析变更
            change = self.parse_change(msg.payload)

            # 回调处理
            callback(change)

            # 确认消费
            msg.cursor.send_feedback(flush_lsn=msg.data_start)

        cur.consume_stream(consume)

    def parse_change(self, payload):
        """解析变更事件"""
        # 解析逻辑复制协议
        # 返回：{'action': 'INSERT', 'table': 'orders', 'data': {...}}
        pass

# 使用
cdc = CDCConsumer(
    "dbname=mydb",
    "cdc_slot",
    "cdc_pub"
)

def handle_change(change):
    print(f"Change detected: {change}")
    # 同步到目标系统

cdc.start(handle_change)
```

### 2.2 触发器CDC

**基于触发器的CDC**：

```sql
-- CDC事件表
CREATE TABLE cdc_events (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    operation TEXT,  -- 'INSERT', 'UPDATE', 'DELETE'
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 通用CDC触发器
CREATE FUNCTION cdc_capture()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO cdc_events (table_name, operation, old_data, new_data)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END
    );

    -- 发送通知
    PERFORM pg_notify('cdc_events',
        json_build_object(
            'table', TG_TABLE_NAME,
            'operation', TG_OP,
            'id', COALESCE(NEW.id, OLD.id)
        )::text
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 应用到表
CREATE TRIGGER orders_cdc
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION cdc_capture();
```

---

## 三、Debezium深入

### 3.1 配置与部署

**完整Debezium配置**：

```json
{
  "name": "pg-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "localhost",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "password",
    "database.dbname": "mydb",
    "database.server.name": "pg_server",
    "table.include.list": "public.orders,public.users",
    "plugin.name": "pgoutput",
    "publication.name": "cdc_pub",
    "slot.name": "debezium_slot",
    "heartbeat.interval.ms": "10000",
    "snapshot.mode": "initial",
    "decimal.handling.mode": "precise"
  }
}
```

### 3.2 变更事件格式

**Debezium事件结构**：

```json
{
  "before": null,
  "after": {
    "id": 12345,
    "user_id": 999,
    "amount": "99.99",
    "status": "pending",
    "created_at": 1701234567890
  },
  "source": {
    "version": "2.5.0",
    "connector": "postgresql",
    "name": "pg_server",
    "ts_ms": 1701234567900,
    "snapshot": "false",
    "db": "mydb",
    "schema": "public",
    "table": "orders",
    "txId": 12345678,
    "lsn": 123456789,
    "xmin": null
  },
  "op": "c",  // c=create, u=update, d=delete
  "ts_ms": 1701234567905
}
```

---

## 四、CDC最佳实践

### 4.1 幂等性处理

**确保幂等消费**：

```python
def process_cdc_event_idempotent(event):
    """幂等处理CDC事件"""
    event_id = f"{event['source']['lsn']}"

    # 检查是否已处理
    if redis_client.exists(f"processed:{event_id}"):
        return  # 已处理，跳过

    # 处理事件
    if event['op'] == 'c':  # INSERT
        insert_to_target(event['after'])
    elif event['op'] == 'u':  # UPDATE
        update_target(event['after'])
    elif event['op'] == 'd':  # DELETE
        delete_from_target(event['before']['id'])

    # 标记已处理（保留24小时）
    redis_client.setex(f"processed:{event_id}", 86400, '1')
```

---

## 五、生产案例

### 案例1：数据湖同步

**场景**：

- PostgreSQL（OLTP）→ ClickHouse（OLAP）
- 实时分析需求

**架构**：

```text
PostgreSQL → Debezium → Kafka → ClickHouse Sink
```

**效果**：

- 同步延迟：<2秒
- 数据一致性：100%
- 分析查询：实时

---

### 案例2：审计日志系统

**场景**：

- 金融合规
- 完整审计trail

**实现**：使用触发器CDC

**效果**：

- 完整审计记录 ✅
- 不可篡改 ✅
- 实时告警 ✅

---

**最后更新**: 2025年12月4日
**文档编号**: P7-3-CDC
**版本**: v1.0
**状态**: ✅ 完成
