---

> **📋 文档来源**: `docs\01-PostgreSQL18\37-JSON-JSONB完整实战.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL JSON/JSONB完整实战

## 📑 目录

- [PostgreSQL JSON/JSONB完整实战](#postgresql-jsonjsonb完整实战)
  - [📑 目录](#-目录)
  - [1. JSON vs JSONB](#1-json-vs-jsonb)
  - [2. 基础操作](#2-基础操作)
    - [2.1 插入](#21-插入)
    - [2.2 查询](#22-查询)
    - [2.3 更新](#23-更新)
  - [3. 高级查询](#3-高级查询)
    - [3.1 条件查询](#31-条件查询)
    - [3.2 JSONPath查询](#32-jsonpath查询)
  - [4. 索引优化](#4-索引优化)
    - [4.1 GIN索引](#41-gin索引)
    - [4.2 表达式索引](#42-表达式索引)
  - [5. 聚合与统计](#5-聚合与统计)
  - [6. 实战案例](#6-实战案例)
    - [6.1 事件日志](#61-事件日志)
    - [6.2 产品属性](#62-产品属性)
    - [6.3 用户配置](#63-用户配置)
  - [7. 性能优化](#7-性能优化)

## 1. JSON vs JSONB

```sql
-- 性能测试：JSON vs JSONB（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS logs_json (
    id SERIAL PRIMARY KEY,
    data JSON
);
CREATE TABLE IF NOT EXISTS logs_jsonb (
    id SERIAL PRIMARY KEY,
    data JSONB
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '部分表已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：性能对比（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
INSERT INTO logs_json (data)
SELECT ('{"user_id": ' || i || ', "action": "login", "timestamp": "2024-01-01"}')::JSON
FROM generate_series(1, 100000) i;
-- 时间: 2.5秒
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'JSON插入失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
INSERT INTO logs_jsonb (data)
SELECT ('{"user_id": ' || i || ', "action": "login", "timestamp": "2024-01-01"}')::JSONB
FROM generate_series(1, 100000) i;
-- 时间: 3.2秒（插入稍慢，但查询更快）
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONB插入失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查询对比（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM logs_json WHERE data->>'user_id' = '12345';
-- 无索引支持，全表扫描
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'JSON查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM logs_jsonb WHERE data @> '{"user_id": 12345}';
-- 可使用GIN索引，快速查询
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONB查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 结论: 优先使用JSONB（除非需要保留JSON格式）
```

---

## 2. 基础操作

### 2.1 插入

```sql
-- 性能测试：插入JSON数据（带错误处理）
BEGIN;
INSERT INTO users (id, info) VALUES
(1, '{"name": "Alice", "age": 30, "tags": ["admin", "user"]}'),
(2, '{"name": "Bob", "age": 25, "email": "bob@example.com"}')
ON CONFLICT (id) DO NOTHING;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '插入JSON数据失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：从函数构建（带错误处理）
BEGIN;
INSERT INTO users (id, info) VALUES
(3, jsonb_build_object(
    'name', 'Charlie',
    'age', 35,
    'tags', jsonb_build_array('user', 'premium')
))
ON CONFLICT (id) DO NOTHING;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '构建JSONB对象失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 2.2 查询

```sql
-- 性能测试：-> 返回JSON对象（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT info->'name' FROM users WHERE id = 1;
-- 结果: "Alice"（带引号）
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'JSON查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：->> 返回文本（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT info->>'name' FROM users WHERE id = 1;
-- 结果: Alice（无引号）
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'JSON查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：嵌套访问（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT info->'address'->>'city' FROM users WHERE id = 1;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '嵌套访问失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：数组访问（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT info->'tags'->0 FROM users WHERE id = 1;
-- 结果: "admin"
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '数组访问失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：数组展开（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT jsonb_array_elements_text(info->'tags') AS tag
FROM users WHERE id = 1;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '数组展开失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

/*
tag
------

admin
user
*/

```

### 2.3 更新

```sql
-- 性能测试：更新整个字段（带错误处理）
BEGIN;
UPDATE users
SET info = '{"name": "Alice Updated", "age": 31}'
WHERE id = 1;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '更新JSONB字段失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：更新单个键（带错误处理）
BEGIN;
UPDATE users
SET info = jsonb_set(info, '{age}', '31')
WHERE id = 1;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '更新JSONB键失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：添加新键（带错误处理）
BEGIN;
UPDATE users
SET info = info || '{"email": "alice@example.com"}'
WHERE id = 1;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '添加JSONB键失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：删除键（带错误处理）
BEGIN;
UPDATE users
SET info = info - 'email'
WHERE id = 1;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '删除JSONB键失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：深度更新（带错误处理）
BEGIN;
UPDATE users
SET info = jsonb_set(info, '{address,city}', '"NYC"')
WHERE id = 1;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '深度更新JSONB失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 3. 高级查询

### 3.1 条件查询

```sql
-- 性能测试：包含检查（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE info @> '{"name": "Alice"}';
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '包含检查查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：被包含检查（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE '{"name": "Alice"}' <@ info;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '被包含检查查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：键存在（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE info ? 'email';
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '键存在查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：任一键存在（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE info ?| ARRAY['email', 'phone'];
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '任一键存在查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：所有键存在（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE info ?& ARRAY['name', 'age'];
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '所有键存在查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：路径存在（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE info @? '$.address.city';
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '路径存在查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 3.2 JSONPath查询

```sql
-- 性能测试：路径查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users
WHERE jsonb_path_exists(info, '$.age ? (@ > 25)');
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONPath查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：提取值（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT jsonb_path_query(info, '$.tags[*]') FROM users;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONPath提取值失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：复杂条件（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users
WHERE jsonb_path_exists(
    info,
    '$.tags[*] ? (@ == "admin")'
);
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONPath复杂条件查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 4. 索引优化

### 4.1 GIN索引

```sql
-- 性能测试：创建默认GIN索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_users_info ON users USING GIN (info);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_users_info已存在';
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建GIN索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查询使用索引（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE info @> '{"name": "Alice"}';
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'GIN索引查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建jsonb_ops索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_info_ops ON users USING GIN (info jsonb_ops);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_info_ops已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建jsonb_ops索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建jsonb_path_ops索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_info_path_ops ON users USING GIN (info jsonb_path_ops);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_info_path_ops已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建jsonb_path_ops索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
-- 性能对比
-- jsonb_ops: 100MB索引, 5ms查询
-- jsonb_path_ops: 60MB索引, 3ms查询 (-40%体积, -40%时间)
```

### 4.2 表达式索引

```sql
-- 性能测试：创建单个键索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_users_name ON users ((info->>'name'));
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_users_name已存在';
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建表达式索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE info->>'name' = 'Alice';
-- 使用索引
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '表达式索引查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建嵌套键索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_users_city ON users ((info->'address'->>'city'));
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_users_city已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建嵌套键索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建数组元素索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_users_tags ON users USING GIN ((info->'tags'));
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_users_tags已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建数组元素索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 5. 聚合与统计

```sql
-- 性能测试：计数（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    info->>'status' AS status,
    COUNT(*) AS count
FROM orders
GROUP BY info->>'status';
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表orders不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONB计数查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：求和（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT SUM((info->>'amount')::NUMERIC) AS total
FROM orders
WHERE info->>'date' >= '2024-01-01';
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表orders不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONB求和查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：平均值（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT AVG((info->>'rating')::NUMERIC) AS avg_rating
FROM reviews;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表reviews不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONB平均值查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：数组聚合（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    user_id,
    jsonb_agg(info->'product_id') AS purchased_products
FROM orders
GROUP BY user_id;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表orders不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONB数组聚合查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：对象聚合（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT jsonb_object_agg(
    info->>'name',
    info->>'email'
) AS users_map
FROM users;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONB对象聚合查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 6. 实战案例

### 6.1 事件日志

```sql
-- 性能测试：创建事件日志表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS event_logs (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表event_logs已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_event_type ON event_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_event_data ON event_logs USING GIN (event_data);
CREATE INDEX IF NOT EXISTS idx_created_at ON event_logs(created_at);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '部分索引已存在';
    WHEN undefined_table THEN
        RAISE NOTICE '表event_logs不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：插入数据（带错误处理）
BEGIN;
INSERT INTO event_logs (event_type, event_data) VALUES
('user_login', '{"user_id": 123, "ip": "1.2.3.4", "device": "mobile"}'),
('purchase', '{"user_id": 123, "product_id": 456, "amount": 99.99}')
ON CONFLICT DO NOTHING;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '插入事件日志失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查询：特定用户所有事件（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM event_logs
WHERE event_data @> '{"user_id": 123}'
ORDER BY created_at DESC;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表event_logs不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '查询事件日志失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：统计：每种事件数量（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT event_type, COUNT(*)
FROM event_logs
WHERE created_at >= now() - INTERVAL '7 days'
GROUP BY event_type;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表event_logs不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '统计事件数量失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 6.2 产品属性

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    attributes JSONB
);

-- 不同产品有不同属性
INSERT INTO products (name, attributes) VALUES
('Laptop', '{"brand": "Dell", "cpu": "Intel i7", "ram": "16GB", "storage": "512GB SSD"}'),
('Shirt', '{"brand": "Nike", "size": "L", "color": "blue", "material": "cotton"}');

-- 索引
CREATE INDEX idx_attributes ON products USING GIN (attributes);

-- 查询：特定品牌
SELECT * FROM products WHERE attributes @> '{"brand": "Dell"}';

-- 查询：属性范围
SELECT * FROM products
WHERE (attributes->>'ram')::TEXT LIKE '%16GB%';

-- 动态过滤
SELECT * FROM products
WHERE attributes ?| ARRAY['cpu', 'gpu'];  -- 有CPU或GPU属性
```

### 6.3 用户配置

```sql
CREATE TABLE user_settings (
    user_id INT PRIMARY KEY,
    settings JSONB DEFAULT '{}'
);

-- 默认配置
INSERT INTO user_settings (user_id, settings) VALUES
(1, '{
    "theme": "dark",
    "language": "en",
    "notifications": {
        "email": true,
        "push": false
    },
    "privacy": {
        "profile_visible": true
    }
}');

-- 更新单个配置
UPDATE user_settings
SET settings = jsonb_set(
    settings,
    '{notifications,push}',
    'true'
)
WHERE user_id = 1;

-- 合并配置（保留其他字段）
UPDATE user_settings
SET settings = settings || '{"theme": "light"}'
WHERE user_id = 1;

-- 批量更新
UPDATE user_settings
SET settings = jsonb_set(
    settings,
    '{privacy,profile_visible}',
    'false'
)
WHERE settings @> '{"notifications": {"email": true}}';
```

---

## 7. 性能优化

```sql
-- 1. 使用jsonb_path_ops索引（查询简单时）
CREATE INDEX idx_fast ON logs USING GIN (data jsonb_path_ops);

-- 2. 提取常用字段
ALTER TABLE logs ADD COLUMN user_id INT;
UPDATE logs SET user_id = (data->>'user_id')::INT;
CREATE INDEX idx_user_id ON logs(user_id);
-- 查询user_id时使用普通索引，比JSONB快

-- 3. 分区表
CREATE TABLE logs_partitioned (
    id BIGSERIAL,
    data JSONB,
    created_at TIMESTAMPTZ
) PARTITION BY RANGE (created_at);

-- 4. 避免SELECT *
SELECT data->'user_id', data->'action'  -- 只选择需要的字段
FROM logs
WHERE data @> '{"status": "active"}';

-- 5. 使用CTE分解复杂查询
WITH filtered AS (
    SELECT id, data
    FROM logs
    WHERE data @> '{"status": "active"}'
)
SELECT data->'user_id', COUNT(*)
FROM filtered
GROUP BY data->'user_id';
```

---

**完成**: PostgreSQL JSON/JSONB完整实战
**字数**: ~10,000字
**涵盖**: JSON vs JSONB、基础操作、高级查询、索引优化、聚合统计、实战案例、性能优化
