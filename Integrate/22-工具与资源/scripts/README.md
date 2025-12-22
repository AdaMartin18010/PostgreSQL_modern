---

> **📋 文档来源**: `PostgreSQL\bench\scripts\README.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 基准测试脚本

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **pgvector版本**: 2.0 ⭐ | 0.7+
> **最后更新**: 2025-11-12

---

## 📋 脚本列表

### 混合查询脚本

这些脚本用于测试混合查询（全文搜索 + 向量搜索）的性能。

1. **mix_basic.sql** - 基础混合查询
   - 全文搜索筛选候选集
   - 向量搜索精排
   - 适合快速性能测试

2. **mix_rrf.sql** - RRF 融合查询
   - 使用 Reciprocal Rank Fusion 算法
   - 自动融合多路召回结果
   - 无需调参

3. **mix_weighted.sql** - 加权融合查询
   - 向量权重 60%，全文权重 40%
   - 可调整权重比例
   - 适合需要精确控制权重的场景

4. **mix_filtered.sql** - 结构化过滤 + 混合查询
   - 先应用结构化过滤（时间、分类等）
   - 再进行全文和向量搜索
   - 适合生产环境场景

---

## 🚀 使用方法

### 前置条件

1. 确保已创建测试表 `docs`，包含以下字段：
   - `id` (bigint)
   - `text` (text)
   - `embedding` (vector)
   - `category` (text, 可选)
   - `created_at` (timestamptz, 可选)

2. 已创建索引：
   - 全文索引：`CREATE INDEX ON docs USING gin (to_tsvector('simple', text));`
   - 向量索引：`CREATE INDEX ON docs USING hnsw (embedding vector_l2_ops);`

3. 已准备测试数据（建议 100万+ 文档）

### 运行测试

```bash
# 基础混合查询测试
pgbench -c 32 -j 32 -T 300 -f mix_basic.sql postgres

# RRF 融合查询测试
pgbench -c 32 -j 32 -T 300 -f mix_rrf.sql postgres

# 加权融合查询测试
pgbench -c 32 -j 32 -T 300 -f mix_weighted.sql postgres

# 结构化过滤 + 混合查询测试
pgbench -c 32 -j 32 -T 300 -f mix_filtered.sql postgres
```

### 参数说明

- `-c`: 客户端连接数（并发数）
- `-j`: 工作线程数（建议等于 CPU 核心数）
- `-T`: 测试持续时间（秒）
- `-r`: 报告每个语句的平均延迟（可选）
- `-l`: 记录每个事务的延迟到日志文件（可选）

### 示例：完整测试流程

```bash
# 1. 预热测试（不记录结果）
pgbench -c 32 -j 32 -T 60 -f mix_basic.sql postgres

# 2. 正式测试（记录结果）
pgbench -c 32 -j 32 -T 300 -r -l -f mix_basic.sql postgres > result_basic.log 2>&1

# 3. 对比测试
pgbench -c 32 -j 32 -T 300 -r -l -f mix_rrf.sql postgres > result_rrf.log 2>&1
```

---

## 📊 结果分析

### 查看 pgbench 输出

```bash
# 查看测试结果
cat result_basic.log

# 关键指标：
# - tps: 每秒事务数
# - latency average: 平均延迟
# - latency stddev: 延迟标准差
```

### 分析延迟日志

```bash
# 如果使用了 -l 选项，可以分析延迟分布
# 提取延迟值并计算分位数
awk '{print $NF}' pgbench_log.* | sort -n | \
  awk '{
    a[NR]=$1
  }
  END{
    print "TP50:", a[int(NR*0.5)]
    print "TP95:", a[int(NR*0.95)]
    print "TP99:", a[int(NR*0.99)]
  }'
```

---

## 🔧 自定义脚本

### 修改查询参数

脚本中使用 `\set` 命令设置变量：

```sql
\set qv random(1, 1000)      -- 查询向量 ID（随机）
\set kw random(1, 5)         -- 关键词索引（随机）
\set keyword :kw             -- 实际关键词
\set query_vector :qv        -- 实际查询向量 ID
```

可以根据实际数据调整这些参数的范围。

### 调整权重

在 `mix_weighted.sql` 中，可以调整权重：

```sql
-- 向量权重 60%，全文权重 40%
0.6 * (1.0 / (dist + 0.001)) + 0.4 * tr AS combined_score

-- 修改为向量权重 70%，全文权重 30%
0.7 * (1.0 / (dist + 0.001)) + 0.3 * tr AS combined_score
```

### 调整候选集大小

```sql
-- 全文搜索 LIMIT（默认 500）
ORDER BY tr DESC LIMIT 500

-- 向量搜索 LIMIT（默认 100）
ORDER BY dist ASC LIMIT 100
```

---

## 📚 相关文档

- **混合查询基准模板**: `../混合查询-基准模板.md`
- **SQL 示例**: `../../sql/vector_examples.sql`
- **落地指南**: `../../runbook/04-向量检索与混合查询-落地指南.md`

---

## ⚠️ 注意事项

1. **数据准备**：确保测试数据已准备充分，索引已创建
2. **资源监控**：测试时同时监控系统资源（CPU、内存、IO）
3. **多次运行**：建议多次运行取平均值，减少波动影响
4. **预热测试**：正式测试前先运行预热，确保缓存已加载
5. **环境隔离**：确保测试环境不受其他负载干扰
