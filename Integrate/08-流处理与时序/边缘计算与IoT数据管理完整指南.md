---
> **📋 文档来源**: 新增深化文档
> **📅 创建日期**: 2025-01
> **⚠️ 注意**: 本文档为深度补充，深化边缘计算与IoT数据管理技术栈

---

# 边缘计算与IoT数据管理完整指南

## 元数据

- **文档版本**: v1.0
- **创建日期**: 2025-01
- **技术栈**: PostgreSQL 17+/18+ | TimescaleDB 2.x | 逻辑复制 | pg_logical | MQTT
- **难度级别**: ⭐⭐⭐⭐ (高级)
- **预计阅读**: 150分钟
- **前置要求**: 熟悉PostgreSQL基础、时序数据库、网络架构

---

## 📋 完整目录

- [边缘计算与IoT数据管理完整指南](#边缘计算与iot数据管理完整指南)
  - [元数据](#元数据)
  - [📋 完整目录](#-完整目录)
  - [1. 边缘计算架构概述](#1-边缘计算架构概述)
    - [1.1 边缘计算概念](#11-边缘计算概念)
      - [边缘计算的优势](#边缘计算的优势)
      - [边缘计算挑战](#边缘计算挑战)
    - [1.2 边缘-云架构模式](#12-边缘-云架构模式)
      - [模式1：边缘预处理 + 云端存储](#模式1边缘预处理--云端存储)
      - [模式2：边缘存储 + 云端分析](#模式2边缘存储--云端分析)
      - [模式3：混合模式（推荐）](#模式3混合模式推荐)
    - [1.3 边缘数据库选型](#13-边缘数据库选型)
      - [PostgreSQL vs TimescaleDB](#postgresql-vs-timescaledb)
      - [选择建议](#选择建议)
  - [2. 边缘数据库部署](#2-边缘数据库部署)
    - [2.1 边缘节点架构设计](#21-边缘节点架构设计)
      - [硬件配置建议](#硬件配置建议)
      - [软件架构](#软件架构)
    - [2.2 PostgreSQL边缘部署](#22-postgresql边缘部署)
      - [最小化配置](#最小化配置)
      - [性能优化](#性能优化)
    - [2.3 TimescaleDB边缘部署](#23-timescaledb边缘部署)
      - [基础配置](#基础配置)
      - [压缩配置](#压缩配置)
      - [数据保留策略](#数据保留策略)
    - [2.4 容器化边缘部署](#24-容器化边缘部署)
      - [Docker Compose配置](#docker-compose配置)
      - [Kubernetes边缘部署](#kubernetes边缘部署)
  - [3. IoT数据采集与处理](#3-iot数据采集与处理)
    - [3.1 IoT数据模型设计](#31-iot数据模型设计)
      - [传感器数据模型](#传感器数据模型)
      - [数据质量保证](#数据质量保证)
    - [3.2 数据采集模式](#32-数据采集模式)
      - [模式1：MQTT采集](#模式1mqtt采集)
      - [模式2：HTTP REST API采集](#模式2http-rest-api采集)
    - [3.3 边缘数据处理](#33-边缘数据处理)
      - [实时聚合](#实时聚合)
      - [异常检测](#异常检测)
  - [4. 边缘-云端数据同步](#4-边缘-云端数据同步)
    - [4.1 同步策略](#41-同步策略)
      - [策略选择](#策略选择)
    - [4.2 逻辑复制同步](#42-逻辑复制同步)
      - [边缘节点发布](#边缘节点发布)
      - [云端节点订阅](#云端节点订阅)
      - [双向同步（冲突解决）](#双向同步冲突解决)
    - [4.3 MQTT消息同步](#43-mqtt消息同步)
      - [4.3.1 边缘节点发布](#431-边缘节点发布)
      - [4.3.2 云端节点订阅](#432-云端节点订阅)
  - [5. 离线场景处理](#5-离线场景处理)
    - [5.1 离线数据存储](#51-离线数据存储)
      - [本地队列管理](#本地队列管理)
    - [5.2 数据队列管理](#52-数据队列管理)
      - [队列持久化](#队列持久化)
  - [6. 数据压缩与传输优化](#6-数据压缩与传输优化)
    - [6.1 数据压缩策略](#61-数据压缩策略)
      - [TimescaleDB压缩](#timescaledb压缩)
      - [导出时压缩](#导出时压缩)
    - [6.2 增量传输](#62-增量传输)
      - [基于时间戳的增量同步](#基于时间戳的增量同步)
  - [7. 边缘节点管理](#7-边缘节点管理)
    - [7.1 节点监控](#71-节点监控)
      - [监控指标](#监控指标)
  - [8. 实践案例](#8-实践案例)
    - [8.1 工业IoT边缘计算案例](#81-工业iot边缘计算案例)
      - [场景描述](#场景描述)
  - [📚 参考资源](#-参考资源)
  - [📝 更新日志](#-更新日志)

---

## 1. 边缘计算架构概述

### 1.1 边缘计算概念

边缘计算是一种分布式计算架构，将计算和数据处理能力推向网络的边缘，靠近数据源和用户。

#### 边缘计算的优势

```text
优势:
✅ 低延迟: 本地处理，减少网络延迟（<10ms）
✅ 带宽节省: 边缘过滤和聚合，减少传输数据量（90%+减少）
✅ 离线能力: 网络中断时仍可运行
✅ 隐私保护: 敏感数据本地处理
✅ 成本优化: 减少云端计算和存储成本
```

#### 边缘计算挑战

```text
挑战:
⚠️ 资源受限: CPU、内存、存储有限
⚠️ 网络不稳定: 可能间歇性断网
⚠️ 管理复杂: 分散的节点管理
⚠️ 数据一致性: 边缘和云端数据同步
⚠️ 安全性: 边缘设备安全防护
```

### 1.2 边缘-云架构模式

#### 模式1：边缘预处理 + 云端存储

```text
IoT设备
  ↓
边缘节点（PostgreSQL/TimescaleDB）
  ↓ (预处理、聚合、过滤)
云端中心数据库（PostgreSQL）
  ↓
数据分析与应用
```

#### 模式2：边缘存储 + 云端分析

```text
IoT设备
  ↓
边缘节点（PostgreSQL，完整数据存储）
  ↓ (定期同步)
云端中心数据库（PostgreSQL，备份和分析）
  ↓
大数据分析
```

#### 模式3：混合模式（推荐）

```text
IoT设备
  ↓
边缘节点（PostgreSQL/TimescaleDB）
  ├─ 实时数据（本地存储和处理）
  ├─ 聚合数据（定期同步到云端）
  └─ 告警数据（实时推送）
  ↓
云端中心数据库（PostgreSQL）
  ├─ 历史数据归档
  ├─ 跨节点分析
  └─ 全局视图
```

### 1.3 边缘数据库选型

#### PostgreSQL vs TimescaleDB

| 特性 | PostgreSQL | TimescaleDB |
|------|-----------|-------------|
| **时序数据** | ⚠️ 需要手动分区 | ✅ 自动Hypertable |
| **数据压缩** | ⚠️ 需要扩展 | ✅ 原生压缩 |
| **连续聚合** | ⚠️ 需要物化视图 | ✅ 自动增量聚合 |
| **资源占用** | 中等 | 略高（扩展开销） |
| **适用场景** | 通用场景 | 时序数据密集 |

#### 选择建议

```text
使用PostgreSQL的情况:
- 数据结构复杂（关系型数据为主）
- 需要复杂查询和事务
- 资源非常受限
- 数据不是纯时序数据

使用TimescaleDB的情况:
- 主要是时序数据（传感器、监控数据）
- 需要高频写入
- 需要时间范围查询优化
- 需要数据压缩
```

---

## 2. 边缘数据库部署

### 2.1 边缘节点架构设计

#### 硬件配置建议

```yaml
小型边缘节点:
  CPU: 2-4核
  内存: 4-8GB
  存储: 64-128GB SSD
  网络: 100Mbps

中型边缘节点:
  CPU: 4-8核
  内存: 8-16GB
  存储: 256-512GB SSD
  网络: 1Gbps

大型边缘节点:
  CPU: 8-16核
  内存: 16-32GB
  存储: 512GB-1TB SSD
  网络: 1-10Gbps
```

#### 软件架构

```text
边缘节点软件栈:
┌─────────────────────────────────┐
│  应用层（业务逻辑）                │
├─────────────────────────────────┤
│  数据采集层（MQTT/HTTP/Modbus）   │
├─────────────────────────────────┤
│  数据处理层（流处理、聚合）         │
├─────────────────────────────────┤
│  数据存储层（PostgreSQL/TimescaleDB）│
├─────────────────────────────────┤
│  同步层（逻辑复制/MQTT）           │
├─────────────────────────────────┤
│  操作系统（Linux）                │
└─────────────────────────────────┘
```

### 2.2 PostgreSQL边缘部署

#### 最小化配置

```bash
# PostgreSQL边缘部署配置（资源受限环境）
# postgresql.conf

# 内存配置（4GB总内存）
shared_buffers = 512MB              # 12.5%内存
effective_cache_size = 2GB          # 50%内存
work_mem = 16MB                     # 每个操作
maintenance_work_mem = 128MB        # 维护操作
temp_buffers = 8MB                  # 临时缓冲区

# WAL配置（优化写入）
wal_buffers = 16MB
checkpoint_timeout = 15min          # 减少检查点频率
max_wal_size = 1GB                  # 控制WAL大小
min_wal_size = 256MB

# 连接配置
max_connections = 50                # 边缘节点连接数少
superuser_reserved_connections = 2

# 查询优化
random_page_cost = 1.1              # SSD优化
effective_io_concurrency = 200      # SSD并发

# 日志配置（节省存储）
logging_collector = on
log_destination = 'stderr'
log_min_duration_statement = 1000   # 只记录慢查询（>1秒）
log_rotation_age = 1d               # 每日轮转
log_rotation_size = 100MB           # 最大100MB
```

#### 性能优化

```sql
-- 创建适合边缘环境的索引
-- 使用部分索引减少索引大小
CREATE INDEX idx_sensor_recent ON sensor_data (device_id, time DESC)
WHERE time > NOW() - INTERVAL '7 days';

-- 使用表达式索引优化查询
CREATE INDEX idx_sensor_value_threshold ON sensor_data ((value > 100))
WHERE value > 100;

-- 表分区（PostgreSQL原生）
CREATE TABLE sensor_data (
    id BIGSERIAL,
    device_id TEXT NOT NULL,
    time TIMESTAMPTZ NOT NULL,
    value NUMERIC(10,2),
    PRIMARY KEY (id, time)
) PARTITION BY RANGE (time);

-- 创建月度分区
CREATE TABLE sensor_data_2025_01 PARTITION OF sensor_data
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- 自动创建分区（使用触发器或脚本）
```

### 2.3 TimescaleDB边缘部署

#### 基础配置

```sql
-- 安装TimescaleDB（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = current_user
        AND rolsuper = TRUE
    ) THEN
        RAISE EXCEPTION '当前用户不是超级用户，无法创建扩展';
    END IF;

    CREATE EXTENSION IF NOT EXISTS timescaledb;
    RAISE NOTICE '扩展安装成功: timescaledb';
EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建扩展';
    WHEN undefined_file THEN
        RAISE EXCEPTION '扩展文件不存在，请检查PostgreSQL安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '扩展安装失败: %', SQLERRM;
END $$;

-- 创建时序表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sensor_data') THEN
        DROP TABLE sensor_data;
        RAISE NOTICE '已删除现有表: sensor_data';
    END IF;

    CREATE TABLE sensor_data (
        time TIMESTAMPTZ NOT NULL,
        device_id TEXT NOT NULL,
        sensor_type TEXT NOT NULL,
        value NUMERIC(10,2),
        metadata JSONB
    );

    RAISE NOTICE '表创建成功: sensor_data';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表sensor_data已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 转换为Hypertable（带错误处理）
DO $$
DECLARE
    hypertable_exists BOOLEAN;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sensor_data') THEN
        RAISE EXCEPTION '表sensor_data不存在，请先创建';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'timescaledb'
    ) THEN
        RAISE EXCEPTION 'TimescaleDB扩展未安装，请先安装';
    END IF;

    SELECT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables
        WHERE hypertable_name = 'sensor_data'
    ) INTO hypertable_exists;

    IF NOT hypertable_exists THEN
        PERFORM create_hypertable(
            'sensor_data',
            'time',
            chunk_time_interval => INTERVAL '1 day',  -- 每日一个chunk
            if_not_exists => TRUE
        );
        RAISE NOTICE 'Hypertable创建成功: sensor_data';
    ELSE
        RAISE WARNING 'Hypertable sensor_data已存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表sensor_data不存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION 'create_hypertable函数不存在，请检查TimescaleDB扩展安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建Hypertable失败: %', SQLERRM;
END $$;

-- 创建索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sensor_data') THEN
        RAISE EXCEPTION '表sensor_data不存在，请先创建';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'sensor_data'
        AND indexname = 'idx_sensor_device_time'
    ) THEN
        CREATE INDEX idx_sensor_device_time ON sensor_data (device_id, time DESC);
        RAISE NOTICE '索引创建成功: idx_sensor_device_time';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'sensor_data'
        AND indexname = 'idx_sensor_type'
    ) THEN
        CREATE INDEX idx_sensor_type ON sensor_data (sensor_type, time DESC);
        RAISE NOTICE '索引创建成功: idx_sensor_type';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表sensor_data不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;
```

#### 压缩配置

```sql
-- 启用压缩（7天前的数据，带错误处理）
DO $$
DECLARE
    policy_exists BOOLEAN;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables
        WHERE hypertable_name = 'sensor_data'
    ) THEN
        RAISE EXCEPTION 'Hypertable sensor_data不存在，请先创建';
    END IF;

    SELECT EXISTS (
        SELECT 1 FROM timescaledb_information.jobs
        WHERE hypertable_name = 'sensor_data'
        AND proc_name = 'policy_compression'
    ) INTO policy_exists;

    IF NOT policy_exists THEN
        PERFORM add_compression_policy('sensor_data', INTERVAL '7 days');
        RAISE NOTICE '压缩策略添加成功: sensor_data (7天)';
    ELSE
        RAISE WARNING '压缩策略已存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'Hypertable sensor_data不存在';
    WHEN undefined_function THEN
        RAISE EXCEPTION 'add_compression_policy函数不存在，请检查TimescaleDB扩展安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '添加压缩策略失败: %', SQLERRM;
END $$;

-- 压缩配置（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables
        WHERE hypertable_name = 'sensor_data'
    ) THEN
        RAISE EXCEPTION 'Hypertable sensor_data不存在，请先创建';
    END IF;

    ALTER TABLE sensor_data SET (
        timescaledb.compress,
        timescaledb.compress_segmentby = 'device_id',
        timescaledb.compress_orderby = 'time DESC'
    );

    RAISE NOTICE '压缩配置已设置: sensor_data';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表sensor_data不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '设置压缩配置失败: %', SQLERRM;
END $$;

-- 查看压缩统计（带错误处理和性能测试）
DO $$
DECLARE
    job_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'timescaledb'
    ) THEN
        RAISE WARNING 'TimescaleDB扩展未安装';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO job_count
    FROM timescaledb_information.jobs
    WHERE proc_name = 'policy_compression';

    RAISE NOTICE '找到 % 个压缩策略任务', job_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'timescaledb_information.jobs视图不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询压缩统计失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_compression';
-- 执行时间: <10ms
-- 计划: Seq Scan
```

#### 数据保留策略

```sql
-- 设置数据保留策略（保留30天，带错误处理）
DO $$
DECLARE
    policy_exists BOOLEAN;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables
        WHERE hypertable_name = 'sensor_data'
    ) THEN
        RAISE EXCEPTION 'Hypertable sensor_data不存在，请先创建';
    END IF;

    SELECT EXISTS (
        SELECT 1 FROM timescaledb_information.jobs
        WHERE hypertable_name = 'sensor_data'
        AND proc_name = 'policy_retention'
    ) INTO policy_exists;

    IF NOT policy_exists THEN
        PERFORM add_retention_policy('sensor_data', INTERVAL '30 days');
        RAISE NOTICE '数据保留策略添加成功: sensor_data (30天)';
    ELSE
        RAISE WARNING '数据保留策略已存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION 'Hypertable sensor_data不存在';
    WHEN undefined_function THEN
        RAISE EXCEPTION 'add_retention_policy函数不存在，请检查TimescaleDB扩展安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '添加数据保留策略失败: %', SQLERRM;
END $$;

-- 自定义保留策略（保留不同时间段的数据）
-- 保留最近1小时：原始数据
-- 保留最近1天：1分钟聚合
-- 保留最近7天：5分钟聚合
-- 保留最近30天：1小时聚合
-- 保留1年以上：1天聚合

-- 创建聚合表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables
        WHERE hypertable_name = 'sensor_data'
    ) THEN
        RAISE EXCEPTION 'Hypertable sensor_data不存在，请先创建';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_matviews
        WHERE schemaname = 'public'
        AND matviewname = 'sensor_data_1min'
    ) THEN
        DROP MATERIALIZED VIEW sensor_data_1min;
        RAISE NOTICE '已删除现有物化视图: sensor_data_1min';
    END IF;

    CREATE MATERIALIZED VIEW sensor_data_1min
    WITH (timescaledb.continuous) AS
    SELECT
        time_bucket('1 minute', time) AS bucket,
        device_id,
        sensor_type,
        avg(value) AS avg_value,
        min(value) AS min_value,
        max(value) AS max_value,
        count(*) AS count
    FROM sensor_data
    GROUP BY bucket, device_id, sensor_type;

    RAISE NOTICE '连续聚合视图创建成功: sensor_data_1min';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表sensor_data不存在';
    WHEN undefined_function THEN
        RAISE EXCEPTION 'time_bucket函数不存在，请检查TimescaleDB扩展安装';
    WHEN duplicate_table THEN
        RAISE WARNING '物化视图已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建连续聚合视图失败: %', SQLERRM;
END $$;

-- 设置刷新策略（带错误处理）
DO $$
DECLARE
    policy_exists BOOLEAN;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_matviews
        WHERE schemaname = 'public'
        AND matviewname = 'sensor_data_1min'
    ) THEN
        RAISE EXCEPTION '物化视图sensor_data_1min不存在，请先创建';
    END IF;

    SELECT EXISTS (
        SELECT 1 FROM timescaledb_information.jobs
        WHERE hypertable_name = 'sensor_data_1min'
        AND proc_name = 'policy_refresh_continuous_aggregate'
    ) INTO policy_exists;

    IF NOT policy_exists THEN
        PERFORM add_continuous_aggregate_policy('sensor_data_1min',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute');
```

### 2.4 容器化边缘部署

#### Docker Compose配置

```yaml
# docker-compose.yml (边缘节点)
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg17
    container_name: edge-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: iot_data
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "-E UTF8"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    command:
      - "postgres"
      - "-c"
      - "config_file=/etc/postgresql/postgresql.conf"
    ports:
      - "5432:5432"
    networks:
      - edge-network
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  # MQTT Broker (可选，用于数据采集)
  mosquitto:
    image: eclipse-mosquitto:latest
    container_name: edge-mosquitto
    restart: unless-stopped
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mosquitto-data:/mosquitto/data
    ports:
      - "1883:1883"
    networks:
      - edge-network

  # 数据采集服务
  data-collector:
    image: edge-data-collector:latest
    container_name: edge-data-collector
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/iot_data
      MQTT_BROKER: mosquitto:1883
    depends_on:
      - postgres
      - mosquitto
    networks:
      - edge-network

volumes:
  postgres-data:
  mosquitto-data:

networks:
  edge-network:
    driver: bridge
```

#### Kubernetes边缘部署

```yaml
# edge-postgres.yaml (Kubernetes)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: edge-postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: local-storage  # 边缘节点使用本地存储
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edge-postgres
spec:
  replicas: 1  # 边缘节点通常单实例
  selector:
    matchLabels:
      app: edge-postgres
  template:
    metadata:
      labels:
        app: edge-postgres
    spec:
      containers:
      - name: postgres
        image: timescale/timescaledb:latest-pg17
        env:
        - name: POSTGRES_DB
          value: "iot_data"
        - name: POSTGRES_USER
          value: "postgres"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        - name: postgres-config
          mountPath: /etc/postgresql
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
      volumes:
      - name: postgres-data
        persistentVolumeClaim:
          claimName: edge-postgres-pvc
      - name: postgres-config
        configMap:
          name: postgres-config
---
apiVersion: v1
kind: Service
metadata:
  name: edge-postgres
spec:
  selector:
    app: edge-postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
```

---

## 3. IoT数据采集与处理

### 3.1 IoT数据模型设计

#### 传感器数据模型

```sql
-- 基础传感器数据表
CREATE TABLE sensor_readings (
    id BIGSERIAL,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    device_id TEXT NOT NULL,
    sensor_id TEXT NOT NULL,
    value NUMERIC(12,4),
    unit TEXT,
    quality INTEGER,  -- 数据质量（0-100）
    location GEOGRAPHY(POINT, 4326),
    metadata JSONB,
    PRIMARY KEY (id, time)
);

-- 转换为Hypertable (TimescaleDB)
SELECT create_hypertable('sensor_readings', 'time',
    chunk_time_interval => INTERVAL '1 day');

-- 创建索引
CREATE INDEX idx_sensor_device ON sensor_readings (device_id, time DESC);
CREATE INDEX idx_sensor_location ON sensor_readings USING GIST (location);
CREATE INDEX idx_sensor_quality ON sensor_readings (quality) WHERE quality < 80;

-- 设备元数据表（普通表）
CREATE TABLE devices (
    device_id TEXT PRIMARY KEY,
    device_name TEXT NOT NULL,
    device_type TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    installed_at TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    status TEXT,  -- 'online', 'offline', 'maintenance'
    metadata JSONB
);

-- 传感器配置表
CREATE TABLE sensors (
    sensor_id TEXT PRIMARY KEY,
    device_id TEXT REFERENCES devices(device_id),
    sensor_type TEXT NOT NULL,
    sensor_name TEXT,
    unit TEXT,
    min_value NUMERIC,
    max_value NUMERIC,
    calibration_date TIMESTAMPTZ,
    metadata JSONB
);
```

#### 数据质量保证

```sql
-- 数据验证函数
CREATE OR REPLACE FUNCTION validate_sensor_reading(
    p_device_id TEXT,
    p_sensor_id TEXT,
    p_value NUMERIC
) RETURNS BOOLEAN AS $$
DECLARE
    sensor_config RECORD;
BEGIN
    -- 获取传感器配置
    SELECT * INTO sensor_config
    FROM sensors
    WHERE sensor_id = p_sensor_id AND device_id = p_device_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- 检查值范围
    IF sensor_config.min_value IS NOT NULL AND p_value < sensor_config.min_value THEN
        RETURN FALSE;
    END IF;

    IF sensor_config.max_value IS NOT NULL AND p_value > sensor_config.max_value THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 使用触发器验证数据
CREATE TRIGGER validate_reading
BEFORE INSERT ON sensor_readings
FOR EACH ROW
EXECUTE FUNCTION check_sensor_reading();
```

### 3.2 数据采集模式

#### 模式1：MQTT采集

```python
# MQTT数据采集服务
import paho.mqtt.client as mqtt
import psycopg2
import json
from datetime import datetime

class MQTTDataCollector:
    """MQTT数据采集器"""

    def __init__(self, mqtt_broker, db_conn_string):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.db_conn = psycopg2.connect(db_conn_string)
        self.db_cursor = self.db_conn.cursor()

        self.mqtt_client.connect(mqtt_broker, 1883, 60)

    def on_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        if rc == 0:
            print("Connected to MQTT broker")
            # 订阅传感器数据主题
            client.subscribe("sensors/+/+/data")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        """MQTT消息回调"""
        try:
            topic_parts = msg.topic.split('/')
            device_id = topic_parts[1]
            sensor_id = topic_parts[2]

            # 解析消息
            data = json.loads(msg.payload.decode())
            value = data['value']
            timestamp = datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat()))

            # 插入数据库
            self.insert_sensor_data(device_id, sensor_id, value, timestamp)
        except Exception as e:
            print(f"Error processing message: {e}")

    def insert_sensor_data(self, device_id, sensor_id, value, timestamp):
        """插入传感器数据"""
        # 使用批量插入优化性能
        self.db_cursor.execute("""
            INSERT INTO sensor_readings (time, device_id, sensor_id, value)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (timestamp, device_id, sensor_id, value))

        # 每100条提交一次
        if self.db_cursor.rowcount % 100 == 0:
            self.db_conn.commit()

    def run(self):
        """运行采集服务"""
        self.mqtt_client.loop_forever()
```

#### 模式2：HTTP REST API采集

```python
# HTTP REST API数据采集
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import execute_batch

app = Flask(__name__)

# 数据库连接池
def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        database='iot_data',
        user='postgres',
        password='password'
    )

@app.route('/api/v1/sensors/<device_id>/<sensor_id>/data', methods=['POST'])
def collect_sensor_data(device_id, sensor_id):
    """收集传感器数据"""
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 批量插入
        readings = []
        for reading in data.get('readings', []):
            readings.append((
                reading['timestamp'],
                device_id,
                sensor_id,
                reading['value'],
                reading.get('quality', 100)
            ))

        execute_batch(
            cursor,
            """
            INSERT INTO sensor_readings (time, device_id, sensor_id, value, quality)
            VALUES (%s, %s, %s, %s, %s)
            """,
            readings
        )

        conn.commit()
        return jsonify({'status': 'success', 'count': len(readings)}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
```

### 3.3 边缘数据处理

#### 实时聚合

```sql
-- 创建实时聚合视图（TimescaleDB连续聚合）
CREATE MATERIALIZED VIEW sensor_5min_stats
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS bucket,
    device_id,
    sensor_id,
    COUNT(*) AS count,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value) AS median_value
FROM sensor_readings
GROUP BY bucket, device_id, sensor_id;

-- 自动刷新策略
SELECT add_continuous_aggregate_policy('sensor_5min_stats',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes');
```

#### 异常检测

```sql
-- 异常检测函数（基于统计方法）
CREATE OR REPLACE FUNCTION detect_anomalies(
    p_device_id TEXT,
    p_sensor_id TEXT,
    p_window_hours INTEGER DEFAULT 24
) RETURNS TABLE (
    time TIMESTAMPTZ,
    value NUMERIC,
    z_score NUMERIC,
    is_anomaly BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT
            AVG(value) AS mean,
            STDDEV(value) AS stddev
        FROM sensor_readings
        WHERE device_id = p_device_id
          AND sensor_id = p_sensor_id
          AND time > NOW() - (p_window_hours || ' hours')::INTERVAL
    ),
    readings AS (
        SELECT
            time,
            value,
            (value - stats.mean) / NULLIF(stats.stddev, 0) AS z_score
        FROM sensor_readings, stats
        WHERE device_id = p_device_id
          AND sensor_id = p_sensor_id
          AND time > NOW() - (p_window_hours || ' hours')::INTERVAL
    )
    SELECT
        readings.time,
        readings.value,
        readings.z_score,
        ABS(readings.z_score) > 3 AS is_anomaly  -- Z-score > 3视为异常
    FROM readings;
END;
$$ LANGUAGE plpgsql;
```

---

## 4. 边缘-云端数据同步

### 4.1 同步策略

#### 策略选择

```text
实时同步:
- 适用: 关键数据、告警数据
- 方法: 逻辑复制、MQTT推送
- 延迟: < 1秒
- 成本: 高（持续连接）

批量同步:
- 适用: 历史数据、非关键数据
- 方法: 批量导出/导入
- 延迟: 分钟级
- 成本: 低

混合同步:
- 实时数据: 逻辑复制
- 聚合数据: 批量同步
- 归档数据: 定期同步
```

### 4.2 逻辑复制同步

#### 边缘节点发布

```sql
-- 在边缘节点创建发布
CREATE PUBLICATION edge_publication FOR TABLE sensor_readings;

-- 只发布特定条件的数据（减少同步量）
CREATE PUBLICATION edge_recent_publication FOR TABLE sensor_readings
WHERE (time > NOW() - INTERVAL '7 days');

-- 添加过滤器（只同步关键传感器）
CREATE PUBLICATION edge_critical_publication FOR TABLE sensor_readings
WHERE (device_id IN ('device_001', 'device_002'));
```

#### 云端节点订阅

```sql
-- 在云端节点创建订阅
CREATE SUBSCRIPTION cloud_subscription
CONNECTION 'host=edge-node.example.com port=5432 user=replicator password=secret dbname=iot_data'
PUBLICATION edge_publication
WITH (
    copy_data = false,  -- 不复制现有数据（仅同步新数据）
    create_slot = true,
    enabled = true
);

-- 监控订阅状态
SELECT * FROM pg_stat_subscription;

-- 查看复制延迟
SELECT
    subname,
    pg_wal_lsn_diff(pg_current_wal_lsn(), latest_end_lsn) AS replication_lag_bytes
FROM pg_stat_subscription;
```

#### 双向同步（冲突解决）

```sql
-- 使用Last-Write-Wins策略
CREATE OR REPLACE FUNCTION resolve_conflict(
    edge_value NUMERIC,
    cloud_value NUMERIC,
    edge_time TIMESTAMPTZ,
    cloud_time TIMESTAMPTZ
) RETURNS NUMERIC AS $$
BEGIN
    -- 比较时间戳，返回最新的值
    IF edge_time > cloud_time THEN
        RETURN edge_value;
    ELSE
        RETURN cloud_value;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 使用触发器处理冲突
CREATE OR REPLACE FUNCTION handle_sync_conflict()
RETURNS TRIGGER AS $$
DECLARE
    existing_record RECORD;
BEGIN
    -- 检查是否存在冲突
    SELECT * INTO existing_record
    FROM sensor_readings
    WHERE device_id = NEW.device_id
      AND sensor_id = NEW.sensor_id
      AND time = NEW.time;

    IF FOUND THEN
        -- 解决冲突（使用Last-Write-Wins）
        NEW.value = resolve_conflict(
            NEW.value, existing_record.value,
            NEW.time, existing_record.time
        );
        RETURN NEW;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_conflict_resolver
BEFORE INSERT ON sensor_readings
FOR EACH ROW
EXECUTE FUNCTION handle_sync_conflict();
```

### 4.3 MQTT消息同步

#### 4.3.1 边缘节点发布

```python
# 边缘节点MQTT发布
import paho.mqtt.client as mqtt
import psycopg2
import json

class EdgeSyncPublisher:
    """边缘节点同步发布器"""

    def __init__(self, mqtt_broker, db_conn_string):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(mqtt_broker, 1883, 60)

        self.db_conn = psycopg2.connect(db_conn_string)

    def sync_recent_data(self):
        """同步最近的数据到云端"""
        cursor = self.db_conn.cursor()

        # 获取未同步的数据
        cursor.execute("""
            SELECT device_id, sensor_id, time, value, quality
            FROM sensor_readings
            WHERE sync_status IS NULL
              AND time > NOW() - INTERVAL '1 hour'
            ORDER BY time
            LIMIT 1000
        """)

        for row in cursor.fetchall():
            device_id, sensor_id, time, value, quality = row

            # 发布到MQTT
            topic = f"sync/{device_id}/{sensor_id}"
            payload = json.dumps({
                'time': time.isoformat(),
                'value': float(value),
                'quality': quality
            })

            self.mqtt_client.publish(topic, payload, qos=1)

            # 标记为已同步
            cursor.execute("""
                UPDATE sensor_readings
                SET sync_status = 'synced'
                WHERE device_id = %s AND sensor_id = %s AND time = %s
            """, (device_id, sensor_id, time))

        self.db_conn.commit()
```

#### 4.3.2 云端节点订阅

```python
# 云端节点MQTT订阅
class CloudSyncSubscriber:
    """云端节点同步订阅器"""

    def __init__(self, mqtt_broker, db_conn_string):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.db_conn = psycopg2.connect(db_conn_string)
        self.mqtt_client.connect(mqtt_broker, 1883, 60)

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("sync/+/+/+")

    def on_message(self, client, userdata, msg):
        topic_parts = msg.topic.split('/')
        device_id = topic_parts[1]
        sensor_id = topic_parts[2]

        data = json.loads(msg.payload.decode())

        # 插入到云端数据库
        cursor = self.db_conn.cursor()
        cursor.execute("""
            INSERT INTO sensor_readings (time, device_id, sensor_id, value, quality, source)
            VALUES (%s, %s, %s, %s, %s, 'edge')
            ON CONFLICT (device_id, sensor_id, time) DO UPDATE
            SET value = EXCLUDED.value,
                quality = EXCLUDED.quality
        """, (
            data['time'],
            device_id,
            sensor_id,
            data['value'],
            data['quality']
        ))

        self.db_conn.commit()
```

---

## 5. 离线场景处理

### 5.1 离线数据存储

#### 本地队列管理

```python
# 离线数据队列管理器
import queue
import threading
import psycopg2
from datetime import datetime

class OfflineDataQueue:
    """离线数据队列"""

    def __init__(self, db_conn_string, max_queue_size=10000):
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.db_conn_string = db_conn_string
        self.is_online = False
        self.flush_thread = None

    def start(self):
        """启动队列处理器"""
        self.flush_thread = threading.Thread(target=self._flush_queue, daemon=True)
        self.flush_thread.start()

    def add_data(self, device_id, sensor_id, value, timestamp):
        """添加数据到队列"""
        try:
            self.queue.put_nowait({
                'device_id': device_id,
                'sensor_id': sensor_id,
                'value': value,
                'timestamp': timestamp
            })
        except queue.Full:
            # 队列满，丢弃最旧的数据
            try:
                self.queue.get_nowait()
                self.queue.put_nowait({
                    'device_id': device_id,
                    'sensor_id': sensor_id,
                    'value': value,
                    'timestamp': timestamp
                })
            except queue.Empty:
                pass

    def _flush_queue(self):
        """刷新队列到数据库"""
        batch = []

        while True:
            try:
                # 从队列获取数据
                item = self.queue.get(timeout=1)
                batch.append(item)

                # 批量处理（每100条或1秒）
                if len(batch) >= 100:
                    self._write_batch(batch)
                    batch = []
            except queue.Empty:
                # 队列空，处理剩余批次
                if batch:
                    self._write_batch(batch)
                    batch = []
                continue

    def _write_batch(self, batch):
        """批量写入数据库"""
        if not self.is_online:
            # 离线时，保存到本地文件
            self._save_to_file(batch)
            return

        try:
            conn = psycopg2.connect(self.db_conn_string)
            cursor = conn.cursor()

            values = [
                (item['timestamp'], item['device_id'], item['sensor_id'], item['value'])
                for item in batch
            ]

            execute_batch(
                cursor,
                """
                INSERT INTO sensor_readings (time, device_id, sensor_id, value)
                VALUES (%s, %s, %s, %s)
                """,
                values
            )

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error writing batch: {e}")
            # 写入失败，保存到文件
            self._save_to_file(batch)

    def _save_to_file(self, batch):
        """保存到本地文件（离线模式）"""
        import json
        filename = f"offline_queue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(batch, f)
```

### 5.2 数据队列管理

#### 队列持久化

```sql
-- 使用PostgreSQL表作为持久化队列
CREATE TABLE data_queue (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'processing', 'done', 'failed'
    device_id TEXT NOT NULL,
    sensor_id TEXT NOT NULL,
    time TIMESTAMPTZ NOT NULL,
    value NUMERIC(12,4),
    retry_count INTEGER DEFAULT 0,
    error_message TEXT
);

-- 创建索引
CREATE INDEX idx_queue_status ON data_queue (status, created_at)
WHERE status IN ('pending', 'processing');

-- 获取待处理数据
CREATE OR REPLACE FUNCTION get_pending_queue_items(batch_size INTEGER DEFAULT 100)
RETURNS TABLE (
    id BIGINT,
    device_id TEXT,
    sensor_id TEXT,
    time TIMESTAMPTZ,
    value NUMERIC
) AS $$
BEGIN
    -- 标记为处理中
    UPDATE data_queue
    SET status = 'processing', processed_at = NOW()
    WHERE id IN (
        SELECT id FROM data_queue
        WHERE status = 'pending'
        ORDER BY created_at
        LIMIT batch_size
        FOR UPDATE SKIP LOCKED
    );

    -- 返回处理中的数据
    RETURN QUERY
    SELECT q.id, q.device_id, q.sensor_id, q.time, q.value
    FROM data_queue q
    WHERE q.status = 'processing'
    ORDER BY q.created_at;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. 数据压缩与传输优化

### 6.1 数据压缩策略

#### TimescaleDB压缩

```sql
-- 启用压缩（7天前的数据自动压缩）
SELECT add_compression_policy('sensor_readings', INTERVAL '7 days');

-- 手动压缩
SELECT compress_chunk(chunk) FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_readings'
  AND is_compressed = false
  AND range_end < NOW() - INTERVAL '7 days';

-- 查看压缩效果
SELECT
    hypertable_name,
    total_chunks,
    number_compressed_chunks,
    pg_size_pretty(before_compression_total_bytes) AS before_size,
    pg_size_pretty(after_compression_total_bytes) AS after_size,
    ROUND((1.0 - after_compression_total_bytes::NUMERIC / before_compression_total_bytes) * 100, 2) AS compression_ratio
FROM timescaledb_information.compressed_hypertable_stats;
```

#### 导出时压缩

```bash
# 使用pg_dump压缩导出
pg_dump -h edge-node -U postgres -d iot_data \
  --table=sensor_readings \
  --compress=9 \
  -F c \
  -f sensor_readings_compressed.dump

# 传输压缩文件
scp sensor_readings_compressed.dump cloud-server:/backup/

# 导入
pg_restore -h cloud-server -U postgres -d iot_data \
  -F c \
  sensor_readings_compressed.dump
```

### 6.2 增量传输

#### 基于时间戳的增量同步

```sql
-- 获取需要同步的数据（增量）
CREATE OR REPLACE FUNCTION get_incremental_data(
    p_last_sync_time TIMESTAMPTZ,
    p_batch_size INTEGER DEFAULT 1000
) RETURNS TABLE (
    device_id TEXT,
    sensor_id TEXT,
    time TIMESTAMPTZ,
    value NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.device_id, r.sensor_id, r.time, r.value
    FROM sensor_readings r
    WHERE r.time > p_last_sync_time
      AND r.sync_status IS NULL
    ORDER BY r.time
    LIMIT p_batch_size;
END;
$$ LANGUAGE plpgsql;

-- 标记已同步
CREATE OR REPLACE FUNCTION mark_as_synced(
    p_device_id TEXT,
    p_sensor_id TEXT,
    p_time TIMESTAMPTZ
) RETURNS void AS $$
BEGIN
    UPDATE sensor_readings
    SET sync_status = 'synced',
        sync_time = NOW()
    WHERE device_id = p_device_id
      AND sensor_id = p_sensor_id
      AND time = p_time;
END;
$$ LANGUAGE plpgsql;
```

---

## 7. 边缘节点管理

### 7.1 节点监控

#### 监控指标

```python
# 边缘节点监控
import psycopg2
import time
from datetime import datetime

class EdgeNodeMonitor:
    """边缘节点监控器"""

    def __init__(self, db_conn_string):
        self.db_conn_string = db_conn_string

    def get_node_health(self):
        """获取节点健康状态"""
        conn = psycopg2.connect(self.db_conn_string)
        cursor = conn.cursor()

        health = {
            'timestamp': datetime.utcnow().isoformat(),
            'database': {},
            'data': {},
            'sync': {}
        }

        # 数据库状态
        cursor.execute("SELECT version();")
        health['database']['version'] = cursor.fetchone()[0]

        cursor.execute("SELECT pg_database_size(current_database());")
        health['database']['size_bytes'] = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM pg_stat_activity;")
        health['database']['connections'] = cursor.fetchone()[0]

        # 数据统计
        cursor.execute("""
            SELECT
                COUNT(*) as total_readings,
                COUNT(DISTINCT device_id) as device_count,
                MAX(time) as latest_reading,
                MIN(time) as earliest_reading
            FROM sensor_readings
        """)
        row = cursor.fetchone()
        health['data'] = {
            'total_readings': row[0],
            'device_count': row[1],
            'latest_reading': row[2].isoformat() if row[2] else None,
            'earliest_reading': row[3].isoformat() if row[3] else None
        }

        # 同步状态
        cursor.execute("""
            SELECT
                COUNT(*) FILTER (WHERE sync_status IS NULL) as unsynced_count,
                COUNT(*) FILTER (WHERE sync_status = 'synced') as synced_count,
                MAX(sync_time) as last_sync_time
            FROM sensor_readings
        """)
        row = cursor.fetchone()
        health['sync'] = {
            'unsynced_count': row[0],
            'synced_count': row[1],
            'last_sync_time': row[2].isoformat() if row[2] else None
        }

        cursor.close()
        conn.close()

        return health
```

---

## 8. 实践案例

### 8.1 工业IoT边缘计算案例

#### 场景描述

```text
场景: 制造工厂IoT监控系统

需求:
- 1000+传感器设备
- 每秒10,000+数据点
- 边缘处理：实时告警、本地存储
- 云端分析：历史数据分析、预测维护

架构:
┌─────────────────┐
│  传感器设备      │ (Modbus/OPC-UA)
└────────┬────────┘
         ↓
┌─────────────────┐
│  边缘网关        │ (Raspberry Pi / 工控机)
│  - MQTT Broker  │
│  - 数据采集服务   │
└────────┬────────┘
         ↓
┌─────────────────┐
│  边缘数据库      │ (TimescaleDB on 边缘服务器)
│  - 实时数据存储   │
│  - 实时聚合      │
│  - 异常检测      │
└────────┬────────┘
         ↓ (逻辑复制 + MQTT)
┌─────────────────┐
│  云端数据库      │ (PostgreSQL集群)
│  - 历史数据归档   │
│  - 跨工厂分析     │
│  - 预测分析      │
└─────────────────┘
```

---

## 📚 参考资源

1. **TimescaleDB官方文档**: <https://docs.timescale.com/>
2. **PostgreSQL逻辑复制**: <https://www.postgresql.org/docs/current/logical-replication.html>
3. **MQTT协议**: <https://mqtt.org/>

---

## 📝 更新日志

- **v1.0** (2025-01): 初始版本
  - 边缘计算架构概述
  - 边缘数据库部署
  - IoT数据采集与处理
  - 边缘-云端数据同步
  - 离线场景处理
  - 数据压缩与传输优化
  - 边缘节点管理
  - 实践案例

---

**状态**: ✅ **文档完成** | [返回目录](./README.md)
