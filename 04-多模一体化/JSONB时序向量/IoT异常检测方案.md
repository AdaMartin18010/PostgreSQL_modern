# IoT 异常检测方案

> **更新时间**: 2025 年 11 月 1 日  
> **技术版本**: PostgreSQL 18+ / TimescaleDB 2.13+ / pgvector 0.7.0+  
> **文档编号**: 04-02-02

## 📑 目录

- [IoT 异常检测方案](#iot-异常检测方案)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. 检测方案](#2-检测方案)
    - [2.1 检测流程](#21-检测流程)
    - [2.2 异常模式库](#22-异常模式库)
  - [3. 实现细节](#3-实现细节)
    - [3.1 实时检测](#31-实时检测)
    - [3.2 批量检测](#32-批量检测)
  - [4. 性能优化](#4-性能优化)
    - [4.1 索引优化](#41-索引优化)
    - [4.2 查询优化](#42-查询优化)
  - [5. 最佳实践](#5-最佳实践)
  - [6. 参考资料](#6-参考资料)

---

## 1. 概述

IoT 异常检测方案结合时序数据、JSONB 元数据和向量相似度，实现高效的异常检测。

---

## 2. 检测方案

### 2.1 检测流程

```text
传感器数据采集
    │
    ▼
数据存储（时序 + JSONB + 向量）
    │
    ▼
异常模式匹配（向量相似度）
    │
    ▼
异常告警
```

### 2.2 异常模式库

```sql
-- 创建异常模式表
CREATE TABLE anomaly_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type TEXT NOT NULL,
    description TEXT,
    pattern_vector vector(64) NOT NULL,
    threshold FLOAT DEFAULT 0.7,
    severity TEXT,  -- 'low', 'medium', 'high', 'critical'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建向量索引
CREATE INDEX ON anomaly_patterns
USING hnsw (pattern_vector vector_cosine_ops);
```

---

## 3. 实现细节

### 3.1 实时检测

```sql
-- 实时异常检测函数
CREATE OR REPLACE FUNCTION detect_anomalies(
    device_id_param TEXT,
    time_window INTERVAL DEFAULT '1 hour'
)
RETURNS TABLE (
    device_id TEXT,
    time TIMESTAMPTZ,
    metric_type TEXT,
    value DOUBLE PRECISION,
    anomaly_type TEXT,
    anomaly_score FLOAT,
    severity TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH recent_data AS (
        SELECT *
        FROM device_data
        WHERE device_data.device_id = device_id_param
          AND device_data.time > NOW() - time_window
    ),
    anomaly_detection AS (
        SELECT
            r.device_id,
            r.time,
            r.metric_type,
            r.value,
            a.pattern_type as anomaly_type,
            r.anomaly_vector <=> a.pattern_vector as anomaly_score,
            a.severity
        FROM recent_data r
        CROSS JOIN anomaly_patterns a
        WHERE r.anomaly_vector <=> a.pattern_vector < a.threshold
    )
    SELECT DISTINCT ON (device_id, time, metric_type)
        device_id,
        time,
        metric_type,
        value,
        anomaly_type,
        anomaly_score,
        severity
    FROM anomaly_detection
    ORDER BY device_id, time, metric_type, anomaly_score;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 批量检测

```python
def batch_anomaly_detection(device_ids, time_window='1 hour'):
    """批量异常检测"""
    results = []

    for device_id in device_ids:
        query = """
            SELECT * FROM detect_anomalies($1, $2)
        """
        result = conn.execute(query, (device_id, time_window))
        results.extend(result)

    return results
```

---

## 4. 性能优化

### 4.1 索引优化

```sql
-- 优化查询索引
CREATE INDEX ON device_data (device_id, time DESC)
INCLUDE (anomaly_vector);

-- 部分索引（只索引异常数据）
CREATE INDEX ON device_data (device_id, time)
WHERE anomaly_vector IS NOT NULL;
```

### 4.2 查询优化

```sql
-- 使用物化视图预计算
CREATE MATERIALIZED VIEW device_anomaly_summary AS
SELECT
    device_id,
    DATE_TRUNC('hour', time) as hour,
    COUNT(*) as anomaly_count,
    AVG(anomaly_score) as avg_score
FROM detect_anomalies('device_001', '24 hours')
GROUP BY device_id, hour;
```

---

## 5. 最佳实践

1. **模式库管理**: 定期更新异常模式库
1. **阈值调优**: 根据实际情况调整检测阈值
1. **性能监控**: 监控检测性能，优化慢查询
1. **告警策略**: 设置合理的告警策略，避免告警风暴

---

## 6. 参考资料

- [混合数据模型设计](./混合数据模型设计.md)
- [性能优化策略](./性能优化策略.md)

---

**最后更新**: 2025 年 11 月 1 日  
**维护者**: PostgreSQL Modern Team
