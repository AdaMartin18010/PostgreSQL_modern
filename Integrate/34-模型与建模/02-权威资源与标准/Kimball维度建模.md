# Kimball维度建模完整指南

> **创建日期**: 2025年1月
> **来源**: 《数据仓库工具箱：维度建模权威指南》- Ralph Kimball & Margy Ross
> **状态**: 基于权威资源深化扩展
> **文档编号**: 02-02

---

## 📑 目录

- [Kimball维度建模完整指南](#kimball维度建模完整指南)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [1.1 理论基础](#11-理论基础)
    - [1.1.1 Kimball维度建模理论](#111-kimball维度建模理论)
    - [1.1.2 四个关键决策理论](#112-四个关键决策理论)
    - [1.1.3 星型模式理论](#113-星型模式理论)
    - [1.1.4 维度表去范式化理论](#114-维度表去范式化理论)
    - [1.1.5 复杂度分析](#115-复杂度分析)
  - [2. 核心原则](#2-核心原则)
    - [2.1 Kimball的四个关键决策](#21-kimball的四个关键决策)
  - [3. 维度建模基础](#3-维度建模基础)
    - [3.1 星型模式（Star Schema）](#31-星型模式star-schema)
    - [3.2 雪花模式（Snowflake Schema）](#32-雪花模式snowflake-schema)
    - [3.3 星型模式 vs 雪花模式](#33-星型模式-vs-雪花模式)
  - [4. 事实表技术](#4-事实表技术)
    - [4.1 事务事实表（Transaction Fact Table）](#41-事务事实表transaction-fact-table)
    - [4.2 周期快照事实表（Periodic Snapshot Fact Table）](#42-周期快照事实表periodic-snapshot-fact-table)
    - [4.3 累积快照事实表（Accumulating Snapshot Fact Table）](#43-累积快照事实表accumulating-snapshot-fact-table)
  - [5. 维度表技术](#5-维度表技术)
    - [5.1 缓慢变化维度（Slowly Changing Dimensions, SCD）](#51-缓慢变化维度slowly-changing-dimensions-scd)
      - [5.1.1 SCD Type 1: 覆盖历史值](#511-scd-type-1-覆盖历史值)
      - [5.1.2 SCD Type 2: 保留完整历史](#512-scd-type-2-保留完整历史)
      - [5.1.3 SCD Type 3: 保留有限历史](#513-scd-type-3-保留有限历史)
    - [5.2 角色扮演维度（Role-Playing Dimensions）](#52-角色扮演维度role-playing-dimensions)
    - [5.3 杂项维度（Junk Dimensions）](#53-杂项维度junk-dimensions)
  - [6. Kimball建模最佳实践](#6-kimball建模最佳实践)
    - [6.1 业务需求驱动](#61-业务需求驱动)
    - [6.2 粒度设计](#62-粒度设计)
    - [6.3 维度表去范式化](#63-维度表去范式化)
    - [6.4 事实表设计](#64-事实表设计)
  - [7. 相关资源](#7-相关资源)
  - [8. 参考文档](#8-参考文档)

---

## 1. 概述

Kimball维度建模方法是数据仓库设计的权威方法论，由Ralph Kimball在1996年提出。
该方法以业务需求为驱动，采用星型模式（Star Schema）设计，强调易用性和查询性能。

---

## 1.1 理论基础

### 1.1.1 Kimball维度建模理论

**Kimball维度建模**:

- **核心思想**: 以业务需求为驱动，采用星型模式设计
- **设计原则**: 易用性、查询性能、业务理解
- **应用范围**: 数据仓库、OLAP系统

**维度建模特点**:

- **业务驱动**: 以业务需求为核心
- **星型模式**: 事实表+维度表的星型结构
- **去范式化**: 维度表去范式化优化查询

### 1.1.2 四个关键决策理论

**Kimball的四个关键决策**:

1. **业务过程（Business Process）**: 识别核心业务活动
2. **粒度（Grain）**: 定义事实表的详细程度
3. **维度（Dimensions）**: 描述业务过程的上下文
4. **事实（Facts）**: 业务过程的度量值

**决策原则**:

- **业务驱动**: 以业务需求为核心
- **粒度优先**: 先确定粒度，再设计维度
- **维度完整**: 维度表包含所有查询属性

### 1.1.3 星型模式理论

**星型模式（Star Schema）**:

- **定义**: 中心是事实表，周围是维度表
- **结构**: $Star = \{Fact, \{Dim_1, Dim_2, ..., Dim_n\}\}$
- **优势**: 查询简单、性能优异、易于理解

**星型模式特点**:

- **事实表**: 存储度量值，行数大
- **维度表**: 存储描述属性，行数小
- **关系**: 事实表通过外键连接维度表

### 1.1.4 维度表去范式化理论

**维度表去范式化**:

- **目的**: 优化查询性能，简化查询逻辑
- **方法**: 将维度属性合并到维度表
- **权衡**: 存储空间 vs 查询性能

**去范式化原则**:

- **查询优化**: 优先优化查询性能
- **存储权衡**: 在存储和性能间权衡
- **维护成本**: 考虑维护成本

### 1.1.5 复杂度分析

**存储复杂度**:

- **事实表**: $O(F)$ where F is number of facts
- **维度表**: $O(D)$ where D is number of dimensions
- **总存储**: $O(F + D)$

**查询复杂度**:

- **星型查询**: $O(\log F + \log D)$ with indexes
- **聚合查询**: $O(\log F)$ with aggregation

---

## 2. 核心原则

### 2.1 Kimball的四个关键决策

1. **业务过程（Business Process）**: 识别核心业务活动
2. **粒度（Grain）**: 定义事实表的详细程度
3. **维度（Dimensions）**: 描述业务过程的上下文
4. **事实（Facts）**: 业务过程的度量值

---

## 3. 维度建模基础

### 3.1 星型模式（Star Schema）

**定义**: 中心是事实表，周围是维度表，形成星型结构。

**特点**:

- 事实表存储度量值（事实）
- 维度表存储描述性属性
- 维度表去范式化（Denormalized）
- 查询性能优异

**示例**:

```sql
-- 事实表：销售事实（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_sales') THEN
        CREATE TABLE fact_sales (
            sale_id BIGSERIAL PRIMARY KEY,
            date_id INT NOT NULL,
            product_id INT NOT NULL,
            customer_id INT NOT NULL,
            store_id INT NOT NULL,
            quantity INT NOT NULL,
            amount NUMERIC(10,2) NOT NULL,
            cost NUMERIC(10,2) NOT NULL,
            profit NUMERIC(10,2) GENERATED ALWAYS AS (amount - cost) STORED
        );
        RAISE NOTICE '表 fact_sales 创建成功';
    ELSE
        RAISE NOTICE '表 fact_sales 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 fact_sales 失败: %', SQLERRM;
END $$;

-- 维度表：日期维度（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_date') THEN
        CREATE TABLE dim_date (
            date_id INT PRIMARY KEY,
            date_actual DATE NOT NULL UNIQUE,
            day_name VARCHAR(10),
            day_of_week INT,
            day_of_month INT,
            day_of_year INT,
            week_of_year INT,
            month_name VARCHAR(10),
            month_of_year INT,
            quarter_name VARCHAR(2),
            quarter_of_year INT,
            year INT,
            is_weekend BOOLEAN,
            is_holiday BOOLEAN
        );
        RAISE NOTICE '表 dim_date 创建成功';
    ELSE
        RAISE NOTICE '表 dim_date 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 dim_date 失败: %', SQLERRM;
END $$;

-- 维度表：产品维度（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_product') THEN
        CREATE TABLE dim_product (
            product_id INT PRIMARY KEY,
            product_code VARCHAR(50) UNIQUE NOT NULL,
            product_name VARCHAR(200) NOT NULL,
            category_name VARCHAR(100),
            brand_name VARCHAR(100),
            unit_price NUMERIC(10,2),
            is_active BOOLEAN DEFAULT TRUE
        );
        RAISE NOTICE '表 dim_product 创建成功';
    ELSE
        RAISE NOTICE '表 dim_product 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 dim_product 失败: %', SQLERRM;
END $$;

-- 维度表：客户维度（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_customer') THEN
        CREATE TABLE dim_customer (
            customer_id INT PRIMARY KEY,
            customer_code VARCHAR(50) UNIQUE NOT NULL,
            customer_name VARCHAR(200) NOT NULL,
            city VARCHAR(100),
            state VARCHAR(50),
            country VARCHAR(50),
            customer_segment VARCHAR(50)
        );
        RAISE NOTICE '表 dim_customer 创建成功';
    ELSE
        RAISE NOTICE '表 dim_customer 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 dim_customer 失败: %', SQLERRM;
END $$;

-- 维度表：门店维度（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_store') THEN
        CREATE TABLE dim_store (
            store_id INT PRIMARY KEY,
            store_code VARCHAR(50) UNIQUE NOT NULL,
            store_name VARCHAR(200) NOT NULL,
            city VARCHAR(100),
            state VARCHAR(50),
            country VARCHAR(50),
            store_type VARCHAR(50),
            square_feet INT
        );
        RAISE NOTICE '表 dim_store 创建成功';
    ELSE
        RAISE NOTICE '表 dim_store 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 dim_store 失败: %', SQLERRM;
END $$;

-- 外键约束（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_sales_date' AND conrelid = 'fact_sales'::regclass
    ) THEN
        ALTER TABLE fact_sales
        ADD CONSTRAINT fk_sales_date FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
        ADD CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
        ADD CONSTRAINT fk_sales_customer FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
        ADD CONSTRAINT fk_sales_store FOREIGN KEY (store_id) REFERENCES dim_store(store_id);
        RAISE NOTICE '外键约束创建成功';
    ELSE
        RAISE NOTICE '外键约束已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '请先创建所有维度表';
    WHEN OTHERS THEN
        RAISE WARNING '创建外键约束失败: %', SQLERRM;
END $$;

-- 创建索引优化查询（带错误处理）
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_sales_date ON fact_sales(date_id);
    CREATE INDEX IF NOT EXISTS idx_sales_product ON fact_sales(product_id);
    CREATE INDEX IF NOT EXISTS idx_sales_customer ON fact_sales(customer_id);
    CREATE INDEX IF NOT EXISTS idx_sales_store ON fact_sales(store_id);
    CREATE INDEX IF NOT EXISTS idx_sales_date_product ON fact_sales(date_id, product_id);
    RAISE NOTICE '索引创建成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建索引失败: %', SQLERRM;
END $$;
```

---

### 3.2 雪花模式（Snowflake Schema）

**定义**: 维度表进一步规范化，形成多层级结构。

**特点**:

- 维度表规范化（Normalized）
- 减少数据冗余
- 查询需要更多JOIN
- 存储空间更小

**示例**:

```sql
-- 雪花模式：产品维度规范化（带错误处理）
DO $$
BEGIN
    -- 创建部门维度表
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_department') THEN
        CREATE TABLE dim_department (
            department_id INT PRIMARY KEY,
            department_name VARCHAR(100) NOT NULL
        );
        RAISE NOTICE '表 dim_department 创建成功';
    ELSE
        RAISE NOTICE '表 dim_department 已存在，跳过创建';
    END IF;

    -- 创建分类维度表
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_category') THEN
        CREATE TABLE dim_category (
            category_id INT PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL,
            department_id INT NOT NULL
        );
        RAISE NOTICE '表 dim_category 创建成功';
    ELSE
        RAISE NOTICE '表 dim_category 已存在，跳过创建';
    END IF;

    -- 创建品牌维度表
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_brand') THEN
        CREATE TABLE dim_brand (
            brand_id INT PRIMARY KEY,
            brand_name VARCHAR(100) NOT NULL
        );
        RAISE NOTICE '表 dim_brand 创建成功';
    ELSE
        RAISE NOTICE '表 dim_brand 已存在，跳过创建';
    END IF;

    -- 创建产品维度表（雪花模式）
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_product_snowflake') THEN
        CREATE TABLE dim_product_snowflake (
            product_id INT PRIMARY KEY,
            product_code VARCHAR(50) UNIQUE NOT NULL,
            product_name VARCHAR(200) NOT NULL,
            category_id INT NOT NULL,
            brand_id INT NOT NULL,
            unit_price NUMERIC(10,2)
        );
        RAISE NOTICE '表 dim_product_snowflake 创建成功';
    ELSE
        RAISE NOTICE '表 dim_product_snowflake 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建维度表失败: %', SQLERRM;
END $$;

-- 外键关系（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_product_category' AND conrelid = 'dim_product_snowflake'::regclass
    ) THEN
        ALTER TABLE dim_product_snowflake
        ADD CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES dim_category(category_id),
        ADD CONSTRAINT fk_product_brand FOREIGN KEY (brand_id) REFERENCES dim_brand(brand_id);
        RAISE NOTICE '产品表外键约束创建成功';
    ELSE
        RAISE NOTICE '产品表外键约束已存在，跳过创建';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_category_department' AND conrelid = 'dim_category'::regclass
    ) THEN
        ALTER TABLE dim_category
        ADD CONSTRAINT fk_category_department FOREIGN KEY (department_id) REFERENCES dim_department(department_id);
        RAISE NOTICE '分类表外键约束创建成功';
    ELSE
        RAISE NOTICE '分类表外键约束已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '请先创建所有相关维度表';
    WHEN OTHERS THEN
        RAISE WARNING '创建外键约束失败: %', SQLERRM;
END $$;
```

---

### 3.3 星型模式 vs 雪花模式

| 维度 | 星型模式 | 雪花模式 |
| ------ | --------- | --------- |
| **查询性能** | ⭐⭐⭐⭐⭐ 快速 | ⭐⭐☆☆☆ 较慢（多JOIN） |
| **存储空间** | ⭐⭐⭐☆☆ 冗余 | ⭐⭐⭐⭐⭐ 节省 |
| **维护成本** | ⭐⭐⭐⭐☆ 简单 | ⭐⭐⭐☆☆ 复杂 |
| **易用性** | ⭐⭐⭐⭐⭐ 直观 | ⭐⭐⭐☆☆ 复杂 |
| **适用场景** | 大多数OLAP场景 | 存储敏感场景 |

**Kimball建议**: 优先使用星型模式，除非存储成本是主要考虑因素。

---

## 4. 事实表技术

### 4.1 事务事实表（Transaction Fact Table）

**定义**: 记录业务过程中的每个事务事件。

**特点**:

- 粒度：每个事务一行
- 事实：可加性度量（金额、数量）
- 时间：事务发生时间
- 不更新，只追加

**示例**:

```sql
-- 事务事实表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_sales_transaction') THEN
        CREATE TABLE fact_sales_transaction (
            sale_id BIGSERIAL PRIMARY KEY,
            transaction_time TIMESTAMPTZ NOT NULL,
            date_id INT NOT NULL,
            product_id INT NOT NULL,
            customer_id INT NOT NULL,
            store_id INT NOT NULL,
            salesperson_id INT,
            quantity INT NOT NULL,
            unit_price NUMERIC(10,2) NOT NULL,
            discount_amount NUMERIC(10,2) DEFAULT 0,
            total_amount NUMERIC(10,2) NOT NULL,
            cost_amount NUMERIC(10,2) NOT NULL,
            profit_amount NUMERIC(10,2) GENERATED ALWAYS AS (total_amount - cost_amount) STORED
        );
        RAISE NOTICE '表 fact_sales_transaction 创建成功';
    ELSE
        RAISE NOTICE '表 fact_sales_transaction 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 fact_sales_transaction 失败: %', SQLERRM;
END $$;

-- 分区策略（按日期，带错误处理）
-- 注意：需要先删除原表才能改为分区表，这里提供分区表创建示例
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_sales_transaction_partitioned') THEN
        CREATE TABLE fact_sales_transaction_partitioned (
            sale_id BIGSERIAL,
            transaction_time TIMESTAMPTZ NOT NULL,
            date_id INT NOT NULL,
            product_id INT NOT NULL,
            customer_id INT NOT NULL,
            store_id INT NOT NULL,
            quantity INT NOT NULL,
            total_amount NUMERIC(10,2) NOT NULL,
            PRIMARY KEY (sale_id, date_id)
        ) PARTITION BY RANGE (date_id);
        RAISE NOTICE '分区表 fact_sales_transaction_partitioned 创建成功';
    ELSE
        RAISE NOTICE '表 fact_sales_transaction_partitioned 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建分区表失败: %', SQLERRM;
END $$;

-- 创建月度分区（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_sales_transaction_partitioned') THEN
        CREATE TABLE IF NOT EXISTS fact_sales_transaction_202401 PARTITION OF fact_sales_transaction_partitioned
            FOR VALUES FROM (20240101) TO (20240201);
        CREATE TABLE IF NOT EXISTS fact_sales_transaction_202402 PARTITION OF fact_sales_transaction_partitioned
            FOR VALUES FROM (20240201) TO (20240301);
        RAISE NOTICE '分区创建成功';
    ELSE
        RAISE WARNING '请先创建 fact_sales_transaction_partitioned 分区表';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '分区已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE WARNING '创建分区失败: %', SQLERRM;
END $$;
```

---

### 4.2 周期快照事实表（Periodic Snapshot Fact Table）

**定义**: 定期记录业务状态的快照。

**特点**:

- 粒度：每个时间周期一行
- 事实：半可加性度量（余额、库存）
- 时间：快照时间点
- 定期更新

**示例**:

```sql
-- 周期快照事实表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_account_balance') THEN
        CREATE TABLE fact_account_balance (
            snapshot_id BIGSERIAL PRIMARY KEY,
            snapshot_date DATE NOT NULL,
            date_id INT NOT NULL,
            account_id INT NOT NULL,
            customer_id INT NOT NULL,
            account_type VARCHAR(50),
            opening_balance NUMERIC(15,2) NOT NULL,
            closing_balance NUMERIC(15,2) NOT NULL,
            transaction_count INT DEFAULT 0,
            deposit_amount NUMERIC(15,2) DEFAULT 0,
            withdrawal_amount NUMERIC(15,2) DEFAULT 0,
            UNIQUE (snapshot_date, account_id)
        );
        RAISE NOTICE '表 fact_account_balance 创建成功';
    ELSE
        RAISE NOTICE '表 fact_account_balance 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 fact_account_balance 失败: %', SQLERRM;
END $$;

-- 每日快照
INSERT INTO fact_account_balance (
    snapshot_date, date_id, account_id, customer_id,
    opening_balance, closing_balance, transaction_count
)
SELECT
    CURRENT_DATE,
    TO_CHAR(CURRENT_DATE, 'YYYYMMDD')::INT,
    account_id,
    customer_id,
    LAG(closing_balance, 1, 0) OVER (PARTITION BY account_id ORDER BY snapshot_date) AS opening_balance,
    closing_balance,
    transaction_count
FROM fact_account_balance
WHERE snapshot_date = CURRENT_DATE - INTERVAL '1 day';
```

---

### 4.3 累积快照事实表（Accumulating Snapshot Fact Table）

**定义**: 记录业务过程的生命周期，从开始到结束。

**特点**:

- 粒度：每个业务过程一行
- 事实：过程各阶段的度量
- 时间：多个时间戳（开始、中间、结束）
- 更新生命周期状态

**示例**:

```sql
-- 累积快照事实表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_order_fulfillment') THEN
        CREATE TABLE fact_order_fulfillment (
            order_id BIGINT PRIMARY KEY,
            order_date DATE NOT NULL,
            order_date_id INT NOT NULL,
            customer_id INT NOT NULL,
            product_id INT NOT NULL,
            order_quantity INT NOT NULL,

            -- 订单生命周期时间点
            order_placed_date DATE,
            order_placed_date_id INT,
            order_processed_date DATE,
            order_processed_date_id INT,
            order_shipped_date DATE,
            order_shipped_date_id INT,
            order_delivered_date DATE,
            order_delivered_date_id INT,
            order_cancelled_date DATE,
            order_cancelled_date_id INT,

            -- 各阶段度量
            order_amount NUMERIC(10,2),
            shipping_cost NUMERIC(10,2),
            total_amount NUMERIC(10,2),

            -- 计算字段
            days_to_process INT GENERATED ALWAYS AS (
                CASE WHEN order_processed_date IS NOT NULL
                THEN order_processed_date - order_placed_date
                ELSE NULL END
            ) STORED,
            days_to_ship INT GENERATED ALWAYS AS (
                CASE WHEN order_shipped_date IS NOT NULL
                THEN order_shipped_date - order_processed_date
                ELSE NULL END
            ) STORED,
            days_to_deliver INT GENERATED ALWAYS AS (
                CASE WHEN order_delivered_date IS NOT NULL
                THEN order_delivered_date - order_shipped_date
                ELSE NULL END
            ) STORED,
            total_days INT GENERATED ALWAYS AS (
                CASE WHEN order_delivered_date IS NOT NULL
                THEN order_delivered_date - order_placed_date
                ELSE NULL END
            ) STORED
        );
        RAISE NOTICE '表 fact_order_fulfillment 创建成功';
    ELSE
        RAISE NOTICE '表 fact_order_fulfillment 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 fact_order_fulfillment 失败: %', SQLERRM;
END $$;

-- 更新订单状态
UPDATE fact_order_fulfillment
SET
    order_shipped_date = CURRENT_DATE,
    order_shipped_date_id = TO_CHAR(CURRENT_DATE, 'YYYYMMDD')::INT
WHERE order_id = 12345
  AND order_shipped_date IS NULL;
```

---

## 5. 维度表技术

### 5.1 缓慢变化维度（Slowly Changing Dimensions, SCD）

#### 5.1.1 SCD Type 1: 覆盖历史值

**定义**: 直接更新维度记录，不保留历史。

**适用场景**: 错误修正、不重要的属性变化。

**示例**:

```sql
-- SCD Type 1维度表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_customer_type1') THEN
        CREATE TABLE dim_customer_type1 (
            customer_id INT PRIMARY KEY,
            customer_code VARCHAR(50) UNIQUE NOT NULL,
            customer_name VARCHAR(200) NOT NULL,
            city VARCHAR(100),
            state VARCHAR(50),
            country VARCHAR(50),
            customer_segment VARCHAR(50),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        RAISE NOTICE '表 dim_customer_type1 创建成功';
    ELSE
        RAISE NOTICE '表 dim_customer_type1 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 dim_customer_type1 失败: %', SQLERRM;
END $$;

-- 更新客户信息（覆盖历史）
UPDATE dim_customer_type1
SET
    city = 'New City',
    customer_segment = 'Premium',
    updated_at = NOW()
WHERE customer_id = 12345;
```

---

#### 5.1.2 SCD Type 2: 保留完整历史

**定义**: 创建新记录保存历史版本，使用代理键和生效/失效时间。

**适用场景**: 需要历史追踪的重要属性变化。

**示例**:

```sql
-- SCD Type 2维度表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_customer_type2') THEN
        CREATE TABLE dim_customer_type2 (
            customer_sk SERIAL PRIMARY KEY,  -- 代理键
            customer_id INT NOT NULL,         -- 业务键
            customer_code VARCHAR(50) NOT NULL,
            customer_name VARCHAR(200) NOT NULL,
            city VARCHAR(100),
            state VARCHAR(50),
            country VARCHAR(50),
            customer_segment VARCHAR(50),
            effective_date DATE NOT NULL,
            expiry_date DATE,
            is_current BOOLEAN DEFAULT TRUE,
            UNIQUE (customer_id, effective_date)
        );
        RAISE NOTICE '表 dim_customer_type2 创建成功';
    ELSE
        RAISE NOTICE '表 dim_customer_type2 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 dim_customer_type2 失败: %', SQLERRM;
END $$;

-- 创建索引（带错误处理）
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_customer_type2_id ON dim_customer_type2(customer_id);
    CREATE INDEX IF NOT EXISTS idx_customer_type2_current ON dim_customer_type2(is_current) WHERE is_current = TRUE;
    RAISE NOTICE '索引创建成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建索引失败: %', SQLERRM;
END $$;

-- 插入新客户
INSERT INTO dim_customer_type2 (
    customer_id, customer_code, customer_name, city,
    customer_segment, effective_date, is_current
)
VALUES (
    12345, 'C001', 'John Doe', 'New York',
    'Standard', '2024-01-01', TRUE
);

-- 客户信息变更（SCD Type 2处理）
BEGIN;

-- 1. 将当前记录设为失效
UPDATE dim_customer_type2
SET
    expiry_date = CURRENT_DATE - INTERVAL '1 day',
    is_current = FALSE
WHERE customer_id = 12345
  AND is_current = TRUE;

-- 2. 插入新记录
INSERT INTO dim_customer_type2 (
    customer_id, customer_code, customer_name, city,
    customer_segment, effective_date, is_current
)
VALUES (
    12345, 'C001', 'John Doe', 'Los Angeles',  -- 城市变更
    'Premium',  -- 客户等级变更
    CURRENT_DATE,
    TRUE
);

COMMIT;

-- 查询当前版本
SELECT * FROM dim_customer_type2
WHERE customer_id = 12345
  AND is_current = TRUE;

-- 查询历史版本
SELECT * FROM dim_customer_type2
WHERE customer_id = 12345
ORDER BY effective_date DESC;
```

---

#### 5.1.3 SCD Type 3: 保留有限历史

**定义**: 在当前记录中保存前一个值。

**适用场景**: 只需要最近一次变化的历史。

**示例**:

```sql
-- SCD Type 3维度表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_customer_type3') THEN
        CREATE TABLE dim_customer_type3 (
            customer_id INT PRIMARY KEY,
            customer_code VARCHAR(50) UNIQUE NOT NULL,
            customer_name VARCHAR(200) NOT NULL,
            city VARCHAR(100),
            previous_city VARCHAR(100),  -- 前一个城市
            city_changed_date DATE,      -- 变更日期
            customer_segment VARCHAR(50),
            previous_segment VARCHAR(50),
            segment_changed_date DATE
        );
        RAISE NOTICE '表 dim_customer_type3 创建成功';
    ELSE
        RAISE NOTICE '表 dim_customer_type3 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 dim_customer_type3 失败: %', SQLERRM;
END $$;

-- 更新客户信息（保留前一个值）
UPDATE dim_customer_type3
SET
    previous_city = city,
    city = 'New City',
    city_changed_date = CURRENT_DATE,
    previous_segment = customer_segment,
    customer_segment = 'Premium',
    segment_changed_date = CURRENT_DATE
WHERE customer_id = 12345;
```

---

### 5.2 角色扮演维度（Role-Playing Dimensions）

**定义**: 同一个维度表在事实表中多次出现，扮演不同角色。

**示例**:

```sql
-- 角色扮演维度示例（带错误处理，需要先创建dim_date表）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_orders') THEN
        CREATE TABLE fact_orders (
            order_id BIGSERIAL PRIMARY KEY,
            order_date_id INT NOT NULL,      -- 订单日期
            ship_date_id INT,                -- 发货日期
            delivery_date_id INT,            -- 交付日期
            customer_id INT NOT NULL,
            product_id INT NOT NULL,
            order_amount NUMERIC(10,2) NOT NULL,
            CONSTRAINT fk_order_date FOREIGN KEY (order_date_id) REFERENCES dim_date(date_id),
            CONSTRAINT fk_ship_date FOREIGN KEY (ship_date_id) REFERENCES dim_date(date_id),
            CONSTRAINT fk_delivery_date FOREIGN KEY (delivery_date_id) REFERENCES dim_date(date_id)
        );
        RAISE NOTICE '表 fact_orders 创建成功';
    ELSE
        RAISE NOTICE '表 fact_orders 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '请先创建 dim_date 表';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 fact_orders 失败: %', SQLERRM;
END $$;

-- 查询时使用表别名区分角色
SELECT
    od.year AS order_year,
    sd.month_name AS ship_month,
    dd.day_name AS delivery_day,
    SUM(fo.order_amount) AS total_amount
FROM fact_orders fo
JOIN dim_date od ON fo.order_date_id = od.date_id
JOIN dim_date sd ON fo.ship_date_id = sd.date_id
JOIN dim_date dd ON fo.delivery_date_id = dd.date_id
GROUP BY od.year, sd.month_name, dd.day_name;
```

---

### 5.3 杂项维度（Junk Dimensions）

**定义**: 将多个低基数的标志位和属性组合成一个维度。

**目的**: 减少事实表的列数，提高查询性能。

**示例**:

```sql
-- 杂项维度：组合多个标志位（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_junk') THEN
        CREATE TABLE dim_junk (
            junk_id SERIAL PRIMARY KEY,
            payment_method VARCHAR(20),      -- 支付方式
            delivery_method VARCHAR(20),     -- 配送方式
            order_source VARCHAR(20),        -- 订单来源
            is_gift BOOLEAN,                 -- 是否礼品
            is_express BOOLEAN,              -- 是否加急
            is_international BOOLEAN,        -- 是否国际
            UNIQUE (payment_method, delivery_method, order_source, is_gift, is_express, is_international)
        );
        RAISE NOTICE '表 dim_junk 创建成功';
    ELSE
        RAISE NOTICE '表 dim_junk 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 dim_junk 失败: %', SQLERRM;
END $$;

-- 事实表引用杂项维度（带错误处理，注意避免与上面的fact_orders冲突）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_orders_with_junk') THEN
        CREATE TABLE fact_orders_with_junk (
            order_id BIGSERIAL PRIMARY KEY,
            date_id INT NOT NULL,
            customer_id INT NOT NULL,
            product_id INT NOT NULL,
            junk_id INT NOT NULL,  -- 引用杂项维度
            order_amount NUMERIC(10,2) NOT NULL,
            CONSTRAINT fk_order_junk FOREIGN KEY (junk_id) REFERENCES dim_junk(junk_id)
        );
        RAISE NOTICE '表 fact_orders_with_junk 创建成功';
    ELSE
        RAISE NOTICE '表 fact_orders_with_junk 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '请先创建 dim_junk 表';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 fact_orders_with_junk 失败: %', SQLERRM;
END $$;
```

---

## 6. Kimball建模最佳实践

### 6.1 业务需求驱动

**原则**: 从业务需求出发，而非数据源结构。

**步骤**:

1. 识别业务过程（如销售、库存、订单）
2. 确定业务度量（如销售额、订单数）
3. 识别维度（如时间、产品、客户）

---

### 6.2 粒度设计

**原则**: 选择最细粒度的数据，支持向上汇总。

**示例**:

```sql
-- ✅ 正确：事务级粒度（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_sales_transaction_fine') THEN
        CREATE TABLE fact_sales_transaction_fine (
            transaction_id BIGSERIAL PRIMARY KEY,
            transaction_time TIMESTAMPTZ NOT NULL,
            date_id INT NOT NULL,
            product_id INT NOT NULL,
            customer_id INT NOT NULL,
            quantity INT NOT NULL,
            amount NUMERIC(10,2) NOT NULL
        );
        RAISE NOTICE '表 fact_sales_transaction_fine 创建成功';
    ELSE
        RAISE NOTICE '表 fact_sales_transaction_fine 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 fact_sales_transaction_fine 失败: %', SQLERRM;
END $$;

-- ❌ 错误：汇总级粒度（无法向下钻取，带错误处理，示例表）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_sales_daily_bad') THEN
        CREATE TABLE fact_sales_daily_bad (
            sale_date DATE PRIMARY KEY,
            total_amount NUMERIC(10,2)  -- 已汇总，无法分析明细
        );
        RAISE NOTICE '表 fact_sales_daily_bad 创建成功（反模式示例）';
    ELSE
        RAISE NOTICE '表 fact_sales_daily_bad 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建示例表失败: %', SQLERRM;
END $$;
```

---

### 6.3 维度表去范式化

**原则**: 维度表应该去范式化，减少JOIN操作。

**示例**:

```sql
-- ✅ 正确：星型模式（去范式化，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_product_star') THEN
        CREATE TABLE dim_product_star (
            product_id INT PRIMARY KEY,
            product_name VARCHAR(200),
            category_name VARCHAR(100),  -- 直接存储，不JOIN
            brand_name VARCHAR(100)       -- 直接存储，不JOIN
        );
        RAISE NOTICE '表 dim_product_star 创建成功';
    ELSE
        RAISE NOTICE '表 dim_product_star 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 dim_product_star 失败: %', SQLERRM;
END $$;

-- ⚠️ 可选：雪花模式（规范化，节省存储，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dim_product_snowflake_example') THEN
        CREATE TABLE dim_product_snowflake_example (
            product_id INT PRIMARY KEY,
            product_name VARCHAR(200),
            category_id INT,  -- 需要JOIN
            brand_id INT      -- 需要JOIN
        );
        RAISE NOTICE '表 dim_product_snowflake_example 创建成功';
    ELSE
        RAISE NOTICE '表 dim_product_snowflake_example 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 dim_product_snowflake_example 失败: %', SQLERRM;
END $$;
```

---

### 6.4 事实表设计

**原则**:

- 只存储度量值（可加性事实）
- 避免存储文本描述（应放在维度表）
- 使用代理键作为主键
- 外键引用维度表的代理键

**示例**:

```sql
-- ✅ 正确：事实表只存储度量（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_sales_correct') THEN
        CREATE TABLE fact_sales_correct (
            sale_id BIGSERIAL PRIMARY KEY,
            date_id INT NOT NULL,
            product_id INT NOT NULL,
            customer_id INT NOT NULL,
            quantity INT NOT NULL,        -- 可加性事实
            amount NUMERIC(10,2) NOT NULL -- 可加性事实
        );
        RAISE NOTICE '表 fact_sales_correct 创建成功';
    ELSE
        RAISE NOTICE '表 fact_sales_correct 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 fact_sales_correct 失败: %', SQLERRM;
END $$;

-- ❌ 错误：事实表包含描述性属性（带错误处理，反模式示例）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'fact_sales_bad') THEN
        CREATE TABLE fact_sales_bad (
            sale_id BIGSERIAL PRIMARY KEY,
            product_name VARCHAR(200),    -- ❌ 应该在维度表
            customer_name VARCHAR(200),   -- ❌ 应该在维度表
            amount NUMERIC(10,2)
        );
        RAISE NOTICE '表 fact_sales_bad 创建成功（反模式示例）';
    ELSE
        RAISE NOTICE '表 fact_sales_bad 已存在，跳过创建';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建示例表失败: %', SQLERRM;
END $$;
```

---

## 7. 相关资源

- [维度建模基础](../05-OLAP建模/维度建模基础.md)
- [事实表技术](../05-OLAP建模/事实表技术.md)
- [维度表技术](../05-OLAP建模/维度表技术.md)
- [PostgreSQL列存实现](../05-OLAP建模/PostgreSQL列存实现.md)

---

## 8. 参考文档

- 《数据仓库工具箱：维度建模权威指南》- Ralph Kimball & Margy Ross
- Kimball Group网站: <https://www.kimballgroup.com/>
- PostgreSQL官方文档: [Table Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
