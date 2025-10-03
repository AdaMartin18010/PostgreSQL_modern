# PostgreSQL_modern

面向现代数据库的 PostgreSQL 全面梳理与工程化实践（知识 + 软件工程梳理项目）。

## 📊 项目状态（2025-10-03）

> **定位**：PostgreSQL 17 导航框架 + 分布式/扩展生态深度指南  
> **成熟度**：结构完整（100%），内容建设中（60%），持续改进中

### ✅ 已完成部分

- **结构框架**：16个一级目录，职责边界清晰
- **PostgreSQL 17特性**：JSON增强、性能优化、逻辑复制、增量备份等核心特性已覆盖
- **分布式数据库**：理论完整（~2,700行），涵盖一致性、分片、分布式事务、HTAP等
- **实战案例**：3个完整案例（RAG向量检索、Citus分布式、pgbench性能测试）
- **版本对齐**：所有文档统一到2025-10，与PostgreSQL 17同步

### 🚧 进行中部分

- **基础模块深化**：SQL/事务/存储模块正在从骨架扩充为教程（目标：500-600行/模块）
- **对标工作落地**：与Wikipedia/CMU 15-445课程的详细对照表开发中
- **工程化建设**：CI/CD、自动化测试、版本监控机制规划中

### 📅 预计完成时间

- 基础模块深化：2025年10月底
- 对标落地：2025年11月底
- 工程化体系：2025年12月底

详见：[质量矩阵](QUALITY_MATRIX.md) | [改进计划](ACTION_PLAN_DETAILED.md) | [改进建议](IMPROVEMENT_SUMMARY.md)

## 🚀 快速开始

### 环境配置

本项目包含Python测试脚本，需要配置Python环境：

```powershell
# 1. 安装Python依赖
python -m pip install -r requirements.txt

# 2. 验证环境
python test_setup.py

# 3. 配置数据库（可选，用于运行测试）
cp tests/config/database.yml.example tests/config/database.yml
# 编辑 database.yml 填入数据库连接信息
```

**遇到 `psycopg2` 导入错误？** 请参考 [Python环境配置指南](SETUP_PYTHON_ENVIRONMENT.md)

### 测试框架

```powershell
# 运行单个测试
python tests/scripts/run_single_test.py tests/sql_tests/example_test.sql

# 运行所有测试
python tests/scripts/run_all_tests.py
```

详见：[测试框架文档](tests/README.md) | [快速开始](tests/QUICK_START.md)

---

• 对标目标：

- PostgreSQL 17（最新稳定版本，2024年9月发布）
- 生态组件：pgvector（向量）、TimescaleDB（时序）、PostGIS（地理空间）、Citus（分布式/扩展性）
- 知识组织：结构化导航 + 深度内容 + 实战案例
- 国际维基、高校课程与权威教材/论文的对照梳理（进行中）

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
  - distributed_db/（分布式数据库：一致性/共识/分片/分布式事务/HTAP/云原生/评测）
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

• PostgreSQL 17 核心新特性：

- **JSON 增强**：JSON_TABLE() 函数、JSON 构造函数和查询函数（JSON_EXISTS、JSON_QUERY、JSON_VALUE）
- **性能优化**：VACUUM 内存管理优化、流式 I/O 顺序读取、高并发写入吞吐量提升
- **逻辑复制增强**：故障转移控制、pg_createsubscriber 工具、升级过程保留复制槽和订阅状态
- **备份恢复**：pg_basebackup 增量备份支持、COPY 命令 ON_ERROR ignore 选项
- **连接优化**：sslnegotiation=direct 客户端连接选项

• 更新策略：

- 持续跟踪 PostgreSQL 官方"最新稳定版"与主要生态扩展的"最新 GA 版"，定期对照更新。
- 每个目录内的 README 给出主题边界、知识地图与权威参考链接。

• 贡献指南（简）：

- 新增内容：在相应目录添加子目录或文档，并补充该目录 README 的索引。
- 文献/链接：优先官方文档、权威书籍/论文与高校课程；注明版本与日期。
- 术语统一：使用简体中文，英文关键术语保留原文缩写。
