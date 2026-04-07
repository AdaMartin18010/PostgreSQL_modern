# 案例5: SaaS多租户系统

> **实战案例**
> **创建日期**: 2026-03-04

---

## 1. 多租户模式

| 模式 | 优点 | 缺点 |
|------|------|------|
| **独立数据库** | 隔离性好 | 成本高 |
| **共享数据库独立Schema** | 平衡 | 复杂 |
| **共享Schema** | 成本低 | 隔离差 |

---

## 2. RLS实现

```sql
-- 行级安全
CREATE POLICY tenant_isolation ON orders
    USING (tenant_id = current_setting('app.current_tenant')::INT);
```

---

**完成度**: 100%
