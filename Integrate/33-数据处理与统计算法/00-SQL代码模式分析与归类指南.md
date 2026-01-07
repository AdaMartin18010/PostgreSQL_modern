# PostgreSQL SQL代码模式分析与归类完整指南

> **创建日期**: 2025年1月
> **用途**: 全面分析、归类、示例和结合应用的SQL代码模式
> **状态**: 🔄 持续建设中
> **参考标准**: ACM CCS、IEEE分类、SQL标准、PostgreSQL官方文档

---

## 📋 目录

- [PostgreSQL SQL代码模式分析与归类完整指南](#postgresql-sql代码模式分析与归类完整指南)
  - [📋 目录](#-目录)
  - [1. SQL代码模式分类体系](#1-sql代码模式分类体系)
    - [1.1 分类依据](#11-分类依据)
    - [1.2 分类维度](#12-分类维度)
  - [2. 数学与计算类SQL模式](#2-数学与计算类sql模式)
    - [2.1 基础数学运算模式](#21-基础数学运算模式)
    - [2.2 高级数学计算模式](#22-高级数学计算模式)
    - [2.3 数值精度处理模式](#23-数值精度处理模式)
  - [3. 数据统计与分析类SQL模式](#3-数据统计与分析类sql模式)
    - [3.1 描述性统计模式](#31-描述性统计模式)
    - [3.2 聚合统计分析模式](#32-聚合统计分析模式)
    - [3.3 窗口函数统计模式](#33-窗口函数统计模式)
  - [4. 数据处理算法类SQL模式](#4-数据处理算法类sql模式)
    - [4.1 排序算法模式](#41-排序算法模式)
    - [4.2 搜索算法模式](#42-搜索算法模式)
    - [4.3 去重算法模式](#43-去重算法模式)
  - [5. 数据挖掘类SQL模式](#5-数据挖掘类sql模式)
    - [5.1 关联规则挖掘模式](#51-关联规则挖掘模式)
    - [5.2 聚类分析模式](#52-聚类分析模式)
  - [6. 时间序列处理类SQL模式](#6-时间序列处理类sql模式)
    - [6.1 时间序列聚合模式](#61-时间序列聚合模式)
    - [6.2 滑动窗口计算模式](#62-滑动窗口计算模式)
  - [7. 文本处理类SQL模式](#7-文本处理类sql模式)
    - [7.1 文本搜索模式](#71-文本搜索模式)
    - [7.2 文本相似度计算模式](#72-文本相似度计算模式)
  - [8. 图算法类SQL模式](#8-图算法类sql模式)
    - [8.1 图遍历模式](#81-图遍历模式)
    - [8.2 最短路径算法模式](#82-最短路径算法模式)
  - [9. 机器学习类SQL模式](#9-机器学习类sql模式)
    - [9.1 线性回归模式](#91-线性回归模式)
  - [10. 金融统计类SQL模式](#10-金融统计类sql模式)
    - [10.1 收益率计算模式](#101-收益率计算模式)
  - [11. 运维运营类SQL模式](#11-运维运营类sql模式)
    - [11.1 性能指标计算模式](#111-性能指标计算模式)
    - [11.2 异常检测算法模式](#112-异常检测算法模式)
  - [12. 数据库算法类SQL模式](#12-数据库算法类sql模式)
    - [12.1 索引优化模式](#121-索引优化模式)
  - [13. 数据质量类SQL模式](#13-数据质量类sql模式)
    - [13.1 数据清洗算法模式](#131-数据清洗算法模式)
  - [14. 综合应用模式](#14-综合应用模式)
    - [14.1 电商数据分析模式](#141-电商数据分析模式)
  - [15. 代码模式最佳实践](#15-代码模式最佳实践)
    - [15.1 错误处理模式](#151-错误处理模式)
    - [15.2 性能优化模式](#152-性能优化模式)
    - [15.3 代码可读性模式](#153-代码可读性模式)
  - [📊 模式统计与索引](#-模式统计与索引)
    - [模式统计](#模式统计)
  - [🎯 使用指南](#-使用指南)
    - [快速查找](#快速查找)
    - [模式应用](#模式应用)
    - [扩展开发](#扩展开发)

---

## 1. SQL代码模式分类体系

### 1.1 分类依据

基于以下权威标准进行分类：

1. **ACM计算分类系统 (CCS)**
   - 数据结构和算法
   - 数据库系统
   - 信息检索
   - 机器学习

2. **IEEE计算分类**
   - 数据库系统
   - 数据挖掘
   - 机器学习
   - 统计分析

3. **SQL标准 (ISO/IEC 9075)**
   - SQL/Foundation
   - SQL/OLAP
   - SQL/MED

4. **PostgreSQL官方文档分类**
   - 数学函数
   - 聚合函数
   - 窗口函数
   - 全文搜索
   - 数组函数
   - JSON/JSONB函数

### 1.2 分类维度

| 维度 | 说明 | 示例 |
|------|------|------|
| **功能维度** | 按算法功能分类 | 排序、搜索、聚合、统计 |
| **复杂度维度** | 按时间复杂度分类 | O(1)、O(log n)、O(n)、O(n²) |
| **应用维度** | 按应用场景分类 | 业务分析、技术分析、预测分析 |
| **技术维度** | 按技术特性分类 | 窗口函数、递归CTE、数组操作 |

---

## 2. 数学与计算类SQL模式

### 2.1 基础数学运算模式

**模式特征**:

- 使用PostgreSQL内置数学函数
- 复杂度: O(1)
- 应用场景: 通用计算、科学计算、工程计算

**核心SQL模式**:

```sql
-- 模式1: 基础四则运算（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    value1 + value2 AS addition,
    value1 - value2 AS subtraction,
    value1 * value2 AS multiplication,
    value1 / NULLIF(value2, 0) AS division  -- 避免除零错误
FROM table_name
LIMIT 100;

-- 模式2: 幂运算和开方（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    POWER(value, exponent) AS power_result,
    SQRT(value) AS square_root,
    CBRT(value) AS cube_root
FROM table_name
LIMIT 100;

-- 模式3: 对数运算（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    LN(value) AS natural_log,
    LOG(10, value) AS log_base_10,
    LOG(2, value) AS log_base_2
FROM table_name
LIMIT 100;

-- 模式4: 三角函数（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    SIN(angle) AS sine,
    COS(angle) AS cosine,
    TAN(angle) AS tangent,
    ASIN(value) AS arc_sine,
    ACOS(value) AS arc_cosine,
    ATAN(value) AS arc_tangent
FROM table_name
LIMIT 100;
```

**归类标签**: `数学函数` `基础运算` `科学计算` `O(1)`

### 2.2 高级数学计算模式

**模式特征**:

- 矩阵运算、向量计算、复数运算
- 复杂度: O(n) 到 O(n²)
- 应用场景: 科学计算、机器学习、数据分析

**核心SQL模式**:

```sql
-- 模式1: 向量点积（使用数组）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    array1,
    array2,
    (
        SELECT SUM(a * b)
        FROM unnest(array1) WITH ORDINALITY AS t1(a, idx)
        JOIN unnest(array2) WITH ORDINALITY AS t2(b, idx) USING (idx)
    ) AS dot_product
FROM vectors
LIMIT 100;

-- 模式2: 向量范数（L2范数）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    array_value,
    SQRT(SUM(x * x)) AS l2_norm
FROM (
    SELECT unnest(array_value) AS x
    FROM vectors
) AS expanded
LIMIT 100;

-- 模式3: 矩阵转置（使用数组）
SELECT
    array_agg(row_value ORDER BY col_idx) AS transposed_matrix
FROM (
    SELECT
        col_idx,
        array_agg(value ORDER BY row_idx) AS row_value
    FROM (
        SELECT
            row_idx,
            col_idx,
            value
        FROM unnest(matrix_array) WITH ORDINALITY AS t(value, idx)
        CROSS JOIN LATERAL (
            SELECT
                (idx - 1) / array_length(matrix_array, 1) AS row_idx,
                (idx - 1) % array_length(matrix_array, 1) AS col_idx
        ) AS indices
    ) AS matrix_expanded
    GROUP BY col_idx
) AS transposed;
```

**归类标签**: `高级数学` `向量计算` `矩阵运算` `O(n²)`

### 2.3 数值精度处理模式

**模式特征**:

- 四舍五入、截断、精度控制
- 复杂度: O(1)
- 应用场景: 金融计算、报表生成、数据展示

**核心SQL模式**:

```sql
-- 模式1: 四舍五入（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    ROUND(value, 2) AS rounded_2_decimal,
    ROUND(value, -2) AS rounded_hundreds,
    ROUND(value::numeric, 4) AS rounded_numeric
FROM table_name
LIMIT 100;

-- 模式2: 截断（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    TRUNC(value, 2) AS truncated_2_decimal,
    TRUNC(value, -2) AS truncated_hundreds
FROM table_name
LIMIT 100;

-- 模式3: 精度控制（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    value,
    CAST(value AS NUMERIC(10, 2)) AS fixed_precision,
    value::DECIMAL(10, 4) AS decimal_precision
FROM table_name
LIMIT 100;

-- 模式4: 科学计数法（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    value,
    value::TEXT AS text_format,
    TO_CHAR(value, '9.99EEEE') AS scientific_notation
FROM table_name
LIMIT 100;
```

**归类标签**: `精度处理` `金融计算` `数据格式化` `O(1)`

---

## 3. 数据统计与分析类SQL模式

### 3.1 描述性统计模式

**模式特征**:

- 中心趋势、离散程度、分布形状
- 复杂度: O(n)
- 应用场景: 数据分析、报表生成、数据探索

**核心SQL模式**:

```sql
-- 模式1: 中心趋势度量（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    AVG(value) AS mean,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value) AS median,
    MODE() WITHIN GROUP (ORDER BY value) AS mode
FROM table_name
LIMIT 100;

-- 模式2: 离散程度度量（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    STDDEV(value) AS standard_deviation,
    VARIANCE(value) AS variance,
    MAX(value) - MIN(value) AS range,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) -
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) AS iqr
FROM table_name
LIMIT 100;

-- 模式3: 分位数统计（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    PERCENTILE_CONT(ARRAY[0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    WITHIN GROUP (ORDER BY value) AS percentiles
FROM table_name
LIMIT 100;

-- 模式4: 综合统计报告（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    COUNT(*) AS count,
    AVG(value) AS mean,
    STDDEV(value) AS stddev,
    MIN(value) AS min_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) AS q1,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value) AS median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) AS q3,
    MAX(value) AS max_value
FROM table_name
LIMIT 100;
```

**归类标签**: `描述性统计` `中心趋势` `离散程度` `O(n)`

### 3.2 聚合统计分析模式

**模式特征**:

- COUNT、SUM、AVG、MIN、MAX、PERCENTILE
- 复杂度: O(n)
- 应用场景: 报表生成、数据汇总、业务分析

**核心SQL模式**:

```sql
-- 模式1: 基础聚合（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    COUNT(*) AS total_count,
    COUNT(DISTINCT column) AS distinct_count,
    SUM(value) AS total_sum,
    AVG(value) AS average,
    MIN(value) AS minimum,
    MAX(value) AS maximum
FROM table_name
WHERE condition
LIMIT 100;

-- 模式2: 条件聚合（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    COUNT(*) FILTER (WHERE status = 'active') AS active_count,
    SUM(amount) FILTER (WHERE status = 'completed') AS completed_amount,
    AVG(price) FILTER (WHERE category = 'A') AS category_a_avg
FROM table_name
LIMIT 100;

-- 模式3: 分组聚合（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    category,
    COUNT(*) AS count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount
FROM table_name
GROUP BY category
ORDER BY total_amount DESC
LIMIT 100;

-- 模式4: 多维度聚合（ROLLUP）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    region,
    category,
    SUM(amount) AS total_amount
FROM table_name
GROUP BY ROLLUP(region, category)
LIMIT 100;
```

**归类标签**: `聚合统计` `分组分析` `多维分析` `O(n)`

### 3.3 窗口函数统计模式

**模式特征**:

- ROW_NUMBER、RANK、DENSE_RANK、LAG、LEAD
- 复杂度: O(n log n)
- 应用场景: 排名分析、趋势分析、同比环比

**核心SQL模式**:

```sql
-- 模式1: 排名函数（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    id,
    value,
    ROW_NUMBER() OVER (ORDER BY value DESC) AS row_number,
    RANK() OVER (ORDER BY value DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY value DESC) AS dense_rank,
    PERCENT_RANK() OVER (ORDER BY value DESC) AS percent_rank
FROM table_name
LIMIT 100;

-- 模式2: 窗口聚合（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    date,
    value,
    SUM(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_sum_7,
    AVG(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7
FROM table_name
LIMIT 100;

-- 模式3: 前后值比较（LAG/LEAD）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    date,
    value,
    LAG(value, 1) OVER (ORDER BY date) AS prev_value,
    LEAD(value, 1) OVER (ORDER BY date) AS next_value,
    value - LAG(value, 1) OVER (ORDER BY date) AS diff_from_prev,
    (value - LAG(value, 1) OVER (ORDER BY date)) / NULLIF(LAG(value, 1) OVER (ORDER BY date), 0) * 100 AS pct_change
FROM table_name
LIMIT 100;

-- 模式4: 累计统计（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    date,
    value,
    SUM(value) OVER (ORDER BY date) AS cumulative_sum,
    AVG(value) OVER (ORDER BY date) AS cumulative_avg,
    COUNT(*) OVER (ORDER BY date) AS cumulative_count
FROM table_name
LIMIT 100;
```

**归类标签**: `窗口函数` `排名分析` `趋势分析` `O(n log n)`

---

## 4. 数据处理算法类SQL模式

### 4.1 排序算法模式

**模式特征**:

- ORDER BY、窗口排序、自定义排序
- 复杂度: O(n log n)
- 应用场景: 数据排序、Top N查询、分页

**核心SQL模式**:

```sql
-- 模式1: 基础排序（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM table_name
ORDER BY column1 ASC, column2 DESC
LIMIT 100;

-- 模式2: 自定义排序（CASE WHEN）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM table_name
ORDER BY
    CASE status
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END
LIMIT 100;

-- 模式3: 窗口排序（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY value DESC) AS rank_in_category
FROM table_name
WHERE ROW_NUMBER() OVER (PARTITION BY category ORDER BY value DESC) <= 10  -- Top 10 per category
LIMIT 100;

-- 模式4: 分页排序（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM table_name
) AS ranked
WHERE rn BETWEEN 101 AND 200  -- Page 2 (每页100条)
LIMIT 100;
```

**归类标签**: `排序算法` `Top N查询` `分页` `O(n log n)`

### 4.2 搜索算法模式

**模式特征**:

- 精确搜索、模糊搜索、全文搜索、正则搜索
- 复杂度: O(log n) 到 O(n)
- 应用场景: 数据查找、内容搜索、模式匹配

**核心SQL模式**:

```sql
-- 模式1: 精确搜索（索引优化）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM table_name
WHERE id = 123  -- 使用主键索引，O(log n)
LIMIT 100;

-- 模式2: 范围搜索（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM table_name
WHERE value BETWEEN 100 AND 200
ORDER BY value
LIMIT 100;

-- 模式3: 模糊搜索（LIKE）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM table_name
WHERE name LIKE '%keyword%'  -- 注意：前导通配符无法使用索引
LIMIT 100;

-- 模式4: 全文搜索（tsvector）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM table_name
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'keyword & search')
LIMIT 100;

-- 模式5: 正则表达式搜索（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM table_name
WHERE column ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'  -- 日期格式匹配
LIMIT 100;

-- 模式6: 数组包含搜索（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM table_name
WHERE tags @> ARRAY['tag1', 'tag2']  -- 数组包含所有指定元素
LIMIT 100;
```

**归类标签**: `搜索算法` `全文搜索` `模式匹配` `O(log n)`

### 4.3 去重算法模式

**模式特征**:

- DISTINCT、GROUP BY去重、窗口函数去重
- 复杂度: O(n log n)
- 应用场景: 数据清洗、唯一值提取

**核心SQL模式**:

```sql
-- 模式1: DISTINCT去重（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT DISTINCT column1, column2
FROM table_name
LIMIT 100;

-- 模式2: GROUP BY去重（保留其他列）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    column1,
    column2,
    MAX(column3) AS column3,  -- 或其他聚合函数
    MAX(column4) AS column4
FROM table_name
GROUP BY column1, column2
LIMIT 100;

-- 模式3: 窗口函数去重（保留第一条）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY column1, column2 ORDER BY id) AS rn
    FROM table_name
) AS ranked
WHERE rn = 1
LIMIT 100;

-- 模式4: EXISTS去重（相关子查询）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT *
FROM table_name t1
WHERE NOT EXISTS (
    SELECT 1
    FROM table_name t2
    WHERE t2.column1 = t1.column1
      AND t2.column2 = t1.column2
      AND t2.id < t1.id
)
LIMIT 100;
```

**归类标签**: `去重算法` `数据清洗` `唯一值` `O(n log n)`

---

## 5. 数据挖掘类SQL模式

### 5.1 关联规则挖掘模式

**模式特征**:

- Apriori算法、频繁项集、关联规则
- 复杂度: O(2^n) 到 O(n²)
- 应用场景: 市场分析、推荐系统、购物篮分析

**核心SQL模式**:

```sql
-- 模式1: 频繁项集统计（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    item1,
    item2,
    COUNT(*) AS support_count,
    COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM transactions), 0) AS support_pct
FROM (
    SELECT DISTINCT
        t1.transaction_id,
        t1.item AS item1,
        t2.item AS item2
    FROM transaction_items t1
    JOIN transaction_items t2 ON t1.transaction_id = t2.transaction_id
    WHERE t1.item < t2.item  -- 避免重复组合
) AS pairs
GROUP BY item1, item2
HAVING COUNT(*) >= 10  -- 最小支持度阈值
ORDER BY support_count DESC
LIMIT 100;

-- 模式2: 关联规则计算（置信度）
WITH frequent_itemsets AS (
    SELECT
        item1,
        item2,
        COUNT(*) AS support_count
    FROM (
        SELECT DISTINCT
            t1.transaction_id,
            t1.item AS item1,
            t2.item AS item2
        FROM transaction_items t1
        JOIN transaction_items t2 ON t1.transaction_id = t2.transaction_id
        WHERE t1.item < t2.item
    ) AS pairs
    GROUP BY item1, item2
    HAVING COUNT(*) >= 10
),
item_counts AS (
    SELECT
        item,
        COUNT(DISTINCT transaction_id) AS item_count
    FROM transaction_items
    GROUP BY item
)
SELECT
    fi.item1,
    fi.item2,
    fi.support_count,
    fi.support_count * 100.0 / ic.item_count AS confidence_pct
FROM frequent_itemsets fi
JOIN item_counts ic ON fi.item1 = ic.item
ORDER BY confidence_pct DESC;
```

**归类标签**: `关联规则` `频繁项集` `市场分析` `O(n²)`

### 5.2 聚类分析模式

**模式特征**:

- K-means、层次聚类、DBSCAN
- 复杂度: O(n²)
- 应用场景: 用户分群、数据分类、异常检测

**核心SQL模式**:

```sql
-- 模式1: 简单K-means（使用窗口函数）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH initial_centroids AS (
    SELECT
        id,
        x,
        y,
        NTILE(3) OVER (ORDER BY x, y) AS cluster_id
    FROM points
),
cluster_centers AS (
    SELECT
        cluster_id,
        AVG(x) AS center_x,
        AVG(y) AS center_y
    FROM initial_centroids
    GROUP BY cluster_id
),
distances AS (
    SELECT
        p.id,
        p.x,
        p.y,
        c.cluster_id,
        SQRT(POWER(p.x - c.center_x, 2) + POWER(p.y - c.center_y, 2)) AS distance
    FROM points p
    CROSS JOIN cluster_centers c
),
closest_clusters AS (
    SELECT
        id,
        x,
        y,
        cluster_id,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY distance) AS rn
    FROM distances
)
SELECT
    id,
    x,
    y,
    cluster_id
FROM closest_clusters
WHERE rn = 1
LIMIT 100;
```

**归类标签**: `聚类分析` `K-means` `用户分群` `O(n²)`

---

## 6. 时间序列处理类SQL模式

### 6.1 时间序列聚合模式

**模式特征**:

- 按时间分组聚合、时间桶聚合
- 复杂度: O(n)
- 应用场景: 业务指标监控、报表生成

**核心SQL模式**:

```sql
-- 模式1: 按时间分组聚合（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    DATE_TRUNC('day', timestamp) AS date,
    COUNT(*) AS count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount
FROM table_name
GROUP BY DATE_TRUNC('day', timestamp)
ORDER BY date
LIMIT 100;

-- 模式2: 时间桶聚合（自定义时间间隔）
SELECT
    date_bin('1 hour', timestamp, '2024-01-01 00:00:00'::timestamp) AS hour_bucket,
    COUNT(*) AS count,
    SUM(value) AS total_value
FROM table_name
GROUP BY hour_bucket
ORDER BY hour_bucket;

-- 模式3: 时间序列填充（生成连续时间序列）
WITH time_series AS (
    SELECT generate_series(
        '2024-01-01'::date,
        '2024-12-31'::date,
        '1 day'::interval
    ) AS date
)
SELECT
    ts.date,
    COALESCE(d.count, 0) AS count,
    COALESCE(d.amount, 0) AS amount
FROM time_series ts
LEFT JOIN (
    SELECT
        DATE_TRUNC('day', timestamp) AS date,
        COUNT(*) AS count,
        SUM(amount) AS amount
    FROM table_name
    GROUP BY DATE_TRUNC('day', timestamp)
) d ON ts.date = d.date
ORDER BY ts.date;
```

**归类标签**: `时间序列` `时间聚合` `时间桶` `O(n)`

### 6.2 滑动窗口计算模式

**模式特征**:

- 移动平均、指数移动平均、滚动统计
- 复杂度: O(n)
- 应用场景: 趋势分析、平滑处理、预测

**核心SQL模式**:

```sql
-- 模式1: 简单移动平均（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    date,
    value,
    AVG(value) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7
FROM table_name
ORDER BY date
LIMIT 100;

-- 模式2: 指数移动平均（EMA）
WITH ema_calc AS (
    SELECT
        date,
        value,
        value AS ema,
        0.3 AS alpha  -- 平滑系数
    FROM table_name
    WHERE date = (SELECT MIN(date) FROM table_name)
    UNION ALL
    SELECT
        t.date,
        t.value,
        e.ema * (1 - e.alpha) + t.value * e.alpha AS ema,
        e.alpha
    FROM table_name t
    JOIN ema_calc e ON t.date = e.date + INTERVAL '1 day'
)
SELECT * FROM ema_calc;

-- 模式3: 滚动统计
SELECT
    date,
    value,
    AVG(value) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_30,
    STDDEV(value) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_stddev_30,
    MIN(value) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_min_30,
    MAX(value) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_max_30
FROM table_name
ORDER BY date;
```

**归类标签**: `滑动窗口` `移动平均` `趋势分析` `O(n)`

---

## 7. 文本处理类SQL模式

### 7.1 文本搜索模式

**模式特征**:

- 全文搜索、模糊搜索、正则搜索
- 复杂度: O(n+m)
- 应用场景: 内容搜索、文档检索、知识管理

**核心SQL模式**:

```sql
-- 模式1: 全文搜索（tsvector）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    id,
    title,
    content,
    ts_rank(to_tsvector('english', content), query) AS rank
FROM documents,
     to_tsquery('english', 'keyword1 & keyword2') AS query
WHERE to_tsvector('english', content) @@ query
ORDER BY rank DESC
LIMIT 100;

-- 模式2: 模糊搜索（相似度）
SELECT
    id,
    name,
    similarity(name, 'search_term') AS similarity_score
FROM table_name
WHERE similarity(name, 'search_term') > 0.3
ORDER BY similarity_score DESC;

-- 模式3: 正则表达式搜索
SELECT *
FROM table_name
WHERE content ~* 'pattern.*regex';  -- 不区分大小写

-- 模式4: 数组文本搜索
SELECT *
FROM table_name
WHERE tags && ARRAY['tag1', 'tag2'];  -- 数组重叠
```

**归类标签**: `文本搜索` `全文搜索` `模糊搜索` `O(n+m)`

### 7.2 文本相似度计算模式

**模式特征**:

- 编辑距离、余弦相似度、Jaccard相似度
- 复杂度: O(n*m)
- 应用场景: 重复检测、相似度匹配、推荐系统

**核心SQL模式**:

```sql
-- 模式1: 编辑距离（Levenshtein）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    text1,
    text2,
    levenshtein(text1, text2) AS edit_distance,
    1.0 - levenshtein(text1, text2)::float / NULLIF(GREATEST(length(text1), length(text2)), 0) AS similarity
FROM text_pairs
LIMIT 100;

-- 模式2: Jaccard相似度（基于词集合）
WITH words1 AS (
    SELECT unnest(string_to_array(lower(text1), ' ')) AS word
    FROM text_pairs
),
words2 AS (
    SELECT unnest(string_to_array(lower(text2), ' ')) AS word
    FROM text_pairs
),
intersection AS (
    SELECT COUNT(DISTINCT w1.word) AS count
    FROM words1 w1
    JOIN words2 w2 ON w1.word = w2.word
),
union_set AS (
    SELECT COUNT(DISTINCT word) AS count
    FROM (SELECT word FROM words1 UNION SELECT word FROM words2) AS all_words
)
SELECT
    i.count::float / NULLIF(u.count, 0) AS jaccard_similarity
FROM intersection i, union_set u;
```

**归类标签**: `文本相似度` `编辑距离` `Jaccard` `O(n*m)`

---

## 8. 图算法类SQL模式

### 8.1 图遍历模式

**模式特征**:

- 深度优先搜索、广度优先搜索
- 复杂度: O(V+E)
- 应用场景: 社交网络分析、推荐系统、关系分析

**核心SQL模式**:

```sql
-- 模式1: 递归CTE深度优先搜索（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH RECURSIVE dfs AS (
    -- 起始节点
    SELECT
        id,
        ARRAY[id] AS path,
        0 AS depth
    FROM nodes
    WHERE id = 1  -- 起始节点ID

    UNION ALL

    -- 递归：访问相邻节点
    SELECT
        e.target_id,
        d.path || e.target_id,
        d.depth + 1
    FROM dfs d
    JOIN edges e ON d.id = e.source_id
    WHERE e.target_id != ALL(d.path)  -- 避免循环
      AND d.depth < 10  -- 最大深度限制
)
SELECT * FROM dfs
LIMIT 100;

-- 模式2: 广度优先搜索（使用队列）
WITH RECURSIVE bfs AS (
    SELECT
        id,
        ARRAY[id] AS path,
        0 AS level
    FROM nodes
    WHERE id = 1

    UNION ALL

    SELECT
        e.target_id,
        b.path || e.target_id,
        b.level + 1
    FROM bfs b
    JOIN edges e ON b.id = e.source_id
    WHERE e.target_id != ALL(b.path)
      AND b.level < 10
)
SELECT
    id,
    path,
    level
FROM bfs
WHERE level = (
    SELECT MIN(level)
    FROM bfs
    WHERE id = bfs.id
)
ORDER BY level, id;
```

**归类标签**: `图遍历` `DFS` `BFS` `递归CTE` `O(V+E)`

### 8.2 最短路径算法模式

**模式特征**:

- Dijkstra算法、Floyd-Warshall算法
- 复杂度: O(V²) 到 O(V³)
- 应用场景: 路径规划、网络分析、路由优化

**核心SQL模式**:

```sql
-- 模式1: Dijkstra算法（递归CTE实现）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH RECURSIVE dijkstra AS (
    SELECT
        1 AS start_node,
        1 AS current_node,
        0 AS total_distance,
        ARRAY[1] AS path
    UNION ALL
    SELECT
        d.start_node,
        e.target_id,
        d.total_distance + e.weight,
        d.path || e.target_id
    FROM dijkstra d
    JOIN edges e ON d.current_node = e.source_id
    WHERE e.target_id != ALL(d.path)
      AND d.total_distance + e.weight < (
          SELECT COALESCE(MIN(total_distance), 999999)
          FROM dijkstra
          WHERE start_node = d.start_node
            AND current_node = e.target_id
      )
)
SELECT
    start_node,
    current_node AS target_node,
    MIN(total_distance) AS shortest_distance,
    (SELECT path FROM dijkstra
     WHERE start_node = d.start_node
       AND current_node = d.current_node
       AND total_distance = MIN(d.total_distance)
     LIMIT 1) AS shortest_path
FROM dijkstra d
GROUP BY start_node, current_node
LIMIT 100;
```

**归类标签**: `最短路径` `Dijkstra` `路径规划` `O(V²)`

---

## 9. 机器学习类SQL模式

### 9.1 线性回归模式

**模式特征**:

- 简单线性回归、多元线性回归
- 复杂度: O(n)
- 应用场景: 预测分析、趋势分析、相关性分析

**核心SQL模式**:

```sql
-- 模式1: 简单线性回归（最小二乘法）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH stats AS (
    SELECT
        AVG(x) AS avg_x,
        AVG(y) AS avg_y,
        COUNT(*) AS n,
        SUM(x * y) AS sum_xy,
        SUM(x * x) AS sum_x2
    FROM data_points
)
SELECT
    (sum_xy - n * avg_x * avg_y) / NULLIF(sum_x2 - n * avg_x * avg_x, 0) AS slope,
    avg_y - (sum_xy - n * avg_x * avg_y) / NULLIF(sum_x2 - n * avg_x * avg_x, 0) * avg_x AS intercept,
    CORR(x, y) AS correlation
FROM stats
LIMIT 100;

-- 模式2: 预测值计算
WITH regression AS (
    SELECT
        (sum_xy - n * avg_x * avg_y) / NULLIF(sum_x2 - n * avg_x * avg_x, 0) AS slope,
        avg_y - (sum_xy - n * avg_x * avg_y) / NULLIF(sum_x2 - n * avg_x * avg_x, 0) * avg_x AS intercept
    FROM (
        SELECT
            AVG(x) AS avg_x,
            AVG(y) AS avg_y,
            COUNT(*) AS n,
            SUM(x * y) AS sum_xy,
            SUM(x * x) AS sum_x2
        FROM data_points
    ) AS stats
)
SELECT
    x,
    y,
    r.slope * x + r.intercept AS predicted_y,
    y - (r.slope * x + r.intercept) AS residual
FROM data_points
CROSS JOIN regression r;
```

**归类标签**: `线性回归` `预测分析` `相关性分析` `O(n)`

---

## 10. 金融统计类SQL模式

### 10.1 收益率计算模式

**模式特征**:

- 简单收益率、对数收益率、年化收益率
- 复杂度: O(n)
- 应用场景: 投资分析、风险评估、资产配置

**核心SQL模式**:

```sql
-- 模式1: 简单收益率（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    date,
    price,
    LAG(price) OVER (ORDER BY date) AS prev_price,
    (price - LAG(price) OVER (ORDER BY date)) / NULLIF(LAG(price) OVER (ORDER BY date), 0) AS simple_return
FROM prices
ORDER BY date
LIMIT 100;

-- 模式2: 对数收益率
SELECT
    date,
    price,
    LN(price / NULLIF(LAG(price) OVER (ORDER BY date), 0)) AS log_return
FROM prices
ORDER BY date;

-- 模式3: 年化收益率
WITH daily_returns AS (
    SELECT
        date,
        (price - LAG(price) OVER (ORDER BY date)) / NULLIF(LAG(price) OVER (ORDER BY date), 0) AS daily_return
    FROM prices
)
SELECT
    AVG(daily_return) * 252 AS annualized_return,  -- 252个交易日
    STDDEV(daily_return) * SQRT(252) AS annualized_volatility
FROM daily_returns
WHERE daily_return IS NOT NULL;
```

**归类标签**: `收益率计算` `金融分析` `风险评估` `O(n)`

---

## 11. 运维运营类SQL模式

### 11.1 性能指标计算模式

**模式特征**:

- TPS、QPS、延迟、吞吐量
- 复杂度: O(n)
- 应用场景: 性能监控、容量规划、性能优化

**核心SQL模式**:

```sql
-- 模式1: TPS/QPS计算（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    DATE_TRUNC('second', timestamp) AS time_bucket,
    COUNT(*) AS request_count,
    COUNT(*) / 1.0 AS tps  -- 每秒事务数
FROM requests
GROUP BY DATE_TRUNC('second', timestamp)
ORDER BY time_bucket
LIMIT 100;

-- 模式2: 延迟统计
SELECT
    DATE_TRUNC('minute', timestamp) AS time_bucket,
    COUNT(*) AS request_count,
    AVG(response_time) AS avg_latency,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time) AS p50_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) AS p95_latency,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time) AS p99_latency,
    MAX(response_time) AS max_latency
FROM requests
GROUP BY DATE_TRUNC('minute', timestamp)
ORDER BY time_bucket;

-- 模式3: 错误率计算
SELECT
    DATE_TRUNC('hour', timestamp) AS time_bucket,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE status_code >= 400) AS error_count,
    COUNT(*) FILTER (WHERE status_code >= 400) * 100.0 / COUNT(*) AS error_rate_pct
FROM requests
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY time_bucket;
```

**归类标签**: `性能指标` `TPS` `QPS` `延迟统计` `O(n)`

### 11.2 异常检测算法模式

**模式特征**:

- 阈值检测、统计异常检测、Z-score
- 复杂度: O(n)
- 应用场景: 异常监控、故障预测、性能预警

**核心SQL模式**:

```sql
-- 模式1: Z-score异常检测
WITH stats AS (
    SELECT
        AVG(value) AS mean,
        STDDEV(value) AS stddev
    FROM metrics
    WHERE timestamp >= NOW() - INTERVAL '7 days'
)
SELECT
    timestamp,
    value,
    (value - s.mean) / NULLIF(s.stddev, 0) AS z_score,
    CASE
        WHEN ABS((value - s.mean) / NULLIF(s.stddev, 0)) > 3 THEN '异常'
        ELSE '正常'
    END AS status
FROM metrics
CROSS JOIN stats s
WHERE timestamp >= NOW() - INTERVAL '1 day'
ORDER BY ABS((value - s.mean) / NULLIF(s.stddev, 0)) DESC;

-- 模式2: 移动平均异常检测
SELECT
    timestamp,
    value,
    AVG(value) OVER (
        ORDER BY timestamp
        ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
    ) AS moving_avg_24,
    STDDEV(value) OVER (
        ORDER BY timestamp
        ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
    ) AS moving_stddev_24,
    CASE
        WHEN ABS(value - AVG(value) OVER (
            ORDER BY timestamp
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        )) > 3 * STDDEV(value) OVER (
            ORDER BY timestamp
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) THEN '异常'
        ELSE '正常'
    END AS status
FROM metrics
ORDER BY timestamp;
```

**归类标签**: `异常检测` `Z-score` `统计异常` `O(n)`

---

## 12. 数据库算法类SQL模式

### 12.1 索引优化模式

**模式特征**:

- B-tree、Hash、GIN、GiST索引
- 复杂度: O(log n)
- 应用场景: 查询优化、性能调优

**核心SQL模式**:

```sql
-- 模式1: 索引使用分析（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC
LIMIT 100;

-- 模式2: 未使用索引检测（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 100;
```

**归类标签**: `索引优化` `查询优化` `性能调优` `O(log n)`

---

## 13. 数据质量类SQL模式

### 13.1 数据清洗算法模式

**模式特征**:

- 缺失值处理、异常值处理、重复值处理
- 复杂度: O(n)
- 应用场景: 数据清洗、数据质量监控

**核心SQL模式**:

```sql
-- 模式1: 缺失值检测（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    column_name,
    COUNT(*) AS total_rows,
    COUNT(column_name) AS non_null_rows,
    COUNT(*) - COUNT(column_name) AS null_rows,
    (COUNT(*) - COUNT(column_name)) * 100.0 / NULLIF(COUNT(*), 0) AS null_percentage
FROM table_name
GROUP BY column_name
LIMIT 100;

-- 模式2: 异常值检测（IQR方法）
WITH quartiles AS (
    SELECT
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) AS q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) AS q3
    FROM table_name
),
bounds AS (
    SELECT
        q1,
        q3,
        q1 - 1.5 * (q3 - q1) AS lower_bound,
        q3 + 1.5 * (q3 - q1) AS upper_bound
    FROM quartiles
)
SELECT
    t.*,
    CASE
        WHEN t.value < b.lower_bound OR t.value > b.upper_bound THEN '异常值'
        ELSE '正常值'
    END AS status
FROM table_name t
CROSS JOIN bounds b;

-- 模式3: 重复值检测（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    column1,
    column2,
    COUNT(*) AS duplicate_count
FROM table_name
GROUP BY column1, column2
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 100;
```

**归类标签**: `数据清洗` `缺失值` `异常值` `重复值` `O(n)`

---

## 14. 综合应用模式

### 14.1 电商数据分析模式

**模式特征**:

- 销售分析、用户分析、商品分析
- 复杂度: 多种复杂度组合
- 应用场景: 业务分析、决策支持

**核心SQL模式**:

```sql
-- 模式1: 销售趋势分析（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    DATE_TRUNC('day', order_date) AS date,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(amount) AS total_sales,
    AVG(amount) AS avg_order_value,
    COUNT(DISTINCT customer_id) AS customer_count
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', order_date)
ORDER BY date
LIMIT 100;

-- 模式2: 用户行为分析（RFM模型）
WITH rfm AS (
    SELECT
        customer_id,
        MAX(order_date) AS last_order_date,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(amount) AS monetary_value,
        CURRENT_DATE - MAX(order_date) AS recency_days
    FROM orders
    GROUP BY customer_id
)
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary_value,
    NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
    NTILE(5) OVER (ORDER BY frequency) AS f_score,
    NTILE(5) OVER (ORDER BY monetary_value) AS m_score
FROM rfm;
```

**归类标签**: `电商分析` `销售分析` `用户分析` `RFM模型`

---

## 15. 代码模式最佳实践

### 15.1 错误处理模式

**标准错误处理模板**:

```sql
-- 模式：DO块错误处理
DO $$
BEGIN
    BEGIN
        -- 检查表是否存在
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'table_name'
        ) THEN
            RAISE WARNING '表 table_name 不存在';
            RETURN;
        END IF;

        -- 检查列是否存在
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'table_name'
              AND column_name = 'column_name'
        ) THEN
            RAISE WARNING '列 column_name 不存在';
            RETURN;
        END IF;

        -- 执行主要逻辑
        RAISE NOTICE '开始执行操作';

    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 15.2 性能优化模式

**性能优化最佳实践**:

1. **使用索引**: 在WHERE、JOIN、ORDER BY列上创建索引
2. **避免全表扫描**: 使用LIMIT、WHERE条件过滤
3. **使用EXISTS而非IN**: 对于子查询，EXISTS通常更快
4. **避免SELECT ***: 只选择需要的列
5. **使用窗口函数**: 替代自连接和子查询
6. **批量处理**: 使用批量INSERT、UPDATE、DELETE

### 15.3 代码可读性模式

**代码格式化标准**:

```sql
-- 1. 使用有意义的别名（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    o.order_id,
    o.order_date,
    c.customer_name,
    SUM(oi.quantity * oi.price) AS total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.order_date, c.customer_name
LIMIT 100;

-- 2. 使用CTE提高可读性（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH filtered_orders AS (
    SELECT *
    FROM orders
    WHERE order_date >= '2024-01-01'
),
aggregated AS (
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(amount) AS total_amount
    FROM filtered_orders
    GROUP BY customer_id
)
SELECT * FROM aggregated
LIMIT 100;
```

---

## 📊 模式统计与索引

### 模式统计

| 分类 | 模式数量 | 复杂度范围 | 应用场景数 |
|------|---------|-----------|-----------|
| 数学与计算 | 3 | O(1) - O(n²) | 5+ |
| 数据统计与分析 | 3 | O(n) - O(n log n) | 10+ |
| 数据处理算法 | 3 | O(log n) - O(n log n) | 8+ |
| 数据挖掘 | 2 | O(n²) - O(2^n) | 6+ |
| 时间序列处理 | 2 | O(n) | 5+ |
| 文本处理 | 2 | O(n+m) - O(n*m) | 4+ |
| 图算法 | 2 | O(V+E) - O(V²) | 4+ |
| 机器学习 | 1 | O(n) | 3+ |
| 金融统计 | 1 | O(n) | 4+ |
| 运维运营 | 2 | O(n) | 6+ |
| 数据库算法 | 1 | O(log n) | 3+ |
| 数据质量 | 1 | O(n) | 4+ |
| 综合应用 | 1 | 多种 | 5+ |

**总计**: 24+个核心SQL模式，50+个应用场景

---

## 🎯 使用指南

### 快速查找

1. **按功能查找**: 使用分类目录快速定位
2. **按复杂度查找**: 参考复杂度维度选择合适模式
3. **按应用场景查找**: 参考应用场景匹配业务需求

### 模式应用

1. **理解模式**: 阅读模式说明和SQL代码
2. **适配场景**: 根据实际需求调整SQL代码
3. **性能测试**: 使用EXPLAIN (ANALYZE, BUFFERS, TIMING)测试性能
4. **错误处理**: 添加适当的错误处理逻辑

### 扩展开发

1. **模式组合**: 组合多个模式解决复杂问题
2. **模式优化**: 根据数据特点优化模式实现
3. **模式创新**: 基于现有模式开发新模式

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**版本**: 1.0
