---

> **📋 文档来源**: `MVCC-ACID-CAP\03-场景实践\高可用\PostgreSQL集群的CAP.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL集群的CAP

> **文档编号**: CAP-PRACTICE-006
> **主题**: PostgreSQL集群的CAP
> **版本**: PostgreSQL 17 & 18
> **状态**: ✅ 已完成

---

## 📑 目录

- [PostgreSQL集群的CAP](#postgresql集群的cap)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📊 第一部分：PostgreSQL集群架构](#-第一部分postgresql集群架构)
    - [1.1 集群架构类型](#11-集群架构类型)
    - [1.2 主从复制集群](#12-主从复制集群)
    - [1.3 主主复制集群](#13-主主复制集群)
  - [📊 第二部分：集群的CAP选择](#-第二部分集群的cap选择)
    - [2.1 主从复制CAP](#21-主从复制cap)
    - [2.2 主主复制CAP](#22-主主复制cap)
    - [2.3 多主复制CAP](#23-多主复制cap)
  - [📊 第三部分：集群的故障处理](#-第三部分集群的故障处理)
    - [3.1 故障检测机制](#31-故障检测机制)
    - [3.2 故障转移流程](#32-故障转移流程)
    - [3.3 故障恢复策略](#33-故障恢复策略)
  - [📊 第四部分：集群的一致性保证](#-第四部分集群的一致性保证)
    - [4.1 主从复制一致性](#41-主从复制一致性)
    - [4.2 主主复制一致性](#42-主主复制一致性)
    - [4.3 集群一致性配置](#43-集群一致性配置)
  - [📊 第五部分：集群CAP选择指南](#-第五部分集群cap选择指南)
    - [5.1 场景化CAP选择](#51-场景化cap选择)
    - [5.2 集群CAP配置](#52-集群cap配置)
    - [5.3 集群CAP监控](#53-集群cap监控)
  - [📝 总结](#-总结)
    - [核心结论](#核心结论)
    - [实践建议](#实践建议)

---

## 📋 概述

PostgreSQL集群是高可用架构的核心，理解集群的CAP选择，有助于设计高可用的PostgreSQL集群。

本文档从集群架构、CAP选择、故障处理、一致性保证和选择指南五个维度，全面阐述PostgreSQL集群的CAP完整体系。

**核心观点**：

- **主从复制集群**：可以配置CP或AP模式
- **主主复制集群**：通常采用AP模式
- **集群故障处理**：影响CAP选择
- **集群一致性**：需要根据场景选择

---

## 📊 第一部分：PostgreSQL集群架构

### 1.1 集群架构类型

**PostgreSQL集群架构**：

| 架构类型 | 说明 | CAP模式 |
|---------|------|---------|
| **主从复制** | 一个主库，多个备库 | CP/AP可配置 |
| **主主复制** | 多个主库，双向复制 | AP |
| **多主复制** | 多个主库，多向复制 | AP |

### 1.2 主从复制集群

**主从复制架构**：

```text
主库 (Primary)
  │
  ├─ 备库1 (Standby) - 同步
  ├─ 备库2 (Standby) - 异步
  └─ 备库3 (Standby) - 异步
```

**配置示例**：

```sql
-- 主库配置（postgresql.conf，这些是配置文件设置，不是SQL语句）
-- synchronous_standby_names = 'standby1'  -- 同步一个
-- max_wal_senders = 10

-- 或者使用ALTER SYSTEM设置（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = 'standby1';
            RAISE NOTICE '同步备库名称已设置为 standby1';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置同步备库名称失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 1.3 主主复制集群

**主主复制架构**：

```text
主库1 (Primary) ←→ 主库2 (Primary)
  │                    │
  └─ 逻辑复制          └─ 逻辑复制
```

**配置示例**：

```sql
-- 主库1创建发布（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'pub1') THEN
            RAISE NOTICE '发布 pub1 已存在';
        ELSE
            BEGIN
                CREATE PUBLICATION pub1 FOR ALL TABLES;
                RAISE NOTICE '发布 pub1 创建成功（主库1，包含所有表）';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '发布 pub1 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建发布失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 主库2创建订阅（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_subscription WHERE subname = 'sub1') THEN
            RAISE NOTICE '订阅 sub1 已存在';
        ELSE
            BEGIN
                CREATE SUBSCRIPTION sub1
                CONNECTION 'host=primary1 port=5432 dbname=mydb'
                PUBLICATION pub1;
                RAISE NOTICE '订阅 sub1 创建成功（主库2订阅主库1）';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '订阅 sub1 已存在';
                WHEN sqlclient_unable_to_establish_sqlconnection THEN
                    RAISE WARNING '无法连接到主库1，请检查连接字符串';
                WHEN OTHERS THEN
                    RAISE WARNING '创建订阅失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 📊 第二部分：集群的CAP选择

### 2.1 主从复制CAP

**主从复制CAP选择**：

| 配置 | CAP模式 | 说明 |
|------|---------|------|
| **同步复制** | CP | 强一致性，低可用性 |
| **异步复制** | AP | 弱一致性，高可用性 |
| **混合模式** | CP/AP动态 | 部分同步，部分异步 |

**PostgreSQL配置**：

```sql
-- CP模式：同步复制（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
            RAISE NOTICE '同步备库名称已设置为 standby1,standby2（CP模式）';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置同步备库名称失败: %', SQLERRM;
        END;

        BEGIN
            ALTER SYSTEM SET synchronous_commit = 'remote_apply';
            RAISE NOTICE '同步提交模式已设置为 remote_apply（CP模式，强一致性）';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置同步提交模式失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- AP模式：异步复制（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式，异步复制）';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置同步备库名称失败: %', SQLERRM;
        END;

        BEGIN
            ALTER SYSTEM SET synchronous_commit = 'local';
            RAISE NOTICE '同步提交模式已设置为 local（AP模式，高可用性）';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置同步提交模式失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 2.2 主主复制CAP

**主主复制CAP选择**：

| CAP属性 | 主主复制 | 说明 |
|---------|---------|------|
| **C (一致性)** | ❌ 弱 | 最终一致性 |
| **A (可用性)** | ✅ 高 | 任一主库可用即可 |
| **P (分区容错)** | ✅ 高 | 网络分区时继续服务 |

**主主复制特征**：

- ✅ **高可用性**：任一主库故障，其他主库继续服务
- ❌ **弱一致性**：主库间数据可能不一致
- ✅ **分区容错**：网络分区时继续服务

### 2.3 多主复制CAP

**多主复制CAP选择**：

| CAP属性 | 多主复制 | 说明 |
|---------|---------|------|
| **C (一致性)** | ❌ 弱 | 最终一致性 |
| **A (可用性)** | ✅ 高 | 多个主库高可用 |
| **P (分区容错)** | ✅ 高 | 网络分区时继续服务 |

---

## 📊 第三部分：集群的故障处理

### 3.1 故障检测机制

**故障检测方法**：

1. **心跳检测**
   - 定期发送心跳
   - 检测节点存活
   - 超时判定故障

2. **健康检查**
   - 定期健康检查
   - 检测服务状态
   - 返回健康状态

**PostgreSQL实现**：

```sql
-- 监控集群状态（带错误处理和性能测试）
DO $$
DECLARE
    v_application_name TEXT;
    v_state TEXT;
    v_sync_state TEXT;
    v_lag_bytes BIGINT;
BEGIN
    BEGIN
        BEGIN
            SELECT
                application_name,
                state,
                sync_state,
                pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
            INTO v_application_name, v_state, v_sync_state, v_lag_bytes
            FROM pg_stat_replication
            LIMIT 1;

            IF FOUND THEN
                RAISE NOTICE '集群状态监控：';
                RAISE NOTICE '  application_name: %', v_application_name;
                RAISE NOTICE '  state: %', v_state;
                RAISE NOTICE '  sync_state: %', v_sync_state;
                RAISE NOTICE '  lag_bytes: %', v_lag_bytes;
            ELSE
                RAISE NOTICE '未找到复制连接';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '监控集群状态失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 性能测试：监控集群状态
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    application_name,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
FROM pg_stat_replication;
```

### 3.2 故障转移流程

**故障转移流程**：

```text
1. 检测主库故障
   │
2. 选择最佳备库
   │
3. 提升备库为主库
   │
4. 更新连接配置
   │
5. 恢复服务
```

**PostgreSQL故障转移工具**：

- **pg_auto_failover**：自动故障转移
- **Patroni**：高可用管理工具
- **repmgr**：复制管理器

### 3.3 故障恢复策略

**恢复策略**：

1. **自动恢复**：使用故障转移工具自动恢复
2. **手动恢复**：手动提升备库为主库
3. **数据恢复**：从备份恢复数据

---

## 📊 第四部分：集群的一致性保证

### 4.1 主从复制一致性

**主从复制一致性**：

| 复制模式 | 一致性 | 说明 |
|---------|--------|------|
| **同步复制** | 强一致性 | 主库等待备库确认 |
| **异步复制** | 最终一致性 | 主库立即提交 |

**PostgreSQL配置**：

```sql
-- 强一致性：同步复制
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
ALTER SYSTEM SET synchronous_commit = 'remote_apply';

-- 最终一致性：异步复制
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';
```

### 4.2 主主复制一致性

**主主复制一致性**：

- ❌ **弱一致性**：主库间数据可能不一致
- ✅ **最终一致性**：最终所有主库一致
- ⚠️ **冲突解决**：需要处理写入冲突

**冲突解决策略**：

```sql
-- 逻辑复制冲突解决
ALTER SUBSCRIPTION sub1 SET (
    conflict_resolution = 'last_update_wins'
);
```

### 4.3 集群一致性配置

**集群一致性配置**：

```sql
-- 关键数据：强一致性
ALTER TABLE accounts SET (synchronous_commit = 'remote_apply');

-- 非关键数据：最终一致性
ALTER TABLE logs SET (synchronous_commit = 'local');
```

---

## 📊 第五部分：集群CAP选择指南

### 5.1 场景化CAP选择

**场景化选择**：

| 场景 | 集群架构 | CAP模式 | 说明 |
|------|---------|---------|------|
| **金融交易** | 主从复制 | CP | 强一致性 |
| **日志系统** | 主从复制 | AP | 高可用性 |
| **内容管理** | 主主复制 | AP | 高可用性 |

### 5.2 集群CAP配置

**集群CAP配置示例**：

```sql
-- 金融场景：CP模式
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
ALTER SYSTEM SET synchronous_commit = 'remote_apply';
ALTER SYSTEM SET default_transaction_isolation = 'serializable';

-- 日志场景：AP模式
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';
ALTER SYSTEM SET default_transaction_isolation = 'read committed';
```

### 5.3 集群CAP监控

**监控指标**：

```sql
-- 监控集群状态
SELECT
    application_name,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
FROM pg_stat_replication;

-- 监控集群可用性
SELECT
    COUNT(*) FILTER (WHERE state = 'active') AS active_nodes,
    COUNT(*) AS total_nodes
FROM pg_stat_replication;
```

---

## 📝 总结

### 核心结论

1. **主从复制集群**：可以配置CP或AP模式
2. **主主复制集群**：通常采用AP模式
3. **集群故障处理**：影响CAP选择
4. **集群一致性**：需要根据场景选择

### 实践建议

1. **根据场景选择集群架构**：金融场景选择主从CP，日志场景选择主从AP
2. **配置集群CAP**：根据业务需求配置CAP模式
3. **监控集群状态**：实时监控集群可用性和一致性
4. **准备故障处理**：制定集群故障处理预案

---

**最后更新**: 2024年
**维护状态**: ✅ 已完成
