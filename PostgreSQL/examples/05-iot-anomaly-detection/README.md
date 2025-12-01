# IoT 异常检测示例

> **PostgreSQL版本**: 18 ⭐ | 17
> **TimescaleDB版本**: 2.13+
> **pgvector版本**: 2.0 ⭐ | 0.7+
> **最后更新**: 2025-11-11

---

## 📋 示例说明

本示例展示如何使用PostgreSQL 18 + TimescaleDB + pgvector构建IoT异常检测系统，结合时序数据和向量特征，实现设备异常检测和预测性维护。

**核心特性**：

- ✅ TimescaleDB时序数据存储
- ✅ pgvector向量特征分析
- ✅ 基于向量相似度的异常检测
- ✅ 时序连续聚合

**适用场景**：

- 工业设备监控
- IoT传感器数据分析
- 预测性维护
- 设备健康监测

---

## 🚀 快速开始

### 1. 启动服务

```bash
docker-compose up -d
```

### 2. 连接到数据库

```bash
docker-compose exec postgres psql -U postgres -d iot_monitoring
```

### 3. 检测异常

```sql
-- 检测设备1在过去1小时内的异常
SELECT * FROM detect_anomalies(1, '1 hour', 0.8);
```

### 4. 批量标记异常

```sql
-- 标记设备1的异常数据
SELECT mark_anomalies(1, '1 hour', 0.8);
```

### 5. 查看异常数据

```sql
-- 查看所有异常读数
SELECT
    time,
    device_id,
    temperature,
    humidity,
    pressure,
    vibration,
    anomaly_score
FROM sensor_readings
WHERE is_anomaly = true
ORDER BY time DESC
LIMIT 20;
```

### 6. 时序聚合查询

```sql
-- 查看每小时聚合数据
SELECT
    hour,
    device_id,
    avg_temperature,
    avg_humidity,
    anomaly_count
FROM sensor_readings_hourly
ORDER BY hour DESC
LIMIT 24;
```

### 7. 停止服务

```bash
docker-compose down
```

---

## 📊 架构说明

```text
┌─────────────────────────────────────────┐
│        IoT设备/传感器                    │
│  - 温度、湿度、压力、振动传感器            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      PostgreSQL 18 + TimescaleDB        │
│  - 时序数据表（超表）                     │
│  - 向量特征存储                          │
│  - 异常检测函数                          │
│  - 连续聚合视图                          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        应用层（监控/告警）                │
│  - 实时异常检测                          │
│  - 告警通知                              │
│  - 预测性维护建议                        │
└─────────────────────────────────────────┘
```

---

## 🔧 实际使用流程

### 1. 设备注册

```sql
-- 注册新设备
INSERT INTO devices (device_name, device_type, location, feature_vector)
VALUES (
    'sensor-004',
    'temperature',
    'factory-floor-4',
    '[生成的128维特征向量]'::vector(128)
);
```

### 2. 数据采集

```sql
-- 插入传感器读数
INSERT INTO sensor_readings (
    time, device_id, temperature, humidity, pressure, vibration, reading_vector
)
VALUES (
    now(),
    1,
    25.5,
    60.0,
    1013.25,
    0.0123,
    '[生成的128维读数向量]'::vector(128)
);
```

### 3. 实时异常检测

```python
# Python示例：实时异常检测
import psycopg2
from datetime import datetime, timedelta

def check_anomalies(device_id):
    conn = psycopg2.connect("dbname=iot_monitoring user=postgres")
    cur = conn.cursor()

    # 检测过去1小时的异常
    cur.execute("""
        SELECT * FROM detect_anomalies(%s, '1 hour', 0.8)
    """, (device_id,))

    anomalies = cur.fetchall()

    if anomalies:
        # 发送告警
        send_alert(device_id, anomalies)

    cur.close()
    conn.close()

    return anomalies
```

### 4. 批量处理

```sql
-- 定期批量标记异常（可设置定时任务）
SELECT mark_anomalies(device_id, '24 hours', 0.8)
FROM devices;
```

---

## 📈 性能优化建议

### 1. TimescaleDB分区策略

```sql
-- 查看分区信息
SELECT * FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_readings';

-- 手动压缩旧数据
SELECT compress_chunk(chunk)
FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_readings'
  AND range_end < now() - INTERVAL '30 days';
```

### 2. 索引优化

```sql
-- 确保向量索引存在
CREATE INDEX IF NOT EXISTS idx_readings_vector
ON sensor_readings USING hnsw (reading_vector vector_cosine_ops);

-- 设备+时间复合索引
CREATE INDEX IF NOT EXISTS idx_readings_device_time
ON sensor_readings (device_id, time DESC);
```

### 3. 数据保留策略

```sql
-- 删除30天前的数据
DELETE FROM sensor_readings
WHERE time < now() - INTERVAL '30 days';

-- 或使用TimescaleDB数据保留策略
SELECT add_retention_policy('sensor_readings', INTERVAL '30 days');
```

---

## 📚 相关文档

- [AI 时代专题 - 多模一体化](../../05-前沿技术/AI-时代/04-多模一体化-JSONB时序图向量.md)
- [落地案例 - 工业IoT异常检测](../../05-前沿技术/AI-时代/06-落地案例-2025精选.md#案例-4工业-iot-异常检测timescaledb--pgvector)
- [TimescaleDB文档](https://docs.timescale.com/)

---

## 🎯 扩展场景

### 1. 预测性维护

```sql
-- 基于异常频率预测设备故障
SELECT
    device_id,
    COUNT(*) FILTER (WHERE is_anomaly = true) AS anomaly_count,
    COUNT(*) AS total_readings,
    COUNT(*) FILTER (WHERE is_anomaly = true)::float / COUNT(*) AS anomaly_rate
FROM sensor_readings
WHERE time >= now() - INTERVAL '7 days'
GROUP BY device_id
HAVING COUNT(*) FILTER (WHERE is_anomaly = true)::float / COUNT(*) > 0.1;
```

### 2. 设备健康评分

```sql
-- 计算设备健康评分
CREATE OR REPLACE FUNCTION device_health_score(p_device_id bigint)
RETURNS numeric AS $$
DECLARE
    recent_anomaly_rate numeric;
    health_score numeric;
BEGIN
    SELECT
        COUNT(*) FILTER (WHERE is_anomaly = true)::float /
        NULLIF(COUNT(*), 0)
    INTO recent_anomaly_rate
    FROM sensor_readings
    WHERE device_id = p_device_id
      AND time >= now() - INTERVAL '24 hours';

    -- 健康评分：100 - (异常率 * 100)
    health_score := 100 - (COALESCE(recent_anomaly_rate, 0) * 100);

    RETURN GREATEST(0, LEAST(100, health_score));
END;
$$ LANGUAGE plpgsql;
```

### 3. 实时监控视图

```sql
-- 创建实时监控视图
CREATE VIEW device_status AS
SELECT
    d.id,
    d.device_name,
    d.location,
    sr.temperature,
    sr.humidity,
    sr.pressure,
    sr.vibration,
    sr.is_anomaly,
    device_health_score(d.id) AS health_score,
    sr.time AS last_reading_time
FROM devices d
LEFT JOIN LATERAL (
    SELECT *
    FROM sensor_readings
    WHERE device_id = d.id
    ORDER BY time DESC
    LIMIT 1
) sr ON true;
```

---

**最后更新**：2025-11-11
