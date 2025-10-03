# 联邦查询实战案例 — Federated Queries with Foreign Data Wrappers

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **难度等级**：⭐⭐⭐⭐ 高级  
> **预计时间**：60-90分钟  
> **适合场景**：跨库查询、异构数据源集成、数据湖查询、遗留系统集成

---

## 📋 案例目标

构建一个生产级的联邦查询系统，包括：

1. ✅ 跨PostgreSQL数据库查询（postgres_fdw）
2. ✅ 查询MySQL/MongoDB/CSV/API等外部数据源
3. ✅ 分布式JOIN与查询优化
4. ✅ 数据虚拟化与联邦视图
5. ✅ 跨库事务与一致性保证

---

## 🎯 业务场景

**场景描述**：多数据源统一查询平台

- **数据源**：
  - PostgreSQL OLTP库（订单数据）
  - MySQL遗留系统（用户数据）
  - MongoDB（日志数据）
  - CSV文件（外部数据）
  - REST API（第三方服务）
- **需求**：
  - 统一SQL接口查询所有数据源
  - 支持跨库JOIN
  - 最小化数据迁移成本
  - 实时数据访问

---

## 🏗️ 架构设计

```text
应用层
    ↓
PostgreSQL（联邦查询中心）
    ├── postgres_fdw → 远程PostgreSQL
    ├── mysql_fdw → MySQL
    ├── mongo_fdw → MongoDB
    ├── file_fdw → CSV文件
    └── http_fdw → REST API
```

---

## 📦 1. 方案一：postgres_fdw（跨PostgreSQL查询）

### 1.1 安装与配置

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- 查看已安装的FDW
SELECT * FROM pg_foreign_data_wrapper;

-- 创建外部服务器
CREATE SERVER remote_pg_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (
        host 'remote-db.example.com',
        port '5432',
        dbname 'orders_db'
    );

-- 创建用户映射（本地用户 → 远程用户）
CREATE USER MAPPING FOR current_user
    SERVER remote_pg_server
    OPTIONS (
        user 'remote_user',
        password 'remote_password'
    );

-- 或者使用更安全的方式（密码存储在pgpass文件）
CREATE USER MAPPING FOR current_user
    SERVER remote_pg_server
    OPTIONS (
        user 'remote_user'
    );
-- 然后在 ~/.pgpass 文件添加：
-- remote-db.example.com:5432:orders_db:remote_user:remote_password
```

### 1.2 创建外部表

```sql
-- 方式1：手动创建外部表
CREATE FOREIGN TABLE remote_orders (
    id bigint,
    user_id bigint,
    product_name text,
    quantity int,
    price numeric(10,2),
    status text,
    created_at timestamptz
)
SERVER remote_pg_server
OPTIONS (
    schema_name 'public',
    table_name 'orders'
);

-- 方式2：自动导入整个schema
IMPORT FOREIGN SCHEMA public
    FROM SERVER remote_pg_server
    INTO public;

-- 方式3：选择性导入
IMPORT FOREIGN SCHEMA public
    LIMIT TO (orders, order_items)
    FROM SERVER remote_pg_server
    INTO public;

-- 查看外部表
SELECT 
    foreign_table_schema,
    foreign_table_name,
    foreign_server_name
FROM information_schema.foreign_tables;
```

### 1.3 查询外部表

```sql
-- 直接查询远程表
SELECT * FROM remote_orders WHERE status = 'pending' LIMIT 10;

-- 跨库JOIN（本地users表 + 远程orders表）
CREATE TABLE local_users (
    id bigint PRIMARY KEY,
    username text NOT NULL,
    email text NOT NULL,
    created_at timestamptz DEFAULT now()
);

INSERT INTO local_users VALUES
(1, 'alice', 'alice@example.com', now()),
(2, 'bob', 'bob@example.com', now()),
(3, 'charlie', 'charlie@example.com', now());

-- 联邦JOIN查询
SELECT 
    u.username,
    u.email,
    o.id AS order_id,
    o.product_name,
    o.price,
    o.created_at
FROM 
    local_users u
JOIN 
    remote_orders o ON u.id = o.user_id
WHERE 
    o.status = 'completed'
    AND o.created_at > now() - interval '30 days'
ORDER BY 
    o.created_at DESC
LIMIT 100;
```

### 1.4 查询优化

```sql
-- 查看执行计划
EXPLAIN (ANALYZE, VERBOSE)
SELECT * FROM remote_orders WHERE status = 'pending';

-- 输出分析：
-- Foreign Scan on public.remote_orders
--   Remote SQL: SELECT id, user_id, ... FROM public.orders WHERE status = 'pending'
-- 注意：WHERE条件被推送到远程服务器执行（predicate pushdown）

-- 查看实际发送到远程的SQL
EXPLAIN (VERBOSE)
SELECT COUNT(*) FROM remote_orders WHERE created_at > '2025-01-01';

-- 创建索引（在远程服务器上）
-- 注意：需要直接连接远程服务器执行
-- CREATE INDEX idx_orders_status ON orders(status);
-- CREATE INDEX idx_orders_created_at ON orders(created_at);
```

---

## 📦 2. 方案二：file_fdw（查询CSV文件）

### 2.1 配置file_fdw

```sql
-- file_fdw通常已预装
CREATE EXTENSION IF NOT EXISTS file_fdw;

-- 创建文件服务器
CREATE SERVER csv_server
    FOREIGN DATA WRAPPER file_fdw;
```

### 2.2 创建CSV外部表

```sql
-- 准备CSV文件（放在服务器可访问位置）
-- /var/lib/postgresql/data/sales_data.csv：
-- product_id,product_name,sales,revenue,date
-- 1,Product A,100,5000.00,2025-01-01
-- 2,Product B,150,7500.00,2025-01-02

-- 创建外部表
CREATE FOREIGN TABLE sales_data_csv (
    product_id int,
    product_name text,
    sales int,
    revenue numeric(12,2),
    sale_date date
)
SERVER csv_server
OPTIONS (
    filename '/var/lib/postgresql/data/sales_data.csv',
    format 'csv',
    header 'true',
    delimiter ',',
    null ''
);

-- 查询CSV数据
SELECT * FROM sales_data_csv;

-- 与本地数据JOIN
SELECT 
    p.name AS product_name,
    p.category,
    s.sales AS csv_sales,
    s.revenue AS csv_revenue,
    s.sale_date
FROM 
    local_products p
JOIN 
    sales_data_csv s ON p.id = s.product_id
ORDER BY 
    s.revenue DESC;
```

### 2.3 导入CSV数据到本地表

```sql
-- 将CSV数据导入到本地表（物化）
CREATE TABLE sales_data_local AS
SELECT * FROM sales_data_csv;

-- 或使用INSERT
INSERT INTO sales_data_local
SELECT * FROM sales_data_csv
WHERE sale_date > '2025-01-01';
```

---

## 📦 3. 方案三：mysql_fdw（查询MySQL）

### 3.1 安装mysql_fdw

```bash
-- 注意：mysql_fdw需要单独安装
-- Ubuntu/Debian:
sudo apt-get install postgresql-17-mysql-fdw

-- CentOS/RHEL:
sudo yum install mysql_fdw_17

-- 编译安装:
git clone https://github.com/EnterpriseDB/mysql_fdw.git
cd mysql_fdw
make USE_PGXS=1
sudo make USE_PGXS=1 install
```

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS mysql_fdw;

-- 创建MySQL服务器
CREATE SERVER mysql_server
    FOREIGN DATA WRAPPER mysql_fdw
    OPTIONS (
        host 'mysql-server.example.com',
        port '3306'
    );

-- 创建用户映射
CREATE USER MAPPING FOR current_user
    SERVER mysql_server
    OPTIONS (
        username 'mysql_user',
        password 'mysql_password'
    );
```

### 3.2 创建MySQL外部表

```sql
-- 手动创建外部表
CREATE FOREIGN TABLE mysql_legacy_users (
    id int,
    username varchar(50),
    email varchar(100),
    created_at timestamp
)
SERVER mysql_server
OPTIONS (
    dbname 'legacy_db',
    table_name 'users'
);

-- 查询MySQL数据
SELECT * FROM mysql_legacy_users LIMIT 10;

-- 跨数据库JOIN（PostgreSQL + MySQL）
SELECT 
    mu.username AS mysql_user,
    mu.email,
    o.id AS pg_order_id,
    o.product_name,
    o.created_at
FROM 
    mysql_legacy_users mu
JOIN 
    local_orders o ON mu.id = o.user_id
WHERE 
    o.status = 'completed'
ORDER BY 
    o.created_at DESC;
```

---

## 📦 4. 方案四：mongodb_fdw（查询MongoDB）

### 4.1 安装mongodb_fdw

```bash
-- 编译安装
git clone https://github.com/EnterpriseDB/mongo_fdw.git
cd mongo_fdw
make USE_PGXS=1
sudo make USE_PGXS=1 install
```

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS mongo_fdw;

-- 创建MongoDB服务器
CREATE SERVER mongo_server
    FOREIGN DATA WRAPPER mongo_fdw
    OPTIONS (
        address 'mongodb-server.example.com',
        port '27017'
    );

-- 创建用户映射
CREATE USER MAPPING FOR current_user
    SERVER mongo_server
    OPTIONS (
        username 'mongo_user',
        password 'mongo_password'
    );
```

### 4.2 创建MongoDB外部表

```sql
-- 创建外部表（映射MongoDB集合）
CREATE FOREIGN TABLE mongo_logs (
    _id name,
    level text,
    message text,
    timestamp timestamp,
    metadata jsonb
)
SERVER mongo_server
OPTIONS (
    database 'logs_db',
    collection 'application_logs'
);

-- 查询MongoDB数据
SELECT 
    level,
    message,
    timestamp,
    metadata->>'user_id' AS user_id
FROM 
    mongo_logs
WHERE 
    level = 'ERROR'
    AND timestamp > now() - interval '1 hour'
ORDER BY 
    timestamp DESC
LIMIT 100;
```

---

## 🚀 5. 高级特性

### 5.1 联邦视图（统一查询接口）

```sql
-- 创建联邦视图：统一用户数据
CREATE VIEW unified_users AS
-- PostgreSQL本地用户
SELECT 
    'pg' AS source,
    id,
    username,
    email,
    created_at
FROM local_users
UNION ALL
-- MySQL遗留用户
SELECT 
    'mysql' AS source,
    id,
    username,
    email,
    created_at
FROM mysql_legacy_users;

-- 查询所有来源的用户
SELECT 
    source,
    COUNT(*) AS user_count,
    MAX(created_at) AS latest_created_at
FROM unified_users
GROUP BY source;
```

### 5.2 跨库事务（限制）

```sql
-- PostgreSQL FDW支持两阶段提交（2PC）
-- 但需要特殊配置，且有性能影响

-- 示例：跨库更新（单独事务）
BEGIN;

-- 更新本地表
UPDATE local_users SET email = 'newemail@example.com' WHERE id = 1;

-- 更新远程表（通过FDW）
UPDATE remote_orders SET status = 'cancelled' WHERE user_id = 1 AND status = 'pending';

COMMIT;

-- 注意：FDW默认使用独立事务，可能不满足ACID要求
-- 生产环境建议使用应用层事务协调或消息队列
```

### 5.3 数据聚合与ETL

```sql
-- 创建物化视图：定期聚合远程数据
CREATE MATERIALIZED VIEW order_summary_materialized AS
SELECT 
    DATE_TRUNC('day', o.created_at) AS order_date,
    u.username,
    COUNT(*) AS order_count,
    SUM(o.price * o.quantity) AS total_revenue
FROM 
    remote_orders o
JOIN 
    local_users u ON o.user_id = u.id
WHERE 
    o.status = 'completed'
GROUP BY 
    order_date, u.username;

-- 创建唯一索引
CREATE UNIQUE INDEX idx_order_summary_date_user 
    ON order_summary_materialized(order_date, username);

-- 定期刷新（可使用pg_cron定时任务）
REFRESH MATERIALIZED VIEW CONCURRENTLY order_summary_materialized;

-- 查询物化视图（快速）
SELECT * FROM order_summary_materialized
WHERE order_date > now() - interval '7 days'
ORDER BY total_revenue DESC;
```

---

## 📊 6. 性能优化

### 6.1 谓词下推（Predicate Pushdown）

```sql
-- FDW自动将WHERE条件推送到远程服务器
EXPLAIN (VERBOSE)
SELECT * FROM remote_orders
WHERE status = 'completed'
  AND created_at > '2025-01-01'
  AND price > 100;

-- 输出：
-- Foreign Scan on remote_orders
--   Remote SQL: SELECT ... FROM orders 
--                WHERE status = 'completed' 
--                  AND created_at > '2025-01-01'
--                  AND price > 100

-- 优化建议：
-- 1. 在WHERE子句中使用远程表的索引列
-- 2. 避免在远程列上使用本地函数（破坏下推）
-- 3. 尽量减少数据传输量
```

### 6.2 批量数据传输

```sql
-- 配置fetch_size（减少网络往返）
ALTER FOREIGN TABLE remote_orders
    OPTIONS (ADD fetch_size '10000');

-- 查看当前配置
SELECT 
    foreign_table_name,
    option_name,
    option_value
FROM information_schema.foreign_table_options
WHERE foreign_table_name = 'remote_orders';
```

### 6.3 异步执行（PG 17优化）

```sql
-- PostgreSQL 17改进了FDW并行查询
SET max_parallel_workers_per_gather = 4;

EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    o.status,
    COUNT(*) AS order_count,
    AVG(o.price) AS avg_price
FROM remote_orders o
GROUP BY o.status;

-- 查看是否使用并行扫描
-- Gather
--   Workers Planned: 2
--   -> Parallel Foreign Scan on remote_orders
```

---

## 🎨 7. 监控与故障排查

### 7.1 监控外部连接

```sql
-- 查看活动的FDW连接
SELECT 
    srvname AS server_name,
    usename AS user_name,
    COUNT(*) AS connection_count
FROM pg_stat_activity
WHERE backend_type = 'client backend'
  AND application_name LIKE '%fdw%'
GROUP BY srvname, usename;

-- 查看FDW查询统计
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables
WHERE tablename IN (
    SELECT foreign_table_name
    FROM information_schema.foreign_tables
);
```

### 7.2 故障处理

```sql
-- 测试外部服务器连接
DO $$
BEGIN
    PERFORM * FROM remote_orders LIMIT 1;
    RAISE NOTICE 'Connection to remote_orders successful';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Connection failed: %', SQLERRM;
END $$;

-- 禁用故障的外部表（临时）
ALTER FOREIGN TABLE remote_orders
    OPTIONS (SET use_remote_estimate 'false');

-- 删除外部表（不影响远程数据）
DROP FOREIGN TABLE IF EXISTS remote_orders;

-- 删除服务器（需要先删除所有外部表和用户映射）
DROP USER MAPPING IF EXISTS FOR current_user SERVER remote_pg_server;
DROP SERVER IF EXISTS remote_pg_server CASCADE;
```

---

## ✅ 8. 完整示例：多数据源统一查询

```sql
-- 场景：生成跨数据源的用户订单报表

-- 1. 配置所有外部数据源
CREATE SERVER pg_orders_server FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'orders-db.example.com', dbname 'orders', port '5432');
CREATE USER MAPPING FOR current_user SERVER pg_orders_server
    OPTIONS (user 'reader', password 'password');

CREATE FOREIGN TABLE pg_orders (
    id bigint,
    user_id bigint,
    total numeric(10,2),
    status text,
    created_at timestamptz
) SERVER pg_orders_server OPTIONS (table_name 'orders');

-- 2. 创建统一查询视图
CREATE VIEW user_order_report AS
SELECT 
    u.id AS user_id,
    u.username,
    u.email,
    COUNT(o.id) AS total_orders,
    SUM(o.total) AS total_spent,
    MAX(o.created_at) AS last_order_date,
    ARRAY_AGG(o.status) AS order_statuses
FROM 
    local_users u
LEFT JOIN 
    pg_orders o ON u.id = o.user_id
WHERE 
    o.created_at > now() - interval '90 days'
GROUP BY 
    u.id, u.username, u.email;

-- 3. 查询报表
SELECT 
    username,
    email,
    total_orders,
    round(total_spent, 2) AS total_spent,
    last_order_date
FROM user_order_report
WHERE total_orders > 0
ORDER BY total_spent DESC
LIMIT 20;
```

---

## 📚 9. 最佳实践

### 9.1 架构设计

- ✅ 集中式联邦查询中心（单点查询）
- ✅ 最小化跨库JOIN（优先本地计算）
- ✅ 使用物化视图缓存远程数据
- ✅ 定期刷新而非实时查询

### 9.2 性能优化

- ✅ 在远程表上创建索引
- ✅ 利用谓词下推
- ✅ 配置合理的fetch_size
- ✅ 避免SELECT *

### 9.3 安全与权限

- ✅ 使用只读账号访问远程数据
- ✅ 在pgpass中存储密码
- ✅ 限制外部表访问权限
- ✅ 记录审计日志

### 9.4 运维管理

- ✅ 监控外部连接健康
- ✅ 定期测试故障转移
- ✅ 文档化所有外部依赖
- ✅ 设置超时和重试策略

---

## 🎯 10. 练习任务

1. **基础练习**：
   - 创建跨PostgreSQL数据库的联邦查询
   - 查询CSV文件数据
   - 实现本地表与远程表JOIN

2. **进阶练习**：
   - 配置MySQL FDW并查询遗留系统
   - 创建统一的联邦视图
   - 实现物化视图定期刷新

3. **挑战任务**：
   - 构建多数据源ETL流程
   - 优化跨库JOIN性能（10万+数据）
   - 实现跨数据库的事务一致性保证

---

## 📖 11. FDW扩展列表

| FDW | 数据源 | 用途 | 官方支持 |
|-----|--------|------|---------|
| **postgres_fdw** | PostgreSQL | 跨PG查询 | ✅ 官方 |
| **file_fdw** | CSV/文本文件 | 文件数据 | ✅ 官方 |
| **mysql_fdw** | MySQL/MariaDB | MySQL集成 | ❌ 第三方 |
| **mongo_fdw** | MongoDB | NoSQL集成 | ❌ 第三方 |
| **oracle_fdw** | Oracle | Oracle集成 | ❌ 第三方 |
| **redis_fdw** | Redis | 缓存查询 | ❌ 第三方 |
| **clickhouse_fdw** | ClickHouse | OLAP查询 | ❌ 第三方 |
| **http_fdw** | REST API | API数据 | ❌ 第三方 |

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**下一步**：查看 [实时分析案例](../realtime_analytics/README.md)
