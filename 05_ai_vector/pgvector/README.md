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

## 评测要点

- 指标：召回@K、P95/P99 延迟、QPS、内存占用、索引构建时长
- 维度：向量维度（d）、数据规模（N）、度量（L2/Cosine/IP）
- 方案：IVFFlat vs HNSW；`lists/probes` 与 `m/ef` 的权衡曲线

## 常见参数（示例）

- IVFFlat：`lists`（倒排桶数）、`probes`（查询时探测桶数）
- HNSW：`m`（出度）、`ef_construction`（建索引时候选）、`ef_search`（查询候选）
- 统计与维护：`ANALYZE` 后更新统计；大规模导入后再建索引/分批重建
