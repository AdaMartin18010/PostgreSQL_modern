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

```sql
-- 创建外部服务器
CREATE SERVER foreign_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'remote_host', port '5432', dbname 'remote_db');

-- 创建用户映射
CREATE USER MAPPING FOR current_user
SERVER foreign_server
OPTIONS (user 'remote_user', password 'remote_password');

-- 创建外部表
CREATE FOREIGN TABLE foreign_table (
    id INT,
    name TEXT
)
SERVER foreign_server
OPTIONS (schema_name 'public', table_name 'remote_table');
```

### 2.2 FDW查询

```sql
-- 查询外部表
SELECT * FROM foreign_table WHERE id > 100;

-- 跨数据源JOIN
SELECT
    l.id,
    l.name,
    r.description
FROM local_table l
JOIN foreign_table r ON l.id = r.id;
```

---

## 3. 常用FDW扩展

### 3.1 postgres_fdw

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- 创建服务器
CREATE SERVER remote_pg
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host '192.168.1.100', port '5432', dbname 'mydb');
```

### 3.2 mysql_fdw

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS mysql_fdw;

-- 创建服务器
CREATE SERVER remote_mysql
FOREIGN DATA WRAPPER mysql_fdw
OPTIONS (host '192.168.1.101', port '3306', database 'mydb');
```

### 3.3 file_fdw

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS file_fdw;

-- 创建外部表（CSV文件）
CREATE FOREIGN TABLE csv_data (
    id INT,
    name TEXT,
    value NUMERIC
)
SERVER file_server
OPTIONS (filename '/path/to/data.csv', format 'csv', header 'true');
```

---

## 4. 多数据源查询

### 4.1 多数据源集成

```sql
-- 创建多个外部服务器
CREATE SERVER pg_server FOREIGN DATA WRAPPER postgres_fdw ...;
CREATE SERVER mysql_server FOREIGN DATA WRAPPER mysql_fdw ...;

-- 跨数据源查询
SELECT
    pg_data.id,
    pg_data.name,
    mysql_data.description
FROM pg_foreign_table pg_data
JOIN mysql_foreign_table mysql_data ON pg_data.id = mysql_data.id;
```

### 4.2 数据源统一

```sql
-- 使用视图统一接口
CREATE VIEW unified_data AS
SELECT 'postgres' AS source, * FROM pg_foreign_table
UNION ALL
SELECT 'mysql' AS source, * FROM mysql_foreign_table;
```

---

## 5. 性能优化

### 5.1 查询下推

```sql
-- 启用查询下推
ALTER FOREIGN TABLE foreign_table
OPTIONS (ADD use_remote_estimate 'true');

-- 使用WHERE子句下推
SELECT * FROM foreign_table WHERE id > 1000;
-- 查询会在远程执行
```

### 5.2 批量操作

```sql
-- 批量导入
INSERT INTO local_table
SELECT * FROM foreign_table
WHERE created_at > CURRENT_DATE - INTERVAL '7 days';
```

---

## 📚 相关文档

- [FDW外部数据包装器完整实战指南.md](./FDW外部数据包装器完整实战指南.md) - FDW完整实战指南
- [多数据源查询.md](./多数据源查询.md) - 多数据源查询详解
- [02-查询与优化/README.md](../README.md) - 查询与优化主题

---

**最后更新**: 2025年1月
