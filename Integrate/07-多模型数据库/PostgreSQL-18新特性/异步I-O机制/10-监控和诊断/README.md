# 10. 监控和诊断

> **章节编号**: 10
> **章节标题**: 监控和诊断
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 📑 目录

- [10. 监控和诊断](#10-监控和诊断)
  - [📑 目录](#-目录)
  - [10. 监控和诊断](#10-监控和诊断-1)
    - [10.1 I/O性能监控](#101-io性能监控)
      - [10.1.1 pg\_stat\_io视图](#1011-pg_stat_io视图)
      - [10.1.2 缓存命中率监控](#1012-缓存命中率监控)
      - [10.1.3 实时监控脚本](#1013-实时监控脚本)
    - [10.2 异步I/O监控](#102-异步io监控)
      - [10.2.1 异步I/O使用情况](#1021-异步io使用情况)
      - [10.2.2 I/O并发度监控](#1022-io并发度监控)
    - [10.3 性能指标分析](#103-性能指标分析)
      - [10.3.1 关键性能指标](#1031-关键性能指标)
      - [10.3.2 性能趋势分析](#1032-性能趋势分析)
    - [10.4 诊断工具和方法](#104-诊断工具和方法)
      - [10.4.1 系统级诊断工具](#1041-系统级诊断工具)
      - [10.4.2 PostgreSQL诊断查询](#1042-postgresql诊断查询)
      - [10.4.3 日志分析](#1043-日志分析)
    - [10.5 故障排查案例](#105-故障排查案例)
      - [10.5.1 案例1: 异步I/O未生效](#1051-案例1-异步io未生效)
      - [10.5.2 案例2: I/O延迟过高](#1052-案例2-io延迟过高)
      - [10.5.3 案例3: 系统资源耗尽](#1053-案例3-系统资源耗尽)

---

## 10. 监控和诊断

### 10.1 I/O性能监控

#### 10.1.1 pg_stat_io视图

PostgreSQL 18引入了`pg_stat_io`视图，提供详细的I/O统计信息。

**基本查询**:

```sql
-- 查看I/O统计概览
SELECT
    object,
    context,
    reads,
    writes,
    read_time,
    write_time,
    extends,
    extend_time,
    fsyncs,
    fsync_time
FROM pg_stat_io
ORDER BY reads DESC
LIMIT 20;
```

**按后端类型统计**:

```sql
-- 按后端类型查看I/O统计
SELECT
    backend_type,
    object,
    context,
    SUM(reads) AS total_reads,
    SUM(writes) AS total_writes,
    SUM(read_time) AS total_read_time,
    SUM(write_time) AS total_write_time
FROM pg_stat_io
GROUP BY backend_type, object, context
ORDER BY total_reads DESC;
```

**I/O效率分析**:

```sql
-- 计算平均I/O时间
SELECT
    object,
    context,
    reads,
    read_time,
    CASE
        WHEN reads > 0 THEN ROUND(read_time::numeric / reads, 2)
        ELSE 0
    END AS avg_read_time_ms,
    writes,
    write_time,
    CASE
        WHEN writes > 0 THEN ROUND(write_time::numeric / writes, 2)
        ELSE 0
    END AS avg_write_time_ms
FROM pg_stat_io
WHERE reads > 0 OR writes > 0
ORDER BY (read_time + write_time) DESC;
```

#### 10.1.2 缓存命中率监控

**缓存命中率计算**:

```sql
-- 计算缓存命中率
SELECT
    object,
    context,
    reads,
    hits,
    CASE
        WHEN (reads + hits) > 0 THEN
            ROUND(hits * 100.0 / (reads + hits), 2)
        ELSE 0
    END AS cache_hit_ratio
FROM pg_stat_io
WHERE reads > 0 OR hits > 0
ORDER BY cache_hit_ratio ASC;
```

**整体缓存命中率**:

```sql
-- 整体缓存命中率
SELECT
    SUM(hits) AS total_hits,
    SUM(reads) AS total_reads,
    CASE
        WHEN SUM(reads + hits) > 0 THEN
            ROUND(SUM(hits) * 100.0 / SUM(reads + hits), 2)
        ELSE 0
    END AS overall_cache_hit_ratio
FROM pg_stat_io;
```

#### 10.1.3 实时监控脚本

**实时I/O监控脚本**:

```sql
-- 实时I/O监控（每5秒刷新）
DO $$
DECLARE
    v_reads BIGINT;
    v_writes BIGINT;
    v_read_time NUMERIC;
    v_write_time NUMERIC;
BEGIN
    LOOP
        SELECT
            SUM(reads),
            SUM(writes),
            SUM(read_time),
            SUM(write_time)
        INTO v_reads, v_writes, v_read_time, v_write_time
        FROM pg_stat_io;

        RAISE NOTICE '时间: % | 读取: % | 写入: % | 读时间: % ms | 写时间: % ms',
            NOW(),
            v_reads,
            v_writes,
            ROUND(v_read_time, 2),
            ROUND(v_write_time, 2);

        PERFORM pg_sleep(5);
    END LOOP;
END $$;
```

### 10.2 异步I/O监控

#### 10.2.1 异步I/O使用情况

**检查异步I/O是否启用**:

```sql
-- 检查异步I/O配置
SELECT
    name,
    setting,
    unit,
    context,
    source
FROM pg_settings
WHERE name IN (
    'io_direct',
    'effective_io_concurrency',
    'maintenance_io_concurrency',
    'wal_io_concurrency'
)
ORDER BY name;
```

**监控异步I/O活动**:

```sql
-- 查看等待I/O的进程
SELECT
    pid,
    usename,
    application_name,
    state,
    wait_event_type,
    wait_event,
    query_start,
    state_change
FROM pg_stat_activity
WHERE wait_event_type = 'IO'
ORDER BY query_start;
```

#### 10.2.2 I/O并发度监控

**当前I/O并发度**:

```sql
-- 查看当前I/O并发配置
SELECT
    name,
    setting::INTEGER AS current_value,
    CASE name
        WHEN 'effective_io_concurrency' THEN
            CASE
                WHEN setting::INTEGER < 50 THEN '低（HDD推荐）'
                WHEN setting::INTEGER < 200 THEN '中（SATA SSD推荐）'
                WHEN setting::INTEGER < 300 THEN '高（NVMe SSD推荐）'
                ELSE '非常高（NVMe RAID推荐）'
            END
        ELSE 'N/A'
    END AS recommendation
FROM pg_settings
WHERE name IN (
    'effective_io_concurrency',
    'maintenance_io_concurrency',
    'wal_io_concurrency'
);
```

**I/O队列深度监控**:

```sql
-- 监控I/O队列深度（需要系统级工具）
-- 使用strace或perf工具监控io_uring队列
```

### 10.3 性能指标分析

#### 10.3.1 关键性能指标

**I/O吞吐量**:

```sql
-- 计算I/O吞吐量（MB/s）
SELECT
    object,
    context,
    reads,
    read_time,
    CASE
        WHEN read_time > 0 THEN
            ROUND((reads * 8192.0 / 1024 / 1024) / (read_time / 1000.0), 2)
        ELSE 0
    END AS read_throughput_mbps,
    writes,
    write_time,
    CASE
        WHEN write_time > 0 THEN
            ROUND((writes * 8192.0 / 1024 / 1024) / (write_time / 1000.0), 2)
        ELSE 0
    END AS write_throughput_mbps
FROM pg_stat_io
WHERE reads > 0 OR writes > 0
ORDER BY (read_time + write_time) DESC;
```

**I/O延迟分析**:

```sql
-- I/O延迟分析
SELECT
    object,
    context,
    reads,
    ROUND(AVG(read_time::numeric / NULLIF(reads, 0)), 2) AS avg_read_latency_ms,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY read_time::numeric / NULLIF(reads, 0)) AS p50_read_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY read_time::numeric / NULLIF(reads, 0)) AS p95_read_latency_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY read_time::numeric / NULLIF(reads, 0)) AS p99_read_latency_ms
FROM pg_stat_io
WHERE reads > 0
GROUP BY object, context, reads
ORDER BY avg_read_latency_ms DESC;
```

#### 10.3.2 性能趋势分析

**I/O性能趋势**:

```sql
-- 创建I/O性能历史表（需要定期收集数据）
CREATE TABLE IF NOT EXISTS io_performance_history (
    timestamp TIMESTAMP DEFAULT NOW(),
    object TEXT,
    context TEXT,
    reads BIGINT,
    writes BIGINT,
    read_time NUMERIC,
    write_time NUMERIC
);

-- 定期收集I/O统计
INSERT INTO io_performance_history (object, context, reads, writes, read_time, write_time)
SELECT object, context, reads, writes, read_time, write_time
FROM pg_stat_io;

-- 分析I/O性能趋势
SELECT
    DATE_TRUNC('hour', timestamp) AS hour,
    object,
    context,
    AVG(read_time / NULLIF(reads, 0)) AS avg_read_latency_ms,
    AVG(write_time / NULLIF(writes, 0)) AS avg_write_latency_ms
FROM io_performance_history
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', timestamp), object, context
ORDER BY hour DESC, avg_read_latency_ms DESC;
```

### 10.4 诊断工具和方法

#### 10.4.1 系统级诊断工具

**使用strace监控I/O系统调用**:

```bash
# 监控PostgreSQL进程的I/O系统调用
strace -p $(pgrep -f "postgres.*main") -e trace=read,write,pread64,pwrite64 -f 2>&1 | grep -E "read|write"

# 监控io_uring相关系统调用
strace -p $(pgrep -f "postgres.*main") -e trace=io_uring_setup,io_uring_enter -f
```

**使用perf分析I/O性能**:

```bash
# 记录I/O性能事件
perf record -e syscalls:sys_enter_io_uring_setup,syscalls:sys_enter_io_uring_enter -p $(pgrep -f "postgres.*main")

# 分析性能数据
perf report
```

**使用iostat监控磁盘I/O**:

```bash
# 实时监控磁盘I/O
iostat -x 1

# 监控特定设备
iostat -x /dev/nvme0n1 1
```

#### 10.4.2 PostgreSQL诊断查询

**检查慢查询**:

```sql
-- 查看慢查询（需要启用pg_stat_statements）
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    (shared_blks_hit + shared_blks_read) AS total_blocks,
    shared_blks_hit * 100.0 / NULLIF(shared_blks_hit + shared_blks_read, 0) AS cache_hit_ratio
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- 平均执行时间超过100ms
ORDER BY mean_exec_time DESC
LIMIT 20;
```

**检查I/O等待事件**:

```sql
-- 查看I/O等待事件
SELECT
    wait_event_type,
    wait_event,
    COUNT(*) AS wait_count,
    SUM(EXTRACT(EPOCH FROM (NOW() - state_change))) AS total_wait_seconds
FROM pg_stat_activity
WHERE wait_event_type = 'IO'
GROUP BY wait_event_type, wait_event
ORDER BY total_wait_seconds DESC;
```

#### 10.4.3 日志分析

**检查PostgreSQL日志**:

```bash
# 查看I/O相关日志
grep -i "io\|uring\|async" /var/log/postgresql/postgresql-18-main.log

# 查看错误日志
grep -i "error\|warning" /var/log/postgresql/postgresql-18-main.log | grep -i "io"
```

**检查系统日志**:

```bash
# 查看内核日志中的io_uring信息
dmesg | grep -i "io_uring"

# 查看systemd日志
journalctl -u postgresql@18-main | grep -i "io"
```

### 10.5 故障排查案例

#### 10.5.1 案例1: 异步I/O未生效

**问题描述**:

用户配置了`io_direct = 'data'`，但性能提升不明显。

**诊断步骤**:

```sql
-- 1. 检查配置
SHOW io_direct;  -- 'data'
SHOW effective_io_concurrency;  -- 1 (默认值，太低)

-- 2. 检查I/O统计
SELECT * FROM pg_stat_io;
-- 发现I/O并发度很低

-- 3. 检查系统支持
SELECT version();  -- PostgreSQL 18.1
```

**解决方案**:

```sql
-- 设置合适的I/O并发数
ALTER SYSTEM SET effective_io_concurrency = 200;
SELECT pg_reload_conf();

-- 验证
SHOW effective_io_concurrency;  -- 200
```

**结果**:

- 性能提升200%
- I/O吞吐量从500 MB/s提升至1500 MB/s

#### 10.5.2 案例2: I/O延迟过高

**问题描述**:

异步I/O启用后，I/O延迟仍然很高。

**诊断步骤**:

```sql
-- 1. 检查I/O延迟
SELECT
    object,
    context,
    reads,
    read_time,
    ROUND(read_time::numeric / NULLIF(reads, 0), 2) AS avg_read_latency_ms
FROM pg_stat_io
WHERE reads > 0
ORDER BY avg_read_latency_ms DESC;
-- 发现平均读取延迟 > 10ms

-- 2. 检查存储类型
-- 发现使用的是HDD而非SSD
```

**根本原因**:

- HDD本身是瓶颈，异步I/O对HDD提升有限
- I/O并发数设置过高，导致I/O竞争

**解决方案**:

```sql
-- 1. 降低I/O并发数（适合HDD）
ALTER SYSTEM SET effective_io_concurrency = 50;

-- 2. 考虑升级到SSD
```

#### 10.5.3 案例3: 系统资源耗尽

**问题描述**:

启用异步I/O后，系统内存和文件描述符耗尽。

**诊断步骤**:

```bash
# 1. 检查文件描述符使用
lsof -p $(pgrep -f "postgres.*main") | wc -l

# 2. 检查内存使用
ps aux | grep postgres

# 3. 检查系统限制
ulimit -n
```

**解决方案**:

```sql
-- 1. 降低I/O并发数
ALTER SYSTEM SET effective_io_concurrency = 100;

-- 2. 降低队列深度（如果支持）
-- ALTER SYSTEM SET io_uring_queue_depth = 128;
```

```bash
# 3. 增加系统限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf
```

---

**返回**: [文档首页](../README.md) | [上一章节](../09-最佳实践/README.md) | [下一章节](../11-迁移指南/README.md)
