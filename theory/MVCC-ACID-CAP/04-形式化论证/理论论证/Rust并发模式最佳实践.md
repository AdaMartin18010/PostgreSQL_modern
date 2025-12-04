# Rust并发模式最佳实践

> **文档编号**: RUST-PRACTICE-PATTERNS-001
> **主题**: Rust并发模式与PostgreSQL MVCC最佳实践
> **版本**: PostgreSQL 17 & 18
> **相关文档**:
>
> - [PostgreSQL MVCC与Rust并发模型同构性论证](PostgreSQL-MVCC与Rust并发模型同构性论证.md)
> - [Rust并发原语深度对比](Rust并发原语深度对比.md)
> - [Rust驱动PostgreSQL实践](Rust驱动PostgreSQL实践.md)

---

## 📑 目录

- [Rust并发模式最佳实践](#rust并发模式最佳实践)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔧 第一部分：并发模式设计原则](#-第一部分并发模式设计原则)
    - [1.1 所有权与生命周期管理](#11-所有权与生命周期管理)
      - [1.1.1 连接所有权模式](#111-连接所有权模式)
      - [1.1.2 事务生命周期管理](#112-事务生命周期管理)
    - [1.2 并发安全保证](#12-并发安全保证)
      - [1.2.1 Send + Sync保证](#121-send--sync保证)
      - [1.2.2 无数据竞争保证](#122-无数据竞争保证)
    - [1.3 性能优化原则](#13-性能优化原则)
      - [1.3.1 零成本抽象](#131-零成本抽象)
      - [1.3.2 异步优先](#132-异步优先)
  - [🚀 第二部分：常见并发模式](#-第二部分常见并发模式)
    - [2.1 Actor模式](#21-actor模式)
      - [2.1.1 Actor实现](#211-actor实现)
    - [2.2 工作窃取模式](#22-工作窃取模式)
      - [2.2.1 工作队列实现](#221-工作队列实现)
    - [2.3 生产者-消费者模式](#23-生产者-消费者模式)
      - [2.3.1 生产者-消费者实现](#231-生产者-消费者实现)
    - [2.4 扇出-扇入模式](#24-扇出-扇入模式)
      - [2.4.1 扇出-扇入实现](#241-扇出-扇入实现)
  - [🔗 第三部分：PostgreSQL MVCC集成模式](#-第三部分postgresql-mvcc集成模式)
    - [3.1 连接池模式](#31-连接池模式)
      - [3.1.1 连接池配置](#311-连接池配置)
    - [3.2 事务管理模式](#32-事务管理模式)
      - [3.2.1 事务装饰器模式](#321-事务装饰器模式)
    - [3.3 查询优化模式](#33-查询优化模式)
      - [3.3.1 查询缓存模式](#331-查询缓存模式)
    - [3.4 错误处理模式](#34-错误处理模式)
      - [3.4.1 错误分类处理](#341-错误分类处理)
  - [⚡ 第四部分：性能优化模式](#-第四部分性能优化模式)
    - [4.1 批量操作模式](#41-批量操作模式)
      - [4.1.1 批量插入](#411-批量插入)
    - [4.2 异步I/O模式](#42-异步io模式)
      - [4.2.1 并发查询](#421-并发查询)
    - [4.3 缓存模式](#43-缓存模式)
      - [4.3.1 多级缓存](#431-多级缓存)
  - [🛡️ 第五部分：错误处理与恢复模式](#️-第五部分错误处理与恢复模式)
    - [5.1 重试模式](#51-重试模式)
      - [5.1.1 指数退避重试](#511-指数退避重试)
    - [5.2 断路器模式](#52-断路器模式)
      - [5.2.1 断路器实现](#521-断路器实现)
  - [📊 第六部分：监控与可观测性模式](#-第六部分监控与可观测性模式)
    - [6.1 指标收集模式](#61-指标收集模式)
      - [6.1.1 指标收集器](#611-指标收集器)
  - [🎯 第七部分：最佳实践总结](#-第七部分最佳实践总结)
    - [7.1 模式选择指南](#71-模式选择指南)
    - [7.2 常见陷阱避免](#72-常见陷阱避免)
      - [7.2.1 长事务陷阱](#721-长事务陷阱)
    - [7.3 性能调优建议](#73-性能调优建议)
  - [📝 总结](#-总结)

---

## 📋 概述

本文档提供Rust并发模式与PostgreSQL MVCC集成的最佳实践，涵盖常见并发模式、性能优化策略、错误处理机制和监控方案，帮助开发者构建高性能、可靠的数据库应用。

**核心内容**：

- Rust并发模式设计原则
- 常见并发模式实现
- PostgreSQL MVCC集成模式
- 性能优化模式
- 错误处理与恢复模式
- 监控与可观测性模式
- 最佳实践总结

**目标读者**：

- Rust开发者
- PostgreSQL开发者
- 系统架构师
- 性能优化工程师

---

## 🔧 第一部分：并发模式设计原则

### 1.1 所有权与生命周期管理

#### 1.1.1 连接所有权模式

```rust
use sqlx::PgPool;
use std::sync::Arc;

// ✅ 好的实践：使用Arc共享连接池
struct AppState {
    pool: Arc<PgPool>,
}

impl AppState {
    fn new(pool: PgPool) -> Self {
        Self {
            pool: Arc::new(pool),
        }
    }

    fn get_pool(&self) -> Arc<PgPool> {
        Arc::clone(&self.pool)
    }
}

// 多个处理器共享连接池
let state = AppState::new(pool);
let state1 = state.clone();
let state2 = state.clone();
```

#### 1.1.2 事务生命周期管理

```rust
use sqlx::PgPool;

// ✅ 好的实践：RAII模式管理事务
async fn transaction_with_raii(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    // 执行操作
    sqlx::query("INSERT INTO users (id, name) VALUES ($1, $2)")
        .bind(1i32)
        .bind("Alice")
        .execute(&mut *tx)
        .await?;

    // tx drop时自动回滚（如果未提交）
    tx.commit().await?;
    Ok(())
}
```

### 1.2 并发安全保证

#### 1.2.1 Send + Sync保证

```rust
use sqlx::PgPool;
use std::sync::Arc;

// ✅ PgPool是Send + Sync的
fn spawn_task(pool: Arc<PgPool>) {
    tokio::spawn(async move {
        // 可以在不同线程间传递
        let row = sqlx::query("SELECT * FROM users")
            .fetch_one(&*pool)
            .await
            .unwrap();
    });
}
```

#### 1.2.2 无数据竞争保证

```rust
use sqlx::PgPool;
use std::sync::Arc;

// ✅ Rust编译期保证无数据竞争
async fn concurrent_queries(pool: Arc<PgPool>) -> Result<(), sqlx::Error> {
    let mut handles = vec![];

    for i in 0..10 {
        let pool = Arc::clone(&pool);
        let handle = tokio::spawn(async move {
            // 每个任务有独立的查询，无数据竞争
            sqlx::query("SELECT COUNT(*) FROM users")
                .fetch_one(&*pool)
                .await
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.await??;
    }

    Ok(())
}
```

### 1.3 性能优化原则

#### 1.3.1 零成本抽象

```rust
// ✅ Rust零成本抽象：编译时优化
let pool = Arc::new(pool);
// Arc::clone只是增加引用计数，不复制数据
```

#### 1.3.2 异步优先

```rust
// ✅ 使用异步I/O，避免阻塞
async fn async_query(pool: &PgPool) -> Result<(), sqlx::Error> {
    // 异步查询，不阻塞线程
    sqlx::query("SELECT * FROM users")
        .fetch_all(pool)
        .await?;
    Ok(())
}
```

---

## 🚀 第二部分：常见并发模式

### 2.1 Actor模式

#### 2.1.1 Actor实现

```rust
use sqlx::PgPool;
use tokio::sync::mpsc;
use std::sync::Arc;

enum Message {
    Query(String),
    Update(i32, String),
}

struct DatabaseActor {
    pool: Arc<PgPool>,
    receiver: mpsc::Receiver<Message>,
}

impl DatabaseActor {
    async fn run(mut self) {
        while let Some(msg) = self.receiver.recv().await {
            match msg {
                Message::Query(query) => {
                    let _ = sqlx::query(&query)
                        .fetch_all(&*self.pool)
                        .await;
                }
                Message::Update(id, name) => {
                    let _ = sqlx::query("UPDATE users SET name = $1 WHERE id = $2")
                        .bind(name)
                        .bind(id)
                        .execute(&*self.pool)
                        .await;
                }
            }
        }
    }
}

// 使用Actor模式
let (tx, rx) = mpsc::channel(100);
let actor = DatabaseActor {
    pool: Arc::clone(&pool),
    receiver: rx,
};

tokio::spawn(actor.run());

// 发送消息
tx.send(Message::Query("SELECT * FROM users".to_string())).await?;
```

### 2.2 工作窃取模式

#### 2.2.1 工作队列实现

```rust
use sqlx::PgPool;
use tokio::sync::mpsc;
use std::sync::Arc;

async fn worker_pool(pool: Arc<PgPool>, num_workers: usize) {
    let (tx, mut rx) = mpsc::unbounded_channel::<String>();

    // 创建工作线程
    for _ in 0..num_workers {
        let pool = Arc::clone(&pool);
        let mut rx = rx.clone();

        tokio::spawn(async move {
            while let Some(query) = rx.recv().await {
                // 执行查询
                let _ = sqlx::query(&query)
                    .fetch_all(&*pool)
                    .await;
            }
        });
    }

    // 分发任务
    for i in 0..100 {
        tx.send(format!("SELECT * FROM users WHERE id = {}", i)).unwrap();
    }
}
```

### 2.3 生产者-消费者模式

#### 2.3.1 生产者-消费者实现

```rust
use sqlx::PgPool;
use tokio::sync::mpsc;
use std::sync::Arc;

async fn producer_consumer(pool: Arc<PgPool>) {
    let (tx, mut rx) = mpsc::channel(100);

    // 生产者
    let producer = tokio::spawn(async move {
        for i in 0..100 {
            tx.send(i).await.unwrap();
        }
    });

    // 消费者
    let consumer = tokio::spawn(async move {
        while let Some(id) = rx.recv().await {
            // 处理数据
            let _ = sqlx::query("SELECT * FROM users WHERE id = $1")
                .bind(id)
                .fetch_one(&*pool)
                .await;
        }
    });

    producer.await.unwrap();
    consumer.await.unwrap();
}
```

### 2.4 扇出-扇入模式

#### 2.4.1 扇出-扇入实现

```rust
use sqlx::PgPool;
use tokio::sync::mpsc;
use std::sync::Arc;

async fn fan_out_fan_in(pool: Arc<PgPool>) {
    let (tx, mut rx) = mpsc::unbounded_channel();

    // 扇出：多个生产者
    for i in 0..10 {
        let tx = tx.clone();
        tokio::spawn(async move {
            for j in 0..10 {
                tx.send(i * 10 + j).unwrap();
            }
        });
    }
    drop(tx);

    // 扇入：单个消费者
    let mut results = Vec::new();
    while let Some(id) = rx.recv().await {
        let row = sqlx::query("SELECT * FROM users WHERE id = $1")
            .bind(id)
            .fetch_one(&*pool)
            .await
            .unwrap();
        results.push(row);
    }
}
```

---

## 🔗 第三部分：PostgreSQL MVCC集成模式

### 3.1 连接池模式

#### 3.1.1 连接池配置

```rust
use sqlx::postgres::PgPoolOptions;

async fn create_optimized_pool() -> Result<PgPool, sqlx::Error> {
    let pool = PgPoolOptions::new()
        .max_connections(20)  // 最大连接数
        .min_connections(5)   // 最小连接数
        .acquire_timeout(std::time::Duration::from_secs(30))
        .idle_timeout(std::time::Duration::from_secs(600))
        .max_lifetime(std::time::Duration::from_secs(1800))
        .connect("postgres://postgres@localhost/test")
        .await?;

    Ok(pool)
}
```

### 3.2 事务管理模式

#### 3.2.1 事务装饰器模式

```rust
use sqlx::PgPool;

async fn with_transaction<F, T>(
    pool: &PgPool,
    f: F,
) -> Result<T, sqlx::Error>
where
    F: for<'a> FnOnce(&'a mut sqlx::Transaction<'_, sqlx::Postgres>) -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<T, sqlx::Error>> + Send + 'a>>,
{
    let mut tx = pool.begin().await?;

    match f(&mut tx).await {
        Ok(result) => {
            tx.commit().await?;
            Ok(result)
        }
        Err(e) => {
            tx.rollback().await?;
            Err(e)
        }
    }
}

// 使用事务装饰器
let result = with_transaction(&pool, |tx| {
    Box::pin(async move {
        sqlx::query("INSERT INTO users (id, name) VALUES ($1, $2)")
            .bind(1i32)
            .bind("Alice")
            .execute(&mut **tx)
            .await?;
        Ok(())
    })
}).await?;
```

### 3.3 查询优化模式

#### 3.3.1 查询缓存模式

```rust
use sqlx::PgPool;
use std::sync::Arc;
use std::collections::HashMap;
use tokio::sync::RwLock;

struct QueryCache {
    cache: Arc<RwLock<HashMap<String, Vec<sqlx::postgres::PgRow>>>>,
    pool: Arc<PgPool>,
}

impl QueryCache {
    async fn get(&self, query: &str) -> Result<Vec<sqlx::postgres::PgRow>, sqlx::Error> {
        // 检查缓存
        {
            let cache = self.cache.read().await;
            if let Some(result) = cache.get(query) {
                return Ok(result.clone());
            }
        }

        // 查询数据库
        let rows = sqlx::query(query)
            .fetch_all(&*self.pool)
            .await?;

        // 更新缓存
        {
            let mut cache = self.cache.write().await;
            cache.insert(query.to_string(), rows.clone());
        }

        Ok(rows)
    }
}
```

### 3.4 错误处理模式

#### 3.4.1 错误分类处理

```rust
use sqlx::Error;

fn handle_error(error: sqlx::Error) {
    match error {
        Error::Database(ref e) => {
            match e.code() {
                Some("23505") => {
                    // 唯一约束违反：可重试
                    eprintln!("Unique constraint violation");
                }
                Some("40001") => {
                    // 序列化失败：可重试
                    eprintln!("Serialization failure: retry");
                }
                Some("40P01") => {
                    // 死锁：可重试
                    eprintln!("Deadlock detected: retry");
                }
                _ => {
                    eprintln!("Database error: {}", e);
                }
            }
        }
        Error::RowNotFound => {
            eprintln!("Row not found");
        }
        _ => {
            eprintln!("Other error: {}", error);
        }
    }
}
```

---

## ⚡ 第四部分：性能优化模式

### 4.1 批量操作模式

#### 4.1.1 批量插入

```rust
use sqlx::PgPool;

async fn batch_insert(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    // 批量插入（单次事务）
    for i in 1..=1000 {
        sqlx::query("INSERT INTO users (id, name) VALUES ($1, $2)")
            .bind(i)
            .bind(format!("User{}", i))
            .execute(&mut *tx)
            .await?;
    }

    tx.commit().await?;
    Ok(())
}
```

### 4.2 异步I/O模式

#### 4.2.1 并发查询

```rust
use sqlx::PgPool;
use std::sync::Arc;

async fn concurrent_queries(pool: Arc<PgPool>) -> Result<(), sqlx::Error> {
    let mut handles = vec![];

    for i in 0..100 {
        let pool = Arc::clone(&pool);
        let handle = tokio::spawn(async move {
            sqlx::query("SELECT * FROM users WHERE id = $1")
                .bind(i)
                .fetch_one(&*pool)
                .await
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.await??;
    }

    Ok(())
}
```

### 4.3 缓存模式

#### 4.3.1 多级缓存

```rust
use sqlx::PgPool;
use std::sync::Arc;
use std::collections::HashMap;
use tokio::sync::RwLock;
use std::time::{Duration, Instant};

struct CacheEntry<T> {
    value: T,
    expires_at: Instant,
}

struct MultiLevelCache {
    l1: Arc<RwLock<HashMap<String, CacheEntry<String>>>>,  // 内存缓存
    pool: Arc<PgPool>,
}

impl MultiLevelCache {
    async fn get(&self, key: &str) -> Result<String, sqlx::Error> {
        // L1缓存
        {
            let cache = self.l1.read().await;
            if let Some(entry) = cache.get(key) {
                if entry.expires_at > Instant::now() {
                    return Ok(entry.value.clone());
                }
            }
        }

        // 查询数据库
        let row = sqlx::query("SELECT value FROM cache WHERE key = $1")
            .bind(key)
            .fetch_one(&*self.pool)
            .await?;

        let value: String = row.get("value");

        // 更新L1缓存
        {
            let mut cache = self.l1.write().await;
            cache.insert(key.to_string(), CacheEntry {
                value: value.clone(),
                expires_at: Instant::now() + Duration::from_secs(60),
            });
        }

        Ok(value)
    }
}
```

---

## 🛡️ 第五部分：错误处理与恢复模式

### 5.1 重试模式

#### 5.1.1 指数退避重试

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

                // 检查是否可重试
                if is_retryable(&e) {
                    retries += 1;
                    sleep(delay).await;
                    delay *= 2;  // 指数退避
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
            matches!(e.code(), Some("40001") | Some("40P01"))  // 序列化失败或死锁
        }
        _ => false,
    }
}
```

### 5.2 断路器模式

#### 5.2.1 断路器实现

```rust
use std::sync::Arc;
use tokio::sync::RwLock;
use std::time::{Duration, Instant};

enum CircuitState {
    Closed,
    Open,
    HalfOpen,
}

struct CircuitBreaker {
    state: Arc<RwLock<CircuitState>>,
    failure_count: Arc<RwLock<usize>>,
    last_failure_time: Arc<RwLock<Option<Instant>>>,
    threshold: usize,
    timeout: Duration,
}

impl CircuitBreaker {
    async fn call<F, T>(&self, f: F) -> Result<T, sqlx::Error>
    where
        F: std::future::Future<Output = Result<T, sqlx::Error>>,
    {
        let state = self.state.read().await;

        match *state {
            CircuitState::Open => {
                // 检查是否应该尝试半开
                if let Some(last_failure) = *self.last_failure_time.read().await {
                    if last_failure.elapsed() > self.timeout {
                        // 转换为半开状态
                        drop(state);
                        *self.state.write().await = CircuitState::HalfOpen;
                    } else {
                        return Err(sqlx::Error::PoolClosed);
                    }
                }
            }
            _ => {}
        }

        drop(state);

        // 执行操作
        match f.await {
            Ok(result) => {
                // 成功：重置状态
                *self.state.write().await = CircuitState::Closed;
                *self.failure_count.write().await = 0;
                Ok(result)
            }
            Err(e) => {
                // 失败：增加计数
                let mut count = self.failure_count.write().await;
                *count += 1;

                if *count >= self.threshold {
                    *self.state.write().await = CircuitState::Open;
                    *self.last_failure_time.write().await = Some(Instant::now());
                }

                Err(e)
            }
        }
    }
}
```

---

## 📊 第六部分：监控与可观测性模式

### 6.1 指标收集模式

#### 6.1.1 指标收集器

```rust
use std::sync::Arc;
use std::sync::atomic::{AtomicU64, Ordering};
use tokio::sync::RwLock;

struct Metrics {
    query_count: AtomicU64,
    error_count: AtomicU64,
    latency_sum: Arc<RwLock<u64>>,
}

impl Metrics {
    fn record_query(&self, latency: Duration) {
        self.query_count.fetch_add(1, Ordering::Relaxed);
        let mut sum = self.latency_sum.write().blocking_lock();
        *sum += latency.as_millis() as u64;
    }

    fn record_error(&self) {
        self.error_count.fetch_add(1, Ordering::Relaxed);
    }

    fn get_stats(&self) -> (u64, u64, f64) {
        let queries = self.query_count.load(Ordering::Relaxed);
        let errors = self.error_count.load(Ordering::Relaxed);
        let avg_latency = {
            let sum = self.latency_sum.read().blocking_lock();
            if queries > 0 {
                *sum as f64 / queries as f64
            } else {
                0.0
            }
        };
        (queries, errors, avg_latency)
    }
}
```

---

## 🎯 第七部分：最佳实践总结

### 7.1 模式选择指南

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| **高并发读** | 连接池 + 无锁读 | MVCC无锁读性能最佳 |
| **批量写入** | 批量操作 + 单事务 | 减少事务开销 |
| **错误恢复** | 重试 + 断路器 | 提高可靠性 |
| **性能监控** | 指标收集 + 日志 | 可观测性 |

### 7.2 常见陷阱避免

#### 7.2.1 长事务陷阱

```rust
// ❌ 陷阱：长事务
let mut tx = pool.begin().await?;
let rows = sqlx::query("SELECT * FROM users").fetch_all(&mut *tx).await?;
tokio::time::sleep(Duration::from_secs(60)).await;  // 长时间持有事务
tx.commit().await?;

// ✅ 避免：短事务
let rows = sqlx::query("SELECT * FROM users").fetch_all(pool).await?;
// 查询完成，立即释放快照
```

### 7.3 性能调优建议

```rust
// ✅ 连接池大小 = 预期最大并发事务数
let pool = PgPoolOptions::new()
    .max_connections(20)
    .connect("postgres://...")
    .await?;

// ✅ 使用批量操作
let mut tx = pool.begin().await?;
for i in 1..=100 {
    sqlx::query("INSERT INTO users (id, name) VALUES ($1, $2)")
        .bind(i)
        .bind(format!("User{}", i))
        .execute(&mut *tx)
        .await?;
}
tx.commit().await?;

// ✅ 并发查询
let mut handles = vec![];
for i in 0..10 {
    let pool = Arc::clone(&pool);
    let handle = tokio::spawn(async move {
        sqlx::query("SELECT * FROM users WHERE id = $1")
            .bind(i)
            .fetch_one(&*pool)
            .await
    });
    handles.push(handle);
}
```

---

## 📝 总结

本文档提供了Rust并发模式与PostgreSQL MVCC集成的最佳实践，涵盖了常见并发模式、性能优化策略、错误处理机制和监控方案。

**核心要点**：

1. **并发模式**：
   - Actor模式、工作窃取、生产者-消费者、扇出-扇入

2. **MVCC集成**：
   - 连接池模式、事务管理、查询优化、错误处理

3. **性能优化**：
   - 批量操作、异步I/O、缓存、连接复用

4. **错误处理**：
   - 重试、断路器、超时、优雅降级

5. **监控**：
   - 指标收集、日志记录、追踪

**下一步**：

- 深入分析Rust应用并发监控指标
- 探索更多性能优化模式
- 完善监控和可观测性方案

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
