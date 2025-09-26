# Outbox / Saga 最小链路示例（说明）

本示例说明如何在跨分片写入时，结合 Outbox（事务消息）与 Saga（补偿）降低不一致风险。

## 思路

- 业务写入与 outbox 表同事务提交（同一分片或协调路由确保原子性）
- 异步投递 outbox 记录到消息通道（此处用 SQL 轮询模拟）
- 下游处理失败时记录补偿任务，重放或反向操作

## 建议表结构（示意）

```sql
CREATE TABLE outbox (
  id BIGSERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  delivered BOOLEAN NOT NULL DEFAULT FALSE
);
```

## 执行流程（示意）

1) 业务事务：插入业务表 + 插入 outbox
2) 轮询 outbox：取未投递记录，投递成功后置 delivered=true
3) 异常：写入 compensations 表，后续定时补偿/重放

可结合 `two_phase_commit_min.sql` 观察 2PC 与补偿的取舍与组合。

