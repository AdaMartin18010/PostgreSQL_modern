# PostgreSQL 18 开发者速查表

一页纸速查常用命令、函数和技巧。

---

## 📊 数据类型

```sql
-- 数值
SMALLINT, INTEGER, BIGINT
NUMERIC(precision, scale)
REAL, DOUBLE PRECISION

-- 字符串
VARCHAR(n), TEXT
CHAR(n)

-- 日期时间
DATE, TIME, TIMESTAMP
TIMESTAMPTZ  -- 带时区（推荐）
INTERVAL

-- 布尔
BOOLEAN

-- JSON
JSON, JSONB  -- JSONB更快

-- PostgreSQL 18
UUID  -- gen_uuid_v7()支持UUIDv7
VECTOR(n)  -- pgvector扩展

-- 数组
TEXT[], INTEGER[]

-- 范围
INT4RANGE, TSTZRANGE
```

---

## 🔍 常用查询

```sql
-- 基础查询
SELECT * FROM users WHERE age > 25;
SELECT COUNT(*) FROM users;
SELECT DISTINCT city FROM users;

-- JOIN
SELECT * FROM orders o
JOIN users u ON o.user_id = u.id;

-- LEFT JOIN
SELECT * FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- 聚合
SELECT city, COUNT(*), AVG(age)
FROM users
GROUP BY city
HAVING COUNT(*) > 100;

-- 子查询
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 1000);

-- CTE
WITH active_users AS (
    SELECT * FROM users WHERE last_login > now() - INTERVAL '30 days'
)
SELECT * FROM active_users WHERE age > 25;

-- 窗口函数
SELECT
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS rank,
    AVG(salary) OVER () AS avg_salary
FROM employees;
```

---

## ⚡ 性能优化

```sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_name ON users(name);  -- 不锁表

-- 唯一索引
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- 部分索引
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- 表达式索引
CREATE INDEX idx_lower_email ON users(LOWER(email));

-- 多列索引
CREATE INDEX idx_users_name_age ON users(last_name, first_name, age);

-- GIN索引（JSON/数组/全文搜索）
CREATE INDEX idx_data_gin ON docs USING GIN (data);

-- HNSW索引（向量，PostgreSQL 18）
CREATE INDEX idx_embedding ON docs USING hnsw (embedding vector_cosine_ops);

-- 查看执行计划
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- VACUUM
VACUUM ANALYZE users;

-- 更新统计信息
ANALYZE users;
```

---

## 🛠️ 数据操作

```sql
-- INSERT
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- 批量INSERT
INSERT INTO users (name, email) VALUES
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com');

-- COPY（最快）
COPY users FROM '/tmp/users.csv' WITH CSV HEADER;

-- UPDATE
UPDATE users SET email = 'new@example.com' WHERE id = 1;

-- DELETE
DELETE FROM users WHERE id = 1;

-- UPSERT (ON CONFLICT)
INSERT INTO users (id, name, email)
VALUES (1, 'Alice', 'alice@example.com')
ON CONFLICT (id) DO UPDATE
SET name = EXCLUDED.name, email = EXCLUDED.email;

-- RETURNING（获取插入的ID）
INSERT INTO users (name) VALUES ('Bob') RETURNING id;
```

---

## 🔐 用户管理

```sql
-- 创建用户
CREATE USER app_user WITH PASSWORD 'strong_password';

-- 创建角色
CREATE ROLE readonly;

-- 授权
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
GRANT readonly TO app_user;

-- 撤销
REVOKE SELECT ON users FROM app_user;

-- 修改密码
ALTER USER app_user WITH PASSWORD 'new_password';

-- 删除用户
DROP USER app_user;
```

---

## 📦 数据库管理

```sql
-- 创建数据库
CREATE DATABASE mydb;

-- 删除数据库
DROP DATABASE mydb;

-- 列出数据库
\l
SELECT datname FROM pg_database;

-- 数据库大小
SELECT pg_size_pretty(pg_database_size('mydb'));

-- 表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- 连接到其他数据库
\c mydb
```

---

## 📈 监控查询

```sql
-- 当前连接数
SELECT COUNT(*) FROM pg_stat_activity;

-- 活跃查询
SELECT pid, usename, state, query
FROM pg_stat_activity
WHERE state != 'idle';

-- 慢查询（需要pg_stat_statements）
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 缓存命中率
SELECT
    ROUND(SUM(blks_hit) * 100.0 / NULLIF(SUM(blks_hit + blks_read), 0), 2) AS hit_ratio
FROM pg_stat_database;

-- 表统计
SELECT * FROM pg_stat_user_tables WHERE schemaname = 'public';

-- 索引使用
SELECT * FROM pg_stat_user_indexes ORDER BY idx_scan;

-- 未使用的索引
SELECT indexname FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- 锁等待
SELECT * FROM pg_locks WHERE NOT granted;
```

---

## 🎯 PostgreSQL 18新特性

```sql
-- 异步I/O（性能+35%）
ALTER SYSTEM SET io_direct = 'data,wal';
SELECT pg_reload_conf();

-- Skip Scan
ALTER SYSTEM SET enable_skip_scan = on;

-- UUIDv7（时间排序）
SELECT gen_uuid_v7();

-- GIN并行构建（索引快73%）
CREATE INDEX CONCURRENTLY idx_data ON docs USING GIN (data);
```

---

## 🔧 实用函数

```sql
-- 字符串
LENGTH(str), LOWER(str), UPPER(str)
CONCAT(str1, str2), str1 || str2
SUBSTRING(str FROM start FOR len)
REPLACE(str, from, to)
TRIM(str), LTRIM(str), RTRIM(str)

-- 日期时间
NOW(), CURRENT_DATE, CURRENT_TIME
AGE(timestamp), EXTRACT(YEAR FROM date)
DATE_TRUNC('day', timestamp)

-- 数学
ABS(n), ROUND(n, d), CEIL(n), FLOOR(n)
RANDOM(), GREATEST(a,b), LEAST(a,b)

-- 聚合
COUNT(*), SUM(n), AVG(n), MIN(n), MAX(n)
STRING_AGG(str, delimiter)
ARRAY_AGG(expr)
JSONB_AGG(expr)

-- JSON
data->>'key'  -- 文本
data->'key'  -- JSON对象
data @> '{"key":"value"}'  -- 包含

-- 数组
ARRAY[1,2,3]
array_length(arr, 1)
unnest(arr)  -- 展开数组
```

---

## 💾 备份恢复

```bash
# 逻辑备份
pg_dump mydb > backup.sql
pg_dump -Fc mydb > backup.dump  # 压缩

# 恢复
psql mydb < backup.sql
pg_restore -d mydb backup.dump

# 只备份schema
pg_dump --schema-only mydb > schema.sql

# 只备份数据
pg_dump --data-only mydb > data.sql

# 只备份特定表
pg_dump -t users mydb > users.sql
```

---

## 🚨 紧急操作

```sql
-- 终止查询
SELECT pg_cancel_backend(pid);  -- 尝试取消
SELECT pg_terminate_backend(pid);  -- 强制终止

-- 终止所有空闲连接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND pid != pg_backend_pid();

-- 查看配置
SHOW ALL;
SHOW shared_buffers;

-- 修改配置
ALTER SYSTEM SET work_mem = '128MB';
SELECT pg_reload_conf();

-- 查看版本
SELECT version();

-- 查看运行时间
SELECT pg_postmaster_start_time();
```

---

## 📱 psql命令

```bash
\l          # 列出数据库
\c mydb     # 连接数据库
\dt         # 列出表
\d table    # 表结构
\di         # 列出索引
\dv         # 列出视图
\df         # 列出函数
\du         # 列出用户
\x          # 切换扩展显示
\timing     # 显示查询时间
\q          # 退出
\! cmd      # 执行shell命令
\i file.sql # 执行SQL文件
\o file     # 输出到文件
```

---

**打印此页作为速查表！** 📄
