-- TEST: 流式复制监控功能测试
-- DESCRIPTION: 测试流式复制的监控和健康检查功能
-- EXPECTED: 复制相关的系统视图和函数正常工作
-- TAGS: streaming-replication, monitoring, high-availability
-- NOTE: 此测试主要验证监控功能，不测试实际的复制配置

-- SETUP
-- 创建测试表用于监控复制延迟
CREATE TABLE test_replication_monitor (
    id serial PRIMARY KEY,
    check_time timestamptz DEFAULT now(),
    message text
);

-- 创建复制监控函数
CREATE OR REPLACE FUNCTION test_check_replication_status()
RETURNS TABLE (
    is_primary boolean,
    is_in_recovery boolean,
    current_wal_lsn text,
    has_replication_slots boolean
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        NOT pg_is_in_recovery() AS is_primary,
        pg_is_in_recovery() AS is_in_recovery,
        pg_current_wal_lsn()::text AS current_wal_lsn,
        EXISTS(SELECT 1 FROM pg_replication_slots) AS has_replication_slots;
END;
$$ LANGUAGE plpgsql;

-- 创建WAL位置比较函数
CREATE OR REPLACE FUNCTION test_wal_lsn_diff_bytes(lsn1 text, lsn2 text)
RETURNS bigint AS $$
BEGIN
    RETURN pg_wal_lsn_diff(lsn1::pg_lsn, lsn2::pg_lsn);
END;
$$ LANGUAGE plpgsql;

-- TEST_BODY
-- 测试1：检查是否为Primary节点
SELECT pg_is_in_recovery();  -- 应该返回 boolean 值

-- 测试2：获取当前WAL LSN
SELECT pg_current_wal_lsn() IS NOT NULL;  -- EXPECT_VALUE: true

-- 测试3：获取最后接收的WAL LSN（如果是Standby）
-- 如果是Primary，这个函数会返回NULL
SELECT pg_last_wal_receive_lsn() IS NOT NULL OR NOT pg_is_in_recovery();  -- EXPECT_VALUE: true

-- 测试4：获取最后回放的WAL LSN（如果是Standby）
SELECT pg_last_wal_replay_lsn() IS NOT NULL OR NOT pg_is_in_recovery();  -- EXPECT_VALUE: true

-- 测试5：检查复制相关系统视图存在
SELECT COUNT(*) FROM information_schema.tables
WHERE table_name IN ('pg_stat_replication', 'pg_replication_slots');  -- EXPECT_VALUE: 2

-- 测试6：查询复制连接状态（可能为空，如果没有Standby）
SELECT COUNT(*) >= 0 FROM pg_stat_replication;  -- EXPECT_VALUE: true

-- 测试7：查询复制槽（可能为空）
SELECT COUNT(*) >= 0 FROM pg_replication_slots;  -- EXPECT_VALUE: true

-- 测试8：使用监控函数
SELECT * FROM test_check_replication_status();  -- EXPECT_ROWS: 1

-- 测试9：WAL段文件相关函数
SELECT pg_walfile_name(pg_current_wal_lsn()) IS NOT NULL;  -- EXPECT_VALUE: true

-- 测试10：WAL位置比较
SELECT pg_wal_lsn_diff(
    pg_current_wal_lsn(),
    pg_current_wal_lsn()
) = 0;  -- EXPECT_VALUE: true

-- 测试11：插入数据并生成WAL
INSERT INTO test_replication_monitor (message)
VALUES ('Replication test message 1'),
       ('Replication test message 2'),
       ('Replication test message 3');

SELECT COUNT(*) FROM test_replication_monitor;  -- EXPECT_VALUE: 3

-- 测试12：检查WAL写入后LSN变化
DO $$
DECLARE
    lsn_before pg_lsn;
    lsn_after pg_lsn;
BEGIN
    lsn_before := pg_current_wal_lsn();
    
    INSERT INTO test_replication_monitor (message)
    VALUES ('WAL change test');
    
    lsn_after := pg_current_wal_lsn();
    
    IF pg_wal_lsn_diff(lsn_after, lsn_before) <= 0 THEN
        RAISE EXCEPTION 'WAL LSN did not advance after INSERT';
    END IF;
END $$;

-- 测试13：检查WAL发送进程（如果存在）
SELECT COUNT(*) >= 0 FROM pg_stat_activity
WHERE backend_type = 'walsender';  -- EXPECT_VALUE: true

-- 测试14：检查WAL接收进程（如果是Standby）
SELECT COUNT(*) >= 0 FROM pg_stat_activity
WHERE backend_type = 'walreceiver';  -- EXPECT_VALUE: true

-- 测试15：查询WAL接收器状态（如果是Standby）
SELECT COUNT(*) >= 0 FROM pg_stat_wal_receiver;  -- EXPECT_VALUE: true

-- 测试16：检查复制延迟监控函数
-- 如果是Standby，计算复制延迟
DO $$
BEGIN
    IF pg_is_in_recovery() THEN
        PERFORM now() - pg_last_xact_replay_timestamp();
    END IF;
END $$;

-- 测试17：检查同步复制配置
SHOW synchronous_commit;  -- 应该返回配置值

-- 测试18：检查WAL相关配置
SHOW wal_level;  -- 应该返回配置值（replica或logical）

-- TEARDOWN
-- 清理函数
DROP FUNCTION IF EXISTS test_wal_lsn_diff_bytes(text, text);
DROP FUNCTION IF EXISTS test_check_replication_status();

-- 清理表
DROP TABLE IF EXISTS test_replication_monitor;

