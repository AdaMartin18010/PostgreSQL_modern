# LangChain 集成实践

> **更新时间**: 2025 年 11 月 1 日  
> **技术版本**: LangChain 0.1+ / Neon v3.0+  
> **文档编号**: 03-04-03

## 📑 目录

- [LangChain 集成实践](#langchain-集成实践)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. 集成方案](#2-集成方案)
    - [2.1 环境配置](#21-环境配置)
    - [2.2 向量存储配置](#22-向量存储配置)
  - [3. 实现示例](#3-实现示例)
    - [3.1 完整 RAG 流程](#31-完整-rag-流程)
    - [3.2 多分支实验](#32-多分支实验)
  - [4. 最佳实践](#4-最佳实践)
  - [5. 参考资料](#5-参考资料)

---

## 1. 概述

LangChain 集成 Neon 分支，实现 RAG 应用的数据版本管理和实验隔离。

---

## 2. 集成方案

### 2.1 环境配置

```python
import os
from neon import NeonClient
from langchain.vectorstores import PGVector
from langchain.embeddings import OpenAIEmbeddings

# Neon 客户端
neon_client = NeonClient(api_key=os.getenv('NEON_API_KEY'))

# 创建实验分支
branch = neon_client.branches.create(
    project_id=os.getenv('NEON_PROJECT_ID'),
    name='experiment-rag-v2'
)

# 获取连接字符串
CONNECTION_STRING = branch.connection_string
```

### 2.2 向量存储配置

```python
# 创建向量存储
vectorstore = PGVector.from_documents(
    documents=documents,
    embedding=OpenAIEmbeddings(),
    connection_string=CONNECTION_STRING,
    collection_name='documents_v2'
)
```

---

## 3. 实现示例

### 3.1 完整 RAG 流程

```python
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# 创建检索器
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)

# 创建 RAG 链
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=retriever
)

# 执行查询
result = qa_chain.run("What is RAG?")
print(result)
```

### 3.2 多分支实验

```python
class RAGExperiment:
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        self.branch = self.create_branch(experiment_name)
        self.vectorstore = self.setup_vectorstore()

    def create_branch(self, name):
        """创建实验分支"""
        return neon_client.branches.create(
            project_id=PROJECT_ID,
            name=name
        )

    def setup_vectorstore(self):
        """设置向量存储"""
        return PGVector.from_documents(
            documents=self.load_documents(),
            embedding=OpenAIEmbeddings(),
            connection_string=self.branch.connection_string
        )

    def run_experiment(self, queries):
        """运行实验"""
        results = []
        for query in queries:
            result = self.qa_chain.run(query)
            results.append(result)
        return results
```

---

## 4. 最佳实践

1. **分支管理**: 为每个实验创建独立分支
1. **版本控制**: 使用版本标签管理稳定版本
1. **性能监控**: 监控不同版本的性能指标
1. **清理策略**: 及时清理不需要的实验分支

---

## 5. 参考资料

- [RAG 架构设计](./RAG架构设计.md)
- [数据版本控制策略](./数据版本控制策略.md)
- [LangChain 集成](../../07-技术堆栈/开发工具链/LangChain集成.md)

---

**最后更新**: 2025 年 11 月 1 日  
**维护者**: PostgreSQL Modern Team
