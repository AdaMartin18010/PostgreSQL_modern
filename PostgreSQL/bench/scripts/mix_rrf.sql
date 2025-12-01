-- RRF 融合查询脚本
-- 用于 pgbench 压测
-- 使用方法: pgbench -c 32 -j 32 -T 300 -f mix_rrf.sql postgres

\set qv random(1, 1000)
\set kw random(1, 5)
\set keyword :kw
\set query_vector :qv

WITH vector_results AS (
    SELECT id, 
           ROW_NUMBER() OVER (ORDER BY embedding <-> (SELECT embedding FROM docs WHERE id = :query_vector LIMIT 1)) AS vec_rank
    FROM docs
    WHERE embedding IS NOT NULL
    ORDER BY embedding <-> (SELECT embedding FROM docs WHERE id = :query_vector LIMIT 1)
    LIMIT 50
),
fulltext_results AS (
    SELECT id,
           ROW_NUMBER() OVER (
               ORDER BY ts_rank(to_tsvector('simple', text), plainto_tsquery('simple', :keyword)) DESC
           ) AS text_rank
    FROM docs
    WHERE to_tsvector('simple', text) @@ plainto_tsquery('simple', :keyword)
    LIMIT 50
)
SELECT
    COALESCE(v.id, f.id) AS id,
    COALESCE(1.0 / (60 + v.vec_rank), 0) + COALESCE(1.0 / (60 + f.text_rank), 0) AS rrf_score
FROM vector_results v
FULL OUTER JOIN fulltext_results f ON v.id = f.id
ORDER BY rrf_score DESC
LIMIT 10;
