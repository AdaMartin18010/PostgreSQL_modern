# Prometheus-Rust监控集成

> **文档编号**: OPS-PROMETHEUS-RUST-001
> **主题**: Prometheus与Rust应用监控集成
> **版本**: PostgreSQL 17 & 18
> **相关文档**:
>
> - [Prometheus配置](Prometheus配置.md)
> - [Rust应用并发监控指标](Rust应用并发监控指标.md)
> - [Grafana仪表盘](Grafana仪表盘.md)

---

## 📑 目录

- [Prometheus-Rust监控集成](#prometheus-rust监控集成)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔧 第一部分：Rust应用指标导出](#-第一部分rust应用指标导出)
    - [1.1 Prometheus客户端集成](#11-prometheus客户端集成)
    - [1.2 指标注册](#12-指标注册)
    - [1.3 HTTP端点暴露](#13-http端点暴露)
  - [📊 第二部分：Prometheus服务器配置](#-第二部分prometheus服务器配置)
    - [2.1 抓取配置](#21-抓取配置)
    - [2.2 服务发现](#22-服务发现)
    - [2.3 标签配置](#23-标签配置)
  - [🚨 第三部分：告警规则配置](#-第三部分告警规则配置)
    - [3.1 连接池告警](#31-连接池告警)
    - [3.2 事务告警](#32-事务告警)
    - [3.3 性能告警](#33-性能告警)
  - [📈 第四部分：Grafana仪表盘集成](#-第四部分grafana仪表盘集成)
    - [4.1 数据源配置](#41-数据源配置)
    - [4.2 仪表盘配置](#42-仪表盘配置)
    - [4.3 面板配置](#43-面板配置)
  - [🔍 第五部分：监控最佳实践](#-第五部分监控最佳实践)
    - [5.1 指标命名规范](#51-指标命名规范)
    - [5.2 标签使用规范](#52-标签使用规范)
    - [5.3 性能优化建议](#53-性能优化建议)
  - [📝 总结](#-总结)

---

## 📋 概述

本文档详细说明如何将Rust应用的监控指标集成到Prometheus监控系统中，包括指标导出、Prometheus配置、告警规则和Grafana仪表盘集成。

**核心内容**：

- Rust应用指标导出实现
- Prometheus服务器配置
- 告警规则配置
- Grafana仪表盘集成
- 监控最佳实践

**目标读者**：

- 运维工程师
- Rust开发者
- SRE工程师
- 系统架构师

---

## 🔧 第一部分：Rust应用指标导出

### 1.1 Prometheus客户端集成

#### 1.1.1 添加依赖

```toml
# Cargo.toml
[dependencies]
prometheus = "0.13"
axum = "0.7"
tokio = { version = "1", features = ["full"] }
```

#### 1.1.2 创建指标注册表

```rust
use prometheus::{Registry, Encoder, TextEncoder};

pub struct Metrics {
    registry: Registry,
}

impl Metrics {
    pub fn new() -> Self {
        let registry = Registry::new();

        // 注册所有指标
        // ...

        Self { registry }
    }

    pub fn registry(&self) -> &Registry {
        &self.registry
    }
}
```

### 1.2 指标注册

#### 1.2.1 连接池指标注册

```rust
use prometheus::{Gauge, Counter, Histogram, HistogramOpts};

pub struct ConnectionPoolMetrics {
    pub pool_size: Gauge,
    pub pool_idle: Gauge,
    pub pool_active: Gauge,
    pub connections_acquired: Counter,
    pub connection_acquire_duration: Histogram,
}

impl ConnectionPoolMetrics {
    pub fn new(registry: &Registry) -> Self {
        let pool_size = Gauge::new("pg_pool_size", "Connection pool size")
            .expect("metric can be created");
        registry.register(Box::new(pool_size.clone())).unwrap();

        let pool_idle = Gauge::new("pg_pool_idle", "Idle connections in pool")
            .expect("metric can be created");
        registry.register(Box::new(pool_idle.clone())).unwrap();

        let pool_active = Gauge::new("pg_pool_active", "Active connections in pool")
            .expect("metric can be created");
        registry.register(Box::new(pool_active.clone())).unwrap();

        let connections_acquired = Counter::new("pg_connections_acquired_total", "Total connections acquired")
            .expect("metric can be created");
        registry.register(Box::new(connections_acquired.clone())).unwrap();

        let connection_acquire_duration = Histogram::with_opts(
            HistogramOpts::new("pg_connection_acquire_duration_seconds", "Connection acquire duration")
                .buckets(vec![0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0])
        )
        .expect("metric can be created");
        registry.register(Box::new(connection_acquire_duration.clone())).unwrap();

        Self {
            pool_size,
            pool_idle,
            pool_active,
            connections_acquired,
            connection_acquire_duration,
        }
    }
}
```

### 1.3 HTTP端点暴露

#### 1.3.1 Axum集成

```rust
use axum::{Router, response::Response, routing::get};
use prometheus::{Encoder, TextEncoder};

async fn metrics_handler(metrics: Metrics) -> Response<String> {
    let encoder = TextEncoder::new();
    let metric_families = metrics.registry().gather();
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
    .route("/metrics", get(metrics_handler))
    .with_state(metrics);
```

---

## 📊 第二部分：Prometheus服务器配置

### 2.1 抓取配置

#### 2.1.1 prometheus.yml配置

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Rust应用指标
  - job_name: 'rust-app'
    static_configs:
      - targets: ['localhost:8080']
        labels:
          app: 'rust-app'
          environment: 'production'
    metrics_path: '/metrics'
    scrape_interval: 10s

  # PostgreSQL Exporter
  - job_name: 'postgresql'
    static_configs:
      - targets: ['localhost:9187']
        labels:
          database: 'postgres'
          environment: 'production'
```

### 2.2 服务发现

#### 2.2.1 Kubernetes服务发现

```yaml
scrape_configs:
  - job_name: 'rust-app-kubernetes'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - default
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: rust-app
      - source_labels: [__meta_kubernetes_pod_ip]
        action: replace
        target_label: __address__
        replacement: '${1}:8080'
```

### 2.3 标签配置

#### 2.3.1 标签重写

```yaml
relabel_configs:
  - source_labels: [__meta_kubernetes_pod_name]
    target_label: instance
  - source_labels: [__meta_kubernetes_namespace]
    target_label: namespace
  - source_labels: [__meta_kubernetes_pod_label_app]
    target_label: app
```

---

## 🚨 第三部分：告警规则配置

### 3.1 连接池告警

#### 3.1.1 连接池告警规则

```yaml
groups:
  - name: rust_pg_connection_pool
    interval: 30s
    rules:
      - alert: ConnectionPoolExhausted
        expr: pg_pool_active / pg_pool_size > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Connection pool nearly exhausted (instance {{ $labels.instance }})"
          description: "Connection pool is {{ $value | humanizePercentage }} full"

      - alert: ConnectionAcquireTimeout
        expr: rate(pg_connection_timeouts_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High connection acquire timeout rate (instance {{ $labels.instance }})"
          description: "Connection acquire timeout rate is {{ $value | humanize }} per second"
```

### 3.2 事务告警

#### 3.2.1 事务告警规则

```yaml
      - alert: LongTransactions
        expr: pg_long_transactions > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Too many long transactions (instance {{ $labels.instance }})"
          description: "{{ $value }} long transactions detected"

      - alert: HighDeadlockRate
        expr: rate(pg_deadlocks_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High deadlock rate (instance {{ $labels.instance }})"
          description: "Deadlock rate is {{ $value | humanize }} per second"

      - alert: HighSerializationFailureRate
        expr: rate(pg_serialization_failures_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High serialization failure rate (instance {{ $labels.instance }})"
          description: "Serialization failure rate is {{ $value | humanize }} per second"
```

### 3.3 性能告警

#### 3.3.1 性能告警规则

```yaml
      - alert: HighQueryLatency
        expr: histogram_quantile(0.95, rate(pg_query_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High query latency (instance {{ $labels.instance }})"
          description: "P95 query latency is {{ $value }}s"

      - alert: LowThroughput
        expr: rate(pg_queries_total[5m]) < 10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low query throughput (instance {{ $labels.instance }})"
          description: "Query throughput is {{ $value | humanize }} queries/second"
```

---

## 📈 第四部分：Grafana仪表盘集成

### 4.1 数据源配置

#### 4.1.1 Prometheus数据源

```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://prometheus:9090",
  "access": "proxy",
  "isDefault": true
}
```

### 4.2 仪表盘配置

#### 4.2.1 连接池监控面板

```json
{
  "title": "Connection Pool",
  "targets": [
    {
      "expr": "pg_pool_size",
      "legendFormat": "Pool Size"
    },
    {
      "expr": "pg_pool_active",
      "legendFormat": "Active"
    },
    {
      "expr": "pg_pool_idle",
      "legendFormat": "Idle"
    }
  ],
  "type": "graph"
}
```

### 4.3 面板配置

#### 4.3.1 事务监控面板

```json
{
  "title": "Transactions",
  "targets": [
    {
      "expr": "rate(pg_transactions_started_total[5m])",
      "legendFormat": "Started"
    },
    {
      "expr": "rate(pg_transactions_committed_total[5m])",
      "legendFormat": "Committed"
    },
    {
      "expr": "rate(pg_transactions_rolled_back_total[5m])",
      "legendFormat": "Rolled Back"
    }
  ],
  "type": "graph"
}
```

---

## 🔍 第五部分：监控最佳实践

### 5.1 指标命名规范

#### 5.1.1 命名规则

```rust
// ✅ 好的命名
pg_pool_size                    // 前缀_指标名
pg_transactions_started_total   // 后缀_total表示计数器
pg_query_duration_seconds      // 后缀_seconds表示时间

// ❌ 不好的命名
pool_size                       // 缺少前缀
transactions                    // 不明确
query_time                      // 单位不明确
```

### 5.2 标签使用规范

#### 5.2.1 标签选择

```rust
// ✅ 好的标签
pg_query_duration_seconds{query_type="SELECT", table="users"}

// ❌ 不好的标签
pg_query_duration_seconds{query="SELECT * FROM users WHERE id = 1"}  // 高基数标签
```

### 5.3 性能优化建议

```rust
// ✅ 使用Histogram而不是Summary（Prometheus推荐）
let histogram = Histogram::with_opts(
    HistogramOpts::new("pg_query_duration_seconds", "Query duration")
        .buckets(vec![0.001, 0.01, 0.1, 1.0, 5.0, 10.0])
);

// ✅ 避免高基数标签
// 不要使用查询文本作为标签，使用查询类型
pg_query_duration_seconds{query_type="SELECT"}  // ✅
pg_query_duration_seconds{query="SELECT * FROM..."}  // ❌
```

---

## 📝 总结

本文档详细说明了如何将Rust应用的监控指标集成到Prometheus监控系统中。

**核心要点**：

1. **指标导出**：
   - Prometheus客户端集成
   - 指标注册和更新
   - HTTP端点暴露

2. **Prometheus配置**：
   - 抓取配置
   - 服务发现
   - 标签配置

3. **告警规则**：
   - 连接池告警
   - 事务告警
   - 性能告警

4. **Grafana集成**：
   - 数据源配置
   - 仪表盘配置
   - 面板配置

5. **最佳实践**：
   - 指标命名规范
   - 标签使用规范
   - 性能优化建议

**下一步**：

- 完善Grafana仪表盘配置
- 添加更多告警规则
- 完善监控最佳实践文档

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
