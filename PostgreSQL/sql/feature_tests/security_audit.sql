-- PostgreSQL 17.x 安全审计功能测试
-- 版本：PostgreSQL 17+
-- 用途：测试pgaudit扩展和审计功能
-- 执行环境：PostgreSQL 17+ 或兼容版本

-- =====================
-- 1. 环境准备
-- =====================

-- 1.1 检查PostgreSQL版本和扩展
SELECT version();
SELECT extname, extversion FROM pg_extension WHERE extname = 'pgaudit';

-- 1.2 创建测试环境
CREATE SCHEMA IF NOT EXISTS ft_sec_audit;
SET search_path TO ft_sec_audit, public;

-- =====================
-- 2. 审计配置
-- =====================

-- 2.1 检查pgaudit配置
SELECT 
    name,
    setting,
    context,
    short_desc
FROM pg_settings 
WHERE name LIKE '%pgaudit%';

-- 2.2 创建审计表
DROP TABLE IF EXISTS audit_log CASCADE;
CREATE TABLE audit_log (
    id bigserial PRIMARY KEY,
    timestamp timestamptz DEFAULT now(),
    user_name text,
    database_name text,
    session_id text,
    command_tag text,
    statement text,
    audit_type text,
    object_name text,
    object_type text,
    result text,
    client_addr inet,
    application_name text
);

-- 2.3 创建审计函数
CREATE OR REPLACE FUNCTION log_audit_event()
RETURNS trigger AS $$
BEGIN
    INSERT INTO audit_log (
        user_name,
        database_name,
        command_tag,
        statement,
        audit_type,
        object_name,
        object_type,
        result
    ) VALUES (
        current_user,
        current_database(),
        TG_OP,
        current_query(),
        TG_OP,
        TG_TABLE_NAME,
        'TABLE',
        CASE 
            WHEN TG_OP = 'INSERT' THEN 'SUCCESS'
            WHEN TG_OP = 'UPDATE' THEN 'SUCCESS'
            WHEN TG_OP = 'DELETE' THEN 'SUCCESS'
            ELSE 'UNKNOWN'
        END
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- =====================
-- 3. 测试表创建
-- =====================

-- 3.1 创建敏感数据表
DROP TABLE IF EXISTS sensitive_data CASCADE;
CREATE TABLE sensitive_data (
    id bigserial PRIMARY KEY,
    user_id text NOT NULL,
    personal_info jsonb NOT NULL,
    financial_data jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by text DEFAULT current_user,
    updated_by text DEFAULT current_user
);

-- 3.2 创建审计触发器
CREATE TRIGGER audit_sensitive_data_trigger
    AFTER INSERT OR UPDATE OR DELETE ON sensitive_data
    FOR EACH ROW EXECUTE FUNCTION log_audit_event();

-- 3.3 创建索引
CREATE INDEX idx_audit_log_timestamp ON audit_log (timestamp);
CREATE INDEX idx_audit_log_user ON audit_log (user_name);
CREATE INDEX idx_audit_log_type ON audit_log (audit_type);
CREATE INDEX idx_audit_log_object ON audit_log (object_name);

-- =====================
-- 4. 数据操作审计测试
-- =====================

-- 4.1 插入敏感数据
INSERT INTO sensitive_data (user_id, personal_info, financial_data) VALUES
('USER001', 
 '{"name": "John Doe", "email": "john@example.com", "phone": "+1-555-0123"}',
 '{"salary": 75000, "bank_account": "****1234", "credit_score": 750}'),
('USER002',
 '{"name": "Jane Smith", "email": "jane@example.com", "phone": "+1-555-0456"}',
 '{"salary": 85000, "bank_account": "****5678", "credit_score": 780}'),
('USER003',
 '{"name": "Bob Wilson", "email": "bob@example.com", "phone": "+1-555-0789"}',
 '{"salary": 65000, "bank_account": "****9012", "credit_score": 720}');

-- 4.2 更新敏感数据
UPDATE sensitive_data 
SET personal_info = jsonb_set(personal_info, '{email}', '"john.doe.updated@example.com"'),
    updated_at = now(),
    updated_by = current_user
WHERE user_id = 'USER001';

-- 4.3 删除敏感数据
DELETE FROM sensitive_data WHERE user_id = 'USER003';

-- 4.4 查看审计日志
SELECT 
    timestamp,
    user_name,
    audit_type,
    object_name,
    result,
    statement
FROM audit_log
ORDER BY timestamp DESC
LIMIT 10;

-- =====================
-- 5. 权限审计测试
-- =====================

-- 5.1 创建测试用户
DO $$
BEGIN
    -- 创建审计测试用户
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'audit_test_user') THEN
        EXECUTE 'CREATE ROLE audit_test_user WITH LOGIN PASSWORD ''test_password''';
        RAISE NOTICE 'Test user audit_test_user created';
    END IF;
END $$;

-- 5.2 授权测试
GRANT USAGE ON SCHEMA ft_sec_audit TO audit_test_user;
GRANT SELECT, INSERT, UPDATE ON sensitive_data TO audit_test_user;
GRANT SELECT ON audit_log TO audit_test_user;

-- 5.3 模拟用户操作（需要切换到audit_test_user）
-- 注意：以下操作需要在audit_test_user会话中执行
/*
SET ROLE audit_test_user;

-- 尝试访问敏感数据
SELECT user_id, personal_info->>'name' as name 
FROM sensitive_data 
WHERE user_id = 'USER001';

-- 尝试更新数据
UPDATE sensitive_data 
SET personal_info = jsonb_set(personal_info, '{name}', '"John Updated"')
WHERE user_id = 'USER001';

-- 尝试插入新数据
INSERT INTO sensitive_data (user_id, personal_info) VALUES
('USER004', '{"name": "Test User", "email": "test@example.com"}');

-- 重置角色
RESET ROLE;
*/

-- =====================
-- 6. 行级安全审计
-- =====================

-- 6.1 启用行级安全
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- 6.2 创建RLS策略
CREATE POLICY user_data_policy ON sensitive_data
    FOR ALL TO audit_test_user
    USING (user_id = current_user);

-- 6.3 创建RLS审计函数
CREATE OR REPLACE FUNCTION audit_rls_access()
RETURNS trigger AS $$
BEGIN
    INSERT INTO audit_log (
        user_name,
        database_name,
        command_tag,
        statement,
        audit_type,
        object_name,
        object_type,
        result
    ) VALUES (
        current_user,
        current_database(),
        'RLS_ACCESS',
        current_query(),
        'RLS_ACCESS',
        TG_TABLE_NAME,
        'TABLE',
        'RLS_POLICY_APPLIED'
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 6.4 创建RLS审计触发器
CREATE TRIGGER audit_rls_trigger
    AFTER SELECT ON sensitive_data
    FOR EACH ROW EXECUTE FUNCTION audit_rls_access();

-- =====================
-- 7. 数据脱敏和匿名化
-- =====================

-- 7.1 创建数据脱敏函数
CREATE OR REPLACE FUNCTION mask_personal_info(data jsonb)
RETURNS jsonb AS $$
BEGIN
    RETURN jsonb_build_object(
        'name', CASE 
            WHEN data ? 'name' THEN 
                left(data->>'name', 1) || repeat('*', length(data->>'name') - 1)
            ELSE NULL 
        END,
        'email', CASE 
            WHEN data ? 'email' THEN 
                split_part(data->>'email', '@', 1) || '@***.***'
            ELSE NULL 
        END,
        'phone', CASE 
            WHEN data ? 'phone' THEN 
                '***-***-' || right(data->>'phone', 4)
            ELSE NULL 
        END
    );
END;
$$ LANGUAGE plpgsql;

-- 7.2 创建财务数据脱敏函数
CREATE OR REPLACE FUNCTION mask_financial_data(data jsonb)
RETURNS jsonb AS $$
BEGIN
    RETURN jsonb_build_object(
        'salary', CASE 
            WHEN data ? 'salary' THEN 
                round((data->>'salary')::numeric / 10000) * 10000
            ELSE NULL 
        END,
        'bank_account', CASE 
            WHEN data ? 'bank_account' THEN 
                '****' || right(data->>'bank_account', 4)
            ELSE NULL 
        END,
        'credit_score', CASE 
            WHEN data ? 'credit_score' THEN 
                round((data->>'credit_score')::numeric / 50) * 50
            ELSE NULL 
        END
    );
END;
$$ LANGUAGE plpgsql;

-- 7.3 测试数据脱敏
SELECT 
    user_id,
    mask_personal_info(personal_info) as masked_personal_info,
    mask_financial_data(financial_data) as masked_financial_data
FROM sensitive_data;

-- =====================
-- 8. 审计报告生成
-- =====================

-- 8.1 用户活动报告
SELECT 
    user_name,
    audit_type,
    count(*) as activity_count,
    min(timestamp) as first_activity,
    max(timestamp) as last_activity
FROM audit_log
WHERE timestamp >= now() - interval '1 day'
GROUP BY user_name, audit_type
ORDER BY activity_count DESC;

-- 8.2 对象访问报告
SELECT 
    object_name,
    audit_type,
    count(*) as access_count,
    count(DISTINCT user_name) as unique_users
FROM audit_log
WHERE timestamp >= now() - interval '1 day'
GROUP BY object_name, audit_type
ORDER BY access_count DESC;

-- 8.3 安全事件报告
SELECT 
    'Security Events Summary' as report_type,
    count(*) as total_events,
    count(*) FILTER (WHERE audit_type = 'INSERT') as insert_events,
    count(*) FILTER (WHERE audit_type = 'UPDATE') as update_events,
    count(*) FILTER (WHERE audit_type = 'DELETE') as delete_events,
    count(*) FILTER (WHERE audit_type = 'RLS_ACCESS') as rls_events
FROM audit_log
WHERE timestamp >= now() - interval '1 day';

-- =====================
-- 9. 合规性检查
-- =====================

-- 9.1 GDPR合规检查
SELECT 
    'GDPR Compliance Check' as check_type,
    count(*) as total_records,
    count(*) FILTER (WHERE personal_info ? 'email') as records_with_email,
    count(*) FILTER (WHERE personal_info ? 'phone') as records_with_phone,
    count(*) FILTER (WHERE personal_info ? 'name') as records_with_name
FROM sensitive_data;

-- 9.2 数据保留策略检查
SELECT 
    'Data Retention Check' as check_type,
    count(*) as total_records,
    count(*) FILTER (WHERE created_at < now() - interval '7 years') as old_records,
    min(created_at) as oldest_record,
    max(created_at) as newest_record
FROM sensitive_data;

-- 9.3 访问权限检查
SELECT 
    'Access Control Check' as check_type,
    schemaname,
    tablename,
    hasinserts,
    hasselects,
    hasupdates,
    hasdeletes
FROM pg_tables t
LEFT JOIN pg_stat_user_tables s ON t.tablename = s.relname
WHERE schemaname = 'ft_sec_audit';

-- =====================
-- 10. 清理和总结
-- =====================

-- 10.1 显示审计摘要
SELECT 
    'Security Audit Test Summary' AS test_name,
    count(*) AS total_audit_events,
    count(DISTINCT user_name) AS unique_users,
    count(DISTINCT object_name) AS unique_objects,
    min(timestamp) AS first_event,
    max(timestamp) AS last_event
FROM audit_log;

-- 10.2 清理测试数据
-- DROP ROLE IF EXISTS audit_test_user;
-- DROP SCHEMA IF EXISTS ft_sec_audit CASCADE;

-- =====================
-- 11. 最佳实践建议
-- =====================

/*
安全审计最佳实践：

1. 审计配置：
   - 启用pgaudit扩展进行详细审计
   - 配置适当的审计级别（READ, WRITE, FUNCTION等）
   - 定期审查审计日志大小和性能影响

2. 数据保护：
   - 实施行级安全策略
   - 使用数据脱敏和匿名化技术
   - 定期进行合规性检查

3. 监控和告警：
   - 设置异常访问模式告警
   - 监控特权用户活动
   - 定期生成安全报告

4. 合规要求：
   - 遵循GDPR、SOX、PCI DSS等法规
   - 实施数据保留和删除策略
   - 维护审计轨迹完整性

5. 性能优化：
   - 合理配置审计参数
   - 使用分区表管理审计日志
   - 定期清理历史审计数据

6. 安全考虑：
   - 保护审计日志不被篡改
   - 限制审计日志访问权限
   - 使用加密保护敏感审计信息
*/