-- 分片倾斜检测（示例）
-- 目标：识别分片/节点级请求或数据量倾斜

-- 1) 基于统计表或路由日志的分布统计（示例结构，按实际表替换）
-- SELECT shard_id, count(*) AS req_cnt
-- FROM coordinator_query_log
-- WHERE ts >= now() - interval '10 minutes'
-- GROUP BY shard_id
-- ORDER BY req_cnt DESC;

-- 2) 倾斜度量：P95/P99 分片请求占比（示意）
-- WITH agg AS (
--   SELECT shard_id, count(*) AS req_cnt
--   FROM coordinator_query_log
--   WHERE ts >= now() - interval '10 minutes'
--   GROUP BY shard_id
-- )
-- SELECT percentile_cont(0.95) WITHIN GROUP (ORDER BY req_cnt) AS p95,
--        percentile_cont(0.99) WITHIN GROUP (ORDER BY req_cnt) AS p99
-- FROM agg;

-- 3) 热分片定位与重分布建议（示意输出）
-- SELECT shard_id, req_cnt
-- FROM (
--   SELECT shard_id, count(*) AS req_cnt
--   FROM coordinator_query_log
--   WHERE ts >= now() - interval '10 minutes'
--   GROUP BY shard_id
-- ) t
-- WHERE req_cnt > (SELECT percentile_cont(0.99) WITHIN GROUP (ORDER BY count(*))
--                  FROM coordinator_query_log
--                  WHERE ts >= now() - interval '10 minutes')
-- ORDER BY req_cnt DESC;


