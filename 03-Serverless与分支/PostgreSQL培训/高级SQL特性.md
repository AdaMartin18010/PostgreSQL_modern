# PostgreSQL 高级 SQL 特性

> **更新时间**: 2025 年 11 月 1 日
> **技术版本**: PostgreSQL 14+
> **文档编号**: 03-03-06

## 📑 目录

- [PostgreSQL 高级 SQL 特性](#postgresql-高级-sql-特性)
  - [📑 目录](#-目录)
  - [1. 窗口函数](#1-窗口函数)
    - [1.1 排名函数](#11-排名函数)
    - [1.2 分区窗口函数](#12-分区窗口函数)
    - [1.3 聚合窗口函数](#13-聚合窗口函数)
    - [1.4 LAG 和 LEAD](#14-lag-和-lead)
  - [2. CTE（公用表表达式）](#2-cte公用表表达式)
    - [2.1 简单 CTE](#21-简单-cte)
    - [2.2 递归 CTE](#22-递归-cte)
  - [3. 高级查询技巧](#3-高级查询技巧)
    - [3.1 CASE 表达式](#31-case-表达式)
    - [3.2 FILTER 子句](#32-filter-子句)
    - [3.3 LATERAL JOIN](#33-lateral-join)
  - [4. 实践练习](#4-实践练习)
    - [练习 1: 使用窗口函数](#练习-1-使用窗口函数)
  - [5. 参考资料](#5-参考资料)

---

## 1. 窗口函数

### 1.1 排名函数

```sql
-- ROW_NUMBER() - 行号
SELECT
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- RANK() - 排名（相同值相同排名，跳过后续排名）
SELECT
    name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- DENSE_RANK() - 密集排名（相同值相同排名，不跳过）
SELECT
    name,
    salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;
```

### 1.2 分区窗口函数

```sql
-- 按部门分区
SELECT
    department,
    name,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employees;
```

### 1.3 聚合窗口函数

```sql
SELECT
    name,
    salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary,
    SUM(salary) OVER (PARTITION BY department) AS dept_total_salary
FROM employees;
```

### 1.4 LAG 和 LEAD

```sql
-- 访问前后行
SELECT
    order_date,
    total_amount,
    LAG(total_amount) OVER (ORDER BY order_date) AS prev_amount,
    LEAD(total_amount) OVER (ORDER BY order_date) AS next_amount
FROM orders;
```

## 2. CTE（公用表表达式）

### 2.1 简单 CTE

```sql
WITH high_salary_employees AS (
    SELECT * FROM employees WHERE salary > 100000
)
SELECT * FROM high_salary_employees;
```

### 2.2 递归 CTE

```sql
-- 查询员工层级关系
WITH RECURSIVE employee_hierarchy AS (
    -- 基础查询（顶级管理者）
    SELECT id, name, manager_id, 1 AS level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- 递归查询（下属）
    SELECT e.id, e.name, e.manager_id, eh.level + 1
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy;
```

## 3. 高级查询技巧

### 3.1 CASE 表达式

```sql
SELECT
    name,
    salary,
    CASE
        WHEN salary > 100000 THEN 'High'
        WHEN salary > 50000 THEN 'Medium'
        ELSE 'Low'
    END AS salary_category
FROM employees;
```

### 3.2 FILTER 子句

```sql
SELECT
    department,
    COUNT(*) AS total_employees,
    COUNT(*) FILTER (WHERE salary > 100000) AS high_salary_count,
    SUM(salary) FILTER (WHERE salary > 100000) AS high_salary_total
FROM employees
GROUP BY department;
```

### 3.3 LATERAL JOIN

```sql
-- 横向连接
SELECT
    u.name,
    recent_orders.order_date,
    recent_orders.total_amount
FROM users u
CROSS JOIN LATERAL (
    SELECT order_date, total_amount
    FROM orders
    WHERE orders.user_id = u.id
    ORDER BY order_date DESC
    LIMIT 3
) AS recent_orders;
```

## 4. 实践练习

### 练习 1: 使用窗口函数

```sql
-- 任务: 查询每个部门工资最高的前 3 名员工
WITH ranked_employees AS (
    SELECT
        department,
        name,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
    FROM employees
)
SELECT department, name, salary
FROM ranked_employees
WHERE rank <= 3;
```

## 5. 参考资料

- [PostgreSQL 官方文档 - 窗口函数](https://www.postgresql.org/docs/current/tutorial-window.html)
- [PostgreSQL 官方文档 - WITH 查询](https://www.postgresql.org/docs/current/queries-with.html)

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
**文档编号**: 03-03-06
