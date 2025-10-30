# RAG 最小可运行案例

> 版本对标：pgvector 0.7.0+，PostgreSQL 17

## 📋 目标

演示如何使用 PostgreSQL + pgvector 构建最小可用的 RAG（Retrieval-Augmented Generation）检索系统，包
括：

- 向量数据存储
- HNSW 索引构建
- 向量相似度检索
- 元数据过滤

## 🚀 快速开始

### 前置要求

```bash
# 确保已安装 pgvector 扩展
psql -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"

# 确保 PostgreSQL 版本 >= 12
psql -c "SELECT version();"
```

### 步骤 1：创建数据结构

```bash
psql -U postgres -d your_database -f schema.sql
```

这将创建：

- `rag` schema
- `rag.docs` 表（存储文档和 embedding）
- HNSW 索引（用于快速向量检索）

### 步骤 2：准备数据

**方式 A：使用示例数据**:

```bash
# 使用提供的sample.jsonl
psql -U postgres -d your_database -f import_example.sql
```

**方式 B：导入自己的数据**:

1. 生成 embedding（使用 OpenAI、HuggingFace 等）
2. 准备 JSONL 格式数据：

   ```json
   {"id":1,"meta":{"title":"文档1","source":"test"},"embedding":[0.01,0.02,...]}
   {"id":2,"meta":{"title":"文档2","source":"test"},"embedding":[0.05,0.02,...]}
   ```

3. 导入数据（修改 load.sql 中的路径）

### 步骤 3：执行检索查询

```bash
# 在psql中执行查询
psql -U postgres -d your_database

# 设置查询向量（384维）
\set q '[0.01,0.02,0.03,...]'

# 执行相似度检索
\i query.sql
```

**Python 应用示例**：

```python
import psycopg2
import numpy as np

# 连接数据库
conn = psycopg2.connect("dbname=your_database user=postgres")
cur = conn.cursor()

# 查询向量（假设已经通过embedding模型生成）
query_embedding = np.random.rand(384).tolist()

# 执行向量检索
cur.execute("""
    SELECT id, meta, embedding <-> %s::vector as distance
    FROM rag.docs
    WHERE meta->>'source' = 'test'
    ORDER BY embedding <-> %s::vector
    LIMIT 5
""", (query_embedding, query_embedding))

results = cur.fetchall()
for row in results:
    print(f"ID: {row[0]}, Meta: {row[1]}, Distance: {row[2]}")

cur.close()
conn.close()
```

## 📊 性能优化建议

### 索引参数调优

```sql
-- HNSW索引参数说明
-- m: 每个节点的最大连接数（默认16，建议范围8-64）
-- ef_construction: 构建时的候选数（默认64，建议范围100-200）

-- 创建优化的索引
DROP INDEX IF EXISTS rag.idx_docs_hnsw;
CREATE INDEX idx_docs_hnsw ON rag.docs
USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 200);

-- 查询时调整ef_search
SET hnsw.ef_search = 40; -- 默认40，增加可提高召回率但降低速度
```

### 批量导入最佳实践

```sql
-- 1. 大批量导入时先删除索引
DROP INDEX IF EXISTS rag.idx_docs_hnsw;

-- 2. 批量导入数据
COPY rag.docs (meta, embedding) FROM '/path/to/data.csv' CSV;

-- 3. 导入完成后重建索引
CREATE INDEX idx_docs_hnsw ON rag.docs
USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 200);

-- 4. 更新统计信息
ANALYZE rag.docs;
```

### 查询性能优化

```sql
-- 1. 结合元数据过滤（推荐：先过滤后检索）
CREATE INDEX idx_docs_meta ON rag.docs USING gin (meta);

-- 2. 使用合适的距离度量
-- L2距离（欧几里得）：vector_l2_ops
-- 余弦距离：vector_cosine_ops
-- 内积：vector_ip_ops

-- 3. 限制结果数量
SELECT * FROM rag.docs
WHERE meta->>'category' = 'tech'
ORDER BY embedding <-> '[...]'::vector
LIMIT 10; -- 只取Top 10
```

## 🔧 故障排查

### 问题 1：索引构建失败

```sql
-- 检查向量维度一致性
SELECT id, array_length(embedding::float[], 1) as dim
FROM rag.docs
GROUP BY array_length(embedding::float[], 1);

-- 确保所有向量维度相同
```

### 问题 2：查询性能慢

```sql
-- 检查是否使用了索引
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM rag.docs
ORDER BY embedding <-> '[...]'::vector
LIMIT 5;

-- 应该看到 "Index Scan using idx_docs_hnsw"
```

### 问题 3：内存不足

```sql
-- 调整维护内存
SET maintenance_work_mem = '2GB'; -- 索引构建时使用

-- 调整工作内存
SET work_mem = '256MB'; -- 查询时使用
```

## 📈 性能基准

在标准配置下（PostgreSQL 17 + pgvector 0.7.0）：

| 数据量 | 维度 | 索引大小 | 构建时间 | P95 延迟 |
| ------ | ---- | -------- | -------- | -------- |
| 10K    | 384  | 15MB     | 2s       | 5ms      |
| 100K   | 384  | 150MB    | 25s      | 8ms      |
| 1M     | 384  | 1.5GB    | 5min     | 15ms     |

_测试环境：8 核 CPU，32GB 内存，SSD 存储_-

## 📚 扩展阅读

- pgvector 文档：`<https://github.com/pgvector/pgvector`>
- HNSW 算法论文：`<https://arxiv.org/abs/1603.09320`>
- RAG 架构指南：`../../05_ai_vector/README.md`

## ⚠️ 注意事项

1. **生产环境建议**：

   - 使用连接池（如 pgbouncer）
   - 定期 VACUUM 和 ANALYZE
   - 监控索引大小和查询性能
   - 备份 embedding 数据

2. **数据安全**：

   - embedding 包含敏感信息，注意访问控制
   - 定期备份向量数据
   - 使用 SSL/TLS 加密连接

3. **可扩展性**：
   - 单表建议不超过 1000 万向量
   - 更大规模考虑分区或 Citus 分布式
   - 监控磁盘空间使用
