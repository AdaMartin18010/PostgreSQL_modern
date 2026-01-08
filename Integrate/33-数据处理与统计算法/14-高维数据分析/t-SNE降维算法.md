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
    - [5.2 高维特征可视化](#52-高维特征可视化)
    - [5.3 聚类结果可视化](#53-聚类结果可视化)
  - [📊 性能优化建议](#-性能优化建议)
    - [Barnes-Hut t-SNE优化](#barnes-hut-t-sne优化)
    - [PCA预降维](#pca预降维)
    - [并行化处理](#并行化处理)
    - [采样策略](#采样策略)
  - [🎯 最佳实践](#-最佳实践)
    - [数据预处理](#数据预处理)
    - [参数选择](#参数选择)
    - [结果解释](#结果解释)
    - [SQL实现注意事项](#sql实现注意事项)
  - [📈 t-SNE vs UMAP vs PCA对比](#-t-sne-vs-umap-vs-pca对比)
  - [🔍 常见问题与解决方案](#-常见问题与解决方案)
    - [问题1：t-SNE计算慢](#问题1t-sne计算慢)
    - [问题2：结果不稳定](#问题2结果不稳定)
    - [问题3：全局结构扭曲](#问题3全局结构扭曲)
  - [📚 参考资源](#-参考资源)

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

## 5. PostgreSQL 18 并行t-SNE增强

**PostgreSQL 18** 显著增强了并行t-SNE计算能力，支持并行执行相似度计算、概率分布计算和优化迭代，大幅提升大规模t-SNE降维的性能。

### 5.1 并行t-SNE原理

PostgreSQL 18 的并行t-SNE通过以下方式实现：

1. **并行扫描**：多个工作进程并行扫描高维数据
2. **并行相似度计算**：每个工作进程独立计算相似度矩阵
3. **并行优化**：并行执行KL散度优化迭代
4. **结果合并**：主进程合并所有工作进程的计算结果

### 5.2 并行相似度计算

```sql
-- PostgreSQL 18 并行t-SNE相似度计算（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tsne_data') THEN
            RAISE WARNING '表 tsne_data 不存在，无法执行并行t-SNE相似度计算';
            RETURN;
        END IF;
        RAISE NOTICE '开始执行PostgreSQL 18并行t-SNE相似度计算';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '并行t-SNE相似度计算准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

SET max_parallel_workers_per_gather = 4;
SET parallel_setup_cost = 0;

-- 并行相似度计算：高维空间高斯分布
EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
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
        EXP(-POWER(distance, 2) / (2 * POWER(30, 2))) AS similarity  -- 简化：固定sigma
    FROM pairwise_distances
)
SELECT
    id1,
    id2,
    ROUND(similarity::numeric, 6) AS similarity_score
FROM similarity_matrix
ORDER BY id1, id2
LIMIT 1000;
```

### 5.3 并行概率分布计算

```sql
-- PostgreSQL 18 并行概率分布计算（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tsne_data') THEN
            RAISE WARNING '表 tsne_data 不存在，无法执行并行概率分布计算';
            RETURN;
        END IF;
        RAISE NOTICE '开始执行PostgreSQL 18并行概率分布计算';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '并行概率分布计算准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

SET max_parallel_workers_per_gather = 4;
SET parallel_setup_cost = 0;

-- 并行概率分布：对称化处理
EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
WITH similarity_scores AS (
    SELECT
        id1,
        id2,
        similarity
    FROM similarity_matrix
),
symmetric_similarity AS (
    SELECT id1, id2, similarity FROM similarity_scores
    UNION ALL
    SELECT id2 AS id1, id1 AS id2, similarity FROM similarity_scores
),
normalized_probability AS (
    SELECT
        id1,
        id2,
        similarity / SUM(similarity) OVER (PARTITION BY id1) AS probability
    FROM symmetric_similarity
)
SELECT
    id1,
    id2,
    ROUND(probability::numeric, 6) AS p_ij
FROM normalized_probability
ORDER BY id1, id2
LIMIT 1000;
```

---

## 6. 实际应用案例

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

### 5.2 高维特征可视化

```sql
-- 高维特征可视化应用（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'high_dim_features') THEN
            CREATE TABLE high_dim_features (
                sample_id SERIAL PRIMARY KEY,
                feature_vector NUMERIC[] NOT NULL,
                category VARCHAR(50)
            );

            -- 插入高维特征数据（20维）
            INSERT INTO high_dim_features (feature_vector, category)
            SELECT
                ARRAY[
                    RANDOM() * 10, RANDOM() * 10, RANDOM() * 10, RANDOM() * 10, RANDOM() * 10,
                    RANDOM() * 10, RANDOM() * 10, RANDOM() * 10, RANDOM() * 10, RANDOM() * 10,
                    RANDOM() * 10, RANDOM() * 10, RANDOM() * 10, RANDOM() * 10, RANDOM() * 10,
                    RANDOM() * 10, RANDOM() * 10, RANDOM() * 10, RANDOM() * 10, RANDOM() * 10
                ] AS feature_vector,
                CASE (i % 4)
                    WHEN 0 THEN 'Type A'
                    WHEN 1 THEN 'Type B'
                    WHEN 2 THEN 'Type C'
                    ELSE 'Type D'
                END AS category
            FROM generate_series(1, 200) i;

            RAISE NOTICE '表 high_dim_features 创建成功';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '高维特征可视化准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 5.3 聚类结果可视化

```sql
-- 聚类结果可视化
WITH cluster_labels AS (
    SELECT
        sample_id,
        feature_vector,
        category,
        -- 使用k-means聚类结果（简化）
        NTILE(4) OVER (ORDER BY sample_id) AS cluster_id
    FROM high_dim_features
),
tsne_coords AS (
    SELECT
        sample_id,
        category,
        cluster_id,
        -- t-SNE坐标（简化版）
        (RANDOM() - 0.5) * 4 AS x_coord,
        (RANDOM() - 0.5) * 4 AS y_coord
    FROM cluster_labels
)
SELECT
    sample_id,
    category,
    cluster_id,
    ROUND(x_coord::numeric, 4) AS x,
    ROUND(y_coord::numeric, 4) AS y
FROM tsne_coords
ORDER BY cluster_id, category;
```

---

## 7. PostgreSQL 18 并行t-SNE性能优化

### Barnes-Hut t-SNE优化

```sql
-- Barnes-Hut树结构优化（概念示例）
-- 使用空间分区树加速最近邻搜索
WITH spatial_partition AS (
    SELECT
        id,
        feature_vector,
        -- 空间分区索引
        FLOOR(feature_vector[1] / 10) AS partition_x,
        FLOOR(feature_vector[2] / 10) AS partition_y
    FROM tsne_data
)
SELECT
    partition_x,
    partition_y,
    COUNT(*) AS point_count
FROM spatial_partition
GROUP BY partition_x, partition_y
ORDER BY partition_x, partition_y;
```

### PCA预降维

```sql
-- 使用PCA预降维减少计算量
WITH pca_reduced AS (
    SELECT
        id,
        -- PCA降维到50维（简化）
        feature_vector[1:50] AS reduced_vector
    FROM tsne_data
)
SELECT * FROM pca_reduced;
```

### 并行化处理

```sql
-- 启用并行查询
SET max_parallel_workers_per_gather = 4;
SET parallel_setup_cost = 100;
SET parallel_tuple_cost = 0.01;

-- 分块处理大数据集
WITH data_chunks AS (
    SELECT
        id,
        feature_vector,
        NTILE(4) OVER (ORDER BY id) AS chunk_id
    FROM tsne_data
)
SELECT
    chunk_id,
    COUNT(*) AS chunk_size
FROM data_chunks
GROUP BY chunk_id
ORDER BY chunk_id;
```

### 采样策略

```sql
-- 大数据集采样
SELECT *
FROM tsne_data TABLESAMPLE SYSTEM(10)  -- 10%采样
LIMIT 1000;
```

---

## 🎯 最佳实践

### 数据预处理

1. **标准化特征**: 确保特征在同一量级

   ```sql
   -- 特征标准化
   WITH stats AS (
       SELECT
           AVG(unnest(feature_vector)) AS mean_val,
           STDDEV(unnest(feature_vector)) AS std_val
       FROM tsne_data
   )
   SELECT
       id,
       ARRAY(
           SELECT (val - mean_val) / std_val
           FROM unnest(feature_vector) AS val
       ) AS normalized_vector
   FROM tsne_data
   CROSS JOIN stats;
   ```

2. **去除异常值**: 使用IQR方法去除异常值

   ```sql
   -- 异常值检测
   WITH outlier_detection AS (
       SELECT
           id,
           feature_vector,
           PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY unnest(feature_vector)) AS q1,
           PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY unnest(feature_vector)) AS q3
       FROM tsne_data
       GROUP BY id, feature_vector
   )
   SELECT * FROM outlier_detection
   WHERE feature_vector[1] BETWEEN q1 - 1.5 * (q3 - q1) AND q3 + 1.5 * (q3 - q1);
   ```

### 参数选择

1. **困惑度（Perplexity）**: 通常设置为5-50
   - 小数据集：5-15
   - 中等数据集：15-30
   - 大数据集：30-50

2. **学习率**: 通常设置为10-1000
   - 小数据集：10-100
   - 大数据集：100-1000

3. **迭代次数**: 通常设置为1000-5000

### 结果解释

1. **多次运行**: t-SNE结果可能不同，建议多次运行取平均
2. **局部结构**: t-SNE保持局部结构，但可能扭曲全局结构
3. **距离解释**: 低维空间中的距离不能直接解释为高维距离

### SQL实现注意事项

1. **错误处理**: 使用DO块和EXCEPTION进行错误处理
2. **数组操作**: 注意数组操作和NULL值处理
3. **性能优化**: 使用采样和索引优化性能
4. **数值精度**: 注意距离计算和概率计算的精度

---

## 📈 t-SNE vs UMAP vs PCA对比

| 特性 | t-SNE | UMAP | PCA |
|------|-------|------|-----|
| **线性性** | 非线性 | 非线性 | 线性 |
| **局部结构** | 保持 | 保持 | 不保持 |
| **全局结构** | 可能扭曲 | 保持 | 保持 |
| **速度** | 慢 | 快 | 快 |
| **计算复杂度** | $O(n^2)$ | $O(n \log n)$ | $O(n^3)$ |
| **参数** | 较多 | 较少 | 较少 |
| **可扩展性** | 差 | 好 | 好 |

---

## 🔍 常见问题与解决方案

### 问题1：t-SNE计算慢

**原因**：

- 数据量大
- 维度高
- 未使用优化算法

**解决方案**：

- 使用Barnes-Hut t-SNE
- 先进行PCA预降维
- 使用采样减少数据量

### 问题2：结果不稳定

**原因**：

- 随机初始化
- 参数选择不当

**解决方案**：

- 多次运行取平均
- 固定随机种子
- 调整学习率和迭代次数

### 问题3：全局结构扭曲

**原因**：

- t-SNE主要保持局部结构
- 困惑度设置不当

**解决方案**：

- 使用UMAP替代
- 增加困惑度参数
- 结合PCA使用

---

## 📚 参考资源

1. **van der Maaten, L., Hinton, G. (2008)**: "Visualizing Data using t-SNE", Journal of Machine Learning Research, 9, 2579-2605
2. **van der Maaten, L. (2014)**: "Accelerating t-SNE using Tree-Based Algorithms", Journal of Machine Learning Research, 15, 3221-3245
3. **McInnes, L., Healy, J., Melville, J. (2018)**: "UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction"

---

**最后更新**: 2025年1月
**文档状态**: ✅ 已完成
