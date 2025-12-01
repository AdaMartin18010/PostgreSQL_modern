# 医疗知识库示例

> **PostgreSQL版本**: 18 ⭐ | 17
> **pgvector版本**: 2.0 ⭐ | 0.7+
> **最后更新**: 2025-11-11

---

## 📋 示例说明

本示例展示如何构建医疗知识库系统，使用PostgreSQL存储医疗文档和向量，实现语义检索。本示例还演示了如何使用实验分支（模拟Neon Serverless分支功能）进行A/B测试。

**核心特性**：

- ✅ 医疗知识库检索
- ✅ 向量+全文混合搜索
- ✅ 实验分支管理（模拟Neon分支）
- ✅ 分类过滤

**适用场景**：

- 医疗知识库
- 临床决策支持
- 医学文献检索
- 实验数据管理

---

## 🚀 快速开始

### 1. 启动服务

```bash
docker-compose up -d
```

### 2. 连接到数据库

```bash
docker-compose exec postgres psql -U postgres -d medical_kb
```

### 3. 执行医疗知识检索

```sql
-- 搜索医疗知识（需要提供查询向量）
SELECT * FROM medical_search(
    '高血压治疗',  -- 查询文本
    '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(1536),  -- 查询向量
    NULL,  -- 类别过滤（可选）
    5  -- 返回top 5结果
);
```

### 4. 按类别检索

```sql
-- 只检索诊断类别的知识
SELECT * FROM medical_search(
    '高血压',
    '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(1536),
    'diagnosis',  -- 只检索诊断类别
    5
);
```

### 5. 查看所有知识

```sql
SELECT id, title, category, source, created_at
FROM medical_knowledge
ORDER BY created_at DESC;
```

### 6. 停止服务

```bash
docker-compose down
```

---

## 🔧 实验分支管理（Neon Serverless）

### 概念说明

Neon Serverless支持数据库分支功能，可以快速创建数据库副本用于实验，而无需复制整个数据库。

### 模拟实现

本示例使用表分区模拟分支功能：

```sql
-- 查看主分支数据
SELECT * FROM medical_knowledge_experiment WHERE experiment_name = 'main';

-- 查看实验分支数据
SELECT * FROM medical_knowledge_experiment WHERE experiment_name = 'experiment-v2';
```

### 实际使用Neon

```python
# Python示例：使用Neon API创建分支
from neon import Neon

neon = Neon(api_key="your-api-key")

# 创建实验分支
branch = neon.branches.create(
    project_id="your-project-id",
    name="experiment-v2"
)

# 在新分支上测试不同的embedding模型
# 对比主分支和实验分支的检索效果
```

---

## 📊 架构说明

```text
┌─────────────────────────────────────────┐
│        医疗应用系统                      │
│  - 知识检索接口                          │
│  - 实验分支管理                          │
│  - A/B测试对比                           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      PostgreSQL 18 + pgvector            │
│  - 医疗知识库表                           │
│  - 向量索引（HNSW）                      │
│  - 全文索引（GIN）                       │
│  - 混合检索函数                           │
└─────────────────────────────────────────┘
```

---

## 📚 相关文档

- [AI 时代专题 - Serverless与分支](../../05-前沿技术/AI-时代/03-Serverless与分支-Neon与Supabase.md)
- [落地案例 - 医疗实验数据分支](../../05-前沿技术/AI-时代/06-落地案例-2025精选.md#案例-3医疗实验数据分支neon-serverless)
- [RAG架构实战指南](../../05-前沿技术/05.04-RAG架构实战指南.md)

---

## 🎯 扩展场景

### 1. A/B测试不同embedding模型

```sql
-- 主分支：使用embedding模型v1
-- 实验分支：使用embedding模型v2

-- 对比检索效果
WITH main_results AS (
    SELECT * FROM medical_search_main('query', vector_v1, NULL, 10)
),
experiment_results AS (
    SELECT * FROM medical_search_experiment('query', vector_v2, NULL, 10)
)
SELECT
    'main' AS branch,
    COUNT(*) AS result_count,
    AVG(similarity) AS avg_similarity
FROM main_results
UNION ALL
SELECT
    'experiment' AS branch,
    COUNT(*) AS result_count,
    AVG(similarity) AS avg_similarity
FROM experiment_results;
```

### 2. 知识库版本管理

```sql
-- 使用实验分支管理不同版本的知识库
-- 主分支：生产版本
-- 实验分支：测试新版本的知识内容

-- 合并实验分支到主分支（模拟）
INSERT INTO medical_knowledge_experiment (experiment_name, ...)
SELECT 'main', ... FROM medical_knowledge_experiment
WHERE experiment_name = 'experiment-v2';
```

---

**最后更新**：2025-11-11
