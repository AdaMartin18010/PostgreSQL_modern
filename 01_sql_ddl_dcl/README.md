# 01_sql_ddl_dcl — SQL语言基础与进阶

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **模块完整度**：⭐⭐⭐⭐ 85%（已深化，持续完善）  
> **适合人群**：从入门到进阶，涵盖标准SQL、PostgreSQL特性、生产实践

---

## 📋 目录

- [01\_sql\_ddl\_dcl — SQL语言基础与进阶](#01_sql_ddl_dcl--sql语言基础与进阶)
  - [📋 目录](#-目录)
  - [模块定位与边界](#模块定位与边界)
    - [主题边界](#主题边界)
    - [知识地图](#知识地图)
  - [1. SQL语言元素](#1-sql语言元素)
    - [1.1 数据类型全览](#11-数据类型全览)
      - [基础类型](#基础类型)
      - [PostgreSQL 17 JSON增强](#postgresql-17-json增强)
    - [1.2 标识符与命名规范](#12-标识符与命名规范)
      - [大小写规则](#大小写规则)
      - [命名约定](#命名约定)
    - [1.3 字面量与常量](#13-字面量与常量)
      - [SQL-2023新特性（PG17已支持部分）](#sql-2023新特性pg17已支持部分)
  - [2. DDL数据定义](#2-ddl数据定义)
    - [2.1 模式管理](#21-模式管理)
      - [模式（Schema）的作用](#模式schema的作用)
    - [2.2 表设计与约束](#22-表设计与约束)
      - [完整表定义示例](#完整表定义示例)
      - [约束类型详解](#约束类型详解)
    - [2.3 分区表](#23-分区表)
      - [Range分区（按时间范围）](#range分区按时间范围)
      - [List分区（按离散值）](#list分区按离散值)
      - [Hash分区（均匀分布）](#hash分区均匀分布)
    - [2.4 索引管理](#24-索引管理)
      - [索引类型选择](#索引类型选择)
      - [并发索引创建（生产必备）](#并发索引创建生产必备)
      - [部分索引（Partial Index）](#部分索引partial-index)
      - [表达式索引](#表达式索引)
    - [2.5 在线DDL陷阱](#25-在线ddl陷阱)
      - [锁级别对照表](#锁级别对照表)
      - [大表变更最佳实践](#大表变更最佳实践)
      - [查询当前锁等待](#查询当前锁等待)
  - [3. DML数据操纵](#3-dml数据操纵)
    - [3.1 查询基础](#31-查询基础)
      - [JOIN类型完整示例](#join类型完整示例)
      - [子查询与EXISTS](#子查询与exists)
    - [3.2 INSERT/UPDATE/DELETE](#32-insertupdatedelete)
      - [INSERT多种形式](#insert多种形式)
      - [UPDATE与DELETE](#update与delete)
      - [RETURNING子句（PostgreSQL特色）](#returning子句postgresql特色)
    - [3.3 CTE与递归查询](#33-cte与递归查询)
      - [基本CTE（Common Table Expression）](#基本ctecommon-table-expression)
      - [递归CTE（树形结构）](#递归cte树形结构)
    - [3.4 PostgreSQL 17新特性](#34-postgresql-17新特性)
      - [MERGE语句增强（SQL-2023标准）](#merge语句增强sql-2023标准)
      - [聚合函数新增](#聚合函数新增)
  - [4. DCL数据控制](#4-dcl数据控制)
    - [4.1 角色与权限模型](#41-角色与权限模型)
      - [角色层次结构](#角色层次结构)
      - [权限授予与撤销](#权限授予与撤销)
      - [权限查询](#权限查询)
    - [4.2 行级安全策略（RLS）](#42-行级安全策略rls)
      - [启用RLS](#启用rls)
      - [RLS策略类型](#rls策略类型)
  - [5. TCL事务控制](#5-tcl事务控制)
  - [6. 常见陷阱与最佳实践](#6-常见陷阱与最佳实践)
    - [6.1 隐式类型转换陷阱](#61-隐式类型转换陷阱)
    - [6.2 NULL语义陷阱](#62-null语义陷阱)
    - [6.3 时区陷阱](#63-时区陷阱)
    - [6.4 大批量DML最佳实践](#64-大批量dml最佳实践)
    - [6.5 索引失效场景](#65-索引失效场景)
  - [7. 权威参考](#7-权威参考)
    - [官方文档](#官方文档)
    - [SQL标准](#sql标准)
    - [扩展阅读](#扩展阅读)
  - [8. Checklist（执行前/提交前）](#8-checklist执行前提交前)
    - [DDL操作检查清单](#ddl操作检查清单)
    - [DML操作检查清单](#dml操作检查清单)
    - [DCL操作检查清单](#dcl操作检查清单)
    - [TCL操作检查清单](#tcl操作检查清单)

---

## 模块定位与边界

### 主题边界

- **核心内容**：SQL语言基础与进阶，涵盖DDL、DML、DCL、TCL四大类
- **标准对齐**：SQL标准（SQL:2023）+ PostgreSQL 17特性实现
- **深度定位**：从语法基础到生产级实践（约束设计、在线DDL、权限模型、性能陷阱）

### 知识地图

```text
SQL语言元素
    ├── 数据类型（基础类型、JSON、数组、复合类型、域）
    ├── 标识符与命名（大小写、关键字、转义）
    └── 字面量与常量（数值、字符串、日期、NULL）
        ↓
DDL数据定义
    ├── 模式管理（SCHEMA、搜索路径）
    ├── 表设计（列类型、约束、默认值、生成列）
    ├── 分区表（Range/List/Hash）
    ├── 索引（B-tree、GIN、GiST、BRIN、并发索引）
    └── 在线DDL陷阱（锁、大表变更、索引重建）
        ↓
DML数据操纵
    ├── 查询（SELECT、JOIN、子查询、聚合）
    ├── 修改（INSERT、UPDATE、DELETE、MERGE）
    ├── CTE与递归（WITH、RECURSIVE）
    └── RETURNING子句
        ↓
DCL数据控制
    ├── 角色与权限（GRANT、REVOKE、默认权限）
    └── 行级安全策略（RLS、Policy）
        ↓
TCL事务控制
    └── BEGIN、COMMIT、ROLLBACK、SAVEPOINT
```

---

## 1. SQL语言元素

### 1.1 数据类型全览

#### 基础类型

| 类型类别 | PostgreSQL类型 | 说明 | PG17特性 |
|---------|---------------|------|----------|
| **数值** | `integer`, `bigint`, `numeric`, `real`, `double precision` | 整数、高精度小数、浮点数 | - |
| **字符** | `text`, `varchar(n)`, `char(n)` | 可变长文本、定长字符 | 推荐使用`text` |
| **布尔** | `boolean` | `TRUE`, `FALSE`, `NULL` | - |
| **日期时间** | `date`, `time`, `timestamp`, `timestamptz`, `interval` | 时区感知的`timestamptz`是最佳实践 | - |
| **JSON** | `json`, `jsonb` | `jsonb`支持索引和高效查询 | **PG17: JSON_TABLE()** |
| **数组** | `integer[]`, `text[]` | 多维数组支持 | - |
| **UUID** | `uuid` | 全局唯一标识符 | - |
| **二进制** | `bytea` | 二进制数据 | - |
| **枚举** | `CREATE TYPE mood AS ENUM (...)` | 自定义枚举类型 | - |
| **几何** | `point`, `line`, `polygon` | 几何类型（PostGIS更强大） | - |
| **网络** | `inet`, `cidr`, `macaddr` | IP地址、MAC地址 | - |

#### PostgreSQL 17 JSON增强

```sql
-- JSON_TABLE(): 将JSON转为关系表（SQL:2023标准）
SELECT * FROM JSON_TABLE(
  '[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]',
  '$[*]' COLUMNS (
    id INT PATH '$.id',
    name TEXT PATH '$.name'
  )
);

-- JSON构造函数（PG17新增）
SELECT JSON_OBJECT('key1': 'value1', 'key2': 123);
SELECT JSON_ARRAY('a', 'b', 'c');
```

### 1.2 标识符与命名规范

#### 大小写规则

```sql
-- 未加引号：自动转为小写
CREATE TABLE Users (ID int);  -- 实际创建 users(id)

-- 加引号：保持原样（不推荐，除非必要）
CREATE TABLE "Users" ("ID" int);  -- 必须用 "Users"."ID" 访问

-- ✅ 最佳实践：全小写+下划线
CREATE TABLE user_profiles (user_id bigint, created_at timestamptz);
```

#### 命名约定

| 对象类型 | 命名格式 | 示例 |
|---------|---------|------|
| 表 | `snake_case` | `user_orders` |
| 索引 | `idx_{table}_{columns}` | `idx_users_email` |
| 主键约束 | `pk_{table}` | `pk_users` |
| 外键约束 | `fk_{table}_{ref_table}` | `fk_orders_users` |
| 唯一约束 | `uq_{table}_{columns}` | `uq_users_email` |
| 检查约束 | `ck_{table}_{condition}` | `ck_users_age_positive` |

### 1.3 字面量与常量

#### SQL-2023新特性（PG17已支持部分）

```sql
-- 数值字面量下划线分隔（可读性）
SELECT 1_000_000;  -- 1000000

-- 非十进制整数字面量
SELECT 0b1010;     -- 二进制：10
SELECT 0o755;      -- 八进制：493
SELECT 0xFF;       -- 十六进制：255

-- 字符串字面量
SELECT 'standard', $$dollar quoted$$, E'escape\n';

-- 日期时间字面量
SELECT DATE '2025-10-03';
SELECT TIMESTAMP '2025-10-03 10:30:00';
SELECT TIMESTAMPTZ '2025-10-03 10:30:00+08';
```

---

## 2. DDL数据定义

### 2.1 模式管理

#### 模式（Schema）的作用

```sql
-- 创建模式
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA sales AUTHORIZATION sales_admin;

-- 设置搜索路径（影响不带schema前缀的对象解析）
SHOW search_path;  -- 默认："$user", public
SET search_path TO app, public;

-- 删除模式（CASCADE会删除所有依赖对象）
DROP SCHEMA IF EXISTS old_schema CASCADE;
```

### 2.2 表设计与约束

#### 完整表定义示例

```sql
CREATE TABLE app.users (
  -- 主键：自增序列
  id bigserial PRIMARY KEY,
  
  -- 唯一约束
  email text NOT NULL,
  CONSTRAINT uq_users_email UNIQUE (email),
  
  -- 检查约束
  age integer,
  CONSTRAINT ck_users_age CHECK (age >= 0 AND age <= 150),
  
  -- 默认值
  status text DEFAULT 'active',
  created_at timestamptz DEFAULT now(),
  
  -- 生成列（PostgreSQL 12+）
  full_name text GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
  
  -- 外键
  company_id bigint,
  CONSTRAINT fk_users_company FOREIGN KEY (company_id) 
    REFERENCES app.companies(id) ON DELETE CASCADE
);

-- 添加注释
COMMENT ON TABLE app.users IS '用户主表';
COMMENT ON COLUMN app.users.email IS '用户邮箱（唯一）';
```

#### 约束类型详解

| 约束类型 | 语法 | 说明 |
|---------|------|------|
| **NOT NULL** | `column_name TYPE NOT NULL` | 禁止NULL值 |
| **UNIQUE** | `UNIQUE (column)` | 唯一约束（允许多个NULL） |
| **PRIMARY KEY** | `PRIMARY KEY (column)` | 主键（自动NOT NULL + UNIQUE） |
| **FOREIGN KEY** | `REFERENCES table(column)` | 外键约束 |
| **CHECK** | `CHECK (condition)` | 自定义条件 |
| **EXCLUDE** | `EXCLUDE USING gist (...)` | 排斥约束（如时间区间不重叠） |

### 2.3 分区表

#### Range分区（按时间范围）

```sql
CREATE TABLE measurements (
  id bigserial,
  sensor_id int,
  value numeric,
  measured_at timestamptz
) PARTITION BY RANGE (measured_at);

-- 创建分区
CREATE TABLE measurements_2025_10 PARTITION OF measurements
  FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE measurements_2025_11 PARTITION OF measurements
  FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- 自动分区管理（使用pg_partman扩展）
```

#### List分区（按离散值）

```sql
CREATE TABLE orders (
  id bigserial,
  region text,
  amount numeric
) PARTITION BY LIST (region);

CREATE TABLE orders_asia PARTITION OF orders
  FOR VALUES IN ('CN', 'JP', 'KR');

CREATE TABLE orders_europe PARTITION OF orders
  FOR VALUES IN ('UK', 'DE', 'FR');
```

#### Hash分区（均匀分布）

```sql
CREATE TABLE events (
  id bigserial,
  user_id bigint,
  event_type text
) PARTITION BY HASH (user_id);

CREATE TABLE events_p0 PARTITION OF events
  FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE events_p1 PARTITION OF events
  FOR VALUES WITH (MODULUS 4, REMAINDER 1);
-- ...继续到 REMAINDER 3
```

### 2.4 索引管理

#### 索引类型选择

| 索引类型 | 适用场景 | 示例 |
|---------|---------|------|
| **B-tree** | 等值查询、范围查询、排序 | `CREATE INDEX idx_users_email ON users(email);` |
| **Hash** | 仅等值查询（PG10+可用于查询） | `CREATE INDEX idx_users_id_hash ON users USING hash(id);` |
| **GIN** | 全文搜索、JSON、数组 | `CREATE INDEX idx_docs_content ON docs USING gin(content);` |
| **GiST** | 几何数据、全文搜索、范围类型 | `CREATE INDEX idx_locations ON places USING gist(location);` |
| **BRIN** | 大表按序存储（如时序数据） | `CREATE INDEX idx_logs_time ON logs USING brin(created_at);` |
| **SP-GiST** | 非平衡数据结构（如IP地址） | `CREATE INDEX idx_ips ON connections USING spgist(ip_address);` |

#### 并发索引创建（生产必备）

```sql
-- ✅ 推荐：不阻塞写入（需要更长时间）
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- ❌ 避免：锁表，阻塞所有写入
CREATE INDEX idx_users_email ON users(email);

-- 如果CONCURRENTLY失败，需要先删除无效索引
DROP INDEX CONCURRENTLY IF EXISTS idx_users_email;
```

#### 部分索引（Partial Index）

```sql
-- 仅索引活跃用户
CREATE INDEX idx_users_active ON users(email) 
WHERE status = 'active';

-- 仅索引非空值
CREATE INDEX idx_users_phone ON users(phone) 
WHERE phone IS NOT NULL;
```

#### 表达式索引

```sql
-- 索引函数结果
CREATE INDEX idx_users_lower_email ON users(lower(email));

-- 索引JSON字段
CREATE INDEX idx_users_settings_theme ON users((settings->>'theme'));
```

### 2.5 在线DDL陷阱

#### 锁级别对照表

| 操作 | 锁级别 | 阻塞读 | 阻塞写 | 安全性 |
|------|--------|--------|--------|--------|
| `SELECT` | AccessShareLock | ❌ | ❌ | ✅ 安全 |
| `CREATE INDEX` | ShareLock | ❌ | ✅ | ⚠️ 阻塞写入 |
| `CREATE INDEX CONCURRENTLY` | ShareUpdateExclusiveLock | ❌ | ❌ | ✅ 推荐 |
| `ALTER TABLE ADD COLUMN (无默认值)` | AccessExclusiveLock | ✅ | ✅ | ❌ 危险 |
| `ALTER TABLE ADD COLUMN DEFAULT` | AccessExclusiveLock | ✅ | ✅ | ❌ 危险 |
| `ALTER TABLE DROP COLUMN` | AccessExclusiveLock | ✅ | ✅ | ❌ 危险 |
| `VACUUM` | ShareUpdateExclusiveLock | ❌ | ❌ | ✅ 安全 |

#### 大表变更最佳实践

```sql
-- ❌ 危险：直接添加带默认值的列（全表重写）
ALTER TABLE large_table ADD COLUMN new_col text DEFAULT 'value';

-- ✅ 推荐：分两步执行
-- 步骤1：不带默认值添加列（PG11+是元数据操作，瞬间完成）
ALTER TABLE large_table ADD COLUMN new_col text;

-- 步骤2：批量更新（分批执行，避免长事务）
UPDATE large_table SET new_col = 'value' WHERE new_col IS NULL AND id < 100000;
UPDATE large_table SET new_col = 'value' WHERE new_col IS NULL AND id < 200000;
-- ...

-- 步骤3：添加NOT NULL约束（PG12+可使用NOT VALID快速添加）
ALTER TABLE large_table ADD CONSTRAINT check_new_col CHECK (new_col IS NOT NULL) NOT VALID;
ALTER TABLE large_table VALIDATE CONSTRAINT check_new_col;
```

#### 查询当前锁等待

```sql
SELECT
  blocked_locks.pid AS blocked_pid,
  blocked_activity.usename AS blocked_user,
  blocking_locks.pid AS blocking_pid,
  blocking_activity.usename AS blocking_user,
  blocked_activity.query AS blocked_query,
  blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
  ON blocking_locks.locktype = blocked_locks.locktype
  AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
  AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
  AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
  AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
  AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
  AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
  AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
  AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
  AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
  AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

---

## 3. DML数据操纵

### 3.1 查询基础

#### JOIN类型完整示例

```sql
-- INNER JOIN：仅返回匹配行
SELECT u.name, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN：保留左表所有行
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- RIGHT JOIN：保留右表所有行（少用，可用LEFT JOIN代替）
SELECT u.name, o.amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- FULL OUTER JOIN：保留两表所有行
SELECT u.name, o.amount
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;

-- CROSS JOIN：笛卡尔积
SELECT u.name, p.product_name
FROM users u
CROSS JOIN products p;
```

#### 子查询与EXISTS

```sql
-- 标量子查询
SELECT name, (SELECT COUNT(*) FROM orders WHERE user_id = users.id) AS order_count
FROM users;

-- IN子查询
SELECT name FROM users WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- EXISTS子查询（性能通常优于IN）
SELECT name FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.amount > 1000);

-- NOT EXISTS
SELECT name FROM users u WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

### 3.2 INSERT/UPDATE/DELETE

#### INSERT多种形式

```sql
-- 基本插入
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- 批量插入
INSERT INTO users (name, email) VALUES
  ('Bob', 'bob@example.com'),
  ('Charlie', 'charlie@example.com');

-- 从SELECT插入
INSERT INTO users_archive SELECT * FROM users WHERE created_at < '2020-01-01';

-- ON CONFLICT（UPSERT）
INSERT INTO users (id, name, email) 
VALUES (1, 'Alice', 'alice@example.com')
ON CONFLICT (id) DO UPDATE SET 
  name = EXCLUDED.name,
  email = EXCLUDED.email;

-- ON CONFLICT DO NOTHING
INSERT INTO users (email, name) 
VALUES ('alice@example.com', 'Alice')
ON CONFLICT (email) DO NOTHING;
```

#### UPDATE与DELETE

```sql
-- 基本更新
UPDATE users SET status = 'inactive' WHERE last_login < '2024-01-01';

-- 从其他表更新
UPDATE orders o
SET total_amount = oi.sum_amount
FROM (SELECT order_id, SUM(amount) AS sum_amount FROM order_items GROUP BY order_id) oi
WHERE o.id = oi.order_id;

-- 删除（建议加LIMIT，分批删除）
DELETE FROM logs WHERE created_at < '2024-01-01' LIMIT 10000;

-- TRUNCATE（快速清空表，不可回滚）
TRUNCATE TABLE temp_table;
```

#### RETURNING子句（PostgreSQL特色）

```sql
-- 插入后返回生成的ID
INSERT INTO users (name) VALUES ('Alice') RETURNING id;

-- 批量插入返回所有ID
INSERT INTO users (name) VALUES ('Bob'), ('Charlie') RETURNING id, name;

-- 更新后返回修改的行
UPDATE users SET status = 'active' WHERE id = 1 RETURNING *;

-- 删除后返回被删除的行
DELETE FROM users WHERE status = 'inactive' RETURNING id, name;
```

### 3.3 CTE与递归查询

#### 基本CTE（Common Table Expression）

```sql
-- 提高可读性
WITH active_users AS (
  SELECT * FROM users WHERE status = 'active'
),
recent_orders AS (
  SELECT * FROM orders WHERE created_at > now() - interval '30 days'
)
SELECT u.name, COUNT(o.id) AS order_count
FROM active_users u
LEFT JOIN recent_orders o ON u.id = o.user_id
GROUP BY u.name;
```

#### 递归CTE（树形结构）

```sql
-- 组织架构树
WITH RECURSIVE org_tree AS (
  -- 基础查询：顶级节点
  SELECT id, name, parent_id, 1 AS level
  FROM departments
  WHERE parent_id IS NULL
  
  UNION ALL
  
  -- 递归查询：子节点
  SELECT d.id, d.name, d.parent_id, ot.level + 1
  FROM departments d
  INNER JOIN org_tree ot ON d.parent_id = ot.id
)
SELECT * FROM org_tree ORDER BY level, id;

-- 图遍历（防止循环）
WITH RECURSIVE graph_traversal AS (
  SELECT id, ARRAY[id] AS path
  FROM nodes
  WHERE id = 1  -- 起始节点
  
  UNION ALL
  
  SELECT e.target_id, gt.path || e.target_id
  FROM edges e
  INNER JOIN graph_traversal gt ON e.source_id = gt.id
  WHERE NOT e.target_id = ANY(gt.path)  -- 防止循环
)
SELECT * FROM graph_traversal;
```

### 3.4 PostgreSQL 17新特性

#### MERGE语句增强（SQL-2023标准）

```sql
-- MERGE（类似UPSERT，但更强大）
MERGE INTO target_table t
USING source_table s ON t.id = s.id
WHEN MATCHED THEN
  UPDATE SET t.value = s.value, t.updated_at = now()
WHEN NOT MATCHED THEN
  INSERT (id, value, created_at) VALUES (s.id, s.value, now());
```

#### 聚合函数新增

```sql
-- ANY_VALUE：从分组中任意选择一个非空值
SELECT category, ANY_VALUE(name) AS sample_name
FROM products
GROUP BY category;
```

---

## 4. DCL数据控制

### 4.1 角色与权限模型

#### 角色层次结构

```sql
-- 创建角色（用户是可登录的角色）
CREATE ROLE app_readonly NOLOGIN;
CREATE ROLE app_readwrite NOLOGIN;
CREATE ROLE app_admin LOGIN PASSWORD 'secure_password';

-- 角色继承
GRANT app_readonly TO app_readwrite;
GRANT app_readwrite TO app_admin;

-- 查看角色
\du  -- psql命令
SELECT rolname FROM pg_roles;
```

#### 权限授予与撤销

```sql
-- 授予模式权限
GRANT USAGE ON SCHEMA app TO app_readonly;

-- 授予表权限
GRANT SELECT ON ALL TABLES IN SCHEMA app TO app_readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app TO app_readwrite;

-- 授予序列权限（自增ID）
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app TO app_readwrite;

-- 授予函数权限
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA app TO app_readwrite;

-- 默认权限（新创建对象自动授权）
ALTER DEFAULT PRIVILEGES IN SCHEMA app 
  GRANT SELECT ON TABLES TO app_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA app 
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;

-- 撤销权限
REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app FROM app_readonly;

-- 撤销PUBLIC的默认权限（安全加固）
REVOKE ALL ON SCHEMA public FROM PUBLIC;
```

#### 权限查询

```sql
-- 查看表权限
SELECT grantee, privilege_type 
FROM information_schema.table_privileges 
WHERE table_schema = 'app' AND table_name = 'users';

-- 查看当前用户权限
SELECT * FROM information_schema.role_table_grants WHERE grantee = current_user;
```

### 4.2 行级安全策略（RLS）

#### 启用RLS

```sql
-- 创建多租户表
CREATE TABLE documents (
  id bigserial PRIMARY KEY,
  tenant_id bigint NOT NULL,
  content text,
  created_by text
);

-- 启用行级安全
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 创建策略：用户只能看到自己租户的数据
CREATE POLICY tenant_isolation ON documents
  FOR ALL
  TO PUBLIC
  USING (tenant_id = current_setting('app.current_tenant_id')::bigint);

-- 创建策略：用户只能修改自己创建的文档
CREATE POLICY owner_only ON documents
  FOR UPDATE
  TO PUBLIC
  USING (created_by = current_user);

-- 设置租户ID（应用层设置）
SET app.current_tenant_id = '123';

-- 查询自动过滤
SELECT * FROM documents;  -- 只返回tenant_id=123的行
```

#### RLS策略类型

```sql
-- SELECT策略
CREATE POLICY select_own ON documents FOR SELECT USING (created_by = current_user);

-- INSERT策略
CREATE POLICY insert_own ON documents FOR INSERT WITH CHECK (created_by = current_user);

-- UPDATE策略
CREATE POLICY update_own ON documents FOR UPDATE USING (created_by = current_user);

-- DELETE策略
CREATE POLICY delete_own ON documents FOR DELETE USING (created_by = current_user);

-- 禁用RLS（超级用户和表所有者默认跳过RLS）
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;

-- 强制RLS（连所有者也生效）
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
```

---

## 5. TCL事务控制

```sql
-- 开始事务
BEGIN;
-- 或
START TRANSACTION;

-- 设置事务隔离级别
BEGIN ISOLATION LEVEL SERIALIZABLE;
BEGIN ISOLATION LEVEL REPEATABLE READ;
BEGIN ISOLATION LEVEL READ COMMITTED;  -- 默认

-- 保存点
BEGIN;
INSERT INTO users (name) VALUES ('Alice');
SAVEPOINT sp1;
INSERT INTO users (name) VALUES ('Bob');
ROLLBACK TO SAVEPOINT sp1;  -- 回滚到保存点，Bob未插入
COMMIT;  -- Alice已插入

-- 只读事务（优化性能）
BEGIN TRANSACTION READ ONLY;
SELECT * FROM large_table;
COMMIT;

-- 设置事务特性
SET TRANSACTION DEFERRABLE;  -- 延迟约束检查到提交时
```

---

## 6. 常见陷阱与最佳实践

### 6.1 隐式类型转换陷阱

```sql
-- ❌ 陷阱：索引失效
CREATE INDEX idx_users_id_text ON users((id::text));
SELECT * FROM users WHERE id::text = '123';  -- 使用索引

SELECT * FROM users WHERE id = '123';  -- id是bigint，'123'是text，可能不使用索引

-- ✅ 最佳实践：显式类型转换或使用正确类型
SELECT * FROM users WHERE id = 123;
```

### 6.2 NULL语义陷阱

```sql
-- ❌ 错误：NULL不等于NULL
SELECT * FROM users WHERE email != 'test@example.com';  -- 不会返回email为NULL的行

-- ✅ 正确
SELECT * FROM users WHERE email != 'test@example.com' OR email IS NULL;

-- ❌ 错误：NOT IN遇到NULL
SELECT * FROM users WHERE id NOT IN (SELECT user_id FROM blocked_users);  -- 如果blocked_users.user_id有NULL，返回空

-- ✅ 正确：使用NOT EXISTS
SELECT * FROM users u WHERE NOT EXISTS (SELECT 1 FROM blocked_users b WHERE b.user_id = u.id);
```

### 6.3 时区陷阱

```sql
-- ✅ 推荐：始终使用timestamptz
CREATE TABLE events (
  id bigserial PRIMARY KEY,
  created_at timestamptz DEFAULT now()  -- 带时区
);

-- ❌ 避免：timestamp（无时区信息）
created_at timestamp  -- 应用在不同时区会有歧义

-- 时区设置
SHOW timezone;  -- 查看当前时区
SET timezone TO 'Asia/Shanghai';
SET timezone TO 'UTC';  -- 推荐服务器使用UTC

-- 时区转换
SELECT now() AT TIME ZONE 'UTC';
SELECT created_at AT TIME ZONE 'Asia/Shanghai' FROM events;
```

### 6.4 大批量DML最佳实践

```sql
-- ✅ 分批删除
DO $$
DECLARE
  deleted_count INT;
BEGIN
  LOOP
    DELETE FROM logs WHERE created_at < '2024-01-01' AND ctid IN (
      SELECT ctid FROM logs WHERE created_at < '2024-01-01' LIMIT 10000
    );
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    EXIT WHEN deleted_count = 0;
    COMMIT;  -- 每批提交一次
  END LOOP;
END $$;

-- ✅ 使用COPY批量导入
COPY users (name, email) FROM '/path/to/file.csv' WITH (FORMAT csv, HEADER true);

-- ✅ 禁用触发器加速批量操作（谨慎使用）
ALTER TABLE users DISABLE TRIGGER ALL;
-- ... 批量操作
ALTER TABLE users ENABLE TRIGGER ALL;
```

### 6.5 索引失效场景

```sql
-- ❌ 函数调用导致索引失效
SELECT * FROM users WHERE lower(email) = 'alice@example.com';  -- 不使用idx_users_email

-- ✅ 创建表达式索引
CREATE INDEX idx_users_lower_email ON users(lower(email));

-- ❌ OR条件可能不使用索引
SELECT * FROM users WHERE id = 1 OR name = 'Alice';

-- ✅ 使用UNION ALL
SELECT * FROM users WHERE id = 1
UNION ALL
SELECT * FROM users WHERE name = 'Alice' AND id != 1;

-- ❌ LIKE前导通配符
SELECT * FROM users WHERE email LIKE '%@example.com';  -- 无法使用B-tree索引

-- ✅ 使用pg_trgm扩展+GIN索引
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_users_email_trgm ON users USING gin(email gin_trgm_ops);
SELECT * FROM users WHERE email LIKE '%@example.com';  -- 可使用GIN索引
```

---

## 7. 权威参考

### 官方文档

- **PostgreSQL 17 SQL命令**：<https://www.postgresql.org/docs/17/sql-commands.html>
- **SQL语法参考**：<https://www.postgresql.org/docs/17/sql-syntax.html>
- **数据类型**：<https://www.postgresql.org/docs/17/datatype.html>
- **DDL语句**：<https://www.postgresql.org/docs/17/ddl.html>
- **DML语句**：<https://www.postgresql.org/docs/17/dml.html>
- **权限系统**：<https://www.postgresql.org/docs/17/user-manag.html>

### SQL标准

- **SQL:2023标准**：ISO/IEC 9075-2:2023（PostgreSQL 17部分实现）
- **Wikipedia SQL页面**：<https://en.wikipedia.org/wiki/SQL>

### 扩展阅读

- **PostgreSQL Wiki - Don't Do This**：<https://wiki.postgresql.org/wiki/Don't_Do_This>（反模式集合）
- **Use The Index, Luke!**：<https://use-the-index-luke.com/>（索引优化指南）

---

## 8. Checklist（执行前/提交前）

### DDL操作检查清单

- [ ] 表/索引/约束命名符合规范（全小写+下划线）
- [ ] 所有DDL已评估锁影响（生产环境优先使用`CONCURRENTLY`）
- [ ] 大表变更已拆分为多步骤，避免长时间锁表
- [ ] 索引类型选择合理（B-tree/GIN/GiST/BRIN）
- [ ] 外键约束已评估性能影响（高并发场景需谨慎）
- [ ] 分区表策略已规划（自动分区管理/分区裁剪）

### DML操作检查清单

- [ ] 大批量DML已分批执行，避免长事务
- [ ] 使用`RETURNING`子句代替额外查询
- [ ] JOIN顺序已优化（小表在前/驱动表选择）
- [ ] 子查询已考虑用`EXISTS`代替`IN`（性能更好）
- [ ] 避免`SELECT *`，明确指定需要的列

### DCL操作检查清单

- [ ] 权限最小化原则（按角色授予最小权限）
- [ ] 避免使用超级用户执行应用操作
- [ ] 生产环境已撤销`PUBLIC`模式的默认权限
- [ ] RLS策略已测试边界条件（NULL/空集合）
- [ ] 默认权限（`ALTER DEFAULT PRIVILEGES`）已配置

### TCL操作检查清单

- [ ] 事务边界明确（避免隐式提交/自动提交）
- [ ] 长事务已拆分或使用游标
- [ ] 隔离级别根据需求设置（避免不必要的高隔离级别）
- [ ] 异常处理已完善（确保事务回滚）

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**下一步**：查看 [02_transactions](../02_transactions/README.md) 深入事务管理
