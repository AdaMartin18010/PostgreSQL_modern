# TimescaleDB 时序数据库扩展

> 版本对标（更新于 2025-10）  
> TimescaleDB 2.14+ | PostgreSQL 17

## 📋 主题边界

基于 PostgreSQL 的专业时序数据库扩展，提供高性能的时序数据存储、查询和管理能力：

- **Hypertable**：自动分区的时序表
- **压缩**：列式压缩降低存储成本
- **连续聚合**：实时物化视图
- **数据保留**：自动化 TTL 策略
- **分布式**：多节点扩展（企业版）

---

## 🎯 核心概念

### 1. Hypertable（超表）

Hypertable 是 TimescaleDB 的核心抽象，自动将时序数据按时间（和可选的空间维度）分区为 Chunks。

```sql
-- 创建普通表
CREATE TABLE sensor_data (
    time        TIMESTAMPTZ NOT NULL,
    sensor_id   INT NOT NULL,
    temperature DOUBLE PRECISION,
    humidity    DOUBLE PRECISION
);

-- 转换为Hypertable
SELECT create_hypertable('sensor_data', 'time');

-- 带空间分区的Hypertable（按sensor_id分区）
SELECT create_hypertable('sensor_data', 'time',
    partitioning_column => 'sensor_id',
    number_partitions => 4
);
```

**Chunk 策略**：

```sql
-- 查看Chunks
SELECT * FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_data';

-- 调整Chunk时间间隔（默认7天）
SELECT set_chunk_time_interval('sensor_data', INTERVAL '1 day');

-- 手动Reorder Chunk（按特定列排序，提高查询性能）
SELECT add_reorder_policy('sensor_data', 'sensor_data_time_idx');
```

### 2. 压缩（Compression）

列式压缩可以显著降低存储成本（压缩比通常达到 10-20 倍）。

```sql
-- 启用压缩
ALTER TABLE sensor_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id',  -- 分段键
    timescaledb.compress_orderby = 'time DESC'     -- 排序键
);

-- 添加压缩策略（自动压缩7天前的数据）
SELECT add_compression_policy('sensor_data', INTERVAL '7 days');

-- 手动压缩特定Chunk
SELECT compress_chunk(i) FROM show_chunks('sensor_data', older_than => INTERVAL '7 days') i;

-- 查看压缩状态
SELECT
    chunk_schema,
    chunk_name,
    pg_size_pretty(before_compression_total_bytes) as before,
    pg_size_pretty(after_compression_total_bytes) as after,
    ROUND(100 - (after_compression_total_bytes::numeric /
                 before_compression_total_bytes::numeric * 100), 2) as compression_ratio
FROM chunk_compression_stats('sensor_data');
```

### 3. 连续聚合（Continuous Aggregates）

实时物化视图，自动增量刷新预聚合数据。

```sql
-- 创建连续聚合：每小时平均温度
CREATE MATERIALIZED VIEW sensor_data_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    sensor_id,
    AVG(temperature) as avg_temp,
    MAX(temperature) as max_temp,
    MIN(temperature) as min_temp,
    COUNT(*) as readings
FROM sensor_data
GROUP BY bucket, sensor_id;

-- 添加刷新策略（每小时刷新，延迟1小时）
SELECT add_continuous_aggregate_policy('sensor_data_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

-- 手动刷新
CALL refresh_continuous_aggregate('sensor_data_hourly',
    '2025-01-01', '2025-01-02'
);

-- 查询连续聚合（自动使用物化数据）
SELECT * FROM sensor_data_hourly
WHERE bucket >= NOW() - INTERVAL '24 hours'
ORDER BY bucket DESC;
```

### 4. 数据保留策略（Retention Policy）

自动删除过期数据，控制存储成本。

```sql
-- 添加保留策略（删除90天前的数据）
SELECT add_retention_policy('sensor_data', INTERVAL '90 days');

-- 删除保留策略
SELECT remove_retention_policy('sensor_data');

-- 手动删除旧Chunks
SELECT drop_chunks('sensor_data', older_than => INTERVAL '180 days');

-- 查看保留策略
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_retention';
```

---

## 🚀 完整示例：IoT 传感器监控系统

### 场景设计

- 10,000 个传感器
- 每个传感器每分钟上报一次数据
- 保留 90 天数据
- 需要实时查询最近数据和历史聚合

### 1. 表结构设计

```sql
-- 创建Schema
CREATE SCHEMA IF NOT EXISTS iot;

-- 原始数据表
CREATE TABLE iot.sensor_readings (
    time        TIMESTAMPTZ NOT NULL,
    sensor_id   INT NOT NULL,
    location    TEXT,
    temperature DOUBLE PRECISION,
    humidity    DOUBLE PRECISION,
    pressure    DOUBLE PRECISION,
    battery     SMALLINT,
    status      TEXT
);

-- 转换为Hypertable（每天一个Chunk）
SELECT create_hypertable('iot.sensor_readings', 'time',
    chunk_time_interval => INTERVAL '1 day'
);

-- 创建索引
CREATE INDEX idx_sensor_id ON iot.sensor_readings (sensor_id, time DESC);
CREATE INDEX idx_location ON iot.sensor_readings (location, time DESC);
```

### 2. 配置压缩

```sql
-- 启用压缩（按sensor_id分段）
ALTER TABLE iot.sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id, location',
    timescaledb.compress_orderby = 'time DESC'
);

-- 自动压缩3天前的数据
SELECT add_compression_policy('iot.sensor_readings', INTERVAL '3 days');
```

### 3. 创建连续聚合

```sql
-- 每5分钟聚合
CREATE MATERIALIZED VIEW iot.sensor_readings_5min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS bucket,
    sensor_id,
    location,
    AVG(temperature) as avg_temp,
    MAX(temperature) as max_temp,
    MIN(temperature) as min_temp,
    AVG(humidity) as avg_humidity,
    COUNT(*) as reading_count
FROM iot.sensor_readings
GROUP BY bucket, sensor_id, location;

-- 每小时聚合
CREATE MATERIALIZED VIEW iot.sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    sensor_id,
    location,
    AVG(temperature) as avg_temp,
    STDDEV(temperature) as stddev_temp,
    MAX(temperature) as max_temp,
    MIN(temperature) as min_temp,
    AVG(humidity) as avg_humidity,
    COUNT(*) as reading_count
FROM iot.sensor_readings
GROUP BY bucket, sensor_id, location;

-- 每天聚合
CREATE MATERIALIZED VIEW iot.sensor_readings_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    sensor_id,
    location,
    AVG(temperature) as avg_temp,
    MAX(temperature) as max_temp,
    MIN(temperature) as min_temp,
    AVG(humidity) as avg_humidity,
    SUM(reading_count) as total_readings
FROM iot.sensor_readings_hourly
GROUP BY bucket, sensor_id, location;

-- 配置刷新策略
SELECT add_continuous_aggregate_policy('iot.sensor_readings_5min',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes'
);

SELECT add_continuous_aggregate_policy('iot.sensor_readings_hourly',
    start_offset => INTERVAL '4 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

SELECT add_continuous_aggregate_policy('iot.sensor_readings_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day'
);
```

### 4. 配置数据保留

```sql
-- 原始数据保留90天
SELECT add_retention_policy('iot.sensor_readings', INTERVAL '90 days');

-- 5分钟聚合保留30天
SELECT add_retention_policy('iot.sensor_readings_5min', INTERVAL '30 days');

-- 小时聚合保留1年
SELECT add_retention_policy('iot.sensor_readings_hourly', INTERVAL '365 days');

-- 日聚合永久保留（不设置策略）
```

### 5. 常用查询

```sql
-- 1. 最近24小时的原始数据
SELECT * FROM iot.sensor_readings
WHERE time >= NOW() - INTERVAL '24 hours'
  AND sensor_id = 100
ORDER BY time DESC;

-- 2. 最近7天的小时级趋势
SELECT
    bucket,
    avg_temp,
    avg_humidity
FROM iot.sensor_readings_hourly
WHERE bucket >= NOW() - INTERVAL '7 days'
  AND sensor_id = 100
ORDER BY bucket;

-- 3. 异常检测（温度超过阈值）
SELECT
    bucket,
    sensor_id,
    location,
    max_temp
FROM iot.sensor_readings_5min
WHERE bucket >= NOW() - INTERVAL '1 hour'
  AND max_temp > 35.0
ORDER BY bucket DESC;

-- 4. 多传感器对比
SELECT
    bucket,
    sensor_id,
    avg_temp
FROM iot.sensor_readings_hourly
WHERE bucket >= NOW() - INTERVAL '24 hours'
  AND sensor_id IN (100, 101, 102)
ORDER BY bucket, sensor_id;

-- 5. 按位置聚合
SELECT
    location,
    AVG(avg_temp) as avg_temp,
    COUNT(DISTINCT sensor_id) as sensor_count
FROM iot.sensor_readings_daily
WHERE bucket >= NOW() - INTERVAL '30 days'
GROUP BY location
ORDER BY avg_temp DESC;
```

---

## 📊 性能优化

### 写入优化

```sql
-- 批量写入（推荐）
COPY iot.sensor_readings (time, sensor_id, location, temperature, humidity)
FROM '/path/to/data.csv' CSV;

-- 或使用事务批量INSERT
BEGIN;
INSERT INTO iot.sensor_readings VALUES
    ('2025-01-01 00:00:00', 1, 'room_a', 22.5, 45.2, 1013.2, 95, 'ok'),
    ('2025-01-01 00:01:00', 1, 'room_a', 22.6, 45.1, 1013.3, 95, 'ok'),
    -- ... 批量数据
COMMIT;

-- 调整参数
SET timescaledb.max_insert_batch_size = 1000;  -- 插入批次大小
```

### 查询优化

```sql
-- 1. 使用合适的时间范围过滤
-- 好：利用时间分区
SELECT * FROM iot.sensor_readings
WHERE time >= '2025-01-01' AND time < '2025-01-02';

-- 避免：全表扫描
SELECT * FROM iot.sensor_readings WHERE sensor_id = 100;  -- 缺少时间过滤

-- 2. 利用连续聚合
-- 好：查询聚合视图
SELECT * FROM iot.sensor_readings_hourly
WHERE bucket >= NOW() - INTERVAL '30 days';

-- 避免：实时聚合大量数据
SELECT time_bucket('1 hour', time), AVG(temperature)
FROM iot.sensor_readings
WHERE time >= NOW() - INTERVAL '30 days'
GROUP BY 1;

-- 3. 启用并行查询
SET max_parallel_workers_per_gather = 4;
```

### 维护任务

```sql
-- 查看所有后台任务
SELECT * FROM timescaledb_information.jobs;

-- 查看任务统计
SELECT * FROM timescaledb_information.job_stats;

-- 手动触发任务
CALL run_job(1000);  -- 使用job_id

-- 暂停/恢复任务
SELECT alter_job(1000, scheduled => false);  -- 暂停
SELECT alter_job(1000, scheduled => true);   -- 恢复
```

---

## 📈 监控指标

### 关键指标

```sql
-- 1. Hypertable大小
SELECT
    hypertable_name,
    pg_size_pretty(hypertable_size(format('%I.%I', hypertable_schema, hypertable_name)::regclass)) as size
FROM timescaledb_information.hypertables;

-- 2. Chunk数量和大小
SELECT
    hypertable_name,
    COUNT(*) as chunk_count,
    pg_size_pretty(SUM(total_bytes)) as total_size
FROM timescaledb_information.chunks
GROUP BY hypertable_name;

-- 3. 压缩效果
SELECT
    hypertable_name,
    compression_status,
    pg_size_pretty(uncompressed_total_bytes) as uncompressed,
    pg_size_pretty(compressed_total_bytes) as compressed,
    ROUND(100 - (compressed_total_bytes::numeric / uncompressed_total_bytes::numeric * 100), 2) as ratio
FROM timescaledb_information.compression_settings cs
JOIN timescaledb_information.hypertables h ON cs.hypertable_name = h.hypertable_name;

-- 4. 连续聚合刷新延迟
SELECT
    view_name,
    completed_threshold,
    NOW() - completed_threshold as lag
FROM timescaledb_information.continuous_aggregates;
```

---

## ⚠️ 最佳实践

### 1. 设计原则

- ✅ **时间列索引**：Hypertable 自动按时间分区，确保时间列为 NOT NULL
- ✅ **选择合适的 Chunk 大小**：通常 1 天-1 周，根据数据量调整
- ✅ **合理使用空间分区**：高基数列（如设备 ID）适合作为空间分区键
- ✅ **延迟压缩**：保留近期热数据为行式存储，压缩历史数据

### 2. 压缩策略

- ✅ **segmentby 选择**：选择查询常用的过滤列（如 sensor_id）
- ✅ **orderby 选择**：选择范围查询列（通常是 time DESC）
- ✅ **压缩延迟**：根据查询模式，通常延迟 1-7 天
- ⚠️ **压缩后限制**：压缩 Chunk 不支持 UPDATE/DELETE

### 3. 连续聚合

- ✅ **分层聚合**：5 分钟 → 1 小时 → 1 天，逐级聚合
- ✅ **适当延迟**：end_offset 留出数据延迟缓冲
- ✅ **索引优化**：为连续聚合视图创建索引
- ⚠️ **避免过度聚合**：不要创建太多不常用的聚合

### 4. 运维建议

- 📊 **监控磁盘空间**：定期检查 Chunk 大小和压缩比
- 🔧 **定期 VACUUM**：压缩和删除操作后执行 VACUUM
- 📈 **性能测试**：在生产环境前充分测试写入和查询性能
- 🔄 **版本升级**：关注 TimescaleDB 更新，及时升级

---

## 📚 参考资源

### 官方文档

- **官方文档**：<https://docs.timescale.com/>
- **GitHub**：<https://github.com/timescale/timescaledb>
- **最佳实践**：<https://docs.timescale.com/timescaledb/latest/how-to-guides/>

### 示例脚本

- `continuous_aggregate_example.sql` - 连续聚合完整示例
- `../../10_benchmarks/` - 性能基准测试

### 相关章节

- `../README.md` - 时序数据总览
- `../../04_modern_features/` - PostgreSQL 现代特性
- `../../09_deployment_ops/` - 部署运维指南

---

## 🎯 评测要点

### 性能指标

| 指标     | 说明             | 目标值           |
| -------- | ---------------- | ---------------- |
| 写入吞吐 | 每秒插入行数     | 100K+ rows/s     |
| 查询延迟 | P95 查询延迟     | <100ms（热数据） |
| 压缩比   | 压缩后/压缩前    | 10-20x           |
| 聚合延迟 | 连续聚合刷新延迟 | <5min            |
| 存储效率 | 单 GB 存储数据量 | 根据压缩比       |

### 测试场景

- **批量写入**：使用 COPY 批量导入历史数据
- **乱序写入**：模拟延迟到达的数据
- **时间范围查询**：查询最近 N 天/小时数据
- **聚合查询**：窗口函数、GROUP BY
- **高并发**：多客户端同时读写

---

**版本兼容性**：

- PostgreSQL 12-17
- TimescaleDB 2.x 推荐使用 2.14+
- 关注 PostgreSQL 17 新特性集成
