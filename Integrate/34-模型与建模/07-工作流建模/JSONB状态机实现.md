# JSONB状态机实现

> **创建日期**: 2025年1月
> **来源**: PostgreSQL JSONB实践
> **状态**: ✅ 已完成
> **文档编号**: 07-03

---

## 📑 目录

- [JSONB状态机实现](#jsonb状态机实现)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [1.1 理论基础](#11-理论基础)
    - [1.1.1 JSONB状态机基本概念](#111-jsonb状态机基本概念)
    - [1.1.2 JSONB状态存储理论](#112-jsonb状态存储理论)
    - [1.1.3 JSONB索引理论](#113-jsonb索引理论)
    - [1.1.4 JSONB状态转换理论](#114-jsonb状态转换理论)
    - [1.1.5 JSONB vs 传统表对比](#115-jsonb-vs-传统表对比)
    - [1.1.6 复杂度分析](#116-复杂度分析)
  - [2. JSONB状态存储](#2-jsonb状态存储)
    - [2.1 状态数据结构设计](#21-状态数据结构设计)
    - [2.2 状态定义存储](#22-状态定义存储)
    - [2.3 索引优化](#23-索引优化)
  - [3. 状态转换函数](#3-状态转换函数)
    - [3.1 状态转换函数](#31-状态转换函数)
    - [3.2 基于状态机定义的状态转换](#32-基于状态机定义的状态转换)
  - [4. 状态查询优化](#4-状态查询优化)
    - [4.1 状态查询函数](#41-状态查询函数)
    - [4.2 状态统计查询](#42-状态统计查询)
  - [5. 最佳实践](#5-最佳实践)
    - [5.1 设计建议](#51-设计建议)
    - [5.2 性能优化](#52-性能优化)
    - [5.3 错误处理](#53-错误处理)
  - [6. 更多实际案例 / More Practical Examples](#6-更多实际案例--more-practical-examples)
    - [6.1 案例1: 订单状态机（JSONB实现）](#61-案例1-订单状态机jsonb实现)
    - [6.2 案例2: 用户认证状态机](#62-案例2-用户认证状态机)
    - [6.3 案例3: 库存管理状态机](#63-案例3-库存管理状态机)
  - [7. 性能优化与监控 / Performance Optimization and Monitoring](#7-性能优化与监控--performance-optimization-and-monitoring)
    - [7.1 JSONB索引优化](#71-jsonb索引优化)
    - [7.2 查询性能优化](#72-查询性能优化)
    - [7.3 状态机监控](#73-状态机监控)
  - [8. 常见问题解答 / FAQ](#8-常见问题解答--faq)
    - [Q1: JSONB状态机和传统状态表哪个更好？](#q1-jsonb状态机和传统状态表哪个更好)
    - [Q2: JSONB状态机如何保证数据一致性？](#q2-jsonb状态机如何保证数据一致性)
    - [Q3: JSONB状态历史会很大，如何优化？](#q3-jsonb状态历史会很大如何优化)
    - [Q4: JSONB状态机查询性能如何优化？](#q4-jsonb状态机查询性能如何优化)
    - [Q5: 如何实现JSONB状态机的回滚？](#q5-如何实现jsonb状态机的回滚)
  - [8. 相关资源 / Related Resources](#8-相关资源--related-resources)
    - [8.1 核心相关文档 / Core Related Documents](#81-核心相关文档--core-related-documents)
    - [8.2 理论基础 / Theoretical Foundation](#82-理论基础--theoretical-foundation)
    - [8.3 实践指南 / Practical Guides](#83-实践指南--practical-guides)
    - [8.4 应用案例 / Application Cases](#84-应用案例--application-cases)
    - [8.5 参考资源 / Reference Resources](#85-参考资源--reference-resources)

---

## 1. 概述

使用PostgreSQL的JSONB类型实现灵活的状态机，适合复杂的状态管理场景。
JSONB提供了灵活的文档存储能力，可以存储状态机的完整定义和状态数据。

**核心优势**:

- **灵活性**：支持动态状态定义
- **性能**：JSONB索引支持高效查询
- **简洁性**：单一字段存储完整状态信息
- **扩展性**：易于添加新的状态属性

---

## 1.1 理论基础

### 1.1.1 JSONB状态机基本概念

**JSONB状态机**使用JSONB类型存储状态机定义和状态数据：

- **状态定义**: 存储在JSONB中的状态机定义
- **状态数据**: 存储在JSONB中的当前状态和历史
- **动态性**: 支持动态添加状态和转换

**JSONB优势**:

- **灵活性**: 支持动态结构
- **性能**: GIN索引支持高效查询
- **简洁性**: 单一字段存储完整信息

### 1.1.2 JSONB状态存储理论

**状态JSONB结构**:

- **当前状态**: `state.current`
- **状态历史**: `state.history[]`
- **元数据**: `state.metadata{}`

**JSONB查询**:

- **路径查询**: `state->'current'`
- **数组查询**: `state->'history'->0`
- **包含查询**: `state @> '{"current": "active"}'`

### 1.1.3 JSONB索引理论

**GIN索引**:

- **索引类型**: Generalized Inverted Index
- **适用场景**: JSONB字段查询
- **索引大小**: $O(N \times K)$ where N is rows, K is average keys

**索引优化**:

- **路径索引**: 为常用路径创建索引
- **表达式索引**: 为常用表达式创建索引
- **部分索引**: 为部分数据创建索引

### 1.1.4 JSONB状态转换理论

**状态转换函数**:

- **验证**: 验证转换是否合法
- **执行**: 执行状态转换
- **记录**: 记录状态历史

**原子性**:

- **事务**: 状态转换在事务中执行
- **锁**: 使用行锁保证并发安全
- **一致性**: 保证状态一致性

### 1.1.5 JSONB vs 传统表对比

**存储方式对比**:

| 特性 | JSONB | 传统表 |
|------|-------|--------|
| **灵活性** | 高 | 低 |
| **查询性能** | 中 | 高 |
| **索引支持** | GIN索引 | B-Tree索引 |
| **扩展性** | 高 | 低 |

### 1.1.6 复杂度分析

**存储复杂度**:

- **JSONB存储**: $O(N \times S)$ where N is entities, S is average state size
- **索引存储**: $O(N \times K)$ where K is average keys

**查询复杂度**:

- **路径查询**: $O(\log N)$ with GIN index
- **包含查询**: $O(\log N)$ with GIN index
- **数组查询**: $O(N)$ (worst case)

---

## 2. JSONB状态存储

### 2.1 状态数据结构设计

**状态JSONB结构**:

```sql
-- 使用JSONB存储状态的表（带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS workflow_entity (
        entity_id BIGSERIAL PRIMARY KEY,
        entity_type VARCHAR(100) NOT NULL,
        -- JSONB状态存储
        state JSONB NOT NULL DEFAULT '{
            "current": "initial",
            "history": [],
            "metadata": {}
        }'::JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    RAISE NOTICE '表 workflow_entity 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表 workflow_entity 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 workflow_entity 失败: %', SQLERRM;
END $$;

-- 状态JSONB结构说明
-- {
--   "current": "状态名称",
--   "history": [
--     {"state": "状态名", "timestamp": "时间", "event": "事件名"}
--   ],
--   "metadata": {
--     "key": "value"
--   }
-- }
```

### 2.2 状态定义存储

**状态机定义表（JSONB）**:

```sql
-- 状态机定义表（使用JSONB存储完整定义，带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS state_machine_definition (
        machine_id SERIAL PRIMARY KEY,
        machine_name VARCHAR(100) UNIQUE NOT NULL,
        -- JSONB存储完整状态机定义
        definition JSONB NOT NULL,
        version INT DEFAULT 1,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    RAISE NOTICE '表 state_machine_definition 创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表 state_machine_definition 已存在，跳过创建';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 state_machine_definition 失败: %', SQLERRM;
END $$;

-- 状态机定义JSONB结构示例（带错误处理）
DO $$
BEGIN
    INSERT INTO state_machine_definition (machine_name, definition) VALUES (
        'order_workflow',
        '{
            "states": {
                "pending": {
                    "type": "initial",
                    "transitions": {
                        "start": "processing",
                        "cancel": "cancelled"
                    }
                },
                "processing": {
                    "type": "normal",
                    "transitions": {
                        "complete": "completed",
                        "cancel": "cancelled",
                        "error": "error"
                    }
                },
                "completed": {"type": "final"},
                "cancelled": {"type": "final"},
                "error": {"type": "error"}
            },
            "initial_state": "pending"
        }'::JSONB
    ) ON CONFLICT DO NOTHING;
    RAISE NOTICE '状态机定义数据插入成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '插入状态机定义数据失败: %', SQLERRM;
END $$;
```

### 2.3 索引优化

**JSONB索引创建**:

```sql
-- GIN索引：支持JSONB查询（带错误处理）
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_workflow_state_current ON workflow_entity USING GIN((state->'current'));
    CREATE INDEX IF NOT EXISTS idx_workflow_state_metadata ON workflow_entity USING GIN((state->'metadata'));

    -- 表达式索引：状态查询优化
    CREATE INDEX IF NOT EXISTS idx_workflow_current_state ON workflow_entity((state->>'current'))
        WHERE (state->>'current') IS NOT NULL;

    -- 部分索引：特定状态查询
    CREATE INDEX IF NOT EXISTS idx_workflow_pending ON workflow_entity(entity_id)
        WHERE (state->>'current') = 'pending';

    RAISE NOTICE '索引创建成功';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建索引失败: %', SQLERRM;
END $$;
```

---

## 3. 状态转换函数

### 3.1 状态转换函数

**JSONB状态转换**:

```sql
-- JSONB状态转换函数
CREATE OR REPLACE FUNCTION transition_state_jsonb(
    p_entity_id BIGINT,
    p_event_name VARCHAR,
    p_new_state VARCHAR,
    p_metadata JSONB DEFAULT NULL
)
RETURNS JSONB AS $$
DECLARE
    v_current_state JSONB;
    v_new_state_jsonb JSONB;
BEGIN
    -- 获取当前状态
    SELECT state INTO v_current_state
    FROM workflow_entity
    WHERE entity_id = p_entity_id;

    IF v_current_state IS NULL THEN
        RAISE EXCEPTION 'Entity % not found', p_entity_id;
    END IF;

    -- 验证状态转换
    IF v_current_state->>'current' != p_new_state THEN
        -- 构建新状态
        v_new_state_jsonb := jsonb_set(
            jsonb_set(
                v_current_state,
                '{current}',
                to_jsonb(p_new_state)
            ),
            '{history}',
            (
                v_current_state->'history' ||
                jsonb_build_array(
                    jsonb_build_object(
                        'state', p_new_state,
                        'timestamp', NOW(),
                        'event', p_event_name,
                        'previous', v_current_state->>'current'
                    )
                )
            )
        );

        -- 更新元数据
        IF p_metadata IS NOT NULL THEN
            v_new_state_jsonb := jsonb_set(
                v_new_state_jsonb,
                '{metadata}',
                COALESCE(v_new_state_jsonb->'metadata', '{}'::JSONB) || p_metadata
            );
        END IF;

        -- 更新状态
        UPDATE workflow_entity
        SET state = v_new_state_jsonb,
            updated_at = NOW()
        WHERE entity_id = p_entity_id;

        RETURN v_new_state_jsonb;
    END IF;

    RETURN v_current_state;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 基于状态机定义的状态转换

**使用状态机定义进行转换**:

```sql
-- 基于状态机定义的状态转换
CREATE OR REPLACE FUNCTION transition_with_definition(
    p_entity_id BIGINT,
    p_machine_name VARCHAR,
    p_event_name VARCHAR
)
RETURNS JSONB AS $$
DECLARE
    v_current_state VARCHAR;
    v_machine_def JSONB;
    v_new_state VARCHAR;
    v_transitions JSONB;
BEGIN
    -- 获取当前状态
    SELECT state->>'current' INTO v_current_state
    FROM workflow_entity
    WHERE entity_id = p_entity_id;

    -- 获取状态机定义
    SELECT definition INTO v_machine_def
    FROM state_machine_definition
    WHERE machine_name = p_machine_name
      AND is_active = TRUE;

    IF v_machine_def IS NULL THEN
        RAISE EXCEPTION 'State machine % not found', p_machine_name;
    END IF;

    -- 查找转换规则
    v_transitions := v_machine_def->'states'->v_current_state->'transitions';

    IF v_transitions IS NULL THEN
        RAISE EXCEPTION 'No transitions defined for state %', v_current_state;
    END IF;

    -- 获取目标状态
    v_new_state := v_transitions->>p_event_name;

    IF v_new_state IS NULL THEN
        RAISE EXCEPTION 'Event % not allowed in state %', p_event_name, v_current_state;
    END IF;

    -- 执行转换
    RETURN transition_state_jsonb(p_entity_id, p_event_name, v_new_state);
END;
$$ LANGUAGE plpgsql;
```

---

## 4. 状态查询优化

### 4.1 状态查询函数

**高效状态查询**:

```sql
-- 查询特定状态的实体
CREATE OR REPLACE FUNCTION get_entities_by_state(
    p_state_name VARCHAR,
    p_limit INT DEFAULT 100
)
RETURNS TABLE (
    entity_id BIGINT,
    entity_type VARCHAR,
    state JSONB,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        we.entity_id,
        we.entity_type,
        we.state,
        we.updated_at
    FROM workflow_entity we
    WHERE we.state->>'current' = p_state_name
    ORDER BY we.updated_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- 查询状态历史
CREATE OR REPLACE FUNCTION get_state_history(
    p_entity_id BIGINT
)
RETURNS TABLE (
    state VARCHAR,
    timestamp TIMESTAMPTZ,
    event VARCHAR,
    previous_state VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (h->>'state')::VARCHAR AS state,
        (h->>'timestamp')::TIMESTAMPTZ AS timestamp,
        (h->>'event')::VARCHAR AS event,
        (h->>'previous')::VARCHAR AS previous_state
    FROM workflow_entity we,
         jsonb_array_elements(we.state->'history') AS h
    WHERE we.entity_id = p_entity_id
    ORDER BY (h->>'timestamp')::TIMESTAMPTZ DESC;
END;
$$ LANGUAGE plpgsql;
```

### 4.2 状态统计查询

**状态统计**:

```sql
-- 状态统计视图
CREATE VIEW state_statistics AS
SELECT
    entity_type,
    state->>'current' AS current_state,
    COUNT(*) AS entity_count,
    AVG(EXTRACT(EPOCH FROM (NOW() - updated_at))) AS avg_duration_seconds,
    MAX(updated_at) AS last_transition
FROM workflow_entity
GROUP BY entity_type, state->>'current';

-- 状态转换频率统计
CREATE VIEW transition_frequency AS
SELECT
    entity_type,
    (h->>'previous')::VARCHAR AS from_state,
    (h->>'state')::VARCHAR AS to_state,
    (h->>'event')::VARCHAR AS event_name,
    COUNT(*) AS transition_count
FROM workflow_entity we,
     jsonb_array_elements(we.state->'history') AS h
GROUP BY entity_type, from_state, to_state, event_name
ORDER BY transition_count DESC;
```

---

## 5. 最佳实践

### 5.1 设计建议

**JSONB状态机设计原则**:

1. **状态结构标准化**：统一的状态JSONB结构
2. **历史记录限制**：避免历史记录无限增长
3. **索引优化**：为常用查询创建索引
4. **验证机制**：在应用层验证状态转换

### 5.2 性能优化

**性能优化策略**:

```sql
-- 定期清理历史记录（保留最近N条）
CREATE OR REPLACE FUNCTION cleanup_state_history(
    p_entity_id BIGINT,
    p_keep_count INT DEFAULT 100
)
RETURNS VOID AS $$
DECLARE
    v_history JSONB;
    v_cleaned JSONB;
BEGIN
    SELECT state->'history' INTO v_history
    FROM workflow_entity
    WHERE entity_id = p_entity_id;

    -- 保留最近N条记录
    SELECT jsonb_agg(elem)
    INTO v_cleaned
    FROM (
        SELECT elem
        FROM jsonb_array_elements(v_history) AS elem
        ORDER BY (elem->>'timestamp')::TIMESTAMPTZ DESC
        LIMIT p_keep_count
    ) AS sub;

    -- 更新状态
    UPDATE workflow_entity
    SET state = jsonb_set(state, '{history}', v_cleaned)
    WHERE entity_id = p_entity_id;
END;
$$ LANGUAGE plpgsql;

-- 批量清理
CREATE OR REPLACE FUNCTION cleanup_all_state_history(p_keep_count INT DEFAULT 100)
RETURNS INT AS $$
DECLARE
    v_count INT := 0;
    v_entity RECORD;
BEGIN
    FOR v_entity IN SELECT entity_id FROM workflow_entity
    LOOP
        PERFORM cleanup_state_history(v_entity.entity_id, p_keep_count);
        v_count := v_count + 1;
    END LOOP;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;
```

### 5.3 错误处理

**状态转换错误处理**:

```sql
-- 带错误处理的状态转换
CREATE OR REPLACE FUNCTION safe_transition_state(
    p_entity_id BIGINT,
    p_machine_name VARCHAR,
    p_event_name VARCHAR
)
RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
    v_error TEXT;
BEGIN
    BEGIN
        v_result := transition_with_definition(p_entity_id, p_machine_name, p_event_name);
        RETURN v_result;
    EXCEPTION
        WHEN OTHERS THEN
            -- 记录错误到状态元数据
            UPDATE workflow_entity
            SET state = jsonb_set(
                state,
                '{metadata,last_error}',
                jsonb_build_object(
                    'error', SQLERRM,
                    'timestamp', NOW(),
                    'event', p_event_name
                )
            )
            WHERE entity_id = p_entity_id;

            RAISE;
    END;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. 更多实际案例 / More Practical Examples

### 6.1 案例1: 订单状态机（JSONB实现）

**完整订单状态机JSONB实现**:

```sql
-- 订单表（使用JSONB存储状态）
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    state JSONB NOT NULL DEFAULT '{
        "current": "created",
        "history": [],
        "metadata": {
            "created_at": null,
            "updated_at": null
        }
    }'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 订单状态机定义
INSERT INTO state_machine_definition (machine_name, definition) VALUES
('order', '{
    "states": {
        "created": {"type": "initial", "description": "订单已创建"},
        "paid": {"type": "normal", "description": "订单已支付"},
        "shipped": {"type": "normal", "description": "订单已发货"},
        "delivered": {"type": "final", "description": "订单已送达"},
        "cancelled": {"type": "final", "description": "订单已取消"}
    },
    "transitions": {
        "created": {"pay": "paid", "cancel": "cancelled"},
        "paid": {"ship": "shipped", "cancel": "cancelled"},
        "shipped": {"deliver": "delivered"}
    }
}'::jsonb);

-- 订单状态转换函数
CREATE OR REPLACE FUNCTION change_order_state(
    p_order_id BIGINT,
    p_event VARCHAR
)
RETURNS JSONB AS $$
DECLARE
    v_current_state VARCHAR;
    v_new_state VARCHAR;
    v_state_machine JSONB;
    v_new_state_json JSONB;
BEGIN
    -- 获取当前状态
    SELECT state->>'current' INTO v_current_state
    FROM orders WHERE order_id = p_order_id;

    -- 获取状态机定义
    SELECT definition INTO v_state_machine
    FROM state_machine_definition
    WHERE machine_name = 'order';

    -- 查找新状态
    v_new_state := v_state_machine->'transitions'->v_current_state->>p_event;

    IF v_new_state IS NULL THEN
        RAISE EXCEPTION 'Invalid transition from % with event %', v_current_state, p_event;
    END IF;

    -- 构建新状态JSONB
    v_new_state_json := jsonb_set(
        jsonb_set(
            jsonb_set(
                state,
                '{current}',
                to_jsonb(v_new_state)
            ),
            '{history}',
            (state->'history') || jsonb_build_object(
                'from', v_current_state,
                'to', v_new_state,
                'event', p_event,
                'timestamp', NOW()
            )
        ),
        '{metadata,updated_at}',
        to_jsonb(NOW())
    );

    -- 更新订单状态
    UPDATE orders
    SET state = v_new_state_json
    WHERE order_id = p_order_id;

    RETURN v_new_state_json;
END;
$$ LANGUAGE plpgsql;

-- 使用示例
SELECT change_order_state(1, 'pay');
SELECT change_order_state(1, 'ship');
```

### 6.2 案例2: 用户认证状态机

**用户认证流程JSONB状态机**:

```sql
-- 用户认证表
CREATE TABLE user_auth (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    state JSONB NOT NULL DEFAULT '{
        "current": "unverified",
        "attempts": 0,
        "locked_until": null,
        "metadata": {}
    }'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 认证状态机定义
INSERT INTO state_machine_definition (machine_name, definition) VALUES
('user_auth', '{
    "states": {
        "unverified": {"type": "initial"},
        "verified": {"type": "normal"},
        "locked": {"type": "normal"},
        "suspended": {"type": "final"}
    },
    "transitions": {
        "unverified": {"verify_email": "verified"},
        "verified": {"lock": "locked", "suspend": "suspended"},
        "locked": {"unlock": "verified"}
    }
}'::jsonb);

-- 认证状态转换函数（带条件检查）
CREATE OR REPLACE FUNCTION change_auth_state(
    p_user_id BIGINT,
    p_event VARCHAR,
    p_context JSONB DEFAULT '{}'::jsonb
)
RETURNS JSONB AS $$
DECLARE
    v_current_state VARCHAR;
    v_attempts INT;
    v_new_state_json JSONB;
BEGIN
    SELECT state->>'current', (state->>'attempts')::INT
    INTO v_current_state, v_attempts
    FROM user_auth WHERE user_id = p_user_id;

    -- 检查锁定状态
    IF v_current_state = 'locked' THEN
        IF (SELECT state->>'locked_until' FROM user_auth WHERE user_id = p_user_id)::TIMESTAMPTZ > NOW() THEN
            RAISE EXCEPTION 'Account is locked until %', (SELECT state->>'locked_until' FROM user_auth WHERE user_id = p_user_id);
        END IF;
    END IF;

    -- 处理登录失败
    IF p_event = 'login_failed' THEN
        v_attempts := v_attempts + 1;
        IF v_attempts >= 5 THEN
            v_new_state_json := jsonb_set(
                jsonb_set(
                    state,
                    '{current}',
                    '"locked"'::jsonb
                ),
                '{locked_until}',
                to_jsonb(NOW() + INTERVAL '30 minutes')
            );
        ELSE
            v_new_state_json := jsonb_set(state, '{attempts}', to_jsonb(v_attempts));
        END IF;
    ELSE
        -- 正常状态转换
        v_new_state_json := execute_state_transition('user_auth', v_current_state, p_event, state, p_context);
    END IF;

    UPDATE user_auth SET state = v_new_state_json WHERE user_id = p_user_id;
    RETURN v_new_state_json;
END;
$$ LANGUAGE plpgsql;
```

### 6.3 案例3: 库存管理状态机

**库存状态管理JSONB实现**:

```sql
-- 库存表
CREATE TABLE inventory (
    item_id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    state JSONB NOT NULL DEFAULT '{
        "current": "in_stock",
        "reserved": 0,
        "history": [],
        "alerts": []
    }'::jsonb
);

-- 库存状态机定义
INSERT INTO state_machine_definition (machine_name, definition) VALUES
('inventory', '{
    "states": {
        "in_stock": {"type": "normal"},
        "low_stock": {"type": "normal"},
        "out_of_stock": {"type": "normal"},
        "discontinued": {"type": "final"}
    },
    "transitions": {
        "in_stock": {"deplete": "low_stock", "sell_out": "out_of_stock", "discontinue": "discontinued"},
        "low_stock": {"restock": "in_stock", "sell_out": "out_of_stock"},
        "out_of_stock": {"restock": "in_stock"}
    },
    "conditions": {
        "low_stock": {"quantity": {"$lt": 10}},
        "out_of_stock": {"quantity": {"$eq": 0}}
    }
}'::jsonb);

-- 库存状态自动更新函数
CREATE OR REPLACE FUNCTION update_inventory_state(p_item_id BIGINT)
RETURNS JSONB AS $$
DECLARE
    v_quantity INT;
    v_current_state VARCHAR;
    v_new_state VARCHAR;
    v_state_machine JSONB;
BEGIN
    SELECT quantity, state->>'current'
    INTO v_quantity, v_current_state
    FROM inventory WHERE item_id = p_item_id;

    SELECT definition INTO v_state_machine
    FROM state_machine_definition WHERE machine_name = 'inventory';

    -- 根据数量自动确定状态
    IF v_quantity = 0 THEN
        v_new_state := 'out_of_stock';
    ELSIF v_quantity < 10 THEN
        v_new_state := 'low_stock';
    ELSE
        v_new_state := 'in_stock';
    END IF;

    -- 如果状态改变，更新状态
    IF v_new_state != v_current_state THEN
        UPDATE inventory
        SET state = jsonb_set(
            jsonb_set(
                jsonb_set(
                    state,
                    '{current}',
                    to_jsonb(v_new_state)
                ),
                '{history}',
                (state->'history') || jsonb_build_object(
                    'from', v_current_state,
                    'to', v_new_state,
                    'timestamp', NOW(),
                    'quantity', v_quantity
                )
            ),
            '{alerts}',
            CASE
                WHEN v_new_state = 'out_of_stock' THEN
                    (state->'alerts') || jsonb_build_object('type', 'out_of_stock', 'timestamp', NOW())
                WHEN v_new_state = 'low_stock' THEN
                    (state->'alerts') || jsonb_build_object('type', 'low_stock', 'timestamp', NOW())
                ELSE state->'alerts'
            END
        )
        WHERE item_id = p_item_id;
    END IF;

    RETURN (SELECT state FROM inventory WHERE item_id = p_item_id);
END;
$$ LANGUAGE plpgsql;
```

---

## 7. 性能优化与监控 / Performance Optimization and Monitoring

### 7.1 JSONB索引优化

**GIN索引优化**:

```sql
-- 为状态字段创建GIN索引
CREATE INDEX idx_orders_state_gin ON orders USING GIN (state);

-- 为特定路径创建索引
CREATE INDEX idx_orders_state_current ON orders ((state->>'current'));
CREATE INDEX idx_orders_state_metadata ON orders USING GIN ((state->'metadata'));

-- 复合索引（状态+时间）
CREATE INDEX idx_orders_state_created ON orders ((state->>'current'), created_at);

-- 部分索引（仅索引特定状态）
CREATE INDEX idx_orders_pending ON orders (order_id)
WHERE (state->>'current') IN ('created', 'paid');
```

### 7.2 查询性能优化

**查询优化示例**:

```sql
-- ✅ 优化：使用索引的查询
SELECT * FROM orders
WHERE state->>'current' = 'pending';  -- 使用索引

-- ❌ 未优化：使用函数查询
SELECT * FROM orders
WHERE jsonb_extract_path_text(state, 'current') = 'pending';  -- 不使用索引

-- ✅ 优化：使用GIN索引的包含查询
SELECT * FROM orders
WHERE state @> '{"current": "pending"}';  -- 使用GIN索引

-- ✅ 优化：使用表达式索引
SELECT * FROM orders
WHERE (state->>'current') = 'pending'  -- 使用表达式索引
ORDER BY created_at DESC;
```

### 7.3 状态机监控

**状态机监控查询**:

```sql
-- 监控：各状态的实体数量
SELECT
    state->>'current' AS current_state,
    COUNT(*) AS entity_count,
    MIN(created_at) AS oldest_entity,
    MAX(created_at) AS newest_entity
FROM orders
GROUP BY state->>'current'
ORDER BY entity_count DESC;

-- 监控：状态转换频率
SELECT
    state->'history'->-1->>'from' AS from_state,
    state->'history'->-1->>'to' AS to_state,
    state->'history'->-1->>'event' AS event,
    COUNT(*) AS transition_count
FROM orders
WHERE jsonb_array_length(state->'history') > 0
GROUP BY from_state, to_state, event
ORDER BY transition_count DESC;

-- 监控：长时间停留在某个状态的实体
SELECT
    order_id,
    state->>'current' AS current_state,
    (state->'metadata'->>'updated_at')::TIMESTAMPTZ AS last_update,
    NOW() - (state->'metadata'->>'updated_at')::TIMESTAMPTZ AS duration_in_state
FROM orders
WHERE state->>'current' NOT IN ('delivered', 'cancelled')
  AND (state->'metadata'->>'updated_at')::TIMESTAMPTZ < NOW() - INTERVAL '7 days'
ORDER BY duration_in_state DESC;
```

---

## 8. 常见问题解答 / FAQ

### Q1: JSONB状态机和传统状态表哪个更好？

**A**: 选择原则：

| 特性 | JSONB状态机 | 传统状态表 |
|------|------------|-----------|
| 灵活性 | ✅ 高（动态结构） | ❌ 低（固定结构） |
| 查询性能 | ⚠️ 中等（需要索引） | ✅ 高（直接查询） |
| 存储空间 | ⚠️ 较大 | ✅ 较小 |
| 维护复杂度 | ⚠️ 中等 | ✅ 简单 |

**建议**:

- 状态结构经常变化 → 使用JSONB
- 状态结构固定 → 使用传统表
- 需要复杂查询 → 使用传统表+JSONB混合

### Q2: JSONB状态机如何保证数据一致性？

**A**: 一致性保证：

```sql
-- 使用CHECK约束验证状态格式
ALTER TABLE orders
ADD CONSTRAINT chk_state_format
CHECK (
    state ? 'current' AND
    state ? 'history' AND
    jsonb_typeof(state->'history') = 'array'
);

-- 使用触发器验证状态转换
CREATE OR REPLACE FUNCTION validate_state_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- 验证状态转换是否合法
    IF NOT EXISTS (
        SELECT 1 FROM state_machine_definition
        WHERE machine_name = 'order'
          AND definition->'transitions'->(OLD.state->>'current') ? (NEW.state->'history'->-1->>'event')
    ) THEN
        RAISE EXCEPTION 'Invalid state transition';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_state
BEFORE UPDATE ON orders
FOR EACH ROW
WHEN (OLD.state->>'current' IS DISTINCT FROM NEW.state->>'current')
EXECUTE FUNCTION validate_state_transition();
```

### Q3: JSONB状态历史会很大，如何优化？

**A**: 优化策略：

1. **限制历史长度**: 只保留最近N条历史
2. **归档旧历史**: 将旧历史移到归档表
3. **压缩历史**: 使用JSONB压缩存储

```sql
-- 限制历史长度为100条
CREATE OR REPLACE FUNCTION trim_state_history()
RETURNS TRIGGER AS $$
BEGIN
    IF jsonb_array_length(NEW.state->'history') > 100 THEN
        NEW.state := jsonb_set(
            NEW.state,
            '{history}',
            (SELECT jsonb_agg(elem)
             FROM jsonb_array_elements(NEW.state->'history') WITH ORDINALITY AS t(elem, idx)
             WHERE idx > jsonb_array_length(NEW.state->'history') - 100)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Q4: JSONB状态机查询性能如何优化？

**A**: 性能优化建议：

1. **创建表达式索引**: 为频繁查询的路径创建索引
2. **使用物化视图**: 缓存状态统计信息
3. **避免深度嵌套**: 保持JSONB结构扁平化

```sql
-- 创建物化视图缓存状态统计
CREATE MATERIALIZED VIEW order_state_statistics AS
SELECT
    state->>'current' AS current_state,
    COUNT(*) AS count,
    AVG(total_amount) AS avg_amount
FROM orders
GROUP BY state->>'current';

CREATE INDEX ON order_state_statistics(current_state);

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY order_state_statistics;
```

### Q5: 如何实现JSONB状态机的回滚？

**A**: 回滚实现：

```sql
-- 回滚到历史中的某个状态
CREATE OR REPLACE FUNCTION rollback_state(
    p_order_id BIGINT,
    p_steps INT DEFAULT 1
)
RETURNS JSONB AS $$
DECLARE
    v_history JSONB;
    v_target_state JSONB;
BEGIN
    SELECT state->'history' INTO v_history
    FROM orders WHERE order_id = p_order_id;

    -- 获取目标历史记录
    v_target_state := v_history->(jsonb_array_length(v_history) - p_steps - 1);

    -- 恢复到目标状态
    UPDATE orders
    SET state = jsonb_set(
        jsonb_set(
            state,
            '{current}',
            v_target_state->'from'
        ),
        '{history}',
        (SELECT jsonb_agg(elem)
         FROM jsonb_array_elements(state->'history') WITH ORDINALITY AS t(elem, idx)
         WHERE idx <= jsonb_array_length(state->'history') - p_steps)
    )
    WHERE order_id = p_order_id;

    RETURN (SELECT state FROM orders WHERE order_id = p_order_id);
END;
$$ LANGUAGE plpgsql;
```

---

## 8. 相关资源 / Related Resources

### 8.1 核心相关文档 / Core Related Documents

- [状态机建模](./状态机建模.md) - 状态机建模基础
- [工作流模式](./工作流模式.md) - 工作流模式指南
- [BPMN建模](./BPMN建模.md) - BPMN标准建模
- [数据类型选择](../08-PostgreSQL建模实践/数据类型选择.md) - JSONB数据类型选择
- [索引策略](../08-PostgreSQL建模实践/索引策略.md) - JSONB索引设计

### 8.2 理论基础 / Theoretical Foundation

- [约束理论](../01-数据建模理论基础/约束理论.md) - JSONB状态约束理论

### 8.3 实践指南 / Practical Guides

- [性能优化与监控](#7-性能优化与监控--performance-optimization-and-monitoring) - 本文档的性能监控章节
- [更多实际案例](#6-更多实际案例--more-practical-examples) - 本文档的应用案例章节
- [性能优化](../08-PostgreSQL建模实践/性能优化.md) - JSONB查询性能优化

### 8.4 应用案例 / Application Cases

- [电商数据模型案例](../10-综合应用案例/电商数据模型案例.md) - 电商JSONB状态机案例

### 8.5 参考资源 / Reference Resources

- [权威资源索引](../00-导航与索引/权威资源索引.md) - 权威资源列表
- [术语对照表](../00-导航与索引/术语对照表.md) - 术语对照
- [快速查找指南](../00-导航与索引/快速查找指南.md) - 快速查找工具
- PostgreSQL官方文档: [JSONB Types](https://www.postgresql.org/docs/current/datatype-json.html)
- PostgreSQL官方文档: [GIN Indexes](https://www.postgresql.org/docs/current/gin.html)

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
