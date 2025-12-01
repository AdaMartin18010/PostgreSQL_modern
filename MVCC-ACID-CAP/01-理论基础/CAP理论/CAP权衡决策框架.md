# CAP权衡决策框架

> **文档编号**: CAP-THEORY-003
> **主题**: CAP权衡决策框架
> **版本**: PostgreSQL 17 & 18
> **状态**: ✅ 已完成

---

## 📑 目录

- [CAP权衡决策框架](#cap权衡决策框架)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📊 第一部分：CAP权衡决策模型](#-第一部分cap权衡决策模型)
    - [1.1 决策空间定义](#11-决策空间定义)
    - [1.2 权衡矩阵](#12-权衡矩阵)
    - [1.3 决策树](#13-决策树)
  - [📊 第二部分：CP模式应用场景](#-第二部分cp模式应用场景)
    - [2.1 CP模式特征](#21-cp模式特征)
    - [2.2 CP模式适用场景](#22-cp模式适用场景)
      - [2.2.1 金融交易系统](#221-金融交易系统)
      - [2.2.2 支付系统](#222-支付系统)
      - [2.2.3 库存管理系统](#223-库存管理系统)
    - [2.3 CP模式实现策略](#23-cp模式实现策略)
      - [2.3.1 同步复制策略](#231-同步复制策略)
      - [2.3.2 两阶段提交策略](#232-两阶段提交策略)
  - [📊 第三部分：AP模式应用场景](#-第三部分ap模式应用场景)
    - [3.1 AP模式特征](#31-ap模式特征)
    - [3.2 AP模式适用场景](#32-ap模式适用场景)
      - [3.2.1 日志系统](#321-日志系统)
      - [3.2.2 分析系统](#322-分析系统)
      - [3.2.3 内容管理系统](#323-内容管理系统)
    - [3.3 AP模式实现策略](#33-ap模式实现策略)
      - [3.3.1 异步复制策略](#331-异步复制策略)
      - [3.3.2 最终一致性策略](#332-最终一致性策略)
  - [📊 第四部分：CA模式局限性分析](#-第四部分ca模式局限性分析)
    - [4.1 CA模式定义](#41-ca模式定义)
    - [4.2 CA模式局限性](#42-ca模式局限性)
    - [4.3 CA模式适用场景](#43-ca模式适用场景)
  - [📊 第五部分：PostgreSQL场景下的CAP选择](#-第五部分postgresql场景下的cap选择)
    - [5.1 PostgreSQL CAP选择决策流程](#51-postgresql-cap选择决策流程)
    - [5.2 场景化CAP选择指南](#52-场景化cap选择指南)
      - [5.2.1 金融场景](#521-金融场景)
      - [5.2.2 日志场景](#522-日志场景)
      - [5.2.3 通用场景](#523-通用场景)
    - [5.3 CAP动态调整策略](#53-cap动态调整策略)
  - [📝 总结](#-总结)
    - [核心结论](#核心结论)
    - [实践建议](#实践建议)
  - [📚 外部资源引用](#-外部资源引用)
    - [Wikipedia资源](#wikipedia资源)
    - [学术论文](#学术论文)
    - [官方文档](#官方文档)

---

## 📋 概述

CAP权衡决策框架为系统设计者提供了一套系统化的方法，用于在分布式系统中做出正确的CAP选择。

本文档从决策模型、应用场景、实现策略和PostgreSQL实践四个维度，全面阐述CAP权衡决策的完整框架。

**核心观点**：

- CAP选择需要基于**业务需求**和**系统约束**
- CP和AP模式各有**适用场景**和**实现策略**
- CA模式在分布式系统中**不可行**，但单机系统可以）
- PostgreSQL支持**动态CAP调整**以适应不同场景

---

## 📊 第一部分：CAP权衡决策模型

### 1.1 决策空间定义

**CAP决策空间**：

$$
\mathcal{D}_{\text{CAP}} = \{(\text{C}, \text{A}, \text{P}) \mid
  \text{C} \in \{0,1\}, \text{A} \in \{0,1\}, \text{P} \in \{0,1\}\}
$$

其中：

- $\text{C} = 1$：强一致性
- $\text{A} = 1$：高可用性
- $\text{P} = 1$：分区容错

**可行决策空间**：

$$
\mathcal{D}_{\text{feasible}} = \{(\text{C}, \text{A}, \text{P}) \mid
  \neg(\text{C} \land \text{A} \land \text{P})\}
$$

**实际决策空间**：

| CAP组合 | 可行性 | 模式 | 说明 |
|---------|--------|------|------|
| (1,1,1) | ❌ 不可能 | - | CAP定理禁止 |
| (1,0,1) | ✅ CP模式 | CP | 一致性+分区容错 |
| (0,1,1) | ✅ AP模式 | AP | 可用性+分区容错 |
| (1,1,0) | ✅ CA模式 | CA | 单机系统 |
| (0,0,1) | ✅ 无保证 | - | 无一致性无可用性 |
| 其他 | ❌ 无意义 | - | 无分区容错无法分布式 |

### 1.2 权衡矩阵

**CAP权衡矩阵**：

| 模式 | C | A | P | 一致性 | 可用性 | 分区容错 | 性能 | 复杂度 |
|------|---|---|---|------|--------|--------|---------|------|--------|
| **CP** | ✅ | ❌ | ✅ | 强 | 低 | 高 | 低 | 高 |
| **AP** | ❌ | ✅ | ✅ | 弱 | 高 | 高 | 高 | 中 |
| **CA** | ✅ | ✅ | ❌ | 强 | 高 | 无 | 中 | 低 |

**PostgreSQL实现对比**：

| 模式 | PostgreSQL配置 | 一致性模型 | 可用性 | 性能 |
|------|---------------|-----------|--------|------|
| **CP** | 同步复制 | 线性一致性 | 低（分区时阻塞） | 低（延迟高） |
| **AP** | 异步复制 | 最终一致性 | 高（分区时继续） | 高（延迟低） |
| **CA** | 单机模式 | 强一致性 | 高（无分区） | 中 |

### 1.3 决策树

**CAP选择决策树**：

```text
开始：CAP模式选择
    │
    ├─ 是否需要分布式？
    │   ├─ 否 → CA模式（单机系统）⭐
    │   │   ├─ 配置：默认PostgreSQL配置
    │   │   ├─ 特点：
    │   │   │   ├─ ✅ 强一致性
    │   │   │   ├─ ✅ 高可用性
    │   │   │   └─ ❌ 无分区容错（单机无分区）
    │   │   ├─ 适用场景：
    │   │   │   ├─ 小规模应用
    │   │   │   ├─ 单机部署
    │   │   │   └─ 无扩展需求
    │   │   └─ PostgreSQL配置：
    │   │       └─ 无需特殊配置，默认即可
    │   │
    │   └─ 是 → 继续判断（分布式系统）
    │       │
    │       ├─ 业务需求分析
    │       │   ├─ 是否需要强一致性？
    │       │   │   ├─ 是 → CP模式 ⭐
    │       │   │   │   ├─ 配置：同步复制
    │       │   │   │   │   └─ synchronous_standby_names = 'standby1,standby2'
    │       │   │   │   │   └─ synchronous_commit = 'remote_apply'
    │       │   │   │   ├─ 特点：
    │       │   │   │   │   ├─ ✅ 强一致性（线性一致性）
    │       │   │   │   │   ├─ ❌ 低可用性（分区时阻塞）
    │   │   │   │   │   └─ ✅ 分区容错
    │       │   │   │   ├─ 适用场景：
    │       │   │   │   │   ├─ 金融交易系统
    │       │   │   │   │   ├─ 支付系统
    │       │   │   │   │   ├─ 库存管理系统
    │       │   │   │   │   └─ 关键业务数据
    │       │   │   │   ├─ 性能影响：
    │       │   │   │   │   ├─ 延迟：高（等待备库确认）
    │       │   │   │   │   ├─ 吞吐量：低（同步等待）
    │       │   │   │   │   └─ 可用性：低（分区时阻塞）
    │       │   │   │   └─ 风险：
    │       │   │   │       ├─ 分区时写入阻塞
    │       │   │   │       └─ 性能下降
    │       │   │   │
    │       │   │   └─ 否 → 继续判断
    │       │   │       │
    │       │   │       ├─ 是否需要高可用性？
    │       │   │       │   ├─ 是 → AP模式 ⭐
    │       │   │       │   │   ├─ 配置：异步复制
    │       │   │       │   │   │   └─ synchronous_standby_names = ''
    │       │   │       │   │   │   └─ synchronous_commit = 'local'
    │       │   │       │   │   ├─ 特点：
    │       │   │       │   │   │   ├─ ❌ 弱一致性（最终一致性）
    │       │   │       │   │   │   ├─ ✅ 高可用性（分区时继续）
    │       │   │       │   │   │   └─ ✅ 分区容错
    │       │   │       │   │   ├─ 适用场景：
    │       │   │       │   │   │   ├─ 日志系统
    │       │   │       │   │   │   ├─ 分析系统
    │       │   │       │   │   │   ├─ 内容管理系统
    │       │   │       │   │   │   └─ 非关键数据
    │       │   │       │   │   ├─ 性能影响：
    │       │   │       │   │   │   ├─ 延迟：低（立即提交）
    │       │   │       │   │   │   ├─ 吞吐量：高（无等待）
    │       │   │       │   │   │   └─ 可用性：高（分区时继续）
    │       │   │       │   │   └─ 风险：
    │       │   │       │   │       ├─ 可能读到旧数据
    │       │   │       │   │       └─ 数据延迟
    │       │   │       │   │
    │       │   │       │   └─ 否 → 混合模式 ⭐
    │       │   │       │       ├─ 配置：部分同步
    │       │   │       │       │   └─ synchronous_standby_names = 'standby1'
    │       │   │       │       │   └─ synchronous_commit = 'remote_write'
    │       │   │       │       ├─ 特点：
    │       │   │       │       │   ├─ ⚖️ 平衡一致性和可用性
    │       │   │       │       │   ├─ ⚖️ 中等性能
    │       │   │       │       │   └─ ✅ 分区容错
    │       │   │       │       ├─ 适用场景：
    │       │   │       │       │   ├─ 通用业务系统
    │       │   │       │       │   ├─ 需要平衡的场景
    │       │   │       │       │   └─ 动态调整需求
    │       │   │       │       └─ 性能影响：
    │       │   │       │           ├─ 延迟：中（部分等待）
    │       │   │       │           ├─ 吞吐量：中
    │       │   │       │           └─ 可用性：中
    │       │   │       │
    │       │   │       └─ 性能要求分析
    │       │   │           ├─ 性能要求极高？
    │       │   │           │   ├─ 是 → AP模式
    │       │   │           │   └─ 否 → 继续判断
    │       │   │           │
    │       │   │           └─ 一致性要求极高？
    │       │   │               ├─ 是 → CP模式
    │       │   │               └─ 否 → 混合模式
    │       │   │
    │       │   └─ 场景类型分析
    │       │       ├─ 金融场景？
    │       │       │   └─ 是 → CP模式（强一致性优先）
    │       │       │
    │       │       ├─ 日志场景？
    │       │       │   └─ 是 → AP模式（高可用性优先）
    │       │       │
    │       │       └─ 通用场景？
    │       │           └─ 是 → 混合模式（平衡）
    │       │
    │       └─ 动态调整策略
    │           ├─ 是否需要动态调整？
    │           │   ├─ 是 → 混合模式（支持动态切换）
    │           │   │   ├─ 业务高峰期 → 切换到AP模式
    │           │   │   ├─ 业务低峰期 → 切换到CP模式
    │           │   │   └─ 故障恢复 → 临时切换到AP模式
    │           │   │
    │           │   └─ 否 → 根据业务需求选择固定模式
```

**决策树使用说明**：

1. **从根节点开始**：首先判断是否需要分布式系统
2. **业务需求分析**：根据业务需求选择一致性或可用性
3. **场景类型分析**：根据具体场景类型选择模式
4. **动态调整**：考虑是否需要动态调整CAP模式
5. **配置实施**：根据选择的模式配置PostgreSQL参数

**决策树特点**：

- ✅ 覆盖所有CAP模式（CP、AP、CA、混合）
- ✅ 包含PostgreSQL具体配置
- ✅ 提供性能影响分析
- ✅ 包含风险提示
- ✅ 支持动态调整策略

---

## 📊 第二部分：CP模式应用场景

### 2.1 CP模式特征

**CP模式核心特征**：

- ✅ **强一致性**：所有节点看到相同数据
- ❌ **低可用性**：分区时可能拒绝服务
- ✅ **分区容错**：系统在网络分区时仍能运行

**形式化表达**：

$$
\text{CP}(S) \iff \text{C}(S) \land \text{P}(S) \land \neg\text{A}(S)
$$

### 2.2 CP模式适用场景

#### 2.2.1 金融交易系统

**需求**：

- 账户余额必须准确
- 交易必须原子性
- 不允许数据不一致

**PostgreSQL实现**：

```sql
-- CP模式配置
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
ALTER SYSTEM SET synchronous_commit = 'remote_apply';
ALTER SYSTEM SET default_transaction_isolation = 'serializable';

-- 特征：
-- ✅ 强一致性：同步复制保证数据一致
-- ❌ 低可用性：分区时写入阻塞
-- ✅ 分区容错：系统继续运行（但可能阻塞）
```

#### 2.2.2 支付系统

**需求**：

- 支付金额必须准确
- 不允许重复支付
- 必须保证原子性

**PostgreSQL实现**：

```sql
-- CP模式配置
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 支付逻辑
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
INSERT INTO payments (account_id, amount) VALUES (1, 100);

COMMIT;

-- 特征：
-- ✅ 强一致性：SERIALIZABLE保证无异常
-- ❌ 低可用性：冲突时事务回滚
```

#### 2.2.3 库存管理系统

**需求**：

- 库存数量必须准确
- 不允许超卖
- 必须保证一致性

**PostgreSQL实现**：

```sql
-- CP模式配置
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 库存扣减
UPDATE inventory SET quantity = quantity - 1
WHERE product_id = 1 AND quantity > 0;

COMMIT;

-- 特征：
-- ✅ 强一致性：SERIALIZABLE防止超卖
-- ❌ 低可用性：高并发时性能下降
```

### 2.3 CP模式实现策略

#### 2.3.1 同步复制策略

**配置**：

```sql
-- 同步复制（CP模式）
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
ALTER SYSTEM SET synchronous_commit = 'remote_apply';
```

**特点**：

- 主库等待备库确认后才提交
- 分区时，如果无法联系到足够备库，写入阻塞
- 保证强一致性，但牺牲可用性

#### 2.3.2 两阶段提交策略

**配置**：

```sql
-- 两阶段提交（CP模式）
BEGIN;
-- 第一阶段：准备
PREPARE TRANSACTION 'tx1';
-- 第二阶段：提交
COMMIT PREPARED 'tx1';
```

**特点**：

- 分布式事务的原子性保证
- 分区时，如果无法联系到所有节点，事务阻塞
- 保证强一致性，但复杂度高

---

## 📊 第三部分：AP模式应用场景

### 3.1 AP模式特征

**AP模式核心特征**：

- ❌ **弱一致性**：可能返回不一致数据
- ✅ **高可用性**：分区时继续服务
- ✅ **分区容错**：系统在网络分区时继续运行

**形式化表达**：

$$
\text{AP}(S) \iff \text{A}(S) \land \text{P}(S) \land \neg\text{C}(S)
$$

### 3.2 AP模式适用场景

#### 3.2.1 日志系统

**需求**：

- 高写入吞吐量
- 允许短暂不一致
- 最终一致性即可

**PostgreSQL实现**：

```sql
-- AP模式配置
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';
ALTER SYSTEM SET default_transaction_isolation = 'read committed';

-- 特征：
-- ❌ 弱一致性：异步复制，可能延迟
-- ✅ 高可用性：分区时继续写入
-- ✅ 分区容错：系统继续运行
```

#### 3.2.2 分析系统

**需求**：

- 高查询吞吐量
- 允许数据延迟
- 最终一致性即可

**PostgreSQL实现**：

```sql
-- AP模式配置（只读备库）
-- 主库：异步复制
ALTER SYSTEM SET synchronous_standby_names = '';

-- 备库：只读查询
SET default_transaction_read_only = on;

-- 特征：
-- ❌ 弱一致性：备库可能延迟
-- ✅ 高可用性：备库继续查询
```

#### 3.2.3 内容管理系统

**需求**：

- 高并发读写
- 允许短暂不一致
- 最终一致性即可

**PostgreSQL实现**：

```sql
-- AP模式配置
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';

-- 特征：
-- ❌ 弱一致性：可能读到旧数据
-- ✅ 高可用性：高并发性能好
```

### 3.3 AP模式实现策略

#### 3.3.1 异步复制策略

**配置**：

```sql
-- 异步复制（AP模式）
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';
```

**特点**：

- 主库立即提交，不等待备库
- 分区时，主库继续服务
- 保证高可用性，但可能数据不一致

#### 3.3.2 最终一致性策略

**配置**：

```sql
-- 最终一致性（AP模式）
-- 主库：立即提交
ALTER SYSTEM SET synchronous_commit = 'local';

-- 备库：延迟同步
ALTER SYSTEM SET max_standby_streaming_delay = '30s';
```

**特点**：

- 允许短暂不一致
- 最终所有节点一致
- 保证高可用性，但一致性弱

---

## 📊 第四部分：CA模式局限性分析

### 4.1 CA模式定义

**CA模式核心特征**：

- ✅ **强一致性**：所有节点看到相同数据
- ✅ **高可用性**：系统始终可用
- ❌ **无分区容错**：无法容忍网络分区

**形式化表达**：

$$
\text{CA}(S) \iff \text{C}(S) \land \text{A}(S) \land \neg\text{P}(S)
$$

### 4.2 CA模式局限性

**局限性分析**：

1. **无法分布式**：
   - CA模式要求无网络分区
   - 分布式系统必然存在网络分区风险
   - 因此CA模式在分布式系统中不可行

2. **单机限制**：
   - CA模式只能用于单机系统
   - 单机系统无法扩展
   - 无法满足大规模系统需求

3. **CAP定理约束**：
   - CAP定理指出三者不能同时满足
   - CA模式在分布式系统中违反CAP定理
   - 必须选择CP或AP模式

### 4.3 CA模式适用场景

**适用场景**：

- **单机PostgreSQL**：
  - 无网络分区风险
  - 可以同时保证一致性和可用性
  - 适合小规模应用

**PostgreSQL实现**：

```sql
-- CA模式（单机PostgreSQL）
-- 无需特殊配置，默认即可

-- 特征：
-- ✅ 强一致性：单机保证
-- ✅ 高可用性：单机保证
-- ❌ 无分区容错：单机无分区
```

---

## 📊 第五部分：PostgreSQL场景下的CAP选择

### 5.1 PostgreSQL CAP选择决策流程

**决策流程图**：

```text
开始
  │
  ├─ 是否需要分布式？
  │   ├─ 否 → CA模式（单机PostgreSQL）
  │   │   └─ 配置：默认配置
  │   │
  │   └─ 是 → 继续判断
  │       │
  │       ├─ 业务是否需要强一致性？
  │       │   ├─ 是 → CP模式
  │       │   │   ├─ 配置：同步复制
  │       │   │   ├─ 隔离级别：SERIALIZABLE
  │       │   │   └─ 场景：金融、支付
  │       │   │
  │       │   └─ 否 → AP模式
  │       │       ├─ 配置：异步复制
  │       │       ├─ 隔离级别：READ COMMITTED
  │       │       └─ 场景：日志、分析
  │       │
  │       └─ 是否需要高可用性？
  │           ├─ 是 → AP模式
  │           └─ 否 → CP模式
```

### 5.2 场景化CAP选择指南

#### 5.2.1 金融场景

**需求**：

- 强一致性
- 数据准确性
- 可接受低可用性

**CAP选择**：**CP模式**

**PostgreSQL配置**：

```sql
-- CP模式配置
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
ALTER SYSTEM SET synchronous_commit = 'remote_apply';
ALTER SYSTEM SET default_transaction_isolation = 'serializable';
```

#### 5.2.2 日志场景

**需求**：

- 高写入吞吐量
- 允许短暂不一致
- 高可用性

**CAP选择**：**AP模式**

**PostgreSQL配置**：

```sql
-- AP模式配置
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';
ALTER SYSTEM SET default_transaction_isolation = 'read committed';
```

#### 5.2.3 通用场景

**需求**：

- 平衡一致性和可用性
- 动态调整

**CAP选择**：**混合模式**

**PostgreSQL配置**：

```sql
-- 混合模式配置
ALTER SYSTEM SET synchronous_standby_names = 'standby1';  -- 只同步一个
ALTER SYSTEM SET synchronous_commit = 'remote_write';
ALTER SYSTEM SET default_transaction_isolation = 'repeatable read';
```

### 5.3 CAP动态调整策略

**动态调整场景**：

1. **业务高峰期**：切换到AP模式，提高可用性
2. **业务低峰期**：切换到CP模式，提高一致性
3. **故障恢复**：临时切换到AP模式，快速恢复

**PostgreSQL动态调整**：

```sql
-- 动态切换到AP模式（提高可用性）
ALTER SYSTEM SET synchronous_standby_names = '';
SELECT pg_reload_conf();

-- 动态切换到CP模式（提高一致性）
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
SELECT pg_reload_conf();
```

**监控与告警**：

```sql
-- 监控CAP模式
SELECT
    name,
    setting,
    unit,
    context
FROM pg_settings
WHERE name IN (
    'synchronous_standby_names',
    'synchronous_commit',
    'default_transaction_isolation'
);
```

---

## 📝 总结

### 核心结论

1. **CAP选择需要基于业务需求**：金融场景选择CP，日志场景选择AP
2. **CP和AP模式各有适用场景**：不能一概而论
3. **CA模式在分布式系统中不可行**：只能用于单机系统
4. **PostgreSQL支持动态CAP调整**：可以根据场景动态切换

### 实践建议

1. **根据业务需求选择CAP模式**：
   - 金融场景：CP模式（同步复制）
   - 日志场景：AP模式（异步复制）
   - 通用场景：混合模式（动态调整）

2. **监控CAP指标**：
   - 同步延迟（CP模式）
   - 复制延迟（AP模式）
   - 可用性指标

3. **理解CAP权衡**：
   - CP模式：一致性优先，牺牲可用性
   - AP模式：可用性优先，牺牲一致性
   - 根据场景动态调整

---

## 📚 外部资源引用

### Wikipedia资源

1. **CAP定理相关**：
   - [CAP Theorem](https://en.wikipedia.org/wiki/CAP_theorem)
   - [Consistency Model](https://en.wikipedia.org/wiki/Consistency_model)
   - [Eventual Consistency](https://en.wikipedia.org/wiki/Eventual_consistency)
   - [High Availability](https://en.wikipedia.org/wiki/High_availability)
   - [Network Partition](https://en.wikipedia.org/wiki/Network_partition)

2. **分布式系统**：
   - [Distributed Computing](https://en.wikipedia.org/wiki/Distributed_computing)
   - [Distributed Database](https://en.wikipedia.org/wiki/Distributed_database)
   - [System Design](https://en.wikipedia.org/wiki/Systems_design)

### 学术论文

1. **CAP定理**：
   - Brewer, E. A. (2000). "Towards Robust Distributed Systems"
   - Gilbert, S., & Lynch, N. (2002). "Brewer's Conjecture and the Feasibility of
     Consistent, Available, Partition-Tolerant Web Services"
   - Abadi, D. (2012). "Consistency Tradeoffs in Modern Distributed Database System Design"

2. **决策框架**：
   - Fox, A., et al. (1997). "Cluster-Based Scalable Network Services"
   - DeCandia, G., et al. (2007). "Dynamo: Amazon's Highly Available Key-value Store"

### 官方文档

1. **PostgreSQL官方文档**：
   - [High Availability](https://www.postgresql.org/docs/current/high-availability.html)
   - [Replication](https://www.postgresql.org/docs/current/high-availability.html)
   - [Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)

2. **分布式数据库文档**：
   - [Google Spanner Documentation](https://cloud.google.com/spanner/docs)
   - [TiDB Documentation](https://docs.pingcap.com/tidb/stable)
   - [CockroachDB Documentation](https://www.cockroachlabs.com/docs/)

---

**最后更新**: 2024年
**维护状态**: ✅ 已完成
