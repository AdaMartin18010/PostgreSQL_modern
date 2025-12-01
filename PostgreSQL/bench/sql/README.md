# 基准测试 SQL 脚本

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **最后更新**: 2025-11-12

---

## 📋 脚本列表

### benchmark_monitoring.sql

基准测试监控 SQL 脚本，用于在基准测试期间收集性能指标。

**功能**：

- 测试前系统状态检查
- 测试期间实时监控
- 测试后性能分析
- 基准测试结果对比

**使用方法**：

```sql
-- 测试前：检查系统状态
\i benchmark_monitoring.sql

-- 测试期间：定期执行监控查询（第 2 节）

-- 测试后：分析性能指标（第 3 节）
```

**主要查询**：

1. 系统配置概览
2. 数据库大小和对象统计
3. 活跃连接和查询监控
4. 缓存命中率
5. 索引使用统计
6. 慢查询分析
7. IO 统计（PostgreSQL 17+）
8. 等待事件统计

---

## 🚀 快速使用

### 1. 测试前准备

```sql
-- 连接到测试数据库
\c pgbench_test

-- 执行测试前检查
\i benchmark_monitoring.sql
```

### 2. 测试期间监控

在测试运行期间，定期执行以下查询：

```sql
-- 查看当前活跃连接
SELECT pid, state, query_start, LEFT(query, 100) AS query
FROM pg_stat_activity
WHERE state != 'idle';

-- 查看缓存命中率
SELECT round(100.0 * sum(blks_hit) / NULLIF(sum(blks_hit) + sum(blks_read), 0), 2) AS buffer_hit_ratio
FROM pg_stat_database
WHERE datname = current_database();
```

### 3. 测试后分析

```sql
-- 查看慢查询
SELECT queryid, calls, mean_exec_time, LEFT(query, 100) AS query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 查看表扫描统计
SELECT tablename, seq_scan, idx_scan
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY seq_scan DESC;
```

---

## 📊 结果记录

### 使用基准测试结果表

```sql
-- 创建结果表（如果不存在）
\i benchmark_monitoring.sql

-- 插入测试结果
INSERT INTO benchmark_results (
    test_name, tps, avg_latency_ms, tp50_ms, tp95_ms, tp99_ms,
    connection_count, buffer_hit_ratio, notes
) VALUES (
    'baseline_test',
    412.567,
    77.234,
    65.12,
    123.45,
    189.23,
    32,
    98.5,
    'Baseline test with default configuration'
);

-- 查看历史结果
SELECT * FROM benchmark_results ORDER BY test_time DESC;
```

---

## 🔗 相关资源

- **主基准模板**: `../README.md`
- **监控文档**: `../../04-部署运维/04.04-监控与诊断.md`
- **SQL 监控脚本**: `../../sql/monitoring_dashboard.sql`
