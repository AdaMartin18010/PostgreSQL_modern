-- PostgreSQL 18自动优化建议
-- 分析数据库并给出优化建议

CREATE OR REPLACE FUNCTION generate_optimization_suggestions()
RETURNS TABLE (
    category VARCHAR(50),
    severity VARCHAR(20),
    suggestion TEXT,
    current_value TEXT,
    recommended_value TEXT
) AS $$
BEGIN
    -- 1. 检查缺失的索引
    RETURN QUERY
    SELECT 
        'Index'::VARCHAR(50),
        'HIGH'::VARCHAR(20),
        'Table ' || schemaname || '.' || tablename || ' has seq_scan=' || seq_scan::text || 
        ' but no index scans. Consider adding index on frequently queried columns.'::TEXT,
        'No suitable index'::TEXT,
        'CREATE INDEX ON ' || schemaname || '.' || tablename || '(...)'::TEXT
    FROM pg_stat_user_tables
    WHERE seq_scan > 1000
      AND idx_scan = 0
      AND n_live_tup > 10000
    LIMIT 5;
    
    -- 2. 检查未使用的索引
    RETURN QUERY
    SELECT 
        'Index'::VARCHAR(50),
        'MEDIUM'::VARCHAR(20),
        'Index ' || schemaname || '.' || indexrelname || 
        ' is never used. Consider dropping it.'::TEXT,
        'idx_scan=0, size=' || pg_size_pretty(pg_relation_size(indexrelid))::TEXT,
        'DROP INDEX ' || schemaname || '.' || indexrelname::TEXT
    FROM pg_stat_user_indexes
    WHERE idx_scan = 0
      AND pg_relation_size(indexrelid) > 10 * 1024 * 1024  -- >10MB
    LIMIT 5;
    
    -- 3. 检查表膨胀
    RETURN QUERY
    SELECT 
        'Vacuum'::VARCHAR(50),
        CASE 
            WHEN dead_pct > 20 THEN 'HIGH'::VARCHAR(20)
            WHEN dead_pct > 10 THEN 'MEDIUM'::VARCHAR(20)
            ELSE 'LOW'::VARCHAR(20)
        END,
        'Table ' || schemaname || '.' || tablename || 
        ' has ' || dead_pct::text || '% dead tuples. Run VACUUM.'::TEXT,
        'dead_pct=' || dead_pct::text || '%'::TEXT,
        'VACUUM (ANALYZE, PARALLEL 4) ' || schemaname || '.' || tablename::TEXT
    FROM (
        SELECT 
            schemaname,
            tablename,
            ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_pct
        FROM pg_stat_user_tables
        WHERE n_dead_tup > 1000
    ) sub
    WHERE dead_pct > 10
    LIMIT 5;
    
    -- 4. 检查统计信息过期
    RETURN QUERY
    SELECT 
        'Statistics'::VARCHAR(50),
        'MEDIUM'::VARCHAR(20),
        'Table ' || schemaname || '.' || tablename || 
        ' statistics are outdated (last analyzed ' || 
        COALESCE(last_analyze::text, last_autoanalyze::text, 'never') || ')'::TEXT,
        'Last analyze: ' || COALESCE(last_analyze::text, 'never')::TEXT,
        'ANALYZE ' || schemaname || '.' || tablename::TEXT
    FROM pg_stat_user_tables
    WHERE (last_analyze IS NULL AND last_autoanalyze IS NULL)
       OR (last_analyze < NOW() - INTERVAL '7 days' 
           AND last_autoanalyze < NOW() - INTERVAL '7 days')
    LIMIT 5;
    
    -- 5. ⭐ PostgreSQL 18特性建议
    RETURN QUERY
    SELECT 
        'PG18 Feature'::VARCHAR(50),
        'MEDIUM'::VARCHAR(20),
        'Enable built-in connection pooling for better concurrency'::TEXT,
        current_setting('enable_builtin_connection_pooling')::TEXT,
        'ALTER SYSTEM SET enable_builtin_connection_pooling = on'::TEXT
    WHERE current_setting('enable_builtin_connection_pooling') = 'off';
    
    RETURN QUERY
    SELECT 
        'PG18 Feature'::VARCHAR(50),
        'MEDIUM'::VARCHAR(20),
        'Enable async I/O for better throughput'::TEXT,
        current_setting('enable_async_io')::TEXT,
        'ALTER SYSTEM SET enable_async_io = on'::TEXT
    WHERE current_setting('enable_async_io') = 'off';
    
    -- 6. 检查配置参数
    RETURN QUERY
    SELECT 
        'Configuration'::VARCHAR(50),
        'HIGH'::VARCHAR(20),
        'shared_buffers is too small. Should be ~25% of RAM.'::TEXT,
        current_setting('shared_buffers')::TEXT,
        'ALTER SYSTEM SET shared_buffers = ''32GB'''::TEXT
    WHERE pg_size_bytes(current_setting('shared_buffers')) < 1024 * 1024 * 1024  -- <1GB
    LIMIT 1;
    
    RETURN QUERY
    SELECT 
        'Configuration'::VARCHAR(50),
        'MEDIUM'::VARCHAR(20),
        'work_mem might be too small for large sorts/aggregations'::TEXT,
        current_setting('work_mem')::TEXT,
        'ALTER SYSTEM SET work_mem = ''256MB'''::TEXT
    WHERE pg_size_bytes(current_setting('work_mem')) < 64 * 1024 * 1024  -- <64MB
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- 使用示例
SELECT * FROM generate_optimization_suggestions()
ORDER BY 
    CASE severity 
        WHEN 'HIGH' THEN 1 
        WHEN 'MEDIUM' THEN 2 
        ELSE 3 
    END,
    category;
