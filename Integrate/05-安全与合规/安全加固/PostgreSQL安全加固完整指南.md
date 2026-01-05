# PostgreSQL安全加固完整指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级

---

## 📋 目录

- [PostgreSQL安全加固完整指南](#postgresql安全加固完整指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 安全加固目标](#11-安全加固目标)
  - [2. 身份认证加固](#2-身份认证加固)
    - [2.1 密码策略](#21-密码策略)
    - [2.2 认证方法](#22-认证方法)
    - [2.3 SSL/TLS配置](#23-ssltls配置)
  - [3. 访问控制加固](#3-访问控制加固)
    - [3.1 权限最小化](#31-权限最小化)
    - [3.2 行级安全（RLS）](#32-行级安全rls)
  - [4. 数据加密加固](#4-数据加密加固)
    - [4.1 传输加密](#41-传输加密)
    - [4.2 存储加密](#42-存储加密)
  - [5. 审计与监控加固](#5-审计与监控加固)
    - [5.1 启用审计日志](#51-启用审计日志)
    - [5.2 监控配置](#52-监控配置)
  - [6. 网络加固](#6-网络加固)
    - [6.1 防火墙配置](#61-防火墙配置)
    - [6.2 连接限制](#62-连接限制)
  - [7. 系统加固](#7-系统加固)
    - [7.1 文件权限](#71-文件权限)
    - [7.2 禁用危险功能](#72-禁用危险功能)
  - [8. 合规性加固](#8-合规性加固)
    - [8.1 GDPR合规](#81-gdpr合规)
    - [8.2 审计合规](#82-审计合规)
  - [9. 安全检查清单](#9-安全检查清单)
    - [9.1 初始配置检查](#91-初始配置检查)
    - [9.2 运行时检查](#92-运行时检查)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

PostgreSQL安全加固是一个系统化的过程，涉及多个层面的安全措施。本指南提供完整的安全加固方案。

### 1.1 安全加固目标

PostgreSQL安全加固的目标是建立一个多层次、全方位的安全防护体系，确保数据库系统的安全性、完整性和可用性。

**核心安全目标**：

1. **防止未授权访问**：
   - 确保只有授权用户能访问数据库
   - 实现强身份认证机制
   - 控制网络访问和连接
   - 防止暴力破解和未授权访问

2. **保护数据安全**：
   - 防止数据泄露、篡改、丢失
   - 实现数据加密（传输和存储）
   - 保护敏感数据的完整性
   - 实现数据备份和恢复

3. **满足合规要求**：
   - 符合GDPR、HIPAA、PCI-DSS等法规要求
   - 实现审计日志和合规报告
   - 支持数据保留和删除策略
   - 满足行业特定的合规要求

4. **建立安全监控**：
   - 及时发现和响应安全事件
   - 实现安全审计和日志记录
   - 监控异常访问和行为
   - 建立安全告警机制

**安全加固的层次**：

```text
安全加固层次结构：
-----------------
应用层安全
  ├── 输入验证
  ├── SQL注入防护
  └── 应用级加密

数据库层安全
  ├── 身份认证
  ├── 访问控制
  ├── 数据加密
  └── 审计日志

网络层安全
  ├── SSL/TLS加密
  ├── 防火墙规则
  └── 连接限制

系统层安全
  ├── 文件权限
  ├── 操作系统安全
  └── 系统监控
```

**安全加固的收益**：

| 安全措施 | 安全收益 | 性能影响 | 实施难度 |
|---------|---------|---------|---------|
| **强密码策略** | ⭐⭐⭐⭐⭐ | 无 | ⭐⭐ |
| **SSL/TLS加密** | ⭐⭐⭐⭐⭐ | 5-10% | ⭐⭐⭐ |
| **行级安全（RLS）** | ⭐⭐⭐⭐⭐ | 10-20% | ⭐⭐⭐⭐ |
| **审计日志** | ⭐⭐⭐⭐ | 5-15% | ⭐⭐⭐ |
| **数据加密** | ⭐⭐⭐⭐⭐ | 15-30% | ⭐⭐⭐⭐ |

**安全加固的实施原则**：

1. **最小权限原则**：用户只获得完成工作所需的最小权限
2. **深度防御**：建立多层安全防护，不依赖单一安全措施
3. **定期审计**：定期检查和审计安全配置和访问日志
4. **及时更新**：及时应用安全补丁和更新
5. **持续监控**：持续监控安全事件和异常行为

---

## 2. 身份认证加固

### 2.1 密码策略

```sql
-- 安装passwordcheck扩展（如果可用，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'passwordcheck') THEN
            CREATE EXTENSION passwordcheck;
            RAISE NOTICE 'passwordcheck扩展安装成功';
        ELSE
            RAISE NOTICE 'passwordcheck扩展已存在';
        END IF;
    EXCEPTION
        WHEN undefined_file THEN
            RAISE WARNING 'passwordcheck扩展不可用，需要先安装';
        WHEN insufficient_privilege THEN
            RAISE EXCEPTION '需要超级用户权限来安装扩展';
        WHEN OTHERS THEN
            RAISE WARNING '安装passwordcheck扩展失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 配置密码复杂度要求（需要在postgresql.conf中设置，需要超级用户权限）
-- passwordcheck.min_length = 12
-- passwordcheck.max_length = 128
-- 设置后需要重启PostgreSQL或执行: SELECT pg_reload_conf();
```

### 2.2 认证方法

PostgreSQL支持多种认证方法，选择合适的认证方法对安全性至关重要。

**认证方法对比**：

| 认证方法 | 安全性 | 适用场景 | 推荐度 |
|---------|--------|---------|--------|
| **trust** | ⭐ | 仅本地开发 | ❌ 不推荐 |
| **md5** | ⭐⭐ | 旧系统兼容 | ⚠️ 不推荐 |
| **scram-sha-256** | ⭐⭐⭐⭐⭐ | 生产环境 | ✅ 强烈推荐 |
| **cert** | ⭐⭐⭐⭐⭐ | 高安全环境 | ✅ 推荐 |
| **ldap** | ⭐⭐⭐⭐ | 企业环境 | ✅ 推荐 |
| **pam** | ⭐⭐⭐⭐ | 系统集成 | ✅ 推荐 |

**推荐配置**：

```bash
# 编辑pg_hba.conf
# 推荐配置：
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# 本地连接（使用SCRAM-SHA-256）
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256

# SSL连接（强制SSL）
hostssl all             all             0.0.0.0/0               scram-sha-256

# 拒绝其他连接
host    all             all             0.0.0.0/0               reject
```

**认证方法详细说明**：

1. **SCRAM-SHA-256（推荐）**：
   - **安全性**：最高，使用SHA-256哈希和盐值
   - **性能**：良好，现代标准
   - **适用场景**：所有生产环境
   - **配置**：

     ```sql
     ALTER SYSTEM SET password_encryption = 'scram-sha-256';
     SELECT pg_reload_conf();
     ```

2. **SSL客户端证书（高安全）**：
   - **安全性**：最高，基于证书的双向认证
   - **性能**：良好，但需要证书管理
   - **适用场景**：高安全要求的系统
   - **配置**：

     ```bash
     # pg_hba.conf
     hostssl all all 0.0.0.0/0 cert
     ```

3. **LDAP认证（企业环境）**：
   - **安全性**：高，集中式身份管理
   - **性能**：取决于LDAP服务器
   - **适用场景**：企业环境，需要统一身份管理
   - **配置**：

     ```bash
     # pg_hba.conf
     host all all 0.0.0.0/0 ldap ldapserver=ldap.example.com ldapprefix="cn=" ldapsuffix=",dc=example,dc=com"
     ```

**认证方法最佳实践**：

1. **禁用trust认证**：

   ```bash
   # 检查是否有trust认证
   grep -E "^[^#].*trust" /etc/postgresql/*/main/pg_hba.conf

   # 如果有，改为scram-sha-256
   ```

2. **使用SSL连接**：
   - 强制所有远程连接使用SSL
   - 配置SSL证书和密钥
   - 验证客户端证书

3. **限制连接来源**：
   - 使用IP白名单限制连接
   - 只允许必要的IP地址连接
   - 使用防火墙进一步限制

4. **定期审查认证配置**：
   - 定期检查pg_hba.conf配置
   - 移除不必要的认证规则
   - 确保所有认证方法都是安全的

### 2.3 SSL/TLS配置

SSL/TLS配置是保护数据传输安全的关键措施，确保数据在传输过程中不被窃听或篡改。

**SSL/TLS配置步骤**：

1. **生成SSL证书**：

   ```bash
   # 生成自签名证书（仅用于测试）
   openssl req -new -x509 -days 365 -nodes -text \
     -out server.crt -keyout server.key \
     -subj "/CN=db.example.com"

   # 设置证书权限
   chmod 600 server.key
   chown postgres:postgres server.crt server.key
   ```

2. **配置PostgreSQL**：

   ```conf
   # postgresql.conf
   ssl = on
   ssl_cert_file = 'server.crt'
   ssl_key_file = 'server.key'
   ssl_ca_file = 'ca.crt'  # 如果使用CA签名的证书
   ```

3. **配置客户端连接**：

   ```bash
   # pg_hba.conf - 强制SSL连接
   hostssl all all 0.0.0.0/0 scram-sha-256

   # 拒绝非SSL连接
   host all all 0.0.0.0/0 reject
   ```

**SSL/TLS安全配置**：

1. **使用强加密算法**：

   ```conf
   # postgresql.conf
   ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
   ssl_prefer_server_ciphers = on
   ```

2. **启用SSL协议版本控制**：

   ```conf
   # 只允许TLS 1.2及以上版本
   ssl_min_protocol_version = 'TLSv1.2'
   ```

3. **配置SSL证书验证**：

   ```conf
   # 要求客户端证书（双向认证）
   ssl_ca_file = 'ca.crt'
   ssl_cert_file = 'server.crt'
   ssl_key_file = 'server.key'
   ```

**SSL/TLS性能优化**：

1. **使用会话缓存**：

   ```conf
   # postgresql.conf
   ssl_session_cache = on
   ssl_session_cache_size = 100MB
   ```

2. **启用SSL压缩（谨慎使用）**：

   ```conf
   # 注意：SSL压缩可能导致安全问题（CRIME攻击）
   # 通常不建议启用
   # ssl_compression = off
   ```

**SSL/TLS验证和测试**：

```sql
-- 检查SSL连接状态（带性能测试）
EXPLAIN ANALYZE
SELECT ssl_is_used();

-- 查看SSL连接信息（带性能测试）
EXPLAIN ANALYZE
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    ssl,
    sslversion,
    sslcipher
FROM pg_stat_ssl
JOIN pg_stat_activity USING (pid)
WHERE ssl = true;
```

**SSL/TLS最佳实践**：

1. **使用CA签名的证书**：生产环境应使用CA签名的证书，而不是自签名证书
2. **定期更新证书**：定期更新SSL证书，避免证书过期
3. **监控SSL连接**：监控SSL连接的使用情况和性能
4. **禁用弱加密**：禁用SSL 2.0、SSL 3.0和弱加密算法
5. **强制SSL连接**：对于敏感数据，强制所有连接使用SSL

```bash
# postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
ssl_ca_file = 'ca.crt'
```

---

## 3. 访问控制加固

### 3.1 权限最小化

```sql
-- 创建只读用户（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'readonly_user') THEN
            CREATE USER readonly_user WITH PASSWORD 'strong_password';
            RAISE NOTICE '只读用户创建成功';
        ELSE
            RAISE NOTICE '只读用户已存在';
        END IF;

        -- 授予权限
        IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'mydb') THEN
            GRANT CONNECT ON DATABASE mydb TO readonly_user;
            GRANT USAGE ON SCHEMA public TO readonly_user;
            GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
            RAISE NOTICE '只读用户权限授予成功';
        ELSE
            RAISE WARNING '数据库 mydb 不存在，跳过权限授予';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '只读用户已存在';
        WHEN undefined_database THEN
            RAISE WARNING '数据库 mydb 不存在';
            RAISE;
        WHEN OTHERS THEN
            RAISE WARNING '创建只读用户失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
            CREATE USER app_user WITH PASSWORD 'strong_password';
            RAISE NOTICE '应用用户创建成功';
        ELSE
            RAISE NOTICE '应用用户已存在';
        END IF;

        -- 授予权限
        IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'mydb') THEN
            GRANT CONNECT ON DATABASE mydb TO app_user;
            GRANT USAGE ON SCHEMA public TO app_user;
            GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
            RAISE NOTICE '应用用户权限授予成功';
        ELSE
            RAISE WARNING '数据库 mydb 不存在，跳过权限授予';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE '应用用户已存在';
        WHEN undefined_database THEN
            RAISE WARNING '数据库 mydb 不存在';
            RAISE;
        WHEN OTHERS THEN
            RAISE WARNING '创建应用用户失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 3.2 行级安全（RLS）

```sql
-- 启用RLS（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sensitive_data') THEN
            RAISE EXCEPTION '表 sensitive_data 不存在，请先创建该表';
        END IF;

        -- 启用RLS
        ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE '表 sensitive_data 已启用行级安全';

        -- 删除已存在的策略（如果存在）
        DROP POLICY IF EXISTS user_data_policy ON sensitive_data;

        -- 创建策略
        CREATE POLICY user_data_policy ON sensitive_data
            FOR ALL
            TO app_user
            USING (user_id = current_user_id());

        RAISE NOTICE '行级安全策略创建成功';
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 sensitive_data 不存在';
            RAISE;
        WHEN undefined_function THEN
            RAISE WARNING '函数 current_user_id() 不存在，请先创建该函数';
            RAISE;
        WHEN OTHERS THEN
            RAISE WARNING '启用RLS失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 4. 数据加密加固

### 4.1 传输加密

```sql
-- 强制SSL连接（带错误处理，需要超级用户权限）
DO $$
BEGIN
    BEGIN
        -- 检查是否有超级用户权限
        IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname = current_user) THEN
            RAISE EXCEPTION '需要超级用户权限来修改系统配置';
        END IF;

        -- 设置SSL配置
        ALTER SYSTEM SET ssl = on;
        ALTER SYSTEM SET ssl_cert_file = 'server.crt';
        ALTER SYSTEM SET ssl_key_file = 'server.key';

        -- 重新加载配置（不需要重启）
        PERFORM pg_reload_conf();

        RAISE NOTICE 'SSL配置已设置并重新加载';
    EXCEPTION
        WHEN insufficient_privilege THEN
            RAISE EXCEPTION '需要超级用户权限';
        WHEN OTHERS THEN
            RAISE WARNING '设置SSL配置失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 注意：修改后需要重启PostgreSQL使配置完全生效
-- 或者某些配置可以通过 pg_reload_conf() 重新加载
```

### 4.2 存储加密

```sql
-- 使用pgcrypto扩展（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            CREATE EXTENSION pgcrypto;
            RAISE NOTICE 'pgcrypto扩展安装成功';
        ELSE
            RAISE NOTICE 'pgcrypto扩展已存在';
        END IF;
    EXCEPTION
        WHEN undefined_file THEN
            RAISE EXCEPTION 'pgcrypto扩展不可用，需要先安装';
        WHEN insufficient_privilege THEN
            RAISE EXCEPTION '需要超级用户权限来安装扩展';
        WHEN OTHERS THEN
            RAISE WARNING '安装pgcrypto扩展失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 加密敏感数据（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE NOTICE '表 users 已存在，跳过创建';
        ELSE
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                email_encrypted BYTEA,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE INDEX idx_users_username ON users(username);
            RAISE NOTICE '表 users 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE NOTICE '表 users 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表 users 失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 加密函数（带错误处理）
DO $$
DECLARE
    encryption_key TEXT := 'encryption_key';
BEGIN
    BEGIN
        -- 检查pgcrypto扩展是否已安装
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE EXCEPTION 'pgcrypto扩展未安装，无法使用加密函数';
        END IF;

        -- 插入加密数据
        INSERT INTO users (username, password_hash, email_encrypted)
        VALUES (
            'user1',
            crypt('password', gen_salt('bf')),
            pgp_sym_encrypt('user@example.com', encryption_key)
        ) ON CONFLICT (username) DO NOTHING;

        RAISE NOTICE '加密数据插入成功';
    EXCEPTION
        WHEN undefined_function THEN
            RAISE WARNING '加密函数不可用，请检查pgcrypto扩展';
            RAISE;
        WHEN OTHERS THEN
            RAISE WARNING '插入加密数据失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 5. 审计与监控加固

### 5.1 启用审计日志

```sql
-- 安装pgAudit扩展（带错误处理）
DO $$
BEGIN
    BEGIN
        -- 检查是否有超级用户权限
        IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname = current_user) THEN
            RAISE EXCEPTION '需要超级用户权限来安装扩展';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgaudit') THEN
            -- 注意：pgaudit需要在shared_preload_libraries中配置后才能创建扩展
            CREATE EXTENSION pgaudit;
            RAISE NOTICE 'pgAudit扩展安装成功';
        ELSE
            RAISE NOTICE 'pgAudit扩展已存在';
        END IF;
    EXCEPTION
        WHEN undefined_file THEN
            RAISE WARNING 'pgAudit扩展不可用，可能需要在shared_preload_libraries中配置';
        WHEN insufficient_privilege THEN
            RAISE EXCEPTION '需要超级用户权限来安装扩展';
        WHEN OTHERS THEN
            RAISE WARNING '安装pgAudit扩展失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 配置审计日志（带错误处理，需要超级用户权限）
DO $$
BEGIN
    BEGIN
        IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname = current_user) THEN
            RAISE EXCEPTION '需要超级用户权限来修改系统配置';
        END IF;

        ALTER SYSTEM SET pgaudit.log = 'all';
        ALTER SYSTEM SET pgaudit.log_catalog = off;
        ALTER SYSTEM SET pgaudit.log_parameter = on;

        -- 重新加载配置
        PERFORM pg_reload_conf();

        RAISE NOTICE '审计日志配置已设置';
    EXCEPTION
        WHEN insufficient_privilege THEN
            RAISE EXCEPTION '需要超级用户权限';
        WHEN OTHERS THEN
            RAISE WARNING '配置审计日志失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 5.2 监控配置

```sql
-- 监控配置（带错误处理，需要超级用户权限）
DO $$
BEGIN
    BEGIN
        IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname = current_user) THEN
            RAISE EXCEPTION '需要超级用户权限来修改系统配置';
        END IF;

        -- 记录所有DDL语句
        ALTER SYSTEM SET log_statement = 'ddl';

        -- 记录慢查询（1秒）
        ALTER SYSTEM SET log_min_duration_statement = 1000;

        -- 记录连接和断开
        ALTER SYSTEM SET log_connections = on;
        ALTER SYSTEM SET log_disconnections = on;

        -- 重新加载配置
        PERFORM pg_reload_conf();

        RAISE NOTICE '监控配置已设置';
    EXCEPTION
        WHEN insufficient_privilege THEN
            RAISE EXCEPTION '需要超级用户权限';
        WHEN OTHERS THEN
            RAISE WARNING '设置监控配置失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 6. 网络加固

### 6.1 防火墙配置

```bash
# 只允许必要的IP访问
# 使用iptables或firewalld限制访问
```

### 6.2 连接限制

```sql
-- 限制连接数（带错误处理，需要超级用户权限）
DO $$
BEGIN
    BEGIN
        IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname = current_user) THEN
            RAISE EXCEPTION '需要超级用户权限来修改系统配置';
        END IF;

        -- 限制连接数
        ALTER SYSTEM SET max_connections = 100;

        -- 注意：max_connections需要重启PostgreSQL才能生效
        RAISE NOTICE '连接数限制已设置（需要重启PostgreSQL生效）';
    EXCEPTION
        WHEN insufficient_privilege THEN
            RAISE EXCEPTION '需要超级用户权限';
        WHEN OTHERS THEN
            RAISE WARNING '设置连接数限制失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 限制每个用户的连接数（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
            RAISE EXCEPTION '用户 app_user 不存在，请先创建该用户';
        END IF;

        ALTER USER app_user WITH CONNECTION LIMIT 10;
        RAISE NOTICE '用户 app_user 连接数限制已设置为10';
    EXCEPTION
        WHEN undefined_object THEN
            RAISE WARNING '用户 app_user 不存在';
            RAISE;
        WHEN OTHERS THEN
            RAISE WARNING '设置用户连接数限制失败: %', SQLERRM;
            RAISE;
    END;
END $$;

```

---

## 7. 系统加固

### 7.1 文件权限

```bash
# 确保配置文件权限正确
chmod 600 postgresql.conf
chmod 600 pg_hba.conf
chmod 600 server.key
```

### 7.2 禁用危险功能

```sql
-- 禁用不安全的函数（如果不需要，带错误处理）
DO $$
BEGIN
    BEGIN
        -- 检查函数是否存在并撤销PUBLIC权限
        IF EXISTS (
            SELECT 1 FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'pg_catalog' AND p.proname = 'pg_read_file'
              AND pg_get_function_identity_arguments(p.oid) = 'text'
        ) THEN
            REVOKE EXECUTE ON FUNCTION pg_read_file(text) FROM PUBLIC;
            RAISE NOTICE '已撤销 pg_read_file(text) 的PUBLIC执行权限';
        ELSE
            RAISE NOTICE '函数 pg_read_file(text) 不存在或已撤销权限';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '撤销 pg_read_file 权限失败: %', SQLERRM;
    END;

    BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'pg_catalog' AND p.proname = 'pg_ls_dir'
              AND pg_get_function_identity_arguments(p.oid) = 'text'
        ) THEN
            REVOKE EXECUTE ON FUNCTION pg_ls_dir(text) FROM PUBLIC;
            RAISE NOTICE '已撤销 pg_ls_dir(text) 的PUBLIC执行权限';
        ELSE
            RAISE NOTICE '函数 pg_ls_dir(text) 不存在或已撤销权限';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '撤销 pg_ls_dir 权限失败: %', SQLERRM;
    END;
END $$;
```

---

## 8. 合规性加固

### 8.1 GDPR合规

```sql
-- 数据保留策略（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_data') THEN
            RAISE EXCEPTION '表 user_data 不存在，请先创建该表';
        END IF;

        -- 启用RLS（如果需要）
        ALTER TABLE user_data ENABLE ROW LEVEL SECURITY;

        -- 删除已存在的策略（如果存在）
        DROP POLICY IF EXISTS data_retention_policy ON user_data;

        -- 创建数据保留策略
        CREATE POLICY data_retention_policy ON user_data
            FOR DELETE
            USING (created_at < NOW() - INTERVAL '7 years');

        RAISE NOTICE '数据保留策略创建成功';
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 user_data 不存在';
            RAISE;
        WHEN OTHERS THEN
            RAISE WARNING '创建数据保留策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 数据脱敏（带错误处理）
DO $$
BEGIN
    BEGIN
        -- 检查anon扩展是否可用
        IF NOT EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'anon') THEN
            RAISE WARNING 'anon扩展不可用，可能需要安装';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'anon') THEN
            CREATE EXTENSION anon;
            RAISE NOTICE 'anon扩展安装成功';
        ELSE
            RAISE NOTICE 'anon扩展已存在';
        END IF;

        -- 测试数据脱敏
        RAISE NOTICE '脱敏测试: %', anon.mask('email', 'user@example.com');
    EXCEPTION
        WHEN undefined_file THEN
            RAISE WARNING 'anon扩展不可用';
        WHEN insufficient_privilege THEN
            RAISE EXCEPTION '需要超级用户权限来安装扩展';
        WHEN OTHERS THEN
            RAISE WARNING 'anon扩展操作失败: %', SQLERRM;
    END;
END $$;
```

### 8.2 审计合规

```sql
-- 不可篡改审计日志
-- 使用pgAudit和外部审计系统
```

---

## 9. 安全检查清单

### 9.1 初始配置检查

- [ ] 修改默认postgres用户密码
- [ ] 配置强密码策略
- [ ] 启用SSL/TLS
- [ ] 配置pg_hba.conf限制访问
- [ ] 禁用不必要的扩展

### 9.2 运行时检查

- [ ] 定期审查用户权限
- [ ] 检查审计日志
- [ ] 监控异常连接
- [ ] 检查系统更新
- [ ] 验证备份完整性

---

## 📚 相关文档

- [安全体系详解.md](../安全体系详解.md) - 安全体系完整说明
- [【深入】PostgreSQL安全深化-RLS与审计完整指南.md](../【深入】PostgreSQL安全深化-RLS与审计完整指南.md) - RLS与审计指南
- [05-安全与合规/README.md](../README.md) - 安全与合规主题

---

**最后更新**: 2025年1月
