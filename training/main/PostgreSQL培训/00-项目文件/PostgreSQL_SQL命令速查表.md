# PostgreSQL SQL 命令速查表

> **更新时间**: 2025 年 1 月
> **适用版本**: PostgreSQL 17+/18+
> **文档编号**: 00-01-07

---

## 📑 目录

- [PostgreSQL SQL 命令速查表](#postgresql-sql-命令速查表)
  - [📑 目录](#-目录)
  - [1. DDL - 数据定义](#1-ddl---数据定义)
    - [创建表](#创建表)
    - [修改表](#修改表)
    - [删除表](#删除表)
  - [2. DML - 数据操作](#2-dml---数据操作)
    - [插入数据](#插入数据)
    - [更新数据](#更新数据)
    - [删除数据](#删除数据)
  - [3. DQL - 数据查询](#3-dql---数据查询)
    - [基础查询](#基础查询)
    - [连接查询](#连接查询)
    - [子查询](#子查询)
    - [GROUP BY 和 HAVING](#group-by-和-having)
  - [4. 事务控制](#4-事务控制)
    - [基础事务](#基础事务)
    - [保存点](#保存点)
    - [隔离级别](#隔离级别)
    - [锁](#锁)
  - [5. 索引操作](#5-索引操作)
    - [创建索引](#创建索引)
    - [管理索引](#管理索引)
  - [6. 视图操作](#6-视图操作)
    - [创建视图](#创建视图)
    - [管理视图](#管理视图)
  - [7. 函数和触发器](#7-函数和触发器)
    - [创建函数](#创建函数)
    - [创建触发器](#创建触发器)
  - [8. 权限管理](#8-权限管理)
    - [用户和角色](#用户和角色)
    - [权限授予](#权限授予)
    - [权限撤销](#权限撤销)
    - [行级安全（RLS）](#行级安全rls)
  - [9. 分区表](#9-分区表)
    - [创建分区表](#创建分区表)
    - [管理分区](#管理分区)
  - [10. PostgreSQL 17/18 新语法](#10-postgresql-1718-新语法)
    - [MERGE 语句（PostgreSQL 17+）](#merge-语句postgresql-17)
    - [JSON 增强（PostgreSQL 17+）](#json-增强postgresql-17)
    - [异步 I/O（PostgreSQL 18+）](#异步-iopostgresql-18)
  - [🔧 常用系统查询](#-常用系统查询)
    - [查看数据库信息](#查看数据库信息)
    - [查看表信息](#查看表信息)
    - [查看索引信息](#查看索引信息)
  - [🎯 性能优化常用查询](#-性能优化常用查询)
    - [缓冲区命中率（应 \> 99%）](#缓冲区命中率应--99)
    - [表膨胀检查](#表膨胀检查)
    - [慢查询Top 10](#慢查询top-10)
  - [📚 相关文档](#-相关文档)
  - [💡 使用提示](#-使用提示)
    - [如何使用本速查表](#如何使用本速查表)
    - [打印建议](#打印建议)
    - [扩展使用](#扩展使用)

---

## 1. DDL - 数据定义

### 创建表

```sql
-- 基础表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    age INT CHECK (age >= 0 AND age <= 150),
    is_active BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 带外键的表
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 从查询结果创建表
CREATE TABLE active_users AS
SELECT * FROM users WHERE is_active = true;

-- 创建临时表
CREATE TEMP TABLE temp_data (
    id INT,
    value TEXT
);

-- 创建无日志表（更快，但不安全）
CREATE UNLOGGED TABLE cache_data (
    key TEXT PRIMARY KEY,
    value TEXT,
    expires_at TIMESTAMPTZ
);
```

### 修改表

```sql
-- 添加列
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- 删除列
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users DROP COLUMN IF EXISTS phone CASCADE;

-- 修改列类型
ALTER TABLE users ALTER COLUMN name TYPE TEXT;
ALTER TABLE users ALTER COLUMN age SET DATA TYPE BIGINT;

-- 修改列约束
ALTER TABLE users ALTER COLUMN name SET NOT NULL;
ALTER TABLE users ALTER COLUMN name DROP NOT NULL;
ALTER TABLE users ALTER COLUMN is_active SET DEFAULT false;

-- 重命名
ALTER TABLE users RENAME TO customers;
ALTER TABLE users RENAME COLUMN name TO full_name;

-- 添加约束
ALTER TABLE users ADD CONSTRAINT uk_email UNIQUE (email);
ALTER TABLE users ADD CONSTRAINT ck_age CHECK (age >= 0);
ALTER TABLE orders ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id);

-- 删除约束
ALTER TABLE users DROP CONSTRAINT uk_email;
```

### 删除表

```sql
-- 删除表
DROP TABLE users;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS users CASCADE;  -- 级联删除依赖对象

-- 清空表（比 DELETE 快）
TRUNCATE users;
TRUNCATE users RESTART IDENTITY;  -- 重置序列
TRUNCATE users CASCADE;  -- 级联清空关联表
```

---

## 2. DML - 数据操作

### 插入数据

```sql
-- 单行插入
INSERT INTO users (name, email) VALUES ('张三', 'zhang@example.com');

-- 多行插入
INSERT INTO users (name, email) VALUES
    ('李四', 'li@example.com'),
    ('王五', 'wang@example.com'),
    ('赵六', 'zhao@example.com');

-- 插入并返回
INSERT INTO users (name, email) VALUES ('张三', 'zhang@example.com')
RETURNING id, created_at;

-- 从查询插入
INSERT INTO active_users SELECT * FROM users WHERE is_active = true;

-- 冲突时更新（UPSERT）
INSERT INTO users (id, name, email) VALUES (1, '张三', 'zhang@example.com')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email;

-- 冲突时忽略
INSERT INTO users (email, name) VALUES ('test@example.com', 'Test')
ON CONFLICT (email) DO NOTHING;

-- 批量导入（最快）
COPY users (name, email) FROM '/path/to/data.csv' CSV HEADER;
COPY users (name, email) FROM STDIN CSV;
```

### 更新数据

```sql
-- 基础更新
UPDATE users SET name = '张三丰' WHERE id = 1;

-- 多列更新
UPDATE users SET
    name = '张三丰',
    email = 'zhang@new.com',
    updated_at = NOW()
WHERE id = 1;

-- 更新并返回
UPDATE users SET is_active = false WHERE id = 1
RETURNING *;

-- 从其他表更新
UPDATE users u SET name = t.new_name
FROM temp_updates t
WHERE u.id = t.user_id;

-- 批量更新
UPDATE users SET is_active = false
WHERE id IN (SELECT user_id FROM banned_users);

-- 条件更新
UPDATE users SET status =
    CASE
        WHEN age < 18 THEN 'minor'
        WHEN age < 60 THEN 'adult'
        ELSE 'senior'
    END;
```

### 删除数据

```sql
-- 基础删除
DELETE FROM users WHERE id = 1;

-- 条件删除
DELETE FROM users WHERE created_at < NOW() - INTERVAL '1 year';

-- 删除并返回
DELETE FROM users WHERE id = 1 RETURNING *;

-- 从关联表删除
DELETE FROM users WHERE id IN (
    SELECT user_id FROM orders WHERE status = 'cancelled'
);

-- 使用 USING 子句
DELETE FROM users u
USING orders o
WHERE u.id = o.user_id AND o.status = 'cancelled';
```

---

## 3. DQL - 数据查询

### 基础查询

```sql
-- SELECT 基础
SELECT * FROM users;
SELECT id, name, email FROM users;
SELECT DISTINCT status FROM orders;

-- WHERE 过滤
SELECT * FROM users WHERE age > 18;
SELECT * FROM users WHERE name LIKE '张%';
SELECT * FROM users WHERE email ILIKE '%@gmail.com';  -- 不区分大小写
SELECT * FROM users WHERE age BETWEEN 18 AND 60;
SELECT * FROM users WHERE status IN ('active', 'pending');
SELECT * FROM users WHERE email IS NULL;
SELECT * FROM users WHERE email IS NOT NULL;

-- 排序和限制
SELECT * FROM users ORDER BY created_at DESC;
SELECT * FROM users ORDER BY age DESC, name ASC;
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;
SELECT * FROM users ORDER BY id OFFSET 20 LIMIT 10;  -- 分页

-- 聚合
SELECT COUNT(*) FROM users;
SELECT COUNT(DISTINCT email) FROM users;
SELECT AVG(age), MAX(age), MIN(age), SUM(amount) FROM users;
```

### 连接查询

```sql
-- INNER JOIN
SELECT u.name, o.order_id
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN
SELECT u.name, o.order_id
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- RIGHT JOIN
SELECT u.name, o.order_id
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- FULL OUTER JOIN
SELECT u.name, o.order_id
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;

-- CROSS JOIN（笛卡尔积）
SELECT * FROM users CROSS JOIN products;

-- 多表连接
SELECT u.name, o.order_id, p.product_name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN products p ON o.product_id = p.id;
```

### 子查询

```sql
-- WHERE 子查询
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- SELECT 子查询
SELECT
    name,
    (SELECT COUNT(*) FROM orders WHERE user_id = users.id) AS order_count
FROM users;

-- FROM 子查询
SELECT * FROM (
    SELECT * FROM users WHERE age > 18
) AS adults
WHERE name LIKE '张%';

-- EXISTS 子查询（性能更好）
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

### GROUP BY 和 HAVING

```sql
-- 基础分组
SELECT status, COUNT(*) FROM orders GROUP BY status;

-- 多列分组
SELECT user_id, status, COUNT(*), SUM(amount)
FROM orders
GROUP BY user_id, status;

-- HAVING 过滤
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 10;

-- ROLLUP（小计和总计）
SELECT status, COUNT(*), SUM(amount)
FROM orders
GROUP BY ROLLUP(status);

-- CUBE（所有组合）
SELECT status, payment_method, SUM(amount)
FROM orders
GROUP BY CUBE(status, payment_method);
```

---

## 4. 事务控制

### 基础事务

```sql
-- 开始事务
BEGIN;
-- 或
START TRANSACTION;

-- 提交事务
COMMIT;

-- 回滚事务
ROLLBACK;

-- 完整示例
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

### 保存点

```sql
BEGIN;
    INSERT INTO users (name) VALUES ('张三');

    SAVEPOINT sp1;

    UPDATE users SET email = 'zhang@example.com' WHERE name = '张三';

    ROLLBACK TO SAVEPOINT sp1;  -- 回滚到保存点

    RELEASE SAVEPOINT sp1;  -- 释放保存点
COMMIT;
```

### 隔离级别

```sql
-- 设置事务隔离级别
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 设置会话默认隔离级别
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 查看当前隔离级别
SHOW transaction_isolation;
```

### 锁

```sql
-- 显式锁表
LOCK TABLE users IN ACCESS EXCLUSIVE MODE;
LOCK TABLE users IN SHARE MODE;

-- 行级锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;  -- 排他锁
SELECT * FROM users WHERE id = 1 FOR SHARE;   -- 共享锁
SELECT * FROM users FOR UPDATE SKIP LOCKED;   -- 跳过已锁定的行
SELECT * FROM users FOR UPDATE NOWAIT;        -- 不等待，立即返回错误
```

---

## 5. 索引操作

### 创建索引

```sql
-- B-tree 索引（默认）
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);  -- 在线创建

-- 唯一索引
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- 复合索引
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- 部分索引
CREATE INDEX idx_orders_pending ON orders(created_at)
WHERE status = 'pending';

-- 表达式索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- GIN 索引（JSONB、数组、全文搜索）
CREATE INDEX idx_products_properties ON products USING gin(properties);
CREATE INDEX idx_articles_tsv ON articles USING gin(tsv);

-- GiST 索引（范围、几何）
CREATE INDEX idx_events_period ON events USING gist(period);

-- BRIN 索引（大表，按顺序）
CREATE INDEX idx_logs_created ON logs USING brin(created_at);

-- HASH 索引（相等查询）
CREATE INDEX idx_users_email_hash ON users USING hash(email);
```

### 管理索引

```sql
-- 查看索引
\di                  -- psql命令
SELECT * FROM pg_indexes WHERE tablename = 'users';

-- 删除索引
DROP INDEX idx_users_email;
DROP INDEX CONCURRENTLY idx_users_email;  -- 在线删除

-- 重建索引
REINDEX INDEX idx_users_email;
REINDEX INDEX CONCURRENTLY idx_users_email;  -- 在线重建
REINDEX TABLE users;
REINDEX TABLE CONCURRENTLY users;

-- 查看索引使用情况
SELECT * FROM pg_stat_user_indexes WHERE indexrelname = 'idx_users_email';
```

---

## 6. 视图操作

### 创建视图

```sql
-- 普通视图
CREATE VIEW active_users AS
SELECT * FROM users WHERE is_active = true;

-- 或替换
CREATE OR REPLACE VIEW active_users AS
SELECT id, name, email FROM users WHERE is_active = true;

-- 物化视图
CREATE MATERIALIZED VIEW user_stats AS
SELECT
    user_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount
FROM orders
GROUP BY user_id;

-- 带数据创建
CREATE MATERIALIZED VIEW user_stats AS
SELECT ... WITH DATA;

-- 不带数据创建
CREATE MATERIALIZED VIEW user_stats AS
SELECT ... WITH NO DATA;
```

### 管理视图

```sql
-- 查看视图
\dv                  -- psql命令
SELECT * FROM information_schema.views;

-- 删除视图
DROP VIEW active_users;
DROP VIEW IF EXISTS active_users CASCADE;
DROP MATERIALIZED VIEW user_stats;

-- 刷新物化视图
REFRESH MATERIALIZED VIEW user_stats;
REFRESH MATERIALIZED VIEW CONCURRENTLY user_stats;  -- 在线刷新

-- 查看视图定义
\d+ active_users
SELECT definition FROM pg_views WHERE viewname = 'active_users';
```

---

## 7. 函数和触发器

### 创建函数

```sql
-- 简单函数
CREATE OR REPLACE FUNCTION get_user_age(user_id INT)
RETURNS INT AS $$
    SELECT age FROM users WHERE id = user_id;
$$ LANGUAGE sql;

-- PL/pgSQL 函数
CREATE OR REPLACE FUNCTION calculate_total(order_id INT)
RETURNS DECIMAL AS $$
DECLARE
    total DECIMAL;
BEGIN
    SELECT SUM(price * quantity) INTO total
    FROM order_items
    WHERE order_id = order_id;

    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- 返回表的函数
CREATE OR REPLACE FUNCTION get_active_users()
RETURNS TABLE(id INT, name TEXT, email TEXT) AS $$
BEGIN
    RETURN QUERY SELECT id, name, email FROM users WHERE is_active = true;
END;
$$ LANGUAGE plpgsql;

-- 删除函数
DROP FUNCTION get_user_age(INT);
```

### 创建触发器

```sql
-- 创建触发器函数
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_update_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- 删除触发器
DROP TRIGGER trigger_update_timestamp ON users;

-- 禁用/启用触发器
ALTER TABLE users DISABLE TRIGGER trigger_update_timestamp;
ALTER TABLE users ENABLE TRIGGER trigger_update_timestamp;
```

---

## 8. 权限管理

### 用户和角色

```sql
-- 创建用户
CREATE USER app_user WITH PASSWORD 'secure_password';
CREATE USER admin_user WITH SUPERUSER PASSWORD 'admin_password';

-- 创建角色
CREATE ROLE readonly;
CREATE ROLE readwrite;

-- 授予角色给用户
GRANT readonly TO app_user;
GRANT readwrite TO app_user;

-- 修改用户
ALTER USER app_user WITH PASSWORD 'new_password';
ALTER USER app_user WITH SUPERUSER;
ALTER USER app_user WITH NOSUPERUSER;

-- 删除用户
DROP USER app_user;
DROP USER IF EXISTS app_user;
```

### 权限授予

```sql
-- 数据库权限
GRANT ALL PRIVILEGES ON DATABASE mydb TO app_user;
GRANT CONNECT ON DATABASE mydb TO app_user;

-- 表权限
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO app_user;
GRANT ALL PRIVILEGES ON users TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;

-- 序列权限
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 函数权限
GRANT EXECUTE ON FUNCTION my_function TO app_user;

-- Schema 权限
GRANT ALL ON SCHEMA public TO app_user;

-- 默认权限（未来创建的对象）
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
```

### 权限撤销

```sql
-- 撤销表权限
REVOKE ALL PRIVILEGES ON users FROM app_user;
REVOKE INSERT, UPDATE, DELETE ON users FROM app_user;

-- 撤销数据库权限
REVOKE ALL PRIVILEGES ON DATABASE mydb FROM app_user;
```

### 行级安全（RLS）

```sql
-- 启用 RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY user_documents ON documents
FOR ALL TO app_user
USING (owner_id = current_setting('app.current_user_id')::INT);

-- 不同操作的策略
CREATE POLICY select_policy ON documents FOR SELECT
USING (is_public = true OR owner_id = current_user_id());

CREATE POLICY insert_policy ON documents FOR INSERT
WITH CHECK (owner_id = current_user_id());

-- 查看策略
\d+ documents
SELECT * FROM pg_policies WHERE tablename = 'documents';

-- 删除策略
DROP POLICY user_documents ON documents;
```

---

## 9. 分区表

### 创建分区表

```sql
-- 范围分区
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE NOT NULL,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (sale_date);

-- 创建分区
CREATE TABLE sales_2024_q1 PARTITION OF sales
FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE sales_2024_q2 PARTITION OF sales
FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- 列表分区
CREATE TABLE users_by_region (
    id SERIAL,
    name TEXT,
    region TEXT
) PARTITION BY LIST (region);

CREATE TABLE users_china PARTITION OF users_by_region
FOR VALUES IN ('CN', 'HK', 'TW');

-- 哈希分区
CREATE TABLE logs (
    id SERIAL,
    user_id INT,
    message TEXT
) PARTITION BY HASH (user_id);

CREATE TABLE logs_0 PARTITION OF logs
FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```

### 管理分区

```sql
-- 查看分区
SELECT * FROM pg_partitions WHERE tablename = 'sales';

-- 分离分区
ALTER TABLE sales DETACH PARTITION sales_2024_q1;

-- 附加分区
ALTER TABLE sales ATTACH PARTITION sales_2024_q1
FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- 删除分区
DROP TABLE sales_2024_q1;
```

---

## 10. PostgreSQL 17/18 新语法

### MERGE 语句（PostgreSQL 17+）

```sql
-- MERGE 示例
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET value = s.value
WHEN NOT MATCHED THEN
    INSERT (id, value) VALUES (s.id, s.value);

-- 带条件的 MERGE
MERGE INTO inventory i
USING orders o ON i.product_id = o.product_id
WHEN MATCHED AND o.quantity > 0 THEN
    UPDATE SET quantity = i.quantity - o.quantity
WHEN MATCHED AND i.quantity <= 0 THEN
    DELETE;
```

### JSON 增强（PostgreSQL 17+）

```sql
-- JSON_TABLE（将JSON转换为表）
SELECT * FROM json_table(
    '{"users": [{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}]}'::jsonb,
    '$.users[*]' COLUMNS (
        id INT PATH '$.id',
        name TEXT PATH '$.name'
    )
);

-- JSON 聚合增强
SELECT jsonb_agg(jsonb_build_object('id', id, 'name', name))
FROM users;
```

### 异步 I/O（PostgreSQL 18+）

```sql
-- 启用异步 I/O
ALTER SYSTEM SET enable_async_io = on;
SELECT pg_reload_conf();

-- 查看异步 I/O 状态
SHOW enable_async_io;
```

---

## 🔧 常用系统查询

### 查看数据库信息

```sql
-- 当前数据库
SELECT current_database();

-- 当前用户
SELECT current_user;

-- 数据库版本
SELECT version();

-- 数据库大小
SELECT pg_size_pretty(pg_database_size(current_database()));

-- 运行时间
SELECT pg_postmaster_start_time(),
       now() - pg_postmaster_start_time() AS uptime;
```

### 查看表信息

```sql
-- 表列表
SELECT * FROM pg_tables WHERE schemaname = 'public';

-- 表大小
SELECT
    schemaname, tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 表统计
SELECT * FROM pg_stat_user_tables WHERE tablename = 'users';

-- 表的行数估算
SELECT reltuples::bigint FROM pg_class WHERE relname = 'users';
```

### 查看索引信息

```sql
-- 索引列表
SELECT * FROM pg_indexes WHERE tablename = 'users';

-- 索引大小
SELECT
    schemaname, tablename, indexname,
    pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes;

-- 索引使用情况
SELECT
    indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public';
```

---

## 🎯 性能优化常用查询

### 缓冲区命中率（应 > 99%）

```sql
SELECT
    round(100.0 * sum(blks_hit) / NULLIF(sum(blks_hit + blks_read), 0), 2) AS cache_hit_ratio
FROM pg_stat_database;
```

### 表膨胀检查

```sql
SELECT
    schemaname, tablename,
    n_dead_tup, n_live_tup,
    round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS bloat_pct,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### 慢查询Top 10

```sql
SELECT
    substring(query, 1, 100) AS short_query,
    calls,
    round(total_exec_time::numeric, 2) AS total_ms,
    round(mean_exec_time::numeric, 2) AS avg_ms
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 📚 相关文档

- 📖 [SQL基础培训](../01-SQL基础/SQL基础培训.md)
- 📖 [高级SQL特性](../02-SQL高级特性/高级SQL特性.md)
- 📖 [索引与查询优化](../01-SQL基础/索引与查询优化.md)
- 📖 [性能调优深入](../11-性能调优/性能调优深入.md)
- 📖 [PostgreSQL快速参考卡片集](./PostgreSQL快速参考卡片集.md)

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
**文档编号**: 00-01-07

---

## 💡 使用提示

### 如何使用本速查表

1. **快速查找**：使用Ctrl+F搜索关键词
2. **日常参考**：保存到收藏夹，随时查阅
3. **学习工具**：配合详细文档深入学习
4. **团队共享**：分享给团队成员，统一操作规范

### 打印建议

- 可以打印出来放在手边
- 建议双面打印，节省纸张
- 可以按模块分别打印

### 扩展使用

本速查表可以配合以下文档使用：

- [常见问题快速查询手册](./PostgreSQL常见问题快速查询手册.md) - 问题诊断
- [性能调优检查清单](./PostgreSQL性能调优检查清单.md) - 性能优化
- [学习路径完整指南](./PostgreSQL学习路径完整指南.md) - 系统学习
