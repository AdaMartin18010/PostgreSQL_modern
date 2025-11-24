# Rust应用并发监控指标

> **文档编号**: OPS-RUST-MONITOR-001
> **主题**: Rust应用并发监控指标与PostgreSQL MVCC
> **版本**: PostgreSQL 17 & 18
> **相关文档**:
>
> - [监控指标体系](监控指标体系.md)
> - [Prometheus配置](Prometheus配置.md)
> - [Grafana仪表盘](Grafana仪表盘.md)
> - [Rust并发模式最佳实践](../../04-形式化论证/理论论证/Rust并发模式最佳实践.md)

---

## 📑 目录

- [Rust应用并发监控指标](#rust应用并发监控指标)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📊 第一部分：Rust应用指标](#-第一部分rust应用指标)
    - [1.1 连接池指标](#11-连接池指标)
      - [1.1.1 连接池状态指标](#111-连接池状态指标)
    - [1.2 事务指标](#12-事务指标)
      - [1.2.1 事务状态指标](#121-事务状态指标)
    - [1.3 查询指标](#13-查询指标)
      - [1.3.1 查询性能指标](#131-查询性能指标)
    - [1.4 错误指标](#14-错误指标)
      - [1.4.1 错误分类指标](#141-错误分类指标)
  - [🔍 第二部分：PostgreSQL MVCC指标](#-第二部分postgresql-mvcc指标)
    - [2.1 快照指标](#21-快照指标)
      - [2.1.1 快照状态指标](#211-快照状态指标)
    - [2.2 版本链指标](#22-版本链指标)
      - [2.2.1 版本链长度指标](#221-版本链长度指标)
    - [2.3 锁指标](#23-锁指标)
      - [2.3.1 锁等待指标](#231-锁等待指标)
    - [2.4 VACUUM指标](#24-vacuum指标)
      - [2.4.1 VACUUM状态指标](#241-vacuum状态指标)
  - [⚡ 第三部分：性能指标](#-第三部分性能指标)
    - [3.1 延迟指标](#31-延迟指标)
      - [3.1.1 查询延迟分布](#311-查询延迟分布)
    - [3.2 吞吐量指标](#32-吞吐量指标)
      - [3.2.1 吞吐量统计](#321-吞吐量统计)
  - [🛡️ 第四部分：健康检查指标](#️-第四部分健康检查指标)
    - [4.1 连接健康](#41-连接健康)
  - [📈 第五部分：指标收集实现](#-第五部分指标收集实现)
    - [5.1 Prometheus集成](#51-prometheus集成)
  - [🎯 第六部分：告警规则](#-第六部分告警规则)
    - [6.1 连接池告警](#61-连接池告警)
    - [6.2 事务告警](#62-事务告警)
  - [📝 总结](#-总结)

---

## 📋 概述

本文档定义Rust应用并发监控指标体系，涵盖连接池、事务、查询、错误等关键指标，以及与PostgreSQL MVCC相关的监控指标，帮助运维人员及时发现和解决性能问题。

**核心内容**：

- Rust应用指标（连接池、事务、查询、错误）
- PostgreSQL MVCC指标（快照、版本链、锁、VACUUM）
- 性能指标（延迟、吞吐量、资源使用）
- 健康检查指标
- 指标收集实现
- 告警规则

**目标读者**：

- 运维工程师
- Rust开发者
- 系统架构师
- SRE工程师

---

## 📊 第一部分：Rust应用指标

### 1.1 连接池指标

#### 1.1.1 连接池状态指标

```rust
use prometheus::{Counter, Gauge, Histogram, Registry};

pub struct ConnectionPoolMetrics {
    // 连接池大小
    pub pool_size: Gauge,
    pub pool_idle: Gauge,
    pub pool_active: Gauge,

    // 连接获取
    pub connections_acquired: Counter,
    pub connections_released: Counter,
    pub connection_acquire_duration: Histogram,

    // 连接错误
    pub connection_errors: Counter,
    pub connection_timeouts: Counter,
}

impl ConnectionPoolMetrics {
    pub fn new(registry: &Registry) -> Self {
        Self {
            pool_size: Gauge::new("pg_pool_size", "Connection pool size")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            pool_idle: Gauge::new("pg_pool_idle", "Idle connections in pool")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            pool_active: Gauge::new("pg_pool_active", "Active connections in pool")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            connections_acquired: Counter::new("pg_connections_acquired_total", "Total connections acquired")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            connections_released: Counter::new("pg_connections_released_total", "Total connections released")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            connection_acquire_duration: Histogram::with_opts(
                HistogramOpts::new("pg_connection_acquire_duration_seconds", "Connection acquire duration")
                    .buckets(vec![0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0])
            )
            .expect("metric can be created")
            .register(registry)
            .unwrap(),
            connection_errors: Counter::new("pg_connection_errors_total", "Total connection errors")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            connection_timeouts: Counter::new("pg_connection_timeouts_total", "Total connection timeouts")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
        }
    }
}
```

### 1.2 事务指标

#### 1.2.1 事务状态指标

```rust
pub struct TransactionMetrics {
    // 事务计数
    pub transactions_started: Counter,
    pub transactions_committed: Counter,
    pub transactions_rolled_back: Counter,

    // 事务持续时间
    pub transaction_duration: Histogram,

    // 长事务
    pub long_transactions: Gauge,

    // 事务错误
    pub transaction_errors: Counter,
    pub deadlocks: Counter,
    pub serialization_failures: Counter,
}

impl TransactionMetrics {
    pub fn new(registry: &Registry) -> Self {
        Self {
            transactions_started: Counter::new("pg_transactions_started_total", "Total transactions started")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            transactions_committed: Counter::new("pg_transactions_committed_total", "Total transactions committed")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            transactions_rolled_back: Counter::new("pg_transactions_rolled_back_total", "Total transactions rolled back")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            transaction_duration: Histogram::with_opts(
                HistogramOpts::new("pg_transaction_duration_seconds", "Transaction duration")
                    .buckets(vec![0.001, 0.01, 0.1, 1.0, 5.0, 10.0, 30.0, 60.0])
            )
            .expect("metric can be created")
            .register(registry)
            .unwrap(),
            long_transactions: Gauge::new("pg_long_transactions", "Number of long transactions (>60s)")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            transaction_errors: Counter::new("pg_transaction_errors_total", "Total transaction errors")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            deadlocks: Counter::new("pg_deadlocks_total", "Total deadlocks")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
            serialization_failures: Counter::new("pg_serialization_failures_total", "Total serialization failures")
                .expect("metric can be created")
                .register(registry)
                .unwrap(),
        }
    }
}
```

### 1.3 查询指标

#### 1.3.1 查询性能指标

```rust
pub struct QueryMetrics {
    // 查询计数
    pub queries_total: Counter,
    pub queries_by_type: CounterVec,

    // 查询延迟
    pub query_duration: HistogramVec,

    // 查询错误
    pub query_errors: CounterVec,

    // 慢查询
    pub slow_queries: Counter,
}
```

### 1.4 错误指标

#### 1.4.1 错误分类指标

```rust
pub struct ErrorMetrics {
    pub errors_total: Counter,
    pub errors_by_type: CounterVec,
    pub errors_by_code: CounterVec,
}
```

---

## 🔍 第二部分：PostgreSQL MVCC指标

### 2.1 快照指标

#### 2.1.1 快照状态指标

```sql
-- 活跃事务数（影响快照获取性能）
SELECT count(*) as active_transactions
FROM pg_stat_activity
WHERE state = 'active';

-- 长事务数（影响MVCC性能）
SELECT count(*) as long_transactions
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - xact_start > interval '60 seconds';

-- 快照年龄（XID wraparound风险）
SELECT
    datname,
    age(datfrozenxid) as xid_age
FROM pg_database
WHERE datname = current_database();
```

### 2.2 版本链指标

#### 2.2.1 版本链长度指标

```sql
-- 表膨胀率
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as indexes_size,
    n_dead_tup,
    n_live_tup,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_tuple_percent
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 2.3 锁指标

#### 2.3.1 锁等待指标

```sql
-- 锁等待数
SELECT count(*) as lock_waits
FROM pg_locks
WHERE NOT granted;

-- 死锁数
SELECT count(*) as deadlocks
FROM pg_stat_database
WHERE datname = current_database();
```

### 2.4 VACUUM指标

#### 2.4.1 VACUUM状态指标

```sql
-- VACUUM进度
SELECT
    pid,
    datname,
    relid::regclass,
    phase,
    heap_blks_total,
    heap_blks_scanned,
    heap_blks_vacuumed,
    index_vacuum_count,
    max_dead_tuples,
    num_dead_tuples
FROM pg_stat_progress_vacuum;
```

---

## ⚡ 第三部分：性能指标

### 3.1 延迟指标

#### 3.1.1 查询延迟分布

```rust
pub struct LatencyMetrics {
    pub p50: Gauge,
    pub p95: Gauge,
    pub p99: Gauge,
    pub p999: Gauge,
    pub max: Gauge,
}
```

### 3.2 吞吐量指标

#### 3.2.1 吞吐量统计

```rust
pub struct ThroughputMetrics {
    pub queries_per_second: Gauge,
    pub transactions_per_second: Gauge,
    pub bytes_per_second: Gauge,
}
```

---

## 🛡️ 第四部分：健康检查指标

### 4.1 连接健康

```rust
pub struct HealthMetrics {
    pub connection_pool_health: Gauge,  // 0=healthy, 1=unhealthy
    pub database_connectivity: Gauge,     // 0=connected, 1=disconnected
}
```

---

## 📈 第五部分：指标收集实现

### 5.1 Prometheus集成

```rust
use prometheus::{Registry, Encoder, TextEncoder};
use axum::{Router, response::Response};

async fn metrics_handler(registry: Registry) -> Response<String> {
    let encoder = TextEncoder::new();
    let metric_families = registry.gather();
    let mut buffer = Vec::new();
    encoder.encode(&metric_families, &mut buffer).unwrap();

    Response::builder()
        .status(200)
        .header("Content-Type", "text/plain; version=0.0.4")
        .body(String::from_utf8(buffer).unwrap())
        .unwrap()
}

// 在应用中集成
let app = Router::new()
    .route("/metrics", get(metrics_handler));
```

---

## 🎯 第六部分：告警规则

### 6.1 连接池告警

```yaml
groups:
  - name: rust_pg_connection_pool
    rules:
      - alert: ConnectionPoolExhausted
        expr: pg_pool_active / pg_pool_size > 0.9
        for: 5m
        annotations:
          summary: "Connection pool nearly exhausted"

      - alert: ConnectionAcquireTimeout
        expr: rate(pg_connection_timeouts_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High connection acquire timeout rate"
```

### 6.2 事务告警

```yaml
      - alert: LongTransactions
        expr: pg_long_transactions > 10
        for: 5m
        annotations:
          summary: "Too many long transactions"

      - alert: HighDeadlockRate
        expr: rate(pg_deadlocks_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High deadlock rate"
```

---

## 📝 总结

本文档定义了Rust应用并发监控指标体系，涵盖连接池、事务、查询、错误等关键指标，以及与PostgreSQL MVCC相关的监控指标。

**核心要点**：

1. **Rust应用指标**：
   - 连接池状态、事务状态、查询性能、错误统计

2. **PostgreSQL MVCC指标**：
   - 快照状态、版本链长度、锁等待、VACUUM进度

3. **性能指标**：
   - 延迟分布、吞吐量统计、资源使用

4. **健康检查**：
   - 连接健康、事务健康、查询健康

5. **告警规则**：
   - 连接池告警、事务告警、性能告警

**下一步**：

- 完善Prometheus集成实现
- 添加Grafana仪表盘配置
- 完善告警规则和通知机制

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
