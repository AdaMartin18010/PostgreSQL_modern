---

> **📋 文档来源**: `PostgreSQL培训\06-应用开发\【深入】FDW外部数据包装器完整实战指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

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
| --- | --- | --- |
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
-- 1. 安装扩展（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
            CREATE EXTENSION postgres_fdw;
            RAISE NOTICE '扩展 postgres_fdw 创建成功';
        ELSE
            RAISE NOTICE '扩展 postgres_fdw 已存在';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '扩展 postgres_fdw 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建扩展失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 2. 创建服务器（Server）（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'foreign_server') THEN
            CREATE SERVER foreign_server
            FOREIGN DATA WRAPPER postgres_fdw
            OPTIONS (host 'remote-host', port '5432', dbname 'remotedb');
            RAISE NOTICE '外部服务器 foreign_server 创建成功';
        ELSE
            RAISE NOTICE '外部服务器 foreign_server 已存在';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '外部服务器已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建外部服务器失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 3. 创建用户映射（User Mapping）（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'foreign_server') THEN
            IF NOT EXISTS (SELECT 1 FROM pg_user_mappings WHERE srvname = 'foreign_server' AND usename = 'postgres') THEN
                CREATE USER MAPPING FOR postgres
                SERVER foreign_server
                OPTIONS (user 'remote_user', password 'remote_password');
                RAISE NOTICE '用户映射创建成功';
            ELSE
                RAISE NOTICE '用户映射已存在';
            END IF;
        ELSE
            RAISE NOTICE '外部服务器不存在，跳过用户映射创建';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '用户映射已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建用户映射失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 4. 创建外部表（Foreign Table）（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'foreign_server') THEN
            IF NOT EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'remote_users') THEN
                CREATE FOREIGN TABLE remote_users (
                    id INT,
                    username TEXT,
                    email TEXT
                )
                SERVER foreign_server
                OPTIONS (schema_name 'public', table_name 'users');
                RAISE NOTICE '外部表 remote_users 创建成功';
            ELSE
                RAISE NOTICE '外部表 remote_users 已存在';
            END IF;
        ELSE
            RAISE NOTICE '外部服务器不存在，跳过外部表创建';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE NOTICE '外部表已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建外部表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 5. 查询外部表（如本地表）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM remote_users WHERE id > 100
LIMIT 100;
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
-- 完整示例（带错误处理）
DO $$
BEGIN
    BEGIN
        -- 安装扩展
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
            CREATE EXTENSION postgres_fdw;
            RAISE NOTICE '扩展 postgres_fdw 创建成功';
        END IF;

        -- 创建服务器
        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
            CREATE SERVER remote_pg
            FOREIGN DATA WRAPPER postgres_fdw
            OPTIONS (host '192.168.1.100', port '5432', dbname 'app_db');
            RAISE NOTICE '外部服务器 remote_pg 创建成功';
        END IF;

        -- 创建用户映射
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
            IF NOT EXISTS (SELECT 1 FROM pg_user_mappings WHERE srvname = 'remote_pg') THEN
                CREATE USER MAPPING FOR current_user
                SERVER remote_pg
                OPTIONS (user 'app_user', password 'app_password');
                RAISE NOTICE '用户映射创建成功';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '对象已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建FDW对象失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 导入整个schema（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
            IMPORT FOREIGN SCHEMA public
            FROM SERVER remote_pg
            INTO public;
            RAISE NOTICE 'Schema导入成功';
        ELSE
            RAISE NOTICE '外部服务器不存在，跳过schema导入';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '导入schema失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 或导入特定表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
            IMPORT FOREIGN SCHEMA public
            LIMIT TO (users, orders)
            FROM SERVER remote_pg
            INTO public;
            RAISE NOTICE '特定表导入成功';
        ELSE
            RAISE NOTICE '外部服务器不存在，跳过表导入';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '导入表失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 3.2 跨库JOIN

```sql
-- 本地表 JOIN 远程表（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    lu.name AS local_user,
    ru.username AS remote_user,
    lu.total_orders
FROM local_users lu
JOIN remote_users ru ON lu.email = ru.email
WHERE lu.total_orders > 10
LIMIT 100;

-- 性能优化：本地表小、远程表大时，先过滤（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH local_emails AS (
    SELECT email FROM local_users WHERE total_orders > 10
)
SELECT ru.*
FROM remote_users ru
WHERE ru.email IN (SELECT email FROM local_emails)
LIMIT 100;
```

### 3.3 写入操作

```sql
-- FDW支持INSERT、UPDATE、DELETE（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'remote_users') THEN
            -- INSERT（带错误处理）
            BEGIN
                INSERT INTO remote_users (username, email)
                VALUES ('newuser', 'new@example.com');
                RAISE NOTICE 'INSERT成功';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING 'INSERT失败: %', SQLERRM;
            END;

            -- UPDATE（带错误处理）
            BEGIN
                UPDATE remote_users
                SET email = 'updated@example.com'
                WHERE id = 123;
                RAISE NOTICE 'UPDATE成功';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING 'UPDATE失败: %', SQLERRM;
            END;

            -- DELETE（带错误处理）
            BEGIN
                DELETE FROM remote_users WHERE id = 456;
                RAISE NOTICE 'DELETE成功';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING 'DELETE失败: %', SQLERRM;
            END;
        ELSE
            RAISE NOTICE '外部表 remote_users 不存在，跳过写入操作';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 事务支持（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'remote_users') AND
           EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'local_users') THEN
            BEGIN;
            INSERT INTO remote_users (username) VALUES ('user1');
            INSERT INTO local_users (name) VALUES ('user1');
            COMMIT;
            RAISE NOTICE '事务提交成功（两阶段提交（2PC）保证一致性）';
        ELSE
            RAISE NOTICE '表不存在，跳过事务操作';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '事务失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 4. file_fdw

### 4.1 读取CSV文件

```sql
-- file_fdw扩展和服务器（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'file_fdw') THEN
            CREATE EXTENSION file_fdw;
            RAISE NOTICE '扩展 file_fdw 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'file_server') THEN
            CREATE SERVER file_server
            FOREIGN DATA WRAPPER file_fdw;
            RAISE NOTICE '外部服务器 file_server 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '对象已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建file_fdw对象失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 创建外部表映射CSV（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'file_server') THEN
            IF NOT EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'sales_data') THEN
                CREATE FOREIGN TABLE sales_data (
                    date DATE,
                    product_id INT,
                    quantity INT,
                    amount NUMERIC(10,2)
                )
                SERVER file_server
                OPTIONS (filename '/data/sales_2024.csv', format 'csv', header 'true');
                RAISE NOTICE '外部表 sales_data 创建成功';
            ELSE
                RAISE NOTICE '外部表 sales_data 已存在';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE NOTICE '外部表已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建外部表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查询CSV（如普通表）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    DATE_TRUNC('month', date) AS month,
    SUM(amount) AS total_sales
FROM sales_data
WHERE date >= '2024-01-01'
GROUP BY month
ORDER BY month
LIMIT 100;

-- JOIN CSV + 数据库表（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    p.product_name,
    s.quantity,
    s.amount
FROM sales_data s
JOIN products p ON s.product_id = p.id
WHERE s.date = CURRENT_DATE
LIMIT 100;
```

### 4.2 读取日志文件

```sql
-- 创建外部表映射日志文件（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'file_server') THEN
            IF NOT EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'app_logs') THEN
                CREATE FOREIGN TABLE app_logs (
                    timestamp TEXT,
                    level TEXT,
                    message TEXT,
                    details TEXT
                )
                SERVER file_server
                OPTIONS (filename '/var/log/app.log', format 'csv', delimiter '|');
                RAISE NOTICE '外部表 app_logs 创建成功';
            ELSE
                RAISE NOTICE '外部表 app_logs 已存在';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE NOTICE '外部表已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建外部表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 分析日志（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    level,
    COUNT(*) AS count,
    COUNT(*) FILTER (WHERE message LIKE '%ERROR%') AS error_count
FROM app_logs
WHERE timestamp::TIMESTAMPTZ >= NOW() - INTERVAL '1 hour'
GROUP BY level
LIMIT 100;
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
-- mysql_fdw配置（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'mysql_fdw') THEN
            CREATE EXTENSION mysql_fdw;
            RAISE NOTICE '扩展 mysql_fdw 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mysql_server') THEN
            CREATE SERVER mysql_server
            FOREIGN DATA WRAPPER mysql_fdw
            OPTIONS (host '192.168.1.200', port '3306');
            RAISE NOTICE '外部服务器 mysql_server 创建成功';
        END IF;

        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mysql_server') THEN
            IF NOT EXISTS (SELECT 1 FROM pg_user_mappings WHERE srvname = 'mysql_server') THEN
                CREATE USER MAPPING FOR postgres
                SERVER mysql_server
                OPTIONS (username 'mysql_user', password 'mysql_password');
                RAISE NOTICE '用户映射创建成功';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '对象已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建mysql_fdw对象失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 导入MySQL表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mysql_server') THEN
            IMPORT FOREIGN SCHEMA mydb
            FROM SERVER mysql_server
            INTO public;
            RAISE NOTICE 'MySQL schema导入成功';
        ELSE
            RAISE NOTICE '外部服务器不存在，跳过schema导入';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '导入schema失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 5.2 跨数据库查询

```sql
-- PostgreSQL JOIN MySQL（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pg.order_id,
    pg.created_at,
    mysql.customer_name,
    mysql.customer_email
FROM pg_orders pg
JOIN mysql_customers mysql ON pg.customer_id = mysql.id
WHERE pg.created_at >= '2025-01-01'
LIMIT 100;

-- 数据迁移（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pg_orders') AND
           EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'mysql_orders') THEN
            INSERT INTO pg_orders (id, amount, customer_id)
            SELECT id, amount, customer_id
            FROM mysql_orders
            WHERE created_at >= '2024-01-01';
            RAISE NOTICE '数据迁移成功';
        ELSE
            RAISE NOTICE '表不存在，跳过数据迁移';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '数据迁移失败: %', SQLERRM;
            RAISE;
    END;
END $$;
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
-- mongo_fdw配置（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'mongo_fdw') THEN
            CREATE EXTENSION mongo_fdw;
            RAISE NOTICE '扩展 mongo_fdw 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mongo_server') THEN
            CREATE SERVER mongo_server
            FOREIGN DATA WRAPPER mongo_fdw
            OPTIONS (address '192.168.1.300', port '27017');
            RAISE NOTICE '外部服务器 mongo_server 创建成功';
        END IF;

        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mongo_server') THEN
            IF NOT EXISTS (SELECT 1 FROM pg_user_mappings WHERE srvname = 'mongo_server') THEN
                CREATE USER MAPPING FOR postgres
                SERVER mongo_server
                OPTIONS (username 'mongo_user', password 'mongo_password');
                RAISE NOTICE '用户映射创建成功';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '对象已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建mongo_fdw对象失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 创建外部表映射MongoDB集合（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mongo_server') THEN
            IF NOT EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'mongo_products') THEN
                CREATE FOREIGN TABLE mongo_products (
                    _id NAME,
                    name TEXT,
                    price NUMERIC,
                    specs JSONB
                )
                SERVER mongo_server
                OPTIONS (database 'shop', collection 'products');
                RAISE NOTICE '外部表 mongo_products 创建成功';
            ELSE
                RAISE NOTICE '外部表 mongo_products 已存在';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE NOTICE '外部表已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建外部表失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 6.2 MongoDB + PostgreSQL混合查询

```sql
-- PostgreSQL关系表 JOIN MongoDB文档（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    o.order_id,
    o.amount,
    mp.name AS product_name,
    mp.specs ->> 'brand' AS brand
FROM orders o
JOIN mongo_products mp ON o.product_id = mp._id::TEXT
WHERE o.created_at >= '2025-01-01'
LIMIT 100;

-- 聚合分析（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    mp.specs ->> 'category' AS category,
    COUNT(*) AS order_count,
    SUM(o.amount) AS total_revenue
FROM orders o
JOIN mongo_products mp ON o.product_id = mp._id::TEXT
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 100;
```

---

## 7. 其他常用FDW

### 7.1 redis_fdw

```sql
-- 访问Redis数据（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'redis_fdw') THEN
            CREATE EXTENSION redis_fdw;
            RAISE NOTICE '扩展 redis_fdw 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'redis_server') THEN
            CREATE SERVER redis_server
            FOREIGN DATA WRAPPER redis_fdw
            OPTIONS (address '127.0.0.1', port '6379');
            RAISE NOTICE '外部服务器 redis_server 创建成功';
        END IF;

        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'redis_server') THEN
            IF NOT EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'redis_cache') THEN
                CREATE FOREIGN TABLE redis_cache (
                    key TEXT,
                    value TEXT
                )
                SERVER redis_server
                OPTIONS (database '0');
                RAISE NOTICE '外部表 redis_cache 创建成功';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '对象已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建redis_fdw对象失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查询Redis（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM redis_cache WHERE key LIKE 'user:%'
LIMIT 100;
```

### 7.2 http_fdw

```sql
-- 访问REST API（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'http_fdw') THEN
            CREATE EXTENSION http_fdw;
            RAISE NOTICE '扩展 http_fdw 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'api_server') THEN
            CREATE SERVER api_server
            FOREIGN DATA WRAPPER http_fdw;
            RAISE NOTICE '外部服务器 api_server 创建成功';
        END IF;

        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'api_server') THEN
            IF NOT EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'github_users') THEN
                CREATE FOREIGN TABLE github_users (
                    login TEXT,
                    id INT,
                    avatar_url TEXT
                )
                SERVER api_server
                OPTIONS (uri 'https://api.github.com/users');
                RAISE NOTICE '外部表 github_users 创建成功';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '对象已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建http_fdw对象失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查询API数据（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM github_users LIMIT 10;
```

### 7.3 其他FDW扩展

| FDW | 数据源 | 用途 |
| --- | --- | --- |
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
-- postgres_fdw支持完整下推（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
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
-- 设置批量获取大小（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
            ALTER SERVER remote_pg
            OPTIONS (ADD fetch_size '10000');
            RAISE NOTICE '服务器批量获取大小设置成功';
        ELSE
            RAISE NOTICE '外部服务器不存在，跳过设置';
        END IF;

        IF EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'remote_users') THEN
            ALTER FOREIGN TABLE remote_users
            OPTIONS (ADD fetch_size '10000');
            RAISE NOTICE '外部表批量获取大小设置成功';
        ELSE
            RAISE NOTICE '外部表不存在，跳过设置';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '设置批量获取大小失败: %', SQLERRM;
            RAISE;
    END;
END $$;
-- 默认100行，增加到10000提升批量查询性能
```

### 8.3 连接池

```sql
-- 使用连接池避免频繁建立连接（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
            CREATE EXTENSION postgres_fdw;
            RAISE NOTICE '扩展 postgres_fdw 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '扩展已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建扩展失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查看当前连接（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
            SELECT * FROM postgres_fdw_get_connections() LIMIT 100;
            RAISE NOTICE '连接查询成功';
        ELSE
            RAISE NOTICE '扩展 postgres_fdw 未安装，跳过连接查询';
        END IF;
    EXCEPTION
        WHEN undefined_function THEN
            RAISE WARNING '函数 postgres_fdw_get_connections 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '查询连接失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 断开空闲连接（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
            SELECT postgres_fdw_disconnect('remote_pg');
            RAISE NOTICE '断开连接成功';
        ELSE
            RAISE NOTICE '扩展 postgres_fdw 未安装，跳过断开连接';
        END IF;
    EXCEPTION
        WHEN undefined_function THEN
            RAISE WARNING '函数 postgres_fdw_disconnect 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '断开连接失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 断开所有连接（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
            SELECT postgres_fdw_disconnect_all();
            RAISE NOTICE '断开所有连接成功';
        ELSE
            RAISE NOTICE '扩展 postgres_fdw 未安装，跳过断开连接';
        END IF;
    EXCEPTION
        WHEN undefined_function THEN
            RAISE WARNING '函数 postgres_fdw_disconnect_all 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '断开所有连接失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 9. 生产实战案例

### 9.1 案例1：数据仓库整合

```sql
-- 整合3个数据源：PostgreSQL + MySQL + MongoDB（带错误处理）

-- PostgreSQL（订单）（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'orders') THEN
            CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                customer_id INT,
                amount NUMERIC,
                created_at TIMESTAMPTZ
            );
            RAISE NOTICE '表 orders 创建成功';
        ELSE
            RAISE NOTICE '表 orders 已存在';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE NOTICE '表已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- MySQL（客户）和MongoDB（产品）的FDW配置需要单独创建
-- 注意：这里省略了具体的FDW创建代码，实际使用时需要完整配置

-- 统一查询（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
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
ORDER BY o.created_at DESC
LIMIT 100;
-- 单一SQL，整合3个数据库！
```

### 9.2 案例2：渐进式数据迁移

```sql
-- 从MySQL迁移到PostgreSQL（带错误处理）

-- 第1步：创建FDW连接（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mysql_legacy') THEN
            CREATE SERVER mysql_legacy FOREIGN DATA WRAPPER mysql_fdw
            OPTIONS (host 'legacy-mysql', port '3306');
            RAISE NOTICE '外部服务器 mysql_legacy 创建成功';
        END IF;

        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mysql_legacy') THEN
            IF NOT EXISTS (SELECT 1 FROM pg_user_mappings WHERE srvname = 'mysql_legacy') THEN
                CREATE USER MAPPING FOR postgres SERVER mysql_legacy
                OPTIONS (username 'root', password 'password');
                RAISE NOTICE '用户映射创建成功';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '对象已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建FDW连接失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 第2步：映射MySQL表（需要根据实际表结构创建）
-- 第3步：创建PostgreSQL表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'mysql_orders') THEN
            IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pg_orders') THEN
                CREATE TABLE pg_orders (LIKE mysql_orders);
                RAISE NOTICE '表 pg_orders 创建成功';
            END IF;
        END IF;

        IF EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'mysql_customers') THEN
            IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pg_customers') THEN
                CREATE TABLE pg_customers (LIKE mysql_customers);
                RAISE NOTICE '表 pg_customers 创建成功';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE NOTICE '表已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 第4步：历史数据迁移（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pg_orders') AND
           EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'mysql_orders') THEN
            INSERT INTO pg_orders SELECT * FROM mysql_orders
            WHERE created_at < '2025-01-01';
            RAISE NOTICE '历史订单数据迁移成功';
        END IF;

        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pg_customers') AND
           EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'mysql_customers') THEN
            INSERT INTO pg_customers SELECT * FROM mysql_customers;
            RAISE NOTICE '客户数据迁移成功';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '数据迁移失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 第5步：创建联合视图（过渡期）（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pg_orders') AND
           EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'mysql_orders') THEN
            DROP VIEW IF EXISTS orders_unified;
            CREATE VIEW orders_unified AS
            SELECT * FROM pg_orders          -- 新数据
            UNION ALL
            SELECT * FROM mysql_orders       -- 历史数据
            WHERE created_at >= '2025-01-01';
            RAISE NOTICE '联合视图 orders_unified 创建成功';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '创建视图失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 第6步：应用切换到unified视图
-- 应用无感知，渐进式迁移！
```

### 9.3 案例3：实时报表系统

```sql
-- 整合多个微服务数据库（带错误处理）

-- 服务1：用户服务（PostgreSQL）（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'user_service_db') THEN
            CREATE SERVER user_service_db FOREIGN DATA WRAPPER postgres_fdw
            OPTIONS (host 'user-service-db', dbname 'users');
            RAISE NOTICE '外部服务器 user_service_db 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '外部服务器已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建外部服务器失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 服务2：订单服务（MySQL）（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'order_service_db') THEN
            CREATE SERVER order_service_db FOREIGN DATA WRAPPER mysql_fdw
            OPTIONS (host 'order-service-db');
            RAISE NOTICE '外部服务器 order_service_db 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '外部服务器已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建外部服务器失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 服务3：产品服务（MongoDB）（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'product_service_db') THEN
            CREATE SERVER product_service_db FOREIGN DATA WRAPPER mongo_fdw
            OPTIONS (address 'product-service-db');
            RAISE NOTICE '外部服务器 product_service_db 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '外部服务器已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建外部服务器失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 实时报表查询（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
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
ORDER BY date DESC
LIMIT 100;
```

---

## 10. 最佳实践

### 10.1 性能优化

```sql
-- ✅ 1. 启用查询下推（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
            ALTER SERVER remote_pg
            OPTIONS (ADD extensions 'postgres_fdw');
            RAISE NOTICE '查询下推启用成功';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '启用查询下推失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- ✅ 2. 使用异步执行（PostgreSQL 14+）（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
            ALTER SERVER remote_pg
            OPTIONS (ADD async_capable 'true');
            RAISE NOTICE '异步执行启用成功';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '启用异步执行失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- ✅ 3. 增加批量大小（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'remote_table') THEN
            ALTER FOREIGN TABLE remote_table
            OPTIONS (ADD fetch_size '10000');
            RAISE NOTICE '批量大小设置成功';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '设置批量大小失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- ✅ 4. 在远程创建索引
-- 在远程数据库为外部表查询列创建索引

-- ✅ 5. 物化外部数据（频繁访问）（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'remote_table') THEN
            DROP MATERIALIZED VIEW IF EXISTS mv_remote_data;
            CREATE MATERIALIZED VIEW mv_remote_data AS
            SELECT * FROM remote_table WHERE active = TRUE;
            RAISE NOTICE '物化视图创建成功';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '创建物化视图失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 刷新物化视图（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_matviews WHERE matviewname = 'mv_remote_data') THEN
            REFRESH MATERIALIZED VIEW CONCURRENTLY mv_remote_data;
            RAISE NOTICE '物化视图刷新成功';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '刷新物化视图失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 10.2 安全建议

```sql
-- ❌ 不要在USER MAPPING中硬编码密码
-- CREATE USER MAPPING FOR postgres
-- SERVER remote_server
-- OPTIONS (user 'remote_user', password 'plain_text_password');  -- 危险！

-- ✅ 使用.pgpass文件
-- ~/.pgpass
-- hostname:port:database:username:password
-- remote-host:5432:remotedb:remote_user:secure_password

-- ✅ 或使用证书认证（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_server') THEN
            IF NOT EXISTS (SELECT 1 FROM pg_user_mappings WHERE srvname = 'remote_server') THEN
                CREATE USER MAPPING FOR postgres
                SERVER remote_server
                OPTIONS (sslcert '/path/to/client-cert.pem', sslkey '/path/to/client-key.pem');
                RAISE NOTICE '证书认证用户映射创建成功';
            END IF;
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '用户映射已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建用户映射失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- ✅ 限制访问权限（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_server') THEN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
                GRANT USAGE ON FOREIGN SERVER remote_server TO app_user;
                RAISE NOTICE '服务器权限授予成功';
            END IF;
        END IF;

        IF EXISTS (SELECT 1 FROM information_schema.foreign_tables WHERE foreign_table_name = 'remote_users') THEN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
                GRANT SELECT ON remote_users TO app_user;
                RAISE NOTICE '表权限授予成功（不授予INSERT/UPDATE/DELETE）';
            END IF;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '授予权限失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 10.3 监控

```sql
-- 查看FDW连接（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
            SELECT * FROM postgres_fdw_get_connections() LIMIT 100;
            RAISE NOTICE 'FDW连接查询成功';
        ELSE
            RAISE NOTICE '扩展 postgres_fdw 未安装，跳过连接查询';
        END IF;
    EXCEPTION
        WHEN undefined_function THEN
            RAISE WARNING '函数 postgres_fdw_get_connections 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '查询连接失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查看外部表统计（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan
FROM pg_stat_user_tables
WHERE tablename LIKE 'remote_%'
LIMIT 100;

-- 慢查询分析（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
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
