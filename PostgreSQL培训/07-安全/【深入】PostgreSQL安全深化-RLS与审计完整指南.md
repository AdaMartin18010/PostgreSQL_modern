# 【深入】PostgreSQL安全深化 - RLS与审计完整指南

> **创建时间**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级
> **预计学习时间**: 1-2周

---

## 📑 目录

- [1. 行级安全（RLS）完整指南](#1-行级安全rls完整指南)
- [2. 审计日志系统](#2-审计日志系统)
- [3. 数据脱敏](#3-数据脱敏)
- [4. 安全加固实战](#4-安全加固实战)
- [5. 渗透测试](#5-渗透测试)
- [6. 合规性检查](#6-合规性检查)
- [7. 完整实战案例](#7-完整实战案例)

---

## 1. 行级安全（RLS）完整指南

### 1.1 RLS基础概念

**什么是RLS**：

行级安全（Row Level Security）允许在表级别定义安全策略，控制用户只能看到和修改特定的行。

**适用场景**：
- 多租户SaaS应用
- 基于角色的数据访问控制
- 数据隔离和权限管理
- 符合GDPR等法规要求

### 1.2 RLS快速开始（15分钟）

```sql
-- 1. 创建示例表
CREATE TABLE documents (
    id serial PRIMARY KEY,
    title text NOT NULL,
    content text,
    owner_id int NOT NULL,
    department text,
    classification text CHECK (classification IN ('public', 'internal', 'confidential', 'secret')),
    created_at timestamptz DEFAULT now()
);

-- 2. 插入测试数据
INSERT INTO documents (title, content, owner_id, department, classification) VALUES
    ('Public Doc', 'Everyone can see', 1, 'marketing', 'public'),
    ('Team Doc', 'Team only', 2, 'engineering', 'internal'),
    ('Manager Doc', 'Managers only', 3, 'hr', 'confidential'),
    ('CEO Doc', 'CEO only', 4, 'executive', 'secret');

-- 3. 启用RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 4. 创建策略：用户只能看到自己的文档
CREATE POLICY documents_owner_policy
    ON documents
    FOR SELECT
    USING (owner_id = current_setting('app.current_user_id')::int);

-- 5. 测试
-- 设置当前用户ID
SET app.current_user_id = '1';

-- 查询（只能看到owner_id=1的文档）
SELECT * FROM documents;
-- 结果：只返回 'Public Doc'

-- 切换用户
SET app.current_user_id = '2';
SELECT * FROM documents;
-- 结果：只返回 'Team Doc'
```

### 1.3 RLS策略类型

#### 1.3.1 SELECT策略（查询控制）

```sql
-- 策略1：用户只能看到自己的数据
CREATE POLICY user_own_data
    ON documents
    FOR SELECT
    USING (owner_id = current_user_id());

-- 策略2：用户可以看到自己部门的数据
CREATE POLICY department_data
    ON documents
    FOR SELECT
    USING (department = current_user_department());

-- 策略3：基于角色的访问
CREATE POLICY role_based_access
    ON documents
    FOR SELECT
    USING (
        CASE
            WHEN current_user_role() = 'admin' THEN true
            WHEN current_user_role() = 'manager' THEN classification IN ('public', 'internal', 'confidential')
            WHEN current_user_role() = 'employee' THEN classification IN ('public', 'internal')
            ELSE classification = 'public'
        END
    );

-- 策略4：时间范围访问
CREATE POLICY time_based_access
    ON documents
    FOR SELECT
    USING (
        created_at >= now() - interval '1 year'
        OR owner_id = current_user_id()
    );

-- 策略5：地理位置限制（结合PostGIS）
CREATE POLICY geo_based_access
    ON locations
    FOR SELECT
    USING (
        ST_DWithin(
            location::geometry,
            current_user_location()::geometry,
            1000  -- 1km范围内
        )
    );
```

#### 1.3.2 INSERT策略（插入控制）

```sql
-- 策略：用户只能以自己的名义创建文档
CREATE POLICY documents_insert_policy
    ON documents
    FOR INSERT
    WITH CHECK (owner_id = current_user_id());

-- 策略：限制classification
CREATE POLICY classification_insert_policy
    ON documents
    FOR INSERT
    WITH CHECK (
        classification IN ('public', 'internal')
        OR current_user_role() = 'manager'
    );
```

#### 1.3.3 UPDATE策略（更新控制）

```sql
-- 策略：只能更新自己的文档
CREATE POLICY documents_update_policy
    ON documents
    FOR UPDATE
    USING (owner_id = current_user_id())
    WITH CHECK (owner_id = current_user_id());

-- 策略：不能降低classification
CREATE POLICY classification_update_policy
    ON documents
    FOR UPDATE
    USING (true)
    WITH CHECK (
        classification >= OLD.classification
        OR current_user_role() = 'admin'
    );
```

#### 1.3.4 DELETE策略（删除控制）

```sql
-- 策略：只能删除自己的文档
CREATE POLICY documents_delete_policy
    ON documents
    FOR DELETE
    USING (
        owner_id = current_user_id()
        AND classification != 'secret'
    );
```

### 1.4 RLS性能优化

#### 问题：RLS可能导致性能下降

```sql
-- 性能问题示例
CREATE POLICY slow_policy
    ON large_table
    FOR SELECT
    USING (
        user_id IN (SELECT user_id FROM user_permissions WHERE ...)  -- 子查询可能很慢
    );
```

#### 优化方案

**方案1：使用JOIN代替子查询**

```sql
CREATE POLICY optimized_policy
    ON large_table
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM user_permissions up
            WHERE up.user_id = large_table.user_id
            AND up.resource_id = large_table.id
        )
    );

-- 确保索引
CREATE INDEX idx_user_permissions ON user_permissions(user_id, resource_id);
```

**方案2：使用物化视图缓存权限**

```sql
-- 创建权限缓存
CREATE MATERIALIZED VIEW user_accessible_documents AS
SELECT user_id, document_id
FROM user_permissions
WHERE is_active = true;

CREATE INDEX ON user_accessible_documents(user_id, document_id);

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY user_accessible_documents;

-- 使用缓存的策略
CREATE POLICY cached_policy
    ON documents
    FOR SELECT
    USING (
        id IN (
            SELECT document_id
            FROM user_accessible_documents
            WHERE user_id = current_user_id()
        )
    );
```

**方案3：使用Security Barrier Views**

```sql
CREATE VIEW user_documents
WITH (security_barrier = true) AS
SELECT *
FROM documents
WHERE owner_id = current_user_id()
   OR department = current_user_department();

-- 用户查询视图而不是表
SELECT * FROM user_documents;
```

### 1.5 多租户RLS完整方案

```sql
-- 租户表
CREATE TABLE tenants (
    tenant_id serial PRIMARY KEY,
    tenant_name text UNIQUE NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- 用户表
CREATE TABLE users (
    user_id serial PRIMARY KEY,
    username text UNIQUE NOT NULL,
    tenant_id int REFERENCES tenants(tenant_id),
    role text CHECK (role IN ('admin', 'user', 'readonly'))
);

-- 业务表（多租户）
CREATE TABLE orders (
    order_id serial PRIMARY KEY,
    tenant_id int NOT NULL REFERENCES tenants(tenant_id),
    user_id int NOT NULL REFERENCES users(user_id),
    amount numeric(10,2),
    status text,
    created_at timestamptz DEFAULT now()
);

-- 启用RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 策略1：租户隔离（最重要）
CREATE POLICY tenant_isolation
    ON orders
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::int);

-- 策略2：用户权限
CREATE POLICY user_access
    ON orders
    FOR SELECT
    USING (
        -- 管理员可以看所有
        current_user_role() = 'admin'
        -- 普通用户只能看自己的
        OR user_id = current_user_id()
    );

-- 策略3：只读用户不能修改
CREATE POLICY readonly_restriction
    ON orders
    FOR UPDATE
    USING (current_user_role() != 'readonly');

CREATE POLICY readonly_delete_restriction
    ON orders
    FOR DELETE
    USING (current_user_role() != 'readonly');

-- 辅助函数
CREATE FUNCTION current_user_id() RETURNS int AS $$
    SELECT current_setting('app.user_id')::int;
$$ LANGUAGE SQL STABLE;

CREATE FUNCTION current_user_role() RETURNS text AS $$
    SELECT current_setting('app.user_role')::text;
$$ LANGUAGE SQL STABLE;

-- 应用层设置（每个请求开始时）
DO $$
BEGIN
    PERFORM set_config('app.tenant_id', '123', false);
    PERFORM set_config('app.user_id', '456', false);
    PERFORM set_config('app.user_role', 'user', false);
END $$;
```

---

## 2. 审计日志系统

### 2.1 使用pgAudit扩展

**安装**：

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-17-pgaudit

# 配置postgresql.conf
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'all'  # 或者 'read, write, ddl'
pgaudit.log_catalog = off
pgaudit.log_level = 'log'
pgaudit.log_parameter = on
pgaudit.log_relation = on
pgaudit.log_statement_once = off
```

**使用**：

```sql
-- 创建扩展
CREATE EXTENSION pgaudit;

-- 配置审计（会话级别）
SET pgaudit.log = 'read, write';
SET pgaudit.log_relation = on;

-- 配置审计（数据库级别）
ALTER DATABASE mydb SET pgaudit.log = 'ddl, role';

-- 配置审计（用户级别）
ALTER ROLE dba SET pgaudit.log = 'all';

-- 配置审计（表级别）
CREATE TABLE sensitive_data (
    id serial PRIMARY KEY,
    ssn text,
    credit_card text
);

-- 为特定表启用审计
ALTER TABLE sensitive_data SET (pgaudit.log = 'read, write');
```

**审计日志示例**：

```
2025-01-01 10:00:00 UTC [12345]: [1-1] user=alice,db=mydb LOG:  AUDIT: SESSION,1,1,READ,SELECT,,,
    "SELECT * FROM sensitive_data WHERE id = 1",<not logged>
2025-01-01 10:00:05 UTC [12346]: [1-1] user=bob,db=mydb LOG:  AUDIT: SESSION,2,1,WRITE,UPDATE,,,
    "UPDATE sensitive_data SET ssn = '***' WHERE id = 2",<not logged>
```

### 2.2 自定义审计触发器

**完整审计表设计**：

```sql
-- 审计日志表
CREATE TABLE audit_log (
    audit_id bigserial PRIMARY KEY,
    table_name text NOT NULL,
    operation text NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE', 'TRUNCATE')),
    old_data jsonb,
    new_data jsonb,
    changed_fields text[],
    user_name text NOT NULL,
    user_ip inet,
    application_name text,
    transaction_id bigint,
    occurred_at timestamptz NOT NULL DEFAULT now(),
    query_text text
);

-- 索引
CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_user ON audit_log(user_name);
CREATE INDEX idx_audit_log_time ON audit_log(occurred_at);
CREATE INDEX idx_audit_log_operation ON audit_log(operation);
CREATE INDEX idx_audit_log_data ON audit_log USING gin(old_data, new_data);

-- 分区（按月）
CREATE TABLE audit_log_2025_01 PARTITION OF audit_log
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- 自动创建分区函数
CREATE OR REPLACE FUNCTION create_audit_partition()
RETURNS void AS $$
DECLARE
    partition_date date;
    partition_name text;
    start_date date;
    end_date date;
BEGIN
    partition_date := date_trunc('month', now() + interval '1 month');
    partition_name := 'audit_log_' || to_char(partition_date, 'YYYY_MM');
    start_date := partition_date;
    end_date := partition_date + interval '1 month';

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF audit_log FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;

-- 定期任务
SELECT cron.schedule('create_audit_partition', '0 0 25 * *', 'SELECT create_audit_partition()');
```

**通用审计触发器函数**：

```sql
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS trigger AS $$
DECLARE
    old_data jsonb;
    new_data jsonb;
    changed_fields text[];
    query_text text;
BEGIN
    -- 获取查询文本
    query_text := current_query();

    -- 处理不同操作
    IF TG_OP = 'INSERT' THEN
        new_data := to_jsonb(NEW);
        old_data := NULL;
        changed_fields := NULL;

    ELSIF TG_OP = 'UPDATE' THEN
        old_data := to_jsonb(OLD);
        new_data := to_jsonb(NEW);

        -- 找出变更的字段
        SELECT array_agg(key)
        INTO changed_fields
        FROM (
            SELECT key
            FROM jsonb_each(new_data)
            WHERE new_data->key IS DISTINCT FROM old_data->key
        ) t;

    ELSIF TG_OP = 'DELETE' THEN
        old_data := to_jsonb(OLD);
        new_data := NULL;
        changed_fields := NULL;
    END IF;

    -- 插入审计日志
    INSERT INTO audit_log (
        table_name,
        operation,
        old_data,
        new_data,
        changed_fields,
        user_name,
        user_ip,
        application_name,
        transaction_id,
        query_text
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        old_data,
        new_data,
        changed_fields,
        current_user,
        inet_client_addr(),
        current_setting('application_name', true),
        txid_current(),
        query_text
    );

    -- 返回适当的值
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**应用到表**：

```sql
-- 为敏感表创建审计触发器
CREATE TRIGGER audit_sensitive_data
    AFTER INSERT OR UPDATE OR DELETE
    ON sensitive_data
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- 批量应用到所有表
DO $$
DECLARE
    table_record record;
BEGIN
    FOR table_record IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename != 'audit_log'
    LOOP
        EXECUTE format(
            'CREATE TRIGGER audit_%I AFTER INSERT OR UPDATE OR DELETE ON %I.%I FOR EACH ROW EXECUTE FUNCTION audit_trigger_function()',
            table_record.tablename,
            table_record.schemaname,
            table_record.tablename
        );
    END LOOP;
END $$;
```

### 2.3 审计日志查询和分析

```sql
-- 查询1：查看某个用户的所有操作
SELECT
    occurred_at,
    table_name,
    operation,
    changed_fields,
    query_text
FROM audit_log
WHERE user_name = 'alice'
ORDER BY occurred_at DESC
LIMIT 100;

-- 查询2：查看敏感数据访问
SELECT
    user_name,
    user_ip,
    COUNT(*) AS access_count,
    array_agg(DISTINCT operation) AS operations
FROM audit_log
WHERE table_name = 'sensitive_data'
  AND occurred_at >= now() - interval '24 hours'
GROUP BY user_name, user_ip
ORDER BY access_count DESC;

-- 查询3：查找异常操作（大量删除）
SELECT
    user_name,
    table_name,
    COUNT(*) AS delete_count,
    min(occurred_at) AS first_delete,
    max(occurred_at) AS last_delete
FROM audit_log
WHERE operation = 'DELETE'
  AND occurred_at >= now() - interval '1 hour'
GROUP BY user_name, table_name
HAVING COUNT(*) > 100  -- 1小时内删除超过100行
ORDER BY delete_count DESC;

-- 查询4：数据变更历史
SELECT
    audit_id,
    operation,
    occurred_at,
    user_name,
    old_data->>'title' AS old_title,
    new_data->>'title' AS new_title,
    changed_fields
FROM audit_log
WHERE table_name = 'documents'
  AND (old_data->>'id' = '123' OR new_data->>'id' = '123')
ORDER BY occurred_at;

-- 查询5：恢复删除的数据
SELECT
    old_data->>'id' AS id,
    old_data->>'title' AS title,
    old_data->>'content' AS content
FROM audit_log
WHERE table_name = 'documents'
  AND operation = 'DELETE'
  AND old_data->>'id' = '123';

-- 恢复数据
INSERT INTO documents (id, title, content, ...)
SELECT
    (old_data->>'id')::int,
    old_data->>'title',
    old_data->>'content',
    ...
FROM audit_log
WHERE table_name = 'documents'
  AND operation = 'DELETE'
  AND old_data->>'id' = '123'
ORDER BY occurred_at DESC
LIMIT 1;
```

### 2.4 不可篡改审计日志

```sql
-- 使用Ledger表（PostgreSQL 18+概念，当前可用hash链实现）
CREATE TABLE immutable_audit_log (
    audit_id bigserial PRIMARY KEY,
    table_name text NOT NULL,
    operation text NOT NULL,
    data_hash text NOT NULL,  -- 数据哈希
    previous_hash text,        -- 前一条记录的哈希
    chain_hash text NOT NULL,  -- 链式哈希
    occurred_at timestamptz NOT NULL DEFAULT now()
);

-- 审计插入函数（带哈希链）
CREATE OR REPLACE FUNCTION insert_immutable_audit()
RETURNS trigger AS $$
DECLARE
    data_text text;
    data_hash_val text;
    prev_hash_val text;
    chain_hash_val text;
BEGIN
    -- 计算数据哈希
    data_text := NEW.table_name || NEW.operation || coalesce(NEW.old_data::text, '') || coalesce(NEW.new_data::text, '');
    data_hash_val := encode(digest(data_text, 'sha256'), 'hex');

    -- 获取前一条记录的chain_hash
    SELECT chain_hash INTO prev_hash_val
    FROM immutable_audit_log
    ORDER BY audit_id DESC
    LIMIT 1;

    -- 计算链式哈希
    chain_hash_val := encode(
        digest(coalesce(prev_hash_val, '') || data_hash_val, 'sha256'),
        'hex'
    );

    -- 更新NEW记录
    NEW.data_hash := data_hash_val;
    NEW.previous_hash := prev_hash_val;
    NEW.chain_hash := chain_hash_val;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER immutable_audit_trigger
    BEFORE INSERT ON immutable_audit_log
    FOR EACH ROW
    EXECUTE FUNCTION insert_immutable_audit();

-- 验证审计链完整性
CREATE OR REPLACE FUNCTION verify_audit_chain()
RETURNS TABLE(audit_id bigint, is_valid boolean, error_message text) AS $$
DECLARE
    rec record;
    expected_chain_hash text;
BEGIN
    FOR rec IN
        SELECT a1.audit_id, a1.data_hash, a1.previous_hash, a1.chain_hash,
               lag(a1.chain_hash) OVER (ORDER BY a1.audit_id) AS prev_chain_hash
        FROM immutable_audit_log a1
        ORDER BY a1.audit_id
    LOOP
        -- 验证previous_hash
        IF rec.previous_hash IS DISTINCT FROM rec.prev_chain_hash THEN
            RETURN QUERY SELECT rec.audit_id, false, 'Previous hash mismatch';
            CONTINUE;
        END IF;

        -- 验证chain_hash
        expected_chain_hash := encode(
            digest(coalesce(rec.previous_hash, '') || rec.data_hash, 'sha256'),
            'hex'
        );

        IF rec.chain_hash != expected_chain_hash THEN
            RETURN QUERY SELECT rec.audit_id, false, 'Chain hash mismatch';
            CONTINUE;
        END IF;

        RETURN QUERY SELECT rec.audit_id, true, NULL::text;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 定期验证
SELECT * FROM verify_audit_chain() WHERE NOT is_valid;
```

---

## 3. 数据脱敏

### 3.1 静态脱敏（数据导出时）

```sql
-- 创建脱敏函数
CREATE OR REPLACE FUNCTION mask_phone(phone text)
RETURNS text AS $$
    SELECT regexp_replace(phone, '(\d{3})\d{4}(\d{4})', '\1****\2');
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE FUNCTION mask_email(email text)
RETURNS text AS $$
    SELECT regexp_replace(email, '(.{2})(.*)(@.*)', '\1***\3');
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE FUNCTION mask_id_card(id_card text)
RETURNS text AS $$
    SELECT regexp_replace(id_card, '(\d{6})\d{8}(\d{4})', '\1********\2');
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE FUNCTION mask_credit_card(cc text)
RETURNS text AS $$
    SELECT regexp_replace(cc, '(\d{4})\d{8}(\d{4})', '\1********\2');
$$ LANGUAGE SQL IMMUTABLE;

-- 脱敏视图
CREATE VIEW users_masked AS
SELECT
    id,
    username,
    mask_email(email) AS email,
    mask_phone(phone) AS phone,
    mask_id_card(id_card) AS id_card,
    department,
    created_at
FROM users;

-- 授权给开发/测试环境
GRANT SELECT ON users_masked TO dev_role;
REVOKE SELECT ON users FROM dev_role;
```

### 3.2 动态脱敏（anon扩展）

**安装postgresql_anonymizer**：

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-17-anonymizer
```

**使用**：

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS anon CASCADE;

-- 初始化
SELECT anon.init();

-- 定义脱敏规则
SECURITY LABEL FOR anon ON COLUMN users.email
    IS 'MASKED WITH FUNCTION anon.fake_email()';

SECURITY LABEL FOR anon ON COLUMN users.phone
    IS 'MASKED WITH FUNCTION anon.partial(phone, 2, $$****$$, 2)';

SECURITY LABEL FOR anon ON COLUMN users.ssn
    IS 'MASKED WITH VALUE NULL';

SECURITY LABEL FOR anon ON COLUMN users.salary
    IS 'MASKED WITH FUNCTION anon.random_int_between(30000, 150000)';

-- 创建脱敏角色
CREATE ROLE masked_user;
SECURITY LABEL FOR anon ON ROLE masked_user IS 'MASKED';

-- 测试
SET ROLE masked_user;
SELECT email, phone, ssn, salary FROM users;
-- 结果：显示脱敏后的数据

RESET ROLE;
SELECT email, phone, ssn, salary FROM users;
-- 结果：显示真实数据
```

**批量脱敏导出**：

```sql
-- 匿名化整个数据库
SELECT anon.anonymize_database();

-- 匿名化特定表
SELECT anon.anonymize_table('users');

-- 导出到CSV
\copy (SELECT * FROM anon.anonymize_table_json('users')) TO 'users_masked.csv' CSV HEADER;
```

### 3.3 差分隐私

```sql
-- 添加噪声函数（满足epsilon-差分隐私）
CREATE OR REPLACE FUNCTION add_laplace_noise(value numeric, epsilon numeric DEFAULT 0.1)
RETURNS numeric AS $$
DECLARE
    sensitivity numeric := 1.0;
    scale numeric;
    u numeric;
    noise numeric;
BEGIN
    scale := sensitivity / epsilon;

    -- 生成Laplace噪声
    u := random() - 0.5;
    noise := -scale * sign(u) * ln(1 - 2 * abs(u));

    RETURN value + noise;
END;
$$ LANGUAGE plpgsql VOLATILE;

-- 使用示例：查询平均薪资（带隐私保护）
SELECT add_laplace_noise(AVG(salary)::numeric, 0.1) AS avg_salary_dp
FROM employees
WHERE department = 'engineering';
```

---

## 4. 安全加固实战

### 4.1 SSL/TLS加密

**配置服务器**（`postgresql.conf`）：

```conf
# SSL配置
ssl = on
ssl_cert_file = '/etc/postgresql/17/main/server.crt'
ssl_key_file = '/etc/postgresql/17/main/server.key'
ssl_ca_file = '/etc/postgresql/17/main/root.crt'

# 强制SSL
ssl_min_protocol_version = 'TLSv1.2'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on

# 客户端证书认证
ssl_ca_file = '/etc/postgresql/17/main/root.crt'
```

**配置pg_hba.conf**：

```conf
# 强制SSL连接
hostssl all all 0.0.0.0/0 scram-sha-256
hostssl all all ::/0 scram-sha-256

# 要求客户端证书
hostssl all all 0.0.0.0/0 cert clientcert=verify-full

# 特定用户必须使用SSL
hostssl admin all 0.0.0.0/0 scram-sha-256
host admin all 0.0.0.0/0 reject
```

**生成证书**：

```bash
# 1. 生成CA证书
openssl genrsa -out root.key 2048
openssl req -new -x509 -key root.key -out root.crt -days 3650

# 2. 生成服务器证书
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -CA root.crt -CAkey root.key -CAcreateserial -out server.crt -days 365

# 3. 设置权限
chmod 600 server.key
chown postgres:postgres server.key server.crt root.crt

# 4. 测试连接
psql "host=localhost dbname=mydb sslmode=require"
```

### 4.2 数据加密（pgcrypto）

```sql
-- 创建扩展
CREATE EXTENSION pgcrypto;

-- 对称加密（AES）
CREATE TABLE encrypted_data (
    id serial PRIMARY KEY,
    data_encrypted bytea,
    key_id int NOT NULL
);

-- 加密插入
INSERT INTO encrypted_data (data_encrypted, key_id)
VALUES (
    pgp_sym_encrypt('sensitive data', 'encryption-key'),
    1
);

-- 解密查询
SELECT
    id,
    pgp_sym_decrypt(data_encrypted, 'encryption-key') AS data_decrypted
FROM encrypted_data;

-- 非对称加密（RSA）
-- 生成密钥对
SELECT
    armor(gen_random_bytes(32)) AS encryption_key,
    armor(gen_random_bytes(32)) AS decryption_key;

-- 使用公钥加密
INSERT INTO encrypted_data (data_encrypted, key_id)
VALUES (
    pgp_pub_encrypt('sensitive data', dearmor('-----BEGIN PGP PUBLIC KEY BLOCK-----...')),
    1
);

-- 使用私钥解密
SELECT
    pgp_pub_decrypt(data_encrypted, dearmor('-----BEGIN PGP PRIVATE KEY BLOCK-----...'))
FROM encrypted_data;
```

**列级加密方案**：

```sql
CREATE TABLE users_secure (
    id serial PRIMARY KEY,
    username text NOT NULL,
    email_encrypted bytea,      -- 加密存储
    phone_encrypted bytea,       -- 加密存储
    ssn_encrypted bytea,         -- 加密存储
    key_id int NOT NULL,         -- 密钥标识
    created_at timestamptz DEFAULT now()
);

-- 加密辅助函数
CREATE OR REPLACE FUNCTION encrypt_column(data text, key_id int)
RETURNS bytea AS $$
DECLARE
    encryption_key text;
BEGIN
    -- 从密钥管理表获取密钥（实际应该从KMS）
    SELECT key INTO encryption_key
    FROM encryption_keys
    WHERE id = key_id;

    RETURN pgp_sym_encrypt(data, encryption_key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 解密辅助函数
CREATE OR REPLACE FUNCTION decrypt_column(data_encrypted bytea, key_id int)
RETURNS text AS $$
DECLARE
    decryption_key text;
BEGIN
    SELECT key INTO decryption_key
    FROM encryption_keys
    WHERE id = key_id;

    RETURN pgp_sym_decrypt(data_encrypted, decryption_key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 插入数据
INSERT INTO users_secure (username, email_encrypted, phone_encrypted, key_id)
VALUES (
    'alice',
    encrypt_column('alice@example.com', 1),
    encrypt_column('13800138000', 1),
    1
);

-- 查询数据
SELECT
    id,
    username,
    decrypt_column(email_encrypted, key_id) AS email,
    decrypt_column(phone_encrypted, key_id) AS phone
FROM users_secure;
```

### 4.3 密钥轮换

```sql
-- 密钥管理表
CREATE TABLE encryption_keys (
    key_id serial PRIMARY KEY,
    key_version int NOT NULL,
    key_value text NOT NULL,  -- 实际应该存在KMS中
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    expires_at timestamptz
);

-- 密钥轮换函数
CREATE OR REPLACE FUNCTION rotate_encryption_key()
RETURNS void AS $$
DECLARE
    old_key_id int;
    new_key_id int;
    old_key text;
    new_key text;
BEGIN
    -- 获取当前活跃密钥
    SELECT key_id, key_value INTO old_key_id, old_key
    FROM encryption_keys
    WHERE is_active = true
    ORDER BY key_id DESC
    LIMIT 1;

    -- 生成新密钥
    INSERT INTO encryption_keys (key_version, key_value, is_active)
    VALUES (
        (SELECT max(key_version) + 1 FROM encryption_keys),
        encode(gen_random_bytes(32), 'base64'),
        true
    )
    RETURNING key_id, key_value INTO new_key_id, new_key;

    -- 重新加密所有数据
    UPDATE users_secure
    SET
        email_encrypted = pgp_sym_encrypt(
            pgp_sym_decrypt(email_encrypted, old_key),
            new_key
        ),
        phone_encrypted = pgp_sym_encrypt(
            pgp_sym_decrypt(phone_encrypted, old_key),
            new_key
        ),
        key_id = new_key_id
    WHERE key_id = old_key_id;

    -- 停用旧密钥
    UPDATE encryption_keys
    SET is_active = false
    WHERE key_id = old_key_id;

    RAISE NOTICE 'Key rotation completed: % -> %', old_key_id, new_key_id;
END;
$$ LANGUAGE plpgsql;

-- 定期轮换（每季度）
SELECT cron.schedule('rotate_key', '0 0 1 */3 *', 'SELECT rotate_encryption_key()');
```

---

## 5. 渗透测试

### 5.1 SQL注入测试

**测试用例**：

```sql
-- 测试1：基础SQL注入
DO $$
DECLARE
    malicious_input text := $$' OR '1'='1$$;
    result text;
BEGIN
    -- 不安全的查询（永远不要这样做）
    EXECUTE 'SELECT username FROM users WHERE username = ''' || malicious_input || '''';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'SQL injection blocked: %', SQLERRM;
END $$;

-- 测试2：使用参数化查询（安全）
DO $$
DECLARE
    malicious_input text := $$' OR '1'='1$$;
    result text;
BEGIN
    EXECUTE 'SELECT username FROM users WHERE username = $1'
    INTO result
    USING malicious_input;

    RAISE NOTICE 'Result: %', result;  -- 返回NULL或具体值，不会注入
END $$;
```

**SQL注入防护清单**：

```sql
-- ✅ 安全：使用参数化查询
PREPARE get_user(text) AS
    SELECT * FROM users WHERE username = $1;
EXECUTE get_user('alice');

-- ✅ 安全：使用quote_literal
EXECUTE 'SELECT * FROM users WHERE username = ' || quote_literal(user_input);

-- ✅ 安全：使用quote_ident（标识符）
EXECUTE 'SELECT * FROM ' || quote_ident(table_name);

-- ✅ 安全：使用format with %L (literal) 和 %I (identifier)
EXECUTE format('SELECT * FROM %I WHERE username = %L', table_name, user_input);

-- ❌ 不安全：字符串拼接
EXECUTE 'SELECT * FROM users WHERE username = ''' || user_input || '''';
```

### 5.2 权限提升测试

```sql
-- 测试1：检查SECURITY DEFINER函数
SELECT
    n.nspname AS schema,
    p.proname AS function,
    pg_get_userbyid(p.proowner) AS owner,
    p.prosecdef AS security_definer
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE p.prosecdef = true
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schema, function;

-- 测试2：检查危险的GRANT
SELECT
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'PUBLIC'
   OR privilege_type IN ('INSERT', 'UPDATE', 'DELETE')
ORDER BY table_schema, table_name;

-- 测试3：检查超级用户
SELECT
    rolname,
    rolsuper,
    rolinherit,
    rolcreaterole,
    rolcreatedb
FROM pg_roles
WHERE rolsuper = true;
```

### 5.3 DoS攻击测试

```sql
-- 测试1：资源耗尽攻击
-- 设置资源限制
ALTER ROLE test_user SET statement_timeout = '30s';
ALTER ROLE test_user SET lock_timeout = '10s';
ALTER ROLE test_user SET idle_in_transaction_session_timeout = '60s';

-- 测试2：连接耗尽
-- 限制连接数
ALTER ROLE test_user CONNECTION LIMIT 10;

-- 测试3：临时文件耗尽
-- 限制临时文件大小
ALTER DATABASE testdb SET temp_file_limit = '1GB';

-- 测试4：检查慢查询
SELECT
    pid,
    usename,
    datname,
    state,
    query_start,
    now() - query_start AS duration,
    query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - query_start > interval '10 seconds'
ORDER BY duration DESC;
```

---

## 6. 合规性检查

### 6.1 GDPR合规

```sql
-- 创建数据主体权限管理表
CREATE TABLE data_subject_requests (
    request_id serial PRIMARY KEY,
    user_id int NOT NULL,
    request_type text CHECK (request_type IN ('access', 'rectification', 'erasure', 'portability', 'restriction')),
    request_status text CHECK (request_status IN ('pending', 'processing', 'completed', 'rejected')),
    requested_at timestamptz DEFAULT now(),
    completed_at timestamptz,
    notes text
);

-- 数据导出（Right to Access）
CREATE OR REPLACE FUNCTION export_user_data(p_user_id int)
RETURNS jsonb AS $$
DECLARE
    result jsonb;
BEGIN
    SELECT jsonb_build_object(
        'user_info', (SELECT row_to_json(u) FROM users u WHERE id = p_user_id),
        'orders', (SELECT jsonb_agg(row_to_json(o)) FROM orders o WHERE user_id = p_user_id),
        'payments', (SELECT jsonb_agg(row_to_json(p)) FROM payments p WHERE user_id = p_user_id),
        'audit_log', (SELECT jsonb_agg(row_to_json(a)) FROM audit_log a WHERE user_name = (SELECT username FROM users WHERE id = p_user_id))
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 数据删除（Right to Erasure）
CREATE OR REPLACE FUNCTION erase_user_data(p_user_id int)
RETURNS void AS $$
BEGIN
    -- 记录删除请求
    INSERT INTO data_subject_requests (user_id, request_type, request_status)
    VALUES (p_user_id, 'erasure', 'processing');

    -- 删除或匿名化数据
    BEGIN
        -- 删除可删除的数据
        DELETE FROM user_sessions WHERE user_id = p_user_id;
        DELETE FROM user_preferences WHERE user_id = p_user_id;

        -- 匿名化必须保留的数据（如订单记录）
        UPDATE orders
        SET
            user_email = 'deleted@example.com',
            user_phone = NULL,
            billing_address = 'DELETED'
        WHERE user_id = p_user_id;

        -- 删除用户主记录
        DELETE FROM users WHERE id = p_user_id;

        -- 更新请求状态
        UPDATE data_subject_requests
        SET request_status = 'completed', completed_at = now()
        WHERE user_id = p_user_id AND request_type = 'erasure';

    EXCEPTION WHEN OTHERS THEN
        UPDATE data_subject_requests
        SET request_status = 'rejected', notes = SQLERRM
        WHERE user_id = p_user_id AND request_type = 'erasure';

        RAISE;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 6.2 数据保留策略

```sql
-- 数据保留策略表
CREATE TABLE retention_policies (
    policy_id serial PRIMARY KEY,
    table_name text NOT NULL,
    retention_period interval NOT NULL,
    action text CHECK (action IN ('delete', 'archive', 'anonymize')),
    is_active boolean DEFAULT true
);

-- 插入策略
INSERT INTO retention_policies (table_name, retention_period, action) VALUES
    ('audit_log', '7 years', 'archive'),
    ('user_sessions', '90 days', 'delete'),
    ('temp_data', '7 days', 'delete'),
    ('orders', '10 years', 'anonymize');

-- 执行保留策略函数
CREATE OR REPLACE FUNCTION apply_retention_policy()
RETURNS TABLE(table_name text, action text, rows_affected bigint) AS $$
DECLARE
    policy record;
    cutoff_date timestamptz;
    rows_count bigint;
BEGIN
    FOR policy IN
        SELECT * FROM retention_policies WHERE is_active = true
    LOOP
        cutoff_date := now() - policy.retention_period;

        IF policy.action = 'delete' THEN
            EXECUTE format(
                'DELETE FROM %I WHERE created_at < $1',
                policy.table_name
            ) USING cutoff_date;

        ELSIF policy.action = 'archive' THEN
            -- 移动到归档表
            EXECUTE format(
                'INSERT INTO %I_archive SELECT * FROM %I WHERE created_at < $1',
                policy.table_name, policy.table_name
            ) USING cutoff_date;

            EXECUTE format(
                'DELETE FROM %I WHERE created_at < $1',
                policy.table_name
            ) USING cutoff_date;

        ELSIF policy.action = 'anonymize' THEN
            -- 匿名化旧数据
            EXECUTE format(
                'UPDATE %I SET email = ''deleted@example.com'', phone = NULL WHERE created_at < $1',
                policy.table_name
            ) USING cutoff_date;
        END IF;

        GET DIAGNOSTICS rows_count = ROW_COUNT;

        RETURN QUERY SELECT policy.table_name, policy.action, rows_count;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 定期执行（每天凌晨3点）
SELECT cron.schedule('apply_retention', '0 3 * * *', 'SELECT apply_retention_policy()');
```

---

## 7. 完整实战案例

### 7.1 案例：多租户SaaS安全方案

**需求**：
- 1000+租户，完全数据隔离
- 每个租户有自己的用户和权限
- 审计所有数据访问
- 支持数据导出和删除（GDPR）

**完整实现**：

```sql
-- 1. 租户和用户表
CREATE TABLE tenants (
    tenant_id serial PRIMARY KEY,
    tenant_name text UNIQUE NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now()
);

CREATE TABLE users (
    user_id serial PRIMARY KEY,
    tenant_id int NOT NULL REFERENCES tenants(tenant_id),
    username text NOT NULL,
    email text NOT NULL,
    role text CHECK (role IN ('admin', 'user', 'readonly')),
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    UNIQUE(tenant_id, username)
);

-- 2. 业务表（所有表都有tenant_id）
CREATE TABLE projects (
    project_id serial PRIMARY KEY,
    tenant_id int NOT NULL REFERENCES tenants(tenant_id),
    project_name text NOT NULL,
    owner_id int NOT NULL REFERENCES users(user_id),
    created_at timestamptz DEFAULT now()
);

CREATE TABLE tasks (
    task_id serial PRIMARY KEY,
    tenant_id int NOT NULL REFERENCES tenants(tenant_id),
    project_id int NOT NULL REFERENCES projects(project_id),
    assignee_id int REFERENCES users(user_id),
    task_title text NOT NULL,
    task_status text,
    created_at timestamptz DEFAULT now()
);

-- 3. 启用RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- 4. RLS策略：租户隔离
CREATE POLICY tenant_isolation_projects
    ON projects
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::int);

CREATE POLICY tenant_isolation_tasks
    ON tasks
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::int);

-- 5. RLS策略：角色权限
CREATE POLICY project_owner_access
    ON projects
    FOR UPDATE
    USING (
        owner_id = current_setting('app.user_id')::int
        OR current_setting('app.user_role') = 'admin'
    );

CREATE POLICY task_assignee_access
    ON tasks
    FOR UPDATE
    USING (
        assignee_id = current_setting('app.user_id')::int
        OR current_setting('app.user_role') = 'admin'
    );

-- 6. 审计所有表
CREATE TRIGGER audit_projects
    AFTER INSERT OR UPDATE OR DELETE ON projects
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_tasks
    AFTER INSERT OR UPDATE OR DELETE ON tasks
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- 7. 应用层连接管理
CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id int, p_user_id int, p_role text)
RETURNS void AS $$
BEGIN
    -- 验证租户和用户关系
    IF NOT EXISTS (
        SELECT 1 FROM users
        WHERE user_id = p_user_id
          AND tenant_id = p_tenant_id
          AND is_active = true
    ) THEN
        RAISE EXCEPTION 'Invalid user or tenant';
    END IF;

    -- 设置会话变量
    PERFORM set_config('app.tenant_id', p_tenant_id::text, false);
    PERFORM set_config('app.user_id', p_user_id::text, false);
    PERFORM set_config('app.user_role', p_role, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. 使用示例（应用层）
-- 每个请求开始时调用
SELECT set_tenant_context(123, 456, 'user');

-- 现在所有查询都自动应用RLS
SELECT * FROM projects;  -- 只返回tenant_id=123的数据
SELECT * FROM tasks;     -- 只返回tenant_id=123的数据
```

### 7.2 案例：金融系统审计方案

**需求**：
- 所有交易必须审计
- 审计日志不可篡改
- 支持审计日志查询和分析
- 符合SOC2、PCI-DSS要求

**完整实现**（参考上文不可篡改审计日志）

---

## 📊 安全检查清单

### 日常安全检查

```sql
-- 1. 检查弱密码
SELECT rolname
FROM pg_authid
WHERE rolpassword IS NULL
   OR rolpassword = ''
   OR rolcanlogin = true;

-- 2. 检查过期密码（需要自定义实现）
SELECT rolname, rolvaliduntil
FROM pg_authid
WHERE rolvaliduntil < now();

-- 3. 检查权限过大的角色
SELECT
    grantee,
    string_agg(privilege_type, ', ') AS privileges
FROM information_schema.table_privileges
WHERE grantee NOT IN ('postgres', 'pg_monitor')
GROUP BY grantee
HAVING count(*) > 100;  -- 拥有超过100个权限

-- 4. 检查未加密连接
SELECT
    datname,
    usename,
    client_addr,
    ssl,
    query
FROM pg_stat_ssl
JOIN pg_stat_activity USING (pid)
WHERE ssl = false
  AND client_addr IS NOT NULL;

-- 5. 检查长期未使用的账号
SELECT
    rolname,
    rolvaliduntil,
    '90 days' AS inactive_threshold
FROM pg_authid
WHERE rolcanlogin = true
  AND NOT EXISTS (
      SELECT 1 FROM pg_stat_activity
      WHERE usename = rolname
  );
```

---

## 📚 参考资源

### 官方文档
1. [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
2. [pgAudit](https://github.com/pgaudit/pgaudit)
3. [pgcrypto](https://www.postgresql.org/docs/current/pgcrypto.html)
4. [postgresql_anonymizer](https://postgresql-anonymizer.readthedocs.io/)

### 最佳实践
1. [OWASP PostgreSQL Security](https://cheatsheetseries.owasp.org/cheatsheets/PostgreSQL_Cheat_Sheet.html)
2. [CIS PostgreSQL Benchmark](https://www.cisecurity.org/benchmark/postgresql)
3. [PostgreSQL Security Best Practices](https://www.postgresql.org/docs/current/security.html)

### 合规框架
1. **GDPR**: 数据保护条例
2. **CCPA**: 加州消费者隐私法
3. **SOC 2**: 服务组织控制
4. **PCI-DSS**: 支付卡行业数据安全标准
5. **HIPAA**: 健康保险便携性和责任法案

---

**创建时间**: 2025年1月
**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**难度等级**: ⭐⭐⭐⭐ 高级

🔒 **构建安全可信的PostgreSQL系统！**
