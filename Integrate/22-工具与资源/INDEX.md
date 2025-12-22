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

### 测试脚本

1. **[scripts/mix_basic.sql](./scripts/mix_basic.sql)** - 基础混合查询脚本
2. **[scripts/mix_rrf.sql](./scripts/mix_rrf.sql)** - RRF 融合查询脚本
3. **[scripts/mix_weighted.sql](./scripts/mix_weighted.sql)** - 加权融合查询脚本
4. **[scripts/mix_filtered.sql](./scripts/mix_filtered.sql)** - 结构化过滤+混合查询脚本
5. **[scripts/README.md](./scripts/README.md)** - 脚本使用说明

### 辅助工具

1. **[tools/analyze_pgbench_log.sh](./tools/analyze_pgbench_log.sh)** - 日志分析工具（Linux/macOS）
2. **[tools/analyze_pgbench_log.ps1](./tools/analyze_pgbench_log.ps1)** - 日志分析工具（Windows）
3. **[tools/monitor_system.sh](./tools/monitor_system.sh)** - 系统资源监控脚本
4. **[tools/extract_pgbench_metrics.sh](./tools/extract_pgbench_metrics.sh)** - 指标提取工具（Linux/macOS）
5. **[tools/extract_pgbench_metrics.ps1](./tools/extract_pgbench_metrics.ps1)** - 指标提取工具（Windows）
6. **[tools/run_benchmark_suite.sh](./tools/run_benchmark_suite.sh)** - 自动化测试套件（Linux/macOS）
7. **[tools/run_benchmark_suite.ps1](./tools/run_benchmark_suite.ps1)** - 自动化测试套件（Windows）
8. **[tools/compare_results.sh](./tools/compare_results.sh)** - 性能对比脚本
9. **[tools/baseline_manager.sh](./tools/baseline_manager.sh)** - 性能基线管理脚本
10. **[tools/README.md](./tools/README.md)** - 工具使用说明

### SQL 监控脚本

1. **[sql/benchmark_monitoring.sql](./sql/benchmark_monitoring.sql)** - 基准测试监控 SQL 脚本
2. **[sql/README.md](./sql/README.md)** - SQL 脚本使用说明

### 配置文件

1. **[config/benchmark_config.example.json](./config/benchmark_config.example.json)** - 基准测试配置文件示例
2. **[config/benchmark_config.dev.json](./config/benchmark_config.dev.json)** - 开发环境配置
3. **[config/benchmark_config.prod.json](./config/benchmark_config.prod.json)** - 生产环境配置
4. **[config/README.md](./config/README.md)** - 配置文件使用说明

### 快速开始和模板

1. **[QUICK_START.md](./QUICK_START.md)** - 5 分钟快速体验指南 ⭐
2. **[REPORT_TEMPLATE.md](./REPORT_TEMPLATE.md)** - 测试报告模板
3. **[BEST_PRACTICES.md](./BEST_PRACTICES.md)** - 最佳实践指南 ⭐
4. **[FAQ.md](./FAQ.md)** - 常见问题解答
5. **[CHANGELOG.md](./CHANGELOG.md)** - 更新日志

### CI/CD 集成

1. **[.github/workflows/benchmark.yml](./.github/workflows/benchmark.yml)** - GitHub Actions 工作流
2. **[.github/workflows/README.md](./.github/workflows/README.md)** - CI/CD 集成使用说明

### Docker 环境

1. **[docker-compose.yml](./docker-compose.yml)** - Docker Compose 配置
2. **[docker-compose.README.md](./docker-compose.README.md)** - Docker 环境使用说明

---

## 🎯 按使用场景分类

### 新手入门

1. **[QUICK_START.md](./QUICK_START.md)** - 5 分钟快速体验
2. **[README.md](./README.md)** - 完整使用指南
3. **[pgbench-模板.md](./pgbench-模板.md)** - 标准压测模板

### OLTP 性能测试

1. **[pgbench-模板.md](./pgbench-模板.md)** - 标准 pgbench 压测
2. **[tools/](./tools/)** - 辅助分析工具
3. **[sql/benchmark_monitoring.sql](./sql/benchmark_monitoring.sql)** - 性能监控

### 混合查询测试

1. **[混合查询-基准模板.md](./混合查询-基准模板.md)** - 完整测试指南
2. **[scripts/](./scripts/)** - 测试脚本集合
3. **[tools/](./tools/)** - 结果分析工具

### 复制延迟测试

1. **[复制延迟-基准模板.md](./复制延迟-基准模板.md)** - 延迟测试指南
2. **[sql/benchmark_monitoring.sql](./sql/benchmark_monitoring.sql)** - 监控查询

### 新特性验证

1. **[feature_bench/README.md](./feature_bench/README.md)** - 特性基准总览
2. **[feature_bench/vacuum_memory_throughput.md](./feature_bench/vacuum_memory_throughput.md)** - VACUUM 测试
3. **[feature_bench/in_clause_btree.md](./feature_bench/in_clause_btree.md)** - IN 子句优化测试
4. **[feature_bench/brin_parallel_build.md](./feature_bench/brin_parallel_build.md)** - BRIN 并行构建测试

---

## 📊 按功能分类

### 环境准备

- **[QUICK_START.md](./QUICK_START.md)** - 环境检查
- **[pgbench-模板.md](./pgbench-模板.md)** - 数据初始化
- **[混合查询-基准模板.md](./混合查询-基准模板.md)** - 混合查询数据准备

### 测试执行

- **[scripts/](./scripts/)** - 测试脚本
- **[pgbench-模板.md](./pgbench-模板.md)** - 测试方法
- **[混合查询-基准模板.md](./混合查询-基准模板.md)** - 混合查询测试

### 监控与分析

- **[sql/benchmark_monitoring.sql](./sql/benchmark_monitoring.sql)** - SQL 监控
- **[tools/monitor_system.sh](./tools/monitor_system.sh)** - 系统监控
- **[tools/analyze_pgbench_log.sh](./tools/analyze_pgbench_log.sh)** - 日志分析
- **[tools/extract_pgbench_metrics.sh](./tools/extract_pgbench_metrics.sh)** - 指标提取

### 结果记录

- **[REPORT_TEMPLATE.md](./REPORT_TEMPLATE.md)** - 报告模板
- **[sql/benchmark_monitoring.sql](./sql/benchmark_monitoring.sql)** - 结果存储

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

详见 [CHANGELOG.md](./CHANGELOG.md)

---

## 💡 使用建议

1. **首次使用**: 从 [QUICK_START.md](./QUICK_START.md) 开始
2. **选择测试**: 根据场景选择对应的基准模板
3. **执行测试**: 使用 scripts/ 中的脚本
4. **监控分析**: 使用 tools/ 和 sql/ 中的工具
5. **记录结果**: 使用 REPORT_TEMPLATE.md 记录

---

**快速开始**: [QUICK_START.md](./QUICK_START.md) | [README.md](./README.md)
