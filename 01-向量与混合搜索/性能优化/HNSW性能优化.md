# HNSW 性能优化

> **更新时间**: 2025 年 11 月 1 日
> **技术版本**: PostgreSQL 14+, pgvector 0.7.0+
> **文档编号**: 01-04-01

## 📑 目录

- [HNSW 性能优化](#hnsw-性能优化)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 HNSW 索引特点](#11-hnsw-索引特点)
    - [1.2 优化目标](#12-优化目标)
  - [2. 索引参数优化](#2-索引参数优化)
    - [2.1 m 参数优化](#21-m-参数优化)
    - [2.2 ef\_construction 参数优化](#22-ef_construction-参数优化)
  - [3. 查询参数优化](#3-查询参数优化)
    - [3.1 ef\_search 参数](#31-ef_search-参数)
    - [3.2 动态 ef\_search 调整](#32-动态-ef_search-调整)
  - [4. 内存优化](#4-内存优化)
    - [4.1 索引大小优化](#41-索引大小优化)
    - [4.2 批量插入优化](#42-批量插入优化)
  - [5. 并发优化](#5-并发优化)
    - [5.1 连接池优化](#51-连接池优化)
    - [5.2 查询缓存](#52-查询缓存)
  - [6. 实践案例](#6-实践案例)
    - [6.1 高并发场景优化](#61-高并发场景优化)
  - [7. 参考资料](#7-参考资料)

---

## 1. 概述

### 1.1 HNSW 索引特点

**HNSW (Hierarchical Navigable Small World)** 索引特点：

- **高精度**: 召回率 > 99%
- **快速查询**: 查询时间 O(log N)
- **内存占用**: 相对较高
- **更新成本**: 重建索引成本高

### 1.2 优化目标

- **查询速度**: P99 延迟 < 50ms
- **内存使用**: 优化内存占用
- **索引构建**: 加快索引构建速度
- **并发性能**: 支持高并发查询

## 2. 索引参数优化

### 2.1 m 参数优化

```sql
-- m 参数：每个节点的最大连接数
-- 推荐值：16（默认），范围：4-64
-- 越大：查询更快，但索引更大，构建更慢
CREATE INDEX ON vectors USING hnsw (embedding vector_cosine_ops)
WITH (m = 16);

-- 高精度场景：m = 32
CREATE INDEX ON vectors USING hnsw (embedding vector_cosine_ops)
WITH (m = 32);

-- 内存受限场景：m = 8
CREATE INDEX ON vectors USING hnsw (embedding vector_cosine_ops)
WITH (m = 8);
```

### 2.2 ef_construction 参数优化

```sql
-- ef_construction：构建时的候选集大小
-- 推荐值：64（默认），范围：4-1000
-- 越大：索引质量更高，但构建更慢
CREATE INDEX ON vectors USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 高质量索引：ef_construction = 200
CREATE INDEX ON vectors USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);

-- 快速构建：ef_construction = 32
CREATE INDEX ON vectors USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 32);
```

## 3. 查询参数优化

### 3.1 ef_search 参数

```sql
-- ef_search：查询时的候选集大小
-- 默认值：40，范围：1-1000
-- 越大：召回率更高，但查询更慢

-- 高召回率查询
SET hnsw.ef_search = 200;
SELECT * FROM vectors
ORDER BY embedding <=> query_vector
LIMIT 10;

-- 快速查询（召回率可能降低）
SET hnsw.ef_search = 20;
SELECT * FROM vectors
ORDER BY embedding <=> query_vector
LIMIT 10;
```

### 3.2 动态 ef_search 调整

```python
# 根据查询需求动态调整 ef_search
class AdaptiveEFSearch:
    def __init__(self):
        self.base_ef_search = 40

    async def search(self, query_vector, limit, recall_target=0.95):
        """根据召回率目标调整 ef_search"""
        ef_search = self.base_ef_search

        while True:
            result = await self._search_with_ef(query_vector, limit, ef_search)
            recall = self._estimate_recall(result)

            if recall >= recall_target:
                return result

            ef_search = int(ef_search * 1.5)
            if ef_search > 1000:
                break

        return result
```

## 4. 内存优化

### 4.1 索引大小优化

```sql
-- 查看索引大小
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE indexname LIKE '%hnsw%';

-- 优化索引大小：降低 m 参数
CREATE INDEX ON vectors USING hnsw (embedding vector_cosine_ops)
WITH (m = 8);  -- 降低 m 值减少内存占用
```

### 4.2 批量插入优化

```python
# 批量插入优化
class OptimizedBatchInsert:
    async def insert_batch(self, vectors, batch_size=1000):
        """批量插入，减少索引更新次数"""
        async with self.db.transaction():
            # 1. 先插入数据（不更新索引）
            await self.db.executemany(
                "INSERT INTO vectors (embedding, metadata) VALUES ($1, $2)",
                vectors
            )

            # 2. 批量重建索引（更高效）
            await self.db.execute("REINDEX INDEX vectors_embedding_idx")
```

## 5. 并发优化

### 5.1 连接池优化

```python
# 连接池配置优化
from asyncpg import create_pool

class OptimizedConnectionPool:
    def __init__(self):
        self.pool = None

    async def initialize(self, database_url):
        self.pool = await create_pool(
            database_url,
            min_size=20,  # 最小连接数
            max_size=100,  # 最大连接数
            max_queries=50000,  # 每个连接最大查询数
            max_inactive_connection_lifetime=300.0  # 非活跃连接生命周期
        )

    async def search(self, query_vector, limit=10):
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT * FROM vectors
                ORDER BY embedding <=> $1::vector
                LIMIT $2
            """, query_vector, limit)
```

### 5.2 查询缓存

```python
# 查询结果缓存
class CachedVectorSearch:
    def __init__(self, db_pool, cache):
        self.db_pool = db_pool
        self.cache = cache

    async def search(self, query_vector, limit=10):
        # 1. 检查缓存
        cache_key = self._get_cache_key(query_vector, limit)
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result

        # 2. 执行查询
        async with self.db_pool.acquire() as conn:
            result = await conn.fetch("""
                SELECT * FROM vectors
                ORDER BY embedding <=> $1::vector
                LIMIT $2
            """, query_vector, limit)

        # 3. 缓存结果
        await self.cache.set(cache_key, result, ttl=300)
        return result
```

## 6. 实践案例

### 6.1 高并发场景优化

```python
# 高并发向量搜索优化
class HighConcurrencyOptimizer:
    def __init__(self):
        self.pool = create_pool(min_size=50, max_size=200)
        self.cache = RedisCache()
        self.ef_search = 40

    async def search(self, query_vector, limit=10):
        # 1. 使用较低的 ef_search 提升速度
        async with self.pool.acquire() as conn:
            await conn.execute(f"SET hnsw.ef_search = {self.ef_search}")

            result = await conn.fetch("""
                SELECT * FROM vectors
                ORDER BY embedding <=> $1::vector
                LIMIT $2
            """, query_vector, limit)

        return result
```

## 7. 参考资料

- [索引选择策略](../最佳实践/索引选择策略.md)
- [pgvector HNSW 文档](https://github.com/pgvector/pgvector#hnsw)

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
**文档编号**: 01-04-01
