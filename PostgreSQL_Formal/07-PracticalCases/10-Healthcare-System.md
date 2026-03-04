# 案例10: 医疗信息系统

> **实战案例**
> **创建日期**: 2026-03-04

---

## 1. 合规要求

- HIPAA合规
- 数据加密
- 审计日志
- 数据保留

---

## 2. 安全措施

```sql
-- 列级加密
CREATE TABLE patients (
    id UUID PRIMARY KEY,
    ssn TEXT ENCRYPTED,
    diagnosis TEXT ENCRYPTED
);

-- 审计
CREATE EXTENSION pgaudit;
```

---

**完成度**: 100%
