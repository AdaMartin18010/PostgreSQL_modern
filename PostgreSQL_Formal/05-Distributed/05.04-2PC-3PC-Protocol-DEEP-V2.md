# 2PC/3PC协议深度形式化 V2

> **文档类型**: 分布式系统 (DEEP-V2学术深度版本)
> **对齐标准**: "Distributed Systems" (van Steen), "Principles of Distributed Computing" (Wattenhofer)
> **数学基础**: 分布式算法理论、状态机复制、共识理论
> **版本**: DEEP-V2 | 字数: ~6500字
> **创建日期**: 2026-03-04

---

## 📑 目录

- [2PC/3PC协议深度形式化 V2](#2pc3pc协议深度形式化-v2)
  - [📑 目录](#-目录)
  - [1. 分布式事务理论基础](#1-分布式事务理论基础)
    - [1.1 分布式事务模型](#11-分布式事务模型)
    - [1.2 分布式系统特性](#12-分布式系统特性)
    - [1.3 一致性层次](#13-一致性层次)
  - [2. 两阶段提交 (2PC) 形式化](#2-两阶段提交-2pc-形式化)
    - [2.1 协议定义](#21-协议定义)
    - [2.2 协议阶段](#22-协议阶段)
    - [2.3 状态机模型](#23-状态机模型)
    - [2.4 日志记录](#24-日志记录)
  - [3. 三阶段提交 (3PC) 形式化](#3-三阶段提交-3pc-形式化)
    - [3.1 协议动机](#31-协议动机)
    - [3.2 协议定义](#32-协议定义)
    - [3.3 协议阶段](#33-协议阶段)
    - [3.4 3PC状态机](#34-3pc状态机)
    - [3.5 超时处理](#35-超时处理)
  - [4. 故障恢复与正确性](#4-故障恢复与正确性)
    - [4.1 故障场景分析](#41-故障场景分析)
    - [4.2 恢复算法](#42-恢复算法)
    - [4.3 2PC vs 3PC对比](#43-2pc-vs-3pc对比)
  - [5. CAP定理与权衡](#5-cap定理与权衡)
    - [5.1 CAP定理形式化](#51-cap定理形式化)
    - [5.2 CAP权衡空间](#52-cap权衡空间)
    - [5.3 PACELC定理](#53-pacelc定理)
    - [5.4 分布式事务与CAP](#54-分布式事务与cap)
  - [6. PostgreSQL分布式事务实现](#6-postgresql分布式事务实现)
    - [6.1 PostgreSQL两阶段提交](#61-postgresql两阶段提交)
    - [6.2 PostgreSQL 2PC实现细节](#62-postgresql-2pc实现细节)
    - [6.3 分布式事务监控](#63-分布式事务监控)
    - [6.4 外部事务管理器集成](#64-外部事务管理器集成)
  - [7. 现代替代方案](#7-现代替代方案)
    - [7.1 TCC模式](#71-tcc模式)
    - [7.2 Saga模式](#72-saga模式)
    - [7.3 共识协议](#73-共识协议)
  - [8. 形式化证明](#8-形式化证明)
    - [8.1 2PC安全性证明](#81-2pc安全性证明)
    - [8.2 2PC阻塞性证明](#82-2pc阻塞性证明)
    - [8.3 3PC非阻塞证明](#83-3pc非阻塞证明)
  - [9. 参考文献](#9-参考文献)

---

## 1. 分布式事务理论基础

### 1.1 分布式事务模型

**定义 1.1 (分布式事务)**:

分布式事务 D 是跨越多个节点的操作集合:

$$
D = \{T_1, T_2, ..., T_n\}
$$

其中每个 T_i 在节点 N_i 上执行，所有子事务必须原子性完成。

**定义 1.2 (全局提交)**:

$$
\text{Commit}(D) \iff \forall T_i \in D: \text{Commit}(T_i)
$$

**定义 1.3 (全局中止)**:

$$
\text{Abort}(D) \iff \exists T_i \in D: \text{Abort}(T_i)
$$

### 1.2 分布式系统特性

**网络模型**:

| 特性 | 同步网络 | 异步网络 |
|------|----------|----------|
| 消息延迟 | 有上界 | 无保证 |
| 时钟同步 | 近似 | 无保证 |
| 故障检测 | 可靠 | 不可靠 |
| 实际系统 | 数据中心内 | 广域网 |

**故障类型**:

$$
\mathcal{F} = \{crash, omission, timing, Byzantine\}
$$

### 1.3 一致性层次

```text
一致性强度层次:

强一致性 ---------------------------------------------------▶ 弱一致性
    │
    ├── 线性一致性 (Linearizability)
    │
    ├── 顺序一致性 (Sequential Consistency)
    │
    ├── 因果一致性 (Causal Consistency)
    │
    ├── 会话一致性 (Session Consistency)
    │
    └── 最终一致性 (Eventual Consistency)
```

---

## 2. 两阶段提交 (2PC) 形式化

### 2.1 协议定义

**参与者集合**:

$$
\mathcal{P} = \{P_1, P_2, ..., P_n\} \cup \{C\}
$$

其中 C 为协调者 (Coordinator)，P_i 为参与者。

**消息集合**:

$$
\mathcal{M}_{2PC} = \{Prepare, Yes, No, Commit, Abort, Ack\}
$$

### 2.2 协议阶段

**Phase 1: 准备阶段 (Prepare Phase)**:

```text
协调者C                参与者P1 ... Pn
  │                        │
  │───── Prepare ─────────>│
  │                        │ 写redo/undo日志
  │<───── Yes/No ──────────│
  │                        │
```

形式化:

$$
\forall P_i \in \mathcal{P}: C \xrightarrow{prepare} P_i
$$

$$
P_i \xrightarrow{vote_i} C \quad \text{where } vote_i \in \{Yes, No\}
$$

**Phase 2: 提交阶段 (Commit Phase)**:

```text
协调者C                参与者P1 ... Pn
  │                        │
  │───── Commit/Abort ────>│
  │                        │ 执行提交/回滚
  │<───── Ack ─────────────│
  │                        │
```

决策函数:

$$
\text{Decision}(C) = \begin{cases}
Commit & \text{if } \forall i: vote_i = Yes \\
Abort & \text{if } \exists i: vote_i = No
\end{cases}
$$

### 2.3 状态机模型

**协调者状态机**:

```text
        INIT
          │
          │ send Prepare
          ▼
      WAIT_VOTES
          │
          ├── 全部Yes ──→ COMMIT ──→ send Commit ──→ COMMITTED
          │
          └── 任意No ───→ ABORT ───→ send Abort ───→ ABORTED
```

**参与者状态机**:

```text
        INIT
          │
          │ receive Prepare
          ▼
      PREPARED ──→ 写prepare记录
          │
          ├── vote Yes ──→ READY
          │
          └── vote No ───→ ABORTED
          │
          │ receive Commit/Abort
          ▼
      COMMITTED / ABORTED
```

### 2.4 日志记录

**参与者日志**:

| 记录类型 | 写入时机 | 用途 |
|----------|----------|------|
| Prepare T | Phase 1 | 承诺参与提交 |
| Commit T | Phase 2 | 提交完成 |
| Abort T | Phase 2 | 中止完成 |
| Complete T | 结束 | 事务完成 |

**协调者日志**:

| 记录类型 | 写入时机 | 用途 |
|----------|----------|------|
| Start 2PC T | Phase 1开始 | 开始2PC |
| Commit T | Phase 2决定 | 全局提交 |
| Abort T | Phase 2决定 | 全局中止 |

---

## 3. 三阶段提交 (3PC) 形式化

### 3.1 协议动机

2PC的阻塞问题: 协调者崩溃后，参与者可能处于不确定状态，必须等待协调者恢复。

### 3.2 协议定义

**消息集合**:

$$
\mathcal{M}_{3PC} = \{CanCommit, Yes, No, PreCommit, Ack, DoCommit, HaveCommitted\}
$$

### 3.3 协议阶段

**Phase 1: 能否提交 (CanCommit)**

```text
协调者C                参与者P1 ... Pn
  │                        │
  │───── CanCommit? ──────>│
  │                        │ 检查本地状态
  │<───── Yes/No ──────────│
  │                        │
```

**Phase 2: 预提交 (PreCommit)**

```text
协调者C                参与者P1 ... Pn
  │                        │
  │───── PreCommit ───────>│
  │                        │ 写prepare记录
  │<───── Ack ─────────────│
  │                        │
```

**Phase 3: 执行提交 (DoCommit)**

```text
协调者C                参与者P1 ... Pn
  │                        │
  │───── DoCommit ────────>│
  │                        │ 执行提交
  │<───── HaveCommitted ───│
  │                        │
```

### 3.4 3PC状态机

**协调者状态机**:

```text
INIT ──→ CanCommit ──→ PreCommit ──→ DoCommit ──→ Committed
            │              │
            └── 超时 ──────┴── 超时 ──→ Abort
```

**参与者状态机**:

```text
INIT ──→ Ready ──→ PreCommit ──→ Committed
            │          │
            └── 超时 ──┴── 超时 ──→ Abort
```

### 3.5 超时处理

**协调者超时**:

| 当前状态 | 超时动作 |
|----------|----------|
| WAIT_CANCOMMIT | 发送Abort |
| WAIT_PRECOMMIT | 发送Abort |
| WAIT_DOCOMMIT | 发送DoCommit |

**参与者超时**:

| 当前状态 | 超时动作 |
|----------|----------|
| INIT | 可以单方面Abort |
| READY | 询问协调者 |
| PRECOMMIT | 可以单方面Commit |

---

## 4. 故障恢复与正确性

### 4.1 故障场景分析

**场景1: 协调者在Phase 1崩溃**

```text
参与者状态: INIT
动作: 单方面中止
安全性: ✓
```

**场景2: 协调者在Phase 2崩溃 (2PC)**

```text
参与者状态: PREPARED (不确定)
动作: 必须等待协调者恢复
安全性: ✓, 活性: ✗ (阻塞)
```

**场景3: 协调者在Phase 2崩溃 (3PC)**

```text
参与者状态: READY 或 PRECOMMIT
动作:
  - 如果知道其他参与者已Commit，则Commit
  - 否则，询问协调者或超时Abort
安全性: ✓, 活性: ✓ (非阻塞)
```

### 4.2 恢复算法

**协调者恢复**:

```text
1. 读取日志
2. 如果 Start 2PC T 存在:
   - 如果 Commit T 存在 → 重新发送Commit
   - 如果 Abort T 存在 → 重新发送Abort
   - 否则 → 中止事务
3. 等待参与者确认
```

**参与者恢复**:

```text
1. 读取日志
2. 如果 Prepare T 存在:
   - 如果 Commit T 存在 → 完成提交
   - 如果 Abort T 存在 → 完成中止
   - 否则 → 询问协调者
3. 如果无记录 → 无事可做
```

### 4.3 2PC vs 3PC对比

| 特性 | 2PC | 3PC |
|------|-----|-----|
| 网络轮次 | 2 | 3 |
| 消息复杂度 | 4n | 6n |
| 阻塞性 | 可能阻塞 | 非阻塞 |
| 故障容忍 | 单点故障 | 更好 |
| 实现复杂度 | 简单 | 复杂 |
| 实际使用 | 广泛 | 较少 |
| 超时处理 | 有限 | 完善 |

---

## 5. CAP定理与权衡

### 5.1 CAP定理形式化

**定理 5.1 (CAP定理)**:

分布式系统不可能同时保证:

- **一致性 (Consistency)**: 所有节点看到相同数据

  $$
  \forall n_1, n_2 \in N, \forall t: read_{n_1}(t) = read_{n_2}(t)
  $$

- **可用性 (Availability)**: 每个请求都收到响应

  $$
  \forall req: P[response(req)] = 1
  $$

- **分区容错性 (Partition Tolerance)**: 网络分区时系统继续运行

### 5.2 CAP权衡空间

```text
            一致性 (Consistency)
                 /
                /\
               /  \
              /    \
             /  CP  \
            /________\
分区容错性 /          \
(P)      /            \
        /    AP       \
       /  (NoSQL)     \
      /_______________

CP系统: BigTable, HBase, MongoDB (强一致性模式)
AP系统: Cassandra, Dynamo, CouchDB
```

### 5.3 PACELC定理

扩展CAP，引入延迟 (Latency) 与一致性 (Consistency) 的权衡:

**如果有分区 (P)**: Availability vs Consistency

**否则 (E - Else)**: Latency vs Consistency

### 5.4 分布式事务与CAP

| 协议 | CAP特性 | 适用场景 |
|------|---------|----------|
| 2PC | CP | 强一致性要求的金融系统 |
| 3PC | CP | 高可用要求的分布式系统 |
| Paxos/Raft | CP | 配置管理、元数据 |
| 最终一致性 | AP | 高并发互联网应用 |
| TCC模式 | AP | 长事务业务 |
| Saga模式 | AP | 微服务事务 |

---

## 6. PostgreSQL分布式事务实现

### 6.1 PostgreSQL两阶段提交

```sql
-- 会话1 (协调节点)
BEGIN;
-- 在多个节点执行操作
-- ...

-- 准备阶段
PREPARE TRANSACTION 'txn_001';

-- 收到所有参与者确认后
COMMIT PREPARED 'txn_001';
-- 或 ROLLBACK PREPARED 'txn_001';
```

**pg_prepared_xacts视图**:

```sql
SELECT * FROM pg_prepared_xacts;

-- 输出:
-- transaction | gid    | prepared           | owner | database
-- 12345       | txn_001| 2024-01-01 10:00:00| admin | mydb
```

### 6.2 PostgreSQL 2PC实现细节

**源码位置**: `src/backend/access/transam/twophase.c`

```c
/*
 * StartPrepare - 开始准备阶段
 */
void StartPrepare(GlobalTransaction gxact) {
    // 1. 记录准备日志
    XLogBeginInsert();
    XLogRegisterData(...);
    (void) XLogInsert(RM_XACT_ID, XLOG_XACT_PREPARE);

    // 2. 强制刷盘
    XLogFlush(gxact->prepare_end_lsn);

    // 3. 将事务状态改为PREPARED
    gxact->status = GXACT_PREPARED;
}

/*
 * FinishPreparedTransaction - 完成准备的事务
 */
void FinishPreparedTransaction(const char *gid, bool isCommit) {
    // 1. 查找准备好的事务
    gxact = LookupGXact(gid);

    // 2. 提交或回滚
    if (isCommit) {
        // 重放提交记录
        RecordTransactionCommitPrepared(...);
    } else {
        // 重放回滚记录
        RecordTransactionAbortPrepared(...);
    }

    // 3. 清理
    RemoveGXact(gxact);
}
```

### 6.3 分布式事务监控

```sql
-- 查看准备的事务
SELECT
    gid,
    prepared,
    owner,
    database,
    transaction AS xid
FROM pg_prepared_xacts;

-- 查看锁定情况
SELECT
    l.locktype,
    l.relation,
    l.mode,
    x.gid
FROM pg_locks l
JOIN pg_prepared_xacts x ON l.transaction = x.transaction;

-- 自动清理悬挂的准备事务
-- 使用max_prepared_transactions参数限制数量
SHOW max_prepared_transactions;
```

### 6.4 外部事务管理器集成

**XA协议支持**:

```text
应用程序
    │
    ├── JTA / JTS (Java)
    │
    ▼
XA Resource Manager
    │
    ├── XA SWITCH: PostgreSQL
    │
    ▼
PostgreSQL: PREPARE / COMMIT PREPARED
```

---

## 7. 现代替代方案

### 7.1 TCC模式

**Try-Confirm-Cancel**:

```text
Try阶段:    预留资源
            │
            ├── 成功 ──→ Confirm: 确认执行
            │
            └── 失败 ──→ Cancel: 取消预留
```

**适用场景**: 互联网高并发场景

**优点**: 无全局锁，高性能

**缺点**: 业务侵入性强，需实现补偿逻辑

### 7.2 Saga模式

**长事务拆分**:

```text
事务 T = T1 → T2 → T3 → ... → Tn
              │
              └── 失败时反向补偿
                  C2 → C1
```

**编排方式**:

- **编排式 (Choreography)**: 服务间通过事件协调
- **编排式 (Orchestration)**: 中央协调器管理流程

### 7.3 共识协议

**Raft协议**:

```text
领导者选举 ──→ 日志复制 ──→ 安全提交
```

**与2PC对比**:

| 特性 | Raft | 2PC |
|------|------|-----|
| 容错 | 多数派可用即可 | 需所有参与者 |
| 领导者 | 动态选举 | 固定协调者 |
| 消息数 | 2n | 4n |
| 使用场景 | 复制状态机 | 分布式事务 |

---

## 8. 形式化证明

### 8.1 2PC安全性证明

**定理 8.1 (2PC安全性)**:

如果任何参与者提交事务，则所有能提交的非故障参与者都会提交。

**证明**:

1. 协调者发送Commit决策当且仅当收到所有参与者的Yes投票
2. 参与者仅在收到Commit消息时提交
3. 如果参与者 P_i 提交，则它收到了Commit消息
4. 协调者发送Commit消息给所有参与者
5. 因此所有参与者都收到Commit消息并提交 ∎

### 8.2 2PC阻塞性证明

**定理 8.2 (2PC阻塞性)**:

在异步网络中，如果协调者在Phase 2崩溃，参与者可能阻塞。

**证明**:

1. 设协调者在发送Commit消息前崩溃
2. 参与者 P_i 处于PREPARED状态
3. P_i 不知道协调者的决策:
   - 可能协调者已发送Commit给其他节点
   - 可能协调者决定Abort
4. 如果 P_i 单方面决定:
   - 如果决定Commit但协调者决定Abort → 违反一致性
   - 如果决定Abort但协调者决定Commit → 违反一致性
5. 因此 P_i 必须等待协调者恢复 ∎

### 8.3 3PC非阻塞证明

**定理 8.3 (3PC非阻塞性)**:

在同步网络中，3PC是非阻塞的。

**证明草图**:

1. 3PC引入PreCommit状态作为中间状态
2. 如果参与者处于READY状态超时:
   - 可以安全地Abort，因为尚未承诺
3. 如果参与者处于PRECOMMIT状态超时:
   - 询问其他参与者
   - 如果任何参与者已Commit，则Commit
   - 如果协调者决定Abort，则Abort
   - 如果超时，可以Commit（因为已进入PRECOMMIT）
4. 通过超时机制，参与者总可以做出决策
5. 因此3PC是非阻塞的 ∎

---

## 9. 参考文献

1. **Gray, J., & Lamport, L.** (2006). Consensus on transaction commit. *ACM Transactions on Database Systems*, 31(1), 133-160.

2. **Skeen, D.** (1981). Nonblocking commit protocols. *SIGMOD'81*.

3. **Brewer, E.** (2000). Towards robust distributed systems. *PODC'00* (CAP定理首次提出).

4. **Gilbert, S., & Lynch, N.** (2002). Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services. *ACM SIGACT News*.

5. **van Steen, M., & Tanenbaum, A. S.** (2017). *Distributed Systems* (3rd ed.).

6. **PostgreSQL Global Development Group.** (2025). *PostgreSQL Documentation - PREPARE TRANSACTION*.

7. **Ongaro, D., & Ousterhout, J.** (2014). In search of an understandable consensus algorithm. *USENIX ATC'14* (Raft).

---

**创建者**: PostgreSQL_Modern Academic Team
**审核状态**: 学术级深度版本 (DEEP-V2)
**最后更新**: 2026-03-04
**完成度**: 100% (DEEP-V2)
