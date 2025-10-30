# 复制与拓扑（主从/主备/一主多从/级联/分布式概览）

## 概览

- 物理复制：基于 WAL 的字节级复制；典型用于主备/只读从库
- 逻辑复制：库/表级复制（发布/订阅）；支持行过滤/列列表/跨版本迁移

## 常见拓扑

- 主备（Primary-Standby）：1 主 + 1 备，备库只读
- 一主多从（Primary-Read Replicas）：1 主 + N 只读副本
- 级联复制（Cascading）：从库再向下游复制，降低主库压力
- 同步/异步：
  - 同步：提交需等待副本确认（更高一致性、更高延迟）
  - 异步：主库提交不等待副本（更低延迟、可能数据丢失窗口）
- 延迟只读副本：人为延迟回放，作为“误删回滚”缓冲

## 参数要点（示例）

- 主库：`wal_level=replica`/`logical`、`max_wal_senders`、`synchronous_standby_names`
- 从库：`primary_conninfo`、`primary_slot_name`、`hot_standby=on`
- 槽与归档：`wal_keep_size`/`replication slots`、归档/清理策略

## 典型部署步骤（物理复制）

1. 主库开启 WAL 与复制参数，创建复制槽（可选）
2. 基础备份：`pg_basebackup -D $DATADIR -R -C -S slot_name`
3. 启动从库，验证 `pg_stat_wal_receiver`、`pg_stat_replication`

## 逻辑复制（发布/订阅）

- 发布端：`CREATE PUBLICATION ... FOR TABLE ...`
- 订阅端：`CREATE SUBSCRIPTION ... CONNECTION '...' PUBLICATION ...`
- 用途：跨版本/跨库同步、子集复制、在线迁移

## 故障切换与演练（概要）

- 计划切换：Promote 备库、应用切换连接、旧主以只读或重新加入
- 非计划切换：依据仲裁/探测（外部工具）自动提升；确保写入幂等与冲突处理
- 级联拓扑演练：验证下游自动跟随与回切

## 分布式概览

- Citus 等分布式扩展：面向水平扩展与并行查询（见 `07_extensions/citus`）
- 与复制关系：分布式系统内部也可结合物理/逻辑复制实现 HA 与迁移

## 参考

- 物理复制：`<https://www.postgresql.org/docs/current/warm-standby.html`>
- 逻辑复制：`<https://www.postgresql.org/docs/current/logical-replication.html`>
