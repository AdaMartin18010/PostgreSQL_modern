# 01_sql_ddl_dcl

## 主题边界

- SQL 语言基础与进阶：数据定义（DDL）、数据操纵（DML）、数据控制（DCL）、事务控制（TCL）
- 标准对齐：SQL 标准（优先参考 PostgreSQL 实现与文档差异）
  
## 核心要点

- 模式与对象：`SCHEMA`、`TABLE`、`VIEW`、`SEQUENCE`、`INDEX`、`TYPE`
- DDL：`CREATE/ALTER/DROP`，分区表、约束、默认值、生成列
- DML：`SELECT/INSERT/UPDATE/DELETE/MERGE`，`RETURNING`，CTE（`WITH`）
- DCL：`GRANT/REVOKE`，角色与权限模型
- TCL：`BEGIN/COMMIT/ROLLBACK/SAVEPOINT`，`SET TRANSACTION`
- SQL:2023 相关：数值字面量下划线、非十进制整数字面量、`ANY_VALUE` 等（以官方实现为准）

## 知识地图

- 语言元素 → 数据模型与约束 → 查询优化（计划/统计）→ 安全与权限
- 常见陷阱：隐式类型转换、大小写/标识符、时区/日期、NULL 语义、索引失效场景

## 权威参考

- PostgreSQL 文档（SQL 命令）：`https://www.postgresql.org/docs/current/sql-commands.html`
- SQL 语法参考：`https://www.postgresql.org/docs/current/sql-syntax.html`

## Checklist（执行前/提交前）
- 表/索引/约束命名规范一致，避免大小写混用与未加引号的歧义
- 所有 DDL 评审：是否需要并发索引（`CREATE INDEX CONCURRENTLY`）与锁影响评估
- 大批量 DML：是否分批、是否使用 `RETURNING`/CTE、是否需要禁用触发器/外键后再回填
- 权限最小化：按角色授予最小权限，避免使用超级用户
- 事务边界明确：TCL 使用清晰，避免隐式提交/自动提交带来的半成品状态

## 最小可复现脚本（psql）
```sql
-- DDL 与 DML 基本流程
CREATE SCHEMA IF NOT EXISTS demo;
CREATE TABLE IF NOT EXISTS demo.users (
  id bigserial PRIMARY KEY,
  name text NOT NULL,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_name ON demo.users (name);

BEGIN;
INSERT INTO demo.users(name) VALUES ('alice') RETURNING id;
COMMIT;

-- 权限示例
CREATE ROLE app_rw LOGIN PASSWORD 'secret';
GRANT USAGE ON SCHEMA demo TO app_rw;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA demo TO app_rw;
```
