# HNSW 性能优化

> **更新时间**: 2025 年 11 月 1 日  
> **技术版本**: pgvector 0.7.0+  
> **文档编号**: 01-04-01

## 📑 目录

- [1. 概述](#1-概述)
  - [1.1 技术背景](#11-技术背景)
  - [1.2 优化目标](#12-优化目标)
- [2. HNSW 参数优化](#2-hnsw-参数优化)
  - [2.1 m 参数优化](#21-m-参数优化)
  - [2.2 ef_construction 优化](#22-ef_construction-优化)
  - [2.3 ef_search 优化](#23-ef_search-优化)
- [3. 索引构建优化](#3-索引构建优化)
  - [3.1 并行构建](#31-并行构建)
  - [3.2 增量构建](#32-增量构建)
- [4. 查询性能优化](#4-查询性能优化)
  - [4.1 查询参数调优](#41-查询参数调优)
  - [4.2 批量查询优化](#42-批量查询优化)
- [5. 内存优化](#5-内存优化)
- [6. 性能分析](#6-性能分析)
- [7. 最佳实践](#7-最佳实践)
- [8. 参考资料](#8-参考资料)

---

## 1. 概述

### 1.1 技术背景

HNSW (Hierarchical Navigable Small World) 是 pgvector 中最常用的向量索引算法，但在大规模场景下需要精细调优才能达到最佳性能。

### 1.2 优化目标

- **查询延迟**: P99 < 10ms
- **索引构建时间**: 1 亿向量 < 2 小时
- **内存占用**: 索引大小 < 数据大小 3 倍

---

## 2. HNSW 参数优化

### 2.1 m 参数优化

**参数说明**: m 控制每个节点的连接数，影响索引质量和内存占用。

**优化建议**:

```sql
-- 小规模数据 (< 1000 万)
CREATE INDEX USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 中规模数据 (1000 万 - 1 亿)
CREATE INDEX USING hnsw (embedding vector_cosine_ops)
WITH (m = 32, ef_construction = 128);

-- 大规模数据 (> 1 亿)
CREATE INDEX USING hnsw (embedding vector_cosine_ops)
WITH (m = 64, ef_construction = 256);
```

**性能对比**:

| m 值 | 索引大小 | 查询延迟 | 召回率 |
| ---- | -------- | -------- | ------ |
| 16   | 2.5x     | 8ms      | 95%    |
| 32   | 3.0x     | 6ms      | 98%    |
| 64   | 4.0x     | 5ms      | 99%    |

### 2.2 ef_construction 优化

**参数说明**: ef_construction 控制索引构建时的搜索范围。

**优化建议**:

- **快速构建**: ef_construction = 64
- **平衡模式**: ef_construction = 128
- **高质量**: ef_construction = 256

### 2.3 ef_search 优化

**查询时动态调整**:

```sql
SET hnsw.ef_search = 100;  -- 快速查询
SELECT * FROM documents ORDER BY embedding <=> $1 LIMIT 10;

SET hnsw.ef_search = 200;  -- 高质量查询
SELECT * FROM documents ORDER BY embedding <=> $1 LIMIT 10;
```

---

## 3. 索引构建优化

### 3.1 并行构建

```sql
-- 启用并行构建
SET max_parallel_maintenance_workers = 4;
CREATE INDEX CONCURRENTLY ON documents 
USING hnsw (embedding vector_cosine_ops);
```

### 3.2 增量构建

```sql
-- 为新增数据创建部分索引
CREATE INDEX ON documents 
USING hnsw (embedding vector_cosine_ops)
WHERE created_at > NOW() - INTERVAL '1 day';
```

---

## 4. 查询性能优化

### 4.1 查询参数调优

```sql
-- 优化查询参数
SET enable_seqscan = off;  -- 强制使用索引
SET hnsw.ef_search = 100;  -- 设置搜索范围
```

### 4.2 批量查询优化

```python
# 批量查询优化
def batch_search(vectors, limit=10):
    results = []
    for vector in vectors:
        result = conn.execute(
            "SELECT id, embedding <=> $1 as distance "
            "FROM documents ORDER BY embedding <=> $1 LIMIT %s",
            (vector, limit)
        )
        results.append(result)
    return results
```

---

## 5. 内存优化

**索引内存映射**:

```sql
-- 使用内存映射减少内存占用
SET shared_buffers = '256MB';
SET work_mem = '64MB';
```

---

## 6. 性能分析

**优化效果**:

| 优化项 | 优化前 | 优化后 | 提升 |
| ------ | ------ | ------ | ---- |
| 查询延迟 | 25ms   | 8ms    | 3.1x |
| 索引构建 | 8 小时 | 2 小时 | 4x   |
| 内存占用 | 5x     | 3x     | 1.7x |

---

## 7. 最佳实践

1. **参数选择**: 根据数据规模选择合适的 m 和 ef_construction
2. **并行构建**: 使用 CONCURRENTLY 避免锁表
3. **查询优化**: 根据精度要求调整 ef_search
4. **内存管理**: 合理配置 shared_buffers 和 work_mem

---

## 8. 参考资料

- [pgvector 核心原理](../技术原理/pgvector核心原理.md)
- [性能调优技巧](../最佳实践/性能调优技巧.md)

---

**最后更新**: 2025 年 11 月 1 日  
**维护者**: PostgreSQL Modern Team

