# PostgreSQL 官方文档季度对齐检查清单

## 概述

本文档用于定期检查 PostgreSQL_Formal 项目内容与 PostgreSQL 官方文档的对齐状态。建议每季度执行一次完整检查。

**检查周期**: 每季度（3月、6月、9月、12月）
**最后更新**: 2026-04-07
**版本**: 1.0

---

## 一、PostgreSQL 17 Release Notes 检查项

### 1.1 核心功能验证

- [ ] **VACUUM 内存优化** (`vacuum_buffer_usage_limit`)
  - [ ] 检查参数文档是否准确
  - [ ] 验证默认值是否与官方一致
  - [ ] 确认性能基准数据有效性
  - [ ] 检查文档文件: `00-Version-Specific/17-Released/17.01-VACUUM-Memory-Optimization-DEEP-V2.md`

- [ ] **增量备份** (pg_basebackup --incremental)
  - [ ] 验证命令语法准确性
  - [ ] 检查 manifest 文件格式说明
  - [ ] 确认与 pgBackRest 集成文档
  - [ ] 检查文档文件: `00-Version-Specific/17-Released/17.02-Incremental-Backup-DEEP-V2.md`

- [ ] **JSON_TABLE** 支持
  - [ ] 验证 SQL/JSON 标准兼容性说明
  - [ ] 检查嵌套路径语法文档
  - [ ] 确认错误处理行为描述
  - [ ] 检查文档文件: `00-Version-Specific/17-Released/17.03-JSON_TABLE-DEEP-V2.md`

- [ ] **MERGE 语句增强**
  - [ ] 验证 RETURNING 子句支持
  - [ ] 检查视图/物化视图支持状态
  - [ ] 确认并发行为文档
  - [ ] 检查文档文件: `00-Version-Specific/17-Released/17.04-MERGE-Enhancements-DEEP-V2.md`

- [ ] **逻辑复制升级**
  - [ ] 验证 pg_upgrade 兼容性
  - [ ] 检查复制槽迁移流程
  - [ ] 确认订阅状态保留机制
  - [ ] 检查文档文件: `00-Version-Specific/17-Released/17.05-Logical-Replication-Upgrades-DEEP-V2.md`

- [ ] **pg_maintain 角色**
  - [ ] 验证权限范围准确性
  - [ ] 检查与现有角色对比
  - [ ] 确认安全最佳实践
  - [ ] 检查文档文件: `00-Version-Specific/17-Released/17.06-pg_maintain-Role-DEEP-V2.md`

- [ ] **监控与诊断增强**
  - [ ] 验证 pg_stat_io 视图字段
  - [ ] 检查 EXPLAIN 新选项
  - [ ] 确认等待事件分类
  - [ ] 检查文档文件: `00-Version-Specific/17-Released/17.07-Monitoring-Diagnostics-DEEP-V2.md`

- [ ] **升级指南**
  - [ ] 验证升级路径准确性
  - [ ] 检查 EOL 版本信息
  - [ ] 确认兼容性矩阵
  - [ ] 检查文档文件: `00-Version-Specific/17-Released/17.08-Upgrade-Guide-DEEP-V2.md`

### 1.2 PG17 官方参考链接

- Release Notes: <https://www.postgresql.org/docs/17/release-17.html>
- 完整新特性列表: <https://www.postgresql.org/docs/17/release-17.html#RELEASE-17-HIGHLIGHTS>

---

## 二、PostgreSQL 18 Release Notes 检查项

### 2.1 核心功能验证

- [ ] **异步 I/O (AIO)**
  - [ ] 验证 `effective_io_concurrency` 新行为
  - [ ] 检查系统调用支持矩阵
  - [ ] 确认性能基准数据
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.01-AIO-DEEP-V2.md`

- [ ] **Skip Scan 优化**
  - [ ] 验证 B-Tree 索引优化器行为
  - [ ] 检查查询模式识别文档
  - [ ] 确认执行计划示例准确性
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.02-SkipScan-DEEP-V2.md`

- [ ] **UUIDv7 支持**
  - [ ] 验证 `gen_random_uuid_v7()` 函数
  - [ ] 检查时序排序特性说明
  - [ ] 确认与 UUIDv4 对比
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.03-UUIDv7-DEEP-V2.md`

- [ ] **虚拟生成列**
  - [ ] 验证 `GENERATED ALWAYS AS` 语法
  - [ ] 检查表达式限制文档
  - [ ] 确认索引支持状态
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.04-Virtual-Generated-Columns-DEEP-V2.md`

- [ ] **时态约束**
  - [ ] 验证 `PERIOD` 和 `WITHOUT OVERLAPS`
  - [ ] 检查时区处理
  - [ ] 确认与触发器对比
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.05-Temporal-Constraints-DEEP-V2.md`

- [ ] **OAuth2 集成**
  - [ ] 验证 `pg_oauth` 扩展状态
  - [ ] 检查身份提供商配置
  - [ ] 确认令牌刷新机制
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.06-OAuth2-Integration-DEEP-V2.md`

- [ ] **并行 GIN 索引构建**
  - [ ] 验证 `MAINTAIN_PARALLEL` 参数
  - [ ] 检查 workers 配置
  - [ ] 确认性能提升数据
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.07-Parallel-GIN-Build-DEEP-V2.md`

- [ ] **pg_upgrade 增强**
  - [ ] 验证 `--clone` 模式
  - [ ] 检查 `--sync` 选项
  - [ ] 确认跨版本兼容性
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.08-pg_upgrade-Enhancements-DEEP-V2.md`

- [ ] **pgvector 正式集成**
  - [ ] 验证向量操作符
  - [ ] 检查索引类型 (IVFFlat, HNSW)
  - [ ] 确认距离函数
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.09-pgvector-DEEP-V2.md`

- [ ] **CloudNativePG 支持**
  - [ ] 验证 Kubernetes CRD
  - [ ] 检查故障转移机制
  - [ ] 确认备份集成
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.10-CloudNativePG-DEEP-V2.md`

- [ ] **OpenTelemetry 集成**
  - [ ] 验证 `otel_exporter` 配置
  - [ ] 检查 span 和 metrics 导出
  - [ ] 确认采样策略
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.11-OpenTelemetry-DEEP-V2.md`

- [ ] **LZ4 压缩增强**
  - [ ] 验证 TOAST 压缩选项
  - [ ] 检查 WAL 压缩
  - [ ] 确认网络压缩
  - [ ] 检查文档文件: `00-Version-Specific/18-Released/18.12-LZ4-Compression-DEEP-V2.md`

### 2.2 PG18 官方参考链接

- Release Notes: <https://www.postgresql.org/docs/18/release-18.html>
- 开发中特性: <https://commitfest.postgresql.org/>

---

## 三、配置参数检查项

### 3.1 新增参数检查

- [ ] **PostgreSQL 17 新增参数**
  - [ ] `vacuum_buffer_usage_limit`
  - [ ] `io_combine_limit`
  - [ ] `maintenance_io_concurrency`
  - [ ] `ssl_crl_dir`
  - [ ] `max_slot_wal_keep_size`
  - [ ] `wal_summary_keep_time`

- [ ] **PostgreSQL 18 新增参数** (预览版)
  - [ ] `effective_io_concurrency` (新行为)
  - [ ] `aio_mode`
  - [ ] `aio_workers`
  - [ ] `otel_exporter_endpoint`
  - [ ] `otel_sample_rate`
  - [ ] `compression_method`

### 3.2 变更参数检查

- [ ] **默认值变更**
  - [ ] `max_connections` (如适用)
  - [ ] `shared_buffers` 推荐值
  - [ ] `work_mem` 推荐值
  - [ ] `autovacuum_max_workers`

- [ ] **废弃参数**
  - [ ] 检查 deprecated 警告
  - [ ] 验证替代方案文档
  - [ ] 确认迁移路径

### 3.3 参数文档参考

- PG17 参数: <https://www.postgresql.org/docs/17/runtime-config.html>
- PG18 参数: <https://www.postgresql.org/docs/18/runtime-config.html>

---

## 四、废弃特性检查项

### 4.1 PostgreSQL 17 废弃特性

- [ ] **客户端编码自动转换**
  - [ ] 验证 `client_encoding` 行为变更
  - [ ] 检查应用程序影响
  - [ ] 确认迁移指南

- [ ] **旧版 vacuumdb 选项**
  - [ ] 验证移除的选项
  - [ ] 检查替代命令

### 4.2 PostgreSQL 18 废弃特性

- [ ] **extprotocol** (外部表协议)
  - [ ] 验证移除状态
  - [ ] 检查 FDW 替代方案

- [ ] **旧版统计信息收集器**
  - [ ] 验证新统计框架
  - [ ] 检查监控查询兼容性

### 4.3 版本生命周期检查

- [ ] **EOL 版本确认**
  - [ ] PostgreSQL 12 (已 EOL)
  - [ ] PostgreSQL 13 (计划 EOL)
  - [ ] PostgreSQL 14 (状态)
  - [ ] PostgreSQL 15 (状态)

- [ ] **升级建议更新**
  - [ ] 验证最低推荐版本
  - [ ] 检查迁移路径

### 4.4 废弃文档参考

- 版本策略: <https://www.postgresql.org/support/versioning/>
- EOL 信息: <https://www.postgresql.org/support/versioning/>

---

## 五、交叉引用检查

### 5.1 内部链接验证

- [ ] `00-Version-Specific/INDEX.md` 完整性
- [ ] `00-NewFeatures-18/00-COMPLETE-COVERAGE-INDEX.md` 更新
- [ ] 知识图谱链接 (`KNOWLEDGE_GRAPH.yml`)
- [ ] 术语一致性 (`TERMINOLOGY.md`)

### 5.2 外部链接验证

- [ ] 所有官方文档链接有效性
- [ ] Release Notes 链接准确性
- [ ] 邮件列表引用
- [ ] CommitFest 链接

---

## 六、执行记录

| 季度 | 执行日期 | 执行人 | 结果 | 备注 |
|------|----------|--------|------|------|
| 2026-Q1 | 2026-04-07 | - | 创建中 | 初始版本 |
| 2026-Q2 | - | - | - | - |
| 2026-Q3 | - | - | - | - |
| 2026-Q4 | - | - | - | - |

---

## 七、相关文档

- [权威来源监控列表](./authority-sources.md)
- [季度对齐报告模板](../reports/quarterly-alignment-report-template.md)
- [AUTHORITY_CONTENT_INDEX.md](../AUTHORITY_CONTENT_INDEX.md)
- [PG18_VERIFICATION_REPORT.md](../PG18_VERIFICATION_REPORT.md)

---

## 八、附录

### A. 官方文档版本 URL 模式

```
https://www.postgresql.org/docs/{version}/
```

### B. Release Notes URL 模式

```
https://www.postgresql.org/docs/{version}/release-{version}.html
```

### C. 检查工具建议

1. 使用 `link_verifier.py` 验证外部链接
2. 使用 `analyze_v2.py` 检查文档结构
3. 手动检查关键功能描述

---

**维护**: PostgreSQL_Formal 文档维护团队
**审核周期**: 每季度
**下次检查**: 2026-06-30
