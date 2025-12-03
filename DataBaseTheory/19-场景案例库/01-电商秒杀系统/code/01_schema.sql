-- ============================================
-- 电商秒杀系统 - 数据库Schema
-- PostgreSQL 18.x
-- 创建日期: 2025-12-04
-- ============================================

-- 设置客户端编码
SET client_encoding = 'UTF8';

-- ============================================
-- 1. 创建数据库（如果不存在）
-- ============================================

-- 注意：需要以超级用户身份执行
-- CREATE DATABASE seckill ENCODING 'UTF8' LC_COLLATE='C' LC_CTYPE='C' TEMPLATE=template0;

-- \c seckill

-- ============================================
-- 2. 启用必要的扩展
-- ============================================

-- PostgreSQL 18向量扩展（用于AI功能）
CREATE EXTENSION IF NOT EXISTS vector;

-- 定时任务扩展
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- UUID生成
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ⭐ PostgreSQL 18：UUIDv7支持
-- SELECT gen_random_uuidv7();  -- 时间有序的UUID

-- ============================================
-- 3. 创建Schema
-- ============================================

CREATE SCHEMA IF NOT EXISTS seckill;
SET search_path TO seckill, public;

-- ============================================
-- 4. 用户表
-- ============================================

CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),

    -- 风控字段
    risk_level INT DEFAULT 0 CHECK (risk_level BETWEEN 0 AND 10),
    is_blacklist BOOLEAN DEFAULT FALSE,

    status VARCHAR(20) DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'banned')),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

-- 索引
CREATE INDEX idx_users_phone ON users(phone) WHERE status = 'active';
CREATE INDEX idx_users_email ON users(email) WHERE status = 'active';
CREATE INDEX idx_users_risk ON users(risk_level) WHERE risk_level > 5;
CREATE INDEX idx_users_status ON users(status, created_at DESC);

-- 注释
COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.risk_level IS '风险等级：0-10，>5需要额外验证';

-- ============================================
-- 5. 商品表
-- ============================================

CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    normal_price NUMERIC(10,2) NOT NULL CHECK (normal_price > 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    category_id INT,
    brand VARCHAR(100),
    image_urls TEXT[],
    attributes JSONB,
    status VARCHAR(20) DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'deleted')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- 索引
CREATE INDEX idx_products_category ON products(category_id)
    WHERE status = 'active';
CREATE INDEX idx_products_status ON products(status, created_at DESC);

-- ⭐ PostgreSQL 18：JSONB GIN索引优化
CREATE INDEX idx_products_attrs ON products USING GIN (attributes jsonb_path_ops);

-- 全文搜索索引
CREATE INDEX idx_products_search ON products USING GIN (
    to_tsvector('simple', name || ' ' || COALESCE(description, ''))
);

-- 注释
COMMENT ON TABLE products IS '商品基础信息表';
COMMENT ON COLUMN products.attributes IS '商品属性(JSONB)：{"color": "red", "size": "L"}';

-- ============================================
-- 6. 秒杀活动表（核心表）
-- ============================================

CREATE TABLE flash_sales (
    sale_id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    flash_price NUMERIC(10,2) NOT NULL CHECK (flash_price > 0),
    total_stock INT NOT NULL CHECK (total_stock > 0),
    remaining_stock INT NOT NULL CHECK (remaining_stock >= 0),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'active', 'finished', 'cancelled')),

    -- 乐观锁版本号
    version INT DEFAULT 0 NOT NULL,

    -- 统计字段
    view_count BIGINT DEFAULT 0,
    click_count BIGINT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 约束
    CONSTRAINT chk_flash_sales_time CHECK (end_time > start_time),
    CONSTRAINT chk_flash_sales_stock CHECK (remaining_stock <= total_stock)
);

-- 索引
-- ⭐ PostgreSQL 18：B-tree Skip Scan优化
CREATE INDEX idx_flash_sales_time_status
ON flash_sales(status, start_time, end_time);

CREATE INDEX idx_flash_sales_product
ON flash_sales(product_id, status);

-- 部分索引（只索引活跃活动）
CREATE INDEX idx_flash_sales_active
ON flash_sales(sale_id, remaining_stock)
INCLUDE (flash_price, start_time, end_time)
WHERE status IN ('pending', 'active');

-- ⭐ PostgreSQL 18：多变量统计
CREATE STATISTICS flash_sales_stats (dependencies, ndistinct)
ON sale_id, product_id, remaining_stock FROM flash_sales;

-- 注释
COMMENT ON TABLE flash_sales IS '秒杀活动表';
COMMENT ON COLUMN flash_sales.version IS '乐观锁版本号';
COMMENT ON COLUMN flash_sales.remaining_stock IS '剩余库存，防止超卖';

-- ============================================
-- 7. 秒杀订单表（分区表）
-- ============================================

CREATE TABLE flash_orders (
    order_id BIGSERIAL,
    sale_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    quantity INT DEFAULT 1 CHECK (quantity > 0),
    total_amount NUMERIC(10,2) GENERATED ALWAYS AS (price * quantity) STORED,

    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'paid', 'cancelled', 'refunded')),

    payment_method VARCHAR(20),
    transaction_id VARCHAR(100),

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    paid_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,

    PRIMARY KEY (order_id, created_at),
    CONSTRAINT uq_flash_orders_user_sale UNIQUE (sale_id, user_id)
) PARTITION BY RANGE (created_at);

-- 创建分区（当前月+未来2个月）
CREATE TABLE flash_orders_2025_12 PARTITION OF flash_orders
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE TABLE flash_orders_2026_01 PARTITION OF flash_orders
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE flash_orders_2026_02 PARTITION OF flash_orders
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- 索引（自动应用到所有分区）
CREATE INDEX idx_flash_orders_user ON flash_orders(user_id, created_at DESC);
CREATE INDEX idx_flash_orders_sale ON flash_orders(sale_id, status, created_at DESC);
CREATE INDEX idx_flash_orders_status ON flash_orders(status, created_at)
    WHERE status IN ('pending', 'paid');

-- 注释
COMMENT ON TABLE flash_orders IS '秒杀订单表（按月分区）';
COMMENT ON COLUMN flash_orders.total_amount IS '总金额（计算列）';

-- ============================================
-- 8. 秒杀日志表（按天分区）
-- ============================================

CREATE TABLE flash_logs (
    log_id BIGSERIAL,
    sale_id BIGINT NOT NULL,
    user_id BIGINT,
    action VARCHAR(50) NOT NULL,
    result VARCHAR(20),
    error_message TEXT,
    ip_address INET,
    user_agent TEXT,
    request_time TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    response_time_ms INT,

    PRIMARY KEY (log_id, request_time)
) PARTITION BY RANGE (request_time);

-- 创建今天和未来7天的分区
CREATE TABLE flash_logs_2025_12_04 PARTITION OF flash_logs
    FOR VALUES FROM ('2025-12-04') TO ('2025-12-05');

-- 索引
CREATE INDEX idx_flash_logs_sale ON flash_logs(sale_id, request_time);
CREATE INDEX idx_flash_logs_user ON flash_logs(user_id, action, request_time);

-- 注释
COMMENT ON TABLE flash_logs IS '秒杀日志表（按天分区，保留7天）';

-- ============================================
-- 9. 通用函数
-- ============================================

-- 自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 应用到需要的表
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_flash_sales_updated_at
    BEFORE UPDATE ON flash_sales
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 10. 防超卖触发器
-- ============================================

CREATE OR REPLACE FUNCTION prevent_oversell()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.remaining_stock < 0 THEN
        RAISE EXCEPTION '超卖检测：sale_id=%, remaining_stock=%',
            NEW.sale_id, NEW.remaining_stock
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_flash_sales_prevent_oversell
    BEFORE UPDATE ON flash_sales
    FOR EACH ROW
    WHEN (NEW.remaining_stock <> OLD.remaining_stock)
    EXECUTE FUNCTION prevent_oversell();

-- ============================================
-- 11. 自动创建分区函数
-- ============================================

CREATE OR REPLACE FUNCTION create_flash_orders_partitions()
RETURNS void AS $$
DECLARE
    start_date DATE;
    end_date DATE;
    partition_name TEXT;
BEGIN
    -- 创建未来3个月的分区
    FOR i IN 0..2 LOOP
        start_date := DATE_TRUNC('month', NOW() + (i || ' months')::INTERVAL)::DATE;
        end_date := (start_date + INTERVAL '1 month')::DATE;
        partition_name := 'flash_orders_' || TO_CHAR(start_date, 'YYYY_MM');

        -- 检查分区是否存在
        IF NOT EXISTS (
            SELECT 1 FROM pg_class WHERE relname = partition_name
        ) THEN
            EXECUTE FORMAT(
                'CREATE TABLE %I PARTITION OF flash_orders FOR VALUES FROM (%L) TO (%L)',
                partition_name, start_date, end_date
            );
            RAISE NOTICE '创建分区: %', partition_name;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 定时任务：每天凌晨3点创建分区
SELECT cron.schedule('create-partitions', '0 3 * * *',
    'SELECT create_flash_orders_partitions()');

-- ============================================
-- 12. 清理旧数据函数
-- ============================================

CREATE OR REPLACE FUNCTION cleanup_old_flash_logs()
RETURNS void AS $$
DECLARE
    partition_name TEXT;
    partition_date DATE;
BEGIN
    -- 删除7天前的日志分区
    FOR partition_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'seckill'
          AND tablename LIKE 'flash_logs_%'
    LOOP
        -- 提取日期
        partition_date := TO_DATE(SUBSTRING(partition_name FROM 12), 'YYYY_MM_DD');

        IF partition_date < CURRENT_DATE - INTERVAL '7 days' THEN
            EXECUTE FORMAT('DROP TABLE IF EXISTS %I', partition_name);
            RAISE NOTICE '删除旧分区: %', partition_name;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 定时任务：每天凌晨4点清理
SELECT cron.schedule('cleanup-logs', '0 4 * * *',
    'SELECT cleanup_old_flash_logs()');

-- ============================================
-- 13. 性能优化配置
-- ============================================

-- 表级配置
ALTER TABLE flash_orders SET (
    autovacuum_enabled = true,
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_vacuum_threshold = 5000,
    autovacuum_analyze_scale_factor = 0.005,
    autovacuum_analyze_threshold = 2500,
    fillfactor = 90  -- 预留10%空间用于HOT更新
);

ALTER TABLE flash_sales SET (
    autovacuum_enabled = true,
    autovacuum_vacuum_scale_factor = 0.02,
    autovacuum_vacuum_threshold = 1000
);

-- ============================================
-- 14. 权限设置
-- ============================================

-- 创建应用用户
CREATE ROLE seckill_app WITH LOGIN PASSWORD 'your_secure_password';

-- 授予权限
GRANT USAGE ON SCHEMA seckill TO seckill_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA seckill TO seckill_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA seckill TO seckill_app;

-- 只读用户（用于从库）
CREATE ROLE seckill_readonly WITH LOGIN PASSWORD 'your_readonly_password';
GRANT USAGE ON SCHEMA seckill TO seckill_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA seckill TO seckill_readonly;

-- ============================================
-- 15. 统计信息收集
-- ============================================

-- 手动分析（首次部署）
ANALYZE users;
ANALYZE products;
ANALYZE flash_sales;
ANALYZE flash_orders;

-- ============================================
-- 完成
-- ============================================

SELECT 'Schema创建完成！' as message;

-- 查看表列表
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'seckill'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
