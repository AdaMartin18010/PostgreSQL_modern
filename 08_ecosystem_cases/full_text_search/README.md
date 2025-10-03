# 全文搜索实战案例 — Full-Text Search with PostgreSQL

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **难度等级**：⭐⭐⭐ 中级  
> **预计时间**：30-60分钟  
> **适合场景**：文档搜索、日志检索、商品搜索、内容推荐

---

## 📋 案例目标

构建一个生产级的全文搜索系统，包括：

1. ✅ 中英文混合全文搜索
2. ✅ 相关性排序与高亮显示
3. ✅ 搜索性能优化（GIN索引）
4. ✅ 搜索建议与自动补全
5. ✅ 实时索引更新

---

## 🎯 业务场景

**场景描述**：构建一个技术文档搜索平台

- **文档类型**：技术博客、API文档、问答帖子
- **搜索需求**：
  - 支持中英文混合搜索
  - 按相关性排序
  - 搜索结果高亮
  - 支持同义词（如"数据库"="DB"）
  - 性能要求：100万文档，搜索响应<100ms

---

## 🏗️ 架构设计

```text
用户搜索请求
    ↓
查询处理层（分词、同义词）
    ↓
全文搜索引擎（tsvector + GIN索引）
    ↓
结果排序（ts_rank）
    ↓
结果高亮（ts_headline）
    ↓
返回给用户
```

---

## 📦 1. 数据模型设计

### 1.1 创建文档表

```sql
-- 创建文档表
CREATE TABLE documents (
    id bigserial PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    author text,
    category text,
    tags text[],
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    view_count int DEFAULT 0,
    
    -- 全文搜索向量（自动维护）
    search_vector tsvector,
    
    -- 添加索引
    CONSTRAINT documents_title_not_empty CHECK (char_length(title) > 0)
);

-- 创建GIN索引（加速全文搜索）
CREATE INDEX idx_documents_search_vector ON documents USING gin(search_vector);

-- 创建其他索引
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX idx_documents_tags ON documents USING gin(tags);

-- 添加注释
COMMENT ON TABLE documents IS '文档表：支持全文搜索';
COMMENT ON COLUMN documents.search_vector IS '全文搜索向量（tsvector类型）';
```

### 1.2 自动更新搜索向量

```sql
-- 创建触发器函数：自动更新search_vector
CREATE OR REPLACE FUNCTION documents_search_vector_update() 
RETURNS trigger AS $$
BEGIN
    -- 合并标题（权重A）、内容（权重B）、标签（权重C）
    NEW.search_vector := 
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.content, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(array_to_string(NEW.tags, ' '), '')), 'C');
    
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_documents_search_vector_update
    BEFORE INSERT OR UPDATE OF title, content, tags
    ON documents
    FOR EACH ROW
    EXECUTE FUNCTION documents_search_vector_update();
```

---

## 📝 2. 插入测试数据

### 2.1 批量插入示例文档

```sql
-- 插入示例文档
INSERT INTO documents (title, content, author, category, tags) VALUES
('PostgreSQL 17 新特性详解', 
 'PostgreSQL 17 引入了多项重要改进：JSON_TABLE函数支持SQL标准、B-tree索引多值搜索优化、VACUUM内存管理改进、Streaming I/O顺序读取优化等。这些特性显著提升了数据库性能和开发效率。',
 'Alice',
 'Database',
 ARRAY['PostgreSQL', 'Database', 'Performance']
),
('全文搜索实战指南', 
 '全文搜索（Full-Text Search）是PostgreSQL的强大特性之一。通过tsvector和tsquery数据类型，配合GIN索引，可以实现高性能的文本检索。本文介绍如何构建生产级全文搜索系统。',
 'Bob',
 'Tutorial',
 ARRAY['Full-Text Search', 'PostgreSQL', 'GIN Index']
),
('MVCC并发控制原理', 
 'Multi-Version Concurrency Control (MVCC) 是PostgreSQL的核心机制。通过为每个事务创建快照，MVCC实现了读不阻塞写、写不阻塞读的高并发性能。理解xmin、xmax、快照隔离等概念是掌握PostgreSQL的关键。',
 'Charlie',
 'Advanced',
 ARRAY['MVCC', 'Transaction', 'Concurrency']
),
('B-tree索引深度解析', 
 'B-tree索引是PostgreSQL默认的索引类型。它支持等值查询、范围查询、排序等操作。PostgreSQL 17对B-tree进行了优化，特别是多值搜索（IN子句）性能显著提升。本文深入剖析B-tree内部结构和优化技巧。',
 'David',
 'Performance',
 ARRAY['Index', 'B-tree', 'Optimization']
),
('如何优化PostgreSQL查询性能', 
 '查询性能优化是数据库管理的核心工作。本文介绍常用的优化方法：创建合适的索引、使用EXPLAIN分析执行计划、调整统计信息、优化JOIN顺序、避免函数破坏索引等。掌握这些技巧可以显著提升查询速度。',
 'Eve',
 'Performance',
 ARRAY['Performance', 'Query Optimization', 'Index']
),
('分布式数据库架构设计', 
 '分布式数据库通过分片（Sharding）和复制（Replication）实现水平扩展。本文介绍Citus扩展如何将PostgreSQL转变为分布式数据库，涵盖分片策略、分布式JOIN、故障转移等核心技术。',
 'Frank',
 'Distributed',
 ARRAY['Distributed Database', 'Citus', 'Sharding']
),
('向量数据库与RAG应用', 
 'pgvector扩展为PostgreSQL添加了向量检索能力，支持构建RAG（Retrieval-Augmented Generation）系统。本文介绍如何使用pgvector实现语义搜索、相似度查询、向量索引优化等功能。',
 'Grace',
 'AI',
 ARRAY['Vector Database', 'pgvector', 'AI', 'RAG']
),
('TimescaleDB时序数据管理', 
 'TimescaleDB是PostgreSQL的时序数据库扩展。通过超表（Hypertable）、连续聚合（Continuous Aggregate）、数据压缩等特性，TimescaleDB可以高效处理海量时序数据。本文介绍时序数据建模和性能优化。',
 'Henry',
 'Time-Series',
 ARRAY['TimescaleDB', 'Time-Series', 'IoT']
),
('PostGIS地理空间查询', 
 'PostGIS是PostgreSQL的地理空间扩展，支持点、线、面等几何类型，提供距离计算、空间索引、地理围栏等功能。本文介绍如何使用PostGIS构建位置服务应用。',
 'Ivy',
 'GIS',
 ARRAY['PostGIS', 'GIS', 'Spatial']
),
('PostgreSQL逻辑复制实战', 
 '逻辑复制（Logical Replication）是PostgreSQL 10+的核心特性。相比物理复制，逻辑复制支持跨版本、跨平台、选择性复制。本文介绍逻辑复制的配置、监控、故障处理等实战经验。',
 'Jack',
 'Replication',
 ARRAY['Logical Replication', 'High Availability', 'Disaster Recovery']
);

-- 查看插入结果
SELECT id, title, category, array_length(tags, 1) AS tag_count 
FROM documents 
ORDER BY id;
```

---

## 🔍 3. 全文搜索查询

### 3.1 基本搜索

```sql
-- 搜索包含"PostgreSQL"的文档
SELECT 
    id,
    title,
    ts_rank(search_vector, query) AS rank
FROM 
    documents,
    to_tsquery('english', 'PostgreSQL') AS query
WHERE 
    search_vector @@ query
ORDER BY rank DESC;

-- 搜索包含"性能"或"优化"的文档
SELECT 
    id,
    title,
    ts_rank(search_vector, query) AS rank
FROM 
    documents,
    to_tsquery('english', 'Performance | Optimization') AS query
WHERE 
    search_vector @@ query
ORDER BY rank DESC;

-- 搜索包含"PostgreSQL"且包含"索引"的文档
SELECT 
    id,
    title,
    ts_rank(search_vector, query) AS rank
FROM 
    documents,
    to_tsquery('english', 'PostgreSQL & Index') AS query
WHERE 
    search_vector @@ query
ORDER BY rank DESC;
```

### 3.2 相关性排序

```sql
-- 使用ts_rank_cd（考虑词频和文档长度）
SELECT 
    id,
    title,
    ts_rank_cd(search_vector, query) AS rank,
    ts_rank_cd(search_vector, query, 32) AS rank_normalized
FROM 
    documents,
    to_tsquery('english', 'PostgreSQL & Performance') AS query
WHERE 
    search_vector @@ query
ORDER BY rank_normalized DESC;

-- 自定义权重（标题权重更高）
SELECT 
    id,
    title,
    ts_rank(
        search_vector, 
        query,
        1 | 2 | 4 | 8  -- 使用所有权重
    ) AS rank
FROM 
    documents,
    to_tsquery('english', 'PostgreSQL') AS query
WHERE 
    search_vector @@ query
ORDER BY rank DESC;
```

### 3.3 搜索结果高亮

```sql
-- 高亮显示搜索关键词
SELECT 
    id,
    title,
    ts_headline(
        'english',
        content,
        query,
        'StartSel=<b>, StopSel=</b>, MaxWords=50, MinWords=10'
    ) AS highlighted_content,
    ts_rank(search_vector, query) AS rank
FROM 
    documents,
    to_tsquery('english', 'PostgreSQL & Performance') AS query
WHERE 
    search_vector @@ query
ORDER BY rank DESC
LIMIT 10;
```

### 3.4 模糊搜索（前缀匹配）

```sql
-- 前缀搜索：匹配以"Post"开头的词
SELECT 
    id,
    title,
    ts_rank(search_vector, query) AS rank
FROM 
    documents,
    to_tsquery('english', 'Post:*') AS query
WHERE 
    search_vector @@ query
ORDER BY rank DESC;

-- 组合前缀搜索
SELECT 
    id,
    title,
    ts_rank(search_vector, query) AS rank
FROM 
    documents,
    to_tsquery('english', 'Post:* & Optim:*') AS query
WHERE 
    search_vector @@ query
ORDER BY rank DESC;
```

---

## 🚀 4. 高级特性

### 4.1 同义词支持

```sql
-- 创建同义词字典
CREATE TEXT SEARCH DICTIONARY synonym_dict (
    TEMPLATE = synonym,
    SYNONYMS = pg_synonym
);

-- 创建自定义配置（需要先创建同义词文件）
-- 注意：生产环境需要在服务器上创建 $SHAREDIR/tsearch_data/pg_synonym.syn 文件

-- 示例同义词文件内容：
-- db database
-- pg postgresql
-- perf performance

-- 使用同义词搜索（简化版：直接使用OR）
SELECT 
    id,
    title,
    ts_rank(search_vector, query) AS rank
FROM 
    documents,
    to_tsquery('english', 'database | db | postgresql | pg') AS query
WHERE 
    search_vector @@ query
ORDER BY rank DESC;
```

### 4.2 搜索建议（自动补全）

```sql
-- 创建搜索词表（记录用户搜索历史）
CREATE TABLE search_suggestions (
    id bigserial PRIMARY KEY,
    search_term text NOT NULL,
    search_count int DEFAULT 1,
    last_searched_at timestamptz DEFAULT now()
);

CREATE INDEX idx_search_suggestions_term ON search_suggestions(search_term text_pattern_ops);

-- 记录搜索词
INSERT INTO search_suggestions (search_term)
VALUES ('PostgreSQL')
ON CONFLICT (search_term) DO UPDATE
SET search_count = search_suggestions.search_count + 1,
    last_searched_at = now();

-- 获取搜索建议（基于前缀）
SELECT 
    search_term,
    search_count
FROM 
    search_suggestions
WHERE 
    search_term ILIKE 'Post%'
ORDER BY 
    search_count DESC,
    search_term
LIMIT 10;
```

### 4.3 多语言支持（中英文混合）

```sql
-- 创建支持中文的搜索向量
CREATE EXTENSION IF NOT EXISTS zhparser;  -- 需要安装中文分词扩展

-- 创建中文文本搜索配置
CREATE TEXT SEARCH CONFIGURATION zh_cn (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION zh_cn ADD MAPPING FOR n,v,a,i,e,l WITH simple;

-- 创建支持中英文的表
CREATE TABLE documents_cn (
    id bigserial PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    category text,
    search_vector_en tsvector,  -- 英文搜索向量
    search_vector_cn tsvector   -- 中文搜索向量
);

-- 创建双语索引
CREATE INDEX idx_documents_cn_search_en ON documents_cn USING gin(search_vector_en);
CREATE INDEX idx_documents_cn_search_cn ON documents_cn USING gin(search_vector_cn);

-- 插入中英文混合文档
INSERT INTO documents_cn (title, content, category, search_vector_en, search_vector_cn)
VALUES (
    'PostgreSQL数据库教程',
    'PostgreSQL是世界上最先进的开源数据库系统。它支持ACID事务、MVCC并发控制、丰富的数据类型。',
    'Tutorial',
    to_tsvector('english', 'PostgreSQL'),
    to_tsvector('zh_cn', 'PostgreSQL数据库教程 PostgreSQL是世界上最先进的开源数据库系统。它支持ACID事务、MVCC并发控制、丰富的数据类型。')
);

-- 中英文混合搜索
SELECT 
    id,
    title,
    greatest(
        ts_rank(search_vector_en, to_tsquery('english', 'PostgreSQL')),
        ts_rank(search_vector_cn, to_tsquery('zh_cn', 'PostgreSQL'))
    ) AS rank
FROM 
    documents_cn
WHERE 
    search_vector_en @@ to_tsquery('english', 'PostgreSQL')
    OR search_vector_cn @@ to_tsquery('zh_cn', 'PostgreSQL')
ORDER BY rank DESC;
```

---

## 📊 5. 性能优化

### 5.1 索引维护

```sql
-- 查看索引大小
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE tablename = 'documents';

-- 查看索引使用情况
SELECT
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE tablename = 'documents'
ORDER BY idx_scan DESC;

-- VACUUM维护（清理死元组）
VACUUM ANALYZE documents;
```

### 5.2 查询性能分析

```sql
-- 分析查询计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    id,
    title,
    ts_rank(search_vector, query) AS rank
FROM 
    documents,
    to_tsquery('english', 'PostgreSQL & Performance') AS query
WHERE 
    search_vector @@ query
ORDER BY rank DESC
LIMIT 10;

-- 期望看到：
-- Bitmap Heap Scan on documents
--   Recheck Cond: (search_vector @@ query)
--   -> Bitmap Index Scan on idx_documents_search_vector  ← 使用GIN索引
```

### 5.3 性能测试

```sql
-- 生成大量测试数据
INSERT INTO documents (title, content, author, category, tags)
SELECT
    'Document ' || i,
    'Content for document ' || i || '. This is a test document with PostgreSQL keywords.',
    'Author' || (i % 10),
    (ARRAY['Database', 'Tutorial', 'Advanced', 'Performance'])[1 + (i % 4)],
    ARRAY['PostgreSQL', 'Test']
FROM generate_series(1, 100000) AS i;

-- 测试搜索性能
\timing on
SELECT COUNT(*) 
FROM documents 
WHERE search_vector @@ to_tsquery('english', 'PostgreSQL');
\timing off

-- 对比全表扫描性能
\timing on
SELECT COUNT(*) 
FROM documents 
WHERE content ILIKE '%PostgreSQL%';
\timing off
```

---

## 🎨 6. 生产级封装

### 6.1 创建搜索函数

```sql
-- 创建通用搜索函数
CREATE OR REPLACE FUNCTION search_documents(
    search_query text,
    result_limit int DEFAULT 10,
    result_offset int DEFAULT 0
)
RETURNS TABLE (
    doc_id bigint,
    doc_title text,
    doc_category text,
    doc_author text,
    highlighted_content text,
    relevance_rank real,
    doc_created_at timestamptz
) AS $$
DECLARE
    ts_query tsquery;
BEGIN
    -- 转换搜索查询
    ts_query := plainto_tsquery('english', search_query);
    
    RETURN QUERY
    SELECT 
        d.id,
        d.title,
        d.category,
        d.author,
        ts_headline(
            'english',
            d.content,
            ts_query,
            'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=10'
        ) AS highlighted_content,
        ts_rank_cd(d.search_vector, ts_query, 32)::real AS relevance_rank,
        d.created_at
    FROM 
        documents d
    WHERE 
        d.search_vector @@ ts_query
    ORDER BY 
        relevance_rank DESC,
        d.created_at DESC
    LIMIT result_limit
    OFFSET result_offset;
END;
$$ LANGUAGE plpgsql STABLE;

-- 使用搜索函数
SELECT * FROM search_documents('PostgreSQL performance optimization', 10, 0);
```

### 6.2 搜索分析视图

```sql
-- 创建搜索统计视图
CREATE MATERIALIZED VIEW search_statistics AS
SELECT 
    category,
    COUNT(*) AS document_count,
    AVG(char_length(content)) AS avg_content_length,
    COUNT(DISTINCT author) AS author_count
FROM documents
GROUP BY category;

CREATE INDEX idx_search_stats_category ON search_statistics(category);

-- 刷新统计视图
REFRESH MATERIALIZED VIEW search_statistics;

-- 查询统计
SELECT * FROM search_statistics ORDER BY document_count DESC;
```

---

## 🔧 7. 监控与运维

### 7.1 搜索性能监控

```sql
-- 创建搜索日志表
CREATE TABLE search_logs (
    id bigserial PRIMARY KEY,
    search_query text NOT NULL,
    result_count int,
    execution_time_ms numeric(10,2),
    user_id bigint,
    searched_at timestamptz DEFAULT now()
);

CREATE INDEX idx_search_logs_query ON search_logs(search_query);
CREATE INDEX idx_search_logs_searched_at ON search_logs(searched_at DESC);

-- 记录搜索日志（应用层调用）
INSERT INTO search_logs (search_query, result_count, execution_time_ms)
VALUES ('PostgreSQL performance', 15, 12.34);

-- 分析热门搜索词
SELECT 
    search_query,
    COUNT(*) AS search_count,
    AVG(execution_time_ms) AS avg_time_ms,
    AVG(result_count) AS avg_results
FROM search_logs
WHERE searched_at > now() - interval '7 days'
GROUP BY search_query
ORDER BY search_count DESC
LIMIT 20;
```

### 7.2 索引健康检查

```sql
-- 检查索引膨胀
CREATE EXTENSION IF NOT EXISTS pgstattuple;

SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    round((100 * (1 - avg_leaf_density / 100)), 2) AS bloat_ratio
FROM pg_stat_user_indexes
JOIN LATERAL pgstatindex(indexrelid) ON true
WHERE tablename = 'documents'
  AND indexname LIKE '%search_vector%';
```

---

## ✅ 8. 完整示例查询

```sql
-- 综合搜索示例：支持分页、排序、过滤
WITH search_results AS (
    SELECT 
        d.id,
        d.title,
        d.author,
        d.category,
        d.created_at,
        ts_headline(
            'english',
            d.content,
            query,
            'StartSel=<b>, StopSel=</b>, MaxWords=50'
        ) AS snippet,
        ts_rank_cd(d.search_vector, query, 32) AS rank
    FROM 
        documents d,
        plainto_tsquery('english', 'PostgreSQL performance optimization') AS query
    WHERE 
        d.search_vector @@ query
        AND d.category = 'Performance'  -- 分类过滤
        AND d.created_at > now() - interval '1 year'  -- 时间过滤
)
SELECT 
    id,
    title,
    author,
    category,
    snippet,
    round(rank::numeric, 4) AS relevance_score,
    created_at
FROM search_results
ORDER BY rank DESC, created_at DESC
LIMIT 10 OFFSET 0;
```

---

## 📚 9. 最佳实践

### 9.1 索引策略

- ✅ 对搜索字段创建GIN索引
- ✅ 使用触发器自动更新tsvector
- ✅ 定期VACUUM维护索引
- ✅ 监控索引使用率

### 9.2 查询优化

- ✅ 使用plainto_tsquery简化查询
- ✅ 限制返回结果数量（LIMIT）
- ✅ 使用ts_rank_cd考虑文档长度
- ✅ 缓存热门搜索结果

### 9.3 扩展性

- ✅ 大数据量考虑分区表
- ✅ 使用pg_trgm支持模糊搜索
- ✅ 集成Elasticsearch用于复杂场景
- ✅ 实现搜索建议与自动补全

---

## 🎯 10. 练习任务

1. **基础练习**：
   - 创建文档表并插入10条测试数据
   - 实现基本的关键词搜索
   - 添加搜索结果高亮

2. **进阶练习**：
   - 实现分页搜索API
   - 添加分类过滤和时间筛选
   - 记录搜索日志并分析热门关键词

3. **挑战任务**：
   - 实现中英文混合搜索
   - 构建搜索建议系统
   - 优化百万级数据的搜索性能

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**下一步**：查看 [CDC变更数据捕获案例](../change_data_capture/README.md)
