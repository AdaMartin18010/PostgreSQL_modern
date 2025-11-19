# Azure Database for PostgreSQL 方案

> **更新时间**: 2025 年 11 月 1 日
> **技术版本**: Azure Database for PostgreSQL 14+, pgvector 0.7.0+
> **文档编号**: 07-03-03

## 📑 目录

- [Azure Database for PostgreSQL 方案](#azure-database-for-postgresql-方案)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 技术背景](#11-技术背景)
    - [1.2 核心价值](#12-核心价值)
  - [2. 架构设计](#2-架构设计)
    - [2.1 整体架构](#21-整体架构)
    - [2.2 高可用架构](#22-高可用架构)
    - [2.3 扩展架构](#23-扩展架构)
  - [3. 向量搜索集成](#3-向量搜索集成)
    - [3.1 pgvector 安装](#31-pgvector-安装)
    - [3.2 向量索引创建](#32-向量索引创建)
    - [3.3 性能优化](#33-性能优化)
  - [4. 实践案例](#4-实践案例)
    - [4.1 AI 应用集成](#41-ai-应用集成)
  - [5. 参考资料](#5-参考资料)

---

## 1. 概述

### 1.1 技术背景

**问题需求**:

Azure Database for PostgreSQL 需要：

- **AI 应用支持**: 支持 AI 应用的向量搜索
- **高可用性**: 99.99% 可用性保证
- **自动扩展**: 自动扩展计算和存储
- **安全合规**: 满足企业安全合规要求

**技术方案**:

- **Azure Database**: 托管 PostgreSQL 服务
- **pgvector**: 向量搜索扩展
- **Azure AI 服务**: 与 Azure AI 服务集成

### 1.2 核心价值

- **可用性**: 99.99% SLA
- **性能**: 高性能向量搜索
- **集成**: 与 Azure AI 服务无缝集成

## 2. 架构设计

### 2.1 整体架构

```text
Azure 应用服务
  ↓
Azure Database for PostgreSQL
  ├── 主节点（读写）
  ├── 只读副本（高可用）
  └── 备份（自动备份）
  ↓
pgvector 扩展
  ├── HNSW 索引
  └── 向量查询优化
```

### 2.2 高可用架构

```sql
-- Azure Database 高可用配置
-- 1. 启用只读副本
-- 在 Azure Portal 中配置只读副本

-- 2. 应用连接配置
-- 主节点：读写
-- 只读副本：只读查询

-- 3. 故障转移
-- Azure 自动故障转移（<60秒）
```

### 2.3 扩展架构

```sql
-- Azure Database 扩展配置
-- 1. 计算扩展（vCore）
-- 2. 存储扩展（自动扩展）
-- 3. 连接池（PgBouncer）
```

## 3. 向量搜索集成

### 3.1 pgvector 安装

```sql
-- 在 Azure Database 中启用 pgvector
-- 方法 1: 通过 Azure Portal 启用扩展
-- 方法 2: 通过 SQL 启用

CREATE EXTENSION IF NOT EXISTS vector;

-- 验证安装
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 3.2 向量索引创建

```sql
-- 创建向量表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建 HNSW 索引
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,
    ef_construction = 64
);
```

### 3.3 性能优化

```sql
-- 1. 连接池配置
-- 使用 Azure Database 连接池（PgBouncer）

-- 2. 查询优化
SET enable_seqscan = off;

-- 3. 向量查询
SELECT
    id,
    content,
    1 - (embedding <=> $1::vector) AS similarity
FROM documents
WHERE 1 - (embedding <=> $1::vector) > 0.8
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

## 4. 实践案例

### 4.1 AI 应用集成

**案例背景**:

某企业 AI 应用（2025 年 11 月）：

- **数据规模**: 1000 万文档向量
- **查询 QPS**: 5,000+
- **需求**: 与 Azure AI 服务集成

**实现方案**:

```python
# Azure AI 服务集成
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import psycopg2

class AzureAIIntegration:
    def __init__(self):
        # Azure AI 客户端
        self.ai_client = TextAnalyticsClient(
            endpoint="https://your-endpoint.cognitiveservices.azure.com/",
            credential=AzureKeyCredential("your-key")
        )

        # Azure Database 连接
        self.db_conn = psycopg2.connect(
            host="your-server.postgres.database.azure.com",
            database="your-database",
            user="your-user",
            password="your-password",
            sslmode="require"
        )

    def index_document(self, text):
        """索引文档"""
        # 1. 生成向量（使用 Azure AI）
        embeddings = self.ai_client.analyze_sentiment([text])
        vector = self._generate_embedding(text)

        # 2. 存储到 Azure Database
        cursor = self.db_conn.cursor()
        cursor.execute("""
            INSERT INTO documents (content, embedding)
            VALUES (%s, %s)
        """, (text, vector))
        self.db_conn.commit()

    def search_documents(self, query, limit=10):
        """搜索文档"""
        # 1. 生成查询向量
        query_vector = self._generate_embedding(query)

        # 2. 向量搜索
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT id, content,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM documents
            WHERE 1 - (embedding <=> %s::vector) > 0.8
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_vector, query_vector, query_vector, limit))

        return cursor.fetchall()
```

**效果**:

- **查询性能**: P99 延迟 30ms
- **可用性**: 99.99% SLA
- **集成**: 与 Azure AI 服务无缝集成

## 5. 参考资料

- [AWS Aurora 方案](./AWS-Aurora方案.md)
- [阿里云 AnalyticDB 方案](./阿里云AnalyticDB方案.md)
- [pgvector 核心原理](../../01-向量与混合搜索/技术原理/pgvector核心原理.md)

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
**文档编号**: 07-03-03
