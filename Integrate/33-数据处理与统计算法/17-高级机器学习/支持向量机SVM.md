# PostgreSQL 支持向量机（SVM）完整指南

> **创建日期**: 2025年1月
> **技术栈**: PostgreSQL 17+/18+ | 机器学习 | 分类算法 | 最大间隔
> **难度级别**: ⭐⭐⭐⭐⭐ (专家级)
> **参考标准**: Support Vector Machines (Cortes & Vapnik), Pattern Recognition

---

## 📋 目录

- [PostgreSQL 支持向量机（SVM）完整指南](#postgresql-支持向量机svm完整指南)
  - [📋 目录](#-目录)
  - [SVM概述](#svm概述)
    - [理论基础](#理论基础)
      - [核心思想](#核心思想)
      - [几何直观](#几何直观)
    - [数学原理](#数学原理)
      - [分离超平面](#分离超平面)
      - [分类决策函数](#分类决策函数)
      - [函数间隔和几何间隔](#函数间隔和几何间隔)
    - [核心思想](#核心思想-1)
  - [1. 线性SVM](#1-线性svm)
    - [1.1 硬间隔SVM](#11-硬间隔svm)
      - [优化问题](#优化问题)
      - [数学推导](#数学推导)
      - [支持向量](#支持向量)
    - [1.2 软间隔SVM](#12-软间隔svm)
      - [优化问题](#优化问题-1)
      - [参数C的作用](#参数c的作用)
      - [松弛变量的解释](#松弛变量的解释)
      - [Hinge损失函数](#hinge损失函数)
  - [2. 非线性SVM](#2-非线性svm)
    - [2.1 核函数理论](#21-核函数理论)
      - [核函数定义](#核函数定义)
      - [Mercer定理](#mercer定理)
      - [常用核函数](#常用核函数)
    - [2.2 核技巧](#22-核技巧)
      - [优势](#优势)
      - [决策函数](#决策函数)
  - [3. 对偶问题](#3-对偶问题)
    - [3.1 拉格朗日对偶](#31-拉格朗日对偶)
      - [对偶问题](#对偶问题)
      - [KKT条件（Karush-Kuhn-Tucker Conditions）](#kkt条件karush-kuhn-tucker-conditions)
      - [支持向量的分类](#支持向量的分类)
      - [权重向量和偏置的计算](#权重向量和偏置的计算)
    - [3.2 SMO算法](#32-smo算法)
      - [算法原理](#算法原理)
      - [SMO算法步骤](#smo算法步骤)
      - [收敛条件](#收敛条件)
  - [4. 复杂度分析](#4-复杂度分析)
    - [4.1 时间复杂度](#41-时间复杂度)
    - [4.2 空间复杂度](#42-空间复杂度)
    - [4.3 优化策略](#43-优化策略)
  - [5. 实际应用案例](#5-实际应用案例)
    - [5.1 文本分类](#51-文本分类)
    - [5.2 图像识别](#52-图像识别)
    - [5.3 异常检测](#53-异常检测)
    - [5.4 客户细分](#54-客户细分)
  - [6. 算法性能对比与优化](#6-算法性能对比与优化)
    - [6.1 SVM vs 其他分类算法](#61-svm-vs-其他分类算法)
    - [6.2 性能优化建议](#62-性能优化建议)
    - [6.3 常见问题与解决方案](#63-常见问题与解决方案)
  - [7. 最佳实践](#7-最佳实践)
    - [7.1 数据预处理](#71-数据预处理)
    - [7.2 参数选择](#72-参数选择)
    - [7.3 模型评估](#73-模型评估)
    - [7.4 SQL实现注意事项](#74-sql实现注意事项)
  - [📚 参考资源](#-参考资源)
    - [学术文献](#学术文献)
    - [在线资源](#在线资源)
    - [相关算法](#相关算法)

---

## SVM概述

**支持向量机（Support Vector Machine, SVM）**是一种强大的监督学习算法，由Vapnik和Cortes在1995年提出。SVM通过寻找最大间隔超平面来进行分类，在文本分类、图像识别、生物信息学等领域有广泛应用。

### 理论基础

#### 核心思想

SVM的核心思想是找到一个**最优分离超平面（Optimal Separating Hyperplane）**，使得两类样本之间的间隔（Margin）最大。

**关键概念**：

- **分离超平面**：能够将两类样本分开的决策边界
- **间隔**：超平面到最近样本点的距离
- **支持向量**：距离超平面最近的样本点，决定超平面的位置
- **最大间隔**：最大化间隔可以提高分类器的泛化能力

#### 几何直观

- 在二维空间中，分离超平面是一条直线
- 在三维空间中，分离超平面是一个平面
- 在高维空间中，分离超平面是一个超平面

**间隔最大化原理**：选择使两类样本到超平面距离最大的超平面，这样的超平面具有最好的泛化能力。

### 数学原理

给定训练样本集 $\{(x_i, y_i)\}_{i=1}^{n}$，其中：

- $x_i \in \mathbb{R}^d$ 是 $d$ 维特征向量
- $y_i \in \{-1, +1\}$ 是类别标签

#### 分离超平面

**超平面方程**：
$$w^T x + b = 0$$

其中：

- $w \in \mathbb{R}^d$ 是法向量（权重向量）
- $b \in \mathbb{R}$ 是偏置项

#### 分类决策函数

**决策函数**：
$$f(x) = \text{sign}(w^T x + b)$$

- 如果 $f(x) > 0$，预测为正类（$y = +1$）
- 如果 $f(x) < 0$，预测为负类（$y = -1$）

#### 函数间隔和几何间隔

**函数间隔（Functional Margin）**：
$$\hat{\gamma}_i = y_i(w^T x_i + b)$$

**几何间隔（Geometric Margin）**：
$$\gamma_i = \frac{y_i(w^T x_i + b)}{||w||} = \frac{\hat{\gamma}_i}{||w||}$$

**最小间隔**：
$$\gamma = \min_{i=1,...,n} \gamma_i$$

### 核心思想

1. **最大间隔原理**：最大化两类样本之间的几何间隔
2. **支持向量**：只有支持向量影响超平面的位置，其他样本点不影响
3. **核技巧**：通过核函数将非线性问题映射到高维空间，使其线性可分
4. **对偶问题**：通过拉格朗日对偶将原始优化问题转化为对偶问题，便于求解

---

## 1. 线性SVM

### 1.1 硬间隔SVM

**硬间隔SVM（Hard-Margin SVM）**假设数据线性可分，即存在超平面能够完美分离两类样本。

#### 优化问题

**原始优化问题（Primal Problem）**：
$$\min_{w,b} \frac{1}{2}||w||^2$$

**约束条件**：
$$y_i(w^T x_i + b) \geq 1, \quad i = 1, ..., n$$

#### 数学推导

**目标**：最大化几何间隔 $\gamma = \frac{1}{||w||}$

等价于最小化 $||w||$，进一步等价于最小化 $\frac{1}{2}||w||^2$（便于求导）。

**约束条件解释**：

- 约束 $y_i(w^T x_i + b) \geq 1$ 确保所有样本点距离超平面至少为 $\frac{1}{||w||}$
- 通过缩放 $w$ 和 $b$，可以将函数间隔标准化为1

**间隔计算**：

- 两类样本之间的间隔为 $\frac{2}{||w||}$
- 最大化间隔等价于最小化 $||w||$

#### 支持向量

**支持向量（Support Vectors）**是满足 $y_i(w^T x_i + b) = 1$ 的样本点，即位于间隔边界上的点。

**性质**：

- 支持向量决定超平面的位置
- 删除非支持向量不影响分类结果
- 支持向量数量通常远小于样本总数

```sql
-- 线性SVM实现（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'svm_training_data') THEN
            RAISE WARNING '表 svm_training_data 已存在，先删除';
            DROP TABLE svm_training_data CASCADE;
        END IF;

        CREATE TABLE svm_training_data (
            id SERIAL PRIMARY KEY,
            feature1 NUMERIC NOT NULL,
            feature2 NUMERIC NOT NULL,
            label INTEGER NOT NULL CHECK (label IN (-1, 1))
        );

        -- 插入线性可分数据
        INSERT INTO svm_training_data (feature1, feature2, label) VALUES
            -- 类别+1
            (1, 1, 1), (2, 2, 1), (1, 2, 1),
            -- 类别-1
            (4, 4, -1), (5, 5, -1), (4, 5, -1);

        RAISE NOTICE '表 svm_training_data 创建成功';
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 svm_training_data 已存在';
        WHEN OTHERS THEN
            RAISE EXCEPTION '创建表失败: %', SQLERRM;
    END;
END $$;

-- SVM分类决策（简化版：使用线性分类器）
WITH class_centroids AS (
    SELECT
        label,
        AVG(feature1) AS centroid_f1,
        AVG(feature2) AS centroid_f2
    FROM svm_training_data
    GROUP BY label
),
decision_boundary AS (
    SELECT
        (c1.centroid_f1 + c2.centroid_f1) / 2.0 AS boundary_f1,
        (c1.centroid_f2 + c2.centroid_f2) / 2.0 AS boundary_f2
    FROM class_centroids c1
    CROSS JOIN class_centroids c2
    WHERE c1.label = 1 AND c2.label = -1
)
SELECT
    td.id,
    td.feature1,
    td.feature2,
    td.label,
    CASE
        WHEN td.feature1 + td.feature2 > (SELECT boundary_f1 + boundary_f2 FROM decision_boundary) THEN 1
        ELSE -1
    END AS predicted_label
FROM svm_training_data td;

-- 性能测试
EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
SELECT
    label,
    AVG(feature1) AS mean_f1,
    AVG(feature2) AS mean_f2
FROM svm_training_data
GROUP BY label;
```

### 1.2 软间隔SVM

**软间隔SVM（Soft-Margin SVM）**允许分类错误，适用于数据不完全线性可分的情况。

#### 优化问题

**原始优化问题**：
$$\min_{w,b,\xi} \frac{1}{2}||w||^2 + C\sum_{i=1}^{n}\xi_i$$

**约束条件**：
$$y_i(w^T x_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0, \quad i = 1, ..., n$$

其中：

- $\xi_i$ 是松弛变量（Slack Variable），表示第 $i$ 个样本的违反程度
- $C > 0$ 是惩罚参数（Penalty Parameter），控制对误分类的惩罚程度

#### 参数C的作用

- **$C$ 很大**：对误分类惩罚大，倾向于硬间隔（可能过拟合）
- **$C$ 很小**：对误分类惩罚小，允许更多误分类（可能欠拟合）
- **$C$ 的选择**：通常通过交叉验证确定

#### 松弛变量的解释

- $\xi_i = 0$：样本正确分类且在间隔边界外
- $0 < \xi_i < 1$：样本正确分类但在间隔内
- $\xi_i = 1$：样本在超平面上
- $\xi_i > 1$：样本被误分类

#### Hinge损失函数

软间隔SVM等价于最小化Hinge损失：
$$L(y, f(x)) = \max(0, 1 - y \cdot f(x))$$

其中 $f(x) = w^T x + b$。

```sql
-- 软间隔SVM（简化版：展示松弛变量概念）
WITH misclassified_samples AS (
    SELECT
        id,
        feature1,
        feature2,
        label,
        CASE
            WHEN label = 1 AND feature1 + feature2 < 3 THEN 1
            WHEN label = -1 AND feature1 + feature2 > 3 THEN 1
            ELSE 0
        END AS slack_variable
    FROM svm_training_data
)
SELECT
    id,
    label,
    slack_variable,
    CASE
        WHEN slack_variable > 0 THEN 'Misclassified'
        ELSE 'Correctly classified'
    END AS classification_status
FROM misclassified_samples;
```

---

## 2. 非线性SVM

### 2.1 核函数理论

**核函数（Kernel Function）**将数据从原始空间映射到高维特征空间，使非线性问题在高维空间中变为线性问题。

#### 核函数定义

**核函数** $K: \mathcal{X} \times \mathcal{X} \to \mathbb{R}$ 满足：
$$K(x_i, x_j) = \langle \phi(x_i), \phi(x_j) \rangle$$

其中 $\phi: \mathcal{X} \to \mathcal{H}$ 是特征映射，$\mathcal{H}$ 是高维特征空间（可能是无限维）。

#### Mercer定理

**Mercer条件**：核函数 $K$ 是有效核函数的充要条件是，对于任意有限样本集，对应的Gram矩阵是半正定的。

#### 常用核函数

1. **线性核（Linear Kernel）**：
   $$K(x_i, x_j) = x_i^T x_j$$
   - 参数：无
   - 适用：线性可分数据

2. **多项式核（Polynomial Kernel）**：
   $$K(x_i, x_j) = (x_i^T x_j + c)^d$$
   - 参数：$d$（次数）、$c$（常数项）
   - 适用：多项式关系的数据

3. **RBF核（Radial Basis Function Kernel，高斯核）**：
   $$K(x_i, x_j) = \exp(-\gamma ||x_i - x_j||^2)$$
   - 参数：$\gamma > 0$（带宽参数）
   - 适用：非线性数据，通用性强
   - 性质：$\gamma$ 越大，决策边界越复杂（可能过拟合）

4. **Sigmoid核**：
   $$K(x_i, x_j) = \tanh(\alpha x_i^T x_j + \beta)$$
   - 参数：$\alpha$（斜率）、$\beta$（截距）
   - 适用：神经网络风格的分类

### 2.2 核技巧

**核技巧（Kernel Trick）**的核心思想：避免显式计算高维映射 $\phi(x)$，直接计算核函数值 $K(x_i, x_j)$。

#### 优势

1. **计算效率**：避免高维空间的计算，复杂度从 $O(d')$ 降低到 $O(d)$（$d' \gg d$）
2. **无限维空间**：可以处理无限维特征空间（如RBF核）
3. **灵活性**：只需要定义核函数，不需要知道具体的映射函数

#### 决策函数

使用核函数后，决策函数变为：
$$f(x) = \sum_{i=1}^{n} \alpha_i y_i K(x_i, x) + b$$

其中 $\alpha_i$ 是拉格朗日乘数（对偶变量）。

```sql
-- RBF核函数计算
WITH kernel_matrix AS (
    SELECT
        t1.id AS id1,
        t2.id AS id2,
        t1.feature1 AS f1_1,
        t1.feature2 AS f2_1,
        t2.feature1 AS f1_2,
        t2.feature2 AS f2_2,
        1.0 AS gamma  -- RBF参数
    FROM svm_training_data t1
    CROSS JOIN svm_training_data t2
),
rbf_kernel AS (
    SELECT
        id1,
        id2,
        EXP(-gamma * (
            POWER(f1_1 - f1_2, 2) + POWER(f2_1 - f2_2, 2)
        )) AS kernel_value
    FROM kernel_matrix
)
SELECT
    id1,
    id2,
    ROUND(kernel_value::numeric, 4) AS rbf_kernel_value
FROM rbf_kernel
WHERE id1 <= id2
ORDER BY id1, id2;
```

---

## 3. 对偶问题

### 3.1 拉格朗日对偶

**拉格朗日函数**（软间隔SVM）：

$$L(w, b, \xi, \alpha, \mu) = \frac{1}{2}||w||^2 + C\sum_{i=1}^{n}\xi_i - \sum_{i=1}^{n}\alpha_i[y_i(w^T x_i + b) - 1 + \xi_i] - \sum_{i=1}^{n}\mu_i \xi_i$$

其中 $\alpha_i \geq 0$ 和 $\mu_i \geq 0$ 是拉格朗日乘数。

#### 对偶问题

**对偶优化问题（Dual Problem）**：

$$\max_{\alpha} \sum_{i=1}^{n}\alpha_i - \frac{1}{2}\sum_{i,j=1}^{n}\alpha_i \alpha_j y_i y_j K(x_i, x_j)$$

**约束条件**：
$$\sum_{i=1}^{n}\alpha_i y_i = 0$$
$$0 \leq \alpha_i \leq C, \quad i = 1, ..., n$$

#### KKT条件（Karush-Kuhn-Tucker Conditions）

**KKT条件**是优化问题的最优性条件：

1. **原始可行性**：
   - $y_i(w^T x_i + b) \geq 1 - \xi_i$
   - $\xi_i \geq 0$

2. **对偶可行性**：
   - $\alpha_i \geq 0$
   - $\mu_i \geq 0$

3. **互补松弛性**：
   - $\alpha_i[y_i(w^T x_i + b) - 1 + \xi_i] = 0$
   - $\mu_i \xi_i = 0$

#### 支持向量的分类

根据KKT条件，样本点可以分为三类：

- **$\alpha_i = 0$**：样本不在边界上，对分类无影响（非支持向量）
- **$0 < \alpha_i < C$**：样本在间隔边界上，$y_i(w^T x_i + b) = 1$（支持向量）
- **$\alpha_i = C$**：样本在间隔内或误分类，$\xi_i > 0$（边界支持向量或误分类样本）

#### 权重向量和偏置的计算

**权重向量**：
$$w = \sum_{i=1}^{n} \alpha_i y_i x_i$$

**偏置**（使用支持向量计算）：
$$b = \frac{1}{|S|} \sum_{s \in S} \left(y_s - \sum_{i=1}^{n} \alpha_i y_i K(x_i, x_s)\right)$$

其中 $S$ 是支持向量集合。

### 3.2 SMO算法

**SMO（Sequential Minimal Optimization）**算法由Platt在1998年提出，是求解SVM对偶问题的高效算法。

#### 算法原理

**核心思想**：将对偶问题分解为一系列子问题，每次优化两个拉格朗日乘数 $\alpha_i$ 和 $\alpha_j$。

**为什么选择两个**：

- 由于约束 $\sum_{i=1}^{n}\alpha_i y_i = 0$，至少需要两个变量才能保持约束
- 两个变量的优化问题有解析解，计算效率高

#### SMO算法步骤

1. **选择两个乘数** $\alpha_i$ 和 $\alpha_j$：
   - 使用启发式方法选择违反KKT条件最严重的样本对

2. **优化这两个乘数**：
   - 固定其他乘数，只优化 $\alpha_i$ 和 $\alpha_j$
   - 有解析解，可以直接计算

3. **更新阈值** $b$：
   - 根据新的乘数值更新偏置

4. **重复**：直到收敛或达到最大迭代次数

#### 收敛条件

- 所有样本满足KKT条件（在容差范围内）
- 目标函数不再显著增加
- 达到最大迭代次数

```sql
-- SMO算法简化实现（展示迭代过程）
WITH svm_parameters AS (
    SELECT
        id,
        feature1,
        feature2,
        label,
        0.0 AS alpha,  -- 拉格朗日乘数
        0.0 AS error    -- 预测误差
    FROM svm_training_data
),
smo_iteration AS (
    SELECT
        -- SMO迭代更新（简化版）
        id,
        alpha,
        CASE
            WHEN error * label < -1 THEN LEAST(alpha + 1.0, 1.0)
            WHEN error * label > 1 THEN GREATEST(alpha - 1.0, 0.0)
            ELSE alpha
        END AS updated_alpha
    FROM svm_parameters
)
SELECT
    id,
    ROUND(alpha::numeric, 4) AS old_alpha,
    ROUND(updated_alpha::numeric, 4) AS new_alpha,
    CASE
        WHEN updated_alpha > 0 THEN 'Support Vector'
        ELSE 'Non-support Vector'
    END AS vector_type
FROM smo_iteration;
```

---

## 4. 复杂度分析

### 4.1 时间复杂度

| 算法 | 时间复杂度 | 说明 |
|------|-----------|------|
| **线性SVM（原始问题）** | $O(n^2 \cdot d)$ | $n$是样本数，$d$是特征数 |
| **非线性SVM（对偶问题）** | $O(n^2 \sim n^3)$ | 取决于核矩阵计算 |
| **SMO算法** | $O(n^2 \cdot d)$ | 实际中通常更快 |
| **预测** | $O(s \cdot d)$ | $s$是支持向量数 |

### 4.2 空间复杂度

| 算法 | 空间复杂度 | 说明 |
|------|-----------|------|
| **线性SVM** | $O(n \cdot d)$ | 存储训练数据 |
| **非线性SVM** | $O(n^2)$ | 存储核矩阵 |
| **SMO算法** | $O(n)$ | 只存储支持向量 |

### 4.3 优化策略

1. **增量学习**：使用增量SVM处理流式数据
2. **近似方法**：使用Nyström方法近似核矩阵
3. **并行计算**：并行计算核矩阵和SMO迭代
4. **特征选择**：减少特征维度降低计算复杂度
5. **缓存优化**：缓存频繁使用的核函数值

---

## 5. 实际应用案例

### 5.1 文本分类

**场景**：使用SVM对新闻文章进行分类（政治、体育、科技等）。

```sql
-- 文本分类：使用SVM进行文档分类
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'document_features') THEN
            CREATE TABLE document_features (
                document_id INTEGER PRIMARY KEY,
                feature_id INTEGER NOT NULL,
                feature_value NUMERIC NOT NULL,  -- TF-IDF值
                category_label INTEGER NOT NULL CHECK (category_label IN (-1, 1))
            );
            -- 插入示例数据：100个文档，每个50维特征
            INSERT INTO document_features (document_id, feature_id, feature_value, category_label)
            SELECT
                doc_id,
                feat_id,
                (RANDOM() * 0.5 + CASE WHEN category_label = 1 THEN 0.3 ELSE 0.0 END)::NUMERIC AS feature_value,
                category_label
            FROM generate_series(1, 100) AS doc_id
            CROSS JOIN generate_series(1, 50) AS feat_id
            CROSS JOIN (SELECT CASE WHEN doc_id <= 50 THEN 1 ELSE -1 END AS category_label FROM generate_series(1, 100) AS doc_id) AS cat;
        END IF;
        RAISE NOTICE '开始文本分类SVM';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '文本分类准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 文本分类：计算文档特征向量和类别
WITH document_vectors AS (
    SELECT
        document_id,
        category_label,
        ARRAY_AGG(feature_value ORDER BY feature_id) AS feature_vector
    FROM document_features
    GROUP BY document_id, category_label
),
-- 计算类别中心（简化：使用类别中心作为分类基准）
class_centroids AS (
    SELECT
        category_label,
        ARRAY_AGG(avg_feature ORDER BY feature_id) AS centroid_vector
    FROM (
        SELECT
            category_label,
            feature_id,
            AVG(feature_value) AS avg_feature
        FROM document_features
        GROUP BY category_label, feature_id
    ) AS avg_features
    GROUP BY category_label
),
-- 使用RBF核计算相似度进行分类
svm_classification AS (
    SELECT
        dv.document_id,
        dv.category_label AS true_label,
        dv.feature_vector,
        -- 计算与两个类别中心的RBF核值
        EXP(-1.0 * (
            SELECT SUM(POWER(dv.feature_vector[i] - cc1.centroid_vector[i], 2))
            FROM generate_series(1, array_length(dv.feature_vector, 1)) AS i
        )) AS kernel_class1,
        EXP(-1.0 * (
            SELECT SUM(POWER(dv.feature_vector[i] - cc2.centroid_vector[i], 2))
            FROM generate_series(1, array_length(dv.feature_vector, 1)) AS i
        )) AS kernel_class2
    FROM document_vectors dv
    CROSS JOIN class_centroids cc1
    CROSS JOIN class_centroids cc2
    WHERE cc1.category_label = 1 AND cc2.category_label = -1
),
predictions AS (
    SELECT
        document_id,
        true_label,
        CASE
            WHEN kernel_class1 > kernel_class2 THEN 1
            ELSE -1
        END AS predicted_label
    FROM svm_classification
)
SELECT
    true_label,
    predicted_label,
    COUNT(*) AS count,
    CASE
        WHEN true_label = predicted_label THEN 'Correct'
        ELSE 'Incorrect'
    END AS classification_result
FROM predictions
GROUP BY true_label, predicted_label
ORDER BY true_label, predicted_label;
```

### 5.2 图像识别

**场景**：使用SVM进行图像分类（猫、狗、鸟等）。

```sql
-- 图像识别：使用SVM进行物体分类
WITH image_features AS (
    SELECT
        image_id,
        object_class,
        -- 特征提取：颜色直方图、纹理特征等（简化：使用随机特征）
        ARRAY[
            AVG(red_value), AVG(green_value), AVG(blue_value),
            STDDEV(red_value), STDDEV(green_value), STDDEV(blue_value)
        ] AS feature_vector
    FROM image_pixels
    GROUP BY image_id, object_class
),
-- 计算类别中心
class_centers AS (
    SELECT
        object_class,
        ARRAY_AGG(avg_feat ORDER BY feat_idx) AS class_center
    FROM (
        SELECT
            object_class,
            feat_idx,
            AVG(feature_vector[feat_idx]) AS avg_feat
        FROM image_features
        CROSS JOIN generate_series(1, 6) AS feat_idx
        GROUP BY object_class, feat_idx
    ) AS avg_features
    GROUP BY object_class
),
-- SVM分类：使用RBF核
svm_predictions AS (
    SELECT
        if.image_id,
        if.object_class AS true_class,
        cc.object_class AS predicted_class,
        EXP(-1.0 * (
            SELECT SUM(POWER(if.feature_vector[i] - cc.class_center[i], 2))
            FROM generate_series(1, 6) AS i
        )) AS kernel_value
    FROM image_features if
    CROSS JOIN class_centers cc
),
best_predictions AS (
    SELECT DISTINCT ON (image_id)
        image_id,
        true_class,
        predicted_class,
        kernel_value
    FROM svm_predictions
    ORDER BY image_id, kernel_value DESC
)
SELECT
    true_class,
    predicted_class,
    COUNT(*) AS count,
    ROUND(COUNT(*) FILTER (WHERE true_class = predicted_class)::NUMERIC / COUNT(*) * 100, 2) AS accuracy_pct
FROM best_predictions
GROUP BY true_class, predicted_class
ORDER BY true_class, predicted_class;
```

### 5.3 异常检测

**场景**：使用One-Class SVM进行异常检测。

```sql
-- 异常检测：One-Class SVM
WITH normal_data AS (
    SELECT
        feature1,
        feature2,
        feature3
    FROM sensor_data
    WHERE is_anomaly = FALSE
),
data_center AS (
    SELECT
        AVG(feature1) AS center_f1,
        AVG(feature2) AS center_f2,
        AVG(feature3) AS center_f3,
        STDDEV(feature1) AS std_f1,
        STDDEV(feature2) AS std_f2,
        STDDEV(feature3) AS std_f3
    FROM normal_data
),
anomaly_detection AS (
    SELECT
        sd.id,
        sd.feature1,
        sd.feature2,
        sd.feature3,
        -- 计算到数据中心的距离（使用RBF核的逆）
        SQRT(
            POWER((sd.feature1 - dc.center_f1) / NULLIF(dc.std_f1, 0), 2) +
            POWER((sd.feature2 - dc.center_f2) / NULLIF(dc.std_f2, 0), 2) +
            POWER((sd.feature3 - dc.center_f3) / NULLIF(dc.std_f3, 0), 2)
        ) AS distance_to_center
    FROM sensor_data sd
    CROSS JOIN data_center dc
),
threshold AS (
    SELECT
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY distance_to_center) AS anomaly_threshold
    FROM anomaly_detection
    WHERE id IN (SELECT id FROM normal_data)
)
SELECT
    ad.id,
    ROUND(ad.distance_to_center::numeric, 4) AS distance,
    ROUND(t.anomaly_threshold::numeric, 4) AS threshold,
    CASE
        WHEN ad.distance_to_center > t.anomaly_threshold THEN '异常'
        ELSE '正常'
    END AS anomaly_status
FROM anomaly_detection ad
CROSS JOIN threshold t
ORDER BY ad.distance_to_center DESC;
```

### 5.4 客户细分

**场景**：使用SVM进行客户分类（高价值客户 vs 低价值客户）。

```sql
-- 客户细分：使用SVM进行二分类
WITH customer_features AS (
    SELECT
        customer_id,
        total_purchase_amount,
        purchase_frequency,
        avg_order_value,
        days_since_last_purchase,
        CASE
            WHEN total_purchase_amount > 10000 THEN 1
            ELSE -1
        END AS customer_segment
    FROM customer_data
),
normalized_features AS (
    SELECT
        customer_id,
        customer_segment,
        (total_purchase_amount - AVG(total_purchase_amount) OVER ()) / NULLIF(STDDEV(total_purchase_amount) OVER (), 0) AS norm_amount,
        (purchase_frequency - AVG(purchase_frequency) OVER ()) / NULLIF(STDDEV(purchase_frequency) OVER (), 0) AS norm_frequency,
        (avg_order_value - AVG(avg_order_value) OVER ()) / NULLIF(STDDEV(avg_order_value) OVER (), 0) AS norm_avg_value
    FROM customer_features
),
segment_centers AS (
    SELECT
        customer_segment,
        AVG(norm_amount) AS center_amount,
        AVG(norm_frequency) AS center_frequency,
        AVG(norm_avg_value) AS center_avg_value
    FROM normalized_features
    GROUP BY customer_segment
),
svm_classification AS (
    SELECT
        nf.customer_id,
        nf.customer_segment AS true_segment,
        sc.customer_segment AS predicted_segment,
        EXP(-1.0 * (
            POWER(nf.norm_amount - sc.center_amount, 2) +
            POWER(nf.norm_frequency - sc.center_frequency, 2) +
            POWER(nf.norm_avg_value - sc.center_avg_value, 2)
        )) AS kernel_value
    FROM normalized_features nf
    CROSS JOIN segment_centers sc
),
best_predictions AS (
    SELECT DISTINCT ON (customer_id)
        customer_id,
        true_segment,
        predicted_segment
    FROM svm_classification
    ORDER BY customer_id, kernel_value DESC
)
SELECT
    true_segment,
    predicted_segment,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) FILTER (WHERE true_segment = predicted_segment)::NUMERIC / COUNT(*) * 100, 2) AS accuracy_pct
FROM best_predictions
GROUP BY true_segment, predicted_segment
ORDER BY true_segment, predicted_segment;
```

---

## 6. 算法性能对比与优化

### 6.1 SVM vs 其他分类算法

| 算法 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **SVM** | 泛化能力强、支持高维数据、核技巧处理非线性 | 大规模数据慢、参数敏感 | 中小规模数据、高维数据 |
| **逻辑回归** | 简单快速、可解释性强 | 需要线性可分 | 线性分类、大规模数据 |
| **决策树** | 可解释、处理非线性 | 容易过拟合 | 特征重要性分析 |
| **随机森林** | 准确率高、抗过拟合 | 可解释性差 | 大规模数据 |
| **神经网络** | 表达能力强 | 需要大量数据、调参复杂 | 大规模数据、深度学习 |

### 6.2 性能优化建议

1. **核函数选择**：
   - 线性数据：使用线性核
   - 非线性数据：使用RBF核（通用选择）
   - 文本数据：使用线性核或多项式核

2. **参数调优**：
   - **网格搜索**：系统搜索参数空间
   - **交叉验证**：使用k折交叉验证评估参数
   - **贝叶斯优化**：更高效的参数搜索方法

3. **特征缩放**：
   - 标准化特征（Z-score标准化）
   - 归一化特征（Min-Max标准化）
   - 提高SVM的数值稳定性

4. **大规模数据**：
   - 使用线性SVM（Liblinear）
   - 采样策略：随机采样或分层采样
   - 增量学习：在线SVM

### 6.3 常见问题与解决方案

**问题1**：训练时间过长

- **解决方案**：使用线性SVM、减少特征数、使用采样

**问题2**：过拟合

- **解决方案**：减小$C$值、增加正则化、使用更多数据

**问题3**：欠拟合

- **解决方案**：增大$C$值、选择更复杂的核函数、增加特征

**问题4**：支持向量过多

- **解决方案**：减小$C$值、使用更简单的核函数、检查数据质量

---

## 7. 最佳实践

### 7.1 数据预处理

1. **特征标准化**：
   - 使用Z-score标准化：$z = \frac{x - \mu}{\sigma}$
   - 确保所有特征在相同量级

2. **缺失值处理**：
   - 删除缺失值过多的样本
   - 使用均值/中位数填充
   - 使用插值方法

3. **异常值处理**：
   - 使用IQR方法识别异常值
   - 删除或修正异常值
   - 使用Robust Scaling

### 7.2 参数选择

1. **C参数**：
   - 默认值：$C = 1$
   - 搜索范围：$[10^{-3}, 10^{3}]$（对数尺度）
   - 大$C$：硬间隔，可能过拟合
   - 小$C$：软间隔，可能欠拟合

2. **RBF核参数$\gamma$**：
   - 默认值：$\gamma = \frac{1}{d}$（$d$是特征数）
   - 搜索范围：$[10^{-5}, 10^{2}]$（对数尺度）
   - 大$\gamma$：复杂决策边界，可能过拟合
   - 小$\gamma$：简单决策边界，可能欠拟合

3. **网格搜索**：
   - 使用交叉验证评估参数组合
   - 选择验证集上性能最好的参数

### 7.3 模型评估

1. **交叉验证**：
   - 使用k折交叉验证（通常$k=5$或$k=10$）
   - 评估模型的泛化能力

2. **评估指标**：
   - **准确率（Accuracy）**：整体分类正确率
   - **精确率（Precision）**：正类预测的准确性
   - **召回率（Recall）**：正类识别的完整性
   - **F1分数**：精确率和召回率的调和平均
   - **ROC-AUC**：ROC曲线下面积

3. **支持向量分析**：
   - 检查支持向量的数量（应该远小于样本数）
   - 分析支持向量的分布
   - 识别可能的异常值

### 7.4 SQL实现注意事项

1. **核矩阵计算**：
   - 对于大规模数据，核矩阵可能非常大
   - 考虑使用近似方法或采样

2. **数值稳定性**：
   - 使用NUMERIC类型保持精度
   - 注意指数运算的溢出问题

3. **扩展函数**：
   - 考虑使用PL/Python调用scikit-learn
   - 或使用PostgreSQL扩展（如MADlib）

4. **性能优化**：
   - 创建特征索引加速查询
   - 使用物化视图缓存中间结果
   - 并行处理大规模数据

---

## 📚 参考资源

### 学术文献

1. **Cortes, C., Vapnik, V. (1995)**: "Support-vector networks", *Machine Learning*, 20(3), 273-297.

2. **Vapnik, V.N. (1998)**: "Statistical Learning Theory", Wiley.

3. **Schölkopf, B., Smola, A.J. (2002)**: "Learning with Kernels: Support Vector Machines, Regularization, Optimization, and Beyond", MIT Press.

4. **Platt, J. (1998)**: "Sequential Minimal Optimization: A Fast Algorithm for Training Support Vector Machines", Microsoft Research Technical Report.

5. **Bishop, C.M. (2006)**: "Pattern Recognition and Machine Learning", Springer.

6. **《统计学习方法》**（李航，2012）- 第7章 支持向量机

### 在线资源

- **scikit-learn SVM文档**: <https://scikit-learn.org/stable/modules/svm.html>
- **LIBSVM**: <https://www.csie.ntu.edu.tw/~cjlin/libsvm/>
- **PostgreSQL MADlib扩展**: <https://madlib.apache.org/>
- **SVM可视化**: <https://www.csie.ntu.edu.tw/~cjlin/libsvm/>

### 相关算法

- **逻辑回归**：线性分类的替代方法
- **感知机**：SVM的前身
- **核方法**：核PCA、核岭回归
- **结构化SVM**：处理结构化输出
- **多类SVM**：一对多、一对一方法

---

**最后更新**: 2025年1月
**文档状态**: ✅ 已完成
