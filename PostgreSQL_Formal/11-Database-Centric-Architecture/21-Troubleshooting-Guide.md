# DCA故障排查与应急手册

> **文档类型**: 故障排查指南
> **适用对象**: DBA、运维工程师、开发人员
> **更新日期**: 2026-03-04

---

## 目录

- [DCA故障排查与应急手册](#dca故障排查与应急手册)
  - [目录](#目录)
  - [1. 故障快速诊断](#1-故障快速诊断)
    - [1.1 一键诊断脚本](#11-一键诊断脚本)
  - [2. 常见问题排查](#2-常见问题排查)
    - [2.1 连接问题](#21-连接问题)
      - [问题: 无法连接到数据库](#问题-无法连接到数据库)
      - [问题: 连接池耗尽](#问题-连接池耗尽)
    - [2.2 性能问题](#22-性能问题)
      - [问题: 查询缓慢](#问题-查询缓慢)
      - [问题: 死锁](#问题-死锁)
    - [2.3 存储过程问题](#23-存储过程问题)
      - [问题: 存储过程执行失败](#问题-存储过程执行失败)
    - [2.4 复制问题](#24-复制问题)
      - [问题: 复制延迟](#问题-复制延迟)
      - [问题: 复制槽满了](#问题-复制槽满了)
    - [2.5 磁盘空间问题](#25-磁盘空间问题)
  - [3. 应急处理方案](#3-应急处理方案)
    - [3.1 主库故障转移](#31-主库故障转移)
    - [3.2 数据库恢复](#32-数据库恢复)
    - [3.3 存储过程热修复](#33-存储过程热修复)
  - [4. 监控告警清单](#4-监控告警清单)
    - [4.1 关键指标阈值](#41-关键指标阈值)
    - [4.2 告警规则（Prometheus）](#42-告警规则prometheus)

---

## 1. 故障快速诊断

### 1.1 一键诊断脚本

```bash
#!/bin/bash
# ============================================
# diagnose.sh - 一键故障诊断脚本
# ============================================

echo "=========================================="
echo "PostgreSQL DCA 故障诊断"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "1. 检查PostgreSQL服务状态..."
systemctl status postgresql --no-pager -l

echo ""
echo "2. 检查进程..."
ps aux | grep postgres | grep -v grep

echo ""
echo "3. 检查端口监听..."
netstat -tlnp | grep 5432 || ss -tlnp | grep 5432

echo ""
echo "4. 检查磁盘空间..."
df -h | grep -E "(Filesystem|/var/lib/postgresql|/tmp)"

echo ""
echo "5. 检查内存使用..."
free -h

echo ""
echo "6. 检查连接数..."
psql -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

echo ""
echo "7. 检查锁等待..."
psql -c "
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.relation = blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
"

echo ""
echo "8. 检查复制状态..."
psql -c "SELECT * FROM pg_stat_replication;"

echo ""
echo "9. 检查长事务..."
psql -c "
SELECT
    pid,
    usename,
    state,
    NOW() - xact_start as duration,
    LEFT(query, 100) as query_preview
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND NOW() - xact_start > interval '1 minute'
ORDER BY xact_start;
"

echo ""
echo "10. 检查表膨胀..."
psql -c "
SELECT
    schemaname,
    relname,
    n_dead_tup,
    n_live_tup,
    ROUND(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 2) as bloat_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC
LIMIT 10;
"

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
```

---

## 2. 常见问题排查

### 2.1 连接问题

#### 问题: 无法连接到数据库

```bash
# 检查步骤

# 1. 检查服务是否运行
sudo systemctl status postgresql

# 2. 检查端口监听
sudo netstat -tlnp | grep 5432

# 3. 检查日志
tail -f /var/log/postgresql/postgresql-*.log

# 4. 检查防火墙
sudo iptables -L | grep 5432
sudo ufw status | grep 5432

# 5. 检查最大连接数
psql -c "SHOW max_connections;"
psql -c "SELECT count(*) FROM pg_stat_activity;"
```

#### 问题: 连接池耗尽

```sql
-- 检查连接池状态
SELECT
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle,
    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity;

-- 查看等待连接的查询
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    backend_start,
    state
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY backend_start;

-- 解决方案：增加连接池大小或清理空闲连接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < NOW() - INTERVAL '1 hour';
```

### 2.2 性能问题

#### 问题: 查询缓慢

```sql
-- 找出慢查询
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    NOW() - query_start as duration,
    query
FROM pg_stat_activity
WHERE state = 'active'
  AND NOW() - query_start > interval '5 seconds'
ORDER BY duration DESC;

-- 查看查询执行计划
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM orders WHERE user_id = 12345 ORDER BY created_at DESC;

-- 检查表统计信息是否过期
SELECT
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE last_analyze IS NULL
   OR last_analyze < NOW() - INTERVAL '7 days';

-- 手动更新统计信息
ANALYZE orders;
ANALYZE order_items;
```

#### 问题: 死锁

```sql
-- 查看死锁信息
SELECT
    bl.pid AS blocked_pid,
    bl.usename AS blocked_user,
    kl.pid AS blocking_pid,
    kl.usename AS blocking_user,
    a.query AS blocked_query,
    ka.query AS blocking_query
FROM pg_catalog.pg_locks bl
JOIN pg_catalog.pg_stat_activity a ON bl.pid = a.pid
JOIN pg_catalog.pg_locks kl ON kl.locktype = bl.locktype
    AND kl.relation = bl.relation
    AND kl.pid != bl.pid
JOIN pg_catalog.pg_stat_activity ka ON kl.pid = ka.pid
WHERE NOT bl.granted;

-- 终止阻塞进程（谨慎使用）
SELECT pg_terminate_backend(<blocking_pid>);
```

### 2.3 存储过程问题

#### 问题: 存储过程执行失败

```sql
-- 启用详细错误日志
SET log_min_messages = 'DEBUG1';

-- 检查存储过程定义
\df+ sp_order_create

-- 单步调试（使用RAISE NOTICE）
CREATE OR REPLACE PROCEDURE sp_order_create_debug(...)
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE NOTICE 'Step 1: Input validated';

    -- 检查库存
    RAISE NOTICE 'Step 2: Checking product_id %', v_product_id;
    SELECT * INTO v_product FROM products WHERE id = v_product_id;
    RAISE NOTICE 'Step 3: Product found, stock=%', v_product.stock_quantity;

    -- ... 其他逻辑
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error at step: %, SQLERRM: %', v_step, SQLERRM;
    RAISE;
END;
$$;

-- 查看存储过程依赖
SELECT
    p.proname as procedure_name,
    d.deptype,
    d.refobjid::regclass as referenced_object
FROM pg_proc p
JOIN pg_depend d ON p.oid = d.objid
WHERE p.proname = 'sp_order_create';
```

### 2.4 复制问题

#### 问题: 复制延迟

```sql
-- 检查复制延迟
SELECT
    client_addr as standby,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) as lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) as lag_size,
    reply_time
FROM pg_stat_replication;

-- 检查WAL积压
SELECT
    slot_name,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) as lag_bytes,
    active,
    restart_lsn
FROM pg_replication_slots;

-- 如果延迟过高，检查从库性能
-- 在从库上执行：
SELECT
    pg_last_wal_receive_lsn(),
    pg_last_wal_replay_lsn(),
    pg_last_xact_replay_timestamp(),
    NOW() - pg_last_xact_replay_timestamp() as lag;

-- 临时解决方案：增加WAL发送缓冲区
-- postgresql.conf:
-- wal_buffers = 128MB
```

#### 问题: 复制槽满了

```sql
-- 检查复制槽状态
SELECT
    slot_name,
    plugin,
    slot_type,
    database,
    active,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) as lag_bytes
FROM pg_replication_slots;

-- 如果复制槽不再需要，删除它
SELECT pg_drop_replication_slot('slot_name');

-- 如果复制槽正在使用但延迟高，检查消费者状态
```

### 2.5 磁盘空间问题

```sql
-- 检查数据库大小
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname))
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- 检查表大小
SELECT
    schemaname,
    relname,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    pg_size_pretty(pg_relation_size(relid)) as table_size,
    pg_size_pretty(pg_indexes_size(relid)) as index_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;

-- 检查WAL文件占用
SELECT
    pg_size_pretty(sum(size)) as total_wal_size
FROM pg_ls_waldir();

-- 清理策略
-- 1. 归档WAL文件
-- 2. 清理日志文件
-- 3. VACUUM FULL大表（注意：会锁定表）
```

---

## 3. 应急处理方案

### 3.1 主库故障转移

```bash
#!/bin/bash
# ============================================
# failover.sh - 手动故障转移脚本
# ============================================

STANDBY_HOST="standby1.internal"
NEW_PRIMARY="standby1"

echo "1. 检查主库状态..."
if pg_isready -h primary.internal -p 5432; then
    echo "主库仍在运行，确定要强制故障转移吗？(yes/no)"
    read confirm
    if [ "$confirm" != "yes" ]; then
        exit 1
    fi
fi

echo "2. 提升从库为主库..."
ssh postgres@${STANDBY_HOST} "
    /usr/lib/postgresql/18/bin/pg_ctl promote -D /var/lib/postgresql/18/main
"

echo "3. 更新应用配置..."
# 更新DNS/配置指向新的主库

echo "4. 检查新主库状态..."
psql -h ${STANDBY_HOST} -c "SELECT pg_is_in_recovery();"

echo "故障转移完成"
```

### 3.2 数据库恢复

```bash
#!/bin/bash
# ============================================
# restore.sh - 数据库恢复脚本
# ============================================

BACKUP_FILE="/backup/base_20260304_120000.tar.gz"
DATA_DIR="/var/lib/postgresql/18/main"

echo "1. 停止PostgreSQL..."
systemctl stop postgresql

echo "2. 备份当前数据（可选）..."
mv ${DATA_DIR} ${DATA_DIR}.corrupted.$(date +%Y%m%d)

echo "3. 解压备份..."
mkdir -p ${DATA_DIR}
tar -xzf ${BACKUP_FILE} -C ${DATA_DIR} --strip-components=1

echo "4. 设置权限..."
chown -R postgres:postgres ${DATA_DIR}
chmod 700 ${DATA_DIR}

echo "5. 创建recovery信号..."
touch ${DATA_DIR}/recovery.signal

echo "6. 配置恢复..."
cat >> ${DATA_DIR}/postgresql.conf <<EOF
restore_command = 'cp /backup/wal_archive/%f %p'
recovery_target_time = '2026-03-04 12:00:00'
recovery_target_action = 'promote'
EOF

echo "7. 启动PostgreSQL..."
systemctl start postgresql

echo "恢复完成"
```

### 3.3 存储过程热修复

```sql
-- 方法1: 使用事务包装修复
BEGIN;
    -- 1. 备份旧版本
    CREATE OR REPLACE PROCEDURE sp_order_create_backup(...)
    AS $$
    -- 复制旧代码
    $$;

    -- 2. 更新存储过程
    CREATE OR REPLACE PROCEDURE sp_order_create(...)
    AS $$
    -- 修复后的代码
    $$;

    -- 3. 测试
    CALL sp_order_create(...);

    -- 如果测试失败，回滚
    -- ROLLBACK;
COMMIT;

-- 方法2: 蓝绿部署
-- 创建新版本存储过程，逐步切换流量
CREATE OR REPLACE PROCEDURE sp_order_create_v2(...);

-- 应用层切换版本
```

---

## 4. 监控告警清单

### 4.1 关键指标阈值

| 指标 | 警告阈值 | 严重阈值 | 处理建议 |
|-----|---------|---------|---------|
| 连接数使用率 | > 70% | > 90% | 增加连接池或检查连接泄漏 |
| 复制延迟 | > 1MB | > 100MB | 检查网络或从库性能 |
| 查询响应时间(P99) | > 100ms | > 1s | 优化查询或增加索引 |
| 磁盘使用率 | > 80% | > 95% | 清理日志或扩容 |
| 死锁次数 | > 0/小时 | > 10/小时 | 检查事务逻辑 |
| 长事务 | > 1分钟 | > 5分钟 | 终止或优化事务 |
| 表膨胀率 | > 20% | > 50% | 执行VACUUM |

### 4.2 告警规则（Prometheus）

```yaml
# prometheus-alerts.yml
groups:
  - name: postgresql-alerts
    rules:
      - alert: PostgreSQLDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL实例宕机"

      - alert: PostgreSQLHighConnections
        expr: |
          pg_stat_activity_count{state="active"} / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL连接数过高"

      - alert: PostgreSQLReplicationLag
        expr: |
          pg_wal_lsn_diff(pg_stat_replication_pg_current_wal_lsn,
                         pg_stat_replication_pg_last_xact_replay_timestamp) > 100000000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL复制延迟过高"

      - alert: PostgreSQLSlowQueries
        expr: |
          rate(pg_stat_statements_total_time_sum[5m]) > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL慢查询增多"
```

---

**文档版本**: v1.0
**更新日期**: 2026-03-04
