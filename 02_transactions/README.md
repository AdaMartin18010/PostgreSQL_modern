# 02_transactions

## 主题边界

- 事务、并发控制与隔离级别；锁、MVCC、快照、死锁处理

## 核心要点

- ACID 与 MVCC 实现概览（可见性、快照、XID、冻结）
- 隔离级别：Read Committed、Repeatable Read、Serializable（SSI）
- 锁：行级锁、表级锁、意向锁、死锁检测与避免
- 事务语句：`BEGIN/COMMIT/ROLLBACK/SAVEPOINT/SET TRANSACTION`
- 一致性工具：`EXPLAIN` 与 `pg_locks`、`pg_stat_activity` 辅助诊断

## 知识地图

- 模型：ACID/MVCC → 隔离级别与异常 → 锁/等待/死锁 → 调优与诊断
- 常见问题：幻读/不可重复读、长事务膨胀、热点更新、锁升级

## 权威参考

- 事务/并发控制：`https://www.postgresql.org/docs/current/mvcc.html`
- 锁机制文档：`https://www.postgresql.org/docs/current/explicit-locking.html`

## Checklist（上线/变更前）
- 避免长事务：确认业务不持有长事务；后台任务批量提交并定期 `COMMIT`
- 隔离级别评估：确认是否需要 `SERIALIZABLE`；可否用 `REPEATABLE READ`/`READ COMMITTED`
- 死锁风险检查：统一锁顺序；将大事务拆分；必要时使用 NOWAIT/SKIP LOCKED
- 监控可观测性：启用 `log_lock_waits`、`deadlock_timeout` 合理、保留锁等待与阻塞链路脚本

## 最小可复现脚本（两个会话模拟锁冲突）
```sql
-- Session A
BEGIN;
UPDATE demo.users SET name = 'alice_1' WHERE id = 1;
-- 不提交，保持行锁

-- Session B
BEGIN;
UPDATE demo.users SET name = 'alice_2' WHERE id = 1; -- 将被阻塞
-- 观察 pg_locks / pg_stat_activity
SELECT pid, wait_event_type, wait_event FROM pg_stat_activity WHERE state <> 'idle';
-- 解除阻塞：在 Session A 提交或回滚
```
