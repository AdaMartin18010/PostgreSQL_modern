# Distributed Database（分布式数据库）

> 版本对标（更新于 2025-10）

## 主题边界

- 一致性模型与共识：线性一致性、顺序一致性、最终一致性；Paxos/Raft
- 数据切分与复制：分片（哈希/范围/目录）、主从/多主、同步/异步/仲裁
- 分布式事务：两阶段提交（2PC）、三阶段提交（3PC）、补偿/幂等、全局时钟与真相源
- 查询与执行：分布式优化器、路由/重分布、广播/分片连接、代价与倾斜
- HTAP 与混部：OLTP/OLAP 融合、列行混合、冷热分层
- 云原生与多活：容器与调度、跨 AZ/Region、故障域与仲裁、网络分区
- 可观测性与 SRE：跨节点指标、慢查询与倾斜分析、限流与回退
- 评测与方法：TPC-C/H/DS、YCSB、微基准与混沌工程

## 与本仓库的关系

- PostgreSQL 内建：物理/逻辑复制、分区、FDW 提供扩展基座
- Citus 等扩展：提供分片、分布式查询与事务能力（见 `07_extensions/citus/`）
- 本模块：抽象分布式数据库通用原理与工程方法，统一对标国际 wiki 与高校课程

## 知识地图

- 概念与模型 → 数据切分与复制 → 分布式事务 → 查询执行与优化 → 运维与 SRE → 评测

## 目录

- `concepts_overview.md`（核心概念与模型综述）
- `consistency_consensus.md`（一致性模型与共识协议）
- `sharding_replication.md`（分片策略与复制拓扑）
- `distributed_transactions.md`（分布式事务与幂等补偿）
- `htap_architecture.md`（HTAP 与混合负载架构）
- `cloud_native.md`（云原生与跨区域多活）
- `observability_sre.md`（可观测性、倾斜分析与 SRE 手册）
- `benchmarking_guides.md`（评测方法与指标体系）

## 实践/运维/评测入口

- 实践脚本：`../../08_ecosystem_cases/distributed_db/`
- Citus 最小演示：`../../08_ecosystem_cases/distributed_db/citus_demo/`
- 跨区域多活骨架：`../../08_ecosystem_cases/distributed_db/multi_region_demo/`
- 倾斜负载发生器：`../../08_ecosystem_cases/distributed_db/skew_loadgen/`
- 运维清单：`../../09_deployment_ops/distributed_ops_checklist.md`
- 分布式评测：`../../10_benchmarks/distributed_benchmarks.md`

## 权威参考（对标）

- Wikipedia：`https://en.wikipedia.org/wiki/Distributed_database`、`https://en.wikipedia.org/wiki/Consistency_model`、`https://en.wikipedia.org/wiki/Raft_(algorithm)`
- CMU 15-445/645：`https://15445.courses.cs.cmu.edu/`（分布式与并发专题）
- MIT 6.824：`https://pdos.csail.mit.edu/6.824/`
- 论文与教科书："Designing Data-Intensive Applications"（Kleppmann）、"Readings in Database Systems"

## Checklist（工程落地）

- 明确一致性目标与失败模型；选定共识与仲裁策略
- 选择分片键并评估倾斜；跨分片 JOIN/事务占比与路由策略
- 定义全局唯一键与幂等语义；补偿流程与可重放日志
- 观测分布式执行计划与热点；限流/重试/熔断阈值
- 评测覆盖：单分片/跨分片、扩缩容/重分片、故障注入
