# ACID公理系统

> **文档编号**: AXIOM-ACID-001
> **主题**: ACID公理系统
> **版本**: PostgreSQL 17 & 18
> **状态**: ✅ 已完成

---

## 📑 目录

- [ACID公理系统](#acid公理系统)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📊 第一部分：形式化基础](#-第一部分形式化基础)
    - [1.1 符号定义](#11-符号定义)
    - [1.2 基本概念](#12-基本概念)
  - [📊 第二部分：ACID公理](#-第二部分acid公理)
    - [2.1 原子性公理](#21-原子性公理)
    - [2.2 一致性公理](#22-一致性公理)
    - [2.3 隔离性公理](#23-隔离性公理)
    - [2.4 持久性公理](#24-持久性公理)
  - [📊 第三部分：ACID关系公理](#-第三部分acid关系公理)
    - [3.1 原子性与一致性](#31-原子性与一致性)
    - [3.2 隔离性与一致性](#32-隔离性与一致性)
    - [3.3 持久性与一致性](#33-持久性与一致性)
  - [📊 第四部分：推理规则](#-第四部分推理规则)
  - [📚 参考资料](#-参考资料)

---

## 📋 概述

本文档定义ACID属性的形式化公理系统，建立ACID的形式化数学基础。这些公理与MVCC核心公理一起，构成完整的MVCC-ACID公理体系。

---

## 📊 第一部分：形式化基础

### 1.1 符号定义

**基本符号**：

- `T` - 事务集合
- `τ ∈ T` - 事务τ
- `O(τ)` - 事务τ的操作集合
- `S` - 数据库状态集合
- `s ∈ S` - 数据库状态s
- `C` - 一致性约束集合
- `c ∈ C` - 一致性约束c

**关系符号**：

- `begin(τ)` - 事务τ开始
- `commit(τ)` - 事务τ提交
- `abort(τ)` - 事务τ中止
- `state(τ)` - 事务τ的数据库状态
- `satisfies(s, c)` - 状态s满足约束c

### 1.2 基本概念

**定义1.1（事务）**：

事务τ是一个操作序列：
```
τ = [o₁, o₂, ..., oₙ]
```

其中每个操作oᵢ是读操作或写操作。

**定义1.2（数据库状态）**：

数据库状态s是一个映射：
```
s: R → V
```

将元组r映射到版本v。

**定义1.3（一致性约束）**：

一致性约束c是一个谓词：
```
c: S → {true, false}
```

判断状态s是否满足约束c。

---

## 📊 第二部分：ACID公理

### 2.1 原子性公理

**公理2.1（原子性 - 全部提交）**：

如果事务τ提交，则τ的所有操作都生效：
```
commit(τ) ⟹ ∀o ∈ O(τ), applied(o, state(τ))
```

**公理2.2（原子性 - 全部回滚）**：

如果事务τ中止，则τ的所有操作都不生效：
```
abort(τ) ⟹ ∀o ∈ O(τ), ¬applied(o, state(τ))
```

**公理2.3（原子性 - 二元性）**：

事务τ要么全部提交，要么全部中止：
```
commit(τ) ⟺ ¬abort(τ)
```

### 2.2 一致性公理

**公理2.4（一致性 - 初始状态）**：

数据库初始状态满足所有一致性约束：
```
∀c ∈ C, satisfies(initial_state, c)
```

**公理2.5（一致性 - 提交后状态）**：

如果事务τ提交，则提交后的状态满足所有一致性约束：
```
commit(τ) ⟹ ∀c ∈ C, satisfies(state(τ), c)
```

**公理2.6（一致性 - 事务内状态）**：

事务τ执行过程中的中间状态可能不满足一致性约束，但提交时必须满足：
```
∀s ∈ intermediate_states(τ),
  (satisfies(s, c) ∨ ¬commit(τ)) ⟹
  (commit(τ) ⟹ satisfies(state(τ), c))
```

### 2.3 隔离性公理

**公理2.7（隔离性 - 读未提交）**：

READ UNCOMMITTED隔离级别允许读取未提交的数据：
```
isolation_level(τ) = READ_UNCOMMITTED ⟹
  ∀τ' ∈ concurrent(τ), can_read(τ, uncommitted_data(τ'))
```

**公理2.8（隔离性 - 读已提交）**：

READ COMMITTED隔离级别只允许读取已提交的数据：
```
isolation_level(τ) = READ_COMMITTED ⟹
  ∀τ' ∈ concurrent(τ), can_read(τ, committed_data(τ'))
```

**公理2.9（隔离性 - 可重复读）**：

REPEATABLE READ隔离级别保证同一事务内多次读取结果一致：
```
isolation_level(τ) = REPEATABLE_READ ⟹
  ∀r ∈ R, ∀t₁, t₂ ∈ time(τ), read(τ, r, t₁) = read(τ, r, t₂)
```

**公理2.10（隔离性 - 可串行化）**：

SERIALIZABLE隔离级别保证事务执行结果等价于某个串行执行：
```
isolation_level(τ) = SERIALIZABLE ⟹
  ∃serial_order, result(concurrent_execution) = result(serial_order)
```

### 2.4 持久性公理

**公理2.11（持久性 - 提交持久化）**：

如果事务τ提交，则τ的修改持久化到存储：
```
commit(τ) ⟹ persisted(state(τ))
```

**公理2.12（持久性 - 故障恢复）**：

系统故障后恢复，已提交事务的修改仍然存在：
```
crash_recovery() ⟹
  ∀τ: commit(τ) ∧ timestamp(commit(τ)) < crash_time,
    state(τ) ∈ recovered_state
```

**公理2.13（持久性 - WAL保证）**：

所有提交操作都写入WAL，WAL持久化保证数据持久化：
```
commit(τ) ⟹ written_to_wal(O(τ)) ⟹ persisted(state(τ))
```

---

## 📊 第三部分：ACID关系公理

### 3.1 原子性与一致性

**公理3.1（原子性保证一致性）**：

原子性保证事务要么全部生效，要么全部不生效，从而保证一致性：
```
atomicity(τ) ⟹
  (commit(τ) ⟹ consistency(state(τ))) ∨
  (abort(τ) ⟹ consistency(previous_state))
```

### 3.2 隔离性与一致性

**公理3.2（隔离性保证一致性）**：

隔离性防止并发事务相互干扰，保证一致性：
```
isolation(τ₁, τ₂) ⟹
  consistency(state(τ₁)) ∧ consistency(state(τ₂))
```

### 3.3 持久性与一致性

**公理3.3（持久性保证一致性）**：

持久性保证已提交的一致性状态不会丢失：
```
durability(τ) ⟹
  commit(τ) ⟹ persisted(consistent_state(τ))
```

---

## 📊 第四部分：推理规则

**规则4.1（ACID完整性）**：

事务τ满足ACID属性，当且仅当：
```
ACID(τ) ⟺
  atomicity(τ) ∧
  consistency(τ) ∧
  isolation(τ) ∧
  durability(τ)
```

**规则4.2（MVCC保证ACID）**：

MVCC机制保证ACID属性：
```
MVCC_mechanism ⟹
  ∀τ ∈ T, ACID(τ)
```

---

## 📚 参考资料

1. PostgreSQL官方文档 - ACID属性
2. 数据库理论 - 事务处理原理
3. MVCC核心公理 - 本文档同目录
4. 形式化方法 - 公理系统

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
