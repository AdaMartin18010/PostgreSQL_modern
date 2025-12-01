# 向量处理能力 - pgvector

> **文档编号**: AI-03-01
> **最后更新**: 2025年1月
> **主题**: 03-核心能力
> **子主题**: 01-向量处理能力

## 📑 目录

- [向量处理能力 - pgvector](#向量处理能力---pgvector)
  - [📑 目录](#-目录)
  - [一、概述](#一概述)
  - [二、核心功能](#二核心功能)
    - [2.1 向量数据类型](#21-向量数据类型)
    - [2.2 相似性搜索操作符](#22-相似性搜索操作符)
    - [2.3 向量索引](#23-向量索引)
      - [2.3.1 HNSW索引 (推荐用于大规模数据)](#231-hnsw索引-推荐用于大规模数据)
      - [2.3.2 IVFFlat索引 (适合小规模数据)](#232-ivfflat索引-适合小规模数据)
  - [三、性能特性](#三性能特性)
    - [3.1 性能基准 (参考数据)](#31-性能基准-参考数据)
    - [3.2 性能优化建议](#32-性能优化建议)
  - [四、混合查询](#四混合查询)
  - [五、对标资源](#五对标资源)
    - [学术论文](#学术论文)
    - [官方文档](#官方文档)
    - [企业案例](#企业案例)
  - [六、最佳实践](#六最佳实践)
  - [七、关联主题](#七关联主题)

## 一、概述

pgvector是PostgreSQL的向量扩展，为PostgreSQL添加了高效的向量存储和相似性搜索能力，使其成为AI应用的原生向量数据库。

## 二、核心功能

### 2.1 向量数据类型

pgvector提供了`vector`数据类型，支持存储高维向量：

```sql
-- 创建包含向量列的表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536)  -- OpenAI text-embedding-3-small维度
);

-- 插入向量数据
INSERT INTO documents (content, embedding)
VALUES (
    'PostgreSQL AI应用',
    '[0.1, 0.2, 0.3, ...]'::vector
);
```

### 2.2 相似性搜索操作符

pgvector支持多种相似性度量：

```sql
-- 余弦相似度 (<=>)
SELECT id, content, embedding <=> query_vector AS distance
FROM documents
ORDER BY embedding <=> query_vector
LIMIT 10;

-- 欧氏距离 (<->)
SELECT id, content, embedding <-> query_vector AS distance
FROM documents
ORDER BY embedding <-> query_vector
LIMIT 10;

-- 内积 (<#>)
SELECT id, content, embedding <#> query_vector AS distance
FROM documents
ORDER BY embedding <#> query_vector
LIMIT 10;
```

### 2.3 向量索引

#### 2.3.1 HNSW索引 (推荐用于大规模数据)

```sql
-- 创建HNSW索引
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 100);

-- 查询时设置ef_search参数
SET hnsw.ef_search = 100;
SELECT * FROM documents
ORDER BY embedding <=> query_vector
LIMIT 10;
```

**参数说明**:

- `m`: 每个节点的最大连接数 (默认16, 范围4-64)
- `ef_construction`: 构建时的搜索宽度 (默认100, 范围4-1000)
- `ef_search`: 查询时的搜索宽度 (默认40, 范围1-1000)

#### 2.3.2 IVFFlat索引 (适合小规模数据)

```sql
-- 创建IVFFlat索引
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 查询前需要设置合适的lists参数
SET ivfflat.probes = 10;  -- 通常设为lists的10%
SELECT * FROM documents
ORDER BY embedding <=> query_vector
LIMIT 10;
```

**参数说明**:

- `lists`: 聚类中心数量 (建议: 行数/1000 到 行数/10000)
- `probes`: 查询时搜索的聚类数 (范围1到lists)

## 三、性能特性

### 3.1 性能基准 (参考数据)

| 数据规模 | 向量维度 | 索引类型 | QPS | P95延迟 | 召回率 |
|---------|---------|---------|-----|---------|--------|
| 100万 | 768 | HNSW | 8,000 | <10ms | >0.95 |
| 1000万 | 768 | HNSW | 5,000 | <15ms | >0.95 |
| 1亿 | 768 | HNSW | 2,000 | <20ms | >0.90 |

### 3.2 性能优化建议

1. **索引选择**:
   - 小规模数据 (<100万): IVFFlat
   - 大规模数据 (>100万): HNSW
   - 极高召回率要求: HNSW with higher ef_search

2. **参数调优**:
   - HNSW: 提高`ef_construction`和`ef_search`可提升召回率
   - IVFFlat: 增加`lists`和`probes`可提升召回率

3. **硬件优化**:
   - 使用SSD存储
   - 增加内存容量
   - 考虑GPU加速 (未来支持)

## 四、混合查询

pgvector支持与PostgreSQL的SQL功能无缝集成：

```sql
-- 混合查询: 向量相似度 + 条件过滤
SELECT id, content, embedding <=> query_vector AS distance
FROM documents
WHERE category = 'technology'
  AND created_at > '2024-01-01'
  AND embedding <=> query_vector < 0.8
ORDER BY embedding <=> query_vector
LIMIT 20;

-- 结合全文搜索
SELECT id, content,
       embedding <=> query_vector AS vector_distance,
       ts_rank(content_tsv, query_ts) AS text_rank
FROM documents
WHERE content_tsv @@ query_ts
ORDER BY (embedding <=> query_vector) * 0.7 + (1 - ts_rank(content_tsv, query_ts)) * 0.3
LIMIT 20;
```

## 五、对标资源

### 学术论文

- **HNSW算法**: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs" (IEEE TPAMI 2018)
- **Product Quantization**: "Product Quantization for Nearest Neighbor Search" (IEEE TPAMI 2011)
- **DiskANN**: "DiskANN: Fast Accurate Billion-point Nearest Neighbor Search" (NeurIPS 2019)

### 官方文档

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [pgvector文档](https://github.com/pgvector/pgvector#documentation)

### 企业案例

- Qunar途家: 向量搜索在旅游场景的应用
- 性能提升: 召回率提升30%, 延迟降低

## 六、最佳实践

1. **向量维度选择**:
   - OpenAI text-embedding-3-small: 1536维
   - OpenAI text-embedding-3-large: 3072维
   - 自定义模型: 根据模型输出维度

2. **索引创建时机**:
   - 数据导入完成后创建索引
   - 使用`CREATE INDEX CONCURRENTLY`避免锁表

3. **查询优化**:
   - 合理设置`ef_search`平衡性能和召回率
   - 使用`LIMIT`限制返回结果数
   - 结合条件过滤减少搜索空间

4. **监控指标**:
   - 查询延迟 (P50, P95, P99)
   - 召回率
   - 索引大小
   - 查询吞吐量

## 七、关联主题

- [AI原生调用 (pgai)](./AI原生调用-pgai.md) - 自动生成Embedding
- [混合查询能力](./混合查询能力.md) - 向量+SQL联合查询
- [性能优化技术](./性能优化技术.md) - 索引优化策略

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**文档编号**: AI-03-01
