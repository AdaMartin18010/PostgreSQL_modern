# 时序数据管理实战案例 — TimescaleDB Time-Series Database

> **版本对标**：PostgreSQL 17 + TimescaleDB 2.13+（更新于 2025-10）  
> **难度等级**：⭐⭐⭐⭐ 高级  
> **预计时间**：60-90 分钟  
> **适合场景**：IoT 数据、监控指标、金融行情、日志分析

---

## 📋 案例目标

构建一个生产级的时序数据库系统，包括：

1. ✅ TimescaleDB 超表（Hypertable）设计
2. ✅ 高频数据写入优化（10K+ TPS）
3. ✅ 连续聚合（Continuous Aggregate）
4. ✅ 数据压缩与保留策略
5. ✅ 时序查询优化

---

## 🎯 业务场景

**场景描述**：IoT 设备监控数据采集与分析

- **数据来源**：
  - 10,000 个 IoT 设备
  - 每个设备每 10 秒上报一次数据
  - 指标包括：温度、湿度、电量、状态
- **数据量**：
  - 每秒 1,000 条数据
  - 每天 8,640 万条数据
  - 每月约 26 亿条数据
- **查询需求**：
  - 实时监控（最近 1 小时数据）
  - 历史趋势分析（按小时/天/月聚合）
  - 异常检测（超出阈值告警）
  - 设备健康分析

---

## 🏗️ 架构设计

```text
IoT设备 (10K个)
    ↓ 每10秒上报
数据采集层
    ↓ 批量写入
TimescaleDB超表 (按时间自动分区)
    ↓
连续聚合视图 (1分钟/1小时/1天)
    ↓
压缩策略 (7天后压缩)
    ↓
保留策略 (90天后删除)
```

---

## 📦 1. 环境准备

### 1.1 安装 TimescaleDB

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-17-timescaledb

# 或使用Docker
docker run -d --name timescaledb \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  timescale/timescaledb:latest-pg17
```

### 1.2 启用 TimescaleDB 扩展

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 验证版本
SELECT default_version, installed_version
FROM pg_available_extensions
WHERE name = 'timescaledb';
```

---

## 🗄️ 2. 数据模型设计

### 2.1 创建普通表并转换为超表

```sql
-- 创建IoT数据表
CREATE TABLE iot_sensor_data (
    time timestamptz NOT NULL,
    device_id int NOT NULL,
    temperature double precision,
    humidity double precision,
    battery_level int,
    status text,
    metadata jsonb
);

-- 转换为超表（按时间分区）
SELECT create_hypertable(
    'iot_sensor_data',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- 创建索引
CREATE INDEX idx_iot_device_time ON iot_sensor_data (device_id, time DESC);
CREATE INDEX idx_iot_status ON iot_sensor_data (status, time DESC)
    WHERE status != 'normal';

-- 添加约束
ALTER TABLE iot_sensor_data
    ADD CONSTRAINT iot_battery_level_check
    CHECK (battery_level BETWEEN 0 AND 100);
```

### 2.2 创建设备信息表

```sql
-- 设备元数据表
CREATE TABLE iot_devices (
    device_id int PRIMARY KEY,
    device_name text NOT NULL,
    device_type text NOT NULL,
    location text,
    installed_at timestamptz DEFAULT now()
);

-- 插入测试设备
INSERT INTO iot_devices (device_id, device_name, device_type, location)
SELECT
    i,
    'Device-' || i,
    (ARRAY['temperature_sensor', 'humidity_sensor', 'combo_sensor'])[1 + (i % 3)],
    (ARRAY['Floor-1', 'Floor-2', 'Floor-3', 'Warehouse'])[1 + (i % 4)]
FROM generate_series(1, 10000) i;
```

---

## 📝 3. 高频数据写入

### 3.1 批量插入测试数据

```sql
-- 插入最近7天的模拟数据（约6000万条）
INSERT INTO iot_sensor_data (time, device_id, temperature, humidity, battery_level, status, metadata)
SELECT
    now() - (random() * interval '7 days'),
    (random() * 10000)::int + 1,
    20 + (random() * 15)::numeric(4,2),  -- 温度20-35°C
    40 + (random() * 40)::numeric(4,2),  -- 湿度40-80%
    50 + (random() * 50)::int,           -- 电量50-100%
    (ARRAY['normal', 'warning', 'error'])[1 + (random() * 2.5)::int],
    jsonb_build_object(
        'firmware_version', '1.0.' || (random() * 10)::int,
        'signal_strength', -50 - (random() * 50)::int
    )
FROM generate_series(1, 60000000) i;

-- 查看数据量和表大小
SELECT
    COUNT(*) AS total_rows,
    pg_size_pretty(pg_total_relation_size('iot_sensor_data')) AS total_size
FROM iot_sensor_data;
```

### 3.2 查看超表 chunks

```sql
-- 查看时间分区（chunks）
SELECT
    chunk_schema,
    chunk_name,
    range_start,
    range_end,
    pg_size_pretty(total_bytes) AS chunk_size
FROM timescaledb_information.chunks
WHERE hypertable_name = 'iot_sensor_data'
ORDER BY range_start DESC
LIMIT 10;
```

---

## 🔍 4. 时序查询

### 4.1 基本时序查询

```sql
-- 查询最近1小时的数据
SELECT
    time_bucket('5 minutes', time) AS bucket,
    device_id,
    AVG(temperature) AS avg_temp,
    AVG(humidity) AS avg_humidity,
    MIN(battery_level) AS min_battery
FROM iot_sensor_data
WHERE time > now() - interval '1 hour'
GROUP BY bucket, device_id
ORDER BY bucket DESC, device_id
LIMIT 100;

-- 查询特定设备的历史趋势
SELECT
    time_bucket('1 hour', time) AS hour,
    COUNT(*) AS data_points,
    AVG(temperature) AS avg_temp,
    MIN(temperature) AS min_temp,
    MAX(temperature) AS max_temp,
    STDDEV(temperature) AS stddev_temp
FROM iot_sensor_data
WHERE device_id = 1
  AND time > now() - interval '7 days'
GROUP BY hour
ORDER BY hour DESC;
```

### 4.2 窗口函数与移动平均

```sql
-- 计算移动平均（5分钟窗口）
SELECT
    time,
    device_id,
    temperature,
    AVG(temperature) OVER (
        PARTITION BY device_id
        ORDER BY time
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS moving_avg_5
FROM iot_sensor_data
WHERE device_id = 1
  AND time > now() - interval '1 day'
ORDER BY time DESC
LIMIT 100;
```

---

## 📊 5. 连续聚合（Continuous Aggregates）

### 5.1 创建 1 分钟聚合视图

```sql
-- 创建连续聚合视图（每分钟）
CREATE MATERIALIZED VIEW iot_sensor_data_1min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS bucket,
    device_id,
    COUNT(*) AS data_points,
    AVG(temperature) AS avg_temperature,
    MIN(temperature) AS min_temperature,
    MAX(temperature) AS max_temperature,
    AVG(humidity) AS avg_humidity,
    AVG(battery_level) AS avg_battery
FROM iot_sensor_data
GROUP BY bucket, device_id;

-- 添加刷新策略（实时更新）
SELECT add_continuous_aggregate_policy(
    'iot_sensor_data_1min',
    start_offset => INTERVAL '2 minutes',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute'
);

-- 创建索引
CREATE INDEX idx_iot_1min_device_time
    ON iot_sensor_data_1min (device_id, bucket DESC);
```

### 5.2 创建 1 小时聚合视图

```sql
-- 创建连续聚合视图（每小时）
CREATE MATERIALIZED VIEW iot_sensor_data_1hour
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    COUNT(*) AS data_points,
    AVG(temperature) AS avg_temperature,
    MIN(temperature) AS min_temperature,
    MAX(temperature) AS max_temperature,
    AVG(humidity) AS avg_humidity,
    AVG(battery_level) AS avg_battery
FROM iot_sensor_data
GROUP BY bucket, device_id;

-- 添加刷新策略
SELECT add_continuous_aggregate_policy(
    'iot_sensor_data_1hour',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);
```

### 5.3 查询连续聚合视图

```sql
-- 查询每小时聚合数据（非常快）
SELECT
    bucket,
    COUNT(DISTINCT device_id) AS active_devices,
    AVG(avg_temperature) AS overall_avg_temp,
    SUM(data_points) AS total_data_points
FROM iot_sensor_data_1hour
WHERE bucket > now() - interval '24 hours'
GROUP BY bucket
ORDER BY bucket DESC;

-- 对比原始查询和聚合查询的性能
\timing on
-- 原始查询
SELECT time_bucket('1 hour', time) AS hour, AVG(temperature)
FROM iot_sensor_data
WHERE time > now() - interval '7 days'
GROUP BY hour;

-- 聚合查询（快得多）
SELECT bucket, AVG(avg_temperature)
FROM iot_sensor_data_1hour
WHERE bucket > now() - interval '7 days'
GROUP BY bucket;
\timing off
```

---

## 🗜️ 6. 数据压缩

### 6.1 启用自动压缩

```sql
-- 添加压缩策略（7天后压缩）
ALTER TABLE iot_sensor_data
SET (timescaledb.compress,
     timescaledb.compress_segmentby = 'device_id',
     timescaledb.compress_orderby = 'time DESC');

-- 添加压缩策略
SELECT add_compression_policy(
    'iot_sensor_data',
    INTERVAL '7 days'
);

-- 查看压缩策略
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_compression';
```

### 6.2 手动压缩与解压缩

```sql
-- 手动压缩特定chunk
SELECT compress_chunk(i)
FROM show_chunks('iot_sensor_data', older_than => INTERVAL '7 days') i;

-- 查看压缩效果
SELECT
    pg_size_pretty(before_compression_total_bytes) AS before_compression,
    pg_size_pretty(after_compression_total_bytes) AS after_compression,
    round(100.0 * (before_compression_total_bytes - after_compression_total_bytes)
          / before_compression_total_bytes, 2) AS compression_ratio
FROM timescaledb_information.compression_settings
WHERE hypertable_name = 'iot_sensor_data';

-- 解压缩（如需修改数据）
SELECT decompress_chunk(i)
FROM show_chunks('iot_sensor_data') i
WHERE is_compressed = true
LIMIT 1;
```

---

## 🗑️ 7. 数据保留策略

### 7.1 自动删除历史数据

```sql
-- 添加保留策略（保留90天数据）
SELECT add_retention_policy(
    'iot_sensor_data',
    INTERVAL '90 days'
);

-- 查看保留策略
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_retention';

-- 手动删除旧数据
SELECT drop_chunks(
    'iot_sensor_data',
    older_than => INTERVAL '90 days'
);
```

---

## 📈 8. 性能优化

### 8.1 查询性能分析

```sql
-- 分析查询计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    time_bucket('1 hour', time) AS hour,
    device_id,
    AVG(temperature) AS avg_temp
FROM iot_sensor_data
WHERE time > now() - interval '7 days'
  AND device_id IN (1, 2, 3, 4, 5)
GROUP BY hour, device_id
ORDER BY hour DESC;

-- 查看chunk排除（chunk exclusion）
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM iot_sensor_data
WHERE time BETWEEN '2025-10-01' AND '2025-10-02';
```

### 8.2 并行查询优化

```sql
-- 启用并行查询
SET max_parallel_workers_per_gather = 4;

-- 并行聚合查询
SELECT
    device_id,
    COUNT(*) AS data_points,
    AVG(temperature) AS avg_temp
FROM iot_sensor_data
WHERE time > now() - interval '30 days'
GROUP BY device_id;
```

---

## 🔔 9. 实时告警

### 9.1 异常检测查询

```sql
-- 创建异常检测视图
CREATE OR REPLACE VIEW device_anomalies AS
SELECT
    device_id,
    time,
    temperature,
    humidity,
    battery_level,
    CASE
        WHEN temperature > 35 THEN 'High Temperature'
        WHEN temperature < 15 THEN 'Low Temperature'
        WHEN humidity > 85 THEN 'High Humidity'
        WHEN humidity < 30 THEN 'Low Humidity'
        WHEN battery_level < 20 THEN 'Low Battery'
        ELSE 'Normal'
    END AS anomaly_type
FROM iot_sensor_data
WHERE time > now() - interval '1 hour'
  AND (
    temperature NOT BETWEEN 15 AND 35
    OR humidity NOT BETWEEN 30 AND 85
    OR battery_level < 20
  );

-- 查询当前异常
SELECT
    anomaly_type,
    COUNT(DISTINCT device_id) AS affected_devices,
    COUNT(*) AS anomaly_count
FROM device_anomalies
GROUP BY anomaly_type
ORDER BY anomaly_count DESC;
```

### 9.2 触发器告警（示例）

```sql
-- 创建告警表
CREATE TABLE device_alerts (
    id serial PRIMARY KEY,
    device_id int NOT NULL,
    alert_type text NOT NULL,
    alert_message text,
    alert_time timestamptz DEFAULT now()
);

-- 创建告警触发器函数
CREATE OR REPLACE FUNCTION check_sensor_thresholds()
RETURNS trigger AS $$
BEGIN
    IF NEW.temperature > 35 THEN
        INSERT INTO device_alerts (device_id, alert_type, alert_message)
        VALUES (NEW.device_id, 'HIGH_TEMP',
                'Temperature exceeded 35°C: ' || NEW.temperature);
    END IF;

    IF NEW.battery_level < 20 THEN
        INSERT INTO device_alerts (device_id, alert_type, alert_message)
        VALUES (NEW.device_id, 'LOW_BATTERY',
                'Battery level below 20%: ' || NEW.battery_level);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 注意：生产环境中，高频写入场景不建议使用触发器
-- 建议使用定时任务或流处理框架
```

---

## ✅ 10. 完整监控查询

```sql
-- 综合监控仪表板查询
WITH device_stats AS (
    SELECT
        device_id,
        COUNT(*) AS data_points,
        AVG(temperature) AS avg_temp,
        AVG(humidity) AS avg_humidity,
        AVG(battery_level) AS avg_battery,
        MAX(time) AS last_seen
    FROM iot_sensor_data
    WHERE time > now() - interval '1 hour'
    GROUP BY device_id
),
device_health AS (
    SELECT
        device_id,
        CASE
            WHEN MAX(time) < now() - interval '5 minutes' THEN 'Offline'
            WHEN AVG(battery_level) < 20 THEN 'Low Battery'
            WHEN AVG(temperature) NOT BETWEEN 15 AND 35 THEN 'Temperature Warning'
            ELSE 'Healthy'
        END AS health_status
    FROM iot_sensor_data
    WHERE time > now() - interval '1 hour'
    GROUP BY device_id
)
SELECT
    d.device_name,
    d.location,
    ds.data_points,
    round(ds.avg_temp::numeric, 2) AS avg_temp,
    round(ds.avg_humidity::numeric, 2) AS avg_humidity,
    round(ds.avg_battery::numeric, 0) AS avg_battery,
    dh.health_status,
    ds.last_seen
FROM device_stats ds
JOIN iot_devices d ON ds.device_id = d.device_id
JOIN device_health dh ON ds.device_id = dh.device_id
WHERE dh.health_status != 'Healthy'
ORDER BY ds.last_seen DESC
LIMIT 50;
```

---

## 📚 11. 最佳实践

### 11.1 数据模型设计

- ✅ 使用 time 作为第一分区键
- ✅ chunk_time_interval 选择 1 天或 1 周
- ✅ 在高基数列上创建索引（device_id）
- ✅ 避免过多的索引（影响写入性能）

### 11.2 写入优化

- ✅ 使用批量 INSERT（1000-10000 行/批）
- ✅ 使用 COPY 协议（最快）
- ✅ 避免在写入路径上使用触发器
- ✅ 调整 autovacuum 参数

### 11.3 查询优化

- ✅ 优先使用连续聚合视图
- ✅ 利用 chunk 排除（时间范围过滤）
- ✅ 使用 time_bucket 聚合
- ✅ 启用并行查询

### 11.4 运维管理

- ✅ 配置自动压缩（7 天后）
- ✅ 配置数据保留（90 天）
- ✅ 监控 chunk 数量和大小
- ✅ 定期 VACUUM 和 ANALYZE

---

## 🎯 12. 练习任务

1. **基础练习**：

   - 创建超表并插入 10 万条测试数据
   - 创建连续聚合视图（5 分钟粒度）
   - 查询最近 1 小时的数据趋势

2. **进阶练习**：

   - 实现自动压缩和保留策略
   - 创建异常检测查询
   - 优化高频查询性能

3. **挑战任务**：
   - 构建完整的 IoT 监控平台
   - 实现实时告警系统
   - 处理千万级数据的查询优化

---

## 📖 13. 参考资源

- TimescaleDB 官方文档: <https://docs.timescale.com/>
- Time-Series Best Practices: <https://docs.timescale.com/timescaledb/latest/how-to-guides/>
- PostgreSQL Performance Tuning: <https://wiki.postgresql.org/wiki/Performance_Optimization>

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**下一步**：查看 [分布式锁案例](../distributed_locks/README.md)
