# Rust集合类型与PostgreSQL数组

> **文档编号**: DESIGN-RUST-COLLECTIONS-001
> **主题**: Rust集合类型与PostgreSQL数组类型映射
> **版本**: PostgreSQL 17 & 18
> **相关文档**:
>
> - [Rust数据结构与PostgreSQL表结构映射](Rust数据结构与PostgreSQL表结构映射.md)
> - [Rust类型系统与PostgreSQL类型系统](Rust类型系统与PostgreSQL类型系统.md)

---

## 📑 目录

- [Rust集合类型与PostgreSQL数组](#rust集合类型与postgresql数组)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📦 第一部分：Rust集合类型](#-第一部分rust集合类型)
    - [1.1 Vec类型](#11-vec类型)
    - [1.1.1 Vec基础](#111-vec基础)
    - [1.2 HashMap类型](#12-hashmap类型)
    - [1.2.1 HashMap基础](#121-hashmap基础)
  - [📊 第二部分：PostgreSQL数组类型](#-第二部分postgresql数组类型)
    - [2.1 数组类型](#21-数组类型)
    - [2.1.1 数组定义](#211-数组定义)
    - [2.2 数组操作](#22-数组操作)
    - [2.2.1 数组查询](#221-数组查询)
  - [⚡ 第三部分：类型映射](#-第三部分类型映射)
    - [3.1 Vec到数组映射](#31-vec到数组映射)
    - [3.1.1 Vec映射示例](#311-vec映射示例)
    - [3.2 HashMap到JSONB映射](#32-hashmap到jsonb映射)
    - [3.2.1 HashMap映射示例](#321-hashmap映射示例)
  - [🔄 第四部分：MVCC与集合类型](#-第四部分mvcc与集合类型)
    - [4.1 数组MVCC](#41-数组mvcc)
    - [4.1.1 数组版本管理](#411-数组版本管理)
    - [4.2 JSONB MVCC](#42-jsonb-mvcc)
    - [4.2.1 JSONB版本管理](#421-jsonb版本管理)
  - [📝 总结](#-总结)

---

## 📋 概述

本文档详细说明Rust集合类型与PostgreSQL数组类型的映射关系，包括Vec、HashMap与PostgreSQL数组、JSONB的映射。

**核心内容**：

- Rust集合类型（Vec、HashMap）
- PostgreSQL数组类型（数组定义、数组操作）
- 类型映射（Vec到数组、HashMap到JSONB）
- MVCC与集合类型（数组MVCC、JSONB MVCC）

**目标读者**：

- Rust开发者
- 数据库设计人员

---

## 📦 第一部分：Rust集合类型

### 1.1 Vec类型

#### 1.1.1 Vec基础

```rust
let vec: Vec<i32> = vec![1, 2, 3, 4, 5];
```

### 1.2 HashMap类型

#### 1.2.1 HashMap基础

```rust
use std::collections::HashMap;

let mut map = HashMap::new();
map.insert("key1", "value1");
map.insert("key2", "value2");
```

---

## 📊 第二部分：PostgreSQL数组类型

### 2.1 数组类型

#### 2.1.1 数组定义

```sql
-- PostgreSQL数组类型
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tags TEXT[]  -- 文本数组
);
```

### 2.2 数组操作

#### 2.2.1 数组查询

```sql
-- 数组查询
SELECT * FROM users WHERE 'admin' = ANY(tags);
```

---

## ⚡ 第三部分：类型映射

### 3.1 Vec到数组映射

#### 3.1.1 Vec映射示例

```rust
use sqlx::PgPool;

async fn vec_to_array(pool: &PgPool) -> Result<(), sqlx::Error> {
    let tags: Vec<String> = vec!["admin".to_string(), "user".to_string()];

    sqlx::query("INSERT INTO users (id, name, tags) VALUES ($1, $2, $3)")
        .bind(1i32)
        .bind("Alice")
        .bind(&tags)  // Vec自动映射到数组
        .execute(pool)
        .await?;

    Ok(())
}
```

### 3.2 HashMap到JSONB映射

#### 3.2.1 HashMap映射示例

```rust
use sqlx::PgPool;
use sqlx::types::Json;
use std::collections::HashMap;

async fn hashmap_to_jsonb(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut metadata = HashMap::new();
    metadata.insert("role".to_string(), "admin".to_string());
    metadata.insert("department".to_string(), "IT".to_string());

    sqlx::query("INSERT INTO users (id, name, metadata) VALUES ($1, $2, $3)")
        .bind(1i32)
        .bind("Alice")
        .bind(Json(metadata))  // HashMap映射到JSONB
        .execute(pool)
        .await?;

    Ok(())
}
```

---

## 🔄 第四部分：MVCC与集合类型

### 4.1 数组MVCC

#### 4.1.1 数组版本管理

```rust
// PostgreSQL数组MVCC：
// 1. 数组作为整体版本化
// 2. UPDATE时创建新版本
// 3. 版本链中存储完整数组
```

---

## 📝 总结

本文档详细说明了Rust集合类型与PostgreSQL数组类型的映射关系。

**核心要点**：

1. **Rust集合类型**：
   - Vec、HashMap

2. **PostgreSQL数组类型**：
   - 数组定义、数组操作

3. **类型映射**：
   - Vec到数组、HashMap到JSONB

4. **MVCC与集合类型**：
   - 数组MVCC、JSONB MVCC

**下一步**：

- 完善类型映射案例
- 添加更多集合类型支持
- 完善MVCC分析文档

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
