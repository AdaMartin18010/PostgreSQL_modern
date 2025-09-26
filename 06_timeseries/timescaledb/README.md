# timescaledb

> 版本对标（更新于 2025-09）

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

## 评测要点

- 写入吞吐（批写/乱序写）、查询延迟（窗口/近实时）、压缩比与查询影响
- 连续聚合刷新滞后、资源占用与并发下的稳定性
- Retention/TTL 对存储与查询路径的影响

## 常见参数（示例）

- Chunk 策略：时间窗口大小、空间维度（如 `device_id`）
- 压缩：列编码策略、冷/热数据分层
- 连续聚合：刷新策略与并发，物化视图索引

## 参考脚本索引

- `continuous_aggregate_example.sql`
