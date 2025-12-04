-- PostgreSQL 18隔离级别完整演示
-- 交互式验证4种隔离级别的MVCC行为

\echo '======================================================================'
\echo '     PostgreSQL 18隔离级别完整演示（MVCC实现）'
\echo '======================================================================'
\echo ''
\echo '本演示需要两个psql会话同时操作'
\echo '会话1：当前会话（你正在运行的）'
\echo '会话2：请另开一个psql连接到同一数据库'
\echo ''
\echo '======================================================================'

\prompt '按回车开始...' dummy

-- 准备测试数据
DROP TABLE IF EXISTS isolation_demo CASCADE;

CREATE TABLE isolation_demo (
    id INT PRIMARY KEY,
    value INT,
    description TEXT
);

INSERT INTO isolation_demo VALUES
    (1, 100, '账户A'),
    (2, 200, '账户B'),
    (3, 300, '账户C');

\echo ''
\echo '✅ 测试表准备完成'
SELECT * FROM isolation_demo ORDER BY id;
\echo ''

\echo '======================================================================'
\echo ' 演示1：READ UNCOMMITTED（实际是READ COMMITTED）'
\echo '======================================================================'
\echo ''
\echo 'PostgreSQL不支持READ UNCOMMITTED，自动升级为READ COMMITTED'
\echo ''

BEGIN TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

\echo '【会话1】当前隔离级别：'
SHOW transaction_isolation;

\echo ''
\echo '【会话1】第一次查询：'
SELECT * FROM isolation_demo WHERE id = 1;

\echo ''
\echo '>>> 切换到会话2，执行以下命令（不要COMMIT）：'
\echo '    BEGIN;'
\echo '    UPDATE isolation_demo SET value = 150 WHERE id = 1;'
\echo '    -- 暂停，不要COMMIT'
\echo ''

\prompt '完成后按回车...' dummy

\echo ''
\echo '【会话1】第二次查询（会话2的更新未提交）：'
SELECT * FROM isolation_demo WHERE id = 1;

\echo ''
\echo '>>> 现在在会话2执行：'
\echo '    COMMIT;'
\echo ''

\prompt '完成后按回车...' dummy

\echo ''
\echo '【会话1】第三次查询（会话2已提交）：'
SELECT * FROM isolation_demo WHERE id = 1;

COMMIT;

\echo ''
\echo '✅ READ COMMITTED特性：'
\echo '   - 看不到未提交的数据（脏读不可能）'
\echo '   - 能看到其他事务已提交的数据（不可重复读可能）'
\echo ''

\prompt '按回车继续...' dummy

\echo ''
\echo '======================================================================'
\echo ' 演示2：READ COMMITTED - 不可重复读'
\echo '======================================================================'
\echo ''

-- 恢复数据
UPDATE isolation_demo SET value = 100 WHERE id = 1;

BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;

\echo '【会话1-READ COMMITTED】第一次读取：'
SELECT * FROM isolation_demo WHERE id = 1;
SELECT value as v1 FROM isolation_demo WHERE id = 1 \gset

\echo ''
\echo '>>> 在会话2执行：'
\echo '    UPDATE isolation_demo SET value = 999 WHERE id = 1;'
\echo ''

\prompt '完成后按回车...' dummy

\echo ''
\echo '【会话1】第二次读取：'
SELECT * FROM isolation_demo WHERE id = 1;
SELECT value as v2 FROM isolation_demo WHERE id = 1 \gset

COMMIT;

\if :v1 <> :v2
    \echo ''
    \echo '✅ 不可重复读发生：' :v1 ' → ' :v2
    \echo '   READ COMMITTED允许不可重复读'
\endif

\echo ''

\prompt '按回车继续...' dummy

\echo ''
\echo '======================================================================'
\echo ' 演示3：REPEATABLE READ - 快照隔离'
\echo '======================================================================'
\echo ''

-- 恢复
UPDATE isolation_demo SET value = 100 WHERE id = 1;

BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

\echo '【会话1-REPEATABLE READ】获取快照：'
SELECT * FROM isolation_demo ORDER BY id;
SELECT SUM(value) as sum1 FROM isolation_demo \gset
\echo '总和: ' :sum1

\echo ''
\echo '>>> 在会话2执行：'
\echo '    UPDATE isolation_demo SET value = 500 WHERE id = 1;'
\echo '    UPDATE isolation_demo SET value = 600 WHERE id = 2;'
\echo '    INSERT INTO isolation_demo VALUES (4, 400, '\''账户D'\'');'
\echo ''

\prompt '完成后按回车...' dummy

\echo ''
\echo '【会话1】再次查询（应该看到相同的数据）：'
SELECT * FROM isolation_demo ORDER BY id;
SELECT SUM(value) as sum2 FROM isolation_demo \gset
\echo '总和: ' :sum2

COMMIT;

\if :sum1 = :sum2
    \echo ''
    \echo '✅ REPEATABLE READ快照隔离正确！'
    \echo '   整个事务期间看到一致的快照'
    \echo '   MVCC实现：使用事务开始时的snapshot'
\endif

\echo ''

\prompt '按回车继续...' dummy

\echo ''
\echo '======================================================================'
\echo ' 演示4：SERIALIZABLE - 最强隔离'
\echo '======================================================================'
\echo ''

-- 恢复
DELETE FROM isolation_demo WHERE id = 4;
UPDATE isolation_demo SET value = 100 WHERE id = 1;
UPDATE isolation_demo SET value = 200 WHERE id = 2;

\echo '演示：并发事务冲突检测'
\echo ''

BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

\echo '【会话1-SERIALIZABLE】读取账户A：'
SELECT * FROM isolation_demo WHERE id = 1;

\echo ''
\echo '>>> 在会话2执行（也使用SERIALIZABLE）：'
\echo '    BEGIN ISOLATION LEVEL SERIALIZABLE;'
\echo '    UPDATE isolation_demo SET value = 150 WHERE id = 1;'
\echo '    COMMIT;'
\echo ''

\prompt '完成后按回车...' dummy

\echo ''
\echo '【会话1】尝试更新同一行：'
\echo 'UPDATE isolation_demo SET value = 110 WHERE id = 1;'
\echo ''

UPDATE isolation_demo SET value = 110 WHERE id = 1;

\echo ''
\echo '【会话1】尝试提交：'
\echo 'COMMIT;'

\prompt '按回车执行COMMIT（可能失败）...' dummy

COMMIT;

\echo ''
\echo '如果COMMIT失败（serialization failure），说明：'
\echo '✅ SERIALIZABLE检测到冲突'
\echo '   PostgreSQL使用SSI（Serializable Snapshot Isolation）'
\echo '   MVCC+谓词锁实现可串行化'
\echo ''

\echo ''
\echo '======================================================================'
\echo ' 演示5：幻读（Phantom Read）'
\echo '======================================================================'
\echo ''

-- 恢复
TRUNCATE isolation_demo;
INSERT INTO isolation_demo VALUES (1, 100, 'A'), (2, 200, 'B');

\echo '【READ COMMITTED】不能防止幻读：'
\echo ''

BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;

SELECT COUNT(*) as count1 FROM isolation_demo \gset
\echo '第一次COUNT: ' :count1 '行'

\echo ''
\echo '>>> 在会话2执行：'
\echo '    INSERT INTO isolation_demo VALUES (3, 300, '\''C'\'');'
\echo ''

\prompt '完成后按回车...' dummy

SELECT COUNT(*) as count2 FROM isolation_demo \gset
\echo '第二次COUNT: ' :count2 '行'

COMMIT;

\if :count1 <> :count2
    \echo ''
    \echo '✅ 幻读发生：' :count1 ' → ' :count2
    \echo '   READ COMMITTED无法防止幻读'
\endif

\echo ''
\echo '【REPEATABLE READ】可以防止幻读：'
\echo ''

-- 恢复
DELETE FROM isolation_demo WHERE id = 3;

BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

SELECT COUNT(*) as count3 FROM isolation_demo \gset
\echo '第一次COUNT: ' :count3 '行'

\echo ''
\echo '>>> 在会话2执行：'
\echo '    INSERT INTO isolation_demo VALUES (3, 300, '\''C'\'');'
\echo ''

\prompt '完成后按回车...' dummy

SELECT COUNT(*) as count4 FROM isolation_demo \gset
\echo '第二次COUNT: ' :count4 '行'

COMMIT;

\if :count3 = :count4
    \echo ''
    \echo '✅ 幻读被防止：' :count3 ' = ' :count4
    \echo '   REPEATABLE READ的MVCC快照隔离防止幻读'
\endif

\echo ''

\prompt '按回车查看总结...' dummy

\echo ''
\echo '======================================================================'
\echo '                   隔离级别总结（MVCC实现）'
\echo '======================================================================'
\echo ''
\echo '| 隔离级别 | 脏读 | 不可重复读 | 幻读 | MVCC机制 |'
\echo '|----------|------|-----------|------|----------|'
\echo '| READ UNCOMMITTED | ❌ | ✅ | ✅ | 实际是RC |'
\echo '| READ COMMITTED | ❌ | ✅ | ✅ | 每个语句新快照 |'
\echo '| REPEATABLE READ | ❌ | ❌ | ❌ | 事务开始快照 |'
\echo '| SERIALIZABLE | ❌ | ❌ | ❌ | 快照+SSI |'
\echo ''
\echo 'MVCC关键：'
\echo '  - 每个事务有snapshot（xmin, xmax, xip_list）'
\echo '  - 根据snapshot判断版本可见性'
\echo '  - 不同隔离级别=不同的snapshot获取策略'
\echo ''
\echo 'PostgreSQL 18优化：'
\echo '  - 异步I/O加速版本读取'
\echo '  - 并行VACUUM加速版本清理'
\echo '  - 组提交优化事务吞吐'
\echo '  - 所有优化保持MVCC语义不变！'
\echo ''
\echo '======================================================================'

-- 清理
DROP TABLE IF EXISTS isolation_demo CASCADE;

\echo ''
\echo '✅ 演示完成，测试表已清理'
\echo ''
\echo '深入学习：'
\echo '  理论：MVCC-ACID-CAP/01-理论基础/'
\echo '  实践：DataBaseTheory/19-场景案例库/'
\echo ''
