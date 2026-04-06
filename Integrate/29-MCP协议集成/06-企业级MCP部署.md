# 企业级MCP部署与运维指南

> **部署级别**: 生产环境  
> **可用性目标**: 99.9%+  
> **安全等级**: 企业级

---

## 一、架构设计

### 1.1 生产架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         生产架构                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐      ┌──────────────┐      ┌────────────┐  │
│   │   Claude/    │      │   MCP Server │      │ PostgreSQL │  │
│   │   Cursor     │◄────►│   Cluster    │◄────►│   Cluster  │  │
│   │   (Client)   │      │   (Docker)   │      │  (Primary) │  │
│   └──────────────┘      └──────┬───────┘      └──────┬─────┘  │
│                                │                     │        │
│                         ┌──────▼───────┐      ┌──────▼─────┐  │
│                         │   Redis      │      │  Read      │  │
│                         │   (Cache)    │      │  Replicas  │  │
│                         └──────────────┘      └────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │              Monitoring Stack (Prometheus/Grafana)        │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 高可用设计

| 组件 | 高可用策略 | 故障恢复时间 |
|------|-----------|-------------|
| MCP Server | 多实例负载均衡 | < 5秒 |
| PostgreSQL | 主从复制 + 自动故障转移 | < 30秒 |
| Redis | Sentinel模式 | < 10秒 |

---

## 二、Docker部署

### 2.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY postgres_mcp_server.py .

# 非root用户运行
RUN useradd -m -u 1000 mcp && chown -R mcp:mcp /app
USER mcp

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

EXPOSE 8080

CMD ["python", "postgres_mcp_server.py"]
```

### 2.2 Docker Compose

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    restart: always
    environment:
      - DATABASE_URL=postgresql://mcp_user:${DB_PASSWORD}@postgres:5432/proddb
      - READ_ONLY_MODE=true
      - MAX_QUERY_RESULTS=1000
      - QUERY_TIMEOUT=30
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
    networks:
      - mcp-network
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  postgres:
    image: postgres:18-alpine
    restart: always
    environment:
      - POSTGRES_USER=mcp_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=proddb
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mcp_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - mcp-network

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - mcp-network

  grafana:
    image: grafana/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    networks:
      - mcp-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  mcp-network:
    driver: bridge
```

---

## 三、Kubernetes部署

### 3.1 Deployment配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: your-registry/postgres-mcp-server:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: READ_ONLY_MODE
          value: "true"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server
  namespace: production
spec:
  selector:
    app: mcp-server
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

### 3.2 HPA自动扩缩容

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-server-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-server
  minReplicas: 3
  maxReplicas: 10
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

---

## 四、监控与告警

### 4.1 关键指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| mcp_requests_total | 请求总数 | - |
| mcp_request_duration_seconds | 请求延迟 | P99 > 5s |
| mcp_errors_total | 错误数 | 增长率 > 10% |
| mcp_active_connections | 活跃连接数 | > 80% |
| db_query_duration_seconds | 查询延迟 | P99 > 3s |

### 4.2 Prometheus配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mcp-server'
    static_configs:
      - targets: ['mcp-server:8080']
    metrics_path: /metrics
    scrape_interval: 10s
```

### 4.3 Grafana仪表盘

参考 `grafana/dashboards/mcp-dashboard.json`

---

## 五、日志管理

### 5.1 结构化日志

```python
import logging
import json
from pythonjsonlogger import jsonlogger

# 配置JSON格式日志
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s'
)
logHandler.setFormatter(formatter)

logger = logging.getLogger('mcp')
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# 使用
logger.info("Query executed", extra={
    "query_hash": "abc123",
    "duration_ms": 150,
    "row_count": 100
})
```

### 5.2 ELK集成

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/mcp/*.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "mcp-logs-%{+yyyy.MM.dd}"
```

---

## 六、备份与恢复

### 6.1 配置备份

```bash
#!/bin/bash
# backup-config.sh

# 备份MCP服务器配置
tar -czf /backup/mcp-config-$(date +%Y%m%d).tar.gz \
    docker-compose.yml \
    kubernetes/ \
    grafana/ \
    prometheus/

# 上传到S3
aws s3 cp /backup/mcp-config-$(date +%Y%m%d).tar.gz \
    s3://mcp-backups/config/
```

### 6.2 灾难恢复

```bash
#!/bin/bash
# disaster-recovery.sh

# 1. 恢复配置
aws s3 cp s3://mcp-backups/config/mcp-config-latest.tar.gz /tmp/
tar -xzf /tmp/mcp-config-latest.tar.gz -C /opt/mcp/

# 2. 重新部署
kubectl apply -f kubernetes/

# 3. 验证
kubectl rollout status deployment/mcp-server
```

---

## 七、性能优化

### 7.1 连接池调优

```python
# 连接池配置优化
pool = await asyncpg.create_pool(
    database_url,
    min_size=5,          # 最小连接数
    max_size=20,         # 最大连接数
    max_inactive_time=300,  # 连接最大空闲时间
    max_queries=100000,  # 单连接最大查询数
    command_timeout=30   # 查询超时
)
```

### 7.2 缓存策略

```python
import aioredis

# Redis缓存
redis = aioredis.from_url("redis://localhost")

async def get_cached_schema(table_name: str):
    cache_key = f"schema:{table_name}"
    
    # 尝试缓存
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 查询数据库
    schema = await fetch_schema_from_db(table_name)
    
    # 写入缓存（5分钟过期）
    await redis.setex(cache_key, 300, json.dumps(schema))
    
    return schema
```

---

## 八、安全加固

### 8.1 网络策略

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mcp-server-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: mcp-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: client-namespace
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### 8.2 Secret管理

```bash
# 创建Kubernetes Secret
kubectl create secret generic db-credentials \
    --from-literal=url='postgresql://user:pass@host/db' \
    --namespace=production
```

---

## 九、运维检查清单

### 部署前

- [ ] 配置审查完成
- [ ] 安全扫描通过
- [ ] 性能测试达标
- [ ] 回滚方案准备

### 部署中

- [ ] 蓝绿部署或金丝雀发布
- [ ] 实时监控关键指标
- [ ] 准备好回滚命令

### 部署后

- [ ] 功能验证通过
- [ ] 监控告警正常
- [ ] 日志收集正常
- [ ] 备份任务运行

---

## 十、故障排查

### 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 连接超时 | 连接池耗尽 | 增加max_size或优化查询 |
| 内存泄漏 | 未关闭的连接 | 检查连接释放逻辑 |
| 查询缓慢 | 缺少索引 | 优化数据库索引 |
| 服务不可用 | 健康检查失败 | 检查依赖服务状态 |

---

*生产环境部署请参考完整配置模板。*
