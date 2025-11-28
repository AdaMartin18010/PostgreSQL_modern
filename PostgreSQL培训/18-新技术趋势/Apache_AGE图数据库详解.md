# Apache AGE 图数据库详解

> **更新时间**: 2025 年 1 月
> **技术版本**: PostgreSQL 17+ with Apache AGE 1.5+
> **文档编号**: 03-03-TREND-09

## 📑 概述

Apache AGE 是 PostgreSQL 的图数据库扩展，为 PostgreSQL 添加了图数据存储和查询能力。
它支持 Cypher 查询语言，提供了强大的图分析功能，适用于知识图谱、社交网络、推荐系统等场景。

## 🎯 核心价值

- **Cypher 查询语言**：直观的图查询语法
- **图数据模型**：节点和关系的灵活建模
- **图算法**：内置图算法支持
- **完整 SQL**：与 PostgreSQL SQL 无缝集成
- **高性能**：基于 PostgreSQL 的高性能图查询

## 📚 目录

- [Apache AGE 图数据库详解](#apache-age-图数据库详解)
  - [📑 概述](#-概述)
  - [🎯 核心价值](#-核心价值)
  - [📚 目录](#-目录)
  - [1. Apache AGE 基础](#1-apache-age-基础)
    - [1.1 什么是 Apache AGE](#11-什么是-apache-age)
    - [1.2 安装 Apache AGE](#12-安装-apache-age)
    - [1.3 版本要求](#13-版本要求)
  - [2. 图数据模型](#2-图数据模型)
    - [2.1 图的基本概念](#21-图的基本概念)
    - [2.2 创建图](#22-创建图)
    - [2.3 创建节点](#23-创建节点)
    - [2.4 创建关系](#24-创建关系)
  - [3. Cypher 查询语言](#3-cypher-查询语言)
    - [3.1 基本查询](#31-基本查询)
    - [3.2 关系查询](#32-关系查询)
    - [3.3 聚合查询](#33-聚合查询)
    - [3.4 复杂查询](#34-复杂查询)
  - [4. 图算法](#4-图算法)
    - [4.1 最短路径算法](#41-最短路径算法)
    - [4.2 社区检测](#42-社区检测)
    - [4.3 中心性分析](#43-中心性分析)
  - [5. 性能优化](#5-性能优化)
    - [5.1 索引优化](#51-索引优化)
    - [5.2 查询优化](#52-查询优化)
    - [5.3 批量操作](#53-批量操作)
  - [6. 实际案例](#6-实际案例)
    - [6.1 案例：社交网络分析](#61-案例社交网络分析)
    - [6.2 案例：知识图谱](#62-案例知识图谱)
  - [📊 总结](#-总结)

---

## 1. Apache AGE 基础

### 1.1 什么是 Apache AGE

Apache AGE 是 PostgreSQL 的扩展，为 PostgreSQL 添加了图数据库功能，支持 Cypher 查询语言。

### 1.2 安装 Apache AGE

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS age;

-- 加载 AGE
LOAD 'age';

-- 验证安装
SELECT * FROM pg_extension WHERE extname = 'age';
```

### 1.3 版本要求

- PostgreSQL 12+
- 推荐 PostgreSQL 17+ 以获得最佳性能
- Apache AGE 1.5+（最新版本）

---

## 2. 图数据模型

### 2.1 图的基本概念

图由节点（Node）和关系（Relationship）组成：

- **节点**：实体，可以有标签和属性
- **关系**：连接节点的边，有类型和方向
- **标签**：节点的分类
- **属性**：节点和关系的键值对

### 2.2 创建图

```sql
-- 创建图
SELECT create_graph('social_network');

-- 查看所有图
SELECT * FROM ag_catalog.ag_graph;

-- 删除图
SELECT drop_graph('social_network', true);
```

### 2.3 创建节点

```sql
-- 使用 Cypher 创建节点
SELECT * FROM cypher('social_network', $$
    CREATE (u:User {
        id: 1,
        name: 'Alice',
        age: 30,
        email: 'alice@example.com'
    })
    RETURN u
$$) AS (u agtype);

-- 创建多个节点
SELECT * FROM cypher('social_network', $$
    CREATE
        (u1:User {id: 1, name: 'Alice'}),
        (u2:User {id: 2, name: 'Bob'}),
        (u3:User {id: 3, name: 'Charlie'})
    RETURN u1, u2, u3
$$) AS (u1 agtype, u2 agtype, u3 agtype);
```

### 2.4 创建关系

```sql
-- 创建关系
SELECT * FROM cypher('social_network', $$
    MATCH (u1:User {id: 1}), (u2:User {id: 2})
    CREATE (u1)-[r:FOLLOWS {since: '2024-01-01'}]->(u2)
    RETURN r
$$) AS (r agtype);

-- 创建双向关系
SELECT * FROM cypher('social_network', $$
    MATCH (u1:User {id: 1}), (u2:User {id: 2})
    CREATE (u1)-[r:FRIENDS {since: '2024-01-01'}]-(u2)
    RETURN r
$$) AS (r agtype);
```

---

## 3. Cypher 查询语言

### 3.1 基本查询

```sql
-- 查询所有节点
SELECT * FROM cypher('social_network', $$
    MATCH (n)
    RETURN n
    LIMIT 10
$$) AS (n agtype);

-- 查询特定标签的节点
SELECT * FROM cypher('social_network', $$
    MATCH (u:User)
    RETURN u
$$) AS (u agtype);

-- 查询节点的属性
SELECT * FROM cypher('social_network', $$
    MATCH (u:User {id: 1})
    RETURN u.name, u.age, u.email
$$) AS (name agtype, age agtype, email agtype);
```

### 3.2 关系查询

```sql
-- 查询关系
SELECT * FROM cypher('social_network', $$
    MATCH (u1:User)-[r:FOLLOWS]->(u2:User)
    RETURN u1.name, r.since, u2.name
$$) AS (from agtype, since agtype, to agtype);

-- 查询路径
SELECT * FROM cypher('social_network', $$
    MATCH path = (u1:User)-[:FOLLOWS*1..3]->(u2:User)
    WHERE u1.id = 1 AND u2.id = 3
    RETURN path
$$) AS (path agtype);

-- 查询最短路径
SELECT * FROM cypher('social_network', $$
    MATCH path = shortestPath(
        (u1:User {id: 1})-[*]-(u2:User {id: 3})
    )
    RETURN path
$$) AS (path agtype);
```

### 3.3 聚合查询

```sql
-- 统计节点的度（连接数）
SELECT * FROM cypher('social_network', $$
    MATCH (u:User)-[r]-()
    RETURN u.name, count(r) AS degree
    ORDER BY degree DESC
$$) AS (name agtype, degree agtype);

-- 分组聚合
SELECT * FROM cypher('social_network', $$
    MATCH (u:User)-[r:FOLLOWS]->()
    RETURN u.name, count(r) AS following_count
    ORDER BY following_count DESC
$$) AS (name agtype, count agtype);
```

### 3.4 复杂查询

```sql
-- 查找共同关注
SELECT * FROM cypher('social_network', $$
    MATCH (u1:User {id: 1})-[:FOLLOWS]->(common)<-[:FOLLOWS]-(u2:User {id: 2})
    RETURN common.name AS common_following
$$) AS (name agtype);

-- 查找推荐用户（朋友的朋友）
SELECT * FROM cypher('social_network', $$
    MATCH (u1:User {id: 1})-[:FRIENDS]->(friend)-[:FRIENDS]->(recommended)
    WHERE u1 <> recommended
      AND NOT (u1)-[:FRIENDS]-(recommended)
    RETURN recommended.name, count(*) AS mutual_friends
    ORDER BY mutual_friends DESC
    LIMIT 10
$$) AS (name agtype, count agtype);
```

---

## 4. 图算法

### 4.1 最短路径算法

```sql
-- 使用 shortestPath 函数
SELECT * FROM cypher('social_network', $$
    MATCH path = shortestPath(
        (start:User {id: 1})-[*]-(end:User {id: 5})
    )
    RETURN path, length(path) AS path_length
$$) AS (path agtype, length agtype);
```

### 4.2 社区检测

```sql
-- 查找紧密连接的社区
SELECT * FROM cypher('social_network', $$
    MATCH (u1:User)-[:FRIENDS]-(u2:User)
    WHERE u1.id < u2.id
    RETURN u1.name, u2.name
    ORDER BY u1.name, u2.name
$$) AS (u1 agtype, u2 agtype);
```

### 4.3 中心性分析

```sql
-- 计算节点的度中心性
SELECT * FROM cypher('social_network', $$
    MATCH (u:User)
    OPTIONAL MATCH (u)-[r]-()
    RETURN u.name, count(r) AS degree_centrality
    ORDER BY degree_centrality DESC
$$) AS (name agtype, centrality agtype);
```

---

## 5. 性能优化

### 5.1 索引优化

```sql
-- 在节点属性上创建索引（使用 PostgreSQL 索引）
CREATE INDEX idx_user_id ON social_network."User" USING btree ((properties->>'id'));

-- 在关系属性上创建索引
CREATE INDEX idx_follows_since ON social_network."FOLLOWS" USING btree ((properties->>'since'));
```

### 5.2 查询优化

```sql
-- 使用 WHERE 子句过滤
SELECT * FROM cypher('social_network', $$
    MATCH (u:User)
    WHERE u.age > 25 AND u.age < 35
    RETURN u
$$) AS (u agtype);

-- 限制结果集
SELECT * FROM cypher('social_network', $$
    MATCH (u:User)
    RETURN u
    LIMIT 100
$$) AS (u agtype);

-- 使用投影减少数据传输
SELECT * FROM cypher('social_network', $$
    MATCH (u:User)
    RETURN u.id, u.name
    LIMIT 100
$$) AS (id agtype, name agtype);
```

### 5.3 批量操作

```sql
-- 批量创建节点
SELECT * FROM cypher('social_network', $$
    UNWIND $users AS user
    CREATE (u:User {
        id: user.id,
        name: user.name,
        age: user.age
    })
    RETURN u
$$, '{"users": [{"id": 1, "name": "Alice", "age": 30}, {"id": 2, "name": "Bob", "age": 25}]}') AS (u agtype);
```

---

## 6. 实际案例

### 6.1 案例：社交网络分析

```sql
-- 场景：社交网络用户关系分析
-- 要求：查找用户关系、推荐好友、社区检测

-- 创建图
SELECT create_graph('social_network');

-- 创建用户节点
SELECT * FROM cypher('social_network', $$
    CREATE
        (u1:User {id: 1, name: 'Alice'}),
        (u2:User {id: 2, name: 'Bob'}),
        (u3:User {id: 3, name: 'Charlie'}),
        (u4:User {id: 4, name: 'David'}),
        (u5:User {id: 5, name: 'Eve'})
    RETURN count(*) AS created
$$) AS (count agtype);

-- 创建关系
SELECT * FROM cypher('social_network', $$
    MATCH (u1:User {id: 1}), (u2:User {id: 2}),
          (u2:User {id: 2}), (u3:User {id: 3}),
          (u3:User {id: 3}), (u4:User {id: 4}),
          (u1:User {id: 1}), (u5:User {id: 5})
    CREATE
        (u1)-[:FRIENDS]->(u2),
        (u2)-[:FRIENDS]->(u3),
        (u3)-[:FRIENDS]->(u4),
        (u1)-[:FRIENDS]->(u5)
    RETURN count(*) AS created
$$) AS (count agtype);

-- 查找用户的朋友
SELECT * FROM cypher('social_network', $$
    MATCH (u:User {id: 1})-[:FRIENDS]->(friend)
    RETURN friend.name AS friend_name
$$) AS (name agtype);

-- 查找推荐好友（朋友的朋友）
SELECT * FROM cypher('social_network', $$
    MATCH (u:User {id: 1})-[:FRIENDS]->(friend)-[:FRIENDS]->(recommended)
    WHERE u <> recommended
      AND NOT (u)-[:FRIENDS]-(recommended)
    RETURN recommended.name AS recommended_friend,
           count(*) AS mutual_friends
    ORDER BY mutual_friends DESC
$$) AS (name agtype, count agtype);
```

### 6.2 案例：知识图谱

```sql
-- 场景：构建知识图谱
-- 要求：实体关系抽取、知识查询、推理

-- 创建图
SELECT create_graph('knowledge_graph');

-- 创建实体和关系
SELECT * FROM cypher('knowledge_graph', $$
    CREATE
        (p1:Person {name: 'Albert Einstein', born: 1879}),
        (p2:Person {name: 'Isaac Newton', born: 1643}),
        (t1:Topic {name: 'Physics'}),
        (t2:Topic {name: 'Relativity'}),
        (t3:Topic {name: 'Gravity'}),
        (p1)-[:STUDIED {year: 1905}]->(t2),
        (p1)-[:INTERESTED_IN]->(t1),
        (p2)-[:DISCOVERED {year: 1687}]->(t3),
        (p2)-[:INTERESTED_IN]->(t1),
        (t2)-[:RELATED_TO]->(t1),
        (t3)-[:RELATED_TO]->(t1)
    RETURN count(*) AS created
$$) AS (count agtype);

-- 查询相关实体
SELECT * FROM cypher('knowledge_graph', $$
    MATCH (p:Person)-[:INTERESTED_IN]->(t:Topic)
    RETURN p.name, t.name
$$) AS (person agtype, topic agtype);

-- 查找实体间的路径
SELECT * FROM cypher('knowledge_graph', $$
    MATCH path = (p1:Person {name: 'Albert Einstein'})-[*]-(p2:Person {name: 'Isaac Newton'})
    RETURN path
$$) AS (path agtype);
```

---

## 📊 总结

Apache AGE 为 PostgreSQL 提供了强大的图数据库能力，通过 Cypher 查询语言可以直观地查询和分析图数据。
它特别适合知识图谱、社交网络、推荐系统等图数据应用场景，在保持 PostgreSQL 完整功能的同时，提供了高效的图数据存储和查询能力。

## 📚 参考资料

### 官方文档

- [Apache AGE 官方文档](https://age.apache.org/)
- [Apache AGE GitHub](https://github.com/apache/age)
- [Cypher 查询语言规范](https://neo4j.com/docs/cypher-manual/current/)
- [PostgreSQL 官方文档 - 扩展](https://www.postgresql.org/docs/current/extend.html)

### 技术论文

- [Graph Databases: A Survey](https://www.vldb.org/pvldb/vol15/p2658-neumann.pdf) - 图数据库研究综述
- [The Property Graph Database Model](https://neo4j.com/whitepapers/property-graph-model/) - 属性图数据库模型
- [Cypher: An Evolving Query Language for Property Graphs](https://dl.acm.org/doi/10.1145/3183713.3190657) - Cypher 查询语言演进

### 技术博客

- [Apache AGE 官方博客](https://age.apache.org/blog/) - Apache AGE 最新动态
- [Understanding Graph Databases](https://neo4j.com/developer/graph-database/) - 图数据库详解
- [PostgreSQL Graph Database Best Practices](https://age.apache.org/docs/) - PostgreSQL 图数据库最佳实践

### 社区资源

- [Apache AGE Wiki](https://github.com/apache/age/wiki) - Apache AGE 相关 Wiki
- [PostgreSQL Mailing Lists](https://www.postgresql.org/list/) - PostgreSQL 邮件列表讨论
- [Stack Overflow - Apache AGE](https://stackoverflow.com/questions/tagged/apache-age) - Stack Overflow 相关问题

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
**文档编号**: 03-03-TREND-09
