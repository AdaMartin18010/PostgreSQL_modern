# OLTP 观测与容量规划

## 目标

- 面向 OLTP 负载的监控指标、瓶颈定位与容量规划方法

## 关键指标（建议采集）

- 延迟：P50/P95/P99（读/写分开），超时比例
- 吞吐：TPS/QPS（区分只读/读写）
- 连接：活跃连接、阻塞队列长度、连接池命中
- 锁与等待：锁类型分布、等待事件（锁/I/O/CPU）
- WAL/检查点：写入速率、检查点间隔与耗时、recovery 延迟
- Autovacuum：触发频率、运行时长、冻结进度
- 资源：CPU/内存/磁盘 I/O/网络带宽与突发

## 采集与看板

- pg_stat_statements：热点 SQL（平均/总耗时、调用次数、共享缓冲命中率）
- pg_stat_activity/pg_locks：阻塞链与等待事件
- OS/容器指标：CPU steal、IO wait、FS 延迟、队列深度
- 建议按场景建立 Grafana/Prometheus 看板（模板占位）

### Grafana 面板示例结构（占位）
- 概览：TPS/P95/P99、错误率、活动连接
- 资源：CPU/内存/IO 带宽与延迟、网络带宽
- PostgreSQL：
  - WAL/Checkpoint：wal_bytes, checkpoints_timed/req, checkpoint_write_time
  - Autovacuum：workers 活动、队列、冻结进度
  - 锁与等待：blocked/backends、wait_event_type 分类
  - SQL 热点：pg_stat_statements topN（avg_time、calls、shared_blks_read/hit）

## 容量规划方法

- 基线测量：在准生产环境用 pgbench/业务压测获取“峰值/均值”指标
- 伸缩模型：根据 CPU 利用率/延迟阈值设定扩容触发（纵向/横向）
- 负载结构：读写比、热点表/索引、事务时长分布与峰谷规律
- 预留冗余：面向故障切换、备份/分析作业的干扰预算

## 执行动作清单（Playbook）

- 监控异常 → 定位（SQL/锁/资源）→ 临时缓解（限流/索引/参数）→ 根因修复（模式/代码/架构）
- 变更前后对照：固定负载回放/基准，比较 P95/P99、pg_stat_* 指标

## 参考脚本

- `../bloat_check.sql`、`../lock_chain.sql`
- `../../10_benchmarks/pgbench_example.md`、`../../10_benchmarks/pgbench_oltp_playbook.md`
