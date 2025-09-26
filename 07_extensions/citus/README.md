# citus

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

## 权威参考

- 文档：`https://docs.citusdata.com/`
- Releases：`https://github.com/citusdata/citus/releases`

## 评测要点

- 单分片路由查询 vs 跨分片重分布查询的对比
- 分片键倾斜对吞吐与延迟的影响
- 扩缩容与重分片过程中的可用性与性能波动

## 常见参数（示例）

- 分片数与副本数、分片键/分布列选择
- 任务执行并发度与网络带宽限制
- 事务隔离与写入路由策略
