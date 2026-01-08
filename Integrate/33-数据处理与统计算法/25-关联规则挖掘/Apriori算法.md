# PostgreSQL Apriori算法完整指南

> **创建日期**: 2025年1月
> **技术栈**: PostgreSQL 17+/18+ | 数据挖掘 | 关联规则 | 频繁项集
> **难度级别**: ⭐⭐⭐⭐⭐ (专家级)
> **参考标准**: Data Mining (Han et al.), Association Rule Mining, Market Basket Analysis

---

## 📋 目录

- [PostgreSQL Apriori算法完整指南](#postgresql-apriori算法完整指南)
  - [📋 目录](#-目录)
  - [Apriori概述](#apriori概述)
    - [理论基础](#理论基础)
    - [核心思想](#核心思想)
    - [应用场景](#应用场景)
  - [1. 频繁项集挖掘](#1-频繁项集挖掘)
    - [1.1 支持度计算](#11-支持度计算)
    - [1.2 候选项集生成](#12-候选项集生成)
    - [1.3 剪枝策略](#13-剪枝策略)
  - [2. 关联规则生成](#2-关联规则生成)
    - [2.1 置信度计算](#21-置信度计算)
    - [2.2 规则评估](#22-规则评估)
  - [3. 提升度分析](#3-提升度分析)
    - [3.1 提升度计算](#31-提升度计算)
  - [4. 复杂度分析](#4-复杂度分析)
  - [5. 实际应用案例](#5-实际应用案例)
    - [5.1 市场篮分析](#51-市场篮分析)
  - [📚 参考资源](#-参考资源)
  - [📊 性能优化建议](#-性能优化建议)
  - [🎯 最佳实践](#-最佳实践)

---

## Apriori概述

**Apriori算法**是经典的关联规则挖掘算法，用于发现频繁项集和关联规则。

### 理论基础

**关联规则**: $X \Rightarrow Y$，表示如果 $X$ 出现，则 $Y$ 也可能出现。

**支持度**: $support(X \Rightarrow Y) = P(X \cup Y)$
**置信度**: $confidence(X \Rightarrow Y) = P(Y | X) = \frac{P(X \cup Y)}{P(X)}$

### 核心思想

**Apriori性质**: 频繁项集的子集也是频繁的。

**算法流程**:

1. 找出所有1-项频繁项集
2. 使用频繁k-项集生成候选(k+1)-项集
3. 扫描数据库计算支持度
4. 剪枝非频繁项集
5. 重复直到没有新的频繁项集

### 应用场景

| 应用领域 | 具体应用 |
|---------|---------|
| **零售** | 市场篮分析、商品推荐 |
| **推荐系统** | 协同过滤、商品关联 |
| **Web挖掘** | 页面关联、用户行为 |
| **医疗** | 症状-疾病关联 |

---

## 1. 频繁项集挖掘

### 1.1 支持度计算

**支持度**是项集在事务中出现的频率。

```sql
-- Apriori数据准备（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'transaction_data') THEN
            RAISE WARNING '表 transaction_data 已存在，先删除';
            DROP TABLE transaction_data CASCADE;
        END IF;

        CREATE TABLE transaction_data (
            transaction_id INTEGER NOT NULL,
            item_id VARCHAR(20) NOT NULL,
            PRIMARY KEY (transaction_id, item_id)
        );

        -- 插入事务数据
        INSERT INTO transaction_data (transaction_id, item_id) VALUES
            (1, 'A'), (1, 'B'), (1, 'C'),
            (2, 'A'), (2, 'B'),
            (3, 'B'), (3, 'C'),
            (4, 'A'), (4, 'B'), (4, 'C'),
            (5, 'A'), (5, 'C');

        RAISE NOTICE '表 transaction_data 创建成功';
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 transaction_data 已存在';
        WHEN OTHERS THEN
            RAISE EXCEPTION '创建表失败: %', SQLERRM;
    END;
END $$;

-- 1-项集支持度计算
WITH total_transactions AS (
    SELECT COUNT(DISTINCT transaction_id) AS total_count
    FROM transaction_data
),
item_support AS (
    SELECT
        item_id,
        COUNT(DISTINCT transaction_id) AS support_count,
        COUNT(DISTINCT transaction_id)::NUMERIC / (SELECT total_count FROM total_transactions) AS support
    FROM transaction_data
    GROUP BY item_id
),
min_support AS (
    SELECT 0.4 AS min_sup  -- 最小支持度阈值
)
SELECT
    item_id,
    support_count,
    ROUND((support * 100)::numeric, 2) AS support_percentage,
    CASE
        WHEN support >= (SELECT min_sup FROM min_support) THEN 'Frequent'
        ELSE 'Infrequent'
    END AS status
FROM item_support
ORDER BY support DESC;

-- 性能测试
EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
SELECT
    item_id,
    COUNT(DISTINCT transaction_id) AS support_count
FROM transaction_data
GROUP BY item_id;
```

### 1.2 候选项集生成

**候选项集生成**使用连接和剪枝操作。

```sql
-- 2-项集候选项生成
WITH frequent_1_items AS (
    SELECT item_id
    FROM transaction_data
    GROUP BY item_id
    HAVING COUNT(DISTINCT transaction_id) >= 2  -- 最小支持度
),
candidate_2_items AS (
    SELECT
        f1.item_id AS item1,
        f2.item_id AS item2
    FROM frequent_1_items f1
    CROSS JOIN frequent_1_items f2
    WHERE f1.item_id < f2.item_id  -- 避免重复
),
support_2_items AS (
    SELECT
        c.item1,
        c.item2,
        COUNT(DISTINCT t1.transaction_id) AS support_count
    FROM candidate_2_items c
    JOIN transaction_data t1 ON c.item1 = t1.item_id
    JOIN transaction_data t2 ON c.item2 = t2.item_id AND t1.transaction_id = t2.transaction_id
    GROUP BY c.item1, c.item2
)
SELECT
    item1,
    item2,
    support_count,
    ROUND((support_count::NUMERIC / (SELECT COUNT(DISTINCT transaction_id) FROM transaction_data) * 100)::numeric, 2) AS support_pct
FROM support_2_items
WHERE support_count >= 2
ORDER BY support_count DESC;
```

### 1.3 剪枝策略

**剪枝**基于Apriori性质：如果项集的子集不是频繁的，则该项集也不是频繁的。

```sql
-- 剪枝操作（检查子集是否频繁）
WITH candidate_itemsets AS (
    SELECT
        ARRAY[item1, item2] AS itemset,
        support_count
    FROM support_2_items
),
subset_check AS (
    SELECT
        itemset,
        support_count,
        -- 检查所有子集是否频繁（简化版）
        CASE
            WHEN itemset[1] IN (SELECT item_id FROM frequent_1_items)
                 AND itemset[2] IN (SELECT item_id FROM frequent_1_items)
            THEN 'Keep'
            ELSE 'Prune'
        END AS prune_decision
    FROM candidate_itemsets
)
SELECT
    itemset,
    support_count,
    prune_decision
FROM subset_check
WHERE prune_decision = 'Keep';
```

---

## 2. 关联规则生成

### 2.1 置信度计算

**置信度**衡量规则的可靠性。

```sql
-- 关联规则生成和置信度计算
WITH rule_support AS (
    SELECT
        item1 AS antecedent,
        item2 AS consequent,
        support_count AS rule_support
    FROM support_2_items
),
antecedent_support AS (
    SELECT
        item_id,
        COUNT(DISTINCT transaction_id) AS antecedent_count
    FROM transaction_data
    GROUP BY item_id
),
confidence_calculation AS (
    SELECT
        rs.antecedent,
        rs.consequent,
        rs.rule_support,
        asup.antecedent_count,
        rs.rule_support::NUMERIC / NULLIF(asup.antecedent_count, 0) AS confidence
    FROM rule_support rs
    JOIN antecedent_support asup ON rs.antecedent = asup.item_id
)
SELECT
    antecedent || ' => ' || consequent AS rule,
    rule_support,
    ROUND((confidence * 100)::numeric, 2) AS confidence_percentage
FROM confidence_calculation
ORDER BY confidence DESC;
```

### 2.2 规则评估

**规则评估**使用多个指标。

```sql
-- 综合规则评估
WITH rule_metrics AS (
    SELECT
        antecedent,
        consequent,
        rule_support,
        confidence,
        (SELECT COUNT(DISTINCT transaction_id) FROM transaction_data) AS total_transactions,
        (SELECT COUNT(DISTINCT transaction_id) FROM transaction_data WHERE item_id = consequent) AS consequent_support
    FROM confidence_calculation
),
evaluation AS (
    SELECT
        antecedent || ' => ' || consequent AS rule,
        ROUND((confidence * 100)::numeric, 2) AS confidence_pct,
        ROUND((rule_support::NUMERIC / total_transactions * 100)::numeric, 2) AS support_pct,
        ROUND((confidence / NULLIF(consequent_support::NUMERIC / total_transactions, 0))::numeric, 2) AS lift,
        CASE
            WHEN confidence > 0.6 AND rule_support::NUMERIC / total_transactions > 0.3 THEN 'Strong'
            WHEN confidence > 0.4 THEN 'Moderate'
            ELSE 'Weak'
        END AS rule_strength
    FROM rule_metrics
)
SELECT
    rule,
    confidence_pct,
    support_pct,
    ROUND(lift::numeric, 2) AS lift,
    rule_strength
FROM evaluation
ORDER BY confidence DESC, support_pct DESC;
```

---

## 3. 提升度分析

### 3.1 提升度计算

**提升度（Lift）**:
$$Lift(X \Rightarrow Y) = \frac{confidence(X \Rightarrow Y)}{support(Y)} = \frac{P(Y|X)}{P(Y)}$$

```sql
-- 提升度计算
WITH lift_calculation AS (
    SELECT
        antecedent,
        consequent,
        confidence,
        consequent_support::NUMERIC / total_transactions AS consequent_prob,
        confidence / NULLIF(consequent_support::NUMERIC / total_transactions, 0) AS lift_value
    FROM rule_metrics
)
SELECT
    antecedent || ' => ' || consequent AS rule,
    ROUND(confidence::numeric, 4) AS confidence,
    ROUND(lift_value::numeric, 4) AS lift,
    CASE
        WHEN lift_value > 1 THEN 'Positive association'
        WHEN lift_value = 1 THEN 'Independent'
        ELSE 'Negative association'
    END AS association_type
FROM lift_calculation
ORDER BY lift DESC;
```

---

## 4. 复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| **支持度计算** | $O(nm)$ | $O(m)$ |
| **候选项生成** | $O(k^2)$ | $O(k)$ |
| **总体** | $O(2^m \times n)$ 最坏情况 | $O(2^m)$ |

其中 $n$ 是事务数，$m$ 是项数，$k$ 是频繁项集大小。

---

## 5. PostgreSQL 18 并行Apriori增强

**PostgreSQL 18** 显著增强了并行Apriori计算能力，支持并行执行支持度计算、候选项集生成和关联规则挖掘，大幅提升大规模关联规则挖掘的性能。

### 5.1 并行Apriori原理

PostgreSQL 18 的并行Apriori通过以下方式实现：

1. **并行扫描**：多个工作进程并行扫描事务数据
2. **并行支持度计算**：每个工作进程独立计算支持度
3. **并行候选项生成**：并行生成候选项集
4. **结果合并**：主进程合并所有工作进程的计算结果

### 5.2 并行支持度计算

```sql
-- PostgreSQL 18 并行支持度计算（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'transaction_data') THEN
            RAISE WARNING '表 transaction_data 不存在，无法执行并行支持度计算';
            RETURN;
        END IF;
        RAISE NOTICE '开始执行PostgreSQL 18并行支持度计算';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '并行支持度计算准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

SET max_parallel_workers_per_gather = 4;
SET parallel_setup_cost = 0;

-- 并行支持度：频繁项集识别
EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
WITH total_transactions AS (
    SELECT COUNT(DISTINCT transaction_id) AS total FROM transaction_data
),
item_support AS (
    SELECT
        item_id,
        COUNT(DISTINCT transaction_id) AS item_count,
        COUNT(DISTINCT transaction_id)::NUMERIC / (SELECT total FROM total_transactions) AS support
    FROM transaction_data
    GROUP BY item_id
)
SELECT
    item_id,
    item_count,
    ROUND(support::numeric, 4) AS support_value,
    CASE WHEN support >= 0.3 THEN 'Frequent' ELSE 'Infrequent' END AS status
FROM item_support
ORDER BY support DESC;
```

### 5.3 并行候选项集生成

```sql
-- PostgreSQL 18 并行候选项集生成（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'transaction_data') THEN
            RAISE WARNING '表 transaction_data 不存在，无法执行并行候选项集生成';
            RETURN;
        END IF;
        RAISE NOTICE '开始执行PostgreSQL 18并行候选项集生成';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '并行候选项集生成准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

SET max_parallel_workers_per_gather = 4;
SET parallel_setup_cost = 0;

-- 并行候选项集：2-项集生成
EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
WITH frequent_items AS (
    SELECT item_id FROM item_support WHERE support >= 0.3
),
candidate_pairs AS (
    SELECT
        f1.item_id AS item1,
        f2.item_id AS item2
    FROM frequent_items f1
    CROSS JOIN frequent_items f2
    WHERE f1.item_id < f2.item_id
),
pair_support AS (
    SELECT
        cp.item1,
        cp.item2,
        COUNT(DISTINCT td.transaction_id) AS pair_count,
        COUNT(DISTINCT td.transaction_id)::NUMERIC / (SELECT COUNT(DISTINCT transaction_id) FROM transaction_data) AS support
    FROM candidate_pairs cp
    JOIN transaction_data td1 ON cp.item1 = td1.item_id
    JOIN transaction_data td2 ON cp.item2 = td2.item_id AND td1.transaction_id = td2.transaction_id
    JOIN transaction_data td ON td1.transaction_id = td.transaction_id
    GROUP BY cp.item1, cp.item2
)
SELECT
    item1 || ',' || item2 AS itemset,
    pair_count,
    ROUND(support::numeric, 4) AS support_value
FROM pair_support
WHERE support >= 0.3
ORDER BY support DESC;
```

---

## 6. 实际应用案例

### 5.1 市场篮分析

```sql
-- 市场篮分析应用
WITH market_basket_rules AS (
    SELECT
        product1 || ' + ' || product2 AS product_pair,
        support_count AS co_occurrence,
        confidence AS purchase_probability,
        lift AS association_strength
    FROM association_rules
)
SELECT
    product_pair,
    co_occurrence,
    ROUND((purchase_probability * 100)::numeric, 2) AS purchase_prob_pct,
    ROUND(association_strength::numeric, 2) AS lift
FROM market_basket_rules
WHERE purchase_probability > 0.5 AND association_strength > 1.0
ORDER BY association_strength DESC;
```

---

## 📚 参考资源

1. **Agrawal, R., Srikant, R. (1994)**: "Fast algorithms for mining association rules"
2. **Han, J., Kamber, M., Pei, J. (2011)**: "Data Mining: Concepts and Techniques"

## 📊 性能优化建议

1. **支持度阈值**: 设置合理的最小支持度
2. **数据库扫描**: 减少数据库扫描次数
3. **剪枝优化**: 有效利用Apriori性质

## 🎯 最佳实践

1. **参数调优**: 调整支持度和置信度阈值
2. **规则解释**: 确保规则有业务意义
3. **验证**: 使用测试集验证规则
4. **更新**: 定期更新规则

---

**最后更新**: 2025年1月
**文档状态**: ✅ 已完成
