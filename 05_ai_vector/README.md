# 05_ai_vector

> 版本对标（更新于 2025-10）

## 主题边界

- 向量相似检索在 PostgreSQL 的体系化集成与实践（搜索、推荐、RAG、Embedding 存取）

## 核心要点

- 数据建模：向量维度/类型、度量方式（L2、Cosine、Inner Product）
- 索引策略：HNSW、IVFFlat 的适用性与参数调优
- 写入/更新：批量导入、分批构建索引、增量构建与重建
- 检索与召回：近邻搜索、重排序、过滤（metadata 结合）
- 一致性与性能：并发、内存/磁盘占用、ANALYZE 与统计

## 知识地图

- Embedding 管道 → 表/索引设计 → 查询与重排 → 评测与调优

## 权威参考

- pgvector 仓库与文档：`<https://github.com/pgvector/pgvector`>
- PostgreSQL 扩展：`<https://www.postgresql.org/docs/current/extend.html`>

## 端到端 Checklist（从零到检索）

- 环境：确认 `pgvector` 安装与 `CREATE EXTENSION`
- Schema：创建 `rag.docs(meta jsonb, embedding vector(d))`
- 数据：生成/导入 embedding（批量写入，必要时先不建索引）
- 索引：选择 HNSW/IVFFlat 并建索引（大批量导入后建索引或重建）
- 统计：`ANALYZE` 更新统计信息
- 查询：`<->` 距离 + 过滤；验证 P95/P99 延迟与召回率
- 维护：索引重建策略、`probes/ef` 调优、分批更新与真空
