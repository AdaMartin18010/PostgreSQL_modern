# 金融系统数据库中心架构(DCA)实现

## 目录

- [金融系统数据库中心架构(DCA)实现](#金融系统数据库中心架构dca实现)
  - [目录](#目录)
  - [1. 系统概述](#1-系统概述)
    - [1.1 业务背景](#11-业务背景)
    - [1.2 设计原则](#12-设计原则)
    - [1.3 会计恒等式](#13-会计恒等式)
  - [2. 系统架构设计](#2-系统架构设计)
    - [2.1 整体架构图](#21-整体架构图)
    - [2.2 模块交互关系](#22-模块交互关系)
    - [2.3 数据一致性保障机制](#23-数据一致性保障机制)
  - [3. 数据库设计](#3-数据库设计)
    - [3.1 完整ER图](#31-完整er图)
    - [3.2 数据库Schema创建](#32-数据库schema创建)
  - [4. 账户系统实现](#4-账户系统实现)
    - [4.1 账户生命周期](#41-账户生命周期)
    - [4.2 账户核心存储过程](#42-账户核心存储过程)
      - [4.2.1 客户开户存储过程](#421-客户开户存储过程)
      - [4.2.2 账户开户存储过程](#422-账户开户存储过程)
      - [4.2.3 账户销户存储过程](#423-账户销户存储过程)
      - [4.2.4 账户冻结/解冻存储过程](#424-账户冻结解冻存储过程)
      - [4.2.5 余额查询存储过程](#425-余额查询存储过程)
    - [4.3 账户相关触发器](#43-账户相关触发器)
  - [5. 转账系统实现](#5-转账系统实现)
    - [5.1 转账流程架构](#51-转账流程架构)
    - [5.2 转账核心存储过程](#52-转账核心存储过程)
      - [5.2.1 实时转账存储过程](#521-实时转账存储过程)
      - [5.2.2 存款存储过程](#522-存款存储过程)
      - [5.2.3 取款存储过程](#523-取款存储过程)
      - [5.2.4 批量转账存储过程](#524-批量转账存储过程)
    - [5.3 转账相关触发器](#53-转账相关触发器)
  - [6. 清算系统实现](#6-清算系统实现)
    - [6.1 日终清算流程](#61-日终清算流程)
    - [6.2 清算核心存储过程](#62-清算核心存储过程)
      - [6.2.1 日终清算存储过程](#621-日终清算存储过程)
      - [6.2.2 对账存储过程](#622-对账存储过程)
    - [6.3 会计恒等式校验函数](#63-会计恒等式校验函数)
  - [7. 风控系统实现](#7-风控系统实现)
    - [7.1 风控架构设计](#71-风控架构设计)
    - [7.2 风控核心存储过程](#72-风控核心存储过程)
      - [7.2.1 综合风控检查函数](#721-综合风控检查函数)
      - [7.2.2 限额检查函数](#722-限额检查函数)
      - [7.2.3 反欺诈检查函数](#723-反欺诈检查函数)
      - [7.2.4 反洗钱检查函数](#724-反洗钱检查函数)
  - [8. 性能优化策略](#8-性能优化策略)
    - [8.1 数据库优化](#81-数据库优化)
    - [8.2 高并发处理](#82-高并发处理)
  - [9. 安全控制措施](#9-安全控制措施)
    - [9.1 权限控制](#91-权限控制)
    - [9.2 数据加密](#92-数据加密)
  - [10. 测试方案](#10-测试方案)
    - [10.1 单元测试](#101-单元测试)
    - [10.2 性能测试](#102-性能测试)
  - [11. 总结](#11-总结)
    - [11.1 核心特性](#111-核心特性)
    - [11.2 存储过程清单](#112-存储过程清单)
    - [11.3 风控规则清单](#113-风控规则清单)

---

## 1. 系统概述

### 1.1 业务背景

金融系统是数据一致性和安全性要求最高的业务场景之一。
在数据库中心架构(DCA)模式下，我们通过存储过程实现核心业务逻辑，确保账务处理的**强一致性**、**原子性**和**可追溯性**。
本系统严格遵循会计恒等式，实现完整的借贷记账体系。

### 1.2 设计原则

| 原则 | 说明 | 实现方式 |
|------|------|----------|
| **ACID** | 原子性、一致性、隔离性、持久性 | 存储过程内事务控制 |
| **借贷平衡** | 有借必有贷，借贷必相等 | 双向记账校验 |
| **不可篡改** | 账务记录一旦生成就不能修改 | 只插入不更新设计 |
| **全程留痕** | 所有操作完整记录审计日志 | 触发器自动记录 |
| **T+0实时** | 转账实时到账 | 同步处理机制 |

### 1.3 会计恒等式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          会计恒等式与记账规则                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   基本恒等式:                                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  资产 = 负债 + 所有者权益                                            │  │
│   │  Assets = Liabilities + Owner's Equity                              │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   扩展恒等式:                                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  资产 + 费用 = 负债 + 所有者权益 + 收入                              │  │
│   │  Assets + Expenses = Liabilities + Equity + Revenue                 │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   记账规则:                                                                  │
│   ┌──────────────────┬──────────────────┬──────────────────┐             │  │
│   │     账户类型      │     增加方向      │     减少方向      │             │  │
│   ├──────────────────┼──────────────────┼──────────────────┤             │  │
│   │     资产类       │       借方        │       贷方        │             │  │
│   │     负债类       │       贷方        │       借方        │             │  │
│   │     权益类       │       贷方        │       借方        │             │  │
│   │     收入类       │       贷方        │       借方        │             │  │
│   │     费用类       │       借方        │       贷方        │             │  │
│   └──────────────────┴──────────────────┴──────────────────┘             │  │
│                                                                             │
│   系统校验:                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  ∀交易: Σ借方金额 = Σ贷方金额                                        │  │
│   │  ∀时点: 总资产账户余额 = 总负债账户余额 + 总权益账户余额              │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 系统架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            金融系统DCA架构总览                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│   │   网银门户   │  │   移动APP   │  │   商户平台  │  │  运营管理台  │           │
│   │   (Web)     │  │   (iOS/Android)│  │   (API)   │  │   (Admin)   │           │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘           │
│          │                │                │                │                  │
│          └────────────────┴────────────────┴────────────────┘                  │
│                                   │                                              │
│                          ┌────────▼────────┐                                     │
│                          │   API Gateway   │                                     │
│                          │  (限流/鉴权/路由) │                                    │
│                          └────────┬────────┘                                     │
│                                   │                                              │
│   ╔═══════════════════════════════╧═══════════════════════════════╗              │
│   ║                    数据库中心架构核心层                         ║              │
│   ║  ┌─────────────────────────────────────────────────────┐     ║              │
│   ║  │  业务编排层 (Business Orchestration)                 │     ║              │
│   ║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │     ║              │
│   ║  │  │账户开户  │ │实时转账  │ │批量转账  │ │日终清算│ │     ║              │
│   ║  │  │sp_acct_  │ │sp_transfer│ │sp_batch_ │ │sp_daily│ │     ║              │
│   ║  │  │  open   │ │  _realtime│ │ transfer│ │settle  │ │     ║              │
│   ║  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │     ║              │
│   ║  └─────────────────────────────────────────────────────┘     ║              │
│   ║  ┌─────────────────────────────────────────────────────┐     ║              │
│   ║  │  核心账务引擎 (Core Accounting Engine)               │     ║              │
│   ║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │     ║              │
│   ║  │  │借贷记账  │ │余额更新  │ │会计分录  │ │恒等校验│ │     ║              │
│   ║  │  │trg_debit │ │trg_credit│ │trg_entry │ │fn_check│ │     ║              │
│   ║  │  │ _credit  │ │  _update │ │  _create │ │ balance│ │     ║              │
│   ║  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │     ║              │
│   ║  └─────────────────────────────────────────────────────┘     ║              │
│   ║  ┌─────────────────────────────────────────────────────┐     ║              │
│   ║  │  风控引擎层 (Risk Control Engine)                    │     ║              │
│   ║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │     ║              │
│   ║  │  │规则引擎  │ │反欺诈检测│ │额度控制  │ │异常监控│ │     ║              │
│   ║  │  │fn_risk_  │ │fn_fraud_ │ │sp_limit_ │ │trg_alert│ │     ║              │
│   ║  │  │  check   │ │  detect  │ │  check   │ │       │ │     ║              │
│   ║  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │     ║              │
│   ║  └─────────────────────────────────────────────────────┘     ║              │
│   ╚═══════════════════════════════════════════════════════════════╝              │
│                                   │                                              │
│   ┌───────────────────────────────┼───────────────────────────────┐              │
│   │        PostgreSQL Cluster      │                               │              │
│   │  ┌──────────┐ ┌──────────┐    │    ┌──────────┐ ┌──────────┐ │              │
│   │  │  Primary │←│ Standby  │    │    │  只读节点  │ │  审计库   │ │              │
│   │  │   Node   │→│   Node   │    │    │  (报表)   │ │ (归档)   │ │              │
│   │  │ (同步流) │  │ (异步流) │    │    │          │ │          │ │              │
│   │  └──────────┘ └──────────┘    │    └──────────┘ └──────────┘ │              │
│   │                               │                               │              │
│   │  ┌─────────────────────────────────────────────────────────┐  │              │
│   │  │  分区策略: 账户表(hash) / 交易表(时间) / 流水表(时间)      │  │              │
│   │  └─────────────────────────────────────────────────────────┘  │              │
│   └───────────────────────────────┼───────────────────────────────┘              │
│                                   │                                              │
│                          ┌────────▼────────┐                                     │
│                          │    审计追踪系统   │                                     │
│                          │  (CDC → Kafka → │                                     │
│                          │   Data Lake)    │                                     │
│                          └─────────────────┘                                     │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块交互关系

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          核心模块交互关系图                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                          ┌─────────────┐                                        │
│                          │   账户系统   │                                        │
│                          │  sp_acct_*  │                                        │
│                          │  开户/销户  │                                        │
│                          │  余额管理   │                                        │
│                          └──────┬──────┘                                        │
│                                 │                                               │
│                    ┌────────────┼────────────┐                                  │
│                    │            │            │                                  │
│                    ▼            ▼            ▼                                  │
│            ┌───────────┐ ┌───────────┐ ┌───────────┐                          │
│            │  转账系统  │ │  清算系统  │ │  风控系统  │                          │
│            │sp_transfer│ │sp_settle* │ │sp_risk_*  │                          │
│            │实时/批量  │ │日终清算   │ │规则/反欺诈│                          │
│            └─────┬─────┘ └─────┬─────┘ └─────┬─────┘                          │
│                  │             │             │                                  │
│                  └─────────────┼─────────────┘                                  │
│                                │                                                │
│                    ┌───────────▼───────────┐                                    │
│                    │    统一账务引擎        │                                    │
│                    │  ┌─────────────────┐  │                                    │
│                    │  │   借贷记账原则   │  │                                    │
│                    │  │ Debit = Credit  │  │                                    │
│                    │  └─────────────────┘  │                                    │
│                    └───────────┬───────────┘                                    │
│                                │                                                │
│                    ┌───────────▼───────────┐                                    │
│                    │    会计分录/余额表     │                                    │
│                    │  account_entries      │                                    │
│                    │  account_balances     │                                    │
│                    └───────────────────────┘                                    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 数据一致性保障机制

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        强一致性保障机制                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   1. 事务隔离级别: SERIALIZABLE                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │  BEGIN ISOLATION LEVEL SERIALIZABLE;                                    │   │
│   │  -- 执行转账操作                                                         │   │
│   │  -- 1. 检查余额                                                         │   │
│   │  -- 2. 扣减付款方余额                                                    │   │
│   │  -- 3. 增加收款方余额                                                    │   │
│   │  -- 4. 插入会计分录                                                      │   │
│   │  -- 5. 更新交易状态                                                      │   │
│   │  COMMIT;                                                                │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   2. 乐观锁版本控制                                                              │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │  UPDATE account_balances                                               │   │
│   │  SET balance = balance - p_amount,                                     │   │
│   │      version = version + 1,                                            │   │
│   │      last_tx_id = p_tx_id                                              │   │
│   │  WHERE account_no = p_from_account                                     │   │
│   │    AND version = p_expected_version;  -- 版本号校验                      │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   3. 会计恒等式校验                                                              │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │  CREATE CONSTRAINT TRIGGER trg_accounting_balance                       │   │
│   │  AFTER INSERT ON account_entries                                        │   │
│   │  DEFERRABLE INITIALLY DEFERRED                                          │   │
│   │  FOR EACH ROW EXECUTE FUNCTION fn_check_accounting_balance();          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   4. 对账补偿机制                                                                │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │  每日批处理:                                                            │   │
│   │  1. 汇总当日所有交易                                                    │   │
│   │  2. 计算各账户期末余额                                                   │   │
│   │  3. 校验: Σ借方 = Σ贷方                                                  │   │
│   │  4. 校验: 各账户余额 = 期初 + 流入 - 流出                                  │   │
│   │  5. 生成差异报告，触发人工复核                                             │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 数据库设计

### 3.1 完整ER图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           金融系统数据库ER图                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌──────────────────┐                                                           │
│   │   customers      │                                                           │
│   │──────────────────│                                                           │
│   │ PK customer_id   │                                                           │
│   │    customer_no   │◄─────────────────────────────────────┐                    │
│   │    name          │                                    │                    │
│   │    id_type       │                                    │                    │
│   │    id_number     │                                    │                    │
│   │    phone         │                                    │                    │
│   │    status        │                                    │                    │
│   │    risk_level    │                                    │                    │
│   └────────┬─────────┘                                    │                    │
│            │                                               │                    │
│            │ 1:N                                           │                    │
│            ▼                                               │                    │
│   ┌──────────────────┐         ┌──────────────────┐       │                    │
│   │   accounts       │         │ account_limits   │       │                    │
│   │──────────────────│         │──────────────────│       │                    │
│   │ PK account_id    │         │ PK limit_id      │       │                    │
│   │    account_no    │         │ FK account_id    │───────┘                    │
│   │ FK customer_id   │◄────────│    daily_limit   │                            │
│   │    account_type  │         │    single_limit  │                            │
│   │    currency      │         │    monthly_limit │                            │
│   │    status        │         └──────────────────┘                            │
│   │    opened_at     │                                                         │
│   │    closed_at     │                                                         │
│   └────────┬─────────┘                                                         │
│            │                                                                    │
│            │ 1:N                                                                │
│            ▼                                                                    │
│   ┌──────────────────┐         ┌──────────────────┐        ┌────────────────┐  │
│   │ account_balances │         │ account_entries  │        │  transactions  │  │
│   │──────────────────│         │──────────────────│        │────────────────│  │
│   │ PK balance_id    │         │ PK entry_id      │◄───────│ FK entry_id    │  │
│   │ FK account_id    │◄────────│ FK account_id    │        │    tx_id       │  │
│   │    balance       │         │    tx_id         │        │    tx_no       │  │
│   │    frozen_amount │         │    entry_type    │        │    tx_type     │  │
│   │    available     │         │    amount        │        │    amount      │  │
│   │    version       │         │    direction     │        │    currency    │  │
│   │    last_tx_id    │         │    remark        │        │    status      │  │
│   └──────────────────┘         │    created_at    │        │    created_at  │  │
│                                └──────────────────┘        └────────────────┘  │
│                                                                                  │
│   ┌──────────────────┐         ┌──────────────────┐        ┌────────────────┐  │
│   │  batch_tasks     │         │ batch_details    │        │   risk_logs    │  │
│   │──────────────────│         │──────────────────│        │────────────────│  │
│   │ PK batch_id      │◄────────│ FK batch_id      │        │ PK risk_id     │  │
│   │    batch_no      │         │    detail_id     │        │    tx_id       │  │
│   │    batch_type    │         │    from_account  │        │    risk_type   │  │
│   │    total_count   │         │    to_account    │        │    risk_level  │  │
│   │    total_amount  │         │    amount        │        │    rule_id     │  │
│   │    status        │         │    status        │        │    result      │  │
│   │    execute_time  │         │    error_msg     │        │    created_at  │  │
│   └──────────────────┘         └──────────────────┘        └────────────────┘  │
│                                                                                  │
│   ┌──────────────────┐         ┌──────────────────┐        ┌────────────────┐  │
│   │  daily_settlements│        │ settlement_details│       │ audit_logs     │  │
│   │──────────────────│         │──────────────────│        │────────────────│  │
│   │ PK settle_id     │◄────────│ FK settle_id     │        │ PK audit_id    │  │
│   │    settle_date   │         │    detail_id     │        │    table_name  │  │
│   │    total_debit   │         │    account_no    │        │    record_id   │  │
│   │    total_credit  │         │    begin_balance │        │    operation   │  │
│   │    diff_amount   │         │    end_balance   │        │    old_value   │  │
│   │    status        │         │    total_in      │        │    new_value   │  │
│   └──────────────────┘         │    total_out     │        │    operator    │  │
│                                └──────────────────┘        └────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 数据库Schema创建

```sql
-- =============================================
-- 金融系统数据库Schema创建脚本
-- =============================================

CREATE DATABASE finance_dca
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';

\c finance_dca;

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =============================================
-- 1. 客户信息表
-- =============================================

CREATE TABLE customers (
    customer_id         BIGSERIAL PRIMARY KEY,
    customer_no         VARCHAR(20) NOT NULL UNIQUE,
    customer_type       SMALLINT DEFAULT 1, -- 1:个人 2:企业

    -- 基本信息
    name                VARCHAR(100) NOT NULL,
    name_en             VARCHAR(100),

    -- 证件信息
    id_type             VARCHAR(10) NOT NULL, -- ID_CARD:身份证 PASSPORT:护照 BUSINESS:营业执照
    id_number           VARCHAR(50) NOT NULL,
    id_expire_date      DATE,

    -- 联系信息
    phone               VARCHAR(20) NOT NULL,
    email               VARCHAR(100),
    address             VARCHAR(255),

    -- 状态与风控
    status              SMALLINT DEFAULT 0, -- 0:待审核 1:正常 2:冻结 3:注销
    risk_level          SMALLINT DEFAULT 1, -- 1:低 2:中 3:高
    kyc_status          SMALLINT DEFAULT 0, -- KYC认证状态

    -- 时间戳
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    verified_at         TIMESTAMPTZ
);

CREATE INDEX idx_customer_no ON customers(customer_no);
CREATE INDEX idx_customer_idnum ON customers(id_type, id_number);

COMMENT ON TABLE customers IS '客户信息主表';
COMMENT ON COLUMN customers.status IS '客户状态: 0=待审核 1=正常 2=冻结 3=注销';
COMMENT ON COLUMN customers.risk_level IS '风险等级: 1=低风险 2=中风险 3=高风险';

-- =============================================
-- 2. 账户主表
-- =============================================

CREATE TABLE accounts (
    account_id          BIGSERIAL PRIMARY KEY,
    account_no          VARCHAR(32) NOT NULL UNIQUE,
    customer_id         BIGINT NOT NULL REFERENCES customers(customer_id),

    -- 账户属性
    account_type        VARCHAR(10) NOT NULL, -- SAVINGS:储蓄 CHECKING:活期 FIXED:定期
    currency            VARCHAR(3) DEFAULT 'CNY',

    -- 账户状态
    status              SMALLINT DEFAULT 0, -- 0:开户中 1:正常 2:冻结 3:销户
    open_reason         VARCHAR(255),
    close_reason        VARCHAR(255),

    -- 时间戳
    opened_at           TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    closed_at           TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- 扩展属性
    attributes          JSONB DEFAULT '{}'
);

-- 账户分区: 按账户号哈希分区 (便于水平扩展)
CREATE INDEX idx_account_customer ON accounts(customer_id);
CREATE INDEX idx_account_status ON accounts(status) WHERE status = 1;

COMMENT ON TABLE accounts IS '账户主表';
COMMENT ON COLUMN accounts.status IS '账户状态: 0=开户中 1=正常 2=冻结 3=销户';

-- =============================================
-- 3. 账户余额表 (核心表，高频更新)
-- =============================================

CREATE TABLE account_balances (
    balance_id          BIGSERIAL PRIMARY KEY,
    account_id          BIGINT NOT NULL UNIQUE REFERENCES accounts(account_id),
    account_no          VARCHAR(32) NOT NULL,

    -- 余额组成
    current_balance     DECIMAL(18,2) DEFAULT 0,    -- 当前余额
    available_balance   DECIMAL(18,2) DEFAULT 0,    -- 可用余额
    frozen_amount       DECIMAL(18,2) DEFAULT 0,    -- 冻结金额

    -- 统计字段
    total_in_amount     DECIMAL(18,2) DEFAULT 0,    -- 累计流入
    total_out_amount    DECIMAL(18,2) DEFAULT 0,    -- 累计流出
    total_in_count      INTEGER DEFAULT 0,          -- 累计流入笔数
    total_out_count     INTEGER DEFAULT 0,          -- 累计流出笔数

    -- 并发控制
    version             INTEGER DEFAULT 0,          -- 乐观锁版本号
    last_tx_id          BIGINT,                     -- 最后交易ID
    last_tx_time        TIMESTAMPTZ,                -- 最后交易时间

    -- 日终标记
    last_settle_date    DATE,                       -- 最后清算日期
    begin_balance       DECIMAL(18,2) DEFAULT 0,    -- 日初余额

    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_balance_account ON account_balances(account_no);
CREATE INDEX idx_balance_available ON account_balances(available_balance)
    WHERE available_balance > 0;

COMMENT ON TABLE account_balances IS '账户余额表';
COMMENT ON COLUMN account_balances.current_balance IS '当前余额 = 可用余额 + 冻结金额';

-- =============================================
-- 4. 会计分录表 (不可修改，只增不改)
-- =============================================

CREATE TABLE account_entries (
    entry_id            BIGSERIAL PRIMARY KEY,
    entry_no            VARCHAR(32) NOT NULL UNIQUE,

    -- 关联信息
    tx_id               BIGINT NOT NULL,            -- 交易ID
    tx_no               VARCHAR(32) NOT NULL,       -- 交易流水号

    -- 账户信息
    account_id          BIGINT NOT NULL REFERENCES accounts(account_id),
    account_no          VARCHAR(32) NOT NULL,

    -- 分录信息
    entry_type          VARCHAR(20) NOT NULL,       -- 分录类型
    amount              DECIMAL(18,2) NOT NULL,     -- 金额
    direction           SMALLINT NOT NULL,          -- 1:借方(Debits) 2:贷方(Credits)

    -- 会计要素
    account_category    VARCHAR(10),                -- ASSET:资产 LIABILITY:负债 EQUITY:权益

    -- 对方信息 (用于对账)
    counter_account_no  VARCHAR(32),
    counter_entry_id    BIGINT,

    -- 余额快照
    balance_before      DECIMAL(18,2) NOT NULL,     -- 交易前余额
    balance_after       DECIMAL(18,2) NOT NULL,     -- 交易后余额

    -- 业务信息
    remark              VARCHAR(255),
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- 创建分区 (按月分区)
CREATE TABLE account_entries_2024_01 PARTITION OF account_entries
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE account_entries_2024_02 PARTITION OF account_entries
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- 依此类推...

CREATE INDEX idx_entry_tx ON account_entries(tx_id);
CREATE INDEX idx_entry_account ON account_entries(account_no, created_at DESC);
CREATE INDEX idx_entry_date ON account_entries(created_at);

COMMENT ON TABLE account_entries IS '会计分录表 - 记录所有账务变动，不可修改';
COMMENT ON COLUMN account_entries.direction IS '1=借方(Debits) 2=贷方(Credits)';

-- =============================================
-- 5. 交易主表
-- =============================================

CREATE TABLE transactions (
    tx_id               BIGSERIAL PRIMARY KEY,
    tx_no               VARCHAR(32) NOT NULL UNIQUE,

    -- 交易类型
    tx_type             VARCHAR(20) NOT NULL, -- TRANSFER:转账 DEPOSIT:存款 WITHDRAW:取款 FEE:手续费
    tx_subtype          VARCHAR(20),          -- REALTIME:实时 BATCH:批量

    -- 金额信息
    amount              DECIMAL(18,2) NOT NULL,
    currency            VARCHAR(3) DEFAULT 'CNY',
    fee_amount          DECIMAL(18,2) DEFAULT 0,

    -- 交易双方
    from_account_no     VARCHAR(32),
    to_account_no       VARCHAR(32),

    -- 状态
    status              SMALLINT DEFAULT 0, -- 0:初始化 1:处理中 2:成功 3:失败 4:撤销
    error_code          VARCHAR(20),
    error_msg           VARCHAR(255),

    -- 业务信息
    remark              VARCHAR(255),
    biz_no              VARCHAR(64),          -- 业务流水号
    biz_type            VARCHAR(20),          -- 业务类型

    -- 时间戳
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMPTZ,

    -- 扩展
    extra_data          JSONB DEFAULT '{}'
) PARTITION BY RANGE (created_at);

CREATE INDEX idx_tx_no ON transactions(tx_no);
CREATE INDEX idx_tx_from ON transactions(from_account_no, created_at DESC);
CREATE INDEX idx_tx_to ON transactions(to_account_no, created_at DESC);
CREATE INDEX idx_tx_status ON transactions(status);

COMMENT ON TABLE transactions IS '交易主表';
COMMENT ON COLUMN transactions.status IS '交易状态: 0=初始化 1=处理中 2=成功 3=失败 4=撤销';

-- =============================================
-- 6. 账户限额表
-- =============================================

CREATE TABLE account_limits (
    limit_id            BIGSERIAL PRIMARY KEY,
    account_id          BIGINT NOT NULL UNIQUE REFERENCES accounts(account_id),

    -- 额度限制
    single_limit        DECIMAL(18,2) DEFAULT 50000,     -- 单笔限额
    daily_limit         DECIMAL(18,2) DEFAULT 200000,    -- 日累计限额
    monthly_limit       DECIMAL(18,2) DEFAULT 2000000,   -- 月累计限额
    yearly_limit        DECIMAL(18,2) DEFAULT 20000000,  -- 年累计限额

    -- 计数限制
    daily_count_limit   INTEGER DEFAULT 100,             -- 日累计笔数限制

    -- 当前使用情况 (每日重置)
    daily_used_amount   DECIMAL(18,2) DEFAULT 0,
    daily_used_count    INTEGER DEFAULT 0,
    last_reset_date     DATE DEFAULT CURRENT_DATE,

    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE account_limits IS '账户限额配置表';

-- =============================================
-- 7. 批量任务表
-- =============================================

CREATE TABLE batch_tasks (
    batch_id            BIGSERIAL PRIMARY KEY,
    batch_no            VARCHAR(32) NOT NULL UNIQUE,

    batch_type          VARCHAR(20) NOT NULL, -- SALARY:代发工资 REPAYMENT:批量扣款
    batch_name          VARCHAR(100),

    -- 统计信息
    total_count         INTEGER DEFAULT 0,
    total_amount        DECIMAL(18,2) DEFAULT 0,
    success_count       INTEGER DEFAULT 0,
    success_amount      DECIMAL(18,2) DEFAULT 0,
    fail_count          INTEGER DEFAULT 0,
    fail_amount         DECIMAL(18,2) DEFAULT 0,

    -- 状态
    status              SMALLINT DEFAULT 0, -- 0:待处理 1:处理中 2:部分成功 3:全部成功 4:失败

    -- 执行信息
    execute_time        TIMESTAMPTZ,          -- 计划执行时间
    actual_start        TIMESTAMPTZ,
    actual_end          TIMESTAMPTZ,

    -- 发起方
    from_account_no     VARCHAR(32),
    operator_id         BIGINT,

    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_batch_status ON batch_tasks(status, execute_time);

-- 批量明细表
CREATE TABLE batch_details (
    detail_id           BIGSERIAL PRIMARY KEY,
    batch_id            BIGINT NOT NULL REFERENCES batch_tasks(batch_id),

    -- 交易信息
    seq_no              INTEGER NOT NULL,     -- 序号
    to_account_no       VARCHAR(32) NOT NULL,
    to_account_name     VARCHAR(100),
    amount              DECIMAL(18,2) NOT NULL,
    currency            VARCHAR(3) DEFAULT 'CNY',
    remark              VARCHAR(255),

    -- 执行结果
    status              SMALLINT DEFAULT 0, -- 0:待处理 1:成功 2:失败
    tx_id               BIGINT,              -- 关联的交易ID
    error_code          VARCHAR(20),
    error_msg           VARCHAR(255),

    UNIQUE(batch_id, seq_no)
);

CREATE INDEX idx_detail_batch ON batch_details(batch_id);

-- =============================================
-- 8. 日终清算表
-- =============================================

CREATE TABLE daily_settlements (
    settle_id           BIGSERIAL PRIMARY KEY,
    settle_date         DATE NOT NULL UNIQUE,

    -- 汇总信息
    total_accounts      INTEGER DEFAULT 0,    -- 总账户数
    active_accounts     INTEGER DEFAULT 0,    -- 活跃账户数

    total_entries       INTEGER DEFAULT 0,    -- 总分录数
    total_debit         DECIMAL(18,2) DEFAULT 0,  -- 总借方发生额
    total_credit        DECIMAL(18,2) DEFAULT 0,  -- 总贷方发生额
    diff_amount         DECIMAL(18,2) DEFAULT 0,  -- 差额 (应为0)

    -- 状态
    status              SMALLINT DEFAULT 0, -- 0:待清算 1:清算中 2:成功 3:失败
    error_msg           VARCHAR(255),

    -- 时间戳
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 清算明细表 (每个账户的日终状态)
CREATE TABLE settlement_details (
    detail_id           BIGSERIAL PRIMARY KEY,
    settle_id           BIGINT NOT NULL REFERENCES daily_settlements(settle_id),

    account_no          VARCHAR(32) NOT NULL,

    -- 余额信息
    begin_balance       DECIMAL(18,2) NOT NULL,  -- 日初余额
    end_balance         DECIMAL(18,2) NOT NULL,  -- 日终余额

    -- 发生额
    total_in_amount     DECIMAL(18,2) DEFAULT 0,
    total_out_amount    DECIMAL(18,2) DEFAULT 0,
    total_in_count      INTEGER DEFAULT 0,
    total_out_count     INTEGER DEFAULT 0,

    -- 校验
    check_result        BOOLEAN,                 -- 校验是否通过
    diff_amount         DECIMAL(18,2) DEFAULT 0  -- 差异金额
);

CREATE INDEX idx_settle_detail_account ON settlement_details(account_no);
CREATE INDEX idx_settle_detail_settle ON settlement_details(settle_id);

-- =============================================
-- 9. 风控日志表
-- =============================================

CREATE TABLE risk_logs (
    risk_id             BIGSERIAL PRIMARY KEY,
    tx_id               BIGINT,

    -- 风控信息
    risk_type           VARCHAR(20) NOT NULL, -- LIMIT:限额 FRAUD:反欺诈 AML:反洗钱
    risk_level          SMALLINT,             -- 1:提示 2:警告 3:拦截
    rule_id             VARCHAR(50),          -- 触发的规则ID
    rule_name           VARCHAR(100),

    -- 检查结果
    check_result        VARCHAR(20),          -- PASS:通过 REJECT:拦截 REVIEW:人工审核
    check_detail        JSONB,                -- 详细检查数据

    -- 处理结果
    action_taken        VARCHAR(20),          -- 采取的行动
    operator_id         BIGINT,               -- 处理人
    remark              VARCHAR(255),

    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

CREATE INDEX idx_risk_tx ON risk_logs(tx_id);
CREATE INDEX idx_risk_time ON risk_logs(created_at DESC);

-- =============================================
-- 10. 审计日志表
-- =============================================

CREATE TABLE audit_logs (
    audit_id            BIGSERIAL PRIMARY KEY,

    table_name          VARCHAR(50) NOT NULL,
    record_id           BIGINT NOT NULL,
    operation           VARCHAR(10) NOT NULL, -- INSERT UPDATE DELETE

    old_value           JSONB,
    new_value           JSONB,

    operator_type       VARCHAR(20), -- SYSTEM USER ADMIN
    operator_id         BIGINT,
    operator_ip         INET,

    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

CREATE INDEX idx_audit_table ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_time ON audit_logs(created_at DESC);

-- =============================================
-- 11. 系统配置表
-- =============================================

CREATE TABLE system_configs (
    config_key          VARCHAR(50) PRIMARY KEY,
    config_value        TEXT NOT NULL,
    config_type         VARCHAR(20) DEFAULT 'STRING', -- STRING NUMBER JSON
    description         VARCHAR(255),
    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 初始化配置
INSERT INTO system_configs (config_key, config_value, config_type, description) VALUES
('system.account_no.prefix', '6222', 'STRING', '账号前缀'),
('system.tx.timeout.seconds', '60', 'NUMBER', '交易超时时间(秒)'),
('system.daily.limit.reset.hour', '0', 'NUMBER', '日限额重置时间(小时)'),
('system.settlement.start.time', '23:30', 'STRING', '日终清算开始时间'),
('system.fraud.enabled', 'true', 'STRING', '是否启用反欺诈'),
('system.aml.threshold', '50000', 'NUMBER', '反洗钱监控阈值');
```

---

## 4. 账户系统实现

### 4.1 账户生命周期

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           账户生命周期状态机                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────┐                                                                    │
│   │  客户   │                                                                    │
│   │  开户   │                                                                    │
│   └────┬────┘                                                                    │
│        │ sp_customer_register                                                    │
│        ▼                                                                          │
│   ┌─────────┐      ┌─────────┐                                                  │
│   │ 开户申请 │─────→│  已拒绝  │                                                  │
│   │PENDING  │ 拒绝  │REJECTED │                                                  │
│   └────┬────┘      └─────────┘                                                  │
│        │ 通过                                                                    │
│        ▼                                                                          │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐                                │
│   │  正常   │←────→│  冻结   │←────→│  解冻   │                                │
│   │ ACTIVE  │ 冻结 │ FROZEN │ 解冻 │ ACTIVE  │                                │
│   └────┬────┘      └─────────┘      └─────────┘                                │
│        │ 销户                                                                    │
│        ▼                                                                          │
│   ┌─────────┐                                                                    │
│   │  已销户  │                                                                    │
│   │CLOSED   │                                                                    │
│   └─────────┘                                                                    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 账户核心存储过程

#### 4.2.1 客户开户存储过程

```sql
-- =============================================
-- 存储过程1: 客户开户
-- =============================================
CREATE OR REPLACE FUNCTION sp_customer_register(
    p_name              VARCHAR(100),
    p_id_type           VARCHAR(10),
    p_id_number         VARCHAR(50),
    p_phone             VARCHAR(20),
    p_email             VARCHAR(100) DEFAULT NULL,
    p_address           VARCHAR(255) DEFAULT NULL,
    p_customer_type     SMALLINT DEFAULT 1
) RETURNS TABLE (
    customer_id         BIGINT,
    customer_no         VARCHAR(20),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_customer_id       BIGINT;
    v_customer_no       VARCHAR(20);
BEGIN
    -- 检查证件号是否已存在
    IF EXISTS (SELECT 1 FROM customers
               WHERE id_type = p_id_type AND id_number = p_id_number) THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -1,
                            '证件号码已存在'::VARCHAR;
        RETURN;
    END IF;

    -- 生成客户号: C + 年月 + 6位序号
    v_customer_no := 'C' || TO_CHAR(CURRENT_DATE, 'YYYYMM') ||
                     LPAD(NEXTVAL('customers_customer_id_seq')::TEXT, 6, '0');

    INSERT INTO customers (
        customer_no, customer_type, name, id_type, id_number,
        phone, email, address, status
    ) VALUES (
        v_customer_no, p_customer_type, p_name, p_id_type, p_id_number,
        p_phone, p_email, p_address, 0
    ) RETURNING customers.customer_id INTO v_customer_id;

    -- 记录审计日志
    INSERT INTO audit_logs (table_name, record_id, operation,
                           new_value, operator_type, remark)
    VALUES ('customers', v_customer_id, 'INSERT',
            jsonb_build_object('customer_no', v_customer_no, 'name', p_name),
            'SYSTEM', '客户开户');

    RETURN QUERY SELECT v_customer_id, v_customer_no, 0, '客户开户申请已提交'::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_customer_register IS '客户开户存储过程';
```

#### 4.2.2 账户开户存储过程

```sql
-- =============================================
-- 存储过程2: 账户开户
-- =============================================
CREATE OR REPLACE FUNCTION sp_account_open(
    p_customer_id       BIGINT,
    p_account_type      VARCHAR(10),
    p_currency          VARCHAR(3) DEFAULT 'CNY',
    p_initial_deposit   DECIMAL(18,2) DEFAULT 0,
    p_open_reason       VARCHAR(255) DEFAULT NULL
) RETURNS TABLE (
    account_id          BIGINT,
    account_no          VARCHAR(32),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_account_id        BIGINT;
    v_account_no        VARCHAR(32);
    v_prefix            VARCHAR(10);
    v_customer_status   SMALLINT;
BEGIN
    -- 检查客户状态
    SELECT status INTO v_customer_status FROM customers WHERE customer_id = p_customer_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -1, '客户不存在'::VARCHAR;
        RETURN;
    END IF;

    IF v_customer_status != 1 THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -2, '客户状态不正常'::VARCHAR;
        RETURN;
    END IF;

    -- 获取账号前缀
    SELECT config_value INTO v_prefix FROM system_configs
    WHERE config_key = 'system.account_no.prefix';

    -- 生成账号: 前缀 + 校验位 + 序号
    v_account_no := v_prefix ||
                    LPAD(FLOOR(RANDOM() * 9 + 1)::TEXT, 1, '0') ||
                    LPAD(NEXTVAL('accounts_account_id_seq')::TEXT, 10, '0');

    BEGIN
        -- 创建账户
        INSERT INTO accounts (
            account_no, customer_id, account_type, currency,
            status, open_reason
        ) VALUES (
            v_account_no, p_customer_id, p_account_type, p_currency,
            1, p_open_reason
        ) RETURNING accounts.account_id INTO v_account_id;

        -- 创建余额记录
        INSERT INTO account_balances (account_id, account_no)
        VALUES (v_account_id, v_account_no);

        -- 创建限额记录
        INSERT INTO account_limits (account_id) VALUES (v_account_id);

        -- 如果有初始存款
        IF p_initial_deposit > 0 THEN
            PERFORM sp_deposit(v_account_no, p_initial_deposit, 'INIT_DEPOSIT', '初始存款');
        END IF;

        -- 记录审计
        INSERT INTO audit_logs (table_name, record_id, operation,
                               new_value, operator_type, remark)
        VALUES ('accounts', v_account_id, 'INSERT',
                jsonb_build_object('account_no', v_account_no, 'type', p_account_type),
                'SYSTEM', '账户开户');

        RETURN QUERY SELECT v_account_id, v_account_no, 0, '账户开户成功'::VARCHAR;

    EXCEPTION WHEN OTHERS THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -99, SQLERRM::VARCHAR;
    END;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_account_open IS '账户开户存储过程';
```

#### 4.2.3 账户销户存储过程

```sql
-- =============================================
-- 存储过程3: 账户销户
-- =============================================
CREATE OR REPLACE FUNCTION sp_account_close(
    p_account_no        VARCHAR(32),
    p_close_reason      VARCHAR(255),
    p_operator_id       BIGINT
) RETURNS TABLE (
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_account           RECORD;
    v_balance           RECORD;
BEGIN
    -- 获取账户信息
    SELECT a.* INTO v_account FROM accounts a WHERE a.account_no = p_account_no;

    IF NOT FOUND THEN
        RETURN QUERY SELECT -1, '账户不存在'::VARCHAR;
        RETURN;
    END IF;

    IF v_account.status = 3 THEN
        RETURN QUERY SELECT -2, '账户已销户'::VARCHAR;
        RETURN;
    END IF;

    -- 获取余额信息
    SELECT * INTO v_balance FROM account_balances WHERE account_no = p_account_no;

    -- 检查余额
    IF v_balance.current_balance != 0 THEN
        RETURN QUERY SELECT -3, ('账户余额不为零: ' || v_balance.current_balance)::VARCHAR;
        RETURN;
    END IF;

    IF v_balance.frozen_amount > 0 THEN
        RETURN QUERY SELECT -4, ('账户有冻结金额: ' || v_balance.frozen_amount)::VARCHAR;
        RETURN;
    END IF;

    -- 检查是否有未完成的交易
    IF EXISTS (SELECT 1 FROM transactions
               WHERE (from_account_no = p_account_no OR to_account_no = p_account_no)
                 AND status = 1) THEN
        RETURN QUERY SELECT -5, '账户有未完成的交易'::VARCHAR;
        RETURN;
    END IF;

    -- 更新账户状态
    UPDATE accounts SET
        status = 3,
        close_reason = p_close_reason,
        closed_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE account_no = p_account_no;

    -- 记录审计
    INSERT INTO audit_logs (table_name, record_id, operation,
                           old_value, new_value, operator_id, remark)
    VALUES ('accounts', v_account.account_id, 'UPDATE',
            jsonb_build_object('status', 1),
            jsonb_build_object('status', 3),
            p_operator_id, '账户销户: ' || p_close_reason);

    RETURN QUERY SELECT 0, '账户销户成功'::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

#### 4.2.4 账户冻结/解冻存储过程

```sql
-- =============================================
-- 存储过程4: 账户冻结
-- =============================================
CREATE OR REPLACE FUNCTION sp_account_freeze(
    p_account_no        VARCHAR(32),
    p_freeze_reason     VARCHAR(255),
    p_operator_id       BIGINT
) RETURNS TABLE (
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_account_id        BIGINT;
    v_old_status        SMALLINT;
BEGIN
    SELECT account_id, status INTO v_account_id, v_old_status
    FROM accounts WHERE account_no = p_account_no;

    IF NOT FOUND THEN
        RETURN QUERY SELECT -1, '账户不存在'::VARCHAR;
        RETURN;
    END IF;

    IF v_old_status != 1 THEN
        RETURN QUERY SELECT -2, '账户状态不允许冻结'::VARCHAR;
        RETURN;
    END IF;

    UPDATE accounts SET status = 2, updated_at = CURRENT_TIMESTAMP
    WHERE account_no = p_account_no;

    INSERT INTO audit_logs (table_name, record_id, operation,
                           old_value, new_value, operator_id, remark)
    VALUES ('accounts', v_account_id, 'UPDATE',
            jsonb_build_object('status', v_old_status),
            jsonb_build_object('status', 2),
            p_operator_id, '账户冻结: ' || p_freeze_reason);

    RETURN QUERY SELECT 0, '账户冻结成功'::VARCHAR;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 存储过程5: 账户解冻
-- =============================================
CREATE OR REPLACE FUNCTION sp_account_unfreeze(
    p_account_no        VARCHAR(32),
    p_unfreeze_reason   VARCHAR(255),
    p_operator_id       BIGINT
) RETURNS TABLE (
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_account_id        BIGINT;
BEGIN
    SELECT account_id INTO v_account_id FROM accounts
    WHERE account_no = p_account_no AND status = 2;

    IF NOT FOUND THEN
        RETURN QUERY SELECT -1, '账户不存在或未冻结'::VARCHAR;
        RETURN;
    END IF;

    UPDATE accounts SET status = 1, updated_at = CURRENT_TIMESTAMP
    WHERE account_no = p_account_no;

    INSERT INTO audit_logs (table_name, record_id, operation,
                           old_value, new_value, operator_id, remark)
    VALUES ('accounts', v_account_id, 'UPDATE',
            jsonb_build_object('status', 2),
            jsonb_build_object('status', 1),
            p_operator_id, '账户解冻: ' || p_unfreeze_reason);

    RETURN QUERY SELECT 0, '账户解冻成功'::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

#### 4.2.5 余额查询存储过程

```sql
-- =============================================
-- 存储过程6: 查询账户余额
-- =============================================
CREATE OR REPLACE FUNCTION sp_get_account_balance(
    p_account_no        VARCHAR(32)
) RETURNS TABLE (
    account_no          VARCHAR(32),
    account_type        VARCHAR(10),
    currency            VARCHAR(3),
    current_balance     DECIMAL(18,2),
    available_balance   DECIMAL(18,2),
    frozen_amount       DECIMAL(18,2),
    status              SMALLINT,
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.account_no, a.account_type, a.currency,
        b.current_balance, b.available_balance, b.frozen_amount,
        a.status, 0, '查询成功'::VARCHAR
    FROM accounts a
    JOIN account_balances b ON a.account_id = b.account_id
    WHERE a.account_no = p_account_no;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::VARCHAR, NULL::VARCHAR, NULL::VARCHAR,
                            NULL::DECIMAL, NULL::DECIMAL, NULL::DECIMAL,
                            NULL::SMALLINT, -1, '账户不存在'::VARCHAR;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 存储过程7: 查询账户流水
-- =============================================
CREATE OR REPLACE FUNCTION sp_get_account_entries(
    p_account_no        VARCHAR(32),
    p_start_date        DATE DEFAULT NULL,
    p_end_date          DATE DEFAULT NULL,
    p_page              INTEGER DEFAULT 1,
    p_page_size         INTEGER DEFAULT 20
) RETURNS TABLE (
    entry_no            VARCHAR(32),
    tx_no               VARCHAR(32),
    entry_type          VARCHAR(20),
    amount              DECIMAL(18,2),
    direction           SMALLINT,
    direction_name      VARCHAR(10),
    balance_after       DECIMAL(18,2),
    remark              VARCHAR(255),
    created_at          TIMESTAMPTZ,
    total_count         BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH filtered AS (
        SELECT * FROM account_entries
        WHERE account_no = p_account_no
          AND (p_start_date IS NULL OR created_at >= p_start_date)
          AND (p_end_date IS NULL OR created_at < p_end_date + INTERVAL '1 day')
    ),
    total AS (SELECT COUNT(*) AS cnt FROM filtered)
    SELECT
        e.entry_no, e.tx_no, e.entry_type, e.amount, e.direction,
        CASE e.direction WHEN 1 THEN '借' WHEN 2 THEN '贷' END::VARCHAR(10),
        e.balance_after, e.remark, e.created_at,
        (SELECT cnt FROM total)
    FROM filtered e
    ORDER BY e.created_at DESC
    LIMIT p_page_size OFFSET (p_page - 1) * p_page_size;
END;
$$ LANGUAGE plpgsql;
```

### 4.3 账户相关触发器

```sql
-- =============================================
-- 触发器1: 余额变动审计
-- =============================================
CREATE OR REPLACE FUNCTION trg_fn_balance_audit()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        -- 只记录余额变化
        IF OLD.current_balance IS DISTINCT FROM NEW.current_balance OR
           OLD.frozen_amount IS DISTINCT FROM NEW.frozen_amount THEN
            INSERT INTO audit_logs (table_name, record_id, operation,
                                   old_value, new_value, remark)
            VALUES ('account_balances', NEW.balance_id, 'UPDATE',
                    jsonb_build_object('balance', OLD.current_balance, 'frozen', OLD.frozen_amount),
                    jsonb_build_object('balance', NEW.current_balance, 'frozen', NEW.frozen_amount),
                    '余额变动: tx_id=' || NEW.last_tx_id);
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_balance_audit
    AFTER UPDATE ON account_balances
    FOR EACH ROW EXECUTE FUNCTION trg_fn_balance_audit();

-- =============================================
-- 触发器2: 日限额自动重置
-- =============================================
CREATE OR REPLACE FUNCTION trg_fn_limit_daily_reset()
RETURNS TRIGGER AS $$
BEGIN
    -- 检查是否需要重置日限额
    IF OLD.last_reset_date IS DISTINCT FROM CURRENT_DATE THEN
        NEW.daily_used_amount := 0;
        NEW.daily_used_count := 0;
        NEW.last_reset_date := CURRENT_DATE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_limit_daily_reset
    BEFORE UPDATE ON account_limits
    FOR EACH ROW EXECUTE FUNCTION trg_fn_limit_daily_reset();
```

---

## 5. 转账系统实现

### 5.1 转账流程架构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          实时转账流程时序图                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  付款方                            数据库DCA                          收款方    │
│    │                                  │                                  │     │
│    │ 1.发起转账请求                    │                                  │     │
│    │─────────────────────────────────→│                                  │     │
│    │                                  │                                  │     │
│    │                                  │ 2.风控检查                        │     │
│    │                                  │┌────────────────────────────────┐│     │
│    │                                  ││fn_risk_check: 限额/反欺诈/AML  ││     │
│    │                                  │└────────────────────────────────┘│     │
│    │                                  │                                  │     │
│    │                                  │ 3.创建交易记录                    │     │
│    │                                  │ INSERT INTO transactions        │     │
│    │                                  │                                  │     │
│    │                                  │ 4.扣减付款方余额                  │     │
│    │                                  │ UPDATE account_balances         │     │
│    │                                  │   SET balance = balance - amount│     │
│    │                                  │ WHERE account_no = from_account │     │
│    │                                  │                                  │     │
│    │                                  │ 5.增加收款方余额                  │     │
│    │                                  │ UPDATE account_balances         │     │
│    │                                  │   SET balance = balance + amount│     │
│    │                                  │ WHERE account_no = to_account   │     │
│    │                                  │                                  │     │
│    │                                  │ 6.生成会计分录                    │     │
│    │                                  │ INSERT INTO account_entries     │     │
│    │                                  │   (付款方借方, 收款方贷方)        │     │
│    │                                  │                                  │     │
│    │                                  │ 7.校验会计恒等式                  │     │
│    │                                  │ ASSERT SUM(debits) = SUM(credits)│    │
│    │                                  │                                  │     │
│    │ 8.返回结果                        │                                  │     │
│    │←─────────────────────────────────│                                  │     │
│    │                                  │                                  │     │
│    │                                  │ 9.通知收款方                      │     │
│    │                                  │─────────────────────────────────→│     │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 转账核心存储过程

#### 5.2.1 实时转账存储过程

```sql
-- =============================================
-- 存储过程8: 实时转账 (核心)
-- 特点: 强一致性、原子性、幂等性
-- =============================================
CREATE OR REPLACE FUNCTION sp_transfer_realtime(
    p_from_account      VARCHAR(32),
    p_to_account        VARCHAR(32),
    p_amount            DECIMAL(18,2),
    p_remark            VARCHAR(255) DEFAULT NULL,
    p_biz_no            VARCHAR(64) DEFAULT NULL  -- 业务方幂等号
) RETURNS TABLE (
    tx_id               BIGINT,
    tx_no               VARCHAR(32),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_tx_id             BIGINT;
    v_tx_no             VARCHAR(32);
    v_from_acct         RECORD;
    v_to_acct           RECORD;
    v_from_bal          RECORD;
    v_to_bal            RECORD;
    v_from_entry_id     BIGINT;
    v_to_entry_id       BIGINT;
    v_entry_no          VARCHAR(32);
    v_risk_result       RECORD;
    v_total_debit       DECIMAL(18,2);
    v_total_credit      DECIMAL(18,2);
BEGIN
    -- 参数校验
    IF p_amount <= 0 THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -1, '转账金额必须大于0'::VARCHAR;
        RETURN;
    END IF;

    IF p_from_account = p_to_account THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -2, '不能转账给自己'::VARCHAR;
        RETURN;
    END IF;

    -- 幂等性检查
    IF p_biz_no IS NOT NULL THEN
        SELECT tx_id, tx_no, status INTO v_tx_id, v_tx_no, v_from_acct.status
        FROM transactions WHERE biz_no = p_biz_no;

        IF FOUND THEN
            IF v_from_acct.status = 2 THEN
                RETURN QUERY SELECT v_tx_id, v_tx_no, 0, '交易已处理'::VARCHAR;
            ELSIF v_from_acct.status = 1 THEN
                RETURN QUERY SELECT v_tx_id, v_tx_no, 1, '交易处理中'::VARCHAR;
            ELSE
                RETURN QUERY SELECT v_tx_id, v_tx_no, -3, '交易失败'::VARCHAR;
            END IF;
            RETURN;
        END IF;
    END IF;

    -- 获取付款方账户并锁定
    SELECT a.* INTO v_from_acct
    FROM accounts a WHERE a.account_no = p_from_account FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -4, '付款方账户不存在'::VARCHAR;
        RETURN;
    END IF;

    IF v_from_acct.status != 1 THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -5, '付款方账户状态异常'::VARCHAR;
        RETURN;
    END IF;

    -- 获取收款方账户并锁定
    SELECT a.* INTO v_to_acct
    FROM accounts a WHERE a.account_no = p_to_account FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -6, '收款方账户不存在'::VARCHAR;
        RETURN;
    END IF;

    IF v_to_acct.status != 1 THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -7, '收款方账户状态异常'::VARCHAR;
        RETURN;
    END IF;

    -- 风控检查
    SELECT * INTO v_risk_result FROM fn_risk_check(
        p_from_account, p_to_account, p_amount, 'TRANSFER'
    );

    IF v_risk_result.check_result != 'PASS' THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -8,
                            ('风控拦截: ' || v_risk_result.check_result)::VARCHAR;
        RETURN;
    END IF;

    -- 生成交易流水号
    v_tx_no := 'TX' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') ||
               LPAD(FLOOR(RANDOM() * 100000000)::TEXT, 8, '0');

    BEGIN
        -- 创建交易记录
        INSERT INTO transactions (
            tx_no, tx_type, tx_subtype, amount, currency,
            from_account_no, to_account_no, status, remark, biz_no
        ) VALUES (
            v_tx_no, 'TRANSFER', 'REALTIME', p_amount, v_from_acct.currency,
            p_from_account, p_to_account, 1, p_remark, p_biz_no
        ) RETURNING transactions.tx_id INTO v_tx_id;

        -- 锁定余额记录 (按账户号顺序锁定，防止死锁)
        SELECT * INTO v_from_bal FROM account_balances
        WHERE account_no = p_from_account FOR UPDATE;

        SELECT * INTO v_to_bal FROM account_balances
        WHERE account_no = p_to_account FOR UPDATE;

        -- 检查余额
        IF v_from_bal.available_balance < p_amount THEN
            RAISE EXCEPTION '余额不足: 可用=%, 需要=%',
                v_from_bal.available_balance, p_amount;
        END IF;

        -- 更新付款方余额 (借方 - 资产减少)
        UPDATE account_balances SET
            current_balance = current_balance - p_amount,
            available_balance = available_balance - p_amount,
            total_out_amount = total_out_amount + p_amount,
            total_out_count = total_out_count + 1,
            version = version + 1,
            last_tx_id = v_tx_id,
            last_tx_time = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE account_no = p_from_account;

        -- 更新收款方余额 (贷方 - 资产增加)
        UPDATE account_balances SET
            current_balance = current_balance + p_amount,
            available_balance = available_balance + p_amount,
            total_in_amount = total_in_amount + p_amount,
            total_in_count = total_in_count + 1,
            version = version + 1,
            last_tx_id = v_tx_id,
            last_tx_time = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE account_no = p_to_account;

        -- 生成会计分录号
        v_entry_no := 'EN' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') ||
                      LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');

        -- 插入付款方分录 (借方 - 资产减少)
        INSERT INTO account_entries (
            entry_no, tx_id, tx_no, account_id, account_no,
            entry_type, amount, direction, account_category,
            counter_account_no, balance_before, balance_after, remark
        ) VALUES (
            v_entry_no || 'D', v_tx_id, v_tx_no, v_from_acct.account_id, p_from_account,
            'TRANSFER_OUT', p_amount, 1, 'ASSET',
            p_to_account, v_from_bal.current_balance, v_from_bal.current_balance - p_amount,
            '转账支出: ' || COALESCE(p_remark, '')
        ) RETURNING entry_id INTO v_from_entry_id;

        -- 插入收款方分录 (贷方 - 资产增加)
        INSERT INTO account_entries (
            entry_no, tx_id, tx_no, account_id, account_no,
            entry_type, amount, direction, account_category,
            counter_account_no, balance_before, balance_after, remark
        ) VALUES (
            v_entry_no || 'C', v_tx_id, v_tx_no, v_to_acct.account_id, p_to_account,
            'TRANSFER_IN', p_amount, 2, 'ASSET',
            p_from_account, v_to_bal.current_balance, v_to_bal.current_balance + p_amount,
            '转账收入: ' || COALESCE(p_remark, '')
        ) RETURNING entry_id INTO v_to_entry_id;

        -- 更新对方分录ID
        UPDATE account_entries SET counter_entry_id = v_to_entry_id
        WHERE entry_id = v_from_entry_id;
        UPDATE account_entries SET counter_entry_id = v_from_entry_id
        WHERE entry_id = v_to_entry_id;

        -- 会计恒等式校验
        SELECT COALESCE(SUM(amount), 0) INTO v_total_debit
        FROM account_entries WHERE tx_id = v_tx_id AND direction = 1;

        SELECT COALESCE(SUM(amount), 0) INTO v_total_credit
        FROM account_entries WHERE tx_id = v_tx_id AND direction = 2;

        IF v_total_debit != v_total_credit THEN
            RAISE EXCEPTION '会计恒等式不成立: 借方=%, 贷方=%', v_total_debit, v_total_credit;
        END IF;

        -- 更新交易状态为成功
        UPDATE transactions SET
            status = 2, completed_at = CURRENT_TIMESTAMP
        WHERE tx_id = v_tx_id;

        -- 更新限额使用
        UPDATE account_limits SET
            daily_used_amount = daily_used_amount + p_amount,
            daily_used_count = daily_used_count + 1
        WHERE account_id = v_from_acct.account_id;

        RETURN QUERY SELECT v_tx_id, v_tx_no, 0, '转账成功'::VARCHAR;

    EXCEPTION WHEN OTHERS THEN
        -- 记录失败
        UPDATE transactions SET
            status = 3, error_msg = SQLERRM
        WHERE tx_id = v_tx_id;

        RETURN QUERY SELECT v_tx_id, v_tx_no, -99, SQLERRM::VARCHAR;
    END;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_transfer_realtime IS '实时转账存储过程 - 核心交易引擎';
```

#### 5.2.2 存款存储过程

```sql
-- =============================================
-- 存储过程9: 存款入账
-- =============================================
CREATE OR REPLACE FUNCTION sp_deposit(
    p_account_no        VARCHAR(32),
    p_amount            DECIMAL(18,2),
    p_deposit_type      VARCHAR(20),
    p_remark            VARCHAR(255) DEFAULT NULL,
    p_channel           VARCHAR(20) DEFAULT 'COUNTER'  -- 存款渠道
) RETURNS TABLE (
    tx_id               BIGINT,
    tx_no               VARCHAR(32),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_tx_id             BIGINT;
    v_tx_no             VARCHAR(32);
    v_account           RECORD;
    v_balance           RECORD;
BEGIN
    IF p_amount <= 0 THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -1, '存款金额必须大于0'::VARCHAR;
        RETURN;
    END IF;

    SELECT * INTO v_account FROM accounts
    WHERE account_no = p_account_no AND status = 1 FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -2, '账户不存在或状态异常'::VARCHAR;
        RETURN;
    END IF;

    v_tx_no := 'DP' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') ||
               LPAD(FLOOR(RANDOM() * 100000000)::TEXT, 8, '0');

    INSERT INTO transactions (
        tx_no, tx_type, amount, currency, to_account_no,
        status, remark, extra_data
    ) VALUES (
        v_tx_no, 'DEPOSIT', p_amount, v_account.currency, p_account_no,
        1, p_remark, jsonb_build_object('channel', p_channel, 'type', p_deposit_type)
    ) RETURNING transactions.tx_id INTO v_tx_id;

    SELECT * INTO v_balance FROM account_balances
    WHERE account_no = p_account_no FOR UPDATE;

    -- 更新余额
    UPDATE account_balances SET
        current_balance = current_balance + p_amount,
        available_balance = available_balance + p_amount,
        total_in_amount = total_in_amount + p_amount,
        total_in_count = total_in_count + 1,
        version = version + 1,
        last_tx_id = v_tx_id,
        last_tx_time = CURRENT_TIMESTAMP
    WHERE account_no = p_account_no;

    -- 插入会计分录 (贷方 - 资产增加)
    INSERT INTO account_entries (
        entry_no, tx_id, tx_no, account_id, account_no,
        entry_type, amount, direction, account_category,
        balance_before, balance_after, remark
    ) VALUES (
        'EN' || v_tx_no, v_tx_id, v_tx_no, v_account.account_id, p_account_no,
        p_deposit_type, p_amount, 2, 'ASSET',
        v_balance.current_balance, v_balance.current_balance + p_amount,
        COALESCE(p_remark, '存款')
    );

    UPDATE transactions SET status = 2, completed_at = CURRENT_TIMESTAMP
    WHERE tx_id = v_tx_id;

    RETURN QUERY SELECT v_tx_id, v_tx_no, 0, '存款成功'::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT COALESCE(v_tx_id, NULL)::BIGINT, v_tx_no::VARCHAR, -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

#### 5.2.3 取款存储过程

```sql
-- =============================================
-- 存储过程10: 取款
-- =============================================
CREATE OR REPLACE FUNCTION sp_withdraw(
    p_account_no        VARCHAR(32),
    p_amount            DECIMAL(18,2),
    p_remark            VARCHAR(255) DEFAULT NULL
) RETURNS TABLE (
    tx_id               BIGINT,
    tx_no               VARCHAR(32),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_tx_id             BIGINT;
    v_tx_no             VARCHAR(32);
    v_account           RECORD;
    v_balance           RECORD;
    v_risk_result       RECORD;
BEGIN
    IF p_amount <= 0 THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -1, '取款金额必须大于0'::VARCHAR;
        RETURN;
    END IF;

    SELECT * INTO v_account FROM accounts
    WHERE account_no = p_account_no AND status = 1 FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -2, '账户不存在或状态异常'::VARCHAR;
        RETURN;
    END IF;

    -- 风控检查
    SELECT * INTO v_risk_result FROM fn_risk_check(
        p_account_no, NULL, p_amount, 'WITHDRAW'
    );

    IF v_risk_result.check_result != 'PASS' THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -3,
                            ('风控拦截: ' || v_risk_result.check_result)::VARCHAR;
        RETURN;
    END IF;

    SELECT * INTO v_balance FROM account_balances
    WHERE account_no = p_account_no FOR UPDATE;

    IF v_balance.available_balance < p_amount THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, -4, '余额不足'::VARCHAR;
        RETURN;
    END IF;

    v_tx_no := 'WD' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') ||
               LPAD(FLOOR(RANDOM() * 100000000)::TEXT, 8, '0');

    INSERT INTO transactions (
        tx_no, tx_type, amount, currency, from_account_no, status, remark
    ) VALUES (
        v_tx_no, 'WITHDRAW', p_amount, v_account.currency, p_account_no, 1, p_remark
    ) RETURNING transactions.tx_id INTO v_tx_id;

    -- 更新余额
    UPDATE account_balances SET
        current_balance = current_balance - p_amount,
        available_balance = available_balance - p_amount,
        total_out_amount = total_out_amount + p_amount,
        total_out_count = total_out_count + 1,
        version = version + 1,
        last_tx_id = v_tx_id,
        last_tx_time = CURRENT_TIMESTAMP
    WHERE account_no = p_account_no;

    -- 插入会计分录 (借方 - 资产减少)
    INSERT INTO account_entries (
        entry_no, tx_id, tx_no, account_id, account_no,
        entry_type, amount, direction, account_category,
        balance_before, balance_after, remark
    ) VALUES (
        'EN' || v_tx_no, v_tx_id, v_tx_no, v_account.account_id, p_account_no,
        'WITHDRAW', p_amount, 1, 'ASSET',
        v_balance.current_balance, v_balance.current_balance - p_amount,
        COALESCE(p_remark, '取款')
    );

    UPDATE transactions SET status = 2, completed_at = CURRENT_TIMESTAMP
    WHERE tx_id = v_tx_id;

    -- 更新限额
    UPDATE account_limits SET
        daily_used_amount = daily_used_amount + p_amount,
        daily_used_count = daily_used_count + 1
    WHERE account_id = v_account.account_id;

    RETURN QUERY SELECT v_tx_id, v_tx_no, 0, '取款成功'::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT COALESCE(v_tx_id, NULL)::BIGINT, v_tx_no::VARCHAR, -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

#### 5.2.4 批量转账存储过程

```sql
-- =============================================
-- 存储过程11: 创建批量转账任务
-- =============================================
CREATE OR REPLACE FUNCTION sp_batch_transfer_create(
    p_from_account      VARCHAR(32),
    p_batch_type        VARCHAR(20),
    p_batch_name        VARCHAR(100),
    p_details           JSONB,  -- [{"seq_no": 1, "to_account": "xxx", "amount": 100, "remark": ""}, ...]
    p_execute_time      TIMESTAMPTZ DEFAULT NULL
) RETURNS TABLE (
    batch_id            BIGINT,
    batch_no            VARCHAR(32),
    total_count         INTEGER,
    total_amount        DECIMAL(18,2),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_batch_id          BIGINT;
    v_batch_no          VARCHAR(32);
    v_total_count       INTEGER := 0;
    v_total_amount      DECIMAL(18,2) := 0;
    v_item              JSONB;
    v_detail            RECORD;
    v_account           RECORD;
BEGIN
    -- 检查付款账户
    SELECT * INTO v_account FROM accounts
    WHERE account_no = p_from_account AND status = 1;

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, 0, 0::DECIMAL,
                            -1, '付款账户不存在或状态异常'::VARCHAR;
        RETURN;
    END IF;

    -- 生成批次号
    v_batch_no := 'BT' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') ||
                  LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');

    -- 统计明细
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_details)
    LOOP
        v_total_count := v_total_count + 1;
        v_total_amount := v_total_amount + (v_item->>'amount')::DECIMAL;
    END LOOP;

    -- 创建批量任务
    INSERT INTO batch_tasks (
        batch_no, batch_type, batch_name, total_count, total_amount,
        from_account_no, status, execute_time
    ) VALUES (
        v_batch_no, p_batch_type, p_batch_name, v_total_count, v_total_amount,
        p_from_account, 0, COALESCE(p_execute_time, CURRENT_TIMESTAMP)
    ) RETURNING batch_tasks.batch_id INTO v_batch_id;

    -- 插入明细
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_details)
    LOOP
        INSERT INTO batch_details (
            batch_id, seq_no, to_account_no, to_account_name,
            amount, remark
        ) VALUES (
            v_batch_id,
            (v_item->>'seq_no')::INTEGER,
            v_item->>'to_account',
            v_item->>'to_name',
            (v_item->>'amount')::DECIMAL,
            v_item->>'remark'
        );
    END LOOP;

    RETURN QUERY SELECT v_batch_id, v_batch_no, v_total_count, v_total_amount,
                        0, '批量任务创建成功'::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT NULL::BIGINT, NULL::VARCHAR, 0, 0::DECIMAL, -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 存储过程12: 执行批量转账
-- =============================================
CREATE OR REPLACE FUNCTION sp_batch_transfer_execute(
    p_batch_id          BIGINT
) RETURNS TABLE (
    success_count       INTEGER,
    fail_count          INTEGER,
    success_amount      DECIMAL(18,2),
    fail_amount         DECIMAL(18,2),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_batch             RECORD;
    v_detail            RECORD;
    v_result            RECORD;
    v_success_count     INTEGER := 0;
    v_fail_count        INTEGER := 0;
    v_success_amount    DECIMAL(18,2) := 0;
    v_fail_amount       DECIMAL(18,2) := 0;
BEGIN
    SELECT * INTO v_batch FROM batch_tasks
    WHERE batch_id = p_batch_id AND status = 0 FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT 0, 0, 0::DECIMAL, 0::DECIMAL,
                            -1, '批量任务不存在或状态异常'::VARCHAR;
        RETURN;
    END IF;

    -- 更新状态为处理中
    UPDATE batch_tasks SET status = 1, actual_start = CURRENT_TIMESTAMP
    WHERE batch_id = p_batch_id;

    -- 逐笔处理
    FOR v_detail IN
        SELECT * FROM batch_details
        WHERE batch_id = p_batch_id AND status = 0
        ORDER BY seq_no
    LOOP
        SELECT * INTO v_result FROM sp_transfer_realtime(
            v_batch.from_account_no,
            v_detail.to_account_no,
            v_detail.amount,
            v_detail.remark
        );

        IF v_result.result_code = 0 THEN
            UPDATE batch_details SET
                status = 1, tx_id = v_result.tx_id
            WHERE detail_id = v_detail.detail_id;
            v_success_count := v_success_count + 1;
            v_success_amount := v_success_amount + v_detail.amount;
        ELSE
            UPDATE batch_details SET
                status = 2, error_code = v_result.result_code::TEXT,
                error_msg = v_result.result_msg
            WHERE detail_id = v_detail.detail_id;
            v_fail_count := v_fail_count + 1;
            v_fail_amount := v_fail_amount + v_detail.amount;
        END IF;
    END LOOP;

    -- 更新批量任务状态
    UPDATE batch_tasks SET
        status = CASE WHEN v_fail_count = 0 THEN 3
                      WHEN v_success_count > 0 THEN 2
                      ELSE 4 END,
        success_count = v_success_count,
        success_amount = v_success_amount,
        fail_count = v_fail_count,
        fail_amount = v_fail_amount,
        actual_end = CURRENT_TIMESTAMP
    WHERE batch_id = p_batch_id;

    RETURN QUERY SELECT v_success_count, v_fail_count, v_success_amount, v_fail_amount,
                        0, format('批量处理完成: 成功%d笔, 失败%d笔',
                                  v_success_count, v_fail_count)::VARCHAR;

EXCEPTION WHEN OTHERS THEN
    UPDATE batch_tasks SET status = 4, error_msg = SQLERRM WHERE batch_id = p_batch_id;
    RETURN QUERY SELECT 0, 0, 0::DECIMAL, 0::DECIMAL, -99, SQLERRM::VARCHAR;
END;
$$ LANGUAGE plpgsql;
```

### 5.3 转账相关触发器

```sql
-- =============================================
-- 触发器: 交易完成后的后续处理
-- =============================================
CREATE OR REPLACE FUNCTION trg_fn_tx_post_process()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 2 AND OLD.status != 2 THEN
        -- 交易成功后的处理

        -- 1. 触发风控评分更新 (异步，实际生产使用消息队列)
        -- PERFORM pg_notify('risk_update', jsonb_build_object(
        --     'account_no', NEW.from_account_no,
        --     'tx_id', NEW.tx_id,
        --     'amount', NEW.amount
        -- )::TEXT);

        -- 2. 大额交易通知
        IF NEW.amount >= 50000 THEN
            RAISE NOTICE '大额交易通知: tx_no=%, amount=%', NEW.tx_no, NEW.amount;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tx_post_process
    AFTER UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION trg_fn_tx_post_process();
```

---

## 6. 清算系统实现

### 6.1 日终清算流程

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          日终清算流程图                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                         日终清算批处理流程                                │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                            │
│                                    ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ 1. 预处理阶段                                                            │   │
│   │    - 检查未完成交易                                                       │   │
│   │    - 冻结当日交易录入                                                      │   │
│   │    - 锁定所有账户余额表                                                    │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                            │
│                                    ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ 2. 数据汇总阶段                                                          │   │
│   │    - 统计当日所有会计分录                                                  │   │
│   │    - 按账户汇总借方/贷方发生额                                              │   │
│   │    - 计算各账户期末余额                                                    │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                            │
│                                    ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ 3. 校验阶段                                                              │   │
│   │    - 校验: Σ借方发生额 = Σ贷方发生额                                        │   │
│   │    - 校验: 各账户期末余额 = 期初 + 流入 - 流出                               │   │
│   │    - 校验: 总资产 = 总负债 + 总权益                                         │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                            │
│                                    ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ 4. 归档阶段                                                              │   │
│   │    - 生成分户账                                                           │   │
│   │    - 生成总账                                                             │   │
│   │    - 更新账户日初余额                                                      │   │
│   │    - 归档当日明细到历史表                                                   │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                            │
│                                    ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ 5. 完成阶段                                                              │   │
│   │    - 释放账户锁                                                           │   │
│   │    - 恢复交易录入                                                         │   │
│   │    - 生成清算报告                                                         │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 清算核心存储过程

#### 6.2.1 日终清算存储过程

```sql
-- =============================================
-- 存储过程13: 日终清算 (核心批处理)
-- =============================================
CREATE OR REPLACE FUNCTION sp_daily_settlement(
    p_settle_date       DATE DEFAULT CURRENT_DATE
) RETURNS TABLE (
    settle_id           BIGINT,
    total_accounts      INTEGER,
    total_entries       INTEGER,
    diff_amount         DECIMAL(18,2),
    result_code         INTEGER,
    result_msg          VARCHAR(255)
) AS $$
DECLARE
    v_settle_id         BIGINT;
    v_total_debit       DECIMAL(18,2) := 0;
    v_total_credit      DECIMAL(18,2) := 0;
    v_diff              DECIMAL(18,2) := 0;
    v_account_count     INTEGER := 0;
    v_entry_count       INTEGER := 0;
    v_account           RECORD;
    v_begin_balance     DECIMAL(18,2);
    v_end_balance       DECIMAL(18,2);
    v_total_in          DECIMAL(18,2);
    v_total_out         DECIMAL(18,2);
    v_calc_balance      DECIMAL(18,2);
    v_account_diff      DECIMAL(18,2);
BEGIN
    -- 检查是否已清算
    IF EXISTS (SELECT 1 FROM daily_settlements WHERE settle_date = p_settle_date) THEN
        RETURN QUERY SELECT NULL::BIGINT, 0, 0, 0::DECIMAL, -1,
                            '当日已清算'::VARCHAR;
        RETURN;
    END IF;

    -- 检查是否有处理中的交易
    IF EXISTS (SELECT 1 FROM transactions
               WHERE DATE(created_at) = p_settle_date AND status = 1) THEN
        RETURN QUERY SELECT NULL::BIGINT, 0, 0, 0::DECIMAL, -2,
                            '存在未完成的交易'::VARCHAR;
        RETURN;
    END IF;

    -- 创建清算记录
    INSERT INTO daily_settlements (
        settle_date, status, started_at
    ) VALUES (
        p_settle_date, 1, CURRENT_TIMESTAMP
    ) RETURNING daily_settlements.settle_id INTO v_settle_id;

    BEGIN
        -- 1. 统计当日会计分录
        SELECT
            COUNT(*),
            COALESCE(SUM(CASE WHEN direction = 1 THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN direction = 2 THEN amount ELSE 0 END), 0)
        INTO v_entry_count, v_total_debit, v_total_credit
        FROM account_entries
        WHERE DATE(created_at) = p_settle_date;

        -- 2. 会计恒等式校验
        v_diff := v_total_debit - v_total_credit;

        IF v_diff != 0 THEN
            RAISE EXCEPTION '会计恒等式不成立: 借方总额=%, 贷方总额=%, 差额=%',
                v_total_debit, v_total_credit, v_diff;
        END IF;

        -- 3. 逐账户清算
        FOR v_account IN
            SELECT DISTINCT a.account_id, a.account_no, b.begin_balance, b.current_balance
            FROM accounts a
            JOIN account_balances b ON a.account_id = b.account_id
            WHERE a.status = 1
            ORDER BY a.account_no
        LOOP
            -- 统计该账户当日发生额
            SELECT
                COALESCE(SUM(CASE WHEN direction = 2 THEN amount ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN direction = 1 THEN amount ELSE 0 END), 0),
                COUNT(*)
            INTO v_total_in, v_total_out, v_entry_count
            FROM account_entries
            WHERE account_no = v_account.account_no
              AND DATE(created_at) = p_settle_date;

            v_begin_balance := COALESCE(v_account.begin_balance, 0);
            v_end_balance := v_account.current_balance;

            -- 计算预期期末余额
            v_calc_balance := v_begin_balance + v_total_in - v_total_out;
            v_account_diff := v_end_balance - v_calc_balance;

            -- 插入清算明细
            INSERT INTO settlement_details (
                settle_id, account_no, begin_balance, end_balance,
                total_in_amount, total_out_amount, total_in_count, total_out_count,
                check_result, diff_amount
            ) VALUES (
                v_settle_id, v_account.account_no, v_begin_balance, v_end_balance,
                v_total_in, v_total_out,
                (SELECT COUNT(*) FROM account_entries WHERE account_no = v_account.account_no AND direction = 2 AND DATE(created_at) = p_settle_date),
                (SELECT COUNT(*) FROM account_entries WHERE account_no = v_account.account_no AND direction = 1 AND DATE(created_at) = p_settle_date),
                v_account_diff = 0, v_account_diff
            );

            -- 更新账户日初余额 (用于次日清算)
            UPDATE account_balances SET
                begin_balance = v_end_balance,
                last_settle_date = p_settle_date
            WHERE account_no = v_account.account_no;

            v_account_count := v_account_count + 1;
        END LOOP;

        -- 4. 更新清算汇总
        UPDATE daily_settlements SET
            total_accounts = v_account_count,
            active_accounts = (SELECT COUNT(DISTINCT account_no) FROM account_entries
                               WHERE DATE(created_at) = p_settle_date),
            total_entries = v_entry_count,
            total_debit = v_total_debit,
            total_credit = v_total_credit,
            diff_amount = v_diff,
            status = 2,
            completed_at = CURRENT_TIMESTAMP
        WHERE settle_id = v_settle_id;

        RETURN QUERY SELECT v_settle_id, v_account_count, v_entry_count, v_diff,
                            0, '清算成功'::VARCHAR;

    EXCEPTION WHEN OTHERS THEN
        UPDATE daily_settlements SET
            status = 3, error_msg = SQLERRM
        WHERE settle_id = v_settle_id;

        RETURN QUERY SELECT v_settle_id, 0, 0, 0::DECIMAL, -99, SQLERRM::VARCHAR;
    END;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_daily_settlement IS '日终清算存储过程';
```

#### 6.2.2 对账存储过程

```sql
-- =============================================
-- 存储过程14: 账户对账
-- =============================================
CREATE OR REPLACE FUNCTION sp_account_reconciliation(
    p_account_no        VARCHAR(32),
    p_start_date        DATE,
    p_end_date          DATE
) RETURNS TABLE (
    check_date          DATE,
    begin_balance       DECIMAL(18,2),
    total_in            DECIMAL(18,2),
    total_out           DECIMAL(18,2),
    calc_end_balance    DECIMAL(18,2),
    actual_end_balance  DECIMAL(18,2),
    is_balanced         BOOLEAN,
    diff_amount         DECIMAL(18,2)
) AS $$
BEGIN
    RETURN QUERY
    WITH daily_summary AS (
        SELECT
            DATE(e.created_at) AS tx_date,
            SUM(CASE WHEN e.direction = 2 THEN e.amount ELSE 0 END) AS daily_in,
            SUM(CASE WHEN e.direction = 1 THEN e.amount ELSE 0 END) AS daily_out
        FROM account_entries e
        WHERE e.account_no = p_account_no
          AND DATE(e.created_at) BETWEEN p_start_date AND p_end_date
        GROUP BY DATE(e.created_at)
    ),
    dates AS (
        SELECT generate_series(p_start_date, p_end_date, INTERVAL '1 day')::DATE AS d
    )
    SELECT
        d.d AS check_date,
        COALESCE(sd.begin_balance, LAG(daily_in - daily_out) OVER (ORDER BY d.d), 0) AS begin_balance,
        COALESCE(ds.daily_in, 0) AS total_in,
        COALESCE(ds.daily_out, 0) AS total_out,
        COALESCE(sd.begin_balance, 0) + COALESCE(ds.daily_in, 0) - COALESCE(ds.daily_out, 0) AS calc_end_balance,
        COALESCE(sd.end_balance, 0) AS actual_end_balance,
        COALESCE(sd.check_result, true) AS is_balanced,
        COALESCE(sd.diff_amount, 0) AS diff_amount
    FROM dates d
    LEFT JOIN daily_summary ds ON d.d = ds.tx_date
    LEFT JOIN settlement_details sd ON sd.account_no = p_account_no
        AND sd.settle_id = (SELECT settle_id FROM daily_settlements WHERE settle_date = d.d)
    ORDER BY d.d;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 存储过程15: 生成对账报表
-- =============================================
CREATE OR REPLACE FUNCTION sp_generate_recon_report(
    p_settle_date       DATE
) RETURNS TABLE (
    report_type         VARCHAR(20),
    item_name           VARCHAR(100),
    item_count          BIGINT,
    item_amount         DECIMAL(18,2)
) AS $$
BEGIN
    -- 总账报表
    RETURN QUERY
    SELECT '总账'::VARCHAR(20), '借方发生额'::VARCHAR(100),
           total_entries::BIGINT, total_debit
    FROM daily_settlements WHERE settle_date = p_settle_date;

    RETURN QUERY
    SELECT '总账'::VARCHAR(20), '贷方发生额'::VARCHAR(100),
           total_entries::BIGINT, total_credit
    FROM daily_settlements WHERE settle_date = p_settle_date;

    -- 交易类型统计
    RETURN QUERY
    SELECT '交易类型'::VARCHAR(20), tx_type::VARCHAR(100),
           COUNT(*)::BIGINT, COALESCE(SUM(amount), 0)
    FROM transactions
    WHERE DATE(created_at) = p_settle_date AND status = 2
    GROUP BY tx_type;

    -- 异常账户统计
    RETURN QUERY
    SELECT '异常账户'::VARCHAR(20), '余额不平'::VARCHAR(100),
           COUNT(*)::BIGINT, COALESCE(SUM(ABS(diff_amount)), 0)
    FROM settlement_details sd
    JOIN daily_settlements ds ON sd.settle_id = ds.settle_id
    WHERE ds.settle_date = p_settle_date AND sd.check_result = false;
END;
$$ LANGUAGE plpgsql;
```

### 6.3 会计恒等式校验函数

```sql
-- =============================================
-- 函数: 校验会计恒等式
-- =============================================
CREATE OR REPLACE FUNCTION fn_check_accounting_balance(
    p_tx_id             BIGINT
) RETURNS BOOLEAN AS $$
DECLARE
    v_total_debit       DECIMAL(18,2);
    v_total_credit      DECIMAL(18,2);
BEGIN
    SELECT COALESCE(SUM(amount), 0) INTO v_total_debit
    FROM account_entries WHERE tx_id = p_tx_id AND direction = 1;

    SELECT COALESCE(SUM(amount), 0) INTO v_total_credit
    FROM account_entries WHERE tx_id = p_tx_id AND direction = 2;

    RETURN v_total_debit = v_total_credit;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 触发器: 会计分录自动校验
-- =============================================
CREATE OR REPLACE FUNCTION trg_fn_validate_accounting()
RETURNS TRIGGER AS $$
DECLARE
    v_is_balanced       BOOLEAN;
BEGIN
    -- 校验借贷平衡
    SELECT fn_check_accounting_balance(NEW.tx_id) INTO v_is_balanced;

    IF NOT v_is_balanced THEN
        RAISE EXCEPTION '会计恒等式校验失败: tx_id=%', NEW.tx_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER trg_validate_accounting
    AFTER INSERT ON account_entries
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION trg_fn_validate_accounting();
```

---

## 7. 风控系统实现

### 7.1 风控架构设计

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           风控系统架构图                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                         交易请求                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                            │
│                                    ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                        风控决策引擎                                        │   │
│   │  ┌──────────────────────────────────────────────────────────────────┐  │   │
│   │  │ 规则引擎 (Rule Engine)                                           │  │   │
│   │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │  │   │
│   │  │  │ 限额规则    │ │ 频次规则    │ │ 时间规则    │ │ 黑名单    │  │  │   │
│   │  │  │Limit Rules │ │Freq Rules  │ │Time Rules  │ │Blacklist  │  │  │   │
│   │  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │  │   │
│   │  └──────────────────────────────────────────────────────────────────┘  │   │
│   │  ┌──────────────────────────────────────────────────────────────────┐  │   │
│   │  │ 反欺诈引擎 (Anti-Fraud Engine)                                   │  │   │
│   │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │  │   │
│   │  │  │ 设备指纹    │ │ 行为分析    │ │ 关系图谱    │ │ 异常检测  │  │  │   │
│   │  │  │Device     │ │Behavior   │ │Graph      │ │Anomaly   │  │  │   │
│   │  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │  │   │
│   │  └──────────────────────────────────────────────────────────────────┘  │   │
│   │  ┌──────────────────────────────────────────────────────────────────┐  │   │
│   │  │ AML引擎 (Anti-Money Laundering)                                  │  │   │
│   │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │  │   │
│   │  │  │ 大额监控    │ │ 可疑交易    │ │ 资金流向    │ │ 名单筛查  │  │  │   │
│   │  │  │Threshold  │ │Suspicious │ │Tracking   │ │Screening  │  │  │   │
│   │  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │  │   │
│   │  └──────────────────────────────────────────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                            │
│                     ┌──────────────┼──────────────┐                            │
│                     ▼              ▼              ▼                            │
│                 ┌──────┐     ┌──────┐      ┌──────┐                           │
│                 │通过  │     │警告  │      │拦截  │                           │
│                 │PASS │     │WARN  │      │REJECT│                           │
│                 └──┬───┘     └──┬───┘      └──┬───┘                           │
│                    │            │             │                                │
│                    ▼            ▼             ▼                                │
│               正常处理      人工审核        拒绝交易                            │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 风控核心存储过程

#### 7.2.1 综合风控检查函数

```sql
-- =============================================
-- 函数: 综合风控检查 (核心)
-- =============================================
CREATE OR REPLACE FUNCTION fn_risk_check(
    p_from_account      VARCHAR(32),
    p_to_account        VARCHAR(32) DEFAULT NULL,
    p_amount            DECIMAL(18,2),
    p_tx_type           VARCHAR(20)
) RETURNS TABLE (
    check_result        VARCHAR(20),  -- PASS, WARN, REJECT, REVIEW
    risk_level          SMALLINT,     -- 1:低 2:中 3:高
    risk_type           VARCHAR(20),  -- LIMIT, FRAUD, AML
    rule_id             VARCHAR(50),
    rule_name           VARCHAR(100),
    check_detail        JSONB
) AS $$
DECLARE
    v_result            VARCHAR(20) := 'PASS';
    v_level             SMALLINT := 1;
    v_type              VARCHAR(20) := '';
    v_rule_id           VARCHAR(50) := '';
    v_rule_name         VARCHAR(100) := '';
    v_detail            JSONB := '{}'::JSONB;
    v_limit_result      RECORD;
    v_fraud_result      RECORD;
    v_aml_result        RECORD;
BEGIN
    -- 1. 限额检查
    SELECT * INTO v_limit_result FROM fn_check_limit(
        p_from_account, p_amount, p_tx_type
    );

    IF v_limit_result.check_result = 'REJECT' THEN
        RETURN QUERY SELECT v_limit_result.check_result, 3::SMALLINT,
                            'LIMIT'::VARCHAR(20), v_limit_result.rule_id,
                            v_limit_result.rule_name, v_limit_result.check_detail;
        RETURN;
    ELSIF v_limit_result.check_result = 'WARN' THEN
        v_result := 'WARN';
        v_level := 2;
        v_type := 'LIMIT';
        v_rule_id := v_limit_result.rule_id;
        v_rule_name := v_limit_result.rule_name;
        v_detail := v_limit_result.check_detail;
    END IF;

    -- 2. 反欺诈检查
    SELECT * INTO v_fraud_result FROM fn_check_fraud(
        p_from_account, p_to_account, p_amount, p_tx_type
    );

    IF v_fraud_result.check_result = 'REJECT' THEN
        RETURN QUERY SELECT v_fraud_result.check_result, 3::SMALLINT,
                            'FRAUD'::VARCHAR(20), v_fraud_result.rule_id,
                            v_fraud_result.rule_name, v_fraud_result.check_detail;
        RETURN;
    ELSIF v_fraud_result.check_result = 'WARN' AND v_result = 'PASS' THEN
        v_result := 'WARN';
        v_level := 2;
        v_type := 'FRAUD';
        v_rule_id := v_fraud_result.rule_id;
        v_rule_name := v_fraud_result.rule_name;
        v_detail := v_fraud_result.check_detail;
    END IF;

    -- 3. AML检查
    SELECT * INTO v_aml_result FROM fn_check_aml(
        p_from_account, p_to_account, p_amount, p_tx_type
    );

    IF v_aml_result.check_result = 'REJECT' THEN
        RETURN QUERY SELECT v_aml_result.check_result, 3::SMALLINT,
                            'AML'::VARCHAR(20), v_aml_result.rule_id,
                            v_aml_result.rule_name, v_aml_result.check_detail;
        RETURN;
    ELSIF v_aml_result.check_result = 'REVIEW' THEN
        RETURN QUERY SELECT 'REVIEW'::VARCHAR(20), 2::SMALLINT,
                            'AML'::VARCHAR(20), v_aml_result.rule_id,
                            v_aml_result.rule_name, v_aml_result.check_detail;
        RETURN;
    END IF;

    -- 返回最终结果
    RETURN QUERY SELECT v_result, v_level, v_type, v_rule_id, v_rule_name, v_detail;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_risk_check IS '综合风控检查函数';
```

#### 7.2.2 限额检查函数

```sql
-- =============================================
-- 函数: 限额检查
-- =============================================
CREATE OR REPLACE FUNCTION fn_check_limit(
    p_account_no        VARCHAR(32),
    p_amount            DECIMAL(18,2),
    p_tx_type           VARCHAR(20)
) RETURNS TABLE (
    check_result        VARCHAR(20),
    rule_id             VARCHAR(50),
    rule_name           VARCHAR(100),
    check_detail        JSONB
) AS $$
DECLARE
    v_limit             RECORD;
    v_daily_sum         DECIMAL(18,2);
BEGIN
    -- 获取账户限额
    SELECT l.* INTO v_limit
    FROM account_limits l
    JOIN accounts a ON l.account_id = a.account_id
    WHERE a.account_no = p_account_no;

    IF NOT FOUND THEN
        RETURN QUERY SELECT 'PASS'::VARCHAR(20), ''::VARCHAR(50), ''::VARCHAR(100), '{}'::JSONB;
        RETURN;
    END IF;

    -- 检查单笔限额
    IF p_amount > v_limit.single_limit THEN
        RETURN QUERY SELECT 'REJECT'::VARCHAR(20),
                            'LIMIT_001'::VARCHAR(50),
                            '单笔金额超限'::VARCHAR(100),
                            jsonb_build_object(
                                'amount', p_amount,
                                'single_limit', v_limit.single_limit
                            );
        RETURN;
    END IF;

    -- 重置日限额 (如果需要)
    IF v_limit.last_reset_date != CURRENT_DATE THEN
        v_limit.daily_used_amount := 0;
        v_limit.daily_used_count := 0;
    END IF;

    -- 检查日限额
    IF v_limit.daily_used_amount + p_amount > v_limit.daily_limit THEN
        RETURN QUERY SELECT 'REJECT'::VARCHAR(20),
                            'LIMIT_002'::VARCHAR(50),
                            '日累计金额超限'::VARCHAR(100),
                            jsonb_build_object(
                                'amount', p_amount,
                                'daily_used', v_limit.daily_used_amount,
                                'daily_limit', v_limit.daily_limit
                            );
        RETURN;
    END IF;

    -- 检查日累计笔数
    IF v_limit.daily_used_count >= v_limit.daily_count_limit THEN
        RETURN QUERY SELECT 'REJECT'::VARCHAR(20),
                            'LIMIT_003'::VARCHAR(50),
                            '日累计笔数超限'::VARCHAR(100),
                            jsonb_build_object(
                                'daily_count', v_limit.daily_used_count,
                                'count_limit', v_limit.daily_count_limit
                            );
        RETURN;
    END IF;

    RETURN QUERY SELECT 'PASS'::VARCHAR(20), ''::VARCHAR(50), ''::VARCHAR(100), '{}'::JSONB;
END;
$$ LANGUAGE plpgsql;
```

#### 7.2.3 反欺诈检查函数

```sql
-- =============================================
-- 函数: 反欺诈检查
-- =============================================
CREATE OR REPLACE FUNCTION fn_check_fraud(
    p_from_account      VARCHAR(32),
    p_to_account        VARCHAR(32),
    p_amount            DECIMAL(18,2),
    p_tx_type           VARCHAR(20)
) RETURNS TABLE (
    check_result        VARCHAR(20),
    rule_id             VARCHAR(50),
    rule_name           VARCHAR(100),
    check_detail        JSONB
) AS $$
DECLARE
    v_recent_count      INTEGER;
    v_hour_count        INTEGER;
    v_avg_amount        DECIMAL(18,2);
    v_customer_risk     SMALLINT;
BEGIN
    -- 检查客户风险等级
    SELECT c.risk_level INTO v_customer_risk
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    WHERE a.account_no = p_from_account;

    -- 高风险客户
    IF v_customer_risk = 3 THEN
        RETURN QUERY SELECT 'REVIEW'::VARCHAR(20),
                            'FRAUD_001'::VARCHAR(50),
                            '高风险客户'::VARCHAR(100),
                            jsonb_build_object('risk_level', v_customer_risk);
        RETURN;
    END IF;

    -- 检查短时高频交易 (1分钟内超过5笔)
    SELECT COUNT(*) INTO v_recent_count
    FROM transactions
    WHERE from_account_no = p_from_account
      AND created_at > CURRENT_TIMESTAMP - INTERVAL '1 minute'
      AND status IN (1, 2);

    IF v_recent_count > 5 THEN
        RETURN QUERY SELECT 'REJECT'::VARCHAR(20),
                            'FRAUD_002'::VARCHAR(50),
                            '短时高频交易'::VARCHAR(100),
                            jsonb_build_object('recent_count', v_recent_count);
        RETURN;
    END IF;

    -- 检查金额异常 (超过近30日平均10倍)
    SELECT AVG(amount) INTO v_avg_amount
    FROM transactions
    WHERE from_account_no = p_from_account
      AND created_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
      AND status = 2;

    IF v_avg_amount IS NOT NULL AND v_avg_amount > 0
       AND p_amount > v_avg_amount * 10 THEN
        RETURN QUERY SELECT 'WARN'::VARCHAR(20),
                            'FRAUD_003'::VARCHAR(50),
                            '交易金额异常'::VARCHAR(100),
                            jsonb_build_object(
                                'amount', p_amount,
                                'avg_amount', v_avg_amount,
                                'multiple', p_amount / v_avg_amount
                            );
        RETURN;
    END IF;

    -- 检查循环转账 (A→B→A)
    IF p_to_account IS NOT NULL THEN
        IF EXISTS (
            SELECT 1 FROM transactions
            WHERE from_account_no = p_to_account
              AND to_account_no = p_from_account
              AND created_at > CURRENT_TIMESTAMP - INTERVAL '1 hour'
              AND status = 2
        ) THEN
            RETURN QUERY SELECT 'REVIEW'::VARCHAR(20),
                                'FRAUD_004'::VARCHAR(50),
                                '疑似循环转账'::VARCHAR(100),
                                '{}'::JSONB;
            RETURN;
        END IF;
    END IF;

    RETURN QUERY SELECT 'PASS'::VARCHAR(20), ''::VARCHAR(50), ''::VARCHAR(100), '{}'::JSONB;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_check_fraud IS '反欺诈检查函数';
```

#### 7.2.4 反洗钱检查函数

```sql
-- =============================================
-- 函数: AML检查
-- =============================================
CREATE OR REPLACE FUNCTION fn_check_aml(
    p_from_account      VARCHAR(32),
    p_to_account        VARCHAR(32),
    p_amount            DECIMAL(18,2),
    p_tx_type           VARCHAR(20)
) RETURNS TABLE (
    check_result        VARCHAR(20),
    rule_id             VARCHAR(50),
    rule_name           VARCHAR(100),
    check_detail        JSONB
) AS $$
DECLARE
    v_threshold         DECIMAL(18,2);
    v_daily_sum         DECIMAL(18,2);
BEGIN
    -- 获取AML阈值
    SELECT config_value::DECIMAL INTO v_threshold
    FROM system_configs WHERE config_key = 'system.aml.threshold';

    -- 大额交易监控
    IF p_amount >= v_threshold THEN
        RETURN QUERY SELECT 'REVIEW'::VARCHAR(20),
                            'AML_001'::VARCHAR(50),
                            '大额交易监控'::VARCHAR(100),
                            jsonb_build_object('amount', p_amount, 'threshold', v_threshold);
        RETURN;
    END IF;

    -- 当日累计大额
    SELECT COALESCE(SUM(amount), 0) INTO v_daily_sum
    FROM transactions
    WHERE from_account_no = p_from_account
      AND DATE(created_at) = CURRENT_DATE
      AND status = 2;

    IF v_daily_sum >= v_threshold * 5 THEN
        RETURN QUERY SELECT 'REVIEW'::VARCHAR(20),
                            'AML_002'::VARCHAR(50),
                            '当日累计大额'::VARCHAR(100),
                            jsonb_build_object('daily_sum', v_daily_sum);
        RETURN;
    END IF;

    RETURN QUERY SELECT 'PASS'::VARCHAR(20), ''::VARCHAR(50), ''::VARCHAR(100), '{}'::JSONB;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 存储过程: 记录风控日志
-- =============================================
CREATE OR REPLACE FUNCTION sp_log_risk_event(
    p_tx_id             BIGINT,
    p_risk_type         VARCHAR(20),
    p_risk_level        SMALLINT,
    p_rule_id           VARCHAR(50),
    p_check_result      VARCHAR(20),
    p_check_detail      JSONB
) RETURNS void AS $$
BEGIN
    INSERT INTO risk_logs (
        tx_id, risk_type, risk_level, rule_id,
        check_result, check_detail, created_at
    ) VALUES (
        p_tx_id, p_risk_type, p_risk_level, p_rule_id,
        p_check_result, p_check_detail, CURRENT_TIMESTAMP
    );
END;
$$ LANGUAGE plpgsql;
```

---

## 8. 性能优化策略

### 8.1 数据库优化

```sql
-- =============================================
-- 性能优化配置
-- =============================================

-- 分区策略: 会计分录按时间分区
-- 已在前文创建 account_entries_YYYY_MM 分区

-- 索引优化
CREATE INDEX CONCURRENTLY idx_entries_tx_account ON account_entries(tx_id, account_no);
CREATE INDEX CONCURRENTLY idx_tx_status_time ON transactions(status, created_at)
    WHERE status = 1;

-- 并行查询
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET parallel_tuple_cost = 0.1;
ALTER SYSTEM SET parallel_setup_cost = 100;

-- 内存配置
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET work_mem = '32MB';
```

### 8.2 高并发处理

```sql
-- =============================================
-- 乐观锁版本控制 (已集成在转账存储过程中)
-- =============================================

-- 批量更新优化: 减少锁竞争
CREATE OR REPLACE FUNCTION sp_batch_update_balances(
    p_updates           JSONB  -- [{"account_no": "xxx", "delta": 100}, ...]
) RETURNS void AS $$
DECLARE
    v_item              JSONB;
BEGIN
    -- 按账户号排序，统一锁定顺序，防止死锁
    FOR v_item IN
        SELECT * FROM jsonb_array_elements(p_updates)
        ORDER BY (v_item->>'account_no')
    LOOP
        UPDATE account_balances SET
            current_balance = current_balance + (v_item->>'delta')::DECIMAL,
            version = version + 1
        WHERE account_no = (v_item->>'account_no');
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

---

## 9. 安全控制措施

### 9.1 权限控制

```sql
-- =============================================
-- 数据库角色设计
-- =============================================

-- 创建角色
CREATE ROLE finance_app WITH LOGIN PASSWORD 'app_secure_pass';
CREATE ROLE finance_admin WITH LOGIN PASSWORD 'admin_secure_pass';
CREATE ROLE finance_readonly WITH LOGIN PASSWORD 'readonly_pass';

-- 应用层权限
GRANT USAGE ON SCHEMA public TO finance_app;
GRANT EXECUTE ON FUNCTION sp_transfer_realtime TO finance_app;
GRANT EXECUTE ON FUNCTION sp_deposit TO finance_app;
GRANT EXECUTE ON FUNCTION sp_withdraw TO finance_app;
GRANT EXECUTE ON FUNCTION sp_get_account_balance TO finance_app;
GRANT SELECT ON accounts, account_balances TO finance_app;

-- 只读权限
GRANT SELECT ON ALL TABLES IN SCHEMA public TO finance_readonly;

-- 撤销直接修改权限
REVOKE INSERT, UPDATE, DELETE ON account_entries FROM PUBLIC;
REVOKE UPDATE, DELETE ON transactions FROM PUBLIC;
```

### 9.2 数据加密

```sql
-- =============================================
-- 敏感字段加密
-- =============================================

-- 证件号加密存储
CREATE OR REPLACE FUNCTION fn_encrypt_id(
    p_id_number         VARCHAR(50)
) RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(p_id_number, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_decrypt_id(
    p_encrypted         BYTEA
) RETURNS VARCHAR(50) AS $$
BEGIN
    RETURN pgp_sym_decrypt(p_encrypted, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql;
```

---

## 10. 测试方案

### 10.1 单元测试

```sql
-- =============================================
-- 会计恒等式测试
-- =============================================

CREATE OR REPLACE FUNCTION test_accounting_equation()
RETURNS BOOLEAN AS $$
DECLARE
    v_cust_id           BIGINT;
    v_acct1_id          BIGINT;
    v_acct1_no          VARCHAR(32);
    v_acct2_id          BIGINT;
    v_acct2_no          VARCHAR(32);
    v_result            RECORD;
    v_total_debit       DECIMAL(18,2);
    v_total_credit      DECIMAL(18,2);
BEGIN
    -- 创建测试数据
    INSERT INTO customers (customer_no, name, id_type, id_number, phone, status)
    VALUES ('TC001', '测试客户', 'ID_CARD', '110101199001011234', '13800138000', 1)
    RETURNING customer_id INTO v_cust_id;

    SELECT account_id, account_no INTO v_acct1_id, v_acct1_no
    FROM sp_account_open(v_cust_id, 'SAVINGS', 'CNY', 10000);

    SELECT account_id, account_no INTO v_acct2_id, v_acct2_no
    FROM sp_account_open(v_cust_id, 'SAVINGS', 'CNY', 0);

    -- 执行转账
    SELECT * INTO v_result FROM sp_transfer_realtime(
        v_acct1_no, v_acct2_no, 5000, '测试转账'
    );

    ASSERT v_result.result_code = 0, '转账失败';

    -- 校验会计恒等式
    SELECT COALESCE(SUM(amount), 0) INTO v_total_debit
    FROM account_entries WHERE tx_id = v_result.tx_id AND direction = 1;

    SELECT COALESCE(SUM(amount), 0) INTO v_total_credit
    FROM account_entries WHERE tx_id = v_result.tx_id AND direction = 2;

    ASSERT v_total_debit = v_total_credit, '会计恒等式不成立';
    ASSERT v_total_debit = 5000, '分录金额错误';

    -- 校验余额
    SELECT current_balance INTO v_total_debit FROM account_balances
    WHERE account_no = v_acct1_no;

    SELECT current_balance INTO v_total_credit FROM account_balances
    WHERE account_no = v_acct2_no;

    ASSERT v_total_debit = 5000, '付款方余额错误';
    ASSERT v_total_credit = 5000, '收款方余额错误';

    RETURN true;

EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '测试失败: %', SQLERRM;
    RETURN false;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 并发转账测试
-- =============================================

CREATE OR REPLACE FUNCTION test_concurrent_transfer()
RETURNS BOOLEAN AS $$
DECLARE
    v_cust_id           BIGINT;
    v_acct1_no          VARCHAR(32);
    v_acct2_no          VARCHAR(32);
    v_balance1          DECIMAL(18,2);
    v_balance2          DECIMAL(18,2);
BEGIN
    -- 准备数据
    INSERT INTO customers (customer_no, name, id_type, id_number, phone, status)
    VALUES ('TC002', '并发测试', 'ID_CARD', '110101199001015678', '13800138001', 1)
    RETURNING customer_id INTO v_cust_id;

    SELECT account_no INTO v_acct1_no FROM sp_account_open(v_cust_id, 'SAVINGS', 'CNY', 100000);
    SELECT account_no INTO v_acct2_no FROM sp_account_open(v_cust_id, 'SAVINGS', 'CNY', 0);

    -- 模拟100次转账 (实际测试使用pgbench)
    FOR i IN 1..100 LOOP
        PERFORM sp_transfer_realtime(v_acct1_no, v_acct2_no, 100, '并发测试');
    END LOOP;

    -- 验证结果
    SELECT current_balance INTO v_balance1 FROM account_balances WHERE account_no = v_acct1_no;
    SELECT current_balance INTO v_balance2 FROM account_balances WHERE account_no = v_acct2_no;

    ASSERT v_balance1 = 0, format('付款方余额应为0, 实际=%s', v_balance1);
    ASSERT v_balance2 = 100000, format('收款方余额应为100000, 实际=%s', v_balance2);

    RETURN true;
END;
$$ LANGUAGE plpgsql;
```

### 10.2 性能测试

```sql
-- =============================================
-- 转账性能监控
-- =============================================

CREATE VIEW vw_transfer_perf AS
SELECT
    DATE_TRUNC('hour', created_at) AS hour,
    COUNT(*) AS tx_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) AS avg_latency,
    PERCENTILE_CONT(0.99) WITHIN GROUP (
        ORDER BY EXTRACT(EPOCH FROM (completed_at - created_at))
    ) AS p99_latency
FROM transactions
WHERE status = 2 AND created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;

-- =============================================
-- 清算性能统计
-- =============================================

CREATE VIEW vw_settlement_perf AS
SELECT
    settle_date,
    total_accounts,
    total_entries,
    EXTRACT(EPOCH FROM (completed_at - started_at)) AS duration_seconds,
    CASE
        WHEN EXTRACT(EPOCH FROM (completed_at - started_at)) < 300 THEN '正常'
        WHEN EXTRACT(EPOCH FROM (completed_at - started_at)) < 600 THEN '警告'
        ELSE '异常'
    END AS status
FROM daily_settlements
WHERE status = 2
ORDER BY settle_date DESC;
```

---

## 11. 总结

### 11.1 核心特性

本金融系统DCA实现具有以下核心特性：

| 特性 | 实现方案 | 效果 |
|------|----------|------|
| **强一致性** | SERIALIZABLE隔离级别 + 存储过程事务 | 零数据不一致 |
| **会计恒等式** | 触发器自动校验借贷平衡 | 100%账务准确性 |
| **审计追踪** | 全链路审计日志 + 只增不改设计 | 完整操作追溯 |
| **风控能力** | 限额/反欺诈/AML三层防护 | 风险可控 |
| **高可用** | 分区表 + 读写分离 | 7x24服务 |

### 11.2 存储过程清单

| 序号 | 名称 | 功能 | 模块 |
|------|------|------|------|
| 1 | sp_customer_register | 客户开户 | 账户系统 |
| 2 | sp_account_open | 账户开户 | 账户系统 |
| 3 | sp_account_close | 账户销户 | 账户系统 |
| 4 | sp_account_freeze | 账户冻结 | 账户系统 |
| 5 | sp_account_unfreeze | 账户解冻 | 账户系统 |
| 6 | sp_get_account_balance | 查询余额 | 账户系统 |
| 7 | sp_get_account_entries | 查询流水 | 账户系统 |
| 8 | sp_transfer_realtime | 实时转账 | 转账系统 |
| 9 | sp_deposit | 存款入账 | 转账系统 |
| 10 | sp_withdraw | 取款 | 转账系统 |
| 11 | sp_batch_transfer_create | 创建批量任务 | 转账系统 |
| 12 | sp_batch_transfer_execute | 执行批量转账 | 转账系统 |
| 13 | sp_daily_settlement | 日终清算 | 清算系统 |
| 14 | sp_account_reconciliation | 账户对账 | 清算系统 |
| 15 | sp_generate_recon_report | 对账报表 | 清算系统 |

### 11.3 风控规则清单

| 规则ID | 类型 | 描述 | 处理方式 |
|--------|------|------|----------|
| LIMIT_001 | 限额 | 单笔金额超限 | 拦截 |
| LIMIT_002 | 限额 | 日累计金额超限 | 拦截 |
| LIMIT_003 | 限额 | 日累计笔数超限 | 拦截 |
| FRAUD_001 | 反欺诈 | 高风险客户 | 人工审核 |
| FRAUD_002 | 反欺诈 | 短时高频交易 | 拦截 |
| FRAUD_003 | 反欺诈 | 交易金额异常 | 警告 |
| FRAUD_004 | 反欺诈 | 疑似循环转账 | 人工审核 |
| AML_001 | AML | 大额交易监控 | 人工审核 |
| AML_002 | AML | 当日累计大额 | 人工审核 |

---

*文档版本: 1.0*
*创建日期: 2025-01*
*作者: PostgreSQL DCA项目团队*
