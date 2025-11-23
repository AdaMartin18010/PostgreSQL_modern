# Rust类型系统与PostgreSQL类型系统

> **文档编号**: DESIGN-RUST-TYPESYSTEM-001
> **主题**: Rust类型系统与PostgreSQL类型系统映射
> **版本**: PostgreSQL 17 & 18
> **相关文档**:
>
> - [Rust数据结构与PostgreSQL表结构映射](Rust数据结构与PostgreSQL表结构映射.md)
> - [Rust序列化与PostgreSQL存储](Rust序列化与PostgreSQL存储.md)

---

## 📑 目录

- [Rust类型系统与PostgreSQL类型系统](#rust类型系统与postgresql类型系统)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔢 第一部分：基本类型映射](#-第一部分基本类型映射)
    - [1.1 整数类型](#11-整数类型)
    - [1.2 浮点数类型](#12-浮点数类型)
    - [1.3 字符串类型](#13-字符串类型)
    - [1.4 布尔类型](#14-布尔类型)
  - [📅 第二部分：时间类型映射](#-第二部分时间类型映射)
    - [2.1 时间戳类型](#21-时间戳类型)
    - [2.2 日期类型](#22-日期类型)
    - [2.3 时间间隔类型](#23-时间间隔类型)
  - [📦 第三部分：复合类型映射](#-第三部分复合类型映射)
    - [3.1 Option类型](#31-option类型)
    - [3.2 Vec类型](#32-vec类型)
    - [3.3 HashMap类型](#33-hashmap类型)
  - [🔗 第四部分：自定义类型映射](#-第四部分自定义类型映射)
    - [4.1 Enum类型](#41-enum类型)
    - [4.2 Struct类型](#42-struct类型)
    - [4.3 新类型模式](#43-新类型模式)
  - [⚡ 第五部分：类型安全保证](#-第五部分类型安全保证)
    - [5.1 编译期类型检查](#51-编译期类型检查)
    - [5.2 运行时类型验证](#52-运行时类型验证)
    - [5.3 MVCC类型一致性](#53-mvcc类型一致性)
  - [📝 总结](#-总结)

---

## 📋 概述

本文档详细说明Rust类型系统与PostgreSQL类型系统的映射关系，包括基本类型、时间类型、复合类型和自定义类型的映射规则，以及MVCC对类型系统的影响。

**核心内容**：

- 基本类型映射（整数、浮点数、字符串、布尔）
- 时间类型映射
- 复合类型映射（Option、Vec、HashMap）
- 自定义类型映射（Enum、Struct）
- 类型安全保证和MVCC类型一致性

**目标读者**：

- Rust开发者
- 数据库设计人员
- 类型系统研究者

---

## 🔢 第一部分：基本类型映射

### 1.1 整数类型

#### 1.1.1 整数类型映射

| Rust类型 | PostgreSQL类型 | 范围 | MVCC影响 |
|---------|---------------|------|---------|
| `i8` | `SMALLINT` | -128 to 127 | 无影响 |
| `i16` | `SMALLINT` | -32768 to 32767 | 无影响 |
| `i32` | `INTEGER` | -2^31 to 2^31-1 | 无影响 |
| `i64` | `BIGINT` | -2^63 to 2^63-1 | 无影响 |
| `u8` | `SMALLINT` | 0 to 255 | 无影响 |
| `u16` | `SMALLINT` | 0 to 65535 | 无影响 |
| `u32` | `INTEGER` | 0 to 2^32-1 | 无影响 |
| `u64` | `BIGINT` | 0 to 2^64-1 | 无影响 |

```rust
use sqlx::PgPool;

async fn integer_types(pool: &PgPool) -> Result<(), sqlx::Error> {
    let id: i32 = sqlx::query_scalar("SELECT id FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_one(pool)
        .await?;

    let count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM users")
        .fetch_one(pool)
        .await?;

    Ok(())
}
```

### 1.2 浮点数类型

#### 1.2.1 浮点数类型映射

| Rust类型 | PostgreSQL类型 | 精度 | MVCC影响 |
|---------|---------------|------|---------|
| `f32` | `REAL` | 6位小数 | 无影响 |
| `f64` | `DOUBLE PRECISION` | 15位小数 | 无影响 |

### 1.3 字符串类型

#### 1.3.1 字符串类型映射

| Rust类型 | PostgreSQL类型 | MVCC影响 |
|---------|---------------|---------|
| `String` | `TEXT` | 可能触发TOAST |
| `&str` | `TEXT` | 可能触发TOAST |
| `Vec<u8>` | `BYTEA` | 可能触发TOAST |

### 1.4 布尔类型

#### 1.4.1 布尔类型映射

```rust
use sqlx::PgPool;

async fn boolean_types(pool: &PgPool) -> Result<(), sqlx::Error> {
    let is_active: bool = sqlx::query_scalar("SELECT is_active FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_one(pool)
        .await?;

    Ok(())
}
```

---

## 📅 第二部分：时间类型映射

### 2.1 时间戳类型

#### 2.1.1 时间戳映射

| Rust类型 | PostgreSQL类型 | MVCC影响 |
|---------|---------------|---------|
| `chrono::DateTime<Utc>` | `TIMESTAMP WITH TIME ZONE` | 时间戳比较 |
| `chrono::NaiveDateTime` | `TIMESTAMP WITHOUT TIME ZONE` | 时间戳比较 |

```rust
use chrono::{DateTime, Utc};
use sqlx::PgPool;

async fn timestamp_types(pool: &PgPool) -> Result<(), sqlx::Error> {
    let created_at: DateTime<Utc> = sqlx::query_scalar("SELECT created_at FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_one(pool)
        .await?;

    Ok(())
}
```

---

## 📦 第三部分：复合类型映射

### 3.1 Option类型

#### 3.1.1 Option映射

```rust
use sqlx::PgPool;

async fn option_types(pool: &PgPool) -> Result<(), sqlx::Error> {
    // Option<T> 映射到 PostgreSQL NULL
    let email: Option<String> = sqlx::query_scalar("SELECT email FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_optional(pool)
        .await?;

    match email {
        Some(e) => println!("Email: {}", e),
        None => println!("No email"),
    }

    Ok(())
}
```

### 3.2 Vec类型

#### 3.2.1 Vec映射

```rust
// Vec<T> 映射到 PostgreSQL 数组类型
use sqlx::PgPool;

async fn vec_types(pool: &PgPool) -> Result<(), sqlx::Error> {
    let tags: Vec<String> = sqlx::query_scalar("SELECT tags FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_one(pool)
        .await?;

    Ok(())
}
```

---

## 🔗 第四部分：自定义类型映射

### 4.1 Enum类型

#### 4.1.1 Enum映射

```rust
use sqlx::{PgPool, Type, FromRow};

#[derive(Debug, Clone, Copy, Type)]
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

// PostgreSQL枚举类型
// CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
```

### 4.2 Struct类型

#### 4.2.1 Struct映射

```rust
use sqlx::FromRow;

#[derive(FromRow)]
struct User {
    id: i32,
    name: String,
    email: String,
}

// 映射到PostgreSQL表结构
// CREATE TABLE users (
//     id INTEGER PRIMARY KEY,
//     name TEXT NOT NULL,
//     email TEXT NOT NULL
// );
```

---

## ⚡ 第五部分：类型安全保证

### 5.1 编译期类型检查

#### 5.1.1 类型安全

```rust
use sqlx::PgPool;

// ✅ Rust编译期类型检查
async fn type_safe_query(pool: &PgPool) -> Result<(), sqlx::Error> {
    let id: i32 = sqlx::query_scalar("SELECT id FROM users WHERE id = $1")
        .bind(1i32)  // 类型匹配
        .fetch_one(pool)
        .await?;

    // ❌ 编译错误：类型不匹配
    // let id: i32 = sqlx::query_scalar("SELECT id FROM users WHERE id = $1")
    //     .bind("wrong")  // 编译错误！
    //     .fetch_one(pool)
    //     .await?;

    Ok(())
}
```

### 5.3 MVCC类型一致性

#### 5.3.1 类型一致性保证

```rust
// MVCC保证类型一致性：
// 1. 同一事务内，类型保持一致
// 2. 版本链中，类型保持一致
// 3. 查询时，使用快照保证类型一致性

use sqlx::PgPool;

async fn mvcc_type_consistency(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    // 查询1：获取类型
    let user: User = sqlx::query_as("SELECT * FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_one(&mut *tx)
        .await?;

    // 查询2：类型保持一致（使用相同快照）
    let user2: User = sqlx::query_as("SELECT * FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_one(&mut *tx)
        .await?;

    tx.commit().await?;
    Ok(())
}
```

---

## 📝 总结

本文档详细说明了Rust类型系统与PostgreSQL类型系统的映射关系。

**核心要点**：

1. **基本类型映射**：
   - 整数、浮点数、字符串、布尔类型
   - 类型范围和精度

2. **时间类型映射**：
   - 时间戳、日期、时间间隔类型

3. **复合类型映射**：
   - Option、Vec、HashMap类型

4. **自定义类型映射**：
   - Enum、Struct、新类型模式

5. **类型安全保证**：
   - 编译期类型检查
   - 运行时类型验证
   - MVCC类型一致性

**下一步**：

- 深入分析类型系统优化
- 探索更多类型映射模式
- 完善MVCC类型一致性分析

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
