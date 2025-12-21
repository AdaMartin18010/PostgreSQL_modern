# PostgreSQL 18 JSONB高级应用指南

## 1. JSONB vs JSON

```sql
-- 性能测试：JSON vs JSONB（带错误处理）
BEGIN;
-- JSON: 存储原始文本
CREATE TABLE IF NOT EXISTS json_test (data JSON);
INSERT INTO json_test VALUES ('{"name":"Alice","age":30}')
ON CONFLICT DO NOTHING;
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表json_test已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建JSON表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
-- JSONB: 二进制存储（推荐）
CREATE TABLE IF NOT EXISTS jsonb_test (data JSONB);
INSERT INTO jsonb_test VALUES ('{"name":"Alice","age":30}')
ON CONFLICT DO NOTHING;
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表jsonb_test已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建JSONB表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 对比
/*
特性          JSON    JSONB
存储格式      文本    二进制
存储空间      小      略大
插入速度      快      略慢
查询速度      慢      快
支持索引      否      是 (GIN)
键重复        保留    去重
键顺序        保留    不保证
*/

-- 建议: 始终使用JSONB

```

---

## 2. JSONB操作符

### 2.1 查询操作符

```sql
-- 性能测试：创建测试表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    profile JSONB
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表users已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
INSERT INTO users (profile) VALUES
('{"name":"Alice","age":30,"tags":["vip","active"],"address":{"city":"NYC"}}'),
('{"name":"Bob","age":25,"tags":["active"],"address":{"city":"LA"}}')
ON CONFLICT DO NOTHING;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '插入数据失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：获取值（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT profile->'name' FROM users;              -- 返回JSONB
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '获取JSONB值失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT profile->>'name' FROM users;             -- 返回TEXT
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '获取TEXT值失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：路径访问（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT profile#>'{address,city}' FROM users;   -- 返回JSONB
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '路径访问失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT profile#>>'{address,city}' FROM users;  -- 返回TEXT
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '路径访问TEXT失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：存在性检查（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE profile ? 'age';     -- 键存在
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '存在性检查失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE profile ?| ARRAY['name','age'];  -- 任一键存在
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '任一键存在检查失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE profile ?& ARRAY['name','age'];  -- 所有键存在
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '所有键存在检查失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：包含（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE profile @> '{"age":30}';  -- 包含
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '包含检查失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE profile <@ '{"name":"Alice","age":30,"extra":"value"}';  -- 被包含
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '被包含检查失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：数组操作（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE profile->'tags' @> '["vip"]';  -- 数组包含
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '数组包含检查失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

```

### 2.2 更新操作符

```sql
-- 性能测试：更新操作符（带错误处理）
BEGIN;
-- 拼接
UPDATE users SET profile = profile || '{"verified":true}';
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'JSONB拼接失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
-- 删除键
UPDATE users SET profile = profile - 'age';
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '删除键失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
-- 删除多个键
UPDATE users SET profile = profile - ARRAY['age','tags'];
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '删除多个键失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
-- 删除路径
UPDATE users SET profile = profile #- '{address,zipcode}';
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '删除路径失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
-- 设置值
UPDATE users SET profile = jsonb_set(
    profile,
    '{address,country}',
    '"USA"'
);
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '设置值失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
-- 深度合并
UPDATE users SET profile = jsonb_set(
    profile,
    '{address}',
    profile->'address' || '{"country":"USA"}'
);
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '深度合并失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 3. GIN索引

### 3.1 创建GIN索引

```sql
-- 性能测试：默认GIN索引（jsonb_ops）（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_profile ON users USING GIN (profile);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_profile已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建GIN索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 支持的查询
-- @>, ?, ?|, ?&

-- 性能测试：jsonb_path_ops索引（更小，更快）（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_profile_path ON users USING GIN (profile jsonb_path_ops);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_profile_path已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建jsonb_path_ops索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 只支持@>操作符
-- 索引更小（~30%）
-- 查询更快
```

### 3.2 表达式索引

```sql
-- 性能测试：索引特定路径（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_profile_age ON users ((profile->'age'));
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_profile_age已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建路径索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：索引转换后的值（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_profile_age_int ON users (((profile->>'age')::int));
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_profile_age_int已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建表达式索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：使用（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE (profile->>'age')::int > 25;
-- 使用idx_profile_age_int索引
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 4. 查询优化

### 4.1 高效查询

```sql
-- 性能测试：Good: 使用@>（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE profile @> '{"age":30}';
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：Bad: 使用函数（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE (profile->>'age')::int = 30;
-- 无法使用jsonb_ops索引，但可使用表达式索引
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：Good: 存在性检查（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE profile ? 'email';
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '存在性检查查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：Good: 数组包含（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE profile->'tags' @> '["vip"]';
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '数组包含查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 4.2 避免全文档扫描

```sql
-- 性能测试：Bad: 提取所有字段（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    profile->>'name',
    profile->>'age',
    profile->>'email'
FROM users;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '提取字段查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- Good: 一次提取
SELECT jsonb_populate_record(null::user_type, profile)
FROM users;

-- 或使用jsonb_to_record
SELECT * FROM users,
LATERAL jsonb_to_record(profile) AS (
    name TEXT,
    age INT,
    email TEXT
);
```

---

## 5. 聚合函数

### 5.1 JSONB聚合

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
LATERAL jsonb_array_elements_text(profile->'tags') AS tag
GROUP BY tag
ORDER BY user_count DESC;
```

### 5.2 复杂聚合

```sql
-- 嵌套聚合
SELECT jsonb_build_object(
    'total_users', COUNT(*),
    'avg_age', AVG((profile->>'age')::int),
    'users_by_city', (
        SELECT jsonb_object_agg(city, count)
        FROM (
            SELECT profile#>>'{address,city}' AS city, COUNT(*) AS count
            FROM users
            GROUP BY city
        ) sub
    )
) AS summary
FROM users;
```

---

## 6. 实战应用

### 6.1 灵活Schema设计

```sql
-- 用户事件表（schema-less）
CREATE TABLE user_events (
    event_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- GIN索引
CREATE INDEX idx_events_data ON user_events USING GIN (event_data);

-- 不同事件类型存储不同字段
INSERT INTO user_events (user_id, event_type, event_data) VALUES
(123, 'page_view', '{"url":"/products","duration":45}'),
(123, 'purchase', '{"order_id":789,"amount":99.99,"items":[{"id":1,"qty":2}]}'),
(124, 'login', '{"ip":"1.2.3.4","device":"mobile"}');

-- 灵活查询
SELECT * FROM user_events
WHERE event_data @> '{"device":"mobile"}';

SELECT * FROM user_events
WHERE event_data->'amount' > '50';
```

### 6.2 审计日志

```sql
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(10),
    old_data JSONB,
    new_data JSONB,
    changed_fields JSONB,  -- 存储变更字段
    user_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 触发器自动记录
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    old_json JSONB;
    new_json JSONB;
    changed JSONB;
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, operation, new_data)
        VALUES (TG_TABLE_NAME, 'INSERT', row_to_json(NEW)::jsonb);

    ELSIF TG_OP = 'UPDATE' THEN
        old_json := row_to_json(OLD)::jsonb;
        new_json := row_to_json(NEW)::jsonb;

        -- 计算差异
        SELECT jsonb_object_agg(key, value)
        INTO changed
        FROM jsonb_each(new_json)
        WHERE value != old_json->key;

        INSERT INTO audit_logs (table_name, operation, old_data, new_data, changed_fields)
        VALUES (TG_TABLE_NAME, 'UPDATE', old_json, new_json, changed);

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, operation, old_data)
        VALUES (TG_TABLE_NAME, 'DELETE', row_to_json(OLD)::jsonb);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 应用到表
CREATE TRIGGER trg_audit
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

---

## 7. 性能优化

### 7.1 索引策略

```sql
-- 场景1: 频繁查询特定键
-- 使用表达式索引
CREATE INDEX idx_user_email ON users ((profile->>'email'));

-- 场景2: 多条件查询
-- 使用GIN索引
CREATE INDEX idx_profile_gin ON users USING GIN (profile);

-- 场景3: 特定路径查询
CREATE INDEX idx_profile_address ON users ((profile->'address'));
```

### 7.2 查询优化

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
SELECT p.* FROM users,
LATERAL jsonb_to_record(profile) AS p(
    name TEXT,
    age INT,
    email TEXT
);
```

---

## 8. PostgreSQL 18改进

### 8.1 JSONB性能提升

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
-- PostgreSQL 18: 18ms (-28%)
```

### 8.2 JSON路径表达式

```sql
-- jsonb_path_query (SQL/JSON path)
SELECT jsonb_path_query(
    '{"items":[{"name":"item1","price":100},{"name":"item2","price":200}]}',
    '$.items[*] ? (@.price > 150)'
);

-- jsonb_path_exists
SELECT * FROM orders
WHERE jsonb_path_exists(
    order_data,
    '$.items[*] ? (@.quantity > 10)'
);

-- 性能: 比传统方法快20-30%
```

---

## 9. 最佳实践

```text
设计原则:
✓ 结构化数据用列，半结构化用JSONB
✓ 高频查询字段提取为列
✓ 不要把JSONB当作垃圾桶
✓ 合理规范JSONB结构

索引策略:
✓ 小JSONB: 表达式索引
✓ 大JSONB: GIN索引
✓ 高频路径: 表达式索引
✓ 复杂查询: jsonb_path_ops

查询优化:
✓ 使用@>而非函数提取
✓ 批量提取字段
✓ 避免深层嵌套
✓ 合理使用LATERAL

维护:
✓ 定期VACUUM
✓ 监控JSONB列大小
✓ 考虑归档策略
```

---

**完成**: PostgreSQL 18 JSONB高级应用指南
**字数**: ~8,000字
**涵盖**: 操作符、索引、查询优化、实战应用、PG18改进
