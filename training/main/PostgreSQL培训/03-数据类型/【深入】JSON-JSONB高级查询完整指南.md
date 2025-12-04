# 【深入】JSON/JSONB高级查询完整指南

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 12+
> **难度等级**: ⭐⭐⭐⭐ 高级 | **预计学习时间**: 6-8小时

---

## 📋 目录

- [【深入】JSON/JSONB高级查询完整指南](#深入jsonjsonb高级查询完整指南)
  - [📋 目录](#-目录)
  - [1. 课程概述](#1-课程概述)
    - [1.1 为什么使用JSON/JSONB？](#11-为什么使用jsonjsonb)
      - [适用场景](#适用场景)
    - [1.2 核心优势](#12-核心优势)
  - [2. JSON vs JSONB](#2-json-vs-jsonb)
    - [2.1 核心区别](#21-核心区别)
    - [2.2 性能对比](#22-性能对比)
  - [3. 基础操作](#3-基础操作)
    - [3.1 创建与插入](#31-创建与插入)
    - [3.2 提取数据](#32-提取数据)
    - [3.3 修改数据](#33-修改数据)
    - [3.4 检查存在性](#34-检查存在性)
  - [4. 高级查询](#4-高级查询)
    - [4.1 数组操作](#41-数组操作)
    - [4.2 对象操作](#42-对象操作)
    - [4.3 类型转换与验证](#43-类型转换与验证)
    - [4.4 聚合函数](#44-聚合函数)
  - [5. JSON路径表达式](#5-json路径表达式)
    - [5.1 JSONPath语法](#51-jsonpath语法)
    - [5.2 JSONPath操作符](#52-jsonpath操作符)
  - [6. 索引优化](#6-索引优化)
    - [6.1 GIN索引](#61-gin索引)
    - [6.2 表达式索引](#62-表达式索引)
    - [6.3 部分索引](#63-部分索引)
    - [6.4 索引选择建议](#64-索引选择建议)
  - [7. 聚合与统计](#7-聚合与统计)
    - [7.1 统计分析](#71-统计分析)
    - [7.2 复杂聚合](#72-复杂聚合)
  - [8. 数据验证](#8-数据验证)
    - [8.1 CHECK约束](#81-check约束)
    - [8.2 JSON Schema验证](#82-json-schema验证)
  - [9. 性能优化](#9-性能优化)
    - [9.1 查询优化](#91-查询优化)
    - [9.2 存储优化](#92-存储优化)
    - [9.3 批量操作](#93-批量操作)
  - [10. 生产实战案例](#10-生产实战案例)
    - [10.1 案例1：产品规格系统](#101-案例1产品规格系统)
    - [10.2 案例2：用户自定义字段](#102-案例2用户自定义字段)
    - [10.3 案例3：API响应缓存](#103-案例3api响应缓存)
  - [11. 与MongoDB对比](#11-与mongodb对比)
    - [11.1 功能对比](#111-功能对比)
    - [11.2 选择建议](#112-选择建议)
  - [12. 最佳实践](#12-最佳实践)
    - [12.1 设计原则](#121-设计原则)
    - [12.2 查询优化Checklist](#122-查询优化checklist)
    - [12.3 安全注意事项](#123-安全注意事项)
  - [📚 延伸阅读](#-延伸阅读)
    - [官方资源](#官方资源)
    - [推荐工具](#推荐工具)
  - [✅ 学习检查清单](#-学习检查清单)
  - [💡 下一步学习](#-下一步学习)

---

## 1. 课程概述

### 1.1 为什么使用JSON/JSONB？

**PostgreSQL的JSON支持** 让关系数据库也能处理文档型数据，实现混合数据模型。

#### 适用场景

| 场景 | 说明 | 示例 |
|------|------|------|
| **灵活Schema** | 字段不固定 | 用户自定义属性、产品规格 |
| **嵌套数据** | 对象或数组 | 订单明细、评论列表 |
| **API数据** | 存储JSON响应 | 第三方API缓存 |
| **日志数据** | 结构化日志 | 应用日志、事件追踪 |
| **配置数据** | 应用配置 | 功能开关、用户偏好 |

### 1.2 核心优势

```text
PostgreSQL JSON vs MongoDB:

✅ 优势：
1. ACID事务保证
2. 关系数据 + 文档数据混合
3. 强大的SQL查询能力
4. 丰富的索引类型
5. 数据一致性保证
6. 无需学习新查询语言

⚠️ 劣势：
1. 大规模纯文档场景不如MongoDB
2. 水平扩展需自行实现
3. Schema-less带来的灵活性略逊

适用场景：
✅ 混合数据模型（关系+文档）
✅ 需要ACID保证
✅ 已使用PostgreSQL
✅ 复杂JOIN查询
```

---

## 2. JSON vs JSONB

### 2.1 核心区别

| 特性 | JSON | JSONB |
|------|------|-------|
| **存储格式** | 文本 | 二进制 |
| **写入速度** | 快 | 稍慢（需解析） |
| **查询速度** | 慢（需解析） | 快（预解析） |
| **索引支持** | ❌ 无 | ✅ GIN/GiST |
| **空格保留** | ✅ 保留 | ❌ 去除 |
| **键顺序** | ✅ 保留 | ❌ 不保证 |
| **重复键** | ✅ 允许 | ❌ 保留最后一个 |
| **推荐使用** | 极少数场景 | ✅ 99%场景 |

### 2.2 性能对比

```sql
-- 创建测试表
CREATE TABLE json_test (
    id SERIAL PRIMARY KEY,
    data_json JSON,
    data_jsonb JSONB
);

-- 插入100万条数据
INSERT INTO json_test (data_json, data_jsonb)
SELECT
    jsonb_build_object('name', 'User' || i, 'age', (random() * 100)::int, 'city', 'City' || (i % 100)),
    jsonb_build_object('name', 'User' || i, 'age', (random() * 100)::int, 'city', 'City' || (i % 100))
FROM generate_series(1, 1000000) i;

-- 查询性能对比
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM json_test WHERE data_json->>'age' = '25';
-- Execution Time: ~8000ms（全表扫描）

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM json_test WHERE data_jsonb->>'age' = '25';
-- Execution Time: ~7500ms（稍快，但仍全表扫描）

-- 创建GIN索引（只支持JSONB）
CREATE INDEX json_test_jsonb_idx ON json_test USING GIN(data_jsonb);

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM json_test WHERE data_jsonb @> '{"age": 25}';
-- Execution Time: ~50ms（索引扫描，150倍提升！）
```

**结论**：**99%情况使用JSONB**，只有需要精确保留格式时用JSON。

---

## 3. 基础操作

### 3.1 创建与插入

```sql
-- 创建表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    profile JSONB
);

-- 插入数据
INSERT INTO users (name, profile) VALUES
('Alice', '{"age": 30, "city": "Beijing", "hobbies": ["reading", "coding"]}'),
('Bob', '{"age": 25, "city": "Shanghai", "skills": {"language": ["Python", "Go"], "database": ["PostgreSQL"]}}');

-- 使用json_build_object构建
INSERT INTO users (name, profile) VALUES
('Carol', jsonb_build_object(
    'age', 28,
    'city', 'Guangzhou',
    'contact', jsonb_build_object(
        'email', 'carol@example.com',
        'phone', '13800138000'
    )
));
```

### 3.2 提取数据

```sql
-- -> 提取JSON对象/数组元素（返回JSONB）
SELECT profile -> 'age' FROM users WHERE name = 'Alice';
-- 结果：30

SELECT profile -> 'hobbies' FROM users WHERE name = 'Alice';
-- 结果：["reading", "coding"]

-- ->> 提取JSON对象/数组元素（返回TEXT）
SELECT profile ->> 'city' FROM users WHERE name = 'Alice';
-- 结果：Beijing（TEXT类型）

-- #> 通过路径提取（返回JSONB）
SELECT profile #> '{skills, language}' FROM users WHERE name = 'Bob';
-- 结果：["Python", "Go"]

-- #>> 通过路径提取（返回TEXT）
SELECT profile #>> '{skills, language, 0}' FROM users WHERE name = 'Bob';
-- 结果：Python

-- jsonb_extract_path系列函数
SELECT jsonb_extract_path(profile, 'contact', 'email') FROM users WHERE name = 'Carol';
-- 结果："carol@example.com"

SELECT jsonb_extract_path_text(profile, 'contact', 'email') FROM users WHERE name = 'Carol';
-- 结果：carol@example.com（TEXT）
```

### 3.3 修改数据

```sql
-- || 合并/覆盖
UPDATE users
SET profile = profile || '{"city": "Shenzhen"}'
WHERE name = 'Alice';

-- jsonb_set 设置值
UPDATE users
SET profile = jsonb_set(profile, '{age}', '31')
WHERE name = 'Alice';

-- 嵌套路径设置
UPDATE users
SET profile = jsonb_set(profile, '{contact, email}', '"alice@newdomain.com"', true)
WHERE name = 'Alice';
-- 第4个参数true表示路径不存在时创建

-- jsonb_insert 插入值
UPDATE users
SET profile = jsonb_insert(profile, '{hobbies, 0}', '"swimming"', true)
WHERE name = 'Alice';
-- 在数组第0位前插入

-- - 删除键
UPDATE users
SET profile = profile - 'city'
WHERE name = 'Alice';

-- #- 删除路径
UPDATE users
SET profile = profile #- '{contact, phone}'
WHERE name = 'Carol';
```

### 3.4 检查存在性

```sql
-- ? 键是否存在
SELECT name FROM users WHERE profile ? 'age';
-- 返回所有有age键的用户

-- ?| 任一键存在
SELECT name FROM users WHERE profile ?| array['age', 'city'];
-- 返回有age或city的用户

-- ?& 所有键存在
SELECT name FROM users WHERE profile ?& array['age', 'city'];
-- 返回同时有age和city的用户

-- @> 包含（左包含右）
SELECT name FROM users WHERE profile @> '{"city": "Beijing"}';
-- 返回city为Beijing的用户

-- <@ 被包含（左被右包含）
SELECT name FROM users WHERE '{"age": 30}' <@ profile;
-- 返回包含age=30的用户
```

---

## 4. 高级查询

### 4.1 数组操作

```sql
-- jsonb_array_elements 展开数组
SELECT u.name, hobby
FROM users u, jsonb_array_elements_text(u.profile -> 'hobbies') hobby
WHERE u.profile ? 'hobbies';

-- 结果：
-- Alice | reading
-- Alice | coding

-- jsonb_array_length 数组长度
SELECT name, jsonb_array_length(profile -> 'hobbies') AS hobby_count
FROM users
WHERE profile ? 'hobbies';

-- jsonb_array_elements 数组元素（保留JSON类型）
SELECT elem
FROM users, jsonb_array_elements(profile -> 'skills' -> 'language') elem
WHERE name = 'Bob';

-- 数组包含查询
SELECT name
FROM users
WHERE profile -> 'hobbies' ? 'coding';
-- 返回hobbies包含"coding"的用户

-- 数组条件查询
SELECT name
FROM users
WHERE EXISTS (
    SELECT 1
    FROM jsonb_array_elements_text(profile -> 'hobbies') hobby
    WHERE hobby = 'reading'
);
```

### 4.2 对象操作

```sql
-- jsonb_each 展开对象为键值对
SELECT key, value
FROM users, jsonb_each(profile)
WHERE name = 'Alice';

-- 结果：
-- age    | 30
-- city   | "Beijing"
-- hobbies| ["reading", "coding"]

-- jsonb_each_text 展开对象（值为TEXT）
SELECT key, value
FROM users, jsonb_each_text(profile)
WHERE name = 'Alice';

-- jsonb_object_keys 获取所有键
SELECT DISTINCT jsonb_object_keys(profile) AS keys
FROM users;

-- 统计键的使用频率
SELECT key, COUNT(*) AS count
FROM users, jsonb_object_keys(profile) key
GROUP BY key
ORDER BY count DESC;
```

### 4.3 类型转换与验证

```sql
-- jsonb_typeof 获取类型
SELECT
    profile ->> 'age' AS age,
    jsonb_typeof(profile -> 'age') AS age_type,
    jsonb_typeof(profile -> 'hobbies') AS hobbies_type
FROM users
WHERE name = 'Alice';

-- 结果：
-- age | age_type | hobbies_type
-- 30  | number   | array

-- 类型检查
SELECT name
FROM users
WHERE jsonb_typeof(profile -> 'age') = 'number'
  AND (profile ->> 'age')::int > 25;

-- 安全的类型转换
SELECT
    name,
    CASE
        WHEN jsonb_typeof(profile -> 'age') = 'number'
        THEN (profile ->> 'age')::int
        ELSE NULL
    END AS age
FROM users;
```

### 4.4 聚合函数

```sql
-- jsonb_agg 聚合为JSON数组
SELECT jsonb_agg(profile) AS all_profiles
FROM users;

-- jsonb_object_agg 聚合为JSON对象
SELECT jsonb_object_agg(name, profile) AS users_by_name
FROM users;

-- 分组聚合
SELECT
    profile ->> 'city' AS city,
    jsonb_agg(jsonb_build_object('name', name, 'age', profile -> 'age')) AS users
FROM users
WHERE profile ? 'city'
GROUP BY profile ->> 'city';

-- 结果：
-- city     | users
-- Beijing  | [{"name": "Alice", "age": 30}]
-- Shanghai | [{"name": "Bob", "age": 25}]
```

---

## 5. JSON路径表达式

### 5.1 JSONPath语法

```sql
-- jsonb_path_query 查询路径
SELECT jsonb_path_query(
    '[
        {"name": "Alice", "age": 30, "scores": [85, 90, 95]},
        {"name": "Bob", "age": 25, "scores": [70, 80, 85]}
    ]',
    '$[*] ? (@.age > 25)'
);
-- 返回所有age>25的对象

-- jsonb_path_query_first 返回第一个匹配
SELECT jsonb_path_query_first(
    profile,
    '$.skills.language[*] ? (@ == "Python")'
) AS has_python
FROM users
WHERE name = 'Bob';

-- jsonb_path_exists 检查路径是否存在
SELECT name
FROM users
WHERE jsonb_path_exists(profile, '$.contact.email');

-- jsonb_path_match 路径匹配（返回布尔）
SELECT name
FROM users
WHERE jsonb_path_match(profile, '$.age > 25');
```

### 5.2 JSONPath操作符

```sql
-- $ 根节点
-- @ 当前节点
-- . 子节点
-- [] 数组访问
-- * 通配符
-- ? 过滤表达式

-- 复杂查询示例
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    data JSONB
);

INSERT INTO products (data) VALUES
('{"name": "Laptop", "price": 1000, "specs": {"cpu": "i7", "ram": 16}, "tags": ["electronics", "computer"]}'),
('{"name": "Phone", "price": 500, "specs": {"cpu": "A15", "ram": 6}, "tags": ["electronics", "mobile"]}'),
('{"name": "Book", "price": 30, "category": "education"}');

-- 查询价格>100且有tags的产品
SELECT data ->> 'name' AS name
FROM products
WHERE jsonb_path_exists(data, '$ ? (@.price > 100 && exists(@.tags))');

-- 查询tags包含"electronics"的产品
SELECT data ->> 'name' AS name
FROM products
WHERE jsonb_path_exists(data, '$.tags[*] ? (@ == "electronics")');

-- 查询specs.ram >= 8的产品
SELECT data ->> 'name' AS name
FROM products
WHERE jsonb_path_match(data, '$.specs.ram >= 8');
```

---

## 6. 索引优化

### 6.1 GIN索引

```sql
-- 默认GIN索引（支持@>, ?, ?&, ?|）
CREATE INDEX users_profile_gin_idx ON users USING GIN(profile);

-- 查询自动使用索引
EXPLAIN (ANALYZE)
SELECT * FROM users WHERE profile @> '{"city": "Beijing"}';
-- Index Scan using users_profile_gin_idx

-- jsonb_path_ops（更小更快，但只支持@>）
CREATE INDEX users_profile_path_idx ON users USING GIN(profile jsonb_path_ops);

-- 空间对比
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE tablename = 'users';

-- 结果：
-- users_profile_gin_idx  | 1024 kB
-- users_profile_path_idx | 512 kB  ← 更小
```

### 6.2 表达式索引

```sql
-- 索引特定键
CREATE INDEX users_city_idx ON users ((profile ->> 'city'));

-- 查询使用索引
SELECT * FROM users WHERE profile ->> 'city' = 'Beijing';

-- 索引嵌套路径
CREATE INDEX users_email_idx ON users ((profile #>> '{contact, email}'));

-- 索引数组元素
CREATE INDEX users_hobbies_idx ON users USING GIN((profile -> 'hobbies'));

SELECT * FROM users WHERE profile -> 'hobbies' ? 'coding';
-- 使用users_hobbies_idx
```

### 6.3 部分索引

```sql
-- 只索引有效用户
CREATE INDEX users_active_profile_idx ON users USING GIN(profile)
WHERE deleted_at IS NULL AND status = 'active';

-- 查询必须包含相同条件
SELECT * FROM users
WHERE profile @> '{"city": "Beijing"}'
  AND deleted_at IS NULL
  AND status = 'active';
-- 使用users_active_profile_idx
```

### 6.4 索引选择建议

```sql
-- 场景1：@>查询为主 → jsonb_path_ops（更小）
CREATE INDEX idx_name ON table USING GIN(column jsonb_path_ops);

-- 场景2：多种操作符（@>, ?, ?&, ?|） → 默认GIN
CREATE INDEX idx_name ON table USING GIN(column);

-- 场景3：查询特定键 → 表达式索引
CREATE INDEX idx_name ON table ((column ->> 'key'));

-- 场景4：数组操作 → GIN索引数组字段
CREATE INDEX idx_name ON table USING GIN((column -> 'array_field'));
```

---

## 7. 聚合与统计

### 7.1 统计分析

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_type TEXT,
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入示例数据
INSERT INTO events (event_type, event_data) VALUES
('page_view', '{"page": "/home", "duration": 30, "user_agent": "Chrome"}'),
('page_view', '{"page": "/products", "duration": 120, "user_agent": "Firefox"}'),
('purchase', '{"product_id": 123, "amount": 99.99, "quantity": 2}'),
('purchase', '{"product_id": 456, "amount": 49.99, "quantity": 1}');

-- 统计每种页面的浏览时长
SELECT
    event_data ->> 'page' AS page,
    COUNT(*) AS view_count,
    AVG((event_data ->> 'duration')::int) AS avg_duration,
    MAX((event_data ->> 'duration')::int) AS max_duration
FROM events
WHERE event_type = 'page_view'
GROUP BY event_data ->> 'page';

-- 统计销售总额
SELECT
    SUM((event_data ->> 'amount')::numeric * (event_data ->> 'quantity')::int) AS total_revenue,
    COUNT(*) AS order_count,
    AVG((event_data ->> 'amount')::numeric) AS avg_order_value
FROM events
WHERE event_type = 'purchase';
```

### 7.2 复杂聚合

```sql
-- 多维度聚合
SELECT
    DATE(created_at) AS date,
    event_type,
    jsonb_object_agg(
        COALESCE(event_data ->> 'page', event_data ->> 'product_id'),
        COUNT(*)
    ) AS counts
FROM events
GROUP BY DATE(created_at), event_type;

-- 动态透视
SELECT
    user_id,
    jsonb_object_agg(
        metric_name,
        metric_value
    ) AS metrics
FROM (
    SELECT
        event_data ->> 'user_id' AS user_id,
        'page_views' AS metric_name,
        COUNT(*) AS metric_value
    FROM events
    WHERE event_type = 'page_view'
    GROUP BY event_data ->> 'user_id'

    UNION ALL

    SELECT
        event_data ->> 'user_id' AS user_id,
        'purchases' AS metric_name,
        COUNT(*) AS metric_value
    FROM events
    WHERE event_type = 'purchase'
    GROUP BY event_data ->> 'user_id'
) sub
GROUP BY user_id;
```

---

## 8. 数据验证

### 8.1 CHECK约束

```sql
CREATE TABLE users_validated (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    profile JSONB NOT NULL,

    -- 确保age是数字
    CONSTRAINT profile_age_is_number
        CHECK (jsonb_typeof(profile -> 'age') = 'number'),

    -- 确保email格式正确
    CONSTRAINT profile_email_format
        CHECK (profile ->> 'email' ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),

    -- 确保hobbies是数组
    CONSTRAINT profile_hobbies_is_array
        CHECK (jsonb_typeof(profile -> 'hobbies') = 'array' OR profile -> 'hobbies' IS NULL)
);

-- 插入成功
INSERT INTO users_validated (name, profile) VALUES
('Alice', '{"age": 30, "email": "alice@example.com", "hobbies": ["reading"]}');

-- 插入失败（age不是数字）
INSERT INTO users_validated (name, profile) VALUES
('Bob', '{"age": "thirty", "email": "bob@example.com"}');
-- ERROR: new row violates check constraint "profile_age_is_number"
```

### 8.2 JSON Schema验证

```sql
-- 安装pg_jsonschema扩展（PostgreSQL 14+）
CREATE EXTENSION IF NOT EXISTS pg_jsonschema;

-- 定义Schema
CREATE TABLE product_schemas (
    id SERIAL PRIMARY KEY,
    schema JSONB NOT NULL
);

INSERT INTO product_schemas (schema) VALUES
('{
    "type": "object",
    "required": ["name", "price"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "price": {"type": "number", "minimum": 0},
        "tags": {"type": "array", "items": {"type": "string"}},
        "specs": {
            "type": "object",
            "properties": {
                "weight": {"type": "number"},
                "dimensions": {
                    "type": "object",
                    "properties": {
                        "length": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"}
                    }
                }
            }
        }
    }
}'::jsonb);

-- 应用Schema验证
CREATE TABLE products_validated (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,

    CONSTRAINT data_valid_schema
        CHECK (jsonb_matches_schema(
            (SELECT schema FROM product_schemas LIMIT 1),
            data
        ))
);

-- 插入成功
INSERT INTO products_validated (data) VALUES
('{"name": "Laptop", "price": 999.99, "tags": ["electronics"], "specs": {"weight": 1.5}}');

-- 插入失败（缺少required字段）
INSERT INTO products_validated (data) VALUES
('{"name": "Phone"}');
-- ERROR: violates check constraint "data_valid_schema"
```

---

## 9. 性能优化

### 9.1 查询优化

```sql
-- ❌ 慢：动态提取+类型转换
SELECT * FROM users
WHERE (profile ->> 'age')::int > 25;

-- ✅ 快：使用@>（可用索引）
SELECT * FROM users
WHERE profile @> '{"city": "Beijing"}';

-- ✅ 更快：表达式索引
CREATE INDEX users_age_idx ON users (((profile ->> 'age')::int));
SELECT * FROM users WHERE (profile ->> 'age')::int > 25;
```

### 9.2 存储优化

```sql
-- 压缩JSONB（使用TOAST）
ALTER TABLE users ALTER COLUMN profile SET STORAGE EXTENDED;

-- 查看压缩效果
SELECT
    pg_column_size(profile) AS raw_size,
    pg_column_size(profile::text) AS text_size,
    length(profile::text) AS json_length
FROM users
LIMIT 5;
```

### 9.3 批量操作

```sql
-- 批量更新
UPDATE users
SET profile = jsonb_set(profile, '{updated_at}', to_jsonb(NOW()::text))
WHERE id IN (SELECT id FROM users LIMIT 10000);

-- 使用临时表优化大批量操作
CREATE TEMP TABLE updates (
    id INT,
    new_profile JSONB
);

INSERT INTO updates
SELECT id, profile || '{"batch_updated": true}'::jsonb
FROM users
WHERE created_at < '2025-01-01';

UPDATE users u
SET profile = up.new_profile
FROM updates up
WHERE u.id = up.id;
```

---

## 10. 生产实战案例

### 10.1 案例1：产品规格系统

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    base_price NUMERIC(10,2) NOT NULL,
    specifications JSONB NOT NULL,  -- 灵活的规格数据
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入不同类型产品（规格完全不同）
INSERT INTO products (sku, name, category, base_price, specifications) VALUES
(
    'LAPTOP-001',
    'Gaming Laptop',
    'Electronics',
    1299.99,
    '{
        "brand": "Dell",
        "processor": {"model": "Intel i7-12700H", "cores": 14, "base_clock": 2.3},
        "memory": {"size_gb": 16, "type": "DDR5"},
        "storage": [{"type": "SSD", "capacity_gb": 512}, {"type": "HDD", "capacity_gb": 1000}],
        "display": {"size_inch": 15.6, "resolution": "1920x1080", "refresh_rate_hz": 144},
        "graphics": {"model": "RTX 3060", "vram_gb": 6}
    }'
),
(
    'BOOK-001',
    'PostgreSQL Guide',
    'Books',
    29.99,
    '{
        "author": "John Doe",
        "publisher": "TechPress",
        "isbn": "978-1234567890",
        "pages": 450,
        "language": "English",
        "binding": "Paperback",
        "dimensions": {"length_cm": 23, "width_cm": 15, "height_cm": 2.5}
    }'
);

-- 创建索引
CREATE INDEX products_specifications_gin_idx ON products USING GIN(specifications);
CREATE INDEX products_category_idx ON products(category);

-- 查询：16GB内存的笔记本
SELECT name, base_price, specifications -> 'memory' AS memory
FROM products
WHERE category = 'Electronics'
  AND specifications @> '{"memory": {"size_gb": 16}}';

-- 查询：多个存储设备的产品
SELECT name, specifications -> 'storage' AS storage
FROM products
WHERE jsonb_array_length(specifications -> 'storage') > 1;

-- 动态过滤（用户自定义搜索）
CREATE OR REPLACE FUNCTION search_products(
    search_specs JSONB
) RETURNS TABLE (
    id INT,
    name TEXT,
    base_price NUMERIC,
    specifications JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.base_price, p.specifications
    FROM products p
    WHERE p.specifications @> search_specs
    ORDER BY p.base_price;
END;
$$ LANGUAGE plpgsql;

-- 使用
SELECT * FROM search_products('{"memory": {"size_gb": 16}}');
```

### 10.2 案例2：用户自定义字段

```sql
CREATE TABLE custom_forms (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,
    form_name TEXT NOT NULL,
    form_schema JSONB NOT NULL,  -- 表单定义
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE form_submissions (
    id SERIAL PRIMARY KEY,
    form_id INT REFERENCES custom_forms(id),
    user_id INT,
    form_data JSONB NOT NULL,  -- 用户填写的数据
    submitted_at TIMESTAMPTZ DEFAULT NOW()
);

-- 租户A定义表单
INSERT INTO custom_forms (tenant_id, form_name, form_schema) VALUES
(1, 'Customer Feedback', '{
    "fields": [
        {"name": "name", "type": "text", "required": true},
        {"name": "email", "type": "email", "required": true},
        {"name": "rating", "type": "number", "min": 1, "max": 5, "required": true},
        {"name": "comments", "type": "textarea", "required": false},
        {"name": "would_recommend", "type": "boolean", "required": true}
    ]
}');

-- 用户提交表单
INSERT INTO form_submissions (form_id, user_id, form_data) VALUES
(1, 123, '{
    "name": "Alice Wang",
    "email": "alice@example.com",
    "rating": 5,
    "comments": "Excellent service!",
    "would_recommend": true
}');

-- 统计分析
SELECT
    AVG((form_data ->> 'rating')::int) AS avg_rating,
    COUNT(*) FILTER (WHERE (form_data ->> 'would_recommend')::boolean = true) AS would_recommend_count,
    COUNT(*) AS total_submissions
FROM form_submissions
WHERE form_id = 1;

-- 动态报表生成
SELECT
    jsonb_object_agg(
        field_name,
        jsonb_build_object(
            'count', field_count,
            'sample', sample_values
        )
    ) AS field_analysis
FROM (
    SELECT
        key AS field_name,
        COUNT(*) AS field_count,
        jsonb_agg(value ORDER BY random() LIMIT 5) AS sample_values
    FROM form_submissions, jsonb_each(form_data)
    WHERE form_id = 1
    GROUP BY key
) sub;
```

### 10.3 案例3：API响应缓存

```sql
CREATE TABLE api_cache (
    id SERIAL PRIMARY KEY,
    api_endpoint TEXT NOT NULL,
    request_params JSONB NOT NULL,
    response_data JSONB NOT NULL,
    status_code INT NOT NULL,
    cache_ttl INTERVAL NOT NULL DEFAULT '1 hour',
    cached_at TIMESTAMPTZ DEFAULT NOW(),

    -- 复合唯一索引
    UNIQUE (api_endpoint, request_params)
);

-- GIN索引支持查询
CREATE INDEX api_cache_response_gin_idx ON api_cache USING GIN(response_data);
CREATE INDEX api_cache_cached_at_idx ON api_cache(cached_at);

-- 缓存API响应
INSERT INTO api_cache (api_endpoint, request_params, response_data, status_code)
VALUES (
    '/api/users',
    '{"filters": {"city": "Beijing", "age": ">25"}, "sort": "created_at", "limit": 100}',
    '[{"id": 1, "name": "Alice", "city": "Beijing", "age": 30}, ...]',
    200
)
ON CONFLICT (api_endpoint, request_params) DO UPDATE
SET
    response_data = EXCLUDED.response_data,
    status_code = EXCLUDED.status_code,
    cached_at = NOW();

-- 查询缓存（带TTL检查）
SELECT response_data, status_code
FROM api_cache
WHERE api_endpoint = '/api/users'
  AND request_params = '{"filters": {"city": "Beijing", "age": ">25"}, "sort": "created_at", "limit": 100}'
  AND cached_at > NOW() - cache_ttl;

-- 定期清理过期缓存
DELETE FROM api_cache
WHERE cached_at < NOW() - cache_ttl;
```

---

## 11. 与MongoDB对比

### 11.1 功能对比

| 特性 | PostgreSQL JSONB | MongoDB |
|------|------------------|---------|
| **ACID事务** | ✅ 完整 | ⚠️ 有限（单文档/4.0+多文档） |
| **Schema灵活性** | ⚠️ 混合模式 | ✅ Schema-less |
| **查询语言** | ✅ SQL | ⚠️ 自定义查询语言 |
| **JOIN** | ✅ 原生支持 | ⚠️ $lookup（性能差） |
| **索引类型** | ✅ 丰富（GIN、GiST、B-tree） | ✅ 多种 |
| **水平扩展** | ⚠️ 需扩展（Citus） | ✅ 原生分片 |
| **性能（纯文档）** | ⚠️ 良好 | ✅ 优秀 |
| **性能（混合查询）** | ✅ 优秀 | ❌ 不支持 |
| **运维复杂度** | ✅ 低 | ⚠️ 中 |

### 11.2 选择建议

```text
选择PostgreSQL JSONB，如果：
✅ 需要ACID事务保证
✅ 混合数据模型（关系+文档）
✅ 复杂JOIN查询
✅ 团队熟悉SQL
✅ 已有PostgreSQL基础设施
✅ 数据一致性优先

选择MongoDB，如果：
✅ 纯文档存储
✅ 极致的Schema灵活性
✅ 需要原生水平扩展
✅ 大规模文档数据（>TB级）
✅ 团队熟悉MongoDB
✅ 性能优先于一致性
```

---

## 12. 最佳实践

### 12.1 设计原则

```sql
-- ✅ 1. 关键数据使用结构化列，灵活数据使用JSONB
CREATE TABLE products (
    id SERIAL PRIMARY KEY,              -- 结构化
    sku TEXT UNIQUE NOT NULL,           -- 结构化
    name TEXT NOT NULL,                 -- 结构化
    base_price NUMERIC(10,2) NOT NULL,  -- 结构化
    specifications JSONB NOT NULL,      -- 灵活（JSONB）
    metadata JSONB                      -- 可选扩展（JSONB）
);

-- ✅ 2. 使用99%情况使用JSONB而非JSON
-- ✅ 3. 为常用查询创建GIN索引
CREATE INDEX products_specifications_idx ON products USING GIN(specifications);

-- ✅ 4. 为频繁访问的键创建表达式索引
CREATE INDEX products_brand_idx ON products ((specifications ->> 'brand'));

-- ✅ 5. 使用CHECK约束验证数据
ALTER TABLE products ADD CONSTRAINT specifications_has_brand
    CHECK (specifications ? 'brand');
```

### 12.2 查询优化Checklist

- [ ] 使用JSONB而非JSON（99%场景）
- [ ] 创建GIN索引支持查询
- [ ] 使用@>而非->>进行包含查询
- [ ] 为频繁查询的键创建表达式索引
- [ ] 使用jsonb_path_ops减小索引大小
- [ ] 避免在SELECT中提取整个JSONB对象
- [ ] 定期VACUUM ANALYZE
- [ ] 监控查询性能（pg_stat_statements）

### 12.3 安全注意事项

```sql
-- ⚠️ 防止JSON注入
-- ❌ 危险：直接拼接
query := format('SELECT * FROM users WHERE profile @> %s', user_input);

-- ✅ 安全：使用参数化查询
PREPARE get_users AS
SELECT * FROM users WHERE profile @> $1;

EXECUTE get_users('{"city": "Beijing"}');

-- ⚠️ 验证输入
-- 确保输入是有效JSON
SELECT * FROM users WHERE profile @> $1::jsonb;
-- 如果$1不是有效JSON，会抛出错误
```

---

## 📚 延伸阅读

### 官方资源

- [PostgreSQL JSON Functions](https://www.postgresql.org/docs/current/functions-json.html)
- [JSONB Indexing](https://www.postgresql.org/docs/current/datatype-json.html#JSON-INDEXING)
- [JSON Path](https://www.postgresql.org/docs/current/functions-json.html#FUNCTIONS-SQLJSON-PATH)

### 推荐工具

- **pgAdmin**: 可视化查看JSONB
- **jq**: 命令行JSON处理工具
- **JSON Schema**: Schema验证标准

---

## ✅ 学习检查清单

- [ ] 理解JSON vs JSONB区别
- [ ] 掌握JSONB基础操作符
- [ ] 能够提取和修改JSONB数据
- [ ] 理解GIN索引原理和使用
- [ ] 掌握JSONPath查询
- [ ] 能够进行JSONB聚合分析
- [ ] 理解性能优化技巧
- [ ] 能够设计混合数据模型

---

## 💡 下一步学习

1. **进阶主题**:
   - JSONB性能深度优化
   - 自定义JSON操作符
   - JSONB与全文搜索结合

2. **相关课程**:
   - [PostgreSQL全文搜索](./【深入】PostgreSQL全文搜索完整实战指南.md)
   - [PostgreSQL性能调优](../11-性能调优/)

---

**文档维护**: 本文档持续更新以反映PostgreSQL JSON特性最新发展。
**反馈**: 如发现错误或有改进建议，请提交issue。

**版本历史**:

- v1.0 (2025-01): 初始版本，覆盖PostgreSQL 12+ JSON/JSONB核心特性
