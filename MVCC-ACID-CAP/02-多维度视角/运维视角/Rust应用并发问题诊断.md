# Rust应用并发问题诊断

> **文档编号**: OPS-RUST-CONCURRENCY-001
> **主题**: Rust应用并发问题诊断与PostgreSQL MVCC
> **版本**: PostgreSQL 17 & 18
> **相关文档**:
>
> - [Rust应用故障诊断](Rust应用故障诊断.md)
> - [Rust应用性能故障处理](Rust应用性能故障处理.md)
> - [Rust并发原语深度对比](../../04-形式化论证/理论论证/Rust并发原语深度对比.md)

---

## 📑 目录

- [Rust应用并发问题诊断](#rust应用并发问题诊断)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔍 第一部分：数据竞争检测](#-第一部分数据竞争检测)
    - [1.1 Rust编译期数据竞争检测](#11-rust编译期数据竞争检测)
      - [1.1.1 借用检查器](#111-借用检查器)
    - [1.2 运行时数据竞争检测](#12-运行时数据竞争检测)
      - [1.2.1 ThreadSanitizer](#121-threadsanitizer)
    - [1.3 与PostgreSQL MVCC数据竞争的对比](#13-与postgresql-mvcc数据竞争的对比)
      - [1.3.1 MVCC无锁读](#131-mvcc无锁读)
  - [🔒 第二部分：死锁检测与预防](#-第二部分死锁检测与预防)
    - [2.1 Rust死锁检测](#21-rust死锁检测)
      - [2.1.1 死锁检测工具](#211-死锁检测工具)
    - [2.2 PostgreSQL死锁检测](#22-postgresql死锁检测)
      - [2.2.1 死锁检测查询](#221-死锁检测查询)
    - [2.3 死锁预防策略](#23-死锁预防策略)
      - [2.3.1 固定锁顺序](#231-固定锁顺序)
  - [⚡ 第三部分：竞态条件分析](#-第三部分竞态条件分析)
    - [3.1 竞态条件检测](#31-竞态条件检测)
      - [3.1.1 竞态条件示例](#311-竞态条件示例)
    - [3.2 与PostgreSQL并发问题的对比](#32-与postgresql并发问题的对比)
      - [3.2.1 MVCC隔离级别](#321-mvcc隔离级别)
  - [🔄 第四部分：并发问题诊断工具](#-第四部分并发问题诊断工具)
    - [4.1 Rust并发诊断工具](#41-rust并发诊断工具)
      - [4.1.1 工具列表](#411-工具列表)
    - [4.2 PostgreSQL并发诊断工具](#42-postgresql并发诊断工具)
      - [4.2.1 工具列表](#421-工具列表)
  - [📊 第五部分：并发问题案例研究](#-第五部分并发问题案例研究)
    - [5.1 数据竞争案例](#51-数据竞争案例)
    - [5.2 死锁案例](#52-死锁案例)
  - [📝 总结](#-总结)

---

## 📋 概述

本文档提供Rust应用并发问题诊断的完整指南，重点关注数据竞争、死锁和竞态条件的检测与预防，以及与PostgreSQL MVCC并发问题的对比分析。

**核心内容**：

- 数据竞争检测（编译期和运行时）
- 死锁检测与预防
- 竞态条件分析
- 并发问题诊断工具
- 并发问题案例研究

**目标读者**：

- Rust开发者
- 运维工程师
- 并发编程开发者
- SRE工程师

---

## 🔍 第一部分：数据竞争检测

### 1.1 Rust编译期数据竞争检测

#### 1.1.1 借用检查器

```rust
// Rust编译期检测数据竞争
fn data_race_example() {
    let mut data = vec![1, 2, 3];

    // ❌ 编译错误：不能同时有可变和不可变借用
    // let r1 = &data;
    // let r2 = &mut data;  // 编译错误！

    // ✅ 正确的做法：使用Mutex保护共享数据
    use std::sync::Mutex;
    let data = Mutex::new(vec![1, 2, 3]);
    let r1 = data.lock().unwrap();
    let r2 = data.lock().unwrap();  // 可以，但会等待
}
```

### 1.2 运行时数据竞争检测

#### 1.2.1 ThreadSanitizer

```rust
// 使用ThreadSanitizer检测运行时数据竞争
// 编译时添加：RUSTFLAGS="-Z sanitizer=thread" cargo test

#[test]
fn test_data_race() {
    use std::sync::Arc;
    use std::thread;

    let data = Arc::new(std::cell::RefCell::new(0));
    let data1 = Arc::clone(&data);
    let data2 = Arc::clone(&data);

    let handle1 = thread::spawn(move || {
        *data1.borrow_mut() += 1;
    });

    let handle2 = thread::spawn(move || {
        *data2.borrow_mut() += 1;
    });

    handle1.join().unwrap();
    handle2.join().unwrap();

    // ThreadSanitizer会检测到数据竞争
}
```

### 1.3 与PostgreSQL MVCC数据竞争的对比

#### 1.3.1 MVCC无锁读

```rust
// Rust编译期检测 vs PostgreSQL MVCC无锁读
// Rust：编译期避免数据竞争
// PostgreSQL：MVCC无锁读避免数据竞争

use sqlx::PgPool;

async fn mvcc_no_data_race(pool: &PgPool) -> Result<(), sqlx::Error> {
    // PostgreSQL MVCC：读操作不获取锁，无数据竞争
    let user1 = sqlx::query("SELECT * FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_one(pool)
        .await?;

    let user2 = sqlx::query("SELECT * FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_one(pool)
        .await?;

    // 两个读操作可以并发执行，无数据竞争
    Ok(())
}
```

---

## 🔒 第二部分：死锁检测与预防

### 2.1 Rust死锁检测

#### 2.1.1 死锁检测工具

```rust
use std::sync::{Mutex, Arc};
use std::thread;

// 使用deadlock检测库
fn detect_deadlock() {
    let mutex1 = Arc::new(Mutex::new(0));
    let mutex2 = Arc::new(Mutex::new(0));

    let m1 = Arc::clone(&mutex1);
    let m2 = Arc::clone(&mutex2);

    let handle1 = thread::spawn(move || {
        let _lock1 = m1.lock().unwrap();
        thread::sleep(std::time::Duration::from_secs(1));
        let _lock2 = m2.lock().unwrap();  // 可能死锁
    });

    let handle2 = thread::spawn(move || {
        let _lock2 = mutex2.lock().unwrap();
        thread::sleep(std::time::Duration::from_secs(1));
        let _lock1 = mutex1.lock().unwrap();  // 可能死锁
    });

    handle1.join().unwrap();
    handle2.join().unwrap();
}
```

### 2.2 PostgreSQL死锁检测

#### 2.2.1 死锁检测查询

```sql
-- PostgreSQL自动检测死锁
-- 检测死锁等待
SELECT
    blocked_locks.pid AS blocked_pid,
    blocking_locks.pid AS blocking_pid,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

### 2.3 死锁预防策略

#### 2.3.1 固定锁顺序

```rust
use sqlx::PgPool;

// ✅ 好的实践：固定锁顺序
async fn fixed_lock_order(pool: &PgPool, id1: i32, id2: i32) -> Result<(), sqlx::Error> {
    // 总是先锁较小的ID
    let (min_id, max_id) = if id1 < id2 {
        (id1, id2)
    } else {
        (id2, id1)
    };

    let mut tx1 = pool.begin().await?;
    sqlx::query("SELECT * FROM accounts WHERE id = $1 FOR UPDATE")
        .bind(min_id)
        .fetch_one(&mut *tx1)
        .await?;

    let mut tx2 = pool.begin().await?;
    sqlx::query("SELECT * FROM accounts WHERE id = $1 FOR UPDATE")
        .bind(max_id)
        .fetch_one(&mut *tx2)
        .await?;

    // 避免死锁
    Ok(())
}
```

---

## ⚡ 第三部分：竞态条件分析

### 3.1 竞态条件检测

#### 3.1.1 竞态条件示例

```rust
use sqlx::PgPool;
use std::sync::Arc;
use std::sync::atomic::{AtomicI32, Ordering};

// ❌ 竞态条件：非原子操作
async fn race_condition_bad(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    // 读取
    let balance: i64 = sqlx::query_scalar("SELECT balance FROM accounts WHERE id = $1")
        .bind(1i32)
        .fetch_one(&mut *tx)
        .await?;

    // 计算（可能被其他事务修改）
    let new_balance = balance - 100;

    // 写入
    sqlx::query("UPDATE accounts SET balance = $1 WHERE id = $2")
        .bind(new_balance)
        .bind(1i32)
        .execute(&mut *tx)
        .await?;

    tx.commit().await?;
    Ok(())
}

// ✅ 避免竞态条件：原子操作
async fn race_condition_good(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    // 原子更新
    sqlx::query("UPDATE accounts SET balance = balance - 100 WHERE id = $1")
        .bind(1i32)
        .execute(&mut *tx)
        .await?;

    tx.commit().await?;
    Ok(())
}
```

### 3.2 与PostgreSQL并发问题的对比

#### 3.2.1 MVCC隔离级别

```rust
// Rust并发问题 vs PostgreSQL MVCC隔离级别
// Rust：编译期避免数据竞争
// PostgreSQL：隔离级别控制并发问题

use sqlx::PgPool;

async fn isolation_levels(pool: &PgPool) -> Result<(), sqlx::Error> {
    // READ COMMITTED：避免脏读
    let mut tx1 = pool.begin().await?;
    sqlx::query("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
        .execute(&mut *tx1)
        .await?;

    // REPEATABLE READ：避免不可重复读
    let mut tx2 = pool.begin().await?;
    sqlx::query("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        .execute(&mut *tx2)
        .await?;

    // SERIALIZABLE：避免所有并发问题
    let mut tx3 = pool.begin().await?;
    sqlx::query("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        .execute(&mut *tx3)
        .await?;

    Ok(())
}
```

---

## 🔄 第四部分：并发问题诊断工具

### 4.1 Rust并发诊断工具

#### 4.1.1 工具列表

- **ThreadSanitizer**: 运行时数据竞争检测
- **Miri**: 未定义行为检测
- **deadlock**: 死锁检测库
- **loom**: 并发模型检查

### 4.2 PostgreSQL并发诊断工具

#### 4.2.1 工具列表

- **pg_locks**: 锁监控
- **pg_stat_activity**: 活动连接监控
- **deadlock_timeout**: 死锁检测超时
- **log_lock_waits**: 锁等待日志

---

## 📊 第五部分：并发问题案例研究

### 5.1 数据竞争案例

```rust
// 案例：多线程修改共享数据
// 问题：数据竞争导致数据不一致
// 解决：使用Mutex保护共享数据
```

### 5.2 死锁案例

```rust
// 案例：两个事务互相等待锁
// 问题：死锁导致事务无法完成
// 解决：固定锁顺序
```

---

## 📝 总结

本文档提供了Rust应用并发问题诊断的完整指南，重点关注数据竞争、死锁和竞态条件的检测与预防。

**核心要点**：

1. **数据竞争检测**：
   - Rust编译期检测
   - 运行时检测工具
   - 与MVCC对比

2. **死锁检测**：
   - Rust死锁检测
   - PostgreSQL死锁检测
   - 死锁预防策略

3. **竞态条件**：
   - 竞态条件检测
   - 与PostgreSQL并发问题对比
   - 竞态条件预防

4. **诊断工具**：
   - Rust并发诊断工具
   - PostgreSQL并发诊断工具
   - 集成诊断方案

**下一步**：

- 添加更多并发问题案例
- 完善诊断工具使用指南
- 完善预防策略文档

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
