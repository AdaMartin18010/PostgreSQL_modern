# PostgreSQL 17 vs 16 性能测试指南

> 完整的性能测试执行指南

---

## 📋 测试前准备

### 1. 环境要求

**硬件**：

- CPU: 8核心以上
- 内存: 32GB以上
- 磁盘: SSD，100GB+可用空间
- 网络: 1Gbps+

**软件**：

- PostgreSQL 16.x（用于基准测试）
- PostgreSQL 17.0（用于对比测试）
- pgbench（随PostgreSQL安装）
- psql客户端

### 2. 创建测试数据库

```bash
# PG16测试库
createdb -h pg16_host -p 5432 pg16_bench

# PG17测试库
createdb -h pg17_host -p 5432 pg17_bench
```

### 3. 配置数据库参数

确保两个版本使用相同的配置：

```ini
# postgresql.conf (PG16 & PG17)
shared_buffers = 8GB
effective_cache_size = 24GB
maintenance_work_mem = 2GB
work_mem = 256MB
max_connections = 100
max_parallel_workers_per_gather = 4
```

---

## 🧪 运行测试

### 测试1：JSON处理性能

```bash
# PG16
psql -h pg16_host -d pg16_bench -f scripts/01_json_performance.sql > results/pg16_json.log 2>&1

# PG17
psql -h pg17_host -d pg17_bench -f scripts/01_json_performance.sql > results/pg17_json.log 2>&1

# 对比结果
diff results/pg16_json.log results/pg17_json.log
```

**关注指标**：

- Execution Time（执行时间）
- Planning Time（规划时间）
- Shared Buffers Hit/Read（缓冲池命中率）

---

### 测试2：B-tree索引多值搜索

```bash
# PG16
psql -h pg16_host -d pg16_bench -f scripts/02_btree_in_optimization.sql > results/pg16_btree.log 2>&1

# PG17
psql -h pg17_host -d pg17_bench -f scripts/02_btree_in_optimization.sql > results/pg17_btree.log 2>&1
```

**关注指标**：

- Index Scan次数
- 执行时间
- Buffer使用量

---

### 测试3：VACUUM性能

```bash
# PG16
psql -h pg16_host -d pg16_bench -f scripts/03_vacuum_performance.sql > results/pg16_vacuum.log 2>&1

# PG17
psql -h pg17_host -d pg17_bench -f scripts/03_vacuum_performance.sql > results/pg17_vacuum.log 2>&1
```

**关注指标**：

- VACUUM执行时间
- 内存使用峰值（查看日志）
- I/O读写量

---

### 测试4：TPC-C基准测试（高并发写入）

```bash
# 初始化TPC-C数据（两个版本分别执行）
pgbench -i -s 100 -h pg16_host -d pg16_bench
pgbench -i -s 100 -h pg17_host -d pg17_bench

# 运行TPC-C测试（50并发，30分钟）
pgbench -c 50 -j 10 -T 1800 -h pg16_host -d pg16_bench > results/pg16_tpcc.log 2>&1
pgbench -c 50 -j 10 -T 1800 -h pg17_host -d pg17_bench > results/pg17_tpcc.log 2>&1

# 提取TPS结果
grep "tps" results/pg16_tpcc.log
grep "tps" results/pg17_tpcc.log
```

---

## 📊 结果分析

### 1. 提取执行时间

```bash
# 从日志中提取关键指标
grep "Execution Time" results/*.log | sort

# 计算性能提升百分比
python3 << EOF
pg16_time = 1234.5  # 替换为实际值
pg17_time = 856.3   # 替换为实际值
improvement = ((pg16_time - pg17_time) / pg16_time) * 100
print(f"性能提升: {improvement:.2f}%")
EOF
```

### 2. 生成对比报告

```bash
# 创建报告目录
mkdir -p results/summary

# 生成Markdown格式的对比表
cat > results/summary/comparison.md << 'EOF'
# PostgreSQL 17 vs 16 性能对比结果

## JSON处理
| 指标 | PG16 | PG17 | 提升 |
|------|------|------|------|
| 执行时间 | XXXms | XXXms | XX% |

## B-tree索引
| 指标 | PG16 | PG17 | 提升 |
|------|------|------|------|
| 执行时间 | XXXms | XXXms | XX% |

## VACUUM
| 指标 | PG16 | PG17 | 提升 |
|------|------|------|------|
| 执行时间 | XXXmin | XXXmin | XX% |

## TPC-C
| 指标 | PG16 | PG17 | 提升 |
|------|------|------|------|
| TPS | XXXX | XXXX | XX% |
EOF
```

---

## 📈 性能监控

### 实时监控（在测试过程中）

```sql
-- 监控活动查询
SELECT
    pid,
    usename,
    application_name,
    state,
    query_start,
    now() - query_start AS duration,
    LEFT(query, 100) AS query_preview
FROM pg_stat_activity
WHERE state = 'active'
  AND pid != pg_backend_pid()
ORDER BY duration DESC;

-- 监控I/O统计
SELECT * FROM pg_stat_bgwriter;

-- 监控VACUUM进度
SELECT * FROM pg_stat_progress_vacuum;

-- 监控表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## ⚠️ 注意事项

### 1. 测试隔离

- ✅ 使用专用测试环境
- ✅ 避免与生产环境混合
- ✅ 每次测试前重启数据库

### 2. 数据一致性

- ✅ 两个版本使用相同的测试数据
- ✅ 使用相同的配置参数
- ✅ 使用相同的硬件环境

### 3. 多次测试

- ✅ 每个测试至少运行3次
- ✅ 取中位数或平均值
- ✅ 记录标准差

### 4. 系统预热

- ✅ 测试前先运行一次预热查询
- ✅ 等待缓存填充
- ✅ 清除操作系统缓存（如需要）

```bash
# Linux清除系统缓存
sync
echo 3 > /proc/sys/vm/drop_caches
```

---

## 🐛 故障排查

### 问题1：连接失败

```bash
# 检查PostgreSQL服务状态
pg_ctl status -D /path/to/data

# 检查端口监听
netstat -an | grep 5432

# 测试连接
psql -h localhost -U postgres -c "SELECT version();"
```

### 问题2：内存不足

```sql
-- 降低配置参数
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET work_mem = '128MB';
SELECT pg_reload_conf();
```

### 问题3：磁盘空间不足

```bash
# 检查磁盘空间
df -h

# 清理旧数据
DROP TABLE IF EXISTS old_test_table CASCADE;
VACUUM FULL;
```

---

## 📚 参考资源

- PostgreSQL性能调优: <https://wiki.postgresql.org/wiki/Performance_Optimization>
- pgbench文档: <https://www.postgresql.org/docs/17/pgbench.html>
- EXPLAIN详解: <https://www.postgresql.org/docs/17/using-explain.html>

---

**版本**：1.0.0  
**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03
