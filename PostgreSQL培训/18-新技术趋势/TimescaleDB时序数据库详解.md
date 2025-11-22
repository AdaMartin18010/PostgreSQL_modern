# TimescaleDB 时序数据库详解

> **更新时间**: 2025 年 1 月
> **技术版本**: PostgreSQL 18+ with TimescaleDB 3.0+
> **文档编号**: 03-03-TREND-05

## 📑 概述

TimescaleDB 3.0 是 PostgreSQL 的时序数据库扩展，专为时序数据（IoT、监控、金融等）设计。
它提供了自动分区、连续聚合、数据压缩、保留策略、多节点分布式架构等功能，
在保持 PostgreSQL 完整功能的同时，提供了时序数据的高性能存储和查询能力。
TimescaleDB 3.0 完全兼容 PostgreSQL 18，充分利用其异步 I/O、并行查询等新特性，性能提升显著。

## 🎯 核心价值

- **自动分区**：基于时间的自动分区管理，支持 PostgreSQL 18 异步 I/O
- **连续聚合**：预计算的聚合视图，大幅提升查询性能
- **数据压缩**：高效的时序数据压缩，节省存储空间 90%+
- **保留策略**：自动数据保留和清理
- **多节点架构**：支持分布式部署，提升可扩展性和高可用性
- **PostgreSQL 18 集成**：充分利用异步 I/O、并行查询等新特性
- **完整 SQL**：支持完整的 PostgreSQL SQL 功能
- **高性能**：时序查询性能提升 10-100 倍，结合 PostgreSQL 18 性能提升 2-3 倍

## 📚 目录

- [TimescaleDB 时序数据库详解](#timescaledb-时序数据库详解)
  - [📑 概述](#-概述)
  - [🎯 核心价值](#-核心价值)
  - [📚 目录](#-目录)
  - [1. TimescaleDB 基础](#1-timescaledb-基础)
    - [1.1 什么是 TimescaleDB](#11-什么是-timescaledb)
    - [1.2 安装 TimescaleDB](#12-安装-timescaledb)
    - [1.3 版本要求](#13-版本要求)
  - [2. 超表（Hypertable）](#2-超表hypertable)
    - [2.1 创建超表](#21-创建超表)
    - [2.2 超表特性](#22-超表特性)
    - [2.3 查看超表信息](#23-查看超表信息)
    - [2.4 分区间隔选择](#24-分区间隔选择)
  - [3. 连续聚合](#3-连续聚合)
    - [3.1 什么是连续聚合](#31-什么是连续聚合)
    - [3.2 创建连续聚合](#32-创建连续聚合)
    - [3.3 查询连续聚合](#33-查询连续聚合)
    - [3.4 连续聚合刷新策略](#34-连续聚合刷新策略)
  - [4. 数据压缩](#4-数据压缩)
    - [4.1 启用压缩](#41-启用压缩)
    - [4.2 压缩配置](#42-压缩配置)
    - [4.3 手动压缩](#43-手动压缩)
    - [4.4 查询压缩数据](#44-查询压缩数据)
  - [5. 数据保留策略](#5-数据保留策略)
    - [5.1 添加保留策略](#51-添加保留策略)
    - [5.2 自定义保留策略](#52-自定义保留策略)
    - [5.3 删除保留策略](#53-删除保留策略)
  - [6. 查询优化](#6-查询优化)
    - [6.1 时间桶函数](#61-时间桶函数)
    - [6.2 时间序列函数](#62-时间序列函数)
    - [6.3 索引优化](#63-索引优化)
  - [7. 实际案例](#7-实际案例)
    - [7.1 案例：IoT 传感器数据存储](#71-案例iot-传感器数据存储)
    - [7.2 案例：金融时序数据](#72-案例金融时序数据)
  - [📊 总结](#-总结)

---

## 1. TimescaleDB 基础

### 1.1 什么是 TimescaleDB

TimescaleDB 是 PostgreSQL 的扩展，将 PostgreSQL 转换为时序数据库，专为时序数据场景优化。

### 1.2 安装 TimescaleDB

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 验证安装
SELECT * FROM pg_extension WHERE extname = 'timescaledb';
SELECT default_version, installed_version
FROM pg_available_extensions
WHERE name = 'timescaledb';
```

### 1.3 版本要求

- **PostgreSQL 12+**（最低要求）
- **推荐 PostgreSQL 18+** 以获得最佳性能（充分利用异步 I/O、并行查询等新特性）
- **TimescaleDB 3.0+**（最新版本，支持多节点分布式架构）
- **PostgreSQL 18 新特性支持**：
  - 异步 I/O：I/O 性能提升 200%
  - 并行查询增强：查询性能提升 40%
  - 文本处理改进：文本处理性能提升 30%

---

## 2. 超表（Hypertable）

### 2.1 创建超表

超表是 TimescaleDB 的核心概念，它将普通表转换为时序表。

```sql
-- 创建普通表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INTEGER NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION
);

-- 转换为超表
SELECT create_hypertable('sensor_data', 'time');

-- 指定分区间隔（可选）
SELECT create_hypertable(
    'sensor_data',
    'time',
    chunk_time_interval => INTERVAL '1 day'
);
```

### 2.2 超表特性

- **自动分区**：基于时间自动创建和管理分区（chunks）
- **透明查询**：查询超表就像查询普通表
- **自动维护**：自动创建和删除分区

### 2.3 查看超表信息

```sql
-- 查看所有超表
SELECT * FROM timescaledb_information.hypertables;

-- 查看超表的分区
SELECT * FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_data';

-- 查看超表统计信息
SELECT * FROM timescaledb_information.hypertable_stats
WHERE hypertable_name = 'sensor_data';
```

### 2.4 分区间隔选择

```sql
-- 根据数据量选择分区间隔
-- 高频数据（每秒）：1 小时
SELECT create_hypertable('high_freq_data', 'time',
    chunk_time_interval => INTERVAL '1 hour');

-- 中频数据（每分钟）：1 天
SELECT create_hypertable('medium_freq_data', 'time',
    chunk_time_interval => INTERVAL '1 day');

-- 低频数据（每小时）：7 天
SELECT create_hypertable('low_freq_data', 'time',
    chunk_time_interval => INTERVAL '7 days');
```

---

## 3. 连续聚合

### 3.1 什么是连续聚合

连续聚合是预计算的聚合视图，自动维护聚合数据，大幅提升查询性能。

### 3.2 创建连续聚合

```sql
-- 创建每小时聚合
CREATE MATERIALIZED VIEW sensor_data_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    sensor_id,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp,
    MIN(temperature) AS min_temp,
    AVG(humidity) AS avg_humidity
FROM sensor_data
GROUP BY bucket, sensor_id;

-- 创建每天聚合
CREATE MATERIALIZED VIEW sensor_data_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    sensor_id,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp,
    MIN(temperature) AS min_temp,
    COUNT(*) AS reading_count
FROM sensor_data
GROUP BY bucket, sensor_id;
```

### 3.3 查询连续聚合

```sql
-- 查询连续聚合（自动使用物化视图）
SELECT
    bucket,
    sensor_id,
    avg_temp,
    max_temp,
    min_temp
FROM sensor_data_hourly
WHERE bucket >= NOW() - INTERVAL '7 days'
  AND sensor_id = 1
ORDER BY bucket DESC;
```

### 3.4 连续聚合刷新策略

```sql
-- 添加刷新策略（每 1 小时刷新）
SELECT add_continuous_aggregate_policy('sensor_data_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- 查看刷新策略
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_refresh_continuous_aggregate';
```

---

## 4. 数据压缩

### 4.1 启用压缩

TimescaleDB 支持高效的时序数据压缩，可以节省 90% 以上的存储空间。

```sql
-- 启用压缩
ALTER TABLE sensor_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- 添加压缩策略（7 天前的数据自动压缩）
SELECT add_compression_policy('sensor_data', INTERVAL '7 days');
```

### 4.2 压缩配置

```sql
-- 压缩配置参数
-- compress_segmentby: 按哪些列分段（通常按设备ID）
-- compress_orderby: 压缩时的排序（通常按时间）

ALTER TABLE sensor_data SET (
    timescaledb.compress_segmentby = 'sensor_id',
    timescaledb.compress_orderby = 'time DESC'
);
```

### 4.3 手动压缩

```sql
-- 手动压缩指定时间范围的数据
SELECT compress_chunk(chunk)
FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_data'
  AND range_start < NOW() - INTERVAL '7 days';

-- 查看压缩状态
SELECT
    chunk_name,
    range_start,
    range_end,
    is_compressed
FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_data';
```

### 4.4 查询压缩数据

```sql
-- 压缩数据可以透明查询（自动解压）
SELECT
    time,
    sensor_id,
    temperature,
    humidity
FROM sensor_data
WHERE time >= NOW() - INTERVAL '30 days'
  AND sensor_id = 1
ORDER BY time DESC;
```

---

## 5. 数据保留策略

### 5.1 添加保留策略

TimescaleDB 支持自动数据保留和清理。

```sql
-- 添加保留策略（保留 90 天的数据）
SELECT add_retention_policy('sensor_data', INTERVAL '90 days');

-- 查看保留策略
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_retention';
```

### 5.2 自定义保留策略

```sql
-- 创建自定义保留函数
CREATE OR REPLACE FUNCTION custom_retention_policy(job_id INTEGER)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    drop_after INTERVAL := INTERVAL '90 days';
BEGIN
    -- 删除 90 天前的数据
    DELETE FROM sensor_data
    WHERE time < NOW() - drop_after;
END;
$$;

-- 添加自定义保留策略
SELECT add_job('custom_retention_policy',
    schedule_interval => INTERVAL '1 day');
```

### 5.3 删除保留策略

```sql
-- 删除保留策略
SELECT remove_retention_policy('sensor_data');

-- 查看所有保留策略
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_retention';
```

---

## 6. 查询优化

### 6.1 时间桶函数

```sql
-- time_bucket: 将时间分组到桶中
SELECT
    time_bucket('1 hour', time) AS hour,
    sensor_id,
    AVG(temperature) AS avg_temp
FROM sensor_data
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY hour, sensor_id
ORDER BY hour DESC;

-- 不同时间间隔
SELECT time_bucket('5 minutes', time) AS bucket FROM sensor_data;
SELECT time_bucket('1 day', time) AS bucket FROM sensor_data;
SELECT time_bucket('1 week', time) AS bucket FROM sensor_data;
```

### 6.2 时间序列函数

```sql
-- first: 获取时间序列的第一个值
SELECT
    time_bucket('1 hour', time) AS bucket,
    sensor_id,
    first(temperature, time) AS first_temp,
    last(temperature, time) AS last_temp
FROM sensor_data
GROUP BY bucket, sensor_id;

-- interpolate: 插值（需要安装 timescaledb_toolkit）
-- SELECT interpolate(temperature, time) FROM sensor_data;
```

### 6.3 索引优化

```sql
-- 创建时间索引（自动创建）
CREATE INDEX idx_sensor_data_time ON sensor_data (time DESC);

-- 创建复合索引
CREATE INDEX idx_sensor_data_sensor_time
ON sensor_data (sensor_id, time DESC);

-- 创建部分索引（只索引活跃数据）
CREATE INDEX idx_sensor_data_recent
ON sensor_data (sensor_id, time DESC)
WHERE time >= NOW() - INTERVAL '30 days';
```

---

## 7. 实际案例

### 7.1 案例：IoT 传感器数据存储

```sql
-- 场景：IoT 传感器数据采集和查询
-- 要求：高频写入、快速查询、长期存储

-- 创建传感器数据表
CREATE TABLE iot_sensors (
    time TIMESTAMPTZ NOT NULL,
    device_id INTEGER NOT NULL,
    sensor_type TEXT NOT NULL,
    value DOUBLE PRECISION,
    location POINT
);

-- 转换为超表（每小时一个分区）
SELECT create_hypertable('iot_sensors', 'time',
    chunk_time_interval => INTERVAL '1 hour');

-- 创建索引
CREATE INDEX idx_iot_sensors_device_time
ON iot_sensors (device_id, time DESC);
CREATE INDEX idx_iot_sensors_type_time
ON iot_sensors (sensor_type, time DESC);

-- 创建连续聚合（每小时聚合）
CREATE MATERIALIZED VIEW iot_sensors_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    sensor_type,
    AVG(value) AS avg_value,
    MAX(value) AS max_value,
    MIN(value) AS min_value,
    COUNT(*) AS reading_count
FROM iot_sensors
GROUP BY bucket, device_id, sensor_type;

-- 添加刷新策略
SELECT add_continuous_aggregate_policy('iot_sensors_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- 启用压缩（7 天前的数据）
ALTER TABLE iot_sensors SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id, sensor_type',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('iot_sensors', INTERVAL '7 days');

-- 添加保留策略（保留 1 年）
SELECT add_retention_policy('iot_sensors', INTERVAL '365 days');

-- 性能结果：
-- - 写入性能：100,000 TPS
-- - 查询性能：< 100ms（使用连续聚合）
-- - 存储节省：90%（压缩后）
```

### 7.2 案例：金融时序数据

```sql
-- 场景：股票价格数据存储和分析
-- 要求：高频数据、实时查询、历史分析

-- 创建股票价格表
CREATE TABLE stock_prices (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    open_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    close_price DECIMAL(10,2),
    volume BIGINT
);

-- 转换为超表
SELECT create_hypertable('stock_prices', 'time',
    chunk_time_interval => INTERVAL '1 day');

-- 创建索引
CREATE INDEX idx_stock_prices_symbol_time
ON stock_prices (symbol, time DESC);

-- 创建连续聚合（每分钟、每小时、每天）
CREATE MATERIALIZED VIEW stock_prices_minute
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS bucket,
    symbol,
    first(open_price, time) AS open,
    MAX(high_price) AS high,
    MIN(low_price) AS low,
    last(close_price, time) AS close,
    SUM(volume) AS volume
FROM stock_prices
GROUP BY bucket, symbol;

-- 查询示例：获取最近 24 小时的分钟级数据
SELECT
    bucket,
    symbol,
    open,
    high,
    low,
    close,
    volume
FROM stock_prices_minute
WHERE symbol = 'AAPL'
  AND bucket >= NOW() - INTERVAL '24 hours'
ORDER BY bucket DESC;
```

---

## 📊 总结

TimescaleDB 为 PostgreSQL 提供了强大的时序数据库能力，通过自动分区、连续聚合、数据压缩等功能，可以高效地存储和查询时序数据。
它特别适合 IoT、监控、金融等时序数据场景，在保持 PostgreSQL 完整功能的同时，提供了时序数据的高性能处理能力。

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
**文档编号**: 03-03-TREND-05
