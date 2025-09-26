# pgvector

## 主题边界

- 在 PostgreSQL 中进行向量相似性搜索的扩展与工程实践

## 核心要点

- 安装与启用：`CREATE EXTENSION pgvector;`
- 数据类型：`vector`；维度限制与存储考量
- 索引：`HNSW`、`IVFFlat` 的建索引与参数（`m`, `ef_construction`, `lists`, `probes`）
- 查询：`<->` 距离操作符；过滤 + 向量检索组合查询
- 维护：重建索引、更新策略、统计与 ANALYZE

## 知识地图

- 模型与距离 → 索引选择 → 构建/查询 → 维护与调优

## 权威参考

- Releases：`https://github.com/pgvector/pgvector/releases`
- 文档与示例：`https://github.com/pgvector/pgvector`
