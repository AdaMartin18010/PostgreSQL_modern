---

> **📋 文档来源**: `PostgreSQL\bench\INDEX.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 基准测试文档索引

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **最后更新**: 2025-11-12

---

## 🚀 快速入口

- **[QUICK_START.md](./QUICK_START.md)** ⭐ - 5 分钟快速体验
- **[README.md](./README.md)** - 完整文档索引和使用指南
- **[REPORT_TEMPLATE.md](./REPORT_TEMPLATE.md)** - 测试报告模板

---

## 📋 按类型分类

### 基准模板

1. **[pgbench-模板.md](./pgbench-模板.md)** - 标准 pgbench 压测模板
2. **[混合查询-基准模板.md](./混合查询-基准模板.md)** ⭐ - 混合查询性能基准
3. **[复制延迟-基准模板.md](./复制延迟-基准模板.md)** - 主从复制延迟测试

### PostgreSQL 17+ 特性基准

1. **[feature_bench/vacuum_memory_throughput.md](./feature_bench/vacuum_memory_throughput.md)** - VACUUM 内存/吞吐微基准
2. **[feature_bench/in_clause_btree.md](./feature_bench/in_clause_btree.md)** - IN 子句 + B-Tree 优化微基准
3. **[feature_bench/brin_parallel_build.md](./feature_bench/brin_parallel_build.md)** - BRIN 并行构建微基准
4. **[feature_bench/README.md](./feature_bench/README.md)** - 特性基准总览

### PostgreSQL 18 新特性基准 ⭐

1. **[feature_bench/async_io.md](./feature_bench/async_io.md)** - 异步I/O性能基准测试
2. **[feature_bench/parallel_query.md](./feature_bench/parallel_query.md)** - 并行查询性能基准测试
3. **[feature_bench/skip_scan.md](./feature_bench/skip_scan.md)** - Skip Scan性能基准测试
4. **[feature_bench/parallel_index_build.md](./feature_bench/parallel_index_build.md)** - 并行索引构建性能测试

### 测试脚本

1. **[scripts/mix_basic.sql](./scripts/mix_basic.sql)** ✅ - 基础混合查询脚本
2. **[scripts/mix_rrf.sql](./scripts/mix_rrf.sql)** ✅ - RRF 融合查询脚本
3. **[scripts/mix_weighted.sql](./scripts/mix_weighted.sql)** ✅ - 加权融合查询脚本
4. **[scripts/mix_filtered.sql](./scripts/mix_filtered.sql)** ✅ - 结构化过滤+混合查询脚本
5. **[scripts/README.md](./scripts/README.md)** ✅ - 脚本使用说明

### 辅助工具

> **注意**: 以下工具脚本正在开发中，请参考 [tools/README.md](./tools/README.md) 了解使用方法

1. ~~**[tools/analyze_pgbench_log.sh](./tools/analyze_pgbench_log.sh)**~~ - 日志分析工具（Linux/macOS，计划中）
2. ~~**[tools/analyze_pgbench_log.ps1](./tools/analyze_pgbench_log.ps1)**~~ - 日志分析工具（Windows，计划中）
3. ~~**[tools/monitor_system.sh](./tools/monitor_system.sh)**~~ - 系统资源监控脚本（计划中）
4. ~~**[tools/extract_pgbench_metrics.sh](./tools/extract_pgbench_metrics.sh)**~~ - 指标提取工具（Linux/macOS，计划中）
5. ~~**[tools/extract_pgbench_metrics.ps1](./tools/extract_pgbench_metrics.ps1)**~~ - 指标提取工具（Windows，计划中）
6. ~~**[tools/run_benchmark_suite.sh](./tools/run_benchmark_suite.sh)**~~ - 自动化测试套件（Linux/macOS，计划中）
7. ~~**[tools/run_benchmark_suite.ps1](./tools/run_benchmark_suite.ps1)**~~ - 自动化测试套件（Windows，计划中）
8. ~~**[tools/compare_results.sh](./tools/compare_results.sh)**~~ - 性能对比脚本（计划中）
9. ~~**[tools/baseline_manager.sh](./tools/baseline_manager.sh)**~~ - 性能基线管理脚本（计划中）
10. ~~**[tools/enhanced_monitor.sh](./tools/enhanced_monitor.sh)**~~ - 增强的系统监控脚本（PostgreSQL 18，计划中）
11. ~~**[tools/diagnose_performance.sh](./tools/diagnose_performance.sh)**~~ - 性能诊断工具（计划中）
12. ~~**[tools/stress_test.sh](./tools/stress_test.sh)**~~ - 压力测试工具（计划中）
13. ~~**[tools/compare_postgresql_versions.sh](./tools/compare_postgresql_versions.sh)**~~ - PostgreSQL版本对比工具（计划中）
14. **[tools/README.md](./tools/README.md)** ✅ - 工具使用说明

### SQL 监控脚本

1. **[sql/benchmark_monitoring.sql](./sql/benchmark_monitoring.sql)** ✅ - 基准测试监控 SQL 脚本
2. **[sql/README.md](./sql/README.md)** ✅ - SQL 脚本使用说明

### 配置文件

1. ~~**[config/benchmark_config.example.json](./config/benchmark_config.example.json)**~~ - 基准测试配置文件示例（计划中）
2. ~~**[config/benchmark_config.dev.json](./config/benchmark_config.dev.json)**~~ - 开发环境配置（计划中）
3. ~~**[config/benchmark_config.prod.json](./config/benchmark_config.prod.json)**~~ - 生产环境配置（计划中）
4. **[config/README.md](./config/README.md)** ✅ - 配置文件使用说明

### 快速开始和模板

1. **[QUICK_START.md](./QUICK_START.md)** - 5 分钟快速体验指南 ⭐
2. **[REPORT_TEMPLATE.md](./REPORT_TEMPLATE.md)** - 测试报告模板
3. **[BEST_PRACTICES.md](./BEST_PRACTICES.md)** - 最佳实践指南 ⭐
4. **[FAQ.md](./FAQ.md)** - 常见问题解答
5. **[CHANGELOG.md](./CHANGELOG.md)** - 更新日志

### CI/CD 集成

1. ~~**[.github/workflows/benchmark.yml](./.github/workflows/benchmark.yml)**~~ - GitHub Actions 工作流（计划中）
2. ~~**[.github/workflows/README.md](./.github/workflows/README.md)**~~ - CI/CD 集成使用说明（计划中）

### Docker 环境

1. ~~**[docker-compose.yml](./docker-compose.yml)**~~ - Docker Compose 配置（计划中）
2. **[docker-compose.README.md](./docker-compose.README.md)** ✅ - Docker 环境使用说明

---

## 🎯 按使用场景分类

### 新手入门

1. **[QUICK_START.md](./QUICK_START.md)** - 5 分钟快速体验
2. **[README.md](./README.md)** - 完整使用指南
3. **[pgbench-模板.md](./pgbench-模板.md)** - 标准压测模板

### OLTP 性能测试

1. **[pgbench-模板.md](./pgbench-模板.md)** ✅ - 标准 pgbench 压测
2. **[tools/README.md](./tools/README.md)** ✅ - 辅助分析工具说明
3. **[sql/benchmark_monitoring.sql](./sql/benchmark_monitoring.sql)** ✅ - 性能监控

### 混合查询测试

1. **[混合查询-基准模板.md](./混合查询-基准模板.md)** ✅ - 完整测试指南
2. **[scripts/README.md](./scripts/README.md)** ✅ - 测试脚本使用说明
3. **[tools/README.md](./tools/README.md)** ✅ - 结果分析工具说明

### 复制延迟测试

1. **[复制延迟-基准模板.md](./复制延迟-基准模板.md)** ✅ - 延迟测试指南
2. **[sql/benchmark_monitoring.sql](./sql/benchmark_monitoring.sql)** ✅ - 监控查询

### 新特性验证

1. **[feature_bench/README.md](./feature_bench/README.md)** - 特性基准总览
2. **[feature_bench/vacuum_memory_throughput.md](./feature_bench/vacuum_memory_throughput.md)** - VACUUM 测试
3. **[feature_bench/in_clause_btree.md](./feature_bench/in_clause_btree.md)** - IN 子句优化测试
4. **[feature_bench/brin_parallel_build.md](./feature_bench/brin_parallel_build.md)** - BRIN 并行构建测试

### PostgreSQL 18 特性验证 ⭐

> **注意**: 以下基准文档正在开发中

1. ~~**[feature_bench/async_io.md](./feature_bench/async_io.md)**~~ - 异步I/O性能测试（计划中）
2. ~~**[feature_bench/parallel_query.md](./feature_bench/parallel_query.md)**~~ - 并行查询性能测试（计划中）
3. ~~**[feature_bench/skip_scan.md](./feature_bench/skip_scan.md)**~~ - Skip Scan优化测试（计划中）
4. ~~**[feature_bench/parallel_index_build.md](./feature_bench/parallel_index_build.md)**~~ - 并行索引构建测试（计划中）

**参考文档**: 可参考现有的PostgreSQL 18特性文档：

- [异步I/O机制](../../07-多模型数据库/PostgreSQL-18新特性/异步I-O机制/README.md)
- [并行查询优化](../../07-多模型数据库/PostgreSQL-18新特性/README.md)

---

## 📊 按功能分类

### 环境准备

- **[QUICK_START.md](./QUICK_START.md)** - 环境检查
- **[pgbench-模板.md](./pgbench-模板.md)** - 数据初始化
- **[混合查询-基准模板.md](./混合查询-基准模板.md)** - 混合查询数据准备

### 测试执行

- **[scripts/README.md](./scripts/README.md)** ✅ - 测试脚本使用说明
- **[pgbench-模板.md](./pgbench-模板.md)** ✅ - 测试方法
- **[混合查询-基准模板.md](./混合查询-基准模板.md)** ✅ - 混合查询测试

### 监控与分析

- **[sql/benchmark_monitoring.sql](./sql/benchmark_monitoring.sql)** ✅ - SQL 监控
- ~~**[tools/monitor_system.sh](./tools/monitor_system.sh)**~~ - 系统监控（计划中）
- ~~**[tools/analyze_pgbench_log.sh](./tools/analyze_pgbench_log.sh)**~~ - 日志分析（计划中）
- ~~**[tools/extract_pgbench_metrics.sh](./tools/extract_pgbench_metrics.sh)**~~ - 指标提取（计划中）

**当前可用**:

- ✅ SQL监控脚本已创建
- ⏳ Shell工具脚本请参考 [tools/README.md](./tools/README.md) 了解详细使用方法

### 结果记录

- **[REPORT_TEMPLATE.md](./REPORT_TEMPLATE.md)** ✅ - 报告模板
- **[sql/benchmark_monitoring.sql](./sql/benchmark_monitoring.sql)** ✅ - 结果存储（包含benchmark_results表）

---

## 🔗 相关资源

### 项目内资源

- **SQL 示例**: `../sql/vector_examples.sql`
- **落地指南**: `../runbook/04-向量检索与混合查询-落地指南.md`
- **AI 时代专题**: `../05-前沿技术/AI-时代/01-向量与混合搜索-pgvector与RRF.md`
- **性能调优**: `../04-部署运维/04.04-监控与诊断.md`

### 外部资源

- **PostgreSQL 官方文档**: <https://www.postgresql.org/docs/current/pgbench.html>
- **pgvector 文档**: <https://github.com/pgvector/pgvector>
- **TPC-B 基准**: <http://www.tpc.org/tpcb/>

---

## 📝 文档更新记录

- **2025-11-12**: 基准测试体系完善
  - 新增快速开始指南
  - 新增测试报告模板
  - 新增 PowerShell 工具支持
  - 新增 SQL 监控脚本
  - 完善所有基准模板文档

- **2025-01-XX**: PostgreSQL 18特性增强
  - 新增异步I/O性能基准（计划中）
  - 新增并行查询性能基准（计划中）
  - 新增Skip Scan性能基准（计划中）
  - 新增并行索引构建基准（计划中）
  - 新增增强的监控工具（计划中）
  - 新增性能诊断工具（计划中）
  - 新增压力测试工具（计划中）
  - 新增版本对比工具（计划中）

- **2025-01-XX**: 文档完善和链接修复
  - ✅ 修复INDEX.md中所有无效链接
  - ✅ 创建混合查询测试脚本（mix_basic.sql, mix_rrf.sql, mix_weighted.sql, mix_filtered.sql）
  - ✅ 创建SQL监控脚本（benchmark_monitoring.sql）
  - ✅ 更新文档状态标记，明确已存在和计划中的内容

详见 [CHANGELOG.md](./CHANGELOG.md)

---

## 💡 使用建议

1. **首次使用**: 从 [QUICK_START.md](./QUICK_START.md) 开始
2. **选择测试**: 根据场景选择对应的基准模板
3. **执行测试**: 参考 [scripts/README.md](./scripts/README.md) 了解测试脚本使用方法
4. **监控分析**: 参考 [tools/README.md](./tools/README.md) 和 [sql/README.md](./sql/README.md) 了解工具使用方法
5. **记录结果**: 使用 [REPORT_TEMPLATE.md](./REPORT_TEMPLATE.md) 记录

## ⚠️ 重要提示

**当前状态**: 部分脚本和工具文件正在开发中，请参考对应的README.md文件了解详细使用方法。

**已完成的文档**:

- ✅ 所有基准模板文档
- ✅ 所有README说明文档
- ✅ PostgreSQL 17+ 特性基准文档

**计划中的内容**:

- ⏳ PostgreSQL 18 新特性基准文档
- ⏳ 测试脚本文件（SQL）
- ⏳ 辅助工具脚本（Shell/PowerShell）
- ⏳ SQL监控脚本
- ⏳ 配置文件示例

---

**快速开始**: [QUICK_START.md](./QUICK_START.md) | [README.md](./README.md)

1. **记录结果**: 使用 REPORT_TEMPLATE.md 记录

---

**快速开始**: [QUICK_START.md](./QUICK_START.md) | [README.md](./README.md)
