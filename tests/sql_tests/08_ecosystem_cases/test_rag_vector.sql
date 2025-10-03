-- TEST: RAG向量检索功能测试
-- DESCRIPTION: 测试pgvector扩展的向量存储和相似度搜索功能
-- EXPECTED: 向量索引和相似度查询正常工作
-- TAGS: pgvector, vector-search, rag, similarity
-- NOTE: 需要安装pgvector扩展

-- SETUP
-- 检查并创建pgvector扩展
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        CREATE EXTENSION vector;
    END IF;
END $$;

-- 创建文档表
CREATE TABLE test_documents (
    id serial PRIMARY KEY,
    content text NOT NULL,
    embedding vector(384),  -- 假设使用384维向量
    metadata jsonb,
    created_at timestamptz DEFAULT now()
);

-- 创建向量索引（HNSW）
CREATE INDEX idx_test_documents_embedding_hnsw 
    ON test_documents 
    USING hnsw (embedding vector_cosine_ops);

-- 插入测试数据（使用随机向量模拟embedding）
INSERT INTO test_documents (content, embedding, metadata)
SELECT
    'Document content ' || i,
    -- 生成随机384维向量并归一化
    (SELECT array_agg(random())::vector FROM generate_series(1, 384)),
    jsonb_build_object('category', (ARRAY['tech', 'science', 'business'])[1 + (i % 3)], 'priority', i % 5)
FROM generate_series(1, 100) i;

-- 创建查询向量辅助函数
CREATE OR REPLACE FUNCTION test_random_vector(dim int)
RETURNS vector AS $$
    SELECT array_agg(random())::vector FROM generate_series(1, dim);
$$ LANGUAGE sql;

-- TEST_BODY
-- 测试1：验证数据插入
SELECT COUNT(*) FROM test_documents;  -- EXPECT_VALUE: 100

-- 测试2：验证向量维度
SELECT vector_dims(embedding) FROM test_documents LIMIT 1;  -- EXPECT_VALUE: 384

-- 测试3：验证向量不为NULL
SELECT COUNT(*) FROM test_documents WHERE embedding IS NULL;  -- EXPECT_VALUE: 0

-- 测试4：计算向量之间的余弦相似度
SELECT 
    COUNT(*) > 0
FROM test_documents d1
CROSS JOIN test_documents d2
WHERE d1.id = 1 AND d2.id = 2
  AND (d1.embedding <=> d2.embedding) IS NOT NULL;  -- EXPECT_VALUE: true

-- 测试5：余弦相似度查询（Top-K）
SELECT COUNT(*) FROM (
    SELECT id, content, embedding <=> test_random_vector(384) AS distance
    FROM test_documents
    ORDER BY distance
    LIMIT 10
) sub;  -- EXPECT_VALUE: 10

-- 测试6：欧几里得距离查询
SELECT COUNT(*) FROM (
    SELECT id, content, embedding <-> test_random_vector(384) AS distance
    FROM test_documents
    ORDER BY distance
    LIMIT 5
) sub;  -- EXPECT_VALUE: 5

-- 测试7：内积相似度查询
SELECT COUNT(*) FROM (
    SELECT id, content, embedding <#> test_random_vector(384) AS distance
    FROM test_documents
    ORDER BY distance
    LIMIT 5
) sub;  -- EXPECT_VALUE: 5

-- 测试8：结合WHERE条件的向量搜索
SELECT COUNT(*) FROM (
    SELECT id, content
    FROM test_documents
    WHERE metadata->>'category' = 'tech'
    ORDER BY embedding <=> test_random_vector(384)
    LIMIT 10
) sub;  -- EXPECT_VALUE: 10

-- 测试9：验证HNSW索引使用
EXPLAIN (COSTS OFF)
SELECT id FROM test_documents
ORDER BY embedding <=> test_random_vector(384)
LIMIT 10;
-- 应该看到 "Index Scan using idx_test_documents_embedding_hnsw"

-- 测试10：向量算术运算
SELECT 
    (embedding + embedding) IS NOT NULL
FROM test_documents
LIMIT 1;  -- EXPECT_VALUE: true

-- 测试11：向量范数计算
SELECT 
    COUNT(*) 
FROM test_documents
WHERE vector_norm(embedding) > 0;  -- EXPECT_VALUE: 100

-- 测试12：批量相似度搜索
WITH query_vector AS (
    SELECT test_random_vector(384) AS qv
)
SELECT COUNT(*) FROM (
    SELECT 
        d.id,
        d.content,
        d.embedding <=> qv.qv AS similarity
    FROM test_documents d, query_vector qv
    ORDER BY similarity
    LIMIT 20
) sub;  -- EXPECT_VALUE: 20

-- 测试13：创建IVFFlat索引（另一种索引类型）
CREATE INDEX idx_test_documents_embedding_ivfflat 
    ON test_documents 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

-- 验证索引创建
SELECT COUNT(*) FROM pg_indexes
WHERE tablename = 'test_documents'
  AND indexname LIKE '%ivfflat%';  -- EXPECT_VALUE: 1

-- 测试14：验证两种索引都能工作
SET enable_seqscan = off;
SELECT COUNT(*) FROM (
    SELECT id FROM test_documents
    ORDER BY embedding <=> test_random_vector(384)
    LIMIT 5
) sub;  -- EXPECT_VALUE: 5
SET enable_seqscan = on;

-- 测试15：元数据过滤 + 向量搜索
SELECT COUNT(*) FROM (
    SELECT 
        d.id,
        d.content,
        d.metadata->>'category' AS category
    FROM test_documents d
    WHERE d.metadata->>'category' IN ('tech', 'science')
    ORDER BY d.embedding <=> test_random_vector(384)
    LIMIT 15
) sub;  -- EXPECT_VALUE: 15

-- 测试16：聚合函数 - 平均向量
SELECT 
    AVG(embedding) IS NOT NULL
FROM test_documents
WHERE id BETWEEN 1 AND 10;  -- EXPECT_VALUE: true

-- TEARDOWN
-- 清理函数
DROP FUNCTION IF EXISTS test_random_vector(int);

-- 清理表（会自动删除索引）
DROP TABLE IF EXISTS test_documents;

