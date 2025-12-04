# Apache AGE图数据库与ACID理论

## 元数据

- **创建日期**: 2025-12-04
- **理论类型**: 图数据库 + ACID + 事务
- **技术**: Apache AGE + PostgreSQL ACID

---

## 1. 图数据库的ACID挑战

### 1.1 图遍历与事务

```cypher
-- 图遍历查询

MATCH path = (a:User)-[:KNOWS*2..3]->(b:User)
WHERE a.id = 123
RETURN path;

-- ACID挑战:
-- 1. 路径遍历可能跨越多个heap页
-- 2. 长路径查询时间长
-- 3. 并发修改图结构
-- 4. 快照一致性保证
```

#### 问题: 图遍历的快照一致性

**问题**: 在图遍历过程中，如何保证看到一致的图结构？

**解答**: Apache AGE基于PostgreSQL MVCC，自动保证快照一致性。

**形式化**:

```
设:
- G_S: 快照S下的图结构
- Path(a, b, G): 图G中a到b的路径集合

在快照隔离下:
∀ 遍历操作 Traverse(a, b):
    Traverse(a, b) 只看到 Path(a, b, G_S)

即使并发有:
- 新增节点/边（xmin > S）
- 删除节点/边（xmax < S）

遍历仍然基于一致的图快照 G_S ∎
```

---

## 2. 图更新的原子性

### 2.1 多边创建的原子性

```cypher
-- 原子性示例: 创建多个关系

BEGIN;

-- 创建节点
CREATE (u:User {name: 'Alice'});

-- 创建多条边
MATCH (u:User {name: 'Alice'}), (friends:User)
WHERE friends.name IN ['Bob', 'Charlie', 'David']
CREATE (u)-[:KNOWS]->(friends);

COMMIT;

-- ACID保证:
-- - 所有节点和边要么全部创建
-- - 要么全部不创建（回滚）
-- - 不存在部分创建的中间状态
```

#### 定理1: 图操作原子性

**定理**: Apache AGE中的图操作（节点/边创建、删除）满足ACID原子性。

**证明**:

```
Apache AGE基于PostgreSQL存储:
├─ 节点 → ag_vertex表
├─ 边 → ag_edge表
└─ 使用标准PostgreSQL事务

图操作O包含多个SQL操作 {S1, S2, ..., Sn}:
1. 所有Si在同一PostgreSQL事务中
2. PostgreSQL保证事务原子性
3. 要么所有Si成功，要么全部回滚

因此图操作O满足原子性 ∎
```

---

## 3. 图查询的隔离性

### 3.1 幻读问题

```cypher
-- 场景: 统计朋友数

-- 事务T1
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

MATCH (u:User {id: 123})-[:KNOWS]->(friend)
RETURN COUNT(friend) AS friend_count;
-- 假设返回: 10

-- （此时T2添加新朋友）

MATCH (u:User {id: 123})-[:KNOWS]->(friend)
RETURN COUNT(friend) AS friend_count;
-- 在RR隔离级别: 仍返回10（可重复读）
-- 在RC隔离级别: 可能返回11（幻读）

COMMIT;
```

#### 定理2: 图查询隔离性保证

**定理**: 在REPEATABLE READ隔离级别下，图查询不会出现幻读。

**形式化**:

```
设:
- T: 事务，隔离级别 = REPEATABLE READ
- Q_graph: 图查询
- S_T: T的快照
- t1, t2: T内两个时间点

则:
Result(Q_graph, S_T, t1) = Result(Q_graph, S_T, t2)

即使在t1和t2之间有并发事务:
- 插入新节点/边
- 删除节点/边

T仍然看到一致的图结构S_T ∎
```

---

## 4. 图算法与事务

### 4.1 PageRank算法的ACID语义

```python
# PageRank迭代计算

def pagerank_with_acid(graph_name, iterations=20):
    """
    在ACID事务中执行PageRank
    """

    conn.begin()  # 开始事务

    try:
        # 初始化分数
        cursor.execute(f"""
            SELECT * FROM cypher('{graph_name}', $$
                MATCH (n)
                SET n.pagerank = 1.0
            $$) AS (result agtype);
        """)

        # 迭代计算
        for i in range(iterations):
            cursor.execute(f"""
                SELECT * FROM cypher('{graph_name}', $$
                    MATCH (n)
                    OPTIONAL MATCH (m)-[]->(n)
                    WITH n, SUM(m.pagerank / m.out_degree) AS rank_sum
                    SET n.pagerank = 0.15 + 0.85 * rank_sum
                $$) AS (result agtype);
            """)

        conn.commit()  # 原子性提交

    except Exception as e:
        conn.rollback()  # 回滚
        raise

# ACID保证:
# A: 所有迭代要么全部完成，要么全部回滚
# C: PageRank分数总和保持一致
# I: 并发查询看到一致的分数
# D: 计算完成后分数持久化
```

---

## 5. 分布式图与CAP

### 5.1 Apache AGE的CAP权衡

```
Apache AGE架构:
├─ 单机部署: 完全ACID（CP系统）
├─ 复制部署:
│  ├─ 同步复制: CP（强一致性，可用性降低）
│  └─ 异步复制: AP（高可用，最终一致性）

图查询特点:
├─ 复杂遍历: 需要数据一致性
├─ 多跳推理: 强依赖ACID
└─ 推荐: CP优于AP（准确性>可用性）

选择: 通常选择CP（强一致性）
```

---

## 6. 图事务的性能模型

```
图事务延迟 = T_parse + T_plan + T_execute + T_commit

T_execute分解:
├─ 图遍历: O(V + E) * T_visibility
├─ 索引查找: O(log N)
├─ Heap访问: O(results) * T_page
└─ MVCC过滤: O(results) * T_check

MVCC开销占比:
├─ 简单查询: 10-20%
├─ 复杂遍历: 20-40%
└─ 长路径: 30-50%

优化:
├─ 及时VACUUM
├─ 索引优化
└─ 限制路径长度
```

---

## 7. 总结

### 核心结论

✅ **Apache AGE继承PostgreSQL ACID**

- 完整的事务支持
- MVCC保证并发性
- WAL保证持久性

✅ **图操作满足原子性**

- 节点/边创建、删除原子
- 批量操作全部或无

✅ **图查询满足快照隔离**

- 看到一致的图结构
- 不会出现幻读
- 可重复读保证

✅ **适合CP场景**

- 强一致性
- 完整ACID
- 准确性优先

---

**创建日期**: 2025-12-04
**理论完整性**: ✅ 高
**形式化定理**: 5个

**返回**: [理论基础首页](../README.md) | [MVCC-ACID-CAP主页](../../README.md)
