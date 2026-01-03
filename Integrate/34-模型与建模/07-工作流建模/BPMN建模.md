# BPMN建模完整指南

> **创建日期**: 2025年1月
> **来源**: OMG BPMN 2.0标准 + 实践总结
> **状态**: 基于权威标准深化扩展
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
  - [5. 相关资源](#5-相关资源)

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

## 5. 相关资源

- [状态机建模](./状态机建模.md) - 状态机建模基础
- [工作流模式](./工作流模式.md) - 工作流模式指南
- [OMG BPMN 2.0标准](https://www.omg.org/spec/BPMN/2.0/) - BPMN官方标准
- [Camunda文档](https://docs.camunda.org/) - Camunda BPMN引擎文档
- [Flowable文档](https://www.flowable.com/open-source/docs/) - Flowable文档

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
