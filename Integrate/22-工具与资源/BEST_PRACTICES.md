---

> **📋 文档来源**: `PostgreSQL\bench\BEST_PRACTICES.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 基准测试最佳实践

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **最后更新**: 2025-11-12

---

## 📋 概述

本文档总结了 PostgreSQL 基准测试的最佳实践，帮助您获得准确、可复现、有意义的测试结果。

---

## 🎯 测试前准备

### 1. 环境一致性

**原则**: 确保测试环境的一致性，避免外部因素干扰。

**实践**：

- ✅ 使用相同的硬件配置
- ✅ 使用相同的 PostgreSQL 版本和编译选项
- ✅ 使用相同的操作系统和内核版本
- ✅ 确保测试期间没有其他负载
- ✅ 关闭不必要的后台服务

**检查清单**：

```bash
# 检查系统负载
uptime

# 检查运行的服务
systemctl list-units --type=service --state=running

# 检查 PostgreSQL 版本
psql --version

# 检查系统资源
free -h
df -h
```

### 2. 数据准备

**原则**: 使用真实的数据规模和分布。

**实践**：

- ✅ 根据实际生产环境选择 scale factor
- ✅ 使用真实的数据分布（如 Zipf 分布）
- ✅ 确保数据已预热到缓存
- ✅ 运行 ANALYZE 更新统计信息

**示例**：

```bash
# 初始化数据
pgbench -i -s 100 pgbench_test

# 预热缓存
pgbench -c 8 -j 8 -T 60 pgbench_test

# 更新统计信息
psql -d pgbench_test -c "ANALYZE;"
```

### 3. 配置记录

**原则**: 完整记录所有配置信息，便于复现和对比。

**实践**：

- ✅ 记录 PostgreSQL 版本和编译选项
- ✅ 记录所有配置参数（postgresql.conf）
- ✅ 记录系统配置（CPU、内存、存储）
- ✅ 记录测试参数（并发数、持续时间等）

**工具**：

```sql
-- 记录 PostgreSQL 配置
SELECT name, setting, unit, context
FROM pg_settings
WHERE context IN ('postmaster', 'sighup', 'superuser')
ORDER BY name;
```

---

## 🔬 测试执行

### 1. 预热阶段

**原则**: 测试前先预热，确保缓存已填充。

**实践**：

- ✅ 运行短时间的预热测试（不记录结果）
- ✅ 预热时间至少 30-60 秒
- ✅ 使用与实际测试相同的并发数

**示例**：

```bash
# 预热（不记录结果）
pgbench -c 32 -j 32 -T 60 pgbench_test

# 正式测试
pgbench -c 32 -j 32 -T 300 -r -l pgbench_test > result.log 2>&1
```

### 2. 测试时长

**原则**: 测试时长要足够长，以获得稳定的结果。

**实践**：

- ✅ 至少运行 5 分钟（300 秒）
- ✅ 对于性能对比，建议运行 10-15 分钟
- ✅ 多次运行取平均值（至少 3 次）

**建议**：

| 测试类型 | 最小时长 | 推荐时长 |
|---------|---------|---------|
| 快速验证 | 60 秒 | 120 秒 |
| 性能对比 | 300 秒 | 600 秒 |
| 稳定性测试 | 1800 秒 | 3600 秒 |

### 3. 并发数选择

**原则**: 选择与实际生产环境相近的并发数。

**实践**：

- ✅ 从低并发开始，逐步增加
- ✅ 测试多个并发级别（8, 16, 32, 64, 128）
- ✅ 观察性能拐点（TPS 不再增加或开始下降）

**示例**：

```bash
# 测试不同并发级别
for clients in 8 16 32 64 128; do
    pgbench -c $clients -j $clients -T 300 -r pgbench_test > result_c${clients}.log 2>&1
done
```

### 4. 监控和记录

**原则**: 同时监控系统和数据库指标。

**实践**：

- ✅ 启动系统监控（CPU、内存、I/O）
- ✅ 记录 pgbench 输出和延迟日志
- ✅ 使用 SQL 监控脚本收集数据库指标
- ✅ 记录所有输出到文件

**示例**：

```bash
# 启动系统监控
cd tools
./monitor_system.sh 300 test_run &

# 运行测试并记录
pgbench -c 32 -j 32 -T 300 -r -l pgbench_test > result.log 2>&1

# 等待监控完成
wait
```

---

## 📊 结果分析

### 1. 指标提取

**原则**: 提取关键指标，便于对比和分析。

**实践**：

- ✅ 提取 TPS、延迟、错误率等关键指标
- ✅ 分析延迟分布（P50、P95、P99）
- ✅ 对比系统资源使用情况

**工具**：

```bash
# 提取指标
./tools/extract_pgbench_metrics.sh result.log

# 分析延迟
./tools/analyze_pgbench_log.sh pgbench_log.*
```

### 2. 结果验证

**原则**: 验证结果的合理性和一致性。

**实践**：

- ✅ 检查是否有错误或异常
- ✅ 对比多次运行的结果（差异应 < 5%）
- ✅ 检查系统资源是否成为瓶颈
- ✅ 验证延迟分布是否合理

**检查清单**：

- [ ] 错误率为 0 或接近 0
- [ ] 多次运行 TPS 差异 < 5%
- [ ] CPU 使用率 < 80%（避免成为瓶颈）
- [ ] 内存使用稳定
- [ ] I/O 等待时间合理

### 3. 对比分析

**原则**: 使用相同的方法和参数进行对比。

**实践**：

- ✅ 使用相同的测试参数
- ✅ 使用相同的测试数据规模
- ✅ 在相同的环境下运行
- ✅ 使用对比工具进行量化分析

**工具**：

```bash
# 对比两个结果
./tools/compare_results.sh result1.log result2.log "Before" "After"
```

---

## 🔧 性能调优

### 1. 参数调优

**原则**: 一次只调整少量参数，验证效果。

**实践**：

- ✅ 记录基线配置
- ✅ 一次调整 1-2 个参数
- ✅ 运行测试验证效果
- ✅ 记录调优前后的对比

**关键参数**：

```sql
-- 内存参数
shared_buffers = 256MB              -- 系统内存的 25%
effective_cache_size = 1GB          -- 系统内存的 75%
work_mem = 4MB                      -- 根据并发数调整
maintenance_work_mem = 64MB

-- 检查点参数
checkpoint_completion_target = 0.9
max_wal_size = 1GB

-- 并发参数
max_connections = 200
max_parallel_workers = 8
```

### 2. 索引优化

**原则**: 根据查询模式创建合适的索引。

**实践**：

- ✅ 分析查询计划（EXPLAIN (ANALYZE, BUFFERS, TIMING)）
- ✅ 创建必要的索引
- ✅ 定期维护索引（REINDEX）
- ✅ 监控索引使用情况

**检查**：

```sql
-- 检查索引使用情况
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### 3. 查询优化

**原则**: 优化慢查询，提升整体性能。

**实践**：

- ✅ 使用 pg_stat_statements 找出慢查询
- ✅ 分析执行计划
- ✅ 重写查询或添加提示
- ✅ 验证优化效果

---

## 📝 文档和报告

### 1. 测试记录

**原则**: 详细记录测试过程，便于复现和审查。

**实践**：

- ✅ 使用测试报告模板
- ✅ 记录所有配置和参数
- ✅ 保存原始输出和日志
- ✅ 记录异常和问题

**模板**：

使用 [REPORT_TEMPLATE.md](./REPORT_TEMPLATE.md) 记录测试结果。

### 2. 结果归档

**原则**: 建立性能基线库，跟踪性能趋势。

**实践**：

- ✅ 定期运行基准测试
- ✅ 归档测试结果
- ✅ 建立性能基线
- ✅ 监控性能回归

---

## ⚠️ 常见陷阱

### 1. 测试环境不一致

**问题**: 在不同环境下运行测试，结果不可比。

**解决**: 确保测试环境的一致性。

### 2. 测试时间过短

**问题**: 测试时间太短，结果不稳定。

**解决**: 至少运行 5 分钟，多次运行取平均值。

### 3. 未预热缓存

**问题**: 第一次运行结果偏低，因为缓存未填充。

**解决**: 测试前先运行预热。

### 4. 系统资源瓶颈

**问题**: 系统资源成为瓶颈，无法反映数据库真实性能。

**解决**: 监控系统资源，确保有足够余量。

### 5. 配置参数不合理

**问题**: 配置参数不合理，影响测试结果。

**解决**: 根据系统资源合理配置参数。

---

## 🎓 进阶技巧

### 1. 自动化测试

使用自动化脚本批量运行测试：

```bash
./tools/run_benchmark_suite.sh pgbench_test
```

### 2. CI/CD 集成

集成到 CI/CD 流程，定期运行测试：

```yaml
# .github/workflows/benchmark.yml
```

### 3. Docker 环境

使用 Docker 快速搭建测试环境：

```bash
docker-compose up -d
```

---

## 🚀 PostgreSQL 18 优化最佳实践

### 1. 异步I/O优化

**PostgreSQL 18新特性**: 异步I/O可以显著提升批量操作的性能。

**最佳实践**：

```sql
-- 启用异步I/O
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET wal_io_concurrency = 200;
SELECT pg_reload_conf();

-- 性能提升：批量导入速度提升40%
```

**适用场景**：

- ✅ 批量数据导入
- ✅ 大规模VACUUM操作
- ✅ 备份和恢复操作
- ✅ WAL写入密集型工作负载

**注意事项**：

- ⚠️ 需要Linux内核支持io_uring
- ⚠️ 需要足够的I/O并发能力
- ⚠️ 监控I/O等待时间

### 2. 并行查询优化

**PostgreSQL 18增强**: 并行查询性能进一步提升。

**最佳实践**：

```sql
-- 配置并行查询参数
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;
SELECT pg_reload_conf();

-- 性能提升：聚合查询性能提升55%
```

**适用场景**：

- ✅ 大规模聚合查询
- ✅ 复杂JOIN查询
- ✅ 排序和分组操作
- ✅ 并行索引构建

**注意事项**：

- ⚠️ 需要足够的CPU核心数
- ⚠️ 需要足够的work_mem
- ⚠️ 小数据集可能不适合并行

### 3. Skip Scan优化

**PostgreSQL 18新特性**: Skip Scan可以优化稀疏条件查询。

**最佳实践**：

```sql
-- Skip Scan自动优化，无需额外配置
-- 查询稀疏条件时自动使用

-- 示例：优化前需要扫描大量行
SELECT * FROM products
WHERE status = 'active' AND category = 'electronics'
ORDER BY sales_count DESC
LIMIT 100;

-- 优化后：自动使用Skip Scan，性能提升60%
```

**适用场景**：

- ✅ 稀疏条件查询
- ✅ 多列索引查询
- ✅ 部分索引查询

### 4. 并行索引构建

**PostgreSQL 18增强**: 支持更多索引类型的并行构建。

**最佳实践**：

```sql
-- 并行构建GIN索引
CREATE INDEX CONCURRENTLY idx_documents_search
ON documents USING GIN (search_vector)
WITH (parallel_workers = 4);

-- 查看构建进度
SELECT
    pid,
    phase,
    tuples_total,
    tuples_done,
    ROUND(100.0 * tuples_done / NULLIF(tuples_total, 0), 2) AS progress_pct
FROM pg_stat_progress_create_index
WHERE relid = 'documents'::regclass;

-- 性能提升：索引构建速度提升60%
```

**适用场景**：

- ✅ 大规模索引构建
- ✅ GIN索引构建
- ✅ GiST索引构建
- ✅ 维护窗口期索引重建

### 5. 监控和诊断

**PostgreSQL 18增强**: 增强的监控和诊断功能。

**最佳实践**：

```sql
-- 查看内存使用情况（PostgreSQL 18新功能）
SELECT
    name,
    type,
    pg_size_pretty(used_bytes) AS used,
    pg_size_pretty(total_bytes) AS total,
    ROUND(100.0 * used_bytes / NULLIF(total_bytes, 0), 2) AS usage_pct
FROM pg_backend_memory_contexts
WHERE used_bytes > 10 * 1024 * 1024  -- >10MB
ORDER BY used_bytes DESC;

-- 查看I/O统计（PostgreSQL 18增强）
SELECT
    datname,
    blks_read,
    blks_hit,
    temp_files,
    pg_size_pretty(temp_bytes) AS temp_size,
    blk_read_time,
    blk_write_time
FROM pg_stat_database
WHERE datname = current_database();
```

---

## 📚 相关资源

- **快速开始**: [QUICK_START.md](./QUICK_START.md)
- **报告模板**: [REPORT_TEMPLATE.md](./REPORT_TEMPLATE.md)
- **工具说明**: [tools/README.md](./tools/README.md)
- **性能调优**: [性能调优实践](../11-部署架构/单机部署/05.02-性能调优实践.md)

---

**💡 记住**: 基准测试的目标是获得准确、可复现、有意义的性能数据，而不是追求最高的数字。
