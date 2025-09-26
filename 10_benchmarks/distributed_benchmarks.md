# 分布式评测指引

## 工作负载与场景

- OLTP：pgbench（单分片/跨分片写/读混合）
- OLAP：分布式扫描/聚合/连接；广播与重分布对比
- 扩缩容/重分片：过程中吞吐/延迟/错误率

## 指标与方法

- 吞吐/延迟分位（P50/P95/P99）、可用性、SLA 违约率
- 热点与倾斜：任务耗时与数据量分布；重试/退避次数
- 故障注入：节点/网络/共识路径；恢复时间与数据正确性

## 最小演示（配合 demo）

- 参见：`../08_ecosystem_cases/distributed_db/citus_demo/`
- 示例：在 `init.sql` 基础上，使用 pgbench 自定义脚本对 `orders` 进行单键路由写与跨分片读的对比，采集 P95 延迟与重试次数。

## 报告模板

- 参见：`report_templates/README.md`（CSV 列定义与 Markdown 报告骨架）
