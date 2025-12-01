-- PostgreSQL 18 + pgvector 2.0 混合搜索（RRF）示例
-- 最后更新: 2025-11-11

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建商品表（电商场景）
CREATE TABLE products (
    id bigserial PRIMARY KEY,
    name text NOT NULL,
    description text NOT NULL,
    category text,
    price numeric(10,2),
    -- 全文搜索向量（自动生成）
    description_tsv tsvector GENERATED ALWAYS AS (
        to_tsvector('simple', coalesce(name, '') || ' ' || coalesce(description, ''))
    ) STORED,
    -- 向量嵌入（384维）
    embedding vector(384),
    created_at timestamptz DEFAULT now()
);

-- 创建全文搜索索引（GIN）
CREATE INDEX idx_products_tsv ON products USING GIN (description_tsv);

-- 创建向量索引（HNSW，PostgreSQL 18 异步 I/O 提升性能 2-3 倍）⭐
CREATE INDEX idx_products_embed ON products USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 插入示例数据
INSERT INTO products (name, description, category, price, embedding) VALUES
('PostgreSQL数据库', 'PostgreSQL是一个强大的开源关系型数据库管理系统，支持向量搜索和全文搜索...', '数据库', 0.00,
 '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'::vector(384)),
('向量数据库教程', '学习如何使用pgvector扩展在PostgreSQL中实现向量相似度搜索和混合检索...', '教程', 99.99,
 '[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1]'::vector(384)),
('AI集成指南', 'PostgreSQL通过pgvector扩展支持AI模型集成，实现语义搜索和智能推荐...', '指南', 199.99,
 '[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2]'::vector(384));

-- 注意：实际使用时，embedding应该是完整的384维向量
-- 这里仅作示例，实际向量需要从embedding模型生成

-- RRF（Reciprocal Rank Fusion）融合查询函数
CREATE OR REPLACE FUNCTION hybrid_search_rrf(
    query_text text,
    query_vector vector(384),
    limit_count int DEFAULT 10
)
RETURNS TABLE (
    id bigint,
    name text,
    description text,
    category text,
    price numeric,
    combined_score numeric
) AS $$
BEGIN
    RETURN QUERY
    WITH 
    -- 全文搜索结果
    text_results AS (
        SELECT 
            p.id,
            p.name,
            p.description,
            p.category,
            p.price,
            ts_rank(p.description_tsv, plainto_tsquery('simple', query_text)) AS text_score,
            ROW_NUMBER() OVER (ORDER BY ts_rank(p.description_tsv, plainto_tsquery('simple', query_text)) DESC) AS text_rank
        FROM products p
        WHERE p.description_tsv @@ plainto_tsquery('simple', query_text)
    ),
    -- 向量搜索结果
    vector_results AS (
        SELECT 
            p.id,
            p.name,
            p.description,
            p.category,
            p.price,
            1 - (p.embedding <=> query_vector) AS vector_score,
            ROW_NUMBER() OVER (ORDER BY p.embedding <=> query_vector) AS vector_rank
        FROM products p
        WHERE p.embedding IS NOT NULL
    ),
    -- RRF融合
    rrf_fusion AS (
        SELECT 
            COALESCE(t.id, v.id) AS id,
            COALESCE(t.name, v.name) AS name,
            COALESCE(t.description, v.description) AS description,
            COALESCE(t.category, v.category) AS category,
            COALESCE(t.price, v.price) AS price,
            -- RRF公式: 1/(60 + rank)
            COALESCE(1.0 / (60 + t.text_rank), 0) + 
            COALESCE(1.0 / (60 + v.vector_rank), 0) AS combined_score
        FROM text_results t
        FULL OUTER JOIN vector_results v ON t.id = v.id
    )
    SELECT 
        r.id,
        r.name,
        r.description,
        r.category,
        r.price,
        r.combined_score
    FROM rrf_fusion r
    ORDER BY r.combined_score DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;
