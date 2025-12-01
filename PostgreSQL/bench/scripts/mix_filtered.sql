-- 结构化过滤 + 混合查询脚本
-- 用于 pgbench 压测
-- 使用方法: pgbench -c 32 -j 32 -T 300 -f mix_filtered.sql postgres

\set qv random(1, 1000)
\set kw random(1, 5)
\set keyword :kw
\set query_vector :qv

WITH filtered AS (
    SELECT id, text, embedding
    FROM docs
    WHERE created_at >= now() - interval '30 days'
      AND category = 'tech'
),
text_search AS (
    SELECT id, ts_rank(to_tsvector('simple', text), plainto_tsquery('simple', :keyword)) AS tr
    FROM filtered
    WHERE to_tsvector('simple', text) @@ plainto_tsquery('simple', :keyword)
    ORDER BY tr DESC LIMIT 500
),
vector_search AS (
    SELECT id, embedding <-> (SELECT embedding FROM docs WHERE id = :query_vector LIMIT 1) AS dist
    FROM filtered
    WHERE id IN (SELECT id FROM text_search)
    ORDER BY dist ASC LIMIT 100
)
SELECT count(*) FROM vector_search;
