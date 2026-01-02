# PostgreSQL ARIMA模型完整指南

> **创建日期**: 2025年1月
> **技术栈**: PostgreSQL 17+/18+ | 时间序列 | ARIMA | 预测模型
> **难度级别**: ⭐⭐⭐⭐⭐ (专家级)
> **参考标准**: Time Series Analysis (Box & Jenkins), Forecasting Methods

---

## 📋 目录

- [PostgreSQL ARIMA模型完整指南](#postgresql-arima模型完整指南)
  - [📋 目录](#-目录)
  - [ARIMA概述](#arima概述)
    - [理论基础](#理论基础)
    - [模型结构](#模型结构)
    - [参数含义](#参数含义)
  - [1. 自回归（AR）](#1-自回归ar)
    - [1.1 AR模型原理](#11-ar模型原理)
  - [2. 差分（I）](#2-差分i)
    - [2.1 平稳性检验](#21-平稳性检验)
  - [3. 移动平均（MA）](#3-移动平均ma)
    - [3.1 MA模型原理](#31-ma模型原理)
  - [4. ARIMA模型](#4-arima模型)
    - [4.1 ARIMA(p,d,q)](#41-arimapdq)
    - [4.2 模型识别](#42-模型识别)
  - [5. 预测](#5-预测)
    - [5.1 点预测](#51-点预测)
  - [📚 参考资源](#-参考资源)
  - [📊 性能优化建议](#-性能优化建议)
  - [🎯 最佳实践](#-最佳实践)

---

## ARIMA概述

**ARIMA（AutoRegressive Integrated Moving Average）**是经典的时间序列预测模型。

### 理论基础

ARIMA模型结合了：

- **AR（自回归）**: 使用历史值预测
- **I（差分）**: 使序列平稳
- **MA（移动平均）**: 使用历史误差预测

### 模型结构

**ARIMA(p,d,q)**:

- $p$: 自回归项数
- $d$: 差分次数
- $q$: 移动平均项数

### 参数含义

| 参数 | 含义 | 影响 |
|------|------|------|
| **p** | AR项数 | 历史值的依赖程度 |
| **d** | 差分次数 | 平稳性处理 |
| **q** | MA项数 | 误差的依赖程度 |

---

## 1. 自回归（AR）

### 1.1 AR模型原理

**AR(p)模型**:
$$X_t = c + \phi_1 X_{t-1} + \phi_2 X_{t-2} + ... + \phi_p X_{t-p} + \epsilon_t$$

```sql
-- ARIMA数据准备（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'arima_data') THEN
            RAISE WARNING '表 arima_data 已存在，先删除';
            DROP TABLE arima_data CASCADE;
        END IF;

        CREATE TABLE arima_data (
            time_point INTEGER PRIMARY KEY,
            value NUMERIC NOT NULL
        );

        -- 插入时间序列数据
        INSERT INTO arima_data (time_point, value) VALUES
            (1, 10), (2, 12), (3, 11), (4, 13), (5, 14),
            (6, 15), (7, 13), (8, 16), (9, 17), (10, 15);

        RAISE NOTICE '表 arima_data 创建成功';
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 arima_data 已存在';
        WHEN OTHERS THEN
            RAISE EXCEPTION '创建表失败: %', SQLERRM;
    END;
END $$;

-- AR(1)模型参数估计（使用Yule-Walker方程）
WITH autocorrelations AS (
    SELECT
        lag,
        CORR(value, LAG(value, lag) OVER (ORDER BY time_point)) AS autocorr
    FROM arima_data
    CROSS JOIN generate_series(1, 3) AS lag
    WHERE LAG(value, lag) OVER (ORDER BY time_point) IS NOT NULL
    GROUP BY lag
),
ar_coefficients AS (
    SELECT
        autocorr AS phi1
    FROM autocorrelations
    WHERE lag = 1
)
SELECT
    ROUND(phi1::numeric, 4) AS ar1_coefficient
FROM ar_coefficients;
```

---

## 2. 差分（I）

### 2.1 平稳性检验

**ADF检验**（Augmented Dickey-Fuller）用于检验平稳性。

```sql
-- 差分操作
WITH differenced_data AS (
    SELECT
        time_point,
        value,
        value - LAG(value) OVER (ORDER BY time_point) AS first_diff,
        (value - LAG(value) OVER (ORDER BY time_point)) -
        LAG(value - LAG(value) OVER (ORDER BY time_point)) OVER (ORDER BY time_point) AS second_diff
    FROM arima_data
)
SELECT
    time_point,
    ROUND(value::numeric, 2) AS original_value,
    ROUND(first_diff::numeric, 2) AS first_difference,
    ROUND(second_diff::numeric, 2) AS second_difference
FROM differenced_data
ORDER BY time_point;
```

---

## 3. 移动平均（MA）

### 3.1 MA模型原理

**MA(q)模型**:
$$X_t = \mu + \epsilon_t + \theta_1 \epsilon_{t-1} + \theta_2 \epsilon_{t-2} + ... + \theta_q \epsilon_{t-q}$$

```sql
-- MA模型参数估计（简化版）
WITH residuals AS (
    SELECT
        time_point,
        value - AVG(value) OVER () AS residual
    FROM arima_data
),
ma_coefficients AS (
    SELECT
        CORR(residual, LAG(residual) OVER (ORDER BY time_point)) AS theta1
    FROM residuals
    WHERE LAG(residual) OVER (ORDER BY time_point) IS NOT NULL
)
SELECT
    ROUND(theta1::numeric, 4) AS ma1_coefficient
FROM ma_coefficients;
```

---

## 4. ARIMA模型

### 4.1 ARIMA(p,d,q)

**ARIMA(p,d,q)模型**:
$$\phi(B)(1-B)^d X_t = \theta(B) \epsilon_t$$

其中 $B$ 是滞后算子。

### 4.2 模型识别

**ACF和PACF**用于识别模型参数。

```sql
-- ACF和PACF计算
WITH acf_values AS (
    SELECT
        lag,
        CORR(value, LAG(value, lag) OVER (ORDER BY time_point)) AS acf
    FROM arima_data
    CROSS JOIN generate_series(1, 5) AS lag
    WHERE LAG(value, lag) OVER (ORDER BY time_point) IS NOT NULL
    GROUP BY lag
)
SELECT
    lag,
    ROUND(acf::numeric, 4) AS autocorrelation
FROM acf_values
ORDER BY lag;
```

---

## 5. 预测

### 5.1 点预测

**ARIMA预测**:
$$\hat{X}_{t+h} = E[X_{t+h} | X_t, X_{t-1}, ...]$$

```sql
-- ARIMA预测（简化版：AR(1)）
WITH ar_model AS (
    SELECT
        0.8 AS phi1,  -- AR(1)系数
        10.0 AS mean_value
    FROM generate_series(1, 1)
),
forecast_steps AS (
    SELECT
        generate_series(11, 15) AS forecast_time,
        (SELECT mean_value FROM ar_model) AS last_value
    FROM generate_series(1, 1)
)
SELECT
    forecast_time,
    ROUND((mean_value + phi1 * (last_value - mean_value))::numeric, 2) AS forecast_value
FROM forecast_steps
CROSS JOIN ar_model;
```

---

## 📚 参考资源

1. **Box, G.E.P., Jenkins, G.M. (1976)**: "Time Series Analysis: Forecasting and Control"
2. **Hamilton, J.D. (1994)**: "Time Series Analysis"

## 📊 性能优化建议

1. **模型选择**: 使用AIC/BIC选择最优模型
2. **参数估计**: 使用最大似然估计
3. **验证**: 使用交叉验证评估模型

## 🎯 最佳实践

1. **平稳性**: 确保序列平稳
2. **模型诊断**: 检查残差
3. **参数选择**: 使用信息准则
4. **预测评估**: 评估预测准确性

---

**最后更新**: 2025年1月
**文档状态**: ✅ 已完成
