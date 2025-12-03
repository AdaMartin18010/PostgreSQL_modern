# 实时推荐系统

> **PostgreSQL版本**: 18.x
> **特点**: 实时计算、协同过滤、向量相似度

---

## 核心场景

### 商品推荐

```sql
-- 用户行为表
CREATE TABLE user_behaviors (
    user_id BIGINT,
    item_id BIGINT,
    behavior_type VARCHAR(20),  -- view/click/buy
    score NUMERIC(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 物品向量表（pgvector扩展）
CREATE EXTENSION vector;

CREATE TABLE item_vectors (
    item_id BIGINT PRIMARY KEY,
    embedding vector(128),  -- 128维向量
    category VARCHAR(50),
    tags TEXT[]
);

-- 创建向量索引（HNSW）
CREATE INDEX idx_item_vectors_embedding
ON item_vectors USING hnsw (embedding vector_cosine_ops);
```

### 相似度查询

```sql
-- 查找相似商品（<5ms）
SELECT
    item_id,
    1 - (embedding <=> $1::vector) as similarity
FROM item_vectors
ORDER BY embedding <=> $1::vector
LIMIT 20;

-- ⭐ PostgreSQL 18：向量查询优化
-- HNSW索引性能提升30%
```

---

## PostgreSQL 18特性

- **并行查询**: 协同过滤计算
- **JSONB优化**: 存储用户画像
- **Skip Scan**: 多维度过滤

---

**完整文档待补充**
