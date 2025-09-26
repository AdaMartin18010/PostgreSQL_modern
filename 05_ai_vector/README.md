# 05_ai_vector

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

- pgvector 仓库与文档：`https://github.com/pgvector/pgvector`
- PostgreSQL 扩展：`https://www.postgresql.org/docs/current/extend.html`
