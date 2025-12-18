# 故障诊断案例库

> **PostgreSQL 18**
> **真实故障与解决方案**
> **6个文档，22个案例**

---

## 📚 案例分类

### 性能问题

| 案例 | 症状 | 根因 | 解决方案 |
|------|------|------|---------|
| [慢查询](./01-慢查询诊断.md) | 查询15秒 | 缺失索引 | 创建索引 -99.9% |
| [JOIN慢](./01-慢查询诊断.md) | JOIN 45秒 | 统计信息过期 | ANALYZE -87% |
| [N+1查询](./01-慢查询诊断.md) | 1000次查询 | 应用代码问题 | 改用JOIN -95% |

### 锁问题

| 案例 | 症状 | 根因 | 解决方案 |
|------|------|------|---------|
| [长事务阻塞](./02-锁冲突诊断.md) | timeout | idle in transaction | 设置超时 |
| [死锁](./02-锁冲突诊断.md) | deadlock | 表访问顺序不一致 | 统一顺序 |
| [DDL阻塞](./02-锁冲突诊断.md) | ALTER等待 | 长查询持有锁 | CONCURRENTLY |

### 内存问题

| 案例 | 症状 | 根因 | 解决方案 |
|------|------|------|---------|
| [work_mem溢出](./03-内存溢出诊断.md) | 80GB临时文件 | work_mem太小 | 增加work_mem |
| [OOM](./03-内存溢出诊断.md) | 进程被杀 | 大结果集查询 | LIMIT+优化 |
| [缓存命中低](./03-内存溢出诊断.md) | I/O高 | shared_buffers小 | 增加到25%内存 |

### 连接问题

| 案例 | 症状 | 根因 | 解决方案 |
|------|------|------|---------|
| [连接数耗尽](./04-连接问题诊断.md) | 无法建立连接 | 连接泄漏 | 连接池+超时 |
| [连接超时](./04-连接问题诊断.md) | timeout | 慢查询/锁等待 | 优化查询 |
| [连接泄漏](./04-连接问题诊断.md) | 连接数持续增长 | 应用未关闭连接 | 使用连接池 |

### 复制问题

| 案例 | 症状 | 根因 | 解决方案 |
|------|------|------|---------|
| [复制延迟高](./05-复制问题诊断.md) | 延迟>1分钟 | 网络/从库负载 | 优化配置 |
| [复制中断](./05-复制问题诊断.md) | not streaming | 网络/配置错误 | 检查连接 |
| [逻辑复制延迟](./05-复制问题诊断.md) | 数据不同步 | 大表/配置 | 优化订阅 |

### 存储问题

| 案例 | 症状 | 根因 | 解决方案 |
|------|------|------|---------|
| [表膨胀严重](./06-存储问题诊断.md) | 表持续增长 | 死元组未清理 | VACUUM FULL |
| [磁盘空间不足](./06-存储问题诊断.md) | 无法写入 | 空间耗尽 | 清理/扩展 |
| [VACUUM不工作](./06-存储问题诊断.md) | autovacuum未运行 | 配置/阻塞 | 调整参数 |
| [索引膨胀](./06-存储问题诊断.md) | 索引异常大 | 索引碎片 | REINDEX |
| [WAL空间过大](./06-存储问题诊断.md) | WAL>50GB | checkpoint少 | 调整checkpoint |

---

## 🔍 快速诊断SQL

### 1. 性能问题诊断

```sql
-- 1. 找慢查询
SELECT * FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC LIMIT 10;

-- 2. 看执行计划
EXPLAIN (ANALYZE, BUFFERS) <your_query>;

-- 3. 检查索引
SELECT * FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

### 2. 锁问题诊断

```sql
-- 查找锁等待（完整查询）
SELECT
    blocked.pid AS blocked_pid,
    blocked.query AS blocked_query,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query,
    blocking.state,
    blocking.query_start,
    now() - blocking.query_start AS blocking_duration
FROM pg_stat_activity blocked
JOIN pg_locks blocked_lock ON blocked.pid = blocked_lock.pid
JOIN pg_locks blocking_lock ON blocking_lock.locktype = blocked_lock.locktype
    AND blocking_lock.pid != blocked_lock.pid
    AND blocking_lock.relation = blocked_lock.relation
JOIN pg_stat_activity blocking ON blocking.pid = blocking_lock.pid
WHERE NOT blocked_lock.granted
  AND blocking_lock.granted
ORDER BY blocking_duration DESC;

-- 查找长事务（可能持锁）
SELECT
    pid,
    usename,
    state,
    query,
    query_start,
    now() - query_start AS duration,
    xact_start,
    now() - xact_start AS xact_duration
FROM pg_stat_activity
WHERE state = 'idle in transaction'
   OR (now() - xact_start) > interval '10 minutes'
ORDER BY xact_duration DESC;
```

### 3. 内存问题诊断

```sql
-- ⭐ PostgreSQL 18：增强的内存诊断
SELECT
    name,
    type,
    path,
    pg_size_pretty(total_bytes) AS total,
    pg_size_pretty(used_bytes) AS used,
    pg_size_pretty(free_bytes) AS free,
    round(100.0 * used_bytes / NULLIF(total_bytes, 0), 2) AS usage_pct
FROM pg_backend_memory_contexts
WHERE used_bytes > 100 * 1024 * 1024  -- >100MB
ORDER BY used_bytes DESC;

-- 查找内存使用最多的会话
SELECT
    pid,
    usename,
    query,
    state,
    pg_size_pretty(
        (SELECT sum(used_bytes)
         FROM pg_backend_memory_contexts
         WHERE pid = pg_stat_activity.pid)
    ) AS total_mem_used
FROM pg_stat_activity
WHERE pid IN (
    SELECT DISTINCT pid
    FROM pg_backend_memory_contexts
    WHERE used_bytes > 100 * 1024 * 1024
)
ORDER BY total_mem_used DESC;

-- 检查临时文件使用
SELECT
    datname,
    temp_files,
    temp_bytes,
    pg_size_pretty(temp_bytes) AS temp_size,
    round(100.0 * temp_bytes / NULLIF(temp_bytes + blks_hit * current_setting('block_size')::int, 0), 2) AS temp_ratio
FROM pg_stat_database
WHERE temp_bytes > 0
ORDER BY temp_bytes DESC;
```

---

## 🔧 诊断工具

### PostgreSQL 18 新特性

- **`pg_backend_memory_contexts`**: 详细的内存上下文诊断
- **增强的锁信息**: 更详细的锁等待链
- **改进的统计信息**: 多变量统计支持

### 常用诊断视图

| 视图 | 用途 | 关键字段 |
|-----|------|---------|
| `pg_stat_activity` | 活动会话 | `state`, `query`, `wait_event` |
| `pg_stat_statements` | 查询统计 | `mean_exec_time`, `calls` |
| `pg_locks` | 锁信息 | `mode`, `granted`, `pid` |
| `pg_stat_user_tables` | 表统计 | `seq_scan`, `idx_scan`, `n_dead_tup` |
| `pg_backend_memory_contexts` | 内存使用 | `used_bytes`, `total_bytes` |

## 📊 诊断流程

### 性能问题诊断流程

```text
1. 识别症状
   ├─ 查询慢？
   ├─ 连接超时？
   └─ 系统负载高？

2. 收集数据
   ├─ pg_stat_statements（慢查询）
   ├─ EXPLAIN ANALYZE（执行计划）
   └─ pg_stat_activity（活动会话）

3. 分析根因
   ├─ 索引缺失？
   ├─ 统计信息过期？
   ├─ 锁等待？
   └─ 内存不足？

4. 实施解决方案
   └─ 创建索引 / ANALYZE / 优化查询
```

### 2. 锁问题诊断流程

```text
1. 识别症状
   └─ 查询等待 / 超时

2. 查找阻塞
   ├─ 查询锁等待链
   └─ 查找长事务

3. 分析根因
   ├─ idle in transaction？
   ├─ 死锁？
   └─ DDL阻塞？

4. 解决
   ├─ 终止阻塞会话
   ├─ 设置超时
   └─ 优化事务
```

### 3. 内存问题诊断流程

```text
1. 识别症状
   ├─ OOM Killer？
   ├─ 临时文件多？
   └─ 缓存命中率低？

2. 诊断
   ├─ pg_backend_memory_contexts（内存使用）
   ├─ pg_stat_database（临时文件）
   └─ pg_statio_user_tables（缓存命中率）

3. 分析根因
   ├─ work_mem太小？
   ├─ 大结果集查询？
   └─ shared_buffers不足？

4. 解决
   ├─ 增加work_mem
   ├─ 优化查询（LIMIT）
   └─ 增加shared_buffers
```

## 📖 更多资源

- [故障诊断手册](../00-总览/PostgreSQL18故障诊断手册-2025-12-04.md)
- [性能调优案例](../00-总览/PostgreSQL18性能调优案例-2025-12-04.md)
- [核心理论模型](../90-事务与并发设计理论体系/01-核心理论模型/)

## 🎯 案例贡献

欢迎贡献真实故障案例！

**案例格式**:

- 症状描述
- 诊断步骤
- 根因分析
- 解决方案
- 效果评估

---

**持续更新中** 🚀
