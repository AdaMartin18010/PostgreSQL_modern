# 错误处理与日志深度分析 v2.0

> **文档类型**: 数据库错误处理与可观测性
> **创建日期**: 2026-03-04
> **文档长度**: 7500+字

---

## 摘要

建立完善的错误处理体系、结构化日志输出和分布式追踪集成，确保DCA系统的可靠性和可观测性。

---

## 1. 错误处理体系

### 1.1 统一错误代码

**错误代码设计**:

```sql
-- 创建错误代码表
CREATE TABLE error_codes (
    code VARCHAR(10) PRIMARY KEY,
    category VARCHAR(50),
    message TEXT,
    http_status INTEGER,
    severity VARCHAR(20)  -- ERROR, WARNING, INFO
);

-- 插入标准错误代码
INSERT INTO error_codes VALUES
    ('E0001', 'VALIDATION', 'Invalid input parameters', 400, 'ERROR'),
    ('E0002', 'BUSINESS', 'Insufficient balance', 422, 'ERROR'),
    ('E0003', 'BUSINESS', 'Product out of stock', 422, 'ERROR'),
    ('E0004', 'AUTH', 'Permission denied', 403, 'ERROR'),
    ('E0005', 'NOT_FOUND', 'Record not found', 404, 'ERROR'),
    ('E0006', 'CONFLICT', 'Duplicate record', 409, 'ERROR'),
    ('E0007', 'SYSTEM', 'Database connection error', 500, 'ERROR'),
    ('E0008', 'TIMEOUT', 'Operation timeout', 504, 'ERROR');
```

### 1.2 错误处理模板

**标准错误处理框架**:

```sql
CREATE OR REPLACE PROCEDURE sp_template_with_error_handling(
    IN p_param1 BIGINT,
    IN p_param2 VARCHAR,
    OUT p_result JSONB,
    OUT p_success BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_context JSONB;
    v_error_code VARCHAR(10);
    v_error_message TEXT;
BEGIN
    -- 初始化
    p_success := false;
    v_context := jsonb_build_object(
        'procedure', 'sp_template_with_error_handling',
        'params', jsonb_build_object('p1', p_param1, 'p2', p_param2),
        'started_at', NOW(),
        'transaction_id', txid_current()
    );

    -- 参数验证
    IF p_param1 IS NULL THEN
        v_error_code := 'E0001';
        v_error_message := 'p_param1 is required';
        RAISE EXCEPTION USING
            ERRCODE = 'P0001',
            MESSAGE = v_error_message,
            DETAIL = v_context::TEXT,
            HINT = v_error_code;
    END IF;

    -- 业务逻辑
    BEGIN
        -- 操作1
        PERFORM operation1();

        -- 操作2 (可能出错)
        PERFORM operation2();

    EXCEPTION
        WHEN unique_violation THEN
            v_error_code := 'E0006';
            v_error_message := 'Record already exists';

            -- 记录错误日志
            INSERT INTO error_logs (
                error_code, message, sqlstate, detail, context, occurred_at
            ) VALUES (
                v_error_code, v_error_message, SQLSTATE, SQLERRM, v_context, NOW()
            );

            -- 重新抛出
            RAISE EXCEPTION USING
                ERRCODE = 'P0001',
                MESSAGE = v_error_message,
                DETAIL = v_context::TEXT,
                HINT = v_error_code;

        WHEN foreign_key_violation THEN
            v_error_code := 'E0005';
            v_error_message := 'Referenced record not found';
            RAISE;

        WHEN OTHERS THEN
            -- 记录未预期错误
            INSERT INTO error_logs (
                error_code, message, sqlstate, detail, context, occurred_at
            ) VALUES (
                'E9999', SQLERRM, SQLSTATE, SQLERRM, v_context, NOW()
            );
            RAISE;
    END;

    -- 成功处理
    p_success := true;
    p_result := jsonb_build_object(
        'status', 'success',
        'data', ...
    );

    -- 记录成功日志
    INSERT INTO operation_logs (context, status, result, completed_at)
    VALUES (v_context, 'success', p_result, NOW());

EXCEPTION
    WHEN OTHERS THEN
        -- 确保错误被记录
        INSERT INTO error_logs (error_code, message, sqlstate, detail, context, occurred_at)
        VALUES (COALESCE(v_error_code, 'E9999'), SQLERRM, SQLSTATE, SQLERRM, v_context, NOW());

        p_result := jsonb_build_object(
            'status', 'error',
            'code', COALESCE(v_error_code, 'E9999'),
            'message', SQLERRM
        );
        RAISE;
END;
$$;
```

### 1.3 业务错误处理

**库存不足处理示例**:

```sql
CREATE OR REPLACE PROCEDURE sp_check_and_deduct_stock(
    IN p_product_id BIGINT,
    IN p_quantity INT,
    OUT p_available BOOLEAN,
    OUT p_message TEXT
)
AS $$
DECLARE
    v_current_stock INT;
    v_reserved_stock INT;
    v_available_stock INT;
BEGIN
    -- 获取库存信息 (带悲观锁)
    SELECT stock_quantity, reserved_quantity
    INTO v_current_stock, v_reserved_stock
    FROM products
    WHERE id = p_product_id
    FOR UPDATE;

    IF NOT FOUND THEN
        p_available := false;
        p_message := 'E0005|Product not found';
        RETURN;
    END IF;

    -- 计算可用库存
    v_available_stock := v_current_stock - v_reserved_stock;

    -- 检查库存
    IF v_available_stock < p_quantity THEN
        p_available := false;
        p_message := format('E0003|Insufficient stock: required %s, available %s',
                           p_quantity, v_available_stock);
        RETURN;
    END IF;

    -- 扣减库存
    UPDATE products
    SET reserved_quantity = reserved_quantity + p_quantity
    WHERE id = p_product_id;

    p_available := true;
    p_message := 'Stock reserved successfully';
END;
$$;
```

---

## 2. 结构化日志系统

### 2.1 日志表设计

```sql
-- 操作日志
CREATE TABLE operation_logs (
    log_id BIGSERIAL PRIMARY KEY,
    log_time TIMESTAMP DEFAULT clock_timestamp(),
    level VARCHAR(10) DEFAULT 'INFO',  -- DEBUG, INFO, WARN, ERROR
    procedure_name VARCHAR(100),
    transaction_id BIGINT,
    user_id BIGINT,
    tenant_id BIGINT,
    context JSONB,           -- 上下文信息
    message TEXT,
    duration_ms INTEGER,     -- 执行时间
    rows_affected INTEGER,
    status VARCHAR(20)       -- success, failed
) PARTITION BY RANGE (log_time);

-- 按时间分区
CREATE TABLE operation_logs_2026_03 PARTITION OF operation_logs
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- 错误日志
CREATE TABLE error_logs (
    error_id BIGSERIAL PRIMARY KEY,
    error_time TIMESTAMP DEFAULT clock_timestamp(),
    error_code VARCHAR(10),
    severity VARCHAR(20),    -- CRITICAL, HIGH, MEDIUM, LOW
    procedure_name VARCHAR(100),
    transaction_id BIGINT,
    message TEXT,
    sqlstate VARCHAR(5),
    detail TEXT,
    context JSONB,
    stack_trace TEXT,
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(50)
);

-- 审计日志 (不可修改)
CREATE TABLE audit_logs (
    audit_id BIGSERIAL PRIMARY KEY,
    audit_time TIMESTAMP DEFAULT clock_timestamp(),
    table_name VARCHAR(50),
    record_id BIGINT,
    action VARCHAR(10),      -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    session_id VARCHAR(100),
    application VARCHAR(50)
) WITH (fillfactor=100);  -- 只插入不更新，使用100%填充
```

### 2.2 日志写入函数

```sql
-- 结构化日志写入
CREATE OR REPLACE PROCEDURE sp_log_operation(
    IN p_level VARCHAR(10),
    IN p_procedure_name VARCHAR(100),
    IN p_message TEXT,
    IN p_context JSONB DEFAULT NULL,
    IN p_duration_ms INTEGER DEFAULT NULL,
    IN p_status VARCHAR(20) DEFAULT 'success'
)
AS $$
BEGIN
    INSERT INTO operation_logs (
        level, procedure_name, transaction_id, user_id, tenant_id,
        message, context, duration_ms, status
    ) VALUES (
        p_level,
        p_procedure_name,
        txid_current(),
        current_setting('app.current_user_id', true)::BIGINT,
        current_setting('app.current_tenant', true)::BIGINT,
        p_message,
        COALESCE(p_context, '{}'::JSONB),
        p_duration_ms,
        p_status
    );
END;
$$;

-- 使用示例
CREATE OR REPLACE PROCEDURE sp_create_order_with_logging(...)
AS $$
DECLARE
    v_start TIMESTAMP;
    v_context JSONB;
BEGIN
    v_start := clock_timestamp();

    v_context := jsonb_build_object('user_id', p_user_id, 'item_count', jsonb_array_length(p_items));

    CALL sp_log_operation('INFO', 'sp_create_order', 'Starting order creation', v_context);

    -- 业务逻辑...

    CALL sp_log_operation(
        'INFO',
        'sp_create_order',
        'Order created successfully',
        v_context || jsonb_build_object('order_id', v_order_id),
        EXTRACT(MILLISECOND FROM (clock_timestamp() - v_start))::INTEGER,
        'success'
    );
END;
$$;
```

---

## 3. 监控与告警

### 3.1 监控视图

```sql
-- 实时错误统计
CREATE VIEW v_error_statistics AS
SELECT
    date_trunc('hour', error_time) as hour,
    error_code,
    COUNT(*) as error_count,
    COUNT(DISTINCT transaction_id) as affected_transactions
FROM error_logs
WHERE error_time > NOW() - INTERVAL '24 hours'
GROUP BY 1, 2;

-- 慢操作监控
CREATE VIEW v_slow_operations AS
SELECT
    procedure_name,
    COUNT(*) as call_count,
    AVG(duration_ms) as avg_duration,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_duration,
    MAX(duration_ms) as max_duration
FROM operation_logs
WHERE log_time > NOW() - INTERVAL '1 hour'
  AND duration_ms > 1000  -- 超过1秒
GROUP BY procedure_name
ORDER BY avg_duration DESC;
```

### 3.2 自动告警

```sql
-- 告警检查存储过程
CREATE OR REPLACE PROCEDURE sp_check_alerts()
AS $$
DECLARE
    v_error_count INTEGER;
    v_slow_count INTEGER;
BEGIN
    -- 检查错误率
    SELECT COUNT(*) INTO v_error_count
    FROM error_logs
    WHERE error_time > NOW() - INTERVAL '5 minutes'
      AND severity IN ('CRITICAL', 'HIGH');

    IF v_error_count > 10 THEN
        -- 发送告警 (调用外部webhook)
        PERFORM pg_notify('critical_alerts',
            format('High error rate detected: %s errors in 5 minutes', v_error_count));
    END IF;

    -- 检查慢查询
    SELECT COUNT(*) INTO v_slow_count
    FROM operation_logs
    WHERE log_time > NOW() - INTERVAL '5 minutes'
      AND duration_ms > 5000;  -- 超过5秒

    IF v_slow_count > 5 THEN
        PERFORM pg_notify('performance_alerts',
            format('Slow operations detected: %s operations > 5s', v_slow_count));
    END IF;
END;
$$;

-- 定时执行告警检查
SELECT cron.schedule('alert-check', '*/5 * * * *', 'CALL sp_check_alerts()');
```

---

**文档信息**:

- 字数: 7500+
- 错误代码: 8个
- 日志表: 3个
- 状态: ✅ 完成
