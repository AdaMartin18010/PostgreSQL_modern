-- PostgreSQL 图与递归查询示例
-- 版本：PostgreSQL 12+ with Apache AGE extension
-- 用途：图数据库查询、递归关系分析、社交网络分析
-- 执行环境：需要安装Apache AGE扩展

-- =====================
-- 1. 环境准备
-- =====================

-- 1.1 安装Apache AGE扩展
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';

-- 1.2 验证扩展安装
SELECT extname, extversion FROM pg_extension WHERE extname = 'age';

-- =====================
-- 2. 图数据库基础操作
-- =====================

-- 2.1 创建图
SELECT * FROM create_graph('social_network');

-- 2.2 创建节点
-- 创建用户节点
SELECT * FROM cypher('social_network', $$
  CREATE (alice:User {id: 1, name: 'Alice', age: 25, city: 'New York'})
  CREATE (bob:User {id: 2, name: 'Bob', age: 30, city: 'San Francisco'})
  CREATE (charlie:User {id: 3, name: 'Charlie', age: 28, city: 'New York'})
  CREATE (diana:User {id: 4, name: 'Diana', age: 32, city: 'Los Angeles'})
  CREATE (eve:User {id: 5, name: 'Eve', age: 27, city: 'Chicago'})
$$) as (v agtype);

-- 创建公司节点
SELECT * FROM cypher('social_network', $$
  CREATE (techcorp:Company {id: 101, name: 'TechCorp', industry: 'Technology'})
  CREATE (financeinc:Company {id: 102, name: 'FinanceInc', industry: 'Finance'})
  CREATE (startupxyz:Company {id: 103, name: 'StartupXYZ', industry: 'Technology'})
$$) as (v agtype);

-- 2.3 创建关系
-- 创建用户关系
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {name: 'Alice'}), (b:User {name: 'Bob'})
  CREATE (a)-[:FOLLOWS {since: '2023-01-15', strength: 0.8}]->(b)
$$) as (v agtype);

SELECT * FROM cypher('social_network', $$
  MATCH (a:User {name: 'Alice'}), (c:User {name: 'Charlie'})
  CREATE (a)-[:FOLLOWS {since: '2023-02-20', strength: 0.9}]->(c)
$$) as (v agtype);

SELECT * FROM cypher('social_network', $$
  MATCH (b:User {name: 'Bob'}), (d:User {name: 'Diana'})
  CREATE (b)-[:FOLLOWS {since: '2023-03-10', strength: 0.7}]->(d)
$$) as (v agtype);

SELECT * FROM cypher('social_network', $$
  MATCH (c:User {name: 'Charlie'}), (e:User {name: 'Eve'})
  CREATE (c)-[:FOLLOWS {since: '2023-04-05', strength: 0.6}]->(e)
$$) as (v agtype);

-- 创建用户-公司关系
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {name: 'Alice'}), (tc:Company {name: 'TechCorp'})
  CREATE (a)-[:WORKS_AT {position: 'Software Engineer', start_date: '2022-06-01'}]->(tc)
$$) as (v agtype);

SELECT * FROM cypher('social_network', $$
  MATCH (b:User {name: 'Bob'}), (fi:Company {name: 'FinanceInc'})
  CREATE (b)-[:WORKS_AT {position: 'Data Analyst', start_date: '2021-09-15'}]->(fi)
$$) as (v agtype);

-- =====================
-- 3. 基础图查询
-- =====================

-- 3.1 查询所有用户
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)
  RETURN u.name, u.age, u.city
  ORDER BY u.age
$$) as (name agtype, age agtype, city agtype);

-- 3.2 查询特定用户的朋友
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {name: 'Alice'})-[:FOLLOWS]->(friend:User)
  RETURN friend.name, friend.age, friend.city
$$) as (name agtype, age agtype, city agtype);

-- 3.3 查询用户的工作信息
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)-[r:WORKS_AT]->(c:Company)
  RETURN u.name, c.name, r.position, r.start_date
$$) as (user_name agtype, company_name agtype, position agtype, start_date agtype);

-- =====================
-- 4. 路径查询
-- =====================

-- 4.1 查找两个用户之间的路径
SELECT * FROM cypher('social_network', $$
  MATCH path = (a:User {name: 'Alice'})-[:FOLLOWS*1..3]->(b:User {name: 'Eve'})
  RETURN path
  LIMIT 5
$$) as (path agtype);

-- 4.2 查找最短路径
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {name: 'Alice'}), (b:User {name: 'Eve'})
  MATCH path = shortestPath((a)-[:FOLLOWS*]-(b))
  RETURN path
$$) as (path agtype);

-- 4.3 查找所有路径（限制深度）
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {name: 'Alice'}), (b:User {name: 'Eve'})
  MATCH path = (a)-[:FOLLOWS*1..2]-(b)
  RETURN path, length(path) as path_length
  ORDER BY path_length
$$) as (path agtype, path_length agtype);

-- =====================
-- 5. 聚合查询
-- =====================

-- 5.1 统计每个用户的关注者数量
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)<-[:FOLLOWS]-(follower:User)
  RETURN u.name, count(follower) as follower_count
  ORDER BY follower_count DESC
$$) as (name agtype, follower_count agtype);

-- 5.2 统计每个公司的员工数量
SELECT * FROM cypher('social_network', $$
  MATCH (c:Company)<-[:WORKS_AT]-(employee:User)
  RETURN c.name, c.industry, count(employee) as employee_count
  ORDER BY employee_count DESC
$$) as (name agtype, industry agtype, employee_count agtype);

-- 5.3 查找最受欢迎的用户（被关注最多）
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)<-[:FOLLOWS]-(follower:User)
  WITH u, count(follower) as follower_count
  ORDER BY follower_count DESC
  LIMIT 3
  RETURN u.name, u.age, u.city, follower_count
$$) as (name agtype, age agtype, city agtype, follower_count agtype);

-- =====================
-- 6. 复杂图分析
-- =====================

-- 6.1 查找共同关注者
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {name: 'Alice'})<-[:FOLLOWS]-(common:User)-[:FOLLOWS]->(b:User {name: 'Bob'})
  RETURN common.name, common.age
  ORDER BY common.age
$$) as (name agtype, age agtype);

-- 6.2 查找三角关系（A关注B，B关注C，C关注A）
SELECT * FROM cypher('social_network', $$
  MATCH (a:User)-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User)-[:FOLLOWS]->(a)
  RETURN a.name, b.name, c.name
$$) as (user_a agtype, user_b agtype, user_c agtype);

-- 6.3 查找影响力用户（关注者数量多且关注的人也多的用户）
SELECT * FROM cypher('social_network', $$
  MATCH (u:User)
  OPTIONAL MATCH (u)<-[:FOLLOWS]-(follower:User)
  OPTIONAL MATCH (u)-[:FOLLOWS]->(following:User)
  WITH u, count(DISTINCT follower) as followers, count(DISTINCT following) as following
  WHERE followers > 0 AND following > 0
  RETURN u.name, followers, following, (followers + following) as total_connections
  ORDER BY total_connections DESC
$$) as (name agtype, followers agtype, following agtype, total_connections agtype);

-- =====================
-- 7. 递归CTE图查询
-- =====================

-- 7.1 创建传统关系表结构
CREATE TABLE IF NOT EXISTS edges (
    id serial PRIMARY KEY,
    src int NOT NULL,
    dst int NOT NULL,
    weight decimal(3,2) DEFAULT 1.0,
    created_at timestamptz DEFAULT now()
);

-- 插入边数据
INSERT INTO edges (src, dst, weight) VALUES
(1, 2, 0.8),
(1, 3, 0.9),
(2, 4, 0.7),
(3, 5, 0.6),
(4, 6, 0.5),
(5, 6, 0.4);

-- 7.2 递归路径查找
WITH RECURSIVE reachable_nodes(id, depth, path, total_weight) AS (
    -- 基础查询：从节点1开始
    SELECT 
        1 as id, 
        0 as depth, 
        ARRAY[1] as path, 
        0.0 as total_weight
    UNION ALL
    -- 递归查询：扩展路径
    SELECT 
        e.dst, 
        r.depth + 1, 
        r.path || e.dst,
        r.total_weight + e.weight
    FROM reachable_nodes r
    JOIN edges e ON e.src = r.id
    WHERE r.depth < 3 
      AND NOT e.dst = ANY(r.path)  -- 避免循环
)
SELECT 
    id,
    depth,
    path,
    total_weight,
    array_length(path, 1) as path_length
FROM reachable_nodes
ORDER BY depth, total_weight DESC;

-- 7.3 查找所有可达节点
WITH RECURSIVE all_reachable AS (
    -- 基础查询
    SELECT 
        1 as start_node,
        1 as current_node,
        0 as depth,
        ARRAY[1] as path
    UNION ALL
    -- 递归查询
    SELECT 
        ar.start_node,
        e.dst,
        ar.depth + 1,
        ar.path || e.dst
    FROM all_reachable ar
    JOIN edges e ON e.src = ar.current_node
    WHERE ar.depth < 5 
      AND NOT e.dst = ANY(ar.path)
)
SELECT 
    start_node,
    current_node,
    depth,
    path
FROM all_reachable
WHERE current_node != start_node
ORDER BY start_node, depth, current_node;

-- =====================
-- 8. 图算法实现
-- =====================

-- 8.1 度中心性计算
WITH node_degrees AS (
    SELECT 
        src as node_id,
        'outgoing' as degree_type,
        count(*) as degree
    FROM edges
    GROUP BY src
    UNION ALL
    SELECT 
        dst as node_id,
        'incoming' as degree_type,
        count(*) as degree
    FROM edges
    GROUP BY dst
)
SELECT 
    node_id,
    sum(CASE WHEN degree_type = 'outgoing' THEN degree ELSE 0 END) as out_degree,
    sum(CASE WHEN degree_type = 'incoming' THEN degree ELSE 0 END) as in_degree,
    sum(degree) as total_degree
FROM node_degrees
GROUP BY node_id
ORDER BY total_degree DESC;

-- 8.2 简单PageRank算法（迭代版本）
CREATE OR REPLACE FUNCTION calculate_pagerank(
    damping_factor decimal DEFAULT 0.85,
    max_iterations int DEFAULT 10,
    tolerance decimal DEFAULT 0.001
)
RETURNS TABLE(node_id int, pagerank decimal) AS $$
DECLARE
    iteration int := 0;
    total_nodes int;
    converged boolean := false;
BEGIN
    -- 获取总节点数
    SELECT count(DISTINCT node) INTO total_nodes
    FROM (
        SELECT src as node FROM edges
        UNION
        SELECT dst as node FROM edges
    ) all_nodes;
    
    -- 创建临时表存储PageRank值
    CREATE TEMP TABLE pagerank_values (
        node_id int PRIMARY KEY,
        pr_value decimal DEFAULT 1.0 / total_nodes,
        new_pr_value decimal DEFAULT 0.0
    );
    
    -- 初始化所有节点
    INSERT INTO pagerank_values (node_id)
    SELECT DISTINCT node
    FROM (
        SELECT src as node FROM edges
        UNION
        SELECT dst as node FROM edges
    ) all_nodes;
    
    -- 迭代计算
    WHILE iteration < max_iterations AND NOT converged LOOP
        iteration := iteration + 1;
        
        -- 计算新的PageRank值
        UPDATE pagerank_values SET new_pr_value = (
            SELECT (1 - damping_factor) / total_nodes + 
                   damping_factor * sum(pr.pr_value / out_degrees.out_degree)
            FROM pagerank_values pr
            JOIN (
                SELECT src, count(*) as out_degree
                FROM edges
                GROUP BY src
            ) out_degrees ON out_degrees.src = pr.node_id
            JOIN edges e ON e.dst = pagerank_values.node_id AND e.src = pr.node_id
        );
        
        -- 检查收敛性
        SELECT NOT EXISTS (
            SELECT 1 FROM pagerank_values 
            WHERE abs(pr_value - new_pr_value) > tolerance
        ) INTO converged;
        
        -- 更新PageRank值
        UPDATE pagerank_values SET pr_value = new_pr_value;
    END LOOP;
    
    -- 返回结果
    RETURN QUERY
    SELECT pv.node_id, pv.pr_value
    FROM pagerank_values pv
    ORDER BY pv.pr_value DESC;
    
    -- 清理临时表
    DROP TABLE pagerank_values;
END;
$$ LANGUAGE plpgsql;

-- 执行PageRank计算
SELECT * FROM calculate_pagerank();

-- =====================
-- 9. 图数据管理
-- =====================

-- 9.1 图数据备份
-- 导出节点数据
SELECT * FROM cypher('social_network', $$
  MATCH (n)
  RETURN n
$$) as (node agtype);

-- 导出关系数据
SELECT * FROM cypher('social_network', $$
  MATCH (a)-[r]->(b)
  RETURN a, r, b
$$) as (start_node agtype, relationship agtype, end_node agtype);

-- 9.2 图数据清理
-- 删除特定节点及其关系
SELECT * FROM cypher('social_network', $$
  MATCH (u:User {name: 'Eve'})
  DETACH DELETE u
$$) as (result agtype);

-- 删除特定关系
SELECT * FROM cypher('social_network', $$
  MATCH (a:User {name: 'Alice'})-[r:FOLLOWS]->(b:User {name: 'Bob'})
  DELETE r
$$) as (result agtype);

-- 9.3 图数据验证
-- 检查孤立节点
SELECT * FROM cypher('social_network', $$
  MATCH (n)
  WHERE NOT (n)--() AND NOT ()--(n)
  RETURN n
$$) as (isolated_node agtype);

-- 检查自环
SELECT * FROM cypher('social_network', $$
  MATCH (a)-[r]->(a)
  RETURN a, r
$$) as (node agtype, self_loop agtype);


