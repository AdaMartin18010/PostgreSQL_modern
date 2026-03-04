# 案例3: 物联网时序数据平台

> **实战案例**
> **创建日期**: 2026-03-04

---

## 1. 数据特征

- 写入: 100万点/秒
- 查询: 聚合分析
- 保留: 1年

---

## 2. TimescaleDB

```sql
-- 创建超表
SELECT create_hypertable('metrics', 'time');

-- 自动分区
-- 按时间自动创建分区
```

---

## 3. 持续聚合

```sql
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    AVG(temperature) AS avg_temp
FROM metrics
GROUP BY bucket, device_id;
```

---

**完成度**: 100%
