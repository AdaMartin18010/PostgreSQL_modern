# PostgreSQL FP-Growth算法完整指南

> **创建日期**: 2025年1月
> **技术栈**: PostgreSQL 17+/18+ | 数据挖掘 | FP-Growth | 频繁模式
> **难度级别**: ⭐⭐⭐⭐⭐ (专家级)
> **参考标准**: FP-Growth (Han et al.), Frequent Pattern Mining, Data Mining

---

## 📋 目录

- [PostgreSQL FP-Growth算法完整指南](#postgresql-fp-growth算法完整指南)
  - [📋 目录](#-目录)
  - [FP-Growth概述](#fp-growth概述)
    - [理论基础](#理论基础)
    - [核心思想](#核心思想)
    - [与Apriori的对比](#与apriori的对比)
  - [1. FP树构建](#1-fp树构建)
    - [1.1 频繁项排序](#11-频繁项排序)
    - [1.2 FP树结构](#12-fp树结构)
  - [📚 参考资源](#-参考资源)

---

## FP-Growth概述

**FP-Growth（Frequent Pattern Growth）**是高效的频繁项集挖掘算法，避免了Apriori的多次数据库扫描。

### 理论基础

FP-Growth使用**FP树（Frequent Pattern Tree）**压缩存储事务数据，通过模式增长挖掘频繁项集。

### 核心思想

1. **FP树构建**: 将事务压缩为树结构
2. **模式增长**: 从条件模式基递归构建条件FP树
3. **频繁项集**: 通过模式增长生成所有频繁项集

### 与Apriori的对比

| 特性 | FP-Growth | Apriori |
|------|-----------|---------|
| **数据库扫描** | 2次 | 多次 |
| **候选项生成** | 不需要 | 需要 |
| **时间复杂度** | $O(n)$ | $O(2^m)$ |

---

## 1. FP树构建

### 1.1 频繁项排序

**频繁项排序**按支持度降序排列。

```sql
-- FP-Growth数据准备（复用transaction_data）
-- FP树构建：频繁项排序
WITH item_support AS (
    SELECT
        item_id,
        COUNT(DISTINCT transaction_id) AS support_count
    FROM transaction_data
    GROUP BY item_id
    HAVING COUNT(DISTINCT transaction_id) >= 2  -- 最小支持度
),
sorted_items AS (
    SELECT
        item_id,
        support_count,
        ROW_NUMBER() OVER (ORDER BY support_count DESC, item_id) AS item_order
    FROM item_support
)
SELECT
    item_id,
    support_count,
    item_order
FROM sorted_items
ORDER BY item_order;
```

### 1.2 FP树结构

**FP树**是前缀树结构，共享相同前缀的项。

```sql
-- FP树节点表示（简化版）
WITH fp_tree_nodes AS (
    SELECT
        transaction_id,
        ARRAY_AGG(item_id ORDER BY item_order) AS sorted_items
    FROM transaction_data td
    JOIN sorted_items si ON td.item_id = si.item_id
    GROUP BY transaction_id
)
SELECT
    transaction_id,
    sorted_items,
    array_length(sorted_items, 1) AS item_count
FROM fp_tree_nodes
ORDER BY transaction_id;
```

---

## 📚 参考资源

1. **Han, J., et al. (2004)**: "Mining Frequent Patterns without Candidate Generation"

---

**最后更新**: 2025年1月
**文档状态**: ✅ 已完成
