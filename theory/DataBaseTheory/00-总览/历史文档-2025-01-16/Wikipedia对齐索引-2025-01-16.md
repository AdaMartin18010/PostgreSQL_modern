# Wikipedia对齐索引

> **创建日期**: 2025-01-16
> **状态**: 📋 进行中
> **目标**: 为每个核心主题文档至少引用3-5个相关Wikipedia条目

---

## 📋 目录

- [Wikipedia对齐索引](#wikipedia对齐索引)
  - [📋 目录](#-目录)
  - [1. 核心理论主题](#1-核心理论主题)
    - [1.1 形式化方法](#11-形式化方法)
    - [1.2 范畴论](#12-范畴论)
  - [2. 事务与并发控制](#2-事务与并发控制)
    - [2.1 ACID与事务](#21-acid与事务)
    - [2.2 MVCC](#22-mvcc)
    - [2.3 锁机制](#23-锁机制)
  - [3. 分布式系统理论](#3-分布式系统理论)
    - [3.1 CAP定理](#31-cap定理)
    - [3.2 分布式事务](#32-分布式事务)
  - [4. 查询优化与索引](#4-查询优化与索引)
    - [4.1 查询优化](#41-查询优化)
    - [4.2 索引结构](#42-索引结构)
  - [5. 存储与恢复](#5-存储与恢复)
    - [5.1 日志与恢复](#51-日志与恢复)
  - [6. 安全与合规](#6-安全与合规)
    - [6.1 访问控制](#61-访问控制)
  - [7. 数据模型](#7-数据模型)
    - [7.1 关系模型](#71-关系模型)
  - [8. 向量与AI](#8-向量与ai)
    - [8.1 向量检索](#81-向量检索)
  - [📝 使用说明](#-使用说明)
    - [如何添加Wikipedia引用](#如何添加wikipedia引用)
    - [对齐检查清单](#对齐检查清单)

---

## 1. 核心理论主题

### 1.1 形式化方法

**相关Wikipedia条目**:

1. **Formal methods** (<https://en.wikipedia.org/wiki/Formal_methods>)
   - 形式化方法总论
   - 相关文档: `01-形式化方法与基础理论/01.01-形式化验证方法.md`

2. **TLA+** (<https://en.wikipedia.org/wiki/TLA%2B>)
   - TLA+规范语言
   - 相关文档: `06-存储与恢复/06.01-TLA+-事务与WAL-规范纲要.md`

3. **Coq (proof assistant)** (<https://en.wikipedia.org/wiki/Coq>)
   - Coq证明助手
   - 相关文档: `01-形式化方法与基础理论/01.01-形式化验证方法.md`

4. **Isabelle (proof assistant)** (<https://en.wikipedia.org/wiki/Isabelle_(proof_assistant)>)
   - Isabelle证明助手
   - 相关文档: `01-形式化方法与基础理论/01.01-形式化验证方法.md`

5. **Alloy (specification language)** (<https://en.wikipedia.org/wiki/Alloy_(specification_language)>)
   - Alloy规范语言
   - 相关文档: `01-形式化方法与基础理论/01.01-形式化验证方法.md`

### 1.2 范畴论

**相关Wikipedia条目**:

1. **Category theory** (<https://en.wikipedia.org/wiki/Category_theory>)
   - 范畴论基础
   - 相关文档: `01-形式化方法与基础理论/01.03-范畴论基础.md`

2. **Functor** (<https://en.wikipedia.org/wiki/Functor>)
   - 函子
   - 相关文档: `02-范畴论应用/02.04-模式映射与范畴视角-函子与自然变换.md`

3. **Natural transformation** (<https://en.wikipedia.org/wiki/Natural_transformation>)
   - 自然变换
   - 相关文档: `02-范畴论应用/02.04-模式映射与范畴视角-函子与自然变换.md`

---

## 2. 事务与并发控制

### 2.1 ACID与事务

**相关Wikipedia条目**:

1. **ACID** (<https://en.wikipedia.org/wiki/ACID>)
   - ACID特性
   - 相关文档: `03-事务与并发控制/03.01-MVCC高级分析与形式证明.md`

2. **Database transaction** (<https://en.wikipedia.org/wiki/Database_transaction>)
   - 数据库事务
   - 相关文档: `03-事务与并发控制/03.03-事务隔离与MVCC-统一形式模型与完备性证明.md`

3. **Transaction isolation** (<https://en.wikipedia.org/wiki/Isolation_(database_systems)>)
   - 事务隔离
   - 相关文档: `03-事务与并发控制/03.03-事务隔离与MVCC-统一形式模型与完备性证明.md`

### 2.2 MVCC

**相关Wikipedia条目**:

1. **Multiversion concurrency control** (<https://en.wikipedia.org/wiki/Multiversion_concurrency_control>)
   - 多版本并发控制
   - 相关文档: `03-事务与并发控制/03.01-MVCC高级分析与形式证明.md`

2. **Snapshot isolation** (<https://en.wikipedia.org/wiki/Snapshot_isolation>)
   - 快照隔离
   - 相关文档: `03-事务与并发控制/03.06-快照隔离异常谱系-形式分类与必要条件.md`

3. **Serializability** (<https://en.wikipedia.org/wiki/Serializability>)
   - 可串行化
   - 相关文档: `03-事务与并发控制/03.09-两阶段加锁-可串行化的严格证明.md`

### 2.3 锁机制

**相关Wikipedia条目**:

1. **Lock (computer science)** (<https://en.wikipedia.org/wiki/Lock_(computer_science)>)
   - 锁机制
   - 相关文档: `03-事务与并发控制/03.09-两阶段加锁-可串行化的严格证明.md`

2. **Two-phase locking** (<https://en.wikipedia.org/wiki/Two-phase_locking>)
   - 两阶段加锁
   - 相关文档: `03-事务与并发控制/03.09-两阶段加锁-可串行化的严格证明.md`

3. **Deadlock** (<https://en.wikipedia.org/wiki/Deadlock>)
   - 死锁
   - 相关文档: `03-事务与并发控制/03.08-死锁与等待图-检测正确性与避免策略.md`

---

## 3. 分布式系统理论

### 3.1 CAP定理

**相关Wikipedia条目**:

1. **CAP theorem** (<https://en.wikipedia.org/wiki/CAP_theorem>)
   - CAP定理
   - 相关文档: `04-分布式系统理论/04.02-分布式一致性与CAP-形式化刻画与权衡.md`

2. **Consistency model** (<https://en.wikipedia.org/wiki/Consistency_model>)
   - 一致性模型
   - 相关文档: `04-分布式系统理论/04.02-分布式一致性与CAP-形式化刻画与权衡.md`

3. **Eventual consistency** (<https://en.wikipedia.org/wiki/Eventual_consistency>)
   - 最终一致性
   - 相关文档: `04-分布式系统理论/04.05-CRDT与最终一致-会合半格与收敛性证明.md`

### 3.2 分布式事务

**相关Wikipedia条目**:

1. **Two-phase commit protocol** (<https://en.wikipedia.org/wiki/Two-phase_commit_protocol>)
   - 两阶段提交
   - 相关文档: `04-分布式系统理论/04.03-两阶段提交-可恢复性与阻塞特性证明.md`

2. **Three-phase commit protocol** (<https://en.wikipedia.org/wiki/Three-phase_commit_protocol>)
   - 三阶段提交
   - 相关文档: `04-分布式系统理论/04.03-两阶段提交-可恢复性与阻塞特性证明.md`

3. **Saga pattern** (<https://en.wikipedia.org/wiki/Saga_pattern>)
   - SAGA模式
   - 相关文档: `04-分布式系统理论/04.04-SAGA与补偿事务-可达性与幂等性条件.md`

---

## 4. 查询优化与索引

### 4.1 查询优化

**相关Wikipedia条目**:

1. **Query optimization** (<https://en.wikipedia.org/wiki/Query_optimization>)
   - 查询优化
   - 相关文档: `05-索引与查询优化/05.01-代价模型与优化器-等价重写与最优性.md`

2. **Query plan** (<https://en.wikipedia.org/wiki/Query_plan>)
   - 查询计划
   - 相关文档: `05-索引与查询优化/05.01-代价模型与优化器-等价重写与最优性.md`

### 4.2 索引结构

**相关Wikipedia条目**:

1. **B-tree** (<https://en.wikipedia.org/wiki/B-tree>)
   - B树
   - 相关文档: `05-索引与查询优化/05.02-索引结构正确性-BTree_GiST_GiN不变式与证明.md`

2. **B+ tree** (<https://en.wikipedia.org/wiki/B%2B_tree>)
   - B+树
   - 相关文档: `05-索引与查询优化/05.02-索引结构正确性-BTree_GiST_GiN不变式与证明.md`

3. **Hash table** (<https://en.wikipedia.org/wiki/Hash_table>)
   - 哈希表
   - 相关文档: `05-索引与查询优化/05.02-索引结构正确性-BTree_GiST_GiN不变式与证明.md`

---

## 5. 存储与恢复

### 5.1 日志与恢复

**相关Wikipedia条目**:

1. **Write-ahead logging** (<https://en.wikipedia.org/wiki/Write-ahead_logging>)
   - 预写日志
   - 相关文档: `06-存储与恢复/06.01-TLA+-事务与WAL-规范纲要.md`

2. **ARIES (computer science)** (<https://en.wikipedia.org/wiki/ARIES_(computer_science)>)
   - ARIES恢复算法
   - 相关文档: `06-存储与恢复/06.03-ARIES日志恢复-正确性与不变式.md`

3. **Checkpoint (database)** (<https://en.wikipedia.org/wiki/Checkpoint_(database)>)
   - 检查点
   - 相关文档: `06-存储与恢复/06.01-TLA+-事务与WAL-规范纲要.md`

---

## 6. 安全与合规

### 6.1 访问控制

**相关Wikipedia条目**:

1. **Access control** (<https://en.wikipedia.org/wiki/Access_control>)
   - 访问控制
   - 相关文档: `07-安全与合规/07.04-数据库安全模型-访问控制与信息流安全的形式化.md`

2. **Role-based access control** (<https://en.wikipedia.org/wiki/Role-based_access_control>)
   - 基于角色的访问控制
   - 相关文档: `07-安全与合规/07.04-数据库安全模型-访问控制与信息流安全的形式化.md`

3. **Differential privacy** (<https://en.wikipedia.org/wiki/Differential_privacy>)
   - 差分隐私
   - 相关文档: `07-安全与合规/07.02-差分隐私-SQL聚合的灵敏度与噪声机制.md`

---

## 7. 数据模型

### 7.1 关系模型

**相关Wikipedia条目**:

1. **Relational model** (<https://en.wikipedia.org/wiki/Relational_model>)
   - 关系模型
   - 相关文档: `09-数据模型与规范化/09.01-关系约束与规范化-函数依赖与范式证明.md`

2. **Database normalization** (<https://en.wikipedia.org/wiki/Database_normalization>)
   - 数据库规范化
   - 相关文档: `09-数据模型与规范化/09.01-关系约束与规范化-函数依赖与范式证明.md`

3. **Third normal form** (<https://en.wikipedia.org/wiki/Third_normal_form>)
   - 第三范式
   - 相关文档: `09-数据模型与规范化/09.02-BCNF与3NF-完整证明稿.md`

4. **Boyce–Codd normal form** (<https://en.wikipedia.org/wiki/Boyce%E2%80%93Codd_normal_form>)
   - BCNF
   - 相关文档: `09-数据模型与规范化/09.02-BCNF与3NF-完整证明稿.md`

---

## 8. 向量与AI

### 8.1 向量检索

**相关Wikipedia条目**:

1. **Nearest neighbor search** (<https://en.wikipedia.org/wiki/Nearest_neighbor_search>)
   - 最近邻搜索
   - 相关文档: `11-向量与AI/11.01-向量检索与Top-k-数学模型与可近似性证明.md`

2. **Locality-sensitive hashing** (<https://en.wikipedia.org/wiki/Locality-sensitive_hashing>)
   - 局部敏感哈希
   - 相关文档: `11-向量与AI/11.01-向量检索与Top-k-数学模型与可近似性证明.md`

---

## 📝 使用说明

### 如何添加Wikipedia引用

在每个相关文档的参考文献部分，添加Wikipedia条目：

```markdown
### 7. 参考文献

#### 7.1 Wikipedia条目

- **ACID** (https://en.wikipedia.org/wiki/ACID)
  - Wikipedia条目: ACID
  - **重要性**: 数据库事务的基础概念
  - **核心内容**: 原子性、一致性、隔离性、持久性
  - **与本文档的关系**: 本文档形式化证明了ACID特性在MVCC中的实现
```

### 对齐检查清单

- [ ] 每个核心理论文档至少引用3-5个Wikipedia条目
- [ ] Wikipedia条目链接有效
- [ ] 说明Wikipedia条目与文档的关系
- [ ] 标注Wikipedia内容的准确性

---

**最后更新**: 2025-01-16
**维护者**: Documentation Team
**状态**: 📋 进行中
