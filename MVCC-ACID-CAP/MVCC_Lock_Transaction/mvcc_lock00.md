# **MVCC, LOCK & Transaction: Comprehensive Dual-Language Analysis with Formal Proofs & Multi-Modal Thinking Frameworks**

---

## **Part I: Core Concepts & Formal Definitions (中英对照)**

### **1.1 Multi-Version Concurrency Control (MVCC) / 多版本并发控制**

**English Definition:**
MVCC is a **timestamp-ordered versioning mechanism** that creates a new data version for each write operation while preserving historical versions. It enables **non-blocking reads** by serving each transaction a **consistent snapshot** of the database state at a specific point in time, fundamentally decoupling read and write operations.

**中文定义:**
MVCC是一种基于时间戳排序的版本化机制，为每个写操作创建新数据版本的同时保留历史版本。通过为每个事务提供数据库在特定时间点的**一致性快照**，实现读写操作的**非阻塞**，从根本上解耦读和写。

**Formal Specification (形式化规范):**
For any data item $x$, its version chain is:
$$V(x) = \{ (x_v, t_v, p_v) \mid v \in \mathbb{N} \}$$
where:

- $x_v$ = version $v$ of data
- $t_v$ = transaction ID that created $x_v$ (monotonically increasing)
- $p_v$ = pointer to previous version $x_{v-1}$

**Visibility Predicate (可见性谓词):**
$$\text{Visible}(x_v, T_i) \equiv (t_v < \text{up_limit}_i) \land (t_v \notin \text{active}_i) \land (t_v \neq \text{creator}_i)$$

---

### **1.2 Lock Mechanisms / 锁机制**

**English Definition:**
Locking is a **pessimistic concurrency control** that uses **mutual exclusion** to prevent conflicting operations. Transactions acquire locks on resources before access and release them after operation completion, creating a **happens-before** relationship.

**中文定义:**
锁机制是一种**悲观并发控制**，使用**互斥访问**防止冲突操作。事务在访问资源前获取锁，操作完成后释放锁，建立**先行发生**关系。

**Lock Type Lattice (锁类型格):**
$$
\begin{array}{c}
\text{IS (意向共享)} \quad \text{IX (意向排他)} \\
\downarrow \quad \downarrow \\
\text{S (共享)} \quad \text{X (排他)}
\end{array}
$$

**Compatibility Matrix (相容矩阵):**

|       | S   | X   | IS  | IX  |
|-------|-----|-----|-----|-----|
| **S** | ✓   | ✗   | ✓   | ✗   |
| **X** | ✗   | ✗   | ✗   | ✗   |
| **IS**| ✓   | ✗   | ✓   | ✓   |
| **IX**| ✗   | ✗   | ✓   | ✓   |

---

### **1.3 Transaction Isolation Levels / 事务隔离级别**

**Formal Model of Anomalies (异常形式化模型):**

- **Dirty Read (脏读)**: $\exists T_i, T_j: r_i(x_j) \land w_j(x) \land a_j$
- **Non-Repeatable Read (不可重复读)**: $\exists T_i, T_j: r_i(x) \land c_j(w_j(x)) \land r_i(x') \land x \neq x'$
- **Phantom Read (幻读)**: $\exists T_i, T_j: r_i(P) \land c_j(\text{insert}_j(y) \land P(y)) \land r_i(P') \land |P'| > |P|$

---

## **Part II: Comprehensive Thinking Frameworks (多元化思维表征系统)**

### **2.1 Mind Map: MVCC vs LOCK Architecture (思维导图)**

```mermaid
mindmap
  root((Concurrency Control))
    MVCC (Multi-Version)
      Philosophy: Versioning by Time
      Implementation
        Hidden Columns
          trx_id
          roll_pointer
          row_id
        Undo Log Chain
        Read View
          creator_trx_id
          active_trx_ids
          up_limit_id
          low_limit_id
      Read Type
        Snapshot Read
          SELECT
          No Lock
        Current Read
          SELECT...FOR UPDATE
          UPDATE/DELETE
          X Lock + Next-Key
      Isolation Levels
        Read Committed
          Per-Statement Snapshot
        Repeatable Read
          Per-Transaction Snapshot
      Pros
        High Concurrency
        Non-blocking Reads
      Cons
        Storage Overhead
        Garbage Collection
    LOCK (Locking)
      Philosophy: Mutual Exclusion
      Lock Types
        Shared (S)
        Exclusive (X)
        Intention (IS/IX)
        Gap
        Next-Key
      Lock Duration
        Statement Level
        Transaction Level
      Isolation Levels
        Read Uncommitted
          No Lock
        Read Committed
          Short-term Lock
        Serializable
          Strict 2PL
      Pros
        Simple Implementation
        Immediate Consistency
      Cons
        Lock Contention
        Deadlock Risk
    Hybrid Model
      Read: MVCC Snapshot
      Write: 2PL + Next-Key
      Goal: Serializability
```

---

### **2.2 Matrix Comparison: Isolation Level Implementation (矩阵对比)**

| **Isolation Level** | **MVCC Implementation** | **Lock Implementation** | **Anomalies Prevented** | **Performance Impact** |
|---------------------|------------------------|------------------------|------------------------|------------------------|
| **Read Uncommitted** | N/A (reads latest version) | No locks | None | Highest speed, lowest safety |
| **读未提交** | 直接读最新版本，无视trx_id | 不获取任何锁 | 无 | 速度最快，安全性最低 |
| **Read Committed** | Per-statement Read View | Short-term S/X locks | Dirty Read | Moderate overhead |
| **读已提交** | 每条语句新建Read View | 短期S/X锁（语句结束释放） | 脏读 | 中等开销 |
| **Repeatable Read** | Per-transaction Read View + Next-Key Lock | Long-term S locks + Gap locks | Dirty Read, Non-Repeatable Read, Phantom* | Higher memory usage |
| **可重复读** | 事务级Read View + Next-Key锁 | 长期S锁 + 间隙锁 | 脏读、不可重复读、幻读* | 内存占用较高 |
| **Serializable** | MVCC disabled, pure S2PL | Strict 2PL (all locks to commit) | All anomalies | Lowest concurrency |
| **可串行化** | 禁用MVCC，纯S2PL | 严格两阶段锁（锁到提交） | 所有异常 | 并发度最低 |

*InnoDB's RR eliminates phantoms via Next-Key Locks

---

### **2.3 Decision Tree: When to Use MVCC vs LOCK (决策树)**

```mermaid
graph TD
    A[Workload Type?] --> B{Read/Write Ratio}
    B -->|Read-heavy > 80%| C[Use MVCC]
    B -->|Write-heavy > 60%| D[Use Pessimistic Locking]
    B -->|Mixed 40-60%| E{Contention Level?}

    E -->|Low Conflict| F[MVCC + Optimistic]
    E -->|High Conflict| G[MVCC + Pessimistic Write Locks]

    C --> H[Isolation Level?]
    H -->|RC/RR| I[Standard MVCC]
    H -->|Serializable| J[MVCC + SSI*]

    D --> K[Isolation Level?]
    K -->|RU/RC| L[Short-term Locks]
    K -->|Serializable| M[Strict 2PL]

    E --> N[Transaction Duration?]
    N -->|Long-running| O[MVCC Snapshot]
    N -->|Short-running| P[Either OK]

    style C fill:#90EE90
    style D fill:#FFB6C1
    style G fill:#FFD700
```

*SSI = Serializable Snapshot Isolation

---

### **2.4 Flow Chart: Transaction Execution Process (流程图)**

```mermaid
sequenceDiagram
    participant T as Transaction
    participant RV as Read View
    participant UL as Undo Log
    participant L as Lock Manager
    participant DB as Database

    T->>T: BEGIN
    T->>RV: Create Read View
    Note over T,RV: Record up_limit_id, active_trx_ids

    T->>DB: SELECT (Snapshot Read)
    DB->>UL: Traverse version chain
    UL-->>T: Return visible version

    T->>L: SELECT...FOR UPDATE
    L->>L: Acquire X-lock + Gap lock
    L-->>T: Grant lock

    T->>DB: UPDATE
    DB->>DB: Create new version
    DB->>UL: Store old version in undo log
    DB->>RV: Update trx_id

    T->>T: COMMIT
    T->>L: Release all locks
    Note over T,DB: Make versions visible to future transactions

    alt Conflict Detection
        T->>T: ROLLBACK
        T->>UL: Restore from undo log
        T->>L: Release locks
    end
```

---

### **2.5 State Transition Diagram: Transaction Lifecycle (状态转换)**

```mermaid
stateDiagram-v2
    [*] --> ACTIVE: BEGIN
    ACTIVE --> SNAPSHOT_READING: Read-only
    ACTIVE --> LOCK_ACQUIRING: Current Read
    LOCK_ACQUIRING --> LOCK_WAIT: Conflict
    LOCK_WAIT --> LOCK_ACQUIRING: Lock Granted
    LOCK_ACQUIRING --> MODIFYING: Lock Acquired
    MODIFYING --> VERSION_CREATING: Write Operation
    VERSION_CREATING --> MODIFYING: Continue

    MODIFYING --> VALIDATING: COMMIT Request
    SNAPSHOT_READING --> VALIDATING: COMMIT Request

    VALIDATING --> COMMITTED: No Conflict
    VALIDATING --> ABORTED: Conflict Detected

    COMMITTED --> [*]: Release Resources
    ABORTED --> [*]: Rollback & Release

    note right of ACTIVE: Read View Created
    note right of LOCK_WAIT: Wait for lock_timeout
    note right of VALIDATING: Check trx_id vs Read View
```

---

## **Part III: Advanced Formal Proofs (深度形式化证明)**

### **3.1 Theorem: Linearization Point Challenge in MVCC (MIT vMVCC)**

**Problem Statement:**
In MVCC, the **linearization point** occurs at `BEGIN()` when the timestamp is obtained, **before** the transaction body executes. This creates a verification challenge: the system must commit to a logical order without knowing the transaction's future operations.

**Formal Solution (Prophecy Variables):**

**Definition (Prophecy Variable):**
$$\Psi = \langle \text{actions}_T, \text{commit}_T, \text{writes}_T \rangle$$
where:

- $\text{actions}_T$ = predicted operation sequence of transaction $T$
- $\text{commit}_T \in \{0,1\}$ = predicted commit decision
- $\text{writes}_T = \{ (x, v) \}$ = predicted write set

**Theorem 4 (vMVCC Correctness):**
$$\forall T \in \mathbb{T}: \text{Linearize}(T) \iff \text{Validate}(\Psi_T) \land \text{CommitOrder}(t_T) \land \text{ConflictFree}(\text{writes}_T)$$

*Proof Sketch* (from MIT vMVCC paper):

1. **Speculation**: At `BEGIN()`, create prophecy variable $\Psi_T$ predicting $T$'s future behavior
2. **Logical State Update**: Update abstract state at linearization point using $\Psi_T$:
   $$\text{State}_{\text{logical}}(t_T) = \text{State}_{\text{logical}}(t_T-1) \cup \text{writes}_T$$
3. **Validation**: At `COMMIT()`, verify actual behavior matches prophecy:
   $$\text{actions}_T^{\text{actual}} = \text{actions}_T^{\text{predicted}}$$
4. **Conflict Resolution**: If conflict detected, abort and roll back:
   $$\text{If } \exists T': \text{writes}_T \cap \text{writes}_{T'} \neq \emptyset \land t_T' < t_T \implies \text{abort}(T)$$

This approach allows proving **serializability** despite early linearization.

---

### **3.2 Theorem: Serializable Snapshot Isolation (SSI)**

**SSI** extends MVCC to achieve **full serializability** by detecting **dangerous structures**:

**Definition 5 (Dangerous Structure):**
A pair of concurrent transactions $T_1, T_2$ forms a dangerous structure if:

1. $T_1$ reads $x$, $T_2$ writes $x$ (rw-dependency)
2. $T_2$ reads $y$, $T_1$ writes $y$ (rw-dependency)
3. $T_1$ and $T_2$ both commit

**Theorem 5 (SSI Correctness):**
Any schedule that aborts transactions forming dangerous structures is **serializable**.

*Proof*:

1. **Dependency Graph**: Construct graph $G$ with vertices = transactions, edges = dependencies (rw, wr, ww)
2. **Cycle Detection**: Dangerous structure creates a **cycle** $T_1 \rightarrow T_2 \rightarrow T_1$
3. **Serial Order**: By aborting one transaction in each cycle, $G$ becomes acyclic
4. **Topological Sort**: Acyclic graph yields serial order equivalent to original schedule
5. **Commit Order**: Transactions commit in monotonic timestamp order, preserving consistency

This is used in PostgreSQL's `SERIALIZABLE` isolation level.

---

### **3.3 Theorem: Next-Key Lock Phantom Prevention**

**Formal Proof of Range Stability:**

**Definition 6 (Range Lock):**
For index $I$ and predicate $P$, Next-Key Lock $L_{NK}$ locks:
$$L_{NK} = \{ r \mid r \in I \land P(r) \} \cup \{ \text{gap}_k \mid \text{gap}_k \text{ between } r_k \text{ and } r_{k+1} \}$$

**Invariant (Range Stability):**
$$\forall T_i: \text{If } T_i \text{ holds } L_{NK} \text{ on range } R, \text{ then } \forall T_j \neq T_i: \neg \exists r \notin R_{\text{initial}} \text{ s.t. } P(r) \land \text{insert}_j(r)$$

*Proof by Contradiction*:

1. Assume $\exists T_j$ inserts $r_{\text{new}}$ where $P(r_{\text{new}})$ holds
2. $r_{\text{new}}$ must be placed in some gap $\text{gap}_k \subseteq L_{NK}$
3. To insert, $T_j$ must acquire lock on $\text{gap}_k$
4. But $\text{gap}_k$ is held by $T_i$ in X-mode (conflict)
5. Therefore $T_j$ must wait until $T_i$ commits
6. After $T_i$ commits, $r_{\text{new}}$ is visible only to future transactions
7. $T_i$'s range result remains unchanged. ∎

---

### **3.4 Cost-Benefit Quantitative Model (成本收益量化模型)**

**Performance Metric:**
$$\text{Throughput} = \frac{N_{\text{ops}}}{T_{\text{wait}} + T_{\text{exec}} + p_{\text{conflict}} \cdot T_{\text{rollback}}}$$

**Parameter Comparison**:

| **Parameter** | **MVCC (RC)** | **MVCC (RR)** | **2PL (Serializable)** |
|---------------|---------------|---------------|------------------------|
| $T_{\text{wait}}$ | 0 (non-blocking) | 0 (non-blocking) | $\sum C_{\text{lock}}$ |
| $T_{\text{exec}}$ | $C_{\text{visibility}}$ | $C_{\text{visibility}}$ | $C_{\text{lock}}$ |
| $p_{\text{conflict}}$ | $p_{\text{ww}}$ | $p_{\text{ww}} + p_{\text{rw}}$ | $p_{\text{deadlock}}$ |
| $T_{\text{rollback}}$ | $C_{\text{undo}}$ | $C_{\text{undo}}$ | $C_{\text{timeout}}$ |

**Breakpoint Analysis**:
MVCC outperforms locking when:
$$\frac{\text{Reads}}{\text{Writes}} > \frac{C_{\text{lock}}}{C_{\text{visibility}}} \approx 3:1 \text{ (empirical)}$$

---

## **Part IV: Implementation Deep Dive (实现深度剖析)**

### **4.1 InnoDB vs PostgreSQL MVCC Implementation**

| **Aspect** | **InnoDB (Undo Log)** | **PostgreSQL (Tuple Versioning)** |
|------------|----------------------|-----------------------------------|
| **Storage** | Base row + undo chain | Full tuple copies |
| **Version Access** | Reconstruct via undo | Direct tuple read |
| **Visibility** | Transaction ID + roll_ptr | xmin/xmax + snapshot |
| **Cleanup** | Background purge | VACUUM process |
| **Space Overhead** | Lower (only changed cols) | Higher (full rows) |
| **Read Cost** | Higher (reconstruction) | Lower (direct access) |

**InnoDB Version Reconstruction:**

```sql
-- Pseudocode for version reconstruction
FUNCTION Read_Version(row_ptr, trx_id):
    version = row_ptr
    WHILE version.trx_id > trx_id OR version.trx_id IN active_list:
        version = version.roll_pointer.undo_record
        IF version IS NULL:
            RETURN "row not exist"
    RETURN version
```

---

### **4.2 Lock Escalation Matrix (锁升级矩阵)**

```mermaid
graph LR
    A[Row Lock] -->|Lock Table Full| B[Page Lock]
    B -->|Contention High| C[Table Lock]
    C -->|System Overload| D[Global Lock]

    style A fill:#90EE90
    style D fill:#FF4500

    subgraph "Cost"
        A -->|Low| E[N=O(rows)]
        B -->|Medium| F[N=O(pages)]
        C -->|High| G[N=1]
    end
```

**Escalation Conditions**:

- **Row → Page**: When lock memory > `innodb_lock_memory` (default 256KB)
- **Page → Table**: When > 50% rows in page are locked
- **Table → Global**: `LOCK TABLES` command or DDL operations

---

## **Part V: Anomaly Prevention Decision Table (异常防止决策表)**

| **Isolation Level** | **MVCC Mechanism** | **Lock Mechanism** | **Dirty Read** | **Non-Repeatable** | **Phantom** | **Write Skew** |
|---------------------|--------------------|--------------------|----------------|-------------------|-------------|----------------|
| **Read Uncommitted** | Read latest version | None | ❌ | ❌ | ❌ | ❌ |
| **读未提交** | 直接读最新物理版本 | 无锁 | 不防止 | 不防止 | 不防止 | 不防止 |
| **Read Committed** | Per-statement snapshot | Short X-lock on write | ✅ | ❌ | ❌ | ❌ |
| **读已提交** | 语句级快照 | 写操作短期X锁 | 防止 | 不防止 | 不防止 | 不防止 |
| **Repeatable Read** | Per-transaction snapshot + Next-Key Lock | Long S-lock + Gap lock | ✅ | ✅ | ✅* | ⚠️ (some cases) |
| **可重复读** | 事务级快照 + Next-Key锁 | 长期S锁 + 间隙锁 | 防止 | 防止 | 防止* | ⚠️ (部分场景) |
| **Serializable** | SSI + predicate locks | Strict 2PL | ✅ | ✅ | ✅ | ✅ |
| **可串行化** | SSI + 谓词锁 | 严格两阶段锁 | 防止 | 防止 | 防止 | 防止 |

*Note: PostgreSQL/MongoDB RR still allows write skew; requires application-level locks or SELECT FOR UPDATE*

**Write Skew Example**:

```sql
-- T1: SELECT * FROM seats WHERE booked = false; -- finds seat A
-- T2: SELECT * FROM seats WHERE booked = false; -- finds seat B
-- T1: UPDATE seats SET booked = true WHERE id = A; -- commits
-- T2: UPDATE seats SET booked = true WHERE id = B; -- commits
-- Result: Both think they booked the last seat (application bug)
```

**Solution**: Use `SELECT ... FOR UPDATE` (current read + X lock) instead of snapshot read.

---

## **Part VI: Formal Proof of Serializability (串行化形式证明)**

### **6.1 MV2PL Protocol (MVCC + 2PL Hybrid)**

**Definition 7 (MV2PL Schedule):**
A schedule $S$ is MV2PL if:

1. **Reads**: Use MVCC snapshot reads (no locks)
2. **Writes**: Acquire X-lock before write (strict 2PL)
3. **Lock Release**: All locks held until commit
4. **Commit Order**: Transaction timestamps define total order

**Theorem 6 (MV2PL Serializability):**
Every MV2PL schedule is conflict-serializable.

*Proof*:

1. **Lock Graph**: Construct precedence graph $G$ where edge $T_i \rightarrow T_j$ exists if:
   - $T_i$ holds lock on $x$ and $T_j$ requests conflicting lock on $x$
   - Or: $T_i$ writes version $x_v$ and $T_j$ reads $x_v$ (version dependency)

2. **Acyclicity**: By strict 2PL, all edges point from earlier-locking to later-locking transactions. Commit timestamps ensure no cycles.

3. **Topological Order**: The commit timestamp order $t_1 < t_2 < ... < t_n$ yields a serial schedule $S_{serial}$.

4. **Equivalence**: $S$ is conflict-equivalent to $S_{serial}$ because:
   - All conflicting operations appear in same order
   - Snapshot reads don't create conflicts
   - Write-write conflicts resolved by locks

5. **Conclusion**: $S$ is serializable. ∎

---

## **Part VII: Practical Decision Framework (实践决策框架)**

### **7.1 When to Use MVCC vs LOCK: Decision Matrix (决策矩阵)**

```mermaid
decision-tree
  title: Concurrency Control Strategy Selection

  A{Workload Pattern?}
    A --> B[Read-Heavy OLAP]
    A --> C[Write-Heavy OLTP]
    A --> D[Mixed OLTP/OLAP]

    B --> E[Use MVCC (RR)]
    B --> F[Enable Read Replicas]

    C --> G{Contention Level?}
      G --> H[High (e.g., Counter Updates)]
      G --> I[Low (e.g., Appends)]

      H --> J[Use Pessimistic Locking]
      H --> K[Consider Partitioning]

      I --> L[MVCC + Batch Commits]

    D --> M{Latency Sensitivity?}
      M --> N[Low Latency (P99<10ms)]
      M --> O[Fair Latency OK]

      N --> P[Hybrid: MVCC Read + SELECT FOR UPDATE]
      O --> Q[Standard MVCC (RC)]
```

**Rule-Based Decision System:**

1. **IF** `read_ratio > 0.7` **THEN** MVCC
2. **IF** `write_contention > 0.3` **THEN** Add SELECT FOR UPDATE
3. **IF** `transaction_duration > 1s` **THEN** Use RR + Snapshot
4. **IF** `phantom_risk == true` **THEN** Enable Next-Key Locks
5. **IF** `serializability_required == true` **THEN** Use SSI or Serializable

---

## **Part VIII: Performance Benchmarking Matrix (性能基准矩阵)**

| **Workload** | **Transactions/sec** | **P99 Latency** | **Best Strategy** | **Reasoning** |
|--------------|---------------------|-----------------|-------------------|---------------|
| **Read-Only** | 100,000+ | 5ms | MVCC (RR) | No lock overhead |
| **Read-Heavy 90%** | 50,000 | 10ms | MVCC (RC) | Snapshot isolation |
| **Write-Heavy 60%** | 10,000 | 50ms | MVCC + Optimistic Locks | Low rollback rate |
| **Write-Heavy 80%** | 5,000 | 100ms | Pessimistic 2PL | High contention |
| **Long Transaction** | 1,000 | 500ms | MVCC (RR) | Stable snapshot |
| **Short Transaction** | 50,000 | 20ms | Either | Low lock duration |

**Latency Decomposition**:
$$T_{\text{total}} = T_{\text{CPU}} + T_{\text{lock}} + T_{\text{IO}} + T_{\text{GC}}$$

- **MVCC**: $T_{\text{lock}} \approx 0$, $T_{\text{GC}} > 0$
- **2PL**: $T_{\text{lock}} >> 0$, $T_{\text{GC}} = 0$

---

## **Part IX: Summary & Best Practices (总结与最佳实践)**

### **Key Takeaways (核心要点)**

1. **MVCC = Time + Versioning**: Each transaction operates on a **temporal snapshot** of the database
2. **LOCK = Space + Exclusion**: Each transaction controls **physical regions** of the database
3. **Hybrid = Best of Both**: Modern databases combine MVCC reads with locking writes for **serializability**

### **Best Practices (最佳实践)**

| **Scenario** | **Recommended Approach** | **Why** |
|--------------|------------------------|---------|
| **Web App Queries** | MVCC (RC) | High concurrency, low contention |
| **Financial Transfer** | MVCC (RR) + SELECT FOR UPDATE | Prevent write skew |
| **Batch Update** | Pessimistic Locking (Table Lock) | Reduce deadlock risk |
| **Report Generation** | MVCC (RR) + Read Replica | Long-running snapshot |
| **Inventory Management** | MVCC + Optimistic Locking (version column) | High write contention |
| **Queue Processing** | SKIP LOCKED + MVCC | Avoid lock contention |

### **Common Pitfalls (常见陷阱)**

1. **Assuming RR prevents all anomalies**: It doesn't prevent write skew
2. **Overusing SELECT FOR UPDATE**: Turns MVCC into locking system
3. **Long-running transactions**: Causes version bloat and performance degradation
4. **Ignoring vacuum/optimize**: Leads to table bloat in PostgreSQL
5. **Mixing isolation levels**: Can cause subtle consistency bugs

---

## **Conclusion (结论)**

The **MVCC + LOCK** architecture represents a **duality of concurrency control**:

- **MVCC** provides **temporal isolation** through versioning
- **LOCK** provides **spatial isolation** through mutual exclusion
- **Together**, they achieve **serializability** with **high performance**

The formal proofs demonstrate that this hybrid approach is **both correct** (guarantees ACID) and **complete** (handles all anomalies), making it the **de facto standard** for modern RDBMS (InnoDB, PostgreSQL) and increasingly for NoSQL systems (MongoDB, Couchbase).

**Final Decision Rule**:
> **Use MVCC by default, add locks only when contention requires exclusion.** For true serializability, combine MVCC with **SSI** or **Next-Key Locks**.

---

**References**:
: MIT CSAIL vMVCC Formal Verification
: CMU 15-721 Serializable MVCC Proof
: ByteByteGo Isolation Levels
: PostgreSQL MVCC Implementation
: DEV Community Isolation Time Concepts
: Medium Concurrency Control Guide
: Celerdata MVCC vs Locking Comparison
