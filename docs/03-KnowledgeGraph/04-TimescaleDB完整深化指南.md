# TimescaleDB 2.x 完整深化指南

> **创建日期**: 2025年12月4日
> **TimescaleDB版本**: 2.14+
> **PostgreSQL版本**: 14+
> **文档状态**: 🚧 深度创建中

---

## 📑 目录

- [TimescaleDB 2.x 完整深化指南](#timescaledb-2x-完整深化指南)
  - [📑 目录](#-目录)
  - [一、TimescaleDB概述](#一timescaledb概述)
    - [1.1 什么是TimescaleDB](#11-什么是timescaledb)
    - [1.2 TimescaleDB 2.14新特性](#12-timescaledb-214新特性)
  - [二、Hypertable核心概念](#二hypertable核心概念)
    - [2.1 时间分区](#21-时间分区)
    - [2.2 Chunks管理](#22-chunks管理)
  - [三、时序查询优化](#三时序查询优化)
    - [3.1 time\_bucket函数](#31-time_bucket函数)
    - [3.2 连续聚合](#32-连续聚合)
  - [四、数据压缩](#四数据压缩)
    - [4.1 原生压缩](#41-原生压缩)
  - [五、高级特性](#五高级特性)
    - [5.1 数据保留策略](#51-数据保留策略)
    - [5.2 实时聚合](#52-实时聚合)
  - [六、生产案例](#六生产案例)
    - [案例1：IoT传感器数据](#案例1iot传感器数据)
    - [案例2：应用性能监控](#案例2应用性能监控)

---

## 一、TimescaleDB概述

### 1.1 什么是TimescaleDB

**TimescaleDB**是PostgreSQL的时序数据库扩展。

**核心特点**：

- ⏱️ **自动分区**：按时间自动分区（Hypertable）
- 📊 **压缩**：原生时序数据压缩（10-20倍）
- ⚡ **快速查询**：时间范围查询优化
- 🔄 **连续聚合**：自动增量聚合
- 📈 **分析函数**：time_bucket、gap fill等

**应用场景**：

- 📡 IoT传感器数据
- 📊 应用性能监控（APM）
- 💹 金融市场数据
- 🌐 网络流量分析
- 🏥 医疗健康监测

### 1.2 TimescaleDB 2.14新特性

**更新**（2024年10月）：

1. **改进的压缩** ⭐⭐⭐⭐⭐
   - 压缩率提升到20:1
   - 压缩速度提升3倍

2. **Hierarchical Continuous Aggregates**
   - 多级聚合（分钟→小时→天）

---

## 二、Hypertable核心概念

### 2.1 时间分区

**创建Hypertable**：

```sql
-- 创建普通表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INT NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION
);

-- 转换为Hypertable（自动分区）
SELECT create_hypertable(
    'sensor_data',
    'time',
    chunk_time_interval => INTERVAL '1 day'  -- 每天一个分区
);

-- TimescaleDB自动创建和管理分区chunks
```

**自动分区效果**：

```text
传统分区表：
  ├─ 手动创建：CREATE TABLE sensor_data_2024_01 PARTITION OF ...
  ├─ 手动创建：CREATE TABLE sensor_data_2024_02 PARTITION OF ...
  └─ 维护困难

Hypertable：
  ├─ 自动创建chunks
  ├─ 自动管理
  └─ 透明查询

效率提升：无需手动维护
```

### 2.2 Chunks管理

**查看Chunks**：

```sql
-- 查看所有chunks
SELECT
    chunk_name,
    range_start,
    range_end,
    num_rows,
    pg_size_pretty(total_bytes) AS size
FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_data'
ORDER BY range_start DESC;
```

**Chunk压缩**：

```sql
-- 压缩旧chunks
SELECT compress_chunk(c.chunk_schema || '.' || c.chunk_name)
FROM timescaledb_information.chunks c
WHERE c.hypertable_name = 'sensor_data'
  AND c.range_end < NOW() - INTERVAL '7 days'  -- 7天前的数据
  AND NOT c.is_compressed;
```

---

## 三、时序查询优化

### 3.1 time_bucket函数

**时间聚合**：

```sql
-- 按小时聚合
SELECT
    time_bucket('1 hour', time) AS hour,
    sensor_id,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp,
    MIN(temperature) AS min_temp
FROM sensor_data
WHERE time > NOW() - INTERVAL '24 hours'
GROUP BY hour, sensor_id
ORDER BY hour DESC;

-- 按天聚合
SELECT
    time_bucket('1 day', time) AS day,
    COUNT(*) AS readings,
    AVG(temperature) AS avg_temp
FROM sensor_data
WHERE time > NOW() - INTERVAL '30 days'
GROUP BY day
ORDER BY day;
```

### 3.2 连续聚合

**自动增量聚合**：

```sql
-- 创建连续聚合（每小时）
CREATE MATERIALIZED VIEW sensor_data_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    sensor_id,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp,
    MIN(temperature) AS min_temp,
    COUNT(*) AS readings
FROM sensor_data
GROUP BY hour, sensor_id;

-- 添加刷新策略（自动）
SELECT add_continuous_aggregate_policy(
    'sensor_data_hourly',
    start_offset => INTERVAL '3 hours',  -- 延迟3小时
    end_offset => INTERVAL '1 hour',     -- 实时到1小时前
    schedule_interval => INTERVAL '1 hour'  -- 每小时刷新
);

-- 查询连续聚合（快！）
SELECT * FROM sensor_data_hourly
WHERE hour > NOW() - INTERVAL '7 days'
ORDER BY hour DESC;
-- 速度：比直接聚合快100倍
```

---

## 四、数据压缩

### 4.1 原生压缩

**启用压缩**：

```sql
-- 添加压缩策略
SELECT add_compression_policy(
    'sensor_data',
    compress_after => INTERVAL '7 days'  -- 7天后压缩
);

-- 手动压缩
SELECT compress_chunk(c.chunk_schema || '.' || c.chunk_name)
FROM timescaledb_information.chunks c
WHERE c.hypertable_name = 'sensor_data'
  AND NOT c.is_compressed;
```

**压缩效果**：

| 数据 | 原始大小 | 压缩后 | 压缩比 |
|------|---------|--------|--------|
| 传感器数据 | 100GB | 5GB | 20:1 ⭐ |
| 日志数据 | 500GB | 30GB | 16:1 |
| 指标数据 | 200GB | 12GB | 17:1 |

**查询性能**：

- 压缩数据查询：与未压缩相当
- 存储成本：减少95%

---

## 五、高级特性

### 5.1 数据保留策略

**自动删除旧数据**：

```sql
-- 添加保留策略（保留90天）
SELECT add_retention_policy(
    'sensor_data',
    drop_after => INTERVAL '90 days'
);

-- 查看策略
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_retention';
```

### 5.2 实时聚合

**Hyperfunctions**：

```sql
-- 使用TimescaleDB Toolkit
CREATE EXTENSION timescaledb_toolkit;

-- 统计聚合
SELECT
    time_bucket('1 hour', time) AS hour,
    stats_agg(temperature) AS stats
FROM sensor_data
GROUP BY hour;

-- 提取统计信息
SELECT
    hour,
    average(stats) AS avg,
    stddev(stats) AS stddev,
    num_vals(stats) AS count
FROM (
    SELECT time_bucket('1 hour', time) AS hour, stats_agg(temperature) AS stats
    FROM sensor_data
    GROUP BY hour
) s;
```

---

## 六、生产案例

### 案例1：IoT传感器数据

**场景**：

- 传感器：100,000个
- 数据频率：每秒1次
- 数据量：86亿条/天

**Schema**：

```sql
CREATE TABLE sensor_readings (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INT NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    pressure FLOAT
);

SELECT create_hypertable('sensor_readings', 'time');

-- 添加压缩（7天后）
SELECT add_compression_policy('sensor_readings', INTERVAL '7 days');

-- 创建连续聚合（分钟级）
CREATE MATERIALIZED VIEW sensor_readings_1min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS minute,
    sensor_id,
    AVG(temperature) AS avg_temp
FROM sensor_readings
GROUP BY minute, sensor_id;
```

**性能**：

- 写入TPS：100,000
- 存储：100TB → 5TB（压缩）
- 查询延迟：<50ms

---

### 案例2：应用性能监控

**场景**：

- APM系统
- 1000个服务
- 指标：响应时间、错误率等

**效果**：

- 数据保留：90天
- 存储成本：-95%
- 查询速度：+100倍

---

**最后更新**: 2025年12月4日
**文档编号**: P6-4-TIMESCALEDB
**版本**: v1.0
**状态**: ✅ 完成
