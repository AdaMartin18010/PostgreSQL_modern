# 混合搜索（RRF）示例

> **PostgreSQL版本**: 18 ⭐ | 17
> **pgvector版本**: 2.0 ⭐ | 0.7+
> **最后更新**: 2025-11-11

---

## 📋 示例说明

本示例展示如何在PostgreSQL中使用**RRF（Reciprocal Rank Fusion）算法**融合全文搜索和向量搜索的结果，实现混合检索。

**适用场景**：

- 电商商品搜索
- 内容平台搜索
- 知识库检索

---

## 🚀 快速开始

### 1. 启动服务

```bash
docker-compose up -d
```

### 2. 连接到数据库

```bash
docker-compose exec postgres psql -U postgres -d hybrid_search
```

### 3. 执行混合搜索

```sql
-- 使用RRF融合查询
SELECT * FROM hybrid_search_rrf(
    'PostgreSQL 向量搜索',  -- 查询文本
    '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(384),  -- 查询向量
    10  -- 返回结果数量
);
```

### 4. 单独测试全文搜索

```sql
-- 全文搜索
SELECT
    id,
    name,
    ts_rank(description_tsv, plainto_tsquery('simple', 'PostgreSQL 向量')) AS score
FROM products
WHERE description_tsv @@ plainto_tsquery('simple', 'PostgreSQL 向量')
ORDER BY score DESC
LIMIT 10;
```

### 5. 单独测试向量搜索

```sql
-- 向量搜索
SELECT
    id,
    name,
    1 - (embedding <=> '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(384)) AS similarity
FROM products
WHERE embedding IS NOT NULL
ORDER BY embedding <=> '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(384)
LIMIT 10;
```

### 6. 停止服务

```bash
docker-compose down
```

---

## 📊 RRF算法说明

**RRF（Reciprocal Rank Fusion）公式**：

```text
RRF_score = Σ(1 / (60 + rank_i))
```

其中：

- `rank_i` 是第i个检索方法的结果排名
- 常数60用于平衡不同检索方法的权重

**优势**：

- 无需调参，自动融合不同检索方法
- 对缺失结果有容错性
- 适合多模态检索场景

---

## 📚 相关文档

- [AI 时代专题 - 向量与混合搜索](../../05-前沿技术/AI-时代/01-向量与混合搜索-pgvector与RRF.md)
- [落地案例 - 电商商品混合搜索](../../05-前沿技术/AI-时代/06-落地案例-2025精选.md#案例-1电商商品混合搜索supabase-实践)
- [向量检索性能调优指南](../../05-前沿技术/05.05-向量检索性能调优指南.md)

---

## 🔧 自定义配置

### 调整RRF参数

修改 `init.sql` 中的RRF函数，调整常数60的值：

```sql
-- 更重视排名靠前的结果（减小常数）
COALESCE(1.0 / (30 + t.text_rank), 0) +
COALESCE(1.0 / (30 + v.vector_rank), 0) AS combined_score

-- 更平滑的融合（增大常数）
COALESCE(1.0 / (100 + t.text_rank), 0) +
COALESCE(1.0 / (100 + v.vector_rank), 0) AS combined_score
```

---

**最后更新**：2025-11-11
