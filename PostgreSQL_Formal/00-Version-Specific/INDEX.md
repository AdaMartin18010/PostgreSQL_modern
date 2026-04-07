# PostgreSQL 版本特定文档索引

> 📅 最后更新: 2026-04-07

本文档索引汇总 `00-Version-Specific` 目录下的所有版本相关文档。

---

## 📚 旧版本档案 (PG16 及以下)

### 核心档案文档

| 文档 | 说明 | 状态 |
|------|------|------|
| **[ARCHIVE.md](./ARCHIVE.md)** | PostgreSQL 版本历史档案，包含版本生命周期、EOL日期、各版本重要特性回顾 | ✅ 完整 |
| **[VERSION-COMPARISON.md](./VERSION-COMPARISON.md)** | 版本对比矩阵，从性能、SQL功能、管理运维、安全、复制等维度对比 PG10-PG16 | ✅ 完整 |
| **[UPGRADE-PATHS.md](./UPGRADE-PATHS.md)** | 升级路径指南，推荐升级路径、兼容性矩阵、风险评估 | ✅ 完整 |
| **[FEATURE-EVOLUTION.md](./FEATURE-EVOLUTION.md)** | 特性演进时间线，按特性类别展示 PG9.5-PG17+ 的演进 | ✅ 完整 |

---

## 📂 子目录结构

```
PostgreSQL_Formal/00-Version-Specific/
├── ARCHIVE.md                    # 版本历史档案
├── VERSION-COMPARISON.md         # 版本对比矩阵
├── UPGRADE-PATHS.md              # 升级路径指南
├── FEATURE-EVOLUTION.md          # 特性演进时间线
├── INDEX.md                      # 本索引文件
│
├── 17-Released/                  # PG17 已发布特性
│   ├── INDEX.md
│   ├── 17.01-VACUUM-Memory-Optimization-DEEP-V2.md
│   ├── 17.02-Incremental-Backup-DEEP-V2.md
│   ├── 17.03-JSON_TABLE-DEEP-V2.md
│   ├── 17.04-MERGE-Enhancements-DEEP-V2.md
│   ├── 17.05-Logical-Replication-Upgrades-DEEP-V2.md
│   ├── 17.06-pg_maintain-Role-DEEP-V2.md
│   ├── 17.07-Monitoring-Diagnostics-DEEP-V2.md
│   └── 17.08-Upgrade-Guide-DEEP-V2.md
│
├── 18-Released/                  # PG18 已发布特性
│   ├── INDEX.md
│   ├── 18.01-AIO-DEEP-V2.md
│   ├── 18.02-SkipScan-DEEP-V2.md
│   ├── 18.03-UUIDv7-DEEP-V2.md
│   ├── 18.04-Virtual-Generated-Columns-DEEP-V2.md
│   ├── 18.05-Temporal-Constraints-DEEP-V2.md
│   ├── 18.06-OAuth2-Integration-DEEP-V2.md
│   ├── 18.07-Parallel-GIN-Build-DEEP-V2.md
│   ├── 18.08-pg_upgrade-Enhancements-DEEP-V2.md
│   ├── 18.09-pgvector-DEEP-V2.md
│   ├── 18.10-CloudNativePG-DEEP-V2.md
│   ├── 18.11-OpenTelemetry-DEEP-V2.md
│   └── 18.12-LZ4-Compression-DEEP-V2.md
│
├── 19-Preview/                   # PG19 预览/规划
│   ├── ROADMAP.md
│   └── SOURCES.md
│
├── benchmarks/                   # 基准测试
│   ├── incremental-backup-benchmark/
│   ├── json-table-benchmark/
│   └── vacuum-memory-benchmark/
│
└── config/                       # 配置文件
    ├── postgresql16.conf
    ├── postgresql17.conf
    └── postgresql18.conf
```

---

## 🗓️ 版本支持状态

| 版本 | 发布日期 | EOL日期 | 状态 |
|------|----------|---------|------|
| PG 18 | 2025-09 | 2030-11 | 🔵 最新稳定版 |
| PG 17 | 2024-09 | 2029-11 | 🔵 维护中 |
| PG 16 | 2023-09 | 2028-11 | 🔵 维护中 |
| PG 15 | 2022-10 | 2027-11 | 🔵 维护中 |
| PG 14 | 2021-09 | 2026-11 | 🟡 即将EOL |
| PG 13 | 2020-09 | 2025-11 | 🔴 已停止支持 |
| PG 12 | 2019-10 | 2024-11 | 🔴 已停止支持 |
| PG 11 | 2018-10 | 2023-11 | 🔴 已停止支持 |
| PG 10 | 2017-10 | 2022-11 | 🔴 已停止支持 |

---

## 📖 使用指南

### 查看版本历史

- 访问 [ARCHIVE.md](./ARCHIVE.md) 了解各版本生命周期和关键特性

### 选择目标版本

- 查看 [VERSION-COMPARISON.md](./VERSION-COMPARISON.md) 对比不同版本的功能差异

### 规划升级

- 参考 [UPGRADE-PATHS.md](./UPGRADE-PATHS.md) 制定升级计划

### 了解特性演进

- 查看 [FEATURE-EVOLUTION.md](./FEATURE-EVOLUTION.md) 深入了解特定功能的演进历程

---

## 🔗 相关链接

- [PostgreSQL 官方发布说明](https://www.postgresql.org/docs/release/)
- [PostgreSQL 版本支持政策](https://www.postgresql.org/support/versioning/)
- [PostgreSQL EOL 日期](https://eosl.date/eol/product/postgresql/)

---

*文档维护: PostgreSQL 中文社区*
