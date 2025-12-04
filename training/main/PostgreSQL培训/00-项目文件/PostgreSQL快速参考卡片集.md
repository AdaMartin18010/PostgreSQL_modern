# PostgreSQL 快速参考卡片集

> **更新时间**: 2025 年 1 月
> **适用版本**: PostgreSQL 17+/18+
> **文档编号**: 00-01-06

---

## 📑 使用说明

本文档提供 PostgreSQL 各个主题的快速参考卡片，每个卡片包含最常用的命令、语法和技巧，适合打印或作为快速参考。

---

## 🗂️ 卡片目录

- [PostgreSQL 快速参考卡片集](#postgresql-快速参考卡片集)
  - [📑 使用说明](#-使用说明)
  - [🗂️ 卡片目录](#️-卡片目录)
  - [1. SQL 基础语法速查卡](#1-sql-基础语法速查卡)
    - [DDL（数据定义语言）](#ddl数据定义语言)
    - [DML（数据操作语言）](#dml数据操作语言)
    - [DQL（数据查询语言）](#dql数据查询语言)
  - [2. SQL 高级特性速查卡](#2-sql-高级特性速查卡)
    - [窗口函数](#窗口函数)
    - [CTE（公共表表达式）](#cte公共表表达式)
    - [JSONB 操作](#jsonb-操作)
    - [全文搜索](#全文搜索)
  - [3. 性能优化速查卡](#3-性能优化速查卡)
    - [执行计划分析](#执行计划分析)
    - [索引优化](#索引优化)
    - [统计信息](#统计信息)
    - [查询优化技巧](#查询优化技巧)
  - [4. 管理命令速查卡](#4-管理命令速查卡)
    - [数据库管理](#数据库管理)
    - [用户和权限](#用户和权限)
    - [表空间管理](#表空间管理)
    - [VACUUM 和维护](#vacuum-和维护)
  - [5. 监控诊断速查卡](#5-监控诊断速查卡)
    - [连接监控](#连接监控)
    - [锁监控](#锁监控)
    - [慢查询监控](#慢查询监控)
    - [数据库大小监控](#数据库大小监控)
  - [6. 配置参数速查卡](#6-配置参数速查卡)
    - [内存配置（按16GB内存服务器）](#内存配置按16gb内存服务器)
    - [WAL 配置](#wal-配置)
    - [查询优化器配置](#查询优化器配置)
    - [并行查询配置（8核CPU）](#并行查询配置8核cpu)
    - [自动 VACUUM 配置](#自动-vacuum-配置)
  - [7. 备份恢复速查卡](#7-备份恢复速查卡)
    - [逻辑备份（pg\_dump）](#逻辑备份pg_dump)
    - [逻辑恢复（pg\_restore）](#逻辑恢复pg_restore)
    - [物理备份（pg\_basebackup）](#物理备份pg_basebackup)
    - [PITR 恢复](#pitr-恢复)
  - [8. 安全权限速查卡](#8-安全权限速查卡)
    - [用户管理](#用户管理)
    - [角色管理](#角色管理)
    - [行级安全（RLS）](#行级安全rls)
    - [SSL/TLS 配置](#ssltls-配置)
  - [9. 扩展管理速查卡](#9-扩展管理速查卡)
    - [常用扩展](#常用扩展)
    - [pgvector（向量数据库）](#pgvector向量数据库)
    - [TimescaleDB（时序数据库）](#timescaledb时序数据库)
  - [10. psql 命令速查卡](#10-psql-命令速查卡)
    - [基本命令](#基本命令)
  - [📊 常用系统视图速查](#-常用系统视图速查)
    - [pg\_stat\_\* 视图](#pg_stat_-视图)
    - [pg\_settings 视图](#pg_settings-视图)
    - [information\_schema 视图](#information_schema-视图)
  - [🎯 性能调优速查](#-性能调优速查)
    - [黄金配置法则](#黄金配置法则)
    - [快速诊断命令](#快速诊断命令)
  - [🚀 常用命令速查](#-常用命令速查)
    - [系统管理命令](#系统管理命令)
    - [批量操作命令](#批量操作命令)
  - [📚 PostgreSQL 17/18 新特性速查](#-postgresql-1718-新特性速查)
    - [PostgreSQL 17 新特性](#postgresql-17-新特性)
    - [PostgreSQL 18 新特性](#postgresql-18-新特性)
  - [🔍 快速故障排查](#-快速故障排查)
    - [常见错误及解决](#常见错误及解决)
    - [紧急操作命令](#紧急操作命令)
  - [📖 学习资源快速链接](#-学习资源快速链接)
    - [基础学习](#基础学习)
    - [进阶学习](#进阶学习)
    - [运维管理](#运维管理)
    - [实用指南](#实用指南)
  - [💡 使用建议](#-使用建议)
    - [如何使用快速参考卡](#如何使用快速参考卡)
  - [⚡ 最常用的 TOP 10 命令](#-最常用的-top-10-命令)
    - [每个 PostgreSQL 用户都应该知道的命令](#每个-postgresql-用户都应该知道的命令)

---

## 1. SQL 基础语法速查卡

### DDL（数据定义语言）

```sql
-- 创建表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 修改表
ALTER TABLE users ADD COLUMN age INT;
ALTER TABLE users DROP COLUMN age;
ALTER TABLE users ALTER COLUMN name TYPE TEXT;
ALTER TABLE users RENAME TO customers;

-- 删除表
DROP TABLE users;
DROP TABLE IF EXISTS users CASCADE;

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_name ON users(name);
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
```

### DML（数据操作语言）

```sql
-- 插入数据
INSERT INTO users (name, email) VALUES ('张三', 'zhang@example.com');
INSERT INTO users (name, email) VALUES
    ('李四', 'li@example.com'),
    ('王五', 'wang@example.com');

-- 更新数据
UPDATE users SET name = '张三丰' WHERE id = 1;
UPDATE users SET email = LOWER(email);

-- 删除数据
DELETE FROM users WHERE id = 1;
DELETE FROM users WHERE created_at < NOW() - INTERVAL '1 year';

-- 批量插入（COPY，最快）
COPY users (name, email) FROM '/path/to/data.csv' CSV HEADER;
```

### DQL（数据查询语言）

```sql
-- 基础查询
SELECT * FROM users;
SELECT id, name FROM users WHERE age > 18;
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;

-- 聚合查询
SELECT count(*), avg(age), max(age), min(age) FROM users;
SELECT status, count(*) FROM orders GROUP BY status;
SELECT status, count(*) FROM orders GROUP BY status HAVING count(*) > 100;

-- 连接查询
SELECT u.name, o.order_id FROM users u
JOIN orders o ON u.id = o.user_id;

SELECT u.name, o.order_id FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- 子查询
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);
SELECT * FROM users WHERE EXISTS (SELECT 1 FROM orders WHERE user_id = users.id);
```

---

## 2. SQL 高级特性速查卡

### 窗口函数

```sql
-- ROW_NUMBER：行号
SELECT name, ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
FROM users;

-- RANK：排名（有并列）
SELECT name, score, RANK() OVER (ORDER BY score DESC) AS rank
FROM students;

-- LAG/LEAD：访问前后行
SELECT
    date,
    amount,
    LAG(amount) OVER (ORDER BY date) AS prev_amount,
    LEAD(amount) OVER (ORDER BY date) AS next_amount
FROM sales;

-- 移动平均
SELECT
    date,
    amount,
    AVG(amount) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma7
FROM sales;
```

### CTE（公共表表达式）

```sql
-- 简单 CTE
WITH recent_users AS (
    SELECT * FROM users WHERE created_at > NOW() - INTERVAL '30 days'
)
SELECT * FROM recent_users WHERE age > 18;

-- 递归 CTE（树形结构）
WITH RECURSIVE org_tree AS (
    -- 基础查询：根节点
    SELECT id, name, parent_id, 1 AS level
    FROM employees WHERE parent_id IS NULL

    UNION ALL

    -- 递归查询：子节点
    SELECT e.id, e.name, e.parent_id, t.level + 1
    FROM employees e
    JOIN org_tree t ON e.parent_id = t.id
)
SELECT * FROM org_tree;
```

### JSONB 操作

```sql
-- 创建 JSONB 列
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    properties JSONB
);

-- 插入 JSON 数据
INSERT INTO products (properties) VALUES
    ('{"name": "Product A", "price": 99.99, "tags": ["new", "hot"]}');

-- 查询 JSON
SELECT properties->>'name' AS name FROM products;
SELECT * FROM products WHERE properties->>'price' > '50';
SELECT * FROM products WHERE properties @> '{"tags": ["hot"]}';

-- 创建 GIN 索引
CREATE INDEX idx_products_properties ON products USING gin(properties);

-- JSON 路径查询
SELECT * FROM products WHERE properties @? '$.tags[*] ? (@ == "hot")';
```

### 全文搜索

```sql
-- 创建全文搜索列
ALTER TABLE articles ADD COLUMN tsv tsvector;

-- 更新全文搜索列
UPDATE articles SET tsv = to_tsvector('english', title || ' ' || content);

-- 创建 GIN 索引
CREATE INDEX idx_articles_tsv ON articles USING gin(tsv);

-- 全文搜索
SELECT * FROM articles WHERE tsv @@ to_tsquery('english', 'postgresql & performance');

-- 排序结果
SELECT *, ts_rank(tsv, query) AS rank
FROM articles, to_tsquery('postgresql') query
WHERE tsv @@ query
ORDER BY rank DESC;
```

---

## 3. 性能优化速查卡

### 执行计划分析

```sql
-- 基本执行计划
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- 详细执行计划
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM users WHERE email = 'test@example.com';

-- 关键指标：
-- • Seq Scan：全表扫描（考虑添加索引）
-- • Index Scan：索引扫描（好）
-- • Nested Loop：嵌套循环（小表连接时好）
-- • Hash Join：哈希连接（大表连接时好）
-- • Sort：排序（work_mem可能不足）
-- • Buffers：缓冲区使用（shared_buffers优化）
```

### 索引优化

```sql
-- 查找未使用的索引
SELECT
    schemaname, tablename, indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- 查找缺失索引（全表扫描多）
SELECT
    schemaname, tablename, seq_scan, seq_tup_read,
    seq_tup_read / seq_scan AS avg_tuples
FROM pg_stat_user_tables
WHERE seq_scan > 100
ORDER BY seq_tup_read DESC;

-- 重建索引
REINDEX INDEX CONCURRENTLY index_name;
REINDEX TABLE CONCURRENTLY table_name;
```

### 统计信息

```sql
-- 更新统计信息
ANALYZE table_name;
VACUUM ANALYZE table_name;

-- 查看统计信息
SELECT * FROM pg_stats WHERE tablename = 'users';

-- 增加统计精度
ALTER TABLE users ALTER COLUMN email SET STATISTICS 1000;
ANALYZE users;
```

### 查询优化技巧

```sql
-- 1. 使用 EXISTS 代替 IN
SELECT * FROM users WHERE EXISTS (
    SELECT 1 FROM orders WHERE user_id = users.id
);

-- 2. 使用 CTE 避免重复子查询
WITH stats AS (
    SELECT user_id, COUNT(*) cnt FROM orders GROUP BY user_id
)
SELECT u.*, s.cnt FROM users u JOIN stats s ON u.id = s.user_id;

-- 3. 使用 DISTINCT ON 代替子查询
SELECT DISTINCT ON (user_id) *
FROM orders
ORDER BY user_id, created_at DESC;

-- 4. 使用部分索引
CREATE INDEX idx_orders_pending ON orders(created_at) WHERE status = 'pending';

-- 5. 使用 LIMIT 限制结果
SELECT * FROM large_table ORDER BY created_at DESC LIMIT 100;
```

---

## 4. 管理命令速查卡

### 数据库管理

```sql
-- 创建/删除数据库
CREATE DATABASE mydb ENCODING 'UTF8' LC_COLLATE 'zh_CN.UTF-8';
DROP DATABASE mydb;

-- 查看数据库
\l                    -- 列出所有数据库
\l+                   -- 显示详细信息
SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database;

-- 连接数据库
\c mydb              -- 在 psql 中切换数据库
psql -U postgres -d mydb  -- 命令行连接
```

### 用户和权限

```sql
-- 创建用户
CREATE USER app_user WITH PASSWORD 'secure_password';
CREATE ROLE readonly_role;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE mydb TO app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_role;
GRANT readonly_role TO app_user;

-- 撤销权限
REVOKE ALL PRIVILEGES ON DATABASE mydb FROM app_user;

-- 查看权限
\du                  -- 列出所有用户
\dp table_name       -- 查看表权限
SELECT * FROM information_schema.table_privileges;
```

### 表空间管理

```sql
-- 创建表空间
CREATE TABLESPACE fast_space LOCATION '/fast/disk/pgdata';

-- 移动表到新表空间
ALTER TABLE large_table SET TABLESPACE fast_space;

-- 查看表空间
\db+                 -- 列出所有表空间
SELECT * FROM pg_tablespace;
```

### VACUUM 和维护

```sql
-- VACUUM（清理死元组）
VACUUM table_name;
VACUUM VERBOSE table_name;
VACUUM ANALYZE table_name;

-- VACUUM FULL（完全清理，需要排他锁）
VACUUM FULL table_name;

-- 查看 VACUUM 状态
SELECT * FROM pg_stat_progress_vacuum;

-- 查看表膨胀
SELECT
    schemaname, tablename,
    n_dead_tup, n_live_tup,
    round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS bloat_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

---

## 5. 监控诊断速查卡

### 连接监控

```sql
-- 查看所有连接
SELECT * FROM pg_stat_activity;

-- 查看活跃连接
SELECT pid, usename, datname, state, query
FROM pg_stat_activity
WHERE state = 'active';

-- 查看空闲连接
SELECT pid, usename, state_change, now() - state_change AS idle_time
FROM pg_stat_activity
WHERE state = 'idle'
ORDER BY idle_time DESC;

-- 终止连接
SELECT pg_terminate_backend(pid);
SELECT pg_cancel_backend(pid);  -- 只取消查询，不断开连接
```

### 锁监控

```sql
-- 查看锁等待
SELECT * FROM pg_locks WHERE NOT granted;

-- 查看阻塞关系
SELECT
    blocked.pid AS blocked_pid,
    blocked.query AS blocked_query,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks blocked_locks ON blocked.pid = blocked_locks.pid
JOIN pg_locks blocking_locks ON blocked_locks.locktype = blocking_locks.locktype
JOIN pg_stat_activity blocking ON blocking.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted AND blocking_locks.granted;
```

### 慢查询监控

```sql
-- 查看正在执行的慢查询
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '5 seconds'
ORDER BY duration DESC;

-- 查看历史慢查询（需要 pg_stat_statements）
CREATE EXTENSION pg_stat_statements;

SELECT
    substring(query, 1, 80) AS query,
    calls, mean_exec_time, max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 重置统计
SELECT pg_stat_statements_reset();
```

### 数据库大小监控

```sql
-- 数据库大小
SELECT datname, pg_size_pretty(pg_database_size(datname))
FROM pg_database;

-- 表大小（前20）
SELECT
    schemaname, tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) -
                   pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- 索引大小
SELECT
    schemaname, tablename, indexname,
    pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## 6. 配置参数速查卡

### 内存配置（按16GB内存服务器）

```sql
-- 共享缓冲区（物理内存的25%）
ALTER SYSTEM SET shared_buffers = '4GB';

-- 有效缓存大小（物理内存的75%）
ALTER SYSTEM SET effective_cache_size = '12GB';

-- 工作内存（根据并发数调整）
ALTER SYSTEM SET work_mem = '64MB';

-- 维护工作内存（物理内存的5-10%）
ALTER SYSTEM SET maintenance_work_mem = '1GB';

-- 应用配置
SELECT pg_reload_conf();  -- 无需重启
-- 或重启：systemctl restart postgresql
```

### WAL 配置

```sql
-- WAL 缓冲区
ALTER SYSTEM SET wal_buffers = '16MB';

-- 检查点配置
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET min_wal_size = '2GB';
ALTER SYSTEM SET max_wal_size = '8GB';

-- WAL 压缩（PG 9.5+）
ALTER SYSTEM SET wal_compression = on;

-- 同步提交（OLTP 系统可关闭以提升性能）
ALTER SYSTEM SET synchronous_commit = off;
```

### 查询优化器配置

```sql
-- SSD 存储
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- 机械硬盘
ALTER SYSTEM SET random_page_cost = 4.0;
ALTER SYSTEM SET effective_io_concurrency = 2;

-- 统计精度
ALTER SYSTEM SET default_statistics_target = 100;
```

### 并行查询配置（8核CPU）

```sql
ALTER SYSTEM SET max_worker_processes = 8;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
```

### 自动 VACUUM 配置

```sql
-- 全局配置
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_max_workers = 3;
ALTER SYSTEM SET autovacuum_naptime = '1min';

-- 表级配置（高频更新表）
ALTER TABLE high_update_table SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);
```

---

## 7. 备份恢复速查卡

### 逻辑备份（pg_dump）

```bash
# 导出单个数据库
pg_dump -U postgres -d mydb -f mydb.sql

# 导出压缩格式（推荐）
pg_dump -U postgres -Fc -d mydb -f mydb.dump

# 导出目录格式（支持并行）
pg_dump -U postgres -Fd -j 4 -d mydb -f mydb_dir

# 导出所有数据库
pg_dumpall -U postgres -f all_databases.sql

# 仅导出 schema
pg_dump -U postgres -s -d mydb -f schema.sql

# 仅导出数据
pg_dump -U postgres -a -d mydb -f data.sql

# 导出特定表
pg_dump -U postgres -d mydb -t table_name -f table.sql
```

### 逻辑恢复（pg_restore）

```bash
# 恢复数据库
pg_restore -U postgres -d mydb mydb.dump

# 并行恢复
pg_restore -U postgres -d mydb -j 4 mydb.dump

# 仅恢复 schema
pg_restore -U postgres -d mydb --schema-only mydb.dump

# 仅恢复数据
pg_restore -U postgres -d mydb --data-only mydb.dump

# 恢复特定表
pg_restore -U postgres -d mydb -t table_name mydb.dump

# 从 SQL 文件恢复
psql -U postgres -d mydb -f mydb.sql
```

### 物理备份（pg_basebackup）

```bash
# 基础备份
pg_basebackup -h localhost -U postgres -D /backup/pgdata -P

# 压缩备份
pg_basebackup -h localhost -U postgres -D /backup/pgdata -P -z

# 流式备份
pg_basebackup -h localhost -U postgres -D /backup/pgdata -Xs -P
```

### PITR 恢复

```bash
# 1. 恢复基础备份
tar -xzf base_backup.tar.gz -C /var/lib/postgresql/17/main/

# 2. 创建恢复配置
cat > /var/lib/postgresql/17/main/recovery.signal <<EOF
# Recovery signal
EOF

cat >> /var/lib/postgresql/17/main/postgresql.conf <<EOF
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2025-01-15 14:30:00'
recovery_target_action = 'promote'
EOF

# 3. 启动数据库
systemctl start postgresql
```

---

## 8. 安全权限速查卡

### 用户管理

```sql
-- 创建用户
CREATE USER app_user WITH PASSWORD 'secure_password';
CREATE USER admin_user WITH SUPERUSER PASSWORD 'admin_password';

-- 修改密码
ALTER USER app_user PASSWORD 'new_password';

-- 删除用户
DROP USER app_user;

-- 查看用户
\du
SELECT usename, usesuper, usecreatedb FROM pg_user;
```

### 角色管理

```sql
-- 创建角色
CREATE ROLE readonly;
CREATE ROLE readwrite;

-- 授予角色权限
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO readwrite;

-- 为用户授予角色
GRANT readonly TO app_user;

-- 撤销角色
REVOKE readonly FROM app_user;
```

### 行级安全（RLS）

```sql
-- 启用 RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY user_policy ON documents
FOR ALL TO app_user
USING (user_id = current_user_id());

-- 查看策略
\d+ documents
SELECT * FROM pg_policies;
```

### SSL/TLS 配置

```bash
# 生成自签名证书
openssl req -new -x509 -days 365 -nodes -text \
  -out server.crt -keyout server.key

# 配置 postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'

# 配置 pg_hba.conf
hostssl all all 0.0.0.0/0 scram-sha-256
```

---

## 9. 扩展管理速查卡

### 常用扩展

```sql
-- 查看可用扩展
SELECT * FROM pg_available_extensions;

-- 查看已安装扩展
\dx
SELECT * FROM pg_extension;

-- 安装扩展
CREATE EXTENSION pg_stat_statements;
CREATE EXTENSION pgcrypto;
CREATE EXTENSION pg_trgm;
CREATE EXTENSION pgvector;
CREATE EXTENSION timescaledb;

-- 更新扩展
ALTER EXTENSION pg_stat_statements UPDATE;

-- 删除扩展
DROP EXTENSION pg_stat_statements;
```

### pgvector（向量数据库）

```sql
-- 安装
CREATE EXTENSION vector;

-- 创建向量列
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    embedding vector(1536)
);

-- 插入向量
INSERT INTO items (embedding) VALUES ('[0.1, 0.2, ...]');

-- 创建索引
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);

-- 向量搜索
SELECT * FROM items
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 10;
```

### TimescaleDB（时序数据库）

```sql
-- 安装
CREATE EXTENSION timescaledb;

-- 创建超表
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id INT,
    temperature DOUBLE PRECISION
);

SELECT create_hypertable('metrics', 'time');

-- 数据保留策略
SELECT add_retention_policy('metrics', INTERVAL '90 days');

-- 连续聚合
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', time) AS hour,
       device_id,
       avg(temperature) as avg_temp
FROM metrics
GROUP BY hour, device_id;
```

---

## 10. psql 命令速查卡

### 基本命令

```text
连接和退出：
\c database_name     -- 切换数据库
\q                   -- 退出
\! clear             -- 清屏

查看信息：
\l                   -- 列出数据库
\dt                  -- 列出表
\di                  -- 列出索引
\dv                  -- 列出视图
\df                  -- 列出函数
\du                  -- 列出用户
\dn                  -- 列出schema

查看详情：
\d table_name        -- 查看表结构
\d+ table_name       -- 查看表详细信息
\di+ index_name      -- 查看索引详情

执行SQL：
\i script.sql        -- 执行SQL文件
\o output.txt        -- 输出到文件
\g                   -- 执行查询

格式化输出：
\x                   -- 切换扩展显示模式
\a                   -- 切换对齐模式
\t                   -- 只显示数据
\pset format html    -- HTML格式输出

变量：
\set var 'value'     -- 设置变量
\echo :var           -- 显示变量

时间：
\timing              -- 显示查询执行时间

编辑：
\e                   -- 在编辑器中编辑查询
\ef function_name    -- 编辑函数

帮助：
\?                   -- psql命令帮助
\h SELECT            -- SQL命令帮助
```

---

## 📊 常用系统视图速查

### pg_stat_* 视图

```sql
-- 数据库统计
SELECT * FROM pg_stat_database;

-- 表统计
SELECT * FROM pg_stat_user_tables;

-- 索引统计
SELECT * FROM pg_stat_user_indexes;

-- 活动会话
SELECT * FROM pg_stat_activity;

-- 复制状态
SELECT * FROM pg_stat_replication;

-- 后台写进程
SELECT * FROM pg_stat_bgwriter;
```

### pg_settings 视图

```sql
-- 查看所有配置
SELECT * FROM pg_settings;

-- 查看特定配置
SELECT name, setting, unit, source
FROM pg_settings
WHERE name LIKE '%memory%';

-- 查看需要重启的配置
SELECT name, setting, pending_restart
FROM pg_settings
WHERE pending_restart = true;
```

### information_schema 视图

```sql
-- 查看表信息
SELECT * FROM information_schema.tables;

-- 查看列信息
SELECT * FROM information_schema.columns WHERE table_name = 'users';

-- 查看约束信息
SELECT * FROM information_schema.table_constraints;

-- 查看视图定义
SELECT * FROM information_schema.views;
```

---

## 🎯 性能调优速查

### 黄金配置法则

```text
物理内存 RAM：
├─ shared_buffers = RAM × 25%
├─ effective_cache_size = RAM × 75%
├─ work_mem = (RAM - shared_buffers) / max_connections / 2
└─ maintenance_work_mem = RAM × 5-10%

示例（16GB RAM）：
├─ shared_buffers = 4GB
├─ effective_cache_size = 12GB
├─ work_mem = 64MB（假设200连接）
└─ maintenance_work_mem = 1GB
```

### 快速诊断命令

```sql
-- 缓冲区命中率（应 > 99%）
SELECT
    round(100.0 * sum(blks_hit) / NULLIF(sum(blks_hit + blks_read), 0), 2) AS hit_ratio
FROM pg_stat_database;

-- 连接使用率（应 < 80%）
SELECT
    count(*) * 100.0 / (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') AS usage_pct
FROM pg_stat_activity;

-- 检查点频率（checkpoints_req 应 < 10% checkpoints_timed）
SELECT
    checkpoints_timed,
    checkpoints_req,
    round(100.0 * checkpoints_req / NULLIF(checkpoints_timed, 0), 2) AS req_pct
FROM pg_stat_bgwriter;
```

---

## 🚀 常用命令速查

### 系统管理命令

```bash
# 启动/停止/重启
systemctl start postgresql
systemctl stop postgresql
systemctl restart postgresql
systemctl reload postgresql  # 重新加载配置

# 查看状态
systemctl status postgresql

# 查看日志
tail -f /var/log/postgresql/postgresql-17-main.log
journalctl -u postgresql -f

# 查看版本
psql --version
psql -U postgres -c "SELECT version();"

# 连接数据库
psql -U postgres              # 本地连接
psql -h localhost -U postgres -d mydb -p 5432  # 指定参数
```

### 批量操作命令

```bash
# 批量 VACUUM
vacuumdb -U postgres -d mydb -z

# 批量 REINDEX
reindexdb -U postgres -d mydb

# 批量 ANALYZE
vacuumdb -U postgres -d mydb --analyze-only

# 所有数据库
vacuumdb -U postgres --all -z
```

---

## 📚 PostgreSQL 17/18 新特性速查

### PostgreSQL 17 新特性

```sql
-- MERGE 语句（终于支持了！）
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET value = s.value
WHEN NOT MATCHED THEN INSERT VALUES (s.id, s.value);

-- 逻辑复制并行应用
ALTER SUBSCRIPTION my_sub SET (streaming = parallel);

-- JSON 函数增强
SELECT jsonb_path_query(data, '$.items[*] ? (@.price > 100)') FROM products;
```

### PostgreSQL 18 新特性

```sql
-- 异步 I/O（需要系统支持）
ALTER SYSTEM SET enable_async_io = on;

-- 查询优化器改进
ALTER SYSTEM SET enable_query_optimizer_v2 = on;

-- 并行度自适应
ALTER SYSTEM SET enable_adaptive_parallelism = on;
```

---

## 🔍 快速故障排查

### 常见错误及解决

| 错误信息 | 原因 | 快速解决 |
|---------|------|---------|
| `FATAL: too many connections` | 连接数已满 | `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';` |
| `deadlock detected` | 死锁 | 统一访问顺序，使用`FOR UPDATE SKIP LOCKED` |
| `permission denied` | 权限不足 | `GRANT SELECT, INSERT, UPDATE, DELETE ON table TO user;` |
| `out of memory` | 内存不足 | 降低`work_mem`或增加物理内存 |
| `could not resize shared memory` | shared_buffers太大 | 降低shared_buffers或增加系统shared memory限制 |

### 紧急操作命令

```sql
-- 终止所有空闲连接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND pid != pg_backend_pid();

-- 终止长时间运行的查询
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '5 minutes'
  AND pid != pg_backend_pid();

-- 取消正在执行的VACUUM
SELECT pg_cancel_backend(pid)
FROM pg_stat_activity
WHERE query LIKE 'VACUUM%';
```

---

## 📖 学习资源快速链接

### 基础学习

- 📚 [SQL基础培训](../01-SQL基础/SQL基础培训.md)
- 📚 [数据类型详解](../03-数据类型/数据类型详解.md)
- 📚 [函数与存储过程](../04-函数与编程/函数与存储过程.md)

### 进阶学习

- 📚 [窗口函数详解](../02-SQL高级特性/窗口函数详解.md)
- 📚 [CTE详解](../02-SQL高级特性/CTE详解.md)
- 📚 [查询计划与优化器](../01-SQL基础/查询计划与优化器.md)

### 运维管理

- 📚 [监控与诊断](../10-监控诊断/监控与诊断.md)
- 📚 [性能调优深入](../11-性能调优/性能调优深入.md)
- 📚 [高可用体系详解](../09-高可用/高可用体系详解.md)

### 实用指南

- 📚 [学习路径完整指南](./PostgreSQL学习路径完整指南.md)
- 📚 [常见问题快速查询手册](./PostgreSQL常见问题快速查询手册.md)
- 📚 [性能调优检查清单](./PostgreSQL性能调优检查清单.md)

---

## 💡 使用建议

### 如何使用快速参考卡

1. **日常使用**：
   - 打印出来放在手边
   - 保存到收藏夹
   - 作为速查手册

2. **学习使用**：
   - 配合详细文档学习
   - 先理解原理再查命令
   - 实际操作中验证

3. **团队使用**：
   - 分享给团队成员
   - 作为团队规范参考
   - 统一操作标准

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
**文档编号**: 00-01-06

---

## ⚡ 最常用的 TOP 10 命令

### 每个 PostgreSQL 用户都应该知道的命令

1. **连接数据库**：`psql -U postgres -d mydb`
2. **查看表结构**：`\d table_name`
3. **执行计划**：`EXPLAIN ANALYZE SELECT ...`
4. **查看连接**：`SELECT * FROM pg_stat_activity;`
5. **终止会话**：`SELECT pg_terminate_backend(pid);`
6. **备份数据库**：`pg_dump -Fc mydb -f mydb.dump`
7. **恢复数据库**：`pg_restore -d mydb mydb.dump`
8. **更新统计**：`VACUUM ANALYZE table_name;`
9. **查看大小**：`SELECT pg_size_pretty(pg_database_size('mydb'));`
10. **查看慢查询**：`SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;`
