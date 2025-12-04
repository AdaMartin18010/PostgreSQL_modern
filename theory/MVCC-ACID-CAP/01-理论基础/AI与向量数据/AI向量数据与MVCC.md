# AI向量数据与MVCC理论整合

## 元数据

- **创建日期**: 2025-12-04
- **理论类型**: 向量数据 + MVCC + 并发控制
- **技术**: pgvector + MVCC

---

## 1. 向量数据的MVCC特性

### 1.1 向量更新与可见性

```sql
-- 向量数据的MVCC更新

-- 场景: 用户兴趣向量更新
BEGIN;

UPDATE user_embeddings
SET embedding = new_vector,
    updated_at = CURRENT_TIMESTAMP
WHERE user_id = 123;

-- MVCC保证:
-- 1. 其他事务仍能看到旧向量
-- 2. 更新不阻塞读取
-- 3. 提交后新向量才可见

COMMIT;
```

#### 定理1: 向量更新原子性

**定理**: 向量列的更新操作满足MVCC原子性。

**证明**:

```
设向量更新操作 U: V_old → V_new

根据MVCC原理:
1. 更新创建新版本元组 t_new
2. t_old 保留, xmax = current_xid
3. t_new 创建, xmin = current_xid

可见性规则:
- 未提交: 只有当前事务看到 t_new
- 已提交: 所有后续事务看到 t_new
- 并发事务: 继续看到 t_old

因此向量更新满足原子性: All or Nothing ∎
```

---

### 1.2 向量检索与快照隔离

```sql
-- 向量相似度搜索的快照隔离

-- 事务T1: 相似度搜索
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

SELECT
    id,
    content,
    1 - (embedding <=> query_vector) AS similarity
FROM documents
ORDER BY embedding <=> query_vector
LIMIT 10;

-- 在整个事务期间:
-- - 看到一致的数据快照
-- - 不受其他事务的向量更新影响
-- - 保证可重复读

COMMIT;
```

#### 定理2: 向量检索快照一致性

**定理**: 在可重复读隔离级别下，向量相似度搜索看到一致的数据快照。

**形式化**:

```
设快照 S_T 为事务 T 开始时的数据状态
设查询 Q_vec(v) 为向量相似度搜索

对于事务 T 中的两次查询 Q_vec(v)_t1 和 Q_vec(v)_t2:
    Result(Q_vec(v)_t1, S_T) = Result(Q_vec(v)_t2, S_T)

即: 相同查询在同一快照下返回相同结果 ∎
```

---

## 2. pgvector索引与MVCC

### 2.1 HNSW索引的MVCC行为

```sql
-- HNSW索引创建
CREATE INDEX idx_doc_embedding
ON documents
USING hnsw (embedding vector_cosine_ops);

-- MVCC特性:
-- 1. 索引条目包含tuple版本信息
-- 2. 查询时过滤不可见版本
-- 3. VACUUM清理死亡索引条目
```

#### 索引可见性规则

**规则**: HNSW索引条目遵循与heap tuple相同的可见性规则。

```
索引条目 (key, tid):
├─ key: 向量值（或哈希）
└─ tid: heap tuple标识符 (ctid)

查询时:
1. 从索引获取候选 tid 列表
2. 检查 heap tuple 可见性
3. 过滤不可见元组
4. 返回可见结果

可见性检查:
- xmin 已提交 AND xmin < snapshot_xid
- xmax 未提交 OR xmax >= snapshot_xid
```

---

### 2.2 并发插入与索引更新

```sql
-- 场景: 并发插入带向量的文档

-- 事务T1
BEGIN;
INSERT INTO documents (content, embedding)
VALUES ('doc1', vector1);
-- MVCC: 创建xmin=T1的元组
COMMIT;

-- 事务T2（并发）
BEGIN;
INSERT INTO documents (content, embedding)
VALUES ('doc2', vector2);
-- MVCC: 创建xmin=T2的元组
-- 不阻塞T1
COMMIT;

-- HNSW索引更新:
-- - 两个插入并发构建索引
-- - 使用乐观并发控制
-- - 冲突时重试
```

#### 定理3: 向量索引并发插入不阻塞

**定理**: 在MVCC下，向量索引的并发插入操作不会相互阻塞（除非页分裂）。

**证明**:

```
HNSW索引更新流程:
1. 查找插入位置（读操作，不加锁）
2. 创建新索引条目（乐观插入）
3. 链接到现有图结构（CAS操作）

并发插入T1、T2:
- T1插入v1 到层L1
- T2插入v2 到层L2
- 如果 L1 ≠ L2: 完全不冲突
- 如果 L1 = L2: 仅在同一页时有冲突

冲突概率: P = 1 / (页数 * 层数) << 1

因此并发插入基本不阻塞 ∎
```

---

## 3. 向量更新与HOT

### 3.1 HOT优化对向量列的影响

```sql
-- HOT (Heap-Only Tuple) 更新

-- 场景1: 更新非向量列（可HOT优化）
UPDATE documents
SET title = 'new title'
WHERE id = 123;
-- ✅ HOT优化: 索引不更新

-- 场景2: 更新向量列（不能HOT）
UPDATE documents
SET embedding = new_vector
WHERE id = 123;
-- ❌ 非HOT: HNSW索引必须更新
```

#### 性能影响分析

```
向量列HOT限制:
├─ 原因: 向量值变化 → 索引必须更新
├─ 影响: 更新开销增大
└─ 优化: 减少向量更新频率

最佳实践:
├─ 向量计算离线化
├─ 批量更新
└─ 使用单独的向量表
```

---

## 4. 向量检索的并发控制

### 4.1 MVCC在向量检索中的应用

```python
# 向量相似度搜索的MVCC行为

def vector_search_with_mvcc(query_vector, snapshot_xid):
    """
    向量检索的MVCC流程

    1. HNSW索引搜索阶段（不考虑可见性）
    2. Heap访问阶段（应用MVCC可见性）
    """

    # 阶段1: HNSW搜索（获取候选）
    candidate_tids = hnsw_search(query_vector, ef_search=40)

    # 阶段2: MVCC过滤
    visible_results = []
    for tid in candidate_tids:
        tuple = heap_fetch(tid)

        if is_visible(tuple, snapshot_xid):
            visible_results.append(tuple)

    return visible_results

def is_visible(tuple, snapshot_xid):
    """MVCC可见性判断"""

    # 检查xmin
    if not committed(tuple.xmin):
        return False  # 未提交

    if tuple.xmin >= snapshot_xid:
        return False  # 在快照之后

    # 检查xmax
    if tuple.xmax == 0:
        return True  # 未删除

    if not committed(tuple.xmax):
        return True  # 删除未提交

    if tuple.xmax >= snapshot_xid:
        return True  # 在快照之后删除

    return False  # 已删除
```

---

## 5. 向量数据的ACID保证

### 5.1 原子性 (Atomicity)

```sql
-- 批量向量插入的原子性

BEGIN;

-- 插入100个文档及其向量
INSERT INTO documents (content, embedding)
SELECT
    content,
    generate_embedding(content)
FROM raw_documents
LIMIT 100;

-- MVCC保证:
-- - 100个插入要么全部成功
-- - 要么全部回滚
-- - 不会部分可见

COMMIT;
```

### 5.2 一致性 (Consistency)

```sql
-- 向量维度一致性约束

ALTER TABLE documents
ADD CONSTRAINT check_embedding_dim
CHECK (array_length(embedding::float[], 1) = 384);

-- MVCC确保:
-- - 约束在事务提交时检查
-- - 违反约束则回滚
-- - 保持数据库一致性
```

### 5.3 隔离性 (Isolation)

```sql
-- 向量更新的隔离性

-- 事务T1: 更新向量
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
UPDATE user_embeddings
SET embedding = compute_new_embedding(user_id)
WHERE user_id = 123;

-- 事务T2: 并发搜索
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM user_embeddings
ORDER BY embedding <=> query_vector
LIMIT 10;

-- MVCC隔离:
-- - T2不会看到T1未提交的更新
-- - T1更新不阻塞T2搜索
-- - 两个事务可串行化
```

### 5.4 持久性 (Durability)

```sql
-- 向量数据的持久性

BEGIN;
INSERT INTO documents (content, embedding) VALUES (...);
COMMIT;  -- 返回成功

-- PostgreSQL保证:
-- 1. WAL日志记录向量数据
-- 2. 检查点持久化到磁盘
-- 3. 崩溃恢复时重放WAL
-- 4. 向量数据不会丢失
```

---

## 6. 向量检索性能模型

### 6.1 MVCC开销分析

```
向量检索总延迟 = T_index + T_heap + T_filter

其中:
├─ T_index: HNSW索引搜索时间
│  └─ ~O(log N) * ef_search
│
├─ T_heap: Heap tuple访问时间
│  └─ ~O(ef_search) * T_page_access
│
└─ T_filter: MVCC可见性过滤时间
   └─ ~O(ef_search) * T_visibility_check

MVCC开销: T_heap + T_filter
占比: 通常10-30%

优化策略:
├─ 增大ef_search（减少heap访问）
├─ 及时VACUUM（减少死元组）
└─ 使用Index-Only Scan（如适用）
```

---

## 7. 并发场景分析

### 7.1 读写并发

```
场景: 向量检索 vs 向量更新

R: 读事务（相似度搜索）
W: 写事务（向量更新）

MVCC行为:
├─ R 获取快照 snapshot_R
├─ W 创建新版本 v_new (xmin=W)
├─ R 继续看到旧版本 v_old
└─ W 提交后，新R才看到 v_new

优势:
✅ 读不阻塞写
✅ 写不阻塞读
✅ 高并发性能

代价:
❌ 版本维护开销
❌ VACUUM必要性
```

### 7.2 写写并发

```
场景: 两个事务更新同一向量

T1: UPDATE embeddings SET embedding=v1 WHERE id=123
T2: UPDATE embeddings SET embedding=v2 WHERE id=123

MVCC + 锁机制:
├─ T1 先获取行锁
├─ T2 等待T1提交
├─ T1 提交后，T2继续
└─ 最终: embedding = v2

隔离级别影响:
├─ READ COMMITTED: T2看到T1的更新
└─ REPEATABLE READ: 可能导致T2失败（冲突检测）
```

---

## 8. 形式化定理

### 定理4: 向量检索快照隔离保证

**定理**: 在快照隔离下，向量相似度搜索Top-K结果在事务内部保持一致。

**形式化**:

```
设:
- T: 事务
- S_T: T的快照
- Q_k(v): 返回与v最相似的k个向量的查询
- t1, t2: T内两个时间点

则:
Q_k(v) at t1 using S_T = Q_k(v) at t2 using S_T

证明:
根据快照隔离定义:
1. S_T 在T开始时确定
2. T内所有查询使用相同S_T
3. Q_k(v) 只依赖于S_T中的数据

因此: Q_k(v)的结果在T内不变 ∎
```

---

### 定理5: 向量索引一致性

**定理**: HNSW索引与heap数据在MVCC下保持一致性。

**形式化**:

```
设:
- H: Heap数据
- I: HNSW索引
- V(T, S): 在快照S下事务T可见的数据

则对于任意快照S:
∀ tuple ∈ V(T, S):
    tuple在H中可见 ⟺ tuple在I中可访问

一致性保证:
1. 索引条目指向有效heap tuple
2. heap可见性决定索引结果
3. VACUUM同时清理heap和索引

因此索引与heap保持MVCC一致性 ∎
```

---

## 9. 实践建议

### 9.1 向量表设计

```sql
-- 推荐设计: 分离向量表

-- 主表（经常更新的业务数据）
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50),
    profile JSONB,
    updated_at TIMESTAMP
);

-- 向量表（不常更新）
CREATE TABLE user_embeddings (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id),
    embedding vector(384),
    version INTEGER DEFAULT 1,  -- 版本号
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 优势:
-- ✅ 主表更新不影响向量索引
-- ✅ 可HOT优化主表更新
-- ✅ 向量表仅在必要时更新
```

### 9.2 并发更新策略

```python
# 乐观锁更新向量

def update_embedding_optimistic(user_id, new_embedding):
    """使用乐观锁更新向量"""

    # 1. 读取当前版本
    row = db.fetchone("""
        SELECT embedding, version
        FROM user_embeddings
        WHERE user_id = %(user_id)s
    """, {'user_id': user_id})

    old_version = row['version']

    # 2. 计算新向量...

    # 3. 乐观更新（检查版本）
    result = db.execute("""
        UPDATE user_embeddings
        SET embedding = %(new_embedding)s,
            version = version + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %(user_id)s
          AND version = %(old_version)s  -- 版本检查
        RETURNING version;
    """, {
        'user_id': user_id,
        'new_embedding': new_embedding.tolist(),
        'old_version': old_version
    })

    if not result:
        # 版本冲突，重试
        return update_embedding_optimistic(user_id, new_embedding)

    return True
```

---

## 10. 性能优化

### 10.1 减少MVCC开销

```sql
-- 优化1: 定期VACUUM
VACUUM ANALYZE user_embeddings;

-- 优化2: 调整autovacuum参数
ALTER TABLE user_embeddings SET (
    autovacuum_vacuum_scale_factor = 0.05,  -- 更频繁VACUUM
    autovacuum_analyze_scale_factor = 0.05
);

-- 优化3: 使用分区表
CREATE TABLE user_embeddings_partitioned (
    user_id BIGINT,
    embedding vector(384),
    ...
) PARTITION BY HASH (user_id);
```

### 10.2 查询优化

```sql
-- 优化向量检索查询

-- ✅ 好: 限制搜索范围
SELECT * FROM documents
WHERE category_id = 5  -- 先过滤
ORDER BY embedding <=> query_vector
LIMIT 10;

-- ❌ 差: 全表扫描
SELECT * FROM documents
ORDER BY embedding <=> query_vector
LIMIT 10;
```

---

## 11. 参考资源

1. **pgvector文档**: <https://github.com/pgvector/pgvector>
2. **MVCC原理**: <https://www.postgresql.org/docs/current/mvcc.html>
3. **快照隔离论文**: "A Critique of ANSI SQL Isolation Levels"

---

**创建日期**: 2025-12-04
**理论完整性**: ✅ 高
**形式化程度**: 5个定理

**返回**: [理论基础首页](../README.md) | [MVCC-ACID-CAP主页](../../README.md)
