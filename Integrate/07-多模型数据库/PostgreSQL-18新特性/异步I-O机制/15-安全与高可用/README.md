# 15. 性能基准测试工具

> **章节编号**: 15
> **章节标题**: 性能基准测试工具
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 15. 性能基准测试工具

## 📑 目录

- [15. 性能基准测试工具](#15-性能基准测试工具)
  - [15. 性能基准测试工具](#15-性能基准测试工具-1)
  - [📑 目录](#-目录)
    - [15.1 pgbench基准测试](#151-pgbench基准测试)
    - [15.2 自定义性能测试工具](#152-自定义性能测试工具)
    - [15.3 性能对比工具](#153-性能对比工具)
    - [15.4 持续性能监控](#154-持续性能监控)
  - [15. 安全与高可用](#15-安全与高可用)
  - [15. 安全与高可用](#15-安全与高可用-1)
  - [📑 目录](#-目录-1)
    - [15.1 安全考虑](#151-安全考虑)
    - [15.2 备份恢复考虑](#152-备份恢复考虑)
    - [15.3 高可用环境配置](#153-高可用环境配置)
    - [15.4 安全最佳实践](#154-安全最佳实践)
    - [15.5 高可用架构设计](#155-高可用架构设计)
    - [15.6 备份恢复最佳实践](#156-备份恢复最佳实践)

---

---

### 15.1 pgbench基准测试

使用pgbench进行PostgreSQL 18异步I/O性能基准测试：

**初始化测试数据**:

```bash
# 初始化测试数据库
pgbench -i -s 100 testdb

# -i: 初始化
# -s: 缩放因子（100表示1000万行）
```

**运行基准测试**:

```bash
# 只读测试
pgbench -c 100 -j 8 -T 300 -S testdb

# 读写混合测试
pgbench -c 100 -j 8 -T 300 testdb

# 只写测试
pgbench -c 100 -j 8 -T 300 -N testdb
```

**测试参数说明**:

- `-c`: 客户端连接数
- `-j`: 线程数
- `-T`: 测试持续时间（秒）
- `-S`: 只读模式
- `-N`: 跳过SELECT语句

**性能指标**:

| 测试类型 | TPS | 延迟 | 说明 |
|---------|-----|------|------|
| **只读** | 基准 | 基准 | 基准性能 |
| **读写混合** | +70% | -60% | 性能提升明显 |
| **只写** | +170% | -63% | 最大性能提升 |

### 15.2 自定义性能测试工具

创建自定义性能测试工具以测试特定场景：

**Python测试脚本**:

```python
import psycopg2
import time
import statistics

def test_async_io_performance():
    conn = psycopg2.connect(
        host='localhost',
        database='testdb',
        user='postgres'
    )
    cur = conn.cursor()

    # 创建测试表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS perf_test (
            id SERIAL PRIMARY KEY,
            data JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    # 批量插入测试
    times = []
    for i in range(100):
        start = time.time()
        cur.execute("""
            INSERT INTO perf_test (data)
            SELECT jsonb_build_object('key', generate_series(1, 1000))
        """)
        conn.commit()
        times.append(time.time() - start)

    print(f"平均时间: {statistics.mean(times):.3f}s")
    print(f"TPS: {1000/statistics.mean(times):.0f}")

    cur.close()
    conn.close()
```

### 15.3 性能对比工具

使用性能对比工具对比同步I/O和异步I/O的性能差异：

**对比测试脚本**:

```sql
-- 创建性能对比表
CREATE TABLE performance_comparison (
    test_name TEXT,
    io_mode TEXT,
    tps NUMERIC,
    avg_latency_ms NUMERIC,
    p99_latency_ms NUMERIC,
    test_time TIMESTAMPTZ DEFAULT NOW()
);

-- 记录测试结果
INSERT INTO performance_comparison (test_name, io_mode, tps, avg_latency_ms, p99_latency_ms)
VALUES
    ('批量写入', '同步I/O', 1000, 100, 250),
    ('批量写入', '异步I/O', 2700, 37, 93);
```

**性能对比分析**:

```sql
-- 对比分析查询
SELECT
    test_name,
    io_mode,
    tps,
    avg_latency_ms,
    p99_latency_ms,
    ROUND((tps / LAG(tps) OVER (PARTITION BY test_name ORDER BY io_mode) - 1) * 100, 1) AS tps_improvement
FROM performance_comparison
ORDER BY test_name, io_mode;
```

### 15.4 持续性能监控

**性能监控脚本**：

```bash
#!/bin/bash
# 性能监控脚本

while true; do
    psql -d testdb -c "
    SELECT
        NOW() AS timestamp,
        (SELECT SUM(reads + writes) FROM pg_stat_io WHERE context = 'async') AS total_io,
        (SELECT SUM(io_wait_time) FROM pg_stat_io WHERE context = 'async') AS wait_time,
        (SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active') AS active_queries
    " >> performance_log.csv
    sleep 60
done
```

**性能趋势分析**：

```sql
-- 创建性能趋势表
CREATE TABLE IF NOT EXISTS performance_trends (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    tps NUMERIC,
    avg_latency_ms NUMERIC,
    io_wait_pct NUMERIC,
    cpu_usage_pct NUMERIC
);

-- 分析性能趋势
SELECT
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(tps) AS avg_tps,
    AVG(avg_latency_ms) AS avg_latency,
    AVG(io_wait_pct) AS avg_io_wait
FROM performance_trends
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour;
```

---

## 15. 安全与高可用

> **章节编号**: 15
> **章节标题**: 安全与高可用
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 15. 安全与高可用

## 📑 目录

- [15. 性能基准测试工具](#15-性能基准测试工具)
  - [15. 性能基准测试工具](#15-性能基准测试工具-1)
  - [📑 目录](#-目录)
    - [15.1 pgbench基准测试](#151-pgbench基准测试)
    - [15.2 自定义性能测试工具](#152-自定义性能测试工具)
    - [15.3 性能对比工具](#153-性能对比工具)
    - [15.4 持续性能监控](#154-持续性能监控)
  - [15. 安全与高可用](#15-安全与高可用)
  - [15. 安全与高可用](#15-安全与高可用-1)
  - [📑 目录](#-目录-1)
    - [15.1 安全考虑](#151-安全考虑)
    - [15.2 备份恢复考虑](#152-备份恢复考虑)
    - [15.3 高可用环境配置](#153-高可用环境配置)
    - [15.4 安全最佳实践](#154-安全最佳实践)
    - [15.5 高可用架构设计](#155-高可用架构设计)
    - [15.6 备份恢复最佳实践](#156-备份恢复最佳实践)

---

### 15.1 安全考虑

异步I/O机制在安全方面需要注意以下事项：

**权限控制**:

- 异步I/O配置需要超级用户权限
- 建议通过配置文件而非SQL命令设置敏感参数
- 定期审计配置变更

**数据安全**:

```sql
-- 确保WAL完整性
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET synchronous_commit = 'on';

-- 启用SSL连接
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
```

**审计日志**:

```sql
-- 启用审计日志
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
```

### 15.2 备份恢复考虑

异步I/O机制对备份恢复的影响和注意事项：

**备份策略**:

```bash
# 使用pg_basebackup进行物理备份
pg_basebackup -D /backup/pg18 -Ft -z -P

# 使用pg_dump进行逻辑备份
pg_dump -Fc -f backup.dump database_name
```

**恢复测试**:

- 定期测试备份恢复流程
- 验证异步I/O配置在恢复后是否正确
- 确保恢复后性能正常

**WAL归档**:

```sql
-- 配置WAL归档
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command = 'cp %p /archive/%f';
```

### 15.3 高可用环境配置

在高可用环境中配置异步I/O的最佳实践：

**主从复制配置**:

```sql
-- 主库配置
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET max_wal_senders = 10;
ALTER SYSTEM SET wal_keep_size = '1GB';

-- 异步I/O配置
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET wal_io_concurrency = 200;
```

**流复制配置**:

```sql
-- 从库配置
ALTER SYSTEM SET hot_standby = on;
ALTER SYSTEM SET max_standby_streaming_delay = 30s;
```

**故障切换**:

- 配置自动故障检测
- 准备手动切换流程
- 测试故障切换场景

### 15.4 安全最佳实践

**安全配置检查清单**：

```sql
-- 1. 检查SSL配置（带性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始检查SSL配置';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查SSL配置准备失败: %', SQLERRM;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT name, setting
FROM pg_settings
WHERE name LIKE 'ssl%'
ORDER BY name;

-- 2. 检查访问控制（带性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始检查访问控制';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查访问控制准备失败: %', SQLERRM;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    datname,
    datacl,
    CASE
        WHEN datacl IS NULL THEN '⚠️ 无访问控制'
        ELSE '✅ 已配置'
    END AS acl_status
FROM pg_database
WHERE datname NOT IN ('template0', 'template1', 'postgres');

-- 3. 检查审计日志（带性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始检查审计日志配置';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查审计日志准备失败: %', SQLERRM;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT name, setting
FROM pg_settings
WHERE name LIKE 'log%'
ORDER BY name;
```

**安全加固建议**：

```sql
-- 1. 启用SSL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/postgresql/ssl/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/postgresql/ssl/server.key';

-- 2. 配置访问控制
-- 编辑pg_hba.conf
-- hostssl all all 0.0.0.0/0 md5

-- 3. 启用行级安全
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- 4. 创建安全策略
CREATE POLICY data_access_policy ON sensitive_data
FOR SELECT
USING (user_id = current_user_id());
```

### 15.5 高可用架构设计

**主从复制架构**：

```sql
-- 主库配置（postgresql.conf）
wal_level = replica
max_wal_senders = 10
wal_keep_size = 1GB
effective_io_concurrency = 300
wal_io_concurrency = 300

-- 从库配置（postgresql.conf）
hot_standby = on
max_standby_streaming_delay = 30s
hot_standby_feedback = on
```

**流复制监控**：

```sql
-- 监控复制状态
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    write_lag,
    flush_lag,
    replay_lag,
    sync_priority,
    sync_state
FROM pg_stat_replication;

-- 检查复制延迟
SELECT
    application_name,
    EXTRACT(EPOCH FROM (NOW() - write_lag)) AS write_delay_seconds,
    EXTRACT(EPOCH FROM (NOW() - replay_lag)) AS replay_delay_seconds
FROM pg_stat_replication
WHERE state = 'streaming';
```

**故障切换流程**：

```bash
# 1. 检测主库故障
pg_isready -h primary_host -p 5432

# 2. 提升从库为主库
pg_ctl promote -D /var/lib/postgresql/data

# 3. 更新应用连接配置
# 修改连接字符串指向新主库

# 4. 验证新主库
psql -h new_primary -U postgres -c "SELECT pg_is_in_recovery();"
```

### 15.6 备份恢复最佳实践

**备份策略**：

```bash
# 1. 物理备份（推荐）
pg_basebackup \
    -D /backup/pg18_$(date +%Y%m%d) \
    -Ft -z -P \
    -U replication \
    -h primary_host

# 2. 逻辑备份
pg_dump \
    -Fc \
    -f backup_$(date +%Y%m%d).dump \
    -U postgres \
    database_name

# 3. WAL归档备份
# 配置archive_command自动归档WAL文件
```

**恢复测试**：

```bash
# 1. 恢复物理备份
pg_basebackup -D /restore/pg18 -Ft -z -P

# 2. 恢复逻辑备份
pg_restore \
    -d database_name \
    -U postgres \
    backup_20250101.dump

# 3. 时间点恢复（PITR）
# 配置recovery.conf
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2025-01-01 12:00:00'
```

**备份验证**：

```sql
-- 验证备份完整性
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS size,
    CASE
        WHEN pg_database_size(datname) > 0 THEN '✅ 正常'
        ELSE '❌ 异常'
    END AS status
FROM pg_database
WHERE datname NOT IN ('template0', 'template1');
```

---

**返回**: [文档首页](../README.md) | [上一章节](../14-常见问题FAQ/README.md) | [下一章节](../16-性能测试工具/README.md)
