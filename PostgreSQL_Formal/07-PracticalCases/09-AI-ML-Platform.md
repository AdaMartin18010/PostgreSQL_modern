# 案例9: AI/ML平台

> **实战案例**
> **创建日期**: 2026-03-04

---

## 1. 向量数据库

使用pgvector存储模型embeddings。

```sql
-- 创建向量表
CREATE TABLE embeddings (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(768)
);

-- 相似度搜索
SELECT content, embedding <-> query_embedding AS distance
FROM embeddings
ORDER BY distance
LIMIT 5;
```

---

## 2. RAG架构

PostgreSQL作为向量存储 + 全文搜索。

---

**完成度**: 100%
