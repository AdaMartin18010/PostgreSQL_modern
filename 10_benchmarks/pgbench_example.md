# pgbench 完整使用指南

> PostgreSQL 17 官方性能基准测试工具

## 📋 目录

- [pgbench 完整使用指南](#pgbench-完整使用指南)
  - [📋 目录](#-目录)
  - [基础概念](#基础概念)
    - [pgbench是什么？](#pgbench是什么)
    - [核心术语](#核心术语)
  - [快速开始](#快速开始)
    - [1. 基础测试流程](#1-基础测试流程)
    - [2. 数据规模选择](#2-数据规模选择)
    - [3. 生成的表结构](#3-生成的表结构)
  - [测试模式](#测试模式)
    - [1. 默认模式（读写混合）](#1-默认模式读写混合)
    - [2. 只读模式 (-S)](#2-只读模式--s)
    - [3. 简单写入模式 (-N)](#3-简单写入模式--n)
    - [4. 混合比例测试](#4-混合比例测试)
  - [自定义脚本](#自定义脚本)
    - [1. 基础自定义脚本](#1-基础自定义脚本)
    - [2. 带变量的脚本](#2-带变量的脚本)
    - [3. 复杂业务脚本](#3-复杂业务脚本)
    - [4. 多脚本混合](#4-多脚本混合)
  - [性能调优](#性能调优)
    - [1. 并发与线程配置](#1-并发与线程配置)
    - [2. 连接池配置](#2-连接池配置)
    - [3. 预热数据](#3-预热数据)
    - [4. 参数优化](#4-参数优化)
  - [结果分析](#结果分析)
    - [1. 输出解读](#1-输出解读)
    - [2. 详细统计 (-r)](#2-详细统计--r)
    - [3. 进度报告 (-P)](#3-进度报告--p)
    - [4. 日志模式 (-l)](#4-日志模式--l)
  - [最佳实践](#最佳实践)
    - [1. 测试前准备](#1-测试前准备)
    - [2. 标准测试流程](#2-标准测试流程)
    - [3. 对比测试](#3-对比测试)
    - [4. 监控配合](#4-监控配合)
    - [5. 常见陷阱](#5-常见陷阱)
  - [实战案例](#实战案例)
    - [案例1：评估硬件升级效果](#案例1评估硬件升级效果)
    - [案例2：连接池效果验证](#案例2连接池效果验证)
    - [案例3：参数调优效果](#案例3参数调优效果)
  - [📚 参考资源](#-参考资源)

---

## 基础概念

### pgbench是什么？

pgbench是PostgreSQL官方提供的基准测试工具，用于：

- 测试数据库的TPS（每秒事务数）
- 评估不同配置下的性能表现
- 模拟真实业务负载
- 验证硬件和优化效果

### 核心术语

| 术语 | 说明 |
|------|------|
| **Scale Factor (-s)** | 数据规模因子，1=10万行，10=100万行 |
| **Clients (-c)** | 并发客户端数量（连接数） |
| **Threads (-j)** | 工作线程数量，建议≤CPU核心数 |
| **Duration (-T)** | 测试持续时间（秒） |
| **Transactions (-t)** | 每客户端执行事务数 |
| **TPS** | 每秒事务数（Transactions Per Second） |

---

## 快速开始

### 1. 基础测试流程

```bash
# 步骤1：初始化测试数据（scale=10，约100万行）
pgbench -i -s 10 -U postgres -d testdb

# 步骤2：运行基准测试（60秒，16并发，1线程）
pgbench -T 60 -c 16 -j 1 -U postgres -d testdb

# 步骤3：查看结果
# TPS (including/excluding connections)
# Latency (average, median, p95, p99)
```

### 2. 数据规模选择

```bash
# 小规模测试（快速验证）
pgbench -i -s 1     # 10万行，约16MB

# 中等规模（常用）
pgbench -i -s 10    # 100万行，约160MB

# 大规模（接近生产）
pgbench -i -s 100   # 1000万行，约1.6GB

# 超大规模（生产级）
pgbench -i -s 1000  # 1亿行，约16GB
```

### 3. 生成的表结构

```sql
-- pgbench 自动创建4张表：

-- 1. pgbench_accounts (主表)
-- 约10万行/scale，包含余额信息
CREATE TABLE pgbench_accounts (
    aid    INTEGER PRIMARY KEY,
    bid    INTEGER,
    abalance INTEGER,
    filler CHAR(84)
);

-- 2. pgbench_branches
-- 每scale 1行
CREATE TABLE pgbench_branches (
    bid      INTEGER PRIMARY KEY,
    bbalance INTEGER,
    filler   CHAR(88)
);

-- 3. pgbench_tellers
-- 每scale 10行
CREATE TABLE pgbench_tellers (
    tid      INTEGER PRIMARY KEY,
    bid      INTEGER,
    tbalance INTEGER,
    filler   CHAR(84)
);

-- 4. pgbench_history
-- 记录事务历史
CREATE TABLE pgbench_history (
    tid    INTEGER,
    bid    INTEGER,
    aid    INTEGER,
    delta  INTEGER,
    mtime  TIMESTAMP,
    filler CHAR(22)
);
```

---

## 测试模式

### 1. 默认模式（读写混合）

```bash
# 默认TPC-B like事务
pgbench -T 60 -c 16 -j 2 testdb
```

**事务内容**：

```sql
BEGIN;
UPDATE pgbench_accounts SET abalance = abalance + :delta WHERE aid = :aid;
SELECT abalance FROM pgbench_accounts WHERE aid = :aid;
UPDATE pgbench_tellers SET tbalance = tbalance + :delta WHERE tid = :tid;
UPDATE pgbench_branches SET bbalance = bbalance + :delta WHERE bid = :bid;
INSERT INTO pgbench_history VALUES (:tid, :bid, :aid, :delta, CURRENT_TIMESTAMP);
COMMIT;
```

### 2. 只读模式 (-S)

```bash
# Select-only测试
pgbench -S -T 60 -c 32 -j 4 testdb
```

**事务内容**：

```sql
SELECT abalance FROM pgbench_accounts WHERE aid = :aid;
```

### 3. 简单写入模式 (-N)

```bash
# 跳过UPDATE pgbench_branches和INSERT history
pgbench -N -T 60 -c 16 -j 2 testdb
```

### 4. 混合比例测试

```bash
# 80%读 + 20%写
pgbench -b select-only@80 -b tpcb-like@20 -T 60 -c 16 testdb
```

---

## 自定义脚本

### 1. 基础自定义脚本

**select_only.sql**:

```sql
-- 单表查询
\set aid random(1, 100000 * :scale)
SELECT abalance FROM pgbench_accounts WHERE aid = :aid;
```

**使用**:

```bash
pgbench -T 60 -c 16 -j 2 -f select_only.sql testdb
```

### 2. 带变量的脚本

**range_query.sql**:

```sql
-- 范围查询
\set start_aid random(1, 100000 * :scale - 1000)
\set end_aid :start_aid + 1000
SELECT count(*), avg(abalance) 
FROM pgbench_accounts 
WHERE aid BETWEEN :start_aid AND :end_aid;
```

### 3. 复杂业务脚本

**complex_txn.sql**:

```sql
-- 模拟转账业务
\set from_aid random(1, 100000 * :scale)
\set to_aid random(1, 100000 * :scale)
\set amount random(1, 1000)

BEGIN;
-- 检查余额
SELECT abalance FROM pgbench_accounts WHERE aid = :from_aid;
-- 转账
UPDATE pgbench_accounts SET abalance = abalance - :amount WHERE aid = :from_aid;
UPDATE pgbench_accounts SET abalance = abalance + :amount WHERE aid = :to_aid;
-- 记录日志
INSERT INTO pgbench_history (aid, delta, mtime) VALUES (:from_aid, -:amount, now());
COMMIT;
```

### 4. 多脚本混合

```bash
# 70%读 + 30%写
pgbench -T 120 \
  -f select_only.sql@70 \
  -f complex_txn.sql@30 \
  -c 32 -j 4 testdb
```

---

## 性能调优

### 1. 并发与线程配置

```bash
# 低并发（适合小型服务器）
pgbench -c 8 -j 2 -T 60 testdb

# 中等并发（适合中型服务器）
pgbench -c 32 -j 4 -T 60 testdb

# 高并发（适合大型服务器）
pgbench -c 128 -j 8 -T 60 testdb

# 超高并发（压力测试）
pgbench -c 500 -j 16 -T 60 testdb
```

**建议**：

- 线程数(-j) ≤ CPU核心数
- 客户端数(-c) = 线程数(-j) × (4~16)
- 先从低并发开始，逐步增加

### 2. 连接池配置

**不使用连接池**：

```bash
pgbench -c 100 -j 4 -T 60 testdb
# 每次测试都建立100个新连接
```

**使用pgbouncer**：

```bash
# 配置pgbouncer transaction模式
pgbench -c 100 -j 4 -T 60 \
  -h localhost -p 6432 testdb
# 连接池复用，性能更好
```

### 3. 预热数据

```bash
# 步骤1：预热（加载热数据到缓存）
pgbench -S -T 60 -c 16 testdb

# 步骤2：正式测试
pgbench -T 300 -c 32 -j 4 testdb
```

### 4. 参数优化

**关键PostgreSQL参数**：

```sql
-- 内存
shared_buffers = 4GB              -- 25-40% of RAM
work_mem = 64MB                   -- 每连接排序内存
maintenance_work_mem = 1GB        -- 索引创建/VACUUM

-- 检查点
checkpoint_timeout = 15min        -- 检查点间隔
max_wal_size = 4GB                -- WAL最大大小
checkpoint_completion_target = 0.9

-- WAL
wal_compression = on              -- WAL压缩
wal_buffers = 16MB                

-- 并发
max_connections = 200             -- 最大连接数
effective_cache_size = 12GB       -- 可用缓存（仅规划器使用）
```

---

## 结果分析

### 1. 输出解读

```bash
$ pgbench -T 60 -c 16 -j 2 testdb

transaction type: <builtin: TPC-B (sort of)>
scaling factor: 10
query mode: simple
number of clients: 16
number of threads: 2
duration: 60 s
number of transactions actually processed: 54826
latency average = 17.523 ms
latency stddev = 12.345 ms
initial connection time = 45.678 ms
tps = 913.204756 (without initial connection time)
tps = 910.123456 (including connection time)

statement latencies in milliseconds:
         0.002  \set aid random(1, 100000 * :scale)
         0.003  \set bid random(1, 1 * :scale)
         0.002  \set tid random(1, 10 * :scale)
         0.002  \set delta random(-5000, 5000)
         0.412  BEGIN;
         1.234  UPDATE pgbench_accounts SET abalance = abalance + :delta WHERE aid = :aid;
         0.567  SELECT abalance FROM pgbench_accounts WHERE aid = :aid;
         2.345  UPDATE pgbench_tellers SET tbalance = tbalance + :delta WHERE tid = :tid;
         3.456  UPDATE pgbench_branches SET bbalance = bbalance + :delta WHERE bid = :bid;
         8.901  INSERT INTO pgbench_history VALUES (:tid, :bid, :aid, :delta, CURRENT_TIMESTAMP);
         0.601  END;
```

**关键指标**：

- **TPS**: 913（每秒事务数）
- **平均延迟**: 17.5ms
- **标准差**: 12.3ms（越小越稳定）
- **最慢语句**: INSERT INTO pgbench_history (8.9ms)

### 2. 详细统计 (-r)

```bash
# 启用每语句统计
pgbench -T 60 -c 16 -j 2 -r testdb
```

### 3. 进度报告 (-P)

```bash
# 每10秒输出一次进度
pgbench -T 300 -c 32 -j 4 -P 10 testdb

# 输出示例：
# progress: 10.0 s, 920.3 tps, lat 17.391 ms stddev 12.123
# progress: 20.0 s, 915.7 tps, lat 17.489 ms stddev 11.987
```

### 4. 日志模式 (-l)

```bash
# 记录每个事务的详细日志
pgbench -T 60 -c 16 -j 2 -l --log-prefix=test1 testdb

# 生成文件：test1.*.log
# 格式：client_id transaction_no time script_no time_epoch time_us [schedule_lag]
```

**日志分析**：

```bash
# 计算P95延迟
cat test1.*.log | awk '{print $3}' | sort -n | \
  awk 'BEGIN{c=0} {lat[c++]=$1} END{print lat[int(c*0.95)]}'
```

---

## 最佳实践

### 1. 测试前准备

```bash
# ✅ 1. 重启数据库（清空缓存，公平对比）
pg_ctl restart

# ✅ 2. 初始化测试数据
pgbench -i -s 100 testdb

# ✅ 3. 运行VACUUM和ANALYZE
psql testdb -c "VACUUM ANALYZE;"

# ✅ 4. 预热数据
pgbench -S -T 60 -c 16 testdb
```

### 2. 标准测试流程

```bash
# 场景1：只读性能
pgbench -S -T 300 -c 32 -j 4 -P 10 -r testdb > readonly.log

# 场景2：读写混合（默认）
pgbench -T 300 -c 32 -j 4 -P 10 -r testdb > readwrite.log

# 场景3：高并发压测
pgbench -T 300 -c 128 -j 8 -P 10 -r testdb > highload.log
```

### 3. 对比测试

```bash
# 基线测试（优化前）
pgbench -T 300 -c 32 -j 4 testdb > baseline.log

# 修改配置
psql -c "ALTER SYSTEM SET shared_buffers = '8GB';"
pg_ctl restart

# 对比测试（优化后）
pgbench -T 300 -c 32 -j 4 testdb > optimized.log

# 比较结果
grep "tps =" baseline.log optimized.log
```

### 4. 监控配合

**同时监控系统指标**：

```bash
# 在另一个终端运行
vmstat 1

# 或使用pg_stat_statements
psql -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### 5. 常见陷阱

❌ **避免**：

- 测试前不预热，冷缓存影响结果
- 单次测试时间过短（<60s）
- 并发数远超服务器能力
- 忽略网络延迟（远程测试）
- 不同环境对比（硬件/配置差异）

✅ **推荐**：

- 多次测试取平均值
- 测试时长≥300秒（稳定状态）
- 使用本地连接（减少网络干扰）
- 记录完整环境信息
- 使用版本控制管理测试脚本

---

## 实战案例

### 案例1：评估硬件升级效果

```bash
# 场景：从HDD升级到SSD

# 1. HDD基线
pgbench -i -s 100 testdb
pgbench -T 300 -c 32 -j 4 testdb
# 结果：TPS = 450

# 2. 迁移到SSD

# 3. SSD测试
pgbench -T 300 -c 32 -j 4 testdb
# 结果：TPS = 2800

# 性能提升：6.2倍
```

### 案例2：连接池效果验证

```bash
# 场景：验证pgbouncer收益

# 1. 无连接池（高并发）
pgbench -T 300 -c 200 -j 8 testdb
# 结果：TPS = 3200，延迟高

# 2. 使用pgbouncer
pgbench -T 300 -c 200 -j 8 -h localhost -p 6432 testdb
# 结果：TPS = 5400，延迟降低

# 性能提升：68%
```

### 案例3：参数调优效果

```bash
# 场景：优化shared_buffers

# 测试不同值：2GB, 4GB, 8GB, 16GB
for sb in 2GB 4GB 8GB 16GB; do
    psql -c "ALTER SYSTEM SET shared_buffers = '$sb';"
    pg_ctl restart
    sleep 10
    pgbench -S -T 180 -c 32 testdb | grep "tps ="
done

# 找到最优值：8GB (TPS最高)
```

---

## 📚 参考资源

- **官方文档**: <https://www.postgresql.org/docs/17/pgbench.html>
- **性能调优**: <https://www.postgresql.org/docs/17/performance-tips.html>
- **pg_stat_statements**: 配合使用，分析热点SQL
- **相关章节**: `../README.md`, `pgbench_oltp_playbook.md`

---

**最后更新**: 2025-10  
**适用版本**: PostgreSQL 12-17
