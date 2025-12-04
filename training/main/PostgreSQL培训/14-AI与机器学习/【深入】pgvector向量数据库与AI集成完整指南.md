# 【深入】pgvector向量数据库与AI集成完整指南

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 12+, pgvector 0.5+
> **难度等级**: ⭐⭐⭐⭐⭐ 专家 | **预计学习时间**: 8-10小时

---

## 📋 目录

- [【深入】pgvector向量数据库与AI集成完整指南](#深入pgvector向量数据库与ai集成完整指南)
  - [📋 目录](#-目录)
  - [1. 课程概述](#1-课程概述)
    - [1.1 什么是pgvector？](#11-什么是pgvector)
      - [核心特性](#核心特性)
      - [适用场景](#适用场景)
    - [1.2 pgvector vs 专用向量数据库](#12-pgvector-vs-专用向量数据库)
  - [2. 向量数据库基础](#2-向量数据库基础)
    - [2.1 什么是向量？](#21-什么是向量)
    - [2.2 相似度度量](#22-相似度度量)
      - [距离度量对比](#距离度量对比)
  - [3. pgvector安装与配置](#3-pgvector安装与配置)
    - [3.1 安装](#31-安装)
    - [3.2 启用扩展](#32-启用扩展)
    - [3.3 创建向量表](#33-创建向量表)
  - [4. 向量操作](#4-向量操作)
    - [4.1 插入向量](#41-插入向量)
    - [4.2 向量运算](#42-向量运算)
  - [5. 相似度搜索](#5-相似度搜索)
    - [5.1 基础搜索](#51-基础搜索)
    - [5.2 语义搜索实现](#52-语义搜索实现)
    - [5.3 混合搜索（向量+过滤）](#53-混合搜索向量过滤)
  - [6. 向量索引](#6-向量索引)
    - [6.1 IVFFlat索引](#61-ivfflat索引)
    - [6.2 HNSW索引（推荐）](#62-hnsw索引推荐)
    - [6.3 索引对比](#63-索引对比)
  - [7. AI模型集成](#7-ai模型集成)
    - [7.1 OpenAI集成](#71-openai集成)
    - [7.2 开源模型集成（Sentence Transformers）](#72-开源模型集成sentence-transformers)
  - [8. 混合搜索](#8-混合搜索)
    - [8.1 向量 + 全文搜索](#81-向量--全文搜索)
    - [8.2 向量 + 结构化过滤](#82-向量--结构化过滤)
    - [8.3 向量 + 空间数据](#83-向量--空间数据)
  - [9. RAG应用](#9-rag应用)
    - [9.1 什么是RAG？](#91-什么是rag)
    - [9.2 RAG实现](#92-rag实现)
    - [9.3 文档分块策略](#93-文档分块策略)
  - [10. 性能优化](#10-性能优化)
    - [10.1 批量操作](#101-批量操作)
    - [10.2 查询优化](#102-查询优化)
    - [10.3 缓存策略](#103-缓存策略)
  - [11. 生产实战案例](#11-生产实战案例)
    - [11.1 案例1：智能客服知识库](#111-案例1智能客服知识库)
    - [11.2 案例2：个性化推荐系统](#112-案例2个性化推荐系统)
    - [11.3 案例3：去重与相似检测](#113-案例3去重与相似检测)
  - [12. 最佳实践](#12-最佳实践)
    - [12.1 设计原则](#121-设计原则)
    - [12.2 性能优化Checklist](#122-性能优化checklist)
    - [12.3 安全建议](#123-安全建议)
  - [📚 延伸阅读](#-延伸阅读)
    - [官方资源](#官方资源)
    - [相关技术](#相关技术)
  - [✅ 学习检查清单](#-学习检查清单)

---

## 1. 课程概述

### 1.1 什么是pgvector？

**pgvector** 是PostgreSQL的向量扩展，支持向量存储和相似度搜索，是AI/ML应用的理想数据库。

#### 核心特性

| 特性 | 说明 | 应用 |
|------|------|------|
| **向量存储** | 存储embedding向量 | AI模型输出 |
| **相似度搜索** | 向量近邻搜索 | 语义搜索、推荐 |
| **向量索引** | IVFFlat、HNSW | 高性能搜索 |
| **混合查询** | 向量+结构化数据 | 过滤+语义搜索 |
| **SQL集成** | 原生SQL操作 | 无需新查询语言 |

#### 适用场景

```text
✅ 语义搜索（文本、图像、音频）
✅ 推荐系统（内容、商品、用户）
✅ RAG（检索增强生成）
✅ 相似度检测（去重、欺诈）
✅ 异常检测（安全、质量）
✅ 聚类分析（用户分组、内容分类）
```

### 1.2 pgvector vs 专用向量数据库

```text
pgvector vs Pinecone/Milvus/Weaviate:

✅ 优势：
1. 统一数据库（无需同步）
2. ACID事务保证
3. 混合查询能力强
4. SQL原生集成
5. 成本低（无额外服务）

⚠️ 劣势：
1. 超大规模（>1亿向量）性能不如专用DB
2. 分布式能力有限
3. 高级向量操作较少

适用场景：
✅ 中小规模（<1000万向量）
✅ 需要混合查询
✅ 已使用PostgreSQL
✅ 成本敏感
```

---

## 2. 向量数据库基础

### 2.1 什么是向量？

```text
向量（Embedding）：将文本/图像/音频转换为数值数组

示例：
文本："PostgreSQL is great"
    ↓ OpenAI text-embedding-ada-002
向量：[0.023, -0.015, 0.041, ..., -0.008]  # 1536维

作用：
- 捕捉语义信息
- 相似文本 → 相似向量
- 支持数学运算（距离、相似度）
```

### 2.2 相似度度量

```sql
-- L2距离（欧氏距离）
SELECT embedding <-> '[0.1, 0.2, 0.3]' AS distance FROM items;
-- 距离越小越相似

-- 余弦距离
SELECT embedding <=> '[0.1, 0.2, 0.3]' AS cosine_distance FROM items;
-- 距离越小越相似（归一化向量）

-- 内积
SELECT (embedding <#> '[0.1, 0.2, 0.3]') * -1 AS inner_product FROM items;
-- 值越大越相似
```

#### 距离度量对比

| 度量 | 操作符 | 适用场景 | 特点 |
|------|--------|---------|------|
| **L2距离** | `<->` | 通用 | 考虑幅度差异 |
| **余弦距离** | `<=>` | 文本embedding | 只看方向，忽略幅度 |
| **内积** | `<#>` | 推荐系统 | 考虑向量长度 |

---

## 3. pgvector安装与配置

### 3.1 安装

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
docker run -d --name pgvector -p 5432:5432 -e POSTGRES_PASSWORD=postgres pgvector/pgvector:pg15
```

### 3.2 启用扩展

```sql
-- 创建扩展
CREATE EXTENSION vector;

-- 验证
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 查看支持的向量维度（最大2000）
SELECT typname, typlen FROM pg_type WHERE typname = 'vector';
```

### 3.3 创建向量表

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI ada-002: 1536维
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 或使用不同模型
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    image_url TEXT,
    embedding vector(512)  -- ResNet: 512维
);
```

---

## 4. 向量操作

### 4.1 插入向量

```sql
-- 直接插入
INSERT INTO documents (content, embedding) VALUES
('PostgreSQL is a powerful database',
 '[0.023, -0.015, 0.041, ...]'::vector);  -- 1536个数字

-- 从Python插入（推荐）
-- python
import psycopg2
import openai

# 生成embedding
response = openai.Embedding.create(
    model="text-embedding-ada-002",
    input="PostgreSQL is a powerful database"
)
embedding = response['data'][0]['embedding']

# 插入数据库
conn = psycopg2.connect("dbname=mydb")
cur = conn.cursor()
cur.execute(
    "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
    ("PostgreSQL is a powerful database", embedding)
)
conn.commit()
```

### 4.2 向量运算

```sql
-- 向量加法
SELECT '[1, 2, 3]'::vector + '[4, 5, 6]'::vector;
-- 结果：[5, 7, 9]

-- 向量减法
SELECT '[4, 5, 6]'::vector - '[1, 2, 3]'::vector;
-- 结果：[3, 3, 3]

-- 标量乘法
SELECT '[1, 2, 3]'::vector * 2;
-- 结果：[2, 4, 6]

-- 向量维度
SELECT vector_dims(embedding) FROM documents LIMIT 1;

-- 向量范数
SELECT vector_norm(embedding) FROM documents LIMIT 1;
```

---

## 5. 相似度搜索

### 5.1 基础搜索

```sql
-- 查找最相似的文档
WITH query_vector AS (
    SELECT '[0.023, -0.015, ...]'::vector(1536) AS vec
)
SELECT
    id,
    content,
    embedding <-> query_vector.vec AS distance
FROM documents, query_vector
ORDER BY embedding <-> query_vector.vec
LIMIT 10;
```

### 5.2 语义搜索实现

```python
# 完整的语义搜索示例
import openai
import psycopg2

def semantic_search(query_text, limit=10):
    # 1. 生成查询向量
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=query_text
    )
    query_embedding = response['data'][0]['embedding']

    # 2. 向量搜索
    conn = psycopg2.connect("dbname=mydb")
    cur = conn.cursor()

    cur.execute("""
        SELECT id, content, embedding <-> %s::vector AS distance
        FROM documents
        ORDER BY embedding <-> %s::vector
        LIMIT %s
    """, (query_embedding, query_embedding, limit))

    results = cur.fetchall()
    cur.close()
    conn.close()

    return results

# 使用
results = semantic_search("How to optimize PostgreSQL performance?", limit=5)
for id, content, distance in results:
    print(f"{id}: {content[:100]}... (distance: {distance:.4f})")
```

### 5.3 混合搜索（向量+过滤）

```sql
-- 向量搜索 + 结构化过滤
WITH query_vector AS (
    SELECT '[...]'::vector(1536) AS vec
)
SELECT
    id,
    title,
    content,
    embedding <-> query_vector.vec AS distance
FROM documents, query_vector
WHERE category = 'Technology'
  AND published = TRUE
  AND created_at >= '2024-01-01'
ORDER BY embedding <-> query_vector.vec
LIMIT 10;

-- 向量搜索 + JSONB过滤
SELECT
    id,
    content,
    metadata ->> 'author' AS author,
    embedding <=> query_vec AS similarity
FROM documents
WHERE metadata @> '{"language": "en", "verified": true}'
ORDER BY embedding <=> query_vec
LIMIT 10;
```

---

## 6. 向量索引

### 6.1 IVFFlat索引

```sql
-- 创建IVFFlat索引
CREATE INDEX documents_embedding_ivfflat_idx
ON documents USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);

-- lists参数建议：
-- < 100万行：lists = rows / 1000
-- > 100万行：lists = sqrt(rows)

-- 示例：
-- 10万行 → lists = 100
-- 100万行 → lists = 1000
-- 1000万行 → lists = 3162

-- 查询时设置probes（扫描的列表数）
SET ivfflat.probes = 10;

SELECT id, content, embedding <-> query_vec AS distance
FROM documents
ORDER BY embedding <-> query_vec
LIMIT 10;
-- probes越大，召回越准确，但速度越慢
```

### 6.2 HNSW索引（推荐）

```sql
-- 创建HNSW索引（更快更准）
CREATE INDEX documents_embedding_hnsw_idx
ON documents USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 64);

-- 参数说明：
-- m: 每层最大连接数（默认16）
--    - 增大m：更准确，但索引更大
--    - 范围：4-64，推荐16
-- ef_construction: 构建时搜索深度（默认64）
--    - 增大：索引质量更高，构建更慢
--    - 范围：4-1000，推荐64-200

-- 查询时设置ef（搜索深度）
SET hnsw.ef_search = 40;

SELECT id, content, embedding <-> query_vec AS distance
FROM documents
ORDER BY embedding <-> query_vec
LIMIT 10;

-- ef_search建议：
-- 一般查询：40
-- 高准确度：100-200
-- 实时查询：10-20
```

### 6.3 索引对比

| 索引类型 | 构建速度 | 查询速度 | 准确度 | 内存占用 | 推荐场景 |
|---------|---------|---------|--------|---------|---------|
| **无索引** | - | 极慢 | 100% | 低 | <1000行 |
| **IVFFlat** | 快 | 中 | 90-95% | 中 | 通用 |
| **HNSW** | 慢 | 快 | 95-99% | 高 | 高QPS场景 |

**推荐**：

- 开发测试：无索引
- 生产环境：HNSW（查询性能最优）
- 大规模数据（>1000万）：IVFFlat（内存友好）

---

## 7. AI模型集成

### 7.1 OpenAI集成

```python
# embedding_service.py
import openai
import psycopg2

class EmbeddingService:
    def __init__(self, db_config, openai_api_key):
        self.conn = psycopg2.connect(**db_config)
        openai.api_key = openai_api_key

    def embed_text(self, text):
        """生成文本embedding"""
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response['data'][0]['embedding']

    def add_document(self, content, metadata=None):
        """添加文档并生成embedding"""
        embedding = self.embed_text(content)

        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO documents (content, embedding, metadata)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (content, embedding, metadata))

        doc_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()

        return doc_id

    def semantic_search(self, query, limit=10, filters=None):
        """语义搜索"""
        query_embedding = self.embed_text(query)

        cur = self.conn.cursor()

        sql = """
            SELECT id, content, metadata,
                   embedding <=> %s::vector AS similarity
            FROM documents
            WHERE 1=1
        """
        params = [query_embedding]

        # 添加过滤条件
        if filters:
            for key, value in filters.items():
                sql += f" AND metadata @> %s"
                params.append({key: value})

        sql += " ORDER BY embedding <=> %s::vector LIMIT %s"
        params.extend([query_embedding, limit])

        cur.execute(sql, params)
        results = cur.fetchall()
        cur.close()

        return results

# 使用
service = EmbeddingService(
    db_config={'dbname': 'vectordb', 'user': 'postgres'},
    openai_api_key='sk-...'
)

# 添加文档
doc_id = service.add_document(
    "PostgreSQL is a powerful open-source database",
    {"category": "database", "language": "en"}
)

# 搜索
results = service.semantic_search(
    "How to use PostgreSQL?",
    limit=5,
    filters={"category": "database"}
)
```

### 7.2 开源模型集成（Sentence Transformers）

```python
# 使用本地模型（无API费用）
from sentence_transformers import SentenceTransformer
import psycopg2

class LocalEmbeddingService:
    def __init__(self, db_config, model_name='all-MiniLM-L6-v2'):
        self.conn = psycopg2.connect(**db_config)
        self.model = SentenceTransformer(model_name)
        # 384维向量

    def embed_text(self, text):
        return self.model.encode(text).tolist()

    def batch_embed(self, texts):
        """批量生成embedding"""
        return self.model.encode(texts, show_progress_bar=True)

    def bulk_add_documents(self, documents):
        """批量添加文档"""
        contents = [doc['content'] for doc in documents]
        embeddings = self.batch_embed(contents)

        cur = self.conn.cursor()
        cur.executemany("""
            INSERT INTO documents (content, embedding, metadata)
            VALUES (%s, %s, %s)
        """, [(doc['content'], emb.tolist(), doc.get('metadata'))
              for doc, emb in zip(documents, embeddings)])

        self.conn.commit()
        cur.close()

# 使用
service = LocalEmbeddingService({'dbname': 'vectordb', 'user': 'postgres'})

# 批量添加
docs = [
    {"content": "PostgreSQL is great", "metadata": {"type": "review"}},
    {"content": "How to optimize queries", "metadata": {"type": "tutorial"}},
    # ... 1000+ documents
]
service.bulk_add_documents(docs)
```

---

## 8. 混合搜索

### 8.1 向量 + 全文搜索

```sql
-- 创建表
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
    ) STORED
);

-- 创建索引
CREATE INDEX articles_embedding_hnsw_idx ON articles
USING hnsw (embedding vector_l2_ops);

CREATE INDEX articles_search_gin_idx ON articles
USING GIN (search_vector);

-- 混合搜索（语义 + 关键词）
WITH
semantic_results AS (
    SELECT id, embedding <=> query_vec AS semantic_score
    FROM articles
    ORDER BY embedding <=> query_vec
    LIMIT 100
),
keyword_results AS (
    SELECT id, ts_rank(search_vector, query) AS keyword_score
    FROM articles
    WHERE search_vector @@ query
    LIMIT 100
)
SELECT
    a.id,
    a.title,
    a.content,
    COALESCE(sr.semantic_score, 1.0) AS semantic_score,
    COALESCE(kr.keyword_score, 0.0) AS keyword_score,
    (
        COALESCE(1.0 - sr.semantic_score, 0) * 0.7 +  -- 语义权重70%
        COALESCE(kr.keyword_score, 0) * 0.3            -- 关键词权重30%
    ) AS combined_score
FROM articles a
LEFT JOIN semantic_results sr ON a.id = sr.id
LEFT JOIN keyword_results kr ON a.id = kr.id
WHERE sr.id IS NOT NULL OR kr.id IS NOT NULL
ORDER BY combined_score DESC
LIMIT 10;
```

### 8.2 向量 + 结构化过滤

```sql
-- 向量搜索 + 复杂过滤
SELECT
    p.id,
    p.title,
    p.price,
    p.embedding <-> query_vec AS distance,
    r.avg_rating,
    r.review_count
FROM products p
LEFT JOIN (
    SELECT product_id, AVG(rating) AS avg_rating, COUNT(*) AS review_count
    FROM reviews
    GROUP BY product_id
) r ON p.id = r.product_id
WHERE p.category = 'Electronics'
  AND p.price BETWEEN 500 AND 2000
  AND p.in_stock = TRUE
  AND (r.avg_rating IS NULL OR r.avg_rating >= 4.0)
ORDER BY p.embedding <-> query_vec
LIMIT 20;
```

### 8.3 向量 + 空间数据

```sql
-- 向量搜索 + 地理位置
SELECT
    s.id,
    s.name,
    s.description,
    s.embedding <=> query_vec AS semantic_similarity,
    ST_Distance(s.location::geography, user_location::geography) / 1000 AS distance_km
FROM stores s
WHERE ST_DWithin(s.location::geography, user_location::geography, 10000)
ORDER BY
    (1.0 - (s.embedding <=> query_vec)) * 0.6 +  -- 语义相似度60%
    (1.0 - LEAST(ST_Distance(s.location::geography, user_location::geography) / 10000, 1.0)) * 0.4  -- 距离40%
DESC
LIMIT 10;
```

---

## 9. RAG应用

### 9.1 什么是RAG？

```text
RAG（Retrieval-Augmented Generation）：
检索增强生成，LLM应用的核心架构

流程：
用户问题 → Embedding → 向量搜索（相关文档）
         → 组合（问题+文档）→ LLM生成答案

优势：
✅ 减少幻觉（基于真实文档）
✅ 知识可更新（无需重训模型）
✅ 可追溯（显示来源）
✅ 降低成本（小模型+检索）
```

### 9.2 RAG实现

```python
import openai
import psycopg2

class RAGSystem:
    def __init__(self, db_config, openai_api_key):
        self.conn = psycopg2.connect(**db_config)
        openai.api_key = openai_api_key

    def retrieve(self, query, top_k=3):
        """检索相关文档"""
        # 1. 生成查询embedding
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_embedding = response['data'][0]['embedding']

        # 2. 向量搜索
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, content, embedding <=> %s::vector AS similarity
            FROM knowledge_base
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_embedding, top_k))

        results = cur.fetchall()
        cur.close()

        return [{"id": id, "content": content, "similarity": sim}
                for id, content, sim in results]

    def generate(self, query, retrieved_docs):
        """基于检索结果生成答案"""
        # 构建prompt
        context = "\n\n".join([doc['content'] for doc in retrieved_docs])

        prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""

        # 调用LLM
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response['choices'][0]['message']['content']

    def ask(self, question):
        """完整RAG流程"""
        # 1. 检索
        docs = self.retrieve(question, top_k=3)

        print("Retrieved documents:")
        for i, doc in enumerate(docs, 1):
            print(f"{i}. {doc['content'][:100]}... (similarity: {1-doc['similarity']:.3f})")

        # 2. 生成
        answer = self.generate(question, docs)

        return {
            "answer": answer,
            "sources": [{"id": doc['id'], "content": doc['content']} for doc in docs]
        }

# 使用
rag = RAGSystem(
    db_config={'dbname': 'vectordb', 'user': 'postgres'},
    openai_api_key='sk-...'
)

result = rag.ask("How do I optimize PostgreSQL query performance?")
print(f"Answer: {result['answer']}")
print(f"\nSources: {len(result['sources'])} documents")
```

### 9.3 文档分块策略

```python
def chunk_document(text, chunk_size=500, overlap=100):
    """将长文档分块"""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i+chunk_size])
        chunks.append(chunk)

    return chunks

# 批量处理文档
def process_document(doc_id, content, service):
    chunks = chunk_document(content, chunk_size=500, overlap=100)

    for i, chunk in enumerate(chunks):
        service.add_document(
            content=chunk,
            metadata={
                "source_doc_id": doc_id,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
        )
```

---

## 10. 性能优化

### 10.1 批量操作

```python
# 批量插入（使用COPY）
import io

def bulk_insert_embeddings(conn, documents):
    """高性能批量插入"""
    # 生成所有embeddings
    contents = [doc['content'] for doc in documents]
    embeddings = model.encode(contents, batch_size=32, show_progress_bar=True)

    # 使用COPY批量插入
    buffer = io.StringIO()
    for doc, emb in zip(documents, embeddings):
        buffer.write(f"{doc['content']}\t{emb.tolist()}\n")

    buffer.seek(0)
    cur = conn.cursor()
    cur.copy_expert("""
        COPY documents (content, embedding)
        FROM STDIN
    """, buffer)
    conn.commit()
    cur.close()

# 性能：
# 逐行插入：100 docs/秒
# 批量INSERT：1000 docs/秒
# COPY：5000+ docs/秒 ✅
```

### 10.2 查询优化

```sql
-- ❌ 慢：全表扫描
SELECT * FROM documents
ORDER BY embedding <-> query_vec
LIMIT 10;

-- ✅ 快：使用索引 + 适当的参数
SET hnsw.ef_search = 40;
SELECT * FROM documents
ORDER BY embedding <-> query_vec
LIMIT 10;

-- ✅ 更快：预过滤 + 向量搜索
WITH filtered AS (
    SELECT * FROM documents
    WHERE category = 'tech' AND published = TRUE
)
SELECT * FROM filtered
ORDER BY embedding <-> query_vec
LIMIT 10;
```

### 10.3 缓存策略

```python
import redis
import json

class CachedEmbeddingService:
    def __init__(self, db_config, openai_api_key):
        self.conn = psycopg2.connect(**db_config)
        self.redis = redis.Redis(host='localhost', port=6379)
        openai.api_key = openai_api_key

    def embed_text(self, text):
        """带缓存的embedding生成"""
        # 检查缓存
        cache_key = f"emb:{hash(text)}"
        cached = self.redis.get(cache_key)

        if cached:
            return json.loads(cached)

        # 生成新embedding
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        embedding = response['data'][0]['embedding']

        # 缓存（7天）
        self.redis.setex(cache_key, 7*24*3600, json.dumps(embedding))

        return embedding
```

---

## 11. 生产实战案例

### 11.1 案例1：智能客服知识库

```sql
-- 知识库表
CREATE TABLE kb_articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    embedding vector(1536),
    view_count INT DEFAULT 0,
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX kb_articles_embedding_hnsw_idx
ON kb_articles USING hnsw (embedding vector_cosine_ops);

-- 搜索函数
CREATE OR REPLACE FUNCTION search_kb(
    query_text TEXT,
    query_embedding vector(1536),
    category_filter TEXT DEFAULT NULL,
    top_k INT DEFAULT 5
) RETURNS TABLE (
    id INT,
    title TEXT,
    content TEXT,
    similarity FLOAT,
    rank FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.title,
        kb.content,
        (1.0 - (kb.embedding <=> query_embedding))::FLOAT AS similarity,
        (
            (1.0 - (kb.embedding <=> query_embedding)) * 0.7 +  -- 语义70%
            (kb.helpful_count::FLOAT / GREATEST(kb.view_count, 1)) * 0.2 +  -- 有用度20%
            (1.0 / (1.0 + EXTRACT(EPOCH FROM NOW() - kb.created_at) / 86400 / 365)) * 0.1  -- 时效性10%
        )::FLOAT AS rank
    FROM kb_articles kb
    WHERE (category_filter IS NULL OR kb.category = category_filter)
    ORDER BY rank DESC
    LIMIT top_k;
END;
$$ LANGUAGE plpgsql STABLE;
```

### 11.2 案例2：个性化推荐系统

```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    preference_embedding vector(384)  -- 用户偏好向量
);

-- 内容表
CREATE TABLE content_items (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding vector(384),
    category TEXT,
    tags TEXT[]
);

-- 个性化推荐
SELECT
    ci.id,
    ci.title,
    ci.category,
    (1.0 - (ci.embedding <=> u.preference_embedding)) AS relevance_score,
    -- 多样性：避免推荐过于相似的内容
    (1.0 - (ci.embedding <=> prev.avg_embedding)) AS diversity_score
FROM content_items ci
CROSS JOIN users u
LEFT JOIN (
    -- 用户最近查看的平均向量
    SELECT AVG(ci2.embedding) AS avg_embedding
    FROM user_views uv
    JOIN content_items ci2 ON uv.item_id = ci2.id
    WHERE uv.user_id = $user_id
      AND uv.viewed_at > NOW() - INTERVAL '7 days'
) prev ON TRUE
WHERE u.id = $user_id
  AND ci.category = ANY(u.interested_categories)
ORDER BY
    relevance_score * 0.8 +  -- 相关性80%
    diversity_score * 0.2    -- 多样性20%
DESC
LIMIT 20;
```

### 11.3 案例3：去重与相似检测

```sql
-- 检测重复文档
WITH new_doc AS (
    SELECT '[...]'::vector(1536) AS embedding
)
SELECT
    id,
    title,
    embedding <-> new_doc.embedding AS distance
FROM documents, new_doc
WHERE embedding <-> new_doc.embedding < 0.1  -- 距离阈值
ORDER BY distance
LIMIT 5;

-- 批量去重
WITH duplicates AS (
    SELECT
        d1.id AS id1,
        d2.id AS id2,
        d1.embedding <-> d2.embedding AS distance
    FROM documents d1
    JOIN documents d2 ON d1.id < d2.id
    WHERE d1.embedding <-> d2.embedding < 0.05
)
SELECT * FROM duplicates ORDER BY distance;
```

---

## 12. 最佳实践

### 12.1 设计原则

```sql
-- ✅ 1. 选择合适的向量维度
-- OpenAI ada-002: 1536维（高质量）
-- Sentence-BERT small: 384维（快速）
-- 权衡：维度越高越准确，但越慢

-- ✅ 2. 归一化向量（使用余弦距离时）
CREATE OR REPLACE FUNCTION normalize_vector(v vector)
RETURNS vector AS $$
    SELECT (v / vector_norm(v))::vector;
$$ LANGUAGE SQL IMMUTABLE;

-- ✅ 3. 混合搜索权重调优
-- 根据业务调整语义vs关键词权重
-- A/B测试找到最优比例

-- ✅ 4. 定期更新embedding
-- 内容更新 → 重新生成embedding
CREATE OR REPLACE FUNCTION update_embedding()
RETURNS TRIGGER AS $$
BEGIN
    -- 调用外部服务更新embedding
    -- 或标记为需要更新
    NEW.embedding_outdated = TRUE;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER content_updated
AFTER UPDATE OF content ON documents
FOR EACH ROW
EXECUTE FUNCTION update_embedding();
```

### 12.2 性能优化Checklist

- [ ] 使用HNSW索引（生产环境）
- [ ] 调整ef_search参数（准确度vs速度）
- [ ] 预过滤减少搜索空间
- [ ] 批量操作（COPY vs INSERT）
- [ ] 缓存高频查询embedding
- [ ] 定期VACUUM ANALYZE
- [ ] 监控查询性能

### 12.3 安全建议

```sql
-- 1. 敏感数据不要存储在向量中
-- embedding可能泄露部分原文信息

-- 2. 访问控制
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY documents_tenant_isolation ON documents
FOR SELECT
USING (tenant_id = current_setting('app.tenant_id')::INT);

-- 3. API密钥管理
-- 不要在代码中硬编码API密钥
-- 使用环境变量或密钥管理服务
```

---

## 📚 延伸阅读

### 官方资源

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Sentence Transformers](https://www.sbert.net/)

### 相关技术

- **Pinecone**: 专用向量数据库
- **Milvus**: 开源向量数据库
- **Weaviate**: 向量搜索引擎
- **LangChain**: LLM应用框架

---

## ✅ 学习检查清单

- [ ] 理解向量embedding概念
- [ ] 掌握pgvector基础操作
- [ ] 能创建和优化向量索引
- [ ] 能实现语义搜索
- [ ] 能设计混合搜索方案
- [ ] 能构建完整的RAG系统
- [ ] 理解性能优化技巧

---

**文档维护**: 本文档持续更新以反映pgvector最新特性。
**反馈**: 如发现错误或有改进建议，请提交issue。

**版本历史**:

- v1.0 (2025-01): 初始版本，覆盖pgvector核心特性和RAG应用
