# PostgreSQL SLA管理完整指南

> **PostgreSQL版本**: 17+/18+
> **适用场景**: 企业级数据库服务、云数据库服务
> **难度等级**: ⭐⭐⭐⭐ 高级

---

## 📋 目录

- [PostgreSQL SLA管理完整指南](#postgresql-sla管理完整指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 什么是SLA？](#11-什么是sla)
    - [1.2 SLA的重要性](#12-sla的重要性)
  - [2. SLA定义与指标](#2-sla定义与指标)
    - [2.1 可用性指标](#21-可用性指标)
      - [2.1.1 可用性计算](#211-可用性计算)
      - [2.1.2 可用性监控](#212-可用性监控)
    - [2.2 性能指标](#22-性能指标)
      - [2.2.1 响应时间](#221-响应时间)
      - [2.2.2 吞吐量](#222-吞吐量)
    - [2.3 可靠性指标](#23-可靠性指标)
      - [2.3.1 数据一致性](#231-数据一致性)
      - [2.3.2 备份恢复](#232-备份恢复)
  - [3. SLA监控方法](#3-sla监控方法)
    - [3.1 实时监控](#31-实时监控)
      - [3.1.1 连接监控](#311-连接监控)
      - [3.1.2 性能监控](#312-性能监控)
    - [3.2 历史监控](#32-历史监控)
      - [3.2.1 创建监控表](#321-创建监控表)
      - [3.2.2 定期监控脚本](#322-定期监控脚本)
  - [4. SLA报告生成](#4-sla报告生成)
    - [4.1 日报生成](#41-日报生成)
    - [4.2 月报生成](#42-月报生成)
  - [5. SLA优化策略](#5-sla优化策略)
    - [5.1 可用性优化](#51-可用性优化)
    - [5.2 性能优化](#52-性能优化)
    - [5.3 容量规划](#53-容量规划)
  - [6. 最佳实践](#6-最佳实践)
    - [6.1 SLA定义](#61-sla定义)
    - [6.2 SLA监控](#62-sla监控)
    - [6.3 SLA优化](#63-sla优化)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

### 1.1 什么是SLA？

服务等级协议（Service Level Agreement, SLA）是服务提供商与客户之间关于服务质量和性能的正式协议。

**SLA核心要素**:

- ✅ **可用性**: 服务可用时间百分比
- ✅ **性能**: 响应时间、吞吐量
- ✅ **可靠性**: 数据一致性、故障恢复
- ✅ **支持**: 响应时间、解决时间

### 1.2 SLA的重要性

- **客户满意度**: 明确的性能承诺
- **服务质量**: 量化服务标准
- **风险管理**: 明确责任和补偿
- **持续改进**: 基于SLA优化服务

---

## 2. SLA定义与指标

### 2.1 可用性指标

#### 2.1.1 可用性计算

```text
可用性 = (总时间 - 停机时间) / 总时间 × 100%

示例：
- 99.9%可用性 = 每月最多43.2分钟停机
- 99.99%可用性 = 每月最多4.32分钟停机
- 99.999%可用性 = 每月最多26秒停机
```

#### 2.1.2 可用性监控

```sql
-- 创建可用性监控表
CREATE TABLE sla_availability (
    id SERIAL PRIMARY KEY,
    check_time TIMESTAMPTZ DEFAULT NOW(),
    is_available BOOLEAN,
    response_time_ms NUMERIC,
    error_message TEXT
);

-- 插入监控数据
INSERT INTO sla_availability (is_available, response_time_ms)
VALUES (true, 10.5);

-- 计算可用性
SELECT
    DATE_TRUNC('day', check_time) as date,
    COUNT(*) as total_checks,
    SUM(CASE WHEN is_available THEN 1 ELSE 0 END) as available_checks,
    (SUM(CASE WHEN is_available THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC * 100) as availability_percent
FROM sla_availability
WHERE check_time >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', check_time)
ORDER BY date DESC;
```

### 2.2 性能指标

#### 2.2.1 响应时间

```sql
-- 使用pg_stat_statements监控查询响应时间
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查看平均响应时间
SELECT
    userid::regrole,
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- 超过100ms的查询
ORDER BY mean_exec_time DESC
LIMIT 10;
```

#### 2.2.2 吞吐量

```sql
-- 监控事务吞吐量
SELECT
    datname,
    xact_commit as committed_transactions,
    xact_rollback as rolled_back_transactions,
    xact_commit + xact_rollback as total_transactions
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1', 'postgres')
ORDER BY xact_commit DESC;
```

### 2.3 可靠性指标

#### 2.3.1 数据一致性

```sql
-- 检查数据完整性
SELECT
    schemaname,
    tablename,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > n_live_tup * 0.1;  -- 死元组超过10%
```

#### 2.3.2 备份恢复

```sql
-- 检查备份状态
SELECT
    backup_start,
    backup_end,
    backup_size,
    CASE
        WHEN backup_end IS NULL THEN 'In Progress'
        ELSE 'Completed'
    END as status
FROM pg_backup_history
ORDER BY backup_start DESC
LIMIT 10;
```

---

## 3. SLA监控方法

### 3.1 实时监控

#### 3.1.1 连接监控

```sql
-- 监控连接状态
SELECT
    datname,
    count(*) as current_connections,
    (SELECT setting::INT FROM pg_settings WHERE name = 'max_connections') as max_connections,
    (count(*)::NUMERIC / (SELECT setting::INT FROM pg_settings WHERE name = 'max_connections')::NUMERIC * 100) as connection_usage_percent
FROM pg_stat_activity
WHERE datname IS NOT NULL
GROUP BY datname;
```

#### 3.1.2 性能监控

```sql
-- 监控慢查询
SELECT
    pid,
    usename,
    datname,
    state,
    query_start,
    NOW() - query_start as query_duration,
    query
FROM pg_stat_activity
WHERE state = 'active'
AND NOW() - query_start > INTERVAL '5 seconds'
ORDER BY query_start;
```

### 3.2 历史监控

#### 3.2.1 创建监控表

```sql
-- 创建SLA监控历史表
CREATE TABLE sla_monitoring_history (
    id SERIAL PRIMARY KEY,
    check_time TIMESTAMPTZ DEFAULT NOW(),
    metric_name TEXT,
    metric_value NUMERIC,
    metric_unit TEXT,
    threshold_value NUMERIC,
    is_violated BOOLEAN
);

-- 创建索引
CREATE INDEX idx_sla_monitoring_time ON sla_monitoring_history(check_time);
CREATE INDEX idx_sla_monitoring_metric ON sla_monitoring_history(metric_name);
```

#### 3.2.2 定期监控脚本

```sql
-- 监控函数
CREATE OR REPLACE FUNCTION monitor_sla_metrics()
RETURNS void AS $$
DECLARE
    v_availability NUMERIC;
    v_avg_response_time NUMERIC;
    v_connection_usage NUMERIC;
BEGIN
    -- 计算可用性
    SELECT
        (SUM(CASE WHEN is_available THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC * 100)
    INTO v_availability
    FROM sla_availability
    WHERE check_time >= NOW() - INTERVAL '1 hour';

    -- 计算平均响应时间
    SELECT AVG(mean_exec_time)
    INTO v_avg_response_time
    FROM pg_stat_statements
    WHERE calls > 100;

    -- 计算连接使用率
    SELECT
        (COUNT(*)::NUMERIC / (SELECT setting::INT FROM pg_settings WHERE name = 'max_connections')::NUMERIC * 100)
    INTO v_connection_usage
    FROM pg_stat_activity
    WHERE datname IS NOT NULL;

    -- 插入监控数据
    INSERT INTO sla_monitoring_history (metric_name, metric_value, metric_unit, threshold_value, is_violated)
    VALUES
        ('availability', v_availability, 'percent', 99.9, v_availability < 99.9),
        ('avg_response_time', v_avg_response_time, 'ms', 100, v_avg_response_time > 100),
        ('connection_usage', v_connection_usage, 'percent', 80, v_connection_usage > 80);
END;
$$ LANGUAGE plpgsql;

-- 使用pg_cron定期执行（如果可用）
-- SELECT cron.schedule('monitor-sla', '*/5 * * * *', 'SELECT monitor_sla_metrics();');
```

---

## 4. SLA报告生成

### 4.1 日报生成

```sql
-- 生成SLA日报
CREATE OR REPLACE FUNCTION generate_sla_daily_report(report_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    metric_name TEXT,
    metric_value NUMERIC,
    threshold_value NUMERIC,
    is_violated BOOLEAN,
    violation_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.metric_name,
        AVG(m.metric_value) as metric_value,
        MAX(m.threshold_value) as threshold_value,
        BOOL_OR(m.is_violated) as is_violated,
        SUM(CASE WHEN m.is_violated THEN 1 ELSE 0 END)::BIGINT as violation_count
    FROM sla_monitoring_history m
    WHERE DATE(m.check_time) = report_date
    GROUP BY m.metric_name
    ORDER BY m.metric_name;
END;
$$ LANGUAGE plpgsql;

-- 执行报告
SELECT * FROM generate_sla_daily_report();
```

### 4.2 月报生成

```sql
-- 生成SLA月报
CREATE OR REPLACE FUNCTION generate_sla_monthly_report(report_month DATE DEFAULT DATE_TRUNC('month', CURRENT_DATE))
RETURNS TABLE (
    metric_name TEXT,
    avg_value NUMERIC,
    min_value NUMERIC,
    max_value NUMERIC,
    threshold_value NUMERIC,
    violation_count BIGINT,
    violation_percent NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.metric_name,
        AVG(m.metric_value) as avg_value,
        MIN(m.metric_value) as min_value,
        MAX(m.metric_value) as max_value,
        MAX(m.threshold_value) as threshold_value,
        SUM(CASE WHEN m.is_violated THEN 1 ELSE 0 END)::BIGINT as violation_count,
        (SUM(CASE WHEN m.is_violated THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC * 100) as violation_percent
    FROM sla_monitoring_history m
    WHERE DATE_TRUNC('month', m.check_time) = report_month
    GROUP BY m.metric_name
    ORDER BY m.metric_name;
END;
$$ LANGUAGE plpgsql;

-- 执行月报
SELECT * FROM generate_sla_monthly_report();
```

---

## 5. SLA优化策略

### 5.1 可用性优化

```sql
-- 高可用配置
-- 1. 主从复制
-- 2. 自动故障转移
-- 3. 负载均衡

-- 监控主从延迟
SELECT
    client_addr,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) as replication_lag_bytes
FROM pg_stat_replication;
```

### 5.2 性能优化

```sql
-- 查询优化
-- 1. 索引优化
-- 2. 查询重写
-- 3. 统计信息更新

-- 更新统计信息
ANALYZE;

-- 查看索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0  -- 未使用的索引
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 5.3 容量规划

```sql
-- 容量监控
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) as size,
    numbackends as connections,
    xact_commit + xact_rollback as transactions
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1', 'postgres')
ORDER BY pg_database_size(datname) DESC;
```

---

## 6. 最佳实践

### 6.1 SLA定义

- ✅ **明确指标**: 定义清晰的性能指标
- ✅ **合理阈值**: 设置可实现的阈值
- ✅ **测量方法**: 定义准确的测量方法
- ✅ **补偿机制**: 明确违反SLA的补偿

### 6.2 SLA监控

- ✅ **实时监控**: 24/7实时监控
- ✅ **自动告警**: 自动检测SLA违反
- ✅ **历史记录**: 保存历史监控数据
- ✅ **定期报告**: 生成定期SLA报告

### 6.3 SLA优化

- ✅ **持续改进**: 基于SLA数据持续优化
- ✅ **容量规划**: 提前规划容量需求
- ✅ **故障预防**: 预防性维护
- ✅ **性能调优**: 定期性能调优

---

## 📚 相关文档

- [资源隔离与配额管理](./资源隔离与配额管理.md) - 资源管理
- [12-监控与诊断](../12-监控与诊断/README.md) - 监控和诊断
- [13-高可用架构](../13-高可用架构/README.md) - 高可用架构
- [31-容量规划](../31-容量规划/README.md) - 容量规划

---

**最后更新**: 2025年1月
**状态**: ✅ 完成
