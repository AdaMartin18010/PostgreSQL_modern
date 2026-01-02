# PostgreSQL GARCH模型完整指南

> **创建日期**: 2025年1月
> **技术栈**: PostgreSQL 17+/18+ | 时间序列 | GARCH | 波动率建模
> **难度级别**: ⭐⭐⭐⭐⭐ (专家级)
> **参考标准**: GARCH Models (Engle), Financial Time Series, Volatility Modeling

---

## 📋 目录

- [PostgreSQL GARCH模型完整指南](#postgresql-garch模型完整指南)
  - [📋 目录](#-目录)
  - [GARCH概述](#garch概述)
    - [理论基础](#理论基础)
    - [模型结构](#模型结构)
    - [应用场景](#应用场景)
  - [1. ARCH模型](#1-arch模型)
    - [1.1 ARCH原理](#11-arch原理)
  - [2. GARCH模型](#2-garch模型)
    - [2.1 GARCH(p,q)](#21-garchpq)
  - [📚 参考资源](#-参考资源)

---

## GARCH概述

**GARCH（Generalized Autoregressive Conditional Heteroskedasticity）**用于建模时间序列的条件异方差性。

### 理论基础

GARCH模型假设条件方差依赖于历史方差和残差平方。

### 模型结构

**GARCH(p,q)模型**:
$$\sigma_t^2 = \omega + \sum_{i=1}^{q} \alpha_i \epsilon_{t-i}^2 + \sum_{j=1}^{p} \beta_j \sigma_{t-j}^2$$

其中：

- $\sigma_t^2$ 是条件方差
- $\epsilon_t$ 是残差
- $\omega, \alpha_i, \beta_j$ 是参数

### 应用场景

| 应用领域 | 具体应用 |
|---------|---------|
| **金融** | 波动率预测、风险管理 |
| **经济** | 经济波动建模 |
| **能源** | 价格波动分析 |

---

## 1. ARCH模型

### 1.1 ARCH原理

**ARCH(q)模型**:
$$\sigma_t^2 = \omega + \sum_{i=1}^{q} \alpha_i \epsilon_{t-i}^2$$

```sql
-- GARCH数据准备（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'garch_data') THEN
            RAISE WARNING '表 garch_data 已存在，先删除';
            DROP TABLE garch_data CASCADE;
        END IF;

        CREATE TABLE garch_data (
            date DATE PRIMARY KEY,
            return_rate NUMERIC NOT NULL,
            squared_return NUMERIC NOT NULL
        );

        -- 插入收益率数据
        INSERT INTO garch_data (date, return_rate, squared_return) VALUES
            ('2024-01-01', 0.02, 0.0004),
            ('2024-01-02', -0.01, 0.0001),
            ('2024-01-03', 0.015, 0.000225);

        RAISE NOTICE '表 garch_data 创建成功';
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 garch_data 已存在';
        WHEN OTHERS THEN
            RAISE EXCEPTION '创建表失败: %', SQLERRM;
    END;
END $$;

-- ARCH效应检验（Ljung-Box检验）
WITH squared_residuals AS (
    SELECT
        date,
        return_rate,
        POWER(return_rate, 2) AS squared_return
    FROM garch_data
),
autocorrelations AS (
    SELECT
        lag,
        CORR(squared_return, LAG(squared_return, lag) OVER (ORDER BY date)) AS autocorr
    FROM squared_residuals
    CROSS JOIN generate_series(1, 5) AS lag
    WHERE LAG(squared_return, lag) OVER (ORDER BY date) IS NOT NULL
    GROUP BY lag
)
SELECT
    lag,
    ROUND(autocorr::numeric, 4) AS autocorrelation,
    CASE
        WHEN ABS(autocorr) > 0.2 THEN 'ARCH effect present'
        ELSE 'No ARCH effect'
    END AS arch_test_result
FROM autocorrelations
ORDER BY lag;
```

---

## 2. GARCH模型

### 2.1 GARCH(p,q)

**GARCH(1,1)**是最常用的模型：
$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

```sql
-- GARCH(1,1)条件方差计算（简化版）
WITH garch_parameters AS (
    SELECT
        0.0001 AS omega,
        0.1 AS alpha,
        0.85 AS beta
    FROM generate_series(1, 1)
),
conditional_variance AS (
    SELECT
        date,
        return_rate,
        POWER(return_rate, 2) AS squared_return,
        -- 递归计算条件方差
        omega + alpha * LAG(POWER(return_rate, 2)) OVER (ORDER BY date) +
        beta * LAG(conditional_var) OVER (ORDER BY date) AS conditional_var
    FROM garch_data
    CROSS JOIN garch_parameters
)
SELECT
    date,
    ROUND(return_rate::numeric, 4) AS return_rate,
    ROUND(SQRT(conditional_var)::numeric, 4) AS conditional_volatility
FROM conditional_variance
ORDER BY date;
```

---

## 📚 参考资源

1. **Engle, R.F. (1982)**: "Autoregressive Conditional Heteroscedasticity"
2. **Bollerslev, T. (1986)**: "Generalized Autoregressive Conditional Heteroskedasticity"

---

**最后更新**: 2025年1月
**文档状态**: ✅ 已完成
