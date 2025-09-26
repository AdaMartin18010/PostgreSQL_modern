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
