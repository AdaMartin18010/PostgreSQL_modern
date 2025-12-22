---

> **📋 文档来源**: `PostgreSQL\bench\feature_bench\vacuum_memory_throughput.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# VACUUM 内存/吞吐微基准

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **最后更新**: 2025-11-12

---

## 1. 目标

- 观察 PostgreSQL 17+ 对 VACUUM 内存占用与吞吐改进的影响
- 对比不同 `maintenance_work_mem` 设置下的 VACUUM 性能
- 评估 VACUUM 对系统资源（CPU、内存、IO）的影响
- 测试不同数据规模下的 VACUUM 性能

---

## 2. 环境准备

### 2.1 前置条件

- PostgreSQL 17+（17.x 对 VACUUM 有重要改进）
- 足够的测试数据（建议 1000万+ 行）
- 监控工具可用（sar、iostat、pg_stat_io）

### 2.2 配置检查

```sql
-- 检查相关配置参数
SELECT
    name,
    setting,
    unit,
    context,
    source
FROM pg_settings
WHERE name IN (
    'maintenance_work_mem',
    'autovacuum_work_mem',
    'shared_buffers',
    'work_mem',
    'autovacuum',
    'autovacuum_max_workers',
    'wal_level',
    'max_wal_size'
)
ORDER BY name;
```

---

## 3. 数据准备

### 3.1 创建测试表

```sql
-- 创建测试表（模拟热点更新场景）
CREATE TABLE IF NOT EXISTS test_vacuum (
    id bigserial PRIMARY KEY,
    data text NOT NULL,
    status int DEFAULT 0,
    updated_at timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_test_vacuum_status ON test_vacuum(status);
CREATE INDEX IF NOT EXISTS idx_test_vacuum_updated ON test_vacuum(updated_at);
```

### 3.2 生成测试数据

```sql
-- 生成初始数据（1000万行）
INSERT INTO test_vacuum (data, status)
SELECT
    md5(random()::text),
    (random() * 10)::int
FROM generate_series(1, 10000000);

-- 更新统计信息
ANALYZE test_vacuum;
```

### 3.3 模拟热点更新

```sql
-- 模拟频繁更新（产生死元组）
-- 运行多次以产生足够的死元组
DO $$
DECLARE
    i int;
BEGIN
    FOR i IN 1..1000 LOOP
        UPDATE test_vacuum
        SET status = (random() * 10)::int,
            updated_at = now(),
            data = md5(random()::text)
        WHERE id IN (
            SELECT id FROM test_vacuum
            ORDER BY random()
            LIMIT 10000
        );
        COMMIT;
    END LOOP;
END $$;
```

### 3.4 检查死元组

```sql
-- 检查死元组数量
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    n_dead_tup::float / NULLIF(n_live_tup + n_dead_tup, 0) * 100 AS dead_tuple_pct,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE tablename = 'test_vacuum';
```

---

## 4. 测试方法

### 4.1 不同内存配置测试

```sql
-- 测试 1: 低内存配置（256MB）
SET maintenance_work_mem = '256MB';
VACUUM VERBOSE ANALYZE test_vacuum;

-- 测试 2: 中等内存配置（1GB）
SET maintenance_work_mem = '1GB';
VACUUM VERBOSE ANALYZE test_vacuum;

-- 测试 3: 高内存配置（4GB）
SET maintenance_work_mem = '4GB';
VACUUM VERBOSE ANALYZE test_vacuum;
```

### 4.2 VACUUM vs VACUUM FULL

```sql
-- 普通 VACUUM（不锁表）
VACUUM VERBOSE ANALYZE test_vacuum;

-- VACUUM FULL（需要锁表，但回收更多空间）
VACUUM FULL VERBOSE ANALYZE test_vacuum;
```

### 4.3 监控 VACUUM 执行

```sql
-- 查看当前 VACUUM 进程
SELECT
    pid,
    usename,
    datname,
    state,
    query,
    query_start,
    now() - query_start AS duration
FROM pg_stat_activity
WHERE query LIKE '%VACUUM%'
ORDER BY query_start;
```

---

## 5. 监控指标

### 5.1 VACUUM 性能指标

```sql
-- 使用 EXPLAIN 分析 VACUUM（PostgreSQL 17+）
EXPLAIN (ANALYZE, BUFFERS, WAL, SUMMARY, VERBOSE)
VACUUM ANALYZE test_vacuum;

-- 查看 VACUUM 统计（需要启用 track_io_timing）
SELECT
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count,
    n_dead_tup,
    n_live_tup
FROM pg_stat_user_tables
WHERE tablename = 'test_vacuum';
```

### 5.2 IO 统计（PostgreSQL 17+）

```sql
-- 查看 IO 统计（需要启用 pg_stat_io）
SELECT
    object,
    context,
    reads,
    writes,
    extends,
    fsyncs,
    op_bytes,
    evictions,
    reuses,
    fsyncs * op_bytes AS total_bytes_written
FROM pg_stat_io
WHERE object = 'relation'
ORDER BY total_bytes_written DESC;
```

### 5.3 系统资源监控

```bash
# 监控 CPU 和内存
sar -u 1 300 > vacuum_cpu.log &
sar -r 1 300 > vacuum_memory.log &

# 监控 IO
iostat -x 1 300 > vacuum_io.log &

# 监控 PostgreSQL 进程
top -p $(pgrep -f "postgres.*vacuum") -b -n 300 > vacuum_process.log &
```

### 5.4 表大小变化

```sql
-- 查看表大小变化（VACUUM 前后对比）
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE tablename = 'test_vacuum';
```

---

## 6. 结果记录

### 6.1 性能指标记录表

| 配置 | maintenance_work_mem | VACUUM 耗时 (s) | 回收死元组数 | IO 读取 (MB) | IO 写入 (MB) | 内存峰值 (MB) | 表大小变化 (MB) |
|------|---------------------|----------------|------------|-------------|-------------|--------------|---------------|
| 低内存 | 256MB | | | | | | |
| 中等内存 | 1GB | | | | | | |
| 高内存 | 4GB | | | | | | |
| VACUUM FULL | 4GB | | | | | | |

### 6.2 不同数据规模测试

| 数据规模 | 行数 | 表大小 (GB) | VACUUM 耗时 (s) | 回收空间 (MB) | 吞吐 (MB/s) |
|---------|------|------------|----------------|-------------|------------|
| 小规模 | 100万 | | | | |
| 中规模 | 1000万 | | | | |
| 大规模 | 1亿 | | | | |

### 6.3 记录模板

```markdown
## 测试环境
- **硬件**: CPU型号、内存、存储类型
- **系统**: OS版本、内核版本
- **PostgreSQL版本**: 18.x
- **数据规模**: 行数、表大小、索引大小

## 配置参数
- **maintenance_work_mem**:
- **autovacuum_work_mem**:
- **shared_buffers**:
- **max_wal_size**:

## 测试结果
- **测试时间**:
- **VACUUM 类型**: VACUUM / VACUUM FULL
- **执行耗时**:
- **回收死元组数**:
- **IO 统计**: 读取=MB, 写入=MB
- **内存使用**: 峰值=MB
- **表大小变化**: 前=GB, 后=GB, 回收=MB

## 关键发现
-
-

## 优化建议
-
-
```

---

## 7. 性能调优建议

### 7.1 内存配置

- **maintenance_work_mem**: 建议设置为系统内存的 5-10%，但不超过 4GB
- **autovacuum_work_mem**: 如果单独设置，建议与 `maintenance_work_mem` 相同
- **权衡**: 内存越大，VACUUM 越快，但可能影响其他操作

### 7.2 VACUUM 策略

- **普通 VACUUM**: 适合日常维护，不锁表
- **VACUUM FULL**: 适合需要回收大量空间时，但需要锁表
- **定期 VACUUM**: 根据死元组比例决定频率

### 7.3 自动 VACUUM 调优

```sql
-- 调整自动 VACUUM 参数
ALTER TABLE test_vacuum SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05,
    autovacuum_vacuum_cost_delay = 10,
    autovacuum_vacuum_cost_limit = 200
);
```

---

## 8. PostgreSQL 17+ 改进

### 8.1 主要改进

- **并行 VACUUM**: 支持并行处理多个索引
- **IO 统计增强**: `pg_stat_io` 提供更详细的 IO 信息
- **内存优化**: 更高效的内存使用
- **性能提升**: 整体 VACUUM 性能提升

### 8.2 新特性使用

```sql
-- 并行 VACUUM（PostgreSQL 17+）
VACUUM (PARALLEL 4) VERBOSE ANALYZE test_vacuum;

-- 查看并行 VACUUM 进度
SELECT * FROM pg_stat_progress_vacuum;
```

---

## 9. 故障排查

### 9.1 VACUUM 慢

- 检查死元组数量是否过多
- 检查 IO 性能
- 检查是否有锁冲突
- 考虑增加 `maintenance_work_mem`

### 9.2 内存不足

- 减少 `maintenance_work_mem`
- 分批处理大表
- 使用 `VACUUM (INDEX_CLEANUP false)` 跳过索引清理

### 9.3 锁冲突

```sql
-- 检查锁等待
SELECT
    blocked_locks.pid AS blocked_pid,
    blocking_locks.pid AS blocking_pid,
    blocked_activity.query AS blocked_query,
    blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

---

## 10. 参考资源

- **PostgreSQL 官方文档**: <https://www.postgresql.org/docs/current/sql-vacuum.html>
- **VACUUM 调优指南**: `../04-部署运维/`
- **性能监控**: `../sql/monitoring_dashboard.sql`
