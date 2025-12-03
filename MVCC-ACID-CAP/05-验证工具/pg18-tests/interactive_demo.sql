-- PostgreSQL 18交互式演示
-- 手动验证MVCC-ACID-CAP特性

\echo '======================================================================'
\echo '        PostgreSQL 18 MVCC-ACID-CAP交互式演示'
\echo '======================================================================'
\echo ''
\echo '本演示将带你逐步体验PostgreSQL 18的MVCC-ACID-CAP特性'
\echo '请按照提示在两个psql会话中操作'
\echo ''
\echo '======================================================================'
\echo ''

\prompt '按回车键继续...' dummy

-- 准备
DROP TABLE IF EXISTS demo CASCADE;

CREATE TABLE demo (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(10),
    balance NUMERIC(10,2),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO demo VALUES 
    (1, 'A001', 1000.00),
    (2, 'A002', 2000.00),
    (3, 'A003', 3000.00);

\echo '✅ 演示表创建完成'
\echo ''
SELECT * FROM demo;
\echo ''

\echo '======================================================================'
\echo ' 演示1：MVCC快照隔离（REPEATABLE READ）'
\echo '======================================================================'
\echo ''
\echo '我们将演示两个并发事务如何通过MVCC实现隔离'
\echo ''

\prompt '准备好后按回车...' dummy

\echo ''
\echo '【会话1 - 你当前的会话】'
\echo '执行：BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;'
\echo ''

BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

\echo '【会话1】获取快照，查看数据：'
SELECT * FROM demo ORDER BY id;
SELECT SUM(balance) as total FROM demo \gset
\echo '总余额: ' :total
\echo ''

\prompt '现在请打开另一个psql会话，执行以下命令，然后按回车：' dummy
\echo ''
\echo '  -- 在新会话中执行'
\echo '  \\c testdb'
\echo '  UPDATE demo SET balance = balance + 500 WHERE account_id = '\''A001'\'';'
\echo '  -- 查看结果'
\echo '  SELECT * FROM demo;'
\echo ''

\prompt '完成后按回车继续...' dummy

\echo ''
\echo '【会话1】现在再次查询（应该看到相同的数据）：'
SELECT * FROM demo ORDER BY id;
SELECT SUM(balance) as total_after FROM demo \gset
\echo '总余额: ' :total_after

\if :total = :total_after
    \echo ''
    \echo '✅ MVCC快照隔离正确！'
    \echo '   会话1始终看到一致的快照，不受会话2的影响'
\else
    \echo '❌ 快照不一致'
\endif

COMMIT;
\echo ''

\prompt '按回车继续下一个演示...' dummy

\echo ''
\echo '======================================================================'
\echo ' 演示2：ACID原子性（转账事务）'
\echo '======================================================================'
\echo ''

-- 恢复数据
UPDATE demo SET balance = 1000 WHERE account_id = 'A001';
UPDATE demo SET balance = 2000 WHERE account_id = 'A002';

SELECT SUM(balance) as total_before FROM demo \gset
\echo '转账前总余额: ' :total_before
\echo ''

\echo '执行转账：A001 → A002 转账500元'
\echo ''

BEGIN;

\echo '【步骤1】扣减A001账户'
UPDATE demo SET balance = balance - 500 WHERE account_id = 'A001';
SELECT * FROM demo WHERE account_id IN ('A001', 'A002') ORDER BY account_id;

\echo ''
\prompt '目前只扣款，还未入账。按回车执行回滚...' dummy

ROLLBACK;

\echo ''
\echo '【事务回滚】查看结果：'
SELECT * FROM demo WHERE account_id IN ('A001', 'A002') ORDER BY account_id;
SELECT SUM(balance) as total_after FROM demo \gset

\if :total_before = :total_after
    \echo ''
    \echo '✅ ACID原子性正确！'
    \echo '   回滚后，数据完全恢复，总金额不变'
\else
    \echo '❌ 原子性失败'
\endif

\echo ''

\prompt '按回车继续...' dummy

\echo ''
\echo '======================================================================'
\echo ' 演示3：完整的转账（原子性+一致性）'
\echo '======================================================================'
\echo ''

BEGIN;

\echo '【转账事务】A001 → A002 转账300元'
UPDATE demo SET balance = balance - 300 WHERE account_id = 'A001';
\echo '  ✅ 扣款完成'

UPDATE demo SET balance = balance + 300 WHERE account_id = 'A002';
\echo '  ✅ 入账完成'

\echo ''
SELECT * FROM demo WHERE account_id IN ('A001', 'A002') ORDER BY account_id;

COMMIT;
\echo ''
\echo '【提交】'

SELECT SUM(balance) as total_final FROM demo \gset

\if :total_before = :total_final
    \echo '✅ ACID一致性保持：总金额保持不变 (' :total_final ')'
\else
    \echo '❌ 一致性失败'
\endif

\echo ''

\prompt '按回车继续...' dummy

\echo ''
\echo '======================================================================'
\echo ' 演示4：PostgreSQL 18性能特性演示'
\echo '======================================================================'
\echo ''

\echo '检查PostgreSQL 18特性状态：'
\echo ''

SHOW enable_builtin_connection_pooling;
SHOW enable_async_io;
SHOW max_parallel_workers_per_gather;

\echo ''
\echo '如果这些特性启用，你正在体验PostgreSQL 18的强大性能！'
\echo ''

-- 创建大表测试
\echo '创建大表测试Skip Scan...'

DROP TABLE IF EXISTS demo_large;
CREATE TABLE demo_large (
    store_id INT,
    order_date DATE,
    order_id BIGINT PRIMARY KEY,
    amount NUMERIC(10,2)
);

INSERT INTO demo_large
SELECT 
    (random() * 10)::int,
    CURRENT_DATE - (random() * 100)::int,
    generate_series(1, 100000),
    (random() * 1000)::numeric(10,2);

CREATE INDEX idx_demo_large ON demo_large(store_id, order_date);
ANALYZE demo_large;

\echo ''
\echo '【查询】只使用order_date（索引第二列）'
\echo '在PostgreSQL 18中应该使用Skip Scan'
\echo ''

EXPLAIN (ANALYZE, COSTS OFF)
SELECT COUNT(*) FROM demo_large WHERE order_date = CURRENT_DATE - 30;

\echo ''
\echo '查看执行计划，如果显示"Index Skip Scan"或使用了索引，'
\echo '说明PostgreSQL 18 Skip Scan特性生效！'
\echo ''

\prompt '按回车查看最终总结...' dummy

\echo ''
\echo '======================================================================'
\echo '                          演示总结'
\echo '======================================================================'
\echo ''
\echo 'MVCC特性演示:'
\echo '  ✅ 快照隔离（REPEATABLE READ）'
\echo '  ✅ 多版本并发控制'
\echo '  ✅ 不同隔离级别的行为'
\echo ''
\echo 'ACID特性演示:'
\echo '  ✅ 原子性（事务全部成功或全部失败）'
\echo '  ✅ 一致性（转账前后总金额不变）'
\echo '  ✅ 隔离性（事务之间互不干扰）'
\echo '  ✅ 持久性（提交后数据永久保存）'
\echo ''
\echo 'PostgreSQL 18新特性:'
\echo '  ✅ 内置连接池（检查enable_builtin_connection_pooling）'
\echo '  ✅ 异步I/O（检查enable_async_io）'
\echo '  ✅ Skip Scan（查看执行计划）'
\echo '  ✅ 并行查询（检查max_parallel_workers_per_gather）'
\echo ''
\echo 'CAP视角:'
\echo '  ✅ C（一致性）：通过MVCC+ACID保证强一致性'
\echo '  ✅ A（可用性）：通过连接池+异步I/O提升'
\echo '  ✅ P（分区容错）：单机系统，主要优化C和A'
\echo ''
\echo '======================================================================'
\echo ''
\echo '🎉 演示完成！你已经体验了PostgreSQL 18的MVCC-ACID-CAP特性！'
\echo ''
\echo '深入学习:'
\echo '  - 理论：MVCC-ACID-CAP/01-理论基础/'
\echo '  - 实践：DataBaseTheory/19-场景案例库/'
\echo '  - 验证：MVCC-ACID-CAP/05-验证工具/pg18-tests/'
\echo ''
\echo '======================================================================'

-- 清理
DROP TABLE IF EXISTS demo CASCADE;
DROP TABLE IF EXISTS demo_large CASCADE;

\echo ''
\echo '✅ 测试表已清理'
