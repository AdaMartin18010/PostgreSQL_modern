# PostgreSQL MVCC-ACID Grafana仪表盘配置

> **文档编号**: OPS-GRAFANA-001
> **主题**: Grafana仪表盘配置
> **版本**: PostgreSQL 17 & 18

---

## 📑 目录

- [PostgreSQL MVCC-ACID Grafana仪表盘配置](#postgresql-mvcc-acid-grafana仪表盘配置)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔍 第一部分：数据源配置](#-第一部分数据源配置)
    - [1.1 Prometheus数据源](#11-prometheus数据源)
    - [1.2 PostgreSQL数据源](#12-postgresql数据源)
  - [🚀 第二部分：事务监控仪表盘](#-第二部分事务监控仪表盘)
    - [2.1 活动事务面板](#21-活动事务面板)
    - [2.2 长事务面板](#22-长事务面板)
    - [2.3 事务状态分布](#23-事务状态分布)
  - [📊 第三部分：锁监控仪表盘](#-第三部分锁监控仪表盘)
    - [3.1 锁等待面板](#31-锁等待面板)
    - [3.2 锁持有面板](#32-锁持有面板)
    - [3.3 死锁面板](#33-死锁面板)
  - [🔧 第四部分：表膨胀监控仪表盘](#-第四部分表膨胀监控仪表盘)
    - [4.1 死亡元组面板](#41-死亡元组面板)
    - [4.2 表大小面板](#42-表大小面板)
    - [4.3 VACUUM面板](#43-vacuum面板)
  - [📈 第五部分：XID年龄监控仪表盘](#-第五部分xid年龄监控仪表盘)
    - [5.1 XID年龄面板](#51-xid年龄面板)
    - [5.2 回卷风险面板](#52-回卷风险面板)
  - [🎯 第六部分：性能监控仪表盘](#-第六部分性能监控仪表盘)
    - [6.1 查询性能面板](#61-查询性能面板)
    - [6.2 连接监控面板](#62-连接监控面板)
    - [6.3 复制监控面板](#63-复制监控面板)
  - [📝 总结](#-总结)
    - [核心仪表盘](#核心仪表盘)
    - [最佳实践](#最佳实践)

---

## 📋 概述

Grafana是PostgreSQL MVCC-ACID监控的可视化工具，通过丰富的仪表盘展示关键指标，帮助运维人员快速了解数据库状态。本文档详细说明Grafana仪表盘的配置方法。

---

## 🔍 第一部分：数据源配置

### 1.1 Prometheus数据源

```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://localhost:9090",
  "access": "proxy",
  "isDefault": true,
  "jsonData": {
    "timeInterval": "15s",
    "httpMethod": "POST"
  }
}
```

### 1.2 PostgreSQL数据源

```json
{
  "name": "PostgreSQL",
  "type": "postgres",
  "url": "localhost:5432",
  "database": "postgres",
  "user": "postgres",
  "secureJsonData": {
    "password": "password"
  },
  "jsonData": {
    "sslmode": "disable",
    "maxOpenConns": 100,
    "maxIdleConns": 100,
    "connMaxLifetime": 14400
  }
}
```

---

## 🚀 第二部分：事务监控仪表盘

### 2.1 活动事务面板

**Panel配置**:

- **Title**: 活动事务数量
- **Query**: `sum(pg_stat_activity_count{state="active"})`
- **Type**: Stat
- **Unit**: short
- **Thresholds**:
  - Green: 0-50
  - Yellow: 50-100
  - Red: 100+

**Panel JSON**:

```json
{
  "targets": [
    {
      "expr": "sum(pg_stat_activity_count{state=\"active\"})",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": 0, "color": "green"},
          {"value": 50, "color": "yellow"},
          {"value": 100, "color": "red"}
        ]
      }
    }
  }
}
```

### 2.2 长事务面板

**Panel配置**:

- **Title**: 长事务（>5分钟）
- **Query**: `pg_stat_activity_max_xact_duration{state="active"} > 300`
- **Type**: Table
- **Columns**: pid, datname, duration, query

**Panel JSON**:

```json
{
  "targets": [
    {
      "expr": "pg_stat_activity_max_xact_duration{state=\"active\"} > 300",
      "refId": "A",
      "format": "table"
    }
  ],
  "transformations": [
    {
      "id": "organize",
      "options": {
        "excludeByName": {},
        "indexByName": {},
        "renameByName": {
          "Value": "Duration (s)",
          "pid": "PID",
          "datname": "Database"
        }
      }
    }
  ]
}
```

### 2.3 事务状态分布

**Panel配置**:

- **Title**: 事务状态分布
- **Query**: `sum by (state) (pg_stat_activity_count)`
- **Type**: Pie Chart

**Panel JSON**:

```json
{
  "targets": [
    {
      "expr": "sum by (state) (pg_stat_activity_count)",
      "refId": "A",
      "legendFormat": "{{state}}"
    }
  ],
  "options": {
    "pieType": "pie",
    "tooltip": {
      "mode": "single"
    },
    "legend": {
      "displayMode": "table",
      "placement": "right"
    }
  }
}
```

---

## 📊 第三部分：锁监控仪表盘

### 3.1 锁等待面板

**Panel配置**:

- **Title**: 锁等待数量
- **Query**: `pg_locks_waiting`
- **Type**: Graph
- **Y-axis**: Lock Waits

**Panel JSON**:

```json
{
  "targets": [
    {
      "expr": "pg_locks_waiting",
      "refId": "A",
      "legendFormat": "Lock Waits"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": 0, "color": "green"},
          {"value": 5, "color": "yellow"},
          {"value": 10, "color": "red"}
        ]
      }
    }
  }
}
```

### 3.2 锁持有面板

**Panel配置**:

- **Title**: 锁持有数量
- **Query**: `pg_locks_held`
- **Type**: Stat
- **Unit**: short

### 3.3 死锁面板

**Panel配置**:

- **Title**: 死锁次数（5分钟）
- **Query**: `increase(pg_stat_database_deadlocks[5m])`
- **Type**: Graph

---

## 🔧 第四部分：表膨胀监控仪表盘

### 4.1 死亡元组面板

**Panel配置**:

- **Title**: Top 10 死亡元组最多的表
- **Query**: `topk(10, pg_stat_user_tables_n_dead_tup)`
- **Type**: Bar Chart

**Panel JSON**:

```json
{
  "targets": [
    {
      "expr": "topk(10, pg_stat_user_tables_n_dead_tup)",
      "refId": "A",
      "legendFormat": "{{schemaname}}.{{relname}}"
    }
  ],
  "options": {
    "orientation": "horizontal",
    "xTickAlignment": "center"
  }
}
```

### 4.2 表大小面板

**Panel配置**:

- **Title**: Top 10 最大的表
- **Query**: `topk(10, pg_stat_user_tables_size_bytes)`
- **Type**: Bar Chart
- **Unit**: bytes

### 4.3 VACUUM面板

**Panel配置**:

- **Title**: VACUUM执行时间
- **Query**: `pg_stat_progress_vacuum_elapsed_time`
- **Type**: Graph
- **Unit**: seconds

---

## 📈 第五部分：XID年龄监控仪表盘

### 5.1 XID年龄面板

**Panel配置**:

- **Title**: 数据库XID年龄
- **Query**: `pg_database_age_datfrozenxid`
- **Type**: Gauge
- **Unit**: none
- **Max**: 2000000000
- **Thresholds**:
  - Green: 0-1000000000
  - Yellow: 1000000000-1500000000
  - Red: 1500000000+

**Panel JSON**:

```json
{
  "targets": [
    {
      "expr": "pg_database_age_datfrozenxid",
      "refId": "A",
      "legendFormat": "{{datname}}"
    }
  ],
  "options": {
    "min": 0,
    "max": 2000000000,
    "thresholds": {
      "mode": "absolute",
      "steps": [
        {"value": 0, "color": "green"},
        {"value": 1000000000, "color": "yellow"},
        {"value": 1500000000, "color": "red"}
      ]
    }
  }
}
```

### 5.2 回卷风险面板

**Panel配置**:

- **Title**: XID回卷风险
- **Query**: `(2147483647 - pg_database_age_datfrozenxid) / 2147483647 * 100`
- **Type**: Stat
- **Unit**: percent
- **Thresholds**:
  - Red: 0-10
  - Yellow: 10-20
  - Green: 20+

---

## 🎯 第六部分：性能监控仪表盘

### 6.1 查询性能面板

**Panel配置**:

- **Title**: 慢查询（>1秒）
- **Query**: `pg_stat_statements_mean_exec_time > 1000`
- **Type**: Table

### 6.2 连接监控面板

**Panel配置**:

- **Title**: 连接使用率
- **Query**: `pg_stat_database_numbackends / pg_settings_max_connections * 100`
- **Type**: Gauge
- **Unit**: percent

### 6.3 复制监控面板

**Panel配置**:

- **Title**: 复制延迟
- **Query**: `pg_replication_lag_bytes`
- **Type**: Graph
- **Unit**: bytes

---

## 📝 总结

### 核心仪表盘

1. **事务监控仪表盘**：活动事务、长事务、事务状态
2. **锁监控仪表盘**：锁等待、锁持有、死锁
3. **表膨胀监控仪表盘**：死亡元组、表大小、VACUUM
4. **XID年龄监控仪表盘**：XID年龄、回卷风险
5. **性能监控仪表盘**：查询性能、连接、复制

### 最佳实践

1. **合理布局**：按功能分组，重要指标放在顶部
2. **颜色编码**：使用统一的颜色表示状态（绿/黄/红）
3. **阈值设置**：设置合理的告警阈值
4. **时间范围**：提供多个时间范围选择
5. **刷新间隔**：设置合适的自动刷新间隔（30秒-1分钟）

PostgreSQL 17/18的MVCC机制需要全面的Grafana监控，通过丰富的仪表盘，可以直观地了解数据库状态，及时发现和解决问题。
