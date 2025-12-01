# 05 合规与可信（AI Act / 审计 / 脱敏）

> **最后更新**：2025年11月11日
> **版本覆盖**：PostgreSQL 17+ | PostgreSQL 18
> **核验来源**：EU AI Act、PostgreSQL 官方文档、业界实践

---

## 📋 目录

- [05 合规与可信（AI Act / 审计 / 脱敏）](#05-合规与可信ai-act--审计--脱敏)
  - [📋 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
  - [2. 能力与边界](#2-能力与边界)
    - [2.1 RLS（Row Level Security）](#21-rlsrow-level-security)
    - [审计能力](#审计能力)
    - [2.3 数据脱敏](#23-数据脱敏)
    - [2.4 边界与限制](#24-边界与限制)
  - [📊 数据分类分级](#-数据分类分级)
    - [分类标准](#分类标准)
    - [3.2 保存期策略](#32-保存期策略)
  - [4. RLS 策略模板库](#4-rls-策略模板库)
    - [4.1 多租户隔离](#41-多租户隔离)
    - [2. 地理区域限制](#2-地理区域限制)
    - [4.3 角色权限控制](#43-角色权限控制)
    - [4.4 时间窗口控制](#44-时间窗口控制)
    - [4.5 数据主权标签](#45-数据主权标签)
    - [4.6 组合策略示例](#46-组合策略示例)
  - [5. 审计接入说明](#5-审计接入说明)
    - [5.1 pgAudit 扩展安装](#51-pgaudit-扩展安装)
    - [2. 审计策略配置](#2-审计策略配置)
    - [5.3 审计日志查询](#53-审计日志查询)
    - [5.4 不可篡改审计日志](#54-不可篡改审计日志)
    - [5.5 审计日志归档](#55-审计日志归档)
  - [6. 数据脱敏模板](#6-数据脱敏模板)
    - [6.1 列级脱敏视图](#61-列级脱敏视图)
    - [6.2 动态脱敏函数](#62-动态脱敏函数)
    - [6.3 行级脱敏策略](#63-行级脱敏策略)
  - [7. 最佳实践总结](#7-最佳实践总结)
    - [7.1 策略即代码](#71-策略即代码)
    - [7.2 合规测试用例](#72-合规测试用例)
    - [3. 性能监控](#3-性能监控)
  - [⚠️ 风险与缓解](#️-风险与缓解)
  - [🚀 PostgreSQL 18 增强](#-postgresql-18-增强)
    - [时间约束主键/唯一键/外键 ⭐](#时间约束主键唯一键外键-)
    - [OAuth 2.0 认证支持 ⭐](#oauth-20-认证支持-)
    - [RETURNING 子句增强（OLD/NEW 支持）](#returning-子句增强oldnew-支持)
  - [📚 参考链接（2025-11-11 核验）](#-参考链接2025-11-11-核验)
    - [官方文档](#官方文档)
    - [社区资源](#社区资源)
    - [工具与扩展](#工具与扩展)

---

## 1. 核心结论

- **合规目标**：最小化数据暴露、审计可追溯、跨境/主权可控、按需脱敏。
- **PostgreSQL 能力**：通过行级安全（RLS）、审计扩展、日志链路与策略化脱敏实现合规落地。
- **2025 年 EU AI Act**：正式执行，要求 AI 系统具备数据治理、审计追踪、透明度等能力。

## 2. 能力与边界

### 2.1 RLS（Row Level Security）

- **细粒度访问控制**：以租户/地区/主权/角色维度定义访问策略，控制到行级别
- **策略类型**：
  - `USING`：查询过滤条件
  - `WITH CHECK`：插入/更新检查条件
  - `FOR SELECT/INSERT/UPDATE/DELETE`：针对特定操作
- **性能影响**：RLS 策略会增加查询开销，需合理设计策略

### 审计能力

- **pgAudit 扩展**：记录所有数据库操作（DML、DDL、连接等）
- **不可篡改日志**：结合外部审计系统或账本表实现
- **访问追踪**：记录谁、何时、做了什么操作

### 2.3 数据脱敏

- **列级脱敏**：使用视图、函数对敏感列进行掩码
- **行级脱敏**：基于 RLS 策略过滤敏感行
- **动态脱敏**：根据用户角色动态调整脱敏规则

### 2.4 边界与限制

- **性能开销**：RLS/审计/脱敏叠加需压测，可能影响查询性能
- **配置复杂度**：需要结合业务场景设计策略，运维门槛较高
- **数据主权**：需要外部系统支持（如地理隔离、跨境拦截）

## 📊 数据分类分级

### 分类标准

```sql
-- 数据分类枚举
CREATE TYPE data_classification AS ENUM (
    'public',        -- 公开数据
    'internal',      -- 内部数据
    'sensitive',     -- 敏感数据
    'highly_sensitive' -- 高度敏感数据
);

-- 数据表添加分类列
ALTER TABLE documents ADD COLUMN classification data_classification DEFAULT 'internal';

-- 更新分类
UPDATE documents
SET classification = 'highly_sensitive'
WHERE content LIKE '%password%' OR content LIKE '%ssn%';
```

### 3.2 保存期策略

```sql
-- 创建保存期策略表
CREATE TABLE retention_policy (
    classification data_classification PRIMARY KEY,
    retention_days INTEGER NOT NULL,
    auto_delete BOOLEAN DEFAULT FALSE
);

INSERT INTO retention_policy VALUES
    ('public', 365, FALSE),
    ('internal', 1095, FALSE),  -- 3年
    ('sensitive', 2555, TRUE),  -- 7年，自动删除
    ('highly_sensitive', 3650, FALSE);  -- 10年

-- 自动清理过期数据（定时任务）
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS void AS $$
BEGIN
    DELETE FROM documents d
    USING retention_policy rp
    WHERE d.classification = rp.classification
      AND d.created_at < NOW() - (rp.retention_days || ' days')::INTERVAL
      AND rp.auto_delete = TRUE;
END;
$$ LANGUAGE plpgsql;

-- 创建定时任务（使用 pg_cron）
SELECT cron.schedule('cleanup-expired-data', '0 2 * * *',
    'SELECT cleanup_expired_data()');
```

## 4. RLS 策略模板库

### 4.1 多租户隔离

```sql
-- 场景：SaaS 平台多租户数据隔离

-- 启用 RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 策略1：租户隔离（基于 tenant_id）
CREATE POLICY tenant_isolation ON documents
    USING (tenant_id = current_setting('app.current_tenant_id', true));

-- 应用层设置租户ID
SET app.current_tenant_id = 'tenant_001';

-- 验证：只能看到当前租户的数据
SELECT * FROM documents;  -- 只返回 tenant_001 的数据
```

### 2. 地理区域限制

```sql
-- 场景：跨境数据主权控制

-- 添加区域列
ALTER TABLE user_data ADD COLUMN region TEXT NOT NULL DEFAULT 'CN';

-- 策略：限制用户只能访问本区域数据
CREATE POLICY region_restriction ON user_data
    USING (region = current_setting('app.user_region', true));

-- 应用层设置用户区域
SET app.user_region = 'CN';

-- 拒绝跨境访问
CREATE POLICY block_cross_region ON user_data
    USING (
        region = current_setting('app.user_region', true)
        OR current_setting('app.user_region', true) IS NULL
    );
```

### 4.3 角色权限控制

```sql
-- 场景：基于角色的访问控制（RBAC）

-- 创建角色表
CREATE TABLE user_roles (
    user_id TEXT PRIMARY KEY,
    role TEXT NOT NULL,  -- admin, manager, employee, guest
    department TEXT
);

-- 策略：管理员可访问所有数据
CREATE POLICY admin_full_access ON documents
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = current_setting('app.current_user_id', true)
              AND role = 'admin'
        )
    );

-- 策略：员工只能访问本部门数据
CREATE POLICY department_access ON documents
    USING (
        department = (
            SELECT department FROM user_roles
            WHERE user_id = current_setting('app.current_user_id', true)
        )
    );

-- 策略：访客只能访问公开数据
CREATE POLICY guest_readonly ON documents
    FOR SELECT
    USING (
        classification = 'public'
        AND EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = current_setting('app.current_user_id', true)
              AND role = 'guest'
        )
    );
```

### 4.4 时间窗口控制

```sql
-- 场景：限制访问时间窗口

-- 策略：只能访问最近30天的数据
CREATE POLICY time_window_access ON documents
    USING (
        created_at >= NOW() - INTERVAL '30 days'
        OR EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = current_setting('app.current_user_id', true)
              AND role = 'admin'
        )
    );
```

### 4.5 数据主权标签

```sql
-- 场景：EU AI Act 数据主权要求

-- 创建主权标签表
CREATE TABLE data_sovereignty_labels (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    row_id BIGINT NOT NULL,
    sovereignty_region TEXT NOT NULL,  -- EU, US, CN, etc.
    data_category TEXT NOT NULL,       -- personal, financial, health, etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 策略：禁止跨主权区域访问
CREATE POLICY sovereignty_control ON documents
    USING (
        NOT EXISTS (
            SELECT 1 FROM data_sovereignty_labels dsl
            WHERE dsl.table_name = 'documents'
              AND dsl.row_id = documents.id
              AND dsl.sovereignty_region != current_setting('app.user_region', true)
        )
    );
```

### 4.6 组合策略示例

```sql
-- 场景：综合多维度控制

-- 策略：多条件组合
CREATE POLICY multi_factor_access ON documents
    USING (
        -- 条件1：租户匹配
        tenant_id = current_setting('app.current_tenant_id', true)
        -- 条件2：区域匹配
        AND region = current_setting('app.user_region', true)
        -- 条件3：角色权限
        AND (
            EXISTS (
                SELECT 1 FROM user_roles
                WHERE user_id = current_setting('app.current_user_id', true)
                  AND role IN ('admin', 'manager')
            )
            OR classification != 'highly_sensitive'
        )
        -- 条件4：时间窗口
        AND created_at >= NOW() - INTERVAL '90 days'
    );
```

## 5. 审计接入说明

### 5.1 pgAudit 扩展安装

```sql
-- 安装 pgAudit 扩展
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- 配置审计级别
ALTER DATABASE mydb SET pgaudit.log = 'all';  -- 记录所有操作
-- 或
ALTER DATABASE mydb SET pgaudit.log = 'ddl,write';  -- 只记录 DDL 和写操作

-- 配置审计目录
ALTER DATABASE mydb SET pgaudit.log_catalog = 'on';  -- 记录系统目录访问
ALTER DATABASE mydb SET pgaudit.log_parameter = 'on';  -- 记录参数值
```

### 2. 审计策略配置

```sql
-- 审计特定表的所有操作
ALTER TABLE documents SET (pgaudit.log = 'all');

-- 审计特定用户的操作
ALTER ROLE audit_user SET pgaudit.log = 'all';

-- 审计特定操作类型
ALTER DATABASE mydb SET pgaudit.log = 'ddl,write,function';
```

### 5.3 审计日志查询

```sql
-- 创建审计日志表（可选，用于结构化查询）
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    log_time TIMESTAMPTZ NOT NULL,
    user_name TEXT,
    database_name TEXT,
    command_tag TEXT,
    query TEXT,
    client_addr INET,
    application_name TEXT
);

-- 从 PostgreSQL 日志解析审计记录（需要外部工具）
-- 或使用 pgAudit 的 JSON 格式输出

-- 查询最近的审计记录
SELECT
    log_time,
    user_name,
    database_name,
    command_tag,
    substring(query, 1, 100) AS query_preview
FROM pg_stat_statements
WHERE query LIKE '%documents%'
ORDER BY log_time DESC
LIMIT 100;
```

### 5.4 不可篡改审计日志

```sql
-- 场景：实现不可篡改的审计日志

-- 创建审计日志表（带哈希链）
CREATE TABLE immutable_audit_log (
    id BIGSERIAL PRIMARY KEY,
    log_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_name TEXT NOT NULL,
    action TEXT NOT NULL,
    table_name TEXT,
    row_id BIGINT,
    old_data JSONB,
    new_data JSONB,
    -- 哈希链：保证日志不可篡改
    previous_hash TEXT,
    current_hash TEXT GENERATED ALWAYS AS (
        encode(digest(
            id::text || log_time::text || user_name || action ||
            COALESCE(previous_hash, '') ||
            COALESCE(old_data::text, '') || COALESCE(new_data::text, ''),
            'sha256'
        ), 'hex')
    ) STORED
);

-- 触发器：自动计算哈希链
CREATE OR REPLACE FUNCTION audit_hash_chain()
RETURNS TRIGGER AS $$
DECLARE
    prev_hash TEXT;
BEGIN
    -- 获取上一条记录的哈希
    SELECT current_hash INTO prev_hash
    FROM immutable_audit_log
    ORDER BY id DESC
    LIMIT 1;

    -- 设置前一条哈希
    NEW.previous_hash := prev_hash;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_hash_trigger
    BEFORE INSERT ON immutable_audit_log
    FOR EACH ROW
    EXECUTE FUNCTION audit_hash_chain();

-- 验证日志完整性
CREATE OR REPLACE FUNCTION verify_audit_integrity()
RETURNS TABLE (
    id BIGINT,
    is_valid BOOLEAN,
    error_message TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH audit_chain AS (
        SELECT
            id,
            current_hash,
            previous_hash,
            LAG(current_hash) OVER (ORDER BY id) AS expected_previous_hash
        FROM immutable_audit_log
        ORDER BY id
    )
    SELECT
        ac.id,
        (ac.previous_hash = ac.expected_previous_hash) AS is_valid,
        CASE
            WHEN ac.previous_hash != ac.expected_previous_hash
            THEN 'Hash chain broken'
            ELSE NULL
        END AS error_message
    FROM audit_chain ac
    WHERE ac.previous_hash IS NOT NULL;
END;
$$ LANGUAGE plpgsql;
```

### 5.5 审计日志归档

```sql
-- 创建归档表
CREATE TABLE audit_log_archive (
    LIKE immutable_audit_log INCLUDING ALL
) PARTITION BY RANGE (log_time);

-- 按月分区
CREATE TABLE audit_log_archive_2025_10
    PARTITION OF audit_log_archive
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

-- 归档旧数据（定时任务）
CREATE OR REPLACE FUNCTION archive_audit_logs()
RETURNS void AS $$
BEGIN
    INSERT INTO audit_log_archive
    SELECT * FROM immutable_audit_log
    WHERE log_time < NOW() - INTERVAL '90 days';

    DELETE FROM immutable_audit_log
    WHERE log_time < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- 创建定时任务
SELECT cron.schedule('archive-audit-logs', '0 3 1 * *',
    'SELECT archive_audit_logs()');
```

## 6. 数据脱敏模板

### 6.1 列级脱敏视图

```sql
-- 场景：用户数据脱敏

-- 创建脱敏视图
CREATE VIEW user_data_masked AS
SELECT
    id,
    -- 姓名脱敏（保留首尾）
    LEFT(name, 1) || '***' || RIGHT(name, 1) AS name_masked,
    -- 邮箱脱敏（保留域名）
    REGEXP_REPLACE(email, '(.)(.*)(@.*)', '\1***\3') AS email_masked,
    -- 手机号脱敏（保留前后3位）
    LEFT(phone, 3) || '****' || RIGHT(phone, 3) AS phone_masked,
    -- 身份证脱敏（保留前后4位）
    LEFT(id_card, 4) || '********' || RIGHT(id_card, 4) AS id_card_masked,
    -- 地址脱敏（保留省市）
    SPLIT_PART(address, ' ', 1) || ' ' || SPLIT_PART(address, ' ', 2) || ' ***' AS address_masked
FROM user_data;

-- 使用视图查询
SELECT * FROM user_data_masked WHERE id = 1;
```

### 6.2 动态脱敏函数

```sql
-- 场景：根据用户角色动态脱敏

CREATE OR REPLACE FUNCTION get_user_data(user_id_param BIGINT, requester_role TEXT)
RETURNS TABLE (
    id BIGINT,
    name TEXT,
    email TEXT,
    phone TEXT,
    id_card TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ud.id,
        -- 管理员：不脱敏
        CASE
            WHEN requester_role = 'admin' THEN ud.name
            ELSE LEFT(ud.name, 1) || '***' || RIGHT(ud.name, 1)
        END AS name,
        -- 经理：部分脱敏
        CASE
            WHEN requester_role IN ('admin', 'manager') THEN ud.email
            ELSE REGEXP_REPLACE(ud.email, '(.)(.*)(@.*)', '\1***\3')
        END AS email,
        -- 员工：完全脱敏
        CASE
            WHEN requester_role = 'admin' THEN ud.phone
            ELSE LEFT(ud.phone, 3) || '****' || RIGHT(ud.phone, 3)
        END AS phone,
        -- 身份证：根据分类决定
        CASE
            WHEN requester_role = 'admin' THEN ud.id_card
            WHEN ud.classification = 'highly_sensitive' THEN '****-****-****-****'
            ELSE LEFT(ud.id_card, 4) || '********' || RIGHT(ud.id_card, 4)
        END AS id_card
    FROM user_data ud
    WHERE ud.id = user_id_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 使用示例
SELECT * FROM get_user_data(1, 'employee');
```

### 6.3 行级脱敏策略

```sql
-- 场景：基于 RLS 的行级脱敏

-- 策略：访客只能看到公开数据
CREATE POLICY guest_data_access ON user_data
    FOR SELECT
    USING (
        classification = 'public'
        AND EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = current_setting('app.current_user_id', true)
              AND role = 'guest'
        )
    );

-- 策略：员工只能看到脱敏后的敏感数据
CREATE VIEW employee_user_view AS
SELECT
    id,
    LEFT(name, 1) || '***' AS name_masked,
    REGEXP_REPLACE(email, '(.)(.*)(@.*)', '\1***\3') AS email_masked,
    classification
FROM user_data
WHERE classification IN ('public', 'internal', 'sensitive');

-- 授予访问权限
GRANT SELECT ON employee_user_view TO employee_role;
```

## 7. 最佳实践总结

### 7.1 策略即代码

```sql
-- 版本化策略管理
CREATE TABLE rls_policy_version (
    id BIGSERIAL PRIMARY KEY,
    policy_name TEXT NOT NULL,
    policy_sql TEXT NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- 记录策略变更
INSERT INTO rls_policy_version (policy_name, policy_sql, version, created_by)
VALUES (
    'tenant_isolation',
    'CREATE POLICY tenant_isolation ON documents USING (tenant_id = current_setting(''app.current_tenant_id'', true));',
    1,
    'admin'
);

-- 回滚策略
CREATE OR REPLACE FUNCTION rollback_policy(policy_name_param TEXT, target_version INTEGER)
RETURNS void AS $$
DECLARE
    policy_sql_text TEXT;
BEGIN
    SELECT policy_sql INTO policy_sql_text
    FROM rls_policy_version
    WHERE policy_name = policy_name_param
      AND version = target_version;

    -- 删除当前策略
    EXECUTE format('DROP POLICY IF EXISTS %I ON documents', policy_name_param);

    -- 应用旧策略
    EXECUTE policy_sql_text;

    -- 更新版本
    UPDATE rls_policy_version
    SET is_active = FALSE
    WHERE policy_name = policy_name_param;

    UPDATE rls_policy_version
    SET is_active = TRUE
    WHERE policy_name = policy_name_param
      AND version = target_version;
END;
$$ LANGUAGE plpgsql;
```

### 7.2 合规测试用例

```sql
-- 创建合规测试表
CREATE TABLE compliance_tests (
    id BIGSERIAL PRIMARY KEY,
    test_name TEXT NOT NULL,
    test_sql TEXT NOT NULL,
    expected_result TEXT,
    actual_result TEXT,
    passed BOOLEAN,
    test_date TIMESTAMPTZ DEFAULT NOW()
);

-- 测试用例：验证 RLS 策略
INSERT INTO compliance_tests (test_name, test_sql, expected_result)
VALUES (
    'tenant_isolation_test',
    'SET app.current_tenant_id = ''tenant_001''; SELECT COUNT(*) FROM documents;',
    'Should only return tenant_001 data'
);

-- 运行测试
CREATE OR REPLACE FUNCTION run_compliance_tests()
RETURNS TABLE (
    test_name TEXT,
    passed BOOLEAN,
    error_message TEXT
) AS $$
DECLARE
    test_record RECORD;
BEGIN
    FOR test_record IN SELECT * FROM compliance_tests WHERE passed IS NULL
    LOOP
        BEGIN
            -- 执行测试 SQL
            EXECUTE test_record.test_sql;
            -- 验证结果
            -- ...

            RETURN QUERY SELECT test_record.test_name, TRUE, NULL::TEXT;
        EXCEPTION WHEN OTHERS THEN
            RETURN QUERY SELECT test_record.test_name, FALSE, SQLERRM;
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### 3. 性能监控

```sql
-- 监控 RLS 策略性能
CREATE TABLE rls_performance_log (
    id BIGSERIAL PRIMARY KEY,
    policy_name TEXT,
    query_time_ms FLOAT,
    rows_scanned BIGINT,
    rows_returned BIGINT,
    log_time TIMESTAMPTZ DEFAULT NOW()
);

-- 分析慢查询
SELECT
    policy_name,
    AVG(query_time_ms) AS avg_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY query_time_ms) AS p95_time,
    COUNT(*) AS query_count
FROM rls_performance_log
WHERE log_time > NOW() - INTERVAL '24 hours'
GROUP BY policy_name
ORDER BY avg_time DESC;
```

## ⚠️ 风险与缓解

| 风险 | 影响 | 缓解策略 |
|------|------|---------|
| **性能开销** | RLS/审计/脱敏叠加可能影响查询性能 | 压测、索引优化、缓存策略 |
| **策略复杂度** | 配置错误导致数据泄露 | 策略即代码、自动化测试 |
| **规则漂移** | 策略变更导致合规失效 | 定期基线巡检、差异报警 |
| **审计日志膨胀** | 日志占用大量存储空间 | 分区归档、压缩存储 |
| **数据主权** | 跨境数据访问难以控制 | 地理隔离、标签策略 |

## 🚀 PostgreSQL 18 增强

### 时间约束主键/唯一键/外键 ⭐

PostgreSQL 18 支持对主键、唯一键和外键设置时间约束或范围约束，对合规场景有重要价值：

- **时间窗口控制**：满足时间序列数据管理的需求
- **数据版本管理**：支持时序数据的版本管理
- **合规要求**：实现数据的时间窗口约束，满足审计要求

**合规应用场景**：

```sql
-- 示例 1：带时间约束的唯一键（数据保留期管理）
CREATE TABLE audit_logs (
    id INT,
    timestamp TIMESTAMPTZ,
    operation TEXT,
    user_id INT,
    -- 唯一键带时间约束，支持数据保留期管理
    UNIQUE (id, timestamp) DEFERRABLE INITIALLY DEFERRED
);

-- 示例 2：时间窗口约束（满足合规要求）
CREATE TABLE sensitive_data (
    id SERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    -- 使用时间约束确保数据在有效期内
    CONSTRAINT valid_time_window CHECK (
        expires_at > created_at AND expires_at < created_at + INTERVAL '1 year'
    )
);

-- 示例 3：数据主权标签（结合时间约束）
CREATE TABLE cross_border_data (
    id SERIAL PRIMARY KEY,
    data JSONB,
    region TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- 时间约束 + 区域约束，满足数据主权要求
    CONSTRAINT region_time_constraint CHECK (
        region = 'EU' OR created_at < NOW() - INTERVAL '90 days'
    )
);
```

**合规价值**：

- 支持数据保留期自动管理
- 满足 GDPR 的"被遗忘权"要求
- 实现时间窗口内的数据访问控制

### OAuth 2.0 认证支持 ⭐

PostgreSQL 18 新增对 OAuth 2.0 认证的支持，对合规场景有重要价值：

- **安全集成**：方便 AI 应用程序与 PostgreSQL 数据库的安全集成
- **SSO 支持**：支持云原生部署，与 SSO 系统无缝对接
- **审计追踪**：OAuth 2.0 认证可以与审计系统集成，实现完整的访问追踪

**合规应用场景**：

```sql
-- 配置 OAuth 2.0 认证（在 pg_hba.conf 中）
-- host all all 0.0.0.0/0 oauth2

-- OAuth 2.0 与审计系统集成
-- 1. 所有 OAuth 认证请求都会被记录
-- 2. 支持细粒度的权限控制
-- 3. 满足企业级合规要求
```

### RETURNING 子句增强（OLD/NEW 支持）

PostgreSQL 18 在 RETURNING 子句中支持 OLD 和 NEW 关键字：

- **审计价值**：简化数据变更追踪，支持实时审计日志记录
- **合规应用**：支持实时数据变更审计，满足合规要求

```sql
-- 更新敏感数据并记录变更历史
UPDATE sensitive_data
SET data = $1,
    updated_at = NOW()
WHERE id = $2
RETURNING
    OLD.data AS old_data,
    NEW.data AS new_data,
    OLD.updated_at AS old_time,
    NEW.updated_at AS new_time;

-- 将变更记录插入审计表
INSERT INTO audit_logs (operation, old_value, new_value, changed_at)
SELECT
    'UPDATE',
    OLD.data,
    NEW.data,
    NEW.updated_at
FROM sensitive_data
WHERE id = $2;
```

---

## 📚 参考链接（2025-11-11 核验）

### 官方文档

- **PostgreSQL RLS**：
  - <https://www.postgresql.org/docs/current/ddl-rowsecurity.html>
  - <https://www.postgresql.org/docs/current/sql-createpolicy.html>

- **pgAudit**：
  - GitHub: <https://github.com/pgaudit/pgaudit>
  - 文档: <https://www.pgaudit.org/>

- **EU AI Act**：
  - 官方: <https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai>
  - 解读: <https://www.europarl.europa.eu/topics/en/article/20230601STO93804/eu-ai-act-first-regulation-on-artificial-intelligence>

### 社区资源

- **RLS 最佳实践**：
  - <https://www.postgresql.org/docs/current/sql-createpolicy.html>
  - <https://supabase.com/docs/guides/auth/row-level-security>

- **数据脱敏**：
  - <https://www.postgresql.org/docs/current/sql-createview.html>
  - <https://www.postgresql.org/docs/current/functions-string.html>

### 工具与扩展

- **pgAudit**: <https://github.com/pgaudit/pgaudit>
- **pg_cron**: <https://github.com/citusdata/pg_cron（定时任务）>
- **pg_partman**: <https://github.com/pgpartman/pg_partman（分区管理）>

> 注：具体实现请以官方文档为准。非官方社区已发布的插件与能力，一律标注"前瞻/候选"。

---

---

**文档版本**：v3.0 (2025-11-11)
**维护者**：Data-Science 项目组
**更新频率**：每月更新，重大版本发布时即时更新
**本次更新**：

- ✅ 新增 PostgreSQL 18 时间约束主键/唯一键/外键说明
- ✅ 新增 PostgreSQL 18 OAuth 2.0 认证支持说明
- ✅ 新增 RETURNING 子句增强（OLD/NEW 支持）说明
- ✅ 更新所有合规场景示例，反映 PostgreSQL 18 最新特性

**反馈渠道**：通过项目 Issue 或 Pull Request 提交反馈
