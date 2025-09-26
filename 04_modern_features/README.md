# 04_modern_features

> 版本对标（更新于 2025-09）

## 主题边界

- 分区、复制（物理/逻辑）、高可用、备份恢复、全文检索、扩展机制、外部数据源（FDW）

## 核心要点

- 分区：范围/列表/哈希；全局索引策略与维护
- 复制与 HA：流复制（主备/一主多从/级联、同步/异步/延迟只读）、逻辑复制（库/表/过滤）
- 备份恢复：`pg_basebackup`、`pg_dump/pg_restore`、WAL 归档与 PITR
- 检索与搜索：全文检索（TSVector/TSQuery）、模糊/相似度
- 可扩展性：`CREATE EXTENSION`、FDW（如 `postgres_fdw`、`mysql_fdw`）

## 知识地图

- 数据生命周期与可用性 → 复制/备份/恢复 → 扩展与集成 → 安全与审计

## 权威参考

- 复制：`https://www.postgresql.org/docs/current/logical-replication.html`
- 备份与恢复：`https://www.postgresql.org/docs/current/backup.html`
- 全文检索：`https://www.postgresql.org/docs/current/textsearch.html`

## Checklist（上线/演练）

- 分区键与热点写入评估；子分区数量与维护策略清晰
- 物理复制延迟与槽监控；故障切换剧本（演练含回切）
- 逻辑复制：行过滤/列列表正确；冲突处理与重放策略明确
- 备份与恢复：定期校验备份可用性；PITR 演练有记录
- 全文检索：词典/配置确认；统计与计划符合预期

## 最小可复现脚本（逻辑复制最小集）

```sql
-- 在发布端（publisher）
CREATE PUBLICATION pub_demo FOR TABLE demo.events;
-- 在订阅端（subscriber）
CREATE SUBSCRIPTION sub_demo CONNECTION 'host=PUB_HOST dbname=DB user=USER password=PASS'
  PUBLICATION pub_demo;
-- 检查复制进度
SELECT * FROM pg_stat_subscription;
```

## 参考脚本索引

- `logical_replication_min.sql`
- `pitr_example.md`
- `primary_standby_params.md`
- `dr_runbook_templates.sql`

## 复制与高可用

- `replication_topologies.md`
- `failover_playbook.md`

## 备份与容灾

- `backup_disaster_recovery.md`

## 版本差异与迁移

- `version_diff_16_to_17.md`
