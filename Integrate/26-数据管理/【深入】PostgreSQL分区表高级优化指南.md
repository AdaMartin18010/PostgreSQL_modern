---

> **📋 文档来源**: `PostgreSQL培训\05-数据管理\【深入】PostgreSQL分区表高级优化指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 【深入】PostgreSQL分区表高级优化指南

> **创建时间**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级
> **预计学习时间**: 1-2周

---

## 📑 目录

- [1.1 分区策略对比](#11-分区策略对比)
- [1.2 子分区（Multi-Level Partitioning）](#12-子分区multi-level-partitioning)
- [1.3 默认分区](#13-默认分区)
- [2.1 分区裁剪原理](#21-分区裁剪原理)
- [2.2 静态裁剪（Planning-Time Pruning）](#22-静态裁剪planning-time-pruning)
- [2.3 动态裁剪（Execution-Time Pruning）](#23-动态裁剪execution-time-pruning)
- [2.4 分区裁剪失效案例](#24-分区裁剪失效案例)
- [3.1 自动创建分区](#31-自动创建分区)
- [3.2 自动删除旧分区](#32-自动删除旧分区)
- [3.3 分区归档（Detach而不删除）](#33-分区归档detach而不删除)
- [4.1 分区索引策略](#41-分区索引策略)
- [4.2 分区与并行查询](#42-分区与并行查询)
- [4.3 分区表VACUUM策略](#43-分区表vacuum策略)
- [5.1 从普通表迁移到分区表](#51-从普通表迁移到分区表)
- [5.2 分区表合并](#52-分区表合并)
- [6.1 案例：时序数据分区方案（IoT场景）](#61-案例时序数据分区方案iot场景)
- [6.2 案例：多租户SaaS分区方案](#62-案例多租户saas分区方案)
- [7.1 分区设计原则](#71-分区设计原则)
- [7.2 分区监控](#72-分区监控)
- [官方文档](#官方文档)
- [最佳实践](#最佳实践)
---

## 1. 分区表进阶

### 1.1 分区策略对比

| 分区类型 | 适用场景 | 优势 | 劣势 | PostgreSQL支持 |
| --- | --- | --- | --- | --- |
| **范围分区** | 时序数据、订单 | 查询高效、裁剪明显 | 数据倾斜 | ✅ RANGE |
| **列表分区** | 地区、类别 | 简单明确 | 分区多 | ✅ LIST |
| **哈希分区** | 负载均衡 | 数据均匀 | 裁剪困难 | ✅ HASH |
| **复合分区** | 时间+地区 | 灵活 | 复杂 | ✅ 子分区 |

### 1.2 子分区（Multi-Level Partitioning）

```sql
-- 第一级：按年份分区（RANGE）
CREATE TABLE orders (
    order_id bigserial,
    order_date date NOT NULL,
    region text NOT NULL,
    customer_id int,
    amount numeric,
    PRIMARY KEY (order_id, order_date, region)
) PARTITION BY RANGE (order_date);

-- 第二级：按地区分区（LIST）
CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
    PARTITION BY LIST (region);

CREATE TABLE orders_2024_us PARTITION OF orders_2024
    FOR VALUES IN ('US', 'CA', 'MX');

CREATE TABLE orders_2024_eu PARTITION OF orders_2024
    FOR VALUES IN ('UK', 'DE', 'FR', 'IT', 'ES');

CREATE TABLE orders_2024_asia PARTITION OF orders_2024
    FOR VALUES IN ('CN', 'JP', 'KR', 'IN');

-- 第三级：按月份分区（可选）
CREATE TABLE orders_2024_us_q1 PARTITION OF orders_2024_us
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- 查询：自动分区裁剪
EXPLAIN (ANALYZE, COSTS)
SELECT * FROM orders
WHERE order_date BETWEEN '2024-06-01' AND '2024-06-30'
  AND region = 'US';
-- 只扫描 orders_2024_us_q2分区
```

### 1.3 默认分区

```sql
-- 创建默认分区（捕获所有未匹配的行）
CREATE TABLE orders_default PARTITION OF orders DEFAULT;

-- 插入测试
INSERT INTO orders (order_date, region, amount)
VALUES ('2026-01-01', 'AU', 100);  -- 进入默认分区

-- 查询默认分区
SELECT tableoid::regclass, * FROM orders WHERE order_date >= '2026-01-01';

-- 分割默认分区
-- 1. 创建新分区
CREATE TABLE orders_2026 PARTITION OF orders
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- 2. 数据会自动移动
SELECT tableoid::regclass, * FROM orders WHERE order_date >= '2026-01-01';
-- 现在在orders_2026分区
```

---

## 2. 分区裁剪深度解析

### 2.1 分区裁剪原理

**什么是分区裁剪**：

优化器在查询规划阶段，根据WHERE条件，自动排除不需要扫描的分区。

**启用分区裁剪**：

```sql
-- 查看设置
SHOW enable_partition_pruning;  -- 应该是on（默认）
SHOW constraint_exclusion;      -- partition或on

-- 如果关闭，启用
SET enable_partition_pruning = on;
SET constraint_exclusion = partition;
```

### 2.2 静态裁剪（Planning-Time Pruning）

```sql
-- 示例：WHERE条件是常量
EXPLAIN (ANALYZE, COSTS)
SELECT * FROM orders
WHERE order_date = '2024-06-15';

-- 执行计划显示：
-- Append  (cost=...)
--   ->  Seq Scan on orders_2024_q2  (cost=...)
--         Filter: (order_date = '2024-06-15'::date)
--
-- 只扫描orders_2024_q2，其他分区被裁剪

-- 查看裁剪细节
EXPLAIN (VERBOSE, COSTS)
SELECT * FROM orders
WHERE order_date BETWEEN '2024-06-01' AND '2024-06-30';
-- Subplans Removed: 11  （11个分区被裁剪）
```

**裁剪条件**：

```sql
-- ✅ 可以裁剪（常量条件）
SELECT * FROM orders WHERE order_date = '2024-06-15';
SELECT * FROM orders WHERE order_date > '2024-01-01';
SELECT * FROM orders WHERE order_date BETWEEN '2024-06-01' AND '2024-06-30';

-- ✅ 可以裁剪（参数化条件）
PREPARE get_orders(date) AS
    SELECT * FROM orders WHERE order_date = $1;
EXECUTE get_orders('2024-06-15');

-- ✅ 可以裁剪（函数条件，如果IMMUTABLE）
CREATE FUNCTION get_last_month_start() RETURNS date AS $$
    SELECT date_trunc('month', current_date - interval '1 month')::date;
$$ LANGUAGE SQL IMMUTABLE;

SELECT * FROM orders WHERE order_date >= get_last_month_start();

-- ❌ 不能裁剪（非确定性函数）
SELECT * FROM orders WHERE order_date >= now() - interval '30 days';
-- now()是STABLE，不是IMMUTABLE，优化器无法在规划阶段计算

-- 解决方案：在应用层计算
SELECT * FROM orders WHERE order_date >= $1;  -- $1 = now() - interval '30 days'
```

### 2.3 动态裁剪（Execution-Time Pruning）

```sql
-- PostgreSQL 11+支持执行时裁剪
-- 示例：JOIN中的分区裁剪
CREATE TABLE recent_customers (
    customer_id int PRIMARY KEY,
    signup_date date
);

INSERT INTO recent_customers
SELECT i, current_date - (random() * 30)::int
FROM generate_series(1, 1000) i;

-- 查询：使用recent_customers的日期来裁剪orders分区
EXPLAIN (ANALYZE, COSTS)
SELECT o.*
FROM orders o
JOIN recent_customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= c.signup_date;

-- 执行时裁剪（Execution-Time Pruning）
-- 优化器在JOIN过程中动态裁剪分区
```

### 2.4 分区裁剪失效案例

**案例1：隐式类型转换**：

```sql
-- ❌ 裁剪失效（类型不匹配）
CREATE TABLE events (
    event_id bigserial,
    event_date date NOT NULL,
    data jsonb
) PARTITION BY RANGE (event_date);

-- 创建分区...

-- 查询使用timestamp类型
EXPLAIN SELECT * FROM events
WHERE event_date = '2024-06-15'::timestamp;  -- 注意：timestamp类型
-- 裁剪失效！扫描所有分区

-- ✅ 正确：使用date类型
EXPLAIN SELECT * FROM events
WHERE event_date = '2024-06-15'::date;
-- 裁剪成功
```

**案例2：函数包装**：

```sql
-- ❌ 裁剪失效
EXPLAIN SELECT * FROM orders
WHERE extract(year from order_date) = 2024;
-- 函数包装导致裁剪失效

-- ✅ 正确
EXPLAIN SELECT * FROM orders
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
-- 裁剪成功
```

**案例3：OR条件**：

```sql
-- ❌ 裁剪可能不完全
EXPLAIN SELECT * FROM orders
WHERE order_date = '2024-06-15' OR order_date = '2024-12-15';
-- 可能扫描多个分区

-- ✅ 更好：使用IN
EXPLAIN SELECT * FROM orders
WHERE order_date IN ('2024-06-15', '2024-12-15');
-- 裁剪更高效
```

---

## 3. 分区维护自动化

### 3.1 自动创建分区

**需求**：时序数据每天/每月自动创建新分区

**方案1：使用pg_partman扩展**:

```sql
-- 安装pg_partman
CREATE EXTENSION pg_partman;

-- 创建父表
CREATE TABLE events (
    event_id bigserial,
    event_time timestamptz NOT NULL,
    data jsonb
) PARTITION BY RANGE (event_time);

-- 配置pg_partman
SELECT partman.create_parent(
    p_parent_table => 'public.events',
    p_control => 'event_time',
    p_type => 'native',
    p_interval => 'daily',  -- 或'monthly', 'weekly'
    p_premake => 7,         -- 提前创建7个分区
    p_start_partition => '2025-01-01'
);

-- 自动维护（创建新分区、删除旧分区）
SELECT partman.run_maintenance();

-- 定期执行
SELECT cron.schedule('partman-maintenance', '*/15 * * * *',
    'SELECT partman.run_maintenance()');

-- 配置保留策略
UPDATE partman.part_config
SET retention = '90 days',
    retention_keep_table = false  -- 删除而不是分离
WHERE parent_table = 'public.events';
```

**方案2：自定义函数**:

```sql
-- 创建分区管理函数
CREATE OR REPLACE FUNCTION create_monthly_partition(
    parent_table text,
    partition_date date
) RETURNS void AS $$
DECLARE
    partition_name text;
    start_date date;
    end_date date;
BEGIN
    -- 计算分区名称和范围
    partition_name := parent_table || '_' || to_char(partition_date, 'YYYY_MM');
    start_date := date_trunc('month', partition_date);
    end_date := start_date + interval '1 month';

    -- 检查分区是否已存在
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = partition_name
    ) THEN
        -- 创建分区
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
            partition_name, parent_table, start_date, end_date
        );

        -- 创建索引
        EXECUTE format(
            'CREATE INDEX %I ON %I(event_time)',
            partition_name || '_idx', partition_name
        );

        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 自动创建未来3个月的分区
DO $$
DECLARE
    i int;
BEGIN
    FOR i IN 0..2 LOOP
        PERFORM create_monthly_partition('events', current_date + (i || ' month')::interval);
    END LOOP;
END $$;

-- 定期任务
SELECT cron.schedule(
    'create-future-partitions',
    '0 0 25 * *',  -- 每月25日
    $$
    DO $$
    DECLARE i int;
    BEGIN
        FOR i IN 0..2 LOOP
            PERFORM create_monthly_partition('events', current_date + (i || ' month')::interval);
        END LOOP;
    END $$;
    $$
);
```

### 3.2 自动删除旧分区

```sql
-- 删除旧分区函数
CREATE OR REPLACE FUNCTION drop_old_partitions(
    parent_table text,
    retention_months int DEFAULT 12
) RETURNS void AS $$
DECLARE
    partition_record record;
    cutoff_date date;
BEGIN
    cutoff_date := date_trunc('month', current_date - (retention_months || ' months')::interval);

    FOR partition_record IN
        SELECT
            c.relname,
            pg_get_expr(c.relpartbound, c.oid) AS partition_bound
        FROM pg_class c
        JOIN pg_inherits i ON c.oid = i.inhrelid
        JOIN pg_class p ON i.inhparent = p.oid
        WHERE p.relname = parent_table
          AND c.relkind = 'r'
    LOOP
        -- 解析分区边界
        -- 简化版：使用分区命名约定
        IF partition_record.relname ~ '\d{4}_\d{2}$' THEN
            DECLARE
                partition_date date;
            BEGIN
                partition_date := to_date(
                    substring(partition_record.relname from '\d{4}_\d{2}$'),
                    'YYYY_MM'
                );

                IF partition_date < cutoff_date THEN
                    -- 删除分区
                    EXECUTE format('DROP TABLE %I', partition_record.relname);
                    RAISE NOTICE 'Dropped old partition: %', partition_record.relname;
                END IF;
            END;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 定期删除（每月1日）
SELECT cron.schedule(
    'drop-old-partitions',
    '0 0 1 * *',
    'SELECT drop_old_partitions(''events'', 12)'
);
```

### 3.3 分区归档（Detach而不删除）

```sql
-- 归档分区函数
CREATE OR REPLACE FUNCTION archive_old_partition(
    parent_table text,
    partition_name text,
    archive_schema text DEFAULT 'archive'
) RETURNS void AS $$
BEGIN
    -- 1. 分离分区
    EXECUTE format('ALTER TABLE %I DETACH PARTITION %I', parent_table, partition_name);

    -- 2. 移动到归档schema
    EXECUTE format('ALTER TABLE %I SET SCHEMA %I', partition_name, archive_schema);

    -- 3. 压缩数据（可选）
    EXECUTE format('VACUUM FULL %I.%I', archive_schema, partition_name);

    RAISE NOTICE 'Archived partition % to %', partition_name, archive_schema;
END;
$$ LANGUAGE plpgsql;

-- 创建归档schema
CREATE SCHEMA IF NOT EXISTS archive;

-- 归档2023年的分区
SELECT archive_old_partition('events', 'events_2023', 'archive');

-- 查询归档数据（可选：创建外部表）
CREATE FOREIGN TABLE events_2023_archived (
    event_id bigint,
    event_time timestamptz,
    data jsonb
) SERVER archive_server
OPTIONS (schema_name 'archive', table_name 'events_2023');
```

---

## 4. 性能优化技巧

### 4.1 分区索引策略

```sql
-- 方案1：每个分区独立索引（默认）
CREATE INDEX ON orders_2024_01 (customer_id);
CREATE INDEX ON orders_2024_02 (customer_id);
-- ...

-- 方案2：全局索引（在父表上）
CREATE INDEX ON orders (customer_id);
-- PostgreSQL会自动在所有分区上创建索引

-- 方案3：部分索引（节省空间）
CREATE INDEX ON orders_2024_01 (customer_id) WHERE amount > 1000;
CREATE INDEX ON orders_2024_02 (customer_id) WHERE amount > 1000;

-- 方案4：自动创建索引模板
CREATE OR REPLACE FUNCTION auto_create_partition_indexes()
RETURNS event_trigger AS $$
DECLARE
    partition_name text;
BEGIN
    SELECT objid::regclass::text INTO partition_name
    FROM pg_event_trigger_ddl_commands()
    WHERE object_type = 'table';

    -- 为新分区自动创建索引
    IF partition_name LIKE 'orders_%' THEN
        EXECUTE format('CREATE INDEX ON %I (customer_id)', partition_name);
        EXECUTE format('CREATE INDEX ON %I (order_date)', partition_name);
        RAISE NOTICE 'Auto-created indexes for %', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER auto_index_trigger
    ON ddl_command_end
    WHEN TAG IN ('CREATE TABLE')
    EXECUTE FUNCTION auto_create_partition_indexes();
```

### 4.2 分区与并行查询

```sql
-- 启用并行查询
SET max_parallel_workers_per_gather = 4;
SET parallel_setup_cost = 100;  -- 降低以更容易触发并行

-- 查询多个分区（自动并行）
EXPLAIN (ANALYZE, COSTS, BUFFERS)
SELECT region, COUNT(*), SUM(amount)
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY region;

-- 执行计划可能显示：
-- Finalize GroupAggregate
--   ->  Gather Merge
--         Workers Planned: 4
--         ->  Sort
--               ->  Partial GroupAggregate
--                     ->  Parallel Append
--                           ->  Parallel Seq Scan on orders_2024_01
--                           ->  Parallel Seq Scan on orders_2024_02
--                           ...
```

### 4.3 分区表VACUUM策略

```sql
-- 问题：对大分区表VACUUM很慢
-- 解决：分别VACUUM各个分区

-- 方案1：手动VACUUM各分区
VACUUM (ANALYZE, VERBOSE) orders_2024_01;
VACUUM (ANALYZE, VERBOSE) orders_2024_02;

-- 方案2：并行VACUUM（多个会话）
-- Session 1
VACUUM orders_2024_01;

-- Session 2
VACUUM orders_2024_02;

-- Session 3
VACUUM orders_2024_03;

-- 方案3：自动化脚本
DO $$
DECLARE
    partition_record record;
BEGIN
    FOR partition_record IN
        SELECT c.relname
        FROM pg_class c
        JOIN pg_inherits i ON c.oid = i.inhrelid
        JOIN pg_class p ON i.inhparent = p.oid
        WHERE p.relname = 'orders'
        ORDER BY c.relname
    LOOP
        EXECUTE format('VACUUM (ANALYZE) %I', partition_record.relname);
        RAISE NOTICE 'Vacuumed %', partition_record.relname;
    END LOOP;
END $$;

-- 方案4：调整autovacuum（分区级别）
ALTER TABLE orders_2024_12 SET (
    autovacuum_vacuum_scale_factor = 0.01,  -- 1%变化触发（默认20%）
    autovacuum_analyze_scale_factor = 0.01,
    autovacuum_vacuum_cost_limit = 2000     -- 加快VACUUM速度
);
```

---

## 5. 分区表迁移

### 5.1 从普通表迁移到分区表

**场景**：现有一个5000万行的orders表，需要迁移到分区表

**零停机迁移步骤**：

```sql
-- 步骤1：创建分区表结构（与原表相同）
CREATE TABLE orders_partitioned (
    LIKE orders INCLUDING ALL
) PARTITION BY RANGE (order_date);

-- 步骤2：创建所有需要的分区
-- （使用上文的自动创建分区函数）
DO $$
DECLARE
    start_date date := '2020-01-01';
    end_date date := '2025-12-31';
    current_date date := start_date;
BEGIN
    WHILE current_date < end_date LOOP
        PERFORM create_monthly_partition('orders_partitioned', current_date);
        current_date := current_date + interval '1 month';
    END LOOP;
END $$;

-- 步骤3：创建迁移函数（批量+限流）
CREATE OR REPLACE FUNCTION migrate_to_partitioned(
    batch_size int DEFAULT 10000,
    sleep_ms int DEFAULT 100
) RETURNS bigint AS $$
DECLARE
    total_migrated bigint := 0;
    rows_migrated int;
BEGIN
    LOOP
        -- 复制一批数据
        WITH batch AS (
            SELECT * FROM orders
            WHERE order_id NOT IN (
                SELECT order_id FROM orders_partitioned
            )
            ORDER BY order_id
            LIMIT batch_size
        )
        INSERT INTO orders_partitioned
        SELECT * FROM batch
        ON CONFLICT DO NOTHING;

        GET DIAGNOSTICS rows_migrated = ROW_COUNT;

        EXIT WHEN rows_migrated = 0;

        total_migrated := total_migrated + rows_migrated;

        -- 限流（避免影响业务）
        PERFORM pg_sleep(sleep_ms / 1000.0);

        RAISE NOTICE 'Migrated % rows, total: %', rows_migrated, total_migrated;
    END LOOP;

    RETURN total_migrated;
END;
$$ LANGUAGE plpgsql;

-- 步骤4：后台执行迁移
-- 在低峰期执行
SELECT migrate_to_partitioned(10000, 100);

-- 步骤5：验证数据一致性
SELECT
    (SELECT COUNT(*) FROM orders) AS original_count,
    (SELECT COUNT(*) FROM orders_partitioned) AS partitioned_count,
    (SELECT COUNT(*) FROM orders) = (SELECT COUNT(*) FROM orders_partitioned) AS match;

-- 步骤6：双写（应用层同时写两个表）
-- 在应用中修改：
-- INSERT INTO orders (...) VALUES (...);
-- INSERT INTO orders_partitioned (...) VALUES (...);

-- 步骤7：切换（rename）
BEGIN;
ALTER TABLE orders RENAME TO orders_old;
ALTER TABLE orders_partitioned RENAME TO orders;
COMMIT;

-- 步骤8：清理旧表（确认无问题后）
DROP TABLE orders_old;
```

### 5.2 分区表合并

```sql
-- 场景：将多个小分区合并为大分区

-- 步骤1：创建新的大分区
CREATE TABLE orders_2024_h1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-07-01');

-- 步骤2：移动数据
INSERT INTO orders_2024_h1
SELECT * FROM orders_2024_q1
UNION ALL
SELECT * FROM orders_2024_q2;

-- 步骤3：分离旧分区
ALTER TABLE orders DETACH PARTITION orders_2024_q1;
ALTER TABLE orders DETACH PARTITION orders_2024_q2;

-- 步骤4：删除旧分区
DROP TABLE orders_2024_q1;
DROP TABLE orders_2024_q2;
```

---

## 6. 完整生产案例

### 6.1 案例：时序数据分区方案（IoT场景）

**需求**：

- 每天10亿条IoT事件
- 保留90天数据
- 查询最近7天数据（90%查询）
- 查询历史数据（10%查询）

**方案设计**：

```sql
-- 1. 创建分区表（按小时分区）
CREATE TABLE iot_events (
    event_id bigserial,
    device_id bigint NOT NULL,
    event_time timestamptz NOT NULL,
    event_type text,
    payload jsonb,
    PRIMARY KEY (event_id, event_time)
) PARTITION BY RANGE (event_time);

-- 2. 使用pg_partman自动管理
SELECT partman.create_parent(
    p_parent_table => 'public.iot_events',
    p_control => 'event_time',
    p_type => 'native',
    p_interval => 'hourly',
    p_premake => 168,         -- 提前创建7天（168小时）
    p_start_partition => date_trunc('hour', now())::text
);

-- 3. 配置保留（90天）
UPDATE partman.part_config
SET retention = '90 days',
    retention_keep_table = false,
    optimize_constraint = 100  -- 每100个分区优化约束
WHERE parent_table = 'public.iot_events';

-- 4. 创建索引模板
CREATE INDEX ON iot_events (device_id, event_time DESC);
CREATE INDEX ON iot_events USING gin(payload);

-- 5. 配置autovacuum（按小时分区，快速VACUUM）
ALTER TABLE iot_events SET (
    autovacuum_vacuum_scale_factor = 0.0,
    autovacuum_vacuum_threshold = 5000,
    autovacuum_analyze_scale_factor = 0.0,
    autovacuum_analyze_threshold = 5000
);

-- 6. 查询优化
-- 最近7天（热数据）
EXPLAIN (ANALYZE, COSTS)
SELECT device_id, COUNT(*)
FROM iot_events
WHERE event_time >= now() - interval '7 days'
GROUP BY device_id;
-- 只扫描168个分区（7天）

-- 历史数据（归档查询）
EXPLAIN (ANALYZE, COSTS)
SELECT device_id, COUNT(*)
FROM iot_events
WHERE event_time BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY device_id;
-- 只扫描744个分区（31天）
```

### 6.2 案例：多租户SaaS分区方案

```sql
-- 需求：1000+租户，按租户隔离数据

-- 方案1：按租户哈希分区（16个分区）
CREATE TABLE tenant_data (
    tenant_id int NOT NULL,
    user_id bigint NOT NULL,
    data jsonb,
    created_at timestamptz DEFAULT now(),
    PRIMARY KEY (tenant_id, user_id)
) PARTITION BY HASH (tenant_id);

-- 创建16个哈希分区
DO $$
BEGIN
    FOR i IN 0..15 LOOP
        EXECUTE format(
            'CREATE TABLE tenant_data_%s PARTITION OF tenant_data FOR VALUES WITH (MODULUS 16, REMAINDER %s)',
            i, i
        );
    END LOOP;
END $$;

-- 查询（自动路由到特定分区）
EXPLAIN SELECT * FROM tenant_data WHERE tenant_id = 123;
-- 只扫描1个分区（tenant_data_11，假设123 % 16 = 11）

-- 方案2：按租户+时间复合分区
CREATE TABLE tenant_orders (
    tenant_id int NOT NULL,
    order_id bigserial,
    order_date date NOT NULL,
    amount numeric,
    PRIMARY KEY (tenant_id, order_id, order_date)
) PARTITION BY RANGE (order_date);

-- 创建月度分区
CREATE TABLE tenant_orders_2024_01 PARTITION OF tenant_orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01')
    PARTITION BY HASH (tenant_id);

-- 创建租户哈希子分区
DO $$
BEGIN
    FOR i IN 0..7 LOOP
        EXECUTE format(
            'CREATE TABLE tenant_orders_2024_01_%s PARTITION OF tenant_orders_2024_01 FOR VALUES WITH (MODULUS 8, REMAINDER %s)',
            i, i
        );
    END LOOP;
END $$;

-- 查询（同时裁剪时间和租户）
EXPLAIN SELECT * FROM tenant_orders
WHERE tenant_id = 123
  AND order_date BETWEEN '2024-01-01' AND '2024-01-31';
-- 只扫描1个子分区
```

---

## 7. 分区表最佳实践

### 7.1 分区设计原则

✅ **DO（应该做）**：

1. **选择合适的分区键**：
   - 时序数据：按时间分区
   - 地理数据：按地区分区
   - 多租户：按tenant_id分区
   - 负载均衡：哈希分区

2. **合理的分区粒度**：
   - 每个分区：100万-1000万行
   - 总分区数：<1000个
   - 权衡：分区太多→规划慢，分区太少→裁剪效果差

3. **分区键在主键中**：

   ```sql
   PRIMARY KEY (order_id, order_date)  -- ✅ 包含分区键
   ```

4. **提前创建分区**：
   - 避免运行时创建分区（影响性能）
   - 使用pg_partman提前创建

5. **定期清理旧分区**：
   - 自动化删除或归档
   - 节省存储空间

❌ **DON'T（不要做）**：

1. **分区键不在主键**：

   ```sql
   PRIMARY KEY (order_id)  -- ❌ 不包含分区键
   ```

2. **分区过多**：

   ```sql
   -- ❌ 按小时分区，保留10年 = 87600个分区（太多）
   PARTITION BY RANGE (event_time)  -- 改为按天或按月
   ```

3. **使用FOREIGN KEY指向分区表**：
   - PostgreSQL限制：外键不支持跨分区

4. **频繁跨分区查询**：

   ```sql
   -- ❌ 没有分区键，扫描所有分区
   SELECT * FROM orders WHERE customer_id = 123;
   ```

### 7.2 分区监控

```sql
-- 监控1：分区大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'orders_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 监控2：分区数量
SELECT
    parent.relname AS parent_table,
    COUNT(*) AS partition_count,
    SUM(child.reltuples) AS total_rows,
    pg_size_pretty(SUM(pg_total_relation_size(child.oid))) AS total_size
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child ON pg_inherits.inhrelid = child.oid
WHERE parent.relname = 'orders'
GROUP BY parent.relname;

-- 监控3：空分区
SELECT
    schemaname,
    tablename,
    n_live_tup
FROM pg_stat_user_tables
WHERE tablename LIKE 'orders_%'
  AND n_live_tup = 0
ORDER BY tablename;

-- 监控4：最新分区状态
SELECT
    schemaname,
    tablename,
    n_live_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze
FROM pg_stat_user_tables
WHERE tablename LIKE 'orders_2025%'
ORDER BY tablename DESC
LIMIT 5;

-- 监控5：查询分区裁剪效果
-- 使用pg_stat_statements
SELECT
    query,
    calls,
    mean_exec_time,
    plans  -- PostgreSQL 13+
FROM pg_stat_statements
WHERE query LIKE '%orders%'
ORDER BY calls DESC
LIMIT 10;
```

---

## 📚 参考资源

### 官方文档

1. [Table Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)
2. [Partition Pruning](https://www.postgresql.org/docs/current/ddl-partitioning.html#DDL-PARTITION-PRUNING)
3. [pg_partman](https://github.com/pgpartman/pg_partman)

### 最佳实践

1. [Partitioning Best Practices](https://www.postgresql.org/docs/current/ddl-partitioning.html#DDL-PARTITIONING-BEST-PRACTICES)
2. [When to Use Partitioning](https://wiki.postgresql.org/wiki/Table_partitioning)

---

**创建时间**: 2025年1月
**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**难度等级**: ⭐⭐⭐⭐ 高级

📊 **合理分区，性能倍增！**
