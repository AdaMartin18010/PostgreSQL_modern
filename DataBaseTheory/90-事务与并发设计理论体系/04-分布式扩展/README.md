# 04 | 分布式扩展

> **模块定位**: 本模块将单机并发控制理论扩展到分布式环境，重点关注LSEM L2层的实现和验证。

---

## 📚 模块概览

### 分布式扩展路径

```
单机事务 (L0)
    ↓ 扩展
分布式MVCC (Percolator)
    ↓ 协调
分布式事务 (2PC/3PC)
    ↓ 一致性
共识协议 (Raft/Paxos)
    ↓ 时间
时钟同步 (HLC/TrueTime)
```

---

## 📋 文档目录

### 待创建文档

#### [01-分布式MVCC(Percolator).md](./01-分布式MVCC(Percolator).md)

**计划内容**:

**第一部分: Percolator模型**

- 架构: 基于Bigtable的MVCC
- Primary Lock / Secondary Lock机制
- 两阶段提交流程
- 与PostgreSQL MVCC的对比

**第二部分: 冲突处理**

- 分布式写写冲突检测
- 锁服务(Chubby)的作用
- 死锁检测与超时

**第三部分: 性能分析**

- 延迟分析（网络往返）
- 吞吐量模型
- 与单机MVCC对比

**优先级**: P1
**预计字数**: ~14,000
**预计完成**: 2025-04

---

#### [02-分布式事务协议.md](./02-分布式事务协议.md)

**计划内容**:

**第一部分: 2PC (两阶段提交)**

- 协议流程（Prepare/Commit）
- 正确性证明
- 失败场景分析
- 阻塞问题

**第二部分: 3PC (三阶段提交)**

- 改进点（PreCommit阶段）
- 非阻塞性证明
- 实际应用少的原因

**第三部分: 现代变体**

- Spanner的2PC改进
- Calvin的确定性事务
- FaunaDB的Calvin变体

**优先级**: P1
**预计字数**: ~15,000
**预计完成**: 2025-05

---

#### [03-共识协议(Raft_Paxos).md](./03-共识协议(Raft_Paxos).md)

**计划内容**:

**第一部分: Raft协议**

- Leader选举算法
- 日志复制机制
- 安全性证明（5大定理）
- 活性分析

**第二部分: Paxos协议**

- Basic Paxos
- Multi-Paxos
- Fast Paxos
- 与Raft的对比

**第三部分: 工程实践**

- etcd (Raft实现)
- ZooKeeper (Zab协议)
- Consul (Raft变体)

**优先级**: P1
**预计字数**: ~18,000
**预计完成**: 2025-05

---

#### [04-时钟同步(HLC_TrueTime).md](./04-时钟同步(HLC_TrueTime).md)

**计划内容**:

**第一部分: 时钟理论**

- Lamport逻辑时钟
- 向量时钟 (Vector Clock)
- 混合逻辑时钟 (HLC)
- 物理时钟同步 (NTP)

**第二部分: TrueTime**

- 原理: GPS + 原子钟
- API设计
- 不确定性窗口
- Commit Wait机制

**第三部分: 时钟偏序**

- 定理4.1: HLC保持偏序
- 定理4.2: TrueTime保证外部一致性
- 时钟漂移分析

**优先级**: P1
**预计字数**: ~13,000
**预计完成**: 2025-06

---

#### [05-CAP实践案例.md](./05-CAP实践案例.md)

**计划内容**:

**案例1: PostgreSQL集群**

- 单机CA模式
- 同步复制CP模式
- 异步复制AP模式
- 切换策略

**案例2: Spanner**

- 突破CAP的方法
- TrueTime的代价
- 全球部署架构

**案例3: Cassandra**

- 可调一致性
- Quorum配置
- 冲突解决策略

**案例4: CockroachDB**

- 基于Raft的分布式SQL
- MVCC扩展
- 事务协调

**案例5: TiDB**

- Percolator模型实现
- PD (Placement Driver)
- 分布式执行引擎

**优先级**: P2
**预计字数**: ~16,000
**预计完成**: 2025-06

---

## 🔗 学习路径

### 路径1: 从单机到分布式

```
01-核心理论模型/02-MVCC理论
    ↓
04-分布式扩展/01-分布式MVCC(Percolator)
    ↓
04-分布式扩展/02-分布式事务协议
    ↓
04-分布式扩展/03-共识协议
```

### 路径2: CAP实践

```
01-核心理论模型/04-CAP理论
    ↓
04-分布式扩展/03-共识协议 (CP实现)
    ↓
04-分布式扩展/05-CAP实践案例
    ↓
02-设计权衡分析/03-CAP权衡决策
```

---

## 🎯 核心概念速查

| 概念 | 定义 | 所在文档 |
|-----|------|---------|
| **Percolator** | 分布式MVCC模型 | 01-分布式MVCC |
| **2PC** | 两阶段提交协议 | 02-分布式事务 |
| **Raft** | 易理解的共识协议 | 03-共识协议 |
| **HLC** | 混合逻辑时钟 | 04-时钟同步 |
| **TrueTime** | 物理时钟API | 04-时钟同步 |
| **Quorum** | 多数派机制 | 05-CAP实践案例 |

---

## 📊 文档完成度

| 文档 | 状态 | 字数 | 完成度 |
|-----|------|------|--------|
| 01-Percolator | 📋 待创建 | - | 0% |
| 02-分布式事务 | 📋 待创建 | - | 0% |
| 03-共识协议 | 📋 待创建 | - | 0% |
| 04-时钟同步 | 📋 待创建 | - | 0% |
| 05-CAP案例 | 📋 待创建 | - | 0% |

**总体完成度**: 0/5 = **0%** 📋

---

## 🌐 与其他模块的关联

```
04-分布式扩展
    ├─→ 01-核心理论模型 (L2层具体化)
    ├─→ 02-设计权衡分析 (分布式决策)
    ├─→ 03-证明与形式化 (共识协议证明)
    └─→ 06-性能分析 (分布式性能)
```

---

## 📖 参考文献

**核心论文**:

- Peng, D., & Dabek, F. (2010). "Large-scale Incremental Processing Using Distributed Transactions and Notifications" (Percolator)
- Corbett, J. C., et al. (2012). "Spanner: Google's Globally-Distributed Database"
- Ongaro, D., & Ousterhout, J. (2014). "In Search of an Understandable Consensus Algorithm" (Raft)
- Lamport, L. (1998). "The Part-Time Parliament" (Paxos)

**系统文档**:

- CockroachDB Architecture
- TiDB Design Documents
- etcd Documentation

---

## 🚀 下一步

**立即行动**:

- [ ] 学习分布式系统基础
- [ ] 阅读Raft论文
- [ ] 理解Percolator模型

**深度研究**:

- [ ] 研究Spanner架构
- [ ] 分析CockroachDB实现
- [ ] 对比不同共识协议

**实践验证**:

- [ ] 实现Mini-Raft
- [ ] 测试分布式事务
- [ ] 验证CAP权衡

---

**最后更新**: 2025-12-05
**模块负责人**: PostgreSQL理论研究组
**版本**: 1.0.0
**优先级**: P1 (分布式核心理论)
