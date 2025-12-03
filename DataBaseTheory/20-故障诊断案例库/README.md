# 故障诊断案例库

> **PostgreSQL 18**
> **真实故障与解决方案**

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

---

## 🔍 快速诊断

### 性能问题

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

### 锁问题

```sql
-- 查找锁等待
SELECT blocked.pid, blocked.query, blocking.pid, blocking.query
FROM pg_stat_activity blocked
JOIN pg_locks ...
WHERE NOT blocked_lock.granted;
```

### 内存问题

```sql
-- ⭐ PostgreSQL 18
SELECT name, type, path,
    pg_size_pretty(used_bytes) as used
FROM pg_backend_memory_contexts
WHERE used_bytes > 100*1024*1024
ORDER BY used_bytes DESC;
```

---

## 📖 更多资源

- [故障诊断手册](../00-总览/PostgreSQL18故障诊断手册-2025-12-04.md)
- [性能调优案例](../00-总览/PostgreSQL18性能调优案例-2025-12-04.md)

---

**持续更新中** 🚀
