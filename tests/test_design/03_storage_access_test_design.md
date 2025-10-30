# 03_storage_access 模块测试设计

> **模块**：存储结构与访问路径  
> **设计日期**：2025 年 10 月 3 日  
> **目标测试数量**：30+场景  
> **预计完成时间**：Week 4（2025-10-11 至 2025-10-17）

---

## 📋 测试范围

### 模块内容回顾

- 存储结构（堆表、TOAST、FILLFACTOR、表膨胀）
- 索引类型（B-tree、Hash、GIN、GiST、BRIN、SP-GiST）
- 执行计划分析（EXPLAIN、扫描方法、JOIN 方法）
- 统计信息（ANALYZE、扩展统计）
- 维护操作（VACUUM、Autovacuum、REINDEX、CLUSTER）
- PostgreSQL 17 存储优化（B-tree 多值搜索、Streaming I/O、VACUUM 内存管理）

---

## 🎯 测试场景设计

### 1. 存储结构测试（6 个测试）

#### TEST-03-001: 堆表基本结构

**测试目的**：验证堆表的基本存储特性

```sql
-- TEST_BODY
CREATE TABLE test_heap_table (
    id SERIAL PRIMARY KEY,
    data TEXT
);

INSERT INTO test_heap_table (data)
SELECT 'Data ' || generate_series FROM generate_series(1, 1000);

-- 查看表占用的页数
SELECT
    relname,
    relpages,
    reltuples,
    pg_size_pretty(pg_relation_size('test_heap_table')) AS size
FROM pg_class
WHERE relname = 'test_heap_table';

-- ASSERTIONS
EXPECT_RESULT: SELECT relpages FROM pg_class WHERE relname = 'test_heap_table'; => > 0
EXPECT_ROWS: SELECT COUNT(*) FROM test_heap_table; => 1000

-- TEARDOWN
DROP TABLE IF EXISTS test_heap_table CASCADE;
```

---

#### TEST-03-002: TOAST - 超大字段存储

**测试目的**：验证 TOAST 机制

```sql
-- TEST_BODY
CREATE TABLE test_toast (
    id SERIAL PRIMARY KEY,
    small_text TEXT,
    large_text TEXT
);

-- 插入小文本（不会TOAST）
INSERT INTO test_toast (small_text, large_text) VALUES
('Small', repeat('A', 100));

-- 插入大文本（会TOAST）
INSERT INTO test_toast (small_text, large_text) VALUES
('Small', repeat('B', 10000));

-- 查看TOAST策略
SELECT
    attname,
    attstorage
FROM pg_attribute
WHERE attrelid = 'test_toast'::regclass
  AND attnum > 0
  AND attname IN ('small_text', 'large_text');

-- 查看TOAST表大小
SELECT
    pg_size_pretty(pg_relation_size('test_toast')) AS table_size,
    pg_size_pretty(pg_total_relation_size('test_toast') - pg_relation_size('test_toast')) AS toast_size;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_toast WHERE length(large_text) > 5000; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_toast CASCADE;
```

---

#### TEST-03-003: FILLFACTOR 与 HOT 更新

**测试目的**：验证 FILLFACTOR 和 HOT 更新机制

```sql
-- TEST_BODY
CREATE TABLE test_fillfactor (
    id SERIAL PRIMARY KEY,
    name TEXT,
    counter INT
) WITH (FILLFACTOR = 80);

-- 插入数据
INSERT INTO test_fillfactor (name, counter)
SELECT 'Name ' || generate_series, 0
FROM generate_series(1, 1000);

-- 查看HOT更新前的统计
SELECT
    n_tup_upd,
    n_tup_hot_upd
FROM pg_stat_user_tables
WHERE tablename = 'test_fillfactor';

-- 更新非索引列（应该产生HOT更新）
UPDATE test_fillfactor SET counter = counter + 1 WHERE id <= 500;

-- 查看HOT更新后的统计
SELECT
    n_tup_upd,
    n_tup_hot_upd,
    CASE WHEN n_tup_upd > 0
        THEN round(100.0 * n_tup_hot_upd / n_tup_upd, 2)
        ELSE 0
    END AS hot_update_ratio
FROM pg_stat_user_tables
WHERE tablename = 'test_fillfactor';

-- ASSERTIONS
EXPECT_RESULT: SELECT n_tup_hot_upd FROM pg_stat_user_tables WHERE tablename = 'test_fillfactor'; => > 0

-- TEARDOWN
DROP TABLE IF EXISTS test_fillfactor CASCADE;
```

---

#### TEST-03-004: 表膨胀检测

**测试目的**：验证表膨胀监控

```sql
-- SETUP
CREATE EXTENSION IF NOT EXISTS pgstattuple;

-- TEST_BODY
CREATE TABLE test_bloat (
    id SERIAL PRIMARY KEY,
    data TEXT
);

-- 插入数据
INSERT INTO test_bloat (data)
SELECT 'Data ' || generate_series FROM generate_series(1, 5000);

-- 更新所有行（产生死元组）
UPDATE test_bloat SET data = 'Updated ' || id;

-- 检查膨胀
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_relation_size('test_bloat')) AS table_size,
    round(dead_tuple_percent, 2) AS dead_tuple_percent
FROM pg_stat_user_tables t
JOIN LATERAL pgstattuple('test_bloat') p ON true
WHERE tablename = 'test_bloat';

-- ASSERTIONS
EXPECT_RESULT: SELECT dead_tuple_percent FROM pgstattuple('test_bloat'); => > 10.0

-- TEARDOWN
DROP TABLE IF EXISTS test_bloat CASCADE;
```

---

#### TEST-03-005: 页结构检查（pageinspect）

**测试目的**：验证页结构检查工具

```sql
-- SETUP
CREATE EXTENSION IF NOT EXISTS pageinspect;

-- TEST_BODY
CREATE TABLE test_page_inspect (
    id INT,
    data TEXT
);

INSERT INTO test_page_inspect VALUES (1, 'Data 1'), (2, 'Data 2');

-- 查看页头信息
SELECT * FROM page_header(get_raw_page('test_page_inspect', 0));

-- 查看页内元组
SELECT
    lp,
    lp_off,
    lp_len,
    t_xmin,
    t_xmax
FROM heap_page_items(get_raw_page('test_page_inspect', 0));

-- ASSERTIONS
EXPECT_RESULT: SELECT COUNT(*) FROM heap_page_items(get_raw_page('test_page_inspect', 0)); => >= 2

-- TEARDOWN
DROP TABLE IF EXISTS test_page_inspect CASCADE;
```

---

#### TEST-03-006: TOAST 策略修改

**测试目的**：验证 TOAST 策略修改

```sql
-- TEST_BODY
CREATE TABLE test_toast_strategy (
    id SERIAL PRIMARY KEY,
    content TEXT
);

-- 查看默认策略
SELECT attname, attstorage
FROM pg_attribute
WHERE attrelid = 'test_toast_strategy'::regclass
  AND attname = 'content';
-- 默认应该是 'x' (EXTENDED)

-- 修改为EXTERNAL策略
ALTER TABLE test_toast_strategy ALTER COLUMN content SET STORAGE EXTERNAL;

-- 验证策略已修改
SELECT attname, attstorage
FROM pg_attribute
WHERE attrelid = 'test_toast_strategy'::regclass
  AND attname = 'content';

-- ASSERTIONS
EXPECT_VALUE: SELECT attstorage FROM pg_attribute WHERE attrelid = 'test_toast_strategy'::regclass AND attname = 'content'; => 'e'

-- TEARDOWN
DROP TABLE IF EXISTS test_toast_strategy CASCADE;
```

---

### 2. 索引类型测试（8 个测试）

#### TEST-03-007: B-tree 索引 - 基本功能

**测试目的**：验证 B-tree 索引的基本功能

```sql
-- SETUP
CREATE TABLE test_btree (
    id SERIAL PRIMARY KEY,
    value INT,
    name TEXT
);

INSERT INTO test_btree (value, name)
SELECT generate_series, 'Name ' || generate_series
FROM generate_series(1, 10000);

-- TEST_BODY
CREATE INDEX idx_btree_value ON test_btree(value);

-- 验证索引被使用
EXPLAIN (FORMAT JSON) SELECT * FROM test_btree WHERE value = 5000;

-- 范围查询
EXPLAIN (FORMAT JSON) SELECT * FROM test_btree WHERE value BETWEEN 1000 AND 2000;

-- 排序优化
EXPLAIN (FORMAT JSON) SELECT * FROM test_btree ORDER BY value LIMIT 10;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_btree_value'; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_btree CASCADE;
```

---

#### TEST-03-008: B-tree 索引 - 复合索引与最左前缀

**测试目的**：验证复合索引的最左前缀原则

```sql
-- SETUP
CREATE TABLE test_composite_index (
    id SERIAL PRIMARY KEY,
    user_id INT,
    created_at TIMESTAMP,
    status VARCHAR(20)
);

INSERT INTO test_composite_index (user_id, created_at, status)
SELECT
    (random() * 100)::int,
    NOW() - (random() * 365 || ' days')::interval,
    (ARRAY['active', 'inactive', 'pending'])[1 + (random() * 2)::int]
FROM generate_series(1, 10000);

-- TEST_BODY
CREATE INDEX idx_composite ON test_composite_index(user_id, created_at, status);

-- 可以使用索引：user_id
EXPLAIN (FORMAT JSON) SELECT * FROM test_composite_index WHERE user_id = 50;

-- 可以使用索引：user_id + created_at
EXPLAIN (FORMAT JSON) SELECT * FROM test_composite_index
WHERE user_id = 50 AND created_at > NOW() - interval '30 days';

-- 不能使用索引：仅created_at（缺少user_id）
EXPLAIN (FORMAT JSON) SELECT * FROM test_composite_index
WHERE created_at > NOW() - interval '30 days';

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_composite'; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_composite_index CASCADE;
```

---

#### TEST-03-009: Hash 索引

**测试目的**：验证 Hash 索引功能

```sql
-- SETUP
CREATE TABLE test_hash (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid(),
    data TEXT
);

INSERT INTO test_hash (data)
SELECT 'Data ' || generate_series FROM generate_series(1, 5000);

-- TEST_BODY
CREATE INDEX idx_hash_uuid ON test_hash USING hash(uuid);

-- 验证索引类型
SELECT indexname, indexdef
FROM pg_indexes
WHERE indexname = 'idx_hash_uuid';

-- 等值查询（Hash索引支持）
SELECT uuid FROM test_hash LIMIT 1;
-- 使用该UUID进行查询
EXPLAIN (FORMAT JSON) SELECT * FROM test_hash WHERE uuid = (SELECT uuid FROM test_hash LIMIT 1);

-- ASSERTIONS
EXPECT_VALUE: SELECT indexdef FROM pg_indexes WHERE indexname = 'idx_hash_uuid'; => CONTAINS 'hash'

-- TEARDOWN
DROP TABLE IF EXISTS test_hash CASCADE;
```

---

#### TEST-03-010: GIN 索引 - JSONB 查询

**测试目的**：验证 GIN 索引用于 JSONB

```sql
-- SETUP
CREATE TABLE test_gin_jsonb (
    id SERIAL PRIMARY KEY,
    data JSONB
);

INSERT INTO test_gin_jsonb (data) VALUES
('{"name": "Alice", "tags": ["postgresql", "database"]}'::jsonb),
('{"name": "Bob", "tags": ["python", "programming"]}'::jsonb),
('{"name": "Charlie", "tags": ["postgresql", "python"]}'::jsonb);

-- TEST_BODY
CREATE INDEX idx_gin_data ON test_gin_jsonb USING GIN (data);

-- 包含查询
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT * FROM test_gin_jsonb WHERE data @> '{"tags": ["postgresql"]}'::jsonb;

-- 键存在查询
SELECT * FROM test_gin_jsonb WHERE data ? 'name';

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_gin_jsonb WHERE data @> '{"tags": ["postgresql"]}'::jsonb; => 2

-- TEARDOWN
DROP TABLE IF EXISTS test_gin_jsonb CASCADE;
```

---

#### TEST-03-011: GIN 索引 - 全文搜索

**测试目的**：验证 GIN 索引用于全文搜索

```sql
-- SETUP
CREATE TABLE test_gin_fts (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT
);

INSERT INTO test_gin_fts (title, content) VALUES
('PostgreSQL Tutorial', 'Learn PostgreSQL database management'),
('Python Programming', 'Introduction to Python programming'),
('Database Design', 'PostgreSQL and MySQL comparison');

-- TEST_BODY
CREATE INDEX idx_gin_fts ON test_gin_fts
USING GIN (to_tsvector('english', title || ' ' || content));

-- 全文搜索
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT * FROM test_gin_fts
WHERE to_tsvector('english', title || ' ' || content) @@ to_tsquery('postgresql');

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_gin_fts WHERE to_tsvector('english', title || ' ' || content) @@ to_tsquery('postgresql'); => 2

-- TEARDOWN
DROP TABLE IF EXISTS test_gin_fts CASCADE;
```

---

#### TEST-03-012: GiST 索引 - 范围类型

**测试目的**：验证 GiST 索引用于范围类型

```sql
-- TEST_BODY
CREATE TABLE test_gist_range (
    id SERIAL PRIMARY KEY,
    room_id INT,
    period TSTZRANGE
);

INSERT INTO test_gist_range (room_id, period) VALUES
(1, tstzrange('2025-10-01 10:00', '2025-10-01 12:00')),
(1, tstzrange('2025-10-01 14:00', '2025-10-01 16:00')),
(2, tstzrange('2025-10-01 10:00', '2025-10-01 13:00'));

-- 创建GiST索引
CREATE INDEX idx_gist_period ON test_gist_range USING GiST (period);

-- 范围重叠查询
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT * FROM test_gist_range
WHERE period && tstzrange('2025-10-01 11:00', '2025-10-01 15:00');

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_gist_range WHERE period && tstzrange('2025-10-01 11:00', '2025-10-01 15:00'); => 2

-- TEARDOWN
DROP TABLE IF EXISTS test_gist_range CASCADE;
```

---

#### TEST-03-013: BRIN 索引 - 时序数据

**测试目的**：验证 BRIN 索引用于时序数据

```sql
-- TEST_BODY
CREATE TABLE test_brin (
    id SERIAL,
    created_at TIMESTAMP DEFAULT NOW(),
    data TEXT
);

-- 按时间顺序插入大量数据
INSERT INTO test_brin (data)
SELECT 'Data ' || generate_series FROM generate_series(1, 50000);

-- 创建BRIN索引
CREATE INDEX idx_brin_created ON test_brin USING BRIN (created_at);

-- 创建B-tree索引对比
CREATE INDEX idx_btree_created ON test_brin (created_at);

-- 比较索引大小
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE tablename = 'test_brin'
ORDER BY indexname;

-- 范围查询
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT * FROM test_brin
WHERE created_at > NOW() - interval '1 hour';

-- ASSERTIONS
EXPECT_RESULT: SELECT pg_relation_size((SELECT indexrelid FROM pg_stat_user_indexes WHERE indexname = 'idx_brin_created')) < pg_relation_size((SELECT indexrelid FROM pg_stat_user_indexes WHERE indexname = 'idx_btree_created')); => true

-- TEARDOWN
DROP TABLE IF EXISTS test_brin CASCADE;
```

---

#### TEST-03-014: SP-GiST 索引 - IP 地址

**测试目的**：验证 SP-GiST 索引用于 IP 地址

```sql
-- TEST_BODY
CREATE TABLE test_spgist_ip (
    id SERIAL PRIMARY KEY,
    client_ip INET,
    access_time TIMESTAMP DEFAULT NOW()
);

-- 插入IP地址数据
INSERT INTO test_spgist_ip (client_ip)
SELECT ('192.168.' || (random() * 255)::int || '.' || (random() * 255)::int)::inet
FROM generate_series(1, 5000);

-- 创建SP-GiST索引
CREATE INDEX idx_spgist_ip ON test_spgist_ip USING SPGIST (client_ip);

-- IP范围查询
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT * FROM test_spgist_ip
WHERE client_ip << '192.168.1.0/24'::inet;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_spgist_ip'; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_spgist_ip CASCADE;
```

---

### 3. 执行计划分析（6 个测试）

#### TEST-03-015: EXPLAIN - 基本用法

**测试目的**：验证 EXPLAIN 各种选项

```sql
-- SETUP
CREATE TABLE test_explain (
    id SERIAL PRIMARY KEY,
    value INT,
    data TEXT
);

INSERT INTO test_explain (value, data)
SELECT generate_series, 'Data ' || generate_series
FROM generate_series(1, 1000);

CREATE INDEX idx_explain_value ON test_explain(value);

-- TEST_BODY
-- 基本EXPLAIN
EXPLAIN SELECT * FROM test_explain WHERE value = 500;

-- EXPLAIN ANALYZE（实际执行）
EXPLAIN (ANALYZE) SELECT * FROM test_explain WHERE value = 500;

-- EXPLAIN BUFFERS（缓冲区使用）
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM test_explain WHERE value BETWEEN 100 AND 200;

-- EXPLAIN VERBOSE（详细输出）
EXPLAIN (ANALYZE, VERBOSE) SELECT * FROM test_explain WHERE value > 900;

-- EXPLAIN JSON格式
EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM test_explain ORDER BY value LIMIT 10;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_explain WHERE value = 500; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_explain CASCADE;
```

---

#### TEST-03-016: 扫描方法 - Seq Scan vs Index Scan

**测试目的**：验证不同扫描方法的选择

```sql
-- SETUP
CREATE TABLE test_scan_methods (
    id SERIAL PRIMARY KEY,
    category VARCHAR(10),
    value INT
);

-- 插入数据（category有10个不同值）
INSERT INTO test_scan_methods (category, value)
SELECT
    'Cat' || ((generate_series - 1) % 10),
    generate_series
FROM generate_series(1, 10000);

CREATE INDEX idx_scan_category ON test_scan_methods(category);

-- TEST_BODY
-- 高选择性查询：应该使用Index Scan
EXPLAIN (ANALYZE) SELECT * FROM test_scan_methods WHERE category = 'Cat0';

-- 低选择性查询：应该使用Seq Scan
EXPLAIN (ANALYZE) SELECT * FROM test_scan_methods WHERE category IN ('Cat0', 'Cat1', 'Cat2', 'Cat3', 'Cat4');

-- 强制Seq Scan
SET enable_indexscan = off;
EXPLAIN (ANALYZE) SELECT * FROM test_scan_methods WHERE category = 'Cat0';
SET enable_indexscan = on;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_scan_methods WHERE category = 'Cat0'; => 1000

-- TEARDOWN
DROP TABLE IF EXISTS test_scan_methods CASCADE;
```

---

#### TEST-03-017: Index Only Scan（索引覆盖扫描）

**测试目的**：验证 Index Only Scan 优化

```sql
-- SETUP
CREATE TABLE test_index_only (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(100)
);

INSERT INTO test_index_only (email, name)
SELECT
    'user' || generate_series || '@example.com',
    'Name ' || generate_series
FROM generate_series(1, 10000);

-- TEST_BODY
-- 创建覆盖索引
CREATE INDEX idx_covering ON test_index_only(email, name);

-- VACUUM以更新可见性映射
VACUUM test_index_only;

-- 查询仅访问索引列（应该使用Index Only Scan）
EXPLAIN (ANALYZE, BUFFERS)
SELECT email, name FROM test_index_only WHERE email = 'user5000@example.com';

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_index_only WHERE email = 'user5000@example.com'; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_index_only CASCADE;
```

---

#### TEST-03-018: Bitmap Scan

**测试目的**：验证 Bitmap Scan 机制

```sql
-- SETUP
CREATE TABLE test_bitmap (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    status VARCHAR(20),
    value INT
);

INSERT INTO test_bitmap (category, status, value)
SELECT
    'Category' || ((generate_series - 1) % 20),
    (ARRAY['active', 'inactive'])[1 + (random())::int],
    generate_series
FROM generate_series(1, 50000);

CREATE INDEX idx_bitmap_category ON test_bitmap(category);
CREATE INDEX idx_bitmap_status ON test_bitmap(status);

-- TEST_BODY
-- 多个索引条件（应该使用Bitmap Scan）
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_bitmap
WHERE category IN ('Category0', 'Category1', 'Category2');

-- ASSERTIONS
EXPECT_RESULT: SELECT COUNT(*) FROM test_bitmap WHERE category IN ('Category0', 'Category1', 'Category2'); => > 0

-- TEARDOWN
DROP TABLE IF EXISTS test_bitmap CASCADE;
```

---

#### TEST-03-019: JOIN 方法 - Nested Loop vs Hash Join

**测试目的**：验证不同 JOIN 方法

```sql
-- SETUP
CREATE TABLE test_join_small (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE test_join_large (
    id SERIAL PRIMARY KEY,
    ref_id INT,
    data TEXT
);

INSERT INTO test_join_small
SELECT generate_series, 'Name ' || generate_series
FROM generate_series(1, 100);

INSERT INTO test_join_large (ref_id, data)
SELECT
    1 + (random() * 99)::int,
    'Data ' || generate_series
FROM generate_series(1, 10000);

CREATE INDEX idx_join_ref ON test_join_large(ref_id);

-- TEST_BODY
-- 小表JOIN大表（应该使用Hash Join或Nested Loop）
EXPLAIN (ANALYZE)
SELECT * FROM test_join_small s
JOIN test_join_large l ON s.id = l.ref_id
WHERE s.id < 10;

-- 强制Nested Loop
SET enable_hashjoin = off;
SET enable_mergejoin = off;
EXPLAIN (ANALYZE)
SELECT * FROM test_join_small s
JOIN test_join_large l ON s.id = l.ref_id
WHERE s.id < 10;

-- 恢复设置
SET enable_hashjoin = on;
SET enable_mergejoin = on;

-- ASSERTIONS
EXPECT_RESULT: SELECT COUNT(*) FROM test_join_small s JOIN test_join_large l ON s.id = l.ref_id WHERE s.id < 10; => > 0

-- TEARDOWN
DROP TABLE IF EXISTS test_join_small CASCADE;
DROP TABLE IF EXISTS test_join_large CASCADE;
```

---

#### TEST-03-020: Merge Join

**测试目的**：验证 Merge Join

```sql
-- SETUP
CREATE TABLE test_merge_a (
    id INT PRIMARY KEY,
    value INT
);

CREATE TABLE test_merge_b (
    id INT PRIMARY KEY,
    value INT
);

-- 插入有序数据
INSERT INTO test_merge_a
SELECT generate_series, generate_series * 10
FROM generate_series(1, 5000);

INSERT INTO test_merge_b
SELECT generate_series, generate_series * 20
FROM generate_series(1, 5000);

-- TEST_BODY
-- 有序JOIN（应该使用Merge Join）
EXPLAIN (ANALYZE)
SELECT * FROM test_merge_a a
JOIN test_merge_b b ON a.id = b.id
ORDER BY a.id;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_merge_a a JOIN test_merge_b b ON a.id = b.id; => 5000

-- TEARDOWN
DROP TABLE IF EXISTS test_merge_a CASCADE;
DROP TABLE IF EXISTS test_merge_b CASCADE;
```

---

### 4. 统计信息测试（4 个测试）

#### TEST-03-021: ANALYZE - 统计信息收集

**测试目的**：验证 ANALYZE 功能

```sql
-- SETUP
CREATE TABLE test_analyze (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    value INT
);

INSERT INTO test_analyze (category, value)
SELECT
    'Category' || ((generate_series - 1) % 10),
    generate_series
FROM generate_series(1, 10000);

-- TEST_BODY
-- 执行ANALYZE
ANALYZE test_analyze;

-- 查看统计信息
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename = 'test_analyze'
  AND attname IN ('category', 'value');

-- 查看上次ANALYZE时间
SELECT
    last_analyze,
    last_autoanalyze,
    n_live_tup
FROM pg_stat_user_tables
WHERE tablename = 'test_analyze';

-- ASSERTIONS
EXPECT_RESULT: SELECT last_analyze FROM pg_stat_user_tables WHERE tablename = 'test_analyze'; => IS NOT NULL

-- TEARDOWN
DROP TABLE IF EXISTS test_analyze CASCADE;
```

---

#### TEST-03-022: 统计目标（statistics target）

**测试目的**：验证统计目标设置

```sql
-- SETUP
CREATE TABLE test_statistics_target (
    id SERIAL PRIMARY KEY,
    high_cardinality_col UUID DEFAULT gen_random_uuid(),
    data TEXT
);

INSERT INTO test_statistics_target (data)
SELECT 'Data ' || generate_series FROM generate_series(1, 10000);

-- TEST_BODY
-- 提高统计目标
ALTER TABLE test_statistics_target
ALTER COLUMN high_cardinality_col SET STATISTICS 1000;

-- 执行ANALYZE
ANALYZE test_statistics_target;

-- 查看统计信息
SELECT
    attname,
    attstattarget
FROM pg_attribute
WHERE attrelid = 'test_statistics_target'::regclass
  AND attname = 'high_cardinality_col';

-- ASSERTIONS
EXPECT_VALUE: SELECT attstattarget FROM pg_attribute WHERE attrelid = 'test_statistics_target'::regclass AND attname = 'high_cardinality_col'; => 1000

-- TEARDOWN
DROP TABLE IF EXISTS test_statistics_target CASCADE;
```

---

#### TEST-03-023: 扩展统计 - 多列相关性

**测试目的**：验证扩展统计功能

```sql
-- TEST_BODY
CREATE TABLE test_extended_stats (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(10)
);

-- 插入相关数据（城市和州有强相关性）
INSERT INTO test_extended_stats (city, state, zip_code) VALUES
('San Francisco', 'CA', '94102'),
('Los Angeles', 'CA', '90001'),
('San Diego', 'CA', '92101'),
('New York', 'NY', '10001'),
('Buffalo', 'NY', '14201');

-- 创建扩展统计
CREATE STATISTICS stats_city_state (dependencies)
ON city, state
FROM test_extended_stats;

-- 执行ANALYZE
ANALYZE test_extended_stats;

-- 查看扩展统计
SELECT * FROM pg_statistic_ext WHERE stxname = 'stats_city_state';

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_statistic_ext WHERE stxname = 'stats_city_state'; => 1

-- TEARDOWN
DROP STATISTICS IF EXISTS stats_city_state;
DROP TABLE IF EXISTS test_extended_stats CASCADE;
```

---

#### TEST-03-024: pg_stats 视图查询

**测试目的**：验证统计信息视图查询

```sql
-- SETUP
CREATE TABLE test_pg_stats (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20),
    value INT
);

INSERT INTO test_pg_stats (status, value)
SELECT
    (ARRAY['active', 'inactive', 'pending'])[1 + (random() * 2)::int],
    (random() * 1000)::int
FROM generate_series(1, 10000);

ANALYZE test_pg_stats;

-- TEST_BODY
-- 查看列统计信息
SELECT
    attname,
    n_distinct,
    null_frac,
    avg_width,
    most_common_vals,
    most_common_freqs
FROM pg_stats
WHERE tablename = 'test_pg_stats'
  AND attname = 'status';

-- ASSERTIONS
EXPECT_RESULT: SELECT n_distinct FROM pg_stats WHERE tablename = 'test_pg_stats' AND attname = 'status'; => > 0

-- TEARDOWN
DROP TABLE IF EXISTS test_pg_stats CASCADE;
```

---

### 5. 维护操作测试（4 个测试)

#### TEST-03-025: VACUUM - 死元组清理

**测试目的**：验证 VACUUM 清理死元组

```sql
-- SETUP
CREATE TABLE test_vacuum (
    id SERIAL PRIMARY KEY,
    data TEXT
);

INSERT INTO test_vacuum (data)
SELECT 'Data ' || generate_series FROM generate_series(1, 5000);

-- TEST_BODY
-- 更新所有行（产生死元组）
UPDATE test_vacuum SET data = 'Updated ' || id;

-- 查看死元组数量
SELECT n_dead_tup FROM pg_stat_user_tables WHERE tablename = 'test_vacuum';

-- 执行VACUUM
VACUUM test_vacuum;

-- 再次查看死元组数量
SELECT n_dead_tup FROM pg_stat_user_tables WHERE tablename = 'test_vacuum';

-- ASSERTIONS
EXPECT_RESULT: SELECT n_dead_tup FROM pg_stat_user_tables WHERE tablename = 'test_vacuum'; => < 100

-- TEARDOWN
DROP TABLE IF EXISTS test_vacuum CASCADE;
```

---

#### TEST-03-026: Autovacuum 配置

**测试目的**：验证表级 Autovacuum 配置

```sql
-- TEST_BODY
CREATE TABLE test_autovacuum (
    id SERIAL PRIMARY KEY,
    data TEXT
);

-- 设置表级Autovacuum参数
ALTER TABLE test_autovacuum SET (
    autovacuum_vacuum_threshold = 100,
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_threshold = 50,
    autovacuum_analyze_scale_factor = 0.05
);

-- 查看表的Autovacuum配置
SELECT
    relname,
    reloptions
FROM pg_class
WHERE relname = 'test_autovacuum';

-- ASSERTIONS
EXPECT_RESULT: SELECT reloptions FROM pg_class WHERE relname = 'test_autovacuum'; => IS NOT NULL

-- TEARDOWN
DROP TABLE IF EXISTS test_autovacuum CASCADE;
```

---

#### TEST-03-027: REINDEX - 索引重建

**测试目的**：验证索引重建

```sql
-- SETUP
CREATE TABLE test_reindex (
    id SERIAL PRIMARY KEY,
    value INT,
    data TEXT
);

INSERT INTO test_reindex (value, data)
SELECT generate_series, 'Data ' || generate_series
FROM generate_series(1, 10000);

CREATE INDEX idx_reindex_value ON test_reindex(value);

-- TEST_BODY
-- 查看索引大小
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size_before
FROM pg_stat_user_indexes
WHERE indexname = 'idx_reindex_value';

-- 重建索引
REINDEX INDEX idx_reindex_value;

-- 再次查看索引大小
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size_after
FROM pg_stat_user_indexes
WHERE indexname = 'idx_reindex_value';

-- 并发重建（不锁表）
REINDEX INDEX CONCURRENTLY idx_reindex_value;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_reindex_value'; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_reindex CASCADE;
```

---

#### TEST-03-028: CLUSTER - 表重组

**测试目的**：验证 CLUSTER 表重组

```sql
-- SETUP
CREATE TABLE test_cluster (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP,
    data TEXT
);

-- 插入乱序数据
INSERT INTO test_cluster (created_at, data)
SELECT
    NOW() - (random() * 365 || ' days')::interval,
    'Data ' || generate_series
FROM generate_series(1, 10000);

CREATE INDEX idx_cluster_created ON test_cluster(created_at);

-- TEST_BODY
-- 按created_at重组表
CLUSTER test_cluster USING idx_cluster_created;

-- 查看表是否已CLUSTER
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_relation_size(schemaname || '.' || tablename)) AS table_size
FROM pg_tables
WHERE tablename = 'test_cluster';

-- 查看相关性（应该接近1或-1）
SELECT
    attname,
    correlation
FROM pg_stats
WHERE tablename = 'test_cluster'
  AND attname = 'created_at';

-- ASSERTIONS
EXPECT_RESULT: SELECT ABS(correlation) FROM pg_stats WHERE tablename = 'test_cluster' AND attname = 'created_at'; => > 0.9

-- TEARDOWN
DROP TABLE IF EXISTS test_cluster CASCADE;
```

---

### 6. PostgreSQL 17 存储优化（2 个测试）

#### TEST-03-029: B-tree 多值搜索优化（PG17）

**测试目的**：验证 PG17 B-tree 多值搜索优化

```sql
-- SETUP
CREATE TABLE test_pg17_btree (
    id INT PRIMARY KEY,
    value INT
);

INSERT INTO test_pg17_btree
SELECT generate_series, generate_series * 10
FROM generate_series(1, 100000);

-- TEST_BODY
-- IN查询（PG17优化）
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_pg17_btree
WHERE id IN (100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 10000, 20000, 30000, 40000, 50000);

-- 查看缓冲区使用
SELECT
    COUNT(*) AS result_count,
    MAX(value) AS max_value
FROM test_pg17_btree
WHERE id IN (100, 200, 300, 400, 500);

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_pg17_btree WHERE id IN (100, 200, 300, 400, 500); => 5

-- TEARDOWN
DROP TABLE IF EXISTS test_pg17_btree CASCADE;
```

---

#### TEST-03-030: VACUUM 内存管理改进（PG17）

**测试目的**：验证 PG17 VACUUM 内存管理改进

```sql
-- SETUP
CREATE TABLE test_pg17_vacuum (
    id SERIAL PRIMARY KEY,
    data TEXT
);

INSERT INTO test_pg17_vacuum (data)
SELECT 'Data ' || generate_series FROM generate_series(1, 50000);

-- 更新大量行（产生死元组）
UPDATE test_pg17_vacuum SET data = 'Updated ' || id WHERE id % 2 = 0;

-- TEST_BODY
-- 查看VACUUM前的统计
SELECT
    n_dead_tup,
    last_vacuum
FROM pg_stat_user_tables
WHERE tablename = 'test_pg17_vacuum';

-- 设置较大的maintenance_work_mem
SET maintenance_work_mem = '256MB';

-- 执行VACUUM（PG17优化内存管理）
VACUUM (VERBOSE, ANALYZE, INDEX_CLEANUP AUTO) test_pg17_vacuum;

-- 查看VACUUM后的统计
SELECT
    n_dead_tup,
    last_vacuum,
    vacuum_count
FROM pg_stat_user_tables
WHERE tablename = 'test_pg17_vacuum';

-- 恢复设置
RESET maintenance_work_mem;

-- ASSERTIONS
EXPECT_RESULT: SELECT n_dead_tup FROM pg_stat_user_tables WHERE tablename = 'test_pg17_vacuum'; => < 1000

-- TEARDOWN
DROP TABLE IF EXISTS test_pg17_vacuum CASCADE;
```

---

## 📊 测试统计

### 测试数量

| 类别                       | 测试数量  |
| -------------------------- | --------- |
| **存储结构测试**           | 6 个      |
| **索引类型测试**           | 8 个      |
| **执行计划分析**           | 6 个      |
| **统计信息测试**           | 4 个      |
| **维护操作测试**           | 4 个      |
| **PostgreSQL 17 存储优化** | 2 个      |
| **总计**                   | **30 个** |

### 覆盖率

- ✅ 存储结构（堆表、TOAST、FILLFACTOR、HOT 更新、表膨胀、页结构）
- ✅ 索引类型（B-tree、Hash、GIN、GiST、BRIN、SP-GiST）
- ✅ 执行计划（EXPLAIN 选项、扫描方法、JOIN 方法）
- ✅ 统计信息（ANALYZE、统计目标、扩展统计、pg_stats）
- ✅ 维护操作（VACUUM、Autovacuum、REINDEX、CLUSTER）
- ✅ PostgreSQL 17 优化（B-tree 多值搜索、VACUUM 内存管理）

---

## 🔧 实现建议

### 测试框架增强需求

1. **EXPLAIN 解析支持**

   - 解析 EXPLAIN JSON 输出
   - 验证执行计划节点类型（Seq Scan、Index Scan 等）
   - 验证索引是否被使用

2. **性能断言**

   - `EXPECT_TIME`：验证执行时间
   - `EXPECT_BUFFERS`：验证缓冲区使用
   - `EXPECT_PLAN_NODE`：验证执行计划节点

3. **扩展支持**
   - 自动安装测试所需扩展（pageinspect、pgstattuple）
   - 检查扩展是否可用

### 测试执行注意事项

1. **数据量**：测试使用适中的数据量（1K-50K 行），平衡覆盖度和执行速度
2. **索引维护**：测试后正确清理索引和表
3. **统计信息**：某些测试需要 ANALYZE 更新统计信息

---

## 📅 实施计划

### Week 4（2025-10-11 至 2025-10-17）

**Day 1-3**：测试框架增强（8 小时）

- 实现 EXPLAIN 解析支持
- 实现性能断言
- 实现扩展自动安装

**Day 4-6**：测试用例实现（12 小时）

- 实现 30 个测试用例
- 验证所有扩展可用
- 测试执行计划验证

**Day 7**：文档完善（2 小时）

- 更新测试用例索引
- 编写执行计划测试指南

---

**设计者**：PostgreSQL_modern Project Team  
**设计日期**：2025 年 10 月 3 日  
**目标版本**：v1.0  
**状态**：设计完成，待实现 ✅
