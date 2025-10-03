-- ========================================
-- RAG 向量检索查询示例集
-- ========================================

-- 示例1：基础向量相似度检索（Top-K）
-- 使用L2距离（欧几里得距离）
\echo '=== 示例1: 基础向量检索 ==='

-- 在psql中设置查询向量（384维示例，实际使用时需要完整向量）
-- \set query_vec '[0.01,0.02,0.03,...]'

-- 基础查询
-- SELECT 
--     id,
--     meta->>'title' as title,
--     meta->>'source' as source,
--     embedding <-> :query_vec::vector as distance
-- FROM rag.docs
-- ORDER BY embedding <-> :query_vec::vector
-- LIMIT 5;

-- ========================================
-- 示例2：结合元数据过滤的检索
-- ========================================
\echo '=== 示例2: 带元数据过滤的检索 ==='

-- 只检索特定来源的文档
-- SELECT 
--     id,
--     meta->>'title' as title,
--     meta->>'category' as category,
--     embedding <-> :query_vec::vector as distance
-- FROM rag.docs
-- WHERE meta->>'source' = 'technical_docs'
--   AND meta->>'category' = 'database'
-- ORDER BY embedding <-> :query_vec::vector
-- LIMIT 10;

-- ========================================
-- 示例3：使用余弦相似度
-- ========================================
\echo '=== 示例3: 余弦相似度检索 ==='

-- 余弦相似度：1 - cosine_distance
-- SELECT 
--     id,
--     meta->>'title' as title,
--     1 - (embedding <=> :query_vec::vector) as cosine_similarity,
--     embedding <=> :query_vec::vector as cosine_distance
-- FROM rag.docs
-- ORDER BY embedding <=> :query_vec::vector
-- LIMIT 5;

-- ========================================
-- 示例4：混合检索（向量 + 全文搜索）
-- ========================================
\echo '=== 示例4: 混合检索（向量+全文） ==='

-- 假设meta中有text字段
-- SELECT 
--     id,
--     meta->>'title' as title,
--     meta->>'text' as text_snippet,
--     embedding <-> :query_vec::vector as vec_distance,
--     ts_rank_cd(to_tsvector('english', meta->>'text'), 
--                plainto_tsquery('english', 'database performance')) as text_rank
-- FROM rag.docs
-- WHERE to_tsvector('english', meta->>'text') @@ 
--       plainto_tsquery('english', 'database performance')
-- ORDER BY 
--     embedding <-> :query_vec::vector ASC,
--     ts_rank_cd(to_tsvector('english', meta->>'text'), 
--                plainto_tsquery('english', 'database performance')) DESC
-- LIMIT 10;

-- ========================================
-- 示例5：批量查询（多个向量）
-- ========================================
\echo '=== 示例5: 批量向量查询 ==='

-- 使用临时表或CTE批量查询
-- WITH query_vectors AS (
--     SELECT 1 as query_id, '[0.01,0.02,...]'::vector as qvec
--     UNION ALL
--     SELECT 2 as query_id, '[0.05,0.06,...]'::vector as qvec
--     UNION ALL
--     SELECT 3 as query_id, '[0.10,0.11,...]'::vector as qvec
-- )
-- SELECT 
--     qv.query_id,
--     d.id as doc_id,
--     d.meta->>'title' as title,
--     d.embedding <-> qv.qvec as distance
-- FROM query_vectors qv
-- CROSS JOIN LATERAL (
--     SELECT id, meta, embedding
--     FROM rag.docs
--     ORDER BY embedding <-> qv.qvec
--     LIMIT 5
-- ) d
-- ORDER BY qv.query_id, distance;

-- ========================================
-- 示例6：范围查询（距离阈值）
-- ========================================
\echo '=== 示例6: 距离阈值过滤 ==='

-- 只返回距离小于阈值的结果
-- SELECT 
--     id,
--     meta->>'title' as title,
--     embedding <-> :query_vec::vector as distance
-- FROM rag.docs
-- WHERE embedding <-> :query_vec::vector < 0.5  -- 距离阈值
-- ORDER BY embedding <-> :query_vec::vector
-- LIMIT 20;

-- ========================================
-- 示例7：分页查询
-- ========================================
\echo '=== 示例7: 分页查询 ==='

-- 第一页（OFFSET 0）
-- SELECT 
--     id,
--     meta->>'title' as title,
--     embedding <-> :query_vec::vector as distance
-- FROM rag.docs
-- ORDER BY embedding <-> :query_vec::vector
-- LIMIT 10 OFFSET 0;

-- 第二页（OFFSET 10）
-- SELECT 
--     id,
--     meta->>'title' as title,
--     embedding <-> :query_vec::vector as distance
-- FROM rag.docs
-- ORDER BY embedding <-> :query_vec::vector
-- LIMIT 10 OFFSET 10;

-- ========================================
-- 示例8：性能分析查询
-- ========================================
\echo '=== 示例8: 查询性能分析 ==='

-- 使用EXPLAIN ANALYZE查看执行计划
-- EXPLAIN (ANALYZE, BUFFERS, TIMING)
-- SELECT 
--     id,
--     meta->>'title' as title,
--     embedding <-> :query_vec::vector as distance
-- FROM rag.docs
-- ORDER BY embedding <-> :query_vec::vector
-- LIMIT 5;

-- 检查索引使用情况
-- 应该看到 "Index Scan using idx_docs_hnsw"

-- ========================================
-- 示例9：多条件组合查询
-- ========================================
\echo '=== 示例9: 多条件组合查询 ==='

-- 结合时间范围、类别、向量相似度
-- SELECT 
--     id,
--     meta->>'title' as title,
--     meta->>'created_at' as created_at,
--     meta->>'category' as category,
--     embedding <-> :query_vec::vector as distance
-- FROM rag.docs
-- WHERE (meta->>'created_at')::timestamp > NOW() - INTERVAL '30 days'
--   AND meta->>'category' IN ('tech', 'database', 'ai')
--   AND meta->>'status' = 'published'
-- ORDER BY embedding <-> :query_vec::vector
-- LIMIT 10;

-- ========================================
-- 示例10：聚合统计查询
-- ========================================
\echo '=== 示例10: 检索结果聚合统计 ==='

-- 统计不同类别的平均距离
-- WITH top_results AS (
--     SELECT 
--         meta->>'category' as category,
--         embedding <-> :query_vec::vector as distance
--     FROM rag.docs
--     ORDER BY embedding <-> :query_vec::vector
--     LIMIT 100
-- )
-- SELECT 
--     category,
--     COUNT(*) as count,
--     AVG(distance) as avg_distance,
--     MIN(distance) as min_distance,
--     MAX(distance) as max_distance
-- FROM top_results
-- GROUP BY category
-- ORDER BY count DESC;

-- ========================================
-- 实用工具查询
-- ========================================

-- 检查向量维度
\echo '=== 检查向量维度 ==='
SELECT 
    'Vector dimension' as info,
    vector_dims(embedding) as dimensions
FROM rag.docs
LIMIT 1;

-- 统计文档数量
\echo '=== 文档统计 ==='
SELECT 
    COUNT(*) as total_docs,
    COUNT(DISTINCT meta->>'source') as unique_sources,
    COUNT(DISTINCT meta->>'category') as unique_categories
FROM rag.docs;

-- 检查索引状态
\echo '=== 索引状态检查 ==='
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE tablename = 'docs' AND schemaname = 'rag';

-- ========================================
-- 性能调优参数
-- ========================================

-- 调整HNSW查询参数（会话级别）
-- SET hnsw.ef_search = 40;  -- 默认值，增加可提高召回率但降低速度

-- 调整工作内存（会话级别）
-- SET work_mem = '256MB';

\echo '=== 查询示例说明 ==='
\echo '请取消注释相应的查询并提供实际的查询向量'
\echo '在psql中使用: \\set query_vec ''[0.01,0.02,...]'''
\echo '然后执行对应的SELECT语句'
