# PostgreSQL 18 新特性文档索引

> **版本**: PostgreSQL 18 (2025-09-25 发布)
> **索引创建日期**: 2026-04-07
> **文档总数**: 12 篇

---

## 📋 文档列表

### 🔧 核心特性 (Core Features)

| 序号 | 文档 | 特性描述 | 状态 |
|------|------|----------|------|
| 18.01 | [AIO 异步 I/O](./18.01-AIO-DEEP-V2.md) | Linux io_uring 异步 I/O 支持 | ✅ 核心特性 |
| 18.02 | [Skip Scan](./18.02-SkipScan-DEEP-V2.md) | B-tree 索引跳跃扫描优化 | ✅ 核心特性 |
| 18.03 | [UUIDv7](./18.03-UUIDv7-DEEP-V2.md) | 新版 UUID v7 支持 | ✅ 核心特性 |
| 18.04 | [虚拟生成列](./18.04-Virtual-Generated-Columns-DEEP-V2.md) | Virtual Generated Columns | ✅ 核心特性 |
| 18.05 | [时态约束](./18.05-Temporal-Constraints-DEEP-V2.md) | Temporal Constraints | ⚠️ 需核实 |
| 18.06 | [OAuth2 集成](./18.06-OAuth2-Integration-DEEP-V2.md) | OAuth2/SSO 认证集成 | ✅ 核心特性 |
| 18.07 | [并行 GIN 构建](./18.07-Parallel-GIN-Build-DEEP-V2.md) | 并行 GIN 索引构建 | ✅ 核心特性 |
| 18.08 | [pg_upgrade 增强](./18.08-pg_upgrade-Enhancements-DEEP-V2.md) | 版本升级工具增强 | ✅ 核心特性 |
| 18.11 | [OpenTelemetry](./18.11-OpenTelemetry-DEEP-V2.md) | 可观测性集成 | ✅ 核心特性 |
| 18.12 | [LZ4 压缩](./18.12-LZ4-Compression-DEEP-V2.md) | LZ4 压缩算法支持 | ✅ 核心特性 |

### 🔌 扩展与工具 (Extensions & Tools)

| 序号 | 文档 | 描述 | 类型 |
|------|------|------|------|
| 18.09 | [pgvector](./18.09-pgvector-DEEP-V2.md) | 向量数据库扩展 | 🔌 第三方扩展 |
| 18.10 | [CloudNativePG](./18.10-CloudNativePG-DEEP-V2.md) | K8s PostgreSQL Operator | 🛠️ 外部工具 |

---

## ⚠️ 重要说明

### 时态约束特性状态

**18.05-Temporal-Constraints-DEEP-V2.md** 中的时态约束特性在 PG17 开发周期中被回滚。
请在 PostgreSQL 18 正式发布后核实该特性是否正式包含。

### 扩展与工具说明

- **pgvector**: 需要单独安装 `CREATE EXTENSION vector;`
- **CloudNativePG**: 由 EDB 维护的独立 Kubernetes Operator 项目

---

## 🚀 快速导航

### 按类别浏览

**性能优化**

- [18.01 AIO 异步 I/O](./18.01-AIO-DEEP-V2.md)
- [18.02 Skip Scan](./18.02-SkipScan-DEEP-V2.md)
- [18.07 并行 GIN 构建](./18.07-Parallel-GIN-Build-DEEP-V2.md)
- [18.12 LZ4 压缩](./18.12-LZ4-Compression-DEEP-V2.md)

**数据类型与约束**

- [18.03 UUIDv7](./18.03-UUIDv7-DEEP-V2.md)
- [18.04 虚拟生成列](./18.04-Virtual-Generated-Columns-DEEP-V2.md)
- [18.05 时态约束](./18.05-Temporal-Constraints-DEEP-V2.md)

**安全与认证**

- [18.06 OAuth2 集成](./18.06-OAuth2-Integration-DEEP-V2.md)

**运维与监控**

- [18.08 pg_upgrade 增强](./18.08-pg_upgrade-Enhancements-DEEP-V2.md)
- [18.11 OpenTelemetry](./18.11-OpenTelemetry-DEEP-V2.md)

**AI 与云原生**

- [18.09 pgvector](./18.09-pgvector-DEEP-V2.md)
- [18.10 CloudNativePG](./18.10-CloudNativePG-DEEP-V2.md)

---

## 📁 原文档位置

这些文档从 `PostgreSQL_Formal/00-NewFeatures-18/` 迁移而来。
迁移日期: 2026-04-07
