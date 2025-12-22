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

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- 创建服务器
CREATE SERVER remote_pg
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host '192.168.1.100', port '5432', dbname 'mydb');

-- 创建用户映射
CREATE USER MAPPING FOR current_user
SERVER remote_pg
OPTIONS (user 'postgres', password 'password');
```

### 2.2 使用示例

```sql
-- 创建外部表
CREATE FOREIGN TABLE remote_users (
    id INT,
    name TEXT,
    email TEXT
)
SERVER remote_pg
OPTIONS (schema_name 'public', table_name 'users');

-- 查询外部表
SELECT * FROM remote_users WHERE id > 100;
```

---

## 3. mysql_fdw

### 3.1 安装配置

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS mysql_fdw;

-- 创建服务器
CREATE SERVER remote_mysql
FOREIGN DATA WRAPPER mysql_fdw
OPTIONS (host '192.168.1.101', port '3306', database 'mydb');

-- 创建用户映射
CREATE USER MAPPING FOR current_user
SERVER remote_mysql
OPTIONS (username 'mysql_user', password 'password');
```

### 3.2 使用示例

```sql
-- 创建外部表
CREATE FOREIGN TABLE mysql_users (
    id INT,
    name TEXT,
    email TEXT
)
SERVER remote_mysql
OPTIONS (table_name 'users');

-- 查询外部表
SELECT * FROM mysql_users;
```

---

## 4. file_fdw

### 4.1 安装配置

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS file_fdw;

-- 创建服务器
CREATE SERVER file_server
FOREIGN DATA WRAPPER file_fdw;
```

### 4.2 使用示例

```sql
-- 创建外部表（CSV文件）
CREATE FOREIGN TABLE csv_data (
    id INT,
    name TEXT,
    value NUMERIC
)
SERVER file_server
OPTIONS (filename '/path/to/data.csv', format 'csv', header 'true');

-- 查询文件数据
SELECT * FROM csv_data;
```

---

## 5. 其他FDW扩展

### 5.1 oracle_fdw

```sql
-- Oracle数据源
CREATE SERVER oracle_server
FOREIGN DATA WRAPPER oracle_fdw
OPTIONS (dbserver '//oracle_host:1521/orcl');
```

### 5.2 multicorn

```sql
-- Python FDW框架
CREATE SERVER python_server
FOREIGN DATA WRAPPER multicorn
OPTIONS (wrapper 'multicorn.pythonfdw.PythonFdw');
```

---

## 📚 相关文档

- [FDW完整指南.md](./FDW完整指南.md) - FDW完整指南
- [多数据源查询.md](./多数据源查询.md) - 多数据源查询详解
- [02-查询与优化/README.md](../README.md) - 查询与优化主题

---

**最后更新**: 2025年1月
