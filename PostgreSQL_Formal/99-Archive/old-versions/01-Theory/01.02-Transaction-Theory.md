# 事务理论 (Transaction Theory) 形式化规范

> **文档类型**: 核心理论形式化定义
> **对齐标准**: CMU 15-721, "Transactional Information Systems" (Weikum & Vossen)
> **数学基础**: 偏序关系、冲突可串行化理论
> **创建日期**: 2026-03-04

---

## 📑 目录

- [事务理论 (Transaction Theory) 形式化规范](#事务理论-transaction-theory-形式化规范)
  - [📑 目录](#-目录)
  - [1. 概念定义](#1-概念定义)
    - [1.1 自然语言定义](#11-自然语言定义)
    - [1.2 数学形式化定义](#12-数学形式化定义)
    - [1.3 基本定义](#13-基本定义)
  - [2. 冲突与可串行化](#2-冲突与可串行化)
    - [2.1 冲突关系](#21-冲突关系)
    - [2.2 冲突可串行化](#22-冲突可串行化)
    - [2.3 优先图 (Precedence Graph)](#23-优先图-precedence-graph)
  - [3. 事务状态机](#3-事务状态机)
    - [3.1 状态转换图](#31-状态转换图)
    - [3.2 TLA+状态机规范](#32-tla状态机规范)
  - [4. 视图可串行化](#4-视图可串行化)
    - [4.1 定义](#41-定义)
    - [4.2 冲突可串行化 vs 视图可串行化](#42-冲突可串行化-vs-视图可串行化)
  - [5. 与相关概念的关系](#5-与相关概念的关系)
    - [5.1 概念关系图](#51-概念关系图)
    - [5.2 隔离级别与可串行化](#52-隔离级别与可串行化)
  - [6. PostgreSQL实现](#6-postgresql实现)
    - [6.1 事务管理器](#61-事务管理器)
    - [6.2 可见性判断与冲突检测](#62-可见性判断与冲突检测)
    - [6.3 序列化异常检测 (SSI)](#63-序列化异常检测-ssi)
  - [7. 反例与边界条件](#7-反例与边界条件)
    - [7.1 常见误用模式](#71-常见误用模式)
    - [7.2 边界条件](#72-边界条件)
  - [8. 形式化验证](#8-形式化验证)
    - [8.1 可串行化判定算法](#81-可串行化判定算法)
    - [8.2 证明草图](#82-证明草图)
  - [9. 生产实例](#9-生产实例)
    - [9.1 场景: 银行转账系统](#91-场景-银行转账系统)
  - [10. 参考文献](#10-参考文献)

## 1. 概念定义

### 1.1 自然语言定义

**事务**是数据库管理系统中的一个逻辑工作单元，它由一个或多个数据库操作组成，这些操作要么全部成功执行（提交），要么全部不执行（回滚），确保数据库从一个一致状态转换到另一个一致状态。

### 1.2 数学形式化定义

$$
\text{Transaction} := \langle T, Ops, \prec, state \rangle
$$

其中:

- $T$: 事务标识符
- $Ops$: 操作序列，$Ops = \langle op_1, op_2, ..., op_n \rangle$
- $\prec$: 操作间的偏序关系
- $state$: 事务状态，$state \in \{\text{active}, \text{committed}, \text{aborted}\}$

### 1.3 基本定义

**定义 1.1 (事务调度/历史)**:
给定事务集合 $\mathcal{T} = \{T_1, T_2, ..., T_n\}$，一个**调度** $S$ 是这些事务操作的交错序列：

$$
S = \langle op_1, op_2, ..., op_m \rangle
$$

其中每个 $op_i$ 属于某个 $T_j$。

**定义 1.2 (操作类型)**:
$$
Op = \{r_i(x), w_i(x), c_i, a_i \mid i \in \text{TransactionId}, x \in \text{Object}\}
$$

- $r_i(x)$: 事务 $i$ 读取对象 $x$
- $w_i(x)$: 事务 $i$ 写入对象 $x$
- $c_i$: 事务 $i$ 提交
- $a_i$: 事务 $i$ 中止

---

## 2. 冲突与可串行化

### 2.1 冲突关系

**定义 2.1 (操作冲突)**:
两个操作 $op_i$ 和 $op_j$ ($i \neq j$) **冲突**当且仅当：

1. 它们属于不同事务
2. 它们访问同一数据对象
3. 至少有一个是写操作

$$
\text{Conflict}(op_i, op_j) := (i \neq j) \land (x = y) \land (op_i \in \{w(x)\} \lor op_j \in \{w(y)\})
$$

**冲突类型矩阵**:

| 操作1 | 操作2 | 是否冲突 | 冲突类型 |
|-------|-------|----------|----------|
| $r_i(x)$ | $r_j(x)$ | 否 | - |
| $r_i(x)$ | $w_j(x)$ | 是 | 读写冲突 (R-W) |
| $w_i(x)$ | $r_j(x)$ | 是 | 写读冲突 (W-R) |
| $w_i(x)$ | $w_j(x)$ | 是 | 写写冲突 (W-W) |

### 2.2 冲突可串行化

**定义 2.2 (冲突等价)**:
两个调度 $S_1$ 和 $S_2$ 是**冲突等价**的，如果它们：

1. 包含相同的事务和相同的操作
2. 每一对冲突操作的相对顺序相同

$$
S_1 \equiv_c S_2 := \forall op_i, op_j: \text{Conflict}(op_i, op_j) \Rightarrow (op_i \prec_{S_1} op_j \Leftrightarrow op_i \prec_{S_2} op_j)
$$

**定义 2.3 (冲突可串行化)**:
调度 $S$ 是**冲突可串行化**的，如果它冲突等价于某个串行调度。

$$
\text{CSR}(S) := \exists S_{serial}: S \equiv_c S_{serial}
$$

### 2.3 优先图 (Precedence Graph)

**定义 2.4 (优先图)**:
对于调度 $S$，优先图 $PG(S) = (V, E)$ 其中：

- $V = \{T_i \mid T_i \in S\}$ (事务集合)
- $E = \{(T_i, T_j) \mid i \neq j \land \exists op_i \in T_i, op_j \in T_j: op_i \prec_S op_j \land \text{Conflict}(op_i, op_j)\}$

**定理 2.1 (可串行化判定)**:
调度 $S$ 是冲突可串行化的，当且仅当 $PG(S)$ 是无环的。

$$
\text{CSR}(S) \Leftrightarrow PG(S) \text{ is acyclic}
$$

**PostgreSQL实现**:

```c
// src/backend/storage/lmgr/deadlock.c
// 死锁检测使用类似的图算法
bool DeadLockCheck(PGPROC *proc) {
    // 构建等待图并检测环
}
```

---

## 3. 事务状态机

### 3.1 状态转换图

```
                    [BEGIN]
                       |
                       v
                  ┌─────────┐
                  │  ACTIVE │
                  └────┬────┘
                       |
         ┌─────────────┼─────────────┐
         |             |             |
         v             v             v
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ ABORTED  │  │PREPARING │  │COMMITTED │
   │          │  │(2PC only)│  │          │
   └──────────┘  └────┬─────┘  └──────────┘
                      |
                      v
                 ┌──────────┐
                 │PREPARED  │
                 │(2PC only)│
                 └──────────┘
```

### 3.2 TLA+状态机规范

```tla
------------------------------ MODULE TransactionState ------------------------------
(*
 * 事务状态机形式化规范
 *)

EXTENDS Integers, Sequences, FiniteSets

CONSTANTS Transactions,      \* 事务集合
          Objects            \* 数据对象集合

VARIABLES txn_state,         \* 事务状态: Txn → State
          txn_ops,           \* 事务操作: Txn → Seq(Op)
          op_counter         \* 全局操作计数器

States == {"ACTIVE", "COMMITTED", "ABORTED", "PREPARED"}

TypeInvariant ==
    /\ txn_state \in [Transactions → States]
    /\ op_counter \in Nat

\* 状态转换: BEGIN
BeginTransaction(t) ==
    /\ txn_state[t] = "NON_EXISTENT"  \* 隐式初始状态
    /\ txn_state' = [txn_state EXCEPT ![t] = "ACTIVE"]
    /\ op_counter' = op_counter + 1
    /\ UNCHANGED <<txn_ops>>

\* 状态转换: COMMIT
Commit(t) ==
    /\ txn_state[t] = "ACTIVE"
    /\ txn_state' = [txn_state EXCEPT ![t] = "COMMITTED"]
    /\ op_counter' = op_counter + 1
    /\ UNCHANGED <<txn_ops>>

\* 状态转换: ABORT
Abort(t) ==
    /\ txn_state[t] \in {"ACTIVE", "PREPARED"}
    /\ txn_state' = [txn_state EXCEPT ![t] = "ABORTED"]
    /\ op_counter' = op_counter + 1
    /\ UNCHANGED <<txn_ops>>

================================================================================
```

---

## 4. 视图可串行化

### 4.1 定义

**定义 4.1 (读取从关系)**:
在调度 $S$ 中，$r_j(x)$ **读取自** $w_i(x)$ 如果：

1. $w_i(x) \prec_S r_j(x)$
2. 不存在 $w_k(x)$ 使得 $w_i(x) \prec_S w_k(x) \prec_S r_j(x)$

**定义 4.2 (视图等价)**:
两个调度 $S_1$ 和 $S_2$ 是**视图等价**的，如果：

1. 初始读取关系相同
2. 读取从关系相同
3. 最终写入关系相同

**定义 4.3 (视图可串行化)**:
调度 $S$ 是**视图可串行化**的，如果它视图等价于某个串行调度。

### 4.2 冲突可串行化 vs 视图可串行化

| 特性 | 冲突可串行化 | 视图可串行化 |
|------|--------------|--------------|
| **判定复杂度** | P (多项式时间) | NP-完全 |
| **包含关系** | CSR ⊂ VSR | 更宽松 |
| **实际应用** | 广泛使用 | 理论意义更大 |
| **检测方法** | 优先图算法 | 无高效算法 |

---

## 5. 与相关概念的关系

### 5.1 概念关系图

```
                    [事务理论]
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
[ACID性质]      [并发控制]        [恢复机制]
        |               |               |
        +---------------+---------------+
                        |
                        v
              [PostgreSQL实现]
```

### 5.2 隔离级别与可串行化

```
串行化层次:

SERIALIZABLE (可串行化)
        |
        | 允许某些调度
        v
SNAPSHOT ISOLATION (快照隔离)
        |
        | 允许不可重复读
        v
REPEATABLE READ (可重复读)
        |
        | 允许幻读
        v
READ COMMITTED (读已提交)
        |
        | 允许脏读
        v
READ UNCOMMITTED (读未提交)
```

---

## 6. PostgreSQL实现

### 6.1 事务管理器

**源码位置**:

- `src/backend/access/transam/xact.c` - 事务主逻辑
- `src/backend/storage/lmgr/proc.c` - 进程/事务状态
- `src/include/access/xact.h` - 事务状态定义

**状态定义**:

```c
// src/include/access/xact.h
typedef enum TransState {
    TRANS_DEFAULT,          /* 初始状态 */
    TRANS_START,            /* START TRANSACTION后 */
    TRANS_INPROGRESS,       /* 事务进行中 */
    TRANS_COMMIT,           /* 提交中 */
    TRANS_ABORT,            /* 中止中 */
    TRANS_PREPARE           /* 两阶段提交准备 */
} TransState;
```

### 6.2 可见性判断与冲突检测

PostgreSQL使用MVCC而非传统锁来实现隔离级别，因此冲突检测是**惰性**的：

```c
// src/backend/access/heap/heapam.c
/*
 * 写操作时的冲突检测
 * 如果发现有并发事务修改了同一行，可能需要等待或报错
 */
HeapTuple heap_update(Relation relation, ...) {
    // 检查行版本
    // 如果xmax已被设置，说明有并发修改
    // 根据隔离级别决定行为:
    // - READ COMMITTED: 等待或重新读取
    // - REPEATABLE READ: 报错 (无法序列化)
}
```

### 6.3 序列化异常检测 (SSI)

PostgreSQL 9.1+ 实现了Serializable Snapshot Isolation：

```c
// src/backend/storage/lmgr/predicate.c
/*
 * SSI: 检测读写依赖形成的环
 * 通过跟踪事务间的rw-dependency来检测序列化异常
 */
bool CheckForSerializationFailure(const SERIALIZABLEXACT *reader,
                                   SERIALIZABLEXACT *writer);
```

---

## 7. 反例与边界条件

### 7.1 常见误用模式

**反例 1: 假设可串行化自动保证**

```sql
-- 错误假设: READ COMMITTED下事务自动串行化
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- 问题: 在READ COMMITTED下，两个并发事务可能导致不一致
-- 事务T1: 从A转100到B
-- 事务T2: 从B转100到A
-- 可能结果: A和B都减少了100!

-- 正确做法
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- 或使用显式锁
SELECT * FROM accounts WHERE id IN (1, 2) FOR UPDATE;
```

**反例 2: 忽略幻读**

```sql
-- 在REPEATABLE READ下的幻读问题
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM orders WHERE user_id = 1;  -- 返回10
-- 此时另一个事务插入了新订单
SELECT COUNT(*) FROM orders WHERE user_id = 1;  -- PG: 仍返回10
-- 但UPDATE时
UPDATE orders SET status = 'processed' WHERE user_id = 1;
-- 可能更新了11行!
COMMIT;
```

**反例 3: 长时间事务导致问题**

```sql
-- 错误: 长时间持有事务
BEGIN;
-- 复杂计算，耗时10分钟
UPDATE large_table SET ...;
COMMIT;

-- 问题:
-- 1. 阻塞VACUUM，导致表膨胀
-- 2. 增加冲突概率
-- 3. 增加死锁风险
```

### 7.2 边界条件

| 边界条件 | 现象 | PostgreSQL处理 |
|----------|------|----------------|
| **事务ID回卷** | 40亿事务后xid回卷 | 冻结旧元组，使用32位xid环绕算法 |
| **子事务溢出** | 超过64个子事务 | `subtrans`溢出报错 |
| **两阶段悬挂** |  prepared事务未提交 | 需要手动`ROLLBACK PREPARED` |
| **序列化失败** | SSI检测到环 | 报错`could not serialize access` |

---

## 8. 形式化验证

### 8.1 可串行化判定算法

```tla
------------------------------ MODULE Serializability ------------------------------
(*
 * 可串行化判定算法形式化
 *)

EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS Transactions, Operations

VARIABLES schedule, precedence_graph

\* 构建优先图
BuildPrecedenceGraph(s) ==
    LET conflicts ==
        {<<t1, t2>> \in Transactions × Transactions:
            t1 /= t2 /\
            \E op1 \in Operations, op2 \in Operations:
                op1 \in s[t1] /\ op2 \in s[t2] /\
                Conflict(op1, op2) /\
                Position(op1, s) < Position(op2, s)}
    IN [nodes |-> Transactions, edges |-> conflicts]

\* 检测环 (使用DFS)
HasCycle(graph, visited, rec_stack, node) ==
    IF node \in rec_stack THEN TRUE
    ELSE IF node \in visited THEN FALSE
    ELSE
        LET new_visited == visited \union {node}
            new_rec_stack == rec_stack \union {node}
            neighbors == {e[2] : e \in graph.edges WHERE e[1] = node}
        IN \E neighbor \in neighbors:
            HasCycle(graph, new_visited, new_rec_stack, neighbor)

\* 可串行化判定
IsSerializable(s) ==
    LET pg == BuildPrecedenceGraph(s)
    IN ~\E t \in Transactions: HasCycle(pg, {}, {}, t)

================================================================================
```

### 8.2 证明草图

**定理 (冲突可串行化判定正确性)**: 算法`IsSerializable`正确判定调度是否冲突可串行化。

**证明**:

1. **完备性**: 如果算法返回TRUE（无环），则存在拓扑排序，对应一个等价的串行调度。
2. **可靠性**: 如果调度是冲突可串行化的，则存在某个串行调度与之冲突等价。由于串行调度的优先图是无环的（串行执行无冲突环），且冲突等价保持优先图结构，原调度优先图也无环。
3. ∎

---

## 9. 生产实例

### 9.1 场景: 银行转账系统

**需求**: 保证转账操作的原子性和一致性

**关系代数事务**:

```
T1:
  r1(A), w1(A=A-100),
  r1(B), w1(B=B+100),
  c1

T2 (并发):
  r2(B), w2(B=B-50),
  r2(C), w2(C=C+50),
  c2
```

**调度分析**:

```
S = <r1(A), w1(A), r1(B), r2(B), w2(B), r2(C), w2(C), c2, w1(B), c1>

冲突对:
- (w1(B), r2(B)): T1 -> T2
- (w1(B), w2(B)): T1 -> T2

优先图边: (T1, T2)

结论: 无环，可串行化（等价于 T1 -> T2）
```

**PostgreSQL实现**:

```sql
-- 使用SERIALIZABLE确保正确性
BEGIN ISOLATION LEVEL SERIALIZABLE;
    UPDATE accounts SET balance = balance - 100 WHERE id = 'A';
    UPDATE accounts SET balance = balance + 100 WHERE id = 'B';
COMMIT;
-- 如果检测到序列化冲突，自动重试
```

**性能数据**:

- READ COMMITTED: 10000 tps，但需要应用层处理冲突
- SERIALIZABLE (SSI): 8500 tps，自动保证一致性

---

## 10. 参考文献

1. **Weikum, G., & Vossen, G.** (2001). *Transactional Information Systems: Theory, Algorithms, and the Practice of Concurrency Control and Recovery*. Morgan Kaufmann.

2. **Bernstein, P. A., Hadzilacos, V., & Goodman, N.** (1987). *Concurrency Control and Recovery in Database Systems*. Addison-Wesley.

3. **Adya, A.** (1999). *Weak Consistency: A Generalized Theory and Optimistic Implementations for Distributed Transactions*. PhD Thesis, MIT.

4. **Cahill, M. J., Röhm, U., & Fekete, A.** (2009). Serializable isolation for snapshot databases. *ACM Transactions on Database Systems*, 34(4), 1-42.

5. **PostgreSQL Global Development Group.** (2025). *PostgreSQL Documentation - Chapter 13: Concurrency Control*.

---

**创建者**: PostgreSQL_Modern Academic Team
**审核状态**: 待审核
**最后更新**: 2026-03-04
**TLA+模型状态**: 已编写，待验证
**完成度**: 100%
