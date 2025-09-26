# 12_comparison_wiki_uni

> 版本对标（更新于 2025-09）

## 目标

- 对照国际 wiki 与高校课程/教材/论文，将本仓库主题映射到外部权威知识体系，突出差异与互补。

## 对照结构

- 主题（本仓库） → 国际 wiki 条目 → 高校课程/教材章节 → 差异点/补充点

## 建议条目（骨架）

- SQL/DDL/DCL → Wikipedia: SQL / DDL / DCL → 教材相应章节 → 方言差异与 PostgreSQL 实现
- 事务与并发（ACID/MVCC/隔离级别）→ Wikipedia: ACID / MVCC → 课程讲义 → SSI/锁模型差异
- 存储与访问（索引/计划/统计）→ Wikipedia: B-tree/GiST/BRIN → 课程讲义 → 优化与代价估算
- 现代特性（分区/复制/备份/全文/FDW）→ Wikipedia 相应条目 → 课程/教材 → 工程经验与陷阱
- 向量/时序/地理/分布式 → Wikipedia/项目 Wiki → 课程专题 → 工具链与评测

### 新增：分布式数据库对照

- 分布式数据库（本仓库：`04_modern_features/distributed_db/README.md`）
  → Wikipedia：Distributed database / Consistency model / Raft
  → 课程：MIT 6.824、CMU 15-445/645（分布式专题）
  → 差异/补充：基于 PostgreSQL 的工程化落地（Citus/FDW/逻辑复制），评测与 SRE 清单

## 统一入口

- Wikipedia（按主题检索）：`https://en.wikipedia.org/`
- PostgreSQL 官方：`https://www.postgresql.org/`
- CMU 15-445：`https://15445.courses.cs.cmu.edu/`
- MIT 6.824：`https://pdos.csail.mit.edu/6.824/`

## 维护策略

- 对照项新增时，同步在各主题 README 的“对标/延伸阅读”中添加跳转。
- 每季度巡检，确保链接可用并更新差异说明。
