# 图数据库与 Cypher - 落地指南（Runbook）

对齐：`03-高级特性/03.06-图数据库功能.md`

## 1. 目标

- 在 PostgreSQL 上快速搭建属性图能力（Apache AGE）并执行常见遍历与路径查询，支持与SQL混合。

## 2. 安装与启用

```sql
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SELECT * FROM create_graph('g');
```

## 3. 基础操作

```sql
-- 创建点与边
SELECT * FROM cypher('g', $$
  CREATE (a:User {id:1})-[:FOLLOWS]->(b:User {id:2})
$$) as (v agtype);

-- k步可达
SELECT * FROM cypher('g', $$
  MATCH (a:User {id:1})-[:FOLLOWS*1..3]->(x)
  RETURN x LIMIT 10
$$) as (x agtype);
```

## 4. 运维要点

- 与PG版本兼容性；ANALYZE 与统计；
- 与传统SQL过滤结合，控制数据量与代价；
- 备份/恢复与图数据一致性。
