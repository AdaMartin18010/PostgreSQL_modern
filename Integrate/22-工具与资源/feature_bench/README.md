---

> **📋 文档来源**: `PostgreSQL\bench\feature_bench\README.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# Feature Benchmarks (PostgreSQL 17+)

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **最后更新**: 2025-11-12

---

## 📋 基准列表

本目录包含针对 PostgreSQL 17+ 新特性的微基准测试方法。

### 已完成的基准

1. **[vacuum_memory_throughput.md](./vacuum_memory_throughput.md)** - VACUUM 内存/吞吐微基准
   - 观察 PostgreSQL 17+ 对 VACUUM 内存占用与吞吐改进的影响
   - 对比不同 `maintenance_work_mem` 设置下的性能
   - 评估 VACUUM 对系统资源的影响

2. **[in_clause_btree.md](./in_clause_btree.md)** - IN 子句 + B-Tree 优化微基准
   - 评估 PostgreSQL 17+ 对 B-Tree 上 IN 子句查询的优化收益
   - 对比不同 IN 列表大小的查询性能
   - 测试不同数据分布（均匀/Zipf）下的性能差异

3. **[brin_parallel_build.md](./brin_parallel_build.md)** - BRIN 并行构建微基准
   - 对比串行/并行构建 BRIN 索引的时间与资源使用
   - 评估不同 `pages_per_range` 设置对构建性能的影响
   - 测试分区表上的 BRIN 索引构建性能

---

## 🎯 通用测试流程

### 1. 环境准备

- 记录硬件配置（CPU、内存、存储）
- 记录 PostgreSQL 版本和配置参数
- 准备测试数据

### 2. 基线测试

- 运行标准测试脚本
- 记录关键指标（时延、吞吐、IO、WAL）
- 监控系统资源（CPU、内存、IO）

### 3. 参数调优

- 调整 PostgreSQL 配置参数
- 测试不同参数组合
- 对比性能变化

### 4. 结果分析

- 对比不同配置的性能差异
- 识别性能瓶颈
- 提出优化建议

---

## 📊 观测建议

### 配置记录

记录以下配置参数：

- **shared_buffers**: 共享缓冲区大小
- **work_mem**: 工作内存
- **maintenance_work_mem**: 维护工作内存
- **WAL 相关**: wal_level、max_wal_size 等
- **并行相关**: max_parallel_workers、max_parallel_maintenance_workers 等

### 数据规模

记录：

- **行数**: 表的总行数
- **表大小**: 表的总大小（GB）
- **索引大小**: 索引的总大小（GB）
- **数据分布**: 均匀分布、Zipf 分布等

### 关键指标

使用以下工具收集指标：

- **EXPLAIN (ANALYZE, BUFFERS, WAL, SUMMARY)**: 查询计划分析
- **pg_stat_io**: IO 统计（PostgreSQL 17+）
- **pg_stat_statements**: 查询性能统计
- **系统监控**: sar、iostat、top 等

---

## 🔧 通用工具与命令

### 查询计划分析

```sql
-- 详细查询计划
EXPLAIN (ANALYZE, BUFFERS, WAL, SUMMARY, VERBOSE, TIMING, COSTS)
SELECT ...;

-- 关键指标：
-- - Planning Time: 计划时间
-- - Execution Time: 执行时间
-- - Buffers: shared hit/read/dirtied/written
-- - I/O Timings: read/write 时间
```

### IO 统计（PostgreSQL 17+）

```sql
-- 查看 IO 统计
SELECT
    object,
    context,
    reads,
    writes,
    extends,
    fsyncs,
    op_bytes,
    reads * op_bytes AS total_bytes_read,
    writes * op_bytes AS total_bytes_written
FROM pg_stat_io
WHERE object = 'relation'
ORDER BY total_bytes_written DESC;
```

### 查询性能统计

```sql
-- 启用 pg_stat_statements（如未启用）
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查看慢查询
SELECT
    queryid,
    calls,
    total_exec_time,
    mean_exec_time,
    stddev_exec_time,
    substring(query, 1, 100) AS query_preview
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

### 系统资源监控

```bash
# CPU 和内存监控
sar -u 1 300 > cpu.log &
sar -r 1 300 > memory.log &

# IO 监控
iostat -x 1 300 > io.log &

# PostgreSQL 进程监控
top -p $(pgrep -f postgres) -b -n 300 > process.log &
```

---

## 📝 结果记录模板

### 测试环境

```markdown
- **硬件**: CPU型号、内存、存储类型
- **系统**: OS版本、内核版本
- **PostgreSQL版本**: 18.x
- **数据规模**: 行数、表大小、索引大小
```

### 配置参数

```markdown
- **shared_buffers**:
- **work_mem**:
- **maintenance_work_mem**:
- **max_parallel_workers**:
- **其他相关参数**:
```

### 测试结果

```markdown
- **测试时间**:
- **测试场景**:
- **执行时间**: Planning=ms, Execution=ms
- **Buffers**: Hit=, Read=, Written=
- **IO 统计**: 读取=MB, 写入=MB
- **系统资源**: CPU=%, Memory=%, IO=MB/s
```

### 关键发现与建议

```markdown
## 关键发现
-
-

## 优化建议
-
-
```

---

## 🚀 快速开始

### 1. 选择基准

根据要测试的特性选择合适的基准文档。

### 2. 准备环境

按照基准文档中的"环境准备"部分设置测试环境。

### 3. 运行测试

按照基准文档中的"测试方法"部分执行测试。

### 4. 记录结果

使用"结果记录"部分的模板记录测试结果。

---

## 📚 相关资源

- **主基准模板**: `../README.md`
- **pgbench 模板**: `../pgbench-模板.md`
- **混合查询基准**: `../混合查询-基准模板.md`
- **PostgreSQL 官方文档**: <https://www.postgresql.org/docs/current/>

---

## 💡 最佳实践

1. **建立基线**: 在优化前先建立性能基线
2. **单变量测试**: 每次只改变一个参数，便于对比
3. **多次运行**: 运行多次测试取平均值，减少波动影响
4. **记录环境**: 详细记录测试环境，确保可复现
5. **监控资源**: 同时监控系统资源，避免瓶颈转移
6. **版本对比**: 对比不同 PostgreSQL 版本的性能差异
