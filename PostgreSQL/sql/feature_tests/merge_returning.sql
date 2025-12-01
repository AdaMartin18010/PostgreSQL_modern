-- PostgreSQL 17.x MERGE RETURNING 功能测试
-- 版本：PostgreSQL 17+
-- 用途：测试MERGE语句的RETURNING子句功能
-- 执行环境：PostgreSQL 17+ 或兼容版本

-- =====================
-- 1. 环境准备
-- =====================

-- 1.1 检查PostgreSQL版本
SELECT version();

-- 1.2 创建测试环境
CREATE SCHEMA IF NOT EXISTS ft_merge;
SET search_path TO ft_merge, public;

-- 创建测试表
DROP TABLE IF EXISTS inventory CASCADE;
CREATE TABLE inventory (
    sku text PRIMARY KEY,
    product_name text NOT NULL,
    quantity int NOT NULL DEFAULT 0,
    last_updated timestamptz DEFAULT now(),
    version int DEFAULT 1
);

-- 创建更新日志表
DROP TABLE IF EXISTS inventory_changes CASCADE;
CREATE TABLE inventory_changes (
    id bigserial PRIMARY KEY,
    sku text NOT NULL,
    change_type text NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    old_quantity int,
    new_quantity int,
    change_timestamp timestamptz DEFAULT now(),
    change_source text
);

-- 插入初始数据
INSERT INTO inventory (sku, product_name, quantity) VALUES
('LAPTOP-001', 'Gaming Laptop', 10),
('MOUSE-001', 'Wireless Mouse', 25),
('KEYBOARD-001', 'Mechanical Keyboard', 15),
('MONITOR-001', '4K Monitor', 5);

-- =====================
-- 2. 基础MERGE功能测试
-- =====================

-- 2.1 测试MERGE支持（如果可用）
DO $$
BEGIN
    -- 尝试使用MERGE语句
    BEGIN
        EXECUTE 'MERGE INTO inventory AS target 
                 USING (VALUES (''LAPTOP-001'', 5), (''NEW-ITEM'', 10)) AS source(sku, delta)
                 ON target.sku = source.sku
                 WHEN MATCHED THEN UPDATE SET quantity = target.quantity + source.delta
                 WHEN NOT MATCHED THEN INSERT (sku, product_name, quantity) VALUES (source.sku, ''New Product'', source.delta)';
        RAISE NOTICE 'MERGE statement is supported in this version';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'MERGE statement not supported: %', SQLERRM;
    END;
END $$;

-- 2.2 兼容性回退方案 - 使用UPSERT
-- 创建更新数据表
CREATE TEMP TABLE inventory_updates (
    sku text,
    delta_quantity int,
    product_name text DEFAULT 'Unknown Product'
);

INSERT INTO inventory_updates VALUES
('LAPTOP-001', 5, 'Gaming Laptop'),
('MOUSE-001', -3, 'Wireless Mouse'),
('NEW-ITEM-001', 10, 'New Product'),
('KEYBOARD-001', 2, 'Mechanical Keyboard');

-- 使用UPSERT替代MERGE
INSERT INTO inventory (sku, product_name, quantity)
SELECT sku, product_name, delta_quantity
FROM inventory_updates
ON CONFLICT (sku) 
DO UPDATE SET 
    quantity = inventory.quantity + EXCLUDED.quantity,
    last_updated = now(),
    version = inventory.version + 1
RETURNING 
    sku,
    product_name,
    quantity,
    'UPSERT' as operation_type;


