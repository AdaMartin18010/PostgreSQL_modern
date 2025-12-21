# 代码示例性能测试补充报告

> **生成日期**: 2025年1月
> **扫描结果**: 找到 998 个需要添加性能测试的代码示例

---

## 📊 统计信息

- **需要性能测试的代码示例**: 998 个

## 📋 需要性能测试的代码示例

### 01-AIO异步IO完整深度指南.md

**行 355** (sql, query):

```sql
-- 1. 启用AIO（默认on）
SHOW io_direct;  -- 需要设置为'data'或'all'才能使用AIO
ALTER SYSTEM SET io_direct = 'data';  -- 启用direct I/O

-- 2. io_uring队列深度
SHOW io_uring_queue_depth;  -- 默认256
ALTER SYSTEM SET io_uring_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 405** (sql, query):

```sql
-- 全表扫描
SELECT COUNT(*) FROM large_table;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 442** (sql, query):

```sql
-- 使用索引的位图扫描
SELECT * FROM orders
WHERE status = 'pending' AND created_at > '2024-01-01';
-- 结果集：100万行（总表10亿行）

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 632** (sql, query):

```sql
-- 执行EXPLAIN ANALYZE
EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*) FROM large_table;

-- 查看输出中是否有"Prefetch"相关信息
-- PostgreSQL 18会显示预读信息

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 642** (sql, query):

```sql
-- 查看I/O统计
SELECT * FROM pg_stat_io WHERE context = 'normal';

-- 如果AIO生效，reads和read_time的比例会改善

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 657** (sql, query):

```sql
-- 1. 查看I/O统计
SELECT
    backend_type,
    object,
    context,
    reads,
    read_time,
    writes,
    write_time,
    CASE WHEN reads > 0
         THEN round(read_time::numeric / reads, 2)

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 698** (sql, query):

```sql
-- effective_io_concurrency越大，预读越激进
-- 但也会占用更多shared_buffers

-- 测试不同值
SET effective_io_concurrency = 50;
EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*) FROM large_table;
-- 记录时间

SET effective_io_concurr
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 725** (sql, query):

```sql
-- 更大的队列=更多并发I/O，但占用更多内存
-- 每个队列项约128字节

-- 256（默认）：占用32KB
-- 512：占用64KB
-- 1024：占用128KB

-- 推荐根据workload测试
ALTER SYSTEM SET io_uring_queue_depth = 512;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 824** (sql, query):

```sql
-- 降低队列深度
ALTER SYSTEM SET io_uring_queue_depth = 128;

-- 或降低并发度
ALTER SYSTEM SET max_parallel_workers_per_gather = 2;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 846** (sql, query):

```sql
-- 每日统计查询
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS orders,
    SUM(amount) AS revenue
FROM orders
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(created_at);

-- 执行时间：
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 862** (sql, query):

```sql
-- 1. 启用AIO
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET effective_io_concurrency = 200;

-- 2. 重启

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 904** (sql, query):

```sql
-- 启用AIO for VACUUM
ALTER SYSTEM SET maintenance_io_concurrency = 200;
ALTER SYSTEM SET io_direct = 'data';

-- 调整autovacuum
ALTER SYSTEM SET autovacuum_vacuum_cost_delay = 0;  -- 移除延迟
ALTER SYSTEM SE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 938** (sql, bulk):

```sql
-- ETL流程
COPY staging_table FROM '/data/file1.csv';
-- 加载100GB CSV，耗时：4.5小时

```

**建议**:

- 添加批量操作性能测试

---

**行 946** (sql, query):

```sql
-- 1. 启用AIO
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET effective_io_concurrency = 200;

-- 2. 调整checkpoint
ALTER SYSTEM SET checkpoint_timeout = '30min';
ALTER SYSTEM SET max_wal_size = '10
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 994** (sql, query):

```sql
-- 生产环境推荐配置
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET io_uring_queue_depth = 256;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET maintenance_io_concurrency = 200;
ALTER
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1005** (sql, query):

```sql
ALTER SYSTEM SET effective_io_concurrency = 500;
ALTER SYSTEM SET maintenance_io_concurrency = 500;
ALTER SYSTEM SET io_uring_queue_depth = 512;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1013** (sql, query):

```sql
ALTER SYSTEM SET effective_io_concurrency = 100;
ALTER SYSTEM SET maintenance_io_concurrency = 100;
ALTER SYSTEM SET io_uring_queue_depth = 256;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1023** (sql, query):

```sql
-- 1. I/O性能
SELECT * FROM pg_stat_io;

-- 2. 缓存命中率
SELECT
    SUM(heap_blks_hit) / NULLIF(SUM(heap_blks_hit + heap_blks_read), 0) AS cache_hit_ratio
FROM pg_statio_user_tables;
-- 目标：>95%

-- 3. 慢查询
S
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 02-跳跃扫描Skip-Scan完整指南-改进补充.md

**行 105** (sql, query):

```sql
-- 启用Skip Scan（默认）
ALTER SYSTEM SET enable_indexskipscan = on;
SELECT pg_reload_conf();

-- 禁用Skip Scan（用于测试对比）
ALTER SYSTEM SET enable_indexskipscan = off;
SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 139** (sql, query):

```sql
-- 针对低基数场景优化
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 50;
SELECT pg_reload_conf();

-- 验证配置
SHOW index_skip_scan_cardinality_threshold;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 167** (sql, query):

```sql
-- 针对大表优化
ALTER SYSTEM SET index_skip_scan_min_rows = 5000;
SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 181** (sql, index):

```sql
-- 场景1: 低基数列在前
CREATE INDEX idx_orders_status_date ON orders(status, created_at);
-- status: 5个值（低基数）
-- created_at: 高基数
-- 查询: WHERE created_at > ? （可以使用Skip Scan）

-- 场景2: 考虑查询频率
CREATE INDEX idx_or
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 201** (sql, query):

```sql
-- 1. 定期分析索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 250** (sql, query):

```sql
-- 1. 检查Skip Scan是否启用
SHOW enable_indexskipscan;
-- 应该是 'on'

-- 2. 检查前缀列基数
SELECT
    COUNT(DISTINCT status) AS status_cardinality
FROM orders;
-- 应该 <= index_skip_scan_cardinality_threshold

-- 3. 检
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 277** (sql, query):

```sql
-- 方案1: 确保Skip Scan启用
ALTER SYSTEM SET enable_indexskipscan = on;
SELECT pg_reload_conf();

-- 方案2: 调整基数阈值
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 200;
SELECT pg_reload_conf();

-- 方案
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 312** (sql, query):

```sql
-- 1. 检查前缀列基数
SELECT COUNT(DISTINCT status) FROM orders;

-- 2. 更新统计信息
ANALYZE orders;

-- 3. 对比性能
SET enable_indexskipscan = off;
EXPLAIN ANALYZE SELECT ...;

SET enable_indexskipscan = on;
EXPLAIN A
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 329** (sql, index):

```sql
-- 方案1: 降低基数阈值
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 50;
SELECT pg_reload_conf();

-- 方案2: 创建单列索引（如果Skip Scan不适用）
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- 方案3:
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 353** (sql, query):

```sql
-- 1. 查看所有可用索引
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'orders';

-- 2. 查看执行计划
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM orders
WHERE created_at > '2024-01-01';

-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 377** (sql, index):

```sql
-- 方案1: 删除冗余索引
DROP INDEX IF EXISTS idx_orders_redundant;

-- 方案2: 调整索引顺序
DROP INDEX idx_orders_status_date;
CREATE INDEX idx_orders_status_date ON orders(status, created_at);

-- 方案3: 使用索引提示（PostgreS
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 474** (sql, query):

```sql
-- 方法1: 使用EXPLAIN查看执行计划
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM orders
WHERE created_at > '2024-01-01';

-- 如果输出包含 "Index Skip Scan"，说明生效
-- 示例输出:
-- Index Skip Scan using idx_orders_status_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 493** (sql, query):

```sql
-- 方法3: 对比启用/禁用Skip Scan
-- 禁用Skip Scan
SET enable_indexskipscan = off;
EXPLAIN ANALYZE SELECT ...;
-- 应该显示 Seq Scan

-- 启用Skip Scan
SET enable_indexskipscan = on;
EXPLAIN ANALYZE SELECT ...;
-- 应该显示
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 508** (sql, query):

```sql
-- 完整验证脚本
DO $$
DECLARE
    skip_scan_enabled BOOLEAN;
    cardinality_threshold INTEGER;
    plan_text TEXT;
BEGIN
    -- 检查配置
    SELECT setting::BOOLEAN INTO skip_scan_enabled
    FROM pg_settings
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 563** (sql, index):

```sql
   -- 将低基数列放在前面
   CREATE INDEX idx ON t(low_cardinality_col, high_cardinality_col);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 570** (sql, query):

```sql
   -- 根据实际情况调整阈值
   ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 50;
   ALTER SYSTEM SET index_skip_scan_min_rows = 1000;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 615** (sql, index):

```sql
-- 1. 确保前缀列基数合适
SELECT COUNT(DISTINCT status) FROM orders;
-- 应该 < 100

-- 2. 确保查询选择性足够
EXPLAIN ANALYZE
SELECT * FROM orders WHERE created_at > '2024-01-01';
-- 查看实际行数，应该 > 1000

-- 3. 使用B-tree索引
CREA
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

### 02-跳跃扫描Skip-Scan完整指南.md

**行 70** (sql, index):

```sql
-- 创建多列索引
CREATE INDEX idx_orders_status_date ON orders(status, created_at);

-- 查询1：使用索引（有前缀列）✅
SELECT * FROM orders WHERE status = 'shipped' AND created_at > '2024-01-01';
-- 索引可用：status是前缀列

-- 查询2
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 86** (sql, query):

```sql
-- 查询2在PostgreSQL 18中：可以使用索引！✅
SELECT * FROM orders WHERE created_at > '2024-01-01';

-- PostgreSQL 18会：
-- 1. 跳跃扫描status的所有值
-- 2. 对每个status值，扫描created_at范围
-- 3. 合并结果

-- EXPLAIN输出会显示："Index Skip Sc
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 206** (sql, index):

```sql
-- 场景1：缺少最左前缀列
CREATE INDEX idx ON t(a, b, c);
SELECT * FROM t WHERE b = ? AND c = ?;
-- ✅ 可以使用Skip Scan（如果a基数低）

-- 场景2：缺少中间列
SELECT * FROM t WHERE a = ? AND c = ?;
-- ✅ 也可以使用Skip Scan（PostgreSQL 18优
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 223** (sql, index):

```sql
-- 场景1：前缀列基数太高
CREATE INDEX idx ON t(user_id, date);  -- user_id有百万个值
SELECT * FROM t WHERE date = '2024-01-01';
-- ❌ 不会使用Skip Scan（成本太高）
-- 会使用全表扫描或其他索引

-- 场景2：查询选择性太低
SELECT * FROM t WHERE b > 0;
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 246** (sql, index):

```sql
-- ✅ 好的设计
CREATE INDEX idx_orders ON orders(status, type, created_at);
-- status: 5个值（pending, processing, shipped, delivered, cancelled）
-- type: 10个值（online, offline, wholesale, ...）
-- created_at:
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 259** (sql, index):

```sql
-- ❌ 不好的设计
CREATE INDEX idx_orders ON orders(user_id, status, created_at);
-- user_id: 百万个值（高基数）
-- status: 5个值
-- created_at: 高基数

-- 查询示例
SELECT * FROM orders
WHERE status = 'shipped' AND created_at
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 275** (sql, index):

```sql
-- 如果经常查询：
-- Q1: WHERE status = ? AND date > ?
-- Q2: WHERE date > ?

-- 索引设计：
CREATE INDEX idx ON orders(status, date);
-- Q1：正常索引扫描
-- Q2：Skip Scan（跳过status，仅5个值）

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 310** (sql, index):

```sql
-- 创建测试表
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    status VARCHAR(20),  -- 5个值
    type VARCHAR(20),     -- 10个值
    amount NUMERIC(10, 2),
    created_at TIMESTAMPTZ
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 353** (sql, query):

```sql
-- 查询1：有完整前缀（传统索引扫描）
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE status = 'shipped'
  AND type = 'online'
  AND created_at > '2024-06-01';

-- 输出：
-- Index Scan using idx_orders_status_type_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 386** (sql, query):

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM orders
WHERE type = 'online' AND created_at > '2024-06-01';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 450** (sql, query):

```sql
-- 运营人员常查：最近30天的订单
SELECT * FROM orders
WHERE created_at > NOW() - INTERVAL '30 days'
ORDER BY created_at DESC;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 496** (sql, query):

```sql
-- 查询某服务的日志（缺少log_level）
SELECT * FROM access_logs
WHERE service = 'api-gateway'
  AND timestamp > '2024-12-01'
ORDER BY timestamp DESC
LIMIT 100;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 519** (sql, index):

```sql
-- 如果查询模式是：
-- Q1: WHERE a = ? AND b = ?  （频繁，80%）
-- Q2: WHERE b = ?            （偶尔，20%）

-- 设计索引：
CREATE INDEX idx ON t(a, b);
-- Q1：正常索引扫描（快）
-- Q2：Skip Scan（可接受）

-- 而不是：
CREATE INDEX idx1 ON t(a,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 537** (sql, query):

```sql
-- 查看哪些查询使用了Skip Scan
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
WHERE query LIKE '%Skip Scan%'
ORDER BY calls DESC;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 547** (sql, query):

```sql
-- 对比启用/禁用Skip Scan
SET enable_indexskipscan = off;  -- 禁用
EXPLAIN ANALYZE SELECT ...;

SET enable_indexskipscan = on;   -- 启用（默认）
EXPLAIN ANALYZE SELECT ...;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 636** (sql, query):

```sql
-- 启用Skip Scan（默认）
ALTER SYSTEM SET enable_indexskipscan = on;
SELECT pg_reload_conf();

-- 禁用Skip Scan（用于测试对比）
ALTER SYSTEM SET enable_indexskipscan = off;
SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 663** (sql, query):

```sql
-- 针对低基数场景优化
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 50;
SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 690** (sql, index):

```sql
-- 场景1: 低基数列在前
CREATE INDEX idx_orders_status_date ON orders(status, created_at);
-- status: 5个值（低基数）
-- created_at: 高基数
-- 查询: WHERE created_at > ? （可以使用Skip Scan）

-- 场景2: 考虑查询频率
CREATE INDEX idx_or
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 718** (sql, query):

```sql
-- 1. 检查Skip Scan是否启用
SHOW enable_indexskipscan;
-- 应该是 'on'

-- 2. 检查前缀列基数
SELECT COUNT(DISTINCT status) AS status_cardinality
FROM orders;
-- 应该 <= index_skip_scan_cardinality_threshold

-- 3. 检查查询选
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 737** (sql, query):

```sql
-- 方案1: 确保Skip Scan启用
ALTER SYSTEM SET enable_indexskipscan = on;
SELECT pg_reload_conf();

-- 方案2: 调整基数阈值
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 200;
SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 762** (sql, index):

```sql
-- 方案1: 降低基数阈值
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 50;
SELECT pg_reload_conf();

-- 方案2: 创建单列索引（如果Skip Scan不适用）
CREATE INDEX idx_orders_created_at ON orders(created_at);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 807** (sql, query):

```sql
-- 方法1: 使用EXPLAIN查看执行计划
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM orders
WHERE created_at > '2024-01-01';

-- 如果输出包含 "Index Skip Scan"，说明生效

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 843** (sql, index):

```sql
   -- 将低基数列放在前面
   CREATE INDEX idx ON t(low_cardinality_col, high_cardinality_col);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 850** (sql, query):

```sql
   -- 根据实际情况调整阈值
   ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 50;
   ALTER SYSTEM SET index_skip_scan_min_rows = 1000;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 03-虚拟生成列完整实战指南.md

**行 46** (sql, query):

```sql
-- PostgreSQL 18：虚拟列（默认）
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT GENERATED ALWAYS AS (first_name || ' ' || last_name)
    -- 默认是VIRT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 93** (sql, query):

```sql
CREATE TABLE test_virtual (
    id SERIAL PRIMARY KEY,
    price NUMERIC(10, 2),
    quantity INT,
    -- 虚拟列
    total_virtual GENERATED ALWAYS AS (price * quantity) VIRTUAL
);

CREATE TABLE test_sto
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 113** (sql, query):

```sql
-- 插入100万行
\timing on

-- 虚拟列表
INSERT INTO test_virtual (price, quantity)
SELECT random() * 1000, (random() * 100)::INT
FROM generate_series(1, 1000000);
-- 时间：8.5秒

-- 存储列表
INSERT INTO test_stored (p
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 134** (sql, query):

```sql
-- 虚拟列查询
SELECT id, price, quantity, total_virtual
FROM test_virtual
WHERE id < 100000;
-- 时间：250ms（需要计算total_virtual）

-- 存储列查询
SELECT id, price, quantity, total_stored
FROM test_stored
WHERE id < 10
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 152** (sql, query):

```sql
SELECT
    pg_size_pretty(pg_total_relation_size('test_virtual')) AS virtual_size,
    pg_size_pretty(pg_total_relation_size('test_stored')) AS stored_size;

-- 结果：
-- virtual_size: 65 MB
-- stored_si
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 171** (sql, query):

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    price NUMERIC(10, 2),
    tax_rate NUMERIC(3, 2),  -- 0.08表示8%
    -- 含税价格（简单计算，偶尔读取）
    price_with_tax GENERATED ALWAYS AS (price * (1 + tax_ra
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 186** (sql, query):

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    -- 全名（仅用于显示）
    full_name GENERATED ALWAYS AS (first_name || ' ' || last_name) VIRTUAL,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 203** (sql, query):

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_data JSONB,
    -- 提取字段（虚拟）
    event_type GENERATED ALWAYS AS (event_data->>'type') VIRTUAL,
    user_id GENERATED ALWAYS AS ((event_data->>
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 217** (sql, index):

```sql
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    data JSONB,
    -- 复杂聚合计算（昂贵）
    score GENERATED ALWAYS AS (
        calculate_complex_score(data)  -- 自定义函数，计算耗时
    ) STORED;  -- 必须STORED，否则
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 232** (sql, index):

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    content TEXT,
    -- 全文搜索向量（需要GIN索引）
    tsv GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
    -- 必须STORED才能创建索引
);

CREATE INDEX
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 295** (sql, query):

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT GENERATED ALWAYS AS (
        first_name || ' ' || last_name
    ) VIRTUAL
);

-- 优点：
--
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 315** (sql, index):

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT GENERATED ALWAYS AS (
        first_name || ' ' || last_name
    ) STORED
);

CREATE INDE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 342** (sql, index):

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT GENERATED ALWAYS AS (
        first_name || ' ' || last_name
    ) VIRTUAL
);

-- 在虚拟列上创建
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

### 04-UUIDv7完整指南-改进补充.md

**行 78** (sql, query):

```sql
-- 测试场景：持续插入1小时
-- UUIDv4
CREATE TABLE orders_v4 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT,
    amount NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- UUID
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 111** (sql, query):

```sql
-- 测试场景：批量插入日志
-- UUIDv4
CREATE TABLE logs_v4 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level VARCHAR(10),
    message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- UUIDv7
CREAT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 149** (sql, query):

```sql
-- 新表直接使用UUIDv7
CREATE TABLE new_orders (
    id UUID PRIMARY KEY DEFAULT gen_uuid_v7(),
    user_id BIGINT,
    amount NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 161** (sql, query):

```sql
-- 步骤1: 添加新列
ALTER TABLE orders ADD COLUMN id_v7 UUID;

-- 步骤2: 生成UUIDv7（基于created_at时间）
UPDATE orders
SET id_v7 = gen_uuid_v7_at(created_at)
WHERE id_v7 IS NULL;

-- 步骤3: 创建新索引
CREATE UNIQUE INDEX id
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 185** (sql, query):

```sql
-- 完整迁移脚本
DO $$
DECLARE
    batch_size INTEGER := 10000;
    total_rows BIGINT;
    processed_rows BIGINT := 0;
BEGIN
    -- 获取总行数
    SELECT COUNT(*) INTO total_rows FROM orders;

    RAISE NOTICE '开
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 247** (sql, query):

```sql
-- 方案：新数据使用UUIDv7，旧数据保持UUIDv4
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    -- 其他字段
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 使用触发器自动选择
CREATE OR REPLACE FUNCTION orders_id_default()
RETURN
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 300** (sql, index):

```sql
-- 定期重建索引（UUIDv7索引更紧凑，重建频率可以降低）
-- UUIDv4: 每月重建
-- UUIDv7: 每季度重建

-- 检查索引碎片
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 337** (sql, query):

```sql
-- 1. 检查函数性能
EXPLAIN ANALYZE
SELECT gen_uuid_v7() FROM generate_series(1, 100000);

-- 2. 检查系统时间同步
SELECT now(), clock_timestamp();

-- 3. 检查序列号生成
SELECT gen_uuid_v7(), gen_uuid_v7(), gen_uuid_v7();
-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 352** (sql, query):

```sql
-- 方案1: 使用批量生成
INSERT INTO orders (user_id, amount)
SELECT i, 100.0
FROM generate_series(1, 10000) i;
-- 批量插入性能更好

-- 方案2: 使用连接池
-- 减少连接开销

-- 方案3: 优化系统时间同步
-- 使用NTP同步系统时间

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 377** (sql, query):

```sql
-- 1. 检查UUIDv7格式
SELECT gen_uuid_v7();
-- 应该以018d开头（版本7标识）

-- 2. 检查时间戳提取
SELECT
    gen_uuid_v7() AS uuid,
    uuid_extract_time(gen_uuid_v7()) AS timestamp_ms,
    to_timestamp(uuid_extract_time(gen
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 396** (sql, query):

```sql
-- 确保使用PostgreSQL 18+
SELECT version();
-- 应该显示PostgreSQL 18.0或更高版本

-- 确保函数存在
SELECT proname FROM pg_proc WHERE proname = 'gen_uuid_v7';
SELECT proname FROM pg_proc WHERE proname = 'uuid_extract_time
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 423** (sql, index):

```sql
-- 方案1: 重建索引
REINDEX INDEX CONCURRENTLY orders_pkey;

-- 方案2: 更新统计信息
ANALYZE orders;

-- 方案3: 检查数据分布
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT id) AS distinct_ids,
    pg_size_pretty(pg_to
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 486** (sql, query):

```sql
-- 方法1: 检查生成的UUID格式
SELECT gen_uuid_v7();
-- 应该以018d开头（版本7标识）

-- 方法2: 检查时间戳提取
SELECT
    gen_uuid_v7() AS uuid,
    uuid_extract_time(gen_uuid_v7()) AS timestamp_ms,
    to_timestamp(uuid_extract_tim
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 550** (sql, query):

```sql
-- 1. 确保系统时间同步
-- 使用NTP同步系统时间

-- 2. 监控UUID生成速度
SELECT
    COUNT(*) AS uuid_count,
    MIN(uuid_extract_time(id)) AS min_timestamp,
    MAX(uuid_extract_time(id)) AS max_timestamp
FROM orders
WHERE cr
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 578** (sql, query):

```sql
   -- 检查表大小
   SELECT
       schemaname,
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   WHERE schemaname = 'public';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 04-UUIDv7完整指南.md

**行 100** (sql, query):

```sql
-- UUIDv4（随机UUID）
CREATE TABLE users_v4 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- UUIDv4
    name TEXT
);

-- 插入100万行
INSERT INTO users_v4 (name)
SELECT 'User ' || i FROM generate_serie
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 144** (sql, query):

```sql
-- UUIDv7（时间排序）
CREATE TABLE users_v7 (
    id UUID PRIMARY KEY DEFAULT gen_uuid_v7(),  -- PostgreSQL 18
    name TEXT
);

-- 插入100万行
INSERT INTO users_v7 (name)
SELECT 'User ' || i FROM generate_seri
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 210** (sql, bulk):

```sql
-- 测试插入100万行

-- UUIDv4
CREATE TABLE test_v4 (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), data TEXT);
INSERT INTO test_v4 (data) SELECT 'data' FROM generate_series(1, 1000000);
-- 时间：8.5秒
-- 索引大小：4
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 236** (sql, query):

```sql
-- 随机查询
SELECT * FROM test_v4 WHERE id = '<random_uuid>';
-- 平均：0.12ms

SELECT * FROM test_v7 WHERE id = '<random_uuid>';
-- 平均：0.10ms（快20%）

-- 范围查询（按时间）
SELECT * FROM test_v7
WHERE id >= uuid_extrac
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 259** (sql, query):

```sql
-- PostgreSQL 18新函数
gen_uuid_v7() → uuid

-- 示例
SELECT gen_uuid_v7();
-- 输出：018d2a54-6c1f-7000-8000-123456789abc

-- 连续生成10个（按时间排序）
SELECT gen_uuid_v7() FROM generate_series(1, 10);
-- 输出：
-- 018d2a54
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 278** (sql, query):

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_uuid_v7(),
    user_id BIGINT NOT NULL,
    total NUMERIC(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入数据
INSERT INTO orders (use
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 297** (sql, query):

```sql
-- 从UUIDv7提取Unix时间戳（毫秒）
uuid_extract_time(uuid) → bigint

-- 示例
SELECT uuid_extract_time('018d2a54-6c1f-7000-8000-123456789abc'::uuid);
-- 输出：1701234567890（Unix毫秒）

-- 转换为时间戳
SELECT to_timestamp(uuid_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 312** (sql, query):

```sql
-- 查询最近1小时的订单
SELECT *
FROM orders
WHERE uuid_extract_time(id) > extract(epoch from now() - interval '1 hour') * 1000;

-- 按日期范围查询
SELECT *
FROM orders
WHERE id >= gen_uuid_v7_at('2024-01-01 00:00:00'
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 329** (sql, query):

```sql
-- 生成指定时间的UUIDv7
CREATE OR REPLACE FUNCTION gen_uuid_v7_at(ts timestamptz)
RETURNS uuid AS $$
DECLARE
    unix_ts_ms bigint;
    uuid_bytes bytea;
BEGIN
    unix_ts_ms := (EXTRACT(EPOCH FROM ts) * 100
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 379** (sql, query):

```sql
-- 检查索引碎片（pgstattuple扩展）
CREATE EXTENSION IF NOT EXISTS pgstattuple;

-- UUIDv4索引
SELECT * FROM pgstatindex('test_v4_pkey');
-- avg_leaf_density: 65%（碎片严重）
-- leaf_fragmentation: 42%

-- UUIDv7索引
SELE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 404** (sql, query):

```sql
-- 新表默认使用UUIDv7
CREATE TABLE new_orders (
    id UUID PRIMARY KEY DEFAULT gen_uuid_v7(),
    -- 其他列...
);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 416** (sql, query):

```sql
-- 步骤1：添加UUIDv7列
ALTER TABLE orders ADD COLUMN id_v7 UUID DEFAULT gen_uuid_v7();

-- 步骤2：为现有行生成UUIDv7
UPDATE orders SET id_v7 = gen_uuid_v7() WHERE id_v7 IS NULL;

-- 步骤3：创建索引
CREATE UNIQUE INDEX idx_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 440** (sql, bulk):

```sql
-- 适用于小表（<100万行）

-- 步骤1：创建新表
CREATE TABLE orders_new (LIKE orders INCLUDING ALL);
ALTER TABLE orders_new ALTER COLUMN id SET DEFAULT gen_uuid_v7();

-- 步骤2：复制数据
INSERT INTO orders_new SELECT * FROM o
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 475** (sql, index):

```sql
-- 新订单表使用UUIDv7
CREATE TABLE orders_v7 (
    id UUID PRIMARY KEY DEFAULT gen_uuid_v7(),
    user_id BIGINT,
    amount NUMERIC(10, 2),
    status VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 515** (sql, query):

```sql
CREATE TABLE logs_v7 (
    id UUID PRIMARY KEY DEFAULT gen_uuid_v7(),  -- 天然时间排序
    service VARCHAR(50),
    level VARCHAR(10),
    message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 不需要cr
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 606** (sql, query):

```sql
-- 新表直接使用UUIDv7
CREATE TABLE new_orders (
    id UUID PRIMARY KEY DEFAULT gen_uuid_v7(),
    user_id BIGINT,
    amount NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 618** (sql, query):

```sql
-- 步骤1: 添加新列
ALTER TABLE orders ADD COLUMN id_v7 UUID;

-- 步骤2: 生成UUIDv7（基于created_at时间）
UPDATE orders
SET id_v7 = gen_uuid_v7_at(created_at)
WHERE id_v7 IS NULL;

-- 步骤3: 创建新索引
CREATE UNIQUE INDEX id
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 642** (sql, query):

```sql
-- 完整迁移脚本
DO $$
DECLARE
    batch_size INTEGER := 10000;
    total_rows BIGINT;
    processed_rows BIGINT := 0;
BEGIN
    -- 获取总行数
    SELECT COUNT(*) INTO total_rows FROM orders;

    RAISE NOTICE '开
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 708** (sql, index):

```sql
-- 定期重建索引（UUIDv7索引更紧凑，重建频率可以降低）
-- UUIDv4: 每月重建
-- UUIDv7: 每季度重建

-- 检查索引碎片
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 745** (sql, query):

```sql
-- 1. 检查函数性能
EXPLAIN ANALYZE
SELECT gen_uuid_v7() FROM generate_series(1, 100000);

-- 2. 检查系统时间同步
SELECT now(), clock_timestamp();

-- 3. 检查序列号生成
SELECT gen_uuid_v7(), gen_uuid_v7(), gen_uuid_v7();
-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 760** (sql, query):

```sql
-- 方案1: 使用批量生成
INSERT INTO orders (user_id, amount)
SELECT i, 100.0
FROM generate_series(1, 10000) i;
-- 批量插入性能更好

-- 方案2: 使用连接池
-- 减少连接开销

-- 方案3: 优化系统时间同步
-- 使用NTP同步系统时间

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 783** (sql, query):

```sql
-- 1. 检查UUIDv7格式
SELECT gen_uuid_v7();
-- 应该以018d开头（版本7标识）

-- 2. 检查时间戳提取
SELECT
    gen_uuid_v7() AS uuid,
    uuid_extract_time(gen_uuid_v7()) AS timestamp_ms,
    to_timestamp(uuid_extract_time(gen
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 802** (sql, query):

```sql
-- 确保使用PostgreSQL 18+
SELECT version();
-- 应该显示PostgreSQL 18.0或更高版本

-- 确保函数存在
SELECT proname FROM pg_proc WHERE proname = 'gen_uuid_v7';
SELECT proname FROM pg_proc WHERE proname = 'uuid_extract_time
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 851** (sql, query):

```sql
-- 方法1: 检查生成的UUID格式
SELECT gen_uuid_v7();
-- 应该以018d开头（版本7标识）

-- 方法2: 检查时间戳提取
SELECT
    gen_uuid_v7() AS uuid,
    uuid_extract_time(gen_uuid_v7()) AS timestamp_ms,
    to_timestamp(uuid_extract_tim
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 915** (sql, query):

```sql
   -- 检查表大小
   SELECT
       schemaname,
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   WHERE schemaname = 'public';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 05-GIN并行构建完整指南.md

**行 46** (sql, index):

```sql
-- JSONB索引
CREATE INDEX idx_data_gin ON products USING GIN (data jsonb_path_ops);

-- 数组索引
CREATE INDEX idx_tags_gin ON articles USING GIN (tags);

-- 全文搜索索引
CREATE INDEX idx_fts_gin ON documents USIN
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 67** (sql, index):

```sql
-- 传统构建（PostgreSQL 17）
CREATE INDEX idx_tags ON articles USING GIN (tags);
-- 表：5000万行
-- 时间：45分钟（单核）
-- 期间：表被ShareLock锁定

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 121** (sql, query):

```sql
-- 1. 最大并行Worker数量（全局）
SHOW max_parallel_maintenance_workers;
-- 默认：2
-- 推荐：4-8（根据CPU核心数）

ALTER SYSTEM SET max_parallel_maintenance_workers = 8;

-- 2. 单个索引构建的Worker数量
SET max_parallel_workers_per_ga
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 141** (sql, index):

```sql
-- 方法1：会话级别设置
SET max_parallel_workers_per_gather = 4;
CREATE INDEX idx_tags ON articles USING GIN (tags);

-- 方法2：直接指定
CREATE INDEX idx_tags ON articles USING GIN (tags)
WITH (parallel_workers = 4);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 205** (sql, index):

```sql
-- postgresql.conf
max_parallel_maintenance_workers = 8  -- 根据CPU核心数
maintenance_work_mem = '2GB'          -- 每个Worker的内存
max_worker_processes = 32             -- 总Worker池

-- 创建索引时
SET max_parallel_w
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 231** (sql, index):

```sql
-- 查看当前索引构建进度
SELECT
    pid,
    datname,
    query,
    state,
    wait_event_type,
    wait_event
FROM pg_stat_activity
WHERE query LIKE '%CREATE INDEX%';

-- 查看Worker状态
SELECT
    pid,
    leader_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 267** (sql, index):

```sql
CREATE INDEX idx_data_gin ON products USING GIN (data);
-- 时间：75分钟（单核）
-- CPU：6%

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 275** (sql, index):

```sql
-- 设置8个并行Worker
SET max_parallel_workers_per_gather = 8;
SET maintenance_work_mem = '2GB';

CREATE INDEX idx_data_gin ON products USING GIN (data);
-- 时间：12分钟（8核）
-- CPU：48%
-- 提升：525%

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 303** (sql, index):

```sql
-- 创建tsvector列
ALTER TABLE documents
ADD COLUMN tsv tsvector
GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

-- 并行构建GIN索引
SET max_parallel_workers_per_gather = 6;
CREATE INDEX idx_fts O
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

### 06-OAuth2.0认证集成完整指南-改进补充.md

**行 85** (sql, query):

```sql
-- 1. 检查OAuth配置
SHOW oauth_enabled;
SHOW oauth_issuer;
SHOW oauth_audience;

-- 2. 检查pg_hba.conf
SELECT * FROM pg_hba_file_rules WHERE auth_method = 'oauth';

-- 3. 检查日志
-- 查看PostgreSQL日志
tail -f /var
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 101** (sql, query):

```sql
-- 方案1: 验证配置
ALTER SYSTEM SET oauth_enabled = on;
ALTER SYSTEM SET oauth_issuer = 'https://accounts.google.com';
ALTER SYSTEM SET oauth_audience = 'your-client-id';
SELECT pg_reload_conf();

-- 方案2: 检
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 127** (sql, query):

```sql
-- 1. 检查Token过期时间
SELECT
    oid,
    rolname,
    rolvaliduntil
FROM pg_roles
WHERE rolname LIKE 'oauth%';

-- 2. 检查Token刷新配置
SHOW oauth_token_refresh_enabled;
SHOW oauth_token_refresh_threshold;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 143** (sql, query):

```sql
-- 方案1: 启用Token自动刷新
ALTER SYSTEM SET oauth_token_refresh_enabled = on;
ALTER SYSTEM SET oauth_token_refresh_threshold = 300;  -- 提前5分钟刷新
SELECT pg_reload_conf();

-- 方案2: 增加Token有效期
-- 在OAuth Provider
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 167** (sql, query):

```sql
-- 1. 检查角色映射配置
SHOW oauth_claim_role_mapping;
SHOW oauth_role_claim;

-- 2. 检查Token Claims
-- 查看JWT Token中的claims
-- 应该包含角色信息

-- 3. 检查角色是否存在
SELECT rolname FROM pg_roles WHERE rolname = 'expected_rol
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 182** (sql, query):

```sql
-- 方案1: 配置角色映射
ALTER SYSTEM SET oauth_claim_role_mapping = on;
ALTER SYSTEM SET oauth_role_claim = 'groups';  -- 或'roles'
SELECT pg_reload_conf();

-- 方案2: 创建映射角色
CREATE ROLE oauth_user_role;
GRANT CO
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 209** (sql, query):

```sql
-- 1. 使用强算法
-- 推荐使用RS256（非对称加密）
-- 避免使用HS256（对称加密，密钥泄露风险）

-- 2. 验证Token签名
ALTER SYSTEM SET oauth_jwt_verify_signature = on;
SELECT pg_reload_conf();

-- 3. 验证Token过期
ALTER SYSTEM SET oauth_token_expi
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 248** (sql, query):

```sql
-- 1. 创建最小权限角色
CREATE ROLE oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oauth_readon
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 306** (sql, query):

```sql
-- 方法1: 检查配置
SHOW oauth_enabled;  -- 应该是 'on'
SHOW oauth_issuer;
SHOW oauth_audience;

-- 方法2: 检查pg_hba.conf
SELECT * FROM pg_hba_file_rules WHERE auth_method = 'oauth';

-- 方法3: 测试连接
-- 使用OAuth Token
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 374** (sql, query):

```sql
   ALTER SYSTEM SET oauth_enabled = on;
   ALTER SYSTEM SET oauth_issuer = 'https://oauth-provider.com';
   ALTER SYSTEM SET oauth_audience = 'your-client-id';
   SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 06-OAuth2.0认证集成完整指南.md

**行 184** (sql, query):

```sql
-- 创建角色
CREATE ROLE google_users;
GRANT CONNECT ON DATABASE mydb TO google_users;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO google_users;

-- 创建用户（自动从Google email创建）
-- PostgreSQL 18会自动根据token中的e
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 332** (sql, query):

```sql
-- 创建受限角色
CREATE ROLE oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oauth_readonly;


```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 362** (sql, query):

```sql
-- 配置Azure AD OAuth
-- postgresql.conf
oauth_enabled = on
oauth_issuer = 'https://login.microsoftonline.com/company-tenant-id/v2.0'
oauth_audience = 'company-pg-client-id'
oauth_jwks_uri = 'https://lo
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 409** (sql, query):

```sql
-- 支持多OAuth Provider
-- postgresql.conf
oauth_enabled = on
oauth_multi_issuer = on  # 允许多个issuer

-- 创建Issuer配置表
CREATE TABLE oauth_issuers (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 507** (sql, query):

```sql
-- 1. 检查OAuth配置
SHOW oauth_enabled;
SHOW oauth_issuer;
SHOW oauth_audience;

-- 2. 检查pg_hba.conf
SELECT * FROM pg_hba_file_rules WHERE auth_method = 'oauth';

-- 3. 检查日志
-- 查看PostgreSQL日志
tail -f /var
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 523** (sql, query):

```sql
-- 方案1: 验证配置
ALTER SYSTEM SET oauth_enabled = on;
ALTER SYSTEM SET oauth_issuer = 'https://accounts.google.com';
ALTER SYSTEM SET oauth_audience = 'your-client-id';
SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 540** (sql, query):

```sql
-- 方案1: 启用Token自动刷新
ALTER SYSTEM SET oauth_token_refresh_enabled = on;
ALTER SYSTEM SET oauth_token_refresh_threshold = 300;  -- 提前5分钟刷新
SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 556** (sql, query):

```sql
-- 方案1: 配置角色映射
ALTER SYSTEM SET oauth_claim_role_mapping = on;
ALTER SYSTEM SET oauth_role_claim = 'groups';
SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 571** (sql, query):

```sql
-- 1. 使用强算法
-- 推荐使用RS256（非对称加密）

-- 2. 验证Token签名
ALTER SYSTEM SET oauth_jwt_verify_signature = on;
SELECT pg_reload_conf();

-- 3. 验证Token过期
ALTER SYSTEM SET oauth_token_expiry_check = on;
SELECT pg_r
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 588** (sql, query):

```sql
-- 1. 创建最小权限角色
CREATE ROLE oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oauth_readon
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 629** (sql, query):

```sql
-- 方法1: 检查配置
SHOW oauth_enabled;  -- 应该是 'on'
SHOW oauth_issuer;
SHOW oauth_audience;

-- 方法2: 检查pg_hba.conf
SELECT * FROM pg_hba_file_rules WHERE auth_method = 'oauth';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 679** (sql, query):

```sql
   ALTER SYSTEM SET oauth_enabled = on;
   ALTER SYSTEM SET oauth_issuer = 'https://oauth-provider.com';
   SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 07-逻辑复制增强完整指南-改进补充.md

**行 96** (sql, query):

```sql
-- 1. 检查复制延迟
SELECT
    subname,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), latest_end_lsn)) AS replication_lag
FROM pg_subscription;

-- 2. 检查Worker状态
SELECT
    pid,
    application_na
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 118** (sql, query):

```sql
-- 方案1: 增加Worker数量
ALTER SYSTEM SET max_logical_replication_workers = 8;
ALTER SYSTEM SET max_sync_workers_per_subscription = 4;
SELECT pg_reload_conf();

-- 方案2: 优化网络
-- 使用10Gbps网络
-- 启用WAL压缩

-- 方案3
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 144** (sql, query):

```sql
-- 1. 检查DDL复制配置
SHOW logical_replication_ddl_replication;
-- 应该是 'on'

-- 2. 检查发布配置
SELECT * FROM pg_publication;
SELECT * FROM pg_publication_tables;

-- 3. 检查订阅配置
SELECT * FROM pg_subscription;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 159** (sql, query):

```sql
-- 方案1: 启用DDL复制
ALTER SYSTEM SET logical_replication_ddl_replication = on;
SELECT pg_reload_conf();

-- 方案2: 检查发布配置
-- 确保发布包含需要复制的表
ALTER PUBLICATION mypub ADD TABLE new_table;

-- 方案3: 手动同步DDL
-- 如果D
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 183** (sql, query):

```sql
-- 1. 检查冲突统计
SELECT * FROM pg_stat_replication_conflicts;

-- 2. 检查冲突日志
-- 查看PostgreSQL日志中的冲突信息

-- 3. 检查冲突解决策略
SHOW logical_replication_conflict_resolution;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 196** (sql, query):

```sql
-- 方案1: 配置冲突解决策略
ALTER SYSTEM SET logical_replication_conflict_resolution = 'last_write_wins';
SELECT pg_reload_conf();

-- 方案2: 使用自定义冲突处理函数
CREATE FUNCTION resolve_conflict()
RETURNS trigger AS $$
BE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 253** (sql, query):

```sql
-- 1. 复制延迟监控
SELECT
    subname,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), latest_end_lsn)) AS replication_lag,
    latest_end_time
FROM pg_subscription;

-- 2. Worker状态监控
SELECT
    pi
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 329** (sql, query):

```sql
-- 方法1: 检查订阅状态
SELECT * FROM pg_subscription;
-- 应该显示active状态

-- 方法2: 检查复制延迟
SELECT
    subname,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), latest_end_lsn)) AS replication_lag
FROM pg_s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 399** (sql, query):

```sql
   ALTER SYSTEM SET max_logical_replication_workers = 8;
   ALTER SYSTEM SET max_sync_workers_per_subscription = 4;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 406** (sql, query):

```sql
   ALTER SYSTEM SET logical_replication_batch_size = 1000;
   ALTER SYSTEM SET logical_replication_commit_interval = 100ms;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 413** (sql, query):

```sql
   ALTER SYSTEM SET wal_compression = on;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 07-逻辑复制增强完整指南.md

**行 132** (sql, query):

```sql
-- 创建Publication，启用DDL复制
CREATE PUBLICATION my_pub
FOR ALL TABLES  -- 或指定表
WITH (
    publish = 'insert,update,delete',
    publish_via_partition_root = true,
    ddl_replication = true  -- ⭐ 启用DDL复制

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 145** (sql, query):

```sql
-- 创建Subscription
CREATE SUBSCRIPTION my_sub
CONNECTION 'host=publisher dbname=mydb user=repuser'
PUBLICATION my_pub
WITH (
    ddl_replication = true,  -- ⭐ 启用DDL复制
    ddl_conflict_action = 'apply_r
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 160** (sql, index):

```sql
-- ✅ 添加列
ALTER TABLE users ADD COLUMN age INT;
-- 自动复制到订阅端

-- ✅ 修改列类型
ALTER TABLE users ALTER COLUMN age TYPE BIGINT;

-- ✅ 添加约束
ALTER TABLE users ADD CONSTRAINT users_age_check CHECK (age > 0);

--
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 180** (sql, query):

```sql
-- ❌ 创建/删除表（需手动）
CREATE TABLE new_table (...);

-- ❌ 重命名表
ALTER TABLE users RENAME TO customers;

-- ❌ 修改表空间
ALTER TABLE users SET TABLESPACE new_tablespace;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 201** (sql, query):

```sql
-- 场景：两端同时插入相同主键
-- Node A:
INSERT INTO users (id, name) VALUES (1, 'Alice');

-- Node B（几乎同时）:
INSERT INTO users (id, name) VALUES (1, 'Bob');

-- 冲突：主键重复

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 214** (sql, query):

```sql
-- 场景：两端同时更新同一行
-- Node A:
UPDATE users SET name = 'Alice Updated' WHERE id = 1;

-- Node B:
UPDATE users SET name = 'Alice Modified' WHERE id = 1;

-- 冲突：UPDATE冲突

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 227** (sql, query):

```sql
-- 场景：一端UPDATE，另一端DELETE
-- Node A:
UPDATE users SET name = 'Alice' WHERE id = 1;

-- Node B:
DELETE FROM users WHERE id = 1;

-- 冲突：行不存在

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 242** (sql, query):

```sql
-- Subscription级别配置
ALTER SUBSCRIPTION my_sub
SET (
    conflict_action = 'apply_remote'  -- 应用远程变更（默认）
);

-- 可选策略：
-- 1. apply_remote：应用远程变更（覆盖本地）
-- 2. skip：跳过冲突变更
-- 3. error：报错并停止复制
-- 4. latest_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 258** (sql, query):

```sql
-- 创建带时间戳的表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 配置使用时间戳解决冲突
ALTER SUBSCRIPTION my_sub
SET (
    conflict_action = 'latest_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 281** (sql, query):

```sql
-- 创建冲突处理函数
CREATE OR REPLACE FUNCTION handle_user_conflict()
RETURNS TRIGGER AS $$
BEGIN
    -- 记录冲突
    INSERT INTO conflict_log (table_name, conflict_type, old_data, new_data)
    VALUES (TG_TABLE_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 316** (sql, query):

```sql
-- 创建Subscription时指定并行度
CREATE SUBSCRIPTION my_sub
CONNECTION 'host=publisher'
PUBLICATION my_pub
WITH (
    streaming = on,
    parallel_apply_workers = 8,  -- ⭐ 8个并行Worker
    parallel_apply_batch_s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 350** (sql, query):

```sql
CREATE SUBSCRIPTION my_sub
CONNECTION 'host=publisher'
PUBLICATION my_pub
WITH (
    streaming = on,
    batch_mode = 'on',           -- ⭐ 启用批量模式
    batch_size = 10000,          -- 每批10000条
    batch
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 376** (sql, query):

```sql
-- 1. 查看Subscription状态
SELECT
    subname,
    subenabled,
    subconninfo,
    subslotname,
    subpublications
FROM pg_subscription;

-- 2. 查看复制延迟
SELECT
    application_name,
    client_addr,
    s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 427** (sql, query):

```sql
-- 诊断
SELECT
    application_name,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) / 1024 / 1024 AS lag_mb,
    now() - pg_last_xact_replay_timestamp() AS lag_time
FROM pg_stat_replication;

-- 解决方案：
-- 1.
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 447** (sql, query):

```sql
-- 查看冲突
SELECT * FROM pg_stat_subscription_conflicts
WHERE conflict_count > 0
ORDER BY last_conflict_time DESC;

-- 解决方案：
-- 1. 调整冲突策略
ALTER SUBSCRIPTION my_sub SET (conflict_action = 'latest_timestam
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 488** (sql, query):

```sql
-- 每个DC创建Publication
-- DC1:
CREATE PUBLICATION dc1_pub FOR ALL TABLES WITH (ddl_replication = true);

-- 每个DC订阅其他DC
-- DC1订阅DC2和DC3:
CREATE SUBSCRIPTION dc2_sub
CONNECTION 'host=dc2'
PUBLICATION dc2_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 529** (sql, query):

```sql
-- 步骤1：新PG18节点，创建Subscription
CREATE SUBSCRIPTION migration_sub
CONNECTION 'host=old-pg14 port=5432 dbname=mydb user=repuser'
PUBLICATION my_pub
WITH (
    copy_data = true,           -- 初始全量复制
    pa
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 620** (sql, query):

```sql
-- 1. 检查复制延迟
SELECT
    subname,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), latest_end_lsn)) AS replication_lag
FROM pg_subscription;

-- 2. 检查Worker状态
SELECT
    pid,
    application_na
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 638** (sql, query):

```sql
-- 方案1: 增加Worker数量
ALTER SYSTEM SET max_logical_replication_workers = 8;
ALTER SYSTEM SET max_sync_workers_per_subscription = 4;
SELECT pg_reload_conf();

-- 方案2: 优化批量提交
ALTER SYSTEM SET logical_repli
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 658** (sql, query):

```sql
-- 方案1: 启用DDL复制
ALTER SYSTEM SET logical_replication_ddl_replication = on;
SELECT pg_reload_conf();

-- 方案2: 检查发布配置
ALTER PUBLICATION mypub ADD TABLE new_table;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 676** (sql, query):

```sql
-- 方案1: 配置冲突解决策略
ALTER SYSTEM SET logical_replication_conflict_resolution = 'last_write_wins';
SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 714** (sql, query):

```sql
-- 1. 复制延迟监控
SELECT
    subname,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), latest_end_lsn)) AS replication_lag
FROM pg_subscription;

-- 2. Worker状态监控
SELECT
    pid,
    application_na
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 774** (sql, query):

```sql
-- 方法1: 检查订阅状态
SELECT * FROM pg_subscription;
-- 应该显示active状态

-- 方法2: 检查复制延迟
SELECT
    subname,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), latest_end_lsn)) AS replication_lag
FROM pg_s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 830** (sql, query):

```sql
   ALTER SYSTEM SET max_logical_replication_workers = 8;
   ALTER SYSTEM SET max_sync_workers_per_subscription = 4;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 837** (sql, query):

```sql
   ALTER SYSTEM SET logical_replication_batch_size = 1000;
   ALTER SYSTEM SET logical_replication_commit_interval = 100ms;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 844** (sql, query):

```sql
   ALTER SYSTEM SET wal_compression = on;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 08-EXPLAIN增强完整指南.md

**行 38** (sql, query):

```sql
-- 查看执行计划
EXPLAIN SELECT * FROM users WHERE age > 25;

-- 实际执行并显示统计
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 25;

-- 显示详细信息
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT * FROM users WHERE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 66** (sql, query):

```sql
EXPLAIN (ANALYZE, BUFFERS, MEMORY)
SELECT *
FROM large_table t1
JOIN another_table t2 ON t1.id = t2.foreign_id
ORDER BY t1.created_at;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 99** (sql, query):

```sql
EXPLAIN (ANALYZE, SERIALIZE)
SELECT * FROM users WHERE data_jsonb @> '{"status": "active"}';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 127** (sql, query):

```sql
EXPLAIN (ANALYZE, BUFFERS, IO_TIMING)
SELECT * FROM large_table WHERE status = 'active';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 160** (sql, query):

```sql
EXPLAIN (
    ANALYZE,        -- 实际执行
    BUFFERS,        -- 缓冲区统计
    VERBOSE,        -- 详细输出
    TIMING,         -- 时间统计
    MEMORY,         -- ⭐ 内存统计（PG18）
    SERIALIZE,      -- ⭐ 序列化统计（PG18）

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 188** (sql, query):

```sql
EXPLAIN (ANALYZE, MEMORY)
SELECT * FROM large_table ORDER BY created_at;

-- 输出：
Sort  (actual time=5432.123...ms rows=10000000 loops=1)
  Sort Key: created_at
  Sort Method: external merge  Disk: 152
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 202** (sql, query):

```sql
-- 增加work_mem
SET work_mem = '256MB';

EXPLAIN (ANALYZE, MEMORY)
SELECT * FROM large_table ORDER BY created_at;

-- 输出：
Sort  (actual time=856.234...ms rows=10000000 loops=1)
  Sort Key: created_at

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 222** (sql, query):

```sql
EXPLAIN (ANALYZE, BUFFERS, IO_TIMING)
SELECT * FROM orders WHERE created_at > '2024-01-01';

-- 输出：
Seq Scan on orders  (actual time=12345.678...ms)
  Filter: (created_at > '2024-01-01')
  Rows Remove
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 236** (sql, index):

```sql
CREATE INDEX idx_orders_created_at ON orders(created_at);

EXPLAIN (ANALYZE, BUFFERS, IO_TIMING)
SELECT * FROM orders WHERE created_at > '2024-01-01';

-- 输出：
Index Scan using idx_orders_created_at on
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 260** (sql, query):

```sql
-- 耗时：8.5秒
SELECT u.name, COUNT(o.id) as order_count, SUM(o.amount) as total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2023-01-01'
GROUP BY u.id, u.name
HAVING COUNT(o.
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 307** (sql, index):

```sql
-- 1. 添加索引
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- 2. 增加内存
SET work_mem = '512MB';

-- 3. 重写查询（使用CTE）
WITH active_users AS (

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 371** (sql, query):

```sql
-- 5表JOIN，耗时25秒
SELECT
    u.name,
    p.title as product_title,
    c.name as category_name,
    COUNT(DISTINCT r.id) as review_count,
    AVG(r.rating) as avg_rating
FROM users u
JOIN orders o ON u.
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 08-性能调优实战指南.md

**行 121** (sql, index):

```sql
-- B-Tree索引（默认）
CREATE INDEX idx_users_email ON users(email);

-- 部分索引
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- 表达式索引
CREATE INDEX idx_lower_email ON users(lower(email));
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 148** (sql, index):

```sql
-- 查找缺失索引
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan AS avg_seq_tup
FROM pg_stat_user_tables
WHERE seq_scan > 0
  AND seq_tup_read
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 187** (sql, query):

```sql
-- 基础EXPLAIN
EXPLAIN SELECT * FROM orders WHERE user_id = 123;

-- ANALYZE（实际执行）
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE user_id = 123;

-- 详细格式
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, COSTS
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 213** (sql, index):

```sql
-- 1. 使用索引扫描代替全表扫描
-- BAD
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- GOOD
CREATE INDEX idx_lower_email ON users(lower(email));
SELECT * FROM users WHERE lower(email) = 'test@exam
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 286** (sql, query):

```sql
-- 标准VACUUM
VACUUM (VERBOSE, ANALYZE) users;

-- FULL VACUUM（锁表，重建表）
VACUUM FULL users;

-- 冻结事务ID
VACUUM (FREEZE) users;

-- 监控膨胀
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_rel
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 342** (python, database):

```python
# Python: psycopg2 connection pool
from psycopg2 import pool

connection_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host='localhost',
    port=5432,
    database='mydb',

```

**建议**:

- 添加数据库操作性能测试

---

**行 371** (sql, query):

```sql
-- 范围分区（时序数据）
CREATE TABLE logs (
    log_id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    message TEXT
) PARTITION BY RANGE (timestamp);

-- 创建分区（月度）
CREATE TABLE logs_2023_12 PARTITION OF logs

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 420** (sql, query):

```sql
-- 自动创建分区（使用pg_partman扩展）
CREATE EXTENSION pg_partman;

SELECT partman.create_parent(
    p_parent_table := 'public.logs',
    p_control := 'timestamp',
    p_type := 'native',
    p_interval := 'mont
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 462** (sql, query):

```sql
-- 查看并行计划
EXPLAIN (ANALYZE)
SELECT COUNT(*) FROM large_table;

-- 强制并行
SET max_parallel_workers_per_gather = 8;
SET parallel_setup_cost = 0;
SET parallel_tuple_cost = 0;

SELECT COUNT(*) FROM large_ta
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 484** (sql, query):

```sql
-- 启用扩展
CREATE EXTENSION pg_stat_statements;

-- 配置
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET pg_stat_statem
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 513** (sql, query):

```sql
-- 当前活动查询
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 09-异步IO深度解析.md

**行 73** (sql, query):

```sql
-- 查看当前配置
SHOW io_direct;
SHOW io_combine_limit;
SHOW io_method;

-- 动态修改（部分参数需要重启）
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET io_combine_limit = '256kB';
SELECT pg_reload_conf();

-- 查看I/O
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 170** (sql, query):

```sql
-- 查看I/O合并效果
SELECT
    backend_type,
    io_context,
    reads,
    read_time,
    writes,
    write_time,
    extends,
    extend_time
FROM pg_stat_io
ORDER BY read_time + write_time DESC;

-- 根据工作负
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 302** (sql, query):

```sql
-- 创建测试表
CREATE TABLE bulk_test (
    id BIGSERIAL PRIMARY KEY,
    data TEXT,
    ts TIMESTAMPTZ DEFAULT now()
);

-- 批量插入测试
\timing on

-- 配置1: 传统I/O
SET io_direct = 'off';
INSERT INTO bulk_test (da
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 330** (sql, query):

```sql
-- 创建大表
CREATE TABLE scan_test AS
SELECT
    i AS id,
    md5(random()::text) AS data
FROM generate_series(1, 50000000) i;

-- 测试顺序扫描
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM scan_test;

-- 传统I
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 352** (sql, query):

```sql
-- PostgreSQL 18新增视图
SELECT
    backend_type,
    io_context,
    io_object,
    reads,
    read_time,
    writes,
    write_time,
    writebacks,
    writeback_time,
    extends,
    extend_time,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 519** (sql, query):

```sql
-- 检查I/O模式
SHOW io_direct;
SHOW io_method;

-- 查看I/O统计
SELECT * FROM pg_stat_io;

-- 可能原因
-- 1. 硬件不支持 (HDD)
-- 2. io_combine_limit过大
-- 3. 系统I/O压力大

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 548** (sql, query):

```sql
-- 异步I/O + 并行查询
SET max_parallel_workers_per_gather = 8;
SET io_direct = 'data';
SET io_combine_limit = '512kB';

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM large_table;

-- 效果:
-- 传统I/O + 串行: 12
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 565** (sql, query):

```sql
-- 分区表 + 异步I/O
CREATE TABLE logs_partitioned (
    id BIGSERIAL,
    ts TIMESTAMPTZ NOT NULL,
    message TEXT
) PARTITION BY RANGE (ts);

-- 异步I/O可以并行处理多个分区
-- 性能提升显著

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 09-约束增强完整指南.md

**行 37** (sql, query):

```sql
-- 1. NOT NULL约束
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL
);

-- 2. UNIQUE约束
ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);

-- 3. PRIMARY KEY约束
ALT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 85** (sql, query):

```sql
-- 传统方式：添加约束会锁表
ALTER TABLE large_table
ADD CONSTRAINT check_age CHECK (age > 0);
-- 问题：扫描10亿行，锁表30分钟！

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 94** (sql, query):

```sql
-- 步骤1：添加NOT VALID约束（瞬间完成，不验证现有数据）
ALTER TABLE large_table
ADD CONSTRAINT check_age CHECK (age > 0) NOT VALID;
-- 时间：<1秒
-- 锁：ShareRowExclusiveLock（允许读写）

-- 步骤2：异步验证约束（PostgreSQL 18并行化）
ALTER TABLE l
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 112** (sql, query):

```sql
-- 设置并行度
SET max_parallel_maintenance_workers = 8;

-- 验证约束（自动并行）
ALTER TABLE large_table VALIDATE CONSTRAINT check_age;

-- 内部执行（简化）：
-- Worker 1: 验证 0-12.5% 的行
-- Worker 2: 验证 12.5-25% 的行
-- Worker
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 144** (sql, query):

```sql
-- 创建分区表
CREATE TABLE orders (
    id BIGSERIAL,
    user_id BIGINT,
    amount NUMERIC(10, 2),
    created_at TIMESTAMPTZ,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 创建分区
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 170** (sql, query):

```sql
-- 查询1月数据
EXPLAIN SELECT * FROM orders WHERE created_at = '2024-01-15';

-- PostgreSQL 18优化：
-- 1. 检查CHECK约束
-- 2. 排除orders_2024_02、orders_2024_03（违反CHECK）
-- 3. 只扫描orders_2024_01

-- 输出（简化）：
Seq Scan
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 193** (sql, index):

```sql
-- 添加CHECK约束
ALTER TABLE products
ADD CONSTRAINT products_price_positive CHECK (price > 0);

-- PostgreSQL 18自动利用约束优化查询
SELECT * FROM products WHERE price > 100;
-- 优化器知道：price已经>0，无需再检查

-- 创建表达式索引
C
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 219** (sql, query):

```sql
-- 创建外键
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE
);

-- 批量删除用户（触发级联）
DELETE FROM users WHERE last_login < '2020-01-01';  -- 删除10万用户
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 252** (sql, query):

```sql
-- 创建分区表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMPTZ
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE users_2024 PARTITION OF users
FOR VALUES
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 289** (sql, query):

```sql
-- 直接添加约束
ALTER TABLE transactions
ADD CONSTRAINT check_amount CHECK (amount > 0);

-- 问题：
-- 1. 扫描20亿行，需要2小时
-- 2. 锁表2小时，业务停止
-- 结果：不可接受

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 302** (sql, query):

```sql
-- 步骤1：添加NOT VALID约束（瞬间）
ALTER TABLE transactions
ADD CONSTRAINT check_amount CHECK (amount > 0) NOT VALID;
-- 时间：<1秒
-- 影响：最小（ShareRowExclusiveLock）

-- 步骤2：并行验证（业务继续）
SET max_parallel_maintenance_wo
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 335** (sql, query):

```sql
EXPLAIN SELECT * FROM logs WHERE log_date = '2024-06-15';

-- 输出：
Append  (actual time=...ms rows=...)
  ->  Seq Scan on logs_2024_01
  ->  Seq Scan on logs_2024_02
  ->  Seq Scan on logs_2024_03
  ..
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 352** (sql, query):

```sql
-- 为每个分区添加CHECK约束
ALTER TABLE logs_2024_01
ADD CONSTRAINT check_date_2024_01
CHECK (log_date >= '2024-01-01' AND log_date < '2024-02-01');

ALTER TABLE logs_2024_02
ADD CONSTRAINT check_date_2024_02
C
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 366** (sql, query):

```sql
EXPLAIN SELECT * FROM logs WHERE log_date = '2024-06-15';

-- 输出：
Seq Scan on logs_2024_06  (actual time=...ms rows=...)
  Filter: (log_date = '2024-06-15')
  Partitions pruned: 119  -- ⭐ CHECK约束排除119
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 10-SkipScan深度解析.md

**行 7** (sql, index):

```sql
-- 传统索引查询
CREATE INDEX idx_user_status_created ON users(status, created_at);

-- 查询1: 使用索引第一列 ✓
SELECT * FROM users WHERE status = 'active';

-- 查询2: 只使用索引第二列 ✗ (无法使用索引)
SELECT * FROM users WHERE crea
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 55** (sql, query):

```sql
-- PostgreSQL 18会自动评估是否使用Skip Scan

-- 查看查询计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users WHERE created_at > '2023-01-01';

-- Skip Scan计划示例
/*
Index Skip Scan using idx_user_status_created on user
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 97** (sql, index):

```sql
-- 创建测试表
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    country VARCHAR(2),
    email VARCHAR(255),
    status VARCHAR(20),
    created_at TIMESTAMPTZ,
    last_login TIMESTAMPTZ
);

-- 插
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 128** (sql, query):

```sql
-- 查询1: 只使用后续列
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users
WHERE created_at > NOW() - INTERVAL '30 days';

-- PostgreSQL 17: Seq Scan (全表扫描)
-- PostgreSQL 18: Index Skip Scan
/*
Planning Time: 0.5m
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 203** (sql, query):

```sql
-- 查看优化器选择
EXPLAIN (COSTS, VERBOSE)
SELECT * FROM users
WHERE created_at > '2023-06-01';

-- 成本对比
/*
Seq Scan:
  Cost: 0.00..250000.00
  Rows: 500000

Index Skip Scan:
  Cost: 0.42..15000.00  (比全表扫描低1
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 232** (sql, query):

```sql
-- 禁用Skip Scan
SET enable_indexskipscan = off;

-- 启用Skip Scan (默认on)
SET enable_indexskipscan = on;

-- 临时禁用（调试）
EXPLAIN (ANALYZE)
SELECT /*+ NoIndexSkipScan(users idx_users_country_created) */
* FRO
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 251** (sql, index):

```sql
-- 场景: 经常按时间查询，偶尔按国家过滤

-- 方案1: (country, created_at) ← 支持Skip Scan
CREATE INDEX idx_country_created ON users(country, created_at);

-- 查询: WHERE created_at > '2023-01-01'
-- 使用Skip Scan: 5个国家 × 索引扫描

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 274** (sql, index):

```sql
-- 多查询模式优化

-- 查询模式1: WHERE status = ? AND created_at > ?
-- 查询模式2: WHERE created_at > ?
-- 查询模式3: WHERE status = ?

-- 策略: 创建(status, created_at)索引
CREATE INDEX idx_status_created ON users(status, cr
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 297** (sql, query):

```sql
-- 查看Skip Scan统计
SELECT
    schemaname,
    tablename,
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexrelname LIKE '%country%'
ORDER BY idx_sc
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 325** (sql, query):

```sql
-- 详细执行计划
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, COSTS)
SELECT * FROM users WHERE created_at > '2023-01-01';

-- 关键指标
/*
Index Skip Scan using idx_users_country_created
  Buffers: shared hit=850 read=0

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 355** (sql, index):

```sql
-- 包含查询所需的所有列
CREATE INDEX idx_status_created_email ON users(status, created_at, email);

-- Index Only Scan + Skip Scan
EXPLAIN (ANALYZE, BUFFERS)
SELECT email FROM users
WHERE created_at > '2023-01-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 370** (sql, index):

```sql
-- 创建分区表
CREATE TABLE orders_partitioned (
    order_id BIGSERIAL,
    region VARCHAR(10),
    status VARCHAR(20),
    created_at TIMESTAMPTZ,
    amount NUMERIC
) PARTITION BY RANGE (created_at);

--
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 408** (sql, index):

```sql
-- 场景: 订单系统
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    shop_id INT,
    user_id BIGINT,
    status VARCHAR(20),
    created_at TIMESTAMPTZ,
    amount NUMERIC
);

-- 索引
CREATE INDEX
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 435** (sql, index):

```sql
-- 场景: 日志表
CREATE TABLE application_logs (
    log_id BIGSERIAL PRIMARY KEY,
    level VARCHAR(10),
    service VARCHAR(50),
    timestamp TIMESTAMPTZ,
    message TEXT
);

-- 索引
CREATE INDEX idx_logs
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 463** (sql, index):

```sql
-- 场景1: 前导列基数过高
CREATE INDEX idx_user_email_status ON users(email, status);

-- 查询: WHERE status = 'active'
-- email基数=1000万 (唯一)
-- Skip Scan需要扫描1000万次，不如全表扫描

-- 场景2: 所有列基数都低
CREATE INDEX idx_type_s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 487** (sql, query):

```sql
-- 确保统计信息准确
ANALYZE users;

-- 检查统计信息
SELECT
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename = 'users';

-- n_distinct影响Skip Scan评估
-- 定期ANALYZE (autovacuum自动
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 510** (sql, query):

```sql
-- Skip Scan + 并行
SET max_parallel_workers_per_gather = 4;

EXPLAIN (ANALYZE)
SELECT COUNT(*) FROM large_table
WHERE created_at > '2023-01-01';

-- 计划:
-- Parallel Index Skip Scan
-- Workers: 4
-- 性能倍
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 526** (sql, query):

```sql
-- Skip Scan + JIT
SET jit = on;

EXPLAIN (ANALYZE)
SELECT * FROM users
WHERE created_at > '2023-01-01';

-- JIT优化Skip Scan循环
-- 性能提升5-10%

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 571** (sql, query):

```sql
-- 查看优化器决策
SET client_min_messages = debug1;
SET debug_print_plan = on;

EXPLAIN SELECT * FROM users WHERE created_at > '2023-01-01';

-- 查看日志
-- 包含Skip Scan评估过程

-- 强制不同计划
SET enable_indexskipscan =
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 10-pg_upgrade升级完整指南.md

**行 177** (sql, query):

```sql
-- 删除prepared transactions
SELECT * FROM pg_prepared_xacts;
-- 手动COMMIT或ROLLBACK

-- 删除旧扩展
DROP EXTENSION IF EXISTS tsearch2;  -- 已废弃

-- 更新pg_upgrade不支持的类型
-- （根据--check输出处理）

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 272** (sql, index):

```sql
-- 重建所有索引（提升性能）
REINDEX DATABASE mydb;

-- 或仅重建特定索引
REINDEX INDEX CONCURRENTLY idx_large_table;

```

**建议**:

- 添加索引构建性能测试

---

**行 282** (sql, query):

```sql
-- 启用AIO
ALTER SYSTEM SET io_direct = 'data';

-- 启用其他PG18特性
ALTER SYSTEM SET max_parallel_maintenance_workers = 8;

-- 重载配置
SELECT pg_reload_conf();

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 295** (sql, query):

```sql
-- 监控查询性能
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 10;

-- 监控缓存命中率
SELECT
    SUM(heap_blks_hit) / NULLIF(SUM(heap_blks_hit + heap_blks_read), 0)
FROM pg_statio_user_tables;
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 320** (sql, query):

```sql
-- 查看prepared transactions
SELECT * FROM pg_prepared_xacts;

-- 提交或回滚
COMMIT PREPARED 'transaction_id';
-- 或
ROLLBACK PREPARED 'transaction_id';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 11-VACUUM增强与积极冻结策略完整指南.md

**行 278** (sql, query):

```sql
-- 创建测试表
CREATE TABLE large_table (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    data JSONB,
    status
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 439** (sql, query):

```sql
-- 监控积极冻结效果
CREATE OR REPLACE FUNCTION check_eager_freeze_stats(
    schema_name TEXT DEFAULT 'public'
)
RETURNS TABLE (
    table_name TEXT,
    total_pages BIGINT,
    frozen_pages BIGINT,
    froze
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 516** (sql, query):

```sql
-- 旧版本：必须在表级设置
ALTER TABLE large_table SET (vacuum_truncate = off);

-- 问题：
-- ❌ 需要为每个表单独配置
-- ❌ 新创建的表默认启用truncate
-- ❌ 无法全局禁用（集群级配置）

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 528** (sql, query):

```sql
-- 新增全局配置（postgresql.conf）
vacuum_truncate = on  -- 默认值

-- 优先级：
-- 1. 表级设置（ALTER TABLE）
-- 2. 全局参数（postgresql.conf）
-- 3. 默认值（on）

-- 典型场景
-- 场景1：全局禁用，个别表启用
ALTER SYSTEM SET vacuum_truncate = off;
AL
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 585** (sql, query):

```sql
-- 会话1: 长查询（持有AccessShareLock）
BEGIN;
SELECT count(*) FROM large_table WHERE status = 'active';
-- 执行10分钟...

-- 会话2: VACUUM尝试truncate（需要AccessExclusiveLock）
VACUUM large_table;
-- ⚠️ 等待会话1释放锁...

--
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 602** (sql, query):

```sql
-- 查询被阻塞的会话数
SELECT
    blocked.pid AS blocked_pid,
    blocked.query AS blocked_query,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query,
    now() - blocked.query_start AS block
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 670** (sql, query):

```sql
-- 监控VACUUM truncate行为
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查询VACUUM truncate统计
SELECT
    schemaname,
    relname,
    last_vacuum,
    vacuum_count,

    -- 估算truncate节省的空间
    pg_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 737** (sql, query):

```sql
-- 创建XID风险监控函数
CREATE OR REPLACE FUNCTION calculate_xid_risk()
RETURNS TABLE (
    database_name NAME,
    oldest_xid XID,
    current_xid XID,
    xid_age BIGINT,
    remaining_xids BIGINT,
    risk_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 810** (sql, query):

```sql
-- 测试表：100GB，100亿行
CREATE TABLE xid_risk_test (
    id BIGSERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 场景1：传统VACUUM（PG 17）
-- vacuum_max_eager_freeze_failure_rate
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1055** (sql, query):

```sql
-- 策略1：按时间分区（推荐）
CREATE TABLE orders (
    order_id BIGSERIAL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    total_amount DECIMAL(12,2),
    status VARCHAR(20)
)
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1094** (sql, query):

```sql
-- 策略2：控制VACUUM扫描范围
-- 使用fillfactor预留空间，减少死元组

-- 高更新频率表
ALTER TABLE hot_table SET (
    fillfactor = 80,  -- 预留20%空间给HOT更新
    autovacuum_vacuum_scale_factor = 0.01,  -- 1%变更触发VACUUM
    autovacuum_v
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1115** (sql, query):

```sql
-- 策略3：分阶段执行大表VACUUM

-- 阶段1：快速清理（只清理死元组，不冻结）
VACUUM (FREEZE off, TRUNCATE off) large_table;
-- 耗时：30分钟

-- 阶段2：渐进式冻结（分批冻结页面）
DO $$
DECLARE
    block_start BIGINT;
    block_end BIGINT;
    total_bloc
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1213** (sql, query):

```sql
-- 使用pg_cron扩展自动调度
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 每天凌晨2点执行大表VACUUM（分散到多天）
-- 周一：orders表
SELECT cron.schedule('vacuum-orders', '0 2 * * 1',
    'VACUUM (VERBOSE) orders;');

-- 周二：order_it
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1478** (sql, query):

```sql
-- 创建VACUUM监控视图
CREATE OR REPLACE VIEW vacuum_monitor_dashboard AS
SELECT
    schemaname,
    relname AS table_name,

    -- 表大小信息
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname))
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1537** (sql, query):

```sql
-- 诊断1：检查长事务阻塞
SELECT
    pid,
    usename,
    application_name,
    state,
    query_start,
    now() - query_start AS duration,
    wait_event_type,
    wait_event,
    LEFT(query, 100) AS query_pr
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1588** (sql, query):

```sql
-- 紧急诊断
SELECT
    datname,
    age(datfrozenxid) AS xid_age,
    current_setting('autovacuum_freeze_max_age')::INT - age(datfrozenxid) AS remaining_xids,
    CASE
        WHEN age(datfrozenxid) > cur
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 11-查询优化器深度解析.md

**行 33** (sql, query):

```sql
-- 查看成本参数
SHOW seq_page_cost;      -- 顺序页成本: 1.0
SHOW random_page_cost;   -- 随机页成本: 4.0 (HDD) / 1.1 (SSD)
SHOW cpu_tuple_cost;     -- 元组处理成本: 0.01
SHOW cpu_index_tuple_cost;  -- 索引元组成本: 0.005
SHOW cpu
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 68** (sql, query):

```sql
-- 查看统计信息
SELECT
    tablename,
    attname,
    n_distinct,        -- 不同值数量
    correlation,       -- 物理顺序相关性
    most_common_vals,  -- 最常见值
    most_common_freqs  -- 最常见值频率
FROM pg_stats
WHERE table
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 99** (sql, query):

```sql
-- 提高统计精度
ALTER TABLE users ALTER COLUMN email
SET STATISTICS 1000;  -- 默认100

-- 全局设置
ALTER SYSTEM SET default_statistics_target = 500;

-- 重新收集
ANALYZE users;

-- 影响:
-- 更准确的基数估算
-- 更好的计划选择
-- ANALY
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 122** (sql, query):

```sql
-- 适用场景: 小表 JOIN 大表（有索引）
EXPLAIN ANALYZE
SELECT * FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE u.user_id = 123;

/*
Nested Loop
  ->  Index Scan on users (cost=0..8 rows=1)
        Index
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 143** (sql, query):

```sql
-- 适用场景: 等值JOIN，中等大小表
EXPLAIN ANALYZE
SELECT * FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.created_at > '2023-01-01';

/*
Hash Join
  Hash Cond: (o.product_id = p.product_id)

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 165** (sql, query):

```sql
-- 适用场景: 有序数据，大表JOIN
EXPLAIN ANALYZE
SELECT * FROM logs l
JOIN events e ON l.timestamp = e.timestamp
WHERE l.timestamp > '2023-01-01';

/*
Merge Join
  Merge Cond: (l.timestamp = e.timestamp)
  ->  In
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 194** (sql, query):

```sql
-- 全表扫描
EXPLAIN ANALYZE
SELECT * FROM users;

/*
Seq Scan on users (cost=0.00..10000.00 rows=100000)

适用:
✓ 小表
✓ 返回大部分行 (>10%)
✓ 无合适索引
*/

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 211** (sql, query):

```sql
-- Index Scan
EXPLAIN ANALYZE
SELECT * FROM users WHERE user_id = 123;

/*
Index Scan using users_pkey on users
  Index Cond: (user_id = 123)

适用:
✓ 高选择性查询
✓ 少量行返回
*/

-- Index Only Scan
EXPLAIN ANALY
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 241** (sql, query):

```sql
-- Bitmap Index Scan
EXPLAIN ANALYZE
SELECT * FROM users
WHERE status = 'active' OR created_at > '2023-01-01';

/*
Bitmap Heap Scan on users
  Recheck Cond: ((status = 'active') OR (created_at > '2023
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 267** (sql, query):

```sql
-- 原始查询（子查询）
SELECT * FROM users
WHERE user_id IN (
    SELECT user_id FROM orders WHERE amount > 1000
);

-- 优化器自动改写为JOIN
EXPLAIN
SELECT * FROM users
WHERE user_id IN (SELECT user_id FROM orders WHER
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 298** (sql, query):

```sql
-- Materialized CTE (默认)
WITH recent_orders AS (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    WHERE created_at > '2023-01-01'
    GROUP BY user_id
)
SELECT * FROM users u
JOIN recen
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 348** (sql, query):

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM large_table;

/*
Finalize Aggregate
  ->  Gather
        Workers Planned: 4
        Workers Launched: 4
        ->  Partial Aggregate
              ->
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 374** (sql, index):

```sql
-- 部分有序数据
CREATE INDEX idx_users_status_created ON users(status, created_at);

-- 查询
EXPLAIN ANALYZE
SELECT * FROM users
WHERE status = 'active'
ORDER BY status, created_at, user_id
LIMIT 100;

/*
Pos
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 404** (sql, index):

```sql
-- 多列索引非前导列查询
CREATE INDEX idx_country_email ON users(country, email);

-- PostgreSQL 17: 全表扫描
-- PostgreSQL 18: Skip Scan
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@example.com';

/*
Ind
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 424** (sql, query):

```sql
-- PostgreSQL 18: 更智能的并行哈希
EXPLAIN (ANALYZE)
SELECT * FROM large_table1 t1
JOIN large_table2 t2 ON t1.id = t2.ref_id;

/*
Gather
  Workers: 4
  ->  Parallel Hash Join
        Hash Cond: (t1.id = t2.re
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 452** (sql, query):

```sql
-- 多列统计（处理列相关性）
CREATE STATISTICS stats_user_country_city
ON country, city FROM users;

-- 示例
SELECT * FROM users
WHERE country = 'US' AND city = 'New York';

-- 无扩展统计: 独立性假设
-- Rows估算 = (国家US比例) × (城
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 511** (sql, query):

```sql
-- 降低某个路径成本
SET random_page_cost = 1.0;  -- 让索引更"便宜"

-- 提高并行度
SET parallel_setup_cost = 0;
SET parallel_tuple_cost = 0;

-- 临时调整（单个查询）
BEGIN;
SET LOCAL random_page_cost = 1.0;
SELECT ...;
COMMIT;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 532** (sql, query):

```sql
-- 估算计划
EXPLAIN
SELECT * FROM users WHERE user_id = 123;

/*
Index Scan using users_pkey on users (cost=0.42..8.44 rows=1 width=100)
  Index Cond: (user_id = 123)

cost=0.42..8.44:
  0.42: 启动成本
  8.44
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 552** (sql, query):

```sql
-- 实际执行
EXPLAIN ANALYZE
SELECT * FROM users WHERE user_id = 123;

/*
Index Scan using users_pkey on users (cost=0.42..8.44 rows=1 width=100) (actual time=0.015..0.016 rows=1 loops=1)
  Index Cond: (us
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 574** (sql, query):

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users WHERE status = 'active';

/*
Seq Scan on users (cost=0.00..10000.00 rows=5000 width=100) (actual time=0.010..25.123 rows=5123 loops=1)
  Filter: (status
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 598** (sql, query):

```sql
-- 方法1: 禁用顺序扫描
SET enable_seqscan = off;
SELECT * FROM users WHERE email = 'test@example.com';
RESET enable_seqscan;

-- 方法2: 降低随机页成本
SET random_page_cost = 0.1;
SELECT * FROM users WHERE email = 'tes
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 612** (sql, query):

```sql
-- 小表驱动大表
SELECT * FROM
    small_table s
    JOIN large_table l ON s.id = l.ref_id;

-- 优化器自动调整JOIN顺序
-- 查看实际顺序
EXPLAIN
SELECT * FROM
    table1 t1
    JOIN table2 t2 ON t1.id = t2.id
    JOIN table3
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 632** (sql, query):

```sql
-- 分区表
CREATE TABLE logs_partitioned (...) PARTITION BY RANGE (created_at);

-- 查询自动裁剪
EXPLAIN ANALYZE
SELECT * FROM logs_partitioned
WHERE created_at BETWEEN '2023-12-01' AND '2023-12-31';

/*
Append
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 12-JSONB高级应用指南.md

**行 5** (sql, query):

```sql
-- JSON: 存储原始文本
CREATE TABLE json_test (data JSON);
INSERT INTO json_test VALUES ('{"name":"Alice","age":30}');

-- JSONB: 二进制存储（推荐）
CREATE TABLE jsonb_test (data JSONB);
INSERT INTO jsonb_test VALUES
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 35** (sql, query):

```sql
-- 创建测试表
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    profile JSONB
);

INSERT INTO users (profile) VALUES
('{"name":"Alice","age":30,"tags":["vip","active"],"address":{"city":"NYC"}}'),
(
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 69** (sql, query):

```sql
-- 拼接
UPDATE users SET profile = profile || '{"verified":true}';

-- 删除键
UPDATE users SET profile = profile - 'age';

-- 删除多个键
UPDATE users SET profile = profile - ARRAY['age','tags'];

-- 删除路径
UPDATE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 103** (sql, index):

```sql
-- 默认GIN索引（jsonb_ops）
CREATE INDEX idx_profile ON users USING GIN (profile);

-- 支持的查询
-- @>, ?, ?|, ?&

-- jsonb_path_ops索引（更小，更快）
CREATE INDEX idx_profile_path ON users USING GIN (profile jsonb_path
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 120** (sql, index):

```sql
-- 索引特定路径
CREATE INDEX idx_profile_age ON users ((profile->'age'));

-- 索引转换后的值
CREATE INDEX idx_profile_age_int ON users (((profile->>'age')::int));

-- 使用
SELECT * FROM users WHERE (profile->>'age')
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 138** (sql, query):

```sql
-- Good: 使用@>
SELECT * FROM users WHERE profile @> '{"age":30}';

-- Bad: 使用函数
SELECT * FROM users WHERE (profile->>'age')::int = 30;
-- 无法使用jsonb_ops索引，但可使用表达式索引

-- Good: 存在性检查
SELECT * FROM users W
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 155** (sql, query):

```sql
-- Bad: 提取所有字段
SELECT
    profile->>'name',
    profile->>'age',
    profile->>'email'
FROM users;

-- Good: 一次提取
SELECT jsonb_populate_record(null::user_type, profile)
FROM users;

-- 或使用jsonb_to_rec
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 182** (sql, query):

```sql
-- 聚合为JSONB数组
SELECT jsonb_agg(profile) FROM users;

-- 聚合为JSONB对象
SELECT jsonb_object_agg(user_id, profile->'name') FROM users;

-- 示例: 统计标签
SELECT
    tag,
    COUNT(*) AS user_count
FROM users,
LAT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 201** (sql, query):

```sql
-- 嵌套聚合
SELECT jsonb_build_object(
    'total_users', COUNT(*),
    'avg_age', AVG((profile->>'age')::int),
    'users_by_city', (
        SELECT jsonb_object_agg(city, count)
        FROM (

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 224** (sql, index):

```sql
-- 用户事件表（schema-less）
CREATE TABLE user_events (
    event_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIM
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 253** (sql, query):

```sql
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(10),
    old_data JSONB,
    new_data JSONB,
    changed_fields JSONB,  -- 存储变更字段
    use
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 311** (sql, index):

```sql
-- 场景1: 频繁查询特定键
-- 使用表达式索引
CREATE INDEX idx_user_email ON users ((profile->>'email'));

-- 场景2: 多条件查询
-- 使用GIN索引
CREATE INDEX idx_profile_gin ON users USING GIN (profile);

-- 场景3: 特定路径查询
CREATE INDEX
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 326** (sql, query):

```sql
-- Bad: 多次访问JSONB
SELECT
    profile->>'name',
    profile->>'age',
    profile->>'email'
FROM users;

-- Good: 一次提取
SELECT (jsonb_populate_record(null::user_record, profile)).*
FROM users;

-- 或
SELE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 353** (sql, query):

```sql
-- PostgreSQL 18优化:
-- 1. 更快的JSONB解析
-- 2. 优化的GIN索引扫描
-- 3. 改进的jsonb_path函数

-- 测试查询
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users
WHERE profile @> '{"age":30}';

-- PostgreSQL 17: 25ms
-- PostgreSQL
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 370** (sql, query):

```sql
-- jsonb_path_query (SQL/JSON path)
SELECT jsonb_path_query(
    '{"items":[{"name":"item1","price":100},{"name":"item2","price":200}]}',
    '$.items[*] ? (@.price > 150)'
);

-- jsonb_path_exists
SE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 12-时态约束与时间段完整性指南.md

**行 120** (sql, query):

```sql
-- ❌ 传统主键（无法防止时间段冲突）
CREATE TABLE room_booking_old (
    room_id INT,
    booking_date DATE,
    guest_name TEXT,
    PRIMARY KEY (room_id, booking_date)  -- 仅保证每天每房间一个预订
);

-- 问题：同一天可以多个预订，时间段冲突！
IN
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 198** (sql, query):

```sql
-- 完整语法（PostgreSQL 18）
CREATE TABLE table_name (
    -- 业务主键列
    id INT,

    -- 时间段定义（两列）
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,

    -- 其他业务列
    data TEXT,

    --
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 241** (sql, index):

```sql
-- 案例：酒店房间预订系统
CREATE TABLE hotel_bookings (
    booking_id SERIAL,
    room_id INT NOT NULL,
    guest_name TEXT NOT NULL,
    check_in TIMESTAMPTZ NOT NULL,
    check_out TIMESTAMPTZ NOT NULL,
    b
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 279** (sql, query):

```sql
-- 案例：会议室管理（多维度时段约束）
CREATE TABLE meeting_rooms (
    building TEXT NOT NULL,
    floor INT NOT NULL,
    room_number INT NOT  NULL,
    meeting_start TIMESTAMPTZ NOT NULL,
    meeting_end TIMESTAMPTZ
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 310** (sql, query):

```sql
-- 案例：租赁合同管理
CREATE TABLE lease_contracts (
    contract_id SERIAL PRIMARY KEY,
    property_id INT NOT NULL,
    tenant_name TEXT NOT NULL,
    lease_start DATE NOT NULL,
    lease_end DATE NOT NULL,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 343** (sql, query):

```sql
-- WITHOUT OVERLAPS的等价实现（底层机制）
ALTER TABLE hotel_bookings
ADD CONSTRAINT hotel_bookings_no_overlap
EXCLUDE USING gist (
    room_id WITH =,
    tstzrange(check_in, check_out) WITH &&
);

-- 解释：
-- 1.
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 385** (sql, query):

```sql
-- 父表：员工合同
CREATE TABLE employee_contracts (
    employee_id INT,
    contract_start DATE NOT NULL,
    contract_end DATE NOT NULL,
    position TEXT,
    salary NUMERIC(10,2),

    CONSTRAINT valid_c
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 519** (sql, query):

```sql
-- PostgreSQL 18使用左闭右开区间（数学标准）
-- Range类型：tstzrange(lower, upper, '[)')

-- 实例
SELECT tstzrange('2025-01-15 10:00', '2025-01-15 12:00');
-- 输出：["2025-01-15 10:00:00+00","2025-01-15 12:00:00+00")

-- 边
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 541** (sql, query):

```sql
-- 酒店退房时间10:00，下一客人入住时间10:00 → 允许
INSERT INTO hotel_bookings VALUES
    (DEFAULT, 201, 'Alice', '2025-01-15 14:00', '2025-01-17 10:00', 'confirmed'),
    (DEFAULT, 201, 'Bob', '2025-01-17 10:00', '202
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 563** (sql, query):

```sql
-- 1. 房间信息表
CREATE TABLE rooms (
    room_id INT PRIMARY KEY,
    room_type TEXT,
    floor INT,
    price_per_night NUMERIC(10,2)
);

-- 2. 预订表（时态约束）
CREATE TABLE bookings (
    booking_id SERIAL,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 665** (sql, query):

```sql
-- 持仓表
CREATE TABLE positions (
    position_id SERIAL,
    account_id BIGINT NOT NULL,
    security_code TEXT NOT NULL,  -- 证券代码
    quantity BIGINT NOT NULL,
    valid_from TIMESTAMPTZ NOT NULL,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 748** (sql, query):

```sql
-- 无约束，应用层检查
CREATE TABLE bookings_app_check (
    booking_id SERIAL PRIMARY KEY,
    room_id INT,
    check_in TIMESTAMPTZ,
    check_out TIMESTAMPTZ
);

-- 应用层代码（Python示例）
def create_booking(room_id
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 782** (sql, query):

```sql
CREATE OR REPLACE FUNCTION check_booking_overlap()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM bookings_trigger_check
        WHERE room_id = NEW.room_id
          AND booking_id
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 811** (sql, query):

```sql
CREATE TABLE bookings_exclude (
    booking_id SERIAL PRIMARY KEY,
    room_id INT,
    check_in TIMESTAMPTZ,
    check_out TIMESTAMPTZ,

    EXCLUDE USING gist (
        room_id WITH =,
        tstzr
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 833** (sql, query):

```sql
CREATE TABLE bookings_temporal (
    booking_id SERIAL,
    room_id INT,
    check_in TIMESTAMPTZ NOT NULL,
    check_out TIMESTAMPTZ NOT NULL,

    CONSTRAINT valid_period CHECK (check_out > check_in
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 884** (sql, query):

```sql
-- 迁移步骤
-- 1. 创建新表（时态约束）
CREATE TABLE bookings_new (
    booking_id SERIAL,
    room_id INT NOT NULL,
    check_in TIMESTAMPTZ NOT NULL,
    check_out TIMESTAMPTZ NOT NULL,
    guest_name TEXT,

    C
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 946** (sql, index):

```sql
-- 1. 索引策略
-- PostgreSQL 18自动创建GiST索引，但可手动优化

-- 查看自动索引
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'bookings'
  AND indexdef LIKE '%gist%';

-- 2. 添加辅助索引（常见查询）
CREATE INDEX idx_booki
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 1010** (sql, query):

```sql
-- 性能测试：不同数据规模

-- 10万记录：性能优秀
CREATE TABLE test_10w AS
SELECT ... FROM generate_series(1, 100000);
-- INSERT平均3ms

-- 100万记录：性能良好
CREATE TABLE test_100w AS
SELECT ... FROM generate_series(1, 1000000);
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1053** (sql, query):

```sql
-- 创建约束违反日志表
CREATE TABLE temporal_constraint_violations (
    violation_id SERIAL PRIMARY KEY,
    occurred_at TIMESTAMPTZ DEFAULT now(),
    table_name TEXT,
    constraint_name TEXT,
    conflictin
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1105** (sql, query):

```sql
-- 监控时态约束性能
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched,
    pg_size_pretty(pg_relation_size(
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 13-存储过程与触发器实战.md

**行 5** (sql, query):

```sql
-- 函数 (FUNCTION)
CREATE OR REPLACE FUNCTION calculate_total(order_id INT)
RETURNS NUMERIC AS $$
DECLARE
    total NUMERIC;
BEGIN
    SELECT SUM(price * quantity) INTO total
    FROM order_items
    WH
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 65** (sql, query):

```sql
-- 返回TABLE
CREATE OR REPLACE FUNCTION get_user_orders(p_user_id INT)
RETURNS TABLE (
    order_id INT,
    order_date TIMESTAMPTZ,
    total_amount NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT o.
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 88** (sql, query):

```sql
CREATE OR REPLACE FUNCTION dynamic_query(
    table_name TEXT,
    condition TEXT
) RETURNS SETOF RECORD AS $$
DECLARE
    query TEXT;
BEGIN
    query := format('SELECT * FROM %I WHERE %s', table_name
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 112** (sql, query):

```sql
CREATE OR REPLACE FUNCTION process_large_table()
RETURNS VOID AS $$
DECLARE
    cur CURSOR FOR SELECT * FROM large_table;
    rec RECORD;
    counter INT := 0;
BEGIN
    OPEN cur;

    LOOP
        FE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 149** (sql, query):

```sql
-- 自动设置时间戳
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 183** (sql, query):

```sql
-- 审计日志
CREATE TABLE audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    user_name TEXT,
    changed_at TIMESTAMPTZ DEFAU
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 223** (sql, query):

```sql
-- 视图触发器
CREATE VIEW user_summary AS
SELECT
    user_id,
    username,
    COUNT(o.order_id) AS order_count,
    SUM(o.amount) AS total_spent
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
G
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 262** (sql, query):

```sql
-- 记录DDL操作
CREATE TABLE ddl_log (
    log_id BIGSERIAL PRIMARY KEY,
    event_type TEXT,
    object_type TEXT,
    object_identity TEXT,
    command TEXT,
    user_name TEXT,
    created_at TIMESTAMPT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 304** (sql, query):

```sql
-- 阻止DROP TABLE
CREATE OR REPLACE FUNCTION prevent_drop_table()
RETURNS event_trigger AS $$
BEGIN
    IF TG_TAG = 'DROP TABLE' THEN
        RAISE EXCEPTION '禁止删除表！请联系DBA。';
    END IF;
END;
$$ LANGUAG
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 326** (sql, query):

```sql
CREATE OR REPLACE FUNCTION safe_divide(a NUMERIC, b NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    RETURN a / b;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE '除数为零，返回NULL';
        RETURN N
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 347** (sql, query):

```sql
CREATE OR REPLACE FUNCTION get_table_data(table_name TEXT)
RETURNS SETOF RECORD AS $$
BEGIN
    RETURN QUERY EXECUTE format('SELECT * FROM %I', table_name);
END;
$$ LANGUAGE plpgsql;

-- 使用时指定列类型
SELE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 365** (sql, query):

```sql
CREATE OR REPLACE PROCEDURE batch_update_prices(
    category_id INT,
    discount_percent NUMERIC
)
LANGUAGE plpgsql AS $$
DECLARE
    batch_size INT := 1000;
    updated INT;
BEGIN
    LOOP

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 403** (sql, query):

```sql
-- VOLATILE (默认): 每行都调用
CREATE FUNCTION random_value() RETURNS FLOAT AS $$
    SELECT random();
$$ LANGUAGE SQL VOLATILE;

SELECT random_value() FROM generate_series(1, 10);
-- 每行不同的随机值

-- STABLE: 每个
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 430** (sql, query):

```sql
-- SQL函数自动内联
CREATE FUNCTION get_active_users()
RETURNS SETOF users AS $$
    SELECT * FROM users WHERE status = 'active';
$$ LANGUAGE SQL STABLE;

-- 查询
SELECT * FROM get_active_users() WHERE age > 2
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 452** (sql, query):

```sql
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    status order_status DEFAULT 'pending',
    cre
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 494** (sql, query):

```sql
CREATE OR REPLACE FUNCTION deduct_inventory(
    p_product_id INT,
    p_quantity INT
) RETURNS BOOLEAN AS $$
DECLARE
    current_stock INT;
BEGIN
    -- 锁定库存行
    SELECT stock INTO current_stock

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 532** (sql, query):

```sql
-- 订单汇总表
CREATE TABLE order_summary (
    user_id INT PRIMARY KEY,
    total_orders INT DEFAULT 0,
    total_amount NUMERIC DEFAULT 0,
    last_order_at TIMESTAMPTZ
);

-- 触发器维护汇总
CREATE OR REPLACE FU
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 581** (sql, query):

```sql
-- Bad: 可能无限递归
CREATE OR REPLACE FUNCTION bad_trigger()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users SET updated_at = now() WHERE user_id = NEW.user_id;
    RETURN NEW;  -- 触发器本身又会被触发
END;
$$ LANGUAGE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 603** (sql, query):

```sql
-- 行级触发器（每行触发一次）
CREATE TRIGGER trg_row_level
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION row_level_function();

-- 语句级触发器（每个语句触发一次）
CREATE TRIGGER trg_statement_level
    AFTER U
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 649** (sql, query):

```sql
CREATE OR REPLACE FUNCTION debug_function()
RETURNS VOID AS $$
DECLARE
    var1 INT := 100;
BEGIN
    RAISE NOTICE '变量值: %', var1;
    RAISE DEBUG '调试信息';
    RAISE LOG '日志信息';
    RAISE WARNING '警告信息
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 670** (sql, query):

```sql
-- 启用函数计时
ALTER FUNCTION expensive_function() SET log_min_duration_statement = 0;

-- 查看执行时间
SELECT
    funcname,
    calls,
    total_time / calls AS avg_time_ms,
    self_time / calls AS self_time_m
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 13-查询优化器增强完整指南.md

**行 196** (sql, query):

```sql
-- 典型的冗余自连接（ORM生成的SQL）
SELECT o1.order_id, o1.amount, o2.status
FROM orders o1
JOIN orders o2 ON o1.order_id = o2.order_id
WHERE o1.amount > 100;

-- 逻辑上等价于（无冗余）
SELECT order_id, amount, status
FROM o
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 271** (sql, query):

```sql
-- 原始查询（Django ORM生成）
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT
    o1.order_id,
    o1.order_date,
    o1.total_amount,
    o2.user_id,
    o2.status
FROM orders o1
INNER JOIN orders o2 ON o1.or
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 365** (sql, query):

```sql
-- 创建订单汇总视图
CREATE VIEW order_summary AS
SELECT
    o.order_id,
    o.user_id,
    o.total_amount,
    o.order_date,
    u.user_name,
    u.email
FROM orders o
JOIN users u ON o.user_id = u.user_id;


```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 390** (sql, query):

```sql
-- 4表JOIN！
SELECT
    o1.order_id,
    u1.user_name,
    o2.total_amount
FROM orders o1
JOIN users u1 ON o1.user_id = u1.user_id
JOIN orders o2 ON o1.order_id = o2.order_id  -- 冗余自连接
JOIN users u2 ON
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 405** (sql, query):

```sql
-- 消除冗余，仅2表JOIN
SELECT
    o.order_id,
    u.user_name,
    o.total_amount
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.total_amount > 500;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 424** (sql, query):

```sql
-- 检查查询是否触发自连接消除
EXPLAIN (ANALYZE, VERBOSE, BUFFERS)
SELECT ... ;  -- 查看EXPLAIN输出中是否有 "Self-Join Elimination" 标记

-- 使用auto_explain记录优化决策
LOAD 'auto_explain';
SET auto_explain.log_min_duration = 0;
SE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 458** (sql, query):

```sql
-- 原始查询
SELECT * FROM orders
WHERE status IN ('pending', 'processing', 'shipped');

-- PostgreSQL 17: 扩展为OR（低效）
WHERE (status = 'pending' OR status = 'processing' OR status = 'shipped')

-- PostgreSQL
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 479** (sql, query):

```sql
-- 复杂OR条件
SELECT * FROM products
WHERE (category_id = 10 AND status = 'active')
   OR (category_id = 20 AND status = 'active')
   OR (category_id = 30 AND status = 'active');

-- PostgreSQL 18自动重写为
SE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 502** (sql, index):

```sql
-- 测试场景：100万行表，IN列表包含10-10000个值

-- 创建测试表
CREATE TABLE test_in_performance (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    category_id INT NOT NULL,
    value NUMERIC(12,2),
    creat
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 571** (sql, index):

```sql
-- 场景：IN列表超过10000个值

-- ❌ 不推荐：超大IN列表
SELECT * FROM orders
WHERE order_id IN (SELECT unnest(ARRAY[... 50000个值 ...]));
-- 问题：查询计划生成慢、内存消耗大

-- ✅ 推荐：使用临时表
CREATE TEMP TABLE temp_order_ids (order_id BIGIN
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 615** (sql, query):

```sql
-- 原始查询
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM products
WHERE status = 'active' OR status = 'featured' OR status = 'hot';

-- PostgreSQL 17执行计划
Seq Scan on products  (cost=0..28500 rows=15000)
  Fil
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 650** (sql, query):

```sql
-- 复杂OR条件（电商促销规则）
SELECT * FROM orders
WHERE (category_id = 100 AND amount > 500)
   OR (category_id = 200 AND amount > 300)
   OR (category_id = 300 AND amount > 200);

-- PostgreSQL 18智能重写策略
-- 步骤1:
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 674** (sql, index):

```sql
-- 为OR重写优化创建复合索引
CREATE INDEX idx_category_amount ON orders(category_id, amount);

-- 验证索引使用
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE (category_id = 100 AND amount > 500)
   OR (category_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 691** (sql, query):

```sql
-- 1. 使用IN替代OR（同列）
-- ✅ 推荐
SELECT * FROM products WHERE category_id IN (10, 20, 30);
-- ❌ 避免
SELECT * FROM products WHERE category_id = 10 OR category_id = 20 OR category_id = 30;

-- 2. 使用ANY替代大IN列表

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 715** (sql, query):

```sql
-- 陷阱1: IN列表包含NULL
SELECT * FROM orders WHERE status IN ('active', NULL);
-- 行为：NULL被忽略，不等价于 status IS NULL
-- 解决：显式处理 WHERE (status IN ('active') OR status IS NULL)

-- 陷阱2: IN子查询返回NULL
SELECT * FROM
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 772** (sql, query):

```sql
-- 测试场景：365个日分区，查询1天数据

CREATE TABLE sales_data (
    sale_id BIGSERIAL,
    sale_date DATE NOT NULL,
    user_id BIGINT,
    amount NUMERIC(12,2),
    region VARCHAR(50)
) PARTITION BY RANGE (sale_da
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 865** (sql, query):

```sql
-- 场景：范围+列表复合分区
CREATE TABLE logs (
    log_id BIGSERIAL,
    log_date DATE NOT NULL,
    region VARCHAR(20) NOT NULL,
    level VARCHAR(10),
    message TEXT
) PARTITION BY RANGE (log_date);

-- 按日期范
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 919** (sql, query):

```sql
-- 场景：基于表达式的分区键
CREATE TABLE events (
    event_id BIGSERIAL,
    event_time TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(50),
    payload JSONB
) PARTITION BY RANGE (date_trunc('month', event_time));
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 956** (sql, query):

```sql
-- 场景：两个分区表JOIN

CREATE TABLE orders_partitioned (
    order_id BIGSERIAL,
    order_date DATE NOT NULL,
    user_id BIGINT,
    amount NUMERIC(12,2)
) PARTITION BY RANGE (order_date);

CREATE TABLE o
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1026** (sql, query):

```sql
-- PostgreSQL 18默认启用，可验证
SHOW enable_partitionwise_join;  -- on

SHOW enable_partitionwise_aggregate;  -- on

-- 如需禁用（调试用）
SET enable_partitionwise_join = off;

-- 验证是否生效
EXPLAIN (VERBOSE)
SELECT ...
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1043** (sql, query):

```sql
-- 查看分区表统计
SELECT
    schemaname,
    tablename AS parent_table,

    -- 分区数量
    (SELECT count(*)
     FROM pg_inherits i
     WHERE i.inhparent = c.oid) AS partition_count,

    -- 总大小
    pg_size_p
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1137** (sql, query):

```sql
-- 1. 检查FDW是否支持下推
SELECT
    fdwname,
    fdwoptions
FROM pg_foreign_data_wrapper
WHERE fdwname = 'postgres_fdw';

-- postgres_fdw从PG 9.6开始支持下推

-- 2. 配置外部表支持下推
ALTER SERVER foreign_server OPTIONS (

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1195** (sql, query):

```sql
-- 架构：
-- - 订单数据库（本地）：orders, order_items
-- - 用户中心数据库（远程）：users, user_preferences

-- 1. 配置外部数据源
CREATE EXTENSION postgres_fdw;

CREATE SERVER user_center_server
    FOREIGN DATA WRAPPER postgres_fdw
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1295** (sql, query):

```sql
-- ❌ 场景1: 包含易失函数（VOLATILE）
SELECT * FROM local_table l
JOIN remote_table r ON l.id = r.id
WHERE l.created_at > now();  -- now()是VOLATILE函数
-- 解决：改用STABLE函数
WHERE l.created_at > CURRENT_TIMESTAMP;

--
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1326** (sql, index):

```sql
-- 1. 使用列投影（避免传输无用列）
-- ✅ 推荐
SELECT r.id, r.name FROM remote_table r WHERE r.active = true;
-- ❌ 避免
SELECT * FROM remote_table r WHERE r.active = true;

-- 2. 在远程端创建索引
-- 在远程数据库执行
CREATE INDEX idx_rem
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 1373** (sql, query):

```sql
-- 典型的相关子查询（性能灾难）
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    c.customer_id,
    c.customer_name,
    c.email,
    (SELECT COUNT(*)
     FROM orders o
     WHERE o.customer_id = c.customer_id
       AND o.o
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1436** (sql, query):

```sql
-- 优化器自动重写为（概念上等价）
WITH order_stats AS (
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS total_spent
    FROM orders
    WHERE order_date >= '2024-01-01'

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1509** (sql, query):

```sql
-- 三层嵌套相关子查询（极端场景）
SELECT
    p.product_id,
    p.product_name,
    p.category_id,

    -- 子查询1: 订单数
    (SELECT COUNT(DISTINCT o.order_id)
     FROM orders o
     JOIN order_items oi ON o.order_id =
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1556** (sql, query):

```sql
-- 优化器自动重写为（简化版）
WITH order_stats AS (
    SELECT
        oi.product_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oi.quantity) AS total_quantity,
        MIN(o.order_date) AS fir
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1628** (sql, query):

```sql
-- EXISTS相关子查询
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.customer_id, c.customer_name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.customer_id
      AND o.order_dat
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1666** (sql, query):

```sql
-- NOT EXISTS（反Semi-Join）
SELECT c.customer_id, c.customer_name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.customer_id
      AND o.order_date >= '2025-0
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1700** (sql, query):

```sql
-- 1. 优先使用JOIN替代相关子查询
-- ✅ 推荐
SELECT c.*, os.order_count
FROM customers c
LEFT JOIN (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
) os ON c.customer_id = o
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1742** (sql, query):

```sql
-- 场景1: 包含易失函数
SELECT c.*,
    (SELECT COUNT(*) FROM orders o
     WHERE o.customer_id = c.customer_id
       AND o.created_at > now() - INTERVAL '1 hour')  -- now()是VOLATILE
FROM customers c;
-- 无法去相
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1821** (sql, query):

```sql
-- 测试查询：8表JOIN（TPC-H Q5变体）
EXPLAIN (ANALYZE, TIMING)
SELECT
    n.n_name AS nation,
    SUM(l.l_extendedprice * (1 - l.l_discount)) AS revenue
FROM customer c
JOIN orders o ON c.c_custkey = o.o_custke
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1866** (sql, query):

```sql
-- 典型星型模型：1个事实表 + 5个维度表
SELECT
    d.date_year,
    p.product_category,
    c.customer_segment,
    g.geo_region,
    s.store_type,
    SUM(f.sales_amount) AS total_sales,
    SUM(f.quantity) AS total
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1958** (sql, query):

```sql
-- PostgreSQL 18默认启用星型优化
SHOW enable_star_schema_optimization;  -- on

-- 查看是否触发星型优化
EXPLAIN (VERBOSE, COSTS)
SELECT ... FROM fact_table JOIN dim1 JOIN dim2 ...;

-- 在EXPLAIN输出中查找：
-- "Star-Schema Opt
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2004** (sql, query):

```sql
-- 场景：嵌套循环中重复访问同一行
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    o.order_id,
    o.order_date,
    c.customer_name,
    c.email
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_da
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2054** (sql, query):

```sql
-- 1. 检查Memoize是否启用
SHOW enable_memoize;  -- on (PG 14+)

-- 2. 监控缓存命中率
SELECT
    query,
    calls,

    -- 提取Memoize统计（需解析EXPLAIN JSON）
    (SELECT jsonb_path_query(
        to_jsonb(pg_stat_stateme
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2083** (sql, query):

```sql
-- PostgreSQL 18扩展统计支持更多类型

-- 1. 多列依赖关系
CREATE STATISTICS city_state_deps (dependencies)
ON city, state FROM addresses;

-- 2. 多维直方图（MCV - Most Common Values）
CREATE STATISTICS product_category_brand
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2110** (sql, query):

```sql
-- 查看扩展统计信息
SELECT
    stxname AS stats_name,
    stxkeys AS column_numbers,
    stxkind AS stat_types,
    stxndistinct AS ndistinct_data,
    stxdependencies AS dependency_data
FROM pg_statistic_ext
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2132** (sql, query):

```sql
-- 场景：关联列查询

-- 创建测试数据（强关联）
CREATE TABLE orders_test (
    order_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    country VARCHAR(2),
    region VARCHAR(50),
    amount NUMERIC(12,2)
);

-- country和r
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2192** (sql, query):

```sql
-- PostgreSQL 18动态采样策略

-- 1. 自适应采样率
ALTER TABLE large_table SET (n_distinct_inherited = 1000000);

-- 2. 监控统计信息陈旧度
SELECT
    schemaname,
    tablename,
    last_analyze,
    n_live_tup,
    n_dead_t
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2266** (sql, query):

```sql
-- PostgreSQL 18并行参数

-- 全局配置
max_parallel_workers_per_gather = 8  -- 单查询最大worker数
max_parallel_workers = 16  -- 全局最大并行worker
max_worker_processes = 32  -- 总worker进程数

parallel_leader_participation =
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2329** (sql, index):

```sql
-- 场景：大表GROUP BY

CREATE TABLE sales_data (
    sale_id BIGSERIAL,
    product_id INT,
    region_id INT,
    sale_date DATE,
    amount NUMERIC(12,2)
);

-- 插入10亿行
INSERT INTO sales_data (product_id,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 2433** (sql, query):

```sql
-- TPC-H Query 1: Pricing Summary Report
SELECT
    l_returnflag,
    l_linestatus,
    SUM(l_quantity) AS sum_qty,
    SUM(l_extendedprice) AS sum_base_price,
    SUM(l_extendedprice * (1 - l_discoun
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2462** (sql, query):

```sql
-- TPC-H Query 2: Minimum Cost Supplier
SELECT
    s_acctbal,
    s_name,
    n_name,
    p_partkey,
    p_mfgr,
    s_address,
    s_phone,
    s_comment
FROM part, supplier, partsupp, nation, region
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2504** (sql, query):

```sql
-- TPC-H Query 20: Potential Part Promotion
SELECT
    s_name,
    s_address
FROM supplier, nation
WHERE s_suppkey IN (
    SELECT ps_suppkey
    FROM partsupp
    WHERE ps_partkey IN (
        SELECT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 2701** (sql, query):

```sql
-- 1. 启用慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1秒
ALTER SYSTEM SET log_statement = 'all';  -- 记录所有SQL
ALTER SYSTEM SET log_duration = on;
SELECT pg_reload_conf();

-- 2. 安装pg_st
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 14-并行查询与JIT编译增强指南.md

**行 158** (sql, query):

```sql
-- 创建测试表（1000万行）
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    total_amount NUMERIC(12,2),
    discount_rate NUMERIC(3,2),
    tax_rate NUMERIC(3
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 222** (sql, query):

```sql
-- 1. 算术表达式
SELECT a + b * c / (d - e) FROM table;
-- JIT优化：编译为内联汇编，消除函数调用

-- 2. 逻辑表达式
SELECT * FROM table WHERE a > 10 AND b < 20 OR c = 'value';
-- JIT优化：短路求值，分支预测

-- 3. 函数调用
SELECT upper(name), l
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 272** (sql, query):

```sql
-- 创建测试表
CREATE TABLE large_table (
    id BIGINT PRIMARY KEY,
    user_id INT,
    amount NUMERIC(12,2),
    created_at TIMESTAMPTZ
);

CREATE TABLE small_table (
    user_id INT PRIMARY KEY,
    use
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 406** (sql, query):

```sql
-- 启用详细JIT统计
SET jit = on;
SET jit_above_cost = 100000;
SET jit_inline_above_cost = 500000;
SET jit_optimize_above_cost = 500000;
SET jit_expressions = on;
SET jit_tuple_deforming = on;
SET jit_profil
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 475** (sql, query):

```sql
-- 查看实际分配的worker数量
EXPLAIN (ANALYZE, VERBOSE)
SELECT COUNT(*) FROM large_table
WHERE amount > 1000;

/*
Finalize Aggregate  (cost=... rows=1 width=8)
  ->  Gather  (cost=... rows=6 width=8)
        Wo
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 518** (sql, index):

```sql
-- 位图索引扫描的并行化（PG18优化）
CREATE INDEX idx_orders_amount ON orders (total_amount);
CREATE INDEX idx_orders_date ON orders (order_date);

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE total_amount
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 561** (sql, query):

```sql
-- TPC-H Q1: 聚合查询
SELECT
    l_returnflag,
    l_linestatus,
    SUM(l_quantity) AS sum_qty,
    SUM(l_extendedprice) AS sum_base_price,
    SUM(l_extendedprice * (1 - l_discount)) AS sum_disc_price,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 595** (sql, query):

```sql
-- 业务查询：用户行为分析
WITH user_orders AS (
    SELECT
        user_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS total_spent,
        AVG(total_amount) AS avg_order_value,
        MAX(or
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 667** (sql, query):

```sql
-- 高性能服务器（32核/128GB）
ALTER SYSTEM SET max_parallel_workers_per_gather = 8;
ALTER SYSTEM SET max_parallel_workers = 16;
ALTER SYSTEM SET parallel_setup_cost = 500;  -- 降低门槛
ALTER SYSTEM SET parallel_tu
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 692** (sql, query):

```sql
-- 查看查询成本
EXPLAIN (COSTS ON)
SELECT ... FROM large_table;

-- 调整成本参数以影响计划选择
SET random_page_cost = 1.1;  -- SSD场景（默认4.0）
SET seq_page_cost = 1.0;
SET cpu_tuple_cost = 0.01;
SET cpu_operator_cost = 0.0
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 741** (sql, query):

```sql
-- 1. 全局启用JIT（默认）
ALTER SYSTEM SET jit = on;

-- 2. 针对特定查询禁用JIT（如短查询）
SET jit = off;
SELECT * FROM small_table WHERE id = 123;

-- 3. 会话级临时启用
SET LOCAL jit_above_cost = 10000;  -- 降低阈值
SELECT ... FROM
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 767** (sql, query):

```sql
-- 创建监控视图
CREATE OR REPLACE VIEW parallel_query_stats AS
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,

    -- 并行度
    (regexp_match(query, 'Workers Launched: (\d+)'))[1]::int
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 816** (sql, query):

```sql
-- 实时查看并行查询
SELECT
    pid,
    usename,
    application_name,
    state,
    query,

    -- 并行worker识别
    CASE
        WHEN backend_type = 'parallel worker' THEN '⚙️ Worker'
        ELSE '👤 Leader'

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 852** (sql, query):

```sql
-- 查看JIT编译热点
SELECT
    queryid,
    query,
    calls,

    -- JIT统计
    jit_functions,
    jit_generation_time,
    jit_inlining_time,
    jit_optimization_time,
    jit_emission_time,

    -- JIT总开销
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 910** (sql, query):

```sql
-- ❌ 无法并行（游标）
DECLARE cur CURSOR FOR
    SELECT * FROM large_table WHERE amount > 1000;

-- ✅ 改为批量查询
SELECT * FROM large_table
WHERE amount > 1000
LIMIT 10000 OFFSET 0;  -- 分页处理

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 923** (sql, query):

```sql
-- JIT不适用的场景

-- 1. 短查询（编译开销>执行时间）
SELECT * FROM users WHERE id = 123;
-- 执行时间：0.5ms，JIT编译：15ms → 得不偿失

-- 2. 大量小事务（OLTP）
BEGIN;
INSERT INTO orders VALUES (...);
UPDATE inventory SET quantity = quanti
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 14-数据类型深度解析.md

**行 7** (sql, query):

```sql
-- 类型选择
SMALLINT    -- 2字节, -32768 to 32767
INTEGER     -- 4字节, -2^31 to 2^31-1
BIGINT      -- 8字节, -2^63 to 2^63-1

-- 自增
SERIAL      -- INTEGER + SEQUENCE
BIGSERIAL   -- BIGINT + SEQUENCE

-- 示例
CRE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 39** (sql, query):

```sql
-- 浮点类型
REAL           -- 4字节, 6位精度
DOUBLE PRECISION  -- 8字节, 15位精度

-- 定点类型（推荐金额）
NUMERIC(10,2)  -- 总10位，小数2位
DECIMAL(10,2)  -- 与NUMERIC等价

-- 金额存储
CREATE TABLE orders (
    order_id BIGSERIAL PRIMAR
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 71** (sql, query):

```sql
-- 类型对比
VARCHAR(n)  -- 变长，最大n字符
TEXT        -- 变长，无限制
CHAR(n)     -- 定长，空格填充

-- 性能测试
CREATE TABLE text_test (
    id SERIAL PRIMARY KEY,
    col_varchar VARCHAR(100),
    col_text TEXT,
    col_char
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 110** (sql, index):

```sql
-- tsvector: 预处理的文本向量
CREATE TABLE documents (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    search_vector tsvector
);

-- 自动更新tsvector
CREATE OR REPLACE FUNCTION update_search_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 149** (sql, query):

```sql
-- 日期时间类型
DATE           -- 日期
TIME           -- 时间
TIMESTAMP      -- 日期时间（无时区）
TIMESTAMPTZ    -- 日期时间（带时区，推荐）
INTERVAL       -- 时间间隔

-- 推荐: 始终使用TIMESTAMPTZ
CREATE TABLE events (
    event_id BIGSERI
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 175** (sql, query):

```sql
-- INTERVAL运算
SELECT
    now() + INTERVAL '1 day' AS tomorrow,
    now() - INTERVAL '7 days' AS week_ago,
    now() + INTERVAL '1 hour 30 minutes' AS later;

-- 日期截断
SELECT
    date_trunc('hour', now(
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 217** (sql, index):

```sql
-- 创建数组列
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    tags TEXT[],
    scores INT[]
);

-- 插入
INSERT INTO users (tags, scores) VALUES
(ARRAY['vip', 'active'], ARRAY[95, 87, 92]),
('{premiu
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 251** (sql, query):

```sql
-- 聚合为数组
SELECT array_agg(user_id) AS user_ids
FROM users
WHERE status = 'active';

-- 去重聚合
SELECT array_agg(DISTINCT category) AS categories
FROM products;

-- 解包数组
SELECT unnest(tags) AS tag
FROM us
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 281** (sql, index):

```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_data JSONB
);

-- 嵌套JSON
INSERT INTO products (product_data) VALUES
('{
    "name": "Laptop",
    "price": 999.99,
    "specs": {
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 323** (sql, query):

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- UUID生成
SELECT
    uuid_generate_v4() AS v4,      -- 随机UUID
    gen_random_uuid() AS random,   -- 随机（内置）
    uuidv7() AS v7;                -- UU
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 365** (sql, query):

```sql
-- 创建枚举
CREATE TYPE order_status AS ENUM (
    'pending',
    'paid',
    'shipped',
    'delivered',
    'cancelled'
);

CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    status order_sta
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 403** (sql, index):

```sql
-- 创建复合类型
CREATE TYPE address_type AS (
    street TEXT,
    city TEXT,
    state VARCHAR(2),
    zip_code VARCHAR(10)
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT,
    a
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 443** (sql, query):

```sql
-- 范围类型
int4range     -- INTEGER范围
int8range     -- BIGINT范围
numrange      -- NUMERIC范围
tsrange       -- TIMESTAMP范围
tstzrange     -- TIMESTAMPTZ范围
daterange     -- DATE范围

-- 创建范围
SELECT
    int4rang
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 499** (sql, index):

```sql
-- 类型
INET    -- IP地址或网络
CIDR    -- 网络地址（必须有前缀）
MACADDR -- MAC地址

-- 示例
CREATE TABLE access_logs (
    log_id BIGSERIAL PRIMARY KEY,
    client_ip INET,
    server_ip INET,
    network CIDR,
    creat
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 540** (sql, index):

```sql
-- 创建向量
CREATE EXTENSION vector;

CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    vec vector(128)
);

-- 插入
INSERT INTO embeddings (vec) VALUES
('[0.1, 0.2, 0.3, ...]'),  -- 文本格式
(ARRAY[0.1,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 575** (sql, query):

```sql
-- 文本转数值
SELECT '123'::INTEGER;
SELECT CAST('123' AS INTEGER);

-- 数值转文本
SELECT 123::TEXT;

-- 日期转换
SELECT '2024-01-01'::DATE;
SELECT to_date('2024-01-01', 'YYYY-MM-DD');

-- JSONB转换
SELECT '{"name":"
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 594** (sql, query):

```sql
-- 自动转换
SELECT * FROM orders WHERE order_id = '123';  -- TEXT→INTEGER

-- 注意：可能影响索引使用
-- Bad
SELECT * FROM users WHERE user_id = '123';  -- 如果user_id是INTEGER

-- Good
SELECT * FROM users WHERE user_id
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 612** (sql, query):

```sql
-- 创建domain（带约束的类型别名）
CREATE DOMAIN email_type AS TEXT
CHECK (VALUE ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

CREATE DOMAIN phone_type AS TEXT
CHECK (VALUE ~ '^\d{3}-\d{3}-\d{4}$');

CRE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 640** (sql, query):

```sql
-- 存储效率测试（100万行）
CREATE TABLE type_comparison (
    id BIGINT,                    -- 8字节
    status VARCHAR(20),           -- 变长，平均10字节
    status_enum order_status,     -- 4字节
    amount NUMERIC(12,2
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 15-WAL与检查点优化完整指南.md

**行 111** (sql, query):

```sql
-- 插入一行数据
INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com');

-- 生成的WAL记录（简化）
{
    "type": "HEAP_INSERT",
    "relation": "users (OID 16384)",
    "block": 0,
    "offset":
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 182** (sql, query):

```sql
-- 测试：10万行INSERT操作的WAL生成量

-- PostgreSQL 17（默认压缩）
CREATE TABLE test_wal (
    id BIGSERIAL PRIMARY KEY,
    data TEXT
);

-- 记录WAL位置
SELECT pg_current_wal_lsn() AS start_lsn \gset

-- 插入数据
INSERT INTO
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 267** (sql, query):

```sql
-- 模拟检查点风暴
-- 大量写入 → 大量脏页 → 检查点刷盘 → I/O尖峰

CREATE TABLE wal_intensive (
    id BIGSERIAL,
    payload BYTEA
);

-- 写入10GB数据
INSERT INTO wal_intensive (payload)
SELECT gen_random_bytes(10240)  -- 10KB
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 307** (sql, query):

```sql
-- 测试不同压缩算法

-- 1. 无压缩（基线）
ALTER SYSTEM SET wal_compression = off;
SELECT pg_reload_conf();

-- 2. pglz压缩（传统，PG 9.5+）
ALTER SYSTEM SET wal_compression = pglz;
SELECT pg_reload_conf();

-- 3. lz4压缩（PG
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 344** (sql, query):

```sql
-- PostgreSQL 18流复制增强

-- 1. 并行WAL解码（主库）
ALTER SYSTEM SET max_wal_senders = 10;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET wal_sender_timeout = 60000;  -- 60s

-- 2. 断点续传优化（从库）
-- 从
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 467** (sql, query):

```sql
-- 监控检查点性能

-- 触发检查点前
SELECT
    pg_current_wal_lsn() AS wal_before,
    now() AS time_before \gset

-- 手动触发检查点
CHECKPOINT;

-- 检查点后
SELECT
    pg_current_wal_lsn() AS wal_after,
    now() AS time_aft
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 522** (sql, query):

```sql
-- 核心WAL参数

-- 1. WAL缓冲区大小
SHOW wal_buffers;  -- 默认：-1（自动，约shared_buffers的1/32）
-- 推荐：高写入场景设置64MB-256MB
ALTER SYSTEM SET wal_buffers = '128MB';

-- 2. WAL文件大小
SHOW wal_segment_size;  -- 编译时固定，默认16MB
-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 557** (sql, query):

```sql
-- 检查点参数

-- 1. 检查点超时时间
SHOW checkpoint_timeout;  -- 默认：5min
-- 推荐：高写入场景15-30min
ALTER SYSTEM SET checkpoint_timeout = '15min';

-- 2. WAL大小触发阈值
SHOW max_wal_size;  -- 默认：1GB
-- 推荐：高写入场景4GB-16GB
ALTER
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 591** (sql, query):

```sql
-- 高性能OLTP场景（1000+ TPS）

-- WAL配置
ALTER SYSTEM SET wal_buffers = '128MB';
ALTER SYSTEM SET wal_compression = 'lz4';  -- CPU友好
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET synchronous_commi
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 716** (sql, query):

```sql
-- 创建监控视图
CREATE OR REPLACE VIEW wal_health_check AS
SELECT
    -- WAL生成速率
    pg_wal_lsn_diff(pg_current_wal_lsn(), pg_current_wal_lsn() - '0/10000000'::pg_lsn) / 60.0 AS wal_rate_mb_per_min,

    --
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 774** (sql, query):

```sql
-- 1. WAL生成统计
SELECT
    pg_current_wal_lsn() AS current_lsn,
    pg_walfile_name(pg_current_wal_lsn()) AS current_wal_file,

    -- 距离上次重启的WAL量
    pg_size_pretty(
        pg_wal_lsn_diff(pg_current_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 831** (sql, query):

```sql
-- 查看WAL相关的等待事件
SELECT
    wait_event_type,
    wait_event,
    COUNT(*) AS wait_count,

    -- 等待描述
    CASE wait_event
        WHEN 'WALWrite' THEN 'WAL写入到磁盘'
        WHEN 'WALSync' THEN 'WAL fsync同
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 930** (sql, query):

```sql
-- 检查恢复状态
SELECT
    pg_is_in_recovery() AS in_recovery,
    pg_last_wal_receive_lsn() AS receive_lsn,
    pg_last_wal_replay_lsn() AS replay_lsn,

    -- 恢复延迟
    pg_size_pretty(
        pg_wal_lsn_d
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 15-扩展开发完整指南.md

**行 35** (sql, query):

```sql
-- my_extension--1.0.sql

-- 创建schema
CREATE SCHEMA IF NOT EXISTS my_extension;

-- 创建函数
CREATE OR REPLACE FUNCTION my_extension.hello(name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN 'Hello, ' || name
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 143** (sql, query):

```sql
-- SQL包装
CREATE OR REPLACE FUNCTION add_numbers(INT, INT)
RETURNS INT AS '$libdir/my_extension', 'add_numbers'
LANGUAGE C IMMUTABLE STRICT;

-- 使用
SELECT add_numbers(10, 20);  -- 30

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 228** (sql, query):

```sql
-- SQL定义
CREATE TYPE complex;

CREATE FUNCTION complex_in(cstring)
RETURNS complex AS '$libdir/complex'
LANGUAGE C IMMUTABLE STRICT;

CREATE FUNCTION complex_out(complex)
RETURNS cstring AS '$libdir/c
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 355** (sql, query):

```sql
-- auto_partition扩展
CREATE OR REPLACE FUNCTION auto_partition.create_partition_if_not_exists(
    parent_table TEXT,
    partition_column TEXT,
    partition_value DATE
) RETURNS VOID AS $$
DECLARE

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 411** (sql, query):

```sql
-- 使用pgTAP
CREATE EXTENSION pgtap;

-- 测试脚本
BEGIN;
SELECT plan(5);

SELECT has_function('my_extension', 'hello', ARRAY['text']);
SELECT function_returns('my_extension', 'hello', ARRAY['text'], 'text')
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 434** (sql, query):

```sql
-- 性能比较
\timing on

-- 测试1000次调用
SELECT my_extension.expensive_function(i)
FROM generate_series(1, 1000) i;

-- 与原生函数对比
SELECT built_in_function(i)
FROM generate_series(1, 1000) i;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 491** (sql, query):

```sql
-- 创建监控函数
CREATE OR REPLACE FUNCTION monitor.table_stats()
RETURNS TABLE (
    table_name TEXT,
    row_count BIGINT,
    total_size TEXT,
    index_size TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 518** (sql, query):

```sql
-- 字符串工具
CREATE OR REPLACE FUNCTION utils.slugify(input TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN lower(regexp_replace(
        regexp_replace(input, '[^a-zA-Z0-9\s-]', '', 'g'),
        '[\s-]+', '-'
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 16-事务隔离级别深度解析.md

**行 27** (sql, query):

```sql
-- 会话1
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
-- 不提交

-- 会话2
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT balance FROM accounts WHERE account_id = 1;
-- 看
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 73** (sql, query):

```sql
-- 会话1
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE account_id = 1;
-- 读取: 1000

-- 会话2
BEGIN;
UPDATE accounts SET balance = balance + 500 WHERE account_id = 1
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 92** (sql, query):

```sql
-- 会话1
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE account_id = 1;  -- 1000
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;

-- 会话2
BEGIN TR
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 140** (sql, query):

```sql
-- 会话1
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*) FROM orders WHERE user_id = 123;  -- 假设为5

-- 会话2
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
INSERT INTO orders (user_id, am
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 201** (sql, query):

```sql
-- PostgreSQL不会发生（最低级别是READ COMMITTED）

-- 会话1
BEGIN;
UPDATE accounts SET balance = 0 WHERE account_id = 1;
-- 未提交

-- 会话2
SELECT balance FROM accounts WHERE account_id = 1;
-- 读取旧值，不会读到0（未提交的值）

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 216** (sql, query):

```sql
-- Read Committed级别会发生

-- 会话1
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT balance FROM accounts WHERE account_id = 1;  -- 1000

-- 会话2
UPDATE accounts SET balance = 2000 WHERE account_id
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 235** (sql, query):

```sql
-- PostgreSQL的REPEATABLE READ防止幻读

-- 会话1
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM orders WHERE user_id = 123;  -- 5

-- 会话2
INSERT INTO orders (user_id, amount) VALUES
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 252** (sql, query):

```sql
-- 只有SERIALIZABLE可以防止

-- 场景: 账户总和必须>=0
CREATE TABLE accounts (account_id INT, balance NUMERIC);
INSERT INTO accounts VALUES (1, 100), (2, 100);

-- 会话1 (REPEATABLE READ)
BEGIN TRANSACTION ISOLATION L
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 283** (sql, query):

```sql
-- FOR UPDATE: 排他锁
BEGIN;
SELECT * FROM accounts WHERE account_id = 1 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
COMMIT;

-- FOR SHARE: 共享锁
BEGIN;
SELECT * FROM acco
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 312** (sql, index):

```sql
-- 显式锁表
LOCK TABLE accounts IN EXCLUSIVE MODE;

-- 锁模式:
ACCESS SHARE          -- SELECT
ROW SHARE             -- SELECT FOR UPDATE/SHARE
ROW EXCLUSIVE         -- INSERT/UPDATE/DELETE
SHARE UPDATE EXCL
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 383** (python, loop):

```python
import psycopg2
from time import sleep

def transaction_with_retry(conn, operation, max_retries=5):
    """带重试的事务"""

    for attempt in range(max_retries):
        try:
            cursor = conn.curs
```

**建议**:

- 添加数据库操作性能测试
- 添加循环性能测试

---

### 16-统计信息增强与查询规划指南.md

**行 103** (sql, query):

```sql
-- pg_statistic表是PostgreSQL统计信息的核心存储
-- 注意：直接查询pg_statistic需要超级用户权限，一般使用pg_stats视图

SELECT
    schemaname,
    tablename,
    attname,
    null_frac,           -- NULL值比例
    avg_width,           -- 平
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 142** (sql, query):

```sql
-- 创建测试表
CREATE TABLE sales (
    sale_id BIGSERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    amount NUMERIC(12,2),
    region TEXT,
    category TEXT
);

INSERT INTO sales
SELECT
    generate_ser
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 218** (sql, query):

```sql
-- 创建数据倾斜的表
CREATE TABLE skewed_data (
    id SERIAL PRIMARY KEY,
    value INT
);

-- 插入倾斜数据：80%集中在1-100，20%在100-10000
INSERT INTO skewed_data (value)
SELECT
    CASE
        WHEN random() < 0.8 THEN
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 258** (sql, query):

```sql
-- 查看采样统计
SELECT
    schemaname,
    tablename,
    n_live_tup,                    -- 总行数
    n_mod_since_analyze,           -- 自上次ANALYZE后修改行数
    last_analyze,
    last_autoanalyze
FROM pg_stat_user
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 294** (sql, query):

```sql
-- 大表ANALYZE性能测试
CREATE TABLE huge_table AS
SELECT
    generate_series(1, 100000000) AS id,
    md5(random()::text) AS data,
    (random() * 1000)::int AS value;

-- PostgreSQL 17
\timing on
ANALYZE h
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 322** (sql, query):

```sql
-- Selectivity估算示例
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    age INT,
    city TEXT,
    income NUMERIC(12,2)
);

INSERT INTO customers
SELECT
    generate_series(1, 1000000),

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 386** (sql, query):

```sql
-- 多表JOIN场景
CREATE TABLE orders (order_id INT PRIMARY KEY, customer_id INT, total NUMERIC);
CREATE TABLE customers (customer_id INT PRIMARY KEY, name TEXT);
CREATE TABLE products (product_id INT PRIMA
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 412** (python, loop):

```python
def find_optimal_join_order(tables, statistics):
    # 1. 初始化：单表访问路径
    plans = {}
    for table in tables:
        plans[frozenset([table])] = {
            'cost': estimate_scan_cost(table, statist
```

**建议**:

- 添加循环性能测试

---

**行 488** (sql, query):

```sql
-- 查看当前成本参数
SHOW seq_page_cost;         -- 默认1.0
SHOW random_page_cost;      -- 默认4.0（HDD），SSD建议1.1
SHOW cpu_tuple_cost;        -- 默认0.01
SHOW cpu_index_tuple_cost;  -- 默认0.005
SHOW cpu_operator_cost;
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 565** (python, loop):

```python
def vitter_sampling(table_size, sample_size):
    """
    Vitter算法（单次扫描，等概率采样）
    时间复杂度：O(N)
    空间复杂度：O(sample_size)
    """
    sample = []

    # 阶段1：填充样本
    for i in range(sample_size):

```

**建议**:

- 添加循环性能测试

---

**行 620** (sql, query):

```sql
-- 自动ANALYZE触发条件
/*
触发条件：
(n_tup_ins + n_tup_upd + n_tup_del) >
    autovacuum_analyze_threshold +
    autovacuum_analyze_scale_factor * n_live_tup

默认值：
- autovacuum_analyze_threshold = 50
- autovacu
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 665** (sql, query):

```sql
-- 创建相关列的表
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    department TEXT,
    job_title TEXT,
    salary NUMERIC(10,2)
);

-- 插入相关数据（部门和职位强相关）
INSERT INTO employees (department, job
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 719** (sql, query):

```sql
-- 查看依赖系数
SELECT
    stxname,
    stxkeys,
    stxdependencies
FROM pg_statistic_ext
WHERE stxname = 'dept_title_stats';

/*
stxdependencies:
[
    {"2 => 3": 0.95},  -- job_title依赖于department（95%相关性）
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 745** (sql, query):

```sql
-- 创建倾斜数据
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    status TEXT
);

INSERT INTO orders (status)
SELECT
    CASE
        WHEN random() < 0.7 THEN 'completed'
        WHEN random() < 0.
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 798** (sql, query):

```sql
-- N-Distinct估算算法
/*
PostgreSQL使用HyperLogLog算法估算唯一值数量

n_distinct含义：
- 正数：实际唯一值数量（如1000）
- 负数：唯一值比例（如-0.5表示50%行不同）

示例：
- n_distinct = 5：5个唯一值（status列）
- n_distinct = -1.0：每行都不同（主键）
- n_distinct = -0.
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 846** (sql, query):

```sql
-- default_statistics_target：统计信息详细程度
-- 范围：1-10000，默认100

-- 影响：
-- 1. MCV列表长度：100个值
-- 2. 直方图桶数：100个桶
-- 3. ANALYZE采样行数：300 * statistics_target

-- 场景1：低基数列（如性别：M/F）
ALTER TABLE users ALTER COLUMN g
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 893** (sql, query):

```sql
-- 针对性创建扩展统计
CREATE STATISTICS order_stats (dependencies, mcv, ndistinct)
ON customer_id, product_id, order_date
FROM orders;

ANALYZE orders;

-- 查看扩展统计
SELECT
    stxname,
    stxnamespace::regnames
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 919** (sql, query):

```sql
-- 创建统计信息健康检查视图
CREATE OR REPLACE VIEW stats_health_check AS
SELECT
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    n_mod_since_analyze,
    last_analyze,
    last_autoanalyze,

    -
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 983** (sql, query):

```sql
-- 完整的EXPLAIN选项
EXPLAIN (
    ANALYZE true,       -- 实际执行并显示真实统计
    VERBOSE true,       -- 显示详细输出
    COSTS true,         -- 显示成本估算
    BUFFERS true,       -- 显示缓冲区命中统计
    TIMING true,        -- 显示每
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1055** (sql, query):

```sql
-- 问题：估算严重偏差
EXPLAIN ANALYZE
SELECT * FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'completed'
  AND c.region = 'Beijing';

/*
假设：
- status='completed': 70%行
- regi
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1090** (sql, query):

```sql
-- 表结构变化后统计信息未更新
-- 例如：大批量DELETE后，n_live_tup仍为旧值

-- 检测
SELECT
    relname,
    n_live_tup,           -- pg_stat统计
    (SELECT COUNT(*) FROM orders) AS actual_rows,  -- 实际行数
    last_analyze
FROM pg_s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1164** (sql, query):

```sql
-- 策略1：定期全局ANALYZE（每日凌晨）
-- cron job或pg_cron
SELECT cron.schedule(
    'daily-analyze',
    '0 2 * * *',  -- 每天凌晨2点
    $$
    ANALYZE VERBOSE;
    $$
);

-- 策略2：针对性ANALYZE（高频变更表）
-- 监控n_mod_since_ana
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1207** (sql, query):

```sql
-- 监控仪表板
CREATE OR REPLACE VIEW stats_dashboard AS
WITH stats_age AS (
    SELECT
        schemaname,
        relname,
        n_live_tup,
        n_mod_since_analyze,
        EXTRACT(EPOCH FROM (now(
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1285** (sql, bulk):

```sql
-- 伪造统计信息（用于测试）
-- 警告：仅用于开发/测试环境！

-- 1. 备份真实统计
CREATE TABLE pg_statistic_backup AS
SELECT * FROM pg_statistic
WHERE starelid = 'orders'::regclass;

-- 2. 修改统计信息
UPDATE pg_statistic
SET stanumbers1 =
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

### 17-MERGE命令与RETURNING增强完整指南.md

**行 84** (sql, query):

```sql
-- PostgreSQL 17：MERGE不支持RETURNING
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET value = s.value
WHEN NOT MATCHED THEN
    INSERT (id, value) VALUES (s.id, s.value
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 124** (sql, query):

```sql
-- 创建测试表
CREATE TABLE inventory (
    product_id INT PRIMARY KEY,
    quantity INT,
    last_updated TIMESTAMPTZ DEFAULT now()
);

INSERT INTO inventory VALUES (1, 100), (2, 200), (3, 300);

-- MERGE操
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 173** (sql, query):

```sql
-- 将MERGE结果存储到临时表或传递给后续查询
WITH merge_results AS (
    MERGE INTO target t
    USING source s ON t.id = s.id
    WHEN MATCHED THEN UPDATE SET value = s.value
    WHEN NOT MATCHED THEN INSERT VALUES (s.
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 206** (sql, query):

```sql
MERGE INTO target_table [ [ AS ] target_alias ]
USING source_table [ [ AS ] source_alias ]
ON join_condition

-- 匹配时的操作（可以多个WHEN MATCHED）
[ WHEN MATCHED [ AND condition ] THEN
    { UPDATE SET { colum
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 233** (sql, query):

```sql
-- 案例：库存同步系统
MERGE INTO warehouse_inventory wi
USING daily_transactions dt
    ON wi.product_id = dt.product_id AND wi.warehouse_id = dt.warehouse_id

-- 场景1：匹配且有足够库存 → 更新
WHEN MATCHED AND wi.quantity
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 306** (sql, index):

```sql
-- 1. 创建CDC日志表
CREATE TABLE order_changes (
    change_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    change_type TEXT NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    old_data JSONB,
    n
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 361** (sql, query):

```sql
-- 数据仓库增量更新

-- 源表：OLTP订单表
-- 目标表：OLAP订单事实表

CREATE TABLE fact_orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT,
    order_date DATE,
    total_amount NUMERIC(12,2),
    status TEXT,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 431** (sql, query):

```sql
-- 缓慢变化维度（SCD Type 2）：保留历史版本

-- 目标表：客户维度（历史版本）
CREATE TABLE dim_customer (
    customer_key BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    customer_name TEXT,
    address TEXT,
    phone TE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 513** (sql, query):

```sql
-- 源库 → 目标库实时同步（with conflict resolution）

MERGE INTO target_table t
USING (
    SELECT * FROM source_table
    WHERE updated_at > (
        SELECT COALESCE(MAX(sync_timestamp), '1970-01-01')

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 560** (sql, query):

```sql
-- 场景：100万行UPSERT操作

-- 方案A：INSERT ON CONFLICT
\timing on
INSERT INTO target (id, value)
SELECT id, value FROM source
ON CONFLICT (id) DO UPDATE
    SET value = EXCLUDED.value;
-- Time: 8500.234 ms

-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 601** (sql, query):

```sql
-- 测试：RETURNING对性能的影响

-- 基线：无RETURNING
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET value = s.value
WHEN NOT MATCHED THEN INSERT VALUES (s.id, s.value);
-- Time: 820
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 643** (sql, index):

```sql
-- 通用审计日志表
CREATE TABLE audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    record_id TEXT NOT NULL,  -- 记录主
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 783** (sql, query):

```sql
-- ❌ 反模式：MERGE中使用子查询
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET value = (
        SELECT AVG(value) FROM other_table  -- ❌ 子查询在UPDATE中
        WHERE id = t.id

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 820** (sql, query):

```sql
CREATE TABLE central_inventory (
    sku_id BIGINT PRIMARY KEY,
    quantity INT,
    reserved INT,
    available AS (quantity - reserved) STORED,
    last_updated TIMESTAMPTZ,
    updated_from TEXT,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 882** (sql, query):

```sql
-- 银行流水对账

CREATE TABLE bank_transactions (
    transaction_id BIGINT PRIMARY KEY,
    account_id BIGINT,
    amount NUMERIC(18,2),
    transaction_type TEXT,
    transaction_time TIMESTAMPTZ,
    rec
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 938** (sql, query):

```sql
-- 创建MERGE操作监控视图
CREATE OR REPLACE VIEW merge_performance_stats AS
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,

    -- 识别MERGE操作
    CASE
        WHEN query LIKE 'MERGE INTO%
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 17-窗口函数完整实战.md

**行 7** (sql, query):

```sql
-- 基础语法
function_name() OVER (
    PARTITION BY column1, column2
    ORDER BY column3
    ROWS/RANGE BETWEEN ... AND ...
)

-- 示例
SELECT
    employee_id,
    department,
    salary,
    AVG(salary) OV
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 31** (sql, query):

```sql
CREATE TABLE scores (
    student_id INT,
    subject VARCHAR(50),
    score INT
);

INSERT INTO scores VALUES
(1, 'Math', 95),
(2, 'Math', 95),
(3, 'Math', 90),
(4, 'Math', 85);

SELECT
    student_i
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 68** (sql, query):

```sql
SELECT
    student_id,
    score,
    PERCENT_RANK() OVER (ORDER BY score DESC) AS percent_rank,
    CUME_DIST() OVER (ORDER BY score DESC) AS cumulative_dist,
    NTILE(4) OVER (ORDER BY score DESC)
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 90** (sql, query):

```sql
-- 销售数据
CREATE TABLE daily_sales (
    sale_date DATE,
    amount NUMERIC
);

-- 7日移动平均
SELECT
    sale_date,
    amount,
    AVG(amount) OVER (
        ORDER BY sale_date
        ROWS BETWEEN 6 PRECE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 122** (sql, query):

```sql
-- ROWS: 物理行
ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING      -- 前3行到后3行
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  -- 从开始到当前
ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING  -- 从当前到结束

-- RANGE:
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 148** (sql, query):

```sql
-- 获取前后行数据
SELECT
    sale_date,
    amount,
    LAG(amount) OVER (ORDER BY sale_date) AS prev_day_amount,
    LEAD(amount) OVER (ORDER BY sale_date) AS next_day_amount,
    amount - LAG(amount) OVER
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 170** (sql, query):

```sql
-- 获取窗口内第一个/最后一个值
SELECT
    employee_id,
    department,
    salary,
    FIRST_VALUE(salary) OVER (
        PARTITION BY department
        ORDER BY salary DESC
    ) AS highest_salary_in_dept,
    L
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 192** (sql, query):

```sql
-- 获取第N个值
SELECT
    product_id,
    review_date,
    rating,
    NTH_VALUE(rating, 1) OVER w AS first_rating,
    NTH_VALUE(rating, 2) OVER w AS second_rating,
    NTH_VALUE(rating, 3) OVER w AS thir
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 212** (sql, query):

```sql
-- 每个部门薪资Top 3
WITH ranked AS (
    SELECT
        employee_id,
        name,
        department,
        salary,
        RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
    FROM em
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 230** (sql, query):

```sql
-- 去重，保留每个用户最新记录
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM user_events
)
DELETE FROM user_events
WHERE (user_id, c
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 254** (sql, query):

```sql
-- 销售同比环比分析
SELECT
    sale_date,
    amount,
    -- 环比（Day over Day）
    LAG(amount, 1) OVER (ORDER BY sale_date) AS prev_day,
    amount - LAG(amount, 1) OVER (ORDER BY sale_date) AS dod_change,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 271** (sql, query):

```sql
-- 找出数值跳跃
WITH gaps AS (
    SELECT
        id,
        LAG(id) OVER (ORDER BY id) AS prev_id,
        id - LAG(id) OVER (ORDER BY id) AS gap
    FROM sequential_table
)
SELECT * FROM gaps
WHERE gap >
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 286** (sql, query):

```sql
-- 计算用户连续登录天数
WITH login_groups AS (
    SELECT
        user_id,
        login_date,
        login_date - ROW_NUMBER() OVER (
            PARTITION BY user_id ORDER BY login_date
        )::int AS gro
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 314** (sql, query):

```sql
-- Bad: 重复定义
SELECT
    employee_id,
    AVG(salary) OVER (PARTITION BY department ORDER BY hire_date),
    SUM(salary) OVER (PARTITION BY department ORDER BY hire_date),
    COUNT(*) OVER (PARTITION
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 335** (sql, index):

```sql
-- 如果数据已按某列排序，利用这个顺序
CREATE INDEX idx_sales_date ON daily_sales (sale_date);

-- 查询会利用索引顺序
SELECT
    sale_date,
    amount,
    SUM(amount) OVER (ORDER BY sale_date) AS cumsum
FROM daily_sales;
-- 无需
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 354** (sql, index):

```sql
-- 部分有序数据的窗口函数
CREATE INDEX idx_emp_dept_salary ON employees (department, salary);

SELECT
    employee_id,
    department,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC, h
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 379** (sql, query):

```sql
-- 将用户访问分组为会话（超过30分钟算新会话）
WITH session_starts AS (
    SELECT
        user_id,
        visit_time,
        CASE
            WHEN visit_time - LAG(visit_time) OVER (
                PARTITION BY user_i
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 420** (sql, query):

```sql
-- 转化漏斗
WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_type = 'visit' THEN 1 ELSE 0 END) AS visited,
        MAX(CASE WHEN event_type = 'view_product' THEN 1 ELSE 0 END) AS v
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 18-存储管理与TOAST优化指南.md

**行 123** (sql, query):

```sql
-- 查看页面利用率
CREATE EXTENSION IF NOT EXISTS pageinspect;

SELECT
    *,
    round(100.0 * avg_free_space / pagesize, 2) AS avg_free_pct
FROM (
    SELECT
        avg(lower) AS avg_lower,
        avg(upp
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 169** (sql, query):

```sql
-- 创建测试表
CREATE TABLE mvcc_test (
    id INT PRIMARY KEY,
    value TEXT
);

INSERT INTO mvcc_test VALUES (1, 'version 1');

-- 查看初始tuple
SELECT
    t_ctid,          -- 元组标识符(page, offset)
    t_xmin,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 223** (sql, query):

```sql
-- TOAST触发条件
/*
触发条件：
1. 单行大小超过约2KB（8KB页面的1/4）
2. 列值超过约2KB（变长类型：TEXT, BYTEA, JSONB等）

TOAST策略选择（自动）：
1. 尝试压缩（如果启用压缩策略）
2. 如果压缩后仍>2KB，移到TOAST表
3. 最大单值：1GB（受限于TOAST chunk大小）
*/

-- 查看TOAST配置
SELECT

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 260** (sql, query):

```sql
-- PLAIN：不压缩，不外部存储（定长类型默认）
-- 适用：INT, BIGINT, TIMESTAMP等

-- EXTENDED：先压缩，大于2KB再外部存储（TEXT/JSONB默认）
CREATE TABLE test_extended (
    id SERIAL PRIMARY KEY,
    data TEXT  -- 默认EXTENDED
);
ALTER TABLE t
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 321** (sql, query):

```sql
-- 查看TOAST表
SELECT
    n.nspname AS toast_schema,
    c.relname AS toast_table,
    t.relname AS main_table,
    pg_size_pretty(pg_relation_size(c.oid)) AS toast_size
FROM pg_class c
JOIN pg_namespace
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 364** (sql, query):

```sql
-- 测试不同压缩算法
CREATE TABLE compression_test (
    id SERIAL PRIMARY KEY,
    algorithm TEXT,
    data TEXT
);

-- pglz压缩（传统，PG默认）
ALTER TABLE compression_test ALTER COLUMN data SET COMPRESSION pglz;

IN
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 428** (sql, query):

```sql
-- PostgreSQL 18改进的Page压缩
/*
优化点：
1. 更智能的压缩决策（根据数据类型）
2. 压缩缓存（避免重复解压）
3. 部分解压（仅解压需要的列）
*/

-- 测试：宽表部分列访问
CREATE TABLE wide_table (
    id SERIAL PRIMARY KEY,
    col1 TEXT,
    col2 TEXT,
    col3 TEX
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 530** (sql, query):

```sql
-- 安装Citus
CREATE EXTENSION citus;

-- 创建列式表
CREATE TABLE analytics_data (
    date DATE,
    user_id INT,
    event_type TEXT,
    value NUMERIC
) USING columnar;

-- 插入数据
INSERT INTO analytics_data

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 589** (sql, bulk):

```sql
-- 测试：100万行，不同数据类型的存储大小
CREATE TABLE type_test_int (id INT, value INT);
CREATE TABLE type_test_bigint (id INT, value BIGINT);
CREATE TABLE type_test_numeric (id INT, value NUMERIC(10,2));
CREATE TABLE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 639** (sql, query):

```sql
-- 创建Large Object
SELECT lo_create(0);  -- 返回OID：16789

-- 写入数据（流式）
\lo_import /path/to/large_video.mp4 16789

-- 关联到表
CREATE TABLE videos (
    video_id SERIAL PRIMARY KEY,
    title TEXT,
    video_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 671** (sql, index):

```sql
-- Fillfactor：页面填充因子（默认100%）
/*
fillfactor = 80表示：
- 每个8KB页面仅使用6.4KB（80%）
- 剩余1.6KB（20%）预留给HOT更新

目的：
1. 减少页面分裂
2. 提高HOT更新概率
3. 减少表膨胀
*/

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    cus
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 730** (sql, bulk):

```sql
-- 测试fillfactor对HOT更新的影响
CREATE TABLE hot_test_100 (
    id SERIAL PRIMARY KEY,
    value INT,
    data TEXT
) WITH (fillfactor = 100);  -- 无预留空间

CREATE TABLE hot_test_80 (
    id SERIAL PRIMARY KEY,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试
- 添加批量操作性能测试

---

**行 820** (sql, query):

```sql
-- 创建表膨胀检测函数
CREATE OR REPLACE FUNCTION check_table_bloat(
    p_schema TEXT DEFAULT 'public'
)
RETURNS TABLE (
    schema_name TEXT,
    table_name TEXT,
    actual_size_bytes BIGINT,
    expected_si
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 884** (sql, query):

```sql
-- 策略1：VACUUM（在线，最低影响）
VACUUM VERBOSE orders;
-- 优点：无锁，可在生产运行
-- 缺点：不释放磁盘空间，仅标记空间可重用

-- 策略2：VACUUM FULL（锁表，彻底重建）
VACUUM FULL VERBOSE orders;
-- 优点：完全消除膨胀，释放磁盘空间
-- 缺点：排它锁，停机时间长

-- 策略3：pg_repack（在线重建
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 927** (sql, query):

```sql
-- I/O监控（使用pg_stat_io，PostgreSQL 16+）
SELECT
    backend_type,
    object,
    context,
    reads,
    writes,
    extends,
    op_bytes,
    evictions,
    reuses,
    fsyncs,
    read_time,
    writ
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 964** (sql, query):

```sql
-- HDD配置（传统）
ALTER SYSTEM SET random_page_cost = 4.0;
ALTER SYSTEM SET seq_page_cost = 1.0;
ALTER SYSTEM SET effective_io_concurrency = 2;

-- SSD配置（推荐）
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 985** (sql, query):

```sql
-- 查询计划变化
EXPLAIN (COSTS ON)
SELECT * FROM large_table WHERE id > 1000000;

-- HDD配置：
-- Seq Scan  (cost=0.00..500000.00 rows=...)  ← 顺序扫描

-- SSD配置：
-- Index Scan  (cost=0.42..150000.00 rows=...)  ←
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1000** (sql, query):

```sql
-- 创建表空间（不同存储类型）
-- 1. 高性能表空间（NVMe SSD）
CREATE TABLESPACE fast_storage
LOCATION '/nvme/pgdata';

-- 2. 归档表空间（HDD）
CREATE TABLESPACE archive_storage
LOCATION '/hdd/pgarchive';

-- 3. 临时表空间（SSD）
CREATE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1045** (sql, query):

```sql
-- 完整的存储空间监控视图
CREATE OR REPLACE VIEW storage_monitoring AS
SELECT
    schemaname,
    tablename,

    -- 存储大小
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1089** (sql, query):

```sql
-- TOAST表健康检查
SELECT
    n.nspname AS toast_schema,
    c.relname AS toast_table,
    t.relname AS main_table,

    -- TOAST表大小
    pg_size_pretty(pg_relation_size(c.oid)) AS toast_size,

    -- TOAST
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1123** (sql, query):

```sql
-- 实时表膨胀监控（Prometheus metrics）
CREATE OR REPLACE FUNCTION table_bloat_metrics()
RETURNS TABLE (
    metric_name TEXT,
    metric_value NUMERIC,
    labels TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELEC
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1164** (sql, query):

```sql
-- 容量规划公式
/*
总存储需求 =
    数据大小 +
    索引大小 +
    TOAST大小 +
    WAL大小 +
    临时文件空间 +
    VACUUM工作空间 +
    安全余量

推荐比例：
- 数据：60%
- 索引：20%
- TOAST：10%
- WAL + 临时：5%
- 安全余量：5%

示例：
- 预计数据量：1TB
- 总存储需求：1TB /
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1284** (sql, query):

```sql
-- 性能对比测试（10MB文件）

-- 方案A：TOAST存储
CREATE TABLE docs_toast (
    id SERIAL PRIMARY KEY,
    content TEXT
);

INSERT INTO docs_toast (content)
SELECT repeat('x', 10485760)  -- 10MB
FROM generate_series(
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1356** (sql, query):

```sql
-- PostgreSQL：UPDATE创建新版本
UPDATE orders SET status = 'completed' WHERE id = 1;
-- 结果：
-- - 旧版本保留在heap（死元组）
-- - 新版本写入heap
-- - 需VACUUM清理死元组

-- MySQL InnoDB：UPDATE覆盖
UPDATE orders SET status = 'comple
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 18-并发控制深度解析.md

**行 7** (sql, query):

```sql
-- 查看行版本信息
CREATE EXTENSION IF NOT EXISTS pageinspect;

-- 创建测试表
CREATE TABLE mvcc_test (id INT PRIMARY KEY, value TEXT);
INSERT INTO mvcc_test VALUES (1, 'version 1');

-- 查看页面内容
SELECT * FROM heap_p
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 46** (sql, query):

```sql
-- 事务快照
SELECT
    txid_current() AS current_xid,
    txid_current_snapshot() AS snapshot;

/*
snapshot格式: xmin:xmax:xip_list
100:105:101,103

xmin=100: 最小活跃事务ID
xmax=105: 下一个分配的事务ID
xip_list: 活跃事务列表

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 85** (sql, query):

```sql
-- FOR UPDATE（排他锁）
BEGIN;
SELECT * FROM accounts WHERE account_id = 1 FOR UPDATE;
-- 其他事务无法UPDATE/DELETE/FOR UPDATE这一行
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
COMMIT;

-- FOR
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 131** (sql, query):

```sql
-- 会话1
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
-- 等待...
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;

-- 会话2
BEGIN;
UPDATE accounts SET balance =
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 195** (sql, query):

```sql
-- 添加version列
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    balance NUMERIC NOT NULL,
    version INT NOT NULL DEFAULT 0
);

-- 乐观锁更新
UPDATE accounts
SET
    balance = balance - 100,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 220** (python, loop):

```python
def optimistic_lock_update(conn, account_id, amount, max_retries=5):
    """乐观锁更新（带重试）"""

    for attempt in range(max_retries):
        cursor = conn.cursor()

        # 读取当前版本
        cursor.execut
```

**建议**:

- 添加数据库操作性能测试
- 添加循环性能测试

---

**行 266** (sql, query):

```sql
-- 查看锁等待
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 297** (sql, query):

```sql
-- 终止阻塞会话
SELECT pg_cancel_backend(blocking_pid);   -- 温和取消
SELECT pg_terminate_backend(blocking_pid); -- 强制终止

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 309** (sql, query):

```sql
-- 任务队列
CREATE TABLE task_queue (
    task_id BIGSERIAL PRIMARY KEY,
    task_data JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Worker获取任务（无锁竞争）
BEG
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 19-分区表增强与智能裁剪指南.md

**行 137** (sql, query):

```sql
-- 创建分区表（按月分区，100个分区）
CREATE TABLE orders (
    order_id BIGINT,
    customer_id INT,
    order_date DATE NOT NULL,
    total_amount NUMERIC(12,2),
    status TEXT
) PARTITION BY RANGE (order_date);


```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 225** (sql, query):

```sql
-- 案例1：函数表达式裁剪
SELECT * FROM orders
WHERE EXTRACT(YEAR FROM order_date) = 2024  -- PostgreSQL 18可裁剪
  AND EXTRACT(MONTH FROM order_date) = 6;

-- PostgreSQL 17: 无法裁剪，扫描所有分区
-- PostgreSQL 18: 裁剪到orders
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 257** (sql, query):

```sql
-- 创建测试函数
CREATE OR REPLACE FUNCTION get_month_range(year INT, month INT)
RETURNS DATERANGE AS $$
BEGIN
    RETURN daterange(
        make_date(year, month, 1),
        make_date(year, month, 1) + INT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 289** (sql, query):

```sql
-- 多列Range分区
CREATE TABLE sales (
    sale_id BIGINT,
    region_id INT,
    sale_date DATE,
    amount NUMERIC(12,2)
) PARTITION BY RANGE (region_id, sale_date);

-- 创建分区（区域 + 日期）
CREATE TABLE sales_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 372** (sql, query):

```sql
-- 第一级：年分区
CREATE TABLE logs (
    log_id BIGSERIAL,
    log_time TIMESTAMPTZ NOT NULL,
    region TEXT NOT NULL,
    level TEXT,
    message TEXT
) PARTITION BY RANGE (log_time);

CREATE TABLE logs_2
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 413** (sql, query):

```sql
-- 测试查询：精确到具体分区
EXPLAIN (ANALYZE, COSTS OFF)
SELECT COUNT(*) FROM logs
WHERE log_time >= '2024-01-15 10:00:00'
  AND log_time < '2024-01-15 11:00:00'
  AND region = '华北';

/*
PostgreSQL 18:
  Aggregat
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 500** (sql, query):

```sql
-- 创建分区表1：订单
CREATE TABLE orders_partitioned (
    order_id BIGINT,
    order_date DATE NOT NULL,
    customer_id INT,
    total_amount NUMERIC(12,2)
) PARTITION BY RANGE (order_date);

-- 创建分区表2：订单明细
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 645** (sql, query):

```sql
-- 创建自动分区管理函数
CREATE OR REPLACE FUNCTION create_partitions_for_next_months(
    p_table_name TEXT,
    p_months_ahead INT DEFAULT 3
)
RETURNS TEXT AS $$
DECLARE
    v_start_date DATE;
    v_end_date D
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 714** (sql, bulk):

```sql
-- 分区归档函数（移动到归档表）
CREATE OR REPLACE FUNCTION archive_old_partitions(
    p_table_name TEXT,
    p_months_old INT DEFAULT 12
)
RETURNS TEXT AS $$
DECLARE
    v_partition_record RECORD;
    v_archive_ta
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 803** (sql, query):

```sql
-- 场景1：单分区查询
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE order_date = '2024-06-15';

/*
PostgreSQL 17:
  Planning Time: 45.234 ms  (扫描1000个分区元数据)
  Execution Time: 125.456 ms

PostgreSQL 18:
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 901** (sql, query):

```sql
-- 分区大小评估函数
CREATE OR REPLACE FUNCTION evaluate_partition_size(
    p_table_name TEXT,
    p_row_count BIGINT,
    p_partition_count INT
)
RETURNS TABLE (
    partition_strategy TEXT,
    avg_partitio
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 971** (sql, index):

```sql
-- 主表：按天分区
CREATE TABLE orders (
    order_id BIGINT,
    user_id BIGINT,
    order_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    status TEXT,
    total_amount NUMERIC(12,2)
) PARTITION
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 1031** (sql, query):

```sql
-- 多级分区：日期 → 设备哈希
CREATE TABLE sensor_data (
    device_id BIGINT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature NUMERIC(5,2),
    humidity NUMERIC(5,2),
    pressure NUMERIC(7,2)
) PAR
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1091** (sql, query):

```sql
-- 分区统计视图
CREATE OR REPLACE VIEW partition_health_stats AS
WITH partition_info AS (
    SELECT
        nmsp_parent.nspname AS schema_name,
        parent.relname AS table_name,
        child.relname A
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1137** (sql, query):

```sql
-- 分区查询统计
SELECT
    schemaname,
    tablename,

    -- 扫描统计
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,

    -- 缓存命中率
    ROUND(
        CASE
            WHEN (heap_blks_hit + he
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 19-高级SQL查询技巧.md

**行 7** (sql, query):

```sql
-- 员工表（树形结构）
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT REFERENCES employees(emp_id),
    department VARCHAR(50)
);

-- 查询某人的所有下属（递归）
WITH RECURSIVE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 50** (sql, query):

```sql
-- 社交网络好友关系
CREATE TABLE friendships (
    user_id INT,
    friend_id INT,
    PRIMARY KEY (user_id, friend_id)
);

-- 查找N度好友
WITH RECURSIVE friend_network AS (
    -- 1度好友
    SELECT friend_id AS use
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 81** (sql, query):

```sql
-- 生成日期序列
WITH RECURSIVE dates AS (
    SELECT '2024-01-01'::DATE AS date
    UNION ALL
    SELECT date + 1
    FROM dates
    WHERE date < '2024-12-31'
)
SELECT date FROM dates;

-- 或使用generate_serie
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 106** (sql, query):

```sql
-- 计算每日及其前7天的移动平均
SELECT
    sale_date,
    amount,
    AVG(amount) OVER (
        ORDER BY sale_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS ma_7d,
    -- 加权移动平均
    SUM(amount * (R
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 126** (sql, query):

```sql
-- 计算连续上涨天数
WITH price_changes AS (
    SELECT
        date,
        price,
        price > LAG(price) OVER (ORDER BY date) AS is_up
    FROM stock_prices
),
groups AS (
    SELECT
        date,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 159** (sql, query):

```sql
-- 每个用户的最近3个订单
-- Bad: 慢
SELECT u.user_id, u.username, o.*
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.order_id IN (
    SELECT order_id FROM orders
    WHERE user_id = u.user_id
    O
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 187** (sql, query):

```sql
-- 每个类别销量Top 5
SELECT c.category_name, p.*
FROM categories c
CROSS JOIN LATERAL (
    SELECT * FROM products
    WHERE category_id = c.category_id
    ORDER BY sales_count DESC
    LIMIT 5
) p;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 205** (sql, query):

```sql
-- 每个用户最新登录记录
SELECT DISTINCT ON (user_id)
    user_id,
    login_time,
    ip_address
FROM login_history
ORDER BY user_id, login_time DESC;

-- 等价于（但更高效）
SELECT user_id, login_time, ip_address
FROM (
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 230** (sql, query):

```sql
-- 聚合为数组
SELECT
    department,
    array_agg(name ORDER BY salary DESC) AS employees,
    array_agg(salary ORDER BY salary DESC) AS salaries
FROM employees
GROUP BY department;

-- 数组展开+编号
SELECT

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 249** (sql, query):

```sql
-- 数组操作
SELECT
    ARRAY[1,2,3,4] && ARRAY[3,4,5,6] AS has_overlap,      -- true
    ARRAY[1,2,3,4] @> ARRAY[2,3] AS contains,             -- true
    ARRAY[1,2,3] || ARRAY[4,5] AS concatenate,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 265** (sql, query):

```sql
-- 分组统计不同条件
SELECT
    department,
    COUNT(*) AS total_employees,
    COUNT(*) FILTER (WHERE salary > 100000) AS high_earners,
    COUNT(*) FILTER (WHERE hire_date > '2023-01-01') AS new_hires,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 292** (sql, query):

```sql
-- 按不同维度组合汇总
SELECT
    region,
    product_category,
    DATE_TRUNC('month', sale_date) AS month,
    SUM(amount) AS total_sales
FROM sales
GROUP BY GROUPING SETS (
    (region, product_category, mon
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 337** (sql, query):

```sql
-- jsonb_path_query
SELECT jsonb_path_query(
    '{"items":[
        {"name":"item1","price":100,"stock":50},
        {"name":"item2","price":200,"stock":30}
    ]}',
    '$.items[*] ? (@.price > 150
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 358** (sql, query):

```sql
-- jsonb_to_recordset
SELECT * FROM jsonb_to_recordset('[
    {"name":"Alice","age":30},
    {"name":"Bob","age":25}
]') AS (name TEXT, age INT);

-- jsonb_populate_recordset
CREATE TYPE person AS (na
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 380** (sql, query):

```sql
-- 复杂分类
SELECT
    product_id,
    price,
    CASE
        WHEN price < 10 THEN 'Budget'
        WHEN price < 50 THEN 'Standard'
        WHEN price < 200 THEN 'Premium'
        ELSE 'Luxury'
    END A
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 402** (sql, query):

```sql
-- COALESCE: 返回第一个非NULL值
SELECT
    name,
    COALESCE(mobile_phone, home_phone, work_phone, 'No phone') AS contact_phone
FROM users;

-- NULLIF: 如果相等返回NULL
SELECT
    product_id,
    price,
    disco
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 431** (sql, query):

```sql
-- INSERT ... ON CONFLICT
INSERT INTO inventory (product_id, stock)
VALUES
    (1, 100),
    (2, 200),
    (3, 300)
ON CONFLICT (product_id)
DO UPDATE SET
    stock = inventory.stock + EXCLUDED.stock,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 456** (sql, query):

```sql
-- 检查多个值是否存在
SELECT value, EXISTS(SELECT 1 FROM table WHERE id = value) AS exists
FROM unnest(ARRAY[1,2,3,4,5]) AS value;

-- 或使用LEFT JOIN
SELECT v.value, t.id IS NOT NULL AS exists
FROM unnest(ARRAY[
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 473** (sql, query):

```sql
-- 计算百分位
SELECT
    percentile_cont(0.5) WITHIN GROUP (ORDER BY salary) AS median,
    percentile_cont(0.25) WITHIN GROUP (ORDER BY salary) AS q1,
    percentile_cont(0.75) WITHIN GROUP (ORDER BY sala
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 491** (sql, query):

```sql
-- 创建直方图
WITH bins AS (
    SELECT
        width_bucket(price, 0, 1000, 10) AS bin,
        COUNT(*) AS count
    FROM products
    WHERE price BETWEEN 0 AND 1000
    GROUP BY bin
)
SELECT
    bin,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 517** (sql, query):

```sql
-- 匹配
SELECT email FROM users WHERE email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';

-- 提取
SELECT
    email,
    (regexp_match(email, '@([A-Za-z0-9.-]+)'))[1] AS domain
FROM users;

-- 替换

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 547** (sql, query):

```sql
-- string_agg: 聚合为字符串
SELECT
    department,
    string_agg(name, ', ' ORDER BY name) AS employees
FROM employees
GROUP BY department;

-- array_to_string
SELECT array_to_string(ARRAY['a','b','c'], '-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 566** (sql, query):

```sql
-- 按小时分组
SELECT
    date_trunc('hour', timestamp) AS hour,
    COUNT(*) AS request_count,
    AVG(response_time) AS avg_response
FROM api_logs
WHERE timestamp > now() - INTERVAL '24 hours'
GROUP BY ho
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 596** (sql, query):

```sql
-- 生成完整时间序列（填充缺失）
WITH time_series AS (
    SELECT generate_series(
        '2024-01-01'::TIMESTAMP,
        '2024-01-31'::TIMESTAMP,
        '1 hour'::INTERVAL
    ) AS hour
)
SELECT
    ts.hour,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 619** (sql, query):

```sql
-- crosstab（需要tablefunc扩展）
CREATE EXTENSION IF NOT EXISTS tablefunc;

-- 原始数据
SELECT * FROM sales;
/*
 region  | product | amount
---------+---------+--------
 East    | A       | 100
 East    | B
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 661** (sql, query):

```sql
-- 查找高于部门平均薪资的员工
SELECT e.name, e.department, e.salary
FROM employees e
WHERE e.salary > (
    SELECT AVG(salary)
    FROM employees
    WHERE department = e.department
);

-- 优化为窗口函数
SELECT name, dep
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 686** (sql, query):

```sql
-- ANY: 满足任一条件
SELECT * FROM products
WHERE price > ANY(SELECT AVG(price) FROM products GROUP BY category);

-- ALL: 满足所有条件
SELECT * FROM products
WHERE price > ALL(SELECT price FROM products WHERE ca
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 706** (sql, query):

```sql
CREATE OR REPLACE FUNCTION dynamic_count(table_name TEXT, condition TEXT)
RETURNS BIGINT AS $$
DECLARE
    result BIGINT;
BEGIN
    EXECUTE format('SELECT COUNT(*) FROM %I WHERE %s', table_name, condi
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 725** (sql, query):

```sql
-- 根据参数选择列
CREATE OR REPLACE FUNCTION flexible_query(
    columns TEXT[],
    table_name TEXT,
    where_clause TEXT
) RETURNS TABLE(result JSONB) AS $$
BEGIN
    RETURN QUERY EXECUTE format(

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 20-全文检索与排序规则变更指南.md

**行 128** (sql, query):

```sql
-- 检测需要重建的全文检索索引
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,

    -- 估算重建时间（基于索引大小）
    CASE
        WHEN pg_relation_size(inde
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 163** (sql, query):

```sql
-- 创建测试表
CREATE TABLE collation_test (
    id SERIAL PRIMARY KEY,
    text_data TEXT
);

-- 插入100万行测试数据
INSERT INTO collation_test (text_data)
SELECT md5(random()::text)
FROM generate_series(1, 100000
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 214** (sql, query):

```sql
-- PostgreSQL 18新增：casefold()函数
-- 用于大小写不敏感比较

-- 问题场景：德语ß字符
SELECT
    'straße'::text = 'STRASSE'::text AS traditional_compare,
    lower('STRASSE') = 'straße' AS lower_compare,
    casefold('STRASSE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 237** (sql, index):

```sql
-- 创建大小写不敏感索引
CREATE INDEX idx_users_email_casefold
ON users (casefold(email));

-- 大小写不敏感查询
SELECT * FROM users
WHERE casefold(email) = casefold('Alice@Example.COM');
-- 可以匹配 'alice@example.com', 'AL
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 291** (sql, index):

```sql
-- 策略1：在线重建（推荐，无停机）
-- 使用CONCURRENTLY避免锁表

-- 查看现有索引定义
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'articles'
  AND indexdef LIKE '%tsvector%';

-- 示例输出：
-- indexname: idx_articles_ft
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 396** (sql, query):

```sql
-- 估算索引重建时间（基于表大小和索引配置）
WITH index_estimates AS (
    SELECT
        schemaname,
        tablename,
        indexname,
        pg_relation_size(indexrelid) AS index_size,
        pg_relation_size(tabl
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 435** (sql, query):

```sql
-- 查找所有pg_trgm索引
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size,
    idx_scan AS scans,
    idx_tup_read AS tuples_read,


```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 461** (sql, index):

```sql
-- 示例：用户表的模糊搜索索引
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 原索引
CREATE INDEX idx_users_name_trgm
ON users USING gin (name gin_trgm_ops);

-- pg_upgrade后重建
REINDEX INDEX CONCURRENTLY idx_users_name_tr
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 484** (sql, query):

```sql
-- PostgreSQL 17：LIKE不支持非确定性排序
CREATE COLLATION case_insensitive (
    provider = icu,
    locale = 'und-u-ks-level2',
    deterministic = false
);

CREATE TABLE test_like (
    name TEXT COLLATE case
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 508** (sql, index):

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT
);

INSERT INTO articles (title, content)
SELECT
    'Article ' || generate_series,
    md5(random()::text)
FROM gen
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 548** (sql, query):

```sql
-- 基准测试：字符串大小写转换

-- 创建测试表（多语言文本）
CREATE TABLE text_processing_test (
    id SERIAL PRIMARY KEY,
    english TEXT,
    chinese TEXT,
    japanese TEXT,
    arabic TEXT,
    mixed TEXT
);

-- 插入10万行
IN
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 589** (sql, index):

```sql
-- 测试：100万文档全文检索

CREATE TABLE documents (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    content_tsvector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
)
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 860** (sql, index):

```sql
-- 1. 升级前准备（周五晚）
-- 估算重建时间：18GB * 8min/GB = 144分钟

-- 2. 执行pg_upgrade（凌晨2点）
-- 耗时：45分钟

-- 3. 重建索引（凌晨2:45）
REINDEX INDEX CONCURRENTLY idx_products_fts;
-- 实际耗时：182分钟（超出预估）

-- 4. 问题：凌晨5点用户开始访问，索引未完成
-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 891** (sql, index):

```sql
-- PG17: 使用默认排序规则
CREATE INDEX idx_posts_zh_fts ON posts
USING gin (to_tsvector('zh_cn', content));

-- pg_upgrade后未重建，索引损坏

-- 解决：
REINDEX INDEX idx_posts_zh_fts;

-- 验证
SELECT * FROM posts
WHERE to_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

### 20-实用SQL模式集锦.md

**行 7** (sql, query):

```sql
-- 方法1: DELETE + ROW_NUMBER
DELETE FROM user_events
WHERE ctid NOT IN (
    SELECT ctid FROM (
        SELECT ctid,
               ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 44** (sql, query):

```sql
-- 账户余额计算
WITH transactions AS (
    SELECT
        transaction_id,
        account_id,
        amount,
        transaction_date,
        SUM(amount) OVER (
            PARTITION BY account_id

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 65** (sql, query):

```sql
-- 用户留存分析
WITH user_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', register_date) AS cohort_month,
        DATE_TRUNC('month', activity_date) AS activity_month
    FROM user_acti
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 98** (sql, query):

```sql
-- 查找订单号间隙
WITH gaps AS (
    SELECT
        order_id,
        LEAD(order_id) OVER (ORDER BY order_id) AS next_id,
        LEAD(order_id) OVER (ORDER BY order_id) - order_id AS gap_size
    FROM order
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 136** (sql, query):

```sql
-- 游戏排行榜
CREATE TABLE player_scores (
    player_id BIGINT,
    game_id INT,
    score BIGINT,
    achieved_at TIMESTAMPTZ,
    PRIMARY KEY (player_id, game_id)
);

-- Top 100排行榜（带并列处理）
SELECT
    pla
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 189** (sql, query):

```sql
-- 避免长事务和锁
DO $$
DECLARE
    deleted INT;
BEGIN
    LOOP
        DELETE FROM logs
        WHERE created_at < CURRENT_DATE - INTERVAL '90 days'
          AND ctid = ANY(
              ARRAY(

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 222** (sql, query):

```sql
CREATE OR REPLACE FUNCTION batch_update_with_progress()
RETURNS VOID AS $$
DECLARE
    batch_size INT := 10000;
    total_rows BIGINT;
    updated BIGINT := 0;
    batch_updated INT;
BEGIN
    SELECT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 271** (sql, query):

```sql
-- 销售同比环比
WITH daily_sales AS (
    SELECT
        DATE(order_date) AS sale_date,
        SUM(amount) AS daily_amount
    FROM orders
    GROUP BY DATE(order_date)
)
SELECT
    sale_date,
    daily_am
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 299** (sql, query):

```sql
-- 移动平均+趋势
WITH ma AS (
    SELECT
        date,
        value,
        AVG(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7d,
        AVG(value) OVER (ORDER BY date ROWS B
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 329** (sql, query):

```sql
-- 清洗用户数据
UPDATE users
SET
    email = LOWER(TRIM(email)),
    phone = regexp_replace(phone, '[^0-9]', '', 'g'),
    name = INITCAP(TRIM(name))
WHERE
    email != LOWER(TRIM(email))
    OR phone != re
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 344** (sql, query):

```sql
-- 识别并处理异常值（3σ原则）
WITH stats AS (
    SELECT
        AVG(price) AS mean,
        STDDEV(price) AS stddev
    FROM products
),
outliers AS (
    SELECT
        product_id,
        price,
        (price
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 371** (sql, index):

```sql
-- 传统OFFSET分页（慢）
SELECT * FROM products
ORDER BY product_id
LIMIT 20 OFFSET 10000;  -- 扫描10020行

-- Keyset分页（快）
SELECT * FROM products
WHERE product_id > 10000  -- 上一页最后的ID
ORDER BY product_id
LIMIT 2
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 399** (sql, query):

```sql
CREATE TABLE audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    record_id TEXT,
    old_values JSONB,
    new_values JSONB,
    changed_fiel
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 459** (sql, query):

```sql
-- 汇总缓存表
CREATE TABLE user_stats_cache (
    user_id BIGINT PRIMARY KEY,
    order_count INT,
    total_spent NUMERIC,
    last_order_at TIMESTAMPTZ,
    cache_updated_at TIMESTAMPTZ DEFAULT now()
);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 511** (sql, query):

```sql
-- 当前版本表
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name VARCHAR(200),
    price NUMERIC(10,2),
    version INT DEFAULT 1,
    valid_from TIMESTAMPTZ DEFAULT now(),
    valid_to TIMES
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 577** (sql, index):

```sql
-- 任务表
CREATE TABLE task_queue (
    task_id BIGSERIAL PRIMARY KEY,
    task_type VARCHAR(50),
    payload JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    priority INT DEFAULT 0,
    retry_count
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 652** (sql, query):

```sql
-- 多字段加权搜索
SELECT
    doc_id,
    title,
    ts_rank_cd(
        setweight(to_tsvector('english', title), 'A') ||
        setweight(to_tsvector('english', content), 'B') ||
        setweight(to_tsvect
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 680** (sql, query):

```sql
-- 预计算每日汇总（物化视图）
CREATE MATERIALIZED VIEW daily_stats AS
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    COUNT(DIS
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 21-SQL优化50条军规.md

**行 7** (sql, index):

```sql
-- ✓ B-Tree: 等值/范围查询
CREATE INDEX ON users(email);

-- ✓ Hash: 纯等值查询（少用）
CREATE INDEX ON users USING hash(email);

-- ✓ GIN: 全文搜索、JSONB、数组
CREATE INDEX ON documents USING GIN(content);

-- ✓ BRIN: 时序数
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 26** (sql, index):

```sql
-- ✗ 需要回表
CREATE INDEX ON orders(user_id);
SELECT order_id, amount FROM orders WHERE user_id = 123;

-- ✓ 覆盖索引，无需回表
CREATE INDEX ON orders(user_id, order_id, amount);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 37** (sql, index):

```sql
-- ✗ 索引所有行
CREATE INDEX ON users(status);

-- ✓ 只索引活跃用户
CREATE INDEX ON users(status) WHERE status = 'active';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 47** (sql, index):

```sql
-- ✗ 无法使用索引
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- ✓ 表达式索引
CREATE INDEX ON users(LOWER(email));

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 57** (sql, index):

```sql
-- ✗ 冗余
CREATE INDEX ON orders(user_id);
CREATE INDEX ON orders(user_id, created_at);  -- 第一个索引多余

-- ✓ 只创建第二个
DROP INDEX orders_user_id_idx;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 72** (sql, query):

```sql
-- ✗ 传输不需要的数据
SELECT * FROM users WHERE user_id = 123;

-- ✓ 只选择需要的列
SELECT user_id, username, email FROM users WHERE user_id = 123;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 82** (sql, query):

```sql
-- ✗ 子查询返回大量数据
SELECT * FROM users WHERE user_id IN (SELECT user_id FROM orders);

-- ✓ 使用EXISTS（短路评估）
SELECT * FROM users u WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.user_id
);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 94** (sql, query):

```sql
-- ✗ OR导致无法使用索引
SELECT * FROM users WHERE email = 'a@x.com' OR username = 'alice';

-- ✓ UNION使用两个索引
SELECT * FROM users WHERE email = 'a@x.com'
UNION
SELECT * FROM users WHERE username = 'alice';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 106** (sql, query):

```sql
-- ✗ 先JOIN再LIMIT
SELECT o.* FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE u.status = 'vip'
ORDER BY o.created_at DESC
LIMIT 10;

-- ✓ 先LIMIT再JOIN（如果可能）
SELECT o.* FROM (
    SELECT * FROM
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 125** (sql, query):

```sql
-- ✗ 子查询多次执行
SELECT * FROM users WHERE user_id IN (
    SELECT user_id FROM orders WHERE amount > 1000
);

-- ✓ JOIN一次完成
SELECT DISTINCT u.* FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 139** (sql, query):

```sql
-- ✗ 逐条插入
INSERT INTO logs (message) VALUES ('log1');
INSERT INTO logs (message) VALUES ('log2');

-- ✓ 批量插入
INSERT INTO logs (message) VALUES ('log1'), ('log2'), ('log3');

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 150** (sql, bulk):

```sql
-- ✗ INSERT慢
INSERT INTO large_table SELECT * FROM source;

-- ✓ COPY最快
COPY large_table FROM '/tmp/data.csv' WITH (FORMAT csv);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 160** (sql, query):

```sql
-- ✗ 无法使用索引
SELECT * FROM users WHERE YEAR(created_at) = 2024;

-- ✓ 范围查询
SELECT * FROM users
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 171** (sql, query):

```sql
-- ✗ CTE被物化
WITH large_cte AS (
    SELECT * FROM huge_table WHERE ...
)
SELECT * FROM large_cte WHERE extra_filter;

-- ✓ 使用NOT MATERIALIZED
WITH large_cte AS NOT MATERIALIZED (
    SELECT * FROM hug
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 187** (sql, query):

```sql
-- 分区表
CREATE TABLE logs (...) PARTITION BY RANGE (created_at);

-- ✓ 查询包含分区键
SELECT * FROM logs WHERE created_at >= '2024-01-01';
-- 只扫描相关分区

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 202** (sql, query):

```sql
-- ✗ 长事务
BEGIN;
SELECT * FROM large_table;  -- 1000万行
-- 处理数据...（5分钟）
COMMIT;

-- ✓ 游标分批处理
BEGIN;
DECLARE cur CURSOR FOR SELECT * FROM large_table;
FETCH 1000 FROM cur;
-- 处理1000行
COMMIT;
-- 重复

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 220** (sql, query):

```sql
-- ✗ 过度使用SERIALIZABLE
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT * FROM products;  -- 只读查询
COMMIT;

-- ✓ 使用READ COMMITTED
BEGIN;  -- 默认READ COMMITTED
SELECT * FROM products;
COMMIT;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 234** (python, database):

```python
# ✗ 事务后空闲
conn.cursor().execute("BEGIN")
result = conn.cursor().execute("SELECT * FROM users WHERE id=1")
# 处理结果...（忘记commit）
time.sleep(60)

# ✓ 及时提交
cursor.execute("BEGIN")
result = cursor.execute("
```

**建议**:

- 添加数据库操作性能测试

---

**行 253** (python, database):

```python
# ✗ 每次新建连接
conn = psycopg2.connect(...)
cursor = conn.cursor()
cursor.execute("SELECT ...")
conn.close()

# ✓ 使用连接池
conn = connection_pool.getconn()
try:
    cursor = conn.cursor()
    cursor.execute(
```

**建议**:

- 添加数据库操作性能测试

---

**行 271** (python, database):

```python
# ✓ 预编译（降低解析开销）
cursor.execute("PREPARE stmt AS SELECT * FROM users WHERE user_id = $1")
cursor.execute("EXECUTE stmt (123)")
cursor.execute("EXECUTE stmt (456)")

```

**建议**:

- 添加数据库操作性能测试

---

**行 284** (sql, query):

```sql
-- ✗ 过大类型
CREATE TABLE products (
    product_id BIGINT,  -- 实际只有1万条
    stock BIGINT        -- 最大1000
);

-- ✓ 合适类型
CREATE TABLE products (
    product_id INT,
    stock SMALLINT
);
-- 节省50%空间

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 301** (sql, query):

```sql
-- ✗ VARCHAR
CREATE TABLE orders (status VARCHAR(20));

-- ✓ ENUM（4字节 vs 变长）
CREATE TYPE order_status AS ENUM ('pending','paid','shipped');
CREATE TABLE orders (status order_status);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 312** (sql, query):

```sql
-- ✓ 使用TEXT（无性能差异）
CREATE TABLE docs (content TEXT);

-- 不要使用VARCHAR(无明确长度需求时)

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 362** (sql, query):

```sql
-- ✓ 定期执行
VACUUM ANALYZE users;

-- ✓ 配置autovacuum
ALTER SYSTEM SET autovacuum_naptime = '1min';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 372** (sql, query):

```sql
-- ✓ 高频更新表更激进
ALTER TABLE hot_table SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 21-云原生部署与配置优化指南.md

**行 755** (sql, query):

```sql
-- 创建性能测试表
CREATE TABLE numa_test (
    id BIGSERIAL PRIMARY KEY,
    data TEXT
);

INSERT INTO numa_test (data)
SELECT md5(random()::TEXT)
FROM generate_series(1, 100000000);

VACUUM ANALYZE numa_tes
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 895** (sql, query):

```sql
-- 阿里云RDS PostgreSQL 18参数优化

-- 1. AIO配置
ALTER SYSTEM SET io_method = 'worker';  -- 阿里云推荐
ALTER SYSTEM SET effective_io_concurrency = 48;
ALTER SYSTEM SET maintenance_io_concurrency = 48;

-- 2. ESSD性
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 22-TimescaleDB时序数据库完整指南.md

**行 55** (sql, query):

```sql
-- 创建普通表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INT NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    pressure FLOAT
);

-- 转换为Hypertable
SELECT create_hypertab
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 77** (sql, query):

```sql
-- 高频插入
INSERT INTO sensor_data (time, sensor_id, temperature, humidity, pressure)
VALUES
    (now(), 1, 23.5, 65.2, 1013.2),
    (now(), 2, 24.1, 62.8, 1012.8),
    (now(), 3, 22.9, 67.5, 1014.1);

-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 104** (sql, query):

```sql
-- 查询最近1小时
EXPLAIN ANALYZE
SELECT * FROM sensor_data
WHERE time > now() - INTERVAL '1 hour';

/*
Append (cost=...)
  ->  Seq Scan on _hyper_1_10_chunk  ← 只扫描相关chunk
  ->  Seq Scan on _hyper_1_11_chunk
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 135** (sql, query):

```sql
-- 创建1分钟聚合
CREATE MATERIALIZED VIEW sensor_data_1min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS bucket,
    sensor_id,
    AVG(temperature) AS avg_temp,
    MAX(tempe
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 180** (sql, query):

```sql
-- 启用压缩
ALTER TABLE sensor_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- 自动压缩策略（7天后压缩）
SELECT add_compres
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 212** (sql, query):

```sql
-- 保留365天数据
SELECT add_retention_policy('sensor_data', INTERVAL '365 days');

-- 查看策略
SELECT * FROM timescaledb_information.jobs;

-- 手动删除chunk
SELECT drop_chunks('sensor_data', INTERVAL '400 days');

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 239** (sql, query):

```sql
-- time_bucket: 灵活的时间分组
SELECT
    time_bucket('5 minutes', time) AS bucket,
    sensor_id,
    AVG(temperature) AS avg_temp
FROM sensor_data
WHERE time > now() - INTERVAL '1 hour'
GROUP BY bucket, se
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 272** (sql, query):

```sql
-- first/last聚合（时序专用）
SELECT
    sensor_id,
    first(temperature, time) AS first_reading,
    last(temperature, time) AS last_reading,
    last(time, time) AS last_time
FROM sensor_data
WHERE time >
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 306** (python, loop):

```python
from psycopg2.extras import execute_values

def bulk_insert_timeseries(conn, data, batch_size=10000):
    """高性能批量插入"""

    cursor = conn.cursor()

    for i in range(0, len(data), batch_size):

```

**建议**:

- 添加循环性能测试

---

**行 329** (sql, query):

```sql
-- 时间+空间分区（高效）
SELECT create_hypertable(
    'sensor_data',
    'time',
    partitioning_column => 'sensor_id',
    number_partitions => 8
);

-- 查询单个sensor（只扫描1/8的chunk）
SELECT * FROM sensor_data
WHE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 350** (sql, index):

```sql
-- Schema设计
CREATE TABLE device_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    tags JSONB
);

SELECT create_hy
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 418** (sql, query):

```sql
SET max_parallel_workers_per_gather = 8;

-- 大范围聚合
SELECT
    time_bucket('1 day', time) AS day,
    AVG(temperature) AS avg_temp
FROM sensor_data
WHERE time > '2023-01-01'
GROUP BY day;

-- 自动并行扫描多个c
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 22-监控与可观测性完整体系指南.md

**行 216** (python, loop):

```python
#!/usr/bin/env python3
"""
PostgreSQL 18 JSON日志解析器
功能：解析、过滤、聚合、告警
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

class PG1
```

**建议**:

- 添加循环性能测试

---

**行 423** (sql, query):

```sql
-- 查看pg_stat_io结构（PostgreSQL 18）
\d pg_stat_io

-- 核心字段
SELECT
    backend_type,
    object,
    context,

    -- ✅ 新增字节级统计
    reads,
    read_time,
    read_bytes,  -- 新增：读取字节数

    writes,
    writ
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 461** (sql, query):

```sql
-- 创建I/O性能分析视图
CREATE OR REPLACE VIEW io_performance_analysis AS
SELECT
    backend_type,
    object,
    context,

    -- 读性能
    reads AS read_operations,
    pg_size_pretty(read_bytes) AS read_data
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 533** (sql, query):

```sql
-- I/O热点表识别
SELECT
    schemaname,
    tablename,

    -- 堆表I/O
    heap_blks_read,
    heap_blks_hit,
    ROUND(heap_blks_hit * 100.0 / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) AS heap_hit_ratio
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 616** (sql, bulk):

```sql
-- 从JSON日志中提取连接性能统计
-- （需要先导入日志到临时表）

CREATE TEMP TABLE connection_logs (
    log_time TIMESTAMPTZ,
    session_id TEXT,
    remote_host TEXT,
    user_name TEXT,
    database_name TEXT,
    setup_dur
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 677** (sql, query):

```sql
-- 识别慢连接
SELECT
    log_time,
    session_id,
    remote_host,
    user_name,
    database_name,
    setup_duration_ms,
    fork_duration_ms,
    auth_duration_ms,

    -- 标识瓶颈阶段
    CASE
        WHEN
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 711** (sql, query):

```sql
-- 生成优化建议
WITH connection_perf AS (
    SELECT
        AVG(setup_duration_ms) AS avg_setup,
        AVG(fork_duration_ms) AS avg_fork,
        AVG(auth_duration_ms) AS avg_auth
    FROM connection_log
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 748** (sql, query):

```sql
-- 查看pg_aios视图结构
\d pg_aios

-- 查询AIO状态
SELECT
    backend_type,
    backend_pid,

    -- 文件信息
    io_object,  -- 'relation', 'temp'等
    io_context,  -- 'normal', 'bulkread', 'vacuum'等

    -- ✅ AIO句
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 783** (sql, query):

```sql
-- 创建AIO监控视图
CREATE OR REPLACE VIEW aio_performance_dashboard AS
WITH aio_summary AS (
    SELECT
        COUNT(*) AS active_backends,
        SUM(allocated_aios) AS total_allocated,
        SUM(max_a
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 838** (sql, query):

```sql
-- 对比AIO开启前后的性能
-- （需要先记录历史数据到监控表）

CREATE TABLE aio_performance_history (
    sample_time TIMESTAMPTZ DEFAULT now(),
    aio_enabled BOOLEAN,
    query_type TEXT,
    avg_duration_ms NUMERIC,
    io_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 922** (sql, query):

```sql
-- 查看当前锁等待情况
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    bloc
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 974** (sql, query):

```sql
-- 从JSON日志中提取死锁信息
CREATE TEMP TABLE deadlock_history (
    occurred_at TIMESTAMPTZ,
    victim_pid INT,
    victor_pid INT,
    victim_query TEXT,
    victor_query TEXT,
    locked_relation TEXT,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1015** (sql, query):

```sql
-- 创建锁超时告警函数
CREATE OR REPLACE FUNCTION check_long_running_locks()
RETURNS TABLE (
    alert_level TEXT,
    message TEXT,
    action_required TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        '🔴
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1050** (sql, query):

```sql
-- PostgreSQL 18 pg_stat_statements新增字段

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查询增强统计信息
SELECT
    queryid,
    query,
    calls,
    total_exec_time,
    mean_exec_time,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1104** (sql, query):

```sql
-- PostgreSQL 18新增维护耗时统计
SELECT
    schemaname,
    relname AS table_name,

    -- ✅ 新增：VACUUM耗时统计
    last_vacuum,
    vacuum_count,
    CASE
        WHEN total_vacuum_time_ms IS NOT NULL AND vacuum_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1802** (sql, query):

```sql
-- 创建性能基线表
CREATE TABLE performance_baseline (
    metric_name TEXT PRIMARY KEY,
    baseline_value NUMERIC,
    unit TEXT,
    threshold_warning NUMERIC,
    threshold_critical NUMERIC,
    last_upda
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1863** (python, loop):

```python
#!/usr/bin/env python3
"""
PostgreSQL 18 自动化巡检脚本
每日执行，生成健康报告
"""

import psycopg2
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mi
```

**建议**:

- 添加数据库操作性能测试
- 添加循环性能测试

---

### 23-PostGIS地理空间数据库实战.md

**行 25** (sql, query):

```sql
-- 点（POINT）
CREATE TABLE locations (
    loc_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom geometry(POINT, 4326)  -- WGS84坐标系
);

INSERT INTO locations (name, geom) VALUES
('北京', ST_GeomFromT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 68** (sql, index):

```sql
-- 创建空间索引
CREATE INDEX idx_locations_geom ON locations USING gist(geom);
CREATE INDEX idx_roads_geom ON roads USING gist(geom);
CREATE INDEX idx_districts_geom ON districts USING gist(geom);

-- 查询性能

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 91** (sql, query):

```sql
-- 计算两点距离（米）
SELECT
    l1.name AS from_loc,
    l2.name AS to_loc,
    ST_Distance(
        l1.geom::geography,
        l2.geom::geography
    ) AS distance_meters
FROM locations l1, locations l2
WHE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 118** (sql, query):

```sql
-- 点是否在多边形内
SELECT l.name
FROM locations l
JOIN districts d ON ST_Within(l.geom, d.geom)
WHERE d.name = '朝阳区';

-- 相交
SELECT r.name
FROM roads r
JOIN districts d ON ST_Intersects(r.geom, d.geom)
WHERE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 150** (sql, index):

```sql
-- 商家表
CREATE TABLE restaurants (
    restaurant_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    location geometry(POINT, 4326),
    delivery_range INT DEFAULT 3000  -- 配送范围（米）
);

CREATE INDEX idx_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 231** (sql, index):

```sql
-- 围栏表
CREATE TABLE geofences (
    fence_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    fence_type VARCHAR(50),
    geom geometry(POLYGON, 4326),
    metadata JSONB
);

CREATE INDEX idx_geofences_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 294** (sql, query):

```sql
-- 轨迹表
CREATE TABLE trajectories (
    traj_id BIGSERIAL PRIMARY KEY,
    device_id INT,
    path geometry(LINESTRING, 4326),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ
);

-- 计算路径长度
SELECT

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 329** (sql, query):

```sql
-- 将点聚合到网格
WITH grid AS (
    SELECT
        ST_MakeEnvelope(
            x, y,
            x + 0.01, y + 0.01,
            4326
        ) AS cell,
        x, y
    FROM
        generate_series(116.0,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 360** (sql, query):

```sql
-- 聚簇索引（物理排序）
CLUSTER locations USING idx_locations_geom;

-- 定期维护
VACUUM ANALYZE locations;

-- 查看索引使用
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 382** (sql, query):

```sql
-- geometry: 平面坐标，快
SELECT ST_Distance(
    ST_MakePoint(116.4, 39.9),
    ST_MakePoint(116.5, 40.0)
);  -- 返回度数

-- geography: 球面坐标，准确
SELECT ST_Distance(
    ST_MakePoint(116.4, 39.9)::geography,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 23-安全增强与零信任架构指南.md

**行 161** (sql, query):

```sql
-- 企业SSO集成（Okta/Azure AD/Keycloak）
-- 1. 安装oauth扩展
CREATE EXTENSION IF NOT EXISTS oauth2;

-- 2. 配置OAuth提供商（企业Okta）
CREATE SERVER okta_oauth FOREIGN DATA WRAPPER oauth2_fdw OPTIONS (
    authorization
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 299** (sql, query):

```sql
-- PostgreSQL 18 SCRAM增强

-- 1. 强制SCRAM认证（禁用MD5）
-- pg_hba.conf
host    all    all    0.0.0.0/0    scram-sha-256

-- 2. 密码强度策略（使用passwordcheck扩展）
CREATE EXTENSION IF NOT EXISTS passwordcheck;

-- post
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 439** (sql, query):

```sql
-- 企业级角色体系设计

-- 1. 创建角色层次
-- 顶层：超级管理员（仅DBA）
CREATE ROLE dba WITH SUPERUSER LOGIN PASSWORD 'xxx';

-- 第二层：功能角色（不可登录）
CREATE ROLE db_readonly NOLOGIN;
CREATE ROLE db_readwrite NOLOGIN;
CREATE ROLE db_a
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 526** (sql, query):

```sql
-- 多租户SaaS平台示例
CREATE TABLE tenants (
    tenant_id SERIAL PRIMARY KEY,
    tenant_name TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 596** (sql, query):

```sql
-- 完整的多租户安全架构

-- 1. 租户上下文设置（应用层）
CREATE OR REPLACE FUNCTION set_tenant_context(
    p_tenant_id INT,
    p_user_id INT
)
RETURNS VOID AS $$
BEGIN
    -- 验证用户属于该租户
    IF NOT EXISTS (
        SELECT 1
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 676** (sql, index):

```sql
-- RLS性能开销测试

-- 1. 无RLS基线测试
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM documents WHERE tenant_id = 1;
-- Execution Time: 125 ms

-- 2. 启用RLS
ALTER TAB
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 741** (sql, query):

```sql
-- 查看SSL连接统计
SELECT
    datname,
    usename,
    client_addr,
    ssl,
    ssl_version,
    ssl_cipher,
    ssl_bits
FROM pg_stat_ssl
WHERE ssl = true;

-- 监控非SSL连接（安全审计）
SELECT
    usename,
    clie
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 810** (sql, query):

```sql
-- 使用pgcrypto扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 敏感数据表
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    ssn_encrypted BYTEA,
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 867** (sql, query):

```sql
-- 安装pgAudit
CREATE EXTENSION pgaudit;

-- 配置审计策略
-- postgresql.conf
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'all'  -- 审计所有操作
pgaudit.log_catalog = off  -- 不审计系统表查询
pgaudit.log_parameter =
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 902** (sql, query):

```sql
-- 将审计日志导入数据库（使用file_fdw）
CREATE EXTENSION file_fdw;

CREATE SERVER log_server FOREIGN DATA WRAPPER file_fdw;

CREATE FOREIGN TABLE audit_logs (
    log_time TIMESTAMPTZ,
    user_name TEXT,
    datab
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 975** (sql, query):

```sql
-- GDPR合规报告：数据访问追踪
CREATE OR REPLACE FUNCTION gdpr_access_report(
    p_user_email TEXT,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    access_time TIMESTAMPTZ,
    database_name TEX
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1057** (sql, query):

```sql
-- 微隔离：细粒度网络访问控制

-- 1. Schema级隔离
CREATE SCHEMA finance;
CREATE SCHEMA operations;
CREATE SCHEMA analytics;

-- 2. 角色绑定Schema
GRANT USAGE ON SCHEMA finance TO finance_team;
REVOKE ALL ON SCHEMA financ
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1100** (sql, query):

```sql
-- 持续验证：会话中的实时权限检查

-- 1. 会话超时（自动断开）
ALTER SYSTEM SET idle_in_transaction_session_timeout = '10min';
ALTER SYSTEM SET statement_timeout = '5min';

-- 2. 动态权限验证
CREATE OR REPLACE FUNCTION verify_sessio
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1164** (sql, query):

```sql
-- GDPR工具函数集

-- 1. 用户数据导出（数据可携权）
CREATE OR REPLACE FUNCTION gdpr_export_user_data(
    p_user_email TEXT
)
RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    SELECT json_build_object(
        'p
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1308** (sql, query):

```sql
-- SOC 2审计证据收集

-- CC6.1：逻辑和物理访问控制
-- 证据：pg_hba.conf + 角色权限报告
SELECT
    r.rolname,
    r.rolsuper,
    r.rolcreaterole,
    r.rolcreatedb,
    array_agg(m.rolname) AS member_of
FROM pg_roles r
LEFT J
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1349** (sql, query):

```sql
-- 实时安全事件监控
CREATE MATERIALIZED VIEW security_events_summary AS
SELECT
    DATE_TRUNC('hour', log_time) AS event_hour,

    -- 认证失败
    COUNT(*) FILTER (WHERE message LIKE '%authentication failed%') A
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1394** (sql, query):

```sql
-- 基于行为的入侵检测
CREATE OR REPLACE FUNCTION detect_intrusion()
RETURNS TABLE (
    threat_level TEXT,
    user_name TEXT,
    client_addr INET,
    threat_description TEXT,
    evidence JSONB
) AS $$
BEGI
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 24-全文检索深度实战.md

**行 7** (sql, query):

```sql
-- 文本转向量
SELECT to_tsvector('english', 'PostgreSQL is a powerful database');
-- 结果: 'databas':5 'postgresql':1 'power':4

-- 查询
SELECT to_tsquery('english', 'postgresql & database');
-- 结果: 'postgresq
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 24** (sql, query):

```sql
-- 安装zhparser
-- sudo apt install postgresql-18-zhparser

CREATE EXTENSION zhparser;

-- 创建中文配置
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION chinese AD
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 49** (sql, index):

```sql
CREATE TABLE documents (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    search_vector tsvector
);

-- 生成搜索向量
UPDATE documents
SET search_vector =
    setweight(to_tsvector('engli
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 88** (sql, query):

```sql
-- 基础排序
SELECT
    doc_id,
    title,
    ts_rank(search_vector, query) AS rank
FROM documents,
     to_tsquery('english', 'postgresql & database') query
WHERE search_vector @@ query
ORDER BY rank DES
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 131** (sql, query):

```sql
-- 高亮匹配内容
SELECT
    doc_id,
    title,
    ts_headline(
        'english',
        content,
        to_tsquery('english', 'postgresql & mvcc'),
        'StartSel=<b>, StopSel=</b>, MaxWords=50, MinWo
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 156** (sql, query):

```sql
-- 精确短语
SELECT * FROM documents
WHERE search_vector @@ phraseto_tsquery('english', 'database management system');

-- 邻近搜索（词距离<3）
SELECT * FROM documents
WHERE search_vector @@ to_tsquery('english', '
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 168** (sql, query):

```sql
-- 前缀匹配
SELECT * FROM documents
WHERE search_vector @@ to_tsquery('english', 'postgre:*');
-- 匹配: postgres, postgresql, postgresconf等

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 197** (sql, index):

```sql
CREATE TABLE multilang_docs (
    doc_id SERIAL PRIMARY KEY,
    title_en TEXT,
    content_en TEXT,
    title_zh TEXT,
    content_zh TEXT,
    search_vector_en tsvector,
    search_vector_zh tsvecto
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 240** (sql, index):

```sql
-- GIN索引（推荐）
CREATE INDEX idx_gin ON documents USING gin(search_vector);
-- 构建慢，查询快，更新慢

-- GiST索引
CREATE INDEX idx_gist ON documents USING gist(search_vector);
-- 构建快，查询较快，更新快

-- 性能对比（100万文档）
/*
索引类
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 261** (sql, index):

```sql
-- 启用并行构建
SET max_parallel_maintenance_workers = 8;

CREATE INDEX idx_search_parallel ON documents
USING gin(search_vector);

-- 时间: 15分钟 → 4分钟 (-73%)

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 277** (sql, index):

```sql
-- 搜索词表
CREATE TABLE search_terms (
    term VARCHAR(100) PRIMARY KEY,
    frequency INT DEFAULT 0,
    last_searched TIMESTAMPTZ DEFAULT now()
);

-- 记录搜索
INSERT INTO search_terms (term, frequency)
V
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 316** (sql, index):

```sql
-- 表结构
CREATE TABLE hybrid_docs (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    search_vector tsvector,
    embedding vector(768)
);

-- 双索引
CREATE INDEX ON hybrid_docs USING gi
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

### 24-容灾与高可用架构设计指南.md

**行 111** (sql, query):

```sql
-- === 发布端配置 ===

-- 1. 创建发布
CREATE PUBLICATION prod_publication FOR ALL TABLES;

-- 或选择性发布
CREATE PUBLICATION orders_publication
FOR TABLE orders, order_items, customers
WITH (publish = 'insert,updat
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 313** (sql, query):

```sql
-- 在主库执行
CREATE USER replicator REPLICATION LOGIN ENCRYPTED PASSWORD 'secure_password';

-- 授权
GRANT pg_read_all_data TO replicator;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 580** (sql, query):

```sql
-- 查看复制槽状态
SELECT
    slot_name,
    slot_type,
    database,
    active,

    -- ✅ PG18新增：更详细的状态
    confirmed_flush_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) / 1024 / 1024
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 619** (sql, query):

```sql
-- 自动清理空闲复制槽
CREATE OR REPLACE FUNCTION cleanup_inactive_slots()
RETURNS TABLE (
    dropped_slot TEXT,
    reason TEXT
) AS $$
DECLARE
    slot RECORD;
    inactive_duration INTERVAL;
BEGIN
    FOR s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 664** (sql, query):

```sql
-- 查看订阅冲突统计
SELECT
    subname AS subscription_name,

    -- ✅ PG18新增：冲突统计
    apply_error_count,
    sync_error_count,

    -- 冲突类型统计
    stats ->> 'insert_conflicts' AS insert_conflicts,
    stats -
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 691** (sql, query):

```sql
-- 配置冲突解决策略
ALTER SUBSCRIPTION my_subscription SET (
    -- ✅ PG18新增选项
    disable_on_error = false,  -- 遇到错误不禁用订阅

    -- 冲突解决策略（未来版本）
    -- conflict_resolution = 'apply_remote'  -- 使用远程数据
    -- co
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1091** (sql, query):

```sql
-- RTO优化清单

-- 1. 减少检测时间
ALTER SYSTEM SET wal_receiver_timeout = 5000;  -- 5秒检测
ALTER SYSTEM SET wal_sender_timeout = 5000;

-- 2. 加速故障切换（Patroni配置）
# patroni.yml
bootstrap:
  dcs:
    ttl: 15  -- 缩短T
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 25-JIT编译深度解析.md

**行 27** (sql, query):

```sql
-- 查看JIT状态
SHOW jit;  -- on/off

-- 启用JIT
SET jit = on;

-- JIT参数
SET jit_above_cost = 100000;           -- 成本阈值
SET jit_inline_above_cost = 500000;    -- 内联阈值
SET jit_optimize_above_cost = 500000;  -
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 61** (sql, query):

```sql
-- 场景1: 大量表达式计算
SELECT
    user_id,
    amount * 1.1 * (1 - discount) * (1 + tax) AS final_price,
    CASE
        WHEN amount > 1000 THEN 'high'
        WHEN amount > 100 THEN 'medium'
        ELSE '
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 98** (sql, query):

```sql
-- 场景1: I/O密集型
SELECT * FROM users WHERE user_id = 123;
-- 主要时间在I/O，JIT无帮助

-- 场景2: 小结果集
SELECT * FROM users LIMIT 10;
-- JIT编译时间 > 执行时间

-- 场景3: 简单查询
SELECT user_id, username FROM users WHERE status
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 118** (sql, query):

```sql
-- 禁用JIT
SET jit = off;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    l_returnflag,
    l_linestatus,
    sum(l_quantity) as sum_qty,
    sum(l_extendedprice) as sum_base_price,
    sum(l_extendedprice * (1
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 197** (sql, query):

```sql
-- pg_stat_statements查看JIT使用
SELECT
    LEFT(query, 100) AS query,
    calls,
    mean_exec_time,
    jit_functions,
    jit_generation_time,
    jit_inlining_time,
    jit_optimization_time,
    jit_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 25-性能基准测试与调优实战指南.md

**行 373** (sql, query):

```sql
-- custom_workload.sql
-- 模拟真实电商场景

\set customer_id random(1, 10000000)
\set product_id random(1, 100000)
\set quantity random(1, 10)

BEGIN;

-- 1. 查询商品信息（30%）
SELECT * FROM products
WHERE product_i
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 532** (sql, query):

```sql
-- 秒杀压测脚本
-- spike_test.sql

\set product_id 12345
\set user_id random(1, 10000000)

-- 模拟秒杀抢购
BEGIN;

-- 1. 检查库存（SELECT FOR UPDATE）
SELECT stock, version
FROM products
WHERE product_id = :product_id

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 585** (sql, query):

```sql
-- iot_insert_test.sql
-- 模拟IoT设备高频写入

\set device_id random(1, 100000)
\set metric_value random(0, 1000)

INSERT INTO sensor_data (device_id, timestamp, value, quality)
VALUES (
    :device_id,
    n
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 632** (sql, query):

```sql
-- 分析工作负载类型
WITH workload_stats AS (
    SELECT
        SUM(calls) FILTER (WHERE query LIKE 'SELECT%' AND query NOT LIKE '%FOR UPDATE%') AS select_count,
        SUM(calls) FILTER (WHERE query LIKE 'I
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 741** (sql, query):

```sql
-- 综合性能分析视图
CREATE OR REPLACE VIEW query_performance_analysis AS
SELECT
    queryid,
    LEFT(query, 80) AS query_preview,
    calls,

    -- 执行时间统计
    ROUND(total_exec_time::NUMERIC, 2) AS total_tim
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 962** (sql, query):

```sql
-- 原始查询（PG17: 8分钟）
SELECT ...
FROM fact_sales f
WHERE EXISTS (
    SELECT 1 FROM dim_product p
    WHERE p.product_id = f.product_id AND p.category = 'Electronics'
)
AND f.amount > (
    SELECT AVG(am
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1011** (sql, index):

```sql
-- 1. 优化分区策略（按天分区）
CREATE TABLE sensor_data (
    device_id INT,
    timestamp TIMESTAMPTZ,
    value NUMERIC,
    PRIMARY KEY (device_id, timestamp)
) PARTITION BY RANGE (timestamp);

-- 2. 使用BRIN索引（
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

### 26-并行查询深度优化.md

**行 60** (sql, query):

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM large_table;

/*
Finalize Aggregate (cost=...)
  ->  Gather (cost=...)
        Workers Planned: 4
        Workers Launched: 4
        ->  Partial Aggreg
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 78** (sql, index):

```sql
CREATE INDEX idx_created ON orders(created_at);

EXPLAIN ANALYZE
SELECT * FROM orders WHERE created_at > '2024-01-01';

/*
Gather (cost=...)
  Workers Planned: 2
  ->  Parallel Index Scan using idx_cr
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 95** (sql, query):

```sql
EXPLAIN ANALYZE
SELECT * FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.created_at > '2024-01-01';

/*
Gather
  Workers: 4
  ->  Parallel Hash Join
        Hash Cond: (o.user_id = u.user_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 119** (sql, query):

```sql
EXPLAIN ANALYZE
SELECT
    category,
    COUNT(*),
    AVG(price),
    SUM(sales)
FROM products
GROUP BY category;

/*
Finalize GroupAggregate
  ->  Gather Merge
        Workers: 4
        ->  Partial
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 148** (sql, query):

```sql
-- 优化器自动决定并行度
-- 基于表大小和系统资源

-- 查看计划的并行度
EXPLAIN
SELECT COUNT(*) FROM large_table;

/*
Workers Planned: 4  ← 自动决定
Workers Launched: 4
*/

-- 影响因素:
-- 1. 表大小
-- 2. max_parallel_workers_per_gather
-- 3.
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 170** (sql, query):

```sql
-- 表级设置
ALTER TABLE large_table SET (parallel_workers = 8);

-- 查询级设置（通过成本参数）
SET parallel_setup_cost = 0;
SET parallel_tuple_cost = 0;

-- 强制并行
SET min_parallel_table_scan_size = 0;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 249** (sql, query):

```sql
-- 检查函数并行安全性
SELECT
    proname,
    proparallel
FROM pg_proc
WHERE proname LIKE 'my_%';

/*
proparallel:
'r' = RESTRICTED (默认)
's' = SAFE (并行安全)
'u' = UNSAFE (不能并行)
*/

-- 标记函数为并行安全
CREATE OR REPLACE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 305** (sql, query):

```sql
-- 大表聚合查询
CREATE TABLE fact_sales (
    sale_id BIGSERIAL PRIMARY KEY,
    product_id INT,
    amount NUMERIC,
    sale_date DATE
);
-- 1亿行

-- 优化前（单线程）
SET max_parallel_workers_per_gather = 0;
SELECT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 26-扩展开发与插件生态指南.md

**行 204** (sql, query):

```sql
-- my_extension--1.0.sql

-- 注册C函数
CREATE OR REPLACE FUNCTION add_numbers(int, int)
RETURNS int
AS 'MODULE_PATHNAME', 'add_numbers'
LANGUAGE C STRICT IMMUTABLE;

CREATE OR REPLACE FUNCTION concat_with
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 295** (sql, bulk):

```sql
-- 技巧1：使用RETURNS TABLE替代OUT参数
-- ❌ 低效
CREATE OR REPLACE FUNCTION get_user_orders_slow(
    p_user_id INT,
    OUT order_count INT,
    OUT total_amount NUMERIC
)
AS $$
BEGIN
    SELECT COUNT(*), SUM(t
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 375** (sql, query):

```sql
-- 完善的异常处理
CREATE OR REPLACE FUNCTION safe_transfer(
    p_from_account INT,
    p_to_account INT,
    p_amount NUMERIC
)
RETURNS VOID AS $$
DECLARE
    v_from_balance NUMERIC;
BEGIN
    -- 开始事务（隐式）


```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 441** (sql, query):

```sql
-- 调试技巧1：使用RAISE NOTICE
CREATE OR REPLACE FUNCTION debug_example(p_value INT)
RETURNS INT AS $$
DECLARE
    v_result INT;
BEGIN
    RAISE NOTICE '输入参数: %', p_value;

    v_result := p_value * 2;
    R
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 489** (sql, query):

```sql
-- Citus：将PostgreSQL转为分布式数据库
CREATE EXTENSION citus;

-- 配置Worker节点（Coordinator节点执行）
SELECT citus_add_node('worker1.example.com', 5432);
SELECT citus_add_node('worker2.example.com', 5432);

-- 创建分布式表

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 610** (sql, query):

```sql
-- complex--1.0.sql

-- 注册类型
CREATE TYPE complex;

CREATE FUNCTION complex_in(cstring)
RETURNS complex
AS 'MODULE_PATHNAME'
LANGUAGE C IMMUTABLE STRICT;

CREATE FUNCTION complex_out(complex)
RETURNS c
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 652** (sql, query):

```sql
-- 复数操作符完整集合
CREATE OPERATOR - (
    LEFTARG = complex,
    RIGHTARG = complex,
    FUNCTION = complex_subtract
);

CREATE OPERATOR * (
    LEFTARG = complex,
    RIGHTARG = complex,
    FUNCTION = co
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 713** (sql, index):

```sql
-- 注册操作符类
CREATE OPERATOR CLASS complex_ops
    DEFAULT FOR TYPE complex USING btree AS
        OPERATOR 1 <,
        OPERATOR 2 <=,
        OPERATOR 3 =,
        OPERATOR 4 >=,
        OPERATOR 5 >,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 812** (sql, query):

```sql
-- 安装pg_cron
CREATE EXTENSION pg_cron;

-- 定时任务：每天凌晨2点清理旧数据
SELECT cron.schedule(
    'cleanup-old-data',
    '0 2 * * *',  -- cron表达式
    $$
    DELETE FROM logs WHERE created_at < now() - INTERVAL '
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 898** (sql, query):

```sql
-- 配置auto_explain
-- postgresql.conf
shared_preload_libraries = 'auto_explain'
auto_explain.log_min_duration = 1000  -- 超过1秒的查询
auto_explain.log_analyze = on
auto_explain.log_buffers = on
auto_explain
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1030** (sql, query):

```sql
-- 安全检查清单

-- 1. 使用SECURITY DEFINER谨慎
-- ❌ 危险：函数以DEFINER权限运行，可能权限提升
CREATE OR REPLACE FUNCTION dangerous_function()
RETURNS VOID
SECURITY DEFINER  -- ⚠️ 危险
AS $$
BEGIN
    EXECUTE 'DROP TABLE importan
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1083** (sql, query):

```sql
-- 扩展版本管理
-- my_extension--1.0.sql （初始版本）
-- my_extension--1.0--1.1.sql （升级脚本）
-- my_extension--1.1--1.2.sql

-- 升级扩展
ALTER EXTENSION my_extension UPDATE TO '1.2';

-- 查看扩展版本
SELECT
    extname,
    e
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1117** (sql, query):

```sql
-- 创建升级脚本：my_extension--1.0--1.1.sql
-- 添加新函数
CREATE OR REPLACE FUNCTION new_feature()
RETURNS TEXT AS $$
BEGIN
    RETURN 'Version 1.1 feature';
END;
$$ LANGUAGE plpgsql;

-- 修改现有函数
CREATE OR REPLACE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 27-分区表深度实战.md

**行 7** (sql, query):

```sql
-- 时序数据：按时间分区
CREATE TABLE logs (
    log_id BIGSERIAL,
    message TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (log_id, created_at)
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE T
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 29** (sql, query):

```sql
-- 按地区分区
CREATE TABLE orders (
    order_id BIGSERIAL,
    region VARCHAR(10) NOT NULL,
    amount NUMERIC,
    PRIMARY KEY (order_id, region)
) PARTITION BY LIST (region);

CREATE TABLE orders_asia P
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 50** (sql, query):

```sql
-- 均匀分布大表
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(100)
) PARTITION BY HASH (user_id);

-- 创建8个分区
DO $$
BEGIN
    FOR i IN 0..7 LOOP
        EXECUTE format('

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 77** (sql, query):

```sql
-- 一级：按年分区
CREATE TABLE sales (
    sale_id BIGSERIAL,
    region VARCHAR(10),
    amount NUMERIC,
    sale_date DATE NOT NULL,
    PRIMARY KEY (sale_id, sale_date, region)
) PARTITION BY RANGE (sale_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 111** (sql, query):

```sql
-- 使用pg_partman扩展
CREATE EXTENSION pg_partman;

-- 配置自动分区
SELECT partman.create_parent(
    p_parent_table := 'public.logs',
    p_control := 'created_at',
    p_type := 'native',
    p_interval := 'd
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 134** (sql, bulk):

```sql
-- 创建独立表
CREATE TABLE logs_2024_03 (LIKE logs INCLUDING ALL);

-- 加载数据
COPY logs_2024_03 FROM '/data/logs_2024_03.csv';

-- 附加为分区
ALTER TABLE logs ATTACH PARTITION logs_2024_03
FOR VALUES FROM ('2024-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 158** (sql, query):

```sql
-- 启用分区裁剪（默认开启）
SET constraint_exclusion = partition;
SET enable_partition_pruning = on;

-- 查看裁剪效果
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM logs
WHERE created_at >= '2024-01-15' AND created_at < '202
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 189** (sql, index):

```sql
-- 本地索引（每个分区独立）
CREATE INDEX ON logs (created_at);
-- 自动在每个分区创建独立索引

-- 查看分区索引
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE tablename LIKE 'logs_%'
ORDER BY tablename, ind
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 220** (sql, query):

```sql
-- 测试数据：1亿行，10年数据

-- 单表查询
SELECT COUNT(*) FROM logs_single
WHERE created_at >= '2024-01-01' AND created_at < '2024-02-01';
-- 时间: 8.5秒（全表扫描）

-- 分区表查询（按月分区）
SELECT COUNT(*) FROM logs_partitioned
WHER
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 280** (sql, query):

```sql
SET max_parallel_workers_per_gather = 8;

EXPLAIN ANALYZE
SELECT COUNT(*) FROM logs_partitioned
WHERE created_at >= '2024-01-01';

/*
Finalize Aggregate
  ->  Gather
        Workers: 8
        ->  Par
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 27-多模态数据库能力指南.md

**行 153** (sql, query):

```sql
-- JSON vs JSONB
CREATE TABLE json_test (
    id SERIAL PRIMARY KEY,
    data_json JSON,
    data_jsonb JSONB
);

-- 插入相同数据
INSERT INTO json_test (data_json, data_jsonb)
VALUES (
    '{"name": "Alice"
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 227** (sql, query):

```sql
-- JSON_TABLE：将JSON展开为关系表
SELECT * FROM JSON_TABLE(
    '[
        {"name": "Alice", "age": 30, "skills": ["Python", "SQL"]},
        {"name": "Bob", "age": 25, "skills": ["Java", "Go"]}
    ]'::jsonb
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 291** (sql, index):

```sql
-- 索引策略1：GIN索引（通用）
CREATE INDEX idx_data_gin ON json_table USING gin (data);

-- 查询
EXPLAIN ANALYZE
SELECT * FROM json_table
WHERE data @> '{"status": "active"}';
-- 使用GIN索引，快速定位

-- 索引策略2：GIN jsonb_p
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 328** (sql, query):

```sql
-- 安装pgvector
CREATE EXTENSION vector;

-- 创建向量表
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536)  -- OpenAI ada-002维度
);

-- 插入向量数据
INSERT INTO embedd
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 370** (sql, index):

```sql
-- 创建测试表（100万向量）
CREATE TABLE vectors_test (
    id SERIAL PRIMARY KEY,
    embedding vector(384)  -- 降维模型，提高测试速度
);

INSERT INTO vectors_test (embedding)
SELECT
    array_to_string(
        ARRAY(SEL
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 467** (sql, index):

```sql
-- 1. 创建知识库表
CREATE TABLE knowledge_base (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 549** (sql, query):

```sql
-- 优化1：预过滤（减少向量搜索范围）
SELECT * FROM knowledge_base
WHERE metadata->>'category' = 'PostgreSQL'  -- 先过滤
ORDER BY embedding <=> query_vector
LIMIT 5;

-- 优化2：混合检索（BM25 + 向量）
WITH keyword_results AS (

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 586** (sql, query):

```sql
-- 安装Apache AGE
CREATE EXTENSION age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- 创建图
SELECT create_graph('social_network');

-- 创建节点（Cypher语法）
SELECT * FROM cypher('social_network'
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 626** (sql, query):

```sql
-- 最短路径算法
SELECT * FROM cypher('social_network', $$
    MATCH path = shortestPath(
        (alice:Person {name: 'Alice'})-[:FOLLOWS*]-(charlie:Person {name: 'Charlie'})
    )
    RETURN length(path) A
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 654** (sql, query):

```sql
-- 企业知识图谱示例
SELECT create_graph('enterprise_kg');

-- 创建多类型节点
SELECT * FROM cypher('enterprise_kg', $$
    CREATE (p1:Product {name: 'PostgreSQL 18', category: 'Database'})
    CREATE (p2:Product {nam
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 694** (sql, query):

```sql
-- 安装TimescaleDB
CREATE EXTENSION timescaledb;

-- 创建普通表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INT,
    temperature NUMERIC,
    humidity NUMERIC
);

-- 转换为Hypertable
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 747** (sql, query):

```sql
-- 连续聚合（Continuous Aggregate）：预聚合物化视图
CREATE MATERIALIZED VIEW sensor_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    sensor_id,
    AVG(temperature) AS avg
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 778** (sql, query):

```sql
-- 压缩旧数据（节省80-95%存储）
ALTER TABLE sensor_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- 自动压缩策略（30天前数据）
SELE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 823** (sql, query):

```sql
-- 安装PostGIS
CREATE EXTENSION postgis;

-- 创建空间表
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(Point, 4326),  -- WGS 84坐标系
    address TEXT
);

-- 插入地理位
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 860** (sql, index):

```sql
-- GiST索引（精确空间查询）
CREATE INDEX idx_locations_gist ON locations USING gist (geom);

-- BRIN索引（大规模时序空间数据）
CREATE INDEX idx_locations_brin ON locations USING brin (geom);

-- 性能对比（1000万地理点）
-- GiST索引：查询5
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 878** (sql, query):

```sql
-- 案例：外卖配送距离计算
CREATE TABLE restaurants (
    restaurant_id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOMETRY(Point, 4326)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    restaur
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 937** (sql, index):

```sql
-- 全文检索表
CREATE TABLE articles (
    article_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    content_tsv tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '')
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 964** (sql, index):

```sql
-- 中文分词（使用zhparser）
CREATE EXTENSION zhparser;
CREATE TEXT SEARCH CONFIGURATION chinese_zh (PARSER = zhparser);

-- 中文文档
CREATE TABLE articles_zh (
    article_id SERIAL PRIMARY KEY,
    title TEXT,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 988** (sql, query):

```sql
-- 多因素相关性排序
SELECT
    article_id,
    title,

    -- 因素1：文本相关性
    ts_rank(content_tsv, query) AS text_relevance,

    -- 因素2：时间新鲜度
    EXTRACT(EPOCH FROM (now() - created_at)) / 86400 AS days_old,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1025** (sql, query):

```sql
-- 混合查询：关系型 + JSON + 向量
SELECT
    u.user_id,
    u.name,
    u.profile->>'bio' AS bio,  -- JSON查询

    -- 向量相似度
    u.interests_vector <=> target_vector AS interest_similarity,

    -- 全文检索
    ts_ra
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1059** (sql, index):

```sql
-- 多模态索引组合
CREATE INDEX idx_users_profile_gin ON users USING gin (profile jsonb_path_ops);
CREATE INDEX idx_users_vector_hnsw ON users USING hnsw (interests_vector vector_cosine_ops);
CREATE INDEX idx
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 1082** (sql, query):

```sql
-- 多模态查询性能调优

-- 1. work_mem调整（向量/排序）
SET work_mem = '256MB';  -- 向量搜索需要更多内存

-- 2. 向量索引参数
SET hnsw.ef_search = 100;  -- 提高召回率

-- 3. 并行查询
SET max_parallel_workers_per_gather = 4;

-- 4. JIT编译
SET jit
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1182** (sql, index):

```sql
-- 1. 知识库表（向量+JSON元数据）
CREATE TABLE knowledge_articles (
    article_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding vector(1536),
    metadata JSONB,  -- {category, tags, autho
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 1255** (sql, query):

```sql
-- 社交网络：图关系 + 时序活动
-- 1. 用户表（关系型）
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. 关注关系（图数据，使用AGE）
SELECT create_graph(
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 1316** (sql, index):

```sql
-- IoT设备监控平台

-- 1. 设备表（关系型 + 空间）
CREATE TABLE devices (
    device_id SERIAL PRIMARY KEY,
    device_name TEXT,
    device_type TEXT,
    location GEOMETRY(Point, 4326),
    metadata JSONB
);

CREATE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

### 28-云原生存储引擎适配指南.md

**行 172** (sql, query):

```sql
-- 创建使用自定义存储引擎的表（理论）
CREATE TABLE columnar_data (
    id INT,
    value TEXT
) USING columnar;  -- ← 指定存储引擎

-- 当前支持的存储引擎：
-- 1. heap（默认）
-- 2. columnar（Citus提供）
-- 3. zedstore（实验性，列式存储）
-- 4. zheap（实
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 202** (sql, query):

```sql
-- 安装s3_fdw
CREATE EXTENSION s3_fdw;

-- 创建S3服务器
CREATE SERVER s3_server
FOREIGN DATA WRAPPER s3_fdw
OPTIONS (
    endpoint 's3.amazonaws.com',
    region 'us-east-1'
);

-- 创建用户映射（访问密钥）
CREATE USER M
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 253** (sql, query):

```sql
-- 优化1：分区裁剪（S3按日期分区）
CREATE FOREIGN TABLE s3_logs_partitioned (
    log_time TIMESTAMPTZ,
    user_id INT,
    event_type TEXT
) SERVER s3_server
OPTIONS (
    bucket 'my-logs',
    prefix 'year=2024/
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 405** (sql, query):

```sql
-- Neon CLI
neonctl branches create --name dev_branch --parent main
-- 创建时间：<1秒（基于写时复制）

-- 分支之间独立
-- main分支：生产数据
-- dev_branch：开发测试，修改不影响main

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 417** (sql, query):

```sql
-- 回到任意时间点（无需PITR）
neonctl branches create --name debug_branch --parent main --timestamp '2024-12-04 10:00:00'

-- 连接到历史时间点分支
psql postgresql://...@debug_branch.neon.tech/mydb
SELECT * FROM orders WHE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 523** (sql, query):

```sql
-- 传统流复制：延迟100ms-1s
-- Aurora：延迟<10ms（共享存储）

-- 只读副本配置（最多15个）
aws rds create-db-instance-read-replica \
    --db-instance-identifier my-aurora-replica-1 \
    --source-db-instance-identifier my-aurora
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 601** (sql, query):

```sql
-- AlloyDB独特优势：混合行列存储
-- （无需扩展，原生支持）

-- 创建表（自动优化）
CREATE TABLE analytics_data (
    date DATE,
    user_id INT,
    event_type TEXT,
    value NUMERIC
);

-- AlloyDB自动识别：
-- - OLTP查询（WHERE user_id=xx
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 660** (sql, query):

```sql
-- IOPS监控（pg_stat_io）
SELECT
    backend_type,
    object,
    reads,
    writes,
    read_time,
    write_time,

    -- IOPS计算
    ROUND(reads * 1000.0 / NULLIF(read_time, 0), 2) AS read_iops,
    RO
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 686** (sql, bulk):

```sql
-- 吞吐量测试
-- COPY大批量导入
\timing on
COPY large_table FROM '/data/import.csv' WITH (FORMAT csv, PARALLEL 8);
-- Time: 45s（1000万行，5GB数据）

-- 吞吐量 = 5GB / 45s = 111 MB/s

-- 优化：
-- 1. 增加maintenance_work_mem

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试
- 添加批量操作性能测试

---

### 28-表空间与存储管理.md

**行 7** (sql, query):

```sql
-- 创建表空间
CREATE TABLESPACE fast_ssd LOCATION '/mnt/nvme/pg_tablespace';
CREATE TABLESPACE archive_hdd LOCATION '/mnt/hdd/pg_archive';

-- 查看表空间
\db+
SELECT * FROM pg_tablespace;

-- 设置默认表空间
SET defaul
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 38** (sql, query):

```sql
-- 热数据（NVMe SSD）
CREATE TABLESPACE hot_storage LOCATION '/mnt/nvme';

-- 温数据（SATA SSD）
CREATE TABLESPACE warm_storage LOCATION '/mnt/ssd';

-- 冷数据（HDD）
CREATE TABLESPACE cold_storage LOCATION '/mnt/hd
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 91** (sql, query):

```sql
-- TOAST存储策略
/*
PLAIN: 不压缩，不外部存储（小数据）
EXTENDED: 压缩+外部存储（默认）
EXTERNAL: 外部存储，不压缩（已压缩数据）
MAIN: 压缩，尽量不外部存储
*/

-- 设置TOAST策略
ALTER TABLE documents ALTER COLUMN content SET STORAGE EXTERNAL;

-- 查看TOAST使用
S
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 122** (sql, query):

```sql
-- 设置填充因子（预留更新空间）
CREATE TABLE frequently_updated (
    id SERIAL PRIMARY KEY,
    data TEXT
) WITH (fillfactor = 70);  -- 预留30%空间

-- 适用场景:
-- ✓ 高频UPDATE
-- ✓ 减少HOT更新失败
-- ✓ 减少页分裂

-- 不适用:
-- ✗ 只读表（浪
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 149** (sql, query):

```sql
-- 启用压缩（默认）
ALTER TABLE large_table ALTER COLUMN content SET COMPRESSION pglz;

-- PostgreSQL 14+: LZ4压缩（更快）
ALTER TABLE large_table ALTER COLUMN content SET COMPRESSION lz4;

-- 查看压缩效果
SELECT
    att
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 172** (sql, query):

```sql
-- 数据库大小
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS size,
    pg_database_size(datname) AS bytes
FROM pg_database
ORDER BY bytes DESC;

-- 表空间使用
SELECT
    spcname,
    pg_si
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 29-pg_cron定时任务实战.md

**行 29** (sql, index):

```sql
-- 每天凌晨2点VACUUM
SELECT cron.schedule('nightly-vacuum', '0 2 * * *', 'VACUUM ANALYZE;');

-- 每小时清理旧日志
SELECT cron.schedule('cleanup-logs', '0 * * * *',
    'DELETE FROM logs WHERE created_at < now() -
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 48** (sql, query):

```sql
-- 查看所有任务
SELECT * FROM cron.job ORDER BY jobid;

-- 查看任务运行历史
SELECT
    job_id,
    run_details->'command' AS command,
    status,
    start_time,
    end_time,
    end_time - start_time AS duration

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 81** (sql, query):

```sql
-- 数据归档任务
SELECT cron.schedule('archive-old-orders', '0 1 * * *', $$
    INSERT INTO orders_archive
    SELECT * FROM orders
    WHERE created_at < CURRENT_DATE - INTERVAL '365 days';

    DELETE FROM
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 106** (sql, query):

```sql
-- 创建维护存储过程
CREATE OR REPLACE PROCEDURE maintenance_routine()
LANGUAGE plpgsql AS $$
BEGIN
    -- 1. VACUUM
    VACUUM ANALYZE;

    -- 2. 更新统计
    ANALYZE;

    -- 3. 清理日志
    DELETE FROM logs WHERE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 137** (sql, query):

```sql
-- 自动创建分区函数
CREATE OR REPLACE FUNCTION auto_create_partitions()
RETURNS VOID AS $$
DECLARE
    target_date DATE;
    partition_name TEXT;
BEGIN
    -- 创建未来7天的分区
    FOR i IN 0..6 LOOP
        target_d
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 182** (sql, bulk):

```sql
-- 创建备份函数
CREATE OR REPLACE FUNCTION backup_database()
RETURNS VOID AS $$
DECLARE
    backup_file TEXT;
BEGIN
    backup_file := '/backup/db_' || to_char(now(), 'YYYYMMDD_HH24MISS') || '.sql';

    --
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 209** (sql, query):

```sql
-- 记录性能指标
CREATE TABLE performance_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    recorded_at TIMESTAMPTZ DEFAULT now()
);

-- 定时采集
SELECT c
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 240** (sql, query):

```sql
-- 查看失败的任务
SELECT
    j.jobid,
    j.schedule,
    j.command,
    r.status,
    r.start_time,
    r.return_message
FROM cron.job j
JOIN cron.job_run_details r ON j.jobid = r.job_id
WHERE r.status = 'f
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 30-pg_stat_statements性能分析.md

**行 5** (sql, query):

```sql
-- 安装扩展
CREATE EXTENSION pg_stat_statements;

-- 配置参数
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.max = 10000;  -- 跟踪10000个查询
ALTER SYSTEM SET
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 26** (sql, query):

```sql
SELECT
    queryid,              -- 查询ID（hash）
    query,                -- 查询文本
    calls,                -- 执行次数
    total_exec_time,      -- 总执行时间（ms）
    mean_exec_time,       -- 平均执行时间
    min_ex
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 52** (sql, query):

```sql
-- 按平均时间排序
SELECT
    queryid,
    LEFT(query, 100) AS query_preview,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_ms,
    ROUND(min_exec_time::numeric, 2) AS min_ms,
    ROUND(max_exec_tim
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 82** (sql, query):

```sql
-- 查询缓存命中率
SELECT
    LEFT(query, 100) AS query,
    calls,
    shared_blks_hit + shared_blks_read AS total_blks,
    ROUND(shared_blks_hit * 100.0 / NULLIF(shared_blks_hit + shared_blks_read, 0), 2)
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 99** (sql, query):

```sql
-- 查找使用临时文件的查询
SELECT
    LEFT(query, 100) AS query,
    calls,
    temp_blks_read + temp_blks_written AS temp_blks,
    ROUND((temp_blks_read + temp_blks_written) * 8.0 / 1024, 2) AS temp_mb
FROM pg_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 120** (sql, query):

```sql
-- 查询类型分布
SELECT
    CASE
        WHEN query LIKE 'SELECT%' THEN 'SELECT'
        WHEN query LIKE 'INSERT%' THEN 'INSERT'
        WHEN query LIKE 'UPDATE%' THEN 'UPDATE'
        WHEN query LIKE 'DELET
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 141** (sql, query):

```sql
-- 最常访问的表
SELECT
    regexp_replace(query, '.*FROM\s+(\w+).*', '\1') AS table_name,
    COUNT(*) AS query_count,
    SUM(calls) AS total_calls
FROM pg_stat_statements
WHERE query LIKE '%FROM%'
GROUP B
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 160** (sql, query):

```sql
-- 保存当前统计作为基线
CREATE TABLE query_baseline AS
SELECT
    queryid,
    query,
    calls,
    mean_exec_time,
    total_exec_time,
    now() AS baseline_time
FROM pg_stat_statements;

-- 对比当前与基线
SELECT

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 191** (sql, query):

```sql
-- 创建报告表
CREATE TABLE daily_query_reports (
    report_id BIGSERIAL PRIMARY KEY,
    report_date DATE,
    top_slow_queries JSONB,
    top_frequent_queries JSONB,
    cache_hit_summary JSONB,
    gene
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 258** (sql, query):

```sql
-- 重置所有统计
SELECT pg_stat_statements_reset();

-- 重置特定查询
SELECT pg_stat_statements_reset(queryid := 123456789);

-- 定期重置（避免统计过时）
SELECT cron.schedule('monthly-reset', '0 0 1 * *',
    'SELECT pg_stat_s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 31-连接管理深度优化.md

**行 5** (sql, query):

```sql
-- 查看连接状态
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    backend_start,
    state,
    state_change,
    now() - backend_start AS connection_age,
    now() - state_change AS s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 37** (sql, query):

```sql
-- 查看配置
SHOW max_connections;  -- 默认100

-- 修改
ALTER SYSTEM SET max_connections = 200;
-- 需要重启

-- 当前连接数
SELECT COUNT(*) FROM pg_stat_activity;

-- 保留连接
ALTER SYSTEM SET superuser_reserved_connections
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 54** (sql, query):

```sql
-- 限制用户连接数
ALTER USER app_user CONNECTION LIMIT 50;

-- 限制数据库连接数
ALTER DATABASE mydb CONNECTION LIMIT 100;

-- 查看限制
SELECT
    rolname,
    rolconnlimit
FROM pg_roles
WHERE rolconnlimit != -1;

SELECT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 81** (sql, query):

```sql
-- PostgreSQL 14+: idle_session_timeout
ALTER SYSTEM SET idle_session_timeout = '10min';

-- idle_in_transaction_session_timeout
ALTER SYSTEM SET idle_in_transaction_session_timeout = '5min';

SELECT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 104** (python, database):

```python
# Python: SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@localhost/mydb',
    poolclass=QueuePool,
    pool_
```

**建议**:

- 添加数据库操作性能测试

---

**行 131** (sql, query):

```sql
-- 创建监控视图
CREATE VIEW connection_leaks AS
SELECT
    usename,
    application_name,
    client_addr,
    backend_start,
    state,
    now() - backend_start AS connection_age,
    now() - state_change
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 167** (sql, query):

```sql
-- 问题1: 连接数满
SELECT
    COUNT(*) AS current,
    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') AS max,
    ROUND(COUNT(*) * 100.0 / (SELECT setting::int FROM pg_settings WHERE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 32-查询计划缓存优化.md

**行 7** (sql, query):

```sql
-- 准备语句
PREPARE user_query (INT) AS
SELECT * FROM users WHERE user_id = $1;

-- 执行（使用缓存计划）
EXECUTE user_query(123);
EXECUTE user_query(456);
EXECUTE user_query(789);

-- 查看prepared语句
SELECT
    name,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 32** (python, loop):

```python
import psycopg2
import time

conn = psycopg2.connect("dbname=mydb")
cursor = conn.cursor()

# 不使用prepared statement
start = time.time()
for i in range(1000):
    cursor.execute("SELECT * FROM users WH
```

**建议**:

- 添加数据库操作性能测试
- 添加循环性能测试

---

**行 67** (sql, query):

```sql
-- PostgreSQL自动选择通用或自定义计划
PREPARE user_query (INT) AS
SELECT * FROM users WHERE user_id = $1;

-- 前5次：使用custom plan
EXECUTE user_query(1);
EXECUTE user_query(2);
EXECUTE user_query(3);
EXECUTE user_qu
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 106** (sql, query):

```sql
-- 导致计划失效的操作:
-- 1. 表结构改变
ALTER TABLE users ADD COLUMN status VARCHAR(20);
-- prepared statement自动失效

-- 2. 统计信息更新
ANALYZE users;
-- custom plan重新生成

-- 3. 配置参数改变
SET work_mem = '512MB';
-- 影响计划选择

--
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 166** (sql, query):

```sql
-- 查看prepared statements
SELECT
    name,
    statement,
    prepare_time,
    parameter_types,
    from_sql  -- 是否来自SQL PREPARE命令
FROM pg_prepared_statements;

-- 查看执行统计（需要pg_stat_statements）
SELECT

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 33-批量操作性能优化.md

**行 7** (python, loop):

```python
import psycopg2
import time

conn = psycopg2.connect("dbname=test")
cursor = conn.cursor()

# 方法1: 单条INSERT（最慢）
start = time.time()
for i in range(10000):
    cursor.execute("INSERT INTO test (id, dat
```

**建议**:

- 添加数据库操作性能测试
- 添加循环性能测试

---

**行 47** (sql, query):

```sql
-- 单条（慢）
INSERT INTO users (username, email) VALUES ('user1', 'user1@example.com');
INSERT INTO users (username, email) VALUES ('user2', 'user2@example.com');

-- 批量（快）
INSERT INTO users (username, em
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 69** (sql, query):

```sql
-- 批量UPDATE
UPDATE products p
SET price = v.new_price
FROM (VALUES
    (1, 99.99),
    (2, 149.99),
    (3, 199.99),
    (4, 249.99)
) AS v(product_id, new_price)
WHERE p.product_id = v.product_id;

-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 87** (sql, bulk):

```sql
-- 大批量UPDATE（>1000行）
CREATE TEMP TABLE updates_temp (
    product_id INT,
    new_price NUMERIC
);

-- 批量导入
COPY updates_temp FROM '/tmp/price_updates.csv' WITH CSV;

-- 批量更新
UPDATE products p
SET pri
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 112** (sql, query):

```sql
-- 避免长事务和锁
DO $$
DECLARE
    deleted INT;
    total INT := 0;
BEGIN
    LOOP
        DELETE FROM logs
        WHERE created_at < CURRENT_DATE - INTERVAL '90 days'
          AND ctid = ANY(

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 149** (sql, query):

```sql
-- DELETE: 逐行删除，生成WAL，可回滚
DELETE FROM large_table;
-- 时间: 120秒

-- TRUNCATE: 快速清空，极少WAL，不可回滚
TRUNCATE TABLE large_table;
-- 时间: 0.5秒 (-99.6%)

-- TRUNCATE级联
TRUNCATE TABLE parent_table CASCADE;
-- 同时清
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 169** (sql, bulk):

```sql
-- 准备数据文件
-- /tmp/data.csv

-- 基础COPY
COPY users FROM '/tmp/data.csv' WITH (FORMAT csv, HEADER true);

-- 优化技巧:
-- 1. 临时禁用触发器
ALTER TABLE users DISABLE TRIGGER ALL;
COPY users FROM '/tmp/data.csv' WIT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试
- 添加批量操作性能测试

---

**行 202** (sql, query):

```sql
-- 批量插入或更新
INSERT INTO inventory (product_id, stock, updated_at)
VALUES
    (1, 100, now()),
    (2, 200, now()),
    (3, 300, now())
ON CONFLICT (product_id)
DO UPDATE SET
    stock = inventory.stock
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 219** (sql, query):

```sql
MERGE INTO inventory t
USING (VALUES
    (1, 100),
    (2, 200),
    (3, 300)
) AS s(product_id, stock_delta)
ON t.product_id = s.product_id
WHEN MATCHED THEN
    UPDATE SET stock = t.stock + s.stock_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 239** (python, loop):

```python
from concurrent.futures import ThreadPoolExecutor
import psycopg2

def insert_batch(batch_id, batch_data):
    """单个批次插入"""
    conn = psycopg2.connect("dbname=mydb")
    cursor = conn.cursor()

    f
```

**建议**:

- 添加循环性能测试

---

### 34-EXPLAIN执行计划完全解读.md

**行 5** (sql, query):

```sql
-- 基础EXPLAIN
EXPLAIN SELECT * FROM users WHERE age > 25;

-- 实际执行
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 25;

-- 详细信息
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, COSTS, TIMING, SUMMARY)
SELECT * FROM
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 27** (sql, query):

```sql
EXPLAIN ANALYZE
SELECT * FROM users;

/*
Seq Scan on users  (cost=0.00..1000.00 rows=10000 width=100) (actual time=0.010..5.234 rows=9850 loops=1)

解读:
├─ cost=0.00..1000.00
│  ├─ 0.00: 启动成本
│  └─ 100
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 52** (sql, query):

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE user_id = 123;

/*
Index Scan using users_pkey on users  (cost=0.42..8.44 rows=1 width=100) (actual time=0.015..0.016 rows=1 loops=1)
  Index Cond: (user_id =
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 75** (sql, query):

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT email FROM users WHERE email = 'test@example.com';

/*
Index Only Scan using idx_users_email on users  (cost=0.42..8.44 rows=1 width=100) (actual time=0.012..0.013 ro
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 92** (sql, query):

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE age > 25 OR city = 'NYC';

/*
Bitmap Heap Scan on users  (cost=25.00..500.00 rows=5000 width=100)
  Recheck Cond: ((age > 25) OR (city = 'NYC'))
  Buffers: sh
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 122** (sql, query):

```sql
EXPLAIN ANALYZE
SELECT * FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE u.user_id = 123;

/*
Nested Loop  (cost=0.85..25.00 rows=10 width=200) (actual time=0.025..0.156 rows=8 loops=1)
  ->
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 143** (sql, query):

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders o
JOIN products p ON o.product_id = p.product_id;

/*
Hash Join  (cost=500.00..5000.00 rows=50000 width=200) (actual time=5.234..125.456 rows=48523 loop
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 175** (sql, query):

```sql
EXPLAIN ANALYZE
SELECT * FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id;

/*
Merge Join  (cost=0.85..5000.00 rows=100000 width=200)
  Merge Cond: (o.order_id = oi.order_id)
  ->  Index
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 198** (sql, query):

```sql
EXPLAIN ANALYZE
SELECT department, COUNT(*), AVG(salary)
FROM employees
GROUP BY department
ORDER BY department;

/*
GroupAggregate  (cost=1000.00..1500.00 rows=50 width=12)
  Group Key: department

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 217** (sql, query):

```sql
EXPLAIN ANALYZE
SELECT department, COUNT(*), AVG(salary)
FROM employees
GROUP BY department;

/*
HashAggregate  (cost=1000.00..1050.00 rows=50 width=12)
  Group Key: department
  Batches: 1  Memory Us
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 35-慢查询优化实战案例.md

**行 7** (sql, query):

```sql
-- 慢查询
SELECT * FROM orders WHERE user_id = 12345;
-- 执行时间: 2.5秒

EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 12345;

/*
Seq Scan on orders  (cost=0.00..250000.00 rows=100 width=150) (actual
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 27** (sql, index):

```sql
-- 创建索引
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- 再次执行
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 12345;

/*
Index Scan using idx_orders_user_id on orders  (cost=0.56..325.67 r
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 50** (sql, query):

```sql
-- 查询
SELECT * FROM products WHERE category_id = 5;
-- 执行时间: 3.2秒

EXPLAIN ANALYZE
SELECT * FROM products WHERE category_id = 5;

/*
Seq Scan on products  (cost=0.00..50000.00 rows=100 width=200) (act
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 69** (sql, query):

```sql
-- 更新统计信息
ANALYZE products;

-- 再次查询
EXPLAIN ANALYZE
SELECT * FROM products WHERE category_id = 5;

/*
Index Scan using idx_products_category on products  (cost=0.56..25000.00 rows=850000 width=200) (
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 91** (python, loop):

```python
# ORM查询（Django/SQLAlchemy）
users = User.objects.all()
for user in users:  # 1次查询
    orders = user.orders.all()  # N次查询
    print(f"{user.name}: {len(orders)} orders")

# 生成SQL:
# SELECT * FROM users;
```

**建议**:

- 添加循环性能测试

---

**行 110** (python, loop):

```python
# 使用JOIN或prefetch
users = User.objects.prefetch_related('orders').all()
for user in users:
    orders = user.orders.all()  # 无额外查询
    print(f"{user.name}: {len(orders)} orders")

# 生成SQL:
# SELECT *
```

**建议**:

- 添加循环性能测试

---

**行 131** (sql, query):

```sql
-- 查询
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';
-- 执行时间: 1.8秒

EXPLAIN ANALYZE
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

/*
Seq Scan on users  (cost=0.00..50000.
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 149** (sql, index):

```sql
-- 方案1: 表达式索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

EXPLAIN ANALYZE
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

/*
Index Scan using idx_users_lower_email  (cost
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 172** (sql, query):

```sql
-- 三表JOIN
SELECT * FROM
    large_table1 t1  -- 1000万行
    JOIN large_table2 t2 ON t1.id = t2.ref_id  -- 1000万行
    JOIN small_table t3 ON t2.category = t3.category  -- 100行
WHERE t3.category = 'elect
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 196** (sql, query):

```sql
-- 改写查询：小表驱动
SELECT * FROM
    small_table t3
    JOIN large_table2 t2 ON t3.category = t2.category
    JOIN large_table1 t1 ON t2.ref_id = t1.id
WHERE t3.category = 'electronics';

-- 或使用CTE
WITH fil
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 224** (sql, query):

```sql
-- user_id列类型: BIGINT
SELECT * FROM users WHERE user_id = '12345';  -- 字符串
-- 执行时间: 850ms

EXPLAIN ANALYZE
/*
Seq Scan on users  (cost=0.00..50000.00 rows=5000 width=100)
  Filter: ((user_id)::text =
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 240** (sql, query):

```sql
-- 使用正确类型
SELECT * FROM users WHERE user_id = 12345;  -- 整数

/*
Index Scan using users_pkey  (cost=0.42..8.44 rows=1 width=100)

优化后: 850ms → 2ms (-99.8%)
*/

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 257** (sql, query):

```sql
-- 查询前10个结果
SELECT * FROM orders
WHERE status = 'pending'
ORDER BY created_at DESC
LIMIT 10;
-- 执行时间: 5.8秒

EXPLAIN ANALYZE
/*
Limit  (actual time=5234.567..5789.123 rows=10 loops=1)
  ->  Sort  (actu
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 281** (sql, index):

```sql
-- 创建组合索引
CREATE INDEX idx_orders_status_created ON orders(status, created_at DESC);

EXPLAIN ANALYZE
SELECT * FROM orders
WHERE status = 'pending'
ORDER BY created_at DESC
LIMIT 10;

/*
Limit  (actua
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 307** (sql, query):

```sql
-- 相关子查询
SELECT
    u.user_id,
    u.username,
    (SELECT COUNT(*) FROM orders WHERE user_id = u.user_id) AS order_count
FROM users u;
-- 执行时间: 25秒

EXPLAIN ANALYZE
/*
Seq Scan on users u  (actual ti
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 330** (sql, query):

```sql
-- 改写为JOIN
SELECT
    u.user_id,
    u.username,
    COUNT(o.order_id) AS order_count
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.username;

EXPLAIN ANALYZE
/*
HashA
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 356** (sql, query):

```sql
SELECT DISTINCT user_id FROM orders;
-- 执行时间: 8.5秒

EXPLAIN ANALYZE
/*
HashAggregate  (actual time=6234.567..8456.789 rows=10000 loops=1)
  Batches: 8  Memory Usage: 256MB  Disk Usage: 128MB
  ->  Seq
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 372** (sql, index):

```sql
-- 方案1: 使用索引（如果存在）
CREATE INDEX idx_orders_user_id ON orders(user_id);

SELECT DISTINCT user_id FROM orders;

/*
HashAggregate  (actual time=125.456..156.789 rows=10000 loops=1)
  ->  Index Only Scan
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 395** (sql, query):

```sql
-- 深度分页
SELECT * FROM products
ORDER BY product_id
LIMIT 20 OFFSET 100000;
-- 执行时间: 1.2秒

EXPLAIN ANALYZE
/*
Limit  (actual time=1156.789..1189.012 rows=20 loops=1)
  ->  Seq Scan on products  (actual
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 413** (sql, index):

```sql
-- Keyset分页
SELECT * FROM products
WHERE product_id > 100000  -- 上一页最后的ID
ORDER BY product_id
LIMIT 20;

EXPLAIN ANALYZE
/*
Index Scan using products_pkey on products  (actual time=0.025..0.156 rows=2
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

### 36-SQL注入防御完整指南.md

**行 7** (python, database):

```python
# ❌ 危险代码
username = request.GET['username']
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

# 攻击payload:
# username = "admin' OR '1'='1"
# 生成SQL: SELECT * FROM user
```

**建议**:

- 添加数据库操作性能测试

---

**行 30** (python, database):

```python
# ✅ 正确方式：参数化查询
username = request.GET['username']
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)  # 参数作为tuple传递
)

# psycopg2自动转义，无论输入什么都安全
# username = "admin' OR '1'=
```

**建议**:

- 添加数据库操作性能测试

---

**行 100** (python, database):

```python
# ✅ 安全：ORM查询
session.query(User).filter(User.username == username).all()

# ✅ 安全：text() with bindparams
from sqlalchemy import text
session.execute(
    text("SELECT * FROM users WHERE username = :use
```

**建议**:

- 添加数据库操作性能测试

---

**行 139** (python, database):

```python
# ❌ 部分防御
keyword = request.GET['keyword']
cursor.execute(
    "SELECT * FROM products WHERE name LIKE %s",
    (f"%{keyword}%",)  # 参数化了，但...
)

# 攻击: keyword = "%"
# 返回所有记录（DoS攻击）

# ✅ 完整防御
keyword =
```

**建议**:

- 添加数据库操作性能测试

---

**行 165** (python, database):

```python
# ❌ 危险
page = request.GET['page']
query = f"SELECT * FROM users LIMIT 20 OFFSET {page * 20}"

# ✅ 安全：强制类型转换
page = int(request.GET['page'])  # 抛出ValueError如果非整数
if page < 0 or page > 10000:
    page =
```

**建议**:

- 添加数据库操作性能测试

---

**行 187** (python, database):

```python
# 场景1: 注册 → 存储（第一步）
username = "admin'--"
cursor.execute(
    "INSERT INTO users (username) VALUES (%s)",
    (username,)  # 安全存储了 "admin'--"
)

# 场景2: 读取 → 使用（第二步，危险）
cursor.execute("SELECT username
```

**建议**:

- 添加数据库操作性能测试

---

**行 218** (sql, query):

```sql
-- 应用账号：只授予必要权限
CREATE ROLE app_user LOGIN PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
-- 不授予DELETE, DROP等危险权限

-- 只读账号
C
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 233** (sql, query):

```sql
-- 使用SECURITY DEFINER函数
CREATE OR REPLACE FUNCTION safe_get_user(p_username TEXT)
RETURNS TABLE(id INT, username TEXT, email TEXT)
SECURITY DEFINER
LANGUAGE plpgsql AS $$
BEGIN
    -- 函数内部控制查询逻辑
    R
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 270** (sql, query):

```sql
-- 启用查询日志
ALTER SYSTEM SET log_statement = 'all';  -- 或 'mod'（修改语句）
ALTER SYSTEM SET log_min_duration_statement = 0;

-- 分析日志（Python示例）
import re

# 检测可疑模式
sql_injection_patterns = [
    r"(?i)union\s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 337** (python, loop):

```python
# SQL注入测试Payload
injection_payloads = [
    "admin' OR '1'='1",
    "admin'--",
    "'; DROP TABLE users; --",
    "1' UNION SELECT password FROM users--",
    "1' AND (SELECT COUNT(*) FROM users) > 0
```

**建议**:

- 添加循环性能测试

---

### 37-JSON-JSONB完整实战.md

**行 5** (sql, query):

```sql
-- JSON: 文本存储，保留格式
CREATE TABLE logs_json (
    id SERIAL PRIMARY KEY,
    data JSON
);

-- JSONB: 二进制存储，支持索引
CREATE TABLE logs_jsonb (
    id SERIAL PRIMARY KEY,
    data JSONB
);

-- 性能对比
INSERT INT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 47** (sql, query):

```sql
-- 插入JSON数据
INSERT INTO users (id, info) VALUES
(1, '{"name": "Alice", "age": 30, "tags": ["admin", "user"]}'),
(2, '{"name": "Bob", "age": 25, "email": "bob@example.com"}');

-- 从函数构建
INSERT INTO use
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 64** (sql, query):

```sql
-- -> 返回JSON对象
SELECT info->'name' FROM users WHERE id = 1;
-- 结果: "Alice"（带引号）

-- ->> 返回文本
SELECT info->>'name' FROM users WHERE id = 1;
-- 结果: Alice（无引号）

-- 嵌套访问
SELECT info->'address'->>'city' FR
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 93** (sql, query):

```sql
-- 更新整个字段
UPDATE users
SET info = '{"name": "Alice Updated", "age": 31}'
WHERE id = 1;

-- 更新单个键
UPDATE users
SET info = jsonb_set(info, '{age}', '31')
WHERE id = 1;

-- 添加新键
UPDATE users
SET info = i
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 126** (sql, query):

```sql
-- 包含检查 (@>)
SELECT * FROM users WHERE info @> '{"name": "Alice"}';

-- 被包含检查 (<@)
SELECT * FROM users WHERE '{"name": "Alice"}' <@ info;

-- 键存在
SELECT * FROM users WHERE info ? 'email';

-- 任一键存在
SE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 148** (sql, query):

```sql
-- 路径查询（PostgreSQL 12+）
SELECT * FROM users
WHERE jsonb_path_exists(info, '$.age ? (@ > 25)');

-- 提取值
SELECT jsonb_path_query(info, '$.tags[*]') FROM users;

-- 复杂条件
SELECT * FROM users
WHERE jsonb_p
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 170** (sql, index):

```sql
-- 默认GIN索引（支持 @>, ?, ?|, ?&）
CREATE INDEX idx_users_info ON users USING GIN (info);

-- 查询使用索引
EXPLAIN ANALYZE
SELECT * FROM users WHERE info @> '{"name": "Alice"}';

-- GIN索引类型
-- 1. jsonb_ops（默认）: 支
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 192** (sql, index):

```sql
-- 单个键索引
CREATE INDEX idx_users_name ON users ((info->>'name'));

-- 查询
SELECT * FROM users WHERE info->>'name' = 'Alice';
-- 使用索引

-- 嵌套键索引
CREATE INDEX idx_users_city ON users ((info->'address'->>'c
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 211** (sql, query):

```sql
-- 计数
SELECT
    info->>'status' AS status,
    COUNT(*) AS count
FROM orders
GROUP BY info->>'status';

-- 求和
SELECT SUM((info->>'amount')::NUMERIC) AS total
FROM orders
WHERE info->>'date' >= '2024-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 249** (sql, index):

```sql
CREATE TABLE event_logs (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 索引
CREATE INDEX idx_event_type ON event_logs(e
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 281** (sql, index):

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    attributes JSONB
);

-- 不同产品有不同属性
INSERT INTO products (name, attributes) VALUES
('Laptop', '{"brand": "Dell", "cpu": "Int
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 310** (sql, query):

```sql
CREATE TABLE user_settings (
    user_id INT PRIMARY KEY,
    settings JSONB DEFAULT '{}'
);

-- 默认配置
INSERT INTO user_settings (user_id, settings) VALUES
(1, '{
    "theme": "dark",
    "language": "
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 358** (sql, index):

```sql
-- 1. 使用jsonb_path_ops索引（查询简单时）
CREATE INDEX idx_fast ON logs USING GIN (data jsonb_path_ops);

-- 2. 提取常用字段
ALTER TABLE logs ADD COLUMN user_id INT;
UPDATE logs SET user_id = (data->>'user_id')::INT;
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

### 38-CTE与递归查询完全指南.md

**行 7** (sql, query):

```sql
-- 不使用CTE
SELECT *
FROM (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY user_id
) AS user_orders
WHERE order_count > 5;

-- 使用CTE（更清晰）
WITH user_orders AS (
    SELECT user_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 30** (sql, query):

```sql
WITH
active_users AS (
    SELECT id, username
    FROM users
    WHERE last_login > now() - INTERVAL '30 days'
),
recent_orders AS (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    WH
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 57** (sql, query):

```sql
-- 组织表
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT REFERENCES employees(id),
    title VARCHAR(100)
);

INSERT INTO employees (id, name, manager_id, t
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 107** (sql, query):

```sql
-- 显示完整层级路径
WITH RECURSIVE org_tree AS (
    SELECT
        id,
        name,
        manager_id,
        ARRAY[id] AS path,
        name::TEXT AS path_names,
        1 AS level
    FROM employees

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 157** (sql, query):

```sql
-- 好友表
CREATE TABLE friendships (
    user1_id INT,
    user2_id INT,
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user1_id, user2_id)
);

-- 查找所有朋友的朋友（2度连接）
WITH RECURSIVE friends_of_fr
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 220** (sql, query):

```sql
-- 城市路线表
CREATE TABLE routes (
    from_city VARCHAR(50),
    to_city VARCHAR(50),
    distance INT,
    PRIMARY KEY (from_city, to_city)
);

-- 查找最短路径
WITH RECURSIVE shortest_path AS (
    SELECT

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 274** (sql, query):

```sql
-- 生成1到100
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numbers
    WHERE n < 100
)
SELECT * FROM numbers;

-- 斐波那契数列
WITH RECURSIVE fibonacci(a, b, n) AS (

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 313** (sql, query):

```sql
-- 生成过去30天的日期
WITH RECURSIVE date_series AS (
    SELECT CURRENT_DATE AS date
    UNION ALL
    SELECT date - INTERVAL '1 day'
    FROM date_series
    WHERE date > CURRENT_DATE - INTERVAL '30 days'
)
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 349** (sql, query):

```sql
-- ❌ 危险：可能无限递归
WITH RECURSIVE bad_recursion AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM bad_recursion
    -- 没有终止条件！
)
SELECT * FROM bad_recursion;

-- ✅ 安全：添加终止条件
WITH RECURSIVE sa
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 376** (sql, query):

```sql
-- 图遍历中使用数组检测循环
WITH RECURSIVE graph_traversal AS (
    SELECT
        id,
        ARRAY[id] AS visited,
        1 AS depth
    FROM nodes
    WHERE id = 1

    UNION ALL

    SELECT
        e.target_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 406** (sql, query):

```sql
-- 产品物料表
CREATE TABLE bill_of_materials (
    product_id INT,
    component_id INT,
    quantity INT,
    PRIMARY KEY (product_id, component_id)
);

-- 递归展开BOM
WITH RECURSIVE bom_explosion AS (
    SE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 449** (sql, query):

```sql
-- 评论表
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    parent_id INT REFERENCES comments(id),
    user_id INT,
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 展示评论树
WITH RECUR
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 39-外键与约束完全实战.md

**行 7** (sql, query):

```sql
-- 创建表时定义
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200),
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 42** (sql, query):

```sql
-- CASCADE: 级联删除
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

DELETE FROM users WHERE id = 1;
-- 同时删除该用户的所有订单

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 93** (sql, query):

```sql
-- 主键更新时级联更新外键
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

UPDATE users SET
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 111** (sql, query):

```sql
-- 员工-经理关系
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT,
    FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL
);

INSERT INTO emplo
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 140** (sql, query):

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price NUMERIC(10, 2) CHECK (price > 0),
    discount_pct INT CHECK (discount_pct >= 0 AND discount_pct <= 100),
    stock
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 162** (sql, query):

```sql
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    check_in DATE,
    check_out DATE,
    guests INT,
    CHECK (check_out > check_in),
    CHECK (guests > 0 AND guests <= 10)
);

-- 测试
INSERT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 183** (sql, query):

```sql
CREATE TABLE discounts (
    id SERIAL PRIMARY KEY,
    product_id INT,
    discount_type VARCHAR(20),  -- 'percentage' or 'fixed'
    discount_value NUMERIC(10, 2),
    CONSTRAINT valid_discount CHEC
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 212** (sql, query):

```sql
-- 单列唯一
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(50) UNIQUE NOT NULL
);

-- 多列唯一（组合唯一）
CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 250** (sql, query):

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT  --
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 274** (sql, query):

```sql
-- 延迟约束（事务结束时检查）
CREATE TABLE employees (
    id INT PRIMARY KEY,
    manager_id INT,
    FOREIGN KEY (manager_id) REFERENCES employees(id)
        DEFERRABLE INITIALLY DEFERRED
);

-- 场景：交换两个员工的ID
BE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 302** (sql, query):

```sql
-- 防止时间重叠
CREATE EXTENSION btree_gist;

CREATE TABLE room_bookings (
    id SERIAL PRIMARY KEY,
    room_id INT,
    booked_range tstzrange,
    EXCLUDE USING gist (
        room_id WITH =,
        bo
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 333** (sql, index):

```sql
-- 外键索引
-- PostgreSQL不会自动为外键创建索引
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ❌ 慢：查询某用户的所有帖子
SELECT * FROM posts WHERE user_id
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 364** (sql, query):

```sql
-- 推荐命名规范
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT,
    status VARCHAR(20),
    total_amount NUMERIC(10, 2),

    -- pk_<table>
    CONSTRAINT pk_orders PRIMARY KEY (id),


```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 40-PostgreSQL18新特性总结.md

**行 7** (sql, query):

```sql
-- 配置异步I/O
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET io_combine_limit = '256kB';

-- 性能提升
-- TPC-H测试: +15% ~ +35%
-- 写密集: +25%
-- 全表扫描: +40%

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 28** (sql, index):

```sql
-- 场景：组合索引跳过前导列
CREATE INDEX idx_users_status_created ON users(status, created_at);

-- PostgreSQL 17及之前：无法使用索引
SELECT * FROM users WHERE created_at > '2024-01-01';
-- 全表扫描

-- PostgreSQL 18：Skip Scan
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 54** (sql, index):

```sql
-- PostgreSQL 18支持GIN索引并行构建
CREATE INDEX CONCURRENTLY idx_docs_content_gin ON documents USING GIN (content);

-- 性能对比
-- PostgreSQL 17: 45分钟（单线程）
-- PostgreSQL 18: 12分钟（8线程，-73%）

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 69** (sql, query):

```sql
-- 生成UUIDv7（时间排序）
SELECT gen_uuid_v7();
-- 01933b7e-8f5a-7000-8000-123456789abc

-- 对比UUIDv4
CREATE TABLE logs_v4 (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    data TEXT
);
-- INSERT性能: 基准

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 93** (sql, query):

```sql
-- 显示I/O统计
EXPLAIN (ANALYZE, BUFFERS, IO)
SELECT * FROM large_table WHERE condition;

/*
新增输出:
  I/O Timings: read=125.456 write=45.123
  Direct I/O: yes
  I/O Combine: 8 operations
*/

-- 显示JIT详情
EXP
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 114** (sql, query):

```sql
-- 时态约束（Temporal Constraints）
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    room_id INT,
    booking_period tstzrange,
    CONSTRAINT no_overlap EXCLUDE USING gist (
        room_id WITH =,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 146** (sql, query):

```sql
-- 双向逻辑复制
CREATE PUBLICATION pub_products FOR TABLE products;
CREATE SUBSCRIPTION sub_products
    CONNECTION 'host=replica1 dbname=mydb'
    PUBLICATION pub_products
    WITH (bidirectional = true);
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 163** (sql, query):

```sql
-- 复制槽自动清理
ALTER SYSTEM SET max_slot_wal_keep_size = '10GB';

-- 复制进度监控增强
SELECT
    slot_name,
    confirmed_flush_lsn,
    wal_status,
    safe_wal_size
FROM pg_replication_slots;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 196** (sql, query):

```sql
-- 新增RLS函数
CREATE POLICY tenant_isolation ON orders
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true)::INT)
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 228** (sql, query):

```sql
-- 积极冻结策略
ALTER SYSTEM SET vacuum_freeze_table_age = 100000000;  -- 降低默认值
ALTER SYSTEM SET autovacuum_freeze_max_age = 1000000000;

-- VACUUM进度详情
SELECT
    phase,
    heap_blks_total,
    heap_blks_s
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 263** (sql, query):

```sql
-- 更友好的错误信息
INSERT INTO users (email) VALUES ('invalid');

-- PostgreSQL 17:
-- ERROR: duplicate key value violates unique constraint "users_email_key"

-- PostgreSQL 18:
-- ERROR: duplicate key value
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 327** (sql, query):

```sql
-- 推荐PostgreSQL 18配置
ALTER SYSTEM SET io_direct = 'data,wal';          -- 异步I/O
ALTER SYSTEM SET io_combine_limit = '256kB';      -- I/O合并
ALTER SYSTEM SET enable_skip_scan = on;           -- Skip Sca
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 41-PostgreSQL开发者速查表.md

**行 45** (sql, query):

```sql
-- 基础查询
SELECT * FROM users WHERE age > 25;
SELECT COUNT(*) FROM users;
SELECT DISTINCT city FROM users;

-- JOIN
SELECT * FROM orders o
JOIN users u ON o.user_id = u.id;

-- LEFT JOIN
SELECT * FROM u
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 88** (sql, index):

```sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_name ON users(name);  -- 不锁表

-- 唯一索引
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- 部分索引
CREATE IN
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 125** (sql, bulk):

```sql
-- INSERT
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- 批量INSERT
INSERT INTO users (name, email) VALUES
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.co
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 157** (sql, query):

```sql
-- 创建用户
CREATE USER app_user WITH PASSWORD 'strong_password';

-- 创建角色
CREATE ROLE readonly;

-- 授权
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 183** (sql, query):

```sql
-- 创建数据库
CREATE DATABASE mydb;

-- 删除数据库
DROP DATABASE mydb;

-- 列出数据库
\l
SELECT datname FROM pg_database;

-- 数据库大小
SELECT pg_size_pretty(pg_database_size('mydb'));

-- 表大小
SELECT
    schemaname,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 214** (sql, query):

```sql
-- 当前连接数
SELECT COUNT(*) FROM pg_stat_activity;

-- 活跃查询
SELECT pid, usename, state, query
FROM pg_stat_activity
WHERE state != 'idle';

-- 慢查询（需要pg_stat_statements）
SELECT
    query,
    calls,
    m
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 255** (sql, index):

```sql
-- 异步I/O（性能+35%）
ALTER SYSTEM SET io_direct = 'data,wal';
SELECT pg_reload_conf();

-- Skip Scan
ALTER SYSTEM SET enable_skip_scan = on;

-- UUIDv7（时间排序）
SELECT gen_uuid_v7();

-- GIN并行构建（索引快73%）
CREA
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 335** (sql, query):

```sql
-- 终止查询
SELECT pg_cancel_backend(pid);  -- 尝试取消
SELECT pg_terminate_backend(pid);  -- 强制终止

-- 终止所有空闲连接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND pid != pg_backen
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 41-实时数据库完全指南.md

**行 75** (sql, query):

```sql
-- 创建通知函数
CREATE OR REPLACE FUNCTION notify_order_change()
RETURNS TRIGGER AS $$
BEGIN
    -- 发送通知
    PERFORM pg_notify(
        'order_events',
        json_build_object(
            'action', TG_OP
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 119** (sql, query):

```sql
-- Payload最大8000字节
SELECT length('very long string'::text);

-- 超过限制需要传递ID，再查询
PERFORM pg_notify(
    'large_data_event',
    json_build_object('id', NEW.id)::text
);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 138** (sql, query):

```sql
-- 订单表
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT no
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 189** (python, loop):

```python
import psycopg2
import json
import select

def listen_orders():
    """监听订单事件"""

    conn = psycopg2.connect(
        host='localhost',
        database='mydb',
        user='postgres'
    )

    con
```

**建议**:

- 添加数据库操作性能测试
- 添加循环性能测试

---

**行 306** (sql, query):

```sql
-- 消息表
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    room_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 通知函数
C
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 341** (python, database):

```python
def join_room(room_id: int):
    """加入聊天室"""

    cursor.execute(f"LISTEN room_{room_id};")
    print(f"✓ 加入房间 {room_id}")

def leave_room(room_id: int):
    """离开聊天室"""

    cursor.execute(f"UNLISTEN
```

**建议**:

- 添加数据库操作性能测试

---

**行 357** (sql, query):

```sql
-- 缓存失效通知
CREATE OR REPLACE FUNCTION notify_cache_invalidation()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'cache_invalidation',
        json_build_object(
            'table', TG_TAB
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 411** (sql, query):

```sql
-- 批量通知（避免每行触发）
CREATE OR REPLACE FUNCTION notify_batch_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- 只在事务结束时通知
    PERFORM pg_notify(
        'batch_changes',
        json_build_object(
            't
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 438** (sql, query):

```sql
-- 只在重要变更时通知
CREATE OR REPLACE FUNCTION notify_important_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- 只有状态变更时通知
    IF NEW.status != OLD.status THEN
        PERFORM pg_notify('order_status_changes',

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 494** (sql, query):

```sql
   BEGIN;
   INSERT INTO orders VALUES (...);
   -- 通知在COMMIT后才发送
   COMMIT;

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 515** (python, loop):

```python
   import time

   last_notify_time = time.time()

   while True:
       # 10秒超时
       if select.select([conn], [], [], 10) == ([], [], []):
           # 发送心跳查询
           cursor.execute("SELECT 1;")
```

**建议**:

- 添加数据库操作性能测试
- 添加循环性能测试

---

**行 554** (sql, query):

```sql
-- 统计表
CREATE TABLE dashboard_stats (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL,
    metric_value NUMERIC NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 更新触发器
CREAT
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 636** (sql, query):

```sql
-- 查看当前监听的通道
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    backend_start,
    state
FROM pg_stat_activity
WHERE backend_type = 'client backend'
  AND query LIKE '%LISTEN%';

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 652** (sql, query):

```sql
-- 通知统计（需要自定义）
CREATE TABLE notify_stats (
    channel_name VARCHAR(100),
    notify_count BIGINT,
    last_notify TIMESTAMPTZ
);

-- 在通知函数中记录
UPDATE notify_stats
SET notify_count = notify_count + 1,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 42-PostgreSQL故障排查手册.md

**行 77** (sql, query):

```sql
-- 查看当前连接
SELECT COUNT(*) FROM pg_stat_activity;

-- 查看max_connections
SHOW max_connections;

-- 查看各状态连接数
SELECT state, COUNT(*) FROM pg_stat_activity GROUP BY state;

-- 查看连接来源
SELECT
    application
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 114** (sql, index):

```sql
-- Step 1: 识别慢查询
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time,
    (mean_exec_time * calls) AS total_time
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- >100ms
ORDER BY t
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 176** (sql, query):

```sql
-- 查看活跃查询
SELECT
    pid,
    usename,
    state,
    now() - query_start AS duration,
    LEFT(query, 100) AS query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- 终止耗CPU查询
S
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 215** (sql, query):

```sql
-- 检查数据库大小
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- 检查大表
SELECT
    schemaname,
    tablename,
    pg_siz
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 258** (sql, query):

```sql
-- 查看所有锁
SELECT
    locktype,
    database,
    relation::regclass AS table,
    mode,
    granted,
    pid
FROM pg_locks
ORDER BY granted, pid;

-- 查看阻塞关系
WITH RECURSIVE blocking AS (
    SELECT

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 302** (sql, query):

```sql
-- 主库检查
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;

-- 从库检查
SELECT
    pg_is_in_recovery(),
    pg_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 42-全文搜索深度实战.md

**行 50** (sql, query):

```sql
-- tsvector: 文档向量
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- 结果: 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2

-- tsquery: 查询表达式
SELECT to_tsquery('engli
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 67** (sql, query):

```sql
-- 创建文章表
CREATE TABLE articles (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 简单搜索
SELECT * FROM articles
WHERE to_
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 88** (sql, index):

```sql
-- 添加tsvector列
ALTER TABLE articles ADD COLUMN tsv tsvector;

-- 生成tsvector
UPDATE articles SET tsv =
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''));

-- 创建GIN索引（性能关键！
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 106** (sql, query):

```sql
-- 触发器函数
CREATE OR REPLACE FUNCTION articles_tsv_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tsv := to_tsvector('english',
        coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, '')
    );

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 131** (sql, query):

```sql
-- 不同字段不同权重
UPDATE articles SET tsv =
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(content, '')), 'B');

-- 查询时考虑权重
SELECT
    id,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 149** (sql, query):

```sql
-- ts_rank: 基础排序
SELECT
    title,
    ts_rank(tsv, query) AS rank
FROM articles, to_tsquery('english', 'postgresql & performance') query
WHERE tsv @@ query
ORDER BY rank DESC;

-- ts_rank_cd: 考虑位置的排序
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 197** (sql, query):

```sql
-- 高亮匹配词
SELECT
    title,
    ts_headline('english', content, query, 'MaxWords=50, MinWords=20') AS snippet
FROM articles, to_tsquery('english', 'postgresql') query
WHERE tsv @@ query;

-- 自定义高亮标签
SE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 220** (sql, index):

```sql
-- GIN索引（推荐）：更快查询，较慢更新
CREATE INDEX idx_articles_gin ON articles USING GIN(tsv);

-- GiST索引：较快更新，较慢查询
CREATE INDEX idx_articles_gist ON articles USING GIST(tsv);

-- 性能对比
EXPLAIN ANALYZE
SELECT * FROM
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 234** (sql, index):

```sql
-- 调整GIN参数（PostgreSQL 18）
CREATE INDEX idx_articles_gin ON articles
USING GIN(tsv) WITH (fastupdate = on, gin_pending_list_limit = 4096);

-- fastupdate: 批量更新pending list
-- gin_pending_list_limit: pe
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 245** (sql, index):

```sql
-- 按时间分区
CREATE TABLE articles_2024_01 PARTITION OF articles
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE articles_2024_02 PARTITION OF articles
FOR VALUES FROM ('2024-02-01') TO ('
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 260** (sql, query):

```sql
-- 使用LIMIT
SELECT * FROM articles
WHERE tsv @@ to_tsquery('postgresql')
ORDER BY ts_rank(tsv, to_tsquery('postgresql')) DESC
LIMIT 20;

-- 使用CTE预过滤
WITH matched AS (
    SELECT id, title, tsv
    FROM
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 303** (sql, query):

```sql
-- 创建扩展
CREATE EXTENSION zhparser;

-- 创建中文文本搜索配置
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);

-- 添加token映射
ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR
    n,v,a,i,e,l WI
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 321** (sql, index):

```sql
-- 创建带中文的文章表
CREATE TABLE cn_articles (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tsv tsvector
);

-- 触发器（中文）
CREATE OR REPLACE FUNCTION cn_articles_tsv_tri
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 363** (sql, query):

```sql
-- 检测语言并使用相应配置
CREATE OR REPLACE FUNCTION detect_language(text TEXT)
RETURNS regconfig AS $$
BEGIN
    -- 简单检测：是否包含中文
    IF text ~ '[\u4e00-\u9fa5]' THEN
        RETURN 'chinese'::regconfig;
    ELSE
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 388** (sql, index):

```sql
-- 完整的博客搜索表
CREATE TABLE blog_posts (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    category VARCHAR(50),
    tags TEXT[],
    pu
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 460** (sql, query):

```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    brand VARCHAR(100),
    category VARCHAR(100),
    price NUMERIC(10, 2),
    stock INT,
    tsv
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 507** (sql, index):

```sql
-- 文档表（支持多种格式）
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type VARCHAR(20),
    content TEXT,  -- 提取的文本内容
    metadata JSONB,
    uploaded_by BIGINT,

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 568** (sql, query):

```sql
-- 查看索引大小
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE indexname LIKE '%tsv%';

-- 查看索引扫描次数
SELECT

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 592** (sql, query):

```sql
-- 记录搜索日志
CREATE TABLE search_logs (
    id BIGSERIAL PRIMARY KEY,
    query TEXT,
    results_count INT,
    execution_time_ms REAL,
    searched_at TIMESTAMPTZ DEFAULT now()
);

-- 在搜索函数中记录
CREATE O
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 637** (sql, index):

```sql
   CREATE INDEX idx_tsv ON table_name USING GIN(tsv);

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 643** (sql, query):

```sql
   ALTER TABLE table_name ADD COLUMN tsv tsvector;
   -- 使用触发器自动更新

```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

### 43-SQL优化速查手册.md

**行 9** (sql, index):

```sql
-- ❌ 函数包裹索引列
WHERE LOWER(email) = 'test@example.com'

-- ✅ 使用表达式索引
CREATE INDEX idx_lower_email ON users(LOWER(email));

---

-- ❌ 隐式类型转换
WHERE user_id = '12345'  -- user_id是INT

-- ✅ 使用正确类型
WHERE use
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加索引构建性能测试

---

**行 49** (sql, query):

```sql
-- ❌ 子查询在SELECT中
SELECT
    u.id,
    (SELECT COUNT(*) FROM orders WHERE user_id = u.id) AS order_count
FROM users u;
-- 每行执行一次子查询！

-- ✅ 改写为JOIN
SELECT
    u.id,
    COUNT(o.id) AS order_count
FROM u
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 78** (sql, query):

```sql
-- ❌ OFFSET深度分页
SELECT * FROM products
ORDER BY id
LIMIT 20 OFFSET 100000;
-- 扫描100020行，只返回20行

-- ✅ Keyset分页
SELECT * FROM products
WHERE id > 100000  -- 上一页最后的ID
ORDER BY id
LIMIT 20;
-- 直接定位，只扫描20行
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 107** (sql, query):

```sql
-- ❌ 多次聚合查询
SELECT COUNT(*) FROM users WHERE status = 'active';
SELECT COUNT(*) FROM users WHERE status = 'inactive';

-- ✅ 一次查询
SELECT
    status,
    COUNT(*) AS count
FROM users
GROUP BY status;

-
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 139** (sql, query):

```sql
-- 大外表，小内表: IN更快
SELECT * FROM large_table
WHERE id IN (SELECT id FROM small_table);

-- 小外表，大内表: EXISTS更快
SELECT * FROM small_table st
WHERE EXISTS (
    SELECT 1 FROM large_table lt WHERE lt.id = st
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 159** (sql, bulk):

```sql
-- ❌ 循环单条INSERT
FOR i IN 1..10000 LOOP
    INSERT INTO users VALUES (i, ...);
END LOOP;
-- 10000次INSERT，慢

-- ✅ 批量VALUES
INSERT INTO users VALUES
(1, ...), (2, ...), (3, ...), ... (10000, ...);
-- 1次I
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）
- 添加批量操作性能测试

---

**行 199** (sql, query):

```sql
-- ❌ SELECT *
SELECT * FROM users;  -- 返回所有列

-- ✅ 只选需要的列
SELECT id, username, email FROM users;

---

-- ❌ 不必要的DISTINCT
SELECT DISTINCT * FROM (
    SELECT id, name FROM users WHERE status = 'active'
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---

**行 250** (sql, query):

```sql
-- 运行这个查询检查常见问题
SELECT
    '连接数' AS check,
    COUNT(*)||'/'||(SELECT setting FROM pg_settings WHERE name='max_connections') AS value
FROM pg_stat_activity

UNION ALL

SELECT
    '缓存命中率',
    ROUND(SU
```

**建议**:

- 添加查询性能测试（EXPLAIN ANALYZE）

---
