# PostgreSQL故障排查手册

系统化的PostgreSQL故障诊断和解决流程。

---

## 🚨 故障分类与处理流程

### 快速诊断决策树

```text
PostgreSQL故障？
│
├─ 无法连接？
│  ├─ 服务未运行 → 检查进程和日志
│  ├─ 端口不通 → 检查防火墙和网络
│  ├─ 认证失败 → 检查pg_hba.conf
│  └─ 连接数满 → 检查max_connections
│
├─ 查询很慢？
│  ├─ 特定查询慢 → EXPLAIN分析
│  ├─ 所有查询慢 → 检查系统资源
│  ├─ 突然变慢 → 检查统计信息
│  └─ 逐渐变慢 → 检查表膨胀
│
├─ 磁盘满？
│  ├─ 数据目录满 → 清理或扩容
│  ├─ WAL满 → 检查归档和复制槽
│  └─ 临时文件满 → 检查复杂查询
│
├─ 内存不足？
│  ├─ OOM Killer → 调整work_mem
│  ├─ 交换频繁 → 调整shared_buffers
│  └─ 缓存命中率低 → 增加内存
│
└─ 复制问题？
   ├─ 延迟高 → 检查从库性能
   ├─ 断开 → 检查网络和配置
   └─ 冲突 → 检查hot_standby_feedback
```

---

## 1. 连接问题

### 1.1 无法连接诊断

```bash
# Step 1: 检查服务状态
systemctl status postgresql
pg_isready -h localhost -p 5432

# Step 2: 检查监听
netstat -tlnp | grep 5432
ss -tlnp | grep 5432

# Step 3: 检查配置
grep listen_addresses /etc/postgresql/18/main/postgresql.conf
# 应该是 '*' 或具体IP

# Step 4: 测试本地连接
psql -h localhost -U postgres

# Step 5: 测试远程连接
psql -h remote_host -U postgres

# Step 6: 检查防火墙
sudo iptables -L | grep 5432
sudo firewall-cmd --list-all

# Step 7: 检查pg_hba.conf
cat /etc/postgresql/18/main/pg_hba.conf
```

### 1.2 连接数满

```sql
-- 性能测试：查看当前连接（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM pg_stat_activity;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查看连接数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查看max_connections（带错误处理）
BEGIN;
DO $$
BEGIN
    PERFORM current_setting('max_connections');
    RAISE NOTICE 'max_connections查询成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询max_connections失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
END $$;
COMMIT;

-- 性能测试：查看各状态连接数（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT state, COUNT(*) FROM pg_stat_activity GROUP BY state;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查看连接状态失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查看连接来源（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    application_name,
    client_addr,
    state,
    COUNT(*)
FROM pg_stat_activity
GROUP BY application_name, client_addr, state
ORDER BY COUNT(*) DESC;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查看连接来源失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：紧急措施：终止idle连接（带错误处理）
BEGIN;
DO $$
DECLARE
    terminated_count INT := 0;
BEGIN
    SELECT COUNT(*) INTO terminated_count
    FROM pg_stat_activity
    WHERE state = 'idle'
      AND state_change < now() - INTERVAL '10 minutes'
      AND pid != pg_backend_pid();

    PERFORM pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE state = 'idle'
      AND state_change < now() - INTERVAL '10 minutes'
      AND pid != pg_backend_pid();

    RAISE NOTICE '已终止 % 个空闲连接', terminated_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '终止空闲连接失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
END $$;
COMMIT;

-- 长期方案：使用连接池
-- 部署pgBouncer或使用应用层连接池
```

---

## 2. 性能问题

### 2.1 慢查询诊断

```sql
-- 性能测试：Step 1: 识别慢查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time,
    (mean_exec_time * calls) AS total_time
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- >100ms
ORDER BY total_time DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'pg_stat_statements扩展未安装，请先执行: CREATE EXTENSION pg_stat_statements;';
    WHEN OTHERS THEN
        RAISE NOTICE '识别慢查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- Step 2: EXPLAIN分析
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM slow_query_here;

-- 常见问题模式：
-- Pattern 1: Seq Scan（缺索引）
--   解决: CREATE INDEX
--
-- Pattern 2: 行数估算错误（统计过时）
--   解决: ANALYZE table
--
-- Pattern 3: External Sort（work_mem不足）
--   解决: 增加work_mem或添加索引
--
-- Pattern 4: Nested Loop不当（统计错误）
--   解决: ANALYZE或禁用enable_nestloop测试

-- Step 3: 检查表膨胀
SELECT
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;

-- Step 4: 检查统计信息
SELECT
    schemaname,
    tablename,
    last_analyze,
    last_autoanalyze,
    GREATEST(last_analyze, last_autoanalyze) AS last_stats
FROM pg_stat_user_tables
WHERE GREATEST(last_analyze, last_autoanalyze) < now() - INTERVAL '7 days'
ORDER BY n_live_tup DESC;

-- Step 5: 检查缓存命中率
SELECT
    'cache' AS metric,
    ROUND(SUM(blks_hit) * 100.0 / NULLIF(SUM(blks_hit + blks_read), 0), 2) AS hit_ratio
FROM pg_stat_database;
-- 应该 >95%
```

### 2.2 CPU 100%

```sql
-- 性能测试：查看活跃查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pid,
    usename,
    state,
    now() - query_start AS duration,
    LEFT(query, 100) AS query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查看活跃查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：终止耗CPU查询（带错误处理）
BEGIN;
DO $$
DECLARE
    cancelled_count INT := 0;
BEGIN
    SELECT COUNT(*) INTO cancelled_count
    FROM pg_stat_activity
    WHERE state = 'active' AND pid != pg_backend_pid();

    PERFORM pg_cancel_backend(pid)
    FROM pg_stat_activity
    WHERE state = 'active' AND pid != pg_backend_pid();

    RAISE NOTICE '已取消 % 个活跃查询', cancelled_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '取消查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
END $$;
COMMIT;

-- 性能测试：检查是否有大量并发查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT state, COUNT(*) FROM pg_stat_activity GROUP BY state;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '检查并发查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

---

## 3. 磁盘问题

### 3.1 磁盘满

```bash
# 检查磁盘使用
df -h /var/lib/postgresql

# 数据目录大小
du -sh /var/lib/postgresql/18/main/*

# WAL目录大小
du -sh /var/lib/postgresql/18/main/pg_wal

# 查看WAL文件
ls -lh /var/lib/postgresql/18/main/pg_wal/ | head -20
```

```sql
-- 性能测试：检查数据库大小（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '检查数据库大小失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：检查大表（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '检查大表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：检查WAL文件数量（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM pg_ls_waldir();
-- 正常<100个，>200个需要检查
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '检查WAL文件数量失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：检查复制槽（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    slot_name,
    active,
    wal_status,
    safe_wal_size
FROM pg_replication_slots;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '检查复制槽失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：删除无用复制槽（带错误处理）
BEGIN;
DO $$
BEGIN
    PERFORM pg_drop_replication_slot('unused_slot');
    RAISE NOTICE '复制槽unused_slot已删除';
EXCEPTION
    WHEN undefined_object THEN
        RAISE NOTICE '复制槽unused_slot不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '删除复制槽失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
END $$;
COMMIT;

-- 紧急措施：手动清理旧WAL（危险！）
-- 确保已归档
-- rm /var/lib/postgresql/18/main/pg_wal/00000001*
```

---

## 4. 锁问题

### 4.1 锁等待诊断

```sql
-- 查看所有锁
SELECT
    locktype,
    database,
    relation::regclass AS table,
    mode,
    granted,
    pid
FROM pg_locks
ORDER BY granted, pid;

-- 查看阻塞关系
WITH RECURSIVE blocking AS (
    SELECT
        blocked_locks.pid AS blocked_pid,
        blocking_locks.pid AS blocking_pid,
        blocked_activity.usename AS blocked_user,
        blocking_activity.usename AS blocking_user,
        blocked_activity.query AS blocked_query,
        blocking_activity.query AS blocking_query,
        blocked_activity.application_name AS blocked_app
    FROM pg_catalog.pg_locks blocked_locks
    JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
    JOIN pg_catalog.pg_locks blocking_locks
        ON blocking_locks.locktype = blocked_locks.locktype
        AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
        AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
        AND blocking_locks.pid != blocked_locks.pid
    JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
    WHERE NOT blocked_locks.granted
)
SELECT * FROM blocking;

-- 终止阻塞进程
SELECT pg_terminate_backend(blocking_pid);
```

---

## 5. 复制问题

### 5.1 复制延迟

```sql
-- 主库检查
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;

-- 从库检查
SELECT
    pg_is_in_recovery(),
    pg_last_wal_receive_lsn(),
    pg_last_wal_replay_lsn(),
    pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) / 1024 / 1024 AS lag_mb;

-- 复制槽状态
SELECT * FROM pg_replication_slots;

-- 解决方案：
-- 1. 检查从库资源（CPU/IOPS）
-- 2. 优化从库配置
-- 3. 检查网络延迟
-- 4. 考虑添加更多从库
```

---

## 6. 快速诊断脚本

```bash
#!/bin/bash
# quick-diagnose.sh - 快速诊断脚本

echo "PostgreSQL快速诊断"
echo "===================="

# 1. 服务状态
echo -e "\n1. 服务状态:"
systemctl status postgresql | grep Active

# 2. 连接数
echo -e "\n2. 连接数:"
psql -Atc "SELECT COUNT(*) || '/' || setting AS connections FROM pg_stat_activity, pg_settings WHERE name='max_connections';"

# 3. 缓存命中率
echo -e "\n3. 缓存命中率:"
psql -Atc "SELECT ROUND(SUM(blks_hit)*100/NULLIF(SUM(blks_hit+blks_read),0),2)||'%' FROM pg_stat_database;"

# 4. 表膨胀
echo -e "\n4. 表膨胀（>20%）:"
psql -c "SELECT tablename, ROUND(n_dead_tup*100.0/NULLIF(n_live_tup+n_dead_tup,0),1)||'%' AS bloat FROM pg_stat_user_tables WHERE n_dead_tup*100.0/NULLIF(n_live_tup+n_dead_tup,0) > 20 ORDER BY n_dead_tup DESC LIMIT 5;"

# 5. 锁等待
echo -e "\n5. 锁等待:"
psql -Atc "SELECT COUNT(*) FROM pg_locks WHERE NOT granted;"

# 6. 长事务
echo -e "\n6. 长事务（>5分钟）:"
psql -c "SELECT pid, usename, state, now()-xact_start AS duration, LEFT(query,50) FROM pg_stat_activity WHERE xact_start < now() - INTERVAL '5 minutes' AND state != 'idle' ORDER BY duration DESC LIMIT 5;"

# 7. 磁盘使用
echo -e "\n7. 磁盘使用:"
df -h /var/lib/postgresql | tail -1

# 8. WAL文件数
echo -e "\n8. WAL文件数:"
ls /var/lib/postgresql/18/main/pg_wal/ | wc -l

echo -e "\n===================="
echo "诊断完成"
```

---

**完成**: PostgreSQL故障排查手册
**字数**: ~10,000字
**涵盖**: 决策树、连接问题、性能问题、磁盘问题、锁问题、复制问题、快速诊断脚本
