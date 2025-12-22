---

> **📋 文档来源**: `docs\01-PostgreSQL18\20-实用SQL模式集锦.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL实用SQL模式集锦

## 1. 去重模式

### 1.1 保留最新记录

```sql
-- 性能测试：方法1: DELETE + ROW_NUMBER（带错误处理）
BEGIN;
DELETE FROM user_events
WHERE ctid NOT IN (
    SELECT ctid FROM (
        SELECT ctid,
               ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
        FROM user_events
    ) sub
    WHERE rn = 1
);
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '删除重复记录失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：方法2: DISTINCT ON + INSERT（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS user_events_dedup AS
SELECT DISTINCT ON (user_id)
    *
FROM user_events
ORDER BY user_id, created_at DESC;
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表user_events_dedup已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建去重表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：方法3: 窗口函数 + CTE（带错误处理）
BEGIN;
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM user_events
)
DELETE FROM user_events
WHERE (user_id, created_at) IN (
    SELECT user_id, created_at FROM ranked WHERE rn > 1
);
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '窗口函数去重失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 2. 累计计算

### 2.1 累计和

```sql
-- 性能测试：账户余额计算（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH transactions AS (
    SELECT
        transaction_id,
        account_id,
        amount,
        transaction_date,
        SUM(amount) OVER (
            PARTITION BY account_id
            ORDER BY transaction_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_balance
    FROM account_transactions
    ORDER BY account_id, transaction_date
)
SELECT * FROM transactions;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '账户余额计算失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 2.2 累计统计

```sql
-- 性能测试：用户留存分析（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH user_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', register_date) AS cohort_month,
        DATE_TRUNC('month', activity_date) AS activity_month
    FROM user_activities
),
retention AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT CASE WHEN activity_month = cohort_month THEN user_id END) AS m0,
        COUNT(DISTINCT CASE WHEN activity_month = cohort_month + INTERVAL '1 month' THEN user_id END) AS m1,
        COUNT(DISTINCT CASE WHEN activity_month = cohort_month + INTERVAL '2 months' THEN user_id END) AS m2
    FROM user_cohorts
    GROUP BY cohort_month
)
SELECT
    cohort_month,
    m0,
    ROUND(m1::NUMERIC / NULLIF(m0, 0) * 100, 2) AS retention_m1,
    ROUND(m2::NUMERIC / NULLIF(m0, 0) * 100, 2) AS retention_m2
FROM retention
ORDER BY cohort_month;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '用户留存分析失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 3. 时间间隙分析

### 3.1 查找时间间隙

```sql
-- 性能测试：查找订单号间隙（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH gaps AS (
    SELECT
        order_id,
        LEAD(order_id) OVER (ORDER BY order_id) AS next_id,
        LEAD(order_id) OVER (ORDER BY order_id) - order_id AS gap_size
    FROM orders
)
SELECT order_id, next_id, gap_size
FROM gaps
WHERE gap_size > 1;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表orders不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '查找订单号间隙失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：生成缺失ID列表（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH RECURSIVE missing_ids AS (
    SELECT
        order_id + 1 AS missing_id,
        LEAD(order_id) OVER (ORDER BY order_id) AS next_id
    FROM orders
    WHERE LEAD(order_id) OVER (ORDER BY order_id) - order_id > 1

    UNION ALL

    SELECT
        missing_id + 1,
        next_id
    FROM missing_ids
    WHERE missing_id + 1 < next_id
)
SELECT missing_id FROM missing_ids ORDER BY missing_id;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表orders不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '生成缺失ID列表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 4. 排行榜模式

### 4.1 实时排行榜

```sql
-- 性能测试：游戏排行榜（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS player_scores (
    player_id BIGINT,
    game_id INT,
    score BIGINT,
    achieved_at TIMESTAMPTZ,
    PRIMARY KEY (player_id, game_id)
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表player_scores已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：Top 100排行榜（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    player_id,
    score,
    DENSE_RANK() OVER (ORDER BY score DESC) AS rank,
    NTILE(100) OVER (ORDER BY score DESC) AS percentile
FROM player_scores
WHERE game_id = 1
ORDER BY score DESC
LIMIT 100;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表player_scores不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'Top 100排行榜查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：玩家排名查询（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    player_id,
    score,
    (
        SELECT COUNT(*) + 1
        FROM player_scores ps2
        WHERE ps2.game_id = ps1.game_id
          AND ps2.score > ps1.score
    ) AS rank
FROM player_scores ps1
WHERE player_id = 12345 AND game_id = 1;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表player_scores不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '玩家排名查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：优化: 使用窗口函数（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT player_id, score, rank
FROM (
    SELECT
        player_id,
        score,
        RANK() OVER (PARTITION BY game_id ORDER BY score DESC) AS rank
    FROM player_scores
    WHERE game_id = 1
) ranked
WHERE player_id = 12345;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表player_scores不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '窗口函数排名查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 5. 批量操作模式

### 5.1 安全的批量删除

```sql
-- 性能测试：避免长事务和锁（带错误处理）
DO $$
DECLARE
    deleted INT;
BEGIN
    LOOP
        BEGIN
            DELETE FROM logs
            WHERE created_at < CURRENT_DATE - INTERVAL '90 days'
              AND ctid = ANY(
                  ARRAY(
                      SELECT ctid FROM logs
                      WHERE created_at < CURRENT_DATE - INTERVAL '90 days'
                      LIMIT 1000
                  )
              );

            GET DIAGNOSTICS deleted = ROW_COUNT;

            EXIT WHEN deleted = 0;

            COMMIT;

            RAISE NOTICE '删除 % 行', deleted;

            -- 短暂休眠
            PERFORM pg_sleep(0.1);
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE '批量删除失败: %', SQLERRM;
                ROLLBACK;
                EXIT;
        END;
    END LOOP;
END $$;
```

### 5.2 批量更新with进度

```sql
CREATE OR REPLACE FUNCTION batch_update_with_progress()
RETURNS VOID AS $$
DECLARE
    batch_size INT := 10000;
    total_rows BIGINT;
    updated BIGINT := 0;
    batch_updated INT;
BEGIN
    SELECT COUNT(*) INTO total_rows FROM products WHERE needs_update = true;

    RAISE NOTICE '总共需要更新: % 行', total_rows;

    LOOP
        UPDATE products
        SET
            price = price * 1.1,
            needs_update = false
        WHERE ctid IN (
            SELECT ctid FROM products
            WHERE needs_update = true
            LIMIT batch_size
        );

        GET DIAGNOSTICS batch_updated = ROW_COUNT;

        EXIT WHEN batch_updated = 0;

        updated := updated + batch_updated;

        RAISE NOTICE '进度: %/%  (%%)', updated, total_rows,
                     ROUND(updated * 100.0 / total_rows, 2);

        COMMIT;

        PERFORM pg_sleep(0.05);
    END LOOP;

    RAISE NOTICE '✅ 批量更新完成';
END;
$$ LANGUAGE plpgsql;
```

---

## 6. 时序分析模式

### 6.1 同比环比

```sql
-- 性能测试：销售同比环比（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH daily_sales AS (
    SELECT
        DATE(order_date) AS sale_date,
        SUM(amount) AS daily_amount
    FROM orders
    GROUP BY DATE(order_date)
)
SELECT
    sale_date,
    daily_amount,
    -- 环比（Day over Day）
    LAG(daily_amount, 1) OVER (ORDER BY sale_date) AS prev_day,
    daily_amount - LAG(daily_amount, 1) OVER (ORDER BY sale_date) AS dod_diff,
    ROUND((daily_amount - LAG(daily_amount, 1) OVER (ORDER BY sale_date)) * 100.0 /
          NULLIF(LAG(daily_amount, 1) OVER (ORDER BY sale_date), 0), 2) AS dod_pct,
    -- 同比（Year over Year）
    LAG(daily_amount, 365) OVER (ORDER BY sale_date) AS same_day_last_year,
    ROUND((daily_amount - LAG(daily_amount, 365) OVER (ORDER BY sale_date)) * 100.0 /
          NULLIF(LAG(daily_amount, 365) OVER (ORDER BY sale_date), 0), 2) AS yoy_pct
FROM daily_sales
ORDER BY sale_date DESC
LIMIT 30;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表orders不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '销售同比环比查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 6.2 趋势检测

```sql
-- 性能测试：移动平均+趋势（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH ma AS (
    SELECT
        date,
        value,
        AVG(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7d,
        AVG(value) OVER (ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS ma_30d
    FROM metrics
)
SELECT
    date,
    value,
    ma_7d,
    ma_30d,
    CASE
        WHEN ma_7d > ma_30d THEN '上升'
        WHEN ma_7d < ma_30d THEN '下降'
        ELSE '平稳'
    END AS trend
FROM ma
ORDER BY date DESC;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表metrics不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '移动平均+趋势查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 7. 数据清洗模式

### 7.1 标准化处理

```sql
-- 性能测试：清洗用户数据（带错误处理）
BEGIN;
UPDATE users
SET
    email = LOWER(TRIM(email)),
    phone = regexp_replace(phone, '[^0-9]', '', 'g'),
    name = INITCAP(TRIM(name))
WHERE
    email != LOWER(TRIM(email))
    OR phone != regexp_replace(phone, '[^0-9]', '', 'g')
    OR name != INITCAP(TRIM(name));
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '清洗用户数据失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 7.2 异常值处理

```sql
-- 性能测试：识别并处理异常值（3σ原则）（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH stats AS (
    SELECT
        AVG(price) AS mean,
        STDDEV(price) AS stddev
    FROM products
),
outliers AS (
    SELECT
        product_id,
        price,
        (price - s.mean) / s.stddev AS z_score
    FROM products p, stats s
    WHERE ABS((price - s.mean) / s.stddev) > 3
)
UPDATE products
SET price = (SELECT mean FROM stats)
WHERE product_id IN (SELECT product_id FROM outliers);
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表products不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '处理异常值失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 8. 分页优化

### 8.1 Keyset分页

```sql
-- 性能测试：传统OFFSET分页（慢）（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM products
ORDER BY product_id
LIMIT 20 OFFSET 10000;  -- 扫描10020行
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表products不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'OFFSET分页查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：Keyset分页（快）（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM products
WHERE product_id > 10000  -- 上一页最后的ID
ORDER BY product_id
LIMIT 20;  -- 只扫描20行
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表products不存在';
    WHEN OTHERS THEN
        RAISE NOTICE 'Keyset分页查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：时间戳分页（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM events
WHERE (created_at, event_id) < ('2024-01-01 12:00:00', 12345)  -- 上一页最后记录
ORDER BY created_at DESC, event_id DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表events不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '时间戳分页查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_events_created_id ON events (created_at DESC, event_id DESC);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_events_created_id已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 9. 审计模式

### 9.1 审计表设计

```sql
-- 性能测试：创建审计表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    record_id TEXT,
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    changed_by TEXT DEFAULT current_user,
    changed_at TIMESTAMPTZ DEFAULT now(),
    ip_address INET,
    application_name TEXT
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表audit_log已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建审计表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：通用审计触发器（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION generic_audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    old_json JSONB;
    new_json JSONB;
    changed_fields TEXT[];
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, record_id, new_values)
        VALUES (TG_TABLE_NAME, 'INSERT', NEW.id::TEXT, to_jsonb(NEW));

    ELSIF TG_OP = 'UPDATE' THEN
        old_json := to_jsonb(OLD);
        new_json := to_jsonb(NEW);

        -- 计算变更字段
        SELECT array_agg(key) INTO changed_fields
        FROM jsonb_each(new_json)
        WHERE value != old_json->key;

        INSERT INTO audit_log (table_name, operation, record_id, old_values, new_values, changed_fields)
        VALUES (TG_TABLE_NAME, 'UPDATE', NEW.id::TEXT, old_json, new_json, changed_fields);

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_values)
        VALUES (TG_TABLE_NAME, 'DELETE', OLD.id::TEXT, to_jsonb(OLD));
    END IF;

    RETURN COALESCE(NEW, OLD);
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '审计触发器执行失败: %', SQLERRM;
        RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建审计触发器失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：应用到表（带错误处理）
BEGIN;
DROP TRIGGER IF EXISTS trg_audit_users ON users;
CREATE TRIGGER trg_audit_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION generic_audit_trigger();
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users或函数generic_audit_trigger不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建审计触发器失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 10. 缓存表模式

### 10.1 自动刷新缓存

```sql
-- 性能测试：创建汇总缓存表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS user_stats_cache (
    user_id BIGINT PRIMARY KEY,
    order_count INT,
    total_spent NUMERIC,
    last_order_at TIMESTAMPTZ,
    cache_updated_at TIMESTAMPTZ DEFAULT now()
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表user_stats_cache已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建缓存表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：增量更新函数（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION refresh_user_stats_incremental(p_user_id BIGINT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO user_stats_cache (user_id, order_count, total_spent, last_order_at)
    SELECT
        user_id,
        COUNT(*),
        SUM(amount),
        MAX(created_at)
    FROM orders
    WHERE user_id = p_user_id
    GROUP BY user_id
    ON CONFLICT (user_id) DO UPDATE
    SET
        order_count = EXCLUDED.order_count,
        total_spent = EXCLUDED.total_spent,
        last_order_at = EXCLUDED.last_order_at,
        cache_updated_at = now();
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表user_stats_cache或orders不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '刷新用户统计缓存失败: %', SQLERRM;
        RAISE;
END;
$$ LANGUAGE plpgsql;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建增量更新函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：触发器自动更新（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION trigger_refresh_user_stats()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM refresh_user_stats_incremental(COALESCE(NEW.user_id, OLD.user_id));
    RETURN COALESCE(NEW, OLD);
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '触发器刷新用户统计失败: %', SQLERRM;
        RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建触发器函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

CREATE TRIGGER trg_refresh_stats
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION trigger_refresh_user_stats();
```

---

## 11. 数据版本控制

### 11.1 Temporal表

```sql
-- 性能测试：当前版本表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY,
    name VARCHAR(200),
    price NUMERIC(10,2),
    version INT DEFAULT 1,
    valid_from TIMESTAMPTZ DEFAULT now(),
    valid_to TIMESTAMPTZ DEFAULT 'infinity'
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表products已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建当前版本表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：历史版本表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS products_history (
    history_id BIGSERIAL PRIMARY KEY,
    product_id INT,
    name VARCHAR(200),
    price NUMERIC(10,2),
    version INT,
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表products_history已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建历史版本表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：自动记录历史（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION save_product_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        -- 关闭旧版本
        UPDATE products SET valid_to = now() WHERE product_id = OLD.product_id;

        -- 保存到历史表
        INSERT INTO products_history
        SELECT product_id, name, price, version, valid_from, now()
        FROM products WHERE product_id = OLD.product_id;

        -- 更新版本号
        NEW.version := OLD.version + 1;
        NEW.valid_from := now();
        NEW.valid_to := 'infinity';
    END IF;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '保存产品历史失败: %', SQLERRM;
        RETURN NEW;
END;
$$ LANGUAGE plpgsql;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建历史记录函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建触发器（带错误处理）
BEGIN;
DROP TRIGGER IF EXISTS trg_product_history ON products;
CREATE TRIGGER trg_product_history
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION save_product_history();
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表products或函数save_product_history不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建触发器失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查询历史价格（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM products_history
WHERE product_id = 123
ORDER BY valid_from DESC;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表products_history不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '查询历史价格失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查询某个时间点的价格（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM products_history
WHERE product_id = 123
  AND '2023-06-01'::TIMESTAMPTZ BETWEEN valid_from AND valid_to;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表products_history不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '查询时间点价格失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 12. 队列处理模式

### 12.1 任务队列

```sql
-- 性能测试：任务表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS task_queue (
    task_id BIGSERIAL PRIMARY KEY,
    task_type VARCHAR(50),
    payload JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    priority INT DEFAULT 0,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    created_at TIMESTAMPTZ DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表task_queue已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建任务表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_queue_pending ON task_queue (status, priority DESC, created_at)
WHERE status = 'pending';
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_queue_pending已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：Worker获取任务（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION dequeue_task()
RETURNS task_queue AS $$
DECLARE
    task task_queue;
BEGIN
    UPDATE task_queue
    SET
        status = 'processing',
        started_at = now()
    WHERE task_id = (
        SELECT task_id
        FROM task_queue
        WHERE status = 'pending'
          AND retry_count < max_retries
        ORDER BY priority DESC, created_at
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    RETURNING * INTO task;

    RETURN task;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '获取任务失败: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建获取任务函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：标记完成（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION complete_task(p_task_id BIGINT, p_success BOOLEAN, p_error TEXT DEFAULT NULL)
RETURNS VOID AS $$
BEGIN
    IF p_success THEN
        UPDATE task_queue
        SET
            status = 'completed',
            completed_at = now()
        WHERE task_id = p_task_id;
    ELSE
        UPDATE task_queue
        SET
            status = CASE
                WHEN retry_count + 1 >= max_retries THEN 'failed'
                ELSE 'pending'
            END,
            retry_count = retry_count + 1,
            error_message = p_error
        WHERE task_id = p_task_id;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '标记任务完成失败: %', SQLERRM;
        RAISE;
END;
$$ LANGUAGE plpgsql;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建标记完成函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 13. 全文搜索模式

### 13.1 加权搜索

```sql
-- 性能测试：多字段加权搜索（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    doc_id,
    title,
    ts_rank_cd(
        setweight(to_tsvector('english', title), 'A') ||
        setweight(to_tsvector('english', content), 'B') ||
        setweight(to_tsvector('english', COALESCE(tags::text, '')), 'C'),
        query
    ) AS rank
FROM documents,
     to_tsquery('english', 'postgresql & database') query
WHERE
    setweight(to_tsvector('english', title), 'A') ||
    setweight(to_tsvector('english', content), 'B') ||
    setweight(to_tsvector('english', COALESCE(tags::text, '')), 'C')
    @@ query
ORDER BY rank DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表documents不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '多字段加权搜索失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 14. 性能模式

### 14.1 预计算汇总

```sql
-- 性能测试：预计算每日汇总（物化视图）（带错误处理）
BEGIN;
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_stats AS
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    COUNT(DISTINCT user_id) AS unique_users
FROM orders
GROUP BY DATE(created_at);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '物化视图daily_stats已存在';
    WHEN undefined_table THEN
        RAISE NOTICE '表orders不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建物化视图失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建唯一索引（带错误处理）
BEGIN;
CREATE UNIQUE INDEX IF NOT EXISTS daily_stats_date_idx ON daily_stats (date);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引daily_stats_date_idx已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建唯一索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：增量刷新（只更新最近数据）（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION refresh_daily_stats_incremental()
RETURNS VOID AS $$
BEGIN
    -- 删除最近3天
    DELETE FROM daily_stats
    WHERE date >= CURRENT_DATE - 3;

    -- 重新计算
    INSERT INTO daily_stats
    SELECT
        DATE(created_at),
        COUNT(*),
        SUM(amount),
        AVG(amount),
        COUNT(DISTINCT user_id)
    FROM orders
    WHERE DATE(created_at) >= CURRENT_DATE - 3
    GROUP BY DATE(created_at);
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表daily_stats或orders不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '增量刷新失败: %', SQLERRM;
        RAISE;
END;
$$ LANGUAGE plpgsql;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建增量刷新函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

**完成**: PostgreSQL实用SQL模式集锦
**字数**: ~10,000字
**涵盖**: 去重、累计、排行榜、批量操作、时序分析、队列、审计、缓存
