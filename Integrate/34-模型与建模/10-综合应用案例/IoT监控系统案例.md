# IoT监控系统案例

> **创建日期**: 2025年1月
> **来源**: 综合应用案例
> **状态**: ✅ 已完成
> **文档编号**: 10-03

---

## 📑 目录

- [IoT监控系统案例](#iot监控系统案例)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [1.1 理论基础](#11-理论基础)
    - [1.1.1 IoT数据模型设计理论](#111-iot数据模型设计理论)
    - [1.1.2 设备孪生理论](#112-设备孪生理论)
    - [1.1.3 时序数据理论](#113-时序数据理论)
    - [1.1.4 TimescaleDB理论](#114-timescaledb理论)
    - [1.1.5 实时监控理论](#115-实时监控理论)
    - [1.1.6 数据压缩理论](#116-数据压缩理论)
    - [1.1.7 复杂度分析](#117-复杂度分析)
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
  - [7. 性能优化与监控 / Performance Optimization and Monitoring](#7-性能优化与监控--performance-optimization-and-monitoring)
    - [7.1 数据写入优化](#71-数据写入优化)
    - [7.2 查询性能优化](#72-查询性能优化)
    - [7.3 存储优化](#73-存储优化)
    - [7.4 系统监控](#74-系统监控)
  - [8. 常见问题解答 / FAQ](#8-常见问题解答--faq)
    - [Q1: 如何支持百万级设备接入？](#q1-如何支持百万级设备接入)
    - [Q2: 如何处理高频数据写入？](#q2-如何处理高频数据写入)
    - [Q3: 如何优化实时查询性能？](#q3-如何优化实时查询性能)
    - [Q4: 如何实现数据压缩和归档？](#q4-如何实现数据压缩和归档)
    - [Q5: 如何优化告警检测性能？](#q5-如何优化告警检测性能)
    - [Q6: 如何监控系统健康状态？](#q6-如何监控系统健康状态)
  - [8. 相关资源 / Related Resources](#8-相关资源--related-resources)
    - [8.1 核心相关文档 / Core Related Documents](#81-核心相关文档--core-related-documents)
    - [8.2 理论基础 / Theoretical Foundation](#82-理论基础--theoretical-foundation)
    - [8.3 实践指南 / Practical Guides](#83-实践指南--practical-guides)
    - [8.4 应用案例 / Application Cases](#84-应用案例--application-cases)
    - [8.5 参考资源 / Reference Resources](#85-参考资源--reference-resources)

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

## 1.1 理论基础

### 1.1.1 IoT数据模型设计理论

**IoT数据模型**:

- **设备模型**: 设备元数据和状态管理
- **时序数据**: 设备传感器时序数据
- **实时监控**: 实时数据采集和告警

**模型设计原则**:

- **设备管理**: 使用设备孪生模型管理设备
- **时序存储**: 使用时序数据库存储时序数据
- **实时处理**: 实时数据处理和告警

### 1.1.2 设备孪生理论

**设备孪生（Digital Twin）**:

- **设备模型**: 设备在数字世界的完整映射
- **状态同步**: 实时同步物理设备状态
- **远程控制**: 通过数字孪生控制物理设备

**设备孪生特点**:

- **状态管理**: 设备状态实时同步
- **命令控制**: 设备命令可靠执行
- **历史追溯**: 设备完整生命周期记录

### 1.1.3 时序数据理论

**时序数据**:

- **数据特征**: 时间有序、高频写入、不可变
- **数据模型**: 时间戳+指标值+标签
- **存储优化**: 时序数据压缩和分区

**时序数据处理**:

- **数据采集**: 高频数据采集
- **数据存储**: 时序数据压缩存储
- **数据查询**: 时间范围查询和聚合

### 1.1.4 TimescaleDB理论

**TimescaleDB**:

- **Hypertable**: 自动分区的时序表
- **连续聚合**: 自动维护的物化视图
- **数据压缩**: 时序数据压缩

**TimescaleDB优势**:

- **自动分区**: 自动按时间分区
- **查询优化**: 分区剪枝优化查询
- **压缩优化**: 时序数据高效压缩

### 1.1.5 实时监控理论

**实时监控**:

- **数据采集**: 实时数据采集
- **异常检测**: 实时异常检测
- **告警通知**: 实时告警通知

**实时监控方法**:

- **流式处理**: 流式数据处理
- **规则引擎**: 基于规则的异常检测
- **机器学习**: 基于机器学习的异常检测

### 1.1.6 数据压缩理论

**时序数据压缩**:

- **压缩算法**: Delta Encoding、Gorilla Encoding
- **压缩率**: 通常5-10倍压缩率
- **查询性能**: 压缩后查询性能略有下降

**压缩策略**:

- **时间压缩**: 时间戳差值压缩
- **值压缩**: 数值差值压缩
- **标签压缩**: 标签去重和编码

### 1.1.7 复杂度分析

**存储复杂度**:

- **设备存储**: $O(D)$ where D is number of devices
- **时序存储**: $O(D \times T)$ where T is average telemetry per device
- **压缩存储**: $O(D \times T \times C)$ where C is compression ratio

**查询复杂度**:

- **设备查询**: $O(\log D)$ with index
- **时序查询**: $O(\log T)$ with time index
- **聚合查询**: $O(\log A)$ with continuous aggregates

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
-- 设备类型表（带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS device_types (
        type_id SERIAL PRIMARY KEY,
        type_code VARCHAR(50) UNIQUE NOT NULL,
        type_name VARCHAR(200) NOT NULL,
        description TEXT,
        -- 设备属性定义
        attributes_schema JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    RAISE NOTICE '表 device_types 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表 device_types 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 device_types 失败: %', SQLERRM;
END $$;

-- 设备表（设备孪生，带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS devices (
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
    RAISE NOTICE '表 devices 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表 devices 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 devices 失败: %', SQLERRM;
END $$;

-- 设备分组表（带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS device_groups (
        group_id SERIAL PRIMARY KEY,
        group_name VARCHAR(200) NOT NULL,
        parent_group_id INT REFERENCES device_groups(group_id),
        description TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    RAISE NOTICE '表 device_groups 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表 device_groups 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 device_groups 失败: %', SQLERRM;
END $$;

-- 设备分组关联表（带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS device_group_members (
        device_id VARCHAR(50) REFERENCES devices(device_id),
        group_id INT REFERENCES device_groups(group_id),
        PRIMARY KEY (device_id, group_id)
    );
    RAISE NOTICE '表 device_group_members 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表 device_group_members 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 device_group_members 失败: %', SQLERRM;
END $$;
```

### 3.2 设备状态管理

**状态历史表**:

```sql
-- 设备状态历史表（分区表，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'device_state_history') THEN
        CREATE TABLE device_state_history (
            state_id BIGSERIAL,
            device_id VARCHAR(50) NOT NULL REFERENCES devices(device_id),
            status VARCHAR(50) NOT NULL,
            state_data JSONB,
            change_reason VARCHAR(200),
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            PRIMARY KEY (state_id, timestamp)
        ) PARTITION BY RANGE (timestamp);
        RAISE NOTICE '分区表 device_state_history 创建成功';
    ELSE
        RAISE NOTICE '表 device_state_history 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建分区表 device_state_history 失败: %', SQLERRM;
END $$;

-- 创建分区（按月，带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS device_state_history_2025_01
        PARTITION OF device_state_history
        FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
    RAISE NOTICE '分区 device_state_history_2025_01 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '分区 device_state_history_2025_01 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE WARNING '创建分区失败: %', SQLERRM;
END $$;
```

---

## 4. 时序数据设计

### 4.1 TimescaleDB Hypertable

**时序数据表**:

```sql
-- 安装TimescaleDB扩展（带错误处理）
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS timescaledb;
    RAISE NOTICE 'TimescaleDB扩展已安装';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE 'TimescaleDB扩展已存在，跳过安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装TimescaleDB扩展失败: %', SQLERRM;
END $$;

-- 设备遥测数据表（Hypertable，带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS device_telemetry (
        time TIMESTAMPTZ NOT NULL,
        device_id VARCHAR(50) NOT NULL REFERENCES devices(device_id),
        -- 遥测数据（JSONB存储灵活结构）
        telemetry_data JSONB NOT NULL,
        -- 数据质量
        quality_code INT DEFAULT 0, -- 0=good, 1=uncertain, 2=bad
        -- 元数据
        metadata JSONB
    );
    RAISE NOTICE '表 device_telemetry 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表 device_telemetry 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 device_telemetry 失败: %', SQLERRM;
END $$;

-- 转换为Hypertable（带错误处理）
DO $$
BEGIN
    PERFORM create_hypertable('device_telemetry', 'time',
        chunk_time_interval => INTERVAL '1 day');
    RAISE NOTICE 'Hypertable创建成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建Hypertable失败: %', SQLERRM;
END $$;

-- 创建索引（带错误处理）
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_telemetry_device_time ON device_telemetry(device_id, time DESC);
    CREATE INDEX IF NOT EXISTS idx_telemetry_data ON device_telemetry USING GIN(telemetry_data);
    RAISE NOTICE '索引创建成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建索引失败: %', SQLERRM;
END $$;

-- 启用压缩（7天前的数据自动压缩，带错误处理）
DO $$
BEGIN
    ALTER TABLE device_telemetry SET (
        timescaledb.compress,
        timescaledb.compress_segmentby = 'device_id',
        timescaledb.compress_orderby = 'time DESC'
    );
    PERFORM add_compression_policy('device_telemetry', INTERVAL '7 days');
    RAISE NOTICE '压缩策略已配置';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '配置压缩策略失败: %', SQLERRM;
END $$;

-- 数据保留策略（原始数据保留1年，带错误处理）
DO $$
BEGIN
    PERFORM add_retention_policy('device_telemetry', INTERVAL '1 year');
    RAISE NOTICE '数据保留策略已配置';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '配置数据保留策略失败: %', SQLERRM;
END $$;
```

### 4.2 连续聚合视图

**聚合视图**:

```sql
-- 小时聚合视图（带错误处理）
DO $$
BEGIN
    CREATE MATERIALIZED VIEW IF NOT EXISTS device_telemetry_hourly
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
    RAISE NOTICE '连续聚合视图 device_telemetry_hourly 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '连续聚合视图 device_telemetry_hourly 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建连续聚合视图失败: %', SQLERRM;
END $$;

-- 自动刷新策略（带错误处理）
DO $$
BEGIN
    PERFORM add_continuous_aggregate_policy('device_telemetry_hourly',
        start_offset => INTERVAL '3 hours',
        end_offset => INTERVAL '1 hour',
        schedule_interval => INTERVAL '1 hour');
    RAISE NOTICE '刷新策略已配置';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '配置刷新策略失败: %', SQLERRM;
END $$;

-- 日聚合视图（带错误处理）
DO $$
BEGIN
    CREATE MATERIALIZED VIEW IF NOT EXISTS device_telemetry_daily
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
    RAISE NOTICE '连续聚合视图 device_telemetry_daily 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '连续聚合视图 device_telemetry_daily 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建连续聚合视图失败: %', SQLERRM;
END $$;

-- 自动刷新策略（带错误处理）
DO $$
BEGIN
    PERFORM add_continuous_aggregate_policy('device_telemetry_daily',
        start_offset => INTERVAL '3 days',
        end_offset => INTERVAL '1 day',
        schedule_interval => INTERVAL '1 day');
    RAISE NOTICE '刷新策略已配置';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '配置刷新策略失败: %', SQLERRM;
END $$;
```

---

## 5. 实时监控设计

### 5.1 告警规则表

**告警配置**:

```sql
-- 告警规则表（带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS alert_rules (
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
    RAISE NOTICE '表 alert_rules 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表 alert_rules 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 alert_rules 失败: %', SQLERRM;
END $$;

-- 告警事件表（带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS alert_events (
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
    RAISE NOTICE '表 alert_events 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表 alert_events 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 alert_events 失败: %', SQLERRM;
END $$;
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
-- 查询设备最新数据（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT DISTINCT ON (device_id)
    device_id,
    time,
    telemetry_data->>'temperature' AS temperature,
    telemetry_data->>'humidity' AS humidity
FROM device_telemetry
WHERE device_id IN ('device_001', 'device_002')
ORDER BY device_id, time DESC;

-- 查询告警事件（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
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

-- 查询历史趋势（使用连续聚合，带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
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

## 7. 性能优化与监控 / Performance Optimization and Monitoring

### 7.1 数据写入优化

**批量写入优化**:

```sql
-- 批量插入遥测数据
CREATE OR REPLACE FUNCTION batch_insert_telemetry(
    p_data JSONB
)
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    INSERT INTO device_telemetry (device_id, time, sensor_type, value)
    SELECT
        (elem->>'device_id')::INT,
        (elem->>'time')::TIMESTAMPTZ,
        elem->>'sensor_type',
        (elem->>'value')::DOUBLE PRECISION
    FROM jsonb_array_elements(p_data) AS elem;

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- 使用COPY批量导入（最快）
COPY device_telemetry (device_id, time, sensor_type, value)
FROM '/path/to/data.csv' WITH CSV HEADER;
```

**写入性能监控**:

```sql
-- 监控写入速率（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    time_bucket('1 minute', time) AS minute,
    COUNT(*) AS data_points,
    COUNT(DISTINCT device_id) AS device_count
FROM device_telemetry
WHERE time >= NOW() - INTERVAL '1 hour'
GROUP BY minute
ORDER BY minute DESC;
```

### 7.2 查询性能优化

**连续聚合优化**:

```sql
-- 创建多级聚合视图
CREATE MATERIALIZED VIEW device_telemetry_minutely
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS bucket,
    device_id,
    sensor_type,
    AVG(value) AS avg_value,
    MAX(value) AS max_value,
    MIN(value) AS min_value,
    COUNT(*) AS data_points
FROM device_telemetry
GROUP BY bucket, device_id, sensor_type;

CREATE MATERIALIZED VIEW device_telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    sensor_type,
    AVG(value) AS avg_value,
    MAX(value) AS max_value,
    MIN(value) AS min_value
FROM device_telemetry_minutely
GROUP BY bucket, device_id, sensor_type;

-- 查询时使用聚合视图
SELECT * FROM device_telemetry_hourly
WHERE device_id = 1
  AND bucket >= NOW() - INTERVAL '24 hours';
```

### 7.3 存储优化

**压缩策略优化**:

```sql
-- TimescaleDB压缩配置
ALTER TABLE device_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- 设置压缩策略（7天后压缩）
SELECT add_compression_policy('device_telemetry', INTERVAL '7 days');

-- 数据保留策略（90天后删除）
SELECT add_retention_policy('device_telemetry', INTERVAL '90 days');
```

**存储空间监控**:

```sql
-- 监控存储空间
SELECT
    hypertable_name,
    COUNT(*) AS chunk_count,
    pg_size_pretty(SUM(chunk_size)) AS total_size,
    COUNT(*) FILTER (WHERE is_compressed = true) AS compressed_chunks,
    pg_size_pretty(SUM(chunk_size) FILTER (WHERE is_compressed = true)) AS compressed_size
FROM timescaledb_information.chunks
WHERE hypertable_name = 'device_telemetry'
GROUP BY hypertable_name;
```

### 7.4 系统监控

**设备监控**:

```sql
-- 监控设备在线状态
SELECT
    device_type,
    COUNT(*) FILTER (WHERE status = 'online') AS online_count,
    COUNT(*) FILTER (WHERE status = 'offline') AS offline_count,
    COUNT(*) FILTER (WHERE last_connected_at < NOW() - INTERVAL '5 minutes') AS disconnected_count,
    AVG(EXTRACT(EPOCH FROM (NOW() - last_connected_at))) FILTER (WHERE status = 'offline') AS avg_offline_seconds
FROM device_twin
GROUP BY device_type;

-- 监控数据采集延迟
SELECT
    device_id,
    MAX(time) AS last_data_time,
    NOW() - MAX(time) AS data_delay,
    COUNT(*) FILTER (WHERE time >= NOW() - INTERVAL '1 hour') AS data_points_last_hour
FROM device_telemetry
GROUP BY device_id
HAVING MAX(time) < NOW() - INTERVAL '5 minutes'
ORDER BY data_delay DESC;
```

**告警监控**:

```sql
-- 监控告警统计
SELECT
    alert_level,
    COUNT(*) AS alert_count,
    COUNT(*) FILTER (WHERE status = 'active') AS active_count,
    COUNT(*) FILTER (WHERE status = 'resolved') AS resolved_count,
    AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))) FILTER (WHERE status = 'resolved') AS avg_resolution_seconds
FROM device_alerts
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY alert_level
ORDER BY alert_count DESC;
```

---

## 8. 常见问题解答 / FAQ

### Q1: 如何支持百万级设备接入？

**A**: 大规模设备支持策略：

1. **分区优化**: 按设备ID或时间分区
2. **连接池**: 使用pgBouncer管理连接
3. **异步处理**: 使用消息队列缓冲写入
4. **读写分离**: 分离实时写入和历史查询

```sql
-- 按设备ID HASH分区
-- 设备遥测数据表（分区表，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'device_telemetry') THEN
        CREATE TABLE device_telemetry (
            telemetry_id BIGSERIAL,
            device_id VARCHAR(50) NOT NULL,
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            metric_name VARCHAR(50) NOT NULL,
            metric_value DOUBLE PRECISION NOT NULL,
            PRIMARY KEY (telemetry_id, device_id)
        ) PARTITION BY HASH (device_id);
        RAISE NOTICE '分区表 device_telemetry 创建成功';
    ELSE
        RAISE NOTICE '表 device_telemetry 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建分区表 device_telemetry 失败: %', SQLERRM;
END $$;

-- 创建8个分区（带错误处理）
DO $$
BEGIN
    FOR i IN 0..7 LOOP
        EXECUTE format('CREATE TABLE IF NOT EXISTS device_telemetry_%s PARTITION OF device_telemetry FOR VALUES WITH (MODULUS 8, REMAINDER %s)', i, i);
    END LOOP;
    RAISE NOTICE 'HASH分区创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '分区已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE WARNING '创建HASH分区失败: %', SQLERRM;
END $$;
```

### Q2: 如何处理高频数据写入？

**A**: 高频写入优化：

1. **批量写入**: 使用批量INSERT或COPY
2. **异步写入**: 使用消息队列缓冲
3. **连接复用**: 使用连接池
4. **减少索引**: 仅创建必要索引

```sql
-- 批量写入函数
CREATE OR REPLACE FUNCTION batch_insert_telemetry_bulk(
    p_device_id INT,
    p_data_points JSONB
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO device_telemetry (device_id, time, sensor_type, value)
    SELECT
        p_device_id,
        (elem->>'time')::TIMESTAMPTZ,
        elem->>'sensor_type',
        (elem->>'value')::DOUBLE PRECISION
    FROM jsonb_array_elements(p_data_points) AS elem;
END;
$$ LANGUAGE plpgsql;
```

### Q3: 如何优化实时查询性能？

**A**: 实时查询优化：

1. **使用连续聚合**: 预计算聚合结果
2. **限制查询范围**: 只查询最近数据
3. **使用物化视图**: 缓存热点查询
4. **索引优化**: 为时间范围查询创建索引

```sql
-- 实时数据查询（仅查询最近1小时）
SELECT * FROM device_telemetry
WHERE device_id = 1
  AND time >= NOW() - INTERVAL '1 hour'
ORDER BY time DESC;

-- 使用连续聚合查询历史数据
SELECT * FROM device_telemetry_hourly
WHERE device_id = 1
  AND bucket >= NOW() - INTERVAL '7 days';
```

### Q4: 如何实现数据压缩和归档？

**A**: 压缩和归档策略：

```sql
-- TimescaleDB自动压缩
SELECT add_compression_policy('device_telemetry', INTERVAL '7 days');

-- 手动压缩
SELECT compress_chunk(chunk) FROM timescaledb_information.chunks
WHERE hypertable_name = 'device_telemetry'
  AND is_compressed = false
  AND range_end < NOW() - INTERVAL '7 days';

-- 归档旧数据
-- 设备遥测数据归档表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'device_telemetry_archive') THEN
        CREATE TABLE device_telemetry_archive (LIKE device_telemetry INCLUDING ALL);
        RAISE NOTICE '归档表 device_telemetry_archive 创建成功';
    ELSE
        RAISE NOTICE '归档表 device_telemetry_archive 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建归档表 device_telemetry_archive 失败: %', SQLERRM;
END $$;

INSERT INTO device_telemetry_archive
SELECT * FROM device_telemetry
WHERE time < NOW() - INTERVAL '1 year';

DELETE FROM device_telemetry
WHERE time < NOW() - INTERVAL '1 year';
```

### Q5: 如何优化告警检测性能？

**A**: 告警检测优化：

1. **规则缓存**: 缓存活跃告警规则
2. **批量检测**: 批量处理多个设备
3. **异步检测**: 非关键告警异步检测
4. **规则优先级**: 先检测高优先级规则

```sql
-- 批量告警检测
CREATE OR REPLACE FUNCTION batch_check_alerts(
    p_device_ids INT[]
)
RETURNS TABLE(device_id INT, alert_level VARCHAR, message TEXT) AS $$
DECLARE
    v_device_id INT;
    v_rule RECORD;
BEGIN
    FOR v_device_id IN SELECT unnest(p_device_ids)
    LOOP
        FOR v_rule IN SELECT * FROM alert_rules WHERE is_enabled = TRUE ORDER BY priority DESC
        LOOP
            -- 执行规则检测
            IF check_alert_rule(v_device_id, v_rule) THEN
                RETURN QUERY SELECT v_device_id, v_rule.alert_level, v_rule.message;
                EXIT;  -- 找到告警后退出
            END IF;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### Q6: 如何监控系统健康状态？

**A**: 系统健康监控：

```sql
-- 系统健康检查视图
CREATE VIEW system_health_check AS
SELECT
    'device_online_rate' AS metric,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'online') / COUNT(*), 2) AS value
FROM device_twin
UNION ALL
SELECT
    'data_collection_rate' AS metric,
    COUNT(*) AS value
FROM device_telemetry
WHERE time >= NOW() - INTERVAL '1 minute'
UNION ALL
SELECT
    'alert_resolution_rate' AS metric,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'resolved') / COUNT(*), 2) AS value
FROM device_alerts
WHERE created_at >= NOW() - INTERVAL '24 hours';

-- 查询系统健康状态
SELECT * FROM system_health_check;
```

---

## 8. 相关资源 / Related Resources

### 8.1 核心相关文档 / Core Related Documents

- [TimescaleDB实践](../06-IoT与时序建模/TimescaleDB实践.md) - TimescaleDB详细指南
- [时序数据模型](../06-IoT与时序建模/时序数据模型.md) - 时序数据建模
- [设备孪生模型](../06-IoT与时序建模/设备孪生模型.md) - 设备孪生设计
- [分区策略](../08-PostgreSQL建模实践/分区策略.md) - IoT数据分区策略
- [索引策略](../08-PostgreSQL建模实践/索引策略.md) - IoT数据索引设计
- [性能优化](../08-PostgreSQL建模实践/性能优化.md) - 性能优化指南

### 8.2 理论基础 / Theoretical Foundation

- [范式理论](../01-数据建模理论基础/范式理论.md) - 时序数据范式设计

### 8.3 实践指南 / Practical Guides

- [性能优化与监控](#7-性能优化与监控--performance-optimization-and-monitoring) - 本文档的性能监控章节

### 8.4 应用案例 / Application Cases

- [电商数据模型案例](./电商数据模型案例.md) - 电商系统建模案例
- [金融数据模型案例](./金融数据模型案例.md) - 金融系统建模案例

### 8.5 参考资源 / Reference Resources

- [权威资源索引](../00-导航与索引/权威资源索引.md) - 权威资源列表
- [术语对照表](../00-导航与索引/术语对照表.md) - 术语对照
- [快速查找指南](../00-导航与索引/快速查找指南.md) - 快速查找工具

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
