# PostgreSQL CAP监控与诊断

> **文档编号**: CAP-PRACTICE-009
> **主题**: PostgreSQL CAP监控与诊断
> **版本**: PostgreSQL 17 & 18
> **状态**: ✅ 已完成

---

## 📑 目录

- [PostgreSQL CAP监控与诊断](#postgresql-cap监控与诊断)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📊 第一部分：CAP指标监控](#-第一部分cap指标监控)
    - [1.1 一致性指标](#11-一致性指标)
    - [1.2 可用性指标](#12-可用性指标)
    - [1.3 分区容错指标](#13-分区容错指标)
  - [📊 第二部分：分区检测与告警](#-第二部分分区检测与告警)
    - [2.1 分区检测机制](#21-分区检测机制)
    - [2.2 分区告警规则](#22-分区告警规则)
    - [2.3 分区故障处理](#23-分区故障处理)
  - [📊 第三部分：一致性验证工具](#-第三部分一致性验证工具)
    - [3.1 一致性检查脚本](#31-一致性检查脚本)
    - [3.2 一致性验证工具](#32-一致性验证工具)
    - [3.3 一致性报告](#33-一致性报告)
  - [📊 第四部分：可用性测量工具](#-第四部分可用性测量工具)
    - [4.1 可用性监控](#41-可用性监控)
    - [4.2 可用性测量](#42-可用性测量)
    - [4.3 可用性报告](#43-可用性报告)
  - [📝 总结](#-总结)
    - [核心结论](#核心结论)
    - [实践建议](#实践建议)

---

## 📋 概述

CAP监控与诊断是保证PostgreSQL高可用的关键，理解CAP指标的监控方法和诊断工具，有助于及时发现和处理CAP相关问题。

本文档从CAP指标监控、分区检测告警、一致性验证和可用性测量四个维度，全面阐述PostgreSQL CAP监控与诊断的完整体系。

**核心观点**：

- **CAP指标监控**：实时监控一致性、可用性和分区容错指标
- **分区检测告警**：及时发现网络分区问题
- **一致性验证**：验证数据一致性
- **可用性测量**：测量系统可用性

---

## 📊 第一部分：CAP指标监控

### 1.1 一致性指标

**一致性监控指标**：

```sql
-- 监控复制延迟（一致性指标）
SELECT
    application_name,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn) AS lag_bytes,
    EXTRACT(EPOCH FROM (now() - pg_stat_file('pg_wal/' || pg_walfile_name(flush_lsn))::timestamp)) AS lag_seconds
FROM pg_stat_replication
WHERE sync_state = 'sync';

-- 监控串行化冲突（一致性指标）
SELECT
    datname,
    xact_commit,
    xact_rollback,
    conflicts
FROM pg_stat_database
WHERE datname = current_database();
```

### 1.2 可用性指标

**可用性监控指标**：

```sql
-- 监控数据库连接（可用性指标）
SELECT
    COUNT(*) FILTER (WHERE state = 'active') AS active_connections,
    COUNT(*) AS total_connections,
    COUNT(*) FILTER (WHERE state = 'active')::float / COUNT(*)::float * 100 AS availability_percent
FROM pg_stat_activity;

-- 监控查询响应时间（可用性指标）
SELECT
    percentile_cont(0.95) WITHIN GROUP (ORDER BY mean_exec_time) AS p95_latency,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY mean_exec_time) AS p99_latency
FROM pg_stat_statements;
```

### 1.3 分区容错指标

**分区容错监控指标**：

```sql
-- 监控复制连接状态（分区容错指标）
SELECT
    application_name,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn) AS lag_bytes
FROM pg_stat_replication;

-- 监控网络分区（分区容错指标）
SELECT
    application_name,
    CASE
        WHEN pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn) > 104857600 THEN 'Partitioned'
        ELSE 'Connected'
    END AS partition_status
FROM pg_stat_replication;
```

---

## 📊 第二部分：分区检测与告警

### 2.1 分区检测机制

**分区检测方法**：

1. **心跳检测**
   - 定期发送心跳
   - 检测节点存活
   - 超时判定分区

2. **复制延迟检测**
   - 监控复制延迟
   - 延迟过大判定分区
   - 设置告警阈值

**PostgreSQL分区检测**：

```sql
-- 分区检测函数
CREATE OR REPLACE FUNCTION detect_partition()
RETURNS TABLE (
    application_name TEXT,
    partition_status TEXT,
    lag_bytes BIGINT,
    lag_seconds NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.application_name,
        CASE
            WHEN r.state = 'streaming' AND pg_wal_lsn_diff(pg_current_wal_lsn(), r.flush_lsn) < 104857600 THEN 'Connected'
            WHEN r.state = 'streaming' AND pg_wal_lsn_diff(pg_current_wal_lsn(), r.flush_lsn) >= 104857600 THEN 'Partitioned'
            ELSE 'Disconnected'
        END AS partition_status,
        pg_wal_lsn_diff(pg_current_wal_lsn(), r.flush_lsn) AS lag_bytes,
        EXTRACT(EPOCH FROM (now() - pg_stat_file('pg_wal/' || pg_walfile_name(r.flush_lsn))::timestamp)) AS lag_seconds
    FROM pg_stat_replication r;
END;
$$ LANGUAGE plpgsql;
```

### 2.2 分区告警规则

**Prometheus告警规则**：

```yaml
groups:
  - name: postgresql_cap
    rules:
      - alert: HighReplicationLag
        expr: pg_replication_lag_bytes > 104857600  # 100MB
        for: 5m
        annotations:
          summary: "复制延迟过高，可能存在网络分区"

      - alert: ReplicationDisconnected
        expr: pg_replication_state != 'streaming'
        for: 1m
        annotations:
          summary: "复制连接断开，可能存在网络分区"
```

### 2.3 分区故障处理

**分区故障处理流程**：

```text
1. 检测分区
   │
2. 评估影响
   │
3. 选择处理策略
   │
   ├─ CP模式：阻塞写入，等待恢复
   │
   └─ AP模式：继续服务，异步同步
```

---

## 📊 第三部分：一致性验证工具

### 3.1 一致性检查脚本

**一致性检查脚本**：

```sql
-- 一致性检查函数
CREATE OR REPLACE FUNCTION verify_consistency()
RETURNS TABLE (
    check_name TEXT,
    result BOOLEAN,
    details TEXT
) AS $$
BEGIN
    -- 检查1：复制延迟
    RETURN QUERY
    SELECT
        'Replication Lag'::TEXT,
        pg_wal_lsn_diff(pg_current_wal_lsn(), (SELECT flush_lsn FROM pg_stat_replication WHERE sync_state = 'sync' LIMIT 1)) < 10485760 AS result,
        pg_wal_lsn_diff(pg_current_wal_lsn(), (SELECT flush_lsn FROM pg_stat_replication WHERE sync_state = 'sync' LIMIT 1))::TEXT AS details;

    -- 检查2：串行化冲突
    RETURN QUERY
    SELECT
        'Serialization Conflicts'::TEXT,
        (SELECT conflicts FROM pg_stat_database WHERE datname = current_database()) = 0 AS result,
        (SELECT conflicts FROM pg_stat_database WHERE datname = current_database())::TEXT AS details;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 一致性验证工具

**一致性验证工具**：

```bash
#!/bin/bash
# 一致性验证脚本

# 检查复制延迟
psql -c "SELECT application_name, pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn) AS lag_bytes FROM pg_stat_replication WHERE sync_state = 'sync';"

# 检查串行化冲突
psql -c "SELECT conflicts FROM pg_stat_database WHERE datname = current_database();"

# 检查数据一致性
psql -c "SELECT verify_consistency();"
```

### 3.3 一致性报告

**一致性报告生成**：

```sql
-- 生成一致性报告
SELECT
    'Consistency Report' AS report_type,
    now() AS report_time,
    (SELECT COUNT(*) FROM pg_stat_replication WHERE sync_state = 'sync') AS sync_replicas,
    (SELECT MAX(pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn)) FROM pg_stat_replication WHERE sync_state = 'sync') AS max_lag_bytes,
    (SELECT conflicts FROM pg_stat_database WHERE datname = current_database()) AS serialization_conflicts;
```

---

## 📊 第四部分：可用性测量工具

### 4.1 可用性监控

**可用性监控指标**：

```sql
-- 监控数据库可用性
SELECT
    'Database Availability' AS metric,
    COUNT(*) FILTER (WHERE state = 'active')::float / COUNT(*)::float * 100 AS availability_percent,
    COUNT(*) FILTER (WHERE state = 'idle') AS idle_connections,
    COUNT(*) FILTER (WHERE state = 'active') AS active_connections
FROM pg_stat_activity;

-- 监控查询可用性
SELECT
    'Query Availability' AS metric,
    COUNT(*) FILTER (WHERE state = 'active' AND query_start < now() - interval '1 minute') AS long_running_queries,
    COUNT(*) FILTER (WHERE wait_event_type IS NOT NULL) AS waiting_queries
FROM pg_stat_activity;
```

### 4.2 可用性测量

**可用性测量函数**：

```sql
-- 可用性测量函数
CREATE OR REPLACE FUNCTION measure_availability()
RETURNS TABLE (
    metric_name TEXT,
    availability_percent NUMERIC,
    details TEXT
) AS $$
BEGIN
    -- 测量数据库连接可用性
    RETURN QUERY
    SELECT
        'Connection Availability'::TEXT,
        COUNT(*) FILTER (WHERE state = 'active')::float / NULLIF(COUNT(*), 0) * 100 AS availability_percent,
        COUNT(*) FILTER (WHERE state = 'active')::TEXT || ' active / ' || COUNT(*)::TEXT || ' total' AS details
    FROM pg_stat_activity;

    -- 测量查询可用性
    RETURN QUERY
    SELECT
        'Query Availability'::TEXT,
        COUNT(*) FILTER (WHERE state = 'active' AND wait_event_type IS NULL)::float / NULLIF(COUNT(*) FILTER (WHERE state = 'active'), 0) * 100 AS availability_percent,
        COUNT(*) FILTER (WHERE state = 'active' AND wait_event_type IS NULL)::TEXT || ' non-waiting / ' || COUNT(*) FILTER (WHERE state = 'active')::TEXT || ' active' AS details
    FROM pg_stat_activity;
END;
$$ LANGUAGE plpgsql;
```

### 4.3 可用性报告

**可用性报告生成**：

```sql
-- 生成可用性报告
SELECT
    'Availability Report' AS report_type,
    now() AS report_time,
    (SELECT availability_percent FROM measure_availability() WHERE metric_name = 'Connection Availability') AS connection_availability,
    (SELECT availability_percent FROM measure_availability() WHERE metric_name = 'Query Availability') AS query_availability;
```

---

## 📝 总结

### 核心结论

1. **CAP指标监控**：实时监控一致性、可用性和分区容错指标
2. **分区检测告警**：及时发现网络分区问题
3. **一致性验证**：验证数据一致性
4. **可用性测量**：测量系统可用性

### 实践建议

1. **设置监控指标**：设置CAP相关监控指标
2. **配置告警规则**：配置分区和一致性告警规则
3. **定期验证一致性**：定期运行一致性验证工具
4. **测量可用性**：定期测量系统可用性

---

**最后更新**: 2024年
**维护状态**: ✅ 已完成
