-- PostgreSQL MVCC可见性测试脚本
-- 测试不同隔离级别下的可见性行为
-- 版本: PostgreSQL 17 & 18

-- ============================================
-- 测试1: READ COMMITTED 隔离级别可见性测试
-- ============================================

-- 会话1: 插入数据
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
INSERT INTO test_table (id, value) VALUES (1, 'initial');
-- 不提交，测试未提交数据的可见性

-- 会话2: 读取数据（应该看不到未提交的数据）
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT * FROM test_table WHERE id = 1;
-- 预期结果: 0 rows（脏读被防止）

-- 会话1: 提交
COMMIT;

-- 会话2: 再次读取（应该看到已提交的数据）
SELECT * FROM test_table WHERE id = 1;
-- 预期结果: 1 row, value = 'initial'

-- 会话1: 更新数据
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
UPDATE test_table SET value = 'updated' WHERE id = 1;
-- 不提交

-- 会话2: 读取数据（应该看到旧值）
SELECT * FROM test_table WHERE id = 1;
-- 预期结果: value = 'initial'（语句级快照）

-- 会话1: 提交
COMMIT;

-- 会话2: 再次读取（应该看到新值）
SELECT * FROM test_table WHERE id = 1;
-- 预期结果: value = 'updated'（READ COMMITTED允许不可重复读）

-- ============================================
-- 测试2: REPEATABLE READ 隔离级别可见性测试
-- ============================================

-- 会话1: 插入数据
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
INSERT INTO test_table (id, value) VALUES (2, 'initial');
COMMIT;

-- 会话2: 开始事务
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM test_table WHERE id = 2;
-- 预期结果: value = 'initial'

-- 会话1: 更新数据
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
UPDATE test_table SET value = 'updated' WHERE id = 2;
COMMIT;

-- 会话2: 再次读取（应该看到旧值）
SELECT * FROM test_table WHERE id = 2;
-- 预期结果: value = 'initial'（事务级快照，防止不可重复读）

-- 会话2: 提交
COMMIT;

-- 会话2: 新事务读取（应该看到新值）
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM test_table WHERE id = 2;
-- 预期结果: value = 'updated'

-- ============================================
-- 测试3: SERIALIZABLE 隔离级别可见性测试
-- ============================================

-- 会话1: 开始事务
BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT * FROM test_table WHERE id = 1;
SELECT * FROM test_table WHERE id = 2;
-- 记录SIREAD锁

-- 会话2: 开始事务
BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT * FROM test_table WHERE id = 1;
SELECT * FROM test_table WHERE id = 2;
-- 记录SIREAD锁

-- 会话1: 更新数据
UPDATE test_table SET value = 'serial1' WHERE id = 1;
COMMIT;

-- 会话2: 更新数据（可能触发冲突检测）
UPDATE test_table SET value = 'serial2' WHERE id = 2;
COMMIT;
-- 可能结果: ERROR: could not serialize access（如果检测到冲突）

-- ============================================
-- 测试4: 幻读测试（REPEATABLE READ）
-- ============================================

-- 会话1: 开始事务
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM test_table WHERE value = 'phantom';
-- 预期结果: 0

-- 会话2: 插入数据
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
INSERT INTO test_table (id, value) VALUES (3, 'phantom');
COMMIT;

-- 会话1: 再次查询（应该看不到新数据）
SELECT COUNT(*) FROM test_table WHERE value = 'phantom';
-- 预期结果: 0（REPEATABLE READ防止幻读）

-- 会话1: 提交
COMMIT;

-- ============================================
-- 测试5: 写偏序异常测试
-- ============================================

-- 创建测试表
CREATE TABLE IF NOT EXISTS accounts (
    id INT PRIMARY KEY,
    balance INT CHECK (balance >= 0)
);

INSERT INTO accounts (id, balance) VALUES (1, 100), (2, 100);

-- 会话1: 开始事务
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1;
SELECT balance FROM accounts WHERE id = 2;
-- 预期结果: 100, 100

-- 会话2: 开始事务（并发）
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1;
SELECT balance FROM accounts WHERE id = 2;
-- 预期结果: 100, 100

-- 会话1: 更新账户1
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
-- 预期结果: 成功（满足约束：0 + 100 >= 0）

-- 会话2: 更新账户2
UPDATE accounts SET balance = balance - 100 WHERE id = 2;
COMMIT;
-- REPEATABLE READ: 成功（写偏序异常）
-- SERIALIZABLE: ERROR（SSI检测到冲突）

-- ============================================
-- 测试6: 版本链可见性测试
-- ============================================

-- 创建测试表
CREATE TABLE IF NOT EXISTS version_test (
    id INT PRIMARY KEY,
    value TEXT
);

-- 插入初始数据
INSERT INTO version_test (id, value) VALUES (1, 'v1');
COMMIT;

-- 会话1: 更新数据（创建版本链）
BEGIN;
UPDATE version_test SET value = 'v2' WHERE id = 1;
COMMIT;

-- 会话2: 开始事务（在v2提交之前）
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT value FROM version_test WHERE id = 1;
-- 预期结果: 'v1'（基于快照）

-- 会话1: 再次更新
BEGIN;
UPDATE version_test SET value = 'v3' WHERE id = 1;
COMMIT;

-- 会话2: 查询（应该仍然看到v1）
SELECT value FROM version_test WHERE id = 1;
-- 预期结果: 'v1'（事务级快照）

-- 会话2: 提交
COMMIT;

-- 会话2: 新事务查询（应该看到v3）
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT value FROM version_test WHERE id = 1;
-- 预期结果: 'v3'

-- ============================================
-- 测试7: HOT更新可见性测试
-- ============================================

-- 创建测试表（设置fillfactor）
CREATE TABLE IF NOT EXISTS hot_test (
    id INT PRIMARY KEY,
    status VARCHAR(20)
) WITH (fillfactor = 80);

INSERT INTO hot_test (id, status) VALUES (1, 'initial');

-- 会话1: HOT更新（不更新索引列）
BEGIN;
UPDATE hot_test SET status = 'updated' WHERE id = 1;
COMMIT;
-- 预期: HOT更新，版本链不增长

-- 会话2: 查询（应该看到新值）
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT status FROM hot_test WHERE id = 1;
-- 预期结果: 'updated'

-- ============================================
-- 测试8: 子事务可见性测试
-- ============================================

-- 会话1: 开始事务
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM test_table WHERE id = 1;

-- 创建保存点
SAVEPOINT sp1;
UPDATE test_table SET value = 'savepoint' WHERE id = 1;
SELECT * FROM test_table WHERE id = 1;
-- 预期结果: value = 'savepoint'

-- 回滚到保存点
ROLLBACK TO SAVEPOINT sp1;
SELECT * FROM test_table WHERE id = 1;
-- 预期结果: value = 'initial'（回滚后）

-- 提交
COMMIT;

-- ============================================
-- 测试9: 并发更新冲突测试
-- ============================================

-- 会话1: 开始事务
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
UPDATE test_table SET value = 'session1' WHERE id = 1;
-- 不提交

-- 会话2: 尝试更新同一行
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
UPDATE test_table SET value = 'session2' WHERE id = 1;
-- 预期: 等待会话1提交或超时

-- 会话1: 提交
COMMIT;

-- 会话2: 更新成功
COMMIT;

-- ============================================
-- 测试10: 长事务可见性测试
-- ============================================

-- 会话1: 开始长事务
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM test_table;
-- 记录快照

-- 等待一段时间（模拟长事务）
-- SELECT pg_sleep(10);

-- 会话2: 在此期间更新数据
BEGIN;
UPDATE test_table SET value = 'long_transaction' WHERE id = 1;
COMMIT;

-- 会话1: 再次查询（应该看不到更新）
SELECT * FROM test_table WHERE id = 1;
-- 预期结果: 旧值（长事务快照）

-- 会话1: 提交
COMMIT;

-- ============================================
-- 清理测试数据
-- ============================================

-- DROP TABLE IF EXISTS test_table;
-- DROP TABLE IF EXISTS accounts;
-- DROP TABLE IF EXISTS version_test;
-- DROP TABLE IF EXISTS hot_test;
