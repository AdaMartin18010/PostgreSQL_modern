# 实时分析实战案例 — Real-Time Analytics with PostgreSQL

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **难度等级**：⭐⭐⭐⭐⭐ 专家级  
> **预计时间**：90-120分钟  
> **适合场景**：实时大屏、监控告警、流式分析、业务指标实时计算

---

## 📋 案例目标

构建一个生产级的实时分析系统，包括：
1. ✅ 高频数据写入（10K+ TPS）
2. ✅ 实时聚合查询（亚秒级响应）
3. ✅ 滑动窗口分析（1分钟/5分钟/1小时）
4. ✅ 物化视图增量刷新
5. ✅ 流式处理与OLAP优化

---

## 🎯 业务场景

**场景描述**：电商平台实时业务监控大屏

- **数据源**：
  - 订单事件（每秒1000+）
  - 用户行为（每秒5000+）
  - 支付事件（每秒500+）
- **分析需求**：
  - 实时GMV（成交总额）
  - 每分钟订单量/转化率
  - 热门商品Top10
  - 地区销售分布
- **性能要求**：
  - 查询响应<100ms
  - 数据延迟<1秒
  - 支持高并发查询

---

## 🏗️ 架构设计

```text
高频事件流
    ↓
分区表（按时间分区）
    ↓
并行写入（COPY/批量INSERT）
    ↓
物化视图（预聚合）
    ↓
增量刷新（pg_cron定时）
    ↓
实时查询API
```

---

## 📦 1. 数据模型设计

### 1.1 创建事件表（高性能写入）

```sql
-- 创建订单事件表（分区表）
CREATE TABLE order_events (
    id bigserial,
    order_id bigint NOT NULL,
    user_id bigint NOT NULL,
    product_id bigint NOT NULL,
    product_name text NOT NULL,
    quantity int NOT NULL,
    price numeric(10,2) NOT NULL,
    amount numeric(12,2) NOT NULL,  -- quantity * price
    status text NOT NULL,
    region text,
    city text,
    event_time timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id, event_time)
) PARTITION BY RANGE (event_time);

-- 创建分区（每天一个分区，提升写入和查询性能）
CREATE TABLE order_events_2025_10_01 PARTITION OF order_events
    FOR VALUES FROM ('2025-10-01') TO ('2025-10-02');
CREATE TABLE order_events_2025_10_02 PARTITION OF order_events
    FOR VALUES FROM ('2025-10-02') TO ('2025-10-03');
CREATE TABLE order_events_2025_10_03 PARTITION OF order_events
    FOR VALUES FROM ('2025-10-03') TO ('2025-10-04');

-- 创建索引（只在常用查询列上）
CREATE INDEX idx_order_events_event_time ON order_events(event_time DESC);
CREATE INDEX idx_order_events_status ON order_events(status) WHERE status IN ('paid', 'completed');
CREATE INDEX idx_order_events_region ON order_events(region);

-- 优化写入性能：减少索引、使用FILLFACTOR
ALTER TABLE order_events SET (
    fillfactor = 90,  -- 预留10%空间给HOT更新
    autovacuum_vacuum_scale_factor = 0.05,  -- 更频繁的VACUUM
    autovacuum_analyze_scale_factor = 0.02  -- 更频繁的ANALYZE
);
```

### 1.2 创建用户行为表

```sql
-- 创建用户行为事件表（点击、浏览、加购）
CREATE TABLE user_behavior_events (
    id bigserial,
    user_id bigint NOT NULL,
    session_id text NOT NULL,
    event_type text NOT NULL,  -- 'view', 'click', 'add_to_cart'
    product_id bigint,
    page_url text,
    referrer text,
    device_type text,
    event_time timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id, event_time)
) PARTITION BY RANGE (event_time);

-- 创建分区
CREATE TABLE user_behavior_events_2025_10_03 PARTITION OF user_behavior_events
    FOR VALUES FROM ('2025-10-03') TO ('2025-10-04');

-- 索引
CREATE INDEX idx_behavior_event_time ON user_behavior_events(event_time DESC);
CREATE INDEX idx_behavior_event_type ON user_behavior_events(event_type);
```

---

## 📝 2. 高性能数据写入

### 2.1 批量插入（推荐）

```sql
-- 使用INSERT...VALUES批量插入（100-1000条/批）
INSERT INTO order_events (order_id, user_id, product_id, product_name, quantity, price, amount, status, region, city, event_time)
VALUES
    (1001, 1, 101, 'iPhone 15', 1, 5999.00, 5999.00, 'paid', '华北', '北京', now()),
    (1002, 2, 102, 'MacBook Pro', 1, 12999.00, 12999.00, 'paid', '华东', '上海', now()),
    (1003, 3, 103, 'AirPods Pro', 2, 1999.00, 3998.00, 'pending', '华南', '广州', now()),
    (1004, 4, 101, 'iPhone 15', 1, 5999.00, 5999.00, 'completed', '华北', '北京', now()),
    (1005, 5, 104, 'iPad Air', 1, 4799.00, 4799.00, 'paid', '华东', '杭州', now());

-- 查看插入结果
SELECT * FROM order_events ORDER BY event_time DESC LIMIT 10;
```

### 2.2 COPY批量导入（最快）

```sql
-- 使用COPY导入CSV数据（百万级性能）
COPY order_events (order_id, user_id, product_id, product_name, quantity, price, amount, status, region, city, event_time)
FROM '/tmp/order_events.csv'
WITH (FORMAT csv, HEADER true);

-- 或从程序中使用COPY协议（Python示例）
-- import psycopg2
-- conn = psycopg2.connect("dbname=mydb")
-- cursor = conn.cursor()
-- with open('events.csv', 'r') as f:
--     cursor.copy_expert(
--         "COPY order_events FROM STDIN WITH CSV HEADER",
--         f
--     )
-- conn.commit()
```

### 2.3 生成测试数据

```sql
-- 生成10万条测试订单数据
INSERT INTO order_events (order_id, user_id, product_id, product_name, quantity, price, amount, status, region, city, event_time)
SELECT
    1000000 + i AS order_id,
    (random() * 10000)::int AS user_id,
    (random() * 100)::int AS product_id,
    'Product ' || ((random() * 100)::int) AS product_name,
    (random() * 5 + 1)::int AS quantity,
    (random() * 1000 + 10)::numeric(10,2) AS price,
    ((random() * 1000 + 10) * (random() * 5 + 1))::numeric(12,2) AS amount,
    (ARRAY['pending', 'paid', 'completed', 'cancelled'])[1 + (random() * 3)::int] AS status,
    (ARRAY['华北', '华东', '华南', '西南'])[1 + (random() * 3)::int] AS region,
    (ARRAY['北京', '上海', '广州', '深圳', '杭州'])[1 + (random() * 4)::int] AS city,
    now() - (random() * interval '24 hours') AS event_time
FROM generate_series(1, 100000) AS i;

-- 查看数据量
SELECT 
    COUNT(*) AS total_events,
    pg_size_pretty(pg_total_relation_size('order_events')) AS table_size
FROM order_events;
```

---

## 🔍 3. 实时分析查询

### 3.1 实时GMV（成交总额）

```sql
-- 实时GMV（最近1小时）
SELECT 
    COUNT(*) AS order_count,
    SUM(amount) AS gmv,
    AVG(amount) AS avg_order_value
FROM order_events
WHERE status IN ('paid', 'completed')
  AND event_time > now() - interval '1 hour';

-- 按时间段分组（每分钟）
SELECT 
    DATE_TRUNC('minute', event_time) AS time_bucket,
    COUNT(*) AS order_count,
    SUM(amount) AS gmv
FROM order_events
WHERE status IN ('paid', 'completed')
  AND event_time > now() - interval '1 hour'
GROUP BY time_bucket
ORDER BY time_bucket DESC;
```

### 3.2 滑动窗口分析

```sql
-- 使用窗口函数计算移动平均
WITH minute_stats AS (
    SELECT 
        DATE_TRUNC('minute', event_time) AS time_bucket,
        COUNT(*) AS order_count,
        SUM(amount) AS gmv
    FROM order_events
    WHERE status IN ('paid', 'completed')
      AND event_time > now() - interval '6 hours'
    GROUP BY time_bucket
)
SELECT 
    time_bucket,
    order_count,
    gmv,
    -- 5分钟移动平均
    AVG(order_count) OVER (
        ORDER BY time_bucket
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS ma5_order_count,
    AVG(gmv) OVER (
        ORDER BY time_bucket
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS ma5_gmv
FROM minute_stats
ORDER BY time_bucket DESC
LIMIT 60;
```

### 3.3 热门商品Top10

```sql
-- 实时热门商品（最近1小时）
SELECT 
    product_id,
    product_name,
    COUNT(*) AS sale_count,
    SUM(quantity) AS total_quantity,
    SUM(amount) AS total_revenue
FROM order_events
WHERE status IN ('paid', 'completed')
  AND event_time > now() - interval '1 hour'
GROUP BY product_id, product_name
ORDER BY sale_count DESC
LIMIT 10;
```

### 3.4 地区销售分布

```sql
-- 按地区统计
SELECT 
    region,
    city,
    COUNT(*) AS order_count,
    SUM(amount) AS gmv,
    AVG(amount) AS avg_order_value,
    COUNT(DISTINCT user_id) AS unique_users
FROM order_events
WHERE status IN ('paid', 'completed')
  AND event_time > now() - interval '1 hour'
GROUP BY ROLLUP(region, city)
ORDER BY region NULLS LAST, gmv DESC;
```

---

## 🚀 4. 物化视图优化

### 4.1 创建物化视图（预聚合）

```sql
-- 创建每分钟聚合的物化视图
CREATE MATERIALIZED VIEW order_metrics_1min AS
SELECT 
    DATE_TRUNC('minute', event_time) AS time_bucket,
    status,
    region,
    COUNT(*) AS order_count,
    SUM(amount) AS gmv,
    SUM(quantity) AS total_quantity,
    AVG(amount) AS avg_order_value,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(DISTINCT product_id) AS unique_products
FROM order_events
WHERE event_time > now() - interval '7 days'
GROUP BY time_bucket, status, region;

-- 创建唯一索引（支持CONCURRENTLY刷新）
CREATE UNIQUE INDEX idx_order_metrics_1min_pk 
    ON order_metrics_1min(time_bucket, status, region);

-- 创建其他索引
CREATE INDEX idx_order_metrics_1min_time ON order_metrics_1min(time_bucket DESC);
CREATE INDEX idx_order_metrics_1min_status ON order_metrics_1min(status);

-- 查询物化视图（快速）
SELECT 
    time_bucket,
    SUM(gmv) AS total_gmv,
    SUM(order_count) AS total_orders
FROM order_metrics_1min
WHERE time_bucket > now() - interval '1 hour'
  AND status IN ('paid', 'completed')
GROUP BY time_bucket
ORDER BY time_bucket DESC;
```

### 4.2 增量刷新物化视图

```sql
-- 安装pg_cron扩展（定时任务）
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 每分钟刷新物化视图
SELECT cron.schedule(
    'refresh_order_metrics',
    '* * * * *',  -- 每分钟
    $$REFRESH MATERIALIZED VIEW CONCURRENTLY order_metrics_1min$$
);

-- 查看定时任务
SELECT * FROM cron.job;

-- 查看任务执行历史
SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 10;

-- 取消定时任务
-- SELECT cron.unschedule('refresh_order_metrics');
```

### 4.3 创建多层级物化视图

```sql
-- 5分钟聚合
CREATE MATERIALIZED VIEW order_metrics_5min AS
SELECT 
    DATE_TRUNC('minute', time_bucket) - 
        (EXTRACT(minute FROM time_bucket)::int % 5) * interval '1 minute' AS time_bucket,
    status,
    region,
    SUM(order_count) AS order_count,
    SUM(gmv) AS gmv,
    AVG(avg_order_value) AS avg_order_value
FROM order_metrics_1min
GROUP BY 1, status, region;

CREATE UNIQUE INDEX idx_order_metrics_5min_pk 
    ON order_metrics_5min(time_bucket, status, region);

-- 1小时聚合
CREATE MATERIALIZED VIEW order_metrics_1hour AS
SELECT 
    DATE_TRUNC('hour', time_bucket) AS time_bucket,
    status,
    region,
    SUM(order_count) AS order_count,
    SUM(gmv) AS gmv,
    AVG(avg_order_value) AS avg_order_value
FROM order_metrics_1min
GROUP BY 1, status, region;

CREATE UNIQUE INDEX idx_order_metrics_1hour_pk 
    ON order_metrics_1hour(time_bucket, status, region);
```

---

## 📊 5. 性能优化

### 5.1 分区管理自动化

```sql
-- 创建自动分区函数
CREATE OR REPLACE FUNCTION create_partition_if_not_exists(
    parent_table text,
    partition_date date
)
RETURNS void AS $$
DECLARE
    partition_name text;
    start_date text;
    end_date text;
BEGIN
    partition_name := parent_table || '_' || to_char(partition_date, 'YYYY_MM_DD');
    start_date := partition_date::text;
    end_date := (partition_date + interval '1 day')::text;
    
    -- 检查分区是否存在
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
            partition_name, parent_table, start_date, end_date
        );
        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 提前创建未来7天的分区
SELECT create_partition_if_not_exists('order_events', current_date + i)
FROM generate_series(0, 7) AS i;

-- 使用pg_cron每天自动创建分区
SELECT cron.schedule(
    'create_daily_partitions',
    '0 0 * * *',  -- 每天0点
    $$SELECT create_partition_if_not_exists('order_events', current_date + 1)$$
);
```

### 5.2 历史数据清理

```sql
-- 删除30天前的分区（释放空间）
CREATE OR REPLACE FUNCTION drop_old_partitions(
    parent_table text,
    retention_days int DEFAULT 30
)
RETURNS int AS $$
DECLARE
    partition_record RECORD;
    dropped_count int := 0;
BEGIN
    FOR partition_record IN
        SELECT 
            c.relname AS partition_name,
            pg_get_expr(c.relpartbound, c.oid) AS partition_bound
        FROM pg_class c
        JOIN pg_inherits i ON c.oid = i.inhrelid
        JOIN pg_class p ON i.inhparent = p.oid
        WHERE p.relname = parent_table
          AND c.relkind = 'r'
    LOOP
        -- 解析分区范围，检查是否超过保留期
        -- （简化版，实际需要解析partition_bound）
        IF partition_record.partition_name ~ '_\d{4}_\d{2}_\d{2}$' THEN
            EXECUTE format('DROP TABLE IF EXISTS %I', partition_record.partition_name);
            dropped_count := dropped_count + 1;
            RAISE NOTICE 'Dropped partition: %', partition_record.partition_name;
        END IF;
    END LOOP;
    
    RETURN dropped_count;
END;
$$ LANGUAGE plpgsql;

-- 定期清理
SELECT cron.schedule(
    'drop_old_partitions',
    '0 2 * * *',  -- 每天凌晨2点
    $$SELECT drop_old_partitions('order_events', 30)$$
);
```

### 5.3 并行查询优化

```sql
-- 启用并行查询
SET max_parallel_workers_per_gather = 4;
SET parallel_setup_cost = 100;
SET parallel_tuple_cost = 0.01;

-- 测试并行聚合
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    DATE_TRUNC('hour', event_time) AS hour,
    COUNT(*) AS order_count,
    SUM(amount) AS gmv
FROM order_events
WHERE event_time > now() - interval '7 days'
GROUP BY hour;

-- 查看是否使用并行
-- Finalize GroupAggregate
--   -> Gather
--        Workers Planned: 4
--        -> Partial GroupAggregate
--             -> Parallel Seq Scan on order_events
```

---

## 🎨 6. 实时大屏API设计

### 6.1 创建查询函数

```sql
-- 实时指标汇总函数
CREATE OR REPLACE FUNCTION get_realtime_metrics(
    time_window interval DEFAULT '1 hour'
)
RETURNS TABLE (
    metric_name text,
    metric_value numeric,
    unit text
) AS $$
BEGIN
    RETURN QUERY
    -- GMV
    SELECT 
        'gmv'::text,
        COALESCE(SUM(amount), 0),
        'CNY'::text
    FROM order_events
    WHERE status IN ('paid', 'completed')
      AND event_time > now() - time_window
    UNION ALL
    -- 订单量
    SELECT 
        'order_count'::text,
        COALESCE(COUNT(*)::numeric, 0),
        'orders'::text
    FROM order_events
    WHERE status IN ('paid', 'completed')
      AND event_time > now() - time_window
    UNION ALL
    -- 客单价
    SELECT 
        'avg_order_value'::text,
        COALESCE(AVG(amount), 0),
        'CNY'::text
    FROM order_events
    WHERE status IN ('paid', 'completed')
      AND event_time > now() - time_window
    UNION ALL
    -- 活跃用户数
    SELECT 
        'active_users'::text,
        COALESCE(COUNT(DISTINCT user_id)::numeric, 0),
        'users'::text
    FROM order_events
    WHERE event_time > now() - time_window;
END;
$$ LANGUAGE plpgsql STABLE;

-- 调用示例
SELECT * FROM get_realtime_metrics('1 hour');
```

### 6.2 趋势图数据API

```sql
-- 时序趋势数据
CREATE OR REPLACE FUNCTION get_order_trend(
    time_window interval DEFAULT '24 hours',
    bucket_size interval DEFAULT '1 hour'
)
RETURNS TABLE (
    time_bucket timestamptz,
    order_count bigint,
    gmv numeric,
    avg_order_value numeric
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE_TRUNC('hour', event_time) AS time_bucket,
        COUNT(*) AS order_count,
        SUM(amount) AS gmv,
        AVG(amount) AS avg_order_value
    FROM order_events
    WHERE status IN ('paid', 'completed')
      AND event_time > now() - time_window
    GROUP BY time_bucket
    ORDER BY time_bucket;
END;
$$ LANGUAGE plpgsql STABLE;

-- 调用示例（返回JSON）
SELECT json_agg(row_to_json(t)) AS trend_data
FROM get_order_trend('24 hours', '1 hour') t;
```

---

## ✅ 7. 完整监控大屏示例

```sql
-- 综合实时监控查询（适合大屏刷新）
WITH realtime_summary AS (
    SELECT 
        COUNT(*) AS order_count,
        SUM(amount) AS gmv,
        AVG(amount) AS avg_order_value,
        COUNT(DISTINCT user_id) AS unique_users
    FROM order_events
    WHERE status IN ('paid', 'completed')
      AND event_time > now() - interval '1 hour'
),
region_breakdown AS (
    SELECT 
        region,
        COUNT(*) AS order_count,
        SUM(amount) AS gmv
    FROM order_events
    WHERE status IN ('paid', 'completed')
      AND event_time > now() - interval '1 hour'
    GROUP BY region
    ORDER BY gmv DESC
    LIMIT 5
),
top_products AS (
    SELECT 
        product_name,
        COUNT(*) AS sale_count,
        SUM(amount) AS revenue
    FROM order_events
    WHERE status IN ('paid', 'completed')
      AND event_time > now() - interval '1 hour'
    GROUP BY product_name
    ORDER BY sale_count DESC
    LIMIT 10
)
SELECT 
    json_build_object(
        'summary', (SELECT row_to_json(rs) FROM realtime_summary rs),
        'region_breakdown', (SELECT json_agg(row_to_json(rb)) FROM region_breakdown rb),
        'top_products', (SELECT json_agg(row_to_json(tp)) FROM top_products tp),
        'timestamp', extract(epoch from now())
    ) AS dashboard_data;
```

---

## 📚 8. 最佳实践

### 8.1 架构设计
- ✅ 使用分区表存储时序数据
- ✅ 物化视图预聚合热点指标
- ✅ 多层级聚合（分钟→小时→天）
- ✅ 读写分离（主库写入，从库查询）

### 8.2 性能优化
- ✅ 批量写入（COPY/批量INSERT）
- ✅ 启用并行查询
- ✅ 减少不必要的索引
- ✅ 定期VACUUM和ANALYZE

### 8.3 实时性保证
- ✅ 使用pg_cron定时刷新
- ✅ 增量刷新而非全量
- ✅ 缓存热点查询结果
- ✅ LISTEN/NOTIFY推送变更

### 8.4 扩展性
- ✅ 考虑使用Citus分布式扩展
- ✅ TimescaleDB时序数据优化
- ✅ 集成ClickHouse做OLAP
- ✅ 使用连接池（PgBouncer）

---

## 🎯 9. 练习任务

1. **基础练习**：
   - 创建分区表并插入10万条测试数据
   - 实现实时GMV查询
   - 创建热门商品Top10查询

2. **进阶练习**：
   - 创建物化视图并设置定时刷新
   - 实现滑动窗口分析
   - 设计实时监控API

3. **挑战任务**：
   - 构建完整的实时大屏系统
   - 优化百万级TPS写入性能
   - 实现跨数据中心实时同步

---

## 📖 10. 扩展阅读

- PostgreSQL分区表：<https://www.postgresql.org/docs/17/ddl-partitioning.html>
- 物化视图：<https://www.postgresql.org/docs/17/sql-creatematerializedview.html>
- pg_cron扩展：<https://github.com/citusdata/pg_cron>
- TimescaleDB：<https://docs.timescale.com/>
- Apache Superset（可视化）：<https://superset.apache.org/>

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**相关案例**：[全文搜索](../full_text_search/README.md) | [CDC](../change_data_capture/README.md) | [地理围栏](../geofencing/README.md) | [联邦查询](../federated_queries/README.md)

