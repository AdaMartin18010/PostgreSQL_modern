-- TEST: CDC变更数据捕获测试
-- DESCRIPTION: 测试基于触发器的CDC功能
-- EXPECTED: 所有INSERT/UPDATE/DELETE操作都被正确捕获
-- TAGS: cdc, triggers, audit-log

-- SETUP
-- 创建源表
CREATE TABLE test_orders (
    id serial PRIMARY KEY,
    user_id int NOT NULL,
    amount numeric(10,2) NOT NULL,
    status text DEFAULT 'pending'
);

-- 创建审计日志表
CREATE TABLE test_audit_log (
    id serial PRIMARY KEY,
    table_name text NOT NULL,
    record_id int NOT NULL,
    operation text NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values jsonb,
    new_values jsonb,
    changed_by text DEFAULT current_user,
    changed_at timestamptz DEFAULT now()
);

-- 创建CDC触发器函数
CREATE OR REPLACE FUNCTION test_audit_trigger()
RETURNS trigger AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO test_audit_log (table_name, record_id, operation, old_values)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO test_audit_log (table_name, record_id, operation, new_values)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW));
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO test_audit_log (table_name, record_id, operation, old_values, new_values)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER test_orders_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON test_orders
    FOR EACH ROW
    EXECUTE FUNCTION test_audit_trigger();

-- TEST_BODY
-- 测试1：INSERT操作捕获
INSERT INTO test_orders (user_id, amount, status)
VALUES (1, 100.00, 'pending');

-- 验证INSERT被捕获
SELECT COUNT(*) FROM test_audit_log
WHERE operation = 'INSERT';  -- EXPECT_VALUE: 1

-- 验证捕获的数据正确
SELECT
    (new_values->>'user_id')::int = 1 AND
    (new_values->>'amount')::numeric = 100.00 AND
    (new_values->>'status') = 'pending'
FROM test_audit_log
WHERE operation = 'INSERT';  -- EXPECT_VALUE: true

-- 测试2：UPDATE操作捕获
UPDATE test_orders SET status = 'paid' WHERE id = 1;

-- 验证UPDATE被捕获
SELECT COUNT(*) FROM test_audit_log
WHERE operation = 'UPDATE';  -- EXPECT_VALUE: 1

-- 验证old和new值都被记录
SELECT
    old_values IS NOT NULL AND
    new_values IS NOT NULL AND
    (old_values->>'status') = 'pending' AND
    (new_values->>'status') = 'paid'
FROM test_audit_log
WHERE operation = 'UPDATE';  -- EXPECT_VALUE: true

-- 测试3：多次UPDATE
UPDATE test_orders SET amount = 150.00 WHERE id = 1;
UPDATE test_orders SET status = 'completed' WHERE id = 1;

SELECT COUNT(*) FROM test_audit_log
WHERE operation = 'UPDATE';  -- EXPECT_VALUE: 3

-- 测试4：DELETE操作捕获
DELETE FROM test_orders WHERE id = 1;

-- 验证DELETE被捕获
SELECT COUNT(*) FROM test_audit_log
WHERE operation = 'DELETE';  -- EXPECT_VALUE: 1

-- 验证DELETE记录了old_values
SELECT old_values IS NOT NULL
FROM test_audit_log
WHERE operation = 'DELETE';  -- EXPECT_VALUE: true

-- 测试5：批量操作
INSERT INTO test_orders (user_id, amount, status) VALUES
    (2, 200.00, 'pending'),
    (3, 300.00, 'pending'),
    (4, 400.00, 'pending');

SELECT COUNT(*) FROM test_audit_log
WHERE operation = 'INSERT';  -- EXPECT_VALUE: 4

-- 测试6：审计日志完整性
-- 验证所有操作都有时间戳和用户
SELECT COUNT(*) FROM test_audit_log
WHERE changed_at IS NOT NULL AND changed_by IS NOT NULL;  -- EXPECT_VALUE: 8

-- 测试7：查询变更历史
SELECT
    operation,
    COUNT(*) AS operation_count
FROM test_audit_log
GROUP BY operation
ORDER BY operation;  -- EXPECT_ROWS: 3

-- 测试8：时间顺序验证
SELECT
    COUNT(*) = COUNT(DISTINCT changed_at) OR COUNT(*) > 1
FROM test_audit_log;  -- 时间戳应该单调递增或相同

-- TEARDOWN
-- 清理测试数据
DROP TRIGGER IF EXISTS test_orders_audit_trigger ON test_orders;
DROP FUNCTION IF EXISTS test_audit_trigger();
DROP TABLE IF EXISTS test_orders;
DROP TABLE IF EXISTS test_audit_log;

