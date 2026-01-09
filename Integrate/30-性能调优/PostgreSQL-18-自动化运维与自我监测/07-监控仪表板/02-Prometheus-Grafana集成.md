# 7.2 Prometheus + Grafana集成方案

> **所属主题**: 07-监控仪表板
> **章节编号**: 7.2
> **创建日期**: 2025年1月
> **PostgreSQL版本**: 18+
> **难度等级**: ⭐⭐⭐⭐
> **相关章节**: [7.1 监控仪表板设计](./01-监控仪表板设计.md) | [08-性能调优案例](../08-性能调优案例/README.md)

---

## 📋 目录

- [7.2 Prometheus + Grafana集成方案](#72-prometheus--grafana集成方案)
  - [📋 目录](#-目录)
  - [7.2.1 概述与背景](#721-概述与背景)
  - [7.2.2 Prometheus配置](#722-prometheus配置)
    - [7.2.2.1 PostgreSQL 18 Prometheus导出器配置](#7221-postgresql-18-prometheus导出器配置)
    - [7.2.2.2 安装PostgreSQL Exporter](#7222-安装postgresql-exporter)
  - [7.2.3 Grafana仪表板配置](#723-grafana仪表板配置)
    - [7.2.3.1 PostgreSQL 18关键指标仪表板](#7231-postgresql-18关键指标仪表板)
  - [7.2.4 PostgreSQL 18特定指标](#724-postgresql-18特定指标)
    - [7.2.4.1 I/O性能指标](#7241-io性能指标)
    - [7.2.4.2 并行查询指标（PostgreSQL 18）](#7242-并行查询指标postgresql-18)
    - [7.2.4.3 检查点指标（PostgreSQL 18）](#7243-检查点指标postgresql-18)
  - [7.2.5 Grafana面板配置示例](#725-grafana面板配置示例)
    - [7.2.5.1 缓存命中率面板](#7251-缓存命中率面板)
    - [7.2.5.2 I/O吞吐量面板（PostgreSQL 18）](#7252-io吞吐量面板postgresql-18)
    - [7.2.5.3 并行查询效率面板（PostgreSQL 18）](#7253-并行查询效率面板postgresql-18)
  - [7.2.6 告警规则配置](#726-告警规则配置)
    - [7.2.6.1 Prometheus告警规则](#7261-prometheus告警规则)
  - [7.2.7 部署步骤](#727-部署步骤)
    - [7.2.7.1 安装Prometheus](#7271-安装prometheus)
    - [7.2.7.2 安装Grafana](#7272-安装grafana)
    - [7.2.7.3 配置数据源](#7273-配置数据源)
    - [7.2.7.4 导入仪表板](#7274-导入仪表板)
  - [7.2.8 注意事项与最佳实践](#728-注意事项与最佳实践)
    - [7.2.8.1 PostgreSQL 18增强特性](#7281-postgresql-18增强特性)
    - [7.2.8.2 注意事项](#7282-注意事项)
    - [7.2.8.3 最佳实践](#7283-最佳实践)
  - [7.2.9 导航](#729-导航)
    - [7.2.9.1 章节导航](#7291-章节导航)
    - [7.2.9.2 相关章节](#7292-相关章节)
  - [📚 相关资源](#-相关资源)

---

## 7.2.1 概述与背景

Prometheus + Grafana集成方案提供了完整的PostgreSQL 18监控可视化解决方案，支持PostgreSQL 18新增的I/O统计、并行查询追踪等特性。

---

## 7.2.2 Prometheus配置

### 7.2.2.1 PostgreSQL 18 Prometheus导出器配置

```yaml
# prometheus.yml - PostgreSQL 18监控配置
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'postgresql18'
    static_configs:
      - targets: ['localhost:9187']
    scrape_interval: 15s
    metrics_path: /metrics

    # PostgreSQL 18特定指标
    params:
      include:
        - pg_stat_io
        - pg_stat_statements
        - pg_stat_activity
        - pg_stat_checkpointer
```

### 7.2.2.2 安装PostgreSQL Exporter

```bash
# 下载PostgreSQL Exporter
wget https://github.com/prometheus-community/postgres_exporter/releases/latest/download/postgres_exporter-*.tar.gz

# 解压
tar -xzf postgres_exporter-*.tar.gz

# 配置环境变量
export DATA_SOURCE_NAME="postgresql://postgres:password@localhost:5432/postgres?sslmode=disable"

# 启动Exporter
./postgres_exporter
```

---

## 7.2.3 Grafana仪表板配置

### 7.2.3.1 PostgreSQL 18关键指标仪表板

```json
{
  "dashboard": {
    "title": "PostgreSQL 18 自动化运维监控",
    "panels": [
      {
        "title": "缓存命中率",
        "targets": [
          {
            "expr": "100 * (pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read))",
            "legendFormat": "缓存命中率"
          }
        ],
        "thresholds": [
          {"value": 0, "color": "red"},
          {"value": 90, "color": "yellow"},
          {"value": 95, "color": "green"}
        ]
      },
      {
        "title": "I/O吞吐量 (PostgreSQL 18)",
        "targets": [
          {
            "expr": "sum(pg_stat_io_read_bytes + pg_stat_io_write_bytes) / 1024 / 1024 / 1024",
            "legendFormat": "I/O吞吐量(GB)"
          }
        ]
      },
      {
        "title": "并行查询效率 (PostgreSQL 18)",
        "targets": [
          {
            "expr": "100 * (pg_stat_statements_parallel_workers_launched / pg_stat_statements_parallel_workers_to_launch)",
            "legendFormat": "并行效率(%)"
          }
        ]
      },
      {
        "title": "连接数",
        "targets": [
          {
            "expr": "pg_stat_activity_count",
            "legendFormat": "活跃连接"
          }
        ]
      }
    ]
  }
}
```

---

## 7.2.4 PostgreSQL 18特定指标

### 7.2.4.1 I/O性能指标

```promql
# I/O读取吞吐量（PostgreSQL 18）
sum(pg_stat_io_read_bytes) / 1024 / 1024 / 1024

# I/O写入吞吐量（PostgreSQL 18）
sum(pg_stat_io_write_bytes) / 1024 / 1024 / 1024

# I/O总吞吐量（PostgreSQL 18）
sum(pg_stat_io_read_bytes + pg_stat_io_write_bytes) / 1024 / 1024 / 1024
```

### 7.2.4.2 并行查询指标（PostgreSQL 18）

```promql
# 并行查询效率（PostgreSQL 18）
100 * (pg_stat_statements_parallel_workers_launched / pg_stat_statements_parallel_workers_to_launch)

# 并行查询数量（PostgreSQL 18）
count(pg_stat_statements{parallel_workers_to_launch > "0"})
```

### 7.2.4.3 检查点指标（PostgreSQL 18）

```promql
# 完成的检查点数量（PostgreSQL 18新增）
pg_stat_checkpointer_num_done

# 检查点写入时间（PostgreSQL 18）
pg_stat_checkpointer_checkpoint_write_time
```

---

## 7.2.5 Grafana面板配置示例

### 7.2.5.1 缓存命中率面板

```json
{
  "title": "缓存命中率",
  "type": "graph",
  "targets": [
    {
      "expr": "100 * (pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read))",
      "legendFormat": "{{datname}}"
    }
  ],
  "yaxes": [
    {
      "format": "percent",
      "min": 0,
      "max": 100
    }
  ],
  "thresholds": [
    {"value": 0, "color": "red"},
    {"value": 90, "color": "yellow"},
    {"value": 95, "color": "green"}
  ]
}
```

### 7.2.5.2 I/O吞吐量面板（PostgreSQL 18）

```json
{
  "title": "I/O吞吐量 (PostgreSQL 18)",
  "type": "graph",
  "targets": [
    {
      "expr": "sum(pg_stat_io_read_bytes) / 1024 / 1024 / 1024",
      "legendFormat": "读取(GB)"
    },
    {
      "expr": "sum(pg_stat_io_write_bytes) / 1024 / 1024 / 1024",
      "legendFormat": "写入(GB)"
    }
  ],
  "yaxes": [
    {
      "format": "GB"
    }
  ]
}
```

### 7.2.5.3 并行查询效率面板（PostgreSQL 18）

```json
{
  "title": "并行查询效率 (PostgreSQL 18)",
  "type": "graph",
  "targets": [
    {
      "expr": "100 * (pg_stat_statements_parallel_workers_launched / pg_stat_statements_parallel_workers_to_launch)",
      "legendFormat": "并行效率(%)"
    }
  ],
  "yaxes": [
    {
      "format": "percent",
      "min": 0,
      "max": 100
    }
  ],
  "thresholds": [
    {"value": 0, "color": "red"},
    {"value": 70, "color": "yellow"},
    {"value": 90, "color": "green"}
  ]
}
```

---

## 7.2.6 告警规则配置

### 7.2.6.1 Prometheus告警规则

```yaml
# postgresql18_alerts.yml
groups:
  - name: postgresql18
    interval: 30s
    rules:
      - alert: PostgreSQLHighConnectionUsage
        expr: pg_stat_activity_count / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL连接数使用率过高"
          description: "连接数使用率: {{ $value | humanizePercentage }}"

      - alert: PostgreSQLLowCacheHitRatio
        expr: 100 * (pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)) < 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL缓存命中率过低"
          description: "缓存命中率: {{ $value }}%"

      - alert: PostgreSQLHighIOThroughput
        expr: sum(pg_stat_io_read_bytes + pg_stat_io_write_bytes) / 1024 / 1024 / 1024 > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL I/O吞吐量过高 (PostgreSQL 18)"
          description: "I/O吞吐量: {{ $value }} GB"
```

---

## 7.2.7 部署步骤

### 7.2.7.1 安装Prometheus

```bash
# 下载Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz

# 解压
tar -xzf prometheus-2.45.0.linux-amd64.tar.gz

# 配置prometheus.yml（如上所示）

# 启动Prometheus
./prometheus --config.file=prometheus.yml
```

### 7.2.7.2 安装Grafana

```bash
# 安装Grafana
wget https://dl.grafana.com/oss/release/grafana-10.0.0.linux-amd64.tar.gz

# 解压
tar -xzf grafana-10.0.0.linux-amd64.tar.gz

# 启动Grafana
./grafana-server
```

### 7.2.7.3 配置数据源

1. 登录Grafana（默认<http://localhost:3000）>
2. 添加Prometheus数据源
3. 配置Prometheus URL（<http://localhost:9090）>
4. 保存并测试连接

### 7.2.7.4 导入仪表板

1. 创建新的仪表板
2. 导入JSON配置（如上所示）
3. 配置数据源
4. 保存仪表板

---

---

## 7.2.8 注意事项与最佳实践

### 7.2.8.1 PostgreSQL 18增强特性

1. **I/O统计增强**：支持read_bytes/write_bytes指标
2. **并行查询追踪**：支持parallel_workers_to_launch/parallel_workers_launched指标
3. **检查点统计**：支持num_done指标

### 7.2.8.2 注意事项

⚠️ **重要提醒**：

1. **Exporter版本**：确保使用支持PostgreSQL 18的Exporter版本
2. **指标名称**：PostgreSQL 18新增指标的PromQL查询语法可能不同
3. **性能影响**：监控本身会有性能开销，合理设置采集间隔（建议15-30秒）

### 7.2.8.3 最佳实践

✅ **推荐做法**：

1. **版本兼容**：确保Prometheus Exporter支持PostgreSQL 18新特性
2. **指标优化**：只采集必要的指标，减少性能开销
3. **仪表板设计**：设计清晰的仪表板，便于快速发现问题
4. **告警配置**：配置关键指标的告警规则

---

## 7.2.9 导航

### 7.2.9.1 章节导航

- **上一节**：[7.1 监控仪表板设计](./01-监控仪表板设计.md)
- **下一节**：无（本章为07-监控仪表板的最后一节）
- **返回主题目录**：[07-监控仪表板](./README.md)
- **返回主文档**：[PostgreSQL-18-自动化运维与自我监测](../README.md)

### 7.2.9.2 相关章节

- [7.1 监控仪表板设计](./01-监控仪表板设计.md) - 内置视图监控
- [5.2 自动化性能报告](../05-自动化运维脚本/02-自动化性能报告.md) - 性能报告
- [5.3 自动化告警系统](../05-自动化运维脚本/03-自动化告警系统.md) - 告警系统

---

## 📚 相关资源

- [Prometheus文档](https://prometheus.io/docs/)
- [Grafana文档](https://grafana.com/docs/)
- [PostgreSQL Exporter](https://github.com/prometheus-community/postgres_exporter)
- [PostgreSQL监控最佳实践](../10-最佳实践/01-推荐做法与注意事项.md)

---

**最后更新**: 2025年1月
**文档版本**: v2.0（已添加完整目录、章节编号、详细内容）
