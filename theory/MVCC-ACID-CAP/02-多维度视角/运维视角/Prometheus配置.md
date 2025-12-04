# PostgreSQL MVCC-ACID Prometheus监控配置

> **文档编号**: OPS-PROMETHEUS-001
> **主题**: Prometheus监控配置
> **版本**: PostgreSQL 17 & 18

---

## 📑 目录

- [PostgreSQL MVCC-ACID Prometheus监控配置](#postgresql-mvcc-acid-prometheus监控配置)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔍 第一部分：PostgreSQL Exporter配置](#-第一部分postgresql-exporter配置)
    - [1.1 安装和配置](#11-安装和配置)
      - [安装postgres\_exporter](#安装postgres_exporter)
      - [配置连接](#配置连接)
      - [启动exporter](#启动exporter)
    - [1.2 指标收集配置](#12-指标收集配置)
      - [查询配置](#查询配置)
      - [自定义查询](#自定义查询)
      - [指标标签](#指标标签)
  - [🚀 第二部分：Prometheus服务器配置](#-第二部分prometheus服务器配置)
    - [2.1 基本配置](#21-基本配置)
      - [prometheus.yml配置](#prometheusyml配置)
      - [抓取配置](#抓取配置)
      - [存储配置](#存储配置)
    - [2.2 告警规则配置](#22-告警规则配置)
      - [事务告警规则](#事务告警规则)
      - [锁告警规则](#锁告警规则)
      - [表膨胀告警规则](#表膨胀告警规则)
      - [XID年龄告警规则](#xid年龄告警规则)
    - [2.3 记录规则配置](#23-记录规则配置)
      - [聚合规则](#聚合规则)
      - [计算规则](#计算规则)
  - [📊 第三部分：关键指标说明](#-第三部分关键指标说明)
    - [3.1 事务指标](#31-事务指标)
    - [3.2 锁指标](#32-锁指标)
    - [3.3 表膨胀指标](#33-表膨胀指标)
    - [3.4 XID年龄指标](#34-xid年龄指标)
  - [🔧 第四部分：高可用配置](#-第四部分高可用配置)
    - [4.1 Prometheus高可用](#41-prometheus高可用)
    - [4.2 服务发现配置](#42-服务发现配置)
  - [📝 总结](#-总结)
    - [核心配置](#核心配置)
    - [关键告警](#关键告警)
    - [最佳实践](#最佳实践)

---

## 📋 概述

Prometheus是PostgreSQL MVCC-ACID监控的核心组件，通过postgres_exporter收集PostgreSQL指标，Prometheus服务器存储和查询这些指标，并提供告警功能。本文档详细说明Prometheus的完整配置。

---

## 🔍 第一部分：PostgreSQL Exporter配置

### 1.1 安装和配置

#### 安装postgres_exporter

```bash
# 下载postgres_exporter
wget https://github.com/prometheus-community/postgres_exporter/releases/download/v0.15.0/postgres_exporter-0.15.0.linux-amd64.tar.gz

# 解压
tar -xzf postgres_exporter-0.15.0.linux-amd64.tar.gz
cd postgres_exporter-0.15.0.linux-amd64

# 复制到系统目录
sudo cp postgres_exporter /usr/local/bin/
sudo chmod +x /usr/local/bin/postgres_exporter
```

#### 配置连接

```bash
# 创建PostgreSQL监控用户
sudo -u postgres psql <<EOF
CREATE USER postgres_exporter WITH PASSWORD 'password';
ALTER USER postgres_exporter SET SEARCH_PATH TO postgres_exporter,pg_catalog;
GRANT CONNECT ON DATABASE postgres TO postgres_exporter;
GRANT pg_monitor TO postgres_exporter;
EOF

# 创建配置文件
sudo mkdir -p /etc/postgres_exporter
sudo tee /etc/postgres_exporter/.env <<EOF
DATA_SOURCE_NAME="postgresql://postgres_exporter:password@localhost:5432/postgres?sslmode=disable"
EOF
```

#### 启动exporter

```bash
# 创建systemd服务
sudo tee /etc/systemd/system/postgres_exporter.service <<EOF
[Unit]
Description=PostgreSQL Exporter
After=network.target

[Service]
Type=simple
User=postgres
EnvironmentFile=/etc/postgres_exporter/.env
ExecStart=/usr/local/bin/postgres_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable postgres_exporter
sudo systemctl start postgres_exporter

# 检查状态
sudo systemctl status postgres_exporter
```

### 1.2 指标收集配置

#### 查询配置

```yaml
# queries.yaml - 自定义查询配置
pg_stat_database:
  query: |
    SELECT
      datname,
      numbackends,
      xact_commit,
      xact_rollback,
      blks_read,
      blks_hit,
      tup_returned,
      tup_fetched,
      tup_inserted,
      tup_updated,
      tup_deleted,
      conflicts,
      temp_files,
      temp_bytes,
      deadlocks,
      blk_read_time,
      blk_write_time,
      stats_reset
    FROM pg_stat_database
    WHERE datname NOT IN ('template0', 'template1', 'postgres')
  metrics:
    - datname:
        usage: "LABEL"
        description: "Database name"
    - numbackends:
        usage: "GAUGE"
        description: "Number of backends currently connected to this database"
    - xact_commit:
        usage: "COUNTER"
        description: "Number of transactions in this database that have been committed"
    - xact_rollback:
        usage: "COUNTER"
        description: "Number of transactions in this database that have been rolled back"
    - deadlocks:
        usage: "COUNTER"
        description: "Number of deadlocks detected in this database"
```

#### 自定义查询

```yaml
# 自定义MVCC相关查询
pg_stat_user_tables_mvcc:
  query: |
    SELECT
      schemaname,
      relname,
      n_live_tup,
      n_dead_tup,
      n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0) as dead_ratio,
      last_vacuum,
      last_autovacuum,
      vacuum_count,
      autovacuum_count
    FROM pg_stat_user_tables
    WHERE n_dead_tup > 0
  metrics:
    - schemaname:
        usage: "LABEL"
    - relname:
        usage: "LABEL"
    - n_live_tup:
        usage: "GAUGE"
        description: "Estimated number of live tuples"
    - n_dead_tup:
        usage: "GAUGE"
        description: "Estimated number of dead tuples"
    - dead_ratio:
        usage: "GAUGE"
        description: "Dead tuple ratio percentage"
```

#### 指标标签

```yaml
# 添加自定义标签
pg_stat_activity_mvcc:
  query: |
    SELECT
      datname,
      state,
      count(*) as count,
      avg(EXTRACT(EPOCH FROM (now() - xact_start))) as avg_xact_duration,
      max(EXTRACT(EPOCH FROM (now() - xact_start))) as max_xact_duration
    FROM pg_stat_activity
    WHERE datname IS NOT NULL
    GROUP BY datname, state
  metrics:
    - datname:
        usage: "LABEL"
    - state:
        usage: "LABEL"
    - count:
        usage: "GAUGE"
        description: "Number of connections in this state"
    - avg_xact_duration:
        usage: "GAUGE"
        description: "Average transaction duration in seconds"
    - max_xact_duration:
        usage: "GAUGE"
        description: "Maximum transaction duration in seconds"
```

---

## 🚀 第二部分：Prometheus服务器配置

### 2.1 基本配置

#### prometheus.yml配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s      # 抓取间隔
  evaluation_interval: 15s  # 告警评估间隔
  external_labels:
    cluster: 'production'
    environment: 'prod'

# 告警规则文件
rule_files:
  - "rules/*.yml"

# 抓取配置
scrape_configs:
  # PostgreSQL Exporter
  - job_name: 'postgresql'
    static_configs:
      - targets: ['localhost:9187']
        labels:
          instance: 'postgresql-primary'
          role: 'primary'

    # 抓取超时
    scrape_timeout: 10s

    # 指标路径
    metrics_path: '/metrics'

    # 重试配置
    scrape_interval: 15s

    # 标签重写
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9187

# 存储配置
storage:
  tsdb:
    path: /var/lib/prometheus
    retention.time: 30d      # 保留30天
    retention.size: 50GB     # 最大50GB

# 远程写入配置（可选）
# remote_write:
#   - url: "http://remote-prometheus:9090/api/v1/write"
```

#### 抓取配置

```yaml
# 多实例配置
scrape_configs:
  - job_name: 'postgresql-primary'
    static_configs:
      - targets: ['primary-db:9187']
        labels:
          instance: 'postgresql-primary'
          role: 'primary'

  - job_name: 'postgresql-replica'
    static_configs:
      - targets: ['replica-db-1:9187', 'replica-db-2:9187']
        labels:
          role: 'replica'

  # 服务发现配置（Consul）
  - job_name: 'postgresql-consul'
    consul_sd_configs:
      - server: 'localhost:8500'
        services: ['postgresql']
    relabel_configs:
      - source_labels: [__meta_consul_service]
        target_label: job
```

#### 存储配置

```yaml
# 存储配置优化
storage:
  tsdb:
    path: /var/lib/prometheus
    retention.time: 90d      # 保留90天
    retention.size: 100GB    # 最大100GB

    # WAL配置
    wal-compression: true

    # 块配置
    min-block-duration: 2h
    max-block-duration: 24h
```

### 2.2 告警规则配置

#### 事务告警规则

```yaml
# rules/postgresql_transactions.yml
groups:
  - name: postgresql_transactions
    interval: 30s
    rules:
      # 长事务告警
      - alert: PostgreSQLLongTransaction
        expr: |
          pg_stat_activity_max_xact_duration{state="active"} > 300
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL long transaction detected"
          description: "Transaction {{ $labels.instance }} has been running for {{ $value }}s"

      # 活动事务过多
      - alert: PostgreSQLTooManyActiveTransactions
        expr: |
          sum(pg_stat_activity_count{state="active"}) > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Too many active transactions"
          description: "{{ $value }} active transactions detected"

      # 阻塞事务
      - alert: PostgreSQLBlockedTransactions
        expr: |
          pg_stat_activity_count{state="active", wait_event_type="Lock"} > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL blocked transactions"
          description: "{{ $value }} transactions are blocked"
```

#### 锁告警规则

```yaml
# rules/postgresql_locks.yml
groups:
  - name: postgresql_locks
    interval: 30s
    rules:
      # 锁等待过多
      - alert: PostgreSQLLockWaits
        expr: |
          pg_locks_waiting > 10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL lock waits detected"
          description: "{{ $value }} locks are waiting"

      # 死锁检测
      - alert: PostgreSQLDeadlocks
        expr: |
          increase(pg_stat_database_deadlocks[5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL deadlocks detected"
          description: "{{ $value }} deadlocks in the last 5 minutes"
```

#### 表膨胀告警规则

```yaml
# rules/postgresql_bloat.yml
groups:
  - name: postgresql_bloat
    interval: 1m
    rules:
      # 死亡元组过多
      - alert: PostgreSQLTooManyDeadTuples
        expr: |
          pg_stat_user_tables_n_dead_tup > 10000000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Too many dead tuples"
          description: "Table {{ $labels.schemaname }}.{{ $labels.relname }} has {{ $value }} dead tuples"

      # 表膨胀率过高
      - alert: PostgreSQLTableBloat
        expr: |
          pg_stat_user_tables_dead_ratio > 20
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Table bloat detected"
          description: "Table {{ $labels.schemaname }}.{{ $labels.relname }} has {{ $value }}% dead tuples"

      # VACUUM未执行
      - alert: PostgreSQLVacuumNotRun
        expr: |
          (time() - pg_stat_user_tables_last_autovacuum) > 86400
            and pg_stat_user_tables_n_dead_tup > 1000000
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "VACUUM not run recently"
          description: "Table {{ $labels.schemaname }}.{{ $labels.relname }} has not been vacuumed for {{ $value }}s"
```

#### XID年龄告警规则

```yaml
# rules/postgresql_xid_age.yml
groups:
  - name: postgresql_xid_age
    interval: 1m
    rules:
      # XID年龄过高
      - alert: PostgreSQLHighXIDAge
        expr: |
          pg_database_age_datfrozenxid > 1000000000
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "High XID age detected"
          description: "Database {{ $labels.datname }} has XID age of {{ $value }}"

      # XID回卷风险
      - alert: PostgreSQLXIDWraparoundRisk
        expr: |
          pg_database_age_datfrozenxid > 1800000000
        for: 30m
        labels:
          severity: critical
        annotations:
          summary: "XID wraparound risk"
          description: "Database {{ $labels.datname }} is at risk of XID wraparound (age: {{ $value }})"

      # 表XID年龄过高
      - alert: PostgreSQLHighTableXIDAge
        expr: |
          pg_stat_user_tables_age_relfrozenxid > 1000000000
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "High table XID age"
          description: "Table {{ $labels.schemaname }}.{{ $labels.relname }} has XID age of {{ $value }}"
```

### 2.3 记录规则配置

#### 聚合规则

```yaml
# rules/postgresql_recording.yml
groups:
  - name: postgresql_recording
    interval: 30s
    rules:
      # 事务速率
      - record: postgresql:transactions:rate
        expr: |
          rate(pg_stat_database_xact_commit[5m]) + rate(pg_stat_database_xact_rollback[5m])

      # 查询速率
      - record: postgresql:queries:rate
        expr: |
          rate(pg_stat_database_tup_returned[5m]) + rate(pg_stat_database_tup_fetched[5m])

      # 缓存命中率
      - record: postgresql:cache:hit_ratio
        expr: |
          rate(pg_stat_database_blks_hit[5m]) /
          (rate(pg_stat_database_blks_hit[5m]) + rate(pg_stat_database_blks_read[5m]))
```

#### 计算规则

```yaml
      # 表膨胀率
      - record: postgresql:table:bloat_ratio
        expr: |
          pg_stat_user_tables_n_dead_tup /
          NULLIF(pg_stat_user_tables_n_live_tup + pg_stat_user_tables_n_dead_tup, 0) * 100

      # XID剩余
      - record: postgresql:xid:remaining
        expr: |
          2147483647 - pg_database_age_datfrozenxid

      # 连接使用率
      - record: postgresql:connections:usage_ratio
        expr: |
          pg_stat_database_numbackends /
          pg_settings_max_connections * 100
```

---

## 📊 第三部分：关键指标说明

### 3.1 事务指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `pg_stat_activity_count` | GAUGE | 活动连接数 |
| `pg_stat_activity_max_xact_duration` | GAUGE | 最长事务持续时间（秒） |
| `pg_stat_database_xact_commit` | COUNTER | 提交的事务数 |
| `pg_stat_database_xact_rollback` | COUNTER | 回滚的事务数 |
| `pg_stat_database_deadlocks` | COUNTER | 死锁次数 |

### 3.2 锁指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `pg_locks_waiting` | GAUGE | 等待的锁数量 |
| `pg_locks_held` | GAUGE | 持有的锁数量 |
| `pg_locks_wait_duration` | GAUGE | 锁等待时间（秒） |

### 3.3 表膨胀指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `pg_stat_user_tables_n_live_tup` | GAUGE | 存活元组数 |
| `pg_stat_user_tables_n_dead_tup` | GAUGE | 死亡元组数 |
| `pg_stat_user_tables_dead_ratio` | GAUGE | 死亡元组比例（%） |
| `pg_stat_user_tables_last_autovacuum` | GAUGE | 最后autovacuum时间（Unix时间戳） |

### 3.4 XID年龄指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `pg_database_age_datfrozenxid` | GAUGE | 数据库XID年龄 |
| `pg_stat_user_tables_age_relfrozenxid` | GAUGE | 表XID年龄 |
| `pg_xid_remaining` | GAUGE | XID剩余数量 |

---

## 🔧 第四部分：高可用配置

### 4.1 Prometheus高可用

```yaml
# Prometheus高可用配置
# 使用Prometheus联邦或Thanos

# 联邦配置
scrape_configs:
  - job_name: 'federate'
    scrape_interval: 15s
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job=~"postgresql.*"}'
    static_configs:
      - targets:
          - 'prometheus-1:9090'
          - 'prometheus-2:9090'
```

### 4.2 服务发现配置

```yaml
# Consul服务发现
scrape_configs:
  - job_name: 'postgresql-consul'
    consul_sd_configs:
      - server: 'consul:8500'
        services: ['postgresql']
    relabel_configs:
      - source_labels: [__meta_consul_service]
        target_label: job
      - source_labels: [__meta_consul_service_id]
        target_label: instance
```

---

## 📝 总结

### 核心配置

1. **PostgreSQL Exporter**：收集PostgreSQL指标
2. **Prometheus服务器**：存储和查询指标
3. **告警规则**：定义告警条件
4. **记录规则**：预计算常用指标

### 关键告警

- ✅ 长事务告警（>5分钟）
- ✅ 活动事务过多（>100）
- ✅ 锁等待过多（>10）
- ✅ 死亡元组过多（>1000万）
- ✅ XID年龄过高（>10亿）

### 最佳实践

1. **合理设置抓取间隔**：15-30秒
2. **配置告警规则**：覆盖所有关键指标
3. **使用记录规则**：预计算常用指标
4. **高可用配置**：使用联邦或Thanos
5. **定期检查**：检查告警规则和指标收集

PostgreSQL 17/18的MVCC机制需要全面的Prometheus监控，通过合理配置，可以及时发现和预防问题，确保数据库稳定运行。
