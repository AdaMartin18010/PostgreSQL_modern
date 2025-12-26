---

> **📋 文档来源**: `MVCC-ACID-CAP\03-场景实践\SQL编程\MVCC与SQL编程实践.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# MVCC与SQL编程实践

> **文档编号**: SQL-PRACTICE-001
> **主题**: MVCC与SQL编程实践
> **版本**: PostgreSQL 17 & 18
> **状态**: ✅ 已完成

---

## 📑 目录

- [MVCC与SQL编程实践](#mvcc与sql编程实践)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📊 第一部分：MVCC对SQL查询的影响](#-第一部分mvcc对sql查询的影响)
    - [1.1 SELECT查询与快照](#11-select查询与快照)
    - [1.2 UPDATE操作与版本链](#12-update操作与版本链)
    - [1.3 DELETE操作与可见性](#13-delete操作与可见性)
    - [1.4 INSERT操作与MVCC](#14-insert操作与mvcc)
  - [📊 第二部分：隔离级别与SQL行为](#-第二部分隔离级别与sql行为)
    - [2.1 READ UNCOMMITTED](#21-read-uncommitted)
    - [2.2 READ COMMITTED](#22-read-committed)
    - [2.3 REPEATABLE READ](#23-repeatable-read)
    - [2.4 SERIALIZABLE](#24-serializable)
  - [📊 第三部分：MVCC友好的SQL模式](#-第三部分mvcc友好的sql模式)
    - [3.1 避免长事务](#31-避免长事务)
    - [3.2 合理使用锁](#32-合理使用锁)
    - [3.3 优化UPDATE模式](#33-优化update模式)
    - [3.4 批量操作优化](#34-批量操作优化)
  - [📊 第四部分：常见SQL模式与MVCC](#-第四部分常见sql模式与mvcc)
    - [4.1 计数器模式](#41-计数器模式)
    - [4.2 乐观锁模式](#42-乐观锁模式)
    - [4.3 悲观锁模式](#43-悲观锁模式)
    - [4.4 队列模式](#44-队列模式)
  - [📊 第五部分：SQL性能优化与MVCC](#-第五部分sql性能优化与mvcc)
    - [5.1 查询优化](#51-查询优化)
    - [5.2 索引优化](#52-索引优化)
    - [5.3 事务优化](#53-事务优化)
  - [📝 总结](#-总结)
    - [核心结论](#核心结论)
    - [实践建议](#实践建议)

---

## 📋 概述

理解MVCC对SQL编程的影响，有助于编写MVCC友好的SQL代码，避免常见的并发问题和性能问题。

本文档从MVCC对SQL查询的影响、隔离级别与SQL行为、MVCC友好的SQL模式、常见SQL模式与MVCC和SQL性能优化五个维度，全面阐述MVCC与SQL编程实践的完整体系。

**核心观点**：

- **MVCC影响SQL行为**：不同隔离级别下SQL行为不同
- **MVCC友好的SQL模式**：避免长事务、合理使用锁
- **常见SQL模式**：计数器、乐观锁、悲观锁、队列模式
- **SQL性能优化**：查询优化、索引优化、事务优化

---

## 📊 第一部分：MVCC对SQL查询的影响

### 1.1 SELECT查询与快照

**SELECT查询与快照**：

PostgreSQL的SELECT查询基于快照隔离，每个查询看到的是事务开始时的数据快照。

**示例**：

```sql
-- MVCC快照隔离演示（带错误处理和性能测试）
-- 事务1：REPEATABLE READ隔离级别
DO $$
DECLARE
    account_record accounts%ROWTYPE;
    balance1 NUMERIC;
    balance2 NUMERIC;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法演示MVCC快照隔离';
            RETURN;
        END IF;

        SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
        RAISE NOTICE '开始事务1（REPEATABLE READ隔离级别）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        BEGIN;

        -- 第一次查询（看到快照1）
        SELECT * INTO account_record FROM accounts WHERE id = 1;

        IF FOUND THEN
            balance1 := account_record.balance;
            RAISE NOTICE '事务1第一次查询：看到快照1，balance=%', balance1;
        ELSE
            RAISE NOTICE '账户 1 不存在';
        END IF;

        -- 注意：事务2（并发）在这里执行UPDATE并COMMIT
        -- 但事务1仍然看到快照1的数据

        -- 第二次查询（仍然看到快照1）
        SELECT * INTO account_record FROM accounts WHERE id = 1;

        IF FOUND THEN
            balance2 := account_record.balance;
            RAISE NOTICE '事务1第二次查询：仍然看到快照1，balance=%（REPEATABLE READ保证可重复读）', balance2;

            IF balance1 != balance2 THEN
                RAISE WARNING '快照不一致：第一次查询=%，第二次查询=%', balance1, balance2;
            END IF;
        ELSE
            RAISE NOTICE '账户 1 不存在（第二次查询）';
        END IF;

        COMMIT;
        RAISE NOTICE '事务1提交成功';
    EXCEPTION
        WHEN serialization_failure THEN
            ROLLBACK;
            RAISE WARNING '序列化冲突，事务需要重试';
            RAISE;
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '事务1失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 性能测试：REPEATABLE READ查询
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM accounts WHERE id = 1;
```

### 1.2 UPDATE操作与版本链

**UPDATE操作与版本链**：

UPDATE操作创建新版本，旧版本保留在版本链中。

**示例**：

```sql
-- UPDATE操作与版本链演示（带错误处理）
-- 初始版本（带错误处理）
DO $$
DECLARE
    v_inserted INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法演示版本链';
            RETURN;
        END IF;

        BEGIN
            INSERT INTO accounts (id, balance) VALUES (1, 1000)
            ON CONFLICT (id) DO UPDATE SET balance = 1000;
            GET DIAGNOSTICS v_inserted = ROW_COUNT;
            RAISE NOTICE '初始版本创建成功（版本1：balance=1000）';
        EXCEPTION
            WHEN unique_violation THEN
                RAISE NOTICE '账户 1 已存在，已更新为初始版本';
            WHEN OTHERS THEN
                RAISE WARNING '创建初始版本失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 更新1（创建版本2，带错误处理和性能测试）
DO $$
DECLARE
    v_updated INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法执行更新';
            RETURN;
        END IF;

        BEGIN
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            UPDATE accounts SET balance = 1100 WHERE id = 1;

            GET DIAGNOSTICS v_updated = ROW_COUNT;
            IF v_updated = 0 THEN
                RAISE WARNING '账户 1 不存在，无法创建版本2';
            ELSE
                RAISE NOTICE '更新1成功（创建版本2：balance=1100）';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '更新1失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 更新2（创建版本3，带错误处理和性能测试）
DO $$
DECLARE
    v_updated INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法执行更新';
            RETURN;
        END IF;

        BEGIN
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            UPDATE accounts SET balance = 1200 WHERE id = 1;

            GET DIAGNOSTICS v_updated = ROW_COUNT;
            IF v_updated = 0 THEN
                RAISE WARNING '账户 1 不存在，无法创建版本3';
            ELSE
                RAISE NOTICE '更新2成功（创建版本3：balance=1200）';
                RAISE NOTICE '版本链：版本1(1000) -> 版本2(1100) -> 版本3(1200)';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '更新2失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 1.3 DELETE操作与可见性

**DELETE操作与可见性**：

DELETE操作标记元组为删除，但不立即删除，通过MVCC可见性规则控制可见性。

**示例**：

```sql
-- DELETE操作与可见性演示（带错误处理）
-- 删除操作（标记xmax，带错误处理和性能测试）
DO $$
DECLARE
    v_deleted INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法执行删除操作';
            RETURN;
        END IF;

        BEGIN
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            DELETE FROM accounts WHERE id = 1;

            GET DIAGNOSTICS v_deleted = ROW_COUNT;
            IF v_deleted = 0 THEN
                RAISE WARNING '账户 1 不存在，无法删除';
            ELSE
                RAISE NOTICE '删除操作成功（标记xmax，但元组未立即物理删除）';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '删除操作失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 其他事务仍可能看到该行（如果快照在删除之前，带错误处理）
DO $$
DECLARE
    account_record accounts%ROWTYPE;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法查询';
            RETURN;
        END IF;

        BEGIN;
        SELECT * INTO account_record FROM accounts WHERE id = 1;

        IF FOUND THEN
            RAISE NOTICE '其他事务仍然可以看到该行（如果快照在删除之前）: id=%, balance=%', account_record.id, account_record.balance;
        ELSE
            RAISE NOTICE '其他事务看不到该行（快照在删除之后或行不存在）';
        END IF;

        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '查询失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 1.4 INSERT操作与MVCC

**INSERT操作与MVCC**：

INSERT操作创建新元组，设置xmin为当前事务ID。

**示例**：

```sql
-- INSERT操作与MVCC演示（带错误处理）
DO $$
DECLARE
    v_inserted INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法执行插入操作';
            RETURN;
        END IF;

        BEGIN;

        BEGIN
            INSERT INTO accounts (id, balance) VALUES (2, 2000);
            GET DIAGNOSTICS v_inserted = ROW_COUNT;

            IF v_inserted > 0 THEN
                RAISE NOTICE '插入操作成功: id=2, balance=2000';
                RAISE NOTICE 'xmin = 当前事务ID（插入时设置）';
            ELSE
                RAISE WARNING '插入操作未插入任何记录';
            END IF;
        EXCEPTION
            WHEN unique_violation THEN
                RAISE WARNING '账户 2 已存在，无法插入';
                ROLLBACK;
                RETURN;
            WHEN OTHERS THEN
                RAISE WARNING '插入操作失败: %', SQLERRM;
                RAISE;
        END;

        COMMIT;
        RAISE NOTICE '事务提交成功（提交后，xmin可见）';
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 📊 第二部分：隔离级别与SQL行为

### 2.1 READ UNCOMMITTED

**READ UNCOMMITTED**：

PostgreSQL不支持READ UNCOMMITTED，最低级别是READ COMMITTED。

### 2.2 READ COMMITTED

**READ COMMITTED**：

每个语句看到的是语句开始时的快照。

**示例**：

```sql
-- READ COMMITTED隔离级别演示（带错误处理和性能测试）
DO $$
DECLARE
    balance1 NUMERIC;
    balance2 NUMERIC;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法演示READ COMMITTED隔离级别';
            RETURN;
        END IF;

        SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
        RAISE NOTICE '开始演示READ COMMITTED隔离级别';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        BEGIN;

        -- 第一次查询（快照1）
        SELECT balance INTO balance1 FROM accounts WHERE id = 1;

        IF FOUND THEN
            RAISE NOTICE '第一次查询（快照1）：balance=%', balance1;
        ELSE
            RAISE WARNING '账户 1 不存在';
            ROLLBACK;
            RETURN;
        END IF;

        -- 注意：其他事务在这里执行UPDATE并COMMIT
        -- 在READ COMMITTED级别下，第二次查询会看到新快照

        -- 第二次查询（快照2）
        SELECT balance INTO balance2 FROM accounts WHERE id = 1;

        IF FOUND THEN
            RAISE NOTICE '第二次查询（快照2）：balance=%（不可重复读）', balance2;

            IF balance1 != balance2 THEN
                RAISE NOTICE 'READ COMMITTED允许不可重复读：第一次查询=%，第二次查询=%', balance1, balance2;
            END IF;
        ELSE
            RAISE WARNING '账户 1 不存在（第二次查询）';
        END IF;

        COMMIT;
        RAISE NOTICE '事务提交成功';
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '事务失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 性能测试：READ COMMITTED查询
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT balance FROM accounts WHERE id = 1;
```

### 2.3 REPEATABLE READ

**REPEATABLE READ**：

整个事务看到的是事务开始时的快照。

**示例**：

```sql
-- REPEATABLE READ隔离级别演示（带错误处理和性能测试）
DO $$
DECLARE
    balance1 NUMERIC;
    balance2 NUMERIC;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法演示REPEATABLE READ隔离级别';
            RETURN;
        END IF;

        SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
        RAISE NOTICE '开始演示REPEATABLE READ隔离级别';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        BEGIN;

        -- 第一次查询（快照：事务开始时的快照）
        SELECT balance INTO balance1 FROM accounts WHERE id = 1;

        IF FOUND THEN
            RAISE NOTICE '第一次查询（快照：事务开始时的快照）：balance=%', balance1;
        ELSE
            RAISE WARNING '账户 1 不存在';
            ROLLBACK;
            RETURN;
        END IF;

        -- 注意：其他事务在这里执行UPDATE并COMMIT
        -- 在REPEATABLE READ级别下，第二次查询仍然看到事务开始时的快照

        -- 第二次查询（仍然是事务开始时的快照）
        SELECT balance INTO balance2 FROM accounts WHERE id = 1;

        IF FOUND THEN
            RAISE NOTICE '第二次查询（仍然是事务开始时的快照）：balance=%（可重复读）', balance2;

            IF balance1 != balance2 THEN
                RAISE WARNING 'REPEATABLE READ违反：第一次查询=%，第二次查询=%', balance1, balance2;
            ELSE
                RAISE NOTICE 'REPEATABLE READ保证可重复读：两次查询结果一致（balance=%）', balance1;
            END IF;
        ELSE
            RAISE WARNING '账户 1 不存在（第二次查询）';
        END IF;

        COMMIT;
        RAISE NOTICE '事务提交成功';
    EXCEPTION
        WHEN serialization_failure THEN
            ROLLBACK;
            RAISE WARNING '序列化冲突，事务需要重试';
            RAISE;
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '事务失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 性能测试：REPEATABLE READ查询
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT balance FROM accounts WHERE id = 1;
```

### 2.4 SERIALIZABLE

**SERIALIZABLE**：

最高隔离级别，通过串行化异常检测保证可串行化。

**示例**：

```sql
-- SERIALIZABLE隔离级别演示（带错误处理和性能测试）
DO $$
DECLARE
    account_balance NUMERIC;
    v_updated INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法演示SERIALIZABLE隔离级别';
            RETURN;
        END IF;

        SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
        RAISE NOTICE '开始演示SERIALIZABLE隔离级别（最高隔离级别）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        BEGIN;

        -- 查询余额（快照：事务开始时的快照）
        SELECT balance INTO account_balance FROM accounts WHERE id = 1;

        IF NOT FOUND THEN
            RAISE WARNING '账户 1 不存在';
            ROLLBACK;
            RETURN;
        END IF;

        RAISE NOTICE '查询余额（快照：事务开始时的快照）：balance=%', account_balance;

        -- 检查余额是否足够
        IF account_balance < 100 THEN
            RAISE WARNING '余额不足：当前余额=%，需要=100', account_balance;
            ROLLBACK;
            RETURN;
        END IF;

        -- 更新余额
        UPDATE accounts SET balance = balance - 100 WHERE id = 1;
        GET DIAGNOSTICS v_updated = ROW_COUNT;

        IF v_updated = 0 THEN
            RAISE WARNING '更新失败：账户 1 可能不存在或已被其他事务修改';
        ELSE
            RAISE NOTICE '更新成功：balance从%减少到%', account_balance, account_balance - 100;
        END IF;

        COMMIT;
        RAISE NOTICE '事务提交成功（可能检测到串行化冲突，如果检测到会中止事务）';
    EXCEPTION
        WHEN serialization_failure THEN
            ROLLBACK;
            RAISE WARNING '检测到串行化冲突，事务已中止，需要重试';
            RAISE;
        WHEN check_violation THEN
            ROLLBACK;
            RAISE WARNING '余额约束违反（余额不能为负）';
            RAISE;
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '事务失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 性能测试：SERIALIZABLE查询和更新
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT balance FROM accounts WHERE id = 1;
```

---

## 📊 第三部分：MVCC友好的SQL模式

### 3.1 避免长事务

**避免长事务**：

长事务会阻止VACUUM清理旧版本，导致表膨胀。

**不良实践**：

```sql
-- 不良：长事务（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN;
        -- 长时间处理...
        PERFORM (SELECT * FROM large_table LIMIT 1);
        -- 等待用户输入...
        UPDATE large_table SET status = 'processed' WHERE id = 1;
        COMMIT;  -- 事务时间过长
        RAISE NOTICE '长事务完成（不推荐：事务时间过长）';
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '长事务失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

**良好实践**：

```sql
-- 良好：短事务（带错误处理）
DO $$
DECLARE
    v_record large_table%ROWTYPE;
BEGIN
    BEGIN
        BEGIN;
        SELECT * INTO v_record FROM large_table WHERE id = 1;
        COMMIT;
        RAISE NOTICE '短事务1完成（查询）';
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '查询失败: %', SQLERRM;
            RAISE;
    END;

    -- 处理数据...

    BEGIN
        BEGIN;
        UPDATE large_table SET status = 'processed' WHERE id = 1;
        COMMIT;
        RAISE NOTICE '短事务2完成（更新）';
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '更新失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 3.2 合理使用锁

**合理使用锁**：

只在必要时使用显式锁，避免死锁。

**示例**：

```sql
-- 合理使用FOR UPDATE（带错误处理）
DO $$
DECLARE
    v_account accounts%ROWTYPE;
BEGIN
    BEGIN
        BEGIN;
        SELECT * INTO v_account FROM accounts WHERE id = 1 FOR UPDATE;  -- 锁定行

        IF NOT FOUND THEN
            ROLLBACK;
            RAISE WARNING '账户 1 不存在';
            RETURN;
        END IF;

        UPDATE accounts SET balance = balance - 100 WHERE id = 1;
        COMMIT;
        RAISE NOTICE '账户更新成功（使用FOR UPDATE锁定）';
    EXCEPTION
        WHEN lock_not_available THEN
            ROLLBACK;
            RAISE WARNING '无法获取锁，账户可能被其他事务锁定';
            RAISE;
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '更新失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 3.3 优化UPDATE模式

**优化UPDATE模式**：

避免不必要的UPDATE，使用HOT更新。

**示例**：

```sql
-- HOT更新（在同一页，带错误处理和性能测试）
DO $$
DECLARE
    v_updated INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法执行HOT更新';
            RETURN;
        END IF;

        BEGIN
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            UPDATE accounts SET balance = balance + 100 WHERE id = 1;

            GET DIAGNOSTICS v_updated = ROW_COUNT;
            IF v_updated = 0 THEN
                RAISE WARNING '账户 1 不存在，无法执行HOT更新';
            ELSE
                RAISE NOTICE 'HOT更新成功（在同一页，不更新索引）';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING 'HOT更新失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 非HOT更新（跨页，带错误处理和性能测试）
DO $$
DECLARE
    v_updated INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法执行非HOT更新';
            RETURN;
        END IF;

        BEGIN
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            UPDATE accounts SET balance = balance + 100, description = 'updated' WHERE id = 1;

            GET DIAGNOSTICS v_updated = ROW_COUNT;
            IF v_updated = 0 THEN
                RAISE WARNING '账户 1 不存在，无法执行非HOT更新';
            ELSE
                RAISE NOTICE '非HOT更新成功（跨页，需要更新索引）';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '非HOT更新失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 3.4 批量操作优化

**批量操作优化**：

使用批量操作减少事务开销。

**示例**：

```sql
-- 批量插入（带错误处理和性能测试）
DO $$
DECLARE
    v_inserted INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法执行批量插入';
            RETURN;
        END IF;

        BEGIN
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            INSERT INTO accounts (id, balance) VALUES
              (1, 1000),
              (2, 2000),
              (3, 3000);

            GET DIAGNOSTICS v_inserted = ROW_COUNT;
            RAISE NOTICE '批量插入成功，插入 % 条记录', v_inserted;
        EXCEPTION
            WHEN unique_violation THEN
                RAISE WARNING '批量插入失败：存在重复的id';
                RAISE;
            WHEN OTHERS THEN
                RAISE WARNING '批量插入失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 批量更新（带错误处理和性能测试）
DO $$
DECLARE
    v_updated INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法执行批量更新';
            RETURN;
        END IF;

        BEGIN
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            UPDATE accounts SET status = 'active'
            WHERE id IN (1, 2, 3);

            GET DIAGNOSTICS v_updated = ROW_COUNT;
            RAISE NOTICE '批量更新成功，更新 % 条记录', v_updated;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '批量更新失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 📊 第四部分：常见SQL模式与MVCC

### 4.1 计数器模式

**计数器模式**：

使用MVCC实现并发安全的计数器。

**示例**：

```sql
-- 计数器表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'counters') THEN
            RAISE NOTICE '表 counters 已存在';
        ELSE
            BEGIN
                CREATE TABLE counters (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    count INTEGER DEFAULT 0
                );
                RAISE NOTICE '计数器表 counters 创建成功';
            EXCEPTION
                WHEN duplicate_table THEN
                    RAISE WARNING '表 counters 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建计数器表失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 并发增加计数（带错误处理和性能测试）
DO $$
DECLARE
    v_updated INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'counters') THEN
            RAISE WARNING '表 counters 不存在，无法执行计数增加';
            RETURN;
        END IF;

        BEGIN
            BEGIN;

            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            UPDATE counters SET count = count + 1 WHERE name = 'visits';

            GET DIAGNOSTICS v_updated = ROW_COUNT;
            IF v_updated = 0 THEN
                RAISE WARNING '计数器 visits 不存在，无法增加计数';
                ROLLBACK;
                RETURN;
            END IF;

            COMMIT;
            RAISE NOTICE '计数增加成功（并发安全）';
        EXCEPTION
            WHEN OTHERS THEN
                ROLLBACK;
                RAISE WARNING '计数增加失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 4.2 乐观锁模式

**乐观锁模式**：

使用版本号实现乐观锁。

**示例**：

```sql
-- 带版本号的表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products') THEN
            RAISE NOTICE '表 products 已存在';
        ELSE
            BEGIN
                CREATE TABLE products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    price DECIMAL,
                    version INTEGER DEFAULT 0
                );
                RAISE NOTICE '带版本号的表 products 创建成功';
            EXCEPTION
                WHEN duplicate_table THEN
                    RAISE WARNING '表 products 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建表失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 乐观锁更新（带错误处理和性能测试）
DO $$
DECLARE
    v_version INTEGER;
    v_updated INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products') THEN
            RAISE WARNING '表 products 不存在，无法执行乐观锁更新';
            RETURN;
        END IF;

        BEGIN
            BEGIN;

            SELECT version INTO v_version FROM products WHERE id = 1;  -- version = 1

            IF NOT FOUND THEN
                ROLLBACK;
                RAISE WARNING '产品 1 不存在，无法执行乐观锁更新';
                RETURN;
            END IF;

            RAISE NOTICE '当前版本号: %', v_version;

            -- 处理...

            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            UPDATE products SET price = 200, version = version + 1
            WHERE id = 1 AND version = v_version;  -- 检查版本

            GET DIAGNOSTICS v_updated = ROW_COUNT;
            IF v_updated = 0 THEN
                ROLLBACK;
                RAISE WARNING '乐观锁更新失败：版本号不匹配（可能已被其他事务更新）';
                RETURN;
            END IF;

            COMMIT;
            RAISE NOTICE '乐观锁更新成功（版本号从 % 增加到 %）', v_version, v_version + 1;
        EXCEPTION
            WHEN OTHERS THEN
                ROLLBACK;
                RAISE WARNING '乐观锁更新失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 4.3 悲观锁模式

**悲观锁模式**：

使用FOR UPDATE实现悲观锁。

**示例**：

```sql
-- 悲观锁（带错误处理）
DO $$
DECLARE
    v_account accounts%ROWTYPE;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法执行悲观锁更新';
            RETURN;
        END IF;

        BEGIN
            BEGIN;

            SELECT * INTO v_account FROM accounts WHERE id = 1 FOR UPDATE;  -- 锁定

            IF NOT FOUND THEN
                ROLLBACK;
                RAISE WARNING '账户 1 不存在，无法执行悲观锁更新';
                RETURN;
            END IF;

            UPDATE accounts SET balance = balance - 100 WHERE id = 1;

            COMMIT;
            RAISE NOTICE '悲观锁更新成功（使用FOR UPDATE锁定）';
        EXCEPTION
            WHEN lock_not_available THEN
                ROLLBACK;
                RAISE WARNING '无法获取锁，账户可能被其他事务锁定';
                RAISE;
            WHEN OTHERS THEN
                ROLLBACK;
                RAISE WARNING '悲观锁更新失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 4.4 队列模式

**队列模式**：

使用MVCC实现并发安全的队列。

**示例**：

```sql
-- 队列表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'job_queue') THEN
            RAISE NOTICE '表 job_queue 已存在';
        ELSE
            BEGIN
                CREATE TABLE job_queue (
                    id SERIAL PRIMARY KEY,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW()
                );
                RAISE NOTICE '队列表 job_queue 创建成功';
            EXCEPTION
                WHEN duplicate_table THEN
                    RAISE WARNING '表 job_queue 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建队列表失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 获取任务（带错误处理和性能测试）
DO $$
DECLARE
    v_job job_queue%ROWTYPE;
    v_updated INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'job_queue') THEN
            RAISE WARNING '表 job_queue 不存在，无法获取任务';
            RETURN;
        END IF;

        BEGIN
            BEGIN;

            SELECT * INTO v_job FROM job_queue
            WHERE status = 'pending'
            ORDER BY created_at
            LIMIT 1
            FOR UPDATE SKIP LOCKED;  -- 跳过已锁定的行

            IF NOT FOUND THEN
                ROLLBACK;
                RAISE NOTICE '没有待处理的任务';
                RETURN;
            END IF;

            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            UPDATE job_queue SET status = 'processing' WHERE id = v_job.id;

            GET DIAGNOSTICS v_updated = ROW_COUNT;
            IF v_updated = 0 THEN
                ROLLBACK;
                RAISE WARNING '更新任务状态失败';
                RETURN;
            END IF;

            COMMIT;
            RAISE NOTICE '获取任务成功：id=%, status=processing', v_job.id;
        EXCEPTION
            WHEN lock_not_available THEN
                ROLLBACK;
                RAISE WARNING '无法获取锁，任务可能被其他事务锁定';
                RAISE;
            WHEN OTHERS THEN
                ROLLBACK;
                RAISE WARNING '获取任务失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 📊 第五部分：SQL性能优化与MVCC

### 5.1 查询优化

**查询优化**：

优化查询以减少MVCC开销。

**示例**：

```sql
-- 使用索引减少扫描（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法创建索引';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_accounts_status') THEN
            RAISE NOTICE '索引 idx_accounts_status 已存在';
        ELSE
            BEGIN
                CREATE INDEX idx_accounts_status ON accounts(status);
                RAISE NOTICE '索引 idx_accounts_status 创建成功';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '索引 idx_accounts_status 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建索引失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 使用索引查询（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM accounts WHERE status = 'active';  -- 使用索引

-- 避免全表扫描（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM accounts WHERE balance > 1000;  -- 可能需要全表扫描
```

### 5.2 索引优化

**索引优化**：

合理使用索引提高查询性能。

**示例**：

```sql
-- 复合索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法创建复合索引';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_accounts_user_status') THEN
            RAISE NOTICE '索引 idx_accounts_user_status 已存在';
        ELSE
            BEGIN
                CREATE INDEX idx_accounts_user_status ON accounts(user_id, status);
                RAISE NOTICE '复合索引 idx_accounts_user_status 创建成功';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '索引 idx_accounts_user_status 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建复合索引失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 覆盖索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法创建覆盖索引';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_accounts_covering') THEN
            RAISE NOTICE '索引 idx_accounts_covering 已存在';
        ELSE
            BEGIN
                CREATE INDEX idx_accounts_covering ON accounts(user_id) INCLUDE (balance);
                RAISE NOTICE '覆盖索引 idx_accounts_covering 创建成功';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '索引 idx_accounts_covering 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建覆盖索引失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 使用覆盖索引查询（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT user_id, balance FROM accounts WHERE user_id = 1;  -- 使用覆盖索引
```

### 5.3 事务优化

**事务优化**：

优化事务长度和范围。

**示例**：

```sql
-- 短事务（带错误处理和性能测试）
DO $$
DECLARE
    v_updated INTEGER;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'accounts') THEN
            RAISE WARNING '表 accounts 不存在，无法执行短事务';
            RETURN;
        END IF;

        BEGIN
            BEGIN;

            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            UPDATE accounts SET balance = balance - 100 WHERE id = 1;

            GET DIAGNOSTICS v_updated = ROW_COUNT;
            IF v_updated = 0 THEN
                ROLLBACK;
                RAISE WARNING '账户 1 不存在，无法执行更新';
                RETURN;
            END IF;

            COMMIT;
            RAISE NOTICE '短事务完成（推荐：事务时间短）';
        EXCEPTION
            WHEN OTHERS THEN
                ROLLBACK;
                RAISE WARNING '短事务失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 避免长事务
-- 不要在事务中等待用户输入
-- 不要在事务中执行长时间计算
```

---

## 📝 总结

### 核心结论

1. **MVCC影响SQL行为**：不同隔离级别下SQL行为不同
2. **MVCC友好的SQL模式**：避免长事务、合理使用锁
3. **常见SQL模式**：计数器、乐观锁、悲观锁、队列模式
4. **SQL性能优化**：查询优化、索引优化、事务优化

### 实践建议

1. **理解MVCC行为**：理解不同隔离级别下的SQL行为
2. **编写MVCC友好的SQL**：避免长事务、合理使用锁
3. **优化SQL性能**：使用索引、优化查询、优化事务
4. **监控MVCC影响**：监控版本链长度、表膨胀、VACUUM性能

---

**最后更新**: 2024年
**维护状态**: ✅ 已完成
