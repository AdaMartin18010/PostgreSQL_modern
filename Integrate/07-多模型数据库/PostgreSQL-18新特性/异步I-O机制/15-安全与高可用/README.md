# 15. 性能基准测试工具

> **章节编号**: 15
> **章节标题**: 性能基准测试工具
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 15. 性能基准测试工具

## 📑 目录

- [15.1 pgbench基准测试](#151-pgbench基准测试)
- [15.2 自定义性能测试工具](#152-自定义性能测试工具)
- [15.3 性能对比工具](#153-性能对比工具)

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

**返回**: [文档首页](../README.md) | [上一章节](../14-常见问题FAQ/README.md) | [下一章节](../16-性能测试工具/README.md)
