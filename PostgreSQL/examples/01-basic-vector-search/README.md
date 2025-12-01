# 基础向量搜索示例

> **PostgreSQL版本**: 18 ⭐ | 17
> **pgvector版本**: 2.0 ⭐ | 0.7+
> **最后更新**: 2025-11-11

---

## 📋 示例说明

这是一个最基础的向量搜索示例，展示如何在PostgreSQL中使用pgvector进行向量存储和相似度搜索。

## 🚀 快速开始

### 1. 启动服务

```bash
docker-compose up -d
```

### 2. 连接到数据库

```bash
docker-compose exec postgres psql -U postgres -d vectordb
```

### 3. 执行向量搜索

```sql
-- 定义查询向量
WITH query AS (
    SELECT '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(384) AS q_vec
)
SELECT
    id,
    title,
    1 - (embedding <=> q_vec) AS similarity
FROM documents, query
ORDER BY embedding <=> q_vec
LIMIT 5;
```

### 4. 停止服务

```bash
docker-compose down
```

## 📚 相关文档

- [AI 时代专题 - 向量与混合搜索](../../05-前沿技术/AI-时代/01-向量与混合搜索-pgvector与RRF.md)
- [向量检索性能调优指南](../../05-前沿技术/05.05-向量检索性能调优指南.md)
