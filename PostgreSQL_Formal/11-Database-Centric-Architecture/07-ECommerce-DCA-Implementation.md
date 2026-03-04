# 电商系统数据库中心架构(DCA)实现

## 目录

- [电商系统数据库中心架构(DCA)实现](#电商系统数据库中心架构dca实现)
  - [目录](#目录)
  - [1. 系统概述](#1-系统概述)
    - [1.1 业务背景](#11-业务背景)
    - [1.2 设计目标](#12-设计目标)
    - [1.3 DCA核心原则](#13-dca核心原则)
  - [2. 系统架构设计](#2-系统架构设计)
    - [2.1 整体架构图](#21-整体架构图)
    - [2.2 模块交互关系](#22-模块交互关系)
    - [2.3 数据流向图](#23-数据流向图)
  - [3. 数据库设计](#3-数据库设计)
    - [3.1 完整ER图](#31-完整er图)
    - [3.2 数据库Schema创建](#32-数据库schema创建)
  - [4. 订单系统实现](#4-订单系统实现)
    - [4.1 订单状态机](#41-订单状态机)
    - [4.2 核心存储过程](#42-核心存储过程)
      - [4.2.1 创建订单存储过程](#421-创建订单存储过程)
      - [4.2.2 取消订单存储过程](#422-取消订单存储过程)
      - [4.2.3 确认收货存储过程](#423-确认收货存储过程)
      - [4.2.4 订单查询存储过程](#424-订单查询存储过程)
    - [4.3 订单相关触发器](#43-订单相关触发器)
  - [5. 库存系统实现](#5-库存系统实现)
    - [5.1 库存核心模型](#51-库存核心模型)
    - [5.2 库存核心存储过程](#52-库存核心存储过程)
      - [5.2.1 库存扣减存储过程](#521-库存扣减存储过程)
      - [5.2.2 库存入库存储过程](#522-库存入库存储过程)
      - [5.2.3 库存释放存储过程](#523-库存释放存储过程)
      - [5.2.4 库存盘点存储过程](#524-库存盘点存储过程)
      - [5.2.5 库存查询存储过程](#525-库存查询存储过程)
    - [5.3 库存相关触发器](#53-库存相关触发器)
  - [6. 支付系统实现](#6-支付系统实现)
    - [6.1 支付流程架构](#61-支付流程架构)
    - [6.2 支付核心存储过程](#62-支付核心存储过程)
      - [6.2.1 创建支付单存储过程](#621-创建支付单存储过程)
      - [6.2.2 支付回调处理存储过程](#622-支付回调处理存储过程)
      - [6.2.3 退款申请存储过程](#623-退款申请存储过程)
      - [6.2.4 退款处理存储过程](#624-退款处理存储过程)
    - [6.3 对账相关存储过程](#63-对账相关存储过程)
  - [7. 促销系统实现](#7-促销系统实现)
    - [7.1 促销架构设计](#71-促销架构设计)
    - [7.2 促销核心存储过程](#72-促销核心存储过程)
      - [7.2.1 优惠券计算函数](#721-优惠券计算函数)
      - [7.2.2 领取优惠券存储过程](#722-领取优惠券存储过程)
      - [7.2.3 秒杀下单存储过程](#723-秒杀下单存储过程)
      - [7.2.4 促销价格计算存储过程](#724-促销价格计算存储过程)
    - [7.3 促销相关触发器](#73-促销相关触发器)
  - [8. 性能优化策略](#8-性能优化策略)
    - [8.1 数据库优化措施](#81-数据库优化措施)
    - [8.2 缓存策略](#82-缓存策略)
  - [9. 安全控制措施](#9-安全控制措施)
    - [9.1 权限控制](#91-权限控制)
    - [9.2 SQL注入防护](#92-sql注入防护)
    - [9.3 审计日志](#93-审计日志)
  - [10. 测试方案](#10-测试方案)
    - [10.1 单元测试](#101-单元测试)
    - [10.2 集成测试](#102-集成测试)
    - [10.3 性能测试基准](#103-性能测试基准)
  - [11. 总结](#11-总结)
    - [11.1 核心特性总结](#111-核心特性总结)
    - [11.2 存储过程清单](#112-存储过程清单)
    - [11.3 扩展建议](#113-扩展建议)

---

## 1. 系统概述

### 1.1 业务背景

电商系统是典型的复杂业务场景，涉及订单、库存、支付、促销等多个核心域的协同工作。
在数据库中心架构(DCA)模式下，我们将业务逻辑下沉到数据库层，通过存储过程、触发器、函数等数据库对象实现核心业务规则，确保数据一致性、提升系统性能、简化应用层开发。

### 1.2 设计目标

- **强一致性**：订单、库存、支付数据严格一致
- **高性能**：支持秒杀等高并发场景，QPS > 10000
- **高可用**：99.99%可用性，故障自动恢复
- **可审计**：完整的操作日志和审计追踪
- **可扩展**：支持水平扩展和业务快速迭代

### 1.3 DCA核心原则

```
┌─────────────────────────────────────────────────────────────┐
│                    电商DCA架构层次图                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Web/API   │  │   Admin     │  │   Mobile    │  接入层   │
│  │   Gateway   │  │   Console   │  │    App      │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
├─────────┼────────────────┼────────────────┼─────────────────┤
│         │                │                │                 │
│  ┌──────▼────────────────▼────────────────▼──────┐           │
│  │              数据库服务层 (Service Layer)       │           │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐       │           │
│  │  │ 订单服务  │ │ 库存服务  │ │ 支付服务  │       │           │
│  │  │ sp_order_*│ │ sp_stock_*│ │ sp_pay_*  │       │           │
│  │  └──────────┘ └──────────┘ └──────────┘       │           │
│  └───────────────────────────────────────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐     │
│  │              数据库核心层 (Core Layer)               │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │     │
│  │  │ 订单引擎 │ │ 库存引擎 │ │ 支付引擎 │ │ 促销引擎 │   │     │
│  │  │ 触发器  │ │ 触发器  │ │ 触发器  │ │ 触发器  │   │     │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │     │
│  └─────────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐     │
│  │              数据存储层 (Storage Layer)              │     │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  │     │
│  │  │订单表│ │库存表│ │支付表│ │用户表│ │商品表│ │促销表│  │     │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘  │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 系统架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              电商平台系统架构                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐        │
│   │  用户端    │   │  商家端    │   │  运营后台  │   │  支付网关  │        │
│   │  (Web/App)│   │  (Portal) │   │  (Admin)  │   │  (Gateway)│        │
│   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘        │
│         │               │               │               │              │
│         └───────────────┴───────┬───────┴───────────────┘              │
│                                 │                                      │
│                        ┌────────▼────────┐                             │
│                        │   API Gateway   │                             │
│                        │   (Nginx/Kong)  │                             │
│                        └────────┬────────┘                             │
│                                 │                                      │
│   ╔═════════════════════════════╧═══════════════════════════════╗      │
│   ║                    数据库中心架构层 (DCA)                     ║      │
│   ║  ┌─────────────────────────────────────────────────────┐   ║      │
│   ║  │  业务编排层 (Business Orchestration)                 │   ║      │
│   ║  │  sp_create_order / sp_process_payment               │   ║      │
│   ║  │  sp_seckill_order / sp_apply_promotion              │   ║      │
│   ║  └─────────────────────────────────────────────────────┘   ║      │
│   ║  ┌─────────────────────────────────────────────────────┐   ║      │
│   ║  │  核心业务引擎 (Core Business Engine)                 │   ║      │
│   ║  │  trg_order_status_change / trg_inventory_update     │   ║      │
│   ║  │  trg_payment_callback / trg_promotion_calculate     │   ║      │
│   ║  └─────────────────────────────────────────────────────┘   ║      │
│   ║  ┌─────────────────────────────────────────────────────┐   ║      │
│   ║  │  数据访问层 (Data Access Layer)                      │   ║      │
│   ║  │  fn_get_price / fn_calc_discount / fn_check_stock   │   ║      │
│   ║  └─────────────────────────────────────────────────────┘   ║      │
│   ╚═══════════════════════════════════════════════════════════════╝      │
│                                 │                                      │
│   ┌─────────────────────────────┼─────────────────────────────┐        │
│   │         PostgreSQL Cluster   │                             │        │
│   │  ┌──────────┐ ┌──────────┐  │  ┌──────────┐ ┌──────────┐  │        │
│   │  │ Primary  │←│ Standby  │  │  │  pgPool   │ │  Redis   │  │        │
│   │  │   Node   │→│   Node   │  │  │ (HAProxy) │ │  Cache   │  │        │
│   │  └──────────┘ └──────────┘  │  └──────────┘ └──────────┘  │        │
│   └─────────────────────────────┼─────────────────────────────┘        │
│                                 │                                      │
│                        ┌────────▼────────┐                             │
│                        │   审计日志系统    │                             │
│                        │  (CDC/Debezium) │                             │
│                        └─────────────────┘                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块交互关系

```
                    ┌─────────────────────────────────────────────────────┐
                    │                    订单生命周期                         │
                    └─────────────────────────────────────────────────────┘
                                         │
     ┌───────────────────────────────────┼───────────────────────────────────┐
     │                                   │                                   │
     ▼                                   ▼                                   ▼
┌─────────┐                      ┌─────────────┐                    ┌─────────────┐
│  库存系统 │←─────────────────────→│    订单系统   │←─────────────────→│   支付系统   │
│         │   扣减/释放/锁定        │             │    支付/退款       │             │
│trg_stock│                      │  trg_order  │                    │ trg_payment │
│_lock    │                      │  _status    │                    │  _callback   │
└────┬────┘                      └──────┬──────┘                    └──────┬──────┘
     │                                  │                                  │
     │                                  │                                  │
     │                          ┌───────▼───────┐                         │
     │                          │    促销系统     │                         │
     └─────────────────────────→│               │←────────────────────────┘
           库存价格联动          │ trg_promotion │        支付优惠计算
                                │  _calculate   │
                                └───────────────┘
```

### 2.3 数据流向图

```
用户下单流程:
┌────────┐    ┌──────────────────────────────────────────────────────────────┐
│  用户   │    │                      数据库中心架构                            │
└───┬────┘    │                                                              │
    │         │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
    │         │  │   订单模块   │    │   库存模块   │    │   支付模块   │       │
    │         │  │             │    │             │    │             │       │
    │─────────│─→│ sp_create_  │───→│ sp_deduct_  │───→│ sp_create_  │       │
    │  下单    │  │    order    │    │    stock    │    │   payment   │       │
    │         │  │      ↓      │    │      ↓      │    │      ↓      │       │
    │         │  │ trg_order_  │    │ trg_stock_  │    │ trg_payment_│       │
    │         │  │  _validate  │    │   _check    │    │  _initiate  │       │
    │         │  │      ↓      │    │      ↓      │    │      ↓      │       │
    │         │  │ trg_order_  │    │ trg_stock_  │    │ trg_payment_│       │
    │         │  │  _create_log│    │   _log      │    │  _audit     │       │
    │         │  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘       │
    │         │         └──────────────────┼──────────────────┘              │
    │         │                            │                                 │
    │         │  ┌─────────────────────────▼─────────────────────────┐       │
    │         │  │              统一审计日志表 (audit_log)              │       │
    │         │  └─────────────────────────────────────────────────────┘       │
    │         │                                                                │
    │←────────│────────────────────────────────────────────────────────────────│
    │  响应    │                           事务提交/回滚                         │
    └─────────┘                                                                │
               └──────────────────────────────────────────────────────────────┘
```

---

## 3. 数据库设计

### 3.1 完整ER图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           电商系统数据库ER图                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐           │
│   │    users     │         │   products   │         │  categories  │           │
│   │──────────────│         │──────────────│         │──────────────│           │
│   │ PK user_id   │         │ PK product_id│         │ PK category_id│          │
│   │    username  │         │    name      │         │    name      │           │
│   │    email     │         │    sku       │         │    parent_id │──────┐   │
│   │    phone     │         │    price     │         │    level     │      │   │
│   │    status    │         │    stock_qty │         └──────────────┘      │   │
│   │    created_at│         │    category_id│──────────────────────────────┘   │
│   └──────┬───────┘         │    status     │                                  │
│          │                 └───────┬───────┘                                  │
│          │                         │                                          │
│          │         ┌───────────────┼──────────────────┐                      │
│          │         │               │                  │                      │
│          │         ▼               ▼                  ▼                      │
│          │    ┌──────────┐   ┌──────────┐     ┌──────────┐                 │
│          │    │ product_ │   │ inventory│     │ product_ │                 │
│          │    │  images  │   │  _log    │     │  specs   │                 │
│          │    └──────────┘   └──────────┘     └──────────┘                 │
│          │                                                                   │
│          ▼                                                                   │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐        │
│   │    orders    │◄────────│ order_items  │         │  shipments   │        │
│   │──────────────│         │──────────────│         │──────────────│        │
│   │ PK order_id  │         │ PK item_id   │         │ PK shipment_id│       │
│   │ FK user_id   │         │ FK order_id  │         │ FK order_id   │       │
│   │    order_no  │         │ FK product_id│         │    tracking_no│       │
│   │    status    │         │    quantity  │         │    status     │       │
│   │    total_amt │         │    unit_price│         │    shipped_at │       │
│   │    pay_status│         │    subtotal  │         │    created_at │       │
│   │    created_at│         └──────────────┘         └──────────────┘        │
│   └──────┬───────┘                                                           │
│          │                                                                    │
│          │                 ┌──────────────┐         ┌──────────────┐         │
│          │                 │   payments   │         │  refunds     │         │
│          │                 │──────────────│         │──────────────│         │
│          │                 │ PK payment_id│         │ PK refund_id │         │
│          └────────────────→│ FK order_id  │────────→│ FK payment_id│         │
│                            │    amount    │         │    amount    │         │
│                            │    channel   │         │    reason    │         │
│                            │    status    │         │    status    │         │
│                            └──────────────┘         └──────────────┘         │
│                                                                               │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐         │
│   │  promotions  │         │   coupons    │         │ coupon_usage │         │
│   │──────────────│         │──────────────│         │──────────────│         │
│   │ PK promo_id  │◄────────│ FK promo_id  │◄────────│ FK coupon_id │         │
│   │    type      │         │ PK coupon_id │         │ FK user_id   │         │
│   │    rules     │         │    code      │         │ FK order_id  │         │
│   │    discount  │         │    discount  │         │    used_at   │         │
│   │    start_end │         │    valid_period│       └──────────────┘         │
│   └──────────────┘         └──────────────┘                                  │
│                                                                               │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐         │
│   │ seckill_acts │         │  inventory   │         │ stock_       │         │
│   │──────────────│         │──────────────│         │ reservations │         │
│   │ PK act_id    │         │ PK sku_id    │         │──────────────│         │
│   │ FK product_id│◄────────│ FK product_id│         │ PK reserve_id│         │
│   │    price     │         │    quantity  │         │ FK sku_id    │         │
│   │    stock     │         │    locked_qty│         │ FK order_id  │         │
│   │    start_end │         │    warehouse_id│       │    quantity  │         │
│   └──────────────┘         └──────────────┘         │    status    │         │
│                                                     │    expires_at│         │
│                                                     └──────────────┘         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 数据库Schema创建

```sql
-- =============================================
-- 电商系统数据库Schema创建脚本
-- =============================================

-- 创建数据库
CREATE DATABASE ecommerce_dca
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';

\c ecommerce_dca;

-- 启用必要扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- =============================================
-- 1. 用户相关表
-- =============================================

-- 用户主表
CREATE TABLE users (
    user_id         BIGSERIAL PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE,
    email           VARCHAR(100) NOT NULL UNIQUE,
    phone           VARCHAR(20) UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    real_name       VARCHAR(50),
    id_card         VARCHAR(18),
    status          SMALLINT DEFAULT 1 CHECK (status IN (0, 1, 2)), -- 0:禁用 1:正常 2:待验证
    level           SMALLINT DEFAULT 1, -- 会员等级
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_login_at   TIMESTAMPTZ
);

COMMENT ON TABLE users IS '用户主表';
COMMENT ON COLUMN users.status IS '用户状态: 0=禁用, 1=正常, 2=待验证';

-- 用户地址表
CREATE TABLE user_addresses (
    address_id      BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    consignee       VARCHAR(50) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    province        VARCHAR(50) NOT NULL,
    city            VARCHAR(50) NOT NULL,
    district        VARCHAR(50) NOT NULL,
    detail_address  VARCHAR(255) NOT NULL,
    zip_code        VARCHAR(10),
    is_default      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_addr_user_id ON user_addresses(user_id);

-- =============================================
-- 2. 商品相关表
-- =============================================

-- 商品分类表
CREATE TABLE categories (
    category_id     SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    parent_id       INTEGER REFERENCES categories(category_id),
    level           SMALLINT DEFAULT 1,
    sort_order      INTEGER DEFAULT 0,
    is_show         BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 商品主表
CREATE TABLE products (
    product_id      BIGSERIAL PRIMARY KEY,
    sku             VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    category_id     INTEGER REFERENCES categories(category_id),
    brand           VARCHAR(100),
    base_price      DECIMAL(15,2) NOT NULL CHECK (base_price >= 0),
    sale_price      DECIMAL(15,2) NOT NULL CHECK (sale_price >= 0),
    cost_price      DECIMAL(15,2),
    stock_quantity  INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    sold_count      INTEGER DEFAULT 0,
    status          SMALLINT DEFAULT 0 CHECK (status IN (-1, 0, 1)), -- -1:下架 0:待上架 1:上架
    weight          DECIMAL(8,3), -- 单位:kg
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_product_category ON products(category_id);
CREATE INDEX idx_product_status ON products(status);
CREATE INDEX idx_product_price ON products(sale_price);

-- 商品SKU表 (多规格)
CREATE TABLE product_skus (
    sku_id          BIGSERIAL PRIMARY KEY,
    product_id      BIGINT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    sku_code        VARCHAR(50) NOT NULL UNIQUE,
    specs           JSONB NOT NULL, -- {"颜色": "红色", "尺码": "XL"}
    price           DECIMAL(15,2) NOT NULL,
    stock_quantity  INTEGER DEFAULT 0,
    barcode         VARCHAR(50),
    status          SMALLINT DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sku_product ON product_skus(product_id);

-- =============================================
-- 3. 库存相关表
-- =============================================

-- 库存主表 (与SKU一对一)
CREATE TABLE inventory (
    inventory_id    BIGSERIAL PRIMARY KEY,
    sku_id          BIGINT NOT NULL UNIQUE REFERENCES product_skus(sku_id),
    quantity        INTEGER DEFAULT 0 CHECK (quantity >= 0),
    locked_quantity INTEGER DEFAULT 0 CHECK (locked_quantity >= 0),
    available_qty   INTEGER GENERATED ALWAYS AS (quantity - locked_quantity) STORED,
    warehouse_id    INTEGER DEFAULT 1,
    warning_qty     INTEGER DEFAULT 10, -- 库存预警值
    version         INTEGER DEFAULT 0,  -- 乐观锁版本号
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inventory_available ON inventory(available_qty) WHERE available_qty > 0;

-- 库存操作日志表
CREATE TABLE inventory_logs (
    log_id          BIGSERIAL PRIMARY KEY,
    sku_id          BIGINT NOT NULL REFERENCES product_skus(sku_id),
    operation_type  VARCHAR(20) NOT NULL, -- IN:入库 OUT:出库 LOCK:锁定 UNLOCK:释放 ADJ:调整
    quantity        INTEGER NOT NULL,
    before_qty      INTEGER NOT NULL,
    after_qty       INTEGER NOT NULL,
    reference_type  VARCHAR(30), -- ORDER, REFUND, ADJUSTMENT
    reference_id    BIGINT,
    operator_id     BIGINT,
    remark          VARCHAR(255),
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inv_log_sku ON inventory_logs(sku_id, created_at DESC);
CREATE INDEX idx_inv_log_ref ON inventory_logs(reference_type, reference_id);

-- 库存预占表 (订单未支付时锁定库存)
CREATE TABLE stock_reservations (
    reservation_id  BIGSERIAL PRIMARY KEY,
    sku_id          BIGINT NOT NULL REFERENCES product_skus(sku_id),
    order_id        BIGINT NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    status          SMALLINT DEFAULT 1, -- 1:有效 2:已扣减 3:已释放
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stock_resv_sku ON stock_reservations(sku_id, status);
CREATE INDEX idx_stock_resv_order ON stock_reservations(order_id);
CREATE INDEX idx_stock_resv_expires ON stock_reservations(expires_at) WHERE status = 1;

-- =============================================
-- 4. 订单相关表
-- =============================================

-- 订单主表
CREATE TABLE orders (
    order_id        BIGSERIAL PRIMARY KEY,
    order_no        VARCHAR(32) NOT NULL UNIQUE,
    user_id         BIGINT NOT NULL REFERENCES users(user_id),
    order_status    SMALLINT DEFAULT 0, -- 0:待付款 1:已付款 2:已发货 3:已完成 4:已取消 5:退款中 6:已退款
    pay_status      SMALLINT DEFAULT 0, -- 0:未支付 1:部分支付 2:已支付
    ship_status     SMALLINT DEFAULT 0, -- 0:未发货 1:部分发货 2:已发货 3:已收货

    -- 金额信息
    goods_amount    DECIMAL(15,2) NOT NULL DEFAULT 0, -- 商品总金额
    discount_amount DECIMAL(15,2) DEFAULT 0, -- 优惠金额
    freight_amount  DECIMAL(15,2) DEFAULT 0, -- 运费
    tax_amount      DECIMAL(15,2) DEFAULT 0, -- 税费
    pay_amount      DECIMAL(15,2) NOT NULL DEFAULT 0, -- 应付金额
    paid_amount     DECIMAL(15,2) DEFAULT 0, -- 已付金额

    -- 收货信息
    consignee       VARCHAR(50),
    phone           VARCHAR(20),
    address         VARCHAR(500),

    -- 时间戳
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    paid_at         TIMESTAMPTZ,
    shipped_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    cancelled_at    TIMESTAMPTZ,

    -- 其他
    remark          VARCHAR(500),
    source          VARCHAR(20) DEFAULT 'web', -- 订单来源
    version         INTEGER DEFAULT 0
);

CREATE INDEX idx_order_user ON orders(user_id, created_at DESC);
CREATE INDEX idx_order_status ON orders(order_status);
CREATE INDEX idx_order_no ON orders(order_no);
CREATE INDEX idx_order_created ON orders(created_at DESC);

COMMENT ON TABLE orders IS '订单主表';
COMMENT ON COLUMN orders.order_status IS '订单状态: 0=待付款 1=已付款 2=已发货 3=已完成 4=已取消 5=退款中 6=已退款';

-- 订单商品明细表
CREATE TABLE order_items (
    item_id         BIGSERIAL PRIMARY KEY,
    order_id        BIGINT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id      BIGINT NOT NULL REFERENCES products(product_id),
    sku_id          BIGINT NOT NULL REFERENCES product_skus(sku_id),
    product_name    VARCHAR(255) NOT NULL,
    sku_specs       JSONB, -- 规格信息快照
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    unit_price      DECIMAL(15,2) NOT NULL,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    subtotal        DECIMAL(15,2) NOT NULL, -- (unit_price * quantity) - discount

    -- 售后信息
    refund_status   SMALLINT DEFAULT 0, -- 0:无 1:申请中 2:已退款
    refund_qty      INTEGER DEFAULT 0,
    refund_amount   DECIMAL(15,2) DEFAULT 0
);

CREATE INDEX idx_item_order ON order_items(order_id);
CREATE INDEX idx_item_product ON order_items(product_id);

-- 订单状态变更日志
CREATE TABLE order_status_logs (
    log_id          BIGSERIAL PRIMARY KEY,
    order_id        BIGINT NOT NULL REFERENCES orders(order_id),
    from_status     SMALLINT,
    to_status       SMALLINT NOT NULL,
    operator_type   VARCHAR(20), -- SYSTEM, USER, ADMIN
    operator_id     BIGINT,
    remark          VARCHAR(255),
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_status_log_order ON order_status_logs(order_id, created_at DESC);

-- =============================================
-- 5. 支付相关表
-- =============================================

-- 支付记录表
CREATE TABLE payments (
    payment_id      BIGSERIAL PRIMARY KEY,
    payment_no      VARCHAR(32) NOT NULL UNIQUE,
    order_id        BIGINT NOT NULL REFERENCES orders(order_id),
    user_id         BIGINT NOT NULL REFERENCES users(user_id),

    amount          DECIMAL(15,2) NOT NULL,
    channel         VARCHAR(20) NOT NULL, -- alipay, wechat, unionpay
    channel_trans_id VARCHAR(64), -- 第三方支付流水号

    status          SMALLINT DEFAULT 0, -- 0:待支付 1:支付中 2:成功 3:失败 4:关闭
    paid_at         TIMESTAMPTZ,

    request_params  JSONB, -- 支付请求参数
    response_data   JSONB, -- 支付响应数据
    notify_data     JSONB, -- 异步通知数据

    client_ip       INET,
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    expired_at      TIMESTAMPTZ
);

CREATE INDEX idx_payment_order ON payments(order_id);
CREATE INDEX idx_payment_user ON payments(user_id);
CREATE INDEX idx_payment_no ON payments(payment_no);
CREATE INDEX idx_payment_status ON payments(status);

-- 退款记录表
CREATE TABLE refunds (
    refund_id       BIGSERIAL PRIMARY KEY,
    refund_no       VARCHAR(32) NOT NULL UNIQUE,
    payment_id      BIGINT NOT NULL REFERENCES payments(payment_id),
    order_id        BIGINT NOT NULL REFERENCES orders(order_id),
    item_id         BIGINT REFERENCES order_items(item_id), -- 单品退款时填写

    refund_type     SMALLINT DEFAULT 1, -- 1:全额退款 2:部分退款
    amount          DECIMAL(15,2) NOT NULL,
    reason          VARCHAR(255),

    status          SMALLINT DEFAULT 0, -- 0:申请中 1:审核通过 2:审核拒绝 3:退款中 4:成功 5:失败
    channel_trans_id VARCHAR(64),

    applied_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    approved_at     TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,

    applicant_id    BIGINT,
    approver_id     BIGINT,
    remark          VARCHAR(255)
);

CREATE INDEX idx_refund_order ON refunds(order_id);
CREATE INDEX idx_refund_payment ON refunds(payment_id);

-- =============================================
-- 6. 促销相关表
-- =============================================

-- 促销活动表
CREATE TABLE promotions (
    promo_id        SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    promo_type      VARCHAR(20) NOT NULL, -- COUPON:优惠券 SECKILL:秒杀 FLASH:限时购

    -- 时间范围
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ NOT NULL,

    -- 规则配置 (JSON格式存储灵活配置)
    rules           JSONB NOT NULL,
    /* 示例:
    {
        "condition": {"min_amount": 100, "min_quantity": 1},
        "action": {"type": "discount", "value": 0.8}, -- 8折
        "scope": {"product_ids": [1,2,3], "category_ids": [1]}
    }
    */

    status          SMALLINT DEFAULT 0, -- 0:未开始 1:进行中 2:已结束 3:已停用
    total_quota     INTEGER, -- 总配额
    used_quota      INTEGER DEFAULT 0,

    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT
);

CREATE INDEX idx_promo_time ON promotions(start_time, end_time);
CREATE INDEX idx_promo_status ON promotions(status);

-- 优惠券表
CREATE TABLE coupons (
    coupon_id       BIGSERIAL PRIMARY KEY,
    promo_id        INTEGER REFERENCES promotions(promo_id),

    code            VARCHAR(32) NOT NULL UNIQUE,
    coupon_type     VARCHAR(20), -- FULL_REDUCTION:满减 DISCOUNT:折扣 DIRECT:直减

    -- 面额配置
    face_value      DECIMAL(15,2) NOT NULL,
    min_order_amount DECIMAL(15,2) DEFAULT 0, -- 最低使用门槛

    -- 有效期
    valid_start     TIMESTAMPTZ,
    valid_end       TIMESTAMPTZ,
    valid_days      INTEGER, -- 领取后X天内有效

    -- 范围限制
    applicable_type VARCHAR(20) DEFAULT 'all', -- all, category, product
    applicable_ids  INTEGER[], -- 适用商品/类目ID列表

    -- 发放限制
    total_quantity  INTEGER,
    issued_quantity INTEGER DEFAULT 0,
    per_user_limit  INTEGER DEFAULT 1,

    status          SMALLINT DEFAULT 1 -- 1:有效 0:无效
);

-- 用户优惠券记录
CREATE TABLE user_coupons (
    uc_id           BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(user_id),
    coupon_id       BIGINT NOT NULL REFERENCES coupons(coupon_id),

    status          SMALLINT DEFAULT 0, -- 0:未使用 1:已使用 2:已过期 3:已作废
    acquired_at     TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    used_at         TIMESTAMPTZ,
    order_id        BIGINT,
    valid_start     TIMESTAMPTZ,
    valid_end       TIMESTAMPTZ
);

CREATE INDEX idx_uc_user ON user_coupons(user_id, status);
CREATE INDEX idx_uc_coupon ON user_coupons(coupon_id);

-- 秒杀活动表
CREATE TABLE seckill_activities (
    act_id          SERIAL PRIMARY KEY,
    promo_id        INTEGER REFERENCES promotions(promo_id),

    act_name        VARCHAR(100) NOT NULL,
    sku_id          BIGINT NOT NULL REFERENCES product_skus(sku_id),

    seckill_price   DECIMAL(15,2) NOT NULL,
    original_price  DECIMAL(15,2) NOT NULL,
    stock_quantity  INTEGER NOT NULL,
    sold_quantity   INTEGER DEFAULT 0,

    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ NOT NULL,

    status          SMALLINT DEFAULT 0,
    limit_per_user  INTEGER DEFAULT 1, -- 每人限购

    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_seckill_time ON seckill_activities(start_time, end_time);
CREATE INDEX idx_seckill_status ON seckill_activities(status);

-- 秒杀订单记录 (用于限流和统计)
CREATE TABLE seckill_orders (
    so_id           BIGSERIAL PRIMARY KEY,
    act_id          INTEGER NOT NULL REFERENCES seckill_activities(act_id),
    user_id         BIGINT NOT NULL REFERENCES users(user_id),
    order_id        BIGINT REFERENCES orders(order_id),

    status          SMALLINT DEFAULT 1, -- 1:排队中 2:成功 3:失败
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_seckill_user_act ON seckill_orders(act_id, user_id);

-- =============================================
-- 7. 系统配置和日志表
-- =============================================

-- 系统配置表
CREATE TABLE system_configs (
    config_key      VARCHAR(50) PRIMARY KEY,
    config_value    TEXT NOT NULL,
    description     VARCHAR(255),
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 审计日志表
CREATE TABLE audit_logs (
    log_id          BIGSERIAL PRIMARY KEY,
    table_name      VARCHAR(50) NOT NULL,
    record_id       BIGINT NOT NULL,
    operation       VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_data        JSONB,
    new_data        JSONB,
    operator_type   VARCHAR(20),
    operator_id     BIGINT,
    ip_address      INET,
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- 创建审计日志分区
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE audit_logs_2024_02 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- 更多分区按需创建...

CREATE INDEX idx_audit_table ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_time ON audit_logs(created_at DESC);

-- 初始化配置数据
INSERT INTO system_configs (config_key, config_value, description) VALUES
('order.expire.minutes', '30', '订单自动取消时间(分钟)'),
('stock.reserve.minutes', '15', '库存预占超时时间(分钟)'),
('seckill.rate.limit', '1000', '秒杀每秒限流数量'),
('freight.free.threshold', '99.00', '免运费门槛金额'),
('freight.base.amount', '10.00', '基础运费金额');
```

---

## 4. 订单系统实现

### 4.1 订单状态机

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            订单状态流转图                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────┐                                                               │
│   │   创建    │                                                               │
│   │  CREATED │                                                               │
│   └────┬─────┘                                                               │
│        │ sp_create_order                                                      │
│        ▼                                                                      │
│   ┌──────────┐     超时自动取消      ┌──────────┐                            │
│   │ 待付款   │──────────────────────→│  已取消   │                            │
│   │PENDING  │   trg_order_timeout   │CANCELLED │                            │
│   └────┬─────┘                       └──────────┘                            │
│        │ sp_pay_order                                                        │
│        ▼                                                                      │
│   ┌──────────┐     支付失败        ┌──────────┐                              │
│   │ 已付款   │────────────────────→│  已取消   │                              │
│   │  PAID   │                      │CANCELLED │                              │
│   └────┬─────┘                       └──────────┘                            │
│        │ sp_ship_order                                                       │
│        ▼                                                                      │
│   ┌──────────┐                                                              │
│   │ 已发货   │     ┌──────────┐                                              │
│   │SHIPPED  │────→│ 退款申请  │────→ 退款完成                                │
│   └────┬─────┘     │REFUNDING │     REFUNDED                                 │
│        │           └──────────┘                                              │
│        │ sp_confirm_receive                                                   │
│        ▼                                                                      │
│   ┌──────────┐     自动确认收货                                               │
│   │ 已完成   │←─────(7天后)                                                    │
│   │COMPLETED│                                                               │
│   └──────────┘                                                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 核心存储过程

#### 4.2.1 创建订单存储过程

```sql
-- =============================================
-- 存储过程1: 创建订单
-- 功能: 创建新订单，校验库存，计算价格，预占库存
-- =============================================
CREATE OR REPLACE FUNCTION sp_create_order(
    p_user_id           BIGINT,
    p_items             JSONB,        -- [{"sku_id": 1, "quantity": 2}, ...]
    p_address_id        BIGINT,
    p_coupon_id         BIGINT DEFAULT NULL,
    p_remark            VARCHAR(500) DEFAULT NULL,
    p_source            VARCHAR(20) DEFAULT 'web'
) RETURNS TABLE (
    order_id            BIGINT,
    order_no            VARCHAR(32),
    pay_amount          DECIMAL(15,2),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_order_id          BIGINT;
    v_order_no          VARCHAR(32);
    v_goods_amount      DECIMAL(15,2) := 0;
    v_discount_amount   DECIMAL(15,2) := 0;
    v_freight_amount    DECIMAL(15,2) := 0;
    v_pay_amount        DECIMAL(15,2) := 0;
    v_item              JSONB;
    v_sku_id            BIGINT;
    v_quantity          INTEGER;
    v_sku_price         DECIMAL(15,2);
    v_sku_stock         INTEGER;
    v_product_id        BIGINT;
    v_product_name      VARCHAR(255);
    v_sku_specs         JSONB;
    v_item_subtotal     DECIMAL(15,2);
    v_address           RECORD;
    v_coupon_discount   DECIMAL(15,2) := 0;
    v_free_threshold    DECIMAL(15,2);
    v_base_freight      DECIMAL(15,2);
    v_expire_minutes    INTEGER;
    v_reserve_id        BIGINT;
BEGIN
    -- 生成订单号: 年月日时分秒 + 6位随机数
    v_order_no := TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') ||
                  LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');

    -- 获取系统配置
    SELECT config_value::DECIMAL INTO v_free_threshold
    FROM system_configs WHERE config_key = 'freight.free.threshold';
    SELECT config_value::DECIMAL INTO v_base_freight
    FROM system_configs WHERE config_key = 'freight.base.amount';
    SELECT config_value::INTEGER INTO v_expire_minutes
    FROM system_configs WHERE config_key = 'order.expire.minutes';

    -- 获取收货地址
    SELECT * INTO v_address FROM user_addresses
    WHERE address_id = p_address_id AND user_id = p_user_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, NULL::DECIMAL,
                            -1, '收货地址不存在'::VARCHAR;
        RETURN;
    END IF;

    -- 开启事务
    BEGIN
        -- 1. 校验库存并计算商品金额
        FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
        LOOP
            v_sku_id := (v_item->>'sku_id')::BIGINT;
            v_quantity := (v_item->>'quantity')::INTEGER;

            -- 校验SKU
            SELECT s.sku_id, s.product_id, s.price, s.specs, s.stock_quantity,
                   p.name INTO v_sku_id, v_product_id, v_sku_price, v_sku_specs,
                   v_sku_stock, v_product_name
            FROM product_skus s
            JOIN products p ON s.product_id = p.product_id
            WHERE s.sku_id = v_sku_id AND s.status = 1
            FOR UPDATE; -- 锁定SKU行

            IF NOT FOUND THEN
                RAISE EXCEPTION '商品SKU不存在或已下架: %', v_sku_id;
            END IF;

            -- 检查库存
            IF v_sku_stock < v_quantity THEN
                RAISE EXCEPTION '商品库存不足: %, 需要: %, 可用: %',
                    v_product_name, v_quantity, v_sku_stock;
            END IF;

            v_item_subtotal := v_sku_price * v_quantity;
            v_goods_amount := v_goods_amount + v_item_subtotal;
        END LOOP;

        -- 2. 计算运费
        IF v_goods_amount < v_free_threshold THEN
            v_freight_amount := v_base_freight;
        END IF;

        -- 3. 计算优惠券优惠
        IF p_coupon_id IS NOT NULL THEN
            SELECT discount_amount INTO v_coupon_discount
            FROM fn_calc_coupon_discount(p_user_id, p_coupon_id, v_goods_amount);
            v_discount_amount := v_coupon_discount;
        END IF;

        -- 4. 计算应付金额
        v_pay_amount := v_goods_amount + v_freight_amount - v_discount_amount;
        IF v_pay_amount < 0 THEN
            v_pay_amount := 0;
        END IF;

        -- 5. 创建订单主表
        INSERT INTO orders (
            order_no, user_id, order_status, pay_status, ship_status,
            goods_amount, discount_amount, freight_amount, pay_amount,
            consignee, phone, address, remark, source, expired_at
        ) VALUES (
            v_order_no, p_user_id, 0, 0, 0,
            v_goods_amount, v_discount_amount, v_freight_amount, v_pay_amount,
            v_address.consignee, v_address.phone,
            v_address.province || v_address.city || v_address.district || v_address.detail_address,
            p_remark, p_source, CURRENT_TIMESTAMP + (v_expire_minutes || ' minutes')::INTERVAL
        ) RETURNING orders.order_id INTO v_order_id;

        -- 6. 创建订单明细
        FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
        LOOP
            v_sku_id := (v_item->>'sku_id')::BIGINT;
            v_quantity := (v_item->>'quantity')::INTEGER;

            SELECT s.product_id, s.price, s.specs, p.name
            INTO v_product_id, v_sku_price, v_sku_specs, v_product_name
            FROM product_skus s
            JOIN products p ON s.product_id = p.product_id
            WHERE s.sku_id = v_sku_id;

            v_item_subtotal := v_sku_price * v_quantity;

            INSERT INTO order_items (
                order_id, product_id, sku_id, product_name, sku_specs,
                quantity, unit_price, subtotal
            ) VALUES (
                v_order_id, v_product_id, v_sku_id, v_product_name, v_sku_specs,
                v_quantity, v_sku_price, v_item_subtotal
            );

            -- 7. 预占库存
            INSERT INTO stock_reservations (
                sku_id, order_id, quantity, expires_at
            ) VALUES (
                v_sku_id, v_order_id, v_quantity,
                CURRENT_TIMESTAMP + (v_expire_minutes || ' minutes')::INTERVAL
            ) RETURNING reservation_id INTO v_reserve_id;

            -- 更新库存锁定数
            UPDATE inventory
            SET locked_quantity = locked_quantity + v_quantity,
                version = version + 1
            WHERE sku_id = v_sku_id;
        END LOOP;

        -- 8. 锁定优惠券
        IF p_coupon_id IS NOT NULL THEN
            UPDATE user_coupons
            SET status = 1, used_at = CURRENT_TIMESTAMP, order_id = v_order_id
            WHERE uc_id = p_coupon_id AND user_id = p_user_id AND status = 0;
        END IF;

        -- 9. 记录订单状态变更
        INSERT INTO order_status_logs (order_id, from_status, to_status,
                                       operator_type, remark)
        VALUES (v_order_id, NULL, 0, 'SYSTEM', '订单创建成功');

        -- 返回结果
        RETURN QUERY SELECT v_order_id, v_order_no, v_pay_amount,
                            0, '订单创建成功'::VARCHAR;

    EXCEPTION WHEN OTHERS THEN
        RAISE WARNING '创建订单失败: %', SQLERRM;
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, NULL::DECIMAL,
                            -1, SQLERRM::VARCHAR;
    END;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_create_order IS '创建订单主存储过程';
```

#### 4.2.2 取消订单存储过程

```sql
-- =============================================
-- 存储过程2: 取消订单
-- 功能: 取消待付款订单，释放库存和优惠券
-- =============================================
CREATE OR REPLACE FUNCTION sp_cancel_order(
    p_order_id      BIGINT,
    p_user_id       BIGINT,
    p_reason        VARCHAR(255) DEFAULT '用户取消',
    p_operator_type VARCHAR(20) DEFAULT 'USER'
) RETURNS TABLE (
    result_code     INTEGER,
    result_msg      VARCHAR(255)
) AS $$
DECLARE
    v_order         RECORD;
    v_item          RECORD;
    v_uc_id         BIGINT;
BEGIN
    -- 获取订单信息并锁定
    SELECT * INTO v_order FROM orders
    WHERE order_id = p_order_id FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT -1, '订单不存在'::VARCHAR;
        RETURN;
    END IF;

    -- 权限检查
    IF p_operator_type = 'USER' AND v_order.user_id != p_user_id THEN
        RETURN QUERY SELECT -2, '无权操作此订单'::VARCHAR;
        RETURN;
    END IF;

    -- 状态检查: 只能取消待付款订单
    IF v_order.order_status != 0 THEN
        RETURN QUERY SELECT -3, '订单状态不允许取消'::VARCHAR;
        RETURN;
    END IF;

    BEGIN
        -- 1. 更新订单状态
        UPDATE orders SET
            order_status = 4,
            cancelled_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE order_id = p_order_id;

        -- 2. 释放库存预占
        FOR v_item IN
            SELECT * FROM stock_reservations
            WHERE order_id = p_order_id AND status = 1
        LOOP
            -- 更新库存锁定数
            UPDATE inventory
            SET locked_quantity = locked_quantity - v_item.quantity,
                version = version + 1
            WHERE sku_id = v_item.sku_id;

            -- 记录库存日志
            INSERT INTO inventory_logs (
                sku_id, operation_type, quantity,
                before_qty, after_qty, reference_type, reference_id, remark
            )
            SELECT
                v_item.sku_id, 'UNLOCK', v_item.quantity,
                i.locked_quantity + v_item.quantity, i.locked_quantity,
                'ORDER_CANCEL', p_order_id, '订单取消释放库存'
            FROM inventory i WHERE i.sku_id = v_item.sku_id;
        END LOOP;

        -- 3. 标记预占记录为已释放
        UPDATE stock_reservations
        SET status = 3 WHERE order_id = p_order_id AND status = 1;

        -- 4. 返还优惠券
        SELECT uc_id INTO v_uc_id FROM user_coupons
        WHERE order_id = p_order_id AND status = 1;

        IF FOUND THEN
            UPDATE user_coupons
            SET status = 0, used_at = NULL, order_id = NULL
            WHERE uc_id = v_uc_id;
        END IF;

        -- 5. 记录状态变更日志
        INSERT INTO order_status_logs (
            order_id, from_status, to_status,
            operator_type, operator_id, remark
        ) VALUES (
            p_order_id, v_order.order_status, 4,
            p_operator_type, p_user_id, p_reason
        );

        RETURN QUERY SELECT 0, '订单取消成功'::VARCHAR;

    EXCEPTION WHEN OTHERS THEN
        RAISE WARNING '取消订单失败: %', SQLERRM;
        RETURN QUERY SELECT -99, SQLERRM::VARCHAR;
    END;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_cancel_order IS '取消订单存储过程';
```

#### 4.2.3 确认收货存储过程

```sql
-- =============================================
-- 存储过程3: 确认收货
-- =============================================
CREATE OR REPLACE FUNCTION sp_confirm_receive(
    p_order_id      BIGINT,
    p_user_id       BIGINT
) RETURNS TABLE (
    result_code     INTEGER,
    result_msg      VARCHAR(255)
) AS $$
DECLARE
    v_order         RECORD;
BEGIN
    SELECT * INTO v_order FROM orders
    WHERE order_id = p_order_id FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT -1, '订单不存在'::VARCHAR;
        RETURN;
    END IF;

    IF v_order.user_id != p_user_id THEN
        RETURN QUERY SELECT -2, '无权操作此订单'::VARCHAR;
        RETURN;
    END IF;

    IF v_order.order_status != 2 THEN
        RETURN QUERY SELECT -3, '订单未发货'::VARCHAR;
        RETURN;
    END IF;

    UPDATE orders SET
        order_status = 3,
        ship_status = 3,
        completed_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE order_id = p_order_id;

    INSERT INTO order_status_logs (order_id, from_status, to_status,
                                   operator_type, operator_id, remark)
    VALUES (p_order_id, 2, 3, 'USER', p_user_id, '用户确认收货');

    RETURN QUERY SELECT 0, '确认收货成功'::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

#### 4.2.4 订单查询存储过程

```sql
-- =============================================
-- 存储过程4: 查询订单详情
-- =============================================
CREATE OR REPLACE FUNCTION sp_get_order_detail(
    p_order_id      BIGINT
) RETURNS TABLE (
    order_id        BIGINT,
    order_no        VARCHAR(32),
    order_status    SMALLINT,
    pay_status      SMALLINT,
    ship_status     SMALLINT,
    goods_amount    DECIMAL(15,2),
    discount_amount DECIMAL(15,2),
    freight_amount  DECIMAL(15,2),
    pay_amount      DECIMAL(15,2),
    consignee       VARCHAR(50),
    phone           VARCHAR(20),
    address         VARCHAR(500),
    remark          VARCHAR(500),
    created_at      TIMESTAMPTZ,
    items           JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.order_id, o.order_no, o.order_status, o.pay_status, o.ship_status,
        o.goods_amount, o.discount_amount, o.freight_amount, o.pay_amount,
        o.consignee, o.phone, o.address, o.remark, o.created_at,
        (
            SELECT jsonb_agg(jsonb_build_object(
                'item_id', oi.item_id,
                'product_name', oi.product_name,
                'sku_specs', oi.sku_specs,
                'quantity', oi.quantity,
                'unit_price', oi.unit_price,
                'subtotal', oi.subtotal,
                'refund_status', oi.refund_status
            ))
            FROM order_items oi WHERE oi.order_id = o.order_id
        ) AS items
    FROM orders o
    WHERE o.order_id = p_order_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 存储过程5: 查询用户订单列表
-- =============================================
CREATE OR REPLACE FUNCTION sp_get_user_orders(
    p_user_id       BIGINT,
    p_status        SMALLINT DEFAULT NULL,
    p_page          INTEGER DEFAULT 1,
    p_page_size     INTEGER DEFAULT 20
) RETURNS TABLE (
    order_id        BIGINT,
    order_no        VARCHAR(32),
    order_status    SMALLINT,
    pay_amount      DECIMAL(15,2),
    item_count      BIGINT,
    main_image      VARCHAR(255),
    created_at      TIMESTAMPTZ,
    total_count     BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH filtered_orders AS (
        SELECT o.order_id, o.order_no, o.order_status, o.pay_amount, o.created_at
        FROM orders o
        WHERE o.user_id = p_user_id
          AND (p_status IS NULL OR o.order_status = p_status)
    ),
    order_items_agg AS (
        SELECT
            oi.order_id,
            COUNT(*) AS cnt,
            (SELECT pi.image_url FROM product_images pi
             WHERE pi.product_id = oi.product_id LIMIT 1) AS img
        FROM order_items oi
        GROUP BY oi.order_id
    ),
    total AS (
        SELECT COUNT(*) AS cnt FROM filtered_orders
    )
    SELECT
        fo.order_id, fo.order_no, fo.order_status, fo.pay_amount,
        COALESCE(oia.cnt, 0),
        oia.img,
        fo.created_at,
        (SELECT cnt FROM total)
    FROM filtered_orders fo
    LEFT JOIN order_items_agg oia ON fo.order_id = oia.order_id
    ORDER BY fo.created_at DESC
    LIMIT p_page_size OFFSET (p_page - 1) * p_page_size;
END;
$$ LANGUAGE plpgsql;
```

### 4.3 订单相关触发器

```sql
-- =============================================
-- 触发器1: 订单自动取消定时任务
-- =============================================
CREATE OR REPLACE FUNCTION trg_fn_order_auto_cancel()
RETURNS TRIGGER AS $$
BEGIN
    -- 检查是否有超时未支付订单
    PERFORM sp_cancel_order(
        order_id,
        user_id,
        '订单超时自动取消',
        'SYSTEM'
    )
    FROM orders
    WHERE order_status = 0
      AND expired_at < CURRENT_TIMESTAMP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 创建定时触发器 (每分钟执行)
-- 注意: 实际生产环境建议使用 pg_cron 或外部调度
-- SELECT cron.schedule('order-auto-cancel', '* * * * *',
--     'SELECT sp_process_timeout_orders()');

-- =============================================
-- 触发器2: 订单状态变更审计
-- =============================================
CREATE OR REPLACE FUNCTION trg_fn_order_audit()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        table_name, record_id, operation,
        old_data, new_data, operator_type
    ) VALUES (
        'orders', NEW.order_id, TG_OP,
        to_jsonb(OLD), to_jsonb(NEW), 'SYSTEM'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_audit
    AFTER UPDATE ON orders
    FOR EACH ROW
    WHEN (OLD.order_status IS DISTINCT FROM NEW.order_status)
    EXECUTE FUNCTION trg_fn_order_audit();

-- =============================================
-- 触发器3: 订单统计更新
-- =============================================
CREATE OR REPLACE FUNCTION trg_fn_order_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- 订单完成时更新商品销量
    IF NEW.order_status = 3 AND OLD.order_status != 3 THEN
        UPDATE products p
        SET sold_count = p.sold_count + oi.quantity
        FROM order_items oi
        WHERE oi.order_id = NEW.order_id
          AND p.product_id = oi.product_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_stats
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_order_stats();
```

---

## 5. 库存系统实现

### 5.1 库存核心模型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          库存管理核心模型                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐           ┌──────────────┐           ┌──────────────┐   │
│   │  可用库存    │           │  锁定库存    │           │  在途库存    │   │
│   │ available_qty│           │locked_quantity│           │ transit_qty  │   │
│   │              │           │              │           │              │   │
│   │ = quantity   │           │ 订单预占      │           │ 采购在途      │   │
│   │   - locked   │           │ 支付锁定      │           │ 调拨在途      │   │
│   └──────────────┘           └──────────────┘           └──────────────┘   │
│                                                                             │
│   库存操作类型:                                                              │
│   ┌──────────┬──────────┬────────────────────────────────────────────────┐ │
│   │ 类型     │ 代码     │ 说明                                           │ │
│   ├──────────┼──────────┼────────────────────────────────────────────────┤ │
│   │ 入库     │ IN       │ 采购入库、退货入库、调拨入库                    │ │
│   │ 出库     │ OUT      │ 销售出库、调拨出库、损耗出库                    │ │
│   │ 锁定     │ LOCK     │ 订单预占库存                                    │ │
│   │ 释放     │ UNLOCK   │ 取消订单释放库存                                │ │
│   │ 扣减     │ DEDUCT   │ 支付成功扣减库存                                │ │
│   │ 返还     │ RETURN   │ 退款返还库存                                    │ │
│   │ 盘点调整 │ ADJUST   │ 库存盘点调整                                    │ │
│   └──────────┴──────────┴────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 库存核心存储过程

#### 5.2.1 库存扣减存储过程

```sql
-- =============================================
-- 存储过程6: 库存扣减 (支付成功后调用)
-- =============================================
CREATE OR REPLACE FUNCTION sp_deduct_inventory(
    p_order_id      BIGINT,
    p_operator_id   BIGINT DEFAULT NULL
) RETURNS TABLE (
    result_code     INTEGER,
    result_msg      VARCHAR(255)
) AS $$
DECLARE
    v_item          RECORD;
    v_inv           RECORD;
BEGIN
    -- 遍历订单所有商品
    FOR v_item IN
        SELECT oi.* FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE oi.order_id = p_order_id AND o.order_status = 1
        FOR UPDATE OF oi
    LOOP
        -- 获取库存并锁定
        SELECT * INTO v_inv FROM inventory
        WHERE sku_id = v_item.sku_id FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION '库存记录不存在: SKU=%', v_item.sku_id;
        END IF;

        -- 校验可用库存
        IF v_inv.available_qty < v_item.quantity THEN
            RAISE EXCEPTION '库存不足: SKU=%, 需要=%, 可用=%',
                v_item.sku_id, v_item.quantity, v_inv.available_qty;
        END IF;

        -- 更新库存: 减少实际库存和锁定库存
        UPDATE inventory SET
            quantity = quantity - v_item.quantity,
            locked_quantity = locked_quantity - v_item.quantity,
            version = version + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE sku_id = v_item.sku_id;

        -- 记录库存日志
        INSERT INTO inventory_logs (
            sku_id, operation_type, quantity,
            before_qty, after_qty, reference_type, reference_id, operator_id, remark
        ) VALUES (
            v_item.sku_id, 'DEDUCT', v_item.quantity,
            v_inv.quantity, v_inv.quantity - v_item.quantity,
            'ORDER_PAY', p_order_id, p_operator_id, '订单支付扣减库存'
        );

        -- 更新SKU库存
        UPDATE product_skus
        SET stock_quantity = stock_quantity - v_item.quantity
        WHERE sku_id = v_item.sku_id;

        -- 更新预占状态
        UPDATE stock_reservations
        SET status = 2
        WHERE order_id = p_order_id
          AND sku_id = v_item.sku_id
          AND status = 1;
    END LOOP;

    RETURN QUERY SELECT 0, '库存扣减成功'::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT -1, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_deduct_inventory IS '订单支付成功后扣减库存';
```

#### 5.2.2 库存入库存储过程

```sql
-- =============================================
-- 存储过程7: 库存入库
-- =============================================
CREATE OR REPLACE FUNCTION sp_stock_in(
    p_sku_id        BIGINT,
    p_quantity      INTEGER,
    p_operation_type VARCHAR(20), -- PURCHASE, RETURN, TRANSFER_IN, ADJUST
    p_reference_no  VARCHAR(64) DEFAULT NULL,
    p_warehouse_id  INTEGER DEFAULT 1,
    p_operator_id   BIGINT DEFAULT NULL,
    p_remark        VARCHAR(255) DEFAULT NULL
) RETURNS TABLE (
    result_code     INTEGER,
    result_msg      VARCHAR(255)
) AS $$
DECLARE
    v_inv           RECORD;
    v_before_qty    INTEGER;
BEGIN
    IF p_quantity <= 0 THEN
        RETURN QUERY SELECT -1, '入库数量必须大于0'::VARCHAR;
        RETURN;
    END IF;

    -- 锁定库存记录
    SELECT * INTO v_inv FROM inventory
    WHERE sku_id = p_sku_id FOR UPDATE;

    IF NOT FOUND THEN
        -- 创建新库存记录
        INSERT INTO inventory (sku_id, quantity, warehouse_id)
        VALUES (p_sku_id, p_quantity, p_warehouse_id)
        RETURNING * INTO v_inv;
        v_before_qty := 0;
    ELSE
        v_before_qty := v_inv.quantity;
        -- 更新库存
        UPDATE inventory SET
            quantity = quantity + p_quantity,
            version = version + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE sku_id = p_sku_id;
    END IF;

    -- 记录日志
    INSERT INTO inventory_logs (
        sku_id, operation_type, quantity,
        before_qty, after_qty, reference_type, reference_id, operator_id, remark
    ) VALUES (
        p_sku_id, 'IN', p_quantity,
        v_before_qty, v_before_qty + p_quantity,
        p_operation_type, p_reference_no, p_operator_id, p_remark
    );

    -- 更新SKU总库存
    UPDATE product_skus
    SET stock_quantity = stock_quantity + p_quantity
    WHERE sku_id = p_sku_id;

    RETURN QUERY SELECT 0, '入库成功'::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

#### 5.2.3 库存释放存储过程

```sql
-- =============================================
-- 存储过程8: 批量释放过期库存预占
-- =============================================
CREATE OR REPLACE FUNCTION sp_release_expired_reservations()
RETURNS TABLE (
    released_count  INTEGER,
    result_msg      VARCHAR(255)
) AS $$
DECLARE
    v_count         INTEGER := 0;
    v_item          RECORD;
BEGIN
    FOR v_item IN
        SELECT * FROM stock_reservations
        WHERE status = 1 AND expires_at < CURRENT_TIMESTAMP
        FOR UPDATE
    LOOP
        -- 更新库存锁定数
        UPDATE inventory
        SET locked_quantity = GREATEST(0, locked_quantity - v_item.quantity),
            version = version + 1
        WHERE sku_id = v_item.sku_id;

        -- 标记预占记录
        UPDATE stock_reservations
        SET status = 3
        WHERE reservation_id = v_item.reservation_id;

        -- 记录日志
        INSERT INTO inventory_logs (
            sku_id, operation_type, quantity,
            before_qty, after_qty, reference_type, reference_id, remark
        )
        SELECT
            v_item.sku_id, 'UNLOCK', v_item.quantity,
            i.locked_quantity + v_item.quantity, i.locked_quantity,
            'EXPIRE_RELEASE', v_item.order_id, '预占超时释放'
        FROM inventory i WHERE i.sku_id = v_item.sku_id;

        v_count := v_count + 1;
    END LOOP;

    RETURN QUERY SELECT v_count,
        format('已释放 %s 条过期预占记录', v_count)::VARCHAR;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_release_expired_reservations IS '释放过期库存预占';
```

#### 5.2.4 库存盘点存储过程

```sql
-- =============================================
-- 存储过程9: 库存盘点调整
-- =============================================
CREATE OR REPLACE FUNCTION sp_adjust_inventory(
    p_sku_id        BIGINT,
    p_real_qty      INTEGER, -- 实盘数量
    p_operator_id   BIGINT,
    p_reason        VARCHAR(255)
) RETURNS TABLE (
    result_code     INTEGER,
    result_msg      VARCHAR(255),
    diff_qty        INTEGER
) AS $$
DECLARE
    v_inv           RECORD;
    v_diff          INTEGER;
    v_sys_qty       INTEGER;
BEGIN
    SELECT * INTO v_inv FROM inventory WHERE sku_id = p_sku_id FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT -1, '库存记录不存在'::VARCHAR, 0::INTEGER;
        RETURN;
    END IF;

    v_sys_qty := v_inv.quantity;
    v_diff := p_real_qty - v_sys_qty;

    IF v_diff = 0 THEN
        RETURN QUERY SELECT 0, '盘点无差异'::VARCHAR, 0::INTEGER;
        RETURN;
    END IF;

    -- 更新库存
    UPDATE inventory SET
        quantity = p_real_qty,
        version = version + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE sku_id = p_sku_id;

    -- 记录调整日志
    INSERT INTO inventory_logs (
        sku_id, operation_type, quantity,
        before_qty, after_qty, reference_type, operator_id, remark
    ) VALUES (
        p_sku_id, 'ADJUST', ABS(v_diff),
        v_sys_qty, p_real_qty,
        'INVENTORY_CHECK', p_operator_id,
        format('盘点调整: %s (差异: %s)', p_reason, v_diff)
    );

    -- 同步SKU库存
    UPDATE product_skus
    SET stock_quantity = p_real_qty - v_inv.locked_quantity
    WHERE sku_id = p_sku_id;

    RETURN QUERY SELECT 0, '盘点调整完成'::VARCHAR, v_diff;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT -99, SQLERRM::VARCHAR, 0::INTEGER;
END;
$$ LANGUAGE plpgsql;
```

#### 5.2.5 库存查询存储过程

```sql
-- =============================================
-- 存储过程10: 查询库存详情
-- =============================================
CREATE OR REPLACE FUNCTION sp_get_inventory_detail(
    p_sku_id        BIGINT
) RETURNS TABLE (
    sku_id          BIGINT,
    sku_code        VARCHAR(50),
    product_name    VARCHAR(255),
    specs           JSONB,
    quantity        INTEGER,
    locked_quantity INTEGER,
    available_qty   INTEGER,
    warning_qty     INTEGER,
    warehouse_id    INTEGER,
    version         INTEGER,
    updated_at      TIMESTAMPTZ,
    recent_logs     JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        i.sku_id, s.sku_code, p.name, s.specs,
        i.quantity, i.locked_quantity, i.available_qty,
        i.warning_qty, i.warehouse_id, i.version, i.updated_at,
        (
            SELECT jsonb_agg(jsonb_build_object(
                'op_type', l.operation_type,
                'qty', l.quantity,
                'before', l.before_qty,
                'after', l.after_qty,
                'ref_type', l.reference_type,
                'created', l.created_at
            ) ORDER BY l.created_at DESC)
            FROM inventory_logs l
            WHERE l.sku_id = i.sku_id
            LIMIT 10
        ) AS recent_logs
    FROM inventory i
    JOIN product_skus s ON i.sku_id = s.sku_id
    JOIN products p ON s.product_id = p.product_id
    WHERE i.sku_id = p_sku_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 存储过程11: 查询低库存商品
-- =============================================
CREATE OR REPLACE FUNCTION sp_get_low_stock_products(
    p_threshold     INTEGER DEFAULT NULL
) RETURNS TABLE (
    sku_id          BIGINT,
    sku_code        VARCHAR(50),
    product_name    VARCHAR(255),
    available_qty   INTEGER,
    warning_qty     INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        i.sku_id, s.sku_code, p.name,
        i.available_qty, i.warning_qty
    FROM inventory i
    JOIN product_skus s ON i.sku_id = s.sku_id
    JOIN products p ON s.product_id = p.product_id
    WHERE i.available_qty <= COALESCE(p_threshold, i.warning_qty, 10)
      AND p.status = 1
    ORDER BY i.available_qty ASC;
END;
$$ LANGUAGE plpgsql;
```

### 5.3 库存相关触发器

```sql
-- =============================================
-- 触发器: 库存预警
-- =============================================
CREATE OR REPLACE FUNCTION trg_fn_stock_warning()
RETURNS TRIGGER AS $$
BEGIN
    -- 库存低于预警值时记录日志
    IF NEW.available_qty <= NEW.warning_qty AND
       (OLD.available_qty > OLD.warning_qty OR OLD.warning_qty IS NULL) THEN
        RAISE WARNING '库存预警: SKU_ID=%, 可用库存=%, 预警值=%',
            NEW.sku_id, NEW.available_qty, NEW.warning_qty;
        -- 可扩展: 发送通知、生成补货单等
    END IF;

    -- 库存为0时自动下架
    IF NEW.available_qty = 0 AND OLD.available_qty > 0 THEN
        UPDATE product_skus SET status = 0 WHERE sku_id = NEW.sku_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_stock_warning
    AFTER UPDATE ON inventory
    FOR EACH ROW
    WHEN (NEW.available_qty IS DISTINCT FROM OLD.available_qty)
    EXECUTE FUNCTION trg_fn_stock_warning();

-- =============================================
-- 触发器: 库存变更审计
-- =============================================
CREATE OR REPLACE FUNCTION trg_fn_inventory_audit()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (
            table_name, record_id, operation,
            old_data, new_data
        ) VALUES (
            'inventory', NEW.sku_id, 'UPDATE',
            jsonb_build_object('quantity', OLD.quantity, 'locked', OLD.locked_quantity),
            jsonb_build_object('quantity', NEW.quantity, 'locked', NEW.locked_quantity)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_inventory_audit
    AFTER UPDATE ON inventory
    FOR EACH ROW
    WHEN (NEW.quantity IS DISTINCT FROM OLD.quantity OR
          NEW.locked_quantity IS DISTINCT FROM OLD.locked_quantity)
    EXECUTE FUNCTION trg_fn_inventory_audit();
```

---

## 6. 支付系统实现

### 6.1 支付流程架构

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              支付系统流程图                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   用户                    订单系统                    支付系统                │
│    │                        │                           │                   │
│    │ 1.提交支付             │                           │                   │
│    │───────────────────────→│                           │                   │
│    │                        │ 2.创建支付单               │                   │
│    │                        │──────────────────────────→│                   │
│    │                        │                           │ 3.调用第三方支付   │
│    │                        │                           │──────────────────→│
│    │                        │                           │       支付网关     │
│    │ 4.完成支付             │                           │←──────────────────│
│    │───────────────────────────────────────────────────────────────────────→│
│    │                        │                           │ 5.支付回调         │
│    │                        │←──────────────────────────│                   │
│    │                        │ 6.更新订单状态             │                   │
│    │                        │─────┬─────────────────────────────────────────→│
│    │                        │     │ 7.扣减库存          │                   │
│    │                        │     │────────────────────────────────────────→│
│    │ 8.支付成功             │     │                     │                   │
│    │←───────────────────────│←────┘                     │                   │
│    │                        │                           │                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 支付核心存储过程

#### 6.2.1 创建支付单存储过程

```sql
-- =============================================
-- 存储过程12: 创建支付单
-- =============================================
CREATE OR REPLACE FUNCTION sp_create_payment(
    p_order_id      BIGINT,
    p_user_id       BIGINT,
    p_channel       VARCHAR(20), -- alipay, wechat, unionpay
    p_client_ip     INET DEFAULT NULL
) RETURNS TABLE (
    payment_id      BIGINT,
    payment_no      VARCHAR(32),
    amount          DECIMAL(15,2),
    channel         VARCHAR(20),
    pay_params      JSONB, -- 返回给前端的支付参数
    result_code     INTEGER,
    result_msg      VARCHAR(255)
) AS $$
DECLARE
    v_payment_id    BIGINT;
    v_payment_no    VARCHAR(32);
    v_order         RECORD;
    v_expire_minutes INTEGER;
BEGIN
    -- 检查订单
    SELECT * INTO v_order FROM orders
    WHERE order_id = p_order_id AND user_id = p_user_id FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, NULL::DECIMAL,
                            NULL::VARCHAR, NULL::JSONB, -1, '订单不存在'::VARCHAR;
        RETURN;
    END IF;

    IF v_order.order_status != 0 THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, NULL::DECIMAL,
                            NULL::VARCHAR, NULL::JSONB, -2, '订单状态不允许支付'::VARCHAR;
        RETURN;
    END IF;

    -- 检查是否已有进行中的支付
    PERFORM 1 FROM payments
    WHERE order_id = p_order_id AND status IN (0, 1)
      AND expired_at > CURRENT_TIMESTAMP;

    IF FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, NULL::DECIMAL,
                            NULL::VARCHAR, NULL::JSONB, -3, '存在进行中的支付'::VARCHAR;
        RETURN;
    END IF;

    -- 生成支付单号
    v_payment_no := 'P' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') ||
                    LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');

    SELECT config_value::INTEGER INTO v_expire_minutes
    FROM system_configs WHERE config_key = 'order.expire.minutes';

    -- 创建支付记录
    INSERT INTO payments (
        payment_no, order_id, user_id, amount, channel,
        status, expired_at, client_ip, request_params
    ) VALUES (
        v_payment_no, p_order_id, p_user_id, v_order.pay_amount, p_channel,
        0, CURRENT_TIMESTAMP + (v_expire_minutes || ' minutes')::INTERVAL,
        p_client_ip, jsonb_build_object('source', 'order_pay')
    ) RETURNING payments.payment_id INTO v_payment_id;

    -- 更新订单支付状态
    UPDATE orders SET pay_status = 0 WHERE order_id = p_order_id;

    -- 生成支付参数 (实际应调用支付网关SDK)
    RETURN QUERY SELECT
        v_payment_id, v_payment_no, v_order.pay_amount, p_channel,
        jsonb_build_object(
            'payment_id', v_payment_id,
            'payment_no', v_payment_no,
            'amount', v_order.pay_amount,
            'channel', p_channel,
            'expire_time', CURRENT_TIMESTAMP + (v_expire_minutes || ' minutes')::INTERVAL,
            'mock_url', '/api/pay/mock/' || v_payment_no  -- 模拟支付URL
        ),
        0, '支付单创建成功'::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

#### 6.2.2 支付回调处理存储过程

```sql
-- =============================================
-- 存储过程13: 处理支付回调
-- =============================================
CREATE OR REPLACE FUNCTION sp_handle_payment_callback(
    p_payment_no        VARCHAR(32),
    p_channel           VARCHAR(20),
    p_channel_trans_id  VARCHAR(64),
    p_amount            DECIMAL(15,2),
    p_status            VARCHAR(20), -- SUCCESS, FAIL
    p_callback_data     JSONB
) RETURNS TABLE (
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_payment       RECORD;
    v_order         RECORD;
BEGIN
    -- 获取支付单
    SELECT * INTO v_payment FROM payments
    WHERE payment_no = p_payment_no FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT -1, '支付单不存在'::VARCHAR;
        RETURN;
    END IF;

    -- 幂等检查
    IF v_payment.status = 2 THEN
        RETURN QUERY SELECT 0, '支付已处理'::VARCHAR; -- 成功幂等
        RETURN;
    END IF;

    IF v_payment.status = 4 THEN
        RETURN QUERY SELECT -2, '支付单已关闭'::VARCHAR;
        RETURN;
    END IF;

    -- 金额校验
    IF v_payment.amount != p_amount THEN
        RETURN QUERY SELECT -3, '支付金额不匹配'::VARCHAR;
        RETURN;
    END IF;

    -- 处理成功回调
    IF p_status = 'SUCCESS' THEN
        -- 更新支付记录
        UPDATE payments SET
            status = 2,
            channel_trans_id = p_channel_trans_id,
            paid_at = CURRENT_TIMESTAMP,
            notify_data = p_callback_data
        WHERE payment_id = v_payment.payment_id;

        -- 获取并锁定订单
        SELECT * INTO v_order FROM orders
        WHERE order_id = v_payment.order_id FOR UPDATE;

        -- 更新订单状态
        UPDATE orders SET
            order_status = 1,
            pay_status = 2,
            paid_amount = paid_amount + p_amount,
            paid_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE order_id = v_payment.order_id;

        -- 记录状态变更
        INSERT INTO order_status_logs (order_id, from_status, to_status,
                                       operator_type, remark)
        VALUES (v_payment.order_id, 0, 1, 'SYSTEM',
                '支付成功，金额:' || p_amount);

        -- 扣减库存
        PERFORM sp_deduct_inventory(v_payment.order_id, NULL);

        RETURN QUERY SELECT 0, '支付处理成功'::VARCHAR;
    ELSE
        -- 处理失败
        UPDATE payments SET
            status = 3,
            notify_data = p_callback_data
        WHERE payment_id = v_payment.payment_id;

        RETURN QUERY SELECT -4, '支付失败'::VARCHAR;
    END IF;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

#### 6.2.3 退款申请存储过程

```sql
-- =============================================
-- 存储过程14: 申请退款
-- =============================================
CREATE OR REPLACE FUNCTION sp_apply_refund(
    p_order_id          BIGINT,
    p_item_id           BIGINT DEFAULT NULL, -- NULL表示整单退款
    p_user_id           BIGINT,
    p_amount            DECIMAL(15,2),
    p_reason            VARCHAR(255),
    p_refund_type       SMALLINT DEFAULT 1 -- 1:全额 2:部分
) RETURNS TABLE (
    refund_id           BIGINT,
    refund_no           VARCHAR(32),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_refund_id         BIGINT;
    v_refund_no         VARCHAR(32);
    v_order             RECORD;
    v_item              RECORD;
    v_payment           RECORD;
    v_max_refund        DECIMAL(15,2);
BEGIN
    -- 检查订单
    SELECT * INTO v_order FROM orders
    WHERE order_id = p_order_id AND user_id = p_user_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -1, '订单不存在'::VARCHAR;
        RETURN;
    END IF;

    -- 只有已付款订单可以退款
    IF v_order.pay_status != 2 THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -2, '订单未支付'::VARCHAR;
        RETURN;
    END IF;

    -- 获取支付记录
    SELECT * INTO v_payment FROM payments
    WHERE order_id = p_order_id AND status = 2
    ORDER BY paid_at DESC LIMIT 1;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -3, '支付记录不存在'::VARCHAR;
        RETURN;
    END IF;

    -- 单品退款检查
    IF p_item_id IS NOT NULL THEN
        SELECT * INTO v_item FROM order_items
        WHERE item_id = p_item_id AND order_id = p_order_id;

        IF NOT FOUND THEN
            RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -4, '订单商品不存在'::VARCHAR;
            RETURN;
        END IF;

        -- 检查是否已退款
        IF v_item.refund_status = 2 THEN
            RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -5, '该商品已退款'::VARCHAR;
            RETURN;
        END IF;

        v_max_refund := v_item.subtotal - v_item.refund_amount;
    ELSE
        v_max_refund := v_order.paid_amount - v_order.refund_amount;
    END IF;

    -- 金额检查
    IF p_amount > v_max_refund THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -6,
                            ('退款金额超过最大可退金额: ' || v_max_refund)::VARCHAR;
        RETURN;
    END IF;

    -- 生成退款单号
    v_refund_no := 'R' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') ||
                   LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');

    -- 创建退款记录
    INSERT INTO refunds (
        refund_no, payment_id, order_id, item_id,
        refund_type, amount, reason, status, applicant_id
    ) VALUES (
        v_refund_no, v_payment.payment_id, p_order_id, p_item_id,
        p_refund_type, p_amount, p_reason, 0, p_user_id
    ) RETURNING refunds.refund_id INTO v_refund_id;

    -- 更新订单退款状态
    IF p_item_id IS NULL THEN
        UPDATE orders SET order_status = 5 WHERE order_id = p_order_id;
    ELSE
        UPDATE order_items SET refund_status = 1 WHERE item_id = p_item_id;
    END IF;

    RETURN QUERY SELECT v_refund_id, v_refund_no, 0, '退款申请提交成功'::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

#### 6.2.4 退款处理存储过程

```sql
-- =============================================
-- 存储过程15: 执行退款
-- =============================================
CREATE OR REPLACE FUNCTION sp_execute_refund(
    p_refund_id         BIGINT,
    p_approver_id       BIGINT,
    p_approved          BOOLEAN,
    p_remark            VARCHAR(255) DEFAULT NULL
) RETURNS TABLE (
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_refund            RECORD;
    v_payment           RECORD;
    v_order             RECORD;
BEGIN
    SELECT * INTO v_refund FROM refunds
    WHERE refund_id = p_refund_id AND status = 0 FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT -1, '退款申请不存在或已处理'::VARCHAR;
        RETURN;
    END IF;

    IF NOT p_approved THEN
        -- 拒绝退款
        UPDATE refunds SET
            status = 2,
            approver_id = p_approver_id,
            remark = p_remark,
            approved_at = CURRENT_TIMESTAMP
        WHERE refund_id = p_refund_id;

        IF v_refund.item_id IS NULL THEN
            UPDATE orders SET order_status = 1 WHERE order_id = v_refund.order_id;
        ELSE
            UPDATE order_items SET refund_status = 0 WHERE item_id = v_refund.item_id;
        END IF;

        RETURN QUERY SELECT 0, '退款申请已拒绝'::VARCHAR;
        RETURN;
    END IF;

    -- 批准退款
    UPDATE refunds SET
        status = 3,
        approver_id = p_approver_id,
        approved_at = CURRENT_TIMESTAMP
    WHERE refund_id = p_refund_id;

    -- 调用退款接口 (模拟)
    UPDATE refunds SET
        status = 4,
        completed_at = CURRENT_TIMESTAMP,
        channel_trans_id = 'REFUND_' || v_refund.refund_no
    WHERE refund_id = p_refund_id;

    -- 更新订单/商品退款状态
    IF v_refund.item_id IS NULL THEN
        UPDATE orders SET
            order_status = 6,
            refund_amount = refund_amount + v_refund.amount
        WHERE order_id = v_refund.order_id;
    ELSE
        UPDATE order_items SET
            refund_status = 2,
            refund_qty = quantity,
            refund_amount = v_refund.amount
        WHERE item_id = v_refund.item_id;
    END IF;

    -- 返还库存 (如果是发货前退款)
    SELECT * INTO v_order FROM orders WHERE order_id = v_refund.order_id;
    IF v_order.ship_status = 0 THEN
        -- 返还库存逻辑
        PERFORM sp_return_stock(v_refund.order_id, v_refund.item_id);
    END IF;

    RETURN QUERY SELECT 0, '退款成功'::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;

-- 返还库存辅助函数
CREATE OR REPLACE FUNCTION sp_return_stock(
    p_order_id      BIGINT,
    p_item_id       BIGINT DEFAULT NULL
) RETURNS void AS $$
DECLARE
    v_item          RECORD;
BEGIN
    FOR v_item IN
        SELECT oi.* FROM order_items oi
        WHERE oi.order_id = p_order_id
          AND (p_item_id IS NULL OR oi.item_id = p_item_id)
    LOOP
        -- 增加库存
        UPDATE inventory SET
            quantity = quantity + v_item.quantity,
            version = version + 1
        WHERE sku_id = v_item.sku_id;

        -- 记录日志
        INSERT INTO inventory_logs (
            sku_id, operation_type, quantity,
            reference_type, reference_id, remark
        )
        SELECT
            v_item.sku_id, 'RETURN', v_item.quantity,
            'REFUND', p_order_id, '退款返还库存'
        FROM inventory WHERE sku_id = v_item.sku_id;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### 6.3 对账相关存储过程

```sql
-- =============================================
-- 存储过程: 日终对账
-- =============================================
CREATE OR REPLACE FUNCTION sp_daily_reconciliation(
    p_date          DATE
) RETURNS TABLE (
    channel         VARCHAR(20),
    system_count    BIGINT,
    system_amount   DECIMAL(15,2),
    success_count   BIGINT,
    success_amount  DECIMAL(15,2),
    diff_count      BIGINT,
    diff_amount     DECIMAL(15,2),
    result_msg      VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    WITH system_stats AS (
        SELECT
            channel,
            COUNT(*) AS cnt,
            COALESCE(SUM(amount), 0) AS amt
        FROM payments
        WHERE DATE(created_at) = p_date
        GROUP BY channel
    ),
    success_stats AS (
        SELECT
            channel,
            COUNT(*) AS cnt,
            COALESCE(SUM(amount), 0) AS amt
        FROM payments
        WHERE DATE(created_at) = p_date AND status = 2
        GROUP BY channel
    )
    SELECT
        s.channel,
        s.cnt AS system_count,
        s.amt AS system_amount,
        COALESCE(ss.cnt, 0) AS success_count,
        COALESCE(ss.amt, 0) AS success_amount,
        s.cnt - COALESCE(ss.cnt, 0) AS diff_count,
        s.amt - COALESCE(ss.amt, 0) AS diff_amount,
        CASE
            WHEN s.cnt = COALESCE(ss.cnt, 0) THEN '一致'
            ELSE '差异需核实'
        END::VARCHAR
    FROM system_stats s
    LEFT JOIN success_stats ss ON s.channel = ss.channel
    ORDER BY s.channel;
END;
$$ LANGUAGE plpgsql;
```

---

## 7. 促销系统实现

### 7.1 促销架构设计

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            促销系统架构图                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         促销规则引擎                                 │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│   │  │  满减规则   │  │  折扣规则   │  │  直减规则   │  │  包邮规则  │ │   │
│   │  │ condition   │  │ condition   │  │ condition   │  │ condition  │ │   │
│   │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │   │
│   │         └─────────────────┴─────────────────┴───────────────┘        │   │
│   │                              │                                       │   │
│   │                              ▼                                       │   │
│   │                    ┌─────────────────┐                               │   │
│   │                    │  fn_calc_discount │                              │   │
│   │                    │  统一优惠计算函数 │                               │   │
│   │                    └─────────────────┘                               │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   促销类型:                                                                  │
│   ┌────────────┬─────────────────────────────────────────────────────────┐  │
│   │ 优惠券     │ 满减券、折扣券、直减券、兑换券                           │  │
│   ├────────────┼─────────────────────────────────────────────────────────┤  │
│   │ 秒杀活动   │ 限时限量抢购，独立库存，排他性                           │  │
│   ├────────────┼─────────────────────────────────────────────────────────┤  │
│   │ 限时购     │ 时间段内特价销售                                         │  │
│   ├────────────┼─────────────────────────────────────────────────────────┤  │
│   │ 满额包邮   │ 订单金额达到阈值免运费                                   │  │
│   └────────────┴─────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 促销核心存储过程

#### 7.2.1 优惠券计算函数

```sql
-- =============================================
-- 函数: 计算优惠券优惠金额
-- =============================================
CREATE OR REPLACE FUNCTION fn_calc_coupon_discount(
    p_user_id       BIGINT,
    p_uc_id         BIGINT,
    p_order_amount  DECIMAL(15,2)
) RETURNS TABLE (
    discount_amount DECIMAL(15,2),
    result_code     INTEGER,
    result_msg      VARCHAR(255)
) AS $$
DECLARE
    v_uc            RECORD;
    v_coupon        RECORD;
    v_discount      DECIMAL(15,2) := 0;
BEGIN
    -- 获取用户优惠券
    SELECT uc.* INTO v_uc FROM user_coupons uc
    WHERE uc.uc_id = p_uc_id AND uc.user_id = p_user_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT 0::DECIMAL, -1, '优惠券不存在'::VARCHAR;
        RETURN;
    END IF;

    IF v_uc.status != 0 THEN
        RETURN QUERY SELECT 0::DECIMAL, -2, '优惠券状态不可用'::VARCHAR;
        RETURN;
    END IF;

    IF v_uc.valid_end < CURRENT_TIMESTAMP THEN
        RETURN QUERY SELECT 0::DECIMAL, -3, '优惠券已过期'::VARCHAR;
        RETURN;
    END IF;

    -- 获取优惠券详情
    SELECT * INTO v_coupon FROM coupons WHERE coupon_id = v_uc.coupon_id;

    -- 检查使用门槛
    IF p_order_amount < v_coupon.min_order_amount THEN
        RETURN QUERY SELECT 0::DECIMAL, -4,
            ('订单金额未达使用门槛: ' || v_coupon.min_order_amount)::VARCHAR;
        RETURN;
    END IF;

    -- 计算优惠金额
    IF v_coupon.coupon_type = 'FULL_REDUCTION' THEN
        -- 满减: 直接减去面额
        v_discount := LEAST(v_coupon.face_value, p_order_amount);
    ELSIF v_coupon.coupon_type = 'DISCOUNT' THEN
        -- 折扣: 面额表示折扣率，如0.8表示8折
        v_discount := p_order_amount * (1 - v_coupon.face_value);
    ELSIF v_coupon.coupon_type = 'DIRECT' THEN
        -- 直减
        v_discount := LEAST(v_coupon.face_value, p_order_amount);
    END IF;

    RETURN QUERY SELECT v_discount, 0, '计算成功'::VARCHAR;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_calc_coupon_discount IS '计算优惠券优惠金额';
```

#### 7.2.2 领取优惠券存储过程

```sql
-- =============================================
-- 存储过程16: 领取优惠券
-- =============================================
CREATE OR REPLACE FUNCTION sp_acquire_coupon(
    p_user_id       BIGINT,
    p_coupon_id     BIGINT
) RETURNS TABLE (
    uc_id           BIGINT,
    result_code     INTEGER,
    result_msg      VARCHAR(255)
) AS $$
DECLARE
    v_coupon        RECORD;
    v_uc_id         BIGINT;
    v_user_count    INTEGER;
BEGIN
    -- 获取优惠券信息并锁定
    SELECT * INTO v_coupon FROM coupons
    WHERE coupon_id = p_coupon_id AND status = 1 FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, -1, '优惠券不存在'::VARCHAR;
        RETURN;
    END IF;

    -- 检查总库存
    IF v_coupon.total_quantity IS NOT NULL
       AND v_coupon.issued_quantity >= v_coupon.total_quantity THEN
        RETURN QUERY SELECT NULL::BIGINT, -2, '优惠券已领完'::VARCHAR;
        RETURN;
    END IF;

    -- 检查用户领取限制
    SELECT COUNT(*) INTO v_user_count FROM user_coupons
    WHERE user_id = p_user_id AND coupon_id = p_coupon_id;

    IF v_user_count >= v_coupon.per_user_limit THEN
        RETURN QUERY SELECT NULL::BIGINT, -3, '超出领取限制'::VARCHAR;
        RETURN;
    END IF;

    -- 计算有效期
    IF v_coupon.valid_days IS NOT NULL THEN
        INSERT INTO user_coupons (
            user_id, coupon_id, valid_start, valid_end
        ) VALUES (
            p_user_id, p_coupon_id,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP + (v_coupon.valid_days || ' days')::INTERVAL
        ) RETURNING user_coupons.uc_id INTO v_uc_id;
    ELSE
        INSERT INTO user_coupons (
            user_id, coupon_id, valid_start, valid_end
        ) VALUES (
            p_user_id, p_coupon_id,
            v_coupon.valid_start, v_coupon.valid_end
        ) RETURNING user_coupons.uc_id INTO v_uc_id;
    END IF;

    -- 更新发放数量
    UPDATE coupons SET
        issued_quantity = issued_quantity + 1
    WHERE coupon_id = p_coupon_id;

    RETURN QUERY SELECT v_uc_id, 0, '领取成功'::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT NULL::BIGINT, -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

#### 7.2.3 秒杀下单存储过程

```sql
-- =============================================
-- 存储过程17: 秒杀下单
-- 特点: 高并发优化，使用乐观锁和队列控制
-- =============================================
CREATE OR REPLACE FUNCTION sp_create_seckill_order(
    p_user_id           BIGINT,
    p_act_id            INTEGER,
    p_address_id        BIGINT
) RETURNS TABLE (
    order_id            BIGINT,
    order_no            VARCHAR(32),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_act               RECORD;
    v_order_id          BIGINT;
    v_order_no          VARCHAR(32);
    v_address           RECORD;
    v_stock_key         TEXT;
    v_limit_key         TEXT;
    v_already_buy       INTEGER;
BEGIN
    -- 检查活动
    SELECT * INTO v_act FROM seckill_activities
    WHERE act_id = p_act_id FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -1, '活动不存在'::VARCHAR;
        RETURN;
    END IF;

    IF v_act.status != 1 OR v_act.start_time > CURRENT_TIMESTAMP
       OR v_act.end_time < CURRENT_TIMESTAMP THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -2, '活动未开始或已结束'::VARCHAR;
        RETURN;
    END IF;

    -- 检查是否已购买 (一人限购)
    SELECT COUNT(*) INTO v_already_buy FROM seckill_orders
    WHERE act_id = p_act_id AND user_id = p_user_id AND status = 2;

    IF v_already_buy >= v_act.limit_per_user THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -3, '已达到购买限制'::VARCHAR;
        RETURN;
    END IF;

    -- 检查库存 (使用乐观锁)
    IF v_act.sold_quantity >= v_act.stock_quantity THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -4, '秒杀库存不足'::VARCHAR;
        RETURN;
    END IF;

    -- 获取地址
    SELECT * INTO v_address FROM user_addresses
    WHERE address_id = p_address_id AND user_id = p_user_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -5, '收货地址不存在'::VARCHAR;
        RETURN;
    END IF;

    -- 生成订单号
    v_order_no := 'SK' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') ||
                  LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');

    BEGIN
        -- 扣减秒杀库存
        UPDATE seckill_activities SET
            sold_quantity = sold_quantity + 1
        WHERE act_id = p_act_id
          AND sold_quantity < stock_quantity;

        IF NOT FOUND THEN
            RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -4, '秒杀库存不足'::VARCHAR;
            RETURN;
        END IF;

        -- 创建订单
        INSERT INTO orders (
            order_no, user_id, order_status, pay_status, ship_status,
            goods_amount, discount_amount, freight_amount, pay_amount,
            consignee, phone, address, source, expired_at
        ) VALUES (
            v_order_no, p_user_id, 0, 0, 0,
            v_act.seckill_price, 0, 0, v_act.seckill_price,
            v_address.consignee, v_address.phone,
            v_address.province || v_address.city || v_address.district || v_address.detail_address,
            'seckill', CURRENT_TIMESTAMP + INTERVAL '10 minutes'
        ) RETURNING orders.order_id INTO v_order_id;

        -- 插入订单明细
        INSERT INTO order_items (
            order_id, product_id, sku_id, product_name, sku_specs,
            quantity, unit_price, subtotal
        )
        SELECT
            v_order_id, p.product_id, s.sku_id, p.name, s.specs,
            1, v_act.seckill_price, v_act.seckill_price
        FROM product_skus s
        JOIN products p ON s.product_id = p.product_id
        WHERE s.sku_id = v_act.sku_id;

        -- 记录秒杀订单
        INSERT INTO seckill_orders (act_id, user_id, order_id, status)
        VALUES (p_act_id, p_user_id, v_order_id, 2);

        -- 记录状态变更
        INSERT INTO order_status_logs (order_id, from_status, to_status,
                                       operator_type, remark)
        VALUES (v_order_id, NULL, 0, 'SYSTEM', '秒杀订单创建成功');

        RETURN QUERY SELECT v_order_id, v_order_no, 0, '秒杀成功'::VARCHAR;

    EXCEPTION WHEN unique_violation THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -3, '已达到购买限制'::VARCHAR;
    WHEN OTHERS THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -99, SQLERRM::VARCHAR;
    END;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_create_seckill_order IS '秒杀下单存储过程，带并发控制';
```

#### 7.2.4 促销价格计算存储过程

```sql
-- =============================================
-- 存储过程18: 计算促销价格
-- =============================================
CREATE OR REPLACE FUNCTION fn_calc_promotion_price(
    p_sku_id        BIGINT,
    p_user_id       BIGINT DEFAULT NULL
) RETURNS TABLE (
    original_price  DECIMAL(15,2),
    sale_price      DECIMAL(15,2),
    discount_type   VARCHAR(20),
    discount_value  DECIMAL(15,2),
    promotion_id    INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH base_price AS (
        SELECT s.sku_id, s.price AS sku_price, p.sale_price AS prod_price
        FROM product_skus s
        JOIN products p ON s.product_id = p.product_id
        WHERE s.sku_id = p_sku_id
    ),
    active_promotions AS (
        SELECT
            sa.act_id AS promo_id,
            sa.sku_id,
            sa.seckill_price AS promo_price,
            'seckill'::VARCHAR(20) AS promo_type,
            sa.seckill_price AS discount_val
        FROM seckill_activities sa
        WHERE sa.sku_id = p_sku_id
          AND sa.status = 1
          AND sa.start_time <= CURRENT_TIMESTAMP
          AND sa.end_time >= CURRENT_TIMESTAMP
          AND sa.sold_quantity < sa.stock_quantity

        UNION ALL

        SELECT
            p.promo_id,
            NULL AS sku_id,
            NULL AS promo_price,
            p.promo_type,
            (p.rules->'action'->>'value')::DECIMAL AS discount_val
        FROM promotions p
        WHERE p.status = 1
          AND p.start_time <= CURRENT_TIMESTAMP
          AND p.end_time >= CURRENT_TIMESTAMP
          AND (p.total_quota IS NULL OR p.used_quota < p.total_quota)
    ),
    best_promo AS (
        SELECT * FROM active_promotions
        ORDER BY
            CASE promo_type
                WHEN 'seckill' THEN 1
                WHEN 'flash' THEN 2
                ELSE 3
            END
        LIMIT 1
    )
    SELECT
        bp.sku_price,
        COALESCE(bp.promo_price, bp.sku_price),
        COALESCE(ap.promo_type, 'normal'),
        COALESCE(ap.discount_val, 0),
        ap.promo_id::INTEGER
    FROM base_price bp
    LEFT JOIN active_promotions ap ON ap.sku_id = bp.sku_id;
END;
$$ LANGUAGE plpgsql;
```

### 7.3 促销相关触发器

```sql
-- =============================================
-- 触发器: 秒杀库存扣减
-- =============================================
CREATE OR REPLACE FUNCTION trg_fn_seckill_stock()
RETURNS TRIGGER AS $$
BEGIN
    -- 支付成功后扣减秒杀库存
    IF NEW.order_status = 1 AND OLD.order_status = 0 THEN
        -- 更新商品销量统计
        UPDATE products p
        SET sold_count = sold_count + 1
        FROM order_items oi
        WHERE oi.order_id = NEW.order_id
          AND p.product_id = oi.product_id;
    END IF;

    -- 取消时返还秒杀库存
    IF NEW.order_status = 4 AND OLD.order_status = 0 THEN
        UPDATE seckill_activities sa
        SET sold_quantity = GREATEST(0, sold_quantity - 1)
        FROM seckill_orders so
        WHERE so.order_id = NEW.order_id
          AND sa.act_id = so.act_id;

        UPDATE seckill_orders SET status = 3
        WHERE order_id = NEW.order_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_seckill_stock
    AFTER UPDATE ON orders
    FOR EACH ROW
    WHEN (NEW.source = 'seckill')
    EXECUTE FUNCTION trg_fn_seckill_stock();
```

---

## 8. 性能优化策略

### 8.1 数据库优化措施

```sql
-- =============================================
-- 性能优化索引
-- =============================================

-- 订单表复合索引
CREATE INDEX CONCURRENTLY idx_order_user_status ON orders(user_id, order_status, created_at DESC);
CREATE INDEX CONCURRENTLY idx_order_pay_status ON orders(pay_status, expired_at)
    WHERE pay_status = 0;

-- 库存表索引
CREATE INDEX CONCURRENTLY idx_inventory_warehouse ON inventory(warehouse_id, available_qty);

-- 秒杀表索引
CREATE INDEX CONCURRENTLY idx_seckill_active ON seckill_activities(status, start_time, end_time)
    WHERE status = 1;

-- 库存预占表过期索引
CREATE INDEX CONCURRENTLY idx_resv_expired ON stock_reservations(expires_at, status)
    WHERE status = 1;

-- =============================================
-- 分区表设计
-- =============================================

-- 订单表按时间分区
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
-- 依此类推...

-- =============================================
-- 连接池配置建议
-- =============================================
/*
postgresql.conf:
max_connections = 500
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 16MB
maintenance_work_mem = 512MB
wal_buffers = 16MB
checkpoint_completion_target = 0.9
random_page_cost = 1.1
effective_io_concurrency = 200
*/
```

### 8.2 缓存策略

```sql
-- =============================================
-- 热点数据缓存视图
-- =============================================

-- 商品基本信息缓存查询
CREATE OR REPLACE VIEW vw_product_cache AS
SELECT
    p.product_id, p.sku, p.name, p.sale_price, p.status,
    p.stock_quantity, c.name AS category_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
WHERE p.status = 1;

-- 秒杀活动缓存视图
CREATE OR REPLACE VIEW vw_seckill_cache AS
SELECT
    sa.act_id, sa.act_name, sa.sku_id, sa.seckill_price,
    sa.original_price, sa.stock_quantity - sa.sold_quantity AS remain_qty,
    sa.start_time, sa.end_time
FROM seckill_activities sa
WHERE sa.status = 1
  AND sa.end_time > CURRENT_TIMESTAMP;
```

---

## 9. 安全控制措施

### 9.1 权限控制

```sql
-- =============================================
-- 数据库角色权限设计
-- =============================================

-- 创建角色
CREATE ROLE ecommerce_app WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ecommerce_admin WITH LOGIN PASSWORD 'admin_password';

-- 应用层权限 (只授予存储过程执行权限)
GRANT USAGE ON SCHEMA public TO ecommerce_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ecommerce_app;
GRANT SELECT, INSERT, UPDATE ON orders, order_items TO ecommerce_app;
GRANT SELECT ON products, product_skus, categories TO ecommerce_app;
GRANT SELECT, INSERT, UPDATE ON payments TO ecommerce_app;

-- 管理员权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ecommerce_admin;

-- 撤销直接表操作权限
REVOKE INSERT, UPDATE, DELETE ON orders FROM PUBLIC;
REVOKE INSERT, UPDATE, DELETE ON inventory FROM PUBLIC;
```

### 9.2 SQL注入防护

```sql
-- =============================================
-- 参数化查询示例 (存储过程天然防护)
-- =============================================

-- 安全的搜索 (避免动态SQL)
CREATE OR REPLACE FUNCTION sp_search_products(
    p_keyword       VARCHAR(100),
    p_category_id   INTEGER DEFAULT NULL,
    p_min_price     DECIMAL(15,2) DEFAULT NULL,
    p_max_price     DECIMAL(15,2) DEFAULT NULL
) RETURNS TABLE (
    product_id      BIGINT,
    name            VARCHAR(255),
    sale_price      DECIMAL(15,2),
    stock_quantity  INTEGER
) AS $$
BEGIN
    -- 使用参数绑定，自动防止SQL注入
    RETURN QUERY
    SELECT
        p.product_id, p.name, p.sale_price, p.stock_quantity
    FROM products p
    WHERE p.status = 1
      AND (p_keyword IS NULL OR p.name ILIKE '%' || p_keyword || '%')
      AND (p_category_id IS NULL OR p.category_id = p_category_id)
      AND (p_min_price IS NULL OR p.sale_price >= p_min_price)
      AND (p_max_price IS NULL OR p.sale_price <= p_max_price)
    ORDER BY p.sold_count DESC
    LIMIT 100;
END;
$$ LANGUAGE plpgsql;
```

### 9.3 审计日志

```sql
-- =============================================
-- 通用审计触发器
-- =============================================

CREATE OR REPLACE FUNCTION trg_fn_general_audit()
RETURNS TRIGGER AS $$
DECLARE
    v_old_data      JSONB;
    v_new_data      JSONB;
    v_operator_id   BIGINT;
BEGIN
    -- 从会话变量获取当前用户ID
    v_operator_id := NULLIF(current_setting('app.current_user_id', true), '')::BIGINT;

    IF TG_OP = 'DELETE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;
    ELSIF TG_OP = 'INSERT' THEN
        v_old_data := NULL;
        v_new_data := to_jsonb(NEW);
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
    END IF;

    INSERT INTO audit_logs (
        table_name, record_id, operation,
        old_data, new_data, operator_id
    ) VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP, v_old_data, v_new_data, v_operator_id
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 为关键表添加审计触发器
CREATE TRIGGER trg_audit_orders
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION trg_fn_general_audit();
```

---

## 10. 测试方案

### 10.1 单元测试

```sql
-- =============================================
-- 订单系统测试用例
-- =============================================

-- 测试1: 正常创建订单
DO $$
DECLARE
    v_result        RECORD;
    v_user_id       BIGINT;
    v_address_id    BIGINT;
    v_sku_id        BIGINT;
BEGIN
    -- 准备测试数据
    INSERT INTO users (username, email, password_hash)
    VALUES ('test_user', 'test@test.com', 'hash')
    RETURNING user_id INTO v_user_id;

    INSERT INTO user_addresses (user_id, consignee, phone, province, city, district, detail_address)
    VALUES (v_user_id, 'Test', '13800138000', '北京', '北京', '海淀', '测试地址')
    RETURNING address_id INTO v_address_id;

    -- 创建商品
    INSERT INTO categories (name) VALUES ('测试分类');
    INSERT INTO products (sku, name, base_price, sale_price, category_id, status)
    VALUES ('TEST001', '测试商品', 100, 99, 1, 1);
    INSERT INTO product_skus (product_id, sku_code, specs, price, stock_quantity, status)
    VALUES (1, 'TEST001-RED', '{"颜色":"红色"}'::JSONB, 99, 100, 1)
    RETURNING sku_id INTO v_sku_id;

    INSERT INTO inventory (sku_id, quantity) VALUES (v_sku_id, 100);

    -- 执行测试
    SELECT * INTO v_result FROM sp_create_order(
        v_user_id,
        '[{"sku_id": ' || v_sku_id || ', "quantity": 2}]'::JSONB,
        v_address_id
    );

    RAISE NOTICE '测试结果: code=%, msg=%, order_id=%',
        v_result.result_code, v_result.result_msg, v_result.order_id;

    -- 断言
    ASSERT v_result.result_code = 0, '创建订单失败: ' || v_result.result_msg;
    ASSERT v_result.pay_amount = 99 * 2, '金额计算错误';

    -- 清理
    ROLLBACK;
END $$;

-- =============================================
-- 库存系统并发测试
-- =============================================

-- 测试2: 并发库存扣减 (使用pgbench模拟)
/*
创建测试脚本 concurrent_stock_test.sql:
\set sku_id 1
\set qty random(1,5)
\set order_id random(100000,999999)

BEGIN;
SELECT sp_deduct_inventory(:order_id);
COMMIT;

运行命令:
pgbench -c 10 -j 4 -t 1000 -f concurrent_stock_test.sql ecommerce_dca
*/

-- =============================================
-- 秒杀系统压力测试
-- =============================================

-- 测试3: 秒杀超卖检查
CREATE OR REPLACE FUNCTION test_seckill_no_oversell()
RETURNS BOOLEAN AS $$
DECLARE
    v_act_id        INTEGER;
    v_sku_id        BIGINT;
    v_initial_stock INTEGER := 10;
    v_success_count INTEGER := 0;
    v_user_id       BIGINT;
    v_result        RECORD;
BEGIN
    -- 准备数据
    INSERT INTO products (sku, name, base_price, sale_price, status)
    VALUES ('SECKILL01', '秒杀商品', 100, 99, 1);

    INSERT INTO product_skus (product_id, sku_code, specs, price, stock_quantity, status)
    VALUES (1, 'SECKILL01-001', '{}'::JSONB, 99, 100, 1)
    RETURNING sku_id INTO v_sku_id;

    INSERT INTO seckill_activities (act_name, sku_id, seckill_price, original_price,
                                    stock_quantity, start_time, end_time, status)
    VALUES ('测试秒杀', v_sku_id, 9.9, 99, v_initial_stock,
            CURRENT_TIMESTAMP - INTERVAL '1 hour',
            CURRENT_TIMESTAMP + INTERVAL '1 hour', 1)
    RETURNING act_id INTO v_act_id;

    -- 模拟20个用户抢购10件商品
    FOR i IN 1..20 LOOP
        INSERT INTO users (username, email, password_hash)
        VALUES ('user_' || i, 'user' || i || '@test.com', 'hash')
        RETURNING user_id INTO v_user_id;

        INSERT INTO user_addresses (user_id, consignee, phone, province, city, district, detail_address)
        VALUES (v_user_id, 'User', '13800138000', '北京', '北京', '海淀', '地址');

        BEGIN
            SELECT * INTO v_result FROM sp_create_seckill_order(
                v_user_id, v_act_id,
                (SELECT address_id FROM user_addresses WHERE user_id = v_user_id LIMIT 1)
            );

            IF v_result.result_code = 0 THEN
                v_success_count := v_success_count + 1;
            END IF;
        EXCEPTION WHEN OTHERS THEN
            NULL; -- 忽略异常
        END;
    END LOOP;

    RAISE NOTICE '成功订单数: %, 限制: %', v_success_count, v_initial_stock;

    -- 验证没有超卖
    ASSERT v_success_count <= v_initial_stock, '发生超卖!';

    RETURN v_success_count <= v_initial_stock;
END;
$$ LANGUAGE plpgsql;
```

### 10.2 集成测试

```sql
-- =============================================
-- 完整下单流程测试
-- =============================================

CREATE OR REPLACE FUNCTION test_full_order_flow()
RETURNS TABLE (
    step_name       VARCHAR(50),
    result          VARCHAR(20),
    details         TEXT
) AS $$
DECLARE
    v_user_id       BIGINT;
    v_address_id    BIGINT;
    v_sku_id        BIGINT;
    v_order_id      BIGINT;
    v_order_no      VARCHAR(32);
    v_payment_id    BIGINT;
    v_pay_result    RECORD;
    v_order_check   RECORD;
BEGIN
    -- Step 1: 初始化数据
    INSERT INTO users (username, email, password_hash)
    VALUES ('flow_test', 'flow@test.com', 'hash')
    RETURNING user_id INTO v_user_id;

    INSERT INTO user_addresses (user_id, consignee, phone, province, city, district, detail_address)
    VALUES (v_user_id, 'Flow', '13800138000', '北京', '北京', '海淀', '详细地址')
    RETURNING address_id INTO v_address_id;

    INSERT INTO categories (name) VALUES ('测试分类');
    INSERT INTO products (sku, name, base_price, sale_price, category_id, status)
    VALUES ('FLOW001', '流程测试商品', 199, 99, 1, 1);
    INSERT INTO product_skus (product_id, sku_code, specs, price, stock_quantity, status)
    VALUES (1, 'FLOW001-BLACK', '{"颜色":"黑色"}'::JSONB, 99, 50, 1)
    RETURNING sku_id INTO v_sku_id;

    INSERT INTO inventory (sku_id, quantity) VALUES (v_sku_id, 50);

    RETURN QUERY SELECT '初始化数据'::VARCHAR, 'PASS'::VARCHAR, '用户、商品、库存创建成功'::TEXT;

    -- Step 2: 创建订单
    SELECT * INTO v_pay_result FROM sp_create_order(
        v_user_id,
        jsonb_build_array(jsonb_build_object('sku_id', v_sku_id, 'quantity', 2)),
        v_address_id
    );

    v_order_id := v_pay_result.order_id;
    v_order_no := v_pay_result.order_no;

    IF v_pay_result.result_code = 0 THEN
        RETURN QUERY SELECT '创建订单'::VARCHAR, 'PASS'::VARCHAR,
                            ('订单号: ' || v_order_no)::TEXT;
    ELSE
        RETURN QUERY SELECT '创建订单'::VARCHAR, 'FAIL'::VARCHAR, v_pay_result.result_msg::TEXT;
        RETURN;
    END IF;

    -- Step 3: 创建支付
    SELECT * INTO v_pay_result FROM sp_create_payment(v_order_id, v_user_id, 'alipay');
    v_payment_id := v_pay_result.payment_id;

    IF v_pay_result.result_code = 0 THEN
        RETURN QUERY SELECT '创建支付'::VARCHAR, 'PASS'::VARCHAR,
                            ('支付单: ' || v_pay_result.payment_no)::TEXT;
    ELSE
        RETURN QUERY SELECT '创建支付'::VARCHAR, 'FAIL'::VARCHAR, v_pay_result.result_msg::TEXT;
        RETURN;
    END IF;

    -- Step 4: 支付回调
    SELECT * INTO v_pay_result FROM sp_handle_payment_callback(
        v_pay_result.payment_no, 'alipay', 'ALI20240101', v_pay_result.amount, 'SUCCESS',
        '{}'::JSONB
    );

    IF v_pay_result.result_code = 0 THEN
        RETURN QUERY SELECT '支付回调'::VARCHAR, 'PASS'::VARCHAR, '支付处理成功'::TEXT;
    ELSE
        RETURN QUERY SELECT '支付回调'::VARCHAR, 'FAIL'::VARCHAR, v_pay_result.result_msg::TEXT;
        RETURN;
    END IF;

    -- Step 5: 验证订单状态
    SELECT order_status, pay_status INTO v_order_check FROM orders WHERE order_id = v_order_id;

    IF v_order_check.order_status = 1 AND v_order_check.pay_status = 2 THEN
        RETURN QUERY SELECT '状态验证'::VARCHAR, 'PASS'::VARCHAR,
                            ('订单状态=' || v_order_check.order_status)::TEXT;
    ELSE
        RETURN QUERY SELECT '状态验证'::VARCHAR, 'FAIL'::VARCHAR, '订单状态不正确'::TEXT;
        RETURN;
    END IF;

    -- Step 6: 验证库存
    SELECT quantity, locked_quantity INTO v_order_check FROM inventory WHERE sku_id = v_sku_id;

    IF v_order_check.quantity = 48 AND v_order_check.locked_quantity = 0 THEN
        RETURN QUERY SELECT '库存验证'::VARCHAR, 'PASS'::VARCHAR,
                            '库存正确扣减(48/50)'::TEXT;
    ELSE
        RETURN QUERY SELECT '库存验证'::VARCHAR, 'FAIL'::VARCHAR,
                            ('库存异常: ' || v_order_check.quantity)::TEXT;
    END IF;

    RETURN QUERY SELECT '全流程测试'::VARCHAR, 'PASS'::VARCHAR, '所有步骤通过'::TEXT;
END;
$$ LANGUAGE plpgsql;
```

### 10.3 性能测试基准

```sql
-- =============================================
-- 性能监控视图
-- =============================================

-- 慢查询监控
CREATE VIEW vw_slow_queries AS
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE mean_time > 100  -- 超过100ms
ORDER BY mean_time DESC
LIMIT 20;

-- 库存操作性能统计
CREATE VIEW vw_inventory_perf AS
SELECT
    operation_type,
    COUNT(*) AS op_count,
    AVG(EXTRACT(EPOCH FROM (created_at - LAG(created_at) OVER (ORDER BY created_at)))) AS avg_interval
FROM inventory_logs
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY operation_type;

-- 订单吞吐量统计
CREATE VIEW vw_order_throughput AS
SELECT
    DATE_TRUNC('hour', created_at) AS hour,
    COUNT(*) AS order_count,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(pay_amount) AS total_amount
FROM orders
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;
```

---

## 11. 总结

### 11.1 核心特性总结

本文档详细阐述了电商系统的数据库中心架构(DCA)实现，核心特点包括：

| 特性 | 实现方式 | 效果 |
|------|----------|------|
| 强一致性 | 存储过程内事务控制 | 订单/库存/支付数据完全一致 |
| 高并发 | 乐观锁+行级锁 | 支持秒杀等高并发场景 |
| 可审计 | 全链路触发器记录 | 完整的操作追溯能力 |
| 高性能 | 分区表+合理索引 | 亿级数据毫秒响应 |
| 安全 | 角色权限+参数化查询 | 防止SQL注入和越权访问 |

### 11.2 存储过程清单

| 序号 | 名称 | 功能 | 所在模块 |
|------|------|------|----------|
| 1 | sp_create_order | 创建订单 | 订单系统 |
| 2 | sp_cancel_order | 取消订单 | 订单系统 |
| 3 | sp_confirm_receive | 确认收货 | 订单系统 |
| 4 | sp_get_order_detail | 查询订单详情 | 订单系统 |
| 5 | sp_get_user_orders | 查询用户订单列表 | 订单系统 |
| 6 | sp_deduct_inventory | 库存扣减 | 库存系统 |
| 7 | sp_stock_in | 库存入库 | 库存系统 |
| 8 | sp_release_expired_reservations | 释放过期预占 | 库存系统 |
| 9 | sp_adjust_inventory | 库存盘点 | 库存系统 |
| 10 | sp_get_inventory_detail | 查询库存详情 | 库存系统 |
| 11 | sp_get_low_stock_products | 低库存查询 | 库存系统 |
| 12 | sp_create_payment | 创建支付单 | 支付系统 |
| 13 | sp_handle_payment_callback | 支付回调处理 | 支付系统 |
| 14 | sp_apply_refund | 申请退款 | 支付系统 |
| 15 | sp_execute_refund | 执行退款 | 支付系统 |
| 16 | sp_acquire_coupon | 领取优惠券 | 促销系统 |
| 17 | sp_create_seckill_order | 秒杀下单 | 促销系统 |
| 18 | fn_calc_promotion_price | 计算促销价格 | 促销系统 |

### 11.3 扩展建议

1. **读写分离**: 配置PostgreSQL主从复制，查询走从库
2. **分库分表**: 订单量超过单机容量时，按user_id分片
3. **缓存层**: 引入Redis缓存热点商品和库存
4. **消息队列**: 使用RabbitMQ/Kafka处理异步任务
5. **监控告警**: 集成Prometheus+Grafana监控系统健康度

---

*文档版本: 1.0*
*创建日期: 2025-01*
*作者: PostgreSQL DCA项目团队*
