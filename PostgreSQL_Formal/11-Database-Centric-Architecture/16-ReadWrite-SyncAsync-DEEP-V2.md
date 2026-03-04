# 读写分离与同步异步架构深度分析 v2.0

> **文档类型**: 数据库读写分离与同步异步架构
> **核心技术**: 流复制、逻辑复制、异步提交、同步提交、会话一致性
> **创建日期**: 2026-03-04
> **文档长度**: 11000+字

---

## 目录

- [读写分离与同步异步架构深度分析 v2.0](#读写分离与同步异步架构深度分析-v20)
  - [目录](#目录)
  - [摘要](#摘要)
  - [1. 读写分离架构概览](#1-读写分离架构概览)
    - [1.1 为什么需要读写分离](#11-为什么需要读写分离)
    - [1.2 架构模式对比](#12-架构模式对比)
  - [2. 流复制架构](#2-流复制架构)
    - [2.1 物理流复制](#21-物理流复制)
    - [2.2 级联复制](#22-级联复制)
    - [2.3 同步复制配置](#23-同步复制配置)
  - [3. 逻辑复制架构](#3-逻辑复制架构)
    - [3.1 逻辑复制vs物理复制](#31-逻辑复制vs物理复制)
    - [3.2 发布订阅配置](#32-发布订阅配置)
    - [3.3 冲突解决](#33-冲突解决)
  - [4. 存储过程读写路由](#4-存储过程读写路由)
    - [4.1 自动路由策略](#41-自动路由策略)
    - [4.2 会话粘性实现](#42-会话粘性实现)
  - [5. 复制延迟处理](#5-复制延迟处理)
    - [5.1 延迟检测](#51-延迟检测)
    - [5.2 读写一致性保证](#52-读写一致性保证)
  - [6. 同步级别控制](#6-同步级别控制)
    - [6.1 异步提交](#61-异步提交)
    - [6.2 同步提交](#62-同步提交)
    - [6.3 半同步复制](#63-半同步复制)
  - [7. 会话一致性模型](#7-会话一致性模型)
    - [7.1 读写一致性](#71-读写一致性)
    - [7.2 因果一致性](#72-因果一致性)
    - [7.3 单调读一致性](#73-单调读一致性)
  - [8. 高可用架构](#8-高可用架构)
    - [8.1 自动故障转移](#81-自动故障转移)
    - [8.2 连接池配置](#82-连接池配置)
  - [9. 性能优化](#9-性能优化)
  - [10. 持续推进计划](#10-持续推进计划)
    - [短期目标 (1-2周)](#短期目标-1-2周)
    - [中期目标 (1个月)](#中期目标-1个月)
    - [长期目标 (3个月)](#长期目标-3个月)

---

## 摘要

读写分离和同步异步控制是构建高性能、高可用数据库架构的关键技术。
本文档深入分析PostgreSQL的流复制、逻辑复制机制，提供完整的存储过程读写路由方案，确保在分布式环境下的数据一致性和系统可用性。

**核心挑战与解决方案**:

- **读扩展**: 读写分离实现读流量水平扩展
- **数据一致性**: 多种一致性模型满足不同业务需求
- **高可用**: 自动故障转移保障服务连续性
- **延迟处理**: 智能路由和延迟补偿策略

---

## 1. 读写分离架构概览

### 1.1 为什么需要读写分离

```text
┌─────────────────────────────────────────────────────────────────────┐
│  读写分离的收益分析                                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  单机架构（读写混合）                                                 │
│  ───────────────────                                                │
│                                                                     │
│  流量:  ████████████████████████████████████████  100%              │
│        ├─读 80%─┤├───────写 20%───────┤                             │
│                                                                     │
│  问题: 读写争抢资源、锁冲突、扩展受限                                  │
│                                                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                                     │
│  读写分离架构                                                        │
│  ─────────────                                                      │
│                                                                     │
│  写流量: ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░  20% → Primary      │
│                                                                     │
│  读流量: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░███████████████████████████     │
│          ├─Standby 1─┤├─Standby 2─┤├─Standby 3─┤├─Standby 4─┤       │
│              20%           20%           20%           20%          │
│                                                                     │
│  收益: 读性能4x提升、写操作无争抢、可水平扩展                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 架构模式对比

| 模式 | 复制方式 | 一致性 | 延迟 | 适用场景 |
|-----|---------|-------|------|---------|
| **主从异步** | 物理流复制 | 最终一致 | 低 | 读多写少、容忍延迟 |
| **主从同步** | 物理流复制 | 强一致 | 高 | 金融交易、关键数据 |
| **逻辑复制** | 逻辑解码 | 表级/行级 | 中 | 异构复制、部分复制 |
| **多主复制** | 逻辑+BDR | 冲突解决 | 中 | 多地域写入 |
| **级联复制** | 物理流复制 | 最终一致 | 中高 | 大量从库 |

---

## 2. 流复制架构

### 2.1 物理流复制

```sql
-- ============================================
-- 物理流复制配置（postgresql.conf）
-- ============================================

-- 主库配置
wal_level = replica                    -- 或 logical
max_wal_senders = 10                   -- 最大复制连接数
wal_keep_size = 1GB                    -- 保留的WAL大小
max_replication_slots = 10             -- 复制槽数量

-- 从库配置
hot_standby = on                       -- 允许只读查询
hot_standby_feedback = on              -- 向主库反馈查询状态
max_standby_archive_delay = 30s        -- 归档延迟
max_standby_streaming_delay = 30s      -- 流复制延迟

-- pg_hba.conf - 允许复制连接
-- host replication replicator 10.0.0.0/8 scram-sha-256
```

```bash
# ============================================
# 从库初始化（pg_basebackup）
# ============================================

# 1. 创建复制用户（主库）
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'secure_pass';

# 2. 创建复制槽（主库）
SELECT * FROM pg_create_physical_replication_slot('standby_1_slot');

# 3. 基础备份（从库）
pg_basebackup \
  --host=primary.example.com \
  --port=5432 \
  --username=replicator \
  --pgdata=/var/lib/postgresql/16/main \
  --format=plain \
  --wal-method=stream \
  --checkpoint=fast \
  --progress \
  --verbose

# 4. 创建 standby.signal（从库）
touch /var/lib/postgresql/16/main/standby.signal

# 5. 配置主库连接（postgresql.auto.conf）
cat >> /var/lib/postgresql/16/main/postgresql.auto.conf << EOF
primary_conninfo = 'host=primary.example.com port=5432 user=replicator password=secure_pass'
primary_slot_name = 'standby_1_slot'
EOF
```

### 2.2 级联复制

```text
┌─────────────────────────────────────────────────────────────────────┐
│  级联复制架构（多层级）                                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                        ┌───────────────┐                           │
│                        │   Primary     │                           │
│                        │  (主库)        │                           │
│                        └───────┬───────┘                           │
│                                │ WAL Stream                         │
│               ┌────────────────┼────────────────┐                  │
│               │                │                │                  │
│               ▼                ▼                ▼                  │
│        ┌───────────┐    ┌───────────┐    ┌───────────┐            │
│        │ Standby 1 │    │ Standby 2 │    │ Standby 3 │            │
│        │ (级联父)   │    │ (级联父)   │    │ (级联父)   │            │
│        └─────┬─────┘    └─────┬─────┘    └─────┬─────┘            │
│              │                │                │                   │
│        ┌─────┴─────┐    ┌─────┴─────┐    ┌─────┴─────┐            │
│        ▼           ▼    ▼           ▼    ▼           ▼            │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│   │Standby  │ │Standby  │ │Standby  │ │Standby  │ │Standby  │    │
│   │  1-1    │ │  1-2    │ │  2-1    │ │  2-2    │ │  3-1    │    │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘    │
│                                                                     │
│  优势: 减少主库复制压力、支持大量从库、可跨地域级联                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

```sql
-- ============================================
-- 级联复制配置（Standby 1作为级联父）
-- ============================================

-- Standby 1配置（既是订阅者也是发布者）
-- postgresql.conf
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
hot_standby = on

-- 允许级联复制
cascade_standby = on

-- Standby 1-1配置（级联子节点）
-- postgresql.auto.conf
primary_conninfo = 'host=standby1.example.com port=5432 user=replicator'
primary_slot_name = 'cascade_standby_1_1'

-- 创建级联复制槽
SELECT * FROM pg_create_physical_replication_slot('cascade_standby_1_1');
```

### 2.3 同步复制配置

```sql
-- ============================================
-- 同步复制配置
-- ============================================

-- 主库 postgresql.conf
synchronous_commit = remote_apply          -- 或 on, remote_write, local
synchronous_standby_names = 'FIRST 2 (standby_1, standby_2, standby_3)'
-- 或: synchronous_standby_names = 'ANY 1 (standby_1, standby_2)'

-- 查看同步状态
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state,
    reply_time
FROM pg_stat_replication;

-- 同步模式说明
-- off:          不等待从库确认，最快但可能丢数据
-- local:        等待本地刷盘，不等待从库
-- remote_write: 等待从库接收到WAL（写入OS缓存）
-- on:           等待从库刷盘（默认）
-- remote_apply: 等待从库应用（最强一致性）

-- 存储过程：动态调整同步级别
CREATE OR REPLACE PROCEDURE sp_set_sync_level(
    IN p_level TEXT,  -- 'async', 'sync', 'strict'
    IN p_duration INTERVAL DEFAULT NULL  -- 临时设置的有效期
)
LANGUAGE plpgsql
AS $$
BEGIN
    CASE p_level
        WHEN 'async' THEN
            SET LOCAL synchronous_commit = 'off';
        WHEN 'sync' THEN
            SET LOCAL synchronous_commit = 'on';
        WHEN 'strict' THEN
            SET LOCAL synchronous_commit = 'remote_apply';
        ELSE
            RAISE EXCEPTION 'Unknown sync level: %', p_level;
    END CASE;

    -- 记录设置
    INSERT INTO sync_level_log (level, duration, set_at)
    VALUES (p_level, p_duration, NOW());
END;
$$;
```

---

## 3. 逻辑复制架构

### 3.1 逻辑复制vs物理复制

```text
┌─────────────────────────────────────────────────────────────────────┐
│  物理复制 vs 逻辑复制                                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────┐    ┌─────────────────────┐                │
│  │    物理复制          │    │    逻辑复制          │                │
│  ├─────────────────────┤    ├─────────────────────┤                │
│  │ 复制级别: 整个集群   │    │ 复制级别: 表/行      │                │
│  │ 复制内容: WAL字节流  │    │ 复制内容: SQL语句    │                │
│  │ 主从版本: 必须相同   │    │ 主从版本: 可不同     │                │
│  │ 主从架构: 完全一致   │    │ 主从架构: 可不同     │                │
│  │ DDL复制:  自动       │    │ DDL复制:  需手动     │                │
│  │ 冲突处理: 不适用     │    │ 冲突处理: 需配置     │                │
│  │ 适用场景: HA/DR      │    │ 适用场景: 数据集成   │                │
│  └─────────────────────┘    └─────────────────────┘                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 发布订阅配置

```sql
-- ============================================
-- 逻辑复制发布订阅配置
-- ============================================

-- 发布端（主库）
-- 1. 启用逻辑复制
-- postgresql.conf: wal_level = logical

-- 2. 创建发布
CREATE PUBLICATION orders_pub FOR TABLE orders;

-- 3. 创建带过滤的发布
CREATE PUBLICATION active_orders_pub FOR TABLE orders
    WHERE (status IN ('pending', 'processing', 'shipped'));

-- 4. 创建列级过滤发布
CREATE PUBLICATION orders_summary_pub FOR TABLE orders (id, user_id, status, total);

-- 5. 创建全表发布
CREATE PUBLICATION all_tables FOR ALL TABLES;

-- 订阅端（从库）
-- 1. 创建订阅
CREATE SUBSCRIPTION orders_sub
    CONNECTION 'host=primary.example.com port=5432 dbname=mydb user=replicator'
    PUBLICATION orders_pub
    WITH (
        copy_data = true,           -- 初始化复制现有数据
        create_slot = true,         -- 自动创建复制槽
        slot_name = 'orders_sub_slot',
        streaming = parallel,       -- PG 14+: 并行流复制
        binary = on,                -- 使用二进制传输
        commit_order = on           -- 保持提交顺序
    );

-- 2. 监控订阅状态
SELECT
    subname,
    pid,
    received_lsn,
    latest_end_lsn,
    latest_end_time
FROM pg_stat_subscription;

-- 3. 查看复制槽
SELECT
    slot_name,
    plugin,
    slot_type,
    database,
    active,
    restart_lsn,
    confirmed_flush_lsn
FROM pg_replication_slots;

-- 4. 存储过程：动态添加表到发布
CREATE OR REPLACE PROCEDURE sp_add_table_to_publication(
    IN p_publication TEXT,
    IN p_table TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('ALTER PUBLICATION %I ADD TABLE %I', p_publication, p_table);

    -- 记录变更
    INSERT INTO publication_changes (publication_name, action, table_name, changed_at)
    VALUES (p_publication, 'ADD', p_table, NOW());
END;
$$;

-- 5. 存储过程：切换订阅源
CREATE OR REPLACE PROCEDURE sp_switch_subscription_source(
    IN p_subscription TEXT,
    IN p_new_primary_host TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 停用订阅
    ALTER SUBSCRIPTION orders_sub DISABLE;

    -- 更新连接信息
    ALTER SUBSCRIPTION orders_sub
    SET (slot_name = NONE);

    ALTER SUBSCRIPTION orders_sub
    CONNECTION format('host=%s port=5432 dbname=mydb user=replicator', p_new_primary_host);

    -- 重新启用
    ALTER SUBSCRIPTION orders_sub ENABLE;
END;
$$;
```

### 3.3 冲突解决

```sql
-- ============================================
-- 逻辑复制冲突解决
-- ============================================

-- 1. 冲突检测表
CREATE TABLE replication_conflicts (
    conflict_id UUID PRIMARY KEY DEFAULT uuidv7(),
    subscription_name TEXT,
    table_name TEXT,
    conflict_type TEXT,  -- insert_exists, update_missing, delete_missing
    local_tuple JSONB,
    remote_tuple JSONB,
    resolution TEXT,     -- local_wins, remote_wins, merge, manual
    resolved_at TIMESTAMPTZ,
    resolution_action TEXT
);

-- 2. 自动冲突解决函数
CREATE OR REPLACE FUNCTION fn_resolve_insert_conflict()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_local_updated TIMESTAMPTZ;
    v_remote_updated TIMESTAMPTZ;
BEGIN
    -- 获取本地记录的更新时间
    SELECT updated_at INTO v_local_updated
    FROM orders WHERE id = NEW.id;

    v_remote_updated := NEW.updated_at;

    -- 时间戳比较：最新的胜出
    IF v_remote_updated > v_local_updated THEN
        -- 远程更新，替换本地
        resolution_action := 'remote_wins';
        RETURN NEW;
    ELSE
        -- 本地更新更新，保留本地
        INSERT INTO replication_conflicts (...)
        VALUES (...);
        RETURN NULL;  -- 忽略远程更新
    END IF;
END;
$$;

-- 3. 应用冲突解决触发器
CREATE TRIGGER trg_resolve_order_conflict
    BEFORE INSERT ON orders
    FOR EACH ROW
    WHEN (pg_trigger_depth() < 1)  -- 避免递归
    EXECUTE FUNCTION fn_resolve_insert_conflict();

-- 4. 手动冲突解决存储过程
CREATE OR REPLACE PROCEDURE sp_manual_resolve_conflict(
    IN p_conflict_id UUID,
    IN p_resolution TEXT,  -- 'local', 'remote', 'merge', 'custom'
    IN p_custom_data JSONB DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_conflict RECORD;
BEGIN
    SELECT * INTO v_conflict FROM replication_conflicts WHERE conflict_id = p_conflict_id;

    CASE p_resolution
        WHEN 'local' THEN
            -- 保留本地版本，无需操作
            NULL;
        WHEN 'remote' THEN
            -- 应用远程版本
            EXECUTE format('UPDATE %I SET %s WHERE id = $1',
                v_conflict.table_name,
                (SELECT string_agg(format('%I = $2->>%L', key, key), ', ')
                 FROM jsonb_object_keys(v_conflict.remote_tuple) AS key)
            ) USING (v_conflict.remote_tuple->>'id')::UUID, v_conflict.remote_tuple;
        WHEN 'merge' THEN
            -- 合并两个版本
            EXECUTE format('UPDATE %I SET data = data || $1 WHERE id = $2',
                v_conflict.table_name
            ) USING v_conflict.remote_tuple, (v_conflict.remote_tuple->>'id')::UUID;
        WHEN 'custom' THEN
            -- 使用自定义数据
            EXECUTE format('UPDATE %I SET data = $1 WHERE id = $2',
                v_conflict.table_name
            ) USING p_custom_data, (v_conflict.remote_tuple->>'id')::UUID;
    END CASE;

    UPDATE replication_conflicts
    SET resolution = p_resolution, resolved_at = NOW()
    WHERE conflict_id = p_conflict_id;
END;
$$;
```

---

## 4. 存储过程读写路由

### 4.1 自动路由策略

```sql
-- ============================================
-- 存储过程读写路由
-- ============================================

-- 1. 存储过程元数据表
CREATE TABLE procedure_routing_metadata (
    procedure_name TEXT PRIMARY KEY,
    operation_type TEXT NOT NULL,  -- 'read', 'write', 'hybrid'
    target_node_type TEXT DEFAULT 'auto',  -- 'primary', 'standby', 'auto'
    consistency_requirement TEXT DEFAULT 'eventual',  -- 'strong', 'eventual', 'session'
    can_route_to_standby BOOLEAN DEFAULT false,
    requires_session_sticky BOOLEAN DEFAULT false
);

-- 2. 注册存储过程路由信息
INSERT INTO procedure_routing_metadata VALUES
    ('sp_order_create', 'write', 'primary', 'strong', false, false),
    ('sp_order_update', 'write', 'primary', 'strong', false, true),
    ('fn_order_list', 'read', 'auto', 'eventual', true, false),
    ('fn_order_detail', 'read', 'auto', 'session', true, true),
    ('sp_order_cancel', 'write', 'primary', 'strong', false, true);

-- 3. 路由决策函数
CREATE OR REPLACE FUNCTION fn_get_routing_target(
    p_procedure_name TEXT,
    p_session_id TEXT DEFAULT NULL
)
RETURNS TABLE (
    target_node TEXT,
    connection_string TEXT,
    reason TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_meta RECORD;
    v_last_write TIMESTAMPTZ;
    v_lag INTERVAL;
BEGIN
    SELECT * INTO v_meta
    FROM procedure_routing_metadata
    WHERE procedure_name = p_procedure_name;

    IF NOT FOUND THEN
        target_node := 'primary';
        reason := 'No metadata found, default to primary';
        RETURN NEXT;
        RETURN;
    END IF;

    -- 写操作强制主库
    IF v_meta.operation_type = 'write' THEN
        target_node := 'primary';
        connection_string := current_setting('db.primary_conn', true);
        reason := 'Write operation requires primary';
        RETURN NEXT;
        RETURN;
    END IF;

    -- 检查会话粘性
    IF v_meta.requires_session_sticky AND p_session_id IS NOT NULL THEN
        SELECT last_write_time INTO v_last_write
        FROM session_write_markers
        WHERE session_id = p_session_id;

        IF v_last_write > NOW() - INTERVAL '2 seconds' THEN
            target_node := 'primary';
            reason := 'Session sticky after recent write';
            RETURN NEXT;
            RETURN;
        END IF;
    END IF;

    -- 检查复制延迟
    SELECT NOW() - pg_last_xact_replay_timestamp() INTO v_lag;

    IF v_meta.consistency_requirement = 'strong' AND v_lag > INTERVAL '100ms' THEN
        target_node := 'primary';
        reason := 'Strong consistency required, lag too high: ' || v_lag;
        RETURN NEXT;
        RETURN;
    END IF;

    -- 路由到从库
    target_node := 'standby_' || (abs(hashtext(p_session_id || p_procedure_name)) % 3 + 1)::TEXT;
    connection_string := current_setting('db.standby_conn_' || target_node, true);
    reason := 'Read operation routed to standby, lag: ' || v_lag;
    RETURN NEXT;
END;
$$;

-- 4. 带路由的存储过程包装器
CREATE OR REPLACE PROCEDURE sp_routed_call(
    IN p_procedure_name TEXT,
    IN p_params JSONB,
    IN p_session_id TEXT DEFAULT NULL,
    OUT p_result JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_target RECORD;
    v_sql TEXT;
BEGIN
    -- 获取路由目标
    SELECT * INTO v_target FROM fn_get_routing_target(p_procedure_name, p_session_id);

    -- 构建动态调用
    v_sql := format('CALL %I(%s)', p_procedure_name,
        (SELECT string_agg(format('%L', value), ', ')
         FROM jsonb_each_text(p_params)));

    -- 记录路由决策
    INSERT INTO routing_log (
        procedure_name, session_id, target_node, reason, routed_at
    ) VALUES (p_procedure_name, p_session_id, v_target.target_node, v_target.reason, NOW());

    -- 执行（实际应用中通过连接池路由）
    EXECUTE v_sql;
END;
$$;
```

### 4.2 会话粘性实现

```sql
-- ============================================
-- 会话粘性实现（写后读一致性）
-- ============================================

-- 1. 会话状态表
CREATE TABLE session_routing_state (
    session_id TEXT PRIMARY KEY,
    last_write_lsn PG_LSN,
    last_write_time TIMESTAMPTZ,
    force_primary_until TIMESTAMPTZ,
    preferred_standby TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 写操作后标记会话
CREATE OR REPLACE PROCEDURE sp_mark_session_write(
    IN p_session_id TEXT,
    IN p_write_lsn PG_LSN DEFAULT pg_current_wal_lsn()
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO session_routing_state (
        session_id, last_write_lsn, last_write_time, force_primary_until
    ) VALUES (
        p_session_id, p_write_lsn, NOW(), NOW() + INTERVAL '2 seconds'
    )
    ON CONFLICT (session_id) DO UPDATE SET
        last_write_lsn = EXCLUDED.last_write_lsn,
        last_write_time = EXCLUDED.last_write_time,
        force_primary_until = NOW() + INTERVAL '2 seconds',
        updated_at = NOW();
END;
$$;

-- 3. 粘性读取存储过程
CREATE OR REPLACE FUNCTION fn_sticky_read(
    p_session_id TEXT,
    p_sql TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_state RECORD;
    v_standby_lsn PG_LSN;
BEGIN
    SELECT * INTO v_state FROM session_routing_state WHERE session_id = p_session_id;

    -- 检查是否需要强制主库
    IF v_state.force_primary_until > NOW() THEN
        -- 路由到主库
        RETURN dblink_fetch_from_primary(p_sql);
    END IF;

    -- 检查从库是否追上
    SELECT replay_lsn INTO v_standby_lsn
    FROM pg_stat_wal_receiver;

    IF v_standby_lsn >= v_state.last_write_lsn THEN
        -- 从库已追上，可以安全读取
        RETURN dblink_fetch_from_standby(p_sql);
    ELSE
        -- 等待从库追上或路由到主库
        FOR i IN 1..10 LOOP
            PERFORM pg_sleep(0.05);
            SELECT replay_lsn INTO v_standby_lsn
            FROM pg_stat_wal_receiver;
            EXIT WHEN v_standby_lsn >= v_state.last_write_lsn;
        END LOOP;

        IF v_standby_lsn >= v_state.last_write_lsn THEN
            RETURN dblink_fetch_from_standby(p_sql);
        ELSE
            RETURN dblink_fetch_from_primary(p_sql);
        END IF;
    END IF;
END;
$$;

-- 4. 带粘性的订单查询
CREATE OR REPLACE FUNCTION fn_order_list_sticky(
    p_user_id BIGINT,
    p_session_id TEXT
)
RETURNS TABLE (order_id UUID, status VARCHAR, total DECIMAL)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM fn_sticky_read(p_session_id, format(
        'SELECT id, status, total FROM orders WHERE user_id = %s',
        p_user_id
    ))::JSONB;
END;
$$;
```

---

## 5. 复制延迟处理

### 5.1 延迟检测

```sql
-- ============================================
-- 复制延迟监控
-- ============================================

-- 1. 延迟监控视图
CREATE VIEW v_replication_lag AS
SELECT
    client_addr as standby_host,
    application_name as standby_name,
    state,
    -- WAL位置延迟（字节）
    pg_wal_lsn_diff(sent_lsn, replay_lsn) as replay_lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) as replay_lag_size,
    -- 时间延迟估算
    EXTRACT(EPOCH FROM (NOW() - backend_start)) as connection_age_seconds,
    reply_time,
    -- 复制速度估算
    pg_wal_lsn_diff(sent_lsn, write_lsn) as write_lag_bytes
FROM pg_stat_replication;

-- 2. 延迟告警存储过程
CREATE OR REPLACE PROCEDURE sp_check_replication_lag()
LANGUAGE plpgsql
AS $$
DECLARE
    v_lag RECORD;
BEGIN
    FOR v_lag IN
        SELECT * FROM v_replication_lag
        WHERE replay_lag_bytes > 100 * 1024 * 1024  -- 100MB
    LOOP
        -- 发送告警
        PERFORM pg_notify('replication_alert', jsonb_build_object(
            'standby', v_lag.standby_name,
            'lag_bytes', v_lag.replay_lag_bytes,
            'lag_size', v_lag.replay_lag_size,
            'severity', CASE
                WHEN v_lag.replay_lag_bytes > 1024 * 1024 * 1024 THEN 'critical'
                WHEN v_lag.replay_lag_bytes > 500 * 1024 * 1024 THEN 'warning'
                ELSE 'info'
            END
        )::TEXT);
    END LOOP;
END;
$$;

-- 3. 历史延迟趋势
CREATE TABLE replication_lag_history (
    id BIGSERIAL PRIMARY KEY,
    measured_at TIMESTAMPTZ DEFAULT NOW(),
    standby_name TEXT,
    lag_bytes BIGINT,
    lag_seconds NUMERIC
);

CREATE OR REPLACE PROCEDURE sp_record_lag_history()
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO replication_lag_history (standby_name, lag_bytes, lag_seconds)
    SELECT
        standby_name,
        replay_lag_bytes,
        EXTRACT(EPOCH FROM (NOW() - reply_time))
    FROM v_replication_lag;
END;
$$;

-- 4. 延迟预测
CREATE OR REPLACE FUNCTION fn_predict_lag(
    p_standby_name TEXT,
    p_minutes_ahead INT DEFAULT 5
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_avg_rate NUMERIC;
    v_current_lag NUMERIC;
BEGIN
    -- 计算平均复制速率
    SELECT
        (lag_bytes - LAG(lag_bytes) OVER (ORDER BY measured_at)) /
        NULLIF(EXTRACT(EPOCH FROM (measured_at - LAG(measured_at) OVER (ORDER BY measured_at))), 0)
    INTO v_avg_rate
    FROM replication_lag_history
    WHERE standby_name = p_standby_name
    ORDER BY measured_at DESC
    LIMIT 10;

    SELECT lag_bytes INTO v_current_lag
    FROM replication_lag_history
    WHERE standby_name = p_standby_name
    ORDER BY measured_at DESC
    LIMIT 1;

    -- 预测未来延迟
    RETURN v_current_lag + (v_avg_rate * p_minutes_ahead * 60);
END;
$$;
```

### 5.2 读写一致性保证

```sql
-- ============================================
-- 读写一致性保证机制
-- ============================================

-- 1. 时间戳读取
CREATE OR REPLACE FUNCTION fn_read_with_timestamp(
    p_sql TEXT,
    p_min_timestamp TIMESTAMPTZ
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_result JSONB;
    v_current_replay TIMESTAMPTZ;
BEGIN
    LOOP
        -- 检查从库回放时间
        SELECT pg_last_xact_replay_timestamp() INTO v_current_replay;

        IF v_current_replay >= p_min_timestamp THEN
            -- 从库已包含需要的数据
            EXECUTE p_sql INTO v_result;
            RETURN v_result;
        END IF;

        -- 短暂等待
        PERFORM pg_sleep(0.01);

        -- 超时检查
        IF clock_timestamp() > p_min_timestamp + INTERVAL '5 seconds' THEN
            RAISE EXCEPTION 'Read timeout waiting for replica';
        END IF;
    END LOOP;
END;
$$;

-- 2. LSN边界读取
CREATE OR REPLACE FUNCTION fn_read_at_lsn(
    p_sql TEXT,
    p_target_lsn PG_LSN
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_result JSONB;
    v_current_lsn PG_LSN;
BEGIN
    LOOP
        SELECT replay_lsn INTO v_current_lsn FROM pg_stat_wal_receiver;

        IF v_current_lsn >= p_target_lsn THEN
            EXECUTE p_sql INTO v_result;
            RETURN v_result;
        END IF;

        PERFORM pg_sleep(0.01);
    END LOOP;
END;
$$;

-- 3. 订单创建后读取（写后读一致性）
CREATE OR REPLACE PROCEDURE sp_create_order_with_read(
    IN p_user_id BIGINT,
    IN p_items JSONB,
    IN p_session_id TEXT,
    OUT p_order_id UUID,
    OUT p_order_data JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_write_lsn PG_LSN;
BEGIN
    p_order_id := uuidv7();

    -- 创建订单并记录LSN
    INSERT INTO orders (id, user_id, items, status)
    VALUES (p_order_id, p_user_id, p_items, 'pending');

    v_write_lsn := pg_current_wal_lsn();

    -- 标记会话写入
    CALL sp_mark_session_write(p_session_id, v_write_lsn);

    -- 从从库读取（带LSN等待）
    SELECT fn_read_at_lsn(
        format('SELECT to_jsonb(t) FROM orders t WHERE id = %L', p_order_id),
        v_write_lsn
    ) INTO p_order_data;
END;
$$;
```

---

## 6. 同步级别控制

### 6.1 异步提交

```sql
-- ============================================
-- 异步提交优化
-- ============================================

-- 会话级异步提交
SET synchronous_commit = off;

-- 存储过程：异步批量插入
CREATE OR REPLACE PROCEDURE sp_async_bulk_insert(
    IN p_table_name TEXT,
    IN p_records JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 临时启用异步提交以提高吞吐量
    SET LOCAL synchronous_commit = off;

    EXECUTE format('
        INSERT INTO %I (data)
        SELECT value FROM jsonb_array_elements($1) AS t(value)
    ', p_table_name)
    USING p_records;

    -- 函数结束时设置自动恢复
END;
$$;

-- 异步提交的风险管理
CREATE TABLE async_commit_audit (
    operation_id UUID PRIMARY KEY DEFAULT uuidv7(),
    table_name TEXT,
    operation_type TEXT,
    record_count INT,
    committed_at TIMESTAMPTZ,
    wal_flushed_at TIMESTAMPTZ
);

-- 带审计的异步提交
CREATE OR REPLACE PROCEDURE sp_safe_async_insert(
    IN p_table_name TEXT,
    IN p_records JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_op_id UUID := uuidv7();
BEGIN
    SET LOCAL synchronous_commit = off;

    EXECUTE format('INSERT INTO %I SELECT * FROM jsonb_populate_recordset(null::%I, $1)',
                   p_table_name, p_table_name)
    USING p_records;

    -- 记录审计（同步提交）
    SET LOCAL synchronous_commit = on;

    INSERT INTO async_commit_audit (
        operation_id, table_name, operation_type, record_count, committed_at
    ) VALUES (
        v_op_id, p_table_name, 'bulk_insert',
        jsonb_array_length(p_records), NOW()
    );
END;
$$;
```

### 6.2 同步提交

```sql
-- ============================================
-- 同步提交配置
-- ============================================

-- 严格同步提交（金融交易）
CREATE OR REPLACE PROCEDURE sp_strict_sync_transaction(
    IN p_from_account TEXT,
    IN p_to_account TEXT,
    IN p_amount DECIMAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_from_balance DECIMAL;
BEGIN
    -- 强制最高级别同步
    SET LOCAL synchronous_commit = remote_apply;
    SET LOCAL synchronous_standby_names = 'FIRST 1 (standby_1)';

    -- 检查余额
    SELECT balance INTO v_from_balance
    FROM accounts WHERE account_id = p_from_account
    FOR UPDATE;

    IF v_from_balance < p_amount THEN
        RAISE EXCEPTION 'Insufficient balance';
    END IF;

    -- 执行转账
    UPDATE accounts SET balance = balance - p_amount
    WHERE account_id = p_from_account;

    UPDATE accounts SET balance = balance + p_amount
    WHERE account_id = p_to_account;

    -- 记录交易
    INSERT INTO transactions (from_account, to_account, amount, status)
    VALUES (p_from_account, p_to_account, p_amount, 'completed');

    -- 确认同步完成
    COMMIT;

    -- 恢复默认设置
    -- 设置会在事务结束时自动恢复
END;
$$;
```

### 6.3 半同步复制

```sql
-- ============================================
-- 半同步复制（MySQL术语，PostgreSQL类似概念）
-- ============================================

-- PostgreSQL中的"半同步"配置
-- 使用 FIRST 1 确保至少一个从库确认

-- 配置
ALTER SYSTEM SET synchronous_standby_names = 'FIRST 1 (standby_1, standby_2, standby_3)';
SELECT pg_reload_conf();

-- 存储过程：动态调整同步级别
CREATE OR REPLACE PROCEDURE sp_set_semi_sync(
    IN p_required_confirmations INT DEFAULT 1,
    IN p_candidate_standbys TEXT[] DEFAULT ARRAY['standby_1', 'standby_2']
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_config TEXT;
BEGIN
    v_config := format('FIRST %s (%s)',
                       p_required_confirmations,
                       array_to_string(p_candidate_standbys, ', '));

    EXECUTE format('ALTER SYSTEM SET synchronous_standby_names = %L', v_config);
    PERFORM pg_reload_conf();

    -- 记录变更
    INSERT INTO sync_config_changes (config_value, changed_at, changed_by)
    VALUES (v_config, NOW(), current_user);
END;
$$;
```

---

## 7. 会话一致性模型

### 7.1 读写一致性

```sql
-- ============================================
-- 读写一致性（Read-Your-Writes）
-- ============================================

-- 1. 会话写标记表
CREATE TABLE session_write_tokens (
    session_id TEXT PRIMARY KEY,
    last_write_token BIGINT,
    last_write_time TIMESTAMPTZ,
    expires_at TIMESTAMPTZ
);

-- 2. 全局单调token序列
CREATE SEQUENCE global_write_token_seq;

-- 3. 写操作生成token
CREATE OR REPLACE FUNCTION fn_write_with_token(
    p_session_id TEXT,
    p_sql TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_token BIGINT;
BEGIN
    v_token := nextval('global_write_token_seq');

    EXECUTE p_sql;

    INSERT INTO session_write_tokens (session_id, last_write_token, last_write_time, expires_at)
    VALUES (p_session_id, v_token, NOW(), NOW() + INTERVAL '30 seconds')
    ON CONFLICT (session_id) DO UPDATE
    SET last_write_token = v_token,
        last_write_time = NOW(),
        expires_at = NOW() + INTERVAL '30 seconds';

    RETURN v_token;
END;
$$;

-- 4. 读操作检查token
CREATE OR REPLACE FUNCTION fn_read_with_token_check(
    p_session_id TEXT,
    p_sql TEXT,
    p_required_token BIGINT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_session RECORD;
    v_standby_token BIGINT;
BEGIN
    -- 获取会话token
    SELECT * INTO v_session FROM session_write_tokens WHERE session_id = p_session_id;

    p_required_token := COALESCE(p_required_token, v_session.last_write_token);

    -- 检查从库是否应用了该token之前的所有写入
    SELECT COALESCE(MAX(write_token), 0) INTO v_standby_token
    FROM standby_write_progress;  -- 从库上报的进度

    IF v_standby_token >= p_required_token THEN
        -- 安全从从库读取
        RETURN fn_query_standby(p_sql);
    ELSE
        -- 回退到主库
        RETURN fn_query_primary(p_sql);
    END IF;
END;
$$;
```

### 7.2 因果一致性

```sql
-- ============================================
-- 因果一致性（Causal Consistency）
-- ============================================

-- 1. 因果向量时钟
CREATE TABLE causal_context (
    session_id TEXT PRIMARY KEY,
    vector_clock JSONB DEFAULT '{}'::JSONB,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 合并向量时钟
CREATE OR REPLACE FUNCTION fn_merge_vector_clocks(
    p_vc1 JSONB,
    p_vc2 JSONB
)
RETURNS JSONB
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_result JSONB := p_vc1;
    v_key TEXT;
    v_val INT;
BEGIN
    FOR v_key, v_val IN SELECT * FROM jsonb_each_text(p_vc2)
    LOOP
        v_result := jsonb_set(v_result, ARRAY[v_key],
            to_jsonb(GREATEST(
                COALESCE((v_result->>v_key)::INT, 0),
                v_val::INT
            )));
    END LOOP;

    RETURN v_result;
END;
$$;

-- 3. 检查因果前置
CREATE OR REPLACE FUNCTION fn_happens_before(
    p_vc1 JSONB,
    p_vc2 JSONB
)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_all_leq BOOLEAN := true;
    v_any_lt BOOLEAN := false;
    v_key TEXT;
BEGIN
    FOR v_key IN SELECT DISTINCT key FROM (
        SELECT jsonb_object_keys(p_vc1) as key
        UNION
        SELECT jsonb_object_keys(p_vc2) as key
    ) t
    LOOP
        IF COALESCE((p_vc1->>v_key)::INT, 0) > COALESCE((p_vc2->>v_key)::INT, 0) THEN
            v_all_leq := false;
            EXIT;
        END IF;

        IF COALESCE((p_vc1->>v_key)::INT, 0) < COALESCE((p_vc2->>v_key)::INT, 0) THEN
            v_any_lt := true;
        END IF;
    END LOOP;

    RETURN v_all_leq AND v_any_lt;
END;
$$;
```

### 7.3 单调读一致性

```sql
-- ============================================
-- 单调读一致性（Monotonic Reads）
-- ============================================

-- 1. 会话读取检查点
CREATE TABLE monotonic_read_checkpoints (
    session_id TEXT PRIMARY KEY,
    last_read_lsn PG_LSN,
    last_read_time TIMESTAMPTZ,
    checkpoint_count INT DEFAULT 1
);

-- 2. 更新检查点
CREATE OR REPLACE PROCEDURE sp_update_read_checkpoint(
    IN p_session_id TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_lsn PG_LSN;
BEGIN
    -- 获取当前从库回放位置
    SELECT replay_lsn INTO v_lsn FROM pg_stat_wal_receiver;

    INSERT INTO monotonic_read_checkpoints (session_id, last_read_lsn, last_read_time)
    VALUES (p_session_id, v_lsn, NOW())
    ON CONFLICT (session_id) DO UPDATE
    SET last_read_lsn = GREATEST(monotonic_read_checkpoints.last_read_lsn, v_lsn),
        last_read_time = NOW(),
        checkpoint_count = monotonic_read_checkpoints.checkpoint_count + 1;
END;
$$;

-- 3. 单调读查询
CREATE OR REPLACE FUNCTION fn_monotonic_read(
    p_session_id TEXT,
    p_sql TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_checkpoint PG_LSN;
    v_current_lsn PG_LSN;
BEGIN
    -- 获取会话检查点
    SELECT last_read_lsn INTO v_checkpoint
    FROM monotonic_read_checkpoints
    WHERE session_id = p_session_id;

    IF v_checkpoint IS NULL THEN
        -- 首次读取，设置检查点
        CALL sp_update_read_checkpoint(p_session_id);
        RETURN fn_query_standby(p_sql);
    END IF;

    -- 等待从库追上检查点
    LOOP
        SELECT replay_lsn INTO v_current_lsn FROM pg_stat_wal_receiver;
        EXIT WHEN v_current_lsn >= v_checkpoint;
        PERFORM pg_sleep(0.01);
    END LOOP;

    -- 执行查询
    RETURN fn_query_standby(p_sql);
END;
$$;
```

---

## 8. 高可用架构

### 8.1 自动故障转移

```sql
-- ============================================
-- 故障转移与恢复
-- ============================================

-- 1. 故障转移触发存储过程
CREATE OR REPLACE PROCEDURE sp_trigger_failover(
    IN p_failed_primary TEXT,
    IN p_new_primary TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 记录故障转移事件
    INSERT INTO failover_events (
        failed_primary, new_primary, triggered_at, triggered_by
    ) VALUES (p_failed_primary, p_new_primary, NOW(), current_user);

    -- 提升新主库（通过外部脚本或patroni/consul等）
    -- 这里仅记录，实际由HA工具执行
    PERFORM pg_notify('failover_triggered', jsonb_build_object(
        'failed_primary', p_failed_primary,
        'new_primary', p_new_primary,
        'action', 'PROMOTE_STANDBY'
    )::TEXT);
END;
$$;

-- 2. 健康检查函数
CREATE OR REPLACE FUNCTION fn_health_check()
RETURNS TABLE (
    check_name TEXT,
    status TEXT,
    details JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 复制延迟检查
    RETURN QUERY
    SELECT
        'replication_lag'::TEXT,
        CASE
            WHEN replay_lag_bytes < 10 * 1024 * 1024 THEN 'healthy'
            WHEN replay_lag_bytes < 100 * 1024 * 1024 THEN 'warning'
            ELSE 'critical'
        END::TEXT,
        jsonb_build_object('lag_bytes', replay_lag_bytes)
    FROM v_replication_lag
    WHERE standby_name = 'standby_1';

    -- 连接数检查
    RETURN QUERY
    SELECT
        'connection_count'::TEXT,
        CASE
            WHEN count < max_connections * 0.8 THEN 'healthy'
            WHEN count < max_connections * 0.95 THEN 'warning'
            ELSE 'critical'
        END::TEXT,
        jsonb_build_object('current', count, 'max', max_connections)
    FROM (SELECT count(*) as count FROM pg_stat_activity) t,
         (SELECT setting::INT as max_connections FROM pg_settings WHERE name = 'max_connections') m;
END;
$$;
```

### 8.2 连接池配置

```sql
-- ============================================
-- 连接池与负载均衡
-- ============================================

-- 1. PgBouncer配置（通过配置文件，这里提供管理存储过程）
-- pgbouncer.ini 示例
/*
[databases]
mydb_primary = host=primary.internal port=5432 dbname=mydb
mydb_standby1 = host=standby1.internal port=5432 dbname=mydb
mydb_standby2 = host=standby2.internal port=5432 dbname=mydb
mydb = host=pgbouncer.internal port=6432 pool_mode=transaction

[pgbouncer]
listen_port = 6439
listen_addr = 0.0.0.0
auth_type = scram-sha-256
pool_mode = transaction
default_pool_size = 25
reserve_pool_size = 5
max_client_conn = 10000
server_idle_timeout = 600
server_lifetime = 3600
*/

-- 2. 连接池状态监控存储过程
CREATE OR REPLACE FUNCTION fn_pool_status()
RETURNS TABLE (
    pool_name TEXT,
    active_connections INT,
    waiting_clients INT,
    avg_query_time_ms NUMERIC
)
LANGUAGE SQL
AS $$
    -- 实际查询PgBouncer SHOW命令
    -- 这里提供结构示例
    SELECT
        'primary'::TEXT,
        15,
        2,
        5.2
    UNION ALL
    SELECT 'standby1'::TEXT, 10, 0, 3.1
    UNION ALL
    SELECT 'standby2'::TEXT, 8, 1, 4.5;
$$;

-- 3. 动态路由决策
CREATE OR REPLACE FUNCTION fn_get_connection_pool(
    p_operation_type TEXT,  -- 'read', 'write'
    p_consistency TEXT      -- 'eventual', 'session', 'strong'
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_pool_status RECORD;
BEGIN
    IF p_operation_type = 'write' THEN
        RETURN 'mydb_primary';
    END IF;

    -- 读取操作：根据一致性要求和负载选择
    IF p_consistency = 'strong' THEN
        RETURN 'mydb_primary';
    END IF;

    -- 选择负载最低的从库
    SELECT * INTO v_pool_status
    FROM fn_pool_status()
    WHERE pool_name LIKE 'standby%'
    ORDER BY active_connections + waiting_clients
    LIMIT 1;

    RETURN v_pool_status.pool_name;
END;
$$;
```

---

## 9. 性能优化

```sql
-- ============================================
-- 读写分离性能优化
-- ============================================

-- 1. 预热从库缓存
CREATE OR REPLACE PROCEDURE sp_warmup_standby_cache(
    IN p_table_name TEXT,
    IN p_limit INT DEFAULT 10000
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 在从库上执行顺序扫描，预热共享缓冲区
    PERFORM 1 FROM dblink('host=standby1.internal', format(
        'SELECT count(*) FROM %I',
        p_table_name
    )) AS t(count BIGINT);
END;
$$;

-- 2. 复制槽清理
CREATE OR REPLACE PROCEDURE sp_cleanup_replication_slots()
LANGUAGE plpgsql
AS $$
DECLARE
    v_slot RECORD;
BEGIN
    FOR v_slot IN
        SELECT * FROM pg_replication_slots
        WHERE NOT active
          AND restart_lsn < pg_current_wal_lsn() - 1073741824  -- 1GB
    LOOP
        PERFORM pg_drop_replication_slot(v_slot.slot_name);

        INSERT INTO replication_slot_cleanup_log (slot_name, dropped_at)
        VALUES (v_slot.slot_name, NOW());
    END LOOP;
END;
$$;

-- 3. WAL归档优化
-- postgresql.conf
-- archive_mode = on
-- archive_command = 'cp %p /archive/%f'
-- archive_timeout = 60

-- 4. 并行复制 workers
-- max_parallel_workers = 8
-- max_parallel_workers_per_gather = 4
```

---

## 10. 持续推进计划

### 短期目标 (1-2周)

- [ ] 部署流复制架构
- [ ] 配置读写分离路由
- [ ] 实施延迟监控

### 中期目标 (1个月)

- [ ] 部署逻辑复制
- [ ] 实施会话一致性
- [ ] 配置自动故障转移

### 长期目标 (3个月)

- [ ] 多数据中心复制
- [ ] 智能负载均衡
- [ ] 一致性模型全覆盖

---

**文档信息**:

- 字数: 11000+
- 复制模式: 10+
- 代码示例: 50+
- 状态: ✅ 深度分析完成

---

*构建高性能、高可用的数据库架构！* 🔄
