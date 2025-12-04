# Rust数据结构与PostgreSQL表结构映射

> **文档编号**: DESIGN-RUST-DATASTRUCTURE-001
> **主题**: Rust数据结构与PostgreSQL表结构映射
> **版本**: PostgreSQL 17 & 18
> **相关文档**:
>
> - [表结构设计深度分析](表结构设计深度分析.md)
> - [Rust类型系统与PostgreSQL类型系统](Rust类型系统与PostgreSQL类型系统.md)

---

## 📑 目录

- [Rust数据结构与PostgreSQL表结构映射](#rust数据结构与postgresql表结构映射)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📊 第一部分：Struct与Table映射](#-第一部分struct与table映射)
    - [1.1 基本映射规则](#11-基本映射规则)
      - [1.1.1 Struct定义](#111-struct定义)
    - [1.2 字段类型映射](#12-字段类型映射)
      - [1.2.1 类型对应表](#121-类型对应表)
    - [1.3 嵌套结构映射](#13-嵌套结构映射)
      - [1.3.1 嵌套Struct](#131-嵌套struct)
  - [🔢 第二部分：Enum与PostgreSQL枚举类型](#-第二部分enum与postgresql枚举类型)
    - [2.1 Rust Enum映射](#21-rust-enum映射)
      - [2.1.1 Enum定义](#211-enum定义)
    - [2.2 PostgreSQL枚举类型](#22-postgresql枚举类型)
      - [2.2.1 枚举类型创建](#221-枚举类型创建)
  - [❓ 第三部分：Option类型与NULL值处理](#-第三部分option类型与null值处理)
    - [3.1 Option类型映射](#31-option类型映射)
      - [3.1.1 Option字段](#311-option字段)
    - [3.2 NULL值处理](#32-null值处理)
      - [3.2.1 NULL值查询](#321-null值查询)
    - [3.3 MVCC与NULL值](#33-mvcc与null值)
      - [3.3.1 NULL位图](#331-null位图)
  - [📦 第四部分：嵌套结构与JSONB](#-第四部分嵌套结构与jsonb)
    - [4.1 嵌套结构映射](#41-嵌套结构映射)
      - [4.1.1 JSONB存储](#411-jsonb存储)
    - [4.2 JSONB版本管理](#42-jsonb版本管理)
      - [4.2.1 MVCC与JSONB](#421-mvcc与jsonb)
  - [📝 总结](#-总结)

---

## 📋 概述

本文档详细说明Rust数据结构与PostgreSQL表结构的映射关系，包括Struct、Enum、Option和嵌套结构的映射规则，以及MVCC对这些映射的影响。

**核心内容**：

- Struct与Table映射
- Enum与PostgreSQL枚举类型
- Option类型与NULL值处理
- 嵌套结构与JSONB
- MVCC对数据结构映射的影响

**目标读者**：

- Rust开发者
- 数据库设计人员
- 系统架构师

---

## 📊 第一部分：Struct与Table映射

### 1.1 基本映射规则

#### 1.1.1 Struct定义

```rust
use sqlx::FromRow;

#[derive(FromRow)]
struct User {
    id: i32,
    name: String,
    email: String,
    balance: i64,
    created_at: chrono::DateTime<chrono::Utc>,
}

// 对应的PostgreSQL表结构
// CREATE TABLE users (
//     id INTEGER PRIMARY KEY,
//     name TEXT NOT NULL,
//     email TEXT NOT NULL,
//     balance BIGINT NOT NULL,
//     created_at TIMESTAMP WITH TIME ZONE NOT NULL
// );
```

### 1.2 字段类型映射

#### 1.2.1 类型对应表

| Rust类型 | PostgreSQL类型 | MVCC影响 |
|---------|---------------|---------|
| `i32` | `INTEGER` | 无影响 |
| `i64` | `BIGINT` | 无影响 |
| `String` | `TEXT` | 可能触发TOAST |
| `bool` | `BOOLEAN` | 无影响 |
| `chrono::DateTime<Utc>` | `TIMESTAMP WITH TIME ZONE` | 时间戳比较 |
| `Option<T>` | `T`或`NULL` | NULL位图处理 |

### 1.3 嵌套结构映射

#### 1.3.1 嵌套Struct

```rust
#[derive(FromRow)]
struct Address {
    street: String,
    city: String,
    zip_code: String,
}

#[derive(FromRow)]
struct User {
    id: i32,
    name: String,
    address: Address,  // 嵌套结构
}

// 映射到PostgreSQL：
// 1. 使用JSONB存储嵌套结构
// 2. 或使用多个列存储
```

---

## 🔢 第二部分：Enum与PostgreSQL枚举类型

### 2.1 Rust Enum映射

#### 2.1.1 Enum定义

```rust
#[derive(Debug, Clone, Copy, sqlx::Type)]
#[sqlx(type_name = "user_status", rename_all = "lowercase")]
enum UserStatus {
    Active,
    Inactive,
    Suspended,
}

#[derive(FromRow)]
struct User {
    id: i32,
    name: String,
    status: UserStatus,
}
```

### 2.2 PostgreSQL枚举类型

#### 2.2.1 枚举类型创建

```sql
-- 创建PostgreSQL枚举类型
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');

-- 使用枚举类型
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    status user_status NOT NULL
);
```

---

## ❓ 第三部分：Option类型与NULL值处理

### 3.1 Option类型映射

#### 3.1.1 Option字段

```rust
#[derive(FromRow)]
struct User {
    id: i32,
    name: String,
    email: Option<String>,  // 可空字段
    phone: Option<String>,   // 可空字段
}

// 对应的PostgreSQL表结构
// CREATE TABLE users (
//     id INTEGER PRIMARY KEY,
//     name TEXT NOT NULL,
//     email TEXT,      -- 可空
//     phone TEXT       -- 可空
// );
```

### 3.2 NULL值处理

#### 3.2.1 NULL值查询

```rust
use sqlx::PgPool;

async fn handle_null(pool: &PgPool) -> Result<(), sqlx::Error> {
    let user: Option<User> = sqlx::query_as("SELECT * FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_optional(pool)
        .await?;

    match user {
        Some(u) => {
            match u.email {
                Some(email) => println!("Email: {}", email),
                None => println!("No email"),
            }
        }
        None => println!("User not found"),
    }

    Ok(())
}
```

### 3.3 MVCC与NULL值

#### 3.3.1 NULL位图

```rust
// PostgreSQL使用NULL位图存储NULL值
// MVCC版本链中，NULL位图也会被版本化
// Option类型在Rust中安全地处理NULL值
```

---

## 📦 第四部分：嵌套结构与JSONB

### 4.1 嵌套结构映射

#### 4.1.1 JSONB存储

```rust
use serde::{Serialize, Deserialize};
use sqlx::types::Json;

#[derive(Serialize, Deserialize, Clone)]
struct Address {
    street: String,
    city: String,
    zip_code: String,
}

#[derive(FromRow)]
struct User {
    id: i32,
    name: String,
    address: Json<Address>,  // JSONB存储
}

// 对应的PostgreSQL表结构
// CREATE TABLE users (
//     id INTEGER PRIMARY KEY,
//     name TEXT NOT NULL,
//     address JSONB NOT NULL
// );
```

### 4.2 JSONB版本管理

#### 4.2.1 MVCC与JSONB

```rust
// JSONB在MVCC中的行为：
// 1. UPDATE时创建新版本（整个JSONB对象）
// 2. 版本链中存储完整的JSONB对象
// 3. 查询时使用快照判断可见性

use sqlx::PgPool;

async fn update_jsonb(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    // 更新JSONB字段
    sqlx::query("UPDATE users SET address = $1 WHERE id = $2")
        .bind(serde_json::json!({
            "street": "123 Main St",
            "city": "New York",
            "zip_code": "10001"
        }))
        .bind(1i32)
        .execute(&mut *tx)
        .await?;

    // MVCC过程：
    // 1. 创建新版本（包含新的JSONB对象）
    // 2. 设置版本链
    // 3. 旧版本等待VACUUM清理

    tx.commit().await?;
    Ok(())
}
```

---

## 📝 总结

本文档详细说明了Rust数据结构与PostgreSQL表结构的映射关系。

**核心要点**：

1. **Struct映射**：
   - 基本映射规则
   - 字段类型映射
   - 嵌套结构映射

2. **Enum映射**：
   - Rust Enum到PostgreSQL枚举类型
   - 枚举类型优化

3. **Option类型**：
   - Option类型与NULL值
   - NULL值处理
   - MVCC与NULL值

4. **JSONB存储**：
   - 嵌套结构JSONB存储
   - JSONB版本管理
   - MVCC与JSONB

**下一步**：

- 深入分析Rust类型系统映射
- 探索更多数据结构映射模式
- 完善MVCC对数据结构的影响分析

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
