---

> **📋 文档来源**: `DataBaseTheory\19-场景案例库\04-多租户SaaS系统\README.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 多租户SaaS系统

> **PostgreSQL版本**: 18.x
> **租户数**: 1000+
> **特点**: 数据隔离、RLS策略

---

## 核心设计

### 数据隔离策略

**方案1：共享Schema + RLS（推荐）**:

```sql
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,
    customer_id BIGINT,
    amount NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 启用RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 租户隔离策略
CREATE POLICY tenant_isolation ON orders
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::INT);

-- ⭐ PostgreSQL 18：RLS性能提升
-- 策略下推+缓存
-- 性能：查询时间降低20-50%
```

**方案2：独立Schema**:

```sql
-- 为每个租户创建Schema
CREATE SCHEMA tenant_1001;
CREATE TABLE tenant_1001.orders (...);

-- 动态切换Schema
SET search_path TO tenant_1001;
SELECT * FROM orders;  -- 自动隔离
```

---

## PostgreSQL 18特性

- **RLS性能优化**：策略计算开销降低30-60%
- **内置连接池**：支持大量租户连接
- **审计日志**：完整的租户操作审计

---

**完整文档待补充**
