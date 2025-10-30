# OLTP 变更前后对照模板

## 变更信息

- 变更类型：参数/索引/模式/版本/架构
- 变更描述：
- 风险与回滚预案：

## 压测/流量信息

- 负载类型：只读/读写/混合；并发/连接池
- 持续时间与预热：
- 脚本与版本：链接到 `10_benchmarks/*`

## 指标对照（前 vs 后）

- TPS/QPS：
- 延迟：P50/P95/P99（读/写）
- 热点 SQL（avg*time/calls/shared_blks*\*）：
- 锁与等待（blocked/wait_event）：
- WAL/Checkpoint：wal*bytes/checkpoint*\*：
- Autovacuum：运行与干扰：
- 资源：CPU/内存/IO/网络：

## 结论与行动

- 是否达标：
- 下一步：参数/索引/代码/架构调整建议
