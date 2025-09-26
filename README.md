# PostgreSQL_modern

面向现代数据库的 PostgreSQL 全面梳理与工程化实践（知识 + 软件工程梳理项目）。

• 对标目标：

- PostgreSQL 最新稳定版本（核心）
- 生态组件：pgvector（向量）、TimescaleDB（时序）、PostGIS（地理空间）、Citus（分布式/扩展性）
- 工程方法论：CMMI、PMBOK、敏捷/DevOps 等（用于组织知识与工程流程）
- 国际维基、高校课程与权威教材/论文的对照梳理

• 项目范围（主题）：

  1) SQL/DDL/DCL 等数据库语言
  2) 事务与并发控制（ACID、MVCC、隔离级别、锁）
  3) 存储与访问路径（表/索引/执行计划/统计信息）
  4) 现代数据库特性（分区、复制/高可用、逻辑复制、备份恢复等）
  5) AI 时代的能力（向量检索、全文检索、函数式/可扩展性）
  6) 时序/向量/文档/内存/地理/数学等多模型能力与扩展
  7) 工程与生态实践（案例、部署、运维、监控、调优、基准）
  8) 对标国际 Wiki 与高校课程，系统性知识对照

• 目录导航：

- 00_overview/（项目总览与版本对标）
- 01_sql_ddl_dcl/（SQL 语言与 DDL/DML/DCL/TCL）
- 02_transactions/（ACID/MVCC/隔离级别/锁）
- 03_storage_access/（索引/统计/执行计划/维护）
- 04_modern_features/（分区/复制/备份/全文/FDW）
- 05_ai_vector/
  - pgvector/
- 06_timeseries/
  - timescaledb/
- 07_extensions/
  - postgis/
  - citus/
- 08_ecosystem_cases/（实战案例与脚本）
- 09_deployment_ops/（部署/运维/监控/安全）
- 10_benchmarks/（评测方法/脚本/指标）
- 11_courses_papers/（课程/教材/论文索引）
- 12_comparison_wiki_uni/（国际 wiki/高校对照）
- 99_references/（统一参考清单）
- GLOSSARY.md（统一术语表）

• 更新策略：

- 持续跟踪 PostgreSQL 官方“最新稳定版”与主要生态扩展的“最新 GA 版”，定期对照更新。
- 每个目录内的 README 给出主题边界、知识地图与权威参考链接。

• 贡献指南（简）：

- 新增内容：在相应目录添加子目录或文档，并补充该目录 README 的索引。
- 文献/链接：优先官方文档、权威书籍/论文与高校课程；注明版本与日期。
- 术语统一：使用简体中文，英文关键术语保留原文缩写。
