# LangChain与MCP集成实战指南

> **技术栈**: LangChain + MCP + PostgreSQL  
> **目标**: 在LangChain应用中无缝使用MCP工具

---

## 一、概述

### 为什么需要LangChain + MCP？

```
LangChain优势:          MCP优势:
- 丰富的链式编排        - 标准化工具接口
- 多模型支持            - 动态工具发现
- 记忆管理              - 安全上下文控制
- Agent框架            - 生态隔离
         ↓                    ↓
    LangChain + MCP = 强大的AI数据库应用
```

---

## 二、环境准备

### 安装依赖

```bash
pip install langchain langchain-mcp-adapters langchain-openai
pip install mcp asyncpg
```

---

## 三、基础集成

### 3.1 连接MCP服务器

```python
from langchain_mcp_adapters import MCPToolkit
from mcp import ClientSession, StdioServerParameters

# 配置MCP服务器参数
server_params = StdioServerParameters(
    command="python",
    args=["postgres_mcp_server.py"],
    env={
        "DATABASE_URL": "postgresql://postgres:pass@localhost:5432/db",
        "READ_ONLY_MODE": "true"
    }
)

# 创建连接
async with ClientSession(server_params) as session:
    toolkit = MCPToolkit(session=session)
    tools = await toolkit.get_tools()
    
    print(f"Loaded {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
```

### 3.2 与LangChain Agent集成

```python
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent

# 初始化LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 获取prompt
prompt = hub.pull("hwchase17/openai-tools-agent")

# 创建Agent
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# 使用Agent查询数据库
response = await agent_executor.ainvoke({
    "input": "查询订单表中最近一个月的销售额"
})

print(response["output"])
```

---

## 四、高级应用

### 4.1 数据库RAG系统

```python
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings

# 结合pgvector实现RAG
embeddings = OpenAIEmbeddings()
vectorstore = SupabaseVectorStore(
    embedding=embeddings,
    table_name="documents"
)

# MCP工具 + RAG检索
async def database_rag_query(question: str):
    # 1. 向量检索相关文档
    docs = vectorstore.similarity_search(question, k=3)
    
    # 2. 使用MCP工具查询数据库
    context = "\n".join([d.page_content for d in docs])
    
    response = await agent_executor.ainvoke({
        "input": f"基于以下上下文回答问题：{context}\n\n问题：{question}"
    })
    
    return response["output"]
```

### 4.2 多Agent协作

```python
from langchain.agents import Tool

# 定义数据库分析师Agent
db_analyst_tools = [
    Tool(
        name="execute_sql",
        func=lambda q: execute_sql_tool.run(query=q),
        description="Execute SQL queries on the database"
    ),
    Tool(
        name="explain_query",
        func=lambda q: explain_query_tool.run(query=q),
        description="Get query execution plan"
    )
]

db_analyst = create_openai_tools_agent(llm, db_analyst_tools, prompt)

# 与数据可视化Agent协作
visualization_agent = ...

# 工作流编排
async def analyze_and_visualize(query_request: str):
    # 分析师Agent生成SQL
    sql_result = await db_analyst.ainvoke({"input": query_request})
    
    # 可视化Agent生成图表
    viz_result = await visualization_agent.ainvoke({
        "input": f"Create visualization for: {sql_result['output']}"
    })
    
    return viz_result
```

---

## 五、生产环境部署

### 5.1 连接池配置

```python
from mcp import ClientSession

# 生产级连接配置
server_params = StdioServerParameters(
    command="python",
    args=["postgres_mcp_server.py"],
    env={
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "MAX_POOL_SIZE": "20",
        "QUERY_TIMEOUT": "30"
    }
)
```

### 5.2 错误处理和重试

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def robust_query(question: str):
    try:
        return await agent_executor.ainvoke({"input": question})
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise
```

---

## 六、最佳实践

1. **工具选择**: 根据任务类型选择合适的MCP工具
2. **上下文管理**: 合理使用LangChain的记忆功能
3. **安全控制**: 始终使用只读模式连接生产数据库
4. **性能监控**: 监控查询执行时间和资源消耗
5. **错误处理**: 实现完善的错误处理和用户反馈

---

## 七、完整示例代码

参考 `examples/langchain_mcp_example.py` 获取完整可运行代码。

---

*现在您可以在LangChain应用中无缝使用PostgreSQL MCP工具了！*
