# 【深入】TimescaleDB时序数据库完整实战指南

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 13+, TimescaleDB 2.13+
> **难度等级**: ⭐⭐⭐⭐ 高级 | **预计学习时间**: 8-10小时

---

## 📋 目录

- [【深入】TimescaleDB时序数据库完整实战指南](#深入timescaledb时序数据库完整实战指南)
  - [📋 目录](#-目录)
  - [1. 课程概述](#1-课程概述)
    - [1.1 什么是TimescaleDB？](#11-什么是timescaledb)
      - [核心特性](#核心特性)
      - [适用场景](#适用场景)
    - [1.2 TimescaleDB vs 其他方案](#12-timescaledb-vs-其他方案)
  - [2. 时序数据库基础](#2-时序数据库基础)
    - [2.1 时序数据特征](#21-时序数据特征)
      - [示例：IoT传感器数据](#示例iot传感器数据)
    - [2.2 时序数据存储挑战](#22-时序数据存储挑战)
  - [3. TimescaleDB架构](#3-timescaledb架构)
    - [3.1 核心概念](#31-核心概念)
    - [3.2 Chunk管理](#32-chunk管理)
    - [3.3 架构图](#33-架构图)
  - [4. 安装与配置](#4-安装与配置)
    - [4.1 安装TimescaleDB](#41-安装timescaledb)
      - [Ubuntu/Debian](#ubuntudebian)
      - [Docker](#docker)
      - [Docker Compose](#docker-compose)
    - [4.2 初始化](#42-初始化)
    - [4.3 性能调优配置](#43-性能调优配置)
  - [5. Hypertable超表](#5-hypertable超表)
    - [5.1 创建Hypertable](#51-创建hypertable)
    - [5.2 多维分区](#52-多维分区)
    - [5.3 Hypertable管理](#53-hypertable管理)
  - [6. 数据写入优化](#6-数据写入优化)
    - [6.1 批量写入](#61-批量写入)
    - [6.2 并行写入](#62-并行写入)
    - [6.3 无序写入优化](#63-无序写入优化)
  - [7. 时序查询](#7-时序查询)
    - [7.1 时间桶聚合（time\_bucket）](#71-时间桶聚合time_bucket)
    - [7.2 Gap Filling（填补缺失）](#72-gap-filling填补缺失)
    - [7.3 窗口函数](#73-窗口函数)
    - [7.4 Downsampling（降采样）](#74-downsampling降采样)
  - [8. 连续聚合](#8-连续聚合)
    - [8.1 Continuous Aggregate基础](#81-continuous-aggregate基础)
    - [8.2 实时聚合](#82-实时聚合)
    - [8.3 多级聚合](#83-多级聚合)
    - [8.4 连续聚合管理](#84-连续聚合管理)
  - [9. 数据压缩与保留](#9-数据压缩与保留)
    - [9.1 数据压缩](#91-数据压缩)
      - [启用压缩](#启用压缩)
      - [压缩原理](#压缩原理)
    - [9.2 数据保留策略](#92-数据保留策略)
    - [9.3 分层存储](#93-分层存储)
  - [10. 高级特性](#10-高级特性)
    - [10.1 Hyperfunctions（高级时序函数）](#101-hyperfunctions高级时序函数)
    - [10.2 数据分层查询](#102-数据分层查询)
    - [10.3 分布式Hypertable（多节点）](#103-分布式hypertable多节点)
  - [11. 性能优化](#11-性能优化)
    - [11.1 索引策略](#111-索引策略)
    - [11.2 查询优化](#112-查询优化)
    - [11.3 批量操作优化](#113-批量操作优化)
    - [11.4 监控查询](#114-监控查询)
  - [12. 生产实战案例](#12-生产实战案例)
    - [12.1 案例1：IoT设备监控平台](#121-案例1iot设备监控平台)
      - [需求](#需求)
      - [实现](#实现)
    - [12.2 案例2：金融市场数据](#122-案例2金融市场数据)
    - [12.3 案例3：APM（应用性能监控）](#123-案例3apm应用性能监控)
  - [13. 最佳实践](#13-最佳实践)
    - [13.1 设计原则](#131-设计原则)
      - [✅ 推荐做法](#-推荐做法)
    - [13.2 运维Checklist](#132-运维checklist)
    - [13.3 性能调优Checklist](#133-性能调优checklist)
  - [14. FAQ与疑难解答](#14-faq与疑难解答)
    - [Q1: Hypertable vs PostgreSQL分区表？](#q1-hypertable-vs-postgresql分区表)
    - [Q2: chunk数量过多怎么办？](#q2-chunk数量过多怎么办)
    - [Q3: 压缩后能更新数据吗？](#q3-压缩后能更新数据吗)
    - [Q4: 如何迁移现有PostgreSQL时序数据到TimescaleDB？](#q4-如何迁移现有postgresql时序数据到timescaledb)
    - [Q5: TimescaleDB可以用于非时序数据吗？](#q5-timescaledb可以用于非时序数据吗)
  - [📚 延伸阅读](#-延伸阅读)
    - [官方资源](#官方资源)
    - [相关技术](#相关技术)
    - [推荐阅读](#推荐阅读)
  - [✅ 学习检查清单](#-学习检查清单)
  - [💡 下一步学习](#-下一步学习)

---

## 1. 课程概述

### 1.1 什么是TimescaleDB？

**TimescaleDB** 是PostgreSQL的时序数据库扩展，专为时间序列数据优化，提供10-100倍的插入性能和自动数据管理。

#### 核心特性

| 特性 | 说明 | 优势 |
|------|------|------|
| **Hypertable** | 自动分区管理 | 无需手动创建分区 |
| **高速写入** | 批量插入优化 | 100万+ rows/秒 |
| **连续聚合** | 实时物化视图 | 秒级延迟 |
| **数据压缩** | 列式压缩 | 节省90%+存储 |
| **数据保留** | 自动过期删除 | 无需维护脚本 |
| **SQL兼容** | 100% PostgreSQL | 零学习成本 |
| **时序函数** | 专用分析函数 | gap filling, LOCF等 |

#### 适用场景

**✅ 理想场景**:

- IoT设备监控（传感器数据）
- 应用性能监控（APM）
- 金融市场数据（股票、加密货币）
- 日志与事件数据
- 气象与环境监测
- 工业生产监控

**❌ 不适合**:

- 非时序数据为主
- 大量更新/删除操作
- 复杂事务处理

### 1.2 TimescaleDB vs 其他方案

```text
TimescaleDB vs InfluxDB:
✅ SQL标准（学习成本低）
✅ 关系数据+时序数据混合
✅ 复杂查询支持更好
✅ ACID事务保证
❌ 纯时序写入性能略逊

TimescaleDB vs ClickHouse:
✅ 实时写入（非批量）
✅ 更新/删除支持
✅ OLTP+OLAP混合
❌ 纯OLAP分析性能略逊
❌ 数据压缩比不如ClickHouse

TimescaleDB vs Prometheus:
✅ 更灵活的数据模型
✅ 更长的数据保留
✅ 更复杂的查询
✅ 关系数据JOIN
❌ Metrics抓取生态不如Prometheus

TimescaleDB vs 原生PostgreSQL分区:
✅ 自动分区管理（无需手动创建）
✅ 自动压缩、保留策略
✅ 连续聚合（增量更新）
✅ 时序专用函数
✅ 性能优化（批量插入、查询）
```

---

## 2. 时序数据库基础

### 2.1 时序数据特征

```text
时序数据的典型特征：

1. 时间戳：每条记录必有时间标识
2. 只追加：基本只写入，极少更新
3. 时间顺序：按时间排序查询
4. 聚合分析：时间窗口聚合（avg, max, min）
5. 数据量大：持续不断产生
6. 冷热分层：近期数据热，历史数据冷
```

#### 示例：IoT传感器数据

```sql
-- 典型时序数据表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,      -- 时间戳
    device_id INT NOT NULL,          -- 设备ID（维度）
    location TEXT,                   -- 位置（维度）
    temperature DOUBLE PRECISION,    -- 温度（指标）
    humidity DOUBLE PRECISION,       -- 湿度（指标）
    pressure DOUBLE PRECISION        -- 气压（指标）
);

-- 查询模式：时间范围 + 聚合
SELECT
    time_bucket('1 hour', time) AS hour,
    device_id,
    AVG(temperature) AS avg_temp,
    MAX(humidity) AS max_humidity
FROM sensor_data
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY hour, device_id
ORDER BY hour DESC;
```

### 2.2 时序数据存储挑战

| 挑战 | 传统PostgreSQL | TimescaleDB解决方案 |
|------|----------------|---------------------|
| **高并发写入** | 单表锁竞争 | 自动分片，并行写入 |
| **海量数据** | 索引膨胀 | 自动分区+压缩 |
| **查询性能** | 全表扫描 | 时间索引+分区裁剪 |
| **数据老化** | 手动删除 | 自动保留策略 |
| **聚合分析** | 每次重算 | 连续聚合（增量） |

---

## 3. TimescaleDB架构

### 3.1 核心概念

```text
┌───────────────────────────────────────┐
│        Hypertable（逻辑表）            │
│  ┌─────────────────────────────────┐ │
│  │  SELECT * FROM sensor_data;     │ │
│  │  → 自动路由到相关Chunk           │ │
│  └─────────────────────────────────┘ │
└──────────┬────────────────────────────┘
           │
    自动分区（按时间）
           │
     ┌─────┴─────┬─────────┬──────────┐
     │           │         │          │
  ┌──▼──┐    ┌──▼──┐  ┌──▼──┐   ┌───▼───┐
  │Chunk│    │Chunk│  │Chunk│   │ Chunk │
  │ 1   │    │ 2   │  │ 3   │   │  ...  │
  │(1天)│    │(1天)│  │(1天)│   │       │
  └─────┘    └─────┘  └─────┘   └───────┘
  未压缩     压缩     压缩       已归档

特点：
- Hypertable：用户视角的单表
- Chunk：内部实际分区（按时间自动创建）
- 透明：应用无需关心分区细节
- 自动：创建、压缩、删除全自动
```

### 3.2 Chunk管理

```sql
-- Chunk是实际存储数据的分区
-- 示例：sensor_data的chunk结构

_timescaledb_internal._hyper_1_1_chunk  -- 2025-01-01
_timescaledb_internal._hyper_1_2_chunk  -- 2025-01-02
_timescaledb_internal._hyper_1_3_chunk  -- 2025-01-03
...

-- 用户查询Hypertable
SELECT * FROM sensor_data WHERE time >= '2025-01-02';

-- 内部实际查询（分区裁剪）
SELECT * FROM _timescaledb_internal._hyper_1_2_chunk
UNION ALL
SELECT * FROM _timescaledb_internal._hyper_1_3_chunk;
-- 自动跳过不相关的chunk
```

### 3.3 架构图

```text
┌─────────────────────────────────────────────┐
│         Application Layer                   │
│  JDBC / psycopg2 / Go pgx / ...            │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         TimescaleDB Extension               │
├─────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐  │
│  │  Hypertable Manager                  │  │
│  │  - 自动创建/删除chunk                 │  │
│  │  - 查询路由                          │  │
│  │  - 分区裁剪                          │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  Continuous Aggregate Engine         │  │
│  │  - 增量更新物化视图                   │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  Compression Engine                  │  │
│  │  - 列式压缩                          │  │
│  │  - 自动压缩策略                       │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  Retention Policy                    │  │
│  │  - 自动删除过期数据                   │  │
│  └──────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         PostgreSQL Core                     │
│  Storage / Index / Transaction / WAL        │
└─────────────────────────────────────────────┘
```

---

## 4. 安装与配置

### 4.1 安装TimescaleDB

#### Ubuntu/Debian

```bash
# 添加TimescaleDB仓库
sudo apt-get install -y gnupg postgresql-common apt-transport-https lsb-release wget
sudo sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -

# 更新并安装
sudo apt-get update
sudo apt-get install -y timescaledb-2-postgresql-15

# 运行配置脚本
sudo timescaledb-tune --quiet --yes

# 重启PostgreSQL
sudo systemctl restart postgresql
```

#### Docker

```bash
# 快速启动
docker run -d --name timescaledb \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  timescale/timescaledb:latest-pg15

# 连接
docker exec -it timescaledb psql -U postgres
```

#### Docker Compose

```yaml
version: '3.8'
services:
  timescaledb:
    image: timescale/timescaledb:latest-pg15
    container_name: timescaledb
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: tsdb
    volumes:
      - timescaledb-data:/var/lib/postgresql/data
    command:
      - "postgres"
      - "-c"
      - "shared_preload_libraries=timescaledb"
      - "-c"
      - "max_connections=200"
      - "-c"
      - "shared_buffers=512MB"

volumes:
  timescaledb-data:
```

### 4.2 初始化

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 验证安装
SELECT default_version, installed_version
FROM pg_available_extensions
WHERE name = 'timescaledb';

-- 查看版本信息
SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';

-- 查看配置
SHOW timescaledb.telemetry_level;
SHOW timescaledb.max_background_workers;
```

### 4.3 性能调优配置

```sql
-- postgresql.conf推荐配置（16GB RAM服务器）

-- 基础配置
shared_preload_libraries = 'timescaledb'
max_connections = 200

-- 内存配置
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 64MB

-- WAL配置
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
checkpoint_completion_target = 0.9

-- TimescaleDB特定配置
timescaledb.max_background_workers = 8
timescaledb.last_tuned = '2025-01-01 00:00:00'
timescaledb.last_tuned_version = '0.15.0'

-- 并行查询
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

-- 执行配置后
SELECT pg_reload_conf();
```

---

## 5. Hypertable超表

### 5.1 创建Hypertable

```sql
-- 1. 创建普通表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    cpu_usage DOUBLE PRECISION
);

-- 2. 转换为Hypertable
SELECT create_hypertable(
    'sensor_data',           -- 表名
    'time',                  -- 时间列
    chunk_time_interval => INTERVAL '1 day',  -- 每个chunk的时间跨度
    if_not_exists => TRUE
);

-- 3. 创建索引
CREATE INDEX sensor_data_device_time_idx
ON sensor_data (device_id, time DESC);

CREATE INDEX sensor_data_time_idx
ON sensor_data (time DESC);
```

### 5.2 多维分区

```sql
-- 按时间+空间维度分区
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    location TEXT NOT NULL,
    value DOUBLE PRECISION
);

SELECT create_hypertable(
    'metrics',
    'time',
    partitioning_column => 'device_id',  -- 空间分区列
    number_partitions => 4,              -- 空间分区数
    chunk_time_interval => INTERVAL '1 day'
);

-- 结果：4个空间分区 × N个时间分区 = 4N个chunk
-- 优势：并行写入、查询时可以同时裁剪时间和空间
```

### 5.3 Hypertable管理

```sql
-- 查看所有Hypertable
SELECT * FROM timescaledb_information.hypertables;

-- 查看特定Hypertable的chunk
SELECT * FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_data'
ORDER BY range_start DESC;

-- 查看Hypertable详细信息
SELECT
    hypertable_name,
    num_chunks,
    table_size,
    index_size,
    total_size
FROM timescaledb_information.hypertable
WHERE hypertable_name = 'sensor_data';

-- 删除Hypertable
DROP TABLE sensor_data;  -- 自动清理所有chunk
```

---

## 6. 数据写入优化

### 6.1 批量写入

```sql
-- ❌ 慢：逐行插入
DO $$
BEGIN
    FOR i IN 1..10000 LOOP
        INSERT INTO sensor_data (time, device_id, temperature)
        VALUES (NOW(), 1, 25.0 + random());
    END LOOP;
END $$;

-- ✅ 快：批量插入
INSERT INTO sensor_data (time, device_id, temperature, humidity)
SELECT
    NOW() - (random() * INTERVAL '1 day'),
    (random() * 100)::INT,
    20 + random() * 15,
    40 + random() * 40
FROM generate_series(1, 1000000);

-- ✅ 最快：COPY
COPY sensor_data (time, device_id, temperature, humidity)
FROM STDIN CSV;
-- ... 大量数据 ...
\.
```

### 6.2 并行写入

```python
# Python并行写入示例
import psycopg2
from multiprocessing import Pool
import random
from datetime import datetime, timedelta

def insert_batch(worker_id):
    conn = psycopg2.connect("dbname=tsdb user=postgres")
    cur = conn.cursor()

    # 每个worker插入100万条
    batch_size = 10000
    for batch in range(100):
        data = [
            (
                datetime.now() - timedelta(seconds=random.randint(0, 86400)),
                random.randint(1, 1000),
                20 + random.random() * 15,
                40 + random.random() * 40
            )
            for _ in range(batch_size)
        ]

        cur.executemany(
            "INSERT INTO sensor_data (time, device_id, temperature, humidity) VALUES (%s, %s, %s, %s)",
            data
        )
        conn.commit()

        if batch % 10 == 0:
            print(f"Worker {worker_id}: {batch * batch_size} rows inserted")

    cur.close()
    conn.close()

# 启动8个并行worker
if __name__ == '__main__':
    with Pool(8) as pool:
        pool.map(insert_batch, range(8))
```

### 6.3 无序写入优化

```sql
-- 问题：时间戳乱序插入（IoT数据延迟到达）
-- TimescaleDB优化：自动路由到正确的chunk

-- 配置：允许较大的时间窗口乱序
SELECT set_chunk_time_interval('sensor_data', INTERVAL '1 day');

-- 如果数据可能延迟数天，增大chunk间隔
SELECT set_chunk_time_interval('sensor_data', INTERVAL '7 days');

-- 或使用更细粒度的chunk + 合并
-- （适用于大部分数据按时间有序，少量乱序）
```

---

## 7. 时序查询

### 7.1 时间桶聚合（time_bucket）

```sql
-- 按小时聚合
SELECT
    time_bucket('1 hour', time) AS hour,
    device_id,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp,
    MIN(temperature) AS min_temp,
    COUNT(*) AS sample_count
FROM sensor_data
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY hour, device_id
ORDER BY hour DESC, device_id;

-- 按5分钟聚合
SELECT
    time_bucket('5 minutes', time) AS bucket,
    AVG(cpu_usage) AS avg_cpu,
    MAX(cpu_usage) AS max_cpu
FROM sensor_data
WHERE time >= NOW() - INTERVAL '1 hour'
  AND device_id = 123
GROUP BY bucket
ORDER BY bucket DESC;

-- 按天聚合（使用origin对齐到凌晨）
SELECT
    time_bucket('1 day', time, TIMESTAMPTZ '2025-01-01 00:00:00') AS day,
    COUNT(*) AS daily_count
FROM sensor_data
GROUP BY day
ORDER BY day DESC;
```

### 7.2 Gap Filling（填补缺失）

```sql
-- 问题：设备离线导致数据缺失
SELECT
    time_bucket('1 hour', time) AS hour,
    AVG(temperature) AS avg_temp
FROM sensor_data
WHERE device_id = 123
  AND time >= '2025-01-01' AND time < '2025-01-02'
GROUP BY hour
ORDER BY hour;

-- 结果可能缺少某些小时

-- 解决：time_bucket_gapfill
SELECT
    time_bucket_gapfill('1 hour', time) AS hour,
    AVG(temperature) AS avg_temp,
    locf(AVG(temperature)) AS avg_temp_filled  -- Last Observation Carried Forward
FROM sensor_data
WHERE device_id = 123
  AND time >= '2025-01-01' AND time < '2025-01-02'
GROUP BY hour
ORDER BY hour;

-- 或使用interpolate（线性插值）
SELECT
    time_bucket_gapfill('1 hour', time) AS hour,
    interpolate(AVG(temperature)) AS avg_temp_interpolated
FROM sensor_data
WHERE device_id = 123
  AND time >= '2025-01-01' AND time < '2025-01-02'
GROUP BY hour
ORDER BY hour;
```

### 7.3 窗口函数

```sql
-- 计算移动平均（滑动窗口）
SELECT
    time,
    device_id,
    temperature,
    AVG(temperature) OVER (
        PARTITION BY device_id
        ORDER BY time
        ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
    ) AS moving_avg_10
FROM sensor_data
WHERE device_id = 123
  AND time >= NOW() - INTERVAL '1 hour'
ORDER BY time DESC;

-- 计算变化率
SELECT
    time,
    device_id,
    temperature,
    temperature - LAG(temperature) OVER (
        PARTITION BY device_id ORDER BY time
    ) AS temp_change
FROM sensor_data
WHERE device_id = 123
  AND time >= NOW() - INTERVAL '1 hour'
ORDER BY time DESC;

-- 检测异常（超过3倍标准差）
WITH stats AS (
    SELECT
        device_id,
        AVG(temperature) AS mean,
        STDDEV(temperature) AS stddev
    FROM sensor_data
    WHERE time >= NOW() - INTERVAL '7 days'
    GROUP BY device_id
)
SELECT
    sd.time,
    sd.device_id,
    sd.temperature,
    s.mean,
    s.stddev,
    (sd.temperature - s.mean) / s.stddev AS z_score
FROM sensor_data sd
JOIN stats s ON sd.device_id = s.device_id
WHERE sd.time >= NOW() - INTERVAL '1 hour'
  AND ABS((sd.temperature - s.mean) / s.stddev) > 3
ORDER BY sd.time DESC;
```

### 7.4 Downsampling（降采样）

```sql
-- 将高频数据降采样到低频
CREATE TABLE sensor_data_hourly AS
SELECT
    time_bucket('1 hour', time) AS hour,
    device_id,
    AVG(temperature) AS avg_temperature,
    MAX(temperature) AS max_temperature,
    MIN(temperature) AS min_temperature,
    AVG(humidity) AS avg_humidity,
    COUNT(*) AS sample_count
FROM sensor_data
WHERE time >= '2025-01-01'
GROUP BY hour, device_id;

-- 创建为Hypertable
SELECT create_hypertable(
    'sensor_data_hourly',
    'hour',
    chunk_time_interval => INTERVAL '7 days'
);

-- 查询时优先使用降采样表
SELECT * FROM sensor_data_hourly
WHERE hour >= NOW() - INTERVAL '30 days';
```

---

## 8. 连续聚合

### 8.1 Continuous Aggregate基础

```sql
-- 创建连续聚合（类似物化视图，但增量更新）
CREATE MATERIALIZED VIEW sensor_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    device_id,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp,
    MIN(temperature) AS min_temp,
    COUNT(*) AS sample_count
FROM sensor_data
GROUP BY hour, device_id;

-- 添加刷新策略（自动更新）
SELECT add_continuous_aggregate_policy(
    'sensor_hourly',
    start_offset => INTERVAL '3 hours',    -- 保留3小时数据不聚合（允许乱序）
    end_offset => INTERVAL '1 hour',       -- 最新1小时不聚合（实时查询原表）
    schedule_interval => INTERVAL '1 hour' -- 每小时更新一次
);

-- 查询连续聚合（像普通表一样）
SELECT * FROM sensor_hourly
WHERE hour >= NOW() - INTERVAL '7 days'
  AND device_id = 123
ORDER BY hour DESC;
```

### 8.2 实时聚合

```sql
-- 实时聚合：自动合并物化数据+最新实时数据
ALTER MATERIALIZED VIEW sensor_hourly SET (timescaledb.materialized_only = false);

-- 查询时自动合并：
-- 1. 已物化的历史数据（快）
-- 2. 最新1小时的实时数据（实时计算）
SELECT * FROM sensor_hourly
WHERE hour >= NOW() - INTERVAL '7 days';
-- 无缝整合物化+实时数据！
```

### 8.3 多级聚合

```sql
-- 原始数据：每秒
-- 一级聚合：每分钟
CREATE MATERIALIZED VIEW sensor_minutely
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS minute,
    device_id,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp,
    MIN(temperature) AS min_temp
FROM sensor_data
GROUP BY minute, device_id;

-- 二级聚合：每小时（基于分钟聚合）
CREATE MATERIALIZED VIEW sensor_hourly_from_minutely
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', minute) AS hour,
    device_id,
    AVG(avg_temp) AS avg_temp,  -- 注意：avg of avg（近似）
    MAX(max_temp) AS max_temp,
    MIN(min_temp) AS min_temp
FROM sensor_minutely
GROUP BY hour, device_id;

-- 三级聚合：每天
CREATE MATERIALIZED VIEW sensor_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', hour) AS day,
    device_id,
    AVG(avg_temp) AS avg_temp,
    MAX(max_temp) AS max_temp,
    MIN(min_temp) AS min_temp
FROM sensor_hourly_from_minutely
GROUP BY day, device_id;

-- 查询策略：根据时间范围选择合适的聚合级别
-- < 1小时    → sensor_data（原始）
-- 1小时-1天  → sensor_minutely
-- 1天-30天   → sensor_hourly
-- > 30天     → sensor_daily
```

### 8.4 连续聚合管理

```sql
-- 查看所有连续聚合
SELECT * FROM timescaledb_information.continuous_aggregates;

-- 查看刷新策略
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_refresh_continuous_aggregate';

-- 手动刷新
CALL refresh_continuous_aggregate('sensor_hourly', '2025-01-01', '2025-01-02');

-- 删除刷新策略
SELECT remove_continuous_aggregate_policy('sensor_hourly');

-- 删除连续聚合
DROP MATERIALIZED VIEW sensor_hourly;
```

---

## 9. 数据压缩与保留

### 9.1 数据压缩

#### 启用压缩

```sql
-- 1. 在Hypertable上启用压缩
ALTER TABLE sensor_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',  -- 按设备分段压缩
    timescaledb.compress_orderby = 'time DESC'     -- 时间降序排列
);

-- 2. 添加自动压缩策略
SELECT add_compression_policy(
    'sensor_data',
    compress_after => INTERVAL '7 days'  -- 7天后压缩
);

-- 3. 手动压缩特定chunk
SELECT compress_chunk(i) FROM show_chunks('sensor_data', older_than => INTERVAL '8 days') i;

-- 查看压缩率
SELECT
    chunk_schema,
    chunk_name,
    compression_status,
    before_compression_total_bytes,
    after_compression_total_bytes,
    pg_size_pretty(before_compression_total_bytes) AS size_before,
    pg_size_pretty(after_compression_total_bytes) AS size_after,
    ROUND((1 - after_compression_total_bytes::numeric / before_compression_total_bytes) * 100, 2) AS compression_ratio
FROM timescaledb_information.compressed_chunk_stats
WHERE hypertable_name = 'sensor_data';

-- 典型压缩率：90-95%！
```

#### 压缩原理

```text
未压缩Chunk（行式存储）：
Row 1: time=2025-01-01 00:00:00, device_id=1, temp=25.3, humidity=60.5
Row 2: time=2025-01-01 00:01:00, device_id=1, temp=25.4, humidity=60.6
Row 3: time=2025-01-01 00:02:00, device_id=1, temp=25.3, humidity=60.7
...

压缩Chunk（列式存储+算法压缩）：
Segment: device_id=1
  time列: [2025-01-01 00:00:00, 00:01:00, 00:02:00, ...] → Delta编码
  temp列: [25.3, 25.4, 25.3, ...] → Gorilla压缩（时序专用）
  humidity列: [60.5, 60.6, 60.7, ...] → Gorilla压缩

优势：
✅ 90-95%压缩率
✅ 查询时无需解压全部数据（列式访问）
✅ 自动压缩，无需维护
```

### 9.2 数据保留策略

```sql
-- 自动删除超过1年的数据
SELECT add_retention_policy(
    'sensor_data',
    drop_after => INTERVAL '1 year'
);

-- 查看保留策略
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_retention';

-- 修改保留策略
SELECT remove_retention_policy('sensor_data');
SELECT add_retention_policy('sensor_data', drop_after => INTERVAL '2 years');

-- 手动删除旧chunk
DROP TABLE _timescaledb_internal._hyper_1_1_chunk;
-- 或使用函数
SELECT drop_chunks('sensor_data', older_than => INTERVAL '2 years');
```

### 9.3 分层存储

```sql
-- 策略：热数据（未压缩）+ 温数据（压缩）+ 冷数据（归档/删除）

-- 热数据：最近7天，未压缩，快速读写
-- 温数据：7-90天，压缩，节省空间
-- 冷数据：>90天，归档到S3或删除

-- 实现：
-- 1. 7天后压缩
SELECT add_compression_policy('sensor_data', compress_after => INTERVAL '7 days');

-- 2. 90天后归档到S3（使用pg_dump + cron）
-- 脚本示例：archive_old_data.sh
#!/bin/bash
DATE_90_DAYS_AGO=$(date -d '90 days ago' +%Y-%m-%d)

# 导出90天前的数据
pg_dump -h localhost -U postgres -d tsdb \
  -t sensor_data \
  --where="time < '$DATE_90_DAYS_AGO'" \
  | gzip > s3://my-bucket/archives/sensor_data_${DATE_90_DAYS_AGO}.sql.gz

# 删除已归档的数据
psql -h localhost -U postgres -d tsdb -c \
  "SELECT drop_chunks('sensor_data', older_than => INTERVAL '90 days');"

-- 3. Cron定时执行
-- 0 2 * * * /path/to/archive_old_data.sh
```

---

## 10. 高级特性

### 10.1 Hyperfunctions（高级时序函数）

```sql
-- 需要安装timescaledb_toolkit
CREATE EXTENSION timescaledb_toolkit;

-- 1. Stats Agg（统计聚合）
SELECT
    device_id,
    average(stats_agg(temperature)) AS avg_temp,
    stddev(stats_agg(temperature)) AS stddev_temp,
    skewness(stats_agg(temperature)) AS skew,
    kurtosis(stats_agg(temperature)) AS kurt
FROM sensor_data
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY device_id;

-- 2. Time-Weighted Average（时间加权平均）
SELECT
    device_id,
    average(time_weight('LOCF', time, temperature)) AS time_weighted_avg
FROM sensor_data
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY device_id;

-- 3. Heartbeat Agg（检测设备在线状态）
SELECT
    device_id,
    live_ranges(heartbeat_agg(time, INTERVAL '5 minutes')) AS uptime_ranges,
    uptime(heartbeat_agg(time, INTERVAL '5 minutes')) AS uptime_ratio
FROM sensor_data
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY device_id;

-- 4. Counter Agg（单调递增计数器处理，如网络字节数）
SELECT
    device_id,
    delta(counter_agg(time, bytes_sent)) AS total_bytes,
    rate(counter_agg(time, bytes_sent)) AS avg_rate
FROM network_stats
WHERE time >= NOW() - INTERVAL '1 hour'
GROUP BY device_id;
```

### 10.2 数据分层查询

```sql
-- 透明查询：自动选择最优数据源
CREATE VIEW sensor_unified AS
SELECT time, device_id, temperature FROM sensor_data          -- 最近数据
WHERE time >= NOW() - INTERVAL '1 day'
UNION ALL
SELECT hour AS time, device_id, avg_temp AS temperature      -- 中等历史
FROM sensor_hourly
WHERE hour >= NOW() - INTERVAL '30 days'
  AND hour < NOW() - INTERVAL '1 day'
UNION ALL
SELECT day AS time, device_id, avg_temp AS temperature       -- 远期历史
FROM sensor_daily
WHERE day < NOW() - INTERVAL '30 days';

-- 应用查询统一视图，无需关心数据在哪
SELECT * FROM sensor_unified
WHERE device_id = 123
  AND time >= NOW() - INTERVAL '60 days';
```

### 10.3 分布式Hypertable（多节点）

```sql
-- TimescaleDB多节点（Enterprise特性）
-- 类似Citus，将数据分布到多个节点

-- 在Access Node上：
SELECT add_data_node('data_node_1', host => 'dn1.example.com');
SELECT add_data_node('data_node_2', host => 'dn2.example.com');
SELECT add_data_node('data_node_3', host => 'dn3.example.com');

-- 创建分布式Hypertable
CREATE TABLE sensor_data_distributed (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    temperature DOUBLE PRECISION
);

SELECT create_distributed_hypertable(
    'sensor_data_distributed',
    'time',
    'device_id',  -- 空间分区键
    number_partitions => 3,  -- 分布到3个节点
    replication_factor => 2  -- 2副本
);

-- 查询：自动并行执行，从多个节点聚合结果
SELECT
    time_bucket('1 hour', time) AS hour,
    AVG(temperature) AS avg_temp
FROM sensor_data_distributed
WHERE time >= NOW() - INTERVAL '7 days'
GROUP BY hour;
-- Access Node自动路由查询到Data Nodes，并行执行后聚合
```

---

## 11. 性能优化

### 11.1 索引策略

```sql
-- 时序数据索引原则：

-- 1. 时间索引（自动创建）
-- Hypertable自动为时间列创建索引

-- 2. 复合索引（维度+时间）
CREATE INDEX sensor_data_device_time_idx
ON sensor_data (device_id, time DESC);

-- 3. 部分索引（特定条件）
CREATE INDEX sensor_data_high_temp_idx
ON sensor_data (time DESC)
WHERE temperature > 100;

-- 4. 避免在高基数列上创建索引
-- ❌ 不要
CREATE INDEX sensor_data_temp_idx ON sensor_data (temperature);
-- 时序数据的值通常高基数且不常用于精确匹配

-- 5. GIN索引用于JSONB列
ALTER TABLE sensor_data ADD COLUMN metadata JSONB;
CREATE INDEX sensor_data_metadata_gin_idx
ON sensor_data USING GIN (metadata);
```

### 11.2 查询优化

```sql
-- 1. 始终包含时间范围过滤
-- ✅ 好
SELECT * FROM sensor_data
WHERE time >= NOW() - INTERVAL '1 hour'  -- 分区裁剪
  AND device_id = 123;

-- ❌ 坏
SELECT * FROM sensor_data
WHERE device_id = 123;  -- 扫描所有chunk

-- 2. 使用连续聚合替代重复聚合查询
-- ❌ 坏：每次查询都重新计算
SELECT
    time_bucket('1 hour', time) AS hour,
    AVG(temperature)
FROM sensor_data
WHERE time >= NOW() - INTERVAL '30 days'
GROUP BY hour;

-- ✅ 好：查询预聚合的视图
SELECT * FROM sensor_hourly
WHERE hour >= NOW() - INTERVAL '30 days';

-- 3. 使用EXPLAIN ANALYZE查看执行计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM sensor_data
WHERE time >= NOW() - INTERVAL '1 hour'
  AND device_id = 123;

-- 检查：
-- - Chunks Excluded by Constraint（分区裁剪）
-- - Index Scan vs Seq Scan
-- - Planning Time vs Execution Time
```

### 11.3 批量操作优化

```sql
-- 1. 禁用自动聚合刷新（大批量导入时）
SELECT alter_job(
    (SELECT job_id FROM timescaledb_information.jobs
     WHERE proc_name = 'policy_refresh_continuous_aggregate'),
    scheduled => false
);

-- 2. 批量导入
\COPY sensor_data FROM 'large_file.csv' CSV HEADER;

-- 3. 重新启用自动刷新
SELECT alter_job(
    (SELECT job_id FROM timescaledb_information.jobs
     WHERE proc_name = 'policy_refresh_continuous_aggregate'),
    scheduled => true
);

-- 4. 手动刷新连续聚合
CALL refresh_continuous_aggregate('sensor_hourly', NULL, NULL);
```

### 11.4 监控查询

```sql
-- 查看chunk数量和大小
SELECT
    hypertable_name,
    COUNT(*) AS chunk_count,
    pg_size_pretty(SUM(total_bytes)) AS total_size,
    pg_size_pretty(AVG(total_bytes)) AS avg_chunk_size
FROM timescaledb_information.chunks
GROUP BY hypertable_name;

-- 查看压缩效果
SELECT
    hypertable_name,
    COUNT(*) AS compressed_chunks,
    pg_size_pretty(SUM(before_compression_total_bytes)) AS size_before,
    pg_size_pretty(SUM(after_compression_total_bytes)) AS size_after,
    ROUND(AVG(1 - after_compression_total_bytes::numeric / before_compression_total_bytes) * 100, 2) AS avg_compression_ratio
FROM timescaledb_information.compressed_chunk_stats
GROUP BY hypertable_name;

-- 查看后台任务状态
SELECT * FROM timescaledb_information.jobs;

-- 查看任务执行历史
SELECT * FROM timescaledb_information.job_stats
ORDER BY last_run_started_at DESC;
```

---

## 12. 生产实战案例

### 12.1 案例1：IoT设备监控平台

#### 需求

- 100万+设备
- 每设备每秒1条数据
- 100万 writes/秒
- 保留1年数据
- 实时Dashboard

#### 实现

```sql
-- 1. 核心表设计
CREATE TABLE device_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION,
    tags JSONB
);

SELECT create_hypertable(
    'device_metrics',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    partitioning_column => 'device_id',
    number_partitions => 16  -- 16个空间分区，并行写入
);

-- 2. 索引
CREATE INDEX device_metrics_device_time_idx
ON device_metrics (device_id, time DESC);

CREATE INDEX device_metrics_type_time_idx
ON device_metrics (metric_type, time DESC);

-- 3. 连续聚合（5分钟）
CREATE MATERIALIZED VIEW device_metrics_5min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS bucket,
    device_id,
    metric_type,
    AVG(value) AS avg_value,
    MAX(value) AS max_value,
    MIN(value) AS min_value,
    COUNT(*) AS sample_count
FROM device_metrics
GROUP BY bucket, device_id, metric_type
WITH NO DATA;

SELECT add_continuous_aggregate_policy(
    'device_metrics_5min',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes'
);

-- 4. 压缩策略
ALTER TABLE device_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id, metric_type',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('device_metrics', compress_after => INTERVAL '7 days');

-- 5. 保留策略
SELECT add_retention_policy('device_metrics', drop_after => INTERVAL '1 year');

-- 6. Dashboard查询（实时）
SELECT
    bucket,
    device_id,
    metric_type,
    avg_value,
    max_value
FROM device_metrics_5min
WHERE bucket >= NOW() - INTERVAL '1 hour'
  AND device_id = ANY(ARRAY[123, 456, 789])  -- 用户关注的设备
ORDER BY bucket DESC, device_id, metric_type;
```

### 12.2 案例2：金融市场数据

```sql
-- 高频交易数据（Tick Data）
CREATE TABLE market_ticks (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    price DECIMAL(18, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    bid_price DECIMAL(18, 8),
    ask_price DECIMAL(18, 8)
);

SELECT create_hypertable(
    'market_ticks',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    partitioning_column => 'symbol',
    number_partitions => 32
);

-- K线聚合（1分钟）
CREATE MATERIALIZED VIEW market_klines_1min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS bucket,
    symbol,
    exchange,
    FIRST(price, time) AS open,
    MAX(price) AS high,
    MIN(price) AS low,
    LAST(price, time) AS close,
    SUM(volume) AS volume,
    COUNT(*) AS tick_count
FROM market_ticks
GROUP BY bucket, symbol, exchange;

-- 多级聚合：5分钟、15分钟、1小时、1天
CREATE MATERIALIZED VIEW market_klines_5min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', bucket) AS bucket,
    symbol,
    exchange,
    FIRST(open, bucket) AS open,
    MAX(high) AS high,
    MIN(low) AS low,
    LAST(close, bucket) AS close,
    SUM(volume) AS volume
FROM market_klines_1min
GROUP BY bucket, symbol, exchange;

-- 查询：获取BTC-USD的最近24小时1小时K线
SELECT * FROM market_klines_1hour
WHERE symbol = 'BTC-USD'
  AND bucket >= NOW() - INTERVAL '24 hours'
ORDER BY bucket DESC;
```

### 12.3 案例3：APM（应用性能监控）

```sql
-- HTTP请求追踪
CREATE TABLE http_requests (
    time TIMESTAMPTZ NOT NULL,
    request_id UUID NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INT NOT NULL,
    duration_ms DOUBLE PRECISION NOT NULL,
    user_id BIGINT,
    ip_address INET,
    user_agent TEXT,
    tags JSONB
);

SELECT create_hypertable('http_requests', 'time', chunk_time_interval => INTERVAL '6 hours');

CREATE INDEX http_requests_service_time_idx ON http_requests (service_name, time DESC);
CREATE INDEX http_requests_endpoint_time_idx ON http_requests (endpoint, time DESC);
CREATE INDEX http_requests_tags_gin_idx ON http_requests USING GIN (tags);

-- 性能分析聚合
CREATE MATERIALIZED VIEW http_requests_stats_5min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS bucket,
    service_name,
    endpoint,
    method,
    COUNT(*) AS request_count,
    COUNT(*) FILTER (WHERE status_code >= 500) AS error_count,
    AVG(duration_ms) AS avg_duration,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_duration,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY duration_ms) AS p99_duration,
    MAX(duration_ms) AS max_duration
FROM http_requests
GROUP BY bucket, service_name, endpoint, method;

-- Dashboard查询：服务健康度
SELECT
    service_name,
    SUM(request_count) AS total_requests,
    SUM(error_count) AS total_errors,
    ROUND(100.0 * SUM(error_count) / SUM(request_count), 2) AS error_rate,
    ROUND(AVG(avg_duration), 2) AS avg_latency,
    ROUND(AVG(p95_duration), 2) AS p95_latency
FROM http_requests_stats_5min
WHERE bucket >= NOW() - INTERVAL '1 hour'
GROUP BY service_name
ORDER BY error_rate DESC, avg_latency DESC;
```

---

## 13. 最佳实践

### 13.1 设计原则

#### ✅ 推荐做法

1. **时间列使用TIMESTAMPTZ**

    ```sql
    -- ✅ 好：带时区
    CREATE TABLE metrics (
        time TIMESTAMPTZ NOT NULL,
        ...
    );

    -- ❌ 坏：不带时区
    CREATE TABLE metrics (
        time TIMESTAMP NOT NULL,  -- 可能导致时区混乱
        ...
    );
    ```

2. **合理选择chunk间隔**

    ```text
    数据量     |  建议chunk间隔
    -------------------------------
    < 100GB   |  7 days
    100GB-1TB |  1 day
    1TB-10TB  |  6 hours
    > 10TB    |  1 hour

    原则：每个chunk 100MB-1GB最佳
    ```

3. **空间分区用于高并发写入**

    ```sql
    -- 单一时间分区：写入热点在最新chunk
    SELECT create_hypertable('metrics', 'time');

    -- 多维分区：分散写入到多个chunk
    SELECT create_hypertable(
        'metrics',
        'time',
        partitioning_column => 'device_id',
        number_partitions => 4  -- 4个并发写入点
    );
    ```

4. **使用连续聚合替代重复查询**

5. **启用压缩节省存储**

6. **配置保留策略自动清理**

### 13.2 运维Checklist

- [ ] 监控chunk数量（过多影响性能）
- [ ] 监控压缩任务执行状态
- [ ] 监控连续聚合刷新延迟
- [ ] 定期VACUUM ANALYZE（尤其是未压缩的chunk）
- [ ] 监控磁盘使用
- [ ] 测试备份恢复流程
- [ ] 监控后台任务失败（timescaledb_information.job_stats）

### 13.3 性能调优Checklist

- [ ] chunk间隔适当（不要太小或太大）
- [ ] 查询包含时间范围过滤
- [ ] 使用连续聚合预聚合
- [ ] 启用压缩
- [ ] 多维分区用于高并发写入
- [ ] 索引策略合理
- [ ] 批量写入而非逐行插入
- [ ] PostgreSQL参数调优（shared_buffers, work_mem等）

---

## 14. FAQ与疑难解答

### Q1: Hypertable vs PostgreSQL分区表？

| 特性 | Hypertable | PostgreSQL分区 |
|------|-----------|----------------|
| **自动分区** | ✅ 自动创建 | ❌ 手动创建 |
| **压缩** | ✅ 内置 | ❌ 需手动 |
| **保留策略** | ✅ 自动 | ❌ 需脚本 |
| **连续聚合** | ✅ 内置 | ❌ 需手动维护物化视图 |
| **时序函数** | ✅ 丰富 | ❌ 无 |
| **学习成本** | 低 | 中 |

### Q2: chunk数量过多怎么办？

```sql
-- 诊断：查看chunk数量
SELECT COUNT(*) FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_data';

-- 如果超过1000个chunk，考虑：
-- 1. 增大chunk间隔
SELECT set_chunk_time_interval('sensor_data', INTERVAL '7 days');

-- 2. 启用压缩（减少chunk数量）
ALTER TABLE sensor_data SET (timescaledb.compress);
SELECT add_compression_policy('sensor_data', compress_after => INTERVAL '7 days');

-- 3. 删除旧数据
SELECT add_retention_policy('sensor_data', drop_after => INTERVAL '180 days');
```

### Q3: 压缩后能更新数据吗？

```sql
-- ❌ 不能直接更新压缩chunk
UPDATE sensor_data SET temperature = 25.0
WHERE time = '2025-01-01 10:00:00';
-- ERROR: cannot update compressed chunk

-- 解决方案1：解压chunk
SELECT decompress_chunk('_timescaledb_internal._hyper_1_1_chunk');
-- 执行更新
UPDATE sensor_data SET temperature = 25.0 WHERE ...;
-- 重新压缩
SELECT compress_chunk('_timescaledb_internal._hyper_1_1_chunk');

-- 解决方案2：设计避免更新
-- 时序数据应该是只追加的，避免更新
```

### Q4: 如何迁移现有PostgreSQL时序数据到TimescaleDB？

```sql
-- 步骤1：安装TimescaleDB扩展
CREATE EXTENSION timescaledb;

-- 步骤2：保留原表结构，创建新Hypertable
ALTER TABLE sensor_data RENAME TO sensor_data_old;

CREATE TABLE sensor_data (LIKE sensor_data_old INCLUDING ALL);

SELECT create_hypertable('sensor_data', 'time',
    chunk_time_interval => INTERVAL '1 day',
    migrate_data => false
);

-- 步骤3：迁移数据
INSERT INTO sensor_data SELECT * FROM sensor_data_old;

-- 步骤4：验证
SELECT COUNT(*) FROM sensor_data;
SELECT COUNT(*) FROM sensor_data_old;

-- 步骤5：删除旧表
DROP TABLE sensor_data_old;
```

### Q5: TimescaleDB可以用于非时序数据吗？

**A**: 可以，但不推荐。

- Hypertable仍然是PostgreSQL表，可以存储任何数据
- 但TimescaleDB优化是针对时序数据的（时间分区、压缩等）
- 如果数据不是时序的，使用普通PostgreSQL表更合适

---

## 📚 延伸阅读

### 官方资源

- [TimescaleDB Documentation](https://docs.timescale.com/)
- [TimescaleDB GitHub](https://github.com/timescale/timescaledb)
- [Timescale Cloud](https://www.timescale.com/cloud)

### 相关技术

- **InfluxDB**: 纯时序数据库
- **Prometheus**: Metrics监控系统
- **ClickHouse**: OLAP分析数据库
- **Grafana**: 可视化Dashboard

### 推荐阅读

- [Time-Series Data: Why and How to Use a Relational Database](https://blog.timescale.com/)
- [PostgreSQL Partitioning Best Practices](https://www.postgresql.org/docs/current/ddl-partitioning.html)

---

## ✅ 学习检查清单

- [ ] 理解时序数据特征和挑战
- [ ] 掌握Hypertable创建和管理
- [ ] 熟练使用time_bucket和时序函数
- [ ] 理解连续聚合原理和使用
- [ ] 掌握数据压缩和保留策略
- [ ] 能够设计高性能时序数据架构
- [ ] 熟悉性能优化技巧
- [ ] 能够监控和运维生产环境

---

## 💡 下一步学习

1. **进阶主题**:
   - TimescaleDB多节点（分布式）
   - 与Grafana/Prometheus集成
   - 实时流处理（Kafka + TimescaleDB）

2. **相关课程**:
   - [Citus分布式PostgreSQL](./【深入】Citus分布式PostgreSQL完整实战指南.md)
   - [PostgreSQL性能调优](../11-性能调优/)
   - [PostGIS空间数据库](./【深入】PostGIS空间数据库完整实战指南.md)

---

**文档维护**: 本文档持续更新以反映TimescaleDB最新特性。
**反馈**: 如发现错误或有改进建议，请提交issue。

**版本历史**:

- v1.0 (2025-01): 初始版本，覆盖TimescaleDB 2.13+核心特性
