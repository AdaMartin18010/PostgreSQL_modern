# 04 | 常见问题解答 (FAQ)

> **工具定位**: 本文档回答学习和使用过程中的常见问题，提供快速解答。

---

## 📑 目录

- [04 | 常见问题解答 (FAQ)](#04--常见问题解答-faq)
  - [📑 目录](#-目录)
  - [一、理论基础问题](#一理论基础问题)
    - [Q1: LSEM模型的核心是什么？](#q1-lsem模型的核心是什么)
    - [Q2: 三大公理是什么？](#q2-三大公理是什么)
    - [Q3: MVCC如何保证隔离性？](#q3-mvcc如何保证隔离性)
    - [Q4: CAP定理如何理解？](#q4-cap定理如何理解)
  - [二、技术实现问题](#二技术实现问题)
    - [Q5: PostgreSQL如何实现MVCC？](#q5-postgresql如何实现mvcc)
    - [Q6: Rust如何保证线程安全？](#q6-rust如何保证线程安全)
    - [Q7: Raft如何保证一致性？](#q7-raft如何保证一致性)
  - [三、性能优化问题](#三性能优化问题)
    - [Q8: 如何选择合适的隔离级别？](#q8-如何选择合适的隔离级别)
    - [Q9: 表膨胀如何解决？](#q9-表膨胀如何解决)
    - [Q10: 如何预测系统TPS？](#q10-如何预测系统tps)
  - [四、分布式系统问题](#四分布式系统问题)
    - [Q11: 如何在CP和AP之间选择？](#q11-如何在cp和ap之间选择)
    - [Q12: 2PC的阻塞问题如何解决？](#q12-2pc的阻塞问题如何解决)
    - [Q13: Percolator如何扩展MVCC？](#q13-percolator如何扩展mvcc)
  - [五、学习使用问题](#五学习使用问题)
    - [Q14: 从哪里开始学习？](#q14-从哪里开始学习)
    - [Q15: 如何快速解决实际问题？](#q15-如何快速解决实际问题)
    - [Q16: 如何引用本体系？](#q16-如何引用本体系)
    - [Q17: 如何贡献改进？](#q17-如何贡献改进)
    - [Q18: 文档如何更新维护？](#q18-文档如何更新维护)
  - [🔍 更多问题？](#-更多问题)
    - [查找答案](#查找答案)
    - [还是没找到？](#还是没找到)
  - [六、实际应用问题](#六实际应用问题)
    - [Q19: 如何调试MVCC可见性问题？](#q19-如何调试mvcc可见性问题)
    - [Q20: 如何优化高并发写入性能？](#q20-如何优化高并发写入性能)
    - [Q21: 如何监控死锁？](#q21-如何监控死锁)
    - [Q22: 如何选择分布式事务协议？](#q22-如何选择分布式事务协议)
  - [七、理论深入问题](#七理论深入问题)
    - [Q23: LSEM如何统一MVCC和2PL？](#q23-lsem如何统一mvcc和2pl)
    - [Q24: 如何证明MVCC的正确性？](#q24-如何证明mvcc的正确性)
    - [Q25: CAP定理的数学证明？](#q25-cap定理的数学证明)
  - [八、性能调优问题](#八性能调优问题)
    - [Q26: 如何优化VACUUM性能？](#q26-如何优化vacuum性能)
    - [Q27: 如何预测系统容量？](#q27-如何预测系统容量)
    - [Q28: 如何优化索引选择？](#q28-如何优化索引选择)
  - [九、错误排查问题](#九错误排查问题)
    - [Q29: 事务一直等待，如何排查？](#q29-事务一直等待如何排查)
    - [Q30: 表膨胀严重，如何快速解决？](#q30-表膨胀严重如何快速解决)
  - [十、进阶研究问题](#十进阶研究问题)
    - [Q31: 如何扩展LSEM到新场景？](#q31-如何扩展lsem到新场景)
    - [Q32: 如何验证理论正确性？](#q32-如何验证理论正确性)

---

## 一、理论基础问题

### Q1: LSEM模型的核心是什么？

**A**: LSEM将并发控制抽象为跨层状态演化问题

$$LSEM = (States, Timestamp, Visible, Conflict)$$

三层：L0(存储)、L1(运行时)、L2(分布式)

**详见**: [01-LSEM模型](../01-核心理论模型/01-分层状态演化模型(LSEM).md)

### Q2: 三大公理是什么？

**A**:

1. **公理1**: 状态原子性 - 状态转换不可分
2. **公理2**: 可见性偏序 - 满足偏序关系
3. **公理3**: 冲突可串行化 - 等价于串行执行

**详见**: [01-公理系统证明](../03-证明与形式化/01-公理系统证明.md)

### Q3: MVCC如何保证隔离性？

**A**: 通过快照机制，每个事务看到一致的数据版本

```python
def visible(tuple, snapshot):
    return (tuple.xmin < snapshot.xmin and
            tuple.xmax not in snapshot.xip)
```

**详见**: [02-MVCC理论](../01-核心理论模型/02-MVCC理论完整解析.md)

### Q4: CAP定理如何理解？

**A**: 分布式系统无法同时满足C(一致性)、A(可用性)、P(分区容错)

$$C \land A \land P = \emptyset$$

实践中选择CP或AP

**详见**: [04-CAP理论](../01-核心理论模型/04-CAP理论与权衡.md)

---

## 二、技术实现问题

### Q5: PostgreSQL如何实现MVCC？

**A**:

- **版本链**: 元组头部xmin/xmax + ctid指针
- **快照**: (xmin, xmax, xip)三元组
- **可见性检查**: HeapTupleSatisfiesMVCC函数

**详见**: [01-PostgreSQL-MVCC实现](../05-实现机制/01-PostgreSQL-MVCC实现.md)

### Q6: Rust如何保证线程安全？

**A**:

- **编译期检查**: 借用检查器
- **所有权规则**: 唯一所有权 + 借用排他性
- **Send/Sync trait**: 类型系统保证

$$ThreadSafe = OwnershipRules + BorrowChecker$$

**详见**: [06-所有权模型](../01-核心理论模型/06-所有权模型(Rust).md)

### Q7: Raft如何保证一致性？

**A**:

- **多数派机制**: 写入多数派节点
- **Leader唯一性**: 每个term至多一个Leader
- **日志匹配**: Log Matching Property

**详见**: [08-共识协议理论](../01-核心理论模型/08-共识协议理论.md)

---

## 三、性能优化问题

### Q8: 如何选择合适的隔离级别？

**A**: 使用决策矩阵

| 业务类型 | 推荐级别 | 理由 |
|---------|---------|------|
| Web应用 | RC | 性能优先 |
| 报表 | RR | 一致视图 |
| 金融 | Serializable | 强一致 |

**详见**: [02-隔离级别权衡矩阵](../02-设计权衡分析/02-隔离级别权衡矩阵.md)

### Q9: 表膨胀如何解决？

**A**:

1. 终止长事务
2. 调整autovacuum参数
3. 降低fillfactor（预留HOT空间）
4. 必要时VACUUM FULL

**详见**: [05-存储-并发权衡](../02-设计权衡分析/05-存储-并发权衡.md)

### Q10: 如何预测系统TPS？

**A**: 使用性能公式

$$TPS = \frac{Concurrency}{Latency} \times IsolationFactor$$

或使用性能估算器代码

**详见**: [01-吞吐量公式推导](../06-性能分析/01-吞吐量公式推导.md)

---

## 四、分布式系统问题

### Q11: 如何在CP和AP之间选择？

**A**: 使用CAP决策树

```
需要强一致性？
  └─ 是 → CP (etcd, PostgreSQL同步)
  └─ 否 → AP (Cassandra, DynamoDB)
```

**详见**: [03-CAP权衡决策模型](../02-设计权衡分析/03-CAP权衡决策模型.md)

### Q12: 2PC的阻塞问题如何解决？

**A**:

- **方案1**: 使用3PC（引入超时）
- **方案2**: 使用Saga（最终一致性）
- **方案3**: 使用TCC（资源预留）

**详见**: [02-分布式事务协议](../04-分布式扩展/02-分布式事务协议.md)

### Q13: Percolator如何扩展MVCC？

**A**:

- 使用Bigtable存储多版本
- 全局Timestamp Oracle
- Chubby分布式锁

**详见**: [01-分布式MVCC(Percolator)](../04-分布式扩展/01-分布式MVCC(Percolator).md)

---

## 五、学习使用问题

### Q14: 从哪里开始学习？

**A**:

1. 阅读 [README.md](../README.md) - 10分钟
2. 浏览 [理论全景图](./00-理论体系全景图.md) - 30分钟
3. 选择学习路径 [学习路径指南](./02-学习路径指南.md)
4. 开始系统学习

### Q15: 如何快速解决实际问题？

**A**: 使用快速导航

1. 访问 [快速导航索引](../快速导航索引.md)
2. 按问题类型查找
3. 直接跳转到相关决策树
4. 应用工具解决问题

### Q16: 如何引用本体系？

**A**: 学术引用格式

```
PostgreSQL理论研究组. (2025). 事务与并发设计理论体系 (TCDT) v1.0.0.
Retrieved from e:/_src/PostgreSQL_modern/DataBaseTheory/90-事务与并发设计理论体系/
```

### Q17: 如何贡献改进？

**A**:

1. 发现错误或改进点
2. 记录具体位置和建议
3. 提交Issue或Pull Request
4. 参与讨论和Review

### Q18: 文档如何更新维护？

**A**:

- **版本号**: 每个文档都有版本标注
- **更新时间**: 标注最后更新日期
- **关联文档**: 列出相关文档链接
- **持续维护**: 根据反馈持续改进

---

## 🔍 更多问题？

### 查找答案

1. **搜索关键词**: 使用 [核心概念词典](./01-核心概念词典.md)
2. **按主题查找**: 使用 [快速导航索引](../快速导航索引.md)
3. **查看思考题**: 每章末尾的思考题及答案

### 还是没找到？

- 查看 [未解决问题清单](../08-扩展规划/02-未解决问题清单.md)
- 可能是前沿研究问题
- 欢迎提出新问题

---

## 六、实际应用问题

### Q19: 如何调试MVCC可见性问题？

**A**: 使用PostgreSQL工具

```sql
-- 1. 查看当前快照
SELECT pg_current_snapshot();
-- 输出: 100:100: (无活跃事务)

-- 2. 查看元组版本信息
SELECT
    xmin, xmax, ctid,
    (xmin::text::xid < pg_snapshot_xmin(pg_current_snapshot())) AS xmin_committed
FROM accounts WHERE id = 1;

-- 3. 查看活跃事务
SELECT pid, xid, query
FROM pg_stat_activity
WHERE xid IS NOT NULL;
```

**详见**: [PostgreSQL-MVCC实现](../05-实现机制/01-PostgreSQL-MVCC实现.md)

### Q20: 如何优化高并发写入性能？

**A**: 多维度优化策略

**策略1: 行分散**

```sql
-- 预分配多行，随机选择
CREATE TABLE inventory (
    product_id INT,
    shard_id INT,  -- 0-9
    stock INT,
    PRIMARY KEY (product_id, shard_id)
);

-- 写入时随机选择
UPDATE inventory
SET stock = stock - 1
WHERE product_id = 1
  AND shard_id = floor(random() * 10)::int;
```

**策略2: 乐观锁**

```python
def deduct_stock(product_id, amount):
    max_retries = 10
    for i in range(max_retries):
        row = db.execute("SELECT stock, version FROM inventory WHERE id = %s", (product_id,))

        if row.stock < amount:
            return False

        affected = db.execute("""
            UPDATE inventory
            SET stock = stock - %s, version = version + 1
            WHERE id = %s AND version = %s
        """, (amount, product_id, row.version)).rowcount

        if affected > 0:
            return True

        time.sleep(0.001 * (i + 1))  # 指数退避

    return False
```

**策略3: 批量写入**

```sql
-- 使用COPY批量插入
COPY orders (user_id, product_id, amount)
FROM '/tmp/orders.csv' WITH CSV;
```

**详见**: [工程实践指南](../08-扩展规划/03-工程实践指南.md)

### Q21: 如何监控死锁？

**A**: PostgreSQL死锁监控

```sql
-- 1. 查看死锁日志
SELECT * FROM pg_stat_database_conflicts;

-- 2. 查看等待关系
SELECT
    waiting.pid AS waiter_pid,
    waiting.query AS waiter_query,
    blocking.pid AS blocker_pid,
    blocking.query AS blocker_query
FROM pg_stat_activity AS waiting
JOIN pg_stat_activity AS blocking
    ON blocking.pid = ANY(pg_blocking_pids(waiting.pid))
WHERE waiting.wait_event_type = 'Lock';

-- 3. 查看锁等待时间
SELECT
    pid,
    wait_event_type,
    wait_event,
    state,
    query_start,
    NOW() - query_start AS wait_duration
FROM pg_stat_activity
WHERE wait_event_type = 'Lock'
ORDER BY wait_duration DESC;
```

**详见**: [PostgreSQL-锁机制](../05-实现机制/02-PostgreSQL-锁机制.md)

### Q22: 如何选择分布式事务协议？

**A**: 使用决策树

```text
需要强一致性？
  ├─ 是 → 需要原子性？
  │   ├─ 是 → 2PC/3PC
  │   └─ 否 → Saga
  └─ 否 → 最终一致性
      └─ 事件驱动/消息队列
```

**协议对比**:

| 协议 | 一致性 | 性能 | 复杂度 | 适用场景 |
|-----|-------|------|--------|---------|
| **2PC** | 强 | 低 | 中 | 金融交易 |
| **3PC** | 强 | 中 | 高 | 高可用系统 |
| **Saga** | 最终 | 高 | 中 | 长事务 |
| **TCC** | 强 | 中 | 高 | 资源预留 |

**详见**: [分布式事务协议](../04-分布式扩展/02-分布式事务协议.md)

---

## 七、理论深入问题

### Q23: LSEM如何统一MVCC和2PL？

**A**: 通过状态空间映射

```text
MVCC (乐观):
├─ L0: 版本链 (多版本状态)
├─ L1: 快照 (时间戳)
└─ 冲突: 写-写冲突检测

2PL (悲观):
├─ L0: 锁表 (锁状态)
├─ L1: 锁请求序列
└─ 冲突: 锁冲突检测

统一视角:
└─ 都是状态演化 + 冲突检测
```

**详见**: [并发控制统一框架](../01-核心理论模型/05-并发控制理论统一框架.md)

### Q24: 如何证明MVCC的正确性？

**A**: 形式化证明

**定理**: MVCC保证快照隔离

**证明步骤**:

1. **快照一致性**: 所有读操作使用同一快照
2. **可见性单调性**: 已见版本不会消失
3. **无幻读**: 谓词锁 + 快照

**详见**: [MVCC正确性证明](../03-证明与形式化/02-MVCC正确性证明.md)

### Q25: CAP定理的数学证明？

**A**: 反证法

**假设**: 存在系统同时满足C、A、P

**证明**:

```text
1. 网络分区发生 (P必须满足)
2. 节点A和B无法通信
3. 客户端请求写入节点A
4. 选择1: 等待B确认 → 违反A (不可用)
5. 选择2: 不等待B → 违反C (不一致)
6. 矛盾 → 假设不成立
```

**详见**: [CAP理论与权衡](../01-核心理论模型/04-CAP理论与权衡.md)

---

## 八、性能调优问题

### Q26: 如何优化VACUUM性能？

**A**: 多维度优化

**优化1: 调整参数**

```sql
-- 增加并行度
SET maintenance_work_mem = '2GB';
SET max_parallel_maintenance_workers = 4;

-- 调整触发阈值
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_vacuum_threshold = 1000
);
```

**优化2: 使用并行VACUUM**

```sql
VACUUM (PARALLEL 4) orders;
```

**优化3: 分区表策略**

```sql
-- 按时间分区，只VACUUM活跃分区
CREATE TABLE orders (
    id BIGINT,
    created_at TIMESTAMP
) PARTITION BY RANGE (created_at);

-- 只VACUUM最近分区
VACUUM orders_2025_12;
```

**详见**: [PostgreSQL-VACUUM机制](../05-实现机制/03-PostgreSQL-VACUUM机制.md)

### Q27: 如何预测系统容量？

**A**: 使用性能模型

**公式**:

$$TPS = \frac{Concurrency}{AvgLatency} \times (1 - AbortRate)$$

**Python实现**:

```python
def predict_tps(concurrency, avg_latency_ms, abort_rate=0.05):
    """预测系统TPS"""
    tps = (concurrency / (avg_latency_ms / 1000)) * (1 - abort_rate)
    return tps

# 示例
concurrency = 100
avg_latency_ms = 50
abort_rate = 0.02

predicted_tps = predict_tps(concurrency, avg_latency_ms, abort_rate)
print(f"预测TPS: {predicted_tps:.0f}")
# 输出: 预测TPS: 1960
```

**详见**: [吞吐量公式推导](../06-性能分析/01-吞吐量公式推导.md)

### Q28: 如何优化索引选择？

**A**: 使用决策树

```text
查询模式？
  ├─ 等值查询 → B-tree
  ├─ 范围查询 → B-tree
  ├─ 全文搜索 → GIN
  ├─ 数组查询 → GIN
  ├─ 空间查询 → GiST
  └─ 低基数 → BRIN
```

**实际案例**:

```sql
-- 场景: 时间序列数据
CREATE TABLE sensor_data (
    sensor_id INT,
    timestamp TIMESTAMP,
    value FLOAT
);

-- 选择: BRIN索引（时间有序）
CREATE INDEX idx_sensor_time ON sensor_data
USING BRIN (timestamp);

-- 查询性能: 提升10×
```

**详见**: [索引选择决策树](../07-可视化与思维模型/03-决策树图集.md)

---

## 九、错误排查问题

### Q29: 事务一直等待，如何排查？

**A**: 排查步骤

**步骤1: 查看等待关系**

```sql
SELECT
    waiting.pid,
    waiting.query,
    blocking.pid,
    blocking.query,
    waiting.wait_event
FROM pg_stat_activity AS waiting
JOIN pg_stat_activity AS blocking
    ON blocking.pid = ANY(pg_blocking_pids(waiting.pid));
```

**步骤2: 查看锁信息**

```sql
SELECT
    locktype,
    relation::regclass,
    mode,
    granted,
    pid
FROM pg_locks
WHERE NOT granted
ORDER BY pid;
```

**步骤3: 终止阻塞事务**

```sql
-- 查看事务详情
SELECT pid, xid, query, state, query_start
FROM pg_stat_activity
WHERE pid = <blocking_pid>;

-- 终止事务（谨慎使用）
SELECT pg_terminate_backend(<blocking_pid>);
```

**详见**: [PostgreSQL-锁机制](../05-实现机制/02-PostgreSQL-锁机制.md)

### Q30: 表膨胀严重，如何快速解决？

**A**: 紧急处理方案

**方案1: 立即VACUUM**

```sql
-- 普通VACUUM（不锁表）
VACUUM ANALYZE orders;

-- 如果无效，使用VACUUM FULL（锁表）
VACUUM FULL orders;
```

**方案2: 重建表**

```sql
-- 创建新表
CREATE TABLE orders_new (LIKE orders INCLUDING ALL);

-- 迁移数据
INSERT INTO orders_new SELECT * FROM orders;

-- 替换表
BEGIN;
ALTER TABLE orders RENAME TO orders_old;
ALTER TABLE orders_new RENAME TO orders;
COMMIT;

-- 删除旧表
DROP TABLE orders_old;
```

**方案3: 预防措施**

```sql
-- 调整fillfactor（预留HOT空间）
ALTER TABLE orders SET (fillfactor = 80);

-- 调整autovacuum参数
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_vacuum_threshold = 1000
);
```

**详见**: [存储-并发权衡](../02-设计权衡分析/05-存储-并发权衡.md)

---

## 十、进阶研究问题

### Q31: 如何扩展LSEM到新场景？

**A**: 扩展步骤

**步骤1: 识别新层**

```text
现有: L0(存储) L1(运行时) L2(分布式)
新场景: 边缘计算
→ 新增L3(边缘层)
```

**步骤2: 定义状态空间**

```python
class EdgeState:
    """边缘层状态"""
    def __init__(self):
        self.device_id: str
        self.local_version: int
        self.sync_status: SyncStatus
```

**步骤3: 定义可见性规则**

```python
def is_visible_edge(state: EdgeState, snapshot: EdgeSnapshot) -> bool:
    """边缘层可见性"""
    return (state.local_version < snapshot.edge_version and
            state.sync_status == SyncStatus.SYNCED)
```

**详见**: [LSEM模型](../01-核心理论模型/01-分层状态演化模型(LSEM).md)

### Q32: 如何验证理论正确性？

**A**: 形式化验证方法

**方法1: 定理证明**

```coq
(* Coq形式化验证 *)
Theorem mvcc_snapshot_isolation:
  forall (tx: Transaction) (snapshot: Snapshot),
    snapshot_consistent tx snapshot ->
    isolation_guaranteed tx snapshot.
Proof.
  (* 证明过程 *)
Qed.
```

**方法2: 模型检查**

```tla
(* TLA+模型检查 *)
VARIABLES committed, active, snapshot

Init == committed = {} /\ active = {} /\ snapshot = {}

Next == \/ BeginTransaction
        \/ CommitTransaction
        \/ ReadTransaction

Spec == Init /\ [][Next]_vars
```

**详见**: [证明与形式化](../03-证明与形式化/)

---

**版本**: 2.0.0（大幅充实）
**创建日期**: 2025-12-05
**最后更新**: 2025-12-05
**新增内容**: 实际应用问题、理论深入问题、性能调优、错误排查、进阶研究

**问答数**: 32+
**状态**: 持续更新

**关联文档**:

- [核心概念词典.md](./01-核心概念词典.md)
- [快速导航索引.md](../快速导航索引.md)
- [学习路径指南.md](./02-学习路径指南.md)
