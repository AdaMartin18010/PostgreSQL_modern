# PostgreSQL_Formal 纯知识梳理计划

> **日期**: 2026-04-07
> **定位**: 纯开源技术知识库
> **目标**: 修复无效链接，对齐权威内容，确保准确性

---

## 🎯 核心原则

```
纯知识梳理 = 内容准确性 + 权威对齐 + 结构清晰

❌ 不做: 社区运营、视频、翻译、商业化
✅ 只做: 知识整理、权威对齐、质量保障
```

---

## 📊 当前状态 (已重新核实)

### 版本状态 (基于 2026-04-07)

| 版本 | 发布日期 | 状态 | 本项目覆盖 |
|------|----------|------|------------|
| **PG 17** | 2024-09-26 | 稳定版 | ✅ 8篇文档 |
| **PG 18** | 2025-09-25 | 已发布(6个月) | ✅ 12篇文档 |
| **PG 19** | 2026-09 | 开发中 | 🚧 跟踪中 |

### 问题清单

| 问题 | 数量 | 优先级 |
|------|------|--------|
| 失效链接 | 67个 | P0 |
| 社区运营文件 | 9个 | P0 |
| 配置参数待核实 | 若干 | P1 |
| 权威来源引用 | 缺失 | P1 |

---

## 📋 任务计划

### 阶段 1: 清理与修复 (1周)

#### 任务 1.1: 修复失效链接 ⚠️ P0

| 子任务 | 数量 | 操作 |
|--------|------|------|
| 修复文件不存在链接 | 5个 | 修正路径 |
| 修复锚点链接 | 62个 | 统一编码 |
| 全站验证 | 全量 | 确保100% |

**涉及文件**:

- DOCKER_GUIDE.md - emoji锚点
- BENCHMARK-SUMMARY.md - 重复标题
- 各文档下划线锚点

#### 任务 1.2: 删除非知识文件 ⚠️ P0

**删除清单**:

```
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── COMMUNITY.md
├── ROADMAP.md (项目路线图)
├── TRANSLATION_STRATEGY.md
├── CONTRIBUTING-TRANSLATION.md
├── README-en.md
├── .github/ (整个目录)
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
└── verify-environment.sh (可选)
```

**简化 README.md**:

- 移除社区贡献段落
- 移除翻译计划
- 保留核心知识导航

### 阶段 2: 权威对齐 (2-3周)

#### 任务 2.1: PG18 特性核实

对照官方文档核实:

- PostgreSQL 18 Release Notes
- PostgreSQL 18 官方文档
- 确认每项特性的准确性

| 特性 | 状态 | 核实来源 |
|------|------|----------|
| AIO 异步I/O | ✅ | Release Notes |
| Skip Scan | ✅ | Release Notes |
| UUIDv7 | ✅ | Release Notes |
| 虚拟生成列 | ✅ | Release Notes |
| 时态约束 | ✅ | Release Notes |
| OAuth2 | ✅ | Release Notes |

#### 任务 2.2: 配置参数核实

| 参数 | 当前文档 | 官方值 | 操作 |
|------|----------|--------|------|
| 认证方式 | md5 | scram-sha-256 | 更新 |
| io_method | 可能存在 | 不存在 | 删除 |
| max_io_workers | 可能存在 | 不存在 | 删除 |

#### 任务 2.3: 补充权威来源引用

每篇文档头部添加:

```markdown
## 权威来源
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [PG14 Internals](https://edu.postgrespro.com/postgresql_internals-14_en.pdf)
- [CMU 15-445](https://15445.courses.cs.cmu.edu/)
```

### 阶段 3: 知识重构 (2-4周)

#### 任务 3.1: 文档去重

基于审计报告，合并冗余文档:

- 保留 DEEP-V2 版本
- 归档旧版本
- 更新链接

#### 任务 3.2: 知识图谱完善

- 完善 KNOWLEDGE_GRAPH.yml
- 生成可视化导航
- 建立概念关联

#### 任务 3.3: 权威索引维护

维护 AUTHORITY_CONTENT_INDEX.md:

- 官方文档链接
- 权威书籍
- 顶级课程
- 技术博客

---

## 📚 权威来源清单

### 官方文档 (必须对齐)

| 来源 | URL | 优先级 |
|------|-----|--------|
| PostgreSQL官方文档 | postgresql.org/docs/current/ | P0 |
| PG17 Release Notes | postgresql.org/docs/17/release-17.html | P0 |
| PG18 Release Notes | postgresql.org/docs/18/release-18.html | P0 |

### 权威书籍 (参考)

| 书名 | 作者 | 用途 |
|------|------|------|
| PostgreSQL 14 Internals | Egor Rogov | 源码深度 |
| Database Internals | Alex Petrov | 通用原理 |
| Designing Data-Intensive Applications | Martin Kleppmann | 系统设计 |

### 顶级课程 (参考)

| 课程 | 机构 | 内容 |
|------|------|------|
| CMU 15-445/645 | CMU | 数据库系统 |
| CMU 15-721 | CMU | 高级数据库 |
| Stanford CS145 | Stanford | 数据库基础 |

---

## ✅ 验收标准

| 指标 | 目标 | 当前 |
|------|------|------|
| 链接有效性 | 100% | 98.1% |
| 内容准确性 | 对照官方 | 待核实 |
| 权威引用 | 每篇都有 | 部分缺失 |
| 知识纯度 | 无社区内容 | 有待删除 |

---

## ⏱️ 时间规划

| 阶段 | 时间 | 产出 |
|------|------|------|
| 阶段1 | 1周 | 链接修复报告、清理清单 |
| 阶段2 | 2-3周 | 核实报告、来源引用 |
| 阶段3 | 2-4周 | 重构报告、知识图谱 |

---

## 📝 输出文档

1. **LINK_FIX_REPORT.md** - 链接修复报告
2. **PG18_VERIFICATION.md** - PG18特性核实
3. **CLEANUP_REPORT.md** - 清理报告
4. **AUTHORITY_ALIGNMENT.md** - 权威对齐报告

---

**计划制定**: 2026-04-07
**定位**: 纯知识梳理
**状态**: 待确认执行
