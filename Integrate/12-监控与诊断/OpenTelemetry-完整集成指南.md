# OpenTelemetry PostgreSQL 完整集成指南

> **标准**: OpenTelemetry
> **版本**: 最新稳定版
> **文档状态**: ✅ 完整
> **最后更新**: 2025年1月29日
> **兼容性**: PostgreSQL 12+

---

## 📋 目录

- [概述](#概述)
- [架构设计](#架构设计)
- [Collector配置](#collector配置)
- [Metrics收集](#metrics收集)
- [Logs收集](#logs收集)
- [Traces收集](#traces收集)
- [Grafana LGTM+ Stack](#grafana-lgtm-stack)
- [生产最佳实践](#生产最佳实践)
- [实战案例](#实战案例)
- [参考资源](#参考资源)

---

## 📊 概述

### 什么是OpenTelemetry

OpenTelemetry是一个**开放标准**，用于统一收集、处理和导出遥测数据（metrics、logs、traces）。

### 核心优势

1. ✅ **标准化**: 统一的API和SDK
2. ✅ **厂商无关**: 避免厂商锁定
3. ✅ **完整覆盖**: Metrics、Logs、Traces三支柱
4. ✅ **丰富生态**: 广泛的工具支持

### 三支柱模型

```
┌─────────────────────────────────────┐
│      OpenTelemetry 三支柱           │
├─────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐       │
│  │ Metrics  │  │  Logs    │       │
│  │  (指标)  │  │  (日志)  │       │
│  └──────────┘  └──────────┘       │
│  ┌──────────┐                      │
│  │ Traces   │                      │
│  │  (追踪)  │                      │
│  └──────────┘                      │
└─────────────────────────────────────┘
```

---

## 🏗️ 架构设计

### 组件架构

```
┌─────────────────────────────────────┐
│      PostgreSQL 应用                │
├─────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐       │
│  │ Metrics  │  │  Logs    │       │
│  │ Exporter │  │  Exporter│       │
│  └──────────┘  └──────────┘       │
│  ┌──────────┐                      │
│  │ Traces   │                      │
│  │ Exporter │                      │
│  └──────────┘                      │
└──────────┬─────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│   OpenTelemetry Collector           │
├─────────────────────────────────────┤
│  Receivers → Processors → Exporters │
└──────────┬─────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│   后端存储 (Prometheus/Loki/Tempo)  │
└─────────────────────────────────────┘
```

### 数据流

1. **收集**: 从PostgreSQL和应用收集数据
2. **处理**: Collector处理和转换数据
3. **导出**: 发送到后端存储系统
4. **可视化**: Grafana展示和分析

---

## ⚙️ Collector配置

### 安装Collector

#### Linux

```bash
# 下载最新版本
wget https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.95.0/otelcol_0.95.0_linux_amd64.tar.gz

# 解压
tar -xzf otelcol_0.95.0_linux_amd64.tar.gz

# 安装
sudo mv otelcol /usr/local/bin/
sudo chmod +x /usr/local/bin/otelcol
```

#### Docker

```bash
docker run -d \
  --name otel-collector \
  -p 4317:4317 \
  -p 4318:4318 \
  -v $(pwd)/otel-collector-config.yaml:/etc/otelcol/config.yaml \
  otel/opentelemetry-collector:latest
```

### 基础配置

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

  prometheus:
    config:
      scrape_configs:
        - job_name: 'postgresql'
          static_configs:
            - targets: ['localhost:9187']

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

  memory_limiter:
    limit_mib: 512

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"

  loki:
    endpoint: "http://loki:3100/loki/api/v1/push"

  otlp:
    endpoint: "tempo:4317"
    tls:
      insecure: true

service:
  pipelines:
    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch]
      exporters: [prometheus]

    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [loki]

    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp]
```

---

## 📈 Metrics收集

### PostgreSQL Exporter

#### 安装

```bash
# 使用postgres_exporter
docker run -d \
  --name postgres-exporter \
  -p 9187:9187 \
  -e DATA_SOURCE_NAME="postgresql://user:password@localhost:5432/dbname?sslmode=disable" \
  prometheuscommunity/postgres-exporter:latest
```

#### 配置

```yaml
# postgres_exporter配置
queries:
  - name: "pg_stat_database"
    help: "PostgreSQL database statistics"
    values:
      - numbackends
      - xact_commit
      - xact_rollback
      - blks_read
      - blks_hit
      - tup_returned
      - tup_fetched
      - tup_inserted
      - tup_updated
      - tup_deleted
```

#### 自定义指标

```yaml
# custom_queries.yaml
pg_replication:
  query: |
    SELECT
      CASE WHEN NOT pg_is_in_recovery() THEN 1 ELSE 0 END AS is_primary,
      CASE WHEN pg_is_in_recovery() THEN 1 ELSE 0 END AS is_replica
  metrics:
    - is_primary:
        usage: "GAUGE"
        description: "Whether the instance is a primary (1) or replica (0)"
    - is_replica:
        usage: "GAUGE"
        description: "Whether the instance is a replica (1) or primary (0)"
```

### Prometheus集成

#### 配置Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8889']
```

#### 查询示例

```promql
# 数据库连接数
pg_stat_database_numbackends{datname="mydb"}

# 查询TPS
rate(pg_stat_database_xact_commit[5m]) + rate(pg_stat_database_xact_rollback[5m])

# 缓存命中率
sum(rate(pg_stat_database_blks_hit[5m])) /
sum(rate(pg_stat_database_blks_hit[5m]) + rate(pg_stat_database_blks_read[5m]))
```

---

## 📝 Logs收集

### PostgreSQL日志配置

#### 日志格式

```conf
# postgresql.conf
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000  # 记录超过1秒的查询
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0
```

#### 结构化日志

```conf
# 使用JSON格式
log_destination = 'jsonlog'
logging_collector = on
```

### Loki集成

#### 配置Loki

```yaml
# loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/index_cache
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

#### 日志查询

```logql
# 查询错误日志
{job="postgresql"} |= "ERROR"

# 查询慢查询
{job="postgresql"} | json | duration > 1000

# 查询特定数据库
{job="postgresql"} | json | db="mydb"
```

---

## 🔍 Traces收集

### 应用集成

#### Python (psycopg2)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

# 初始化追踪
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# 配置导出器
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 自动追踪psycopg2
Psycopg2Instrumentor().instrument()

# 使用示例
import psycopg2
conn = psycopg2.connect("dbname=mydb user=postgres")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
```

#### Java (JDBC)

```java
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.instrumentation.jdbc.OpenTelemetryDriver;

// 注册OpenTelemetry JDBC驱动
Class.forName("io.opentelemetry.instrumentation.jdbc.OpenTelemetryDriver");

// 使用标准JDBC连接
String url = "jdbc:otel:postgresql://localhost:5432/mydb";
Connection conn = DriverManager.getConnection(url, "user", "password");
```

#### Go (database/sql)

```go
import (
    "database/sql"
    _ "github.com/jackc/pgx/v5/stdlib"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/sdk/trace"
    "go.opentelemetry.io/contrib/instrumentation/database/sql/otelsql"
)

// 初始化追踪
exporter, _ := otlptracegrpc.New(context.Background(),
    otlptracegrpc.WithEndpoint("otel-collector:4317"))
tp := trace.NewTracerProvider(trace.WithBatcher(exporter))
otel.SetTracerProvider(tp)

// 使用otelsql包装
db, _ := otelsql.Open("pgx", "postgres://user:password@localhost/mydb",
    otelsql.WithAttributes(attribute.String("db.system", "postgresql")))
```

### Tempo集成

#### 配置Tempo

```yaml
# tempo-config.yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

ingester:
  max_block_duration: 5m

compactor:
  compaction:
    block_retention: 1h

storage:
  trace:
    backend: local
    local:
      path: /var/tempo/traces
```

#### 查询追踪

```bash
# 使用Tempo API查询
curl "http://tempo:3200/api/traces?tags=db.name=mydb"

# 使用TraceQL查询
curl "http://tempo:3200/api/search?tags=db.name=mydb&limit=10"
```

---

## 📊 Grafana LGTM+ Stack

### 架构介绍

LGTM+ Stack包括：
- **Loki**: 日志聚合
- **Grafana**: 可视化
- **Tempo**: 追踪存储
- **Mimir**: Metrics存储（可选）

### Docker Compose部署

```yaml
# docker-compose-lgtm.yml
version: '3.8'

services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml
    command: -config.file=/etc/loki/local-config.yaml

  tempo:
    image: grafana/tempo:latest
    ports:
      - "3200:3200"
      - "4317:4317"
      - "4318:4318"
    volumes:
      - ./tempo-config.yaml:/etc/tempo/tempo.yaml
      - tempo-data:/var/tempo
    command: -config.file=/etc/tempo/tempo.yaml

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  loki-data:
  tempo-data:
  prometheus-data:
  grafana-data:
```

### Grafana数据源配置

#### 配置Prometheus

1. 进入Grafana: http://localhost:3000
2. Configuration → Data Sources → Add data source
3. 选择Prometheus
4. URL: http://prometheus:9090
5. Save & Test

#### 配置Loki

1. Add data source → Loki
2. URL: http://loki:3100
3. Save & Test

#### 配置Tempo

1. Add data source → Tempo
2. URL: http://tempo:3200
3. 关联Prometheus数据源（用于服务映射）
4. Save & Test

### 仪表板配置

#### PostgreSQL Metrics仪表板

```json
{
  "dashboard": {
    "title": "PostgreSQL Metrics",
    "panels": [
      {
        "title": "Database Connections",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "{{datname}}"
          }
        ]
      },
      {
        "title": "Query TPS",
        "targets": [
          {
            "expr": "rate(pg_stat_database_xact_commit[5m]) + rate(pg_stat_database_xact_rollback[5m])",
            "legendFormat": "{{datname}}"
          }
        ]
      },
      {
        "title": "Cache Hit Ratio",
        "targets": [
          {
            "expr": "sum(rate(pg_stat_database_blks_hit[5m])) / sum(rate(pg_stat_database_blks_hit[5m]) + rate(pg_stat_database_blks_read[5m]))",
            "legendFormat": "Hit Ratio"
          }
        ]
      }
    ]
  }
}
```

---

## 🎯 生产最佳实践

### 性能优化

#### 采样策略

```yaml
# 降低追踪采样率
processors:
  probabilistic_sampler:
    sampling_percentage: 10  # 只采样10%的请求
```

#### 数据压缩

```yaml
exporters:
  otlp:
    compression: gzip
```

#### 存储优化

```yaml
# Tempo存储配置
storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      region: us-east-1
```

### 成本控制

#### 数据保留策略

```yaml
# Loki保留策略
limits_config:
  retention_period: 168h  # 7天

# Tempo保留策略
compactor:
  compaction:
    block_retention: 720h  # 30天
```

#### 采样配置

```yaml
# 根据服务重要性采样
processors:
  tail_sampling:
    policies:
      - name: high-priority
        type: string_attribute
        string_attribute:
          key: priority
          values: ["high"]
          sampling_percentage: 100
      - name: low-priority
        type: string_attribute
        string_attribute:
          key: priority
          values: ["low"]
          sampling_percentage: 1
```

### 安全考虑

#### TLS加密

```yaml
exporters:
  otlp:
    endpoint: tempo:4317
    tls:
      cert_file: /path/to/cert.pem
      key_file: /path/to/key.pem
      ca_file: /path/to/ca.pem
```

#### 访问控制

```yaml
# Grafana认证
auth:
  anonymous:
    enabled: false
  basic_auth:
    enabled: true
```

---

## 💼 实战案例

### 案例1: 单机部署

#### 场景描述

- 单PostgreSQL实例
- 完整的可观测性
- 成本控制

#### 实施方案

```bash
# 启动LGTM+ Stack
docker-compose -f docker-compose-lgtm.yml up -d

# 配置PostgreSQL Exporter
docker run -d \
  --name postgres-exporter \
  -p 9187:9187 \
  -e DATA_SOURCE_NAME="postgresql://user:pass@localhost/db" \
  prometheuscommunity/postgres-exporter

# 配置应用追踪
# (使用上述Python/Java/Go示例)
```

#### 效果评估

- ✅ **Metrics**: 完整收集
- ✅ **Logs**: 集中管理
- ✅ **Traces**: 分布式追踪
- ✅ **成本**: 可控

### 案例2: 分布式部署

#### 场景描述

- 多PostgreSQL实例
- 跨服务追踪
- 统一监控

#### 实施方案

```yaml
# 多实例配置
scrape_configs:
  - job_name: 'postgresql-primary'
    static_configs:
      - targets: ['pg-primary:9187']

  - job_name: 'postgresql-replica'
    static_configs:
      - targets: ['pg-replica-1:9187', 'pg-replica-2:9187']
```

#### 效果评估

- ✅ **统一视图**: 所有实例统一监控
- ✅ **关联分析**: 跨服务追踪
- ✅ **故障定位**: 快速定位问题

---

## 📚 参考资源

### 官方资源

- **OpenTelemetry官网**: https://opentelemetry.io/
- **PostgreSQL Exporter**: https://github.com/prometheus-community/postgres_exporter
- **Grafana LGTM+**: https://grafana.com/docs/lgtm/
- **Tempo文档**: https://grafana.com/docs/tempo/

### 相关文档

- [监控与可观测性完整体系指南](../12-监控与诊断/PostgreSQL可观测性完整指南.md)
- [Prometheus监控配置](../12-监控与诊断/README.md)

---

## 📝 更新日志

| 日期 | 版本 | 说明 |
|------|------|------|
| 2025-01-29 | v1.0 | 初始版本，基于OpenTelemetry最新标准 |

---

**文档维护者**: PostgreSQL_Modern Documentation Team
**最后更新**: 2025年1月29日
**文档状态**: ✅ 完整

---

*本文档基于OpenTelemetry官方标准和最佳实践编写，建议定期查看官方文档获取最新信息。*
