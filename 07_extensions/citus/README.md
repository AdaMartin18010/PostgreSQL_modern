# citus

> 版本对标（更新于 2025-10）

## 主题边界

- PostgreSQL 的分布式扩展：分片、分布式查询与事务

## 核心要点

- 安装与启用：`CREATE EXTENSION citus;`
- 分片表：`create_distributed_table`、分片键选择
- 查询：分布式执行计划、路由/重分布
- 事务：一致性、分布式事务注意事项
- 运维：节点管理、扩缩容、故障切换

## 知识地图

- 数据建模 → 分片策略 → 查询与事务 → 运维与高可用

## 与分布式模块的关系

- 通用原理与工程方法见：`04_modern_features/distributed_db/README.md`
- Citus 作为实现路径之一：提供分片、路由、重分布与协调执行
- 对比项：一致性与事务语义、跨分片 JOIN 策略、扩缩容与重分片行为

## 权威参考

- 文档：`<https://docs.citusdata.com/`>
- Releases：`<https://github.com/citusdata/citus/releases`>

## 评测要点

- 单分片路由查询 vs 跨分片重分布查询的对比
- 分片键倾斜对吞吐与延迟的影响
- 扩缩容与重分片过程中的可用性与性能波动

## 常见参数（示例）

- 分片数与副本数、分片键/分布列选择
- 任务执行并发度与网络带宽限制
- 事务隔离与写入路由策略

## 分布式运维与拓扑

- 与主备/一主多从/级联复制配合实现 HA 与容灾（参考 `04_modern_features/replication_topologies.md`、`backup_disaster_recovery.md`）
- 控制平面/数据平面分离与监控（路由/重分布延迟、失败任务重试）
