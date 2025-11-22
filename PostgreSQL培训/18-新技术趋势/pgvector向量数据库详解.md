# pgvector 向量数据库详解

> **更新时间**: 2025 年 1 月
> **技术版本**: PostgreSQL 17+/18+ with pgvector
> **文档编号**: 03-03-TREND-01

## 📑 概述

pgvector 是 PostgreSQL 的向量数据库扩展，支持高效的向量相似度搜索。
它是 AI/ML 应用的核心技术，广泛应用于推荐系统、语义搜索、图像搜索、RAG（检索增强生成）等场景。

## 🎯 核心价值

- **向量相似度搜索**：支持高效的向量相似度计算和搜索
- **多种索引类型**：HNSW、IVFFlat 等高性能索引
- **AI/ML 集成**：与 OpenAI、Hugging Face 等 AI 模型无缝集成
- **混合搜索**：向量搜索 + 全文搜索的混合查询
- **生产就绪**：成熟稳定，已在生产环境大规模使用

## 📚 目录

- [pgvector 向量数据库详解](#pgvector-向量数据库详解)
  - [📑 概述](#-概述)
  - [🎯 核心价值](#-核心价值)
  - [📚 目录](#-目录)
  - [1. pgvector 基础](#1-pgvector-基础)
    - [1.1 什么是 pgvector](#11-什么是-pgvector)
    - [1.2 安装 pgvector](#12-安装-pgvector)
    - [1.3 版本要求](#13-版本要求)
  - [2. 向量数据类型](#2-向量数据类型)
    - [2.1 vector 类型](#21-vector-类型)
    - [2.2 向量维度](#22-向量维度)
  - [3. 向量索引](#3-向量索引)
    - [3.1 HNSW 索引（推荐）](#31-hnsw-索引推荐)
    - [3.2 IVFFlat 索引](#32-ivfflat-索引)
    - [3.3 索引选择建议](#33-索引选择建议)
  - [4. 相似度搜索](#4-相似度搜索)
    - [4.1 相似度操作符](#41-相似度操作符)
    - [4.2 相似度阈值查询](#42-相似度阈值查询)
    - [4.3 混合查询](#43-混合查询)
  - [5. 性能优化](#5-性能优化)
    - [5.1 索引参数调优](#51-索引参数调优)
    - [5.2 批量插入优化](#52-批量插入优化)
    - [5.3 查询优化](#53-查询优化)
  - [6. AI 应用集成](#6-ai-应用集成)
    - [6.1 OpenAI 集成](#61-openai-集成)
    - [6.2 语义搜索](#62-语义搜索)
    - [6.3 RAG 应用](#63-rag-应用)
  - [7. 实际案例](#7-实际案例)
    - [7.1 案例：电商推荐系统](#71-案例电商推荐系统)
    - [7.2 案例：图像搜索](#72-案例图像搜索)
  - [📊 总结](#-总结)

---

## 1. pgvector 基础

### 1.1 什么是 pgvector

pgvector 是 PostgreSQL 的开源扩展，为 PostgreSQL 添加了向量数据类型和相似度搜索功能。

### 1.2 安装 pgvector

```sql
-- 使用扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证安装
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 1.3 版本要求

- PostgreSQL 11+
- 推荐 PostgreSQL 17+ 以获得最佳性能

---

## 2. 向量数据类型

### 2.1 vector 类型

```sql
-- 创建向量列
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name TEXT,
    embedding vector(1536)  -- 1536 维向量（OpenAI ada-002）
);

-- 插入向量数据
INSERT INTO items (name, embedding)
VALUES (
    'Product A',
    '[0.1, 0.2, 0.3, ...]'::vector
);
```

### 2.2 向量维度

- 支持任意维度（1-16,000）
- 常见维度：
  - OpenAI ada-002: 1536
  - OpenAI text-embedding-3-small: 1536
  - OpenAI text-embedding-3-large: 3072
  - sentence-transformers: 384, 768

---

## 3. 向量索引

### 3.1 HNSW 索引（推荐）

```sql
-- 创建 HNSW 索引
CREATE INDEX ON items
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 参数说明：
-- m: 每个节点的最大连接数（默认 16）
-- ef_construction: 构建时的搜索范围（默认 64）
```

**特点**：

- 查询速度快
- 索引构建时间较长
- 适合读多写少的场景

### 3.2 IVFFlat 索引

```sql
-- 创建 IVFFlat 索引
CREATE INDEX ON items
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 参数说明：
-- lists: 聚类中心数量（建议：rows / 1000）
```

**特点**：

- 索引构建速度快
- 查询速度较 HNSW 慢
- 适合写多读少的场景

### 3.3 索引选择建议

| 场景 | 推荐索引 | 原因 |
|------|---------|------|
| 读多写少 | HNSW | 查询性能最优 |
| 写多读少 | IVFFlat | 构建速度快 |
| 数据量小（< 100万） | HNSW | 性能差异不明显 |
| 数据量大（> 1000万） | HNSW | 查询性能优势明显 |

---

## 4. 相似度搜索

### 4.1 相似度操作符

```sql
-- 余弦相似度（最常用）
SELECT * FROM items
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;

-- 内积相似度
SELECT * FROM items
ORDER BY embedding <#> '[0.1, 0.2, ...]'::vector
LIMIT 10;

-- 欧氏距离
SELECT * FROM items
ORDER BY embedding <-> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

### 4.2 相似度阈值查询

```sql
-- 查找相似度大于阈值的记录
SELECT * FROM items
WHERE embedding <=> '[0.1, 0.2, ...]'::vector < 0.3
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

### 4.3 混合查询

```sql
-- 向量搜索 + 全文搜索
SELECT
    i.*,
    ts_rank(to_tsvector('english', i.name), query) AS text_rank,
    1 - (i.embedding <=> $1::vector) AS vector_similarity
FROM items i,
     to_tsquery('english', 'search term') query
WHERE to_tsvector('english', i.name) @@ query
ORDER BY
    (0.7 * (1 - (i.embedding <=> $1::vector))) +
    (0.3 * ts_rank(to_tsvector('english', i.name), query)) DESC
LIMIT 10;
```

---

## 5. 性能优化

### 5.1 索引参数调优

```sql
-- HNSW 索引优化（大数据量）
CREATE INDEX ON items
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 32,              -- 增加连接数（提高精度，降低速度）
    ef_construction = 200  -- 增加构建范围（提高精度，增加构建时间）
);

-- 查询时设置 ef_search
SET hnsw.ef_search = 100;  -- 增加搜索范围（提高精度，降低速度）
```

### 5.2 批量插入优化

```sql
-- 先插入数据，再创建索引
BEGIN;
-- 插入数据
INSERT INTO items (name, embedding) VALUES ...;
-- 创建索引
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);
COMMIT;
```

### 5.3 查询优化

```sql
-- 使用 LIMIT 限制结果数量
SELECT * FROM items
ORDER BY embedding <=> $1::vector
LIMIT 10;  -- 只返回前 10 个结果

-- 使用 WHERE 子句过滤
SELECT * FROM items
WHERE category = 'electronics'
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

---

## 6. AI 应用集成

### 6.1 OpenAI 集成

```python
import openai
import psycopg2
from pgvector.psycopg2 import register_vector

# 生成嵌入向量
def get_embedding(text):
    response = openai.Embedding.create(
        model="text-embedding-3-small",
        input=text
    )
    return response['data'][0]['embedding']

# 存储向量
conn = psycopg2.connect("...")
register_vector(conn)
cur = conn.cursor()

text = "PostgreSQL is a powerful database"
embedding = get_embedding(text)

cur.execute(
    "INSERT INTO items (name, embedding) VALUES (%s, %s)",
    (text, embedding)
)
conn.commit()
```

### 6.2 语义搜索

```sql
-- 语义搜索函数
CREATE OR REPLACE FUNCTION semantic_search(
    query_text TEXT,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE(id INTEGER, name TEXT, similarity FLOAT)
LANGUAGE plpgsql
AS $$
DECLARE
    query_embedding vector(1536);
BEGIN
    -- 调用外部 API 生成查询向量（实际应用中）
    -- query_embedding := get_embedding(query_text);

    RETURN QUERY
    SELECT
        i.id,
        i.name,
        1 - (i.embedding <=> query_embedding) AS similarity
    FROM items i
    ORDER BY i.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$;
```

### 6.3 RAG 应用

```sql
-- RAG 文档存储
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    metadata JSONB
);

-- RAG 检索
CREATE OR REPLACE FUNCTION rag_retrieve(
    query_embedding vector(1536),
    top_k INTEGER DEFAULT 5
)
RETURNS TABLE(content TEXT, metadata JSONB, similarity FLOAT)
LANGUAGE sql
AS $$
    SELECT
        d.content,
        d.metadata,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM documents d
    ORDER BY d.embedding <=> query_embedding
    LIMIT top_k;
$$;
```

---

## 7. 实际案例

### 7.1 案例：电商推荐系统

```sql
-- 商品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    embedding vector(1536),
    category TEXT
);

CREATE INDEX ON products
USING hnsw (embedding vector_cosine_ops);

-- 推荐相似商品
SELECT
    p2.id,
    p2.name,
    1 - (p2.embedding <=> p1.embedding) AS similarity
FROM products p1
CROSS JOIN products p2
WHERE p1.id = $1
  AND p2.id != p1.id
  AND p2.category = p1.category
ORDER BY p2.embedding <=> p1.embedding
LIMIT 10;
```

### 7.2 案例：图像搜索

```sql
-- 图像表
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    url TEXT,
    embedding vector(512),  -- CLIP 模型
    tags TEXT[]
);

CREATE INDEX ON images
USING hnsw (embedding vector_cosine_ops);

-- 图像相似度搜索
SELECT
    i.url,
    i.tags,
    1 - (i.embedding <=> $1::vector) AS similarity
FROM images i
WHERE 1 - (i.embedding <=> $1::vector) > 0.7
ORDER BY i.embedding <=> $1::vector
LIMIT 20;
```

---

## 📊 总结

pgvector 为 PostgreSQL 提供了强大的向量数据库能力，是构建 AI/ML 应用的重要基础设施。
通过合理使用索引和优化查询，可以实现高效的向量相似度搜索，满足推荐系统、语义搜索、RAG 等应用场景的需求。

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
**文档编号**: 03-03-TREND-01
