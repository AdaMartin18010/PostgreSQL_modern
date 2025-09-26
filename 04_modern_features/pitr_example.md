# PITR（时间点恢复）示意

> 注意：仅为步骤骨架，实际以环境为准演练。

## 1. 备份与归档

- 启用归档：`archive_mode=on`，配置 `archive_command`
- 基础备份：`pg_basebackup -D /backup/base -X stream -C -S bkp_slot`

## 2. 故障模拟

- 记录当前时间 `T_fail`
- 执行破坏性操作（示意），随后停止服务

## 3. 恢复到时间点

- 清理数据目录并恢复基础备份
- `postgresql.auto.conf` 或 `recovery.signal` 中设置：
  - `restore_command`
  - `recovery_target_time='T_fail - 10 seconds'`
- 启动服务并验证

## 4. 校验

- 检查恢复点、WAL 应用、业务数据一致性
