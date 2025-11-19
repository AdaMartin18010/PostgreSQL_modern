# PostgreSQL SQL 基础培训

> **更新时间**: 2025 年 11 月 1 日
> **技术版本**: PostgreSQL 14+
> **文档编号**: 03-03-01

## 📑 目录

- [PostgreSQL SQL 基础培训](#postgresql-sql-基础培训)
  - [📑 目录](#-目录)
  - [1. SQL 数据类型](#1-sql-数据类型)
    - [1.1 数值类型](#11-数值类型)
    - [1.2 字符类型](#12-字符类型)
    - [1.3 日期时间类型](#13-日期时间类型)
    - [1.4 布尔类型](#14-布尔类型)
    - [1.5 JSON 类型](#15-json-类型)
    - [1.6 数组类型](#16-数组类型)
    - [1.7 UUID 类型](#17-uuid-类型)
  - [2. DML 操作（数据操作语言）](#2-dml-操作数据操作语言)
    - [2.1 INSERT 插入数据](#21-insert-插入数据)
    - [2.2 UPDATE 更新数据](#22-update-更新数据)
    - [2.3 DELETE 删除数据](#23-delete-删除数据)
    - [2.4 UPSERT（插入或更新）](#24-upsert插入或更新)
  - [3. DQL 操作（数据查询语言）](#3-dql-操作数据查询语言)
    - [3.1 SELECT 基础查询](#31-select-基础查询)
    - [3.2 WHERE 条件过滤](#32-where-条件过滤)
    - [3.3 ORDER BY 排序](#33-order-by-排序)
    - [3.4 LIMIT 和 OFFSET](#34-limit-和-offset)
    - [3.5 DISTINCT 去重](#35-distinct-去重)
    - [3.6 GROUP BY 分组](#36-group-by-分组)
    - [3.7 JOIN 连接](#37-join-连接)
    - [3.8 子查询](#38-子查询)
    - [3.9 UNION 合并查询结果](#39-union-合并查询结果)
  - [4. 实践练习](#4-实践练习)
    - [练习 1: 创建表并插入数据](#练习-1-创建表并插入数据)
    - [练习 2: 复杂查询](#练习-2-复杂查询)
    - [练习 3: 聚合查询](#练习-3-聚合查询)
  - [5. 参考资料](#5-参考资料)

---

## 1. SQL 数据类型

### 1.1 数值类型

```sql
-- 数值类型示例
CREATE TABLE numeric_types (
    id SERIAL PRIMARY KEY,                    -- 自增整数
    small_int SMALLINT,                       -- -32768 到 32767
    integer_col INTEGER,                      -- -2147483648 到 2147483647
    big_int BIGINT,                           -- 大整数
    decimal_col DECIMAL(10, 2),               -- 精确数值
    numeric_col NUMERIC(10, 2),               -- 精确数值（同 DECIMAL）
    real_col REAL,                            -- 单精度浮点数
    double_col DOUBLE PRECISION,              -- 双精度浮点数
    money_col MONEY                           -- 货币类型
);
```

**类型选择建议**:

| 场景 | 推荐类型 | 说明 |
|------|---------|------|
| 主键 | SERIAL/BIGSERIAL | 自增整数 |
| 金额 | DECIMAL(10,2) | 精确数值，避免浮点误差 |
| 计数器 | INTEGER | 足够大，性能好 |
| 大数值 | BIGINT | 超过 INTEGER 范围 |
| 科学计算 | REAL/DOUBLE PRECISION | 可接受精度损失 |

### 1.2 字符类型

```sql
-- 字符类型示例
CREATE TABLE character_types (
    id SERIAL PRIMARY KEY,
    varchar_col VARCHAR(255),                 -- 可变长度字符串
    char_col CHAR(10),                        -- 固定长度字符串
    text_col TEXT,                            -- 无限长度文本
    name_col NAME                             -- 标识符名称
);
```

**类型选择建议**:

- **VARCHAR(n)**: 已知最大长度的字符串
- **TEXT**: 未知长度或很长的文本（推荐）
- **CHAR(n)**: 固定长度字符串（很少使用）

### 1.3 日期时间类型

```sql
-- 日期时间类型示例
CREATE TABLE datetime_types (
    id SERIAL PRIMARY KEY,
    date_col DATE,                            -- 日期
    time_col TIME,                            -- 时间
    timestamp_col TIMESTAMP,                  -- 时间戳
    timestamptz_col TIMESTAMPTZ,              -- 带时区的时间戳（推荐）
    interval_col INTERVAL                     -- 时间间隔
);
```

**最佳实践**:

- 使用 `TIMESTAMPTZ` 而不是 `TIMESTAMP`（自动处理时区）
- 使用 `NOW()` 或 `CURRENT_TIMESTAMP` 获取当前时间

### 1.4 布尔类型

```sql
-- 布尔类型示例
CREATE TABLE boolean_types (
    id SERIAL PRIMARY KEY,
    is_active BOOLEAN,                        -- TRUE/FALSE/NULL
    status BOOLEAN DEFAULT TRUE
);

-- 插入数据
INSERT INTO boolean_types (is_active) VALUES (TRUE);
INSERT INTO boolean_types (is_active) VALUES (FALSE);
INSERT INTO boolean_types (is_active) VALUES (NULL);
```

### 1.5 JSON 类型

```sql
-- JSON 类型示例
CREATE TABLE json_types (
    id SERIAL PRIMARY KEY,
    json_col JSON,                            -- JSON 数据
    jsonb_col JSONB                           -- 二进制 JSON（推荐）
);

-- 插入 JSON 数据
INSERT INTO json_types (jsonb_col) VALUES (
    '{"name": "John", "age": 30, "tags": ["developer", "admin"]}'::jsonb
);

-- 查询 JSON
SELECT jsonb_col->>'name' AS name FROM json_types;
SELECT jsonb_col->'tags'->0 AS first_tag FROM json_types;
```

**JSON vs JSONB**:

| 特性 | JSON | JSONB |
|------|------|-------|
| 存储格式 | 文本 | 二进制 |
| 查询性能 | 慢 | 快 |
| 索引支持 | 否 | 是 |
| 推荐使用 | 否 | 是 |

### 1.6 数组类型

```sql
-- 数组类型示例
CREATE TABLE array_types (
    id SERIAL PRIMARY KEY,
    tags TEXT[],                              -- 文本数组
    numbers INTEGER[],                        -- 整数数组
    matrix INTEGER[][]                        -- 多维数组
);

-- 插入数组
INSERT INTO array_types (tags, numbers) VALUES (
    ARRAY['tag1', 'tag2', 'tag3'],
    ARRAY[1, 2, 3, 4, 5]
);

-- 查询数组
SELECT * FROM array_types WHERE 'tag1' = ANY(tags);
SELECT * FROM array_types WHERE tags @> ARRAY['tag1'];
```

### 1.7 UUID 类型

```sql
-- UUID 类型示例
CREATE TABLE uuid_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT
);

-- 生成 UUID
SELECT gen_random_uuid();
```

## 2. DML 操作（数据操作语言）

### 2.1 INSERT 插入数据

```sql
-- 单行插入
INSERT INTO users (name, email, age)
VALUES ('John Doe', 'john@example.com', 30);

-- 批量插入
INSERT INTO users (name, email, age)
VALUES
    ('Alice', 'alice@example.com', 25),
    ('Bob', 'bob@example.com', 35),
    ('Charlie', 'charlie@example.com', 28);

-- 从查询插入
INSERT INTO users_backup (name, email, age)
SELECT name, email, age FROM users WHERE age > 25;

-- 使用 RETURNING 返回插入的数据
INSERT INTO users (name, email)
VALUES ('David', 'david@example.com')
RETURNING id, name;
```

### 2.2 UPDATE 更新数据

```sql
-- 基本更新
UPDATE users
SET age = 31, email = 'john.new@example.com'
WHERE id = 1;

-- 使用子查询更新
UPDATE orders
SET total_amount = (
    SELECT SUM(amount)
    FROM order_items
    WHERE order_items.order_id = orders.id
)
WHERE id = 1;

-- 使用 JOIN 更新
UPDATE orders o
SET total_amount = oi.total
FROM (
    SELECT order_id, SUM(amount) AS total
    FROM order_items
    GROUP BY order_id
) oi
WHERE o.id = oi.order_id;

-- 使用 RETURNING 返回更新的数据
UPDATE users
SET age = age + 1
WHERE id = 1
RETURNING id, name, age;
```

### 2.3 DELETE 删除数据

```sql
-- 删除特定行
DELETE FROM users WHERE id = 1;

-- 使用子查询删除
DELETE FROM users
WHERE id IN (
    SELECT user_id FROM orders WHERE total_amount > 1000
);

-- 删除所有数据（保留表结构）
TRUNCATE TABLE users;

-- TRUNCATE 更快，但无法回滚
TRUNCATE TABLE users CASCADE;  -- 级联删除相关表数据

-- 使用 RETURNING 返回删除的数据
DELETE FROM users
WHERE age < 18
RETURNING id, name;
```

### 2.4 UPSERT（插入或更新）

```sql
-- INSERT ... ON CONFLICT（PostgreSQL 9.5+）
INSERT INTO users (email, name, age)
VALUES ('john@example.com', 'John Doe', 30)
ON CONFLICT (email)
DO UPDATE SET
    name = EXCLUDED.name,
    age = EXCLUDED.age;

-- 或者什么都不做
INSERT INTO users (email, name)
VALUES ('john@example.com', 'John Doe')
ON CONFLICT (email) DO NOTHING;
```

## 3. DQL 操作（数据查询语言）

### 3.1 SELECT 基础查询

```sql
-- 查询所有列
SELECT * FROM users;

-- 选择特定列
SELECT name, email FROM users;

-- 使用别名
SELECT
    name AS user_name,
    email AS user_email,
    age AS user_age
FROM users;

-- 使用表达式
SELECT
    name,
    age,
    age * 365 AS days_old
FROM users;
```

### 3.2 WHERE 条件过滤

```sql
-- 基本条件
SELECT * FROM users WHERE age > 25;

-- 多个条件
SELECT * FROM users
WHERE age > 25 AND email LIKE '%@example.com';

-- 使用 IN
SELECT * FROM users
WHERE id IN (1, 2, 3, 4, 5);

-- 使用 BETWEEN
SELECT * FROM users
WHERE age BETWEEN 25 AND 35;

-- 使用 LIKE（模式匹配）
SELECT * FROM users
WHERE name LIKE 'John%';  -- 以 John 开头
SELECT * FROM users
WHERE name LIKE '%Doe';   -- 以 Doe 结尾
SELECT * FROM users
WHERE name LIKE '%John%'; -- 包含 John

-- 使用 ILIKE（不区分大小写）
SELECT * FROM users
WHERE name ILIKE 'john%';

-- 使用 IS NULL
SELECT * FROM users
WHERE email IS NULL;

-- 使用 IS NOT NULL
SELECT * FROM users
WHERE email IS NOT NULL;
```

### 3.3 ORDER BY 排序

```sql
-- 升序排序（默认）
SELECT * FROM users ORDER BY age ASC;

-- 降序排序
SELECT * FROM users ORDER BY age DESC;

-- 多列排序
SELECT * FROM users
ORDER BY age DESC, name ASC;

-- 使用表达式排序
SELECT * FROM users
ORDER BY LENGTH(name) DESC;
```

### 3.4 LIMIT 和 OFFSET

```sql
-- 限制结果数量
SELECT * FROM users LIMIT 10;

-- 跳过前 N 条，取 M 条
SELECT * FROM users
ORDER BY id
LIMIT 10 OFFSET 20;  -- 跳过前20条，取10条

-- 分页查询
SELECT * FROM users
ORDER BY id
LIMIT 10 OFFSET 0;   -- 第1页
SELECT * FROM users
ORDER BY id
LIMIT 10 OFFSET 10;  -- 第2页
```

### 3.5 DISTINCT 去重

```sql
-- 去重
SELECT DISTINCT age FROM users;

-- 多列去重
SELECT DISTINCT age, email FROM users;

-- 使用 DISTINCT ON（PostgreSQL 特有）
SELECT DISTINCT ON (age) age, name, email
FROM users
ORDER BY age, created_at DESC;
```

### 3.6 GROUP BY 分组

```sql
-- 基本分组
SELECT
    age,
    COUNT(*) AS user_count
FROM users
GROUP BY age;

-- 多列分组
SELECT
    department,
    age,
    COUNT(*) AS count
FROM users
GROUP BY department, age;

-- 使用聚合函数
SELECT
    age,
    COUNT(*) AS user_count,
    AVG(age) AS avg_age,
    MIN(age) AS min_age,
    MAX(age) AS max_age,
    SUM(age) AS total_age
FROM users
GROUP BY age;

-- HAVING 过滤分组结果
SELECT
    age,
    COUNT(*) AS user_count
FROM users
GROUP BY age
HAVING COUNT(*) > 5;
```

### 3.7 JOIN 连接

```sql
-- INNER JOIN（内连接）
SELECT u.name, o.order_date, o.total_amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN（左连接）
SELECT u.name, o.order_date
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- RIGHT JOIN（右连接）
SELECT u.name, o.order_date
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- FULL OUTER JOIN（全外连接）
SELECT u.name, o.order_date
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;

-- CROSS JOIN（笛卡尔积）
SELECT u.name, p.product_name
FROM users u
CROSS JOIN products p;

-- 多表连接
SELECT
    u.name,
    o.order_date,
    p.product_name,
    oi.quantity
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;
```

### 3.8 子查询

```sql
-- 标量子查询（返回单个值）
SELECT
    name,
    (SELECT COUNT(*) FROM orders WHERE orders.user_id = users.id) AS order_count
FROM users;

-- EXISTS 子查询
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id AND o.total_amount > 1000
);

-- IN 子查询
SELECT * FROM users
WHERE id IN (
    SELECT user_id FROM orders WHERE total_amount > 1000
);

-- NOT IN 子查询（注意 NULL 值）
SELECT * FROM users
WHERE id NOT IN (
    SELECT user_id FROM orders WHERE user_id IS NOT NULL
);

-- 相关子查询
SELECT
    u.name,
    (SELECT AVG(total_amount)
     FROM orders
     WHERE orders.user_id = u.id) AS avg_order_amount
FROM users u;
```

### 3.9 UNION 合并查询结果

```sql
-- UNION（去重）
SELECT name FROM users
UNION
SELECT name FROM customers;

-- UNION ALL（保留重复）
SELECT name FROM users
UNION ALL
SELECT name FROM customers;

-- UNION 多个查询
SELECT name FROM users
UNION
SELECT name FROM customers
UNION
SELECT name FROM suppliers;
```

## 4. 实践练习

### 练习 1: 创建表并插入数据

```sql
-- 任务: 创建一个员工表，包含以下字段：
-- id (主键), name, email, department, salary, hire_date
-- 插入至少 5 条记录

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    department TEXT,
    salary DECIMAL(10, 2),
    hire_date DATE
);

INSERT INTO employees (name, email, department, salary, hire_date) VALUES
    ('Alice', 'alice@example.com', 'Engineering', 100000, '2023-01-15'),
    ('Bob', 'bob@example.com', 'Sales', 80000, '2023-02-20'),
    ('Charlie', 'charlie@example.com', 'Engineering', 95000, '2023-03-10'),
    ('Diana', 'diana@example.com', 'Marketing', 75000, '2023-04-05'),
    ('Eve', 'eve@example.com', 'Engineering', 105000, '2023-05-12');
```

### 练习 2: 复杂查询

```sql
-- 任务: 查询 Engineering 部门工资最高的前 3 名员工

SELECT name, salary
FROM employees
WHERE department = 'Engineering'
ORDER BY salary DESC
LIMIT 3;
```

### 练习 3: 聚合查询

```sql
-- 任务: 统计每个部门的平均工资和员工数量

SELECT
    department,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary,
    MIN(salary) AS min_salary,
    MAX(salary) AS max_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;
```

## 5. 参考资料

- [PostgreSQL 官方文档 - 数据类型](https://www.postgresql.org/docs/current/datatype.html)
- [PostgreSQL 官方文档 - SQL 命令](https://www.postgresql.org/docs/current/sql-commands.html)
- [PostgreSQL 教程](https://www.postgresql.org/docs/current/tutorial.html)

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
**文档编号**: 03-03-01
