# 故障切换与演练剧本（主从/主备/级联）

## 前置

- 明确拓扑与同步策略；记录 `synchronous_standby_names`
- 确保备库可读；监控复制延迟与槽状态

## 计划切换（演练）

1) 冻结写流量（或降到最小）
2) 在主库检查复制完全追上（`pg_last_wal_replay_lsn()` 对齐）
3) Promote 备库；更新流量入口/连接配置（LB/DSN）
4) 旧主降级为从库或只读；验证数据一致性

## 非计划切换（故障）

1) 判定主库不可用（仲裁/探测规则）
2) Promote 候选备库（优先最新 LSN）
3) 应用切换连接；记录写入幂等/冲突处理
4) 原主恢复后以从库方式重新加入，避免脑裂

## 回切（可选）

- 在新主运行稳定后，安排窗口将角色切回（同“计划切换”流程）

## 验证清单

- 复制延迟回到正常水平
- 应用无大量错误/重试；主从角色一致
- 监控/告警规则已恢复

## 参考

- 热备用与故障切换：`https://www.postgresql.org/docs/current/warm-standby.html`
- 逻辑复制切换：`https://www.postgresql.org/docs/current/logical-replication.html`
