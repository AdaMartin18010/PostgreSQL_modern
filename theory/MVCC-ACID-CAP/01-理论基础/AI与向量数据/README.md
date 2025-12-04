# AI与向量数据理论

> **创建日期**: 2025-12-04
> **理论领域**: 向量数据库 + MVCC + ACID

---

## 📚 文档列表

### 核心文档

1. **[AI向量数据与MVCC](./AI向量数据与MVCC.md)** ⭐ 推荐
   - 向量数据的MVCC特性
   - pgvector索引与并发控制
   - 向量检索的快照隔离
   - 5个形式化定理
   - 完整性能模型

---

## 🎯 核心理论

### 1. 向量更新原子性

**定理**: 向量列的更新操作满足MVCC原子性。

```sql
UPDATE embeddings
SET embedding = new_vector
WHERE id = 123;
-- MVCC保证: All or Nothing
```

---

### 2. 向量检索快照隔离

**定理**: 在可重复读隔离级别下，向量相似度搜索看到一致的数据快照。

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

SELECT * FROM documents
ORDER BY embedding <=> query_vector
LIMIT 10;
-- 多次执行看到相同结果
```

---

### 3. HNSW索引MVCC行为

**规则**: HNSW索引条目遵循与heap tuple相同的可见性规则。

```
索引查询流程:
1. HNSW搜索 → 候选tid列表
2. Heap访问 → 获取tuple
3. MVCC过滤 → 检查可见性
4. 返回结果
```

---

## 🔬 应用场景

### 场景1: 实时推荐系统

```sql
-- 用户向量实时更新
UPDATE user_embeddings
SET embedding = compute_embedding(user_activity)
WHERE user_id = 123;

-- 并发相似度搜索不阻塞
SELECT user_id, similarity
FROM user_embeddings
ORDER BY embedding <=> target_vector
LIMIT 10;
```

**MVCC优势**:

- ✅ 更新不阻塞搜索
- ✅ 搜索看到一致快照
- ✅ 高并发性能

---

### 场景2: 知识图谱向量混合检索

```python
# RAG架构: 向量+图谱混合

def hybrid_search(query):
    with conn.begin():  # ACID事务
        # 向量检索
        vector_results = vector_search(query)

        # 图谱推理
        graph_results = graph_reasoning(vector_results)

        # 融合排序
        return merge_and_rank(vector_results, graph_results)

# ACID保证所有步骤在一致快照下执行
```

---

## 📊 性能模型

```
向量检索延迟 = T_index + T_heap + T_filter

MVCC开销: T_heap + T_filter
占比: 10-30%

优化策略:
├─ 增大 ef_search
├─ 定期 VACUUM
└─ 分区表设计
```

---

## 📖 快速开始

### 1. 理论学习

阅读顺序:

1. [AI向量数据与MVCC](./AI向量数据与MVCC.md) - 完整理论

### 2. 实践应用

参考案例:

1. [实时推荐系统](../../../DataBaseTheory/19-场景案例库/07-实时推荐系统/)
2. [RAG+知识图谱](../../../../docs/03-KnowledgeGraph/09-RAG+知识图谱混合架构.md)

---

## 🔗 相关资源

- **pgvector文档**: <https://github.com/pgvector/pgvector>
- **MVCC原理**: [../PostgreSQL版本特性/PostgreSQL-MVCC实现细节.md](../PostgreSQL版本特性/PostgreSQL-MVCC实现细节.md)
- **向量检索优化**: [../../../../theory/DataBaseTheory/21-AI知识库/05-向量检索优化.md](../../../../theory/DataBaseTheory/21-AI知识库/05-向量检索优化.md)

---

**返回**: [理论基础首页](../README.md) | [MVCC-ACID-CAP主页](../../README.md)
