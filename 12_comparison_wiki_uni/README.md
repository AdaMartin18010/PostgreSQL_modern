# 12_comparison_wiki_uni — Wikipedia 与外部资源对照

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **模块完整度**：⭐⭐⭐⭐ 80%（已建立完整映射，持续更新）  
> **目标**：将本项目主题映射到 Wikipedia、课程、教材等权威知识体系

---

## 📋 目录

- [模块定位](#模块定位)
- [1. 核心概念 Wikipedia 映射](#1-核心概念wikipedia映射)
- [2. 模块级 Wikipedia 对照](#2-模块级wikipedia对照)
- [3. PostgreSQL 特有概念](#3-postgresql特有概念)
- [4. 外部资源统一入口](#4-外部资源统一入口)
- [5. 差异说明](#5-差异说明)

---

## 模块定位

### 目标

- **建立映射**：将本项目每个模块与 Wikipedia 条目建立对照
- **互补关系**：Wikipedia 提供通用理论，本项目提供 PostgreSQL 实现
- **学习导航**：从本项目到外部资源的快速跳转

### 对照结构

```text
本项目模块 ←→ Wikipedia条目 ←→ CMU课程 ←→ 差异点/补充
```

---

## 1. 核心概念 Wikipedia 映射

### 数据库基础概念

| 概念                                 | Wikipedia 条目                                             | 本项目对应章节                                                      |
| ------------------------------------ | ---------------------------------------------------------- | ------------------------------------------------------------------- |
| **Relational Model**                 | <https://en.wikipedia.org/wiki/Relational_model>           | [01_sql_ddl_dcl](../01_sql_ddl_dcl/README.md)                       |
| **Relational Algebra**               | <https://en.wikipedia.org/wiki/Relational_algebra>         | [01_sql_ddl_dcl § 3.1](../01_sql_ddl_dcl/README.md#31-查询基础)     |
| **SQL**                              | <https://en.wikipedia.org/wiki/SQL>                        | [01_sql_ddl_dcl](../01_sql_ddl_dcl/README.md)                       |
| **Data Definition Language (DDL)**   | <https://en.wikipedia.org/wiki/Data_definition_language>   | [01_sql_ddl_dcl § 2](../01_sql_ddl_dcl/README.md#2-ddl数据定义)     |
| **Data Manipulation Language (DML)** | <https://en.wikipedia.org/wiki/Data_manipulation_language> | [01_sql_ddl_dcl § 3](../01_sql_ddl_dcl/README.md#3-dml数据操纵)     |
| **Data Control Language (DCL)**      | <https://en.wikipedia.org/wiki/Data_control_language>      | [01_sql_ddl_dcl § 4](../01_sql_ddl_dcl/README.md#4-dcl数据控制)     |
| **Database Normalization**           | <https://en.wikipedia.org/wiki/Database_normalization>     | [01_sql_ddl_dcl § 2.2](../01_sql_ddl_dcl/README.md#22-表设计与约束) |

---

### 事务与并发控制

| 概念                                        | Wikipedia 条目                                                   | 本项目对应章节                                                           |
| ------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **ACID**                                    | <https://en.wikipedia.org/wiki/ACID>                             | [02_transactions § 1](../02_transactions/README.md#1-acid特性与实现)     |
| **Database Transaction**                    | <https://en.wikipedia.org/wiki/Database_transaction>             | [02_transactions](../02_transactions/README.md)                          |
| **Multiversion Concurrency Control (MVCC)** | <https://en.wikipedia.org/wiki/Multiversion_concurrency_control> | [02_transactions § 2](../02_transactions/README.md#2-mvcc多版本并发控制) |
| **Isolation (database systems)**            | <https://en.wikipedia.org/wiki/Isolation_(database_systems)>     | [02_transactions § 3](../02_transactions/README.md#3-事务隔离级别)       |
| **Snapshot Isolation**                      | <https://en.wikipedia.org/wiki/Snapshot_isolation>               | [02_transactions § 3.3](../02_transactions/README.md#33-repeatable-read) |
| **Serializability**                         | <https://en.wikipedia.org/wiki/Serializability>                  | [02_transactions § 3.4](../02_transactions/README.md#34-serializablessi) |
| **Two-phase Locking**                       | <https://en.wikipedia.org/wiki/Two-phase_locking>                | [02_transactions § 4](../02_transactions/README.md#4-锁机制)             |
| **Deadlock**                                | <https://en.wikipedia.org/wiki/Deadlock>                         | [02_transactions § 4.4](../02_transactions/README.md#44-死锁检测与处理)  |
| **Write-ahead Logging (WAL)**               | <https://en.wikipedia.org/wiki/Write-ahead_logging>              | [02_transactions § 1.1](../02_transactions/README.md#11-原子性atomicity) |

---

### 存储与索引

| 概念                            | Wikipedia 条目                                                             | 本项目对应章节                                                           |
| ------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Database Storage Structures** | <https://en.wikipedia.org/wiki/Database_storage_structures>                | [03_storage_access § 1](../03_storage_access/README.md#1-存储结构)       |
| **B-tree**                      | <https://en.wikipedia.org/wiki/B-tree>                                     | [03_storage_access § 2.1](../03_storage_access/README.md#21-b-tree索引)  |
| **B+ tree**                     | <https://en.wikipedia.org/wiki/B%2B_tree>                                  | [03_storage_access § 2.1](../03_storage_access/README.md#21-b-tree索引)  |
| **Hash Table**                  | <https://en.wikipedia.org/wiki/Hash_table>                                 | [03_storage_access § 2.2](../03_storage_access/README.md#22-hash索引)    |
| **Inverted Index**              | <https://en.wikipedia.org/wiki/Inverted_index>                             | [03_storage_access § 2.3](../03_storage_access/README.md#23-gin索引)     |
| **R-tree**                      | <https://en.wikipedia.org/wiki/R-tree>                                     | [03_storage_access § 2.4](../03_storage_access/README.md#24-gist索引)    |
| **Bitmap Index**                | <https://en.wikipedia.org/wiki/Bitmap_index>                               | [03_storage_access § 2.5](../03_storage_access/README.md#25-brin索引)    |
| **Query Plan**                  | <https://en.wikipedia.org/wiki/Query_plan>                                 | [03_storage_access § 3](../03_storage_access/README.md#3-执行计划分析)   |
| **Query Optimization**          | <https://en.wikipedia.org/wiki/Query_optimization>                         | [03_storage_access § 4](../03_storage_access/README.md#4-统计信息)       |
| **Cost-based Optimizer**        | <https://en.wikipedia.org/wiki/Query_optimization#Cost-based_optimization> | [03_storage_access § 4.1](../03_storage_access/README.md#41-analyze原理) |

---

### 分布式数据库

| 概念                             | Wikipedia 条目                                                | 本项目对应章节                                                                                                                    |
| -------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Distributed Database**         | <https://en.wikipedia.org/wiki/Distributed_database>          | [04_modern_features/distributed_db](../04_modern_features/distributed_db/README.md)                                               |
| **Database Sharding**            | <https://en.wikipedia.org/wiki/Shard_(database_architecture)> | [04_modern_features/distributed_db/sharding_replication.md](../04_modern_features/distributed_db/sharding_replication.md)         |
| **Database Replication**         | <https://en.wikipedia.org/wiki/Replication_(computing)>       | [04_modern_features/replication_topologies.md](../04_modern_features/replication_topologies.md)                                   |
| **CAP Theorem**                  | <https://en.wikipedia.org/wiki/CAP_theorem>                   | [04_modern_features/distributed_db/concepts_overview.md](../04_modern_features/distributed_db/concepts_overview.md)               |
| **Consistency Model**            | <https://en.wikipedia.org/wiki/Consistency_model>             | [04_modern_features/distributed_db/consistency_consensus.md](../04_modern_features/distributed_db/consistency_consensus.md)       |
| **Eventual Consistency**         | <https://en.wikipedia.org/wiki/Eventual_consistency>          | [04_modern_features/distributed_db/consistency_consensus.md](../04_modern_features/distributed_db/consistency_consensus.md)       |
| **Consensus (computer science)** | <https://en.wikipedia.org/wiki/Consensus_(computer_science)>  | [04_modern_features/distributed_db/consistency_consensus.md](../04_modern_features/distributed_db/consistency_consensus.md)       |
| **Paxos (computer science)**     | <https://en.wikipedia.org/wiki/Paxos_(computer_science)>      | [04_modern_features/distributed_db/consistency_consensus.md](../04_modern_features/distributed_db/consistency_consensus.md)       |
| **Raft (algorithm)**             | <https://en.wikipedia.org/wiki/Raft_(algorithm)>              | [04_modern_features/distributed_db/consistency_consensus.md](../04_modern_features/distributed_db/consistency_consensus.md)       |
| **Two-phase Commit Protocol**    | <https://en.wikipedia.org/wiki/Two-phase_commit_protocol>     | [08_ecosystem_cases/distributed_db/two_phase_commit_min.sql](../08_ecosystem_cases/distributed_db/two_phase_commit_min.sql)       |
| **Three-phase Commit Protocol**  | <https://en.wikipedia.org/wiki/Three-phase_commit_protocol>   | [04_modern_features/distributed_db/distributed_transactions.md](../04_modern_features/distributed_db/distributed_transactions.md) |

---

### 特殊数据类型与扩展

| 概念                              | Wikipedia 条目                                                | 本项目对应章节                                                       |
| --------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------- |
| **Vector Database**               | <https://en.wikipedia.org/wiki/Vector_database>               | [05_ai_vector](../05_ai_vector/README.md)                            |
| **Nearest Neighbor Search**       | <https://en.wikipedia.org/wiki/Nearest_neighbor_search>       | [05_ai_vector/pgvector](../05_ai_vector/pgvector/README.md)          |
| **Time Series Database**          | <https://en.wikipedia.org/wiki/Time_series_database>          | [06_timeseries](../06_timeseries/README.md)                          |
| **Geographic Information System** | <https://en.wikipedia.org/wiki/Geographic_information_system> | [07_extensions/postgis](../07_extensions/postgis/README.md)          |
| **Full-text Search**              | <https://en.wikipedia.org/wiki/Full-text_search>              | [03_storage_access § 2.3](../03_storage_access/README.md#23-gin索引) |
| **JSON**                          | <https://en.wikipedia.org/wiki/JSON>                          | [01_sql_ddl_dcl § 1.1](../01_sql_ddl_dcl/README.md#11-数据类型全览)  |

---

## 2. 模块级 Wikipedia 对照

### 01_sql_ddl_dcl — SQL 语言基础

| 本项目章节         | Wikipedia 条目                                                                                                  | 差异与补充                                               |
| ------------------ | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **1.1 数据类型**   | [SQL Data Types](<https://en.wikipedia.org/wiki/SQL#Data_type>s)                                                | 本项目补充 PostgreSQL 特有类型（jsonb、array、range 等） |
| **1.2 标识符命名** | [Identifier (computer languages)](<https://en.wikipedia.org/wiki/Identifier_(computer_language>s))              | 本项目详解 PostgreSQL 大小写规则与命名陷阱               |
| **2.3 分区表**     | [Partition (database)](<https://en.wikipedia.org/wiki/Partition_(databas>e))                                    | 本项目提供 Range/List/Hash 三种分区的完整示例            |
| **3.3 CTE 与递归** | [Hierarchical and recursive queries](<https://en.wikipedia.org/wiki/Hierarchical_and_recursive_queries_in_SQ>L) | 本项目提供树遍历与图遍历防循环示例                       |
| **4.2 行级安全**   | [Row-level security](<https://en.wikipedia.org/wiki/Row-level_securit>y)                                        | 本项目提供多租户隔离完整教程                             |

**外部资源链接**：

- Wikipedia SQL：<https://en.wikipedia.org/wiki/SQL>
- PostgreSQL SQL 语法：<https://www.postgresql.org/docs/17/sql-syntax.html>
- CMU 15-445 Lecture 1-2：关系模型与 SQL 基础

---

### 02_transactions — 事务管理

| 本项目章节        | Wikipedia 条目                                                                       | 差异与补充                                 |
| ----------------- | ------------------------------------------------------------------------------------ | ------------------------------------------ |
| **1. ACID 特性**  | [ACID](<https://en.wikipedia.org/wiki/ACI>D)                                         | 本项目详解 PostgreSQL 的 WAL、fsync 实现   |
| **2. MVCC**       | [MVCC](<https://en.wikipedia.org/wiki/Multiversion_concurrency_contro>l)             | 本项目详解 xmin/xmax 可见性规则与 XID 冻结 |
| **3. 隔离级别**   | [Isolation](<https://en.wikipedia.org/wiki/Isolation_(database_system>s))            | 本项目提供 5 个异常现象可复现演示          |
| **4. 锁机制**     | [Lock (computer science)](<https://en.wikipedia.org/wiki/Lock_(computer_scienc>e))   | 本项目详解 PostgreSQL 8 种表锁+4 种行锁    |
| **6. 长事务管理** | [Long-running transaction](<https://en.wikipedia.org/wiki/Long-running_transactio>n) | 本项目提供监控 SQL 与治理策略              |

**外部资源链接**：

- Wikipedia MVCC：<https://en.wikipedia.org/wiki/Multiversion_concurrency_control>
- CMU 15-445 Lecture 17-19：并发控制
- 论文：Berenson et al. (1995) "A Critique of ANSI SQL Isolation Levels"

---

### 03_storage_access — 存储与访问

| 本项目章节           | Wikipedia 条目                                                                             | 差异与补充                                 |
| -------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------ |
| **1.1 堆表**         | [Database storage structures](<https://en.wikipedia.org/wiki/Database_storage_structure>s) | 本项目详解 PostgreSQL 8KB 页结构           |
| **1.2 TOAST**        | （PostgreSQL 特有）                                                                        | Wikipedia 无对应条目，本项目独家详解       |
| **2.1 B-tree**       | [B-tree](<https://en.wikipedia.org/wiki/B-tre>e)                                           | 本项目补充 PostgreSQL 17 多值搜索优化      |
| **2.3 GIN**          | [Inverted Index](<https://en.wikipedia.org/wiki/Inverted_inde>x)                           | 本项目提供 JSON/数组/全文搜索完整示例      |
| **3.4 执行计划优化** | [Query optimization](<https://en.wikipedia.org/wiki/Query_optimizatio>n)                   | 本项目提供 3 个真实优化案例                |
| **5.1 VACUUM**       | （PostgreSQL 特有）                                                                        | Wikipedia 无对应条目，本项目详解死元组清理 |

**外部资源链接**：

- Wikipedia B-tree：<https://en.wikipedia.org/wiki/B-tree>
- Use The Index, Luke!：<https://use-the-index-luke.com/>
- CMU 15-445 Lecture 7-8：树索引

---

### 04_modern_features/distributed_db — 分布式数据库

| 本项目章节                   | Wikipedia 条目                                                                     | 差异与补充                                   |
| ---------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------- |
| **concepts_overview**        | [Distributed database](<https://en.wikipedia.org/wiki/Distributed_databas>e)       | 本项目详解 CAP 权衡与工程实践                |
| **consistency_consensus**    | [Consensus](<https://en.wikipedia.org/wiki/Consensus_(computer_scienc>e))          | 本项目对比 Paxos/Raft 与 PostgreSQL 逻辑复制 |
| **sharding_replication**     | [Shard](<https://en.wikipedia.org/wiki/Shard_(database_architectur>e))             | 本项目详解 Hash/Range/Directory 三种分片策略 |
| **distributed_transactions** | [Two-phase commit](<https://en.wikipedia.org/wiki/Two-phase_commit_protoco>l)      | 本项目补充 Saga 模式与幂等性设计             |
| **htap_architecture**        | [HTAP](<https://en.wikipedia.org/wiki/Hybrid_transactional/analytical_processin>g) | 本项目详解行列混合存储与资源隔离             |

**外部资源链接**：

- Wikipedia CAP 定理：<https://en.wikipedia.org/wiki/CAP_theorem>
- MIT 6.824：分布式系统
- CMU 15-445 Lecture 22-24：分布式数据库

---

### 05_ai_vector — AI 向量数据库

| 本项目章节   | Wikipedia 条目                                                                     | 差异与补充                 |
| ------------ | ---------------------------------------------------------------------------------- | -------------------------- |
| **pgvector** | [Vector database](<https://en.wikipedia.org/wiki/Vector_databas>e)                 | 本项目提供 RAG 最小案例    |
| **向量检索** | [Nearest neighbor search](<https://en.wikipedia.org/wiki/Nearest_neighbor_searc>h) | 本项目对比 HNSW vs IVFFlat |

**外部资源链接**：

- Wikipedia Vector database：<https://en.wikipedia.org/wiki/Vector_database>
- pgvector GitHub：<https://github.com/pgvector/pgvector>

---

### 06_timeseries — 时序数据库

| 本项目章节      | Wikipedia 条目                                                               | 差异与补充               |
| --------------- | ---------------------------------------------------------------------------- | ------------------------ |
| **TimescaleDB** | [Time series database](<https://en.wikipedia.org/wiki/Time_series_databas>e) | 本项目详解超表与连续聚合 |

**外部资源链接**：

- Wikipedia Time series database：<https://en.wikipedia.org/wiki/Time_series_database>
- TimescaleDB 文档：<https://docs.timescale.com/>

---

### 07_extensions — 扩展生态

| 本项目章节  | Wikipedia 条目                                                                     | 差异与补充                |
| ----------- | ---------------------------------------------------------------------------------- | ------------------------- |
| **PostGIS** | [GIS](<https://en.wikipedia.org/wiki/Geographic_information_syste>m)               | 本项目提供地理查询示例    |
| **Citus**   | [Database sharding](<https://en.wikipedia.org/wiki/Shard_(database_architectur>e)) | 本项目详解 Citus 分片实践 |

---

## 3. PostgreSQL 特有概念

以下概念是 PostgreSQL 特有的，Wikipedia 无直接对应条目：

| PostgreSQL 概念                           | 本项目章节                                                                                          | 说明                                |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------- | ----------------------------------- |
| **TOAST**                                 | [03_storage_access § 1.2](../03_storage_access/README.md#12-toast超大字段)                          | 超大字段存储技术                    |
| **HOT 更新**                              | [03_storage_access § 1.3](../03_storage_access/README.md#13-fillfactor与页填充)                     | Heap-Only Tuple 更新优化            |
| **VACUUM**                                | [03_storage_access § 5.1](../03_storage_access/README.md#51-vacuum详解)                             | 死元组清理与 XID 冻结               |
| **Autovacuum**                            | [03_storage_access § 5.2](../03_storage_access/README.md#52-autovacuum配置)                         | 自动清理机制                        |
| **BRIN 索引**                             | [03_storage_access § 2.5](../03_storage_access/README.md#25-brin索引)                               | 块范围索引                          |
| **SSI (Serializable Snapshot Isolation)** | [02_transactions § 3.4](../02_transactions/README.md#34-serializablessi)                            | PostgreSQL 独有的 Serializable 实现 |
| **逻辑复制**                              | [04_modern_features/logical_replication_min.sql](../04_modern_features/logical_replication_min.sql) | 基于 WAL 的逻辑复制                 |
| **pg_stat_statements**                    | [03_storage_access § 7](../03_storage_access/README.md#7-性能调优实践)                              | 查询统计扩展                        |

**PostgreSQL 官方文档**：

- TOAST：<https://www.postgresql.org/docs/17/storage-toast.html>
- VACUUM：<https://www.postgresql.org/docs/17/sql-vacuum.html>
- SSI 论文：<https://drkp.net/papers/ssi-vldb12.pdf>

---

## 4. 外部资源统一入口

### Wikipedia 主要入口

| 主题                     | Wikipedia 条目                                                   |
| ------------------------ | ---------------------------------------------------------------- |
| **SQL**                  | <https://en.wikipedia.org/wiki/SQL>                              |
| **Database**             | <https://en.wikipedia.org/wiki/Database>                         |
| **Relational database**  | <https://en.wikipedia.org/wiki/Relational_database>              |
| **ACID**                 | <https://en.wikipedia.org/wiki/ACID>                             |
| **MVCC**                 | <https://en.wikipedia.org/wiki/Multiversion_concurrency_control> |
| **B-tree**               | <https://en.wikipedia.org/wiki/B-tree>                           |
| **Distributed database** | <https://en.wikipedia.org/wiki/Distributed_database>             |
| **CAP theorem**          | <https://en.wikipedia.org/wiki/CAP_theorem>                      |

### 官方文档

- **PostgreSQL 17 文档**：<https://www.postgresql.org/docs/17/>
- **PostgreSQL Wiki**：<https://wiki.postgresql.org/>
- **PostgreSQL 中文社区**：<https://www.postgres.cn/>

### 大学课程

- **CMU 15-445/645**：<https://15445.courses.cs.cmu.edu/>
- **MIT 6.824**：<https://pdos.csail.mit.edu/6.824/>
- **MIT 6.5830/6.5831**：<http://dsg.csail.mit.edu/6.5830/>
- **Stanford CS145**：<https://cs145-fa19.github.io/>
- **UC Berkeley CS186**：<https://cs186berkeley.net/>

### 经典教材

- **Database System Concepts**（Silberschatz）：<https://www.db-book.com/>
- **Readings in Database Systems**（Red Book）：<http://www.redbook.io/>

---

## 5. 差异说明

### 本项目 vs Wikipedia

| 维度     | Wikipedia          | 本项目              |
| -------- | ------------------ | ------------------- |
| **广度** | 涵盖所有数据库系统 | 专注 PostgreSQL 17  |
| **深度** | 概念性介绍         | 生产级实践+代码示例 |
| **实践** | 理论为主           | 150+可执行 SQL 示例 |
| **更新** | 社区编辑（较慢）   | 快速跟进 PG 新版本  |
| **中文** | 中文版质量参差     | 高质量中文技术文档  |

**互补关系**：

- **Wikipedia**：理解通用概念和历史背景
- **本项目**：学习 PostgreSQL 具体实现与生产实践

### 本项目 vs 大学课程

| 维度         | 大学课程              | 本项目               |
| ------------ | --------------------- | -------------------- |
| **理论深度** | 深厚（论文+数学证明） | 适度（重点工程实践） |
| **代码实践** | 课程作业（简化）      | 生产级案例           |
| **覆盖范围** | 广泛（多种 DB）       | PostgreSQL 专精      |
| **时效性**   | 1-2 年更新            | 紧跟 PG 版本         |

**互补关系**：

- **大学课程**：建立扎实的理论基础
- **本项目**：快速应用到 PostgreSQL 生产环境

---

## 维护策略

### 链接维护

- **季度巡检**：检查所有 Wikipedia 链接有效性
- **失效处理**：Wikipedia 链接长期稳定，如失效使用 Internet Archive
- **语言版本**：优先使用英文 Wikipedia（质量更高）

### 内容更新

- **随 PG 版本**：每个 PostgreSQL 大版本发布后更新对照
- **补充新概念**：PostgreSQL 新增特性及时补充到本对照表
- **社区反馈**：根据用户反馈补充遗漏的映射关系

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**下一步**：在各模块 README 头部添加外部资源快速链接
