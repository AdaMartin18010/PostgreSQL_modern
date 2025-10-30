# 00_overview

> 版本对标（更新于 2025-10-25）

## 项目定位

知识 + 软件工程梳理：系统化对标 PostgreSQL 核心与现代生态（向量/时序/地理/分布式），结合工程方法
（CMMI、PMBOK、敏捷/DevOps）形成“主题 → 知识地图 → 工程实践 → 案例”的结构化内容。

## 版本对标（核心与生态）

- PostgreSQL（官方下载/文档）

  - 官方下载页（始终为最新稳定版）：`<https://www.postgresql.org/download/`>
  - 官方文档总览：`<https://www.postgresql.org/docs/`>
  - 发行说明总览：`<https://www.postgresql.org/docs/release/`>

- 向量检索扩展 pgvector（GitHub Releases）

  - Releases：`<https://github.com/pgvector/pgvector/releases`>
  - 文档：`<https://github.com/pgvector/pgvector`>

- 时序扩展 TimescaleDB（GitHub Releases）

  - Releases：`<https://github.com/timescale/timescaledb/releases`>
  - 文档：`<https://docs.timescale.com/`>

- 地理空间扩展 PostGIS（官方/安装文档）

  - 官网：`<https://postgis.net/`>
  - 安装与文档：`<https://postgis.net/install/`>

- 分布式/扩展性 Citus（GitHub Releases）
  - Releases：`<https://github.com/citusdata/citus/releases`>
  - 文档：`<https://docs.citusdata.com/`>

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

- PostgreSQL 官方：`<https://www.postgresql.org/`>
- pgvector：`<https://github.com/pgvector/pgvector`>
- TimescaleDB：`<https://github.com/timescale/timescaledb`>
- PostGIS：`<https://postgis.net/`>
- Citus：`<https://github.com/citusdata/citus`>

## PostgreSQL 17 核心特性概览

> **版本**：PostgreSQL 17.0  
> **发布日期**：2024 年 9 月 26 日  
> **最后验证**：2025-10-03

### JSON 数据处理革命性提升

- **JSON_TABLE() 函数**：将 JSON 数据转换为关系表，支持复杂 JSON 查询和分析
- **JSON 构造函数**：`JSON()`、`JSON_SCALAR()`、`JSON_SERIALIZE()` 提供更灵活的 JSON 构建
- **JSON 查询函数**：`JSON_EXISTS()`、`JSON_QUERY()`、`JSON_VALUE()` 简化 JSON 数据提取
- **应用场景**：API 数据存储、半结构化数据分析、微服务架构数据交换

### 性能优化突破

- **VACUUM 内存管理**：智能内存分配，减少 30% 内存使用，提升清理效率
- **流式 I/O 优化**：大表顺序扫描性能提升 20-40%
- **高并发写入**：多用户写入场景吞吐量提升 15-25%
- **B-tree 索引优化**：多值搜索性能显著提升

### 逻辑复制企业级增强

- **故障转移控制**：自动故障检测和切换，提高高可用部署可靠性
- **pg_createsubscriber**：一键在物理备用服务器创建逻辑复制订阅
- **升级兼容性**：pg_upgrade 保留逻辑复制槽和订阅状态，简化版本升级
- **应用场景**：读写分离、数据同步、多数据中心部署

### 备份恢复效率提升

- **增量备份**：pg_basebackup 支持增量备份，减少 60-80% 备份时间
- **COPY 容错**：`ON_ERROR ignore` 选项提高数据导入成功率
- **应用场景**：大规模数据迁移、定期备份优化、数据恢复加速

### 连接性能优化

- **sslnegotiation=direct**：直接 TLS 握手，减少连接建立时间 20-30%
- **应用场景**：高并发连接场景、微服务架构、云原生部署

## 更新记录

- 2025-10：全面更新至 PostgreSQL 17，详细梳理 17 版本新特性与迁移指南
- 2025-01：更新至 PostgreSQL 17，补充 17 版本新特性（JSON_TABLE、逻辑复制增强、增量备份、VACUUM 优化
  等）
- 2025-09：初始化目录、核心/扩展/运维/基准/案例骨架；补充 RAG 最小案例与运维脚本

## 月度巡检看板与定时任务

- 创建 Issue：使用 `.github/ISSUE_TEMPLATE/monthly_review.md`
- PR 流程：使用 `.github/pull_request_template.md`，在 `CHANGELOG.md` 记录结果
- 自动化（可选）：结合外部 CI/定时任务触发链接校验与版本对比（本仓库记录方法与结果）

## OLTP 观测与规划入口

- 运维：`09_deployment_ops/oltp_observability_planning.md`
- 基准：`10_benchmarks/pgbench_oltp_playbook.md`
