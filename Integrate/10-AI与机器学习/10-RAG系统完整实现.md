---

> **📋 文档来源**: `docs\02-AI-ML\10-RAG系统完整实现.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL 18 RAG系统完整实现

## 📑 目录

- [PostgreSQL 18 RAG系统完整实现](#postgresql-18-rag系统完整实现)
  - [📑 目录](#-目录)
  - [1. RAG架构设计](#1-rag架构设计)
  - [2. 数据库Schema](#2-数据库schema)
  - [3. Python实现](#3-python实现)
  - [4. 高级特性](#4-高级特性)
    - [4.1 混合检索（向量+关键词）](#41-混合检索向量关键词)
    - [4.2 重排序（Rerank）](#42-重排序rerank)
  - [5. 性能优化](#5-性能优化)
    - [5.1 缓存策略](#51-缓存策略)
    - [5.2 批量embedding](#52-批量embedding)

## 1. RAG架构设计

```text
┌────────────────────────────────────────────────┐
│         RAG (Retrieval Augmented Generation)   │
├────────────────────────────────────────────────┤
│                                                │
│  用户问题                                       │
│     ↓                                          │
│  [Embedding Model]                             │
│     ↓                                          │
│  问题向量                                       │
│     ↓                                          │
│  [Vector Search] ← PostgreSQL + pgvector       │
│     ↓                                          │
│  相关文档Top-K                                  │
│     ↓                                          │
│  [构建Prompt]                                  │
│  Context + Question                            │
│     ↓                                          │
│  [LLM]                                         │
│     ↓                                          │
│  生成答案                                       │
└────────────────────────────────────────────────┘
```

---

## 2. 数据库Schema

```sql
-- 文档表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'vector'
    ) THEN
        RAISE EXCEPTION 'pgvector扩展未安装，请先安装: CREATE EXTENSION vector;';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
        DROP TABLE documents CASCADE;
        RAISE NOTICE '已删除现有表: documents';
    END IF;

    CREATE TABLE documents (
        doc_id BIGSERIAL PRIMARY KEY,
        source_id VARCHAR(100),
        doc_type VARCHAR(50),
        title TEXT,
        content TEXT,
        metadata JSONB,
        created_at TIMESTAMPTZ DEFAULT now()
    );

    RAISE NOTICE '表创建成功: documents';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表documents已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 文档块表（Chunk，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
        RAISE EXCEPTION '表documents不存在，请先创建';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'document_chunks') THEN
        DROP TABLE document_chunks;
        RAISE NOTICE '已删除现有表: document_chunks';
    END IF;

    CREATE TABLE document_chunks (
        chunk_id BIGSERIAL PRIMARY KEY,
        doc_id BIGINT REFERENCES documents(doc_id) ON DELETE CASCADE,
        chunk_index INT,
        chunk_text TEXT,
        embedding vector(768),
        token_count INT,
        metadata JSONB,
        created_at TIMESTAMPTZ DEFAULT now(),
        UNIQUE (doc_id, chunk_index)
    );

    RAISE NOTICE '表创建成功: document_chunks';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表documents不存在';
    WHEN undefined_type THEN
        RAISE EXCEPTION 'vector类型不存在，请先安装pgvector扩展';
    WHEN duplicate_table THEN
        RAISE WARNING '表document_chunks已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- HNSW索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'document_chunks') THEN
        RAISE EXCEPTION '表document_chunks不存在，请先创建';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'vector'
    ) THEN
        RAISE EXCEPTION 'pgvector扩展未安装，请先安装';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'document_chunks'
        AND indexname = 'idx_chunks_embedding'
    ) THEN
        DROP INDEX idx_chunks_embedding;
        RAISE NOTICE '已删除现有HNSW索引';
    END IF;

    CREATE INDEX idx_chunks_embedding ON document_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

    RAISE NOTICE 'HNSW索引创建成功: idx_chunks_embedding';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表document_chunks不存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION 'hnsw索引方法不存在，请检查pgvector版本（需要0.7+）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建HNSW索引失败: %', SQLERRM;
END $$;

-- 查询日志（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'query_logs') THEN
        DROP TABLE query_logs;
        RAISE NOTICE '已删除现有表: query_logs';
    END IF;

    CREATE TABLE query_logs (
        query_id BIGSERIAL PRIMARY KEY,
        user_id BIGINT,
        question TEXT,
        retrieved_chunks BIGINT[],
        answer TEXT,
        latency_ms FLOAT,
        created_at TIMESTAMPTZ DEFAULT now()
    );

    RAISE NOTICE '表创建成功: query_logs';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表query_logs已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;
```

---

## 3. Python实现

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.vectorstores.pgvector import PGVector
import psycopg2
from psycopg2.extras import RealDictCursor

class RAGSystem:
    """RAG系统"""

    def __init__(self, conn_str: str, openai_api_key: str):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()

        # 初始化组件
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=openai_api_key
        )
        self.llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def index_document(self, doc_id: int, title: str, content: str, metadata: dict = None):
        """索引文档"""

        # 1. 保存文档
        self.cursor.execute("""
            INSERT INTO documents (doc_id, title, content, metadata)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (doc_id) DO UPDATE
            SET title = EXCLUDED.title,
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata;
        """, (doc_id, title, content, metadata or {}))

        # 2. 分块
        chunks = self.text_splitter.split_text(content)

        # 3. 生成embedding
        embeddings = self.embeddings.embed_documents(chunks)

        # 4. 保存chunks
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            self.cursor.execute("""
                INSERT INTO document_chunks
                (doc_id, chunk_index, chunk_text, embedding, token_count)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (doc_id, chunk_index) DO UPDATE
                SET chunk_text = EXCLUDED.chunk_text,
                    embedding = EXCLUDED.embedding;
            """, (doc_id, i, chunk, embedding, len(chunk.split())))

        self.conn.commit()
        print(f"✅ 索引文档{doc_id}: {len(chunks)}个chunks")

    def search(self, question: str, k: int = 5):
        """检索相关文档"""

        # 1. 问题向量化
        question_vec = self.embeddings.embed_query(question)

        # 2. 向量检索
        self.cursor.execute("""
            SELECT
                dc.chunk_id,
                dc.doc_id,
                d.title,
                dc.chunk_text,
                dc.embedding <=> %s::vector AS distance,
                1 - (dc.embedding <=> %s::vector) AS similarity
            FROM document_chunks dc
            JOIN documents d ON dc.doc_id = d.doc_id
            ORDER BY dc.embedding <=> %s::vector
            LIMIT %s;
        """, (question_vec, question_vec, question_vec, k))

        results = self.cursor.fetchall()

        return [
            {
                'chunk_id': r['chunk_id'],
                'doc_id': r['doc_id'],
                'title': r['title'],
                'content': r['chunk_text'],
                'similarity': float(r['similarity'])
            }
            for r in results
        ]

    def generate_answer(self, question: str, k: int = 5):
        """生成答案"""

        import time
        start_time = time.time()

        # 1. 检索
        contexts = self.search(question, k)

        # 2. 构建prompt
        context_text = "\n\n".join([
            f"文档: {ctx['title']}\n内容: {ctx['content']}"
            for ctx in contexts
        ])

        prompt = f"""
基于以下上下文回答问题。如果无法从上下文中找到答案，请说"我不知道"。

上下文:
{context_text}

问题: {question}

回答:
"""

        # 3. LLM生成
        answer = self.llm(prompt)

        latency = (time.time() - start_time) * 1000

        # 4. 记录日志
        self.cursor.execute("""
            INSERT INTO query_logs
            (question, retrieved_chunks, answer, latency_ms)
            VALUES (%s, %s, %s, %s)
            RETURNING query_id;
        """, (
            question,
            [ctx['chunk_id'] for ctx in contexts],
            answer,
            latency
        ))

        query_id = self.cursor.fetchone()['query_id']
        self.conn.commit()

        return {
            'query_id': query_id,
            'question': question,
            'answer': answer.strip(),
            'sources': contexts,
            'latency_ms': latency
        }

    def batch_index_documents(self, documents: list, batch_size: int = 10):
        """批量索引"""

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]

            for doc in batch:
                self.index_document(
                    doc['id'],
                    doc['title'],
                    doc['content'],
                    doc.get('metadata')
                )

            print(f"已索引 {min(i+batch_size, len(documents))}/{len(documents)}")

# 使用
rag = RAGSystem(
    conn_str="postgresql://localhost/ragdb",
    openai_api_key="your-key"
)

# 索引文档
rag.index_document(
    doc_id=1,
    title="PostgreSQL MVCC原理",
    content="多版本并发控制..."
)

# 问答
result = rag.generate_answer("什么是MVCC？")
print(f"答案: {result['answer']}")
print(f"延迟: {result['latency_ms']:.1f}ms")
```

---

## 4. 高级特性

### 4.1 混合检索（向量+关键词）

```sql
-- 添加全文搜索字段
ALTER TABLE document_chunks ADD COLUMN ts_vector tsvector;

UPDATE document_chunks
SET ts_vector = to_tsvector('english', chunk_text);

CREATE INDEX idx_chunks_fulltext ON document_chunks USING gin(ts_vector);

-- 混合检索
WITH vector_results AS (
    SELECT
        chunk_id,
        1 - (embedding <=> query_vec) AS vec_score
    FROM document_chunks
    ORDER BY embedding <=> query_vec
    LIMIT 100
),
text_results AS (
    SELECT
        chunk_id,
        ts_rank(ts_vector, query) AS text_score
    FROM document_chunks
    WHERE ts_vector @@ to_tsquery('postgresql & mvcc')
)
SELECT
    dc.chunk_id,
    dc.chunk_text,
    COALESCE(vr.vec_score, 0) * 0.7 + COALESCE(tr.text_score, 0) * 0.3 AS final_score
FROM document_chunks dc
LEFT JOIN vector_results vr ON dc.chunk_id = vr.chunk_id
LEFT JOIN text_results tr ON dc.chunk_id = tr.chunk_id
WHERE vr.chunk_id IS NOT NULL OR tr.chunk_id IS NOT NULL
ORDER BY final_score DESC
LIMIT 5;
```

### 4.2 重排序（Rerank）

```python
def search_with_rerank(self, question: str, k: int = 5, candidates: int = 20):
    """向量召回+重排序"""

    # 1. 向量召回（快速，召回更多）
    contexts = self.search(question, k=candidates)

    # 2. 计算语义相似度（精确）
    from sentence_transformers import CrossEncoder
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')

    # 重新打分
    pairs = [(question, ctx['content']) for ctx in contexts]
    scores = reranker.predict(pairs)

    # 3. 按新分数排序
    for ctx, score in zip(contexts, scores):
        ctx['rerank_score'] = float(score)

    contexts.sort(key=lambda x: x['rerank_score'], reverse=True)

    return contexts[:k]
```

---

## 5. 性能优化

### 5.1 缓存策略

```python
import redis

class CachedRAG(RAGSystem):
    """带缓存的RAG"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = redis.Redis(host='localhost', decode_responses=True)
        self.cache_ttl = 3600  # 1小时

    def generate_answer(self, question: str, k: int = 5):
        """带缓存的答案生成"""

        # 生成缓存key
        import hashlib
        cache_key = f"rag:answer:{hashlib.md5(question.encode()).hexdigest()}"

        # 检查缓存
        cached = self.redis_client.get(cache_key)
        if cached:
            import json
            return json.loads(cached)

        # 生成答案
        result = super().generate_answer(question, k)

        # 写入缓存
        import json
        self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(result))

        return result
```

### 5.2 批量embedding

```python
def batch_embed_documents(docs: list, batch_size: int = 100):
    """批量生成embedding"""

    all_embeddings = []

    for i in range(0, len(docs), batch_size):
        batch = docs[i:i+batch_size]

        # 批量调用embedding API
        embeddings = embeddings_model.embed_documents(batch)
        all_embeddings.extend(embeddings)

        print(f"已处理 {min(i+batch_size, len(docs))}/{len(docs)}")

    return all_embeddings

# 性能: 单个调用100次 vs 批量调用1次
# 时间: 50秒 vs 5秒 (-90%)
```

---

**完成**: PostgreSQL 18 RAG系统完整实现
**字数**: ~8,000字
**涵盖**: 架构、Schema、Python实现、混合检索、重排序、缓存优化
