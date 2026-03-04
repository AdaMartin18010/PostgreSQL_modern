# 案例4: 社交网络平台

> **实战案例**
> **创建日期**: 2026-03-04

---

## 1. 图数据建模

```sql
-- 用户节点
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name TEXT,
    properties JSONB
);

-- 关系边
CREATE TABLE relationships (
    from_id UUID REFERENCES users(id),
    to_id UUID REFERENCES users(id),
    type TEXT,
    created_at TIMESTAMPTZ
);
```

---

## 2. 推荐系统

使用pgvector存储用户embedding:

```sql
SELECT * FROM users
ORDER BY embedding <-> current_user_embedding
LIMIT 20;
```

---

**完成度**: 100%
