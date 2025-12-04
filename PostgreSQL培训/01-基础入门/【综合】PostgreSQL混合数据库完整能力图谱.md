# 【综合】PostgreSQL混合数据库完整能力图谱

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 12+
> **难度等级**: ⭐⭐⭐⭐⭐ 专家综合 | **文档类型**: 能力总览

---

## 📋 目录

- [【综合】PostgreSQL混合数据库完整能力图谱](#综合postgresql混合数据库完整能力图谱)
  - [📋 目录](#-目录)
  - [1. PostgreSQL：真正的混合数据库](#1-postgresql真正的混合数据库)
    - [1.1 什么是混合数据库？](#11-什么是混合数据库)
    - [1.2 能力全景图](#12-能力全景图)
  - [2. 关系型数据库（核心）](#2-关系型数据库核心)
    - [2.1 标准SQL能力](#21-标准sql能力)
    - [2.2 高级特性](#22-高级特性)
  - [3. 文档数据库（JSONB）](#3-文档数据库jsonb)
    - [3.1 核心能力](#31-核心能力)
    - [3.2 与关系型结合](#32-与关系型结合)
  - [4. 图数据库（Apache AGE）](#4-图数据库apache-age)
    - [4.1 核心能力](#41-核心能力)
    - [4.2 与关系型结合](#42-与关系型结合)
  - [5. 空间数据库（PostGIS）](#5-空间数据库postgis)
    - [5.1 核心能力](#51-核心能力)
    - [5.2 与关系型结合](#52-与关系型结合)
  - [6. 时序数据库（TimescaleDB）](#6-时序数据库timescaledb)
    - [6.1 核心能力](#61-核心能力)
  - [7. 键值存储（hstore）](#7-键值存储hstore)
    - [7.1 hstore基础](#71-hstore基础)
    - [7.2 hstore vs JSONB](#72-hstore-vs-jsonb)
  - [8. 全文搜索引擎](#8-全文搜索引擎)
    - [8.1 核心能力](#81-核心能力)
    - [8.2 多语言支持](#82-多语言支持)
  - [9. 数组与范围类型](#9-数组与范围类型)
    - [9.1 数组类型](#91-数组类型)
    - [9.2 范围类型](#92-范围类型)
  - [10. 分布式数据库（Citus）](#10-分布式数据库citus)
    - [10.1 核心能力](#101-核心能力)
  - [11. 混合查询实战](#11-混合查询实战)
    - [11.1 案例1：智能推荐系统](#111-案例1智能推荐系统)
    - [11.2 案例2：实时物流追踪](#112-案例2实时物流追踪)
    - [11.3 案例3：社交电商平台](#113-案例3社交电商平台)
  - [12. 性能对比](#12-性能对比)
    - [12.1 数据模型性能](#121-数据模型性能)
    - [12.2 混合查询性能](#122-混合查询性能)
  - [📊 完整能力矩阵](#-完整能力矩阵)
    - [数据模型支持](#数据模型支持)
    - [查询语言支持](#查询语言支持)
  - [🎯 使用建议](#-使用建议)
    - [何时使用混合模型？](#何时使用混合模型)
    - [架构决策树](#架构决策树)
  - [📚 相关文档](#-相关文档)
    - [深度指南](#深度指南)
    - [官方资源](#官方资源)
  - [✅ 学习路径](#-学习路径)
    - [初级（关系型为主）](#初级关系型为主)
    - [中级（引入1-2种模型）](#中级引入1-2种模型)
    - [高级（多模型混合）](#高级多模型混合)
    - [专家（架构级）](#专家架构级)
  - [🎉 总结](#-总结)

---

## 1. PostgreSQL：真正的混合数据库

### 1.1 什么是混合数据库？

**混合数据库（Multi-Model Database）** 在单一数据库系统中支持多种数据模型，无需维护多个独立数据库。

```text
传统架构（多数据库）：
┌─────────────┐
│ Application │
└──────┬──────┘
       ├─────→ PostgreSQL（关系数据）
       ├─────→ MongoDB（文档数据）
       ├─────→ Neo4j（图数据）
       ├─────→ Redis（缓存）
       ├─────→ ElasticSearch（搜索）
       └─────→ TimescaleDB（时序数据）

问题：
❌ 运维复杂（6个独立系统）
❌ 数据一致性难保证
❌ 成本高（多套license、硬件）
❌ 学习曲线陡峭

PostgreSQL混合架构：
┌─────────────┐
│ Application │
└──────┬──────┘
       │
       └─────→ PostgreSQL
                ├─ 关系数据（原生）
                ├─ 文档数据（JSONB）
                ├─ 图数据（Apache AGE）
                ├─ 空间数据（PostGIS）
                ├─ 时序数据（TimescaleDB）
                ├─ 键值（hstore）
                ├─ 全文搜索（FTS）
                └─ 数组/范围（原生）

优势：
✅ 单一系统（运维简单）
✅ ACID事务（跨模型）
✅ 成本低（一套系统）
✅ 学习成本低（SQL为主）
✅ 数据一致性保证
```

### 1.2 能力全景图

```text
PostgreSQL混合数据库能力：

┌─────────────────────────────────────────┐
│         PostgreSQL Core Engine          │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────┐    ┌────────────────┐   │
│  │ 关系型数据  │    │ 文档型数据      │   │
│  │ - 表/索引   │    │ - JSON/JSONB   │   │
│  │ - 外键约束  │    │ - GIN索引       │  │
│  │ - JOIN     │    │ - JSONPath      │  │
│  │ - 事务     │    │ - Schema验证    │  │
│  └────────────┘    └────────────────┘  │
│                                         │
│  ┌────────────┐    ┌────────────────┐  │
│  │ 图数据库    │    │ 空间数据库     │  │
│  │ - AGE扩展  │    │ - PostGIS      │  │
│  │ - Cypher   │    │ - GIS函数      │  │
│  │ - 图算法   │    │ - 空间索引      │  │
│  └────────────┘    └────────────────┘  │
│                                         │
│  ┌────────────┐    ┌────────────────┐  │
│  │ 时序数据库  │    │ 全文搜索引擎    │  │
│  │ - TimescaleDB│  │ - tsvector     │  │
│  │ - Hypertable │  │ - tsquery      │  │
│  │ - 压缩     │    │ - 多语言        │  │
│  └────────────┘    └────────────────┘  │
│                                         │
│  ┌────────────┐    ┌────────────────┐  │
│  │ 键值存储    │    │ 其他类型       │  │
│  │ - hstore   │    │ - Arrays       │  │
│  │ - 快速KV   │    │ - Ranges       │  │
│  └────────────┘    │ - UUID/XML     │  │
│                    │ - Network      │  │
│                    └────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 2. 关系型数据库（核心）

### 2.1 标准SQL能力

```sql
-- ACID事务
BEGIN;
    INSERT INTO orders (user_id, amount) VALUES (123, 99.99);
    UPDATE users SET balance = balance - 99.99 WHERE id = 123;
COMMIT;

-- 复杂JOIN
SELECT u.name, o.order_id, oi.product_name, oi.quantity
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
WHERE u.created_at >= '2025-01-01';

-- 窗口函数
SELECT
    name,
    salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
FROM employees;

-- CTE（公共表表达式）
WITH RECURSIVE subordinates AS (
    SELECT id, name, manager_id, 1 AS level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT e.id, e.name, e.manager_id, s.level + 1
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates ORDER BY level, name;
```

### 2.2 高级特性

- ✅ 外键约束
- ✅ Check约束
- ✅ Trigger触发器
- ✅ 存储过程（PL/pgSQL）
- ✅ 视图（普通、物化）
- ✅ 分区表
- ✅ 继承
- ✅ MVCC并发控制

---

## 3. 文档数据库（JSONB）

### 3.1 核心能力

```sql
-- 灵活Schema
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku TEXT UNIQUE,
    data JSONB  -- 完全灵活的文档结构
);

-- 笔记本电脑
INSERT INTO products (sku, data) VALUES
('LAPTOP-001', '{
    "name": "Gaming Laptop",
    "specs": {
        "cpu": "Intel i7",
        "ram_gb": 16,
        "storage": [{"type": "SSD", "size_gb": 512}]
    }
}');

-- 书籍（完全不同的结构）
INSERT INTO products (sku, data) VALUES
('BOOK-001', '{
    "name": "PostgreSQL Guide",
    "author": "John Doe",
    "isbn": "978-1234567890",
    "pages": 450
}');

-- 查询（包含查询）
SELECT data ->> 'name' AS name
FROM products
WHERE data @> '{"specs": {"ram_gb": 16}}';

-- 路径查询
SELECT data ->> 'name' AS name
FROM products
WHERE data #>> '{specs, cpu}' LIKE '%i7%';
```

### 3.2 与关系型结合

```sql
-- 混合模式：结构化 + 文档
CREATE TABLE users (
    id SERIAL PRIMARY KEY,              -- 结构化
    email TEXT UNIQUE NOT NULL,         -- 结构化
    username TEXT NOT NULL,             -- 结构化
    profile JSONB,                      -- 文档（灵活扩展）
    preferences JSONB,                  -- 文档
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- JSONB字段可以JOIN
SELECT
    u.username,
    o.order_id,
    u.profile ->> 'city' AS city
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.profile @> '{"vip": true}';
```

**详细指南**: [JSON/JSONB高级查询完整指南](./【深入】JSON-JSONB高级查询完整指南.md)

---

## 4. 图数据库（Apache AGE）

### 4.1 核心能力

```sql
-- 创建图
SELECT create_graph('social_network');

-- Cypher查询
SELECT * FROM cypher('social_network', $$
    CREATE (alice:Person {name: 'Alice', age: 30})
    CREATE (bob:Person {name: 'Bob', age: 25})
    CREATE (alice)-[:FRIEND {since: '2020'}]->(bob)
    RETURN alice, bob
$$) AS (alice agtype, bob agtype);

-- 图遍历
SELECT * FROM cypher('social_network', $$
    MATCH (a:Person {name: 'Alice'})-[:FRIEND*1..3]->(friend)
    RETURN DISTINCT friend.name
$$) AS (friend_name agtype);

-- 最短路径
SELECT * FROM cypher('social_network', $$
    MATCH path = shortestPath((a:Person {name: 'Alice'})-[:FRIEND*]-(b:Person {name: 'David'}))
    RETURN [node IN nodes(path) | node.name] AS path
$$) AS (path agtype);
```

### 4.2 与关系型结合

```sql
-- SQL + Cypher混合查询
WITH high_value_users AS (
    SELECT id, username
    FROM users
    WHERE total_purchases > 10000
)
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WHERE p.user_id IN $user_ids
    RETURN p.name, p.influence_score
$$, jsonb_build_object('user_ids', (SELECT array_agg(id) FROM high_value_users)))
AS (name agtype, score agtype);
```

**详细指南**: [Apache AGE图数据库完整实战指南](../12-扩展开发/【深入】Apache AGE图数据库完整实战指南.md)

---

## 5. 空间数据库（PostGIS）

### 5.1 核心能力

```sql
-- 空间数据类型
CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOMETRY(Point, 4326)  -- WGS84坐标
);

-- 插入位置
INSERT INTO stores (name, location) VALUES
('Store A', ST_SetSRID(ST_MakePoint(116.4074, 39.9042), 4326));  -- 北京

-- 距离查询
SELECT name, ST_Distance(location::geography,
    ST_MakePoint(116.40, 39.90)::geography) / 1000 AS distance_km
FROM stores
ORDER BY distance_km
LIMIT 5;

-- 范围查询
SELECT name
FROM stores
WHERE ST_DWithin(
    location::geography,
    ST_MakePoint(116.40, 39.90)::geography,
    5000  -- 5公里内
);

-- 多边形包含查询
SELECT s.name
FROM stores s
JOIN districts d ON ST_Contains(d.boundary, s.location)
WHERE d.name = 'Haidian District';
```

### 5.2 与关系型结合

```sql
-- 混合查询：位置 + 业务逻辑
SELECT
    s.name,
    s.rating,
    ST_Distance(s.location::geography, user_location::geography) / 1000 AS distance_km,
    o.order_count
FROM stores s
LEFT JOIN (
    SELECT store_id, COUNT(*) AS order_count
    FROM orders
    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY store_id
) o ON s.id = o.store_id
WHERE ST_DWithin(s.location::geography, user_location::geography, 10000)
  AND s.rating >= 4.0
ORDER BY distance_km;
```

**详细指南**: [PostGIS空间数据库完整实战指南](./【深入】PostGIS空间数据库完整实战指南.md)

---

## 6. 时序数据库（TimescaleDB）

### 6.1 核心能力

```sql
-- Hypertable（自动分区）
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION
);

SELECT create_hypertable('sensor_data', 'time', chunk_time_interval => INTERVAL '1 day');

-- 时间桶聚合
SELECT
    time_bucket('1 hour', time) AS hour,
    device_id,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp
FROM sensor_data
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY hour, device_id;

-- 连续聚合（实时物化视图）
CREATE MATERIALIZED VIEW sensor_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    device_id,
    AVG(temperature) AS avg_temp
FROM sensor_data
GROUP BY hour, device_id;

-- 数据压缩（90-95%压缩率）
ALTER TABLE sensor_data SET (timescaledb.compress);
SELECT add_compression_policy('sensor_data', compress_after => INTERVAL '7 days');
```

**详细指南**: [TimescaleDB时序数据库完整实战指南](./【深入】TimescaleDB时序数据库完整实战指南.md)

---

## 7. 键值存储（hstore）

### 7.1 hstore基础

```sql
-- 安装扩展
CREATE EXTENSION hstore;

-- 创建表
CREATE TABLE user_preferences (
    user_id INT PRIMARY KEY,
    settings hstore
);

-- 插入数据
INSERT INTO user_preferences (user_id, settings) VALUES
(1, 'theme => dark, language => en, notifications => true'),
(2, 'theme => light, language => zh, timezone => Asia/Shanghai');

-- 查询
SELECT settings -> 'theme' AS theme
FROM user_preferences
WHERE user_id = 1;

-- 更新
UPDATE user_preferences
SET settings = settings || 'theme => light'
WHERE user_id = 1;

-- 删除键
UPDATE user_preferences
SET settings = delete(settings, 'timezone')
WHERE user_id = 2;

-- 查询包含某键
SELECT user_id
FROM user_preferences
WHERE settings ? 'timezone';

-- 查询键值对匹配
SELECT user_id
FROM user_preferences
WHERE settings @> 'theme => dark';
```

### 7.2 hstore vs JSONB

| 特性 | hstore | JSONB |
|------|--------|-------|
| **值类型** | 只有字符串 | 任意JSON类型 |
| **嵌套** | ❌ 不支持 | ✅ 支持 |
| **性能** | ✅ 稍快 | ⚠️ 稍慢 |
| **索引** | ✅ GiST/GIN | ✅ GIN |
| **推荐使用** | 简单KV | 99%场景用JSONB |

---

## 8. 全文搜索引擎

### 8.1 核心能力

```sql
-- 全文搜索
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'D')
    ) STORED
);

CREATE INDEX articles_search_idx ON articles USING GIN(search_vector);

-- 搜索查询
SELECT id, title, ts_rank(search_vector, query) AS rank
FROM articles, to_tsquery('english', 'postgresql & search') query
WHERE search_vector @@ query
ORDER BY rank DESC;

-- 高亮显示
SELECT ts_headline('english', content,
    to_tsquery('english', 'postgresql'),
    'StartSel=<mark>, StopSel=</mark>'
) AS highlighted
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql');
```

### 8.2 多语言支持

```sql
-- 中文全文搜索（zhparser扩展）
CREATE EXTENSION zhparser;
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);

-- 中文搜索
SELECT to_tsvector('chinese', '我爱PostgreSQL数据库') @@
       to_tsquery('chinese', 'PostgreSQL & 数据库');
-- 结果：t
```

**详细指南**: [PostgreSQL全文搜索完整实战指南](../04-查询/【深入】PostgreSQL全文搜索完整实战指南.md)

---

## 9. 数组与范围类型

### 9.1 数组类型

```sql
-- 数组列
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT,
    tags TEXT[],  -- 文本数组
    view_counts INT[]
);

-- 插入
INSERT INTO posts (title, tags, view_counts) VALUES
('PostgreSQL Tutorial', ARRAY['database', 'postgresql', 'sql'], ARRAY[100, 150, 200]);

-- 查询
SELECT title
FROM posts
WHERE 'postgresql' = ANY(tags);

-- 数组操作
SELECT
    title,
    array_length(tags, 1) AS tag_count,
    tags[1] AS first_tag,
    array_append(tags, 'new_tag') AS tags_with_new
FROM posts;

-- GIN索引支持数组
CREATE INDEX posts_tags_gin_idx ON posts USING GIN(tags);

SELECT title FROM posts WHERE tags && ARRAY['database', 'sql'];
-- 使用索引，快速查找
```

### 9.2 范围类型

```sql
-- 时间范围
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_name TEXT,
    event_period tstzrange  -- 时间范围类型
);

INSERT INTO events (event_name, event_period) VALUES
('Conference', tstzrange('2025-06-01 09:00', '2025-06-03 18:00'));

-- 范围查询
SELECT event_name
FROM events
WHERE event_period @> '2025-06-02 14:00'::timestamptz;  -- 包含某时刻

-- 范围重叠
SELECT e1.event_name, e2.event_name
FROM events e1
JOIN events e2 ON e1.id < e2.id
WHERE e1.event_period && e2.event_period;  -- 时间重叠

-- 其他范围类型
-- int4range, int8range: 整数范围
-- numrange: 数值范围
-- daterange: 日期范围
-- tsrange, tstzrange: 时间戳范围
```

---

## 10. 分布式数据库（Citus）

### 10.1 核心能力

```sql
-- 水平扩展（分片）
CREATE TABLE events (
    event_id BIGSERIAL,
    tenant_id INT NOT NULL,
    event_data JSONB,
    created_at TIMESTAMPTZ
);

-- 转换为分布式表
SELECT create_distributed_table('events', 'tenant_id');

-- 分布式查询（自动并行）
SELECT tenant_id, COUNT(*)
FROM events
WHERE created_at >= '2025-01-01'
GROUP BY tenant_id;
-- 在多个Worker节点并行执行，Coordinator聚合结果
```

**详细指南**: [Citus分布式PostgreSQL完整实战指南](../05-部署架构/【深入】Citus分布式PostgreSQL完整实战指南.md)

---

## 11. 混合查询实战

### 11.1 案例1：智能推荐系统

**需求**: 结合地理位置、社交关系、用户偏好推荐餐厅

```sql
-- 混合5种数据模型
WITH
-- 1. 空间数据库（PostGIS）：附近餐厅
nearby_restaurants AS (
    SELECT r.id, r.name, r.cuisine_type,
           ST_Distance(r.location::geography, user_location::geography) AS distance
    FROM restaurants r
    WHERE ST_DWithin(r.location::geography, user_location::geography, 5000)
),
-- 2. 图数据库（AGE）：朋友去过的餐厅
friend_recommendations AS (
    SELECT * FROM cypher('social_network', $$
        MATCH (user:Person {id: $user_id})-[:FRIEND]->(friend)-[:VISITED]->(restaurant:Restaurant)
        RETURN restaurant.id AS restaurant_id, COUNT(*) AS friend_visit_count
    $$, jsonb_build_object('user_id', current_user_id))
    AS (restaurant_id agtype, friend_visit_count agtype)
),
-- 3. 文档数据库（JSONB）：用户偏好
user_prefs AS (
    SELECT preferences -> 'cuisine' AS preferred_cuisines
    FROM users
    WHERE id = current_user_id
),
-- 4. 时序数据库（TimescaleDB）：热门餐厅
trending_restaurants AS (
    SELECT restaurant_id, COUNT(*) AS recent_visits
    FROM restaurant_visits
    WHERE time >= NOW() - INTERVAL '7 days'
    GROUP BY restaurant_id
),
-- 5. 关系型：餐厅评分
restaurant_ratings AS (
    SELECT restaurant_id, AVG(rating) AS avg_rating, COUNT(*) AS review_count
    FROM reviews
    GROUP BY restaurant_id
)
-- 综合排序
SELECT
    nr.id,
    nr.name,
    nr.cuisine_type,
    nr.distance / 1000 AS distance_km,
    COALESCE(fr.friend_visit_count, 0) AS friend_visits,
    COALESCE(tr.recent_visits, 0) AS trending_score,
    COALESCE(rr.avg_rating, 0) AS rating,
    -- 综合评分
    (
        (5000 - nr.distance) / 1000 * 1.0 +                    -- 距离（近+分）
        COALESCE(fr.friend_visit_count, 0) * 10.0 +            -- 朋友去过（+分）
        COALESCE(tr.recent_visits, 0) * 0.5 +                  -- 最近热门（+分）
        COALESCE(rr.avg_rating, 0) * 5.0 +                     -- 评分（+分）
        CASE WHEN up.preferred_cuisines @> to_jsonb(nr.cuisine_type)
             THEN 20.0 ELSE 0.0 END                            -- 匹配偏好（+分）
    ) AS final_score
FROM nearby_restaurants nr
LEFT JOIN friend_recommendations fr ON nr.id = fr.restaurant_id::int
LEFT JOIN trending_restaurants tr ON nr.id = tr.restaurant_id
LEFT JOIN restaurant_ratings rr ON nr.id = rr.restaurant_id
CROSS JOIN user_prefs up
ORDER BY final_score DESC
LIMIT 10;
```

### 11.2 案例2：实时物流追踪

```sql
-- 混合数据模型
CREATE TABLE shipments (
    id SERIAL PRIMARY KEY,
    tracking_number TEXT UNIQUE,
    sender_id INT REFERENCES users(id),
    recipient_id INT REFERENCES users(id),

    -- 空间数据（PostGIS）
    current_location GEOMETRY(Point, 4326),
    route_path GEOMETRY(LineString, 4326),

    -- 文档数据（JSONB）
    package_details JSONB,  -- {weight, dimensions, contents}
    delivery_instructions JSONB,

    -- 时序数据
    status_history JSONB[],  -- 按时间排序的状态数组

    -- 关系数据
    status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    estimated_delivery TIMESTAMPTZ
);

-- 插入物流数据
INSERT INTO shipments (tracking_number, sender_id, recipient_id, current_location, package_details) VALUES
(
    'TRACK123456',
    1,
    2,
    ST_SetSRID(ST_MakePoint(116.40, 39.90), 4326),
    '{
        "weight_kg": 2.5,
        "dimensions": {"length_cm": 30, "width_cm": 20, "height_cm": 10},
        "contents": "Electronics",
        "fragile": true
    }'
);

-- 综合查询：我的快递在哪里
SELECT
    s.tracking_number,
    s.status,
    -- 空间查询：距离目的地多远
    ST_Distance(
        s.current_location::geography,
        (SELECT location FROM addresses WHERE user_id = s.recipient_id)::geography
    ) / 1000 AS distance_to_destination_km,
    -- 文档查询：包裹信息
    s.package_details ->> 'weight_kg' AS weight,
    s.package_details -> 'dimensions' AS dimensions,
    -- 时序分析：预计到达时间
    s.estimated_delivery,
    -- 关系查询：发件人信息
    sender.username AS sender_name
FROM shipments s
JOIN users sender ON s.sender_id = sender.id
WHERE s.recipient_id = current_user_id
  AND s.status NOT IN ('delivered', 'cancelled')
ORDER BY s.created_at DESC;
```

### 11.3 案例3：社交电商平台

```sql
-- 完整混合数据模型
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku TEXT UNIQUE,
    name TEXT NOT NULL,
    category TEXT,
    base_price NUMERIC(10,2),

    -- 文档数据：灵活规格
    specifications JSONB,

    -- 全文搜索
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', name), 'A') ||
        setweight(to_tsvector('english', coalesce(specifications ->> 'description', '')), 'D')
    ) STORED,

    -- 数组：标签
    tags TEXT[]
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,

    -- 空间数据：用户位置
    location GEOMETRY(Point, 4326),

    -- 文档数据：用户资料
    profile JSONB
);

-- 综合推荐查询
WITH
-- 全文搜索：关键词匹配
text_matches AS (
    SELECT id, ts_rank(search_vector, query) AS text_rank
    FROM products, to_tsquery('english', 'laptop gaming') query
    WHERE search_vector @@ query
),
-- 图数据库：朋友买过的
social_recommendations AS (
    SELECT * FROM cypher('social_network', $$
        MATCH (user:Person {id: $user_id})-[:FRIEND]->(friend)-[:PURCHASED]->(product:Product)
        RETURN product.id AS product_id, COUNT(*) AS friend_purchase_count
    $$, jsonb_build_object('user_id', current_user_id))
    AS (product_id agtype, friend_purchase_count agtype)
),
-- 空间数据：本地商家
local_sellers AS (
    SELECT DISTINCT ps.product_id
    FROM product_sellers ps
    JOIN sellers s ON ps.seller_id = s.id
    JOIN users u ON u.id = current_user_id
    WHERE ST_DWithin(s.location::geography, u.location::geography, 50000)
),
-- 文档数据：用户偏好匹配
preference_matches AS (
    SELECT p.id,
           CASE WHEN u.profile -> 'preferences' -> 'brands' ? (p.specifications ->> 'brand')
                THEN 10.0 ELSE 0.0 END AS preference_score
    FROM products p
    CROSS JOIN (SELECT profile FROM users WHERE id = current_user_id) u
)
-- 综合评分
SELECT
    p.id,
    p.name,
    p.base_price,
    p.specifications ->> 'brand' AS brand,
    (
        COALESCE(tm.text_rank, 0) * 10.0 +
        COALESCE(sr.friend_purchase_count::numeric, 0) * 5.0 +
        CASE WHEN ls.product_id IS NOT NULL THEN 15.0 ELSE 0.0 END +
        COALESCE(pm.preference_score, 0)
    ) AS final_score
FROM products p
LEFT JOIN text_matches tm ON p.id = tm.id
LEFT JOIN social_recommendations sr ON p.id = sr.product_id::int
LEFT JOIN local_sellers ls ON p.id = ls.product_id
LEFT JOIN preference_matches pm ON p.id = pm.id
WHERE final_score > 0
ORDER BY final_score DESC
LIMIT 20;
```

---

## 12. 性能对比

### 12.1 数据模型性能

| 数据模型 | 场景 | PostgreSQL | 专用数据库 | 差距 |
|---------|------|-----------|-----------|------|
| **关系型** | OLTP | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 持平 |
| **文档型** | CRUD | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ MongoDB | 10-20% |
| **图数据库** | 图遍历 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ Neo4j | 20-30% |
| **空间数据** | GIS | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 持平 |
| **时序数据** | 时序分析 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ InfluxDB | 10-20% |
| **全文搜索** | 搜索 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ ES | 20-40% |
| **键值** | KV读写 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ Redis | 50-70% |

### 12.2 混合查询性能

```text
关键发现：

1. 单一模型查询
   PostgreSQL专用扩展 ≈ 90-95%专用数据库性能

2. 混合模型查询
   PostgreSQL ⭐⭐⭐⭐⭐
   多数据库方案 ⭐⭐ (需应用层整合，性能差)

3. 事务一致性
   PostgreSQL ⭐⭐⭐⭐⭐ (ACID跨所有模型)
   多数据库方案 ⭐⭐ (最终一致性，复杂)

4. 运维复杂度
   PostgreSQL ⭐⭐⭐⭐⭐ (单一系统)
   多数据库方案 ⭐⭐ (6个系统)
```

---

## 📊 完整能力矩阵

### 数据模型支持

| 数据模型 | 支持方式 | 成熟度 | 性能 | 推荐度 |
|---------|---------|--------|------|--------|
| **关系型** | 原生 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **文档型(JSON)** | 原生(JSONB) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **图数据库** | 扩展(AGE) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **空间数据** | 扩展(PostGIS) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **时序数据** | 扩展(TimescaleDB) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **键值存储** | 扩展(hstore) | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **全文搜索** | 原生(FTS) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **数组** | 原生 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **范围类型** | 原生 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **分布式** | 扩展(Citus) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 查询语言支持

| 查询语言 | 支持方式 | 学习曲线 | 推荐度 |
|---------|---------|---------|--------|
| **SQL** | 原生 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cypher** | AGE扩展 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **GraphQL** | 第三方(PostGraphile/Hasura) | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **JSONPath** | 原生 | ⭐⭐ | ⭐⭐⭐⭐ |
| **PL/pgSQL** | 原生 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎯 使用建议

### 何时使用混合模型？

```text
✅ 推荐使用混合模型：
1. 数据模型多样（关系+文档+空间）
2. 需要ACID事务保证
3. 需要复杂JOIN查询
4. 团队熟悉SQL
5. 简化架构（减少服务数量）
6. 预算有限（单一系统许可）

⚠️ 考虑专用数据库：
1. 单一模型为主（>90%）
2. 极致性能要求
3. 超大规模（>10TB单一模型）
4. 团队已有专用数据库经验
```

### 架构决策树

```text
是否需要多种数据模型？
├─ NO → 单一专用数据库
└─ YES → 继续

是否需要跨模型ACID事务？
├─ YES → ✅ PostgreSQL混合模型
└─ NO → 继续

是否有某个模型数据量极大（>10TB）？
├─ YES → 混合架构（PostgreSQL + 专用DB）
└─ NO → ✅ PostgreSQL混合模型

是否团队更熟悉NoSQL？
├─ YES → 考虑专用数据库
└─ NO → ✅ PostgreSQL混合模型
```

---

## 📚 相关文档

### 深度指南

1. [Apache AGE图数据库完整实战指南](../12-扩展开发/【深入】Apache AGE图数据库完整实战指南.md)
2. [PostGIS空间数据库完整实战指南](../03-数据类型/【深入】PostGIS空间数据库完整实战指南.md)
3. [Citus分布式PostgreSQL完整实战指南](../05-部署架构/【深入】Citus分布式PostgreSQL完整实战指南.md)
4. [TimescaleDB时序数据库完整实战指南](../03-数据类型/【深入】TimescaleDB时序数据库完整实战指南.md)
5. [PostgreSQL全文搜索完整实战指南](../04-查询/【深入】PostgreSQL全文搜索完整实战指南.md)
6. [JSON/JSONB高级查询完整指南](../03-数据类型/【深入】JSON-JSONB高级查询完整指南.md)
7. [PostgreSQL + GraphQL完整实战指南](../06-应用开发/【深入】PostgreSQL+GraphQL完整实战指南.md)

### 官方资源

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Extension Network (PGXN)](https://pgxn.org/)

---

## ✅ 学习路径

### 初级（关系型为主）

1. SQL基础
2. 索引优化
3. 事务管理

### 中级（引入1-2种模型）

1. JSONB文档数据
2. 全文搜索
3. 数组类型

### 高级（多模型混合）

1. PostGIS空间数据
2. TimescaleDB时序数据
3. Apache AGE图数据

### 专家（架构级）

1. Citus分布式
2. 混合查询优化
3. 多模型系统架构设计

---

## 🎉 总结

PostgreSQL不仅是世界上最先进的开源关系数据库，更是一个**真正的混合数据库平台**：

**核心优势**:

- ✅ **10种数据模型**：关系、文档、图、空间、时序、KV、全文、数组、范围、分布式
- ✅ **统一的ACID事务**：跨所有数据模型
- ✅ **丰富的查询语言**：SQL、Cypher、GraphQL、JSONPath
- ✅ **单一系统**：简化架构，降低成本
- ✅ **成熟稳定**：30+年历史，生产验证
- ✅ **活跃生态**：数千个扩展，庞大社区

**适用场景**：

- ✅ 混合数据模型应用（90%场景）
- ✅ 中小型到大型应用（<10TB）
- ✅ 需要ACID保证
- ✅ 架构简化优先
- ✅ 成本敏感型项目

---

**文档维护**: 本文档持续更新以反映PostgreSQL生态最新发展。
**反馈**: 如发现错误或有改进建议，请提交issue。

**版本历史**:

- v1.0 (2025-01): 初始版本，全面展示PostgreSQL混合数据库能力
