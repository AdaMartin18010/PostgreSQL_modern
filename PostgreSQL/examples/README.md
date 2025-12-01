# PostgreSQL AI 集成 - 可运行示例

> **最后更新**：2025年11月11日
> **版本覆盖**：PostgreSQL 17+ | PostgreSQL 18 ⭐
> **状态**：✅ **8个核心示例已完成**

---

## 📋 目录说明

本目录包含 PostgreSQL AI 集成的端到端可运行示例，每个示例都包含：

- ✅ **Docker Compose 配置**：一键启动完整环境
- ✅ **初始化 SQL 脚本**：数据库表结构和索引
- ✅ **示例数据**：可直接运行的测试数据
- ✅ **应用代码**：Python/FastAPI 示例（如适用）
- ✅ **README**：详细的运行说明

---

## 🎯 示例列表

### 核心示例（已实现）

1. **基础向量搜索** (`01-basic-vector-search/`) ✅
   - PostgreSQL 18 + pgvector 2.0
   - 基础向量存储和检索
   - 适合：快速入门

2. **混合搜索（RRF）** (`02-hybrid-search-rrf/`) ✅
   - pgvector + 全文搜索 + RRF 融合
   - 适合：电商商品搜索场景

### 案例示例

1. **RAG 知识库** (`03-rag-knowledge-base/`) ✅ 🆕
   - pgvector + 混合检索 + RRF融合
   - 适合：知识库问答系统
   - **完整容器化部署**：包含后端、前端、监控等所有服务
   - **启动脚本**：支持基础模式和完整模式
   - 📖 [完整部署文档](./03-rag-knowledge-base/README.full.md)

2. **智能推荐系统** (`04-recommendation-system/`) ✅
   - pgvector + 虚拟生成列 + 交互历史
   - 适合：内容推荐场景

3. **IoT 异常检测** (`05-iot-anomaly-detection/`) ✅
   - TimescaleDB + pgvector
   - 适合：时序+向量混合分析

4. **金融风控系统** (`06-financial-fraud-detection/`) ✅
   - pgvector + 图关系分析
   - 适合：反欺诈检测

5. **医疗知识库** (`07-medical-knowledge-base/`) ✅
   - pgvector + 实验分支管理
   - 适合：医疗知识检索、A/B测试

6. **政务智能问答** (`08-government-qa/`) ✅
   - pgvector + 数据脱敏 + 审计日志
   - 适合：政务问答、合规场景

7. **列存储示例** (`09-columnar-storage/`) ✅ 🆕
   - cstore_fdw列存储扩展
   - 列存储查询优化
   - 混合存储架构（热数据行存储 + 冷数列存储）
   - 适合：数据仓库、OLAP场景

---

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ 可用内存

### 运行示例

```bash
# 1. 进入示例目录
cd examples/01-basic-vector-search

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 连接到数据库
docker-compose exec postgres psql -U postgres -d vectordb

# 5. 停止服务
docker-compose down
```

---

## 📚 相关文档

- [AI 时代专题](../ai_view.md) ⭐⭐⭐ (v3.0, 2025-11-11)
- [AI 时代专题导航](../05-前沿技术/AI-时代/00-导航.md)
- [落地案例](../05-前沿技术/AI-时代/06-落地案例-2025精选.md)
- [快速开始指南](../00-项目导航/AI集成快速开始.md)

---

## 🔄 更新计划

- [x] 完成所有8个案例的Docker Compose配置 ✅
- [x] RAG知识库完整容器化部署 ✅ (2025-01-15)
- [ ] 添加性能测试脚本
- [ ] 添加监控和日志收集
- [ ] 添加CI/CD配置

---

## 🆕 最新更新（2025-01-15）

### RAG知识库完整容器化部署 ✅

- ✅ 创建完整的docker-compose配置（`docker-compose.full.yml`）
  - 包含所有服务：PostgreSQL、Redis、Backend、Frontend、Celery、Nginx、Prometheus、Grafana
- ✅ 创建启动脚本（`start.sh`）
  - 支持基础模式（仅数据库）和完整模式（所有服务）
  - 自动检查环境和创建配置文件
- ✅ 创建完整部署文档（`README.full.md`）
  - 详细的部署说明、配置指南、故障排查
- ✅ 创建环境变量示例（`env.example`）
- ✅ 更新README.md添加完整部署说明

**使用方式**：

```bash
cd examples/03-rag-knowledge-base
./start.sh  # 交互式选择启动模式
```

---

**最后更新**：2025-01-15
