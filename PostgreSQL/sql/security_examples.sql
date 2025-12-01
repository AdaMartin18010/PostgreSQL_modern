-- 1.1.17 安全与合规 - 可执行示例汇总
-- 说明：本脚本聚合了审计、RLS、加密、合规（GDPR/SOX/PCI）等示例。
-- 使用前提：
--   - 具备超级用户或足够权限
--   - 已安装扩展：pgaudit、pgcrypto、pg_stat_statements（部分查询）
--   - 在非生产环境验证

-- =====================
-- 0. 环境准备
-- =====================
-- 扩展
CREATE EXTENSION IF NOT EXISTS pgaudit;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- 可选：统计扩展（用于示例查询）
-- CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 应用密钥（仅示例，生产环境请改用密钥管理/KMS）
-- 注意：需在postgresql.conf或会话级设置
-- SELECT set_config('app.encryption_key', 'ReplaceWithStrongKey', false);

-- =====================
-- 1. 审计与监控（pgaudit + 触发审计）
-- =====================
-- 基本审计策略
ALTER SYSTEM SET pgaudit.log = 'read, write, ddl, role, function';
ALTER SYSTEM SET pgaudit.log_parameter = on;
-- 需要重启或pg_reload_conf()视参数而定
-- SELECT pg_reload_conf();

-- 应用级审计表示例
CREATE SCHEMA IF NOT EXISTS sec_demo;
SET search_path TO sec_demo, public;

CREATE TABLE IF NOT EXISTS audit_log (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  user_name TEXT,
  database_name TEXT,
  client_addr INET,
  session_id TEXT,
  statement TEXT,
  parameters JSONB
);

CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_log (
    user_name, database_name, client_addr, session_id, statement, parameters
  ) VALUES (
    current_user,
    current_database(),
    inet_client_addr(),
    current_setting('application_name', true),
    current_query(),
    '{}'::jsonb
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 受审计对象（示例表）
CREATE TABLE IF NOT EXISTS sensitive_data (
  id BIGSERIAL PRIMARY KEY,
  owner_name TEXT,
  payload TEXT
);

DROP TRIGGER IF EXISTS tr_audit_sensitive ON sensitive_data;
CREATE TRIGGER tr_audit_sensitive
AFTER INSERT OR UPDATE OR DELETE ON sensitive_data
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- =====================
-- 2. 行级安全（RLS）
-- =====================
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- 简单基于当前用户的访问隔离策略
DROP POLICY IF EXISTS p_owner_only ON sensitive_data;
CREATE POLICY p_owner_only ON sensitive_data
  FOR ALL USING (owner_name = current_user);

-- =====================
-- 3. 存储加密（pgcrypto 对称加密示例）
-- =====================
CREATE TABLE IF NOT EXISTS encrypted_users (
  id BIGSERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  encrypted_email BYTEA NOT NULL,
  encrypted_phone BYTEA NOT NULL,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT)
RETURNS BYTEA AS $$
DECLARE
  k TEXT := current_setting('app.encryption_key', true);
BEGIN
  IF k IS NULL THEN
    RAISE EXCEPTION 'app.encryption_key 未设置';
  END IF;
  RETURN pgp_sym_encrypt(data, k);
END;$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrypt_sensitive_data(encrypted_data BYTEA)
RETURNS TEXT AS $$
DECLARE
  k TEXT := current_setting('app.encryption_key', true);
BEGIN
  IF k IS NULL THEN
    RAISE EXCEPTION 'app.encryption_key 未设置';
  END IF;
  RETURN pgp_sym_decrypt(encrypted_data, k);
END;$$ LANGUAGE plpgsql;

-- 示例插入
-- INSERT INTO encrypted_users(username, encrypted_email, encrypted_phone)
-- VALUES (
--   'alice',
--   encrypt_sensitive_data('alice@example.com'),
--   encrypt_sensitive_data('+1-555-0100')
-- );

-- =====================
-- 4. GDPR 合规模块（最小化/删除权/可携带性）
-- =====================
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  name TEXT
);

CREATE TABLE IF NOT EXISTS user_data (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  key TEXT,
  value TEXT,
  deleted_at TIMESTAMPTZ,
  deleted_by TEXT
);

CREATE TABLE IF NOT EXISTS authorized_users (
  user_id TEXT,
  department TEXT,
  purpose TEXT
);

DROP POLICY IF EXISTS gdpr_minimization ON user_data;
CREATE POLICY gdpr_minimization ON user_data
  FOR SELECT USING (
    current_user IN (
      SELECT user_id FROM authorized_users WHERE purpose = 'legitimate_interest'
    )
  );

CREATE TABLE IF NOT EXISTS data_deletion_log (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT,
  deleted_at TIMESTAMPTZ,
  deleted_by TEXT,
  reason TEXT
);

CREATE OR REPLACE FUNCTION delete_user_data(p_user_id BIGINT)
RETURNS VOID AS $$
BEGIN
  UPDATE user_data
     SET deleted_at = CURRENT_TIMESTAMP,
         deleted_by = current_user
   WHERE user_id = p_user_id;

  INSERT INTO data_deletion_log(user_id, deleted_at, deleted_by, reason)
  VALUES (p_user_id, CURRENT_TIMESTAMP, current_user, 'GDPR request');
END;$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION export_user_data(p_user_id BIGINT)
RETURNS JSON AS $$
DECLARE result JSON; BEGIN
  SELECT json_build_object(
    'user_info', (SELECT row_to_json(u) FROM users u WHERE u.id = p_user_id),
    'user_data', (
      SELECT json_agg(row_to_json(d)) FROM user_data d
      WHERE d.user_id = p_user_id AND d.deleted_at IS NULL
    )
  ) INTO result;
  RETURN result;
END;$$ LANGUAGE plpgsql;

-- =====================
-- 5. SOX 审计模块（CRUD 审计触发器）
-- =====================
CREATE TABLE IF NOT EXISTS sox_audit_log (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  user_name TEXT NOT NULL,
  action_type TEXT NOT NULL,
  table_name TEXT,
  record_id BIGINT,
  old_values JSONB,
  new_values JSONB,
  ip_address INET,
  session_id TEXT
);

CREATE OR REPLACE FUNCTION sox_audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO sox_audit_log(user_name, action_type, table_name, record_id,
      new_values, ip_address, session_id)
    VALUES (current_user, 'INSERT', TG_TABLE_NAME, NEW.id,
      row_to_json(NEW), inet_client_addr(), current_setting('application_name', true));
    RETURN NEW;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO sox_audit_log(user_name, action_type, table_name, record_id,
      old_values, new_values, ip_address, session_id)
    VALUES (current_user, 'UPDATE', TG_TABLE_NAME, NEW.id,
      row_to_json(OLD), row_to_json(NEW), inet_client_addr(), current_setting('application_name', true));
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO sox_audit_log(user_name, action_type, table_name, record_id,
      old_values, ip_address, session_id)
    VALUES (current_user, 'DELETE', TG_TABLE_NAME, OLD.id,
      row_to_json(OLD), inet_client_addr(), current_setting('application_name', true));
    RETURN OLD;
  END IF;
  RETURN NULL;
END;$$ LANGUAGE plpgsql;

-- 需要针对业务表创建触发器，例如：
-- DROP TRIGGER IF EXISTS tr_sox_sensitive ON sensitive_data;
-- CREATE TRIGGER tr_sox_sensitive
-- AFTER INSERT OR UPDATE OR DELETE ON sensitive_data
-- FOR EACH ROW EXECUTE FUNCTION sox_audit_trigger();

-- =====================
-- 6. PCI DSS 支付数据加密流程
-- =====================
CREATE TABLE IF NOT EXISTS encrypted_payment_cards (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  encrypted_card_number BYTEA NOT NULL,
  encrypted_cvv BYTEA NOT NULL,
  card_type TEXT,
  expiry_month INT,
  expiry_year INT,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION encrypt_payment_data(card_number TEXT, cvv TEXT)
RETURNS TABLE(encrypted_card BYTEA, encrypted_cvv BYTEA) AS $$
DECLARE k TEXT := current_setting('app.encryption_key', true); BEGIN
  IF k IS NULL THEN
    RAISE EXCEPTION 'app.encryption_key 未设置';
  END IF;
  RETURN QUERY SELECT pgp_sym_encrypt(card_number, k), pgp_sym_encrypt(cvv, k);
END;$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION insert_payment_card(
  p_user_id BIGINT, p_card_number TEXT, p_cvv TEXT,
  p_card_type TEXT, p_expiry_month INT, p_expiry_year INT
) RETURNS BIGINT AS $$
DECLARE card_id BIGINT; enc RECORD; BEGIN
  SELECT * INTO enc FROM encrypt_payment_data(p_card_number, p_cvv);
  INSERT INTO encrypted_payment_cards(user_id, encrypted_card_number, encrypted_cvv,
    card_type, expiry_month, expiry_year)
  VALUES (p_user_id, enc.encrypted_card, enc.encrypted_cvv,
    p_card_type, p_expiry_month, p_expiry_year)
  RETURNING id INTO card_id;
  RETURN card_id;
END;$$ LANGUAGE plpgsql;

-- =====================
-- 7. 安全指标查询（演示）
-- =====================
-- 失败登录/长时间空闲事务（演示用，需按环境调整）
-- SELECT client_addr, count(*) AS attempts
-- FROM pg_stat_activity
-- WHERE state = 'idle in transaction' AND query_start < NOW() - INTERVAL '5 minutes'
-- GROUP BY client_addr HAVING count(*) > 10;

-- 可疑语句（需启用 pg_stat_statements 并加载共享库）
-- SELECT query, calls, mean_time
-- FROM pg_stat_statements
-- WHERE query ILIKE '%DROP%' OR query ILIKE '%DELETE%' OR query ILIKE '%TRUNCATE%'
-- ORDER BY calls DESC LIMIT 10;

-- 权限巡检
-- SELECT grantee, table_name, privilege_type
-- FROM information_schema.role_table_grants
-- WHERE grantee NOT IN ('postgres')
-- ORDER BY grantee, table_name;

-- 结束
-- 提示：执行完毕后，可根据需要撤销演示对象或在独立schema中清理。

