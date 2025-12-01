-- PostgreSQL 17.x 逻辑复制设置示例
-- 版本：PostgreSQL 17+
-- 用途：配置逻辑复制环境，包括发布者、订阅者和复制槽管理
-- 执行环境：PostgreSQL 17+ 主从环境

-- =====================
-- 1. 环境准备
-- =====================

-- 1.1 检查PostgreSQL版本和配置
SELECT version();
SHOW wal_level;
SHOW max_replication_slots;
SHOW max_wal_senders;

-- 1.2 创建测试环境
CREATE SCHEMA IF NOT EXISTS ft_logical_rep;
SET search_path TO ft_logical_rep, public;

-- =====================
-- 2. 发布者配置
-- =====================

-- 2.1 创建测试表
DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    id bigserial PRIMARY KEY,
    username text UNIQUE NOT NULL,
    email text UNIQUE NOT NULL,
    full_name text NOT NULL,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    is_active boolean DEFAULT true,
    metadata jsonb
);

DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders (
    id bigserial PRIMARY KEY,
    user_id bigint NOT NULL REFERENCES users(id),
    order_number text UNIQUE NOT NULL,
    total_amount numeric(10,2) NOT NULL,
    status text NOT NULL DEFAULT 'pending',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    shipping_address jsonb,
    order_items jsonb
);

DROP TABLE IF EXISTS order_items CASCADE;
CREATE TABLE order_items (
    id bigserial PRIMARY KEY,
    order_id bigint NOT NULL REFERENCES orders(id),
    product_id text NOT NULL,
    product_name text NOT NULL,
    quantity int NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    total_price numeric(10,2) NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- 2.2 创建索引
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_orders_user_id ON orders (user_id);
CREATE INDEX idx_orders_status ON orders (status);
CREATE INDEX idx_orders_created_at ON orders (created_at);
CREATE INDEX idx_order_items_order_id ON order_items (order_id);
CREATE INDEX idx_order_items_product_id ON order_items (product_id);

-- 2.3 插入测试数据
INSERT INTO users (username, email, full_name, metadata) VALUES
('john_doe', 'john@example.com', 'John Doe', '{"preferences": {"theme": "dark"}, "subscription": "premium"}'),
('jane_smith', 'jane@example.com', 'Jane Smith', '{"preferences": {"theme": "light"}, "subscription": "basic"}'),
('bob_wilson', 'bob@example.com', 'Bob Wilson', '{"preferences": {"theme": "auto"}, "subscription": "premium"}'),
('alice_brown', 'alice@example.com', 'Alice Brown', '{"preferences": {"theme": "dark"}, "subscription": "basic"}'),
('charlie_davis', 'charlie@example.com', 'Charlie Davis', '{"preferences": {"theme": "light"}, "subscription": "premium"}');

INSERT INTO orders (user_id, order_number, total_amount, status, shipping_address, order_items) VALUES
(1, 'ORD-001', 299.99, 'completed', '{"street": "123 Main St", "city": "New York", "state": "NY", "zip": "10001"}', 
 '[{"product_id": "LAPTOP-001", "name": "Gaming Laptop", "qty": 1, "price": 299.99}]'),
(2, 'ORD-002', 89.98, 'shipped', '{"street": "456 Oak Ave", "city": "Los Angeles", "state": "CA", "zip": "90210"}',
 '[{"product_id": "MOUSE-001", "name": "Wireless Mouse", "qty": 2, "price": 44.99}]'),
(3, 'ORD-003', 149.99, 'pending', '{"street": "789 Pine St", "city": "Chicago", "state": "IL", "zip": "60601"}',
 '[{"product_id": "KEYBOARD-001", "name": "Mechanical Keyboard", "qty": 1, "price": 149.99}]');

INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, total_price) VALUES
(1, 'LAPTOP-001', 'Gaming Laptop', 1, 299.99, 299.99),
(2, 'MOUSE-001', 'Wireless Mouse', 2, 44.99, 89.98),
(3, 'KEYBOARD-001', 'Mechanical Keyboard', 1, 149.99, 149.99);

-- =====================
-- 3. 逻辑复制配置
-- =====================

-- 3.1 创建发布（Publisher）
-- 注意：需要超级用户权限
DO $$
BEGIN
    -- 检查是否已存在发布
    IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'ft_users_orders') THEN
        -- 创建发布
        EXECUTE 'CREATE PUBLICATION ft_users_orders FOR TABLE users, orders, order_items';
        RAISE NOTICE 'Publication ft_users_orders created successfully';
    ELSE
        RAISE NOTICE 'Publication ft_users_orders already exists';
    END IF;
END $$;

-- 3.2 创建复制用户
DO $$
BEGIN
    -- 检查复制用户是否存在
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'replication_user') THEN
        -- 创建复制用户
        EXECUTE 'CREATE ROLE replication_user WITH REPLICATION LOGIN PASSWORD ''replication_password''';
        RAISE NOTICE 'Replication user created successfully';
    ELSE
        RAISE NOTICE 'Replication user already exists';
    END IF;
END $$;

-- 3.3 授权复制权限
GRANT CONNECT ON DATABASE postgres TO replication_user;
GRANT USAGE ON SCHEMA ft_logical_rep TO replication_user;
GRANT SELECT ON ALL TABLES IN SCHEMA ft_logical_rep TO replication_user;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA ft_logical_rep TO replication_user;

-- =====================
-- 4. 复制槽管理
-- =====================

-- 4.1 创建复制槽
DO $$
BEGIN
    -- 检查复制槽是否存在
    IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'ft_logical_slot') THEN
        -- 创建逻辑复制槽
        EXECUTE 'SELECT pg_create_logical_replication_slot(''ft_logical_slot'', ''pgoutput'')';
        RAISE NOTICE 'Logical replication slot ft_logical_slot created successfully';
    ELSE
        RAISE NOTICE 'Logical replication slot ft_logical_slot already exists';
    END IF;
END $$;

-- 4.2 查看复制槽状态
SELECT 
    slot_name,
    plugin,
    slot_type,
    datoid,
    database,
    active,
    xmin,
    catalog_xmin,
    restart_lsn,
    confirmed_flush_lsn
FROM pg_replication_slots 
WHERE slot_name = 'ft_logical_slot';

-- =====================
-- 5. 订阅者配置（模拟）
-- =====================

-- 5.1 订阅者表结构（在订阅者端执行）
/*
-- 在订阅者数据库执行以下命令：

-- 创建订阅
CREATE SUBSCRIPTION ft_subscription
CONNECTION 'host=localhost port=5432 dbname=postgres user=replication_user password=replication_password'
PUBLICATION ft_users_orders
WITH (copy_data = true);

-- 查看订阅状态
SELECT * FROM pg_subscription;

-- 查看订阅统计
SELECT * FROM pg_stat_subscription;
*/

-- 5.2 生成订阅者配置脚本
SELECT 
    'CREATE SUBSCRIPTION ft_subscription' || chr(10) ||
    'CONNECTION ''host=localhost port=5432 dbname=postgres user=replication_user password=replication_password''' || chr(10) ||
    'PUBLICATION ft_users_orders' || chr(10) ||
    'WITH (copy_data = true);' as subscription_sql;

-- =====================
-- 6. 复制监控
-- =====================

-- 6.1 发布者监控
SELECT 
    'Publisher Statistics' as info,
    count(*) as total_publications
FROM pg_publication;

SELECT 
    pubname as publication_name,
    puballtables as all_tables,
    pubinsert as insert_enabled,
    pubupdate as update_enabled,
    pubdelete as delete_enabled,
    pubtruncate as truncate_enabled
FROM pg_publication_tables 
WHERE pubname = 'ft_users_orders';

-- 6.2 复制槽监控
SELECT 
    slot_name,
    plugin,
    slot_type,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) as lag_size,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) as lag_bytes
FROM pg_replication_slots 
WHERE slot_name = 'ft_logical_slot';

-- 6.3 WAL统计
SELECT 
    'WAL Statistics' as info,
    pg_current_wal_lsn() as current_lsn,
    pg_walfile_name(pg_current_wal_lsn()) as current_wal_file;

-- =====================
-- 7. 数据变更测试
-- =====================

-- 7.1 插入新数据
INSERT INTO users (username, email, full_name, metadata) VALUES
('test_user', 'test@example.com', 'Test User', '{"preferences": {"theme": "dark"}}');

INSERT INTO orders (user_id, order_number, total_amount, status) VALUES
(6, 'ORD-004', 199.99, 'pending');

-- 7.2 更新数据
UPDATE users SET 
    full_name = 'John Doe Updated',
    updated_at = now(),
    metadata = jsonb_set(metadata, '{preferences,theme}', '"light"')
WHERE username = 'john_doe';

UPDATE orders SET 
    status = 'shipped',
    updated_at = now()
WHERE order_number = 'ORD-003';

-- 7.3 删除数据
DELETE FROM order_items WHERE order_id = 2;

-- =====================
-- 8. 故障转移和恢复
-- =====================

-- 8.1 检查复制延迟
SELECT 
    slot_name,
    active,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) as lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) as lag_size
FROM pg_replication_slots;

-- 8.2 复制槽清理（谨慎使用）
/*
-- 删除复制槽（仅在确认不再需要时执行）
SELECT pg_drop_replication_slot('ft_logical_slot');
*/

-- 8.3 发布管理
-- 添加表到发布
-- ALTER PUBLICATION ft_users_orders ADD TABLE new_table;

-- 从发布中移除表
-- ALTER PUBLICATION ft_users_orders DROP TABLE old_table;

-- =====================
-- 9. 性能优化
-- =====================

-- 9.1 复制参数优化
SELECT 
    name,
    setting,
    unit,
    context,
    short_desc
FROM pg_settings 
WHERE name IN (
    'wal_level',
    'max_replication_slots',
    'max_wal_senders',
    'wal_sender_timeout',
    'wal_receiver_timeout',
    'max_slot_wal_keep_size'
);

-- 9.2 监控复制性能
SELECT 
    'Replication Performance' as info,
    pg_current_wal_lsn() as current_lsn,
    pg_walfile_name(pg_current_wal_lsn()) as current_wal_file,
    pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') as total_wal_bytes;

-- =====================
-- 10. 清理和总结
-- =====================

-- 10.1 显示配置摘要
SELECT 
    'Logical Replication Setup Summary' AS test_name,
    count(*) AS total_tables,
    (SELECT count(*) FROM pg_publication WHERE pubname = 'ft_users_orders') AS publications,
    (SELECT count(*) FROM pg_replication_slots WHERE slot_name = 'ft_logical_slot') AS replication_slots;

-- 10.2 清理测试数据（可选）
-- DROP PUBLICATION IF EXISTS ft_users_orders;
-- DROP ROLE IF EXISTS replication_user;
-- SELECT pg_drop_replication_slot('ft_logical_slot');
-- DROP SCHEMA IF EXISTS ft_logical_rep CASCADE;

-- =====================
-- 11. 最佳实践建议
-- =====================

/*
逻辑复制最佳实践：

1. 配置要求：
   - wal_level 必须设置为 'logical'
   - max_replication_slots 和 max_wal_senders 需要适当配置
   - 确保有足够的磁盘空间存储WAL文件

2. 监控要点：
   - 定期检查复制槽状态和延迟
   - 监控WAL文件大小和清理
   - 关注复制连接状态

3. 故障处理：
   - 复制槽延迟过大时检查网络和订阅者状态
   - WAL文件积压时考虑增加磁盘空间或调整参数
   - 定期清理不需要的复制槽

4. 性能优化：
   - 合理设置复制参数
   - 使用适当的索引提高复制效率
   - 考虑分区表减少单次复制数据量

5. 安全考虑：
   - 使用专用复制用户
   - 限制复制用户权限
   - 使用SSL连接保护数据传输
*/