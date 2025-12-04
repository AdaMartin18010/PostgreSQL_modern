-- ============================================
-- 电商秒杀系统 - 核心业务函数
-- PostgreSQL 18.x
-- 创建日期: 2025-12-04
-- ============================================

SET search_path TO seckill, public;

-- ============================================
-- 1. 秒杀下单函数（乐观锁版本）
-- ============================================

CREATE OR REPLACE FUNCTION seckill_create_order(
    p_sale_id BIGINT,
    p_user_id BIGINT,
    p_product_id BIGINT,
    p_price NUMERIC
) RETURNS TABLE (
    success BOOLEAN,
    message TEXT,
    order_id BIGINT,
    remaining_stock INT
) AS $$
DECLARE
    v_order_id BIGINT;
    v_version INT;
    v_remaining INT;
    v_affected INT;
BEGIN
    -- 1. 检查活动状态和获取版本号
    SELECT version, remaining_stock, status, start_time, end_time
    INTO v_version, v_remaining, v_status, v_start, v_end
    FROM flash_sales
    WHERE sale_id = p_sale_id;

    -- 检查活动是否存在
    IF v_version IS NULL THEN
        RETURN QUERY SELECT FALSE, '活动不存在'::TEXT, NULL::BIGINT, 0;
        RETURN;
    END IF;

    -- 检查活动时间
    IF NOW() < v_start THEN
        RETURN QUERY SELECT FALSE, '活动未开始'::TEXT, NULL::BIGINT, v_remaining;
        RETURN;
    END IF;

    IF NOW() > v_end THEN
        RETURN QUERY SELECT FALSE, '活动已结束'::TEXT, NULL::BIGINT, v_remaining;
        RETURN;
    END IF;

    -- 检查活动状态
    IF v_status <> 'active' THEN
        RETURN QUERY SELECT FALSE, format('活动状态异常: %s', v_status), NULL::BIGINT, v_remaining;
        RETURN;
    END IF;

    -- 检查库存
    IF v_remaining <= 0 THEN
        RETURN QUERY SELECT FALSE, '库存不足'::TEXT, NULL::BIGINT, 0;
        RETURN;
    END IF;

    -- 2. 创建订单（INSERT...ON CONFLICT防止重复）
    INSERT INTO flash_orders (sale_id, user_id, product_id, price, status)
    VALUES (p_sale_id, p_user_id, p_product_id, p_price, 'pending')
    ON CONFLICT (sale_id, user_id) DO NOTHING
    RETURNING order_id INTO v_order_id;

    -- 检查是否重复抢购
    IF v_order_id IS NULL THEN
        RETURN QUERY SELECT FALSE, '您已抢购过该商品'::TEXT, NULL::BIGINT, v_remaining;
        RETURN;
    END IF;

    -- 3. 扣减库存（乐观锁CAS操作）
    UPDATE flash_sales
    SET remaining_stock = remaining_stock - 1,
        version = version + 1,
        updated_at = NOW()
    WHERE sale_id = p_sale_id
      AND version = v_version  -- ⬅️ 乐观锁：版本号必须匹配
      AND remaining_stock > 0;  -- ⬅️ 双重检查

    GET DIAGNOSTICS v_affected = ROW_COUNT;

    -- 4. 检查更新结果
    IF v_affected = 0 THEN
        -- 并发冲突：删除刚创建的订单
        DELETE FROM flash_orders WHERE order_id = v_order_id;

        -- 获取最新库存
        SELECT remaining_stock INTO v_remaining
        FROM flash_sales WHERE sale_id = p_sale_id;

        IF v_remaining > 0 THEN
            RETURN QUERY SELECT FALSE, '并发冲突，请重试'::TEXT, NULL::BIGINT, v_remaining;
        ELSE
            RETURN QUERY SELECT FALSE, '库存不足'::TEXT, NULL::BIGINT, 0;
        END IF;
        RETURN;
    END IF;

    -- 5. 成功：返回订单信息
    SELECT remaining_stock INTO v_remaining
    FROM flash_sales WHERE sale_id = p_sale_id;

    RETURN QUERY SELECT TRUE, '抢购成功'::TEXT, v_order_id, v_remaining;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION seckill_create_order IS '秒杀下单（乐观锁版本）';

-- ============================================
-- 2. 库存扣减函数（悲观锁版本，备选）
-- ============================================

CREATE OR REPLACE FUNCTION seckill_create_order_pessimistic(
    p_sale_id BIGINT,
    p_user_id BIGINT,
    p_product_id BIGINT,
    p_price NUMERIC
) RETURNS TABLE (
    success BOOLEAN,
    message TEXT,
    order_id BIGINT
) AS $$
DECLARE
    v_order_id BIGINT;
    v_remaining INT;
BEGIN
    -- 1. 获取行级锁（FOR UPDATE）
    SELECT remaining_stock INTO v_remaining
    FROM flash_sales
    WHERE sale_id = p_sale_id
      AND status = 'active'
    FOR UPDATE;  -- ⬅️ 悲观锁：行级排他锁

    -- 检查库存
    IF v_remaining IS NULL OR v_remaining <= 0 THEN
        RETURN QUERY SELECT FALSE, '库存不足'::TEXT, NULL::BIGINT;
        RETURN;
    END IF;

    -- 2. 创建订单
    INSERT INTO flash_orders (sale_id, user_id, product_id, price, status)
    VALUES (p_sale_id, p_user_id, p_product_id, p_price, 'pending')
    ON CONFLICT (sale_id, user_id) DO NOTHING
    RETURNING order_id INTO v_order_id;

    IF v_order_id IS NULL THEN
        RETURN QUERY SELECT FALSE, '重复抢购'::TEXT, NULL::BIGINT;
        RETURN;
    END IF;

    -- 3. 扣减库存（已持有锁，安全）
    UPDATE flash_sales
    SET remaining_stock = remaining_stock - 1,
        updated_at = NOW()
    WHERE sale_id = p_sale_id;

    -- 4. 返回成功
    RETURN QUERY SELECT TRUE, '抢购成功'::TEXT, v_order_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION seckill_create_order_pessimistic IS '秒杀下单（悲观锁版本）';

-- ============================================
-- 3. 订单支付函数
-- ============================================

CREATE OR REPLACE FUNCTION pay_order(
    p_order_id BIGINT,
    p_user_id BIGINT,
    p_payment_method VARCHAR,
    p_transaction_id VARCHAR
) RETURNS TABLE (
    success BOOLEAN,
    message TEXT
) AS $$
DECLARE
    v_status VARCHAR;
    v_created_at TIMESTAMPTZ;
BEGIN
    -- 1. 检查订单状态
    SELECT status, created_at INTO v_status, v_created_at
    FROM flash_orders
    WHERE order_id = p_order_id AND user_id = p_user_id
    FOR UPDATE;

    IF v_status IS NULL THEN
        RETURN QUERY SELECT FALSE, '订单不存在'::TEXT;
        RETURN;
    END IF;

    IF v_status <> 'pending' THEN
        RETURN QUERY SELECT FALSE, format('订单状态异常: %s', v_status);
        RETURN;
    END IF;

    -- 检查是否超时（30分钟）
    IF NOW() - v_created_at > INTERVAL '30 minutes' THEN
        RETURN QUERY SELECT FALSE, '订单已超时'::TEXT;
        RETURN;
    END IF;

    -- 2. 更新订单状态
    UPDATE flash_orders
    SET status = 'paid',
        payment_method = p_payment_method,
        transaction_id = p_transaction_id,
        paid_at = NOW()
    WHERE order_id = p_order_id;

    -- 3. 返回成功
    RETURN QUERY SELECT TRUE, '支付成功'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4. 订单取消函数（释放库存）
-- ============================================

CREATE OR REPLACE FUNCTION cancel_order(
    p_order_id BIGINT,
    p_user_id BIGINT
) RETURNS TABLE (
    success BOOLEAN,
    message TEXT
) AS $$
DECLARE
    v_sale_id BIGINT;
    v_status VARCHAR;
BEGIN
    -- 1. 检查订单
    SELECT sale_id, status INTO v_sale_id, v_status
    FROM flash_orders
    WHERE order_id = p_order_id AND user_id = p_user_id
    FOR UPDATE;

    IF v_status IS NULL THEN
        RETURN QUERY SELECT FALSE, '订单不存在'::TEXT;
        RETURN;
    END IF;

    IF v_status = 'paid' THEN
        RETURN QUERY SELECT FALSE, '已支付订单不能取消'::TEXT;
        RETURN;
    END IF;

    IF v_status = 'cancelled' THEN
        RETURN QUERY SELECT FALSE, '订单已取消'::TEXT;
        RETURN;
    END IF;

    -- 2. 取消订单
    UPDATE flash_orders
    SET status = 'cancelled',
        cancelled_at = NOW()
    WHERE order_id = p_order_id;

    -- 3. 回滚库存
    UPDATE flash_sales
    SET remaining_stock = remaining_stock + 1,
        version = version + 1
    WHERE sale_id = v_sale_id;

    -- 4. 返回成功
    RETURN QUERY SELECT TRUE, '订单已取消，库存已回滚'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 5. 超时订单处理函数
-- ============================================

CREATE OR REPLACE FUNCTION process_timeout_orders()
RETURNS TABLE (
    order_id BIGINT,
    sale_id BIGINT,
    user_id BIGINT
) AS $$
BEGIN
    -- 查找超时未支付订单（30分钟）
    RETURN QUERY
    WITH timeout_orders AS (
        UPDATE flash_orders
        SET status = 'cancelled',
            cancelled_at = NOW()
        WHERE status = 'pending'
          AND created_at < NOW() - INTERVAL '30 minutes'
        RETURNING order_id, sale_id, user_id
    )
    -- 回滚库存
    , stock_rollback AS (
        UPDATE flash_sales fs
        SET remaining_stock = remaining_stock + rollback.cnt,
            version = version + 1
        FROM (
            SELECT sale_id, COUNT(*) as cnt
            FROM timeout_orders
            GROUP BY sale_id
        ) rollback
        WHERE fs.sale_id = rollback.sale_id
    )
    SELECT * FROM timeout_orders;
END;
$$ LANGUAGE plpgsql;

-- 定时任务：每分钟处理超时订单
SELECT cron.schedule('process-timeout', '* * * * *',
    'SELECT process_timeout_orders()');

-- ============================================
-- 6. 活动状态更新函数
-- ============================================

CREATE OR REPLACE FUNCTION update_flash_sale_status()
RETURNS void AS $$
BEGIN
    -- 1. 激活到期的活动
    UPDATE flash_sales
    SET status = 'active'
    WHERE status = 'pending'
      AND start_time <= NOW()
      AND end_time > NOW();

    -- 2. 结束过期的活动
    UPDATE flash_sales
    SET status = 'finished'
    WHERE status = 'active'
      AND end_time <= NOW();

    -- 3. 结束库存为0的活动
    UPDATE flash_sales
    SET status = 'finished'
    WHERE status = 'active'
      AND remaining_stock = 0;
END;
$$ LANGUAGE plpgsql;

-- 定时任务：每10秒检查
SELECT cron.schedule('update-sale-status', '*/10 * * * * *',
    'SELECT update_flash_sale_status()');

-- ============================================
-- 7. 数据一致性检查函数
-- ============================================

CREATE OR REPLACE FUNCTION check_data_consistency()
RETURNS TABLE (
    sale_id BIGINT,
    total_stock INT,
    remaining_stock INT,
    db_sold INT,
    order_count BIGINT,
    diff INT,
    has_issue BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        fs.sale_id,
        fs.total_stock,
        fs.remaining_stock,
        fs.total_stock - fs.remaining_stock as db_sold,
        COUNT(fo.order_id) as order_count,
        (fs.total_stock - fs.remaining_stock - COUNT(fo.order_id))::INT as diff,
        (fs.total_stock - fs.remaining_stock - COUNT(fo.order_id)) <> 0 as has_issue
    FROM flash_sales fs
    LEFT JOIN flash_orders fo ON fs.sale_id = fo.sale_id
    WHERE fs.status IN ('active', 'finished')
    GROUP BY fs.sale_id, fs.total_stock, fs.remaining_stock
    HAVING (fs.total_stock - fs.remaining_stock - COUNT(fo.order_id)) <> 0;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION check_data_consistency IS '检查库存与订单数据一致性';

-- ============================================
-- 8. 性能监控函数
-- ============================================

CREATE OR REPLACE FUNCTION get_seckill_stats(
    p_sale_id BIGINT DEFAULT NULL
) RETURNS TABLE (
    sale_id BIGINT,
    product_name TEXT,
    total_stock INT,
    remaining_stock INT,
    sold_count BIGINT,
    sold_percentage NUMERIC,
    total_orders BIGINT,
    paid_orders BIGINT,
    pending_orders BIGINT,
    cancelled_orders BIGINT,
    total_sales_amount NUMERIC,
    avg_order_amount NUMERIC,
    status TEXT,
    elapsed_seconds NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.sale_id,
        p.name as product_name,
        s.total_stock,
        s.remaining_stock,
        (s.total_stock - s.remaining_stock)::BIGINT as sold_count,
        ROUND((s.total_stock - s.remaining_stock)::NUMERIC * 100.0 / s.total_stock, 2) as sold_percentage,
        COUNT(o.order_id) as total_orders,
        COUNT(o.order_id) FILTER (WHERE o.status = 'paid') as paid_orders,
        COUNT(o.order_id) FILTER (WHERE o.status = 'pending') as pending_orders,
        COUNT(o.order_id) FILTER (WHERE o.status = 'cancelled') as cancelled_orders,
        COALESCE(SUM(o.total_amount) FILTER (WHERE o.status = 'paid'), 0) as total_sales_amount,
        COALESCE(AVG(o.total_amount) FILTER (WHERE o.status = 'paid'), 0) as avg_order_amount,
        s.status,
        EXTRACT(EPOCH FROM (NOW() - s.start_time)) as elapsed_seconds
    FROM flash_sales s
    JOIN products p ON s.product_id = p.product_id
    LEFT JOIN flash_orders o ON s.sale_id = o.sale_id
    WHERE (p_sale_id IS NULL OR s.sale_id = p_sale_id)
      AND s.status IN ('active', 'finished')
    GROUP BY s.sale_id, p.name, s.total_stock, s.remaining_stock, s.status, s.start_time;
END;
$$ LANGUAGE plpgsql;

-- 使用示例
SELECT * FROM get_seckill_stats();  -- 所有活动统计
SELECT * FROM get_seckill_stats(1); -- 特定活动统计

-- ============================================
-- 9. 性能诊断函数
-- ============================================

CREATE OR REPLACE FUNCTION diagnose_performance()
RETURNS TABLE (
    metric_name TEXT,
    current_value TEXT,
    threshold TEXT,
    status TEXT,
    recommendation TEXT
) AS $$
DECLARE
    v_connections INT;
    v_waiting INT;
    v_cache_hit_ratio NUMERIC;
    v_bloat_ratio NUMERIC;
BEGIN
    -- 1. 连接数检查
    SELECT COUNT(*) INTO v_connections FROM pg_stat_activity;

    RETURN QUERY SELECT
        '数据库连接数'::TEXT,
        v_connections::TEXT,
        '2000'::TEXT,
        CASE
            WHEN v_connections > 1900 THEN '❌ 严重'
            WHEN v_connections > 1700 THEN '⚠️ 警告'
            ELSE '✅ 正常'
        END,
        CASE
            WHEN v_connections > 1900 THEN '立即扩容或限流'
            WHEN v_connections > 1700 THEN '准备扩容'
            ELSE '无需操作'
        END;

    -- 2. 锁等待检查
    SELECT COUNT(*) INTO v_waiting
    FROM pg_stat_activity
    WHERE wait_event_type IS NOT NULL;

    RETURN QUERY SELECT
        '锁等待事务数'::TEXT,
        v_waiting::TEXT,
        '50'::TEXT,
        CASE
            WHEN v_waiting > 100 THEN '❌ 严重'
            WHEN v_waiting > 50 THEN '⚠️ 警告'
            ELSE '✅ 正常'
        END,
        CASE
            WHEN v_waiting > 100 THEN '检查长事务和死锁'
            WHEN v_waiting > 50 THEN '监控锁竞争'
            ELSE '无需操作'
        END;

    -- 3. 缓存命中率检查
    SELECT ROUND(
        sum(heap_blks_hit) * 100.0 /
        NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0), 2
    ) INTO v_cache_hit_ratio
    FROM pg_statio_user_tables;

    RETURN QUERY SELECT
        '缓存命中率'::TEXT,
        v_cache_hit_ratio::TEXT || '%',
        '99%'::TEXT,
        CASE
            WHEN v_cache_hit_ratio < 95 THEN '❌ 严重'
            WHEN v_cache_hit_ratio < 99 THEN '⚠️ 警告'
            ELSE '✅ 正常'
        END,
        CASE
            WHEN v_cache_hit_ratio < 95 THEN '增加shared_buffers'
            WHEN v_cache_hit_ratio < 99 THEN '检查慢查询'
            ELSE '无需操作'
        END;

    -- 4. 表膨胀检查
    SELECT MAX(
        ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2)
    ) INTO v_bloat_ratio
    FROM pg_stat_user_tables
    WHERE schemaname = 'seckill';

    RETURN QUERY SELECT
        '最大表膨胀率'::TEXT,
        v_bloat_ratio::TEXT || '%',
        '10%'::TEXT,
        CASE
            WHEN v_bloat_ratio > 20 THEN '❌ 严重'
            WHEN v_bloat_ratio > 10 THEN '⚠️ 警告'
            ELSE '✅ 正常'
        END,
        CASE
            WHEN v_bloat_ratio > 20 THEN '立即执行VACUUM'
            WHEN v_bloat_ratio > 10 THEN '计划VACUUM'
            ELSE '无需操作'
        END;

    -- ⭐ PostgreSQL 18：异步I/O统计
    RETURN QUERY SELECT
        '异步I/O平均延迟'::TEXT,
        (SELECT avg_latency::TEXT FROM pg_stat_aio),
        '0.5ms'::TEXT,
        CASE
            WHEN (SELECT avg_latency FROM pg_stat_aio) > 1.0 THEN '⚠️ 警告'
            ELSE '✅ 正常'
        END,
        CASE
            WHEN (SELECT avg_latency FROM pg_stat_aio) > 1.0 THEN '检查磁盘I/O'
            ELSE '无需操作'
        END;
END;
$$ LANGUAGE plpgsql;

-- 使用
SELECT * FROM diagnose_performance();

-- ============================================
-- 10. 批量操作函数
-- ============================================

-- 批量创建测试数据
CREATE OR REPLACE FUNCTION generate_test_data(
    p_product_count INT DEFAULT 1000,
    p_sale_count INT DEFAULT 100,
    p_user_count INT DEFAULT 10000
) RETURNS void AS $$
BEGIN
    -- 1. 创建商品
    INSERT INTO products (name, normal_price, stock, category_id, attributes, status)
    SELECT
        'Product ' || i,
        (random() * 1000 + 100)::NUMERIC(10,2),
        (random() * 10000 + 100)::INT,
        (random() * 10 + 1)::INT,
        jsonb_build_object(
            'brand', 'Brand ' || (random() * 100)::INT,
            'color', ARRAY['red', 'blue', 'green'][(random() * 2 + 1)::INT],
            'size', ARRAY['S', 'M', 'L', 'XL'][(random() * 3 + 1)::INT]
        ),
        'active'
    FROM generate_series(1, p_product_count) i
    ON CONFLICT DO NOTHING;

    -- 2. 创建用户
    INSERT INTO users (username, email, phone, password_hash, status)
    SELECT
        'user' || i,
        'user' || i || '@example.com',
        '138' || LPAD(i::TEXT, 8, '0'),
        'hashed_password_' || i,
        'active'
    FROM generate_series(1, p_user_count) i
    ON CONFLICT DO NOTHING;

    -- 3. 创建秒杀活动
    INSERT INTO flash_sales (
        product_id,
        flash_price,
        total_stock,
        remaining_stock,
        start_time,
        end_time,
        status
    )
    SELECT
        (random() * p_product_count + 1)::BIGINT,
        (random() * 500 + 50)::NUMERIC(10,2),
        (random() * 1000 + 100)::INT,
        (random() * 1000 + 100)::INT,
        NOW() + (random() * 7 || ' days')::INTERVAL,
        NOW() + (random() * 7 + 1 || ' days')::INTERVAL,
        'pending'
    FROM generate_series(1, p_sale_count) i;

    RAISE NOTICE '测试数据生成完成：商品%，用户%，活动%', p_product_count, p_user_count, p_sale_count;
END;
$$ LANGUAGE plpgsql;

-- 使用：生成测试数据
-- SELECT generate_test_data(10000, 1000, 100000);

-- ============================================
-- 完成
-- ============================================

SELECT '核心业务函数创建完成！' as message;

-- 查看函数列表
SELECT
    proname as function_name,
    pg_get_functiondef(oid) as definition
FROM pg_proc
WHERE pronamespace = 'seckill'::regnamespace
ORDER BY proname;
