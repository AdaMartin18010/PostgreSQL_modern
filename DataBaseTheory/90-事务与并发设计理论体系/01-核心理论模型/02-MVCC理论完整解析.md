# 02 | MVCC理论完整解析

> **理论定位**: 多版本并发控制（MVCC）是PostgreSQL并发控制的核心机制，本文档提供完整的数学证明和工程实现分析。

---

## 一、理论基础与动机

### 1.1 并发控制问题的本质

**核心矛盾**:

- **正确性**: 事务隔离，防止数据竞争
- **性能**: 高并发吞吐，降低锁开销

**传统2PL（两阶段锁）的困境**:

$$ReadLock(T) \land WriteLock(T) \implies Conflict \implies Wait$$

- ✅ **优势**: 实现简单，强隔离保证
- ❌ **劣势**: 读写互斥，吞吐量低

**MVCC的创新**:

$$Read(T_i) \parallel Write(T_j) \text{ if } Version(T_i) \neq Version(T_j)$$

- 读操作访问历史版本，**无需加锁**
- 写操作创建新版本，**仅写写冲突**

### 1.2 形式化定义

**定义1.1 (版本空间)**:

$$\mathcal{V} = \{v_1, v_2, ..., v_n\} \quad \text{where } v_i = (data, xmin, xmax, ctid)$$

**定义1.2 (版本链)**:

$$VersionChain(row) = \{v_i \in \mathcal{V} : v_i.key = row.key\}$$

排序关系: $v_i \prec v_j \iff v_i.xmin < v_j.xmin$

**定义1.3 (快照)**:

$$Snapshot = (xmin, xmax, xip)$$

其中:

- $xmin$: 最小活跃事务ID
- $xmax$: 最大已提交事务ID + 1
- $xip$: 活跃事务ID集合

---

## 二、可见性判断算法

### 2.1 完整可见性规则

**算法2.1: 元组可见性判断**:

```python
def tuple_visible(tuple: Tuple, snapshot: Snapshot, txid: TransactionId) -> bool:
    """
    完整的可见性判断算法

    时间复杂度: O(log |xip|)（二分查找活跃列表）
    """
    # 规则1: 本事务创建的版本永远可见
    if tuple.xmin == txid:
        if tuple.xmax == 0:
            return True  # 未删除
        if tuple.xmax == txid:
            return False  # 本事务已删除
        if not is_committed(tuple.xmax):
            return True  # 删除事务未提交
        return False  # 删除事务已提交

    # 规则2: 创建事务未提交 → 不可见
    if not is_committed(tuple.xmin):
        return False

    # 规则3: 创建事务在快照后启动 → 不可见
    if tuple.xmin >= snapshot.xmax:
        return False

    # 规则4: 创建事务在活跃列表 → 不可见
    if tuple.xmin in snapshot.xip:  # O(log n) 二分查找
        return False

    # 规则5: 检查删除标记xmax
    if tuple.xmax == 0:
        return True  # 未删除

    if tuple.xmax == txid:
        return False  # 本事务删除

    if not is_committed(tuple.xmax):
        return True  # 删除事务未提交

    if tuple.xmax >= snapshot.xmax:
        return True  # 删除在快照后

    if tuple.xmax in snapshot.xip:
        return True  # 删除事务在活跃列表

    # 所有条件都不满足 → 已删除
    return False
```

### 2.2 可见性证明

**定理2.1 (可见性单调性)**:

$$\forall snap_1, snap_2: snap_1 \prec snap_2 \implies Visible(v, snap_1) \subseteq Visible(v, snap_2)$$

**证明**:

设 $snap_1 = (xmin_1, xmax_1, xip_1)$, $snap_2 = (xmin_2, xmax_2, xip_2)$

且 $snap_1 \prec snap_2$，即 $xmax_1 \leq xmax_2$ 且 $xip_1 \supseteq xip_2$

假设 $v$ 对 $snap_1$ 可见，即:

1. $v.xmin < xmax_1$ 且 $v.xmin \notin xip_1$
2. $v.xmax = 0$ 或 $v.xmax \geq xmax_1$ 或 $v.xmax \in xip_1$

需证明 $v$ 对 $snap_2$ 可见:

**情况1**: 如果 $v.xmin < xmax_1$，则 $v.xmin < xmax_2$（因为 $xmax_1 \leq xmax_2$）

**情况2**: 如果 $v.xmin \notin xip_1$，则 $v.xmin \notin xip_2$（因为 $xip_1 \supseteq xip_2$）

**情况3**: 如果 $v.xmax \geq xmax_1$，则 $v.xmax \geq xmax_2$ 或 $v.xmax \in [xmax_1, xmax_2)$，后者意味着 $v$ 在 $snap_2$ 前未删除

因此 $v$ 对 $snap_2$ 可见。 ∎

**推论2.1**: 快照越新，可见的版本越多（单调递增）

### 2.3 时空复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 | 说明 |
|-----|-----------|-----------|------|
| **可见性检查** | $O(\log\|xip\|)$ | $O(1)$ | 二分查找活跃列表 |
| **快照创建** | $O(N)$ | $O(N)$ | N为活跃事务数 |
| **版本链遍历** | $O(k)$ | $O(1)$ | k为链长度 |
| **索引扫描** | $O(m \log n + mk)$ | $O(1)$ | m个索引项，k为平均链长 |

**最坏情况分析**:

高并发更新同一行 → 版本链长度 $k \to \infty$

$$T_{scan} = O(n \cdot k) \quad \text{where } k = \text{avg chain length}$$

**优化策略**: HOT（Heap-Only Tuple）机制，避免索引膨胀

---

## 三、操作语义与版本链演化

### 3.1 INSERT操作

**语义**:

$$INSERT(data) \implies \text{Create } v_{new} \text{ where } v_{new}.xmin = \text{CurrentTxID}$$

**物理过程**:

```sql
-- 事务T1 (TxID=100)
INSERT INTO users (id, name) VALUES (1, 'Alice');

-- 元组状态
Tuple {
    xmin: 100,
    xmax: 0,        -- 未删除
    data: 'Alice',
    ctid: (0, 1)    -- 页号0, 偏移1
}
```

**可见性**:

- 对T1: 立即可见（规则1）
- 对其他事务: T1提交后可见（规则2）

### 3.2 DELETE操作

**语义**:

$$DELETE(row) \implies v_{old}.xmax \leftarrow \text{CurrentTxID}$$

**物理过程**:

```sql
-- 事务T2 (TxID=105)
DELETE FROM users WHERE id = 1;

-- 元组状态更新
Tuple {
    xmin: 100,
    xmax: 105,      -- 标记删除
    data: 'Alice',
    ctid: (0, 1)
}
```

**延迟清理**: 物理删除由VACUUM完成

### 3.3 UPDATE操作

**语义**:

$$UPDATE(row, new\_data) \equiv DELETE(row) + INSERT(new\_data)$$

**物理过程**:

```sql
-- 事务T3 (TxID=110)
UPDATE users SET name = 'Bob' WHERE id = 1;

-- 旧版本标记删除
Tuple_old {
    xmin: 100,
    xmax: 110,      -- 标记删除
    data: 'Alice',
    ctid: (0, 1)
}

-- 新版本插入
Tuple_new {
    xmin: 110,
    xmax: 0,
    data: 'Bob',
    ctid: (0, 2)    -- 新位置
}
```

**HOT优化条件**:

1. 未更新索引列
2. 新版本在同一页内
3. 页面有足够空间

**HOT链**:

```text
Index → Tuple_old ─[HOT]→ Tuple_new
          ↑ (ctid指针)
```

---

## 四、隔离级别实现

### 4.1 Read Committed

**快照策略**: **语句级快照**

```python
class ReadCommittedTransaction:
    def execute_statement(self, sql):
        snapshot = get_current_snapshot()  # 每条语句获取新快照
        result = execute_with_snapshot(sql, snapshot)
        return result
```

**允许的异常**:

- ✅ **不可重复读**: 同一查询返回不同结果
- ✅ **幻读**: 范围查询出现新行

**示例**:

```sql
-- 会话A
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- 返回 100

-- 会话B
UPDATE accounts SET balance = 200 WHERE id = 1;
COMMIT;

-- 会话A (同一事务内)
SELECT balance FROM accounts WHERE id = 1;  -- 返回 200 (不可重复读)
```

### 4.2 Repeatable Read

**快照策略**: **事务级快照**

```python
class RepeatableReadTransaction:
    def __init__(self):
        self.snapshot = get_current_snapshot()  # 事务开始时固定

    def execute_statement(self, sql):
        result = execute_with_snapshot(sql, self.snapshot)
        return result
```

**防止的异常**:

- ✅ **不可重复读**: 固定快照保证一致性
- ✅ **幻读**: PostgreSQL扩展，事务级快照防止幻读

**写写冲突检测**:

```sql
-- 事务T1
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM accounts WHERE id = 1;  -- 快照: balance=100

-- 事务T2 修改并提交
UPDATE accounts SET balance = 200 WHERE id = 1;
COMMIT;

-- 事务T1 尝试更新
UPDATE accounts SET balance = 150 WHERE id = 1;
-- ERROR: could not serialize access due to concurrent update
```

**冲突检测算法**:

```python
def detect_rr_conflict(tuple, snapshot, txid):
    if tuple.xmax != 0 and tuple.xmax != txid:
        if is_committed(tuple.xmax):
            # 行已被其他已提交事务修改
            raise SerializationError("concurrent update")
```

### 4.3 Serializable (SSI)

**SSI (Serializable Snapshot Isolation)**: 基于依赖图的冲突检测

**核心思想**: 检测**读写依赖环**

**定义4.1 (读写依赖)**:

$$T_i \xrightarrow{rw} T_j \iff T_i \text{ 读取的数据被 } T_j \text{ 修改}$$

**定义4.2 (写读依赖)**:

$$T_i \xrightarrow{wr} T_j \iff T_i \text{ 修改的数据被 } T_j \text{ 读取}$$

**定理4.1 (SSI正确性)**:

$$\text{Serializable} \iff \neg\exists \text{ cycle in dependency graph}$$

**证明**: 见 `03-证明与形式化/03-串行化证明.md#定理4.1`

**实现机制**:

1. **谓词锁** (Predicate Lock): 记录读取的范围

```python
class PredicateLock:
    def __init__(self, table, predicate):
        self.table = table
        self.predicate = predicate  # 例如: "id BETWEEN 1 AND 10"

    def conflicts_with(self, write_op):
        # 检查写操作是否在读取范围内
        return write_op.matches(self.predicate)
```

2. **SIREAD锁**: 轻量级共享锁，标记读取

```sql
-- 事务T1
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT * FROM orders WHERE amount > 100;
-- 内部: 创建SIREAD锁 (amount > 100)

-- 事务T2
INSERT INTO orders VALUES (200);
-- 检测到冲突: 新行满足T1的谓词
-- 记录依赖: T1 → T2

-- 若检测到环 → 中止T1或T2
```

3. **依赖图维护**:

```python
class DependencyGraph:
    def __init__(self):
        self.edges = {}  # {T_i: [T_j, T_k, ...]}

    def add_edge(self, from_tx, to_tx, edge_type):
        self.edges.setdefault(from_tx, []).append((to_tx, edge_type))

        # 检测环
        if self.has_cycle():
            # 选择牺牲事务（通常是最新事务）
            self.abort_transaction(to_tx)

    def has_cycle(self):
        # DFS检测环
        visited = set()
        stack = set()

        def dfs(node):
            if node in stack:
                return True  # 发现环
            if node in visited:
                return False

            visited.add(node)
            stack.add(node)

            for neighbor, _ in self.edges.get(node, []):
                if dfs(neighbor):
                    return True

            stack.remove(node)
            return False

        for node in self.edges:
            if dfs(node):
                return True
        return False
```

---

## 五、VACUUM机制

### 5.1 死元组识别

**定义5.1 (死元组)**:

$$DeadTuple(v) \iff v.xmax \neq 0 \land v.xmax < \text{OldestXmin}$$

其中 $\text{OldestXmin}$ = 所有活跃事务中最小的事务ID

**算法5.1: 计算OldestXmin**

```python
def compute_oldest_xmin():
    active_txs = get_active_transactions()  # 获取所有活跃事务
    if not active_txs:
        return get_latest_completed_xid()

    return min(tx.xmin for tx in active_txs)
```

### 5.2 清理过程

**阶段1: 扫描表**

```python
def vacuum_table(table):
    oldest_xmin = compute_oldest_xmin()
    dead_tuples = []

    for page in table.pages:
        for tuple in page.tuples:
            if is_dead(tuple, oldest_xmin):
                dead_tuples.append(tuple)
                mark_as_unused(tuple)  # 标记为可用空间

    update_fsm(table, dead_tuples)  # 更新空闲空间映射
    return dead_tuples
```

**阶段2: 清理索引**

```python
def vacuum_indexes(table, dead_tuples):
    dead_ctids = {tuple.ctid for tuple in dead_tuples}

    for index in table.indexes:
        for entry in index.entries:
            if entry.ctid in dead_ctids:
                delete_index_entry(index, entry)
```

**阶段3: 截断表文件**（可选）

```python
def truncate_table(table):
    # 如果表尾部有连续的空页面，物理截断文件
    empty_pages = count_trailing_empty_pages(table)
    if empty_pages > threshold:
        truncate_file(table, empty_pages)
```

### 5.3 Freeze操作

**问题**: 32位事务ID回卷

$$\text{XID} \in [0, 2^{32}-1] \implies \text{wrap-around after } 4B \text{ transactions}$$

**解决**: Freeze旧元组

```sql
-- 当元组年龄超过阈值
IF (current_xid - tuple.xmin) > autovacuum_freeze_max_age THEN
    tuple.xmin := FrozenTransactionId  -- 特殊值: 2
    -- 该元组变为"永久可见"
```

**Freeze策略**:

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `vacuum_freeze_min_age` | 50M | 触发freeze的最小年龄 |
| `vacuum_freeze_table_age` | 150M | 强制freeze整表的年龄 |
| `autovacuum_freeze_max_age` | 200M | 防止回卷的最大年龄 |

---

## 六、优化技术

### 6.1 HOT (Heap-Only Tuple)

**条件**:

1. UPDATE不涉及索引列
2. 新版本在同一页内
3. 页面有足够空闲空间

**效果**:

$$\text{Index writes} = 0 \quad (\text{vs traditional: } O(n) \text{ for } n \text{ indexes})$$

**实现**:

```c
// PostgreSQL源码简化
if (HeapTupleIsHotUpdated(oldtup) &&
    !IndexedColumnsChanged(oldtup, newtup) &&
    PageGetFreeSpace(page) >= newtup_size) {

    // 在同页内插入新版本
    newoffset = PageAddItem(page, newtup);

    // 建立HOT链
    oldtup->t_ctid = (page_num, newoffset);

    // 不插入新索引项
}
```

**版本链**:

```text
Index → [Page Header]
          ↓
       [ItemId 1] → Tuple_v1 (xmin=100, xmax=110)
          ↓           ↓ (ctid指向)
       [ItemId 2] → Tuple_v2 (xmin=110, xmax=0)  ← HOT链
```

### 6.2 Index-Only Scan

**前提**: 查询列完全在索引中（覆盖索引）

**问题**: 仍需检查可见性 → 需要访问堆表

**解决**: **Visibility Map**

```python
class VisibilityMap:
    """
    位图: 每个堆页一个bit
    1 = 页面所有元组对所有事务可见
    0 = 需要检查可见性
    """
    def __init__(self, num_pages):
        self.bits = [0] * num_pages

    def set_all_visible(self, page_num):
        self.bits[page_num] = 1

    def is_all_visible(self, page_num):
        return self.bits[page_num] == 1
```

**Index-Only Scan流程**:

```python
def index_only_scan(index, query):
    results = []

    for entry in index.search(query):
        page_num = entry.ctid[0]

        if visibility_map.is_all_visible(page_num):
            # 跳过堆访问
            results.append(entry.data)
        else:
            # 需要检查可见性
            tuple = fetch_tuple(entry.ctid)
            if tuple_visible(tuple, current_snapshot, current_txid):
                results.append(tuple.data)

    return results
```

### 6.3 Parallel VACUUM

**策略**: 多工作进程并行清理

```python
def parallel_vacuum(table, num_workers=4):
    pages = table.pages
    chunk_size = len(pages) // num_workers

    futures = []
    for i in range(num_workers):
        start = i * chunk_size
        end = start + chunk_size if i < num_workers - 1 else len(pages)

        future = executor.submit(vacuum_pages, table, pages[start:end])
        futures.append(future)

    dead_tuples = []
    for future in futures:
        dead_tuples.extend(future.result())

    # 索引清理仍需串行（持有锁）
    vacuum_indexes(table, dead_tuples)
```

---

## 七、性能分析

### 7.1 吞吐量模型

**读密集负载**:

$$TPS_{read} = \frac{C}{T_{snapshot} + T_{scan} + T_{visibility}}$$

其中:

- $C$: 并发度
- $T_{snapshot}$: 快照创建时间 ≈ $O(N_{active})$
- $T_{scan}$: 索引扫描时间
- $T_{visibility}$: 可见性检查时间 ≈ $O(\log N_{active})$

**写密集负载**:

$$TPS_{write} = \frac{C}{T_{lock} + T_{insert} + T_{wal}}$$

其中:

- $T_{lock}$: 锁获取时间（写写冲突）
- $T_{insert}$: 元组插入时间
- $T_{wal}$: WAL写入时间

### 7.2 空间开销

**版本膨胀**:

$$SpaceOverhead = \sum_{row} |\text{VersionChain}(row)| \cdot \text{TupleSize}$$

**最坏情况**: 长事务 + 高频更新

$$|\text{VersionChain}| \propto T_{long\_tx} \cdot \text{UpdateRate}$$

**示例**:

- 长事务运行时间: 1小时
- 更新频率: 1000次/秒
- 版本数: $3600 \times 1000 = 3.6M$ 版本

### 7.3 VACUUM开销

**时间复杂度**:

$$T_{vacuum} = T_{scan} + T_{index\_clean} + T_{fsm\_update}$$

- $T_{scan} = O(N_{pages})$
- $T_{index\_clean} = O(N_{dead} \cdot N_{indexes} \cdot \log N_{index\_entries})$
- $T_{fsm\_update} = O(N_{pages})$

**权衡**:

- VACUUM过于频繁 → CPU/IO开销大
- VACUUM不足 → 表膨胀严重

**自动VACUUM触发条件**:

$$\text{Trigger} \iff N_{dead} > \text{threshold} + \text{scale\_factor} \cdot N_{total}$$

默认: $threshold=50$, $scale\_factor=0.2$

---

## 八、与其他MVCC实现对比

### 8.1 PostgreSQL vs MySQL InnoDB

| 维度 | PostgreSQL | MySQL InnoDB |
|-----|------------|--------------|
| **版本存储** | Heap表内（多版本） | Undo表空间（单版本+回滚段） |
| **版本链** | 前向链（新→旧） | 后向链（旧←新） |
| **清理机制** | VACUUM (后台进程) | Purge线程 (自动) |
| **索引影响** | 每版本一个索引项 | 索引项不变（通过Undo） |
| **空间开销** | 表膨胀 | Undo空间膨胀 |
| **长事务影响** | 版本链变长 | Undo链变长 |

### 8.2 理论优劣

**PostgreSQL优势**:

- ✅ 读性能高（直接读历史版本）
- ✅ 实现简单（无需Undo日志）

**PostgreSQL劣势**:

- ❌ 表膨胀严重（需频繁VACUUM）
- ❌ 索引膨胀（每版本一个索引项）

**InnoDB优势**:

- ✅ 空间利用率高（In-place更新）
- ✅ 无表膨胀（Undo单独管理）

**InnoDB劣势**:

- ❌ Undo回滚复杂
- ❌ 长事务导致Undo链长

---

## 九、总结

### 9.1 核心贡献

**理论贡献**:

1. **完整的可见性证明**（定理2.1）
2. **时空复杂度分析**（第2.3节）
3. **隔离级别形式化**（第四章）

**工程价值**:

1. **HOT优化**：减少索引写放大
2. **Visibility Map**：加速Index-Only Scan
3. **Parallel VACUUM**：降低清理开销

### 9.2 关键公式

**可见性判断**:

$$Visible(v, snap) \iff (v.xmin < snap.xmax \land v.xmin \notin snap.xip) \land$$
$$(v.xmax = 0 \lor v.xmax \geq snap.xmax \lor v.xmax \in snap.xip)$$

**吞吐量预测**:

$$TPS = \frac{Concurrency}{AvgLatency} \cdot IsolationFactor \cdot VacuumFactor$$

### 9.3 设计原则

1. **版本优于锁**: 用存储空间换并发性能
2. **延迟清理**: 后台VACUUM异步清理
3. **分层优化**: HOT/Visibility Map针对性优化

---

## 十、延伸阅读

**理论基础**:

- Bernstein, P. A., & Goodman, N. (1983). "Multiversion concurrency control" → MVCC理论奠基
- Ports, D. R., & Grittner, K. (2012). "Serializable Snapshot Isolation in PostgreSQL" → SSI实现

**实现细节**:

- PostgreSQL源码: `src/backend/access/heap/heapam_visibility.c`
- VACUUM源码: `src/backend/commands/vacuum.c`
- HOT实现: `src/backend/access/heap/pruneheap.c`

**扩展方向**:

- `03-证明与形式化/02-MVCC正确性证明.md` → 完整的数学证明
- `05-实现机制/01-PostgreSQL-MVCC实现.md` → 源码级分析
- `06-性能分析/03-存储开销分析.md` → 量化空间开销

---

**版本**: 1.0.0
**最后更新**: 2025-12-05
**关联文档**:

- `01-核心理论模型/01-分层状态演化模型(LSEM).md`
- `02-设计权衡分析/02-隔离级别权衡矩阵.md`
