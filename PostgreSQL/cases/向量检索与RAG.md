# 案例：向量检索与 RAG（占位）

## 架构

- pgvector/IVFFLAT/HNSW，混合检索（向量+结构化过滤）

## 关键点

- 分区与索引参数、批量导入、近实时更新、延迟与召回权衡

## 验证

- QPS/延迟、召回@k、资源占用、更新一致性

## 最小可复现（占位）

```sql
-- 需安装 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 假设使用 384 维嵌入
CREATE TABLE docs(id bigserial primary key, meta jsonb, embedding vector(384));
CREATE INDEX ON docs USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- 插入示例数据（占位）
-- INSERT INTO docs(meta, embedding) VALUES ('{"title":"a"}', '[0.1, 0.2, ...]');

-- 检索（向量 + 结构化过滤）
SELECT id, meta
FROM docs
WHERE meta->>'lang' = 'zh'
ORDER BY embedding <-> '[0.1,0.2, ...]'::vector
LIMIT 5;
```
