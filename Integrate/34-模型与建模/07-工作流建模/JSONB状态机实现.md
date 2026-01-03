# JSONB状态机实现

> **创建日期**: 2025年1月
> **来源**: PostgreSQL JSONB实践
> **状态**: 待完善
> **文档编号**: 07-03

---

## 📑 目录

- [JSONB状态机实现](#jsonb状态机实现)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
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
  - [6. 相关资源](#6-相关资源)

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

## 2. JSONB状态存储

### 2.1 状态数据结构设计

**状态JSONB结构**:

```sql
-- 使用JSONB存储状态的表
CREATE TABLE workflow_entity (
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
-- 状态机定义表（使用JSONB存储完整定义）
CREATE TABLE state_machine_definition (
    machine_id SERIAL PRIMARY KEY,
    machine_name VARCHAR(100) UNIQUE NOT NULL,
    -- JSONB存储完整状态机定义
    definition JSONB NOT NULL,
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 状态机定义JSONB结构示例
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
);
```

### 2.3 索引优化

**JSONB索引创建**:

```sql
-- GIN索引：支持JSONB查询
CREATE INDEX idx_workflow_state_current ON workflow_entity USING GIN((state->'current'));
CREATE INDEX idx_workflow_state_metadata ON workflow_entity USING GIN((state->'metadata'));

-- 表达式索引：状态查询优化
CREATE INDEX idx_workflow_current_state ON workflow_entity((state->>'current'))
    WHERE (state->>'current') IS NOT NULL;

-- 部分索引：特定状态查询
CREATE INDEX idx_workflow_pending ON workflow_entity(entity_id)
    WHERE (state->>'current') = 'pending';
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

## 6. 相关资源

- [状态机建模](./状态机建模.md) - 状态机建模基础
- [工作流模式](./工作流模式.md) - 工作流模式指南
- [PostgreSQL JSONB文档](https://www.postgresql.org/docs/current/datatype-json.html) - JSONB类型文档
- [JSONB索引优化](https://www.postgresql.org/docs/current/gin.html) - GIN索引指南

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
