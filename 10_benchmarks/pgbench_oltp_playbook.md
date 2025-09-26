# pgbench OLTP Playbook（示例）

## 配置建议
- 连接池：固定并发，避免连接风暴（如 pgbouncer transaction 模式）
- 参数基线：shared_buffers、work_mem、wal_compression、checkpoint_timeout、max_wal_size
- 预热：加载热点数据/预跑 5-10 分钟至稳态

## 基准场景
- 只读：`-S`
- 读写混合：默认脚本（含转账/余额查询等）
- 自定义：按业务热点建脚本，区分读写比例

## 命令示例
```bash
# 初始化并以 10 倍扩展
pgbench -i -s 10
# 读写 60s，16 并发，1 线程
pgbench -T 60 -c 16 -j 1
# 只读 60s
pgbench -S -T 60 -c 32 -j 2
# 使用自定义脚本
pgbench -T 120 -c 32 -j 4 -f select_only.sql -f write_hot.sql
```

## 结果采集
- TPS（including/excluding connections）、平均/中位/分位延迟
- 结合 `pg_stat_statements` 汇总热点 SQL 的平均耗时与 I/O
- 结合系统指标看 CPU/I/O 等瓶颈
