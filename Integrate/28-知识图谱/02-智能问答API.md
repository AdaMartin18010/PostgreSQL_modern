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

**文档完成** ✅
