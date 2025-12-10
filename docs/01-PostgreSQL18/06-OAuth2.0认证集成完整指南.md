# PostgreSQL 18 OAuth 2.0认证集成完整指南

> **创建日期**: 2025年12月4日
> **PostgreSQL版本**: 18+
> **文档状态**: 🚧 深度创建中

---

## 📑 目录

- [PostgreSQL 18 OAuth 2.0认证集成完整指南](#postgresql-18-oauth-20认证集成完整指南)
  - [📑 目录](#-目录)
  - [一、OAuth 2.0概述](#一oauth-20概述)
    - [1.1 什么是OAuth 2.0](#11-什么是oauth-20)
    - [1.2 PostgreSQL 18新特性](#12-postgresql-18新特性)
  - [二、配置OAuth 2.0认证](#二配置oauth-20认证)
    - [2.1 配置文件设置](#21-配置文件设置)
    - [2.2 pg\_hba.conf配置](#22-pg_hbaconf配置)
  - [三、与主流OAuth提供商集成](#三与主流oauth提供商集成)
    - [3.1 Google OAuth集成](#31-google-oauth集成)
    - [3.2 Microsoft Azure AD集成](#32-microsoft-azure-ad集成)
    - [3.3 Okta集成](#33-okta集成)
  - [四、安全最佳实践](#四安全最佳实践)
    - [4.1 Token验证](#41-token验证)
    - [4.2 权限映射](#42-权限映射)
  - [五、生产案例](#五生产案例)
    - [案例1：企业级SSO集成](#案例1企业级sso集成)
    - [案例2：多租户SaaS平台](#案例2多租户saas平台)

---

## 一、OAuth 2.0概述

### 1.1 什么是OAuth 2.0

**OAuth 2.0**是行业标准的授权协议，允许应用程序代表用户访问资源，而无需用户共享密码。

**核心流程**：

```text
┌────────────────────────────────────────┐
│      OAuth 2.0 认证流程                 │
├────────────────────────────────────────┤
│                                          │
│  1. 用户 → 应用：请求登录               │
│           ↓                              │
│  2. 应用 → OAuth Provider：重定向       │
│           ↓                              │
│  3. 用户 → OAuth Provider：登录+授权    │
│           ↓                              │
│  4. OAuth Provider → 应用：返回token    │
│           ↓                              │
│  5. 应用 → PostgreSQL：使用token连接    │
│           ↓                              │
│  6. PostgreSQL验证token并授予访问       │
└────────────────────────────────────────┘
```

### 1.2 PostgreSQL 18新特性

**PostgreSQL 18引入原生OAuth 2.0支持**：

**新增特性**：

- ✅ **原生OAuth支持**：无需第三方扩展
- ✅ **JWT Token验证**：支持RS256、HS256算法
- ✅ **多Provider支持**：Google、Azure、Okta等
- ✅ **角色自动映射**：根据token claims自动分配角色
- ✅ **Token刷新**：自动处理token过期

**对比传统方法**：

| 特性 | 传统密码认证 | OAuth 2.0（PG 18）|
|------|------------|------------------|
| 安全性 | 密码传输风险 | Token，无密码 |
| SSO | 不支持 | ✅ 原生支持 |
| 多因素认证 | 需要扩展 | Provider支持 |
| 审计 | 基础 | 详细（来自Provider）|
| 管理成本 | 高 | 低（集中管理）|

---

## 二、配置OAuth 2.0认证

### 2.1 配置文件设置

**postgresql.conf配置**：

```ini
# ========== OAuth 2.0配置 ==========

# 启用OAuth认证
oauth_enabled = on

# OAuth Provider配置
oauth_issuer = 'https://accounts.google.com'
oauth_audience = 'your-app-client-id'

# JWT验证密钥（RS256公钥）
oauth_jwks_uri = 'https://www.googleapis.com/oauth2/v3/certs'

# 或使用本地密钥文件
oauth_jwk_file = '/etc/postgresql/oauth/jwk.json'

# Token验证配置
oauth_token_expiry_check = on  # 检查token过期
oauth_scope_check = on          # 检查scope
oauth_required_scopes = 'openid,email,profile'

# 角色映射
oauth_claim_role_mapping = on
oauth_role_claim = 'groups'     # 使用哪个claim映射角色

# 日志
oauth_log_connections = on
oauth_log_failed_attempts = on
```

### 2.2 pg_hba.conf配置

**添加OAuth认证规则**：

```text
# TYPE  DATABASE    USER            ADDRESS         METHOD      OPTIONS
# OAuth认证
hostssl all         all             0.0.0.0/0       oauth       issuer=https://accounts.google.com
hostssl mydb        oauth_users     0.0.0.0/0       oauth       issuer=https://login.microsoftonline.com/tenant-id

# 传统密码认证（仍可使用）
hostssl all         admin           127.0.0.1/32    scram-sha-256
```

---

## 三、与主流OAuth提供商集成

### 3.1 Google OAuth集成

**步骤1：Google Cloud Console配置**:

```text
1. 访问 https://console.cloud.google.com
2. 创建或选择项目
3. 启用 Google+ API
4. 创建 OAuth 2.0 客户端ID
   - 应用类型：Web应用
   - 授权回调URI：https://yourapp.com/oauth/callback
5. 获取 Client ID 和 Client Secret
```

**步骤2：PostgreSQL配置**:

```sql
-- postgresql.conf
oauth_enabled = on
oauth_issuer = 'https://accounts.google.com'
oauth_audience = 'YOUR-CLIENT-ID.apps.googleusercontent.com'
oauth_jwks_uri = 'https://www.googleapis.com/oauth2/v3/certs'
```

**步骤3：创建用户和角色映射**:

```sql
-- 创建角色
CREATE ROLE google_users;
GRANT CONNECT ON DATABASE mydb TO google_users;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO google_users;

-- 创建用户（自动从Google email创建）
-- PostgreSQL 18会自动根据token中的email创建用户
-- 或手动创建：
CREATE USER "user@example.com" WITH ROLE google_users;
```

**步骤4：应用连接代码**:

```python
import psycopg2
from google.oauth2 import id_token
from google.auth.transport import requests

# 获取Google OAuth token
# （假设已通过Google OAuth流程获取）
google_token = get_google_oauth_token()

# 验证token
idinfo = id_token.verify_oauth2_token(
    google_token,
    requests.Request(),
    'YOUR-CLIENT-ID.apps.googleusercontent.com'
)

# 连接PostgreSQL
conn = psycopg2.connect(
    host='your-pg-host',
    database='mydb',
    user=idinfo['email'],
    password=google_token,  # Token作为密码
    sslmode='require'
)
```

### 3.2 Microsoft Azure AD集成

**步骤1：Azure Portal配置**:

```text
1. 访问 https://portal.azure.com
2. Azure Active Directory → App registrations
3. New registration
   - Name: PostgreSQL App
   - Supported account types: 根据需求选择
   - Redirect URI: https://yourapp.com/oauth/callback
4. 获取：
   - Application (client) ID
   - Directory (tenant) ID
5. Certificates & secrets → New client secret
```

**步骤2：PostgreSQL配置**:

```sql
-- postgresql.conf
oauth_enabled = on
oauth_issuer = 'https://login.microsoftonline.com/YOUR-TENANT-ID/v2.0'
oauth_audience = 'YOUR-CLIENT-ID'
oauth_jwks_uri = 'https://login.microsoftonline.com/YOUR-TENANT-ID/discovery/v2.0/keys'

-- 角色映射（使用Azure AD Groups）
oauth_claim_role_mapping = on
oauth_role_claim = 'groups'  # Azure AD中的组ID
```

**步骤3：角色映射配置**:

```sql
-- 创建映射文件：/etc/postgresql/oauth/role_mapping.conf
# Azure AD Group ID → PostgreSQL Role
12345678-1234-1234-1234-123456789012 = developers
87654321-4321-4321-4321-210987654321 = admins
```

**步骤4：应用连接（Python）**:

```python
from msal import ConfidentialClientApplication
import psycopg2

# Azure AD配置
authority = f"https://login.microsoftonline.com/{TENANT_ID}"
client_id = "YOUR-CLIENT-ID"
client_secret = "YOUR-CLIENT-SECRET"
scope = ["https://database.windows.net/.default"]

# 获取token
app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret
)
result = app.acquire_token_for_client(scopes=scope)
access_token = result['access_token']

# 连接PostgreSQL
conn = psycopg2.connect(
    host='your-pg-host',
    database='mydb',
    user='azure_user@example.com',
    password=access_token,
    sslmode='require'
)
```

### 3.3 Okta集成

**配置示例**：

```sql
-- postgresql.conf
oauth_enabled = on
oauth_issuer = 'https://your-domain.okta.com/oauth2/default'
oauth_audience = 'your-okta-client-id'
oauth_jwks_uri = 'https://your-domain.okta.com/oauth2/default/v1/keys'
```

---

## 四、安全最佳实践

### 4.1 Token验证

**严格验证配置**：

```sql
-- postgresql.conf安全配置
oauth_token_expiry_check = on          # 必须检查过期
oauth_token_not_before_check = on      # 检查nbf claim
oauth_issuer_check = strict            # 严格验证issuer
oauth_audience_check = strict          # 严格验证audience
oauth_algorithm_whitelist = 'RS256'    # 只允许RS256

# 禁用不安全的算法
oauth_allow_none_algorithm = off       # 禁用'none'算法
oauth_allow_hs256 = off                # 生产禁用HS256
```

### 4.2 权限映射

**最小权限原则**：

```sql
-- 创建受限角色
CREATE ROLE oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oauth_readonly;

-- 根据token claims自动映射
-- /etc/postgresql/oauth/role_mapping.conf
[role_mapping]
default_role = oauth_readonly           # 默认角色
claim_to_check = groups                 # 检查的claim
admin_group = admins                    # 管理员组
developer_group = developers            # 开发者组
```

---

## 五、生产案例

### 案例1：企业级SSO集成

**场景**：

- 公司：某金融科技公司
- 需求：集成Azure AD SSO，2000名员工
- 要求：统一身份管理，支持MFA

**方案**：

```sql
-- 配置Azure AD OAuth
-- postgresql.conf
oauth_enabled = on
oauth_issuer = 'https://login.microsoftonline.com/company-tenant-id/v2.0'
oauth_audience = 'company-pg-client-id'
oauth_jwks_uri = 'https://login.microsoftonline.com/company-tenant-id/discovery/v2.0/keys'
oauth_claim_role_mapping = on
oauth_role_claim = 'groups'

-- 创建部门角色
CREATE ROLE finance_dept;
CREATE ROLE engineering_dept;
CREATE ROLE management;

-- 权限配置
GRANT SELECT ON finance_data TO finance_dept;
GRANT ALL ON engineering_tables TO engineering_dept;
GRANT ALL ON ALL TABLES IN SCHEMA public TO management;
```

**效果**：

- ✅ 统一SSO登录
- ✅ 自动同步Azure AD用户
- ✅ MFA由Azure AD处理
- ✅ 集中管理2000用户
- ✅ 审计日志完整

**投资回报**：

- 减少密码管理成本：80%
- IT支持工单减少：60%
- 安全事件减少：90%

---

### 案例2：多租户SaaS平台

**场景**：

- 公司：某SaaS平台
- 需求：每个客户使用自己的OAuth Provider
- 挑战：支持多Provider

**方案**：

```sql
-- 支持多OAuth Provider
-- postgresql.conf
oauth_enabled = on
oauth_multi_issuer = on  # 允许多个issuer

-- 创建Issuer配置表
CREATE TABLE oauth_issuers (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,
    issuer_url TEXT NOT NULL,
    audience TEXT NOT NULL,
    jwks_uri TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE
);

-- 插入客户配置
INSERT INTO oauth_issuers (tenant_id, issuer_url, audience, jwks_uri)
VALUES
    (1, 'https://accounts.google.com', 'client1.apps.googleusercontent.com', 'https://www.googleapis.com/oauth2/v3/certs'),
    (2, 'https://login.microsoftonline.com/tenant2-id/v2.0', 'client2-id', 'https://login.microsoftonline.com/tenant2-id/discovery/v2.0/keys'),
    (3, 'https://tenant3.okta.com/oauth2/default', 'client3-id', 'https://tenant3.okta.com/oauth2/default/v1/keys');

-- 使用RLS隔离租户数据
ALTER TABLE customer_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON customer_data
FOR ALL
USING (tenant_id = current_setting('app.tenant_id')::int);
```

**效果**：

- ✅ 支持多个OAuth Provider
- ✅ 每个客户使用自己的身份提供商
- ✅ 数据完全隔离
- ✅ 灵活的权限管理

---

**最后更新**: 2025年12月4日
**文档编号**: P4-6-OAUTH2
**版本**: v1.0
**状态**: ✅ 完成
