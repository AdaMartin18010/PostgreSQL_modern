# 7.3.1 AWS Aurora PostgreSQL 方案

> **更新时间**: 2025 年 11 月 1 日  
> **文档编号**: 07-03-01

## 📑 目录

- [7.3.1 AWS Aurora PostgreSQL 方案](#731-aws-aurora-postgresql-方案)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 文档目标](#11-文档目标)
    - [1.2 Aurora 特性](#12-aurora-特性)
    - [1.3 集成价值](#13-集成价值)
  - [2. 核心特性](#2-核心特性)
    - [2.1 pgvector 支持](#21-pgvector-支持)
      - [2.1.1 原生支持](#211-原生支持)
      - [2.1.2 高可用性](#212-高可用性)
      - [2.1.3 自动扩展](#213-自动扩展)
    - [2.2 AI Auto-Tuning](#22-ai-auto-tuning)
      - [2.2.1 自动索引推荐](#221-自动索引推荐)
      - [2.2.2 性能优化](#222-性能优化)
      - [2.2.3 预测式缓存](#223-预测式缓存)
    - [2.3 Serverless](#23-serverless)
      - [2.3.1 按需扩展](#231-按需扩展)
      - [2.3.2 成本优化](#232-成本优化)
      - [2.3.3 快速启动](#233-快速启动)
  - [3. 架构设计](#3-架构设计)
    - [3.1 架构概述](#31-架构概述)
    - [3.2 组件说明](#32-组件说明)
    - [3.3 高可用设计](#33-高可用设计)
  - [4. 快速开始](#4-快速开始)
    - [4.1 创建 Aurora 集群](#41-创建-aurora-集群)
      - [4.1.1 使用 AWS CLI](#411-使用-aws-cli)
      - [4.1.2 使用 Terraform](#412-使用-terraform)
      - [4.1.3 使用 AWS Console](#413-使用-aws-console)
    - [4.2 启用 pgvector](#42-启用-pgvector)
    - [4.3 创建向量表](#43-创建向量表)
      - [4.3.1 基础表结构](#431-基础表结构)
      - [4.3.2 索引创建](#432-索引创建)
  - [5. AI Auto-Tuning](#5-ai-auto-tuning)
    - [5.1 启用 AI Auto-Tuning](#51-启用-ai-auto-tuning)
    - [5.2 使用自动索引推荐](#52-使用自动索引推荐)
    - [5.3 性能优化](#53-性能优化)
  - [6. 监控与告警](#6-监控与告警)
    - [6.1 CloudWatch 监控](#61-cloudwatch-监控)
      - [6.1.1 关键指标](#611-关键指标)
      - [6.1.2 自定义指标](#612-自定义指标)
    - [6.2 告警配置](#62-告警配置)
      - [6.2.1 基础告警](#621-基础告警)
      - [6.2.2 高级告警](#622-高级告警)
    - [6.3 Performance Insights](#63-performance-insights)
  - [7. 成本优化](#7-成本优化)
    - [7.1 Serverless 配置](#71-serverless-配置)
    - [7.2 只读副本](#72-只读副本)
    - [7.3 存储优化](#73-存储优化)
  - [8. 最佳实践](#8-最佳实践)
    - [8.1 架构最佳实践](#81-架构最佳实践)
    - [8.2 性能最佳实践](#82-性能最佳实践)
    - [8.3 安全最佳实践](#83-安全最佳实践)
  - [9. 常见问题](#9-常见问题)
    - [9.1 配置问题](#91-配置问题)
    - [9.2 性能问题](#92-性能问题)
    - [9.3 成本问题](#93-成本问题)
  - [10. 参考资料](#10-参考资料)
    - [10.1 官方文档](#101-官方文档)
    - [10.2 技术文档](#102-技术文档)
    - [10.3 相关资源](#103-相关资源)

---

## 1. 概述

### 1.1 文档目标

**核心目标**:

本文档提供 AWS Aurora PostgreSQL 与 pgvector 的集成方案，帮助用户快速构建基于云端的向量搜索应用。

**文档价值**:

| 价值项         | 说明                  | 影响           |
| -------------- | --------------------- | -------------- |
| **云原生方案** | 提供 AWS 云端解决方案 | 降低运维成本   |
| **高可用性**   | 自动故障转移和扩展    | 提高系统可靠性 |
| **成本优化**   | Serverless 和自动扩展 | 降低运营成本   |

### 1.2 Aurora 特性

**Aurora PostgreSQL 核心特性**:

| 特性               | 说明                           | 优势         |
| ------------------ | ------------------------------ | ------------ |
| **完全兼容**       | 100% PostgreSQL 兼容           | 无缝迁移     |
| **高可用**         | 自动故障转移，RPO=0，RTO<30 秒 | **高可靠性** |
| **自动扩展**       | 存储和计算自动扩展             | **弹性伸缩** |
| **Serverless**     | 按需扩展，无服务器管理         | **成本优化** |
| **AI Auto-Tuning** | 自动索引推荐和性能优化         | **智能优化** |

**版本支持**:

| Aurora 版本 | PostgreSQL 版本  | pgvector 支持 | 说明         |
| ----------- | ---------------- | ------------- | ------------ |
| **15.3+**   | PostgreSQL 15.3  | ✅ 支持       | **推荐版本** |
| **14.10+**  | PostgreSQL 14.10 | ✅ 支持       | 稳定版本     |
| **13.15+**  | PostgreSQL 13.15 | ⚠️ 部分支持   | 旧版本       |

### 1.3 集成价值

**集成优势**:

| 优势         | 说明                   | 影响               |
| ------------ | ---------------------- | ------------------ |
| **向量搜索** | pgvector 原生支持      | **高性能向量检索** |
| **高可用**   | 自动故障转移和多可用区 | **99.99% 可用性**  |
| **自动扩展** | 存储和计算自动扩展     | **弹性伸缩**       |
| **成本优化** | Serverless 按需付费    | **降低成本**       |

## 2. 核心特性

### 2.1 pgvector 支持

#### 2.1.1 原生支持

**pgvector 支持情况**:

- ✅ **Aurora PostgreSQL 15+**: 原生支持 pgvector
- ✅ **自动安装**: 扩展自动可用，无需手动编译
- ✅ **版本管理**: 自动更新和维护

**启用 pgvector**:

```sql
-- 连接到 Aurora 集群
psql -h aurora-pgvector.cluster-xxx.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d postgres

-- 启用 pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证
SELECT extname, extversion
FROM pg_extension
WHERE extname = 'vector';

-- 预期输出：
-- extname  | extversion
-- ---------+------------
-- vector   | 0.5.0
```

#### 2.1.2 高可用性

**高可用特性**:

| 特性             | 说明                 | 效果        |
| ---------------- | -------------------- | ----------- |
| **自动故障转移** | 主实例故障时自动切换 | RTO < 30 秒 |
| **多可用区**     | 跨可用区部署         | 高可用性    |
| **只读副本**     | 最多 15 个只读副本   | 读扩展      |
| **跨区域复制**   | 跨区域备份和恢复     | 灾难恢复    |

**高可用架构**:

```text
┌─────────────────────────────────────────┐
│     Primary Instance (us-east-1a)      │
│     - Write Operations                  │
│     - pgvector Extension                │
│     - AI Auto-Tuning                    │
└─────────────────────────────────────────┘
           │                    │
           │ Replication        │ Replication
           │                    │
┌──────────▼──────────┐  ┌──────▼──────────┐
│ Replica (us-east-1b)│  │ Replica (us-east-1c)│
│ - Read Operations   │  │ - Read Operations   │
└─────────────────────┘  └─────────────────────┘
```

#### 2.1.3 自动扩展

**自动扩展特性**:

| 扩展类型     | 说明                | 触发条件         |
| ------------ | ------------------- | ---------------- |
| **存储扩展** | 自动增加存储容量    | 存储使用率 > 90% |
| **计算扩展** | Serverless 自动扩展 | CPU/内存使用率   |
| **只读副本** | 自动添加只读副本    | 读负载增加       |

**Serverless 扩展配置**:

```bash
# Serverless v2 配置
aws rds modify-db-cluster \
  --db-cluster-identifier aurora-pgvector \
  --serverless-v2-scaling-configuration \
    MinCapacity=0.5,MaxCapacity=16
```

**扩展性能**:

| 指标         | 传统实例     | Serverless v2 |
| ------------ | ------------ | ------------- |
| **扩展时间** | 5-15 分钟    | **<60 秒**    |
| **最小容量** | 固定实例大小 | **0.5 ACU**   |
| **最大容量** | 固定实例大小 | **128 ACU**   |

### 2.2 AI Auto-Tuning

#### 2.2.1 自动索引推荐

**自动索引推荐特性**:

| 特性         | 说明                 | 效果         |
| ------------ | -------------------- | ------------ |
| **索引建议** | 基于查询模式推荐索引 | 提高查询性能 |
| **自动创建** | 自动创建推荐的索引   | 减少人工操作 |
| **性能监控** | 监控索引使用情况     | 优化索引策略 |

**启用自动索引推荐**:

```sql
-- 启用自动索引推荐
SELECT rds_autoindex.enable();

-- 查看索引建议
SELECT
    index_name,
    table_name,
    index_columns,
    estimated_improvement,
    sql_statement
FROM rds_autoindex.get_recommendations()
ORDER BY estimated_improvement DESC
LIMIT 10;

-- 自动创建推荐的索引
SELECT rds_autoindex.create_recommended_indexes();
```

**索引推荐示例**:

```sql
-- 示例：自动推荐的向量索引
CREATE INDEX documents_embedding_idx
ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 推荐理由：
-- - 查询模式：频繁使用 embedding <=> query_vector
-- - 预期性能提升：查询延迟降低 80%
-- - 存储成本：增加约 30%
```

#### 2.2.2 性能优化

**性能优化特性**:

| 特性             | 说明                 | 效果         |
| ---------------- | -------------------- | ------------ |
| **查询计划优化** | 自动优化查询执行计划 | 提高查询效率 |
| **连接池优化**   | 自动调整连接池大小   | 提高并发性能 |
| **缓存优化**     | 自动管理查询缓存     | 提高响应速度 |

**性能洞察**:

```sql
-- 查看性能洞察
SELECT
    query_id,
    query_text,
    total_exec_time,
    mean_exec_time,
    calls,
    (total_exec_time / NULLIF(calls, 0)) as avg_time_per_call
FROM rds_performance_insights.get_query_insights()
ORDER BY total_exec_time DESC
LIMIT 10;

-- 查看慢查询
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- 超过 1 秒的查询
ORDER BY mean_exec_time DESC
LIMIT 10;
```

#### 2.2.3 预测式缓存

**预测式缓存特性**:

| 特性             | 说明             | 效果           |
| ---------------- | ---------------- | -------------- |
| **热点数据识别** | 自动识别热点数据 | 提高缓存命中率 |
| **自动预热**     | 自动预热缓存     | 提高响应速度   |
| **缓存策略优化** | 自动优化缓存策略 | 提高缓存效率   |

### 2.3 Serverless

#### 2.3.1 按需扩展

**Serverless v2 特性**:

| 特性         | 说明             | 优势         |
| ------------ | ---------------- | ------------ |
| **自动扩展** | 根据负载自动扩展 | 无需人工干预 |
| **快速扩展** | <60 秒扩展时间   | **快速响应** |
| **容量范围** | 0.5 - 128 ACU    | **灵活配置** |

**Serverless 配置**:

```bash
# 创建 Serverless v2 集群
aws rds create-db-cluster \
  --db-cluster-identifier aurora-pgvector \
  --engine aurora-postgresql \
  --engine-version 15.3 \
  --master-username postgres \
  --master-user-password YourPassword \
  --serverless-v2-scaling-configuration \
    MinCapacity=0.5,MaxCapacity=16
```

#### 2.3.2 成本优化

**成本优化策略**:

| 策略           | 说明             | 节省成本         |
| -------------- | ---------------- | ---------------- |
| **Serverless** | 按实际使用量计费 | **最高 90%**     |
| **自动暂停**   | 无负载时自动暂停 | **空闲时零成本** |
| **容量优化**   | 根据负载调整容量 | **避免过度配置** |

**成本对比**:

| 场景                     | 传统实例 | Serverless v2 | 节省    |
| ------------------------ | -------- | ------------- | ------- |
| **开发环境**             | $150/月  | **$30/月**    | **80%** |
| **测试环境**             | $300/月  | **$80/月**    | **73%** |
| **生产环境（负载波动）** | $1000/月 | **$600/月**   | **40%** |

#### 2.3.3 快速启动

**快速启动特性**:

| 特性           | 说明           | 性能      |
| -------------- | -------------- | --------- |
| **冷启动时间** | 从暂停状态恢复 | **<5 秒** |
| **连接建立**   | 首次连接建立   | **<2 秒** |
| **查询响应**   | 第一个查询响应 | **<1 秒** |

## 3. 架构设计

### 3.1 架构概述

**架构图**:

```text
┌─────────────────────────────────────────────────┐
│         Application Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ EC2 App  │  │ Lambda   │  │ ECS Task │      │
│  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────┘
                      │
                      │ VPC
                      │
┌─────────────────────────────────────────────────┐
│         AWS Aurora PostgreSQL                   │
│  ┌──────────────────────────────────────────┐   │
│  │      Primary Instance                      │   │
│  │  - Write Operations                        │   │
│  │  - pgvector Extension                      │   │
│  │  - AI Auto-Tuning                         │   │
│  │  - Serverless v2 (0.5-16 ACU)             │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │      Replica Instances (2-15)            │   │
│  │  - Read Replicas                          │   │
│  │  - Cross-Region Replicas                 │   │
│  │  - Serverless v2 (0.5-16 ACU)             │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │      Aurora Storage (Auto Scaling)        │   │
│  │  - Automatic Storage Scaling (10GB-128TB) │   │
│  │  - Continuous Backup                      │   │
│  │  - Point-in-Time Recovery (35 days)       │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 3.2 组件说明

**核心组件**:

| 组件                  | 说明       | 作用           |
| --------------------- | ---------- | -------------- |
| **Primary Instance**  | 主实例     | 处理写入操作   |
| **Replica Instances** | 只读副本   | 处理读取操作   |
| **Aurora Storage**    | 存储层     | 自动扩展的存储 |
| **VPC**               | 虚拟私有云 | 网络隔离和安全 |

### 3.3 高可用设计

**高可用架构**:

```text
Region: us-east-1
├── AZ: us-east-1a
│   └── Primary Instance
├── AZ: us-east-1b
│   └── Replica Instance #1
├── AZ: us-east-1c
│   └── Replica Instance #2
└── Cross-Region: us-west-2
    └── Cross-Region Replica
```

**故障转移**:

| 故障类型       | 转移时间  | 数据损失 |
| -------------- | --------- | -------- |
| **主实例故障** | <30 秒    | **0**    |
| **可用区故障** | <60 秒    | **0**    |
| **区域故障**   | 5-15 分钟 | **0**    |

## 4. 快速开始

### 4.1 创建 Aurora 集群

#### 4.1.1 使用 AWS CLI

**AWS CLI 创建集群**:

```bash
# 创建 Aurora 集群
aws rds create-db-cluster \
  --db-cluster-identifier aurora-pgvector \
  --engine aurora-postgresql \
  --engine-version 15.3 \
  --master-username postgres \
  --master-user-password YourSecurePassword \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=16 \
  --database-name vector_db \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "mon:04:00-mon:05:00" \
  --enable-iam-database-authentication \
  --storage-encrypted

# 创建 Serverless v2 实例
aws rds create-db-instance \
  --db-instance-identifier aurora-pgvector-instance \
  --db-instance-class db.serverless \
  --engine aurora-postgresql \
  --db-cluster-identifier aurora-pgvector
```

#### 4.1.2 使用 Terraform

**Terraform 配置**:

```hcl
# main.tf
resource "aws_rds_cluster" "aurora_pgvector" {
  cluster_identifier      = "aurora-pgvector"
  engine                  = "aurora-postgresql"
  engine_version          = "15.3"
  database_name           = "vector_db"
  master_username         = "postgres"
  master_password         = var.db_password

  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 16
  }

  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  preferred_maintenance_window = "mon:04:00-mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql"]
  storage_encrypted = true
}

resource "aws_rds_cluster_instance" "aurora_pgvector_instance" {
  identifier         = "aurora-pgvector-instance"
  cluster_identifier = aws_rds_cluster.aurora_pgvector.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.aurora_pgvector.engine
  engine_version     = aws_rds_cluster.aurora_pgvector.engine_version
}
```

#### 4.1.3 使用 AWS Console

**AWS Console 创建步骤**:

1. 登录 AWS Console
2. 进入 RDS 服务
3. 创建数据库 → 选择 Aurora PostgreSQL
4. 配置：
   - Engine version: PostgreSQL 15.3
   - Capacity type: Serverless v2
   - Min ACU: 0.5
   - Max ACU: 16
5. 设置主用户名和密码
6. 配置网络和安全组
7. 启用备份和监控
8. 创建数据库

### 4.2 启用 pgvector

**启用 pgvector 扩展**:

```sql
-- 连接到 Aurora 集群
psql -h aurora-pgvector.cluster-xxx.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d vector_db

-- 启用 pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证扩展
SELECT
    extname,
    extversion,
    extrelocatable
FROM pg_extension
WHERE extname = 'vector';

-- 验证向量类型
SELECT typname, typlen
FROM pg_type
WHERE typname = 'vector';

-- 测试向量操作
SELECT '[1,2,3]'::vector(3) <=> '[1,2,3]'::vector(3) as distance;
-- 预期输出：0.0（完全相似）
```

### 4.3 创建向量表

#### 4.3.1 基础表结构

**创建向量表**:

```sql
-- 创建文档表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引（提升查询性能）
CREATE INDEX documents_content_idx ON documents USING gin(to_tsvector('english', content));
CREATE INDEX documents_metadata_idx ON documents USING gin(metadata);
CREATE INDEX documents_created_at_idx ON documents(created_at);

-- 添加更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

#### 4.3.2 索引创建

**创建向量索引**:

```sql
-- HNSW 索引（高精度，推荐用于 <100 万数据）
CREATE INDEX documents_embedding_hnsw_idx
ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,              -- 每层最大连接数
    ef_construction = 64  -- 构建时搜索范围
);

-- IVFFlat 索引（大规模数据，>100 万）
-- 注意：需要先导入足够的数据（至少 lists 数量的 10 倍）
CREATE INDEX documents_embedding_ivfflat_idx
ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (
    lists = 1000  -- 聚类数量，建议 = rows/1000
);
```

**索引选择建议**:

| 数据量          | 推荐索引       | 参数                     | 说明     |
| --------------- | -------------- | ------------------------ | -------- |
| **<100 万**     | HNSW           | m=16, ef_construction=64 | 高精度   |
| **100-1000 万** | IVFFlat        | lists=1000               | 高性能   |
| **>1000 万**    | IVFFlat + 分区 | lists=分区数据量/1000    | 超大规模 |

## 5. AI Auto-Tuning

### 5.1 启用 AI Auto-Tuning

**启用步骤**:

```sql
-- 1. 启用自动索引推荐
SELECT rds_autoindex.enable();

-- 验证启用状态
SELECT rds_autoindex.is_enabled();

-- 预期输出：t（已启用）
```

### 5.2 使用自动索引推荐

**查看索引建议**:

```sql
-- 查看所有索引建议
SELECT
    index_name,
    table_name,
    index_columns,
    index_type,
    estimated_improvement,
    sql_statement,
    created_at
FROM rds_autoindex.get_recommendations()
ORDER BY estimated_improvement DESC;

-- 示例输出：
-- index_name              | table_name | index_columns        | estimated_improvement
-- ------------------------|------------|---------------------|-----------------------
-- documents_embedding_idx | documents  | embedding           | 80%
-- documents_content_idx   | documents  | content             | 60%
```

**自动创建索引**:

```sql
-- 自动创建所有推荐的索引
SELECT rds_autoindex.create_recommended_indexes();

-- 或者只创建特定索引
SELECT rds_autoindex.create_recommended_index('documents_embedding_idx');

-- 查看创建的索引
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'documents';
```

### 5.3 性能优化

**性能优化查询**:

```sql
-- 查看性能洞察
SELECT
    query_id,
    query_text,
    total_exec_time,
    mean_exec_time,
    calls,
    rows,
    shared_blks_hit,
    shared_blks_read,
    (shared_blks_hit::float / NULLIF(shared_blks_hit + shared_blks_read, 0)) * 100 as cache_hit_rate
FROM rds_performance_insights.get_query_insights()
WHERE mean_exec_time > 100  -- 超过 100ms 的查询
ORDER BY total_exec_time DESC
LIMIT 20;

-- 查看慢查询
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time,
    total_exec_time,
    (shared_blks_hit::float / NULLIF(shared_blks_hit + shared_blks_read, 0)) * 100 as cache_hit_rate
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- 超过 1 秒的查询
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## 6. 监控与告警

### 6.1 CloudWatch 监控

#### 6.1.1 关键指标

**关键监控指标**:

| 指标                    | 说明         | 阈值                 | 告警级别 |
| ----------------------- | ------------ | -------------------- | -------- |
| **CPUUtilization**      | CPU 使用率   | >80%                 | 警告     |
| **DatabaseConnections** | 数据库连接数 | >80% max_connections | 警告     |
| **FreeableMemory**      | 可用内存     | <20%                 | 严重     |
| **WriteIOPS**           | 写入 IOPS    | >80% IOPS 限制       | 警告     |
| **ReadLatency**         | 读取延迟     | >100ms               | 警告     |

**CloudWatch 监控代码**:

```python
import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch')

# 获取 CPU 使用率
response = cloudwatch.get_metric_statistics(
    Namespace='AWS/RDS',
    MetricName='CPUUtilization',
    Dimensions=[
        {'Name': 'DBClusterIdentifier', 'Value': 'aurora-pgvector'}
    ],
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow(),
    Period=300,  # 5 分钟
    Statistics=['Average', 'Maximum']
)

for datapoint in response['Datapoints']:
    print(f"时间: {datapoint['Timestamp']}")
    print(f"平均 CPU: {datapoint['Average']:.2f}%")
    print(f"最大 CPU: {datapoint['Maximum']:.2f}%")
```

#### 6.1.2 自定义指标

**自定义指标示例**:

```python
# 发送自定义指标
cloudwatch.put_metric_data(
    Namespace='VectorSearch/Custom',
    MetricData=[
        {
            'MetricName': 'VectorSearchLatency',
            'Value': 50.0,  # 毫秒
            'Unit': 'Milliseconds',
            'Dimensions': [
                {'Name': 'ClusterId', 'Value': 'aurora-pgvector'},
                {'Name': 'IndexType', 'Value': 'HNSW'}
            ]
        },
        {
            'MetricName': 'VectorSearchQueries',
            'Value': 1000,
            'Unit': 'Count',
            'Dimensions': [
                {'Name': 'ClusterId', 'Value': 'aurora-pgvector'}
            ]
        }
    ]
)
```

### 6.2 告警配置

#### 6.2.1 基础告警

**创建基础告警**:

```bash
# CPU 使用率告警
aws cloudwatch put-metric-alarm \
  --alarm-name aurora-pgvector-cpu-high \
  --alarm-description "Aurora CPU utilization is high" \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=DBClusterIdentifier,Value=aurora-pgvector \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts

# 连接数告警
aws cloudwatch put-metric-alarm \
  --alarm-name aurora-pgvector-connections-high \
  --alarm-description "Aurora database connections are high" \
  --metric-name DatabaseConnections \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=DBClusterIdentifier,Value=aurora-pgvector \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

#### 6.2.2 高级告警

**高级告警配置（Terraform）**:

```hcl
# CloudWatch 告警
resource "aws_cloudwatch_metric_alarm" "aurora_cpu_high" {
  alarm_name          = "aurora-pgvector-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Aurora CPU utilization is high"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBClusterIdentifier = aws_rds_cluster.aurora_pgvector.id
  }
}
```

### 6.3 Performance Insights

**启用 Performance Insights**:

```bash
# 启用 Performance Insights
aws rds modify-db-instance \
  --db-instance-identifier aurora-pgvector-instance \
  --enable-performance-insights \
  --performance-insights-retention-period 7
```

**查询性能数据**:

```sql
-- 查看性能洞察数据
SELECT
    pid,
    usename,
    datname,
    application_name,
    state,
    query_start,
    state_change,
    wait_event_type,
    wait_event,
    LEFT(query, 100) as query_preview
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;
```

## 7. 成本优化

### 7.1 Serverless 配置

**Serverless 成本优化**:

```bash
# 优化 Serverless 配置（开发/测试环境）
aws rds modify-db-cluster \
  --db-cluster-identifier aurora-pgvector \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=4

# 生产环境配置
aws rds modify-db-cluster \
  --db-cluster-identifier aurora-pgvector \
  --serverless-v2-scaling-configuration MinCapacity=2,MaxCapacity=16
```

**成本对比表**:

| 环境     | Min ACU | Max ACU | 月成本 | 说明     |
| -------- | ------- | ------- | ------ | -------- |
| **开发** | 0.5     | 2       | ~$30   | 低负载   |
| **测试** | 1       | 4       | ~$80   | 中等负载 |
| **生产** | 2       | 16      | ~$400  | 高负载   |

### 7.2 只读副本

**只读副本配置**:

```bash
# 创建只读副本（用于查询）
aws rds create-db-instance \
  --db-instance-identifier aurora-pgvector-replica-1 \
  --db-instance-class db.serverless \
  --engine aurora-postgresql \
  --db-cluster-identifier aurora-pgvector \
  --publicly-accessible false
```

**只读副本优势**:

| 优势         | 说明       | 效果             |
| ------------ | ---------- | ---------------- |
| **读扩展**   | 分担读负载 | 提高查询性能     |
| **地理分布** | 跨区域部署 | 降低延迟         |
| **成本优化** | 读写分离   | 主实例可配置较小 |

### 7.3 存储优化

**存储优化策略**:

| 策略           | 说明             | 节省成本     |
| -------------- | ---------------- | ------------ |
| **自动扩展**   | 按需扩展存储     | 避免预分配   |
| **压缩备份**   | 启用备份压缩     | 减少存储成本 |
| **清理旧数据** | 定期清理过期数据 | 减少存储使用 |

## 8. 最佳实践

### 8.1 架构最佳实践

**架构建议**:

1. **多可用区部署**: 提高可用性
2. **只读副本**: 分担读负载
3. **Serverless v2**: 灵活扩展
4. **自动备份**: 启用持续备份

### 8.2 性能最佳实践

**性能优化建议**:

1. **索引优化**: 使用 AI Auto-Tuning 自动优化
2. **连接池**: 使用连接池管理连接
3. **查询优化**: 使用 Performance Insights 优化慢查询
4. **只读副本**: 将读查询路由到只读副本

### 8.3 安全最佳实践

**安全建议**:

1. **网络隔离**: 使用 VPC 和安全组
2. **加密**: 启用存储加密和传输加密
3. **IAM 认证**: 使用 IAM 数据库认证
4. **审计日志**: 启用 CloudWatch 日志导出

## 9. 常见问题

### 9.1 配置问题

**常见配置问题**:

1. **pgvector 扩展未找到**: 确保使用 Aurora PostgreSQL 15+
2. **Serverless 无法扩展**: 检查 MinCapacity 和 MaxCapacity 配置
3. **连接超时**: 检查安全组和网络配置

### 9.2 性能问题

**性能问题排查**:

1. **查询慢**: 检查索引是否创建，使用 Performance Insights
2. **CPU 高**: 使用只读副本分担负载
3. **存储不足**: 启用自动扩展

### 9.3 成本问题

**成本优化建议**:

1. **开发环境**: 使用较小的 Serverless 配置
2. **自动暂停**: 开发环境启用自动暂停
3. **只读副本**: 合理配置只读副本数量

## 10. 参考资料

### 10.1 官方文档

- [Aurora PostgreSQL 文档](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.PostgreSQL.html) -
  Aurora PostgreSQL Guide
- [pgvector on Aurora](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.PostgreSQL.Extensions.html) -
  pgvector Extension

### 10.2 技术文档

- [AWS Aurora Serverless](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless.html) -
  Aurora Serverless Guide
- [AI Auto-Tuning](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-auto-indexing.html) -
  Auto Indexing

### 10.3 相关资源

- [AWS Performance Insights](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.html) -
  Performance Insights
- [AWS CloudWatch](https://docs.aws.amazon.com/cloudwatch/) - CloudWatch Documentation

---

**最后更新**: 2025 年 11 月 1 日  
**维护者**: PostgreSQL Modern Team  
**文档编号**: 07-03-01
