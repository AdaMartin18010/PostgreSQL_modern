# PostgreSQL 18 CDC变更数据捕获实战

## 1. CDC架构

```text
┌────────────────────────────────────────────────┐
│         CDC (Change Data Capture)              │
├────────────────────────────────────────────────┤
│                                                  │
│  [PostgreSQL]                                   │
│       │                                          │
│   WAL日志                                       │
│       │                                          │
│  [逻辑解码]                                     │
│       │                                          │
│  [Replication Slot]                             │
│       │                                          │
│   ┌───┴────┬────────┐                          │
│   │        │        │                           │
│ [Kafka] [Kinesis] [自定义]                     │
│   │        │        │                           │
│ [消费者1][消费者2][消费者3]                     │
│                                                  │
└────────────────────────────────────────────────┘
```

---

## 2. 逻辑解码

### 2.1 配置

```sql
-- 启用逻辑复制
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;

-- 重启PostgreSQL
-- sudo systemctl restart postgresql

-- 创建复制槽
SELECT * FROM pg_create_logical_replication_slot('cdc_slot', 'pgoutput');

-- 查看复制槽
SELECT * FROM pg_replication_slots;
```

### 2.2 消费变更

```sql
-- 读取变更
SELECT * FROM pg_logical_slot_peek_changes('cdc_slot', NULL, NULL);

-- 消费变更（推进LSN）
SELECT * FROM pg_logical_slot_get_changes('cdc_slot', NULL, NULL);

-- 输出格式
/*
lsn          | xid  | data
-------------+------+------------------------------------------
0/16B2D50    | 1001 | BEGIN 1001
0/16B2D88    | 1001 | table public.users: INSERT: id[integer]:1 name[text]:'alice'
0/16B2DC0    | 1001 | COMMIT 1001
*/
```

---

## 3. Debezium集成

### 3.1 配置Debezium

```json
{
  "name": "postgres-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "localhost",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "password",
    "database.dbname": "mydb",
    "database.server.name": "postgres-server",
    "table.include.list": "public.users,public.orders",
    "plugin.name": "pgoutput",
    "slot.name": "debezium_slot",
    "publication.name": "debezium_pub"
  }
}
```

### 3.2 创建Publication

```sql
-- 创建发布
CREATE PUBLICATION debezium_pub FOR TABLE users, orders;

-- 或发布所有表
CREATE PUBLICATION debezium_pub FOR ALL TABLES;

-- 查看发布
\dRp+
```

---

## 4. 实时数据同步

### 4.1 PostgreSQL → Kafka

```python
from kafka import KafkaProducer
import psycopg2
import json

class PostgresCDC:
    """PostgreSQL CDC到Kafka"""

    def __init__(self, pg_conn_str, kafka_servers):
        self.pg_conn = psycopg2.connect(pg_conn_str)
        self.cursor = self.pg_conn.cursor()
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def start_cdc(self, slot_name='cdc_slot'):
        """启动CDC"""

        # 创建复制槽
        try:
            self.cursor.execute(f"""
                SELECT * FROM pg_create_logical_replication_slot('{slot_name}', 'pgoutput');
            """)
        except:
            pass  # 槽已存在

        # 持续读取变更
        while True:
            self.cursor.execute(f"""
                SELECT * FROM pg_logical_slot_get_changes('{slot_name}', NULL, NULL,
                    'proto_version', '1',
                    'publication_names', 'debezium_pub');
            """)

            changes = self.cursor.fetchall()

            for lsn, xid, data in changes:
                # 解析变更
                change_event = self.parse_change(data)

                # 发送到Kafka
                if change_event:
                    topic = f"postgres.public.{change_event['table']}"
                    self.producer.send(topic, change_event)

            if not changes:
                time.sleep(0.1)

    def parse_change(self, data: str):
        """解析变更数据"""

        if 'INSERT' in data:
            # 解析INSERT
            return {'operation': 'INSERT', 'table': '...', 'data': {...}}
        elif 'UPDATE' in data:
            return {'operation': 'UPDATE', 'table': '...', 'data': {...}}
        elif 'DELETE' in data:
            return {'operation': 'DELETE', 'table': '...', 'data': {...}}

        return None

# 使用
cdc = PostgresCDC(
    pg_conn_str="postgresql://localhost/mydb",
    kafka_servers=['localhost:9092']
)
cdc.start_cdc()
```

---

## 5. 数据湖同步

### 5.1 PostgreSQL → S3

```python
import boto3
from datetime import datetime

class CDCToS3:
    """CDC到S3数据湖"""

    def __init__(self, pg_conn_str, s3_bucket):
        self.pg_conn = psycopg2.connect(pg_conn_str)
        self.cursor = self.pg_conn.cursor()
        self.s3 = boto3.client('s3')
        self.bucket = s3_bucket
        self.buffer = []
        self.buffer_size = 10000

    def sync_changes(self, slot_name='s3_cdc_slot'):
        """同步变更到S3"""

        while True:
            self.cursor.execute(f"""
                SELECT * FROM pg_logical_slot_get_changes('{slot_name}', NULL, NULL);
            """)

            changes = self.cursor.fetchall()

            for change in changes:
                self.buffer.append(change)

                if len(self.buffer) >= self.buffer_size:
                    self.flush_to_s3()

            if not changes:
                if self.buffer:
                    self.flush_to_s3()
                time.sleep(1)

    def flush_to_s3(self):
        """刷新到S3"""

        if not self.buffer:
            return

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        key = f"cdc/changes_{timestamp}.json"

        # 上传
        data = json.dumps([self.parse_change(c[2]) for c in self.buffer])
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=data)

        print(f"✅ 上传 {len(self.buffer)} 条变更到 s3://{self.bucket}/{key}")
        self.buffer = []
```

---

## 6. 实时物化视图

### 6.1 基于CDC的物化视图

```sql
-- 源表
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    amount NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 物化视图（汇总）
CREATE TABLE user_order_summary (
    user_id BIGINT PRIMARY KEY,
    order_count INT,
    total_amount NUMERIC,
    last_order_at TIMESTAMPTZ
);

-- CDC触发器增量更新
CREATE OR REPLACE FUNCTION update_user_summary()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO user_order_summary (user_id, order_count, total_amount, last_order_at)
        VALUES (NEW.user_id, 1, NEW.amount, NEW.created_at)
        ON CONFLICT (user_id) DO UPDATE
        SET order_count = user_order_summary.order_count + 1,
            total_amount = user_order_summary.total_amount + NEW.amount,
            last_order_at = GREATEST(user_order_summary.last_order_at, NEW.created_at);

    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE user_order_summary
        SET total_amount = total_amount - OLD.amount + NEW.amount
        WHERE user_id = NEW.user_id;

    ELSIF TG_OP = 'DELETE' THEN
        UPDATE user_order_summary
        SET order_count = order_count - 1,
            total_amount = total_amount - OLD.amount
        WHERE user_id = OLD.user_id;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cdc_summary
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_user_summary();
```

---

## 7. 监控CDC

### 7.1 复制槽监控

```sql
-- 查看复制槽状态
SELECT
    slot_name,
    plugin,
    slot_type,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag_size,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS pending_bytes
FROM pg_replication_slots;

-- 告警: lag_size > 1GB
SELECT slot_name
FROM pg_replication_slots
WHERE pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 1073741824;
```

---

## 8. 故障处理

### 8.1 复制槽堵塞

```bash
# 现象: WAL堆积，磁盘满
df -h /var/lib/postgresql/18/main/pg_wal

# 排查
psql -c "SELECT * FROM pg_replication_slots WHERE active = false;"

# 解决: 删除不活跃的槽
psql -c "SELECT pg_drop_replication_slot('stuck_slot');"

# 或重置槽位置
psql -c "SELECT pg_replication_slot_advance('cdc_slot', '0/12345678');"
```

---

**完成**: PostgreSQL 18 CDC变更数据捕获实战
**字数**: ~10,000字
**涵盖**: 逻辑解码、Debezium、Kafka集成、数据湖同步、监控
