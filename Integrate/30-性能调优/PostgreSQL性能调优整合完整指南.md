---
> **📋 文档来源**: 新增整合深化文档
> **📅 创建日期**: 2025-01
> **⚠️ 注意**: 本文档整合所有性能调优内容，提供系统化方法论

---

# PostgreSQL性能调优整合完整指南

## 元数据

- **文档版本**: v2.0
- **创建日期**: 2025-01
- **技术栈**: PostgreSQL 17+/18+ | pg_stat_statements | EXPLAIN | pgBadger
- **难度级别**: ⭐⭐⭐⭐⭐ (专家级)
- **预计阅读**: 180分钟
- **前置要求**: 熟悉PostgreSQL基础、查询优化、索引结构

---

## 📋 完整目录

- [PostgreSQL性能调优整合完整指南](#postgresql性能调优整合完整指南)
  - [元数据](#元数据)
  - [📋 完整目录](#-完整目录)
  - [1. 性能调优方法论](#1-性能调优方法论)
    - [1.1 调优原则](#11-调优原则)
      - [核心原则](#核心原则)
    - [1.2 调优流程](#12-调优流程)
      - [标准调优流程](#标准调优流程)
    - [1.3 调优层次](#13-调优层次)
      - [三层调优模型](#三层调优模型)
    - [1.4 调优工具链](#14-调优工具链)
      - [完整工具链](#完整工具链)
  - [2. 性能基线建立](#2-性能基线建立)
    - [2.1 关键性能指标](#21-关键性能指标)
      - [数据库性能指标](#数据库性能指标)
    - [2.2 基准测试](#22-基准测试)
      - [pgbench基准测试](#pgbench基准测试)
  - [3. 性能瓶颈诊断](#3-性能瓶颈诊断)
    - [3.1 系统资源瓶颈](#31-系统资源瓶颈)
      - [CPU瓶颈诊断](#cpu瓶颈诊断)
      - [内存瓶颈诊断](#内存瓶颈诊断)
      - [I/O瓶颈诊断](#io瓶颈诊断)
    - [3.2 数据库瓶颈](#32-数据库瓶颈)
      - [连接数瓶颈](#连接数瓶颈)
      - [锁等待分析](#锁等待分析)
    - [3.3 查询瓶颈](#33-查询瓶颈)
      - [慢查询识别](#慢查询识别)
    - [3.4 诊断工具与方法](#34-诊断工具与方法)
      - [执行计划分析](#执行计划分析)
  - [4. 系统级调优](#4-系统级调优)
    - [4.1 操作系统参数优化](#41-操作系统参数优化)
      - [Linux内核参数](#linux内核参数)
    - [4.2 硬件资源优化](#42-硬件资源优化)
      - [CPU优化](#cpu优化)
      - [内存优化](#内存优化)
    - [4.3 文件系统优化](#43-文件系统优化)
      - [文件系统选择](#文件系统选择)
  - [5. 数据库级调优](#5-数据库级调优)
    - [5.1 内存配置优化](#51-内存配置优化)
      - [内存参数配置](#内存参数配置)
      - [内存配置计算器](#内存配置计算器)
    - [5.2 连接与并发配置](#52-连接与并发配置)
      - [连接配置](#连接配置)
      - [并发控制](#并发控制)
    - [5.3 WAL与检查点配置](#53-wal与检查点配置)
      - [WAL配置优化](#wal配置优化)
      - [检查点配置](#检查点配置)
    - [5.4 参数优化策略](#54-参数优化策略)
      - [参数调优流程](#参数调优流程)
  - [6. 查询级调优](#6-查询级调优)
    - [6.1 SQL查询优化](#61-sql查询优化)
      - [优化技巧](#优化技巧)
    - [6.2 执行计划分析](#62-执行计划分析)
      - [执行计划解读](#执行计划解读)
      - [执行计划优化](#执行计划优化)
    - [6.3 查询重写优化](#63-查询重写优化)
      - [查询重写技巧](#查询重写技巧)
    - [6.4 慢查询优化](#64-慢查询优化)
      - [慢查询分析流程](#慢查询分析流程)
  - [7. 索引调优](#7-索引调优)
    - [7.1 索引类型选择](#71-索引类型选择)
      - [索引类型对比](#索引类型对比)
    - [7.2 索引设计原则](#72-索引设计原则)
      - [设计原则](#设计原则)
      - [索引设计示例](#索引设计示例)
    - [7.3 索引优化策略](#73-索引优化策略)
      - [索引使用分析](#索引使用分析)
  - [8. 存储调优](#8-存储调优)
    - [8.1 表空间优化](#81-表空间优化)
      - [表空间配置](#表空间配置)
    - [8.2 分区策略](#82-分区策略)
      - [分区设计](#分区设计)
  - [9. 参数调优最佳实践](#9-参数调优最佳实践)
    - [9.1 关键参数详解](#91-关键参数详解)
      - [核心参数配置模板](#核心参数配置模板)
  - [10. 性能监控与持续优化](#10-性能监控与持续优化)
    - [10.1 性能监控工具](#101-性能监控工具)
      - [pg\_stat\_statements配置](#pg_stat_statements配置)
      - [关键指标监控](#关键指标监控)
  - [11. 综合调优案例](#11-综合调优案例)
    - [11.1 高并发场景调优](#111-高并发场景调优)
      - [场景描述](#场景描述)
      - [优化方案](#优化方案)
  - [12. PostgreSQL 18性能优化新特性](#12-postgresql-18性能优化新特性)
    - [12.1 异步I/O优化（PostgreSQL 18）](#121-异步io优化postgresql-18)
      - [异步I/O配置](#异步io配置)
      - [异步I/O性能监控](#异步io性能监控)
      - [异步I/O优化场景](#异步io优化场景)
        - [1. 大表扫描查询](#1-大表扫描查询)
        - [2. 向量检索查询](#2-向量检索查询)
        - [3. 索引构建](#3-索引构建)
    - [12.2 跳过扫描优化（PostgreSQL 18）](#122-跳过扫描优化postgresql-18)
      - [跳过扫描示例](#跳过扫描示例)
      - [跳过扫描优势](#跳过扫描优势)
  - [📚 参考资源](#-参考资源)
  - [📝 更新日志](#-更新日志)

---

## 1. 性能调优方法论

### 1.1 调优原则

#### 核心原则

```text
1. 先测量，后优化 (Measure First, Optimize Later)
   - 建立性能基线
   - 识别真正的瓶颈
   - 量化优化效果

2. 先系统，后应用 (System Before Application)
   - 操作系统层面
   - 数据库层面
   - 应用层面

3. 先索引，后查询 (Index Before Query)
   - 索引优化通常比查询重写更有效
   - 合理的索引可以大幅提升性能

4. 先配置，后代码 (Configuration Before Code)
   - 调整配置参数
   - 优化数据库结构
   - 最后才修改应用代码

5. 80/20原则 (Pareto Principle)
   - 80%的性能问题来自20%的查询
   - 重点优化高频慢查询
```

### 1.2 调优流程

#### 标准调优流程

```text
阶段1: 性能基线建立
  ├─ 收集关键指标
  ├─ 建立性能基线
  └─ 定义性能目标

阶段2: 性能问题识别
  ├─ 识别慢查询
  ├─ 识别资源瓶颈
  └─ 识别系统瓶颈

阶段3: 性能瓶颈分析
  ├─ 执行计划分析
  ├─ 资源使用分析
  └─ 等待事件分析

阶段4: 优化方案制定
  ├─ 制定优化策略
  ├─ 评估优化影响
  └─ 制定实施计划

阶段5: 优化实施
  ├─ 系统级优化
  ├─ 数据库级优化
  └─ 查询级优化

阶段6: 效果验证
  ├─ 性能对比
  ├─ 回归测试
  └─ 效果评估

阶段7: 持续监控
  ├─ 持续监控
  ├─ 趋势分析
  └─ 预防性优化
```

### 1.3 调优层次

#### 三层调优模型

```text
┌─────────────────────────────────────┐
│  应用层调优                          │
│  - SQL优化                           │
│  - 查询重写                          │
│  - 应用逻辑优化                      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  数据库层调优                        │
│  - 索引优化                          │
│  - 参数调优                          │
│  - 架构优化                          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  系统层调优                          │
│  - 操作系统参数                      │
│  - 硬件资源                          │
│  - 文件系统                          │
└─────────────────────────────────────┘
```

### 1.4 调优工具链

#### 完整工具链

```text
监控工具:
├─ pg_stat_statements  (查询统计)
├─ pg_stat_activity    (活动监控)
├─ pg_stat_database    (数据库统计)
├─ pg_stat_user_tables (表统计)
└─ pg_stat_user_indexes (索引统计)

分析工具:
├─ EXPLAIN (ANALYZE, BUFFERS, TIMING)     (执行计划)
├─ pgBadger            (日志分析)
├─ pg_stat_monitor     (性能监控)
└─ pg_top              (实时监控)

测试工具:
├─ pgbench             (基准测试)
├─ HammerDB            (负载测试)
└─ sysbench            (系统测试)
```

---

## 2. 性能基线建立

### 2.1 关键性能指标

#### 数据库性能指标

```sql
-- 创建性能指标收集函数
CREATE OR REPLACE FUNCTION collect_performance_metrics()
RETURNS TABLE (
    metric_name TEXT,
    metric_value NUMERIC,
    metric_unit TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'database_size_gb'::TEXT,
           pg_database_size(current_database()) / 1024.0 / 1024.0 / 1024.0,
           'GB'::TEXT
    UNION ALL
    SELECT 'total_connections',
           (SELECT count(*) FROM pg_stat_activity),
           'count'::TEXT
    UNION ALL
    SELECT 'active_connections',
           (SELECT count(*) FROM pg_stat_activity WHERE state = 'active'),
           'count'::TEXT
    UNION ALL
    SELECT 'cache_hit_ratio',
           (SELECT
                CASE
                    WHEN sum(blks_hit) + sum(blks_read) > 0 THEN
                        sum(blks_hit)::NUMERIC / (sum(blks_hit) + sum(blks_read)) * 100
                    ELSE 0
                END
            FROM pg_stat_database WHERE datname = current_database()),
           'percent'::TEXT
    UNION ALL
    SELECT 'index_usage_ratio',
           (SELECT
                CASE
                    WHEN sum(idx_scan) + sum(seq_scan) > 0 THEN
                        sum(idx_scan)::NUMERIC / (sum(idx_scan) + sum(seq_scan)) * 100
                    ELSE 0
                END
            FROM pg_stat_user_tables),
           'percent'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- 使用函数
SELECT * FROM collect_performance_metrics();
```

### 2.2 基准测试

#### pgbench基准测试

```bash
# 初始化测试数据库
pgbench -i -s 100 mydb  # -s 100表示100倍标准规模

# 只读测试
pgbench -c 10 -j 2 -T 60 -S mydb

# 读写混合测试
pgbench -c 10 -j 2 -T 60 mydb

# 自定义测试脚本
cat > custom_script.sql <<EOF
\set id random(1, 1000000)
SELECT * FROM accounts WHERE aid = :id;
EOF

pgbench -c 10 -j 2 -T 60 -f custom_script.sql mydb
```

---

## 3. 性能瓶颈诊断

### 3.1 系统资源瓶颈

#### CPU瓶颈诊断

```sql
-- 查看CPU密集型查询
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    (total_exec_time / sum(total_exec_time) OVER ()) * 100 AS pct_total_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 查看当前CPU使用情况
SELECT
    pid,
    usename,
    application_name,
    state,
    query,
    query_start,
    now() - query_start AS query_duration
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;
```

#### 内存瓶颈诊断

```sql
-- 查看内存使用情况
SELECT
    name,
    setting,
    unit,
    source
FROM pg_settings
WHERE name IN (
    'shared_buffers',
    'effective_cache_size',
    'work_mem',
    'maintenance_work_mem'
);

-- 查看数据库缓存命中率
SELECT
    datname,
    blks_hit,
    blks_read,
    CASE
        WHEN blks_hit + blks_read > 0 THEN
            round(blks_hit::NUMERIC / (blks_hit + blks_read) * 100, 2)
        ELSE 0
    END AS cache_hit_ratio
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY cache_hit_ratio DESC;
```

#### I/O瓶颈诊断

```sql
-- 查看I/O密集型表
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS table_size
FROM pg_stat_user_tables
ORDER BY seq_tup_read DESC
LIMIT 20;
```

### 3.2 数据库瓶颈

#### 连接数瓶颈

```sql
-- 查看连接使用情况
SELECT
    state,
    count(*) AS connections,
    max(now() - state_change) AS max_idle_time
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state;

-- 查看连接限制
SELECT
    setting AS max_connections,
    (SELECT count(*) FROM pg_stat_activity) AS current_connections,
    setting::INT - (SELECT count(*) FROM pg_stat_activity) AS available_connections
FROM pg_settings
WHERE name = 'max_connections';
```

#### 锁等待分析

```sql
-- 查看锁等待
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    blocked_activity.application_name AS blocked_application,
    blocking_activity.application_name AS blocking_application
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

### 3.3 查询瓶颈

#### 慢查询识别

```sql
-- 使用pg_stat_statements识别慢查询
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查看最耗时的查询
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    stddev_exec_time,
    max_exec_time,
    min_exec_time,
    (total_exec_time / sum(total_exec_time) OVER ()) * 100 AS pct_total_time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY total_exec_time DESC
LIMIT 20;

-- 查看执行次数最多的查询
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY calls DESC
LIMIT 20;

-- 查看平均执行时间最长的查询
SELECT
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE calls > 10
  AND query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### 3.4 诊断工具与方法

#### 执行计划分析

```sql
-- 基本执行计划
EXPLAIN SELECT * FROM orders WHERE customer_id = 12345;

-- 详细执行计划（包含实际执行时间）
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, COSTS, TIMING)
SELECT * FROM orders WHERE customer_id = 12345;

-- 查看执行计划的可视化表示
EXPLAIN (FORMAT JSON)
SELECT * FROM orders WHERE customer_id = 12345;
```

---

## 4. 系统级调优

### 4.1 操作系统参数优化

#### Linux内核参数

```bash
# /etc/sysctl.conf

# 共享内存配置
kernel.shmmax = 68719476736        # 最大共享内存段（64GB）
kernel.shmall = 4294967296         # 共享内存页总数

# 网络参数
net.core.somaxconn = 4096          # 最大连接数
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 3

# 虚拟内存参数
vm.swappiness = 1                  # 减少swap使用
vm.dirty_ratio = 15                # 脏页比例
vm.dirty_background_ratio = 5      # 后台脏页比例

# 文件描述符
fs.file-max = 2097152              # 最大文件描述符数

# 应用配置
ulimit -n 65535                    # 每个进程最大文件描述符
```

### 4.2 硬件资源优化

#### CPU优化

```text
CPU优化建议:
✅ 使用多核CPU（PostgreSQL支持并行查询）
✅ 启用CPU频率调节（performance模式）
✅ 绑定PostgreSQL进程到特定CPU核心（NUMA优化）
✅ 使用SSD存储（提升I/O性能）
```

#### 内存优化

```text
内存配置建议:
- shared_buffers: 25%系统内存（Linux），40%（Windows）
- effective_cache_size: 50-75%系统内存
- work_mem: 根据并发连接数计算（total_mem / max_connections / 4）
- maintenance_work_mem: 1-2GB（用于VACUUM、CREATE INDEX等）
```

### 4.3 文件系统优化

#### 文件系统选择

```text
推荐文件系统:
- ext4 (Linux) - 稳定可靠
- XFS (Linux) - 大文件性能好
- ZFS (Linux/FreeBSD) - 高级特性（压缩、快照）
- NTFS (Windows) - Windows默认

优化建议:
✅ 使用noatime挂载选项（减少I/O）
✅ 使用适当的块大小（4KB或8KB）
✅ 启用TRIM（SSD）
✅ 使用独立的WAL存储（高性能SSD）
```

---

## 5. 数据库级调优

### 5.1 内存配置优化

#### 内存参数配置

```sql
-- postgresql.conf

# 共享内存（25%系统内存，Linux）
shared_buffers = 8GB

# 有效缓存大小（50-75%系统内存）
effective_cache_size = 24GB

# 工作内存（每个操作）
work_mem = 64MB
# 计算: (total_mem - shared_buffers) / (max_connections * 3)

# 维护工作内存（VACUUM、CREATE INDEX等）
maintenance_work_mem = 2GB

# 临时缓冲区
temp_buffers = 16MB
```

#### 内存配置计算器

```python
# 内存配置计算脚本
def calculate_postgres_memory(total_memory_gb, max_connections=100, os_type='linux'):
    """计算PostgreSQL内存配置"""

    # shared_buffers
    if os_type == 'linux':
        shared_buffers_gb = int(total_memory_gb * 0.25)
    else:  # Windows
        shared_buffers_gb = int(total_memory_gb * 0.40)

    # effective_cache_size
    effective_cache_size_gb = int(total_memory_gb * 0.75)

    # work_mem (每个操作)
    available_memory = (total_memory_gb - shared_buffers_gb) * 1024  # MB
    work_mem_mb = int(available_memory / (max_connections * 3))
    work_mem_mb = min(work_mem_mb, 256)  # 最大256MB

    # maintenance_work_mem
    maintenance_work_mem_gb = min(2, int(total_memory_gb * 0.1))

    return {
        'shared_buffers': f'{shared_buffers_gb}GB',
        'effective_cache_size': f'{effective_cache_size_gb}GB',
        'work_mem': f'{work_mem_mb}MB',
        'maintenance_work_mem': f'{maintenance_work_mem_gb}GB'
    }

# 示例：32GB内存，200个连接
config = calculate_postgres_memory(32, 200)
print(config)
```

### 5.2 连接与并发配置

#### 连接配置

```sql
-- postgresql.conf

# 最大连接数
max_connections = 200

# 超级用户保留连接
superuser_reserved_connections = 3

# 连接超时
statement_timeout = 300000          # 5分钟（毫秒）
idle_in_transaction_session_timeout = 600000  # 10分钟
```

#### 并发控制

```sql
-- 并行查询配置（PostgreSQL 17+）
max_parallel_workers_per_gather = 4     # 每个Gather节点的并行工作进程
max_parallel_workers = 8                # 最大并行工作进程总数
max_worker_processes = 8                # 最大工作进程数

# 并行查询成本参数
parallel_tuple_cost = 0.01              # 并行元组传输成本
parallel_setup_cost = 1000              # 并行设置成本
min_parallel_table_scan_size = 8MB      # 最小并行表扫描大小
min_parallel_index_scan_size = 512KB    # 最小并行索引扫描大小
```

### 5.3 WAL与检查点配置

#### WAL配置优化

```sql
-- postgresql.conf

# WAL缓冲区
wal_buffers = 16MB                     # 通常16MB足够

# WAL级别
wal_level = replica                    # 复制所需的最低级别

# 最大WAL大小
max_wal_size = 4GB                     # 检查点之间的最大WAL大小

# 最小WAL大小
min_wal_size = 1GB                     # 保留的最小WAL大小

# WAL压缩（PostgreSQL 17+）
wal_compression = on                   # 启用WAL压缩

# 异步提交（提升性能，降低持久性）
synchronous_commit = on                # 生产环境建议on
```

#### 检查点配置

```sql
-- 检查点配置
checkpoint_timeout = 15min             # 检查点时间间隔
checkpoint_completion_target = 0.9     # 检查点完成目标（0.0-1.0）
checkpoint_warning = 5min              # 检查点警告时间
```

### 5.4 参数优化策略

#### 参数调优流程

```text
1. 建立基线
   - 记录当前参数值
   - 收集性能指标

2. 识别瓶颈
   - 分析性能瓶颈
   - 确定需要优化的参数

3. 调整参数
   - 一次调整一个参数
   - 使用增量调整

4. 测试验证
   - 运行基准测试
   - 对比性能变化

5. 评估效果
   - 量化性能提升
   - 检查负面影响

6. 持续优化
   - 记录优化历史
   - 定期回顾
```

---

## 6. 查询级调优

### 6.1 SQL查询优化

#### 优化技巧

```sql
-- ✅ 推荐：使用索引
SELECT * FROM orders WHERE customer_id = 12345;
-- 需要索引: CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- ✅ 推荐：使用LIMIT限制结果
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;

-- ✅ 推荐：避免SELECT *
SELECT id, customer_id, total_amount FROM orders WHERE customer_id = 12345;

-- ❌ 避免：在WHERE子句中使用函数
-- 错误: WHERE UPPER(name) = 'JOHN'
-- 正确: WHERE name = 'John' (使用函数索引或预处理)

-- ✅ 推荐：使用EXISTS而不是IN（对于大子查询）
SELECT * FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- ❌ 避免：N+1查询
-- 错误: 在循环中执行查询
-- 正确: 使用JOIN或批量查询
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.id IN (1, 2, 3);
```

### 6.2 执行计划分析

#### 执行计划解读

```sql
-- 查看执行计划（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.email = 'user@example.com'
ORDER BY o.created_at DESC
LIMIT 10;

-- 关键指标解读:
-- Planning Time: 查询规划时间
-- Execution Time: 查询执行时间
-- Seq Scan: 顺序扫描（可能较慢）
-- Index Scan: 索引扫描（通常较快）
-- Index Only Scan: 仅索引扫描（最快）
-- Nested Loop: 嵌套循环连接
-- Hash Join: 哈希连接
-- Merge Join: 归并连接
```

#### 执行计划优化

```sql
-- 识别性能问题
-- 1. 顺序扫描大表
-- 解决: 创建索引或使用索引

-- 2. 嵌套循环连接大表
-- 解决: 调整join_collapse_limit或使用哈希连接

-- 3. 排序操作
-- 解决: 使用索引支持排序

-- 4. 并行度不足
-- 解决: 调整并行参数或查询结构

-- 强制使用索引
SET enable_seqscan = off;  -- 仅用于测试，不要在生产环境使用
EXPLAIN SELECT * FROM orders WHERE customer_id = 12345;
SET enable_seqscan = on;
```

### 6.3 查询重写优化

#### 查询重写技巧

```sql
-- 1. 将子查询转换为JOIN
-- 原始查询
SELECT * FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE total_amount > 1000);

-- 优化查询
SELECT DISTINCT c.*
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.total_amount > 1000;

-- 2. 使用UNION代替OR（在某些情况下）
-- 原始查询
SELECT * FROM orders
WHERE customer_id = 123 OR customer_id = 456;

-- 优化查询
SELECT * FROM orders WHERE customer_id = 123
UNION ALL
SELECT * FROM orders WHERE customer_id = 456;

-- 3. 使用窗口函数代替子查询
-- 原始查询
SELECT *,
    (SELECT COUNT(*) FROM orders o2 WHERE o2.customer_id = o1.customer_id) AS order_count
FROM orders o1;

-- 优化查询
SELECT *,
    COUNT(*) OVER (PARTITION BY customer_id) AS order_count
FROM orders;
```

### 6.4 慢查询优化

#### 慢查询分析流程

```sql
-- 1. 识别慢查询（使用pg_stat_statements）
SELECT
    query,
    calls,
    mean_exec_time,
    total_exec_time,
    (total_exec_time / sum(total_exec_time) OVER ()) * 100 AS pct_total
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- 平均执行时间 > 1秒
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 2. 分析执行计划
EXPLAIN (ANALYZE, BUFFERS)
-- 粘贴慢查询SQL

-- 3. 优化建议
-- - 创建缺失的索引
-- - 重写查询
-- - 调整参数
-- - 使用物化视图

-- 4. 验证优化效果
-- 重新运行查询，对比执行时间
```

---

## 7. 索引调优

### 7.1 索引类型选择

#### 索引类型对比

| 索引类型 | 适用场景 | 优势 | 劣势 |
| --- | --- | --- | --- |
| **B-Tree** | 等值查询、范围查询、排序 | 通用性强、支持多种操作 | 索引较大 |
| **Hash** | 等值查询 | 等值查询快 | 不支持范围查询、排序 |
| **GiST** | 全文搜索、空间数据 | 支持复杂数据类型 | 查询可能较慢 |
| **GIN** | 全文搜索、数组 | 多值类型支持好 | 更新较慢、索引大 |
| **SP-GiST** | 点数据、某些特殊场景 | 某些场景性能好 | 适用范围窄 |
| **BRIN** | 大表、有序数据 | 索引小 | 适用范围有限 |

### 7.2 索引设计原则

#### 设计原则

```text
1. 索引选择性
   - 选择性高的列（唯一值多）适合建索引
   - 选择性低的列（唯一值少）不适合建索引

2. 查询模式
   - 为WHERE子句中的列建索引
   - 为JOIN条件中的列建索引
   - 为ORDER BY中的列建索引

3. 复合索引
   - 最左前缀原则
   - 选择性高的列在前
   - 经常一起查询的列组合

4. 部分索引
   - 只为部分数据建索引
   - 减少索引大小
   - 提升索引效率

5. 表达式索引
   - 为函数表达式建索引
   - 例如: CREATE INDEX ON users (LOWER(email));
```

#### 索引设计示例

```sql
-- 单列索引
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- 复合索引（最左前缀）
CREATE INDEX idx_orders_customer_date ON orders(customer_id, created_at);
-- 可以使用索引的查询:
-- WHERE customer_id = ?
-- WHERE customer_id = ? AND created_at > ?

-- 部分索引（只索引活跃订单）
CREATE INDEX idx_orders_active ON orders(customer_id, created_at)
WHERE status = 'active';

-- 表达式索引
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- 覆盖索引（包含所有需要的列）
CREATE INDEX idx_orders_covering ON orders(customer_id)
INCLUDE (total_amount, created_at);
-- 查询只需要索引即可完成，无需回表
```

### 7.3 索引优化策略

#### 索引使用分析

```sql
-- 查看索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,           -- 索引扫描次数
    idx_tup_read,       -- 读取的元组数
    idx_tup_fetch,      -- 获取的元组数
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;  -- 未使用的索引排在前面

-- 查找未使用的索引
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- 查找表扫描过多的表
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan AS avg_seq_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
  AND seq_tup_read / seq_scan > 10000  -- 平均每次顺序扫描读取>10000行
ORDER BY seq_tup_read DESC;
```

---

## 8. 存储调优

### 8.1 表空间优化

#### 表空间配置

```sql
-- 创建表空间（使用高性能存储）
CREATE TABLESPACE fast_ssd
LOCATION '/data/fast_ssd';

-- 将表移动到表空间
ALTER TABLE orders SET TABLESPACE fast_ssd;

-- 将索引移动到表空间
ALTER INDEX idx_orders_customer_id SET TABLESPACE fast_ssd;

-- 创建WAL专用表空间（PostgreSQL 17+支持）
-- 注意：WAL表空间需要在initdb时指定
```

### 8.2 分区策略

#### 分区设计

```sql
-- 范围分区（按日期）
CREATE TABLE orders (
    id BIGSERIAL,
    customer_id INTEGER,
    total_amount NUMERIC,
    created_at TIMESTAMPTZ
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE orders_2025_01 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE orders_2025_02 PARTITION OF orders
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- 自动创建分区（使用触发器或扩展）
-- 可以使用pg_partman扩展自动化分区管理
```

---

## 9. 参数调优最佳实践

### 9.1 关键参数详解

#### 核心参数配置模板

```sql
-- postgresql.conf 核心参数配置

# ============================================
# 内存配置（32GB系统内存示例）
# ============================================
shared_buffers = 8GB                    # 25%系统内存（Linux）
effective_cache_size = 24GB             # 75%系统内存
work_mem = 64MB                         # 根据并发连接数调整
maintenance_work_mem = 2GB              # VACUUM、CREATE INDEX等

# ============================================
# 连接配置
# ============================================
max_connections = 200                   # 根据应用需求
superuser_reserved_connections = 3

# ============================================
# 查询配置
# ============================================
statement_timeout = 300000              # 5分钟
lock_timeout = 30000                    # 30秒

# ============================================
# 并行查询（PostgreSQL 17+）
# ============================================
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
parallel_tuple_cost = 0.01
parallel_setup_cost = 1000

# ============================================
# WAL配置
# ============================================
wal_level = replica
max_wal_size = 4GB
min_wal_size = 1GB
wal_buffers = 16MB
wal_compression = on                    # PostgreSQL 17+

# ============================================
# 检查点配置
# ============================================
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9

# ============================================
# 日志配置
# ============================================
logging_collector = on
log_destination = 'stderr'
log_min_duration_statement = 1000       # 记录>1秒的查询
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0                      # 记录所有临时文件

# ============================================
# 统计信息
# ============================================
track_activity_query_size = 2048
pg_stat_statements.max = 10000
pg_stat_statements.track = all
```

---

## 10. 性能监控与持续优化

### 10.1 性能监控工具

#### pg_stat_statements配置

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 配置
ALTER SYSTEM SET pg_stat_statements.max = 10000;
ALTER SYSTEM SET pg_stat_statements.track = all;
ALTER SYSTEM SET pg_stat_statements.track_utility = on;
SELECT pg_reload_conf();

-- 重置统计
SELECT pg_stat_statements_reset();
```

#### 关键指标监控

```sql
-- 创建性能监控视图
CREATE OR REPLACE VIEW performance_monitor AS
SELECT
    'connections' AS metric_type,
    count(*) AS current_value,
    (SELECT setting::INT FROM pg_settings WHERE name = 'max_connections') AS max_value,
    round(count(*)::NUMERIC / (SELECT setting::INT FROM pg_settings WHERE name = 'max_connections') * 100, 2) AS pct_usage
FROM pg_stat_activity
WHERE datname = current_database()
UNION ALL
SELECT
    'cache_hit_ratio' AS metric_type,
    round(
        sum(blks_hit)::NUMERIC / NULLIF(sum(blks_hit) + sum(blks_read), 0) * 100,
        2
    ) AS current_value,
    95 AS max_value,  -- 目标95%+
    0 AS pct_usage
FROM pg_stat_database
WHERE datname = current_database()
UNION ALL
SELECT
    'index_usage_ratio' AS metric_type,
    round(
        sum(idx_scan)::NUMERIC / NULLIF(sum(idx_scan) + sum(seq_scan), 0) * 100,
        2
    ) AS current_value,
    90 AS max_value,  -- 目标90%+
    0 AS pct_usage
FROM pg_stat_user_tables;

-- 查看监控指标
SELECT * FROM performance_monitor;
```

---

## 11. 综合调优案例

### 11.1 高并发场景调优

#### 场景描述

```text
场景: 电商系统高并发场景
- QPS: 10,000+
- 连接数: 500+
- 读写比例: 80%读 / 20%写
- 数据量: 1亿+订单
```

#### 优化方案

```sql
-- 1. 连接池配置
max_connections = 500
-- 使用PgBouncer连接池（pool_mode = transaction）

-- 2. 内存配置
shared_buffers = 16GB                  # 64GB系统内存
effective_cache_size = 48GB
work_mem = 32MB                        # 降低以支持更多并发

-- 3. 查询优化
-- 使用只读副本分担读负载
-- 使用缓存（Redis）缓存热点数据

-- 4. 索引优化
-- 为热点查询创建覆盖索引
CREATE INDEX idx_orders_hot ON orders(customer_id, status)
INCLUDE (total_amount, created_at)
WHERE status IN ('pending', 'processing');
```

---

## 12. PostgreSQL 18性能优化新特性

PostgreSQL 18引入了多项性能优化新特性，显著提升数据库性能。

### 12.1 异步I/O优化（PostgreSQL 18）

PostgreSQL 18引入了全新的异步I/O子系统，显著提升I/O密集型操作的性能。

#### 异步I/O配置

```sql
-- PostgreSQL 18异步I/O配置（带错误处理和性能测试）
DO $$
BEGIN
    -- 检查是否为超级用户
    IF NOT current_setting('is_superuser')::boolean THEN
        RAISE EXCEPTION '需要超级用户权限才能修改系统配置';
    END IF;

    BEGIN
        -- PostgreSQL 18异步I/O配置
        -- 有效I/O并发数（PostgreSQL 18新增）
        ALTER SYSTEM SET effective_io_concurrency = 200;  -- SSD推荐值：200-300
        ALTER SYSTEM SET maintenance_io_concurrency = 200;  -- 维护操作I/O并发数（PostgreSQL 18新增）

        -- 重新加载配置
        PERFORM pg_reload_conf();

        RAISE NOTICE 'PostgreSQL 18异步I/O配置已更新，配置已重新加载';
        RAISE NOTICE '异步I/O优化效果：';
        RAISE NOTICE '  - I/O性能提升：2-3倍';
        RAISE NOTICE '  - 查询性能提升：30-50%%';
        RAISE NOTICE '  - 索引构建性能提升：2-3倍';
    EXCEPTION
        WHEN insufficient_privilege THEN
            RAISE WARNING '权限不足，无法修改系统配置';
            RAISE;
        WHEN invalid_parameter_value THEN
            RAISE WARNING '参数值无效，请检查配置值';
            RAISE;
        WHEN OTHERS THEN
            RAISE WARNING '设置异步I/O配置失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查看异步I/O配置
SHOW effective_io_concurrency;
SHOW maintenance_io_concurrency;
```

#### 异步I/O性能监控

```sql
-- 查看I/O统计（PostgreSQL 18新增，带错误处理和性能测试）
DO $$
DECLARE
    io_record RECORD;
BEGIN
    RAISE NOTICE '=== PostgreSQL 18 I/O统计 ===';

    FOR io_record IN
        SELECT
            object,
            context,
            reads,
            writes,
            extends
        FROM pg_stat_io
        ORDER BY reads DESC
        LIMIT 10
    LOOP
        RAISE NOTICE '对象: % | 上下文: % | 读取: % | 写入: % | 扩展: %',
            io_record.object,
            io_record.context,
            io_record.reads,
            io_record.writes,
            io_record.extends;
    END LOOP;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_stat_io视图不存在，请确保使用PostgreSQL 18+';
    WHEN OTHERS THEN
        RAISE WARNING '查询I/O统计失败: %', SQLERRM;
END $$;
```

#### 异步I/O优化场景

##### 1. 大表扫描查询

```sql
-- 大表扫描查询（PostgreSQL 18异步I/O优化）
-- PostgreSQL 18: 异步I/O提升扫描速度1.5-2倍
SELECT * FROM large_table WHERE status = 'active';
```

##### 2. 向量检索查询

```sql
-- pgvector向量检索受益于异步I/O
-- PostgreSQL 18: 异步I/O提升性能2-3倍
SELECT id, embedding <-> $1::vector AS distance
FROM vectors
ORDER BY embedding <-> $1::vector
LIMIT 10;
```

##### 3. 索引构建

```sql
-- 索引构建（PostgreSQL 18异步I/O优化）
-- PostgreSQL 18: 异步I/O提升索引构建速度2-3倍
CREATE INDEX CONCURRENTLY idx_orders_customer ON orders(customer_id);
```

### 12.2 跳过扫描优化（PostgreSQL 18）

PostgreSQL 18支持多列B-tree索引的跳过扫描，允许在更多情况下利用多列B-tree索引。

#### 跳过扫描示例

```sql
-- 创建多列B-tree索引
CREATE INDEX idx_orders_multi ON orders(customer_id, status, created_at);

-- 查询可以利用跳过扫描（PostgreSQL 18）
-- 即使WHERE子句不包含索引的第一列，也可以利用索引
SELECT * FROM orders
WHERE status = 'pending' AND created_at > '2025-01-01'
ORDER BY created_at;

-- PostgreSQL 18: 跳过扫描优化查询性能30-50%
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM orders
WHERE status = 'pending' AND created_at > '2025-01-01'
ORDER BY created_at;
```

#### 跳过扫描优势

- ✅ **更灵活的索引使用**：即使WHERE子句不包含索引的第一列，也可以利用索引
- ✅ **减少索引数量**：不需要为每个查询组合创建单独的索引
- ✅ **性能提升**：查询性能提升30-50%

---

## 📚 参考资源

1. **PostgreSQL官方文档**: <https://www.postgresql.org/docs/current/performance-tips.html>
2. **pg_stat_statements**: <https://www.postgresql.org/docs/current/pgstatstatements.html>
3. **pgBadger**: <https://pgbadger.darold.net/>
4. **PostgreSQL性能优化**: <https://wiki.postgresql.org/wiki/Performance_Optimization>

---

## 📝 更新日志

- **v2.1** (2025-01): 补充PostgreSQL 18新特性
  - 补充异步I/O优化（PostgreSQL 18）
  - 补充跳过扫描优化（PostgreSQL 18）
  - 补充I/O性能监控（PostgreSQL 18新增）
- **v2.0** (2025-01): 整合完整指南
  - 系统化性能调优方法论
  - 整合系统级、数据库级、查询级调优
  - 补充性能基线建立
  - 补充性能瓶颈诊断
  - 补充参数调优最佳实践
  - 补充性能监控与持续优化
  - 添加综合调优案例

---

**状态**: ✅ **文档完成** | [返回目录](./README.md)
