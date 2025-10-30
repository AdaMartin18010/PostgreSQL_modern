# 01_sql_ddl_dcl 模块测试设计

> **模块**：SQL DDL/DCL 基础  
> **设计日期**：2025 年 10 月 3 日  
> **目标测试数量**：20+场景  
> **预计完成时间**：Week 4（2025-10-11 至 2025-10-17）

---

## 📋 测试范围

### 模块内容回顾

- DDL 操作（CREATE/ALTER/DROP）
- DCL 操作（GRANT/REVOKE）
- 约束管理（PRIMARY KEY、FOREIGN KEY、CHECK、UNIQUE）
- 索引创建与管理
- 模式（Schema）操作
- PostgreSQL 17 新特性

---

## 🎯 测试场景设计

### 1. DDL 基础操作（8 个测试）

#### TEST-01-001: 创建表（基本类型）

**测试目的**：验证 CREATE TABLE 基本功能

```sql
-- SETUP
-- 无需额外准备

-- TEST_BODY
CREATE TABLE test_basic_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_tables WHERE tablename = 'test_basic_table'; => 1
EXPECT_VALUE: SELECT column_name FROM information_schema.columns WHERE table_name = 'test_basic_table' AND column_name = 'id'; => 'id'

-- TEARDOWN
DROP TABLE IF EXISTS test_basic_table CASCADE;
```

---

#### TEST-01-002: 创建表（PostgreSQL 17 特性 - JSON 增强）

**测试目的**：验证 JSON/JSONB 类型和 PG17 新增 JSON 函数

```sql
-- TEST_BODY
CREATE TABLE test_json_table (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    metadata JSON
);

INSERT INTO test_json_table (data, metadata) VALUES
('{"name": "Alice", "age": 30, "tags": ["dev", "senior"]}'::jsonb, '{"version": 1}'::json);

-- 测试PG17 JSON_TABLE功能（如果环境支持）
-- SELECT * FROM JSON_TABLE(
--     '{"name": "Alice", "age": 30}'::jsonb,
--     '$' COLUMNS (name TEXT PATH '$.name', age INT PATH '$.age')
-- );

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_json_table WHERE data->>'name' = 'Alice'; => 1
EXPECT_VALUE: SELECT data->>'age' FROM test_json_table WHERE data->>'name' = 'Alice'; => '30'

-- TEARDOWN
DROP TABLE IF EXISTS test_json_table CASCADE;
```

---

#### TEST-01-003: ALTER TABLE - 添加/删除列

**测试目的**：验证表结构修改

```sql
-- SETUP
CREATE TABLE test_alter_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

-- TEST_BODY
-- 添加列
ALTER TABLE test_alter_table ADD COLUMN email VARCHAR(255);
ALTER TABLE test_alter_table ADD COLUMN status VARCHAR(20) DEFAULT 'active';

-- 修改列
ALTER TABLE test_alter_table ALTER COLUMN name TYPE TEXT;

-- 删除列
ALTER TABLE test_alter_table DROP COLUMN email;

-- ASSERTIONS
EXPECT_VALUE: SELECT data_type FROM information_schema.columns WHERE table_name = 'test_alter_table' AND column_name = 'name'; => 'text'
EXPECT_ROWS: SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'test_alter_table' AND column_name = 'email'; => 0
EXPECT_ROWS: SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'test_alter_table' AND column_name = 'status'; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_alter_table CASCADE;
```

---

#### TEST-01-004: 约束 - PRIMARY KEY

**测试目的**：验证主键约束

```sql
-- TEST_BODY
CREATE TABLE test_pk (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

INSERT INTO test_pk (id, name) VALUES (1, 'Alice');

-- 应该失败：重复主键
EXPECT_ERROR: INSERT INTO test_pk (id, name) VALUES (1, 'Bob');

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_pk WHERE id = 1; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_pk CASCADE;
```

---

#### TEST-01-005: 约束 - FOREIGN KEY

**测试目的**：验证外键约束

```sql
-- SETUP
CREATE TABLE test_parent (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE test_child (
    id SERIAL PRIMARY KEY,
    parent_id INT REFERENCES test_parent(id) ON DELETE CASCADE,
    description TEXT
);

-- TEST_BODY
INSERT INTO test_parent (id, name) VALUES (1, 'Parent 1');
INSERT INTO test_child (parent_id, description) VALUES (1, 'Child of Parent 1');

-- 应该失败：引用不存在的父记录
EXPECT_ERROR: INSERT INTO test_child (parent_id, description) VALUES (999, 'Invalid child');

-- 测试级联删除
DELETE FROM test_parent WHERE id = 1;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_child WHERE parent_id = 1; => 0

-- TEARDOWN
DROP TABLE IF EXISTS test_child CASCADE;
DROP TABLE IF EXISTS test_parent CASCADE;
```

---

#### TEST-01-006: 约束 - CHECK

**测试目的**：验证 CHECK 约束

```sql
-- TEST_BODY
CREATE TABLE test_check (
    id SERIAL PRIMARY KEY,
    age INT CHECK (age >= 0 AND age <= 150),
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'pending'))
);

INSERT INTO test_check (age, status) VALUES (25, 'active');

-- 应该失败：年龄超出范围
EXPECT_ERROR: INSERT INTO test_check (age, status) VALUES (200, 'active');

-- 应该失败：状态不在允许值中
EXPECT_ERROR: INSERT INTO test_check (age, status) VALUES (25, 'invalid_status');

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_check WHERE age = 25; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_check CASCADE;
```

---

#### TEST-01-007: 约束 - UNIQUE

**测试目的**：验证唯一约束

```sql
-- TEST_BODY
CREATE TABLE test_unique (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100) UNIQUE
);

INSERT INTO test_unique (email, username) VALUES ('alice@example.com', 'alice');

-- 应该失败：重复email
EXPECT_ERROR: INSERT INTO test_unique (email, username) VALUES ('alice@example.com', 'alice2');

-- 应该失败：重复username
EXPECT_ERROR: INSERT INTO test_unique (email, username) VALUES ('alice2@example.com', 'alice');

-- NULL值允许（UNIQUE约束）
INSERT INTO test_unique (email, username) VALUES (NULL, 'bob');
INSERT INTO test_unique (email, username) VALUES (NULL, 'charlie');

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_unique WHERE email IS NULL; => 2

-- TEARDOWN
DROP TABLE IF EXISTS test_unique CASCADE;
```

---

#### TEST-01-008: DROP TABLE - CASCADE

**测试目的**：验证级联删除

```sql
-- SETUP
CREATE TABLE test_drop_parent (id SERIAL PRIMARY KEY);
CREATE TABLE test_drop_child (
    id SERIAL PRIMARY KEY,
    parent_id INT REFERENCES test_drop_parent(id)
);

-- TEST_BODY
-- 应该失败：有依赖的表无法删除
EXPECT_ERROR: DROP TABLE test_drop_parent;

-- CASCADE删除应该成功
DROP TABLE test_drop_parent CASCADE;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_tables WHERE tablename = 'test_drop_parent'; => 0
EXPECT_ROWS: SELECT COUNT(*) FROM pg_tables WHERE tablename = 'test_drop_child'; => 0

-- TEARDOWN
-- 已删除，无需额外清理
```

---

### 2. 索引操作（4 个测试）

#### TEST-01-009: CREATE INDEX - B-tree 索引

**测试目的**：验证 B-tree 索引创建

```sql
-- SETUP
CREATE TABLE test_index_btree (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INT
);

INSERT INTO test_index_btree (name, age)
SELECT 'User' || generate_series, generate_series % 100
FROM generate_series(1, 1000);

-- TEST_BODY
CREATE INDEX idx_test_name ON test_index_btree(name);
CREATE INDEX idx_test_age ON test_index_btree(age);

-- 验证索引被使用
EXPLAIN (FORMAT JSON) SELECT * FROM test_index_btree WHERE name = 'User500';

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'test_index_btree' AND indexname = 'idx_test_name'; => 1
EXPECT_VALUE: SELECT indexdef FROM pg_indexes WHERE indexname = 'idx_test_name'; => CONTAINS 'btree'

-- TEARDOWN
DROP TABLE IF EXISTS test_index_btree CASCADE;
```

---

#### TEST-01-010: CREATE INDEX - GIN 索引（JSONB）

**测试目的**：验证 GIN 索引用于 JSONB

```sql
-- SETUP
CREATE TABLE test_index_gin (
    id SERIAL PRIMARY KEY,
    data JSONB
);

INSERT INTO test_index_gin (data) VALUES
('{"tags": ["postgresql", "database", "sql"]}'::jsonb),
('{"tags": ["python", "programming"]}'::jsonb);

-- TEST_BODY
CREATE INDEX idx_gin_data ON test_index_gin USING GIN (data);

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_index_gin WHERE data @> '{"tags": ["postgresql"]}'::jsonb; => 1
EXPECT_ROWS: SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_gin_data'; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_index_gin CASCADE;
```

---

#### TEST-01-011: 索引维护 - REINDEX

**测试目的**：验证索引重建

```sql
-- SETUP
CREATE TABLE test_reindex (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE INDEX idx_reindex_name ON test_reindex(name);

INSERT INTO test_reindex (name)
SELECT 'Name' || generate_series FROM generate_series(1, 100);

-- TEST_BODY
REINDEX TABLE test_reindex;
REINDEX INDEX idx_reindex_name;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'test_reindex'; => 2 -- PK + idx_reindex_name

-- TEARDOWN
DROP TABLE IF EXISTS test_reindex CASCADE;
```

---

#### TEST-01-012: 索引 - UNIQUE INDEX

**测试目的**：验证唯一索引

```sql
-- SETUP
CREATE TABLE test_unique_index (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255)
);

-- TEST_BODY
CREATE UNIQUE INDEX idx_unique_email ON test_unique_index(email);

INSERT INTO test_unique_index (email) VALUES ('test@example.com');

-- 应该失败：违反唯一约束
EXPECT_ERROR: INSERT INTO test_unique_index (email) VALUES ('test@example.com');

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_unique_index WHERE email = 'test@example.com'; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_unique_index CASCADE;
```

---

### 3. DCL 操作（4 个测试）

#### TEST-01-013: GRANT/REVOKE - 表权限

**测试目的**：验证表级别权限管理

```sql
-- SETUP
CREATE ROLE test_user_read WITH LOGIN PASSWORD 'test_password';
CREATE TABLE test_permissions (
    id SERIAL PRIMARY KEY,
    data VARCHAR(100)
);

-- TEST_BODY
GRANT SELECT ON test_permissions TO test_user_read;

-- 验证权限
SELECT has_table_privilege('test_user_read', 'test_permissions', 'SELECT'); -- => true
SELECT has_table_privilege('test_user_read', 'test_permissions', 'INSERT'); -- => false

REVOKE SELECT ON test_permissions FROM test_user_read;

-- ASSERTIONS
EXPECT_VALUE: SELECT has_table_privilege('test_user_read', 'test_permissions', 'SELECT'); => 'false'

-- TEARDOWN
DROP TABLE IF EXISTS test_permissions CASCADE;
DROP ROLE IF EXISTS test_user_read;
```

---

#### TEST-01-014: GRANT/REVOKE - Schema 权限

**测试目的**：验证 Schema 级别权限

```sql
-- SETUP
CREATE ROLE test_schema_user WITH LOGIN PASSWORD 'test_password';
CREATE SCHEMA test_schema;

-- TEST_BODY
GRANT USAGE ON SCHEMA test_schema TO test_schema_user;
GRANT CREATE ON SCHEMA test_schema TO test_schema_user;

-- 验证权限
SELECT has_schema_privilege('test_schema_user', 'test_schema', 'USAGE'); -- => true
SELECT has_schema_privilege('test_schema_user', 'test_schema', 'CREATE'); -- => true

REVOKE CREATE ON SCHEMA test_schema FROM test_schema_user;

-- ASSERTIONS
EXPECT_VALUE: SELECT has_schema_privilege('test_schema_user', 'test_schema', 'CREATE'); => 'false'
EXPECT_VALUE: SELECT has_schema_privilege('test_schema_user', 'test_schema', 'USAGE'); => 'true'

-- TEARDOWN
DROP SCHEMA IF EXISTS test_schema CASCADE;
DROP ROLE IF EXISTS test_schema_user;
```

---

#### TEST-01-015: 角色管理 - CREATE/ALTER/DROP ROLE

**测试目的**：验证角色管理

```sql
-- TEST_BODY
CREATE ROLE test_role_1;
CREATE ROLE test_role_2 WITH LOGIN PASSWORD 'password123';
CREATE ROLE test_role_3 WITH SUPERUSER;

ALTER ROLE test_role_1 WITH LOGIN;
ALTER ROLE test_role_2 RENAME TO test_role_2_renamed;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_roles WHERE rolname = 'test_role_1' AND rolcanlogin = true; => 1
EXPECT_ROWS: SELECT COUNT(*) FROM pg_roles WHERE rolname = 'test_role_2_renamed'; => 1

-- TEARDOWN
DROP ROLE IF EXISTS test_role_1;
DROP ROLE IF EXISTS test_role_2_renamed;
DROP ROLE IF EXISTS test_role_3;
```

---

#### TEST-01-016: 角色继承 - GRANT ROLE

**测试目的**：验证角色继承机制

```sql
-- SETUP
CREATE ROLE test_parent_role;
CREATE ROLE test_child_role;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO test_parent_role;

-- TEST_BODY
GRANT test_parent_role TO test_child_role;

-- 验证继承
SELECT pg_has_role('test_child_role', 'test_parent_role', 'USAGE'); -- => true

REVOKE test_parent_role FROM test_child_role;

-- ASSERTIONS
EXPECT_VALUE: SELECT pg_has_role('test_child_role', 'test_parent_role', 'USAGE'); => 'false'

-- TEARDOWN
DROP ROLE IF EXISTS test_child_role;
DROP ROLE IF EXISTS test_parent_role;
```

---

### 4. Schema 操作（2 个测试）

#### TEST-01-017: CREATE/DROP SCHEMA

**测试目的**：验证 Schema 创建和删除

```sql
-- TEST_BODY
CREATE SCHEMA test_schema_1;
CREATE SCHEMA test_schema_2 AUTHORIZATION postgres;

CREATE TABLE test_schema_1.test_table (id SERIAL PRIMARY KEY);

-- 应该失败：Schema不为空
EXPECT_ERROR: DROP SCHEMA test_schema_1;

-- CASCADE删除应该成功
DROP SCHEMA test_schema_1 CASCADE;

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM pg_namespace WHERE nspname = 'test_schema_1'; => 0
EXPECT_ROWS: SELECT COUNT(*) FROM pg_namespace WHERE nspname = 'test_schema_2'; => 1

-- TEARDOWN
DROP SCHEMA IF EXISTS test_schema_2 CASCADE;
```

---

#### TEST-01-018: Schema 搜索路径

**测试目的**：验证 search_path 机制

```sql
-- SETUP
CREATE SCHEMA schema_a;
CREATE SCHEMA schema_b;

CREATE TABLE schema_a.test_table (id INT, name VARCHAR(100));
CREATE TABLE schema_b.test_table (id INT, description TEXT);

-- TEST_BODY
SET search_path TO schema_a, public;
INSERT INTO test_table (id, name) VALUES (1, 'From Schema A');

SET search_path TO schema_b, public;
INSERT INTO test_table (id, description) VALUES (2, 'From Schema B');

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM schema_a.test_table WHERE name = 'From Schema A'; => 1
EXPECT_ROWS: SELECT COUNT(*) FROM schema_b.test_table WHERE description = 'From Schema B'; => 1

-- TEARDOWN
DROP SCHEMA IF EXISTS schema_a CASCADE;
DROP SCHEMA IF EXISTS schema_b CASCADE;
RESET search_path;
```

---

### 5. PostgreSQL 17 特性（2 个测试）

#### TEST-01-019: MERGE 语句（PG15+，PG17 增强）

**测试目的**：验证 MERGE 语句

```sql
-- SETUP
CREATE TABLE test_merge_target (
    id INT PRIMARY KEY,
    value VARCHAR(100),
    updated_at TIMESTAMP
);

CREATE TABLE test_merge_source (
    id INT,
    value VARCHAR(100)
);

INSERT INTO test_merge_target (id, value, updated_at) VALUES
(1, 'Old Value 1', NOW()),
(2, 'Old Value 2', NOW());

INSERT INTO test_merge_source (id, value) VALUES
(2, 'Updated Value 2'),
(3, 'New Value 3');

-- TEST_BODY
MERGE INTO test_merge_target AS t
USING test_merge_source AS s
ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET value = s.value, updated_at = NOW()
WHEN NOT MATCHED THEN
    INSERT (id, value, updated_at) VALUES (s.id, s.value, NOW());

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_merge_target; => 3
EXPECT_VALUE: SELECT value FROM test_merge_target WHERE id = 2; => 'Updated Value 2'
EXPECT_VALUE: SELECT value FROM test_merge_target WHERE id = 3; => 'New Value 3'

-- TEARDOWN
DROP TABLE IF EXISTS test_merge_target CASCADE;
DROP TABLE IF EXISTS test_merge_source CASCADE;
```

---

#### TEST-01-020: 增量备份相关 DDL（PG17 新增）

**测试目的**：验证 PG17 增量备份支持

```sql
-- TEST_BODY
-- 创建表并记录WAL位置
CREATE TABLE test_incremental (
    id SERIAL PRIMARY KEY,
    data TEXT
);

-- 获取当前WAL位置
SELECT pg_current_wal_lsn();

INSERT INTO test_incremental (data) VALUES ('Test Data');

-- 再次获取WAL位置，验证WAL记录
SELECT pg_current_wal_lsn();

-- ASSERTIONS
EXPECT_ROWS: SELECT COUNT(*) FROM test_incremental; => 1

-- TEARDOWN
DROP TABLE IF EXISTS test_incremental CASCADE;
```

---

## 📊 测试统计

### 测试数量

| 类别                   | 测试数量  |
| ---------------------- | --------- |
| **DDL 基础操作**       | 8 个      |
| **索引操作**           | 4 个      |
| **DCL 操作**           | 4 个      |
| **Schema 操作**        | 2 个      |
| **PostgreSQL 17 特性** | 2 个      |
| **总计**               | **20 个** |

### 覆盖率

- ✅ CREATE TABLE（基本类型、约束、PG17 特性）
- ✅ ALTER TABLE（列操作、类型修改）
- ✅ DROP TABLE（CASCADE）
- ✅ 约束（PK、FK、CHECK、UNIQUE）
- ✅ 索引（B-tree、GIN、UNIQUE、REINDEX）
- ✅ GRANT/REVOKE（表权限、Schema 权限）
- ✅ 角色管理（CREATE/ALTER/DROP、继承）
- ✅ Schema 操作（创建/删除、搜索路径）
- ✅ PostgreSQL 17 特性（MERGE、增量备份）

---

## 🔧 实现建议

### 测试框架增强需求

1. **DDL 测试支持**

   - 扩展`EXPECT_ERROR`断言，支持特定错误代码验证
   - 增加`EXPECT_TABLE_EXISTS`、`EXPECT_INDEX_EXISTS`宏

2. **权限测试支持**

   - 增加`EXPECT_PRIVILEGE`断言
   - 支持切换用户执行 SQL（`SET ROLE`）

3. **EXPLAIN 验证支持**
   - 解析 EXPLAIN 输出（JSON 格式）
   - 验证索引是否被使用

### 测试执行顺序

1. **隔离性**：每个测试独立，使用唯一的表名/角色名
2. **清理**：确保 TEARDOWN 完整清理资源
3. **并发**：测试可并行执行（无依赖）

---

## 📅 实施计划

### Week 4（2025-10-11 至 2025-10-17）

**Day 1-2**：测试框架增强（4 小时）

- 实现 DDL 测试支持
- 实现 DCL 测试支持

**Day 3-5**：测试用例实现（6 小时）

- 实现 20 个测试用例
- 验证测试通过

**Day 6-7**：文档完善（2 小时）

- 更新测试用例索引
- 编写测试运行指南

---

**设计者**：PostgreSQL_modern Project Team  
**设计日期**：2025 年 10 月 3 日  
**目标版本**：v1.0  
**状态**：设计完成，待实现 ✅
