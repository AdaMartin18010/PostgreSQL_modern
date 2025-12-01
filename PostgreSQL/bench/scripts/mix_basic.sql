-- 基础混合查询脚本（全文 + 向量）
-- 用于 pgbench 压测
-- 使用方法: pgbench -c 32 -j 32 -T 300 -f mix_basic.sql postgres

\set qv random(1, 1000)
\set kw random(1, 5)
\set keyword :kw
\set query_vector :qv

WITH s AS (
  SELECT id, ts_rank(to_tsvector('simple', text), plainto_tsquery('simple', :keyword)) AS tr
  FROM docs
  WHERE to_tsvector('simple', text) @@ plainto_tsquery('simple', :keyword)
  ORDER BY tr DESC LIMIT 500
), v AS (
  SELECT id, embedding <-> (SELECT embedding FROM docs WHERE id = :query_vector LIMIT 1) AS dist 
  FROM docs 
  WHERE id IN (SELECT id FROM s) 
  ORDER BY dist ASC LIMIT 100
)
SELECT count(*) FROM v;
