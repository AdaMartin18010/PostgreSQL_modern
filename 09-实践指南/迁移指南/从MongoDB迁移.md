# 从 MongoDB 迁移到 PostgreSQL

> **更新时间**: 2025 年 11 月 1 日
> **技术版本**: PostgreSQL 14+, MongoDB 4.4+
> **文档编号**: 09-02-02

## 📑 目录

- [从 MongoDB 迁移到 PostgreSQL](#从-mongodb-迁移到-postgresql)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 迁移场景](#11-迁移场景)
    - [1.2 迁移优势](#12-迁移优势)
  - [2. 迁移准备](#2-迁移准备)
    - [2.1 环境准备](#21-环境准备)
    - [2.2 数据评估](#22-数据评估)
  - [3. 数据模型转换](#3-数据模型转换)
    - [3.1 文档到表结构](#31-文档到表结构)
    - [3.2 数组字段转换](#32-数组字段转换)
    - [3.3 嵌套文档转换](#33-嵌套文档转换)
  - [4. 迁移步骤](#4-迁移步骤)
    - [4.1 批量迁移脚本](#41-批量迁移脚本)
    - [4.2 增量迁移](#42-增量迁移)
  - [5. 数据验证](#5-数据验证)
    - [5.1 数据量验证](#51-数据量验证)
    - [5.2 数据一致性验证](#52-数据一致性验证)
  - [6. 性能优化](#6-性能优化)
    - [6.1 批量插入优化](#61-批量插入优化)
    - [6.2 索引创建](#62-索引创建)
  - [7. 常见问题](#7-常见问题)
    - [7.1 ObjectId 转换](#71-objectid-转换)
    - [7.2 时区处理](#72-时区处理)
  - [8. 参考资料](#8-参考资料)

---

## 1. 概述

### 1.1 迁移场景

**适用场景**:

- MongoDB 存储文档数据，需要迁移到 PostgreSQL
- 需要利用 PostgreSQL 的向量搜索能力
- 需要更好的事务支持和数据一致性

**不适用场景**:

- 需要 MongoDB 的灵活 schema
- 大量非结构化数据
- 简单的键值存储需求

### 1.2 迁移优势

- **向量搜索**: PostgreSQL + pgvector 支持向量搜索
- **事务支持**: ACID 事务保证
- **SQL 查询**: 强大的 SQL 查询能力
- **生态系统**: 丰富的工具和扩展

## 2. 迁移准备

### 2.1 环境准备

```bash
# 安装 PostgreSQL
sudo apt-get install postgresql-14

# 安装 pgvector 扩展
sudo apt-get install postgresql-14-pgvector

# 安装迁移工具
pip install pymongo psycopg2-binary
```

### 2.2 数据评估

```python
# 评估 MongoDB 数据
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['mydb']

# 统计集合大小
for collection_name in db.list_collection_names():
    collection = db[collection_name]
    count = collection.count_documents({})
    print(f"{collection_name}: {count} documents")
```

## 3. 数据模型转换

### 3.1 文档到表结构

**MongoDB 文档**:

```json
{
  "_id": ObjectId("..."),
  "name": "Product 1",
  "price": 100,
  "tags": ["electronics", "new"],
  "metadata": {
    "category": "electronics",
    "stock": 50
  }
}
```

**PostgreSQL 表结构**:

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price DECIMAL(10, 2),
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.2 数组字段转换

```python
# MongoDB 数组字段转换为 PostgreSQL 数组
def convert_array(mongo_array):
    """转换 MongoDB 数组为 PostgreSQL 数组"""
    if mongo_array is None:
        return None
    return list(mongo_array)
```

### 3.3 嵌套文档转换

```python
# MongoDB 嵌套文档转换为 JSONB
def convert_nested_doc(mongo_doc):
    """转换嵌套文档为 JSONB"""
    import json
    return json.dumps(mongo_doc)
```

## 4. 迁移步骤

### 4.1 批量迁移脚本

```python
import pymongo
import psycopg2
from psycopg2.extras import execute_batch

class MongoDBToPostgreSQLMigrator:
    def __init__(self, mongo_uri, pg_uri):
        self.mongo_client = pymongo.MongoClient(mongo_uri)
        self.pg_conn = psycopg2.connect(pg_uri)
        self.pg_cursor = self.pg_conn.cursor()

    def migrate_collection(self, mongo_db_name, mongo_collection_name, pg_table_name):
        """迁移单个集合"""
        mongo_db = self.mongo_client[mongo_db_name]
        mongo_collection = mongo_db[mongo_collection_name]

        # 批量读取和插入
        batch_size = 1000
        batch = []

        for doc in mongo_collection.find():
            # 转换文档
            pg_row = self._convert_document(doc)
            batch.append(pg_row)

            if len(batch) >= batch_size:
                self._insert_batch(pg_table_name, batch)
                batch = []

        # 插入剩余数据
        if batch:
            self._insert_batch(pg_table_name, batch)

        self.pg_conn.commit()

    def _convert_document(self, mongo_doc):
        """转换 MongoDB 文档为 PostgreSQL 行"""
        return (
            str(mongo_doc.get('_id', '')),
            mongo_doc.get('name', ''),
            mongo_doc.get('price', 0),
            mongo_doc.get('tags', []),
            json.dumps(mongo_doc.get('metadata', {}))
        )

    def _insert_batch(self, table_name, batch):
        """批量插入数据"""
        query = f"""
            INSERT INTO {table_name} (id, name, price, tags, metadata)
            VALUES (%s, %s, %s, %s, %s::jsonb)
        """
        execute_batch(self.pg_cursor, query, batch)
```

### 4.2 增量迁移

```python
# 增量迁移（基于时间戳）
def incremental_migrate(self, last_migration_time):
    """增量迁移"""
    query = {
        'updated_at': {'$gte': last_migration_time}
    }

    for doc in mongo_collection.find(query):
        # 检查是否已存在
        pg_cursor.execute(
            "SELECT id FROM products WHERE id = %s",
            (str(doc['_id']),)
        )

        if pg_cursor.fetchone():
            # 更新
            self._update_document(doc)
        else:
            # 插入
            self._insert_document(doc)
```

## 5. 数据验证

### 5.1 数据量验证

```python
# 验证数据量
def validate_count(mongo_collection, pg_table):
    mongo_count = mongo_collection.count_documents({})
    pg_cursor.execute(f"SELECT COUNT(*) FROM {pg_table}")
    pg_count = pg_cursor.fetchone()[0]

    assert mongo_count == pg_count, f"Count mismatch: {mongo_count} != {pg_count}"
    print(f"✓ Count validated: {mongo_count} documents")
```

### 5.2 数据一致性验证

```python
# 验证数据一致性
def validate_data(mongo_collection, pg_table):
    """验证数据一致性"""
    sample_size = 100
    sample_docs = list(mongo_collection.aggregate([
        {'$sample': {'size': sample_size}}
    ]))

    for mongo_doc in sample_docs:
        pg_cursor.execute(
            f"SELECT * FROM {pg_table} WHERE id = %s",
            (str(mongo_doc['_id']),)
        )
        pg_row = pg_cursor.fetchone()

        # 比较数据
        assert self._compare_documents(mongo_doc, pg_row)

    print(f"✓ Validated {sample_size} sample documents")
```

## 6. 性能优化

### 6.1 批量插入优化

```python
# 使用 COPY 命令批量插入（最快）
def fast_bulk_insert(self, table_name, data):
    """使用 COPY 命令快速插入"""
    import io

    # 准备数据流
    buffer = io.StringIO()
    for row in data:
        buffer.write('\t'.join(map(str, row)) + '\n')
    buffer.seek(0)

    # 使用 COPY
    pg_cursor.copy_from(buffer, table_name, columns=('id', 'name', 'price', 'tags', 'metadata'))
    pg_conn.commit()
```

### 6.2 索引创建

```sql
-- 迁移完成后创建索引
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_tags ON products USING GIN(tags);
CREATE INDEX idx_products_metadata ON products USING GIN(metadata);
```

## 7. 常见问题

### 7.1 ObjectId 转换

```python
# ObjectId 转换为字符串
def convert_objectid(obj_id):
    """转换 ObjectId 为字符串"""
    if isinstance(obj_id, pymongo.objectid.ObjectId):
        return str(obj_id)
    return obj_id
```

### 7.2 时区处理

```python
# MongoDB 日期转换为 PostgreSQL 时间戳
from datetime import datetime

def convert_datetime(mongo_date):
    """转换 MongoDB 日期"""
    if isinstance(mongo_date, datetime):
        return mongo_date
    return None
```

## 8. 参考资料

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [MongoDB 迁移指南](https://www.mongodb.com/docs/manual/core/migration/)

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
**文档编号**: 09-02-02
