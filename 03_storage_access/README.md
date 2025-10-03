# 03_storage_access — 存储结构与访问路径

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **模块完整度**：⭐⭐⭐⭐ 85%（已深化，持续完善）  
> **适合人群**：理解PostgreSQL存储原理、索引选型、执行计划优化、维护操作

---

## 📋 目录

- [03\_storage\_access — 存储结构与访问路径](#03_storage_access--存储结构与访问路径)
  - [📋 目录](#-目录)
  - [模块定位与边界](#模块定位与边界)
    - [主题边界](#主题边界)
    - [知识地图](#知识地图)
  - [1. 存储结构](#1-存储结构)
    - [1.1 堆表（Heap Table）](#11-堆表heap-table)
    - [1.2 TOAST（超大字段）](#12-toast超大字段)
    - [1.3 FILLFACTOR与页填充](#13-fillfactor与页填充)
    - [1.4 表膨胀（Bloat）](#14-表膨胀bloat)
  - [2. 索引类型详解](#2-索引类型详解)
    - [2.1 B-tree索引](#21-b-tree索引)
    - [2.2 Hash索引](#22-hash索引)
    - [2.3 GIN索引](#23-gin索引)
    - [2.4 GiST索引](#24-gist索引)
    - [2.5 BRIN索引](#25-brin索引)
    - [2.6 SP-GiST索引](#26-sp-gist索引)
    - [2.7 索引选型决策树](#27-索引选型决策树)
  - [3. 执行计划分析](#3-执行计划分析)
    - [3.1 EXPLAIN基础](#31-explain基础)
    - [3.2 扫描方法](#32-扫描方法)
      - [Seq Scan（顺序扫描）](#seq-scan顺序扫描)
      - [Index Scan（索引扫描）](#index-scan索引扫描)
      - [Index Only Scan（索引覆盖扫描）](#index-only-scan索引覆盖扫描)
      - [Bitmap Scan（位图扫描）](#bitmap-scan位图扫描)
    - [3.3 JOIN方法](#33-join方法)
      - [Nested Loop Join（嵌套循环）](#nested-loop-join嵌套循环)
      - [Hash Join（哈希连接）](#hash-join哈希连接)
      - [Merge Join（归并连接）](#merge-join归并连接)
    - [3.4 执行计划优化案例](#34-执行计划优化案例)
      - [案例1：索引失效导致全表扫描](#案例1索引失效导致全表扫描)
      - [案例2：Bitmap Recheck过多](#案例2bitmap-recheck过多)
      - [案例3：不必要的排序](#案例3不必要的排序)
  - [4. 统计信息](#4-统计信息)
    - [4.1 ANALYZE原理](#41-analyze原理)
    - [4.2 扩展统计](#42-扩展统计)
    - [4.3 统计信息查看](#43-统计信息查看)
  - [5. 维护操作](#5-维护操作)
    - [5.1 VACUUM详解](#51-vacuum详解)
    - [5.2 Autovacuum配置](#52-autovacuum配置)
    - [5.3 REINDEX索引维护](#53-reindex索引维护)
    - [5.4 CLUSTER表重组](#54-cluster表重组)
  - [6. PostgreSQL 17存储优化](#6-postgresql-17存储优化)
    - [6.1 B-tree多值搜索优化](#61-b-tree多值搜索优化)
    - [6.2 Streaming I/O（顺序读取优化）](#62-streaming-io顺序读取优化)
    - [6.3 VACUUM内存管理改进](#63-vacuum内存管理改进)
  - [7. 性能调优实践](#7-性能调优实践)
    - [7.1 索引优化清单](#71-索引优化清单)
    - [7.2 执行计划诊断清单](#72-执行计划诊断清单)
    - [7.3 维护操作清单](#73-维护操作清单)
  - [8. 权威参考](#8-权威参考)
    - [官方文档](#官方文档)
    - [扩展与工具](#扩展与工具)
    - [学习资源](#学习资源)
  - [9. Checklist](#9-checklist)
    - [存储设计检查清单](#存储设计检查清单)
    - [索引设计检查清单](#索引设计检查清单)
    - [执行计划诊断检查清单](#执行计划诊断检查清单)
    - [维护操作检查清单](#维护操作检查清单)

---

## 模块定位与边界

### 主题边界

- **核心内容**：存储结构、索引类型、执行计划、统计信息、维护操作
- **深度定位**：从底层存储到查询优化，涵盖6种索引选型、执行计划诊断、Autovacuum调优
- **PostgreSQL 17对齐**：B-tree多值搜索优化、streaming I/O、VACUUM内存管理改进

### 知识地图

```text
存储结构
    ├── 堆表（Heap Table、页结构、元组）
    ├── TOAST（超大字段、压缩、外部存储）
    ├── FILLFACTOR（页填充因子、HOT更新）
    └── 表膨胀（Bloat监控、原因、治理）
        ↓
索引类型
    ├── B-tree（默认、范围查询、排序）
    ├── Hash（等值查询）
    ├── GIN（全文搜索、JSON、数组）
    ├── GiST（几何、范围、全文）
    ├── BRIN（大表、按序存储、时序数据）
    └── SP-GiST（非平衡结构、IP地址）
        ↓
执行计划
    ├── 扫描方法（Seq Scan、Index Scan、Bitmap Scan）
    ├── JOIN方法（Nested Loop、Hash Join、Merge Join）
    ├── EXPLAIN选项（ANALYZE、BUFFERS、VERBOSE）
    └── 性能瓶颈识别
        ↓
统计信息
    ├── ANALYZE（采样、柱状图、MCV）
    ├── 扩展统计（多列相关性、NDV、函数依赖）
    └── 统计信息视图（pg_stats、pg_statistic）
        ↓
维护操作
    ├── VACUUM（死元组清理、XID冻结）
    ├── Autovacuum（触发条件、配置优化）
    ├── REINDEX（索引膨胀、并发重建）
    └── CLUSTER（物理排序、提升缓存命中）
```

---

## 1. 存储结构

### 1.1 堆表（Heap Table）

**堆表特点**：

- 无序存储（插入顺序，非物理排序）
- 每行（元组）有隐藏的系统列（xmin、xmax、ctid等）
- 以8KB页（Page/Block）为单位管理

**页结构**：

```text
+------------------+
| Page Header      | 24 bytes（页头）
+------------------+
| Item Pointers    | 每个指针4 bytes（行指针数组）
+------------------+
| Free Space       | 空闲空间
+------------------+
| Items (Tuples)   | 实际数据行
+------------------+
| Special Space    | 索引专用空间
+------------------+
```

**查看页信息**：

```sql
-- 查看表占用的页数
SELECT relpages, reltuples, pg_size_pretty(pg_relation_size('table_name'))
FROM pg_class
WHERE relname = 'table_name';

-- 使用pageinspect扩展查看页详情
CREATE EXTENSION IF NOT EXISTS pageinspect;

-- 查看页头信息
SELECT * FROM page_header(get_raw_page('table_name', 0));

-- 查看页内所有元组
SELECT lp, lp_off, lp_len, t_xmin, t_xmax, t_ctid
FROM heap_page_items(get_raw_page('table_name', 0));
```

### 1.2 TOAST（超大字段）

**TOAST（The Oversized-Attribute Storage Technique）**：

- 当行大小超过约2KB（页的1/4），PostgreSQL自动使用TOAST
- 大字段被压缩或移到专门的TOAST表

**TOAST策略**：

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **PLAIN** | 不压缩、不TOAST | 小字段（如int、date） |
| **EXTENDED** | 先压缩再TOAST | **默认策略**，适用text、jsonb |
| **EXTERNAL** | 不压缩但TOAST | 已压缩数据（如图片、视频） |
| **MAIN** | 先压缩，尽量不TOAST | 经常访问的中等大小字段 |

```sql
-- 查看列的TOAST策略
SELECT attname, attstorage
FROM pg_attribute
WHERE attrelid = 'table_name'::regclass
  AND attnum > 0;
-- 输出：p=PLAIN, e=EXTENDED, m=MAIN, x=EXTERNAL

-- 修改TOAST策略
ALTER TABLE documents ALTER COLUMN content SET STORAGE EXTERNAL;

-- 查看TOAST表大小
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
  pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS toast_indexes_size
FROM pg_tables
WHERE tablename = 'your_table';
```

**TOAST优化建议**：

1. **大字段分离**：将大字段（如文件内容）拆到独立表
2. **使用EXTERNAL**：已压缩数据（JPEG、MP4）避免重复压缩
3. **避免SELECT \***：减少TOAST字段的不必要读取

### 1.3 FILLFACTOR与页填充

**FILLFACTOR（填充因子）**：

- 控制页的填充百分比（默认100%）
- 预留空间用于HOT（Heap-Only Tuple）更新

**HOT更新**：

- 如果更新后的行能放在同一页，且不修改索引列，则为HOT更新
- HOT更新不需要更新索引，性能更好

```sql
-- 创建表时设置FILLFACTOR
CREATE TABLE users (
  id bigserial PRIMARY KEY,
  name text,
  email text,
  updated_count int
) WITH (FILLFACTOR = 80); -- 预留20%空间

-- 修改已有表的FILLFACTOR
ALTER TABLE users SET (FILLFACTOR = 80);
VACUUM FULL users; -- 需要重建表

-- 查看HOT更新统计
SELECT
  schemaname,
  tablename,
  n_tup_upd AS updates,
  n_tup_hot_upd AS hot_updates,
  CASE WHEN n_tup_upd > 0 
    THEN round(100.0 * n_tup_hot_upd / n_tup_upd, 2) 
    ELSE 0 
  END AS hot_update_ratio
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_tup_upd DESC;
```

**FILLFACTOR设置建议**：

- **高频UPDATE表**：70-80（预留空间给HOT更新）
- **只读/少更新表**：100（默认，充分利用空间）
- **索引**：90（B-tree默认90，平衡空间与分裂）

### 1.4 表膨胀（Bloat）

**膨胀原因**：

1. VACUUM未及时清理死元组
2. 长事务阻止VACUUM清理
3. 高频UPDATE/DELETE操作

**监控表膨胀**：

```sql
-- 简化的膨胀检查（近似值）
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
  round(100 * (pg_total_relation_size(schemaname||'.'||tablename)::numeric - 
    pg_relation_size(schemaname||'.'||tablename)::numeric) / 
    NULLIF(pg_total_relation_size(schemaname||'.'||tablename), 0), 2) AS bloat_ratio
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 精确的膨胀检查（使用pgstattuple扩展）
CREATE EXTENSION IF NOT EXISTS pgstattuple;

SELECT
  schemaname || '.' || tablename AS table_name,
  pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
  round(dead_tuple_percent, 2) AS dead_tuple_percent,
  round(free_percent, 2) AS free_percent
FROM pg_stat_user_tables t
JOIN LATERAL pgstattuple(schemaname||'.'||tablename) p ON true
WHERE schemaname = 'public'
ORDER BY pg_relation_size(schemaname||'.'||tablename) DESC;
```

**膨胀治理**：

```sql
-- 1. 常规VACUUM（清理死元组，不回收空间给操作系统）
VACUUM table_name;

-- 2. VACUUM FULL（重建表，回收空间，需要AccessExclusiveLock）
VACUUM FULL table_name; -- ⚠️ 锁表，生产慎用

-- 3. pg_repack（在线重建，推荐）
-- 需要安装pg_repack扩展
-- pg_repack -d database_name -t table_name
```

---

## 2. 索引类型详解

### 2.1 B-tree索引

**特性**：

- PostgreSQL默认索引类型
- 支持等值查询、范围查询、排序
- 叶子节点有序，适合ORDER BY

**适用场景**：

- `=`, `<`, `<=`, `>`, `>=`, `BETWEEN`
- `IN`, `IS NULL`, `IS NOT NULL`
- `LIKE 'prefix%'`（前缀匹配）
- `ORDER BY`

**PostgreSQL 17优化**：

- **多值搜索优化**：`WHERE id IN (1,2,3,...)` 性能提升
- **更高效的并发插入**：减少B-tree页分裂锁竞争

```sql
-- 创建B-tree索引
CREATE INDEX idx_users_email ON users(email);

-- 多列B-tree索引（遵循最左前缀原则）
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);
-- 可用于：WHERE user_id = ?
-- 可用于：WHERE user_id = ? AND created_at > ?
-- 不能用于：WHERE created_at > ?（缺少user_id）

-- 表达式索引
CREATE INDEX idx_users_lower_email ON users(lower(email));
SELECT * FROM users WHERE lower(email) = 'alice@example.com';

-- 部分索引
CREATE INDEX idx_orders_pending ON orders(created_at) WHERE status = 'pending';
SELECT * FROM orders WHERE status = 'pending' AND created_at < now() - interval '1 day';
```

### 2.2 Hash索引

**特性**：

- 仅支持等值查询（`=`）
- PostgreSQL 10+支持WAL日志（可用于复制和恢复）
- 通常比B-tree略快，但功能受限

**适用场景**：

- 纯等值查询（无范围、排序需求）
- 高基数列（如UUID）

```sql
-- 创建Hash索引
CREATE INDEX idx_users_uuid_hash ON users USING hash(uuid);

-- 查询必须是等值
SELECT * FROM users WHERE uuid = 'xxx-xxx-xxx';
```

**注意**：大多数场景B-tree足够好，Hash索引优势不明显。

### 2.3 GIN索引

**GIN（Generalized Inverted Index，通用倒排索引）**：

- 适合多值列（数组、JSON、全文搜索）
- 查询快，但构建和更新慢

**适用场景**：

- 数组包含查询（`@>`, `<@`, `&&`）
- JSON查询（`@>`, `?`, `?&`, `?|`）
- 全文搜索（`@@`）
- 三元组模糊搜索（pg_trgm）

```sql
-- 数组GIN索引
CREATE INDEX idx_posts_tags ON posts USING gin(tags);
SELECT * FROM posts WHERE tags @> ARRAY['postgresql', 'database'];

-- JSON GIN索引
CREATE INDEX idx_users_settings ON users USING gin(settings);
SELECT * FROM users WHERE settings @> '{"theme": "dark"}';

-- 全文搜索GIN索引
CREATE INDEX idx_documents_content_fts ON documents USING gin(to_tsvector('english', content));
SELECT * FROM documents WHERE to_tsvector('english', content) @@ to_tsquery('postgresql');

-- pg_trgm模糊搜索
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_users_name_trgm ON users USING gin(name gin_trgm_ops);
SELECT * FROM users WHERE name ILIKE '%alice%'; -- 可以使用索引
```

### 2.4 GiST索引

**GiST（Generalized Search Tree，通用搜索树）**：

- 平衡树结构，支持多种数据类型
- 比GIN更通用，但通常性能稍慢

**适用场景**：

- 几何数据（PostGIS）
- 范围类型（`&&`, `@>`, `<@`）
- 全文搜索（替代GIN）
- K近邻搜索（KNN）

```sql
-- 几何GiST索引（PostGIS）
CREATE INDEX idx_locations_geom ON locations USING gist(geom);
SELECT * FROM locations WHERE ST_DWithin(geom, ST_MakePoint(120, 30), 1000);

-- 范围类型GiST索引
CREATE TABLE reservations (
  id serial PRIMARY KEY,
  room_id int,
  period tstzrange
);
CREATE INDEX idx_reservations_period ON reservations USING gist(period);
SELECT * FROM reservations WHERE period && tstzrange('2025-10-03', '2025-10-05');

-- K近邻搜索（<->距离运算符）
SELECT * FROM locations ORDER BY geom <-> ST_MakePoint(120, 30) LIMIT 10;
```

### 2.5 BRIN索引

**BRIN（Block Range Index，块范围索引）**：

- 极小的索引大小（通常<1% 表大小）
- 适合大表且数据按某列物理排序

**适用场景**：

- 时序数据（按时间递增插入）
- 日志表（按日期排序）
- 大表的范围查询

```sql
-- BRIN索引（适合时序数据）
CREATE INDEX idx_logs_created_at_brin ON logs USING brin(created_at);

-- 查看BRIN索引大小（对比B-tree）
SELECT
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE tablename = 'logs';

-- BRIN索引参数调优
CREATE INDEX idx_logs_created_brin ON logs USING brin(created_at) WITH (pages_per_range = 128);
-- pages_per_range: 每个范围的页数（默认128），越小索引越大但精度越高
```

**BRIN vs B-tree对比**：

| 维度 | BRIN | B-tree |
|------|------|--------|
| 索引大小 | 极小（<1% 表大小） | 大（5-20% 表大小） |
| 构建速度 | 快 | 慢 |
| 查询性能 | 需要扫描多个块 | 精确定位 |
| 适用场景 | 大表+物理有序 | 通用 |

### 2.6 SP-GiST索引

**SP-GiST（Space-Partitioned GiST）**：

- 支持非平衡数据结构（如四叉树、前缀树）
- 适合特殊数据类型

**适用场景**：

- IP地址（inet、cidr）
- 电话号码
- 文本前缀搜索

```sql
-- IP地址SP-GiST索引
CREATE INDEX idx_connections_ip ON connections USING spgist(client_ip);
SELECT * FROM connections WHERE client_ip << '192.168.1.0/24'::inet;

-- 文本前缀SP-GiST索引
CREATE INDEX idx_words_text_spgist ON words USING spgist(word);
SELECT * FROM words WHERE word ^@ 'post'; -- 前缀匹配
```

### 2.7 索引选型决策树

```text
查询类型？
├─ 等值查询（=）
│  ├─ 单列 → B-tree（默认）或Hash（略快）
│  └─ 多列 → B-tree（复合索引）
│
├─ 范围查询（<, >, BETWEEN）
│  ├─ 小/中表 → B-tree
│  └─ 大表+物理有序 → BRIN（索引小）
│
├─ 排序（ORDER BY）
│  └─ B-tree（叶子节点有序）
│
├─ 模糊搜索（LIKE '%...%'）
│  └─ GIN + pg_trgm
│
├─ 数组/JSON查询
│  └─ GIN（倒排索引）
│
├─ 全文搜索
│  └─ GIN（to_tsvector）
│
├─ 几何/地理查询
│  └─ GiST（PostGIS）
│
├─ 范围类型查询
│  └─ GiST（tstzrange, int4range等）
│
├─ IP地址查询
│  └─ SP-GiST
│
└─ K近邻搜索
   └─ GiST（<->运算符）
```

---

## 3. 执行计划分析

### 3.1 EXPLAIN基础

**EXPLAIN选项**：

```sql
-- 基本执行计划（不实际执行）
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';

-- ANALYZE：实际执行并返回真实统计
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'alice@example.com';

-- BUFFERS：显示缓冲区使用情况
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE email = 'alice@example.com';

-- VERBOSE：显示详细输出列表
EXPLAIN (ANALYZE, VERBOSE) SELECT * FROM users WHERE email = 'alice@example.com';

-- COSTS OFF：隐藏代价估算（便于测试）
EXPLAIN (COSTS OFF) SELECT * FROM users WHERE email = 'alice@example.com';

-- FORMAT JSON：JSON格式输出（便于程序解析）
EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM users WHERE email = 'alice@example.com';
```

**执行计划输出解读**：

```text
Seq Scan on users  (cost=0.00..15.50 rows=1 width=100) (actual time=0.015..0.023 rows=1 loops=1)
  Filter: (email = 'alice@example.com'::text)
  Rows Removed by Filter: 499
Planning Time: 0.123 ms
Execution Time: 0.045 ms

解读：
- Seq Scan：顺序扫描（全表扫描）
- cost=0.00..15.50：启动代价..总代价
- rows=1：预计返回1行
- width=100：平均行宽100字节
- actual time=0.015..0.023：实际启动时间..总时间（毫秒）
- rows=1：实际返回1行
- loops=1：执行1次
- Rows Removed by Filter: 499：过滤掉499行
```

### 3.2 扫描方法

#### Seq Scan（顺序扫描）

- 全表扫描，按物理顺序读取所有页
- 适合：小表、返回大部分行

```sql
EXPLAIN ANALYZE
SELECT * FROM small_table WHERE status = 'active';
-- Seq Scan on small_table (cost=0.00..1.05 rows=5 width=40)
```

#### Index Scan（索引扫描）

- 通过索引查找，然后回表获取完整行
- 适合：返回少量行、需要排序

```sql
CREATE INDEX idx_users_email ON users(email);

EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'alice@example.com';
-- Index Scan using idx_users_email on users (cost=0.29..8.30 rows=1 width=100)
```

#### Index Only Scan（索引覆盖扫描）

- 所有需要的列都在索引中，无需回表
- 最快的扫描方式（需要VACUUM维护可见性映射）

```sql
CREATE INDEX idx_users_email_name ON users(email, name);

EXPLAIN ANALYZE
SELECT email, name FROM users WHERE email = 'alice@example.com';
-- Index Only Scan using idx_users_email_name on users (cost=0.29..4.30 rows=1 width=64)
--   Heap Fetches: 0  （无需回表）
```

#### Bitmap Scan（位图扫描）

- 先扫描索引生成位图，再按物理顺序访问表
- 适合：返回中等数量行、多个索引条件

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id IN (1,2,3,4,5);
-- Bitmap Heap Scan on orders (cost=12.14..156.39 rows=50 width=100)
--   Recheck Cond: (user_id = ANY ('{1,2,3,4,5}'::integer[]))
--   -> Bitmap Index Scan on idx_orders_user_id (cost=0.00..12.12 rows=50 width=0)
--         Index Cond: (user_id = ANY ('{1,2,3,4,5}'::integer[]))
```

### 3.3 JOIN方法

#### Nested Loop Join（嵌套循环）

- 外表每行与内表所有匹配行连接
- 适合：小表JOIN小表、有索引

```sql
EXPLAIN ANALYZE
SELECT * FROM small_table a
JOIN another_small_table b ON a.id = b.ref_id;
-- Nested Loop (cost=0.29..16.38 rows=10 width=200)
```

#### Hash Join（哈希连接）

- 构建哈希表，再探测匹配
- 适合：中大表JOIN、等值连接

```sql
EXPLAIN ANALYZE
SELECT * FROM users u
JOIN orders o ON u.id = o.user_id;
-- Hash Join (cost=15.50..356.00 rows=1000 width=200)
--   Hash Cond: (o.user_id = u.id)
--   -> Seq Scan on orders o (cost=0.00..250.00 rows=10000 width=100)
--   -> Hash (cost=10.50..10.50 rows=500 width=100)
--         -> Seq Scan on users u (cost=0.00..10.50 rows=500 width=100)
```

#### Merge Join（归并连接）

- 两表都已排序，按序合并
- 适合：大表JOIN大表、有序数据

```sql
EXPLAIN ANALYZE
SELECT * FROM table1 a
JOIN table2 b ON a.sorted_col = b.sorted_col
ORDER BY a.sorted_col;
-- Merge Join (cost=0.56..560.00 rows=5000 width=200)
--   Merge Cond: (a.sorted_col = b.sorted_col)
--   -> Index Scan using idx_table1_sorted on table1 a
--   -> Index Scan using idx_table2_sorted on table2 b
```

### 3.4 执行计划优化案例

#### 案例1：索引失效导致全表扫描

```sql
-- ❌ 问题：函数调用导致索引失效
EXPLAIN ANALYZE
SELECT * FROM users WHERE upper(email) = 'ALICE@EXAMPLE.COM';
-- Seq Scan on users (cost=0.00..15.50 rows=5 width=100)

-- ✅ 解决方案1：表达式索引
CREATE INDEX idx_users_upper_email ON users(upper(email));
EXPLAIN ANALYZE
SELECT * FROM users WHERE upper(email) = 'ALICE@EXAMPLE.COM';
-- Index Scan using idx_users_upper_email (cost=0.29..8.30 rows=1 width=100)

-- ✅ 解决方案2：不使用函数
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = lower('ALICE@EXAMPLE.COM');
-- Index Scan using idx_users_email (cost=0.29..8.30 rows=1 width=100)
```

#### 案例2：Bitmap Recheck过多

```sql
-- ❌ 问题：Bitmap Recheck消耗大量CPU
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM large_table WHERE status = 'active' AND score > 80;
-- Bitmap Heap Scan on large_table (cost=100..5000 rows=50000 width=100)
--   Recheck Cond: ((status = 'active') AND (score > 80))
--   Rows Removed by Recheck: 40000  ← 大量重检查
--   Heap Blocks: exact=1000 lossy=9000  ← lossy块多

-- ✅ 解决方案：复合索引
CREATE INDEX idx_large_table_status_score ON large_table(status, score);
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM large_table WHERE status = 'active' AND score > 80;
-- Index Scan using idx_large_table_status_score (cost=0.42..1523.50 rows=50000 width=100)
```

#### 案例3：不必要的排序

```sql
-- ❌ 问题：额外的Sort节点
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 123 ORDER BY created_at DESC LIMIT 10;
-- Limit (cost=150.00..150.02 rows=10 width=100)
--   -> Sort (cost=150.00..152.50 rows=1000 width=100)  ← 额外排序
--         Sort Key: created_at DESC
--         -> Bitmap Heap Scan on orders (cost=12.00..100.00 rows=1000 width=100)

-- ✅ 解决方案：索引包含排序列
CREATE INDEX idx_orders_user_created_desc ON orders(user_id, created_at DESC);
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 123 ORDER BY created_at DESC LIMIT 10;
-- Limit (cost=0.42..1.67 rows=10 width=100)
--   -> Index Scan using idx_orders_user_created_desc (cost=0.42..125.00 rows=1000 width=100)
```

---

## 4. 统计信息

### 4.1 ANALYZE原理

**ANALYZE工作原理**：

1. 随机采样表的一部分行（默认300 * default_statistics_target）
2. 计算统计信息：
   - **n_distinct**：唯一值数量
   - **histogram_bounds**：柱状图（数据分布）
   - **most_common_vals**：最常见值（MCV）
   - **most_common_freqs**：最常见值频率
3. 存储到pg_statistic（通过pg_stats视图查看）

```sql
-- 手动执行ANALYZE
ANALYZE table_name;

-- 仅分析特定列
ANALYZE table_name(column1, column2);

-- 查看上次ANALYZE时间
SELECT
  schemaname,
  tablename,
  last_analyze,
  last_autoanalyze,
  n_live_tup,
  n_dead_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY last_analyze NULLS FIRST;
```

**统计目标（statistics target）**：

```sql
-- 查看默认统计目标
SHOW default_statistics_target; -- 100（默认）

-- 提高列的统计目标（更精确的统计，但ANALYZE更慢）
ALTER TABLE users ALTER COLUMN email SET STATISTICS 1000;

-- 对高基数列或分布不均的列提高统计目标
ALTER TABLE orders ALTER COLUMN user_id SET STATISTICS 500;

-- 重新ANALYZE生效
ANALYZE users;
```

### 4.2 扩展统计

**扩展统计（PostgreSQL 10+）**：

- 处理多列相关性、函数依赖、唯一值数量（NDV）

```sql
-- 创建扩展统计（多列相关性）
CREATE STATISTICS stats_orders_user_product
ON user_id, product_id
FROM orders;

ANALYZE orders;

-- 查看扩展统计
SELECT * FROM pg_statistic_ext WHERE stxname = 'stats_orders_user_product';

-- 函数依赖示例
CREATE STATISTICS stats_addresses_city_state
(dependencies)
ON city, state
FROM addresses;
-- 告诉优化器：知道城市就能确定州

-- NDV（n-distinct）示例
CREATE STATISTICS stats_logs_user_action
(ndistinct)
ON user_id, action_type
FROM logs;
-- 改进对(user_id, action_type)组合唯一值的估算
```

### 4.3 统计信息查看

```sql
-- 查看列统计信息
SELECT
  schemaname,
  tablename,
  attname AS column_name,
  n_distinct,  -- 唯一值数量（-1表示所有唯一）
  null_frac,   -- NULL值比例
  avg_width,   -- 平均宽度（字节）
  correlation  -- 物理存储顺序与逻辑顺序的相关性（-1到1）
FROM pg_stats
WHERE schemaname = 'public' AND tablename = 'orders';

-- 查看最常见值（MCV）
SELECT
  tablename,
  attname,
  most_common_vals,
  most_common_freqs
FROM pg_stats
WHERE tablename = 'orders' AND attname = 'status';
```

---

## 5. 维护操作

### 5.1 VACUUM详解

**VACUUM的作用**：

1. 清理死元组，回收空间（不归还给操作系统）
2. 更新统计信息（仅fsm和vm）
3. 冻结旧事务ID，防止XID回卷
4. 更新可见性映射（Visibility Map），支持Index Only Scan

**VACUUM变体**：

```sql
-- 常规VACUUM（不锁表，可并发）
VACUUM table_name;

-- VACUUM FULL（重建表，锁表，回收空间给OS）
VACUUM FULL table_name; -- ⚠️ 需要AccessExclusiveLock

-- VACUUM FREEZE（强制冻结）
VACUUM FREEZE table_name;

-- VACUUM ANALYZE（清理+更新统计）
VACUUM ANALYZE table_name;

-- PostgreSQL 13+ 并行VACUUM
VACUUM (PARALLEL 4) large_table;

-- PostgreSQL 17优化：更好的内存管理
VACUUM (INDEX_CLEANUP AUTO, TRUNCATE ON) table_name;
```

**VACUUM监控**：

```sql
-- 查看VACUUM进度（PostgreSQL 13+）
SELECT
  pid,
  datname,
  relid::regclass AS table_name,
  phase,
  heap_blks_total,
  heap_blks_scanned,
  heap_blks_vacuumed,
  index_vacuum_count,
  max_dead_tuples,
  num_dead_tuples,
  round(100.0 * heap_blks_scanned / NULLIF(heap_blks_total, 0), 2) AS progress_percent
FROM pg_stat_progress_vacuum;
```

### 5.2 Autovacuum配置

**Autovacuum触发条件**：

```text
触发VACUUM：dead_tuples > autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor * reltuples
触发ANALYZE：changed_tuples > autovacuum_analyze_threshold + autovacuum_analyze_scale_factor * reltuples
```

**全局配置**：

```sql
-- 查看Autovacuum配置
SHOW autovacuum;                         -- on
SHOW autovacuum_max_workers;             -- 3（默认）
SHOW autovacuum_naptime;                 -- 1min（默认）
SHOW autovacuum_vacuum_threshold;        -- 50（默认）
SHOW autovacuum_vacuum_scale_factor;     -- 0.2（默认，20%）
SHOW autovacuum_analyze_threshold;       -- 50
SHOW autovacuum_analyze_scale_factor;    -- 0.1（默认，10%）
SHOW autovacuum_vacuum_cost_delay;       -- 2ms（默认）
SHOW autovacuum_vacuum_cost_limit;       -- 200（默认）

-- 修改全局配置（postgresql.conf）
-- autovacuum_max_workers = 6
-- autovacuum_naptime = 30s
```

**表级配置（覆盖全局设置）**：

```sql
-- 高频更新表：更积极的Autovacuum
ALTER TABLE hot_table SET (
  autovacuum_vacuum_threshold = 100,
  autovacuum_vacuum_scale_factor = 0.05,  -- 5%触发
  autovacuum_analyze_scale_factor = 0.05
);

-- 大表：提高cost_limit，加快VACUUM
ALTER TABLE large_table SET (
  autovacuum_vacuum_cost_limit = 2000,  -- 10倍
  autovacuum_vacuum_cost_delay = 0      -- 无延迟
);

-- 禁用特定表的Autovacuum（不推荐）
ALTER TABLE temp_table SET (autovacuum_enabled = false);
```

**Autovacuum监控**：

```sql
-- 查看Autovacuum历史
SELECT
  schemaname,
  tablename,
  last_vacuum,
  last_autovacuum,
  last_analyze,
  last_autoanalyze,
  vacuum_count,
  autovacuum_count,
  analyze_count,
  autoanalyze_count,
  n_live_tup,
  n_dead_tup,
  round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_tuple_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- 查找从未Autovacuum的表
SELECT schemaname, tablename, n_dead_tup
FROM pg_stat_user_tables
WHERE last_autovacuum IS NULL AND n_dead_tup > 0
ORDER BY n_dead_tup DESC;
```

### 5.3 REINDEX索引维护

**何时需要REINDEX**：

1. 索引膨胀（大量UPDATE/DELETE后）
2. 索引损坏（极少发生）
3. 修改索引FILLFACTOR后

```sql
-- 重建单个索引
REINDEX INDEX idx_users_email;

-- 重建表的所有索引
REINDEX TABLE users;

-- 重建数据库的所有索引
REINDEX DATABASE database_name;

-- 并发重建（不锁表，PostgreSQL 12+）
REINDEX INDEX CONCURRENTLY idx_users_email;

-- 等效于
DROP INDEX CONCURRENTLY idx_users_email;
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

**索引膨胀检查**：

```sql
-- 查看索引膨胀（使用pgstattuple）
SELECT
  schemaname || '.' || tablename AS table_name,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
  round((100 * (1 - avg_leaf_density / 100)), 2) AS bloat_ratio
FROM pg_stat_user_indexes
JOIN LATERAL pgstatindex(indexrelid) ON true
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 5.4 CLUSTER表重组

**CLUSTER**：按索引物理排序表，提升缓存局部性。

```sql
-- 按索引重组表（需要AccessExclusiveLock）
CLUSTER users USING idx_users_created_at;

-- 重组所有已CLUSTER的表
CLUSTER;

-- 查看表是否已CLUSTER
SELECT
  schemaname,
  tablename,
  indexname AS clustered_index
FROM pg_indexes
WHERE schemaname = 'public';
```

**CLUSTER vs VACUUM FULL**：

| 操作 | 锁 | 空间回收 | 物理排序 | 推荐场景 |
|------|-----|---------|---------|---------|
| CLUSTER | AccessExclusiveLock | ✅ | ✅ | 时序数据（按时间排序） |
| VACUUM FULL | AccessExclusiveLock | ✅ | ❌ | 严重膨胀的表 |
| pg_repack | ShareUpdateExclusiveLock | ✅ | ✅ | 在线重组（推荐） |

---

## 6. PostgreSQL 17存储优化

### 6.1 B-tree多值搜索优化

```sql
-- PostgreSQL 17优化了IN查询
EXPLAIN ANALYZE
SELECT * FROM users WHERE id IN (1,2,3,4,5,10,20,30,40,50);
-- Index Scan using users_pkey (cost=0.42..16.50 rows=10 width=100)
-- PG17：更高效的B-tree遍历，减少重复访问
```

### 6.2 Streaming I/O（顺序读取优化）

```sql
-- PostgreSQL 17改进了顺序扫描的I/O性能
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM large_table WHERE created_at > '2025-01-01';
-- Seq Scan on large_table (cost=0.00..100000.00 rows=1000000 width=100)
--   Buffers: shared read=50000  ← PG17: streaming I/O减少I/O调用
```

### 6.3 VACUUM内存管理改进

```sql
-- PostgreSQL 17允许VACUUM使用更多内存
SHOW maintenance_work_mem; -- 64MB（默认）

-- 提高maintenance_work_mem加速VACUUM/REINDEX
SET maintenance_work_mem = '1GB';
VACUUM large_table;
```

---

## 7. 性能调优实践

### 7.1 索引优化清单

- [ ] 查询的WHERE/JOIN/ORDER BY列有索引
- [ ] 多列索引遵循最左前缀原则
- [ ] 避免过多索引（每个索引都有写入代价）
- [ ] 使用部分索引减小索引大小
- [ ] 高基数列提高statistics_target
- [ ] 定期REINDEX CONCURRENTLY清理膨胀

### 7.2 执行计划诊断清单

- [ ] 使用`EXPLAIN (ANALYZE, BUFFERS)`而非仅EXPLAIN
- [ ] 关注actual time vs estimated rows差异
- [ ] 查找Seq Scan（应该Index Scan的场景）
- [ ] 检查Rows Removed by Filter数量
- [ ] 监控Buffers: shared read（磁盘I/O）
- [ ] 避免嵌套循环JOIN大表

### 7.3 维护操作清单

- [ ] Autovacuum已启用且配置合理
- [ ] 监控long-running事务（阻碍VACUUM）
- [ ] 大表配置表级Autovacuum参数
- [ ] 定期检查表膨胀（dead_tuple_ratio < 10%）
- [ ] 时序数据考虑BRIN索引
- [ ] 生产环境避免VACUUM FULL（使用pg_repack）

---

## 8. 权威参考

### 官方文档

- **索引类型**：<https://www.postgresql.org/docs/17/indexes-types.html>
- **执行计划**：<https://www.postgresql.org/docs/17/using-explain.html>
- **VACUUM**：<https://www.postgresql.org/docs/17/routine-vacuuming.html>
- **统计信息**：<https://www.postgresql.org/docs/17/planner-stats.html>
- **pg_stat_statements**：<https://www.postgresql.org/docs/17/pgstatstatements.html>

### 扩展与工具

- **pgstattuple**：表/索引膨胀检查
- **pageinspect**：页结构检查
- **pg_repack**：在线表重组
- **pg_trgm**：模糊搜索
- **PostGIS**：地理空间索引

### 学习资源

- **Use The Index, Luke!**：<https://use-the-index-luke.com/>（索引优化圣经）
- **PostgreSQL Explain Visualizer**：<https://explain.dalibo.com/>（可视化执行计划）

---

## 9. Checklist

### 存储设计检查清单

- [ ] 大字段（>2KB）考虑TOAST策略或拆表
- [ ] 高频UPDATE表设置FILLFACTOR=80
- [ ] 时序数据按时间分区
- [ ] 监控表膨胀（定期检查dead_tuple_ratio）

### 索引设计检查清单

- [ ] 每个查询的WHERE条件有对应索引
- [ ] 多列索引顺序：等值>范围>排序
- [ ] 避免函数破坏索引（或创建表达式索引）
- [ ] 部分索引用于过滤条件固定的场景
- [ ] LIKE '%...%'使用GIN + pg_trgm
- [ ] JSON/数组查询使用GIN索引
- [ ] 大表+物理有序数据考虑BRIN

### 执行计划诊断检查清单

- [ ] 使用`EXPLAIN (ANALYZE, BUFFERS)`
- [ ] 检查是否使用正确的索引
- [ ] 确认JOIN方法合理（小表Nested Loop，大表Hash Join）
- [ ] 避免不必要的排序（索引已排序）
- [ ] 监控Buffers: shared read（磁盘I/O）
- [ ] 对比estimated rows vs actual rows（统计信息准确性）

### 维护操作检查清单

- [ ] Autovacuum已启用（autovacuum = on）
- [ ] 高频更新表降低autovacuum_vacuum_scale_factor
- [ ] 大表提高autovacuum_vacuum_cost_limit
- [ ] 定期执行ANALYZE（尤其数据分布变化后）
- [ ] 监控vacuum_count和autovacuum_count
- [ ] 长事务监控（阻碍VACUUM/XID冻结）
- [ ] 索引膨胀>30%时REINDEX CONCURRENTLY

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**下一步**：查看 [04_modern_features](../04_modern_features/README.md) 探索现代特性
