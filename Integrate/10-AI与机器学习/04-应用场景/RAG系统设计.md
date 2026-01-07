---

> **📋 文档来源**: `PostgreSQL_AI\04-应用场景\RAG系统设计.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# RAG系统设计

> **文档编号**: AI-04-01
> **最后更新**: 2025年1月
> **主题**: 04-应用场景
> **子主题**: 01-RAG系统设计

## 📑 目录

- [RAG系统设计](#rag系统设计)
  - [📑 目录](#-目录)
  - [1. RAG系统概述](#1-rag系统概述)
    - [1.1 RAG系统思维导图](#11-rag系统思维导图)
    - [1.2 RAG系统简介](#12-rag系统简介)
  - [2. 系统架构设计](#2-系统架构设计)
    - [2.1 核心架构](#21-核心架构)
    - [2.2 数据流](#22-数据流)
  - [3. 数据库设计](#3-数据库设计)
    - [3.1 知识库表结构](#31-知识库表结构)
    - [3.2 查询历史表](#32-查询历史表)
  - [4. 检索实现](#4-检索实现)
    - [4.1 基础向量检索](#41-基础向量检索)
    - [4.2 混合检索（向量 + 关键词）](#42-混合检索向量--关键词)
    - [4.3 带过滤的检索](#43-带过滤的检索)
  - [5. AI集成](#5-ai集成)
    - [5.1 使用pg\_ai扩展（SQL内调用）](#51-使用pg_ai扩展sql内调用)
    - [5.2 使用LangChain集成](#52-使用langchain集成)
  - [6. 性能优化](#6-性能优化)
    - [6.1 索引优化](#61-索引优化)
    - [6.2 缓存策略](#62-缓存策略)
    - [6.3 批量处理](#63-批量处理)
  - [7. 质量评估](#7-质量评估)
    - [7.1 检索质量指标](#71-检索质量指标)
    - [7.2 生成质量指标](#72-生成质量指标)

---

## 1. RAG系统概述

### 1.1 RAG系统思维导图

```mermaid
mindmap
  root((RAG系统))
    核心组件
      知识库
        文档存储
        向量化
        索引
      检索模块
        向量检索
        全文检索
        混合检索
      生成模块
        LLM调用
        上下文增强
        答案生成
    技术栈
      PostgreSQL
        pgvector
        pg_ai
        JSONB
      RAG框架
        LangChain
        LlamaIndex
    应用场景
      智能问答
      文档检索
      知识库查询
```

### 1.2 RAG系统简介

**RAG（Retrieval-Augmented Generation）检索增强生成**是一种结合信息检索和文本生成的技术，通过检索相关文档来增强LLM的生成能力。

**核心优势**：

- ✅ 提供事实依据，减少幻觉
- ✅ 支持实时知识更新
- ✅ 可追溯信息来源
- ✅ 降低LLM成本（减少上下文长度）

---

## 2. 系统架构设计

### 2.1 核心架构

**RAG系统架构图**：

```mermaid
graph TB
    subgraph "数据层"
        Docs[文档源]
        Docs --> Process[文档处理]
        Process --> Chunk[文档分块]
        Chunk --> Embed[向量化]
        Embed --> Store[(PostgreSQL<br/>pgvector)]
    end

    subgraph "检索层"
        Query[用户查询] --> QEmbed[查询向量化]
        QEmbed --> Retriever[检索器]
        Retriever --> Store
        Retriever --> Filter[过滤与排序]
    end

    subgraph "生成层"
        Filter --> Context[上下文构建]
        Context --> LLM[LLM生成]
        LLM --> Answer[答案输出]
    end

    style Store fill:#4a90e2,color:#fff
    style Retriever fill:#50c878,color:#fff
```

**架构特点**：

- **统一数据平台**：PostgreSQL存储文档和向量
- **混合检索**：向量检索+全文检索
- **SQL原生**：所有操作通过SQL完成

### 2.2 数据流

**RAG系统数据流**：

```text
1. 文档入库流程：
   文档源 → 文档解析 → 文档分块 → 向量化 → PostgreSQL存储

2. 查询流程：
   用户查询 → 查询向量化 → 向量检索 → 文档排序 → 上下文构建 → LLM生成 → 答案返回

3. 反馈流程：
   用户反馈 → 查询优化 → 检索优化 → 模型微调
```

---

## 3. 数据库设计

### 3.1 知识库表结构

**核心表设计**：

```sql
-- 1. 文档主表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,  -- 文档来源
    metadata JSONB,  -- 元数据（作者、日期等）
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 文档分块表（向量存储）
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INT,  -- 块在文档中的位置
    embedding vector(1536),  -- OpenAI embedding
    metadata JSONB,  -- 块级元数据
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 创建向量索引
CREATE INDEX ON document_chunks
USING hnsw(embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 4. 全文搜索索引
CREATE INDEX ON document_chunks
USING GIN(to_tsvector('english', chunk_text));
```

### 3.2 查询历史表

**查询历史记录**：

```sql
-- 查询历史表
CREATE TABLE query_history (
    id SERIAL PRIMARY KEY,
    user_id INT,
    query_text TEXT NOT NULL,
    query_embedding vector(1536),
    retrieved_chunks INT[],  -- 检索到的chunk IDs
    answer TEXT,
    feedback_score INT,  -- 用户反馈分数（1-5）
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 查询历史索引
CREATE INDEX ON query_history (user_id, created_at DESC);
CREATE INDEX ON query_history USING GIN(query_embedding vector_cosine_ops);
```

---

## 4. 检索实现

### 4.1 基础向量检索

**简单向量检索**：

```sql
-- 1. 将用户查询转换为向量
WITH query_vec AS (
    SELECT ai.embedding_openai(
        'text-embedding-3-small',
        'What is PostgreSQL?'
    ) AS vec
)
-- 2. 向量相似度检索
SELECT
    dc.id,
    dc.chunk_text,
    d.title,
    d.source,
    1 - (dc.embedding <=> qv.vec) AS similarity
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id,
     query_vec qv
WHERE 1 - (dc.embedding <=> qv.vec) > 0.7  -- 相似度阈值
ORDER BY dc.embedding <=> qv.vec
LIMIT 5;

-- 性能测试：基础向量检索查询
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH query_vec AS (
    SELECT ai.embedding_openai(
        'text-embedding-3-small',
        'What is PostgreSQL?'
    ) AS vec
)
SELECT
    dc.id,
    dc.chunk_text,
    d.title,
    d.source,
    1 - (dc.embedding <=> qv.vec) AS similarity
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id,
     query_vec qv
WHERE 1 - (dc.embedding <=> qv.vec) > 0.7
ORDER BY dc.embedding <=> qv.vec
LIMIT 5;
```

### 4.2 混合检索（向量 + 关键词）

**向量检索 + 全文搜索**：

```sql
WITH query_vec AS (
    SELECT ai.embedding_openai(
        'text-embedding-3-small',
        'PostgreSQL performance optimization'
    ) AS vec
),
vector_results AS (
    SELECT
        dc.id,
        dc.chunk_text,
        1 - (dc.embedding <=> qv.vec) AS vector_score
    FROM document_chunks dc, query_vec qv
    WHERE 1 - (dc.embedding <=> qv.vec) > 0.7
),
text_results AS (
    SELECT
        dc.id,
        ts_rank(
            to_tsvector('english', dc.chunk_text),
            plainto_tsquery('english', 'PostgreSQL performance optimization')
        ) AS text_score
    FROM document_chunks dc
    WHERE to_tsvector('english', dc.chunk_text)
          @@ plainto_tsquery('english', 'PostgreSQL performance optimization')
)
SELECT
    COALESCE(vr.id, tr.id) AS chunk_id,
    dc.chunk_text,
    COALESCE(vr.vector_score, 0) * 0.6 + COALESCE(tr.text_score, 0) * 0.4 AS final_score
FROM vector_results vr
FULL OUTER JOIN text_results tr ON vr.id = tr.id
JOIN document_chunks dc ON dc.id = COALESCE(vr.id, tr.id)
ORDER BY final_score DESC
LIMIT 5;

-- 性能测试：混合检索查询（向量+关键词）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH query_vec AS (
    SELECT ai.embedding_openai(
        'text-embedding-3-small',
        'PostgreSQL performance optimization'
    ) AS vec
),
vector_results AS (
    SELECT
        dc.id,
        dc.chunk_text,
        1 - (dc.embedding <=> qv.vec) AS vector_score
    FROM document_chunks dc, query_vec qv
    WHERE 1 - (dc.embedding <=> qv.vec) > 0.7
),
text_results AS (
    SELECT
        dc.id,
        ts_rank(
            to_tsvector('english', dc.chunk_text),
            plainto_tsquery('english', 'PostgreSQL performance optimization')
        ) AS text_score
    FROM document_chunks dc
    WHERE to_tsvector('english', dc.chunk_text)
          @@ plainto_tsquery('english', 'PostgreSQL performance optimization')
)
SELECT
    COALESCE(vr.id, tr.id) AS chunk_id,
    dc.chunk_text,
    COALESCE(vr.vector_score, 0) * 0.6 + COALESCE(tr.text_score, 0) * 0.4 AS final_score
FROM vector_results vr
FULL OUTER JOIN text_results tr ON vr.id = tr.id
JOIN document_chunks dc ON dc.id = COALESCE(vr.id, tr.id)
ORDER BY final_score DESC
LIMIT 5;
```

### 4.3 带过滤的检索

**向量检索 + 元数据过滤**：

```sql
WITH query_vec AS (
    SELECT ai.embedding_openai(
        'text-embedding-3-small',
        'How to optimize PostgreSQL queries?'
    ) AS vec
)
SELECT
    dc.id,
    dc.chunk_text,
    d.title,
    d.source,
    1 - (dc.embedding <=> qv.vec) AS similarity
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id,
     query_vec qv
WHERE
    -- 向量相似度过滤
    1 - (dc.embedding <=> qv.vec) > 0.7
    -- 元数据过滤
    AND d.metadata->>'category' = 'performance'
    AND d.created_at > NOW() - INTERVAL '1 year'
ORDER BY dc.embedding <=> qv.vec
LIMIT 5;
```

---

## 5. AI集成

### 5.1 使用pg_ai扩展（SQL内调用）

**自动向量化管道**：

```sql
-- 1. 创建自动向量化器
SELECT ai.create_vectorizer(
    'documents'::regclass,
    destination => 'document_chunks',
    embedding => ai.embedding_openai('text-embedding-3-small', 'content'),
    chunking => ai.chunking_recursive_character_text_splitter(
        'content',
        chunk_size => 500,
        chunk_overlap => 100
    )
);

-- 2. 插入文档，自动分块和向量化
INSERT INTO documents(title, content, source)
VALUES (
    'PostgreSQL Performance Guide',
    'PostgreSQL is a powerful database...',
    'official_docs'
);
-- 自动生成chunks和embeddings

-- 3. SQL内调用LLM生成答案
WITH retrieved_chunks AS (
    SELECT chunk_text
    FROM document_chunks
    WHERE embedding <=> query_vec < 0.3
    ORDER BY embedding <=> query_vec
    LIMIT 3
),
context AS (
    SELECT string_agg(chunk_text, '\n\n') AS text
    FROM retrieved_chunks
)
SELECT ai.chat_complete(
    'gpt-4',
    'Based on the following context, answer the question: ' || user_query || '\n\nContext:\n' || context.text
) AS answer
FROM context;
```

### 5.2 使用LangChain集成

**LangChain RAG实现**：

```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

# 1. 创建向量存储
vectorstore = PGVector(
    embeddings=OpenAIEmbeddings(),
    collection_name="knowledge_base",
    connection_string="postgresql://user:pass@localhost/db"
)

# 2. 创建检索器
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.7, "k": 5}
)

# 3. 创建RAG链
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4"),
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# 4. 查询
result = qa_chain({"query": "What is PostgreSQL?"})
print(result["answer"])
print(result["source_documents"])
```

---

## 6. 性能优化

### 6.1 索引优化

**向量索引优化**：

```sql
-- 1. 使用HNSW索引（高召回率）
CREATE INDEX CONCURRENTLY ON document_chunks
USING hnsw(embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 2. 查询时设置ef_search参数
SET hnsw.ef_search = 100;  -- 提升召回率

-- 3. 复合索引（文档ID + 向量）
CREATE INDEX ON document_chunks (document_id, embedding vector_cosine_ops);
```

### 6.2 缓存策略

**查询结果缓存**：

```sql
-- 1. 创建缓存表
CREATE TABLE query_cache (
    query_hash TEXT PRIMARY KEY,
    query_text TEXT,
    results JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- 2. 缓存查询结果
CREATE OR REPLACE FUNCTION cached_retrieve(query_text TEXT)
RETURNS JSONB AS $$
DECLARE
    query_hash TEXT;
    cached_result JSONB;
BEGIN
    query_hash = md5(query_text);

    -- 检查缓存
    SELECT results INTO cached_result
    FROM query_cache
    WHERE query_hash = cached_retrieve.query_hash
      AND expires_at > NOW();

    IF cached_result IS NOT NULL THEN
        RETURN cached_result;
    END IF;

    -- 执行检索（省略具体实现）
    -- ...

    -- 缓存结果
    INSERT INTO query_cache (query_hash, query_text, results, expires_at)
    VALUES (query_hash, query_text, cached_result, NOW() + INTERVAL '1 hour')
    ON CONFLICT (query_hash) DO UPDATE
    SET results = EXCLUDED.results, expires_at = EXCLUDED.expires_at;

    RETURN cached_result;
END;
$$ LANGUAGE plpgsql;
```

### 6.3 批量处理

**批量文档处理**：

```sql
-- 批量向量化文档
WITH batch AS (
    SELECT id, content
    FROM documents
    WHERE id NOT IN (SELECT DISTINCT document_id FROM document_chunks)
    LIMIT 100
)
SELECT ai.create_vectorizer(
    'documents'::regclass,
    destination => 'document_chunks',
    embedding => ai.embedding_openai('text-embedding-3-small', 'content'),
    chunking => ai.chunking_recursive_character_text_splitter('content')
)
FROM batch;
```

---

## 7. 质量评估

### 7.1 检索质量指标

**检索质量评估**：

```sql
-- 1. 召回率（Recall）
-- 检索到的相关文档数 / 总相关文档数

-- 2. 精确率（Precision）
-- 检索到的相关文档数 / 检索到的总文档数

-- 3. MRR（Mean Reciprocal Rank）
-- 第一个相关文档的倒数排名平均值

-- 4. NDCG（Normalized Discounted Cumulative Gain）
-- 考虑排序位置的累积增益
```

### 7.2 生成质量指标

**生成质量评估**：

- **相关性**：答案与问题的相关程度
- **准确性**：答案的事实准确性
- **完整性**：答案的完整程度
- **流畅性**：答案的语言流畅度

**用户反馈收集**：

```sql
-- 记录用户反馈
INSERT INTO query_history (
    user_id, query_text, answer, feedback_score
)
VALUES (
    123,
    'What is PostgreSQL?',
    'PostgreSQL is a powerful database...',
    5  -- 用户评分1-5
);

-- 分析反馈数据
SELECT
    AVG(feedback_score) AS avg_score,
    COUNT(*) AS total_queries,
    COUNT(*) FILTER (WHERE feedback_score >= 4) AS positive_count
FROM query_history
WHERE created_at > NOW() - INTERVAL '7 days';
```

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**文档编号**: AI-04-01
