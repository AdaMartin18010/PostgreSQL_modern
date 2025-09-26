# 04_modern_features

## 主题边界
- 分区、复制（物理/逻辑）、高可用、备份恢复、全文检索、扩展机制、外部数据源（FDW）

## 核心要点
- 分区：范围/列表/哈希；全局索引策略与维护
- 复制与 HA：流复制、槽、故障切换；逻辑复制（库/表级、行过滤/列列表）
- 备份恢复：`pg_basebackup`、`pg_dump/pg_restore`、归档与时间点恢复（PITR）
- 检索与搜索：全文检索（TSVector/TSQuery）、模糊/相似度
- 可扩展性：`CREATE EXTENSION`、FDW（如 `postgres_fdw`、`mysql_fdw`）

## 知识地图
- 数据生命周期与可用性 → 复制/备份/恢复 → 扩展与集成 → 安全与审计

## 权威参考
- 复制：`https://www.postgresql.org/docs/current/logical-replication.html`
- 备份与恢复：`https://www.postgresql.org/docs/current/backup.html`
- 全文检索：`https://www.postgresql.org/docs/current/textsearch.html`
