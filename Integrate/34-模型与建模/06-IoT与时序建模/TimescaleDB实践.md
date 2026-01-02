# TimescaleDB实践完整指南

> **创建日期**: 2025年1月
> **来源**: TimescaleDB官方文档 + 实践总结
> **状态**: 基于TimescaleDB 2.13+特性
> **文档编号**: 06-02

---

## 📑 目录

- [TimescaleDB实践完整指南](#timescaledb实践完整指南)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. Hypertable（超表）](#2-hypertable超表)
    - [2.1 创建Hypertable](#21-创建hypertable)
    - [2.2 Chunk管理](#22-chunk管理)
    - [2.3 分区策略](#23-分区策略)
  - [3. 连续聚合（Continuous Aggregates）](#3-连续聚合continuous-aggregates)
    - [3.1 创建连续聚合](#31-创建连续聚合)
    - [3.2 实时聚合](#32-实时聚合)
    - [3.3 聚合策略配置](#33-聚合策略配置)
  - [4. 数据保留策略（Retention Policies）](#4-数据保留策略retention-policies)
    - [4.1 创建保留策略](#41-创建保留策略)
    - [4.2 条件保留策略](#42-条件保留策略)
  - [5. 压缩策略](#5-压缩策略)
    - [5.1 启用压缩](#51-启用压缩)
    - [5.2 压缩效果](#52-压缩效果)
  - [6. 查询优化](#6-查询优化)
    - [6.1 时间范围查询](#61-时间范围查询)
    - [6.2 使用连续聚合](#62-使用连续聚合)
    - [6.3 使用Gap-filling](#63-使用gap-filling)
  - [7. 最佳实践](#7-最佳实践)
    - [7.1 设计原则](#71-设计原则)
    - [7.2 性能优化](#72-性能优化)
  - [8. 相关资源](#8-相关资源)

---

## 1. 概述

TimescaleDB是PostgreSQL的时序数据库扩展，专为时序数据优化。
它提供了Hypertable（超表）、连续聚合、数据保留策略等特性，大幅提升时序数据的存储和查询性能。

---

## 2. Hypertable（超表）

### 2.1 创建Hypertable

**定义**: Hypertable是TimescaleDB的核心概念，自动将表按时间分区。

**创建步骤**:

```sql
-- 1. 创建普通表
CREATE TABLE sensor_readings (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    quality INT DEFAULT 0
);

-- 2. 创建索引
CREATE INDEX idx_sensor_readings_device_time ON sensor_readings(device_id, time DESC);
CREATE INDEX idx_sensor_readings_time ON sensor_readings(time DESC);

-- 3. 转换为Hypertable
SELECT create_hypertable(
    'sensor_readings',
    'time',                    -- 分区键（时间列）
    chunk_time_interval => INTERVAL '1 day',  -- 每个chunk的时间间隔
    if_not_exists => TRUE
);
```

---

### 2.2 Chunk管理

**Chunk概念**: Hypertable自动将数据分割成多个chunk（块），每个chunk是一个独立的表。

**查看Chunk信息**:

```sql
-- 查看所有chunk
SELECT
    chunk_name,
    range_start,
    range_end,
    pg_size_pretty(total_bytes) AS size
FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_readings'
ORDER BY range_start DESC;

-- 查看chunk统计信息
SELECT
    chunk_name,
    num_rows,
    pg_size_pretty(total_bytes) AS size
FROM timescaledb_information.chunk_stats
WHERE hypertable_name = 'sensor_readings';
```

---

### 2.3 分区策略

**时间分区**:

```sql
-- 按天分区（推荐用于高频数据）
SELECT create_hypertable(
    'sensor_readings',
    'time',
    chunk_time_interval => INTERVAL '1 day'
);

-- 按周分区（推荐用于中频数据）
SELECT create_hypertable(
    'sensor_readings',
    'time',
    chunk_time_interval => INTERVAL '1 week'
);

-- 按月分区（推荐用于低频数据）
SELECT create_hypertable(
    'sensor_readings',
    'time',
    chunk_time_interval => INTERVAL '1 month'
);
```

**空间分区**（PostgreSQL 13+）:

```sql
-- 按时间和设备ID分区
SELECT create_hypertable(
    'sensor_readings',
    'time',
    partitioning_column => 'device_id',
    number_partitions => 4,  -- 4个设备分区
    chunk_time_interval => INTERVAL '1 day'
);
```

---

## 3. 连续聚合（Continuous Aggregates）

### 3.1 创建连续聚合

**定义**: 自动维护的物化视图，定期刷新聚合数据。

**创建连续聚合**:

```sql
-- 创建每小时聚合
CREATE MATERIALIZED VIEW sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    sensor_type,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS reading_count
FROM sensor_readings
GROUP BY bucket, device_id, sensor_type;

-- 添加刷新策略（每小时刷新）
SELECT add_continuous_aggregate_policy(
    'sensor_readings_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);
```

---

### 3.2 实时聚合

**实时聚合视图**:

```sql
-- 创建实时聚合（结合物化数据和实时数据）
CREATE MATERIALIZED VIEW sensor_readings_hourly_realtime
WITH (timescaledb.continuous, timescaledb.materialized_only = false) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    AVG(value) AS avg_value
FROM sensor_readings
GROUP BY bucket, device_id;

-- 查询实时聚合（自动合并物化数据和实时数据）
SELECT * FROM sensor_readings_hourly_realtime
WHERE bucket >= NOW() - INTERVAL '24 hours';
```

---

### 3.3 聚合策略配置

**刷新策略**:

```sql
-- 添加刷新策略
SELECT add_continuous_aggregate_policy(
    'sensor_readings_hourly',
    start_offset => INTERVAL '3 hours',  -- 从3小时前开始刷新
    end_offset => INTERVAL '1 hour',      -- 刷新到1小时前
    schedule_interval => INTERVAL '1 hour' -- 每小时执行一次
);

-- 查看刷新策略
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_refresh_continuous_aggregate';
```

---

## 4. 数据保留策略（Retention Policies）

### 4.1 创建保留策略

**定义**: 自动删除超过保留期的数据。

**创建保留策略**:

```sql
-- 保留30天的数据
SELECT add_retention_policy(
    'sensor_readings',
    INTERVAL '30 days'
);

-- 保留策略执行后，自动删除30天前的数据
```

---

### 4.2 条件保留策略

**按条件保留**:

```sql
-- 创建自定义保留函数
CREATE OR REPLACE FUNCTION drop_old_sensor_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- 删除30天前且质量标记为0的数据
    DELETE FROM sensor_readings
    WHERE time < NOW() - INTERVAL '30 days'
      AND quality = 0;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 添加自定义保留策略
SELECT add_job(
    'drop_old_sensor_data',
    INTERVAL '1 day',
    initial_start => NOW() + INTERVAL '1 hour'
);
```

---

## 5. 压缩策略

### 5.1 启用压缩

**压缩Hypertable**:

```sql
-- 启用压缩
ALTER TABLE sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- 添加压缩策略（压缩7天前的数据）
SELECT add_compression_policy(
    'sensor_readings',
    INTERVAL '7 days'
);
```

---

### 5.2 压缩效果

**查看压缩统计**:

```sql
-- 查看压缩chunk信息
SELECT
    chunk_name,
    pg_size_pretty(before_compression_total_bytes) AS before_size,
    pg_size_pretty(after_compression_total_bytes) AS after_size,
    ROUND(100.0 * (1 - after_compression_total_bytes::NUMERIC / before_compression_total_bytes), 2) AS compression_ratio
FROM timescaledb_information.compressed_chunk_stats
WHERE hypertable_name = 'sensor_readings';
```

---

## 6. 查询优化

### 6.1 时间范围查询

**优化时间范围查询**:

```sql
-- ✅ 正确：使用时间范围查询（自动分区剪枝）
SELECT * FROM sensor_readings
WHERE time >= NOW() - INTERVAL '24 hours'
  AND device_id = 123;

-- ❌ 错误：使用函数（分区剪枝失效）
SELECT * FROM sensor_readings
WHERE DATE_TRUNC('day', time) = CURRENT_DATE
  AND device_id = 123;
```

---

### 6.2 使用连续聚合

**查询聚合数据**:

```sql
-- 使用连续聚合查询（性能更好）
SELECT
    bucket,
    device_id,
    avg_value,
    min_value,
    max_value
FROM sensor_readings_hourly
WHERE bucket >= NOW() - INTERVAL '7 days'
  AND device_id = 123
ORDER BY bucket DESC;
```

---

### 6.3 使用Gap-filling

**填充缺失数据**:

```sql
-- 使用time_bucket_gapfill填充缺失时间点
SELECT
    time_bucket_gapfill('1 hour', time,
        start => NOW() - INTERVAL '24 hours',
        finish => NOW()) AS bucket,
    device_id,
    LOCF(AVG(value)) AS avg_value  -- Last Observation Carried Forward
FROM sensor_readings
WHERE time >= NOW() - INTERVAL '24 hours'
  AND device_id = 123
GROUP BY bucket, device_id
ORDER BY bucket;
```

---

## 7. 最佳实践

### 7.1 设计原则

**原则1: 选择合适的chunk时间间隔**:

- 高频数据（秒级）：1天
- 中频数据（分钟级）：1周
- 低频数据（小时级）：1月

**原则2: 使用连续聚合预计算**:

- 创建多级聚合（小时、天、周）
- 减少实时查询计算量

**原则3: 配置数据保留策略**:

- 原始数据保留30-90天
- 聚合数据保留1-2年

---

### 7.2 性能优化

**索引策略**:

```sql
-- 创建复合索引（设备ID + 时间）
CREATE INDEX idx_sensor_readings_device_time ON sensor_readings(device_id, time DESC);

-- 创建部分索引（仅索引活跃设备）
CREATE INDEX idx_sensor_readings_active_device ON sensor_readings(device_id, time DESC)
WHERE device_id IN (SELECT device_id FROM active_devices);
```

**查询优化**:

```sql
-- 使用LIMIT限制结果集
SELECT * FROM sensor_readings
WHERE device_id = 123
ORDER BY time DESC
LIMIT 1000;

-- 使用时间范围限制
SELECT * FROM sensor_readings
WHERE device_id = 123
  AND time >= NOW() - INTERVAL '1 hour'
ORDER BY time DESC;
```

---

## 8. 相关资源

- [时序数据模型](./时序数据模型.md) - 时序数据建模基础
- [设备孪生模型](./设备孪生模型.md) - IoT设备建模
- [索引策略](../08-PostgreSQL建模实践/索引策略.md) - 时序数据索引策略
- TimescaleDB官方文档: <https://docs.timescale.com/>

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
