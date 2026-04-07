# PostgreSQL_Formal Terminology Glossary

> **Document Status**: 🚧 Draft
> **Version**: v1.0
> **Total Terms**: 60+ core terms
> **Last Updated**: 2026-04-07

---

## How to Use This Glossary

- **Chinese**: Original term used in Chinese documentation
- **English**: Standard English translation
- **Notes**: Usage guidelines and context

Contributions welcome! See [CONTRIBUTING-TRANSLATION.md](CONTRIBUTING-TRANSLATION.md).

---

## Core Database Concepts (核心数据库概念)

| Chinese | English | Notes |
|---------|---------|-------|
| 多版本并发控制 | MVCC (Multi-Version Concurrency Control) | Always use acronym; PostgreSQL core mechanism |
| 预写式日志 | WAL (Write-Ahead Logging) | Always use acronym; durability mechanism |
| 事务 | Transaction | Atomic unit of work |
| 隔离级别 | Isolation Level | ANSI SQL: READ UNCOMMITTED, READ COMMITTED, etc. |
| 原子性 | Atomicity | ACID property |
| 一致性 | Consistency | ACID property; note: different from CAP consistency |
| 隔离性 | Isolation | ACID property |
| 持久性 | Durability | ACID property |
| 并发控制 | Concurrency Control | General term; includes MVCC and locking |
| 锁 | Lock / Locking | Mechanism for synchronization |
| 死锁 | Deadlock | Circular wait condition |
| 活锁 | Livelock | Non-blocking but no progress |
| 可串行化 | Serializable | Highest isolation level |
| 快照隔离 | Snapshot Isolation (SI) | Non-standard isolation level |
| 幻读 | Phantom Read | Anomaly type |
| 不可重复读 | Non-repeatable Read | Anomaly type |
| 脏读 | Dirty Read | Anomaly type |
| 丢失更新 | Lost Update | Anomaly type |

---

## PostgreSQL-Specific Terms (PostgreSQL 专用术语)

| Chinese | English | Notes |
|---------|---------|-------|
| 元组 | Tuple | Database row/record; don't use "row" in formal contexts |
| 页面 | Page | 8KB storage unit; "block" also acceptable |
| 缓冲区 | Buffer Pool | Shared memory for caching pages |
| 清理 | VACUUM | Always uppercase; space reclamation process |
| 自动清理 | Autovacuum | Background VACUUM process |
| 冻结 | Freeze | Transaction ID wraparound prevention |
| TOAST | TOAST | The Oversized-Attribute Storage Technique |
| 堆表 | Heap Table | Default table storage format |
| 追加优化表 | Append-Optimized Table | For append-mostly workloads |
| 可见性映射 | Visibility Map | VM; tracks all-visible pages |
| 空闲空间映射 | Free Space Map | FSM; tracks available space |
| 预写日志 | Write-Ahead Log | WAL; full term |
| 检查点 | Checkpoint | Point of consistency |
| 归档 | Archive / Archiving | WAL archiving for PITR |
| 基础备份 | Base Backup | Full database backup |
| 增量备份 | Incremental Backup | Backup of changed blocks only (PG17+) |

---

## Index Types (索引类型)

| Chinese | English | Notes |
|---------|---------|-------|
| B树索引 | B-tree Index | Default index type |
| 哈希索引 | Hash Index | For equality operations |
| GiST索引 | GiST Index | Generalized Search Tree |
| GIN索引 | GIN Index | Generalized Inverted Index |
| SP-GiST索引 | SP-GiST Index | Space-Partitioned GiST |
| BRIN索引 | BRIN Index | Block Range Index |
| 部分索引 | Partial Index | Index with WHERE clause |
| 表达式索引 | Expression Index | Index on expression/func |
| 覆盖索引 | Covering Index | Index-only scan capable |
| 唯一索引 | Unique Index | Enforces uniqueness |

---

## Query Processing (查询处理)

| Chinese | English | Notes |
|---------|---------|-------|
| 查询优化器 | Query Optimizer | Also "planner" in PostgreSQL |
| 执行器 | Executor | Query execution engine |
| 代价模型 | Cost Model | Mathematical cost estimation |
| 统计信息 | Statistics | Table/column statistics for planning |
| 选择率 | Selectivity | Fraction of rows selected |
| 基数估计 | Cardinality Estimation | Row count estimation |
| 连接 | Join | Combine tables |
| 嵌套循环连接 | Nested Loop Join | Join algorithm |
| 哈希连接 | Hash Join | Join algorithm |
| 归并连接 | Merge Join | Join algorithm; also "sort-merge join" |
| 顺序扫描 | Sequential Scan | Full table scan |
| 索引扫描 | Index Scan | Access via index |
| 位图索引扫描 | Bitmap Index Scan | Index + heap combination |
| 仅索引扫描 | Index-Only Scan | Covering index access |
| 并行查询 | Parallel Query | Parallel execution |
| JIT编译 | JIT Compilation | Just-In-Time code generation |

---

## Storage Engine (存储引擎)

| Chinese | English | Notes |
|---------|---------|-------|
| 存储引擎 | Storage Engine | Table access method layer |
| 访问方法 | Access Method | Table/index AM interface |
| 表空间 | Tablespace | Physical storage location |
| 数据目录 | Data Directory | PGDATA location |
| 关系 | Relation | Table, index, or sequence |
| 系统目录 | System Catalog | Metadata tables (pg_*) |
|  OID | OID | Object Identifier |
| TID | TID | Tuple Identifier (ctid) |
| LSN | LSN | Log Sequence Number |
| XID | XID | Transaction ID |
| CID | CID | Command ID |
| MVCC快照 | MVCC Snapshot | Transaction visibility state |
| 提示位 | Hint Bits | Optimization flags in tuple header |
| 行指针 | Line Pointer | ItemIdData; offset in page |
| 填充因子 | Fillfactor | Space reservation percentage |

---

## Replication & Distributed (复制与分布式)

| Chinese | English | Notes |
|---------|---------|-------|
| 流复制 | Streaming Replication | Physical replication |
| 逻辑复制 | Logical Replication | Row-level logical replication |
| 发布 | Publication | Logical replication source |
| 订阅 | Subscription | Logical replication target |
| 故障转移 | Failover | Switch to standby |
| 切换 | Switchover | Planned failover |
| 热备 | Hot Standby | Readable standby |
| 同步复制 | Synchronous Replication | Durability guarantee |
| 异步复制 | Asynchronous Replication | Performance-priority replication |
| 级联复制 | Cascading Replication | Standby-of-standby |
| 分片 | Sharding | Horizontal partitioning |
| 分区 | Partitioning | Table partitioning |
| 两阶段提交 | Two-Phase Commit | 2PC; distributed transaction protocol |
| 三阶段提交 | Three-Phase Commit | 3PC; enhanced 2PC |
| Raft协议 | Raft Protocol | Consensus algorithm |

---

## Formal Methods (形式化方法)

| Chinese | English | Notes |
|---------|---------|-------|
| 形式化规范 | Formal Specification | Mathematical specification |
| 形式化验证 | Formal Verification | Mathematical proof of correctness |
| TLA+ | TLA+ | Temporal Logic of Actions |
| PlusCal | PlusCal | TLA+ algorithm language |
| 时序逻辑 | Temporal Logic | Logic with time operators |
| 不变量 | Invariant | Property that always holds |
| 活性 | Liveness | "Something good eventually happens" |
| 安全性 | Safety | "Nothing bad happens" |
| 模型检测 | Model Checking | Automated verification |
| 定理证明 | Theorem Proving | Interactive proof assistance |
| 状态空间 | State Space | All possible states |
| 死状态 | Deadlock State | State with no valid actions |

---

## Performance & Monitoring (性能与监控)

| Chinese | English | Notes |
|---------|---------|-------|
| 等待事件 | Wait Event | Performance bottleneck indicator |
| 锁等待 | Lock Wait | Blocking lock event |
| I/O等待 | I/O Wait | Disk/network wait |
| 缓冲区命中率 | Buffer Hit Ratio | Cache efficiency metric |
| 事务吞吐量 | Transaction Throughput | TPS; transactions per second |
| 查询延迟 | Query Latency | Response time |
| 执行计划 | Execution Plan | Query plan; EXPLAIN output |
| 慢查询 | Slow Query | Long-running query |
| 连接池 | Connection Pool | Connection management |
| 工作内存 | Work Memory | Per-operation memory |
| 共享缓冲区 | Shared Buffers | Shared memory cache |
| 有效缓存大小 | Effective Cache Size | Planner cache assumption |
| 维护工作内存 | Maintenance Work Mem | VACUUM, CREATE INDEX memory |

---

## Security & Administration (安全与管理)

| Chinese | English | Notes |
|---------|---------|-------|
| 角色 | Role | User/group entity |
| 权限 | Privilege | Access right |
| 模式 | Schema | Namespace for objects |
| 行级安全 | Row-Level Security | RLS; fine-grained access control |
| 强制访问控制 | Mandatory Access Control | MAC; SELinux integration |
| SSL/TLS | SSL/TLS | Encryption protocol |
| 证书 | Certificate | X.509 authentication |
| 审计日志 | Audit Log | Security event logging |
| pg_hba.conf | pg_hba.conf | Host-based authentication config |
| 转储 | Dump | pg_dump output |
| 恢复 | Restore | pg_restore process |

---

## Version-Specific Features (版本特性)

| Chinese | English | Notes |
|---------|---------|-------|
| 异步I/O | Asynchronous I/O | AIO; PG18 feature |
| 跳跃扫描 | Skip Scan | B-tree optimization; PG18 |
| 生成列 | Generated Column | Computed column; PG12+ |
| 虚拟生成列 | Virtual Generated Column | On-the-fly computation; PG18 |
| 时态约束 | Temporal Constraints | Time-based validity; PG18 |
| JSON_TABLE | JSON_TABLE | SQL/JSON function; PG17 |
| MERGE语句 | MERGE Statement | UPSERT alternative; PG15+ |

---

## Acronyms Reference (缩写速查)

| Acronym | Full Name | Context |
|---------|-----------|---------|
| ACID | Atomicity, Consistency, Isolation, Durability | Transaction properties |
| MVCC | Multi-Version Concurrency Control | Concurrency mechanism |
| WAL | Write-Ahead Logging | Durability mechanism |
| LSN | Log Sequence Number | WAL position |
| XID | Transaction ID | Transaction identifier |
| TID | Tuple ID / Item Pointer | Row location |
| OID | Object Identifier | System object ID |
| AM | Access Method | Table/index interface |
| AMs | Access Methods | Plural |
| JIT | Just-In-Time | Compilation |
| TLA+ | Temporal Logic of Actions | Specification language |
| 2PC | Two-Phase Commit | Distributed protocol |
| 3PC | Three-Phase Commit | Distributed protocol |
| SI | Snapshot Isolation | Isolation level |
| SSI | Serializable Snapshot Isolation | PostgreSQL serializable |
| PG | PostgreSQL | Abbreviation |
| PG17 | PostgreSQL 17 | Version 17 |
| PG18 | PostgreSQL 18 | Version 18 |
| DCA | Database-Centric Architecture | Architecture pattern |
| TPS | Transactions Per Second | Throughput metric |
| QPS | Queries Per Second | Throughput metric |
| RLS | Row-Level Security | Security feature |
| FSM | Free Space Map | Storage structure |
| VM | Visibility Map | Storage structure |

---

## Translation Conventions (翻译约定)

### Verbs

| Chinese | English | Example |
|---------|---------|---------|
| 保证 | guarantee / ensure | ensure durability |
| 维护 | maintain | maintain consistency |
| 冲突 | conflict | write-write conflict |
| 回滚 | rollback | transaction rollback |
| 提交 | commit | commit transaction |
| 中止 | abort | transaction abort |

### Adjectives

| Chinese | English | Example |
|---------|---------|---------|
| 一致的 | consistent | consistent state |
| 持久的 | durable | durable storage |
| 原子的 | atomic | atomic operation |
| 并发的 | concurrent | concurrent access |
| 串行的 | serial | serial execution |

---

## Contributing

To add or modify terminology:

1. Propose changes via GitHub PR
2. Include rationale for new terms
3. Update all affected translations

See [CONTRIBUTING-TRANSLATION.md](CONTRIBUTING-TRANSLATION.md) for details.

---

**Maintained by**: PostgreSQL_Formal Translation Team
**License**: Same as project
