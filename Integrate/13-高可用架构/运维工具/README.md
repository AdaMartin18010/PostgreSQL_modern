---

> **📋 文档来源**: `PostgreSQL\06-运维实践\运维工具\README.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL运维工具集

## 目录

- [常用运维工具](#常用运维工具)
- [自动化脚本](#自动化脚本)
- [实用工具集](#实用工具集)

## 常用运维工具

### 1. pgAdmin

**功能**: PostgreSQL图形化管理工具

**安装**:

```bash
# Ubuntu/Debian
sudo apt-get install pgadmin4

# 或使用Docker
docker run -p 80:80 \
    -e PGADMIN_DEFAULT_EMAIL=admin@example.com \
    -e PGADMIN_DEFAULT_PASSWORD=admin \
    dpage/pgadmin4
```

**使用场景**:

- 数据库管理
- 查询执行
- 性能监控
- 备份恢复

### 2. pg_top

**功能**: PostgreSQL进程监控工具（类似top）

**安装**:

```bash
# Ubuntu/Debian
sudo apt-get install pgtop

# 或从源码编译
git clone https://github.com/zalando/pg_top.git
cd pg_top
make && sudo make install
```

**使用**:

```bash
pg_top -h localhost -U postgres -d mydb
```

### 3. pg_stat_statements

**功能**: 查询性能统计扩展

**安装**:

```sql
-- 启用扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 配置（postgresql.conf）
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
pg_stat_statements.max = 10000
```

**使用**:

```sql
-- 查看Top SQL
SELECT
    queryid,
    LEFT(query, 100) as query_preview,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

### 4. pgBadger

**功能**: PostgreSQL日志分析工具

**安装**:

```bash
# Ubuntu/Debian
sudo apt-get install pgbadger

# 或使用Perl模块
cpan App::pgBadger
```

**使用**:

```bash
# 分析日志
pgbadger /var/log/postgresql/postgresql-*.log -o report.html

# 实时分析
tail -f /var/log/postgresql/postgresql.log | pgbadger -f syslog -o report.html
```

### 5. pg_activity

**功能**: PostgreSQL活动监控工具

**安装**:

```bash
pip install pg_activity
```

**使用**:

```bash
pg_activity -h localhost -U postgres -d mydb
```

### 6. pgbench

**功能**: PostgreSQL基准测试工具

**使用**:

```bash
# 初始化测试数据
pgbench -i -s 100 mydb  # -s 100表示100倍规模

# 运行基准测试
pgbench -c 10 -j 2 -T 60 mydb  # 10个客户端，2个线程，运行60秒
```

### 7. pg_repack

**功能**: 在线表重建工具（减少表膨胀）

**安装**:

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-14-repack

# 或从源码编译
git clone https://github.com/reorg/pg_repack.git
cd pg_repack
make && sudo make install
```

**使用**:

```sql
-- 启用扩展
CREATE EXTENSION IF NOT EXISTS pg_repack;

-- 重建表
SELECT repack.repack_table('public.orders');
```

### 8. pgBackRest

**功能**: PostgreSQL备份恢复工具

**安装**:

```bash
# Ubuntu/Debian
sudo apt-get install pgbackrest

# 或从源码编译
git clone https://github.com/pgbackrest/pgbackrest.git
cd pgbackrest
make && sudo make install
```

**配置**:

```ini
# /etc/pgbackrest.conf
[global]
repo1-path=/backup/pgbackrest
repo1-retention-full=2

[mydb]
pg1-path=/var/lib/postgresql/data
```

**使用**:

```bash
# 全量备份
pgbackrest --stanza=mydb --type=full backup

# 增量备份
pgbackrest --stanza=mydb --type=incr backup

# 恢复
pgbackrest --stanza=mydb restore
```

## 自动化脚本

### 1. 数据库健康检查脚本

```bash
#!/bin/bash
# health_check.sh

DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="postgres"
DB_USER="postgres"

echo "=== PostgreSQL健康检查 ==="

# 1. 连接检查
if ! psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ 数据库连接失败"
    exit 1
else
    echo "✅ 数据库连接正常"
fi

# 2. 检查复制延迟（如果有复制）
REPLICATION_LAG=$(psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -t -c "
    SELECT pg_wal_lsn_diff(
        pg_current_wal_lsn(),
        pg_last_wal_replay_lsn()
    );
" 2>/dev/null)

if [ ! -z "${REPLICATION_LAG}" ] && [ "${REPLICATION_LAG}" -gt 1073741824 ]; then
    echo "⚠️  复制延迟: ${REPLICATION_LAG} bytes (>1GB)"
else
    echo "✅ 复制延迟正常"
fi

# 3. 检查死元组
DEAD_TUPLES=$(psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -t -c "
    SELECT SUM(n_dead_tup) FROM pg_stat_user_tables;
" 2>/dev/null)

if [ "${DEAD_TUPLES}" -gt 1000000 ]; then
    echo "⚠️  死元组过多: ${DEAD_TUPLES}"
else
    echo "✅ 死元组正常"
fi

# 4. 检查连接数
CONNECTIONS=$(psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -t -c "
    SELECT COUNT(*) FROM pg_stat_activity;
" 2>/dev/null)

MAX_CONNECTIONS=$(psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -t -c "
    SELECT setting::int FROM pg_settings WHERE name = 'max_connections';
" 2>/dev/null)

CONNECTION_PERCENT=$((CONNECTIONS * 100 / MAX_CONNECTIONS))

if [ "${CONNECTION_PERCENT}" -gt 80 ]; then
    echo "⚠️  连接数使用率: ${CONNECTION_PERCENT}% (>80%)"
else
    echo "✅ 连接数正常: ${CONNECTIONS}/${MAX_CONNECTIONS}"
fi

echo "=== 健康检查完成 ==="
```

### 2. 自动VACUUM监控脚本

```bash
#!/bin/bash
# vacuum_monitor.sh

DB_HOST="localhost"
DB_NAME="postgres"
DB_USER="postgres"

# 检查需要VACUUM的表
psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} <<EOF
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    CASE
        WHEN n_live_tup > 0 THEN n_dead_tup::float / n_live_tup * 100
        ELSE 0
    END AS dead_tuple_percent,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC
LIMIT 20;
EOF

# 手动触发VACUUM（如果需要）
# psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -c "VACUUM ANALYZE orders;"
```

### 3. 慢查询监控脚本

```bash
#!/bin/bash
# slow_query_monitor.sh

DB_HOST="localhost"
DB_NAME="postgres"
DB_USER="postgres"
THRESHOLD=1000  # 1秒

psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} <<EOF
SELECT
    queryid,
    LEFT(query, 200) as query_preview,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > ${THRESHOLD}
ORDER BY total_exec_time DESC
LIMIT 20;
EOF
```

### 4. 备份验证脚本

```bash
#!/bin/bash
# backup_verify.sh

BACKUP_PATH=$1

if [ -z "${BACKUP_PATH}" ]; then
    echo "Usage: $0 <backup_path>"
    exit 1
fi

echo "=== 备份验证 ==="

# 1. 检查备份目录
if [ ! -d "${BACKUP_PATH}" ]; then
    echo "❌ 备份目录不存在: ${BACKUP_PATH}"
    exit 1
fi

# 2. 检查备份清单
if [ ! -f "${BACKUP_PATH}/backup_manifest" ]; then
    echo "⚠️  备份清单文件不存在"
else
    echo "✅ 备份清单存在"
fi

# 3. 检查WAL文件
if [ -d "${BACKUP_PATH}/pg_wal" ]; then
    WAL_COUNT=$(ls -1 ${BACKUP_PATH}/pg_wal/*.wal 2>/dev/null | wc -l)
    echo "✅ WAL文件数量: ${WAL_COUNT}"
else
    echo "⚠️  WAL目录不存在"
fi

# 4. 检查备份大小
BACKUP_SIZE=$(du -sh ${BACKUP_PATH} | cut -f1)
echo "✅ 备份大小: ${BACKUP_SIZE}"

echo "=== 备份验证完成 ==="
```

## 实用工具集

### 1. 数据库大小统计

```sql
-- 数据库大小
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- 表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
```

### 2. 索引使用统计

```sql
-- 未使用的索引
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 3. 锁等待分析

```sql
-- 锁等待查询
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

### 4. 复制状态监控

```sql
-- 复制延迟
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replication_lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS replication_lag
FROM pg_stat_replication;
```

### 5. 性能指标汇总

```sql
-- 创建性能指标视图
CREATE OR REPLACE VIEW performance_summary AS
SELECT
    NOW() as check_time,
    (SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active') as active_queries,
    (SELECT AVG(mean_exec_time) FROM pg_stat_statements WHERE calls > 100) as avg_query_time,
    (SELECT SUM(blks_hit)::float / NULLIF(SUM(blks_hit) + SUM(blks_read), 0) * 100
     FROM pg_stat_database WHERE datname = current_database()) as cache_hit_ratio,
    (SELECT COUNT(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock') as lock_waits,
    (SELECT SUM(n_dead_tup) FROM pg_stat_user_tables) as total_dead_tuples;

-- 查询性能指标
SELECT * FROM performance_summary;
```

---

## 工具选择指南

### 按场景选择工具

| 场景 | 推荐工具 | 说明 |
|------|---------|------|
| 图形化管理 | pgAdmin | 适合日常管理和查询 |
| 实时监控 | pg_top, pg_activity | 适合实时查看数据库状态 |
| 日志分析 | pgBadger | 适合分析慢查询和错误日志 |
| 性能测试 | pgbench | 适合压力测试和基准测试 |
| 表重组 | pg_repack | 适合在线重组表，减少锁时间 |
| 备份恢复 | pgBackRest | 适合企业级备份恢复方案 |
| 查询统计 | pg_stat_statements | 适合分析查询性能 |

### 工具安装优先级

**生产环境必备**:

1. `pg_stat_statements` - 查询性能分析
2. `pg_activity` 或 `pg_top` - 实时监控
3. `pgBadger` - 日志分析

**推荐安装**:
4. `pgbench` - 性能测试
5. `pg_repack` - 表维护
6. `pgBackRest` - 备份恢复

**可选工具**:
7. `pgAdmin` - 图形化管理（如果团队需要）

## 自动化脚本使用指南

### 脚本部署

```bash
# 1. 创建脚本目录
mkdir -p /usr/local/bin/postgresql-scripts

# 2. 复制脚本
cp health_check.sh /usr/local/bin/postgresql-scripts/
cp vacuum_monitor.sh /usr/local/bin/postgresql-scripts/
cp slow_query_monitor.sh /usr/local/bin/postgresql-scripts/
cp backup_verify.sh /usr/local/bin/postgresql-scripts/

# 3. 设置权限
chmod +x /usr/local/bin/postgresql-scripts/*.sh

# 4. 配置cron任务
cat > /etc/cron.d/postgresql-monitoring <<EOF
# 每小时健康检查
0 * * * * postgres /usr/local/bin/postgresql-scripts/health_check.sh >> /var/log/postgresql/health_check.log 2>&1

# 每天VACUUM监控
0 2 * * * postgres /usr/local/bin/postgresql-scripts/vacuum_monitor.sh >> /var/log/postgresql/vacuum_monitor.log 2>&1

# 每5分钟慢查询监控
*/5 * * * * postgres /usr/local/bin/postgresql-scripts/slow_query_monitor.sh >> /var/log/postgresql/slow_query.log 2>&1
EOF
```

### 脚本监控

```bash
# 查看脚本执行日志
tail -f /var/log/postgresql/health_check.log
tail -f /var/log/postgresql/vacuum_monitor.log
tail -f /var/log/postgresql/slow_query.log

# 检查脚本执行状态
grep -i "error\|fail" /var/log/postgresql/*.log
```

## 实用工具集使用建议

### 定期执行

```sql
-- 建议每天执行一次
-- 1. 数据库大小统计（监控存储增长）
SELECT * FROM database_size_summary;

-- 2. 索引使用统计（识别未使用索引）
SELECT * FROM unused_indexes;

-- 3. 性能指标汇总（监控整体性能）
SELECT * FROM performance_summary;
```

### 告警集成

```bash
# 将工具输出集成到告警系统
# 示例：如果未使用索引超过100MB，发送告警

UNUSED_INDEX_SIZE=$(psql -t -c "
SELECT SUM(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND schemaname = 'public';
" | xargs)

if [ "$UNUSED_INDEX_SIZE" -gt 104857600 ]; then  # 100MB
    echo "WARNING: Unused indexes exceed 100MB" | mail -s "PostgreSQL Alert" admin@example.com
fi
```

## 交叉引用

### 相关文档

- ⭐⭐⭐ [监控与诊断](../监控与诊断/06.01-监控与诊断.md) - 监控理论基础和诊断方法
- ⭐⭐⭐ [监控与诊断落地指南](../监控与诊断/06.02-监控与诊断落地指南.md) - Prometheus + Grafana部署
- ⭐⭐ [性能调优变更闭环](../监控与诊断/06.03-性能调优变更闭环.md) - 性能调优流程
- ⭐⭐ [性能问题案例库](../监控与诊断/06.04-性能问题案例库.md) - 实际性能问题案例
- ⭐⭐ [备份与恢复](../备份与恢复/06.06-备份与恢复.md) - 备份恢复详细指南
- ⭐ [运维手册](../运维手册/README.md) - 运维Runbook集合

### 外部资源

- [pgAdmin官方文档](https://www.pgadmin.org/docs/)
- [pg_stat_statements文档](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [pgBadger官方文档](https://pgbadger.darold.net/)
- [pg_repack官方文档](https://github.com/reorg/pg_repack)
- [pgBackRest官方文档](https://pgbackrest.org/)

---

**文档版本**: v1.0
**最后更新**: 2025-11-22
**PostgreSQL版本**: 18.x (推荐) ⭐ | 17.x (推荐) | 16.x (兼容)
**维护者**: Documentation Team
