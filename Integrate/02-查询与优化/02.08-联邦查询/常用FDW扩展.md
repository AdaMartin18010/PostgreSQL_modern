# PostgreSQL常用FDW扩展指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐ 中级

---

## 📋 目录

- [PostgreSQL常用FDW扩展指南](#postgresql常用fdw扩展指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. postgres\_fdw](#2-postgres_fdw)
    - [2.1 安装配置](#21-安装配置)
    - [2.2 使用示例](#22-使用示例)
  - [3. mysql\_fdw](#3-mysql_fdw)
    - [3.1 安装配置](#31-安装配置)
    - [3.2 使用示例](#32-使用示例)
  - [4. file\_fdw](#4-file_fdw)
    - [4.1 安装配置](#41-安装配置)
    - [4.2 使用示例](#42-使用示例)
  - [5. 其他FDW扩展](#5-其他fdw扩展)
    - [5.1 oracle\_fdw](#51-oracle_fdw)
    - [5.2 multicorn](#52-multicorn)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

PostgreSQL提供了丰富的FDW扩展，支持访问各种数据源。

**常用FDW**:

- postgres_fdw - PostgreSQL数据源
- mysql_fdw - MySQL数据源
- file_fdw - 文件数据源
- oracle_fdw - Oracle数据源

---

## 2. postgres_fdw

### 2.1 安装配置

**postgres_fdw完整配置（带错误处理）**:

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
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
        RAISE EXCEPTION '外部服务器不存在: remote_pg';
    END IF;

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

### 2.2 使用示例

**创建和使用外部表（带完整错误处理和性能测试）**:

```sql
-- 创建外部表（带错误处理）
DO $$
BEGIN
    -- 检查服务器是否存在
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_pg') THEN
        RAISE EXCEPTION '外部服务器不存在: remote_pg';
    END IF;

    -- 检查外部表是否已存在
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'remote_users') THEN
        RAISE WARNING '外部表已存在: remote_users';
    ELSE
        CREATE FOREIGN TABLE remote_users (
            id INT,
            name TEXT,
            email TEXT
        )
        SERVER remote_pg
        OPTIONS (schema_name 'public', table_name 'users');
        RAISE NOTICE '外部表创建成功: remote_users';
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '外部服务器不存在: remote_pg';
    WHEN duplicate_table THEN
        RAISE WARNING '外部表已存在: remote_users';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部表失败: %', SQLERRM;
END $$;

-- 查询外部表（带错误处理和性能测试）
DO $$
DECLARE
    row_count BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'remote_users') THEN
        RAISE EXCEPTION '外部表不存在: remote_users';
    END IF;

    SELECT COUNT(*) INTO row_count FROM remote_users WHERE id > 100;

    IF row_count IS NULL THEN
        RAISE WARNING '查询返回NULL（可能表为空或连接失败）';
    ELSE
        RAISE NOTICE '查询成功: 找到 % 行数据', row_count;
    END IF;
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
-- 计划: Foreign Scan（可能带Remote Filter）
```

---

## 3. mysql_fdw

### 3.1 安装配置

**mysql_fdw完整配置（带错误处理）**:

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

-- 创建用户映射（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_mysql') THEN
        RAISE EXCEPTION '外部服务器不存在: remote_mysql';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_user_mappings
        WHERE srvname = 'remote_mysql' AND usename = current_user::text
    ) THEN
        RAISE WARNING '用户映射已存在: remote_mysql -> %', current_user;
    ELSE
        CREATE USER MAPPING FOR current_user
        SERVER remote_mysql
        OPTIONS (username 'mysql_user', password 'password');
        RAISE NOTICE '用户映射创建成功: % -> remote_mysql', current_user;
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '外部服务器不存在: remote_mysql';
    WHEN duplicate_object THEN
        RAISE WARNING '用户映射已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建用户映射失败: %', SQLERRM;
END $$;
```

### 3.2 使用示例

**创建和使用MySQL外部表（带完整错误处理和性能测试）**:

```sql
-- 创建外部表（带错误处理）
DO $$
BEGIN
    -- 检查服务器是否存在
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'remote_mysql') THEN
        RAISE EXCEPTION '外部服务器不存在: remote_mysql';
    END IF;

    -- 检查外部表是否已存在
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'mysql_users') THEN
        RAISE WARNING '外部表已存在: mysql_users';
    ELSE
        CREATE FOREIGN TABLE mysql_users (
            id INT,
            name TEXT,
            email TEXT
        )
        SERVER remote_mysql
        OPTIONS (table_name 'users');
        RAISE NOTICE '外部表创建成功: mysql_users';
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '外部服务器不存在: remote_mysql';
    WHEN duplicate_table THEN
        RAISE WARNING '外部表已存在: mysql_users';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建外部表失败: %', SQLERRM;
END $$;

-- 查询外部表（带错误处理和性能测试）
DO $$
DECLARE
    row_count BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'mysql_users') THEN
        RAISE EXCEPTION '外部表不存在: mysql_users';
    END IF;

    SELECT COUNT(*) INTO row_count FROM mysql_users;

    IF row_count IS NULL THEN
        RAISE WARNING '查询返回NULL（可能表为空或连接失败）';
    ELSE
        RAISE NOTICE '查询成功: 找到 % 行数据', row_count;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: mysql_users';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询外部表失败: %', SQLERRM;
END $$;

-- 性能测试：查询MySQL外部表
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM mysql_users;
-- 执行时间: 取决于网络延迟和MySQL表大小
-- 计划: Foreign Scan
```

---

## 4. file_fdw

### 4.1 安装配置

**file_fdw完整配置（带错误处理）**:

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
```

### 4.2 使用示例

**创建和使用文件外部表（带完整错误处理和性能测试）**:

```sql
-- 创建外部表（CSV文件，带错误处理）
DO $$
BEGIN
    -- 检查服务器是否存在
    IF NOT EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'file_server') THEN
        RAISE EXCEPTION '外部服务器不存在: file_server';
    END IF;

    -- 检查外部表是否已存在
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

-- 查询文件数据（带错误处理和性能测试）
DO $$
DECLARE
    row_count BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'csv_data') THEN
        RAISE EXCEPTION '外部表不存在: csv_data';
    END IF;

    SELECT COUNT(*) INTO row_count FROM csv_data;

    IF row_count IS NULL THEN
        RAISE WARNING '查询返回NULL（可能文件为空或格式错误）';
    ELSE
        RAISE NOTICE '查询成功: 找到 % 行数据', row_count;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '外部表不存在: csv_data';
    WHEN undefined_file THEN
        RAISE EXCEPTION '文件不存在或无法访问: /path/to/data.csv';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询文件数据失败: %', SQLERRM;
END $$;

-- 性能测试：查询CSV文件
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM csv_data WHERE id > 100;
-- 执行时间: 取决于文件大小和I/O性能
-- 计划: Foreign Scan
```

---

## 5. 其他FDW扩展

### 5.1 oracle_fdw

**Oracle数据源配置（带错误处理）**:

```sql
-- Oracle数据源（带错误处理）
DO $$
BEGIN
    -- 检查oracle_fdw扩展是否安装
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'oracle_fdw') THEN
        CREATE EXTENSION oracle_fdw;
        RAISE NOTICE 'oracle_fdw扩展已创建';
    ELSE
        RAISE NOTICE 'oracle_fdw扩展已存在';
    END IF;

    -- 检查服务器是否已存在
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'oracle_server') THEN
        RAISE WARNING '外部服务器已存在: oracle_server';
    ELSE
        CREATE SERVER oracle_server
        FOREIGN DATA WRAPPER oracle_fdw
        OPTIONS (dbserver '//oracle_host:1521/orcl');
        RAISE NOTICE '外部服务器创建成功: oracle_server';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'oracle_fdw扩展文件未找到（需要单独安装oracle_fdw扩展）';
    WHEN duplicate_object THEN
        RAISE WARNING '外部服务器已存在: oracle_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建Oracle外部服务器失败: %', SQLERRM;
END $$;
```

### 5.2 multicorn

**Python FDW框架配置（带错误处理）**:

```sql
-- Python FDW框架（带错误处理）
DO $$
BEGIN
    -- 检查multicorn扩展是否安装
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'multicorn') THEN
        CREATE EXTENSION multicorn;
        RAISE NOTICE 'multicorn扩展已创建';
    ELSE
        RAISE NOTICE 'multicorn扩展已存在';
    END IF;

    -- 检查服务器是否已存在
    IF EXISTS (SELECT 1 FROM pg_foreign_server WHERE srvname = 'python_server') THEN
        RAISE WARNING '外部服务器已存在: python_server';
    ELSE
        CREATE SERVER python_server
        FOREIGN DATA WRAPPER multicorn
        OPTIONS (wrapper 'multicorn.pythonfdw.PythonFdw');
        RAISE NOTICE '外部服务器创建成功: python_server';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'multicorn扩展文件未找到（需要单独安装multicorn扩展）';
    WHEN duplicate_object THEN
        RAISE WARNING '外部服务器已存在: python_server';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建Python FDW服务器失败: %', SQLERRM;
END $$;
```

---

## 📚 相关文档

- [FDW完整指南.md](./FDW完整指南.md) - FDW完整指南
- [多数据源查询.md](./多数据源查询.md) - 多数据源查询详解
- [02-查询与优化/README.md](../README.md) - 查询与优化主题

---

**最后更新**: 2025年1月
