# Rust集合类型与PostgreSQL数组

> **文档编号**: DESIGN-RUST-COLLECTIONS-001
> **主题**: Rust集合类型与PostgreSQL数组映射
> **版本**: PostgreSQL 17 & 18
> **相关文档**:
>
> - [Rust数据结构与PostgreSQL表结构映射](Rust数据结构与PostgreSQL表结构映射.md)
> - [Rust类型系统与PostgreSQL类型系统](Rust类型系统与PostgreSQL类型系统.md)
> - [Rust序列化与PostgreSQL存储](Rust序列化与PostgreSQL存储.md)

---

## 📑 目录

- [Rust集合类型与PostgreSQL数组](#rust集合类型与postgresql数组)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📊 第一部分：Rust集合类型](#-第一部分rust集合类型)
    - [1.1 Vec类型](#11-vec类型)
      - [1.1.1 Vec使用](#111-vec使用)
    - [1.2 HashMap类型](#12-hashmap类型)
      - [1.2.1 HashMap使用](#121-hashmap使用)
    - [1.3 HashSet类型](#13-hashset类型)
      - [1.3.1 HashSet使用](#131-hashset使用)
  - [🗄️ 第二部分：PostgreSQL数组](#️-第二部分postgresql数组)
    - [2.1 数组类型](#21-数组类型)
      - [2.1.1 数组定义](#211-数组定义)
    - [2.2 数组操作](#22-数组操作)
      - [2.2.1 数组查询](#221-数组查询)
  - [🔄 第三部分：类型映射](#-第三部分类型映射)
    - [3.1 Vec映射](#31-vec映射)
      - [3.1.1 Vec到数组](#311-vec到数组)
    - [3.2 序列化映射](#32-序列化映射)
      - [3.2.1 JSON映射](#321-json映射)
  - [⚡ 第四部分：MVCC与数组](#-第四部分mvcc与数组)
    - [4.1 数组版本控制](#41-数组版本控制)
      - [4.1.1 数组更新](#411-数组更新)
    - [4.2 数组并发](#42-数组并发)
      - [4.2.1 并发安全](#421-并发安全)
  - [📝 总结](#-总结)

---

## 📋 概述

本文档详细说明Rust集合类型与PostgreSQL数组的映射关系，包括类型映射、操作映射和MVCC处理。

**核心内容**：

- Rust集合类型（Vec、HashMap、HashSet）
- PostgreSQL数组（数组类型、数组操作）
- 类型映射（Vec映射、序列化映射）
- MVCC与数组（版本控制、并发安全）

**目标读者**：

- Rust开发者
- 数据库设计人员
- 系统架构师

---

## 📊 第一部分：Rust集合类型

### 1.1 Vec类型

#### 1.1.1 Vec使用

```rust
// Rust Vec类型
let tags: Vec<String> = vec!["rust".to_string(), "postgresql".to_string()];
```

### 1.2 HashMap类型

#### 1.2.1 HashMap使用

```rust
use std::collections::HashMap;

// Rust HashMap类型
let metadata: HashMap<String, String> = HashMap::from([
    ("key1".to_string(), "value1".to_string()),
    ("key2".to_string(), "value2".to_string()),
]);
```

### 1.3 HashSet类型

#### 1.3.1 HashSet使用

```rust
use std::collections::HashSet;

// Rust HashSet类型
let tags: HashSet<String> = HashSet::from([
    "rust".to_string(),
    "postgresql".to_string(),
]);
```

---

## 🗄️ 第二部分：PostgreSQL数组

### 2.1 数组类型

#### 2.1.1 数组定义

```sql
-- PostgreSQL数组类型
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT,
    tags TEXT[]  -- 文本数组
);

-- 插入数组
INSERT INTO posts (title, tags) VALUES
    ('Rust Guide', ARRAY['rust', 'programming']);
```

### 2.2 数组操作

#### 2.2.1 数组查询

```sql
-- 数组查询
SELECT * FROM posts WHERE 'rust' = ANY(tags);

-- 数组包含
SELECT * FROM posts WHERE tags @> ARRAY['rust'];
```

---

## 🔄 第三部分：类型映射

### 3.1 Vec映射

#### 3.1.1 Vec到数组

```rust
use sqlx::PgPool;

// Vec映射到PostgreSQL数组
async fn insert_tags(pool: &PgPool) -> Result<(), sqlx::Error> {
    let tags: Vec<String> = vec!["rust".to_string(), "postgresql".to_string()];

    sqlx::query("INSERT INTO posts (title, tags) VALUES ($1, $2)")
        .bind("Rust Guide")
        .bind(&tags)  // Vec自动映射到数组
        .execute(pool)
        .await?;

    Ok(())
}

// 从数组读取到Vec
async fn get_tags(pool: &PgPool) -> Result<Vec<String>, sqlx::Error> {
    let tags: Vec<String> = sqlx::query_scalar("SELECT tags FROM posts WHERE id = $1")
        .bind(1i32)
        .fetch_one(pool)
        .await?;

    Ok(tags)
}
```

### 3.2 序列化映射

#### 3.2.1 JSON映射

```rust
use serde::{Deserialize, Serialize};
use sqlx::PgPool;

#[derive(Debug, Serialize, Deserialize)]
struct Metadata {
    tags: Vec<String>,
    categories: Vec<String>,
}

// JSONB映射
async fn insert_metadata(pool: &PgPool) -> Result<(), sqlx::Error> {
    let metadata = Metadata {
        tags: vec!["rust".to_string()],
        categories: vec!["programming".to_string()],
    };

    sqlx::query("INSERT INTO posts (title, metadata) VALUES ($1, $2)")
        .bind("Rust Guide")
        .bind(serde_json::to_value(&metadata)?)  // JSONB映射
        .execute(pool)
        .await?;

    Ok(())
}
```

---

## ⚡ 第四部分：MVCC与数组

### 4.1 数组版本控制

#### 4.1.1 数组更新

```rust
use sqlx::PgPool;

// MVCC数组更新
async fn update_tags(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    // 读取当前数组
    let current_tags: Vec<String> = sqlx::query_scalar("SELECT tags FROM posts WHERE id = $1")
        .bind(1i32)
        .fetch_one(&mut *tx)
        .await?;

    // 更新数组
    let mut new_tags = current_tags;
    new_tags.push("updated".to_string());

    sqlx::query("UPDATE posts SET tags = $1 WHERE id = $2")
        .bind(&new_tags)
        .bind(1i32)
        .execute(&mut *tx)
        .await?;

    tx.commit().await?;
    Ok(())
}
```

### 4.2 数组并发

#### 4.2.1 并发安全

```rust
// MVCC数组并发安全：
// 1. 数组更新在同一事务中
// 2. MVCC保证快照一致性
// 3. 并发更新不会冲突（除非使用FOR UPDATE）
```

---

## 📝 总结

本文档详细说明了Rust集合类型与PostgreSQL数组的映射关系。

**核心要点**：

1. **Rust集合类型**：
   - Vec、HashMap、HashSet

2. **PostgreSQL数组**：
   - 数组类型、数组操作

3. **类型映射**：
   - Vec映射、序列化映射

4. **MVCC与数组**：
   - 数组版本控制、并发安全

**下一步**：

- 完善数组操作案例
- 添加更多类型映射示例
- 完善性能测试数据

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
