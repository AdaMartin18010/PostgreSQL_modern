---

> **📋 文档来源**: `MVCC-ACID-CAP\01-理论基础\公理系统\MVCC核心公理.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# MVCC核心公理

> **文档编号**: AXIOM-MVCC-CORE-001
> **主题**: MVCC核心公理
> **版本**: PostgreSQL 17 & 18
> **状态**: ✅ 已完成

---

## 📑 目录

- [MVCC核心公理](#mvcc核心公理)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [第一部分：形式化基础](#第一部分形式化基础)
    - [1.1 符号定义](#11-符号定义)
    - [1.2 基本概念](#12-基本概念)
  - [第二部分：核心公理](#第二部分核心公理)
    - [2.1 版本公理](#21-版本公理)
    - [2.2 可见性公理](#22-可见性公理)
    - [2.3 快照公理](#23-快照公理)
    - [2.4 版本链公理](#24-版本链公理)
  - [第三部分：推理规则](#第三部分推理规则)
    - [3.1 版本推理规则](#31-版本推理规则)
    - [3.2 可见性推理规则](#32-可见性推理规则)
    - [3.3 快照推理规则](#33-快照推理规则)
  - [第四部分：公理一致性](#第四部分公理一致性)
    - [4.1 公理独立性](#41-公理独立性)
    - [4.2 公理完备性](#42-公理完备性)
    - [4.3 公理一致性证明](#43-公理一致性证明)
  - [📚 参考资料](#-参考资料)
    - [Wikipedia资源](#wikipedia资源)
    - [学术论文](#学术论文)
    - [官方文档](#官方文档)

---

## 📋 概述

本文档定义PostgreSQL MVCC的核心公理系统，建立MVCC的形式化数学基础。这些公理是不可证明的基础假设，所有MVCC的理论和实现都基于这些公理。

**公理体系目标**：

1. **精确定义** - 形式化定义MVCC的核心概念
2. **推理基础** - 为MVCC定理提供推理基础
3. **一致性保证** - 确保公理体系的一致性

---

## 第一部分：形式化基础

### 1.1 符号定义

**基本符号**：

- `T` - 事务集合
- `V` - 版本集合
- `R` - 元组集合
- `S` - 快照集合
- `τ ∈ T` - 事务τ
- `v ∈ V` - 版本v
- `r ∈ R` - 元组r
- `s ∈ S` - 快照s

**关系符号**：

- `xmin(v)` - 版本v的创建事务ID
- `xmax(v)` - 版本v的删除事务ID
- `snapshot(τ)` - 事务τ的快照
- `visible(v, s)` - 版本v在快照s中可见
- `committed(τ)` - 事务τ已提交
- `aborted(τ)` - 事务τ已中止

### 1.2 基本概念

**定义1.1（版本）**：

版本v是一个四元组：

```text
v = (xmin, xmax, data, timestamp)
```

其中：

- `xmin ∈ T ∪ {⊥}` - 创建事务ID（⊥表示未分配）
- `xmax ∈ T ∪ {⊥}` - 删除事务ID（⊥表示未删除）
- `data` - 版本数据
- `timestamp` - 版本时间戳

**定义1.2（快照）**：

快照s是一个事务ID集合：

```text
s = {τ₁, τ₂, ..., τₙ}
```

表示在快照s创建时，事务τ₁, τ₂, ..., τₙ已提交。

**定义1.3（版本链）**：

版本链C(r)是元组r的所有版本的序列：

```text
C(r) = [v₁, v₂, ..., vₙ]
```

满足：

- `xmin(vᵢ) < xmin(vᵢ₊₁)` （按创建事务ID排序）
- `xmax(vᵢ) = xmin(vᵢ₊₁)` 或 `xmax(vᵢ) = ⊥` （版本链连续性）

---

## 第二部分：核心公理

### 2.1 版本公理

**公理2.1（版本存在性）**：

对于每个元组r和事务τ，如果τ修改r，则存在版本v使得：

```text
xmin(v) = τ ∧ v ∈ C(r)
```

**公理2.2（版本唯一性）**：

对于每个元组r和事务τ，最多存在一个版本v使得：

```text
xmin(v) = τ ∧ v ∈ C(r)
```

**公理2.3（版本链完整性）**：

对于每个元组r，版本链C(r)包含r的所有版本，且：

```text
∀v ∈ C(r), ∃τ ∈ T: xmin(v) = τ
```

### 2.2 可见性公理

**公理2.4（可见性规则）**：

版本v在快照s中可见，当且仅当：

```text
visible(v, s) ⟺
  (xmin(v) ∈ s ∨ xmin(v) = ⊥) ∧
  (xmax(v) = ⊥ ∨ xmax(v) ∉ s) ∧
  committed(xmin(v))
```

**公理2.5（快照一致性）**：

对于快照s中的任意两个版本v₁和v₂，如果它们属于同一元组r，则：

```text
visible(v₁, s) ∧ visible(v₂, s) ⟹ v₁ = v₂
```

**公理2.6（可见性传递性）**：

如果版本v在快照s中可见，且快照s'包含s的所有已提交事务，则：

```text
visible(v, s) ∧ s ⊆ s' ⟹ visible(v, s')
```

### 2.3 快照公理

**公理2.7（快照分配）**：

对于每个事务τ，存在唯一的快照snapshot(τ)，使得：

```text
snapshot(τ) = {τ' ∈ T | committed(τ') ∧ timestamp(τ') < timestamp(τ)}
```

**公理2.8（快照隔离）**：

对于两个并发事务τ₁和τ₂，如果它们读取同一元组r，则：

```text
snapshot(τ₁) = snapshot(τ₂) ⟹
  ∀v ∈ C(r), visible(v, snapshot(τ₁)) = visible(v, snapshot(τ₂))
```

**公理2.9（快照单调性）**：

对于事务τ₁和τ₂，如果τ₁在τ₂之前开始，则：

```text
timestamp(τ₁) < timestamp(τ₂) ⟹ snapshot(τ₁) ⊆ snapshot(τ₂)
```

### 2.4 版本链公理

**公理2.10（版本链顺序性）**：

对于版本链C(r) = [v₁, v₂, ..., vₙ]，满足：

```text
∀i < j, xmin(vᵢ) < xmin(vⱼ)
```

**公理2.11（版本链连续性）**：

对于版本链C(r) = [v₁, v₂, ..., vₙ]，满足：

```text
∀i < n, xmax(vᵢ) = xmin(vᵢ₊₁) ∨ xmax(vᵢ) = ⊥
```

**公理2.12（版本链可追溯性）**：

对于版本链C(r)中的任意版本vᵢ，存在从v₁到vᵢ的路径，使得：

```text
∀j < i, ∃vⱼ ∈ C(r): xmax(vⱼ) = xmin(vᵢ)
```

---

## 第三部分：推理规则

### 3.1 版本推理规则

**规则3.1（版本创建）**：

如果事务τ创建元组r的版本v，则：

```text
xmin(v) = τ ∧ v ∈ C(r) ∧ committed(τ) ⟹ visible(v, snapshot(τ'))
```

其中τ'是任何在τ提交后开始的事务。

**规则3.2（版本删除）**：

如果事务τ删除版本v，则：

```text
xmax(v) = τ ∧ committed(τ) ⟹
  ∀s: timestamp(s) > timestamp(τ), ¬visible(v, s)
```

### 3.2 可见性推理规则

**规则3.3（可见性判定）**：

版本v在快照s中可见，当且仅当：

```text
visible(v, s) ⟺
  (xmin(v) ∈ s ∨ xmin(v) = ⊥) ∧
  (xmax(v) = ⊥ ∨ xmax(v) ∉ s) ∧
  committed(xmin(v))
```

**规则3.4（最新可见版本）**：

对于元组r和快照s，存在唯一版本v使得：

```text
visible(v, s) ∧ ∀v' ∈ C(r), visible(v', s) ⟹ timestamp(v') ≤ timestamp(v)
```

### 3.3 快照推理规则

**规则3.5（快照一致性）**：

对于事务τ和快照snapshot(τ)，满足：

```text
∀r ∈ R, ∃!v ∈ C(r): visible(v, snapshot(τ))
```

**规则3.6（快照隔离）**：

对于两个并发事务τ₁和τ₂，如果它们读取同一元组r，则：

```text
snapshot(τ₁) = snapshot(τ₂) ⟹
  ∀v ∈ C(r), visible(v, snapshot(τ₁)) = visible(v, snapshot(τ₂))
```

---

## 第四部分：公理一致性

### 4.1 公理独立性

**定理4.1（公理独立性）**：

公理2.1到公理2.12是独立的，即：

- 任何一个公理都不能从其他公理推导出来
- 移除任何一个公理都会导致MVCC系统不完整

**证明思路**：

通过构造反例证明每个公理的独立性。

### 4.2 公理完备性

**定理4.2（公理完备性）**：

公理2.1到公理2.12是完备的，即：

- 所有MVCC的性质都可以从这些公理推导出来
- 不需要额外的公理

**证明思路**：

通过归纳证明所有MVCC操作都可以用这些公理描述。

### 4.3 公理一致性证明

**定理4.3（公理一致性）**：

公理2.1到公理2.12是一致的，即：

- 不存在矛盾
- 所有公理可以同时成立

**证明思路**：

通过构造模型证明所有公理可以同时满足。

---

## 📚 参考资料

### Wikipedia资源

1. **MVCC相关**：
   - [Multiversion Concurrency Control](https://en.wikipedia.org/wiki/Multiversion_concurrency_control)
   - [Concurrency Control](https://en.wikipedia.org/wiki/Concurrency_control)
   - [Snapshot Isolation](https://en.wikipedia.org/wiki/Snapshot_isolation)

2. **形式化方法**：
   - [Axiom](https://en.wikipedia.org/wiki/Axiom)
   - [Formal System](https://en.wikipedia.org/wiki/Formal_system)
   - [First-Order Logic](https://en.wikipedia.org/wiki/First-order_logic)

### 学术论文

1. **MVCC理论**：
   - Reed, D. P. (1978). "Naming and Synchronization in a Decentralized Computer System"
   - Bernstein, P. A., & Goodman, N. (1983). "Multiversion Concurrency Control—Theory and Algorithms"
   - Adya, A., et al. (2000). "Generalized Isolation Level Definitions"

2. **快照隔离**：
   - Berenson, H., et al. (1995). "A Critique of ANSI SQL Isolation Levels"
   - Fekete, A., et al. (2005). "Making Snapshot Isolation Serializable"

3. **形式化方法**：
   - Lamport, L. (2002). "Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers"

### 官方文档

1. **PostgreSQL官方文档**：
   - [MVCC](https://www.postgresql.org/docs/current/mvcc.html)
   - [Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
   - [Concurrency Control](https://www.postgresql.org/docs/current/mvcc.html)

2. **数据库理论**：
   - Gray, J., & Reuter, A. (1993). "Transaction Processing: Concepts and Techniques"

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
