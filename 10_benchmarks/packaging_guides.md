# 压测脚本打包与复现指引

## 目录结构建议

- scripts/: SQL 与 shell 脚本
- datasets/: 生成/下载的数据集与规模说明
- results/: 结果与图表（含原始与汇总）

## 最小复现

- 环境信息：CPU/内存/磁盘/网络，PostgreSQL/扩展版本
- 初始化：`pgbench -i -s <scale>` 或自定义建表脚本
- 运行：命令行、并发/线程、时长；预热说明
- 采集：pg_stat_statements、系统指标、结果 CSV

## 归档

- 保存脚本、参数、版本信息与结果；给出复现命令与期望区间
