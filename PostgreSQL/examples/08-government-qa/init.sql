-- PostgreSQL 18 + pgvector 2.0 政务智能问答示例
-- 最后更新: 2025-11-11
-- 特性：知识库检索 + 数据脱敏 + 审计日志

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建政务知识库表
CREATE TABLE government_knowledge (
    id bigserial PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    category text,  -- 'policy', 'regulation', 'service', 'faq'
    department text,  -- 部门
    -- 敏感信息标记
    is_sensitive boolean DEFAULT false,
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
CREATE INDEX idx_gov_tsv ON government_knowledge USING GIN (content_tsv);

-- 创建向量索引（HNSW，PostgreSQL 18 异步 I/O 提升性能 2-3 倍）⭐
CREATE INDEX idx_gov_embed ON government_knowledge USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 创建分类索引
CREATE INDEX idx_gov_category ON government_knowledge (category);
CREATE INDEX idx_gov_department ON government_knowledge (department);

-- 创建审计日志表
CREATE TABLE audit_log (
    id bigserial PRIMARY KEY,
    user_id text,
    action text,  -- 'search', 'view', 'export'
    resource_id bigint,
    resource_type text,
    query_text text,
    ip_address inet,
    created_at timestamptz DEFAULT now()
);

-- 创建审计日志索引
CREATE INDEX idx_audit_user_time ON audit_log (user_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_log (action, created_at DESC);

-- 插入示例数据
INSERT INTO government_knowledge (title, content, category, department, is_sensitive, embedding) VALUES
('社保缴费政策', '企业职工基本养老保险缴费比例为...', 'policy', '人社局', false,
 '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'::vector(1536)),
('个人所得税申报', '年度个人所得税汇算清缴时间为...', 'service', '税务局', false,
 '[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1]'::vector(1536)),
('数据安全规定', '涉及个人隐私的数据需要严格保护...', 'regulation', '网信办', true,  -- 敏感信息
 '[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2]'::vector(1536));

-- 注意：实际使用时，embedding应该是完整的1536维向量
-- 这里仅作示例，实际向量需要从embedding模型生成

-- 智能问答函数（带权限控制）
CREATE OR REPLACE FUNCTION government_qa(
    query_text text,
    query_vector vector(1536),
    p_user_role text DEFAULT 'public',  -- 'public', 'staff', 'admin'
    top_k int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    title text,
    content text,
    category text,
    department text,
    similarity numeric,
    rank int
) AS $$
BEGIN
    -- 记录审计日志
    INSERT INTO audit_log (user_id, action, query_text)
    VALUES (current_user, 'search', query_text);
    
    RETURN QUERY
    WITH 
    -- 向量相似度搜索
    vector_results AS (
        SELECT 
            gk.id,
            gk.title,
            -- 数据脱敏：敏感信息需要权限
            CASE 
                WHEN gk.is_sensitive AND p_user_role NOT IN ('staff', 'admin') THEN
                    '[敏感信息，需要授权查看]'
                ELSE gk.content
            END AS content,
            gk.category,
            gk.department,
            1 - (gk.embedding <=> query_vector) AS similarity,
            ROW_NUMBER() OVER (ORDER BY gk.embedding <=> query_vector) AS v_rank
        FROM government_knowledge gk
        WHERE gk.embedding IS NOT NULL
          -- 权限过滤：普通用户不能查看敏感信息
          AND (NOT gk.is_sensitive OR p_user_role IN ('staff', 'admin'))
    ),
    -- 全文搜索
    text_results AS (
        SELECT 
            gk.id,
            gk.title,
            CASE 
                WHEN gk.is_sensitive AND p_user_role NOT IN ('staff', 'admin') THEN
                    '[敏感信息，需要授权查看]'
                ELSE gk.content
            END AS content,
            gk.category,
            gk.department,
            ts_rank(gk.content_tsv, plainto_tsquery('simple', query_text)) AS similarity,
            ROW_NUMBER() OVER (ORDER BY ts_rank(gk.content_tsv, plainto_tsquery('simple', query_text)) DESC) AS t_rank
        FROM government_knowledge gk
        WHERE gk.content_tsv @@ plainto_tsquery('simple', query_text)
          AND (NOT gk.is_sensitive OR p_user_role IN ('staff', 'admin'))
    ),
    -- RRF融合
    rrf_fusion AS (
        SELECT 
            COALESCE(v.id, t.id) AS id,
            COALESCE(v.title, t.title) AS title,
            COALESCE(v.content, t.content) AS content,
            COALESCE(v.category, t.category) AS category,
            COALESCE(v.department, t.department) AS department,
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
        r.department,
        r.combined_score AS similarity,
        r.final_rank::int AS rank
    FROM rrf_fusion r
    ORDER BY r.final_rank
    LIMIT top_k;
END;
$$ LANGUAGE plpgsql;

-- 更新updated_at触发器
CREATE OR REPLACE FUNCTION update_gov_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_gov_updated_at
    BEFORE UPDATE ON government_knowledge
    FOR EACH ROW
    EXECUTE FUNCTION update_gov_updated_at();

-- 查看审计日志函数
CREATE OR REPLACE FUNCTION view_audit_log(
    p_start_time timestamptz DEFAULT now() - INTERVAL '24 hours',
    p_end_time timestamptz DEFAULT now()
)
RETURNS TABLE (
    user_id text,
    action text,
    query_text text,
    created_at timestamptz
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.user_id,
        al.action,
        al.query_text,
        al.created_at
    FROM audit_log al
    WHERE al.created_at BETWEEN p_start_time AND p_end_time
    ORDER BY al.created_at DESC;
END;
$$ LANGUAGE plpgsql;

