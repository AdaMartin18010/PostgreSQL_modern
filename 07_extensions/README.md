# 07_extensions

> 版本对标（更新于 2025-10）

## 主题边界

- PostgreSQL 扩展生态：pgvector（向量）、TimescaleDB（时序）、PostGIS（地理）、Citus（分布式）等核心
  扩展的安装、配置与最佳实践

## 核心要点

- **扩展机制**：`CREATE EXTENSION`、版本管理、依赖关系
- **主流扩展**：
  - pgvector：向量相似度检索、HNSW/IVFFlat 索引
  - TimescaleDB：时序数据、Hypertable、连续聚合、压缩
  - PostGIS：地理空间数据、GIS 查询、空间索引
  - Citus：分布式 PostgreSQL、分片、分布式查询
- **集成实践**：扩展组合使用、性能优化、运维监控

## 知识地图

```text
扩展生态 → 扩展选择与评估 → 安装与配置 → 应用开发 → 运维与调优
    ↓
专题扩展:
- pgvector/    (向量检索、RAG、AI应用)
- timescaledb/ (时序数据、IoT、监控)
- postgis/     (地理空间、LBS、GIS)
- citus/       (分布式、分片、HTAP)
```

## 扩展对比

| 扩展            | 用途     | 核心特性                          | 适用场景             |
| --------------- | -------- | --------------------------------- | -------------------- |
| **pgvector**    | 向量检索 | HNSW/IVFFlat 索引、多种距离度量   | AI/ML、推荐系统、RAG |
| **TimescaleDB** | 时序数据 | Hypertable、连续聚合、压缩        | IoT、监控、金融数据  |
| **PostGIS**     | 地理空间 | Geometry/Geography 类型、空间索引 | LBS、地图、空间分析  |
| **Citus**       | 分布式   | 分片、分布式查询、横向扩展        | 多租户 SaaS、大数据  |

## 权威参考

- PostgreSQL 扩展机制：`<https://www.postgresql.org/docs/current/extend.html`>
- pgvector：`<https://github.com/pgvector/pgvector`>
- TimescaleDB：`<https://docs.timescale.com/`>
- PostGIS：`<https://postgis.net/`>
- Citus：`<https://docs.citusdata.com/`>

## 快速开始

### 扩展安装通用流程

```sql
-- 1. 检查可用扩展
SELECT * FROM pg_available_extensions WHERE name IN ('vector', 'timescaledb', 'postgis', 'citus');

-- 2. 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS citus;

-- 3. 查看已安装扩展
SELECT extname, extversion FROM pg_extension;

-- 4. 更新扩展
ALTER EXTENSION vector UPDATE TO '0.7.0';
```

### 扩展组合使用示例

```sql
-- 示例1：TimescaleDB + PostGIS（时空数据）
CREATE TABLE iot_locations (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT,
    location GEOGRAPHY(POINT, 4326),
    temperature NUMERIC
);

SELECT create_hypertable('iot_locations', 'time');
CREATE INDEX idx_location ON iot_locations USING GIST (location);

-- 示例2：Citus + pgvector（分布式向量检索）
CREATE TABLE distributed_embeddings (
    id BIGSERIAL,
    user_id BIGINT NOT NULL,
    embedding vector(384),
    PRIMARY KEY (id, user_id)
);

SELECT create_distributed_table('distributed_embeddings', 'user_id');
CREATE INDEX idx_embedding ON distributed_embeddings USING hnsw (embedding vector_l2_ops);
```

## Checklist（扩展选择与使用）

- [ ] 评估扩展的活跃度和社区支持
- [ ] 确认扩展与 PostgreSQL 版本兼容性
- [ ] 测试扩展对性能的影响
- [ ] 规划扩展的升级和回滚策略
- [ ] 监控扩展相关的资源使用
- [ ] 建立扩展故障的应急预案

## 常见问题

### Q1: 扩展冲突如何处理？

- 检查扩展依赖：`SELECT * FROM pg_depend WHERE refclassid = 'pg_extension'::regclass;`
- 避免功能重叠的扩展同时使用
- 按需加载，不同 schema 隔离

### Q2: 扩展升级注意事项？

- 在测试环境先验证
- 检查 CHANGELOG 中的破坏性变更
- 做好数据备份
- 准备回滚方案

### Q3: 扩展性能优化？

- 合理配置扩展参数
- 针对扩展特性建立适当索引
- 监控扩展相关指标
- 定期 ANALYZE 扩展相关表

## 扩展评测

### 性能指标

- 写入吞吐量（TPS）
- 查询延迟（P50/P95/P99）
- 资源使用（CPU/内存/磁盘）
- 索引大小与构建时间

### 稳定性指标

- 扩展升级兼容性
- 故障恢复能力
- 并发处理能力
- 长期运行稳定性

## 参考案例

- AI 向量检索：`../05_ai_vector/pgvector/`
- 时序数据处理：`../06_timeseries/timescaledb/`
- 分布式数据库：`../08_ecosystem_cases/distributed_db/citus_demo/`

## 延伸阅读

- 分布式数据库理论：`../04_modern_features/distributed_db/README.md`
- 实战案例集：`../08_ecosystem_cases/README.md`
- 性能测试方法：`../10_benchmarks/README.md`
