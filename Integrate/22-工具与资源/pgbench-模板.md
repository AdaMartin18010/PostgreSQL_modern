---

> **📋 文档来源**: `PostgreSQL\bench\pgbench-模板.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# pgbench 压测模板

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **最后更新**: 2025-11-12

---

## 1. 目标

- 评估 PostgreSQL 的 OLTP 性能（TPS、延迟）
- 对比不同配置参数的性能影响
- 建立性能基线，用于回归测试

---

## 2. 环境准备

### 2.1 前置条件

- PostgreSQL 已安装并运行
- pgbench 工具可用（通常包含在 `postgresql-contrib` 包中）
- 足够的磁盘空间（建议至少 10GB 可用空间）

### 2.2 安装 pgbench

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-contrib

# macOS (Homebrew)
brew install postgresql

# 验证安装
pgbench --version
```

### 2.3 创建测试数据库

```bash
# 创建测试数据库
createdb pgbench_test

# 或使用现有数据库
psql -d postgres -c "CREATE DATABASE pgbench_test;"
```

---

## 3. 初始化测试数据

### 3.1 标准初始化

```bash
# -i: 初始化
# -s: scale factor（数据规模因子，1 = 100,000 行）
# 例如 -s 10 表示 1,000,000 行
pgbench -i -s 10 pgbench_test
```

### 3.2 数据规模选择

| Scale Factor | 表大小（约） | 适用场景 |
|-------------|------------|---------|
| 1 | ~25 MB | 快速测试 |
| 10 | ~250 MB | 开发环境 |
| 100 | ~2.5 GB | 生产环境模拟 |
| 1000 | ~25 GB | 大规模测试 |

### 3.3 验证数据

```sql
-- 检查表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 检查行数
SELECT
    'pgbench_accounts' AS table_name,
    COUNT(*) AS row_count
FROM pgbench_accounts;
```

---

## 4. 基线压测

### 4.1 标准 TPC-B 测试

```bash
# 基本参数说明：
# -c: 客户端连接数（并发数）
# -j: 工作线程数（建议等于 CPU 核心数）
# -T: 测试持续时间（秒）
# -r: 报告每个语句的平均延迟

# 标准测试（32 并发，300 秒）
pgbench -c 32 -j 32 -T 300 -r pgbench_test
```

### 4.2 不同并发度测试

```bash
# 低并发（8 客户端）
pgbench -c 8 -j 8 -T 300 -r pgbench_test > result_c8.log 2>&1

# 中等并发（32 客户端）
pgbench -c 32 -j 32 -T 300 -r pgbench_test > result_c32.log 2>&1

# 高并发（64 客户端）
pgbench -c 64 -j 64 -T 300 -r pgbench_test > result_c64.log 2>&1

# 极高并发（128 客户端）
pgbench -c 128 -j 128 -T 300 -r pgbench_test > result_c128.log 2>&1
```

### 4.3 只读测试

```bash
# -S: 只读模式（SELECT only）
pgbench -S -c 32 -j 32 -T 300 -r pgbench_test
```

### 4.4 只写测试

```bash
# -N: 跳过 SELECT 语句（只执行 UPDATE/INSERT）
pgbench -N -c 32 -j 32 -T 300 -r pgbench_test
```

---

## 5. 自定义脚本测试

### 5.1 创建自定义脚本

```sql
-- custom_select.sql
\set aid random(1, 1000000)
SELECT * FROM pgbench_accounts WHERE aid = :aid;
```

```sql
-- custom_update.sql
\set aid random(1, 1000000)
\set delta random(-5000, 5000)
UPDATE pgbench_accounts
SET abalance = abalance + :delta
WHERE aid = :aid;
```

```sql
-- custom_transaction.sql
\set aid random(1, 1000000)
\set bid random(1, 100000)
\set tid random(1, 10000000)
\set delta random(-5000, 5000)
BEGIN;
UPDATE pgbench_accounts SET abalance = abalance + :delta WHERE aid = :aid;
SELECT abalance FROM pgbench_accounts WHERE aid = :aid;
INSERT INTO pgbench_history (tid, bid, aid, delta, mtime)
VALUES (:tid, :bid, :aid, :delta, CURRENT_TIMESTAMP);
COMMIT;
```

### 5.2 运行自定义脚本

```bash
# 运行单个脚本
pgbench -c 32 -j 32 -T 300 -f custom_select.sql -r pgbench_test

# 运行多个脚本（按权重）
pgbench -c 32 -j 32 -T 300 \
  -f custom_select.sql@10 \
  -f custom_update.sql@5 \
  -f custom_transaction.sql@1 \
  -r pgbench_test
```

---

## 6. 高级测试选项

### 6.1 事务数测试

```bash
# -t: 指定事务总数（替代 -T）
pgbench -c 32 -j 32 -t 100000 -r pgbench_test
```

### 6.2 预热测试

```bash
# 先运行预热（不记录结果）
pgbench -c 32 -j 32 -T 60 pgbench_test

# 然后运行正式测试
pgbench -c 32 -j 32 -T 300 -r pgbench_test
```

### 6.3 详细报告

```bash
# -r: 报告每个语句的统计
# -l: 记录每个事务的延迟到日志文件
pgbench -c 32 -j 32 -T 300 -r -l pgbench_test
```

### 6.4 延迟直方图

```bash
# 使用 -l 记录日志，然后分析
pgbench -c 32 -j 32 -T 300 -l pgbench_test

# 分析延迟分布（需要额外工具）
# 或使用 pgbench 的 --aggregate-interval 选项（PostgreSQL 17+）
```

---

## 7. 监控指标

### 7.1 pgbench 输出指标

```text
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 10
query mode: simple
number of clients: 32
number of threads: 32
duration: 300 s
number of transactions actually processed: 123456
latency average = 77.234 ms
latency stddev = 12.456 ms
initial connection time = 45.123 ms
tps = 411.234 (including connections establishing)
tps = 412.567 (excluding connections establishing)
```

**关键指标**：

- **TPS**: 每秒事务数（越高越好）
- **latency average**: 平均延迟（越低越好）
- **latency stddev**: 延迟标准差（越小越稳定）

### 7.2 PostgreSQL 指标

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
WHERE query LIKE '%pgbench%'
ORDER BY total_exec_time DESC
LIMIT 10;

-- 查看表统计
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_tup_upd + n_tup_ins DESC;
```

### 7.3 系统资源监控

```bash
# CPU 和内存监控
sar -u 1 300 > cpu.log &
sar -r 1 300 > memory.log &

# IO 监控
iostat -x 1 300 > io.log &

# 网络监控（如适用）
sar -n DEV 1 300 > network.log &
```

---

## 8. 结果记录与分析

### 8.1 性能指标记录表

| 测试场景 | TPS | 平均延迟 (ms) | 延迟标准差 (ms) | TP95 (ms) | TP99 (ms) | CPU (%) | IO (MB/s) |
|---------|-----|--------------|---------------|-----------|-----------|---------|-----------|
| 基线测试 (c=32) | | | | | | | |
| 低并发 (c=8) | | | | | | | |
| 高并发 (c=64) | | | | | | | |
| 只读测试 | | | | | | | |
| 只写测试 | | | | | | | |

### 8.2 延迟分位分析

```bash
# 如果使用了 -l 选项记录日志
# 可以使用以下命令分析延迟分位（需要额外工具或脚本）

# 示例：使用 awk 分析
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

### 8.3 记录模板

```markdown
## 测试环境
- **硬件**: CPU型号、内存、存储类型
- **系统**: OS版本、内核版本
- **PostgreSQL版本**: 18.x
- **数据规模**: scale factor = X

## 配置参数
- **shared_buffers**:
- **work_mem**:
- **maintenance_work_mem**:
- **effective_cache_size**:
- **max_connections**:
- **checkpoint相关**:

## 测试结果
- **测试时间**:
- **并发数**:
- **测试时长**:
- **TPS**:
- **平均延迟**:
- **延迟标准差**:
- **系统资源**: CPU=%, Memory=%, IO=MB/s

## 关键发现
-
-

## 优化建议
-
-
```

---

## 9. 性能调优建议

### 9.1 PostgreSQL 配置优化

```sql
-- 查看当前配置
SHOW shared_buffers;
SHOW work_mem;
SHOW effective_cache_size;
SHOW max_connections;

-- 推荐配置（根据实际情况调整）
-- shared_buffers = 25% of RAM (但不超过 8GB)
-- work_mem = (RAM - shared_buffers) / (max_connections * 3)
-- effective_cache_size = 50-75% of RAM
-- max_connections = 根据实际需求
```

### 9.2 测试最佳实践

1. **建立基线**: 在优化前先建立性能基线
2. **单变量测试**: 每次只改变一个参数，便于对比
3. **多次运行**: 运行多次测试取平均值，减少波动影响
4. **预热测试**: 正式测试前先运行预热，确保缓存已加载
5. **监控资源**: 同时监控系统资源，避免瓶颈转移
6. **记录环境**: 详细记录测试环境，确保可复现

---

## 10. 常见问题

### 10.1 TPS 过低

- 检查 `max_connections` 是否足够
- 检查系统资源（CPU、内存、IO）是否成为瓶颈
- 检查是否有锁等待或慢查询

### 10.2 延迟不稳定

- 检查是否有其他负载干扰
- 检查 IO 性能是否稳定
- 检查是否有检查点或 VACUUM 在运行

### 10.3 连接失败

- 检查 `max_connections` 设置
- 检查系统资源限制（ulimit）
- 检查网络连接

---

## 11. 参考资源

- **PostgreSQL 官方文档**: <https://www.postgresql.org/docs/current/pgbench.html>
- **TPC-B 基准**: <http://www.tpc.org/tpcb/>
- **性能调优指南**: `../04-部署运维/`
