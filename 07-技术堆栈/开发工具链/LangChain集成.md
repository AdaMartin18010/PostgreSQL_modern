# LangChain 集成

> **更新时间**: 2025 年 11 月 1 日
> **文档编号**: 07-01-02
> **技术版本**: LangChain 0.3+, PostgreSQL 18+

## 📑 目录

- [LangChain 集成](#langchain-集成)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 文档目标](#11-文档目标)
    - [1.2 LangChain 简介](#12-langchain-简介)
    - [1.3 集成价值](#13-集成价值)
  - [2. 快速开始](#2-快速开始)
    - [2.1 环境准备](#21-环境准备)
      - [2.1.1 安装依赖](#211-安装依赖)
      - [2.1.2 环境配置](#212-环境配置)
    - [2.2 初始化向量存储](#22-初始化向量存储)
      - [2.2.1 基础配置](#221-基础配置)
      - [2.2.2 高级配置](#222-高级配置)
    - [2.3 向量搜索](#23-向量搜索)
      - [2.3.1 相似度搜索](#231-相似度搜索)
      - [2.3.2 带分数搜索](#232-带分数搜索)
      - [2.3.3 元数据过滤](#233-元数据过滤)
  - [3. RAG 应用实现](#3-rag-应用实现)
    - [3.1 基础 RAG](#31-基础-rag)
      - [3.1.1 RetrievalQA 链](#311-retrievalqa-链)
      - [3.1.2 Prompt 模板](#312-prompt-模板)
    - [3.2 高级 RAG](#32-高级-rag)
      - [3.2.1 文档压缩器](#321-文档压缩器)
      - [3.2.2 重排序机制](#322-重排序机制)
      - [3.2.3 对话 RAG](#323-对话-rag)
  - [4. Neon 分支集成](#4-neon-分支集成)
    - [4.1 创建实验分支](#41-创建实验分支)
    - [4.2 分支管理](#42-分支管理)
    - [4.3 实验流程](#43-实验流程)
  - [5. 混合搜索实现](#5-混合搜索实现)
    - [5.1 全文+向量搜索](#51-全文向量搜索)
      - [5.1.1 BM25 检索器](#511-bm25-检索器)
      - [5.1.2 向量检索器](#512-向量检索器)
    - [5.2 RRF 融合算法](#52-rrf-融合算法)
      - [5.2.1 Ensemble Retriever](#521-ensemble-retriever)
      - [5.2.2 权重配置](#522-权重配置)
  - [6. 完整 RAG 流程](#6-完整-rag-流程)
    - [6.1 文档加载和向量化](#61-文档加载和向量化)
      - [6.1.1 文档加载器](#611-文档加载器)
      - [6.1.2 文本切分](#612-文本切分)
      - [6.1.3 向量化存储](#613-向量化存储)
    - [6.2 RAG 链配置](#62-rag-链配置)
      - [6.2.1 ConversationalRetrievalChain](#621-conversationalretrievalchain)
      - [6.2.2 对话内存管理](#622-对话内存管理)
  - [7. 性能优化](#7-性能优化)
    - [7.1 批量处理](#71-批量处理)
    - [7.2 缓存策略](#72-缓存策略)
    - [7.3 异步处理](#73-异步处理)
  - [8. 最佳实践](#8-最佳实践)
    - [8.1 配置最佳实践](#81-配置最佳实践)
    - [8.2 性能最佳实践](#82-性能最佳实践)
    - [8.3 RAG 最佳实践](#83-rag-最佳实践)
  - [9. 常见问题](#9-常见问题)
    - [9.1 依赖问题](#91-依赖问题)
    - [9.2 配置问题](#92-配置问题)
    - [9.3 性能问题](#93-性能问题)
  - [10. 参考资料](#10-参考资料)
    - [10.1 官方文档](#101-官方文档)
    - [10.2 技术文档](#102-技术文档)
    - [10.3 相关资源](#103-相关资源)

---

## 1. 概述

### 1.1 文档目标

**核心目标**:

本文档提供 LangChain 与 PostgreSQL + pgvector 的集成指南，帮助开发者快速构建基于向量搜索的 RAG 应用
。

**文档价值**:

| 价值项       | 说明               | 影响             |
| ------------ | ------------------ | ---------------- |
| **快速集成** | 提供完整的集成步骤 | 减少开发时间     |
| **RAG 应用** | 支持检索增强生成   | 提升 AI 应用能力 |
| **性能优化** | 提供性能优化建议   | 提高应用性能     |

### 1.2 LangChain 简介

**LangChain 概述**:

LangChain 是一个用于构建 LLM 应用的框架，提供了文档加载、向量存储、检索增强生成（RAG）、链式调用等功
能。

**核心特性**:

| 特性         | 说明                  | 优势             |
| ------------ | --------------------- | ---------------- |
| **向量存储** | 支持多种向量存储后端  | 灵活选择存储方案 |
| **RAG 支持** | 内置 RAG 应用支持     | 简化 RAG 开发    |
| **链式调用** | 支持复杂的 LLM 应用链 | 提高应用灵活性   |
| **文档处理** | 支持多种文档格式      | 易于文档处理     |

### 1.3 集成价值

**集成优势**:

| 优势         | 说明                           | 影响               |
| ------------ | ------------------------------ | ------------------ |
| **向量搜索** | PostgreSQL + pgvector 向量搜索 | **高性能向量检索** |
| **统一存储** | 业务数据与向量数据统一存储     | **简化架构**       |
| **SQL 支持** | 可使用 SQL 进行复杂查询        | **灵活查询**       |
| **事务支持** | 支持 ACID 事务                 | **数据一致性**     |

## 2. 快速开始

### 2.1 环境准备

#### 2.1.1 安装依赖

**Python 依赖安装**:

```bash
# 基础依赖
pip install langchain langchain-postgres langchain-openai

# PostgreSQL 驱动和扩展
pip install psycopg2-binary pgvector

# 可选：其他依赖
pip install python-dotenv  # 环境变量管理
pip install tiktoken        # Token 计数
```

**依赖版本要求**:

| 包                     | 最低版本 | 推荐版本   |
| ---------------------- | -------- | ---------- |
| **langchain**          | 0.3.0    | **0.3.0+** |
| **langchain-postgres** | 0.0.1    | **0.0.1+** |
| **langchain-openai**   | 0.2.0    | **0.2.0+** |
| **psycopg2-binary**    | 2.9.0    | **2.9.9+** |
| **pgvector**           | 0.3.0    | **0.3.0+** |

**requirements.txt**:

```txt
# LangChain 核心包
langchain>=0.3.0
langchain-core>=0.3.0
langchain-community>=0.3.0

# LangChain PostgreSQL 集成
langchain-postgres>=0.0.1

# LangChain OpenAI 集成
langchain-openai>=0.2.0

# PostgreSQL 驱动
psycopg2-binary>=2.9.9
pgvector>=0.3.0

# 工具包
python-dotenv>=1.0.0
tiktoken>=0.7.0
```

#### 2.1.2 环境配置

**环境变量配置**:

```python
# .env 文件
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/ai_demo
OPENAI_API_KEY=sk-xxx
NEON_API_KEY=neon_xxx  # 可选：Neon 分支支持
```

**环境变量加载**:

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库连接配置
POSTGRES_URL = os.getenv("POSTGRES_URL")
if not POSTGRES_URL:
    raise ValueError("POSTGRES_URL 环境变量未设置")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 环境变量未设置")

# Neon API Key（可选）
NEON_API_KEY = os.getenv("NEON_API_KEY")
```

**配置验证**:

```python
def validate_config():
    """验证配置"""
    required_vars = ["POSTGRES_URL", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(f"缺少必需的环境变量: {', '.join(missing_vars)}")

    print("✅ 配置验证通过")
```

### 2.2 初始化向量存储

#### 2.2.1 基础配置

**基础向量存储初始化**:

```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# 初始化嵌入模型
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",  # 1536 维度
    openai_api_key=OPENAI_API_KEY
)

# 初始化向量存储
vectorstore = PGVector(
    embeddings=embeddings,
    connection=POSTGRES_URL,
    collection_name="documents",
    use_jsonb=True,  # PostgreSQL 18 JSONB 优化
    pre_delete_collection=False,  # 是否在初始化时删除现有集合
    distance_strategy="cosine"  # 距离策略：cosine, euclidean, inner_product
)

print("✅ 向量存储初始化成功")
```

**支持的模型**:

| 模型                       | 维度 | 说明               |
| -------------------------- | ---- | ------------------ |
| **text-embedding-3-small** | 1536 | 推荐用于大多数场景 |
| **text-embedding-3-large** | 3072 | 高精度场景         |
| **text-embedding-ada-002** | 1536 | 旧版本，已废弃     |

#### 2.2.2 高级配置

**高级向量存储配置**:

```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings

# 高级配置
vectorstore = PGVector(
    embeddings=embeddings,
    connection=POSTGRES_URL,
    collection_name="documents",

    # JSONB 支持（PostgreSQL 18）
    use_jsonb=True,

    # 索引类型配置
    # HNSW: 高精度，适合 <100 万数据
    # IVFFlat: 高性能，适合 >100 万数据
    index_type="HNSW",

    # HNSW 参数（高精度配置）
    hnsw_m=32,              # 每层最大连接数（默认 16）
    hnsw_ef_construction=200,  # 构建时搜索范围（默认 64）

    # IVFFlat 参数（大规模配置）
    # ivf_lists=1000,  # 聚类数量（数据量 / 1000）

    # 距离策略
    distance_strategy="cosine",  # cosine, euclidean, inner_product

    # 表名自定义
    table_name="custom_vector_store",

    # 自动初始化
    pre_delete_collection=False
)
```

**配置选择建议**:

| 数据量          | 推荐配置             | 说明     |
| --------------- | -------------------- | -------- |
| **<100 万**     | HNSW (m=16)          | 高精度   |
| **100-1000 万** | IVFFlat (lists=1000) | 高性能   |
| **>1000 万**    | IVFFlat + 分区       | 超大规模 |

### 2.3 向量搜索

#### 2.3.1 相似度搜索

**基础相似度搜索**:

```python
# 添加文档
documents = [
    Document(page_content="PostgreSQL is a powerful database"),
    Document(page_content="pgvector adds vector search capabilities"),
    Document(page_content="LangChain integrates with PostgreSQL")
]

vectorstore.add_documents(documents)
print("✅ 文档添加成功")

# 相似度搜索
query = "What is vector search?"
results = vectorstore.similarity_search(query, k=5)

for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.page_content}")
    if doc.metadata:
        print(f"   元数据: {doc.metadata}")
```

#### 2.3.2 带分数搜索

**带分数的相似度搜索**:

```python
# 相似度搜索（带分数）
results_with_scores = vectorstore.similarity_search_with_score(
    query,
    k=5
)

for doc, score in results_with_scores:
    # 余弦距离：越小越相似（0-2 范围）
    similarity = 1 - score  # 转换为相似度（0-1，越大越相似）
    print(f"[相似度: {similarity:.4f}] {doc.page_content}")
    if doc.metadata:
        print(f"    元数据: {doc.metadata}")
```

**相似度分数说明**:

| 距离类型     | 分数范围 | 说明           |
| ------------ | -------- | -------------- |
| **余弦距离** | 0-2      | 0 表示完全相似 |
| **欧氏距离** | 0-∞      | 0 表示完全相同 |
| **内积**     | -∞-∞     | 越大越相似     |

#### 2.3.3 元数据过滤

**元数据过滤搜索**:

```python
# 添加带元数据的文档
documents_with_metadata = [
    Document(
        page_content="PostgreSQL is a powerful database",
        metadata={"category": "database", "author": "PostgreSQL Team"}
    ),
    Document(
        page_content="pgvector adds vector search capabilities",
        metadata={"category": "extension", "author": "pgvector Team"}
    ),
    Document(
        page_content="LangChain integrates with PostgreSQL",
        metadata={"category": "framework", "author": "LangChain Team"}
    )
]

vectorstore.add_documents(documents_with_metadata)

# 按元数据过滤搜索
from langchain_postgres import PGVector

# 创建带过滤的检索器
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"category": "database"}  # 元数据过滤
    }
)

# 搜索
results = retriever.get_relevant_documents(query)
for doc in results:
    print(f"{doc.page_content}")
    print(f"  类别: {doc.metadata.get('category')}")
```

## 3. RAG 应用实现

### 3.1 基础 RAG

#### 3.1.1 RetrievalQA 链

**基础 RAG 实现**:

```python
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 初始化 LLM
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

# 创建检索器
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}  # 检索前 5 个相关文档
)

# 创建 RAG 链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # stuff: 将所有文档内容放入 prompt
    retriever=retriever,
    return_source_documents=True  # 返回源文档
)

# 提问
query = "What is PostgreSQL?"
result = qa_chain.invoke({"query": query})

print(f"问题: {query}")
print(f"回答: {result['result']}")
print(f"\n来源文档:")
for i, doc in enumerate(result['source_documents'], 1):
    print(f"{i}. {doc.page_content[:100]}...")
    if doc.metadata:
        print(f"   元数据: {doc.metadata}")
```

**Chain Type 说明**:

| Chain Type     | 说明                       | 适用场景           |
| -------------- | -------------------------- | ------------------ |
| **stuff**      | 将所有文档内容放入 prompt  | 文档数量少，内容短 |
| **map_reduce** | 分别处理每个文档，然后合并 | 文档数量多         |
| **refine**     | 迭代处理文档，逐步优化答案 | 需要高质量答案     |
| **map_rerank** | 对每个文档评分并排序       | 需要最佳匹配文档   |

#### 3.1.2 Prompt 模板

**自定义 Prompt 模板**:

```python
from langchain.prompts import PromptTemplate

# 自定义 Prompt 模板
prompt_template = """基于以下上下文回答问题。如果上下文中没有相关信息，请说明你不知道。

上下文：
{context}

问题：{question}

请提供准确、详细的答案："""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# 使用自定义 Prompt
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True
)

# 提问
result = qa_chain.invoke({"query": query})
```

### 3.2 高级 RAG

#### 3.2.1 文档压缩器

**文档压缩器实现**:

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI

# 文档压缩器（提取相关片段）
compressor = LLMChainExtractor.from_llm(ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
))

# 压缩检索器
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 10})  # 先检索 10 个
)

# 创建 RAG 链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=compression_retriever,  # 使用压缩检索器
    return_source_documents=True
)

# 提问
result = qa_chain.invoke({"query": query})
```

#### 3.2.2 重排序机制

**重排序实现**:

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMRerankRetriever

# 重排序检索器
rerank_retriever = LLMRerankRetriever(
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 20}),
    llm=ChatOpenAI(model="gpt-4-turbo-preview", temperature=0),
    top_n=5  # 重排序后返回前 5 个
)

# 创建 RAG 链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=rerank_retriever,
    return_source_documents=True
)
```

#### 3.2.3 对话 RAG

**对话 RAG 实现**:

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# 对话内存
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

# 对话 RAG 链
conversational_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory,
    return_source_documents=True,
    verbose=True
)

# 对话
query = "What is PostgreSQL?"
result = conversational_chain.invoke({"question": query})

print(f"问题: {query}")
print(f"回答: {result['answer']}")

# 继续对话（利用上下文）
query2 = "What are its advantages?"
result2 = conversational_chain.invoke({"question": query2})

print(f"\n问题: {query2}")
print(f"回答: {result2['answer']}")
```

## 4. Neon 分支集成

### 4.1 创建实验分支

**Neon 分支创建**:

```python
from neon import NeonClient
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings

# 初始化 Neon 客户端
neon = NeonClient(api_key=NEON_API_KEY)

# 创建实验分支
branch = neon.branches.create(
    project_id="project-id",
    name="rag-experiment-v2",
    parent_branch="main"
)

print(f"✅ 分支创建成功: {branch.name}")
print(f"连接字符串: {branch.connection_string}")

# 使用分支连接初始化向量存储
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = PGVector(
    embeddings=embeddings,
    connection=branch.connection_string,
    collection_name="documents"
)

# 在分支上进行实验
documents = [
    Document(page_content="实验文档 1"),
    Document(page_content="实验文档 2")
]
vectorstore.add_documents(documents)

# 测试查询
results = vectorstore.similarity_search("实验", k=5)
print(f"✅ 实验完成，找到 {len(results)} 个结果")
```

### 4.2 分支管理

**分支管理操作**:

```python
# 列出所有分支
branches = neon.branches.list(project_id="project-id")
for branch in branches:
    print(f"- {branch.name} ({branch.id})")

# 获取分支信息
branch_info = neon.branches.get(
    project_id="project-id",
    branch_id=branch.id
)
print(f"分支状态: {branch_info.status}")

# 删除分支（实验完成后）
# neon.branches.delete(
#     project_id="project-id",
#     branch_id=branch.id
# )
# print("✅ 分支已删除")
```

### 4.3 实验流程

**实验流程最佳实践**:

```python
class ExperimentManager:
    def __init__(self, neon_client, project_id):
        self.neon = neon_client
        self.project_id = project_id

    def create_experiment(self, experiment_name):
        """创建实验分支"""
        branch = self.neon.branches.create(
            project_id=self.project_id,
            name=f"experiment-{experiment_name}",
            parent_branch="main"
        )
        return branch

    def run_experiment(self, branch, documents, query):
        """运行实验"""
        vectorstore = PGVector(
            embeddings=embeddings,
            connection=branch.connection_string,
            collection_name="documents"
        )

        # 添加文档
        vectorstore.add_documents(documents)

        # 测试查询
        results = vectorstore.similarity_search(query, k=5)

        return {
            "branch_id": branch.id,
            "results_count": len(results),
            "results": results
        }

    def cleanup_experiment(self, branch_id):
        """清理实验分支"""
        self.neon.branches.delete(
            project_id=self.project_id,
            branch_id=branch_id
        )
        print("✅ 实验分支已清理")

# 使用
manager = ExperimentManager(neon, "project-id")

# 创建实验
branch = manager.create_experiment("rag-v2")

# 运行实验
results = manager.run_experiment(branch, documents, "测试查询")

# 评估结果
if results["results_count"] > 0:
    print("✅ 实验成功")
    # 合并到主分支或保留
else:
    print("❌ 实验失败")
    # 清理分支
    manager.cleanup_experiment(branch.id)
```

## 5. 混合搜索实现

### 5.1 全文+向量搜索

#### 5.1.1 BM25 检索器

**BM25 全文检索器**:

```python
from langchain.retrievers import BM25Retriever
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 准备文档
documents = [
    Document(page_content="PostgreSQL is a powerful database"),
    Document(page_content="pgvector adds vector search capabilities"),
    Document(page_content="LangChain integrates with PostgreSQL")
]

# 文档切分
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(documents)

# BM25 检索器
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 5  # 检索前 5 个结果

# 全文搜索
results = bm25_retriever.get_relevant_documents("vector search")
for doc in results:
    print(doc.page_content)
```

#### 5.1.2 向量检索器

**向量检索器**:

```python
# 向量检索器
vector_retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}  # 检索前 5 个结果
)

# 向量搜索
results = vector_retriever.get_relevant_documents("vector search")
for doc in results:
    print(doc.page_content)
```

### 5.2 RRF 融合算法

#### 5.2.1 Ensemble Retriever

**集成检索器（RRF 融合）**:

```python
from langchain.retrievers import EnsembleRetriever

# 集成检索器（RRF 融合）
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6]  # 全文搜索 40%，向量搜索 60%
)

# 混合搜索
results = ensemble_retriever.get_relevant_documents("vector search")
for doc in results:
    print(doc.page_content)
    print(f"  分数: {doc.metadata.get('score', 'N/A')}")
```

**RRF 算法说明**:

- **RRF 分数 = 1 / (k + rank)**
- k = 60（默认值）
- 分数越高，相关性越高

#### 5.2.2 权重配置

**权重配置建议**:

| 场景           | BM25 权重 | 向量权重 | 说明           |
| -------------- | --------- | -------- | -------------- |
| **关键词搜索** | 0.6       | 0.4      | 全文搜索更重要 |
| **语义搜索**   | 0.4       | 0.6      | 向量搜索更重要 |
| **平衡搜索**   | 0.5       | 0.5      | 两者平衡       |

**自定义权重**:

```python
# 动态权重（根据查询类型）
def get_retriever_weights(query_type):
    if query_type == "keyword":
        return [0.6, 0.4]  # BM25 权重更高
    elif query_type == "semantic":
        return [0.4, 0.6]  # 向量权重更高
    else:
        return [0.5, 0.5]  # 平衡

# 使用
weights = get_retriever_weights("semantic")
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=weights
)
```

## 6. 完整 RAG 流程

### 6.1 文档加载和向量化

#### 6.1.1 文档加载器

**支持的文档格式**:

| 格式         | 加载器                     | 说明       |
| ------------ | -------------------------- | ---------- |
| **文本**     | TextLoader                 | .txt 文件  |
| **PDF**      | PyPDFLoader                | PDF 文件   |
| **Word**     | Docx2txtLoader             | .docx 文件 |
| **Markdown** | UnstructuredMarkdownLoader | .md 文件   |
| **网页**     | WebBaseLoader              | HTML/网页  |
| **目录**     | DirectoryLoader            | 批量加载   |

**文档加载示例**:

```python
from langchain.document_loaders import TextLoader, DirectoryLoader

# 单个文件加载
loader = TextLoader("document.txt", encoding="utf-8")
documents = loader.load()

# 目录批量加载
loader = DirectoryLoader(
    "./documents",
    glob="**/*.txt",
    loader_cls=TextLoader
)
documents = loader.load()

print(f"✅ 加载了 {len(documents)} 个文档")
```

#### 6.1.2 文本切分

**文本切分策略**:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 文本切分器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # 每个块的大小（字符数）
    chunk_overlap=200,    # 块之间的重叠（保持上下文）
    length_function=len,  # 长度计算函数
    separators=["\n\n", "\n", " ", ""]  # 分隔符优先级
)

# 切分文档
chunks = text_splitter.split_documents(documents)
print(f"✅ 切分为 {len(chunks)} 个块")

# 添加块元数据
for i, chunk in enumerate(chunks):
    chunk.metadata["chunk_id"] = i
    chunk.metadata["chunk_size"] = len(chunk.page_content)
```

**切分参数建议**:

| 文档类型     | chunk_size | chunk_overlap | 说明           |
| ------------ | ---------- | ------------- | -------------- |
| **技术文档** | 1000       | 200           | 保持代码块完整 |
| **长篇文章** | 2000       | 300           | 保持段落完整   |
| **对话记录** | 500        | 100           | 保持对话完整   |

#### 6.1.3 向量化存储

**批量向量化存储**:

```python
def batch_add_documents(vectorstore, documents, batch_size=100):
    """批量添加文档"""
    total = len(documents)
    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]
        vectorstore.add_documents(batch)
        print(f"✅ 已处理 {min(i + batch_size, total)}/{total} 个文档")

    print(f"✅ 所有文档添加完成")

# 使用
batch_add_documents(vectorstore, chunks, batch_size=100)
```

### 6.2 RAG 链配置

#### 6.2.1 ConversationalRetrievalChain

**对话 RAG 链配置**:

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# 对话内存
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

# 对话 RAG 链
conversational_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(
        search_kwargs={"k": 5}
    ),
    memory=memory,
    return_source_documents=True,
    verbose=True,
    max_tokens_limit=4000  # 限制 prompt 长度
)

# 对话
query = "What is PostgreSQL?"
result = conversational_chain.invoke({"question": query})

print(f"问题: {query}")
print(f"回答: {result['answer']}")
```

#### 6.2.2 对话内存管理

**不同内存策略**:

```python
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory
)

# 策略 1: 完整对话历史（适合短对话）
memory1 = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# 策略 2: 对话摘要（适合长对话）
memory2 = ConversationSummaryMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True
)

# 策略 3: 摘要缓冲（平衡）
memory3 = ConversationSummaryBufferMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True,
    max_token_limit=2000  # 超过此长度则摘要
)

# 使用
conversational_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory3,  # 选择合适的内存策略
    return_source_documents=True
)
```

## 7. 性能优化

### 7.1 批量处理

**批量处理优化**:

```python
import asyncio
from typing import List

# 异步批量添加
async def async_batch_add(vectorstore, documents: List[Document], batch_size=100):
    """异步批量添加文档"""
    total = len(documents)
    tasks = []

    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]
        # 异步添加
        task = vectorstore.aadd_documents(batch)
        tasks.append(task)

    # 等待所有任务完成
    await asyncio.gather(*tasks)
    print(f"✅ 已处理 {total} 个文档")

# 使用
# await async_batch_add(vectorstore, chunks, batch_size=100)
```

### 7.2 缓存策略

**LLM 缓存**:

```python
from langchain.cache import InMemoryCache, SQLiteCache
from langchain.globals import set_llm_cache

# 内存缓存（开发环境）
set_llm_cache(InMemoryCache())

# SQLite 缓存（生产环境）
set_llm_cache(SQLiteCache(database_path=".langchain.db"))

# 使用缓存
result1 = qa_chain.invoke({"query": query})  # 第一次查询
result2 = qa_chain.invoke({"query": query})  # 使用缓存（更快）
```

**向量搜索缓存**:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_similarity_search(query: str, k: int = 5):
    """缓存向量搜索结果"""
    return vectorstore.similarity_search(query, k=k)

# 使用
results = cached_similarity_search("PostgreSQL", k=5)
```

### 7.3 异步处理

**异步 RAG**:

```python
import asyncio

# 异步 RAG
async def async_rag(query: str):
    """异步 RAG 查询"""
    # 异步检索
    docs = await vectorstore.asimilarity_search(query, k=5)

    # 异步 LLM 调用
    response = await llm.ainvoke(f"基于以下上下文回答: {docs}")

    return response

# 使用
# result = await async_rag("What is PostgreSQL?")
```

## 8. 最佳实践

### 8.1 配置最佳实践

**配置建议**:

1. **向量维度**: 根据 Embedding 模型选择（text-embedding-3-small: 1536）
2. **索引类型**:
   - **<100 万数据**: HNSW
   - **>100 万数据**: IVFFlat
3. **距离策略**: 文本向量使用 **cosine**
4. **chunk_size**: 根据文档类型选择（技术文档: 1000，长文章: 2000）

### 8.2 性能最佳实践

**性能优化建议**:

1. **批量操作**: 使用批量添加而不是逐个添加
2. **异步处理**: 对于大量文档，使用异步处理
3. **缓存策略**: 使用 LLM 缓存减少 API 调用
4. **索引优化**: 根据数据量选择合适的索引类型和参数

### 8.3 RAG 最佳实践

**RAG 应用建议**:

1. **文档切分**: 使用合适的 chunk_size 和 chunk_overlap
2. **检索策略**: 根据查询类型选择向量搜索或混合搜索
3. **Prompt 优化**: 使用清晰的 Prompt 模板提高答案质量
4. **重排序**: 对关键查询使用重排序提高准确性

## 9. 常见问题

### 9.1 依赖问题

**常见依赖问题**:

1. **版本冲突**:

   ```bash
   pip install --upgrade langchain langchain-postgres
   ```

2. **缺少依赖**:

   ```bash
   pip install psycopg2-binary pgvector
   ```

### 9.2 配置问题

**常见配置问题**:

1. **维度不匹配**: 确保 Embedding 模型维度与配置一致
2. **连接字符串错误**: 检查 PostgreSQL 连接配置
3. **索引类型错误**: 根据数据量选择合适的索引类型

### 9.3 性能问题

**性能问题排查**:

1. **查询慢**: 检查索引是否创建，优化查询参数
2. **内存不足**: 使用批量操作，减少批次大小
3. **API 调用过多**: 使用缓存策略减少 API 调用

## 10. 参考资料

### 10.1 官方文档

- [LangChain 官方文档](https://python.langchain.com/) - LangChain Documentation
- [LangChain PostgreSQL 集成](https://python.langchain.com/docs/integrations/vectorstores/pgvector) -
  PGVector Integration

### 10.2 技术文档

- [pgvector 核心原理](../../01-向量与混合搜索/技术原理/pgvector核心原理.md) - pgvector Core
  Principles
- [混合搜索 RRF 算法](../../01-向量与混合搜索/技术原理/混合搜索RRF算法.md) - RRF Algorithm

### 10.3 相关资源

- [LangChain RAG 指南](https://python.langchain.com/docs/use_cases/question_answering/) - RAG Guide
- [Neon 分支文档](https://neon.tech/docs/guides/branching) - Neon Branching

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
**文档编号**: 07-01-02
