# PostgreSQL 18 快速参考手册

## 📋 常用命令速查

### 数据库连接

```bash
# 本地连接
psql -d dbname

# 远程连接
psql -h hostname -p 5432 -U username -d dbname

# 使用连接字符串
psql postgresql://username:password@hostname:5432/dbname

# 执行SQL文件
psql -d dbname -f script.sql

# 执行单个命令
psql -d dbname -c "SELECT version();"
```

---

## 🔍 信息查询

### 数据库信息

```sql
-- 列出所有数据库
\l
SELECT datname FROM pg_database;

-- 当前数据库大小
SELECT pg_size_pretty(pg_database_size(current_database()));

-- 所有数据库大小
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;
```

### 表信息

```sql
-- 列出所有表
\dt
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- 表结构
\d tablename
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tablename';

-- 表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- 表行数（精确）
SELECT COUNT(*) FROM tablename;

-- 表行数（估算，快速）
SELECT reltuples::BIGINT FROM pg_class WHERE relname = 'tablename';
```

### 索引信息

```sql
-- 列出所有索引
\di
SELECT indexname FROM pg_indexes WHERE schemaname = 'public';

-- 表的索引
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'tablename';

-- 未使用的索引
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- 重复索引
SELECT
    t.tablename,
    i1.indexname AS index1,
    i2.indexname AS index2
FROM pg_indexes i1
JOIN pg_indexes i2 ON i1.tablename = i2.tablename
    AND i1.indexname < i2.indexname
    AND i1.indexdef = i2.indexdef
JOIN pg_tables t ON i1.tablename = t.tablename
WHERE t.schemaname = 'public';
```

---

## 🎯 性能优化

### 查询优化

```sql
-- 查看执行计划
EXPLAIN SELECT * FROM users WHERE age > 25;

-- 实际执行并显示统计
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 25;

-- 详细信息
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT * FROM users WHERE age > 25;

-- 慢查询统计
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### 索引优化

```sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);

-- 并发创建（不锁表）
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- 唯一索引
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- 部分索引
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- 表达式索引
CREATE INDEX idx_lower_email ON users(LOWER(email));

-- 多列索引
CREATE INDEX idx_users_name_age ON users(last_name, first_name, age);

-- GIN索引（JSON/数组）
CREATE INDEX idx_users_tags ON users USING GIN (tags);

-- 删除索引
DROP INDEX idx_users_email;
```

---

## 🔧 维护命令

### VACUUM

```sql
-- 单表VACUUM
VACUUM users;

-- 详细输出
VACUUM VERBOSE users;

-- VACUUM FULL（锁表，重写表）
VACUUM FULL users;

-- ANALYZE（更新统计信息）
ANALYZE users;

-- VACUUM + ANALYZE
VACUUM ANALYZE users;

-- 所有表
VACUUM ANALYZE;
```

### 表膨胀检查

```sql
SELECT
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### 锁监控

```sql
-- 当前锁
SELECT
    locktype,
    database,
    relation::regclass,
    mode,
    granted
FROM pg_locks
WHERE NOT granted;

-- 阻塞查询
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

-- 杀死查询
SELECT pg_cancel_backend(pid);  -- 尝试取消
SELECT pg_terminate_backend(pid);  -- 强制终止
```

---

## 📊 监控查询

### 连接信息

```sql
-- 当前连接数
SELECT COUNT(*) FROM pg_stat_activity;

-- 各状态连接数
SELECT
    state,
    COUNT(*)
FROM pg_stat_activity
GROUP BY state;

-- 活跃查询
SELECT
    pid,
    usename,
    datname,
    state,
    query,
    now() - query_start AS duration
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- 长事务
SELECT
    pid,
    usename,
    state,
    now() - xact_start AS duration,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
    AND now() - xact_start > INTERVAL '5 minutes'
ORDER BY duration DESC;
```

### 缓存命中率

```sql
SELECT
    'cache_hit_ratio' AS metric,
    ROUND(SUM(blks_hit) * 100.0 / NULLIF(SUM(blks_hit + blks_read), 0), 2) AS value
FROM pg_stat_database;

-- 各表缓存命中率
SELECT
    schemaname,
    tablename,
    heap_blks_hit,
    heap_blks_read,
    ROUND(heap_blks_hit * 100.0 / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) AS hit_ratio
FROM pg_statio_user_tables
WHERE heap_blks_read > 0
ORDER BY heap_blks_read DESC
LIMIT 20;
```

### 数据库统计

```sql
SELECT
    datname,
    numbackends AS connections,
    xact_commit AS commits,
    xact_rollback AS rollbacks,
    blks_read AS disk_reads,
    blks_hit AS cache_hits,
    tup_returned AS rows_returned,
    tup_fetched AS rows_fetched,
    tup_inserted AS rows_inserted,
    tup_updated AS rows_updated,
    tup_deleted AS rows_deleted
FROM pg_stat_database
WHERE datname = current_database();
```

---

## ⚙️ 配置参数

### 查看配置

```sql
-- 所有配置
SHOW ALL;

-- 特定配置
SHOW shared_buffers;
SHOW work_mem;

-- 配置详情
SELECT name, setting, unit, context
FROM pg_settings
WHERE name LIKE '%buffer%';

-- 修改配置
ALTER SYSTEM SET work_mem = '128MB';
SELECT pg_reload_conf();
```

### 关键配置推荐

```sql
-- 内存配置
shared_buffers = 25% of RAM          -- 例如: 16GB
work_mem = 64MB                       -- 根据查询复杂度调整
maintenance_work_mem = 2GB            -- 维护操作
effective_cache_size = 75% of RAM     -- 例如: 48GB

-- 连接配置
max_connections = 100                 -- 使用连接池时可降低
superuser_reserved_connections = 3

-- WAL配置
wal_level = replica
max_wal_size = 4GB
min_wal_size = 1GB
wal_buffers = 16MB

-- 检查点配置
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9

-- 查询优化器
random_page_cost = 1.1               -- SSD
effective_io_concurrency = 200       -- SSD

-- PostgreSQL 18新特性
io_direct = 'data,wal'               -- 异步I/O
io_combine_limit = '256kB'
enable_skip_scan = on
```

---

## 🚨 故障排查

### 连接问题

```bash
# 检查PostgreSQL是否运行
systemctl status postgresql

# 检查端口
netstat -tlnp | grep 5432

# 检查配置文件
cat /etc/postgresql/18/main/postgresql.conf | grep listen
cat /etc/postgresql/18/main/pg_hba.conf
```

### 性能问题

```sql
-- 1. 检查慢查询
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 2. 检查表膨胀
SELECT * FROM pg_stat_user_tables
WHERE n_dead_tup > 10000;

-- 3. 检查锁等待
SELECT * FROM pg_locks WHERE NOT granted;

-- 4. 检查缓存命中率
SELECT SUM(blks_hit) * 100.0 / NULLIF(SUM(blks_hit + blks_read), 0)
FROM pg_stat_database;

-- 5. 检查统计信息
SELECT last_analyze, last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

---

## 🔐 安全相关

### 用户管理

```sql
-- 创建用户
CREATE USER myuser WITH PASSWORD 'password';

-- 创建角色
CREATE ROLE readonly;

-- 授权
GRANT CONNECT ON DATABASE mydb TO myuser;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
GRANT readonly TO myuser;

-- 撤销权限
REVOKE SELECT ON users FROM myuser;

-- 修改密码
ALTER USER myuser WITH PASSWORD 'newpassword';

-- 删除用户
DROP USER myuser;
```

---

## 📦 备份恢复

### 备份

```bash
# 单个数据库
pg_dump mydb > backup.sql
pg_dump -Fc mydb > backup.dump  # 压缩格式

# 所有数据库
pg_dumpall > all_dbs.sql

# 只备份schema
pg_dump --schema-only mydb > schema.sql

# 只备份数据
pg_dump --data-only mydb > data.sql

# 只备份特定表
pg_dump -t users mydb > users.sql
```

### 恢复

```bash
# 从SQL文件
psql mydb < backup.sql

# 从dump文件
pg_restore -d mydb backup.dump

# 并行恢复
pg_restore -j 4 -d mydb backup.dump

# 只恢复schema
pg_restore --schema-only -d mydb backup.dump

# 只恢复特定表
pg_restore -t users -d mydb backup.dump
```

---

## 🎯 快速诊断清单

```sql
-- 1. 系统健康 ✓
SELECT version();
SELECT pg_postmaster_start_time();
SELECT COUNT(*) FROM pg_stat_activity;

-- 2. 性能指标 ✓
SELECT * FROM pg_stat_database WHERE datname = current_database();

-- 3. 缓存命中率 ✓ (应该>95%)
SELECT ROUND(SUM(blks_hit)*100.0/NULLIF(SUM(blks_hit+blks_read),0),2)
FROM pg_stat_database;

-- 4. 表膨胀 ✓
SELECT COUNT(*) FROM pg_stat_user_tables WHERE n_dead_tup > 1000;

-- 5. 锁等待 ✓
SELECT COUNT(*) FROM pg_locks WHERE NOT granted;

-- 6. 慢查询 ✓
SELECT COUNT(*) FROM pg_stat_statements WHERE mean_exec_time > 1000;

-- 7. 长事务 ✓
SELECT COUNT(*) FROM pg_stat_activity
WHERE state != 'idle' AND now() - xact_start > INTERVAL '5 minutes';
```

---

**使用提示**:

- 将本文档保存为书签
- 根据需要快速复制命令
- 结合具体场景调整参数
- 定期检查系统健康状态

📚 **更多详情**: 参考完整文档 `docs/` 目录
