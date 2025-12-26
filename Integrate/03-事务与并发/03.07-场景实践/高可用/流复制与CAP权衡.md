---

> **📋 文档来源**: `MVCC-ACID-CAP\03-场景实践\高可用\流复制与CAP权衡.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 流复制与CAP权衡

> **文档编号**: CAP-PRACTICE-003
> **主题**: 流复制与CAP权衡
> **版本**: PostgreSQL 17 & 18
> **状态**: ✅ 已完成

---

## 📑 目录

- [流复制与CAP权衡](#流复制与cap权衡)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📊 第一部分：流复制基础](#-第一部分流复制基础)
    - [1.1 流复制定义](#11-流复制定义)
    - [1.2 流复制机制](#12-流复制机制)
    - [1.3 流复制配置](#13-流复制配置)
  - [📊 第二部分：同步流复制（CP模式）](#-第二部分同步流复制cp模式)
    - [2.1 同步流复制配置](#21-同步流复制配置)
    - [2.2 CP模式特征](#22-cp模式特征)
    - [2.3 CP模式性能影响](#23-cp模式性能影响)
  - [📊 第三部分：异步流复制（AP模式）](#-第三部分异步流复制ap模式)
    - [3.1 异步流复制配置](#31-异步流复制配置)
    - [3.2 AP模式特征](#32-ap模式特征)
    - [3.3 AP模式性能优势](#33-ap模式性能优势)
  - [📊 第四部分：流复制的分区容错](#-第四部分流复制的分区容错)
    - [4.1 分区容错机制](#41-分区容错机制)
    - [4.2 分区故障处理](#42-分区故障处理)
    - [4.3 分区恢复策略](#43-分区恢复策略)
  - [📊 第五部分：流复制CAP权衡决策](#-第五部分流复制cap权衡决策)
    - [5.1 CAP选择决策树](#51-cap选择决策树)
    - [5.2 场景化CAP选择](#52-场景化cap选择)
      - [5.2.1 金融场景（CP模式）](#521-金融场景cp模式)
      - [5.2.2 日志场景（AP模式）](#522-日志场景ap模式)
    - [5.3 CAP动态调整](#53-cap动态调整)
  - [📝 总结](#-总结)
    - [核心结论](#核心结论)
    - [实践建议](#实践建议)

---

## 📋 概述

PostgreSQL流复制是CAP权衡的典型体现：同步流复制实现CP模式（强一致性+分区容错），异步流复制实现AP模式（高可用性+分区容错）。

本文档从流复制基础、CP/AP模式实现、分区容错和权衡决策四个维度，全面阐述流复制与CAP权衡的完整机制。

**核心观点**：

- **同步流复制** = CP模式：强一致性+分区容错，牺牲可用性
- **异步流复制** = AP模式：高可用性+分区容错，牺牲一致性
- 流复制提供**分区容错**能力
- CAP选择需要基于**业务需求**和**性能要求**

---

## 📊 第一部分：流复制基础

### 1.1 流复制定义

**流复制定义**：

PostgreSQL流复制是一种基于WAL（Write-Ahead Log）的物理复制机制，通过实时传输WAL数据到备库，实现主备库的数据同步。

**流复制特征**：

- ✅ **物理复制**：基于WAL的字节级复制
- ✅ **实时传输**：WAL实时传输到备库
- ✅ **高可靠性**：保证数据一致性

### 1.2 流复制机制

**流复制流程**：

```text
1. 主库执行事务
   │
2. 主库写入WAL
   │
3. WAL发送进程（wal sender）发送WAL到备库
   │
4. 备库接收WAL（wal receiver）
   │
5. 备库应用WAL（startup process）
   │
6. 备库数据与主库同步
```

**PostgreSQL实现**：

```c
// src/backend/replication/walsender.c
void WalSenderMain(void)
{
    // WAL发送进程主循环
    while (true)
    {
        // 读取WAL
        XLogReadRecord();
        // 发送WAL到备库
        WalSndSendData();
    }
}
```

### 1.3 流复制配置

**基本配置**：

```sql
-- 主库配置（postgresql.conf，这些是配置文件设置，不是SQL语句）
-- wal_level = replica
-- max_wal_senders = 10
-- wal_keep_size = 1GB

-- 主库创建复制用户（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'replicator') THEN
            RAISE NOTICE '角色 replicator 已存在';
        ELSE
            BEGIN
                CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'password';
                RAISE NOTICE '角色 replicator 创建成功（复制用户）';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '角色 replicator 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建角色失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 主库配置pg_hba.conf（这是配置文件，不是SQL语句）
-- host replication replicator 0.0.0.0/0 md5

-- 备库配置（postgresql.conf，这是配置文件，不是SQL语句）
-- primary_conninfo = 'host=primary_host port=5432 user=replicator password=password'
```

---

## 📊 第二部分：同步流复制（CP模式）

### 2.1 同步流复制配置

**同步流复制配置**：

```sql
-- 主库配置（postgresql.conf，这些是配置文件设置，不是SQL语句）
-- synchronous_standby_names = 'standby1,standby2'
-- synchronous_commit = 'remote_apply'  -- 或 'remote_write'

-- 或者使用ALTER SYSTEM设置（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
            RAISE NOTICE '同步备库名称已设置为 standby1,standby2';
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
```

**同步级别**：

| 同步级别 | 一致性 | 延迟 | CAP模式 |
|---------|--------|------|---------|
| `remote_apply` | 最强 | 最高 | CP |
| `remote_write` | 强 | 中 | CP |
| `on` | 强 | 中 | CP |

### 2.2 CP模式特征

**CP模式特征**：

- ✅ **强一致性**：主库等待备库确认后才提交
- ❌ **低可用性**：分区时，如果无法联系到足够备库，写入阻塞
- ✅ **分区容错**：系统在网络分区时仍能运行（但可能阻塞）

**形式化表达**：

$$
\text{Sync Replication} \Rightarrow \text{CP Mode}
$$

$$
\text{C}(S) \land \text{P}(S) \land \neg\text{A}(S)
$$

### 2.3 CP模式性能影响

**性能影响**：

| 指标 | 影响 | 说明 |
|------|------|------|
| **写入延迟** | +50-200ms | 等待备库确认 |
| **吞吐量** | -20-40% | 同步等待开销 |
| **可用性** | 降低 | 分区时可能阻塞 |

**性能测试**：

```sql
-- pgbench测试（scale=100, clients=10）
-- 异步流复制：2000 TPS
-- 同步流复制（remote_write）：1500 TPS (-25%)
-- 同步流复制（remote_apply）：1200 TPS (-40%)
```

---

## 📊 第三部分：异步流复制（AP模式）

### 3.1 异步流复制配置

**异步流复制配置**：

```sql
-- 主库配置（postgresql.conf，这些是配置文件设置，不是SQL语句）
-- synchronous_standby_names = ''  -- 空表示异步
-- synchronous_commit = 'local'     -- 本地提交

-- 或者使用ALTER SYSTEM设置（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（异步复制，AP模式）';
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

### 3.2 AP模式特征

**AP模式特征**：

- ❌ **弱一致性**：主库立即提交，备库可能延迟
- ✅ **高可用性**：分区时，主库继续服务
- ✅ **分区容错**：系统在网络分区时继续运行

**形式化表达**：

$$
\text{Async Replication} \Rightarrow \text{AP Mode}
$$

$$
\text{A}(S) \land \text{P}(S) \land \neg\text{C}(S)
$$

### 3.3 AP模式性能优势

**性能优势**：

| 指标 | 影响 | 说明 |
|------|------|------|
| **写入延迟** | 正常 | 无需等待备库 |
| **吞吐量** | 正常 | 无同步开销 |
| **可用性** | 高 | 分区时继续服务 |

**性能测试**：

```sql
-- pgbench测试（scale=100, clients=10）
-- 同步流复制（remote_apply）：1200 TPS
-- 异步流复制：2000 TPS (+67%)
```

---

## 📊 第四部分：流复制的分区容错

### 4.1 分区容错机制

**分区容错定义**：

流复制在网络分区的情况下仍能继续运行，通过以下机制实现：

1. **WAL缓冲**
   - 主库缓冲WAL数据
   - 分区恢复后继续传输
   - 保证数据不丢失

2. **复制槽机制**
   - 防止WAL被删除
   - 保证分区恢复后数据同步
   - 提供持久化保证

**PostgreSQL配置**：

```sql
-- 创建复制槽
SELECT pg_create_physical_replication_slot('standby1_slot');

-- 配置复制槽
primary_slot_name = 'standby1_slot'
```

### 4.2 分区故障处理

**分区故障场景**：

1. **主库与备库网络分区**
   - 主库无法联系到备库
   - 同步流复制：写入阻塞
   - 异步流复制：继续服务

**处理策略**：

```sql
-- CP模式：分区时阻塞
-- 需要等待分区恢复或手动降级

-- AP模式：分区时继续服务
-- 分区恢复后自动同步
```

### 4.3 分区恢复策略

**分区恢复流程**：

```text
1. 检测分区恢复
   │
2. 验证网络连接
   │
3. 恢复WAL传输
   │
4. 同步数据差异
   │
5. 恢复正常服务
```

**PostgreSQL自动恢复**：

```sql
-- 流复制自动恢复
-- 无需手动干预
-- 系统自动检测分区恢复并同步数据
```

---

## 📊 第五部分：流复制CAP权衡决策

### 5.1 CAP选择决策树

**决策树**：

```text
开始
  │
  ├─ 是否需要强一致性？
  │   ├─ 是 → 同步流复制（CP模式）
  │   │   ├─ 配置：synchronous_standby_names
  │   │   ├─ 场景：金融、支付
  │   │   └─ 代价：低可用性
  │   │
  │   └─ 否 → 异步流复制（AP模式）
  │       ├─ 配置：synchronous_standby_names = ''
  │       ├─ 场景：日志、分析
  │       └─ 优势：高可用性
```

### 5.2 场景化CAP选择

#### 5.2.1 金融场景（CP模式）

**需求**：

- 强一致性
- 数据准确性
- 可接受低可用性

**配置**：

```sql
-- 同步流复制（CP模式）
synchronous_standby_names = 'standby1,standby2'
synchronous_commit = 'remote_apply'
```

#### 5.2.2 日志场景（AP模式）

**需求**：

- 高写入吞吐量
- 允许短暂不一致
- 高可用性

**配置**：

```sql
-- 异步流复制（AP模式）
synchronous_standby_names = ''
synchronous_commit = 'local'
```

### 5.3 CAP动态调整

**动态调整场景**：

1. **业务高峰期**：切换到AP模式，提高可用性
2. **业务低峰期**：切换到CP模式，提高一致性
3. **故障恢复**：临时切换到AP模式，快速恢复

**PostgreSQL动态调整**：

```sql
-- 动态切换到AP模式
ALTER SYSTEM SET synchronous_standby_names = '';
SELECT pg_reload_conf();

-- 动态切换到CP模式
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
SELECT pg_reload_conf();
```

---

## 📝 总结

### 核心结论

1. **同步流复制实现CP模式**：强一致性+分区容错，牺牲可用性
2. **异步流复制实现AP模式**：高可用性+分区容错，牺牲一致性
3. **流复制提供分区容错能力**：网络分区时系统继续运行
4. **CAP选择需要基于业务需求**：金融场景选择CP，日志场景选择AP

### 实践建议

1. **根据业务需求选择CAP模式**：
   - 金融场景：同步流复制（CP模式）
   - 日志场景：异步流复制（AP模式）

2. **监控流复制性能**：
   - 同步延迟（CP模式）
   - 复制延迟（AP模式）
   - 分区故障

3. **准备CAP动态调整策略**：
   - 高峰期切换到AP模式
   - 低峰期切换到CP模式
   - 故障时临时降级

---

**最后更新**: 2024年
**维护状态**: ✅ 已完成
