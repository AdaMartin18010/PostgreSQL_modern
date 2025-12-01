# RAG 知识库示例

> **PostgreSQL版本**: 18 ⭐ | 17
> **pgvector版本**: 2.0 ⭐ | 0.7+
> **最后更新**: 2025-11-11

---

## 📋 示例说明

本示例展示如何构建一个完整的RAG（Retrieval-Augmented Generation）知识库系统，使用PostgreSQL存储文档和向量，实现语义检索和混合搜索。

**适用场景**：

- 企业知识库
- 文档问答系统
- 智能客服
- 技术文档检索

---

## 🚀 快速开始

### 1. 启动服务

```bash
docker-compose up -d
```

### 2. 连接到数据库

```bash
docker-compose exec postgres psql -U postgres -d rag_kb
```

### 3. 执行RAG检索

```sql
-- 使用RAG检索函数（需要提供查询向量）
SELECT * FROM rag_retrieve(
    'PostgreSQL 向量搜索',  -- 查询文本
    '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(1536),  -- 查询向量
    5,  -- 返回top 5结果
    NULL  -- 类别过滤（可选）
);
```

### 4. 按类别检索

```sql
-- 只检索特定类别的文档
SELECT * FROM rag_retrieve(
    'PostgreSQL 新特性',
    '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(1536),
    5,
    '数据库'  -- 只检索数据库类别的文档
);
```

### 5. 查看所有文档

```sql
SELECT id, title, category, source, created_at
FROM knowledge_base
ORDER BY created_at DESC;
```

### 6. 停止服务

```bash
docker-compose down
```

---

## 🔧 实际使用流程

### 1. 文档入库

```sql
-- 插入新文档（需要先通过embedding模型生成向量）
INSERT INTO knowledge_base (title, content, source, category, tags, embedding)
VALUES (
    '文档标题',
    '文档内容...',
    '来源',
    '类别',
    ARRAY['标签1', '标签2'],
    '[生成的1536维向量]'::vector(1536)
);
```

### 2. 生成查询向量

在实际应用中，需要使用embedding模型（如OpenAI text-embedding-3-large）将查询文本转换为向量：

```python
# Python示例
import openai

def get_embedding(text):
    response = openai.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding

# 使用
query_text = "PostgreSQL 向量搜索"
query_vector = get_embedding(query_text)
```

### 3. 执行检索

```sql
-- 在Python中执行
results = execute_query("""
    SELECT * FROM rag_retrieve(
        %s,  -- query_text
        %s,  -- query_vector
        5,
        NULL
    )
""", (query_text, query_vector))
```

---

## 📊 架构说明

```text
┌─────────────────────────────────────────┐
│        应用层（FastAPI/Flask）           │
│  - 接收用户查询                          │
│  - 调用embedding模型生成向量              │
│  - 执行RAG检索                           │
│  - 调用LLM生成答案                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      PostgreSQL + pgvector              │
│  - 知识库表（文档+向量）                  │
│  - 向量索引（HNSW）                      │
│  - 全文索引（GIN）                       │
│  - RRF融合函数                           │
└─────────────────────────────────────────┘
```

---

## 📚 相关文档

- [AI 时代专题 - RAG架构](../../05-前沿技术/AI-时代/04-多模一体化-JSONB时序图向量.md)
- [RAG架构实战指南](../../05-前沿技术/05.04-RAG架构实战指南.md)
- [落地案例 - 内容RAG知识库](../../05-前沿技术/AI-时代/06-落地案例-2025精选.md#案例-8内容-rag-知识库pgvector--neon分支)

---

## 🔧 扩展建议

### 1. 添加文档分块

对于长文档，建议分块存储：

```sql
-- 更新chunk_index和chunk_total
UPDATE knowledge_base
SET chunk_index = 0, chunk_total = 5
WHERE id = 1;
```

### 2. 添加缓存层

使用Redis缓存热门查询结果：

```python
import redis

r = redis.Redis(host='localhost', port=6379)

def cached_rag_retrieve(query_text, query_vector):
    cache_key = f"rag:{hash(query_text)}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    results = execute_rag_query(query_text, query_vector)
    r.setex(cache_key, 3600, json.dumps(results))  # 缓存1小时
    return results
```

### 3. 添加LLM集成

检索到相关文档后，输入给LLM生成答案：

```python
from openai import OpenAI

def generate_answer(context_docs, user_query):
    context = "\n\n".join([doc['content'] for doc in context_docs])
    prompt = f"""基于以下文档内容回答问题：

{context}

问题：{user_query}
答案："""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

---

**最后更新**：2025-01-15

---

## 🐳 完整容器化部署

本示例还提供了**完整的容器化部署方案**，包含后端、前端、监控等所有服务：

- 📖 [完整部署文档](./README.full.md) - 详细部署说明
- 🚀 [启动脚本](./start.sh) - 一键启动脚本
- 🐳 [完整docker-compose](./docker-compose.full.yml) - 所有服务配置

### 快速启动完整系统

```bash
# 使用启动脚本（推荐）
chmod +x start.sh
./start.sh

# 或手动启动
docker-compose -f docker-compose.full.yml up -d
```

**完整系统包含**：

- ✅ PostgreSQL 18 + pgvector 2.0
- ✅ Redis缓存
- ✅ FastAPI后端
- ✅ React前端
- ✅ Celery异步任务
- ✅ Nginx反向代理
- ✅ Prometheus + Grafana监控

---
