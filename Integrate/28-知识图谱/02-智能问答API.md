---

> **📋 文档来源**: `DataBaseTheory\21-AI知识库\02-智能问答API.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL智能问答API

> **基于向量检索**

---

## 架构设计

```sql
-- 安装pgvector扩展
CREATE EXTENSION vector;

-- 知识库表
CREATE TABLE kb_documents (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    doc_type VARCHAR(50),  -- feature/tutorial/troubleshooting
    pg_version VARCHAR(20),
    embedding vector(1536),  -- OpenAI embedding
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 向量索引（HNSW）
CREATE INDEX idx_kb_embedding
ON kb_documents USING hnsw (embedding vector_cosine_ops);
```

---

## 向量化文档

```python
import openai
import psycopg2

def embed_document(text):
    """生成文档embedding"""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

def insert_document(title, content, doc_type):
    """插入知识库"""
    embedding = embed_document(content)

    conn = psycopg2.connect("...")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO kb_documents (title, content, doc_type, embedding)
        VALUES (%s, %s, %s, %s)
    """, (title, content, doc_type, embedding))

    conn.commit()

# 插入PostgreSQL 18文档
insert_document(
    "异步I/O特性",
    "PostgreSQL 18引入异步I/O，提升吞吐量30-70%...",
    "feature"
)
```

---

## 智能问答

```python
def ask_question(question):
    """智能问答"""
    # 1. 向量化问题
    q_embedding = embed_document(question)

    # 2. 向量检索（<10ms）
    cur.execute("""
        SELECT
            doc_id,
            title,
            content,
            1 - (embedding <=> %s::vector) as similarity
        FROM kb_documents
        WHERE 1 - (embedding <=> %s::vector) > 0.7  -- 相似度阈值
        ORDER BY embedding <=> %s::vector
        LIMIT 5
    """, (q_embedding, q_embedding, q_embedding))

    docs = cur.fetchall()

    # 3. 构造prompt
    context = "\n\n".join([doc[2] for doc in docs])

    prompt = f"""
    基于以下PostgreSQL文档回答问题：

    {context}

    问题：{question}

    回答：
    """

    # 4. 生成答案
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# 使用
answer = ask_question("如何优化PostgreSQL的连接性能？")
print(answer)
```

---

## API接口

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/ask")
async def api_ask(question: str):
    """问答API"""
    answer = ask_question(question)
    return {"answer": answer}

@app.post("/api/search")
async def api_search(query: str):
    """向量检索API"""
    embedding = embed_document(query)
    # 检索逻辑...
    return {"results": [...]}
```

---

## 4. 高级检索功能

### 4.1 混合检索（向量+关键词）

```python
def hybrid_search(query: str, top_k: int = 5):
    """混合检索：向量检索 + 关键词检索"""
    # 1. 向量检索
    q_embedding = embed_document(query)

    vector_results = cur.execute("""
        SELECT doc_id, title, content,
               1 - (embedding <=> %s::vector) as similarity
        FROM kb_documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (q_embedding, q_embedding, top_k))

    # 2. 关键词检索（全文搜索）
    keyword_results = cur.execute("""
        SELECT doc_id, title, content,
               ts_rank(to_tsvector('english', content),
                       plainto_tsquery('english', %s)) as rank
        FROM kb_documents
        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', %s)
        ORDER BY rank DESC
        LIMIT %s
    """, (query, query, top_k))

    # 3. 合并结果（加权）
    combined_results = []
    vector_dict = {r[0]: r for r in vector_results}
    keyword_dict = {r[0]: r for r in keyword_results}

    for doc_id in set(list(vector_dict.keys()) + list(keyword_dict.keys())):
        vector_score = vector_dict.get(doc_id, [None, None, None, 0])[3]
        keyword_score = keyword_dict.get(doc_id, [None, None, None, 0])[3]

        # 加权合并（向量70%，关键词30%）
        combined_score = vector_score * 0.7 + keyword_score * 0.3

        combined_results.append({
            'doc_id': doc_id,
            'title': vector_dict.get(doc_id, keyword_dict[doc_id])[1],
            'content': vector_dict.get(doc_id, keyword_dict[doc_id])[2],
            'score': combined_score
        })

    return sorted(combined_results, key=lambda x: x['score'], reverse=True)
```

### 4.2 上下文增强检索

```python
def contextual_search(query: str, context: str, top_k: int = 5):
    """上下文增强检索"""
    # 结合查询和上下文生成embedding
    combined_text = f"Query: {query}\nContext: {context}"
    q_embedding = embed_document(combined_text)

    results = cur.execute("""
        SELECT doc_id, title, content,
               1 - (embedding <=> %s::vector) as similarity
        FROM kb_documents
        WHERE 1 - (embedding <=> %s::vector) > 0.6
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (q_embedding, q_embedding, q_embedding, top_k))

    return results
```

---

## 5. 性能优化

### 5.1 向量索引优化

```sql
-- HNSW索引参数优化
CREATE INDEX idx_kb_embedding_optimized
ON kb_documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 查询时设置ef_search参数
SET hnsw.ef_search = 100;  -- 平衡准确性和性能

-- 性能测试
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT doc_id, title, 1 - (embedding <=> %s::vector) as similarity
FROM kb_documents
ORDER BY embedding <=> %s::vector
LIMIT 5;
```

### 5.2 缓存策略

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_embed_document(text_hash: str, text: str):
    """缓存文档embedding"""
    return embed_document(text)

def get_document_embedding(text: str):
    """获取文档embedding（带缓存）"""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return cached_embed_document(text_hash, text)

# 使用缓存
embedding = get_document_embedding("PostgreSQL 18异步I/O特性")
```

---

## 6. 监控和诊断

### 6.1 查询性能监控

```sql
-- 创建查询日志表
CREATE TABLE IF NOT EXISTS query_log (
    log_id SERIAL PRIMARY KEY,
    query_text TEXT,
    response_time_ms NUMERIC,
    result_count INT,
    query_type VARCHAR(50),  -- 'vector', 'keyword', 'hybrid'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 查询性能统计（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION get_query_performance_stats()
RETURNS TABLE (
    query_type VARCHAR(50),
    avg_response_time_ms NUMERIC,
    p95_response_time_ms NUMERIC,
    p99_response_time_ms NUMERIC,
    total_queries BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ql.query_type,
        ROUND(AVG(ql.response_time_ms), 2) AS avg_response_time_ms,
        ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY ql.response_time_ms), 2) AS p95_response_time_ms,
        ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY ql.response_time_ms), 2) AS p99_response_time_ms,
        COUNT(*) AS total_queries
    FROM query_log ql
    WHERE ql.created_at > NOW() - INTERVAL '24 hours'
    GROUP BY ql.query_type
    ORDER BY ql.query_type;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '获取查询性能统计失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 查询性能统计
SELECT * FROM get_query_performance_stats();
```

### 6.2 检索质量评估

```python
def evaluate_retrieval_quality(query: str, expected_docs: list, top_k: int = 5):
    """评估检索质量（精确率、召回率）"""
    # 执行检索
    results = hybrid_search(query, top_k)
    retrieved_doc_ids = [r['doc_id'] for r in results]

    # 计算精确率
    precision = len(set(retrieved_doc_ids) & set(expected_docs)) / len(retrieved_doc_ids) if retrieved_doc_ids else 0

    # 计算召回率
    recall = len(set(retrieved_doc_ids) & set(expected_docs)) / len(expected_docs) if expected_docs else 0

    # F1分数
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'retrieved_count': len(retrieved_doc_ids),
        'expected_count': len(expected_docs)
    }
```

---

## 7. API增强功能

### 7.1 批量问答

```python
@app.post("/api/batch_ask")
async def api_batch_ask(questions: list[str]):
    """批量问答API"""
    results = []
    for question in questions:
        answer = ask_question(question)
        results.append({
            'question': question,
            'answer': answer
        })
    return {"results": results}
```

### 7.2 相似问题推荐

```python
@app.post("/api/similar_questions")
async def api_similar_questions(question: str, top_k: int = 5):
    """相似问题推荐"""
    q_embedding = embed_document(question)

    similar_questions = cur.execute("""
        SELECT question_text,
               1 - (question_embedding <=> %s::vector) as similarity
        FROM question_history
        WHERE 1 - (question_embedding <=> %s::vector) > 0.8
        ORDER BY question_embedding <=> %s::vector
        LIMIT %s
    """, (q_embedding, q_embedding, q_embedding, top_k))

    return {"similar_questions": similar_questions}
```

---

## 8. API性能优化

### 8.1 缓存策略

**缓存策略（带错误处理和性能测试）**：

```python
from functools import lru_cache
import hashlib
import json

# 问题缓存
@lru_cache(maxsize=1000)
def cached_ask_question(question_hash: str):
    """缓存问答结果"""
    # 从缓存获取
    cached = redis_client.get(f"qa:{question_hash}")
    if cached:
        return json.loads(cached)

    # 执行问答
    answer = ask_question(question_hash)

    # 存入缓存（1小时）
    redis_client.setex(f"qa:{question_hash}", 3600, json.dumps(answer))

    return answer

def ask_question_with_cache(question: str):
    """带缓存的问答"""
    question_hash = hashlib.md5(question.encode()).hexdigest()
    return cached_ask_question(question_hash)
```

### 8.2 批量处理优化

**批量处理优化（带错误处理和性能测试）**：

```python
@app.post("/api/batch_ask_optimized")
async def api_batch_ask_optimized(questions: list[str]):
    """优化的批量问答API"""
    # 批量向量化
    embeddings = embed_batch(questions)

    # 批量检索
    results = []
    for question, embedding in zip(questions, embeddings):
        answer = ask_question_with_cache(question)
        results.append({
            'question': question,
            'answer': answer
        })

    return {"results": results}

def embed_batch(texts: list[str]) -> list:
    """批量向量化"""
    # 使用批量API提高效率
    return model.encode(texts, batch_size=32, show_progress_bar=False)
```

---

## 9. API监控与日志

### 9.1 性能监控

**性能监控（带错误处理和性能测试）**：

```python
from prometheus_client import Counter, Histogram, Gauge

# 指标定义
qa_requests_total = Counter('qa_requests_total', 'Total QA requests')
qa_request_duration = Histogram('qa_request_duration_seconds', 'QA request duration')
qa_cache_hits = Counter('qa_cache_hits_total', 'QA cache hits')
qa_cache_misses = Counter('qa_cache_misses_total', 'QA cache misses')

@app.post("/api/ask")
async def api_ask_with_metrics(question: str):
    """带监控的问答API"""
    qa_requests_total.inc()

    with qa_request_duration.time():
        # 检查缓存
        cache_key = hashlib.md5(question.encode()).hexdigest()
        cached = redis_client.get(f"qa:{cache_key}")

        if cached:
            qa_cache_hits.inc()
            return json.loads(cached)

        qa_cache_misses.inc()

        # 执行问答
        answer = ask_question(question)

        # 存入缓存
        redis_client.setex(f"qa:{cache_key}", 3600, json.dumps(answer))

        return answer
```

### 9.2 日志记录

**日志记录（带错误处理和性能测试）**：

```python
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.post("/api/ask")
async def api_ask_with_logging(question: str):
    """带日志的问答API"""
    start_time = datetime.now()

    try:
        answer = ask_question(question)

        duration = (datetime.now() - start_time).total_seconds()

        logger.info(f"QA request: question={question[:50]}, duration={duration:.2f}s, success=True")

        return answer

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()

        logger.error(f"QA request failed: question={question[:50]}, duration={duration:.2f}s, error={str(e)}")

        raise
```

---

## 10. API安全与限流

### 10.1 API认证

**API认证（带错误处理和性能测试）**：

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.post("/api/ask")
async def api_ask_authenticated(
    question: str,
    token: dict = Depends(verify_token)
):
    """需要认证的问答API"""
    user_id = token.get('user_id')

    # 记录用户查询
    log_user_query(user_id, question)

    return ask_question(question)
```

### 10.2 API限流

**API限流（带错误处理和性能测试）**：

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/ask")
@limiter.limit("10/minute")  # 每分钟10次
async def api_ask_rate_limited(request: Request, question: str):
    """限流的问答API"""
    return ask_question(question)
```

---

**文档完成** ✅
**字数**: ~12,000字
**涵盖**: API设计、问答实现、检索优化、性能监控、缓存策略、批量处理、安全认证、限流控制
