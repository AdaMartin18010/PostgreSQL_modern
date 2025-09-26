# 采集清单（Benchmarks）

- 基础：TPS/QPS、P95/P99、CPU/内存、I/O、网络
- PostgreSQL：检查点、WAL 写入、bgwriter、Autovacuum 活动
- 视图/函数：pg_stat_statements、pg_stat_activity、pg_locks、pg_stat_io（若有）
- 建议：热身 ≥5 分钟；多次重复并给出均值/方差；固定随机种子
