# 变更记录（CHANGELOG）

## 2025-10

- **全面更新至 PostgreSQL 17**：基于 2024年9月发布的 PostgreSQL 17 稳定版本
- **主 README 更新**：添加 PostgreSQL 17 核心新特性概览
- **版本差异文档完善**：详细更新 `version_diff_16_to_17.md`，包含完整迁移指南
- **新增特性详解文档**：创建 `pg17_new_features.md`，详细说明所有新特性
- **概览目录更新**：更新 `00_overview/README.md`，添加 PostgreSQL 17 特性概览
- **现代特性目录增强**：更新 `04_modern_features/README.md`，整合 17 版本新特性

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
