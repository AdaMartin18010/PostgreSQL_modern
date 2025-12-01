-- PostgreSQL 18 + pgvector 2.0 医疗知识库示例
-- 最后更新: 2025-11-11
-- 特性：知识库检索 + 实验分支管理

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建医疗知识库表
CREATE TABLE medical_knowledge (
    id bigserial PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    category text,  -- 'diagnosis', 'treatment', 'drug', 'symptom'
    -- 文档分块信息
    chunk_index int DEFAULT 0,
    -- 元数据
    source text,
    tags text[],
    -- 全文搜索向量（自动生成）
    content_tsv tsvector GENERATED ALWAYS AS (
        to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(content, ''))
    ) STORED,
    -- 向量嵌入（1536维）
    embedding vector(1536),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 创建全文搜索索引（GIN）
CREATE INDEX idx_medical_tsv ON medical_knowledge USING GIN (content_tsv);

-- 创建向量索引（HNSW，PostgreSQL 18 异步 I/O 提升性能 2-3 倍）⭐
CREATE INDEX idx_medical_embed ON medical_knowledge USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 创建分类索引
CREATE INDEX idx_medical_category ON medical_knowledge (category);
CREATE INDEX idx_medical_tags ON medical_knowledge USING GIN (tags);

-- 插入示例数据
INSERT INTO medical_knowledge (title, content, category, source, tags, embedding) VALUES
('高血压诊断', '高血压是指血压持续升高的疾病，通常收缩压≥140mmHg或舒张压≥90mmHg...',
 'diagnosis', '医学教科书', ARRAY['高血压', '心血管', '诊断'],
 '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'::vector(1536)),
('高血压治疗', '高血压的治疗包括生活方式干预和药物治疗，常用药物包括ACE抑制剂、ARB等...',
 'treatment', '临床指南', ARRAY['高血压', '治疗', '药物'],
 '[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1]'::vector(1536)),
('糖尿病症状', '糖尿病的典型症状包括多饮、多尿、多食、体重下降等...',
 'symptom', '医学教科书', ARRAY['糖尿病', '症状', '内分泌'],
 '[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2]'::vector(1536));

-- 注意：实际使用时，embedding应该是完整的1536维向量
-- 这里仅作示例，实际向量需要从embedding模型生成

-- 医疗知识检索函数
CREATE OR REPLACE FUNCTION medical_search(
    query_text text,
    query_vector vector(1536),
    category_filter text DEFAULT NULL,
    top_k int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    title text,
    content text,
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
            mk.id,
            mk.title,
            mk.content,
            mk.category,
            1 - (mk.embedding <=> query_vector) AS similarity,
            ROW_NUMBER() OVER (ORDER BY mk.embedding <=> query_vector) AS v_rank
        FROM medical_knowledge mk
        WHERE mk.embedding IS NOT NULL
          AND (category_filter IS NULL OR mk.category = category_filter)
    ),
    -- 全文搜索
    text_results AS (
        SELECT 
            mk.id,
            mk.title,
            mk.content,
            mk.category,
            ts_rank(mk.content_tsv, plainto_tsquery('simple', query_text)) AS similarity,
            ROW_NUMBER() OVER (ORDER BY ts_rank(mk.content_tsv, plainto_tsquery('simple', query_text)) DESC) AS t_rank
        FROM medical_knowledge mk
        WHERE mk.content_tsv @@ plainto_tsquery('simple', query_text)
          AND (category_filter IS NULL OR mk.category = category_filter)
    ),
    -- RRF融合
    rrf_fusion AS (
        SELECT 
            COALESCE(v.id, t.id) AS id,
            COALESCE(v.title, t.title) AS title,
            COALESCE(v.content, t.content) AS content,
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
        r.category,
        r.combined_score AS similarity,
        r.final_rank::int AS rank
    FROM rrf_fusion r
    ORDER BY r.final_rank
    LIMIT top_k;
END;
$$ LANGUAGE plpgsql;

-- 更新updated_at触发器
CREATE OR REPLACE FUNCTION update_medical_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_medical_updated_at
    BEFORE UPDATE ON medical_knowledge
    FOR EACH ROW
    EXECUTE FUNCTION update_medical_updated_at();

-- 实验分支管理（模拟Neon分支功能）
-- 注意：实际Neon分支需要Neon平台，这里使用表分区模拟
CREATE TABLE medical_knowledge_experiment (
    LIKE medical_knowledge INCLUDING ALL,
    experiment_name text NOT NULL DEFAULT 'main'
) PARTITION BY LIST (experiment_name);

-- 主分支
CREATE TABLE medical_knowledge_main PARTITION OF medical_knowledge_experiment
    FOR VALUES IN ('main');

-- 实验分支示例
CREATE TABLE medical_knowledge_exp1 PARTITION OF medical_knowledge_experiment
    FOR VALUES IN ('experiment-v2');

-- 注意：实际使用Neon时，分支是独立的数据库实例，可以通过Neon API创建
