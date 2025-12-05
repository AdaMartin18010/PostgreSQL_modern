# 03 | ACID理论与实现

> **理论定位**: ACID是关系数据库的基石，本文档提供从理论定义到PostgreSQL实现的完整分析链。

---

## 一、ACID理论基础

### 1.1 历史与动机

**提出背景** (Jim Gray, 1981):

- 问题: 并发访问导致数据不一致
- 解决: 定义事务(Transaction)概念
- 目标: 保证数据库**正确性**和**可靠性**

**形式化定义**:

$$Transaction: \text{Sequence of operations that execute atomically}$$

$$\{R(x), W(y), ...\} \xrightarrow{ACID} \text{Database State Transition}$$

### 1.2 四大特性概览

| 特性 | 英文 | 保证内容 | 失败后果 |
|-----|------|---------|---------|
| **原子性** | Atomicity | 全部成功或全部失败 | 部分执行 → 数据不一致 |
| **一致性** | Consistency | 满足所有完整性约束 | 违反约束 → 无效数据 |
| **隔离性** | Isolation | 并发事务互不干扰 | 读脏数据 → 错误决策 |
| **持久性** | Durability | 提交后永久保存 | 数据丢失 → 业务损失 |

---

## 二、原子性 (Atomicity)

### 2.1 理论定义

**定义2.1 (原子性)**:

$$\forall T: T = \{op_1, op_2, ..., op_n\}$$

$$Execute(T) \in \{\text{Commit}, \text{Abort}\}$$

$$\text{Commit} \implies \forall op_i: Applied(op_i)$$

$$\text{Abort} \implies \forall op_i: \neg Applied(op_i)$$

**关键性质**: **All-or-Nothing**

### 2.2 PostgreSQL实现机制

#### 机制1: WAL (Write-Ahead Logging)

**核心思想**: 先写日志，后修改数据

$$\forall \text{modification } M: WAL(M) \text{ written before } M \text{ applied}$$

**WAL记录结构**:

```c
typedef struct XLogRecord {
    uint32      xl_tot_len;    // 总长度
    TransactionId xl_xid;      // 事务ID
    XLogRecPtr  xl_prev;       // 前一条记录指针
    uint8       xl_info;       // 标志位
    RmgrId      xl_rmid;       // 资源管理器ID
    XLogRecPtr  xl_crc;        // CRC校验

    // 具体数据
    union {
        heap_insert_data;
        heap_update_data;
        heap_delete_data;
        // ...
    } xl_data;
} XLogRecord;
```

**事务日志流程**:

```
┌──────────────────────────────────────┐
│         Transaction T1                │
├──────────────────────────────────────┤
│                                      │
│  BEGIN                               │
│    ↓                                 │
│  INSERT INTO users VALUES (...)      │
│    ↓                                 │
│  [1] 生成WAL记录                      │
│  [2] 写入WAL Buffer                   │
│  [3] 修改Shared Buffer (内存)         │
│    ↓                                 │
│  UPDATE accounts SET balance=...     │
│    ↓                                 │
│  [4] 生成WAL记录                      │
│  [5] 写入WAL Buffer                   │
│  [6] 修改Shared Buffer                │
│    ↓                                 │
│  COMMIT                              │
│    ↓                                 │
│  [7] fsync(WAL) ← 关键：持久化日志     │
│  [8] 标记事务COMMITTED (pg_clog)      │
│  [9] 返回客户端成功                    │
│    ↓                                 │
│  [后台] Checkpoint刷盘                │
│                                      │
└──────────────────────────────────────┘
```

**原子性保证**:

- **COMMIT前**: 所有修改记录在WAL
- **崩溃后**: 重放WAL恢复到一致状态
- **ABORT**: 忽略WAL中的记录

**定理2.1 (WAL保证原子性)**:

$$\forall T: \text{Crash} \implies \text{Recovery}(WAL) = \begin{cases}
\text{Redo all committed } T \\
\text{Undo all aborted } T
\end{cases}$$

**证明**: 见 `03-证明与形式化/01-公理系统证明.md#定理2.1`

#### 机制2: 事务状态管理

**pg_clog (Commit Log)**:

```c
// 2-bit per transaction
typedef enum {
    TRANSACTION_STATUS_IN_PROGRESS  = 0x00,
    TRANSACTION_STATUS_COMMITTED    = 0x01,
    TRANSACTION_STATUS_ABORTED      = 0x02,
    TRANSACTION_STATUS_SUB_COMMITTED= 0x03
} TransactionStatus;
```

**状态转换图**:

```
        BEGIN
          ↓
    IN_PROGRESS ──COMMIT──→ COMMITTED
          │                     ↑
          │                     │
        ABORT               (永久状态)
          ↓
       ABORTED ──────────────────→ (永久状态)
```

**原子性保证**:

```python
def commit_transaction(txid):
    # 1. 确保WAL已刷盘
    ensure_wal_flushed(txid)

    # 2. 原子更新状态
    with atomic_operation():
        set_transaction_status(txid, COMMITTED)

    # 3. 返回成功
    return SUCCESS

def abort_transaction(txid):
    # 直接标记为ABORTED（WAL记录被忽略）
    set_transaction_status(txid, ABORTED)
```

---

## 三、一致性 (Consistency)

### 3.1 理论定义

**定义3.1 (一致性)**:

$$\forall T, \forall \text{Constraint } C: $$

$$\text{State}_{\text{before}} \models C \land Execute(T) \implies \text{State}_{\text{after}} \models C$$

**约束类型**:

1. **域约束** (Domain Constraints): $x \in \text{Domain}$
2. **实体完整性** (Entity Integrity): $\text{PRIMARY KEY} \neq \text{NULL}$
3. **参照完整性** (Referential Integrity): $\text{FOREIGN KEY} \subseteq \text{PRIMARY KEY}$
4. **用户定义约束** (CHECK Constraints): $\text{Predicate}(x) = \text{TRUE}$

### 3.2 PostgreSQL约束实现

#### 约束1: 主键约束

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- 内部实现
-- 1. 创建唯一索引
CREATE UNIQUE INDEX users_pkey ON users (id);

-- 2. 添加NOT NULL约束
ALTER TABLE users ALTER COLUMN id SET NOT NULL;
```

**检查时机**: INSERT/UPDATE时

**检查算法**:

```python
def check_primary_key(table, new_row):
    pk_columns = get_primary_key_columns(table)
    pk_value = extract_values(new_row, pk_columns)

    # 1. 检查NULL
    if any(v is None for v in pk_value):
        raise IntegrityError("NULL value in primary key")

    # 2. 检查唯一性（通过索引）
    if index_exists(table.pk_index, pk_value):
        raise IntegrityError("duplicate key value")
```

#### 约束2: 外键约束

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);
```

**检查策略**:

| 动作 | 时机 | 检查内容 |
|-----|------|---------|
| **INSERT orders** | 立即 | user_id是否存在于users |
| **UPDATE orders.user_id** | 立即 | 新user_id是否存在 |
| **DELETE users** | 立即/延迟 | 是否有关联orders |
| **UPDATE users.id** | 立即/延迟 | 是否有关联orders |

**实现**:

```python
def check_foreign_key(child_table, parent_table, fk_column, fk_value):
    # 1. 检查父表是否存在该值
    if fk_value is not None:
        parent_exists = execute_query(
            f"SELECT 1 FROM {parent_table} WHERE id = {fk_value}"
        )
        if not parent_exists:
            raise IntegrityError(f"Foreign key violation: {fk_value} not found")

def handle_delete(parent_table, parent_id, on_delete_action):
    if on_delete_action == 'CASCADE':
        # 级联删除
        execute_query(f"DELETE FROM {child_table} WHERE user_id = {parent_id}")
    elif on_delete_action == 'SET NULL':
        # 设置为NULL
        execute_query(f"UPDATE {child_table} SET user_id = NULL WHERE user_id = {parent_id}")
    elif on_delete_action == 'RESTRICT':
        # 拒绝删除
        child_exists = execute_query(f"SELECT 1 FROM {child_table} WHERE user_id = {parent_id}")
        if child_exists:
            raise IntegrityError("Foreign key constraint violation")
```

#### 约束3: CHECK约束

```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    balance DECIMAL CHECK (balance >= 0)
);
```

**检查时机**: 每次INSERT/UPDATE

**实现**:

```python
def check_constraints(table, new_row):
    for constraint in table.check_constraints:
        predicate = constraint.predicate

        # 评估谓词
        if not evaluate_predicate(predicate, new_row):
            raise IntegrityError(f"CHECK constraint {constraint.name} violated")

# 示例: balance >= 0
def evaluate_predicate(predicate, row):
    if predicate == "balance >= 0":
        return row['balance'] >= 0
```

### 3.3 触发器 (Triggers)

**用途**: 实现复杂业务规则

```sql
CREATE TRIGGER check_balance_trigger
BEFORE UPDATE ON accounts
FOR EACH ROW
EXECUTE FUNCTION check_balance();

CREATE FUNCTION check_balance() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.balance < 0 THEN
        RAISE EXCEPTION 'Balance cannot be negative';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**触发器类型**:

| 时机 | 粒度 | 用途 |
|-----|------|------|
| BEFORE | ROW | 验证/修改数据 |
| AFTER | ROW | 审计/级联 |
| INSTEAD OF | ROW | 视图更新 |
| BEFORE | STATEMENT | 表级验证 |
| AFTER | STATEMENT | 汇总统计 |

---

## 四、隔离性 (Isolation)

### 4.1 理论定义

**定义4.1 (隔离性)**:

$$\forall T_i, T_j: Concurrent(T_i, T_j) \implies$$

$$\exists \text{SerialSchedule } S: Effect(T_i \parallel T_j) = Effect(S)$$

**隔离级别层次**:

```
Serializable (最强)
    ↓
Repeatable Read
    ↓
Read Committed
    ↓
Read Uncommitted (PostgreSQL不支持)
```

### 4.2 异常现象定义

**定义4.2 (脏读)**:

$$T_i \text{ reads data written by uncommitted } T_j$$

**定义4.3 (不可重复读)**:

$$T_i \text{ reads } x \text{ twice, gets different values}$$

**定义4.4 (幻读)**:

$$T_i \text{ range query twice, gets different row sets}$$

**定义4.5 (串行化异常)**:

$$\exists \text{ cycle in serialization graph}$$

### 4.3 隔离级别矩阵

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 串行化异常 |
|---------|-----|-----------|------|-----------|
| **Read Uncommitted** | ✗ | ✗ | ✗ | ✗ |
| **Read Committed** | ✓ | ✗ | ✗ | ✗ |
| **Repeatable Read** | ✓ | ✓ | ✓ (PG扩展) | ✗ |
| **Serializable** | ✓ | ✓ | ✓ | ✓ |

### 4.4 PostgreSQL实现

**Read Committed**:

```python
class ReadCommittedTransaction:
    def execute_statement(self, sql):
        # 每条语句获取新快照
        snapshot = get_current_snapshot()
        result = execute_with_mvcc(sql, snapshot)
        return result
```

**Repeatable Read**:

```python
class RepeatableReadTransaction:
    def __init__(self):
        # 事务开始时固定快照
        self.snapshot = get_current_snapshot()

    def execute_statement(self, sql):
        result = execute_with_mvcc(sql, self.snapshot)
        return result

    def check_write_conflict(self, tuple):
        # 检测写写冲突
        if tuple.xmax != 0 and tuple.xmax != self.txid:
            if is_committed(tuple.xmax):
                raise SerializationError("concurrent update")
```

**Serializable (SSI)**:

```python
class SerializableTransaction:
    def __init__(self):
        self.snapshot = get_current_snapshot()
        self.predicate_locks = []  # SIREAD锁

    def execute_select(self, sql):
        result = execute_with_mvcc(sql, self.snapshot)

        # 记录读取范围
        predicate = extract_predicate(sql)
        self.predicate_locks.append(predicate)

        return result

    def execute_modify(self, sql):
        # 检查是否违反其他事务的谓词锁
        for other_tx in get_concurrent_transactions():
            for pred_lock in other_tx.predicate_locks:
                if conflicts_with(sql, pred_lock):
                    # 记录依赖
                    add_dependency(other_tx, self)

                    # 检测环
                    if has_cycle():
                        raise SerializationError("cycle detected")
```

详细分析见: `01-核心理论模型/02-MVCC理论完整解析.md#四隔离级别实现`

---

## 五、持久性 (Durability)

### 5.1 理论定义

**定义5.1 (持久性)**:

$$\forall T: Commit(T) \implies \forall \text{Crash}: State_{\text{after\_recovery}} \models T$$

**关键性质**: **Survive System Failures**

### 5.2 PostgreSQL实现机制

#### 机制1: WAL持久化

**synchronous_commit参数**:

| 值 | 含义 | 性能 | 可靠性 |
|---|------|------|--------|
| **off** | 异步提交，不等待WAL刷盘 | 最高 | 最低（可能丢失最后几个事务） |
| **local** | 等待本地WAL刷盘 | 中 | 中（单机故障不丢失） |
| **remote_write** | 等待备库接收WAL | 中低 | 高（备库内存有副本） |
| **on/remote_apply** | 等待备库应用WAL | 最低 | 最高（备库已应用） |

**fsync策略**:

```c
// PostgreSQL WAL刷盘
void XLogFlush(XLogRecPtr record) {
    // 1. 等待WAL写入内核缓冲区
    XLogWrite(record);

    // 2. 强制刷盘
    if (sync_method == SYNC_METHOD_FSYNC) {
        fsync(wal_fd);  // ← 关键系统调用
    } else if (sync_method == SYNC_METHOD_FDATASYNC) {
        fdatasync(wal_fd);  // 不同步元数据
    } else if (sync_method == SYNC_METHOD_OPEN_DSYNC) {
        // 使用O_DSYNC标志打开文件
    }
}
```

#### 机制2: Checkpoint

**目的**: 将内存脏页刷盘，缩短恢复时间

**流程**:

```
┌──────────────────────────────────────┐
│         Checkpoint Process            │
├──────────────────────────────────────┤
│                                      │
│  [1] 记录Checkpoint起始LSN            │
│      checkpoint_start_lsn            │
│         ↓                            │
│  [2] 扫描Shared Buffer                │
│      找到所有脏页                     │
│         ↓                            │
│  [3] 按顺序刷盘                       │
│      for page in dirty_pages:        │
│          fsync(page)                 │
│         ↓                            │
│  [4] 记录Checkpoint完成LSN            │
│      checkpoint_end_lsn              │
│         ↓                            │
│  [5] 更新控制文件                     │
│      pg_control.checkPointCopy       │
│                                      │
└──────────────────────────────────────┘
```

**触发条件**:

| 条件 | 参数 | 默认值 |
|-----|------|--------|
| **WAL大小** | `max_wal_size` | 1GB |
| **时间间隔** | `checkpoint_timeout` | 5分钟 |
| **手动触发** | `CHECKPOINT` 命令 | - |

**恢复加速**:

$$\text{Recovery Time} \propto \text{WAL Size Since Last Checkpoint}$$

```python
def recover_from_crash():
    # 1. 读取最后一个Checkpoint位置
    checkpoint_lsn = read_control_file().checkpoint_lsn

    # 2. 从Checkpoint位置开始重放WAL
    current_lsn = checkpoint_lsn
    while current_lsn < latest_wal_lsn:
        record = read_wal_record(current_lsn)

        if record.xid.status == COMMITTED:
            redo_operation(record)  # 重做已提交事务
        # 未提交事务的记录被忽略（相当于回滚）

        current_lsn = record.next_lsn
```

#### 机制3: 故障恢复算法

**ARIES算法** (Algorithms for Recovery and Isolation Exploiting Semantics):

**阶段1: 分析 (Analysis)**

```python
def analysis_phase():
    """确定哪些事务需要REDO/UNDO"""
    redo_list = []
    undo_list = []

    for record in wal_from_checkpoint:
        if record.type == BEGIN:
            active_transactions.add(record.xid)
        elif record.type == COMMIT:
            active_transactions.remove(record.xid)
        elif record.type == ABORT:
            active_transactions.remove(record.xid)
        else:
            # 修改操作
            redo_list.append(record)

    # 崩溃时仍活跃的事务需要UNDO
    undo_list = list(active_transactions)

    return redo_list, undo_list
```

**阶段2: 重做 (Redo)**

```python
def redo_phase(redo_list):
    """重做所有已提交事务的修改"""
    for record in redo_list:
        if is_committed(record.xid):
            apply_modification(record)
```

**阶段3: 回滚 (Undo)**

```python
def undo_phase(undo_list):
    """回滚所有未提交事务"""
    for xid in undo_list:
        # 反向扫描该事务的WAL记录
        for record in reverse_wal_scan(xid):
            undo_modification(record)

        # 标记为ABORTED
        set_transaction_status(xid, ABORTED)
```

---

## 六、ACID之间的关系

### 6.1 依赖关系图

```
        Atomicity (WAL + pg_clog)
              ↓
         Consistency (Constraints)
              ↓
         Isolation (MVCC + Locks)
              ↓
         Durability (WAL fsync + Checkpoint)
```

**关键洞察**:

1. **Atomicity是基础**: 没有原子性，其他特性无从谈起
2. **Consistency是目标**: ACID的最终目的是保证数据一致性
3. **Isolation是手段**: 通过隔离并发事务保证一致性
4. **Durability是保障**: 确保已提交事务不丢失

### 6.2 权衡分析

**性能 vs 一致性**:

| 配置 | 性能 | 一致性 | 适用场景 |
|-----|------|--------|---------|
| `synchronous_commit=off` | 高 | 弱 | 日志、分析 |
| `synchronous_commit=local` | 中 | 强 | 常规OLTP |
| `synchronous_commit=on` | 低 | 最强 | 金融、核心 |

**隔离级别 vs 并发**:

$$Concurrency \propto \frac{1}{IsolationLevel}$$

- Read Committed: 高并发，允许异常
- Serializable: 低并发，无异常

---

## 七、形式化证明

### 7.1 定理: ACID保证正确性

**定理7.1**:

$$\forall T: ACID(T) \implies Correctness(T)$$

**证明**:

**引理1**: Atomicity保证状态转换完整性

$$Atomicity \implies State \in \{S_{\text{before}}, S_{\text{after}}\}$$

**引理2**: Consistency保证约束不变性

$$Consistency \implies \forall C: State \models C$$

**引理3**: Isolation保证串行化等价

$$Isolation \implies \exists SerialSchedule: Equivalent$$

**引理4**: Durability保证持久化

$$Durability \implies \forall Crash: State_{\text{recovered}} = State_{\text{committed}}$$

**结合引理1-4**:

$$ACID \implies \text{Correct State Transitions} \land \text{Constraint Satisfaction} \land$$
$$\text{Serializable Execution} \land \text{Persistent Storage}$$

$$\implies Correctness \quad \square$$

详细证明见: `03-证明与形式化/01-公理系统证明.md#定理7.1`

---

## 八、实践指南

### 8.1 选择合适的隔离级别

**决策树**:

```
需要串行化吗？
├─ 是 → Serializable
└─ 否 → 需要可重复读吗？
    ├─ 是 → Repeatable Read
    └─ 否 → Read Committed（默认）
```

**场景映射**:

| 业务场景 | 推荐级别 | 理由 |
|---------|---------|------|
| **金融转账** | Serializable | 防止丢失更新 |
| **库存扣减** | Serializable | 防止超卖 |
| **报表查询** | Repeatable Read | 一致性快照 |
| **Web应用** | Read Committed | 高并发 |
| **数据分析** | Read Committed | 读最新数据 |

### 8.2 优化WAL性能

**参数调优**:

```sql
-- 提升性能（降低可靠性）
SET synchronous_commit = off;  -- 异步提交
SET wal_writer_delay = 1000ms; -- 延迟刷盘

-- 提升可靠性（降低性能）
SET synchronous_commit = remote_apply;  -- 等待备库
SET full_page_writes = on;               -- 完整页写入
```

**WAL压缩**:

```sql
-- 启用WAL压缩
SET wal_compression = on;  -- 减少WAL大小

-- 权衡
-- 优势: 减少磁盘I/O，减少网络带宽（复制）
-- 劣势: 增加CPU开销
```

### 8.3 Checkpoint调优

```sql
-- 增加Checkpoint间隔
SET checkpoint_timeout = 30min;  -- 默认5min

-- 增加WAL上限
SET max_wal_size = 10GB;         -- 默认1GB

-- 平滑Checkpoint
SET checkpoint_completion_target = 0.9;  -- 90%时间内完成
```

---

## 九、总结

### 9.1 核心贡献

**理论贡献**:
1. **ACID形式化定义**（第一章）
2. **正确性证明**（定理7.1）
3. **隔离级别数学模型**（定义4.1-4.5）

**工程价值**:
1. **WAL机制**：保证原子性和持久性
2. **MVCC + 锁**：实现隔离性
3. **约束系统**：保证一致性

### 9.2 关键公式

**ACID正确性**:

$$ACID = Atomicity \land Consistency \land Isolation \land Durability$$

$$\implies Correctness$$

**恢复时间**:

$$T_{\text{recovery}} = \frac{\text{WAL\_Size\_Since\_Checkpoint}}{\text{Redo\_Speed}}$$

### 9.3 设计原则

1. **WAL优先**: 先写日志后修改数据
2. **延迟刷盘**: 批量fsync提升性能
3. **定期Checkpoint**: 缩短恢复时间
4. **约束检查**: 事务内强制执行

---

## 十、延伸阅读

**理论基础**:
- Gray, J., & Reuter, A. (1992). *Transaction Processing* → ACID理论奠基
- Mohan, C., et al. (1992). "ARIES: A Transaction Recovery Method" → 恢复算法

**实现细节**:
- PostgreSQL WAL源码: `src/backend/access/transam/xlog.c`
- 约束检查: `src/backend/executor/execMain.c`
- Checkpoint: `src/backend/postmaster/checkpointer.c`

**扩展方向**:
- `01-核心理论模型/04-CAP理论与权衡.md` → 分布式环境下的ACID
- `03-证明与形式化/01-公理系统证明.md` → 完整数学证明
- `06-性能分析/02-延迟分析模型.md` → WAL性能量化

---

**版本**: 1.0.0
**最后更新**: 2025-12-05
**关联文档**:
- `01-核心理论模型/01-分层状态演化模型(LSEM).md`
- `01-核心理论模型/02-MVCC理论完整解析.md`
- `02-设计权衡分析/02-隔离级别权衡矩阵.md`
