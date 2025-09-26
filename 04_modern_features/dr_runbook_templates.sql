-- 备份校验（示意）
-- 校验归档可达与新归档写入
-- SELECT pg_switch_wal(); 检查归档目录新增 WAL 文件

-- 基础备份（示意）
-- pg_basebackup -D /backup/base -X stream -C -S nightly_slot

-- PITR 演练（简化占位）
-- 1) 准备基础备份与 WAL 归档；记录 T_fail
-- 2) 清理数据目录，恢复基础备份
-- 3) 配置 restore_command 与 recovery_target_time='T_fail - 10 seconds'
-- 4) 启动并验证

-- 回切（计划）
-- 在新主稳定后，按 failover_playbook.md 的计划切换流程执行
