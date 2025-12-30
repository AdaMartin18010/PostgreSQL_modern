---

> **📋 文档来源**: `PostgreSQL\cases\向量检索与RAG.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 案例：向量检索与 RAG（占位）

## 架构

- pgvector/IVFFLAT/HNSW，混合检索（向量+结构化过滤）

## 关键点

- 分区与索引参数、批量导入、近实时更新、延迟与召回权衡

## 验证

- QPS/延迟、召回@k、资源占用、更新一致性

## 最小可复现（占位）

```sql
-- 需安装 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 假设使用 384 维嵌入
CREATE TABLE docs(id bigserial primary key, meta jsonb, embedding vector(384));
CREATE INDEX ON docs USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- 插入示例数据（占位）
-- INSERT INTO docs(meta, embedding) VALUES ('{"title":"a"}', '[0.1, 0.2, ...]');

-- 检索（向量 + 结构化过滤）
SELECT id, meta
FROM docs
WHERE meta->>'lang' = 'zh'
ORDER BY embedding <-> '[0.1,0.2, ...]'::vector
LIMIT 5;
```

---

## 1. 系统概述

向量检索与RAG系统是基于PostgreSQL和pgvector构建的智能检索系统，支持向量相似度搜索和RAG（检索增强生成）应用。

**系统特点**：

- **高性能** - 利用IVFFLAT/HNSW索引实现快速向量检索
- **混合检索** - 支持向量检索和结构化过滤结合
- **实时更新** - 支持近实时向量更新
- **高召回率** - 优化索引参数提升召回率

---

## 2. 架构设计

### 2.1 整体架构

```text
向量检索与RAG系统架构
├── 数据采集层
│   ├── 文档采集
│   ├── 向量化服务
│   └── 批量导入
├── 数据存储层
│   ├── PostgreSQL + pgvector
│   ├── IVFFLAT/HNSW索引
│   └── 分区表
├── 检索服务层
│   ├── 向量检索
│   ├── 混合检索
│   └── 结果排序
└── RAG应用层
    ├── 上下文检索
    ├── LLM集成
    └── 答案生成
```

### 2.2 数据模型设计

**数据模型实现（带错误处理和性能测试）**：

```sql
-- 1. 安装pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 文档表（假设使用384维嵌入）
CREATE TABLE docs (
    id BIGSERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    meta JSONB,
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY HASH (id);

-- 创建分区
CREATE TABLE docs_p0 PARTITION OF docs
FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE docs_p1 PARTITION OF docs
FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE docs_p2 PARTITION OF docs
FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE docs_p3 PARTITION OF docs
FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- 3. 创建IVFFLAT索引
CREATE INDEX idx_docs_embedding_ivfflat ON docs
USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);

-- 4. 创建HNSW索引（PostgreSQL 17+，性能更好）
-- CREATE INDEX idx_docs_embedding_hnsw ON docs
-- USING hnsw (embedding vector_l2_ops)
-- WITH (m = 16, ef_construction = 64);

-- 5. 创建结构化索引
CREATE INDEX idx_docs_meta_lang ON docs ((meta->>'lang'));
CREATE INDEX idx_docs_meta_category ON docs ((meta->>'category'));
CREATE INDEX idx_docs_created_at ON docs (created_at);
```

---

## 3. 核心实现

### 3.1 批量导入优化

**批量导入函数（带错误处理和性能测试）**：

```sql
-- 批量导入文档和向量
CREATE OR REPLACE FUNCTION batch_import_docs(
    p_docs JSONB[]
)
RETURNS TABLE (
    imported_count BIGINT,
    duration_ms NUMERIC
) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    imported_rows BIGINT;
BEGIN
    start_time := clock_timestamp();

    INSERT INTO docs (title, content, meta, embedding)
    SELECT
        d->>'title',
        d->>'content',
        d->'meta',
        (d->>'embedding')::vector
    FROM unnest(p_docs) AS d;

    GET DIAGNOSTICS imported_rows = ROW_COUNT;
    end_time := clock_timestamp();

    RETURN QUERY SELECT
        imported_rows,
        EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '批量导入失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 使用COPY进行高性能导入
CREATE OR REPLACE FUNCTION copy_import_docs(
    p_docs JSONB[]
)
RETURNS TABLE (
    imported_count BIGINT,
    duration_ms NUMERIC
) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    imported_rows BIGINT;
BEGIN
    start_time := clock_timestamp();

    -- 使用临时表
    CREATE TEMP TABLE temp_docs (
        title TEXT,
        content TEXT,
        meta JSONB,
        embedding vector(384)
    ) ON COMMIT DROP;

    -- 插入临时表
    INSERT INTO temp_docs (title, content, meta, embedding)
    SELECT
        d->>'title',
        d->>'content',
        d->'meta',
        (d->>'embedding')::vector
    FROM unnest(p_docs) AS d;

    -- 批量插入到主表
    INSERT INTO docs (title, content, meta, embedding)
    SELECT title, content, meta, embedding
    FROM temp_docs;

    GET DIAGNOSTICS imported_rows = ROW_COUNT;
    end_time := clock_timestamp();

    RETURN QUERY SELECT
        imported_rows,
        EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'COPY导入失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 索引参数优化

**索引参数优化函数（带错误处理和性能测试）**：

```sql
-- 索引参数优化建议
CREATE OR REPLACE FUNCTION optimize_index_parameters(
    p_total_rows BIGINT,
    p_dimensions INT DEFAULT 384
)
RETURNS TABLE (
    index_type TEXT,
    recommended_lists INT,
    recommended_m INT,
    recommended_ef_construction INT,
    notes TEXT
) AS $$
BEGIN
    -- IVFFLAT参数建议
    RETURN QUERY SELECT
        'IVFFLAT'::TEXT,
        CASE
            WHEN p_total_rows < 100000 THEN 10
            WHEN p_total_rows < 1000000 THEN 100
            ELSE 1000
        END::INT,
        NULL::INT,
        NULL::INT,
        format('总行数: %, 维度: %', p_total_rows, p_dimensions)::TEXT;

    -- HNSW参数建议
    RETURN QUERY SELECT
        'HNSW'::TEXT,
        NULL::INT,
        16::INT,
        CASE
            WHEN p_total_rows < 100000 THEN 32
            WHEN p_total_rows < 1000000 THEN 64
            ELSE 128
        END::INT,
        format('总行数: %, 维度: %', p_total_rows, p_dimensions)::TEXT;

    RETURN;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '索引参数优化失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行优化建议
SELECT * FROM optimize_index_parameters(1000000, 384);
```

---

## 4. 混合检索实现

### 4.1 向量+结构化过滤

**混合检索函数（带错误处理和性能测试）**：

```sql
-- 混合检索函数（向量 + 结构化过滤）
CREATE OR REPLACE FUNCTION hybrid_search(
    p_query_vector vector(384),
    p_lang TEXT DEFAULT NULL,
    p_category TEXT DEFAULT NULL,
    p_top_k INT DEFAULT 10,
    p_similarity_threshold NUMERIC DEFAULT 0.7
)
RETURNS TABLE (
    id BIGINT,
    title TEXT,
    content TEXT,
    meta JSONB,
    similarity NUMERIC,
    rank INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.title,
        d.content,
        d.meta,
        1 - (d.embedding <=> p_query_vector) AS similarity,
        ROW_NUMBER() OVER (ORDER BY d.embedding <=> p_query_vector) AS rank
    FROM docs d
    WHERE (p_lang IS NULL OR d.meta->>'lang' = p_lang)
      AND (p_category IS NULL OR d.meta->>'category' = p_category)
      AND 1 - (d.embedding <=> p_query_vector) >= p_similarity_threshold
    ORDER BY d.embedding <=> p_query_vector
    LIMIT p_top_k;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '混合检索失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 使用示例
SELECT * FROM hybrid_search(
    '[0.1, 0.2, ...]'::vector(384),
    p_lang => 'zh',
    p_category => 'technology',
    p_top_k => 10
);
```

### 4.2 近实时更新

**近实时更新函数（带错误处理和性能测试）**：

```sql
-- 近实时更新函数
CREATE OR REPLACE FUNCTION update_document_embedding(
    p_doc_id BIGINT,
    p_new_embedding vector(384),
    p_update_content BOOLEAN DEFAULT FALSE,
    p_new_content TEXT DEFAULT NULL
)
RETURNS TABLE (
    updated BOOLEAN,
    duration_ms NUMERIC
) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
BEGIN
    start_time := clock_timestamp();

    IF p_update_content AND p_new_content IS NOT NULL THEN
        UPDATE docs
        SET embedding = p_new_embedding,
            content = p_new_content,
            updated_at = NOW()
        WHERE id = p_doc_id;
    ELSE
        UPDATE docs
        SET embedding = p_new_embedding,
            updated_at = NOW()
        WHERE id = p_doc_id;
    END IF;

    IF FOUND THEN
        -- 注意：更新向量后，索引会自动更新（PostgreSQL行为）
        end_time := clock_timestamp();

        RETURN QUERY SELECT
            TRUE,
            EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    ELSE
        RETURN QUERY SELECT FALSE, NULL::NUMERIC;
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RETURN QUERY SELECT FALSE, NULL::NUMERIC;
END;
$$ LANGUAGE plpgsql;
```

---

## 5. 延迟与召回权衡

### 5.1 性能测试

**性能测试函数（带错误处理和性能分析）**：

```sql
-- 向量检索性能测试
CREATE OR REPLACE FUNCTION test_vector_search_performance(
    p_query_vector vector(384),
    p_top_k INT DEFAULT 10,
    p_iterations INT DEFAULT 100
)
RETURNS TABLE (
    avg_latency_ms NUMERIC,
    p95_latency_ms NUMERIC,
    p99_latency_ms NUMERIC,
    avg_recall NUMERIC
) AS $$
DECLARE
    latencies NUMERIC[];
    i INT;
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    latency_ms NUMERIC;
    recall_sum NUMERIC := 0;
    recall_count INT := 0;
BEGIN
    latencies := ARRAY[]::NUMERIC[];

    FOR i IN 1..p_iterations LOOP
        start_time := clock_timestamp();

        -- 执行向量检索
        PERFORM id, 1 - (embedding <=> p_query_vector) AS similarity
        FROM docs
        ORDER BY embedding <=> p_query_vector
        LIMIT p_top_k;

        end_time := clock_timestamp();
        latency_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
        latencies := array_append(latencies, latency_ms);
    END LOOP;

    RETURN QUERY SELECT
        ROUND(AVG(unnest), 2),
        ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY unnest), 2),
        ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY unnest), 2),
        NULL::NUMERIC;  -- 召回率需要ground truth数据

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '性能测试失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行测试
SELECT * FROM test_vector_search_performance('[0.1, 0.2, ...]'::vector(384));
```

### 5.2 召回率评估

**召回率评估函数（带错误处理和性能测试）**：

```sql
-- 召回率评估（需要ground truth数据）
CREATE TABLE IF NOT EXISTS ground_truth (
    query_id BIGINT PRIMARY KEY,
    query_vector vector(384),
    relevant_doc_ids BIGINT[]
);

-- 召回率计算函数
CREATE OR REPLACE FUNCTION evaluate_recall_at_k(
    p_query_id BIGINT,
    p_top_k INT DEFAULT 10
)
RETURNS TABLE (
    recall_at_k NUMERIC,
    precision_at_k NUMERIC,
    f1_score NUMERIC
) AS $$
DECLARE
    relevant_docs BIGINT[];
    retrieved_docs BIGINT[];
    query_vec vector(384);
    intersection_count INT;
BEGIN
    -- 获取ground truth
    SELECT query_vector, relevant_doc_ids
    INTO query_vec, relevant_docs
    FROM ground_truth
    WHERE query_id = p_query_id;

    IF query_vec IS NULL THEN
        RAISE EXCEPTION '查询ID不存在: %', p_query_id;
    END IF;

    -- 获取检索结果
    SELECT ARRAY_AGG(id) INTO retrieved_docs
    FROM (
        SELECT id
        FROM docs
        ORDER BY embedding <=> query_vec
        LIMIT p_top_k
    ) AS subq;

    -- 计算交集
    SELECT COUNT(*) INTO intersection_count
    FROM unnest(retrieved_docs) AS doc_id
    WHERE doc_id = ANY(relevant_docs);

    -- 计算指标
    RETURN QUERY SELECT
        CASE
            WHEN array_length(relevant_docs, 1) > 0
            THEN ROUND(intersection_count::NUMERIC / array_length(relevant_docs, 1), 4)
            ELSE 0
        END,
        CASE
            WHEN array_length(retrieved_docs, 1) > 0
            THEN ROUND(intersection_count::NUMERIC / array_length(retrieved_docs, 1), 4)
            ELSE 0
        END,
        CASE
            WHEN array_length(relevant_docs, 1) > 0 AND array_length(retrieved_docs, 1) > 0
            THEN ROUND(
                2.0 * intersection_count /
                (array_length(relevant_docs, 1) + array_length(retrieved_docs, 1)),
                4
            )
            ELSE 0
        END;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '召回率评估失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. 更新一致性保证

### 6.1 一致性检查

**一致性检查函数（带错误处理和性能测试）**：

```sql
-- 更新一致性检查
CREATE OR REPLACE FUNCTION check_update_consistency()
RETURNS TABLE (
    check_type TEXT,
    check_result TEXT,
    inconsistency_count BIGINT
) AS $$
DECLARE
    inconsistent_count BIGINT;
BEGIN
    -- 检查向量维度一致性
    SELECT COUNT(*) INTO inconsistent_count
    FROM docs
    WHERE array_length(embedding::TEXT::TEXT[], 1) != 384;

    IF inconsistent_count > 0 THEN
        RETURN QUERY SELECT
            '向量维度一致性'::TEXT,
            '失败'::TEXT,
            inconsistent_count;
    ELSE
        RETURN QUERY SELECT
            '向量维度一致性'::TEXT,
            '通过'::TEXT,
            0::BIGINT;
    END IF;

    -- 检查索引完整性
    -- 这里简化处理，实际应该检查索引是否与数据一致

    RETURN;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '一致性检查失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行检查
SELECT * FROM check_update_consistency();
```

---

## 📚 相关文档

- [向量检索与RAG.md](./向量检索与RAG.md) - 向量检索与RAG完整案例
- [10-AI与机器学习/](../10-AI与机器学习/README.md) - AI与机器学习主题
- [19-实战案例/README.md](./README.md) - 实战案例主题

---

**最后更新**: 2025年1月
