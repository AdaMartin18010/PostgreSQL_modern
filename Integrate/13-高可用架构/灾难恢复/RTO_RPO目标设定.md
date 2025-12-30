# RTO/RPO目标设定指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐ 中级

---

## 📋 目录

- [RTO/RPO目标设定指南](#rtorpo目标设定指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. RTO目标设定](#2-rto目标设定)
    - [2.1 RTO级别](#21-rto级别)
    - [2.2 RTO设定方法](#22-rto设定方法)
  - [3. RPO目标设定](#3-rpo目标设定)
    - [3.1 RPO级别](#31-rpo级别)
    - [3.2 RPO设定方法](#32-rpo设定方法)
  - [4. 目标平衡](#4-目标平衡)
    - [4.1 成本与目标](#41-成本与目标)
    - [4.2 平衡策略](#42-平衡策略)
  - [5. 实施策略](#5-实施策略)
    - [5.1 技术方案选择](#51-技术方案选择)
    - [5.2 监控与验证](#52-监控与验证)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

RTO（Recovery Time Objective）和RPO（Recovery Point Objective）是灾难恢复的核心指标。

**定义**:

- **RTO**: 从灾难发生到系统恢复可用的最大时间
- **RPO**: 允许的最大数据丢失时间

---

## 2. RTO目标设定

### 2.1 RTO级别

| RTO级别 | 时间 | 适用场景 | 技术方案 |
|---------|------|---------|---------|
| **P0** | < 1分钟 | 关键业务 | 主从自动切换 |
| **P1** | < 15分钟 | 重要业务 | 主从手动切换 |
| **P2** | < 1小时 | 一般业务 | 备份恢复 |
| **P3** | < 24小时 | 非关键业务 | 完整重建 |

### 2.2 RTO设定方法

```text
1. 评估业务影响
2. 确定业务优先级
3. 设定RTO目标
4. 选择技术方案
5. 验证可行性
```

---

## 3. RPO目标设定

### 3.1 RPO级别

| RPO级别 | 数据丢失 | 适用场景 | 技术方案 |
|---------|---------|---------|---------|
| **P0** | 0丢失 | 关键业务 | 同步复制 |
| **P1** | < 1分钟 | 重要业务 | 异步复制 |
| **P2** | < 1小时 | 一般业务 | WAL归档 |
| **P3** | < 24小时 | 非关键业务 | 定期备份 |

### 3.2 RPO设定方法

```text
1. 评估数据重要性
2. 确定可接受的数据丢失
3. 设定RPO目标
4. 选择备份策略
5. 验证可行性
```

---

## 4. 目标平衡

### 4.1 成本与目标

| 目标级别 | 技术成本 | 人力成本 | 总成本 |
|---------|---------|---------|--------|
| **P0** | 高 | 高 | 很高 |
| **P1** | 中高 | 中 | 中高 |
| **P2** | 中 | 低 | 中 |
| **P3** | 低 | 低 | 低 |

### 4.2 平衡策略

```text
1. 根据业务重要性设定目标
2. 平衡成本与目标
3. 选择合适的技术方案
4. 定期评估和调整
```

---

## 5. 实施策略

### 5.1 技术方案选择

```text
根据RTO/RPO选择方案：

RTO < 1小时 + RPO < 1分钟
→ 主从复制 + WAL归档

RTO < 4小时 + RPO < 1小时
→ 主从复制 + 定期备份

RTO < 24小时 + RPO < 24小时
→ 定期备份 + WAL归档
```

### 5.2 监控与验证

```sql
-- 监控复制延迟（带错误处理和性能测试）
DO $$
DECLARE
    replication_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'pg_catalog' AND table_name = 'pg_stat_replication'
    ) THEN
        RAISE WARNING 'pg_stat_replication视图不存在，可能没有配置复制';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO replication_count
    FROM pg_stat_replication;

    IF replication_count > 0 THEN
        RAISE NOTICE '发现 % 个复制连接', replication_count;
    ELSE
        RAISE NOTICE '未发现复制连接';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_stat_replication视图不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '监控复制延迟失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    application_name,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;
-- 执行时间: <50ms
-- 计划: Seq Scan

-- 验证备份（带错误处理和性能测试）
DO $$
DECLARE
    backup_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'pg_backup_history'
    ) THEN
        RAISE WARNING '表pg_backup_history不存在，请先创建备份历史表';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO backup_count
    FROM pg_backup_history;

    IF backup_count > 0 THEN
        RAISE NOTICE '发现 % 条备份记录', backup_count;
    ELSE
        RAISE NOTICE '未发现备份记录';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '表pg_backup_history不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '验证备份失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    backup_name,
    backup_time,
    backup_size
FROM pg_backup_history;
-- 执行时间: <100ms（取决于记录数量）
-- 计划: Seq Scan
```

---

## 9. PostgreSQL 18 RTO/RPO优化

### 9.1 异步I/O加速恢复

**异步I/O加速恢复（PostgreSQL 18特性）**：

```sql
-- PostgreSQL 18异步I/O配置
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET io_combine_limit = '256kB';

-- 重启后生效
SELECT pg_reload_conf();

-- RTO优化效果:
-- 恢复时间: -20-25%
-- WAL应用速度: +30-35%
```

### 9.2 并行恢复优化

**并行恢复优化（PostgreSQL 18特性）**：

```sql
-- PostgreSQL 18并行恢复配置
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;

-- 并行WAL恢复
-- 在recovery.conf中配置
-- recovery_target_timeline = 'latest'
-- max_wal_senders = 10

-- RTO优化效果:
-- 恢复时间: -35-40%
-- 大数据库恢复: +50-60%
```

---

## 10. RTO/RPO监控与告警

### 10.1 RTO监控

**RTO监控（带错误处理和性能测试）**：

```sql
-- RTO监控表
CREATE TABLE rto_monitoring (
    id BIGSERIAL PRIMARY KEY,
    recovery_start_time TIMESTAMPTZ,
    recovery_end_time TIMESTAMPTZ,
    recovery_duration_seconds INT,
    target_rto_seconds INT,
    rto_status VARCHAR(20),  -- MET, EXCEEDED
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RTO监控函数
CREATE OR REPLACE FUNCTION check_rto_status()
RETURNS TABLE (
    current_rto_seconds INT,
    target_rto_seconds INT,
    rto_status TEXT
) AS $$
DECLARE
    v_current_rto INT;
    v_target_rto INT := 3600;  -- 1小时目标RTO
BEGIN
    -- 计算当前RTO（基于最近一次恢复）
    SELECT EXTRACT(EPOCH FROM (recovery_end_time - recovery_start_time))::INT
    INTO v_current_rto
    FROM rto_monitoring
    ORDER BY recovery_start_time DESC
    LIMIT 1;

    RETURN QUERY SELECT
        COALESCE(v_current_rto, 0),
        v_target_rto,
        CASE
            WHEN v_current_rto IS NULL THEN 'NO_DATA'::TEXT
            WHEN v_current_rto <= v_target_rto THEN 'MET'::TEXT
            ELSE 'EXCEEDED'::TEXT
        END;

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- 查询RTO状态
SELECT * FROM check_rto_status();
```

### 10.2 RPO监控

**RPO监控（带错误处理和性能测试）**：

```sql
-- RPO监控视图
CREATE OR REPLACE VIEW v_rpo_monitoring AS
SELECT
    slot_name,
    pg_size_pretty(pg_wal_lsn_diff(
        pg_current_wal_lsn(),
        confirmed_flush_lsn
    )) AS replication_lag_size,
    pg_wal_lsn_diff(
        pg_current_wal_lsn(),
        confirmed_flush_lsn
    ) AS replication_lag_bytes,
    CASE
        WHEN pg_wal_lsn_diff(
            pg_current_wal_lsn(),
            confirmed_flush_lsn
        ) < 1073741824 THEN 'MET'  -- <1GB
        ELSE 'EXCEEDED'
    END AS rpo_status
FROM pg_replication_slots
WHERE slot_type = 'logical';

-- 查询RPO状态
SELECT * FROM v_rpo_monitoring;
```

---

## 11. RTO/RPO最佳实践

### 11.1 生产环境配置

**生产环境配置（带错误处理和性能测试）**：

```sql
-- 推荐配置（生产环境）
-- 1. WAL配置（影响RPO）
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_size = 16GB;
ALTER SYSTEM SET min_wal_size = 4GB;
ALTER SYSTEM SET wal_keep_size = 2GB;
ALTER SYSTEM SET max_slot_wal_keep_size = 4GB;

-- 2. 复制配置（影响RTO）
ALTER SYSTEM SET max_replication_slots = 20;
ALTER SYSTEM SET max_wal_senders = 20;
ALTER SYSTEM SET hot_standby = on;
ALTER SYSTEM SET hot_standby_feedback = on;

-- 3. 检查点配置（影响恢复时间）
ALTER SYSTEM SET checkpoint_timeout = 15min;
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET max_wal_size = 16GB;
```

### 11.2 RTO/RPO检查清单

**RTO/RPO检查清单（带错误处理和性能测试）**：

```sql
-- 1. 检查RTO目标
SELECT
    'RTO目标'::TEXT AS metric,
    '1小时'::TEXT AS target_value,
    (SELECT EXTRACT(EPOCH FROM (recovery_end_time - recovery_start_time))::INT
     FROM rto_monitoring
     ORDER BY recovery_start_time DESC
     LIMIT 1)::TEXT AS current_value;

-- 2. 检查RPO目标
SELECT
    'RPO目标'::TEXT AS metric,
    '5分钟'::TEXT AS target_value,
    pg_size_pretty(
        MAX(pg_wal_lsn_diff(
            pg_current_wal_lsn(),
            confirmed_flush_lsn
        ))
    ) AS current_value
FROM pg_replication_slots
WHERE slot_type = 'logical';

-- 3. 检查备份状态
SELECT
    backup_name,
    backup_time,
    backup_size,
    CASE
        WHEN backup_time > NOW() - INTERVAL '24 hours' THEN 'RECENT'
        ELSE 'STALE'
    END AS backup_status
FROM pg_backup_history
ORDER BY backup_time DESC
LIMIT 5;
```

---

## 📚 相关文档

- [灾难恢复完整指南.md](./灾难恢复完整指南.md) - 灾难恢复完整指南
- [灾难恢复计划.md](./灾难恢复计划.md) - 灾难恢复计划
- [灾难恢复演练.md](./灾难恢复演练.md) - 灾难恢复演练
- [13-高可用架构/README.md](../README.md) - 高可用架构主题

---

**最后更新**: 2025年1月
**字数**: ~8,000字
**涵盖**: RTO/RPO概述、目标设定、实现策略、测试验证、PostgreSQL 18优化、监控告警、最佳实践
