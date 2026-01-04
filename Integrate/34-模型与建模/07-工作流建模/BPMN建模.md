# BPMN建模完整指南

> **创建日期**: 2025年1月
> **来源**: OMG BPMN 2.0标准 + 实践总结
> **状态**: ✅ 已完成
> **文档编号**: 07-01

---

## 📑 目录

- [BPMN建模完整指南](#bpmn建模完整指南)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. BPMN核心元素](#2-bpmn核心元素)
    - [2.1 流程定义](#21-流程定义)
    - [2.2 任务类型](#22-任务类型)
    - [2.3 网关类型](#23-网关类型)
  - [3. PostgreSQL实现](#3-postgresql实现)
    - [3.1 流程定义表](#31-流程定义表)
    - [3.2 BPMN解析函数](#32-bpmn解析函数)
    - [3.3 流程实例管理](#33-流程实例管理)
  - [4. 工作流引擎集成](#4-工作流引擎集成)
    - [4.1 推荐引擎](#41-推荐引擎)
    - [4.2 数据库集成](#42-数据库集成)
  - [5. 实际应用案例 / Practical Application Examples](#5-实际应用案例--practical-application-examples)
    - [5.1 案例1: 订单审批流程](#51-案例1-订单审批流程)
    - [5.2 案例2: 文档审批流程](#52-案例2-文档审批流程)
    - [5.3 案例3: 请假申请流程](#53-案例3-请假申请流程)
  - [6. 性能优化与监控 / Performance Optimization and Monitoring](#6-性能优化与监控--performance-optimization-and-monitoring)
    - [6.1 BPMN流程性能优化](#61-bpmn流程性能优化)
    - [6.2 流程监控与诊断](#62-流程监控与诊断)
  - [7. 常见问题解答 / FAQ](#7-常见问题解答--faq)
    - [Q1: BPMN流程如何与PostgreSQL集成？](#q1-bpmn流程如何与postgresql集成)
    - [Q2: 如何处理BPMN流程的并发执行？](#q2-如何处理bpmn流程的并发执行)
    - [Q3: 如何优化BPMN流程查询性能？](#q3-如何优化bpmn流程查询性能)
    - [Q4: BPMN流程如何实现超时处理？](#q4-bpmn流程如何实现超时处理)
    - [Q5: 如何实现BPMN流程的版本管理？](#q5-如何实现bpmn流程的版本管理)
  - [7. 相关资源 / Related Resources](#7-相关资源--related-resources)
    - [7.1 核心相关文档 / Core Related Documents](#71-核心相关文档--core-related-documents)
    - [7.2 理论基础 / Theoretical Foundation](#72-理论基础--theoretical-foundation)
    - [7.3 实践指南 / Practical Guides](#73-实践指南--practical-guides)
    - [7.4 应用案例 / Application Cases](#74-应用案例--application-cases)
    - [7.5 参考资源 / Reference Resources](#75-参考资源--reference-resources)

---

## 1. 概述

BPMN（Business Process Model and Notation）是OMG组织维护的业务流程建模标准。
BPMN 2.0定义了完整的业务流程建模语言，支持流程定义、执行和监控。

---

## 2. BPMN核心元素

### 2.1 流程定义

**BPMN核心元素**:

| 元素类型 | 说明 | 示例 |
|---------|------|------|
| Process（流程） | 业务流程定义 | 订单处理流程 |
| Task（任务） | 需要执行的工作 | 验证订单、处理支付 |
| Gateway（网关） | 流程分支控制 | 排他网关、并行网关 |
| Event（事件） | 流程中的事件 | 开始事件、结束事件 |
| Sequence Flow（顺序流） | 连接元素的有向箭头 | 任务A → 任务B |
| Data Object（数据对象） | 流程中的数据 | 订单信息、支付结果 |

### 2.2 任务类型

**BPMN任务类型**:

- **User Task（用户任务）**：需要人工参与
- **Service Task（服务任务）**：调用外部服务
- **Script Task（脚本任务）**：执行脚本
- **Business Rule Task（业务规则任务）**：执行业务规则

### 2.3 网关类型

**BPMN网关类型**:

- **Exclusive Gateway（排他网关）**：互斥选择，只有一个分支执行
- **Parallel Gateway（并行网关）**：并行执行多个分支
- **Inclusive Gateway（包容网关）**：一个或多个分支执行
- **Event Gateway（事件网关）**：基于事件的选择

---

## 3. PostgreSQL实现

### 3.1 流程定义表

**BPMN流程定义存储**:

```sql
-- BPMN流程定义表
CREATE TABLE bpmn_process_definition (
    process_id SERIAL PRIMARY KEY,
    process_key VARCHAR(100) NOT NULL UNIQUE,
    process_name VARCHAR(200) NOT NULL,
    version INT NOT NULL DEFAULT 1,
    -- BPMN XML定义
    bpmn_xml TEXT NOT NULL,
    -- 解析后的JSON结构（便于查询）
    bpmn_json JSONB,
    -- 流程元数据
    description TEXT,
    category VARCHAR(100),
    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    is_deployed BOOLEAN DEFAULT FALSE,
    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deployed_at TIMESTAMPTZ,
    UNIQUE(process_key, version)
);

-- 流程实例表
CREATE TABLE bpmn_process_instance (
    instance_id BIGSERIAL PRIMARY KEY,
    process_id INT NOT NULL REFERENCES bpmn_process_definition(process_id),
    process_key VARCHAR(100) NOT NULL,
    -- 实例状态
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'terminated', 'suspended'
    -- 业务键
    business_key VARCHAR(200),
    -- 实例变量
    variables JSONB DEFAULT '{}',
    -- 时间戳
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    started_by VARCHAR(100)
);

-- 任务实例表
CREATE TABLE bpmn_task_instance (
    task_id BIGSERIAL PRIMARY KEY,
    instance_id BIGINT NOT NULL REFERENCES bpmn_process_instance(instance_id),
    -- 任务定义
    task_key VARCHAR(100) NOT NULL,
    task_name VARCHAR(200),
    task_type VARCHAR(50), -- 'user', 'service', 'script', 'business_rule'
    -- 任务状态
    status VARCHAR(50) DEFAULT 'created', -- 'created', 'assigned', 'completed', 'cancelled'
    -- 分配信息
    assignee VARCHAR(100),
    candidate_users TEXT[],
    candidate_groups TEXT[],
    -- 任务变量
    task_variables JSONB DEFAULT '{}',
    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    due_date TIMESTAMPTZ
);

-- 流程执行历史表
CREATE TABLE bpmn_execution_history (
    history_id BIGSERIAL PRIMARY KEY,
    instance_id BIGINT NOT NULL,
    activity_id VARCHAR(100) NOT NULL,
    activity_type VARCHAR(50), -- 'task', 'gateway', 'event'
    activity_name VARCHAR(200),
    -- 执行状态
    status VARCHAR(50), -- 'started', 'completed', 'cancelled'
    -- 执行变量快照
    variables JSONB,
    -- 时间戳
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    duration_ms BIGINT GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (end_time - start_time)) * 1000
    ) STORED
);

-- 创建索引
CREATE INDEX idx_process_instance_status ON bpmn_process_instance(status, started_at DESC);
CREATE INDEX idx_task_instance_assignee ON bpmn_task_instance(assignee, status);
CREATE INDEX idx_task_instance_instance ON bpmn_task_instance(instance_id, status);
CREATE INDEX idx_execution_history_instance ON bpmn_execution_history(instance_id, start_time DESC);
```

### 3.2 BPMN解析函数

**解析BPMN XML**:

```sql
-- 解析BPMN XML并存储JSON结构
CREATE OR REPLACE FUNCTION parse_bpmn_xml(p_bpmn_xml TEXT)
RETURNS JSONB AS $$
DECLARE
    v_bpmn_json JSONB;
BEGIN
    -- 这里应该使用XML解析库（如PostgreSQL的xml2扩展）
    -- 简化示例：提取关键信息
    -- 实际实现需要使用xml2扩展或外部解析器

    -- 示例：提取流程ID和名称
    v_bpmn_json := jsonb_build_object(
        'process_id', regexp_replace(p_bpmn_xml, '.*process id="([^"]+)".*', '\1', 'g'),
        'process_name', regexp_replace(p_bpmn_xml, '.*name="([^"]+)".*', '\1', 'g'),
        'tasks', '[]'::JSONB,
        'gateways', '[]'::JSONB,
        'events', '[]'::JSONB
    );

    RETURN v_bpmn_json;
END;
$$ LANGUAGE plpgsql;

-- 部署流程定义
CREATE OR REPLACE FUNCTION deploy_process_definition(
    p_process_key VARCHAR,
    p_process_name VARCHAR,
    p_bpmn_xml TEXT
)
RETURNS INT AS $$
DECLARE
    v_process_id INT;
    v_bpmn_json JSONB;
BEGIN
    -- 解析BPMN XML
    v_bpmn_json := parse_bpmn_xml(p_bpmn_xml);

    -- 插入流程定义
    INSERT INTO bpmn_process_definition (
        process_key, process_name, bpmn_xml, bpmn_json, is_deployed
    ) VALUES (
        p_process_key, p_process_name, p_bpmn_xml, v_bpmn_json, TRUE
    ) RETURNING process_id INTO v_process_id;

    RETURN v_process_id;
END;
$$ LANGUAGE plpgsql;
```

### 3.3 流程实例管理

**启动和管理流程实例**:

```sql
-- 启动流程实例
CREATE OR REPLACE FUNCTION start_process_instance(
    p_process_key VARCHAR,
    p_business_key VARCHAR DEFAULT NULL,
    p_variables JSONB DEFAULT '{}',
    p_started_by VARCHAR DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_process_id INT;
    v_instance_id BIGINT;
BEGIN
    -- 获取最新版本的流程定义
    SELECT process_id INTO v_process_id
    FROM bpmn_process_definition
    WHERE process_key = p_process_key
      AND is_active = TRUE
      AND is_deployed = TRUE
    ORDER BY version DESC
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Process definition % not found or not deployed', p_process_key;
    END IF;

    -- 创建流程实例
    INSERT INTO bpmn_process_instance (
        process_id, process_key, business_key, variables, started_by
    ) VALUES (
        v_process_id, p_process_key, p_business_key, p_variables, p_started_by
    ) RETURNING instance_id INTO v_instance_id;

    -- 创建初始任务（根据BPMN定义）
    -- 这里应该解析BPMN定义，创建相应的任务实例
    -- 简化示例：创建第一个用户任务
    INSERT INTO bpmn_task_instance (
        instance_id, task_key, task_name, task_type, status
    ) VALUES (
        v_instance_id, 'start_task', '开始任务', 'user', 'created'
    );

    RETURN v_instance_id;
END;
$$ LANGUAGE plpgsql;

-- 完成任务
CREATE OR REPLACE FUNCTION complete_task(
    p_task_id BIGINT,
    p_task_variables JSONB DEFAULT '{}',
    p_completed_by VARCHAR DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    v_instance_id BIGINT;
BEGIN
    -- 更新任务状态
    UPDATE bpmn_task_instance
    SET status = 'completed',
        task_variables = task_variables || p_task_variables,
        completed_at = NOW()
    WHERE task_id = p_task_id
      AND status IN ('created', 'assigned');

    -- 获取实例ID
    SELECT instance_id INTO v_instance_id
    FROM bpmn_task_instance
    WHERE task_id = p_task_id;

    -- 记录执行历史
    INSERT INTO bpmn_execution_history (
        instance_id, activity_id, activity_type, activity_name,
        status, variables, start_time, end_time
    )
    SELECT
        instance_id, task_key, task_type, task_name,
        'completed', task_variables, created_at, NOW()
    FROM bpmn_task_instance
    WHERE task_id = p_task_id;

    -- 检查流程是否完成（简化逻辑）
    -- 实际应该根据BPMN定义判断
    IF NOT EXISTS (
        SELECT 1 FROM bpmn_task_instance
        WHERE instance_id = v_instance_id
          AND status IN ('created', 'assigned')
    ) THEN
        UPDATE bpmn_process_instance
        SET status = 'completed',
            ended_at = NOW()
        WHERE instance_id = v_instance_id;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

---

## 4. 工作流引擎集成

### 4.1 推荐引擎

**主流BPMN引擎**:

| 引擎 | 特点 | 适用场景 |
|------|------|---------|
| **Camunda** | 开源，功能完整，社区活跃 | 企业级工作流 |
| **Activiti** | 轻量级，易于集成 | 中小型项目 |
| **Flowable** | 基于Activiti，性能优化 | 高性能需求 |
| **jBPM** | Red Hat支持，企业级 | 大型企业 |

### 4.2 数据库集成

**PostgreSQL作为BPMN引擎后端**:

```sql
-- Camunda使用PostgreSQL作为数据库
-- 需要创建Camunda的表结构
-- 参考：https://github.com/camunda/camunda-bpm-platform/tree/master/engine/src/main/resources/org/camunda/bpm/engine/db

-- 示例：Camunda核心表（简化）
CREATE TABLE act_ru_execution (
    id_ VARCHAR(64) PRIMARY KEY,
    rev_ INT,
    proc_inst_id_ VARCHAR(64),
    business_key_ VARCHAR(255),
    parent_id_ VARCHAR(64),
    proc_def_id_ VARCHAR(64),
    act_id_ VARCHAR(255),
    is_active_ BOOLEAN,
    is_concurrent_ BOOLEAN,
    is_scope_ BOOLEAN,
    suspension_state_ INT,
    cached_ent_state_ INT
);

-- 流程定义查询视图
CREATE VIEW bpmn_process_view AS
SELECT
    pd.process_id,
    pd.process_key,
    pd.process_name,
    pd.version,
    COUNT(DISTINCT pi.instance_id) AS instance_count,
    COUNT(DISTINCT CASE WHEN pi.status = 'running' THEN pi.instance_id END) AS running_count,
    COUNT(DISTINCT CASE WHEN pi.status = 'completed' THEN pi.instance_id END) AS completed_count
FROM bpmn_process_definition pd
LEFT JOIN bpmn_process_instance pi ON pd.process_id = pi.process_id
GROUP BY pd.process_id, pd.process_key, pd.process_name, pd.version;
```

---

## 5. 实际应用案例 / Practical Application Examples

### 5.1 案例1: 订单审批流程

**订单审批BPMN流程实现**:

```sql
-- 订单审批流程定义
INSERT INTO bpmn_process_definition (
    process_key, process_name, version, bpmn_xml
) VALUES (
    'order_approval',
    '订单审批流程',
    1,
    '<?xml version="1.0" encoding="UTF-8"?>
    <bpmn:definitions>
        <bpmn:process id="order_approval" name="订单审批流程">
            <bpmn:startEvent id="start"/>
            <bpmn:userTask id="review_order" name="审核订单"/>
            <bpmn:exclusiveGateway id="approval_gateway"/>
            <bpmn:userTask id="approve_order" name="批准订单"/>
            <bpmn:userTask id="reject_order" name="拒绝订单"/>
            <bpmn:endEvent id="end"/>
            <bpmn:sequenceFlow id="flow1" sourceRef="start" targetRef="review_order"/>
            <bpmn:sequenceFlow id="flow2" sourceRef="review_order" targetRef="approval_gateway"/>
            <bpmn:sequenceFlow id="flow3" sourceRef="approval_gateway" targetRef="approve_order">
                <bpmn:conditionExpression>${approved == true}</bpmn:conditionExpression>
            </bpmn:sequenceFlow>
            <bpmn:sequenceFlow id="flow4" sourceRef="approval_gateway" targetRef="reject_order">
                <bpmn:conditionExpression>${approved == false}</bpmn:conditionExpression>
            </bpmn:sequenceFlow>
            <bpmn:sequenceFlow id="flow5" sourceRef="approve_order" targetRef="end"/>
            <bpmn:sequenceFlow id="flow6" sourceRef="reject_order" targetRef="end"/>
        </bpmn:process>
    </bpmn:definitions>'
);

-- 启动订单审批流程
CREATE OR REPLACE FUNCTION start_order_approval_process(
    p_order_id BIGINT,
    p_applicant_id BIGINT
)
RETURNS VARCHAR AS $$
DECLARE
    v_instance_id VARCHAR;
BEGIN
    -- 创建流程实例
    INSERT INTO bpmn_process_instance (
        instance_id, process_id, business_key, status, start_time
    )
    SELECT
        'PI_' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '_' || p_order_id,
        process_id,
        'ORDER_' || p_order_id,
        'running',
        NOW()
    FROM bpmn_process_definition
    WHERE process_key = 'order_approval' AND version = 1
    RETURNING instance_id INTO v_instance_id;

    -- 创建第一个任务
    INSERT INTO bpmn_task (
        task_id, instance_id, task_name, assignee, status
    )
    VALUES (
        'TASK_' || v_instance_id || '_1',
        v_instance_id,
        '审核订单',
        (SELECT user_id FROM users WHERE role = 'reviewer' LIMIT 1),
        'pending'
    );

    RETURN v_instance_id;
END;
$$ LANGUAGE plpgsql;
```

### 5.2 案例2: 文档审批流程

**文档审批BPMN流程实现**:

```sql
-- 文档审批流程（多级审批）
CREATE TABLE document_approval_process (
    process_id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL,
    current_level INT DEFAULT 1,
    max_level INT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 多级审批函数
CREATE OR REPLACE FUNCTION process_document_approval(
    p_document_id BIGINT,
    p_approver_id BIGINT,
    p_approved BOOLEAN,
    p_comment TEXT
)
RETURNS VOID AS $$
DECLARE
    v_current_level INT;
    v_max_level INT;
BEGIN
    -- 获取当前审批级别
    SELECT current_level, max_level INTO v_current_level, v_max_level
    FROM document_approval_process
    WHERE document_id = p_document_id;

    -- 记录审批结果
    INSERT INTO document_approval_history (
        document_id, approver_id, approval_level, approved, comment, approved_at
    )
    VALUES (
        p_document_id, p_approver_id, v_current_level, p_approved, p_comment, NOW()
    );

    IF p_approved THEN
        IF v_current_level < v_max_level THEN
            -- 进入下一级审批
            UPDATE document_approval_process
            SET current_level = current_level + 1
            WHERE document_id = p_document_id;
        ELSE
            -- 所有级别审批完成
            UPDATE document_approval_process
            SET status = 'approved'
            WHERE document_id = p_document_id;
        END IF;
    ELSE
        -- 审批被拒绝
        UPDATE document_approval_process
        SET status = 'rejected'
        WHERE document_id = p_document_id;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### 5.3 案例3: 请假申请流程

**请假申请BPMN流程实现**:

```sql
-- 请假申请流程
CREATE TABLE leave_application_process (
    process_id BIGSERIAL PRIMARY KEY,
    applicant_id BIGINT NOT NULL,
    leave_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days INT NOT NULL,
    reason TEXT,
    approver_id BIGINT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 请假申请处理函数
CREATE OR REPLACE FUNCTION process_leave_application(
    p_applicant_id BIGINT,
    p_leave_type VARCHAR,
    p_start_date DATE,
    p_end_date DATE,
    p_reason TEXT
)
RETURNS BIGINT AS $$
DECLARE
    v_process_id BIGINT;
    v_days INT;
    v_approver_id BIGINT;
BEGIN
    -- 计算请假天数
    v_days := p_end_date - p_start_date + 1;

    -- 根据请假类型和天数确定审批人
    IF p_leave_type = 'annual' AND v_days <= 3 THEN
        -- 年假3天以内，直接主管审批
        SELECT manager_id INTO v_approver_id FROM employees WHERE employee_id = p_applicant_id;
    ELSIF p_leave_type = 'annual' AND v_days > 3 THEN
        -- 年假3天以上，需要部门经理审批
        SELECT department_manager_id INTO v_approver_id
        FROM employees e
        JOIN departments d ON e.department_id = d.department_id
        WHERE e.employee_id = p_applicant_id;
    ELSE
        -- 其他类型，需要HR审批
        SELECT user_id INTO v_approver_id FROM users WHERE role = 'hr' LIMIT 1;
    END IF;

    -- 创建请假申请
    INSERT INTO leave_application_process (
        applicant_id, leave_type, start_date, end_date, days, reason, approver_id
    )
    VALUES (
        p_applicant_id, p_leave_type, p_start_date, p_end_date, v_days, p_reason, v_approver_id
    )
    RETURNING process_id INTO v_process_id;

    -- 创建审批任务
    INSERT INTO bpmn_task (
        task_id, instance_id, task_name, assignee, status, business_key
    )
    VALUES (
        'TASK_' || v_process_id,
        'LEAVE_' || v_process_id,
        '审批请假申请',
        v_approver_id,
        'pending',
        'LEAVE_' || v_process_id
    );

    RETURN v_process_id;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. 性能优化与监控 / Performance Optimization and Monitoring

### 6.1 BPMN流程性能优化

**索引优化**:

```sql
-- 流程实例索引
CREATE INDEX idx_process_instance_status ON bpmn_process_instance(status, start_time DESC);
CREATE INDEX idx_process_instance_business_key ON bpmn_process_instance(business_key);
CREATE INDEX idx_process_instance_process ON bpmn_process_instance(process_id, status);

-- 任务索引
CREATE INDEX idx_task_assignee_status ON bpmn_task(assignee, status);
CREATE INDEX idx_task_instance ON bpmn_task(instance_id, status);
CREATE INDEX idx_task_due_date ON bpmn_task(due_date) WHERE status = 'pending';
```

**查询优化**:

```sql
-- ✅ 优化：使用覆盖索引查询待办任务
CREATE INDEX idx_task_assignee_covering ON bpmn_task(assignee, status)
INCLUDE (task_id, task_name, instance_id, created_time)
WHERE status = 'pending';

-- 查询仅需扫描索引
SELECT task_id, task_name, instance_id, created_time
FROM bpmn_task
WHERE assignee = 123 AND status = 'pending';
```

### 6.2 流程监控与诊断

**流程性能监控**:

```sql
-- 监控：流程执行性能
SELECT
    pd.process_name,
    COUNT(*) AS instance_count,
    AVG(EXTRACT(EPOCH FROM (pi.end_time - pi.start_time))) AS avg_duration_seconds,
    MAX(EXTRACT(EPOCH FROM (pi.end_time - pi.start_time))) AS max_duration_seconds,
    COUNT(*) FILTER (WHERE pi.status = 'completed') AS completed_count,
    COUNT(*) FILTER (WHERE pi.status = 'running') AS running_count
FROM bpmn_process_definition pd
LEFT JOIN bpmn_process_instance pi ON pd.process_id = pi.process_id
WHERE pi.start_time >= NOW() - INTERVAL '24 hours'
GROUP BY pd.process_id, pd.process_name;

-- 监控：任务处理性能
SELECT
    task_name,
    COUNT(*) AS task_count,
    AVG(EXTRACT(EPOCH FROM (completed_time - created_time))) AS avg_processing_seconds,
    COUNT(*) FILTER (WHERE status = 'pending') AS pending_count,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_count
FROM bpmn_task
WHERE created_time >= NOW() - INTERVAL '24 hours'
GROUP BY task_name
ORDER BY task_count DESC;
```

---

## 7. 常见问题解答 / FAQ

### Q1: BPMN流程如何与PostgreSQL集成？

**A**: 集成策略：

```sql
-- 方案1：使用PostgreSQL存储BPMN流程定义和实例
CREATE TABLE bpmn_process_definition (...);
CREATE TABLE bpmn_process_instance (...);
CREATE TABLE bpmn_task (...);

-- 方案2：使用外部BPMN引擎（Camunda、Flowable）
-- 将流程数据存储在PostgreSQL中
-- 使用REST API或消息队列与引擎通信
```

### Q2: 如何处理BPMN流程的并发执行？

**A**: 并发控制策略：

```sql
-- 使用行级锁
BEGIN;
SELECT * FROM bpmn_task
WHERE task_id = 'TASK_123' AND status = 'pending'
FOR UPDATE;

-- 更新任务状态
UPDATE bpmn_task
SET status = 'completed', completed_time = NOW()
WHERE task_id = 'TASK_123';
COMMIT;

-- 使用乐观锁（版本号）
CREATE TABLE bpmn_task (
    task_id VARCHAR PRIMARY KEY,
    version INT DEFAULT 1,
    ...
);

UPDATE bpmn_task
SET status = 'completed',
    version = version + 1
WHERE task_id = 'TASK_123' AND version = 1;
```

### Q3: 如何优化BPMN流程查询性能？

**A**: 查询优化策略：

1. **索引优化**: 为常用查询创建索引
2. **物化视图**: 预计算流程统计
3. **分区优化**: 按时间分区流程实例表

```sql
-- 创建流程统计物化视图
CREATE MATERIALIZED VIEW mv_process_statistics AS
SELECT
    pd.process_name,
    DATE_TRUNC('day', pi.start_time) AS process_day,
    COUNT(*) AS instance_count,
    AVG(EXTRACT(EPOCH FROM (pi.end_time - pi.start_time))) AS avg_duration
FROM bpmn_process_definition pd
JOIN bpmn_process_instance pi ON pd.process_id = pi.process_id
GROUP BY pd.process_name, DATE_TRUNC('day', pi.start_time);

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_process_statistics;
```

### Q4: BPMN流程如何实现超时处理？

**A**: 超时处理实现：

```sql
-- 任务超时检查函数
CREATE OR REPLACE FUNCTION check_task_timeout()
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    -- 查找超时的任务
    UPDATE bpmn_task
    SET status = 'timeout',
        timeout_time = NOW()
    WHERE status = 'pending'
      AND due_date < NOW()
      AND due_date IS NOT NULL;

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- 定时执行超时检查（使用pg_cron）
SELECT cron.schedule('check-task-timeout', '*/5 * * * *',
    'SELECT check_task_timeout();');
```

### Q5: 如何实现BPMN流程的版本管理？

**A**: 版本管理策略：

```sql
-- 流程定义版本管理
CREATE TABLE bpmn_process_definition (
    process_id BIGSERIAL PRIMARY KEY,
    process_key VARCHAR(100) NOT NULL,
    version INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(process_key, version)
);

-- 查询最新版本
SELECT * FROM bpmn_process_definition
WHERE process_key = 'order_approval'
  AND is_active = TRUE
ORDER BY version DESC
LIMIT 1;

-- 流程实例关联版本
CREATE TABLE bpmn_process_instance (
    instance_id VARCHAR PRIMARY KEY,
    process_id BIGINT NOT NULL REFERENCES bpmn_process_definition(process_id),
    process_version INT NOT NULL,
    ...
);
```

---

## 7. 相关资源 / Related Resources

### 7.1 核心相关文档 / Core Related Documents

- [状态机建模](./状态机建模.md) - 状态机建模基础
- [工作流模式](./工作流模式.md) - 工作流模式指南
- [JSONB状态机实现](./JSONB状态机实现.md) - JSONB实现状态机
- [订单管理模型](../04-OLTP建模/订单管理模型.md) - 订单BPMN流程案例

### 7.2 理论基础 / Theoretical Foundation

- [约束理论](../01-数据建模理论基础/约束理论.md) - BPMN流程约束理论

### 7.3 实践指南 / Practical Guides

- [性能优化与监控](#6-性能优化与监控--performance-optimization-and-monitoring) - 本文档的性能监控章节
- [实际应用案例](#5-实际应用案例--practical-application-examples) - 本文档的应用案例章节
- [性能优化](../08-PostgreSQL建模实践/性能优化.md) - BPMN流程性能优化

### 7.4 应用案例 / Application Cases

- [电商数据模型案例](../10-综合应用案例/电商数据模型案例.md) - 电商BPMN流程案例
- [金融数据模型案例](../10-综合应用案例/金融数据模型案例.md) - 金融BPMN流程案例

### 7.5 参考资源 / Reference Resources

- [权威资源索引](../00-导航与索引/权威资源索引.md) - 权威资源列表
- [术语对照表](../00-导航与索引/术语对照表.md) - 术语对照
- [快速查找指南](../00-导航与索引/快速查找指南.md) - 快速查找工具
- OMG BPMN 2.0标准: [BPMN 2.0 Specification](https://www.omg.org/spec/BPMN/2.0/)
- Camunda文档: [Camunda BPMN Engine](https://docs.camunda.org/)
- Flowable文档: [Flowable Documentation](https://www.flowable.com/open-source/docs/)

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
