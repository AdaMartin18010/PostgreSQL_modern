# 00_overview

> 版本对标（更新于 2025-09）

## 项目定位

知识 + 软件工程梳理：系统化对标 PostgreSQL 核心与现代生态（向量/时序/地理/分布式），结合工程方法（CMMI、PMBOK、敏捷/DevOps）形成“主题 → 知识地图 → 工程实践 → 案例”的结构化内容。

## 版本对标（核心与生态）

- PostgreSQL（官方下载/文档）
  - 官方下载页（始终为最新稳定版）：`https://www.postgresql.org/download/`
  - 官方文档总览：`https://www.postgresql.org/docs/`
  - 发行说明总览：`https://www.postgresql.org/docs/release/`

- 向量检索扩展 pgvector（GitHub Releases）
  - Releases：`https://github.com/pgvector/pgvector/releases`
  - 文档：`https://github.com/pgvector/pgvector`

- 时序扩展 TimescaleDB（GitHub Releases）
  - Releases：`https://github.com/timescale/timescaledb/releases`
  - 文档：`https://docs.timescale.com/`

- 地理空间扩展 PostGIS（官方/安装文档）
  - 官网：`https://postgis.net/`
  - 安装与文档：`https://postgis.net/install/`

- 分布式/扩展性 Citus（GitHub Releases）
  - Releases：`https://github.com/citusdata/citus/releases`
  - 文档：`https://docs.citusdata.com/`

更新策略：

- 仅以官方“下载/发行说明/Releases”作为版本权威来源；不采信二手转载的版本号。
- 每月巡检一次（或当上游发布时即时更新），统一在各主题 README 顶部“版本对标”处更新链接与版本号。

## 知识地图（骨架）

- 核心：SQL/DDL/DCL；事务与并发（ACID、MVCC、隔离级别、锁）；存储与访问（表、索引、统计、执行计划）
- 现代能力：分区、复制（物理/逻辑）、高可用、备份恢复、权限与安全
- 生态专题：
  - 向量：`05_ai_vector/pgvector`
  - 时序：`06_timeseries/timescaledb`
  - 地理：`07_extensions/postgis`
  - 分布式：`07_extensions/citus`
- 工程与案例：部署/运维/监控/调优、基准与评测、生态优秀案例
- 对标/课程/论文：国际 wiki、高校公开课、教材与论文

## 方法与产出

- 方法：以领域 → 能力 → 工程实践的结构沉淀；每章配“范围、关键概念、常见陷阱、Checklist、权威链接”。
- 产出：
  - 入门：一页纸快速导航（本目录）
  - 进阶：各主题目录 README 的知识地图与操作清单
  - 实战：`08_ecosystem_cases`、`09_deployment_ops`、`10_benchmarks` 的案例与脚本

## 权威参考（统一入口）

- PostgreSQL 官方：`https://www.postgresql.org/`
- pgvector：`https://github.com/pgvector/pgvector`
- TimescaleDB：`https://github.com/timescale/timescaledb`
- PostGIS：`https://postgis.net/`
- Citus：`https://github.com/citusdata/citus`

## 更新记录
- 2025-09：初始化目录、核心/扩展/运维/基准/案例骨架；补充 RAG 最小案例与运维脚本
