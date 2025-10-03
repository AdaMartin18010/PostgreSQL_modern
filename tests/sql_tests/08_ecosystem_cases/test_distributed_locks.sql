-- TEST: 分布式锁功能测试
-- DESCRIPTION: 测试PostgreSQL Advisory Locks的核心功能
-- EXPECTED: 锁获取、释放、超时等功能正常工作
-- TAGS: advisory-locks, distributed-locks, concurrency

-- SETUP
-- 创建任务调度表
CREATE TABLE test_scheduled_tasks (
    id serial PRIMARY KEY,
    task_name text NOT NULL UNIQUE,
    task_type text NOT NULL,
    is_enabled boolean DEFAULT true,
    last_run_at timestamptz,
    created_at timestamptz DEFAULT now()
);

-- 创建任务执行日志表
CREATE TABLE test_task_execution_log (
    id bigserial PRIMARY KEY,
    task_id int NOT NULL REFERENCES test_scheduled_tasks(id),
    worker_id text NOT NULL,
    status text NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    started_at timestamptz DEFAULT now(),
    completed_at timestamptz,
    lock_id bigint
);

-- 插入测试任务
INSERT INTO test_scheduled_tasks (task_name, task_type) VALUES
    ('test_task_1', 'data_sync'),
    ('test_task_2', 'report_gen'),
    ('test_task_3', 'cleanup');

-- 创建获取任务锁的函数
CREATE OR REPLACE FUNCTION test_try_acquire_task_lock(
    p_task_id int,
    p_worker_id text
)
RETURNS boolean AS $$
DECLARE
    v_lock_id bigint;
    v_acquired boolean;
BEGIN
    v_lock_id := p_task_id;
    v_acquired := pg_try_advisory_lock(v_lock_id);
    
    IF v_acquired THEN
        INSERT INTO test_task_execution_log (task_id, worker_id, status, lock_id)
        VALUES (p_task_id, p_worker_id, 'running', v_lock_id);
        
        UPDATE test_scheduled_tasks
        SET last_run_at = now()
        WHERE id = p_task_id;
    END IF;
    
    RETURN v_acquired;
END;
$$ LANGUAGE plpgsql;

-- 创建释放任务锁的函数
CREATE OR REPLACE FUNCTION test_release_task_lock(
    p_task_id int,
    p_worker_id text,
    p_status text
)
RETURNS void AS $$
DECLARE
    v_lock_id bigint;
BEGIN
    v_lock_id := p_task_id;
    
    UPDATE test_task_execution_log
    SET status = p_status,
        completed_at = now()
    WHERE task_id = p_task_id
      AND worker_id = p_worker_id
      AND status = 'running';
    
    PERFORM pg_advisory_unlock(v_lock_id);
END;
$$ LANGUAGE plpgsql;

-- TEST_BODY
-- 测试1：获取Session级锁（成功）
SELECT pg_try_advisory_lock(12345);  -- EXPECT_VALUE: true

-- 测试2：重复获取同一个锁（应该成功，因为是同一会话）
SELECT pg_try_advisory_lock(12345);  -- EXPECT_VALUE: true

-- 测试3：释放锁
SELECT pg_advisory_unlock(12345);  -- EXPECT_VALUE: true
SELECT pg_advisory_unlock(12345);  -- EXPECT_VALUE: true

-- 测试4：使用任务锁函数获取锁
SELECT test_try_acquire_task_lock(1, 'worker-001');  -- EXPECT_VALUE: true

-- 测试5：验证锁已记录
SELECT COUNT(*) FROM test_task_execution_log
WHERE task_id = 1 AND status = 'running';  -- EXPECT_VALUE: 1

-- 测试6：查看当前持有的Advisory Locks
SELECT COUNT(*) > 0 FROM pg_locks
WHERE locktype = 'advisory' AND objid = 1;  -- EXPECT_VALUE: true

-- 测试7：释放任务锁
SELECT test_release_task_lock(1, 'worker-001', 'completed');

-- 测试8：验证任务状态已更新
SELECT COUNT(*) FROM test_task_execution_log
WHERE task_id = 1 AND status = 'completed';  -- EXPECT_VALUE: 1

-- 测试9：Transaction级锁测试
BEGIN;
SELECT pg_advisory_xact_lock(99999);  -- 获取事务级锁
COMMIT;  -- 锁应该自动释放

-- 验证锁已释放
SELECT COUNT(*) FROM pg_locks
WHERE locktype = 'advisory' AND objid = 99999;  -- EXPECT_VALUE: 0

-- 测试10：多个任务锁测试
SELECT test_try_acquire_task_lock(2, 'worker-002');  -- EXPECT_VALUE: true
SELECT test_try_acquire_task_lock(3, 'worker-003');  -- EXPECT_VALUE: true

-- 验证多个锁同时持有
SELECT COUNT(*) FROM pg_locks
WHERE locktype = 'advisory' 
  AND objid IN (2, 3);  -- EXPECT_VALUE: 2

-- 测试11：释放所有测试锁
SELECT test_release_task_lock(2, 'worker-002', 'completed');
SELECT test_release_task_lock(3, 'worker-003', 'completed');

-- 测试12：验证所有任务都已完成
SELECT COUNT(*) FROM test_task_execution_log
WHERE status = 'completed';  -- EXPECT_VALUE: 3

-- 测试13：共享锁测试
SELECT pg_try_advisory_lock_shared(88888);  -- EXPECT_VALUE: true
SELECT pg_try_advisory_lock_shared(88888);  -- EXPECT_VALUE: true（共享锁可以重复获取）

-- 释放共享锁
SELECT pg_advisory_unlock_shared(88888);  -- EXPECT_VALUE: true
SELECT pg_advisory_unlock_shared(88888);  -- EXPECT_VALUE: true

-- 测试14：使用两个int4参数的锁
SELECT pg_try_advisory_lock(1, 100);  -- EXPECT_VALUE: true
SELECT pg_advisory_unlock(1, 100);  -- EXPECT_VALUE: true

-- TEARDOWN
-- 清理所有Advisory Locks（强制释放）
DO $$
DECLARE
    lock_record record;
BEGIN
    FOR lock_record IN 
        SELECT objid FROM pg_locks 
        WHERE locktype = 'advisory' 
          AND pid = pg_backend_pid()
    LOOP
        BEGIN
            PERFORM pg_advisory_unlock(lock_record.objid);
        EXCEPTION WHEN OTHERS THEN
            -- 忽略错误
        END;
    END LOOP;
END $$;

-- 清理函数
DROP FUNCTION IF EXISTS test_release_task_lock(int, text, text);
DROP FUNCTION IF EXISTS test_try_acquire_task_lock(int, text);

-- 清理表
DROP TABLE IF EXISTS test_task_execution_log;
DROP TABLE IF EXISTS test_scheduled_tasks;

