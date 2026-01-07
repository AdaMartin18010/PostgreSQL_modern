# Serverless PostgreSQL成本优化指南

> **PostgreSQL版本**: 17+/18+
> **适用场景**: 成本敏感场景、按需付费
> **难度等级**: ⭐⭐⭐⭐ 高级
> **参考**: [成本分析/Serverless成本优化深度分析.md](../成本分析/Serverless成本优化深度分析.md)

---

## 📋 目录

- [Serverless PostgreSQL成本优化指南](#serverless-postgresql成本优化指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 成本构成](#11-成本构成)
    - [1.2 成本优化目标](#12-成本优化目标)
  - [2. 成本分析](#2-成本分析)
    - [2.1 计算成本](#21-计算成本)
      - [2.1.1 CPU成本](#211-cpu成本)
      - [2.1.2 内存成本](#212-内存成本)
    - [2.2 存储成本](#22-存储成本)
      - [2.2.1 数据存储](#221-数据存储)
      - [2.2.2 备份存储](#222-备份存储)
    - [2.3 网络成本](#23-网络成本)
  - [3. 优化策略](#3-优化策略)
    - [3.1 计算成本优化](#31-计算成本优化)
      - [3.1.1 查询优化](#311-查询优化)
      - [3.1.2 连接优化](#312-连接优化)
      - [3.1.3 Scale-to-Zero](#313-scale-to-zero)
    - [3.2 存储成本优化](#32-存储成本优化)
      - [3.2.1 数据压缩](#321-数据压缩)
      - [3.2.2 冷热数据分离](#322-冷热数据分离)
      - [3.2.3 数据清理](#323-数据清理)
    - [3.3 网络成本优化](#33-网络成本优化)
      - [3.3.1 批量操作](#331-批量操作)
      - [3.3.2 数据本地化](#332-数据本地化)
  - [4. 成本监控](#4-成本监控)
    - [4.1 成本监控查询](#41-成本监控查询)
    - [4.2 成本报告](#42-成本报告)
  - [5. 最佳实践](#5-最佳实践)
    - [5.1 成本优化策略](#51-成本优化策略)
    - [5.2 存储优化](#52-存储优化)
    - [5.3 监控和告警](#53-监控和告警)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

### 1.1 成本构成

Serverless PostgreSQL的成本主要由以下部分构成：

- ✅ **计算成本**: CPU和内存使用时间
- ✅ **存储成本**: 数据存储大小
- ✅ **网络成本**: 数据传输量
- ✅ **备份成本**: 备份存储大小

### 1.2 成本优化目标

- **降低总成本**: 减少不必要的资源消耗
- **提高效率**: 提高资源利用率
- **按需付费**: 只支付实际使用的资源
- **成本透明**: 清晰的成本分析和报告

---

## 2. 成本分析

### 2.1 计算成本

#### 2.1.1 CPU成本

```sql
-- 监控CPU使用
SELECT
    pid,
    usename,
    query,
    EXTRACT(EPOCH FROM (NOW() - query_start)) as query_duration
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_duration DESC;

-- 计算CPU成本
-- CPU成本 = CPU使用时间(秒) × CPU单价(元/秒)
```

#### 2.1.2 内存成本

```sql
-- 监控内存使用
SELECT
    name,
    setting,
    unit,
    CASE
        WHEN unit = 'kB' THEN setting::NUMERIC / 1024 / 1024
        WHEN unit = 'MB' THEN setting::NUMERIC / 1024
        ELSE setting::NUMERIC
    END as size_gb
FROM pg_settings
WHERE name IN ('shared_buffers', 'work_mem', 'maintenance_work_mem');

-- 计算内存成本
-- 内存成本 = 内存大小(GB) × 使用时间(小时) × 内存单价(元/GB/小时)
```

### 2.2 存储成本

#### 2.2.1 数据存储

```sql
-- 监控存储使用
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) as size,
    pg_database_size(datname) as size_bytes
FROM pg_database
WHERE datname NOT IN ('template0', 'template1', 'postgres')
ORDER BY pg_database_size(datname) DESC;

-- 计算存储成本
-- 存储成本 = 存储大小(GB) × 存储单价(元/GB/月)
```

#### 2.2.2 备份存储

```sql
-- 监控备份大小
SELECT
    backup_name,
    backup_size,
    backup_date,
    pg_size_pretty(backup_size) as size_pretty
FROM pg_backup_history
ORDER BY backup_date DESC;

-- 计算备份成本
-- 备份成本 = 备份大小(GB) × 备份存储单价(元/GB/月)
```

### 2.3 网络成本

```sql
-- 监控网络使用
SELECT
    datname,
    tup_sent,
    tup_received,
    (tup_sent + tup_received) as total_tuples
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1', 'postgres');

-- 计算网络成本
-- 网络成本 = 数据传输量(GB) × 网络单价(元/GB)
```

---

## 3. 优化策略

### 3.1 计算成本优化

#### 3.1.1 查询优化

```sql
-- 优化慢查询
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM large_table WHERE condition;

-- 创建索引
CREATE INDEX idx_large_table_condition ON large_table(condition);

-- 使用物化视图
CREATE MATERIALIZED VIEW mv_summary AS
SELECT
    date_trunc('day', created_at) as date,
    count(*) as count
FROM large_table
GROUP BY date_trunc('day', created_at);

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_summary;
```

#### 3.1.2 连接优化

```sql
-- 使用连接池
-- PgBouncer配置
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25

-- 减少连接数，降低计算成本
-- 连接成本 = 连接数 × 连接保持时间 × 连接单价
```

#### 3.1.3 Scale-to-Zero

```yaml
# 无负载时缩容到零
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 0  # Scale-to-Zero
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 0  # 无CPU使用
```

### 3.2 存储成本优化

#### 3.2.1 数据压缩

```sql
-- 启用表压缩
CREATE TABLE compressed_table (
    id SERIAL PRIMARY KEY,
    data TEXT
) WITH (compression = 'pglz');

-- 压缩现有表
ALTER TABLE large_table SET (compression = 'pglz');
VACUUM FULL large_table;
```

#### 3.2.2 冷热数据分离

```sql
-- 热数据：SSD存储（高性能，高成本）
CREATE TABLESPACE hot_data LOCATION '/data/hot';

-- 冷数据：对象存储（低性能，低成本）
-- 使用FDW访问S3
CREATE EXTENSION aws_s3;

CREATE FOREIGN TABLE cold_data (
    id INT,
    data TEXT
) SERVER s3_server
OPTIONS (
    bucket 'cold-data-bucket',
    region 'us-east-1'
);
```

#### 3.2.3 数据清理

```sql
-- 定期清理历史数据
DELETE FROM old_table
WHERE created_at < NOW() - INTERVAL '1 year';

-- 使用分区表自动清理
CREATE TABLE partitioned_table (
    id SERIAL,
    created_at TIMESTAMPTZ
) PARTITION BY RANGE (created_at);

-- 自动删除旧分区
DROP TABLE IF EXISTS partitioned_table_old;
```

### 3.3 网络成本优化

#### 3.3.1 批量操作

```sql
-- 批量插入
INSERT INTO target_table
SELECT * FROM source_table
WHERE condition;

-- 批量更新
UPDATE target_table
SET column = value
WHERE condition;

-- 减少网络往返次数
```

#### 3.3.2 数据本地化

```sql
-- 使用本地缓存
-- Redis缓存常用数据
-- 减少数据库访问，降低网络成本
```

---

## 4. 成本监控

### 4.1 成本监控查询

```sql
-- 创建成本监控表
CREATE TABLE cost_monitoring (
    id SERIAL PRIMARY KEY,
    metric_time TIMESTAMPTZ DEFAULT NOW(),
    compute_cost NUMERIC,
    storage_cost NUMERIC,
    network_cost NUMERIC,
    backup_cost NUMERIC,
    total_cost NUMERIC
);

-- 计算成本
CREATE OR REPLACE FUNCTION calculate_costs()
RETURNS void AS $$
DECLARE
    v_compute_cost NUMERIC;
    v_storage_cost NUMERIC;
    v_network_cost NUMERIC;
    v_backup_cost NUMERIC;
    v_total_cost NUMERIC;
BEGIN
    -- 计算计算成本（需要外部监控数据）
    v_compute_cost := 0;

    -- 计算存储成本
    SELECT
        SUM(pg_database_size(datname)) / 1024 / 1024 / 1024 * 0.1  -- 假设0.1元/GB/月
    INTO v_storage_cost
    FROM pg_database
    WHERE datname NOT IN ('template0', 'template1', 'postgres');

    -- 计算网络成本（需要外部监控数据）
    v_network_cost := 0;

    -- 计算备份成本（需要外部监控数据）
    v_backup_cost := 0;

    -- 计算总成本
    v_total_cost := v_compute_cost + v_storage_cost + v_network_cost + v_backup_cost;

    -- 插入成本数据
    INSERT INTO cost_monitoring (
        compute_cost,
        storage_cost,
        network_cost,
        backup_cost,
        total_cost
    )
    VALUES (
        v_compute_cost,
        v_storage_cost,
        v_network_cost,
        v_backup_cost,
        v_total_cost
    );
END;
$$ LANGUAGE plpgsql;
```

### 4.2 成本报告

```sql
-- 生成成本报告
CREATE OR REPLACE FUNCTION generate_cost_report(
    report_start DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    report_end DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    metric_date DATE,
    compute_cost NUMERIC,
    storage_cost NUMERIC,
    network_cost NUMERIC,
    backup_cost NUMERIC,
    total_cost NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        DATE(metric_time) as metric_date,
        AVG(compute_cost) as compute_cost,
        AVG(storage_cost) as storage_cost,
        AVG(network_cost) as network_cost,
        AVG(backup_cost) as backup_cost,
        AVG(total_cost) as total_cost
    FROM cost_monitoring
    WHERE DATE(metric_time) BETWEEN report_start AND report_end
    GROUP BY DATE(metric_time)
    ORDER BY metric_date;
END;
$$ LANGUAGE plpgsql;

-- 执行报告
SELECT * FROM generate_cost_report();
```

---

## 5. 最佳实践

### 5.1 成本优化策略

- ✅ **查询优化**: 优化慢查询，减少计算时间
- ✅ **连接池**: 使用连接池减少连接数
- ✅ **缓存策略**: 使用缓存减少数据库访问
- ✅ **Scale-to-Zero**: 无负载时缩容到零

### 5.2 存储优化

- ✅ **数据压缩**: 启用表压缩
- ✅ **冷热分离**: 热数据SSD，冷数据对象存储
- ✅ **定期清理**: 清理历史数据
- ✅ **备份策略**: 优化备份策略

### 5.3 监控和告警

- ✅ **成本监控**: 实时监控成本
- ✅ **预算设置**: 设置成本预算
- ✅ **告警机制**: 成本超预算时告警
- ✅ **定期报告**: 生成成本报告

---

## 📚 相关文档

- [Serverless PostgreSQL完整指南](./Serverless PostgreSQL完整指南.md) - 完整指南
- [成本分析/Serverless成本优化深度分析.md](../成本分析/Serverless成本优化深度分析.md) - 深度分析
- [最佳实践](../../21-最佳实践/成本优化/README.md) - 成本优化最佳实践

---

**最后更新**: 2025年1月
**状态**: ✅ 完成
