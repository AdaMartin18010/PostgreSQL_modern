-- 索引维护与统计更新示例
-- 1) 针对大表分批维护索引/统计
ANALYZE VERBOSE demo.events;

-- 2) 并发重建索引，降低锁影响（注意：不能在事务内）
-- REINDEX INDEX CONCURRENTLY demo.idx_events_user_ts;

-- 3) 针对误配索引的替换流程（创建新索引 -> 验证 -> 删除旧索引）
-- CREATE INDEX CONCURRENTLY idx_events_user_ts_v2 ON demo.events (user_id, ts DESC);
-- DROP INDEX CONCURRENTLY IF EXISTS idx_events_user_ts;

-- 4) 膨胀治理（示意）：
VACUUM (ANALYZE) demo.events;
-- 必要时：CLUSTER 或 pg_repack（外部工具）来回收空间
