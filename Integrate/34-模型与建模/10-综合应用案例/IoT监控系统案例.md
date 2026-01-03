# IoT监控系统案例

> **创建日期**: 2025年1月
> **来源**: 综合应用案例
> **状态**: 待完善
> **文档编号**: 10-03

---

## 📑 目录

- [IoT监控系统案例](#iot监控系统案例)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. 业务需求](#2-业务需求)
    - [2.1 核心业务功能](#21-核心业务功能)
    - [2.2 性能要求](#22-性能要求)
  - [3. 设备模型设计](#3-设备模型设计)
    - [3.1 设备表设计](#31-设备表设计)
    - [3.2 设备状态管理](#32-设备状态管理)
  - [4. 时序数据设计](#4-时序数据设计)
    - [4.1 TimescaleDB Hypertable](#41-timescaledb-hypertable)
    - [4.2 连续聚合视图](#42-连续聚合视图)
  - [5. 实时监控设计](#5-实时监控设计)
    - [5.1 告警规则表](#51-告警规则表)
    - [5.2 实时监控函数](#52-实时监控函数)
  - [6. PostgreSQL实现](#6-postgresql实现)
    - [6.1 完整系统实现](#61-完整系统实现)
    - [6.2 查询示例](#62-查询示例)
  - [7. 相关资源](#7-相关资源)

---

## 1. 概述

IoT监控系统案例展示如何设计支持大规模设备监控的数据模型。
本案例使用TimescaleDB处理时序数据，实现设备监控、数据采集、实时告警等功能。

**案例特点**:

- **大规模设备**：支持百万级设备接入
- **高频数据**：每秒百万级数据点
- **实时监控**：实时数据采集和告警
- **历史分析**：长期数据存储和分析

---

## 2. 业务需求

### 2.1 核心业务功能

**业务需求清单**:

1. **设备管理**
   - 设备注册、配置
   - 设备状态监控
   - 设备分组管理

2. **数据采集**
   - 传感器数据采集
   - 设备遥测数据
   - 数据质量保证

3. **实时监控**
   - 实时数据展示
   - 异常检测
   - 告警通知

4. **数据分析**
   - 历史数据查询
   - 数据聚合分析
   - 趋势预测

### 2.2 性能要求

- **写入性能**：支持100万+数据点/秒
- **查询性能**：实时查询<100ms
- **存储容量**：PB级数据存储
- **数据保留**：原始数据保留1年，聚合数据保留5年

---

## 3. 设备模型设计

### 3.1 设备表设计

**设备模型**:

```sql
-- 设备类型表
CREATE TABLE device_types (
    type_id SERIAL PRIMARY KEY,
    type_code VARCHAR(50) UNIQUE NOT NULL,
    type_name VARCHAR(200) NOT NULL,
    description TEXT,
    -- 设备属性定义
    attributes_schema JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 设备表（设备孪生）
CREATE TABLE devices (
    device_id VARCHAR(50) PRIMARY KEY,
    device_name VARCHAR(200) NOT NULL,
    device_type_id INT NOT NULL REFERENCES device_types(type_id),
    -- 设备属性
    properties JSONB DEFAULT '{}',
    -- 设备配置
    configuration JSONB DEFAULT '{}',
    -- 设备状态
    status VARCHAR(50) DEFAULT 'offline', -- 'online', 'offline', 'error'
    -- 位置信息
    location JSONB,
    -- 元数据
    manufacturer VARCHAR(100),
    model_number VARCHAR(100),
    firmware_version VARCHAR(50),
    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ
);

-- 设备分组表
CREATE TABLE device_groups (
    group_id SERIAL PRIMARY KEY,
    group_name VARCHAR(200) NOT NULL,
    parent_group_id INT REFERENCES device_groups(group_id),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 设备分组关联表
CREATE TABLE device_group_members (
    device_id VARCHAR(50) REFERENCES devices(device_id),
    group_id INT REFERENCES device_groups(group_id),
    PRIMARY KEY (device_id, group_id)
);
```

### 3.2 设备状态管理

**状态历史表**:

```sql
-- 设备状态历史表（分区表）
CREATE TABLE device_state_history (
    state_id BIGSERIAL,
    device_id VARCHAR(50) NOT NULL REFERENCES devices(device_id),
    status VARCHAR(50) NOT NULL,
    state_data JSONB,
    change_reason VARCHAR(200),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (state_id, timestamp)
) PARTITION BY RANGE (timestamp);

-- 创建分区（按月）
CREATE TABLE device_state_history_2025_01
    PARTITION OF device_state_history
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

---

## 4. 时序数据设计

### 4.1 TimescaleDB Hypertable

**时序数据表**:

```sql
-- 安装TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 设备遥测数据表（Hypertable）
CREATE TABLE device_telemetry (
    time TIMESTAMPTZ NOT NULL,
    device_id VARCHAR(50) NOT NULL REFERENCES devices(device_id),
    -- 遥测数据（JSONB存储灵活结构）
    telemetry_data JSONB NOT NULL,
    -- 数据质量
    quality_code INT DEFAULT 0, -- 0=good, 1=uncertain, 2=bad
    -- 元数据
    metadata JSONB
);

-- 转换为Hypertable
SELECT create_hypertable('device_telemetry', 'time',
    chunk_time_interval => INTERVAL '1 day');

-- 创建索引
CREATE INDEX idx_telemetry_device_time ON device_telemetry(device_id, time DESC);
CREATE INDEX idx_telemetry_data ON device_telemetry USING GIN(telemetry_data);

-- 启用压缩（7天前的数据自动压缩）
ALTER TABLE device_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('device_telemetry', INTERVAL '7 days');

-- 数据保留策略（原始数据保留1年）
SELECT add_retention_policy('device_telemetry', INTERVAL '1 year');
```

### 4.2 连续聚合视图

**聚合视图**:

```sql
-- 小时聚合视图
CREATE MATERIALIZED VIEW device_telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    device_id,
    -- 聚合指标
    COUNT(*) AS data_points,
    AVG((telemetry_data->>'temperature')::NUMERIC) AS avg_temperature,
    MAX((telemetry_data->>'temperature')::NUMERIC) AS max_temperature,
    MIN((telemetry_data->>'temperature')::NUMERIC) AS min_temperature,
    AVG((telemetry_data->>'humidity')::NUMERIC) AS avg_humidity,
    AVG((telemetry_data->>'pressure')::NUMERIC) AS avg_pressure
FROM device_telemetry
GROUP BY hour, device_id;

-- 自动刷新策略
SELECT add_continuous_aggregate_policy('device_telemetry_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- 日聚合视图
CREATE MATERIALIZED VIEW device_telemetry_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS day,
    device_id,
    COUNT(*) AS data_points,
    AVG((telemetry_data->>'temperature')::NUMERIC) AS avg_temperature,
    MAX((telemetry_data->>'temperature')::NUMERIC) AS max_temperature,
    MIN((telemetry_data->>'temperature')::NUMERIC) AS min_temperature
FROM device_telemetry
GROUP BY day, device_id;

SELECT add_continuous_aggregate_policy('device_telemetry_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
```

---

## 5. 实时监控设计

### 5.1 告警规则表

**告警配置**:

```sql
-- 告警规则表
CREATE TABLE alert_rules (
    rule_id SERIAL PRIMARY KEY,
    rule_name VARCHAR(200) NOT NULL,
    device_type_id INT REFERENCES device_types(type_id),
    device_id VARCHAR(50) REFERENCES devices(device_id),
    -- 告警条件
    metric_name VARCHAR(100) NOT NULL,
    condition_type VARCHAR(50) NOT NULL, -- 'gt', 'lt', 'eq', 'between'
    threshold_value NUMERIC(10,2),
    threshold_min NUMERIC(10,2),
    threshold_max NUMERIC(10,2),
    -- 告警配置
    severity VARCHAR(50) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    enabled BOOLEAN DEFAULT TRUE,
    -- 通知配置
    notification_channels TEXT[], -- ['email', 'sms', 'webhook']
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 告警事件表
CREATE TABLE alert_events (
    alert_id BIGSERIAL PRIMARY KEY,
    rule_id INT NOT NULL REFERENCES alert_rules(rule_id),
    device_id VARCHAR(50) NOT NULL REFERENCES devices(device_id),
    -- 告警信息
    alert_time TIMESTAMPTZ DEFAULT NOW(),
    metric_name VARCHAR(100),
    metric_value NUMERIC(10,2),
    threshold_value NUMERIC(10,2),
    -- 告警状态
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'acknowledged', 'resolved'
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    -- 通知状态
    notifications_sent BOOLEAN DEFAULT FALSE,
    notification_status JSONB
);
```

### 5.2 实时监控函数

**监控检测**:

```sql
-- 实时告警检测函数
CREATE OR REPLACE FUNCTION check_device_alerts(
    p_device_id VARCHAR,
    p_telemetry_data JSONB
)
RETURNS TABLE (
    rule_id INT,
    alert_id BIGINT
) AS $$
DECLARE
    v_rule RECORD;
    v_metric_value NUMERIC(10,2);
    v_alert_id BIGINT;
BEGIN
    -- 遍历设备的告警规则
    FOR v_rule IN
        SELECT * FROM alert_rules
        WHERE (device_id IS NULL OR device_id = p_device_id)
          AND enabled = TRUE
    LOOP
        -- 获取指标值
        v_metric_value := (p_telemetry_data->>v_rule.metric_name)::NUMERIC;

        -- 检查告警条件
        IF (
            (v_rule.condition_type = 'gt' AND v_metric_value > v_rule.threshold_value) OR
            (v_rule.condition_type = 'lt' AND v_metric_value < v_rule.threshold_value) OR
            (v_rule.condition_type = 'eq' AND v_metric_value = v_rule.threshold_value) OR
            (v_rule.condition_type = 'between' AND
             v_metric_value BETWEEN v_rule.threshold_min AND v_rule.threshold_max)
        ) THEN
            -- 创建告警事件
            INSERT INTO alert_events (
                rule_id, device_id, metric_name, metric_value, threshold_value
            ) VALUES (
                v_rule.rule_id, p_device_id, v_rule.metric_name,
                v_metric_value, v_rule.threshold_value
            ) RETURNING alert_id INTO v_alert_id;

            RETURN QUERY SELECT v_rule.rule_id, v_alert_id;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. PostgreSQL实现

### 6.1 完整系统实现

**数据写入流程**:

```sql
-- 批量写入遥测数据
CREATE OR REPLACE FUNCTION insert_telemetry_batch(
    p_data JSONB
)
RETURNS INT AS $$
DECLARE
    v_count INT := 0;
    v_item JSONB;
    v_device_id VARCHAR(50);
    v_telemetry_data JSONB;
BEGIN
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_data)
    LOOP
        v_device_id := v_item->>'device_id';
        v_telemetry_data := v_item->'telemetry_data';

        -- 插入遥测数据
        INSERT INTO device_telemetry (
            time, device_id, telemetry_data
        ) VALUES (
            COALESCE((v_item->>'time')::TIMESTAMPTZ, NOW()),
            v_device_id,
            v_telemetry_data
        );

        -- 更新设备最后在线时间
        UPDATE devices
        SET last_seen_at = NOW(),
            status = 'online',
            updated_at = NOW()
        WHERE device_id = v_device_id;

        -- 检测告警
        PERFORM check_device_alerts(v_device_id, v_telemetry_data);

        v_count := v_count + 1;
    END LOOP;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;
```

### 6.2 查询示例

**实时查询**:

```sql
-- 查询设备最新数据
SELECT DISTINCT ON (device_id)
    device_id,
    time,
    telemetry_data->>'temperature' AS temperature,
    telemetry_data->>'humidity' AS humidity
FROM device_telemetry
WHERE device_id IN ('device_001', 'device_002')
ORDER BY device_id, time DESC;

-- 查询告警事件
SELECT
    ae.alert_id,
    d.device_name,
    ar.rule_name,
    ae.metric_name,
    ae.metric_value,
    ae.threshold_value,
    ae.alert_time,
    ae.status
FROM alert_events ae
JOIN alert_rules ar ON ae.rule_id = ar.rule_id
JOIN devices d ON ae.device_id = d.device_id
WHERE ae.status = 'active'
ORDER BY ae.alert_time DESC;

-- 查询历史趋势（使用连续聚合）
SELECT
    hour,
    device_id,
    avg_temperature,
    max_temperature,
    min_temperature
FROM device_telemetry_hourly
WHERE device_id = 'device_001'
  AND hour > NOW() - INTERVAL '24 hours'
ORDER BY hour DESC;
```

---

## 7. 相关资源

- [TimescaleDB实践](../06-IoT与时序建模/TimescaleDB实践.md) - TimescaleDB详细指南
- [时序数据模型](../06-IoT与时序建模/时序数据模型.md) - 时序数据建模
- [设备孪生模型](../06-IoT与时序建模/设备孪生模型.md) - 设备孪生设计

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
