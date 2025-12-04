# 【📇速查卡】PostgreSQL混合数据库快速参考手册

> **创建日期**: 2025-01
> **用途**: 日常开发快速查阅
> **建议**: 打印或收藏为书签

---

## 📋 目录

1. [10种数据模型速查](#1-10种数据模型速查)
2. [4种查询语言速查](#2-4种查询语言速查)
3. [索引类型速查](#3-索引类型速查)
4. [性能优化速查](#4-性能优化速查)
5. [常用函数速查](#5-常用函数速查)
6. [故障排查速查](#6-故障排查速查)

---

## 1. 10种数据模型速查

### 1.1 关系型（原生）

```sql
-- 创建表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT
);

-- 外键
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id)
);

-- 索引
CREATE INDEX orders_user_id_idx ON orders(user_id);

-- JOIN查询
SELECT u.name, COUNT(o.id)
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
```

**详细指南**: PostgreSQL培训/基础文档

---

### 1.2 文档型（JSONB）

```sql
-- 创建表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL
);

-- 插入
INSERT INTO products (data) VALUES
('{"name": "Laptop", "price": 999, "specs": {"ram": 16, "cpu": "i7"}}');

-- 查询
SELECT data ->> 'name' AS name
FROM products
WHERE data @> '{"specs": {"ram": 16}}';

-- 索引
CREATE INDEX products_data_gin_idx ON products USING GIN(data);
```

**详细指南**: [JSON/JSONB高级查询完整指南](./PostgreSQL培训/03-数据类型/【深入】JSON-JSONB高级查询完整指南.md)

---

### 1.3 图数据库（Apache AGE）

```sql
-- 创建图
SELECT create_graph('social');

-- 创建节点和边
SELECT * FROM cypher('social', $$
    CREATE (a:Person {name: 'Alice'})
    CREATE (b:Person {name: 'Bob'})
    CREATE (a)-[:FRIEND]->(b)
$$) AS (result agtype);

-- 查询
SELECT * FROM cypher('social', $$
    MATCH (a:Person)-[:FRIEND]->(b:Person)
    RETURN a.name, b.name
$$) AS (person1 agtype, person2 agtype);

-- 最短路径
SELECT * FROM cypher('social', $$
    MATCH path = shortestPath((a)-[:FRIEND*]-(b))
    WHERE a.name = 'Alice' AND b.name = 'David'
    RETURN path
$$) AS (path agtype);
```

**详细指南**: [Apache AGE图数据库完整实战指南](./PostgreSQL培训/12-扩展开发/【深入】Apache AGE图数据库完整实战指南.md)

---

### 1.4 空间数据（PostGIS）

```sql
-- 创建扩展
CREATE EXTENSION postgis;

-- 创建表
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOMETRY(Point, 4326)
);

-- 插入（经纬度）
INSERT INTO locations (name, location) VALUES
('Beijing', ST_SetSRID(ST_MakePoint(116.4074, 39.9042), 4326));

-- 距离查询
SELECT name, ST_Distance(location::geography,
    ST_MakePoint(116.40, 39.90)::geography) / 1000 AS distance_km
FROM locations
ORDER BY distance_km
LIMIT 10;

-- 范围查询
SELECT name FROM locations
WHERE ST_DWithin(location::geography,
    ST_MakePoint(116.40, 39.90)::geography, 5000);

-- 索引
CREATE INDEX locations_location_gist_idx ON locations USING GIST(location);
```

**详细指南**: [PostGIS空间数据库完整实战指南](./PostgreSQL培训/03-数据类型/【深入】PostGIS空间数据库完整实战指南.md)

---

### 1.5 时序数据（TimescaleDB）

```sql
-- 创建扩展
CREATE EXTENSION timescaledb;

-- 创建表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    temperature DOUBLE PRECISION
);

-- 转换为Hypertable
SELECT create_hypertable('sensor_data', 'time',
    chunk_time_interval => INTERVAL '1 day');

-- 时间桶聚合
SELECT
    time_bucket('1 hour', time) AS hour,
    AVG(temperature) AS avg_temp
FROM sensor_data
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY hour;

-- 连续聚合（自动更新）
CREATE MATERIALIZED VIEW sensor_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', time) AS hour,
       AVG(temperature) AS avg_temp
FROM sensor_data
GROUP BY hour;

-- 数据压缩
ALTER TABLE sensor_data SET (timescaledb.compress);
SELECT add_compression_policy('sensor_data', compress_after => INTERVAL '7 days');
```

**详细指南**: [TimescaleDB时序数据库完整实战指南](./PostgreSQL培训/03-数据类型/【深入】TimescaleDB时序数据库完整实战指南.md)

---

### 1.6 全文搜索（FTS）

```sql
-- 创建表
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'D')
    ) STORED
);

-- 索引
CREATE INDEX articles_search_idx ON articles USING GIN(search_vector);

-- 搜索查询
SELECT id, title, ts_rank(search_vector, query) AS rank
FROM articles, to_tsquery('english', 'postgresql & search') query
WHERE search_vector @@ query
ORDER BY rank DESC;

-- 高亮
SELECT ts_headline('english', content,
    to_tsquery('english', 'postgresql'),
    'StartSel=<mark>, StopSel=</mark>'
) FROM articles;
```

**详细指南**: [PostgreSQL全文搜索完整实战指南](./PostgreSQL培训/04-查询/【深入】PostgreSQL全文搜索完整实战指南.md)

---

### 1.7-1.10 其他模型

| 模型 | 关键代码 | 文档 |
|------|---------|------|
| **键值（hstore）** | `CREATE EXTENSION hstore;`<br>`settings hstore` | 混合能力图谱 |
| **数组** | `tags TEXT[]`<br>`tags && ARRAY['db']` | 混合能力图谱 |
| **范围** | `period tstzrange`<br>`period @> NOW()` | 混合能力图谱 |
| **分布式（Citus）** | `SELECT create_distributed_table('events', 'tenant_id');` | [Citus指南](./PostgreSQL培训/05-部署架构/【深入】Citus分布式PostgreSQL完整实战指南.md) |

---

## 2. 4种查询语言速查

### 2.1 SQL（原生）

```sql
-- 基础查询
SELECT * FROM users WHERE age > 25;

-- JOIN
SELECT u.name, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id;

-- 子查询
SELECT * FROM orders
WHERE user_id IN (SELECT id FROM users WHERE city = 'Beijing');

-- CTE
WITH high_value AS (
    SELECT user_id, SUM(amount) AS total
    FROM orders
    GROUP BY user_id
    HAVING SUM(amount) > 10000
)
SELECT u.name, hv.total
FROM users u
JOIN high_value hv ON u.id = hv.user_id;
```

---

### 2.2 Cypher（Apache AGE）

```cypher
-- 创建
CREATE (a:Person {name: 'Alice'})-[:FRIEND]->(b:Person {name: 'Bob'})

-- 查询
MATCH (a:Person)-[:FRIEND]->(b:Person)
WHERE a.age > 25
RETURN a.name, b.name

-- 最短路径
MATCH path = shortestPath((a)-[:FRIEND*]-(b))
WHERE a.name = 'Alice' AND b.name = 'David'
RETURN path

-- 聚合
MATCH (p:Person)-[:FRIEND]->(friend)
RETURN p.name, COUNT(friend) AS friend_count
ORDER BY friend_count DESC
```

---

### 2.3 GraphQL（PostGraphile/Hasura）

```graphql
# 查询
query {
  users(first: 10, condition: {age: {greaterThan: 25}}) {
    nodes {
      name
      email
      posts {
        nodes {
          title
        }
      }
    }
  }
}

# 变更
mutation {
  createUser(input: {name: "Alice", email: "alice@example.com"}) {
    user {
      id
      name
    }
  }
}

# 订阅
subscription {
  posts(order_by: {created_at: desc}, limit: 10) {
    id
    title
    author {
      name
    }
  }
}
```

---

### 2.4 JSONPath（原生）

```sql
-- 路径查询
SELECT jsonb_path_query(data, '$.specs.cpu') FROM products;

-- 过滤
SELECT * FROM products
WHERE jsonb_path_exists(data, '$ ? (@.price > 100 && exists(@.tags))');

-- 数组查询
SELECT * FROM products
WHERE jsonb_path_exists(data, '$.tags[*] ? (@ == "electronics")');
```

---

## 3. 索引类型速查

| 索引类型 | 适用场景 | 创建语法 | 支持操作符 |
|---------|---------|---------|-----------|
| **B-tree** | 精确匹配、范围查询 | `CREATE INDEX ON table(column)` | `=, <, >, <=, >=, BETWEEN` |
| **GIN** | JSONB、数组、全文搜索 | `CREATE INDEX ON table USING GIN(column)` | `@>, <@, &&, ?` |
| **GiST** | 空间数据、范围类型 | `CREATE INDEX ON table USING GIST(column)` | `&&, @>, <@, ST_*` |
| **BRIN** | 大表、有序数据 | `CREATE INDEX ON table USING BRIN(column)` | `=, <, >, <=, >=` |
| **Hash** | 等值查询 | `CREATE INDEX ON table USING HASH(column)` | `=` |
| **SP-GiST** | 点数据、四叉树 | `CREATE INDEX ON table USING SPGIST(column)` | 空间操作符 |

### 常用索引场景

```sql
-- 外键
CREATE INDEX orders_user_id_idx ON orders(user_id);

-- 时间范围
CREATE INDEX orders_created_at_idx ON orders(created_at);

-- 复合索引
CREATE INDEX orders_user_created_idx ON orders(user_id, created_at DESC);

-- JSONB
CREATE INDEX products_data_gin_idx ON products USING GIN(data);

-- 全文搜索
CREATE INDEX articles_search_idx ON articles USING GIN(search_vector);

-- 空间
CREATE INDEX locations_geom_gist_idx ON locations USING GIST(geom);

-- 部分索引
CREATE INDEX active_users_idx ON users(email) WHERE deleted_at IS NULL;

-- 表达式索引
CREATE INDEX users_lower_email_idx ON users(LOWER(email));

-- 覆盖索引
CREATE INDEX orders_user_created_idx ON orders(user_id, created_at)
INCLUDE (amount, status);
```

---

## 4. 性能优化速查

### 4.1 诊断工具

```sql
-- 查看慢查询
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 查看表统计
SELECT schemaname, relname, n_live_tup, n_dead_tup, last_vacuum, last_analyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- 查看索引使用
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;  -- 找出未使用的索引

-- 查看锁等待
SELECT pid, wait_event_type, wait_event, state, query
FROM pg_stat_activity
WHERE wait_event IS NOT NULL;

-- EXPLAIN分析
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM large_table WHERE id = 123;
```

### 4.2 立即见效的优化

| 优化措施 | 投入 | 收益 | 代码 |
|---------|------|------|------|
| **创建索引** | 5分钟 | 100-1000x | `CREATE INDEX` |
| **ANALYZE** | 1分钟 | 2-10x | `ANALYZE;` |
| **VACUUM** | 5分钟 | 10-50% | `VACUUM ANALYZE;` |
| **调整shared_buffers** | 2分钟 | 20-30% | `shared_buffers = 4GB` |
| **批量操作** | 10分钟 | 10-100x | 使用COPY或批量INSERT |

### 4.3 配置速查

```text
# postgresql.conf（16GB RAM服务器）

# 内存
shared_buffers = 4GB              # 25% RAM
effective_cache_size = 12GB       # 75% RAM
work_mem = 64MB
maintenance_work_mem = 1GB

# WAL
wal_buffers = 16MB
checkpoint_completion_target = 0.9

# 查询优化
random_page_cost = 1.1            # SSD使用1.1
effective_io_concurrency = 200

# 并行
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

# 连接
max_connections = 200

# 日志（开发环境）
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000  # 记录>1秒的查询
```

---

## 5. 常用函数速查

### 5.1 JSONB函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `->` | 提取JSON（返回JSONB） | `data -> 'key'` |
| `->>` | 提取JSON（返回TEXT） | `data ->> 'key'` |
| `@>` | 包含 | `data @> '{"key": "value"}'` |
| `?` | 键存在 | `data ? 'key'` |
| `jsonb_set` | 设置值 | `jsonb_set(data, '{key}', '"value"')` |
| `jsonb_agg` | 聚合为数组 | `SELECT jsonb_agg(column)` |
| `jsonb_object_agg` | 聚合为对象 | `SELECT jsonb_object_agg(key, value)` |

### 5.2 PostGIS函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `ST_MakePoint` | 创建点 | `ST_MakePoint(116.40, 39.90)` |
| `ST_Distance` | 计算距离 | `ST_Distance(geom1::geography, geom2::geography)` |
| `ST_DWithin` | 范围内 | `ST_DWithin(geom, point, 5000)` |
| `ST_Contains` | 包含关系 | `ST_Contains(polygon, point)` |
| `ST_Buffer` | 缓冲区 | `ST_Buffer(geom::geography, 1000)` |
| `ST_Transform` | 坐标转换 | `ST_Transform(geom, 3857)` |

### 5.3 TimescaleDB函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `create_hypertable` | 创建超表 | `SELECT create_hypertable('table', 'time')` |
| `time_bucket` | 时间分桶 | `time_bucket('1 hour', time)` |
| `time_bucket_gapfill` | 填补缺失 | `time_bucket_gapfill('1 hour', time)` |
| `locf` | 前值填充 | `locf(AVG(value))` |
| `interpolate` | 线性插值 | `interpolate(AVG(value))` |
| `add_compression_policy` | 压缩策略 | `SELECT add_compression_policy('table', ...)` |

### 5.4 全文搜索函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `to_tsvector` | 文本→向量 | `to_tsvector('english', text)` |
| `to_tsquery` | 查询文本 | `to_tsquery('english', 'word1 & word2')` |
| `@@` | 匹配 | `tsvector @@ tsquery` |
| `ts_rank` | 排名 | `ts_rank(tsvector, tsquery)` |
| `ts_headline` | 高亮 | `ts_headline('english', text, query)` |

---

## 6. 故障排查速查

### 6.1 常见问题

#### 查询慢

```sql
-- 1. 检查是否使用索引
EXPLAIN ANALYZE SELECT * FROM table WHERE column = 'value';
-- 看到 "Seq Scan" → 需要创建索引

-- 2. 创建索引
CREATE INDEX table_column_idx ON table(column);

-- 3. 更新统计
ANALYZE table;

-- 4. 检查死行
SELECT relname, n_dead_tup FROM pg_stat_user_tables
WHERE n_dead_tup > 1000;

-- 5. VACUUM
VACUUM ANALYZE table;
```

#### 连接数满

```sql
-- 查看当前连接
SELECT COUNT(*) FROM pg_stat_activity;

-- 查看连接详情
SELECT pid, usename, application_name, state, query
FROM pg_stat_activity;

-- 终止空闲连接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND state_change < NOW() - INTERVAL '1 hour';

-- 调整max_connections
ALTER SYSTEM SET max_connections = 300;
SELECT pg_reload_conf();
```

#### 锁等待

```sql
-- 查看锁等待
SELECT
    blocked.pid AS blocked_pid,
    blocking.pid AS blocking_pid,
    blocked.query AS blocked_query,
    blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks blocked_locks ON blocked.pid = blocked_locks.pid
JOIN pg_locks blocking_locks ON blocked_locks.locktype = blocking_locks.locktype
JOIN pg_stat_activity blocking ON blocking.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted AND blocking_locks.granted;

-- 终止阻塞进程
SELECT pg_terminate_backend(blocking_pid);
```

#### 磁盘满

```bash
# 查看数据库大小
SELECT pg_size_pretty(pg_database_size('mydb'));

# 查看表大小
SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename::regclass))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;

# 清理
VACUUM FULL table_name;  # 回收空间（锁表）

# 删除旧数据
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days';
```

### 6.2 性能问题速查

| 症状 | 可能原因 | 解决方案 |
|------|---------|---------|
| **查询慢** | 缺失索引 | 创建索引 |
| | 统计过期 | `ANALYZE` |
| | 死行多 | `VACUUM` |
| **写入慢** | 索引过多 | 删除无用索引 |
| | WAL配置 | 调整checkpoint |
| **连接慢** | 连接数不足 | 增加max_connections |
| | 无连接池 | 使用PgBouncer |
| **磁盘满** | 数据增长 | 清理旧数据、分区 |
| | WAL堆积 | 检查归档 |

---

## 📚 快速链接

### 深度指南（按难度）

**入门**：

- [混合数据库能力图谱](./PostgreSQL培训/01-基础入门/【综合】PostgreSQL混合数据库完整能力图谱.md) ⭐

**基础**：

- [JSON/JSONB高级查询指南](./PostgreSQL培训/03-数据类型/【深入】JSON-JSONB高级查询完整指南.md)
- [PostgreSQL全文搜索指南](./PostgreSQL培训/04-查询/【深入】PostgreSQL全文搜索完整实战指南.md)

**进阶**：

- [Apache AGE图数据库指南](./PostgreSQL培训/12-扩展开发/【深入】Apache AGE图数据库完整实战指南.md)
- [PostGIS空间数据库指南](./PostgreSQL培训/03-数据类型/【深入】PostGIS空间数据库完整实战指南.md)
- [TimescaleDB时序数据库指南](./PostgreSQL培训/03-数据类型/【深入】TimescaleDB时序数据库完整实战指南.md)

**高级**：

- [Citus分布式PostgreSQL指南](./PostgreSQL培训/05-部署架构/【深入】Citus分布式PostgreSQL完整实战指南.md)
- [PostgreSQL + GraphQL完整实战指南](./PostgreSQL培训/06-应用开发/【深入】PostgreSQL+GraphQL完整实战指南.md)
- [慢查询优化实战手册](./PostgreSQL培训/11-性能调优/【案例集】PostgreSQL慢查询优化完整实战手册.md)

### 工具与资源

**官方**：

- PostgreSQL Documentation: <https://www.postgresql.org/docs/>
- PostGIS: <https://postgis.net/>
- TimescaleDB: <https://docs.timescale.com/>
- Apache AGE: <https://age.apache.org/>

**工具**：

- pgAdmin: GUI管理工具
- DBeaver: 跨平台数据库工具
- QGIS: GIS可视化（PostGIS）
- Grafana: 监控Dashboard（TimescaleDB）

**社区**：

- PostgreSQL中国社区
- GitHub: postgresql/postgres
- Stack Overflow: [postgresql]

---

## ✅ 使用建议

### 如何使用本速查卡

```text
📌 收藏为浏览器书签
📌 打印为A4纸（4页）
📌 放在开发环境显眼位置
📌 遇到问题先查速查卡
📌 需要深入再看详细指南
```

### 学习建议

```text
✅ 先掌握关系型（基础）
✅ 再学JSONB和全文搜索（最常用）
✅ 根据项目需求选择扩展模型
✅ 不要试图一次学完所有模型
✅ 边学边实践，以项目驱动学习
```

---

**文档状态**: ✅ 完成
**更新频率**: 根据PostgreSQL新版本更新
**建议**: 结合详细指南使用，速查卡作为快速参考

---

**快速参考，高效开发！** ⚡
