# PostgreSQL 17 监控指标体系

> **版本**：PostgreSQL 17  
> **最后更新**：2025-10-03  
> **适用场景**：生产环境监控、性能调优、故障诊断

---

## 📋 目录

- [1. 监控指标概述](#1-监控指标概述)
- [2. 核心监控指标（6大类）](#2-核心监控指标6大类)
  - [2.1 连接与会话](#21-连接与会话)
  - [2.2 事务与性能](#22-事务与性能)
  - [2.3 锁与并发](#23-锁与并发)
  - [2.4 存储与维护](#24-存储与维护)
  - [2.5 复制与高可用](#25-复制与高可用)
  - [2.6 资源使用](#26-资源使用)
- [3. 告警阈值建议](#3-告警阈值建议)
- [4. PostgreSQL 17新增监控点](#4-postgresql-17新增监控点)
- [5. 监控工具集成](#5-监控工具集成)

---

## 1. 监控指标概述

### 监控目标

| 目标 | 说明 | 关键指标 |
|------|------|---------|
| **可用性** | 服务是否正常运行 | 连接成功率、主从状态 |
| **性能** | 查询响应时间 | TPS/QPS、平均查询时间、P95/P99延迟 |
| **容量** | 资源使用情况 | 连接数、表大小、WAL大小 |
| **健康度** | 系统健康状况 | 锁等待、长事务、表膨胀率 |

### 监控数据来源

```sql
-- 1. 系统视图（pg_stat_*）
SELECT * FROM pg_stat_database;   -- 数据库统计
SELECT * FROM pg_stat_user_tables; -- 表统计
SELECT * FROM pg_stat_activity;    -- 活动会话

-- 2. 系统函数
SELECT pg_database_size('mydb');  -- 数据库大小
SELECT pg_relation_size('mytable'); -- 表大小

-- 3. 扩展
CREATE EXTENSION pg_stat_statements; -- 查询统计
CREATE EXTENSION pgstattuple;        -- 表膨胀分析
```

---

## 2. 核心监控指标（6大类）

### 2.1 连接与会话

#### 2.1.1 活跃连接数

**指标名称**：`active_connections`  
**数据源**：`pg_stat_activity`  
**SQL查询**：

```sql
SELECT 
    COUNT(*) FILTER (WHERE state != 'idle') AS active_connections,
    COUNT(*) AS total_connections,
    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') AS max_connections,
    ROUND(100.0 * COUNT(*) / (SELECT setting::int FROM pg_settings WHERE name = 'max_connections'), 2) AS connection_usage_pct
FROM pg_stat_activity;
```

**告警阈值**：

- ⚠️ **警告**：连接使用率 > 80%
- 🔴 **严重**：连接使用率 > 95%

---

#### 2.1.2 IDLE IN TRANSACTION会话

**指标名称**：`idle_in_transaction_sessions`  
**风险**：长时间持有锁，阻塞VACUUM，导致表膨胀  
**SQL查询**：

```sql
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    xact_start,
    EXTRACT(EPOCH FROM (NOW() - xact_start)) AS idle_duration_seconds,
    query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND EXTRACT(EPOCH FROM (NOW() - xact_start)) > 60  -- 超过1分钟
ORDER BY xact_start;
```

**告警阈值**：

- ⚠️ **警告**：存在超过5分钟的IDLE IN TRANSACTION会话
- 🔴 **严重**：存在超过10分钟的IDLE IN TRANSACTION会话

**处理建议**：

```sql
-- 终止长时间空闲的事务
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle in transaction' 
  AND EXTRACT(EPOCH FROM (NOW() - xact_start)) > 600;
```

---

#### 2.1.3 连接池状态（PgBouncer）

**指标名称**：`pgbouncer_pool_stats`  
**监控内容**：

- 客户端连接数
- 服务端连接数
- 等待连接的客户端
- 活跃查询数

**PgBouncer监控SQL**：

```sql
-- 在PgBouncer admin数据库执行
SHOW POOLS;
SHOW STATS;
SHOW CLIENTS;
```

---

### 2.2 事务与性能

#### 2.2.1 TPS/QPS（事务吞吐量）

**指标名称**：`transactions_per_second`  
**数据源**：`pg_stat_database`  
**SQL查询**：

```sql
SELECT 
    datname,
    xact_commit + xact_rollback AS total_transactions,
    xact_commit AS committed_transactions,
    xact_rollback AS rolled_back_transactions,
    ROUND(100.0 * xact_rollback / NULLIF(xact_commit + xact_rollback, 0), 2) AS rollback_ratio_pct
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1', 'postgres')
ORDER BY total_transactions DESC;
```

**计算TPS**：

```sql
-- 方法1：通过pg_stat_database计算增量
SELECT 
    datname,
    (xact_commit + xact_rollback) AS current_txn,
    -- 需要与上一次采样对比计算TPS
    -- TPS = (current_txn - previous_txn) / time_interval
FROM pg_stat_database;

-- 方法2：使用Prometheus的rate()函数
-- rate(pg_stat_database_xact_commit{datname="mydb"}[1m])
```

**告警阈值**：

- ⚠️ **警告**：TPS突然下降50%
- 🔴 **严重**：TPS下降80%或回滚率 > 10%

---

#### 2.2.2 平均查询时间

**指标名称**：`average_query_time_ms`  
**数据源**：`pg_stat_statements`（需要安装扩展）  
**SQL查询**：

```sql
-- TOP 10慢查询（按平均执行时间）
SELECT 
    query,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms,
    ROUND(max_exec_time::numeric, 2) AS max_time_ms,
    ROUND(stddev_exec_time::numeric, 2) AS stddev_time_ms,
    ROUND(total_exec_time::numeric, 2) AS total_time_ms,
    ROUND(100.0 * total_exec_time / SUM(total_exec_time) OVER(), 2) AS time_pct
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**告警阈值**：

- ⚠️ **警告**：平均查询时间 > 100ms
- 🔴 **严重**：平均查询时间 > 1000ms

---

#### 2.2.3 慢查询日志

**配置参数**：

```ini
# postgresql.conf
log_min_duration_statement = 1000  # 记录超过1秒的查询（单位：毫秒）
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'none'  # 不记录所有语句（避免日志过大）
```

**分析慢查询日志**：

```bash
# 使用pgBadger分析慢查询日志
pgbadger -f stderr /var/log/postgresql/postgresql-*.log -o /tmp/pgbadger_report.html

# 查看最慢的10个查询
grep "duration:" /var/log/postgresql/postgresql-*.log | sort -t: -k3 -nr | head -10
```

---

### 2.3 锁与并发

#### 2.3.1 锁等待时间

**指标名称**：`lock_wait_time`  
**SQL查询**：

```sql
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    blocked_activity.application_name AS blocked_app,
    blocking_activity.application_name AS blocking_app,
    EXTRACT(EPOCH FROM (NOW() - blocked_activity.query_start)) AS block_duration_seconds
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
WHERE NOT blocked_locks.granted
ORDER BY block_duration_seconds DESC;
```

**告警阈值**：

- ⚠️ **警告**：锁等待 > 30秒
- 🔴 **严重**：锁等待 > 60秒

---

#### 2.3.2 死锁频率

**指标名称**：`deadlock_count`  
**SQL查询**：

```sql
SELECT 
    datname,
    deadlocks,
    deadlocks - COALESCE(LAG(deadlocks) OVER (PARTITION BY datname ORDER BY stats_reset), 0) AS deadlocks_since_last_reset
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY deadlocks DESC;
```

**告警阈值**：

- ⚠️ **警告**：每小时死锁 > 10次
- 🔴 **严重**：每小时死锁 > 50次

---

#### 2.3.3 长事务

**指标名称**：`long_running_transactions`  
**风险**：阻塞VACUUM，导致表膨胀；持有锁，影响并发  
**SQL查询**：

```sql
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    xact_start,
    EXTRACT(EPOCH FROM (NOW() - xact_start)) AS transaction_duration_seconds,
    query_start,
    EXTRACT(EPOCH FROM (NOW() - query_start)) AS query_duration_seconds,
    LEFT(query, 100) AS query_preview
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND EXTRACT(EPOCH FROM (NOW() - xact_start)) > 300  -- 超过5分钟
ORDER BY xact_start;
```

**告警阈值**：

- ⚠️ **警告**：存在超过5分钟的事务
- 🔴 **严重**：存在超过10分钟的事务

---

### 2.4 存储与维护

#### 2.4.1 表膨胀率

**指标名称**：`table_bloat_ratio`  
**数据源**：`pgstattuple`扩展  
**SQL查询**：

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS pgstattuple;

-- 检查TOP 10膨胀表
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    n_dead_tup,
    n_live_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio_pct,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_live_tup + n_dead_tup > 0
ORDER BY dead_ratio_pct DESC NULLS LAST
LIMIT 10;
```

**告警阈值**：

- ⚠️ **警告**：死元组比例 > 30%
- 🔴 **严重**：死元组比例 > 50%

**处理建议**：

```sql
-- 执行VACUUM
VACUUM ANALYZE schema.table_name;

-- 如果膨胀严重（>50%），考虑VACUUM FULL（需要锁表）
VACUUM FULL schema.table_name;
```

---

#### 2.4.2 VACUUM进度

**指标名称**：`vacuum_progress`  
**数据源**：`pg_stat_progress_vacuum`（PostgreSQL 9.6+）  
**SQL查询**：

```sql
SELECT 
    pid,
    datname,
    relid::regclass AS table_name,
    phase,
    heap_blks_total,
    heap_blks_scanned,
    heap_blks_vacuumed,
    ROUND(100.0 * heap_blks_scanned / NULLIF(heap_blks_total, 0), 2) AS scan_progress_pct,
    index_vacuum_count,
    max_dead_tuples,
    num_dead_tuples
FROM pg_stat_progress_vacuum;
```

---

#### 2.4.3 WAL生成速度

**指标名称**：`wal_generation_rate`  
**数据源**：`pg_stat_wal`（PostgreSQL 14+）  
**SQL查询**：

```sql
SELECT 
    wal_records,
    wal_fpi,  -- Full Page Images
    wal_bytes,
    pg_size_pretty(wal_bytes) AS wal_size,
    wal_buffers_full,
    wal_write,
    wal_sync,
    wal_write_time,
    wal_sync_time,
    stats_reset
FROM pg_stat_wal;
```

**告警阈值**：

- ⚠️ **警告**：WAL生成速度 > 100MB/s（持续5分钟）
- 🔴 **严重**：WAL生成速度 > 500MB/s

---

### 2.5 复制与高可用

#### 2.5.1 复制延迟

**指标名称**：`replication_lag`  
**数据源**：`pg_stat_replication`（主库）  
**SQL查询**：

```sql
-- 在主库执行
SELECT 
    application_name,
    client_addr,
    client_hostname,
    state,
    sync_state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replication_lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) AS replication_lag,
    EXTRACT(EPOCH FROM (NOW() - replay_lsn_时间)) AS replication_lag_seconds
FROM pg_stat_replication;
```

**告警阈值**：

- ⚠️ **警告**：复制延迟 > 10MB 或 > 10秒
- 🔴 **严重**：复制延迟 > 100MB 或 > 60秒

---

#### 2.5.2 复制槽使用

**指标名称**：`replication_slot_status`  
**SQL查询**：

```sql
SELECT 
    slot_name,
    slot_type,
    database,
    active,
    xmin,
    catalog_xmin,
    restart_lsn,
    confirmed_flush_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_wal_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal
FROM pg_replication_slots;
```

**告警阈值**：

- ⚠️ **警告**：复制槽保留WAL > 10GB
- 🔴 **严重**：复制槽保留WAL > 50GB 或槽inactive

---

### 2.6 资源使用

#### 2.6.1 缓存命中率

**指标名称**：`cache_hit_ratio`  
**SQL查询**：

```sql
SELECT 
    sum(heap_blks_read) AS heap_read,
    sum(heap_blks_hit) AS heap_hit,
    sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0) AS cache_hit_ratio
FROM pg_statio_user_tables;
```

**目标**：缓存命中率 > 99%

---

## 3. 告警阈值建议

| 指标 | 警告阈值 | 严重阈值 | 说明 |
|------|---------|---------|------|
| **连接数使用率** | >80% | >95% | 接近max_connections限制 |
| **复制延迟** | >10MB或>10s | >100MB或>60s | 主从数据不一致风险 |
| **表膨胀率** | >30% | >50% | 需要VACUUM FULL |
| **长事务** | >5分钟 | >10分钟 | 阻塞VACUUM，导致膨胀 |
| **锁等待** | >30秒 | >60秒 | 影响用户体验 |
| **死锁频率** | >10次/小时 | >50次/小时 | 应用逻辑问题 |
| **IDLE IN TRANSACTION** | >5分钟 | >10分钟 | 持有锁，影响并发 |
| **缓存命中率** | <95% | <90% | 内存不足或查询低效 |
| **WAL保留** | >10GB | >50GB | 磁盘空间风险 |
| **TPS下降** | -50% | -80% | 性能严重降级 |

---

## 4. PostgreSQL 17新增监控点

### 4.1 JSON性能监控

```sql
-- 监控JSON_TABLE函数使用情况
SELECT 
    query,
    calls,
    mean_exec_time
FROM pg_stat_statements
WHERE query LIKE '%JSON_TABLE%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### 4.2 VACUUM内存使用（PG 17优化）

```sql
-- 查看VACUUM内存配置
SELECT name, setting, unit, context
FROM pg_settings
WHERE name LIKE '%vacuum%mem%';

-- 监控VACUUM内存使用（需要配合操作系统工具）
SELECT * FROM pg_stat_progress_vacuum;
```

### 4.3 逻辑复制监控（PG 17增强）

```sql
-- 监控逻辑复制订阅状态
SELECT 
    subname,
    pid,
    relid,
    received_lsn,
    last_msg_send_time,
    last_msg_receipt_time,
    latest_end_lsn,
    latest_end_time
FROM pg_stat_subscription;
```

---

## 5. 监控工具集成

### 5.1 Prometheus + Grafana

**安装postgres_exporter**：

```bash
# Docker方式
docker run -d \
  --name postgres_exporter \
  -p 9187:9187 \
  -e DATA_SOURCE_NAME="postgresql://user:password@postgres:5432/dbname?sslmode=disable" \
  prometheuscommunity/postgres-exporter
```

**关键指标**：

- `pg_stat_database_xact_commit`
- `pg_stat_database_xact_rollback`
- `pg_stat_replication_lag`
- `pg_stat_activity_count`

---

### 5.2 pgAdmin

**启用统计信息**：

1. 打开pgAdmin
2. 右键数据库 → Properties → Statistics
3. 查看Dashboard → Server Activity

---

### 5.3 自定义监控脚本

参见：[monitoring_queries.sql](monitoring_queries.sql)（30+监控SQL）

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**相关文档**：

- [监控SQL查询](monitoring_queries.sql)
- [告警规则](alerting_rules.yml)
- [运维手册](README.md)
