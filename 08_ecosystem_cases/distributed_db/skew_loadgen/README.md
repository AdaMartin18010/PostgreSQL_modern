# 倾斜负载发生器与 pgbench 自定义脚本

## 目标

- 生成热点客户（如 Zipf 分布）以复现分片倾斜
- 使用 pgbench 自定义脚本对 `orders` 表进行读写，观测分片/任务耗时分布

## 脚本思路

- 预生成热点键集合（如前 1% 的 `customer_id` 产生 30~50% 访问）
- pgbench 自定义脚本（.sql）：
  - 事务 A：按 `customer_id` 单键路由写入/查询
  - 事务 B：跨分片 JOIN 读取（与 `customers` 引用表联动）
- 配合 `08_ecosystem_cases/distributed_db/skew_detection.sql` 分析倾斜

后续可补充可执行脚本与统计汇总工具（如 psql + CSV 输出）。
