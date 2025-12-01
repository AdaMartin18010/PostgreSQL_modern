# RAG系统设计

> **文档编号**: AI-04-01
> **最后更新**: 2025年1月
> **主题**: 04-应用场景
> **子主题**: 01-RAG系统设计

## 📑 目录

- [RAG系统设计](#rag系统设计)
  - [📑 目录](#-目录)
  - [一、概述](#一概述)
  - [二、架构设计](#二架构设计)
    - [2.1 核心架构](#21-核心架构)
    - [2.2 数据流](#22-数据流)
  - [三、数据模型设计](#三数据模型设计)
    - [3.1 知识库表结构](#31-知识库表结构)
    - [3.2 查询历史表](#32-查询历史表)
  - [四、检索策略](#四检索策略)
    - [4.1 基础向量检索](#41-基础向量检索)
    - [4.2 混合检索 (向量 + 关键词)](#42-混合检索-向量--关键词)
    - [4.3 带过滤的检索](#43-带过滤的检索)
  - [五、LLM集成](#五llm集成)
    - [5.1 使用pgai扩展 (SQL内调用)](#51-使用pgai扩展-sql内调用)
    - [5.2 使用LangChain集成](#52-使用langchain集成)
  - [六、性能优化](#六性能优化)
    - [6.1 索引优化](#61-索引优化)
    - [6.2 缓存策略](#62-缓存策略)
    - [6.3 批量处理](#63-批量处理)
  - [七、评估指标](#七评估指标)
    - [7.1 检索质量指标](#71-检索质量指标)
    - [7.2 生成质量指标](#72-生成质量指标)
  - [八、关联主题](#八关联主题)
  - [九、对标资源](#九对标资源)
    - [学术论文](#学术论文)
    - [技术文档](#技术文档)
    - [企业案例](#企业案例)

## 一、概述

RAG (Retrieval-Augmented Generation) 检索增强生成系统，结合向量检索和LLM生成能力，为AI应用提供准确、可追溯的知识问答能力。

## 二、架构设计

### 2.1 核心架构

```mermaid
graph TD
    A[用户查询] --> B[查询向量化]
    B --> C[向量数据库检索]
    C --> D[检索结果排序]
    D --> E[上下文构建]
    E --> F[LLM生成回答]
    F --> G[结果返回]
    G --> H[反馈循环]
    H --> C

    C --> I[PostgreSQL + pgvector]
    I --> J[知识库向量表]
```

### 2.2 数据流

1. **文档处理阶段**:
   - 文档加载 → 文本分块 → Embedding生成 → 向量存储

2. **查询阶段**:
   - 用户查询 → 查询向量化 → 向量检索 → 上下文构建 → LLM生成

3. **反馈阶段**:
   - 用户反馈 → 结果评估 → 检索策略优化

## 三、数据模型设计

### 3.1 知识库表结构

```sql
-- 文档表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_url TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 文档块表 (Chunk)
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_index INTEGER,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI embedding维度
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建向量索引
CREATE INDEX ON document_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 100);

-- 创建文档关联索引
CREATE INDEX ON document_chunks (document_id);
```

### 3.2 查询历史表

```sql
CREATE TABLE query_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    query_text TEXT NOT NULL,
    query_vector vector(1536),
    retrieved_chunks INTEGER[],
    generated_answer TEXT,
    feedback_score INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 四、检索策略

### 4.1 基础向量检索

```sql
-- 简单向量检索
SELECT
    dc.id,
    dc.content,
    dc.metadata,
    dc.embedding <=> :query_vector AS distance
FROM document_chunks dc
WHERE dc.embedding <=> :query_vector < 0.8
ORDER BY dc.embedding <=> :query_vector
LIMIT 10;
```

### 4.2 混合检索 (向量 + 关键词)

```sql
-- 向量检索 + 全文搜索
WITH vector_results AS (
    SELECT
        id, content, metadata,
        embedding <=> :query_vector AS vector_distance
    FROM document_chunks
    WHERE embedding <=> :query_vector < 0.8
    ORDER BY embedding <=> :query_vector
    LIMIT 20
),
text_results AS (
    SELECT
        id, content, metadata,
        ts_rank(content_tsv, plainto_tsquery(:query_text)) AS text_rank
    FROM document_chunks
    WHERE content_tsv @@ plainto_tsquery(:query_text)
    ORDER BY text_rank DESC
    LIMIT 20
)
SELECT DISTINCT
    COALESCE(v.id, t.id) AS id,
    COALESCE(v.content, t.content) AS content,
    COALESCE(v.metadata, t.metadata) AS metadata,
    COALESCE(1 - v.vector_distance, 0) * 0.7 +
    COALESCE(t.text_rank, 0) * 0.3 AS combined_score
FROM vector_results v
FULL OUTER JOIN text_results t ON v.id = t.id
ORDER BY combined_score DESC
LIMIT 10;
```

### 4.3 带过滤的检索

```sql
-- 按部门/权限过滤
SELECT
    dc.id,
    dc.content,
    dc.metadata,
    dc.embedding <=> :query_vector AS distance
FROM document_chunks dc
JOIN documents d ON dc.document_id = d.id
WHERE dc.embedding <=> :query_vector < 0.8
  AND d.metadata->>'department' = :user_department
  AND (d.metadata->>'access_level')::int <= :user_level
ORDER BY dc.embedding <=> :query_vector
LIMIT 10;
```

## 五、LLM集成

### 5.1 使用pgai扩展 (SQL内调用)

```sql
-- 创建RAG查询函数
CREATE OR REPLACE FUNCTION rag_query(
    query_text TEXT,
    top_k INTEGER DEFAULT 5
) RETURNS TEXT AS $$
DECLARE
    query_vector vector(1536);
    context_text TEXT;
    answer TEXT;
BEGIN
    -- 1. 生成查询向量
    query_vector := ai.embedding('text-embedding-3-small', query_text);

    -- 2. 检索相关文档块
    SELECT string_agg(content, E'\n\n')
    INTO context_text
    FROM (
        SELECT content
        FROM document_chunks
        WHERE embedding <=> query_vector < 0.8
        ORDER BY embedding <=> query_vector
        LIMIT top_k
    ) sub;

    -- 3. 调用LLM生成回答
    answer := ai.chat_complete(
        'gpt-4',
        format('基于以下上下文回答问题:\n\n%s\n\n问题: %s',
               context_text, query_text)
    );

    RETURN answer;
END;
$$ LANGUAGE plpgsql;
```

### 5.2 使用LangChain集成

```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

# 初始化向量存储
vectorstore = PGVector(
    embeddings=OpenAIEmbeddings(),
    collection_name="knowledge_base",
    connection_string="postgresql://user:pass@localhost/db"
)

# 创建检索器
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.8, "k": 5}
)

# 创建RAG链
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4"),
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# 查询
result = qa_chain({"query": "PostgreSQL如何实现向量搜索?"})
```

## 六、性能优化

### 6.1 索引优化

```sql
-- 复合索引优化混合查询
CREATE INDEX ON document_chunks
USING btree (document_id, (embedding <=> query_vector))
INCLUDE (content, metadata);

-- 全文搜索索引
CREATE INDEX ON document_chunks
USING gin (content_tsv);
```

### 6.2 缓存策略

```sql
-- 查询结果缓存
CREATE TABLE query_cache (
    query_hash TEXT PRIMARY KEY,
    query_text TEXT,
    query_vector vector(1536),
    result_chunks INTEGER[],
    cached_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- 使用缓存
SELECT result_chunks
FROM query_cache
WHERE query_hash = md5(:query_text)
  AND expires_at > NOW();
```

### 6.3 批量处理

```python
# 批量生成Embedding
def batch_embed_documents(chunks, batch_size=100):
    embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        batch_embeddings = openai.Embedding.create(
            input=batch,
            model="text-embedding-3-small"
        )
        embeddings.extend(batch_embeddings)
    return embeddings
```

## 七、评估指标

### 7.1 检索质量指标

1. **召回率 (Recall)**: 检索到的相关文档比例
2. **精确率 (Precision)**: 检索结果中相关文档比例
3. **MRR (Mean Reciprocal Rank)**: 第一个相关结果的平均排名倒数

### 7.2 生成质量指标

1. **BLEU分数**: 生成文本与参考答案的相似度
2. **ROUGE分数**: 生成文本的摘要质量
3. **人工评估**: 相关性、准确性、流畅性评分

## 八、关联主题

- [向量处理能力 (pgvector)](../03-核心能力/向量处理能力-pgvector.md) - 向量检索实现
- [AI原生调用 (pgai)](../03-核心能力/AI原生调用-pgai.md) - SQL内LLM调用
- [智能客服系统](./智能客服系统.md) - RAG在客服场景的应用

## 九、对标资源

### 学术论文

- **RAG论文**: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (NeurIPS 2020)
- **In-Context RAG**: "In-Context Retrieval-Augmented Language Models" (ACL 2023)

### 技术文档

- [LangChain RAG文档](https://python.langchain.com/docs/use_cases/question_answering/)
- [LlamaIndex RAG文档](https://docs.llamaindex.ai/en/stable/module_guides/deploying/query_engine/root.html)

### 企业案例

- Timescale MarketReader: 自动化新闻Embedding生成
- 开发周期: 3个月 → 2周

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**文档编号**: AI-04-01
