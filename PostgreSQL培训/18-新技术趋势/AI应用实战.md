# AI 应用实战：基于 PostgreSQL 的 AI 应用开发

> **更新时间**: 2025 年 1 月
> **技术版本**: PostgreSQL 17+ with pgvector + AI 框架
> **文档编号**: 03-03-TREND-04

## 📑 概述

本文档介绍如何基于 PostgreSQL 和 pgvector 构建实际的 AI 应用，包括推荐系统、语义搜索、RAG（检索增强生成）、图像搜索等场景的完整实现方案。

## 🎯 核心价值

- **推荐系统**：基于向量相似度的商品/内容推荐
- **语义搜索**：理解查询意图的智能搜索
- **RAG 应用**：检索增强生成，结合向量数据库和 LLM
- **图像搜索**：基于图像特征的相似图像搜索
- **完整方案**：从数据准备到部署的完整实现

## 📚 目录

- [AI 应用实战：基于 PostgreSQL 的 AI 应用开发](#ai-应用实战基于-postgresql-的-ai-应用开发)
  - [📑 概述](#-概述)
  - [🎯 核心价值](#-核心价值)
  - [📚 目录](#-目录)
  - [1. AI 应用架构](#1-ai-应用架构)
    - [1.1 技术栈](#11-技术栈)
    - [1.2 核心组件](#12-核心组件)
  - [2. 推荐系统实现](#2-推荐系统实现)
    - [2.1 商品推荐系统](#21-商品推荐系统)
    - [2.2 推荐算法实现](#22-推荐算法实现)
    - [2.3 混合推荐策略](#23-混合推荐策略)
  - [3. 语义搜索实现](#3-语义搜索实现)
    - [3.1 文档语义搜索](#31-文档语义搜索)
    - [3.2 语义搜索 API](#32-语义搜索-api)
  - [4. RAG 应用实现](#4-rag-应用实现)
    - [4.1 RAG 架构](#41-rag-架构)
    - [4.2 RAG 实现](#42-rag-实现)
  - [5. 图像搜索实现](#5-图像搜索实现)
    - [5.1 图像特征提取](#51-图像特征提取)
  - [6. 性能优化](#6-性能优化)
    - [6.1 向量索引优化](#61-向量索引优化)
    - [6.2 缓存策略](#62-缓存策略)
  - [7. 部署方案](#7-部署方案)
    - [7.1 Docker 部署](#71-docker-部署)
    - [7.2 生产环境配置](#72-生产环境配置)
  - [📊 总结](#-总结)

---

## 1. AI 应用架构

### 1.1 技术栈

```text
┌─────────────────┐
│   应用层        │
│  (Python/Node)  │
└────────┬────────┘
         │
┌────────▼────────┐
│   AI 模型层     │
│  (OpenAI/本地)  │
└────────┬────────┘
         │
┌────────▼────────┐
│  PostgreSQL     │
│  + pgvector     │
└─────────────────┘
```

### 1.2 核心组件

- **PostgreSQL + pgvector**：向量存储和搜索
- **AI 模型**：文本嵌入、图像特征提取
- **应用层**：业务逻辑和 API 服务
- **缓存层**：Redis（可选）

---

## 2. 推荐系统实现

### 2.1 商品推荐系统

```sql
-- 创建商品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    embedding vector(1536),  -- 商品描述向量
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建用户行为表
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER REFERENCES products(id),
    interaction_type TEXT,  -- 'view', 'purchase', 'like'
    embedding vector(1536),  -- 用户偏好向量
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_products_embedding_hnsw
ON products USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_user_interactions_user_product
ON user_interactions (user_id, product_id);
```

### 2.2 推荐算法实现

```python
# Python 实现：基于协同过滤的推荐
import psycopg2
from pgvector.psycopg2 import register_vector
import openai

def get_user_preference_vector(user_id, conn):
    """获取用户偏好向量"""
    cur = conn.cursor()
    cur.execute("""
        SELECT AVG(embedding) AS user_vector
        FROM user_interactions
        WHERE user_id = %s
          AND interaction_type IN ('purchase', 'like')
    """, (user_id,))
    result = cur.fetchone()
    return result[0] if result and result[0] else None

def recommend_products(user_id, limit=10, conn=None):
    """推荐商品"""
    # 获取用户偏好向量
    user_vector = get_user_preference_vector(user_id, conn)
    if not user_vector:
        return []

    # 基于向量相似度推荐
    cur = conn.cursor()
    cur.execute("""
        SELECT
            p.id,
            p.name,
            p.description,
            1 - (p.embedding <=> %s::vector) AS similarity
        FROM products p
        WHERE p.embedding IS NOT NULL
          AND p.id NOT IN (
              SELECT product_id
              FROM user_interactions
              WHERE user_id = %s
          )
        ORDER BY p.embedding <=> %s::vector
        LIMIT %s
    """, (user_vector, user_id, user_vector, limit))

    return cur.fetchall()

# 使用示例
conn = psycopg2.connect("...")
register_vector(conn)
recommendations = recommend_products(user_id=123, limit=10, conn=conn)
```

### 2.3 混合推荐策略

```sql
-- SQL 实现：混合推荐（协同过滤 + 内容推荐）
CREATE OR REPLACE FUNCTION hybrid_recommend(
    p_user_id INTEGER,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_id INTEGER,
    product_name TEXT,
    recommendation_score FLOAT,
    recommendation_type TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_vector vector(1536);
BEGIN
    -- 获取用户偏好向量
    SELECT AVG(embedding) INTO v_user_vector
    FROM user_interactions
    WHERE user_id = p_user_id
      AND interaction_type IN ('purchase', 'like');

    -- 混合推荐：协同过滤 + 内容推荐
    RETURN QUERY
    WITH collaborative_filtering AS (
        -- 协同过滤：基于相似用户
        SELECT DISTINCT
            ui2.product_id,
            0.6 AS score,
            'collaborative' AS rec_type
        FROM user_interactions ui1
        JOIN user_interactions ui2
            ON ui1.product_id = ui2.product_id
            AND ui1.user_id != ui2.user_id
        WHERE ui1.user_id = p_user_id
          AND ui1.interaction_type IN ('purchase', 'like')
          AND ui2.user_id NOT IN (
              SELECT user_id FROM user_interactions
              WHERE user_id = p_user_id
          )
    ),
    content_based AS (
        -- 内容推荐：基于向量相似度
        SELECT
            p.id AS product_id,
            (1 - (p.embedding <=> v_user_vector))::FLOAT * 0.4 AS score,
            'content' AS rec_type
        FROM products p
        WHERE p.embedding IS NOT NULL
          AND p.id NOT IN (
              SELECT product_id FROM user_interactions
              WHERE user_id = p_user_id
          )
        ORDER BY p.embedding <=> v_user_vector
        LIMIT p_limit * 2
    )
    SELECT
        COALESCE(cf.product_id, cb.product_id) AS product_id,
        p.name AS product_name,
        COALESCE(cf.score, 0) + COALESCE(cb.score, 0) AS recommendation_score,
        COALESCE(cf.rec_type, cb.rec_type) AS recommendation_type
    FROM collaborative_filtering cf
    FULL OUTER JOIN content_based cb ON cf.product_id = cb.product_id
    JOIN products p ON p.id = COALESCE(cf.product_id, cb.product_id)
    ORDER BY recommendation_score DESC
    LIMIT p_limit;
END;
$$;
```

---

## 3. 语义搜索实现

### 3.1 文档语义搜索

```sql
-- 创建文档表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_documents_embedding_hnsw
ON documents USING hnsw (embedding vector_cosine_ops);
```

### 3.2 语义搜索 API

```python
# Python 实现：语义搜索 API
from flask import Flask, request, jsonify
import psycopg2
from pgvector.psycopg2 import register_vector
import openai

app = Flask(__name__)

def get_embedding(text):
    """获取文本嵌入向量"""
    response = openai.Embedding.create(
        model="text-embedding-3-small",
        input=text
    )
    return response['data'][0]['embedding']

@app.route('/search', methods=['POST'])
def semantic_search():
    """语义搜索接口"""
    data = request.json
    query_text = data.get('query')
    limit = data.get('limit', 10)

    # 获取查询向量
    query_embedding = get_embedding(query_text)

    # 搜索相似文档
    conn = psycopg2.connect("...")
    register_vector(conn)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            title,
            content,
            1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, query_embedding, limit))

    results = cur.fetchall()
    conn.close()

    return jsonify({
        'results': [
            {
                'id': r[0],
                'title': r[1],
                'content': r[2],
                'similarity': float(r[3])
            }
            for r in results
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 4. RAG 应用实现

### 4.1 RAG 架构

```text
用户查询
    ↓
生成查询向量
    ↓
向量数据库检索相关文档
    ↓
构建上下文
    ↓
LLM 生成回答
```

### 4.2 RAG 实现

```python
# Python 实现：RAG 应用
import psycopg2
from pgvector.psycopg2 import register_vector
import openai

class RAGSystem:
    def __init__(self, db_conn, openai_client):
        self.conn = db_conn
        self.client = openai_client
        register_vector(self.conn)

    def retrieve_context(self, query_embedding, top_k=5):
        """检索相关文档"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT
                content,
                1 - (embedding <=> %s::vector) AS similarity
            FROM documents
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_embedding, top_k))

        results = cur.fetchall()
        return [r[0] for r in results]

    def generate_answer(self, query, context_docs):
        """生成回答"""
        context = "\n\n".join(context_docs)

        prompt = f"""基于以下上下文回答问题。如果上下文中没有相关信息，请说明。

上下文：
{context}

问题：{query}

回答："""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一个有用的助手。"},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    def query(self, user_query):
        """RAG 查询"""
        # 1. 生成查询向量
        embedding_response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=user_query
        )
        query_embedding = embedding_response.data[0].embedding

        # 2. 检索相关文档
        context_docs = self.retrieve_context(query_embedding)

        # 3. 生成回答
        answer = self.generate_answer(user_query, context_docs)

        return {
            'answer': answer,
            'sources': context_docs
        }

# 使用示例
conn = psycopg2.connect("...")
rag = RAGSystem(conn, openai_client)
result = rag.query("什么是 PostgreSQL？")
print(result['answer'])
```

---

## 5. 图像搜索实现

### 5.1 图像特征提取

```python
# Python 实现：图像特征提取和搜索
import psycopg2
from pgvector.psycopg2 import register_vector
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50

class ImageSearchSystem:
    def __init__(self, db_conn):
        self.conn = db_conn
        register_vector(self.conn)

        # 加载预训练模型
        self.model = resnet50(pretrained=True)
        self.model.eval()

        # 图像预处理
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def extract_features(self, image_path):
        """提取图像特征"""
        image = Image.open(image_path).convert('RGB')
        image_tensor = self.transform(image).unsqueeze(0)

        with torch.no_grad():
            features = self.model(image_tensor)
            features = features.squeeze().numpy()

        return features.tolist()

    def search_similar_images(self, query_image_path, limit=10):
        """搜索相似图像"""
        # 提取查询图像特征
        query_features = self.extract_features(query_image_path)

        # 搜索相似图像
        cur = self.conn.cursor()
        cur.execute("""
            SELECT
                id,
                image_path,
                1 - (embedding <=> %s::vector) AS similarity
            FROM images
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_features, query_features, limit))

        return cur.fetchall()

# 使用示例
conn = psycopg2.connect("...")
image_search = ImageSearchSystem(conn)
results = image_search.search_similar_images('query_image.jpg', limit=10)
```

---

## 6. 性能优化

### 6.1 向量索引优化

```sql
-- 优化 HNSW 索引参数
CREATE INDEX idx_products_embedding_hnsw
ON products USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 32,              -- 增加连接数
    ef_construction = 200  -- 增加构建精度
);

-- 查询时调整 ef_search
SET hnsw.ef_search = 100;  -- 增加搜索精度
```

### 6.2 缓存策略

```python
# Python 实现：向量缓存
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_cached_embedding(text):
    """缓存文本嵌入向量"""
    return get_embedding(text)

def get_embedding_with_cache(text):
    """带缓存的嵌入向量获取"""
    cache_key = hashlib.md5(text.encode()).hexdigest()
    return get_cached_embedding(text)
```

---

## 7. 部署方案

### 7.1 Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY . .

# 启动应用
CMD ["python", "app.py"]
```

### 7.2 生产环境配置

```python
# config.py
import os

DATABASE_URL = os.getenv('DATABASE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 连接池配置
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10

# 向量搜索配置
VECTOR_SEARCH_LIMIT = 10
VECTOR_SIMILARITY_THRESHOLD = 0.7
```

---

## 📊 总结

基于 PostgreSQL 和 pgvector 可以构建强大的 AI 应用，包括推荐系统、语义搜索、RAG 应用、图像搜索等。
通过合理设计数据模型、优化向量索引、实现高效的检索算法，可以在生产环境中实现高性能的 AI 应用。

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
**文档编号**: 03-03-TREND-04
