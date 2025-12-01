-- PostgreSQL 18 + pgvector 2.0 RAG知识库示例
-- 最后更新: 2025-11-11

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建知识库文档表
CREATE TABLE knowledge_base (
    id bigserial PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    -- 文档分块信息
    chunk_index int DEFAULT 0,
    chunk_total int DEFAULT 1,
    -- 元数据
    source text,
    category text,
    tags text[],
    -- 全文搜索向量（自动生成）
    content_tsv tsvector GENERATED ALWAYS AS (
        to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(content, ''))
    ) STORED,
    -- 向量嵌入（1536维，OpenAI text-embedding-3-large）
    embedding vector(1536),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 创建全文搜索索引（GIN）
CREATE INDEX idx_kb_tsv ON knowledge_base USING GIN (content_tsv);

-- 创建向量索引（HNSW，PostgreSQL 18 异步 I/O 提升性能 2-3 倍）⭐
CREATE INDEX idx_kb_embed ON knowledge_base USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 创建元数据索引
CREATE INDEX idx_kb_category ON knowledge_base (category);
CREATE INDEX idx_kb_tags ON knowledge_base USING GIN (tags);

-- 插入示例数据
INSERT INTO knowledge_base (title, content, source, category, tags, embedding) VALUES
('PostgreSQL向量搜索', 'PostgreSQL通过pgvector扩展支持向量相似度搜索，可以用于RAG知识库、语义搜索等场景...',
 '官方文档', '数据库', ARRAY['PostgreSQL', '向量搜索', 'pgvector'],
 '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'::vector(1536)),
('RAG架构设计', 'RAG（Retrieval-Augmented Generation）是一种结合检索和生成的AI架构，通过向量数据库检索相关文档，然后输入给LLM生成答案...',
 '技术博客', 'AI架构', ARRAY['RAG', 'AI', 'LLM'],
 '[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1]'::vector(1536)),
('PostgreSQL 18新特性', 'PostgreSQL 18引入了异步I/O子系统、虚拟生成列等新特性，显著提升了向量检索性能...',
 '发布说明', '数据库', ARRAY['PostgreSQL', '新特性', '性能优化'],
 '[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2]'::vector(1536));

-- 注意：实际使用时，embedding应该是完整的1536维向量
-- 这里仅作示例，实际向量需要从embedding模型（如OpenAI text-embedding-3-large）生成

-- RAG检索函数：混合检索（向量+全文）
CREATE OR REPLACE FUNCTION rag_retrieve(
    query_text text,
    query_vector vector(1536),
    top_k int DEFAULT 5,
    category_filter text DEFAULT NULL
)
RETURNS TABLE (
    id bigint,
    title text,
    content text,
    source text,
    category text,
    similarity numeric,
    rank int
) AS $$
BEGIN
    RETURN QUERY
    WITH 
    -- 向量相似度搜索
    vector_results AS (
        SELECT 
            kb.id,
            kb.title,
            kb.content,
            kb.source,
            kb.category,
            1 - (kb.embedding <=> query_vector) AS similarity,
            ROW_NUMBER() OVER (ORDER BY kb.embedding <=> query_vector) AS v_rank
        FROM knowledge_base kb
        WHERE kb.embedding IS NOT NULL
          AND (category_filter IS NULL OR kb.category = category_filter)
    ),
    -- 全文搜索
    text_results AS (
        SELECT 
            kb.id,
            kb.title,
            kb.content,
            kb.source,
            kb.category,
            ts_rank(kb.content_tsv, plainto_tsquery('simple', query_text)) AS similarity,
            ROW_NUMBER() OVER (ORDER BY ts_rank(kb.content_tsv, plainto_tsquery('simple', query_text)) DESC) AS t_rank
        FROM knowledge_base kb
        WHERE kb.content_tsv @@ plainto_tsquery('simple', query_text)
          AND (category_filter IS NULL OR kb.category = category_filter)
    ),
    -- RRF融合
    rrf_fusion AS (
        SELECT 
            COALESCE(v.id, t.id) AS id,
            COALESCE(v.title, t.title) AS title,
            COALESCE(v.content, t.content) AS content,
            COALESCE(v.source, t.source) AS source,
            COALESCE(v.category, t.category) AS category,
            -- RRF公式: 1/(60 + rank)
            COALESCE(1.0 / (60 + v.v_rank), 0) + 
            COALESCE(1.0 / (60 + t.t_rank), 0) AS combined_score,
            ROW_NUMBER() OVER (ORDER BY 
                COALESCE(1.0 / (60 + v.v_rank), 0) + 
                COALESCE(1.0 / (60 + t.t_rank), 0) DESC
            ) AS final_rank
        FROM vector_results v
        FULL OUTER JOIN text_results t ON v.id = t.id
    )
    SELECT 
        r.id,
        r.title,
        r.content,
        r.source,
        r.category,
        r.combined_score AS similarity,
        r.final_rank::int AS rank
    FROM rrf_fusion r
    ORDER BY r.final_rank
    LIMIT top_k;
END;
$$ LANGUAGE plpgsql;

-- 更新updated_at触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_kb_updated_at
    BEFORE UPDATE ON knowledge_base
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
