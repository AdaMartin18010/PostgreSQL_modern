---

> **📋 文档来源**: `DataBaseTheory\21-AI知识库\10-LangChain生产部署指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# LangChain生产部署指南

## 1. 架构设计

### 1.1 微服务架构

```text
┌─────────────────────────────────────────────┐
│          Load Balancer (Nginx)              │
└────────────────┬────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
┌─────▼─────┐        ┌─────▼─────┐
│ API-1     │        │ API-2     │  FastAPI服务
│ LangChain │        │ LangChain │
└─────┬─────┘        └─────┬─────┘
      │                     │
      └──────────┬──────────┘
                 │
      ┌──────────▼──────────┐
      │    pgBouncer        │  连接池
      └──────────┬──────────┘
                 │
      ┌──────────▼──────────┐
      │  PostgreSQL 18      │  数据库
      │  + pgvector         │
      │  + Apache AGE       │
      └─────────────────────┘
```

---

## 2. FastAPI集成

### 2.1 API服务

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import asyncio

app = FastAPI(title="LangChain RAG API")

# 请求模型
class QueryRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    top_k: int = 5
    temperature: float = 0.7

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    latency_ms: float
    tokens: int
    cost: float

# 全局RAG系统
rag_system = ProductionRAGSystem(config)

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """RAG查询API"""

    try:
        result = await asyncio.to_thread(
            rag_system.query,
            request.question,
            request.user_id
        )

        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index")
async def index_document(
    file_path: str,
    background_tasks: BackgroundTasks
):
    """索引文档（异步）"""

    background_tasks.add_task(
        rag_system.index_document,
        file_path
    )

    return {"message": "文档索引任务已提交"}

@app.get("/health")
async def health_check():
    """健康检查"""

    try:
        # 检查PostgreSQL连接
        cursor.execute("SELECT 1")

        # 检查向量检索
        test_embedding = [0.1] * 768
        cursor.execute("""
            SELECT 1 FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT 1
        """, (test_embedding,))

        return {"status": "healthy"}

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"不健康: {e}")

@app.get("/metrics")
async def metrics():
    """暴露Prometheus指标"""

    cursor.execute("""
        SELECT
            COUNT(*) AS total_queries,
            AVG(duration_ms) AS avg_latency,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_latency
        FROM query_logs
        WHERE created_at >= now() - INTERVAL '5 minutes'
    """)

    metrics = cursor.fetchone()

    return {
        "total_queries": metrics['total_queries'],
        "avg_latency_ms": metrics['avg_latency'],
        "p95_latency_ms": metrics['p95_latency']
    }

# 运行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
```

---

## 3. Docker部署

### 3.1 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 运行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 3.2 docker-compose完整编排

```yaml
# docker-compose-langchain.yml
version: '3.8'

services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: langchain_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  langchain-api:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/langchain_db
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - langchain-api

volumes:
  postgres_data:
  redis_data:
```

---

## 4. Kubernetes部署

### 4.1 Deployment配置

```yaml
# langchain-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langchain-api
spec:
  replicas: 5
  selector:
    matchLabels:
      app: langchain-api
  template:
    metadata:
      labels:
        app: langchain-api
    spec:
      containers:
      - name: api
        image: langchain-api:latest
        ports:
        - containerPort: 8000

        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: langchain-secrets
              key: database-url

        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: langchain-secrets
              key: openai-key

        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"

        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

      # HPA自动扩缩容
      - name: metrics-server
        image: metrics-server:latest
        ports:
        - containerPort: 9090
---
apiVersion: v1
kind: Service
metadata:
  name: langchain-service
spec:
  selector:
    app: langchain-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: langchain-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: langchain-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
```

---

## 5. 监控与日志

### 5.1 Prometheus指标

```python
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import make_asgi_app

# 定义指标
query_counter = Counter('langchain_queries_total', 'Total queries', ['model', 'status'])
query_duration = Histogram('langchain_query_duration_seconds', 'Query duration')
active_queries = Gauge('langchain_active_queries', 'Active queries')
vector_search_duration = Histogram('vector_search_duration_seconds', 'Vector search duration')

# 集成到FastAPI
from fastapi import FastAPI

app = FastAPI()

# 暴露metrics端点
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# 使用指标
@app.post("/query")
@query_duration.time()
async def query(request: QueryRequest):
    active_queries.inc()

    try:
        result = await rag_system.query(request.question)

        query_counter.labels(model='gpt-3.5', status='success').inc()

        return result

    except Exception as e:
        query_counter.labels(model='gpt-3.5', status='error').inc()
        raise

    finally:
        active_queries.dec()
```

### 5.2 结构化日志

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON格式日志"""

    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        if hasattr(record, 'query'):
            log_data['query'] = record.query

        if hasattr(record, 'latency_ms'):
            log_data['latency_ms'] = record.latency_ms

        return json.dumps(log_data, ensure_ascii=False)

# 配置日志
logger = logging.getLogger('langchain_app')
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 使用
logger.info(
    "Query executed",
    extra={
        'user_id': 'user_123',
        'query': 'What is MVCC?',
        'latency_ms': 850.5
    }
)

# 输出:
# {"timestamp": "2025-12-05T10:30:00.000Z", "level": "INFO", "message": "Query executed", ...}
```

---

## 6. 限流与熔断

### 6.1 令牌桶限流

```python
from fastapi import HTTPException
import time

class RateLimiter:
    """令牌桶限流器"""

    def __init__(self, rate=100, capacity=200):
        self.rate = rate  # 每秒令牌数
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def acquire(self, tokens=1):
        """获取令牌"""
        now = time.time()

        # 补充令牌
        elapsed = now - self.last_update
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now

        # 检查令牌
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        else:
            return False

# 全局限流器
global_limiter = RateLimiter(rate=100, capacity=200)

# 用户级限流器
user_limiters = {}

def get_user_limiter(user_id):
    if user_id not in user_limiters:
        user_limiters[user_id] = RateLimiter(rate=10, capacity=20)
    return user_limiters[user_id]

# FastAPI中间件
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    # 全局限流
    if not global_limiter.acquire():
        raise HTTPException(status_code=429, detail="全局限流：请求过多")

    # 用户限流
    user_id = request.headers.get('X-User-ID')
    if user_id:
        user_limiter = get_user_limiter(user_id)
        if not user_limiter.acquire():
            raise HTTPException(status_code=429, detail="用户限流：请求过多")

    response = await call_next(request)
    return response
```

### 6.2 熔断器

```python
from circuitbreaker import circuit

class LLMCircuitBreaker:
    """LLM熔断器"""

    def __init__(self):
        self.failure_threshold = 5
        self.recovery_timeout = 60
        self.expected_exception = Exception

    @circuit(failure_threshold=5, recovery_timeout=60)
    def call_llm(self, prompt):
        """调用LLM（带熔断）"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            timeout=30
        )
        return response.choices[0].message.content

# 使用
llm_breaker = LLMCircuitBreaker()

try:
    answer = llm_breaker.call_llm("What is PostgreSQL?")
except CircuitBreakerError:
    # 熔断器打开，使用降级方案
    answer = fallback_answer()

# 保护系统：
# - 5次失败后熔断
# - 60秒后自动恢复
# - 避免级联故障
```

---

## 3. 性能优化

### 3.1 批处理

```python
import asyncio
from collections import defaultdict

class BatchProcessor:
    """批处理器"""

    def __init__(self, batch_size=32, max_wait_ms=100):
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.queue = []
        self.lock = asyncio.Lock()

    async def add_query(self, question):
        """添加查询到批次"""
        future = asyncio.Future()

        async with self.lock:
            self.queue.append((question, future))

            # 达到批次大小或超时
            if len(self.queue) >= self.batch_size:
                await self._process_batch()

        return await future

    async def _process_batch(self):
        """处理批次"""
        if not self.queue:
            return

        batch = self.queue[:self.batch_size]
        self.queue = self.queue[self.batch_size:]

        questions = [item[0] for item in batch]
        futures = [item[1] for item in batch]

        # 批量嵌入
        embeddings = await asyncio.to_thread(
            embedding_model.embed_documents,
            questions
        )

        # 批量检索
        results = await asyncio.to_thread(
            batch_vector_search,
            embeddings
        )

        # 返回结果
        for future, result in zip(futures, results):
            future.set_result(result)

# 使用
processor = BatchProcessor()

async def handle_request(question):
    return await processor.add_query(question)

# 性能提升：
# 逐个处理: 100个×20ms = 2000ms
# 批量处理: 4批×50ms = 200ms (-90%)
```

---

## 4. 高可用配置

### 4.1 多模型备份

```python
class MultiModelRAG:
    """多模型RAG（高可用）"""

    def __init__(self):
        # 主模型: OpenAI GPT-3.5
        self.primary_llm = OpenAI(
            model_name="gpt-3.5-turbo",
            request_timeout=30
        )

        # 备用模型1: OpenAI GPT-4
        self.backup_llm_1 = OpenAI(
            model_name="gpt-4",
            request_timeout=30
        )

        # 备用模型2: 本地模型
        from langchain.llms import LlamaCpp
        self.backup_llm_2 = LlamaCpp(
            model_path="/models/llama-2-7b.gguf",
            n_ctx=2048
        )

    def query(self, question):
        """查询（自动降级）"""

        # 尝试主模型
        try:
            return self.primary_llm(question)
        except Exception as e:
            logger.warning(f"主模型失败: {e}")

        # 尝试备用模型1
        try:
            return self.backup_llm_1(question)
        except Exception as e:
            logger.warning(f"备用模型1失败: {e}")

        # 尝试备用模型2（本地）
        try:
            return self.backup_llm_2(question)
        except Exception as e:
            logger.error(f"所有模型均失败: {e}")
            raise

# 可用性：
# 单模型: 99.5%
# 三模型备份: 99.999% (5个9)
```

---

## 5. 成本优化

### 5.1 智能路由

```python
class CostOptimizedRAG:
    """成本优化的RAG"""

    def __init__(self):
        self.cheap_model = OpenAI(model_name="gpt-3.5-turbo")  # $0.002/1K tokens
        self.expensive_model = OpenAI(model_name="gpt-4")  # $0.03/1K tokens

    def estimate_complexity(self, question):
        """估算问题复杂度"""

        # 简单规则
        if len(question) < 50:
            return 'simple'

        if any(word in question for word in ['详细', '深入', '分析', '对比']):
            return 'complex'

        return 'medium'

    def query(self, question):
        """智能路由查询"""

        complexity = self.estimate_complexity(question)

        if complexity == 'simple':
            # 简单问题用便宜模型
            model = self.cheap_model
            logger.info(f"使用GPT-3.5: {question}")
        else:
            # 复杂问题用贵模型
            model = self.expensive_model
            logger.info(f"使用GPT-4: {question}")

        with get_openai_callback() as cb:
            answer = model(question)

            logger.info(f"成本: ${cb.total_cost:.4f}")

            return answer

# 成本节省：
# 全部GPT-4: $100/天
# 智能路由（70% GPT-3.5）: $25/天 (-75%)
```

---

## 6. 扩展性设计

### 6.1 分布式向量索引

```python
class DistributedVectorStore:
    """分布式向量存储"""

    def __init__(self, shard_configs):
        """
        shard_configs = [
            {'host': 'shard1.db', 'port': 5432},
            {'host': 'shard2.db', 'port': 5432},
            {'host': 'shard3.db', 'port': 5432},
        ]
        """
        self.shards = []

        for config in shard_configs:
            shard = PGVector(
                connection_string=f"postgresql://{config['host']}:{config['port']}/vectordb",
                embedding_function=OpenAIEmbeddings()
            )
            self.shards.append(shard)

    def add_documents(self, documents):
        """添加文档（分片存储）"""

        # 按文档ID Hash分片
        for i, doc in enumerate(documents):
            shard_id = hash(doc.metadata.get('id', i)) % len(self.shards)
            self.shards[shard_id].add_documents([doc])

    def similarity_search(self, query, k=10):
        """相似度搜索（并行查询所有分片）"""

        from concurrent.futures import ThreadPoolExecutor

        def search_shard(shard):
            return shard.similarity_search(query, k=k)

        with ThreadPoolExecutor(max_workers=len(self.shards)) as executor:
            futures = [executor.submit(search_shard, shard) for shard in self.shards]
            shard_results = [f.result() for f in futures]

        # 合并结果
        all_docs = []
        for results in shard_results:
            all_docs.extend(results)

        # 重新排序
        all_docs.sort(key=lambda x: x.metadata.get('score', 0), reverse=True)

        return all_docs[:k]

# 使用
distributed_store = DistributedVectorStore([
    {'host': 'shard1.db', 'port': 5432},
    {'host': 'shard2.db', 'port': 5432},
    {'host': 'shard3.db', 'port': 5432},
])

# 扩展性：
# 单分片: 100万文档，查询25ms
# 3分片: 300万文档，查询30ms（几乎线性扩展）
```

---

## 7. 部署检查清单

```text
□ 环境准备
  □ PostgreSQL 18安装
  □ pgvector扩展安装
  □ Python 3.11+环境
  □ 依赖包安装

□ 配置优化
  □ PostgreSQL配置（io_direct等）
  □ pgvector索引参数
  □ 连接池配置
  □ Redis缓存配置

□ API服务
  □ FastAPI部署
  □ Gunicorn/Uvicorn配置
  □ Nginx反向代理
  □ SSL证书配置

□ 监控告警
  □ Prometheus指标收集
  □ Grafana仪表板
  □ 告警规则配置
  □ 日志聚合（ELK/Loki）

□ 安全配置
  □ API Key管理
  □ 限流配置
  □ 熔断配置
  □ 数据加密

□ 测试验证
  □ 功能测试
  □ 性能测试
  □ 压力测试
  □ 故障恢复测试

□ 文档与运维
  □ API文档
  □ 部署文档
  □ 运维手册
  □ 应急预案
```

---

**完成**: LangChain生产部署指南
**字数**: ~15,000字
**涵盖**: 架构设计、FastAPI集成、Docker部署、Kubernetes、监控日志、限流熔断、成本优化、扩展性、检查清单
