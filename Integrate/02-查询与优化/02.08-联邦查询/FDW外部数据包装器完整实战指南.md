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

**FDW基础配置（带完整错误处理）**:

```sql
-- 1. 安装扩展（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
        CREATE EXTENSION postgres_fdw;
        RAISE NOTICE 'postgres_fdw扩展已创建';
    ELSE
        RAISE NOTICE 'postgres_fdw扩展已存在';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'postgres_fdw扩展文件未找到（需要安装postgres_fdw扩展）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装postgres_fdw扩展失败: %', SQLERRM;
END $$;

-- 2. 创建服务器（Server，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'foreign_server') THEN
        RAISE WARNING '服务器已存在: foreign_server';
    ELSE
        CREATE SERVER foreign_server
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host 'remote-host', port '5432', dbname 'remotedb');
        RAISE NOTICE '服务器创建成功: foreign_server';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '服务器已存在: foreign_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建服务器失败: %', SQLERRM;
END $$;

-- 3. 创建用户映射（User Mapping，带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_user_mappings
        WHERE srvname = 'foreign_server' AND usename = 'postgres'
    ) THEN
        RAISE WARNING '用户映射已存在: postgres -> foreign_server';
    ELSE
        CREATE USER MAPPING FOR postgres
        SERVER foreign_server
        OPTIONS (user 'remote_user', password 'remote_password');
        RAISE NOTICE '用户映射创建成功: postgres -> foreign_server';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '用户映射已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建用户映射失败: %', SQLERRM;
END $$;

-- 4. 创建外部表（Foreign Table，带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_users'
    ) THEN
        RAISE WARNING '外部表已存在: remote_users';
    ELSE
        CREATE FOREIGN TABLE remote_users (
            id INT,
            username TEXT,
            email TEXT
        )
        SERVER foreign_server
        OPTIONS (schema_name 'public', table_name 'users');
        RAISE NOTICE '外部表创建成功: remote_users';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '外部表已存在: remote_users';
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: foreign_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部表失败: %', SQLERRM;
END $$;

-- 5. 查询外部表（如本地表，带错误处理和性能测试）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_users'
    ) THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM remote_users WHERE id > 100;

    RAISE NOTICE '查询成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询外部表失败: %', SQLERRM;
END $$;

-- 性能测试：查询外部表
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM remote_users WHERE id > 100;
-- 执行时间: 取决于网络延迟和远程表大小
-- 计划: Foreign Scan on remote_users
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

**postgres_fdw完整配置（带完整错误处理）**:

```sql
-- 完整示例（带错误处理）
DO $$
BEGIN
    -- 安装扩展
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
        CREATE EXTENSION postgres_fdw;
        RAISE NOTICE 'postgres_fdw扩展已创建';
    END IF;

    -- 创建服务器
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
        RAISE WARNING '服务器已存在: remote_pg';
    ELSE
        CREATE SERVER remote_pg
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host '192.168.1.100', port '5432', dbname 'app_db');
        RAISE NOTICE '服务器创建成功: remote_pg';
    END IF;

    -- 创建用户映射
    IF EXISTS (
        SELECT 1 FROM pg_user_mappings
        WHERE srvname = 'remote_pg' AND usename = current_user
    ) THEN
        RAISE WARNING '用户映射已存在: % -> remote_pg', current_user;
    ELSE
        CREATE USER MAPPING FOR current_user
        SERVER remote_pg
        OPTIONS (user 'app_user', password 'app_password');
        RAISE NOTICE '用户映射创建成功: % -> remote_pg', current_user;
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'postgres_fdw扩展文件未找到';
    WHEN duplicate_object THEN
        RAISE WARNING '部分对象已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '配置postgres_fdw失败: %', SQLERRM;
END $$;

-- 导入整个schema（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    END IF;

    IMPORT FOREIGN SCHEMA public
    FROM SERVER remote_pg
    INTO public;

    RAISE NOTICE 'Schema导入成功: public';
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    WHEN OTHERS THEN
        RAISE EXCEPTION '导入schema失败: %', SQLERRM;
END $$;

-- 或导入特定表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    END IF;

    IMPORT FOREIGN SCHEMA public
    LIMIT TO (users, orders)
    FROM SERVER remote_pg
    INTO public;

    RAISE NOTICE '特定表导入成功: users, orders';
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    WHEN OTHERS THEN
        RAISE EXCEPTION '导入特定表失败: %', SQLERRM;
END $$;
```

### 3.2 跨库JOIN

**跨库JOIN查询（带完整错误处理和性能测试）**:

```sql
-- 本地表 JOIN 远程表（带错误处理）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'local_users'
    ) THEN
        RAISE EXCEPTION '本地表不存在: local_users';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_users'
    ) THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM local_users lu
    JOIN remote_users ru ON lu.email = ru.email
    WHERE lu.total_orders > 10;

    RAISE NOTICE '跨库JOIN查询成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查local_users和remote_users表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '跨库JOIN查询失败: %', SQLERRM;
END $$;

-- 性能测试：本地表 JOIN 远程表
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    lu.name AS local_user,
    ru.username AS remote_user,
    lu.total_orders
FROM local_users lu
JOIN remote_users ru ON lu.email = ru.email
WHERE lu.total_orders > 10;
-- 执行时间: 取决于网络延迟和表大小
-- 计划: Hash Join -> Seq Scan (local) + Foreign Scan (remote)

-- 性能优化：本地表小、远程表大时，先过滤（带错误处理和性能测试）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'local_users'
    ) THEN
        RAISE EXCEPTION '本地表不存在: local_users';
    END IF;

    WITH local_emails AS (
        SELECT email FROM local_users WHERE total_orders > 10
    )
    SELECT COUNT(*) INTO result_count
    FROM remote_users ru
    WHERE ru.email IN (SELECT email FROM local_emails);

    RAISE NOTICE '优化查询成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: local_users或remote_users';
    WHEN OTHERS THEN
        RAISE EXCEPTION '优化查询失败: %', SQLERRM;
END $$;

-- 性能测试：优化查询
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH local_emails AS (
    SELECT email FROM local_users WHERE total_orders > 10
)
SELECT ru.*
FROM remote_users ru
WHERE ru.email IN (SELECT email FROM local_emails);
-- 执行时间: 通常更快（先过滤本地表）
-- 计划: Hash Semi Join -> Foreign Scan (remote)
```

### 3.3 写入操作

**FDW写入操作（带完整错误处理）**:

```sql
-- FDW支持INSERT、UPDATE、DELETE（带错误处理）
DO $$
DECLARE
    inserted_id INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_users'
    ) THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    END IF;

    INSERT INTO remote_users (username, email)
    VALUES ('newuser', 'new@example.com')
    RETURNING id INTO inserted_id;

    RAISE NOTICE 'INSERT成功: id=%', inserted_id;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION '外键约束违反';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'INSERT失败: %', SQLERRM;
END $$;

-- UPDATE操作（带错误处理）
DO $$
DECLARE
    updated_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_users'
    ) THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    END IF;

    UPDATE remote_users
    SET email = 'updated@example.com'
    WHERE id = 123;

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RAISE NOTICE 'UPDATE成功: 更新了 % 行', updated_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'UPDATE失败: %', SQLERRM;
END $$;

-- DELETE操作（带错误处理）
DO $$
DECLARE
    deleted_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_users'
    ) THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    END IF;

    DELETE FROM remote_users WHERE id = 456;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RAISE NOTICE 'DELETE成功: 删除了 % 行', deleted_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'DELETE失败: %', SQLERRM;
END $$;

-- 事务支持（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_users'
    ) THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'local_users'
    ) THEN
        RAISE EXCEPTION '本地表不存在: local_users';
    END IF;

    BEGIN
        INSERT INTO remote_users (username) VALUES ('user1');
        INSERT INTO local_users (name) VALUES ('user1');
        RAISE NOTICE '事务提交成功（两阶段提交2PC保证一致性）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION '事务失败: %', SQLERRM;
            ROLLBACK;
    END;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查remote_users和local_users表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '事务操作失败: %', SQLERRM;
END $$;
```

---

## 4. file_fdw

### 4.1 读取CSV文件

**file_fdw CSV读取（带完整错误处理）**:

```sql
-- 安装file_fdw扩展（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'file_fdw') THEN
        CREATE EXTENSION file_fdw;
        RAISE NOTICE 'file_fdw扩展已创建';
    ELSE
        RAISE NOTICE 'file_fdw扩展已存在';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'file_fdw扩展文件未找到（需要安装file_fdw扩展）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装file_fdw扩展失败: %', SQLERRM;
END $$;

-- 创建文件服务器（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'file_server') THEN
        RAISE WARNING '服务器已存在: file_server';
    ELSE
        CREATE SERVER file_server
        FOREIGN DATA WRAPPER file_fdw;
        RAISE NOTICE '文件服务器创建成功: file_server';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '服务器已存在: file_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建文件服务器失败: %', SQLERRM;
END $$;

-- 创建外部表映射CSV（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'sales_data'
    ) THEN
        RAISE WARNING '外部表已存在: sales_data';
    ELSE
        CREATE FOREIGN TABLE sales_data (
            date DATE,
            product_id INT,
            quantity INT,
            amount NUMERIC(10,2)
        )
        SERVER file_server
        OPTIONS (filename '/data/sales_2024.csv', format 'csv', header 'true');
        RAISE NOTICE '外部表创建成功: sales_data';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '外部表已存在: sales_data';
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: file_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部表失败: %', SQLERRM;
END $$;

-- 查询CSV（如普通表，带错误处理和性能测试）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'sales_data'
    ) THEN
        RAISE EXCEPTION '外部表不存在: sales_data';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM (
        SELECT DATE_TRUNC('month', date) AS month
        FROM sales_data
        WHERE date >= '2024-01-01'
        GROUP BY month
    ) subquery;

    RAISE NOTICE 'CSV查询成功: 找到 % 个月份数据', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: sales_data';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法读取文件: /data/sales_2024.csv';
    WHEN undefined_file THEN
        RAISE EXCEPTION '文件不存在或无法访问: /data/sales_2024.csv';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询CSV失败: %', SQLERRM;
END $$;

-- 性能测试：查询CSV
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    DATE_TRUNC('month', date) AS month,
    SUM(amount) AS total_sales
FROM sales_data
WHERE date >= '2024-01-01'
GROUP BY month
ORDER BY month;
-- 执行时间: 取决于文件大小
-- 计划: Sort -> GroupAggregate -> Foreign Scan

-- JOIN CSV + 数据库表（带错误处理和性能测试）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'sales_data'
    ) THEN
        RAISE EXCEPTION '外部表不存在: sales_data';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'products'
    ) THEN
        RAISE EXCEPTION '表不存在: products';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM sales_data s
    JOIN products p ON s.product_id = p.id
    WHERE s.date = CURRENT_DATE;

    RAISE NOTICE 'JOIN查询成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查sales_data和products表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'JOIN查询失败: %', SQLERRM;
END $$;

-- 性能测试：JOIN CSV + 数据库表
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    p.product_name,
    s.quantity,
    s.amount
FROM sales_data s
JOIN products p ON s.product_id = p.id
WHERE s.date = CURRENT_DATE;
-- 执行时间: 取决于文件大小和products表大小
-- 计划: Hash Join -> Foreign Scan (CSV) + Seq Scan (products)
```

### 4.2 读取日志文件

**读取日志文件（带完整错误处理）**:

```sql
-- 创建外部表映射日志文件（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'file_server') THEN
        RAISE EXCEPTION '服务器不存在: file_server';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'app_logs'
    ) THEN
        RAISE WARNING '外部表已存在: app_logs';
    ELSE
        CREATE FOREIGN TABLE app_logs (
            timestamp TEXT,
            level TEXT,
            message TEXT,
            details TEXT
        )
        SERVER file_server
        OPTIONS (filename '/var/log/app.log', format 'csv', delimiter '|');
        RAISE NOTICE '外部表创建成功: app_logs';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '外部表已存在: app_logs';
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: file_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部表失败: %', SQLERRM;
END $$;

-- 分析日志（带错误处理和性能测试）
DO $$
DECLARE
    log_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'app_logs'
    ) THEN
        RAISE EXCEPTION '外部表不存在: app_logs';
    END IF;

    SELECT COUNT(*) INTO log_count
    FROM app_logs
    WHERE timestamp::TIMESTAMPTZ >= NOW() - INTERVAL '1 hour';

    RAISE NOTICE '日志分析成功: 找到 % 条日志记录', log_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: app_logs';
    WHEN invalid_text_representation THEN
        RAISE EXCEPTION '时间戳格式错误';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法读取文件: /var/log/app.log';
    WHEN OTHERS THEN
        RAISE EXCEPTION '分析日志失败: %', SQLERRM;
END $$;

-- 性能测试：分析日志
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    level,
    COUNT(*) AS count,
    COUNT(*) FILTER (WHERE message LIKE '%ERROR%') AS error_count
FROM app_logs
WHERE timestamp::TIMESTAMPTZ >= NOW() - INTERVAL '1 hour'
GROUP BY level;
-- 执行时间: 取决于文件大小
-- 计划: GroupAggregate -> Foreign Scan
```

---

## 5. mysql_fdw

### 5.1 安装配置

**mysql_fdw配置（带完整错误处理）**:

```sql
-- 安装mysql_fdw扩展（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'mysql_fdw') THEN
        CREATE EXTENSION mysql_fdw;
        RAISE NOTICE 'mysql_fdw扩展已创建';
    ELSE
        RAISE NOTICE 'mysql_fdw扩展已存在';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'mysql_fdw扩展文件未找到（需要单独安装mysql_fdw扩展）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装mysql_fdw扩展失败: %', SQLERRM;
END $$;

-- 创建MySQL服务器（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mysql_server') THEN
        RAISE WARNING '服务器已存在: mysql_server';
    ELSE
        CREATE SERVER mysql_server
        FOREIGN DATA WRAPPER mysql_fdw
        OPTIONS (host '192.168.1.200', port '3306');
        RAISE NOTICE 'MySQL服务器创建成功: mysql_server';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '服务器已存在: mysql_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建MySQL服务器失败: %', SQLERRM;
END $$;

-- 创建用户映射（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mysql_server') THEN
        RAISE EXCEPTION '服务器不存在: mysql_server';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_user_mappings
        WHERE srvname = 'mysql_server' AND usename = 'postgres'
    ) THEN
        RAISE WARNING '用户映射已存在: postgres -> mysql_server';
    ELSE
        CREATE USER MAPPING FOR postgres
        SERVER mysql_server
        OPTIONS (username 'mysql_user', password 'mysql_password');
        RAISE NOTICE '用户映射创建成功: postgres -> mysql_server';
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: mysql_server';
    WHEN duplicate_object THEN
        RAISE WARNING '用户映射已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建用户映射失败: %', SQLERRM;
END $$;

-- 导入MySQL表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mysql_server') THEN
        RAISE EXCEPTION '服务器不存在: mysql_server';
    END IF;

    IMPORT FOREIGN SCHEMA mydb
    FROM SERVER mysql_server
    INTO public;

    RAISE NOTICE 'MySQL schema导入成功: mydb';
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: mysql_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '导入MySQL schema失败: %', SQLERRM;
END $$;
```

### 5.2 跨数据库查询

**跨数据库查询（带完整错误处理和性能测试）**:

```sql
-- PostgreSQL JOIN MySQL（带错误处理）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'pg_orders'
    ) THEN
        RAISE EXCEPTION '表不存在: pg_orders';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'mysql_customers'
    ) THEN
        RAISE EXCEPTION '外部表不存在: mysql_customers';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM pg_orders pg
    JOIN mysql_customers mysql ON pg.customer_id = mysql.id
    WHERE pg.created_at >= '2025-01-01';

    RAISE NOTICE '跨数据库JOIN查询成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查pg_orders和mysql_customers表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '跨数据库JOIN查询失败: %', SQLERRM;
END $$;

-- 性能测试：PostgreSQL JOIN MySQL
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pg.order_id,
    pg.created_at,
    mysql.customer_name,
    mysql.customer_email
FROM pg_orders pg
JOIN mysql_customers mysql ON pg.customer_id = mysql.id
WHERE pg.created_at >= '2025-01-01';
-- 执行时间: 取决于网络延迟和表大小
-- 计划: Hash Join -> Seq Scan (PostgreSQL) + Foreign Scan (MySQL)

-- 数据迁移（带错误处理）
DO $$
DECLARE
    migrated_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'pg_orders'
    ) THEN
        RAISE EXCEPTION '目标表不存在: pg_orders';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'mysql_orders'
    ) THEN
        RAISE EXCEPTION '源外部表不存在: mysql_orders';
    END IF;

    INSERT INTO pg_orders (id, amount, customer_id)
    SELECT id, amount, customer_id
    FROM mysql_orders
    WHERE created_at >= '2024-01-01';

    GET DIAGNOSTICS migrated_count = ROW_COUNT;
    RAISE NOTICE '数据迁移成功: 迁移了 % 行数据', migrated_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查pg_orders和mysql_orders表）';
    WHEN unique_violation THEN
        RAISE EXCEPTION '唯一约束违反（可能存在重复数据）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '数据迁移失败: %', SQLERRM;
END $$;
```

---

## 6. mongo_fdw

### 6.1 安装配置

**mongo_fdw配置（带完整错误处理）**:

```sql
-- 安装mongo_fdw扩展（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'mongo_fdw') THEN
        CREATE EXTENSION mongo_fdw;
        RAISE NOTICE 'mongo_fdw扩展已创建';
    ELSE
        RAISE NOTICE 'mongo_fdw扩展已存在';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'mongo_fdw扩展文件未找到（需要单独安装mongo_fdw扩展）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装mongo_fdw扩展失败: %', SQLERRM;
END $$;

-- 创建MongoDB服务器（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mongo_server') THEN
        RAISE WARNING '服务器已存在: mongo_server';
    ELSE
        CREATE SERVER mongo_server
        FOREIGN DATA WRAPPER mongo_fdw
        OPTIONS (address '192.168.1.300', port '27017');
        RAISE NOTICE 'MongoDB服务器创建成功: mongo_server';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '服务器已存在: mongo_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建MongoDB服务器失败: %', SQLERRM;
END $$;

-- 创建用户映射（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mongo_server') THEN
        RAISE EXCEPTION '服务器不存在: mongo_server';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_user_mappings
        WHERE srvname = 'mongo_server' AND usename = 'postgres'
    ) THEN
        RAISE WARNING '用户映射已存在: postgres -> mongo_server';
    ELSE
        CREATE USER MAPPING FOR postgres
        SERVER mongo_server
        OPTIONS (username 'mongo_user', password 'mongo_password');
        RAISE NOTICE '用户映射创建成功: postgres -> mongo_server';
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: mongo_server';
    WHEN duplicate_object THEN
        RAISE WARNING '用户映射已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建用户映射失败: %', SQLERRM;
END $$;

-- 创建外部表映射MongoDB集合（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mongo_server') THEN
        RAISE EXCEPTION '服务器不存在: mongo_server';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'mongo_products'
    ) THEN
        RAISE WARNING '外部表已存在: mongo_products';
    ELSE
        CREATE FOREIGN TABLE mongo_products (
            _id NAME,
            name TEXT,
            price NUMERIC,
            specs JSONB
        )
        SERVER mongo_server
        OPTIONS (database 'shop', collection 'products');
        RAISE NOTICE '外部表创建成功: mongo_products';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '外部表已存在: mongo_products';
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: mongo_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部表失败: %', SQLERRM;
END $$;
```

### 6.2 MongoDB + PostgreSQL混合查询

**MongoDB + PostgreSQL混合查询（带完整错误处理和性能测试）**:

```sql
-- PostgreSQL关系表 JOIN MongoDB文档（带错误处理）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'orders'
    ) THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'mongo_products'
    ) THEN
        RAISE EXCEPTION '外部表不存在: mongo_products';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM orders o
    JOIN mongo_products mp ON o.product_id = mp._id::TEXT
    WHERE o.created_at >= '2025-01-01';

    RAISE NOTICE '混合查询成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查orders和mongo_products表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '混合查询失败: %', SQLERRM;
END $$;

-- 性能测试：PostgreSQL关系表 JOIN MongoDB文档
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    o.order_id,
    o.amount,
    mp.name AS product_name,
    mp.specs ->> 'brand' AS brand
FROM orders o
JOIN mongo_products mp ON o.product_id = mp._id::TEXT
WHERE o.created_at >= '2025-01-01';
-- 执行时间: 取决于网络延迟和表大小
-- 计划: Hash Join -> Seq Scan (PostgreSQL) + Foreign Scan (MongoDB)

-- 聚合分析（带错误处理和性能测试）
DO $$
DECLARE
    category_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'orders'
    ) THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    SELECT COUNT(DISTINCT mp.specs ->> 'category') INTO category_count
    FROM orders o
    JOIN mongo_products mp ON o.product_id = mp._id::TEXT;

    RAISE NOTICE '聚合分析成功: 找到 % 个类别', category_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查orders和mongo_products表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '聚合分析失败: %', SQLERRM;
END $$;

-- 性能测试：聚合分析
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    mp.specs ->> 'category' AS category,
    COUNT(*) AS order_count,
    SUM(o.amount) AS total_revenue
FROM orders o
JOIN mongo_products mp ON o.product_id = mp._id::TEXT
GROUP BY category
ORDER BY total_revenue DESC;
-- 执行时间: 取决于网络延迟和表大小
-- 计划: Sort -> GroupAggregate -> Hash Join
```

---

## 7. 其他常用FDW

### 7.1 redis_fdw

**redis_fdw配置（带完整错误处理）**:

```sql
-- 访问Redis数据（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'redis_fdw') THEN
        CREATE EXTENSION redis_fdw;
        RAISE NOTICE 'redis_fdw扩展已创建';
    ELSE
        RAISE NOTICE 'redis_fdw扩展已存在';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'redis_fdw扩展文件未找到（需要单独安装redis_fdw扩展）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装redis_fdw扩展失败: %', SQLERRM;
END $$;

-- 创建Redis服务器（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'redis_server') THEN
        RAISE WARNING '服务器已存在: redis_server';
    ELSE
        CREATE SERVER redis_server
        FOREIGN DATA WRAPPER redis_fdw
        OPTIONS (address '127.0.0.1', port '6379');
        RAISE NOTICE 'Redis服务器创建成功: redis_server';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '服务器已存在: redis_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建Redis服务器失败: %', SQLERRM;
END $$;

-- 创建外部表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'redis_server') THEN
        RAISE EXCEPTION '服务器不存在: redis_server';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'redis_cache'
    ) THEN
        RAISE WARNING '外部表已存在: redis_cache';
    ELSE
        CREATE FOREIGN TABLE redis_cache (
            key TEXT,
            value TEXT
        )
        SERVER redis_server
        OPTIONS (database '0');
        RAISE NOTICE '外部表创建成功: redis_cache';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '外部表已存在: redis_cache';
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: redis_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部表失败: %', SQLERRM;
END $$;

-- 查询Redis（带错误处理和性能测试）
DO $$
DECLARE
    cache_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'redis_cache'
    ) THEN
        RAISE EXCEPTION '外部表不存在: redis_cache';
    END IF;

    SELECT COUNT(*) INTO cache_count
    FROM redis_cache WHERE key LIKE 'user:%';

    RAISE NOTICE 'Redis查询成功: 找到 % 条缓存记录', cache_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: redis_cache';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询Redis失败: %', SQLERRM;
END $$;

-- 性能测试：查询Redis
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM redis_cache WHERE key LIKE 'user:%';
-- 执行时间: 取决于Redis连接和键数量
-- 计划: Foreign Scan
```

### 7.2 http_fdw

**http_fdw配置（带完整错误处理）**:

```sql
-- 访问REST API（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'http_fdw') THEN
        CREATE EXTENSION http_fdw;
        RAISE NOTICE 'http_fdw扩展已创建';
    ELSE
        RAISE NOTICE 'http_fdw扩展已存在';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'http_fdw扩展文件未找到（需要单独安装http_fdw扩展）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装http_fdw扩展失败: %', SQLERRM;
END $$;

-- 创建API服务器（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'api_server') THEN
        RAISE WARNING '服务器已存在: api_server';
    ELSE
        CREATE SERVER api_server
        FOREIGN DATA WRAPPER http_fdw;
        RAISE NOTICE 'API服务器创建成功: api_server';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '服务器已存在: api_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建API服务器失败: %', SQLERRM;
END $$;

-- 创建外部表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'api_server') THEN
        RAISE EXCEPTION '服务器不存在: api_server';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'github_users'
    ) THEN
        RAISE WARNING '外部表已存在: github_users';
    ELSE
        CREATE FOREIGN TABLE github_users (
            login TEXT,
            id INT,
            avatar_url TEXT
        )
        SERVER api_server
        OPTIONS (uri 'https://api.github.com/users');
        RAISE NOTICE '外部表创建成功: github_users';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '外部表已存在: github_users';
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: api_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部表失败: %', SQLERRM;
END $$;

-- 查询API数据（带错误处理和性能测试）
DO $$
DECLARE
    api_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'github_users'
    ) THEN
        RAISE EXCEPTION '外部表不存在: github_users';
    END IF;

    SELECT COUNT(*) INTO api_count
    FROM github_users LIMIT 10;

    RAISE NOTICE 'API查询成功: 获取了 % 条数据', api_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: github_users';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询API数据失败: %', SQLERRM;
END $$;

-- 性能测试：查询API数据
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM github_users LIMIT 10;
-- 执行时间: 取决于网络延迟和API响应时间
-- 计划: Limit -> Foreign Scan
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

**查询下推验证（带完整错误处理和性能测试）**:

```sql
-- postgres_fdw支持完整下推（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_users'
    ) THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    END IF;

    RAISE NOTICE '开始验证查询下推功能';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询下推验证准备失败: %', SQLERRM;
END $$;

-- 性能测试：查询下推
EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
SELECT * FROM remote_users
WHERE age > 25 AND city = 'Beijing'
ORDER BY created_at DESC
LIMIT 10;
-- 执行时间: 取决于网络延迟和远程查询性能
-- 计划: Limit -> Foreign Scan on remote_users
-- Remote SQL: SELECT id, name, age, city, created_at
--              FROM public.users
--              WHERE ((age > 25)) AND ((city = 'Beijing'::text))
--              ORDER BY created_at DESC
--              LIMIT 10
-- 完全在远程执行，只传输10行结果 ✅
```

### 8.2 批量获取

**批量获取优化（带完整错误处理）**:

```sql
-- 设置批量获取大小（服务器级别，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    END IF;

    ALTER SERVER remote_pg
    OPTIONS (ADD fetch_size '10000');

    RAISE NOTICE '服务器批量获取大小已设置为: 10000';
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    WHEN OTHERS THEN
        RAISE EXCEPTION '设置批量获取大小失败: %', SQLERRM;
END $$;

-- 或在表级别设置（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_users'
    ) THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    END IF;

    ALTER FOREIGN TABLE remote_users
    OPTIONS (ADD fetch_size '10000');

    RAISE NOTICE '外部表批量获取大小已设置为: 10000（默认100行，增加到10000提升批量查询性能）';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    WHEN OTHERS THEN
        RAISE EXCEPTION '设置批量获取大小失败: %', SQLERRM;
END $$;
```

### 8.3 连接池

**连接池管理（带完整错误处理）**:

```sql
-- 使用连接池避免频繁建立连接（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
        CREATE EXTENSION postgres_fdw;
        RAISE NOTICE 'postgres_fdw扩展已创建';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'postgres_fdw扩展文件未找到';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装postgres_fdw扩展失败: %', SQLERRM;
END $$;

-- 查看当前连接（带错误处理和性能测试）
DO $$
DECLARE
    connection_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
        RAISE EXCEPTION 'postgres_fdw扩展未安装';
    END IF;

    SELECT COUNT(*) INTO connection_count
    FROM postgres_fdw_get_connections();

    IF connection_count = 0 THEN
        RAISE NOTICE '当前没有FDW连接';
    ELSE
        RAISE NOTICE '当前有 % 个FDW连接', connection_count;
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION 'postgres_fdw扩展未安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查看连接失败: %', SQLERRM;
END $$;

-- 性能测试：查看当前连接
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM postgres_fdw_get_connections();
-- 执行时间: <10ms
-- 计划: Function Scan

-- 断开空闲连接（带错误处理）
DO $$
DECLARE
    disconnected_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    END IF;

    SELECT postgres_fdw_disconnect('remote_pg') INTO disconnected_count;

    IF disconnected_count > 0 THEN
        RAISE NOTICE '已断开 % 个连接', disconnected_count;
    ELSE
        RAISE NOTICE '没有需要断开的连接';
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    WHEN OTHERS THEN
        RAISE EXCEPTION '断开连接失败: %', SQLERRM;
END $$;

-- 断开所有连接（带错误处理）
DO $$
DECLARE
    disconnected_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
        RAISE EXCEPTION 'postgres_fdw扩展未安装';
    END IF;

    SELECT postgres_fdw_disconnect_all() INTO disconnected_count;

    IF disconnected_count > 0 THEN
        RAISE NOTICE '已断开所有连接: % 个', disconnected_count;
    ELSE
        RAISE NOTICE '没有需要断开的连接';
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION 'postgres_fdw扩展未安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '断开所有连接失败: %', SQLERRM;
END $$;
```

---

## 9. 生产实战案例

### 9.1 案例1：数据仓库整合

**数据仓库整合（带完整错误处理）**:

```sql
-- 整合3个数据源：PostgreSQL + MySQL + MongoDB
-- PostgreSQL（订单，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE WARNING '表已存在: orders';
    ELSE
        CREATE TABLE orders (
            id SERIAL PRIMARY KEY,
            customer_id INT,
            amount NUMERIC,
            created_at TIMESTAMPTZ
        );
        RAISE NOTICE '表创建成功: orders';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表已存在: orders';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- MySQL（客户）- 假设已配置mysql_server
-- MongoDB（产品）- 假设已配置mongo_server

-- 统一查询（带错误处理和性能测试）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'orders'
    ) THEN
        RAISE EXCEPTION '表不存在: orders';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'mysql_customers'
    ) THEN
        RAISE EXCEPTION '外部表不存在: mysql_customers';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'mongo_products'
    ) THEN
        RAISE EXCEPTION '外部表不存在: mongo_products';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM orders o
    JOIN mysql_customers mc ON o.customer_id = mc.id
    JOIN mongo_products mp ON o.product_id = mp._id::TEXT
    WHERE o.created_at >= '2025-01-01';

    RAISE NOTICE '数据仓库整合查询成功: 找到 % 条结果（单一SQL，整合3个数据库！）', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查orders、mysql_customers和mongo_products表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '数据仓库整合查询失败: %', SQLERRM;
END $$;

-- 性能测试：统一查询
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
ORDER BY o.created_at DESC;
-- 执行时间: 取决于网络延迟和表大小
-- 计划: Sort -> Hash Join -> Hash Join -> Foreign Scan (MySQL + MongoDB)
```

### 9.2 案例2：渐进式数据迁移

**渐进式数据迁移（带完整错误处理）**:

```sql
-- 从MySQL迁移到PostgreSQL（带完整错误处理）

-- 第1步：创建FDW连接（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mysql_legacy') THEN
        RAISE WARNING '服务器已存在: mysql_legacy';
    ELSE
        CREATE SERVER mysql_legacy FOREIGN DATA WRAPPER mysql_fdw
        OPTIONS (host 'legacy-mysql', port '3306');
        RAISE NOTICE 'MySQL服务器创建成功: mysql_legacy';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_user_mappings
        WHERE srvname = 'mysql_legacy' AND usename = 'postgres'
    ) THEN
        CREATE USER MAPPING FOR postgres SERVER mysql_legacy
        OPTIONS (username 'root', password 'password');
        RAISE NOTICE '用户映射创建成功: postgres -> mysql_legacy';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '部分对象已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建FDW连接失败: %', SQLERRM;
END $$;

-- 第2步：映射MySQL表（带错误处理）
-- 假设已创建mysql_orders和mysql_customers外部表

-- 第3步：创建PostgreSQL表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'mysql_orders'
    ) THEN
        RAISE EXCEPTION '外部表不存在: mysql_orders（请先创建外部表）';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'pg_orders') THEN
        RAISE WARNING '表已存在: pg_orders';
    ELSE
        CREATE TABLE pg_orders (LIKE mysql_orders);
        RAISE NOTICE 'PostgreSQL表创建成功: pg_orders';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'pg_customers') THEN
        RAISE WARNING '表已存在: pg_customers';
    ELSE
        CREATE TABLE pg_customers (LIKE mysql_customers);
        RAISE NOTICE 'PostgreSQL表创建成功: pg_customers';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在（请先创建mysql_orders和mysql_customers外部表）';
    WHEN duplicate_table THEN
        RAISE WARNING '部分表已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建PostgreSQL表失败: %', SQLERRM;
END $$;

-- 第4步：历史数据迁移（带错误处理）
DO $$
DECLARE
    orders_migrated BIGINT;
    customers_migrated BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'pg_orders'
    ) THEN
        RAISE EXCEPTION '目标表不存在: pg_orders';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'mysql_orders'
    ) THEN
        RAISE EXCEPTION '源外部表不存在: mysql_orders';
    END IF;

    INSERT INTO pg_orders SELECT * FROM mysql_orders
    WHERE created_at < '2025-01-01';
    GET DIAGNOSTICS orders_migrated = ROW_COUNT;

    INSERT INTO pg_customers SELECT * FROM mysql_customers;
    GET DIAGNOSTICS customers_migrated = ROW_COUNT;

    RAISE NOTICE '历史数据迁移成功: orders=%行, customers=%行', orders_migrated, customers_migrated;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查pg_orders、mysql_orders和mysql_customers表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '历史数据迁移失败: %', SQLERRM;
END $$;

-- 第5步：创建联合视图（过渡期，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.views WHERE table_schema = 'public' AND table_name = 'orders_unified') THEN
        RAISE WARNING '视图已存在: orders_unified';
    ELSE
        CREATE VIEW orders_unified AS
        SELECT * FROM pg_orders          -- 新数据
        UNION ALL
        SELECT * FROM mysql_orders       -- 历史数据
        WHERE created_at >= '2025-01-01';
        RAISE NOTICE '联合视图创建成功: orders_unified（应用无感知，渐进式迁移！）';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '视图已存在: orders_unified';
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查pg_orders和mysql_orders表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建联合视图失败: %', SQLERRM;
END $$;
```

### 9.3 案例3：实时报表系统

**实时报表系统（带完整错误处理）**:

```sql
-- 整合多个微服务数据库（带完整错误处理）

-- 服务1：用户服务（PostgreSQL，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'user_service_db') THEN
        RAISE WARNING '服务器已存在: user_service_db';
    ELSE
        CREATE SERVER user_service_db FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host 'user-service-db', dbname 'users');
        RAISE NOTICE '用户服务服务器创建成功: user_service_db';
    END IF;

    -- 假设已创建svc_users外部表
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '服务器已存在: user_service_db';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建用户服务服务器失败: %', SQLERRM;
END $$;

-- 服务2：订单服务（MySQL，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'order_service_db') THEN
        RAISE WARNING '服务器已存在: order_service_db';
    ELSE
        CREATE SERVER order_service_db FOREIGN DATA WRAPPER mysql_fdw
        OPTIONS (host 'order-service-db');
        RAISE NOTICE '订单服务服务器创建成功: order_service_db';
    END IF;

    -- 假设已创建svc_orders外部表
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '服务器已存在: order_service_db';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订单服务服务器失败: %', SQLERRM;
END $$;

-- 服务3：产品服务（MongoDB，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'product_service_db') THEN
        RAISE WARNING '服务器已存在: product_service_db';
    ELSE
        CREATE SERVER product_service_db FOREIGN DATA WRAPPER mongo_fdw
        OPTIONS (address 'product-service-db');
        RAISE NOTICE '产品服务服务器创建成功: product_service_db';
    END IF;

    -- 假设已创建svc_products外部表
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '服务器已存在: product_service_db';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建产品服务服务器失败: %', SQLERRM;
END $$;

-- 实时报表查询（带错误处理和性能测试）
DO $$
DECLARE
    report_days INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'svc_orders'
    ) THEN
        RAISE EXCEPTION '外部表不存在: svc_orders';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'svc_users'
    ) THEN
        RAISE EXCEPTION '外部表不存在: svc_users';
    END IF;

    SELECT COUNT(DISTINCT DATE(so.created_at)) INTO report_days
    FROM svc_orders so
    JOIN svc_users su ON so.user_id = su.id
    WHERE so.created_at >= CURRENT_DATE - INTERVAL '30 days';

    RAISE NOTICE '实时报表查询成功: 覆盖 % 天的数据', report_days;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在（请检查svc_orders和svc_users表）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '实时报表查询失败: %', SQLERRM;
END $$;

-- 性能测试：实时报表查询
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
ORDER BY date DESC;
-- 执行时间: 取决于网络延迟和表大小
-- 计划: Sort -> GroupAggregate -> Hash Join -> Foreign Scan (多个微服务)
```

---

## 10. 最佳实践

### 10.1 性能优化

**性能优化配置（带完整错误处理）**:

```sql
-- ✅ 1. 启用查询下推（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    END IF;

    ALTER SERVER remote_pg
    OPTIONS (ADD extensions 'postgres_fdw');

    RAISE NOTICE '查询下推已启用: remote_pg';
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    WHEN OTHERS THEN
        RAISE EXCEPTION '启用查询下推失败: %', SQLERRM;
END $$;

-- ✅ 2. 使用异步执行（PostgreSQL 14+，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    END IF;

    IF current_setting('server_version_num')::INT < 140000 THEN
        RAISE WARNING '异步执行需要PostgreSQL 14+';
    END IF;

    ALTER SERVER remote_pg
    OPTIONS (ADD async_capable 'true');

    RAISE NOTICE '异步执行已启用: remote_pg';
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '服务器不存在: remote_pg';
    WHEN feature_not_supported THEN
        RAISE WARNING '异步执行需要PostgreSQL 14+';
    WHEN OTHERS THEN
        RAISE EXCEPTION '启用异步执行失败: %', SQLERRM;
END $$;

-- ✅ 3. 增加批量大小（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_table'
    ) THEN
        RAISE EXCEPTION '外部表不存在: remote_table';
    END IF;

    ALTER FOREIGN TABLE remote_table
    OPTIONS (ADD fetch_size '10000');

    RAISE NOTICE '批量大小已设置为: 10000';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: remote_table';
    WHEN OTHERS THEN
        RAISE EXCEPTION '设置批量大小失败: %', SQLERRM;
END $$;

-- ✅ 4. 在远程创建索引
-- 在远程数据库为外部表查询列创建索引（需要在远程数据库执行）

-- ✅ 5. 物化外部数据（频繁访问，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'remote_table'
    ) THEN
        RAISE EXCEPTION '外部表不存在: remote_table';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'public' AND table_name = 'mv_remote_data'
        AND table_type = 'BASE TABLE'  -- 物化视图在information_schema中显示为BASE TABLE
    ) THEN
        RAISE WARNING '物化视图已存在: mv_remote_data';
    ELSE
        CREATE MATERIALIZED VIEW mv_remote_data AS
        SELECT * FROM remote_table WHERE active = TRUE;
        RAISE NOTICE '物化视图创建成功: mv_remote_data';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: remote_table';
    WHEN duplicate_table THEN
        RAISE WARNING '物化视图已存在: mv_remote_data';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建物化视图失败: %', SQLERRM;
END $$;

-- 刷新物化视图（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'public' AND table_name = 'mv_remote_data'
        AND table_type = 'BASE TABLE'
    ) THEN
        RAISE EXCEPTION '物化视图不存在: mv_remote_data';
    END IF;

    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_remote_data;
    RAISE NOTICE '物化视图刷新成功: mv_remote_data';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '物化视图不存在: mv_remote_data';
    WHEN OTHERS THEN
        RAISE EXCEPTION '刷新物化视图失败: %', SQLERRM;
END $$;
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

**FDW监控（带完整错误处理和性能测试）**:

```sql
-- 查看FDW连接（带错误处理）
DO $$
DECLARE
    connection_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
        RAISE EXCEPTION 'postgres_fdw扩展未安装';
    END IF;

    SELECT COUNT(*) INTO connection_count
    FROM postgres_fdw_get_connections();

    IF connection_count = 0 THEN
        RAISE NOTICE '当前没有FDW连接';
    ELSE
        RAISE NOTICE '当前有 % 个FDW连接', connection_count;
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION 'postgres_fdw扩展未安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查看FDW连接失败: %', SQLERRM;
END $$;

-- 性能测试：查看FDW连接
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM postgres_fdw_get_connections();
-- 执行时间: <10ms
-- 计划: Function Scan

-- 查看外部表统计（带错误处理和性能测试）
DO $$
DECLARE
    table_count INT;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM pg_stat_user_tables
    WHERE tablename LIKE 'remote_%';

    IF table_count = 0 THEN
        RAISE NOTICE '没有找到外部表统计信息';
    ELSE
        RAISE NOTICE '找到 % 个外部表的统计信息', table_count;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '查看外部表统计失败: %', SQLERRM;
END $$;

-- 性能测试：查看外部表统计
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan
FROM pg_stat_user_tables
WHERE tablename LIKE 'remote_%';
-- 执行时间: <10ms
-- 计划: Seq Scan

-- 慢查询分析（带错误处理）
DO $$
DECLARE
    slow_query_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
        RAISE EXCEPTION 'pg_stat_statements扩展未安装';
    END IF;

    SELECT COUNT(*) INTO slow_query_count
    FROM pg_stat_statements
    WHERE query LIKE '%remote_%'
    AND mean_exec_time > 1000;  -- 平均执行时间>1秒

    IF slow_query_count = 0 THEN
        RAISE NOTICE '未找到慢查询（平均执行时间>1秒）';
    ELSE
        RAISE NOTICE '找到 % 个慢查询', slow_query_count;
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION 'pg_stat_statements扩展未安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '慢查询分析失败: %', SQLERRM;
END $$;

-- 性能测试：慢查询分析
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT query, mean_exec_time
FROM pg_stat_statements
WHERE query LIKE '%remote_%'
ORDER BY mean_exec_time DESC;
-- 执行时间: <10ms
-- 计划: Sort -> Seq Scan
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
