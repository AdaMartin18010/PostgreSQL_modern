# 09_deployment_ops

> 版本对标（更新于 2025-10）

## 主题边界

- 部署、配置、备份恢复、监控告警、容量/性能调优、安全与合规、HA/故障切换

## 核心要点

- 部署与配置：版本选择、参数基线（`shared_buffers`, `work_mem`, `maintenance_work_mem`,
  `max_connections` 等）
- 备份恢复：`pg_basebackup`、`pg_dump/pg_restore`、归档与 PITR、校验与演练
- 高可用：物理复制/逻辑复制、复制槽、故障切换、同步/异步策略
- 监控与告警：`pg_stat_*`、`pg_stat_statements`、WAL/复制延迟、膨胀指标、OS 资源
- 安全：角色/权限、SSL/TLS、行级安全（RLS）、审计与日志（`jsonlog`）
- 调优：索引/统计、热点行与锁等待、Autovacuum 参数、I/O 与检查点

## 运维清单（Checklist）

- 周期：每日/每周/每月巡检项与脚本
- 变更：参数变更评审、回滚预案、容量评估与扩容计划

## 权威参考

- 官方配置：`<https://www.postgresql.org/docs/current/runtime-config.html`>
- 备份与恢复：`<https://www.postgresql.org/docs/current/backup.html`>
- 监控统计：`<https://www.postgresql.org/docs/current/monitoring-stats.html`>
- pg_stat_statements：`<https://www.postgresql.org/docs/current/pgstatstatements.html`>
