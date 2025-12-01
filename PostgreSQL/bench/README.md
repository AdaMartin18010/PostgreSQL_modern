# Bench 基准模板索引

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **最后更新**: 2025-11-12
> **快速导航**: [INDEX.md](./INDEX.md) | [QUICK_START.md](./QUICK_START.md) ⭐

---

## 📋 模板列表

### 基础压测

- **[pgbench-模板.md](./pgbench-模板.md)** - 标准 pgbench 压测模板
  - 初始化测试数据
  - 基线性能测试
  - 自定义脚本压测
  - 结果记录与对比

### 专项基准

- **[混合查询-基准模板.md](./混合查询-基准模板.md)** ⭐ - 混合查询性能基准
  - 全文搜索 + 向量搜索组合
  - RRF 融合查询
  - 加权融合查询
  - 结构化过滤 + 混合查询
  - 索引参数调优（HNSW/IVFFlat）
  - 并发度测试

- **[复制延迟-基准模板.md](./复制延迟-基准模板.md)** - 主从复制延迟测试
  - 写负载下的复制延迟测量
  - byte_lag / time_lag 监控
  - RPO 影响评估
  - 同步策略对比

### 特性基准

- **[feature_bench/](./feature_bench/)** - PostgreSQL 17+ 特性微基准
  - `vacuum_memory_throughput.md` - VACUUM 内存吞吐测试
  - `in_clause_btree.md` - IN 子句 B-tree 优化测试
  - `brin_parallel_build.md` - BRIN 并行构建测试

### 测试脚本

- **[scripts/](./scripts/)** - 实际可用的测试脚本
  - `mix_basic.sql` - 基础混合查询脚本
  - `mix_rrf.sql` - RRF 融合查询脚本
  - `mix_weighted.sql` - 加权融合查询脚本
  - `mix_filtered.sql` - 结构化过滤+混合查询脚本
  - 详见 [scripts/README.md](./scripts/README.md)

### 辅助工具

- **[tools/](./tools/)** - 基准测试辅助工具
  - `analyze_pgbench_log.sh/.ps1` - 分析 pgbench 日志，提取延迟分位数
  - `monitor_system.sh` - 系统资源监控脚本
  - `extract_pgbench_metrics.sh/.ps1` - 从 pgbench 输出提取关键指标
  - `run_benchmark_suite.sh/.ps1` - 自动化测试套件脚本
  - `baseline_manager.sh` - 性能基线管理脚本
  - 详见 [tools/README.md](./tools/README.md)

### 配置文件

- **[config/](./config/)** - 基准测试配置文件
  - `benchmark_config.example.json` - 配置文件示例
  - `benchmark_config.dev.json` - 开发环境配置
  - `benchmark_config.prod.json` - 生产环境配置
  - 详见 [config/README.md](./config/README.md)

### CI/CD 集成

- **[.github/workflows/](./.github/workflows/)** - GitHub Actions 工作流
  - `benchmark.yml` - 自动化基准测试工作流
  - 详见 [.github/workflows/README.md](./.github/workflows/README.md)

### Docker 环境

- **[docker-compose.yml](./docker-compose.yml)** - Docker Compose 测试环境配置
  - 快速搭建 PostgreSQL 测试环境
  - 支持版本对比测试
  - 详见 [docker-compose.README.md](./docker-compose.README.md)

### SQL 监控脚本

- **[sql/](./sql/)** - 基准测试 SQL 监控脚本
  - `benchmark_monitoring.sql` - 基准测试期间性能监控和指标收集
  - 详见 [sql/README.md](./sql/README.md)

---

## 🚀 快速开始

> **新手推荐**: 先阅读 [QUICK_START.md](./QUICK_START.md) 进行 5 分钟快速体验

### 1. 选择模板

根据测试目标选择合适的基准模板：

- **通用 OLTP 性能** → `pgbench-模板.md`
- **混合搜索性能** → `混合查询-基准模板.md`
- **复制延迟** → `复制延迟-基准模板.md`
- **新特性验证** → `feature_bench/`

### 2. 准备环境

```bash
# 确保 PostgreSQL 已安装并运行
pg_isready

# 安装 pgbench（通常包含在 postgresql-contrib 中）
# Ubuntu/Debian
sudo apt-get install postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-contrib
```

### 3. 运行测试

按照模板中的步骤执行测试，记录关键指标。

---

## 📊 通用测试流程

### 1. 环境准备

- 记录硬件配置（CPU、内存、存储）
- 记录 PostgreSQL 版本和配置参数
- 准备测试数据

### 2. 基线测试

- 运行标准测试脚本
- 记录 TPS、延迟分位（TP50/TP95/TP99）
- 监控系统资源（CPU、内存、IO）

### 3. 参数调优

- 调整 PostgreSQL 配置参数
- 测试不同索引参数
- 对比性能变化

### 4. 结果分析

- 对比不同配置的性能差异
- 识别性能瓶颈
- 提出优化建议

---

## 📈 关键指标

### 性能指标

- **TPS (Transactions Per Second)**: 每秒事务数
- **延迟分位**: TP50、TP95、TP99
- **平均延迟**: 平均响应时间
- **吞吐量**: 每秒处理的查询数

### 系统资源

- **CPU 使用率**: 平均和峰值
- **内存使用**: 峰值和趋势
- **IO 吞吐**: 读写 IOPS 和带宽
- **网络带宽**: 如适用

### PostgreSQL 指标

- **连接数**: 活跃连接和峰值
- **缓存命中率**: shared_buffers 命中率
- **索引使用**: 索引扫描统计
- **WAL 生成**: WAL 写入速率

---

## 🔧 工具与命令

### pgbench

```bash
# 初始化测试数据（scale factor = 10）
pgbench -i -s 10 postgres

# 标准压测（32 并发，300 秒）
pgbench -c 32 -j 32 -T 300 postgres

# 自定义脚本压测
pgbench -c 32 -j 32 -T 300 -f custom.sql postgres

# 只读测试
pgbench -S -c 32 -j 32 -T 300 postgres
```

### 系统监控

```bash
# CPU 和内存监控
sar -u 1 300 > cpu.log &
sar -r 1 300 > memory.log &

# IO 监控
iostat -x 1 300 > io.log &

# PostgreSQL 统计
psql -c "SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"
```

### 查询分析

```sql
-- 启用 pg_stat_statements（如未启用）
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查看慢查询
SELECT queryid, calls, mean_exec_time, query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 分析查询计划
EXPLAIN (ANALYZE, BUFFERS, WAL, SUMMARY)
SELECT ...;
```

---

## 📝 结果记录模板

### 测试环境

```markdown
- **硬件**: CPU型号、内存、存储类型
- **系统**: OS版本、内核版本
- **PostgreSQL版本**: 18.x
- **数据规模**: 表大小、索引大小
```

### 配置参数

```markdown
- **shared_buffers**:
- **work_mem**:
- **maintenance_work_mem**:
- **effective_cache_size**:
- **max_connections**:
```

### 测试结果

```markdown
- **测试时间**:
- **测试脚本**:
- **TPS**:
- **延迟分位**: TP50=, TP95=, TP99=
- **系统资源**: CPU=%, Memory=%, IO=MB/s
```

---

## 🔗 相关资源

- **SQL 示例**: `../sql/vector_examples.sql`
- **落地指南**: `../runbook/04-向量检索与混合查询-落地指南.md`
- **AI 时代专题**: `../05-前沿技术/AI-时代/01-向量与混合搜索-pgvector与RRF.md`
- **PostgreSQL 官方文档**: <https://www.postgresql.org/docs/current/pgbench.html>

---

## 💡 最佳实践

1. **建立基线**: 在优化前先建立性能基线
2. **单变量测试**: 每次只改变一个参数，便于对比
3. **多次运行**: 运行多次测试取平均值，减少波动影响
4. **记录环境**: 详细记录测试环境，确保可复现
5. **监控资源**: 同时监控系统资源，避免瓶颈转移
6. **回归测试**: 定期运行基准测试，监控性能趋势

---

## 📚 扩展阅读

### 快速开始

- **[QUICK_START.md](./QUICK_START.md)** - 5 分钟快速体验指南 ⭐
- **[INDEX.md](./INDEX.md)** - 完整文档索引
- **[REPORT_TEMPLATE.md](./REPORT_TEMPLATE.md)** - 测试报告模板
- **[BEST_PRACTICES.md](./BEST_PRACTICES.md)** - 最佳实践指南 ⭐
- **[FAQ.md](./FAQ.md)** - 常见问题解答
- **[CHANGELOG.md](./CHANGELOG.md)** - 更新日志

### 相关文档

- [PostgreSQL 性能调优指南](../04-部署运维/)
- [向量检索性能调优](../05-前沿技术/05.05-向量检索性能调优指南.md)
- [查询优化最佳实践](../02-查询处理/)
