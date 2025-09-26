﻿-- 查询占位：:query_embedding 为参数
-- 示例：在 psql 或应用层传入数组并转换为 vector
-- SELECT id, meta FROM rag.docs
-- ORDER BY embedding <-> :query_embedding
-- LIMIT 5;

-- psql 参数化示例：
-- \set q '(0.01,0.02,0.03, ... ,0.04)'
-- SELECT id, meta
-- FROM rag.docs
-- ORDER BY embedding <-> (:q)::vector
-- LIMIT 5;
