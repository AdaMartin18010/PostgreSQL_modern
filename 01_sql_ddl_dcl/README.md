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
