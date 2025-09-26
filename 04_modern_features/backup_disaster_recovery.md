# 备份与容灾（全量/增量/恢复/主从互换/演练）

## 备份类型
- 全量备份：`pg_basebackup`（物理）、`pg_dump/pg_restore`（逻辑）
- 增量/持续归档：WAL 归档（`archive_mode=on` + `archive_command`）
- 逻辑层 CDC：逻辑复制/发布订阅（子集迁移与容灾补充）

## 方案组合
- 物理：基础全量 + WAL 归档（PITR）→ 恢复到任意时间点
- 逻辑：跨版本/跨库迁移、子集恢复；与物理方案互补
- 冷/热/温备：RPO/RTO 目标驱动选择

## 恢复流程（PITR 概要）
1) 准备基础备份与 WAL 归档可用性
2) 清理数据目录，恢复基础备份
3) 配置 `restore_command` 与目标（`recovery_target_time/lsn`）
4) 启动并验证（校验点、业务校验）

## 主从互换（计划演练）
- 前置：确认复制追平、冻结写入
- 步骤：Promote 备库 → 应用切换入口 → 旧主以从库方式回归
- 验证：一致性校验、监控指标恢复

## 容灾演练
- 周期执行：PITR 演练、主从切换与回切、只读副本延迟回放回退
- 验收标准：RPO/RTO 达标、脚本化可重复、变更记录完备

## 注意事项
- 归档清理策略与复制槽保留；防止 WAL 累积
- 一致性校验（校验和、逻辑校验）与备份有效性检查

## 参考
- 备份与恢复：`https://www.postgresql.org/docs/current/backup.html`
- 热备用/故障切换：`https://www.postgresql.org/docs/current/warm-standby.html`
- 逻辑复制：`https://www.postgresql.org/docs/current/logical-replication.html`
