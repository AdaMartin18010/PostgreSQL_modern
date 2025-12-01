# RAG知识库端到端案例 - 完整容器化部署

> **PostgreSQL版本**: 18 ⭐ | 17
> **pgvector版本**: 2.0 ⭐ | 0.7+
> **最后更新**: 2025-01-15
> **部署模式**: 完整容器化（生产级）

---

## 📋 概述

这是一个**完整的、生产级的RAG知识库系统**容器化部署方案，包含：

- ✅ PostgreSQL 18 + pgvector 2.0（向量存储）
- ✅ Redis（缓存和任务队列）
- ✅ FastAPI后端（Python）
- ✅ React前端（TypeScript）
- ✅ Celery（异步任务处理）
- ✅ Nginx（反向代理）
- ✅ Prometheus + Grafana（监控）

---

## 🚀 快速开始

### 方式一：使用启动脚本（推荐）

```bash
# 赋予执行权限
chmod +x start.sh

# 运行启动脚本
./start.sh
```

启动脚本会引导您选择：

- **基础模式**：仅启动PostgreSQL和Redis
- **完整模式**：启动所有服务（后端、前端、监控等）

### 方式二：手动启动

#### 1. 基础模式（仅数据库）

```bash
# 启动PostgreSQL和Redis
docker-compose up -d

# 查看服务状态
docker-compose ps

# 连接到数据库
docker-compose exec postgres psql -U postgres -d rag_kb
```

#### 2. 完整模式（所有服务）

```bash
# 启动所有服务
docker-compose -f docker-compose.full.yml up -d --build

# 查看服务状态
docker-compose -f docker-compose.full.yml ps

# 查看日志
docker-compose -f docker-compose.full.yml logs -f
```

---

## 📁 项目结构

```text
03-rag-knowledge-base/
├── docker-compose.yml          # 基础模式（PostgreSQL + Redis）
├── docker-compose.full.yml     # 完整模式（所有服务）
├── start.sh                    # 启动脚本
├── .env.example                # 环境变量示例
├── database/
│   └── init.sql                # 数据库初始化脚本
├── backend/                    # FastAPI后端（需要创建）
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
├── frontend/                   # React前端（需要创建）
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── nginx/
│   └── nginx.conf              # Nginx配置
└── monitoring/
    ├── prometheus.yml          # Prometheus配置
    └── grafana/
        ├── dashboards/
        └── datasources/
```

---

## 🔧 配置说明

### 环境变量

创建`.env`文件（参考`.env.example`）：

```bash
# PostgreSQL配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rag_kb

# Redis配置
REDIS_URL=redis://redis:6379/0

# OpenAI API Key（用于生成embedding）
OPENAI_API_KEY=your-api-key-here

# 安全密钥
SECRET_KEY=your-secret-key-here

# 环境
ENVIRONMENT=development
```

### 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |
| Backend API | 8000 | FastAPI后端 |
| Frontend | 3000 | React前端 |
| Nginx | 80 | 反向代理 |
| Prometheus | 9090 | 监控 |
| Grafana | 3001 | 可视化 |

---

## 📊 服务访问

### 基础模式

- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

### 完整模式

- **前端应用**: <http://localhost:3000>
- **API文档**: <http://localhost:8000/docs>
- **API健康检查**: <http://localhost:8000/health>
- **Nginx代理**: <http://localhost:80>
- **Prometheus**: <http://localhost:9090>
- **Grafana**: <http://localhost:3001> (admin/admin)

---

## 🔨 开发指南

### 后端开发

```bash
# 进入后端容器
docker-compose -f docker-compose.full.yml exec backend bash

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
# 进入前端容器
docker-compose -f docker-compose.full.yml exec frontend sh

# 安装依赖
npm install

# 运行开发服务器
npm start
```

---

## 📝 数据库操作

### 初始化数据库

```bash
# 数据库已通过init.sql自动初始化
# 如需手动执行：
docker-compose exec postgres psql -U postgres -d rag_kb -f /docker-entrypoint-initdb.d/init.sql
```

### 执行SQL查询

```bash
# 连接到数据库
docker-compose exec postgres psql -U postgres -d rag_kb

# 查看所有文档
SELECT id, title, category, created_at FROM knowledge_base;

# 执行RAG检索
SELECT * FROM rag_retrieve(
    'PostgreSQL 向量搜索',
    '[查询向量]'::vector(1536),
    5,
    NULL
);
```

---

## 🧪 测试

### API测试

```bash
# 健康检查
curl http://localhost:8000/health

# 问答API
curl -X POST http://localhost:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "PostgreSQL 向量搜索",
    "kb_id": "your-kb-id"
  }'
```

### 性能测试

```bash
# 使用ab进行压力测试
ab -n 1000 -c 10 http://localhost:8000/api/qa
```

---

## 📊 监控

### Prometheus指标

访问 <http://localhost:9090> 查看Prometheus监控面板。

### Grafana仪表板

访问 <http://localhost:3001> 查看Grafana可视化仪表板。

默认登录：

- 用户名: `admin`
- 密码: `admin`

---

## 🛑 停止服务

### 基础模式

```bash
docker-compose down
```

### 完整模式

```bash
docker-compose -f docker-compose.full.yml down
```

### 清理数据

```bash
# 停止并删除所有数据卷
docker-compose -f docker-compose.full.yml down -v
```

---

## 🔍 故障排查

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.full.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.full.yml logs -f backend
docker-compose -f docker-compose.full.yml logs -f postgres
```

### 检查服务状态

```bash
# 查看服务状态
docker-compose -f docker-compose.full.yml ps

# 检查服务健康状态
docker-compose -f docker-compose.full.yml exec backend curl http://localhost:8000/health
```

### 常见问题

1. **端口冲突**
   - 检查端口是否被占用：`lsof -i :5432`
   - 修改docker-compose.yml中的端口映射

2. **数据库连接失败**
   - 检查PostgreSQL是否正常启动：`docker-compose ps postgres`
   - 检查环境变量配置

3. **API无法访问**
   - 检查后端服务是否启动：`docker-compose logs backend`
   - 检查防火墙设置

---

## 📚 相关文档

- [RAG知识库完整项目文档](../../08-实战案例/06.02-RAG知识库完整项目.md) - 详细实现说明
- [RAG架构实战指南](../../07-前沿技术/05.04-RAG架构实战指南.md) - 架构设计
- [Docker部署指南](../../05-部署架构/容器化部署/05.12-Docker部署.md) - 容器化部署
- [AI时代专题](../../07-前沿技术/AI-时代/) - AI相关技术

---

## 🎯 下一步

1. **创建后端代码**：参考[完整项目文档](../../08-实战案例/06.02-RAG知识库完整项目.md)中的后端实现
2. **创建前端代码**：参考[完整项目文档](../../08-实战案例/06.02-RAG知识库完整项目.md)中的前端实现
3. **配置监控**：设置Prometheus和Grafana监控面板
4. **生产部署**：参考[部署指南](../../05-部署架构/容器化部署/05.12-Docker部署.md)

---

**最后更新**：2025-01-15
**维护者**：Data-Science Team
