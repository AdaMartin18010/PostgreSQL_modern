# 分布式数据库中心架构深度分析 v2.0

> **文档类型**: 分布式DCA架构设计
> **涵盖技术**: Citus, pg_shard, FDW, 逻辑复制, 分片策略
> **创建日期**: 2026-03-04
> **文档长度**: 12000+字

---

## 目录

- [分布式数据库中心架构深度分析 v2.0](#分布式数据库中心架构深度分析-v20)
  - [目录](#目录)
  - [摘要](#摘要)
  - [1. 分布式DCA架构概览](#1-分布式dca架构概览)
    - [1.1 为什么需要分布式DCA](#11-为什么需要分布式dca)
    - [1.2 分布式DCA架构模式](#12-分布式dca架构模式)
  - [2. 数据分片策略](#2-数据分片策略)
    - [2.1 分片键选择](#21-分片键选择)
    - [2.2 分片算法](#22-分片算法)
    - [2.3 存储过程路由](#23-存储过程路由)
  - [3. Citus 分布式DCA实现](#3-citus-分布式dca实现)
    - [3.1 Citus架构组件](#31-citus架构组件)
    - [3.2 分布式表设计](#32-分布式表设计)
    - [3.3 分布式存储过程](#33-分布式存储过程)
  - [4. 读写分离架构](#4-读写分离架构)
    - [4.1 主从复制架构](#41-主从复制架构)
    - [4.2 读写分离实现](#42-读写分离实现)
    - [4.3 延迟处理策略](#43-延迟处理策略)
  - [5. 多主复制架构](#5-多主复制架构)
    - [5.1 冲突解决策略](#51-冲突解决策略)
    - [5.2 最终一致性模型](#52-最终一致性模型)
  - [6. FDW联邦架构](#6-fdw联邦架构)
    - [6.1 postgres\_fdw高级用法](#61-postgres_fdw高级用法)
    - [6.2 异构数据整合](#62-异构数据整合)
  - [7. 分布式事务管理](#7-分布式事务管理)
    - [7.1 两阶段提交](#71-两阶段提交)
    - [7.2 Saga模式实现](#72-saga模式实现)
  - [8. 分布式缓存层](#8-分布式缓存层)
    - [8.1 缓存一致性策略](#81-缓存一致性策略)
    - [8.2 缓存穿透防护](#82-缓存穿透防护)
  - [9. 跨数据中心架构](#9-跨数据中心架构)
    - [9.1 异地多活](#91-异地多活)
    - [9.2 数据同步策略](#92-数据同步策略)
  - [10. 分布式监控与可观测性](#10-分布式监控与可观测性)
  - [11. 持续推进计划](#11-持续推进计划)
    - [短期目标 (1-2周)](#短期目标-1-2周)
    - [中期目标 (1个月)](#中期目标-1个月)
    - [长期目标 (3个月)](#长期目标-3个月)

---

## 摘要

随着业务规模扩大，单机PostgreSQL面临性能和容量瓶颈。
本文档探讨如何在分布式环境中实施数据库中心架构(DCA)，涵盖数据分片、读写分离、多主复制、联邦查询等核心模式，提供完整的存储过程分布式编程模型。

**核心挑战与解决方案**:

- **数据分布**: 分片键选择 + 路由存储过程
- **事务一致性**: 2PC + Saga分布式事务
- **读写分离**: 自动路由 + 延迟处理
- **跨DC部署**: 逻辑复制 + 冲突解决

---

## 1. 分布式DCA架构概览

### 1.1 为什么需要分布式DCA

```text
┌─────────────────────────────────────────────────────────────────────┐
│  单机PostgreSQL的局限性                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  数据规模              查询性能              可用性                   │
│  ━━━━━━━━━━━━         ━━━━━━━━━━━━         ━━━━━━━━━━━━             │
│  单表>100GB           复杂查询>1s           单点故障                  │
│  单库>1TB             并发<1000 QPS         维护窗口                 │
│  无法水平扩展         CPU/IO瓶颈            地域延迟                  │
│                                                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                                     │
│  分布式DCA解决方案                                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐          │
│  │  分片1   │   │  分片2    │   │  分片3   │   │  分片N   │         │
│  │ (节点1)  │   │ (节点2)   │   │ (节点3)  │   │ (节点N)  │         │
│  │ ┌──────┐ │   │ ┌──────┐ │   │ ┌──────┐ │   │ ┌──────┐ │         │
│  │ │ 存储 │ │   │ │ 存储 │ │   │ │ 存储 │ │   │ │ 存储 │ │         │
│  │ │ 过程 │ │   │ │ 过程 │ │   │ │ 过程 │ │   │ │ 过程 │ │         │
│  │ └──┬───┘ │   │ └──┬───┘ │   │ └──┬───┘ │   │ └──┬───┘ │         │
│  └────┼────┘   └────┼────┘   └────┼────┘   └────┼────┘              │
│       │             │             │             │                   │
│       └─────────────┴─────────────┴─────────────┘                   │
│                     │                                               │
│              ┌──────┴──────┐                                        │
│              │  协调器节点  │  ← 存储过程路由 + 分布式事务             │
│              │  (Coordinator) │                                     │
│              └─────────────┘                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 分布式DCA架构模式

| 模式 | 适用场景 | 复杂度 | 一致性 | 扩展性 |
|-----|---------|-------|-------|-------|
| **垂直分片** | 按业务模块拆分 | 低 | 强 | 有限 |
| **水平分片** | 单表数据量大 | 中 | 强 | 高 |
| **读写分离** | 读多写少 | 低 | 最终 | 中 |
| **多主复制** | 多地域写入 | 高 | 冲突解决 | 高 |
| **联邦查询** | 异构数据源 | 中 | 依赖外部 | 中 |

---

## 2. 数据分片策略

### 2.1 分片键选择

```sql
-- ============================================
-- 分片键选择策略与最佳实践
-- ============================================

-- 1. 租户ID分片（多租户SaaS）
CREATE TABLE tenant_orders (
    order_id UUID DEFAULT uuidv7(),
    tenant_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    total_amount DECIMAL(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (tenant_id, order_id)  -- 复合主键，tenant_id在前
);

-- 2. 用户ID分片（社交/用户中心应用）
CREATE TABLE user_activities (
    activity_id BIGSERIAL,
    user_id BIGINT NOT NULL,
    activity_type VARCHAR(50),
    activity_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, activity_id)
);

-- 3. 时间范围分片（日志/时序数据）
CREATE TABLE event_logs (
    log_id UUID DEFAULT uuidv7(),
    event_time TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(50),
    payload JSONB,
    -- 分区键为时间范围
    PRIMARY KEY (event_time, log_id)
) PARTITION BY RANGE (event_time);

-- 4. 地理位置分片（地图/LBS应用）
CREATE TABLE location_data (
    location_id UUID DEFAULT uuidv7(),
    geo_hash VARCHAR(12) NOT NULL,  -- 地理哈希作为分片键
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    payload JSONB,
    PRIMARY KEY (geo_hash, location_id)
);

-- 分片键评估函数
CREATE OR REPLACE FUNCTION fn_evaluate_shard_key(
    p_table_name TEXT,
    p_candidate_column TEXT
)
RETURNS TABLE (
    metric TEXT,
    value NUMERIC,
    assessment TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cardinality BIGINT;
    v_total_rows BIGINT;
    v_null_count BIGINT;
    v_skew_coefficient NUMERIC;
BEGIN
    -- 获取总行数
    EXECUTE format('SELECT COUNT(*) FROM %I', p_table_name) INTO v_total_rows;

    -- 获取基数（不同值数量）
    EXECUTE format('SELECT COUNT(DISTINCT %I) FROM %I', p_candidate_column, p_table_name)
    INTO v_cardinality;

    -- NULL值数量
    EXECUTE format('SELECT COUNT(*) FROM %I WHERE %I IS NULL', p_table_name, p_candidate_column)
    INTO v_null_count;

    -- 计算倾斜系数（最大值/平均值）
    EXECUTE format('
        SELECT MAX(cnt)::NUMERIC / NULLIF(AVG(cnt), 0)
        FROM (SELECT %I, COUNT(*) as cnt FROM %I GROUP BY %I) t
    ', p_candidate_column, p_table_name, p_candidate_column) INTO v_skew_coefficient;

    -- 返回评估指标
    RETURN QUERY SELECT
        'Cardinality Ratio'::TEXT,
        (v_cardinality::NUMERIC / NULLIF(v_total_rows, 0) * 100)::NUMERIC,
        CASE
            WHEN v_cardinality > v_total_rows * 0.1 THEN 'Excellent - High cardinality'
            WHEN v_cardinality > v_total_rows * 0.01 THEN 'Good - Moderate cardinality'
            ELSE 'Poor - Low cardinality, may cause hotspot'
        END;

    RETURN QUERY SELECT
        'Null Percentage'::TEXT,
        (v_null_count::NUMERIC / NULLIF(v_total_rows, 0) * 100)::NUMERIC,
        CASE
            WHEN v_null_count = 0 THEN 'Excellent - No nulls'
            WHEN v_null_count < v_total_rows * 0.01 THEN 'Good - Minimal nulls'
            ELSE 'Warning - High null percentage'
        END;

    RETURN QUERY SELECT
        'Skew Coefficient'::TEXT,
        COALESCE(v_skew_coefficient, 0),
        CASE
            WHEN v_skew_coefficient < 2 THEN 'Excellent - Even distribution'
            WHEN v_skew_coefficient < 5 THEN 'Good - Slight skew'
            WHEN v_skew_coefficient < 10 THEN 'Warning - Moderate skew'
            ELSE 'Poor - Severe skew, hotspot detected'
        END;
END;
$$;

-- 使用示例
-- SELECT * FROM fn_evaluate_shard_key('orders', 'tenant_id');
```

### 2.2 分片算法

```sql
-- ============================================
-- 分片路由算法实现
-- ============================================

-- 1. 哈希分片（最常用）
CREATE OR REPLACE FUNCTION fn_hash_shard(
    p_shard_key TEXT,
    p_num_shards INT DEFAULT 16
)
RETURNS INT
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    -- 使用PostgreSQL内置hash函数
    RETURN (hashtext(p_shard_key) & 0x7FFFFFFF) % p_num_shards;
END;
$$;

-- 2. 范围分片（时间序列）
CREATE OR REPLACE FUNCTION fn_range_shard(
    p_shard_key TIMESTAMPTZ,
    p_shard_interval INTERVAL DEFAULT INTERVAL '1 month'
)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    -- 返回分片名称，如 'shard_2026_01'
    RETURN 'shard_' || TO_CHAR(p_shard_key, 'YYYY_MM');
END;
$$;

-- 3. 一致性哈希（节点动态扩缩容）
CREATE TABLE consistent_hash_ring (
    node_id TEXT NOT NULL,
    virtual_node_id INT NOT NULL,
    hash_value INT NOT NULL,
    PRIMARY KEY (virtual_node_id, node_id)
);

CREATE OR REPLACE FUNCTION fn_consistent_hash_shard(
    p_shard_key TEXT,
    OUT p_node_id TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    -- 找到顺时针第一个节点
    SELECT node_id INTO p_node_id
    FROM consistent_hash_ring
    WHERE hash_value >= hashtext(p_shard_key)
    ORDER BY hash_value
    LIMIT 1;

    -- 如果没有找到，回绕到第一个节点
    IF p_node_id IS NULL THEN
        SELECT node_id INTO p_node_id
        FROM consistent_hash_ring
        ORDER BY hash_value
        LIMIT 1;
    END IF;
END;
$$;

-- 4. 复合分片（多维度）
CREATE OR REPLACE FUNCTION fn_composite_shard(
    p_tenant_id BIGINT,
    p_user_id BIGINT,
    p_num_tenant_shards INT DEFAULT 8,
    p_num_user_shards_per_tenant INT DEFAULT 4
)
RETURNS TABLE (
    tenant_shard INT,
    user_shard INT,
    full_shard_id TEXT
)
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    tenant_shard := p_tenant_id % p_num_tenant_shards;
    user_shard := (p_tenant_id * 1000000 + p_user_id) % p_num_user_shards_per_tenant;
    full_shard_id := tenant_shard || '_' || user_shard;
    RETURN NEXT;
END;
$$;
```

### 2.3 存储过程路由

```sql
-- ============================================
-- 分布式存储过程路由层
-- ============================================

-- 1. 分片路由配置表
CREATE TABLE shard_routing_config (
    shard_id TEXT PRIMARY KEY,
    node_host TEXT NOT NULL,
    node_port INT DEFAULT 5432,
    database_name TEXT NOT NULL,
    shard_key_min TEXT,
    shard_key_max TEXT,
    is_active BOOLEAN DEFAULT true,
    weight INT DEFAULT 1  -- 用于负载均衡
);

-- 2. 存储过程路由函数
CREATE OR REPLACE FUNCTION fn_route_to_shard(
    p_shard_key TEXT,
    OUT p_connection_string TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_shard_id TEXT;
    v_config RECORD;
BEGIN
    -- 计算分片ID
    v_shard_id := 'shard_' || fn_hash_shard(p_shard_key);

    -- 获取连接信息
    SELECT * INTO v_config
    FROM shard_routing_config
    WHERE shard_id = v_shard_id AND is_active = true;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No active shard found for key: %', p_shard_key;
    END IF;

    -- 构建连接字符串
    p_connection_string := format(
        'host=%s port=%s dbname=%s',
        v_config.node_host,
        v_config.node_port,
        v_config.database_name
    );
END;
$$;

-- 3. 分布式存储过程调用包装器
CREATE OR REPLACE PROCEDURE sp_distributed_call(
    IN p_shard_key TEXT,
    IN p_procedure_name TEXT,
    IN p_params JSONB,
    OUT p_result JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_conn TEXT;
    v_sql TEXT;
BEGIN
    -- 获取目标分片连接
    SELECT fn_route_to_shard(p_shard_key) INTO v_conn;

    -- 构建远程调用SQL
    v_sql := format(
        'SELECT * FROM %I(%s)',
        p_procedure_name,
        (SELECT string_agg(format('%L', value), ', ')
         FROM jsonb_each_text(p_params))
    );

    -- 使用dblink或postgres_fdw执行远程调用
    -- 这里简化处理，实际使用FDW
    SELECT * INTO p_result
    FROM dblink(v_conn, v_sql) AS t(result JSONB);

EXCEPTION WHEN OTHERS THEN
    -- 记录路由失败
    INSERT INTO shard_routing_errors (
        shard_key, procedure_name, error_message, error_time
    ) VALUES (p_shard_key, p_procedure_name, SQLERRM, NOW());
    RAISE;
END;
$$;

-- 4. 跨分片聚合存储过程（协调器）
CREATE OR REPLACE FUNCTION fn_cross_shard_aggregate(
    p_procedure_name TEXT,
    p_params JSONB DEFAULT '{}',
    p_parallel BOOLEAN DEFAULT true
)
RETURNS TABLE (
    shard_id TEXT,
    partial_result JSONB,
    execution_time_ms NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_shard RECORD;
    v_start_time TIMESTAMP;
BEGIN
    FOR v_shard IN SELECT * FROM shard_routing_config WHERE is_active = true
    LOOP
        v_start_time := clock_timestamp();

        BEGIN
            RETURN QUERY EXECUTE format(
                'SELECT %L, result::JSONB, %s
                 FROM dblink(%L, %L) AS t(result TEXT)',
                v_shard.shard_id,
                EXTRACT(EPOCH FROM (clock_timestamp() - v_start_time)) * 1000,
                format('host=%s port=%s dbname=%s',
                       v_shard.node_host, v_shard.node_port, v_shard.database_name),
                format('SELECT %s(%s)::TEXT', p_procedure_name,
                       COALESCE(p_params::TEXT, ''))
            );
        EXCEPTION WHEN OTHERS THEN
            -- 记录失败但继续处理其他分片
            shard_id := v_shard.shard_id;
            partial_result := jsonb_build_object('error', SQLERRM);
            execution_time_ms := -1;
            RETURN NEXT;
        END;
    END LOOP;
END;
$$;
```

---

## 3. Citus 分布式DCA实现

### 3.1 Citus架构组件

```
┌─────────────────────────────────────────────────────────────────────┐
│  Citus 分布式架构                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                     Coordinator (协调器)                       │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │  查询解析 → 计划生成 → 分布式优化器 → 任务分发            │ │ │
│  │  │  存储过程路由 → 分布式事务协调 → 结果聚合                 │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  │                        │                                      │ │
│  │  ┌─────────────────────┼─────────────────────────────────┐  │ │
│  │  │  pg_dist_partition  │ pg_dist_placement │ pg_dist_node │  │ │
│  │  │  (分片元数据)         │ (分片位置)         │ (节点信息)   │  │ │
│  │  └─────────────────────┴─────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                              │                                      │
│          ┌───────────────────┼───────────────────┐                  │
│          ▼                   ▼                   ▼                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │
│  │  Worker 1    │   │  Worker 2    │   │  Worker N    │            │
│  │ ┌──────────┐ │   │ ┌──────────┐ │   │ ┌──────────┐ │            │
│  │ │ 分片 1   │ │   │ │ 分片 2   │ │   │ │ 分片 N   │ │            │
│  │ │ 分片 4   │ │   │ │ 分片 5   │ │   │ │ 分片 N+1 │ │            │
│  │ └──────────┘ │   │ └──────────┘ │   │ └──────────┘ │            │
│  └──────────────┘   └──────────────┘   └──────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 分布式表设计

```sql
-- ============================================
-- Citus 分布式表设计与DCA存储过程
-- ============================================

-- 1. 启用Citus扩展
CREATE EXTENSION IF NOT EXISTS citus;

-- 2. 添加Worker节点
SELECT * FROM citus_add_node('worker1.example.com', 5432);
SELECT * FROM citus_add_node('worker2.example.com', 5432);
SELECT * FROM citus_add_node('worker3.example.com', 5432);

-- 3. 创建分布式订单表
CREATE TABLE distributed_orders (
    order_id UUID DEFAULT uuidv7(),
    tenant_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    order_data JSONB NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (tenant_id, order_id)
);

-- 4. 分发表（按tenant_id哈希分片）
SELECT create_distributed_table('distributed_orders', 'tenant_id');

-- 5. 创建共置表（与订单共置在同一分片）
CREATE TABLE distributed_order_items (
    item_id BIGSERIAL,
    tenant_id BIGINT NOT NULL,
    order_id UUID NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (tenant_id, item_id)
);

-- 共置到同一分片（关键！）
SELECT create_distributed_table('distributed_order_items', 'tenant_id',
                                colocate_with => 'distributed_orders');

-- 6. 创建参考表（全节点复制，小表）
CREATE TABLE product_catalog (
    product_id BIGINT PRIMARY KEY,
    sku VARCHAR(50) UNIQUE,
    product_name VARCHAR(200),
    base_price DECIMAL(10,2)
);

SELECT create_reference_table('product_catalog');

-- 7. 分布式存储过程（在协调器上执行）
CREATE OR REPLACE PROCEDURE sp_distributed_create_order(
    IN p_tenant_id BIGINT,
    IN p_user_id BIGINT,
    IN p_items JSONB,  -- [{"product_id": 1, "qty": 2}, ...]
    IN p_order_data JSONB,
    OUT p_order_id UUID,
    OUT p_total_amount DECIMAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_item JSONB;
    v_product RECORD;
BEGIN
    p_order_id := uuidv7();
    p_total_amount := 0;

    -- 计算总价（使用参考表查询）
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        SELECT base_price INTO v_product
        FROM product_catalog
        WHERE product_id = (v_item->>'product_id')::BIGINT;

        p_total_amount := p_total_amount +
            v_product.base_price * (v_item->>'qty')::INT;
    END LOOP;

    -- 插入订单（Citus自动路由到正确分片）
    INSERT INTO distributed_orders (
        order_id, tenant_id, user_id, order_data, total_amount
    ) VALUES (
        p_order_id, p_tenant_id, p_user_id, p_order_data, p_total_amount
    );

    -- 插入订单项（共置表，同一分片内事务）
    INSERT INTO distributed_order_items (
        tenant_id, order_id, product_id, quantity, unit_price
    )
    SELECT
        p_tenant_id,
        p_order_id,
        (elem->>'product_id')::BIGINT,
        (elem->>'qty')::INT,
        p.base_price
    FROM jsonb_array_elements(p_items) AS elem
    JOIN product_catalog p ON p.product_id = (elem->>'product_id')::BIGINT;

END;
$$;

-- 8. 分布式聚合查询（Citus自动并行化）
CREATE OR REPLACE FUNCTION fn_distributed_sales_report(
    p_tenant_id BIGINT,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    date_period DATE,
    order_count BIGINT,
    total_revenue DECIMAL,
    avg_order_value DECIMAL
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    -- Citus自动将查询推送到各Worker并行执行
    RETURN QUERY
    SELECT
        created_at::DATE as date_period,
        COUNT(*) as order_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_order_value
    FROM distributed_orders
    WHERE tenant_id = p_tenant_id
      AND created_at BETWEEN p_start_date AND p_end_date
    GROUP BY created_at::DATE
    ORDER BY date_period;
END;
$$;

-- 9. 跨分片事务（2PC）
CREATE OR REPLACE PROCEDURE sp_cross_shard_transfer(
    IN p_from_tenant_id BIGINT,
    IN p_to_tenant_id BIGINT,
    IN p_amount DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 开启分布式事务（Citus自动使用2PC）
    PERFORM citus_begin_transaction();

    -- 扣减转出方
    UPDATE distributed_orders
    SET total_amount = total_amount - p_amount
    WHERE tenant_id = p_from_tenant_id
      AND order_id = 'RESERVE_ACCOUNT';

    -- 增加转入方
    UPDATE distributed_orders
    SET total_amount = total_amount + p_amount
    WHERE tenant_id = p_to_tenant_id
      AND order_id = 'RESERVE_ACCOUNT';

    -- 提交分布式事务
    PERFORM citus_commit_transaction();

EXCEPTION WHEN OTHERS THEN
    PERFORM citus_rollback_transaction();
    RAISE;
END;
$$;
```

### 3.3 分布式存储过程

```sql
-- ============================================
-- Citus 高级分布式存储过程模式
-- ============================================

-- 1. 分布式ID生成（避免冲突）
CREATE OR REPLACE FUNCTION fn_distributed_id(
    p_node_id INT DEFAULT 0
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_sequence BIGINT;
    v_timestamp BIGINT;
BEGIN
    -- 雪花算法风格：时间戳(41位) + 节点ID(10位) + 序列号(12位)
    v_timestamp := (EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT - 1609459200000; -- 2021-01-01
    v_sequence := nextval('distributed_id_seq') % 4096;

    RETURN (v_timestamp << 22) | ((p_node_id & 1023) << 12) | v_sequence;
END;
$$;

-- 2. 分布式批量插入（并行）
CREATE OR REPLACE PROCEDURE sp_distributed_bulk_insert(
    IN p_tenant_id BIGINT,
    IN p_records JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 使用COPY协议批量插入（Citus优化）
    INSERT INTO distributed_orders (
        order_id, tenant_id, user_id, order_data, total_amount
    )
    SELECT
        uuidv7(),
        p_tenant_id,
        (elem->>'user_id')::BIGINT,
        elem->'data',
        (elem->>'total')::DECIMAL
    FROM jsonb_array_elements(p_records) AS elem;

    -- Citus自动并行分发到各Worker
END;
$$;

-- 3. 分布式MapReduce模式
CREATE OR REPLACE FUNCTION fn_mapreduce_order_stats(
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    tenant_id BIGINT,
    stat_name TEXT,
    stat_value DECIMAL
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    -- Map阶段：各Worker本地聚合
    -- Reduce阶段：协调器合并结果
    RETURN QUERY
    SELECT
        o.tenant_id,
        'total_revenue'::TEXT as stat_name,
        SUM(o.total_amount) as stat_value
    FROM distributed_orders o
    WHERE o.created_at BETWEEN p_start_date AND p_end_date
    GROUP BY o.tenant_id

    UNION ALL

    SELECT
        o.tenant_id,
        'order_count'::TEXT,
        COUNT(*)::DECIMAL
    FROM distributed_orders o
    WHERE o.created_at BETWEEN p_start_date AND p_end_date
    GROUP BY o.tenant_id;
END;
$$;
```

---

## 4. 读写分离架构

### 4.1 主从复制架构

```
┌─────────────────────────────────────────────────────────────────────┐
│  主从复制 + 读写分离架构                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐                                                │
│  │   Primary       │  ← 写入 + 实时查询                              │
│  │   (主库)         │                                                │
│  │  ┌───────────┐  │                                                │
│  │  │ 存储过程   │  │  CREATE, UPDATE, DELETE                        │
│  │  │ (写操作)   │  │                                                │
│  │  └───────────┘  │                                                │
│  └────────┬────────┘                                                │
│           │ WAL Stream                                               │
│           ▼                                                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Streaming Replication                       │  │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    │  │
│  │  │ Standby │    │ Standby │    │ Standby │    │ Standby │    │  │
│  │  │  1      │    │  2      │    │  3      │    │  N      │    │  │
│  │  │ (只读)   │    │ (只读)   │    │ (只读)   │    │ (只读)   │    │  │
│  │  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘    │  │
│  └───────┼──────────────┼──────────────┼──────────────┼─────────┘  │
│          │              │              │              │            │
│          └──────────────┴──────────────┴──────────────┘            │
│                     │                                                │
│                     ▼                                                │
│            ┌─────────────────┐                                       │
│            │  连接池/代理     │  ← PgPool-II / HAProxy               │
│            │  (读写路由)      │                                       │
│            └────────┬────────┘                                       │
│                     │                                                │
│           ┌────────┴────────┐                                       │
│           ▼                 ▼                                       │
│      写请求 ────────────► 读请求                                     │
│      (Primary)            (Standby轮询)                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 读写分离实现

```sql
-- ============================================
-- 读写分离存储过程路由
-- ============================================

-- 1. 创建读写分离视图
CREATE VIEW v_orders_readonly AS
SELECT * FROM orders;

-- 在主库上授予只读权限
GRANT SELECT ON v_orders_readonly TO app_readonly_role;

-- 2. 存储过程标记（区分读写）
CREATE OR REPLACE PROCEDURE sp_order_create(
    IN p_user_id BIGINT,
    IN p_items JSONB,
    OUT p_order_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 强制使用主库连接
    PERFORM set_config('app.connection_target', 'primary', true);

    p_order_id := uuidv7();

    INSERT INTO orders (id, user_id, items, status)
    VALUES (p_order_id, p_user_id, p_items, 'pending');
END;
$$;

COMMENT ON PROCEDURE sp_order_create IS '@write_operation:true';

CREATE OR REPLACE FUNCTION fn_order_list(
    p_user_id BIGINT,
    p_page INT DEFAULT 1
)
RETURNS TABLE (order_id UUID, status VARCHAR, total DECIMAL)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    -- 标记为只读，可被路由到从库
    PERFORM set_config('app.connection_target', 'standby', true);

    RETURN QUERY
    SELECT o.id, o.status, o.total_amount
    FROM orders o
    WHERE o.user_id = p_user_id
    ORDER BY o.created_at DESC
    LIMIT 20 OFFSET (p_page - 1) * 20;
END;
$$;

COMMENT ON FUNCTION fn_order_list IS '@read_operation:true';

-- 3. 复制延迟感知查询
CREATE OR REPLACE FUNCTION fn_order_check_with_lag(
    p_order_id UUID,
    p_max_lag_seconds INT DEFAULT 5
)
RETURNS TABLE (
    order_id UUID,
    status VARCHAR,
    replication_lag INTERVAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_lag INTERVAL;
BEGIN
    -- 检查复制延迟
    SELECT NOW() - pg_last_xact_replay_timestamp() INTO v_lag;

    IF v_lag > make_interval(secs => p_max_lag_seconds) THEN
        -- 延迟过大，切换到主库查询
        PERFORM set_config('app.force_primary', 'true', true);
    END IF;

    RETURN QUERY
    SELECT
        o.id,
        o.status,
        v_lag as replication_lag
    FROM orders o
    WHERE o.id = p_order_id;
END;
$$;

-- 4. 应用层连接路由（伪代码）
/*
class DCAConnectionRouter:
    def get_connection(self, procedure_name):
        # 查询存储过程元数据
        meta = self.db.execute("""
            SELECT obj_description(%s::regprocedure) as comment
        """, (procedure_name,))

        if '@write_operation:true' in meta['comment']:
            return self.primary_pool.getconn()
        elif '@read_operation:true' in meta['comment']:
            return self.standby_pool.getconn()
        else:
            # 默认主库
            return self.primary_pool.getconn()
*/
```

### 4.3 延迟处理策略

```sql
-- ============================================
-- 复制延迟处理策略
-- ============================================

-- 1. 延迟检测函数
CREATE OR REPLACE FUNCTION fn_check_replication_lag()
RETURNS TABLE (
    standby_name TEXT,
    lag_bytes BIGINT,
    lag_seconds NUMERIC,
    is_healthy BOOLEAN
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        client_addr::TEXT as standby_name,
        pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) as lag_bytes,
        EXTRACT(EPOCH FROM (NOW() - backend_start)) as lag_seconds,
        pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) < 100000000 as is_healthy
    FROM pg_stat_replication;
$$;

-- 2. 延迟补偿读取（写后读一致性）
CREATE OR REPLACE FUNCTION fn_read_after_write(
    p_order_id UUID,
    p_write_timestamp TIMESTAMPTZ
)
RETURNS TABLE (
    order_id UUID,
    status VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_lag INTERVAL;
    v_result RECORD;
BEGIN
    -- 尝试从从库读取
    SELECT status INTO v_result
    FROM orders
    WHERE id = p_order_id;

    IF FOUND AND v_result.status IS NOT NULL THEN
        RETURN QUERY SELECT p_order_id, v_result.status;
        RETURN;
    END IF;

    -- 未找到，检查延迟
    SELECT MAX(NOW() - pg_last_xact_replay_timestamp()) INTO v_lag
    FROM pg_stat_replication;

    IF v_lag > INTERVAL '1 second' THEN
        -- 可能延迟导致，切换到主库
        RAISE NOTICE 'Switching to primary due to replication lag: %', v_lag;

        -- 实际应用中通过连接池切换
        PERFORM pg_sleep(0.1);  -- 短暂等待

        -- 重试
        SELECT status INTO v_result
        FROM orders
        WHERE id = p_order_id;

        IF FOUND THEN
            RETURN QUERY SELECT p_order_id, v_result.status;
        END IF;
    END IF;
END;
$$;

-- 3. 会话粘性（Session Stickiness）
CREATE TABLE session_write_markers (
    session_id TEXT PRIMARY KEY,
    last_write_time TIMESTAMPTZ DEFAULT NOW(),
    force_primary_until TIMESTAMPTZ
);

CREATE OR REPLACE PROCEDURE sp_mark_session_write(IN p_session_id TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO session_write_markers (session_id, force_primary_until)
    VALUES (p_session_id, NOW() + INTERVAL '2 seconds')
    ON CONFLICT (session_id)
    DO UPDATE SET
        last_write_time = NOW(),
        force_primary_until = NOW() + INTERVAL '2 seconds';
END;
$$;

CREATE OR REPLACE FUNCTION fn_should_use_primary(p_session_id TEXT)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1 FROM session_write_markers
        WHERE session_id = p_session_id
          AND force_primary_until > NOW()
    );
$$;
```

---

## 5. 多主复制架构

### 5.1 冲突解决策略

```sql
-- ============================================
-- 多主复制冲突解决
-- ============================================

-- 1. 冲突检测表
CREATE TABLE replication_conflicts (
    conflict_id UUID PRIMARY KEY DEFAULT uuidv7(),
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    node_origin TEXT NOT NULL,
    node_target TEXT NOT NULL,
    local_version JSONB,
    remote_version JSONB,
    resolution_strategy TEXT,  -- 'last_write_wins', 'merge', 'manual'
    resolved_version JSONB,
    resolved_at TIMESTAMPTZ,
    resolved_by TEXT
);

-- 2. 向量时钟冲突检测
CREATE TABLE vector_clock_columns (
    table_name TEXT PRIMARY KEY,
    vc_column_name TEXT DEFAULT 'vector_clock'
);

CREATE OR REPLACE FUNCTION fn_update_vector_clock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_node_id TEXT;
    v_current_vc JSONB;
BEGIN
    v_node_id := current_setting('app.node_id', true);
    v_current_vc := COALESCE(NEW.vector_clock, '{}'::JSONB);

    -- 递增本地时钟
    NEW.vector_clock := jsonb_set(
        v_current_vc,
        ARRAY[v_node_id],
        COALESCE((v_current_vc->>v_node_id)::INT, 0)::TEXT::JSONB
    );

    RETURN NEW;
END;
$$;

-- 3. 最后写入胜利（LWW）策略
CREATE OR REPLACE FUNCTION fn_conflict_resolution_lww()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_local_time TIMESTAMPTZ;
    v_remote_time TIMESTAMPTZ;
BEGIN
    v_local_time := (OLD.vector_clock->>'_timestamp')::TIMESTAMPTZ;
    v_remote_time := (NEW.vector_clock->>'_timestamp')::TIMESTAMPTZ;

    IF v_remote_time > v_local_time THEN
        -- 远程更新更新，接受
        RETURN NEW;
    ELSE
        -- 本地更新更新，拒绝
        INSERT INTO replication_conflicts (
            table_name, record_id, node_origin, node_target,
            local_version, remote_version, resolution_strategy
        ) VALUES (
            TG_TABLE_NAME,
            OLD.id::TEXT,
            NEW._origin_node,
            current_setting('app.node_id'),
            to_jsonb(OLD),
            to_jsonb(NEW),
            'last_write_wins_rejected'
        );
        RETURN NULL;
    END IF;
END;
$$;

-- 4. 合并策略（CRDT风格）
CREATE OR REPLACE FUNCTION fn_conflict_resolution_merge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_merged JSONB;
BEGIN
    -- 合并JSONB字段（取并集）
    v_merged := OLD.data || NEW.data;

    -- 数值字段取最大值
    IF (OLD.data->>'counter')::INT > (NEW.data->>'counter')::INT THEN
        v_merged := jsonb_set(v_merged, '{counter}', OLD.data->'counter');
    END IF;

    NEW.data := v_merged;
    NEW.updated_at := GREATEST(OLD.updated_at, NEW.updated_at);

    -- 记录冲突解决
    INSERT INTO replication_conflicts (
        table_name, record_id, resolution_strategy, resolved_version
    ) VALUES (
        TG_TABLE_NAME, OLD.id::TEXT, 'merge', to_jsonb(NEW)
    );

    RETURN NEW;
END;
$$;
```

### 5.2 最终一致性模型

```sql
-- ============================================
-- 最终一致性存储过程设计
-- ============================================

-- 1. 因果一致性标记
CREATE TABLE causal_markers (
    marker_id UUID PRIMARY KEY DEFAULT uuidv7(),
    session_id TEXT NOT NULL,
    operation_sequence BIGINT NOT NULL,
    depends_on UUID[],  -- 依赖的前序操作
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 因果一致性读取
CREATE OR REPLACE FUNCTION fn_causal_read(
    p_session_id TEXT,
    p_table_name TEXT,
    p_record_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_last_marker UUID;
    v_result JSONB;
BEGIN
    -- 获取会话最后写入标记
    SELECT marker_id INTO v_last_marker
    FROM causal_markers
    WHERE session_id = p_session_id
    ORDER BY operation_sequence DESC
    LIMIT 1;

    -- 等待依赖操作同步
    PERFORM pg_sleep(0.5);  -- 简化实现，实际应检查复制状态

    -- 执行读取
    EXECUTE format('SELECT to_jsonb(t) FROM %I t WHERE id = $1', p_table_name)
    INTO v_result
    USING p_record_id;

    RETURN v_result;
END;
$$;

-- 3. 单调读一致性
CREATE TABLE read_checkpoint (
    session_id TEXT PRIMARY KEY,
    last_read_lsn PG_LSN,
    last_read_time TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION fn_monotonic_read(
    p_session_id TEXT,
    p_query TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_checkpoint PG_LSN;
    v_current_lsn PG_LSN;
BEGIN
    -- 获取会话检查点
    SELECT last_read_lsn INTO v_checkpoint
    FROM read_checkpoint
    WHERE session_id = p_session_id;

    -- 等待复制追上检查点
    LOOP
        SELECT pg_last_xact_replay_timestamp() INTO v_current_lsn;
        EXIT WHEN v_current_lsn >= v_checkpoint;
        PERFORM pg_sleep(0.1);
    END LOOP;

    -- 执行查询
    RETURN (EXECUTE p_query);
END;
$$;
```

---

## 6. FDW联邦架构

### 6.1 postgres_fdw高级用法

```sql
-- ============================================
-- Foreign Data Wrapper 联邦查询
-- ============================================

-- 1. 配置外部服务器
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER legacy_db
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'legacy.example.com', port '5432', dbname 'legacy');

CREATE USER MAPPING FOR CURRENT_USER
    SERVER legacy_db
    OPTIONS (user 'fdw_reader', password 'secret');

-- 2. 导入外部表
IMPORT FOREIGN SCHEMA public
    LIMIT TO (customers, products)
    FROM SERVER legacy_db
    INTO external_schema;

-- 3. 联邦查询存储过程
CREATE OR REPLACE FUNCTION fn_federated_customer_report(
    p_customer_id BIGINT
)
RETURNS TABLE (
    customer_name TEXT,
    legacy_orders BIGINT,
    new_orders BIGINT,
    total_value DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.name as customer_name,
        COALESCE(lo.order_count, 0) as legacy_orders,
        COALESCE(no.order_count, 0) as new_orders,
        COALESCE(lo.total_value, 0) + COALESCE(no.total_value, 0) as total_value
    FROM customers c
    -- 本地新系统数据
    LEFT JOIN (
        SELECT user_id, COUNT(*) as order_count, SUM(total) as total_value
        FROM new_orders
        GROUP BY user_id
    ) no ON no.user_id = c.id
    -- 外部旧系统数据
    LEFT JOIN (
        SELECT customer_id, COUNT(*) as order_count, SUM(amount) as total_value
        FROM external_schema.orders
        GROUP BY customer_id
    ) lo ON lo.customer_id = c.id
    WHERE c.id = p_customer_id;
END;
$$;

-- 4. 跨库事务（两阶段提交）
CREATE OR REPLACE PROCEDURE sp_federated_transfer(
    IN p_from_db TEXT,  -- 'local' 或外部服务器名
    IN p_to_db TEXT,
    IN p_account_id BIGINT,
    IN p_amount DECIMAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_prepared_xid TEXT;
BEGIN
    v_prepared_xid := 'xfer_' || txid_current();

    -- 阶段1：准备
    IF p_from_db = 'local' THEN
        UPDATE accounts SET balance = balance - p_amount WHERE id = p_account_id;
    ELSE
        EXECUTE format('PREPARE TRANSACTION %L', v_prepared_xid)
        USING p_amount, p_account_id;
    END IF;

    IF p_to_db = 'local' THEN
        UPDATE accounts SET balance = balance + p_amount WHERE id = p_account_id;
    ELSE
        EXECUTE format('PREPARE TRANSACTION %L', v_prepared_xid || '_2');
    END IF;

    -- 阶段2：提交
    COMMIT PREPARED v_prepared_xid;
    COMMIT PREPARED v_prepared_xid || '_2';

EXCEPTION WHEN OTHERS THEN
    -- 回滚
    ROLLBACK PREPARED v_prepared_xid;
    ROLLBACK PREPARED v_prepared_xid || '_2';
    RAISE;
END;
$$;
```

### 6.2 异构数据整合

```sql
-- ============================================
-- 异构数据源整合
-- ============================================

-- 1. MySQL外部表（使用mysql_fdw）
CREATE SERVER mysql_orders
    FOREIGN DATA WRAPPER mysql_fdw
    OPTIONS (host 'mysql.example.com', port '3306');

CREATE USER MAPPING FOR CURRENT_USER
    SERVER mysql_orders
    OPTIONS (username 'reader', password 'secret');

IMPORT FOREIGN SCHEMA ecommerce
    LIMIT TO (orders)
    FROM SERVER mysql_orders
    INTO mysql_data;

-- 2. 统一视图（跨异构数据库）
CREATE VIEW unified_orders AS
SELECT
    order_id,
    'postgres' as source_system,
    customer_id,
    order_date,
    total_amount
FROM local_orders

UNION ALL

SELECT
    id::TEXT as order_id,
    'mysql' as source_system,
    user_id::BIGINT as customer_id,
    created_at as order_date,
    amount::DECIMAL as total_amount
FROM mysql_data.orders;

-- 3. 跨系统聚合存储过程
CREATE OR REPLACE FUNCTION fn_cross_system_revenue(
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    date_period DATE,
    postgres_revenue DECIMAL,
    mysql_revenue DECIMAL,
    total_revenue DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(p.date_period, m.date_period) as date_period,
        COALESCE(p.revenue, 0) as postgres_revenue,
        COALESCE(m.revenue, 0) as mysql_revenue,
        COALESCE(p.revenue, 0) + COALESCE(m.revenue, 0) as total_revenue
    FROM (
        SELECT order_date::DATE as date_period, SUM(total_amount) as revenue
        FROM local_orders
        WHERE order_date BETWEEN p_start_date AND p_end_date
        GROUP BY order_date::DATE
    ) p
    FULL OUTER JOIN (
        SELECT created_at::DATE as date_period, SUM(amount::DECIMAL) as revenue
        FROM mysql_data.orders
        WHERE created_at BETWEEN p_start_date AND p_end_date
        GROUP BY created_at::DATE
    ) m ON p.date_period = m.date_period
    ORDER BY date_period;
END;
$$;
```

---

## 7. 分布式事务管理

### 7.1 两阶段提交

```sql
-- ============================================
-- 两阶段提交分布式事务
-- ============================================

-- 1. 分布式事务协调表
CREATE TABLE distributed_transactions (
    xid TEXT PRIMARY KEY,
    status VARCHAR(20),  -- 'preparing', 'prepared', 'committed', 'aborted'
    participants JSONB,  -- [{"node": "node1", "status": "prepared"}, ...]
    created_at TIMESTAMPTZ DEFAULT NOW(),
    committed_at TIMESTAMPTZ
);

-- 2. 存储过程：分布式转账（2PC）
CREATE OR REPLACE PROCEDURE sp_distributed_transfer_2pc(
    IN p_from_node TEXT,
    IN p_from_account TEXT,
    IN p_to_node TEXT,
    IN p_to_account TEXT,
    IN p_amount DECIMAL,
    OUT p_xid TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_participants JSONB;
BEGIN
    p_xid := 'dt_' || txid_current();

    -- 记录参与者
    v_participants := jsonb_build_array(
        jsonb_build_object('node', p_from_node, 'status', 'pending'),
        jsonb_build_object('node', p_to_node, 'status', 'pending')
    );

    INSERT INTO distributed_transactions (xid, status, participants)
    VALUES (p_xid, 'preparing', v_participants);

    -- 阶段1：准备
    -- 节点1准备
    PERFORM dblink_exec(
        format('host=%s', p_from_node),
        format('PREPARE TRANSACTION %L', p_xid)
    );

    -- 节点2准备
    PERFORM dblink_exec(
        format('host=%s', p_to_node),
        format('PREPARE TRANSACTION %L', p_xid)
    );

    -- 更新状态
    UPDATE distributed_transactions
    SET status = 'prepared',
        participants = jsonb_build_array(
            jsonb_build_object('node', p_from_node, 'status', 'prepared'),
            jsonb_build_object('node', p_to_node, 'status', 'prepared')
        )
    WHERE xid = p_xid;

    -- 阶段2：提交
    PERFORM dblink_exec(
        format('host=%s', p_from_node),
        format('COMMIT PREPARED %L', p_xid)
    );

    PERFORM dblink_exec(
        format('host=%s', p_to_node),
        format('COMMIT PREPARED %L', p_xid)
    );

    UPDATE distributed_transactions
    SET status = 'committed', committed_at = NOW()
    WHERE xid = p_xid;

EXCEPTION WHEN OTHERS THEN
    -- 回滚所有参与者
    PERFORM dblink_exec(
        format('host=%s', p_from_node),
        format('ROLLBACK PREPARED %L', p_xid)
    );
    PERFORM dblink_exec(
        format('host=%s', p_to_node),
        format('ROLLBACK PREPARED %L', p_xid)
    );

    UPDATE distributed_transactions
    SET status = 'aborted'
    WHERE xid = p_xid;

    RAISE;
END;
$$;

-- 3. 恢复挂起的事务
CREATE OR REPLACE PROCEDURE sp_recover_distributed_transactions()
LANGUAGE plpgsql
AS $$
DECLARE
    v_xid RECORD;
BEGIN
    FOR v_xid IN
        SELECT * FROM distributed_transactions
        WHERE status = 'prepared'
          AND created_at < NOW() - INTERVAL '1 minute'
    LOOP
        -- 根据业务规则决定提交或回滚
        -- 这里简化为提交
        PERFORM dblink_exec(
            format('host=%s', v_xid.participants->0->>'node'),
            format('COMMIT PREPARED %L', v_xid.xid)
        );

        UPDATE distributed_transactions
        SET status = 'committed', committed_at = NOW()
        WHERE xid = v_xid.xid;
    END LOOP;
END;
$$;
```

### 7.2 Saga模式实现

```sql
-- ============================================
-- Saga分布式事务模式
-- ============================================

-- 1. Saga编排表
CREATE TABLE saga_instances (
    saga_id UUID PRIMARY KEY DEFAULT uuidv7(),
    saga_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'running',  -- running, succeeded, failed, compensating
    current_step INT DEFAULT 0,
    steps JSONB NOT NULL,  -- 步骤定义
    step_results JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 2. 创建Saga
CREATE OR REPLACE FUNCTION fn_create_order_saga(
    p_user_id BIGINT,
    p_items JSONB,
    p_payment_info JSONB
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_saga_id UUID;
    v_steps JSONB;
BEGIN
    v_saga_id := uuidv7();

    v_steps := jsonb_build_array(
        jsonb_build_object(
            'step', 1,
            'action', 'create_order',
            'service', 'order_service',
            'compensate_action', 'cancel_order'
        ),
        jsonb_build_object(
            'step', 2,
            'action', 'reserve_inventory',
            'service', 'inventory_service',
            'compensate_action', 'release_inventory'
        ),
        jsonb_build_object(
            'step', 3,
            'action', 'process_payment',
            'service', 'payment_service',
            'compensate_action', 'refund_payment'
        ),
        jsonb_build_object(
            'step', 4,
            'action', 'confirm_order',
            'service', 'order_service',
            'compensate_action', null
        )
    );

    INSERT INTO saga_instances (saga_id, saga_type, steps)
    VALUES (v_saga_id, 'create_order', v_steps);

    RETURN v_saga_id;
END;
$$;

-- 3. 执行Saga步骤
CREATE OR REPLACE PROCEDURE sp_execute_saga_step(IN p_saga_id UUID)
LANGUAGE plpgsql
AS $$
DECLARE
    v_saga RECORD;
    v_current_step JSONB;
    v_step_result JSONB;
    v_success BOOLEAN;
BEGIN
    SELECT * INTO v_saga FROM saga_instances WHERE saga_id = p_saga_id;

    IF v_saga.status != 'running' THEN
        RETURN;
    END IF;

    v_current_step := v_saga.steps->v_saga.current_step;

    -- 执行当前步骤（调用远程服务）
    BEGIN
        SELECT * INTO v_step_result
        FROM fn_execute_saga_action(
            v_current_step->>'service',
            v_current_step->>'action',
            v_saga.saga_id
        );

        v_success := true;

    EXCEPTION WHEN OTHERS THEN
        v_success := false;
        v_step_result := jsonb_build_object('error', SQLERRM);
    END;

    IF v_success THEN
        -- 更新Saga状态
        UPDATE saga_instances
        SET
            current_step = current_step + 1,
            step_results = step_results || jsonb_build_array(v_step_result),
            status = CASE
                WHEN current_step + 1 >= jsonb_array_length(steps)
                THEN 'succeeded'::VARCHAR
                ELSE 'running'::VARCHAR
            END,
            completed_at = CASE
                WHEN current_step + 1 >= jsonb_array_length(steps)
                THEN NOW()
                ELSE NULL
            END
        WHERE saga_id = p_saga_id;
    ELSE
        -- 触发补偿
        UPDATE saga_instances
        SET status = 'compensating'
        WHERE saga_id = p_saga_id;

        PERFORM fn_compensate_saga(p_saga_id);
    END IF;
END;
$$;

-- 4. 补偿处理
CREATE OR REPLACE FUNCTION fn_compensate_saga(p_saga_id UUID)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_saga RECORD;
    v_step JSONB;
    i INT;
BEGIN
    SELECT * INTO v_saga FROM saga_instances WHERE saga_id = p_saga_id;

    -- 反向执行补偿
    FOR i IN REVERSE v_saga.current_step - 1..0 LOOP
        v_step := v_saga.steps->i;

        IF v_step ? 'compensate_action' AND v_step->>'compensate_action' IS NOT NULL THEN
            PERFORM fn_execute_saga_action(
                v_step->>'service',
                v_step->>'compensate_action',
                v_saga.saga_id
            );
        END IF;
    END LOOP;

    UPDATE saga_instances
    SET status = 'failed', completed_at = NOW()
    WHERE saga_id = p_saga_id;
END;
$$;
```

---

## 8. 分布式缓存层

### 8.1 缓存一致性策略

```sql
-- ============================================
-- 分布式缓存一致性
-- ============================================

-- 1. 缓存失效表（用于发布订阅）
CREATE TABLE cache_invalidation_events (
    event_id UUID PRIMARY KEY DEFAULT uuidv7(),
    cache_key TEXT NOT NULL,
    invalidation_type TEXT,  -- 'update', 'delete', 'refresh'
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 缓存感知存储过程（写穿透）
CREATE OR REPLACE PROCEDURE sp_cache_aware_update(
    IN p_table_name TEXT,
    IN p_record_id UUID,
    IN p_new_values JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cache_key TEXT;
    v_old_values JSONB;
BEGIN
    v_cache_key := format('%s:%s', p_table_name, p_record_id);

    -- 获取旧值
    EXECUTE format('SELECT to_jsonb(t) FROM %I t WHERE id = $1', p_table_name)
    INTO v_old_values
    USING p_record_id;

    -- 更新数据库
    EXECUTE format('
        UPDATE %I SET data = data || $1::JSONB, updated_at = NOW()
        WHERE id = $2
    ', p_table_name)
    USING p_new_values, p_record_id;

    -- 发布缓存失效事件
    INSERT INTO cache_invalidation_events (cache_key, invalidation_type, payload)
    VALUES (
        v_cache_key,
        'update',
        jsonb_build_object('old', v_old_values, 'new', p_new_values)
    );

    -- 通知缓存层（通过pg_notify或外部队列）
    PERFORM pg_notify('cache_invalidation', jsonb_build_object(
        'key', v_cache_key,
        'action', 'invalidate'
    )::TEXT);
END;
$$;

-- 3. 缓存预热存储过程
CREATE OR REPLACE PROCEDURE sp_cache_warmup(
    IN p_table_name TEXT,
    IN p_condition TEXT DEFAULT 'true',
    IN p_batch_size INT DEFAULT 1000
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cursor CURSOR FOR EXECUTE format(
        'SELECT id, to_jsonb(t) as data FROM %I t WHERE %s',
        p_table_name, p_condition
    );
    v_record RECORD;
    v_batch JSONB := '[]'::JSONB;
BEGIN
    OPEN v_cursor;

    LOOP
        FETCH v_cursor INTO v_record;
        EXIT WHEN NOT FOUND;

        v_batch := v_batch || jsonb_build_array(jsonb_build_object(
            'key', format('%s:%s', p_table_name, v_record.id),
            'value', v_record.data
        ));

        IF jsonb_array_length(v_batch) >= p_batch_size THEN
            -- 批量写入缓存
            PERFORM pg_notify('cache_warmup', jsonb_build_object(
                'batch', v_batch
            )::TEXT);
            v_batch := '[]'::JSONB;
        END IF;
    END LOOP;

    CLOSE v_cursor;

    -- 发送剩余批次
    IF jsonb_array_length(v_batch) > 0 THEN
        PERFORM pg_notify('cache_warmup', jsonb_build_object(
            'batch', v_batch
        )::TEXT);
    END IF;
END;
$$;
```

### 8.2 缓存穿透防护

```sql
-- ============================================
-- 缓存穿透防护（布隆过滤器）
-- ============================================

-- 1. 布隆过滤器实现
CREATE TABLE bloom_filter (
    filter_name TEXT PRIMARY KEY,
    bit_array BYTEA,
    hash_count INT DEFAULT 3,
    expected_elements BIGINT,
    false_positive_rate DECIMAL(5,4) DEFAULT 0.01
);

CREATE OR REPLACE FUNCTION fn_bloom_add(
    p_filter_name TEXT,
    p_element TEXT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_filter RECORD;
    v_hash1 BIGINT;
    v_hash2 BIGINT;
    v_bit_index INT;
    v_byte_index INT;
    v_bit_mask INT;
    i INT;
BEGIN
    SELECT * INTO v_filter FROM bloom_filter WHERE filter_name = p_filter_name;

    v_hash1 := hashtext(p_element);
    v_hash2 := hashtext(p_element || 'salt');

    FOR i IN 1..v_filter.hash_count LOOP
        v_bit_index := ((v_hash1 + i * v_hash2) % (length(v_filter.bit_array) * 8))::INT;
        v_byte_index := v_bit_index / 8;
        v_bit_mask := 1 << (v_bit_index % 8);

        -- 设置位
        v_filter.bit_array := set_byte(
            v_filter.bit_array,
            v_byte_index,
            get_byte(v_filter.bit_array, v_byte_index) | v_bit_mask
        );
    END LOOP;

    UPDATE bloom_filter SET bit_array = v_filter.bit_array
    WHERE filter_name = p_filter_name;
END;
$$;

CREATE OR REPLACE FUNCTION fn_bloom_might_contain(
    p_filter_name TEXT,
    p_element TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_filter RECORD;
    v_hash1 BIGINT;
    v_hash2 BIGINT;
    v_bit_index INT;
    v_byte_index INT;
    v_bit_mask INT;
    i INT;
BEGIN
    SELECT * INTO v_filter FROM bloom_filter WHERE filter_name = p_filter_name;

    IF NOT FOUND THEN
        RETURN true;  -- 无过滤器时允许通过
    END IF;

    v_hash1 := hashtext(p_element);
    v_hash2 := hashtext(p_element || 'salt');

    FOR i IN 1..v_filter.hash_count LOOP
        v_bit_index := ((v_hash1 + i * v_hash2) % (length(v_filter.bit_array) * 8))::INT;
        v_byte_index := v_bit_index / 8;
        v_bit_mask := 1 << (v_bit_index % 8);

        IF (get_byte(v_filter.bit_array, v_byte_index) & v_bit_mask) = 0 THEN
            RETURN false;  -- 肯定不存在
        END IF;
    END LOOP;

    RETURN true;  -- 可能存在
END;
$$;

-- 2. 缓存查询存储过程（带穿透防护）
CREATE OR REPLACE FUNCTION fn_cache_safe_get(
    p_table_name TEXT,
    p_record_id UUID,
    OUT p_result JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cache_key TEXT;
    v_bloom_filter_name TEXT;
BEGIN
    v_cache_key := format('%s:%s', p_table_name, p_record_id);
    v_bloom_filter_name := format('bf_%s', p_table_name);

    -- 布隆过滤器检查
    IF NOT fn_bloom_might_contain(v_bloom_filter_name, p_record_id::TEXT) THEN
        -- 肯定不存在，直接返回NULL
        p_result := NULL;
        RETURN;
    END IF;

    -- 查询数据库
    EXECUTE format('SELECT to_jsonb(t) FROM %I t WHERE id = $1', p_table_name)
    INTO p_result
    USING p_record_id;

    -- 如果存在，加入布隆过滤器（幂等）
    IF p_result IS NOT NULL THEN
        PERFORM fn_bloom_add(v_bloom_filter_name, p_record_id::TEXT);
    END IF;
END;
$$;
```

---

## 9. 跨数据中心架构

### 9.1 异地多活

```
┌─────────────────────────────────────────────────────────────────────┐
│  跨数据中心多活架构                                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   北美数据中心                    欧洲数据中心                      │
│   ┌─────────────────┐            ┌─────────────────┐               │
│   │  ┌───────────┐  │            │  ┌───────────┐  │               │
│   │  │ Primary   │  │◄──────────►│  │ Primary   │  │               │
│   │  │ (US-West) │  │ 逻辑复制    │  │ (EU-West) │  │               │
│   │  └─────┬─────┘  │            │  └─────┬─────┘  │               │
│   │        │        │            │        │        │               │
│   │  ┌─────┴─────┐  │            │  ┌─────┴─────┐  │               │
│   │  │  Standby  │  │            │  │  Standby  │  │               │
│   │  │  (US-East)│  │            │  │  (EU-East)│  │               │
│   │  └───────────┘  │            │  └───────────┘  │               │
│   └─────────────────┘            └─────────────────┘               │
│           ▲                              ▲                         │
│           │        全局负载均衡器         │                         │
│           └──────────────┬───────────────┘                         │
│                          │                                          │
│                    ┌─────┴─────┐                                    │
│                    │  GSLB/DNS │  ← 地理路由                        │
│                    └─────┬─────┘                                    │
│                          │                                          │
│              ┌───────────┼───────────┐                              │
│              ▼           ▼           ▼                              │
│            美国用户    欧洲用户    亚太用户                           │
│            ───────►   ───────►   ───────►                           │
│            US-West   EU-West     就近路由                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 数据同步策略

```sql
-- ============================================
-- 跨数据中心数据同步
-- ============================================

-- 1. 地理分区发布
CREATE PUBLICATION us_orders_pub
    FOR TABLE orders
    WHERE (region = 'US');

CREATE PUBLICATION eu_orders_pub
    FOR TABLE orders
    WHERE (region = 'EU');

-- 2. 双向复制冲突处理
CREATE TABLE global_sequence (
    region_id TEXT PRIMARY KEY,
    sequence_value BIGINT DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION fn_generate_global_id(p_region_id TEXT)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_seq BIGINT;
    v_region_code BIGINT;
BEGIN
    -- 获取区域编码
    v_region_code := CASE p_region_id
        WHEN 'US' THEN 1
        WHEN 'EU' THEN 2
        WHEN 'AP' THEN 3
        ELSE 9
    END;

    -- 获取序列值
    UPDATE global_sequence
    SET sequence_value = sequence_value + 1,
        last_updated = NOW()
    WHERE region_id = p_region_id
    RETURNING sequence_value INTO v_seq;

    -- 组合：区域编码(4位) + 时间戳(32位) + 序列(28位)
    RETURN (v_region_code << 60) |
           ((EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT << 28) |
           (v_seq & ((1 << 28) - 1));
END;
$$;

-- 3. 地理感知存储过程路由
CREATE OR REPLACE FUNCTION fn_geo_route(
    p_user_location TEXT,  -- IP或地理坐标
    OUT p_target_dc TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_region TEXT;
BEGIN
    -- 简化：根据位置判断区域
    v_region := CASE
        WHEN p_user_location ~ '^192\.' THEN 'US'
        WHEN p_user_location ~ '^10\.' THEN 'EU'
        ELSE 'US'
    END;

    -- 选择最近的可用数据中心
    SELECT dc_code INTO p_target_dc
    FROM datacenter_health
    WHERE region = v_region AND is_healthy = true
    ORDER BY latency_ms
    LIMIT 1;

    IF p_target_dc IS NULL THEN
        p_target_dc := 'US-WEST-1';  -- 默认回退
    END IF;
END;
$$;

-- 4. 跨DC事务协调
CREATE OR REPLACE PROCEDURE sp_cross_dc_order(
    IN p_user_region TEXT,
    IN p_order_data JSONB,
    OUT p_order_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_local_dc TEXT;
    v_target_dc TEXT;
    v_global_id BIGINT;
BEGIN
    -- 生成分布式ID
    v_global_id := fn_generate_global_id(p_user_region);
    p_order_id := v_global_id;

    -- 本地写入
    INSERT INTO orders (id, region, data, status)
    VALUES (v_global_id, p_user_region, p_order_data, 'pending');

    -- 异步复制到其他DC（通过逻辑复制）
    -- 记录同步状态
    INSERT INTO cross_dc_sync_queue (
        record_id, target_regions, payload, status
    ) VALUES (
        v_global_id,
        ARRAY['US', 'EU', 'AP'],
        p_order_data,
        'pending'
    );
END;
$$;
```

---

## 10. 分布式监控与可观测性

```sql
-- ============================================
-- 分布式监控数据聚合
-- ============================================

-- 1. 分布式查询性能表
CREATE TABLE distributed_query_stats (
    stat_id UUID PRIMARY KEY DEFAULT uuidv7(),
    node_id TEXT NOT NULL,
    query_id TEXT,
    query_text TEXT,
    execution_time_ms NUMERIC,
    rows_returned BIGINT,
    shard_scans INT,
    remote_calls INT,
    coordinator_time_ms NUMERIC,
    worker_time_ms NUMERIC,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 跨节点聚合视图
CREATE VIEW v_cluster_performance AS
SELECT
    date_trunc('hour', recorded_at) as hour,
    node_id,
    COUNT(*) as query_count,
    AVG(execution_time_ms) as avg_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) as p95_time,
    SUM(rows_returned) as total_rows,
    AVG(shard_scans) as avg_shards
FROM distributed_query_stats
WHERE recorded_at > NOW() - INTERVAL '24 hours'
GROUP BY 1, 2;

-- 3. 分片健康检查
CREATE OR REPLACE FUNCTION fn_shard_health_check()
RETURNS TABLE (
    shard_id TEXT,
    node_host TEXT,
    row_count BIGINT,
    size_bytes BIGINT,
    last_vacuum TIMESTAMPTZ,
    replication_lag INTERVAL,
    is_healthy BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.shard_id::TEXT,
        s.node_host,
        s.row_count,
        s.size_bytes,
        s.last_vacuum,
        s.replication_lag,
        (s.replication_lag < INTERVAL '5 seconds') as is_healthy
    FROM (
        -- 从Citus元数据获取分片信息
        SELECT
            shardid::TEXT as shard_id,
            nodename as node_host,
            0::BIGINT as row_count,  -- 实际查询填充
            0::BIGINT as size_bytes,
            NULL::TIMESTAMPTZ as last_vacuum,
            INTERVAL '0' as replication_lag
        FROM pg_dist_shard_placement
    ) s;
END;
$$;

-- 4. 慢查询告警
CREATE OR REPLACE PROCEDURE sp_check_slow_distributed_queries()
LANGUAGE plpgsql
AS $$
DECLARE
    v_slow_count INT;
BEGIN
    SELECT COUNT(*) INTO v_slow_count
    FROM distributed_query_stats
    WHERE recorded_at > NOW() - INTERVAL '5 minutes'
      AND execution_time_ms > 1000;

    IF v_slow_count > 10 THEN
        PERFORM pg_notify('alert_distributed', jsonb_build_object(
            'type', 'slow_queries',
            'count', v_slow_count,
            'threshold', 1000
        )::TEXT);
    END IF;
END;
$$;
```

---

## 11. 持续推进计划

### 短期目标 (1-2周)

- [ ] 完成现有架构的分片策略评估
- [ ] 实施Citus分布式表迁移
- [ ] 配置读写分离路由

### 中期目标 (1个月)

- [ ] 部署分布式事务Saga模式
- [ ] 实施缓存一致性方案
- [ ] 建立跨DC复制链路

### 长期目标 (3个月)

- [ ] 完整异地多活架构
- [ ] 自动化分片再平衡
- [ ] 分布式监控大盘

---

**文档信息**:

- 字数: 12000+
- 分布式模式: 20+
- 代码示例: 50+
- 状态: ✅ 深度分析完成

---

*构建可扩展的分布式数据库中心架构！* 🌐
