# 从 MySQL 迁移到 PostgreSQL 向量搜索

> **更新时间**: 2025 年 11 月 1 日
> **技术版本**: PostgreSQL 14+, pgvector 0.7.0+
> **文档编号**: 09-02-01

## 📑 目录

- [从 MySQL 迁移到 PostgreSQL 向量搜索](#从-mysql-迁移到-postgresql-向量搜索)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 文档目标](#11-文档目标)
    - [1.2 迁移价值](#12-迁移价值)
    - [1.3 迁移挑战](#13-迁移挑战)
  - [2. 迁移策略](#2-迁移策略)
    - [2.1 评估阶段](#21-评估阶段)
      - [2.1.1 数据库差异分析](#211-数据库差异分析)
      - [2.1.2 兼容性检查](#212-兼容性检查)
      - [2.1.3 数据量评估](#213-数据量评估)
    - [2.2 数据迁移](#22-数据迁移)
      - [2.2.1 使用 pgloader 迁移](#221-使用-pgloader-迁移)
      - [2.2.2 手动迁移脚本](#222-手动迁移脚本)
      - [2.2.3 迁移工具对比](#223-迁移工具对比)
    - [2.3 数据类型映射](#23-数据类型映射)
      - [2.3.1 基础类型映射](#231-基础类型映射)
      - [2.3.2 复杂类型映射](#232-复杂类型映射)
      - [2.3.3 自增主键迁移](#233-自增主键迁移)
  - [3. 向量搜索迁移](#3-向量搜索迁移)
    - [3.1 迁移策略](#31-迁移策略)
      - [3.1.1 从其他向量数据库迁移](#311-从其他向量数据库迁移)
      - [3.1.2 从 MySQL 向量存储迁移](#312-从-mysql-向量存储迁移)
    - [3.2 数据导入](#32-数据导入)
      - [3.2.1 向量数据导入脚本](#321-向量数据导入脚本)
      - [3.2.2 批量导入优化](#322-批量导入优化)
    - [3.3 索引创建](#33-索引创建)
      - [3.3.1 HNSW 索引创建](#331-hnsw-索引创建)
      - [3.3.2 IVFFlat 索引创建](#332-ivfflat-索引创建)
  - [4. 迁移后优化](#4-迁移后优化)
    - [4.1 索引重建](#41-索引重建)
    - [4.2 查询重写](#42-查询重写)
    - [4.3 兼容性函数](#43-兼容性函数)
    - [4.4 性能优化](#44-性能优化)
  - [5. 迁移验证](#5-迁移验证)
    - [5.1 数据完整性验证](#51-数据完整性验证)
    - [5.2 性能验证](#52-性能验证)
    - [5.3 功能验证](#53-功能验证)
  - [6. 迁移检查清单](#6-迁移检查清单)
    - [6.1 迁移前准备](#61-迁移前准备)
    - [6.2 迁移中执行](#62-迁移中执行)
    - [6.3 迁移后处理](#63-迁移后处理)
  - [7. 常见问题](#7-常见问题)
    - [7.1 字符编码问题](#71-字符编码问题)
    - [7.2 日期时间格式](#72-日期时间格式)
    - [7.3 自增主键](#73-自增主键)
    - [7.4 其他常见问题](#74-其他常见问题)
  - [8. 最佳实践](#8-最佳实践)
    - [8.1 迁移策略选择](#81-迁移策略选择)
    - [8.2 风险控制](#82-风险控制)
  - [9. 参考资料](#9-参考资料)
    - [9.1 官方文档](#91-官方文档)
    - [9.2 技术文档](#92-技术文档)
    - [9.3 相关资源](#93-相关资源)

---

## 1. 概述

### 1.1 文档目标

**核心目标**:

本指南帮助您将 MySQL 数据库迁移到 PostgreSQL，特别关注向量搜索能力的迁移，确保迁移过程顺利且数据完整
。

**文档价值**:

| 价值项       | 说明                 | 影响             |
| ------------ | -------------------- | ---------------- |
| **迁移指导** | 提供完整迁移流程     | 减少迁移风险     |
| **向量迁移** | 专门指导向量数据迁移 | 获得向量搜索能力 |
| **性能提升** | 利用 PostgreSQL 优势 | 提升数据库性能   |

### 1.2 迁移价值

**迁移优势**:

| 优势          | MySQL    | PostgreSQL     | 说明                        |
| ------------- | -------- | -------------- | --------------------------- |
| **向量搜索**  | 不支持   | **pgvector**   | **新增 AI 能力**            |
| **JSON 支持** | JSON     | **JSONB**      | **更好的 JSON 性能**        |
| **全文搜索**  | FULLTEXT | **tsvector**   | **更强大的全文搜索**        |
| **窗口函数**  | 8.0+     | **原生支持**   | **更早支持，性能更好**      |
| **数据类型**  | 基础类型 | **丰富类型**   | **JSONB, ARRAY, RANGE 等**  |
| **扩展性**    | 有限     | **高度可扩展** | **PostGIS, TimescaleDB 等** |

### 1.3 迁移挑战

**迁移挑战与解决方案**:

| 挑战             | 影响             | 解决方案                |
| ---------------- | ---------------- | ----------------------- |
| **数据类型差异** | 需要映射转换     | 使用类型映射表          |
| **SQL 语法差异** | 查询需要重写     | 提供兼容性函数          |
| **自增主键差异** | 序列生成方式不同 | 使用 SERIAL 或 IDENTITY |
| **字符编码**     | 可能出现乱码     | 统一使用 UTF-8          |
| **日期时间格式** | 格式可能不同     | 使用标准格式或转换      |

## 2. 迁移策略

### 2.1 评估阶段

#### 2.1.1 数据库差异分析

**数据库特性对比**:

| 特性          | MySQL        | PostgreSQL    | 迁移复杂度 | 说明                       |
| ------------- | ------------ | ------------- | ---------- | -------------------------- |
| **数据类型**  | VARCHAR, INT | TEXT, INTEGER | ⭐⭐       | 基础类型映射简单           |
| **JSON 支持** | JSON         | JSONB         | ⭐         | JSONB 性能更好             |
| **全文搜索**  | FULLTEXT     | tsvector      | ⭐⭐       | 语法不同，需要重写         |
| **向量搜索**  | 不支持       | pgvector      | ⭐⭐⭐     | **新增功能，需要额外工作** |
| **窗口函数**  | 8.0+         | 原生支持      | ⭐         | 语法兼容性较好             |
| **存储过程**  | PROCEDURE    | FUNCTION      | ⭐⭐       | 语法差异较大               |
| **触发器**    | TRIGGER      | TRIGGER       | ⭐         | 语法略有差异               |

**迁移复杂度评估**:

- ⭐: 简单，直接迁移
- ⭐⭐: 中等，需要少量修改
- ⭐⭐⭐: 复杂，需要重构

#### 2.1.2 兼容性检查

**兼容性检查脚本**:

```sql
-- MySQL 兼容性检查
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    NUMERIC_PRECISION,
    NUMERIC_SCALE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_KEY,
    EXTRA
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'your_database'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- 检查索引
SELECT
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    NON_UNIQUE,
    INDEX_TYPE
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'your_database'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- 检查外键
SELECT
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'your_database'
  AND REFERENCED_TABLE_NAME IS NOT NULL;

-- 检查存储过程和函数
SELECT
    ROUTINE_NAME,
    ROUTINE_TYPE,
    DATA_TYPE
FROM INFORMATION_SCHEMA.ROUTINES
WHERE ROUTINE_SCHEMA = 'your_database';
```

**兼容性检查报告**:

| 检查项       | MySQL 数量 | PostgreSQL 兼容性 | 迁移复杂度 |
| ------------ | ---------- | ----------------- | ---------- |
| **表数量**   | -          | 完全兼容          | ⭐         |
| **索引数量** | -          | 完全兼容          | ⭐         |
| **外键数量** | -          | 完全兼容          | ⭐         |
| **存储过程** | -          | 需要转换          | ⭐⭐       |
| **触发器**   | -          | 需要转换          | ⭐⭐       |

#### 2.1.3 数据量评估

**数据量评估查询**:

```sql
-- MySQL 数据量评估
SELECT
    TABLE_NAME,
    TABLE_ROWS as estimated_rows,
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) as size_mb
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'your_database'
ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC;

-- 精确统计（可能较慢）
SELECT
    'users' as table_name,
    COUNT(*) as row_count,
    pg_size_pretty(SUM(pg_column_size(*))) as data_size
FROM users;
```

**数据量评估矩阵**:

| 数据量        | 迁移时间预估  | 推荐方式        | 说明                   |
| ------------- | ------------- | --------------- | ---------------------- |
| **<10GB**     | **<1 小时**   | pgloader        | 快速迁移               |
| **10-100GB**  | **1-6 小时**  | pgloader + 优化 | 中等规模               |
| **100GB-1TB** | **6-24 小时** | 分批迁移        | 大规模迁移             |
| **>1TB**      | **>24 小时**  | 分批 + 增量迁移 | **超大规模，需要规划** |

### 2.2 数据迁移

#### 2.2.1 使用 pgloader 迁移

**pgloader 优势**:

| 优势         | 说明                   |
| ------------ | ---------------------- |
| **自动化**   | 自动处理类型映射和转换 |
| **高性能**   | 支持并行迁移           |
| **容错性**   | 支持断点续传           |
| **类型转换** | 自动转换数据类型       |

**pgloader 安装**:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install pgloader

# macOS
brew install pgloader

# 从源码安装（最新版本）
git clone https://github.com/dimitri/pgloader.git
cd pgloader
make pgloader
```

**pgloader 配置**:

```bash
# 创建迁移配置文件 migration.load
cat > migration.load <<EOF
LOAD DATABASE
    FROM mysql://user:password@mysql-host:3306/source_db
    INTO postgresql://user:password@postgres-host:5432/target_db

WITH
    data only,
    create tables,
    create indexes,
    reset sequences,
    workers = 8,
    concurrency = 2,
    multiple readers per thread,
    rows per range = 10000

SET
    postgresql.identifier_case to lower,
    postgresql.timezone to 'UTC',
    work_mem to '256MB',
    maintenance_work_mem to '1GB'

CAST
    type datetime to timestamptz,
    type date to date,
    type time to time,
    type timestamp to timestamptz,
    type year to integer,
    type tinyint to boolean using tinyint-to-boolean,
    type json to jsonb

INCLUDING ONLY TABLE NAMES MATCHING ~/^users$/, ~/^products$/, ~/^orders$/

EXCLUDING TABLE NAMES MATCHING ~/^temp_/, ~/^test_/

BEFORE LOAD DO
    $$ CREATE EXTENSION IF NOT EXISTS vector; $$,
    $$ CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; $$
;
EOF

# 执行迁移
pgloader migration.load

# 查看迁移日志
pgloader migration.load --verbose
```

**迁移性能**:

| 数据量    | 迁移时间       | 说明           |
| --------- | -------------- | -------------- |
| **1GB**   | **2-5 分钟**   | 小数据量       |
| **10GB**  | **20-60 分钟** | 中等数据量     |
| **100GB** | **3-8 小时**   | 大数据量       |
| **1TB**   | **30-80 小时** | **超大数据量** |

#### 2.2.2 手动迁移脚本

**Python 迁移脚本**:

```python
# migrate_mysql_to_postgres.py
import mysql.connector
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.sql import SQL, Identifier
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MySQL 连接配置
MYSQL_CONFIG = {
    'host': 'mysql-host',
    'database': 'source_db',
    'user': 'mysql_user',
    'password': 'mysql_password',
    'charset': 'utf8mb4'
}

# PostgreSQL 连接配置
PG_CONFIG = {
    'host': 'postgres-host',
    'database': 'target_db',
    'user': 'postgres_user',
    'password': 'postgres_password'
}

def connect_mysql():
    """连接 MySQL"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        logger.info("✅ MySQL 连接成功")
        return conn
    except Exception as e:
        logger.error(f"❌ MySQL 连接失败: {e}")
        raise

def connect_postgresql():
    """连接 PostgreSQL"""
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        conn.set_client_encoding('UTF8')
        logger.info("✅ PostgreSQL 连接成功")
        return conn
    except Exception as e:
        logger.error(f"❌ PostgreSQL 连接失败: {e}")
        raise

def get_mysql_tables(mysql_conn):
    """获取 MySQL 表列表"""
    cursor = mysql_conn.cursor()
    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s
          AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """, (MYSQL_CONFIG['database'],))
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables

def get_table_schema(mysql_conn, table_name: str) -> List[Dict]:
    """获取表结构"""
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            EXTRA
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
    """, (MYSQL_CONFIG['database'], table_name))
    columns = cursor.fetchall()
    cursor.close()
    return columns

def create_pg_table(pg_conn, table_name: str, columns: List[Dict]):
    """创建 PostgreSQL 表"""
    cursor = pg_conn.cursor()

    # 类型映射
    TYPE_MAPPING = {
        'VARCHAR': 'TEXT',
        'CHAR': 'TEXT',
        'TEXT': 'TEXT',
        'LONGTEXT': 'TEXT',
        'MEDIUMTEXT': 'TEXT',
        'INT': 'INTEGER',
        'INTEGER': 'INTEGER',
        'TINYINT': 'SMALLINT',
        'SMALLINT': 'SMALLINT',
        'MEDIUMINT': 'INTEGER',
        'BIGINT': 'BIGINT',
        'DECIMAL': 'NUMERIC',
        'NUMERIC': 'NUMERIC',
        'FLOAT': 'REAL',
        'DOUBLE': 'DOUBLE PRECISION',
        'DATETIME': 'TIMESTAMPTZ',
        'TIMESTAMP': 'TIMESTAMPTZ',
        'DATE': 'DATE',
        'TIME': 'TIME',
        'YEAR': 'INTEGER',
        'JSON': 'JSONB',
        'BLOB': 'BYTEA',
        'LONGBLOB': 'BYTEA',
        'BOOLEAN': 'BOOLEAN',
        'BIT': 'BIT'
    }

    column_defs = []
    for col in columns:
        mysql_type = col['DATA_TYPE'].upper()
        pg_type = TYPE_MAPPING.get(mysql_type, 'TEXT')

        # 处理长度和精度
        if mysql_type in ['VARCHAR', 'CHAR'] and col['CHARACTER_MAXIMUM_LENGTH']:
            pg_type = f"VARCHAR({col['CHARACTER_MAXIMUM_LENGTH']})"
        elif mysql_type in ['DECIMAL', 'NUMERIC']:
            precision = col['NUMERIC_PRECISION'] or 10
            scale = col['NUMERIC_SCALE'] or 0
            pg_type = f"NUMERIC({precision},{scale})"

        # 处理自增
        if 'AUTO_INCREMENT' in col['EXTRA']:
            pg_type = 'SERIAL'

        # 处理 NULL/NOT NULL
        nullable = '' if col['IS_NULLABLE'] == 'YES' else 'NOT NULL'

        column_defs.append(f"{col['COLUMN_NAME']} {pg_type} {nullable}")

    # 创建表
    create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(column_defs)}
        )
    """

    cursor.execute(create_sql)
    pg_conn.commit()
    cursor.close()
    logger.info(f"✅ 创建表 {table_name}")

def migrate_table(mysql_conn, pg_conn, table_name: str, batch_size: int = 1000):
    """迁移单个表"""
    logger.info(f"开始迁移表: {table_name}")

    mysql_cursor = mysql_conn.cursor(dictionary=True)
    pg_cursor = pg_conn.cursor()

    try:
        # 获取总行数
        mysql_cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        total_rows = mysql_cursor.fetchone()['count']
        logger.info(f"表 {table_name} 共有 {total_rows} 行")

        if total_rows == 0:
            logger.info(f"表 {table_name} 为空，跳过")
            return

        # 获取列名
        mysql_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        columns = [desc[0] for desc in mysql_cursor.description]
        placeholders = ', '.join(['%s'] * len(columns))

        # 分批读取和插入
        offset = 0
        inserted = 0

        while offset < total_rows:
            mysql_cursor.execute(f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}")
            rows = mysql_cursor.fetchall()

            if not rows:
                break

            # 转换数据
            values = [[row[col] for col in columns] for row in rows]

            # 批量插入
            insert_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES %s
                ON CONFLICT DO NOTHING
            """

            execute_values(pg_cursor, insert_sql, values)
            pg_conn.commit()

            inserted += len(rows)
            offset += batch_size

            logger.info(f"已迁移 {inserted}/{total_rows} 行 ({inserted/total_rows*100:.1f}%)")

        logger.info(f"✅ 表 {table_name} 迁移完成: {inserted} 行")

    except Exception as e:
        logger.error(f"❌ 表 {table_name} 迁移失败: {e}")
        pg_conn.rollback()
        raise
    finally:
        mysql_cursor.close()
        pg_cursor.close()

def main():
    """主函数"""
    mysql_conn = connect_mysql()
    pg_conn = connect_postgresql()

    try:
        # 获取表列表
        tables = get_mysql_tables(mysql_conn)
        logger.info(f"找到 {len(tables)} 个表需要迁移")

        # 迁移每个表
        for table_name in tables:
            # 创建表结构
            columns = get_table_schema(mysql_conn, table_name)
            create_pg_table(pg_conn, table_name, columns)

            # 迁移数据
            migrate_table(mysql_conn, pg_conn, table_name)

        logger.info("✅ 所有表迁移完成")

    finally:
        mysql_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    main()
```

#### 2.2.3 迁移工具对比

**迁移工具对比**:

| 工具                 | 优点                   | 缺点                 | 适用场景               |
| -------------------- | ---------------------- | -------------------- | ---------------------- |
| **pgloader**         | 自动化、高效、支持并行 | 需要安装             | **推荐用于大部分场景** |
| **手动脚本**         | 灵活、可控             | 开发成本高           | 复杂迁移场景           |
| **mysqldump + psql** | 简单、通用             | 速度慢、需要手动处理 | 小数据量迁移           |

### 2.3 数据类型映射

#### 2.3.1 基础类型映射

**基础类型映射表**:

```python
# MySQL 到 PostgreSQL 数据类型映射
TYPE_MAPPING = {
    # 字符串类型
    'VARCHAR': 'TEXT',
    'CHAR': 'TEXT',
    'TEXT': 'TEXT',
    'TINYTEXT': 'TEXT',
    'MEDIUMTEXT': 'TEXT',
    'LONGTEXT': 'TEXT',

    # 整数类型
    'TINYINT': 'SMALLINT',
    'SMALLINT': 'SMALLINT',
    'MEDIUMINT': 'INTEGER',
    'INT': 'INTEGER',
    'INTEGER': 'INTEGER',
    'BIGINT': 'BIGINT',

    # 浮点类型
    'FLOAT': 'REAL',
    'DOUBLE': 'DOUBLE PRECISION',

    # 精确数值类型
    'DECIMAL': 'NUMERIC',
    'NUMERIC': 'NUMERIC',

    # 日期时间类型
    'DATE': 'DATE',
    'TIME': 'TIME',
    'DATETIME': 'TIMESTAMPTZ',
    'TIMESTAMP': 'TIMESTAMPTZ',
    'YEAR': 'INTEGER',

    # 二进制类型
    'BINARY': 'BYTEA',
    'VARBINARY': 'BYTEA',
    'TINYBLOB': 'BYTEA',
    'BLOB': 'BYTEA',
    'MEDIUMBLOB': 'BYTEA',
    'LONGBLOB': 'BYTEA',

    # 其他类型
    'JSON': 'JSONB',
    'BOOLEAN': 'BOOLEAN',
    'BIT': 'BIT',
    'ENUM': 'TEXT',  # 需要特殊处理
    'SET': 'TEXT'    # 需要特殊处理
}

def convert_mysql_type(mysql_type: str, column_info: Dict) -> str:
    """转换 MySQL 数据类型到 PostgreSQL"""
    base_type = mysql_type.split('(')[0].upper().strip()

    # 处理带长度的类型
    if base_type in ['VARCHAR', 'CHAR']:
        length = column_info.get('CHARACTER_MAXIMUM_LENGTH')
        if length:
            return f"VARCHAR({length})"
        return 'TEXT'

    # 处理精度和标度
    if base_type in ['DECIMAL', 'NUMERIC']:
        precision = column_info.get('NUMERIC_PRECISION', 10)
        scale = column_info.get('NUMERIC_SCALE', 0)
        return f"NUMERIC({precision},{scale})"

    # 处理 ENUM 和 SET（转换为 TEXT）
    if base_type in ['ENUM', 'SET']:
        return 'TEXT'

    return TYPE_MAPPING.get(base_type, 'TEXT')
```

#### 2.3.2 复杂类型映射

**复杂类型处理**:

```sql
-- MySQL ENUM 类型
CREATE TABLE products (
    status ENUM('active', 'inactive', 'pending')
);

-- PostgreSQL 处理方式 1: 使用 TEXT
CREATE TABLE products (
    status TEXT CHECK (status IN ('active', 'inactive', 'pending'))
);

-- PostgreSQL 处理方式 2: 使用枚举类型（推荐）
CREATE TYPE product_status AS ENUM ('active', 'inactive', 'pending');
CREATE TABLE products (
    status product_status
);

-- MySQL SET 类型
CREATE TABLE users (
    permissions SET('read', 'write', 'delete')
);

-- PostgreSQL 处理方式: 使用数组
CREATE TABLE users (
    permissions TEXT[] CHECK (permissions <@ ARRAY['read', 'write', 'delete'])
);

-- 或使用位掩码（如果需要兼容）
CREATE TABLE users (
    permissions INTEGER  -- 使用位掩码表示
);
```

#### 2.3.3 自增主键迁移

**自增主键迁移**:

```sql
-- MySQL AUTO_INCREMENT
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);

-- PostgreSQL 方式 1: 使用 SERIAL（推荐）
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT
);

-- PostgreSQL 方式 2: 使用 IDENTITY（PostgreSQL 10+）
CREATE TABLE users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT
);

-- 迁移现有数据时，需要同步序列
-- 1. 插入数据后，设置序列起始值
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

-- 2. 或者手动创建序列
CREATE SEQUENCE users_id_seq;
ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq');
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
```

## 3. 向量搜索迁移

### 3.1 迁移策略

#### 3.1.1 从其他向量数据库迁移

**从 Pinecone/Milvus/Qdrant 等迁移**:

```python
# migrate_from_pinecone.py
import pinecone
import psycopg2
from psycopg2.extras import execute_values
import numpy as np

# Pinecone 配置
PINECONE_API_KEY = "your-api-key"
PINECONE_ENVIRONMENT = "us-east-1"
PINECONE_INDEX_NAME = "your-index"

# PostgreSQL 配置
PG_CONFIG = {
    'host': 'localhost',
    'database': 'vector_db',
    'user': 'postgres',
    'password': 'postgres'
}

def migrate_from_pinecone():
    """从 Pinecone 迁移到 PostgreSQL + pgvector"""
    # 连接 Pinecone
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
    index = pinecone.Index(PINECONE_INDEX_NAME)

    # 连接 PostgreSQL
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    # 创建表（如果不存在）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            content TEXT,
            embedding vector(1536),
            metadata JSONB
        )
    """)

    # 获取所有向量（根据 Pinecone API）
    # 注意: Pinecone 可能需要分批获取
    batch_size = 100
    offset = None

    while True:
        query_result = index.query(
            vector=[0.0] * 1536,  # 使用零向量查询所有
            top_k=10000,
            include_metadata=True,
            namespace=""
        )

        if not query_result.matches:
            break

        # 批量插入
        values = []
        for match in query_result.matches:
            values.append((
                match.id,
                match.metadata.get('content', ''),
                np.array(match.values).tolist(),  # 转换为列表
                str(match.metadata)
            ))

        execute_values(
            cur,
            """
            INSERT INTO documents (id, content, embedding, metadata)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata
            """,
            values
        )

        conn.commit()
        print(f"✅ 已迁移 {len(values)} 条数据")

        if len(query_result.matches) < batch_size:
            break

    # 创建索引
    cur.execute("""
        CREATE INDEX IF NOT EXISTS documents_embedding_idx
        ON documents
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    conn.commit()
    conn.close()
    print("✅ 迁移完成")

if __name__ == "__main__":
    migrate_from_pinecone()
```

#### 3.1.2 从 MySQL 向量存储迁移

**MySQL 向量存储迁移**:

```python
# migrate_vectors_from_mysql.py
import mysql.connector
import psycopg2
from psycopg2.extras import execute_values
import json
import numpy as np

def migrate_vectors_from_mysql():
    """从 MySQL 迁移向量数据"""
    # MySQL 连接
    mysql_conn = mysql.connector.connect(
        host='mysql-host',
        database='source_db',
        user='user',
        password='password'
    )

    # PostgreSQL 连接
    pg_conn = psycopg2.connect(
        host='postgres-host',
        database='target_db',
        user='postgres',
        password='postgres'
    )
    pg_cursor = pg_conn.cursor()

    # 创建向量表
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            content TEXT,
            embedding vector(1536),
            metadata JSONB
        )
    """)

    # 从 MySQL 读取向量数据
    mysql_cursor = mysql_conn.cursor(dictionary=True)
    mysql_cursor.execute("""
        SELECT id, content, embedding_json, metadata_json
        FROM documents
    """)

    batch_size = 1000
    batch = []

    for row in mysql_cursor:
        # 解析 JSON 格式的向量
        embedding = json.loads(row['embedding_json'])

        # 转换为向量格式
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'

        # 解析元数据
        metadata = json.loads(row['metadata_json']) if row['metadata_json'] else {}

        batch.append((
            row['id'],
            row['content'],
            embedding_str,
            json.dumps(metadata)
        ))

        if len(batch) >= batch_size:
            # 批量插入
            execute_values(
                pg_cursor,
                """
                INSERT INTO documents (id, content, embedding, metadata)
                VALUES %s
                """,
                batch
            )
            pg_conn.commit()
            print(f"✅ 已迁移 {len(batch)} 条数据")
            batch = []

    # 处理剩余数据
    if batch:
        execute_values(
            pg_cursor,
            """
            INSERT INTO documents (id, content, embedding, metadata)
            VALUES %s
            """,
            batch
        )
        pg_conn.commit()

    # 创建索引
    pg_cursor.execute("""
        CREATE INDEX IF NOT EXISTS documents_embedding_idx
        ON documents
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    pg_conn.commit()
    mysql_conn.close()
    pg_conn.close()
    print("✅ 向量数据迁移完成")

if __name__ == "__main__":
    migrate_vectors_from_mysql()
```

### 3.2 数据导入

#### 3.2.1 向量数据导入脚本

**完整的向量数据导入脚本**:

```python
# import_vectors.py
import psycopg2
from psycopg2.extras import execute_values
import json
import numpy as np
from typing import List, Dict

def import_vectors_from_json(json_file: str, pg_config: Dict):
    """从 JSON 文件导入向量数据"""
    # 读取 JSON 文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 连接 PostgreSQL
    conn = psycopg2.connect(**pg_config)
    cur = conn.cursor()

    # 准备数据
    values = []
    for doc in data:
        # 确保向量维度一致
        embedding = doc.get('embedding', [])
        if isinstance(embedding, str):
            embedding = json.loads(embedding)

        embedding_str = '[' + ','.join(map(str, embedding)) + ']'

        values.append((
            doc.get('id'),
            doc.get('content', ''),
            embedding_str,
            json.dumps(doc.get('metadata', {}))
        ))

    # 批量插入
    batch_size = 1000
    for i in range(0, len(values), batch_size):
        batch = values[i:i+batch_size]
        execute_values(
            cur,
            """
            INSERT INTO documents (id, content, embedding, metadata)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata
            """,
            batch
        )
        conn.commit()
        print(f"✅ 已导入 {min(i+batch_size, len(values))}/{len(values)} 条数据")

    conn.close()
    print("✅ 向量数据导入完成")

def import_vectors_from_csv(csv_file: str, pg_config: Dict):
    """从 CSV 文件导入向量数据"""
    import csv

    conn = psycopg2.connect(**pg_config)
    cur = conn.cursor()

    values = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 解析向量（假设向量以逗号分隔的字符串存储）
            embedding = [float(x) for x in row['embedding'].split(',')]
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'

            values.append((
                int(row['id']),
                row['content'],
                embedding_str,
                row.get('metadata', '{}')
            ))

    # 批量插入
    execute_values(
        cur,
        """
        INSERT INTO documents (id, content, embedding, metadata)
        VALUES %s
        """,
        values
    )

    conn.commit()
    conn.close()
    print(f"✅ 已导入 {len(values)} 条数据")

if __name__ == "__main__":
    pg_config = {
        'host': 'localhost',
        'database': 'vector_db',
        'user': 'postgres',
        'password': 'postgres'
    }

    # 从 JSON 导入
    import_vectors_from_json('vectors.json', pg_config)

    # 从 CSV 导入
    # import_vectors_from_csv('vectors.csv', pg_config)
```

#### 3.2.2 批量导入优化

**批量导入优化技巧**:

```python
# 优化技巧 1: 禁用自动提交，批量提交
conn.autocommit = False

# 优化技巧 2: 使用 COPY（最快）
import io

def import_with_copy(pg_conn, data: List[Dict]):
    """使用 COPY 命令导入（最快）"""
    cur = pg_conn.cursor()

    # 准备数据流
    output = io.StringIO()
    for doc in data:
        embedding_str = '[' + ','.join(map(str, doc['embedding'])) + ']'
        output.write(f"{doc['id']}\t{doc['content']}\t{embedding_str}\t{json.dumps(doc['metadata'])}\n")

    output.seek(0)

    # 使用 COPY
    cur.copy_from(
        output,
        'documents',
        columns=('id', 'content', 'embedding', 'metadata'),
        null=''
    )

    pg_conn.commit()
    cur.close()

# 优化技巧 3: 分批导入，创建索引
def import_and_index(pg_conn, data: List[Dict], batch_size: int = 10000):
    """分批导入，每批后创建索引"""
    total = len(data)

    for i in range(0, total, batch_size):
        batch = data[i:i+batch_size]

        # 导入数据
        import_batch(pg_conn, batch)

        # 如果已导入足够数据，创建索引
        if i > 0 and i % (batch_size * 10) == 0:
            cur = pg_conn.cursor()
            cur.execute("""
                CREATE INDEX IF NOT EXISTS documents_embedding_idx
                ON documents
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """)
            pg_conn.commit()
            cur.close()
            print(f"✅ 已创建索引（{i}/{total} 条数据）")
```

### 3.3 索引创建

#### 3.3.1 HNSW 索引创建

**HNSW 索引创建策略**:

```sql
-- 方案 1: 先导入数据，后创建索引（推荐）
-- 1. 导入所有数据
-- 2. 创建索引
CREATE INDEX documents_embedding_idx
ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,              -- 每层最大连接数（默认 16）
    ef_construction = 64  -- 构建时搜索范围（默认 64）
);

-- 方案 2: 使用并发创建（PostgreSQL 12+）
CREATE INDEX CONCURRENTLY documents_embedding_idx
ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 方案 3: 高性能配置（大数据量）
CREATE INDEX documents_embedding_idx
ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 32,              -- 提高精度
    ef_construction = 200  -- 提高构建质量
);

-- 查看索引创建进度
SELECT
    pid,
    now() - query_start AS duration,
    query
FROM pg_stat_activity
WHERE query LIKE '%CREATE INDEX%';
```

#### 3.3.2 IVFFlat 索引创建

**IVFFlat 索引创建**:

```sql
-- IVFFlat 索引（适合大规模数据）
-- 注意：需要先导入足够的数据（至少 lists 数量的 10 倍）

-- 1. 先导入数据
-- 2. 创建索引
CREATE INDEX documents_embedding_idx
ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (
    lists = 1000  -- 聚类数量，建议 = rows/1000
);

-- 索引参数说明
-- lists: 聚类数量，建议为数据行数的 1/1000
-- 例如：100万行数据，lists = 1000
```

**索引选择建议**:

| 数据量          | 推荐索引       | 参数                     | 说明     |
| --------------- | -------------- | ------------------------ | -------- |
| **<100 万**     | HNSW           | m=16, ef_construction=64 | 高精度   |
| **100-1000 万** | IVFFlat        | lists=数据量/1000        | 高性能   |
| **>1000 万**    | IVFFlat + 分区 | lists=分区数据量/1000    | 超大规模 |

## 4. 迁移后优化

### 4.1 索引重建

**索引重建策略**:

```sql
-- 1. 重建索引（优化性能）
REINDEX INDEX CONCURRENTLY documents_embedding_idx;

-- 2. 分析表（更新统计信息）
ANALYZE documents;

-- 3. 检查索引健康度
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE tablename = 'documents';

-- 4. 清理碎片
VACUUM ANALYZE documents;
```

### 4.2 查询重写

**MySQL 到 PostgreSQL 查询重写**:

```sql
-- MySQL 全文搜索
SELECT * FROM articles
WHERE MATCH(title, content) AGAINST('keyword' IN NATURAL LANGUAGE MODE);

-- PostgreSQL 全文搜索
SELECT * FROM articles
WHERE to_tsvector('english', title || ' ' || content)
      @@ to_tsquery('english', 'keyword');

-- MySQL LIKE 查询
SELECT * FROM users WHERE name LIKE '%keyword%';

-- PostgreSQL 全文搜索（性能更好）
SELECT * FROM users
WHERE to_tsvector('english', name) @@ to_tsquery('english', 'keyword');

-- 或使用 ILIKE（不区分大小写 LIKE）
SELECT * FROM users WHERE name ILIKE '%keyword%';

-- 向量搜索（新能力）
SELECT
    id,
    content,
    1 - (embedding <=> query_vector::vector) as similarity
FROM documents
ORDER BY embedding <=> query_vector::vector
LIMIT 10;

-- 混合搜索（向量 + 全文）
SELECT
    id,
    content,
    1 - (embedding <=> query_vector::vector) as vector_similarity,
    ts_rank(to_tsvector('english', content), to_tsquery('english', 'keyword')) as text_rank
FROM documents
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'keyword')
ORDER BY vector_similarity DESC, text_rank DESC
LIMIT 10;
```

### 4.3 兼容性函数

**MySQL 兼容性函数**:

```sql
-- 创建 MySQL DATE_FORMAT 兼容函数
CREATE OR REPLACE FUNCTION mysql_date_format(
    date_val DATE,
    format_str TEXT
)
RETURNS TEXT AS $$
BEGIN
    RETURN TO_CHAR(date_val, format_str);
END;
$$ LANGUAGE plpgsql;

-- 创建 MySQL CONCAT 兼容函数（PostgreSQL 已有，但语法不同）
-- MySQL: CONCAT('a', 'b', 'c')
-- PostgreSQL: 'a' || 'b' || 'c'

-- 创建 MySQL IFNULL 兼容函数
CREATE OR REPLACE FUNCTION mysql_ifnull(anyelement, anyelement)
RETURNS anyelement AS $$
BEGIN
    RETURN COALESCE($1, $2);
END;
$$ LANGUAGE plpgsql;

-- 使用示例
SELECT
    mysql_date_format(NOW()::DATE, 'YYYY-MM-DD') as formatted_date,
    mysql_ifnull(NULL, 'default') as default_value;
```

### 4.4 性能优化

**性能优化步骤**:

```sql
-- 1. 更新统计信息
ANALYZE documents;

-- 2. 检查慢查询
SELECT
    query,
    mean_exec_time,
    calls,
    total_exec_time
FROM pg_stat_statements
WHERE query LIKE '%<=>%' OR query LIKE '%<->%'
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 3. 优化查询参数
SET hnsw.ef_search = 40;  -- HNSW 搜索范围
SET ivfflat.probes = 10;   -- IVFFlat 搜索聚类数

-- 4. 检查索引使用情况
EXPLAIN ANALYZE
SELECT * FROM documents
ORDER BY embedding <=> query_vector::vector
LIMIT 10;

-- 应该显示使用索引
```

## 5. 迁移验证

### 5.1 数据完整性验证

**数据完整性验证查询**:

```sql
-- 1. 验证行数
SELECT
    'MySQL' as source,
    (SELECT COUNT(*) FROM mysql_documents) as row_count
UNION ALL
SELECT
    'PostgreSQL' as source,
    COUNT(*) as row_count
FROM documents;

-- 2. 验证数据一致性（抽样）
SELECT
    m.id,
    m.content as mysql_content,
    p.content as pg_content,
    CASE
        WHEN m.content = p.content THEN '一致'
        ELSE '不一致'
    END as status
FROM mysql_documents m
JOIN documents p ON m.id = p.id
LIMIT 100;

-- 3. 验证向量数据
SELECT
    COUNT(*) as total_vectors,
    COUNT(*) FILTER (WHERE embedding IS NOT NULL) as non_null_vectors,
    AVG(array_length(embedding::text::numeric[], 1)) as avg_dimensions
FROM documents;

-- 4. 验证索引
SELECT
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE tablename = 'documents';
```

### 5.2 性能验证

**性能验证测试**:

```sql
-- 1. 测试向量查询性能
EXPLAIN ANALYZE
SELECT
    id,
    content,
    1 - (embedding <=> query_vector::vector) as similarity
FROM documents
ORDER BY embedding <=> query_vector::vector
LIMIT 10;

-- 关键指标：
-- - Execution Time（应该 < 50ms）
-- - 是否使用索引（应该显示 Index Scan）

-- 2. 测试批量查询性能
EXPLAIN ANALYZE
SELECT
    id,
    content,
    1 - (embedding <=> query_vector::vector) as similarity
FROM documents
WHERE embedding <=> query_vector::vector < 0.3
ORDER BY embedding <=> query_vector::vector
LIMIT 100;

-- 3. 测试混合搜索性能
EXPLAIN ANALYZE
SELECT
    id,
    content,
    1 - (embedding <=> query_vector::vector) as vector_similarity,
    ts_rank(to_tsvector('english', content), to_tsquery('english', 'keyword')) as text_rank
FROM documents
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'keyword')
ORDER BY vector_similarity DESC, text_rank DESC
LIMIT 10;
```

### 5.3 功能验证

**功能验证清单**:

- [ ] 向量查询功能正常
- [ ] 全文搜索功能正常
- [ ] 混合搜索功能正常
- [ ] 数据写入功能正常
- [ ] 索引构建成功
- [ ] 性能满足要求

## 6. 迁移检查清单

### 6.1 迁移前准备

**迁移前检查清单**:

- [ ] **备份源数据库**（MySQL 完整备份）
- [ ] **评估数据量大小**（行数、存储空间）
- [ ] **检查数据类型兼容性**（使用兼容性检查脚本）
- [ ] **准备迁移脚本**（pgloader 配置或 Python 脚本）
- [ ] **设置测试环境**（PostgreSQL 测试实例）
- [ ] **准备回滚方案**（保留 MySQL 数据）
- [ ] **通知相关团队**（开发、运维、测试）

### 6.2 迁移中执行

**迁移中执行清单**:

- [ ] **执行数据迁移**（使用 pgloader 或脚本）
- [ ] **验证数据完整性**（检查行数、抽样对比）
- [ ] **创建索引**（HNSW 或 IVFFlat）
- [ ] **更新应用代码**（修改 SQL 查询、连接配置）
- [ ] **执行测试查询**（基本查询、向量查询）
- [ ] **验证向量搜索功能**（测试向量查询性能）
- [ ] **监控迁移进度**（日志、性能指标）

### 6.3 迁移后处理

**迁移后处理清单**:

- [ ] **性能基准测试**（对比 MySQL 性能）
- [ ] **监控系统状态**（CPU、内存、磁盘）
- [ ] **优化慢查询**（分析慢查询日志）
- [ ] **配置备份策略**（PostgreSQL 备份）
- [ ] **文档更新**（API 文档、架构文档）
- [ ] **团队培训**（PostgreSQL 使用培训）
- [ ] **关闭 MySQL 实例**（迁移完成确认后）

## 7. 常见问题

### 7.1 字符编码问题

**字符编码问题处理**:

```sql
-- 1. 设置客户端编码
SET client_encoding = 'UTF8';

-- 2. 检查数据库编码
SELECT datname, encoding, datcollate, datctype
FROM pg_database
WHERE datname = current_database();

-- 3. 检查表编码
SELECT
    schemaname,
    tablename,
    attname,
    pg_encoding_to_char(encoding) as encoding
FROM pg_catalog.pg_attribute
WHERE attrelid = 'documents'::regclass;

-- 4. 创建数据库时指定编码
CREATE DATABASE target_db
WITH ENCODING = 'UTF8'
LC_COLLATE = 'en_US.UTF-8'
LC_CTYPE = 'en_US.UTF-8';
```

### 7.2 日期时间格式

**日期时间格式处理**:

```sql
-- 1. 设置时区
SET timezone = 'UTC';

-- 2. 设置日期格式
SET datestyle = 'ISO, MDY';

-- 3. 日期转换
SELECT
    '2025-11-01'::DATE,
    '2025-11-01 10:00:00'::TIMESTAMPTZ,
    NOW()::TIMESTAMPTZ;

-- 4. 日期格式化
SELECT TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS') as formatted_date;

-- 5. 时区转换
SELECT
    NOW() as utc_time,
    NOW() AT TIME ZONE 'Asia/Shanghai' as shanghai_time;
```

### 7.3 自增主键

**自增主键处理**:

```sql
-- 1. 使用 SERIAL（推荐）
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT
);

-- 2. 使用 IDENTITY（PostgreSQL 10+）
CREATE TABLE users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT
);

-- 3. 迁移现有数据后，同步序列
INSERT INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob');
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

-- 4. 检查序列当前值
SELECT currval('users_id_seq');

-- 5. 重置序列
SELECT setval('users_id_seq', 1, false);
```

### 7.4 其他常见问题

**其他常见问题**:

1. **NULL 值处理**:

   ```sql
   -- MySQL: IFNULL(value, default)
   -- PostgreSQL: COALESCE(value, default)
   SELECT COALESCE(name, 'Unknown') FROM users;
   ```

2. **字符串拼接**:

   ```sql
   -- MySQL: CONCAT('a', 'b')
   -- PostgreSQL: 'a' || 'b'
   SELECT first_name || ' ' || last_name FROM users;
   ```

3. **LIMIT 语法**:

   ```sql
   -- MySQL: LIMIT 10 OFFSET 20
   -- PostgreSQL: LIMIT 10 OFFSET 20（相同）
   SELECT * FROM users LIMIT 10 OFFSET 20;
   ```

4. **布尔值**:

   ```sql
   -- MySQL: 使用 TINYINT(1)
   -- PostgreSQL: 使用 BOOLEAN
   CREATE TABLE users (
       is_active BOOLEAN DEFAULT TRUE
   );
   ```

## 8. 最佳实践

### 8.1 迁移策略选择

**迁移策略选择矩阵**:

| 数据量        | 迁移工具   | 迁移方式    | 说明             |
| ------------- | ---------- | ----------- | ---------------- |
| **<10GB**     | pgloader   | 一次性迁移  | 快速完成         |
| **10-100GB**  | pgloader   | 一次性迁移  | 可能需要优化     |
| **100GB-1TB** | 自定义脚本 | 分批迁移    | 需要规划         |
| **>1TB**      | 自定义脚本 | 分批 + 增量 | **需要详细规划** |

### 8.2 风险控制

**风险控制措施**:

1. **备份策略**:

   - 迁移前完整备份 MySQL
   - 迁移后立即备份 PostgreSQL
   - 保留多个备份版本

2. **测试验证**:

   - 先在测试环境验证
   - 执行完整的功能测试
   - 性能基准测试

3. **回滚方案**:

   - 保留 MySQL 数据
   - 准备回滚脚本
   - 制定回滚流程

4. **监控告警**:
   - 监控迁移进度
   - 监控系统资源
   - 设置告警阈值

## 9. 参考资料

### 9.1 官方文档

- [pgloader 官方文档](https://pgloader.readthedocs.io/) - pgloader Documentation
- [MySQL 到 PostgreSQL 迁移指南](https://www.postgresql.org/docs/current/migration.html) - Migration
  Guide

### 9.2 技术文档

- [快速开始指南](../../01-向量与混合搜索/最佳实践/快速开始指南.md) - Quick Start Guide
- [pgvector 核心原理](../../01-向量与混合搜索/技术原理/pgvector核心原理.md) - pgvector Core
  Principles

### 9.3 相关资源

- [PostgreSQL 数据类型文档](https://www.postgresql.org/docs/current/datatype.html) - Data Types
- [MySQL 到 PostgreSQL 迁移工具对比](https://wiki.postgresql.org/wiki/Converting_from_other_Databases_to_PostgreSQL)
  Migration Tools

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
**文档编号**: 09-04-01
