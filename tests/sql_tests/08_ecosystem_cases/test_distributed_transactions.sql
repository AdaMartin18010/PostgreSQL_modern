-- TEST: 分布式事务功能测试
-- DESCRIPTION: 测试两阶段提交（2PC）和分布式事务相关功能
-- EXPECTED: 事务PREPARE、COMMIT PREPARED、ROLLBACK PREPARED功能正常
-- TAGS: distributed-transactions, 2pc, two-phase-commit

-- SETUP
-- 创建测试表
CREATE TABLE test_accounts (
    account_id serial PRIMARY KEY,
    account_name text NOT NULL,
    balance numeric(15,2) NOT NULL CHECK (balance >= 0),
    created_at timestamptz DEFAULT now()
);

CREATE TABLE test_transaction_log (
    log_id bigserial PRIMARY KEY,
    transaction_id text NOT NULL,
    from_account int,
    to_account int,
    amount numeric(15,2) NOT NULL,
    status text NOT NULL CHECK (status IN ('pending', 'committed', 'rolled_back')),
    created_at timestamptz DEFAULT now()
);

-- 插入测试账户
INSERT INTO test_accounts (account_name, balance) VALUES
    ('Account A', 1000.00),
    ('Account B', 2000.00),
    ('Account C', 3000.00);

-- 创建转账函数（使用普通事务）
CREATE OR REPLACE FUNCTION test_transfer_money(
    p_from_account int,
    p_to_account int,
    p_amount numeric
)
RETURNS boolean AS $$
BEGIN
    -- 检查余额
    IF (SELECT balance FROM test_accounts WHERE account_id = p_from_account) < p_amount THEN
        RAISE EXCEPTION 'Insufficient balance';
    END IF;
    
    -- 扣款
    UPDATE test_accounts 
    SET balance = balance - p_amount
    WHERE account_id = p_from_account;
    
    -- 入账
    UPDATE test_accounts 
    SET balance = balance + p_amount
    WHERE account_id = p_to_account;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- TEST_BODY
-- 测试1：验证初始余额
SELECT SUM(balance) FROM test_accounts;  -- EXPECT_VALUE: 6000.00

-- 测试2：普通事务测试（成功提交）
BEGIN;
SELECT test_transfer_money(1, 2, 100.00);
COMMIT;

-- 验证转账成功
SELECT balance FROM test_accounts WHERE account_id = 1;  -- EXPECT_VALUE: 900.00
SELECT balance FROM test_accounts WHERE account_id = 2;  -- EXPECT_VALUE: 2100.00

-- 测试3：普通事务测试（回滚）
BEGIN;
SELECT test_transfer_money(2, 3, 500.00);
ROLLBACK;

-- 验证回滚成功（余额未变）
SELECT balance FROM test_accounts WHERE account_id = 2;  -- EXPECT_VALUE: 2100.00
SELECT balance FROM test_accounts WHERE account_id = 3;  -- EXPECT_VALUE: 3000.00

-- 测试4：准备事务（PREPARE TRANSACTION）
BEGIN;
UPDATE test_accounts SET balance = balance - 200 WHERE account_id = 1;
UPDATE test_accounts SET balance = balance + 200 WHERE account_id = 3;
PREPARE TRANSACTION 'test_txn_001';

-- 验证事务已准备
SELECT COUNT(*) FROM pg_prepared_xacts 
WHERE gid = 'test_txn_001';  -- EXPECT_VALUE: 1

-- 测试5：查看准备事务的详细信息
SELECT 
    gid,
    prepared,
    owner,
    database
FROM pg_prepared_xacts
WHERE gid = 'test_txn_001';  -- EXPECT_ROWS: 1

-- 测试6：提交准备好的事务
COMMIT PREPARED 'test_txn_001';

-- 验证事务已提交
SELECT COUNT(*) FROM pg_prepared_xacts 
WHERE gid = 'test_txn_001';  -- EXPECT_VALUE: 0

-- 验证余额变化
SELECT balance FROM test_accounts WHERE account_id = 1;  -- EXPECT_VALUE: 700.00
SELECT balance FROM test_accounts WHERE account_id = 3;  -- EXPECT_VALUE: 3200.00

-- 测试7：准备并回滚事务
BEGIN;
UPDATE test_accounts SET balance = balance - 100 WHERE account_id = 2;
UPDATE test_accounts SET balance = balance + 100 WHERE account_id = 1;
PREPARE TRANSACTION 'test_txn_002';

-- 验证事务已准备
SELECT COUNT(*) FROM pg_prepared_xacts 
WHERE gid = 'test_txn_002';  -- EXPECT_VALUE: 1

-- 回滚准备好的事务
ROLLBACK PREPARED 'test_txn_002';

-- 验证事务已回滚
SELECT COUNT(*) FROM pg_prepared_xacts 
WHERE gid = 'test_txn_002';  -- EXPECT_VALUE: 0

-- 验证余额未变
SELECT balance FROM test_accounts WHERE account_id = 2;  -- EXPECT_VALUE: 2100.00
SELECT balance FROM test_accounts WHERE account_id = 1;  -- EXPECT_VALUE: 700.00

-- 测试8：记录分布式事务日志
INSERT INTO test_transaction_log (transaction_id, from_account, to_account, amount, status)
VALUES ('txn_003', 1, 2, 50.00, 'pending');

-- 执行转账
BEGIN;
SELECT test_transfer_money(1, 2, 50.00);
UPDATE test_transaction_log SET status = 'committed' WHERE transaction_id = 'txn_003';
COMMIT;

-- 验证日志记录
SELECT status FROM test_transaction_log 
WHERE transaction_id = 'txn_003';  -- EXPECT_VALUE: committed

-- 测试9：验证总余额不变（守恒定律）
SELECT SUM(balance) FROM test_accounts;  -- EXPECT_VALUE: 6000.00

-- 测试10：测试余额检查约束
BEGIN;
DO $$
BEGIN
    UPDATE test_accounts SET balance = -100 WHERE account_id = 1;
    RAISE EXCEPTION 'Should not reach here';
EXCEPTION
    WHEN check_violation THEN
        -- 预期的错误
        NULL;
END $$;
ROLLBACK;

-- 验证约束生效（余额未变为负）
SELECT balance >= 0 FROM test_accounts WHERE account_id = 1;  -- EXPECT_VALUE: true

-- 测试11：并发事务测试（保存点）
BEGIN;
SAVEPOINT sp1;
UPDATE test_accounts SET balance = balance - 10 WHERE account_id = 1;

SAVEPOINT sp2;
UPDATE test_accounts SET balance = balance + 10 WHERE account_id = 2;

-- 回滚到sp2
ROLLBACK TO sp2;

-- 验证sp2之后的更改被回滚
COMMIT;

SELECT balance FROM test_accounts WHERE account_id = 1;  -- EXPECT_VALUE: 640.00
SELECT balance FROM test_accounts WHERE account_id = 2;  -- EXPECT_VALUE: 2100.00

-- 测试12：验证max_prepared_transactions配置
SHOW max_prepared_transactions;  -- 应该返回非0值（如果支持2PC）

-- 测试13：清理所有准备事务（如果有遗留）
DO $$
DECLARE
    xact record;
BEGIN
    FOR xact IN SELECT gid FROM pg_prepared_xacts LOOP
        BEGIN
            EXECUTE 'ROLLBACK PREPARED ' || quote_literal(xact.gid);
        EXCEPTION WHEN OTHERS THEN
            NULL;
        END;
    END LOOP;
END $$;

-- 验证清理成功
SELECT COUNT(*) FROM pg_prepared_xacts;  -- EXPECT_VALUE: 0

-- TEARDOWN
-- 清理函数
DROP FUNCTION IF EXISTS test_transfer_money(int, int, numeric);

-- 清理表
DROP TABLE IF EXISTS test_transaction_log;
DROP TABLE IF EXISTS test_accounts;

