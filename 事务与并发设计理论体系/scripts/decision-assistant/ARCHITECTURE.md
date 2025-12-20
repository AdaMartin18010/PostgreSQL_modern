# 并发控制决策助手 - 架构设计文档

> **版本**: 1.0.0
> **创建日期**: 2025-12-05
> **状态**: 🚀 开发中

---

## 📋 目录

- [并发控制决策助手 - 架构设计文档](#并发控制决策助手---架构设计文档)
  - [📋 目录](#-目录)
  - [架构概述](#架构概述)
    - [系统定位](#系统定位)
    - [核心功能](#核心功能)
  - [系统架构](#系统架构)
    - [整体架构图](#整体架构图)
  - [技术栈](#技术栈)
    - [前端技术栈](#前端技术栈)
    - [后端技术栈](#后端技术栈)
    - [数据存储](#数据存储)
  - [模块设计](#模块设计)
    - [1. 决策树引擎 (Decision Engine)](#1-决策树引擎-decision-engine)
    - [2. 性能预测器 (Performance Predictor)](#2-性能预测器-performance-predictor)
    - [3. 代码生成器 (Code Generator)](#3-代码生成器-code-generator)
    - [4. 方案对比器 (Comparison Engine)](#4-方案对比器-comparison-engine)
  - [API设计](#api设计)
    - [RESTful API](#restful-api)
      - [1. 获取推荐方案](#1-获取推荐方案)
      - [2. 性能预测](#2-性能预测)
      - [3. 方案对比](#3-方案对比)
      - [4. 代码生成](#4-代码生成)
  - [数据流](#数据流)
    - [推荐流程](#推荐流程)
  - [部署架构](#部署架构)
    - [开发环境](#开发环境)
    - [生产环境](#生产环境)
  - [开发计划](#开发计划)
    - [Phase 1: MVP (2周)](#phase-1-mvp-2周)
    - [Phase 2: 核心功能 (4周)](#phase-2-核心功能-4周)
    - [Phase 3: 优化 (2周)](#phase-3-优化-2周)

---

## 架构概述

### 系统定位

**并发控制决策助手**是一个Web应用 + CLI工具，帮助架构师和开发者快速选择合适的并发控制方案。

### 核心功能

1. **交互式问答**: 通过问答收集系统需求
2. **决策树引擎**: 基于决策树算法推荐方案
3. **性能预测**: 预测不同方案的性能表现
4. **代码生成**: 生成推荐方案的代码模板
5. **方案对比**: 对比多个方案的优缺点

---

## 系统架构

### 整体架构图

```text
┌─────────────────────────────────────────────────────────┐
│                    前端层 (Frontend)                      │
├─────────────────────────────────────────────────────────┤
│  React + TypeScript + Vite                               │
│  ├─ 交互式问答界面                                        │
│  ├─ 决策结果展示                                          │
│  ├─ 性能预测可视化                                        │
│  └─ 代码模板展示                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/REST API
                          │
┌─────────────────────────────────────────────────────────┐
│                    API网关层 (Gateway)                    │
├─────────────────────────────────────────────────────────┤
│  Axum (Rust) / Express (Node.js)                        │
│  ├─ 请求路由                                              │
│  ├─ 认证授权                                              │
│  ├─ 限流控制                                              │
│  └─ 日志记录                                              │
└─────────────────────────────────────────────────────────┘
                          │
                          │
┌─────────────────────────────────────────────────────────┐
│                   业务逻辑层 (Service)                    │
├─────────────────────────────────────────────────────────┤
│  Rust / Node.js                                          │
│  ├─ 决策树引擎 (Decision Engine)                         │
│  ├─ 性能预测器 (Performance Predictor)                   │
│  ├─ 代码生成器 (Code Generator)                          │
│  └─ 方案对比器 (Comparison Engine)                       │
└─────────────────────────────────────────────────────────┘
                          │
                          │
┌─────────────────────────────────────────────────────────┐
│                   数据层 (Data Layer)                    │
├─────────────────────────────────────────────────────────┤
│  ├─ 决策树规则库 (JSON/YAML)                             │
│  ├─ 性能基准数据 (SQLite/PostgreSQL)                     │
│  ├─ 代码模板库 (文件系统)                                 │
│  └─ 用户配置缓存 (Redis)                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 技术栈

### 前端技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI库**: Ant Design / Material-UI
- **状态管理**: Zustand / Redux Toolkit
- **路由**: React Router v6
- **图表**: Recharts / D3.js
- **代码高亮**: Prism.js / highlight.js

### 后端技术栈

**选项1: Rust (推荐)**:

- **Web框架**: Axum / Actix-web
- **异步运行时**: Tokio
- **数据库**: SQLx (PostgreSQL)
- **序列化**: Serde
- **配置**: Config

**选项2: Node.js**:

- **Web框架**: Express / Fastify
- **运行时**: Node.js 18+
- **数据库**: Prisma / TypeORM
- **类型**: TypeScript

### 数据存储

- **规则库**: JSON/YAML文件
- **性能数据**: PostgreSQL / SQLite
- **缓存**: Redis
- **文件存储**: 本地文件系统 / S3

---

## 模块设计

### 1. 决策树引擎 (Decision Engine)

**职责**: 根据输入需求，通过决策树算法推荐并发控制方案

**输入**:

```json
{
  "scenario": "seckill",
  "requirements": {
    "concurrent_users": 100000,
    "peak_qps": 50000,
    "consistency": "strong"
  },
  "workload": {
    "read_write_ratio": "1:10",
    "hot_spot": true
  }
}
```

**输出**:

```json
{
  "recommendation": {
    "isolation_level": "Read Committed",
    "concurrency_control": "Optimistic Locking",
    "caching": "Redis pre-decrement"
  },
  "rationale": [...],
  "alternatives": [...]
}
```

**实现**:

- 决策树规则定义（JSON/YAML）
- 规则匹配引擎
- 方案评分算法

### 2. 性能预测器 (Performance Predictor)

**职责**: 预测不同方案的性能表现

**输入**: 方案配置 + 系统配置

**输出**: TPS、延迟、资源使用预测

**实现**:

- 性能模型（基于基准测试数据）
- 机器学习模型（可选）
- 公式计算引擎

### 3. 代码生成器 (Code Generator)

**职责**: 生成推荐方案的代码模板

**输入**: 推荐方案

**输出**: 多语言代码模板（Rust、Java、Python等）

**实现**:

- 模板引擎（Handlebars / Jinja2）
- 代码模板库
- 语言特定格式化

### 4. 方案对比器 (Comparison Engine)

**职责**: 对比多个方案的优缺点

**输入**: 多个方案配置

**输出**: 对比矩阵、推荐理由

**实现**:

- 方案特征提取
- 对比算法
- 可视化数据生成

---

## API设计

### RESTful API

#### 1. 获取推荐方案

```http
POST /api/v1/recommend
Content-Type: application/json

{
  "scenario": {...},
  "requirements": {...},
  "workload": {...}
}

Response:
{
  "recommendation": {...},
  "predictions": {...},
  "rationale": [...]
}
```

#### 2. 性能预测

```http
POST /api/v1/predict
Content-Type: application/json

{
  "solution": {...},
  "infrastructure": {...}
}

Response:
{
  "tps": 55000,
  "avg_latency_ms": 18,
  "p99_latency_ms": 95,
  "confidence": 0.92
}
```

#### 3. 方案对比

```http
POST /api/v1/compare
Content-Type: application/json

{
  "solutions": [...]
}

Response:
{
  "comparison": [...],
  "recommendation": {...}
}
```

#### 4. 代码生成

```http
POST /api/v1/generate-code
Content-Type: application/json

{
  "solution": {...},
  "language": "rust"
}

Response:
{
  "code": "...",
  "language": "rust",
  "dependencies": [...]
}
```

---

## 数据流

### 推荐流程

```text
用户输入
  │
  ├─→ 需求解析
  │     │
  │     ├─→ 场景识别
  │     ├─→ 需求提取
  │     └─→ 约束分析
  │
  ├─→ 决策树引擎
  │     │
  │     ├─→ 规则匹配
  │     ├─→ 方案评分
  │     └─→ 方案排序
  │
  ├─→ 性能预测
  │     │
  │     ├─→ 模型预测
  │     └─→ 置信度计算
  │
  ├─→ 代码生成
  │     │
  │     └─→ 模板渲染
  │
  └─→ 结果返回
```

---

## 部署架构

### 开发环境

```text
Frontend (Vite Dev Server)
  │
  └─→ Backend (Local)
        │
        ├─→ SQLite (规则库)
        └─→ Redis (缓存)
```

### 生产环境

```text
CDN (静态资源)
  │
  └─→ Load Balancer
        │
        ├─→ Frontend Server 1
        ├─→ Frontend Server 2
        │
        └─→ API Gateway
              │
              ├─→ Backend Service 1
              ├─→ Backend Service 2
              │
              ├─→ PostgreSQL (性能数据)
              ├─→ Redis (缓存)
              └─→ S3 (代码模板)
```

---

## 开发计划

### Phase 1: MVP (2周)

- [x] 架构设计
- [ ] 前端框架搭建
- [ ] 后端API框架
- [ ] 决策树引擎基础实现
- [ ] 简单推荐功能

### Phase 2: 核心功能 (4周)

- [ ] 完整决策树规则
- [ ] 性能预测器
- [ ] 代码生成器
- [ ] 方案对比功能
- [ ] 前端完整UI

### Phase 3: 优化 (2周)

- [ ] 性能优化
- [ ] 用户体验优化
- [ ] 文档完善
- [ ] 测试覆盖

---

**文档版本**: 1.0.0
**最后更新**: 2025-12-05
**维护者**: PostgreSQL理论研究组
