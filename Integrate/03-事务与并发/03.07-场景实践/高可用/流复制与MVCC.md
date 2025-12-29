---

> **📋 文档来源**: `MVCC-ACID-CAP\03-场景实践\高可用\流复制与MVCC.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL流复制与MVCC深度分析

> **文档编号**: SCENARIO-HA-STREAMING-001
> **主题**: 流复制与MVCC
> **版本**: PostgreSQL 17 & 18

---

## 📑 目录

- [PostgreSQL流复制与MVCC深度分析](#postgresql流复制与mvcc深度分析)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔍 第一部分：流复制机制](#-第一部分流复制机制)
    - [1.1 流复制原理](#11-流复制原理)
      - [WAL传输](#wal传输)
      - [同步模式](#同步模式)
      - [复制槽](#复制槽)
    - [1.2 主从架构](#12-主从架构)
      - [主节点角色](#主节点角色)
      - [从节点角色](#从节点角色)
      - [复制流程](#复制流程)
    - [1.3 PostgreSQL 17优化](#13-postgresql-17优化)
      - [逻辑复制故障转移](#逻辑复制故障转移)
      - [性能优化](#性能优化)
  - [🚀 第二部分：MVCC影响分析](#-第二部分mvcc影响分析)
    - [2.1 快照一致性](#21-快照一致性)
      - [主节点快照](#主节点快照)
      - [从节点快照](#从节点快照)
      - [一致性保证](#一致性保证)
    - [2.2 版本链复制](#22-版本链复制)
      - [WAL记录](#wal记录)
      - [版本链同步](#版本链同步)
      - [VACUUM影响](#vacuum影响)
    - [2.3 事务可见性](#23-事务可见性)
      - [主节点可见性](#主节点可见性)
      - [从节点可见性](#从节点可见性)
      - [延迟影响](#延迟影响)
      - [网络优化](#网络优化)
      - [WAL优化](#wal优化)
    - [3.2 查询性能优化](#32-查询性能优化)
      - [只读查询](#只读查询)
      - [热备查询](#热备查询)
      - [查询路由](#查询路由)
    - [3.3 资源优化](#33-资源优化)
      - [WAL保留](#wal保留)
      - [复制槽管理](#复制槽管理)
      - [内存优化](#内存优化)
  - [🔧 第四部分：故障处理](#-第四部分故障处理)
    - [4.1 主节点故障](#41-主节点故障)
      - [故障检测](#故障检测)
      - [故障转移](#故障转移)
    - [4.2 从节点故障](#42-从节点故障)
      - [故障检测](#故障检测-1)
      - [恢复处理](#恢复处理)
    - [4.3 网络故障](#43-网络故障)
      - [分区处理](#分区处理)
      - [延迟处理](#延迟处理)
      - [一致性保证](#一致性保证-1)
  - [📝 总结](#-总结)
    - [核心机制](#核心机制)
    - [MVCC影响](#mvcc影响)
    - [最佳实践](#最佳实践)

---

## 📋 概述

流复制是PostgreSQL高可用的核心机制，通过WAL流式传输实现主从同步。本文档深入分析流复制与MVCC的交互，包括复制机制、MVCC影响、性能优化和故障处理。

---

## 🔍 第一部分：流复制机制

### 1.1 流复制原理

#### WAL传输

```text
WAL流式传输：

1. 主节点：
   - 事务提交写入WAL
   - WAL通过流复制传输
   - 等待从节点确认（同步模式）

2. 从节点：
   - 接收WAL流
   - 应用WAL记录
   - 更新数据库状态

3. 传输协议：
   - 基于TCP连接
   - 流式传输
   - 低延迟
```

#### 同步模式

```sql
-- 同步复制配置（postgresql.conf，带说明）
-- 注意：以下配置需要在postgresql.conf文件中设置，然后重启PostgreSQL
-- synchronous_standby_names = 'standby1,standby2'
-- synchronous_commit = on

-- 同步模式类型（带错误处理说明）：
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '同步模式类型说明：';
        RAISE NOTICE '1. off：异步复制（性能最高，一致性最低）';
        RAISE NOTICE '2. on：同步复制（性能最低，一致性最高）';
        RAISE NOTICE '3. remote_write：远程写入确认（平衡）';
        RAISE NOTICE '4. remote_apply：远程应用确认（最强一致性）';
        RAISE NOTICE '';
        RAISE NOTICE 'MVCC影响：';
        RAISE NOTICE '- 同步模式影响事务提交延迟';
        RAISE NOTICE '- 影响MVCC快照可见性';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

#### 复制槽

```sql
-- 创建复制槽（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replica_slot') THEN
            RAISE NOTICE '复制槽 replica_slot 已存在';
        ELSE
            BEGIN
                PERFORM pg_create_physical_replication_slot('replica_slot');
                RAISE NOTICE '复制槽 replica_slot 创建成功';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '复制槽 replica_slot 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建复制槽失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 复制槽作用说明（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '复制槽作用：';
        RAISE NOTICE '1. 防止WAL被删除';
        RAISE NOTICE '2. 保证从节点可以恢复';
        RAISE NOTICE '3. 跟踪复制进度';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查看复制槽（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始查看复制槽信息';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    slot_name,
    slot_type,
    active,
    restart_lsn,
    confirmed_flush_lsn
FROM pg_replication_slots;

-- MVCC影响说明（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE 'MVCC影响：';
        RAISE NOTICE '- 复制槽保留WAL，影响WAL空间';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
-- 影响VACUUM和MVCC清理
```

### 1.2 主从架构

#### 主节点角色

```text
主节点（Primary）角色：

1. 写操作：
   - 接收写请求
   - 执行事务
   - 写入WAL
   - 传输WAL

2. 复制管理：
   - 管理从节点连接
   - 跟踪复制进度
   - 处理复制故障

3. MVCC处理：
   - 正常MVCC处理
   - 快照创建
   - 版本链管理
```

#### 从节点角色

```text
从节点（Standby）角色：

1. 复制处理：
   - 接收WAL流
   - 应用WAL记录
   - 更新数据库状态

2. 只读查询：
   - 支持只读查询（热备）
   - 基于复制快照
   - 不阻塞复制

3. MVCC处理：
   - 基于WAL应用
   - 快照滞后
   - 版本链同步
```

#### 复制流程

```text
流复制流程：

1. 事务提交：
   Primary: BEGIN → 执行操作 → COMMIT
   Primary: 写入WAL → 传输WAL

2. WAL传输：
   Primary → Standby: WAL记录
   Standby: 接收WAL → 应用WAL

3. 确认机制（同步模式）：
   Standby → Primary: 确认接收
   Primary: 确认提交

4. MVCC影响：
   - Primary: 立即可见
   - Standby: 延迟可见（复制延迟）
```

### 1.3 PostgreSQL 17优化

#### 逻辑复制故障转移

```text
PostgreSQL 17逻辑复制故障转移：

1. 故障检测：
   - 自动检测主节点故障
   - 快速故障转移

2. 故障转移：
   - 从节点提升为主节点
   - 逻辑复制继续工作
   - 保证数据一致性

3. MVCC影响：
   - 故障转移期间MVCC状态保持
   - 保证事务一致性
```

#### 性能优化

```text
PostgreSQL 17性能优化：

1. WAL传输优化：
   - 批量传输
   - 压缩传输
   - 减少网络开销

2. 应用优化：
   - 并行应用
   - 批量应用
   - 提高效率

3. MVCC优化：
   - 优化快照创建
   - 优化版本链处理
   - 提高性能
```

---

## 🚀 第二部分：MVCC影响分析

### 2.1 快照一致性

#### 主节点快照

```text
主节点快照：

1. 正常快照：
   - 事务级快照
   - 立即可见
   - 强一致性

2. 复制影响：
   - 不影响快照创建
   - 不影响可见性判断
   - 正常MVCC处理

3. 同步模式影响：
   - 同步模式延迟提交
   - 不影响快照一致性
   - 保证强一致性
```

#### 从节点快照

```text
从节点快照：

1. 复制快照：
   - 基于WAL应用
   - 快照滞后主节点
   - 最终一致性

2. 可见性判断：
   - 基于复制进度
   - 可能看不到最新数据
   - 延迟可见

3. 一致性保证：
   - 保证数据一致性
   - 不保证时间一致性
   - 最终达到一致
```

#### 一致性保证

```text
流复制一致性保证：

1. 强一致性（同步模式）：
   - 主从数据强一致
   - 事务提交等待从节点确认
   - 保证数据不丢失

2. 最终一致性（异步模式）：
   - 主从数据最终一致
   - 允许复制延迟
   - 提高性能

3. MVCC一致性：
   - 主节点：强一致性
   - 从节点：最终一致性（异步）或强一致性（同步）
```

### 2.2 版本链复制

#### WAL记录

```text
WAL记录与版本链：

1. INSERT操作：
   WAL记录：INSERT元组
   版本链：创建新版本
   复制：传输INSERT WAL

2. UPDATE操作：
   WAL记录：UPDATE元组（新版本）
   版本链：创建新版本，标记旧版本
   复制：传输UPDATE WAL

3. DELETE操作：
   WAL记录：DELETE元组
   版本链：标记删除
   复制：传输DELETE WAL
```

#### 版本链同步

```text
版本链同步机制：

1. 主节点：
   - 正常版本链管理
   - VACUUM清理死亡元组
   - 版本链正常

2. 从节点：
   - 通过WAL应用版本链
   - 版本链与主节点一致
   - 延迟VACUUM

3. 同步保证：
   - 版本链最终一致
   - 需要时间同步
   - 保证数据正确性
```

#### VACUUM影响

```text
VACUUM对复制的影响：

1. 主节点VACUUM：
   - 正常VACUUM清理
   - 不影响复制
   - 版本链清理

2. 从节点VACUUM：
   - 延迟VACUUM
   - 等待复制完成
   - 版本链清理

3. 复制延迟影响：
   - 复制延迟影响VACUUM
   - 版本链可能较长
   - 需要监控
```

### 2.3 事务可见性

#### 主节点可见性

```text
主节点事务可见性：

1. 立即可见：
   - 事务提交后立即可见
   - 其他事务立即看到
   - 强一致性

2. 同步模式：
   - 等待从节点确认
   - 提交延迟增加
   - 不影响可见性

3. MVCC处理：
   - 正常MVCC处理
   - 快照立即更新
   - 版本链正常
```

#### 从节点可见性

```text
从节点事务可见性：

1. 延迟可见：
   - 事务提交后延迟可见
   - 取决于复制延迟
   - 最终一致性

2. 热备查询：
   - 支持只读查询
   - 基于复制快照
   - 可能看到旧数据

3. MVCC处理：
   - 基于WAL应用
   - 快照滞后
   - 版本链同步
```

#### 延迟影响

```sql
-- 监控复制延迟（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始监控复制延迟';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '监控准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    client_addr,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS sent_lag_bytes,
    pg_wal_lsn_diff(pg_current_wal_lsn(), write_lsn) AS write_lag_bytes,
    pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn) AS flush_lag_bytes,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replay_lag_bytes,
    EXTRACT(EPOCH FROM (now() - replay_lag_time)) AS replay_lag_seconds
FROM pg_stat_replication;

-- 延迟影响说明（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '延迟影响：';
        RAISE NOTICE '1. 读延迟：从节点可能读到旧数据';
        RAISE NOTICE '2. 故障恢复：延迟影响恢复时间';
        RAISE NOTICE '3. MVCC：延迟影响快照一致性';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

---

## 📊 第三部分：性能优化

### 3.1 复制延迟优化

#### 同步模式优化

```sql
-- 同步模式优化（带说明）
-- 注意：以下配置需要在postgresql.conf文件中设置，然后重启PostgreSQL
-- 平衡一致性和性能

-- 方案说明（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '同步模式优化方案：';
        RAISE NOTICE '';
        RAISE NOTICE '方案1：远程写入确认（平衡）';
        RAISE NOTICE '配置: synchronous_commit = remote_write;';
        RAISE NOTICE '- 从节点写入WAL后确认，不等待应用';
        RAISE NOTICE '- 延迟：中等';
        RAISE NOTICE '- 一致性：中等';
        RAISE NOTICE '';
        RAISE NOTICE '方案2：远程应用确认（最强一致性）';
        RAISE NOTICE '配置: synchronous_commit = remote_apply;';
        RAISE NOTICE '- 从节点应用WAL后确认';
        RAISE NOTICE '- 延迟：高';
        RAISE NOTICE '- 一致性：最强';
        RAISE NOTICE '';
        RAISE NOTICE '方案3：异步复制（最高性能）';
        RAISE NOTICE '配置: synchronous_commit = off;';
        RAISE NOTICE '- 不等待从节点确认';
        RAISE NOTICE '- 延迟：低';
        RAISE NOTICE '- 一致性：最终一致性';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

#### 网络优化

```text
网络优化策略：

1. 网络带宽：
   - 增加网络带宽
   - 减少网络延迟
   - 提高传输效率

2. 网络路径：
   - 优化网络路径
   - 减少跳数
   - 使用专用网络

3. 压缩传输：
   - WAL压缩传输
   - 减少网络开销
   - 提高效率
```

#### WAL优化

```sql
-- WAL优化配置（带说明）
-- 注意：以下配置需要在postgresql.conf文件中设置，然后重启PostgreSQL
-- 减少WAL生成，提高复制效率

-- 配置说明（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE 'WAL优化配置说明：';
        RAISE NOTICE '';
        RAISE NOTICE '1. 减少WAL生成';
        RAISE NOTICE '   wal_level = replica;  -- 最小WAL级别';
        RAISE NOTICE '   wal_compression = on;  -- WAL压缩';
        RAISE NOTICE '';
        RAISE NOTICE '2. 批量提交';
        RAISE NOTICE '   commit_delay = 100;  -- 延迟提交（微秒）';
        RAISE NOTICE '   commit_siblings = 5;  -- 批量提交阈值';
        RAISE NOTICE '';
        RAISE NOTICE '3. 异步提交（如可接受）';
        RAISE NOTICE '   synchronous_commit = off;  -- 异步提交';
        RAISE NOTICE '';
        RAISE NOTICE 'MVCC影响：';
        RAISE NOTICE '- WAL优化不影响MVCC机制';
        RAISE NOTICE '- 但影响复制延迟和一致性';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 3.2 查询性能优化

#### 只读查询

```sql
-- 从节点只读查询配置（带说明）
-- 注意：以下配置需要在postgresql.conf文件中设置，然后重启PostgreSQL
-- 主节点配置
-- max_wal_senders = 10;
-- wal_level = replica;

-- 从节点配置
-- hot_standby = on;
-- max_standby_streaming_delay = 30s;

-- 只读查询特点说明（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '只读查询特点：';
        RAISE NOTICE '1. 不阻塞复制';
        RAISE NOTICE '2. 基于复制快照';
        RAISE NOTICE '3. 可能看到旧数据';
        RAISE NOTICE '4. 提高读性能';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

#### 热备查询

```text
热备查询优化：

1. 查询路由：
   - 读操作路由到从节点
   - 写操作路由到主节点
   - 负载均衡

2. 延迟处理：
   - 处理复制延迟
   - 提供一致性读
   - 优化用户体验

3. 性能提升：
   - 读性能提升50-80%
   - 主节点负载降低
   - 系统吞吐量提升
```

#### 查询路由

```text
查询路由策略：

1. 自动路由：
   - 根据操作类型路由
   - 读操作：从节点
   - 写操作：主节点

2. 一致性路由：
   - 强一致性读：主节点
   - 最终一致性读：从节点
   - 根据需求选择

3. 负载均衡：
   - 多个从节点
   - 负载均衡
   - 提高性能
```

### 3.3 资源优化

#### WAL保留

```sql
-- WAL保留配置（带错误处理）
-- 平衡空间和安全性

-- 1. 复制槽保留WAL（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replica_slot') THEN
            RAISE NOTICE '复制槽 replica_slot 已存在';
        ELSE
            BEGIN
                PERFORM pg_create_physical_replication_slot('replica_slot');
                RAISE NOTICE '复制槽 replica_slot 创建成功';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '复制槽 replica_slot 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建复制槽失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 2. 最大WAL保留（PostgreSQL 17+，带说明）
-- 注意：以下配置需要在postgresql.conf文件中设置，然后重启PostgreSQL
-- max_slot_wal_keep_size = '10GB';  -- 最大WAL保留大小

-- 3. 监控WAL使用（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replica_slot') THEN
            RAISE WARNING '复制槽 replica_slot 不存在，无法监控WAL使用';
            RETURN;
        END IF;
        RAISE NOTICE '开始监控WAL使用';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '监控准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS wal_retained
FROM pg_replication_slots
WHERE slot_name = 'replica_slot';

-- MVCC影响说明（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE 'MVCC影响：';
        RAISE NOTICE '- WAL保留影响磁盘空间';
        RAISE NOTICE '- 影响VACUUM和MVCC清理';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

#### 复制槽管理

```sql
-- 复制槽管理（带错误处理）
-- 防止WAL无限增长

-- 1. 监控复制槽（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始监控复制槽';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '监控准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    slot_name,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS wal_retained
FROM pg_replication_slots;

-- 2. 删除不活跃复制槽（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'old_slot') THEN
            RAISE WARNING '复制槽 old_slot 不存在，无法删除';
        ELSE
            BEGIN
                PERFORM pg_drop_replication_slot('old_slot');
                RAISE NOTICE '复制槽 old_slot 删除成功';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '删除复制槽失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 3. 定期清理说明（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '定期清理任务：';
        RAISE NOTICE '1. 监控复制槽状态';
        RAISE NOTICE '2. 清理不活跃复制槽';
        RAISE NOTICE '3. 防止WAL无限增长';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

#### 内存优化

```text
内存优化策略：

1. 共享内存：
   - 优化shared_buffers
   - 优化wal_buffers
   - 提高性能

2. 工作内存：
   - 优化work_mem
   - 优化maintenance_work_mem
   - 平衡内存使用

3. 复制内存：
   - 优化复制缓冲区
   - 优化WAL缓冲区
   - 提高复制效率
```

---

## 🔧 第四部分：故障处理

### 4.1 主节点故障

#### 4.1.1 故障检测

```text
主节点故障检测：

1. 心跳检测：
   - 从节点检测主节点心跳
   - 心跳超时触发故障检测
   - 快速故障检测

2. 连接检测：
   - 检测复制连接
   - 连接断开触发故障检测
   - 自动故障转移

3. 健康检查：
   - 定期健康检查
   - 检测主节点状态
   - 触发故障转移
```

#### 故障转移

```sql
-- 从节点提升为主节点（带错误处理）
-- 注意：以下操作需要在从节点上执行

-- 1. 停止从节点（命令行操作，非SQL）
-- pg_ctl stop

-- 2. 提升为主节点（带错误处理）
DO $$
DECLARE
    is_in_recovery boolean;
BEGIN
    BEGIN
        -- 检查当前是否在恢复模式
        SELECT pg_is_in_recovery() INTO is_in_recovery;

        IF NOT is_in_recovery THEN
            RAISE NOTICE '当前节点已经是主节点，无需提升';
            RETURN;
        END IF;

        -- 尝试提升（需要超级用户权限）
        BEGIN
            PERFORM pg_promote();
            RAISE NOTICE '从节点提升为主节点成功';
        EXCEPTION
            WHEN insufficient_privilege THEN
                RAISE WARNING '权限不足，需要超级用户权限才能执行pg_promote()';
            WHEN OTHERS THEN
                RAISE WARNING '提升失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 3. 验证提升（带错误处理和性能测试）
DO $$
DECLARE
    is_in_recovery boolean;
BEGIN
    BEGIN
        SELECT pg_is_in_recovery() INTO is_in_recovery;

        IF is_in_recovery THEN
            RAISE NOTICE '当前节点仍在恢复模式（从节点）';
        ELSE
            RAISE NOTICE '当前节点已提升为主节点（返回false表示已提升为主节点）';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '验证失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT pg_is_in_recovery();

-- MVCC影响说明（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE 'MVCC影响：';
        RAISE NOTICE '- 故障转移期间MVCC状态保持';
        RAISE NOTICE '- 保证事务一致性';
        RAISE NOTICE '- 版本链正常';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

#### 数据一致性

```text
故障转移数据一致性：

1. 同步模式：
   - 保证数据不丢失
   - 强一致性
   - 故障转移安全

2. 异步模式：
   - 可能丢失未复制数据
   - 最终一致性
   - 需要处理数据丢失

3. MVCC一致性：
   - 故障转移后MVCC状态正常
   - 版本链正常
   - 事务一致性保证
```

### 4.2 从节点故障

#### 4.2.1 故障检测

```text
从节点故障检测：

1. 主节点检测：
   - 检测从节点连接
   - 检测复制进度
   - 触发告警

2. 监控告警：
   - 监控复制延迟
   - 监控从节点状态
   - 触发告警

3. 自动恢复：
   - 从节点自动恢复
   - 重新同步
   - 恢复正常服务
```

#### 恢复处理

```sql
-- 从节点恢复（带错误处理）
-- 1. 检查WAL位置（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF pg_is_in_recovery() THEN
            RAISE NOTICE '当前节点在恢复模式（从节点），开始检查WAL位置';
        ELSE
            RAISE WARNING '当前节点不在恢复模式，此操作应在从节点上执行';
            RETURN;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();

-- 2. 检查复制延迟（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF pg_is_in_recovery() THEN
            RAISE NOTICE '开始检查复制延迟';
        ELSE
            RAISE WARNING '当前节点不在恢复模式，此操作应在从节点上执行';
            RETURN;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pg_wal_lsn_diff(pg_current_wal_lsn(), pg_last_wal_replay_lsn()) AS lag_bytes;

-- 3. 重新同步说明（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '重新同步说明：';
        RAISE NOTICE '1. 从节点自动重新同步';
        RAISE NOTICE '2. 或者手动重新同步';
        RAISE NOTICE '';
        RAISE NOTICE 'MVCC影响：';
        RAISE NOTICE '- 恢复期间MVCC状态保持';
        RAISE NOTICE '- 恢复后版本链同步';
        RAISE NOTICE '- 保证数据一致性';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

#### 重新同步

```text
从节点重新同步：

1. 自动同步：
   - 从节点自动重新同步
   - 从WAL位置继续
   - 恢复正常服务

2. 手动同步：
   - 检查WAL位置
   - 手动重新同步
   - 验证同步状态

3. 数据一致性：
   - 重新同步后数据一致
   - MVCC状态正常
   - 版本链同步
```

### 4.3 网络故障

#### 分区处理

```text
网络分区处理：

1. 分区检测：
   - 检测网络分区
   - 识别分区成员
   - 触发处理

2. 分区处理：
   - 主节点继续服务
   - 从节点暂停服务
   - 分区恢复后同步

3. 一致性保证：
   - 保证数据一致性
   - 避免脑裂
   - 处理冲突
```

#### 延迟处理

```text
复制延迟处理：

1. 延迟监控：
   - 监控复制延迟
   - 设置告警阈值
   - 触发处理

2. 延迟处理：
   - 优化网络
   - 优化配置
   - 处理延迟

3. 一致性处理：
   - 处理延迟影响
   - 保证最终一致性
   - 优化用户体验
```

#### 4.3.1 一致性保证

```text
网络故障一致性保证：

1. 同步模式：
   - 网络故障阻塞提交
   - 保证数据不丢失
   - 强一致性

2. 异步模式：
   - 网络故障不影响提交
   - 可能丢失数据
   - 最终一致性

3. MVCC一致性：
   - 网络故障不影响MVCC
   - 恢复后版本链同步
   - 保证数据一致性
```

---

## 📝 总结

### 核心机制

1. **流复制**: 通过WAL流式传输实现主从同步
2. **同步模式**: 平衡一致性和性能
3. **MVCC影响**: 主节点强一致性，从节点最终一致性

### MVCC影响

- **主节点**: 正常MVCC处理，强一致性
- **从节点**: 基于WAL应用，最终一致性
- **版本链**: 通过WAL同步，最终一致

### 最佳实践

1. **同步模式**: 根据需求选择同步模式
2. **性能优化**: 优化网络、WAL、查询路由
3. **故障处理**: 实现故障检测、故障转移、数据恢复
4. **监控告警**: 监控复制延迟、从节点状态、WAL使用

PostgreSQL流复制与MVCC机制协同工作，通过合理配置和优化，可以在保证高可用的同时获得可接受的性能和一致性。
```
