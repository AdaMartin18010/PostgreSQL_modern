---

> **📋 文档来源**: `PostgreSQL\bench\feature_bench\brin_parallel_build.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# BRIN 并行构建微基准

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **最后更新**: 2025-11-12

---

## 1. 目标

- 对比串行/并行构建 BRIN 索引的时间与资源使用
- 评估不同 `pages_per_range` 设置对构建性能的影响
- 测试不同数据规模（数十 GB+）下的构建性能
- 评估分区表上的 BRIN 索引构建性能

---

## 2. 环境准备

### 2.1 前置条件

- PostgreSQL 17+（17.x 支持 BRIN 并行构建）
- 足够的测试数据（建议 数十 GB+）
- 监控工具可用（sar、iostat）

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
    'maintenance_work_mem',
    'max_parallel_maintenance_workers',
    'max_parallel_workers_per_gather',
    'max_worker_processes'
)
ORDER BY name;
```

---

## 3. 数据准备

### 3.1 创建非分区表

```sql
-- 创建大表（时间序列数据）
CREATE TABLE IF NOT EXISTS test_brin_large (
    id bigserial,
    timestamp_col timestamptz NOT NULL,
    value_col numeric(10,2),
    data_col text,
    created_at timestamptz DEFAULT now()
);

-- 生成测试数据（1 亿行，约 30-50 GB）
INSERT INTO test_brin_large (timestamp_col, value_col, data_col)
SELECT
    now() - (random() * interval '365 days'),
    (random() * 10000)::numeric(10,2),
    md5(random()::text)
FROM generate_series(1, 100000000);

-- 更新统计信息
ANALYZE test_brin_large;
```

### 3.2 创建分区表

```sql
-- 创建分区表（按月分区）
CREATE TABLE IF NOT EXISTS test_brin_partitioned (
    id bigserial,
    timestamp_col timestamptz NOT NULL,
    value_col numeric(10,2),
    data_col text,
    created_at timestamptz DEFAULT now()
) PARTITION BY RANGE (timestamp_col);

-- 创建分区（12 个月）
DO $$
DECLARE
    month_start date;
    month_end date;
    partition_name text;
BEGIN
    FOR i IN 0..11 LOOP
        month_start := date '2024-01-01' + (i || ' months')::interval;
        month_end := month_start + '1 month'::interval;
        partition_name := 'test_brin_partitioned_' || to_char(month_start, 'YYYY_MM');

        EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF test_brin_partitioned
                        FOR VALUES FROM (%L) TO (%L)',
                        partition_name, month_start, month_end);
    END LOOP;
END $$;

-- 生成测试数据
INSERT INTO test_brin_partitioned (timestamp_col, value_col, data_col)
SELECT
    '2024-01-01'::date + (random() * 365)::int * interval '1 day',
    (random() * 10000)::numeric(10,2),
    md5(random()::text)
FROM generate_series(1, 100000000);

-- 更新统计信息
ANALYZE test_brin_partitioned;
```

---

## 4. 测试方法

### 4.1 串行构建 BRIN 索引

```sql
-- 测试 1: 默认 pages_per_range (128)
CREATE INDEX CONCURRENTLY idx_test_brin_serial_128
ON test_brin_large USING brin (timestamp_col)
WITH (pages_per_range = 128);

-- 测试 2: 较大 pages_per_range (256)
DROP INDEX IF EXISTS idx_test_brin_serial_128;
CREATE INDEX CONCURRENTLY idx_test_brin_serial_256
ON test_brin_large USING brin (timestamp_col)
WITH (pages_per_range = 256);

-- 测试 3: 较小 pages_per_range (64)
DROP INDEX IF EXISTS idx_test_brin_serial_256;
CREATE INDEX CONCURRENTLY idx_test_brin_serial_64
ON test_brin_large USING brin (timestamp_col)
WITH (pages_per_range = 64);
```

### 4.2 并行构建 BRIN 索引（PostgreSQL 17+）

```sql
-- 测试 1: 并行度 2
CREATE INDEX CONCURRENTLY idx_test_brin_parallel_2
ON test_brin_large USING brin (timestamp_col)
WITH (pages_per_range = 128);

-- 设置并行度
SET max_parallel_maintenance_workers = 2;

-- 重新构建（需要先删除）
DROP INDEX IF EXISTS idx_test_brin_parallel_2;
CREATE INDEX CONCURRENTLY idx_test_brin_parallel_2
ON test_brin_large USING brin (timestamp_col)
WITH (pages_per_range = 128);

-- 测试 2: 并行度 4
SET max_parallel_maintenance_workers = 4;
DROP INDEX IF EXISTS idx_test_brin_parallel_2;
CREATE INDEX CONCURRENTLY idx_test_brin_parallel_4
ON test_brin_large USING brin (timestamp_col)
WITH (pages_per_range = 128);

-- 测试 3: 并行度 8
SET max_parallel_maintenance_workers = 8;
DROP INDEX IF EXISTS idx_test_brin_parallel_4;
CREATE INDEX CONCURRENTLY idx_test_brin_parallel_8
ON test_brin_large USING brin (timestamp_col)
WITH (pages_per_range = 128);
```

### 4.3 分区表上的 BRIN 索引

```sql
-- 在分区表上构建 BRIN 索引
CREATE INDEX CONCURRENTLY idx_test_brin_partitioned
ON test_brin_partitioned USING brin (timestamp_col)
WITH (pages_per_range = 128);
```

### 4.4 监控索引构建进度

```sql
-- 查看索引构建进度（PostgreSQL 17+）
SELECT
    pid,
    datname,
    relid::regclass AS relation,
    phase,
    blocks_total,
    blocks_done,
    tuples_total,
    tuples_done,
    partitions_total,
    partitions_done
FROM pg_stat_progress_create_index
WHERE relid = 'test_brin_large'::regclass;
```

---

## 5. 监控指标

### 5.1 构建时间监控

```sql
-- 记录构建开始时间
SELECT now() AS build_start;

-- 执行 CREATE INDEX

-- 记录构建结束时间
SELECT now() AS build_end;

-- 计算构建耗时
SELECT
    build_end - build_start AS build_duration;
```

### 5.2 系统资源监控

```bash
# 监控 CPU 和内存
sar -u 1 300 > brin_cpu.log &
sar -r 1 300 > brin_memory.log &

# 监控 IO
iostat -x 1 300 > brin_io.log &

# 监控 PostgreSQL 进程
top -p $(pgrep -f "postgres.*CREATE INDEX") -b -n 300 > brin_process.log &
```

### 5.3 索引大小对比

```sql
-- 查看索引大小
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexname LIKE 'idx_test_brin%'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 5.4 IO 统计（PostgreSQL 17+）

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

---

## 6. 结果记录

### 6.1 性能指标记录表

| 构建方式 | pages_per_range | 并行度 | 构建时间 (s) | IO 读取 (MB) | IO 写入 (MB) | CPU (%) | 索引大小 (MB) |
|---------|----------------|--------|-------------|-------------|-------------|---------|--------------|
| 串行 | 64 | 1 | | | | | |
| 串行 | 128 | 1 | | | | | |
| 串行 | 256 | 1 | | | | | |
| 并行 | 128 | 2 | | | | | |
| 并行 | 128 | 4 | | | | | |
| 并行 | 128 | 8 | | | | | |

### 6.2 不同数据规模测试

| 数据规模 | 行数 | 表大小 (GB) | 串行构建 (s) | 并行构建 (s) | 加速比 | 并行度 |
|---------|------|------------|-------------|-------------|--------|--------|
| 小规模 | 1000万 | | | | | 4 |
| 中规模 | 1亿 | | | | | 4 |
| 大规模 | 10亿 | | | | | 4 |

### 6.3 分区表测试

| 分区数 | 总行数 | 串行构建 (s) | 并行构建 (s) | 加速比 | 并行度 |
|--------|--------|-------------|-------------|--------|--------|
| 12 | 1亿 | | | | 4 |

### 6.4 记录模板

```markdown
## 测试环境
- **硬件**: CPU型号、内存、存储类型
- **系统**: OS版本、内核版本
- **PostgreSQL版本**: 18.x
- **数据规模**: 行数、表大小、分区数

## 配置参数
- **maintenance_work_mem**:
- **max_parallel_maintenance_workers**:
- **max_parallel_workers_per_gather**:

## 测试结果
- **测试时间**:
- **构建方式**: 串行 / 并行
- **并行度**:
- **pages_per_range**:
- **构建耗时**:
- **IO 统计**: 读取=MB, 写入=MB
- **CPU 使用**: 平均=%, 峰值=%
- **索引大小**: MB

## 关键发现
-
-

## 优化建议
-
-
```

---

## 7. 性能调优建议

### 7.1 pages_per_range 选择

- **小值（32-64）**: 索引更精确，但索引更大，构建更慢
- **默认值（128）**: 平衡精度和性能
- **大值（256-512）**: 索引更小，构建更快，但精度降低

### 7.2 并行度选择

- **小表（< 10GB）**: 并行度 2-4 通常足够
- **中表（10-100GB）**: 并行度 4-8 推荐
- **大表（> 100GB）**: 并行度 8-16 可能有益

### 7.3 maintenance_work_mem

- 建议设置为系统内存的 5-10%
- 并行构建时，每个工作进程都会使用 `maintenance_work_mem`
- 总内存使用 = `maintenance_work_mem * (1 + 并行度)`

---

## 8. PostgreSQL 17+ 改进

### 8.1 主要改进

- **并行构建**: 支持并行构建 BRIN 索引
- **进度监控**: `pg_stat_progress_create_index` 提供详细进度
- **性能提升**: 大表上构建速度显著提升

### 8.2 使用建议

```sql
-- 对于大表，使用并行构建
SET max_parallel_maintenance_workers = 4;
CREATE INDEX CONCURRENTLY idx_large_brin
ON large_table USING brin (timestamp_col);

-- 监控构建进度
SELECT * FROM pg_stat_progress_create_index;
```

---

## 9. 故障排查

### 9.1 构建慢

- 检查 IO 性能
- 检查是否有锁冲突
- 考虑增加并行度
- 考虑增加 `maintenance_work_mem`

### 9.2 内存不足

```sql
-- 减少并行度或 maintenance_work_mem
SET max_parallel_maintenance_workers = 2;
SET maintenance_work_mem = '512MB';
```

### 9.3 锁冲突

```sql
-- 使用 CONCURRENTLY 选项避免锁表
CREATE INDEX CONCURRENTLY idx_test_brin
ON test_brin_large USING brin (timestamp_col);
```

---

## 10. 参考资源

- **PostgreSQL 官方文档**: <https://www.postgresql.org/docs/current/brin.html>
- **索引优化**: `../03-高级特性/`
- **分区表**: `../03-高级特性/`
