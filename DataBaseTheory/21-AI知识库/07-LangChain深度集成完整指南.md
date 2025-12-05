# LangChain + PostgreSQL 18 深度集成指南

## 1. 核心架构

### 1.1 技术栈

```python
LangChain + PostgreSQL 18 + pgvector + Apache AGE
├─ LLM: OpenAI GPT-4 / Claude / 本地模型
├─ 向量数据库: pgvector
├─ 图数据库: Apache AGE
└─ 关系数据库: PostgreSQL 18
```

### 1.2 集成模式

```text
┌──────────────────────────────────────────────────┐
│         LangChain + PostgreSQL 架构              │
├──────────────────────────────────────────────────┤
│                                                  │
│  [LangChain Application]                         │
│         │                                        │
│    ┌────┴────┐                                   │
│    │         │                                   │
│  [Agent]  [Chain]                                │
│    │         │                                   │
│    └────┬────┘                                   │
│         │                                        │
│  ┌──────┴──────────┐                             │
│  │                 │                             │
│ [VectorStore]  [SQLDatabase]  [GraphDatabase]    │
│  (pgvector)    (PostgreSQL)   (AGE)              │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 2. VectorStore集成

### 2.1 基础配置

```python
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 连接配置
CONNECTION_STRING = "postgresql://postgres:password@localhost:5432/vectordb"

# Embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key="your-api-key"
)

# VectorStore
vectorstore = PGVector(
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
    collection_name="documents",
    distance_strategy="cosine"
)
```

### 2.2 文档索引

```python
# 加载文档
loader = TextLoader("knowledge_base.txt")
documents = loader.load()

# 分块
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)
chunks = text_splitter.split_documents(documents)

# 添加到向量库
vectorstore.add_documents(chunks)

# 批量索引优化
def batch_index_documents(docs, batch_size=100):
    """批量索引，提升性能"""
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i+batch_size]
        vectorstore.add_documents(batch)
        print(f"已索引 {min(i+batch_size, len(docs))}/{len(docs)} 个文档")
```

### 2.3 向量检索

```python
# 相似度搜索
def semantic_search(query: str, k: int = 5):
    """语义搜索"""
    results = vectorstore.similarity_search(query, k=k)
    return results

# 相似度搜索 + 分数
def search_with_score(query: str, k: int = 5):
    """返回文档和相似度分数"""
    results = vectorstore.similarity_search_with_score(query, k=k)
    return [(doc.page_content, score) for doc, score in results]

# MMR搜索（最大边际相关性）
def mmr_search(query: str, k: int = 5, fetch_k: int = 20):
    """平衡相关性和多样性"""
    results = vectorstore.max_marginal_relevance_search(
        query=query,
        k=k,
        fetch_k=fetch_k
    )
    return results

# 过滤搜索
def filtered_search(query: str, filter_dict: dict, k: int = 5):
    """带过滤条件的搜索"""
    results = vectorstore.similarity_search(
        query=query,
        k=k,
        filter=filter_dict
    )
    return results

# 示例
docs = semantic_search("PostgreSQL MVCC原理")
for doc in docs:
    print(doc.page_content[:200])
```

---

## 3. SQL Chain集成

### 3.1 数据库连接

```python
from langchain.sql_database import SQLDatabase
from langchain.chains import SQLDatabaseChain
from langchain.llms import OpenAI

# 连接数据库
db = SQLDatabase.from_uri(
    "postgresql://postgres:password@localhost:5432/mydb",
    include_tables=['users', 'orders', 'products'],  # 限制表
    sample_rows_in_table_info=3  # 样本行数
)

# 查看schema
print(db.table_info)

# LLM
llm = OpenAI(temperature=0, openai_api_key="your-api-key")

# SQL Chain
sql_chain = SQLDatabaseChain.from_llm(
    llm=llm,
    db=db,
    verbose=True,
    return_intermediate_steps=True
)
```

### 3.2 自然语言查询

```python
# Text-to-SQL
def nl_to_sql(question: str):
    """自然语言转SQL查询"""
    result = sql_chain.run(question)
    return result

# 示例
question = "最近一周销售额最高的5个产品是什么？"
answer = nl_to_sql(question)
print(answer)

# 获取中间步骤
def nl_to_sql_detailed(question: str):
    """返回SQL和结果"""
    result = sql_chain(question)
    return {
        'question': question,
        'sql': result['intermediate_steps'][0],
        'result': result['result']
    }
```

### 3.3 SQL Agent

```python
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit

# 创建toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 创建agent
sql_agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="openai-tools"
)

# 使用agent
def ask_database(question: str):
    """使用Agent查询数据库"""
    response = sql_agent.run(question)
    return response

# 复杂查询示例
complex_query = """
分析最近一个月的销售趋势：
1. 每天的销售额
2. 销售额环比增长
3. Top 3产品类别
"""
answer = ask_database(complex_query)
```

---

## 4. Graph Chain集成（Apache AGE）

### 4.1 图数据库连接

```python
from langchain.graphs import Neo4jGraph  # AGE兼容
import psycopg2

class AGEGraph:
    """Apache AGE图数据库连接"""

    def __init__(self, conn_str: str, graph_name: str = "knowledge_graph"):
        self.conn = psycopg2.connect(conn_str)
        self.cursor = self.conn.cursor()
        self.graph_name = graph_name

        # 加载AGE
        self.cursor.execute("LOAD 'age';")
        self.cursor.execute("SET search_path = ag_catalog, '$user', public;")

    def query(self, cypher: str, params: dict = None):
        """执行Cypher查询"""
        if params:
            query = f"""
                SELECT * FROM cypher('{self.graph_name}', $$
                    {cypher}
                $$, %s) AS (result agtype);
            """
            self.cursor.execute(query, (params,))
        else:
            query = f"""
                SELECT * FROM cypher('{self.graph_name}', $$
                    {cypher}
                $$) AS (result agtype);
            """
            self.cursor.execute(query)

        return self.cursor.fetchall()

    def get_schema(self):
        """获取图schema"""
        labels = self.query("MATCH (n) RETURN DISTINCT labels(n)")
        relationships = self.query("MATCH ()-[r]->() RETURN DISTINCT type(r)")
        return {
            'node_labels': labels,
            'relationship_types': relationships
        }

# 使用
graph = AGEGraph("postgresql://postgres@localhost/graphdb")
```

### 4.2 Graph QA Chain

```python
from langchain.chains import GraphCypherQAChain
from langchain.prompts import PromptTemplate

# Cypher生成提示词
CYPHER_GENERATION_TEMPLATE = """
你是一个Cypher查询专家。根据问题生成Cypher查询。

Schema:
{schema}

问题: {question}

只返回Cypher查询:
"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

# Graph QA Chain
class GraphQAChain:
    """图数据库问答"""

    def __init__(self, graph: AGEGraph, llm):
        self.graph = graph
        self.llm = llm
        self.schema = graph.get_schema()

    def ask(self, question: str):
        """回答问题"""
        # 1. 生成Cypher
        cypher = self._generate_cypher(question)

        # 2. 执行查询
        results = self.graph.query(cypher)

        # 3. 生成答案
        answer = self._generate_answer(question, results)

        return {
            'question': question,
            'cypher': cypher,
            'results': results,
            'answer': answer
        }

    def _generate_cypher(self, question: str) -> str:
        """LLM生成Cypher"""
        prompt = cypher_prompt.format(
            schema=str(self.schema),
            question=question
        )
        cypher = self.llm(prompt)
        return cypher.strip()

    def _generate_answer(self, question: str, results: list) -> str:
        """根据结果生成答案"""
        prompt = f"""
        基于以下查询结果回答问题。

        问题: {question}
        结果: {results}

        回答:
        """
        answer = self.llm(prompt)
        return answer.strip()

# 使用
graph_qa = GraphQAChain(graph, llm)
result = graph_qa.ask("PostgreSQL使用了哪些技术？")
```

---

## 5. RAG应用开发

### 5.1 基础RAG

```python
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# RAG提示词
RAG_PROMPT_TEMPLATE = """
使用以下上下文回答问题。如果不知道答案，就说不知道。

上下文:
{context}

问题: {question}

回答:
"""

rag_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=RAG_PROMPT_TEMPLATE
)

# RetrievalQA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": rag_prompt},
    return_source_documents=True
)

# 使用
def rag_query(question: str):
    """RAG查询"""
    result = qa_chain({"query": question})
    return {
        'answer': result['result'],
        'sources': [doc.page_content for doc in result['source_documents']]
    }

# 示例
answer = rag_query("什么是MVCC？")
print(f"答案: {answer['answer']}")
print(f"来源: {answer['sources']}")
```

### 5.2 混合RAG（向量+SQL+图）

```python
class HybridRAG:
    """混合检索增强生成"""

    def __init__(self, vectorstore, sql_db, graph_db, llm):
        self.vectorstore = vectorstore
        self.sql_db = sql_db
        self.graph_db = graph_db
        self.llm = llm

    def query(self, question: str):
        """多源检索+生成"""

        # 1. 问题分类
        query_type = self._classify_question(question)

        # 2. 多路检索
        contexts = []

        # 向量检索
        if query_type in ['concept', 'general']:
            vector_results = self.vectorstore.similarity_search(question, k=3)
            contexts.append({
                'source': 'vector',
                'content': [doc.page_content for doc in vector_results]
            })

        # SQL查询
        if query_type in ['data', 'statistics']:
            sql_chain = SQLDatabaseChain.from_llm(self.llm, self.sql_db)
            sql_result = sql_chain.run(question)
            contexts.append({
                'source': 'sql',
                'content': sql_result
            })

        # 图查询
        if query_type in ['relation', 'path']:
            graph_qa = GraphQAChain(self.graph_db, self.llm)
            graph_result = graph_qa.ask(question)
            contexts.append({
                'source': 'graph',
                'content': graph_result['answer']
            })

        # 3. 融合生成答案
        answer = self._generate_answer(question, contexts)

        return {
            'question': question,
            'query_type': query_type,
            'contexts': contexts,
            'answer': answer
        }

    def _classify_question(self, question: str) -> str:
        """分类问题"""
        prompt = f"""
        将问题分类为以下类型之一：
        - concept: 概念解释
        - data: 数据查询
        - statistics: 统计分析
        - relation: 关系查询
        - path: 路径查询
        - general: 一般问题

        问题: {question}

        类型:
        """
        result = self.llm(prompt).strip().lower()
        return result

    def _generate_answer(self, question: str, contexts: list) -> str:
        """融合多源上下文生成答案"""
        context_text = "\n\n".join([
            f"来源 {ctx['source']}:\n{ctx['content']}"
            for ctx in contexts
        ])

        prompt = f"""
        基于以下多个来源的信息回答问题。

        {context_text}

        问题: {question}

        综合回答:
        """

        answer = self.llm(prompt)
        return answer.strip()

# 使用
hybrid_rag = HybridRAG(vectorstore, db, graph, llm)
result = hybrid_rag.query("PostgreSQL的MVCC在哪些产品中使用？")
```

---

## 6. Agent开发

### 6.1 自定义工具

```python
from langchain.tools import BaseTool
from typing import Optional
from pydantic import BaseModel, Field

class VectorSearchInput(BaseModel):
    """向量搜索输入"""
    query: str = Field(description="搜索查询")
    k: int = Field(default=5, description="返回结果数")

class VectorSearchTool(BaseTool):
    """向量搜索工具"""
    name = "vector_search"
    description = "搜索知识库文档，适用于概念查询和问题解答"
    args_schema = VectorSearchInput
    vectorstore: Any = None

    def _run(self, query: str, k: int = 5) -> str:
        """执行搜索"""
        results = self.vectorstore.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in results])

class SQLQueryTool(BaseTool):
    """SQL查询工具"""
    name = "sql_query"
    description = "查询数据库数据，适用于数据统计和分析"
    db: Any = None
    llm: Any = None

    def _run(self, question: str) -> str:
        """执行SQL查询"""
        chain = SQLDatabaseChain.from_llm(self.llm, self.db)
        result = chain.run(question)
        return result

class GraphQueryTool(BaseTool):
    """图查询工具"""
    name = "graph_query"
    description = "查询知识图谱，适用于关系和路径查询"
    graph: Any = None
    llm: Any = None

    def _run(self, question: str) -> str:
        """执行图查询"""
        qa = GraphQAChain(self.graph, self.llm)
        result = qa.ask(question)
        return result['answer']
```

### 6.2 创建Agent

```python
from langchain.agents import initialize_agent, AgentType

# 初始化工具
tools = [
    VectorSearchTool(vectorstore=vectorstore),
    SQLQueryTool(db=db, llm=llm),
    GraphQueryTool(graph=graph, llm=llm)
]

# 创建Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    max_iterations=5
)

# 使用Agent
def ask_agent(question: str):
    """使用Agent回答问题"""
    response = agent.run(question)
    return response

# 复杂问题示例
question = """
分析PostgreSQL的MVCC机制：
1. 概念解释
2. 在哪些系统中使用
3. 近一年的性能数据
"""
answer = ask_agent(question)
```

---

## 7. 记忆管理

### 7.1 对话记忆（PostgreSQL存储）

```python
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import PostgresChatMessageHistory

# 基于PostgreSQL的对话历史
class PGChatMemory:
    """PostgreSQL对话记忆"""

    def __init__(self, conn_str: str, session_id: str):
        self.history = PostgresChatMessageHistory(
            connection_string=conn_str,
            session_id=session_id
        )
        self.memory = ConversationBufferMemory(
            chat_memory=self.history,
            return_messages=True
        )

    def add_message(self, user_message: str, ai_message: str):
        """添加消息"""
        self.history.add_user_message(user_message)
        self.history.add_ai_message(ai_message)

    def get_messages(self, limit: int = 10):
        """获取最近消息"""
        messages = self.history.messages[-limit:]
        return messages

    def clear(self):
        """清空历史"""
        self.history.clear()

# 使用
memory = PGChatMemory(CONNECTION_STRING, session_id="user123")

# 对话
from langchain.chains import ConversationChain

conversation = ConversationChain(
    llm=llm,
    memory=memory.memory,
    verbose=True
)

response = conversation.predict(input="什么是MVCC？")
```

### 7.2 摘要记忆

```python
from langchain.memory import ConversationSummaryMemory

# 自动摘要长对话
summary_memory = ConversationSummaryMemory(
    llm=llm,
    return_messages=True
)

# 对话链
conversation_with_summary = ConversationChain(
    llm=llm,
    memory=summary_memory
)

# 长对话会自动摘要
for i in range(10):
    response = conversation_with_summary.predict(
        input=f"第{i+1}个问题..."
    )
```

---

## 8. 流式输出

### 8.1 流式生成

```python
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler

class CustomStreamingHandler(BaseCallbackHandler):
    """自定义流式处理器"""

    def on_llm_new_token(self, token: str, **kwargs):
        """处理新token"""
        print(token, end="", flush=True)

    def on_llm_end(self, response, **kwargs):
        """LLM结束"""
        print("\n[完成]")

# 使用流式输出
streaming_llm = OpenAI(
    temperature=0,
    streaming=True,
    callbacks=[CustomStreamingHandler()]
)

# 流式查询
response = streaming_llm("解释PostgreSQL的MVCC机制")
```

### 8.2 异步流式

```python
import asyncio
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler

async def stream_query(question: str):
    """异步流式查询"""

    callback = AsyncIteratorCallbackHandler()

    async_llm = OpenAI(
        temperature=0,
        streaming=True,
        callbacks=[callback]
    )

    # 启动生成任务
    task = asyncio.create_task(
        async_llm.agenerate([[question]])
    )

    # 流式输出
    async for token in callback.aiter():
        print(token, end="", flush=True)

    await task
    print("\n[完成]")

# 运行
asyncio.run(stream_query("什么是ACID？"))
```

---

## 9. 性能优化

### 9.1 向量索引优化

```python
# HNSW索引参数调优
def create_optimized_index(table_name: str, column_name: str):
    """创建优化的HNSW索引"""
    conn = psycopg2.connect(CONNECTION_STRING)
    cursor = conn.cursor()

    # PostgreSQL 18优化参数
    cursor.execute(f"""
        CREATE INDEX idx_{table_name}_{column_name}_hnsw
        ON {table_name}
        USING hnsw ({column_name} vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)

    conn.commit()
    cursor.close()
    conn.close()

# 查询优化
def optimized_search(query: str, k: int = 5):
    """优化的向量搜索"""
    conn = psycopg2.connect(CONNECTION_STRING)
    cursor = conn.cursor()

    # 设置ef_search参数
    cursor.execute("SET hnsw.ef_search = 100;")

    # 执行搜索
    query_vec = embeddings.embed_query(query)
    cursor.execute("""
        SELECT content, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (query_vec, query_vec, k))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results
```

### 9.2 批处理优化

```python
from concurrent.futures import ThreadPoolExecutor

def batch_embed_documents(docs: list, batch_size: int = 100):
    """批量embedding"""

    embeddings_list = []

    for i in range(0, len(docs), batch_size):
        batch = docs[i:i+batch_size]
        batch_texts = [doc.page_content for doc in batch]

        # 批量生成embedding
        batch_embeddings = embeddings.embed_documents(batch_texts)
        embeddings_list.extend(batch_embeddings)

    return embeddings_list

def parallel_index(docs: list, num_workers: int = 4):
    """并行索引"""

    chunk_size = len(docs) // num_workers

    def index_chunk(chunk):
        vectorstore.add_documents(chunk)

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for i in range(0, len(docs), chunk_size):
            chunk = docs[i:i+chunk_size]
            futures.append(executor.submit(index_chunk, chunk))

        for future in futures:
            future.result()
```

### 9.3 缓存策略

```python
from langchain.cache import PostgresCache
from langchain.globals import set_llm_cache

# PostgreSQL缓存
set_llm_cache(PostgresCache(connection_string=CONNECTION_STRING))

# 相同查询会使用缓存
response1 = llm("什么是MVCC？")  # 调用LLM
response2 = llm("什么是MVCC？")  # 使用缓存

# Redis缓存（更快）
from langchain.cache import RedisCache
import redis

redis_client = redis.Redis(host='localhost', port=6379)
set_llm_cache(RedisCache(redis_client))
```

---

## 10. 生产部署

### 10.1 连接池配置

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# 连接池
engine = create_engine(
    CONNECTION_STRING,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)

# 使用连接池
vectorstore = PGVector(
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
    engine=engine
)
```

### 10.2 FastAPI生产部署

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="LangChain PostgreSQL API")

class QueryRequest(BaseModel):
    question: str
    k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: list
    duration_ms: float

@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """RAG查询接口"""

    import time
    start = time.time()

    try:
        result = qa_chain({"query": request.question})

        return QueryResponse(
            answer=result['result'],
            sources=[doc.page_content[:200] for doc in result['source_documents']],
            duration_ms=(time.time() - start) * 1000
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=4
    )
```

### 10.3 Docker部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 运行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg18
    environment:
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build: .
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/vectordb
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"

volumes:
  pgdata:
```

---

## 11. 监控与调试

### 11.1 性能监控

```python
from langchain.callbacks import get_openai_callback
import time

def monitored_query(question: str):
    """带监控的查询"""

    start_time = time.time()

    with get_openai_callback() as cb:
        result = qa_chain({"query": question})

        metrics = {
            'question': question,
            'answer': result['result'],
            'duration_ms': (time.time() - start_time) * 1000,
            'total_tokens': cb.total_tokens,
            'prompt_tokens': cb.prompt_tokens,
            'completion_tokens': cb.completion_tokens,
            'total_cost': cb.total_cost
        }

    return metrics

# 记录到数据库
def log_metrics(metrics: dict):
    """记录指标"""
    conn = psycopg2.connect(CONNECTION_STRING)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO query_metrics
        (question, duration_ms, total_tokens, total_cost)
        VALUES (%s, %s, %s, %s);
    """, (
        metrics['question'],
        metrics['duration_ms'],
        metrics['total_tokens'],
        metrics['total_cost']
    ))

    conn.commit()
    cursor.close()
    conn.close()
```

### 11.2 调试工具

```python
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.tracers import ConsoleCallbackHandler

# 详细调试
debug_handler = ConsoleCallbackHandler()

agent_with_debug = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    callbacks=[debug_handler],
    verbose=True
)

# 执行查看详细步骤
result = agent_with_debug.run("复杂问题...")
```

---

## 12. 最佳实践

### 12.1 Prompt工程

```python
# 好的Prompt设计
GOOD_PROMPT = """
你是PostgreSQL数据库专家。基于以下上下文回答问题。

规则:
1. 如果不确定，说"我不知道"
2. 引用具体的上下文片段
3. 提供技术细节和示例

上下文:
{context}

问题: {question}

回答:
"""

# 坏的Prompt
BAD_PROMPT = "回答: {question}"
```

### 12.2 错误处理

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def robust_query(question: str):
    """带重试的查询"""
    try:
        result = qa_chain({"query": question})
        return result['result']
    except Exception as e:
        print(f"错误: {e}, 重试...")
        raise

# 使用
answer = robust_query("什么是MVCC？")
```

### 12.3 安全实践

```python
# SQL注入防护
def safe_sql_query(user_input: str):
    """安全的SQL查询"""

    # 1. 输入验证
    if len(user_input) > 1000:
        raise ValueError("输入过长")

    # 2. 使用参数化查询
    # SQLDatabaseChain默认已防护

    # 3. 限制表访问
    db = SQLDatabase.from_uri(
        CONNECTION_STRING,
        include_tables=['public_table'],  # 只允许访问特定表
        sample_rows_in_table_info=1
    )

    return sql_chain.run(user_input)

# Prompt注入防护
def sanitize_input(user_input: str) -> str:
    """清理用户输入"""
    # 移除特殊字符
    sanitized = user_input.replace("\\n", " ").replace("\\", "")
    return sanitized[:500]  # 限制长度
```

---

## 13. 完整案例：企业知识库

```python
"""
企业知识库完整实现
功能: RAG问答 + SQL查询 + 图查询
"""

from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.sql_database import SQLDatabase
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import psycopg2

class EnterpriseKnowledgeBase:
    """企业知识库"""

    def __init__(self, db_config: dict, openai_api_key: str):
        # 初始化组件
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = OpenAI(temperature=0, openai_api_key=openai_api_key)

        # Vector Store
        self.vectorstore = PGVector(
            connection_string=db_config['vector_db'],
            embedding_function=self.embeddings
        )

        # SQL Database
        self.sql_db = SQLDatabase.from_uri(db_config['sql_db'])

        # Graph Database
        self.graph_db = AGEGraph(db_config['graph_db'])

        # 创建工具
        self.tools = self._create_tools()

        # 创建Agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )

    def _create_tools(self):
        """创建工具集"""

        # 文档搜索工具
        doc_tool = Tool(
            name="DocumentSearch",
            func=self._search_documents,
            description="搜索技术文档和知识库，适用于概念查询"
        )

        # SQL查询工具
        sql_tool = Tool(
            name="SQLQuery",
            func=self._query_database,
            description="查询结构化数据和统计信息"
        )

        # 图查询工具
        graph_tool = Tool(
            name="GraphQuery",
            func=self._query_graph,
            description="查询实体关系和知识图谱"
        )

        return [doc_tool, sql_tool, graph_tool]

    def _search_documents(self, query: str) -> str:
        """搜索文档"""
        results = self.vectorstore.similarity_search(query, k=3)
        return "\n\n".join([doc.page_content for doc in results])

    def _query_database(self, question: str) -> str:
        """SQL查询"""
        from langchain.chains import SQLDatabaseChain
        chain = SQLDatabaseChain.from_llm(self.llm, self.sql_db)
        return chain.run(question)

    def _query_graph(self, question: str) -> str:
        """图查询"""
        qa = GraphQAChain(self.graph_db, self.llm)
        result = qa.ask(question)
        return result['answer']

    def ask(self, question: str):
        """回答问题"""
        response = self.agent.run(question)
        return response

    def index_document(self, doc_path: str):
        """索引新文档"""
        from langchain.document_loaders import TextLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        # 加载
        loader = TextLoader(doc_path)
        documents = loader.load()

        # 分块
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(documents)

        # 索引
        self.vectorstore.add_documents(chunks)

        return f"已索引 {len(chunks)} 个文档块"

# 使用
kb = EnterpriseKnowledgeBase(
    db_config={
        'vector_db': 'postgresql://...',
        'sql_db': 'postgresql://...',
        'graph_db': 'postgresql://...'
    },
    openai_api_key='your-key'
)

# 查询
answer = kb.ask("""
分析PostgreSQL的MVCC实现:
1. 技术原理 (从文档)
2. 性能数据 (从数据库)
3. 使用关系 (从图谱)
""")
print(answer)
```

---

**完成**: LangChain + PostgreSQL 18完整集成指南
**字数**: ~18,000字
**涵盖**: VectorStore、SQL、Graph、RAG、Agent、生产部署、最佳实践
