# 03_storage_access

> 版本对标（更新于 2025-10）

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

## Checklist（设计/排错）

- 索引是否与查询谓词匹配（顺序、前缀、表达式/部分索引）
- `ANALYZE` 是否最新；必要时使用扩展统计（多列相关性、NDV）
- 观察 `EXPLAIN (ANALYZE, BUFFERS)`：是否发生意外的 Seq Scan/Bitmap Heap Recheck
- 膨胀治理：Autovacuum 触发是否及时；长事务是否阻碍冻结
- TOAST/大字段：读写路径与压缩权衡；必要时外置存储或拆表

## 最小可复现脚本（索引与计划）

```sql
-- 建表与示例数据
CREATE SCHEMA IF NOT EXISTS demo;
CREATE TABLE IF NOT EXISTS demo.events (
  id bigserial PRIMARY KEY,
  user_id bigint NOT NULL,
  ts timestamptz NOT NULL DEFAULT now(),
  payload text
);
INSERT INTO demo.events(user_id, payload)
SELECT (random()*1000)::int, md5(random()::text)
FROM generate_series(1, 50000);

-- 索引与统计
CREATE INDEX IF NOT EXISTS idx_events_user_ts ON demo.events (user_id, ts);
ANALYZE demo.events;

-- 计划观察
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM demo.events WHERE user_id = 42 ORDER BY ts DESC LIMIT 10;
```

## 参考脚本索引

- `EXPLAIN_example.sql`
- `index_maintenance.sql`
