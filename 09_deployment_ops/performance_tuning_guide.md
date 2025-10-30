# ⚡ PostgreSQL 17 性能优化最佳实践

**文档版本**：v1.0  
**创建日期**：2025 年 10 月 3 日  
**适用版本**：PostgreSQL 17.x

---

## 🎯 目标

通过系统化的性能优化方法，提升 PostgreSQL 17 的查询性能、吞吐量和响应时间。

---

## 📊 性能优化方法论

### 优化流程

```text
1. 性能监控 → 2. 问题识别 → 3. 根因分析 → 4. 优化实施 → 5. 效果验证
     ↑                                                              ↓
     └──────────────────── 持续改进 ←──────────────────────────────┘
```

---

## 🔍 性能监控基础

### 1. 关键性能指标（KPIs）

#### 1.1 查询性能

**慢查询识别**：

```sql
-- 启用pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- TOP 10慢查询（按平均时间）
SELECT
    query,
    calls,
    ROUND(mean_exec_time::numeric, 2) as avg_ms,
    ROUND(total_exec_time::numeric, 2) as total_ms,
    ROUND((100 * total_exec_time / SUM(total_exec_time) OVER ())::numeric, 2) as percent
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**目标**：

- 🟢 优秀：平均查询时间 < 10ms
- 🟡 良好：平均查询时间 < 100ms
- 🔴 需优化：平均查询时间 > 1000ms

---

#### 1.2 缓存命中率

```sql
-- 数据库缓存命中率
SELECT
    datname,
    ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) as cache_hit_ratio
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1', 'postgres')
ORDER BY cache_hit_ratio;
```

**目标**：

- 🟢 优秀：> 99%
- 🟡 良好：95-99%
- 🔴 需优化：< 95%

---

#### 1.3 表膨胀率

```sql
-- 表膨胀检测
SELECT
    schemaname || '.' || tablename as table_name,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) as bloat_percent,
    n_dead_tup,
    n_live_tup,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_stat_user_tables
WHERE n_live_tup > 0
ORDER BY bloat_percent DESC NULLS LAST
LIMIT 20;
```

**目标**：

- 🟢 优秀：< 10%
- 🟡 良好：10-20%
- 🔴 需优化：> 20%

---

## 🎯 查询优化

### 2. EXPLAIN 分析

#### 2.1 EXPLAIN 命令

**基础 EXPLAIN**：

```sql
EXPLAIN SELECT * FROM orders WHERE customer_id = 100;
```

**详细分析（推荐）**：

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT * FROM orders WHERE customer_id = 100;
```

**输出解读**：

```text
Bitmap Heap Scan on orders  (cost=4.15..108.27 rows=100 width=50)
                            (actual time=0.023..0.045 rows=5 loops=1)
  Buffers: shared hit=8
  ->  Bitmap Index Scan on idx_customer_id  (cost=0.00..4.13 rows=100 width=0)
                                            (actual time=0.015..0.015 rows=5 loops=1)
        Buffers: shared hit=2
```

**关键指标**：

- `cost`: 估计成本
- `rows`: 估计行数
- `actual time`: 实际执行时间
- `Buffers`: 缓冲区使用情况

---

#### 2.2 常见问题与解决

**问题 1：全表扫描（Seq Scan）**

```sql
-- 问题查询
EXPLAIN SELECT * FROM large_table WHERE status = 'active';

-- Seq Scan on large_table  (cost=0.00..1000000.00 rows=50000 width=100)
```

**解决方案：创建索引**

```sql
CREATE INDEX idx_large_table_status ON large_table(status);
```

---

**问题 2：索引未使用**

```sql
-- 查询
EXPLAIN SELECT * FROM orders WHERE amount::text = '100';

-- 由于类型转换，索引失效
```

**解决方案：避免类型转换**

```sql
-- 正确写法
SELECT * FROM orders WHERE amount = 100;
```

---

**问题 3：JOIN 顺序不当**

```sql
-- 问题：小表驱动大表
SELECT * FROM huge_table h
JOIN small_table s ON h.id = s.id;
```

**解决方案：使用 CTE 或调整 JOIN 顺序**

```sql
-- 使用CTE让优化器更好地选择计划
WITH filtered_small AS (
    SELECT * FROM small_table WHERE condition = true
)
SELECT * FROM huge_table h
JOIN filtered_small s ON h.id = s.id;
```

---

### 3. 索引优化

#### 3.1 索引类型选择

**B-tree 索引（默认，最常用）**：

```sql
-- 适用：等值查询、范围查询、排序
CREATE INDEX idx_orders_date ON orders(order_date);

-- 复合索引
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
```

**使用场景**：

- =, <, >, <=, >=, BETWEEN
- ORDER BY, SORT
- 90%的查询场景

---

**Hash 索引（等值查询）**：

```sql
-- 适用：仅等值查询
CREATE INDEX idx_users_email_hash ON users USING hash(email);
```

**使用场景**：

- 仅 = 操作符
- 大表的精确匹配
- PostgreSQL 10+支持 WAL

---

**GIN 索引（多值字段）**：

```sql
-- 适用：数组、JSON、全文搜索
CREATE INDEX idx_posts_tags ON posts USING gin(tags);
CREATE INDEX idx_docs_content ON documents USING gin(to_tsvector('english', content));
```

**使用场景**：

- JSONB 字段查询
- 数组包含查询（@>, &&）
- 全文搜索

---

**GiST 索引（地理数据）**：

```sql
-- 适用：PostGIS地理查询
CREATE INDEX idx_locations_geom ON locations USING gist(geom);
```

**使用场景**：

- 地理位置查询
- 范围查询
- 最近邻查询

---

**BRIN 索引（大表）**：

```sql
-- 适用：大表、顺序数据
CREATE INDEX idx_logs_timestamp ON logs USING brin(timestamp);
```

**使用场景**：

- 时序数据
- 日志表
- 数据自然排序

**优势**：索引体积极小（1MB vs 100MB）

---

#### 3.2 索引维护

**检查索引使用情况**：

```sql
-- 未使用的索引
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;
```

**删除无用索引**：

```sql
DROP INDEX IF EXISTS unused_index_name;
```

**重建索引（减少膨胀）**：

```sql
-- 在线重建（推荐）
REINDEX INDEX CONCURRENTLY index_name;

-- 重建表的所有索引
REINDEX TABLE CONCURRENTLY table_name;
```

---

#### 3.3 部分索引（节省空间）

```sql
-- 仅索引活跃订单
CREATE INDEX idx_orders_active ON orders(order_date)
WHERE status = 'active';

-- 大幅减小索引大小，提升性能
```

**使用场景**：

- 只查询某个状态的数据
- 过滤大量历史数据
- 节省索引空间

---

### 4. 查询改写技巧

#### 4.1 避免 SELECT \*

**问题**：

```sql
-- 获取所有列，包括不需要的大字段
SELECT * FROM products;
```

**优化**：

```sql
-- 只选择需要的列
SELECT id, name, price FROM products;
```

**收益**：减少 I/O，提升网络传输效率

---

#### 4.2 使用 EXISTS 替代 IN

**问题**：

```sql
-- IN子查询可能性能不佳
SELECT * FROM orders
WHERE customer_id IN (SELECT id FROM customers WHERE region = 'Asia');
```

**优化**：

```sql
-- EXISTS通常更快
SELECT * FROM orders o
WHERE EXISTS (
    SELECT 1 FROM customers c
    WHERE c.id = o.customer_id AND c.region = 'Asia'
);
```

---

#### 4.3 JOIN 替代子查询

**问题**：

```sql
-- 相关子查询
SELECT
    id,
    name,
    (SELECT SUM(amount) FROM orders WHERE customer_id = c.id) as total
FROM customers c;
```

**优化**：

```sql
-- JOIN + GROUP BY
SELECT
    c.id,
    c.name,
    COALESCE(SUM(o.amount), 0) as total
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;
```

---

#### 4.4 LIMIT 优化

**问题**：

```sql
-- 大偏移量分页
SELECT * FROM products ORDER BY id LIMIT 100 OFFSET 100000;
```

**优化（游标分页）**：

```sql
-- 使用WHERE替代OFFSET
SELECT * FROM products
WHERE id > 100000
ORDER BY id
LIMIT 100;
```

**收益**：从 O(n)优化到 O(1)

---

## 🗄️ 表设计优化

### 5. 数据类型选择

#### 5.1 选择合适的数据类型

**整数类型**：

```sql
-- 避免过度使用BIGINT
id INTEGER  -- 21亿范围，足够大多数场景
-- 而不是
id BIGINT   -- 922京范围，占用更多空间
```

**字符类型**：

```sql
-- 使用VARCHAR(n)而不是TEXT（如果长度有限）
email VARCHAR(255)  -- 明确长度限制
-- 而不是
email TEXT  -- 无限制，可能导致滥用
```

**枚举类型**：

```sql
-- 使用ENUM代替VARCHAR
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'completed', 'cancelled');

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    status order_status NOT NULL DEFAULT 'pending'
);
```

**收益**：

- 节省存储空间（1 字节 vs 可变长度）
- 提升查询性能
- 数据完整性保证

---

#### 5.2 分区表

**范围分区（时间序列数据）**：

```sql
-- 创建分区表
CREATE TABLE logs (
    id BIGSERIAL,
    timestamp TIMESTAMP NOT NULL,
    message TEXT
) PARTITION BY RANGE (timestamp);

-- 创建分区
CREATE TABLE logs_2024_01 PARTITION OF logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE logs_2024_02 PARTITION OF logs
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 创建索引
CREATE INDEX ON logs_2024_01(timestamp);
CREATE INDEX ON logs_2024_02(timestamp);
```

**收益**：

- 查询只扫描相关分区
- 易于删除历史数据（DROP PARTITION）
- 维护窗口更小

---

**列表分区（按地区/类别）**：

```sql
CREATE TABLE sales (
    id SERIAL,
    region VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2)
) PARTITION BY LIST (region);

CREATE TABLE sales_asia PARTITION OF sales FOR VALUES IN ('Asia', 'China', 'Japan');
CREATE TABLE sales_europe PARTITION OF sales FOR VALUES IN ('Europe', 'UK', 'Germany');
```

---

### 6. VACUUM 与维护

#### 6.1 VACUUM 配置

**postgresql.conf**：

```ini
# Autovacuum配置
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 30s  # 更频繁

# VACUUM阈值（更激进）
autovacuum_vacuum_scale_factor = 0.05  # 默认0.2
autovacuum_analyze_scale_factor = 0.025  # 默认0.1

# 成本限制（更高=更快）
autovacuum_vacuum_cost_limit = 2000  # 默认200
```

---

#### 6.2 手动 VACUUM

```sql
-- VACUUM单表
VACUUM VERBOSE orders;

-- VACUUM + ANALYZE
VACUUM ANALYZE orders;

-- VACUUM FULL（需要排他锁，慎用）
VACUUM FULL orders;  -- 重建表，回收空间

-- 仅ANALYZE（更新统计信息）
ANALYZE orders;
```

**最佳实践**：

- 大批量 DML 后手动 VACUUM
- 定期（每周）ANALYZE
- 避免生产高峰期 VACUUM FULL

---

## 💾 配置参数优化

### 7. 内存参数

#### 7.1 shared_buffers

```ini
# 推荐值：RAM的25%
# 64GB RAM示例
shared_buffers = 16GB
```

**调优建议**：

- 小于 32GB RAM：25%的 RAM
- 大于 32GB RAM：8-16GB 即可
- 配合 OS 文件系统缓存

---

#### 7.2 work_mem

```ini
# 每个查询操作的内存
# 计算公式：总RAM / (max_connections * 预期并发查询操作)
# 示例：64GB / (200 * 2) = 160MB
work_mem = 160MB
```

**注意**：

- 排序、Hash Join 会使用 work_mem
- 一个查询可能使用多个 work_mem
- 过大可能导致 OOM

---

#### 7.3 maintenance_work_mem

```ini
# VACUUM、CREATE INDEX使用
maintenance_work_mem = 2GB
```

---

### 8. 查询规划器参数

#### 8.1 SSD 优化

```ini
# SSD专用优化
random_page_cost = 1.1  # 默认4.0（HDD）
effective_io_concurrency = 200  # SSD并发
```

**效果**：优化器更倾向使用索引

---

#### 8.2 并行查询

```ini
# PostgreSQL 9.6+
max_parallel_workers_per_gather = 4  # 每个查询
max_parallel_workers = 8  # 全局
max_worker_processes = 8

# 并行查询阈值
min_parallel_table_scan_size = 8MB
min_parallel_index_scan_size = 512kB
```

**测试并行效果**：

```sql
-- 关闭并行
SET max_parallel_workers_per_gather = 0;
EXPLAIN ANALYZE SELECT * FROM large_table WHERE ...;

-- 开启并行
SET max_parallel_workers_per_gather = 4;
EXPLAIN ANALYZE SELECT * FROM large_table WHERE ...;
```

---

## 📊 连接池优化

### 9. PgBouncer 配置

**安装**：

```bash
sudo apt install pgbouncer
```

**配置（/etc/pgbouncer/pgbouncer.ini）**：

```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

# 连接池模式
pool_mode = transaction  # 推荐

# 连接池大小
default_pool_size = 25
max_client_conn = 1000
```

**pool_mode 选择**：

- `session`: 一个客户端连接对应一个数据库连接
- `transaction`: 事务结束后释放连接（推荐）
- `statement`: 每个语句后释放（适用只读查询）

---

## 🔍 性能问题诊断

### 10. 常见问题排查

#### 10.1 锁等待

```sql
-- 查看当前锁
SELECT
    pid,
    usename,
    pg_blocking_pids(pid) as blocked_by,
    query
FROM pg_stat_activity
WHERE wait_event_type = 'Lock';
```

**解决方案**：

- 优化事务，减少持锁时间
- 使用 NOWAIT 或锁超时
- 考虑 SKIP LOCKED

---

#### 10.2 连接数耗尽

```sql
-- 查看连接数
SELECT COUNT(*) FROM pg_stat_activity;

-- 查看最大连接数
SHOW max_connections;
```

**解决方案**：

- 使用连接池（PgBouncer）
- 增加 max_connections（需重启）
- 排查连接泄漏

---

## 📈 性能测试

### 11. pgbench 基准测试

**初始化**：

```bash
pgbench -i -s 100 testdb  # scale=100
```

**TPS 测试**：

```bash
# 4个客户端，持续60秒
pgbench -c 4 -j 2 -T 60 testdb
```

**结果解读**：

```text
tps = 5234.567890 (including connections establishing)
tps = 5238.901234 (excluding connections establishing)
```

---

## ✅ 性能优化检查清单

### 查询级别

- [ ] 慢查询已识别（pg_stat_statements）
- [ ] EXPLAIN 已分析
- [ ] 索引已优化
- [ ] 查询已改写

### 表级别

- [ ] 数据类型已优化
- [ ] 表膨胀已检查（VACUUM）
- [ ] 分区表已考虑（大表）
- [ ] 统计信息已更新（ANALYZE）

### 数据库级别

- [ ] 配置参数已调优
- [ ] 连接池已配置
- [ ] 缓存命中率>95%
- [ ] 监控告警已设置

---

## 🚀 持续优化

### 优化循环

1. **每日**：查看慢查询日志
2. **每周**：审查 TOP 10 慢查询
3. **每月**：性能基线对比
4. **每季度**：全面性能审计

---

**文档维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025 年 10 月 3 日  
**相关文档**：

- [production_deployment_checklist.md](production_deployment_checklist.md)
- [monitoring_metrics.md](monitoring_metrics.md)
- [monitoring_queries.sql](monitoring_queries.sql)

🎯 **持续优化，追求卓越性能！**
