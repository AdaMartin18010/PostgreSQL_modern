-- 跨分片 JOIN 观测（示例）
-- 目标：识别路由（单分片）与重分布（跨分片）执行计划

EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT o.order_id, c.customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= now() - interval '7 days';

-- 观察要点：
-- - 是否出现 Repartition / Redistribute / Gather 等分布式算子
-- - 输入表是否为广播表或引用表以避免重分布
-- - 倾斜：单个分片任务耗时/数据量显著高于中位


