# 基准测试辅助工具

> **最后更新**: 2025-11-12

---

## 📋 工具列表

### 1. analyze_pgbench_log.sh / analyze_pgbench_log.ps1

分析 pgbench 日志文件，提取延迟分位数。

**功能**：

- 计算 TP50、TP95、TP99、TP99.9
- 计算平均延迟、最小延迟、最大延迟
- 支持分析多个日志文件

**使用方法**：

```bash
# 赋予执行权限
chmod +x analyze_pgbench_log.sh

# 分析单个文件
./analyze_pgbench_log.sh pgbench_log.1234

# 分析多个文件
./analyze_pgbench_log.sh pgbench_log.*
```

**输出示例**：

```text
=== pgbench 日志分析 ===

文件: pgbench_log.1234
----------------------------------------
总事务数: 10000
平均延迟: 45.23 ms
最小延迟: 12.34 ms
最大延迟: 234.56 ms
TP50: 42.10 ms
TP95: 78.90 ms
TP99: 123.45 ms
TP99.9: 189.23 ms
```

---

### 2. monitor_system.sh

系统资源监控脚本，在测试期间监控 CPU、内存、IO、网络等资源。

**功能**：

- CPU 使用率监控（sar）
- 内存使用监控（sar）
- IO 监控（iostat）
- 网络监控（sar）
- PostgreSQL 进程监控（top）

**使用方法**：

```bash
# 赋予执行权限
chmod +x monitor_system.sh

# 监控 300 秒（默认）
./monitor_system.sh 300

# 指定输出文件前缀
./monitor_system.sh 300 my_test

# 在后台运行（配合测试）
./monitor_system.sh 300 test_run &
```

**输出文件**：

- `{prefix}_cpu.log` - CPU 使用率
- `{prefix}_memory.log` - 内存使用
- `{prefix}_io.log` - IO 统计
- `{prefix}_network.log` - 网络统计
- `{prefix}_postgres.log` - PostgreSQL 进程信息

---

### 3. extract_pgbench_metrics.sh / extract_pgbench_metrics.ps1

从 pgbench 输出中提取关键指标。

**功能**：

- 提取 TPS（每秒事务数）
- 提取平均延迟
- 提取延迟标准差
- 提取事务总数
- 提取连接时间
- 生成 CSV 格式输出

**使用方法**：

**Linux/macOS (bash)**：

```bash
# 赋予执行权限
chmod +x extract_pgbench_metrics.sh

# 提取指标
./extract_pgbench_metrics.sh result.log

# 保存到 CSV 文件
./extract_pgbench_metrics.sh result.log > metrics.csv
```

**Windows (PowerShell)**：

```powershell
# 提取指标
.\extract_pgbench_metrics.ps1 -InputFile "result.log"

# 保存到 CSV 文件
.\extract_pgbench_metrics.ps1 -InputFile "result.log" | Out-File -FilePath "metrics.csv" -Encoding utf8
```

**输出示例**：

```text
=== pgbench 指标提取 ===
文件: result.log
----------------------------------------
TPS: 412.567
平均延迟: 77.234 ms
延迟标准差: 12.456 ms
事务数: 123456
连接时间: 45.123 ms

=== CSV 格式 ===
TPS,平均延迟(ms),延迟标准差(ms),事务数,连接时间(ms)
412.567,77.234,12.456,123456,45.123
```

---

### 4. run_benchmark_suite.sh / run_benchmark_suite.ps1

自动化基准测试套件，批量运行多个测试场景。

**功能**：

- 自动初始化测试数据
- 批量运行多个测试场景（基线、只读、只写）
- 自动启动系统监控
- 自动分析结果
- 生成摘要报告

**使用方法**：

**Linux/macOS (bash)**：

```bash
# 赋予执行权限
chmod +x run_benchmark_suite.sh

# 使用默认配置运行
./run_benchmark_suite.sh pgbench_test

# 使用环境变量自定义配置
SCALE_FACTOR=100 DURATION=300 CLIENTS=32 ./run_benchmark_suite.sh pgbench_test

# 指定输出目录
OUTPUT_DIR=./my_results ./run_benchmark_suite.sh pgbench_test
```

**Windows (PowerShell)**：

```powershell
# 使用默认配置运行
.\run_benchmark_suite.ps1 -DatabaseName "pgbench_test"

# 自定义配置
.\run_benchmark_suite.ps1 -DatabaseName "pgbench_test" `
    -ScaleFactor 100 `
    -Duration 300 `
    -Clients 32 `
    -OutputDir ".\my_results"
```

**输出**：

- `baseline.log` - 基线测试结果
- `readonly.log` - 只读测试结果
- `writeonly.log` - 只写测试结果
- `latency_analysis.txt` - 延迟分析
- `*_metrics.txt` - 各测试的指标
- `summary.txt` - 测试摘要
- `system_*.log` - 系统监控数据

---

### 5. compare_results.sh

性能对比脚本，用于对比两个测试结果。

**功能**：

- 提取两个测试结果的关键指标
- 计算性能差异百分比
- 彩色输出对比结果
- 支持自定义标签

**使用方法**：

```bash
# 赋予执行权限
chmod +x compare_results.sh

# 对比两个测试结果
./compare_results.sh result1.log result2.log "Before" "After"

# 对比版本性能
./compare_results.sh pg18_result.log pg17_result.log "PostgreSQL 18" "PostgreSQL 17"
```

**输出示例**：

```text
==========================================
性能对比报告
==========================================

指标                  Test 1         Test 2           差异
------------------------------------------
TPS                   412.567       450.123        +9.10%
平均延迟(ms)           77.234        68.456         -11.36%
==========================================
```

**注意事项**：

- 需要安装 `bc` 命令（用于计算）
- 确保两个结果文件格式一致
- 颜色输出在终端中显示，重定向到文件时可能不显示

---

### 6. baseline_manager.sh

性能基线管理脚本，用于保存、对比和管理性能基线。

**功能**：

- 保存测试结果为基线
- 列出所有已保存的基线
- 显示基线详细信息
- 对比两个基线
- 对比最新结果与基线
- 删除基线

**使用方法**：

```bash
# 赋予执行权限
chmod +x baseline_manager.sh

# 保存基线
./baseline_manager.sh save baseline_v1 result.log

# 列出所有基线
./baseline_manager.sh list

# 显示基线信息
./baseline_manager.sh show baseline_v1

# 对比两个基线
./baseline_manager.sh compare baseline_v1 baseline_v2

# 对比最新结果与基线
./baseline_manager.sh compare-latest baseline_v1

# 删除基线
./baseline_manager.sh delete baseline_v1
```

**基线存储结构**：

```text
baselines/
└── baseline_v1/
    ├── metadata.json          # 元数据（创建时间、版本等）
    ├── metrics.txt           # 性能指标
    ├── result.log            # 原始测试结果
    ├── latency_analysis.txt  # 延迟分析（如果有）
    └── pgbench_log.*         # 延迟日志（如果有）
```

**使用场景**：

1. **建立性能基线**: 保存初始性能数据作为参考
2. **版本对比**: 对比不同 PostgreSQL 版本的性能
3. **配置对比**: 对比不同配置参数的性能影响
4. **回归检测**: 检测性能是否退化

---

## 🚀 使用示例

### 完整测试流程

```bash
# 1. 启动系统监控（后台运行）
cd tools
./monitor_system.sh 300 test_run &

# 2. 运行 pgbench 测试
cd ..
pgbench -c 32 -j 32 -T 300 -r -l postgres > result.log 2>&1

# 3. 提取关键指标
cd tools
./extract_pgbench_metrics.sh ../result.log > metrics.csv

# 4. 分析延迟日志
./analyze_pgbench_log.sh ../pgbench_log.* > latency_analysis.txt

# 5. 查看监控结果
cat test_run_cpu.log
cat test_run_memory.log
cat test_run_io.log
```

### 批量测试分析

```bash
# 分析多个测试结果
for result in result_*.log; do
    echo "=== $result ===" >> summary.txt
    ./extract_pgbench_metrics.sh "$result" >> summary.txt
    echo "" >> summary.txt
done
```

---

## 📊 工具依赖

### 必需工具

- **bash**: 所有脚本都需要 bash 环境
- **awk**: 用于数据处理
- **grep**: 用于文本搜索
- **sort**: 用于排序

### 可选工具（monitor_system.sh）

- **sar**: 系统活动报告（sysstat 包）
- **iostat**: IO 统计（sysstat 包）
- **top**: 进程监控

**安装依赖**（Ubuntu/Debian）：

```bash
sudo apt-get install sysstat
```

**安装依赖**（CentOS/RHEL）：

```bash
sudo yum install sysstat
```

---

## 💡 使用建议

1. **测试前准备**：
   - 确保所有工具已安装
   - 赋予脚本执行权限：`chmod +x *.sh`
   - 创建输出目录用于保存结果

2. **测试期间**：
   - 在测试开始前启动监控脚本
   - 使用 `-l` 选项让 pgbench 记录延迟日志
   - 将输出重定向到文件以便后续分析

3. **测试后分析**：
   - 使用 `extract_pgbench_metrics.sh` 提取关键指标
   - 使用 `analyze_pgbench_log.sh` 分析延迟分布
   - 查看监控日志了解系统资源使用情况

---

## 🔧 自定义和扩展

### 修改监控间隔

编辑 `monitor_system.sh`，修改采样间隔：

```bash
sar -u 1 ${DURATION}  # 1 秒间隔
sar -u 5 ${DURATION}  # 5 秒间隔
```

### 添加自定义指标

在 `extract_pgbench_metrics.sh` 中添加新的指标提取：

```bash
# 提取新指标
new_metric=$(grep "pattern" "$INPUT_FILE" | awk '{print $N}')
```

### 集成到 CI/CD

可以将这些脚本集成到 CI/CD 流程中：

```yaml
- name: Run Benchmark
  run: |
    pgbench -c 32 -j 32 -T 300 -r -l postgres > result.log

- name: Extract Metrics
  run: |
    cd bench/tools
    ./extract_pgbench_metrics.sh ../result.log > metrics.csv
```

---

## 📚 相关资源

- **pgbench 文档**: `../pgbench-模板.md`
- **基准测试指南**: `../README.md`
- **PostgreSQL 官方文档**: <https://www.postgresql.org/docs/current/pgbench.html>
