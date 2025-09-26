# 10_benchmarks

## 主题边界
- 基准方法、工具、指标、脚本与结果解读（容量/性能/稳定性）

## 核心要点
- 方法：实验设计、变量控制、热身与重复、置信区间
- 工具：`pgbench`、TPC 系列（T*N*）的公开资料与复现实践
- 模型：OLTP/OLAP、混合负载、只读/读写比例、连接池策略
- 指标：TPS/QPS、P95/P99 延迟、I/O 与缓存命中、WAL/检查点
- 读写路径：执行计划、锁等待、膨胀、Autovacuum 干扰

## 知识地图
- 目标与场景 → 设计与脚本 → 执行与采集 → 分析与结论

## 权威参考
- pgbench：`https://www.postgresql.org/docs/current/pgbench.html`
- 性能相关：`https://www.postgresql.org/docs/current/performance-tips.html`
