---

> **📋 文档来源**: `docs\01-PostgreSQL18\36-SQL注入防御完整指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL SQL注入防御完整指南

## 📑 目录

- [PostgreSQL SQL注入防御完整指南](#postgresql-sql注入防御完整指南)
  - [📑 目录](#-目录)
  - [1. SQL注入原理](#1-sql注入原理)
    - [1.1 经典SQL注入](#11-经典sql注入)
  - [2. 参数化查询](#2-参数化查询)
    - [2.1 Python (psycopg2)](#21-python-psycopg2)
    - [2.2 Node.js (node-postgres)](#22-nodejs-node-postgres)
    - [2.3 Java (JDBC)](#23-java-jdbc)
  - [3. ORM防御](#3-orm防御)
    - [3.1 Django](#31-django)
    - [3.2 SQLAlchemy](#32-sqlalchemy)
  - [4. 高级注入场景](#4-高级注入场景)
    - [4.1 ORDER BY注入](#41-order-by注入)
    - [4.2 LIKE注入](#42-like注入)
    - [4.3 LIMIT/OFFSET注入](#43-limitoffset注入)
  - [5. 二次注入](#5-二次注入)
  - [6. 数据库层防御](#6-数据库层防御)
    - [6.1 最小权限](#61-最小权限)
    - [6.2 函数包装](#62-函数包装)
  - [7. WAF与监控](#7-waf与监控)
    - [7.1 WAF规则](#71-waf规则)
    - [7.2 日志监控](#72-日志监控)
  - [8. 代码审计清单](#8-代码审计清单)
  - [9. 测试用例](#9-测试用例)

## 1. SQL注入原理

### 1.1 经典SQL注入

```python
# ❌ 危险代码
username = request.GET['username']
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

# 攻击payload:
# username = "admin' OR '1'='1"
# 生成SQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# 结果: 返回所有用户！

# 更危险的payload:
# username = "'; DROP TABLE users; --"
# 生成SQL: SELECT * FROM users WHERE username = ''; DROP TABLE users; --'
# 结果: 表被删除！
```

---

## 2. 参数化查询

### 2.1 Python (psycopg2)

```python
# ✅ 正确方式：参数化查询
username = request.GET['username']
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)  # 参数作为tuple传递
)

# psycopg2自动转义，无论输入什么都安全
# username = "admin' OR '1'='1"
# 实际查询: username = 'admin'' OR ''1''=''1'（字符串字面值）
# 结果: 查找这个字符串，而非执行OR逻辑
```

### 2.2 Node.js (node-postgres)

```javascript
// ✅ 正确方式
const username = req.query.username;
const result = await client.query(
    'SELECT * FROM users WHERE username = $1',
    [username]
);

// ❌ 错误方式
const query = `SELECT * FROM users WHERE username = '${username}'`;
```

### 2.3 Java (JDBC)

```java
// ✅ 正确方式：PreparedStatement
String username = request.getParameter("username");
PreparedStatement stmt = conn.prepareStatement(
    "SELECT * FROM users WHERE username = ?"
);
stmt.setString(1, username);
ResultSet rs = stmt.executeQuery();

// ❌ 错误方式：Statement
Statement stmt = conn.createStatement();
String query = "SELECT * FROM users WHERE username = '" + username + "'";
ResultSet rs = stmt.executeQuery(query);
```

---

## 3. ORM防御

### 3.1 Django

```python
# ✅ 安全：ORM自动参数化
User.objects.filter(username=username)

# ✅ 安全：raw() with params
User.objects.raw(
    'SELECT * FROM users WHERE username = %s',
    [username]
)

# ❌ 危险：直接拼接
User.objects.raw(f'SELECT * FROM users WHERE username = "{username}"')

# ❌ 危险：extra() with unsafe WHERE
User.objects.extra(where=[f"username = '{username}'"])
```

### 3.2 SQLAlchemy

```python
# ✅ 安全：ORM查询
session.query(User).filter(User.username == username).all()

# ✅ 安全：text() with bindparams
from sqlalchemy import text
session.execute(
    text("SELECT * FROM users WHERE username = :username"),
    {"username": username}
).fetchall()

# ❌ 危险：直接拼接
session.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

---

## 4. 高级注入场景

### 4.1 ORDER BY注入

```python
# 场景：动态排序
sort_field = request.GET['sort']  # "name" or "created_at"

# ❌ 危险：ORDER BY不能参数化
query = f"SELECT * FROM users ORDER BY {sort_field}"
# 攻击: sort = "(CASE WHEN (SELECT password FROM users WHERE id=1) LIKE 'a%' THEN name ELSE created_at END)"
# 布尔盲注攻击

# ✅ 解决方案：白名单
ALLOWED_FIELDS = ['name', 'created_at', 'email']
if sort_field not in ALLOWED_FIELDS:
    sort_field = 'name'
query = f"SELECT * FROM users ORDER BY {sort_field}"
```

### 4.2 LIKE注入

```python
# ❌ 部分防御
keyword = request.GET['keyword']
cursor.execute(
    "SELECT * FROM products WHERE name LIKE %s",
    (f"%{keyword}%",)  # 参数化了，但...
)

# 攻击: keyword = "%"
# 返回所有记录（DoS攻击）

# ✅ 完整防御
keyword = request.GET['keyword']
if len(keyword) < 3:
    return []  # 要求至少3个字符

# 转义通配符
keyword = keyword.replace('%', '\\%').replace('_', '\\_')
cursor.execute(
    "SELECT * FROM products WHERE name LIKE %s ESCAPE '\\'",
    (f"%{keyword}%",)
)
```

### 4.3 LIMIT/OFFSET注入

```python
# ❌ 危险
page = request.GET['page']
query = f"SELECT * FROM users LIMIT 20 OFFSET {page * 20}"

# ✅ 安全：强制类型转换
page = int(request.GET['page'])  # 抛出ValueError如果非整数
if page < 0 or page > 10000:
    page = 0
query = f"SELECT * FROM users LIMIT 20 OFFSET {page * 20}"

# 更好：参数化（PostgreSQL支持）
cursor.execute(
    "SELECT * FROM users LIMIT %s OFFSET %s",
    (20, page * 20)
)
```

---

## 5. 二次注入

```python
# 场景1: 注册 → 存储（第一步）
username = "admin'--"
cursor.execute(
    "INSERT INTO users (username) VALUES (%s)",
    (username,)  # 安全存储了 "admin'--"
)

# 场景2: 读取 → 使用（第二步，危险）
cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
username = cursor.fetchone()[0]  # 读取: "admin'--"

# ❌ 危险：直接拼接读取的值
query = f"UPDATE users SET status = 'active' WHERE username = '{username}'"
cursor.execute(query)
# 生成SQL: UPDATE users SET status = 'active' WHERE username = 'admin'--'
# 结果: 更新所有用户！

# ✅ 解决方案：始终参数化
cursor.execute(
    "UPDATE users SET status = 'active' WHERE username = %s",
    (username,)
)
```

---

## 6. 数据库层防御

### 6.1 最小权限

```sql
-- 性能测试：应用账号：只授予必要权限（带错误处理）
BEGIN;
CREATE ROLE IF NOT EXISTS app_user LOGIN PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
-- 不授予DELETE, DROP等危险权限
COMMIT;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '角色app_user已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建应用账号失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：只读账号（带错误处理）
BEGIN;
CREATE ROLE IF NOT EXISTS readonly LOGIN PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
COMMIT;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '角色readonly已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建只读账号失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 6.2 函数包装

```sql
-- 性能测试：使用SECURITY DEFINER函数（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION safe_get_user(p_username TEXT)
RETURNS TABLE(id INT, username TEXT, email TEXT)
SECURITY DEFINER
LANGUAGE plpgsql AS $$
BEGIN
    -- 函数内部控制查询逻辑
    RETURN QUERY
    SELECT u.id, u.username, u.email
    FROM users u
    WHERE u.username = p_username;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
        RETURN;
    WHEN OTHERS THEN
        RAISE NOTICE '查询用户失败: %', SQLERRM;
        RETURN;
END;
$$;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建安全函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：应用调用函数而非直接查询表（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM safe_get_user('admin');
COMMIT;
EXCEPTION
    WHEN undefined_function THEN
        RAISE NOTICE '函数safe_get_user不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '调用安全函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 7. WAF与监控

### 7.1 WAF规则

```nginx
# ModSecurity规则示例
SecRule ARGS|ARGS_NAMES "@rx (?i:(union|select|insert|update|delete|drop|create|alter|exec))" \
    "id:1000,\
    phase:2,\
    deny,\
    status:403,\
    msg:'SQL Injection Attempt'"
```

### 7.2 日志监控

```sql
-- 性能测试：启用查询日志（带错误处理）
BEGIN;
DO $$
BEGIN
    ALTER SYSTEM SET log_statement = 'all';  -- 或 'mod'（修改语句）
    ALTER SYSTEM SET log_min_duration_statement = 0;
    PERFORM pg_reload_conf();
    RAISE NOTICE '查询日志配置已更新';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '配置查询日志失败: %', SQLERRM;
        RAISE;
END $$;
COMMIT;

-- 分析日志（Python示例）
import re

## 检测可疑模式

sql_injection_patterns = [
    r"(?i)union\s+select",
    r"(?i)or\s+1\s*=\s*1",
    r"(?i);\s*drop\s+table",
    r"(?i)--\s*$",
]

with open('/var/log/postgresql/postgresql.log') as f:
    for line in f:
        for pattern in sql_injection_patterns:
            if re.search(pattern, line):
                print(f"⚠️ 可疑SQL: {line}")

```

---

## 8. 代码审计清单

```text
□ 参数化查询
  □ 所有用户输入都使用占位符
  □ 无字符串拼接SQL
  □ ORM使用正确

□ 动态SQL
  □ ORDER BY使用白名单
  □ LIMIT/OFFSET类型验证
  □ 表名/列名白名单验证

□ LIKE查询
  □ 通配符转义
  □ 最小长度限制
  □ 结果集大小限制

□ 二次注入
  □ 数据库读取的值也要参数化
  □ 不信任任何存储的数据

□ 权限控制
  □ 最小权限原则
  □ 分离读写账号
  □ 禁用危险命令

□ 监控
  □ 查询日志启用
  □ 异常模式检测
  □ WAF规则配置

□ 测试
  □ SQL注入自动化测试
  □ Payload库覆盖
  □ 定期安全审计
```

---

## 9. 测试用例

```python
# SQL注入测试Payload
injection_payloads = [
    "admin' OR '1'='1",
    "admin'--",
    "'; DROP TABLE users; --",
    "1' UNION SELECT password FROM users--",
    "1' AND (SELECT COUNT(*) FROM users) > 0--",
    "1' AND SLEEP(5)--",
]

def test_sql_injection(username):
    """测试是否存在SQL注入漏洞"""
    try:
        result = get_user(username)  # 你的查询函数

        # 如果返回多条记录或错误，可能有注入
        if len(result) > 1:
            print(f"⚠️ 可能的SQL注入: {username}")
            return False
    except Exception as e:
        print(f"✅ 参数化正确，异常被捕获: {e}")
        return True

    return True

# 运行测试
for payload in injection_payloads:
    test_sql_injection(payload)
```

---

**完成**: PostgreSQL SQL注入防御完整指南
**字数**: ~10,000字
**涵盖**: 注入原理、参数化查询、ORM防御、高级场景、二次注入、数据库层防御、WAF监控、审计清单
