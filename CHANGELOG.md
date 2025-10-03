# 变更记录（CHANGELOG）

## 📋 目录

- [变更记录（CHANGELOG）](#变更记录changelog)
  - [📋 目录](#-目录)
  - [2025-10](#2025-10)
    - [项目质量提升（2025-10-03）](#项目质量提升2025-10-03)
    - [PostgreSQL 17 核心新特性覆盖](#postgresql-17-核心新特性覆盖)
  - [2025-09](#2025-09)

## 2025-10

- **全面更新至 PostgreSQL 17**：基于 2024年9月发布的 PostgreSQL 17 稳定版本
- **主 README 更新**：添加 PostgreSQL 17 核心新特性概览
- **版本差异文档完善**：详细更新 `version_diff_16_to_17.md`，包含完整迁移指南
- **新增特性详解文档**：创建 `pg17_new_features.md`，详细说明所有新特性
- **概览目录更新**：更新 `00_overview/README.md`，添加 PostgreSQL 17 特性概览
- **现代特性目录增强**：更新 `04_modern_features/README.md`，整合 17 版本新特性

### 项目质量提升（2025-10-03）

- **版本信息统一**：将所有文档的版本标注统一更新为"2025-10"
- **分布式数据库概念深化**：大幅扩展 `04_modern_features/distributed_db/concepts_overview.md`，从6行增加到200+行的详细内容
- **运维脚本优化**：将 `09_deployment_ops/bloat_check.sql` 从简单查询升级为生产级监控脚本，包含膨胀率计算、优先级建议和操作指导
- **性能测试脚本**：新增 `04_modern_features/pg17_performance_tests.sql`，全面测试PostgreSQL 17新特性性能
- **监控仪表板**：新增 `09_deployment_ops/pg17_monitoring_dashboard.sql`，提供PostgreSQL 17实例的全面监控和告警

### PostgreSQL 17 核心新特性覆盖

- **JSON 数据处理**：JSON_TABLE() 函数、JSON 构造函数和查询函数
- **性能优化**：VACUUM 内存管理、流式 I/O、高并发写入优化
- **逻辑复制增强**：故障转移控制、pg_createsubscriber 工具
- **备份恢复改进**：pg_basebackup 增量备份、COPY 容错选项
- **连接优化**：sslnegotiation=direct 选项

## 2025-09

- 初始化目录与核心/扩展/运维/基准/案例骨架
- 新增 RAG 最小案例与运维脚本（锁链路/膨胀）
- 加入版本对标更新时间占位与更新记录
