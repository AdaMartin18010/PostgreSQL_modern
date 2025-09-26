# timescaledb

## 主题边界

- 基于 PostgreSQL 的时序扩展：Hypertable、压缩、连续聚合、数据保留

## 核心要点

- 安装与启用：`CREATE EXTENSION timescaledb;`
- Hypertable：`create_hypertable`、Chunk 策略
- 压缩：`ALTER TABLE ... SET (timescaledb.compress)`、压缩策略
- 连续聚合：`CREATE MATERIALIZED VIEW ... WITH (timescaledb.continuous)`
- 保留与数据管理：`add_retention_policy`

## 知识地图

- 表与 Chunk → 写入与查询 → 压缩/聚合 → 策略化运维

## 权威参考

- 文档：`https://docs.timescale.com/`
- Releases：`https://github.com/timescale/timescaledb/releases`
