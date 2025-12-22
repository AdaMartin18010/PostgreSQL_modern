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
-- 安装passwordcheck扩展（如果可用）
CREATE EXTENSION IF NOT EXISTS passwordcheck;

-- 配置密码复杂度要求
-- 在postgresql.conf中设置
-- passwordcheck.min_length = 12
-- passwordcheck.max_length = 128
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
-- 创建只读用户
CREATE USER readonly_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- 创建应用用户（只有必要的权限）
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
```

### 3.2 行级安全（RLS）

```sql
-- 启用RLS
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY user_data_policy ON sensitive_data
    FOR ALL
    TO app_user
    USING (user_id = current_user_id());
```

---

## 4. 数据加密加固

### 4.1 传输加密

```sql
-- 强制SSL连接
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = 'server.crt';
ALTER SYSTEM SET ssl_key_file = 'server.key';

-- 重启PostgreSQL使配置生效
```

### 4.2 存储加密

```sql
-- 使用pgcrypto扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 加密敏感数据
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password_hash TEXT,  -- 使用pgcrypto加密
    email_encrypted BYTEA  -- 加密存储
);

-- 加密函数
INSERT INTO users (username, password_hash, email_encrypted)
VALUES (
    'user1',
    crypt('password', gen_salt('bf')),
    pgp_sym_encrypt('user@example.com', 'encryption_key')
);
```

---

## 5. 审计与监控加固

### 5.1 启用审计日志

```sql
-- 安装pgAudit扩展
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- 配置审计日志
ALTER SYSTEM SET pgaudit.log = 'all';
ALTER SYSTEM SET pgaudit.log_catalog = off;
ALTER SYSTEM SET pgaudit.log_parameter = on;
```

### 5.2 监控配置

```sql
-- 记录所有DDL语句
ALTER SYSTEM SET log_statement = 'ddl';

-- 记录慢查询
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1秒

-- 记录连接和断开
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
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
-- 限制连接数
ALTER SYSTEM SET max_connections = 100;

-- 限制每个用户的连接数
ALTER USER app_user WITH CONNECTION LIMIT 10;
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
-- 禁用不安全的函数（如果不需要）
REVOKE EXECUTE ON FUNCTION pg_read_file(text) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION pg_ls_dir(text) FROM PUBLIC;
```

---

## 8. 合规性加固

### 8.1 GDPR合规

```sql
-- 数据保留策略
CREATE POLICY data_retention_policy ON user_data
    FOR DELETE
    USING (created_at < NOW() - INTERVAL '7 years');

-- 数据脱敏
CREATE EXTENSION IF NOT EXISTS anon;
SELECT anon.mask('email', 'user@example.com');
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
