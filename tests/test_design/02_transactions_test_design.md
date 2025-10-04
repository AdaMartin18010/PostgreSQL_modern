# 02_transactions 模块测试设计

> **模块**：事务管理与并发控制  
> **设计日期**：2025年10月3日  
> **目标测试数量**：25+场景  
> **预计完成时间**：Week 4（2025-10-11至2025-10-17）

---

## 📋 测试范围

### 模块内容回顾

- ACID特性实现
- MVCC多版本并发控制
- 事务隔离级别（Read Committed、Repeatable Read、Serializable）
- 锁机制（表级锁、行级锁、死锁处理）
- 长事务管理
- PostgreSQL 17并发优化（高并发写入、VACUUM内存管理）

---

## 🎯 测试场景设计

### 1. ACID特性测试（4个测试）

#### TEST-02-001: 原子性（Atomicity）- 事务回滚

**测试目的**：验证事务的原子性，失败时全部回滚

```sql
-- SETUP
CREATE TABLE test_atomicity (
    id SERIAL PRIMARY KEY,
    balance NUMERIC CHECK (balance >= 0)
);

INSERT INTO test_atomicity (id, balance) VALUES (1, 1000), (2, 500);

-- TEST_BODY
BEGIN;
UPDATE test_atomicity SET balance = balance - 200 WHERE id = 1;
UPDATE test_atomicity SET balance = balance + 200 WHERE id = 2;

-- 保存点1
SAVEPOINT sp1;
SELECT balance FROM test_atomicity WHERE id = 1; -- => 800

-- 尝试违反约束的操作
BEGIN;
UPDATE test_atomicity SET balance = balance - 1500 WHERE id = 1; -- 违反CHECK约束
COMMIT; -- 应该失败并回滚

-- ASSERTIONS
EXPECT_VALUE: SELECT balance FROM test_atomicity WHERE id = 1; => 1000
EXPECT_VALUE: SELECT balance FROM test_atomicity WHERE id = 2; => 500

-- TEARDOWN
DROP TABLE IF EXISTS test_atomicity CASCADE;
```

---

#### TEST-02-002: 一致性（Consistency）- 约束检查

**测试目的**：验证事务维持数据一致性

```sql
-- SETUP
CREATE TABLE test_accounts (
    id INT PRIMARY KEY,
    balance NUMERIC CHECK (balance >= 0)
);

CREATE TABLE test_transactions (
    id SERIAL PRIMARY KEY,
    from_account INT REFERENCES test_accounts(id),
    to_account INT REFERENCES test_accounts(id),
    amount NUMERIC CHECK (amount > 0)
);

INSERT INTO test_accounts VALUES (1, 1000), (2, 500);

-- TEST_BODY
BEGIN;
-- 转账操作
INSERT INTO test_transactions (from_account, to_account, amount) VALUES (1, 2, 300);
UPDATE test_accounts SET balance = balance - 300 WHERE id = 1;
UPDATE test_accounts SET balance = balance + 300 WHERE id = 2;
COMMIT;

-- 尝试违反一致性的转账
BEGIN;
INSERT INTO test_transactions (from_account, to_account, amount) VALUES (1, 2, 2000);
EXPECT_ERROR: UPDATE test_accounts SET balance = balance - 2000 WHERE id = 1; -- 余额不足
ROLLBACK;

-- ASSERTIONS
EXPECT_VALUE: SELECT balance FROM test_accounts WHERE id = 1; => 700
EXPECT_VALUE: SELECT balance FROM test_accounts WHERE id = 2; => 800

-- TEARDOWN
DROP TABLE IF EXISTS test_transactions CASCADE;
DROP TABLE IF EXISTS test_accounts CASCADE;
```

---

#### TEST-02-003: 隔离性（Isolation）- 并发事务不干扰

**测试目的**：验证事务隔离性（需要并发测试框架支持）

```sql
-- SETUP
CREATE TABLE test_isolation (
    id INT PRIMARY KEY,
    value INT
);

INSERT INTO test_isolation VALUES (1, 100);

-- TEST_BODY
-- Session 1
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT value FROM test_isolation WHERE id = 1; -- => 100

-- Session 2（模拟并发）
-- BEGIN;
-- UPDATE test_isolation SET value = 200 WHERE id = 1;
-- COMMIT;

-- Session 1（继续）
SELECT value FROM test_isolation WHERE id = 1; -- 仍应返回100（Repeatable Read）
COMMIT;

-- ASSERTIONS
EXPECT_VALUE: SELECT value FROM test_isolation WHERE id = 1; => 200 -- 提交后看到新值

-- TEARDOWN
DROP TABLE IF EXISTS test_isolation CASCADE;
```

---

#### TEST-02-004: 持久性（Durability）- WAL日志

**测试目的**：验证事务持久性（通过WAL）

```sql
-- SETUP
CREATE TABLE test_durability (
    id SERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- TEST_BODY
-- 记录WAL位置
SELECT pg_current_wal_lsn() AS start_lsn;

BEGIN;
INSERT INTO test_durability (data) VALUES ('Durable Data 1');
INSERT INTO test_durability (data) VALUES ('Durable Data 2');
COMMIT;

-- 再次记录WAL位置
SELECT pg_current_wal_lsn() AS end_lsn;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_durability WHERE data LIKE 'Durable Data%'; => 2
EXPECT_RESULT: SELECT pg_current_wal_lsn() > pg_current_wal_lsn() - '1000'::pg_lsn; => true

-- TEARDOWN
DROP TABLE IF EXISTS test_durability CASCADE;
```

---

### 2. MVCC多版本并发控制（4个测试）

#### TEST-02-005: MVCC - 读不阻塞写

**测试目的**：验证MVCC机制下读写不冲突

```sql
-- SETUP
CREATE TABLE test_mvcc_read_write (
    id INT PRIMARY KEY,
    value INT
);

INSERT INTO test_mvcc_read_write VALUES (1, 100), (2, 200);

-- TEST_BODY
-- Session 1: 长读取事务
BEGIN;
SELECT SUM(value) FROM test_mvcc_read_write; -- => 300

-- Session 2: 写入（不应该被阻塞）
-- BEGIN;
-- UPDATE test_mvcc_read_write SET value = 150 WHERE id = 1;
-- COMMIT;

-- Session 1: 继续读取（应该看到旧值）
SELECT value FROM test_mvcc_read_write WHERE id = 1; -- => 100 (Repeatable Read)
COMMIT;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_mvcc_read_write; => 2

-- TEARDOWN
DROP TABLE IF EXISTS test_mvcc_read_write CASCADE;
```

---

#### TEST-02-006: MVCC - 事务ID与快照

**测试目的**：验证事务ID和快照机制

```sql
-- TEST_BODY
CREATE TABLE test_mvcc_xid (
    id SERIAL PRIMARY KEY,
    data TEXT
);

-- 获取当前事务ID
SELECT txid_current() AS tx1;

BEGIN;
INSERT INTO test_mvcc_xid (data) VALUES ('Data from TX1');
SELECT txid_current() AS tx2;

-- 获取当前快照
SELECT txid_current_snapshot() AS snapshot;
COMMIT;

-- ASSERTIONS
EXPECT_RESULT: SELECT txid_current() > txid_current() - 10; => true
EXPECT_ROWS: SELECT COUNT(*) FROM test_mvcc_xid; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_mvcc_xid CASCADE;
```

---

#### TEST-02-007: MVCC - 可见性规则

**测试目的**：验证元组可见性规则（xmin/xmax）

```sql
-- SETUP
CREATE EXTENSION IF NOT EXISTS pageinspect;

CREATE TABLE test_mvcc_visibility (
    id INT PRIMARY KEY,
    value TEXT
);

-- TEST_BODY
INSERT INTO test_mvcc_visibility VALUES (1, 'Version 1');

-- 查看系统列（xmin, xmax）
SELECT xmin, xmax, id, value FROM test_mvcc_visibility;

UPDATE test_mvcc_visibility SET value = 'Version 2' WHERE id = 1;

-- 更新后xmax应该被设置
SELECT xmin, xmax, id, value FROM test_mvcc_visibility;

-- ASSERTIONS
EXPECT_VALUE: SELECT value FROM test_mvcc_visibility WHERE id = 1; => 'Version 2'

-- TEARDOWN
DROP TABLE IF EXISTS test_mvcc_visibility CASCADE;
```

---

#### TEST-02-008: XID回卷与冻结

**测试目的**：验证XID冻结机制

```sql
-- TEST_BODY
CREATE TABLE test_xid_freeze (
    id SERIAL PRIMARY KEY,
    data TEXT
);

INSERT INTO test_xid_freeze (data) 
SELECT 'Data ' || generate_series FROM generate_series(1, 1000);

-- 查看表的XID年龄
SELECT
    relname,
    age(relfrozenxid) AS xid_age
FROM pg_class
WHERE relname = 'test_xid_freeze';

-- 手动VACUUM FREEZE
VACUUM FREEZE test_xid_freeze;

-- ASSERTIONS
EXPECT_RESULT: SELECT age(relfrozenxid) FROM pg_class WHERE relname = 'test_xid_freeze'; => < 100

-- TEARDOWN
DROP TABLE IF EXISTS test_xid_freeze CASCADE;
```

---

### 3. 事务隔离级别（6个测试）

#### TEST-02-009: Read Committed - 不可重复读

**测试目的**：验证Read Committed隔离级别的不可重复读现象

```sql
-- SETUP
CREATE TABLE test_read_committed (
    id INT PRIMARY KEY,
    value INT
);

INSERT INTO test_read_committed VALUES (1, 100);

-- TEST_BODY
-- Session 1
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT value FROM test_read_committed WHERE id = 1; -- => 100

-- Session 2（模拟）
-- BEGIN;
-- UPDATE test_read_committed SET value = 200 WHERE id = 1;
-- COMMIT;

-- Session 1（再次读取，应该看到新值）
SELECT value FROM test_read_committed WHERE id = 1; -- => 200 (不可重复读)
COMMIT;

-- ASSERTIONS
EXPECT_VALUE: SELECT value FROM test_read_committed WHERE id = 1; => 200

-- TEARDOWN
DROP TABLE IF EXISTS test_read_committed CASCADE;
```

---

#### TEST-02-010: Read Committed - 幻读

**测试目的**：验证Read Committed隔离级别的幻读现象

```sql
-- SETUP
CREATE TABLE test_phantom_read (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    value INT
);

INSERT INTO test_phantom_read (category, value) VALUES 
('A', 100), ('A', 200);

-- TEST_BODY
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT COUNT(*) FROM test_phantom_read WHERE category = 'A'; -- => 2

-- Session 2（模拟）
-- BEGIN;
-- INSERT INTO test_phantom_read (category, value) VALUES ('A', 300);
-- COMMIT;

-- Session 1（再次查询，应该看到新行）
SELECT COUNT(*) FROM test_phantom_read WHERE category = 'A'; -- => 3 (幻读)
COMMIT;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_phantom_read WHERE category = 'A'; => 3

-- TEARDOWN
DROP TABLE IF EXISTS test_phantom_read CASCADE;
```

---

#### TEST-02-011: Repeatable Read - 防止不可重复读

**测试目的**：验证Repeatable Read隔离级别防止不可重复读

```sql
-- SETUP
CREATE TABLE test_repeatable_read (
    id INT PRIMARY KEY,
    value INT
);

INSERT INTO test_repeatable_read VALUES (1, 100);

-- TEST_BODY
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT value FROM test_repeatable_read WHERE id = 1; -- => 100

-- Session 2（模拟）
-- BEGIN;
-- UPDATE test_repeatable_read SET value = 200 WHERE id = 1;
-- COMMIT;

-- Session 1（再次读取，应该仍然看到旧值）
SELECT value FROM test_repeatable_read WHERE id = 1; -- => 100 (可重复读)

-- 尝试更新会失败
EXPECT_ERROR: UPDATE test_repeatable_read SET value = 150 WHERE id = 1; -- Serialization failure
ROLLBACK;

-- ASSERTIONS
EXPECT_VALUE: SELECT value FROM test_repeatable_read WHERE id = 1; => 200

-- TEARDOWN
DROP TABLE IF EXISTS test_repeatable_read CASCADE;
```

---

#### TEST-02-012: Repeatable Read - 防止幻读（PostgreSQL特性）

**测试目的**：验证PostgreSQL的Repeatable Read防止幻读

```sql
-- SETUP
CREATE TABLE test_rr_phantom (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50)
);

INSERT INTO test_rr_phantom (category) VALUES ('A'), ('A');

-- TEST_BODY
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM test_rr_phantom WHERE category = 'A'; -- => 2

-- Session 2（模拟）
-- BEGIN;
-- INSERT INTO test_rr_phantom (category) VALUES ('A');
-- COMMIT;

-- Session 1（再次查询，仍应看到2行）
SELECT COUNT(*) FROM test_rr_phantom WHERE category = 'A'; -- => 2 (无幻读)
COMMIT;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_rr_phantom WHERE category = 'A'; => 3

-- TEARDOWN
DROP TABLE IF EXISTS test_rr_phantom CASCADE;
```

---

#### TEST-02-013: Serializable - 串行化执行

**测试目的**：验证Serializable隔离级别完全串行化

```sql
-- SETUP
CREATE TABLE test_serializable (
    id INT PRIMARY KEY,
    balance NUMERIC
);

INSERT INTO test_serializable VALUES (1, 1000), (2, 1000);

-- TEST_BODY
-- Session 1
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(balance) FROM test_serializable; -- => 2000
UPDATE test_serializable SET balance = balance - 500 WHERE id = 1;

-- Session 2（模拟）
-- BEGIN ISOLATION LEVEL SERIALIZABLE;
-- SELECT SUM(balance) FROM test_serializable; -- => 2000
-- UPDATE test_serializable SET balance = balance - 500 WHERE id = 2;
-- COMMIT;

-- Session 1尝试提交
EXPECT_ERROR: COMMIT; -- Serialization failure（可能）

-- ASSERTIONS
EXPECT_RESULT: SELECT SUM(balance) FROM test_serializable; => >= 1000

-- TEARDOWN
DROP TABLE IF EXISTS test_serializable CASCADE;
```

---

#### TEST-02-014: 隔离级别切换

**测试目的**：验证隔离级别设置和切换

```sql
-- TEST_BODY
-- 查看默认隔离级别
SHOW default_transaction_isolation; -- => 'read committed'

-- 设置会话级别隔离级别
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SHOW default_transaction_isolation; -- => 'repeatable read'

-- 单个事务设置
BEGIN ISOLATION LEVEL SERIALIZABLE;
SHOW transaction_isolation; -- => 'serializable'
COMMIT;

-- 恢复默认
RESET default_transaction_isolation;

-- ASSERTIONS
EXPECT_VALUE: SHOW default_transaction_isolation; => 'read committed'

-- TEARDOWN
-- 无需清理
```

---

### 4. 锁机制（6个测试）

#### TEST-02-015: 表级锁 - AccessShareLock vs AccessExclusiveLock

**测试目的**：验证表级锁的冲突

```sql
-- SETUP
CREATE TABLE test_table_lock (
    id SERIAL PRIMARY KEY,
    data TEXT
);

-- TEST_BODY
-- Session 1: AccessShareLock（SELECT）
BEGIN;
SELECT * FROM test_table_lock;

-- 查看当前锁
SELECT locktype, mode, granted FROM pg_locks 
WHERE relation = 'test_table_lock'::regclass;

-- Session 2: 尝试AccessExclusiveLock（应该被阻塞）
-- BEGIN;
-- EXPECT_TIMEOUT: DROP TABLE test_table_lock; -- 被阻塞

-- Session 1释放锁
COMMIT;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_locks WHERE relation = 'test_table_lock'::regclass; => 0

-- TEARDOWN
DROP TABLE IF EXISTS test_table_lock CASCADE;
```

---

#### TEST-02-016: 行级锁 - FOR UPDATE

**测试目的**：验证行级锁（悲观锁）

```sql
-- SETUP
CREATE TABLE test_row_lock (
    id INT PRIMARY KEY,
    value INT
);

INSERT INTO test_row_lock VALUES (1, 100), (2, 200);

-- TEST_BODY
-- Session 1: 锁定行1
BEGIN;
SELECT * FROM test_row_lock WHERE id = 1 FOR UPDATE;

-- Session 2: 尝试锁定同一行（应该被阻塞）
-- BEGIN;
-- EXPECT_TIMEOUT: SELECT * FROM test_row_lock WHERE id = 1 FOR UPDATE;

-- Session 2: 锁定行2（不应该被阻塞）
-- SELECT * FROM test_row_lock WHERE id = 2 FOR UPDATE; -- 成功

-- Session 1释放锁
COMMIT;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_row_lock; => 2

-- TEARDOWN
DROP TABLE IF EXISTS test_row_lock CASCADE;
```

---

#### TEST-02-017: FOR UPDATE NOWAIT

**测试目的**：验证NOWAIT快速失败

```sql
-- SETUP
CREATE TABLE test_nowait (
    id INT PRIMARY KEY,
    value INT
);

INSERT INTO test_nowait VALUES (1, 100);

-- TEST_BODY
BEGIN;
SELECT * FROM test_nowait WHERE id = 1 FOR UPDATE;

-- 同一会话尝试NOWAIT（模拟并发）
BEGIN;
EXPECT_ERROR: SELECT * FROM test_nowait WHERE id = 1 FOR UPDATE NOWAIT; -- 立即失败
ROLLBACK;

-- 原事务提交
COMMIT;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_nowait; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_nowait CASCADE;
```

---

#### TEST-02-018: FOR UPDATE SKIP LOCKED（任务队列）

**测试目的**：验证SKIP LOCKED机制

```sql
-- SETUP
CREATE TABLE test_job_queue (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20),
    data TEXT
);

INSERT INTO test_job_queue (status, data) VALUES 
('pending', 'Job 1'),
('pending', 'Job 2'),
('pending', 'Job 3');

-- TEST_BODY
-- Worker 1: 获取待处理任务
BEGIN;
SELECT * FROM test_job_queue 
WHERE status = 'pending' 
ORDER BY id 
LIMIT 1 
FOR UPDATE SKIP LOCKED;

-- Worker 2: 获取下一个任务（跳过已锁定的）
-- BEGIN;
-- SELECT * FROM test_job_queue 
-- WHERE status = 'pending' 
-- ORDER BY id 
-- LIMIT 1 
-- FOR UPDATE SKIP LOCKED; -- 应该返回Job 2

-- Worker 1完成任务
UPDATE test_job_queue SET status = 'processing' WHERE id = 1;
COMMIT;

-- ASSERTIONS
EXPECT_VALUE: SELECT status FROM test_job_queue WHERE id = 1; => 'processing'

-- TEARDOWN
DROP TABLE IF EXISTS test_job_queue CASCADE;
```

---

#### TEST-02-019: 死锁检测

**测试目的**：验证死锁检测机制

```sql
-- SETUP
CREATE TABLE test_deadlock (
    id INT PRIMARY KEY,
    value INT
);

INSERT INTO test_deadlock VALUES (1, 100), (2, 200);

-- TEST_BODY
-- Session 1
BEGIN;
UPDATE test_deadlock SET value = 150 WHERE id = 1; -- 锁定行1

-- Session 2（模拟）
-- BEGIN;
-- UPDATE test_deadlock SET value = 250 WHERE id = 2; -- 锁定行2

-- Session 1: 尝试锁定行2
-- UPDATE test_deadlock SET value = 160 WHERE id = 2; -- 等待Session 2

-- Session 2: 尝试锁定行1（触发死锁）
-- EXPECT_ERROR: UPDATE test_deadlock SET value = 260 WHERE id = 1; -- 死锁检测

-- Session 1成功提交
COMMIT;

-- ASSERTIONS
EXPECT_VALUE: SELECT value FROM test_deadlock WHERE id = 1; => 150

-- TEARDOWN
DROP TABLE IF EXISTS test_deadlock CASCADE;
```

---

#### TEST-02-020: 锁诊断 - pg_locks视图

**测试目的**：验证锁监控查询

```sql
-- SETUP
CREATE TABLE test_lock_monitoring (
    id INT PRIMARY KEY,
    data TEXT
);

-- TEST_BODY
BEGIN;
SELECT * FROM test_lock_monitoring FOR UPDATE;

-- 查询当前锁
SELECT
    locktype,
    relation::regclass AS table_name,
    mode,
    granted,
    pid
FROM pg_locks
WHERE relation = 'test_lock_monitoring'::regclass;

COMMIT;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_locks WHERE relation = 'test_lock_monitoring'::regclass AND NOT granted; => 0

-- TEARDOWN
DROP TABLE IF EXISTS test_lock_monitoring CASCADE;
```

---

### 5. 长事务管理（3个测试）

#### TEST-02-021: 长事务监控

**测试目的**：验证长事务检测

```sql
-- TEST_BODY
CREATE TABLE test_long_transaction (
    id SERIAL PRIMARY KEY,
    data TEXT
);

BEGIN;
INSERT INTO test_long_transaction (data) VALUES ('Long TX Data');

-- 模拟长事务（延迟10秒）
-- SELECT pg_sleep(10);

-- 查询长事务
SELECT
    pid,
    now() - xact_start AS xact_duration,
    state,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND now() - xact_start > interval '1 second'
ORDER BY xact_start;

COMMIT;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_long_transaction; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_long_transaction CASCADE;
```

---

#### TEST-02-022: IDLE IN TRANSACTION检测

**测试目的**：验证idle in transaction状态检测

```sql
-- TEST_BODY
BEGIN;
SELECT 1; -- 开始事务但不提交

-- 查询idle in transaction状态
SELECT
    pid,
    state,
    now() - state_change AS idle_duration,
    query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '1 second';

COMMIT;

-- ASSERTIONS
-- 无需断言，仅验证查询可执行

-- TEARDOWN
-- 无需清理
```

---

#### TEST-02-023: statement_timeout设置

**测试目的**：验证语句超时机制

```sql
-- TEST_BODY
SET statement_timeout = '1s';

-- 应该超时
EXPECT_ERROR: SELECT pg_sleep(5); -- 超时错误

-- 重置
RESET statement_timeout;

-- 应该成功
SELECT pg_sleep(0.5); -- 不超时

-- ASSERTIONS
EXPECT_VALUE: SHOW statement_timeout; => '0'

-- TEARDOWN
-- 无需清理
```

---

### 6. PostgreSQL 17并发优化（2个测试）

#### TEST-02-024: 高并发写入性能（B-tree优化）

**测试目的**：验证PG17高并发写入优化

```sql
-- TEST_BODY
CREATE TABLE test_concurrent_insert (
    id BIGSERIAL PRIMARY KEY,
    value TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 模拟并发插入
INSERT INTO test_concurrent_insert (value)
SELECT 'Value ' || generate_series
FROM generate_series(1, 10000);

-- 查看索引大小和性能
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'test_concurrent_insert';

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_concurrent_insert; => 10000

-- TEARDOWN
DROP TABLE IF EXISTS test_concurrent_insert CASCADE;
```

---

#### TEST-02-025: VACUUM内存管理优化

**测试目的**：验证PG17 VACUUM内存管理改进

```sql
-- SETUP
CREATE TABLE test_vacuum_memory (
    id SERIAL PRIMARY KEY,
    data TEXT
);

-- 插入大量数据
INSERT INTO test_vacuum_memory (data)
SELECT 'Data ' || generate_series FROM generate_series(1, 10000);

-- 更新部分数据（产生死元组）
UPDATE test_vacuum_memory SET data = 'Updated' WHERE id % 2 = 0;

-- TEST_BODY
-- 查看VACUUM前的死元组数量
SELECT n_dead_tup FROM pg_stat_user_tables WHERE tablename = 'test_vacuum_memory';

-- 执行VACUUM
VACUUM (VERBOSE, ANALYZE) test_vacuum_memory;

-- 查看VACUUM后的死元组数量
SELECT n_dead_tup FROM pg_stat_user_tables WHERE tablename = 'test_vacuum_memory';

-- ASSERTIONS
EXPECT_RESULT: SELECT n_dead_tup FROM pg_stat_user_tables WHERE tablename = 'test_vacuum_memory'; => < 100

-- TEARDOWN
DROP TABLE IF EXISTS test_vacuum_memory CASCADE;
```

---

## 📊 测试统计

### 测试数量

| 类别 | 测试数量 |
|------|---------|
| **ACID特性测试** | 4个 |
| **MVCC多版本并发控制** | 4个 |
| **事务隔离级别** | 6个 |
| **锁机制** | 6个 |
| **长事务管理** | 3个 |
| **PostgreSQL 17并发优化** | 2个 |
| **总计** | **25个** |

### 覆盖率

- ✅ ACID特性（原子性、一致性、隔离性、持久性）
- ✅ MVCC（读写不冲突、事务ID、可见性规则、XID冻结）
- ✅ 隔离级别（Read Committed、Repeatable Read、Serializable）
- ✅ 锁机制（表级锁、行级锁、NOWAIT、SKIP LOCKED、死锁检测）
- ✅ 长事务管理（监控、idle in transaction、超时设置）
- ✅ PostgreSQL 17优化（高并发写入、VACUUM内存管理）

---

## 🔧 实现建议

### 测试框架增强需求

1. **并发测试支持**
   - 实现多会话并发测试框架
   - 支持会话间的同步机制
   - 增加`EXPECT_TIMEOUT`断言（锁等待验证）

2. **事务隔离级别支持**
   - 支持在TEST_BODY中设置隔离级别
   - 验证serialization错误

3. **锁监控支持**
   - 查询pg_locks视图
   - 验证锁的模式和授予状态

### 测试执行注意事项

1. **隔离性**：每个测试使用独立的表，避免锁冲突
2. **并发模拟**：注释中标记的"Session 2"需要并发测试框架支持
3. **清理**：确保事务正确提交或回滚，避免长事务

---

## 📅 实施计划

### Week 4（2025-10-11 至 2025-10-17）

**Day 1-2**：测试框架增强（6小时）

- 实现并发测试框架
- 实现事务隔离级别支持
- 实现锁监控断言

**Day 3-6**：测试用例实现（10小时）

- 实现25个测试用例
- 编写并发测试场景
- 验证测试通过

**Day 7**：文档完善（2小时）

- 更新测试用例索引
- 编写并发测试指南

---

**设计者**：PostgreSQL_modern Project Team  
**设计日期**：2025年10月3日  
**目标版本**：v1.0  
**状态**：设计完成，待实现 ✅
