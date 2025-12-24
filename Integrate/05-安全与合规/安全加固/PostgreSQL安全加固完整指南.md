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

- **防止未授权访问** - 确保只有授权用户能访问数据库
- **保护数据安全** - 防止数据泄露、篡改、丢失
- **满足合规要求** - 符合GDPR、HIPAA等法规要求
- **建立安全监控** - 及时发现和响应安全事件

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

```bash
# 编辑pg_hba.conf
# 推荐配置：
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
hostssl all             all             0.0.0.0/0               scram-sha-256
```

### 2.3 SSL/TLS配置

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
