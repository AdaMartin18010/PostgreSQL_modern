---

> **📋 文档来源**: `PostgreSQL\bench\.github\workflows\README.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# CI/CD 集成示例

> **最后更新**: 2025-11-12

---

## 📋 Workflow 文件

### benchmark.yml

GitHub Actions workflow 示例，用于自动化运行基准测试。

**功能**：

- 支持手动触发（workflow_dispatch）
- 支持定时运行（schedule）
- 支持推送触发（push）
- 运行基线 OLTP 基准测试
- 运行混合查询基准测试
- 自动提取指标和分析结果
- 生成测试摘要

**触发方式**：

1. **手动触发**：

   ```yaml
   workflow_dispatch:
     inputs:
       test_type: 'baseline' | 'hybrid' | 'replication'
       scale_factor: '10'
       duration: '300'
       clients: '32'
   ```

2. **定时运行**：

   ```yaml
   schedule:
     - cron: '0 3 * * 0'  # 每周日 UTC 03:00
   ```

3. **推送触发**：

   ```yaml
   push:
     branches: [main]
     paths: ['bench/**']
   ```

---

## 🚀 使用方法

### 1. 手动触发

在 GitHub Actions 页面：

1. 选择 "PostgreSQL Benchmark Tests" workflow
2. 点击 "Run workflow"
3. 选择测试类型和参数
4. 点击 "Run workflow" 按钮

### 2. 定时运行

Workflow 会在每周日 UTC 03:00 自动运行。

### 3. 推送触发

当修改 `bench/` 目录下的文件并推送到 `main` 分支时，会自动触发测试。

---

## 📊 测试结果

### Artifacts

每次运行会生成以下 artifacts：

- **baseline-benchmark-results**: 基线测试结果
  - `baseline_result.log` - pgbench 输出
  - `baseline_metrics.txt` - 提取的指标
  - `latency_analysis.txt` - 延迟分析
  - `pgbench_log.*` - 延迟日志

- **hybrid-benchmark-results**: 混合查询测试结果
  - `hybrid_result.log` - pgbench 输出
  - `hybrid_metrics.txt` - 提取的指标
  - `pgbench_log.*` - 延迟日志

- **benchmark-summary**: 测试摘要
  - `summary.md` - 汇总报告

---

## 🔧 自定义配置

### 修改 PostgreSQL 版本

```yaml
env:
  POSTGRES_VERSION: '18'  # 改为 '17' 或 '16'
```

### 修改测试参数

在 workflow_dispatch 的 inputs 中修改默认值：

```yaml
scale_factor:
  default: '100'  # 修改默认 scale factor
duration:
  default: '600'  # 修改默认测试时长
```

### 添加新的测试场景

在 `jobs` 部分添加新的 job：

```yaml
new-benchmark:
  name: New Benchmark Test
  runs-on: ubuntu-latest
  steps:
    # 添加测试步骤
```

---

## 📚 相关资源

- **基准测试指南**: `../README.md`
- **自动化脚本**: `../tools/run_benchmark_suite.sh`
- **GitHub Actions 文档**: <https://docs.github.com/en/actions>

---

## 💡 最佳实践

1. **定期运行**: 使用 schedule 定期运行，建立性能基线
2. **结果对比**: 对比不同版本的性能差异
3. **告警设置**: 配置性能回归告警
4. **结果归档**: 定期归档测试结果，建立历史记录
