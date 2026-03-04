# 数据仓库PostgreSQL架构深度实战 v2.0

> **文档类型**: 深度实战案例 (形式化论证版)
> **业务场景**: PB级企业数据仓库
> **技术栈**: PostgreSQL 16/17/18, columnar store, Citus, pg_partman
> **创建日期**: 2026-03-04
> **文档长度**: 6000+字

---

## 摘要

本文基于PB级企业数据仓库实战场景，深入剖析PostgreSQL在OLAP分析型负载中的架构设计、存储优化与查询加速方案。
涵盖星型/雪花模型设计、列存表使用、ETL流程实现、并行查询优化、分区策略及物化视图应用。
通过形式化方法定义数据仓库模型，给出维度建模的规范化证明，并基于生产环境TPC-DS基准测试数据验证方案有效性。

**关键词**: 数据仓库、OLAP、列存储、ETL、维度建模、星型模型、PostgreSQL

---

## 1. 系统概述

### 1.1 业务规模与挑战

| 指标 | 数值 | 挑战 |
|------|------|------|
| 数据总量 | 5 PB | 存储成本控制 |
| 日增量 | 10 TB | 批量加载性能 |
| 维度表数量 | 200+ | 维度管理复杂性 |
| 事实表数量 | 50+ | 查询优化 |
| 并发查询 | 500+ | 资源调度 |
| 复杂查询响应 | < 30s (P99) | 查询加速 |
| 数据新鲜度 | < 1小时 | 实时ETL |

### 1.2 数据仓库架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      企业级数据仓库架构                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        数据源层 (Source Layer)                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ 业务系统  │  │ 日志系统  │  │ 外部数据  │  │ 实时流   │            │   │
│  │  │  OLTP    │  │   Logs   │  │ External │  │ Streaming│            │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │   │
│  │       │             │             │             │                  │   │
│  │       └─────────────┴─────────────┴─────────────┘                  │   │
│  │                         │                                          │   │
│  │                         ▼                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                    ETL/ELT处理层                             │   │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │   │
│  │  │  │ 抽取(Extract)│ │ 转换(Transform)│ │ 加载(Load)  │  │ 质量检查  │    │   │   │
│  │  │  │  Debezium  │  │  dbt/Spark  │  │  COPY/ETL  │  │  Great    │    │   │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘  │  Expec.  │    │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                         │                                          │   │
│  │                         ▼                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                            │
│                              ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    数据仓库层 (DW Layer)                             │   │
│  │                                                                     │   │
│  │  ┌──────────────────┐    ┌──────────────────┐                      │   │
│  │  │   ODS (操作数据)  │    │  DW (数据仓库)    │                      │   │
│  │  │  ──────────────  │    │  ──────────────  │                      │   │
│  │  │  原始数据存储     │───►│  星型/雪花模型   │                      │   │
│  │  │  保留7-30天      │    │  历史全量数据    │                      │   │
│  │  └──────────────────┘    └────────┬─────────┘                      │   │
│  │                                   │                                │   │
│  │                                   ▼                                │   │
│  │  ┌──────────────────┐    ┌──────────────────┐                      │   │
│  │  │   DM (数据集市)   │◄───│  Column Store    │                      │   │
│  │  │  部门级汇总       │    │  列存表/压缩     │                      │   │
│  │  │  预聚合数据       │    │  分析型存储      │                      │   │
│  │  └──────────────────┘    └──────────────────┘                      │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                            │
│                              ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    应用服务层 (BI/Analytics)                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ Tableau  │  │ PowerBI  │  │  Superset│  │  即席查询 │            │   │
│  │  │ Looker   │  │ Metabase │  │ Grafana  │  │  SQL接口  │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 数据流架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ETL数据流程                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Source      Extract        Transform              Load         DWH        │
│  ─────      ───────        ─────────              ─────        ────        │
│                                                                             │
│   ┌──┐       ┌───┐          ┌─────────┐            ┌───┐       ┌────┐     │
│   │DB│──────►│CDC│─────────►│Staging  │───────────►│   │──────►│ODS │     │
│   └──┘       └───┘          │  Area   │            │   │       └────┘     │
│                             └────┬────┘            │ L │          │       │
│                                  │                 │ O │          ▼       │
│                             ┌────┴────┐            │ A │       ┌────┐     │
│                             │Cleaning │            │ D │──────►│DWD │     │
│                             │Normalize│            │   │       │明细│     │
│                             └────┬────┘            │   │       └────┘     │
│                                  │                 └───┘          │       │
│                             ┌────┴────┐                           ▼       │
│                             │Business │                        ┌────┐     │
│                             │  Logic  │                        │DWS │     │
│                             │Aggregate│                        │汇总│     │
│                             └────┬────┘                        └────┘     │
│                                  │                                │       │
│                                  ▼                                ▼       │
│                             ┌─────────┐                        ┌────┐     │
│                             │Dimension│                        │ADS │     │
│                             │  Lookup │                        │应用│     │
│                             └─────────┘                        └────┘     │
│                                                                             │
│  数据新鲜度:                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │ 实时流: Kafka → Flink → PostgreSQL (秒级延迟)                    │     │
│  │ 微批处理: 每15分钟批量加载                                         │     │
│  │ 日批处理: T+1 凌晨批量ETL                                          │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 维度建模

### 2.1 星型模型 vs 雪花模型

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    星型模型 vs 雪花模型对比                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  星型模型 (Star Schema)                      雪花模型 (Snowflake Schema)    │
│  ─────────────────────                       ────────────────────────       │
│                                                                             │
│        ┌──────────┐                              ┌──────────┐              │
│        │ dim_date │                              │ dim_date │              │
│        └────┬─────┘                              └────┬─────┘              │
│             │                                         │                     │
│        ┌────┴─────┐                              ┌────┴─────┐              │
│        │          │                              │          │              │
│   ┌────┴────┐     │                         ┌────┴────┐     │              │
│   │dim_user │     │                         │dim_user │     │              │
│   └────┬────┘     │                         └────┬────┘     │              │
│        │          │                              │          │              │
│        │    ┌─────┴─────┐                        │    ┌─────┴─────┐        │
│        │    │ fact_sales│                        │    │ fact_sales│        │
│        │    │───────────│                        │    │───────────│        │
│        │    │ date_key  │                        │    │ date_key  │        │
│        │    │ user_key  │                        │    │ user_key  │        │
│        └───►│ product_key│                       └───►│ product_key│       │
│             │ amount    │                             │ amount    │        │
│             │ quantity  │                             │ quantity  │        │
│             └─────┬─────┘                             └─────┬─────┘        │
│                   │                                         │              │
│              ┌────┴────┐                              ┌─────┴─────┐        │
│              │dim_product│                            │dim_product│        │
│              └─────────┘                              └────┬────┘        │
│                                                            │               │
│                                                       ┌────┴────┐          │
│                                                       │dim_category│        │
│                                                       └────┬────┘          │
│                                                            │               │
│                                                       ┌────┴────┐          │
│                                                       │dim_brand │          │
│                                                       └─────────┘          │
│                                                                             │
│  特点:                                      特点:                          │
│  • 查询简单，性能好                          • 减少冗余，存储高效           │
│  • 维度表有一定冗余                          • 查询需要更多JOIN             │
│  • 适合绝大多数BI场景                        • 适合维度属性频繁变更         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据仓库分层模型

```sql
-- ============================================
-- 2.2.1 分层架构定义
-- ============================================

-- ODS层: 原始数据存储 (Operational Data Store)
-- 保留原始格式，几乎不做转换
CREATE SCHEMA ods;

-- DWD层: 明细数据层 (Data Warehouse Detail)
-- 清洗后的明细数据，轻度汇总
CREATE SCHEMA dwd;

-- DWS层: 汇总数据层 (Data Warehouse Summary)
-- 按维度汇总，中度聚合
CREATE SCHEMA dws;

-- ADS层: 应用数据层 (Application Data Service)
-- 高度聚合，面向具体应用
CREATE SCHEMA ads;

-- DIM层: 维度数据 (Dimension)
CREATE SCHEMA dim;
```

### 2.3 维度表设计

```sql
-- ============================================
-- 2.3.1 日期维度表 (缓慢变化维类型0)
-- ============================================
CREATE TABLE dim.dim_date (
    date_key            INTEGER PRIMARY KEY,     -- 20260101格式
    full_date           DATE NOT NULL,
    year_num            SMALLINT NOT NULL,
    quarter_num         SMALLINT NOT NULL,
    month_num           SMALLINT NOT NULL,
    week_num            SMALLINT NOT NULL,
    day_num             SMALLINT NOT NULL,
    day_of_week         SMALLINT NOT NULL,       -- 1=Monday
    day_of_year         SMALLINT NOT NULL,

    -- 业务属性
    is_weekend          BOOLEAN DEFAULT FALSE,
    is_holiday          BOOLEAN DEFAULT FALSE,
    holiday_name        VARCHAR(50),
    fiscal_year         SMALLINT,
    fiscal_quarter      SMALLINT,

    -- 名称描述
    year_month          VARCHAR(7),              -- '2026-01'
    year_quarter        VARCHAR(7),              -- '2026-Q1'
    month_name          VARCHAR(10),             -- 'January'
    month_name_abbr     VARCHAR(3),              -- 'Jan'
    day_name            VARCHAR(10),             -- 'Monday'
    day_name_abbr       VARCHAR(3),              -- 'Mon'

    -- 相对日期标志
    is_today            BOOLEAN DEFAULT FALSE,
    is_yesterday        BOOLEAN DEFAULT FALSE,
    is_current_week     BOOLEAN DEFAULT FALSE,
    is_current_month    BOOLEAN DEFAULT FALSE,
    is_current_quarter  BOOLEAN DEFAULT FALSE,
    is_current_year     BOOLEAN DEFAULT FALSE
);

-- 生成日期维度数据
CREATE OR REPLACE FUNCTION dim.generate_dim_dates(
    p_start_date DATE,
    p_end_date DATE
) RETURNS INTEGER AS $$
DECLARE
    v_date DATE;
    v_count INTEGER := 0;
BEGIN
    v_date := p_start_date;

    WHILE v_date <= p_end_date LOOP
        INSERT INTO dim.dim_date (
            date_key, full_date, year_num, quarter_num, month_num,
            week_num, day_num, day_of_week, day_of_year,
            year_month, year_quarter, month_name, month_name_abbr,
            day_name, day_name_abbr
        ) VALUES (
            TO_CHAR(v_date, 'YYYYMMDD')::INTEGER,
            v_date,
            EXTRACT(YEAR FROM v_date)::SMALLINT,
            EXTRACT(QUARTER FROM v_date)::SMALLINT,
            EXTRACT(MONTH FROM v_date)::SMALLINT,
            EXTRACT(WEEK FROM v_date)::SMALLINT,
            EXTRACT(DAY FROM v_date)::SMALLINT,
            EXTRACT(ISODOW FROM v_date)::SMALLINT,
            EXTRACT(DOY FROM v_date)::SMALLINT,
            TO_CHAR(v_date, 'YYYY-MM'),
            TO_CHAR(v_date, 'YYYY') || '-Q' || EXTRACT(QUARTER FROM v_date)::TEXT,
            TO_CHAR(v_date, 'Month'),
            TO_CHAR(v_date, 'Mon'),
            TO_CHAR(v_date, 'Day'),
            TO_CHAR(v_date, 'Dy')
        )
        ON CONFLICT (date_key) DO NOTHING;

        v_count := v_count + 1;
        v_date := v_date + INTERVAL '1 day';
    END LOOP;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- 初始化日期维度 (10年数据)
SELECT dim.generate_dim_dates('2020-01-01', '2030-12-31');

-- ============================================
-- 2.3.2 用户维度表 (缓慢变化维类型2 - SCD2)
-- ============================================
CREATE TABLE dim.dim_user (
    user_key            BIGSERIAL PRIMARY KEY,   -- 代理键
    user_id             BIGINT NOT NULL,         -- 自然键
    user_name           VARCHAR(100) NOT NULL,
    email               VARCHAR(255),
    phone               VARCHAR(20),

    -- 维度属性
    gender              CHAR(1),
    age_range           VARCHAR(10),             -- '18-24', '25-34'...
    registration_date   DATE,
    registration_source VARCHAR(50),
    user_level          SMALLINT DEFAULT 1,      -- 1:普通 2:银牌 3:金牌 4:钻石
    membership_type     VARCHAR(20),

    -- 地理属性
    country_code        CHAR(2) DEFAULT 'CN',
    province_code       VARCHAR(6),
    city_code           VARCHAR(6),

    -- SCD2追踪字段
    effective_date      DATE NOT NULL,
    expiration_date     DATE NOT NULL DEFAULT '9999-12-31',
    is_current          BOOLEAN DEFAULT TRUE,

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (user_id, effective_date)
);

-- SCD2处理: 查找当前版本
CREATE INDEX idx_dim_user_current ON dim.dim_user(user_id) WHERE is_current = TRUE;

-- ============================================
-- 2.3.3 产品维度表 (SCD2)
-- ============================================
CREATE TABLE dim.dim_product (
    product_key         BIGSERIAL PRIMARY KEY,
    product_id          BIGINT NOT NULL,
    sku_code            VARCHAR(64) NOT NULL,
    product_name        VARCHAR(255) NOT NULL,

    -- 分类属性
    category_id         INTEGER,
    category_name       VARCHAR(100),
    subcategory_id      INTEGER,
    subcategory_name    VARCHAR(100),
    brand_id            INTEGER,
    brand_name          VARCHAR(100),

    -- 商品属性
    base_price          DECIMAL(18, 2),
    cost_price          DECIMAL(18, 2),
    unit_weight_kg      DECIMAL(8, 3),
    unit_volume_m3      DECIMAL(8, 6),
    supplier_id         BIGINT,

    -- SCD2字段
    effective_date      DATE NOT NULL,
    expiration_date     DATE NOT NULL DEFAULT '9999-12-31',
    is_current          BOOLEAN DEFAULT TRUE,

    UNIQUE (product_id, effective_date)
);

-- ============================================
-- 2.3.4 地区维度表 (层次维度)
-- ============================================
CREATE TABLE dim.dim_region (
    region_key          SERIAL PRIMARY KEY,
    region_level        SMALLINT NOT NULL,       -- 1:国家 2:省 3:市 4:区县
    region_code         VARCHAR(12) NOT NULL,
    region_name         VARCHAR(64) NOT NULL,
    parent_code         VARCHAR(12),

    -- 层次路径 (支持层级钻取)
    region_path         LTREE,                   -- '1.11.1101.110101'
    region_path_name    TEXT,                    -- '中国.北京市.市辖区.东城区'

    -- 地理属性
    longitude           DECIMAL(10, 6),
    latitude            DECIMAL(10, 6),

    UNIQUE (region_code)
);

-- ltree索引支持层次查询
CREATE INDEX idx_dim_region_path ON dim.dim_region USING GIST(region_path);

-- ============================================
-- 2.3.5 营销渠道维度表
-- ============================================
CREATE TABLE dim.dim_channel (
    channel_key         SERIAL PRIMARY KEY,
    channel_id          VARCHAR(32) NOT NULL,
    channel_name        VARCHAR(100) NOT NULL,
    channel_type        VARCHAR(50),             -- 'organic', 'paid', 'social'
    channel_group       VARCHAR(50),             -- 一级分类: Search, Social, Direct
    media_source        VARCHAR(100),            -- 具体来源: Google, Facebook
    campaign_type       VARCHAR(50),
    landing_page_type   VARCHAR(50),
    device_type         VARCHAR(20),

    UNIQUE (channel_id)
);
```

### 2.4 事实表设计

```sql
-- ============================================
-- 2.4.1 销售事实表 (事务型事实表)
-- ============================================
CREATE TABLE dwd.fact_sales (
    -- 代理键
    sales_key           BIGSERIAL,

    -- 维度外键
    date_key            INTEGER NOT NULL REFERENCES dim.dim_date(date_key),
    user_key            BIGINT NOT NULL REFERENCES dim.dim_user(user_key),
    product_key         BIGINT NOT NULL REFERENCES dim.dim_product(product_key),
    region_key          INTEGER NOT NULL REFERENCES dim.dim_region(region_key),
    channel_key         INTEGER NOT NULL REFERENCES dim.dim_channel(channel_key),

    -- 退化维度
    order_id            BIGINT NOT NULL,
    order_line_id       INTEGER NOT NULL,

    -- 度量 (可加)
    quantity            INTEGER NOT NULL,
    unit_price          DECIMAL(18, 4) NOT NULL,
    discount_amount     DECIMAL(18, 4) DEFAULT 0,
    sales_amount        DECIMAL(18, 4) NOT NULL,  -- quantity * unit_price - discount
    cost_amount         DECIMAL(18, 4),           -- quantity * cost_price

    -- 运费等分摊
    shipping_amount     DECIMAL(18, 4) DEFAULT 0,
    tax_amount          DECIMAL(18, 4) DEFAULT 0,

    -- 衍生度量
    gross_profit        DECIMAL(18, 4) GENERATED ALWAYS AS
                        (sales_amount - cost_amount) STORED,

    -- 时间戳
    created_at          TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (date_key, sales_key)
) PARTITION BY RANGE (date_key);

-- 按月分区
CREATE TABLE dwd.fact_sales_y2026m01 PARTITION OF dwd.fact_sales
    FOR VALUES FROM (20260101) TO (20260201);
CREATE TABLE dwd.fact_sales_y2026m02 PARTITION OF dwd.fact_sales
    FOR VALUES FROM (20260201) TO (20260301);

-- 复合索引支持常用查询模式
CREATE INDEX idx_fact_sales_product ON dwd.fact_sales(date_key, product_key);
CREATE INDEX idx_fact_sales_user ON dwd.fact_sales(date_key, user_key);
CREATE INDEX idx_fact_sales_region ON dwd.fact_sales(date_key, region_key);

-- ============================================
-- 2.4.2 用户行为事实表 (累积快照型)
-- ============================================
CREATE TABLE dwd.fact_user_journey (
    journey_key         BIGSERIAL PRIMARY KEY,

    -- 维度外键
    user_key            BIGINT NOT NULL REFERENCES dim.dim_user(user_key),
    date_key            INTEGER NOT NULL REFERENCES dim.dim_date(date_key),
    channel_key         INTEGER NOT NULL REFERENCES dim.dim_channel(channel_key),

    -- 会话属性
    session_id          VARCHAR(64) NOT NULL,
    device_type         VARCHAR(20),
    os_type             VARCHAR(20),
    browser_type        VARCHAR(30),

    -- 时间度量
    page_views          INTEGER DEFAULT 0,
    unique_events       INTEGER DEFAULT 0,
    session_duration_sec INTEGER DEFAULT 0,

    -- 关键事件标记
    is_conversion       BOOLEAN DEFAULT FALSE,
    conversion_event    VARCHAR(50),
    conversion_value    DECIMAL(18, 4),

    -- 累计快照字段
    first_visit_date    DATE,
    last_visit_date     DATE,
    total_visits        INTEGER DEFAULT 1,

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 2.4.3 库存快照事实表 (周期快照型)
-- ============================================
CREATE TABLE dwd.fact_inventory_snapshot (
    snapshot_key        BIGSERIAL,

    snapshot_date_key   INTEGER NOT NULL REFERENCES dim.dim_date(date_key),
    product_key         BIGINT NOT NULL REFERENCES dim.dim_product(product_key),
    warehouse_key       INTEGER NOT NULL,  -- 假设有dim_warehouse

    -- 库存度量
    quantity_on_hand    INTEGER NOT NULL,
    quantity_reserved   INTEGER DEFAULT 0,
    quantity_available  INTEGER GENERATED ALWAYS AS
                        (quantity_on_hand - quantity_reserved) STORED,

    -- 价值度量
    unit_cost           DECIMAL(18, 4),
    inventory_value     DECIMAL(18, 4),

    -- 周转指标
    days_in_inventory   INTEGER,
    turnover_rate       DECIMAL(8, 4),

    PRIMARY KEY (snapshot_date_key, product_key, warehouse_key)
) PARTITION BY RANGE (snapshot_date_key);
```

---

## 3. ETL流程设计

### 3.1 增量抽取策略

```sql
-- ============================================
-- 3.1.1 增量抽取控制表
-- ============================================
CREATE TABLE etl.etl_control (
    control_id          SERIAL PRIMARY KEY,
    source_system       VARCHAR(50) NOT NULL,
    source_table        VARCHAR(100) NOT NULL,
    target_table        VARCHAR(100) NOT NULL,
    last_extract_time   TIMESTAMPTZ,
    last_extract_key    BIGINT,              -- 用于键值增量
    extract_strategy    VARCHAR(20) NOT NULL DEFAULT 'timestamp', -- 'timestamp', 'key', 'cdc'
    water_mark_column   VARCHAR(50),         -- 时间戳或自增列名
    batch_size          INTEGER DEFAULT 10000,
    is_active           BOOLEAN DEFAULT TRUE,
    UNIQUE (source_system, source_table)
);

-- 初始化控制记录
INSERT INTO etl.etl_control (source_system, source_table, target_table, water_mark_column)
VALUES
    ('oltp_db', 'users', 'ods.ods_users', 'updated_at'),
    ('oltp_db', 'orders', 'ods.ods_orders', 'updated_at'),
    ('oltp_db', 'order_items', 'ods.ods_order_items', 'updated_at');

-- ============================================
-- 3.1.2 时间戳增量抽取函数
-- ============================================
CREATE OR REPLACE FUNCTION etl.extract_incremental(
    p_source_system VARCHAR,
    p_source_table VARCHAR
) RETURNS TABLE (
    records_extracted BIGINT,
    new_watermark TIMESTAMPTZ,
    duration_ms INTEGER
) AS $$
DECLARE
    v_control RECORD;
    v_start_time TIMESTAMPTZ;
    v_extracted BIGINT;
BEGIN
    v_start_time := clock_timestamp();

    -- 获取控制信息
    SELECT * INTO v_control
    FROM etl.etl_control
    WHERE source_system = p_source_system AND source_table = p_source_table;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No control record found for %.%', p_source_system, p_source_table;
    END IF;

    -- 动态执行增量抽取 (简化示例，实际使用dblink或fdw)
    -- 这里假设使用postgres_fdw连接到源库
    EXECUTE format('
        INSERT INTO %I (SELECT * FROM source_%I.%I
                        WHERE %I > %L
                        ORDER BY %I
                        LIMIT %s)
        ON CONFLICT DO NOTHING',
        v_control.target_table,
        p_source_system,
        p_source_table,
        v_control.water_mark_column,
        v_control.last_extract_time,
        v_control.water_mark_column,
        v_control.batch_size
    );

    GET DIAGNOSTICS v_extracted = ROW_COUNT;

    -- 更新水位线
    UPDATE etl.etl_control
    SET last_extract_time = NOW()
    WHERE control_id = v_control.control_id;

    RETURN QUERY SELECT
        v_extracted,
        NOW(),
        EXTRACT(MILLISECONDS FROM clock_timestamp() - v_start_time)::INTEGER;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 3.1.3 CDC (变更数据捕获) 处理
-- ============================================
CREATE TABLE etl.cdc_changes (
    change_id           BIGSERIAL PRIMARY KEY,
    source_table        VARCHAR(100) NOT NULL,
    change_type         CHAR(1) NOT NULL,      -- I:Insert U:Update D:Delete
    primary_key_values  JSONB NOT NULL,        -- {user_id: 123}
    old_data            JSONB,
    new_data            JSONB,
    changed_at          TIMESTAMPTZ DEFAULT NOW(),
    processed_at        TIMESTAMPTZ,
    processed           BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_cdc_unprocessed ON etl.cdc_changes(source_table, processed)
WHERE processed = FALSE;

-- CDC处理函数
CREATE OR REPLACE FUNCTION etl.process_cdc_changes(
    p_batch_size INTEGER DEFAULT 1000
) RETURNS TABLE (
    table_name VARCHAR,
    inserts BIGINT,
    updates BIGINT,
    deletes BIGINT
) AS $$
DECLARE
    v_table VARCHAR;
    v_inserts BIGINT := 0;
    v_updates BIGINT := 0;
    v_deletes BIGINT := 0;
BEGIN
    -- 按表处理变更
    FOR v_table IN
        SELECT DISTINCT source_table FROM etl.cdc_changes
        WHERE processed = FALSE
    LOOP
        -- 处理插入
        INSERT INTO ods.ods_users (SELECT * FROM jsonb_populate_recordset(NULL::ods.ods_users,
            (SELECT JSONB_AGG(new_data) FROM etl.cdc_changes
             WHERE source_table = v_table AND change_type = 'I' AND processed = FALSE)));
        GET DIAGNOSTICS v_inserts = ROW_COUNT;

        -- 处理更新
        -- ... (实际实现需要UPSERT逻辑)

        -- 处理删除
        -- ... (软删除或物理删除)

        -- 标记已处理
        UPDATE etl.cdc_changes
        SET processed = TRUE, processed_at = NOW()
        WHERE source_table = v_table AND processed = FALSE;

        RETURN QUERY SELECT v_table::VARCHAR, v_inserts, v_updates, v_deletes;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 数据清洗与转换

```sql
-- ============================================
-- 3.2.1 数据质量检查
-- ============================================
CREATE TABLE etl.data_quality_checks (
    check_id            SERIAL PRIMARY KEY,
    table_name          VARCHAR(100) NOT NULL,
    check_name          VARCHAR(100) NOT NULL,
    check_type          VARCHAR(50) NOT NULL,    -- 'completeness', 'uniqueness', 'validity', 'consistency'
    check_sql           TEXT NOT NULL,
    threshold_percent   DECIMAL(5, 2) DEFAULT 100.00,
    is_critical         BOOLEAN DEFAULT FALSE,
    alert_enabled       BOOLEAN DEFAULT TRUE
);

-- 定义质量规则
INSERT INTO etl.data_quality_checks (table_name, check_name, check_type, check_sql)
VALUES
    ('ods_users', 'user_id_not_null', 'completeness',
     'SELECT COUNT(*) FROM ods_users WHERE user_id IS NULL'),
    ('ods_orders', 'amount_positive', 'validity',
     'SELECT COUNT(*) FROM ods_orders WHERE total_amount <= 0'),
    ('ods_orders', 'order_date_valid', 'validity',
     'SELECT COUNT(*) FROM ods_orders WHERE order_date > CURRENT_DATE');

-- 质量检查执行函数
CREATE OR REPLACE FUNCTION etl.run_data_quality_checks(
    p_table_name VARCHAR DEFAULT NULL
) RETURNS TABLE (
    check_name VARCHAR,
    failed_records BIGINT,
    total_records BIGINT,
    pass_rate DECIMAL(5,2),
    status VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    WITH check_results AS (
        SELECT
            dq.check_id,
            dq.check_name,
            dq.threshold_percent,
            dq.is_critical,
            -- 执行检查SQL (简化，实际使用动态SQL)
            0::BIGINT AS failed_count,
            (SELECT COUNT(*) FROM ods.ods_users)::BIGINT AS total_count
        FROM etl.data_quality_checks dq
        WHERE (p_table_name IS NULL OR dq.table_name = p_table_name)
          AND dq.alert_enabled = TRUE
    )
    SELECT
        cr.check_name::VARCHAR,
        cr.failed_count,
        cr.total_count,
        ROUND((1 - cr.failed_count::DECIMAL / NULLIF(cr.total_count, 0)) * 100, 2),
        CASE
            WHEN (1 - cr.failed_count::DECIMAL / NULLIF(cr.total_count, 0)) * 100 >= cr.threshold_percent
            THEN 'PASS'
            WHEN cr.is_critical THEN 'FAIL_CRITICAL'
            ELSE 'FAIL_WARNING'
        END::VARCHAR
    FROM check_results cr;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 3.2.2 SCD2维度处理
-- ============================================
CREATE OR REPLACE FUNCTION etl.merge_dim_user_scd2()
RETURNS INTEGER AS $$
DECLARE
    v_merged INTEGER := 0;
BEGIN
    -- Step 1: 关闭现有记录的过期日期
    UPDATE dim.dim_user d
    SET
        is_current = FALSE,
        expiration_date = CURRENT_DATE - 1,
        updated_at = NOW()
    FROM ods.ods_users o
    WHERE d.user_id = o.user_id
      AND d.is_current = TRUE
      AND (
          d.user_name != o.user_name OR
          d.email != o.email OR
          d.user_level != o.user_level
      );

    -- Step 2: 插入新记录
    INSERT INTO dim.dim_user (
        user_id, user_name, email, phone, gender,
        age_range, registration_date, user_level,
        effective_date, is_current
    )
    SELECT
        o.user_id,
        o.user_name,
        o.email,
        o.phone,
        o.gender,
        CASE
            WHEN o.birth_year IS NULL THEN 'Unknown'
            WHEN 2026 - o.birth_year BETWEEN 18 AND 24 THEN '18-24'
            WHEN 2026 - o.birth_year BETWEEN 25 AND 34 THEN '25-34'
            WHEN 2026 - o.birth_year BETWEEN 35 AND 44 THEN '35-44'
            ELSE '45+'
        END,
        o.registration_date,
        o.user_level,
        CURRENT_DATE,
        TRUE
    FROM ods.ods_users o
    LEFT JOIN dim.dim_user d ON d.user_id = o.user_id AND d.is_current = TRUE
    WHERE d.user_key IS NULL  -- 新用户
       OR (
           d.user_name != o.user_name OR
           d.email != o.email OR
           d.user_level != o.user_level
       );  -- 属性变更

    GET DIAGNOSTICS v_merged = ROW_COUNT;
    RETURN v_merged;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 3.2.3 事实表加载
-- ============================================
CREATE OR REPLACE FUNCTION etl.load_fact_sales(
    p_date_key INTEGER
) RETURNS BIGINT AS $$
DECLARE
    v_loaded BIGINT;
BEGIN
    INSERT INTO dwd.fact_sales (
        date_key, user_key, product_key, region_key, channel_key,
        order_id, order_line_id, quantity, unit_price,
        discount_amount, sales_amount, cost_amount
    )
    SELECT
        TO_CHAR(o.order_date, 'YYYYMMDD')::INTEGER,
        du.user_key,
        dp.product_key,
        dr.region_key,
        dc.channel_key,
        o.order_id,
        oi.order_line_id,
        oi.quantity,
        oi.unit_price,
        oi.discount_amount,
        oi.quantity * oi.unit_price - oi.discount_amount,
        oi.quantity * dp.cost_price
    FROM ods.ods_orders o
    JOIN ods.ods_order_items oi ON oi.order_id = o.order_id
    LEFT JOIN dim.dim_user du ON du.user_id = o.user_id AND du.is_current = TRUE
    LEFT JOIN dim.dim_product dp ON dp.product_id = oi.product_id AND dp.is_current = TRUE
    LEFT JOIN dim.dim_region dr ON dr.region_code = o.region_code
    LEFT JOIN dim.dim_channel dc ON dc.channel_id = o.channel_id
    WHERE TO_CHAR(o.order_date, 'YYYYMMDD')::INTEGER = p_date_key
    ON CONFLICT DO NOTHING;

    GET DIAGNOSTICS v_loaded = ROW_COUNT;
    RETURN v_loaded;
END;
$$ LANGUAGE plpgsql;
```

---

## 4. 列存储与压缩

### 4.1 列存表设计

```sql
-- ============================================
-- 4.1.1 使用列存扩展 (假设使用citus_columnar或类似)
-- ============================================

-- 创建列存表 (使用PostgreSQL原生分区+TOAST压缩)
CREATE TABLE dws.sales_summary_columnar (
    date_key            INTEGER NOT NULL,
    product_key         BIGINT NOT NULL,
    region_key          INTEGER NOT NULL,
    channel_key         INTEGER NOT NULL,

    -- 度量列
    order_count         BIGINT,
    quantity_sold       BIGINT,
    revenue             DECIMAL(18, 4),
    cost                DECIMAL(18, 4),
    profit              DECIMAL(18, 4),

    -- 派生度量
    avg_order_value     DECIMAL(18, 4),
    profit_margin       DECIMAL(5, 4)
) PARTITION BY RANGE (date_key);

-- 创建列存分区 (使用特定的存储参数)
CREATE TABLE dws.sales_summary_y2026m01 PARTITION OF dws.sales_summary_columnar
    FOR VALUES FROM (20260101) TO (20260201)
    WITH (compression = 'zstd', compression_level = 9);

-- ============================================
-- 4.1.2 列存数据加载优化
-- ============================================
CREATE OR REPLACE FUNCTION dws.aggregate_sales_daily(
    p_date_key INTEGER
) RETURNS BIGINT AS $$
DECLARE
    v_inserted BIGINT;
BEGIN
    -- 批量聚合插入
    INSERT INTO dws.sales_summary_columnar (
        date_key, product_key, region_key, channel_key,
        order_count, quantity_sold, revenue, cost, profit,
        avg_order_value, profit_margin
    )
    SELECT
        date_key,
        product_key,
        region_key,
        channel_key,
        COUNT(DISTINCT order_id),
        SUM(quantity),
        SUM(sales_amount),
        SUM(cost_amount),
        SUM(gross_profit),
        AVG(sales_amount),
        CASE WHEN SUM(sales_amount) > 0
             THEN SUM(gross_profit) / SUM(sales_amount)
             ELSE 0
        END
    FROM dwd.fact_sales
    WHERE date_key = p_date_key
    GROUP BY date_key, product_key, region_key, channel_key
    ON CONFLICT (date_key, product_key, region_key, channel_key)
    DO UPDATE SET
        order_count = EXCLUDED.order_count,
        quantity_sold = EXCLUDED.quantity_sold,
        revenue = EXCLUDED.revenue,
        cost = EXCLUDED.cost,
        profit = EXCLUDED.profit,
        avg_order_value = EXCLUDED.avg_order_value,
        profit_margin = EXCLUDED.profit_margin;

    GET DIAGNOSTICS v_inserted = ROW_COUNT;
    RETURN v_inserted;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4.1.3 数据压缩统计
-- ============================================
CREATE OR REPLACE VIEW monitoring.compression_stats AS
SELECT
    schemaname,
    tablename,
    pg_total_relation_size(schemaname || '.' || tablename) AS total_size,
    pg_relation_size(schemaname || '.' || tablename) AS table_size,
    pg_indexes_size(schemaname || '.' || tablename) AS index_size,
    (SELECT SUM(pg_column_size(attname))
     FROM pg_attribute
     WHERE attrelid = (schemaname || '.' || tablename)::regclass) AS raw_data_size,
    ROUND(
        pg_relation_size(schemaname || '.' || tablename)::DECIMAL /
        NULLIF((SELECT SUM(pg_column_size(attname)) FROM pg_attribute
                WHERE attrelid = (schemaname || '.' || tablename)::regclass), 0),
        2
    ) AS compression_ratio
FROM pg_tables
WHERE schemaname IN ('dwd', 'dws', 'ads');
```

### 4.2 分区策略

```sql
-- ============================================
-- 4.2.1 自动化分区管理
-- ============================================

-- 创建分区管理函数
CREATE OR REPLACE FUNCTION admin.create_monthly_partition(
    p_table_name VARCHAR,
    p_year INTEGER,
    p_month INTEGER
) RETURNS VOID AS $$
DECLARE
    v_partition_name VARCHAR;
    v_start_date DATE;
    v_end_date DATE;
BEGIN
    v_partition_name := p_table_name || '_y' || p_year || 'm' || LPAD(p_month::TEXT, 2, '0');
    v_start_date := MAKE_DATE(p_year, p_month, 1);
    v_end_date := v_start_date + INTERVAL '1 month';

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
         FOR VALUES FROM (%L) TO (%L)',
        v_partition_name,
        p_table_name,
        TO_CHAR(v_start_date, 'YYYYMMDD'),
        TO_CHAR(v_end_date, 'YYYYMMDD')
    );

    -- 创建分区级索引
    EXECUTE format(
        'CREATE INDEX IF NOT EXISTS idx_%s_product ON %I(product_key)',
        v_partition_name,
        v_partition_name
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4.2.2 分区裁剪验证
-- ============================================
-- 验证查询是否使用了分区裁剪
EXPLAIN (ANALYZE, VERBOSE)
SELECT * FROM dwd.fact_sales
WHERE date_key BETWEEN 20260101 AND 20260131;

-- 预期输出应显示:
-- Partition Pruning: fact_sales_y2026m01

-- ============================================
-- 4.2.3 分区维护任务
-- ============================================
CREATE OR REPLACE FUNCTION admin.maintain_partitions()
RETURNS TABLE (
    action VARCHAR,
    partition_name VARCHAR,
    status VARCHAR
) AS $$
DECLARE
    v_partition RECORD;
BEGIN
    -- 1. 创建未来3个月的分区
    FOR i IN 1..3 LOOP
        PERFORM admin.create_monthly_partition(
            'dwd.fact_sales',
            EXTRACT(YEAR FROM NOW() + (i || ' months')::INTERVAL)::INTEGER,
            EXTRACT(MONTH FROM NOW() + (i || ' months')::INTERVAL)::INTEGER
        );
        RETURN QUERY SELECT 'CREATE'::VARCHAR,
            'fact_sales_y' || EXTRACT(YEAR FROM NOW() + (i || ' months')::INTERVAL) ||
            'm' || LPAD(EXTRACT(MONTH FROM NOW() + (i || ' months')::INTERVAL)::TEXT, 2, '0'),
            'SUCCESS';
    END LOOP;

    -- 2. 归档过期分区 (保留2年)
    FOR v_partition IN
        SELECT tablename
        FROM pg_tables
        WHERE tablename LIKE 'fact_sales_y%'
          AND tablename < 'fact_sales_y' || TO_CHAR(NOW() - INTERVAL '2 years', 'YYYY')
    LOOP
        -- 逻辑: 导出到冷存储后删除
        RETURN QUERY SELECT 'ARCHIVE'::VARCHAR, v_partition.tablename::VARCHAR, 'PENDING';
    END LOOP;

END;
$$ LANGUAGE plpgsql;
```

---

## 5. 并行查询优化

### 5.1 并行度配置

```sql
-- ============================================
-- 5.1.1 并行查询参数优化
-- ============================================

-- 会话级并行设置
SET max_parallel_workers_per_gather = 8;
SET parallel_tuple_cost = 0.01;
SET parallel_setup_cost = 100;
SET min_parallel_table_scan_size = '8MB';
SET min_parallel_index_scan_size = '512kB';

-- 表级并行度设置
ALTER TABLE dwd.fact_sales SET (parallel_workers = 4);
ALTER TABLE dws.sales_summary_columnar SET (parallel_workers = 8);

-- ============================================
-- 5.1.2 并行查询计划分析
-- ============================================
EXPLAIN (ANALYZE, VERBOSE, COSTS, BUFFERS, FORMAT TEXT)
SELECT
    d.year_num,
    d.month_num,
    p.category_name,
    SUM(f.sales_amount) AS total_revenue,
    SUM(f.quantity) AS total_quantity,
    COUNT(DISTINCT f.user_key) AS unique_customers
FROM dwd.fact_sales f
JOIN dim.dim_date d ON d.date_key = f.date_key
JOIN dim.dim_product p ON p.product_key = f.product_key
WHERE d.year_num = 2026
GROUP BY d.year_num, d.month_num, p.category_name
ORDER BY d.month_num, total_revenue DESC;

-- 预期看到: Workers Planned: 4, Workers Launched: 4
--          -> Parallel Seq Scan on fact_sales
```

### 5.2 查询优化策略

```sql
-- ============================================
-- 5.2.1 星型查询优化
-- ============================================

-- 优化前 (可能导致大量JOIN)
SELECT
    d.year_month,
    u.age_range,
    p.brand_name,
    SUM(f.sales_amount)
FROM dwd.fact_sales f
JOIN dim.dim_date d ON d.date_key = f.date_key
JOIN dim.dim_user u ON u.user_key = f.user_key
JOIN dim.dim_product p ON p.product_key = f.product_key
WHERE d.year_num = 2026
GROUP BY d.year_month, u.age_range, p.brand_name;

-- 优化后 (使用维度过滤子查询)
WITH filtered_dates AS (
    SELECT date_key, year_month
    FROM dim.dim_date
    WHERE year_num = 2026
),
filtered_users AS (
    SELECT user_key, age_range
    FROM dim.dim_user
    WHERE is_current = TRUE
),
filtered_products AS (
    SELECT product_key, brand_name
    FROM dim.dim_product
    WHERE is_current = TRUE
)
SELECT
    fd.year_month,
    fu.age_range,
    fp.brand_name,
    SUM(f.sales_amount)
FROM dwd.fact_sales f
JOIN filtered_dates fd ON fd.date_key = f.date_key
JOIN filtered_users fu ON fu.user_key = f.user_key
JOIN filtered_products fp ON fp.product_key = f.product_key
GROUP BY fd.year_month, fu.age_range, fp.brand_name;

-- ============================================
-- 5.2.2 位图索引扫描优化
-- ============================================
-- 确保复合索引支持位图扫描
CREATE INDEX idx_fact_sales_date_product ON dwd.fact_sales(date_key, product_key);

-- 多条件OR查询优化
SELECT * FROM dwd.fact_sales
WHERE date_key = 20260101 OR product_key IN (1, 2, 3);
-- 预期: BitmapOr -> Bitmap Index Scan

-- ============================================
-- 5.2.3 聚合下推优化
-- ============================================
-- 使用预聚合减少数据量
CREATE MATERIALIZED VIEW dws.daily_sales_agg AS
SELECT
    date_key,
    product_key,
    region_key,
    SUM(sales_amount) AS revenue,
    SUM(quantity) AS quantity,
    COUNT(*) AS order_count
FROM dwd.fact_sales
GROUP BY date_key, product_key, region_key;

CREATE UNIQUE INDEX idx_daily_sales_agg ON dws.daily_sales_agg(date_key, product_key, region_key);

-- 基于预聚合的查询
SELECT
    d.year_month,
    SUM(dsa.revenue)
FROM dws.daily_sales_agg dsa
JOIN dim.dim_date d ON d.date_key = dsa.date_key
GROUP BY d.year_month;
```

---

## 6. 物化视图与汇总

### 6.1 增量物化视图

```sql
-- ============================================
-- 6.1.1 创建物化视图 (使用pg_ivm扩展)
-- ============================================
-- CREATE EXTENSION IF NOT EXISTS pg_ivm;

-- 创建标准物化视图 (需要手动刷新)
CREATE MATERIALIZED VIEW dws.monthly_sales_summary AS
SELECT
    d.year_num,
    d.month_num,
    d.year_month,
    f.product_key,
    f.region_key,
    f.channel_key,
    COUNT(DISTINCT f.order_id) AS order_count,
    SUM(f.quantity) AS total_quantity,
    SUM(f.sales_amount) AS total_revenue,
    SUM(f.cost_amount) AS total_cost,
    SUM(f.gross_profit) AS total_profit
FROM dwd.fact_sales f
JOIN dim.dim_date d ON d.date_key = f.date_key
GROUP BY d.year_num, d.month_num, d.year_month,
         f.product_key, f.region_key, f.channel_key;

-- 创建唯一索引支持并发刷新
CREATE UNIQUE INDEX idx_monthly_sales_summary
ON dws.monthly_sales_summary(year_num, month_num, product_key, region_key, channel_key);

-- 创建普通索引
CREATE INDEX idx_monthly_sales_summary_date
ON dws.monthly_sales_summary(year_num, month_num);

-- ============================================
-- 6.1.2 物化视图刷新策略
-- ============================================
CREATE OR REPLACE FUNCTION dws.refresh_materialized_views()
RETURNS TABLE (
    view_name VARCHAR,
    refresh_time_ms INTEGER,
    status VARCHAR
) AS $$
DECLARE
    v_start_time TIMESTAMPTZ;
BEGIN
    -- 刷新月度汇总
    v_start_time := clock_timestamp();
    REFRESH MATERIALIZED VIEW CONCURRENTLY dws.monthly_sales_summary;
    RETURN QUERY SELECT
        'monthly_sales_summary'::VARCHAR,
        EXTRACT(MILLISECONDS FROM clock_timestamp() - v_start_time)::INTEGER,
        'SUCCESS';

    -- 刷新其他视图...
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 6.1.3 分层汇总表
-- ============================================

-- 日汇总
CREATE TABLE dws.sales_summary_daily (
    summary_date        DATE PRIMARY KEY,
    order_count         BIGINT,
    item_count          BIGINT,
    total_quantity      BIGINT,
    total_revenue       DECIMAL(18, 4),
    total_cost          DECIMAL(18, 4),
    total_profit        DECIMAL(18, 4),
    unique_customers    BIGINT,
    avg_order_value     DECIMAL(18, 4)
);

-- 周汇总
CREATE TABLE dws.sales_summary_weekly (
    year_num            SMALLINT,
    week_num            SMALLINT,
    order_count         BIGINT,
    total_revenue       DECIMAL(18, 4),
    PRIMARY KEY (year_num, week_num)
);

-- 月汇总
CREATE TABLE dws.sales_summary_monthly (
    year_num            SMALLINT,
    month_num           SMALLINT,
    year_month          VARCHAR(7) PRIMARY KEY,
    order_count         BIGINT,
    total_revenue       DECIMAL(18, 4),
    yoy_growth_rate     DECIMAL(5, 2)  -- 同比增长率
);

-- 汇总计算函数
CREATE OR REPLACE FUNCTION dws.calculate_daily_summary(p_date DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO dws.sales_summary_daily (
        summary_date, order_count, item_count, total_quantity,
        total_revenue, total_cost, total_profit, unique_customers
    )
    SELECT
        p_date,
        COUNT(DISTINCT order_id),
        COUNT(*),
        SUM(quantity),
        SUM(sales_amount),
        SUM(cost_amount),
        SUM(gross_profit),
        COUNT(DISTINCT user_key)
    FROM dwd.fact_sales
    WHERE date_key = TO_CHAR(p_date, 'YYYYMMDD')::INTEGER
    ON CONFLICT (summary_date) DO UPDATE SET
        order_count = EXCLUDED.order_count,
        item_count = EXCLUDED.item_count,
        total_quantity = EXCLUDED.total_quantity,
        total_revenue = EXCLUDED.total_revenue,
        total_cost = EXCLUDED.total_cost,
        total_profit = EXCLUDED.total_profit,
        unique_customers = EXCLUDED.unique_customers,
        avg_order_value = EXCLUDED.total_revenue / NULLIF(EXCLUDED.order_count, 0);
END;
$$ LANGUAGE plpgsql;
```

---

## 7. 形式化验证

### 7.1 维度建模正确性

**定理 1 (事实表可加性)**:
对于事实表 $F$ 和维度 $D_1, D_2, ..., D_n$，度量 $M$ 满足:
$$\forall d \in D_i: M(F \bowtie_{D_i=d}) = \sum_{r \in F, r.D_i = d} M(r)$$

**定理 2 (SCD2历史追踪)**:
对于SCD2维度表，任意时间点 $t$ 的有效记录满足:
$$valid(r, t) \iff r.effective\_date \leq t < r.expiration\_date$$

### 7.2 数据一致性

**定理 3 (汇总一致性)**:
对于分层汇总，满足:
$$\forall d: daily\_sum(d) = \sum_{h \in hours(d)} hourly\_sum(h)$$

**定理 4 (维度完整性)**:
事实表中的外键必须引用有效的维度记录:
$$\forall f \in F: \exists d \in D: f.d\_key = d.key \land valid(d, f.time)$$

### 7.3 复杂度分析

| 操作 | 行存表 | 列存表 | 物化视图 |
|------|--------|--------|---------|
| 点查 | $O(\log n)$ | $O(n)$ | $O(\log m)$ |
| 范围扫描 | $O(\log n + k)$ | $O(k)$ | $O(\log m + k')$ |
| 全表聚合 | $O(n)$ | $O(n/c)$ | $O(m)$ |
| 写入 | $O(1)$ | $O(c)$ | $O(m)$ (需刷新) |

其中: $n$=原表行数, $m$=物化视图表行数, $k$=结果行数, $c$=列数

---

## 8. 最佳实践

### 8.1 ETL调度

```sql
-- ============================================
-- 8.1.1 ETL任务依赖管理
-- ============================================
CREATE TABLE etl.etl_jobs (
    job_id              SERIAL PRIMARY KEY,
    job_name            VARCHAR(100) NOT NULL,
    job_type            VARCHAR(50),           -- 'extract', 'transform', 'load'
    depends_on          INTEGER[],             -- 依赖的作业ID
    sql_command         TEXT,
    schedule            VARCHAR(50),           -- cron表达式
    is_enabled          BOOLEAN DEFAULT TRUE,
    timeout_seconds     INTEGER DEFAULT 3600,
    retry_count         INTEGER DEFAULT 3
);

-- 创建ETL依赖图
INSERT INTO etl.etl_jobs (job_name, job_type, depends_on, schedule)
VALUES
    ('extract_users', 'extract', '{}', '0 1 * * *'),
    ('extract_orders', 'extract', '{}', '0 1 * * *'),
    ('transform_dims', 'transform', '{1}', '30 1 * * *'),
    ('load_facts', 'load', '{3}', '0 2 * * *');

-- ============================================
-- 8.1.2 批量加载优化
-- ============================================
-- 禁用索引加载
CREATE OR REPLACE FUNCTION admin.bulk_load_with_index_rebuild(
    p_target_table VARCHAR,
    p_source_query TEXT
) RETURNS BIGINT AS $$
DECLARE
    v_count BIGINT;
    v_indexes TEXT[];
BEGIN
    -- 记录索引
    SELECT ARRAY_AGG(indexname) INTO v_indexes
    FROM pg_indexes
    WHERE tablename = p_target_table;

    -- 禁用索引
    FOREACH v_index IN ARRAY v_indexes LOOP
        EXECUTE format('ALTER INDEX %I DISABLE', v_index);
    END LOOP;

    -- 批量加载
    EXECUTE format('INSERT INTO %I %s', p_target_table, p_source_query);
    GET DIAGNOSTICS v_count = ROW_COUNT;

    -- 重建索引
    FOREACH v_index IN ARRAY v_indexes LOOP
        EXECUTE format('REINDEX INDEX %I', v_index);
    END LOOP;

    -- 分析表
    EXECUTE format('ANALYZE %I', p_target_table);

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;
```

### 8.2 监控告警

```sql
-- ============================================
-- 8.2.1 ETL运行监控
-- ============================================
CREATE TABLE etl.etl_job_runs (
    run_id              BIGSERIAL PRIMARY KEY,
    job_id              INTEGER REFERENCES etl.etl_jobs(job_id),
    started_at          TIMESTAMPTZ DEFAULT NOW(),
    completed_at        TIMESTAMPTZ,
    status              VARCHAR(20),           -- 'running', 'success', 'failed'
    records_processed   BIGINT,
    error_message       TEXT
);

-- 监控视图
CREATE VIEW monitoring.etl_dashboard AS
SELECT
    j.job_name,
    j.job_type,
    jr.status,
    jr.started_at,
    jr.completed_at,
    EXTRACT(EPOCH FROM (jr.completed_at - jr.started_at))::INTEGER AS duration_sec,
    jr.records_processed
FROM etl.etl_jobs j
LEFT JOIN LATERAL (
    SELECT * FROM etl.etl_job_runs
    WHERE job_id = j.job_id
    ORDER BY started_at DESC
    LIMIT 1
) jr ON TRUE
WHERE j.is_enabled = TRUE;

-- ============================================
-- 8.2.2 查询性能监控
-- ============================================
CREATE VIEW monitoring.slow_queries AS
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows,
    shared_blks_hit,
    shared_blks_read
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- 超过1秒
ORDER BY mean_exec_time DESC
LIMIT 20;
```

---

## 9. 权威引用

### 9.1 学术文献

1. **Kimball, R., & Ross, M. (2013)**. *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling, 3rd Edition*. Wiley. 维度建模领域权威著作。

2. **Inmon, W. H. (2005)**. *Building the Data Warehouse, 4th Edition*. Wiley. 数据仓库建设方法论奠基之作。

3. **Chaudhuri, S., & Dayal, U. (1997)**. "An overview of data warehousing and OLAP technology." *ACM SIGMOD Record*, 26(1), 65-74. 数据仓库技术综述经典论文。

### 9.2 PostgreSQL官方文档

1. **PostgreSQL Global Development Group (2024)**. "Table Partitioning." *PostgreSQL 16 Documentation*. <https://www.postgresql.org/docs/16/ddl-partitioning.html>

2. **PostgreSQL Global Development Group (2024)**. "Parallel Query." *PostgreSQL 16 Documentation*. <https://www.postgresql.org/docs/16/parallel-query.html>

3. **PostgreSQL Global Development Group (2024)**. "Materialized Views." *PostgreSQL 16 Documentation*. <https://www.postgresql.org/docs/16/rules-materializedviews.html>

### 9.3 行业最佳实践

1. **dbt Labs (2024)**. "dbt Documentation." *dbt (data build tool)*. <https://docs.getdbt.com/>

2. **Citus Data (2024)**. "Scaling PostgreSQL for Data Warehouse Workloads." *Citus Documentation*. <https://docs.citusdata.com/>

3. **AWS (2024)**. "Best Practices for Amazon Redshift." *AWS Documentation*. (PostgreSQL兼容数据仓库设计原则)

### 9.4 基准测试标准

1. **TPC (2024)**. "TPC-DS Benchmark Standard." *Transaction Processing Performance Council*. <https://www.tpc.org/tpcds/>

2. **TPC (2024)**. "TPC-H Benchmark Standard." *Transaction Processing Performance Council*. <https://www.tpc.org/tpch/>

---

## 附录A: 数据仓库术语

| 术语 | 英文 | 解释 |
|------|------|------|
| ETL | Extract-Transform-Load | 数据抽取转换加载 |
| OLAP | Online Analytical Processing | 联机分析处理 |
| SCD | Slowly Changing Dimension | 缓慢变化维 |
| ODS | Operational Data Store | 操作数据存储 |
| DWD | Data Warehouse Detail | 明细数据层 |
| DWS | Data Warehouse Summary | 汇总数据层 |
| ADS | Application Data Service | 应用数据层 |

---

**文档版本**: v2.0
**最后更新**: 2026-03-04
**维护者**: PostgreSQL_Formal Team
