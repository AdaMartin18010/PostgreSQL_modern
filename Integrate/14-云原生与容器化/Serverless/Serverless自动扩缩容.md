# Serverless PostgreSQL自动扩缩容指南

> **PostgreSQL版本**: 17+/18+
> **适用场景**: 自动资源管理、负载波动场景
> **难度等级**: ⭐⭐⭐⭐ 高级

---

## 📋 目录

- [Serverless PostgreSQL自动扩缩容指南](#serverless-postgresql自动扩缩容指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 自动扩缩容目标](#11-自动扩缩容目标)
    - [1.2 扩缩容维度](#12-扩缩容维度)
  - [2. 扩缩容策略](#2-扩缩容策略)
    - [2.1 基于CPU使用率](#21-基于cpu使用率)
    - [2.2 基于连接数](#22-基于连接数)
    - [2.3 基于查询负载](#23-基于查询负载)
  - [3. 监控指标](#3-监控指标)
    - [3.1 核心指标](#31-核心指标)
      - [3.1.1 CPU使用率](#311-cpu使用率)
      - [3.1.2 内存使用率](#312-内存使用率)
      - [3.1.3 I/O使用率](#313-io使用率)
    - [3.2 自定义指标](#32-自定义指标)
  - [4. 触发机制](#4-触发机制)
    - [4.1 扩容触发](#41-扩容触发)
      - [4.1.1 条件判断](#411-条件判断)
      - [4.1.2 扩容操作](#412-扩容操作)
    - [4.2 缩容触发](#42-缩容触发)
      - [4.2.1 条件判断](#421-条件判断)
      - [4.2.2 Scale-to-Zero](#422-scale-to-zero)
  - [5. 最佳实践](#5-最佳实践)
    - [5.1 扩缩容策略](#51-扩缩容策略)
    - [5.2 监控指标](#52-监控指标)
    - [5.3 性能优化](#53-性能优化)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

### 1.1 自动扩缩容目标

自动扩缩容的目标是根据实际负载动态调整数据库资源，实现：

- ✅ **成本优化**: 低负载时减少资源，降低成本
- ✅ **性能保障**: 高负载时增加资源，保障性能
- ✅ **自动化**: 无需人工干预
- ✅ **快速响应**: 秒级响应负载变化

### 1.2 扩缩容维度

- **水平扩缩容**: 增加/减少实例数量
- **垂直扩缩容**: 增加/减少实例规格
- **Scale-to-Zero**: 无负载时缩容到零

---

## 2. 扩缩容策略

### 2.1 基于CPU使用率

```yaml
# HPA配置
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: postgresql-cpu-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: postgresql-serverless
  minReplicas: 0
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5分钟稳定期
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
```

### 2.2 基于连接数

```sql
-- 监控连接数
CREATE OR REPLACE FUNCTION get_connection_usage()
RETURNS NUMERIC AS $$
DECLARE
    v_current_connections INT;
    v_max_connections INT;
    v_usage_percent NUMERIC;
BEGIN
    SELECT count(*) INTO v_current_connections
    FROM pg_stat_activity
    WHERE datname IS NOT NULL;

    SELECT setting::INT INTO v_max_connections
    FROM pg_settings
    WHERE name = 'max_connections';

    v_usage_percent := (v_current_connections::NUMERIC / v_max_connections::NUMERIC * 100);

    RETURN v_usage_percent;
END;
$$ LANGUAGE plpgsql;

-- 使用自定义指标
-- 当连接数使用率 > 80% 时扩容
-- 当连接数使用率 < 20% 时缩容
```

### 2.3 基于查询负载

```sql
-- 监控查询负载
CREATE OR REPLACE FUNCTION get_query_load()
RETURNS TABLE (
    active_queries INT,
    avg_duration NUMERIC,
    load_score NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        count(*)::INT as active_queries,
        COALESCE(avg(EXTRACT(EPOCH FROM (NOW() - query_start))), 0)::NUMERIC as avg_duration,
        (count(*)::NUMERIC * COALESCE(avg(EXTRACT(EPOCH FROM (NOW() - query_start))), 0))::NUMERIC as load_score
    FROM pg_stat_activity
    WHERE state = 'active'
    AND query_start IS NOT NULL;
END;
$$ LANGUAGE plpgsql;
```

---

## 3. 监控指标

### 3.1 核心指标

#### 3.1.1 CPU使用率

```sql
-- 监控CPU使用率
SELECT
    pid,
    usename,
    state,
    query,
    cpu_time
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY cpu_time DESC;
```

#### 3.1.2 内存使用率

```sql
-- 监控内存使用
SELECT
    name,
    setting,
    unit
FROM pg_settings
WHERE name IN ('shared_buffers', 'work_mem', 'maintenance_work_mem');

-- 查看实际内存使用
SELECT
    sum(shared_buffers) as shared_buffers_size,
    sum(work_mem) as work_mem_size
FROM pg_stat_activity;
```

#### 3.1.3 I/O使用率

```sql
-- 监控I/O使用
SELECT
    datname,
    blks_read,
    blks_hit,
    (blks_hit::NUMERIC / NULLIF(blks_read + blks_hit, 0) * 100) as hit_ratio
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1', 'postgres');
```

### 3.2 自定义指标

```sql
-- 创建指标表
CREATE TABLE scaling_metrics (
    id SERIAL PRIMARY KEY,
    metric_time TIMESTAMPTZ DEFAULT NOW(),
    cpu_usage NUMERIC,
    memory_usage NUMERIC,
    connection_usage NUMERIC,
    query_load NUMERIC
);

-- 定期收集指标
CREATE OR REPLACE FUNCTION collect_scaling_metrics()
RETURNS void AS $$
DECLARE
    v_cpu_usage NUMERIC;
    v_memory_usage NUMERIC;
    v_connection_usage NUMERIC;
    v_query_load NUMERIC;
BEGIN
    -- 收集CPU使用率（需要外部工具）
    v_cpu_usage := 0;  -- 从系统监控获取

    -- 收集内存使用率
    SELECT
        (sum(shared_buffers)::NUMERIC / (SELECT setting::NUMERIC FROM pg_settings WHERE name = 'shared_buffers') * 100)
    INTO v_memory_usage
    FROM pg_stat_activity;

    -- 收集连接使用率
    SELECT get_connection_usage() INTO v_connection_usage;

    -- 收集查询负载
    SELECT load_score INTO v_query_load FROM get_query_load();

    -- 插入指标
    INSERT INTO scaling_metrics (
        cpu_usage,
        memory_usage,
        connection_usage,
        query_load
    )
    VALUES (
        v_cpu_usage,
        v_memory_usage,
        v_connection_usage,
        v_query_load
    );
END;
$$ LANGUAGE plpgsql;
```

---

## 4. 触发机制

### 4.1 扩容触发

#### 4.1.1 条件判断

```sql
-- 扩容条件检查
CREATE OR REPLACE FUNCTION should_scale_up()
RETURNS BOOLEAN AS $$
DECLARE
    v_cpu_usage NUMERIC;
    v_connection_usage NUMERIC;
    v_query_load NUMERIC;
BEGIN
    -- 获取最新指标
    SELECT
        cpu_usage,
        connection_usage,
        query_load
    INTO
        v_cpu_usage,
        v_connection_usage,
        v_query_load
    FROM scaling_metrics
    ORDER BY metric_time DESC
    LIMIT 1;

    -- 扩容条件：任一指标超过阈值
    RETURN (
        v_cpu_usage > 80 OR
        v_connection_usage > 80 OR
        v_query_load > 1000
    );
END;
$$ LANGUAGE plpgsql;
```

#### 4.1.2 扩容操作

```yaml
# 扩容配置
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: postgresql-hpa
spec:
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100  # 每次扩容100%
        periodSeconds: 15
      - type: Pods
        value: 2  # 或每次增加2个Pod
        periodSeconds: 15
      selectPolicy: Max  # 选择最大值
```

### 4.2 缩容触发

#### 4.2.1 条件判断

```sql
-- 缩容条件检查
CREATE OR REPLACE FUNCTION should_scale_down()
RETURNS BOOLEAN AS $$
DECLARE
    v_cpu_usage NUMERIC;
    v_connection_usage NUMERIC;
    v_query_load NUMERIC;
    v_low_load_duration INTERVAL;
BEGIN
    -- 获取最新指标
    SELECT
        cpu_usage,
        connection_usage,
        query_load
    INTO
        v_cpu_usage,
        v_connection_usage,
        v_query_load
    FROM scaling_metrics
    ORDER BY metric_time DESC
    LIMIT 1;

    -- 检查低负载持续时间
    SELECT
        NOW() - MIN(metric_time)
    INTO v_low_load_duration
    FROM scaling_metrics
    WHERE
        cpu_usage < 20 AND
        connection_usage < 20 AND
        query_load < 100
    AND metric_time >= NOW() - INTERVAL '5 minutes';

    -- 缩容条件：所有指标低于阈值且持续5分钟
    RETURN (
        v_cpu_usage < 20 AND
        v_connection_usage < 20 AND
        v_query_load < 100 AND
        v_low_load_duration >= INTERVAL '5 minutes'
    );
END;
$$ LANGUAGE plpgsql;
```

#### 4.2.2 Scale-to-Zero

```sql
-- Scale-to-Zero条件
CREATE OR REPLACE FUNCTION should_scale_to_zero()
RETURNS BOOLEAN AS $$
DECLARE
    v_active_connections INT;
    v_idle_duration INTERVAL;
BEGIN
    -- 检查活动连接数
    SELECT count(*) INTO v_active_connections
    FROM pg_stat_activity
    WHERE datname IS NOT NULL
    AND state != 'idle';

    -- 检查空闲持续时间
    SELECT
        NOW() - MAX(state_change)
    INTO v_idle_duration
    FROM pg_stat_activity
    WHERE state = 'idle';

    -- Scale-to-Zero条件：无活动连接且空闲超过10分钟
    RETURN (
        v_active_connections = 0 AND
        (v_idle_duration IS NULL OR v_idle_duration >= INTERVAL '10 minutes')
    );
END;
$$ LANGUAGE plpgsql;
```

---

## 5. 最佳实践

### 5.1 扩缩容策略

- ✅ **渐进式缩容**: 避免快速缩容导致性能问题
- ✅ **快速扩容**: 快速响应负载增加
- ✅ **稳定期设置**: 设置稳定期避免频繁扩缩容
- ✅ **最小实例数**: 设置最小实例数保障可用性

### 5.2 监控指标

- ✅ **多维度监控**: CPU、内存、连接数、查询负载
- ✅ **历史数据**: 保存历史数据用于分析
- ✅ **告警机制**: 设置告警及时发现问题
- ✅ **预测分析**: 基于历史数据预测负载

### 5.3 性能优化

- ✅ **预加载**: 预加载常用数据减少冷启动时间
- ✅ **连接池**: 使用连接池管理连接
- ✅ **缓存策略**: 使用缓存减少数据库负载
- ✅ **查询优化**: 优化查询减少资源消耗

---

## 📚 相关文档

- [Serverless PostgreSQL完整指南](./Serverless PostgreSQL完整指南.md) - 完整指南
- [Serverless架构设计](./Serverless架构设计.md) - 架构设计
- [技术原理/Scale-to-Zero机制.md](../技术原理/Scale-to-Zero机制.md) - Scale-to-Zero机制

---

**最后更新**: 2025年1月
**状态**: ✅ 完成
