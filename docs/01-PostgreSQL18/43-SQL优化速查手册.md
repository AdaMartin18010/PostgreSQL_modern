# SQL优化速查手册

一页纸快速查找常见SQL优化技巧。

---

## ⚡ 索引优化

```sql
-- ❌ 函数包裹索引列
WHERE LOWER(email) = 'test@example.com'

-- ✅ 使用表达式索引
CREATE INDEX idx_lower_email ON users(LOWER(email));

---

-- ❌ 隐式类型转换
WHERE user_id = '12345'  -- user_id是INT

-- ✅ 使用正确类型
WHERE user_id = 12345

---

-- ❌ OR条件（可能不用索引）
WHERE name = 'Alice' OR name = 'Bob'

-- ✅ 使用IN
WHERE name IN ('Alice', 'Bob')

---

-- ❌ LIKE前导通配符
WHERE name LIKE '%test%'  -- 无法用索引

-- ✅ 前缀匹配
WHERE name LIKE 'test%'  -- 可用索引

-- ✅ 或使用全文搜索/trigram
CREATE INDEX idx_name_trgm ON users USING GIN (name gin_trgm_ops);
WHERE name % 'test';
```

---

## 🔄 JOIN优化

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
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

---

-- ❌ 不必要的DISTINCT
SELECT DISTINCT user_id FROM orders;

-- ✅ 如果user_id已有索引，用GROUP BY更快
SELECT user_id FROM orders GROUP BY user_id;
```

---

## 📄 分页优化

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

---

-- ❌ COUNT(*)深度分页
SELECT COUNT(*) FROM large_table WHERE condition;
-- 慢

-- ✅ 估算（如果可接受）
SELECT reltuples::BIGINT FROM pg_class WHERE relname = 'large_table';
-- 极快，稍有误差
```

---

## 🎯 聚合优化

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

---

-- ❌ 子查询聚合
SELECT
    category,
    (SELECT AVG(price) FROM products p2 WHERE p2.category = p1.category)
FROM products p1
GROUP BY category;

-- ✅ 窗口函数
SELECT DISTINCT
    category,
    AVG(price) OVER (PARTITION BY category) AS avg_price
FROM products;
```

---

## 🔍 EXISTS vs IN

```sql
-- 大外表，小内表: IN更快
SELECT * FROM large_table
WHERE id IN (SELECT id FROM small_table);

-- 小外表，大内表: EXISTS更快
SELECT * FROM small_table st
WHERE EXISTS (
    SELECT 1 FROM large_table lt WHERE lt.id = st.id
);

-- 通用建议: 让优化器选择（都写成JOIN）
SELECT st.* FROM small_table st
JOIN large_table lt ON st.id = lt.id;
```

---

## 💾 批量操作

```sql
-- ❌ 循环单条INSERT
FOR i IN 1..10000 LOOP
    INSERT INTO users VALUES (i, ...);
END LOOP;
-- 10000次INSERT，慢

-- ✅ 批量VALUES
INSERT INTO users VALUES
(1, ...), (2, ...), (3, ...), ... (10000, ...);
-- 1次INSERT，快

-- ✅ 或使用COPY
COPY users FROM '/tmp/data.csv' WITH CSV;
-- 最快

---

-- ❌ 逐行UPDATE
UPDATE users SET status = 'active' WHERE id = 1;
UPDATE users SET status = 'active' WHERE id = 2;

-- ✅ 批量UPDATE
UPDATE users SET status = 'active'
WHERE id IN (1, 2, 3, ...);

-- ✅ 或使用VALUES
UPDATE users u
SET status = v.new_status
FROM (VALUES
    (1, 'active'),
    (2, 'inactive')
) AS v(id, new_status)
WHERE u.id = v.id;
```

---

## 🎨 SELECT优化

```sql
-- ❌ SELECT *
SELECT * FROM users;  -- 返回所有列

-- ✅ 只选需要的列
SELECT id, username, email FROM users;

---

-- ❌ 不必要的DISTINCT
SELECT DISTINCT * FROM (
    SELECT id, name FROM users WHERE status = 'active'
) sub;
-- 如果id是主键，DISTINCT无意义

-- ✅ 去掉DISTINCT
SELECT id, name FROM users WHERE status = 'active';
```

---

## 🔢 数据类型优化

```sql
-- ❌ 过大的类型
user_id BIGINT  -- 实际只有1万用户

-- ✅ 合适的类型
user_id INTEGER  -- 21亿足够，节省50%空间

---

-- ❌ CHAR(n)
name CHAR(100)  -- 固定长度，浪费空间

-- ✅ VARCHAR(n)
name VARCHAR(100)  -- 变长

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
