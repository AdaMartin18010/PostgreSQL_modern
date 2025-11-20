# AI Act 要求解读

> **更新时间**: 2025 年 11 月 1 日  
> **技术版本**: pg_dsr 1.0  
> **文档编号**: 05-02-01

## 📑 目录

- [AI Act 要求解读](#ai-act-要求解读)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 AI Act 背景](#11-ai-act-背景)
    - [1.2 适用范围](#12-适用范围)
  - [2. 核心要求](#2-核心要求)
    - [2.1 数据主权要求](#21-数据主权要求)
    - [2.2 数据留存要求](#22-数据留存要求)
    - [2.3 审计追踪要求](#23-审计追踪要求)
    - [2.4 透明度要求](#24-透明度要求)
  - [3. 合规实施](#3-合规实施)
    - [3.1 数据分类](#31-数据分类)
    - [3.2 访问控制](#32-访问控制)
    - [3.3 审计日志](#33-审计日志)
  - [4. 最佳实践](#4-最佳实践)
  - [5. 参考资料](#5-参考资料)

---

## 1. 概述

### 1.1 AI Act 背景

欧盟 AI Act 于 2025 年正式执行，是首个全面的 AI 监管法规，对 AI 系统的开发、部署和使用提出了严格要求
。

### 1.2 适用范围

AI Act 适用于：

- 在欧盟市场提供 AI 系统的供应商
- 在欧盟使用 AI 系统的用户
- 处理与 AI 系统相关的数据

---

## 2. 核心要求

### 2.1 数据主权要求

**要求内容**:

- 数据必须标注主权标签（国家/地区）
- 禁止未经授权的跨境数据传输
- 必须实现数据本地化存储

**实施方法**:

```sql
-- 创建数据主权标签
ALTER TABLE user_data ADD COLUMN data_sovereignty TEXT[];

-- 设置主权标签
UPDATE user_data
SET data_sovereignty = ARRAY['EU', 'DE']
WHERE user_country = 'Germany';
```

### 2.2 数据留存要求

**要求内容**:

- 必须保留 AI 训练数据
- 必须保留模型版本历史
- 必须保留数据使用记录

**实施方法**:

```sql
-- 创建数据留存表
CREATE TABLE data_retention (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    record_id BIGINT,
    retention_until TIMESTAMPTZ,
    retention_reason TEXT
);
```

### 2.3 审计追踪要求

**要求内容**:

- 所有数据操作必须记录
- 审计日志必须不可篡改
- 必须支持完整追溯

**实施方法**:

```sql
-- 使用 Ledger 表
CREATE TABLE user_data_ledger (
    id BIGSERIAL PRIMARY KEY,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    timestamp TIMESTAMPTZ,
    user_id TEXT,
    hash TEXT
);
```

### 2.4 透明度要求

**要求内容**:

- 必须披露 AI 系统使用的数据
- 必须提供数据来源信息
- 必须支持数据可解释性

---

## 3. 合规实施

### 3.1 数据分类

```sql
-- 数据分类表
CREATE TABLE data_classification (
    table_name TEXT,
    column_name TEXT,
    data_type TEXT,  -- 'personal', 'sensitive', 'public'
    sovereignty_tags TEXT[],
    retention_period INTERVAL
);
```

### 3.2 访问控制

```sql
-- 基于主权的访问控制
CREATE POLICY "sovereignty_access_control"
ON user_data FOR SELECT
USING (
    current_setting('user.country') = ANY(data_sovereignty)
);
```

### 3.3 审计日志

```sql
-- 自动审计日志
CREATE TRIGGER audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON user_data
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();
```

---

## 4. 最佳实践

1. **数据分类**: 对所有数据进行分类和标签
2. **访问控制**: 实施基于主权的访问控制
3. **审计日志**: 启用不可篡改的审计日志
4. **合规监控**: 持续监控合规状态

---

## 5. 参考资料

- [数据库合规架构](../技术原理/数据库合规架构.md)
- [合规实施方案](./合规实施方案.md)
- [欧盟 AI Act 官方文档](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

---

**最后更新**: 2025 年 11 月 1 日  
**维护者**: PostgreSQL Modern Team
