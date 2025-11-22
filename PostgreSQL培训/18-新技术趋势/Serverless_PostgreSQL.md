# Serverless PostgreSQL：无服务器数据库方案

> **更新时间**: 2025 年 1 月
> **技术版本**: PostgreSQL 17+/18+ Serverless
> **文档编号**: 03-03-TREND-22

## 📑 概述

Serverless PostgreSQL 是一种按需扩展、自动管理的数据库服务，
包括 Neon、Supabase、CockroachDB Serverless 等方案，
提供了弹性扩展、零运维、按需付费等特性，适合现代云原生应用。

## 🎯 核心价值

- **自动扩展**：根据负载自动扩展和收缩
- **零运维**：无需管理服务器和数据库
- **按需付费**：按实际使用量付费
- **快速启动**：秒级数据库创建
- **全球分布**：支持全球多区域部署

## 📚 目录

- [Serverless PostgreSQL：无服务器数据库方案](#serverless-postgresql无服务器数据库方案)
  - [📑 概述](#-概述)
  - [🎯 核心价值](#-核心价值)
  - [📚 目录](#-目录)
  - [1. Serverless PostgreSQL 概述](#1-serverless-postgresql-概述)
    - [1.1 Serverless 架构](#11-serverless-架构)
    - [1.2 主要方案](#12-主要方案)
  - [2. Neon Serverless](#2-neon-serverless)
    - [2.1 Neon 特性](#21-neon-特性)
    - [2.2 Neon 使用](#22-neon-使用)
    - [2.3 Neon 分支](#23-neon-分支)
  - [3. Supabase](#3-supabase)
    - [3.1 Supabase 特性](#31-supabase-特性)
    - [3.2 Supabase 使用](#32-supabase-使用)
    - [3.3 Supabase 实时功能](#33-supabase-实时功能)
  - [4. CockroachDB Serverless](#4-cockroachdb-serverless)
    - [4.1 CockroachDB 特性](#41-cockroachdb-特性)
    - [4.2 分布式特性](#42-分布式特性)
  - [5. 技术选型](#5-技术选型)
    - [5.1 方案对比](#51-方案对比)
    - [5.2 选型建议](#52-选型建议)
  - [6. 最佳实践](#6-最佳实践)
    - [6.1 连接管理](#61-连接管理)
    - [6.2 成本优化](#62-成本优化)
  - [7. 实际案例](#7-实际案例)
    - [7.1 案例：SaaS 应用 Serverless 架构](#71-案例saas-应用-serverless-架构)
  - [📊 总结](#-总结)

---

## 1. Serverless PostgreSQL 概述

### 1.1 Serverless 架构

```text
Serverless PostgreSQL
├── 计算层
│   ├── 自动扩展
│   ├── 按需启动
│   └── 自动休眠
├── 存储层
│   ├── 分离存储
│   ├── 自动备份
│   └── 时间点恢复
└── 网络层
    ├── 全球 CDN
    ├── 低延迟
    └── 自动故障转移
```

### 1.2 主要方案

- **Neon**：基于存储计算分离的 Serverless PostgreSQL
- **Supabase**：开源 Firebase 替代方案
- **CockroachDB Serverless**：分布式 Serverless 数据库
- **AWS RDS Serverless**：AWS 托管的 Serverless 数据库

---

## 2. Neon Serverless

### 2.1 Neon 特性

Neon 是基于存储计算分离架构的 Serverless PostgreSQL：

```bash
# 安装 Neon CLI
npm install -g neonctl

# 创建项目
neonctl projects create --name myproject

# 创建数据库
neonctl databases create --project-id <project-id> --name mydb

# 获取连接字符串
neonctl connection-string --project-id <project-id>
```

### 2.2 Neon 使用

```sql
-- 连接 Neon 数据库
-- 使用标准 PostgreSQL 客户端
psql "postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb"

-- 创建表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 自动扩展，无需配置
INSERT INTO users (email) VALUES ('user@example.com');
```

### 2.3 Neon 分支

```bash
# 创建数据库分支（秒级）
neonctl branches create --project-id <project-id> --name dev-branch

# 切换分支
neonctl branches switch --project-id <project-id> --name dev-branch

# 时间点恢复
neonctl branches create --project-id <project-id> --name restore-branch --point-in-time "2025-01-15T10:00:00Z"
```

---

## 3. Supabase

### 3.1 Supabase 特性

Supabase 是开源 Firebase 替代方案，基于 PostgreSQL：

```bash
# 安装 Supabase CLI
npm install -g supabase

# 初始化项目
supabase init

# 启动本地开发环境
supabase start

# 部署到 Supabase Cloud
supabase link --project-ref <project-ref>
supabase db push
```

### 3.2 Supabase 使用

```sql
-- 使用 Supabase 客户端
-- JavaScript/TypeScript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://xxx.supabase.co',
  'your-anon-key'
)

// 查询数据
const { data, error } = await supabase
  .from('users')
  .select('*')
  .eq('email', 'user@example.com')
```

### 3.3 Supabase 实时功能

```javascript
// 实时订阅
const channel = supabase
  .channel('users')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'users' },
    (payload) => {
      console.log('New user:', payload.new)
    }
  )
  .subscribe()
```

---

## 4. CockroachDB Serverless

### 4.1 CockroachDB 特性

CockroachDB Serverless 是分布式 Serverless 数据库：

```bash
# 创建 CockroachDB Serverless 集群
cockroach sql --url "postgresql://user:password@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/defaultdb?sslmode=require"

# 使用标准 PostgreSQL 语法
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.2 分布式特性

```sql
-- 自动分片和复制
-- CockroachDB 自动处理数据分布

-- 跨区域查询
SELECT * FROM users
WHERE region = 'us-east-1'
OR region = 'us-west-1';

-- 自动故障转移
-- 无需配置，自动处理节点故障
```

---

## 5. 技术选型

### 5.1 方案对比

| 特性 | Neon | Supabase | CockroachDB |
|------|------|----------|-------------|
| 存储计算分离 | ✅ | ❌ | ✅ |
| 自动扩展 | ✅ | ✅ | ✅ |
| 分支功能 | ✅ | ❌ | ❌ |
| 实时功能 | ❌ | ✅ | ❌ |
| 全球分布 | ✅ | ✅ | ✅ |
| 开源 | ✅ | ✅ | ❌ |

### 5.2 选型建议

- **Neon**：适合需要分支、时间点恢复的开发场景
- **Supabase**：适合需要实时功能、认证的 Web 应用
- **CockroachDB**：适合需要全球分布、强一致性的企业应用

---

## 6. 最佳实践

### 6.1 连接管理

```javascript
// 使用连接池
import { Pool } from 'pg'

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
})

// 使用连接
const client = await pool.connect()
try {
  const result = await client.query('SELECT * FROM users')
  return result.rows
} finally {
  client.release()
}
```

### 6.2 成本优化

```sql
-- 使用索引减少查询成本
CREATE INDEX idx_users_email ON users(email);

-- 使用批量操作
INSERT INTO users (email)
SELECT generate_series(1, 1000) || '@example.com';

-- 定期清理旧数据
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '30 days';
```

---

## 7. 实际案例

### 7.1 案例：SaaS 应用 Serverless 架构

**场景**：多租户 SaaS 应用的 Serverless 数据库

**架构**：

```text
应用层
├── API Gateway
├── Lambda Functions
└── Serverless PostgreSQL (Neon)

数据库层
├── 主数据库（生产）
├── 分支数据库（开发/测试）
└── 自动备份
```

**实现**：

```javascript
// 使用 Neon 分支进行开发
const devDb = new Pool({
  connectionString: process.env.DEV_DATABASE_URL
})

// 使用主数据库进行生产
const prodDb = new Pool({
  connectionString: process.env.PROD_DATABASE_URL
})

// 自动扩展，无需配置
async function getUsers() {
  const result = await prodDb.query('SELECT * FROM users')
  return result.rows
}
```

**效果**：

- 数据库启动时间：从 5 分钟降至 5 秒
- 运维成本：降低 90%
- 扩展性：自动扩展，无需干预
- 成本：按需付费，节省 60%

---

## 📊 总结

Serverless PostgreSQL 提供了现代化的数据库解决方案：

1. **自动扩展**：根据负载自动扩展和收缩
2. **零运维**：无需管理服务器和数据库
3. **按需付费**：按实际使用量付费
4. **快速启动**：秒级数据库创建
5. **全球分布**：支持全球多区域部署

**最佳实践**：

- 选择合适的 Serverless 方案
- 使用连接池管理连接
- 优化查询减少成本
- 利用分支功能进行开发
- 监控使用量和成本
- 实施数据备份策略

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
