# 03_storage_access

## 主题边界

- 物理/逻辑存储、索引类型与选择、统计信息与执行计划、Vacuum/Autovacuum、TOAST

## 核心要点

- 存储与表组织：堆表、分区、TOAST、FILLFACTOR
- 索引：B-tree、Hash、GIN、GiST、BRIN；多列/表达式/部分索引
- 统计与计划：`ANALYZE`、扩展统计、代价估算、`EXPLAIN (ANALYZE, BUFFERS)`
- 维护：`VACUUM/ANALYZE/AUTOVACUUM`、膨胀治理、`REINDEX`、`CLUSTER`

## 知识地图

- 表与索引设计 → 统计与计划 → 维护与膨胀治理 → 性能与容量评估
- 常见陷阱：错配索引、统计失真、顺序/随机 I/O、膨胀与冻结

## 权威参考

- 索引指南：`https://www.postgresql.org/docs/current/indexes.html`
- 计划与分析：`https://www.postgresql.org/docs/current/using-explain.html`
- 维护：`https://www.postgresql.org/docs/current/routine-vacuuming.html`
