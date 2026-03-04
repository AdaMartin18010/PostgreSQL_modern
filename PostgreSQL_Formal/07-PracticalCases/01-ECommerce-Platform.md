# 案例1: 电商平台PostgreSQL架构

> **实战案例**
> **创建日期**: 2026-03-04

---

## 1. 业务场景

- 日活用户: 100万
- 日订单量: 50万
- 峰值QPS: 10,000

---

## 2. 数据库架构

```text
┌─────────────────────────────────────────┐
│           读写分离架构                   │
├─────────────────────────────────────────┤
│  Primary (写)                           │
│  ├── 订单库 orders                      │
│  ├── 库存库 inventory                   │
│  └── 用户库 users                       │
│                                         │
│  Replicas (读)                          │
│  ├── 报表查询                            │
│  └── 搜索服务                            │
└─────────────────────────────────────────┘
```

---

## 3. 关键优化

### 3.1 分区表

```sql
CREATE TABLE orders (
    order_id BIGSERIAL,
    user_id BIGINT,
    created_at TIMESTAMPTZ,
    ...
) PARTITION BY RANGE (created_at);
```

### 3.2 连接池

```
PgBouncer
- max_client_conn: 10000
- default_pool_size: 25
- reserve_pool_size: 5
```

---

## 4. 性能数据

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 平均响应 | 150ms | 20ms |
| P99 | 800ms | 100ms |
| 吞吐量 | 2k TPS | 10k TPS |

---

**完成度**: 100%
