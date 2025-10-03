# 08_ecosystem_cases — 生态扩展实战案例

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **难度范围**：⭐⭐⭐ 中级 ~ ⭐⭐⭐⭐⭐ 专家级  
> **目标**：通过完整的生产级案例展示PostgreSQL扩展生态的强大能力

---

## 📚 案例列表

### 🔍 1. 全文搜索（Full-Text Search）

**路径**：[full_text_search/](./full_text_search/README.md)  
**难度**：⭐⭐⭐ 中级  
**适合场景**：文档搜索、日志检索、商品搜索、内容推荐

**核心特性**：

- ✅ 中英文混合全文搜索
- ✅ 相关性排序与高亮显示
- ✅ GIN索引性能优化
- ✅ 搜索建议与自动补全

---

### 🔄 2. CDC变更数据捕获（Change Data Capture）

**路径**：[change_data_capture/](./change_data_capture/README.md)  
**难度**：⭐⭐⭐⭐ 高级  
**适合场景**：数据同步、审计日志、实时ETL、事件驱动架构

**核心特性**：

- ✅ 基于逻辑复制的CDC实现
- ✅ 基于触发器的CDC实现
- ✅ 变更数据流式输出（JSON格式）
- ✅ 性能优化与监控

---

### 🗺️ 3. 地理围栏（Geofencing with PostGIS）

**路径**：[geofencing/](./geofencing/README.md)  
**难度**：⭐⭐⭐⭐ 高级  
**适合场景**：外卖配送、共享出行、物流跟踪、LBS营销

**核心特性**：

- ✅ 点在多边形内判断（Point-in-Polygon）
- ✅ 实时位置追踪与告警
- ✅ 高性能空间索引（GiST索引）
- ✅ 地理围栏进出事件触发

---

### 🔗 4. 联邦查询（Federated Queries with FDW）

**路径**：[federated_queries/](./federated_queries/README.md)  
**难度**：⭐⭐⭐⭐ 高级  
**适合场景**：跨库查询、异构数据源集成、数据湖查询、遗留系统集成

**核心特性**：

- ✅ 跨PostgreSQL数据库查询（postgres_fdw）
- ✅ 查询MySQL/MongoDB/CSV/API等外部数据源
- ✅ 分布式JOIN与查询优化
- ✅ 数据虚拟化与联邦视图

---

### 📊 5. 实时分析（Real-Time Analytics）

**路径**：[realtime_analytics/](./realtime_analytics/README.md)  
**难度**：⭐⭐⭐⭐⭐ 专家级  
**适合场景**：实时大屏、监控告警、流式分析、业务指标实时计算

**核心特性**：

- ✅ 高频数据写入（10K+ TPS）
- ✅ 实时聚合查询（亚秒级响应）
- ✅ 滑动窗口分析（1分钟/5分钟/1小时）
- ✅ 物化视图增量刷新

---

### ⏱️ 6. 时序数据管理（TimescaleDB Time-Series）

**路径**：[timeseries_db/](./timeseries_db/README.md)  
**难度**：⭐⭐⭐⭐ 高级  
**适合场景**：IoT监控、金融行情、系统指标、日志分析

**核心特性**：

- ✅ 超表（Hypertable）自动分区
- ✅ 连续聚合（Continuous Aggregates）
- ✅ 自动数据压缩（7天后压缩70%+）
- ✅ 数据保留策略（自动清理历史数据）

---

### 🔒 7. 分布式锁（Distributed Locks with Advisory Locks）

**路径**：[distributed_locks/](./distributed_locks/README.md)  
**难度**：⭐⭐⭐⭐ 高级  
**适合场景**：分布式任务调度、资源互斥、幂等性保证、集群协调

**核心特性**：

- ✅ Session级和Transaction级锁
- ✅ 分布式任务调度队列
- ✅ 锁超时自动恢复
- ✅ 死锁检测与处理

---

### 🔄 8. 流式复制（Streaming Replication & HA）

**路径**：[streaming_replication/](./streaming_replication/README.md)  
**难度**：⭐⭐⭐⭐⭐ 专家级  
**适合场景**：高可用架构、读写分离、灾难恢复、多地域部署

**核心特性**：

- ✅ 主从复制配置（Primary-Standby）
- ✅ 同步/异步复制（RPO < 5秒）
- ✅ 自动故障转移（RTO < 30秒）
- ✅ 读写分离负载均衡

---

## 🎯 已有案例（专题目录）

### 🤖 AI向量检索

**路径**：[ai_vector/rag_minimal/](./ai_vector/rag_minimal/README.md)  
**扩展**：pgvector  
**场景**：RAG系统、语义搜索、相似度查询

### 🌐 分布式数据库

**路径**：[distributed_db/](./distributed_db/README.md)  
**扩展**：Citus  
**场景**：多租户、分布式查询、水平扩展

---

## 📖 案例使用指南

### 快速开始

每个案例包含：

1. **业务场景**：明确的业务背景和需求
2. **架构设计**：清晰的技术架构图
3. **完整代码**：可直接运行的SQL脚本
4. **性能优化**：生产级优化技巧
5. **练习任务**：分级练习（基础/进阶/挑战）

### 学习路径

**初级用户**（了解PostgreSQL基础）：

1. 全文搜索 → 地理围栏 → RAG向量检索

**中级用户**（熟悉索引和查询优化）：
2. CDC变更捕获 → 联邦查询 → 时序数据管理

**高级用户**（需要高性能和扩展性）：
3. 实时分析 → 分布式锁 → 流式复制 → Citus分布式

### 技术栈对照

| 案例 | 核心扩展 | 索引类型 | 适合数据量 | 复杂度 |
|------|---------|---------|-----------|--------|
| 全文搜索 | 内置tsvector | GIN | 百万级 | ⭐⭐⭐ |
| CDC | 逻辑复制/触发器 | - | 千万级 | ⭐⭐⭐⭐ |
| 地理围栏 | PostGIS | GiST | 百万级 | ⭐⭐⭐⭐ |
| 联邦查询 | postgres_fdw等 | - | 取决于源 | ⭐⭐⭐⭐ |
| 实时分析 | pg_cron/分区表 | B-tree | 亿级+ | ⭐⭐⭐⭐⭐ |
| 时序数据 | TimescaleDB | B-tree | 10亿级+ | ⭐⭐⭐⭐ |
| 分布式锁 | Advisory Locks | - | - | ⭐⭐⭐⭐ |
| 流式复制 | 物理复制 | - | - | ⭐⭐⭐⭐⭐ |
| RAG向量 | pgvector | HNSW/IVFFlat | 千万级 | ⭐⭐⭐ |
| Citus分布式 | Citus | 分布式索引 | 10亿级+ | ⭐⭐⭐⭐⭐ |

---

## 🛠️ 环境准备

### 基础环境

```bash
# PostgreSQL 17
sudo apt-get install postgresql-17

# 常用扩展
sudo apt-get install postgresql-17-postgis-3
sudo apt-get install postgresql-17-cron
```

### 扩展安装

```sql
-- 全文搜索（内置）
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- PostGIS（地理空间）
CREATE EXTENSION IF NOT EXISTS postgis;

-- pgvector（向量检索）
CREATE EXTENSION IF NOT EXISTS vector;

-- pg_cron（定时任务）
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- postgres_fdw（联邦查询）
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
```

---

## 📚 更多资源

- **官方文档**：<https://www.postgresql.org/docs/17/>
- **PostGIS文档**：<https://postgis.net/documentation/>
- **pgvector GitHub**：<https://github.com/pgvector/pgvector>
- **Citus文档**：<https://docs.citusdata.com/>
- **本项目主页**：[../README.md](../README.md)

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**反馈建议**：欢迎提交Issue或Pull Request
