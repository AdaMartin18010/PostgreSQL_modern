# PostgreSQL FDW完整指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级

---

## 📋 目录

- [PostgreSQL FDW完整指南](#postgresql-fdw完整指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. FDW基础](#2-fdw基础)
    - [2.1 FDW概念](#21-fdw概念)
    - [2.2 FDW查询](#22-fdw查询)
  - [3. 常用FDW扩展](#3-常用fdw扩展)
    - [3.1 postgres\_fdw](#31-postgres_fdw)
    - [3.2 mysql\_fdw](#32-mysql_fdw)
    - [3.3 file\_fdw](#33-file_fdw)
  - [4. 多数据源查询](#4-多数据源查询)
    - [4.1 多数据源集成](#41-多数据源集成)
    - [4.2 数据源统一](#42-数据源统一)
  - [5. 性能优化](#5-性能优化)
    - [5.1 查询下推](#51-查询下推)
    - [5.2 批量操作](#52-批量操作)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

FDW（Foreign Data Wrapper）是PostgreSQL实现联邦查询的核心机制。

**FDW优势**:

- 跨数据库查询
- 数据源集成
- 统一查询接口
- 灵活的数据访问

---

## 2. FDW基础

### 2.1 FDW概念

**创建外部服务器（带错误处理）**:

```sql
-- 创建外部服务器（带完整错误处理）
DO $$
BEGIN
    -- 检查postgres_fdw扩展是否安装
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgres_fdw') THEN
        CREATE EXTENSION postgres_fdw;
        RAISE NOTICE 'postgres_fdw扩展已创建';
    END IF;

    -- 检查服务器是否已存在
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'foreign_server') THEN
        RAISE WARNING '外部服务器已存在: foreign_server';
    ELSE
        CREATE SERVER foreign_server
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host 'remote_host', port '5432', dbname 'remote_db');
        RAISE NOTICE '外部服务器创建成功: foreign_server';
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION 'postgres_fdw扩展未安装，请先安装扩展';
    WHEN duplicate_object THEN
        RAISE WARNING '外部服务器已存在: foreign_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部服务器失败: %', SQLERRM;
END $$;

-- 创建用户映射（带错误处理）
DO $$
BEGIN
    -- 检查服务器是否存在
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'foreign_server') THEN
        RAISE EXCEPTION '外部服务器不存在: foreign_server';
    END IF;

    -- 检查用户映射是否已存在
    IF EXISTS (
        SELECT 1 FROM pg_user_mappings
        WHERE srvname = 'foreign_server' AND usename = current_user::text
    ) THEN
        RAISE WARNING '用户映射已存在: foreign_server -> %', current_user;
    ELSE
        CREATE USER MAPPING FOR current_user
        SERVER foreign_server
        OPTIONS (user 'remote_user', password 'remote_password');
        RAISE NOTICE '用户映射创建成功: % -> foreign_server', current_user;
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '外部服务器不存在: foreign_server';
    WHEN duplicate_object THEN
        RAISE WARNING '用户映射已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建用户映射失败: %', SQLERRM;
END $$;

-- 创建外部表（带错误处理）
DO $$
BEGIN
    -- 检查服务器是否存在
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'foreign_server') THEN
        RAISE EXCEPTION '外部服务器不存在: foreign_server';
    END IF;

    -- 检查外部表是否已存在
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'foreign_table') THEN
        RAISE WARNING '外部表已存在: foreign_table';
    ELSE
        CREATE FOREIGN TABLE foreign_table (
            id INT,
            name TEXT
        )
        SERVER foreign_server
        OPTIONS (schema_name 'public', table_name 'remote_table');
        RAISE NOTICE '外部表创建成功: foreign_table';
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '外部服务器不存在: foreign_server';
    WHEN duplicate_table THEN
        RAISE WARNING '外部表已存在: foreign_table';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部表失败: %', SQLERRM;
END $$;
```

### 2.2 FDW查询

**查询外部表（带错误处理和性能测试）**:

```sql
-- 查询外部表（带错误处理）
DO $$
DECLARE
    row_count BIGINT;
BEGIN
    -- 检查外部表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'foreign_table') THEN
        RAISE EXCEPTION '外部表不存在: foreign_table';
    END IF;

    -- 执行查询
    SELECT COUNT(*) INTO row_count FROM foreign_table WHERE id > 100;

    IF row_count IS NULL THEN
        RAISE WARNING '查询返回NULL（可能表为空或连接失败）';
    ELSE
        RAISE NOTICE '查询成功: 找到 % 行数据', row_count;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: foreign_table';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询外部表失败: %', SQLERRM;
END $$;

-- 性能测试：查询外部表
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM foreign_table WHERE id > 100;
-- 执行时间: 取决于网络延迟和远程表大小
-- 计划: Foreign Scan

-- 跨数据源JOIN（带错误处理和性能测试）
DO $$
DECLARE
    join_count BIGINT;
BEGIN
    -- 检查本地表和外部表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'local_table') THEN
        RAISE EXCEPTION '本地表不存在: local_table';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'foreign_table') THEN
        RAISE EXCEPTION '外部表不存在: foreign_table';
    END IF;

    -- 执行JOIN查询
    SELECT COUNT(*) INTO join_count
    FROM local_table l
    JOIN foreign_table r ON l.id = r.id;

    IF join_count IS NULL THEN
        RAISE WARNING 'JOIN查询返回NULL';
    ELSE
        RAISE NOTICE '跨数据源JOIN成功: 找到 % 行匹配数据', join_count;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查local_table和foreign_table）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '跨数据源JOIN失败: %', SQLERRM;
END $$;

-- 性能测试：跨数据源JOIN
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    l.id,
    l.name,
    r.description
FROM local_table l
JOIN foreign_table r ON l.id = r.id;
-- 执行时间: 取决于网络延迟和表大小
-- 计划: Nested Loop (可能) 或 Hash Join
```

---

## 3. 常用FDW扩展

### 3.1 postgres_fdw

**安装和配置（带完整错误处理）**:

```sql
-- 安装扩展（带错误处理）
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
        RAISE EXCEPTION 'postgres_fdw扩展文件未找到（请检查PostgreSQL安装）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装postgres_fdw扩展失败: %', SQLERRM;
END $$;

-- 创建服务器（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
        RAISE WARNING '外部服务器已存在: remote_pg';
    ELSE
        CREATE SERVER remote_pg
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host '192.168.1.100', port '5432', dbname 'mydb');
        RAISE NOTICE '外部服务器创建成功: remote_pg';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '外部服务器已存在: remote_pg';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部服务器失败: %', SQLERRM;
END $$;

-- 创建用户映射（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_user_mappings
        WHERE srvname = 'remote_pg' AND usename = current_user::text
    ) THEN
        RAISE WARNING '用户映射已存在: remote_pg -> %', current_user;
    ELSE
        CREATE USER MAPPING FOR current_user
        SERVER remote_pg
        OPTIONS (user 'postgres', password 'password');
        RAISE NOTICE '用户映射创建成功: % -> remote_pg', current_user;
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '外部服务器不存在: remote_pg';
    WHEN duplicate_object THEN
        RAISE WARNING '用户映射已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建用户映射失败: %', SQLERRM;
END $$;
```

### 3.2 mysql_fdw

**安装和配置（带完整错误处理）**:

```sql
-- 安装扩展（带错误处理）
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

-- 创建服务器（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_mysql') THEN
        RAISE WARNING '外部服务器已存在: remote_mysql';
    ELSE
        CREATE SERVER remote_mysql
        FOREIGN DATA WRAPPER mysql_fdw
        OPTIONS (host '192.168.1.101', port '3306', database 'mydb');
        RAISE NOTICE '外部服务器创建成功: remote_mysql';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '外部服务器已存在: remote_mysql';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部服务器失败: %', SQLERRM;
END $$;
```

### 3.3 file_fdw

**安装和配置（带完整错误处理）**:

```sql
-- 安装扩展（带错误处理）
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
        RAISE EXCEPTION 'file_fdw扩展文件未找到（请检查PostgreSQL安装）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装file_fdw扩展失败: %', SQLERRM;
END $$;

-- 创建服务器（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'file_server') THEN
        RAISE WARNING '外部服务器已存在: file_server';
    ELSE
        CREATE SERVER file_server
        FOREIGN DATA WRAPPER file_fdw;
        RAISE NOTICE '外部服务器创建成功: file_server';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '外部服务器已存在: file_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部服务器失败: %', SQLERRM;
END $$;

-- 创建外部表（CSV文件，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'csv_data') THEN
        RAISE WARNING '外部表已存在: csv_data';
    ELSE
        CREATE FOREIGN TABLE csv_data (
            id INT,
            name TEXT,
            value NUMERIC
        )
        SERVER file_server
        OPTIONS (filename '/path/to/data.csv', format 'csv', header 'true');
        RAISE NOTICE '外部表创建成功: csv_data';
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '外部服务器不存在: file_server';
    WHEN undefined_file THEN
        RAISE EXCEPTION '文件不存在或无法访问: /path/to/data.csv';
    WHEN duplicate_table THEN
        RAISE WARNING '外部表已存在: csv_data';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部表失败: %', SQLERRM;
END $$;

-- 性能测试：查询CSV文件
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM csv_data WHERE id > 100;
-- 执行时间: 取决于文件大小和I/O性能
-- 计划: Foreign Scan
```

---

## 4. 多数据源查询

### 4.1 多数据源集成

**多数据源配置（带完整错误处理）**:

```sql
-- 创建多个外部服务器（带错误处理）
DO $$
BEGIN
    -- 创建PostgreSQL服务器
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'pg_server') THEN
        CREATE SERVER pg_server
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host '192.168.1.100', port '5432', dbname 'pg_db');
        RAISE NOTICE 'PostgreSQL服务器创建成功: pg_server';
    END IF;

    -- 创建MySQL服务器
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'mysql_server') THEN
        CREATE SERVER mysql_server
        FOREIGN DATA WRAPPER mysql_fdw
        OPTIONS (host '192.168.1.101', port '3306', database 'mysql_db');
        RAISE NOTICE 'MySQL服务器创建成功: mysql_server';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '部分服务器已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部服务器失败: %', SQLERRM;
END $$;

-- 跨数据源查询（带错误处理和性能测试）
DO $$
DECLARE
    join_count BIGINT;
BEGIN
    -- 检查外部表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'pg_foreign_table') THEN
        RAISE EXCEPTION 'PostgreSQL外部表不存在: pg_foreign_table';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'mysql_foreign_table') THEN
        RAISE EXCEPTION 'MySQL外部表不存在: mysql_foreign_table';
    END IF;

    -- 执行跨数据源JOIN
    SELECT COUNT(*) INTO join_count
    FROM pg_foreign_table pg_data
    JOIN mysql_foreign_table mysql_data ON pg_data.id = mysql_data.id;

    RAISE NOTICE '跨数据源JOIN成功: 找到 % 行匹配数据', join_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在（请检查pg_foreign_table和mysql_foreign_table）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '跨数据源查询失败: %', SQLERRM;
END $$;

-- 性能测试：跨数据源JOIN
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pg_data.id,
    pg_data.name,
    mysql_data.description
FROM pg_foreign_table pg_data
JOIN mysql_foreign_table mysql_data ON pg_data.id = mysql_data.id;
-- 执行时间: 取决于网络延迟和表大小
-- 计划: Nested Loop 或 Hash Join
```

### 4.2 数据源统一

**统一视图（带完整错误处理）**:

```sql
-- 使用视图统一接口（带错误处理）
DO $$
BEGIN
    -- 检查外部表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'pg_foreign_table') THEN
        RAISE EXCEPTION 'PostgreSQL外部表不存在: pg_foreign_table';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'mysql_foreign_table') THEN
        RAISE EXCEPTION 'MySQL外部表不存在: mysql_foreign_table';
    END IF;

    -- 删除现有视图（如果存在）
    IF EXISTS (SELECT 1 FROM information_schema.views WHERE table_schema = 'public' AND table_name = 'unified_data') THEN
        DROP VIEW unified_data;
        RAISE NOTICE '已删除现有视图: unified_data';
    END IF;

    -- 创建统一视图
    CREATE VIEW unified_data AS
    SELECT 'postgres' AS source, * FROM pg_foreign_table
    UNION ALL
    SELECT 'mysql' AS source, * FROM mysql_foreign_table;

    RAISE NOTICE '统一视图创建成功: unified_data';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在（请检查pg_foreign_table和mysql_foreign_table）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建统一视图失败: %', SQLERRM;
END $$;

-- 性能测试：查询统一视图
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM unified_data WHERE source = 'postgres';
-- 执行时间: 取决于网络延迟和表大小
-- 计划: Append -> Foreign Scan
```

---

## 5. 性能优化

### 5.1 查询下推

**启用查询下推（带完整错误处理）**:

```sql
-- 启用查询下推（带错误处理）
DO $$
BEGIN
    -- 检查外部表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'foreign_table') THEN
        RAISE EXCEPTION '外部表不存在: foreign_table';
    END IF;

    -- 启用远程估算
    ALTER FOREIGN TABLE foreign_table
    OPTIONS (ADD use_remote_estimate 'true');

    RAISE NOTICE '查询下推已启用: foreign_table (use_remote_estimate=true)';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: foreign_table';
    WHEN OTHERS THEN
        RAISE EXCEPTION '启用查询下推失败: %', SQLERRM;
END $$;

-- 使用WHERE子句下推（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM foreign_table WHERE id > 1000;
-- 执行时间: 查询在远程执行，只返回结果
-- 计划: Foreign Scan (带Remote Filter)
-- 注意: 如果查询下推成功，会在远程执行WHERE条件
```

### 5.2 批量操作

**批量导入（带完整错误处理和性能测试）**:

```sql
-- 批量导入（带错误处理）
DO $$
DECLARE
    inserted_count BIGINT;
BEGIN
    -- 检查本地表和外部表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'local_table') THEN
        RAISE EXCEPTION '本地表不存在: local_table';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'foreign_table') THEN
        RAISE EXCEPTION '外部表不存在: foreign_table';
    END IF;

    -- 执行批量导入
    INSERT INTO local_table
    SELECT * FROM foreign_table
    WHERE created_at > CURRENT_DATE - INTERVAL '7 days';

    GET DIAGNOSTICS inserted_count = ROW_COUNT;
    RAISE NOTICE '批量导入成功: 插入了 % 行数据', inserted_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在（请检查local_table和foreign_table）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '批量导入失败: %', SQLERRM;
END $$;

-- 性能测试：批量导入
EXPLAIN (ANALYZE, BUFFERS, TIMING)
INSERT INTO local_table
SELECT * FROM foreign_table
WHERE created_at > CURRENT_DATE - INTERVAL '7 days';
-- 执行时间: 取决于网络延迟和数据量
-- 计划: Insert on local_table -> Foreign Scan
```

---

## 📚 相关文档

- [FDW外部数据包装器完整实战指南.md](./FDW外部数据包装器完整实战指南.md) - FDW完整实战指南
- [多数据源查询.md](./多数据源查询.md) - 多数据源查询详解
- [02-查询与优化/README.md](../README.md) - 查询与优化主题

---

**最后更新**: 2025年1月
