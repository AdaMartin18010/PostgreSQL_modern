# PostgreSQL t-SNE降维算法完整指南

> **创建日期**: 2025年1月
> **技术栈**: PostgreSQL 17+/18+ | 降维 | t-SNE | 非线性降维
> **难度级别**: ⭐⭐⭐⭐⭐ (专家级)
> **参考标准**: t-SNE (van der Maaten & Hinton), Nonlinear Dimensionality Reduction

---

## 📋 目录

- [PostgreSQL t-SNE降维算法完整指南](#postgresql-t-sne降维算法完整指南)
  - [📋 目录](#-目录)
  - [t-SNE概述](#t-sne概述)
    - [理论基础](#理论基础)
    - [核心思想](#核心思想)
    - [与PCA的区别](#与pca的区别)
  - [1. t-SNE数学原理](#1-t-sne数学原理)
    - [1.1 相似度计算](#11-相似度计算)
    - [1.2 概率分布](#12-概率分布)
    - [1.3 目标函数](#13-目标函数)
  - [2. 算法实现](#2-算法实现)
    - [2.1 高维相似度](#21-高维相似度)
  - [3. 参数调优](#3-参数调优)
    - [3.1 困惑度参数](#31-困惑度参数)
    - [3.2 学习率](#32-学习率)
  - [4. 复杂度分析](#4-复杂度分析)
  - [5. 实际应用案例](#5-实际应用案例)
    - [5.1 数据可视化](#51-数据可视化)
  - [📚 参考资源](#-参考资源)
  - [📊 性能优化建议](#-性能优化建议)
  - [🎯 最佳实践](#-最佳实践)

---

## t-SNE概述

**t-SNE（t-distributed Stochastic Neighbor Embedding）**是一种非线性降维方法，特别适合高维数据的可视化。

### 理论基础

t-SNE通过保持数据点之间的局部相似性，将高维数据映射到低维空间（通常是2D或3D）。

### 核心思想

1. **高维空间**: 使用高斯分布计算相似度
2. **低维空间**: 使用t分布计算相似度
3. **优化**: 最小化两个概率分布的KL散度

### 与PCA的区别

| 特性 | t-SNE | PCA |
|------|-------|-----|
| **线性性** | 非线性 | 线性 |
| **局部结构** | 保持 | 不保持 |
| **全局结构** | 可能扭曲 | 保持 |
| **计算复杂度** | $O(n^2)$ | $O(n^3)$ |

---

## 1. t-SNE数学原理

### 1.1 相似度计算

**高维空间相似度**（高斯分布）:
$$p_{j|i} = \frac{\exp(-||x_i - x_j||^2 / 2\sigma_i^2)}{\sum_{k \neq i} \exp(-||x_i - x_k||^2 / 2\sigma_i^2)}$$

**对称化**:
$$p_{ij} = \frac{p_{j|i} + p_{i|j}}{2n}$$

### 1.2 概率分布

**低维空间相似度**（t分布）:
$$q_{ij} = \frac{(1 + ||y_i - y_j||^2)^{-1}}{\sum_{k \neq l} (1 + ||y_k - y_l||^2)^{-1}}$$

### 1.3 目标函数

**KL散度**:
$$C = \sum_{i,j} p_{ij} \log \frac{p_{ij}}{q_{ij}}$$

```sql
-- t-SNE数据准备（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tsne_data') THEN
            RAISE WARNING '表 tsne_data 已存在，先删除';
            DROP TABLE tsne_data CASCADE;
        END IF;

        CREATE TABLE tsne_data (
            id SERIAL PRIMARY KEY,
            feature_vector NUMERIC[] NOT NULL,
            label VARCHAR(20)
        );

        -- 插入高维数据
        INSERT INTO tsne_data (feature_vector, label) VALUES
            (ARRAY[1.0, 2.0, 3.0], 'A'),
            (ARRAY[1.1, 2.1, 3.1], 'A'),
            (ARRAY[5.0, 6.0, 7.0], 'B'),
            (ARRAY[5.1, 6.1, 7.1], 'B');

        RAISE NOTICE '表 tsne_data 创建成功';
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 tsne_data 已存在';
        WHEN OTHERS THEN
            RAISE EXCEPTION '创建表失败: %', SQLERRM;
    END;
END $$;

-- 高维相似度计算（简化版）
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
similarity_matrix AS (
    SELECT
        id1,
        id2,
        EXP(-POWER(distance, 2) / 2.0) AS similarity
    FROM pairwise_distances
)
SELECT
    id1,
    id2,
    ROUND(similarity::numeric, 4) AS high_dim_similarity
FROM similarity_matrix
ORDER BY id1, id2;
```

---

## 2. 算法实现

### 2.1 高维相似度

```sql
-- 高维相似度矩阵计算
WITH distance_matrix AS (
    SELECT
        t1.id AS i,
        t2.id AS j,
        SQRT(SUM(POWER(unnest(t1.feature_vector) - unnest(t2.feature_vector), 2))) AS dist
    FROM tsne_data t1
    CROSS JOIN tsne_data t2
    WHERE t1.id != t2.id
),
perplexity_param AS (
    SELECT 30.0 AS perplexity
),
sigma_search AS (
    SELECT
        i,
        j,
        dist,
        -- 二分搜索找到合适的sigma（简化版）
        1.0 AS sigma
    FROM distance_matrix
    CROSS JOIN perplexity_param
),
conditional_prob AS (
    SELECT
        i,
        j,
        EXP(-POWER(dist, 2) / (2 * POWER(sigma, 2))) AS p_j_given_i
    FROM sigma_search
)
SELECT
    i,
    j,
    ROUND(p_j_given_i::numeric, 4) AS conditional_probability
FROM conditional_prob
ORDER BY i, j;
```

---

## 3. 参数调优

### 3.1 困惑度参数

**困惑度（Perplexity）**控制每个点的有效邻居数，通常设置为5-50。

### 3.2 学习率

**学习率**控制优化速度，通常设置为10-1000。

---

## 4. 复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| **相似度计算** | $O(n^2 d)$ | $O(n^2)$ |
| **优化** | $O(n^2 \times iterations)$ | $O(n^2)$ |
| **总体** | $O(n^2)$ | $O(n^2)$ |

其中 $n$ 是样本数，$d$ 是特征维度。

---

## 5. 实际应用案例

### 5.1 数据可视化

```sql
-- t-SNE可视化数据生成
WITH tsne_embedding AS (
    SELECT
        id,
        label,
        -- 2D嵌入坐标（简化版）
        ARRAY[embedding_x, embedding_y] AS coordinates
    FROM tsne_results
)
SELECT
    id,
    label,
    coordinates[1] AS x_coord,
    coordinates[2] AS y_coord
FROM tsne_embedding
ORDER BY label, id;
```

---

## 📚 参考资源

1. **van der Maaten, L., Hinton, G. (2008)**: "Visualizing Data using t-SNE"
2. **van der Maaten, L. (2014)**: "Accelerating t-SNE using Tree-Based Algorithms"

## 📊 性能优化建议

1. **Barnes-Hut t-SNE**: 使用树结构加速计算
2. **早期压缩**: 使用PCA预降维
3. **并行化**: 利用PostgreSQL并行处理

## 🎯 最佳实践

1. **数据预处理**: 标准化特征
2. **参数选择**: 根据数据规模选择困惑度
3. **多次运行**: t-SNE结果可能不同
4. **解释**: 注意t-SNE可能扭曲全局结构

---

**最后更新**: 2025年1月
**文档状态**: ✅ 已完成
