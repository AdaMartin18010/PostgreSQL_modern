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

## 📚 相关文档

- [灾难恢复完整指南.md](./灾难恢复完整指南.md) - 灾难恢复完整指南
- [灾难恢复计划.md](./灾难恢复计划.md) - 灾难恢复计划
- [灾难恢复演练.md](./灾难恢复演练.md) - 灾难恢复演练
- [13-高可用架构/README.md](../README.md) - 高可用架构主题

---

**最后更新**: 2025年1月
