# PostgreSQL UMAP降维算法完整指南

> **创建日期**: 2025年1月
> **技术栈**: PostgreSQL 17+/18+ | 降维 | UMAP | 流形学习
> **难度级别**: ⭐⭐⭐⭐⭐ (专家级)
> **参考标准**: UMAP (McInnes et al.), Manifold Learning, Dimensionality Reduction

---

## 📋 目录

- [PostgreSQL UMAP降维算法完整指南](#postgresql-umap降维算法完整指南)
  - [📋 目录](#-目录)
  - [UMAP概述](#umap概述)
    - [理论基础](#理论基础)
    - [核心思想](#核心思想)
    - [与t-SNE的对比](#与t-sne的对比)
  - [1. UMAP数学原理](#1-umap数学原理)
    - [1.1 流形学习](#11-流形学习)
    - [1.2 模糊集合理论](#12-模糊集合理论)
    - [1.3 交叉熵优化](#13-交叉熵优化)
  - [📚 参考资源](#-参考资源)

---

## UMAP概述

**UMAP（Uniform Manifold Approximation and Projection）**是一种基于流形学习的降维方法，比t-SNE更快且能更好地保持全局结构。

### 理论基础

UMAP基于**流形学习**和**模糊拓扑**理论，假设数据位于低维流形上。

### 核心思想

1. **流形假设**: 高维数据位于低维流形上
2. **局部结构保持**: 保持局部邻域关系
3. **全局结构保持**: 比t-SNE更好地保持全局结构

### 与t-SNE的对比

| 特性 | UMAP | t-SNE |
|------|------|-------|
| **速度** | 快 | 慢 |
| **全局结构** | 保持 | 可能扭曲 |
| **参数** | 较少 | 较多 |
| **可扩展性** | 好 | 差 |

---

## 1. UMAP数学原理

### 1.1 流形学习

**流形学习**假设数据位于低维流形上，通过局部线性近似学习流形结构。

### 1.2 模糊集合理论

**模糊拓扑**使用模糊集合理论定义邻域关系。

**高维概率**:
$$p_{j|i} = \exp\left(-\frac{d(x_i, x_j) - \rho_i}{\sigma_i}\right)$$

其中 $\rho_i$ 是到最近邻的距离，$\sigma_i$ 是归一化参数。

### 1.3 交叉熵优化

**目标函数**（交叉熵）:
$$CE(X, Y) = \sum_{i,j} p_{ij}(X) \log\left(\frac{p_{ij}(X)}{q_{ij}(Y)}\right) + (1-p_{ij}(X)) \log\left(\frac{1-p_{ij}(X)}{1-q_{ij}(Y)}\right)$$

```sql
-- UMAP数据准备（复用tsne_data表结构）
-- UMAP相似度计算
WITH pairwise_distances AS (
    SELECT
        t1.id AS id1,
        t2.id AS id2,
        SQRT(SUM(POWER(t1.feature_vector[i] - t2.feature_vector[i], 2))) AS distance
    FROM tsne_data t1
    CROSS JOIN tsne_data t2
    CROSS JOIN generate_series(1, array_length(t1.feature_vector, 1)) AS i
    WHERE t1.id < t2.id
    GROUP BY t1.id, t2.id
),
nearest_neighbor_distances AS (
    SELECT
        id1,
        MIN(distance) AS rho_i
    FROM pairwise_distances
    GROUP BY id1
),
umap_probabilities AS (
    SELECT
        pd.id1,
        pd.id2,
        pd.distance,
        nnd.rho_i,
        CASE
            WHEN pd.distance <= nnd.rho_i THEN 1.0
            ELSE EXP(-(pd.distance - nnd.rho_i) / 1.0)  -- 简化：sigma=1
        END AS p_j_given_i
    FROM pairwise_distances pd
    JOIN nearest_neighbor_distances nnd ON pd.id1 = nnd.id1
)
SELECT
    id1,
    id2,
    ROUND(p_j_given_i::numeric, 4) AS umap_similarity
FROM umap_probabilities
ORDER BY id1, id2;
```

---

## 📚 参考资源

1. **McInnes, L., Healy, J., Melville, J. (2018)**: "UMAP: Uniform Manifold Approximation and Projection"

---

**最后更新**: 2025年1月
**文档状态**: ✅ 已完成
