# 图数据库理论

> **创建日期**: 2025-12-04
> **理论领域**: 图数据库 + ACID + 事务

---

## 📚 文档列表

### 核心文档

1. **[Apache AGE与ACID](./Apache-AGE与ACID.md)** ⭐ 推荐
   - 图数据库的ACID挑战
   - 图遍历的快照一致性
   - 图更新的原子性
   - 图算法与事务
   - 5个形式化定理

---

## 🎯 核心理论

### 1. 图操作原子性

**定理**: Apache AGE中的图操作（节点/边创建、删除）满足ACID原子性。

```cypher
BEGIN;

CREATE (u:User {name: 'Alice'});
MATCH (u:User {name: 'Alice'}), (friends:User)
WHERE friends.name IN ['Bob', 'Charlie']
CREATE (u)-[:KNOWS]->(friends);

COMMIT;
-- 要么全部成功，要么全部回滚
```

---

### 2. 图遍历快照一致性

**定理**: 在快照隔离下，图遍历看到一致的图结构。

```cypher
-- 事务T1
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

MATCH path = (a:User)-[:KNOWS*2..3]->(b:User)
WHERE a.id = 123
RETURN path;

-- 多次执行看到相同的路径集合
-- 即使并发有图结构修改
```

---

### 3. 图查询隔离性

**定理**: 在REPEATABLE READ隔离级别下，图查询不会出现幻读。

```
快照隔离保证:
├─ 事务开始时获取快照S
├─ 所有查询基于S
├─ 新增/删除的节点/边不可见
└─ 查询结果可重复
```

---

## 🔬 应用场景

### 场景1: 社交网络

```cypher
-- 好友推荐（ACID事务）
BEGIN;

MATCH (u:User {id: 123})-[:KNOWS]->(friend)-[:KNOWS]->(fof)
WHERE NOT (u)-[:KNOWS]->(fof)
  AND fof.id <> 123
WITH fof, COUNT(*) AS mutual_friends
ORDER BY mutual_friends DESC
LIMIT 10
CREATE (u)-[:RECOMMEND]->(fof);

COMMIT;
```

**ACID保证**:

- ✅ 推荐列表基于一致图结构
- ✅ 批量创建边原子性
- ✅ 并发推荐不冲突

---

### 场景2: 金融反欺诈

```cypher
-- 团伙检测（需要ACID）
BEGIN;

MATCH (a:Account)-[:TRANSFER*1..3]->(b:Account)
WHERE a.suspicious = true
WITH b, COUNT(*) AS connections
WHERE connections >= 3
SET b.risk_level = 'HIGH';

COMMIT;
```

**ACID重要性**:

- ✅ 遍历结果准确
- ✅ 风险标记原子
- ✅ 不会漏检或误检

---

### 场景3: 知识图谱问答

```python
# KBQA: 知识图谱推理

def kbqa_with_acid(question):
    """
    在ACID事务中执行图推理
    """
    with conn.begin():  # ACID事务
        # 1. 实体识别
        entities = extract_entities(question)

        # 2. 图遍历推理
        cypher_query = generate_cypher(question, entities)
        results = execute_cypher(cypher_query)

        # 3. 答案生成
        answer = generate_answer(results)

        return answer

# ACID保证推理过程的一致性
```

---

## 📊 性能模型

```
图遍历延迟 = T_index + T_traverse + T_mvcc

T_traverse 分解:
├─ 节点访问: O(V) * T_node
├─ 边遍历: O(E) * T_edge
└─ MVCC检查: O(V+E) * T_check

MVCC开销占比:
├─ 短路径: 10-20%
├─ 中等路径: 20-40%
└─ 长路径: 30-50%

优化:
├─ 限制路径长度
├─ 索引优化
└─ 及时VACUUM
```

---

## 🆚 Apache AGE vs Neo4j

| 维度 | Apache AGE | Neo4j |
|------|------------|-------|
| **ACID** | 完整PostgreSQL ACID | 完整ACID |
| **隔离级别** | 4种（RU/RC/RR/S） | 2种（RC/S） |
| **MVCC** | ✅ 完整支持 | ❌ 基于锁 |
| **并发读写** | ✅ 读不阻塞写 | ⚠️ 可能阻塞 |
| **快照隔离** | ✅ 天然支持 | ⚠️ 需额外配置 |
| **CAP** | CP（强一致性） | CP（强一致性） |

**结论**: Apache AGE在ACID和并发性方面更优。

---

## 📖 快速开始

### 1. 理论学习

阅读顺序:

1. [Apache AGE与ACID](./Apache-AGE与ACID.md) - 完整理论

### 2. 实践应用

参考案例:

1. [知识图谱问答系统](../../../DataBaseTheory/19-场景案例库/08-知识图谱问答系统/)
2. [金融反欺诈系统](../../../DataBaseTheory/19-场景案例库/10-金融反欺诈系统/)
3. [Apache AGE完整指南](../../../../docs/03-KnowledgeGraph/01-Apache-AGE完整深化指南-v2.md)

---

## 🔗 相关资源

- **Apache AGE文档**: <https://age.apache.org/>
- **Cypher查询语言**: [../../../../docs/03-KnowledgeGraph/01-Apache-AGE完整深化指南-v2.md#cypher查询语言](../../../../docs/03-KnowledgeGraph/01-Apache-AGE完整深化指南-v2.md)
- **图算法**: [../../../../docs/03-KnowledgeGraph/01-Apache-AGE完整深化指南-v2.md#图算法实现](../../../../docs/03-KnowledgeGraph/01-Apache-AGE完整深化指南-v2.md)

---

**返回**: [理论基础首页](../README.md) | [MVCC-ACID-CAP主页](../../README.md)
