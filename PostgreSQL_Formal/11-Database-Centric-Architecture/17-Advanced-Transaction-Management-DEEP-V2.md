# 高级事务管理深度分析 v2.0

> **文档类型**: 数据库事务高级管理
> **核心技术**: ACID、隔离级别、MVCC、锁机制、死锁处理、长事务管理
> **创建日期**: 2026-03-04
> **文档长度**: 10000+字

---

## 目录

- [高级事务管理深度分析 v2.0](#高级事务管理深度分析-v20)
  - [目录](#目录)
  - [摘要](#摘要)
  - [1. 事务基础回顾](#1-事务基础回顾)
    - [1.1 ACID特性](#11-acid特性)
    - [1.2 事务状态机](#12-事务状态机)
  - [2. 隔离级别深度分析](#2-隔离级别深度分析)
    - [2.1 标准隔离级别](#21-标准隔离级别)
    - [2.2 PostgreSQL MVCC实现](#22-postgresql-mvcc实现)
    - [2.3 幻读与Serializable](#23-幻读与serializable)
  - [3. 锁机制详解](#3-锁机制详解)
    - [3.1 锁类型](#31-锁类型)
    - [3.2 锁粒度](#32-锁粒度)
    - [3.3 锁升级与死锁](#33-锁升级与死锁)
  - [4. 存储过程事务模式](#4-存储过程事务模式)
    - [4.1 嵌套事务](#41-嵌套事务)
    - [4.2 自治事务](#42-自治事务)
    - [4.3 链式事务](#43-链式事务)
  - [5. 长事务管理](#5-长事务管理)
    - [5.1 长事务检测](#51-长事务检测)
    - [5.2 长事务优化](#52-长事务优化)
  - [6. 事务性能优化](#6-事务性能优化)
    - [6.1 批量操作](#61-批量操作)
    - [6.2 事务拆分](#62-事务拆分)
  - [7. 异常处理与恢复](#7-异常处理与恢复)
    - [7.1 事务回滚策略](#71-事务回滚策略)
    - [7.2 部分回滚](#72-部分回滚)
  - [8. 分布式事务](#8-分布式事务)
  - [9. 持续推进计划](#9-持续推进计划)
    - [短期目标 (1-2周)](#短期目标-1-2周)
    - [中期目标 (1个月)](#中期目标-1个月)
    - [长期目标 (3个月)](#长期目标-3个月)

---

## 摘要

事务是数据库系统的核心特性，保证数据一致性和完整性。
本文档深入分析PostgreSQL的事务管理机制，包括ACID实现、MVCC原理、锁机制、隔离级别，以及存储过程中的高级事务模式。

**核心内容**:

- **隔离级别**: Read Committed, Repeatable Read, Serializable
- **MVCC机制**: 多版本并发控制实现原理
- **锁管理**: 行锁、表锁、死锁检测与解决
- **存储过程**: 嵌套事务、自治事务、链式事务模式
- **性能优化**: 长事务管理、批量操作、事务拆分

---

## 1. 事务基础回顾

### 1.1 ACID特性

```text
┌─────────────────────────────────────────────────────────────────────┐
│  ACID特性详解                                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ Atomicity   │  │ Consistency │  │ Isolation   │  │ Durability │ │
│  │  原子性     │  │  一致性      │  │  隔离性      │  │  持久性    │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │
│         │                │                │               │        │
│         ▼                ▼                ▼               ▼        │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  A: 要么全部成功，要么全部回滚                                   │ │
│  │     BEGIN → UPDATE A → UPDATE B → COMMIT/ROLLBACK              │ │
│  │                                                                │ │
│  │  C: 事务执行前后，数据库保持一致性约束                           │ │
│  │     转账前后总金额不变：A账户-100，B账户+100                     │ │
│  │                                                                │ │
│  │  I: 并发事务互不干扰                                             │ │
│  │     事务A的修改在提交前对事务B不可见                             │ │
│  │                                                                │ │
│  │  D: 提交后数据永久保存                                           │ │
│  │     即使系统崩溃，已提交数据不丢失                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 事务状态机

```sql
-- ============================================
-- 事务状态监控
-- ============================================

-- 活跃事务视图
CREATE VIEW v_active_transactions AS
SELECT
    pid,
    usename,
    datname,
    backend_xid as xid,
    backend_xmin,
    state,
    state_change,
    xact_start,
    query_start,
    wait_event_type,
    wait_event,
    query,
    age(now(), xact_start) as transaction_age
FROM pg_stat_activity
WHERE backend_xid IS NOT NULL OR xact_start IS NOT NULL
ORDER BY xact_start;

-- 事务状态转换图（简化）
/*
                    BEGIN
                      │
                      ▼
    ┌─────────────────────────────────┐
    │          ACTIVE                 │
    │  (事务执行中，持有锁)            │
    └──────────────┬──────────────────┘
                   │
         ┌─────────┴──────────┐
         │                    │
         ▼                    ▼
    ┌─────────┐         ┌───────────┐
    │ COMMIT  │         │  ROLLBACK │
    │(成功提交)│         │ (回滚撤销) │
    └────┬────┘         └─────┬─────┘
         │                    │
         ▼                    ▼
    ┌──────────┐         ┌──────────┐
    │COMMITTED │         │ABORTED   │
    │(已提交)   │         │(已中止)   │
    └──────────┘         └──────────┘
*/
```

---

## 2. 隔离级别深度分析

### 2.1 标准隔离级别

```sql
-- ============================================
-- 隔离级别设置与演示
-- ============================================

-- 设置隔离级别
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 会话级设置
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 存储过程中设置
CREATE OR REPLACE PROCEDURE sp_strict_transaction()
LANGUAGE plpgsql
AS $$
BEGIN
    -- 设置最严格的隔离级别
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    -- 业务逻辑
    PERFORM * FROM accounts WHERE balance > 1000 FOR UPDATE;

    COMMIT;
END;
$$;

-- 隔离级别对比表
/*
┌──────────────────┬──────────┬────────────┬──────────┬────────────┐
│ 隔离级别         │ 脏读     │ 不可重复读  │ 幻读     │ 序列化异常  │
├──────────────────┼──────────┼────────────┼──────────┼────────────┤
│ Read Uncommitted │ 可能     │ 可能       │ 可能     │ 可能       │
│ Read Committed   │ 不可能   │ 可能       │ 可能     │ 可能       │
│ Repeatable Read  │ 不可能   │ 不可能     │ 可能     │ 可能       │
│ Serializable     │ 不可能   │ 不可能     │ 不可能   │ 不可能     │
└──────────────────┴──────────┴────────────┴──────────┴────────────┘

PostgreSQL实际实现:
- Read Uncommitted 被视作 Read Committed
- Repeatable Read 在PostgreSQL中实际上防止了幻读（Snapshot Isolation）
- Serializable 使用Serializable Snapshot Isolation (SSI)
*/
```

### 2.2 PostgreSQL MVCC实现

```sql
-- ============================================
-- MVCC可见性规则
-- ============================================

-- PostgreSQL每行包含的系统列
SELECT
    xmin,  -- 插入事务ID
    xmax,  -- 删除事务ID（0表示未删除）
    cmin,  -- 插入命令ID
    cmax,  -- 删除命令ID
    ctid   -- 物理行位置
FROM orders
LIMIT 1;

-- 事务快照
CREATE OR REPLACE FUNCTION fn_get_transaction_snapshot()
RETURNS TEXT
LANGUAGE SQL
AS $$
    SELECT pg_current_snapshot();
    -- 返回类似: 100:200:100,150
    -- 格式: xmin:xmax:xip_list
    -- xmin: 最早活跃事务ID
    -- xmax: 最新已分配事务ID+1
    -- xip_list: 活跃事务ID列表
$$;

-- 可见性判断函数（简化版）
CREATE OR REPLACE FUNCTION fn_is_row_visible(
    p_row_xmin XID,
    p_row_xmax XID,
    p_snapshot_xmin XID,
    p_snapshot_xmax XID
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    -- 行对当前事务可见当且仅当:
    -- 1. 插入事务已提交
    -- 2. 插入事务在当前事务开始前提交
    -- 3. 删除事务未发生或删除事务在当前事务开始后才提交

    IF p_row_xmin >= p_snapshot_xmax THEN
        RETURN false;  -- 行在当前快照后插入
    END IF;

    IF p_row_xmax != 0 AND p_row_xmax < p_snapshot_xmin THEN
        RETURN false;  -- 行在当前快照前已删除
    END IF;

    RETURN true;
END;
$$;

-- MVCC清理（VACUUM）
CREATE OR REPLACE PROCEDURE sp_analyze_mvcc_bloat(
    IN p_table_name TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_stats RECORD;
BEGIN
    SELECT
        schemaname,
        relname,
        n_dead_tup as dead_tuples,
        n_live_tup as live_tuples,
        CASE WHEN n_live_tup > 0
            THEN round(n_dead_tup::numeric / n_live_tup * 100, 2)
            ELSE 0
        END as bloat_ratio,
        last_vacuum,
        last_autovacuum,
        last_analyze
    INTO v_stats
    FROM pg_stat_user_tables
    WHERE relname = p_table_name;

    RAISE NOTICE 'Table %: % dead tuples, % live tuples, % bloat',
        p_table_name, v_stats.dead_tuples, v_stats.live_tuples, v_stats.bloat_ratio;

    -- 如果膨胀率超过20%，建议VACUUM
    IF v_stats.bloat_ratio > 20 THEN
        RAISE NOTICE 'Recommend: VACUUM ANALYZE %', p_table_name;
    END IF;
END;
$$;
```

### 2.3 幻读与Serializable

```sql
-- ============================================
-- Serializable隔离级别与SSI
-- ============================================

-- 幻读演示表
CREATE TABLE inventory (
    product_id INT PRIMARY KEY,
    quantity INT NOT NULL,
    version INT DEFAULT 1
);

-- 事务A: 查询库存
-- SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- SELECT * FROM inventory WHERE quantity < 10;
-- 返回: product_id=1, quantity=5

-- 事务B（并发）: 插入新记录
-- INSERT INTO inventory VALUES (2, 3);
-- COMMIT;

-- 事务A: 再次查询
-- SELECT * FROM inventory WHERE quantity < 10;
-- Repeatable Read: 返回1条（看不到新插入的，因为是快照读）
-- Read Committed: 返回2条（看到已提交的新记录）

-- Serializable隔离级别下的序列化冲突检测
CREATE OR REPLACE PROCEDURE sp_serializable_transfer(
    IN p_from_account INT,
    IN p_to_account INT,
    IN p_amount DECIMAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_from_balance DECIMAL;
    v_to_balance DECIMAL;
BEGIN
    -- 使用Serializable隔离级别
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    -- 读取源账户
    SELECT balance INTO v_from_balance
    FROM accounts
    WHERE account_id = p_from_account;

    IF v_from_balance < p_amount THEN
        RAISE EXCEPTION 'Insufficient balance';
    END IF;

    -- 模拟一些处理时间
    PERFORM pg_sleep(0.1);

    -- 读取目标账户
    SELECT balance INTO v_to_balance
    FROM accounts
    WHERE account_id = p_to_account;

    -- 执行转账
    UPDATE accounts SET balance = balance - p_amount
    WHERE account_id = p_from_account;

    UPDATE accounts SET balance = balance + p_amount
    WHERE account_id = p_to_account;

    COMMIT;

EXCEPTION
    WHEN serialization_failure THEN
        -- SSI检测到读写依赖冲突，需要重试
        RAISE NOTICE 'Serialization conflict detected, transaction should be retried';
        RAISE;
END;
$$;

-- 序列化冲突监控
CREATE VIEW v_serializable_conflicts AS
SELECT
    timestamp,
    userid,
    dbid,
    query,
    conflict_type
FROM pg_stat_database_conflicts
WHERE conflicts > 0;
```

---

## 3. 锁机制详解

### 3.1 锁类型

```sql
-- ============================================
-- PostgreSQL锁类型
-- ============================================

-- 锁模式表
/*
┌─────────────────────┬──────────┬────────────────────────────────────────────┐
│ 锁模式              │ 冲突锁   │ 描述                                        │
├─────────────────────┼──────────┼────────────────────────────────────────────┤
│ ACCESS SHARE        │ 8        │ SELECT                                       │
│ ROW SHARE           │ 7        │ SELECT FOR UPDATE/FOR SHARE                  │
│ ROW EXCLUSIVE       │ 6        │ INSERT, UPDATE, DELETE                       │
│ SHARE UPDATE EXCLUSIVE│ 5      │ VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY   │
│ SHARE               │ 4        │ CREATE INDEX                                 │
│ SHARE ROW EXCLUSIVE │ 3        │ 触发器启用/禁用                              │
│ EXCLUSIVE           │ 2        │ REFRESH MATERIALIZED VIEW CONCURRENTLY       │
│ ACCESS EXCLUSIVE    │ 1        │ ALTER TABLE, DROP TABLE, VACUUM FULL, LOCK   │
└─────────────────────┴──────────┴────────────────────────────────────────────┘
*/

-- 查看当前锁
CREATE VIEW v_lock_status AS
SELECT
    l.locktype,
    l.relation::regclass as table_name,
    l.mode,
    l.granted,
    l.pid,
    a.usename,
    a.query,
    a.state
FROM pg_locks l
LEFT JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.locktype = 'relation'
ORDER BY l.relation::regclass::text, l.mode;

-- 行锁类型
/*
FOR UPDATE     - 排他锁，阻止其他事务修改或锁定
FOR NO KEY UPDATE - 不阻止FOR KEY SHARE
FOR SHARE      - 共享锁，阻止排他锁
FOR KEY SHARE  - 最弱锁，只阻止FOR UPDATE
*/

-- 存储过程：带锁的库存扣减
CREATE OR REPLACE PROCEDURE sp_deduct_inventory_with_lock(
    IN p_product_id INT,
    IN p_quantity INT,
    OUT p_success BOOLEAN,
    OUT p_available_quantity INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_quantity INT;
BEGIN
    -- 使用FOR UPDATE锁定特定行
    SELECT quantity INTO v_current_quantity
    FROM inventory
    WHERE product_id = p_product_id
    FOR UPDATE;  -- 等待行锁

    p_available_quantity := v_current_quantity;

    IF v_current_quantity < p_quantity THEN
        p_success := false;
        RETURN;
    END IF;

    UPDATE inventory
    SET quantity = quantity - p_quantity,
        version = version + 1
    WHERE product_id = p_product_id;

    p_success := true;
END;
$$;

-- 跳过锁定的行（NOWAIT vs SKIP LOCKED）
CREATE OR REPLACE FUNCTION fn_get_next_available_task()
RETURNS TABLE (task_id INT, task_data JSONB)
LANGUAGE plpgsql
AS $$
BEGIN
    -- SKIP LOCKED: 跳过已被其他事务锁定的行
    RETURN QUERY
    SELECT t.id, t.data
    FROM tasks t
    WHERE t.status = 'pending'
    ORDER BY t.priority DESC, t.created_at
    FOR UPDATE SKIP LOCKED
    LIMIT 1;

    -- 如果返回空，说明所有待处理任务都被锁定
    IF NOT FOUND THEN
        RAISE NOTICE 'No available tasks (all locked)';
    END IF;
END;
$$;
```

### 3.2 锁粒度

```sql
-- ============================================
-- 锁粒度与优化
-- ============================================

-- 1. 表级锁
LOCK TABLE orders IN ACCESS EXCLUSIVE MODE;
LOCK TABLE inventory IN SHARE MODE;

-- 2. 行级锁（默认）
SELECT * FROM orders WHERE id = 123 FOR UPDATE;

-- 3. 页级锁（PostgreSQL不常用，主要是行锁）

-- 4. 死锁检测（自动）
-- deadlock_timeout = 1s  -- 死锁检测超时

-- 死锁预防存储过程
CREATE OR REPLACE PROCEDURE sp_safe_transfer(
    IN p_from_account INT,
    IN p_to_account INT,
    IN p_amount DECIMAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_first_account INT;
    v_second_account INT;
BEGIN
    -- 按ID排序锁定，避免死锁
    IF p_from_account < p_to_account THEN
        v_first_account := p_from_account;
        v_second_account := p_to_account;
    ELSE
        v_first_account := p_to_account;
        v_second_account := p_from_account;
    END IF;

    -- 按固定顺序锁定
    PERFORM * FROM accounts WHERE account_id = v_first_account FOR UPDATE;
    PERFORM * FROM accounts WHERE account_id = v_second_account FOR UPDATE;

    -- 执行转账
    UPDATE accounts SET balance = balance - p_amount WHERE account_id = p_from_account;
    UPDATE accounts SET balance = balance + p_amount WHERE account_id = p_to_account;
END;
$$;

-- 锁等待监控
CREATE VIEW v_lock_waits AS
SELECT
    w.pid as waiting_pid,
    w.usename as waiting_user,
    w.query as waiting_query,
    b.pid as blocking_pid,
    b.usename as blocking_user,
    b.query as blocking_query,
    l.mode as lock_mode,
    l.relation::regclass as locked_table
FROM pg_stat_activity w
JOIN pg_locks l ON w.pid = l.pid AND NOT l.granted
JOIN pg_locks l2 ON l.locktype = l2.locktype
    AND l.relation = l2.relation
    AND l2.granted
JOIN pg_stat_activity b ON l2.pid = b.pid
WHERE w.wait_event_type = 'Lock';
```

### 3.3 锁升级与死锁

```sql
-- ============================================
-- 死锁检测与解决
-- ============================================

-- 死锁检测器（自动运行）
-- 手动触发死锁检测示例（仅用于演示）

-- 存储过程：带重试的死锁安全执行
CREATE OR REPLACE PROCEDURE sp_deadlock_safe_execute(
    IN p_sql TEXT,
    IN p_max_retries INT DEFAULT 3
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_retry_count INT := 0;
    v_success BOOLEAN := false;
BEGIN
    WHILE v_retry_count < p_max_retries AND NOT v_success LOOP
        BEGIN
            EXECUTE p_sql;
            v_success := true;

        EXCEPTION
            WHEN deadlock_detected THEN
                v_retry_count := v_retry_count + 1;
                RAISE NOTICE 'Deadlock detected, retry %/%', v_retry_count, p_max_retries;

                -- 随机退避
                PERFORM pg_sleep(random() * 0.1 * v_retry_count);
        END;
    END LOOP;

    IF NOT v_success THEN
        RAISE EXCEPTION 'Max retries exceeded due to deadlocks';
    END IF;
END;
$$;

-- 应用层死锁预防（伪代码）
/*
-- 方案1: 固定顺序访问
-- 对所有资源按ID排序后依次访问

-- 方案2: 一次性锁定所有资源
SELECT * FROM resources WHERE id IN (id1, id2, id3) FOR UPDATE;

-- 方案3: 超时重试
BEGIN
    SET LOCAL lock_timeout = '5s';
    -- 业务逻辑
EXCEPTION WHEN lock_not_available THEN
    -- 重试
END;
*/

-- 锁超时设置
CREATE OR REPLACE PROCEDURE sp_with_lock_timeout(
    IN p_sql TEXT,
    IN p_timeout INTERVAL DEFAULT '5 seconds'
)
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('SET LOCAL lock_timeout = %L', p_timeout);
    EXECUTE p_sql;
END;
$$;
```

---

## 4. 存储过程事务模式

### 4.1 嵌套事务

```sql
-- ============================================
-- PostgreSQL中的嵌套事务（SAVEPOINT）
-- ============================================

-- PostgreSQL不真正支持嵌套事务，使用SAVEPOINT模拟

CREATE OR REPLACE PROCEDURE sp_nested_transaction_demo()
LANGUAGE plpgsql
AS $$
DECLARE
    v_outer_sp TEXT;
    v_inner_sp TEXT;
BEGIN
    -- 外层事务开始
    RAISE NOTICE 'Outer transaction started';

    INSERT INTO audit_log (message) VALUES ('Outer: Step 1');

    -- 创建保存点（模拟嵌套事务）
    v_outer_sp := 'sp_outer_' || txid_current();
    EXECUTE 'SAVEPOINT ' || v_outer_sp;

    BEGIN
        INSERT INTO audit_log (message) VALUES ('Outer: Step 2 (in savepoint)');

        -- 内层"事务"
        v_inner_sp := 'sp_inner_' || txid_current();
        EXECUTE 'SAVEPOINT ' || v_inner_sp;

        BEGIN
            INSERT INTO audit_log (message) VALUES ('Inner: Step 1');

            -- 模拟错误
            RAISE EXCEPTION 'Simulated inner error';

        EXCEPTION WHEN OTHERS THEN
            -- 回滚到内层保存点
            EXECUTE 'ROLLBACK TO SAVEPOINT ' || v_inner_sp;
            RAISE NOTICE 'Inner transaction rolled back: %', SQLERRM;

            INSERT INTO audit_log (message) VALUES ('Inner: Rolled back');
        END;

        -- 内层回滚后，外层保存点继续
        INSERT INTO audit_log (message) VALUES ('Outer: Continuing after inner rollback');

    EXCEPTION WHEN OTHERS THEN
        -- 回滚到外层保存点
        EXECUTE 'ROLLBACK TO SAVEPOINT ' || v_outer_sp;
        RAISE NOTICE 'Outer savepoint rolled back: %', SQLERRM;
    END;

    -- 释放保存点
    EXECUTE 'RELEASE SAVEPOINT ' || v_outer_sp;

    INSERT INTO audit_log (message) VALUES ('Outer: Completed');

    -- 外层事务提交
    COMMIT;
END;
$$;

-- 存储过程：带保存点的批量处理
CREATE OR REPLACE PROCEDURE sp_batch_with_savepoints(
    IN p_items JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_item JSONB;
    v_item_id TEXT;
    v_processed INT := 0;
    v_failed INT := 0;
BEGIN
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        v_item_id := v_item->>'id';

        BEGIN
            -- 每个项目使用保存点
            EXECUTE 'SAVEPOINT item_processing';

            -- 处理项目
            INSERT INTO processed_items (item_id, data, status)
            VALUES (v_item_id, v_item, 'success');

            EXECUTE 'RELEASE SAVEPOINT item_processing';
            v_processed := v_processed + 1;

        EXCEPTION WHEN OTHERS THEN
            -- 单个项目失败不影响其他
            EXECUTE 'ROLLBACK TO SAVEPOINT item_processing';

            INSERT INTO processed_items (item_id, data, status, error)
            VALUES (v_item_id, v_item, 'failed', SQLERRM);

            v_failed := v_failed + 1;
        END;
    END LOOP;

    RAISE NOTICE 'Processed: %, Failed: %', v_processed, v_failed;
END;
$$;
```

### 4.2 自治事务

```sql
-- ============================================
-- 自治事务模拟（使用dblink或背景工作者）
-- ============================================

-- PostgreSQL不原生支持自治事务，可以使用以下方法模拟

-- 方法1: 使用dblink
CREATE EXTENSION IF NOT EXISTS dblink;

CREATE OR REPLACE PROCEDURE sp_autonomous_audit_log(
    IN p_message TEXT,
    IN p_severity TEXT DEFAULT 'INFO'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_conn TEXT;
BEGIN
    -- 使用dblink到同一数据库，创建独立连接
    v_conn := 'dbname=' || current_database();

    PERFORM dblink_exec(v_conn, format(
        'INSERT INTO audit_log (message, severity, created_at) VALUES (%L, %L, NOW())',
        p_message, p_severity
    ));
END;
$$;

-- 方法2: 使用pg_background扩展（如安装）
-- CREATE EXTENSION pg_background;

-- 方法3: 使用逻辑复制或NOTIFY异步处理

-- 自治事务示例：订单处理，审计日志独立提交
CREATE OR REPLACE PROCEDURE sp_process_order_autonomous(
    IN p_order_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order RECORD;
BEGIN
    SELECT * INTO v_order FROM orders WHERE id = p_order_id;

    -- 自治事务：记录开始处理（立即提交，不受主事务影响）
    CALL sp_autonomous_audit_log(
        format('Started processing order %s', p_order_id),
        'INFO'
    );

    BEGIN
        -- 主事务：处理订单
        UPDATE orders SET status = 'processing' WHERE id = p_order_id;

        -- 模拟处理
        PERFORM pg_sleep(1);

        UPDATE orders SET status = 'completed' WHERE id = p_order_id;

        -- 自治事务：记录成功
        CALL sp_autonomous_audit_log(
            format('Order %s processed successfully', p_order_id),
            'INFO'
        );

    EXCEPTION WHEN OTHERS THEN
        -- 自治事务：记录失败（即使主事务回滚，此记录仍存在）
        CALL sp_autonomous_audit_log(
            format('Order %s processing failed: %s', p_order_id, SQLERRM),
            'ERROR'
        );
        RAISE;
    END;
END;
$$;
```

### 4.3 链式事务

```sql
-- ============================================
-- 链式事务（COMMIT AND CHAIN）
-- ============================================

-- PostgreSQL 14+ 支持COMMIT AND CHAIN / ROLLBACK AND CHAIN

-- 存储过程：批量处理链式事务
CREATE OR REPLACE PROCEDURE sp_chained_batch_process(
    IN p_batch_size INT DEFAULT 1000
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_batch_count INT := 0;
    v_total_processed INT := 0;
BEGIN
    -- 开启第一个事务
    SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

    WHILE v_batch_count < p_batch_size LOOP
        -- 处理一批数据
        INSERT INTO processed_data (data, batch_id)
        SELECT raw_data, v_batch_count
        FROM raw_data_queue
        WHERE processed = false
        LIMIT 100;

        UPDATE raw_data_queue
        SET processed = true
        WHERE id IN (
            SELECT id FROM raw_data_queue
            WHERE processed = false
            LIMIT 100
        );

        v_batch_count := v_batch_count + 1;
        v_total_processed := v_total_processed + 100;

        -- 每批提交并开启新事务
        IF v_batch_count < p_batch_size THEN
            -- 使用链式事务保持会话状态
            -- COMMIT AND CHAIN;  -- PostgreSQL 14+

            -- 兼容旧版本的实现
            COMMIT;
            -- 新事务自动开始（存储过程中）
        END IF;
    END LOOP;

    RAISE NOTICE 'Total processed: %', v_total_processed;
END;
$$;

-- 手动链式事务管理
CREATE OR REPLACE PROCEDURE sp_manual_chained_transaction()
LANGUAGE plpgsql
AS $$
DECLARE
    v_iteration INT := 0;
BEGIN
    LOOP
        v_iteration := v_iteration + 1;

        BEGIN
            -- 开启新事务块
            -- 处理逻辑
            PERFORM * FROM some_table WHERE processed = false LIMIT 10 FOR UPDATE;

            -- 标记处理完成
            UPDATE some_table SET processed = true
            WHERE id IN (SELECT id FROM some_table WHERE processed = false LIMIT 10);

            -- 提交当前事务
            COMMIT;

        EXCEPTION WHEN OTHERS THEN
            ROLLBACK;
            RAISE NOTICE 'Iteration % failed: %', v_iteration, SQLERRM;
        END;

        EXIT WHEN v_iteration >= 10;
    END LOOP;
END;
$$;
```

---

## 5. 长事务管理

### 5.1 长事务检测

```sql
-- ============================================
-- 长事务检测与告警
-- ============================================

-- 长事务监控视图
CREATE VIEW v_long_transactions AS
SELECT
    pid,
    usename,
    datname,
    state,
    age(now(), xact_start) as transaction_age,
    age(now(), query_start) as query_age,
    wait_event_type,
    wait_event,
    left(query, 100) as query_preview
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND state != 'idle'
ORDER BY xact_start;

-- 危险长事务告警
CREATE OR REPLACE PROCEDURE sp_check_long_transactions()
LANGUAGE plpgsql
AS $$
DECLARE
    v_long_tx RECORD;
    v_threshold INTERVAL := INTERVAL '5 minutes';
BEGIN
    FOR v_long_tx IN
        SELECT * FROM v_long_transactions
        WHERE transaction_age > v_threshold
    LOOP
        -- 发送告警
        PERFORM pg_notify('long_transaction_alert', jsonb_build_object(
            'pid', v_long_tx.pid,
            'user', v_long_tx.usename,
            'duration', v_long_tx.transaction_age::TEXT,
            'query', v_long_tx.query_preview
        )::TEXT);

        -- 如果超过10分钟，考虑终止
        IF v_long_tx.transaction_age > INTERVAL '10 minutes' THEN
            RAISE WARNING 'Consider terminating long transaction: PID %, Duration %',
                v_long_tx.pid, v_long_tx.transaction_age;
        END IF;
    END LOOP;
END;
$$;

-- 空闲事务检测
CREATE OR REPLACE PROCEDURE sp_check_idle_transactions()
LANGUAGE plpgsql
AS $$
DECLARE
    v_idle_tx RECORD;
BEGIN
    FOR v_idle_tx IN
        SELECT
            pid,
            usename,
            state,
            age(now(), xact_start) as idle_age,
            left(query, 100) as last_query
        FROM pg_stat_activity
        WHERE state = 'idle in transaction'
          AND xact_start < NOW() - INTERVAL '1 minute'
    LOOP
        RAISE WARNING 'Idle in transaction: PID %, Duration %, User %',
            v_idle_tx.pid, v_idle_tx.idle_age, v_idle_tx.usename;
    END LOOP;
END;
$$;
```

### 5.2 长事务优化

```sql
-- ============================================
-- 长事务优化策略
-- ============================================

-- 1. 游标优化（避免长事务持有行锁）
CREATE OR REPLACE PROCEDURE sp_cursor_based_processing()
LANGUAGE plpgsql
AS $$
DECLARE
    v_cursor CURSOR FOR
        SELECT id, data FROM large_table WHERE processed = false;
    v_record RECORD;
    v_batch_size INT := 1000;
    v_count INT := 0;
BEGIN
    OPEN v_cursor;

    LOOP
        FETCH v_cursor INTO v_record;
        EXIT WHEN NOT FOUND;

        -- 处理单条记录
        PERFORM process_record(v_record.id, v_record.data);

        v_count := v_count + 1;

        -- 定期提交，避免长事务
        IF v_count >= v_batch_size THEN
            CLOSE v_cursor;
            COMMIT;

            -- 重新打开游标
            OPEN v_cursor;
            v_count := 0;
        END IF;
    END LOOP;

    CLOSE v_cursor;
END;
$$;

-- 2. 基于时间的事务切分
CREATE OR REPLACE PROCEDURE sp_time_bound_processing(
    IN p_max_duration INTERVAL DEFAULT INTERVAL '30 seconds'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_start_time TIMESTAMPTZ := clock_timestamp();
    v_batch_count INT := 0;
BEGIN
    LOOP
        -- 处理一批数据
        WITH batch AS (
            SELECT id FROM processing_queue
            WHERE status = 'pending'
            LIMIT 100
        )
        UPDATE processing_queue
        SET status = 'processing'
        WHERE id IN (SELECT id FROM batch);

        GET DIAGNOSTICS v_batch_count = ROW_COUNT;

        -- 检查时间限制
        IF clock_timestamp() - v_start_time > p_max_duration THEN
            RAISE NOTICE 'Time limit reached, committing batch';
            COMMIT;

            -- 重置计时器
            v_start_time := clock_timestamp();
        END IF;

        EXIT WHEN v_batch_count = 0;
    END LOOP;
END;
$$;

-- 3. 使用临时表减少事务持有时间
CREATE OR REPLACE PROCEDURE sp_temp_table_processing()
LANGUAGE plpgsql
AS $$
BEGIN
    -- 创建临时表，复制需要处理的数据
    CREATE TEMP TABLE temp_processing AS
    SELECT id, data
    FROM large_table
    WHERE processed = false
    LIMIT 10000;

    -- 可以在临时表上创建索引
    CREATE INDEX ON temp_processing(id);

    -- 提交，释放源表锁
    COMMIT;

    -- 基于临时表处理（不影响源表）
    FOR rec IN SELECT * FROM temp_processing
    LOOP
        PERFORM process_data(rec.id, rec.data);
    END LOOP;

    -- 批量更新源表
    UPDATE large_table
    SET processed = true
    WHERE id IN (SELECT id FROM temp_processing);

    -- 清理临时表（会话结束自动清理）
    DROP TABLE IF EXISTS temp_processing;
END;
$$;
```

---

## 6. 事务性能优化

### 6.1 批量操作

```sql
-- ============================================
-- 批量操作优化
-- ============================================

-- 1. 批量插入
CREATE OR REPLACE PROCEDURE sp_bulk_insert_optimized(
    IN p_records JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 禁用约束检查（临时）
    ALTER TABLE orders DISABLE TRIGGER ALL;

    -- 批量插入
    INSERT INTO orders (user_id, total, status, created_at)
    SELECT
        (elem->>'user_id')::BIGINT,
        (elem->>'total')::DECIMAL,
        'pending',
        NOW()
    FROM jsonb_array_elements(p_records) AS elem;

    -- 重新启用约束
    ALTER TABLE orders ENABLE TRIGGER ALL;

    -- 手动触发统计更新
    ANALYZE orders;
END;
$$;

-- 2. COPY协议批量加载
CREATE OR REPLACE PROCEDURE sp_copy_bulk_load(
    IN p_file_path TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 使用COPY（最快的方式）
    EXECUTE format('COPY orders FROM %L WITH (FORMAT csv, HEADER)', p_file_path);
END;
$$;

-- 3. 批量更新（使用CASE WHEN）
CREATE OR REPLACE PROCEDURE sp_bulk_update_optimized(
    IN p_updates JSONB  -- [{"id": 1, "status": "shipped"}, ...]
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 将JSONB转换为临时表
    CREATE TEMP TABLE temp_updates AS
    SELECT
        (elem->>'id')::BIGINT as id,
        elem->>'status' as status
    FROM jsonb_array_elements(p_updates) AS elem;

    -- 批量更新（单条UPDATE语句）
    UPDATE orders o
    SET status = u.status,
        updated_at = NOW()
    FROM temp_updates u
    WHERE o.id = u.id;

    DROP TABLE temp_updates;
END;
$$;
```

### 6.2 事务拆分

```sql
-- ============================================
-- 大事务拆分策略
-- ============================================

-- 1. 分块处理
CREATE OR REPLACE PROCEDURE sp_chunked_processing(
    IN p_table_name TEXT,
    IN p_chunk_size INT DEFAULT 10000
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_offset INT := 0;
    v_processed INT;
    v_total INT;
BEGIN
    -- 获取总数
    EXECUTE format('SELECT COUNT(*) FROM %I WHERE processed = false', p_table_name)
    INTO v_total;

    WHILE v_offset < v_total LOOP
        -- 处理一个块
        EXECUTE format('
            UPDATE %I
            SET processed = true
            WHERE id IN (
                SELECT id FROM %I
                WHERE processed = false
                ORDER BY id
                LIMIT $1 OFFSET $2
            )
        ', p_table_name, p_table_name)
        USING p_chunk_size, v_offset;

        GET DIAGNOSTICS v_processed = ROW_COUNT;

        -- 提交当前块
        COMMIT;

        RAISE NOTICE 'Processed chunk: offset %, rows %', v_offset, v_processed;

        v_offset := v_offset + p_chunk_size;
    END LOOP;
END;
$$;

-- 2. 基于ID范围的拆分
CREATE OR REPLACE PROCEDURE sp_id_range_processing(
    IN p_min_id BIGINT,
    IN p_max_id BIGINT,
    IN p_range_size BIGINT DEFAULT 100000
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_start_id BIGINT := p_min_id;
    v_end_id BIGINT;
BEGIN
    WHILE v_start_id <= p_max_id LOOP
        v_end_id := LEAST(v_start_id + p_range_size - 1, p_max_id);

        -- 处理当前ID范围
        PERFORM process_id_range(v_start_id, v_end_id);

        -- 提交
        COMMIT;

        v_start_id := v_end_id + 1;
    END LOOP;
END;
$$;
```

---

## 7. 异常处理与恢复

### 7.1 事务回滚策略

```sql
-- ============================================
-- 事务回滚策略
-- ============================================

-- 1. 标准回滚模式
CREATE OR REPLACE PROCEDURE sp_safe_transaction()
LANGUAGE plpgsql
AS $$
BEGIN
    -- 设置异常处理
    BEGIN
        -- 业务操作1
        INSERT INTO table1 VALUES (...);

        -- 业务操作2
        UPDATE table2 SET ...;

        -- 如果一切正常，提交
        COMMIT;

    EXCEPTION WHEN OTHERS THEN
        -- 错误处理
        ROLLBACK;

        -- 记录错误
        INSERT INTO error_log (message, error_detail)
        VALUES ('Transaction failed', SQLERRM);

        -- 重新抛出或处理
        RAISE;
    END;
END;
$$;

-- 2. 智能回滚（根据错误类型）
CREATE OR REPLACE PROCEDURE sp_intelligent_rollback()
LANGUAGE plpgsql
AS $$
BEGIN
    BEGIN
        -- 业务逻辑
        PERFORM risky_operation();

    EXCEPTION
        WHEN deadlock_detected THEN
            -- 死锁：重试
            RAISE NOTICE 'Deadlock detected, retrying...';
            PERFORM pg_sleep(random() * 0.1);
            -- 重试逻辑

        WHEN unique_violation THEN
            -- 唯一性冲突：可能是重复提交，记录但不重试
            INSERT INTO conflict_log (error_type, detail)
            VALUES ('unique_violation', SQLERRM);

        WHEN foreign_key_violation THEN
            -- 外键冲突：数据不一致，需要人工介入
            INSERT INTO manual_review_queue (error_type, detail, created_at)
            VALUES ('fk_violation', SQLERRM, NOW());

        WHEN OTHERS THEN
            -- 其他错误：回滚并告警
            ROLLBACK;
            RAISE;
    END;
END;
$$;

-- 3. 回滚日志
CREATE TABLE rollback_log (
    log_id UUID PRIMARY KEY DEFAULT uuidv7(),
    transaction_id BIGINT,
    rollback_reason TEXT,
    rolled_back_at TIMESTAMPTZ DEFAULT NOW(),
    original_state JSONB,
    recovered BOOLEAN DEFAULT false
);

CREATE OR REPLACE PROCEDURE sp_logged_rollback(
    IN p_reason TEXT,
    IN p_original_state JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO rollback_log (transaction_id, rollback_reason, original_state)
    VALUES (txid_current(), p_reason, p_original_state);

    ROLLBACK;
END;
$$;
```

### 7.2 部分回滚

```sql
-- ============================================
-- 部分回滚（使用SAVEPOINT）
-- ============================================

CREATE OR REPLACE PROCEDURE sp_partial_rollback_demo()
LANGUAGE plpgsql
AS $$
DECLARE
    v_sp1 TEXT;
    v_sp2 TEXT;
BEGIN
    -- 外层操作（始终提交）
    INSERT INTO audit_log (message) VALUES ('Transaction started');

    -- 保存点1
    v_sp1 := 'sp1_' || txid_current();
    EXECUTE 'SAVEPOINT ' || v_sp1;

    BEGIN
        INSERT INTO table_a VALUES (1, 'data1');

        -- 保存点2
        v_sp2 := 'sp2_' || txid_current();
        EXECUTE 'SAVEPOINT ' || v_sp2;

        BEGIN
            INSERT INTO table_b VALUES (1, 'data2');

            -- 模拟错误
            RAISE EXCEPTION 'Error in section B';

        EXCEPTION WHEN OTHERS THEN
            -- 回滚到保存点2，table_a的插入仍然保留
            EXECUTE 'ROLLBACK TO SAVEPOINT ' || v_sp2;
            RAISE NOTICE 'Section B rolled back: %', SQLERRM;

            -- 记录部分失败
            INSERT INTO partial_failure_log (section, error)
            VALUES ('B', SQLERRM);
        END;

        -- 继续section C（在保存点1的保护下）
        INSERT INTO table_c VALUES (1, 'data3');

        EXECUTE 'RELEASE SAVEPOINT ' || v_sp1;

    EXCEPTION WHEN OTHERS THEN
        -- 回滚到保存点1，所有操作都回滚
        EXECUTE 'ROLLBACK TO SAVEPOINT ' || v_sp1;
        RAISE NOTICE 'Section A rolled back: %', SQLERRM;
        RAISE;
    END;

    COMMIT;
END;
$$;
```

---

## 8. 分布式事务

```sql
-- ============================================
-- 分布式事务（两阶段提交）
-- ============================================

-- 1. 准备事务（第一阶段）
CREATE OR REPLACE PROCEDURE sp_prepare_transaction(
    IN p_transaction_id TEXT,
    IN p_operation JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 执行本地操作
    EXECUTE format('UPDATE accounts SET balance = balance - %s WHERE id = %s',
                   p_operation->>'amount', p_operation->>'from_account');

    -- 准备事务
    EXECUTE format('PREPARE TRANSACTION %L', p_transaction_id);
END;
$$;

-- 2. 提交准备的事务（第二阶段）
CREATE OR REPLACE PROCEDURE sp_commit_prepared(
    IN p_transaction_id TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('COMMIT PREPARED %L', p_transaction_id);
END;
$$;

-- 3. 回滚准备的事务
CREATE OR REPLACE PROCEDURE sp_rollback_prepared(
    IN p_transaction_id TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('ROLLBACK PREPARED %L', p_transaction_id);
END;
$$;

-- 4. 准备事务监控
CREATE VIEW v_prepared_transactions AS
SELECT
    transaction,
    gid as global_id,
    prepared,
    owner,
    database
FROM pg_prepared_xacts;

-- 5. 存储过程：分布式转账
CREATE OR REPLACE PROCEDURE sp_distributed_transfer_2pc(
    IN p_from_node TEXT,
    IN p_to_node TEXT,
    IN p_from_account TEXT,
    IN p_to_account TEXT,
    IN p_amount DECIMAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_xid TEXT;
    v_prepared_from BOOLEAN := false;
    v_prepared_to BOOLEAN := false;
BEGIN
    v_xid := 'txn_' || txid_current();

    -- 第一阶段：准备
    BEGIN
        -- 节点1准备
        PERFORM dblink_exec(
            format('host=%s', p_from_node),
            format('CALL sp_prepare_transaction(%L, %L)',
                   v_xid || '_from',
                   jsonb_build_object('amount', p_amount, 'from_account', p_from_account))
        );
        v_prepared_from := true;

        -- 节点2准备
        PERFORM dblink_exec(
            format('host=%s', p_to_node),
            format('CALL sp_prepare_transaction(%L, %L)',
                   v_xid || '_to',
                   jsonb_build_object('amount', p_amount, 'to_account', p_to_account))
        );
        v_prepared_to := true;

    EXCEPTION WHEN OTHERS THEN
        -- 准备失败，回滚已准备的
        IF v_prepared_from THEN
            PERFORM dblink_exec(format('host=%s', p_from_node),
                               format('ROLLBACK PREPARED %L', v_xid || '_from'));
        END IF;
        IF v_prepared_to THEN
            PERFORM dblink_exec(format('host=%s', p_to_node),
                               format('ROLLBACK PREPARED %L', v_xid || '_to'));
        END IF;
        RAISE;
    END;

    -- 第二阶段：提交
    PERFORM dblink_exec(format('host=%s', p_from_node),
                       format('COMMIT PREPARED %L', v_xid || '_from'));
    PERFORM dblink_exec(format('host=%s', p_to_node),
                       format('COMMIT PREPARED %L', v_xid || '_to'));

EXCEPTION WHEN OTHERS THEN
    -- 记录需要人工干预的事务
    INSERT INTO pending_commit_recovery (xid, from_node, to_node, error, created_at)
    VALUES (v_xid, p_from_node, p_to_node, SQLERRM, NOW());
    RAISE;
END;
$$;
```

---

## 9. 持续推进计划

### 短期目标 (1-2周)

- [ ] 审计现有存储过程的事务使用
- [ ] 实施长事务监控
- [ ] 优化高频事务性能

### 中期目标 (1个月)

- [ ] 实施隔离级别评估
- [ ] 部署死锁检测与重试机制
- [ ] 建立事务性能基线

### 长期目标 (3个月)

- [ ] 完整的事务治理框架
- [ ] 自动化事务优化建议
- [ ] 分布式事务支持

---

**文档信息**:

- 字数: 10000+
- 事务模式: 15+
- 代码示例: 40+
- 状态: ✅ 深度分析完成

---

*掌握事务，掌控数据一致性！* 🔒
