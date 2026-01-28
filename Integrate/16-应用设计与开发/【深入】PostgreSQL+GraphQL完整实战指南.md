---

> **📋 文档来源**: `PostgreSQL培训\06-应用开发\【深入】PostgreSQL+GraphQL完整实战指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 【深入】PostgreSQL + GraphQL完整实战指南

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 12+
> **难度等级**: ⭐⭐⭐⭐ 高级 | **预计学习时间**: 8-10小时

---

## 📋 目录

- [【深入】PostgreSQL + GraphQL完整实战指南](#深入postgresql--graphql完整实战指南)
  - [📋 目录](#-目录)
  - [1. 课程概述](#1-课程概述)
    - [1.1 什么是GraphQL？](#11-什么是graphql)
      - [核心特性](#核心特性)
      - [GraphQL vs REST](#graphql-vs-rest)
    - [1.2 PostgreSQL + GraphQL的优势](#12-postgresql--graphql的优势)
    - [1.3 三大主流方案](#13-三大主流方案)
  - [2. GraphQL基础](#2-graphql基础)
    - [2.1 核心概念](#21-核心概念)
      - [2.1.1 Schema定义语言（SDL）](#211-schema定义语言sdl)
      - [2.1.2 查询示例](#212-查询示例)
    - [2.2 GraphQL架构](#22-graphql架构)
  - [3. PostGraphile完整指南](#3-postgraphile完整指南)
    - [3.1 什么是PostGraphile？](#31-什么是postgraphile)
      - [3.1.1 核心优势](#311-核心优势)
    - [3.2 安装与配置](#32-安装与配置)
      - [3.2.1 快速开始](#321-快速开始)
      - [3.2.2 生产配置](#322-生产配置)
    - [3.3 数据库设计最佳实践](#33-数据库设计最佳实践)
      - [3.3.1 表设计](#331-表设计)
      - [自定义函数 → GraphQL Mutation](#自定义函数--graphql-mutation)
    - [3.4 权限控制（RLS）](#34-权限控制rls)
    - [3.5 实战查询示例](#35-实战查询示例)
  - [4. Hasura引擎](#4-hasura引擎)
    - [4.1 什么是Hasura？](#41-什么是hasura)
      - [4.1.1 核心特性](#411-核心特性)
    - [4.2 Docker部署](#42-docker部署)
    - [4.3 快速配置](#43-快速配置)
      - [通过Console配置](#通过console配置)
      - [通过Metadata配置](#通过metadata配置)
    - [4.4 实时订阅示例](#44-实时订阅示例)
    - [4.5 事件触发器](#45-事件触发器)
  - [5. Apollo + Prisma方案](#5-apollo--prisma方案)
    - [5.1 架构概览](#51-架构概览)
    - [5.2 Prisma Schema](#52-prisma-schema)
    - [5.3 Apollo Server设置](#53-apollo-server设置)
    - [5.4 DataLoader（N+1优化）](#54-dataloadern1优化)
  - [6. 权限控制与RLS](#6-权限控制与rls)
    - [6.1 JWT认证](#61-jwt认证)
      - [PostGraphile JWT](#postgraphile-jwt)
      - [Hasura JWT](#hasura-jwt)
    - [6.2 Row Level Security（RLS）](#62-row-level-securityrls)
  - [7. 实时订阅](#7-实时订阅)
    - [7.1 PostGraphile实时](#71-postgraphile实时)
    - [7.2 Hasura实时](#72-hasura实时)
  - [8. 性能优化](#8-性能优化)
    - [8.1 查询优化](#81-查询优化)
      - [N+1问题解决](#n1问题解决)
    - [8.2 连接池](#82-连接池)
    - [8.3 缓存策略](#83-缓存策略)
    - [8.4 查询复杂度限制](#84-查询复杂度限制)
  - [9. 生产实战案例](#9-生产实战案例)
    - [9.1 案例1：社交媒体平台](#91-案例1社交媒体平台)
      - [需求](#需求)
      - [架构选择](#架构选择)
      - [核心Schema](#核心schema)
      - [实时动态订阅](#实时动态订阅)
    - [9.2 案例2：实时协作工具](#92-案例2实时协作工具)
      - [9.2.1 需求](#921-需求)
      - [9.2.2 架构选择](#922-架构选择)
      - [Operational Transform实现](#operational-transform实现)
      - [❌ 避免的做法](#-避免的做法)
    - [10.2 安全最佳实践](#102-安全最佳实践)
    - [10.3 性能最佳实践](#103-性能最佳实践)
  - [11. 方案对比](#11-方案对比)
    - [11.1 综合对比](#111-综合对比)
    - [11.2 选择建议](#112-选择建议)
  - [12. FAQ与疑难解答](#12-faq与疑难解答)
    - [Q1: GraphQL会比REST慢吗？](#q1-graphql会比rest慢吗)
    - [Q2: 如何处理文件上传？](#q2-如何处理文件上传)
    - [Q3: 如何实现分页？](#q3-如何实现分页)
    - [Q4: GraphQL如何处理错误？](#q4-graphql如何处理错误)
    - [Q5: 如何监控GraphQL性能？](#q5-如何监控graphql性能)
  - [📚 延伸阅读](#-延伸阅读)
    - [官方资源](#官方资源)
    - [工具生态](#工具生态)
    - [推荐书籍](#推荐书籍)
  - [✅ 学习检查清单](#-学习检查清单)
  - [💡 下一步学习](#-下一步学习)

---

## 1. 课程概述

### 1.1 什么是GraphQL？

**GraphQL** 是Facebook开发的API查询语言，允许客户端精确指定需要的数据，解决REST API的过度获取和不足获取问题。

#### 核心特性

| 特性 | 说明 | 优势 |
| --- | --- | --- |
| **精确查询** | 只返回请求的字段 | 减少带宽，提升性能 |
| **单一端点** | 所有查询通过一个端点 | 简化API管理 |
| **强类型** | 完整的类型系统 | 自动生成文档、类型安全 |
| **实时订阅** | WebSocket推送 | 实时数据更新 |
| **嵌套查询** | 一次获取关联数据 | 减少请求次数 |

#### GraphQL vs REST

```text
REST API问题：
GET /users/1          → 返回用户全部字段（过度获取）
GET /users/1/posts    → 需要第二次请求（N+1问题）
GET /users/1/comments → 需要第三次请求

GraphQL解决方案：
query {
  user(id: 1) {
    name              # 只要name
    email             # 和email
    posts {           # 一次获取关联posts
      title
      comments {      # 和comments
        content
      }
    }
  }
}
# 一次请求，精确数据，无过度获取！
```

### 1.2 PostgreSQL + GraphQL的优势

```text
PostgreSQL → GraphQL的价值：

1. 自动生成API
   - 从数据库schema自动生成GraphQL API
   - 无需手写Resolver
   - 数据库变更自动同步到API

2. 利用PostgreSQL强大功能
   - RLS（行级安全）→ GraphQL权限
   - 函数/存储过程 → GraphQL Mutation
   - 视图 → GraphQL查询
   - Trigger → 实时订阅

3. 高性能
   - SQL优化器自动优化查询
   - 批量查询合并（DataLoader）
   - 连接池管理

4. 类型安全
   - PostgreSQL类型 → GraphQL类型
   - 自动验证
   - IDE自动补全
```

### 1.3 三大主流方案

| 方案 | 特点 | 适用场景 |
| --- | --- | --- |
| **PostGraphile** | 自动生成，PostgreSQL优先 | 快速原型、PostgreSQL重度使用 |
| **Hasura** | 实时订阅，云原生 | 实时应用、微服务 |
| **Apollo + Prisma** | 灵活定制，TypeScript优先 | 复杂业务逻辑、现代前端 |

---

## 2. GraphQL基础

### 2.1 核心概念

#### 2.1.1 Schema定义语言（SDL）

```graphql
# 类型定义
type User {
  id: ID!           # ! 表示非空
  name: String!
  email: String!
  posts: [Post!]!   # 数组类型
  createdAt: DateTime
}

type Post {
  id: ID!
  title: String!
  content: String
  author: User!     # 关联类型
  comments: [Comment!]!
}

# 查询入口
type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
  post(id: ID!): Post
}

# 修改入口
type Mutation {
  createUser(name: String!, email: String!): User!
  updatePost(id: ID!, title: String): Post
  deleteComment(id: ID!): Boolean
}

# 订阅入口
type Subscription {
  userCreated: User!
  postUpdated(userId: ID!): Post!
}
```

#### 2.1.2 查询示例

```graphql
# 基础查询
query {
  user(id: "1") {
    name
    email
  }
}

# 嵌套查询
query {
  user(id: "1") {
    name
    posts {
      title
      comments {
        content
        author {
          name
        }
      }
    }
  }
}

# 查询参数
query GetUsers($limit: Int!, $offset: Int!) {
  users(limit: $limit, offset: $offset) {
    id
    name
  }
}

# 变更操作
mutation CreateUser($name: String!, $email: String!) {
  createUser(name: $name, email: $email) {
    id
    name
    email
  }
}

# 订阅
subscription {
  userCreated {
    id
    name
    email
  }
}
```

### 2.2 GraphQL架构

```text
┌─────────────────────────────────────────┐
│         Client (React/Vue/Mobile)       │
│  Apollo Client / urql / Relay           │
└──────────────────┬──────────────────────┘
                   │ HTTP/WebSocket
┌──────────────────▼──────────────────────┐
│         GraphQL Server                  │
├─────────────────────────────────────────┤
│  ┌──────────────────────────────────┐  │
│  │  Schema (SDL)                    │  │
│  │  - Type Definitions              │  │
│  │  - Query/Mutation/Subscription   │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  Resolvers                       │  │
│  │  - 查询逻辑                       │  │
│  │  - 数据获取                       │  │
│  │  - 权限验证                       │  │
│  └──────────────────────────────────┘  │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         PostgreSQL Database             │
│  Tables / Views / Functions             │
└─────────────────────────────────────────┘
```

---

## 3. PostGraphile完整指南

### 3.1 什么是PostGraphile？

**PostGraphile**（原PostGraphQL）自动将PostgreSQL数据库转换为GraphQL API。

#### 3.1.1 核心优势

```text
✅ 零配置自动生成
   - 表 → GraphQL类型
   - 外键 → 关联查询
   - 函数 → Mutation
   - 视图 → Query

✅ PostgreSQL优先
   - RLS → 权限控制
   - 函数 → 自定义逻辑
   - Trigger → 业务规则
   - 性能优化靠SQL

✅ 高性能
   - 查询优化（单次SQL）
   - DataLoader自动批处理
   - 连接池管理
```

### 3.2 安装与配置

#### 3.2.1 快速开始

```bash
# 安装
npm install -g postgraphile

# 启动（最简单）
postgraphile -c "postgres://user:pass@localhost/mydb" -s public

# 访问GraphiQL
# http://localhost:5000/graphiql
```

#### 3.2.2 生产配置

```javascript
// server.js（带完整错误处理）
const { postgraphile } = require('postgraphile');
const express = require('express');

const app = express();

// 环境变量配置
const DB_URL = process.env.DATABASE_URL || 'postgres://user:pass@localhost/mydb';
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const PORT = parseInt(process.env.PORT || '5000', 10);

// 验证必需的环境变量
if (!process.env.DATABASE_URL && !DB_URL) {
  console.error('Error: DATABASE_URL environment variable is required');
  process.exit(1);
}

if (!process.env.JWT_SECRET && JWT_SECRET === 'your-secret-key') {
  console.warn('Warning: Using default JWT secret. Set JWT_SECRET environment variable for production.');
}

try {
  // 加载PostGraphile插件（带错误处理）
  let plugins = [];
  try {
    plugins.push(require('@graphile-contrib/pg-simplify-inflector'));
  } catch (error) {
    console.warn('Warning: @graphile-contrib/pg-simplify-inflector not found, skipping');
  }

  try {
    plugins.push(require('postgraphile-plugin-connection-filter'));
  } catch (error) {
    console.warn('Warning: postgraphile-plugin-connection-filter not found, skipping');
  }

  app.use(
    postgraphile(DB_URL, 'public', {
      // 开发配置
      watchPg: process.env.NODE_ENV !== 'production',  // 生产环境不监听
      graphiql: process.env.NODE_ENV !== 'production', // 生产环境禁用GraphiQL
      enhanceGraphiql: process.env.NODE_ENV !== 'production',

      // 性能配置
      retryOnInitFail: true,
      dynamicJson: true,
      setofFunctionsContainNulls: false,
      ignoreRBAC: false,

      // 订阅配置
      subscriptions: true,
      simpleSubscriptions: true,

      // JWT认证
      jwtSecret: JWT_SECRET,
      jwtPgTypeIdentifier: 'public.jwt_token',

      // 高级配置
      appendPlugins: plugins.length > 0 ? plugins : undefined,

      // CORS
      enableCors: true,

      // 日志
      showErrorStack: process.env.NODE_ENV === 'development',
      extendedErrors: ['hint', 'detail', 'errcode'],

      // 错误处理
      handleErrors: (errors, req, res) => {
        console.error('GraphQL errors:', errors);
        // 生产环境隐藏详细错误
        if (process.env.NODE_ENV === 'production') {
          return errors.map(error => ({
            message: 'An error occurred',
            locations: error.locations,
            path: error.path
          }));
        }
        return errors;
      }
    })
  );

  // 全局错误处理中间件
  app.use((err, req, res, next) => {
    console.error('Express error:', err);
    res.status(500).json({
      error: process.env.NODE_ENV === 'production'
        ? 'Internal server error'
        : err.message
    });
  });

  // 启动服务器（带错误处理）
  app.listen(PORT, () => {
    console.log(`PostGraphile server running on http://localhost:${PORT}/graphql`);
    console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  }).on('error', (error) => {
    if (error.code === 'EADDRINUSE') {
      console.error(`Error: Port ${PORT} is already in use`);
      process.exit(1);
    } else {
      console.error('Server error:', error);
      process.exit(1);
    }
  });
} catch (error) {
  console.error('Failed to start server:', error);
  process.exit(1);
}

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing server...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, closing server...');
  process.exit(0);
});
```

### 3.3 数据库设计最佳实践

#### 3.3.1 表设计

```sql
-- 1. 用户表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        DROP TABLE users CASCADE;
        RAISE NOTICE '已删除现有表: users';
    END IF;

    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    RAISE NOTICE '用户表创建成功: users';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表 users 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建用户表失败: %', SQLERRM;
END $$;

-- 2. 帖子表（外键自动生成关联，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
        DROP TABLE posts CASCADE;
        RAISE NOTICE '已删除现有表: posts';
    END IF;

    -- 检查users表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION 'users表不存在，无法创建外键约束';
    END IF;

    CREATE TABLE posts (
        id SERIAL PRIMARY KEY,
        author_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        content TEXT,
        published BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    RAISE NOTICE '帖子表创建成功: posts';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'users表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '表 posts 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建帖子表失败: %', SQLERRM;
END $$;

-- 3. 评论表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'comments') THEN
        DROP TABLE comments CASCADE;
        RAISE NOTICE '已删除现有表: comments';
    END IF;

    -- 检查posts表和users表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
        RAISE EXCEPTION 'posts表不存在，无法创建外键约束';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION 'users表不存在，无法创建外键约束';
    END IF;

    CREATE TABLE comments (
        id SERIAL PRIMARY KEY,
        post_id INT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
        author_id INT NOT NULL REFERENCES users(id),
        content TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    RAISE NOTICE '评论表创建成功: comments';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表或users表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '表 comments 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建评论表失败: %', SQLERRM;
END $$;

-- 4. 添加注释（自动生成GraphQL文档，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        COMMENT ON TABLE users IS 'Platform users';
        COMMENT ON COLUMN users.username IS 'Unique username';
        RAISE NOTICE 'users表注释已添加';
    ELSE
        RAISE WARNING 'users表不存在，跳过注释';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
        COMMENT ON TABLE posts IS 'User posts';
        RAISE NOTICE 'posts表注释已添加';
    ELSE
        RAISE WARNING 'posts表不存在，跳过注释';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '表不存在，跳过注释';
    WHEN OTHERS THEN
        RAISE WARNING '添加注释失败: %', SQLERRM;
END $$;
```

**生成的GraphQL Schema**:

```graphql
type User {
  id: Int!
  username: String!
  email: String!
  createdAt: Datetime!
  updatedAt: Datetime!

  # 自动生成的关联
  postsByAuthorId: [Post!]!
  commentsByAuthorId: [Comment!]!
}

type Post {
  id: Int!
  authorId: Int!
  title: String!
  content: String
  published: Boolean
  createdAt: Datetime!

  # 自动生成的关联
  userByAuthorId: User!
  commentsByPostId: [Comment!]!
}
```

#### 自定义函数 → GraphQL Mutation

```sql
-- 创建帖子函数（带错误处理）
CREATE OR REPLACE FUNCTION create_post(
  title TEXT,
  content TEXT
) RETURNS posts AS $$
DECLARE
  user_id INT;
  new_post posts;
BEGIN
  -- 参数验证
  IF title IS NULL OR length(trim(title)) = 0 THEN
    RAISE EXCEPTION 'title不能为空';
  END IF;

  -- 获取当前用户ID（假设有current_user_id函数）
  BEGIN
    user_id := current_user_id();
  EXCEPTION
    WHEN undefined_function THEN
      RAISE EXCEPTION 'current_user_id函数不存在';
    WHEN OTHERS THEN
      RAISE EXCEPTION '获取用户ID失败: %', SQLERRM;
  END;

  IF user_id IS NULL THEN
    RAISE EXCEPTION '用户未登录';
  END IF;

  -- 检查users表是否存在
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
    RAISE EXCEPTION 'posts表不存在';
  END IF;

  -- 插入数据
  BEGIN
    INSERT INTO posts (author_id, title, content)
    VALUES (user_id, title, content)
    RETURNING * INTO new_post;

    RETURN new_post;
  EXCEPTION
    WHEN foreign_key_violation THEN
      RAISE EXCEPTION '用户不存在: %', user_id;
    WHEN not_null_violation THEN
      RAISE EXCEPTION '必填字段不能为空';
    WHEN OTHERS THEN
      RAISE EXCEPTION '创建帖子失败: %', SQLERRM;
  END;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT SECURITY DEFINER;

-- 搜索函数（带错误处理）
CREATE OR REPLACE FUNCTION search_posts(search_term TEXT)
RETURNS SETOF posts AS $$
BEGIN
  -- 参数验证
  IF search_term IS NULL OR length(trim(search_term)) = 0 THEN
    RAISE EXCEPTION '搜索词不能为空';
  END IF;

  -- 检查表是否存在
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
    RAISE EXCEPTION 'posts表不存在';
  END IF;

  -- 执行搜索
  RETURN QUERY
  SELECT * FROM posts
  WHERE title ILIKE '%' || search_term || '%'
     OR content ILIKE '%' || search_term || '%'
  ORDER BY created_at DESC;
EXCEPTION
  WHEN undefined_table THEN
    RAISE EXCEPTION 'posts表不存在';
  WHEN OTHERS THEN
    RAISE EXCEPTION '搜索帖子失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql STABLE;
```

**生成的GraphQL**:

```graphql
type Mutation {
  createPost(title: String!, content: String!): Post
}

type Query {
  searchPosts(searchTerm: String!): [Post!]
}
```

### 3.4 权限控制（RLS）

```sql
-- 启用RLS（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
        RAISE EXCEPTION 'posts表不存在，无法启用RLS';
    END IF;

    ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
    RAISE NOTICE 'RLS已启用: posts';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '启用RLS失败: %', SQLERRM;
END $$;

-- 策略：用户只能查看已发布的帖子或自己的帖子（带错误处理）
DO $$
BEGIN
    -- 删除现有策略（如果存在）
    IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'posts' AND policyname = 'posts_select') THEN
        DROP POLICY posts_select ON posts;
        RAISE NOTICE '已删除现有策略: posts_select';
    END IF;

    CREATE POLICY posts_select ON posts
        FOR SELECT
        USING (
            published = TRUE
            OR author_id = current_user_id()
        );

    RAISE NOTICE '策略创建成功: posts_select';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建SELECT策略失败: %', SQLERRM;
END $$;

-- 策略：用户只能修改自己的帖子（带错误处理）
DO $$
BEGIN
    -- 删除现有策略（如果存在）
    IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'posts' AND policyname = 'posts_update') THEN
        DROP POLICY posts_update ON posts;
        RAISE NOTICE '已删除现有策略: posts_update';
    END IF;

    CREATE POLICY posts_update ON posts
        FOR UPDATE
        USING (author_id = current_user_id())
        WITH CHECK (author_id = current_user_id());

    RAISE NOTICE '策略创建成功: posts_update';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建UPDATE策略失败: %', SQLERRM;
END $$;

-- 策略：用户只能删除自己的帖子（带错误处理）
DO $$
BEGIN
    -- 删除现有策略（如果存在）
    IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'posts' AND policyname = 'posts_delete') THEN
        DROP POLICY posts_delete ON posts;
        RAISE NOTICE '已删除现有策略: posts_delete';
    END IF;

    CREATE POLICY posts_delete ON posts
        FOR DELETE
        USING (author_id = current_user_id());

    RAISE NOTICE '策略创建成功: posts_delete';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建DELETE策略失败: %', SQLERRM;
END $$;
```

**效果**：GraphQL查询自动应用RLS规则，无需在Resolver中编码权限逻辑！

### 3.5 实战查询示例

```graphql
# 1. 获取用户及其帖子
query {
  user(id: 1) {
    username
    email
    posts {
      nodes {
        title
        createdAt
        comments {
          totalCount
        }
      }
    }
  }
}

# 2. 分页查询
query {
  allPosts(
    first: 10
    offset: 0
    orderBy: CREATED_AT_DESC
    condition: { published: true }
  ) {
    nodes {
      id
      title
      author {
        username
      }
    }
    totalCount
    pageInfo {
      hasNextPage
      hasPreviousPage
    }
  }
}

# 3. 过滤查询（需要插件）
query {
  allPosts(
    filter: {
      title: { includesInsensitive: "graphql" }
      published: { equalTo: true }
      createdAt: { greaterThan: "2025-01-01" }
    }
  ) {
    nodes {
      title
      content
    }
  }
}

# 4. 聚合查询（需要插件）
query {
  allUsers {
    nodes {
      username
      postsConnection {
        totalCount
        aggregates {
          average {
            id
          }
        }
      }
    }
  }
}

# 5. 调用自定义函数
mutation {
  createPost(input: {
    title: "My First Post"
    content: "Hello GraphQL!"
  }) {
    post {
      id
      title
      createdAt
    }
  }
}

# 6. 搜索
query {
  searchPosts(searchTerm: "graphql") {
    nodes {
      id
      title
      content
    }
  }
}
```

---

## 4. Hasura引擎

### 4.1 什么是Hasura？

**Hasura** 是开源的实时GraphQL引擎，即时为PostgreSQL生成GraphQL API。

#### 4.1.1 核心特性

```text
✅ 即时GraphQL API
   - 可视化界面配置
   - 自动跟踪表变化
   - 无需编码

✅ 实时订阅
   - 基于事件的订阅
   - WebSocket推送
   - 毫秒级延迟

✅ 远程Schema
   - 合并多个GraphQL源
   - 微服务整合
   - REST API包装

✅ 事件触发器
   - 数据变化 → Webhook
   - 异步处理
   - 集成外部服务
```

### 4.2 Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: hasura-postgres
    restart: always
    environment:
      POSTGRES_PASSWORD: postgrespassword
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  hasura:
    image: hasura/graphql-engine:latest
    container_name: hasura-engine
    ports:
      - "8080:8080"
    depends_on:
      - postgres
    restart: always
    environment:
      ## Postgres连接
      HASURA_GRAPHQL_DATABASE_URL: postgres://postgres:postgrespassword@postgres:5432/postgres

      ## 启用Console
      HASURA_GRAPHQL_ENABLE_CONSOLE: "true"

      ## Admin Secret
      HASURA_GRAPHQL_ADMIN_SECRET: myadminsecretkey

      ## JWT Secret
      HASURA_GRAPHQL_JWT_SECRET: '{"type":"HS256","key":"your-256-bit-secret-key-min-32-chars"}'

      ## 未授权角色（公开访问）
      HASURA_GRAPHQL_UNAUTHORIZED_ROLE: anonymous

      ## 启用开发模式
      HASURA_GRAPHQL_DEV_MODE: "true"

      ## 启用远程Schema
      HASURA_GRAPHQL_ENABLE_REMOTE_SCHEMA_PERMISSIONS: "true"

volumes:
  db_data:
```

```bash
# 启动
docker-compose up -d

# 访问Console
# http://localhost:8080/console
```

### 4.3 快速配置

#### 通过Console配置

1. **跟踪表**
   - Data → Public → Track All Tables
   - 自动生成GraphQL CRUD操作

2. **配置关系**

   ```text
   users (1) → (N) posts
   - 自动检测外键
   - 生成嵌套查询
   ```

3. **设置权限**

   ```json
   {
     "role": "user",
     "table": "posts",
     "permission": {
       "filter": {
         "author_id": {
           "_eq": "X-Hasura-User-Id"
         }
       },
       "columns": ["id", "title", "content"]
     }
   }
   ```

#### 通过Metadata配置

```yaml
# metadata/tables.yaml
- table:
    schema: public
    name: posts

  # 关系配置
  object_relationships:
    - name: author
      using:
        foreign_key_constraint_on: author_id

  array_relationships:
    - name: comments
      using:
        foreign_key_constraint_on:
          column: post_id
          table:
            schema: public
            name: comments

  # 查询权限
  select_permissions:
    - role: user
      permission:
        columns:
          - id
          - title
          - content
          - created_at
        filter:
          _or:
            - published: { _eq: true }
            - author_id: { _eq: X-Hasura-User-Id }

  # 插入权限
  insert_permissions:
    - role: user
      permission:
        check:
          author_id: { _eq: X-Hasura-User-Id }
        columns:
          - title
          - content

  # 更新权限
  update_permissions:
    - role: user
      permission:
        columns:
          - title
          - content
        filter:
          author_id: { _eq: X-Hasura-User-Id }
        check:
          author_id: { _eq: X-Hasura-User-Id }

  # 删除权限
  delete_permissions:
    - role: user
      permission:
        filter:
          author_id: { _eq: X-Hasura-User-Id }
```

### 4.4 实时订阅示例

```graphql
# 订阅新帖子
subscription {
  posts(
    order_by: { created_at: desc }
    limit: 10
  ) {
    id
    title
    author {
      username
    }
    created_at
  }
}

# 订阅特定用户的帖子更新
subscription ($userId: Int!) {
  posts(
    where: { author_id: { _eq: $userId } }
    order_by: { updated_at: desc }
  ) {
    id
    title
    content
    updated_at
  }
}

# 聚合订阅
subscription {
  posts_aggregate {
    aggregate {
      count
      avg {
        id
      }
    }
  }
}
```

**前端集成（React + Apollo）**:

```javascript
import { useSubscription, gql } from '@apollo/client';

const NEW_POSTS_SUBSCRIPTION = gql`
  subscription {
    posts(order_by: { created_at: desc }, limit: 10) {
      id
      title
      author {
        username
      }
      created_at
    }
  }
`;

function LatestPosts() {
  const { data, loading } = useSubscription(NEW_POSTS_SUBSCRIPTION);

  if (loading) return <p>Loading...</p>;

  return (
    <ul>
      {data.posts.map(post => (
        <li key={post.id}>
          {post.title} by {post.author.username}
        </li>
      ))}
    </ul>
  );
}
```

### 4.5 事件触发器

```yaml
# 配置事件触发器（数据变化 → Webhook）
- table:
    schema: public
    name: orders
  event_triggers:
    - name: order_created
      definition:
        enable_manual: true
        insert:
          columns: '*'
      webhook: https://myapi.com/webhooks/order-created
      headers:
        - name: X-API-Key
          value: my-secret-key
```

**Webhook处理**:

```javascript
// webhooks/order-created.js（带完整错误处理）
app.post('/webhooks/order-created', async (req, res) => {
  try {
    // 参数验证
    if (!req.body || !req.body.event || !req.body.event.data) {
      return res.status(400).json({
        error: 'Invalid webhook payload',
        success: false
      });
    }

    const { event, table, trigger } = req.body;
    const newOrder = event.data.new;

    if (!newOrder || !newOrder.id) {
      return res.status(400).json({
        error: 'Invalid order data',
        success: false
      });
    }

    // 发送邮件通知（带错误处理）
    try {
      if (newOrder.customer_email) {
        await sendEmail({
          to: newOrder.customer_email,
          subject: 'Order Confirmed',
          body: `Your order #${newOrder.id} has been confirmed!`
        });
        console.log(`Email sent to ${newOrder.customer_email} for order #${newOrder.id}`);
      } else {
        console.warn(`No customer email for order #${newOrder.id}`);
      }
    } catch (emailError) {
      // 邮件发送失败不影响整体流程，记录日志
      console.error('Failed to send email:', emailError);
      // 可以选择记录到错误追踪系统
    }

    // 调用库存服务（带错误处理）
    try {
      if (newOrder.items && Array.isArray(newOrder.items) && newOrder.items.length > 0) {
        await inventoryService.reserve(newOrder.items);
        console.log(`Inventory reserved for order #${newOrder.id}`);
      } else {
        console.warn(`No items found for order #${newOrder.id}`);
      }
    } catch (inventoryError) {
      // 库存服务失败需要回滚，但这里只是通知，返回错误
      console.error('Failed to reserve inventory:', inventoryError);
      return res.status(500).json({
        error: 'Failed to reserve inventory',
        details: inventoryError.message,
        success: false
      });
    }

    // 返回200确认处理
    res.status(200).json({
      success: true,
      orderId: newOrder.id
    });
  } catch (error) {
    // 全局错误处理
    console.error('Webhook processing error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message,
      success: false
    });
  }
});
```

---

## 5. Apollo + Prisma方案

### 5.1 架构概览

```text
┌─────────────────────────────────────┐
│     Apollo Server (GraphQL)         │
│  - Schema定义                        │
│  - Resolver实现                      │
│  - 中间件/插件                        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Prisma ORM                      │
│  - 类型安全的数据库访问               │
│  - 迁移管理                          │
│  - 查询优化                          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     PostgreSQL Database             │
└─────────────────────────────────────┘
```

### 5.2 Prisma Schema

```prisma
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        Int       @id @default(autoincrement())
  username  String    @unique
  email     String    @unique
  posts     Post[]
  comments  Comment[]
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt
}

model Post {
  id        Int       @id @default(autoincrement())
  title     String
  content   String?
  published Boolean   @default(false)
  author    User      @relation(fields: [authorId], references: [id])
  authorId  Int
  comments  Comment[]
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt
}

model Comment {
  id        Int      @id @default(autoincrement())
  content   String
  post      Post     @relation(fields: [postId], references: [id])
  postId    Int
  author    User     @relation(fields: [authorId], references: [id])
  authorId  Int
  createdAt DateTime @default(now())
}
```

### 5.3 Apollo Server设置

```typescript
// server.ts
import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GraphQL Schema
const typeDefs = `#graphql
  type User {
    id: ID!
    username: String!
    email: String!
    posts: [Post!]!
    comments: [Comment!]!
    createdAt: String!
  }

  type Post {
    id: ID!
    title: String!
    content: String
    published: Boolean!
    author: User!
    comments: [Comment!]!
    createdAt: String!
  }

  type Comment {
    id: ID!
    content: String!
    post: Post!
    author: User!
    createdAt: String!
  }

  type Query {
    users: [User!]!
    user(id: ID!): User
    posts(published: Boolean): [Post!]!
    post(id: ID!): Post
  }

  type Mutation {
    createUser(username: String!, email: String!): User!
    createPost(title: String!, content: String, authorId: ID!): Post!
    publishPost(id: ID!): Post
    deletePost(id: ID!): Boolean
  }
`;

// Resolvers（带完整错误处理）
const resolvers = {
  Query: {
    users: async () => {
      try {
        return await prisma.user.findMany();
      } catch (error: any) {
        console.error('Failed to fetch users:', error);
        throw new Error(`Failed to fetch users: ${error.message}`);
      }
    },

    user: async (_: any, { id }: { id: string }) => {
      try {
        if (!id) {
          throw new Error('User ID is required');
        }

        const userId = Number(id);
        if (isNaN(userId)) {
          throw new Error('Invalid user ID format');
        }

        const user = await prisma.user.findUnique({ where: { id: userId } });

        if (!user) {
          throw new Error(`User with ID ${id} not found`);
        }

        return user;
      } catch (error: any) {
        console.error(`Failed to fetch user ${id}:`, error);
        throw error;
      }
    },

    posts: async (_: any, { published }: { published?: boolean }) => {
      try {
        return await prisma.post.findMany({
          where: published !== undefined ? { published } : undefined,
          orderBy: { createdAt: 'desc' }
        });
      } catch (error: any) {
        console.error('Failed to fetch posts:', error);
        throw new Error(`Failed to fetch posts: ${error.message}`);
      }
    },

    post: async (_: any, { id }: { id: string }) => {
      try {
        if (!id) {
          throw new Error('Post ID is required');
        }

        const postId = Number(id);
        if (isNaN(postId)) {
          throw new Error('Invalid post ID format');
        }

        const post = await prisma.post.findUnique({ where: { id: postId } });

        if (!post) {
          throw new Error(`Post with ID ${id} not found`);
        }

        return post;
      } catch (error: any) {
        console.error(`Failed to fetch post ${id}:`, error);
        throw error;
      }
    }
  },

  Mutation: {
    createUser: async (_: any, { username, email }: { username: string; email: string }) => {
      try {
        // 参数验证
        if (!username || typeof username !== 'string' || username.trim().length === 0) {
          throw new Error('Username is required and must be a non-empty string');
        }

        if (!email || typeof email !== 'string' || !email.includes('@')) {
          throw new Error('Valid email is required');
        }

        return await prisma.user.create({
          data: { username: username.trim(), email: email.trim() }
        });
      } catch (error: any) {
        console.error('Failed to create user:', error);

        // 处理Prisma唯一约束错误
        if (error.code === 'P2002') {
          throw new Error(`User with ${error.meta?.target?.join(', ') || 'this data'} already exists`);
        }

        throw error;
      }
    },

    createPost: async (_: any, args: { title: string; content?: string; authorId: string }) => {
      try {
        // 参数验证
        if (!args.title || typeof args.title !== 'string' || args.title.trim().length === 0) {
          throw new Error('Title is required and must be a non-empty string');
        }

        if (!args.authorId) {
          throw new Error('Author ID is required');
        }

        const authorId = Number(args.authorId);
        if (isNaN(authorId)) {
          throw new Error('Invalid author ID format');
        }

        // 检查作者是否存在
        const author = await prisma.user.findUnique({ where: { id: authorId } });
        if (!author) {
          throw new Error(`Author with ID ${args.authorId} not found`);
        }

        return await prisma.post.create({
          data: {
            title: args.title.trim(),
            content: args.content?.trim() || null,
            authorId: authorId
          }
        });
      } catch (error: any) {
        console.error('Failed to create post:', error);

        // 处理Prisma外键约束错误
        if (error.code === 'P2003') {
          throw new Error('Invalid author ID: author does not exist');
        }

        throw error;
      }
    },

    publishPost: async (_: any, { id }: { id: string }) => {
      try {
        if (!id) {
          throw new Error('Post ID is required');
        }

        const postId = Number(id);
        if (isNaN(postId)) {
          throw new Error('Invalid post ID format');
        }

        const post = await prisma.post.update({
          where: { id: postId },
          data: { published: true }
        });

        return post;
      } catch (error: any) {
        console.error(`Failed to publish post ${id}:`, error);

        // 处理Prisma记录不存在错误
        if (error.code === 'P2025') {
          throw new Error(`Post with ID ${id} not found`);
        }

        throw error;
      }
    },

    deletePost: async (_: any, { id }: { id: string }) => {
      try {
        if (!id) {
          throw new Error('Post ID is required');
        }

        const postId = Number(id);
        if (isNaN(postId)) {
          throw new Error('Invalid post ID format');
        }

        await prisma.post.delete({ where: { id: postId } });
        return true;
      } catch (error: any) {
        console.error(`Failed to delete post ${id}:`, error);

        // 处理Prisma记录不存在错误
        if (error.code === 'P2025') {
          throw new Error(`Post with ID ${id} not found`);
        }

        throw error;
      }
    }
  },

  // 关联字段解析（带错误处理）
  User: {
    posts: async (parent: any) => {
      try {
        if (!parent || !parent.id) {
          throw new Error('Invalid parent user object');
        }
        return await prisma.post.findMany({ where: { authorId: parent.id } });
      } catch (error: any) {
        console.error(`Failed to fetch posts for user ${parent?.id}:`, error);
        throw new Error(`Failed to fetch posts: ${error.message}`);
      }
    },

    comments: async (parent: any) => {
      try {
        if (!parent || !parent.id) {
          throw new Error('Invalid parent user object');
        }
        return await prisma.comment.findMany({ where: { authorId: parent.id } });
      } catch (error: any) {
        console.error(`Failed to fetch comments for user ${parent?.id}:`, error);
        throw new Error(`Failed to fetch comments: ${error.message}`);
      }
    }
  },

  Post: {
    author: async (parent: any) => {
      try {
        if (!parent || !parent.authorId) {
          throw new Error('Invalid parent post object or missing authorId');
        }
        const author = await prisma.user.findUnique({ where: { id: parent.authorId } });
        if (!author) {
          throw new Error(`Author with ID ${parent.authorId} not found`);
        }
        return author;
      } catch (error: any) {
        console.error(`Failed to fetch author for post ${parent?.id}:`, error);
        throw error;
      }
    },

    comments: async (parent: any) => {
      try {
        if (!parent || !parent.id) {
          throw new Error('Invalid parent post object');
        }
        return await prisma.comment.findMany({ where: { postId: parent.id } });
      } catch (error: any) {
        console.error(`Failed to fetch comments for post ${parent?.id}:`, error);
        throw new Error(`Failed to fetch comments: ${error.message}`);
      }
    }
  },

  Comment: {
    post: async (parent: any) => {
      try {
        if (!parent || !parent.postId) {
          throw new Error('Invalid parent comment object or missing postId');
        }
        const post = await prisma.post.findUnique({ where: { id: parent.postId } });
        if (!post) {
          throw new Error(`Post with ID ${parent.postId} not found`);
        }
        return post;
      } catch (error: any) {
        console.error(`Failed to fetch post for comment ${parent?.id}:`, error);
        throw error;
      }
    },

    author: async (parent: any) => {
      try {
        if (!parent || !parent.authorId) {
          throw new Error('Invalid parent comment object or missing authorId');
        }
        const author = await prisma.user.findUnique({ where: { id: parent.authorId } });
        if (!author) {
          throw new Error(`Author with ID ${parent.authorId} not found`);
        }
        return author;
      } catch (error: any) {
        console.error(`Failed to fetch author for comment ${parent?.id}:`, error);
        throw error;
      }
    }
  }
};

// 启动服务器（带完整错误处理）
async function startServer() {
  try {
    const server = new ApolloServer({
      typeDefs,
      resolvers,
      // 全局错误处理
      formatError: (error) => {
        console.error('GraphQL Error:', error);
        // 生产环境隐藏内部错误
        if (process.env.NODE_ENV === 'production') {
          return {
            message: 'An error occurred',
            extensions: {
              code: error.extensions?.code || 'INTERNAL_ERROR'
            }
          };
        }
        return error;
      }
    });

    // 验证Prisma连接
    try {
      await prisma.$connect();
      console.log('✅ Prisma connected to database');
    } catch (error) {
      console.error('❌ Failed to connect to database:', error);
      throw new Error('Database connection failed');
    }

    const { url } = await startStandaloneServer(server, {
      listen: { port: parseInt(process.env.PORT || '4000', 10) },
      context: async ({ req }) => {
        try {
          const user = await getUserFromToken(req.headers.authorization);
          return {
            prisma,
            user
          };
        } catch (error) {
          console.error('Error getting user from token:', error);
          // 返回null而不是抛出错误，允许匿名访问
          return {
            prisma,
            user: null
          };
        }
      }
    });

    console.log(`🚀 Server ready at ${url}`);
    console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

// 优雅关闭
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing server...');
  try {
    await prisma.$disconnect();
    console.log('Prisma disconnected');
  } catch (error) {
    console.error('Error disconnecting Prisma:', error);
  }
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, closing server...');
  try {
    await prisma.$disconnect();
    console.log('Prisma disconnected');
  } catch (error) {
    console.error('Error disconnecting Prisma:', error);
  }
  process.exit(0);
});

// 启动服务器
startServer();
```

### 5.4 DataLoader（N+1优化）

```typescript
import DataLoader from 'dataloader';

// 创建User DataLoader（带完整错误处理）
const createUserLoader = () =>
  new DataLoader(async (userIds: readonly number[]) => {
    try {
      // 参数验证
      if (!userIds || userIds.length === 0) {
        return [];
      }

      // 过滤无效的ID
      const validIds = userIds.filter(id => id != null && typeof id === 'number' && id > 0);
      if (validIds.length === 0) {
        return userIds.map(() => null);
      }

      // 去重
      const uniqueIds = [...new Set(validIds)];

      const users = await prisma.user.findMany({
        where: { id: { in: uniqueIds } }
      });

      // 创建ID到用户的映射
      const userMap = new Map(users.map(user => [user.id, user]));

      // 按请求顺序返回（包括null表示未找到）
      return userIds.map(id => {
        if (id == null || typeof id !== 'number' || id <= 0) {
          return null;
        }
        return userMap.get(id) || null;
      });
    } catch (error) {
      console.error('DataLoader error in createUserLoader:', error);
      // 返回null数组，而不是抛出错误
      return userIds.map(() => null);
    }
  }, {
    // 配置选项
    batch: true,  // 启用批处理
    cache: true,  // 启用缓存
    maxBatchSize: 100  // 限制批次大小
  });

// 创建PostsByAuthor DataLoader（带完整错误处理）
const createPostsByAuthorLoader = () =>
  new DataLoader(async (authorIds: readonly number[]) => {
    try {
      // 参数验证
      if (!authorIds || authorIds.length === 0) {
        return [];
      }

      // 过滤无效的ID
      const validIds = authorIds.filter(id => id != null && typeof id === 'number' && id > 0);
      if (validIds.length === 0) {
        return authorIds.map(() => []);
      }

      // 去重
      const uniqueIds = [...new Set(validIds)];

      const posts = await prisma.post.findMany({
        where: { authorId: { in: uniqueIds } },
        orderBy: { createdAt: 'desc' }  // 排序
      });

      // 按作者分组
      const postsByAuthor = new Map<number, any[]>();
      posts.forEach(post => {
        if (!postsByAuthor.has(post.authorId)) {
          postsByAuthor.set(post.authorId, []);
        }
        postsByAuthor.get(post.authorId)!.push(post);
      });

      // 按请求顺序返回
      return authorIds.map(authorId => {
        if (authorId == null || typeof authorId !== 'number' || authorId <= 0) {
          return [];
        }
        return postsByAuthor.get(authorId) || [];
      });
    } catch (error) {
      console.error('DataLoader error in createPostsByAuthorLoader:', error);
      // 返回空数组，而不是抛出错误
      return authorIds.map(() => []);
    }
  }, {
    // 配置选项
    batch: true,
    cache: true,
    maxBatchSize: 100
  });

// 在context中提供（带错误处理）
const server = new ApolloServer({
  typeDefs,
  resolvers,
});

await startStandaloneServer(server, {
  context: async ({ req }) => {
    try {
      return {
        prisma,
        loaders: {
          user: createUserLoader(),
          postsByAuthor: createPostsByAuthorLoader()
        }
      };
    } catch (error) {
      console.error('Error creating context:', error);
      // 返回基础context，即使loaders初始化失败
      return {
        prisma,
        loaders: {
          user: createUserLoader(),  // 重新创建，即使可能失败
          postsByAuthor: createPostsByAuthorLoader()
        }
      };
    }
  }
});

// 在Resolver中使用（带错误处理）
const resolvers = {
  Post: {
    author: async (parent: any, _: any, context: any) => {
      try {
        if (!parent || !parent.authorId) {
          throw new Error('Invalid parent post object or missing authorId');
        }

        if (!context || !context.loaders || !context.loaders.user) {
          // 降级到直接查询
          return await prisma.user.findUnique({ where: { id: parent.authorId } });
        }

        const user = await context.loaders.user.load(parent.authorId);
        return user;
      } catch (error) {
        console.error('Error loading author:', error);
        // 降级到直接查询
        try {
          return await prisma.user.findUnique({ where: { id: parent?.authorId } });
        } catch (fallbackError) {
          console.error('Fallback query also failed:', fallbackError);
          return null;
        }
      }
    }
  },

  User: {
    posts: async (parent: any, _: any, context: any) => {
      try {
        if (!parent || !parent.id) {
          throw new Error('Invalid parent user object or missing id');
        }

        if (!context || !context.loaders || !context.loaders.postsByAuthor) {
          // 降级到直接查询
          return await prisma.post.findMany({ where: { authorId: parent.id } });
        }

        const posts = await context.loaders.postsByAuthor.load(parent.id);
        return posts || [];
      } catch (error) {
        console.error('Error loading posts:', error);
        // 降级到直接查询
        try {
          return await prisma.post.findMany({ where: { authorId: parent?.id } });
        } catch (fallbackError) {
          console.error('Fallback query also failed:', fallbackError);
          return [];
        }
      }
    }
  }
};
```

---

## 6. 权限控制与RLS

### 6.1 JWT认证

#### PostGraphile JWT

```sql
-- 创建JWT类型
-- 创建JWT token类型（带错误处理）
DO $$
BEGIN
    -- 检查类型是否已存在
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jwt_token') THEN
        DROP TYPE jwt_token CASCADE;
        RAISE NOTICE '已删除现有类型: jwt_token';
    END IF;

    CREATE TYPE jwt_token AS (
        role TEXT,
        user_id INTEGER,
        exp INTEGER
    );

    RAISE NOTICE '类型创建成功: jwt_token';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '类型jwt_token已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建类型失败: %', SQLERRM;
END $$;

-- 登录函数（带完整错误处理）
CREATE OR REPLACE FUNCTION authenticate(
  username TEXT,
  password TEXT
) RETURNS jwt_token AS $$
DECLARE
  account users;
BEGIN
  -- 参数验证
  IF username IS NULL OR length(trim(username)) = 0 THEN
    RAISE EXCEPTION '用户名不能为空';
  END IF;

  IF password IS NULL OR length(password) = 0 THEN
    RAISE EXCEPTION '密码不能为空';
  END IF;

  -- 检查users表是否存在
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
    RAISE EXCEPTION 'users表不存在';
  END IF;

  -- 查询用户
  BEGIN
    SELECT * INTO account
    FROM users
    WHERE users.username = authenticate.username;

    IF NOT FOUND THEN
      -- 为了安全，不暴露用户是否存在
      RAISE EXCEPTION '用户名或密码错误';
    END IF;
  EXCEPTION
    WHEN undefined_table THEN
      RAISE EXCEPTION 'users表不存在';
    WHEN OTHERS THEN
      RAISE EXCEPTION '查询用户失败: %', SQLERRM;
  END;

  -- 验证密码
  IF account.password IS NULL THEN
    RAISE EXCEPTION '用户密码未设置';
  END IF;

  IF account.password = crypt(password, account.password) THEN
    -- 密码正确，返回JWT token
    RETURN (
      'user_role',
      account.id,
      extract(epoch FROM NOW() + INTERVAL '7 days')
    )::jwt_token;
  ELSE
    -- 密码错误
    RAISE EXCEPTION '用户名或密码错误';
  END IF;
EXCEPTION
  WHEN OTHERS THEN
    -- 记录错误但不暴露详细信息
    RAISE EXCEPTION '认证失败';
END;
$$ LANGUAGE plpgsql STRICT SECURITY DEFINER;
```

#### Hasura JWT

```javascript
// 生成JWT（带完整错误处理）
const jwt = require('jsonwebtoken');

/**
 * 生成JWT token
 * @param {Object} user - 用户对象，必须包含id属性
 * @param {Array<string>} roles - 用户角色数组，默认为['user']
 * @param {string} defaultRole - 默认角色，默认为'user'
 * @returns {string} JWT token
 * @throws {Error} 如果参数无效或JWT_SECRET未设置
 */
function generateToken(user, roles = ['user'], defaultRole = 'user') {
  try {
    // 参数验证
    if (!user) {
      throw new Error('User object is required');
    }

    if (!user.id) {
      throw new Error('User id is required');
    }

    if (!Array.isArray(roles) || roles.length === 0) {
      throw new Error('Roles must be a non-empty array');
    }

    if (!defaultRole || typeof defaultRole !== 'string') {
      throw new Error('Default role must be a non-empty string');
    }

    // 检查JWT_SECRET是否设置
    const jwtSecret = process.env.JWT_SECRET;
    if (!jwtSecret) {
      throw new Error('JWT_SECRET environment variable is not set');
    }

    if (jwtSecret.length < 32) {
      console.warn('Warning: JWT_SECRET should be at least 32 characters long for security');
    }

    // 生成token
    const token = jwt.sign(
      {
        'https://hasura.io/jwt/claims': {
          'x-hasura-allowed-roles': roles,
          'x-hasura-default-role': defaultRole,
          'x-hasura-user-id': user.id.toString()
        }
      },
      jwtSecret,
      {
        expiresIn: process.env.JWT_EXPIRES_IN || '7d',
        issuer: process.env.JWT_ISSUER || 'hasura',
        audience: process.env.JWT_AUDIENCE || 'hasura'
      }
    );

    return token;
  } catch (error) {
    console.error('Failed to generate JWT token:', error);
    throw error;
  }
}

/**
 * 验证JWT token
 * @param {string} token - JWT token
 * @returns {Object} 解码后的token payload
 * @throws {Error} 如果token无效或过期
 */
function verifyToken(token) {
  try {
    if (!token) {
      throw new Error('Token is required');
    }

    const jwtSecret = process.env.JWT_SECRET;
    if (!jwtSecret) {
      throw new Error('JWT_SECRET environment variable is not set');
    }

    const decoded = jwt.verify(token, jwtSecret, {
      issuer: process.env.JWT_ISSUER || 'hasura',
      audience: process.env.JWT_AUDIENCE || 'hasura'
    });

    return decoded;
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      throw new Error('Invalid token');
    } else if (error.name === 'TokenExpiredError') {
      throw new Error('Token has expired');
    } else {
      console.error('Token verification error:', error);
      throw new Error('Token verification failed');
    }
  }
}

module.exports = { generateToken, verifyToken };
```

### 6.2 Row Level Security（RLS）

```sql
-- 创建当前用户函数（带错误处理）
CREATE OR REPLACE FUNCTION current_user_id() RETURNS INTEGER AS $$
BEGIN
  RETURN nullif(current_setting('jwt.claims.user_id', true), '')::integer;
EXCEPTION
  WHEN OTHERS THEN
    -- 如果JWT设置不存在，返回NULL（允许匿名访问）
    RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- 启用RLS（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
        ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS已启用: posts';
    ELSE
        RAISE WARNING '表posts不存在，跳过RLS启用';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'comments') THEN
        ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS已启用: comments';
    ELSE
        RAISE WARNING '表comments不存在，跳过RLS启用';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '启用RLS失败: %', SQLERRM;
END $$;

-- Posts策略（带错误处理）
DO $$
BEGIN
    -- 删除现有策略（如果存在）
    IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'posts' AND policyname = 'posts_select_policy') THEN
        DROP POLICY posts_select_policy ON posts;
    END IF;

    CREATE POLICY posts_select_policy ON posts
        FOR SELECT
        USING (
            published = TRUE
            OR author_id = current_user_id()
        );
    RAISE NOTICE '策略创建成功: posts_select_policy';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建SELECT策略失败: %', SQLERRM;
END $$;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'posts' AND policyname = 'posts_insert_policy') THEN
        DROP POLICY posts_insert_policy ON posts;
    END IF;

    CREATE POLICY posts_insert_policy ON posts
        FOR INSERT
        WITH CHECK (author_id = current_user_id());
    RAISE NOTICE '策略创建成功: posts_insert_policy';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建INSERT策略失败: %', SQLERRM;
END $$;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'posts' AND policyname = 'posts_update_policy') THEN
        DROP POLICY posts_update_policy ON posts;
    END IF;

    CREATE POLICY posts_update_policy ON posts
        FOR UPDATE
        USING (author_id = current_user_id())
        WITH CHECK (author_id = current_user_id());
    RAISE NOTICE '策略创建成功: posts_update_policy';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建UPDATE策略失败: %', SQLERRM;
END $$;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'posts' AND policyname = 'posts_delete_policy') THEN
        DROP POLICY posts_delete_policy ON posts;
    END IF;

    CREATE POLICY posts_delete_policy ON posts
        FOR DELETE
        USING (author_id = current_user_id());
    RAISE NOTICE '策略创建成功: posts_delete_policy';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建DELETE策略失败: %', SQLERRM;
END $$;

-- Comments策略（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'comments' AND policyname = 'comments_select_policy') THEN
        DROP POLICY comments_select_policy ON comments;
    END IF;

    CREATE POLICY comments_select_policy ON comments
        FOR SELECT
        USING (
            EXISTS (
                SELECT 1 FROM posts
      WHERE posts.id = comments.post_id
        AND (posts.published = TRUE OR posts.author_id = current_user_id())
    )
  );

CREATE POLICY comments_insert_policy ON comments
  FOR INSERT
  WITH CHECK (author_id = current_user_id());

CREATE POLICY comments_update_policy ON comments
  FOR UPDATE
  USING (author_id = current_user_id());

CREATE POLICY comments_delete_policy ON comments
  FOR DELETE
  USING (author_id = current_user_id());
```

---

## 7. 实时订阅

### 7.1 PostGraphile实时

```javascript
// 使用postgraphile-plugin-subscriptions
const { postgraphile, makePluginHook } = require('postgraphile');
const { default: PgSimplifyInflectorPlugin } = require('@graphile-contrib/pg-simplify-inflector');
const { default: SubscriptionsPlugin } = require('@graphile/pg-pubsub');

const pluginHook = makePluginHook([PgSimplifyInflectorPlugin]);

app.use(
  postgraphile(pgConfig, 'public', {
    pluginHook,
    appendPlugins: [SubscriptionsPlugin],
    subscriptions: true,
    simpleSubscriptions: true,
    websocketMiddlewares: [
      // 认证中间件
      (req, res, next) => {
        // 验证WebSocket连接
        next();
      }
    ]
  })
);
```

**订阅示例**:

```graphql
subscription {
  listen(topic: "new_post") {
    relatedNode {
      ... on Post {
        id
        title
        author {
          username
        }
      }
    }
  }
}
```

### 7.2 Hasura实时

Hasura原生支持实时订阅，基于PostgreSQL LISTEN/NOTIFY。

```graphql
# 自动生成的订阅
subscription {
  posts(
    where: { published: { _eq: true } }
    order_by: { created_at: desc }
    limit: 10
  ) {
    id
    title
    author {
      username
    }
    created_at
  }
}
```

**前端实现**:

```typescript
import { useSubscription, gql } from '@apollo/client';

const POSTS_SUBSCRIPTION = gql`
  subscription OnPostsChanged {
    posts(order_by: { created_at: desc }, limit: 10) {
      id
      title
      content
      author {
        username
      }
    }
  }
`;

function LivePosts() {
  const { data, loading, error } = useSubscription(POSTS_SUBSCRIPTION);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h2>Live Posts</h2>
      {data.posts.map(post => (
        <div key={post.id}>
          <h3>{post.title}</h3>
          <p>by {post.author.username}</p>
          <p>{post.content}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 8. 性能优化

### 8.1 查询优化

#### N+1问题解决

**问题**:

```graphql
query {
  posts {      # 1次查询
    id
    title
    author {   # N次查询（每个post一次）
      username
    }
  }
}
```

**解决方案**:

1. **PostGraphile**: 自动优化为单次SQL JOIN
2. **Hasura**: 自动批处理
3. **Apollo + Prisma**: 使用DataLoader

**PostGraphile生成的SQL**:

```sql
SELECT
  posts.id,
  posts.title,
  users.username
FROM posts
LEFT JOIN users ON posts.author_id = users.id;
-- 单次查询，无N+1问题！
```

### 8.2 连接池

```javascript
// PostGraphile连接池配置（带完整错误处理）
const { Pool } = require('pg');

// 创建连接池（带错误处理）
const pgPool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://user:pass@localhost/db',
  max: parseInt(process.env.DB_MAX_CONNECTIONS || '20', 10),  // 最大连接数
  idleTimeoutMillis: 30000,   // 空闲超时
  connectionTimeoutMillis: 2000,
  // 连接重试配置
  retryDelayMs: 1000,
  retryAttempts: 3
});

// 监听连接池错误
pgPool.on('error', (err, client) => {
  console.error('Unexpected error on idle client:', err);
  // 可以在这里实现重连逻辑或告警
});

// 监听连接池连接事件
pgPool.on('connect', (client) => {
  console.log('New client connected to database');
});

// 测试连接
async function testConnection() {
  try {
    const client = await pgPool.connect();
    const result = await client.query('SELECT NOW()');
    console.log('Database connection test successful:', result.rows[0]);
    client.release();
    return true;
  } catch (error) {
    console.error('Database connection test failed:', error);
    return false;
  }
}

// 启动时测试连接
testConnection().then((success) => {
  if (!success) {
    console.error('Failed to connect to database. Exiting...');
    process.exit(1);
  }
});

// 优雅关闭
process.on('SIGINT', async () => {
  console.log('Closing database pool...');
  try {
    await pgPool.end();
    console.log('Database pool closed successfully');
  } catch (error) {
    console.error('Error closing database pool:', error);
  }
  process.exit(0);
});

app.use(
  postgraphile(pgPool, 'public', {
    // ...其他配置
  })
);
```

### 8.3 缓存策略

```javascript
// Apollo Server缓存（带完整错误处理）
import { ApolloServer } from '@apollo/server';
import { KeyvAdapter } from '@apollo/utils.keyvadapter';
import Keyv from 'keyv';

// 创建Redis缓存连接（带错误处理）
let cacheAdapter;
try {
  const keyv = new Keyv('redis://localhost:6379');

  // 监听错误
  keyv.on('error', (error) => {
    console.error('Redis cache error:', error);
    // 可以选择降级到内存缓存
  });

  // 测试连接
  await keyv.set('test', 'connection-test');
  const testValue = await keyv.get('test');
  if (testValue !== 'connection-test') {
    throw new Error('Redis cache connection test failed');
  }
  await keyv.delete('test');

  console.log('Redis cache connected successfully');
  cacheAdapter = new KeyvAdapter(keyv);
} catch (error) {
  console.error('Failed to initialize Redis cache, falling back to in-memory cache:', error);
  // 降级到内存缓存
  cacheAdapter = new KeyvAdapter(new Keyv());
}

const server = new ApolloServer({
  typeDefs,
  resolvers,
  cache: cacheAdapter,
  plugins: [
    {
      async requestDidStart() {
        return {
          async willSendResponse({ response, errors }) {
            try {
              // 如果有错误，不设置缓存
              if (errors && errors.length > 0) {
                response.http.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
                return;
              }

              // 设置缓存控制
              response.http.headers.set(
                'Cache-Control',
                'public, max-age=60, s-maxage=3600'
              );
            } catch (error) {
              console.error('Error setting cache headers:', error);
              // 失败时设置无缓存
              response.http.headers.set('Cache-Control', 'no-cache');
            }
          }
        };
      }
    }
  ]
});

// 启动服务器（带错误处理）
try {
  const { url } = await startStandaloneServer(server, {
    listen: { port: 4000 }
  });
  console.log(`Server ready at ${url}`);
} catch (error) {
  console.error('Failed to start server:', error);
  process.exit(1);
}
```

### 8.4 查询复杂度限制

```javascript
// 限制查询深度和复杂度（带完整错误处理）
import { createComplexityLimitRule } from 'graphql-validation-complexity';
import { GraphQLError } from 'graphql';

const MAX_COMPLEXITY = 1000;
const WARNING_COMPLEXITY = 500;

// 创建复杂度限制规则（带错误处理）
const complexityLimitRule = createComplexityLimitRule(MAX_COMPLEXITY, {
  onCost: (cost, node) => {
    try {
      // 记录查询成本
      if (cost > WARNING_COMPLEXITY) {
        console.warn(`High complexity query detected: ${cost}`, {
          query: node.loc?.source?.body?.substring(0, 200) // 记录前200个字符
        });
      }

      // 如果超过限制，抛出错误
      if (cost > MAX_COMPLEXITY) {
        throw new GraphQLError(
          `Query complexity ${cost} exceeds maximum allowed complexity of ${MAX_COMPLEXITY}`,
          {
            extensions: {
              code: 'COMPLEXITY_LIMIT_EXCEEDED',
              complexity: cost,
              maxComplexity: MAX_COMPLEXITY
            }
          }
        );
      }
    } catch (error) {
      // 如果是GraphQLError，直接抛出
      if (error instanceof GraphQLError) {
        throw error;
      }
      // 其他错误记录日志但不中断查询
      console.error('Error in complexity calculation:', error);
    }
  },
  // 自定义成本计算函数
  createError: (max, actual) => {
    return new GraphQLError(
      `Query complexity ${actual} exceeds maximum allowed complexity of ${max}`,
      {
        extensions: {
          code: 'COMPLEXITY_LIMIT_EXCEEDED',
          complexity: actual,
          maxComplexity: max
        }
      }
    );
  }
});

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [
    complexityLimitRule
  ],
  // 全局错误处理
  formatError: (error) => {
    console.error('GraphQL Error:', error);

    // 如果是复杂度错误，返回详细信息
    if (error.extensions?.code === 'COMPLEXITY_LIMIT_EXCEEDED') {
      return {
        message: error.message,
        extensions: {
          code: error.extensions.code,
          complexity: error.extensions.complexity,
          maxComplexity: error.extensions.maxComplexity
        }
      };
    }

    // 生产环境隐藏内部错误详情
    if (process.env.NODE_ENV === 'production') {
      return {
        message: 'An error occurred',
        extensions: {
          code: error.extensions?.code || 'INTERNAL_ERROR'
        }
      };
    }

    // 开发环境返回完整错误信息
    return error;
  }
});
```

---

## 9. 生产实战案例

### 9.1 案例1：社交媒体平台

#### 需求

- 10万+用户
- 实时动态更新
- 评论/点赞实时通知
- 高并发读写

#### 架构选择

**Hasura + PostgreSQL + Redis**:

```yaml
# 架构
Frontend (React)
  → Hasura (GraphQL + Subscriptions)
    → PostgreSQL (数据存储)
    → Redis (缓存热数据)
```

#### 核心Schema

```sql
-- 社交网络表结构（带错误处理）
-- 1. 用户表
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        DROP TABLE users CASCADE;
        RAISE NOTICE '已删除现有表: users';
    END IF;

    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        avatar_url TEXT,
        bio TEXT,
        follower_count INT DEFAULT 0,
        following_count INT DEFAULT 0
    );

    RAISE NOTICE '用户表创建成功: users';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表 users 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建用户表失败: %', SQLERRM;
END $$;

-- 2. 帖子表
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
        DROP TABLE posts CASCADE;
        RAISE NOTICE '已删除现有表: posts';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION 'users表不存在，无法创建外键约束';
    END IF;

    CREATE TABLE posts (
        id SERIAL PRIMARY KEY,
        author_id INT REFERENCES users(id),
        content TEXT NOT NULL,
        image_url TEXT,
        like_count INT DEFAULT 0,
        comment_count INT DEFAULT 0,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    RAISE NOTICE '帖子表创建成功: posts';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'users表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '表 posts 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建帖子表失败: %', SQLERRM;
END $$;

-- 3. 评论表
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'comments') THEN
        DROP TABLE comments CASCADE;
        RAISE NOTICE '已删除现有表: comments';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
        RAISE EXCEPTION 'posts表不存在，无法创建外键约束';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION 'users表不存在，无法创建外键约束';
    END IF;

    CREATE TABLE comments (
        id SERIAL PRIMARY KEY,
        post_id INT REFERENCES posts(id) ON DELETE CASCADE,
        author_id INT REFERENCES users(id),
        content TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    RAISE NOTICE '评论表创建成功: comments';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表或users表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '表 comments 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建评论表失败: %', SQLERRM;
END $$;

-- 4. 点赞表
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'likes') THEN
        DROP TABLE likes CASCADE;
        RAISE NOTICE '已删除现有表: likes';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
        RAISE EXCEPTION 'posts表不存在，无法创建外键约束';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION 'users表不存在，无法创建外键约束';
    END IF;

    CREATE TABLE likes (
        user_id INT REFERENCES users(id),
        post_id INT REFERENCES posts(id) ON DELETE CASCADE,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (user_id, post_id)
    );

    RAISE NOTICE '点赞表创建成功: likes';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'posts表或users表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '表 likes 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建点赞表失败: %', SQLERRM;
END $$;

-- 5. 关注表
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'follows') THEN
        DROP TABLE follows CASCADE;
        RAISE NOTICE '已删除现有表: follows';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION 'users表不存在，无法创建外键约束';
    END IF;

    CREATE TABLE follows (
        follower_id INT REFERENCES users(id),
        following_id INT REFERENCES users(id),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (follower_id, following_id),
        CONSTRAINT no_self_follow CHECK (follower_id != following_id)
    );

    RAISE NOTICE '关注表创建成功: follows';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'users表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '表 follows 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建关注表失败: %', SQLERRM;
END $$;
```

#### 实时动态订阅

```graphql
# 订阅关注的人的新帖子
subscription FeedSubscription($userId: Int!) {
  posts(
    where: {
      author: {
        followers: {
          follower_id: { _eq: $userId }
        }
      }
    }
    order_by: { created_at: desc }
    limit: 20
  ) {
    id
    content
    image_url
    like_count
    comment_count
    created_at
    author {
      username
      avatar_url
    }
  }
}
```

### 9.2 案例2：实时协作工具

#### 9.2.1 需求

- 多人同时编辑文档
- 实时同步光标位置
- 操作历史记录
- 冲突解决

#### 9.2.2 架构选择

**PostGraphile + PostgreSQL + WebSocket**:

#### Operational Transform实现

```sql
-- 实时协作表结构（带错误处理）
-- 1. 文档表
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
        DROP TABLE documents CASCADE;
        RAISE NOTICE '已删除现有表: documents';
    END IF;

    -- 检查users表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION 'users表不存在，无法创建外键约束';
    END IF;

    CREATE TABLE documents (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT,
        version INT DEFAULT 0,
        created_by INT REFERENCES users(id),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    RAISE NOTICE '文档表创建成功: documents';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'users表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '表 documents 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建文档表失败: %', SQLERRM;
END $$;

-- 2. 操作记录表
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'operations') THEN
        DROP TABLE operations CASCADE;
        RAISE NOTICE '已删除现有表: operations';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
        RAISE EXCEPTION 'documents表不存在，无法创建外键约束';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION 'users表不存在，无法创建外键约束';
    END IF;

    CREATE TABLE operations (
        id SERIAL PRIMARY KEY,
        document_id INT REFERENCES documents(id) ON DELETE CASCADE,
        user_id INT REFERENCES users(id),
        operation_type TEXT NOT NULL CHECK (operation_type IN ('insert', 'delete', 'retain')),
        position INT NOT NULL CHECK (position >= 0),
        content TEXT,
        version INT NOT NULL,
        timestamp TIMESTAMPTZ DEFAULT NOW()
    );

    RAISE NOTICE '操作记录表创建成功: operations';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'documents表或users表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '表 operations 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建操作记录表失败: %', SQLERRM;
END $$;

-- 应用操作的函数（带完整错误处理）
CREATE OR REPLACE FUNCTION apply_operation(
  doc_id INT,
  op_type TEXT,
  pos INT,
  op_content TEXT,
  expected_version INT
) RETURNS documents AS $$
DECLARE
  doc documents;
  current_content TEXT;
BEGIN
  -- 参数验证
  IF doc_id IS NULL THEN
    RAISE EXCEPTION '文档ID不能为空';
  END IF;

  IF op_type IS NULL OR op_type NOT IN ('insert', 'delete', 'retain') THEN
    RAISE EXCEPTION '无效的操作类型: % (必须是: insert, delete, retain)', op_type;
  END IF;

  IF pos IS NULL OR pos < 0 THEN
    RAISE EXCEPTION '无效的位置: % (必须 >= 0)', pos;
  END IF;

  IF expected_version IS NULL OR expected_version < 0 THEN
    RAISE EXCEPTION '无效的版本号: % (必须 >= 0)', expected_version;
  END IF;

  -- 锁定文档（带错误处理）
  BEGIN
    SELECT * INTO doc FROM documents WHERE id = doc_id FOR UPDATE;

    IF NOT FOUND THEN
      RAISE EXCEPTION '文档不存在: %', doc_id;
    END IF;
  EXCEPTION
    WHEN undefined_table THEN
      RAISE EXCEPTION 'documents表不存在';
    WHEN OTHERS THEN
      RAISE EXCEPTION '查询文档失败: %', SQLERRM;
  END;

  -- 检查版本冲突
  IF doc.version != expected_version THEN
    RAISE EXCEPTION '版本冲突: 期望版本 %, 当前版本 %', expected_version, doc.version;
  END IF;

  -- 保存当前内容
  current_content := COALESCE(doc.content, '');

  -- 验证位置有效性
  IF pos > length(current_content) THEN
    RAISE EXCEPTION '位置超出范围: % > % (内容长度)', pos, length(current_content);
  END IF;

  -- 应用操作
  BEGIN
    CASE op_type
      WHEN 'insert' THEN
        IF op_content IS NULL THEN
          RAISE EXCEPTION 'insert操作需要提供content';
        END IF;
        doc.content := left(current_content, pos) || op_content || substring(current_content FROM pos + 1);

      WHEN 'delete' THEN
        IF op_content IS NULL THEN
          RAISE EXCEPTION 'delete操作需要提供content';
        END IF;
        IF pos + length(op_content) > length(current_content) THEN
          RAISE EXCEPTION '删除范围超出内容长度';
        END IF;
        doc.content := left(current_content, pos) || substring(current_content FROM pos + length(op_content) + 1);

      WHEN 'retain' THEN
        -- retain操作不需要修改内容
        doc.content := current_content;

      ELSE
        RAISE EXCEPTION '未知的操作类型: %', op_type;
    END CASE;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE EXCEPTION '应用操作失败: %', SQLERRM;
  END;

  -- 更新版本
  doc.version := doc.version + 1;

  -- 更新数据库
  BEGIN
    UPDATE documents SET content = doc.content, version = doc.version WHERE id = doc_id;

    IF NOT FOUND THEN
      RAISE EXCEPTION '更新文档失败: 文档不存在或已被删除';
    END IF;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE EXCEPTION '更新文档失败: %', SQLERRM;
  END;

  RETURN doc;
EXCEPTION
  WHEN OTHERS THEN
    RAISE EXCEPTION 'apply_operation失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql VOLATILE;

---

## 10. 最佳实践

### 10.1 Schema设计

#### ✅ 推荐做法

```sql
-- 1. 使用有意义的命名（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'blog_posts') THEN
        DROP TABLE blog_posts CASCADE;
        RAISE NOTICE '已删除现有表: blog_posts';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION 'users表不存在，无法创建外键约束';
    END IF;

    CREATE TABLE blog_posts (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,  -- URL友好
        author_id INT REFERENCES users(id)
    );

    RAISE NOTICE '表创建成功: blog_posts';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'users表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '表 blog_posts 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 2. 添加注释（自动生成文档，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'blog_posts') THEN
        COMMENT ON TABLE blog_posts IS 'User blog posts';
        COMMENT ON COLUMN blog_posts.slug IS 'URL-friendly identifier';
        RAISE NOTICE '注释添加成功';
    ELSE
        RAISE WARNING 'blog_posts表不存在，无法添加注释';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '添加注释失败: %', SQLERRM;
END $$;

-- 3. 合理使用索引（带错误处理）
DO $$
BEGIN
    -- 创建author_id索引
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'blog_posts' AND indexname = 'blog_posts_author_id_idx') THEN
        CREATE INDEX blog_posts_author_id_idx ON blog_posts(author_id);
        RAISE NOTICE '索引创建成功: blog_posts_author_id_idx';
    ELSE
        RAISE NOTICE '索引已存在: blog_posts_author_id_idx';
    END IF;

    -- 创建slug索引
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'blog_posts' AND indexname = 'blog_posts_slug_idx') THEN
        CREATE INDEX blog_posts_slug_idx ON blog_posts(slug);
        RAISE NOTICE '索引创建成功: blog_posts_slug_idx';
    ELSE
        RAISE NOTICE '索引已存在: blog_posts_slug_idx';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'blog_posts表不存在，无法创建索引';
    WHEN duplicate_object THEN
        RAISE WARNING '索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;

-- 4. 使用约束（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_schema = 'public' AND table_name = 'blog_posts' AND constraint_name = 'slug_format') THEN
        ALTER TABLE blog_posts DROP CONSTRAINT slug_format;
        RAISE NOTICE '已删除现有约束: slug_format';
    END IF;

    ALTER TABLE blog_posts ADD CONSTRAINT slug_format
        CHECK (slug ~ '^[a-z0-9-]+$');
    RAISE NOTICE '约束创建成功: slug_format';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'blog_posts表不存在';
    WHEN duplicate_object THEN
        RAISE WARNING '约束已存在';
    WHEN check_violation THEN
        RAISE EXCEPTION '约束检查失败，请检查现有数据是否符合约束条件';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建约束失败: %', SQLERRM;
END $$;
```

#### ❌ 避免的做法

```sql
-- ❌ 1. 避免过度嵌套
-- 不好：需要4层嵌套
posts → comments → replies → likes

-- 好：扁平化
posts → comments (包含parent_id)
comments → likes

-- ❌ 2. 避免没有外键
CREATE TABLE orders (
  user_id INT  -- 没有REFERENCES，无法自动生成关联
);

-- ✅ 应该
CREATE TABLE orders (
  user_id INT REFERENCES users(id)  -- 自动生成GraphQL关联
);
```

### 10.2 安全最佳实践

```sql
-- 1. 永远启用RLS（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sensitive_table') THEN
        ALTER TABLE sensitive_table ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS已启用: sensitive_table';
    ELSE
        RAISE WARNING '表sensitive_table不存在，跳过RLS启用';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表sensitive_table不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '启用RLS失败: %', SQLERRM;
END $$;

-- 2. 最小权限原则（带错误处理）
DO $$
BEGIN
    -- 检查用户是否存在
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'graphql_user') THEN
        -- 授予权限
        GRANT SELECT ON users TO graphql_user;
        GRANT INSERT, UPDATE ON posts TO graphql_user;
        RAISE NOTICE '权限授予成功: graphql_user';
    ELSE
        RAISE WARNING '用户graphql_user不存在，请先创建用户';
    END IF;

    -- 检查表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE WARNING '表users不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts') THEN
        RAISE WARNING '表posts不存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在，无法授予权限';
    WHEN invalid_role_specification THEN
        RAISE EXCEPTION '用户graphql_user不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '授予权限失败: %', SQLERRM;
END $$;

-- 3. 敏感字段使用视图（带错误处理）
DO $$
BEGIN
    -- 检查源表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION 'users表不存在，无法创建视图';
    END IF;

    -- 删除现有视图（如果存在）
    IF EXISTS (SELECT 1 FROM information_schema.views WHERE table_schema = 'public' AND table_name = 'public_user_profile') THEN
        DROP VIEW public_user_profile CASCADE;
        RAISE NOTICE '已删除现有视图: public_user_profile';
    END IF;

    CREATE VIEW public_user_profile AS
    SELECT id, username, avatar_url, bio
    FROM users;
    -- 不暴露email, password_hash等敏感字段

    RAISE NOTICE '视图创建成功: public_user_profile';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'users表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '视图已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建视图失败: %', SQLERRM;
END $$;

-- 4. 审计日志（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
        DROP TABLE audit_log CASCADE;
        RAISE NOTICE '已删除现有表: audit_log';
    END IF;

    CREATE TABLE audit_log (
        id SERIAL PRIMARY KEY,
        table_name TEXT NOT NULL,
        operation TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
        user_id INT,
        old_data JSONB,
        new_data JSONB,
        timestamp TIMESTAMPTZ DEFAULT NOW()
    );

    -- 创建索引以提高查询性能
    CREATE INDEX audit_log_table_name_idx ON audit_log(table_name);
    CREATE INDEX audit_log_timestamp_idx ON audit_log(timestamp);
    CREATE INDEX audit_log_user_id_idx ON audit_log(user_id) WHERE user_id IS NOT NULL;

    RAISE NOTICE '审计日志表创建成功: audit_log';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表audit_log已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建审计日志表失败: %', SQLERRM;
END $$;
```

### 10.3 性能最佳实践

```sql
-- 1. 为关联创建索引
CREATE INDEX posts_author_id_idx ON posts(author_id);
CREATE INDEX comments_post_id_idx ON comments(post_id);

-- 2. 使用部分索引
CREATE INDEX active_posts_idx ON posts(created_at) WHERE published = TRUE;

-- 3. 物化视图缓存复杂查询
CREATE MATERIALIZED VIEW popular_posts AS
SELECT p.id, p.title, COUNT(l.user_id) AS like_count
FROM posts p
LEFT JOIN likes l ON p.id = l.post_id
GROUP BY p.id
HAVING COUNT(l.user_id) > 100;

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY popular_posts;

-- 4. 分区大表
CREATE TABLE events (
  id BIGSERIAL,
  event_type TEXT,
  created_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2025_01 PARTITION OF events
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

---

## 11. 方案对比

### 11.1 综合对比

| 维度 | PostGraphile | Hasura | Apollo + Prisma |
| --- | --- | --- | --- |
| **学习曲线** | 低 | 低 | 中高 |
| **开发速度** | 极快 | 极快 | 中 |
| **灵活性** | 中 | 中 | 极高 |
| **PostgreSQL优先** | ✅ 优秀 | ⚠️ 良好 | ❌ 一般 |
| **实时订阅** | ⚠️ 需插件 | ✅ 原生 | ⚠️ 需额外配置 |
| **权限控制** | ✅ RLS | ✅ RLS + 自定义 | ⚠️ 需手动 |
| **性能** | ✅ 优秀 | ✅ 优秀 | ⚠️ 需优化 |
| **TypeScript支持** | ⚠️ 有限 | ⚠️ 有限 | ✅ 完整 |
| **云服务** | ❌ 无 | ✅ Hasura Cloud | ❌ 无 |
| **开源** | ✅ MIT | ✅ Apache 2.0 | ✅ MIT |
| **社区** | 中等 | 大 | 极大 |
| **适合场景** | PostgreSQL重度 | 实时应用 | 复杂业务 |

### 11.2 选择建议

```text
选择PostGraphile，如果：
✅ PostgreSQL是核心数据源
✅ 需要快速原型开发
✅ 重度使用PostgreSQL特性（函数、视图、RLS）
✅ 团队熟悉SQL

选择Hasura，如果：
✅ 需要实时订阅
✅ 微服务架构（远程Schema）
✅ 需要事件触发器
✅ 希望使用云服务

选择Apollo + Prisma，如果：
✅ 需要完全定制GraphQL Schema
✅ 复杂业务逻辑
✅ TypeScript全栈
✅ 团队偏好编码而非配置
```

---

## 12. FAQ与疑难解答

### Q1: GraphQL会比REST慢吗？

**A**: 不会，通常更快。

- ✅ **减少请求次数**：单次请求获取所有数据
- ✅ **精确数据**：只传输需要的字段
- ✅ **SQL优化**：PostGraphile/Hasura自动生成优化的SQL
- ⚠️ **注意**：需要限制查询复杂度，防止恶意查询

### Q2: 如何处理文件上传？

**A**: GraphQL不直接处理文件，使用以下方案：

```javascript
// 方案1：graphql-upload（带完整错误处理）
import graphqlUploadExpress from 'graphql-upload/graphqlUploadExpress.js';
import { createWriteStream } from 'fs';
import { join } from 'path';
import { v4 as uuidv4 } from 'uuid';

// 配置上传中间件（带错误处理）
app.use('/graphql', graphqlUploadExpress({
  maxFileSize: 10000000,  // 10MB
  maxFiles: 10,
  // 自定义错误处理
  processRequest: (request, response, next) => {
    try {
      // 验证文件大小和数量
      if (request.files && request.files.length > 10) {
        return response.status(400).json({
          error: 'Too many files. Maximum 10 files allowed.'
        });
      }
      next();
    } catch (error) {
      console.error('Upload middleware error:', error);
      response.status(500).json({
        error: 'File upload processing failed'
      });
    }
  }
}));

// Schema
const typeDefs = `
  scalar Upload

  type File {
    filename: String!
    mimetype: String!
    url: String!
    size: Int!
  }

  type Mutation {
    uploadFile(file: Upload!): File!
  }
`;

// Resolver（带完整错误处理）
const resolvers = {
  Mutation: {
    uploadFile: async (_, { file }) => {
      try {
        // 参数验证
        if (!file) {
          throw new Error('File is required');
        }

        const { createReadStream, filename, mimetype, encoding } = await file;

        // 验证文件类型
        const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
        if (!allowedMimeTypes.includes(mimetype)) {
          throw new Error(`File type ${mimetype} is not allowed. Allowed types: ${allowedMimeTypes.join(', ')}`);
        }

        // 生成唯一文件名
        const fileExtension = filename.split('.').pop();
        const uniqueFilename = `${uuidv4()}.${fileExtension}`;
        const filePath = join(__dirname, 'uploads', uniqueFilename);

        // 确保上传目录存在
        const fs = require('fs');
        const uploadDir = join(__dirname, 'uploads');
        if (!fs.existsSync(uploadDir)) {
          fs.mkdirSync(uploadDir, { recursive: true });
        }

        // 上传文件
        return new Promise((resolve, reject) => {
          const stream = createReadStream();
          const writeStream = createWriteStream(filePath);
          let fileSize = 0;

          stream.pipe(writeStream);

          stream.on('data', (chunk) => {
            fileSize += chunk.length;
            // 检查文件大小
            if (fileSize > 10000000) {  // 10MB
              writeStream.destroy();
              fs.unlinkSync(filePath);
              reject(new Error('File size exceeds 10MB limit'));
            }
          });

          stream.on('error', (error) => {
            console.error('Stream error:', error);
            writeStream.destroy();
            if (fs.existsSync(filePath)) {
              fs.unlinkSync(filePath);
            }
            reject(new Error('File upload failed: ' + error.message));
          });

          writeStream.on('finish', () => {
            const uploadedUrl = `/uploads/${uniqueFilename}`;
            resolve({
              filename: uniqueFilename,
              mimetype,
              url: uploadedUrl,
              size: fileSize
            });
          });

          writeStream.on('error', (error) => {
            console.error('Write stream error:', error);
            if (fs.existsSync(filePath)) {
              fs.unlinkSync(filePath);
            }
            reject(new Error('File write failed: ' + error.message));
          });
        });
      } catch (error) {
        console.error('File upload error:', error);
        throw new Error(`File upload failed: ${error.message}`);
      }
    }
  }
};

// 方案2：预签名URL（推荐）
mutation {
  generateUploadUrl(filename: "image.jpg") {
    uploadUrl
    fileUrl
  }
}
// 客户端直接上传到S3
```

### Q3: 如何实现分页？

**A**: 三种分页方式：

```graphql
# 1. Offset分页（简单）
query {
  posts(limit: 10, offset: 20) {
    id
    title
  }
}

# 2. Cursor分页（推荐）
query {
  posts(first: 10, after: "cursor123") {
    edges {
      cursor
      node {
        id
        title
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

# 3. Relay规范分页
query {
  postsConnection(first: 10, after: "cursor123") {
    edges {
      cursor
      node {
        id
        title
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}
```

### Q4: GraphQL如何处理错误？

**A**: 标准化错误处理：

```typescript
// 自定义错误类
import { GraphQLError } from 'graphql';

class AuthenticationError extends GraphQLError {
  constructor(message: string) {
    super(message, {
      extensions: {
        code: 'UNAUTHENTICATED',
        http: { status: 401 }
      }
    });
  }
}

class ValidationError extends GraphQLError {
  constructor(message: string, field: string) {
    super(message, {
      extensions: {
        code: 'BAD_USER_INPUT',
        field,
        http: { status: 400 }
      }
    });
  }
}

// 在Resolver中使用（带完整错误处理）
const resolvers = {
  Mutation: {
    createPost: async (_, { title, content }, context) => {
      try {
        // 认证检查
        if (!context.user || !context.user.id) {
          throw new AuthenticationError('You must be logged in');
        }

        // 参数验证
        if (!title || typeof title !== 'string') {
          throw new ValidationError('Title is required', 'title');
        }

        if (title.trim().length < 5) {
          throw new ValidationError('Title must be at least 5 characters', 'title');
        }

        if (title.length > 200) {
          throw new ValidationError('Title must be less than 200 characters', 'title');
        }

        // 数据库操作（带错误处理）
        try {
          const post = await db.query(
            'INSERT INTO posts (author_id, title, content) VALUES ($1, $2, $3) RETURNING *',
            [context.user.id, title, content || null]
          );

          if (!post.rows || post.rows.length === 0) {
            throw new Error('Failed to create post');
          }

          return post.rows[0];
        } catch (dbError) {
          console.error('Database error:', dbError);

          // 数据库错误处理
          if (dbError.code === '23503') { // 外键约束错误
            throw new ValidationError('Invalid user', 'author_id');
          } else if (dbError.code === '23505') { // 唯一约束错误
            throw new ValidationError('Post with this title already exists', 'title');
          } else {
            throw new Error('Database operation failed');
          }
        }
      } catch (error) {
        // 如果是GraphQL错误，直接抛出
        if (error instanceof AuthenticationError || error instanceof ValidationError) {
          throw error;
        }

        // 其他错误转换为GraphQL错误
        console.error('Unexpected error:', error);
        throw new Error(`Failed to create post: ${error.message}`);
      }
    }
  }
};

// 客户端处理
const { data, errors } = await client.mutate({
  mutation: CREATE_POST,
  variables: { title, content }
});

if (errors) {
  errors.forEach(error => {
    console.error(error.message);
    console.error(error.extensions.code);
  });
}
```

### Q5: 如何监控GraphQL性能？

**A**: 使用Apollo Studio或自定义监控：

```javascript
import { ApolloServerPluginUsageReporting } from '@apollo/server/plugin/usageReporting';

const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: [
    // Apollo Studio监控
    ApolloServerPluginUsageReporting({
      sendVariableValues: { all: true },
      sendHeaders: { all: true }
    }),

    // 自定义监控
    {
      async requestDidStart(requestContext) {
        const start = Date.now();

        return {
          async willSendResponse(requestContext) {
            const duration = Date.now() - start;
            console.log(`Query took ${duration}ms`);

            // 发送到监控系统
            metrics.timing('graphql.query.duration', duration);
          }
        };
      }
    }
  ]
});
```

---

## 📚 延伸阅读

### 官方资源

- [GraphQL Specification](https://spec.graphql.org/)
- [PostGraphile Documentation](https://www.graphile.org/postgraphile/)
- [Hasura Documentation](https://hasura.io/docs/)
- [Apollo Server Documentation](https://www.apollographql.com/docs/apollo-server/)
- [Prisma Documentation](https://www.prisma.io/docs/)

### 工具生态

- **GraphiQL**: 浏览器内GraphQL IDE
- **Apollo Studio**: GraphQL监控平台
- **Altair**: 功能丰富的GraphQL客户端
- **GraphQL Voyager**: Schema可视化工具

### 推荐书籍

- 《Learning GraphQL》by Eve Porcello & Alex Banks
- 《Production Ready GraphQL》by Marc-André Giroux
- 《The Road to GraphQL》by Robin Wieruch

---

## ✅ 学习检查清单

- [ ] 理解GraphQL核心概念和优势
- [ ] 掌握GraphQL Schema定义
- [ ] 能够使用PostGraphile快速构建API
- [ ] 能够配置Hasura实时订阅
- [ ] 理解Apollo + Prisma架构
- [ ] 掌握RLS权限控制
- [ ] 能够实现JWT认证
- [ ] 理解N+1问题及解决方案
- [ ] 能够优化GraphQL查询性能
- [ ] 能够部署生产级GraphQL服务

---

## 💡 下一步学习

1. **进阶主题**:
   - GraphQL Federation（微服务整合）
   - Schema Stitching
   - GraphQL Code Generator
   - 自定义Scalar类型

2. **相关课程**:
   - [PostgreSQL安全深化](../05-安全与合规/README.md)
   - [PostgreSQL高可用](../13-高可用架构/)
   - [PostgreSQL性能调优](../30-性能调优/)

---

**文档维护**: 本文档持续更新以反映GraphQL生态最新特性。
**反馈**: 如发现错误或有改进建议，请提交issue。

**版本历史**:

- v1.0 (2025-01): 初始版本，覆盖PostGraphile、Hasura、Apollo三大方案
