# BPMN建模完整指南

> **创建日期**: 2025年1月
> **来源**: OMG BPMN 2.0标准 + 实践总结
> **状态**: 基于权威标准深化扩展
> **文档编号**: 07-01

---

## 📑 目录

- [1. 概述](#1-概述)
- [2. BPMN核心元素](#2-bpmn核心元素)
- [3. PostgreSQL实现](#3-postgresql实现)
- [4. 工作流引擎集成](#4-工作流引擎集成)
- [5. 相关资源](#5-相关资源)

---

## 1. 概述

BPMN（Business Process Model and Notation）是OMG组织维护的业务流程建模标准。BPMN 2.0定义了完整的业务流程建模语言，支持流程定义、执行和监控。

---

## 2. BPMN核心元素

### 2.1 流程定义

**核心概念**:
- Process（流程）
- Task（任务）
- Gateway（网关）
- Event（事件）

---

## 3. PostgreSQL实现

### 3.1 流程定义表

```sql
-- 流程定义表
CREATE TABLE bpmn_process_definition (
    process_id SERIAL PRIMARY KEY,
    process_key VARCHAR(100) NOT NULL UNIQUE,
    process_name VARCHAR(200) NOT NULL,
    version INT NOT NULL DEFAULT 1,
    bpmn_xml TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 4. 工作流引擎集成

**推荐引擎**:
- Camunda
- Activiti
- Flowable

---

## 5. 相关资源

- OMG BPMN 2.0标准: https://www.omg.org/spec/BPMN/2.0/
- Camunda文档: https://docs.camunda.org/

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
