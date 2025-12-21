# SQL优化速查手册

一页纸快速查找常见SQL优化技巧。

---

## ⚡ 索引优化

```sql
-- 性能测试：❌ 函数包裹索引列（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 使用表达式索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_lower_email ON users(LOWER(email));
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_lower_email已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建表达式索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：❌ 隐式类型转换（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE user_id = '12345';  -- user_id是INT
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 使用正确类型（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE user_id = 12345;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：❌ OR条件（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE name = 'Alice' OR name = 'Bob';
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 使用IN（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE name IN ('Alice', 'Bob');
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：❌ LIKE前导通配符（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE name LIKE '%test%';  -- 无法用索引
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 前缀匹配（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE name LIKE 'test%';  -- 可用索引
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 或使用全文搜索/trigram（带错误处理）
BEGIN;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_name_trgm ON users USING GIN (name gin_trgm_ops);
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE name % 'test';
COMMIT;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '扩展或索引已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建trigram索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 🔄 JOIN优化

```sql
-- 性能测试：❌ 子查询在SELECT中（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    u.id,
    (SELECT COUNT(*) FROM orders WHERE user_id = u.id) AS order_count
FROM users u;
-- 每行执行一次子查询！
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '子查询查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 改写为JOIN（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    u.id,
    COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'JOIN查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：❌ 不必要的DISTINCT（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT DISTINCT user_id FROM orders;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'DISTINCT查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 如果user_id已有索引，用GROUP BY更快（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT user_id FROM orders GROUP BY user_id;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'GROUP BY查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 📄 分页优化

```sql
-- 性能测试：❌ OFFSET深度分页（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM products
ORDER BY id
LIMIT 20 OFFSET 100000;
-- 扫描100020行，只返回20行
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'OFFSET分页查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ Keyset分页（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM products
WHERE id > 100000  -- 上一页最后的ID
ORDER BY id
LIMIT 20;
-- 直接定位，只扫描20行
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Keyset分页查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：❌ COUNT(*)深度分页（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM large_table WHERE condition;
-- 慢
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'COUNT查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 估算（如果可接受）（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT reltuples::BIGINT FROM pg_class WHERE relname = 'large_table';
-- 极快，稍有误差
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '估算查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 🎯 聚合优化

```sql
-- 性能测试：❌ 多次聚合查询（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM users WHERE status = 'active';
SELECT COUNT(*) FROM users WHERE status = 'inactive';
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '多次聚合查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 一次查询（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    status,
    COUNT(*) AS count
FROM users
GROUP BY status;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'GROUP BY查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：❌ 子查询聚合（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    category,
    (SELECT AVG(price) FROM products p2 WHERE p2.category = p1.category)
FROM products p1
GROUP BY category;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '子查询聚合失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 窗口函数（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT DISTINCT
    category,
    AVG(price) OVER (PARTITION BY category) AS avg_price
FROM products;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '窗口函数查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 🔍 EXISTS vs IN

```sql
-- 性能测试：大外表，小内表: IN更快（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM large_table
WHERE id IN (SELECT id FROM small_table);
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表large_table或small_table不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'IN查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：小外表，大内表: EXISTS更快（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM small_table st
WHERE EXISTS (
    SELECT 1 FROM large_table lt WHERE lt.id = st.id
);
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表small_table或large_table不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'EXISTS查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：通用建议: 让优化器选择（都写成JOIN）（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT st.* FROM small_table st
JOIN large_table lt ON st.id = lt.id;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表small_table或large_table不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'JOIN查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 💾 批量操作

```sql
-- 性能测试：❌ 循环单条INSERT（带错误处理）
BEGIN;
DO $$
BEGIN
    FOR i IN 1..10000 LOOP
        INSERT INTO users VALUES (i, 'user' || i, 'email' || i || '@example.com')
        ON CONFLICT DO NOTHING;
    END LOOP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '循环插入失败: %', SQLERRM;
        RAISE;
END $$;
-- 10000次INSERT，慢
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '循环插入事务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 批量VALUES（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
INSERT INTO users VALUES
(1, 'user1', 'email1@example.com'),
(2, 'user2', 'email2@example.com'),
(3, 'user3', 'email3@example.com')
ON CONFLICT DO NOTHING;
-- 1次INSERT，快
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '批量插入失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 或使用COPY（带错误处理）
BEGIN;
COPY users FROM '/tmp/data.csv' WITH CSV;
-- 最快
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'COPY失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：❌ 逐行UPDATE（带错误处理）
BEGIN;
UPDATE users SET status = 'active' WHERE id = 1;
UPDATE users SET status = 'active' WHERE id = 2;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '逐行UPDATE失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 批量UPDATE（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
UPDATE users SET status = 'active'
WHERE id IN (1, 2, 3);
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '批量UPDATE失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 或使用VALUES（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
UPDATE users u
SET status = v.new_status
FROM (VALUES
    (1, 'active'),
    (2, 'inactive')
) AS v(id, new_status)
WHERE u.id = v.id;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'VALUES UPDATE失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 🎨 SELECT优化

```sql
-- 性能测试：❌ SELECT *（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users;  -- 返回所有列
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'SELECT *查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 只选需要的列（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT id, username, email FROM users;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'SELECT特定列查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：❌ 不必要的DISTINCT（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT DISTINCT * FROM (
    SELECT id, name FROM users WHERE status = 'active'
) sub;
-- 如果id是主键，DISTINCT无意义
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'DISTINCT查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 去掉DISTINCT（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT id, name FROM users WHERE status = 'active';
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '去掉DISTINCT查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 🔢 数据类型优化

```sql
-- 性能测试：❌ 过大的类型（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS test_bigint (
    user_id BIGINT PRIMARY KEY
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表test_bigint已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建BIGINT表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：✅ 合适的类型（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS test_integer (
    user_id INTEGER PRIMARY KEY
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表test_integer已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建INTEGER表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
-- 21亿足够，节省50%空间

-- 性能测试：❌ CHAR(n)（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS test_char (
    name CHAR(100)
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表test_char已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建CHAR表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
-- 固定长度，浪费空间

-- 性能测试：✅ VARCHAR(n)（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS test_varchar (
    name VARCHAR(100)
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表test_varchar已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建VARCHAR表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
-- 变长
```

---

-- ❌ TEXT存储数字
amount TEXT  -- '99.99'

-- ✅ 正确类型
amount NUMERIC(10, 2)  -- 数值类型
```

---

## 🎯 快速检查清单

```sql
-- 运行这个查询检查常见问题
SELECT
    '连接数' AS check,
    COUNT(*)||'/'||(SELECT setting FROM pg_settings WHERE name='max_connections') AS value
FROM pg_stat_activity

UNION ALL

SELECT
    '缓存命中率',
    ROUND(SUM(blks_hit)*100/NULLIF(SUM(blks_hit+blks_read),0),2)||'%'
FROM pg_stat_database

UNION ALL

SELECT
    '表膨胀(>20%)',
    COUNT(*)::TEXT
FROM pg_stat_user_tables
WHERE n_dead_tup*100.0/NULLIF(n_live_tup+n_dead_tup,0) > 20

UNION ALL

SELECT
    '锁等待',
    COUNT(*)::TEXT
FROM pg_locks WHERE NOT granted

UNION ALL

SELECT
    '长事务(>5min)',
    COUNT(*)::TEXT
FROM pg_stat_activity
WHERE xact_start < now() - INTERVAL '5 minutes' AND state != 'idle'

UNION ALL

SELECT
    '慢查询(>1s)',
    COUNT(*)::TEXT
FROM pg_stat_statements WHERE mean_exec_time > 1000;

-- 所有指标都应该是0或接近目标值
```

---

**打印此页随时参考！** 📄
