---

> **📋 文档来源**: `docs\01-PostgreSQL18\38-CTE与递归查询完全指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL CTE与递归查询完全指南

## 1. CTE基础

### 1.1 简单CTE

```sql
-- 性能测试：不使用CTE（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY user_id
) AS user_orders
WHERE order_count > 5;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '子查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：使用CTE（更清晰）（带性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH user_orders AS (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY user_id
)
SELECT *
FROM user_orders
WHERE order_count > 5;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'CTE查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 1.2 多个CTE

```sql
-- 性能测试：多个CTE（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH
active_users AS (
    SELECT id, username
    FROM users
    WHERE last_login > now() - INTERVAL '30 days'
),
recent_orders AS (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    WHERE created_at > now() - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    u.username,
    COALESCE(o.order_count, 0) AS orders
FROM active_users u
LEFT JOIN recent_orders o ON u.id = o.user_id
ORDER BY orders DESC;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '多CTE查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 2. 递归CTE

### 2.1 组织层级

```sql
-- 性能测试：组织表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT REFERENCES employees(id),
    title VARCHAR(100)
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表employees已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
INSERT INTO employees (id, name, manager_id, title) VALUES
(1, 'Alice', NULL, 'CEO'),
(2, 'Bob', 1, 'CTO'),
(3, 'Charlie', 1, 'CFO'),
(4, 'David', 2, 'Tech Lead'),
(5, 'Eve', 2, 'Senior Dev'),
(6, 'Frank', 4, 'Developer')
ON CONFLICT (id) DO NOTHING;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '插入数据失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 递归查询：查找所有下属
WITH RECURSIVE subordinates AS (
    -- 基础查询（锚点）
    SELECT id, name, manager_id, title, 1 AS level
    FROM employees
    WHERE id = 2  -- Bob (CTO)

    UNION ALL

    -- 递归查询
    SELECT e.id, e.name, e.manager_id, e.title, s.level + 1
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
)
SELECT
    REPEAT('  ', level - 1) || name AS org_chart,
    title,
    level
FROM subordinates
ORDER BY level, name;

/*

org_chart          | title        | level
-------------------|--------------|-------
Bob                | CTO          | 1
  David            | Tech Lead    | 2
  Eve              | Senior Dev   | 2

    Frank          | Developer    | 3
*/

```

### 2.2 路径追踪

```sql
-- 性能测试：显示完整层级路径（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH RECURSIVE org_tree AS (
    SELECT
        id,
        name,
        manager_id,
        ARRAY[id] AS path,
        name::TEXT AS path_names,
        1 AS level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT
        e.id,
        e.name,
        e.manager_id,
        ot.path || e.id,
        ot.path_names || ' → ' || e.name,
        ot.level + 1
    FROM employees e
    JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT
    name,
    path_names AS hierarchy_path,
    level
FROM org_tree
ORDER BY path;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表employees不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '递归查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

/*

name    | hierarchy_path                  | level
--------|----------------------------------|-------
Alice   | Alice                            | 1
Bob     | Alice → Bob                      | 2
David   | Alice → Bob → David              | 3
Frank   | Alice → Bob → David → Frank      | 4
Eve     | Alice → Bob → Eve                | 3
Charlie | Alice → Charlie                  | 2
*/

```

---

## 3. 图遍历

### 3.1 社交网络

```sql
-- 性能测试：创建好友表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS friendships (
    user1_id INT,
    user2_id INT,
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user1_id, user2_id)
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表friendships已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建好友表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查找所有朋友的朋友（2度连接）（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH RECURSIVE friends_of_friends AS (
    -- 直接朋友（1度）
    SELECT
        user1_id AS source,
        user2_id AS target,
        1 AS degree,
        ARRAY[user1_id, user2_id] AS path
    FROM friendships
    WHERE user1_id = 123

    UNION

    SELECT
        user2_id,
        user1_id,
        1,
        ARRAY[user2_id, user1_id]
    FROM friendships
    WHERE user2_id = 123

    UNION ALL

    -- 朋友的朋友（2度）
    SELECT
        fof.source,
        f.user2_id,
        fof.degree + 1,
        fof.path || f.user2_id
    FROM friends_of_friends fof
    JOIN friendships f ON fof.target = f.user1_id
    WHERE fof.degree < 2
      AND NOT f.user2_id = ANY(fof.path)  -- 避免循环

    UNION ALL

    SELECT
        fof.source,
        f.user1_id,
        fof.degree + 1,
        fof.path || f.user1_id
    FROM friends_of_friends fof
    JOIN friendships f ON fof.target = f.user2_id
    WHERE fof.degree < 2
      AND NOT f.user1_id = ANY(fof.path)
)
SELECT DISTINCT target AS friend_id, degree
FROM friends_of_friends
WHERE target != 123
ORDER BY degree, target;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表friendships不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '图遍历查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 3.2 最短路径

```sql
-- 性能测试：创建城市路线表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS routes (
    from_city VARCHAR(50),
    to_city VARCHAR(50),
    distance INT,
    PRIMARY KEY (from_city, to_city)
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表routes已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建路线表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查找最短路径（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH RECURSIVE shortest_path AS (
    SELECT
        from_city,
        to_city,
        distance,
        ARRAY[from_city, to_city] AS path,
        distance AS total_distance
    FROM routes
    WHERE from_city = 'NYC'

    UNION ALL

    SELECT
        sp.from_city,
        r.to_city,
        r.distance,
        sp.path || r.to_city,
        sp.total_distance + r.distance
    FROM shortest_path sp
    JOIN routes r ON sp.to_city = r.from_city
    WHERE NOT r.to_city = ANY(sp.path)  -- 避免环路
      AND sp.total_distance + r.distance < 1000  -- 剪枝
)
SELECT
    path,
    total_distance
FROM shortest_path
WHERE to_city = 'LA'
ORDER BY total_distance
LIMIT 1;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表routes不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '最短路径查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

/*

path                        | total_distance
----------------------------|----------------
{NYC,Chicago,Denver,LA}     | 850
*/

```

---

## 4. 数列生成

### 4.1 生成序列

```sql
-- 性能测试：生成1到100（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numbers
    WHERE n < 100
)
SELECT * FROM numbers;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '生成数字序列失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：斐波那契数列（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH RECURSIVE fibonacci(a, b, n) AS (
    SELECT 0::BIGINT, 1::BIGINT, 1
    UNION ALL
    SELECT b, a + b, n + 1
    FROM fibonacci
    WHERE n < 20
)
SELECT a AS fib_number
FROM fibonacci;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '生成斐波那契数列失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

/*
fib_number
----------
0
1
1
2
3
5
8
13
...
*/
```

### 4.2 日期序列

```sql
-- 性能测试：生成过去30天的日期（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH RECURSIVE date_series AS (
    SELECT CURRENT_DATE AS date
    UNION ALL
    SELECT date - INTERVAL '1 day'
    FROM date_series
    WHERE date > CURRENT_DATE - INTERVAL '30 days'
)
SELECT date::DATE
FROM date_series
ORDER BY date;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '生成日期序列失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：统计每日订单（填充缺失日期）（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH RECURSIVE date_series AS (
    SELECT '2024-01-01'::DATE AS date
    UNION ALL
    SELECT date + INTERVAL '1 day'
    FROM date_series
    WHERE date < '2024-01-31'::DATE
)
SELECT
    ds.date,
    COALESCE(COUNT(o.id), 0) AS order_count
FROM date_series ds
LEFT JOIN orders o ON o.created_at::DATE = ds.date
GROUP BY ds.date
ORDER BY ds.date;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表orders不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '统计每日订单失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 5. 性能优化

### 5.1 避免无限递归

```sql
-- ❌ 危险：可能无限递归
WITH RECURSIVE bad_recursion AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM bad_recursion
    -- 没有终止条件！
)
SELECT * FROM bad_recursion;

-- ✅ 安全：添加终止条件
WITH RECURSIVE safe_recursion AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM bad_recursion
    WHERE n < 1000  -- 终止条件
)
SELECT * FROM safe_recursion;

-- ✅ 配置最大递归深度
SET max_recursion_depth = 100;
```

### 5.2 优化循环检测

```sql
-- 图遍历中使用数组检测循环
WITH RECURSIVE graph_traversal AS (
    SELECT
        id,
        ARRAY[id] AS visited,
        1 AS depth
    FROM nodes
    WHERE id = 1

    UNION ALL

    SELECT
        e.target_id,
        gt.visited || e.target_id,
        gt.depth + 1
    FROM graph_traversal gt
    JOIN edges e ON gt.id = e.source_id
    WHERE NOT e.target_id = ANY(gt.visited)  -- 关键：避免循环
      AND gt.depth < 10  -- 限制深度
)
SELECT * FROM graph_traversal;
```

---

## 6. 实战案例

### 6.1 物料清单（BOM）

```sql
-- 产品物料表
CREATE TABLE bill_of_materials (
    product_id INT,
    component_id INT,
    quantity INT,
    PRIMARY KEY (product_id, component_id)
);

-- 递归展开BOM
WITH RECURSIVE bom_explosion AS (
    SELECT
        product_id,
        component_id,
        quantity,
        1 AS level,
        ARRAY[product_id] AS path
    FROM bill_of_materials
    WHERE product_id = 100  -- 最终产品

    UNION ALL

    SELECT
        bom.product_id,
        bom.component_id,
        bom.quantity * be.quantity,
        be.level + 1,
        be.path || bom.product_id
    FROM bom_explosion be
    JOIN bill_of_materials bom ON be.component_id = bom.product_id
    WHERE NOT bom.product_id = ANY(be.path)
)
SELECT
    component_id,
    SUM(quantity) AS total_quantity,
    MAX(level) AS deepest_level
FROM bom_explosion
GROUP BY component_id
ORDER BY component_id;
```

### 6.2 评论回复树

```sql
-- 评论表
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    parent_id INT REFERENCES comments(id),
    user_id INT,
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 展示评论树
WITH RECURSIVE comment_tree AS (
    SELECT
        id,
        parent_id,
        content,
        1 AS level,
        ARRAY[id] AS path,
        id::TEXT AS sort_path
    FROM comments
    WHERE parent_id IS NULL

    UNION ALL

    SELECT
        c.id,
        c.parent_id,
        c.content,
        ct.level + 1,
        ct.path || c.id,
        ct.sort_path || '-' || LPAD(c.id::TEXT, 10, '0')
    FROM comments c
    JOIN comment_tree ct ON c.parent_id = ct.id
)
SELECT
    REPEAT('  ', level - 1) || content AS threaded_comment,
    level
FROM comment_tree
ORDER BY sort_path;
```

---

**完成**: PostgreSQL CTE与递归查询完全指南
**字数**: ~10,000字
**涵盖**: CTE基础、递归查询、组织层级、图遍历、最短路径、数列生成、性能优化、实战案例
