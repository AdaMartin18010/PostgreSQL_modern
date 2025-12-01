-- PostgreSQL 向量与混合检索示例
-- 版本：PostgreSQL 12+ with pgvector extension
-- 用途：向量相似性搜索、混合检索、AI应用集成
-- 执行环境：需要安装pgvector扩展

-- =====================
-- 1. 环境准备
-- =====================

-- 1.1 安装pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 1.2 验证扩展安装
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- =====================
-- 2. 基础向量表设计
-- =====================

-- 2.1 文档向量表
CREATE TABLE IF NOT EXISTS documents (
    id bigserial PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    embedding vector(768),  -- OpenAI ada-002 维度
    metadata jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 2.2 用户向量表（推荐系统）
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id bigint PRIMARY KEY,
    username text UNIQUE NOT NULL,
    preferences vector(128),  -- 用户偏好向量
    demographics jsonb,
    created_at timestamptz DEFAULT now()
);

-- 2.3 商品向量表（电商推荐）
CREATE TABLE IF NOT EXISTS products (
    product_id bigserial PRIMARY KEY,
    name text NOT NULL,
    description text,
    category text,
    price decimal(10,2),
    embedding vector(512),  -- 商品特征向量
    tags text[],
    created_at timestamptz DEFAULT now()
);

-- =====================
-- 3. 向量索引创建
-- =====================

-- 3.1 HNSW索引（高性能近似最近邻）
-- 文档向量索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_hnsw 
ON documents USING hnsw (embedding vector_l2_ops) 
WITH (m = 32, ef_construction = 200);

-- 用户偏好向量索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_hnsw 
ON user_profiles USING hnsw (preferences vector_cosine_ops) 
WITH (m = 16, ef_construction = 100);

-- 商品向量索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_hnsw 
ON products USING hnsw (embedding vector_l2_ops) 
WITH (m = 24, ef_construction = 150);

-- 3.2 IVFFlat索引（精确搜索）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_ivfflat 
ON documents USING ivfflat (embedding vector_l2_ops) 
WITH (lists = 100);

-- =====================
-- 4. 基础向量搜索
-- =====================

-- 4.1 相似文档搜索
-- 使用L2距离（欧几里得距离）
SELECT 
    id,
    title,
    content,
    embedding <-> '[0.1,0.2,0.3,...]'::vector AS distance
FROM documents
ORDER BY embedding <-> '[0.1,0.2,0.3,...]'::vector
LIMIT 10;

-- 4.2 余弦相似度搜索
SELECT 
    id,
    title,
    content,
    1 - (embedding <=> '[0.1,0.2,0.3,...]'::vector) AS cosine_similarity
FROM documents
ORDER BY embedding <=> '[0.1,0.2,0.3,...]'::vector
LIMIT 10;

-- 4.3 内积搜索
SELECT 
    id,
    title,
    content,
    embedding <#> '[0.1,0.2,0.3,...]'::vector AS negative_inner_product
FROM documents
ORDER BY embedding <#> '[0.1,0.2,0.3,...]'::vector
LIMIT 10;

-- =====================
-- 5. 混合检索策略
-- =====================

-- 5.1 结构化 + 向量搜索
-- 结合时间过滤的向量搜索
WITH query_vector AS (
    SELECT '[0.1,0.2,0.3,...]'::vector AS qv
)
SELECT 
    d.id,
    d.title,
    d.content,
    d.embedding <-> qv.qv AS distance,
    d.created_at
FROM documents d, query_vector qv
WHERE d.created_at >= now() - interval '30 days'
ORDER BY d.embedding <-> qv.qv
LIMIT 20;

-- 5.2 分类 + 向量搜索
SELECT 
    p.product_id,
    p.name,
    p.description,
    p.price,
    p.embedding <-> '[0.1,0.2,0.3,...]'::vector AS distance
FROM products p
WHERE p.category = 'electronics'
  AND p.price BETWEEN 100 AND 1000
ORDER BY p.embedding <-> '[0.1,0.2,0.3,...]'::vector
LIMIT 15;

-- 5.3 全文搜索 + 向量搜索
-- 第一阶段：全文搜索筛选
WITH text_search AS (
    SELECT 
        id,
        title,
        content,
        ts_rank(to_tsvector('english', title || ' ' || content), 
                plainto_tsquery('english', 'machine learning')) AS text_rank
    FROM documents
    WHERE to_tsvector('english', title || ' ' || content) 
          @@ plainto_tsquery('english', 'machine learning')
    ORDER BY text_rank DESC
    LIMIT 100
),
-- 第二阶段：向量搜索
vector_search AS (
    SELECT 
        d.id,
        d.title,
        d.content,
        d.embedding <-> '[0.1,0.2,0.3,...]'::vector AS distance,
        ts.text_rank
    FROM documents d
    JOIN text_search ts ON d.id = ts.id
    ORDER BY d.embedding <-> '[0.1,0.2,0.3,...]'::vector
    LIMIT 20
)
-- 第三阶段：结果融合
SELECT 
    id,
    title,
    content,
    distance,
    text_rank,
    -- 综合评分（可调整权重）
    0.7 * (1 - distance) + 0.3 * text_rank AS combined_score
FROM vector_search
ORDER BY combined_score DESC;

-- =====================
-- 6. 推荐系统应用
-- =====================

-- 6.1 基于用户的协同过滤
-- 找到相似用户
WITH similar_users AS (
    SELECT 
        user_id,
        username,
        1 - (preferences <=> (SELECT preferences FROM user_profiles WHERE user_id = 123)) AS similarity
    FROM user_profiles
    WHERE user_id != 123
    ORDER BY preferences <=> (SELECT preferences FROM user_profiles WHERE user_id = 123)
    LIMIT 10
)
-- 推荐商品（基于相似用户的偏好）
SELECT 
    p.product_id,
    p.name,
    p.description,
    p.price,
    AVG(su.similarity) AS avg_similarity
FROM products p
JOIN similar_users su ON true  -- 这里需要实际的用户-商品交互数据
GROUP BY p.product_id, p.name, p.description, p.price
ORDER BY avg_similarity DESC
LIMIT 20;

-- 6.2 基于物品的协同过滤
-- 找到相似商品
SELECT 
    p2.product_id,
    p2.name,
    p2.description,
    p2.price,
    1 - (p1.embedding <=> p2.embedding) AS similarity
FROM products p1
CROSS JOIN products p2
WHERE p1.product_id = 456  -- 目标商品ID
  AND p2.product_id != 456
ORDER BY p1.embedding <=> p2.embedding
LIMIT 10;

-- =====================
-- 7. 向量搜索优化
-- =====================

-- 7.1 搜索参数调优
-- 设置HNSW搜索参数
SET hnsw.ef_search = 100;  -- 增加搜索精度，降低速度

-- 执行搜索
SELECT 
    id,
    title,
    embedding <-> '[0.1,0.2,0.3,...]'::vector AS distance
FROM documents
ORDER BY embedding <-> '[0.1,0.2,0.3,...]'::vector
LIMIT 10;

-- 7.2 批量向量搜索
-- 创建临时表存储查询向量
CREATE TEMP TABLE query_vectors (
    query_id int,
    vector vector(768)
);

INSERT INTO query_vectors VALUES 
(1, '[0.1,0.2,0.3,...]'::vector),
(2, '[0.4,0.5,0.6,...]'::vector),
(3, '[0.7,0.8,0.9,...]'::vector);

-- 批量搜索
SELECT 
    qv.query_id,
    d.id,
    d.title,
    d.embedding <-> qv.vector AS distance
FROM query_vectors qv
CROSS JOIN LATERAL (
    SELECT id, title, embedding
    FROM documents
    ORDER BY embedding <-> qv.vector
    LIMIT 5
) d
ORDER BY qv.query_id, distance;

-- =====================
-- 8. 向量数据管理
-- =====================

-- 8.1 向量数据插入
-- 插入文档向量
INSERT INTO documents (title, content, embedding, metadata) VALUES
('Machine Learning Basics', 'Introduction to machine learning concepts...', 
 '[0.1,0.2,0.3,...]'::vector, '{"author": "John Doe", "tags": ["ML", "AI"]}'),
('Deep Learning Guide', 'Comprehensive guide to deep learning...', 
 '[0.4,0.5,0.6,...]'::vector, '{"author": "Jane Smith", "tags": ["DL", "Neural Networks"]}');

-- 8.2 向量数据更新
UPDATE documents 
SET embedding = '[0.1,0.2,0.3,...]'::vector,
    updated_at = now()
WHERE id = 1;

-- 8.3 向量数据验证
-- 检查向量维度
SELECT 
    id,
    title,
    array_length(embedding, 1) AS vector_dimension
FROM documents
WHERE array_length(embedding, 1) != 768;

-- =====================
-- 9. 性能监控
-- =====================

-- 9.1 索引使用统计
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE indexname LIKE '%hnsw%' OR indexname LIKE '%ivfflat%'
ORDER BY idx_scan DESC;

-- 9.2 向量搜索性能测试
-- 创建测试函数
CREATE OR REPLACE FUNCTION test_vector_search_performance(
    test_vector vector(768),
    search_limit int DEFAULT 10
)
RETURNS TABLE(
    search_time interval,
    result_count int
) AS $$
DECLARE
    start_time timestamptz;
    end_time timestamptz;
    result_count int;
BEGIN
    start_time := clock_timestamp();
    
    SELECT COUNT(*) INTO result_count
    FROM (
        SELECT id
        FROM documents
        ORDER BY embedding <-> test_vector
        LIMIT search_limit
    ) t;
    
    end_time := clock_timestamp();
    
    RETURN QUERY SELECT 
        end_time - start_time,
        result_count;
END;
$$ LANGUAGE plpgsql;

-- 执行性能测试
SELECT * FROM test_vector_search_performance('[0.1,0.2,0.3,...]'::vector, 10);


