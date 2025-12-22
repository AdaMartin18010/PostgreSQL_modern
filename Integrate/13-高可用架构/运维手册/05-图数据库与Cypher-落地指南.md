---

> **📋 文档来源**: `PostgreSQL\06-运维实践\运维手册\05-图数据库与Cypher-落地指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 图数据库与 Cypher - 落地指南（Runbook）

> **文档版本**: v1.0
> **最后更新**: 2025-11-22
> **PostgreSQL版本**: 18.x (推荐) ⭐ | 17.x (推荐) | 16.x (兼容)
> 对齐：`../../04-高级特性/03.06-图数据库功能.md`

---

## 📋 目录

- [图数据库与 Cypher - 落地指南（Runbook）](#图数据库与-cypher---落地指南runbook)
  - [📋 目录](#-目录)
  - [1. 目标](#1-目标)
  - [2. 安装与启用](#2-安装与启用)
    - [2.1 Apache AGE安装](#21-apache-age安装)
    - [2.2 版本兼容性检查](#22-版本兼容性检查)
    - [2.3 启用扩展](#23-启用扩展)
    - [2.4 创建图](#24-创建图)
  - [3. 基础操作](#3-基础操作)
    - [3.1 创建节点和边](#31-创建节点和边)
    - [3.2 查询操作](#32-查询操作)
    - [3.3 图遍历查询](#33-图遍历查询)
    - [3.4 与SQL混合查询](#34-与sql混合查询)
  - [4. 运维要点](#4-运维要点)
    - [4.1 版本兼容性](#41-版本兼容性)
    - [4.2 ANALYZE与统计](#42-analyze与统计)
    - [4.3 性能优化](#43-性能优化)
    - [4.4 备份与恢复](#44-备份与恢复)
    - [4.5 监控与维护](#45-监控与维护)
    - [4.6 故障排查](#46-故障排查)
  - [5. 最佳实践](#5-最佳实践)

---

## 1. 目标

- 在 PostgreSQL 上快速搭建属性图能力（Apache AGE）并执行常见遍历与路径查询，支持与SQL混合。

## 2. 安装与启用

```sql
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SELECT * FROM create_graph('g');
```

### 2.1 Apache AGE安装

```bash
# 方法1: 从源码编译
git clone https://github.com/apache/age.git
cd age
make install

# 方法2: 使用预编译包（如果可用）
# 根据PostgreSQL版本选择对应的AGE版本

# 方法3: 使用Docker
docker pull apache/age:latest
```

### 2.2 版本兼容性检查

```sql
-- 检查PostgreSQL版本
SELECT version();

-- 检查AGE扩展是否可用
SELECT * FROM pg_available_extensions WHERE name = 'age';

-- 检查AGE版本
SELECT * FROM ag_catalog.ag_graph;
```

### 2.3 启用扩展

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS age;

-- 加载扩展
LOAD 'age';

-- 验证安装
SELECT * FROM ag_catalog.ag_graph;
```

### 2.4 创建图

```sql
-- 创建图
SELECT * FROM create_graph('social_network');

-- 列出所有图
SELECT * FROM ag_catalog.ag_graph;

-- 删除图（谨慎使用）
-- SELECT * FROM drop_graph('social_network', true);
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

### 3.1 创建节点和边

```sql
-- 创建单个节点
SELECT * FROM cypher('social_network', $$
  CREATE (u:User {
    id: 1,
    name: 'Alice',
    age: 30,
    email: 'alice@example.com'
  })
  RETURN u
$$) AS (u agtype);

-- 批量创建节点
SELECT * FROM cypher('social_network', $$
  CREATE
    (u1:User {id: 1, name: 'Alice'}),
    (u2:User {id: 2, name: 'Bob'}),
    (u3:User {id: 3, name: 'Charlie'})
  RETURN u1, u2, u3
$$) AS (u1 agtype, u2 agtype, u3 agtype);

-- 创建边
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {id: 1}), (b:User {id: 2})
  CREATE (a)-[r:FOLLOWS {
    since: '2024-01-01',
    strength: 0.8
  }]->(b)
  RETURN r
$$) AS (r agtype);

-- 创建路径（节点+边）
SELECT * FROM cypher('social_network', $$
  CREATE (a:User {id: 1})-[:FOLLOWS]->(b:User {id: 2})
  RETURN a, b
$$) AS (a agtype, b agtype);
```

### 3.2 查询操作

```sql
-- 查询所有节点
SELECT * FROM cypher('social_network', $$
  MATCH (n)
  RETURN n
  LIMIT 10
$$) AS (n agtype);

-- 查询特定类型的节点
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)
  WHERE u.age > 25
  RETURN u
  LIMIT 10
$$) AS (u agtype);

-- 查询边
SELECT * FROM cypher('social_network', $$
  MATCH ()-[r:FOLLOWS]->()
  RETURN r
  LIMIT 10
$$) AS (r agtype);

-- 查询路径
SELECT * FROM cypher('social_network', $$
  MATCH path = (a:User {id: 1})-[*1..3]->(b:User)
  RETURN path
  LIMIT 10
$$) AS (path agtype);
```

### 3.3 图遍历查询

```sql
-- k步可达（最短路径）
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {id: 1})-[*1..3]->(x:User)
  RETURN DISTINCT x
  LIMIT 10
$$) AS (x agtype);

-- 查找共同关注
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {id: 1})-[:FOLLOWS]->(common:User)<-[:FOLLOWS]-(b:User {id: 2})
  RETURN common
$$) AS (common agtype);

-- 查找影响力用户（入度最高）
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)<-[r:FOLLOWS]-()
  RETURN u, count(r) AS followers
  ORDER BY followers DESC
  LIMIT 10
$$) AS (u agtype, followers agtype);
```

### 3.4 与SQL混合查询

```sql
-- 将图查询结果转换为SQL表
WITH graph_data AS (
  SELECT * FROM cypher('social_network', $$
    MATCH (u:User)
    RETURN u.id AS user_id, u.name AS user_name, u.age AS user_age
    LIMIT 100
  $$) AS (user_id agtype, user_name agtype, user_age agtype)
)
SELECT
  (user_id::text)::integer AS id,
  user_name::text AS name,
  (user_age::text)::integer AS age
FROM graph_data
WHERE (user_age::text)::integer > 25;

-- 将SQL数据插入图
INSERT INTO users (id, name, age)
SELECT id, name, age FROM external_table;

-- 然后创建图节点
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)
  WHERE u.id IN [1, 2, 3]
  RETURN u
$$) AS (u agtype);
```

## 4. 运维要点

- 与PG版本兼容性；ANALYZE 与统计；
- 与传统SQL过滤结合，控制数据量与代价；
- 备份/恢复与图数据一致性。

### 4.1 版本兼容性

```sql
-- 检查PostgreSQL版本
SELECT version();

-- 检查AGE版本
SELECT extversion FROM pg_extension WHERE extname = 'age';

-- 检查兼容性
-- AGE 1.x 兼容 PostgreSQL 11-14
-- AGE 2.x 兼容 PostgreSQL 14-18
```

### 4.2 ANALYZE与统计

```sql
-- 分析图数据统计信息
ANALYZE;

-- 检查图统计信息
SELECT
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    last_analyze
FROM pg_stat_user_tables
WHERE schemaname LIKE 'ag_%';

-- 手动更新统计信息
ANALYZE VERBOSE;
```

### 4.3 性能优化

```sql
-- 1. 使用索引（在节点属性上）
-- AGE会自动在节点和边的属性上创建索引

-- 2. 限制查询范围
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {id: 1})-[*1..2]->(x:User)  -- 限制深度
  WHERE x.age > 25  -- 添加过滤条件
  RETURN x
  LIMIT 100  -- 限制结果数量
$$) AS (x agtype);

-- 3. 使用EXPLAIN分析查询计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)
  RETURN u
  LIMIT 10
$$) AS (u agtype);
```

### 4.4 备份与恢复

```sql
-- 1. 逻辑备份（使用pg_dump）
-- pg_dump会包含AGE扩展和图数据

-- 2. 检查图数据一致性
SELECT
    graph_name,
    COUNT(*) as node_count
FROM (
    SELECT * FROM cypher('social_network', $$
        MATCH (n)
        RETURN labels(n) as labels, count(*) as cnt
    $$) AS (labels agtype, cnt agtype)
) sub;

-- 3. 验证边的一致性
SELECT * FROM cypher('social_network', $$
    MATCH ()-[r]->()
    RETURN type(r) as edge_type, count(*) as count
$$) AS (edge_type agtype, count agtype);
```

### 4.5 监控与维护

```sql
-- 1. 监控图大小
SELECT
    pg_size_pretty(pg_total_relation_size('ag_catalog.ag_vertex')) AS vertex_size,
    pg_size_pretty(pg_total_relation_size('ag_catalog.ag_edge')) AS edge_size;

-- 2. 监控查询性能
SELECT
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE query LIKE '%cypher%'
ORDER BY total_exec_time DESC
LIMIT 10;

-- 3. 检查死元组
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup
FROM pg_stat_user_tables
WHERE schemaname LIKE 'ag_%'
AND n_dead_tup > 1000;
```

### 4.6 故障排查

**问题1: 查询性能慢**:

```sql
-- 检查查询计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {id: 1})-[*1..5]->(x:User)
  RETURN x
$$) AS (x agtype);

-- 解决方案：
-- 1. 限制路径深度
-- 2. 添加WHERE过滤条件
-- 3. 使用LIMIT限制结果
-- 4. 确保统计信息最新（ANALYZE）
```

**问题2: 内存不足**:

```sql
-- 检查work_mem
SHOW work_mem;

-- 解决方案：增加work_mem或减少查询复杂度
SET work_mem = '256MB';
```

**问题3: 图数据不一致**:

```sql
-- 检查孤立节点（没有边的节点）
SELECT * FROM cypher('social_network', $$
  MATCH (n)
  WHERE NOT (n)--() AND NOT ()--(n)
  RETURN n
  LIMIT 10
$$) AS (n agtype);

-- 检查悬空边（指向不存在的节点）
-- 这通常不会发生，因为AGE维护引用完整性
```

## 5. 最佳实践

1. **图设计**: 合理设计节点和边的类型，避免过度复杂的图结构
2. **查询优化**: 始终限制路径深度和结果数量，使用WHERE过滤
3. **混合使用**: 结合SQL和图查询，利用各自的优势
4. **定期维护**: 定期ANALYZE，监控图大小和查询性能
5. **版本管理**: 确保AGE版本与PostgreSQL版本兼容
