# PostgreSQL 统一术语表（GLOSSARY）

> **最后更新**：2025-10-03  
> **术语总数**：52个  
> **分类**：7大类（PostgreSQL核心、索引与存储、事务与并发、复制与高可用、扩展生态、分布式数据库、运维监控）

---

## 📑 快速索引（按字母排序）

- [PostgreSQL 统一术语表（GLOSSARY）](#postgresql-统一术语表glossary)
  - [📑 快速索引（按字母排序）](#-快速索引按字母排序)
  - [1. PostgreSQL 核心（15个）](#1-postgresql-核心15个)
    - [ACID](#acid)
    - [MVCC](#mvcc)
    - [WAL](#wal)
    - [PITR](#pitr)
    - [HOT](#hot)
    - [TOAST](#toast)
    - [SSI](#ssi)
    - [Autovacuum](#autovacuum)
    - [Checkpoint](#checkpoint)
    - [LSN](#lsn)
    - [XID](#xid)
    - [CTID](#ctid)
    - [FILLFACTOR](#fillfactor)
    - [Vacuum](#vacuum)
    - [Bloat](#bloat)
  - [2. 索引与存储（10个）](#2-索引与存储10个)
    - [B-tree](#b-tree)
    - [GIN](#gin)
    - [GiST](#gist)
    - [BRIN](#brin)
    - [SP-GiST](#sp-gist)
    - [Hash Index](#hash-index)
    - [HNSW](#hnsw)
    - [IVFFlat](#ivfflat)
    - [Bitmap Index Scan](#bitmap-index-scan)
    - [Index-Only Scan](#index-only-scan)
  - [3. 事务与并发（8个）](#3-事务与并发8个)
    - [Serializable](#serializable)
    - [Repeatable Read](#repeatable-read)
    - [Read Committed](#read-committed)
    - [Row Lock](#row-lock)
    - [Table Lock](#table-lock)
    - [Deadlock](#deadlock)
    - [Long Transaction](#long-transaction)
    - [Two-Phase Locking (2PL)](#two-phase-locking-2pl)
  - [4. 复制与高可用（8个）](#4-复制与高可用8个)
    - [Streaming Replication](#streaming-replication)
    - [Logical Replication](#logical-replication)
    - [Replication Slot](#replication-slot)
    - [WAL Sender](#wal-sender)
    - [WAL Receiver](#wal-receiver)
    - [Synchronous Commit](#synchronous-commit)
    - [Cascading Replication](#cascading-replication)
    - [Failover](#failover)
  - [5. 扩展生态（12个）](#5-扩展生态12个)
    - [pgvector](#pgvector)
    - [TimescaleDB](#timescaledb)
    - [PostGIS](#postgis)
    - [Citus](#citus)
    - [Hypertable](#hypertable)
    - [Continuous Aggregate](#continuous-aggregate)
    - [Compression](#compression)
    - [Shard](#shard)
    - [Coordinator](#coordinator)
    - [Worker](#worker)
    - [Reference Table](#reference-table)
    - [Distributed Table](#distributed-table)
  - [6. 分布式数据库（10个）](#6-分布式数据库10个)
    - [2PC](#2pc)
    - [Saga](#saga)
    - [Outbox Pattern](#outbox-pattern)
    - [Raft](#raft)
    - [Paxos](#paxos)
    - [CAP](#cap)
    - [BASE](#base)
    - [HTAP](#htap)
    - [Sharding](#sharding)
    - [RAG](#rag)
  - [7. 运维监控（8个）](#7-运维监控8个)
    - [Connection Pooling](#connection-pooling)
    - [PgBouncer](#pgbouncer)
    - [pgBackRest](#pgbackrest)
    - [pg\_stat\_statements](#pg_stat_statements)
    - [EXPLAIN](#explain)
    - [ANALYZE](#analyze)
    - [Auto\_explain](#auto_explain)
    - [Slow Query Log](#slow-query-log)
  - [📚 参考资源](#-参考资源)

---

## 1. PostgreSQL 核心（15个）

### ACID

- **英文全称**：Atomicity, Consistency, Isolation, Durability
- **中文翻译**：原子性、一致性、隔离性、持久性
- **说明**：数据库事务的四大特性，保证数据库操作的可靠性
- **相关链接**：[PostgreSQL文档 - 事务](https://www.postgresql.org/docs/17/tutorial-transactions.html)

### MVCC

- **英文全称**：Multi-Version Concurrency Control
- **中文翻译**：多版本并发控制
- **说明**：PostgreSQL的并发控制机制，通过保存数据的多个版本实现高并发读写
- **相关链接**：[Wikipedia - MVCC](https://en.wikipedia.org/wiki/Multiversion_concurrency_control)

### WAL

- **英文全称**：Write-Ahead Logging
- **中文翻译**：预写日志
- **说明**：PostgreSQL的事务日志系统，先写日志再修改数据页，保证数据持久性
- **相关链接**：[PostgreSQL文档 - WAL](https://www.postgresql.org/docs/17/wal-intro.html)

### PITR

- **英文全称**：Point-In-Time Recovery
- **中文翻译**：时间点恢复
- **说明**：通过WAL日志将数据库恢复到过去某个精确时间点
- **相关链接**：[PostgreSQL文档 - PITR](https://www.postgresql.org/docs/17/continuous-archiving.html)

### HOT

- **英文全称**：Heap-Only Tuple
- **中文翻译**：仅堆元组
- **说明**：PostgreSQL的UPDATE优化技术，当更新不涉及索引列时避免更新索引
- **相关链接**：[PostgreSQL Wiki - HOT](https://wiki.postgresql.org/wiki/Heap_Only_Tuples)

### TOAST

- **英文全称**：The Oversized-Attribute Storage Technique
- **中文翻译**：超大属性存储技术
- **说明**：PostgreSQL存储大字段（>2KB）的压缩和外部存储机制
- **相关链接**：[PostgreSQL文档 - TOAST](https://www.postgresql.org/docs/17/storage-toast.html)

### SSI

- **英文全称**：Serializable Snapshot Isolation
- **中文翻译**：可串行化快照隔离
- **说明**：PostgreSQL实现SERIALIZABLE隔离级别的算法，避免序列化异常
- **相关链接**：[PostgreSQL文档 - SSI](https://www.postgresql.org/docs/17/transaction-iso.html#XACT-SERIALIZABLE)

### Autovacuum

- **中文翻译**：自动清理进程
- **说明**：后台进程，自动回收死元组、更新统计信息、防止事务ID回卷
- **相关链接**：[PostgreSQL文档 - Autovacuum](https://www.postgresql.org/docs/17/routine-vacuuming.html#AUTOVACUUM)

### Checkpoint

- **中文翻译**：检查点
- **说明**：将脏页（dirty pages）从共享缓冲区刷到磁盘的时间点，恢复时的起点
- **相关链接**：[PostgreSQL文档 - Checkpoint](https://www.postgresql.org/docs/17/wal-configuration.html)

### LSN

- **英文全称**：Log Sequence Number
- **中文翻译**：日志序列号
- **说明**：WAL日志中的位置标识，64位整数，用于标识WAL记录的位置
- **相关链接**：[PostgreSQL文档 - pg_lsn](https://www.postgresql.org/docs/17/datatype-pg-lsn.html)

### XID

- **英文全称**：Transaction ID
- **中文翻译**：事务ID
- **说明**：32位整数，标识每个事务，用于MVCC可见性判断，需要定期冻结防止回卷
- **相关链接**：[PostgreSQL文档 - Transaction ID](https://www.postgresql.org/docs/17/routine-vacuuming.html#VACUUM-FOR-WRAPAROUND)

### CTID

- **英文全称**：Current Tuple ID
- **中文翻译**：当前元组标识
- **说明**：元组的物理位置（page号 + offset），类似行指针，会随UPDATE/VACUUM变化
- **相关链接**：[PostgreSQL文档 - System Columns](https://www.postgresql.org/docs/17/ddl-system-columns.html)

### FILLFACTOR

- **中文翻译**：填充因子
- **说明**：表或索引页的填充比例（默认100），预留空间用于HOT更新，减少页分裂
- **相关链接**：[PostgreSQL文档 - Storage Parameters](https://www.postgresql.org/docs/17/sql-createtable.html#SQL-CREATETABLE-STORAGE-PARAMETERS)

### Vacuum

- **中文翻译**：清理
- **说明**：回收死元组占用的空间，更新统计信息，防止表膨胀和事务ID回卷
- **相关链接**：[PostgreSQL文档 - VACUUM](https://www.postgresql.org/docs/17/sql-vacuum.html)

### Bloat

- **中文翻译**：表膨胀
- **说明**：死元组未及时回收导致的表/索引空间浪费，影响查询性能
- **相关链接**：[PostgreSQL Wiki - Bloat](https://wiki.postgresql.org/wiki/Show_database_bloat)

---

## 2. 索引与存储（10个）

### B-tree

- **英文全称**：Balanced Tree
- **中文翻译**：平衡树索引
- **说明**：PostgreSQL默认索引类型，支持等值和范围查询，自平衡多路搜索树
- **相关链接**：[PostgreSQL文档 - B-tree](https://www.postgresql.org/docs/17/indexes-types.html#INDEXES-TYPES-BTREE)

### GIN

- **英文全称**：Generalized Inverted Index
- **中文翻译**：通用倒排索引
- **说明**：用于全文搜索、JSONB、数组等多值列的索引，适合包含查询（@>）
- **相关链接**：[PostgreSQL文档 - GIN](https://www.postgresql.org/docs/17/gin.html)

### GiST

- **英文全称**：Generalized Search Tree
- **中文翻译**：通用搜索树
- **说明**：可扩展索引框架，用于PostGIS空间数据、范围类型、全文搜索
- **相关链接**：[PostgreSQL文档 - GiST](https://www.postgresql.org/docs/17/gist.html)

### BRIN

- **英文全称**：Block Range Index
- **中文翻译**：块范围索引
- **说明**：适合大表按序存储的数据，索引体积小，查询速度中等，节省存储空间
- **相关链接**：[PostgreSQL文档 - BRIN](https://www.postgresql.org/docs/17/brin.html)

### SP-GiST

- **英文全称**：Space-Partitioned Generalized Search Tree
- **中文翻译**：空间分区通用搜索树
- **说明**：用于非平衡数据结构（如四叉树、K-D树），适合地理数据、IP地址
- **相关链接**：[PostgreSQL文档 - SP-GiST](https://www.postgresql.org/docs/17/spgist.html)

### Hash Index

- **中文翻译**：哈希索引
- **说明**：仅支持等值查询，PostgreSQL 10后支持WAL日志，性能与B-tree接近
- **相关链接**：[PostgreSQL文档 - Hash](https://www.postgresql.org/docs/17/indexes-types.html#INDEXES-TYPES-HASH)

### HNSW

- **英文全称**：Hierarchical Navigable Small World
- **中文翻译**：分层可导航小世界图
- **说明**：pgvector的向量索引算法，查询速度快（ANN），构建时间长，适合高QPS场景
- **相关链接**：[pgvector文档 - HNSW](https://github.com/pgvector/pgvector#hnsw)

### IVFFlat

- **英文全称**：Inverted File with Flat Compression
- **中文翻译**：倒排文件索引
- **说明**：pgvector的另一种向量索引，构建快，查询略慢，适合中等规模数据
- **相关链接**：[pgvector文档 - IVFFlat](https://github.com/pgvector/pgvector#ivfflat)

### Bitmap Index Scan

- **中文翻译**：位图索引扫描
- **说明**：组合多个索引的查询结果（OR/AND），通过位图降低随机I/O
- **相关链接**：[PostgreSQL文档 - Bitmap Scan](https://www.postgresql.org/docs/17/indexes-bitmap-scans.html)

### Index-Only Scan

- **中文翻译**：仅索引扫描
- **说明**：查询只需要索引列，不回表读取数据页，大幅提升性能（需要Visibility Map）
- **相关链接**：[PostgreSQL文档 - Index-Only Scan](https://www.postgresql.org/docs/17/indexes-index-only-scans.html)

---

## 3. 事务与并发（8个）

### Serializable

- **中文翻译**：可串行化
- **说明**：最高隔离级别，通过SSI算法避免所有异常现象（幻读、写偏斜等）
- **相关链接**：[PostgreSQL文档 - Serializable](https://www.postgresql.org/docs/17/transaction-iso.html#XACT-SERIALIZABLE)

### Repeatable Read

- **中文翻译**：可重复读
- **说明**：PostgreSQL的默认推荐隔离级别，避免脏读和不可重复读，可能出现幻读
- **相关链接**：[PostgreSQL文档 - Repeatable Read](https://www.postgresql.org/docs/17/transaction-iso.html#XACT-REPEATABLE-READ)

### Read Committed

- **中文翻译**：读已提交
- **说明**：PostgreSQL的默认隔离级别，每个语句看到最新提交的数据
- **相关链接**：[PostgreSQL文档 - Read Committed](https://www.postgresql.org/docs/17/transaction-iso.html#XACT-READ-COMMITTED)

### Row Lock

- **中文翻译**：行级锁
- **说明**：FOR UPDATE/SHARE/NO KEY UPDATE/KEY SHARE四种行锁，控制并发修改
- **相关链接**：[PostgreSQL文档 - Row Locks](https://www.postgresql.org/docs/17/explicit-locking.html#LOCKING-ROWS)

### Table Lock

- **中文翻译**：表级锁
- **说明**：8种表锁模式（ACCESS SHARE到ACCESS EXCLUSIVE），控制DDL/DML并发
- **相关链接**：[PostgreSQL文档 - Table Locks](https://www.postgresql.org/docs/17/explicit-locking.html#LOCKING-TABLES)

### Deadlock

- **中文翻译**：死锁
- **说明**：两个或多个事务相互等待对方持有的锁，PostgreSQL自动检测并终止一个事务
- **相关链接**：[PostgreSQL文档 - Deadlocks](https://www.postgresql.org/docs/17/explicit-locking.html#LOCKING-DEADLOCKS)

### Long Transaction

- **中文翻译**：长事务
- **说明**：运行时间过长的事务，阻塞VACUUM回收死元组，导致表膨胀
- **相关链接**：[PostgreSQL文档 - Long Transactions](https://www.postgresql.org/docs/17/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW)

### Two-Phase Locking (2PL)

- **中文翻译**：两阶段锁
- **说明**：事务分为增长阶段（获取锁）和缩减阶段（释放锁），保证可串行化
- **相关链接**：[Wikipedia - 2PL](https://en.wikipedia.org/wiki/Two-phase_locking)

---

## 4. 复制与高可用（8个）

### Streaming Replication

- **中文翻译**：流式复制
- **说明**：PostgreSQL的物理复制，主库实时传输WAL日志到备库，延迟低（毫秒级）
- **相关链接**：[PostgreSQL文档 - Streaming Replication](https://www.postgresql.org/docs/17/warm-standby.html#STREAMING-REPLICATION)

### Logical Replication

- **中文翻译**：逻辑复制
- **说明**：基于表级/行级的复制，支持跨版本、跨平台、选择性复制
- **相关链接**：[PostgreSQL文档 - Logical Replication](https://www.postgresql.org/docs/17/logical-replication.html)

### Replication Slot

- **中文翻译**：复制槽
- **说明**：保留备库需要的WAL日志，防止日志被归档删除，确保备库不丢数据
- **相关链接**：[PostgreSQL文档 - Replication Slots](https://www.postgresql.org/docs/17/warm-standby.html#STREAMING-REPLICATION-SLOTS)

### WAL Sender

- **中文翻译**：WAL发送进程
- **说明**：主库的后台进程，负责向备库发送WAL日志
- **相关链接**：[PostgreSQL文档 - WAL Sender](https://www.postgresql.org/docs/17/warm-standby.html#STREAMING-REPLICATION-SENDER)

### WAL Receiver

- **中文翻译**：WAL接收进程
- **说明**：备库的后台进程，负责接收主库的WAL日志并应用
- **相关链接**：[PostgreSQL文档 - WAL Receiver](https://www.postgresql.org/docs/17/warm-standby.html#STREAMING-REPLICATION-STANDBY)

### Synchronous Commit

- **中文翻译**：同步提交
- **说明**：事务提交等待备库确认WAL写入，保证零数据丢失（RPO=0）
- **相关链接**：[PostgreSQL文档 - Synchronous Commit](https://www.postgresql.org/docs/17/runtime-config-wal.html#GUC-SYNCHRONOUS-COMMIT)

### Cascading Replication

- **中文翻译**：级联复制
- **说明**：备库作为其他备库的主库，减轻主库的复制压力
- **相关链接**：[PostgreSQL文档 - Cascading Replication](https://www.postgresql.org/docs/17/warm-standby.html#CASCADING-REPLICATION)

### Failover

- **中文翻译**：故障转移
- **说明**：主库故障时，提升备库为新主库，恢复服务可用性
- **相关链接**：[PostgreSQL文档 - Failover](https://www.postgresql.org/docs/17/warm-standby-failover.html)

---

## 5. 扩展生态（12个）

### pgvector

- **说明**：PostgreSQL的向量数据库扩展，支持存储和搜索向量数据（AI embedding）
- **相关链接**：[GitHub - pgvector](https://github.com/pgvector/pgvector)

### TimescaleDB

- **说明**：基于PostgreSQL的时序数据库扩展，提供自动分区、连续聚合、数据压缩
- **相关链接**：[TimescaleDB官网](https://www.timescale.com/)

### PostGIS

- **说明**：PostgreSQL的地理空间扩展，支持2D/3D几何、地理坐标、空间索引
- **相关链接**：[PostGIS官网](https://postgis.net/)

### Citus

- **说明**：PostgreSQL的分布式扩展，支持水平分片、分布式查询、多租户SaaS
- **相关链接**：[Citus官网](https://www.citusdata.com/)

### Hypertable

- **中文翻译**：超表
- **说明**：TimescaleDB的核心概念，自动按时间分区的表，对应用透明
- **相关链接**：[TimescaleDB文档 - Hypertable](https://docs.timescale.com/use-timescale/latest/hypertables/)

### Continuous Aggregate

- **中文翻译**：连续聚合
- **说明**：TimescaleDB的物化视图，增量更新，加速聚合查询（如1分钟/1小时指标）
- **相关链接**：[TimescaleDB文档 - Continuous Aggregate](https://docs.timescale.com/use-timescale/latest/continuous-aggregates/)

### Compression

- **中文翻译**：数据压缩
- **说明**：TimescaleDB的列式压缩，节省70-90%存储空间，查询性能影响小
- **相关链接**：[TimescaleDB文档 - Compression](https://docs.timescale.com/use-timescale/latest/compression/)

### Shard

- **中文翻译**：分片
- **说明**：Citus的数据分区单元，将表水平切分到多个Worker节点
- **相关链接**：[Citus文档 - Sharding](https://docs.citusdata.com/en/stable/sharding/data_modeling.html)

### Coordinator

- **中文翻译**：协调节点
- **说明**：Citus的主节点，接收查询并分发到Worker节点，聚合结果
- **相关链接**：[Citus文档 - Coordinator](https://docs.citusdata.com/en/stable/get_started/concepts.html#coordinator-node)

### Worker

- **中文翻译**：工作节点
- **说明**：Citus的数据节点，存储分片数据并执行查询
- **相关链接**：[Citus文档 - Worker](https://docs.citusdata.com/en/stable/get_started/concepts.html#worker-nodes)

### Reference Table

- **中文翻译**：引用表
- **说明**：Citus的全量复制表（如字典表），每个Worker节点保存完整数据
- **相关链接**：[Citus文档 - Reference Table](https://docs.citusdata.com/en/stable/sharding/data_modeling.html#reference-tables)

### Distributed Table

- **中文翻译**：分布式表
- **说明**：Citus的分片表，数据按Shard Key分布到多个Worker节点
- **相关链接**：[Citus文档 - Distributed Table](https://docs.citusdata.com/en/stable/sharding/data_modeling.html#distributed-tables)

---

## 6. 分布式数据库（10个）

### 2PC

- **英文全称**：Two-Phase Commit
- **中文翻译**：两阶段提交
- **说明**：分布式事务协议，Prepare阶段预提交，Commit阶段最终提交
- **相关链接**：[PostgreSQL文档 - 2PC](https://www.postgresql.org/docs/17/sql-prepare-transaction.html)

### Saga

- **中文翻译**：长事务补偿模式
- **说明**：将长事务拆分为多个本地事务，失败时执行补偿操作（逆操作）
- **相关链接**：[Wikipedia - Saga Pattern](https://en.wikipedia.org/wiki/Saga_pattern)

### Outbox Pattern

- **中文翻译**：发件箱模式
- **说明**：将消息写入本地事务表（outbox），异步发送到消息队列，保证最终一致性
- **相关链接**：[Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html)

### Raft

- **说明**：分布式共识算法，选举Leader、日志复制、安全性保证，易于理解
- **相关链接**：[Raft官网](https://raft.github.io/)

### Paxos

- **说明**：经典分布式共识算法，理论严谨但难以实现，Raft的理论基础
- **相关链接**：[Wikipedia - Paxos](https://en.wikipedia.org/wiki/Paxos_(computer_science))

### CAP

- **英文全称**：Consistency, Availability, Partition Tolerance
- **中文翻译**：一致性、可用性、分区容错性
- **说明**：分布式系统三选二定理，实际工程中权衡CP或AP
- **相关链接**：[Wikipedia - CAP](https://en.wikipedia.org/wiki/CAP_theorem)

### BASE

- **英文全称**：Basically Available, Soft State, Eventually Consistent
- **中文翻译**：基本可用、软状态、最终一致
- **说明**：与ACID相对的分布式系统设计理念，牺牲强一致性换取可用性
- **相关链接**：[Wikipedia - BASE](https://en.wikipedia.org/wiki/Eventual_consistency)

### HTAP

- **英文全称**：Hybrid Transactional/Analytical Processing
- **中文翻译**：混合事务分析处理
- **说明**：同时支持OLTP和OLAP负载的数据库架构（如列存+行存）
- **相关链接**：[Wikipedia - HTAP](https://en.wikipedia.org/wiki/Hybrid_transactional/analytical_processing)

### Sharding

- **中文翻译**：分片
- **说明**：将数据水平切分到多个节点，实现横向扩展，常见策略：Hash/Range/Directory
- **相关链接**：[Wikipedia - Sharding](https://en.wikipedia.org/wiki/Shard_(database_architecture))

### RAG

- **英文全称**：Retrieval-Augmented Generation
- **中文翻译**：检索增强生成
- **说明**：AI大模型技术，结合向量检索（pgvector）和生成模型（GPT）
- **相关链接**：[RAG论文](https://arxiv.org/abs/2005.11401)

---

## 7. 运维监控（8个）

### Connection Pooling

- **中文翻译**：连接池
- **说明**：复用数据库连接，减少连接开销，提升并发性能（如PgBouncer）
- **相关链接**：[PostgreSQL文档 - Connection Pooling](https://www.postgresql.org/docs/17/runtime-config-connection.html)

### PgBouncer

- **说明**：轻量级PostgreSQL连接池，支持Session/Transaction/Statement三种模式
- **相关链接**：[PgBouncer官网](https://www.pgbouncer.org/)

### pgBackRest

- **说明**：企业级PostgreSQL备份恢复工具，支持全量/增量/差异备份、并行恢复
- **相关链接**：[pgBackRest官网](https://pgbackrest.org/)

### pg_stat_statements

- **说明**：查询统计扩展，记录每个SQL的执行次数、耗时、I/O等，用于性能分析
- **相关链接**：[PostgreSQL文档 - pg_stat_statements](https://www.postgresql.org/docs/17/pgstatstatements.html)

### EXPLAIN

- **说明**：查看SQL执行计划的命令，分析查询性能瓶颈
- **相关链接**：[PostgreSQL文档 - EXPLAIN](https://www.postgresql.org/docs/17/sql-explain.html)

### ANALYZE

- **说明**：更新表统计信息的命令，优化器依赖统计信息生成执行计划
- **相关链接**：[PostgreSQL文档 - ANALYZE](https://www.postgresql.org/docs/17/sql-analyze.html)

### Auto_explain

- **说明**：自动记录慢查询执行计划的扩展，用于生产环境调优
- **相关链接**：[PostgreSQL文档 - auto_explain](https://www.postgresql.org/docs/17/auto-explain.html)

### Slow Query Log

- **中文翻译**：慢查询日志
- **说明**：记录超过阈值的SQL语句（log_min_duration_statement参数）
- **相关链接**：[PostgreSQL文档 - Slow Query Log](https://www.postgresql.org/docs/17/runtime-config-logging.html#GUC-LOG-MIN-DURATION-STATEMENT)

---

## 📚 参考资源

- **PostgreSQL官方文档**：<https://www.postgresql.org/docs/17/>
- **PostgreSQL Wiki**：<https://wiki.postgresql.org/>
- **Wikipedia数据库词汇**：<https://en.wikipedia.org/wiki/Category:Database_management_systems>
- **CMU 15-445课程术语表**：<https://15445.courses.cs.cmu.edu/fall2024/>

---

**维护者**：PostgreSQL_modern Project Team  
**贡献指南**：如需添加新术语，请提交Issue或PR  
**最后更新**：2025-10-03
