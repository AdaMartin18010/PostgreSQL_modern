# PostgreSQL 权威内容索引

> 本文档汇总 PostgreSQL 领域的权威内容来源，用于指导本项目的内容对齐与质量提升。
> 最后更新: 2026-04-07

---

## 目录

- [官方文档](#官方文档)
- [权威书籍](#权威书籍)
- [顶级课程](#顶级课程)
- [权威博客](#权威博客)
- [最新版本特性](#最新版本特性)
- [与本项目的对齐差距分析](#与本项目的对齐差距分析)

---

## 官方文档

| 资源 | 链接 | 内容范围 | 更新频率 | 中文可用性 |
|------|------|----------|----------|------------|
| **PostgreSQL 官方文档** | <https://www.postgresql.org/docs/> | 全部核心功能、SQL参考、管理指南 | 每版本更新 | 社区翻译版可用 |
| **PostgreSQL Release Notes** | <https://www.postgresql.org/docs/release/> | 新特性、变更说明、迁移指南 | 每年大版本 | 部分社区翻译 |
| **PostgreSQL Wiki** | <https://wiki.postgresql.org/> | 社区知识库、最佳实践、扩展列表 | 持续更新 | 有限 |
| **PostgreSQL Roadmap** | <https://www.postgresql.org/developer/roadmap/> | 版本计划、开发路线图 | 每年更新 | 无 |
| **PostgreSQL CommitFest** | <https://commitfest.postgresql.org/> | 补丁审核、开发进展 | 每两个月 | 无 |
| **EDB Documentation** | <https://www.enterprisedb.com/documentation> | 企业版特性、迁移指南 | 每版本更新 | 有限 |

---

## 权威书籍

### 核心必读书籍

| 书名 | 作者 | 出版年份 | 覆盖内容 | 推荐阅读 | 获取方式 |
|------|------|----------|----------|----------|----------|
| **PostgreSQL 14 Internals** | Egor Rogov | 2022-2023 | 源码级深度解析：MVCC、WAL、锁机制、查询执行、索引类型 | ⭐⭐⭐⭐⭐ 必读 | 免费PDF: postgrespro.com/community/books/internals |
| **Database Internals** | Alex Petrov | 2019 | 存储引擎(B-Tree/LSM)、事务、复制、分布式系统 | ⭐⭐⭐⭐⭐ 必读 | O'Reilly出版 |
| **Designing Data-Intensive Applications (DDIA)** | Martin Kleppmann | 2017 (2025第2版) | 数据模型、复制、分区、一致性、事务 | ⭐⭐⭐⭐⭐ 必读 | O'Reilly出版 |
| **PostgreSQL: Up and Running** | Regina Obe, Leo Hsu | 2021 (第4版) | 实用入门、配置优化、日常管理 | ⭐⭐⭐⭐ 推荐 | O'Reilly出版 |
| **The Art of PostgreSQL** | Dimitri Fontaine | 2020 | SQL编程、应用设计、性能最佳实践 | ⭐⭐⭐⭐ 推荐 | 独立出版 |

### 进阶参考书籍

| 书名 | 作者 | 覆盖内容 | 适用场景 |
|------|------|----------|----------|
| **PostgreSQL 16 Administration Cookbook** | Gianni Ciolli 等 | 生产环境管理、故障排查 | DBA运维 |
| **High Performance PostgreSQL for Rails** | Andrew Atkinson | Rails应用性能优化 | 应用开发者 |
| **Database System Implementation** | Hector Garcia-Molina 等 | 数据库内核实现原理 | 内核开发者 |
| **Readings in Database Systems (Red Book)** | Peter Bailis 等 | 经典论文集、前沿研究 | 学术研究者 |

---

## 顶级课程

### 卡内基梅隆大学 (CMU)

| 课程 | 讲师 | 内容 | 资源链接 | 难度 |
|------|------|------|----------|------|
| **CMU 15-445/645** | Andy Pavlo 等 | 数据库系统导论：存储、索引、查询执行、事务 | <https://15445.courses.cs.cmu.edu/> | ⭐⭐⭐⭐ 中级 |
| **CMU 15-721** | Andy Pavlo 等 | 高级数据库系统：OLAP、向量化执行、编译执行、现代系统分析 | <https://15721.courses.cs.cmu.edu/> | ⭐⭐⭐⭐⭐ 高级 |
| **CMU 15-799** |  rotating | 专题研讨：自驱动数据库、查询优化器等 | 见官网 | ⭐⭐⭐⭐⭐ 研究级 |

**课程特色**:

- 开源 BusTub 教学数据库项目
- YouTube 完整视频 (英文字幕)
- 作业支持 Gradescope 自动评测

### 斯坦福大学

| 课程 | 内容 | 资源链接 | 难度 |
|------|------|----------|------|
| **CS145** | 数据库入门：SQL、关系模型、基础设计 | <https://cs145-fa20.github.io/> | ⭐⭐⭐ 初级 |
| **CS245** | 数据密集型系统原理：存储、查询、事务 | <https://web.stanford.edu/class/cs245/> | ⭐⭐⭐⭐ 中级 |
| **CS346** | 数据库系统实现：从零实现RedBase | <https://cs346.stanford.edu/> | ⭐⭐⭐⭐⭐ 高级 |

**课程特色**:

- RedBase 项目完整实现数据库内核
- 配套经典教材《Database System Implementation》

### MIT

| 课程 | 内容 | 资源链接 | 难度 |
|------|------|----------|------|
| **6.5830/6.5831** (原6.830/6.814) | 数据库系统基础：关系代数、优化、事务 | <https://dsg.csail.mit.edu/6.5830/> | ⭐⭐⭐⭐ 中级 |

**课程特色**:

- SimpleDB 教学项目 (Java)
- 基于经典论文阅读 (Red Book)

### 其他优质课程

| 课程 | 机构 | 内容 | 链接 |
|------|------|------|------|
| **CS186** | UC Berkeley | 数据库系统实现 | <https://cs186berkeley.net/> |
| **CS4320** | Cornell | 数据库系统 | YouTube有视频 |

---

## 权威博客

### PostgreSQL 核心开发者博客

| 博客 | 作者/机构 | 特色内容 | 更新频率 | 链接 |
|------|-----------|----------|----------|------|
| **depesz.com** | Hubert Lubaczewski | "Waiting for PostgreSQL"系列、新特性深度解析 | 每周 | <https://www.depesz.com/> |
| **Postgres Professional** | Egor Rogov 等 | 内核详解、查询优化、索引原理 | 每月 | <https://postgrespro.com/blog/> |
| **Peter Eisentraut's Blog** | Peter Eisentraut (Core Team) | 开发内幕、标准化、扩展机制 | 不定期 | <http://peter.eisentraut.org/> |
| **2ndQuadrant Blog** | Simon Riggs 等 | 企业级特性、复制、高可用 | 每周 | <https://www.2ndquadrant.com/en/blog/> |
| **Percona Blog** | Ibrar Ahmed 等 | 性能调优、监控、生产实践 | 每周 | <https://www.percona.com/blog/> |
| **EDB Blog** | Bruce Momjian 等 | 企业应用、迁移、最佳实践 | 每周 | <https://www.enterprisedb.com/blog> |

### 社区技术博客

| 博客 | 特色内容 | 链接 |
|------|----------|------|
| **Robert Haas's Blog** | 内核开发、并行查询、优化器 | 见 PostgreSQL 社区 |
| **Tomas Vondra's Blog** | 性能优化、统计信息、规划器 | 个人博客 |
| **Andres Freund's Blog** | 存储层、WAL、性能剖析 | 见 GitHub/个人站点 |

---

## 最新版本特性

### PostgreSQL 17 (2024年9月发布)

**核心新特性**:

| 特性类别 | 具体特性 | 权威文档 |
|----------|----------|----------|
| **性能优化** | VACUUM内存使用降低20倍、流式I/O接口 | Official Release Notes |
| **SQL/JSON** | JSON_TABLE()函数、JSON_EXISTS/QUERY/VALUE | depesz.com 系列文章 |
| **逻辑复制** | 复制槽故障转移、pg_createsubscriber工具 | 官方文档 |
| **备份** | 增量备份 (pg_basebackup --incremental) | Percona博客 |
| **监控** | pg_wait_events视图、EXPLAIN内存统计 | 官方文档 |
| **安全** | MAINTAIN权限、sslnegotiation参数 | 官方文档 |

### PostgreSQL 18 (2025年9月发布)

**核心新特性**:

| 特性类别 | 具体特性 | 来源 |
|----------|----------|------|
| **存储** | 异步I/O (AIO) 框架、io_uring支持 | CommitFest 2025-03 |
| **查询优化** | 跳跃扫描 (Skip Scan)、并行GIN构建 | PostgresPro博客 |
| **数据类型** | UUIDv7支持、虚拟生成列 | 官方Release Notes |
| **复制** | 逻辑复制统计迁移、双向复制改进 | depesz.com |
| **运维** | REPACK命令整合VACUUM FULL/CLUSTER | CommitFest |
| **安全** | OAuth 2.0集成、增强审计 | EDB博客 |

### PostgreSQL 19 (2026年9月计划)

**开发中特性** (来自CommitFest和Waiting For系列):

| 特性 | 状态 | 说明 |
|------|------|------|
| GROUP BY ALL | 已提交 | 自动包含所有非聚合列 |
| pg_plan_advice | 开发中 | 查询计划提示与稳定化 |
| 向量类型 (SQL标准) | 计划中 | SQL:202y标准向量支持 |

---

## 与本项目的对齐差距分析

### 内容覆盖对比

| 本项目主题 | 权威来源覆盖 | 差距分析 | 建议行动 |
|------------|--------------|----------|----------|
| **MVCC与事务** | Egor Rogov《PostgreSQL 14 Internals》Part I深度覆盖 | 本项目有详细覆盖，但缺少形式化证明 | 参考本书实验验证方法 |
| **查询优化器** | CMU 15-721多节课+论文阅读 | 本项目覆盖较浅，缺少代价模型细节 | 补充CMU课程笔记 |
| **存储引擎** | 《Database Internals》B-Tree/LSM深度解析 | 本项目缺少LSM-Tree对比 | 补充存储引擎对比章节 |
| **分布式系统** | DDIA + CMU 15-721 | 本项目CAP理论覆盖充分，但缺Raft/Paxos细节 | 参考DDIA第9章 |
| **WAL与恢复** | 《PostgreSQL 14 Internals》Part II | 本项目覆盖较完整 | 保持同步 |
| **索引类型** | 《PostgreSQL 14 Internals》Part V | 本项目缺少SP-GiST/BRIN深度 | 补充Part V内容 |
| **PG 17/18新特性** | Release Notes + depesz.com | 本项目有新特性文档 | 需要系统整理 |

### 具体对齐建议

#### 1. 核心理论深度对齐

| 差距领域 | 权威参考 | 建议补充内容 |
|----------|----------|--------------|
| **查询优化代价模型** | CMU 15-445 Lecture 15 | 代价估算公式、统计信息收集 |
| **并发控制理论** | CMU 15-445 Lecture 16-19 | 2PL、MVCC、Serializable冲突检测 |
| **分布式一致性** | DDIA Ch. 8-9 | Linearizability、Consensus算法 |
| **LSM-Tree存储** | 《Database Internals》Ch. 2 | LSM vs B-Tree对比、LevelDB/RocksDB |

#### 2. 版本特性同步

| 版本 | 本项目状态 | 权威参考 | 建议 |
|------|------------|----------|------|
| **PostgreSQL 17** | 有独立文档 | 官方Release Notes | 创建版本特性对照表 |
| **PostgreSQL 18** | 文档较多但分散 | depesz.com系列 | 按模块整理新特性 |
| **PostgreSQL 19** | 缺少跟踪 | CommitFest | 添加开发中特性预览 |

#### 3. 实践案例补充

| 案例类型 | 权威来源 | 建议行动 |
|----------|----------|----------|
| **性能调优案例** | Percona博客系列 | 整理调优方法论 |
| **生产故障排查** | EDB/2ndQuadrant博客 | 补充故障案例库 |
| **扩展开发实战** | Peter Eisentraut博客 | 完善扩展开发指南 |

### 内容质量保证建议

1. **引用规范**: 对来自上述权威来源的内容明确标注出处
2. **定期同步**: 每季度检查权威博客和Release Notes，更新内容
3. **交叉验证**: 关键概念对比多个权威来源，确保准确性
4. **版本标注**: 所有特性说明标注适用的PostgreSQL版本
5. **学习路径**: 为读者提供基于这些权威资源的学习路径建议

---

## 附录: 快速参考

### 权威资源优先级

```
第一优先级 (核心):
- PostgreSQL Official Documentation
- Egor Rogov《PostgreSQL 14 Internals》
- CMU 15-445/721课程
- DDIA (Martin Kleppmann)

第二优先级 (补充):
- Alex Petrov《Database Internals》
- depesz.com博客
- PostgreSQL Release Notes

第三优先级 (扩展):
- Percona/EDB/2ndQuadrant博客
- Stanford/MIT课程
- 学术论文 (VLDB/SIGMOD)
```

### 版本跟踪检查清单

- [ ] 每年9月更新PostgreSQL大版本特性
- [ ] 每两个月查看CommitFest进展
- [ ] 每周浏览depesz.com新文章
- [ ] 每季度检查Postgres Professional博客
- [ ] 持续跟踪CMU数据库课程更新

---

*本文档为动态维护文档，建议每季度评审更新。*
