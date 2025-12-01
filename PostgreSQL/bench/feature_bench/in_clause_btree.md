# IN 子句 + B-Tree 优化微基准

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **最后更新**: 2025-11-12

---

## 1. 目标

- 评估 PostgreSQL 17+ 对 B-Tree 上 IN 子句查询的优化收益
- 对比不同 IN 列表大小（10/100/1000）的查询性能
- 测试不同数据分布（均匀/Zipf）下的性能差异
- 评估不同优化器开关和参数的影响

---

## 2. 环境准备

### 2.1 前置条件

- PostgreSQL 17+（17.x 对 IN 子句有重要优化）
- 足够的测试数据（建议 1000万+ 行）
- 监控工具可用

### 2.2 配置检查

```sql
-- 检查相关配置参数
SELECT
    name,
    setting,
    unit,
    context
FROM pg_settings
WHERE name IN (
    'work_mem',
    'enable_bitmapscan',
    'enable_indexscan',
    'enable_seqscan',
    'random_page_cost',
    'cpu_index_tuple_cost'
)
ORDER BY name;
```

---

## 3. 数据准备

### 3.1 创建测试表（均匀分布）

```sql
-- 创建测试表（均匀分布）
CREATE TABLE IF NOT EXISTS test_in_uniform (
    id bigserial PRIMARY KEY,
    key_value int NOT NULL,
    data text,
    created_at timestamptz DEFAULT now()
);

-- 生成均匀分布数据（1000万行）
INSERT INTO test_in_uniform (key_value, data)
SELECT
    (random() * 1000000)::int,
    md5(random()::text)
FROM generate_series(1, 10000000);

-- 创建 B-Tree 索引
CREATE INDEX IF NOT EXISTS idx_test_in_uniform_key ON test_in_uniform(key_value);

-- 更新统计信息
ANALYZE test_in_uniform;
```

### 3.2 创建测试表（Zipf 分布）

```sql
-- 创建测试表（Zipf 分布，模拟热点数据）
CREATE TABLE IF NOT EXISTS test_in_zipf (
    id bigserial PRIMARY KEY,
    key_value int NOT NULL,
    data text,
    created_at timestamptz DEFAULT now()
);

-- 生成 Zipf 分布数据（使用幂律分布）
-- 注意：这里使用简化方法，实际 Zipf 分布需要更复杂的生成逻辑
INSERT INTO test_in_zipf (key_value, data)
SELECT
    (floor(power(random(), 0.5) * 1000000))::int,  -- 简化的幂律分布
    md5(random()::text)
FROM generate_series(1, 10000000);

-- 创建 B-Tree 索引
CREATE INDEX IF NOT EXISTS idx_test_in_zipf_key ON test_in_zipf(key_value);

-- 更新统计信息
ANALYZE test_in_zipf;
```

### 3.3 生成测试查询列表

```sql
-- 生成不同大小的 IN 列表用于测试
-- 小列表（10 个值）
WITH small_list AS (
    SELECT array_agg((random() * 1000000)::int) AS keys
    FROM generate_series(1, 10)
)
SELECT keys FROM small_list;

-- 中等列表（100 个值）
WITH medium_list AS (
    SELECT array_agg((random() * 1000000)::int) AS keys
    FROM generate_series(1, 100)
)
SELECT keys FROM medium_list;

-- 大列表（1000 个值）
WITH large_list AS (
    SELECT array_agg((random() * 1000000)::int) AS keys
    FROM generate_series(1, 1000)
)
SELECT keys FROM large_list;
```

---

## 4. 测试方法

### 4.1 不同 IN 列表大小测试

```sql
-- 测试 1: 小列表（10 个值）
EXPLAIN (ANALYZE, BUFFERS, WAL, SUMMARY, VERBOSE)
SELECT * FROM test_in_uniform
WHERE key_value IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

-- 测试 2: 中等列表（100 个值）
-- 使用数组生成 IN 列表
EXPLAIN (ANALYZE, BUFFERS, WAL, SUMMARY, VERBOSE)
SELECT * FROM test_in_uniform
WHERE key_value = ANY(ARRAY[/* 100 个值 */]);

-- 测试 3: 大列表（1000 个值）
EXPLAIN (ANALYZE, BUFFERS, WAL, SUMMARY, VERBOSE)
SELECT * FROM test_in_uniform
WHERE key_value = ANY(ARRAY[/* 1000 个值 */]);
```

### 4.2 不同优化器开关测试

```sql
-- 测试 1: 启用所有扫描方式（默认）
SET enable_bitmapscan = on;
SET enable_indexscan = on;
SET enable_seqscan = on;
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_in_uniform
WHERE key_value IN (/* 100 个值 */);

-- 测试 2: 禁用位图扫描
SET enable_bitmapscan = off;
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_in_uniform
WHERE key_value IN (/* 100 个值 */);

-- 测试 3: 禁用索引扫描（强制顺序扫描）
SET enable_indexscan = off;
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_in_uniform
WHERE key_value IN (/* 100 个值 */);
```

### 4.3 不同 work_mem 设置测试

```sql
-- 测试 1: 低内存（4MB）
SET work_mem = '4MB';
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_in_uniform
WHERE key_value IN (/* 1000 个值 */);

-- 测试 2: 中等内存（64MB）
SET work_mem = '64MB';
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_in_uniform
WHERE key_value IN (/* 1000 个值 */);

-- 测试 3: 高内存（256MB）
SET work_mem = '256MB';
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_in_uniform
WHERE key_value IN (/* 1000 个值 */);
```

### 4.4 均匀分布 vs Zipf 分布对比

```sql
-- 均匀分布测试
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_in_uniform
WHERE key_value IN (/* 100 个值 */);

-- Zipf 分布测试（热点数据）
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_in_zipf
WHERE key_value IN (/* 100 个值 */);
```

---

## 5. 监控指标

### 5.1 查询计划分析

```sql
-- 详细查询计划
EXPLAIN (ANALYZE, BUFFERS, WAL, SUMMARY, VERBOSE, TIMING, COSTS)
SELECT * FROM test_in_uniform
WHERE key_value IN (/* 测试值列表 */);

-- 关键指标：
-- - Planning Time: 计划时间
-- - Execution Time: 执行时间
-- - Buffers: shared hit/read/dirtied/written
-- - I/O Timings: read/write 时间
```

### 5.2 索引使用统计

```sql
-- 查看索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename LIKE 'test_in%'
ORDER BY idx_scan DESC;
```

### 5.3 查询性能统计

```sql
-- 使用 pg_stat_statements 查看查询统计
SELECT
    queryid,
    calls,
    total_exec_time,
    mean_exec_time,
    stddev_exec_time,
    min_exec_time,
    max_exec_time,
    substring(query, 1, 100) AS query_preview
FROM pg_stat_statements
WHERE query LIKE '%test_in%'
ORDER BY total_exec_time DESC
LIMIT 10;
```

---

## 6. 结果记录

### 6.1 性能指标记录表

| IN 列表大小 | 数据分布 | 执行时间 (ms) | 计划时间 (ms) | 索引扫描 | 位图扫描 | Buffers Hit | Buffers Read | work_mem |
|-----------|---------|--------------|--------------|---------|---------|------------|-------------|----------|
| 10 | 均匀 | | | | | | | 64MB |
| 100 | 均匀 | | | | | | | 64MB |
| 1000 | 均匀 | | | | | | | 64MB |
| 100 | Zipf | | | | | | | 64MB |

### 6.2 优化器开关对比

| 配置 | enable_bitmapscan | enable_indexscan | 执行时间 (ms) | 计划选择 | 备注 |
|------|------------------|-----------------|--------------|---------|------|
| 默认 | on | on | | | |
| 禁用位图 | off | on | | | |
| 禁用索引 | on | off | | | |

### 6.3 记录模板

```markdown
## 测试环境
- **硬件**: CPU型号、内存、存储类型
- **系统**: OS版本、内核版本
- **PostgreSQL版本**: 18.x
- **数据规模**: 行数、表大小、索引大小

## 配置参数
- **work_mem**:
- **enable_bitmapscan**:
- **enable_indexscan**:
- **random_page_cost**:

## 测试结果
- **测试时间**:
- **IN 列表大小**:
- **数据分布**: 均匀 / Zipf
- **执行时间**: Planning=ms, Execution=ms
- **Buffers**: Hit=, Read=, Written=
- **计划选择**: Index Scan / Bitmap Scan / Seq Scan

## 关键发现
-
-

## 优化建议
-
-
```

---

## 7. PostgreSQL 17+ 优化

### 7.1 主要改进

- **IN 子句优化**: 更智能的查询计划选择
- **位图扫描优化**: 改进的位图索引扫描性能
- **成本估算**: 更准确的成本估算模型

### 7.2 优化建议

1. **小列表（< 50）**: 通常使用索引扫描
2. **中等列表（50-500）**: 可能使用位图扫描
3. **大列表（> 500）**: 考虑使用临时表或 JOIN

---

## 8. 性能调优建议

### 8.1 work_mem 调优

- **小列表**: 4-16MB 通常足够
- **中等列表**: 32-64MB 推荐
- **大列表**: 128-256MB 可能需要

### 8.2 查询重写

```sql
-- 如果 IN 列表很大，考虑使用临时表
CREATE TEMP TABLE temp_keys (key_value int);
INSERT INTO temp_keys VALUES (1), (2), (3), /* ... */;

SELECT t.*
FROM test_in_uniform t
JOIN temp_keys k ON t.key_value = k.key_value;
```

### 8.3 索引优化

- 确保索引统计信息是最新的（ANALYZE）
- 考虑部分索引（如果查询有特定条件）
- 对于热点数据，考虑使用覆盖索引

---

## 9. 故障排查

### 9.1 查询慢

- 检查索引是否存在且被使用
- 检查统计信息是否最新
- 检查 work_mem 是否足够
- 检查查询计划是否最优

### 9.2 内存不足

```sql
-- 检查 work_mem 使用情况
SHOW work_mem;

-- 如果出现磁盘排序，考虑增加 work_mem
SET work_mem = '128MB';
```

### 9.3 计划选择不当

```sql
-- 强制使用索引扫描
SET enable_bitmapscan = off;
SET enable_seqscan = off;

-- 查看计划
EXPLAIN SELECT * FROM test_in_uniform WHERE key_value IN (...);
```

---

## 10. 参考资源

- **PostgreSQL 官方文档**: <https://www.postgresql.org/docs/current/indexes-types.html>
- **查询优化**: `../02-查询处理/`
- **索引优化**: `../03-高级特性/`
