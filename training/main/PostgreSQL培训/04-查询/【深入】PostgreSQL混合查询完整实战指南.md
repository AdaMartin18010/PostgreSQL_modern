# 【深入】PostgreSQL混合查询完整实战指南

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 12+
> **难度等级**: ⭐⭐⭐⭐⭐ 专家 | **预计学习时间**: 10-12小时

---

## 📋 目录

- [【深入】PostgreSQL混合查询完整实战指南](#深入postgresql混合查询完整实战指南)
  - [📋 目录](#-目录)
  - [1. 混合查询概述](#1-混合查询概述)
    - [1.1 什么是混合查询？](#11-什么是混合查询)
    - [1.2 混合查询类型](#12-混合查询类型)
  - [2. 关系+文档混合查询](#2-关系文档混合查询)
    - [2.1 基础混合](#21-基础混合)
    - [2.2 关系JOIN + JSONB聚合](#22-关系join--jsonb聚合)
    - [2.3 JSONB数组展开 + JOIN](#23-jsonb数组展开--join)
  - [3. 关系+图混合查询](#3-关系图混合查询)
    - [3.1 社交推荐（关系数据 + 图关系）](#31-社交推荐关系数据--图关系)
    - [3.2 影响力分析](#32-影响力分析)
  - [4. 关系+空间混合查询](#4-关系空间混合查询)
    - [4.1 位置服务（结构化 + 地理数据）](#41-位置服务结构化--地理数据)
    - [4.2 空间 + 时序分析](#42-空间--时序分析)
  - [5. 关系+时序混合查询](#5-关系时序混合查询)
    - [5.1 时序聚合 + 维度表JOIN](#51-时序聚合--维度表join)
    - [5.2 时序 + JSONB元数据](#52-时序--jsonb元数据)
  - [6. 关系+向量混合查询](#6-关系向量混合查询)
    - [6.1 语义搜索 + 结构化过滤](#61-语义搜索--结构化过滤)
    - [6.2 向量 + 用户行为](#62-向量--用户行为)
  - [7. 全文+向量混合搜索](#7-全文向量混合搜索)
    - [7.1 混合排序](#71-混合排序)
  - [8. 多模型混合查询](#8-多模型混合查询)
    - [8.1 5模型混合（关系+文档+空间+向量+全文）](#81-5模型混合关系文档空间向量全文)
  - [9. 性能优化](#9-性能优化)
    - [9.1 混合查询优化原则](#91-混合查询优化原则)
    - [9.2 CTE vs 子查询](#92-cte-vs-子查询)
  - [10. 生产实战案例](#10-生产实战案例)
    - [10.1 案例1：智能电商搜索](#101-案例1智能电商搜索)
  - [11. 最佳实践](#11-最佳实践)
    - [11.1 混合查询设计原则](#111-混合查询设计原则)
    - [11.2 性能优化Checklist](#112-性能优化checklist)
  - [📚 延伸阅读](#-延伸阅读)
    - [相关指南](#相关指南)
  - [✅ 学习检查清单](#-学习检查清单)

---

## 1. 混合查询概述

### 1.1 什么是混合查询？

**混合查询**是在单一查询中结合多种数据模型的查询方式，是PostgreSQL作为混合数据库的核心竞争力。

```text
传统方案（多数据库）：
┌──────────────────────────────────────┐
│ Application Layer                    │
├──────────────────────────────────────┤
│ 1. 查询PostgreSQL（用户数据）        │
│ 2. 查询MongoDB（产品数据）           │
│ 3. 查询ElasticSearch（搜索）         │
│ 4. 应用层合并结果                     │
│ 5. 应用层过滤排序                     │
└──────────────────────────────────────┘

问题：
❌ 多次网络调用（延迟高）
❌ 应用层复杂（代码量大）
❌ 数据一致性难保证
❌ 性能差（串行执行）

PostgreSQL混合查询：
┌──────────────────────────────────────┐
│ PostgreSQL Single Query              │
├──────────────────────────────────────┤
│ SELECT u.name, p.specs, s.rank      │
│ FROM users u                         │
│ JOIN products p (JSONB)              │
│ JOIN search_results s (FTS)          │
│ WHERE ...                            │
└──────────────────────────────────────┘

优势：
✅ 单次查询（低延迟）
✅ SQL原生（代码简洁）
✅ ACID保证（一致性）
✅ 数据库内优化（高性能）
```

### 1.2 混合查询类型

| 类型 | 数据模型组合 | 典型场景 |
|------|-------------|---------|
| **类型1** | 关系 + 文档(JSONB) | 灵活属性产品 |
| **类型2** | 关系 + 图(AGE) | 社交推荐 |
| **类型3** | 关系 + 空间(PostGIS) | O2O服务 |
| **类型4** | 关系 + 时序(TimescaleDB) | IoT监控 |
| **类型5** | 关系 + 向量(pgvector) | AI语义搜索 |
| **类型6** | 全文 + 向量 | 混合搜索 |
| **类型7** | 3+模型 | 复杂业务 |

---

## 2. 关系+文档混合查询

### 2.1 基础混合

```sql
-- 场景：电商产品（固定字段+灵活规格）
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku TEXT UNIQUE NOT NULL,              -- 结构化
    name TEXT NOT NULL,                    -- 结构化
    base_price NUMERIC(10,2) NOT NULL,     -- 结构化
    category TEXT NOT NULL,                -- 结构化
    specifications JSONB NOT NULL,         -- 文档型（灵活）
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 混合查询：结构化过滤 + JSONB查询
SELECT
    id,
    name,
    base_price,
    specifications ->> 'brand' AS brand,
    specifications -> 'processor' AS cpu_info
FROM products
WHERE category = 'Laptops'                              -- 结构化过滤
  AND base_price BETWEEN 800 AND 2000                   -- 结构化过滤
  AND specifications @> '{"memory_gb": 16}'             -- JSONB过滤
  AND specifications #>> '{processor, cores}' >= '8'    -- JSONB深度过滤
ORDER BY base_price;
```

### 2.2 关系JOIN + JSONB聚合

```sql
-- 订单统计 + 产品规格分析
SELECT
    p.category,
    p.specifications ->> 'brand' AS brand,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.price) AS total_revenue,
    jsonb_agg(DISTINCT p.specifications -> 'processor') AS cpu_types
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.created_at >= '2025-01-01'
GROUP BY p.category, brand
ORDER BY total_revenue DESC;
```

### 2.3 JSONB数组展开 + JOIN

```sql
-- 产品标签关联查询
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    tags JSONB  -- ["electronics", "laptop", "gaming"]
);

-- 展开标签并统计
SELECT
    tag,
    COUNT(DISTINCT p.id) AS product_count,
    AVG(p.base_price) AS avg_price
FROM products p,
     jsonb_array_elements_text(p.tags) AS tag
GROUP BY tag
ORDER BY product_count DESC;

-- 标签共现分析
WITH tag_pairs AS (
    SELECT
        p.id,
        t1.tag AS tag1,
        t2.tag AS tag2
    FROM products p,
         jsonb_array_elements_text(p.tags) t1(tag),
         jsonb_array_elements_text(p.tags) t2(tag)
    WHERE t1.tag < t2.tag
)
SELECT
    tag1,
    tag2,
    COUNT(*) AS co_occurrence
FROM tag_pairs
GROUP BY tag1, tag2
HAVING COUNT(*) > 10
ORDER BY co_occurrence DESC;
```

---

## 3. 关系+图混合查询

### 3.1 社交推荐（关系数据 + 图关系）

```sql
-- 场景：基于好友购买的商品推荐
-- 关系表：用户、订单
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    total_purchases NUMERIC
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_id INT,
    amount NUMERIC
);

-- 图数据：社交关系（Apache AGE）
-- (在social_network图中)

-- 混合查询：SQL + Cypher
WITH
-- 1. 从图数据库获取朋友列表
friends AS (
    SELECT * FROM cypher('social_network', $$
        MATCH (user:Person {id: $user_id})-[:FRIEND]->(friend:Person)
        RETURN friend.user_id AS friend_id
    $$, jsonb_build_object('user_id', 123))
    AS (friend_id agtype)
),
-- 2. 朋友购买的商品
friend_purchases AS (
    SELECT
        o.product_id,
        COUNT(DISTINCT o.user_id) AS friend_count,
        SUM(o.amount) AS total_spent
    FROM orders o
    WHERE o.user_id IN (SELECT friend_id::int FROM friends)
      AND o.created_at >= NOW() - INTERVAL '30 days'
    GROUP BY o.product_id
),
-- 3. 我已购买的商品
my_purchases AS (
    SELECT DISTINCT product_id FROM orders WHERE user_id = 123
)
-- 4. 推荐：朋友买了我没买的
SELECT
    p.id,
    p.name,
    p.base_price,
    fp.friend_count AS friends_bought,
    fp.total_spent,
    (
        fp.friend_count * 10.0 +                    -- 朋友购买数
        LOG(fp.total_spent + 1) * 5.0 +            -- 总消费
        p.rating * 8.0                             -- 商品评分
    ) AS recommendation_score
FROM products p
JOIN friend_purchases fp ON p.id = fp.product_id
WHERE p.id NOT IN (SELECT product_id FROM my_purchases)
ORDER BY recommendation_score DESC
LIMIT 10;
```

### 3.2 影响力分析

```sql
-- 场景：找出影响力大且购买力强的用户
WITH
-- 图数据：影响力（粉丝数、中心性）
influencers AS (
    SELECT * FROM cypher('social_network', $$
        MATCH (p:Person)
        OPTIONAL MATCH (p)<-[:FOLLOW]-(follower)
        WITH p, COUNT(follower) AS follower_count
        WHERE follower_count > 1000
        RETURN p.user_id AS user_id, follower_count
    $$) AS (user_id agtype, follower_count agtype)
),
-- 关系数据：购买力
high_spenders AS (
    SELECT user_id, SUM(amount) AS total_spent
    FROM orders
    WHERE created_at >= NOW() - INTERVAL '90 days'
    GROUP BY user_id
    HAVING SUM(amount) > 5000
)
-- 混合：影响力 + 购买力
SELECT
    u.id,
    u.username,
    i.follower_count::int AS followers,
    hs.total_spent,
    (
        i.follower_count::numeric / 1000 * 50.0 +   -- 影响力权重
        hs.total_spent / 100                         -- 购买力权重
    ) AS kol_score
FROM users u
JOIN influencers i ON u.id = i.user_id::int
JOIN high_spenders hs ON u.id = hs.user_id
ORDER BY kol_score DESC
LIMIT 50;
```

---

## 4. 关系+空间混合查询

### 4.1 位置服务（结构化 + 地理数据）

```sql
-- 场景：附近的高评分餐厅
SELECT
    r.id,
    r.name,
    r.cuisine_type,                                                      -- 结构化
    ST_Distance(r.location::geography, user_loc::geography) / 1000 AS distance_km,  -- 空间计算
    AVG(rv.rating) AS avg_rating,                                        -- 关系聚合
    COUNT(rv.id) AS review_count,
    jsonb_agg(DISTINCT rv.tags) AS all_tags                             -- JSONB聚合
FROM restaurants r
JOIN reviews rv ON r.id = rv.restaurant_id
WHERE ST_DWithin(r.location::geography, user_loc::geography, 5000)      -- 空间过滤
  AND r.is_open = TRUE                                                   -- 结构化过滤
GROUP BY r.id, r.name, r.cuisine_type, r.location
HAVING AVG(rv.rating) >= 4.0
ORDER BY distance_km, avg_rating DESC
LIMIT 10;
```

### 4.2 空间 + 时序分析

```sql
-- 场景：设备轨迹分析
WITH device_trajectory AS (
    SELECT
        device_id,
        time_bucket('1 hour', time) AS hour,
        AVG(ST_X(location)) AS avg_lon,
        AVG(ST_Y(location)) AS avg_lat,
        COUNT(*) AS sample_count
    FROM device_locations
    WHERE time >= NOW() - INTERVAL '24 hours'
      AND device_id = 123
    GROUP BY device_id, hour
)
SELECT
    dt.hour,
    ST_MakeLine(
        ST_SetSRID(ST_MakePoint(dt.avg_lon, dt.avg_lat), 4326)
    ) AS trajectory_line,
    dt.sample_count,
    z.zone_name
FROM device_trajectory dt
LEFT JOIN zones z ON ST_Contains(
    z.boundary,
    ST_SetSRID(ST_MakePoint(dt.avg_lon, dt.avg_lat), 4326)
)
ORDER BY dt.hour;
```

---

## 5. 关系+时序混合查询

### 5.1 时序聚合 + 维度表JOIN

```sql
-- 场景：设备监控Dashboard
SELECT
    d.device_name,                                     -- 维度表
    d.location,                                        -- 维度表
    d.device_type,                                     -- 维度表
    time_bucket('5 minutes', m.time) AS bucket,       -- 时序聚合
    AVG(m.temperature) AS avg_temp,
    MAX(m.cpu_usage) AS max_cpu,
    COUNT(*) AS sample_count
FROM metrics m
JOIN devices d ON m.device_id = d.id                  -- 关系JOIN
WHERE m.time >= NOW() - INTERVAL '1 hour'
  AND d.device_type = 'server'                        -- 维度过滤
  AND d.location = 'Beijing'
GROUP BY d.id, d.device_name, d.location, d.device_type, bucket
ORDER BY bucket DESC, d.device_name;
```

### 5.2 时序 + JSONB元数据

```sql
-- 场景：带复杂元数据的时序分析
CREATE TABLE events (
    time TIMESTAMPTZ NOT NULL,
    event_type TEXT,
    user_id INT,
    event_data JSONB,              -- 灵活的事件数据
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('events', 'time');

-- 混合查询：时间聚合 + JSONB提取
SELECT
    time_bucket('1 hour', time) AS hour,
    event_type,
    event_data ->> 'source' AS source,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users,
    AVG((event_data ->> 'duration')::numeric) AS avg_duration,
    jsonb_object_agg(
        event_data ->> 'status',
        COUNT(*)
    ) AS status_distribution
FROM events
WHERE time >= NOW() - INTERVAL '24 hours'
  AND event_data @> '{"success": true}'              -- JSONB过滤
GROUP BY hour, event_type, source
ORDER BY hour DESC;
```

---

## 6. 关系+向量混合查询

### 6.1 语义搜索 + 结构化过滤

```sql
-- 场景：产品语义搜索 + 精确过滤
SELECT
    p.id,
    p.name,
    p.price,
    p.category,
    (1.0 - (p.embedding <=> query_vec)) AS semantic_similarity,  -- 向量相似度
    r.avg_rating,
    r.review_count
FROM products p
LEFT JOIN (
    SELECT product_id, AVG(rating) AS avg_rating, COUNT(*) AS review_count
    FROM reviews
    GROUP BY product_id
) r ON p.id = r.product_id
WHERE p.category = 'Electronics'                      -- 结构化过滤
  AND p.price BETWEEN 500 AND 2000                    -- 结构化过滤
  AND p.in_stock = TRUE                               -- 结构化过滤
  AND (r.avg_rating IS NULL OR r.avg_rating >= 4.0)  -- 关系过滤
ORDER BY
    (1.0 - (p.embedding <=> query_vec)) * 0.6 +      -- 语义60%
    COALESCE(r.avg_rating / 5.0, 0) * 0.3 +          -- 评分30%
    (1.0 / (1.0 + p.price / 10000.0)) * 0.1          -- 性价比10%
DESC
LIMIT 20;
```

### 6.2 向量 + 用户行为

```sql
-- 场景：基于用户历史的个性化搜索
WITH user_history AS (
    -- 用户最近浏览的产品
    SELECT product_id
    FROM user_views
    WHERE user_id = 123
      AND viewed_at >= NOW() - INTERVAL '7 days'
    LIMIT 50
),
user_preference_vec AS (
    -- 计算用户偏好向量（历史产品的平均向量）
    SELECT AVG(embedding) AS pref_vec
    FROM products
    WHERE id IN (SELECT product_id FROM user_history)
)
SELECT
    p.id,
    p.name,
    p.price,
    (1.0 - (p.embedding <=> upv.pref_vec)) AS personalization_score,
    (1.0 - (p.embedding <=> query_vec)) AS query_relevance
FROM products p, user_preference_vec upv
WHERE p.id NOT IN (SELECT product_id FROM user_history)  -- 排除已浏览
ORDER BY
    query_relevance * 0.7 +           -- 查询相关性70%
    personalization_score * 0.3       -- 个性化30%
DESC
LIMIT 20;
```

---

## 7. 全文+向量混合搜索

### 7.1 混合排序

```sql
-- 场景：文章搜索（关键词 + 语义）
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding vector(1536),            -- 语义向量
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'D')
    ) STORED,                          -- 全文搜索
    view_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 混合搜索函数
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text TEXT,
    query_embedding vector(1536),
    semantic_weight FLOAT DEFAULT 0.7,
    keyword_weight FLOAT DEFAULT 0.3,
    top_k INT DEFAULT 20
) RETURNS TABLE (
    id INT,
    title TEXT,
    semantic_score FLOAT,
    keyword_score FLOAT,
    combined_score FLOAT
) AS $$
DECLARE
    query tsquery := websearch_to_tsquery('english', query_text);
BEGIN
    RETURN QUERY
    WITH
    semantic_results AS (
        SELECT a.id, (1.0 - (a.embedding <=> query_embedding))::FLOAT AS score
        FROM articles a
        ORDER BY a.embedding <=> query_embedding
        LIMIT 100
    ),
    keyword_results AS (
        SELECT a.id, ts_rank_cd(a.search_vector, query, 32)::FLOAT AS score
        FROM articles a
        WHERE a.search_vector @@ query
        ORDER BY score DESC
        LIMIT 100
    )
    SELECT
        a.id,
        a.title,
        COALESCE(sr.score, 0.0) AS semantic_score,
        COALESCE(kr.score, 0.0) AS keyword_score,
        (
            COALESCE(sr.score, 0.0) * semantic_weight +
            COALESCE(kr.score, 0.0) * keyword_weight
        ) AS combined_score
    FROM articles a
    LEFT JOIN semantic_results sr ON a.id = sr.id
    LEFT JOIN keyword_results kr ON a.id = kr.id
    WHERE sr.id IS NOT NULL OR kr.id IS NOT NULL
    ORDER BY combined_score DESC
    LIMIT top_k;
END;
$$ LANGUAGE plpgsql;

-- 使用
SELECT * FROM hybrid_search(
    'postgresql performance optimization',
    '[...]'::vector(1536),
    semantic_weight => 0.6,
    keyword_weight => 0.4,
    top_k => 10
);
```

---

## 8. 多模型混合查询

### 8.1 5模型混合（关系+文档+空间+向量+全文）

```sql
-- 场景：智能餐厅推荐系统
WITH
-- 1. 空间：附近餐厅
nearby_restaurants AS (
    SELECT id, ST_Distance(location::geography, user_location::geography) AS distance
    FROM restaurants
    WHERE ST_DWithin(location::geography, user_location::geography, 5000)
),
-- 2. 向量：语义匹配用户偏好
semantic_matches AS (
    SELECT r.id, (1.0 - (r.description_embedding <=> user_preference_vec)) AS semantic_score
    FROM restaurants r
),
-- 3. 全文：关键词搜索
keyword_matches AS (
    SELECT r.id, ts_rank(r.search_vector, query) AS keyword_score
    FROM restaurants r
    WHERE r.search_vector @@ to_tsquery('english', 'chinese & spicy')
),
-- 4. 图：朋友去过的
friend_visited AS (
    SELECT * FROM cypher('social', $$
        MATCH (user:Person {id: $user_id})-[:FRIEND]->(friend)-[:VISITED]->(restaurant:Restaurant)
        RETURN restaurant.id AS restaurant_id, COUNT(*) AS friend_visit_count
    $$, jsonb_build_object('user_id', 123))
    AS (restaurant_id agtype, friend_visit_count agtype)
)
-- 5. 综合排序
SELECT
    r.id,
    r.name,
    r.cuisine_type,
    r.specifications ->> 'price_range' AS price,           -- JSONB
    nr.distance / 1000 AS distance_km,                     -- 空间
    sm.semantic_score,                                     -- 向量
    km.keyword_score,                                      -- 全文
    COALESCE(fv.friend_visit_count::int, 0) AS friend_visits,  -- 图
    rv.avg_rating,                                         -- 关系
    (
        (5000 - nr.distance) / 5000 * 20.0 +              -- 距离20%
        COALESCE(sm.semantic_score, 0) * 25.0 +           -- 语义25%
        COALESCE(km.keyword_score, 0) * 15.0 +            -- 关键词15%
        COALESCE(fv.friend_visit_count::numeric, 0) * 20.0 + -- 社交20%
        COALESCE(rv.avg_rating, 0) * 20.0                 -- 评分20%
    ) AS final_score
FROM restaurants r
JOIN nearby_restaurants nr ON r.id = nr.id
LEFT JOIN semantic_matches sm ON r.id = sm.id
LEFT JOIN keyword_matches km ON r.id = km.id
LEFT JOIN friend_visited fv ON r.id = fv.restaurant_id::int
LEFT JOIN (
    SELECT restaurant_id, AVG(rating) AS avg_rating
    FROM reviews
    GROUP BY restaurant_id
) rv ON r.id = rv.restaurant_id
WHERE r.specifications @> '{"vegetarian_options": true}'   -- JSONB过滤
  AND r.is_open = TRUE
ORDER BY final_score DESC
LIMIT 10;
```

**这个查询整合了5种数据模型！** 🏆

---

## 9. 性能优化

### 9.1 混合查询优化原则

```sql
-- 原则1：先过滤，后JOIN
-- ❌ 坏：大表直接JOIN
SELECT * FROM large_table1 t1
JOIN large_table2 t2 ON t1.id = t2.ref_id
WHERE t1.category = 'tech';

-- ✅ 好：先过滤再JOIN
WITH filtered AS (
    SELECT * FROM large_table1 WHERE category = 'tech'
)
SELECT * FROM filtered f
JOIN large_table2 t2 ON f.id = t2.ref_id;

-- 原则2：利用索引
-- 确保每种数据模型的过滤列都有索引
CREATE INDEX ON products(category);                    -- 结构化
CREATE INDEX ON products USING GIN(specifications);    -- JSONB
CREATE INDEX ON restaurants USING GIST(location);     -- 空间
CREATE INDEX ON articles USING GIN(search_vector);    -- 全文
CREATE INDEX ON documents USING hnsw(embedding vector_l2_ops);  -- 向量

-- 原则3：控制结果集大小
-- 在每个子查询中使用LIMIT
-- 避免笛卡尔积
```

### 9.2 CTE vs 子查询

```sql
-- CTE（可读性好）
WITH
step1 AS (SELECT ...),
step2 AS (SELECT ... FROM step1),
step3 AS (SELECT ... FROM step2)
SELECT * FROM step3;

-- 子查询（可能更优化）
SELECT * FROM (
    SELECT * FROM (
        SELECT ...
    ) sub1
) sub2;

-- PostgreSQL 12+：CTE内联优化
-- 使用MATERIALIZED强制物化
WITH step1 AS MATERIALIZED (
    SELECT * FROM large_table WHERE ...
)
SELECT * FROM step1;
```

---

## 10. 生产实战案例

### 10.1 案例1：智能电商搜索

```sql
-- 整合7种能力：关系+JSONB+向量+全文+空间+时序+图
CREATE OR REPLACE FUNCTION smart_product_search(
    query_text TEXT,
    query_embedding vector(1536),
    user_id INT,
    user_location GEOMETRY(Point, 4326),
    limit_results INT DEFAULT 20
) RETURNS TABLE (
    product_id INT,
    product_name TEXT,
    final_score NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH
    -- 1. 向量语义搜索
    semantic_results AS (
        SELECT id, (1.0 - (embedding <=> query_embedding)) AS score
        FROM products
        ORDER BY embedding <=> query_embedding
        LIMIT 200
    ),
    -- 2. 全文关键词搜索
    keyword_results AS (
        SELECT id, ts_rank_cd(search_vector, websearch_to_tsquery('english', query_text)) AS score
        FROM products
        WHERE search_vector @@ websearch_to_tsquery('english', query_text)
        LIMIT 200
    ),
    -- 3. 用户历史偏好（时序）
    user_preference AS (
        SELECT
            specifications ->> 'category' AS preferred_category,
            COUNT(*) AS view_count
        FROM user_views uv
        JOIN products p ON uv.product_id = p.id
        WHERE uv.user_id = smart_product_search.user_id
          AND uv.viewed_at >= NOW() - INTERVAL '30 days'
        GROUP BY preferred_category
        ORDER BY view_count DESC
        LIMIT 3
    ),
    -- 4. 社交推荐（图）
    friend_likes AS (
        SELECT * FROM cypher('social', $$
            MATCH (user:Person {id: $user_id})-[:FRIEND]->(friend)-[:LIKED]->(product:Product)
            RETURN product.id AS product_id, COUNT(*) AS friend_like_count
        $$, jsonb_build_object('user_id', smart_product_search.user_id))
        AS (product_id agtype, friend_like_count agtype)
    ),
    -- 5. 位置相关（空间）
    nearby_sellers AS (
        SELECT DISTINCT ps.product_id, (10000 - ST_Distance(s.location::geography, user_location::geography)) AS proximity_score
        FROM product_sellers ps
        JOIN sellers s ON ps.seller_id = s.id
        WHERE ST_DWithin(s.location::geography, user_location::geography, 10000)
    )
    -- 6. 综合评分
    SELECT
        p.id,
        p.name,
        (
            COALESCE(sr.score, 0) * 0.25 +                                    -- 语义25%
            COALESCE(kr.score, 0) * 0.15 +                                    -- 关键词15%
            CASE WHEN up.preferred_category = p.specifications ->> 'category'
                 THEN 0.15 ELSE 0 END +                                        -- 偏好15%
            COALESCE(fl.friend_like_count::numeric, 0) / 10 * 0.20 +         -- 社交20%
            COALESCE(ns.proximity_score, 0) / 10000 * 0.10 +                 -- 位置10%
            p.rating / 5.0 * 0.15                                             -- 评分15%
        )::NUMERIC AS final_score
    FROM products p
    LEFT JOIN semantic_results sr ON p.id = sr.id
    LEFT JOIN keyword_results kr ON p.id = kr.id
    LEFT JOIN user_preference up ON TRUE
    LEFT JOIN friend_likes fl ON p.id = fl.product_id::int
    LEFT JOIN nearby_sellers ns ON p.id = ns.product_id
    WHERE p.in_stock = TRUE
      AND (sr.id IS NOT NULL OR kr.id IS NOT NULL)
    ORDER BY final_score DESC
    LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;

-- 使用
SELECT * FROM smart_product_search(
    'gaming laptop',
    '[...]'::vector(1536),
    123,
    ST_SetSRID(ST_MakePoint(116.40, 39.90), 4326),
    20
);
```

**这个查询整合了7种能力！** 🏆🏆🏆

---

## 11. 最佳实践

### 11.1 混合查询设计原则

```text
✅ 1. 明确查询意图
   - 主要筛选条件是什么？
   - 哪种模型最适合该条件？
   - 其他模型作为增强

✅ 2. 合理分配权重
   - 根据业务重要性
   - A/B测试调优
   - 监控用户行为反馈

✅ 3. 性能优先
   - 先用高选择性条件过滤
   - 控制每个步骤的结果集大小
   - 利用索引

✅ 4. 渐进式复杂化
   - 先实现基础功能
   - 再添加混合模型
   - 逐步调优

✅ 5. 可解释性
   - 记录评分逻辑
   - 可调整权重
   - 便于Debug
```

### 11.2 性能优化Checklist

- [ ] 每种模型都有适当索引
- [ ] 使用EXPLAIN ANALYZE分析
- [ ] 控制每个CTE的结果集大小（LIMIT）
- [ ] 避免不必要的模型（只用需要的）
- [ ] 考虑物化视图缓存复杂查询
- [ ] 监控查询性能
- [ ] 定期更新统计信息（ANALYZE）

---

## 📚 延伸阅读

### 相关指南

1. [PostgreSQL混合数据库完整能力图谱](../../01-基础入门/【综合】PostgreSQL混合数据库完整能力图谱.md) - 总览
2. [Apache AGE图数据库指南](../../12-扩展开发/【深入】Apache AGE图数据库完整实战指南.md)
3. [PostGIS空间数据库指南](../../03-数据类型/【深入】PostGIS空间数据库完整实战指南.md)
4. [TimescaleDB时序数据库指南](../../03-数据类型/【深入】TimescaleDB时序数据库完整实战指南.md)
5. [pgvector向量数据库指南](../../14-AI与机器学习/【深入】pgvector向量数据库与AI集成完整指南.md)
6. [PostgreSQL全文搜索指南](./【深入】PostgreSQL全文搜索完整实战指南.md)
7. [JSON/JSONB高级查询指南](../../03-数据类型/【深入】JSON-JSONB高级查询完整指南.md)

---

## ✅ 学习检查清单

- [ ] 理解混合查询的概念和价值
- [ ] 能编写2种模型的混合查询
- [ ] 能编写3+模型的混合查询
- [ ] 掌握混合查询性能优化
- [ ] 能设计权重评分系统
- [ ] 理解各模型的适用场景
- [ ] 能进行混合查询调优

---

**文档维护**: 本文档持续更新以反映PostgreSQL混合查询最佳实践。
**反馈**: 如发现错误或有改进建议，请提交issue。

**版本历史**:

- v1.0 (2025-01): 初始版本，覆盖7种混合查询模式
