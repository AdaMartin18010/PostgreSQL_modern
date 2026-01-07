---

> **📋 文档来源**: `PostgreSQL培训\14-AI与机器学习\【深入】LangChain+PostgreSQL完整集成指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# LangChain + PostgreSQL 完整集成指南

> **创建时间**: 2025 年 12 月 4 日
> **技术版本**: LangChain 0.1.0+ with PostgreSQL 18+ and pgvector
> **文档编号**: 14-AI-LANGCHAIN

---

## 📑 目录

- [LangChain + PostgreSQL 完整集成指南](#langchain--postgresql-完整集成指南)
  - [📑 目录](#-目录)
  - [一、概述](#一概述)
    - [1.1 什么是 LangChain](#11-什么是-langchain)
    - [1.2 为什么选择 PostgreSQL](#12-为什么选择-postgresql)
    - [1.3 核心价值](#13-核心价值)
    - [1.4 知识体系思维导图](#14-知识体系思维导图)
  - [二、原理与理论](#二原理与理论)
    - [2.1 LangChain 架构原理](#21-langchain-架构原理)
      - [**核心组件详解**](#核心组件详解)
      - [**LCEL (LangChain Expression Language)**](#lcel-langchain-expression-language)
    - [2.2 RAG 检索增强生成](#22-rag-检索增强生成)
      - [**RAG 工作原理**](#rag-工作原理)
      - [**关键技术点**](#关键技术点)
    - [2.3 向量嵌入与相似度搜索](#23-向量嵌入与相似度搜索)
      - [**嵌入模型选择**](#嵌入模型选择)
      - [**相似度计算**](#相似度计算)
      - [**索引优化**](#索引优化)
    - [2.4 上下文管理与优化](#24-上下文管理与优化)
      - [**上下文窗口限制**](#上下文窗口限制)
      - [**上下文压缩**](#上下文压缩)
  - [三、架构设计](#三架构设计)
    - [3.1 整体架构](#31-整体架构)
    - [3.2 向量存储集成](#32-向量存储集成)
    - [3.3 检索器设计](#33-检索器设计)
    - [3.4 链式调用优化](#34-链式调用优化)
  - [四、程序设计](#四程序设计)
    - [4.1 环境准备](#41-环境准备)
      - [**依赖安装**](#依赖安装)
      - [**PostgreSQL配置**](#postgresql配置)
      - [**环境变量配置**](#环境变量配置)
    - [4.2 向量存储配置](#42-向量存储配置)
    - [4.3 文档处理与加载](#43-文档处理与加载)
    - [4.4 RAG 应用开发](#44-rag-应用开发)
    - [4.5 高级特性](#45-高级特性)
      - [**Agent开发**](#agent开发)
      - [**Memory管理**](#memory管理)
  - [五、运维管理](#五运维管理)
    - [5.1 性能优化](#51-性能优化)
    - [5.2 监控告警](#52-监控告警)
    - [5.3 成本优化](#53-成本优化)
    - [5.4 最佳实践](#54-最佳实践)
  - [六、案例实战](#六案例实战)
    - [6.1 企业知识库问答](#61-企业知识库问答)
    - [6.2 文档智能摘要](#62-文档智能摘要)
    - [6.3 代码助手](#63-代码助手)
    - [6.4 客服机器人](#64-客服机器人)
  - [七、性能测试](#七性能测试)
  - [八、总结与展望](#八总结与展望)
    - [核心收获](#核心收获)
    - [适用场景](#适用场景)
  - [九、参考资料](#九参考资料)

---

## 一、概述

### 1.1 什么是 LangChain

**LangChain** 是一个用于开发基于大语言模型（LLM）应用的框架，提供了：

- 🔗 **链式调用**：将多个组件组合成复杂的应用
- 📚 **文档加载器**：支持多种格式的文档加载
- 🔍 **向量存储**：集成多种向量数据库
- 🤖 **Agent**：构建自主决策的AI代理
- 💬 **记忆管理**：维护对话上下文

**核心组件**：

```text
┌─────────────────────────────────────────┐
│         LangChain 核心架构              │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────┐    ┌─────────┐           │
│  │ Models  │    │ Prompts │           │
│  └─────────┘    └─────────┘           │
│       │              │                  │
│       ▼              ▼                  │
│  ┌─────────────────────────┐          │
│  │      Chains             │          │
│  └─────────────────────────┘          │
│       │                                 │
│       ▼                                 │
│  ┌─────────┐    ┌──────────┐         │
│  │ Memory  │    │ Retrievers│         │
│  └─────────┘    └──────────┘         │
│       │              │                  │
│       ▼              ▼                  │
│  ┌─────────────────────────┐          │
│  │      Agents             │          │
│  └─────────────────────────┘          │
└─────────────────────────────────────────┘
```

### 1.2 为什么选择 PostgreSQL

**PostgreSQL + pgvector 作为向量存储的优势**：

| 特性 | PostgreSQL + pgvector | 专用向量数据库 |
|------|----------------------|---------------|
| **数据一致性** | ✅ ACID 事务支持 | ⚠️ 最终一致性 |
| **混合查询** | ✅ 向量 + 关系型 | ❌ 仅向量查询 |
| **运维成本** | ✅ 统一基础设施 | ❌ 额外组件 |
| **生态成熟度** | ✅ 40+ 年历史 | ⚠️ 新兴技术 |
| **成本** | ✅ 开源免费 | ⚠️ 可能收费 |
| **学习曲线** | ✅ 熟悉的 SQL | ⚠️ 新的 API |

### 1.3 核心价值

**技术价值**：

- 🎯 **统一数据栈**：向量数据和关系数据在同一数据库
- ⚡ **高性能**：HNSW 索引，毫秒级检索
- 🔐 **数据安全**：RLS、加密、审计等企业级特性
- 📈 **可扩展**：支持 Citus 分布式扩展

**业务价值**：

- 💰 **降低成本**：无需额外向量数据库
- 🚀 **快速开发**：丰富的 LangChain 集成
- 🛡️ **企业级**：成熟的 PostgreSQL 生态
- 🔄 **易于迁移**：标准 SQL 接口

### 1.4 知识体系思维导图

```mermaid
mindmap
  root((LangChain + PostgreSQL))
    原理与理论
      LangChain架构
        核心组件
        工作流程
        设计模式
      RAG原理
        检索增强
        上下文构建
        生成优化
      向量嵌入
        Embeddings模型
        相似度计算
        索引优化
    架构设计
      整体架构
        应用层
        LangChain层
        数据层
      向量存储
        PGVector配置
        索引策略
        分区管理
      检索器设计
        基础检索
        混合检索
        重排序
      链式调用
        简单链
        复杂链
        条件链
    程序设计
      环境配置
        依赖安装
        数据库配置
        API密钥
      文档处理
        加载器
        分割器
        元数据
      RAG开发
        向量化
        检索
        生成
      高级特性
        Agent
        Memory
        Tool集成
    运维管理
      性能优化
        向量索引
        缓存策略
        批处理
      监控告警
        查询监控
        成本监控
        错误追踪
      成本优化
        Token优化
        缓存命中
        模型选择
    案例实战
      知识库问答
        企业文档
        技术手册
        FAQ系统
      文档摘要
        长文摘要
        多文档摘要
        实时摘要
      代码助手
        代码搜索
        代码生成
        代码解释
      客服机器人
        意图识别
        知识检索
        对话管理
```

---

## 二、原理与理论

### 2.1 LangChain 架构原理

#### **核心组件详解**

```python
# LangChain核心组件示例
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.vectorstores import PGVector
from langchain.embeddings import OpenAIEmbeddings

# 1. Models: 语言模型
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000
)

# 2. Prompts: 提示模板
prompt = ChatPromptTemplate.from_template(
    """基于以下上下文回答问题：

上下文：{context}

问题：{question}

回答："""
)

# 3. Chains: 链式调用
chain = prompt | llm | StrOutputParser()

# 4. Vector Stores: 向量存储
vectorstore = PGVector(
    connection_string="postgresql://user:pass@localhost:5432/db",
    embedding_function=OpenAIEmbeddings(),
    collection_name="documents"
)

# 5. Retrievers: 检索器
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)
```

#### **LCEL (LangChain Expression Language)**

```python
# LCEL: 声明式链构建
from langchain.schema.runnable import RunnablePassthrough

# 构建RAG链
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 使用
answer = rag_chain.invoke("什么是PostgreSQL?")
```

### 2.2 RAG 检索增强生成

#### **RAG 工作原理**

```text
┌─────────────────────────────────────────────────────┐
│              RAG (检索增强生成) 流程                  │
├─────────────────────────────────────────────────────┤
│                                                       │
│  1. 用户查询                                         │
│     "PostgreSQL的MVCC是如何工作的？"                │
│          │                                           │
│          ▼                                           │
│  2. 查询向量化                                       │
│     Embedding([0.123, -0.456, ...])                │
│          │                                           │
│          ▼                                           │
│  3. 向量相似度搜索 (PostgreSQL + pgvector)          │
│     SELECT content, embedding <=> query_embedding   │
│     FROM documents                                   │
│     ORDER BY embedding <=> query_embedding           │
│     LIMIT 5;                                         │
│          │                                           │
│          ▼                                           │
│  4. 检索相关文档                                     │
│     [Doc1: "MVCC通过...", Doc2: "多版本...", ...]  │
│          │                                           │
│          ▼                                           │
│  5. 构建上下文                                       │
│     Context = "相关文档1: ...\n相关文档2: ..."      │
│          │                                           │
│          ▼                                           │
│  6. Prompt构建                                       │
│     "基于以下上下文回答问题：\n{context}\n问题..."  │
│          │                                           │
│          ▼                                           │
│  7. LLM生成回答                                      │
│     "PostgreSQL的MVCC使用多版本并发控制..."         │
│          │                                           │
│          ▼                                           │
│  8. 返回结果                                         │
│     Answer + Source Documents                        │
└─────────────────────────────────────────────────────┘
```

#### **关键技术点**

```python
# 1. 文档分块策略
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # 每块1000字符
    chunk_overlap=200,      # 重叠200字符
    separators=["\n\n", "\n", " ", ""]  # 按段落、句子、词分割
)

# 2. 元数据增强
documents = [
    {
        "content": "PostgreSQL是一个开源数据库...",
        "metadata": {
            "source": "postgresql_intro.pdf",
            "page": 1,
            "category": "database",
            "timestamp": "2024-12-04"
        }
    }
]

# 3. 混合搜索（向量 + 关键词）
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers import BM25Retriever

bm25_retriever = BM25Retriever.from_documents(documents)
vector_retriever = vectorstore.as_retriever()

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.3, 0.7]  # BM25占30%，向量占70%
)
```

### 2.3 向量嵌入与相似度搜索

#### **嵌入模型选择**

| 模型 | 维度 | 性能 | 成本 | 适用场景 |
|------|------|------|------|---------|
| **OpenAI text-embedding-3-small** | 1536 | ⭐⭐⭐⭐ | 💰 | 通用、平衡 |
| **OpenAI text-embedding-3-large** | 3072 | ⭐⭐⭐⭐⭐ | 💰💰 | 高精度 |
| **sentence-transformers/all-MiniLM-L6-v2** | 384 | ⭐⭐⭐ | 免费 | 开源、快速 |
| **BAAI/bge-large-zh-v1.5** | 1024 | ⭐⭐⭐⭐ | 免费 | 中文优化 |

#### **相似度计算**

```sql
-- PostgreSQL中的向量相似度计算（带错误处理和性能测试）

-- 1. 余弦相似度（cosine similarity）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'vector'
    ) THEN
        RAISE WARNING 'pgvector扩展未安装，向量操作可能失败';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'documents'
    ) THEN
        RAISE WARNING '表documents不存在';
    END IF;

    RAISE NOTICE '开始执行余弦相似度查询';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '查询准备失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    content,
    1 - (embedding <=> query_embedding) AS cosine_similarity
FROM documents
ORDER BY embedding <=> query_embedding
LIMIT 10;

-- 2. 欧氏距离（L2 distance）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    content,
    embedding <-> query_embedding AS l2_distance
FROM documents
ORDER BY embedding <-> query_embedding
LIMIT 10;

-- 3. 内积（inner product）
SELECT
    content,
    embedding <#> query_embedding AS inner_product
FROM documents
ORDER BY embedding <#> query_embedding DESC
LIMIT 10;
```

#### **索引优化**

```sql
-- HNSW索引（推荐，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'vector'
    ) THEN
        RAISE EXCEPTION 'pgvector扩展未安装，请先安装: CREATE EXTENSION vector;';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'documents'
    ) THEN
        RAISE EXCEPTION '表documents不存在，请先创建表';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'documents'
        AND indexname LIKE '%hnsw%'
    ) THEN
        DROP INDEX IF EXISTS documents_embedding_hnsw_idx;
        RAISE NOTICE '已删除现有HNSW索引';
    END IF;

    CREATE INDEX documents_embedding_hnsw_idx ON documents
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

    RAISE NOTICE 'HNSW索引创建成功';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表documents不存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION 'hnsw索引方法不存在，请检查pgvector扩展安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建HNSW索引失败: %', SQLERRM;
END $$;

-- 参数说明：
-- m: 每个节点的最大连接数（16是默认值，越大精度越高但索引越大）
-- ef_construction: 构建索引时的搜索深度（64是默认值，越大构建越慢但精度越高）

-- IVFFlat索引（大规模数据，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'vector'
    ) THEN
        RAISE EXCEPTION 'pgvector扩展未安装，请先安装: CREATE EXTENSION vector;';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'documents'
        AND indexname LIKE '%ivfflat%'
    ) THEN
        DROP INDEX IF EXISTS documents_embedding_ivfflat_idx;
        RAISE NOTICE '已删除现有IVFFlat索引';
    END IF;

    CREATE INDEX documents_embedding_ivfflat_idx ON documents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

    RAISE NOTICE 'IVFFlat索引创建成功';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表documents不存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION 'ivfflat索引方法不存在，请检查pgvector扩展安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建IVFFlat索引失败: %', SQLERRM;
END $$;

-- 查询时调整精度
DO $$
BEGIN
    SET hnsw.ef_search = 40;  -- 查询时的搜索深度
    RAISE NOTICE 'HNSW搜索深度已设置为: 40';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '设置搜索深度失败: %', SQLERRM;
END $$;
```

### 2.4 上下文管理与优化

#### **上下文窗口限制**

```python
# Token计数与管理
import tiktoken

def count_tokens(text, model="gpt-4"):
    """计算文本的token数量"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def optimize_context(documents, max_tokens=6000):
    """优化上下文以适应token限制"""
    context = ""
    token_count = 0

    for doc in documents:
        doc_tokens = count_tokens(doc)
        if token_count + doc_tokens > max_tokens:
            break
        context += doc + "\n\n"
        token_count += doc_tokens

    return context, token_count
```

#### **上下文压缩**

```python
# 使用LangChain的ContextualCompressionRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# 创建压缩器
compressor = LLMChainExtractor.from_llm(llm)

# 创建压缩检索器
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)

# 使用：自动压缩检索到的文档
compressed_docs = compression_retriever.get_relevant_documents(
    "什么是PostgreSQL的MVCC?"
)
```

---

## 三、架构设计

### 3.1 整体架构

```python
# 完整的LangChain + PostgreSQL架构
"""
┌──────────────────────────────────────────────────────┐
│                 应用层 (Application)                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│   │  Web UI  │  │  API     │  │  CLI     │         │
│   └──────────┘  └──────────┘  └──────────┘         │
└──────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│              LangChain层 (Framework)                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│   │  Chains  │  │  Agents  │  │  Memory  │         │
│   └──────────┘  └──────────┘  └──────────┘         │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│   │Retrievers│  │ Prompts  │  │  Tools   │         │
│   └──────────┘  └──────────┘  └──────────┘         │
└──────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│               数据层 (Data Layer)                     │
│   ┌────────────────────────────────────────┐        │
│   │        PostgreSQL + pgvector            │        │
│   │  ┌──────────┐  ┌──────────┐           │        │
│   │  │ Vectors  │  │Relational│           │        │
│   │  │  Table   │  │  Tables  │           │        │
│   │  └──────────┘  └──────────┘           │        │
│   │  ┌──────────┐  ┌──────────┐           │        │
│   │  │  Indexes │  │  Cache   │           │        │
│   │  └──────────┘  └──────────┘           │        │
│   └────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│               外部服务 (External)                     │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│   │ OpenAI   │  │  Redis   │  │Monitoring│         │
│   └──────────┘  └──────────┘  └──────────┘         │
└──────────────────────────────────────────────────────┘
"""
```

### 3.2 向量存储集成

```python
# pgvector_store.py
from typing import List, Dict, Any, Optional
from langchain.vectorstores import PGVector
from langchain.embeddings.base import Embeddings
from langchain.schema import Document

class OptimizedPGVector:
    """优化的PGVector向量存储"""

    def __init__(
        self,
        connection_string: str,
        embedding_function: Embeddings,
        collection_name: str = "documents",
        pre_delete_collection: bool = False
    ):
        self.connection_string = connection_string
        self.embedding_function = embedding_function
        self.collection_name = collection_name

        # 创建向量存储
        self.vectorstore = PGVector(
            connection_string=connection_string,
            embedding_function=embedding_function,
            collection_name=collection_name,
            pre_delete_collection=pre_delete_collection
        )

        # 初始化索引
        self._ensure_index()

    def _ensure_index(self):
        """确保向量索引存在"""
        import psycopg2

        conn = psycopg2.connect(self.connection_string)
        with conn.cursor() as cur:
            # 检查索引是否存在
            cur.execute(f"""
                SELECT 1 FROM pg_indexes
                WHERE tablename = '{self.collection_name}'
                  AND indexname = '{self.collection_name}_embedding_idx'
            """)

            if not cur.fetchone():
                # 创建HNSW索引
                cur.execute(f"""
                    CREATE INDEX {self.collection_name}_embedding_idx
                    ON {self.collection_name}
                    USING hnsw (embedding vector_cosine_ops)
                    WITH (m = 16, ef_construction = 64);
                """)
                conn.commit()
                print(f"✅ Created HNSW index on {self.collection_name}")

        conn.close()

    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> List[str]:
        """批量添加文档"""
        doc_ids = []

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            ids = self.vectorstore.add_documents(batch)
            doc_ids.extend(ids)
            print(f"Processed {min(i + batch_size, len(documents))}/{len(documents)} documents")

        return doc_ids

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """带评分的相似度搜索"""
        return self.vectorstore.similarity_search_with_score(
            query,
            k=k,
            filter=filter
        )

    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5
    ) -> List[Document]:
        """最大边际相关性搜索（避免重复结果）"""
        return self.vectorstore.max_marginal_relevance_search(
            query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult
        )
```

### 3.3 检索器设计

```python
# advanced_retrievers.py
from langchain.retrievers import (
    MultiQueryRetriever,
    ContextualCompressionRetriever,
    EnsembleRetriever
)
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.prompts import PromptTemplate

class AdvancedRetriever:
    """高级检索器集合"""

    def __init__(self, vectorstore, llm):
        self.vectorstore = vectorstore
        self.llm = llm
        self.base_retriever = vectorstore.as_retriever()

    def multi_query_retriever(self) -> MultiQueryRetriever:
        """多查询检索器：生成多个查询变体"""
        return MultiQueryRetriever.from_llm(
            retriever=self.base_retriever,
            llm=self.llm
        )

    def compressed_retriever(self) -> ContextualCompressionRetriever:
        """压缩检索器：自动压缩检索结果"""
        compressor = LLMChainExtractor.from_llm(self.llm)
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=self.base_retriever
        )

    def self_query_retriever(self):
        """自查询检索器：从自然语言生成结构化查询"""
        from langchain.retrievers.self_query.base import SelfQueryRetriever
        from langchain.chains.query_constructor.base import AttributeInfo

        metadata_field_info = [
            AttributeInfo(
                name="source",
                description="文档来源",
                type="string"
            ),
            AttributeInfo(
                name="page",
                description="页码",
                type="integer"
            )
        ]

        return SelfQueryRetriever.from_llm(
            llm=self.llm,
            vectorstore=self.vectorstore,
            document_contents="PostgreSQL技术文档",
            metadata_field_info=metadata_field_info
        )

    def parent_document_retriever(self):
        """父文档检索器：检索小块，返回大块"""
        from langchain.retrievers import ParentDocumentRetriever
        from langchain.storage import InMemoryStore

        # 用于存储完整文档
        docstore = InMemoryStore()

        return ParentDocumentRetriever(
            vectorstore=self.vectorstore,
            docstore=docstore,
            child_splitter=self._get_child_splitter(),
            parent_splitter=self._get_parent_splitter()
        )

    def _get_child_splitter(self):
        """子文档分割器（小块）"""
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        return RecursiveCharacterTextSplitter(chunk_size=400)

    def _get_parent_splitter(self):
        """父文档分割器（大块）"""
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        return RecursiveCharacterTextSplitter(chunk_size=2000)
```

### 3.4 链式调用优化

```python
# optimized_chains.py
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.schema.output_parser import StrOutputParser
from operator import itemgetter

class OptimizedChains:
    """优化的链式调用"""

    def __init__(self, retriever, llm, prompt_template):
        self.retriever = retriever
        self.llm = llm
        self.prompt = prompt_template

    def basic_rag_chain(self):
        """基础RAG链"""
        return (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def rag_chain_with_sources(self):
        """带来源的RAG链"""
        from langchain.schema.runnable import RunnableMap

        return (
            RunnableMap({
                "context": self.retriever,
                "question": RunnablePassthrough()
            })
            | {
                "answer": self.prompt | self.llm | StrOutputParser(),
                "sources": lambda x: x["context"]
            }
        )

    def conversational_rag_chain(self, memory):
        """对话式RAG链"""
        from langchain.schema.runnable import RunnableMap

        def format_chat_history(messages):
            return "\n".join([f"{m.type}: {m.content}" for m in messages])

        return (
            RunnableMap({
                "context": itemgetter("question") | self.retriever,
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history") | RunnableLambda(format_chat_history)
            })
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def multi_step_rag_chain(self):
        """多步骤RAG链"""
        # 步骤1：重写查询
        query_rewriter = (
            ChatPromptTemplate.from_template(
                "将以下查询改写得更清晰：{question}"
            )
            | self.llm
            | StrOutputParser()
        )

        # 步骤2：检索
        # 步骤3：生成回答
        return (
            {"rewritten_query": query_rewriter}
            | {"context": lambda x: self.retriever.get_relevant_documents(x["rewritten_query"]),
               "question": itemgetter("question")}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
```

---

## 四、程序设计

### 4.1 环境准备

#### **依赖安装**

```bash
# 创建虚拟环境
python3 -m venv langchain_env
source langchain_env/bin/activate  # Linux/Mac
# langchain_env\Scripts\activate  # Windows

# 安装核心依赖
pip install langchain==0.1.0
pip install langchain-openai==0.0.2
pip install langchain-community==0.0.10
pip install pgvector==0.2.4
pip install psycopg2-binary==2.9.9
pip install tiktoken==0.5.2

# 安装文档处理依赖
pip install pypdf==3.17.0
pip install docx2txt==0.8
pip install unstructured==0.11.0

# 创建requirements.txt
cat > requirements.txt <<EOF
langchain==0.1.0
langchain-openai==0.0.2
langchain-community==0.0.10
pgvector==0.2.4
psycopg2-binary==2.9.9
tiktoken==0.5.2
pypdf==3.17.0
docx2txt==0.8
unstructured==0.11.0
python-dotenv==1.0.0
EOF
```

#### **PostgreSQL配置**

```sql
-- 创建数据库和扩展（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_database
        WHERE datname = 'langchain_db'
    ) THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE langchain_db');
        RAISE NOTICE '数据库 langchain_db 创建成功';
    ELSE
        RAISE NOTICE '数据库 langchain_db 已存在';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '创建数据库失败: %', SQLERRM;
END $$;

-- 切换到新数据库（需要在psql中执行）
-- \c langchain_db

-- 安装pgvector扩展（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'vector'
    ) THEN
        CREATE EXTENSION vector;
        RAISE NOTICE 'pgvector扩展安装成功';
    ELSE
        RAISE NOTICE 'pgvector扩展已存在';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'pgvector扩展文件不存在，请检查PostgreSQL安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装pgvector扩展失败: %', SQLERRM;
END $$;

-- 创建向量表（LangChain会自动创建，这里展示结构，带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'langchain_pg_embedding'
    ) THEN
        RAISE NOTICE '表 langchain_pg_embedding 已存在';
    ELSE
        CREATE TABLE langchain_pg_embedding (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            collection_id UUID,
            embedding VECTOR(1536),  -- OpenAI embeddings维度
            document TEXT,
            cmetadata JSONB,
            custom_id TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        RAISE NOTICE '表 langchain_pg_embedding 创建成功';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表 langchain_pg_embedding 已存在';
    WHEN undefined_type THEN
        RAISE EXCEPTION 'VECTOR类型不存在，请先安装pgvector扩展';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 创建索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'langchain_pg_embedding'
    ) THEN
        RAISE EXCEPTION '表 langchain_pg_embedding 不存在，请先创建表';
    END IF;

    -- HNSW向量索引
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'langchain_pg_embedding'
        AND indexname = 'langchain_pg_embedding_embedding_idx'
    ) THEN
        CREATE INDEX langchain_pg_embedding_embedding_idx
        ON langchain_pg_embedding USING hnsw (embedding vector_cosine_ops);
        RAISE NOTICE 'HNSW向量索引创建成功';
    END IF;

    -- B-tree索引
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'langchain_pg_embedding'
        AND indexname = 'langchain_pg_embedding_collection_id_idx'
    ) THEN
        CREATE INDEX langchain_pg_embedding_collection_id_idx
        ON langchain_pg_embedding USING btree (collection_id);
        RAISE NOTICE 'B-tree索引创建成功';
    END IF;

    -- GIN索引
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'langchain_pg_embedding'
        AND indexname = 'langchain_pg_embedding_cmetadata_idx'
    ) THEN
        CREATE INDEX langchain_pg_embedding_cmetadata_idx
        ON langchain_pg_embedding USING gin (cmetadata);
        RAISE NOTICE 'GIN索引创建成功';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 langchain_pg_embedding 不存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION '索引方法不存在，请检查扩展安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;
```

#### **环境变量配置**

```python
# .env 文件
OPENAI_API_KEY=sk-your-openai-api-key
DATABASE_URL=postgresql://user:password@localhost:5432/langchain_db
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4
LANGCHAIN_TRACING_V2=true  # 启用LangSmith追踪
LANGCHAIN_API_KEY=your-langsmith-api-key
```

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")

    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL")

    # 应用配置
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K = 5

    # LangSmith追踪
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false") == "true"
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
```

### 4.2 向量存储配置

```python
# vector_store_setup.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import PGVector
from config import Config

def initialize_vector_store(collection_name="documents"):
    """初始化向量存储"""

    # 创建embeddings
    embeddings = OpenAIEmbeddings(
        model=Config.EMBEDDING_MODEL,
        openai_api_key=Config.OPENAI_API_KEY
    )

    # 创建PGVector存储
    vectorstore = PGVector(
        connection_string=Config.DATABASE_URL,
        embedding_function=embeddings,
        collection_name=collection_name
    )

    return vectorstore

def test_vector_store():
    """测试向量存储"""
    from langchain.schema import Document

    vectorstore = initialize_vector_store("test_collection")

    # 测试文档
    test_docs = [
        Document(
            page_content="PostgreSQL是一个强大的开源关系数据库。",
            metadata={"source": "test", "id": 1}
        ),
        Document(
            page_content="pgvector是PostgreSQL的向量扩展。",
            metadata={"source": "test", "id": 2}
        )
    ]

    # 添加文档
    ids = vectorstore.add_documents(test_docs)
    print(f"✅ Added {len(ids)} documents")

    # 测试搜索
    results = vectorstore.similarity_search("什么是PostgreSQL?", k=2)
    print(f"✅ Found {len(results)} results")
    for i, doc in enumerate(results):
        print(f"\n结果 {i+1}:")
        print(f"内容: {doc.page_content}")
        print(f"元数据: {doc.metadata}")

if __name__ == "__main__":
    test_vector_store()
```

### 4.3 文档处理与加载

```python
# document_processor.py
from typing import List
from langchain.schema import Document
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
    UnstructuredMarkdownLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

class DocumentProcessor:
    """文档处理器"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 文本分割器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len
        )

    def load_pdf(self, file_path: str) -> List[Document]:
        """加载PDF文件"""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return self.split_documents(documents)

    def load_directory(
        self,
        directory: str,
        glob_pattern: str = "**/*.md"
    ) -> List[Document]:
        """加载目录中的所有文档"""
        loader = DirectoryLoader(
            directory,
            glob=glob_pattern,
            loader_cls=UnstructuredMarkdownLoader
        )
        documents = loader.load()
        return self.split_documents(documents)

    def load_text(self, file_path: str) -> List[Document]:
        """加载文本文件"""
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        return self.split_documents(documents)

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档"""
        return self.splitter.split_documents(documents)

    def add_metadata(
        self,
        documents: List[Document],
        metadata: dict
    ) -> List[Document]:
        """添加元数据"""
        for doc in documents:
            doc.metadata.update(metadata)
        return documents

# 使用示例
if __name__ == "__main__":
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)

    # 加载PDF
    pdf_docs = processor.load_pdf("postgresql_manual.pdf")
    print(f"✅ Loaded {len(pdf_docs)} chunks from PDF")

    # 加载Markdown文件
    md_docs = processor.load_directory("./docs", glob_pattern="**/*.md")
    print(f"✅ Loaded {len(md_docs)} chunks from Markdown files")

    # 添加元数据
    md_docs = processor.add_metadata(
        md_docs,
        {"category": "documentation", "version": "18.0"}
    )
```

### 4.4 RAG 应用开发

```python
# rag_application.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from config import Config

class RAGApplication:
    """RAG应用"""

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

        # LLM
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=0.7,
            openai_api_key=Config.OPENAI_API_KEY
        )

        # Prompt模板
        self.prompt = ChatPromptTemplate.from_template("""
你是一个PostgreSQL专家助手。请基于以下上下文回答用户的问题。

上下文：
{context}

问题：{question}

回答要求：
1. 准确、专业
2. 如果上下文中没有相关信息，请明确说明
3. 提供代码示例（如果适用）
4. 引用来源

回答：
""")

        # 检索器
        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": Config.TOP_K}
        )

        # 构建RAG链
        self.chain = self._build_chain()

    def _build_chain(self):
        """构建RAG链"""
        def format_docs(docs):
            return "\n\n".join([
                f"文档 {i+1} (来源: {doc.metadata.get('source', 'unknown')}):\n{doc.page_content}"
                for i, doc in enumerate(docs)
            ])

        return (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def query(self, question: str) -> dict:
        """查询接口"""
        # 执行检索
        retrieved_docs = self.retriever.get_relevant_documents(question)

        # 生成回答
        answer = self.chain.invoke(question)

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                }
                for doc in retrieved_docs
            ]
        }

    def query_with_history(
        self,
        question: str,
        chat_history: List[tuple[str, str]]
    ) -> dict:
        """带历史的查询"""
        from langchain.schema.runnable import RunnableMap
        from operator import itemgetter

        # 构建对话历史字符串
        history_str = "\n".join([
            f"用户: {q}\n助手: {a}"
            for q, a in chat_history
        ])

        # 更新prompt
        contextualized_prompt = ChatPromptTemplate.from_template("""
基于以下对话历史和上下文，回答最新的问题。

对话历史：
{chat_history}

上下文：
{context}

最新问题：{question}

回答：
""")

        # 构建链
        chain = (
            RunnableMap({
                "context": itemgetter("question") | self.retriever | self._format_docs,
                "chat_history": itemgetter("chat_history"),
                "question": itemgetter("question")
            })
            | contextualized_prompt
            | self.llm
            | StrOutputParser()
        )

        answer = chain.invoke({
            "question": question,
            "chat_history": history_str
        })

        return {
            "question": question,
            "answer": answer
        }

    @staticmethod
    def _format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

# 使用示例
if __name__ == "__main__":
    from vector_store_setup import initialize_vector_store

    # 初始化
    vectorstore = initialize_vector_store()
    rag_app = RAGApplication(vectorstore)

    # 查询
    result = rag_app.query("PostgreSQL的MVCC是如何工作的？")

    print("问题:", result["question"])
    print("\n回答:", result["answer"])
    print("\n来源:")
    for i, source in enumerate(result["sources"]):
        print(f"\n来源 {i+1}:")
        print(f"  内容: {source['content']}")
        print(f"  元数据: {source['metadata']}")
```

### 4.5 高级特性

#### **Agent开发**

```python
# agent_application.py
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

class PostgreSQLAgent:
    """PostgreSQL专家Agent"""

    def __init__(self, vectorstore, llm):
        self.vectorstore = vectorstore
        self.llm = llm
        self.tools = self._create_tools()
        self.agent = self._create_agent()

    def _create_tools(self):
        """创建工具"""
        # 1. 文档搜索工具
        doc_search_tool = Tool(
            name="DocumentSearch",
            func=self._search_documents,
            description="搜索PostgreSQL文档。输入：查询字符串。输出：相关文档内容。"
        )

        # 2. SQL执行工具（演示用，实际需要安全检查）
        sql_tool = Tool(
            name="SQLExecutor",
            func=self._execute_sql,
            description="执行PostgreSQL查询。输入：SQL语句。输出：查询结果。"
        )

        # 3. 性能分析工具
        explain_tool = Tool(
            name="ExplainAnalyze",
            func=self._explain_query,
            description="分析SQL查询性能。输入：SQL语句。输出：EXPLAIN (ANALYZE, BUFFERS, TIMING)结果。"
        )

        return [doc_search_tool, sql_tool, explain_tool]

    def _search_documents(self, query: str) -> str:
        """搜索文档"""
        docs = self.vectorstore.similarity_search(query, k=3)
        return "\n\n".join([doc.page_content for doc in docs])

    def _execute_sql(self, sql: str) -> str:
        """执行SQL（需要安全检查）"""
        import psycopg2
        from config import Config

        try:
            conn = psycopg2.connect(Config.DATABASE_URL)
            with conn.cursor() as cur:
                cur.execute(sql)
                if cur.description:  # SELECT查询
                    results = cur.fetchall()
                    return str(results[:10])  # 限制返回结果
                else:  # DML查询
                    conn.commit()
                    return f"Query executed successfully. Rows affected: {cur.rowcount}"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            conn.close()

    def _explain_query(self, sql: str) -> str:
        """EXPLAIN (ANALYZE, BUFFERS, TIMING)"""
        import psycopg2
        from config import Config

        try:
            conn = psycopg2.connect(Config.DATABASE_URL)
            with conn.cursor() as cur:
                cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, TIMING) {sql}")
                results = cur.fetchall()
                return "\n".join([row[0] for row in results])
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            conn.close()

    def _create_agent(self):
        """创建Agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个PostgreSQL专家助手。你可以使用以下工具来帮助用户：

1. DocumentSearch: 搜索PostgreSQL文档
2. SQLExecutor: 执行SQL查询
3. ExplainAnalyze: 分析查询性能

请根据用户问题选择合适的工具。"""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5
        )

    def run(self, query: str) -> str:
        """运行Agent"""
        return self.agent.invoke({"input": query})
```

#### **Memory管理**

```python
# memory_management.py
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory
)
from langchain.schema import BaseMessage

class ConversationManager:
    """对话管理器"""

    def __init__(self, llm, memory_type="buffer"):
        self.llm = llm
        self.memory = self._create_memory(memory_type)

    def _create_memory(self, memory_type: str):
        """创建Memory"""
        if memory_type == "buffer":
            # 缓冲所有消息
            return ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        elif memory_type == "window":
            # 只保留最近N条消息
            return ConversationBufferWindowMemory(
                k=5,  # 保留最近5条消息
                memory_key="chat_history",
                return_messages=True
            )
        elif memory_type == "summary":
            # 总结历史消息
            return ConversationSummaryMemory(
                llm=self.llm,
                memory_key="chat_history",
                return_messages=True
            )
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")

    def add_message(self, role: str, content: str):
        """添加消息"""
        if role == "user":
            self.memory.chat_memory.add_user_message(content)
        elif role == "assistant":
            self.memory.chat_memory.add_ai_message(content)

    def get_history(self) -> List[BaseMessage]:
        """获取历史"""
        return self.memory.load_memory_variables({})["chat_history"]

    def clear(self):
        """清空历史"""
        self.memory.clear()
```

---

## 五、运维管理

### 5.1 性能优化

```python
# performance_optimization.py
import time
from functools import lru_cache
import hashlib

class PerformanceOptimizer:
    """性能优化器"""

    def __init__(self, vectorstore, llm):
        self.vectorstore = vectorstore
        self.llm = llm
        self.cache = {}
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_queries': 0
        }

    @lru_cache(maxsize=1000)
    def cached_embedding(self, text: str):
        """缓存embedding计算"""
        return self.vectorstore.embedding_function.embed_query(text)

    def cached_retrieval(self, query: str, k: int = 5) -> list:
        """缓存检索结果"""
        cache_key = hashlib.md5(f"{query}_{k}".encode()).hexdigest()

        self.stats['total_queries'] += 1

        if cache_key in self.cache:
            self.stats['cache_hits'] += 1
            return self.cache[cache_key]

        self.stats['cache_misses'] += 1
        results = self.vectorstore.similarity_search(query, k=k)
        self.cache[cache_key] = results

        # 限制缓存大小
        if len(self.cache) > 1000:
            # 删除最老的条目
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        return results

    def batch_embed_documents(self, texts: List[str], batch_size: int = 100):
        """批量嵌入文档"""
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.vectorstore.embedding_function.embed_documents(batch)
            embeddings.extend(batch_embeddings)
            time.sleep(0.1)  # 避免频率限制
        return embeddings

    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        total = self.stats['total_queries']
        hits = self.stats['cache_hits']
        hit_rate = hits / total if total > 0 else 0

        return {
            'total_queries': total,
            'cache_hits': hits,
            'cache_misses': self.stats['cache_misses'],
            'hit_rate': f"{hit_rate:.2%}"
        }
```

### 5.2 监控告警

```python
# monitoring.py
import logging
from datetime import datetime
from typing import Dict, Any

class RAGMonitor:
    """RAG应用监控"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = []

    def log_query(
        self,
        query: str,
        answer: str,
        retrieval_time: float,
        generation_time: float,
        num_docs_retrieved: int,
        tokens_used: int
    ):
        """记录查询指标"""
        metric = {
            'timestamp': datetime.now(),
            'query_length': len(query),
            'answer_length': len(answer),
            'retrieval_time': retrieval_time,
            'generation_time': generation_time,
            'total_time': retrieval_time + generation_time,
            'num_docs_retrieved': num_docs_retrieved,
            'tokens_used': tokens_used
        }

        self.metrics.append(metric)

        # 告警检查
        if retrieval_time > 2.0:
            self.logger.warning(f"Slow retrieval: {retrieval_time:.2f}s")

        if generation_time > 10.0:
            self.logger.warning(f"Slow generation: {generation_time:.2f}s")

        if tokens_used > 6000:
            self.logger.warning(f"High token usage: {tokens_used}")

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        if not self.metrics:
            return {}

        import numpy as np

        retrieval_times = [m['retrieval_time'] for m in self.metrics]
        generation_times = [m['generation_time'] for m in self.metrics]
        total_times = [m['total_time'] for m in self.metrics]
        tokens = [m['tokens_used'] for m in self.metrics]

        return {
            'total_queries': len(self.metrics),
            'avg_retrieval_time': np.mean(retrieval_times),
            'p95_retrieval_time': np.percentile(retrieval_times, 95),
            'avg_generation_time': np.mean(generation_times),
            'p95_generation_time': np.percentile(generation_times, 95),
            'avg_total_time': np.mean(total_times),
            'p95_total_time': np.percentile(total_times, 95),
            'avg_tokens': np.mean(tokens),
            'total_tokens': sum(tokens)
        }
```

### 5.3 成本优化

```python
# cost_optimization.py
import tiktoken

class CostOptimizer:
    """成本优化器"""

    # OpenAI定价（2024年12月）
    PRICING = {
        'text-embedding-3-small': {
            'input': 0.02 / 1_000_000  # $0.02 per 1M tokens
        },
        'text-embedding-3-large': {
            'input': 0.13 / 1_000_000  # $0.13 per 1M tokens
        },
        'gpt-4': {
            'input': 0.03 / 1000,   # $0.03 per 1K tokens
            'output': 0.06 / 1000   # $0.06 per 1K tokens
        },
        'gpt-3.5-turbo': {
            'input': 0.0015 / 1000,  # $0.0015 per 1K tokens
            'output': 0.002 / 1000   # $0.002 per 1K tokens
        }
    }

    def __init__(self, embedding_model: str, llm_model: str):
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.encoding = tiktoken.encoding_for_model(llm_model)

    def count_tokens(self, text: str) -> int:
        """计算token数量"""
        return len(self.encoding.encode(text))

    def estimate_embedding_cost(self, num_documents: int, avg_doc_length: int) -> float:
        """估算embedding成本"""
        total_tokens = num_documents * avg_doc_length
        cost_per_token = self.PRICING[self.embedding_model]['input']
        return total_tokens * cost_per_token

    def estimate_query_cost(
        self,
        context_tokens: int,
        query_tokens: int,
        response_tokens: int
    ) -> float:
        """估算单次查询成本"""
        input_cost = (context_tokens + query_tokens) * self.PRICING[self.llm_model]['input']
        output_cost = response_tokens * self.PRICING[self.llm_model]['output']
        return input_cost + output_cost

    def optimize_context(self, documents: List[str], max_tokens: int = 4000):
        """优化上下文以控制成本"""
        optimized = []
        token_count = 0

        for doc in documents:
            doc_tokens = self.count_tokens(doc)
            if token_count + doc_tokens > max_tokens:
                break
            optimized.append(doc)
            token_count += doc_tokens

        return optimized, token_count

    def suggest_model_switch(
        self,
        avg_input_tokens: int,
        avg_output_tokens: int,
        queries_per_day: int
    ) -> dict:
        """建议模型切换"""
        # 计算GPT-4成本
        gpt4_daily_cost = queries_per_day * self.estimate_query_cost(
            avg_input_tokens, 0, avg_output_tokens
        )

        # 计算GPT-3.5成本
        gpt35_daily_cost = queries_per_day * (
            avg_input_tokens * self.PRICING['gpt-3.5-turbo']['input'] +
            avg_output_tokens * self.PRICING['gpt-3.5-turbo']['output']
        )

        savings = gpt4_daily_cost - gpt35_daily_cost
        savings_percent = (savings / gpt4_daily_cost) * 100

        return {
            'gpt4_daily_cost': f"${gpt4_daily_cost:.2f}",
            'gpt35_daily_cost': f"${gpt35_daily_cost:.2f}",
            'daily_savings': f"${savings:.2f}",
            'savings_percent': f"{savings_percent:.1f}%",
            'recommendation': 'Switch to GPT-3.5-Turbo' if savings > 10 else 'Keep GPT-4'
        }
```

### 5.4 最佳实践

```python
# best_practices.py

class BestPractices:
    """LangChain + PostgreSQL最佳实践"""

    @staticmethod
    def document_preparation():
        """文档准备最佳实践"""
        return {
            'chunking': {
                'chunk_size': '1000-2000字符（取决于内容类型）',
                'chunk_overlap': '10-20%的chunk_size',
                'separators': '按段落、句子、词分割（优先级递减）'
            },
            'metadata': {
                'required': ['source', 'timestamp'],
                'recommended': ['category', 'author', 'version'],
                'indexable': '确保重要字段可搜索'
            },
            'cleaning': {
                'remove_noise': '删除页眉、页脚、重复内容',
                'normalize': '统一格式、编码',
                'validate': '检查内容完整性'
            }
        }

    @staticmethod
    def vector_store_optimization():
        """向量存储优化最佳实践"""
        return {
            'indexing': {
                'type': 'HNSW（推荐）或IVFFlat',
                'timing': '在批量导入后创建索引',
                'parameters': {
                    'hnsw_m': '16-32（越大精度越高）',
                    'hnsw_ef_construction': '64-200（越大构建越慢）',
                    'hnsw_ef_search': '40-100（查询时调整）'
                }
            },
            'partitioning': {
                'strategy': '按时间或类别分区',
                'benefits': '提升查询性能、便于维护',
                'size': '每个分区建议<1000万行'
            },
            'maintenance': {
                'vacuum': '定期VACUUM以回收空间',
                'analyze': '定期ANALYZE以更新统计信息',
                'reindex': '必要时重建索引'
            }
        }

    @staticmethod
    def retrieval_optimization():
        """检索优化最佳实践"""
        return {
            'search_strategies': {
                'similarity': '基础相似度搜索',
                'mmr': '最大边际相关性（避免重复）',
                'multi_query': '生成多个查询变体',
                'hybrid': '结合向量和关键词搜索'
            },
            'filtering': {
                'pre_filtering': '使用元数据过滤后检索',
                'post_filtering': '检索后根据规则过滤',
                'balance': '平衡过滤精度和召回率'
            },
            'reranking': {
                'method': '使用LLM重排序检索结果',
                'benefit': '提升相关性，降低噪音',
                'cost': '增加延迟和成本'
            }
        }

    @staticmethod
    def production_deployment():
        """生产部署最佳实践"""
        return {
            'performance': {
                'caching': '缓存embedding和检索结果',
                'batching': '批量处理文档和请求',
                'async': '使用异步I/O提升吞吐'
            },
            'reliability': {
                'retries': '实现重试机制',
                'fallback': '准备降级方案',
                'monitoring': '全面监控和告警'
            },
            'security': {
                'authentication': 'API密钥管理',
                'authorization': 'RLS行级安全',
                'encryption': '传输和存储加密'
            },
            'scalability': {
                'read_replicas': 'PostgreSQL读副本',
                'connection_pooling': 'PgBouncer连接池',
                'citus': '使用Citus实现分布式'
            }
        }
```

---

## 六、案例实战

### 6.1 企业知识库问答

**完整实现见文档完整版...**

### 6.2 文档智能摘要

**完整实现见文档完整版...**

### 6.3 代码助手

**完整实现见文档完整版...**

### 6.4 客服机器人

**完整实现见文档完整版...**

---

## 七、性能测试

**详细测试数据见文档完整版...**

---

## 八、总结与展望

### 核心收获

1. ✅ LangChain + PostgreSQL 提供了强大的RAG能力
2. ✅ pgvector实现了企业级向量搜索
3. ✅ 统一数据栈降低了运维复杂度
4. ✅ 丰富的集成和工具加速了开发

### 适用场景

- ✅ 企业知识库
- ✅ 智能客服
- ✅ 文档分析
- ✅ 代码助手

---

## 九、参考资料

1. **LangChain官方文档**: [https://python.langchain.com/](https://python.langchain.com/)
2. **pgvector GitHub**: [https://github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)
3. **PostgreSQL官方文档**: [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)

---

**最后更新**: 2025年12月4日
**维护者**: PostgreSQL Modern Team
**文档编号**: 14-AI-LANGCHAIN
**版本**: v1.0
