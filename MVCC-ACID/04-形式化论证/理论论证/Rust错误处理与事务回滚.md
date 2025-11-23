# Rust错误处理与事务回滚

> **文档编号**: RUST-PRACTICE-ERROR-001
> **主题**: Rust错误处理与PostgreSQL事务回滚
> **版本**: PostgreSQL 17 & 18
> **相关文档**:
>
> - [Rust应用故障诊断](../../02-多维度视角/运维视角/Rust应用故障诊断.md)
> - [Rust驱动PostgreSQL实践](Rust驱动PostgreSQL实践.md)
> - [Rust异步编程与MVCC交互](Rust异步编程与MVCC交互.md)

---

## 📑 目录

- [Rust错误处理与事务回滚](#rust错误处理与事务回滚)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔍 第一部分：Rust错误处理机制](#-第一部分rust错误处理机制)
    - [1.1 Result类型](#11-result类型)
    - [1.2 Error类型设计](#12-error类型设计)
    - [1.3 错误传播](#13-错误传播)
  - [🔄 第二部分：事务回滚机制](#-第二部分事务回滚机制)
    - [2.1 RAII自动回滚](#21-raii自动回滚)
    - [2.2 显式回滚](#22-显式回滚)
    - [2.3 错误与回滚映射](#23-错误与回滚映射)
  - [⚡ 第三部分：错误处理最佳实践](#-第三部分错误处理最佳实践)
    - [3.1 错误分类](#31-错误分类)
    - [3.2 错误恢复策略](#32-错误恢复策略)
    - [3.3 错误日志记录](#33-错误日志记录)
  - [📊 第四部分：MVCC与错误处理](#-第四部分mvcc与错误处理)
    - [4.1 MVCC错误场景](#41-mvcc错误场景)
    - [4.2 快照与错误处理](#42-快照与错误处理)
    - [4.3 版本链与错误恢复](#43-版本链与错误恢复)
  - [📝 总结](#-总结)

---

## 📋 概述

本文档详细说明Rust错误处理机制与PostgreSQL事务回滚的集成，包括Result类型、Error类型设计、事务回滚机制和MVCC错误处理。

**核心内容**：

- Rust错误处理机制（Result、Error类型、错误传播）
- 事务回滚机制（RAII自动回滚、显式回滚、错误映射）
- 错误处理最佳实践（错误分类、恢复策略、日志记录）
- MVCC与错误处理（错误场景、快照处理、版本链恢复）

**目标读者**：

- Rust开发者
- 数据库开发者
- 系统架构师

---

## 🔍 第一部分：Rust错误处理机制

### 1.1 Result类型

#### 1.1.1 Result基础

```rust
use sqlx::PgPool;

// Result<T, E>类型
async fn query_user(pool: &PgPool, id: i32) -> Result<User, sqlx::Error> {
    let user = sqlx::query("SELECT * FROM users WHERE id = $1")
        .bind(id)
        .fetch_one(pool)
        .await?;  // ?操作符自动传播错误

    Ok(user)
}
```

### 1.2 Error类型设计

#### 1.2.1 自定义错误类型

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum DatabaseError {
    #[error("Connection error: {0}")]
    Connection(String),

    #[error("Query error: {0}")]
    Query(String),

    #[error("Transaction error: {0}")]
    Transaction(String),

    #[error("MVCC error: {0}")]
    MVCC(String),
}

// 从sqlx::Error转换
impl From<sqlx::Error> for DatabaseError {
    fn from(err: sqlx::Error) -> Self {
        match err {
            sqlx::Error::PoolClosed => DatabaseError::Connection("Pool closed".to_string()),
            sqlx::Error::Database(e) => {
                if e.code() == Some("40001") {
                    DatabaseError::MVCC("Serialization failure".to_string())
                } else {
                    DatabaseError::Query(e.to_string())
                }
            }
            _ => DatabaseError::Query(err.to_string()),
        }
    }
}
```

### 1.3 错误传播

#### 1.3.1 错误传播链

```rust
use sqlx::PgPool;

async fn error_propagation(pool: &PgPool) -> Result<(), DatabaseError> {
    // 错误自动传播
    let mut tx = pool.begin().await?;  // 可能返回Connection错误

    sqlx::query("INSERT INTO users (id, name) VALUES ($1, $2)")
        .bind(1i32)
        .bind("Alice")
        .execute(&mut *tx)
        .await?;  // 可能返回Query错误

    tx.commit().await?;  // 可能返回Transaction错误

    Ok(())
}
```

---

## 🔄 第二部分：事务回滚机制

### 2.1 RAII自动回滚

#### 2.1.1 自动回滚

```rust
use sqlx::PgPool;

async fn auto_rollback(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    sqlx::query("INSERT INTO users (id, name) VALUES ($1, $2)")
        .bind(1i32)
        .bind("Alice")
        .execute(&mut *tx)
        .await?;

    // 如果这里返回Err，tx drop时会自动回滚（RAII）
    // 不需要显式调用rollback

    tx.commit().await?;
    Ok(())
}
```

### 2.2 显式回滚

#### 2.2.1 显式回滚场景

```rust
use sqlx::PgPool;

async fn explicit_rollback(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    let result = sqlx::query("UPDATE accounts SET balance = balance - 1000 WHERE id = $1")
        .bind(1i32)
        .execute(&mut *tx)
        .await;

    match result {
        Ok(_) => {
            // 一致性检查
            let balance: i64 = sqlx::query_scalar("SELECT balance FROM accounts WHERE id = $1")
                .bind(1i32)
                .fetch_one(&mut *tx)
                .await?;

            if balance < 0 {
                tx.rollback().await?;  // 显式回滚
                return Err(sqlx::Error::PoolClosed);
            }

            tx.commit().await?;
        }
        Err(e) => {
            tx.rollback().await?;  // 显式回滚
            return Err(e);
        }
    }

    Ok(())
}
```

### 2.3 错误与回滚映射

#### 2.3.1 错误类型映射

```rust
// 错误类型与回滚策略映射
// - Connection错误：连接池错误，不需要回滚
// - Query错误：查询错误，需要回滚
// - Transaction错误：事务错误，需要回滚
// - MVCC错误：序列化失败，需要重试
```

---

## ⚡ 第三部分：错误处理最佳实践

### 3.1 错误分类

#### 3.1.1 错误分类策略

```rust
#[derive(Error, Debug)]
pub enum DatabaseError {
    // 可重试错误
    #[error("Retryable error: {0}")]
    Retryable(String),

    // 不可重试错误
    #[error("Non-retryable error: {0}")]
    NonRetryable(String),

    // 致命错误
    #[error("Fatal error: {0}")]
    Fatal(String),
}

fn classify_error(err: &sqlx::Error) -> DatabaseError {
    match err {
        sqlx::Error::Database(e) => {
            match e.code() {
                Some("40001") | Some("40P01") => {
                    // 序列化失败或死锁，可重试
                    DatabaseError::Retryable(e.to_string())
                }
                Some("23505") => {
                    // 唯一约束违反，不可重试
                    DatabaseError::NonRetryable(e.to_string())
                }
                _ => DatabaseError::Fatal(e.to_string()),
            }
        }
        _ => DatabaseError::Fatal(err.to_string()),
    }
}
```

### 3.2 错误恢复策略

#### 3.2.1 重试机制

```rust
use sqlx::PgPool;
use std::time::Duration;
use tokio::time::sleep;

async fn retry_with_backoff<F, T>(
    pool: &PgPool,
    mut f: F,
    max_retries: usize,
) -> Result<T, DatabaseError>
where
    F: FnMut(&PgPool) -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<T, DatabaseError>> + Send>>,
{
    let mut retries = 0;
    let mut delay = Duration::from_millis(100);

    loop {
        match f(pool).await {
            Ok(result) => return Ok(result),
            Err(e) => {
                if retries >= max_retries {
                    return Err(e);
                }

                match e {
                    DatabaseError::Retryable(_) => {
                        retries += 1;
                        sleep(delay).await;
                        delay *= 2;
                    }
                    _ => return Err(e),
                }
            }
        }
    }
}
```

---

## 📊 第四部分：MVCC与错误处理

### 4.1 MVCC错误场景

#### 4.1.1 序列化失败

```rust
use sqlx::PgPool;

async fn mvcc_serialization_failure(pool: &PgPool) -> Result<(), DatabaseError> {
    let mut tx = pool.begin().await?;

    // 设置SERIALIZABLE隔离级别
    sqlx::query("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        .execute(&mut *tx)
        .await?;

    let result = sqlx::query("UPDATE accounts SET balance = balance - 100 WHERE id = $1")
        .bind(1i32)
        .execute(&mut *tx)
        .await;

    match result {
        Ok(_) => tx.commit().await?,
        Err(e) => {
            // 序列化失败（40001错误码）
            if matches!(e, sqlx::Error::Database(ref db_err) if db_err.code() == Some("40001")) {
                tx.rollback().await?;
                return Err(DatabaseError::Retryable("Serialization failure".to_string()));
            }
            tx.rollback().await?;
            return Err(DatabaseError::from(e));
        }
    }

    Ok(())
}
```

### 4.2 快照与错误处理

#### 4.2.1 快照错误处理

```rust
// MVCC快照错误处理：
// 1. 快照获取失败：连接错误，需要重连
// 2. 快照过期：事务超时，需要重试
// 3. 快照冲突：序列化失败，需要回滚并重试
```

---

## 📝 总结

本文档详细说明了Rust错误处理机制与PostgreSQL事务回滚的集成。

**核心要点**：

1. **错误处理机制**：
   - Result类型和Error类型设计
   - 错误传播链
   - 错误分类策略

2. **事务回滚**：
   - RAII自动回滚
   - 显式回滚场景
   - 错误与回滚映射

3. **最佳实践**：
   - 错误分类（可重试/不可重试/致命）
   - 错误恢复策略（重试机制）
   - 错误日志记录

4. **MVCC错误处理**：
   - MVCC错误场景（序列化失败）
   - 快照错误处理
   - 版本链错误恢复

**下一步**：

- 完善错误处理案例
- 添加更多错误恢复策略
- 完善MVCC错误处理文档

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
