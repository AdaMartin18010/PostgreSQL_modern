-- 2PC 最小演示（示意）
-- 注意：需启用并配置支持准备事务的组件/扩展，以下为语义示例

BEGIN;
-- 分片 A
INSERT INTO account_balance(account_id, amount) VALUES (1, -100);
-- 分片 B
INSERT INTO account_balance(account_id, amount) VALUES (2, 100);

-- 准备阶段（由协调者触发）
PREPARE TRANSACTION 'tx_xfer_1';

-- 提交阶段（确认各分片就绪）
COMMIT PREPARED 'tx_xfer_1';

-- 失败回滚示例：
-- ROLLBACK PREPARED 'tx_xfer_1';


