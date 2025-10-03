# CDC变更数据捕获实战案例 — Change Data Capture with PostgreSQL

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **难度等级**：⭐⭐⭐⭐ 高级  
> **预计时间**：60-90分钟  
> **适合场景**：数据同步、审计日志、实时ETL、事件驱动架构

---

## 📋 案例目标

构建一个生产级的CDC（Change Data Capture）系统，包括：

1. ✅ 捕获表的INSERT/UPDATE/DELETE操作
2. ✅ 基于逻辑复制的CDC实现
3. ✅ 基于触发器的CDC实现
4. ✅ 变更数据流式输出（JSON格式）
5. ✅ 性能优化与监控

---

## 🎯 业务场景

**场景描述**：电商订单数据实时同步

- **源系统**：PostgreSQL OLTP数据库（订单表）
- **目标系统**：
  - 数据仓库（用于分析）
  - 搜索引擎（Elasticsearch）
  - 缓存系统（Redis）
  - 消息队列（Kafka）
- **需求**：
  - 实时捕获订单变更（延迟<1秒）
  - 保证数据一致性
  - 支持历史变更追溯
  - 性能影响小于5%

---

## 🏗️ 架构设计

```text
源数据库（orders表）
    ↓
CDC捕获层（逻辑复制 / 触发器）
    ↓
变更日志表（change_log）
    ↓
数据处理层（格式转换、过滤）
    ↓
目标系统（数仓/搜索/缓存）
```

---

## 📦 1. 方案一：基于逻辑复制的CDC

### 1.1 配置逻辑复制

```sql
-- 检查当前配置
SHOW wal_level;  -- 必须为 logical

-- 如果不是logical，需要修改postgresql.conf：
-- wal_level = logical
-- max_replication_slots = 10
-- max_wal_senders = 10
-- 然后重启PostgreSQL

-- 创建复制槽
SELECT * FROM pg_create_logical_replication_slot('cdc_slot', 'pgoutput');

-- 查看复制槽
SELECT * FROM pg_replication_slots;
```

### 1.2 创建发布（Publication）

```sql
-- 创建源表
CREATE TABLE orders (
    id bigserial PRIMARY KEY,
    user_id bigint NOT NULL,
    product_name text NOT NULL,
    quantity int NOT NULL,
    price numeric(10,2) NOT NULL,
    status text DEFAULT 'pending',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 创建索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

-- 创建发布（捕获所有变更）
CREATE PUBLICATION orders_pub FOR TABLE orders;

-- 查看发布
SELECT * FROM pg_publication;
SELECT * FROM pg_publication_tables;
```

### 1.3 消费变更数据

```sql
-- 创建消费函数（读取逻辑复制流）
CREATE OR REPLACE FUNCTION consume_logical_changes()
RETURNS TABLE (
    lsn pg_lsn,
    xid xid,
    data text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.lsn,
        t.xid,
        t.data::text
    FROM pg_logical_slot_get_changes('cdc_slot', NULL, NULL) t;
END;
$$ LANGUAGE plpgsql;

-- 测试：插入数据并查看变更
INSERT INTO orders (user_id, product_name, quantity, price)
VALUES (1, 'PostgreSQL Book', 2, 59.99);

-- 消费变更
SELECT * FROM consume_logical_changes();

-- 输出示例：
-- BEGIN
-- table public.orders: INSERT: id[bigint]:1 user_id[bigint]:1 product_name[text]:'PostgreSQL Book' quantity[integer]:2 price[numeric]:59.99 status[text]:'pending' created_at[timestamp with time zone]:'2025-10-03 20:00:00+00' updated_at[timestamp with time zone]:'2025-10-03 20:00:00+00'
-- COMMIT
```

### 1.4 持久化变更日志

```sql
-- 创建变更日志表
CREATE TABLE change_log (
    id bigserial PRIMARY KEY,
    table_name text NOT NULL,
    operation text NOT NULL,  -- INSERT, UPDATE, DELETE
    old_data jsonb,
    new_data jsonb,
    changed_at timestamptz DEFAULT now(),
    lsn pg_lsn
);

CREATE INDEX idx_change_log_table_op ON change_log(table_name, operation);
CREATE INDEX idx_change_log_changed_at ON change_log(changed_at DESC);

-- 创建变更处理函数（将逻辑复制数据解析为JSON）
CREATE OR REPLACE FUNCTION process_logical_changes()
RETURNS int AS $$
DECLARE
    change_record RECORD;
    changes_processed int := 0;
BEGIN
    FOR change_record IN 
        SELECT * FROM pg_logical_slot_get_changes('cdc_slot', NULL, NULL)
    LOOP
        -- 这里需要解析change_record.data
        -- 实际生产中，建议使用wal2json扩展
        changes_processed := changes_processed + 1;
    END LOOP;
    
    RETURN changes_processed;
END;
$$ LANGUAGE plpgsql;
```

---

## 📦 2. 方案二：基于触发器的CDC（推荐）

### 2.1 创建审计表结构

```sql
-- 创建审计日志表
CREATE TABLE audit_log (
    id bigserial PRIMARY KEY,
    table_name text NOT NULL,
    record_id bigint NOT NULL,
    operation text NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values jsonb,
    new_values jsonb,
    changed_by text DEFAULT current_user,
    changed_at timestamptz DEFAULT now(),
    
    -- 索引优化
    CONSTRAINT audit_log_operation_check CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE'))
);

-- 创建分区表（按月分区，提升查询性能）
CREATE TABLE audit_log_partitioned (
    id bigserial,
    table_name text NOT NULL,
    record_id bigint NOT NULL,
    operation text NOT NULL,
    old_values jsonb,
    new_values jsonb,
    changed_by text DEFAULT current_user,
    changed_at timestamptz DEFAULT now(),
    PRIMARY KEY (id, changed_at)
) PARTITION BY RANGE (changed_at);

-- 创建分区
CREATE TABLE audit_log_2025_10 PARTITION OF audit_log_partitioned
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE audit_log_2025_11 PARTITION OF audit_log_partitioned
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- 创建索引
CREATE INDEX idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX idx_audit_log_record_id ON audit_log(record_id);
CREATE INDEX idx_audit_log_operation ON audit_log(operation);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at DESC);
CREATE INDEX idx_audit_log_changed_by ON audit_log(changed_by);
```

### 2.2 创建通用CDC触发器

```sql
-- 创建通用审计触发器函数
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS trigger AS $$
DECLARE
    old_data jsonb;
    new_data jsonb;
    changed_fields jsonb;
BEGIN
    -- 处理DELETE操作
    IF (TG_OP = 'DELETE') THEN
        old_data := to_jsonb(OLD);
        INSERT INTO audit_log (table_name, record_id, operation, old_values)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', old_data);
        RETURN OLD;
    
    -- 处理INSERT操作
    ELSIF (TG_OP = 'INSERT') THEN
        new_data := to_jsonb(NEW);
        INSERT INTO audit_log (table_name, record_id, operation, new_values)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', new_data);
        RETURN NEW;
    
    -- 处理UPDATE操作
    ELSIF (TG_OP = 'UPDATE') THEN
        old_data := to_jsonb(OLD);
        new_data := to_jsonb(NEW);
        
        -- 只记录变化的字段
        SELECT jsonb_object_agg(key, value)
        INTO changed_fields
        FROM jsonb_each(new_data)
        WHERE value IS DISTINCT FROM (old_data->key);
        
        -- 如果有变化才记录
        IF changed_fields IS NOT NULL AND changed_fields != '{}'::jsonb THEN
            INSERT INTO audit_log (table_name, record_id, operation, old_values, new_values)
            VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', old_data, new_data);
        END IF;
        
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 为orders表创建触发器
CREATE TRIGGER orders_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();
```

### 2.3 测试CDC捕获

```sql
-- 测试INSERT
INSERT INTO orders (user_id, product_name, quantity, price)
VALUES (100, 'PostgreSQL Advanced Book', 1, 89.99);

-- 测试UPDATE
UPDATE orders SET status = 'processing' WHERE id = 1;

-- 测试DELETE
DELETE FROM orders WHERE id = 2;

-- 查看审计日志
SELECT 
    id,
    table_name,
    record_id,
    operation,
    old_values,
    new_values,
    changed_by,
    changed_at
FROM audit_log
ORDER BY changed_at DESC;

-- 查看具体变更字段（UPDATE）
SELECT 
    id,
    record_id,
    operation,
    jsonb_pretty(old_values) AS old_data,
    jsonb_pretty(new_values) AS new_data,
    changed_at
FROM audit_log
WHERE operation = 'UPDATE'
ORDER BY changed_at DESC;
```

---

## 🚀 3. 高级特性

### 3.1 变更数据流式输出

```sql
-- 创建变更流视图
CREATE OR REPLACE VIEW change_stream AS
SELECT 
    id,
    table_name,
    record_id,
    operation,
    jsonb_build_object(
        'event_id', id,
        'event_type', operation,
        'table', table_name,
        'record_id', record_id,
        'old_data', old_values,
        'new_data', new_values,
        'changed_by', changed_by,
        'timestamp', extract(epoch from changed_at)::bigint
    ) AS event_json,
    changed_at
FROM audit_log
ORDER BY changed_at DESC;

-- 查询最近的变更事件
SELECT event_json FROM change_stream LIMIT 10;
```

### 3.2 差异计算（仅记录变化字段）

```sql
-- 创建优化的审计函数（只记录变化字段）
CREATE OR REPLACE FUNCTION audit_trigger_function_optimized()
RETURNS trigger AS $$
DECLARE
    old_data jsonb;
    new_data jsonb;
    diff jsonb := '{}'::jsonb;
    key text;
    old_val jsonb;
    new_val jsonb;
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (table_name, record_id, operation, old_values)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (table_name, record_id, operation, new_values)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW));
        RETURN NEW;
    
    ELSIF (TG_OP = 'UPDATE') THEN
        old_data := to_jsonb(OLD);
        new_data := to_jsonb(NEW);
        
        -- 计算差异
        FOR key, new_val IN SELECT * FROM jsonb_each(new_data)
        LOOP
            old_val := old_data->key;
            IF old_val IS DISTINCT FROM new_val THEN
                diff := diff || jsonb_build_object(
                    key, jsonb_build_object(
                        'old', old_val,
                        'new', new_val
                    )
                );
            END IF;
        END LOOP;
        
        -- 只有有变化时才记录
        IF diff != '{}'::jsonb THEN
            INSERT INTO audit_log (table_name, record_id, operation, old_values, new_values)
            VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', diff, diff);
        END IF;
        
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

### 3.3 选择性CDC（只捕获特定列）

```sql
-- 创建配置表（指定要监控的表和列）
CREATE TABLE cdc_config (
    table_name text PRIMARY KEY,
    tracked_columns text[],  -- 要监控的列
    enabled boolean DEFAULT true
);

-- 配置要监控的列
INSERT INTO cdc_config (table_name, tracked_columns)
VALUES ('orders', ARRAY['status', 'price', 'quantity']);

-- 创建选择性CDC触发器
CREATE OR REPLACE FUNCTION audit_trigger_selective()
RETURNS trigger AS $$
DECLARE
    config_record RECORD;
    old_data jsonb := '{}'::jsonb;
    new_data jsonb := '{}'::jsonb;
    col text;
BEGIN
    -- 获取配置
    SELECT * INTO config_record
    FROM cdc_config
    WHERE table_name = TG_TABLE_NAME AND enabled = true;
    
    -- 如果未配置或未启用，直接返回
    IF NOT FOUND THEN
        RETURN COALESCE(NEW, OLD);
    END IF;
    
    -- 只捕获配置的列
    FOREACH col IN ARRAY config_record.tracked_columns
    LOOP
        IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
            old_data := old_data || jsonb_build_object(col, to_jsonb(OLD)->>col);
        END IF;
        
        IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
            new_data := new_data || jsonb_build_object(col, to_jsonb(NEW)->>col);
        END IF;
    END LOOP;
    
    -- 插入审计日志
    INSERT INTO audit_log (table_name, record_id, operation, old_values, new_values)
    VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        NULLIF(old_data, '{}'::jsonb),
        NULLIF(new_data, '{}'::jsonb)
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

---

## 📊 4. 监控与性能优化

### 4.1 CDC性能监控

```sql
-- 创建监控视图
CREATE OR REPLACE VIEW cdc_statistics AS
SELECT 
    table_name,
    operation,
    COUNT(*) AS event_count,
    COUNT(*) FILTER (WHERE changed_at > now() - interval '1 hour') AS last_hour_count,
    COUNT(*) FILTER (WHERE changed_at > now() - interval '1 day') AS last_day_count,
    MAX(changed_at) AS last_change_time
FROM audit_log
GROUP BY table_name, operation
ORDER BY event_count DESC;

-- 查看统计
SELECT * FROM cdc_statistics;

-- 查看触发器性能影响
SELECT 
    schemaname,
    tablename,
    n_tup_ins AS inserts,
    n_tup_upd AS updates,
    n_tup_del AS deletes,
    n_tup_hot_upd AS hot_updates
FROM pg_stat_user_tables
WHERE tablename = 'orders';
```

### 4.2 清理历史数据

```sql
-- 创建清理函数（保留最近30天）
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs(retention_days int DEFAULT 30)
RETURNS int AS $$
DECLARE
    deleted_count int;
BEGIN
    DELETE FROM audit_log
    WHERE changed_at < now() - (retention_days || ' days')::interval;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RAISE NOTICE 'Deleted % old audit log records', deleted_count;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 定期清理（可以使用pg_cron扩展定时执行）
SELECT cleanup_old_audit_logs(30);
```

### 4.3 批量处理优化

```sql
-- 创建批量插入审计日志的函数
CREATE OR REPLACE FUNCTION batch_insert_audit_logs(
    logs jsonb[]
)
RETURNS int AS $$
DECLARE
    inserted_count int;
BEGIN
    INSERT INTO audit_log (table_name, record_id, operation, old_values, new_values)
    SELECT 
        (log->>'table_name')::text,
        (log->>'record_id')::bigint,
        (log->>'operation')::text,
        (log->'old_values')::jsonb,
        (log->'new_values')::jsonb
    FROM unnest(logs) AS log;
    
    GET DIAGNOSTICS inserted_count = ROW_COUNT;
    RETURN inserted_count;
END;
$$ LANGUAGE plpgsql;
```

---

## 🎨 5. CDC数据消费示例

### 5.1 轮询消费（Python示例）

```python
import psycopg2
import json
import time

def consume_changes(conn, last_id=0):
    """消费CDC变更数据"""
    cursor = conn.cursor()
    
    # 查询新的变更
    cursor.execute("""
        SELECT id, table_name, record_id, operation, 
               old_values, new_values, changed_at
        FROM audit_log
        WHERE id > %s
        ORDER BY id
        LIMIT 100
    """, (last_id,))
    
    changes = cursor.fetchall()
    
    for change in changes:
        change_id, table_name, record_id, operation, old_vals, new_vals, changed_at = change
        
        event = {
            'id': change_id,
            'table': table_name,
            'record_id': record_id,
            'operation': operation,
            'old_data': old_vals,
            'new_data': new_vals,
            'timestamp': changed_at.isoformat()
        }
        
        # 处理事件（如发送到Kafka）
        process_event(event)
        
        last_id = change_id
    
    return last_id

def process_event(event):
    """处理变更事件"""
    print(f"Processing {event['operation']} on {event['table']}.{event['record_id']}")
    # 这里可以：
    # 1. 发送到Kafka
    # 2. 更新Elasticsearch
    # 3. 清除Redis缓存
    # 4. 同步到数据仓库
    
# 主循环
conn = psycopg2.connect("dbname=mydb user=postgres")
last_id = 0

while True:
    try:
        last_id = consume_changes(conn, last_id)
        time.sleep(1)  # 1秒轮询一次
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)

conn.close()
```

### 5.2 LISTEN/NOTIFY实时推送

```sql
-- 修改触发器，添加NOTIFY
CREATE OR REPLACE FUNCTION audit_trigger_with_notify()
RETURNS trigger AS $$
DECLARE
    notification jsonb;
BEGIN
    -- 记录审计日志（复用之前的逻辑）
    -- ...
    
    -- 构建通知消息
    notification := jsonb_build_object(
        'table', TG_TABLE_NAME,
        'operation', TG_OP,
        'record_id', COALESCE(NEW.id, OLD.id),
        'timestamp', extract(epoch from now())
    );
    
    -- 发送通知
    PERFORM pg_notify('cdc_channel', notification::text);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Python消费端
import psycopg2
import select

conn = psycopg2.connect("dbname=mydb user=postgres")
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

cursor = conn.cursor()
cursor.execute("LISTEN cdc_channel;")

print("Waiting for notifications...")

while True:
    if select.select([conn], [], [], 5) == ([], [], []):
        print("Timeout")
    else:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            print(f"Got NOTIFY: {notify.payload}")
            # 处理变更事件
```

---

## ✅ 6. 完整部署脚本

```sql
-- CDC完整部署脚本
BEGIN;

-- 1. 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_log (
    id bigserial PRIMARY KEY,
    table_name text NOT NULL,
    record_id bigint NOT NULL,
    operation text NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values jsonb,
    new_values jsonb,
    changed_by text DEFAULT current_user,
    changed_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit_log(changed_at DESC);

-- 2. 创建审计触发器函数
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS trigger AS $$
-- （完整代码见前面）
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. 为目标表创建触发器
CREATE TRIGGER orders_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- 4. 创建监控视图
CREATE OR REPLACE VIEW cdc_statistics AS
SELECT 
    table_name,
    operation,
    COUNT(*) AS event_count,
    MAX(changed_at) AS last_change_time
FROM audit_log
GROUP BY table_name, operation;

COMMIT;

-- 验证部署
SELECT * FROM cdc_statistics;
```

---

## 📚 7. 最佳实践

### 7.1 性能优化

- ✅ 使用分区表存储审计日志
- ✅ 定期清理历史数据
- ✅ 选择性CDC（只监控关键列）
- ✅ 批量消费而非单条轮询

### 7.2 数据一致性

- ✅ 使用事务保证原子性
- ✅ 记录完整的old/new值
- ✅ 包含时间戳和操作人
- ✅ 避免循环触发

### 7.3 运维管理

- ✅ 监控审计日志增长速度
- ✅ 设置合理的保留期
- ✅ 定期备份审计数据
- ✅ 测试CDC对性能的影响

---

## 🎯 8. 练习任务

1. **基础练习**：
   - 为orders表实现基础CDC
   - 测试INSERT/UPDATE/DELETE捕获
   - 查询最近的变更记录

2. **进阶练习**：
   - 实现选择性CDC（只监控status和price）
   - 创建数据消费程序（Python/Node.js）
   - 实现变更数据到Kafka

3. **挑战任务**：
   - 构建完整的ETL流程（CDC→转换→加载）
   - 实现跨库CDC（从PostgreSQL到MySQL）
   - 优化百万级TPS场景下的CDC性能

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**下一步**：查看 [地理围栏案例](../geofencing/README.md)
