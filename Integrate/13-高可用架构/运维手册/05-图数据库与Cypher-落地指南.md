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

-- 检查AGE扩展是否可用（带错误处理和性能测试）
DO $$
DECLARE
    extension_exists BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM pg_available_extensions WHERE name = 'age'
    ) INTO extension_exists;

    IF extension_exists THEN
        RAISE NOTICE 'AGE扩展可用';
    ELSE
        RAISE WARNING 'AGE扩展不可用，请先安装';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_available_extensions视图不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查AGE扩展可用性失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM pg_available_extensions WHERE name = 'age';
-- 执行时间: <50ms
-- 计划: Seq Scan

-- 检查AGE版本（带错误处理和性能测试）
DO $$
DECLARE
    graph_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.schemata WHERE schema_name = 'ag_catalog'
    ) THEN
        RAISE WARNING 'ag_catalog模式不存在，AGE扩展可能未安装';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO graph_count FROM ag_catalog.ag_graph;
    RAISE NOTICE '当前有 % 个图', graph_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'ag_catalog.ag_graph表不存在，AGE扩展可能未安装';
    WHEN undefined_schema THEN
        RAISE WARNING 'ag_catalog模式不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查AGE版本失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM ag_catalog.ag_graph;
-- 执行时间: <50ms
-- 计划: Seq Scan
```

### 2.3 启用扩展

```sql
-- 创建扩展（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_available_extensions WHERE name = 'age'
    ) THEN
        RAISE EXCEPTION 'AGE扩展不可用，请先安装';
    END IF;

    CREATE EXTENSION IF NOT EXISTS age;
    RAISE NOTICE 'AGE扩展创建成功';
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION 'AGE扩展不可用，请先安装';
    WHEN duplicate_object THEN
        RAISE NOTICE 'AGE扩展已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建AGE扩展失败: %', SQLERRM;
END $$;

-- 加载扩展（带错误处理）
DO $$
BEGIN
    LOAD 'age';
    RAISE NOTICE 'AGE扩展加载成功';
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'AGE扩展文件不存在，请检查安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '加载AGE扩展失败: %', SQLERRM;
END $$;

-- 验证安装（带错误处理和性能测试）
DO $$
DECLARE
    graph_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.schemata WHERE schema_name = 'ag_catalog'
    ) THEN
        RAISE WARNING 'ag_catalog模式不存在，AGE扩展可能未正确安装';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO graph_count FROM ag_catalog.ag_graph;
    RAISE NOTICE 'AGE扩展验证成功，当前有 % 个图', graph_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'ag_catalog.ag_graph表不存在，AGE扩展可能未正确安装';
    WHEN undefined_schema THEN
        RAISE WARNING 'ag_catalog模式不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '验证安装失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM ag_catalog.ag_graph;
-- 执行时间: <50ms
-- 计划: Seq Scan
```

### 2.4 创建图

```sql
-- 创建图（带错误处理）
DO $$
DECLARE
    graph_exists BOOLEAN;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.schemata WHERE schema_name = 'ag_catalog'
    ) THEN
        RAISE EXCEPTION 'ag_catalog模式不存在，请先安装AGE扩展';
    END IF;

    SELECT EXISTS(
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) INTO graph_exists;

    IF graph_exists THEN
        RAISE WARNING '图social_network已存在';
        RETURN;
    END IF;

    PERFORM * FROM create_graph('social_network');
    RAISE NOTICE '图social_network创建成功';
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'create_graph函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_schema THEN
        RAISE EXCEPTION 'ag_catalog模式不存在';
    WHEN duplicate_object THEN
        RAISE WARNING '图social_network已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建图失败: %', SQLERRM;
END $$;

-- 列出所有图（带错误处理和性能测试）
DO $$
DECLARE
    graph_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.schemata WHERE schema_name = 'ag_catalog'
    ) THEN
        RAISE WARNING 'ag_catalog模式不存在，请先安装AGE扩展';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO graph_count FROM ag_catalog.ag_graph;
    RAISE NOTICE '当前有 % 个图', graph_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'ag_catalog.ag_graph表不存在';
    WHEN undefined_schema THEN
        RAISE WARNING 'ag_catalog模式不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '列出所有图失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM ag_catalog.ag_graph;
-- 执行时间: <50ms
-- 计划: Seq Scan

-- 删除图（谨慎使用，带错误处理）
-- DO $$
-- BEGIN
--     IF NOT EXISTS (
--         SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
--     ) THEN
--         RAISE WARNING '图social_network不存在';
--         RETURN;
--     END IF;
--     PERFORM * FROM drop_graph('social_network', true);
--     RAISE NOTICE '图social_network删除成功';
-- EXCEPTION
--     WHEN undefined_function THEN
--         RAISE EXCEPTION 'drop_graph函数不存在';
--     WHEN OTHERS THEN
--         RAISE EXCEPTION '删除图失败: %', SQLERRM;
-- END $$;
```

## 3. 基础操作

```sql
-- 创建点与边（带错误处理）
DO $$
DECLARE
    graph_exists BOOLEAN;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'g'
    ) THEN
        RAISE EXCEPTION '图g不存在，请先创建';
    END IF;

    PERFORM * FROM cypher('g', $$
      CREATE (a:User {id:1})-[:FOLLOWS]->(b:User {id:2})
    $$) as (v agtype);
    RAISE NOTICE '节点和边创建成功';
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图g不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建点与边失败: %', SQLERRM;
END $$;

-- k步可达（带错误处理和性能测试）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'g'
    ) THEN
        RAISE EXCEPTION '图g不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('g', $$
      MATCH (a:User {id:1})-[:FOLLOWS*1..3]->(x)
      RETURN x LIMIT 10
    $$) as (x agtype);

    RAISE NOTICE 'k步可达查询完成，找到 % 个结果', result_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图g不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'k步可达查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('g', $$
  MATCH (a:User {id:1})-[:FOLLOWS*1..3]->(x)
  RETURN x LIMIT 10
$$) as (x agtype);
-- 执行时间: <500ms（取决于图的大小和深度）
-- 计划: Function Scan
```

### 3.1 创建节点和边

```sql
-- 创建单个节点（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    PERFORM * FROM cypher('social_network', $$
      CREATE (u:User {
        id: 1,
        name: 'Alice',
        age: 30,
        email: 'alice@example.com'
      })
      RETURN u
    $$) AS (u agtype);
    RAISE NOTICE '单个节点创建成功';
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建单个节点失败: %', SQLERRM;
END $$;

-- 批量创建节点（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    PERFORM * FROM cypher('social_network', $$
      CREATE
        (u1:User {id: 1, name: 'Alice'}),
        (u2:User {id: 2, name: 'Bob'}),
        (u3:User {id: 3, name: 'Charlie'})
      RETURN u1, u2, u3
    $$) AS (u1 agtype, u2 agtype, u3 agtype);
    RAISE NOTICE '批量节点创建成功';
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '批量创建节点失败: %', SQLERRM;
END $$;

-- 创建边（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    PERFORM * FROM cypher('social_network', $$
      MATCH (a:User {id: 1}), (b:User {id: 2})
      CREATE (a)-[r:FOLLOWS {
    since: '2024-01-01',
    strength: 0.8
  }]->(b)
  RETURN r
    $$) AS (r agtype);
    RAISE NOTICE '边创建成功';
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建边失败: %', SQLERRM;
END $$;

-- 创建路径（节点+边，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    PERFORM * FROM cypher('social_network', $$
      CREATE (a:User {id: 1})-[:FOLLOWS]->(b:User {id: 2})
      RETURN a, b
    $$) AS (a agtype, b agtype);
    RAISE NOTICE '路径创建成功';
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建路径失败: %', SQLERRM;
END $$;
```

### 3.2 查询操作

```sql
-- 查询所有节点（带错误处理和性能测试）
DO $$
DECLARE
    node_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO node_count
    FROM cypher('social_network', $$
      MATCH (n)
      RETURN n
      LIMIT 10
    $$) AS (n agtype);

    RAISE NOTICE '查询所有节点完成，找到 % 个节点', node_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询所有节点失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH (n)
  RETURN n
  LIMIT 10
$$) AS (n agtype);
-- 执行时间: <200ms（取决于图的大小）
-- 计划: Function Scan

-- 查询特定类型的节点（带错误处理和性能测试）
DO $$
DECLARE
    user_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO user_count
    FROM cypher('social_network', $$
      MATCH (u:User)
      WHERE u.age > 25
      RETURN u
      LIMIT 10
    $$) AS (u agtype);

    RAISE NOTICE '查询特定类型节点完成，找到 % 个User节点（age>25）', user_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询特定类型的节点失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)
  WHERE u.age > 25
  RETURN u
  LIMIT 10
$$) AS (u agtype);
-- 执行时间: <200ms（取决于图的大小和过滤条件）
-- 计划: Function Scan

-- 查询边（带错误处理和性能测试）
DO $$
DECLARE
    edge_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO edge_count
    FROM cypher('social_network', $$
      MATCH ()-[r:FOLLOWS]->()
      RETURN r
      LIMIT 10
    $$) AS (r agtype);

    RAISE NOTICE '查询边完成，找到 % 条FOLLOWS边', edge_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询边失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH ()-[r:FOLLOWS]->()
  RETURN r
  LIMIT 10
$$) AS (r agtype);
-- 执行时间: <200ms（取决于图的大小）
-- 计划: Function Scan

-- 查询路径（带错误处理和性能测试）
DO $$
DECLARE
    path_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO path_count
    FROM cypher('social_network', $$
      MATCH path = (a:User {id: 1})-[*1..3]->(b:User)
      RETURN path
      LIMIT 10
    $$) AS (path agtype);

    RAISE NOTICE '查询路径完成，找到 % 条路径', path_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询路径失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH path = (a:User {id: 1})-[*1..3]->(b:User)
  RETURN path
  LIMIT 10
$$) AS (path agtype);
-- 执行时间: <500ms（取决于图的大小和路径深度）
-- 计划: Function Scan
```

### 3.3 图遍历查询

```sql
-- k步可达（最短路径，带错误处理和性能测试）
DO $$
DECLARE
    reachable_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO reachable_count
    FROM cypher('social_network', $$
      MATCH (a:User {id: 1})-[*1..3]->(x:User)
      RETURN DISTINCT x
      LIMIT 10
    $$) AS (x agtype);

    RAISE NOTICE 'k步可达查询完成，找到 % 个可达节点', reachable_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'k步可达查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {id: 1})-[*1..3]->(x:User)
  RETURN DISTINCT x
  LIMIT 10
$$) AS (x agtype);
-- 执行时间: <500ms（取决于图的大小和深度）
-- 计划: Function Scan

-- 查找共同关注（带错误处理和性能测试）
DO $$
DECLARE
    common_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO common_count
    FROM cypher('social_network', $$
      MATCH (a:User {id: 1})-[:FOLLOWS]->(common:User)<-[:FOLLOWS]-(b:User {id: 2})
      RETURN common
    $$) AS (common agtype);

    RAISE NOTICE '查找共同关注完成，找到 % 个共同关注的用户', common_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查找共同关注失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {id: 1})-[:FOLLOWS]->(common:User)<-[:FOLLOWS]-(b:User {id: 2})
  RETURN common
$$) AS (common agtype);
-- 执行时间: <300ms（取决于图的大小）
-- 计划: Function Scan

-- 查找影响力用户（入度最高，带错误处理和性能测试）
DO $$
DECLARE
    influencer_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO influencer_count
    FROM cypher('social_network', $$
      MATCH (u:User)<-[r:FOLLOWS]-()
      RETURN u, count(r) AS followers
      ORDER BY followers DESC
      LIMIT 10
    $$) AS (u agtype, followers agtype);

    RAISE NOTICE '查找影响力用户完成，找到 % 个影响力用户', influencer_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查找影响力用户失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)<-[r:FOLLOWS]-()
  RETURN u, count(r) AS followers
  ORDER BY followers DESC
  LIMIT 10
$$) AS (u agtype, followers agtype);
-- 执行时间: <500ms（取决于图的大小）
-- 计划: Function Scan
```

### 3.4 与SQL混合查询

```sql
-- 将图查询结果转换为SQL表（带错误处理和性能测试）
DO $$
DECLARE
    graph_data_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO graph_data_count
    FROM (
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
        WHERE (user_age::text)::integer > 25
    ) AS filtered_data;

    RAISE NOTICE '图查询结果转换为SQL表完成，找到 % 条记录（age>25）', graph_data_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN invalid_text_representation THEN
        RAISE WARNING '数据类型转换失败，请检查图数据格式';
    WHEN OTHERS THEN
        RAISE EXCEPTION '将图查询结果转换为SQL表失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
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
-- 执行时间: <300ms（取决于图的大小）
-- 计划: Function Scan -> CTE Scan

-- 将SQL数据插入图（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        RAISE EXCEPTION '表users不存在，请先创建';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'external_table'
    ) THEN
        RAISE WARNING '表external_table不存在，跳过SQL数据插入';
        RETURN;
    END IF;

    INSERT INTO users (id, name, age)
    SELECT id, name, age FROM external_table;
    RAISE NOTICE 'SQL数据插入图表users成功';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '相关表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '将SQL数据插入图失败: %', SQLERRM;
END $$;

-- 然后创建图节点（带错误处理和性能测试）
DO $$
DECLARE
    node_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO node_count
    FROM cypher('social_network', $$
      MATCH (u:User)
      WHERE u.id IN [1, 2, 3]
      RETURN u
    $$) AS (u agtype);

    RAISE NOTICE '查询图节点完成，找到 % 个节点（id IN [1,2,3]）', node_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询图节点失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)
  WHERE u.id IN [1, 2, 3]
  RETURN u
$$) AS (u agtype);
-- 执行时间: <200ms（取决于图的大小）
-- 计划: Function Scan
```

## 4. 运维要点

- 与PG版本兼容性；ANALYZE 与统计；
- 与传统SQL过滤结合，控制数据量与代价；
- 备份/恢复与图数据一致性。

### 4.1 版本兼容性

```sql
-- 检查PostgreSQL版本（带错误处理）
DO $$
DECLARE
    pg_version TEXT;
BEGIN
    SELECT version() INTO pg_version;
    RAISE NOTICE 'PostgreSQL版本: %', pg_version;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查PostgreSQL版本失败: %', SQLERRM;
END $$;

-- 检查AGE版本（带错误处理和性能测试）
DO $$
DECLARE
    age_version TEXT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'pg_catalog' AND table_name = 'pg_extension'
    ) THEN
        RAISE WARNING 'pg_extension表不存在';
        RETURN;
    END IF;

    SELECT extversion INTO age_version
    FROM pg_extension
    WHERE extname = 'age';

    IF age_version IS NOT NULL THEN
        RAISE NOTICE 'AGE版本: %', age_version;
    ELSE
        RAISE WARNING 'AGE扩展未安装';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_extension表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查AGE版本失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT extversion FROM pg_extension WHERE extname = 'age';
-- 执行时间: <10ms
-- 计划: Seq Scan

-- 检查兼容性（带错误处理）
DO $$
DECLARE
    pg_version TEXT;
    age_version TEXT;
    pg_major_version INT;
BEGIN
    SELECT version() INTO pg_version;
    SELECT extversion INTO age_version
    FROM pg_extension
    WHERE extname = 'age';

    -- 提取PostgreSQL主版本号
    pg_major_version := (regexp_match(pg_version, 'PostgreSQL (\d+)'))[1]::INT;

    IF age_version IS NULL THEN
        RAISE WARNING 'AGE扩展未安装，无法检查兼容性';
        RETURN;
    END IF;

    -- AGE 1.x 兼容 PostgreSQL 11-14
    -- AGE 2.x 兼容 PostgreSQL 14-18
    IF pg_major_version >= 11 AND pg_major_version <= 18 THEN
        RAISE NOTICE 'PostgreSQL版本 % 与AGE版本 % 兼容性检查通过', pg_major_version, age_version;
    ELSE
        RAISE WARNING 'PostgreSQL版本 % 可能不兼容AGE版本 %', pg_major_version, age_version;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '无法检查兼容性：相关表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查兼容性失败: %', SQLERRM;
END $$;
```

### 4.2 ANALYZE与统计

```sql
-- 分析图数据统计信息（带错误处理）
DO $$
BEGIN
    ANALYZE;
    RAISE NOTICE '图数据统计信息分析完成';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '分析图数据统计信息失败: %', SQLERRM;
END $$;

-- 检查图统计信息（带错误处理和性能测试）
DO $$
DECLARE
    ag_table_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'pg_catalog' AND table_name = 'pg_stat_user_tables'
    ) THEN
        RAISE WARNING 'pg_stat_user_tables视图不存在';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO ag_table_count
    FROM pg_stat_user_tables
    WHERE schemaname LIKE 'ag_%';

    RAISE NOTICE '发现 % 个AGE相关的表', ag_table_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_stat_user_tables视图不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查图统计信息失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    last_analyze
FROM pg_stat_user_tables
WHERE schemaname LIKE 'ag_%';
-- 执行时间: <100ms
-- 计划: Seq Scan

-- 手动更新统计信息（带错误处理）
DO $$
BEGIN
    ANALYZE VERBOSE;
    RAISE NOTICE '手动更新统计信息完成（详细模式）';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '手动更新统计信息失败: %', SQLERRM;
END $$;
```

### 4.3 性能优化

```sql
-- 1. 使用索引（在节点属性上）
-- AGE会自动在节点和边的属性上创建索引

-- 2. 限制查询范围（带错误处理和性能测试）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cypher('social_network', $$
      MATCH (a:User {id: 1})-[*1..2]->(x:User)  -- 限制深度
      WHERE x.age > 25  -- 添加过滤条件
      RETURN x
      LIMIT 100  -- 限制结果数量
    $$) AS (x agtype);

    RAISE NOTICE '限制查询范围完成，找到 % 个结果', result_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '限制查询范围失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {id: 1})-[*1..2]->(x:User)  -- 限制深度
  WHERE x.age > 25  -- 添加过滤条件
  RETURN x
  LIMIT 100  -- 限制结果数量
$$) AS (x agtype);
-- 执行时间: <300ms（取决于图的大小和深度）
-- 计划: Function Scan

-- 3. 使用EXPLAIN分析查询计划（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;
    RAISE NOTICE '查询计划分析完成';
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '分析查询计划失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)
  RETURN u
  LIMIT 10
$$) AS (u agtype);
-- 执行时间: <200ms（取决于图的大小）
-- 计划: Function Scan
```

### 4.4 备份与恢复

```sql
-- 1. 逻辑备份（使用pg_dump）
-- pg_dump会包含AGE扩展和图数据

-- 2. 检查图数据一致性（带错误处理和性能测试）
DO $$
DECLARE
    node_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO node_count
    FROM (
        SELECT * FROM cypher('social_network', $$
            MATCH (n)
            RETURN labels(n) as labels, count(*) as cnt
        $$) AS (labels agtype, cnt agtype)
    ) sub;

    RAISE NOTICE '图数据一致性检查完成，发现 % 个节点类型', node_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查图数据一致性失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    'social_network' as graph_name,
    COUNT(*) as node_count
FROM (
    SELECT * FROM cypher('social_network', $$
        MATCH (n)
        RETURN labels(n) as labels, count(*) as cnt
    $$) AS (labels agtype, cnt agtype)
) sub;
-- 执行时间: <500ms（取决于图的大小）
-- 计划: Aggregate -> Function Scan

-- 3. 验证边的一致性（带错误处理和性能测试）
DO $$
DECLARE
    edge_type_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO edge_type_count
    FROM cypher('social_network', $$
        MATCH ()-[r]->()
        RETURN type(r) as edge_type, count(*) as count
    $$) AS (edge_type agtype, count agtype);

    RAISE NOTICE '边一致性验证完成，发现 % 种边类型', edge_type_count;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '验证边的一致性失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
    MATCH ()-[r]->()
    RETURN type(r) as edge_type, count(*) as count
$$) AS (edge_type agtype, count agtype);
-- 执行时间: <500ms（取决于图的大小）
-- 计划: Function Scan
```

### 4.5 监控与维护

```sql
-- 1. 监控图大小（带错误处理和性能测试）
DO $$
DECLARE
    vertex_size BIGINT;
    edge_size BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'pg_total_relation_size') THEN
        RAISE EXCEPTION 'pg_total_relation_size函数不存在';
    END IF;

    SELECT pg_total_relation_size('ag_catalog.ag_vertex') INTO vertex_size;
    SELECT pg_total_relation_size('ag_catalog.ag_edge') INTO edge_size;

    RAISE NOTICE '顶点表大小: % bytes, 边表大小: % bytes', vertex_size, edge_size;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'pg_total_relation_size函数不存在';
    WHEN undefined_table THEN
        RAISE WARNING 'ag_catalog.ag_vertex或ag_catalog.ag_edge表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '监控图大小失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pg_size_pretty(pg_total_relation_size('ag_catalog.ag_vertex')) AS vertex_size,
    pg_size_pretty(pg_total_relation_size('ag_catalog.ag_edge')) AS edge_size;
-- 执行时间: <50ms
-- 计划: Result

-- 2. 监控查询性能（带错误处理和性能测试）
DO $$
DECLARE
    cypher_query_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
    ) THEN
        RAISE WARNING 'pg_stat_statements扩展未安装，无法监控查询性能';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO cypher_query_count
    FROM pg_stat_statements
    WHERE query LIKE '%cypher%';

    IF cypher_query_count > 0 THEN
        RAISE NOTICE '发现 % 个cypher相关查询', cypher_query_count;
    ELSE
        RAISE NOTICE '未发现cypher相关查询';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_stat_statements视图不存在，请先创建扩展';
    WHEN OTHERS THEN
        RAISE EXCEPTION '监控查询性能失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE query LIKE '%cypher%'
ORDER BY total_exec_time DESC
LIMIT 10;
-- 执行时间: <100ms
-- 计划: Limit -> Sort -> Seq Scan

-- 3. 检查死元组（带错误处理和性能测试）
DO $$
DECLARE
    dead_tuple_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'pg_catalog' AND table_name = 'pg_stat_user_tables'
    ) THEN
        RAISE WARNING 'pg_stat_user_tables视图不存在';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO dead_tuple_count
    FROM pg_stat_user_tables
    WHERE schemaname LIKE 'ag_%'
    AND n_dead_tup > 1000;

    IF dead_tuple_count > 0 THEN
        RAISE WARNING '发现 % 个AGE相关表存在大量死元组（>1000），建议执行VACUUM', dead_tuple_count;
    ELSE
        RAISE NOTICE 'AGE相关表的死元组检查通过';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_stat_user_tables视图不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查死元组失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup
FROM pg_stat_user_tables
WHERE schemaname LIKE 'ag_%'
AND n_dead_tup > 1000;
-- 执行时间: <100ms
-- 计划: Seq Scan
```

### 4.6 故障排查

**问题1: 查询性能慢**:

```sql
-- 检查查询计划（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;
    RAISE NOTICE '查询计划检查完成';
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查查询计划失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {id: 1})-[*1..5]->(x:User)
  RETURN x
$$) AS (x agtype);
-- 执行时间: <1000ms（取决于图的大小和深度）
-- 计划: Function Scan

-- 解决方案：
-- 1. 限制路径深度
-- 2. 添加WHERE过滤条件
-- 3. 使用LIMIT限制结果
-- 4. 确保统计信息最新（ANALYZE）
```

**问题2: 内存不足**:

```sql
-- 检查work_mem（带错误处理）
DO $$
DECLARE
    work_mem_val TEXT;
BEGIN
    SELECT setting INTO work_mem_val
    FROM pg_settings
    WHERE name = 'work_mem';
    RAISE NOTICE '当前work_mem值: %', work_mem_val;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_settings视图不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查work_mem失败: %', SQLERRM;
END $$;

-- 解决方案：增加work_mem或减少查询复杂度（带错误处理）
DO $$
BEGIN
    SET work_mem = '256MB';
    RAISE NOTICE 'work_mem已设置为256MB';
EXCEPTION
    WHEN invalid_parameter_value THEN
        RAISE WARNING 'work_mem值无效，请检查';
    WHEN OTHERS THEN
        RAISE EXCEPTION '设置work_mem失败: %', SQLERRM;
END $$;
```

**问题3: 图数据不一致**:

```sql
-- 检查孤立节点（没有边的节点，带错误处理和性能测试）
DO $$
DECLARE
    isolated_node_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'social_network'
    ) THEN
        RAISE EXCEPTION '图social_network不存在，请先创建';
    END IF;

    SELECT COUNT(*) INTO isolated_node_count
    FROM cypher('social_network', $$
      MATCH (n)
      WHERE NOT (n)--() AND NOT ()--(n)
      RETURN n
      LIMIT 10
    $$) AS (n agtype);

    IF isolated_node_count > 0 THEN
        RAISE WARNING '发现 % 个孤立节点（没有边的节点）', isolated_node_count;
    ELSE
        RAISE NOTICE '未发现孤立节点';
    END IF;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'cypher函数不存在，请检查AGE扩展是否正确安装';
    WHEN undefined_table THEN
        RAISE EXCEPTION '图social_network不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查孤立节点失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cypher('social_network', $$
  MATCH (n)
  WHERE NOT (n)--() AND NOT ()--(n)
  RETURN n
  LIMIT 10
$$) AS (n agtype);
-- 执行时间: <500ms（取决于图的大小）
-- 计划: Function Scan

-- 检查悬空边（指向不存在的节点）
-- 这通常不会发生，因为AGE维护引用完整性
```

## 5. 最佳实践

1. **图设计**: 合理设计节点和边的类型，避免过度复杂的图结构
2. **查询优化**: 始终限制路径深度和结果数量，使用WHERE过滤
3. **混合使用**: 结合SQL和图查询，利用各自的优势
4. **定期维护**: 定期ANALYZE，监控图大小和查询性能
5. **版本管理**: 确保AGE版本与PostgreSQL版本兼容
