---
name: Version Update Check / 版本更新检查
about: 定期检查PostgreSQL和扩展的版本更新（每月自动创建）
title: '[VERSION] 月度版本检查 YYYY-MM'
labels: 'version-check'
assignees: ''
---

## 📅 检查日期 / Check Date

**检查日期**：YYYY-MM-DD  
**检查周期**：月度（每月1号自动创建）

---

## 🔍 版本检查清单 / Version Check List

### 1. PostgreSQL核心

- [ ] **当前追踪版本**：17.0（2024-09发布）
- [ ] **最新稳定版本**：___ （检查 <https://www.postgresql.org/download/）>
- [ ] **是否需要更新文档**：是 / 否
- [ ] **更新说明**：

---

### 2. 核心扩展 / Core Extensions

#### 2.1 pgvector（向量检索）

- [ ] **当前追踪版本**：0.5.1
- [ ] **最新版本**：___ （检查 <https://github.com/pgvector/pgvector/releases）>
- [ ] **兼容性**：与PG17兼容 ✅ / 不兼容 ❌
- [ ] **是否需要更新**：是 / 否
- [ ] **更新内容**：

#### 2.2 TimescaleDB（时序数据）

- [ ] **当前追踪版本**：2.13.0
- [ ] **最新版本**：___ （检查 <https://github.com/timescale/timescaledb/releases）>
- [ ] **兼容性**：与PG17兼容 ✅ / 不兼容 ❌
- [ ] **是否需要更新**：是 / 否
- [ ] **更新内容**：

#### 2.3 PostGIS（地理空间）

- [ ] **当前追踪版本**：3.4.0
- [ ] **最新版本**：___ （检查 <https://postgis.net/news/）>
- [ ] **兼容性**：与PG17兼容 ✅ / 不兼容 ❌
- [ ] **是否需要更新**：是 / 否
- [ ] **更新内容**：

#### 2.4 Citus（分布式）

- [ ] **当前追踪版本**：12.1
- [ ] **最新版本**：___ （检查 <https://github.com/citusdata/citus/releases）>
- [ ] **兼容性**：与PG17兼容 ✅ / 不兼容 ❌
- [ ] **是否需要更新**：是 / 否
- [ ] **更新内容**：

---

### 3. 常用扩展 / Common Extensions

#### 3.1 pg_stat_statements

- [ ] **内置扩展**：随PG17发布
- [ ] **新特性**：

#### 3.2 pg_trgm（模糊搜索）

- [ ] **内置扩展**：随PG17发布
- [ ] **新特性**：

#### 3.3 其他扩展

- [ ] **hstore**：
- [ ] **uuid-ossp**：
- [ ] **postgres_fdw**：

---

## 📋 需要更新的文件清单 / Files to Update

### 文档更新

- [ ] `00_overview/README.md`（版本说明）
- [ ] `04_modern_features/version_diff_16_to_17.md`（若PG更新到17.1+）
- [ ] `04_modern_features/pg17_new_features.md`（新特性补充）
- [ ] `05_ai_vector/pgvector/README.md`（pgvector版本）
- [ ] `06_timeseries/timescaledb/README.md`（TimescaleDB版本）
- [ ] `07_extensions/postgis/README.md`（PostGIS版本）
- [ ] `07_extensions/citus/README.md`（Citus版本）
- [ ] `CHANGELOG.md`（记录版本更新）

### 代码示例更新

- [ ] `08_ecosystem_cases/ai_vector/rag_minimal/`（pgvector API变更）
- [ ] `08_ecosystem_cases/distributed_db/citus_demo/`（Citus配置变更）
- [ ] `06_timeseries/timescaledb/continuous_aggregate_example.sql`（TimescaleDB语法变更）

---

## 🚨 重大变更警告 / Breaking Changes

<!-- 如果有不兼容的变更，请在此详细说明 -->

### PostgreSQL核心

-

### 扩展生态

-

---

## ✅ 执行检查清单 / Execution Checklist

- [ ] 已检查所有版本链接
- [ ] 已验证兼容性（若有测试环境）
- [ ] 已识别需要更新的文件
- [ ] 已评估变更影响范围
- [ ] 已创建对应的更新Issue（若需要）
- [ ] 已更新CHANGELOG.md

---

## 📌 检查脚本 / Check Script

可以使用以下脚本自动检查版本（计划开发）：

```bash
# 运行版本检查脚本（待创建）
./tools/check_versions.sh
```

---

## 🔗 参考链接 / References

- PostgreSQL官方：<https://www.postgresql.org/support/versioning/>
- pgvector：<https://github.com/pgvector/pgvector>
- TimescaleDB：<https://docs.timescale.com/about/latest/release-notes/>
- PostGIS：<https://postgis.net/news/>
- Citus：<https://www.citusdata.com/updates/>

---

**维护者**：请在每月1号填写此检查清单  
**自动化**：计划通过GitHub Actions自动创建此Issue
