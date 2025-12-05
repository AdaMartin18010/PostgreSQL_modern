# PostgreSQL实用SQL模式集锦

## 1. 去重模式

### 1.1 保留最新记录

```sql
-- 方法1: DELETE + ROW_NUMBER
DELETE FROM user_events
WHERE ctid NOT IN (
    SELECT ctid FROM (
        SELECT ctid,
               ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
        FROM user_events
    ) sub
    WHERE rn = 1
);

-- 方法2: DISTINCT ON + INSERT
CREATE TABLE user_events_dedup AS
SELECT DISTINCT ON (user_id)
    *
FROM user_events
ORDER BY user_id, created_at DESC;

-- 方法3: 窗口函数 + CTE
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM user_events
)
DELETE FROM user_events
WHERE (user_id, created_at) IN (
    SELECT user_id, created_at FROM ranked WHERE rn > 1
);
```

---

## 2. 累计计算

### 2.1 累计和

```sql
-- 账户余额计算
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
```

### 2.2 累计统计

```sql
-- 用户留存分析
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
```

---

## 3. 时间间隙分析

### 3.1 查找时间间隙

```sql
-- 查找订单号间隙
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

-- 生成缺失ID列表
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
```

---

## 4. 排行榜模式

### 4.1 实时排行榜

```sql
-- 游戏排行榜
CREATE TABLE player_scores (
    player_id BIGINT,
    game_id INT,
    score BIGINT,
    achieved_at TIMESTAMPTZ,
    PRIMARY KEY (player_id, game_id)
);

-- Top 100排行榜（带并列处理）
SELECT
    player_id,
    score,
    DENSE_RANK() OVER (ORDER BY score DESC) AS rank,
    NTILE(100) OVER (ORDER BY score DESC) AS percentile
FROM player_scores
WHERE game_id = 1
ORDER BY score DESC
LIMIT 100;

-- 玩家排名查询
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

-- 优化: 使用窗口函数
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
```

---

## 5. 批量操作模式

### 5.1 安全的批量删除

```sql
-- 避免长事务和锁
DO $$
DECLARE
    deleted INT;
BEGIN
    LOOP
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
-- 销售同比环比
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
```

### 6.2 趋势检测

```sql
-- 移动平均+趋势
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
```

---

## 7. 数据清洗模式

### 7.1 标准化处理

```sql
-- 清洗用户数据
UPDATE users
SET
    email = LOWER(TRIM(email)),
    phone = regexp_replace(phone, '[^0-9]', '', 'g'),
    name = INITCAP(TRIM(name))
WHERE
    email != LOWER(TRIM(email))
    OR phone != regexp_replace(phone, '[^0-9]', '', 'g')
    OR name != INITCAP(TRIM(name));
```

### 7.2 异常值处理

```sql
-- 识别并处理异常值（3σ原则）
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
```

---

## 8. 分页优化

### 8.1 Keyset分页

```sql
-- 传统OFFSET分页（慢）
SELECT * FROM products
ORDER BY product_id
LIMIT 20 OFFSET 10000;  -- 扫描10020行

-- Keyset分页（快）
SELECT * FROM products
WHERE product_id > 10000  -- 上一页最后的ID
ORDER BY product_id
LIMIT 20;  -- 只扫描20行

-- 时间戳分页
SELECT * FROM events
WHERE (created_at, event_id) < ('2024-01-01 12:00:00', 12345)  -- 上一页最后记录
ORDER BY created_at DESC, event_id DESC
LIMIT 20;

-- 索引
CREATE INDEX idx_events_created_id ON events (created_at DESC, event_id DESC);
```

---

## 9. 审计模式

### 9.1 审计表设计

```sql
CREATE TABLE audit_log (
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

-- 通用审计触发器
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
END;
$$ LANGUAGE plpgsql;

-- 应用到表
CREATE TRIGGER trg_audit_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION generic_audit_trigger();
```

---

## 10. 缓存表模式

### 10.1 自动刷新缓存

```sql
-- 汇总缓存表
CREATE TABLE user_stats_cache (
    user_id BIGINT PRIMARY KEY,
    order_count INT,
    total_spent NUMERIC,
    last_order_at TIMESTAMPTZ,
    cache_updated_at TIMESTAMPTZ DEFAULT now()
);

-- 增量更新函数
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
END;
$$ LANGUAGE plpgsql;

-- 触发器自动更新
CREATE OR REPLACE FUNCTION trigger_refresh_user_stats()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM refresh_user_stats_incremental(COALESCE(NEW.user_id, OLD.user_id));
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_refresh_stats
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION trigger_refresh_user_stats();
```

---

## 11. 数据版本控制

### 11.1 Temporal表

```sql
-- 当前版本表
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name VARCHAR(200),
    price NUMERIC(10,2),
    version INT DEFAULT 1,
    valid_from TIMESTAMPTZ DEFAULT now(),
    valid_to TIMESTAMPTZ DEFAULT 'infinity'
);

-- 历史版本表
CREATE TABLE products_history (
    history_id BIGSERIAL PRIMARY KEY,
    product_id INT,
    name VARCHAR(200),
    price NUMERIC(10,2),
    version INT,
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ
);

-- 自动记录历史
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
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_product_history
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION save_product_history();

-- 查询历史价格
SELECT * FROM products_history
WHERE product_id = 123
ORDER BY valid_from DESC;

-- 查询某个时间点的价格
SELECT * FROM products_history
WHERE product_id = 123
  AND '2023-06-01'::TIMESTAMPTZ BETWEEN valid_from AND valid_to;
```

---

## 12. 队列处理模式

### 12.1 任务队列

```sql
-- 任务表
CREATE TABLE task_queue (
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

CREATE INDEX idx_queue_pending ON task_queue (status, priority DESC, created_at)
WHERE status = 'pending';

-- Worker获取任务
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
END;
$$ LANGUAGE plpgsql;

-- 标记完成
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
END;
$$ LANGUAGE plpgsql;
```

---

## 13. 全文搜索模式

### 13.1 加权搜索

```sql
-- 多字段加权搜索
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
```

---

## 14. 性能模式

### 14.1 预计算汇总

```sql
-- 预计算每日汇总（物化视图）
CREATE MATERIALIZED VIEW daily_stats AS
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    COUNT(DISTINCT user_id) AS unique_users
FROM orders
GROUP BY DATE(created_at);

CREATE UNIQUE INDEX ON daily_stats (date);

-- 增量刷新（只更新最近数据）
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
END;
$$ LANGUAGE plpgsql;
```

---

**完成**: PostgreSQL实用SQL模式集锦
**字数**: ~10,000字
**涵盖**: 去重、累计、排行榜、批量操作、时序分析、队列、审计、缓存
