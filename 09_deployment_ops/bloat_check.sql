-- PostgreSQL 表/索引膨胀检查脚本（生产级）
-- 版本：PostgreSQL 17+
-- 用途：监控表膨胀情况，识别需要VACUUM的表
-- 输出：表大小、膨胀率、索引大小、最后VACUUM时间

-- 设置输出格式
\pset format aligned
\pset null '(null)'

-- 创建临时函数：计算膨胀率
CREATE OR REPLACE FUNCTION get_bloat_ratio(relid OID)
RETURNS NUMERIC AS $$
DECLARE
    bloat_ratio NUMERIC;
BEGIN
    -- 使用pg_stat_user_tables的n_dead_tup和n_live_tup计算膨胀率
    SELECT 
        CASE 
            WHEN n_live_tup = 0 THEN 0
            ELSE ROUND((n_dead_tup::NUMERIC / (n_live_tup + n_dead_tup)::NUMERIC) * 100, 2)
        END
    INTO bloat_ratio
    FROM pg_stat_user_tables 
    WHERE pg_stat_user_tables.relid = $1;
    
    RETURN COALESCE(bloat_ratio, 0);
END;
$$ LANGUAGE plpgsql;

-- 主查询：表膨胀分析
WITH table_stats AS (
    SELECT 
        schemaname,
        tablename,
        relid,
        pg_table_size(relid) AS table_size_bytes,
        pg_total_relation_size(relid) AS total_size_bytes,
        pg_indexes_size(relid) AS indexes_size_bytes,
        n_live_tup,
        n_dead_tup,
        last_vacuum,
        last_autovacuum,
        last_analyze,
        last_autoanalyze,
        vacuum_count,
        autovacuum_count
    FROM pg_stat_user_tables
    WHERE schemaname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
),
bloat_analysis AS (
    SELECT 
        schemaname,
        tablename,
        table_size_bytes,
        total_size_bytes,
        indexes_size_bytes,
        n_live_tup,
        n_dead_tup,
        get_bloat_ratio(relid) AS bloat_ratio,
        last_vacuum,
        last_autovacuum,
        last_analyze,
        last_autoanalyze,
        vacuum_count,
        autovacuum_count,
        -- 计算建议的VACUUM优先级
        CASE 
            WHEN get_bloat_ratio(relid) > 20 THEN 'HIGH'
            WHEN get_bloat_ratio(relid) > 10 THEN 'MEDIUM'
            WHEN get_bloat_ratio(relid) > 5 THEN 'LOW'
            ELSE 'OK'
        END AS vacuum_priority
    FROM table_stats
)
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(table_size_bytes) AS table_size,
    pg_size_pretty(total_size_bytes) AS total_size,
    pg_size_pretty(indexes_size_bytes) AS indexes_size,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    bloat_ratio || '%' AS bloat_ratio,
    vacuum_priority,
    COALESCE(last_vacuum::TEXT, last_autovacuum::TEXT, 'Never') AS last_vacuum,
    COALESCE(last_analyze::TEXT, last_autoanalyze::TEXT, 'Never') AS last_analyze,
    vacuum_count + autovacuum_count AS total_vacuums
FROM bloat_analysis
WHERE total_size_bytes > 10 * 1024 * 1024  -- 只显示大于10MB的表
ORDER BY 
    bloat_ratio DESC,
    total_size_bytes DESC
LIMIT 50;

-- 清理临时函数
DROP FUNCTION IF EXISTS get_bloat_ratio(OID);

-- 输出总结信息
\echo ''
\echo '=== 膨胀检查总结 ==='
\echo 'HIGH: 膨胀率 > 20%, 建议立即VACUUM'
\echo 'MEDIUM: 膨胀率 10-20%, 建议尽快VACUUM'  
\echo 'LOW: 膨胀率 5-10%, 可安排VACUUM'
\echo 'OK: 膨胀率 < 5%, 状态良好'
\echo ''
\echo '建议操作：'
\echo '1. 对于HIGH优先级表，执行: VACUUM ANALYZE schema.table_name;'
\echo '2. 对于大量死元组，考虑: VACUUM FULL schema.table_name;'
\echo '3. 检查autovacuum配置是否合理'
\echo '4. 监控VACUUM执行时间和I/O影响'
