# HTAP 混合负载架构

> Hybrid Transaction/Analytical Processing - 事务与分析混合处理架构

## 📋 目录

- [HTAP 混合负载架构](#htap-混合负载架构)
  - [📋 目录](#-目录)
  - [1. HTAP 概述](#1-htap-概述)
    - [1.1 什么是 HTAP](#11-什么是-htap)
    - [1.2 HTAP 的挑战](#12-htap-的挑战)
  - [2. 行列混合存储](#2-行列混合存储)
    - [2.1 行存储 vs 列存储](#21-行存储-vs-列存储)
    - [2.2 PostgreSQL 列存储方案](#22-postgresql-列存储方案)
    - [2.3 混合存储策略](#23-混合存储策略)
  - [3. 实时物化视图](#3-实时物化视图)
    - [3.1 标准物化视图](#31-标准物化视图)
    - [3.2 增量刷新物化视图](#32-增量刷新物化视图)
    - [3.3 TimescaleDB 连续聚合](#33-timescaledb-连续聚合)
  - [4. 冷热分层](#4-冷热分层)
    - [4.1 时间分区策略](#41-时间分区策略)
    - [4.2 自动分层管理](#42-自动分层管理)
    - [4.3 分层压缩](#43-分层压缩)
  - [5. 资源隔离](#5-资源隔离)
    - [5.1 连接池分离](#51-连接池分离)
    - [5.2 资源组管理](#52-资源组管理)
    - [5.3 查询优先级](#53-查询优先级)
    - [5.4 语句超时](#54-语句超时)
  - [6. PostgreSQL HTAP 实现](#6-postgresql-htap-实现)
    - [6.1 读写分离](#61-读写分离)
    - [6.2 智能路由](#62-智能路由)
  - [7. Citus HTAP 方案](#7-citus-htap-方案)
    - [7.1 Citus 混合部署](#71-citus-混合部署)
    - [7.2 Citus 实时分析](#72-citus-实时分析)
  - [8. 工程实践](#8-工程实践)
    - [8.1 监控指标](#81-监控指标)
    - [8.2 性能优化建议](#82-性能优化建议)
    - [8.3 容量规划](#83-容量规划)
  - [参考资源](#参考资源)

## 1. HTAP 概述

### 1.1 什么是 HTAP

**HTAP 定义**:

- 在同一个数据库中同时支持事务处理（OLTP）和分析处理（OLAP）
- 避免传统 ETL 流程的延迟
- 提供实时分析能力

**传统架构 vs HTAP**:

传统架构：

```text
OLTP数据库 --ETL--> 数据仓库 --查询--> 分析报表
延迟：小时级到天级
```

HTAP 架构：

```text
HTAP数据库 --实时--> 事务+分析
延迟：秒级到分钟级
```

### 1.2 HTAP 的挑战

**资源竞争**:

- OLTP 需要低延迟、高并发
- OLAP 需要高吞吐、大扫描
- 两者共享资源导致相互影响

**数据一致性**:

- OLTP 强一致性
- OLAP 可以容忍一定延迟
- 需要平衡新鲜度和性能

**查询优化**:

- OLTP：索引查询，小范围
- OLAP：全表扫描，聚合计算
- 需要不同的优化策略

## 2. 行列混合存储

### 2.1 行存储 vs 列存储

**行存储（Row-Store）**:

- 特点：按行存储，适合事务处理
- 优势：写入快速，点查询高效
- 适用：OLTP 场景
- PostgreSQL 默认存储格式

**列存储（Column-Store）**:

- 特点：按列存储，适合分析处理
- 优势：压缩率高，列扫描快速
- 适用：OLAP 场景
- 需要扩展支持

### 2.2 PostgreSQL 列存储方案

**使用 Cstore_fdw 扩展**:

```sql
-- 安装cstore_fdw扩展
CREATE EXTENSION cstore_fdw;

-- 创建列存储服务器
CREATE SERVER cstore_server FOREIGN DATA WRAPPER cstore_fdw;

-- 创建列存储表
CREATE FOREIGN TABLE events_columnar (
    event_id BIGINT,
    user_id BIGINT,
    event_type TEXT,
    event_time TIMESTAMPTZ,
    properties JSONB
)
SERVER cstore_server
OPTIONS (compression 'pglz', stripe_row_count '150000');

-- 从行存储表迁移数据
INSERT INTO events_columnar SELECT * FROM events;

-- 分析查询性能对比
EXPLAIN (ANALYZE, BUFFERS)
SELECT event_type, COUNT(*), AVG(user_id)
FROM events  -- 行存储
WHERE event_time > NOW() - INTERVAL '7 days'
GROUP BY event_type;

EXPLAIN (ANALYZE, BUFFERS)
SELECT event_type, COUNT(*), AVG(user_id)
FROM events_columnar  -- 列存储
WHERE event_time > NOW() - INTERVAL '7 days'
GROUP BY event_type;
```

**使用 TimescaleDB 压缩**:

```sql
-- 启用压缩（类似列存储）
ALTER TABLE metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- 配置自动压缩策略
SELECT add_compression_policy('metrics', INTERVAL '7 days');

-- 查看压缩效果
SELECT
    pg_size_pretty(before_compression_total_bytes) as before,
    pg_size_pretty(after_compression_total_bytes) as after,
    ROUND(100 - (after_compression_total_bytes::numeric /
                 before_compression_total_bytes::numeric * 100), 2) as compression_ratio
FROM hypertable_compression_stats('metrics');
```

### 2.3 混合存储策略

**热数据行存储，冷数据列存储**:

```sql
-- 创建分区表
CREATE TABLE orders (
    order_id BIGINT,
    user_id BIGINT,
    order_date DATE,
    amount NUMERIC,
    status TEXT
) PARTITION BY RANGE (order_date);

-- 最近数据使用行存储（热数据）
CREATE TABLE orders_2025_10 PARTITION OF orders
FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

-- 历史数据使用列存储（冷数据）
CREATE FOREIGN TABLE orders_2025_09 PARTITION OF orders
FOR VALUES FROM ('2025-09-01') TO ('2025-10-01')
SERVER cstore_server
OPTIONS (compression 'pglz');
```

## 3. 实时物化视图

### 3.1 标准物化视图

```sql
-- 创建物化视图
CREATE MATERIALIZED VIEW daily_sales_summary AS
SELECT
    DATE(order_date) as sale_date,
    COUNT(*) as order_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
FROM orders
WHERE status = 'COMPLETED'
GROUP BY DATE(order_date);

-- 创建索引
CREATE INDEX idx_daily_sales_date ON daily_sales_summary (sale_date);

-- 手动刷新
REFRESH MATERIALIZED VIEW daily_sales_summary;

-- 并发刷新（不阻塞读取）
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales_summary;
```

### 3.2 增量刷新物化视图

```sql
-- 创建增量刷新触发器
CREATE OR REPLACE FUNCTION refresh_daily_sales()
RETURNS TRIGGER AS $$
BEGIN
    -- 只刷新受影响的日期
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales_summary;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_changed
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_daily_sales();
```

### 3.3 TimescaleDB 连续聚合

```sql
-- 创建连续聚合（实时物化视图）
CREATE MATERIALIZED VIEW hourly_metrics
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    device_id,
    AVG(temperature) as avg_temp,
    MAX(temperature) as max_temp,
    MIN(temperature) as min_temp,
    COUNT(*) as reading_count
FROM metrics
GROUP BY hour, device_id;

-- 创建刷新策略
SELECT add_continuous_aggregate_policy('hourly_metrics',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- 实时查询（包含最新数据）
SELECT * FROM hourly_metrics
WHERE hour > NOW() - INTERVAL '24 hours'
ORDER BY hour DESC;
```

## 4. 冷热分层

### 4.1 时间分区策略

```sql
-- 创建时间分区表
CREATE TABLE events (
    event_id BIGSERIAL,
    event_time TIMESTAMPTZ NOT NULL,
    event_type TEXT,
    data JSONB
) PARTITION BY RANGE (event_time);

-- 热数据分区（最近1个月，SSD存储）
CREATE TABLE events_hot PARTITION OF events
FOR VALUES FROM ('2025-09-03') TO ('2025-10-03')
TABLESPACE fast_ssd;

-- 温数据分区（1-3个月，标准存储）
CREATE TABLE events_warm PARTITION OF events
FOR VALUES FROM ('2025-06-03') TO ('2025-09-03')
TABLESPACE standard_storage;

-- 冷数据分区（3个月以上，归档存储）
CREATE TABLE events_cold PARTITION OF events
FOR VALUES FROM ('2020-01-01') TO ('2025-06-03')
TABLESPACE archive_storage;
```

### 4.2 自动分层管理

```sql
-- 创建自动归档函数
CREATE OR REPLACE FUNCTION archive_old_partitions()
RETURNS void AS $$
DECLARE
    partition_name TEXT;
    tablespace_name TEXT;
BEGIN
    -- 将90天前的分区移动到归档表空间
    FOR partition_name, tablespace_name IN
        SELECT
            c.relname,
            t.spcname
        FROM pg_class c
        JOIN pg_namespace n ON c.relnamespace = n.oid
        JOIN pg_tablespace t ON c.reltablespace = t.oid
        WHERE c.relkind = 'r'
          AND n.nspname = 'public'
          AND c.relname LIKE 'events_%'
          AND c.relname NOT IN ('events_hot', 'events_cold')
    LOOP
        -- 移动到冷存储
        IF tablespace_name != 'archive_storage' THEN
            EXECUTE format('ALTER TABLE %I SET TABLESPACE archive_storage',
                          partition_name);
            RAISE NOTICE '已归档分区: %', partition_name;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 定期执行归档
SELECT cron.schedule('archive-old-data', '0 2 * * *',
                     'SELECT archive_old_partitions()');
```

### 4.3 分层压缩

```sql
-- 冷数据启用压缩
ALTER TABLE events_cold SET (
    toast_tuple_target = 128,  -- 启用更激进的TOAST压缩
    fillfactor = 100           -- 最大化页面利用率
);

-- 使用pg_squeeze重新压缩表
CREATE EXTENSION pg_squeeze;

-- 压缩冷数据表
SELECT squeeze.squeeze_table('public', 'events_cold', NULL, NULL);
```

## 5. 资源隔离

### 5.1 连接池分离

```sql
-- pgbouncer配置：分离OLTP和OLAP连接池
[databases]
app_db_oltp = host=primary.db port=5432 dbname=app pool_size=50
app_db_olap = host=replica.db port=5432 dbname=app pool_size=10

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 50
```

### 5.2 资源组管理

```sql
-- PostgreSQL 17 资源组（通过扩展）
-- 创建OLTP资源组
CREATE RESOURCE GROUP oltp_group WITH (
    cpu_rate_limit = 70,
    memory_limit = 60
);

-- 创建OLAP资源组
CREATE RESOURCE GROUP olap_group WITH (
    cpu_rate_limit = 30,
    memory_limit = 40
);

-- 分配角色到资源组
ALTER ROLE app_user RESOURCE GROUP oltp_group;
ALTER ROLE analyst_user RESOURCE GROUP olap_group;
```

### 5.3 查询优先级

```sql
-- 设置不同优先级的work_mem
-- OLTP查询（低内存）
SET work_mem = '4MB';
SELECT * FROM orders WHERE order_id = 12345;

-- OLAP查询（高内存）
SET work_mem = '256MB';
SELECT
    DATE(order_date) as date,
    COUNT(*),
    SUM(amount)
FROM orders
WHERE order_date > NOW() - INTERVAL '1 year'
GROUP BY date;
```

### 5.4 语句超时

```sql
-- OLTP超时设置（快速失败）
ALTER ROLE app_user SET statement_timeout = '5s';
ALTER ROLE app_user SET lock_timeout = '2s';

-- OLAP超时设置（允许长查询）
ALTER ROLE analyst_user SET statement_timeout = '600s';
ALTER ROLE analyst_user SET lock_timeout = '30s';
```

## 6. PostgreSQL HTAP 实现

### 6.1 读写分离

```sql
-- 主库处理OLTP写入
-- postgresql.conf (主库)
synchronous_commit = on
max_connections = 200
shared_buffers = 8GB
effective_cache_size = 24GB

-- 只读副本处理OLAP查询
-- postgresql.conf (副本)
hot_standby = on
max_standby_streaming_delay = 300s  -- 允许更长的查询
hot_standby_feedback = on           -- 防止查询冲突
```

### 6.2 智能路由

```python
# Python应用层路由示例
from sqlalchemy import create_engine

# OLTP连接
oltp_engine = create_engine('postgresql://user:pass@primary:5432/db')

# OLAP连接
olap_engine = create_engine('postgresql://user:pass@replica:5432/db')

def execute_query(query, query_type='oltp'):
    if query_type == 'oltp':
        return oltp_engine.execute(query)
    else:
        return olap_engine.execute(query)

# 使用示例
# 事务查询路由到主库
result = execute_query("SELECT * FROM orders WHERE id = 123", 'oltp')

# 分析查询路由到副本
result = execute_query("""
    SELECT DATE(created_at), COUNT(*)
    FROM orders
    GROUP BY DATE(created_at)
""", 'olap')
```

## 7. Citus HTAP 方案

### 7.1 Citus 混合部署

```sql
-- 创建分布式表（OLTP）
SELECT create_distributed_table('orders', 'user_id');

-- 创建引用表（小维度表）
SELECT create_reference_table('products');

-- 创建列存储表（OLAP）
CREATE FOREIGN TABLE orders_analytics (
    order_id BIGINT,
    user_id BIGINT,
    order_date DATE,
    amount NUMERIC
) SERVER cstore_server;

-- 定期同步到列存储
INSERT INTO orders_analytics
SELECT * FROM orders
WHERE order_date = CURRENT_DATE - 1;
```

### 7.2 Citus 实时分析

```sql
-- 跨分片实时聚合
SELECT
    DATE(order_date) as date,
    COUNT(*) as order_count,
    SUM(amount) as total_amount
FROM orders
WHERE order_date > NOW() - INTERVAL '30 days'
GROUP BY DATE(order_date)
ORDER BY date DESC;

-- Citus自动并行执行，每个分片本地聚合后合并
```

## 8. 工程实践

### 8.1 监控指标

```sql
-- 创建监控视图
CREATE VIEW htap_monitoring AS
SELECT
    'OLTP' as workload_type,
    COUNT(*) as query_count,
    AVG(total_time) as avg_time_ms,
    MAX(total_time) as max_time_ms
FROM pg_stat_statements
WHERE query NOT LIKE '%SELECT COUNT%'
  AND query NOT LIKE '%GROUP BY%'
  AND total_time < 1000  -- 小于1秒的查询

UNION ALL

SELECT
    'OLAP' as workload_type,
    COUNT(*) as query_count,
    AVG(total_time) as avg_time_ms,
    MAX(total_time) as max_time_ms
FROM pg_stat_statements
WHERE (query LIKE '%SELECT COUNT%' OR query LIKE '%GROUP BY%')
  AND total_time >= 1000;  -- 大于1秒的查询
```

### 8.2 性能优化建议

1. **分离工作负载**：使用读写分离或连接池分离
2. **使用列存储**：对历史数据和分析表使用列存储
3. **物化视图**：为常用聚合查询创建物化视图
4. **分区策略**：使用时间分区实现冷热分层
5. **资源隔离**：配置不同的资源组和超时时间
6. **索引优化**：OLTP 使用 B-tree，OLAP 使用 BRIN
7. **并行查询**：为 OLAP 查询启用并行执行
8. **定期维护**：定期 VACUUM、ANALYZE 和重建索引

### 8.3 容量规划

**存储规划**:

- 热数据：SSD 存储，保留 30 天
- 温数据：标准存储，保留 90 天
- 冷数据：归档存储，保留 1 年+

**内存规划**:

- shared_buffers：总内存的 25%
- effective_cache_size：总内存的 75%
- work_mem：OLTP 4-16MB，OLAP 256MB-1GB

**CPU 规划**:

- OLTP：高频 CPU，多核心
- OLAP：启用并行查询（max_parallel_workers）

## 参考资源

- [TimescaleDB
  连续聚合](<https://docs.timescale.com/timescaledb/latest/how-to-guides/continuous-aggregates>/)
- [Citus HTAP](<https://docs.citusdata.com/en/stable/use_cases/realtime_analytics.htm>l)
- [PostgreSQL 并行查询](<https://www.postgresql.org/docs/current/parallel-query.htm>l)
- [列存储扩展](<https://github.com/citusdata/cstore_fd>w)
