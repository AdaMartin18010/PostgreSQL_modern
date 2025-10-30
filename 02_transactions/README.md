# 02_transactions — 事务管理与并发控制

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **模块完整度**：⭐⭐⭐⭐ 85%（已深化，持续完善）  
> **适合人群**：理解事务 ACID、MVCC 机制、隔离级别、锁机制及生产实践

---

## 📋 目录

- [02\_transactions — 事务管理与并发控制](#02_transactions--事务管理与并发控制)
  - [📋 目录](#-目录)
  - [模块定位与边界](#模块定位与边界)
    - [主题边界](#主题边界)
    - [知识地图](#知识地图)
  - [1. ACID 特性与实现](#1-acid-特性与实现)
    - [1.1 原子性（Atomicity）](#11-原子性atomicity)
    - [1.2 一致性（Consistency）](#12-一致性consistency)
    - [1.3 隔离性（Isolation）](#13-隔离性isolation)
    - [1.4 持久性（Durability）](#14-持久性durability)
  - [2. MVCC 多版本并发控制](#2-mvcc-多版本并发控制)
    - [2.1 MVCC 核心原理](#21-mvcc-核心原理)
    - [2.2 事务 ID（XID）与快照](#22-事务-idxid与快照)
      - [事务 ID（Transaction ID）](#事务-idtransaction-id)
      - [快照（Snapshot）](#快照snapshot)
    - [2.3 可见性规则](#23-可见性规则)
    - [2.4 XID 回卷与冻结](#24-xid-回卷与冻结)
  - [3. 事务隔离级别](#3-事务隔离级别)
    - [3.1 隔离级别对比](#31-隔离级别对比)
    - [3.2 Read Committed（默认）](#32-read-committed默认)
    - [3.3 Repeatable Read](#33-repeatable-read)
    - [3.4 Serializable（SSI）](#34-serializablessi)
    - [3.5 异常现象实战演示](#35-异常现象实战演示)
      - [脏读（Dirty Read）- PostgreSQL 不会发生](#脏读dirty-read--postgresql-不会发生)
      - [不可重复读（Non-Repeatable Read）](#不可重复读non-repeatable-read)
      - [幻读（Phantom Read）](#幻读phantom-read)
  - [4. 锁机制](#4-锁机制)
    - [4.1 锁类型与级别](#41-锁类型与级别)
    - [4.2 表级锁](#42-表级锁)
    - [4.3 行级锁](#43-行级锁)
    - [4.4 死锁检测与处理](#44-死锁检测与处理)
    - [4.5 锁诊断与监控](#45-锁诊断与监控)
      - [查询当前锁](#查询当前锁)
      - [查询锁等待](#查询锁等待)
      - [查询长时间持锁](#查询长时间持锁)
  - [5. 事务控制语句](#5-事务控制语句)
  - [6. 长事务管理](#6-长事务管理)
    - [6.1 长事务的危害](#61-长事务的危害)
    - [6.2 监控长事务](#62-监控长事务)
    - [6.3 长事务处理](#63-长事务处理)
    - [6.4 长事务最佳实践](#64-长事务最佳实践)
  - [7. PostgreSQL 17 并发优化](#7-postgresql-17-并发优化)
    - [7.1 高并发写入优化](#71-高并发写入优化)
    - [7.2 VACUUM 内存管理优化](#72-vacuum-内存管理优化)
  - [8. 生产实践与调优](#8-生产实践与调优)
    - [8.1 隔离级别选择](#81-隔离级别选择)
    - [8.2 锁优化策略](#82-锁优化策略)
    - [8.3 监控指标](#83-监控指标)
  - [9. 权威参考](#9-权威参考)
    - [官方文档](#官方文档)
    - [学术论文](#学术论文)
    - [扩展阅读](#扩展阅读)
  - [10. Checklist](#10-checklist)
    - [事务设计检查清单](#事务设计检查清单)
    - [并发控制检查清单](#并发控制检查清单)
    - [监控与诊断检查清单](#监控与诊断检查清单)
    - [性能优化检查清单](#性能优化检查清单)

---

## 模块定位与边界

### 主题边界

- **核心内容**：事务 ACID 特性、MVCC 机制、隔离级别、锁机制、并发控制
- **深度定位**：从理论到实践，涵盖 MVCC 原理、4 种隔离级别实战、死锁案例、长事务治理
- **PostgreSQL 17 对齐**：高并发写入优化、B-tree 锁改进

### 知识地图

```text
ACID特性
    ├── 原子性（日志、回滚）
    ├── 一致性（约束、触发器）
    ├── 隔离性（MVCC、锁）
    └── 持久性（WAL、fsync）
        ↓
MVCC多版本并发控制
    ├── 事务ID（XID）与快照
    ├── 可见性规则（xmin/xmax/cmin/cmax）
    ├── 元组版本链
    └── XID回卷与冻结
        ↓
事务隔离级别
    ├── Read Committed（默认）
    ├── Repeatable Read
    ├── Serializable（SSI）
    └── 异常现象（脏读、不可重复读、幻读、序列化异常）
        ↓
锁机制
    ├── 表级锁（8种）
    ├── 行级锁（4种）
    ├── 咨询锁（Advisory Lock）
    └── 死锁检测
        ↓
事务调优
    ├── 长事务监控
    ├── 锁等待分析
    ├── 死锁预防
    └── 并发性能优化
```

---

## 1. ACID 特性与实现

### 1.1 原子性（Atomicity）

**定义**：事务中的所有操作要么全部成功，要么全部失败回滚。

**PostgreSQL 实现**：

- **WAL（Write-Ahead Logging）**：所有修改先写日志，后写数据文件
- **回滚机制**：通过撤销日志恢复到事务开始前的状态

```sql
-- 原子性示例
BEGIN;
INSERT INTO accounts (id, balance) VALUES (1, 1000);
INSERT INTO accounts (id, balance) VALUES (2, 2000);
-- 如果第二条INSERT失败（如违反约束），整个事务回滚
COMMIT;

-- 手动回滚
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- 发现错误，手动回滚
ROLLBACK;
```

### 1.2 一致性（Consistency）

**定义**：事务执行前后，数据库从一个一致状态转换到另一个一致状态。

**PostgreSQL 实现**：

- **约束检查**：PRIMARY KEY、FOREIGN KEY、UNIQUE、CHECK
- **触发器**：在事务内执行业务规则校验
- **延迟约束**：DEFERRABLE 约束在事务结束时检查

```sql
-- 一致性示例：转账事务保持总额不变
CREATE TABLE accounts (
  id int PRIMARY KEY,
  balance numeric CHECK (balance >= 0)
);

BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1; -- 余额减少
UPDATE accounts SET balance = balance + 100 WHERE id = 2; -- 余额增加
-- 如果账户1余额不足100，CHECK约束失败，事务回滚
COMMIT;

-- 延迟约束示例
CREATE TABLE orders (
  id int PRIMARY KEY,
  total_amount numeric,
  paid_amount numeric,
  CONSTRAINT check_payment CHECK (paid_amount <= total_amount) DEFERRABLE INITIALLY DEFERRED
);

BEGIN;
INSERT INTO orders (id, total_amount, paid_amount) VALUES (1, 100, 150); -- 暂时违反约束
UPDATE orders SET total_amount = 200 WHERE id = 1; -- 修正后满足约束
COMMIT; -- 提交时检查约束
```

### 1.3 隔离性（Isolation）

**定义**：并发执行的事务之间互不干扰。

**PostgreSQL 实现**：

- **MVCC（多版本并发控制）**：读不阻塞写，写不阻塞读
- **4 种隔离级别**：Read Uncommitted（实际实现为 Read Committed）、Read Committed、Repeatable
  Read、Serializable

详见 [3. 事务隔离级别](#3-事务隔离级别)

### 1.4 持久性（Durability）

**定义**：事务一旦提交，修改永久保存，即使系统崩溃也不会丢失。

**PostgreSQL 实现**：

- **WAL（Write-Ahead Logging）**：事务提交前，日志必须落盘
- **fsync**：确保数据刷到磁盘
- **Checkpoint**：定期将脏页刷盘

```sql
-- 持久性配置参数
SHOW fsync;                    -- on（默认，确保持久性）
SHOW synchronous_commit;       -- on（默认，同步提交）
SHOW wal_level;                -- replica（默认）

-- 性能与持久性权衡（高风险，仅测试环境）
SET synchronous_commit = off;  -- 异步提交（可能丢失最后几秒数据）
```

---

## 2. MVCC 多版本并发控制

### 2.1 MVCC 核心原理

**多版本并发控制**（Multi-Version Concurrency Control）：

- 每个事务看到的是数据的一个**快照**（Snapshot）
- 读操作不阻塞写操作，写操作不阻塞读操作
- 通过保存数据的多个版本实现并发控制

**优势**：

- ✅ 读写不冲突，高并发性能好
- ✅ 不需要读锁，减少锁竞争
- ✅ 支持时间点恢复（PITR）

**代价**：

- ⚠️ 旧版本数据需要清理（VACUUM）
- ⚠️ 表膨胀（Bloat）问题
- ⚠️ 事务 ID 回卷风险

### 2.2 事务 ID（XID）与快照

#### 事务 ID（Transaction ID）

```sql
-- 查看当前事务ID
SELECT txid_current();

-- 查看当前快照
SELECT txid_current_snapshot();
-- 输出示例：100:105:100,102
-- 格式：xmin:xmax:xip_list
-- xmin: 最小活跃事务ID
-- xmax: 下一个分配的事务ID
-- xip_list: 当前活跃事务ID列表

-- 查看表的XID信息
SELECT relname, age(relfrozenxid) AS xid_age
FROM pg_class
WHERE relkind = 'r'
ORDER BY age(relfrozenxid) DESC
LIMIT 10;
```

#### 快照（Snapshot）

- **快照创建时机**：
  - Read Committed：每条 SQL 语句开始时创建新快照
  - Repeatable Read/Serializable：事务开始时创建快照，整个事务使用同一快照

### 2.3 可见性规则

每个元组（行）有 4 个系统列：

- `xmin`：插入该行的事务 ID
- `xmax`：删除该行的事务 ID（0 表示未删除）
- `cmin`：插入该行的命令 ID（同一事务内）
- `cmax`：删除该行的命令 ID（同一事务内）

```sql
-- 查看系统列
CREATE TABLE test_mvcc (id int, value text);
INSERT INTO test_mvcc VALUES (1, 'v1');
UPDATE test_mvcc SET value = 'v2' WHERE id = 1;

-- 查看隐藏列（需要使用pageinspect扩展）
CREATE EXTENSION IF NOT EXISTS pageinspect;
SELECT lp, t_xmin, t_xmax, t_ctid
FROM heap_page_items(get_raw_page('test_mvcc', 0));
```

**可见性判断**： 1. 如果`xmin`未提交或在快照之后，该行不可见 2. 如果`xmax`已提交且在快照之前，该行不
可见（已删除） 3. 否则，该行可见

### 2.4 XID 回卷与冻结

**问题**：PostgreSQL 的事务 ID 是 32 位整数（约 42 亿），会回卷。

**解决方案**：冻结（Freezing）

- VACUUM 会将旧元组的`xmin`标记为"冻结"（FrozenXID = 2）
- 冻结后的行对所有事务可见

```sql
-- 查看需要冻结的表
SELECT relname, age(relfrozenxid) AS xid_age,
       pg_size_pretty(pg_total_relation_size(oid)) AS size
FROM pg_class
WHERE relkind = 'r' AND age(relfrozenxid) > 100000000 -- 1亿
ORDER BY age(relfrozenxid) DESC;

-- 手动冻结
VACUUM FREEZE table_name;

-- 配置参数
SHOW vacuum_freeze_min_age;       -- 5000万（默认）
SHOW vacuum_freeze_table_age;     -- 1.5亿（默认）
SHOW autovacuum_freeze_max_age;   -- 2亿（默认，触发紧急VACUUM）
```

---

## 3. 事务隔离级别

### 3.1 隔离级别对比

| 隔离级别             | 脏读    | 不可重复读 | 幻读    | 序列化异常 | 性能 | PostgreSQL 实现               |
| -------------------- | ------- | ---------- | ------- | ---------- | ---- | ----------------------------- |
| **Read Uncommitted** | ❌ 可能 | ❌ 可能    | ❌ 可能 | ❌ 可能    | 最高 | **实际等同于 Read Committed** |
| **Read Committed**   | ✅ 不会 | ❌ 可能    | ❌ 可能 | ❌ 可能    | 高   | **默认级别**                  |
| **Repeatable Read**  | ✅ 不会 | ✅ 不会    | ✅ 不会 | ❌ 可能    | 中   | SSI 部分实现                  |
| **Serializable**     | ✅ 不会 | ✅ 不会    | ✅ 不会 | ✅ 不会    | 低   | SSI 完整实现                  |

**PostgreSQL 特点**：

- 不存在真正的 Read Uncommitted（自动提升为 Read Committed）
- Repeatable Read 通过 MVCC 防止幻读（强于 SQL 标准）
- Serializable 使用 SSI（Serializable Snapshot Isolation）算法

### 3.2 Read Committed（默认）

**特性**：

- 每条 SQL 语句开始时创建新快照
- 只能读到已提交的数据（不会脏读）
- 同一事务内多次读取可能得到不同结果（不可重复读）

```sql
-- Session A
BEGIN;
SELECT balance FROM accounts WHERE id = 1; -- 假设返回1000

-- Session B
BEGIN;
UPDATE accounts SET balance = 1500 WHERE id = 1;
COMMIT;

-- Session A（同一事务内）
SELECT balance FROM accounts WHERE id = 1; -- 返回1500（不可重复读）
COMMIT;
```

**适用场景**：

- 大多数 OLTP 应用
- 对数据一致性要求不高
- 需要高并发性能

### 3.3 Repeatable Read

**特性**：

- 事务开始时创建快照，整个事务使用同一快照
- 不会出现不可重复读和幻读
- 更新冲突时抛出 serialization 错误

```sql
-- Session A
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1; -- 返回1000

-- Session B
BEGIN;
UPDATE accounts SET balance = 1500 WHERE id = 1;
COMMIT;

-- Session A（同一事务内）
SELECT balance FROM accounts WHERE id = 1; -- 仍返回1000（可重复读）

-- 如果Session A尝试更新
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- ERROR: could not serialize access due to concurrent update
ROLLBACK;
```

**适用场景**：

- 报表查询（需要一致性快照）
- 批量数据处理
- 需要避免不可重复读的应用

### 3.4 Serializable（SSI）

**特性**：

- 完全串行化执行的效果
- 检测读写依赖，防止序列化异常
- 冲突时抛出 serialization 错误，需要应用重试

```sql
-- 经典序列化异常示例：两个事务交叉读写

-- 初始数据
CREATE TABLE accounts (id int PRIMARY KEY, balance numeric);
INSERT INTO accounts VALUES (1, 1000), (2, 1000);

-- Session A
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(balance) FROM accounts; -- 2000
-- 假设业务逻辑：如果总额>=2000，允许取款
UPDATE accounts SET balance = balance - 500 WHERE id = 1;

-- Session B（并发执行）
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(balance) FROM accounts; -- 2000
UPDATE accounts SET balance = balance - 500 WHERE id = 2;

-- 提交顺序
-- Session A COMMIT; -- 成功
-- Session B COMMIT; -- ERROR: could not serialize access due to read/write dependencies
```

**适用场景**：

- 金融交易（严格一致性）
- 库存管理（防止超卖）
- 需要完全隔离的关键业务

**性能考虑**：

- Serializable 比 Repeatable Read 慢 10-20%
- 需要应用层实现重试逻辑

### 3.5 异常现象实战演示

#### 脏读（Dirty Read）- PostgreSQL 不会发生

```sql
-- Session A
BEGIN;
UPDATE accounts SET balance = 9999 WHERE id = 1;
-- 不提交

-- Session B（Read Committed或更高级别）
BEGIN;
SELECT balance FROM accounts WHERE id = 1;
-- PostgreSQL：返回原值（1000），不会读到未提交的9999
COMMIT;

-- Session A
ROLLBACK;
```

#### 不可重复读（Non-Repeatable Read）

```sql
-- Read Committed会出现，Repeatable Read不会

-- Session A (Read Committed)
BEGIN;
SELECT balance FROM accounts WHERE id = 1; -- 1000

-- Session B
BEGIN;
UPDATE accounts SET balance = 1500 WHERE id = 1;
COMMIT;

-- Session A
SELECT balance FROM accounts WHERE id = 1; -- 1500（不可重复读）
COMMIT;
```

#### 幻读（Phantom Read）

```sql
-- Read Committed会出现，Repeatable Read不会（PostgreSQL特性）

-- Session A (Read Committed)
BEGIN;
SELECT COUNT(*) FROM accounts WHERE balance > 500; -- 假设返回2

-- Session B
BEGIN;
INSERT INTO accounts VALUES (3, 600);
COMMIT;

-- Session A
SELECT COUNT(*) FROM accounts WHERE balance > 500; -- 返回3（幻读）
COMMIT;
```

---

## 4. 锁机制

### 4.1 锁类型与级别

PostgreSQL 有两大类锁：

1. **表级锁**（Table-Level Locks）：8 种模式
2. **行级锁**（Row-Level Locks）：4 种模式

### 4.2 表级锁

| 锁模式                       | 触发操作                               | 与自身冲突 | 阻塞 SELECT | 阻塞 INSERT/UPDATE/DELETE |
| ---------------------------- | -------------------------------------- | ---------- | ----------- | ------------------------- |
| **AccessShareLock**          | SELECT                                 | ❌         | ❌          | ❌                        |
| **RowShareLock**             | SELECT FOR UPDATE                      | ❌         | ❌          | ❌                        |
| **RowExclusiveLock**         | INSERT/UPDATE/DELETE                   | ❌         | ❌          | ❌                        |
| **ShareUpdateExclusiveLock** | VACUUM, CREATE INDEX CONCURRENTLY      | ✅         | ❌          | ❌                        |
| **ShareLock**                | CREATE INDEX                           | ❌         | ❌          | ✅                        |
| **ShareRowExclusiveLock**    | 少见                                   | ✅         | ❌          | ✅                        |
| **ExclusiveLock**            | REFRESH MATERIALIZED VIEW CONCURRENTLY | ✅         | ❌          | ✅                        |
| **AccessExclusiveLock**      | DROP TABLE, TRUNCATE, ALTER TABLE      | ✅         | ✅          | ✅                        |

```sql
-- 显式获取表级锁
BEGIN;
LOCK TABLE accounts IN ACCESS EXCLUSIVE MODE; -- 最严格的锁
-- ... 操作
COMMIT;

-- 查看当前锁
SELECT locktype, relation::regclass, mode, granted
FROM pg_locks
WHERE pid = pg_backend_pid();
```

### 4.3 行级锁

| 锁模式                | 获取方式                       | 说明                                 |
| --------------------- | ------------------------------ | ------------------------------------ |
| **FOR UPDATE**        | `SELECT ... FOR UPDATE`        | 独占锁，阻塞其他 FOR UPDATE 和修改   |
| **FOR NO KEY UPDATE** | `SELECT ... FOR NO KEY UPDATE` | 允许并发外键检查                     |
| **FOR SHARE**         | `SELECT ... FOR SHARE`         | 共享锁，阻塞修改但允许其他 FOR SHARE |
| **FOR KEY SHARE**     | `SELECT ... FOR KEY SHARE`     | 最弱的锁，仅阻塞 FOR UPDATE          |

```sql
-- FOR UPDATE示例（悲观锁）
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE; -- 锁定该行
-- 其他事务的UPDATE/DELETE/FOR UPDATE会被阻塞
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- NOWAIT（立即返回，不等待）
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
-- 如果行已被锁定，立即抛出错误而不是等待
COMMIT;

-- SKIP LOCKED（跳过已锁定的行，用于任务队列）
BEGIN;
SELECT * FROM job_queue WHERE status = 'pending'
ORDER BY priority DESC
LIMIT 10
FOR UPDATE SKIP LOCKED; -- 跳过被其他事务锁定的任务
-- 更新任务状态
UPDATE job_queue SET status = 'processing' WHERE id IN (...);
COMMIT;
```

### 4.4 死锁检测与处理

**死锁示例**：

```sql
-- Session A
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1; -- 锁定行1

-- Session B
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 2; -- 锁定行2

-- Session A
UPDATE accounts SET balance = balance + 100 WHERE id = 2; -- 等待Session B

-- Session B
UPDATE accounts SET balance = balance + 100 WHERE id = 1; -- 等待Session A
-- ERROR: deadlock detected
```

**死锁检测配置**：

```sql
SHOW deadlock_timeout; -- 1s（默认，检测死锁前等待时间）

-- 调整死锁检测时间
SET deadlock_timeout = '500ms'; -- 更快检测
```

**死锁预防策略**：

1. **统一锁顺序**：所有事务按相同顺序获取锁
2. **缩短事务时间**：避免长事务
3. **使用 NOWAIT**：快速失败并重试
4. **降低隔离级别**：使用 Read Committed 代替 Serializable

```sql
-- 统一锁顺序示例
BEGIN;
-- ✅ 正确：总是先锁定ID小的行
UPDATE accounts SET balance = balance - 100 WHERE id = LEAST(1, 2);
UPDATE accounts SET balance = balance + 100 WHERE id = GREATEST(1, 2);
COMMIT;
```

### 4.5 锁诊断与监控

#### 查询当前锁

```sql
-- 查看所有锁
SELECT
  locktype,
  relation::regclass AS table_name,
  mode,
  granted,
  pid,
  query
FROM pg_locks l
LEFT JOIN pg_stat_activity a ON l.pid = a.pid
WHERE relation IS NOT NULL
ORDER BY granted, relation;
```

#### 查询锁等待

```sql
-- 查看阻塞关系（谁阻塞了谁）
SELECT
  blocked_locks.pid AS blocked_pid,
  blocked_activity.usename AS blocked_user,
  blocking_locks.pid AS blocking_pid,
  blocking_activity.usename AS blocking_user,
  blocked_activity.query AS blocked_query,
  blocking_activity.query AS blocking_query,
  blocked_activity.application_name AS blocked_app
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
  ON blocking_locks.locktype = blocked_locks.locktype
  AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
  AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
  AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

#### 查询长时间持锁

```sql
SELECT
  pid,
  usename,
  application_name,
  client_addr,
  state,
  query_start,
  now() - query_start AS duration,
  wait_event_type,
  wait_event,
  query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '5 minutes'
ORDER BY query_start;
```

---

## 5. 事务控制语句

```sql
-- 开始事务
BEGIN;
BEGIN TRANSACTION;
START TRANSACTION;

-- 设置隔离级别
BEGIN ISOLATION LEVEL READ COMMITTED;
BEGIN ISOLATION LEVEL REPEATABLE READ;
BEGIN ISOLATION LEVEL SERIALIZABLE;

-- 设置事务特性
BEGIN TRANSACTION READ ONLY;         -- 只读事务
BEGIN TRANSACTION READ WRITE;        -- 读写事务
BEGIN TRANSACTION DEFERRABLE;        -- 可延迟事务（Serializable专用）

-- 保存点（Savepoint）
BEGIN;
INSERT INTO accounts VALUES (1, 1000);
SAVEPOINT sp1;
INSERT INTO accounts VALUES (2, 2000);
SAVEPOINT sp2;
INSERT INTO accounts VALUES (3, 3000);
ROLLBACK TO SAVEPOINT sp2; -- 回滚到sp2，账户3未插入
ROLLBACK TO SAVEPOINT sp1; -- 回滚到sp1，账户2和3未插入
COMMIT; -- 只有账户1被插入

-- 提交与回滚
COMMIT;
COMMIT WORK;
ROLLBACK;
ROLLBACK WORK;

-- 会话级设置
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SET default_transaction_isolation = 'serializable';
```

---

## 6. 长事务管理

### 6.1 长事务的危害

1. **表膨胀**：VACUUM 无法清理长事务期间的旧版本
2. **XID 回卷风险**：占用事务 ID，加速 XID 耗尽
3. **锁等待**：持有锁时间长，阻塞其他事务
4. **复制延迟**：备库需要保留快照，延迟应用 WAL

### 6.2 监控长事务

```sql
-- 查找运行超过5分钟的事务
SELECT
  pid,
  usename,
  application_name,
  client_addr,
  state,
  xact_start,
  now() - xact_start AS xact_duration,
  query_start,
  now() - query_start AS query_duration,
  query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND now() - xact_start > interval '5 minutes'
ORDER BY xact_start;

-- 查找长时间IDLE IN TRANSACTION
SELECT
  pid,
  usename,
  state,
  now() - state_change AS idle_duration,
  query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '10 minutes';
```

### 6.3 长事务处理

```sql
-- 设置语句超时
SET statement_timeout = '5min';

-- 设置事务超时（PostgreSQL 14+）
SET idle_in_transaction_session_timeout = '10min';

-- 终止长事务（谨慎使用）
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE pid = 12345 AND state = 'idle in transaction';
```

### 6.4 长事务最佳实践

1. **分批处理**：大批量操作分多个小事务

   ```sql
   -- ❌ 错误：一次性处理100万行
   BEGIN;
   DELETE FROM logs WHERE created_at < '2024-01-01';
   COMMIT;

   -- ✅ 正确：分批删除
   DO $$
   DECLARE
   deleted_count INT;
   BEGIN
   LOOP
       DELETE FROM logs
       WHERE created_at < '2024-01-01'
       AND ctid IN (SELECT ctid FROM logs WHERE created_at < '2024-01-01' LIMIT 10000);
       GET DIAGNOSTICS deleted_count = ROW_COUNT;
       EXIT WHEN deleted_count = 0;
       COMMIT; -- 每批提交
   END LOOP;
   END $$;
   ```

2. **使用游标**：大结果集使用游标分批获取

   ```sql
   BEGIN;
   DECLARE cur CURSOR FOR SELECT * FROM large_table;
   LOOP
   FETCH 1000 FROM cur;
   -- 处理数据
   EXIT WHEN NOT FOUND;
   END LOOP;
   CLOSE cur;
   COMMIT;
   ```

3. **避免 IDLE IN TRANSACTION**：应用层及时提交/回滚

---

## 7. PostgreSQL 17 并发优化

### 7.1 高并发写入优化

PostgreSQL 17 在 B-tree 索引上进行了优化，提升了高并发 INSERT/UPDATE 性能：

```sql
-- 测试高并发写入性能（对比PG16 vs PG17）
CREATE TABLE test_concurrent_insert (
  id bigserial PRIMARY KEY,
  value text,
  created_at timestamptz DEFAULT now()
);

-- 使用pgbench测试并发插入
-- pgbench -c 100 -j 10 -T 60 -f insert_test.sql
```

### 7.2 VACUUM 内存管理优化

PostgreSQL 17 改进了 VACUUM 的内存使用，减少了长时间 VACUUM 对并发事务的影响：

```sql
-- 查看VACUUM进度（PostgreSQL 13+）
SELECT
  pid,
  datname,
  relid::regclass AS table_name,
  phase,
  heap_blks_total,
  heap_blks_scanned,
  heap_blks_vacuumed,
  index_vacuum_count,
  max_dead_tuples,
  num_dead_tuples
FROM pg_stat_progress_vacuum;

-- PostgreSQL 17 VACUUM参数优化
VACUUM (PARALLEL 4, INDEX_CLEANUP AUTO) table_name;
```

---

## 8. 生产实践与调优

### 8.1 隔离级别选择

| 场景             | 推荐隔离级别        | 理由             |
| ---------------- | ------------------- | ---------------- |
| OLTP（在线交易） | Read Committed      | 高并发，低锁冲突 |
| 报表查询         | Repeatable Read     | 一致性快照       |
| 批量 ETL         | Read Committed      | 避免锁等待       |
| 金融交易         | Serializable        | 严格一致性       |
| 库存扣减         | Serializable + 重试 | 防止超卖         |

### 8.2 锁优化策略

1. **缩短事务时间**：事务内只包含必要操作
2. **避免热点更新**：使用队列或分片
3. **使用 SKIP LOCKED**：任务队列场景
4. **批量操作**：减少事务数量

### 8.3 监控指标

```sql
-- 事务提交/回滚统计
SELECT
  datname,
  xact_commit,
  xact_rollback,
  xact_rollback::float / NULLIF(xact_commit + xact_rollback, 0) AS rollback_ratio
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1');

-- 锁等待统计（需要pg_stat_statements扩展）
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
SELECT
  query,
  calls,
  total_exec_time,
  mean_exec_time,
  blk_read_time + blk_write_time AS io_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 9. 权威参考

### 官方文档

- **MVCC 与并发控制**：<https://www.postgresql.org/docs/17/mvcc.html>
- **事务隔离**：<https://www.postgresql.org/docs/17/transaction-iso.html>
- **显式锁**：<https://www.postgresql.org/docs/17/explicit-locking.html>
- **pg_locks 视图**：<https://www.postgresql.org/docs/17/view-pg-locks.html>
- **pg_stat_activity 视
  图**：<https://www.postgresql.org/docs/17/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW>

### 学术论文

- **Serializable Snapshot Isolation 论文**：<https://drkp.net/papers/ssi-vldb12.pdf>
- **MVCC 原理**：<https://en.wikipedia.org/wiki/Multiversion_concurrency_control>

### 扩展阅读

- **PostgreSQL MVCC 详解（中文）**：<https://www.interdb.jp/pg/pgsql02.html>
- **事务隔离级别可视
  化**：<https://www.postgresql.org/docs/17/transaction-iso.html#XACT-READ-COMMITTED>

---

## 10. Checklist

### 事务设计检查清单

- [ ] 隔离级别已根据业务需求选择（默认 Read Committed）
- [ ] 避免长事务（事务时间<5 分钟）
- [ ] 大批量操作已分批处理（每批<10 秒）
- [ ] 统一锁获取顺序，避免死锁
- [ ] 使用 NOWAIT/SKIP LOCKED 处理锁冲突

### 并发控制检查清单

- [ ] 热点更新已优化（队列/分片/乐观锁）
- [ ] 读多写少场景使用 Repeatable Read
- [ ] Serializable 场景已实现重试逻辑
- [ ] 任务队列使用`FOR UPDATE SKIP LOCKED`

### 监控与诊断检查清单

- [ ] 启用`log_lock_waits = on`（记录锁等待）
- [ ] `deadlock_timeout`合理配置（默认 1s）
- [ ] `idle_in_transaction_session_timeout`已设置（如 10min）
- [ ] 监控长事务（xact_start 超过阈值）
- [ ] 监控死锁频率（pg_stat_database.deadlocks）
- [ ] 定期检查表膨胀（age(relfrozenxid)）

### 性能优化检查清单

- [ ] 只读事务使用`BEGIN TRANSACTION READ ONLY`
- [ ] 报表查询使用 Repeatable Read 获取一致性快照
- [ ] 避免在事务内执行慢查询
- [ ] 使用连接池管理连接（如 pgBouncer）
- [ ] 监控事务回滚率（<5%为健康）

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**下一步**：查看 [03_storage_access](../03_storage_access/README.md) 深入存储与索引
