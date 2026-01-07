---

> **📋 文档来源**: `PostgreSQL_View\02-AI自治与自优化\配置示例\pg_ai安装配置.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# pg_ai 安装配置指南

> **更新时间**: 2025 年 1 月
> **技术版本**: pg_ai 1.0+, PostgreSQL 16+
> **文档编号**: 02-04-01

## 📑 目录

- [pg\_ai 安装配置指南](#pg_ai-安装配置指南)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. 安装步骤](#2-安装步骤)
    - [2.1 环境要求](#21-环境要求)
    - [2.2 编译安装](#22-编译安装)
    - [2.3 Docker 安装](#23-docker-安装)
  - [3. 基础配置](#3-基础配置)
    - [3.1 启用扩展](#31-启用扩展)
    - [3.2 基础参数配置](#32-基础参数配置)
  - [4. 训练配置](#4-训练配置)
    - [4.1 训练参数配置](#41-训练参数配置)
    - [4.2 训练数据准备](#42-训练数据准备)
  - [5. 生产环境配置](#5-生产环境配置)
    - [5.1 生产环境参数](#51-生产环境参数)
    - [5.2 监控配置](#52-监控配置)
  - [6. 配置文件示例](#6-配置文件示例)
    - [6.1 完整配置文件](#61-完整配置文件)
    - [6.2 Docker Compose 完整配置](#62-docker-compose-完整配置)
  - [7. 验证和测试](#7-验证和测试)
    - [7.1 验证安装](#71-验证安装)
    - [7.2 测试查询优化](#72-测试查询优化)
  - [8. 参考资料](#8-参考资料)

---

## 1. 概述

**pg_ai** 是 PostgreSQL 的 AI 自治优化插件，提供：

- **自动查询优化**: 基于强化学习的查询计划优化
- **自动索引推荐**: 智能索引推荐和管理
- **自动参数调优**: 自动调整数据库参数

**本文档提供**:

- 完整的安装步骤
- 详细的配置示例
- 生产环境最佳实践

---

## 2. 安装步骤

### 2.1 环境要求

**系统要求**:

- **PostgreSQL**: 16.0+
- **操作系统**: Linux (Ubuntu 20.04+, CentOS 8+)
- **Python**: 3.8+ (用于训练脚本)
- **内存**: 至少 4GB RAM
- **磁盘**: 至少 10GB 可用空间

**依赖包**:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    postgresql-server-dev-16 \
    build-essential \
    git \
    python3-dev \
    python3-pip

# CentOS/RHEL
sudo yum install -y \
    postgresql16-devel \
    gcc \
    gcc-c++ \
    git \
    python3-devel \
    python3-pip
```

### 2.2 编译安装

**步骤 1: 克隆仓库**:

```bash
# 克隆 pg_ai 仓库
git clone https://github.com/pg_ai/pg_ai.git
cd pg_ai
```

**步骤 2: 编译扩展**:

```bash
# 编译扩展
make

# 安装扩展
sudo make install

# 验证安装
ls -la $(pg_config --sharedir)/extension/pg_ai*
```

**步骤 3: 安装 Python 依赖**:

```bash
# 安装训练依赖
pip3 install -r requirements.txt

# 安装 PyTorch (用于强化学习模型)
pip3 install torch torchvision torchaudio
```

### 2.3 Docker 安装

**Docker Compose 配置**:

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres-ai:
    image: postgres:16
    container_name: postgres-ai
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ai_db
    ports:
      - "5432:5432"
    volumes:
      - ./pg_ai:/usr/local/share/postgresql/extension/pg_ai
      - postgres_data:/var/lib/postgresql/data
    command:
      - "postgres"
      - "-c"
      - "shared_preload_libraries=pg_ai"
      - "-c"
      - "pg_ai.enabled=on"
```

---

## 3. 基础配置

### 3.1 启用扩展

**SQL 配置**:

```sql
-- 连接到数据库
\c your_database

-- 启用 pg_ai 扩展
CREATE EXTENSION IF NOT EXISTS pg_ai;

-- 验证扩展
SELECT * FROM pg_extension WHERE extname = 'pg_ai';
```

### 3.2 基础参数配置

**postgresql.conf 配置**:

```conf
# pg_ai 基础配置
shared_preload_libraries = 'pg_ai'

# 启用 AI 优化器
pg_ai.enabled = on

# 优化器模式
# - 'auto': 自动选择（推荐）
# - 'ml': 仅使用机器学习优化器
# - 'traditional': 仅使用传统优化器
pg_ai.optimizer_mode = 'auto'

# 模型路径
pg_ai.model_path = '/var/lib/postgresql/pg_ai/models'

# 训练数据路径
pg_ai.training_data_path = '/var/lib/postgresql/pg_ai/training'
```

---

## 4. 训练配置

### 4.1 训练参数配置

**训练配置文件** (`training_config.json`):

```json
{
  "model": {
    "type": "dqn",
    "state_dim": 128,
    "action_dim": 64,
    "hidden_layers": [256, 128, 64],
    "learning_rate": 0.001,
    "gamma": 0.99,
    "epsilon_start": 1.0,
    "epsilon_end": 0.01,
    "epsilon_decay": 0.995
  },
  "training": {
    "batch_size": 32,
    "replay_buffer_size": 10000,
    "update_frequency": 100,
    "target_update_frequency": 1000,
    "max_episodes": 10000,
    "max_steps_per_episode": 1000
  },
  "data": {
    "query_log_path": "/var/lib/postgresql/pg_ai/logs/queries.log",
    "training_ratio": 0.8,
    "validation_ratio": 0.1,
    "test_ratio": 0.1
  },
  "optimization": {
    "enable_index_recommendation": true,
    "enable_parameter_tuning": true,
    "enable_query_optimization": true
  }
}
```

### 4.2 训练数据准备

**收集训练数据**:

```sql
-- 启用查询日志
SET pg_ai.query_logging = on;

-- 运行典型工作负载
-- ... 执行查询 ...

-- 导出训练数据
SELECT pg_ai.export_training_data('/var/lib/postgresql/pg_ai/training/data.csv');
```

**训练脚本** (`train_model.py`):

```python
#!/usr/bin/env python3
"""pg_ai 模型训练脚本"""

import json
import torch
from pg_ai.trainer import DQNTrainer
from pg_ai.data_loader import QueryDataLoader

# 加载配置
with open('training_config.json', 'r') as f:
    config = json.load(f)

# 初始化数据加载器
data_loader = QueryDataLoader(
    query_log_path=config['data']['query_log_path'],
    training_ratio=config['data']['training_ratio'],
    validation_ratio=config['data']['validation_ratio'],
    test_ratio=config['data']['test_ratio']
)

# 初始化训练器
trainer = DQNTrainer(
    state_dim=config['model']['state_dim'],
    action_dim=config['model']['action_dim'],
    hidden_layers=config['model']['hidden_layers'],
    learning_rate=config['model']['learning_rate'],
    gamma=config['model']['gamma']
)

# 训练模型
trainer.train(
    data_loader=data_loader,
    max_episodes=config['training']['max_episodes'],
    batch_size=config['training']['batch_size'],
    replay_buffer_size=config['training']['replay_buffer_size']
)

# 保存模型
trainer.save_model(config['model']['save_path'])
print("模型训练完成！")
```

---

## 5. 生产环境配置

### 5.1 生产环境参数

**postgresql.conf (生产环境)**:

```conf
# pg_ai 生产环境配置
shared_preload_libraries = 'pg_ai'

# 启用 AI 优化器
pg_ai.enabled = on

# 优化器模式：自动选择
pg_ai.optimizer_mode = 'auto'

# 模型配置
pg_ai.model_path = '/var/lib/postgresql/pg_ai/models/production'
pg_ai.model_update_frequency = 'weekly'  # 每周更新模型

# 训练配置
pg_ai.training.enabled = on
pg_ai.training.frequency = 'daily'  # 每天增量训练
pg_ai.training.data_retention_days = 90  # 保留 90 天数据

# 索引推荐配置
pg_ai.index_recommendation.enabled = on
pg_ai.index_recommendation.auto_create = off  # 生产环境建议手动审核
pg_ai.index_recommendation.recommendation_threshold = 0.8

# 参数调优配置
pg_ai.parameter_tuning.enabled = on
pg_ai.parameter_tuning.auto_apply = off  # 生产环境建议手动审核
pg_ai.parameter_tuning.safety_margin = 0.1  # 10% 安全边际

# 性能监控
pg_ai.monitoring.enabled = on
pg_ai.monitoring.metrics_collection_interval = 60  # 60 秒收集一次
pg_ai.monitoring.alert_threshold = 0.2  # 性能下降 20% 时告警
```

### 5.2 监控配置

**监控脚本** (`monitor_pg_ai.sh`):

```bash
#!/bin/bash
# pg_ai 监控脚本

DB_NAME="your_database"
DB_USER="postgres"

# 检查模型状态
psql -U $DB_USER -d $DB_NAME -c "
SELECT
    model_name,
    model_version,
    last_update_time,
    performance_improvement,
    status
FROM pg_ai.model_status;
"

# 检查训练状态
psql -U $DB_USER -d $DB_NAME -c "
SELECT
    training_id,
    start_time,
    end_time,
    status,
    performance_improvement
FROM pg_ai.training_history
ORDER BY start_time DESC
LIMIT 10;
"

# 检查索引推荐
psql -U $DB_USER -d $DB_NAME -c "
SELECT
    table_name,
    index_name,
    recommendation_score,
    expected_improvement,
    status
FROM pg_ai.index_recommendations
WHERE status = 'pending'
ORDER BY recommendation_score DESC;
"
```

---

## 6. 配置文件示例

### 6.1 完整配置文件

**postgresql.conf (完整示例)**:

```conf
# ============================================
# PostgreSQL 基础配置
# ============================================
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 128MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB

# ============================================
# pg_ai 配置
# ============================================
shared_preload_libraries = 'pg_ai'

# 基础配置
pg_ai.enabled = on
pg_ai.optimizer_mode = 'auto'
pg_ai.model_path = '/var/lib/postgresql/pg_ai/models'
pg_ai.training_data_path = '/var/lib/postgresql/pg_ai/training'

# 训练配置
pg_ai.training.enabled = on
pg_ai.training.frequency = 'daily'
pg_ai.training.data_retention_days = 90
pg_ai.training.batch_size = 32
pg_ai.training.learning_rate = 0.001

# 索引推荐配置
pg_ai.index_recommendation.enabled = on
pg_ai.index_recommendation.auto_create = off
pg_ai.index_recommendation.recommendation_threshold = 0.8

# 参数调优配置
pg_ai.parameter_tuning.enabled = on
pg_ai.parameter_tuning.auto_apply = off
pg_ai.parameter_tuning.safety_margin = 0.1

# 监控配置
pg_ai.monitoring.enabled = on
pg_ai.monitoring.metrics_collection_interval = 60
pg_ai.monitoring.alert_threshold = 0.2
```

### 6.2 Docker Compose 完整配置

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  postgres-ai:
    image: postgres:16
    container_name: postgres-ai
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ai_db
      POSTGRES_USER: postgres
    ports:
      - "5432:5432"
    volumes:
      - ./pg_ai:/usr/local/share/postgresql/extension/pg_ai
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
      - ./training_config.json:/etc/postgresql/training_config.json
      - postgres_data:/var/lib/postgresql/data
      - pg_ai_models:/var/lib/postgresql/pg_ai/models
      - pg_ai_training:/var/lib/postgresql/pg_ai/training
    command:
      - "postgres"
      - "-c"
      - "config_file=/etc/postgresql/postgresql.conf"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d ai_db"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
  pg_ai_models:
  pg_ai_training:
```

---

## 7. 验证和测试

### 7.1 验证安装

```sql
-- 检查扩展是否启用
SELECT * FROM pg_extension WHERE extname = 'pg_ai';

-- 检查配置
SHOW pg_ai.enabled;
SHOW pg_ai.optimizer_mode;

-- 检查模型状态
SELECT * FROM pg_ai.model_status;
```

### 7.2 测试查询优化

```sql
-- 启用查询计划显示
SET pg_ai.show_plans = on;

-- 执行测试查询
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM large_table
WHERE column1 = 'value'
ORDER BY column2
LIMIT 100;

-- 查看优化器选择
SELECT * FROM pg_ai.query_plans
ORDER BY created_at DESC
LIMIT 10;
```

---

## 8. 参考资料

- [pg_ai 官方文档](https://github.com/pg_ai/pg_ai)
- [PostgreSQL 配置文档](https://www.postgresql.org/docs/current/config-setting.html)
- [强化学习优化器研究论文](https://arxiv.org/abs/1808.03196)

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
**文档编号**: 02-04-01
