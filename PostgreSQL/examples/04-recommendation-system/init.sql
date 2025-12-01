-- PostgreSQL 18 + pgvector 2.0 智能推荐系统示例
-- 最后更新: 2025-11-11
-- 特性：使用虚拟生成列实现动态相似度计算

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建用户表
CREATE TABLE users (
    id bigserial PRIMARY KEY,
    username text NOT NULL UNIQUE,
    -- 用户特征向量（基于历史行为生成）
    user_embedding vector(384),
    created_at timestamptz DEFAULT now()
);

-- 创建内容表
CREATE TABLE contents (
    id bigserial PRIMARY KEY,
    title text NOT NULL,
    description text,
    category text,
    -- 内容特征向量
    content_embedding vector(384),
    created_at timestamptz DEFAULT now()
);

-- 创建用户-内容交互表
CREATE TABLE user_interactions (
    id bigserial PRIMARY KEY,
    user_id bigint REFERENCES users(id),
    content_id bigint REFERENCES contents(id),
    interaction_type text,  -- 'view', 'like', 'share', 'purchase'
    interaction_score numeric DEFAULT 1.0,
    created_at timestamptz DEFAULT now(),
    UNIQUE(user_id, content_id, interaction_type)
);

-- PostgreSQL 18: 创建推荐结果表（使用虚拟生成列）⭐
CREATE TABLE recommendations (
    id bigserial PRIMARY KEY,
    user_id bigint REFERENCES users(id),
    content_id bigint REFERENCES contents(id),
    -- 查询时动态计算的相似度向量
    query_vector vector(384),
    -- PostgreSQL 18: 虚拟生成列 - 动态计算相似度 ⭐⭐
    similarity_score FLOAT GENERATED ALWAYS AS (
        1 - (
            (SELECT user_embedding FROM users WHERE id = user_id) <=>
            (SELECT content_embedding FROM contents WHERE id = content_id)
        )
    ) STORED,
    -- 历史交互分数
    interaction_score numeric DEFAULT 0,
    -- 综合推荐分数（相似度 + 交互）
    combined_score numeric GENERATED ALWAYS AS (
        (1 - (
            (SELECT user_embedding FROM users WHERE id = user_id) <=>
            (SELECT content_embedding FROM contents WHERE id = content_id)
        )) * 0.7 + interaction_score * 0.3
    ) STORED,
    created_at timestamptz DEFAULT now()
);

-- 创建向量索引（HNSW，PostgreSQL 18 异步 I/O 提升性能 2-3 倍）⭐
CREATE INDEX idx_users_embed ON users USING hnsw (user_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_contents_embed ON contents USING hnsw (content_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 创建推荐分数索引（利用虚拟生成列）
CREATE INDEX idx_recommendations_score ON recommendations (combined_score DESC);
CREATE INDEX idx_recommendations_user ON recommendations (user_id, combined_score DESC);

-- 插入示例数据
INSERT INTO users (username, user_embedding) VALUES
('user1', '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'::vector(384)),
('user2', '[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1]'::vector(384)),
('user3', '[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2]'::vector(384));

INSERT INTO contents (title, description, category, content_embedding) VALUES
('PostgreSQL教程', '深入学习PostgreSQL数据库的使用和优化...', '技术', '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(384)),
('向量数据库指南', '了解如何使用pgvector进行向量搜索...', '技术', '[0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05,0.15]'::vector(384)),
('AI集成实践', 'PostgreSQL与AI模型的深度集成方案...', '技术', '[0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05,0.15,0.25]'::vector(384));

-- 注意：实际使用时，embedding应该是完整的384维向量
-- 这里仅作示例，实际向量需要从embedding模型生成

-- 推荐函数：基于向量相似度和交互历史
CREATE OR REPLACE FUNCTION get_recommendations(
    p_user_id bigint,
    p_limit int DEFAULT 10,
    p_exclude_interacted boolean DEFAULT true
)
RETURNS TABLE (
    content_id bigint,
    title text,
    description text,
    category text,
    similarity_score numeric,
    interaction_score numeric,
    combined_score numeric
) AS $$
BEGIN
    RETURN QUERY
    WITH user_embedding AS (
        SELECT user_embedding AS vec
        FROM users
        WHERE id = p_user_id
    ),
    user_interacted AS (
        SELECT DISTINCT content_id
        FROM user_interactions
        WHERE user_id = p_user_id
    ),
    candidate_contents AS (
        SELECT 
            c.id,
            c.title,
            c.description,
            c.category,
            c.content_embedding,
            -- 计算相似度
            1 - (c.content_embedding <=> u.vec) AS similarity,
            -- 计算交互分数
            COALESCE(
                SUM(ui.interaction_score) FILTER (WHERE ui.user_id = p_user_id),
                0
            ) AS interaction
        FROM contents c
        CROSS JOIN user_embedding u
        LEFT JOIN user_interactions ui ON c.id = ui.content_id AND ui.user_id = p_user_id
        WHERE (NOT p_exclude_interacted OR c.id NOT IN (SELECT content_id FROM user_interacted))
        GROUP BY c.id, c.title, c.description, c.category, c.content_embedding, u.vec
    )
    SELECT 
        cc.id AS content_id,
        cc.title,
        cc.description,
        cc.category,
        cc.similarity AS similarity_score,
        cc.interaction AS interaction_score,
        -- 综合分数：相似度70% + 交互30%
        cc.similarity * 0.7 + cc.interaction * 0.3 AS combined_score
    FROM candidate_contents cc
    ORDER BY combined_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- 更新推荐表（批量生成推荐）
CREATE OR REPLACE FUNCTION refresh_recommendations(
    p_user_id bigint,
    p_limit int DEFAULT 100
)
RETURNS void AS $$
BEGIN
    -- 删除旧推荐
    DELETE FROM recommendations WHERE user_id = p_user_id;
    
    -- 插入新推荐
    INSERT INTO recommendations (user_id, content_id, query_vector, interaction_score)
    SELECT 
        p_user_id,
        content_id,
        (SELECT user_embedding FROM users WHERE id = p_user_id),
        COALESCE(
            (SELECT SUM(interaction_score) 
             FROM user_interactions 
             WHERE user_id = p_user_id AND content_id = rec.content_id),
            0
        )
    FROM get_recommendations(p_user_id, p_limit, true) rec;
END;
$$ LANGUAGE plpgsql;
