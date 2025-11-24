# Rust应用故障诊断

> **文档编号**: OPS-RUST-TROUBLESHOOTING-001
> **主题**: Rust应用故障诊断与PostgreSQL MVCC
> **版本**: PostgreSQL 17 & 18
> **相关文档**:
>
> - [故障分类和诊断](故障分类和诊断.md)
> - [常见故障处理](常见故障处理.md)
> - [Rust应用并发监控指标](Rust应用并发监控指标.md)
> - [Rust并发模式最佳实践](../../04-形式化论证/理论论证/Rust并发模式最佳实践.md)

---

## 📑 目录

- [Rust应用故障诊断](#rust应用故障诊断)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔍 第一部分：Panic分析与事务回滚](#-第一部分panic分析与事务回滚)
    - [1.1 Panic检测与处理](#11-panic检测与处理)
      - [1.1.1 Panic捕获](#111-panic捕获)
    - [1.2 Panic与事务回滚](#12-panic与事务回滚)
      - [1.2.1 RAII自动回滚](#121-raii自动回滚)
    - [1.3 事务一致性保证](#13-事务一致性保证)
      - [1.3.1 一致性检查](#131-一致性检查)
  - [🔒 第二部分：死锁诊断](#-第二部分死锁诊断)
    - [2.1 Rust死锁检测](#21-rust死锁检测)
      - [2.1.1 死锁检测工具](#211-死锁检测工具)
    - [2.2 PostgreSQL死锁关联](#22-postgresql死锁关联)
      - [2.2.1 死锁检测查询](#221-死锁检测查询)
    - [2.3 死锁预防策略](#23-死锁预防策略)
      - [2.3.1 锁顺序策略](#231-锁顺序策略)
  - [💾 第三部分：内存泄漏诊断](#-第三部分内存泄漏诊断)
    - [3.1 Rust内存泄漏检测](#31-rust内存泄漏检测)
      - [3.1.1 内存泄漏检测工具](#311-内存泄漏检测工具)
    - [3.2 MVCC版本链泄漏对比](#32-mvcc版本链泄漏对比)
      - [3.2.1 版本链泄漏检测](#321-版本链泄漏检测)
    - [3.3 内存管理最佳实践](#33-内存管理最佳实践)
      - [3.3.1 RAII模式](#331-raii模式)
  - [⚡ 第四部分：性能故障诊断](#-第四部分性能故障诊断)
    - [4.1 性能下降诊断](#41-性能下降诊断)
      - [4.1.1 性能指标监控](#411-性能指标监控)
    - [4.2 与PostgreSQL MVCC性能问题的关联](#42-与postgresql-mvcc性能问题的关联)
      - [4.2.1 MVCC性能问题诊断](#421-mvcc性能问题诊断)
    - [4.3 性能优化策略](#43-性能优化策略)
      - [4.3.1 查询优化](#431-查询优化)
  - [🔄 第五部分：故障恢复策略](#-第五部分故障恢复策略)
    - [5.1 自动恢复机制](#51-自动恢复机制)
      - [5.1.1 重试机制](#511-重试机制)
    - [5.2 手动恢复流程](#52-手动恢复流程)
      - [5.2.1 恢复步骤](#521-恢复步骤)
    - [5.3 数据一致性恢复](#53-数据一致性恢复)
      - [5.3.1 一致性检查](#531-一致性检查)
  - [📊 第六部分：诊断工具](#-第六部分诊断工具)
    - [6.1 Rust诊断工具](#61-rust诊断工具)
      - [6.1.1 工具列表](#611-工具列表)
    - [6.2 PostgreSQL诊断工具](#62-postgresql诊断工具)
      - [6.2.1 工具列表](#621-工具列表)
    - [6.3 集成诊断方案](#63-集成诊断方案)
      - [6.3.1 统一诊断平台](#631-统一诊断平台)
  - [📝 总结](#-总结)

---

## 📋 概述

本文档提供Rust应用故障诊断的完整指南，重点关注与PostgreSQL MVCC相关的故障场景，包括panic处理、死锁诊断、内存泄漏检测和性能故障分析。

**核心内容**：

- Panic分析与事务回滚
- 死锁诊断与PostgreSQL死锁关联
- 内存泄漏检测与MVCC版本链泄漏对比
- 性能故障诊断与优化策略
- 故障恢复策略
- 诊断工具使用

**目标读者**：

- 运维工程师
- Rust开发者
- SRE工程师
- 系统架构师

---

## 🔍 第一部分：Panic分析与事务回滚

### 1.1 Panic检测与处理

#### 1.1.1 Panic捕获

```rust
use sqlx::PgPool;
use std::panic;

async fn panic_handler(pool: &PgPool) {
    // 设置panic hook
    panic::set_hook(Box::new(|panic_info| {
        eprintln!("Panic occurred: {:?}", panic_info);
        // 记录panic信息
        // 发送告警
    }));

    // 使用catch_unwind捕获panic
    let result = panic::catch_unwind(|| {
        // 可能panic的代码
        // ...
    });

    match result {
        Ok(_) => {}
        Err(_) => {
            // 处理panic
            // 回滚事务
        }
    }
}
```

### 1.2 Panic与事务回滚

#### 1.2.1 RAII自动回滚

```rust
use sqlx::PgPool;

async fn panic_with_transaction(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    sqlx::query("INSERT INTO users (id, name) VALUES ($1, $2)")
        .bind(1i32)
        .bind("Alice")
        .execute(&mut *tx)
        .await?;

    // 如果这里panic，事务会自动回滚（RAII）
    // tx drop时会自动调用rollback

    // 显式处理panic
    let result = panic::catch_unwind(panic::AssertUnwindSafe(|| {
        // 可能panic的操作
    }));

    match result {
        Ok(_) => tx.commit().await?,
        Err(_) => {
            tx.rollback().await?;
            return Err(sqlx::Error::PoolClosed);
        }
    }

    Ok(())
}
```

### 1.3 事务一致性保证

#### 1.3.1 一致性检查

```rust
use sqlx::PgPool;

async fn consistency_check(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    // 操作1
    sqlx::query("INSERT INTO users (id, name) VALUES ($1, $2)")
        .bind(1i32)
        .bind("Alice")
        .execute(&mut *tx)
        .await?;

    // 操作2（可能失败）
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
                tx.rollback().await?;
                return Err(sqlx::Error::PoolClosed);
            }

            tx.commit().await?;
        }
        Err(e) => {
            tx.rollback().await?;
            return Err(e);
        }
    }

    Ok(())
}
```

---

## 🔒 第二部分：死锁诊断

### 2.1 Rust死锁检测

#### 2.1.1 死锁检测工具

```rust
use std::sync::{Mutex, Arc};
use std::thread;

// 使用deadlock检测库
#[cfg(feature = "deadlock_detection")]
fn detect_deadlock() {
    // 检测Mutex死锁
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

### 2.2 PostgreSQL死锁关联

#### 2.2.1 死锁检测查询

```sql
-- 检测PostgreSQL死锁
SELECT
    blocked_locks.pid AS blocked_pid,
    blocking_locks.pid AS blocking_pid,
    blocked_activity.usename AS blocked_user,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

### 2.3 死锁预防策略

#### 2.3.1 锁顺序策略

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

## 💾 第三部分：内存泄漏诊断

### 3.1 Rust内存泄漏检测

#### 3.1.1 内存泄漏检测工具

```rust
// 使用valgrind或AddressSanitizer检测内存泄漏
// 或使用Rust的内存分析工具

use std::alloc::{GlobalAlloc, Layout, System};
use std::sync::atomic::{AtomicUsize, Ordering};

struct LeakDetector;

static ALLOCATED: AtomicUsize = AtomicUsize::new(0);

unsafe impl GlobalAlloc for LeakDetector {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let ptr = System.alloc(layout);
        if !ptr.is_null() {
            ALLOCATED.fetch_add(layout.size(), Ordering::Relaxed);
        }
        ptr
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        System.dealloc(ptr, layout);
        ALLOCATED.fetch_sub(layout.size(), Ordering::Relaxed);
    }
}

#[global_allocator]
static GLOBAL: LeakDetector = LeakDetector;

// 检查内存泄漏
fn check_memory_leak() {
    let allocated = ALLOCATED.load(Ordering::Relaxed);
    if allocated > 0 {
        eprintln!("Potential memory leak: {} bytes allocated", allocated);
    }
}
```

### 3.2 MVCC版本链泄漏对比

#### 3.2.1 版本链泄漏检测

```sql
-- 检测表膨胀（MVCC版本链泄漏）
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_tuple_percent,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### 3.3 内存管理最佳实践

#### 3.3.1 RAII模式

```rust
use sqlx::PgPool;

// ✅ Rust RAII自动管理内存
async fn raii_memory_management(pool: &PgPool) -> Result<(), sqlx::Error> {
    {
        let mut tx = pool.begin().await?;
        // tx在作用域结束时自动drop，释放资源

        sqlx::query("SELECT * FROM users")
            .fetch_all(&mut *tx)
            .await?;

        tx.commit().await?;
    }  // tx在这里自动drop

    Ok(())
}
```

---

## ⚡ 第四部分：性能故障诊断

### 4.1 性能下降诊断

#### 4.1.1 性能指标监控

```rust
use std::time::Instant;
use sqlx::PgPool;

async fn performance_monitoring(pool: &PgPool) -> Result<(), sqlx::Error> {
    let start = Instant::now();

    // 执行查询
    let rows = sqlx::query("SELECT * FROM users")
        .fetch_all(pool)
        .await?;

    let elapsed = start.elapsed();

    // 记录性能指标
    if elapsed.as_millis() > 1000 {
        eprintln!("Slow query detected: {}ms", elapsed.as_millis());
        // 发送告警
    }

    Ok(())
}
```

### 4.2 与PostgreSQL MVCC性能问题的关联

#### 4.2.1 MVCC性能问题诊断

```sql
-- 检测长事务（影响MVCC性能）
SELECT
    pid,
    usename,
    application_name,
    state,
    now() - xact_start AS transaction_duration,
    now() - query_start AS query_duration,
    query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - xact_start > interval '60 seconds'
ORDER BY transaction_duration DESC;

-- 检测表膨胀
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

### 4.3 性能优化策略

#### 4.3.1 查询优化

```rust
use sqlx::PgPool;

// ✅ 使用索引列过滤
async fn optimized_query(pool: &PgPool) -> Result<(), sqlx::Error> {
    let user = sqlx::query("SELECT * FROM users WHERE id = $1")
        .bind(1i32)
        .fetch_one(pool)
        .await?;

    Ok(())
}

// ✅ 限制结果集大小
async fn limited_query(pool: &PgPool) -> Result<(), sqlx::Error> {
    let users = sqlx::query("SELECT * FROM users LIMIT 100")
        .fetch_all(pool)
        .await?;

    Ok(())
}
```

---

## 🔄 第五部分：故障恢复策略

### 5.1 自动恢复机制

#### 5.1.1 重试机制

```rust
use sqlx::PgPool;
use std::time::Duration;
use tokio::time::sleep;

async fn retry_with_backoff<F, T>(
    pool: &PgPool,
    mut f: F,
    max_retries: usize,
) -> Result<T, sqlx::Error>
where
    F: FnMut(&PgPool) -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<T, sqlx::Error>> + Send>>,
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

                if is_retryable(&e) {
                    retries += 1;
                    sleep(delay).await;
                    delay *= 2;
                } else {
                    return Err(e);
                }
            }
        }
    }
}

fn is_retryable(error: &sqlx::Error) -> bool {
    match error {
        sqlx::Error::Database(e) => {
            matches!(e.code(), Some("40001") | Some("40P01"))
        }
        _ => false,
    }
}
```

### 5.2 手动恢复流程

#### 5.2.1 恢复步骤

```rust
// 1. 检测故障
// 2. 记录故障信息
// 3. 尝试自动恢复
// 4. 如果失败，执行手动恢复
// 5. 验证数据一致性
// 6. 恢复服务
```

### 5.3 数据一致性恢复

#### 5.3.1 一致性检查

```sql
-- 检查数据一致性
SELECT
    COUNT(*) as total_users,
    SUM(balance) as total_balance
FROM users;

-- 检查外键一致性
SELECT
    COUNT(*) as orphaned_orders
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE u.id IS NULL;
```

---

## 📊 第六部分：诊断工具

### 6.1 Rust诊断工具

#### 6.1.1 工具列表

- **perf**: Linux性能分析工具
- **flamegraph**: 火焰图生成工具
- **valgrind**: 内存泄漏检测
- **AddressSanitizer**: 内存错误检测
- **cargo-flamegraph**: Rust火焰图工具

### 6.2 PostgreSQL诊断工具

#### 6.2.1 工具列表

- **pg_stat_statements**: 查询统计
- **pg_stat_activity**: 活动连接监控
- **pg_locks**: 锁监控
- **EXPLAIN ANALYZE**: 查询计划分析

### 6.3 集成诊断方案

#### 6.3.1 统一诊断平台

```rust
// 集成Rust和PostgreSQL诊断工具
// 提供统一的诊断接口
// 自动关联Rust应用故障和PostgreSQL MVCC问题
```

---

## 📝 总结

本文档提供了Rust应用故障诊断的完整指南，重点关注与PostgreSQL MVCC相关的故障场景。

**核心要点**：

1. **Panic处理**：
   - Panic检测与捕获
   - 事务自动回滚
   - 一致性保证

2. **死锁诊断**：
   - Rust死锁检测
   - PostgreSQL死锁关联
   - 死锁预防策略

3. **内存泄漏**：
   - Rust内存泄漏检测
   - MVCC版本链泄漏对比
   - 内存管理最佳实践

4. **性能故障**：
   - 性能下降诊断
   - MVCC性能问题关联
   - 性能优化策略

5. **故障恢复**：
   - 自动恢复机制
   - 手动恢复流程
   - 数据一致性恢复

**下一步**：

- 完善诊断工具集成
- 添加更多故障案例
- 完善恢复策略文档

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
