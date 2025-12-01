-- PostgreSQL 18 + pgvector 2.0 基础向量搜索示例
-- 最后更新: 2025-11-11

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建文档表
CREATE TABLE documents (
    id bigserial PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    embedding vector(384),  -- 384维向量（示例）
    created_at timestamptz DEFAULT now()
);

-- 创建HNSW索引（PostgreSQL 18 异步 I/O 提升性能 2-3 倍）⭐
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 插入示例数据
INSERT INTO documents (title, content, embedding) VALUES
('PostgreSQL简介', 'PostgreSQL是一个强大的开源关系型数据库管理系统...',
 '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'::vector(384)),
('向量数据库', '向量数据库用于存储和检索高维向量数据，支持相似度搜索...',
 '[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1]'::vector(384)),
('AI集成', 'PostgreSQL通过pgvector扩展支持AI模型集成和向量检索...',
 '[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2]'::vector(384));

-- 注意：实际使用时，embedding应该是完整的384维向量
-- 这里仅作示例，实际向量需要从embedding模型生成
