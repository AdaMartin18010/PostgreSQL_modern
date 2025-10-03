# 分布式锁实战案例 — Distributed Locks with Advisory Locks

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **难度等级**：⭐⭐⭐⭐ 高级  
> **预计时间**：45-60分钟  
> **适合场景**：分布式系统、任务调度、资源互斥、幂等性保证

---

## 📋 案例目标

构建一个基于PostgreSQL Advisory Locks的分布式锁系统，包括：

1. ✅ Session级和Transaction级锁
2. ✅ 分布式任务调度
3. ✅ 资源互斥访问
4. ✅ 死锁检测与处理
5. ✅ 高可用锁服务

---

## 🎯 业务场景

**场景描述**：分布式任务调度系统

- **系统架构**：
  - 10个Worker节点
  - 100个定时任务
  - 每个任务需要独占执行
  - 任务执行时间：1秒-10分钟
- **需求**：
  - 保证任务不会被重复执行
  - 支持任务超时自动释放
  - Worker节点故障时自动恢复
  - 高并发场景下的锁竞争

---

## 🏗️ 架构设计

```text
Worker节点1-10
    ↓ 争抢任务锁
PostgreSQL Advisory Locks
    ↓ 锁管理
任务调度表
    ↓ 执行记录
任务执行日志
```

---

## 📦 1. Advisory Lock 基础

### 1.1 Session级锁 vs Transaction级锁

```sql
-- Session级锁（需要显式释放）
-- 获取锁
SELECT pg_advisory_lock(12345);

-- 尝试获取锁（非阻塞）
SELECT pg_try_advisory_lock(12345);  -- 返回 true/false

-- 释放锁
SELECT pg_advisory_unlock(12345);

-- Transaction级锁（事务结束自动释放）
BEGIN;
SELECT pg_advisory_xact_lock(12345);
-- 执行业务逻辑
COMMIT;  -- 自动释放锁
```

### 1.2 锁类型对比

| 锁类型 | 获取函数 | 释放方式 | 适用场景 |
|--------|---------|---------|---------|
| **Session级** | `pg_advisory_lock()` | 显式调用unlock | 长时间持有、跨事务 |
| **Transaction级** | `pg_advisory_xact_lock()` | 事务提交/回滚 | 短时间持有、事务内 |
| **共享锁** | `pg_advisory_lock_shared()` | unlock_shared | 读写分离 |

---

## 🗄️ 2. 数据模型设计

### 2.1 创建任务调度表

```sql
-- 任务定义表
CREATE TABLE scheduled_tasks (
    id serial PRIMARY KEY,
    task_name text NOT NULL UNIQUE,
    task_type text NOT NULL,
    schedule_cron text,
    is_enabled boolean DEFAULT true,
    last_run_at timestamptz,
    next_run_at timestamptz,
    created_at timestamptz DEFAULT now()
);

-- 任务执行日志表
CREATE TABLE task_execution_log (
    id bigserial PRIMARY KEY,
    task_id int NOT NULL REFERENCES scheduled_tasks(id),
    worker_id text NOT NULL,
    status text NOT NULL,  -- 'running', 'completed', 'failed'
    started_at timestamptz DEFAULT now(),
    completed_at timestamptz,
    error_message text,
    lock_id bigint
);

CREATE INDEX idx_task_log_task ON task_execution_log(task_id, started_at DESC);
CREATE INDEX idx_task_log_status ON task_execution_log(status, started_at DESC);

-- 插入示例任务
INSERT INTO scheduled_tasks (task_name, task_type, schedule_cron, next_run_at) VALUES
    ('数据同步任务', 'data_sync', '*/5 * * * *', now()),
    ('报表生成任务', 'report_gen', '0 * * * *', now()),
    ('数据清理任务', 'cleanup', '0 2 * * *', now());
```

---

## 🔒 3. 分布式锁实现

### 3.1 获取任务锁（基本版本）

```sql
-- 创建获取任务锁的函数
CREATE OR REPLACE FUNCTION try_acquire_task_lock(
    p_task_id int,
    p_worker_id text
)
RETURNS boolean AS $$
DECLARE
    v_lock_id bigint;
    v_acquired boolean;
BEGIN
    -- 使用task_id作为锁ID
    v_lock_id := p_task_id;
    
    -- 尝试获取Advisory Lock（非阻塞）
    v_acquired := pg_try_advisory_lock(v_lock_id);
    
    IF v_acquired THEN
        -- 记录任务执行日志
        INSERT INTO task_execution_log (task_id, worker_id, status, lock_id)
        VALUES (p_task_id, p_worker_id, 'running', v_lock_id);
        
        -- 更新任务的最后运行时间
        UPDATE scheduled_tasks
        SET last_run_at = now()
        WHERE id = p_task_id;
    END IF;
    
    RETURN v_acquired;
END;
$$ LANGUAGE plpgsql;

-- 测试获取锁
SELECT try_acquire_task_lock(1, 'worker-001');  -- 返回 true
SELECT try_acquire_task_lock(1, 'worker-002');  -- 返回 false（已被锁定）
```

### 3.2 释放任务锁

```sql
-- 创建释放任务锁的函数
CREATE OR REPLACE FUNCTION release_task_lock(
    p_task_id int,
    p_worker_id text,
    p_status text,
    p_error_message text DEFAULT NULL
)
RETURNS void AS $$
DECLARE
    v_lock_id bigint;
BEGIN
    v_lock_id := p_task_id;
    
    -- 更新任务执行日志
    UPDATE task_execution_log
    SET status = p_status,
        completed_at = now(),
        error_message = p_error_message
    WHERE task_id = p_task_id
      AND worker_id = p_worker_id
      AND status = 'running'
      AND completed_at IS NULL;
    
    -- 释放Advisory Lock
    PERFORM pg_advisory_unlock(v_lock_id);
    
    -- 更新下次运行时间（示例：5分钟后）
    IF p_status = 'completed' THEN
        UPDATE scheduled_tasks
        SET next_run_at = now() + interval '5 minutes'
        WHERE id = p_task_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 测试释放锁
SELECT release_task_lock(1, 'worker-001', 'completed');
```

---

## 🚀 4. 实战应用

### 4.1 Worker节点任务调度

```sql
-- Worker节点获取并执行任务的完整流程
CREATE OR REPLACE FUNCTION worker_fetch_and_execute_task(
    p_worker_id text
)
RETURNS TABLE (
    task_id int,
    task_name text,
    task_type text,
    acquired boolean
) AS $$
DECLARE
    v_task record;
BEGIN
    -- 查找待执行的任务
    FOR v_task IN
        SELECT id, task_name, task_type
        FROM scheduled_tasks
        WHERE is_enabled = true
          AND next_run_at <= now()
        ORDER BY next_run_at
        LIMIT 10
    LOOP
        -- 尝试获取锁
        IF try_acquire_task_lock(v_task.id, p_worker_id) THEN
            RETURN QUERY
            SELECT v_task.id, v_task.task_name, v_task.task_type, true;
            RETURN;  -- 获取到一个任务后立即返回
        END IF;
    END LOOP;
    
    -- 没有获取到任务
    RETURN QUERY
    SELECT NULL::int, NULL::text, NULL::text, false;
END;
$$ LANGUAGE plpgsql;

-- Worker节点调用示例
SELECT * FROM worker_fetch_and_execute_task('worker-001');
```

### 4.2 超时任务自动恢复

```sql
-- 创建任务超时检测函数
CREATE OR REPLACE FUNCTION check_and_recover_timeout_tasks(
    p_timeout_minutes int DEFAULT 30
)
RETURNS TABLE (
    task_id int,
    worker_id text,
    lock_released boolean
) AS $$
DECLARE
    v_timeout_task record;
    v_lock_id bigint;
BEGIN
    -- 查找超时任务
    FOR v_timeout_task IN
        SELECT 
            tel.task_id,
            tel.worker_id,
            tel.lock_id,
            tel.started_at
        FROM task_execution_log tel
        WHERE tel.status = 'running'
          AND tel.started_at < now() - (p_timeout_minutes || ' minutes')::interval
    LOOP
        -- 尝试释放锁（可能worker已释放）
        BEGIN
            PERFORM pg_advisory_unlock(v_timeout_task.lock_id);
            
            -- 更新任务状态为超时
            UPDATE task_execution_log
            SET status = 'failed',
                completed_at = now(),
                error_message = 'Task timeout after ' || p_timeout_minutes || ' minutes'
            WHERE id IN (
                SELECT id FROM task_execution_log
                WHERE task_id = v_timeout_task.task_id
                  AND worker_id = v_timeout_task.worker_id
                  AND status = 'running'
                LIMIT 1
            );
            
            RETURN QUERY
            SELECT v_timeout_task.task_id, v_timeout_task.worker_id, true;
        EXCEPTION
            WHEN OTHERS THEN
                -- 锁可能已经被释放
                RETURN QUERY
                SELECT v_timeout_task.task_id, v_timeout_task.worker_id, false;
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 定期执行超时检测（可使用pg_cron）
SELECT * FROM check_and_recover_timeout_tasks(30);
```

---

## 🔍 5. 锁监控与调试

### 5.1 查看当前持有的锁

```sql
-- 查看所有Advisory Locks
SELECT 
    locktype,
    database,
    classid,
    objid,
    objsubid,
    virtualtransaction,
    pid,
    mode,
    granted,
    fastpath
FROM pg_locks
WHERE locktype = 'advisory'
ORDER BY pid;

-- 查看任务锁的详细信息
SELECT 
    l.pid,
    l.objid AS lock_id,
    st.task_name,
    tel.worker_id,
    tel.started_at,
    now() - tel.started_at AS duration,
    l.mode,
    l.granted
FROM pg_locks l
JOIN task_execution_log tel ON l.objid = tel.lock_id
JOIN scheduled_tasks st ON tel.task_id = st.id
WHERE l.locktype = 'advisory'
  AND tel.status = 'running'
ORDER BY tel.started_at;
```

### 5.2 查看锁等待情况

```sql
-- 查看锁等待的进程
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    blocked_activity.application_name AS blocked_application
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

---

## 📊 6. 性能优化

### 6.1 使用两个参数的锁ID

```sql
-- 使用两个int4参数（更灵活）
SELECT pg_advisory_lock(1, 100);  -- classid=1, objid=100

-- 或者使用一个int8参数
SELECT pg_advisory_lock(hashtext('task:data_sync'));

-- 创建辅助函数生成锁ID
CREATE OR REPLACE FUNCTION get_task_lock_id(p_task_name text)
RETURNS bigint AS $$
BEGIN
    RETURN ('x' || substr(md5(p_task_name), 1, 16))::bit(64)::bigint;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 使用示例
SELECT get_task_lock_id('数据同步任务');
```

### 6.2 批量锁操作

```sql
-- 批量尝试获取多个任务锁
CREATE OR REPLACE FUNCTION try_acquire_multiple_tasks(
    p_worker_id text,
    p_max_tasks int DEFAULT 3
)
RETURNS TABLE (
    task_id int,
    task_name text,
    acquired boolean
) AS $$
DECLARE
    v_task record;
    v_acquired_count int := 0;
BEGIN
    FOR v_task IN
        SELECT id, task_name
        FROM scheduled_tasks
        WHERE is_enabled = true
          AND next_run_at <= now()
        ORDER BY next_run_at
        LIMIT p_max_tasks * 2  -- 多获取一些候选
    LOOP
        IF try_acquire_task_lock(v_task.id, p_worker_id) THEN
            v_acquired_count := v_acquired_count + 1;
            
            RETURN QUERY
            SELECT v_task.id, v_task.task_name, true;
            
            EXIT WHEN v_acquired_count >= p_max_tasks;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

---

## ✅ 7. 完整使用示例

```sql
-- 模拟完整的任务调度流程

-- Step 1: Worker-001获取任务
DO $$
DECLARE
    v_task record;
BEGIN
    -- 获取任务
    SELECT * INTO v_task
    FROM worker_fetch_and_execute_task('worker-001');
    
    IF v_task.acquired THEN
        RAISE NOTICE 'Worker-001 acquired task: % (ID: %)', v_task.task_name, v_task.task_id;
        
        -- 模拟任务执行
        PERFORM pg_sleep(2);
        
        -- 任务执行成功，释放锁
        PERFORM release_task_lock(v_task.task_id, 'worker-001', 'completed');
        
        RAISE NOTICE 'Worker-001 completed task: %', v_task.task_name;
    ELSE
        RAISE NOTICE 'Worker-001 没有获取到可用任务';
    END IF;
END $$;

-- Step 2: 查看执行日志
SELECT 
    st.task_name,
    tel.worker_id,
    tel.status,
    tel.started_at,
    tel.completed_at,
    tel.completed_at - tel.started_at AS duration
FROM task_execution_log tel
JOIN scheduled_tasks st ON tel.task_id = st.id
ORDER BY tel.started_at DESC
LIMIT 10;
```

---

## 📚 8. 最佳实践

### 8.1 锁管理

- ✅ 使用Transaction级锁处理短任务
- ✅ 使用Session级锁处理长任务
- ✅ 实现锁超时机制
- ✅ 记录锁的持有者信息

### 8.2 错误处理

- ✅ 捕获锁获取失败的情况
- ✅ 实现重试机制
- ✅ 记录锁竞争日志
- ✅ 监控锁等待时间

### 8.3 性能优化

- ✅ 使用非阻塞锁（pg_try_advisory_lock）
- ✅ 减少锁持有时间
- ✅ 避免死锁（按顺序获取锁）
- ✅ 合理设置锁粒度

### 8.4 监控运维

- ✅ 监控锁等待情况
- ✅ 定期清理超时任务
- ✅ 记录锁竞争指标
- ✅ 设置告警阈值

---

## 🎯 9. 练习任务

1. **基础练习**：
   - 实现基本的任务锁获取和释放
   - 测试多个Worker竞争同一任务
   - 实现任务执行日志记录

2. **进阶练习**：
   - 实现任务超时自动恢复
   - 创建任务调度监控视图
   - 实现锁竞争统计分析

3. **挑战任务**：
   - 构建完整的分布式任务调度系统
   - 实现任务优先级队列
   - 优化高并发场景的锁性能

---

## 📖 10. 参考资源

- PostgreSQL Advisory Locks: <https://www.postgresql.org/docs/17/explicit-locking.html#ADVISORY-LOCKS>
- pg_locks系统视图: <https://www.postgresql.org/docs/17/view-pg-locks.html>
- 分布式锁最佳实践: <https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html>

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**相关案例**：[时序数据](../timeseries_db/README.md) | [实时分析](../realtime_analytics/README.md)
