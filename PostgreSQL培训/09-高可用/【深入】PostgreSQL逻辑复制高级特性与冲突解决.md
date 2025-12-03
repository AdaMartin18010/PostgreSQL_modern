# 【深入】PostgreSQL逻辑复制高级特性与冲突解决

> **创建时间**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐⭐ 专家级
> **预计学习时间**: 1-2周

---

## 📑 目录

- [1. 逻辑复制进阶](#1-逻辑复制进阶)
- [2. 发布订阅高级用法](#2-发布订阅高级用法)
- [3. 冲突检测和解决](#3-冲突检测和解决)
- [4. 双向复制](#4-双向复制)
- [5. 逻辑复制监控](#5-逻辑复制监控)
- [6. 性能优化](#6-性能优化)
- [7. 完整生产案例](#7-完整生产案例)

---

## 1. 逻辑复制进阶

### 1.1 逻辑复制 vs 物理复制

| 特性 | 物理复制 | 逻辑复制 |
|------|---------|---------|
| **复制粒度** | 整个集群 | 表级别 |
| **跨版本** | ❌ 不支持 | ✅ 支持 |
| **选择性复制** | ❌ 全部复制 | ✅ 部分表 |
| **双向复制** | ❌ 单向 | ✅ 可以（需配置）|
| **DDL复制** | ✅ 自动 | ❌ 需手动 |
| **性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **延迟** | 极低（<1ms） | 低（<100ms）|
| **适用场景** | 完整备份、只读副本 | 部分同步、跨版本升级、数据集成 |

### 1.2 逻辑复制架构

```text
┌──────────────────┐         ┌──────────────────┐
│  Publisher DB    │         │  Subscriber DB   │
│                  │         │                  │
│  ┌────────────┐  │         │  ┌────────────┐  │
│  │ Publication│  │         │  │Subscription│  │
│  │  (Table A) │  │         │  │  (Table A) │  │
│  │  (Table B) │  │         │  │  (Table B) │  │
│  └─────┬──────┘  │         │  └─────▲──────┘  │
│        │         │         │        │         │
│        ▼         │         │        │         │
│  ┌────────────┐  │  Logical│  ┌────────────┐  │
│  │ WAL Sender │──┼─ Repl. ─┼─>│ WAL Receiver│ │
│  └────────────┘  │  Stream │  └────────────┘  │
│        ▲         │         │        │         │
│        │         │         │        ▼         │
│  ┌────────────┐  │         │  ┌────────────┐  │
│  │ Logical    │  │         │  │ Apply      │  │
│  │ Decoding   │  │         │  │ Worker     │  │
│  └────────────┘  │         │  └────────────┘  │
└──────────────────┘         └──────────────────┘
```

### 1.3 快速开始（15分钟）

**发布端配置**：

```sql
-- 1. 配置postgresql.conf
wal_level = logical
max_wal_senders = 10
max_replication_slots = 10

-- 重启PostgreSQL
-- sudo systemctl restart postgresql

-- 2. 创建复制用户
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'rep_password';

-- 3. 配置pg_hba.conf
-- host replication replicator 0.0.0.0/0 scram-sha-256

-- 4. 创建测试表
CREATE TABLE users (
    user_id serial PRIMARY KEY,
    username text UNIQUE NOT NULL,
    email text,
    created_at timestamptz DEFAULT now()
);

INSERT INTO users (username, email)
SELECT 'user_' || i, 'user' || i || '@example.com'
FROM generate_series(1, 10000) i;

-- 5. 创建发布
CREATE PUBLICATION my_pub FOR TABLE users;

-- 或发布所有表
-- CREATE PUBLICATION my_pub FOR ALL TABLES;

-- 或发布特定列
-- CREATE PUBLICATION my_pub FOR TABLE users (user_id, username);
```

**订阅端配置**：

```sql
-- 1. 创建相同结构的表
CREATE TABLE users (
    user_id serial PRIMARY KEY,
    username text UNIQUE NOT NULL,
    email text,
    created_at timestamptz DEFAULT now()
);

-- 2. 创建订阅
CREATE SUBSCRIPTION my_sub
    CONNECTION 'host=publisher_host port=5432 dbname=source_db user=replicator password=rep_password'
    PUBLICATION my_pub;

-- 3. 验证复制状态
SELECT * FROM pg_stat_subscription;

-- 4. 查看数据
SELECT COUNT(*) FROM users;  -- 应该是10000

-- 5. 测试实时复制
-- 在发布端插入数据
-- INSERT INTO users (username, email) VALUES ('new_user', 'new@example.com');

-- 在订阅端查询
-- SELECT * FROM users WHERE username = 'new_user';  -- 应该很快出现
```

---

## 2. 发布订阅高级用法

### 2.1 行过滤（Row Filter）

```sql
-- PostgreSQL 15+支持
-- 发布端：只发布活跃用户
CREATE PUBLICATION active_users_pub
FOR TABLE users
WHERE (is_active = true);

-- 订阅端
CREATE SUBSCRIPTION active_users_sub
    CONNECTION '...'
    PUBLICATION active_users_pub;

-- 只有is_active=true的用户会被复制
```

### 2.2 列过滤（Column Filter）

```sql
-- 发布端：只发布部分列（不包含敏感列）
CREATE PUBLICATION users_pub
FOR TABLE users (user_id, username, created_at);
-- 不包含email（敏感信息）

-- 订阅端表结构
CREATE TABLE users (
    user_id int PRIMARY KEY,
    username text,
    created_at timestamptz
);
-- 不需要email列

CREATE SUBSCRIPTION users_sub
    CONNECTION '...'
    PUBLICATION users_pub;
```

### 2.3 多个发布和订阅

```sql
-- 发布端：创建多个发布
CREATE PUBLICATION pub_users FOR TABLE users;
CREATE PUBLICATION pub_orders FOR TABLE orders;
CREATE PUBLICATION pub_products FOR TABLE products;

-- 订阅端：订阅多个发布
CREATE SUBSCRIPTION sub_all
    CONNECTION '...'
    PUBLICATION pub_users, pub_orders, pub_products;

-- 或者：多个订阅
CREATE SUBSCRIPTION sub_users
    CONNECTION '...'
    PUBLICATION pub_users;

CREATE SUBSCRIPTION sub_orders
    CONNECTION '...'
    PUBLICATION pub_orders;
```

### 2.4 级联复制

```sql
-- 架构：Publisher → Subscriber1 → Subscriber2

-- Publisher：创建发布
CREATE PUBLICATION my_pub FOR ALL TABLES;

-- Subscriber1：订阅并转发
-- 1. 订阅Publisher
CREATE SUBSCRIPTION sub_from_publisher
    CONNECTION 'host=publisher ...'
    PUBLICATION my_pub;

-- 2. 创建自己的发布
CREATE PUBLICATION my_pub_forwarded FOR ALL TABLES;

-- Subscriber2：订阅Subscriber1
CREATE SUBSCRIPTION sub_from_subscriber1
    CONNECTION 'host=subscriber1 ...'
    PUBLICATION my_pub_forwarded;
```

---

## 3. 冲突检测和解决

### 3.1 常见冲突类型

| 冲突类型 | 原因 | 默认行为 | 解决方案 |
|---------|------|---------|---------|
| **主键冲突** | INSERT冲突主键 | 停止复制 | on_error = skip |
| **UPDATE未找到** | UPDATE的行不存在 | 停止复制 | 检查数据一致性 |
| **DELETE未找到** | DELETE的行不存在 | 跳过 | 无需处理 |
| **CHECK约束** | 数据不满足约束 | 停止复制 | 调整约束或数据 |
| **外键约束** | 外键引用不存在 | 停止复制 | 先复制父表 |

### 3.2 冲突检测

```sql
-- 查看复制错误
SELECT
    subname,
    pid,
    received_lsn,
    latest_end_lsn,
    last_msg_send_time,
    last_msg_receipt_time,
    latest_end_time,
    (latest_end_time - last_msg_receipt_time) AS replication_lag
FROM pg_stat_subscription;

-- 查看详细错误
SELECT * FROM pg_subscription_rel WHERE srsubstate = 'd';  -- 'd' = 数据同步失败

-- 查看日志
SHOW log_directory;
-- tail -f /var/log/postgresql/postgresql-*.log | grep "logical replication"
```

### 3.3 冲突解决策略

**策略1：跳过冲突（适用于可容忍数据丢失）**

```sql
-- PostgreSQL 15+
ALTER SUBSCRIPTION my_sub SET (disable_on_error = false);
-- 遇到错误继续复制，跳过问题行

-- 查看被跳过的行
-- 需要在日志中查看
```

**策略2：手动解决冲突**

```sql
-- 步骤1：查看冲突详情（从日志）
-- 假设冲突：INSERT users (user_id=123, username='alice')
-- 错误：duplicate key value violates unique constraint "users_pkey"

-- 步骤2：在订阅端检查
SELECT * FROM users WHERE user_id = 123;

-- 步骤3：决策
-- 选项A：保留订阅端数据，跳过发布端数据
DELETE FROM users WHERE user_id = 123;  -- 然后复制会重新INSERT

-- 选项B：删除订阅端数据，使用发布端数据
-- （不需要操作，复制会失败，手动修复后继续）

-- 步骤4：重置订阅状态
ALTER SUBSCRIPTION my_sub ENABLE;
```

**策略3：使用触发器处理冲突**

```sql
-- 在订阅端创建冲突解决触发器
CREATE OR REPLACE FUNCTION resolve_user_conflict()
RETURNS trigger AS $$
BEGIN
    -- INSERT冲突：更新现有行
    ON CONFLICT (user_id) DO UPDATE SET
        username = EXCLUDED.username,
        email = EXCLUDED.email,
        updated_at = EXCLUDED.updated_at;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 但注意：逻辑复制不能直接使用ON CONFLICT
-- 需要在应用层或使用规则系统

-- 替代方案：使用RULE
CREATE RULE users_insert_conflict AS
    ON INSERT TO users
    WHERE EXISTS (SELECT 1 FROM users WHERE user_id = NEW.user_id)
    DO INSTEAD
        UPDATE users SET
            username = NEW.username,
            email = NEW.email
        WHERE user_id = NEW.user_id;
```

**策略4：时间戳冲突解决（Last-Write-Wins）**

```sql
-- 表结构（添加时间戳列）
CREATE TABLE users (
    user_id int PRIMARY KEY,
    username text,
    email text,
    updated_at timestamptz DEFAULT now()
);

-- 冲突解决规则
CREATE OR REPLACE FUNCTION lww_conflict_resolution()
RETURNS trigger AS $$
BEGIN
    -- 如果新数据更新时间更晚，则更新
    IF NEW.updated_at > OLD.updated_at THEN
        RETURN NEW;
    ELSE
        -- 保留旧数据
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER lww_trigger
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION lww_conflict_resolution();
```

---

## 4. 双向复制

### 4.1 双向复制配置

**需求**：两个数据中心，双向同步

```sql
-- 数据中心A（dc-a）
-- 1. 创建表
CREATE TABLE products (
    product_id int PRIMARY KEY,
    product_name text,
    price numeric,
    updated_at timestamptz DEFAULT now(),
    updated_from text DEFAULT 'dc-a'  -- 标识更新来源
);

-- 2. 创建发布
CREATE PUBLICATION pub_dc_a FOR TABLE products;

-- 3. 创建订阅（从dc-b）
CREATE SUBSCRIPTION sub_from_dc_b
    CONNECTION 'host=dc-b port=5432 dbname=mydb user=replicator password=xxx'
    PUBLICATION pub_dc_b;

-- 数据中心B（dc-b）
-- 相同配置，但方向相反
CREATE TABLE products (
    product_id int PRIMARY KEY,
    product_name text,
    price numeric,
    updated_at timestamptz DEFAULT now(),
    updated_from text DEFAULT 'dc-b'
);

CREATE PUBLICATION pub_dc_b FOR TABLE products;

CREATE SUBSCRIPTION sub_from_dc_a
    CONNECTION 'host=dc-a port=5432 dbname=mydb user=replicator password=xxx'
    PUBLICATION pub_dc_a;
```

**冲突处理（双向复制）**：

```sql
-- 方案1：基于时间戳（Last-Write-Wins）
CREATE OR REPLACE FUNCTION bidirectional_lww_trigger()
RETURNS trigger AS $$
DECLARE
    source_dc text;
BEGIN
    -- 获取复制来源
    source_dc := current_setting('application_name', true);

    -- 如果是从订阅来的更新
    IF source_dc LIKE 'sub_from_%' THEN
        -- 比较时间戳
        IF NEW.updated_at <= OLD.updated_at THEN
            -- 旧数据，不更新
            RETURN OLD;
        END IF;
    ELSE
        -- 本地更新，设置updated_from
        NEW.updated_from := 'dc-a';  -- 或dc-b
        NEW.updated_at := now();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bidirectional_trigger
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION bidirectional_lww_trigger();
```

**方案2：使用pglogical扩展（推荐）**

```bash
# 安装pglogical
sudo apt-get install postgresql-17-pglogical
```

```sql
-- 数据中心A
CREATE EXTENSION pglogical;

SELECT pglogical.create_node(
    node_name := 'dc_a',
    dsn := 'host=dc-a port=5432 dbname=mydb'
);

SELECT pglogical.create_replication_set(
    set_name := 'default',
    replicate_insert := true,
    replicate_update := true,
    replicate_delete := true,
    replicate_truncate := true
);

SELECT pglogical.replication_set_add_table(
    set_name := 'default',
    relation := 'products',
    synchronize_data := true
);

-- 订阅dc-b
SELECT pglogical.create_subscription(
    subscription_name := 'sub_dc_b',
    provider_dsn := 'host=dc-b port=5432 dbname=mydb user=replicator',
    replication_sets := ARRAY['default'],
    synchronize_structure := false,
    synchronize_data := true,
    forward_origins := ARRAY['all']  -- 转发所有来源的数据
);

-- 数据中心B（类似配置）
-- ...
```

---

## 5. 逻辑复制监控

### 5.1 监控复制延迟

```sql
-- 发布端：查看复制槽
SELECT
    slot_name,
    plugin,
    slot_type,
    database,
    active,
    restart_lsn,
    confirmed_flush_lsn,
    pg_current_wal_lsn() - confirmed_flush_lsn AS replication_lag_bytes,
    pg_size_pretty(pg_current_wal_lsn() - confirmed_flush_lsn) AS lag_size
FROM pg_replication_slots
WHERE slot_type = 'logical';

-- 订阅端：查看订阅状态
SELECT
    subname,
    pid,
    received_lsn,
    latest_end_lsn,
    last_msg_send_time,
    last_msg_receipt_time,
    latest_end_time,
    EXTRACT(EPOCH FROM (now() - latest_end_time)) AS lag_seconds
FROM pg_stat_subscription;

-- 详细的表级别状态
SELECT
    sr.srsubid,
    s.subname,
    sr.srrelid::regclass AS table_name,
    sr.srsubstate,  -- r=ready, d=data_sync, s=sync, i=init
    sr.srsublsn
FROM pg_subscription_rel sr
JOIN pg_subscription s ON sr.srsubid = s.oid;
```

### 5.2 监控WAL占用

```sql
-- 检查WAL堆积（复制槽占用）
SELECT
    slot_name,
    pg_size_pretty(
        pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)
    ) AS wal_retained,
    active
FROM pg_replication_slots
WHERE slot_type = 'logical'
ORDER BY pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) DESC;

-- 告警：WAL堆积超过10GB
SELECT
    slot_name,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) / 1024 / 1024 / 1024.0 AS wal_gb
FROM pg_replication_slots
WHERE slot_type = 'logical'
  AND pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 10737418240;  -- 10GB
```

### 5.3 复制性能监控

```sql
-- 查看复制worker状态
SELECT
    pid,
    application_name,
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication
WHERE application_name LIKE 'sub_%';

-- 查看apply worker统计
SELECT * FROM pg_stat_subscription_stats;
-- PostgreSQL 15+提供统计信息
```

---

## 6. 性能优化

### 6.1 批量应用优化

```sql
-- 订阅端配置
ALTER SUBSCRIPTION my_sub SET (streaming = on);  -- PostgreSQL 14+流式应用
ALTER SUBSCRIPTION my_sub SET (binary = true);   -- PostgreSQL 14+二进制格式
ALTER SUBSCRIPTION my_sub SET (parallel_apply_workers = 4);  -- PostgreSQL 16+并行应用

-- 发布端优化
ALTER SYSTEM SET wal_sender_timeout = '60s';
ALTER SYSTEM SET max_logical_replication_workers = 8;
SELECT pg_reload_conf();
```

### 6.2 大事务处理

```sql
-- 问题：大事务（如批量导入）导致复制延迟

-- 发布端：分批提交
DO $$
DECLARE
    batch_size int := 10000;
    total_rows int := 0;
BEGIN
    LOOP
        -- 插入一批
        WITH batch AS (
            INSERT INTO users (username, email)
            SELECT 'user_' || (1000000 + i), 'email' || i || '@example.com'
            FROM generate_series(total_rows + 1, total_rows + batch_size) i
            RETURNING *
        )
        SELECT COUNT(*) INTO batch_size FROM batch;

        EXIT WHEN batch_size = 0;

        total_rows := total_rows + batch_size;

        COMMIT;  -- 提交一批

        -- 限流
        PERFORM pg_sleep(0.1);
    END LOOP;
END $$;

-- 订阅端：调整配置
ALTER SUBSCRIPTION my_sub SET (streaming = on);  -- 流式应用大事务
```

### 6.3 初始数据同步优化

```sql
-- 方案1：禁用触发器和约束（同步期间）
ALTER TABLE users DISABLE TRIGGER ALL;
ALTER TABLE users ALTER CONSTRAINT users_pkey DEFERRABLE;

-- 创建订阅（copy_data = true）
CREATE SUBSCRIPTION my_sub
    CONNECTION '...'
    PUBLICATION my_pub
    WITH (copy_data = true);

-- 等待初始同步完成
SELECT * FROM pg_subscription_rel WHERE srsubstate != 'r';

-- 重新启用
ALTER TABLE users ENABLE TRIGGER ALL;

-- 方案2：使用pg_dump/restore（更快）
-- 1. 在发布端dump
pg_dump -h publisher -U postgres -t users --no-owner --no-acl -Fc > users.dump

-- 2. 在订阅端restore
pg_restore -h subscriber -U postgres -d mydb users.dump

-- 3. 创建订阅（不同步初始数据）
CREATE SUBSCRIPTION my_sub
    CONNECTION '...'
    PUBLICATION my_pub
    WITH (copy_data = false);  -- 不同步初始数据
```

---

## 7. 完整生产案例

### 7.1 案例：跨版本升级（PG 16 → PG 17）

**需求**：零停机升级PostgreSQL

**方案**：使用逻辑复制

```bash
# 步骤1：准备新服务器（PG 17）
sudo apt-get install postgresql-17
sudo -u postgres initdb -D /var/lib/postgresql/17/main

# 步骤2：在旧服务器（PG 16）创建发布
psql -U postgres <<EOF
-- 配置
ALTER SYSTEM SET wal_level = logical;
SELECT pg_reload_conf();

-- 创建发布
CREATE PUBLICATION upgrade_pub FOR ALL TABLES;

-- 创建复制用户
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'xxx';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO replicator;
EOF

# 步骤3：在新服务器（PG 17）创建结构
pg_dump -h old-server -U postgres --schema-only | psql -h new-server -U postgres

# 步骤4：创建订阅
psql -h new-server -U postgres <<EOF
CREATE SUBSCRIPTION upgrade_sub
    CONNECTION 'host=old-server port=5432 dbname=mydb user=replicator password=xxx'
    PUBLICATION upgrade_pub
    WITH (copy_data = true);
EOF

# 步骤5：等待初始同步完成
psql -h new-server -U postgres -c "
    SELECT
        COUNT(*) FILTER (WHERE srsubstate = 'r') AS ready_tables,
        COUNT(*) AS total_tables
    FROM pg_subscription_rel;
"

# 步骤6：监控复制延迟
watch -n 1 "psql -h new-server -U postgres -c \"
    SELECT
        subname,
        EXTRACT(EPOCH FROM (now() - latest_end_time)) AS lag_seconds
    FROM pg_stat_subscription;
\""

# 步骤7：等待延迟<1秒，切换应用
# 1. 停止写入旧服务器
# 2. 等待复制完全同步
# 3. 切换应用指向新服务器
# 4. 验证

# 步骤8：清理
psql -h new-server -U postgres -c "DROP SUBSCRIPTION upgrade_sub"
psql -h old-server -U postgres -c "DROP PUBLICATION upgrade_pub"
```

### 7.2 案例：数据汇总（多源到一个数据仓库）

**需求**：3个应用数据库→1个分析数据库

```sql
-- 数据仓库端
-- 1. 创建汇总表
CREATE TABLE dw_orders (
    source_db text NOT NULL,      -- 来源标识
    order_id bigint NOT NULL,
    order_date date,
    customer_id int,
    amount numeric,
    created_at timestamptz,
    PRIMARY KEY (source_db, order_id)
) PARTITION BY LIST (source_db);

-- 2. 为每个源创建分区
CREATE TABLE dw_orders_app1 PARTITION OF dw_orders FOR VALUES IN ('app1');
CREATE TABLE dw_orders_app2 PARTITION OF dw_orders FOR VALUES IN ('app2');
CREATE TABLE dw_orders_app3 PARTITION OF dw_orders FOR VALUES IN ('app3');

-- 3. 订阅所有源
CREATE SUBSCRIPTION sub_app1
    CONNECTION 'host=app1-db port=5432 dbname=app1 user=replicator password=xxx'
    PUBLICATION pub_orders
    WITH (
        origin = none,
        transform = 'add_column_default(source_db, ''app1'')'  -- 添加source_db列
    );

CREATE SUBSCRIPTION sub_app2
    CONNECTION 'host=app2-db ...'
    PUBLICATION pub_orders;

CREATE SUBSCRIPTION sub_app3
    CONNECTION 'host=app3-db ...'
    PUBLICATION pub_orders;

-- 4. 查询汇总数据
SELECT
    source_db,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount
FROM dw_orders
WHERE order_date >= current_date - 30
GROUP BY source_db;
```

### 7.3 案例：读写分离（逻辑复制）

```sql
-- 主库：所有表发布
CREATE PUBLICATION readonly_pub FOR ALL TABLES;

-- 只读副本1：订阅所有表
CREATE SUBSCRIPTION readonly_sub1
    CONNECTION 'host=primary port=5432 dbname=mydb user=replicator password=xxx'
    PUBLICATION readonly_pub
    WITH (
        copy_data = true,
        streaming = on,
        binary = true
    );

-- 只读副本2
CREATE SUBSCRIPTION readonly_sub2
    CONNECTION '...'
    PUBLICATION readonly_pub;

-- 应用层配置
-- 写操作 → primary
-- 读操作 → 负载均衡(readonly_sub1, readonly_sub2)
```

---

## 8. 高级场景

### 8.1 选择性复制（部分行、部分列）

```sql
-- 场景：只同步VIP客户的订单到数据仓库

-- 发布端
CREATE PUBLICATION vip_orders_pub
FOR TABLE orders
WHERE (
    customer_id IN (SELECT customer_id FROM vip_customers)
);

-- 订阅端
CREATE SUBSCRIPTION vip_orders_sub
    CONNECTION '...'
    PUBLICATION vip_orders_pub;

-- 只有VIP客户的订单会被复制
```

### 8.2 数据转换（Transform）

```sql
-- PostgreSQL 17+ 支持（规划中）
-- 当前版本可以使用触发器实现

-- 订阅端：数据转换触发器
CREATE OR REPLACE FUNCTION transform_orders()
RETURNS trigger AS $$
BEGIN
    -- 转换货币
    NEW.amount := NEW.amount * 6.8;  -- USD to CNY

    -- 脱敏
    NEW.customer_email := regexp_replace(NEW.customer_email, '(.{2})(.*)(@.*)', '\1***\3');

    -- 添加时间戳
    NEW.synced_at := now();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER transform_trigger
    BEFORE INSERT OR UPDATE ON orders
    FOR EACH ROW
    WHEN (pg_trigger_depth() = 1)  -- 只对复制触发
    EXECUTE FUNCTION transform_orders();
```

---

## 📚 参考资源

### 官方文档

1. [Logical Replication](https://www.postgresql.org/docs/current/logical-replication.html)
2. [Publication](https://www.postgresql.org/docs/current/sql-createpublication.html)
3. [Subscription](https://www.postgresql.org/docs/current/sql-createsubscription.html)

### 扩展和工具

1. [pglogical](https://github.com/2ndQuadrant/pglogical) - 增强的逻辑复制
2. [Bucardo](https://bucardo.org/) - 多主复制
3. [SymmetricDS](https://www.symmetricds.org/) - 数据库同步工具

### 最佳实践

1. [Logical Replication Best Practices](https://wiki.postgresql.org/wiki/Logical_Replication_Best_Practices)
2. [Conflict Resolution Strategies](https://www.postgresql.org/docs/current/logical-replication-conflicts.html)

---

**创建时间**: 2025年1月
**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**难度等级**: ⭐⭐⭐⭐⭐ 专家级

🔄 **掌握逻辑复制，实现灵活的数据同步！**
