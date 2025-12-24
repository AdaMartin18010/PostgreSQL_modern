---

> **📋 文档来源**: `PostgreSQL培训\12-扩展开发\【深入】Apache AGE图数据库完整实战指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 【深入】Apache AGE图数据库完整实战指南

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 11+, Apache AGE 1.5+
> **难度等级**: ⭐⭐⭐⭐ 高级 | **预计学习时间**: 8-10小时

---

## 📋 目录

- [【深入】Apache AGE图数据库完整实战指南](#深入apache-age图数据库完整实战指南)
  - [📋 目录](#-目录)
  - [1. 课程概述](#1-课程概述)
    - [1.1 什么是Apache AGE？](#11-什么是apache-age)
      - [核心特性](#核心特性)
      - [适用场景](#适用场景)
    - [1.2 为什么选择AGE？](#12-为什么选择age)
  - [2. 图数据库基础理论](#2-图数据库基础理论)
    - [2.1 属性图模型](#21-属性图模型)
      - [核心概念](#核心概念)
      - [示例：社交网络](#示例社交网络)
    - [2.2 图遍历算法](#22-图遍历算法)
      - [基本遍历](#基本遍历)
      - [高级算法](#高级算法)
  - [3. Apache AGE架构深入](#3-apache-age架构深入)
    - [3.1 系统架构](#31-系统架构)
    - [3.2 数据存储结构](#32-数据存储结构)
      - [图数据在PostgreSQL中的表示](#图数据在postgresql中的表示)
      - [图ID编码](#图id编码)
    - [3.3 查询执行流程](#33-查询执行流程)
  - [4. 安装与环境配置](#4-安装与环境配置)
    - [4.1 编译安装](#41-编译安装)
      - [前置条件](#前置条件)
      - [编译AGE](#编译age)
    - [4.2 配置数据库](#42-配置数据库)
    - [4.3 Docker快速部署](#43-docker快速部署)
  - [5. Cypher查询语言](#5-cypher查询语言)
    - [5.1 基础语法](#51-基础语法)
      - [CREATE - 创建节点和边](#create---创建节点和边)
      - [MATCH - 查询模式](#match---查询模式)
      - [WHERE - 过滤条件](#where---过滤条件)
    - [5.2 高级查询](#52-高级查询)
      - [聚合函数](#聚合函数)
      - [子查询与UNION](#子查询与union)
      - [OPTIONAL MATCH（左外连接）](#optional-match左外连接)
    - [5.3 更新与删除](#53-更新与删除)
      - [SET - 更新属性](#set---更新属性)
      - [REMOVE - 删除属性和标签](#remove---删除属性和标签)
      - [DELETE - 删除节点和边](#delete---删除节点和边)
      - [MERGE - 创建或更新](#merge---创建或更新)
  - [6. 图建模实战](#6-图建模实战)
    - [6.1 社交网络模型](#61-社交网络模型)
      - [数据模型设计](#数据模型设计)
      - [实现代码](#实现代码)
    - [6.2 推荐系统模型](#62-推荐系统模型)
      - [协同过滤推荐](#协同过滤推荐)
    - [6.3 知识图谱模型](#63-知识图谱模型)
      - [实体-关系-属性模型](#实体-关系-属性模型)
  - [7. 高级图算法](#7-高级图算法)
    - [7.1 最短路径算法](#71-最短路径算法)
      - [单源最短路径](#单源最短路径)
      - [Dijkstra算法（带权重）](#dijkstra算法带权重)
    - [7.2 中心性分析](#72-中心性分析)
      - [度中心性（Degree Centrality）](#度中心性degree-centrality)
      - [接近中心性（Closeness Centrality）](#接近中心性closeness-centrality)
      - [中介中心性（Betweenness Centrality）](#中介中心性betweenness-centrality)
    - [7.3 社区发现](#73-社区发现)
      - [简单社区检测（基于连通分量）](#简单社区检测基于连通分量)
      - [三角形计数（聚类系数）](#三角形计数聚类系数)
    - [7.4 PageRank算法](#74-pagerank算法)
      - [简化实现](#简化实现)
  - [8. 性能优化](#8-性能优化)
    - [8.1 索引策略](#81-索引策略)
      - [创建索引](#创建索引)
      - [索引使用建议](#索引使用建议)
    - [8.2 查询优化](#82-查询优化)
      - [EXPLAIN分析](#explain分析)
      - [优化技巧](#优化技巧)
    - [8.3 批量操作优化](#83-批量操作优化)
      - [批量导入](#批量导入)
      - [批量更新](#批量更新)
    - [8.4 监控与调优](#84-监控与调优)
      - [性能监控查询](#性能监控查询)
      - [配置优化](#配置优化)
  - [9. 生产实战案例](#9-生产实战案例)
    - [9.1 案例1：欺诈检测系统](#91-案例1欺诈检测系统)
      - [业务场景](#业务场景)
      - [数据模型](#数据模型)
      - [欺诈检测查询](#欺诈检测查询)
    - [9.2 案例2：社交推荐引擎](#92-案例2社交推荐引擎)
      - [好友推荐算法](#好友推荐算法)
    - [9.3 案例3：供应链分析](#93-案例3供应链分析)
      - [供应链影响分析](#供应链影响分析)
  - [10. 与Neo4j对比](#10-与neo4j对比)
    - [10.1 功能对比](#101-功能对比)
    - [10.2 语法差异](#102-语法差异)
      - [AGE特有语法](#age特有语法)
      - [混合查询](#混合查询)
    - [10.3 迁移指南](#103-迁移指南)
      - [从Neo4j迁移到AGE](#从neo4j迁移到age)
  - [11. 最佳实践](#11-最佳实践)
    - [11.1 设计原则](#111-设计原则)
      - [1. 图建模最佳实践](#1-图建模最佳实践)
      - [2. 性能考虑](#2-性能考虑)
    - [11.2 安全建议](#112-安全建议)
      - [权限控制](#权限控制)
      - [SQL注入防护](#sql注入防护)
    - [11.3 运维建议](#113-运维建议)
      - [备份策略](#备份策略)
      - [监控指标](#监控指标)
  - [12. FAQ与疑难解答](#12-faq与疑难解答)
    - [Q1: AGE性能不如Neo4j怎么办？](#q1-age性能不如neo4j怎么办)
    - [Q2: 如何处理大图数据导入？](#q2-如何处理大图数据导入)
    - [Q3: AGE支持图算法库吗？](#q3-age支持图算法库吗)
    - [Q4: 如何调试慢查询？](#q4-如何调试慢查询)
    - [Q5: AGE可以与其他PostgreSQL扩展一起使用吗？](#q5-age可以与其他postgresql扩展一起使用吗)
  - [📚 延伸阅读](#-延伸阅读)
    - [官方资源](#官方资源)
    - [推荐书籍](#推荐书籍)
    - [相关技术](#相关技术)
  - [✅ 学习检查清单](#-学习检查清单)
  - [💡 下一步学习](#-下一步学习)

1. [图数据库基础理论](#2-图数据库基础理论)
2. [Apache AGE架构深入](#3-apache-age架构深入)
3. [安装与环境配置](#4-安装与环境配置)
4. [Cypher查询语言](#5-cypher查询语言)
5. [图建模实战](#6-图建模实战)
6. [高级图算法](#7-高级图算法)
7. [性能优化](#8-性能优化)
8. [生产实战案例](#9-生产实战案例)
9. [与Neo4j对比](#10-与neo4j对比)
10. [最佳实践](#11-最佳实践)
11. [FAQ与疑难解答](#12-faq与疑难解答)

---

## 1. 课程概述

### 1.1 什么是Apache AGE？

**Apache AGE (A Graph Extension)** 是PostgreSQL的图数据库扩展，让PostgreSQL支持属性图模型和Cypher查询语言。

#### 核心特性

| 特性 | 说明 | 优势 |
|------|------|------|
| **兼容PostgreSQL** | 作为扩展运行 | 无需迁移数据，使用现有基础设施 |
| **Cypher支持** | 兼容openCypher标准 | 与Neo4j查询语法兼容 |
| **混合查询** | SQL + Cypher混合 | 关系数据+图数据统一查询 |
| **ACID保证** | 完整事务支持 | 数据一致性保证 |
| **开源免费** | Apache 2.0许可 | 无许可费用 |

#### 适用场景

- 社交网络分析
- 知识图谱
- 推荐系统
- 欺诈检测
- 网络拓扑分析
- 供应链管理

### 1.2 为什么选择AGE？

```text
传统关系数据库 vs 图数据库：

关系数据库查询"朋友的朋友"：
SELECT f2.name
FROM friends f1
JOIN friends f2 ON f1.friend_id = f2.user_id
WHERE f1.user_id = 123;

图数据库查询：
MATCH (u:User {id: 123})-[:FRIEND]->(:User)-[:FRIEND]->(friend)
RETURN friend.name;
```

**性能对比**：

- 2度关系：图数据库快10倍
- 3度关系：图数据库快100倍
- 4度关系：图数据库快1000倍

---

## 2. 图数据库基础理论

### 2.1 属性图模型

#### 核心概念

```text
属性图 = 节点(Vertex) + 边(Edge) + 属性(Property)

┌──────────────┐
│   节点(Node) │
├──────────────┤
│ - 标签(Label) │
│ - 属性键值对  │
└──────────────┘
       │
       │ ┌──────────────┐
       └─│   边(Edge)   │
         ├──────────────┤
         │ - 类型(Type)  │
         │ - 方向(Dir)   │
         │ - 属性键值对  │
         └──────────────┘
```

#### 示例：社交网络

```cypher
-- 节点示例
(alice:Person {name: 'Alice', age: 30, city: 'Beijing'})
(bob:Person {name: 'Bob', age: 25, city: 'Shanghai'})
(post:Post {title: 'Hello World', created: '2025-01-01'})

-- 边示例
(alice)-[:FRIEND {since: '2020-01-01'}]->(bob)
(alice)-[:CREATED {timestamp: '2025-01-01'}]->(post)
(bob)-[:LIKED {timestamp: '2025-01-02'}]->(post)
```

### 2.2 图遍历算法

#### 基本遍历

| 算法 | 特点 | 应用场景 |
|------|------|----------|
| **广度优先(BFS)** | 逐层遍历 | 最短路径、社交距离 |
| **深度优先(DFS)** | 深入探索 | 路径发现、循环检测 |
| **双向搜索** | 从两端同时搜索 | 大图最短路径 |

#### 高级算法

- **PageRank**: 节点重要性排名
- **社区发现**: Louvain、Label Propagation
- **中心性分析**: Betweenness、Closeness、Degree
- **路径分析**: 所有路径、最短路径、K-最短路径

---

## 3. Apache AGE架构深入

### 3.1 系统架构

```text
┌─────────────────────────────────────────┐
│         应用层 (Application)             │
│  SQL Client / Cypher Client / ORM       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Apache AGE Extension            │
├─────────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ Cypher Parser│  │ Graph Operators │ │
│  └──────────────┘  └─────────────────┘ │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ Query Planner│  │ Index Manager   │ │
│  └──────────────┘  └─────────────────┘ │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         PostgreSQL Core                 │
│  Storage / Transaction / Lock / WAL     │
└─────────────────────────────────────────┘
```

### 3.2 数据存储结构

#### 图数据在PostgreSQL中的表示

```sql
-- 内部存储结构（简化版）
CREATE TABLE ag_label._ag_label_vertex (
    id graphid PRIMARY KEY,
    properties jsonb
);

CREATE TABLE ag_label._ag_label_edge (
    id graphid PRIMARY KEY,
    start_id graphid NOT NULL,
    end_id graphid NOT NULL,
    properties jsonb
);

-- graphid是特殊的int8类型
-- 高16位：label_id
-- 低48位：entry_id
```

#### 图ID编码

```text
GraphID (64位)
┌────────────────┬──────────────────────────────────┐
│  Label ID (16) │     Entry ID (48)                │
└────────────────┴──────────────────────────────────┘
     标签标识              实体标识

示例：
Label ID: 1 (Person)
Entry ID: 100
GraphID: 281474976710756 (0x0001000000000064)
```

### 3.3 查询执行流程

```text
Cypher查询 → 解析器 → AST → 查询计划 → PostgreSQL执行器

示例：
MATCH (a:Person)-[:FRIEND]->(b:Person)
WHERE a.age > 25
RETURN b.name

↓ 转换为

SELECT get_property(v2.properties, 'name')
FROM Person_vertex v1
JOIN Friend_edge e ON e.start_id = v1.id
JOIN Person_vertex v2 ON e.end_id = v2.id
WHERE get_property(v1.properties, 'age')::int > 25;
```

---

## 4. 安装与环境配置

### 4.1 编译安装

#### 前置条件

```bash
# CentOS/RHEL
sudo yum install -y gcc make postgresql-devel flex bison

# Ubuntu/Debian
sudo apt-get install -y build-essential postgresql-server-dev-all flex bison

# 检查PostgreSQL版本
psql --version  # 需要 11+
```

#### 编译AGE

```bash
# 1. 克隆代码
git clone https://github.com/apache/age.git
cd age

# 2. 编译
make

# 3. 安装
sudo make install

# 4. 验证
ls $(pg_config --sharedir)/extension/ | grep age
# 应该看到：age.control, age--*.sql
```

### 4.2 配置数据库

```sql
-- 1. 创建扩展（带错误处理）
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS age;
    RAISE NOTICE 'Apache AGE扩展安装成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE 'Apache AGE扩展已存在';
    WHEN undefined_file THEN
        RAISE EXCEPTION 'Apache AGE扩展文件不存在，请先安装扩展';
    WHEN OTHERS THEN
        RAISE WARNING '安装Apache AGE扩展失败: %', SQLERRM;
        RAISE;
END $$;

-- 2. 设置搜索路径（带错误处理）
DO $$
BEGIN
    PERFORM set_config('search_path', 'ag_catalog, "$user", public', false);
    RAISE NOTICE '搜索路径设置成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '设置搜索路径失败: %', SQLERRM;
        RAISE;
END $$;

-- 3. 创建图（带错误处理）
DO $$
BEGIN
    -- 检查图是否已存在
    IF EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE NOTICE '图 social_network 已存在，跳过创建';
    ELSE
        PERFORM create_graph('social_network');
        RAISE NOTICE '图 social_network 创建成功';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建图失败: %', SQLERRM;
        RAISE;
END $$;

-- 4. 验证（带性能测试）
EXPLAIN ANALYZE
SELECT * FROM ag_graph WHERE name = 'social_network';
```

### 4.3 Docker快速部署

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres-age:
    image: apache/age:latest
    container_name: postgres-age
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: testdb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    command:
      - "postgres"
      - "-c"
      - "shared_preload_libraries=age"

volumes:
  pgdata:
```

```bash
#!/bin/bash
# Docker部署Apache AGE（带错误处理）
set -e
set -u

error_exit() {
    echo "错误: $1" >&2
    exit 1
}

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    error_exit "docker-compose未安装，请先安装Docker和docker-compose"
fi

# 检查docker是否运行
if ! docker info &> /dev/null; then
    error_exit "Docker未运行，请先启动Docker服务"
fi

# 启动容器
echo "启动PostgreSQL+AGE容器..."
docker-compose up -d || error_exit "启动容器失败"

# 等待容器就绪
echo "等待容器就绪..."
sleep 5

# 检查容器状态
if ! docker ps | grep -q postgres-age; then
    error_exit "容器启动失败，请检查日志: docker-compose logs"
fi

# 连接并初始化
echo "连接数据库并初始化..."
docker exec -it postgres-age psql -U postgres -d testdb <<EOF
DO \$\$
BEGIN
    CREATE EXTENSION IF NOT EXISTS age;
    PERFORM set_config('search_path', 'ag_catalog, "\$user", public', false);
    RAISE NOTICE 'Apache AGE初始化成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '初始化失败: %', SQLERRM;
        RAISE;
END \$\$;
EOF

echo "部署完成！"
```

<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
grep

---

## 5. Cypher查询语言

### 5.1 基础语法

#### CREATE - 创建节点和边

```sql
-- 创建单个节点（带错误处理）
DO $$
DECLARE
    result_count int;
BEGIN
    -- 检查图是否存在
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    -- 执行创建节点
    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        CREATE (alice:Person {name: 'Alice', age: 30, city: 'Beijing'})
        RETURN alice
    $$) AS (alice agtype);

    IF result_count > 0 THEN
        RAISE NOTICE '节点创建成功';
    ELSE
        RAISE WARNING '节点创建失败，未返回结果';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建节点失败: %', SQLERRM;
        RAISE;
END $$;

-- 性能测试：创建单个节点
EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    CREATE (alice:Person {name: 'Alice', age: 30, city: 'Beijing'})
    RETURN alice
$$) AS (alice agtype);

-- 创建多个节点和边（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    PERFORM cypher('social_network', $$
        CREATE (alice:Person {name: 'Alice', age: 30})
        CREATE (bob:Person {name: 'Bob', age: 25})
        CREATE (carol:Person {name: 'Carol', age: 28})
        CREATE (alice)-[:FRIEND {since: '2020'}]->(bob)
        CREATE (bob)-[:FRIEND {since: '2021'}]->(carol)
        RETURN alice, bob, carol
    $$);

    RAISE NOTICE '多个节点和边创建成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建多个节点和边失败: %', SQLERRM;
        RAISE;
END $$;

-- 性能测试：创建多个节点和边
EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    CREATE (alice:Person {name: 'Alice', age: 30})
    CREATE (bob:Person {name: 'Bob', age: 25})
    CREATE (carol:Person {name: 'Carol', age: 28})
    CREATE (alice)-[:FRIEND {since: '2020'}]->(bob)
    CREATE (bob)-[:FRIEND {since: '2021'}]->(carol)
    RETURN alice, bob, carol
$$) AS (alice agtype, bob agtype, carol agtype);

-- 创建路径（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    PERFORM cypher('social_network', $$
        CREATE p = (a:Person {name: 'David'})-[:WORKS_AT]->(c:Company {name: 'TechCorp'})
        RETURN p
    $$);

    RAISE NOTICE '路径创建成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建路径失败: %', SQLERRM;
        RAISE;
END $$;

-- 性能测试：创建路径
EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    CREATE p = (a:Person {name: 'David'})-[:WORKS_AT]->(c:Company {name: 'TechCorp'})
    RETURN p
$$) AS (path agtype);
```

#### MATCH - 查询模式

```sql
-- 简单匹配（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    -- 检查图是否存在
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (p:Person)
        WHERE p.age > 25
        RETURN p.name, p.age
    $$) AS (name agtype, age agtype);

    RAISE NOTICE '查询完成，返回 % 条记录', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '查询失败: %', SQLERRM;
END $$;

-- 性能测试：简单匹配
EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WHERE p.age > 25
    RETURN p.name, p.age
$$) AS (name agtype, age agtype);

-- 关系匹配（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (a:Person)-[r:FRIEND]->(b:Person)
        RETURN a.name, b.name, r.since
    $$) AS (person1 agtype, person2 agtype, since agtype);

    RAISE NOTICE '关系匹配完成，返回 % 条记录', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '关系匹配查询失败: %', SQLERRM;
END $$;

-- 性能测试：关系匹配
EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (a:Person)-[r:FRIEND]->(b:Person)
    RETURN a.name, b.name, r.since
$$) AS (person1 agtype, person2 agtype, since agtype);

-- 可变长度路径（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (a:Person {name: 'Alice'})-[:FRIEND*1..3]->(friend)
        RETURN DISTINCT friend.name
    $$) AS (friend_name agtype);

    RAISE NOTICE '可变长度路径查询完成，返回 % 个朋友', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '可变长度路径查询失败: %', SQLERRM;
END $$;

-- 性能测试：可变长度路径
EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (a:Person {name: 'Alice'})-[:FRIEND*1..3]->(friend)
    RETURN DISTINCT friend.name
$$) AS (friend_name agtype);

-- 双向关系（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (a:Person)-[:FRIEND]-(b:Person)
        WHERE a.name = 'Alice'
        RETURN DISTINCT b.name
    $$) AS (name agtype);

    RAISE NOTICE '双向关系查询完成，返回 % 个连接', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '双向关系查询失败: %', SQLERRM;
END $$;

-- 性能测试：双向关系
EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (a:Person)-[:FRIEND]-(b:Person)
    WHERE a.name = 'Alice'
    RETURN DISTINCT b.name
$$) AS (name agtype);
```

<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file

#### WHERE - 过滤条件

```sql
-- 属性过滤（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (p:Person)
        WHERE p.age >= 25 AND p.age <= 35 AND p.city = 'Beijing'
        RETURN p.name, p.age
    $$) AS (name agtype, age agtype);

    RAISE NOTICE '属性过滤查询完成，返回 % 条记录', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '属性过滤查询失败: %', SQLERRM;
END $$;

EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WHERE p.age >= 25 AND p.age <= 35 AND p.city = 'Beijing'
    RETURN p.name, p.age
$$) AS (name agtype, age agtype);

-- 正则表达式（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (p:Person)
        WHERE p.name =~ 'A.*'
        RETURN p.name
    $$) AS (name agtype);

    RAISE NOTICE '正则表达式查询完成，返回 % 条记录', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '正则表达式查询失败: %', SQLERRM;
END $$;

EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WHERE p.name =~ 'A.*'
    RETURN p.name
$$) AS (name agtype);

-- NULL检查（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (p:Person)
        WHERE p.email IS NOT NULL
        RETURN p.name, p.email
    $$) AS (name agtype, email agtype);

    RAISE NOTICE 'NULL检查查询完成，返回 % 条有效记录', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'NULL检查查询失败: %', SQLERRM;
END $$;

EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WHERE p.email IS NOT NULL
    RETURN p.name, p.email
$$) AS (name agtype, email agtype);

-- 列表包含（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (p:Person)
        WHERE p.age IN [25, 30, 35]
        RETURN p.name
    $$) AS (name agtype);

    RAISE NOTICE '列表包含查询完成，返回 % 条记录', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '列表包含查询失败: %', SQLERRM;
END $$;

EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WHERE p.age IN [25, 30, 35]
    RETURN p.name
$$) AS (name agtype);
```

<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
grep

### 5.2 高级查询

#### 聚合函数

```sql
-- COUNT, SUM, AVG, MIN, MAX（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (p:Person)
        RETURN
            COUNT(p) AS total_persons,
            AVG(p.age) AS avg_age,
            MIN(p.age) AS min_age,
            MAX(p.age) AS max_age
    $$) AS (total agtype, avg_age agtype, min_age agtype, max_age agtype);

    IF result_count > 0 THEN
        RAISE NOTICE '聚合查询完成，返回 % 行统计结果', result_count;
    ELSE
        RAISE WARNING '聚合查询返回空结果';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '聚合查询失败: %', SQLERRM;
END $$;

-- 性能测试：聚合函数
EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    RETURN
        COUNT(p) AS total_persons,
        AVG(p.age) AS avg_age,
        MIN(p.age) AS min_age,
        MAX(p.age) AS max_age
$$) AS (total agtype, avg_age agtype, min_age agtype, max_age agtype);

-- GROUP BY（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (p:Person)
        RETURN p.city, COUNT(p) AS person_count, AVG(p.age) AS avg_age
        ORDER BY person_count DESC
    $$) AS (city agtype, count agtype, avg_age agtype);

    RAISE NOTICE 'GROUP BY查询完成，返回 % 个城市的分组统计', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'GROUP BY查询失败: %', SQLERRM;
END $$;

-- 性能测试：GROUP BY
EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    RETURN p.city, COUNT(p) AS person_count, AVG(p.age) AS avg_age
    ORDER BY person_count DESC
$$) AS (city agtype, count agtype, avg_age agtype);

-- COLLECT聚合（带错误处理和性能测试）
DO $$
DECLARE
    result_count int;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = 'social_network') THEN
        RAISE EXCEPTION '图 social_network 不存在，请先创建图';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
        MATCH (p:Person)-[:FRIEND]->(friend)
        RETURN p.name, COLLECT(friend.name) AS friends
    $$) AS (person agtype, friends agtype);

    RAISE NOTICE 'COLLECT聚合查询完成，返回 % 个人的朋友列表', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'COLLECT聚合查询失败: %', SQLERRM;
END $$;

-- 性能测试：COLLECT聚合
EXPLAIN ANALYZE
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)-[:FRIEND]->(friend)
    RETURN p.name, COLLECT(friend.name) AS friends
$$) AS (person agtype, friends agtype);
```

<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
grep

#### 子查询与UNION

```sql
-- UNION ALL
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person) WHERE p.age > 30
    RETURN p.name AS name, 'senior' AS category
    UNION ALL
    MATCH (p:Person) WHERE p.age <= 30
    RETURN p.name AS name, 'junior' AS category
$$) AS (name agtype, category agtype);

-- WITH子句（中间结果）
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WITH p, p.age AS age
    WHERE age > 25
    MATCH (p)-[:FRIEND]->(friend)
    RETURN p.name, COUNT(friend) AS friend_count
$$) AS (name agtype, count agtype);
```

#### OPTIONAL MATCH（左外连接）

```sql
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    OPTIONAL MATCH (p)-[:FRIEND]->(friend)
    RETURN p.name, friend.name
$$) AS (person agtype, friend agtype);
-- 即使某人没有朋友，也会返回其记录（friend为NULL）
```

### 5.3 更新与删除

#### SET - 更新属性

```sql
-- 设置属性
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person {name: 'Alice'})
    SET p.age = 31, p.updated = timestamp()
    RETURN p
$$) AS (person agtype);

-- 添加标签
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person {name: 'Alice'})
    SET p:VIP
    RETURN p
$$) AS (person agtype);

-- 删除属性
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person {name: 'Alice'})
    SET p.email = NULL
    RETURN p
$$) AS (person agtype);
```

#### REMOVE - 删除属性和标签

```sql
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person {name: 'Alice'})
    REMOVE p.age
    RETURN p
$$) AS (person agtype);
```

#### DELETE - 删除节点和边

```sql
-- 删除关系
SELECT * FROM cypher('social_network', $$
    MATCH (a:Person {name: 'Alice'})-[r:FRIEND]->(b:Person {name: 'Bob'})
    DELETE r
$$) AS (result agtype);

-- 删除节点（必须先删除关系）
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person {name: 'Alice'})
    DETACH DELETE p
$$) AS (result agtype);
-- DETACH DELETE 自动删除相关的所有边
```

#### MERGE - 创建或更新

```sql
-- 不存在则创建，存在则更新
SELECT * FROM cypher('social_network', $$
    MERGE (p:Person {email: 'alice@example.com'})
    ON CREATE SET p.name = 'Alice', p.created = timestamp()
    ON MATCH SET p.last_login = timestamp()
    RETURN p
$$) AS (person agtype);

-- 合并关系
SELECT * FROM cypher('social_network', $$
    MATCH (a:Person {name: 'Alice'})
    MATCH (b:Person {name: 'Bob'})
    MERGE (a)-[r:FRIEND]->(b)
    ON CREATE SET r.since = '2025-01-01'
    RETURN r
$$) AS (relationship agtype);
```

---

## 6. 图建模实战

### 6.1 社交网络模型

#### 数据模型设计

```text
节点类型：
- Person: 用户
- Post: 帖子
- Comment: 评论
- Tag: 标签

边类型：
- FRIEND: 好友关系
- FOLLOWS: 关注关系
- CREATED: 创建内容
- LIKED: 点赞
- COMMENTED: 评论
- TAGGED: 标签
```

#### 实现代码

```sql
-- 创建用户
SELECT * FROM cypher('social_network', $$
    CREATE (alice:Person {
        id: 1,
        name: 'Alice Wang',
        email: 'alice@example.com',
        bio: 'Software Engineer',
        location: 'Beijing',
        joined: '2020-01-01'
    })
    CREATE (bob:Person {
        id: 2,
        name: 'Bob Chen',
        email: 'bob@example.com',
        bio: 'Data Scientist',
        location: 'Shanghai',
        joined: '2020-02-15'
    })
    CREATE (carol:Person {
        id: 3,
        name: 'Carol Li',
        email: 'carol@example.com',
        bio: 'Product Manager',
        location: 'Beijing',
        joined: '2020-03-20'
    })
    RETURN alice, bob, carol
$$) AS (alice agtype, bob agtype, carol agtype);

-- 创建关系
SELECT * FROM cypher('social_network', $$
    MATCH (alice:Person {id: 1})
    MATCH (bob:Person {id: 2})
    MATCH (carol:Person {id: 3})
    CREATE (alice)-[:FRIEND {since: '2020-01-15', strength: 0.8}]->(bob)
    CREATE (bob)-[:FRIEND {since: '2020-02-20', strength: 0.9}]->(carol)
    CREATE (alice)-[:FOLLOWS {since: '2020-03-01'}]->(carol)
$$) AS (result agtype);

-- 创建内容
SELECT * FROM cypher('social_network', $$
    MATCH (alice:Person {id: 1})
    CREATE (post:Post {
        id: 101,
        title: 'Getting Started with Graph Databases',
        content: 'Graph databases are powerful...',
        created: '2025-01-01T10:00:00',
        views: 150,
        likes: 25
    })
    CREATE (alice)-[:CREATED {timestamp: '2025-01-01T10:00:00'}]->(post)
    RETURN post
$$) AS (post agtype);

-- 创建标签
SELECT * FROM cypher('social_network', $$
    MATCH (post:Post {id: 101})
    CREATE (tag1:Tag {name: 'database'})
    CREATE (tag2:Tag {name: 'graph'})
    CREATE (post)-[:TAGGED]->(tag1)
    CREATE (post)-[:TAGGED]->(tag2)
$$) AS (result agtype);
```

### 6.2 推荐系统模型

#### 协同过滤推荐

```sql
-- 基于共同好友的用户推荐
SELECT * FROM cypher('social_network', $$
    MATCH (user:Person {id: 1})-[:FRIEND]->(friend)-[:FRIEND]->(recommendation)
    WHERE NOT (user)-[:FRIEND]->(recommendation) AND user <> recommendation
    WITH recommendation, COUNT(friend) AS common_friends
    ORDER BY common_friends DESC
    LIMIT 5
    RETURN recommendation.name, common_friends
$$) AS (recommended_user agtype, common_friends agtype);

-- 基于共同兴趣的内容推荐
SELECT * FROM cypher('social_network', $$
    MATCH (user:Person {id: 1})-[:LIKED]->(post1:Post)-[:TAGGED]->(tag)
    MATCH (post2:Post)-[:TAGGED]->(tag)
    WHERE NOT (user)-[:LIKED]->(post2) AND post1 <> post2
    WITH post2, COUNT(DISTINCT tag) AS common_tags
    ORDER BY common_tags DESC, post2.likes DESC
    LIMIT 10
    RETURN post2.title, common_tags, post2.likes
$$) AS (title agtype, common_tags agtype, likes agtype);
```

### 6.3 知识图谱模型

#### 实体-关系-属性模型

```sql
-- 创建知识图谱
SELECT * FROM cypher('knowledge_graph', $$
    -- 人物实体
    CREATE (einstein:Person {name: 'Albert Einstein', born: 1879, died: 1955})
    CREATE (newton:Person {name: 'Isaac Newton', born: 1642, died: 1727})

    -- 理论实体
    CREATE (relativity:Theory {name: 'Theory of Relativity', year: 1915})
    CREATE (gravity:Theory {name: 'Law of Universal Gravitation', year: 1687})

    -- 机构实体
    CREATE (princeton:University {name: 'Princeton University', founded: 1746})
    CREATE (cambridge:University {name: 'University of Cambridge', founded: 1209})

    -- 关系
    CREATE (einstein)-[:PROPOSED]->(relativity)
    CREATE (newton)-[:PROPOSED]->(gravity)
    CREATE (einstein)-[:WORKED_AT {from: 1933, to: 1955}]->(princeton)
    CREATE (newton)-[:STUDIED_AT]->(cambridge)
    CREATE (relativity)-[:EXTENDS]->(gravity)
$$) AS (result agtype);

-- 知识推理查询
SELECT * FROM cypher('knowledge_graph', $$
    MATCH path = (person:Person)-[:PROPOSED]->(theory1:Theory)-[:EXTENDS]->(theory2:Theory)
    RETURN person.name, theory1.name, theory2.name, LENGTH(path) AS path_length
$$) AS (person agtype, theory1 agtype, theory2 agtype, length agtype);
```

---

## 7. 高级图算法

### 7.1 最短路径算法

#### 单源最短路径

```sql
-- 朋友之间的最短路径
SELECT * FROM cypher('social_network', $$
    MATCH path = shortestPath(
        (alice:Person {name: 'Alice'})-[:FRIEND*]-(target:Person {name: 'David'})
    )
    RETURN [node IN nodes(path) | node.name] AS path, LENGTH(path) AS distance
$$) AS (path agtype, distance agtype);

-- 所有最短路径（可能有多条）
SELECT * FROM cypher('social_network', $$
    MATCH path = allShortestPaths(
        (alice:Person {name: 'Alice'})-[:FRIEND*]-(target:Person {name: 'David'})
    )
    RETURN [node IN nodes(path) | node.name] AS path
$$) AS (path agtype);
```

#### Dijkstra算法（带权重）

```sql
-- 自定义实现带权重的最短路径
WITH cypher('social_network', $$
    MATCH path = (start:Person {name: 'Alice'})-[rels:FRIEND*]-(end:Person {name: 'David'})
    WHERE LENGTH(path) <= 5
    WITH path, REDUCE(weight = 0, r IN rels | weight + (1.0 - r.strength)) AS total_weight
    ORDER BY total_weight ASC
    LIMIT 1
    RETURN [node IN nodes(path) | node.name] AS path, total_weight
$$) AS (path agtype, weight agtype);
```

### 7.2 中心性分析

#### 度中心性（Degree Centrality）

```sql
-- 出度中心性（最多朋友的用户）
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)-[r:FRIEND]->()
    RETURN p.name, COUNT(r) AS out_degree
    ORDER BY out_degree DESC
    LIMIT 10
$$) AS (name agtype, out_degree agtype);

-- 入度中心性（被最多人关注）
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)<-[r:FOLLOWS]-()
    RETURN p.name, COUNT(r) AS in_degree
    ORDER BY in_degree DESC
    LIMIT 10
$$) AS (name agtype, in_degree agtype);
```

#### 接近中心性（Closeness Centrality）

```sql
-- 计算平均最短路径长度
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WITH p
    MATCH path = (p)-[:FRIEND*]-(other:Person)
    WHERE p <> other
    WITH p, AVG(LENGTH(path)) AS avg_distance
    RETURN p.name, 1.0 / avg_distance AS closeness_centrality
    ORDER BY closeness_centrality DESC
    LIMIT 10
$$) AS (name agtype, closeness agtype);
```

#### 中介中心性（Betweenness Centrality）

```sql
-- 简化实现：计算通过某节点的路径数
SELECT * FROM cypher('social_network', $$
    MATCH path = (a:Person)-[:FRIEND*]-(b:Person)
    WHERE a <> b
    WITH [node IN nodes(path)[1..-1] | node] AS intermediate_nodes
    UNWIND intermediate_nodes AS node
    RETURN node.name, COUNT(*) AS paths_through
    ORDER BY paths_through DESC
    LIMIT 10
$$) AS (name agtype, betweenness agtype);
```

### 7.3 社区发现

#### 简单社区检测（基于连通分量）

```sql
-- 查找强连通的社区
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)-[:FRIEND*]-(community_member:Person)
    WITH p, COLLECT(DISTINCT community_member.name) AS community
    WHERE SIZE(community) > 2
    RETURN p.name AS center, community, SIZE(community) AS community_size
    ORDER BY community_size DESC
$$) AS (center agtype, members agtype, size agtype);
```

#### 三角形计数（聚类系数）

```sql
-- 计算每个用户的三角形数量（共同好友成对）
SELECT * FROM cypher('social_network', $$
    MATCH (a:Person)-[:FRIEND]->(b:Person)-[:FRIEND]->(c:Person)-[:FRIEND]->(a)
    RETURN a.name, COUNT(DISTINCT b) AS triangles
    ORDER BY triangles DESC
$$) AS (name agtype, triangles agtype);
```

### 7.4 PageRank算法

#### 简化实现

```sql
-- 迭代计算PageRank（简化版）
DO $$
DECLARE
    damping_factor FLOAT := 0.85;
    iterations INT := 10;
    i INT;
BEGIN
    -- 初始化PageRank
    PERFORM cypher('social_network', $$
        MATCH (p:Person)
        SET p.pagerank = 1.0
    $$);

    -- 迭代计算
    FOR i IN 1..iterations LOOP
        PERFORM cypher('social_network', $$
            MATCH (p:Person)
            OPTIONAL MATCH (p)<-[:FRIEND]-(incoming:Person)
            WITH p, COLLECT(incoming) AS incomings
            WITH p, incomings,
                 REDUCE(sum = 0.0, inc IN incomings |
                    sum + inc.pagerank / SIZE((inc)-[:FRIEND]->())
                 ) AS incoming_rank
            SET p.pagerank = (1 - $damping) + $damping * incoming_rank
        $$, jsonb_build_object('damping', damping_factor));
    END LOOP;
END $$;

-- 查询结果
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    RETURN p.name, p.pagerank
    ORDER BY p.pagerank DESC
$$) AS (name agtype, pagerank agtype);
```

---

## 8. 性能优化

### 8.1 索引策略

#### 创建索引

```sql
-- 1. 为节点属性创建索引
SELECT * FROM cypher('social_network', $$
    CREATE INDEX ON :Person(name)
$$) AS (result agtype);

-- 实际执行的SQL（内部）
CREATE INDEX person_name_idx ON social_network."Person"
USING btree ((properties->>'name'));

-- 2. 组合索引
CREATE INDEX person_city_age_idx ON social_network."Person"
USING btree ((properties->>'city'), (properties->>'age'));

-- 3. JSONB索引（用于属性查询）
CREATE INDEX person_properties_gin_idx ON social_network."Person"
USING gin (properties);
```

#### 索引使用建议

| 场景 | 索引类型 | 示例 |
|------|----------|------|
| 精确匹配 | B-tree | `WHERE p.name = 'Alice'` |
| 范围查询 | B-tree | `WHERE p.age BETWEEN 25 AND 35` |
| 全文搜索 | GIN | `WHERE p.bio @@ 'engineer'` |
| 属性存在性 | GIN | `WHERE properties ? 'email'` |

### 8.2 查询优化

#### EXPLAIN分析

```sql
-- 查看查询计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM cypher('social_network', $$
    MATCH (a:Person {name: 'Alice'})-[:FRIEND*2..3]->(friend)
    RETURN DISTINCT friend.name
$$) AS (name agtype);
```

#### 优化技巧

**1. 限制路径深度**:

```sql
-- ❌ 坏实践：无限深度
MATCH (a)-[:FRIEND*]->(b)

-- ✅ 好实践：限制深度
MATCH (a)-[:FRIEND*1..3]->(b)
```

**2. 使用LIMIT early**:

```sql
-- ❌ 坏实践
MATCH (p:Person)-[:FRIEND]->(friend)
RETURN friend.name
ORDER BY friend.age DESC

-- ✅ 好实践
MATCH (p:Person)-[:FRIEND]->(friend)
WITH friend
ORDER BY friend.age DESC
LIMIT 100
RETURN friend.name
```

**3. 避免笛卡尔积**:

```sql
-- ❌ 坏实践：产生笛卡尔积
MATCH (a:Person), (b:Person)
WHERE a.city = b.city

-- ✅ 好实践
MATCH (a:Person)-[:LIVES_IN]->(city:City)<-[:LIVES_IN]-(b:Person)
```

### 8.3 批量操作优化

#### 批量导入

```sql
-- 使用UNWIND批量创建
SELECT * FROM cypher('social_network', $$
    UNWIND [
        {name: 'User1', age: 25},
        {name: 'User2', age: 30},
        {name: 'User3', age: 35}
    ] AS user_data
    CREATE (p:Person)
    SET p = user_data
$$) AS (result agtype);

-- 从CSV批量导入
COPY (
    SELECT * FROM cypher('social_network', $$
        LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row
        CREATE (p:Person {
            name: row.name,
            age: toInteger(row.age),
            email: row.email
        })
    $$) AS (result agtype)
) TO STDOUT;
```

#### 批量更新

```sql
-- 使用事务批量更新
BEGIN;
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WHERE p.age IS NULL
    SET p.age = 0
$$) AS (result agtype);

SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WHERE p.updated_at IS NULL
    SET p.updated_at = timestamp()
$$) AS (result agtype);
COMMIT;
```

### 8.4 监控与调优

#### 性能监控查询

```sql
-- 查看图的统计信息
SELECT
    nspname AS graph_name,
    relname AS label_name,
    n_live_tup AS row_count,
    n_dead_tup AS dead_rows,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE schemaname LIKE 'social_network';

-- 查看索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname LIKE 'social_network'
ORDER BY idx_scan DESC;
```

#### 配置优化

```sql
-- PostgreSQL配置建议
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET work_mem = '50MB';
ALTER SYSTEM SET random_page_cost = 1.1;  -- SSD

-- AGE特定配置
ALTER SYSTEM SET age.enable_optimizer = ON;
ALTER SYSTEM SET age.extra_float_digits = 0;

SELECT pg_reload_conf();
```

---

## 9. 生产实战案例

### 9.1 案例1：欺诈检测系统

#### 业务场景

检测金融交易中的异常模式：

- 快速连续交易
- 环形转账
- 共享设备/IP

#### 数据模型

```sql
SELECT create_graph('fraud_detection');

-- 创建实体
SELECT * FROM cypher('fraud_detection', $$
    -- 账户
    CREATE (a1:Account {id: 'ACC001', name: 'Alice', risk_score: 0.1})
    CREATE (a2:Account {id: 'ACC002', name: 'Bob', risk_score: 0.2})
    CREATE (a3:Account {id: 'ACC003', name: 'Carol', risk_score: 0.8})

    -- 设备
    CREATE (d1:Device {id: 'DEV001', type: 'mobile', fingerprint: 'ABC123'})
    CREATE (d2:Device {id: 'DEV002', type: 'desktop', fingerprint: 'XYZ789'})

    -- IP地址
    CREATE (ip1:IPAddress {ip: '192.168.1.100', country: 'CN'})
    CREATE (ip2:IPAddress {ip: '10.0.0.50', country: 'US'})

    -- 交易
    CREATE (t1:Transaction {id: 'TXN001', amount: 1000, timestamp: '2025-01-01T10:00:00'})
    CREATE (t2:Transaction {id: 'TXN002', amount: 5000, timestamp: '2025-01-01T10:05:00'})
    CREATE (t3:Transaction {id: 'TXN003', amount: 2000, timestamp: '2025-01-01T10:10:00'})

    -- 关系
    CREATE (a1)-[:TRANSFERRED]->(t1)-[:TO]->(a2)
    CREATE (a2)-[:TRANSFERRED]->(t2)-[:TO]->(a3)
    CREATE (a3)-[:TRANSFERRED]->(t3)-[:TO]->(a1)  -- 环形转账！
    CREATE (a1)-[:USED_DEVICE]->(d1)
    CREATE (a3)-[:USED_DEVICE]->(d1)  -- 共享设备！
    CREATE (t1)-[:FROM_IP]->(ip1)
    CREATE (t2)-[:FROM_IP]->(ip2)
$$) AS (result agtype);
```

#### 欺诈检测查询

```sql
-- 1. 检测环形转账（洗钱模式）
SELECT * FROM cypher('fraud_detection', $$
    MATCH path = (a:Account)-[:TRANSFERRED]->(:Transaction)-[:TO]->(:Account)
                 -[:TRANSFERRED]->(:Transaction)-[:TO]->(:Account)
                 -[:TRANSFERRED]->(:Transaction)-[:TO]->(a)
    WHERE LENGTH(path) >= 3
    RETURN
        [acc IN nodes(path) | acc.id] AS circular_path,
        'Circular Transfer Detected' AS alert_type,
        'HIGH' AS severity
$$) AS (path agtype, alert agtype, severity agtype);

-- 2. 检测共享设备的高风险账户
SELECT * FROM cypher('fraud_detection', $$
    MATCH (a1:Account)-[:USED_DEVICE]->(d:Device)<-[:USED_DEVICE]-(a2:Account)
    WHERE a1 <> a2 AND (a1.risk_score > 0.7 OR a2.risk_score > 0.7)
    RETURN
        a1.name AS account1,
        a2.name AS account2,
        d.fingerprint AS shared_device,
        'Shared Device - High Risk' AS alert_type
$$) AS (acc1 agtype, acc2 agtype, device agtype, alert agtype);

-- 3. 检测快速连续大额交易
SELECT * FROM cypher('fraud_detection', $$
    MATCH (a:Account)-[:TRANSFERRED]->(t1:Transaction)
    MATCH (a)-[:TRANSFERRED]->(t2:Transaction)
    WHERE t1 <> t2
      AND t1.amount > 1000
      AND t2.amount > 1000
      AND duration.between(t1.timestamp, t2.timestamp).minutes < 10
    RETURN
        a.name AS account,
        t1.amount AS amount1,
        t2.amount AS amount2,
        'Rapid Large Transactions' AS alert_type
$$) AS (account agtype, amt1 agtype, amt2 agtype, alert agtype);
```

### 9.2 案例2：社交推荐引擎

#### 好友推荐算法

```sql
-- 基于共同好友的推荐（加权）
SELECT * FROM cypher('social_network', $$
    MATCH (user:Person {id: $user_id})
    MATCH (user)-[:FRIEND]->(mutual_friend)-[:FRIEND]->(recommendation)
    WHERE NOT (user)-[:FRIEND]->(recommendation)
      AND user <> recommendation
      AND NOT (user)-[:BLOCKED]->(recommendation)

    WITH recommendation, COUNT(DISTINCT mutual_friend) AS common_friends,
         COLLECT(DISTINCT mutual_friend.name) AS mutual_names

    OPTIONAL MATCH (recommendation)-[:WORKS_AT]->(company)<-[:WORKS_AT]-(user)
    WITH recommendation, common_friends, mutual_names,
         CASE WHEN company IS NOT NULL THEN 10 ELSE 0 END AS company_bonus

    OPTIONAL MATCH (recommendation)-[:LIVES_IN]->(city)<-[:LIVES_IN]-(user)
    WITH recommendation, common_friends, mutual_names, company_bonus,
         CASE WHEN city IS NOT NULL THEN 5 ELSE 0 END AS location_bonus

    WITH recommendation, common_friends, mutual_names,
         (common_friends * 10 + company_bonus + location_bonus) AS score

    ORDER BY score DESC
    LIMIT 10

    RETURN
        recommendation.name AS recommended_user,
        recommendation.bio AS bio,
        common_friends AS mutual_friends_count,
        mutual_names[0..3] AS sample_mutual_friends,
        score AS recommendation_score
$$) AS (user agtype, bio agtype, mutual_count agtype, mutuals agtype, score agtype);
```

### 9.3 案例3：供应链分析

#### 供应链影响分析

```sql
SELECT create_graph('supply_chain');

-- 创建供应链网络
SELECT * FROM cypher('supply_chain', $$
    CREATE (supplier1:Supplier {name: 'Raw Material Co', location: 'China'})
    CREATE (mfg1:Manufacturer {name: 'Factory A', location: 'Vietnam'})
    CREATE (mfg2:Manufacturer {name: 'Factory B', location: 'Thailand'})
    CREATE (dist:Distributor {name: 'Global Dist', location: 'Singapore'})
    CREATE (retail1:Retailer {name: 'Store Chain A', location: 'US'})
    CREATE (retail2:Retailer {name: 'Store Chain B', location: 'EU'})

    CREATE (supplier1)-[:SUPPLIES {lead_time: 7, reliability: 0.95}]->(mfg1)
    CREATE (supplier1)-[:SUPPLIES {lead_time: 10, reliability: 0.90}]->(mfg2)
    CREATE (mfg1)-[:SHIPS_TO {lead_time: 14, cost: 500}]->(dist)
    CREATE (mfg2)-[:SHIPS_TO {lead_time: 12, cost: 450}]->(dist)
    CREATE (dist)-[:DISTRIBUTES {lead_time: 21, cost: 800}]->(retail1)
    CREATE (dist)-[:DISTRIBUTES {lead_time: 28, cost: 900}]->(retail2)
$$) AS (result agtype);

-- 分析供应链中断影响
SELECT * FROM cypher('supply_chain', $$
    // 假设某个制造商中断
    MATCH (disrupted:Manufacturer {name: 'Factory A'})
    MATCH path = (disrupted)-[*]->(affected)
    WHERE affected:Retailer OR affected:Distributor
    RETURN
        disrupted.name AS disrupted_node,
        COLLECT(DISTINCT affected.name) AS affected_downstream,
        COUNT(DISTINCT affected) AS impact_count
$$) AS (disrupted agtype, affected agtype, impact agtype);

-- 寻找替代供应路径
SELECT * FROM cypher('supply_chain', $$
    MATCH path = (s:Supplier)-[:SUPPLIES*..5]->(r:Retailer {name: 'Store Chain A'})
    WITH path,
         REDUCE(time = 0, rel IN relationships(path) | time + rel.lead_time) AS total_lead_time,
         REDUCE(cost = 0, rel IN relationships(path) | cost + COALESCE(rel.cost, 0)) AS total_cost
    ORDER BY total_lead_time ASC, total_cost ASC
    LIMIT 5
    RETURN
        [node IN nodes(path) | node.name] AS supply_path,
        total_lead_time AS lead_time_days,
        total_cost AS total_cost_usd
$$) AS (path agtype, lead_time agtype, cost agtype);
```

---

## 10. 与Neo4j对比

### 10.1 功能对比

| 特性 | Apache AGE | Neo4j | 说明 |
| ------ | ----------- | ------- | ------ |
| **Cypher支持** | ✅ openCypher | ✅ 完整Cypher | AGE兼容性约80% |
| **ACID事务** | ✅ 完整支持 | ✅ 完整支持 | 基于PostgreSQL |
| **SQL兼容** | ✅ 原生支持 | ❌ 需插件 | AGE核心优势 |
| **混合查询** | ✅ 优秀 | ⚠️ 有限 | SQL+Cypher同时使用 |
| **许可证** | ✅ Apache 2.0 | ⚠️ GPLv3/商业 | AGE完全免费 |
| **集群支持** | ⚠️ 依赖PG扩展 | ✅ 原生支持 | Neo4j更成熟 |
| **可视化工具** | ⚠️ 第三方 | ✅ Neo4j Browser | Neo4j工具更丰富 |
| **性能** | ⚠️ 中等 | ✅ 优秀 | 图查询Neo4j更快 |
| **生态系统** | ⚠️ 发展中 | ✅ 成熟 | Neo4j社区更大 |

### 10.2 语法差异

#### AGE特有语法

```sql
-- AGE需要用SQL包装
SELECT * FROM cypher('graph_name', $$
    MATCH (n:Person) RETURN n
$$) AS (n agtype);

-- Neo4j可直接执行
MATCH (n:Person) RETURN n;
```

#### 混合查询

```sql
-- AGE可以SQL+Cypher混合
WITH person_ids AS (
    SELECT id FROM users WHERE age > 25
)
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person)
    WHERE p.id IN $person_ids
    RETURN p
$$, jsonb_build_object('person_ids', (SELECT array_agg(id) FROM person_ids)))
AS (person agtype);

-- Neo4j需要使用过程
CALL apoc.cypher.runFile('query.cypher');
```

### 10.3 迁移指南

#### 从Neo4j迁移到AGE

```bash
# 1. 导出Neo4j数据
neo4j-admin dump --database=neo4j --to=/backup/neo4j.dump

# 2. 转换为Cypher脚本
# 使用neo4j-shell导出
MATCH (n) RETURN n LIMIT 10000;

# 3. 在AGE中重建
```

```sql
-- 4. 批量导入AGE
SELECT * FROM cypher('new_graph', $$
    UNWIND $nodes AS node_data
    CREATE (n)
    SET n = node_data
$$, jsonb_build_object('nodes', nodes_array)) AS (result agtype);
```

---

## 11. 最佳实践

### 11.1 设计原则

#### 1. 图建模最佳实践

**✅ 好的设计**:

```cypher
-- 使用明确的关系类型
(person)-[:WORKS_FOR]->(company)
(person)-[:LIVES_IN]->(city)

-- 属性存储在正确的位置
(person:Person {name: 'Alice', age: 30})
-[employment:WORKS_FOR {since: '2020', position: 'Engineer'}]->
(company:Company {name: 'TechCorp'})
```

**❌ 避免的设计**:

```cypher
-- 使用通用关系
(person)-[:RELATED_TO]->(company)  // 关系类型不明确

-- 过度使用属性
(person:Person {name: 'Alice', company: 'TechCorp'})  // 应该用关系
```

#### 2. 性能考虑

| 场景 | 建议 | 原因 |
|------|------|------|
| 高频查询属性 | 创建索引 | 加速查找 |
| 大量节点 | 分批处理 | 避免内存溢出 |
| 深度遍历 | 限制深度 | 防止性能下降 |
| 读多写少 | 物化视图 | 预计算结果 |

### 11.2 安全建议

#### 权限控制

```sql
-- 1. 创建只读用户（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'graph_reader') THEN
        CREATE USER graph_reader WITH PASSWORD 'secure_password';
        RAISE NOTICE '只读用户 graph_reader 创建成功';
    ELSE
        RAISE NOTICE '用户 graph_reader 已存在';
    END IF;

    GRANT USAGE ON SCHEMA ag_catalog TO graph_reader;
    GRANT SELECT ON ALL TABLES IN SCHEMA ag_catalog TO graph_reader;
    RAISE NOTICE '只读权限授予成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '用户已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE WARNING '创建只读用户失败: %', SQLERRM;
        RAISE;
END $$;

-- 2. 创建读写用户（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'graph_writer') THEN
        CREATE USER graph_writer WITH PASSWORD 'secure_password';
        RAISE NOTICE '读写用户 graph_writer 创建成功';
    ELSE
        RAISE NOTICE '用户 graph_writer 已存在';
    END IF;

    GRANT ALL ON SCHEMA ag_catalog TO graph_writer;
    RAISE NOTICE '读写权限授予成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '用户已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE WARNING '创建读写用户失败: %', SQLERRM;
        RAISE;
END $$;

-- 3. 使用RLS行级安全（带错误处理）
DO $$
BEGIN
    -- 检查表是否存在
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'ag_catalog'
                 AND table_name LIKE '%Person%') THEN
        ALTER TABLE ag_catalog."Person" ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE '行级安全已启用';
    ELSE
        RAISE WARNING 'Person表不存在，跳过启用行级安全';
        RETURN;
    END IF;

    -- 创建策略（如果不存在）
    DROP POLICY IF EXISTS person_isolation ON ag_catalog."Person";
    CREATE POLICY person_isolation ON ag_catalog."Person"
        USING (
            COALESCE(properties->>'tenant_id', '') =
            COALESCE(current_setting('app.tenant_id', true), '')
        );
    RAISE NOTICE '行级安全策略创建成功';
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '表不存在，跳过行级安全配置';
    WHEN OTHERS THEN
        RAISE WARNING '配置行级安全失败: %', SQLERRM;
        RAISE;
END $$;

-- 性能测试：验证RLS策略
EXPLAIN ANALYZE
SELECT COUNT(*)
FROM ag_catalog."Person"
WHERE properties->>'tenant_id' = current_setting('app.tenant_id', true);
```

#### SQL注入防护

```sql
-- ❌ 危险：字符串拼接
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person {name: '$$) || user_input || $$'}) RETURN p
$$) AS (p agtype);

-- ✅ 安全：使用参数化查询
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person {name: $user_name}) RETURN p
$$, jsonb_build_object('user_name', user_input)) AS (p agtype);
```

### 11.3 运维建议

#### 备份策略

```bash
# 1. 逻辑备份
pg_dump -U postgres -Fc -f graph_backup.dump -n social_network testdb

# 2. 物理备份
pg_basebackup -U postgres -D /backup/pgdata -Ft -z -P

# 3. 增量备份（WAL归档）
# postgresql.conf
archive_mode = on
archive_command = 'cp %p /archive/%f'
```

#### 监控指标

```sql
-- 创建监控视图
CREATE VIEW graph_health_metrics AS
SELECT
    g.name AS graph_name,
    COUNT(DISTINCT l.name) AS label_count,
    SUM(s.n_live_tup) AS total_nodes,
    pg_size_pretty(SUM(pg_total_relation_size(s.relid))) AS total_size
FROM ag_graph g
JOIN ag_label l ON l.graph = g.graphid
JOIN pg_stat_user_tables s ON s.schemaname = g.name
GROUP BY g.name;

-- 查询监控
SELECT * FROM graph_health_metrics;
```

---

## 12. FAQ与疑难解答

### Q1: AGE性能不如Neo4j怎么办？

**A**:

1. **创建适当索引**：为高频查询属性创建索引
2. **限制遍历深度**：避免`-[*]->`，使用`-[*1..3]->`
3. **使用物化视图**：预计算复杂查询结果
4. **调整PostgreSQL配置**：增加`shared_buffers`和`work_mem`

```sql
-- 创建物化视图加速查询
CREATE MATERIALIZED VIEW friend_recommendations AS
SELECT * FROM cypher('social_network', $$
    MATCH (user:Person)-[:FRIEND]->(friend)-[:FRIEND]->(recommendation)
    WHERE NOT (user)-[:FRIEND]->(recommendation)
    RETURN user.id, COLLECT(DISTINCT recommendation.id) AS recommendations
$$) AS (user_id agtype, recommendations agtype);

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY friend_recommendations;
```

### Q2: 如何处理大图数据导入？

**A**: 使用批量导入策略

```python
import psycopg2
import json

conn = psycopg2.connect("dbname=testdb user=postgres")
cur = conn.cursor()

# 批量导入节点
batch_size = 1000
nodes = [...]  # 你的节点数据

for i in range(0, len(nodes), batch_size):
    batch = nodes[i:i+batch_size]
    query = """
    SELECT * FROM cypher('social_network', $$
        UNWIND $batch AS node_data
        CREATE (n:Person)
        SET n = node_data
    $$, %s) AS (result agtype);
    """
    cur.execute(query, (json.dumps({'batch': batch}),))
    conn.commit()
    print(f"Imported {i+len(batch)} nodes")

cur.close()
conn.close()
```

### Q3: AGE支持图算法库吗？

**A**: AGE目前不像Neo4j GDS那样有专门的图算法库，但可以：

1. **自己实现**：使用Cypher实现常见算法
2. **使用PostgreSQL扩展**：如`pgrouting`（配合PostGIS）
3. **导出到Python**：使用NetworkX/igraph处理

```python
import psycopg2
import networkx as nx

# 从AGE导出到NetworkX
conn = psycopg2.connect("dbname=testdb")
cur = conn.cursor()

cur.execute("""
    SELECT * FROM cypher('social_network', $$
        MATCH (a)-[r]->(b)
        RETURN a.id, b.id
    $$) AS (source agtype, target agtype);
""")

G = nx.DiGraph()
for source, target in cur.fetchall():
    G.add_edge(source, target)

# 使用NetworkX算法
pagerank = nx.pagerank(G)
betweenness = nx.betweenness_centrality(G)

print("Top 10 by PageRank:", sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10])
```

### Q4: 如何调试慢查询？

**A**: 使用EXPLAIN ANALYZE

```sql
-- 开启详细日志
SET client_min_messages = DEBUG1;
SET log_statement = 'all';

-- 分析查询
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM cypher('social_network', $$
    MATCH (a:Person {name: 'Alice'})-[:FRIEND*2..3]->(friend)
    RETURN DISTINCT friend.name
$$) AS (name agtype);

-- 查看慢查询日志
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
WHERE query LIKE '%cypher%'
ORDER BY total_time DESC
LIMIT 10;
```

### Q5: AGE可以与其他PostgreSQL扩展一起使用吗？

**A**: 可以！AGE可以与PostGIS、TimescaleDB等扩展结合

```sql
-- 结合PostGIS进行空间图查询
CREATE EXTENSION postgis;

-- 为Person添加地理位置
ALTER TABLE social_network."Person"
ADD COLUMN location GEOMETRY(Point, 4326);

-- 混合查询：找附近的朋友
WITH nearby_users AS (
    SELECT properties->>'id' AS user_id
    FROM social_network."Person"
    WHERE ST_DWithin(
        location,
        ST_SetSRID(ST_MakePoint(116.4074, 39.9042), 4326),  -- 北京
        10000  -- 10km
    )
)
SELECT * FROM cypher('social_network', $$
    MATCH (me:Person {id: $my_id})-[:FRIEND]->(friend:Person)
    WHERE friend.id IN $nearby_ids
    RETURN friend.name, friend.city
$$, jsonb_build_object(
    'my_id', '1',
    'nearby_ids', (SELECT array_agg(user_id) FROM nearby_users)
)) AS (name agtype, city agtype);
```

---

## 📚 延伸阅读

### 官方资源

- [Apache AGE GitHub](https://github.com/apache/age)
- [Apache AGE Documentation](https://age.apache.org/docs/)
- [openCypher Specification](https://opencypher.org/)

### 推荐书籍

- 《Graph Databases》by Ian Robinson (O'Reilly)
- 《Neo4j in Action》by Aleksa Vukotic
- 《Practical Neo4j》by Greg Jordan

### 相关技术

- [Neo4j](https://neo4j.com/) - 最流行的图数据库
- [Amazon Neptune](https://aws.amazon.com/neptune/) - AWS托管图数据库
- [JanusGraph](https://janusgraph.org/) - 分布式图数据库

---

## ✅ 学习检查清单

完成本教程后，你应该能够：

- [ ] 理解图数据库的核心概念和应用场景
- [ ] 安装和配置Apache AGE
- [ ] 使用Cypher查询语言进行CRUD操作
- [ ] 设计和实现图数据模型
- [ ] 编写复杂的图遍历查询
- [ ] 实现常见的图算法（最短路径、中心性分析等）
- [ ] 优化图查询性能
- [ ] 在生产环境中部署和维护图数据库
- [ ] 理解AGE与Neo4j的区别

---

## 💡 下一步学习

1. **实践项目**：
   - 构建一个社交网络应用
   - 实现推荐系统
   - 开发知识图谱

2. **进阶主题**：
   - 图数据库分片和高可用
   - 大规模图数据处理
   - 图神经网络（GNN）

3. **相关课程**：
   - [PostgreSQL扩展开发完整指南](./【深入】PostgreSQL扩展开发完整实战指南.md)
   - [PostgreSQL高可用架构](../09-高可用/)

---

**文档维护**: 本文档会持续更新以反映Apache AGE的最新特性。
**反馈**: 如发现错误或有改进建议，请提交issue或PR。

**版本历史**:

- v1.0 (2025-01): 初始版本，覆盖AGE 1.5+核心特性
