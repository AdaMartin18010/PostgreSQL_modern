# 【深入】FDW外部数据包装器完整实战指南

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 12+
> **难度等级**: ⭐⭐⭐⭐ 高级 | **预计学习时间**: 6-8小时

---

## 📋 目录

- [【深入】FDW外部数据包装器完整实战指南](#深入fdw外部数据包装器完整实战指南)
  - [📋 目录](#-目录)
  - [1. 课程概述](#1-课程概述)
    - [1.1 什么是FDW？](#11-什么是fdw)
      - [核心特性](#核心特性)
      - [适用场景](#适用场景)
    - [1.2 FDW架构](#12-fdw架构)
  - [2. FDW基础理论](#2-fdw基础理论)
    - [2.1 核心概念](#21-核心概念)
    - [2.2 FDW工作原理](#22-fdw工作原理)
  - [3. postgres\_fdw](#3-postgres_fdw)
    - [3.1 基础使用](#31-基础使用)
    - [3.2 跨库JOIN](#32-跨库join)
    - [3.3 写入操作](#33-写入操作)
  - [4. file\_fdw](#4-file_fdw)
    - [4.1 读取CSV文件](#41-读取csv文件)
    - [4.2 读取日志文件](#42-读取日志文件)
  - [5. mysql\_fdw](#5-mysql_fdw)
    - [5.1 安装配置](#51-安装配置)
    - [5.2 跨数据库查询](#52-跨数据库查询)
  - [6. mongo\_fdw](#6-mongo_fdw)
    - [6.1 安装配置](#61-安装配置)
    - [6.2 MongoDB + PostgreSQL混合查询](#62-mongodb--postgresql混合查询)
  - [7. 其他常用FDW](#7-其他常用fdw)
    - [7.1 redis\_fdw](#71-redis_fdw)
    - [7.2 http\_fdw](#72-http_fdw)
    - [7.3 其他FDW扩展](#73-其他fdw扩展)
  - [8. 性能优化](#8-性能优化)
    - [8.1 查询下推（Push Down）](#81-查询下推push-down)
    - [8.2 批量获取](#82-批量获取)
    - [8.3 连接池](#83-连接池)
  - [9. 生产实战案例](#9-生产实战案例)
    - [9.1 案例1：数据仓库整合](#91-案例1数据仓库整合)
    - [9.2 案例2：渐进式数据迁移](#92-案例2渐进式数据迁移)
    - [9.3 案例3：实时报表系统](#93-案例3实时报表系统)
  - [10. 最佳实践](#10-最佳实践)
    - [10.1 性能优化](#101-性能优化)
    - [10.2 安全建议](#102-安全建议)
    - [10.3 监控](#103-监控)
  - [📚 延伸阅读](#-延伸阅读)
    - [官方资源](#官方资源)
    - [推荐FDW](#推荐fdw)
  - [✅ 学习检查清单](#-学习检查清单)

---

## 1. 课程概述

### 1.1 什么是FDW？

**Foreign Data Wrapper（FDW）** 允许PostgreSQL访问外部数据源（其他数据库、文件、API），如同访问本地表。

#### 核心特性

| 特性 | 说明 | 价值 |
|------|------|------|
| **异构数据访问** | 访问MySQL、MongoDB等 | 数据整合 |
| **SQL统一查询** | 标准SQL查询外部数据 | 学习成本低 |
| **透明集成** | 外部表如本地表 | 无需应用层改造 |
| **联合查询** | JOIN本地表+外部表 | 跨库分析 |
| **写入支持** | 部分FDW支持写入 | 数据同步 |

#### 适用场景

```text
✅ 数据仓库（整合多个数据源）
✅ 数据迁移（渐进式迁移）
✅ 实时报表（跨库查询）
✅ 微服务架构（服务间数据访问）
✅ 遗留系统集成
✅ 文件数据导入（CSV、日志）
```

### 1.2 FDW架构

```text
┌─────────────────────────────────────────┐
│         PostgreSQL Server               │
├─────────────────────────────────────────┤
│  ┌──────────────────────────────────┐  │
│  │  SQL Query                       │  │
│  │  SELECT * FROM foreign_table     │  │
│  │  JOIN local_table ...            │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  Foreign Data Wrapper            │  │
│  │  - postgres_fdw                  │  │
│  │  - mysql_fdw                     │  │
│  │  - mongo_fdw                     │  │
│  │  - file_fdw                      │  │
│  └────────────┬─────────────────────┘  │
└───────────────┼─────────────────────────┘
                │
     ┌──────────┼──────────┐
     │          │          │
┌────▼────┐ ┌──▼───┐ ┌───▼──────┐
│MySQL DB │ │MongoDB│ │CSV Files│
└─────────┘ └───────┘ └─────────┘
```

---

## 2. FDW基础理论

### 2.1 核心概念

```sql
-- 1. 安装扩展
CREATE EXTENSION postgres_fdw;

-- 2. 创建服务器（Server）
CREATE SERVER foreign_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'remote-host', port '5432', dbname 'remotedb');

-- 3. 创建用户映射（User Mapping）
CREATE USER MAPPING FOR postgres
SERVER foreign_server
OPTIONS (user 'remote_user', password 'remote_password');

-- 4. 创建外部表（Foreign Table）
CREATE FOREIGN TABLE remote_users (
    id INT,
    username TEXT,
    email TEXT
)
SERVER foreign_server
OPTIONS (schema_name 'public', table_name 'users');

-- 5. 查询外部表（如本地表）
SELECT * FROM remote_users WHERE id > 100;
```

### 2.2 FDW工作原理

```text
查询执行流程：

1. SQL解析
   SELECT * FROM remote_users WHERE id > 100;

2. 查询计划
   Foreign Scan on remote_users
   Filter: (id > 100)

3. 下推优化（Push Down）
   FDW生成远程查询：
   SELECT id, username, email FROM users WHERE id > 100;

4. 执行远程查询
   通过网络连接远程数据库

5. 获取结果
   返回数据到PostgreSQL

6. 后处理
   应用无法下推的过滤、排序等
```

---

## 3. postgres_fdw

### 3.1 基础使用

```sql
-- 完整示例
CREATE EXTENSION postgres_fdw;

CREATE SERVER remote_pg
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host '192.168.1.100', port '5432', dbname 'app_db');

CREATE USER MAPPING FOR current_user
SERVER remote_pg
OPTIONS (user 'app_user', password 'app_password');

-- 导入整个schema
IMPORT FOREIGN SCHEMA public
FROM SERVER remote_pg
INTO public;

-- 或导入特定表
IMPORT FOREIGN SCHEMA public
LIMIT TO (users, orders)
FROM SERVER remote_pg
INTO public;
```

### 3.2 跨库JOIN

```sql
-- 本地表 JOIN 远程表
SELECT
    lu.name AS local_user,
    ru.username AS remote_user,
    lu.total_orders
FROM local_users lu
JOIN remote_users ru ON lu.email = ru.email
WHERE lu.total_orders > 10;

-- 性能优化：本地表小、远程表大时，先过滤
WITH local_emails AS (
    SELECT email FROM local_users WHERE total_orders > 10
)
SELECT ru.*
FROM remote_users ru
WHERE ru.email IN (SELECT email FROM local_emails);
```

### 3.3 写入操作

```sql
-- FDW支持INSERT、UPDATE、DELETE
INSERT INTO remote_users (username, email)
VALUES ('newuser', 'new@example.com');

UPDATE remote_users
SET email = 'updated@example.com'
WHERE id = 123;

DELETE FROM remote_users WHERE id = 456;

-- 事务支持
BEGIN;
INSERT INTO remote_users (username) VALUES ('user1');
INSERT INTO local_users (name) VALUES ('user1');
COMMIT;
-- 两阶段提交（2PC）保证一致性
```

---

## 4. file_fdw

### 4.1 读取CSV文件

```sql
CREATE EXTENSION file_fdw;

CREATE SERVER file_server
FOREIGN DATA WRAPPER file_fdw;

-- 创建外部表映射CSV
CREATE FOREIGN TABLE sales_data (
    date DATE,
    product_id INT,
    quantity INT,
    amount NUMERIC(10,2)
)
SERVER file_server
OPTIONS (filename '/data/sales_2024.csv', format 'csv', header 'true');

-- 查询CSV（如普通表）
SELECT
    DATE_TRUNC('month', date) AS month,
    SUM(amount) AS total_sales
FROM sales_data
WHERE date >= '2024-01-01'
GROUP BY month
ORDER BY month;

-- JOIN CSV + 数据库表
SELECT
    p.product_name,
    s.quantity,
    s.amount
FROM sales_data s
JOIN products p ON s.product_id = p.id
WHERE s.date = CURRENT_DATE;
```

### 4.2 读取日志文件

```sql
CREATE FOREIGN TABLE app_logs (
    timestamp TEXT,
    level TEXT,
    message TEXT,
    details TEXT
)
SERVER file_server
OPTIONS (filename '/var/log/app.log', format 'csv', delimiter '|');

-- 分析日志
SELECT
    level,
    COUNT(*) AS count,
    COUNT(*) FILTER (WHERE message LIKE '%ERROR%') AS error_count
FROM app_logs
WHERE timestamp::TIMESTAMPTZ >= NOW() - INTERVAL '1 hour'
GROUP BY level;
```

---

## 5. mysql_fdw

### 5.1 安装配置

```bash
# 安装mysql_fdw
git clone https://github.com/EnterpriseDB/mysql_fdw.git
cd mysql_fdw
export PATH=/usr/lib/postgresql/15/bin:$PATH
make USE_PGXS=1
sudo make USE_PGXS=1 install
```

```sql
CREATE EXTENSION mysql_fdw;

CREATE SERVER mysql_server
FOREIGN DATA WRAPPER mysql_fdw
OPTIONS (host '192.168.1.200', port '3306');

CREATE USER MAPPING FOR postgres
SERVER mysql_server
OPTIONS (username 'mysql_user', password 'mysql_password');

-- 导入MySQL表
IMPORT FOREIGN SCHEMA mydb
FROM SERVER mysql_server
INTO public;
```

### 5.2 跨数据库查询

```sql
-- PostgreSQL JOIN MySQL
SELECT
    pg.order_id,
    pg.created_at,
    mysql.customer_name,
    mysql.customer_email
FROM pg_orders pg
JOIN mysql_customers mysql ON pg.customer_id = mysql.id
WHERE pg.created_at >= '2025-01-01';

-- 数据迁移
INSERT INTO pg_orders (id, amount, customer_id)
SELECT id, amount, customer_id
FROM mysql_orders
WHERE created_at >= '2024-01-01';
```

---

## 6. mongo_fdw

### 6.1 安装配置

```bash
# 安装mongo_fdw
git clone https://github.com/EnterpriseDB/mongo_fdw.git
cd mongo_fdw
make USE_PGXS=1
sudo make USE_PGXS=1 install
```

```sql
CREATE EXTENSION mongo_fdw;

CREATE SERVER mongo_server
FOREIGN DATA WRAPPER mongo_fdw
OPTIONS (address '192.168.1.300', port '27017');

CREATE USER MAPPING FOR postgres
SERVER mongo_server
OPTIONS (username 'mongo_user', password 'mongo_password');

-- 创建外部表映射MongoDB集合
CREATE FOREIGN TABLE mongo_products (
    _id NAME,
    name TEXT,
    price NUMERIC,
    specs JSONB
)
SERVER mongo_server
OPTIONS (database 'shop', collection 'products');
```

### 6.2 MongoDB + PostgreSQL混合查询

```sql
-- PostgreSQL关系表 JOIN MongoDB文档
SELECT
    o.order_id,
    o.amount,
    mp.name AS product_name,
    mp.specs ->> 'brand' AS brand
FROM orders o
JOIN mongo_products mp ON o.product_id = mp._id::TEXT
WHERE o.created_at >= '2025-01-01';

-- 聚合分析
SELECT
    mp.specs ->> 'category' AS category,
    COUNT(*) AS order_count,
    SUM(o.amount) AS total_revenue
FROM orders o
JOIN mongo_products mp ON o.product_id = mp._id::TEXT
GROUP BY category
ORDER BY total_revenue DESC;
```

---

## 7. 其他常用FDW

### 7.1 redis_fdw

```sql
-- 访问Redis数据
CREATE EXTENSION redis_fdw;

CREATE SERVER redis_server
FOREIGN DATA WRAPPER redis_fdw
OPTIONS (address '127.0.0.1', port '6379');

CREATE FOREIGN TABLE redis_cache (
    key TEXT,
    value TEXT
)
SERVER redis_server
OPTIONS (database '0');

-- 查询Redis
SELECT * FROM redis_cache WHERE key LIKE 'user:%';
```

### 7.2 http_fdw

```sql
-- 访问REST API
CREATE EXTENSION http_fdw;

CREATE SERVER api_server
FOREIGN DATA WRAPPER http_fdw;

CREATE FOREIGN TABLE github_users (
    login TEXT,
    id INT,
    avatar_url TEXT
)
SERVER api_server
OPTIONS (uri 'https://api.github.com/users');

-- 查询API数据
SELECT * FROM github_users LIMIT 10;
```

### 7.3 其他FDW扩展

| FDW | 数据源 | 用途 |
|-----|--------|------|
| **oracle_fdw** | Oracle | Oracle集成 |
| **tds_fdw** | SQL Server | SQL Server集成 |
| **sqlite_fdw** | SQLite | SQLite集成 |
| **cstore_fdw** | 列式存储 | OLAP查询 |
| **parquet_fdw** | Parquet文件 | 大数据分析 |
| **s3_fdw** | AWS S3 | 云存储访问 |
| **kafka_fdw** | Kafka | 流数据集成 |

---

## 8. 性能优化

### 8.1 查询下推（Push Down）

```sql
-- postgres_fdw支持完整下推
EXPLAIN (VERBOSE)
SELECT * FROM remote_users
WHERE age > 25 AND city = 'Beijing'
ORDER BY created_at DESC
LIMIT 10;

-- 输出：
-- Foreign Scan on remote_users
--   Remote SQL: SELECT id, name, age, city, created_at
--                FROM public.users
--                WHERE ((age > 25)) AND ((city = 'Beijing'::text))
--                ORDER BY created_at DESC
--                LIMIT 10

-- 完全在远程执行，只传输10行结果 ✅
```

### 8.2 批量获取

```sql
-- 设置批量获取大小
ALTER SERVER remote_pg
OPTIONS (ADD fetch_size '10000');

-- 或在表级别设置
ALTER FOREIGN TABLE remote_users
OPTIONS (ADD fetch_size '10000');

-- 默认100行，增加到10000提升批量查询性能
```

### 8.3 连接池

```sql
-- 使用连接池避免频繁建立连接
CREATE EXTENSION postgres_fdw;

-- 查看当前连接
SELECT * FROM postgres_fdw_get_connections();

-- 断开空闲连接
SELECT postgres_fdw_disconnect('remote_pg');

-- 断开所有连接
SELECT postgres_fdw_disconnect_all();
```

---

## 9. 生产实战案例

### 9.1 案例1：数据仓库整合

```sql
-- 整合3个数据源：PostgreSQL + MySQL + MongoDB
-- PostgreSQL（订单）
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT,
    amount NUMERIC,
    created_at TIMESTAMPTZ
);

-- MySQL（客户）
CREATE SERVER mysql_server FOREIGN DATA WRAPPER mysql_fdw ...;
CREATE FOREIGN TABLE mysql_customers (...) SERVER mysql_server;

-- MongoDB（产品）
CREATE SERVER mongo_server FOREIGN DATA WRAPPER mongo_fdw ...;
CREATE FOREIGN TABLE mongo_products (...) SERVER mongo_server;

-- 统一查询
SELECT
    o.id AS order_id,
    mc.name AS customer_name,
    mc.email AS customer_email,
    mp.name AS product_name,
    mp.specs ->> 'brand' AS brand,
    o.amount
FROM orders o
JOIN mysql_customers mc ON o.customer_id = mc.id
JOIN mongo_products mp ON o.product_id = mp._id::TEXT
WHERE o.created_at >= '2025-01-01'
ORDER BY o.created_at DESC;

-- 单一SQL，整合3个数据库！
```

### 9.2 案例2：渐进式数据迁移

```sql
-- 从MySQL迁移到PostgreSQL

-- 第1步：创建FDW连接
CREATE SERVER mysql_legacy FOREIGN DATA WRAPPER mysql_fdw
OPTIONS (host 'legacy-mysql', port '3306');

CREATE USER MAPPING FOR postgres SERVER mysql_legacy
OPTIONS (username 'root', password 'password');

-- 第2步：映射MySQL表
CREATE FOREIGN TABLE mysql_orders (...) SERVER mysql_legacy;
CREATE FOREIGN TABLE mysql_customers (...) SERVER mysql_legacy;

-- 第3步：创建PostgreSQL表
CREATE TABLE pg_orders (LIKE mysql_orders);
CREATE TABLE pg_customers (LIKE mysql_customers);

-- 第4步：历史数据迁移
INSERT INTO pg_orders SELECT * FROM mysql_orders
WHERE created_at < '2025-01-01';

INSERT INTO pg_customers SELECT * FROM mysql_customers;

-- 第5步：创建联合视图（过渡期）
CREATE VIEW orders_unified AS
SELECT * FROM pg_orders          -- 新数据
UNION ALL
SELECT * FROM mysql_orders       -- 历史数据
WHERE created_at >= '2025-01-01';

-- 第6步：应用切换到unified视图
-- 应用无感知，渐进式迁移！
```

### 9.3 案例3：实时报表系统

```sql
-- 整合多个微服务数据库

-- 服务1：用户服务（PostgreSQL）
CREATE SERVER user_service_db FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'user-service-db', dbname 'users');

CREATE FOREIGN TABLE svc_users (...) SERVER user_service_db;

-- 服务2：订单服务（MySQL）
CREATE SERVER order_service_db FOREIGN DATA WRAPPER mysql_fdw
OPTIONS (host 'order-service-db');

CREATE FOREIGN TABLE svc_orders (...) SERVER order_service_db;

-- 服务3：产品服务（MongoDB）
CREATE SERVER product_service_db FOREIGN DATA WRAPPER mongo_fdw
OPTIONS (address 'product-service-db');

CREATE FOREIGN TABLE svc_products (...) SERVER product_service_db;

-- 实时报表查询
SELECT
    DATE(so.created_at) AS date,
    COUNT(DISTINCT su.id) AS active_users,
    COUNT(so.id) AS order_count,
    SUM(so.amount) AS total_revenue,
    AVG(so.amount) AS avg_order_value
FROM svc_orders so
JOIN svc_users su ON so.user_id = su.id
WHERE so.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(so.created_at)
ORDER BY date DESC;
```

---

## 10. 最佳实践

### 10.1 性能优化

```sql
-- ✅ 1. 启用查询下推
ALTER SERVER remote_pg
OPTIONS (ADD extensions 'postgres_fdw');

-- ✅ 2. 使用异步执行（PostgreSQL 14+）
ALTER SERVER remote_pg
OPTIONS (ADD async_capable 'true');

-- ✅ 3. 增加批量大小
ALTER FOREIGN TABLE remote_table
OPTIONS (ADD fetch_size '10000');

-- ✅ 4. 在远程创建索引
-- 在远程数据库为外部表查询列创建索引

-- ✅ 5. 物化外部数据（频繁访问）
CREATE MATERIALIZED VIEW mv_remote_data AS
SELECT * FROM remote_table WHERE active = TRUE;

REFRESH MATERIALIZED VIEW CONCURRENTLY mv_remote_data;
```

### 10.2 安全建议

```sql
-- ❌ 不要在USER MAPPING中硬编码密码
CREATE USER MAPPING FOR postgres
SERVER remote_server
OPTIONS (user 'remote_user', password 'plain_text_password');  -- 危险！

-- ✅ 使用.pgpass文件
-- ~/.pgpass
-- hostname:port:database:username:password
-- remote-host:5432:remotedb:remote_user:secure_password

-- ✅ 或使用证书认证
CREATE USER MAPPING FOR postgres
SERVER remote_server
OPTIONS (sslcert '/path/to/client-cert.pem', sslkey '/path/to/client-key.pem');

-- ✅ 限制访问权限
GRANT USAGE ON FOREIGN SERVER remote_server TO app_user;
GRANT SELECT ON remote_users TO app_user;
-- 不授予INSERT/UPDATE/DELETE
```

### 10.3 监控

```sql
-- 查看FDW连接
SELECT * FROM postgres_fdw_get_connections();

-- 查看外部表统计
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan
FROM pg_stat_user_tables
WHERE tablename LIKE 'remote_%';

-- 慢查询分析
SELECT query, mean_exec_time
FROM pg_stat_statements
WHERE query LIKE '%remote_%'
ORDER BY mean_exec_time DESC;
```

---

## 📚 延伸阅读

### 官方资源

- [PostgreSQL FDW Documentation](https://www.postgresql.org/docs/current/postgres-fdw.html)
- [FDW Extensions List](https://wiki.postgresql.org/wiki/Foreign_data_wrappers)

### 推荐FDW

- **postgres_fdw**: 跨PostgreSQL实例
- **mysql_fdw**: MySQL集成
- **mongo_fdw**: MongoDB集成
- **oracle_fdw**: Oracle集成
- **file_fdw**: CSV文件
- **multicorn**: Python自定义FDW

---

## ✅ 学习检查清单

- [ ] 理解FDW架构和工作原理
- [ ] 掌握postgres_fdw使用
- [ ] 能配置mysql_fdw/mongo_fdw
- [ ] 能进行跨库JOIN查询
- [ ] 理解查询下推优化
- [ ] 能设计数据迁移方案
- [ ] 掌握性能优化技巧

---

**文档维护**: 本文档持续更新以反映FDW生态最新发展。
**反馈**: 如发现错误或有改进建议，请提交issue。

**版本历史**:

- v1.0 (2025-01): 初始版本，覆盖主流FDW扩展
