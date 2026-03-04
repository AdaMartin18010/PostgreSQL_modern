# DCA安全审计指南

> **文档类型**: 安全审计与合规
> **适用范围**: 生产环境安全加固
> **更新日期**: 2026-03-04

---

## 目录

- [DCA安全审计指南](#dca安全审计指南)
  - [目录](#目录)
  - [1. 安全基线配置](#1-安全基线配置)
    - [1.1 最小权限原则](#11-最小权限原则)
    - [1.2 行级安全(RLS)完整配置](#12-行级安全rls完整配置)
  - [2. 审计日志配置](#2-审计日志配置)
    - [2.1 详细审计触发器](#21-详细审计触发器)
  - [3. 合规检查清单](#3-合规检查清单)
    - [3.1 自动合规检查脚本](#31-自动合规检查脚本)
  - [4. 安全扫描脚本](#4-安全扫描脚本)

---

## 1. 安全基线配置

### 1.1 最小权限原则

```sql
-- ============================================
-- 创建角色层次结构
-- ============================================

-- 1. 创建应用角色
CREATE ROLE app_readonly NOLOGIN;
CREATE ROLE app_readwrite NOLOGIN;
CREATE ROLE app_admin NOLOGIN;

-- 2. 授予权限
GRANT USAGE ON SCHEMA public TO app_readonly, app_readwrite, app_admin;

-- 只读权限
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;

-- 读写权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO app_readwrite;

-- 执行存储过程权限
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA public TO app_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON PROCEDURES TO app_readwrite;

-- 3. 创建用户并分配角色
CREATE USER app_user1 WITH LOGIN PASSWORD 'SecureRandomPassword123!';
GRANT app_readwrite TO app_user1;

-- 4. 撤销不必要的权限
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
```

### 1.2 行级安全(RLS)完整配置

```sql
-- ============================================
-- 租户隔离RLS配置
-- ============================================

-- 启用RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- 强制RLS（包括表所有者）
ALTER TABLE orders FORCE ROW LEVEL SECURITY;

-- 策略1: 用户只能看到自己的订单
CREATE POLICY user_order_isolation ON orders
    FOR ALL
    TO app_readwrite
    USING (user_id = current_setting('app.current_user_id')::UUID);

-- 策略2: 管理员可以看到所有
CREATE POLICY admin_all_access ON orders
    FOR ALL
    TO app_admin
    USING (true);

-- 策略3: 订单项级联策略
CREATE POLICY order_item_isolation ON order_items
    FOR ALL
    TO app_readwrite
    USING (order_id IN (
        SELECT id FROM orders
        WHERE user_id = current_setting('app.current_user_id')::UUID
    ));

-- 策略4: 产品只读策略
CREATE POLICY product_readonly ON products
    FOR SELECT
    TO app_readwrite
    USING (true);

-- 设置当前用户ID的函数
CREATE OR REPLACE FUNCTION fn_set_user_context(p_user_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    PERFORM set_config('app.current_user_id', p_user_id::TEXT, false);
    PERFORM set_config('app.current_user', current_user, false);
    PERFORM set_config('app.session_start', NOW()::TEXT, false);
END;
$$;
```

---

## 2. 审计日志配置

### 2.1 详细审计触发器

```sql
-- ============================================
-- 审计日志表
-- ============================================

CREATE TABLE security_audit_log (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,  -- SELECT, INSERT, UPDATE, DELETE, LOGIN, FAILED_LOGIN
    table_name VARCHAR(100),
    record_id TEXT,
    user_id UUID,
    username TEXT,
    ip_address INET,
    application_name TEXT,
    old_data JSONB,
    new_data JSONB,
    query TEXT,
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT
) PARTITION BY RANGE (event_time);

-- 创建分区
CREATE TABLE security_audit_log_2026_01 PARTITION OF security_audit_log
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- 索引
CREATE INDEX idx_audit_log_time ON security_audit_log(event_time DESC);
CREATE INDEX idx_audit_log_user ON security_audit_log(user_id);
CREATE INDEX idx_audit_log_table ON security_audit_log(table_name, event_time DESC);

-- ============================================
-- 通用审计触发器函数
-- ============================================

CREATE OR REPLACE FUNCTION fn_security_audit_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
    v_user_id UUID;
BEGIN
    -- 获取当前用户ID
    BEGIN
        v_user_id := current_setting('app.current_user_id')::UUID;
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;

    -- 根据操作类型记录数据
    IF TG_OP = 'DELETE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;
    ELSIF TG_OP = 'INSERT' THEN
        v_old_data := NULL;
        v_new_data := to_jsonb(NEW);
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
    END IF;

    -- 插入审计日志
    INSERT INTO security_audit_log (
        event_type,
        table_name,
        record_id,
        user_id,
        username,
        ip_address,
        application_name,
        old_data,
        new_data
    ) VALUES (
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(OLD.id, NEW.id)::TEXT,
        v_user_id,
        current_user,
        inet_client_addr(),
        current_setting('application_name', true),
        v_old_data,
        v_new_data
    );

    -- 敏感操作额外告警
    IF TG_TABLE_NAME IN ('users', 'payments', 'passwords') AND TG_OP IN ('UPDATE', 'DELETE') THEN
        PERFORM pg_notify('security_alert', jsonb_build_object(
            'severity', 'high',
            'event', TG_OP,
            'table', TG_TABLE_NAME,
            'user', current_user,
            'time', NOW()
        )::TEXT);
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;

-- 应用到关键表
CREATE TRIGGER trg_audit_orders
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION fn_security_audit_trigger();

CREATE TRIGGER trg_audit_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION fn_security_audit_trigger();

-- ============================================
-- 登录审计
-- ============================================

CREATE TABLE login_audit (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ DEFAULT NOW(),
    username TEXT,
    ip_address INET,
    success BOOLEAN,
    failure_reason TEXT,
    session_id TEXT
);

-- 登录失败处理函数
CREATE OR REPLACE FUNCTION fn_log_login_attempt(
    p_username TEXT,
    p_success BOOLEAN,
    p_failure_reason TEXT DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO login_audit (username, ip_address, success, failure_reason)
    VALUES (p_username, inet_client_addr(), p_success, p_failure_reason);

    -- 检测暴力破解
    IF NOT p_success THEN
        PERFORM fn_check_brute_force(p_username);
    END IF;
END;
$$;

-- 暴力破解检测
CREATE OR REPLACE FUNCTION fn_check_brute_force(p_username TEXT)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_failed_attempts INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_failed_attempts
    FROM login_audit
    WHERE username = p_username
      AND success = false
      AND event_time > NOW() - INTERVAL '15 minutes';

    IF v_failed_attempts >= 5 THEN
        -- 发送告警
        PERFORM pg_notify('security_alert', jsonb_build_object(
            'severity', 'critical',
            'event', 'brute_force_detected',
            'username', p_username,
            'failed_attempts', v_failed_attempts
        )::TEXT);

        -- 可以在这里实现自动封禁IP
        RAISE WARNING 'Possible brute force attack detected for user: %', p_username;
    END IF;
END;
$$;
```

---

## 3. 合规检查清单

### 3.1 自动合规检查脚本

```sql
-- ============================================
-- 合规检查函数
-- ============================================

CREATE OR REPLACE FUNCTION fn_security_compliance_check()
RETURNS TABLE (
    check_item TEXT,
    status TEXT,
    details TEXT,
    severity TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 检查1: 默认密码
    RETURN QUERY
    SELECT
        'Default/Weak Passwords'::TEXT,
        CASE WHEN COUNT(*) > 0 THEN 'FAIL' ELSE 'PASS' END,
        'Users with weak passwords: ' || COUNT(*)::TEXT,
        'HIGH'::TEXT
    FROM pg_user
    WHERE passwd IS NULL OR passwd = 'md5d41d8cd98f00b204e9800998ecf8427e';

    -- 检查2: 超级用户权限
    RETURN QUERY
    SELECT
        'Superuser Privileges'::TEXT,
        CASE WHEN COUNT(*) > 1 THEN 'WARNING' ELSE 'PASS' END,
        'Superuser count: ' || COUNT(*)::TEXT || ' (should be 1)',
        'MEDIUM'::TEXT
    FROM pg_user WHERE usesuper = true;

    -- 检查3: 未加密连接
    RETURN QUERY
    SELECT
        'Unencrypted Connections'::TEXT,
        CASE WHEN COUNT(*) > 0 THEN 'FAIL' ELSE 'PASS' END,
        'Unencrypted connections: ' || COUNT(*)::TEXT,
        'HIGH'::TEXT
    FROM pg_stat_ssl WHERE ssl = false;

    -- 检查4: 未使用RLS的敏感表
    RETURN QUERY
    SELECT
        'RLS Not Enabled'::TEXT,
        CASE WHEN COUNT(*) > 0 THEN 'WARNING' ELSE 'PASS' END,
        'Tables without RLS: ' || string_agg(relname, ', '),
        'MEDIUM'::TEXT
    FROM pg_class
    WHERE relname IN ('orders', 'users', 'payments')
      AND NOT relrowsecurity;

    -- 检查5: 审计日志配置
    RETURN QUERY
    SELECT
        'Audit Logging'::TEXT,
        CASE WHEN EXISTS (SELECT 1 FROM pg_trigger WHERE tgname LIKE 'trg_audit_%')
            THEN 'PASS' ELSE 'FAIL' END,
        'Audit triggers configured',
        'HIGH'::TEXT;

    -- 检查6: 密码策略
    RETURN QUERY
    SELECT
        'Password Policy'::TEXT,
        CASE
            WHEN current_setting('password_encryption', true) = 'scram-sha-256'
            THEN 'PASS' ELSE 'WARNING'
        END,
        'Password encryption: ' || current_setting('password_encryption', true),
        'MEDIUM'::TEXT;

    -- 检查7: 日志配置
    RETURN QUERY
    SELECT
        'Logging Configuration'::TEXT,
        CASE
            WHEN current_setting('log_connections', true) = 'on'
             AND current_setting('log_disconnections', true) = 'on'
            THEN 'PASS' ELSE 'WARNING'
        END,
        'Connection logging enabled',
        'MEDIUM'::TEXT;

    RETURN;
END;
$$;

-- 执行合规检查
SELECT * FROM fn_security_compliance_check();
```

---

## 4. 安全扫描脚本

```bash
#!/bin/bash
# ============================================
# security-scan.sh - 安全扫描脚本
# ============================================

echo "=========================================="
echo "PostgreSQL DCA 安全扫描"
echo "=========================================="
echo ""

# 检查PostgreSQL版本
echo "1. 检查PostgreSQL版本..."
psql -c "SELECT version();" | grep -E "PostgreSQL\s+1[4-9]|PostgreSQL\s+[2-9][0-9]"
if [ $? -ne 0 ]; then
    echo "   WARNING: PostgreSQL版本较旧，建议升级"
else
    echo "   PASS: PostgreSQL版本符合要求"
fi

# 检查SSL配置
echo ""
echo "2. 检查SSL配置..."
SSL_ENABLED=$(psql -t -c "SHOW ssl;" | xargs)
if [ "$SSL_ENABLED" = "on" ]; then
    echo "   PASS: SSL已启用"
else
    echo "   FAIL: SSL未启用"
fi

# 检查密码加密
echo ""
echo "3. 检查密码加密..."
PASSWORD_ENC=$(psql -t -c "SHOW password_encryption;" | xargs)
if [ "$PASSWORD_ENC" = "scram-sha-256" ]; then
    echo "   PASS: 使用SCRAM-SHA-256加密"
else
    echo "   WARNING: 密码加密方式较弱: $PASSWORD_ENC"
fi

# 检查弱密码用户
echo ""
echo "4. 检查弱密码用户..."
psql -c "SELECT usename FROM pg_user WHERE passwd IS NULL;"

# 检查超级用户
echo ""
echo "5. 检查超级用户..."
SUPERUSERS=$(psql -t -c "SELECT count(*) FROM pg_user WHERE usesuper = true;" | xargs)
echo "   超级用户数量: $SUPERUSERS"
if [ "$SUPERUSERS" -gt 1 ]; then
    echo "   WARNING: 超级用户过多"
fi

# 检查未加密的连接
echo ""
echo "6. 检查未加密连接..."
UNENCRYPTED=$(psql -t -c "SELECT count(*) FROM pg_stat_ssl WHERE ssl = false;" | xargs)
if [ "$UNENCRYPTED" -gt 0 ]; then
    echo "   WARNING: 存在 $UNENCRYPTED 个未加密连接"
else
    echo "   PASS: 所有连接都已加密"
fi

# 检查审计日志
echo ""
echo "7. 检查审计日志配置..."
AUDIT_TRIGGERS=$(psql -t -c "SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'trg_audit_%';" | xargs)
if [ "$AUDIT_TRIGGERS" -gt 0 ]; then
    echo "   PASS: 发现 $AUDIT_TRIGGERS 个审计触发器"
else
    echo "   WARNING: 未配置审计触发器"
fi

# 检查RLS
echo ""
echo "8. 检查行级安全(RLS)..."
psql -c "SELECT relname, relrowsecurity FROM pg_class WHERE relname IN ('orders', 'users') AND relkind = 'r';"

echo ""
echo "=========================================="
echo "安全扫描完成"
echo "=========================================="
```

---

**文档版本**: v1.0
**更新日期**: 2026-03-04
