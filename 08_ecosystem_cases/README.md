# 08_ecosystem_cases

## 目录结构建议

- ai_vector/: RAG/召回+重排、Embedding 管道、混合检索示例
- timeseries/: 物联网/监控场景，写入/连续聚合/压缩/TTL
- postgis/: 位置服务、空间分析、可视化对接
- citus/: 多租户/分布式查询与扩缩容

## 案例模板（每个子目录）

- 背景与目标
- 架构与数据模型
- 关键 SQL/索引/参数
- 基准指标与结果截图
- 运维要点与 Checklist
- 参考与链接（官方/论文/课程）

## 示例：ai_vector/rag_minimal（占位）

- 目标：用 pgvector 存储文本 Embedding，进行 KNN + 过滤检索
- 步骤：
  1) `CREATE EXTENSION pgvector;`
  2) 建表（id, meta, embedding vector[d]）；批量导入嵌入；
  3) 选择 `HNSW` 或 `IVFFlat` 索引并建索引；
  4) 使用 `<->` + 过滤条件进行查询；
- 脚本占位：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS rag;
CREATE TABLE IF NOT EXISTS rag.docs (
  id bigserial PRIMARY KEY,
  meta jsonb,
  embedding vector(384)
);
-- HNSW 示例
CREATE INDEX IF NOT EXISTS idx_docs_hnsw ON rag.docs USING hnsw (embedding vector_l2_ops) WITH (m=16, ef_construction=200);
-- 查询占位
-- SELECT id FROM rag.docs ORDER BY embedding <-> :query_embedding LIMIT 5;
```
