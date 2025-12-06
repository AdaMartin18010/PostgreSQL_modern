# 03 | CAP权衡决策模型

> **决策工具**: 本文档提供系统化的CAP权衡决策方法，帮助架构师在分布式环境下选择合适的一致性策略。

---

## 📑 目录

- [03 | CAP权衡决策模型](#03--cap权衡决策模型)
  - [📑 目录](#-目录)
  - [一、决策框架](#一决策框架)
    - [1.1 CAP决策树](#11-cap决策树)
    - [1.2 PACELC决策矩阵](#12-pacelc决策矩阵)
  - [二、CP系统设计决策](#二cp系统设计决策)
    - [2.1 CP决策子树](#21-cp决策子树)
    - [2.2 一致性级别选择](#22-一致性级别选择)
    - [2.3 Quorum配置](#23-quorum配置)
  - [三、AP系统设计决策](#三ap系统设计决策)
    - [3.1 AP决策子树](#31-ap决策子树)
    - [3.2 冲突解决策略](#32-冲突解决策略)
    - [3.3 最终一致性保证](#33-最终一致性保证)
  - [四、混合策略](#四混合策略)
    - [4.1 数据分层策略](#41-数据分层策略)
    - [4.2 动态切换策略](#42-动态切换策略)
    - [4.3 读写分离](#43-读写分离)
  - [五、实践案例](#五实践案例)
    - [案例1: 电商订单系统](#案例1-电商订单系统)
    - [案例2: 全球社交网络](#案例2-全球社交网络)
  - [六、监控与度量](#六监控与度量)
    - [6.1 一致性监控](#61-一致性监控)
    - [6.2 可用性监控](#62-可用性监控)
  - [七、权衡量化模型](#七权衡量化模型)
    - [7.1 延迟-一致性曲线](#71-延迟-一致性曲线)
    - [7.2 可用性-一致性曲线](#72-可用性-一致性曲线)
    - [7.3 成本-性能曲线](#73-成本-性能曲线)
  - [八、决策检查清单](#八决策检查清单)
    - [8.1 需求分析清单](#81-需求分析清单)
    - [8.2 方案评估清单](#82-方案评估清单)
  - [九、总结](#九总结)
    - [9.1 核心贡献](#91-核心贡献)
    - [9.2 关键公式](#92-关键公式)
    - [9.3 设计原则](#93-设计原则)
  - [十、延伸阅读](#十延伸阅读)
  - [十一、完整实现代码](#十一完整实现代码)
    - [11.1 CAP决策器完整实现](#111-cap决策器完整实现)
    - [11.2 动态CAP切换实现](#112-动态cap切换实现)
  - [十二、实际应用案例](#十二实际应用案例)
    - [12.1 案例: 混合系统（Spanner风格）](#121-案例-混合系统spanner风格)
    - [12.2 案例: 分层CAP策略](#122-案例-分层cap策略)
  - [十三、反例与错误设计](#十三反例与错误设计)
    - [反例1: 误用AP系统处理金融数据](#反例1-误用ap系统处理金融数据)
    - [反例2: 过度追求一致性导致性能下降](#反例2-过度追求一致性导致性能下降)

---

## 一、决策框架

### 1.1 CAP决策树

```mermaid
graph TD
    A[分布式系统设计] --> B{需要跨地域部署?}
    B -->|否| C[CA系统: 单机PostgreSQL]
    B -->|是| D{能否容忍数据丢失?}

    D -->|否| E{能否容忍阻塞?}
    D -->|是| F[AP系统]

    E -->|是| G[CP系统: 同步复制]
    E -->|否| H[混合策略]

    G --> I{节点数量?}
    I -->|3-7| J[Raft]
    I -->|>7| K[Multi-Paxos]

    F --> L{冲突处理?}
    L -->|无冲突| M[CRDT]
    L -->|LWW| N[Cassandra]
    L -->|应用层| O[Vector Clock]

    H --> P{按数据分层?}
    P -->|是| Q[核心CP + 辅助AP]
    P -->|否| R[可调一致性]
```

### 1.2 PACELC决策矩阵

**完整模型**: 考虑分区和正常情况

| 系统 | 分区时 (PA/PC) | 正常时 (EL/EC) | 典型应用 |
|------|---------------|---------------|---------|
| **DynamoDB** | PA | EL | 购物车、会话 |
| **Cassandra** | PA | EC* | 日志、监控 |
| **MongoDB** | PC | EL | 内容管理 |
| **HBase** | PC | EC | 大数据分析 |
| **etcd** | PC | EC | 配置中心 |
| **PostgreSQL (async)** | PA | EL | Web应用 |
| **PostgreSQL (sync)** | PC | EC | 金融系统 |
| **Spanner** | PC | EC | 全球数据库 |

*可配置

---

## 二、CP系统设计决策

### 2.1 CP决策子树

```mermaid
graph TD
    A[选择CP系统] --> B{写入模式?}
    B -->|单主| C[主从复制]
    B -->|多主| D[共识协议]

    C --> E{同步级别?}
    E -->|单副本| F[PostgreSQL sync_commit=remote_write]
    E -->|多副本| G[Quorum: W≥2]

    D --> H{复杂度接受度?}
    H -->|易理解| I[Raft]
    H -->|理论优雅| J[Paxos]

    I --> K{故障恢复?}
    K -->|快速| L[PreVote优化]
    K -->|标准| M[原始Raft]
```

### 2.2 一致性级别选择

**矩阵**:

| 一致性级别 | 延迟 | 容错性 | 实现复杂度 | 适用场景 |
|-----------|------|--------|-----------|---------|
| **Linearizable** | 高 | ⌊n/2⌋ | 高 | 金融交易、配置 |
| **Sequential** | 中高 | ⌊n/2⌋ | 中高 | 协调服务 |
| **Causal** | 中 | 部分节点 | 中 | 社交网络 |
| **Eventual** | 低 | 几乎所有 | 低 | 日志、监控 |

**选择公式**:

$$ConsistencyLevel = f(\text{DataCriticality}, \text{LatencyBudget}, \text{FailureTolerance})$$

### 2.3 Quorum配置

**定义**:

$$R + W > N \implies \text{Strong Consistency}$$

其中:

- $R$: 读取副本数
- $W$: 写入副本数
- $N$: 总副本数

**常见配置**:

| 配置 | R | W | N | 一致性 | 读性能 | 写性能 |
|-----|---|---|---|--------|--------|--------|
| **强一致读写** | 2 | 2 | 3 | 强 | 中 | 中 |
| **读优化** | 1 | 3 | 3 | 强 | 高 | 低 |
| **写优化** | 3 | 1 | 3 | 强 | 低 | 高 |
| **最终一致** | 1 | 1 | 3 | 弱 | 高 | 高 |

**选择策略**:

```python
def choose_quorum(read_ratio, write_ratio):
    if read_ratio > 0.8:
        return (R=1, W=N)  # 读优化
    elif write_ratio > 0.8:
        return (R=N, W=1)  # 写优化
    else:
        return (R=⌈N/2⌉+1, W=⌈N/2⌉+1)  # 平衡
```

---

## 三、AP系统设计决策

### 3.1 AP决策子树

```mermaid
graph TD
    A[选择AP系统] --> B{数据类型?}
    B -->|计数器| C[CRDT: G-Counter/PN-Counter]
    B -->|集合| D[CRDT: OR-Set/2P-Set]
    B -->|键值| E[LWW + 向量时钟]

    C --> F{精度要求?}
    F -->|精确| G[定期同步到CP系统]
    F -->|近似| H[纯CRDT]

    E --> I{冲突频率?}
    I -->|低| J[LWW足够]
    I -->|高| K[应用层合并]
```

### 3.2 冲突解决策略

**策略矩阵**:

| 策略 | 实现复杂度 | 数据丢失 | 适用场景 |
|-----|-----------|---------|---------|
| **LWW** | 低 | 可能丢失 | 配置、状态 |
| **CRDT** | 中 | 无丢失 | 计数器、集合 |
| **Vector Clock** | 高 | 无丢失（需合并） | 通用场景 |
| **应用层合并** | 很高 | 自定义 | 复杂业务 |

**选择流程**:

```python
def choose_conflict_resolution(data_type, conflict_rate):
    if data_type in ['counter', 'set']:
        return 'CRDT'  # 无冲突合并

    if conflict_rate < 0.01:  # <1%
        return 'LWW'  # 简单高效

    if can_merge_at_application():
        return 'Vector Clock + App Merge'
    else:
        return 'LWW with logging'  # 记录冲突便于审计
```

### 3.3 最终一致性保证

**定义**:

$$\forall w: \text{eventually } \forall n: read_n(x) = w(x)$$

**收敛时间估算**:

$$T_{convergence} \approx \text{max}(\text{GossipRounds}, \text{NetworkDelay})$$

**Gossip协议**:

```python
class GossipProtocol:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.data = {}

    def gossip_round(self):
        # 随机选择peer
        peer = random.choice(self.peers)

        # 交换数据
        my_data = self.data
        peer_data = peer.get_data()

        # 合并（使用版本号）
        for key, value in peer_data.items():
            if key not in my_data or value.version > my_data[key].version:
                my_data[key] = value

        # 发送我的数据给peer
        peer.merge_data(my_data)
```

**收敛速度**: $O(\log n)$ 轮Gossip

---

## 四、混合策略

### 4.1 数据分层策略

**原则**: 按数据重要性分层

```text
┌─────────────────────────────────┐
│        数据分层架构              │
├─────────────────────────────────┤
│                                 │
│  核心数据层 (订单、支付)          │
│  ├─ CP系统: PostgreSQL同步复制   │
│  ├─ Raft共识                    │
│  └─ 强一致性保证                 │
│         ↓                       │
│  辅助数据层 (日志、统计)          │
│  ├─ AP系统: Cassandra           │
│  ├─ 异步复制                    │
│  └─ 最终一致性                   │
│         ↓                       │
│  缓存层 (热点数据)               │
│  ├─ Redis Cluster               │
│  ├─ 最终一致性                   │
│  └─ 允许短暂不一致               │
│                                 │
└─────────────────────────────────┘
```

**决策矩阵**:

| 数据类型 | 一致性 | 系统选择 | 理由 |
|---------|-------|---------|------|
| **订单** | 强 | PostgreSQL CP | 金钱相关 |
| **支付** | 强 | Raft + 2PC | 跨服务事务 |
| **库存** | 强 | CP + 乐观锁 | 超卖风险 |
| **浏览记录** | 弱 | Cassandra AP | 可丢失 |
| **点赞数** | 弱 | Redis AP | 允许延迟 |
| **用户配置** | 中 | etcd CP | 需要一致 |

### 4.2 动态切换策略

**场景**: 根据负载动态调整

```python
class AdaptiveConsistency:
    def __init__(self):
        self.cp_system = PostgreSQL()
        self.ap_system = Cassandra()
        self.load_monitor = LoadMonitor()

    def write(self, key, value, priority):
        load = self.load_monitor.get_current_load()

        if priority == 'CRITICAL':
            # 核心数据，强一致
            return self.cp_system.write(key, value)

        elif load > 0.8:  # 高负载
            # 降级到AP，保证可用性
            logger.warning("High load, using AP system")
            return self.ap_system.write(key, value)

        else:
            # 正常负载，使用CP
            try:
                return self.cp_system.write(key, value, timeout=100ms)
            except TimeoutError:
                # 超时降级到AP
                return self.ap_system.write(key, value)
```

### 4.3 读写分离

**策略**: 写CP，读AP

```text
┌─────────────────────────────────┐
│         读写分离架构             │
├─────────────────────────────────┤
│                                 │
│  写入路径:                       │
│  Client → CP系统 (PostgreSQL)   │
│            ↓ WAL                │
│         持久化                   │
│            ↓ 逻辑复制            │
│  读取缓存:                       │
│  AP系统 (Redis/Cassandra)       │
│            ↓                    │
│  Client ← 高性能读取             │
│                                 │
└─────────────────────────────────┘
```

**延迟分析**:

- 写延迟: CP系统延迟（~10ms）
- 读延迟: AP系统延迟（~1ms）
- 同步延迟: 秒级（异步复制）

---

## 五、实践案例

### 案例1: 电商订单系统

**需求分析**:

| 数据 | 一致性要求 | 可用性要求 | 决策 |
|-----|-----------|-----------|------|
| 订单创建 | 强 | 中 | CP (PostgreSQL) |
| 库存扣减 | 强 | 高 | CP + 预分配 |
| 订单查询 | 中 | 高 | AP (缓存) |
| 物流状态 | 弱 | 极高 | AP (Cassandra) |

**架构**:

```text
订单服务 (CP)
├─ PostgreSQL主从 (同步复制)
├─ 写入: Serializable隔离级别
└─ 读取: 主库（强一致）

库存服务 (CP + 优化)
├─ PostgreSQL + 乐观锁
├─ 预分配策略（降低竞争）
└─ 最终同步

查询服务 (AP)
├─ Redis缓存
├─ 异步更新（1-5秒延迟）
└─ 缓存穿透保护

物流服务 (AP)
├─ Cassandra
├─ 最终一致性
└─ 高可用优先
```

**CAP权衡**:

- 核心流程（订单、支付）: **PC/EC**
- 辅助流程（查询、物流）: **PA/EL**

### 案例2: 全球社交网络

**需求分析**:

| 功能 | 一致性 | 延迟要求 | 决策 |
|-----|-------|---------|------|
| 发帖 | 弱 | <100ms | AP (就近写入) |
| 点赞 | 弱 | <50ms | AP (CRDT计数) |
| 好友关系 | 中 | <200ms | CP (关系重要) |
| 消息发送 | 强 | <500ms | CP (不能丢失) |

**架构**:

```text
全球5个数据中心
├─ 发帖/点赞: Cassandra (PA/EL)
│   ├─ 就近写入
│   ├─ Gossip同步
│   └─ CRDT合并
│
├─ 好友关系: CockroachDB (PC/EC)
│   ├─ Raft复制
│   ├─ 跨区域延迟
│   └─ 强一致性
│
└─ 消息: PostgreSQL + Raft (PC/EC)
    ├─ 分区存储
    ├─ 跨区域2PC
    └─ 消息不丢失
```

**CAP权衡**:

- 轻量级操作（点赞、浏览）: **PA/EL**
- 关键操作（消息、关系）: **PC/EC**

---

## 六、监控与度量

### 6.1 一致性监控

**关键指标**:

| 指标 | 定义 | 阈值 | 告警 |
|-----|------|------|------|
| **复制延迟** | 主从数据差异时间 | <5s | >10s |
| **冲突率** | 写冲突占比 | <1% | >5% |
| **收敛时间** | 达到一致的时间 | <10s | >30s |
| **不一致窗口** | 读到旧数据的时长 | <2s | >10s |

**监控代码**:

```python
class ConsistencyMonitor:
    def measure_replication_lag(self):
        """测量复制延迟"""
        primary_lsn = self.primary.get_current_lsn()

        lags = []
        for standby in self.standbys:
            standby_lsn = standby.get_replay_lsn()
            lag = primary_lsn - standby_lsn
            lags.append(lag)

        return max(lags)  # 最大延迟

    def measure_consistency_window(self):
        """测量不一致窗口"""
        # 写入测试值
        test_key = f"consistency_test_{timestamp()}"
        self.primary.write(test_key, timestamp())

        # 检查所有副本
        start = time.time()
        while True:
            all_consistent = all(
                replica.read(test_key) == value
                for replica in self.replicas
            )

            if all_consistent:
                return time.time() - start

            if time.time() - start > 60:
                return float('inf')  # 超时
```

### 6.2 可用性监控

**关键指标**:

| 指标 | 计算公式 | SLA |
|-----|---------|-----|
| **服务可用性** | $\frac{\text{Uptime}}{\text{Total}}$ | >99.9% |
| **写入成功率** | $\frac{\text{Success}}{\text{Total}}$ | >99.99% |
| **读取成功率** | $\frac{\text{Success}}{\text{Total}}$ | >99.999% |
| **故障恢复时间** | MTTR | <5min |

---

## 七、权衡量化模型

### 7.1 延迟-一致性曲线

**模型**:

$$Latency = Base + Consistency \times Factor$$

| 一致性级别 | Factor | 延迟示例 (Base=5ms) |
|-----------|--------|-------------------|
| Eventual | 0× | 5ms |
| Causal | 1× | 10ms |
| Sequential | 2× | 15ms |
| Linearizable | 3× | 20ms |

**图示**:

```text
延迟 (ms)
  ↑
20│                    ● Linearizable
15│            ● Sequential
10│     ● Causal
 5│ ● Eventual
  └─────────────────────────→ 一致性强度
```

### 7.2 可用性-一致性曲线

**模型**:

$$Availability = Base \times (1 - Consistency \times FailureImpact)$$

| 配置 | 节点故障影响 | 可用性 |
|-----|-------------|--------|
| AP (异步) | 低 (单节点继续) | 99.99% |
| CP (Quorum) | 中 (需多数派) | 99.9% |
| CP (同步全部) | 高 (需所有节点) | 99% |

### 7.3 成本-性能曲线

**模型**:

$$Cost = Storage \times Replicas + Network \times Bandwidth$$

| 配置 | 副本数 | 存储成本 | 网络成本 | 总成本 |
|-----|-------|---------|---------|--------|
| 单机 | 1 | $100 | $0 | $100 |
| 异步3副本 | 3 | $300 | $50 | $350 |
| Raft 5节点 | 5 | $500 | $200 | $700 |

---

## 八、决策检查清单

### 8.1 需求分析清单

- [ ] **数据重要性**
  - [ ] 核心数据（金钱、订单）
  - [ ] 辅助数据（日志、统计）
  - [ ] 临时数据（会话、缓存）

- [ ] **一致性需求**
  - [ ] 强一致性（金融、库存）
  - [ ] 因果一致性（社交关系）
  - [ ] 最终一致性（点赞、浏览）

- [ ] **可用性需求**
  - [ ] 99.999% (五个9)
  - [ ] 99.99% (四个9)
  - [ ] 99.9% (三个9)

- [ ] **延迟预算**
  - [ ] <10ms (实时)
  - [ ] <100ms (交互)
  - [ ] <1s (批处理)

- [ ] **地域分布**
  - [ ] 单数据中心
  - [ ] 同城多机房
  - [ ] 跨地域多区域

### 8.2 方案评估清单

- [ ] **技术可行性**
  - [ ] 团队技术栈匹配
  - [ ] 运维复杂度可接受
  - [ ] 故障恢复可演练

- [ ] **成本可接受性**
  - [ ] 硬件成本
  - [ ] 网络带宽成本
  - [ ] 人力成本

- [ ] **性能验证**
  - [ ] 压力测试达标
  - [ ] 故障演练通过
  - [ ] 监控指标正常

---

## 九、总结

### 9.1 核心贡献

**决策工具**:

1. **CAP决策树**（第1.1节）
2. **PACELC矩阵**（第1.2节）
3. **Quorum配置指南**（第2.3节）
4. **冲突解决策略**（第3.2节）

**量化模型**:

1. **延迟-一致性曲线**（第7.1节）
2. **可用性计算公式**（第7.2节）
3. **成本预估模型**（第7.3节）

### 9.2 关键公式

**Quorum条件**:

$$R + W > N \implies \text{Strong Consistency}$$

**可用性计算**:

$$A_{Raft} = P(\text{majority alive})$$

**收敛时间**:

$$T_{convergence} = O(\log n) \times RTT$$

### 9.3 设计原则

1. **需求驱动**: 从业务需求倒推技术选型
2. **分层设计**: 核心CP，辅助AP
3. **监控先行**: 建立度量体系
4. **渐进式**: 从CA开始，按需扩展

---

## 十、延伸阅读

**理论基础**:

- Brewer, E. (2012). "CAP Twelve Years Later: How the 'Rules' Have Changed"
- Abadi, D. (2012). "Consistency Tradeoffs in Modern Distributed Systems: PACELC"
- Vogels, W. (2009). "Eventually Consistent"

**工程实践**:

- Kleppmann, M. (2017). *Designing Data-Intensive Applications* Chapter 5-9
- *Database Internals* (Alex Petrov) Chapter 12-14

**案例分析**:

- DynamoDB论文 (Amazon, 2007)
- Cassandra论文 (Facebook, 2010)
- Spanner论文 (Google, 2012)

**扩展方向**:

- `01-核心理论模型/04-CAP理论与权衡.md` → CAP理论基础
- `04-分布式扩展/05-CAP实践案例.md` → 真实系统分析
- `06-性能分析/02-延迟分析模型.md` → 量化性能

---

## 十一、完整实现代码

### 11.1 CAP决策器完整实现

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class CAPChoice(Enum):
    CP = "CP"  # 一致性 + 分区容错
    AP = "AP"  # 可用性 + 分区容错
    CA = "CA"  # 一致性 + 可用性（单机）
    HYBRID = "HYBRID"  # 混合策略

@dataclass
class CAPRequirements:
    """CAP需求"""
    consistency_required: str  # 'strict' | 'eventual' | 'none'
    availability_target: float  # 0.99, 0.999, 0.9999
    partition_tolerance: bool  # 是否容忍分区
    data_type: str  # 'financial' | 'social' | 'config' | 'log'
    latency_budget_ms: int  # 延迟预算

class CAPDecisionEngine:
    """CAP决策引擎"""

    def decide(self, requirements: CAPRequirements) -> CAPChoice:
        """根据需求决策CAP选择"""

        # 规则1: 金融数据必须CP
        if requirements.data_type == 'financial':
            return CAPChoice.CP

        # 规则2: 社交数据可用AP
        if requirements.data_type == 'social':
            return CAPChoice.AP

        # 规则3: 单机环境可用CA
        if not requirements.partition_tolerance:
            return CAPChoice.CA

        # 规则4: 强一致性要求 → CP
        if requirements.consistency_required == 'strict':
            return CAPChoice.CP

        # 规则5: 高可用性要求 → AP
        if requirements.availability_target >= 0.9999:
            return CAPChoice.AP

        # 默认: 混合策略
        return CAPChoice.HYBRID

    def recommend_system(self, choice: CAPChoice) -> dict:
        """推荐具体系统"""
        recommendations = {
            CAPChoice.CP: {
                'system': 'PostgreSQL (同步复制)',
                'config': 'synchronous_commit = on',
                'consistency': '强一致',
                'availability': '99.9%'
            },
            CAPChoice.AP: {
                'system': 'Cassandra',
                'config': 'CONSISTENCY LEVEL ONE',
                'consistency': '最终一致',
                'availability': '99.99%'
            },
            CAPChoice.CA: {
                'system': 'PostgreSQL (单机)',
                'config': '单机部署',
                'consistency': '强一致',
                'availability': '99%'
            },
            CAPChoice.HYBRID: {
                'system': 'CockroachDB / Spanner',
                'config': '分布式SQL',
                'consistency': '可配置',
                'availability': '99.99%'
            }
        }
        return recommendations[choice]

# 使用示例
engine = CAPDecisionEngine()

# 金融场景
req1 = CAPRequirements(
    consistency_required='strict',
    availability_target=0.999,
    partition_tolerance=True,
    data_type='financial',
    latency_budget_ms=100
)
choice1 = engine.decide(req1)  # CP
system1 = engine.recommend_system(choice1)  # PostgreSQL同步复制

# 社交场景
req2 = CAPRequirements(
    consistency_required='eventual',
    availability_target=0.9999,
    partition_tolerance=True,
    data_type='social',
    latency_budget_ms=50
)
choice2 = engine.decide(req2)  # AP
system2 = engine.recommend_system(choice2)  # Cassandra
```

### 11.2 动态CAP切换实现

```python
from typing import Dict, Optional
import time

class DynamicCAPSwitcher:
    """动态CAP切换器（PACELC）"""

    def __init__(self, db_conn):
        self.db = db_conn
        self.current_mode = 'normal'  # 'normal' | 'partition'
        self.metrics = {
            'latency': deque(maxlen=100),
            'error_rate': deque(maxlen=100)
        }

    def detect_partition(self) -> bool:
        """检测网络分区"""
        # 检查是否能连接到所有节点
        try:
            self.db.execute("SELECT 1 FROM standby1")
            self.db.execute("SELECT 1 FROM standby2")
            return False
        except:
            return True  # 分区发生

    def switch_mode(self, mode: str):
        """切换模式"""
        if mode == 'partition':
            # 分区时: 选择C或A
            # 金融数据: 选择C（拒绝服务）
            # 非关键数据: 选择A（继续服务）
            self.db.execute("ALTER SYSTEM SET synchronous_commit = 'off'")
        else:
            # 正常时: 选择L或C
            # 延迟高: 选择L（低延迟）
            # 延迟低: 选择C（一致性）
            avg_latency = sum(self.metrics['latency']) / len(self.metrics['latency'])
            if avg_latency > 100:  # 100ms阈值
                self.db.execute("ALTER SYSTEM SET synchronous_commit = 'off'")  # 选择L
            else:
                self.db.execute("ALTER SYSTEM SET synchronous_commit = 'on'")  # 选择C

    def monitor_and_adjust(self):
        """监控并自动调整"""
        while True:
            # 检测分区
            if self.detect_partition():
                if self.current_mode != 'partition':
                    self.current_mode = 'partition'
                    self.switch_mode('partition')
            else:
                if self.current_mode != 'normal':
                    self.current_mode = 'normal'
                    self.switch_mode('normal')

            time.sleep(1)  # 每秒检查一次
```

---

## 十二、实际应用案例

### 12.1 案例: 混合系统（Spanner风格）

**场景**: 全球分布式数据库

**架构**: Spanner (CP/EC)

**实现**:

```text
Spanner架构:
├─ TrueTime: GPS+原子钟同步
├─ Paxos: 多数派复制
├─ 外部一致性: Commit Wait
└─ 延迟: 50-200ms

性能数据:
├─ 一致性: 强一致（线性一致）✅
├─ 可用性: 99.99% ✅
├─ 延迟: P50=50ms, P99=200ms
└─ 分区时: CP（选择一致性）
```

### 12.2 案例: 分层CAP策略

**场景**: 电商系统

**策略**: 不同数据用不同CAP选择

```python
# 分层策略
cap_strategy = {
    'inventory': CAPChoice.CP,  # 库存: CP（防止超卖）
    'user_profile': CAPChoice.AP,  # 用户信息: AP（可容忍不一致）
    'order_status': CAPChoice.CP,  # 订单状态: CP（必须准确）
    'recommendation': CAPChoice.AP,  # 推荐: AP（最终一致即可）
    'audit_log': CAPChoice.AP,  # 审计日志: AP（最终一致）
}
```

**效果**:

- 关键数据强一致
- 非关键数据高可用
- 整体性能最优

---

## 十三、反例与错误设计

### 反例1: 误用AP系统处理金融数据

**错误设计**:

```python
# 错误: 用AP系统处理金融转账
ap_db = APCassandra(nodes)

def transfer(from_account, to_account, amount):
    # AP写入: 可能丢失
    ap_db.write_async(f'account:{from_account}', balance - amount)
    ap_db.write_async(f'account:{to_account}', balance + amount)
    # 问题: 如果节点故障，可能只写入一个账户
```

**问题**: 金融数据要求强一致，AP系统无法保证

**正确设计**:

```python
# 正确: 用CP系统
cp_db = CPPostgreSQL(primary, standbys)

def transfer(from_account, to_account, amount):
    # CP写入: 强一致
    with cp_db.transaction():
        cp_db.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s",
                     (amount, from_account))
        cp_db.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s",
                     (amount, to_account))
    # 保证: 要么全部成功，要么全部失败
```

### 反例2: 过度追求一致性导致性能下降

**错误设计**:

```python
# 错误: 所有操作都用最强一致性
def read_data(key):
    # 使用ALL一致性（等待所有节点）
    return ap_db.read_all(key)  # 延迟: 100ms+
```

**问题**: 不必要的强一致性导致延迟高

**正确设计**:

```python
# 正确: 按需求选择一致性级别
def read_data(key, consistency_required):
    if consistency_required == 'strong':
        return ap_db.read_quorum(key)  # Quorum: 50ms
    else:
        return ap_db.read_one(key)  # ONE: 10ms
```

---

**版本**: 2.0.0（大幅充实）
**最后更新**: 2025-12-05
**新增内容**: 完整CAP决策器实现、动态切换、实际案例、反例分析

**关联文档**:

- `01-核心理论模型/04-CAP理论与权衡.md`
- `02-设计权衡分析/01-并发控制决策树.md`
- `04-分布式扩展/README.md`
