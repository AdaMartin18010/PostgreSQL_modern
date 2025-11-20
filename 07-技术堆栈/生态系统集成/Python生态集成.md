# Python 生态集成 PostgreSQL 向量搜索

> **更新时间**: 2025 年 11 月 1 日
> **技术版本**: PostgreSQL 14+, pgvector 0.7.0+, Python 3.8+
> **文档编号**: 07-03-03

## 📑 目录

- [Python 生态集成 PostgreSQL 向量搜索](#python-生态集成-postgresql-向量搜索)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 文档目标](#11-文档目标)
    - [1.2 Python 生态优势](#12-python-生态优势)
    - [1.3 集成价值](#13-集成价值)
  - [2. 核心库](#2-核心库)
    - [2.1 psycopg2 / psycopg3](#21-psycopg2--psycopg3)
      - [2.1.1 安装和配置](#211-安装和配置)
      - [2.1.2 基础使用](#212-基础使用)
      - [2.1.3 向量查询](#213-向量查询)
    - [2.2 SQLAlchemy + pgvector](#22-sqlalchemy--pgvector)
      - [2.2.1 ORM 集成](#221-orm-集成)
      - [2.2.2 模型定义](#222-模型定义)
      - [2.2.3 向量查询](#223-向量查询)
    - [2.3 asyncpg + pgvector](#23-asyncpg--pgvector)
      - [2.3.1 异步驱动](#231-异步驱动)
      - [2.3.2 异步查询](#232-异步查询)
      - [2.3.3 性能优势](#233-性能优势)
  - [3. LangChain 集成](#3-langchain-集成)
    - [3.1 基础集成](#31-基础集成)
    - [3.2 RAG 应用](#32-rag-应用)
    - [3.3 高级特性](#33-高级特性)
  - [4. FastAPI 集成](#4-fastapi-集成)
    - [4.1 REST API 开发](#41-rest-api-开发)
      - [4.1.1 基础 API](#411-基础-api)
      - [4.1.2 向量搜索 API](#412-向量搜索-api)
      - [4.1.3 RAG API](#413-rag-api)
    - [4.2 异步处理](#42-异步处理)
    - [4.3 API 文档](#43-api-文档)
  - [5. Pandas 集成](#5-pandas-集成)
    - [5.1 数据读取](#51-数据读取)
    - [5.2 数据分析](#52-数据分析)
    - [5.3 数据写入](#53-数据写入)
  - [6. NumPy 集成](#6-numpy-集成)
    - [6.1 向量计算](#61-向量计算)
    - [6.2 批量处理](#62-批量处理)
    - [6.3 性能优化](#63-性能优化)
  - [7. 其他生态工具](#7-其他生态工具)
    - [7.1 Django 集成](#71-django-集成)
    - [7.2 Flask 集成](#72-flask-集成)
    - [7.3 Streamlit 集成](#73-streamlit-集成)
  - [8. 最佳实践](#8-最佳实践)
    - [8.1 连接管理](#81-连接管理)
    - [8.2 性能优化](#82-性能优化)
    - [8.3 错误处理](#83-错误处理)
  - [9. 常见问题](#9-常见问题)
    - [9.1 依赖问题](#91-依赖问题)
    - [9.2 连接问题](#92-连接问题)
    - [9.3 性能问题](#93-性能问题)
  - [10. 参考资料](#10-参考资料)
    - [10.1 官方文档](#101-官方文档)
    - [10.2 技术文档](#102-技术文档)
    - [10.3 相关资源](#103-相关资源)

---

## 1. 概述

### 1.1 文档目标

**核心目标**:

本文档提供 PostgreSQL + pgvector 与 Python 生态系统的完整集成指南，帮助开发者快速构建基于向量搜索的
Python 应用。

**文档价值**:

| 价值项       | 说明                     | 影响         |
| ------------ | ------------------------ | ------------ |
| **完整集成** | 覆盖主流 Python 库和框架 | 提高开发效率 |
| **最佳实践** | 提供集成最佳实践         | 减少常见问题 |
| **性能优化** | 提供性能优化建议         | 提高应用性能 |

### 1.2 Python 生态优势

**Python 生态特性**:

| 特性           | 说明               | 优势         |
| -------------- | ------------------ | ------------ |
| **丰富的库**   | 大量成熟的库和框架 | 快速开发     |
| **易用性**     | 简洁的语法和 API   | 降低学习成本 |
| **生态系统**   | 活跃的社区和支持   | 持续更新     |
| **AI/ML 支持** | 强大的 AI/ML 库    | 适合 AI 应用 |

### 1.3 集成价值

**集成优势**:

| 优势         | 说明                           | 影响               |
| ------------ | ------------------------------ | ------------------ |
| **向量搜索** | PostgreSQL + pgvector 向量搜索 | **高性能向量检索** |
| **ORM 支持** | SQLAlchemy、Django ORM 支持    | **简化数据访问**   |
| **异步支持** | asyncpg 异步驱动               | **提高并发性能**   |
| **框架集成** | FastAPI、Flask、Django 集成    | **快速构建应用**   |

## 2. 核心库

### 2.1 psycopg2 / psycopg3

#### 2.1.1 安装和配置

**安装**:

```bash
# psycopg2（稳定版，推荐）
pip install psycopg2-binary

# psycopg3（新版，性能更好）
pip install psycopg[binary]
```

**版本对比**:

| 特性       | psycopg2 | psycopg3     |
| ---------- | -------- | ------------ |
| **稳定性** | 非常稳定 | 新版本       |
| **性能**   | 良好     | **更好**     |
| **API**    | 传统 API | **现代 API** |
| **异步**   | 不支持   | **支持**     |

**连接配置**:

```python
import psycopg2
from psycopg2 import pool

# 连接池配置
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=20,
    host="localhost",
    port=5432,
    user="postgres",
    password="postgres",
    database="vector_db"
)

def get_connection():
    """获取连接"""
    return connection_pool.getconn()

def return_connection(conn):
    """归还连接"""
    connection_pool.putconn(conn)
```

#### 2.1.2 基础使用

**基础使用示例**:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

# 连接
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="postgres",
    database="vector_db"
)

# 创建扩展
with conn.cursor() as cur:
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()

# 创建表
with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            content TEXT,
            embedding vector(1536),
            metadata JSONB
        )
    """)
    conn.commit()

# 插入数据
with conn.cursor() as cur:
    cur.execute("""
        INSERT INTO documents (content, embedding, metadata)
        VALUES (%s, %s::vector, %s)
    """, (content, str(embedding), metadata))
    conn.commit()

conn.close()
```

#### 2.1.3 向量查询

**向量查询示例**:

```python
import psycopg2
import numpy as np

conn = psycopg2.connect(DATABASE_URL)

# 向量查询（余弦距离）
query_vector = np.random.rand(1536).tolist()
query_vector_str = '[' + ','.join(map(str, query_vector)) + ']'

with conn.cursor() as cur:
    cur.execute("""
        SELECT
            id,
            content,
            1 - (embedding <=> %s::vector) as similarity,
            metadata
        FROM documents
        WHERE embedding <=> %s::vector < 0.3
        ORDER BY embedding <=> %s::vector
        LIMIT 10
    """, (query_vector_str, query_vector_str, query_vector_str))

    results = cur.fetchall()
    for row in results:
        print(f"ID: {row[0]}, 相似度: {row[2]:.4f}, 内容: {row[1][:50]}...")

conn.close()
```

**批量查询**:

```python
from psycopg2.extras import execute_values

with conn.cursor() as cur:
    # 批量查询
    queries = [np.random.rand(1536).tolist() for _ in range(10)]
    query_strings = ['[' + ','.join(map(str, q)) + ']' for q in queries]

    # 使用 UNNEST 进行批量查询
    cur.execute("""
        WITH queries AS (
            SELECT unnest(%s::vector[]) as query_vector
        )
        SELECT
            q.query_vector,
            d.id,
            d.content,
            1 - (d.embedding <=> q.query_vector) as similarity
        FROM queries q
        CROSS JOIN LATERAL (
            SELECT * FROM documents
            ORDER BY embedding <=> q.query_vector
            LIMIT 5
        ) d
        ORDER BY q.query_vector, similarity DESC
    """, (query_strings,))

    results = cur.fetchall()
```

### 2.2 SQLAlchemy + pgvector

#### 2.2.1 ORM 集成

**安装依赖**:

```bash
pip install sqlalchemy psycopg2-binary pgvector
```

**基础配置**:

```python
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector

# 创建引擎
engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/vector_db',
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)

# 创建会话工厂
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
```

#### 2.2.2 模型定义

**模型定义示例**:

```python
from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Document(id={self.id}, content={self.content[:50]}...)>"

# 创建表
Base.metadata.create_all(engine)
```

#### 2.2.3 向量查询

**向量查询示例**:

```python
from sqlalchemy.orm import Session
import numpy as np

# 创建会话
session = SessionLocal()

# 插入数据
query_vector = np.random.rand(1536)
doc = Document(
    content="PostgreSQL is a powerful database",
    embedding=query_vector,
    metadata={"category": "database", "author": "PostgreSQL Team"}
)
session.add(doc)
session.commit()

# 向量查询（余弦距离）
query_vector = np.random.rand(1536)
results = session.query(Document).order_by(
    Document.embedding.cosine_distance(query_vector)
).limit(10).all()

# 向量查询（欧氏距离）
results = session.query(Document).order_by(
    Document.embedding.l2_distance(query_vector)
).limit(10).all()

# 向量查询（内积）
results = session.query(Document).order_by(
    Document.embedding.max_inner_product(query_vector)
).limit(10).all()

# 带阈值的查询
from sqlalchemy import func
results = session.query(Document).filter(
    func.cosine_distance(Document.embedding, query_vector) < 0.3
).order_by(
    Document.embedding.cosine_distance(query_vector)
).limit(10).all()

session.close()
```

### 2.3 asyncpg + pgvector

#### 2.3.1 异步驱动

**安装依赖**:

```bash
pip install asyncpg pgvector
```

**异步连接配置**:

```python
import asyncio
import asyncpg
from pgvector.asyncpg import register_vector

# 连接池配置
async def create_pool():
    """创建连接池"""
    pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="vector_db",
        min_size=5,
        max_size=20
    )
    return pool

# 使用连接池
pool = await create_pool()
```

#### 2.3.2 异步查询

**异步查询示例**:

```python
async def search_vectors(pool, query_vector, top_k=10):
    """异步向量搜索"""
    async with pool.acquire() as conn:
        # 注册向量类型
        await register_vector(conn)

        # 查询
        results = await conn.fetch("""
            SELECT
                id,
                content,
                1 - (embedding <=> $1::vector) as similarity,
                metadata
            FROM documents
            WHERE embedding <=> $1::vector < 0.3
            ORDER BY embedding <=> $1::vector
            LIMIT $2
        """, query_vector, top_k)

        return results

# 使用
import numpy as np
query_vector = np.random.rand(1536).tolist()
results = await search_vectors(pool, query_vector, top_k=10)

for row in results:
    print(f"ID: {row['id']}, 相似度: {row['similarity']:.4f}")
```

**批量异步查询**:

```python
async def batch_search_vectors(pool, query_vectors, top_k=10):
    """批量异步向量搜索"""
    async with pool.acquire() as conn:
        await register_vector(conn)

        # 并行查询
        tasks = []
        for query_vector in query_vectors:
            task = conn.fetch("""
                SELECT * FROM documents
                ORDER BY embedding <=> $1::vector
                LIMIT $2
            """, query_vector, top_k)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results

# 使用
query_vectors = [np.random.rand(1536).tolist() for _ in range(10)]
all_results = await batch_search_vectors(pool, query_vectors)
```

#### 2.3.3 性能优势

**性能对比**:

| 驱动         | 并发支持 | 性能     | 适用场景     |
| ------------ | -------- | -------- | ------------ |
| **psycopg2** | 线程级   | 良好     | 同步应用     |
| **asyncpg**  | 协程级   | **更好** | **异步应用** |

**异步性能示例**:

```python
import asyncio
import time

async def async_performance_test():
    """异步性能测试"""
    pool = await create_pool()

    query_vectors = [np.random.rand(1536).tolist() for _ in range(100)]

    start = time.time()
    results = await batch_search_vectors(pool, query_vectors)
    end = time.time()

    print(f"异步查询耗时: {end - start:.2f} 秒")
    print(f"平均每个查询: {(end - start) / len(query_vectors) * 1000:.2f} ms")

    await pool.close()

# 运行
asyncio.run(async_performance_test())
```

## 3. LangChain 集成

### 3.1 基础集成

**基础集成示例**:

```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os

# 初始化嵌入模型
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 创建向量存储
vectorstore = PGVector(
    embeddings=embeddings,
    connection=os.getenv("POSTGRES_URL"),
    collection_name="documents",
    use_jsonb=True,  # PostgreSQL 18 优化
    pre_delete_collection=False,
    distance_strategy="cosine"
)

# 添加文档
documents = [
    Document(page_content="PostgreSQL is a powerful database"),
    Document(page_content="pgvector adds vector search capabilities"),
    Document(page_content="LangChain integrates with PostgreSQL")
]

vectorstore.add_documents(documents)
print("✅ 文档添加成功")
```

### 3.2 RAG 应用

**RAG 应用示例**:

```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# 初始化 LLM
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 创建 RAG 链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

# 提问
result = qa_chain.invoke({"query": "What is PostgreSQL?"})
print(f"回答: {result['result']}")
```

### 3.3 高级特性

**高级特性示例**:

```python
# 带元数据过滤的搜索
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"category": "database"}
    }
)

# 带分数的搜索
results_with_scores = vectorstore.similarity_search_with_score(
    "PostgreSQL",
    k=5
)

for doc, score in results_with_scores:
    similarity = 1 - score  # 转换为相似度
    print(f"[相似度: {similarity:.4f}] {doc.page_content}")
```

## 4. FastAPI 集成

### 4.1 REST API 开发

#### 4.1.1 基础 API

**基础 FastAPI 应用**:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os

app = FastAPI(title="Vector Search API")

# 初始化向量存储
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

vectorstore = PGVector(
    embeddings=embeddings,
    connection=os.getenv("POSTGRES_URL"),
    collection_name="documents"
)
```

#### 4.1.2 向量搜索 API

**向量搜索 API**:

```python
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    filter: dict = None

class DocumentResponse(BaseModel):
    id: int
    content: str
    similarity: float
    metadata: dict = None

@app.post("/api/search", response_model=list[DocumentResponse])
async def search_documents(request: SearchRequest):
    """向量搜索接口"""
    try:
        search_kwargs = {"k": request.top_k}
        if request.filter:
            search_kwargs["filter"] = request.filter

        retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
        results = retriever.get_relevant_documents(request.query)

        return [
            DocumentResponse(
                id=i,
                content=doc.page_content,
                similarity=1.0,  # 可以从 metadata 获取
                metadata=doc.metadata
            )
            for i, doc in enumerate(results)
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 4.1.3 RAG API

**RAG API**:

```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """RAG 聊天接口"""
    try:
        result = qa_chain.invoke({"query": request.query})

        return ChatResponse(
            answer=result['result'],
            sources=[doc.page_content[:100] for doc in result.get('source_documents', [])]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4.2 异步处理

**异步向量存储**:

```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings

@app.post("/api/search/async")
async def async_search_documents(request: SearchRequest):
    """异步向量搜索"""
    try:
        # 异步搜索
        results = await vectorstore.asimilarity_search(
            request.query,
            k=request.top_k
        )

        return [
            DocumentResponse(
                id=i,
                content=doc.page_content,
                similarity=1.0,
                metadata=doc.metadata
            )
            for i, doc in enumerate(results)
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4.3 API 文档

**自动生成 API 文档**:

```bash
# 运行 FastAPI 应用
uvicorn main:app --reload

# 访问 API 文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## 5. Pandas 集成

### 5.1 数据读取

**数据读取示例**:

```python
import pandas as pd
from sqlalchemy import create_engine

# 创建引擎
engine = create_engine('postgresql://postgres:postgres@localhost:5432/vector_db')

# 读取数据
df = pd.read_sql("""
    SELECT
        id,
        content,
        metadata,
        created_at
    FROM documents
    LIMIT 10000
""", engine)

print(f"读取了 {len(df)} 行数据")
print(df.head())
```

**向量数据读取**:

```python
# 读取向量数据（需要转换为列表）
import numpy as np

df = pd.read_sql("""
    SELECT
        id,
        content,
        embedding::text as embedding_text,
        metadata
    FROM documents
    LIMIT 1000
""", engine)

# 转换为 NumPy 数组
df['embedding'] = df['embedding_text'].apply(
    lambda x: np.array(eval(x))
)

# 删除文本列
df = df.drop('embedding_text', axis=1)
```

### 5.2 数据分析

**数据分析示例**:

```python
# 基础统计
print(df.describe())

# 按类别分组分析
if 'metadata' in df.columns:
    df['category'] = df['metadata'].apply(
        lambda x: x.get('category', 'unknown') if isinstance(x, dict) else 'unknown'
    )

    category_stats = df.groupby('category').agg({
        'id': 'count',
        'content': lambda x: x.str.len().mean()  # 平均内容长度
    })
    print(category_stats)

# 向量相似度分析
if 'embedding' in df.columns:
    query_vector = np.random.rand(1536)
    df['distance'] = df['embedding'].apply(
        lambda x: np.linalg.norm(x - query_vector)
    )

    print(f"平均距离: {df['distance'].mean():.4f}")
    print(f"最小距离: {df['distance'].min():.4f}")
    print(f"最大距离: {df['distance'].max():.4f}")
```

### 5.3 数据写入

**数据写入示例**:

```python
# 准备数据
df_new = pd.DataFrame({
    'query': ['PostgreSQL', 'pgvector', 'LangChain'],
    'result_count': [10, 15, 20],
    'avg_similarity': [0.85, 0.90, 0.88],
    'timestamp': pd.Timestamp.now()
})

# 写入数据库
df_new.to_sql(
    'search_stats',
    engine,
    if_exists='append',  # 追加模式
    index=False
)

print(f"✅ 写入 {len(df_new)} 行数据")
```

## 6. NumPy 集成

### 6.1 向量计算

**向量计算示例**:

```python
import numpy as np
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# 从数据库读取向量
cur.execute("SELECT embedding FROM documents LIMIT 1000")
vectors = np.array([np.array(eval(row[0])) for row in cur.fetchall()])

# NumPy 向量运算
query_vector = np.random.rand(1536)

# 余弦相似度
norms = np.linalg.norm(vectors, axis=1)
query_norm = np.linalg.norm(query_vector)
cosine_similarities = np.dot(vectors, query_vector) / (norms * query_norm)

# 欧氏距离
distances = np.linalg.norm(vectors - query_vector, axis=1)

# Top-K 索引
top_k_indices = np.argsort(distances)[:10]

print(f"Top 10 最相似的文档索引: {top_k_indices}")
print(f"相似度分数: {cosine_similarities[top_k_indices]}")
```

### 6.2 批量处理

**批量向量处理**:

```python
# 批量更新向量
new_vectors = np.random.rand(100, 1536)

# 准备更新数据
update_data = [
    (str(v.tolist()), i) for i, v in enumerate(new_vectors)
]

# 批量更新
execute_values(
    cur,
    "UPDATE documents SET embedding = %s::vector WHERE id = %s",
    update_data
)

conn.commit()
```

### 6.3 性能优化

**NumPy 性能优化**:

```python
import time

# 性能对比测试
def numpy_search(vectors, query_vector, top_k=10):
    """NumPy 向量搜索"""
    distances = np.linalg.norm(vectors - query_vector, axis=1)
    top_k_indices = np.argsort(distances)[:top_k]
    return top_k_indices

# 测试
vectors = np.random.rand(10000, 1536)
query_vector = np.random.rand(1536)

start = time.time()
results = numpy_search(vectors, query_vector)
end = time.time()

print(f"NumPy 搜索耗时: {(end - start) * 1000:.2f} ms")
```

## 7. 其他生态工具

### 7.1 Django 集成

**Django 集成示例**:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vector_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# models.py
from django.db import models
from pgvector.django import VectorField

class Document(models.Model):
    content = models.TextField()
    embedding = VectorField(dimensions=1536)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

# 向量查询
query_vector = [0.1] * 1536
results = Document.objects.order_by(
    'embedding__cosine_distance'
).filter(
    embedding__cosine_distance__lt=0.3
)[:10]
```

### 7.2 Flask 集成

**Flask 集成示例**:

```python
from flask import Flask, request, jsonify
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings

app = Flask(__name__)

# 初始化向量存储
vectorstore = PGVector(
    embeddings=OpenAIEmbeddings(),
    connection=os.getenv("POSTGRES_URL"),
    collection_name="documents"
)

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    top_k = data.get('top_k', 5)

    results = vectorstore.similarity_search(query, k=top_k)

    return jsonify([
        {
            'content': doc.page_content,
            'metadata': doc.metadata
        }
        for doc in results
    ])

if __name__ == '__main__':
    app.run(debug=True)
```

### 7.3 Streamlit 集成

**Streamlit 集成示例**:

```python
import streamlit as st
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings

st.title("向量搜索应用")

# 初始化向量存储
@st.cache_resource
def get_vectorstore():
    return PGVector(
        embeddings=OpenAIEmbeddings(),
        connection=os.getenv("POSTGRES_URL"),
        collection_name="documents"
    )

vectorstore = get_vectorstore()

# 搜索界面
query = st.text_input("输入搜索查询")
top_k = st.slider("返回结果数量", 1, 20, 5)

if query:
    results = vectorstore.similarity_search(query, k=top_k)

    for i, doc in enumerate(results, 1):
        st.write(f"### 结果 {i}")
        st.write(doc.page_content)
        if doc.metadata:
            st.write(f"元数据: {doc.metadata}")
```

## 8. 最佳实践

### 8.1 连接管理

**连接池最佳实践**:

```python
from psycopg2 import pool

# 连接池配置
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=20,
    host="localhost",
    port=5432,
    user="postgres",
    password="postgres",
    database="vector_db"
)

# 使用连接池
def with_connection(func):
    """连接装饰器"""
    def wrapper(*args, **kwargs):
        conn = connection_pool.getconn()
        try:
            return func(conn, *args, **kwargs)
        finally:
            connection_pool.putconn(conn)
    return wrapper

@with_connection
def search_documents(conn, query_vector, top_k=10):
    """使用连接池的搜索函数"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (str(query_vector), top_k))
        return cur.fetchall()
```

### 8.2 性能优化

**性能优化建议**:

1. **使用连接池**: 避免频繁创建和关闭连接
2. **批量操作**: 使用批量插入和批量查询
3. **索引优化**: 确保向量索引已创建
4. **异步处理**: 对于高并发场景，使用 asyncpg

### 8.3 错误处理

**错误处理示例**:

```python
import psycopg2
from psycopg2 import pool, OperationalError

def safe_query(func):
    """安全查询装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OperationalError as e:
            print(f"数据库连接错误: {e}")
            return None
        except Exception as e:
            print(f"查询错误: {e}")
            return None
    return wrapper

@safe_query
def search_documents_safe(query_vector, top_k=10):
    """安全的文档搜索"""
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (str(query_vector), top_k))
            return cur.fetchall()
    finally:
        connection_pool.putconn(conn)
```

## 9. 常见问题

### 9.1 依赖问题

**常见依赖问题**:

1. **psycopg2 安装失败**:

   ```bash
   # 使用二进制版本
   pip install psycopg2-binary
   ```

2. **pgvector 扩展未安装**:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 9.2 连接问题

**常见连接问题**:

1. **连接超时**: 检查网络和防火墙设置
2. **认证失败**: 检查用户名和密码
3. **数据库不存在**: 确保数据库已创建

### 9.3 性能问题

**性能问题排查**:

1. **查询慢**: 检查索引是否创建
2. **连接池耗尽**: 增加连接池大小或使用异步驱动
3. **内存不足**: 减少批量大小或使用流式处理

## 10. 参考资料

### 10.1 官方文档

- [psycopg2 文档](https://www.psycopg.org/docs/) - psycopg2 Documentation
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/) - SQLAlchemy Documentation
- [FastAPI 文档](https://fastapi.tiangolo.com/) - FastAPI Documentation

### 10.2 技术文档

- [LangChain PostgreSQL](https://python.langchain.com/docs/integrations/vectorstores/pgvector) -
  LangChain PGVector Integration
- [pgvector 核心原理](../../01-向量与混合搜索/技术原理/pgvector核心原理.md) - pgvector Core
  Principles

### 10.3 相关资源

- [asyncpg 文档](https://magicstack.github.io/asyncpg/) - asyncpg Documentation
- [Pandas 文档](https://pandas.pydata.org/docs/) - Pandas Documentation

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
**文档编号**: 07-02-01
