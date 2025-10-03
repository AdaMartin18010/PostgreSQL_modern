-- PostgreSQL 17 vs 16: VACUUM性能测试
-- 测试VACUUM内存管理优化的效果

\set ECHO all
\timing on

-- ===========================================
-- 1. 准备测试数据
-- ===========================================

DROP TABLE IF EXISTS large_table CASCADE;

CREATE TABLE large_table (
    id bigserial PRIMARY KEY,
    user_id bigint NOT NULL,
    content text NOT NULL,
    status text NOT NULL,
    score int NOT NULL DEFAULT 0,
    updated_at timestamptz DEFAULT now()
);

-- 插入5000万条数据（约5GB）
INSERT INTO large_table (user_id, content, status, score)
SELECT
    (random() * 1000000)::bigint,
    md5(random()::text),
    (ARRAY['active', 'inactive', 'pending', 'deleted'])[1 + (random() * 3)::int],
    (random() * 100)::int
FROM generate_series(1, 50000000);

CREATE INDEX idx_large_table_user ON large_table(user_id);
CREATE INDEX idx_large_table_status ON large_table(status);

VACUUM ANALYZE large_table;

\echo '========================================='
\echo '测试数据准备完成：50,000,000条记录'
SELECT pg_size_pretty(pg_total_relation_size('large_table')) AS table_size;
\echo '========================================='

-- ===========================================
-- 2. 模拟更新操作（产生dead tuples）
-- ===========================================

\echo ''
\echo '模拟频繁更新操作（10%的行）...'

UPDATE large_table
SET status = 'updated', updated_at = now()
WHERE id % 10 = 0;

\echo '更新完成，dead tuples已产生'

-- 查看表膨胀情况
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio
FROM pg_stat_user_tables
WHERE tablename = 'large_table';

-- ===========================================
-- 3. 执行VACUUM（测试核心）
-- ===========================================

\echo ''
\echo '【核心测试】执行VACUUM ANALYZE'
\echo '关注：执行时间、内存使用、I/O量'
\echo ''

-- 开始监控
\echo 'VACUUM开始时间：' :NOW

VACUUM (ANALYZE, VERBOSE) large_table;

\echo 'VACUUM完成！'

-- ===========================================
-- 4. VACUUM后统计
-- ===========================================

\echo ''
\echo '【VACUUM后统计】'

SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio,
    last_vacuum,
    last_analyze
FROM pg_stat_user_tables
WHERE tablename = 'large_table';

-- ===========================================
-- 5. Autovacuum配置测试
-- ===========================================

\echo ''
\echo '【Autovacuum配置测试】'

-- 调整autovacuum参数
ALTER TABLE large_table SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_vacuum_threshold = 1000,
    autovacuum_analyze_scale_factor = 0.02,
    autovacuum_analyze_threshold = 500
);

-- 查看配置
SELECT
    relname,
    reloptions
FROM pg_class
WHERE relname = 'large_table';

-- 再次更新产生dead tuples
\echo ''
\echo '再次更新10%的行，测试autovacuum触发...'

UPDATE large_table
SET score = score + 1, updated_at = now()
WHERE id % 10 = 1;

-- 手动触发autovacuum（模拟）
VACUUM (ANALYZE) large_table;

-- ===========================================
-- 6. VACUUM vs VACUUM FULL对比
-- ===========================================

\echo ''
\echo '【VACUUM vs VACUUM FULL对比】'

-- 记录VACUUM FULL前的大小
SELECT pg_size_pretty(pg_total_relation_size('large_table')) AS size_before_vacuum_full;

-- 注意：VACUUM FULL会锁表，生产环境需谨慎
\echo ''
\echo '执行VACUUM FULL (锁表操作，测试环境专用)...'

-- 取消注释以执行VACUUM FULL
-- VACUUM FULL large_table;

-- SELECT pg_size_pretty(pg_total_relation_size('large_table')) AS size_after_vacuum_full;

\echo ''
\echo 'VACUUM FULL测试跳过（避免长时间锁表）'

-- ===========================================
-- 7. 清理
-- ===========================================

\echo ''
\echo '测试完成！'
\echo ''
\echo '性能对比要点：'
\echo '1. 比较VACUUM执行时间'
\echo '2. 查看PostgreSQL日志中的内存使用峰值'
\echo '3. 比较I/O读写量（shared hit/read/written）'
\echo '4. PG17预期有30-40%的性能提升'
\echo ''
\echo '监控命令：'
\echo '  SELECT * FROM pg_stat_bgwriter;'
\echo '  SELECT * FROM pg_stat_progress_vacuum;'

\timing off

