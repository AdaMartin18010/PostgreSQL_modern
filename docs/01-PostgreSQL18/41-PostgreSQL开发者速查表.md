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
-- 性能测试：基础查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE age > 25;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '基础查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM users;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'COUNT查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT DISTINCT city FROM users;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'DISTINCT查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：JOIN（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM orders o
JOIN users u ON o.user_id = u.id;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'JOIN查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：LEFT JOIN（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'LEFT JOIN查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：聚合（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT city, COUNT(*), AVG(age)
FROM users
GROUP BY city
HAVING COUNT(*) > 100;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '聚合查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：子查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 1000);
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '子查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：CTE（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH active_users AS (
    SELECT * FROM users WHERE last_login > now() - INTERVAL '30 days'
)
SELECT * FROM active_users WHERE age > 25;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'CTE查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：窗口函数（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS rank,
    AVG(salary) OVER () AS avg_salary
FROM employees;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '窗口函数查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## ⚡ 性能优化

```sql
-- 性能测试：创建索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_users_email已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_name ON users(name);  -- 不锁表
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_name已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建并发索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：唯一索引（带错误处理）
BEGIN;
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users(email);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '唯一索引idx_users_email_unique已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建唯一索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：部分索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_active_users ON users(email) WHERE status = 'active';
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '部分索引idx_active_users已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建部分索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：表达式索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_lower_email ON users(LOWER(email));
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表达式索引idx_lower_email已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建表达式索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：多列索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_users_name_age ON users(last_name, first_name, age);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '多列索引idx_users_name_age已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建多列索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：GIN索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_data_gin ON docs USING GIN (data);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE 'GIN索引idx_data_gin已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建GIN索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：HNSW索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_embedding ON docs USING hnsw (embedding vector_cosine_ops);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE 'HNSW索引idx_embedding已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建HNSW索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查看执行计划（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE email = 'test@example.com';
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'EXPLAIN查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：VACUUM（带错误处理）
BEGIN;
VACUUM ANALYZE users;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'VACUUM ANALYZE失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：更新统计信息（带错误处理）
BEGIN;
ANALYZE users;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'ANALYZE失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 🛠️ 数据操作

```sql
-- 性能测试：INSERT（带错误处理）
BEGIN;
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')
ON CONFLICT DO NOTHING;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'INSERT失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：批量INSERT（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
INSERT INTO users (name, email) VALUES
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com')
ON CONFLICT DO NOTHING;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '批量INSERT失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：COPY（带错误处理）
BEGIN;
COPY users FROM '/tmp/users.csv' WITH CSV HEADER;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'COPY失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：UPDATE（带错误处理）
BEGIN;
UPDATE users SET email = 'new@example.com' WHERE id = 1;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'UPDATE失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：DELETE（带错误处理）
BEGIN;
DELETE FROM users WHERE id = 1;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'DELETE失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：UPSERT (ON CONFLICT)（带错误处理）
BEGIN;
INSERT INTO users (id, name, email)
VALUES (1, 'Alice', 'alice@example.com')
ON CONFLICT (id) DO UPDATE
SET name = EXCLUDED.name, email = EXCLUDED.email;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'UPSERT失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：RETURNING（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
INSERT INTO users (name) VALUES ('Bob') RETURNING id;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'RETURNING插入失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 🔐 用户管理

```sql
-- 性能测试：创建用户（带错误处理）
BEGIN;
CREATE USER IF NOT EXISTS app_user WITH PASSWORD 'strong_password';
COMMIT;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '用户app_user已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建用户失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建角色（带错误处理）
BEGIN;
CREATE ROLE IF NOT EXISTS readonly;
COMMIT;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '角色readonly已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建角色失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：授权（带错误处理）
BEGIN;
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
GRANT readonly TO app_user;
COMMIT;
EXCEPTION
    WHEN undefined_object THEN
        RAISE NOTICE '用户、角色或数据库不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '授权失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：撤销（带错误处理）
BEGIN;
REVOKE SELECT ON users FROM app_user;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '撤销权限失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：修改密码（带错误处理）
BEGIN;
ALTER USER app_user WITH PASSWORD 'new_password';
COMMIT;
EXCEPTION
    WHEN undefined_object THEN
        RAISE NOTICE '用户app_user不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '修改密码失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：删除用户（带错误处理）
BEGIN;
DROP USER IF EXISTS app_user;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '删除用户失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 📦 数据库管理

```sql
-- 性能测试：创建数据库（带错误处理）
BEGIN;
CREATE DATABASE IF NOT EXISTS mydb;
COMMIT;
EXCEPTION
    WHEN duplicate_database THEN
        RAISE NOTICE '数据库mydb已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建数据库失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：删除数据库（带错误处理）
BEGIN;
DROP DATABASE IF EXISTS mydb;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '删除数据库失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：列出数据库（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT datname FROM pg_database;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '列出数据库失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：数据库大小（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT pg_size_pretty(pg_database_size('mydb'));
COMMIT;
EXCEPTION
    WHEN undefined_database THEN
        RAISE NOTICE '数据库mydb不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '查询数据库大小失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：表大小（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询表大小失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 连接到其他数据库
-- \c mydb
```

---

## 📈 监控查询

```sql
-- 性能测试：当前连接数（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM pg_stat_activity;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询连接数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：活跃查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT pid, usename, state, query
FROM pg_stat_activity
WHERE state != 'idle';
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询活跃查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：慢查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'pg_stat_statements扩展未安装，请先执行: CREATE EXTENSION pg_stat_statements;';
    WHEN OTHERS THEN
        RAISE NOTICE '查询慢查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：缓存命中率（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    ROUND(SUM(blks_hit) * 100.0 / NULLIF(SUM(blks_hit + blks_read), 0), 2) AS hit_ratio
FROM pg_stat_database;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询缓存命中率失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：表统计（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM pg_stat_user_tables WHERE schemaname = 'public';
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询表统计失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：索引使用（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM pg_stat_user_indexes ORDER BY idx_scan;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询索引使用失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：未使用的索引（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT indexname FROM pg_stat_user_indexes WHERE idx_scan = 0;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询未使用索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：锁等待（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM pg_locks WHERE NOT granted;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询锁等待失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 🎯 PostgreSQL 18新特性

```sql
-- 性能测试：异步I/O（带错误处理）
BEGIN;
DO $$
BEGIN
    ALTER SYSTEM SET io_direct = 'data,wal';
    PERFORM pg_reload_conf();
    RAISE NOTICE '异步I/O配置已更新';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '配置异步I/O失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
END $$;
COMMIT;

-- 性能测试：Skip Scan（带错误处理）
BEGIN;
DO $$
BEGIN
    ALTER SYSTEM SET enable_skip_scan = on;
    PERFORM pg_reload_conf();
    RAISE NOTICE 'Skip Scan已启用';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '启用Skip Scan失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
END $$;
COMMIT;

-- 性能测试：UUIDv7（带错误处理）
BEGIN;
DO $$
BEGIN
    PERFORM gen_uuid_v7();
    RAISE NOTICE 'UUIDv7生成成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '生成UUIDv7失败: %', SQLERRM;
        RAISE;
END $$;
COMMIT;

-- 性能测试：GIN并行构建（带错误处理）
BEGIN;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_data ON docs USING GIN (data);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_data已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建GIN索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
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
-- 性能测试：终止查询（带错误处理）
BEGIN;
DO $$
DECLARE
    target_pid INT := 12345;  -- 替换为实际PID
BEGIN
    PERFORM pg_cancel_backend(target_pid);  -- 尝试取消
    RAISE NOTICE '已尝试取消查询: %', target_pid;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '取消查询失败: %', SQLERRM;
        RAISE;
END $$;
COMMIT;

-- 性能测试：强制终止（带错误处理）
BEGIN;
DO $$
DECLARE
    target_pid INT := 12345;  -- 替换为实际PID
BEGIN
    PERFORM pg_terminate_backend(target_pid);  -- 强制终止
    RAISE NOTICE '已强制终止查询: %', target_pid;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '终止查询失败: %', SQLERRM;
        RAISE;
END $$;
COMMIT;

-- 性能测试：终止所有空闲连接（带错误处理）
BEGIN;
DO $$
DECLARE
    terminated_count INT := 0;
BEGIN
    SELECT COUNT(*) INTO terminated_count
    FROM pg_stat_activity
    WHERE state = 'idle' AND pid != pg_backend_pid();

    PERFORM pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE state = 'idle' AND pid != pg_backend_pid();

    RAISE NOTICE '已终止 % 个空闲连接', terminated_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '终止空闲连接失败: %', SQLERRM;
        RAISE;
END $$;
COMMIT;

-- 性能测试：查看配置（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT name, setting, unit FROM pg_settings WHERE name = 'shared_buffers';
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查看配置失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：修改配置（带错误处理）
BEGIN;
DO $$
BEGIN
    ALTER SYSTEM SET work_mem = '128MB';
    PERFORM pg_reload_conf();
    RAISE NOTICE '配置已更新并重载';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '修改配置失败: %', SQLERRM;
        RAISE;
END $$;
COMMIT;

-- 性能测试：查看版本（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT version();
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查看版本失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查看运行时间（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT pg_postmaster_start_time();
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查看运行时间失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
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
