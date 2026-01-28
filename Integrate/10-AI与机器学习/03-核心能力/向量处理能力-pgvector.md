---
> **📋 文档来源**: `PostgreSQL_AI\01-核心基础\向量处理能力-pgvector.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 向量处理能力 - pgvector

> **文档编号**: AI-03-01
> **最后更新**: 2025年1月
> **主题**: 01-核心基础
> **子主题**: 01-向量处理能力

## 📑 目录

- [向量处理能力 - pgvector](#向量处理能力---pgvector)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 pgvector能力思维导图](#11-pgvector能力思维导图)
    - [1.2 核心特性与价值](#12-核心特性与价值)
  - [2. 技术架构](#2-技术架构)
    - [2.1 pgvector架构图](#21-pgvector架构图)
    - [2.2 索引选择决策树](#22-索引选择决策树)
    - [2.3 向量数据类型](#23-向量数据类型)
    - [2.4 相似性搜索操作符](#24-相似性搜索操作符)
    - [2.5 向量索引](#25-向量索引)
  - [3. 安装与使用](#3-安装与使用)
    - [3.1 安装与配置](#31-安装与配置)
    - [3.2 基础操作](#32-基础操作)
    - [3.3 相似度搜索](#33-相似度搜索)
  - [4. 性能优化](#4-性能优化)
    - [4.1 性能基准（参考数据）](#41-性能基准参考数据)
    - [4.2 性能优化建议](#42-性能优化建议)
    - [4.3 大规模部署优化](#43-大规模部署优化)
  - [5. 应用场景](#5-应用场景)
    - [5.1 RAG应用场景](#51-rag应用场景)
    - [5.2 推荐系统场景](#52-推荐系统场景)
    - [5.3 混合搜索场景](#53-混合搜索场景)
  - [6. 最佳实践与常见问题](#6-最佳实践与常见问题)
    - [6.1 最佳实践](#61-最佳实践)
    - [6.2 常见问题](#62-常见问题)

---

## 1. 概述

### 1.1 pgvector能力思维导图

```mermaid
mindmap
  root((pgvector向量处理能力))
    核心功能
      向量存储
        支持最大2000维
        原生数据类型
        高效存储
      相似度搜索
        L2距离
        余弦距离
        内积
      向量索引
        IVFFlat
        HNSW
    应用场景
      RAG系统
        知识库检索
        文档问答
      推荐系统
        内容推荐
        用户推荐
      语义搜索
        文本搜索
        图像搜索
    性能优化
      索引优化
        参数调优
        索引选择
      查询优化
        批量操作
        缓存策略
      混合查询
        向量+SQL
        向量+全文
```

### 1.2 核心特性与价值

**pgvector**是PostgreSQL的向量扩展，为AI/ML应用提供强大的向量存储和相似度搜索能力。

**核心特性**：

| 特性 | 说明 | 应用价值 |
|------|------|----------|
| **向量存储** | 原生`vector`数据类型，支持最大2000维 | 存储AI模型生成的embedding向量 |
| **相似度搜索** | 支持L2、余弦、内积三种距离度量 | 实现语义搜索、推荐系统 |
| **高性能索引** | IVFFlat和HNSW两种索引算法 | 支持大规模向量快速检索 |
| **SQL原生集成** | 完全集成PostgreSQL SQL语法 | 无需学习新查询语言 |
| **混合查询** | 向量搜索+结构化过滤+全文搜索 | 实现复杂业务查询需求 |
| **ACID保证** | 完整的事务支持 | 数据一致性和可靠性 |

**适用场景**：

- ✅ **RAG系统**：知识库检索、文档问答
- ✅ **推荐系统**：内容推荐、用户推荐、商品推荐
- ✅ **语义搜索**：文本搜索、图像搜索、音频搜索
- ✅ **相似度检测**：内容去重、欺诈检测
- ✅ **异常检测**：安全监控、质量检测
- ✅ **聚类分析**：用户分组、内容分类

**核心价值**：

1. **统一数据平台**：向量数据与结构化数据统一存储，无需数据同步
2. **强一致性**：ACID事务保证，数据一致性可靠
3. **混合查询能力**：向量搜索+SQL过滤+全文搜索，满足复杂业务需求
4. **成本效益**：无需额外的向量数据库服务，降低TCO
5. **开发效率**：SQL原生集成，降低学习成本

---

## 2. 技术架构

### 2.1 pgvector架构图

```mermaid
graph TB
    subgraph "应用层"
        App[AI应用<br/>RAG/推荐/搜索]
    end

    subgraph "PostgreSQL核心"
        Core[PostgreSQL Core<br/>ACID + SQL + MVCC]
        Vector[pgvector扩展<br/>向量数据类型]
        Index[向量索引<br/>IVFFlat/HNSW]
    end

    subgraph "存储层"
        Data[(向量数据<br/>vector类型)]
        Meta[(元数据<br/>结构化数据)]
    end

    subgraph "查询层"
        Query[SQL查询引擎]
        Op[向量操作符<br/><-> <=> <#>]
    end

    App --> Core
    Core --> Vector
    Vector --> Index
    Index --> Data
    Core --> Meta
    Query --> Op
    Op --> Vector

    style Vector fill:#4a90e2,color:#fff
    style Index fill:#50c878,color:#fff
```

**架构特点**：

1. **原生集成**：pgvector作为PostgreSQL扩展，完全集成到数据库内核
2. **统一存储**：向量数据和元数据统一存储，支持JOIN操作
3. **索引优化**：支持IVFFlat和HNSW两种高性能索引算法
4. **查询优化**：向量操作符集成到PostgreSQL查询优化器

### 2.2 索引选择决策树

```mermaid
flowchart TD
    A[需要向量索引?] --> B{向量规模?}
    B -->|>1000万| C[IVFFlat索引<br/>适合大规模]
    B -->|<1000万| D{查询延迟要求?}
    D -->|P95<10ms| E[HNSW索引<br/>高性能]
    D -->|P95>10ms| F[IVFFlat索引<br/>平衡性能]
    E --> G{召回率要求?}
    G -->|>0.95| H[HNSW m=16<br/>ef_construction=64]
    G -->|<0.95| I[HNSW m=8<br/>ef_construction=32]
    C --> J[IVFFlat lists=100<br/>适合大规模]

    style E fill:#50c878,color:#fff
    style H fill:#50c878,color:#fff
```

**索引选择指南**：

| 场景 | 推荐索引 | 参数配置 | 性能指标 |
|------|---------|---------|----------|
| **小规模（<100万）** | HNSW | m=16, ef_construction=64 | QPS>10K, P95<5ms |
| **中等规模（100万-1000万）** | HNSW | m=16, ef_construction=64 | QPS>5K, P95<10ms |
| **大规模（>1000万）** | IVFFlat | lists=100 | QPS>2K, P95<20ms |
| **超高召回率（>0.98）** | HNSW | m=32, ef_construction=128 | 召回率>0.98 |
| **写入频繁** | IVFFlat | lists=50 | 写入性能更好 |

### 2.3 向量数据类型

**vector类型定义**：

```sql
-- 创建向量列（固定维度）
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536)  -- OpenAI embedding维度
);

-- 创建向量列（可变维度，不推荐）
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    embedding vector  -- 不指定维度，性能较差
);
```

**向量维度限制**：

- **最大维度**：2000维
- **推荐维度**：128-1536维（常见AI模型输出）
- **性能影响**：维度越高，存储和计算成本越高

**向量存储**：

```sql
-- 插入向量数据
INSERT INTO documents (content, embedding)
VALUES (
    'PostgreSQL is great',
    '[0.023, -0.015, 0.041, ..., -0.008]'::vector
);

-- 从数组创建向量
INSERT INTO documents (content, embedding)
VALUES (
    'Another document',
    ARRAY[0.1, 0.2, 0.3, ...]::vector(1536)
);
```

### 2.4 相似性搜索操作符

pgvector支持三种距离度量操作符：

**1. L2距离（欧氏距离）** - `<->`

```sql
-- L2距离查询（距离越小越相似）
SELECT id, content,
       embedding <-> '[0.1, 0.2, 0.3]'::vector AS distance
FROM documents
ORDER BY embedding <-> '[0.1, 0.2, 0.3]'::vector
LIMIT 10;
```

**适用场景**：

- 通用向量相似度搜索
- 考虑向量幅度的场景
- 数值特征向量

**2. 余弦距离** - `<=>`

```sql
-- 余弦距离查询（距离越小越相似）
SELECT id, content,
       1 - (embedding <=> '[0.1, 0.2, 0.3]'::vector) AS similarity
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, 0.3]'::vector
LIMIT 10;
```

**适用场景**：

- 文本embedding（OpenAI、Sentence Transformers）
- 只关注向量方向，忽略幅度
- 归一化向量

**3. 内积** - `<#>`

```sql
-- 内积查询（值越大越相似）
SELECT id, content,
       (embedding <#> '[0.1, 0.2, 0.3]'::vector) * -1 AS inner_product
FROM documents
ORDER BY embedding <#> '[0.1, 0.2, 0.3]'::vector
LIMIT 10;
```

**适用场景**：

- 推荐系统
- 考虑向量长度的场景
- 非归一化向量

**操作符对比**：

| 操作符 | 名称 | 适用场景 | 性能 | 召回率 |
|--------|------|---------|------|--------|
| `<->` | L2距离 | 通用 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| `<=>` | 余弦距离 | 文本embedding | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| `<#>` | 内积 | 推荐系统 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 2.5 向量索引

**1. IVFFlat索引**

IVFFlat（Inverted File with Flat Compression）适合大规模向量数据。

```sql
-- 创建IVFFlat索引
CREATE INDEX ON documents
USING ivfflat(embedding vector_cosine_ops)
WITH (lists = 100);
```

**参数说明**：

- `lists`：聚类中心数量，推荐值为 `rows / 1000` 到 `rows / 10000`
- 索引大小：约为向量数据的1-2倍
- 构建时间：中等（需要先有数据）

**适用场景**：

- 大规模向量数据（>1000万）
- 写入频繁的场景
- 对召回率要求不高的场景（0.85-0.95）

**2. HNSW索引（推荐）**

HNSW（Hierarchical Navigable Small World）提供高性能向量搜索。

```sql
-- 创建HNSW索引
CREATE INDEX ON documents
USING hnsw(embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**参数说明**：

- `m`：每个节点的最大连接数（4-64），默认16
  - 值越大：索引更大，查询更快，构建更慢
  - 推荐值：16（平衡性能）
- `ef_construction`：构建时的搜索范围（4-1000），默认64
  - 值越大：索引质量更高，构建更慢
  - 推荐值：64（平衡质量）

**适用场景**：

- 中小规模向量数据（<1000万）
- 高召回率要求（>0.95）
- 查询延迟敏感的场景

**索引对比**：

| 特性 | IVFFlat | HNSW |
|------|---------|------|
| **构建速度** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **查询速度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **召回率** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **索引大小** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **写入性能** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **适用规模** | >1000万 | <1000万 |

---

## 3. 安装与使用

### 3.1 安装与配置

**安装方式**：

```bash
# Ubuntu/Debian
sudo apt install postgresql-15-pgvector

# 从源码编译
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Docker
docker pull pgvector/pgvector:pg15
docker run -d --name pgvector -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  pgvector/pgvector:pg15
```

**启用扩展**：

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证安装
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 查看版本
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

### 3.2 基础操作

**创建向量表**：

```sql
-- 创建文档表（RAG场景）
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI embedding维度
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建商品表（推荐系统场景）
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    embedding vector(768),  -- 商品特征向量
    category_id INT,
    price DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**插入向量数据**：

```sql
-- 方式1：直接插入向量数组
INSERT INTO documents (content, embedding)
VALUES (
    'PostgreSQL is a powerful database',
    ARRAY[0.023, -0.015, 0.041, ...]::vector(1536)
);

-- 方式2：从Python应用插入
-- Python代码示例
import psycopg2
import numpy as np

conn = psycopg2.connect("postgresql://user:pass@localhost/db")
cur = conn.cursor()

embedding = np.array([0.023, -0.015, 0.041, ...])  # 1536维向量
cur.execute(
    "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
    ("PostgreSQL is great", embedding.tolist())
)
conn.commit()
```

### 3.3 相似度搜索

**基础相似度搜索**：

```sql
-- 1. 准备查询向量
WITH query_vector AS (
    SELECT '[0.1, 0.2, 0.3, ...]'::vector(1536) AS vec
)
-- 2. 执行相似度搜索
SELECT
    id,
    content,
    1 - (embedding <=> query_vector.vec) AS similarity
FROM documents, query_vector
ORDER BY embedding <=> query_vector.vec
LIMIT 10;
```

**带阈值的相似度搜索**：

```sql
-- 只返回相似度>0.8的结果
SELECT
    id,
    content,
    1 - (embedding <=> query_vec) AS similarity
FROM documents
WHERE 1 - (embedding <=> query_vec) > 0.8
ORDER BY embedding <=> query_vec
LIMIT 10;
```

**混合查询（向量+结构化过滤）**：

```sql
-- 向量搜索 + SQL过滤
SELECT
    id,
    content,
    1 - (embedding <=> query_vec) AS similarity
FROM documents
WHERE
    category_id = 1  -- 结构化过滤
    AND created_at > NOW() - INTERVAL '30 days'  -- 时间过滤
    AND 1 - (embedding <=> query_vec) > 0.7  -- 相似度阈值
ORDER BY embedding <=> query_vec
LIMIT 10;
```

**混合查询（向量+全文搜索）**：

```sql
-- 向量搜索 + 全文搜索
SELECT
    id,
    content,
    1 - (embedding <=> query_vec) AS vector_similarity,
    ts_rank(to_tsvector('english', content), query_ts) AS text_rank
FROM documents,
     plainto_tsquery('english', 'PostgreSQL database') AS query_ts
WHERE
    to_tsvector('english', content) @@ query_ts  -- 全文搜索过滤
    AND 1 - (embedding <=> query_vec) > 0.7  -- 向量相似度过滤
ORDER BY
    (vector_similarity * 0.7 + text_rank * 0.3) DESC  -- 加权排序
LIMIT 10;
```

---

## 4. 性能优化

### 4.1 性能基准（参考数据）

**HNSW索引性能**：

| 向量规模 | 维度 | QPS | P50延迟 | P95延迟 | P99延迟 | 召回率 |
|---------|------|-----|---------|---------|---------|--------|
| 10万 | 768 | 15,000 | 2ms | 5ms | 8ms | >0.98 |
| 100万 | 768 | 8,000 | 4ms | 10ms | 15ms | >0.95 |
| 1000万 | 768 | 5,000 | 6ms | 15ms | 25ms | >0.92 |
| 1亿 | 768 | 2,000 | 10ms | 25ms | 40ms | >0.85 |

**IVFFlat索引性能**：

| 向量规模 | 维度 | QPS | P50延迟 | P95延迟 | P99延迟 | 召回率 |
|---------|------|-----|---------|---------|---------|--------|
| 100万 | 768 | 5,000 | 5ms | 12ms | 20ms | >0.90 |
| 1000万 | 768 | 3,000 | 8ms | 20ms | 35ms | >0.85 |
| 1亿 | 768 | 2,000 | 12ms | 30ms | 50ms | >0.80 |

**实际案例性能**：

- **Qunar途家**：pgvector实现"以图搜房"
  - 召回率提升30%
  - 延迟从120ms降至45ms
  - QPS达到5,000+

### 4.2 性能优化建议

**1. 索引参数调优**：

```sql
-- HNSW索引优化（高召回率场景）
CREATE INDEX ON documents
USING hnsw(embedding vector_cosine_ops)
WITH (
    m = 32,              -- 增加连接数，提升查询性能
    ef_construction = 128  -- 增加构建范围，提升索引质量
);

-- HNSW索引优化（平衡性能场景）
CREATE INDEX ON documents
USING hnsw(embedding vector_cosine_ops)
WITH (
    m = 16,              -- 默认值，平衡性能
    ef_construction = 64  -- 默认值，平衡质量
);
```

**2. 查询时ef_search参数**：

```sql
-- 设置查询时的搜索范围（提升召回率）
SET hnsw.ef_search = 100;  -- 默认40，增加可提升召回率但降低性能

-- 执行查询
SELECT id, content, embedding <=> query_vec AS distance
FROM documents
ORDER BY embedding <=> query_vec
LIMIT 10;
```

**3. 批量操作优化**：

```sql
-- 批量插入向量数据（使用COPY）
COPY documents (content, embedding)
FROM '/path/to/data.csv'
WITH (FORMAT csv);

-- 批量更新向量（使用事务）
BEGIN;
UPDATE documents SET embedding = new_vec WHERE id = 1;
UPDATE documents SET embedding = new_vec WHERE id = 2;
-- ... 更多更新
COMMIT;
```

**4. 查询优化**：

```sql
-- 使用LIMIT减少结果集
SELECT id, content, embedding <=> query_vec AS distance
FROM documents
ORDER BY embedding <=> query_vec
LIMIT 10;  -- 只返回Top 10

-- 使用阈值提前过滤
SELECT id, content, embedding <=> query_vec AS distance
FROM documents
WHERE embedding <=> query_vec < 0.3  -- 提前过滤
ORDER BY embedding <=> query_vec
LIMIT 10;
```

### 4.3 大规模部署优化

**1. 分区表策略**：

```sql
-- 按时间分区（时序向量数据）
CREATE TABLE documents (
    id SERIAL,
    content TEXT,
    embedding vector(1536),
    created_at TIMESTAMPTZ
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE documents_2024_01 PARTITION OF documents
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE documents_2024_02 PARTITION OF documents
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 每个分区创建独立索引
CREATE INDEX ON documents_2024_01 USING hnsw(embedding vector_cosine_ops);
CREATE INDEX ON documents_2024_02 USING hnsw(embedding vector_cosine_ops);
```

**2. 读写分离**：

```sql
-- 主库：写入和索引构建
-- 从库：查询（使用逻辑复制同步）

-- 在从库上创建索引（不影响主库性能）
CREATE INDEX CONCURRENTLY ON documents
USING hnsw(embedding vector_cosine_ops);
```

**3. 缓存策略**：

```sql
-- PostgreSQL内置缓存（自动）
-- 调整shared_buffers参数
ALTER SYSTEM SET shared_buffers = '8GB';

-- 应用层缓存（Redis）
-- 缓存热门查询结果
```

---

## 5. 应用场景

### 5.1 RAG应用场景

**RAG（Retrieval-Augmented Generation）系统架构**：

```sql
-- 1. 知识库表结构
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    chunk_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    source TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 创建索引
CREATE INDEX ON knowledge_base
USING hnsw(embedding vector_cosine_ops);

-- 3. RAG检索查询
WITH query_embedding AS (
    SELECT ai.embedding('text-embedding-3-small', '用户问题') AS vec
)
SELECT
    kb.id,
    kb.content,
    kb.source,
    1 - (kb.embedding <=> qe.vec) AS similarity
FROM knowledge_base kb, query_embedding qe
WHERE 1 - (kb.embedding <=> qe.vec) > 0.7
ORDER BY kb.embedding <=> qe.vec
LIMIT 5;
```

**LangChain集成**：

```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings

# 创建向量存储
vectorstore = PGVector(
    embeddings=OpenAIEmbeddings(),
    collection_name="knowledge_base",
    connection_string="postgresql://user:pass@localhost/db"
)

# 检索
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.7, "k": 5}
)
docs = retriever.get_relevant_documents("用户问题")
```

### 5.2 推荐系统场景

**商品推荐系统**：

```sql
-- 1. 用户行为向量表
CREATE TABLE user_behaviors (
    user_id INT,
    item_id INT,
    behavior_vec vector(768),  -- 用户行为特征向量
    timestamp TIMESTAMPTZ
);

-- 2. 商品特征向量表
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name TEXT,
    category_id INT,
    feature_vec vector(768),  -- 商品特征向量
    price DECIMAL(10, 2)
);

-- 3. 创建索引
CREATE INDEX ON items USING hnsw(feature_vec vector_cosine_ops);

-- 4. 推荐查询（基于用户历史行为）
WITH user_profile AS (
    SELECT AVG(behavior_vec) AS profile_vec
    FROM user_behaviors
    WHERE user_id = 123
      AND timestamp > NOW() - INTERVAL '30 days'
)
SELECT
    i.id,
    i.name,
    i.price,
    1 - (i.feature_vec <=> up.profile_vec) AS similarity
FROM items i, user_profile up
WHERE i.category_id IN (1, 2, 3)  -- 类别过滤
ORDER BY i.feature_vec <=> up.profile_vec
LIMIT 20;
```

### 5.3 混合搜索场景

**向量+全文+结构化混合搜索**：

```sql
-- 综合搜索：向量相似度 + 全文搜索 + 结构化过滤
SELECT
    d.id,
    d.content,
    d.category_id,
    -- 向量相似度
    1 - (d.embedding <=> query_vec) AS vector_score,
    -- 全文搜索相关性
    ts_rank(to_tsvector('english', d.content), query_ts) AS text_score,
    -- 综合得分
    (1 - (d.embedding <=> query_vec)) * 0.6 +
    ts_rank(to_tsvector('english', d.content), query_ts) * 0.4 AS final_score
FROM documents d,
     '[0.1, 0.2, ...]'::vector(1536) AS query_vec,
     plainto_tsquery('english', 'search keywords') AS query_ts
WHERE
    d.category_id = 1  -- 结构化过滤
    AND to_tsvector('english', d.content) @@ query_ts  -- 全文搜索
    AND 1 - (d.embedding <=> query_vec) > 0.6  -- 向量相似度阈值
ORDER BY final_score DESC
LIMIT 10;
```

---

## 6. 最佳实践与常见问题

### 6.1 最佳实践

**1. 索引选择原则**：

- ✅ 中小规模（<1000万）：使用HNSW索引
- ✅ 大规模（>1000万）：使用IVFFlat索引
- ✅ 高召回率要求（>0.95）：使用HNSW索引
- ✅ 写入频繁：使用IVFFlat索引

**2. 向量维度选择**：

- ✅ 使用固定维度：`vector(1536)` 而不是 `vector`
- ✅ 根据AI模型输出选择维度
- ✅ 避免过高的维度（>1536）

**3. 查询优化**：

- ✅ 使用LIMIT限制结果集
- ✅ 设置相似度阈值提前过滤
- ✅ 合理使用混合查询（向量+SQL）

**4. 性能监控**：

```sql
-- 查看索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexname LIKE '%hnsw%' OR indexname LIKE '%ivfflat%';

-- 查看慢查询
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE query LIKE '%<=>%' OR query LIKE '%<->%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### 6.2 常见问题

**Q1: 索引构建很慢怎么办？**

A:

- 使用`CREATE INDEX CONCURRENTLY`后台构建
- 对于HNSW，降低`ef_construction`参数
- 对于IVFFlat，减少`lists`参数

**Q2: 查询召回率低怎么办？**

A:

- 对于HNSW，增加`ef_search`参数
- 对于IVFFlat，增加`lists`参数
- 检查向量是否归一化（使用余弦距离）

**Q3: 向量维度不匹配怎么办？**

A:

- 确保所有向量使用相同维度
- 使用`vector(维度)`明确指定维度
- 检查AI模型输出维度

**Q4: 如何优化大规模向量数据？**

A:

- 使用分区表
- 使用IVFFlat索引
- 考虑读写分离
- 使用批量操作

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**文档编号**: AI-03-01
