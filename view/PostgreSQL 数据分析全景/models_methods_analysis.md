# 数据分析数据模型与分析方法：数学严谨性全面分析

> **文档级别**: Stanford Stats 200 / MIT 6.867 数学严谨性标准
> **适用领域**: 数据科学、机器学习、统计分析、商业智能
> **最后更新**: 2025年

---

## 目录

- [数据分析数据模型与分析方法：数学严谨性全面分析](#数据分析数据模型与分析方法数学严谨性全面分析)
  - [目录](#目录)
  - [1. 数据模型理论基础](#1-数据模型理论基础)
    - [1.1 概念模型](#11-概念模型)
      - [1.1.1 ER模型 (Entity-Relationship Model)](#111-er模型-entity-relationship-model)
      - [1.1.2 UML类图形式化](#112-uml类图形式化)
      - [1.1.3 本体模型 (OWL形式化)](#113-本体模型-owl形式化)
    - [1.2 逻辑模型](#12-逻辑模型)
      - [1.2.1 关系模型 (Relational Model)](#121-关系模型-relational-model)
      - [1.2.2 维度模型 (Dimensional Model)](#122-维度模型-dimensional-model)
      - [1.2.3 文档模型 (Document Model)](#123-文档模型-document-model)
      - [1.2.4 图模型 (Graph Model)](#124-图模型-graph-model)
    - [1.3 物理模型](#13-物理模型)
      - [1.3.1 存储结构](#131-存储结构)
      - [1.3.2 索引设计](#132-索引设计)
      - [1.3.3 分区策略](#133-分区策略)
    - [1.4 Data Vault 2.0](#14-data-vault-20)
      - [1.4.1 核心组件](#141-核心组件)
      - [1.4.2 哈希键计算](#142-哈希键计算)
    - [1.5 数据网格 (Data Mesh)](#15-数据网格-data-mesh)
      - [1.5.1 架构原则](#151-架构原则)
      - [1.5.2 数据产品契约](#152-数据产品契约)
  - [2. 描述性分析模型](#2-描述性分析模型)
    - [2.1 汇总统计](#21-汇总统计)
      - [2.1.1 中心趋势度量](#211-中心趋势度量)
      - [2.1.2 离散程度度量](#212-离散程度度量)
      - [2.1.3 分布形态度量](#213-分布形态度量)
    - [2.2 分布分析](#22-分布分析)
      - [2.2.1 正态分布](#221-正态分布)
      - [2.2.2 幂律分布](#222-幂律分布)
      - [2.2.3 泊松分布](#223-泊松分布)
    - [2.3 趋势分析](#23-趋势分析)
      - [2.3.1 时间序列分解](#231-时间序列分解)
      - [2.3.2 移动平均](#232-移动平均)
    - [2.4 对比分析](#24-对比分析)
      - [2.4.1 同期群分析 (Cohort Analysis)](#241-同期群分析-cohort-analysis)
      - [2.4.2 A/B测试](#242-ab测试)
  - [3. 诊断性分析模型](#3-诊断性分析模型)
    - [3.1 根因分析](#31-根因分析)
      - [3.1.1 5 Whys方法](#311-5-whys方法)
      - [3.1.2 鱼骨图 (Ishikawa图)](#312-鱼骨图-ishikawa图)
      - [3.1.3 故障树分析 (FTA)](#313-故障树分析-fta)
    - [3.2 相关性分析](#32-相关性分析)
      - [3.2.1 Pearson相关系数](#321-pearson相关系数)
      - [3.2.2 Spearman秩相关系数](#322-spearman秩相关系数)
      - [3.2.3 Kendall's Tau](#323-kendalls-tau)
    - [3.3 假设检验](#33-假设检验)
      - [3.3.1 t检验](#331-t检验)
      - [3.3.2 卡方检验](#332-卡方检验)
      - [3.3.3 非参数检验](#333-非参数检验)
    - [3.4 方差分析 (ANOVA)](#34-方差分析-anova)
      - [3.4.1 单因素ANOVA](#341-单因素anova)
      - [3.4.2 多因素ANOVA](#342-多因素anova)
      - [3.4.3 重复测量ANOVA](#343-重复测量anova)
  - [4. 预测性分析模型](#4-预测性分析模型)
    - [4.1 回归分析](#41-回归分析)
      - [4.1.1 线性回归](#411-线性回归)
      - [4.1.2 逻辑回归](#412-逻辑回归)
      - [4.1.3 多项式回归](#413-多项式回归)
      - [4.1.4 正则化方法](#414-正则化方法)
    - [4.2 时间序列预测](#42-时间序列预测)
      - [4.2.1 ARIMA模型](#421-arima模型)
      - [4.2.2 SARIMA模型](#422-sarima模型)
      - [4.2.3 Prophet模型](#423-prophet模型)
      - [4.2.4 LSTM时间序列预测](#424-lstm时间序列预测)
    - [4.3 分类算法](#43-分类算法)
      - [4.3.1 决策树](#431-决策树)
      - [4.3.2 随机森林](#432-随机森林)
      - [4.3.3 支持向量机 (SVM)](#433-支持向量机-svm)
      - [4.3.4 朴素贝叶斯](#434-朴素贝叶斯)
    - [4.4 集成学习](#44-集成学习)
      - [4.4.1 Bagging](#441-bagging)
      - [4.4.2 Boosting](#442-boosting)
      - [4.4.3 Stacking](#443-stacking)
    - [4.5 深度学习在数据分析中的应用](#45-深度学习在数据分析中的应用)
      - [4.5.1 卷积神经网络 (CNN)](#451-卷积神经网络-cnn)
      - [4.5.2 循环神经网络 (RNN)](#452-循环神经网络-rnn)
      - [4.5.3 Transformer](#453-transformer)
  - [5. 规范性分析模型](#5-规范性分析模型)
    - [5.1 优化模型](#51-优化模型)
      - [5.1.1 线性规划 (LP)](#511-线性规划-lp)
      - [5.1.2 整数规划](#512-整数规划)
      - [5.1.3 动态规划](#513-动态规划)
    - [5.2 仿真模拟](#52-仿真模拟)
      - [5.2.1 蒙特卡洛模拟](#521-蒙特卡洛模拟)
      - [5.2.2 离散事件仿真](#522-离散事件仿真)
    - [5.3 决策树与决策图](#53-决策树与决策图)
      - [5.3.1 决策树分析](#531-决策树分析)
    - [5.4 强化学习](#54-强化学习)
      - [5.4.1 Q-Learning](#541-q-learning)
      - [5.4.2 策略梯度](#542-策略梯度)
  - [6. 高频经典算法](#6-高频经典算法)
    - [6.1 聚类算法](#61-聚类算法)
      - [6.1.1 K-means聚类](#611-k-means聚类)
      - [6.1.2 层次聚类](#612-层次聚类)
      - [6.1.3 DBSCAN](#613-dbscan)
      - [6.1.4 高斯混合模型 (GMM)](#614-高斯混合模型-gmm)
    - [6.2 降维算法](#62-降维算法)
      - [6.2.1 主成分分析 (PCA)](#621-主成分分析-pca)
      - [6.2.2 线性判别分析 (LDA)](#622-线性判别分析-lda)
      - [6.2.3 t-SNE](#623-t-sne)
      - [6.2.4 UMAP](#624-umap)
    - [6.3 关联规则挖掘](#63-关联规则挖掘)
      - [6.3.1 Apriori算法](#631-apriori算法)
      - [6.3.2 FP-Growth](#632-fp-growth)
    - [6.4 异常检测](#64-异常检测)
      - [6.4.1 统计方法](#641-统计方法)
      - [6.4.2 孤立森林 (Isolation Forest)](#642-孤立森林-isolation-forest)
      - [6.4.3 局部异常因子 (LOF)](#643-局部异常因子-lof)
      - [6.4.4 自编码器异常检测](#644-自编码器异常检测)
  - [7. 因果推断方法](#7-因果推断方法)
    - [7.1 潜在结果框架 (Rubin因果模型)](#71-潜在结果框架-rubin因果模型)
    - [7.2 双重差分 (DID)](#72-双重差分-did)
    - [7.3 工具变量 (IV)](#73-工具变量-iv)
    - [7.4 倾向得分匹配 (PSM)](#74-倾向得分匹配-psm)
    - [7.5 断点回归 (RDD)](#75-断点回归-rdd)
    - [7.6 因果图与do-calculus](#76-因果图与do-calculus)
      - [7.6.1 因果图基础](#761-因果图基础)
      - [7.6.2 do-calculus](#762-do-calculus)
  - [8. 模型选择决策框架](#8-模型选择决策框架)
    - [8.1 模型选择决策树](#81-模型选择决策树)
    - [8.2 模型对比矩阵](#82-模型对比矩阵)
      - [8.2.1 回归模型对比](#821-回归模型对比)
      - [8.2.2 分类模型对比](#822-分类模型对比)
      - [8.2.3 聚类算法对比](#823-聚类算法对比)
      - [8.2.4 因果推断方法对比](#824-因果推断方法对比)
    - [8.3 模型评估指标汇总](#83-模型评估指标汇总)
      - [8.3.1 回归评估](#831-回归评估)
      - [8.3.2 分类评估](#832-分类评估)
      - [8.3.3 聚类评估](#833-聚类评估)
  - [9. 参考文献](#9-参考文献)
    - [经典教材](#经典教材)
    - [数据模型与数据库](#数据模型与数据库)
    - [因果推断](#因果推断)
    - [时间序列](#时间序列)
    - [优化与决策](#优化与决策)
    - [聚类与降维](#聚类与降维)
    - [集成学习](#集成学习)
  - [附录A: 数学符号表](#附录a-数学符号表)
  - [附录B: 算法复杂度速查表](#附录b-算法复杂度速查表)

---

## 1. 数据模型理论基础

### 1.1 概念模型

#### 1.1.1 ER模型 (Entity-Relationship Model)

**数学定义**:

一个ER模型可以形式化定义为五元组：

$$\mathcal{E} = (E, R, A, \text{dom}, \text{card})$$

其中：

- $E = \{e_1, e_2, ..., e_n\}$：实体类型集合
- $R \subseteq E \times E$：关系类型集合
- $A$：属性集合
- $\text{dom}: A \rightarrow \mathcal{D}$：属性到域的映射
- $\text{card}: R \rightarrow \mathbb{N} \times \mathbb{N}$：基数约束映射

**基数约束**:

对于关系 $r \in R$ 连接实体 $e_i$ 和 $e_j$：

$$\text{card}(r) = (\min_i, \max_i, \min_j, \max_j)$$

常见基数类型：

- 一对一 (1:1): $\max_i = \max_j = 1$
- 一对多 (1:N): $\max_i = 1, \max_j = N$
- 多对多 (M:N): $\max_i = M, \max_j = N$

**规范化形式**:

**定理 1.1** (ER模型到关系模型的转换定理)

给定ER模型 $\mathcal{E}$，存在算法 $T$ 将其转换为关系模式集合 $\mathcal{R}$，使得：

$$T: \mathcal{E} \rightarrow \mathcal{R} = \{R_1, R_2, ..., R_m\}$$

转换规则：

1. 每个实体类型 $e \in E$ 转换为关系模式 $R_e$
2. 每个多对多关系转换为独立关系模式
3. 一对多关系通过外键实现

**时间复杂度**: $O(|E| + |R| + |A|)$

---

#### 1.1.2 UML类图形式化

**类定义**:

$$\text{Class} = (N, P, M, \text{sup})$$

其中：

- $N$: 类名
- $P = \{(n_i, t_i, v_i)\}$: 属性集合（名称、类型、可见性）
- $M = \{(n_j, P_j, r_j)\}$: 方法集合
- $\text{sup} \subseteq \mathcal{C}$: 父类集合

**继承关系**:

给定继承层次 $\mathcal{H} = (\mathcal{C}, \preceq)$，其中 $\preceq$ 是偏序关系：

$$c_i \preceq c_j \iff c_i \text{ 继承自 } c_j$$

**Liskov替换原则 (LSP)**:

**定理 1.2** (Liskov, 1994)

对于类型 $S$ 和 $T$，若 $S \preceq T$，则对于所有性质 $P(x)$：

$$\forall x \in T: P(x) \Rightarrow \forall y \in S: P(y)$$

---

#### 1.1.3 本体模型 (OWL形式化)

**描述逻辑基础**:

OWL基于描述逻辑 $\mathcal{ALC}$ (Attributive Language with Complements)：

**语法**:

- 概念 (Concepts): $C, D ::= A \mid \top \mid \bot \mid \neg C \mid C \sqcap D \mid C \sqcup D \mid \forall R.C \mid \exists R.C$
- 角色 (Roles): $R$
- 个体 (Individuals): $a, b, c$

**语义**:

解释 $\mathcal{I} = (\Delta^\mathcal{I}, \cdot^\mathcal{I})$：

- $\Delta^\mathcal{I}$: 非空域
- $A^\mathcal{I} \subseteq \Delta^\mathcal{I}$
- $R^\mathcal{I} \subseteq \Delta^\mathcal{I} \times \Delta^\mathcal{I}$
- $a^\mathcal{I} \in \Delta^\mathcal{I}$

**公理**:

- 概念包含: $C \sqsubseteq D$
- 概念等价: $C \equiv D$
- 角色包含: $R \sqsubseteq S$

**推理复杂度**:

| 描述逻辑 | 概念可满足性 | TBox一致性 |
|---------|-------------|-----------|
| $\mathcal{ALC}$ | PSPACE-complete | EXPTIME-complete |
| $\mathcal{SHOIN}$ (OWL DL) | NEXPTIME-complete | NEXPTIME-complete |
| $\mathcal{SROIQ}$ (OWL 2) | 2NEXPTIME-complete | 2NEXPTIME-complete |

---

### 1.2 逻辑模型

#### 1.2.1 关系模型 (Relational Model)

**形式化定义** (Codd, 1970):

**定义 1.1** (关系)

给定属性集合 $U = \{A_1, A_2, ..., A_n\}$ 和对应域 $\mathcal{D} = \{D_1, D_2, ..., D_n\}$，关系 $R$ 定义为：

$$R \subseteq D_1 \times D_2 \times ... \times D_n$$

即 $R$ 是笛卡尔积的子集，每个元素称为**元组** (tuple)。

**关系代数**:

关系代数是六元组 $\mathcal{A} = (\mathcal{R}, \sigma, \pi, \bowtie, \cup, -, \rho)$：

| 操作 | 符号 | 定义 | 复杂度 |
|-----|------|------|--------|
| 选择 | $\sigma_\theta(R)$ | $\{t \in R : \theta(t)\}$ | $O(\|R\|)$ |
| 投影 | $\pi_A(R)$ | $\{t[A] : t \in R\}$ | $O(\|R\| \log \|R\|)$ |
| 连接 | $R \bowtie_\theta S$ | $\{(r,s) : r \in R, s \in S, \theta(r,s)\}$ | $O(\|R\| \cdot \|S\|)$ |
| 并集 | $R \cup S$ | $\{t : t \in R \lor t \in S\}$ | $O(\|R\| + \|S\|)$ |
| 差集 | $R - S$ | $\{t : t \in R \land t \notin S\}$ | $O(\|R\| \cdot \|S\|)$ |
| 重命名 | $\rho_{S/B}(R)$ | 重命名属性 | $O(1)$ |

**定理 1.3** (关系代数完备性)

关系代数在表达能力上等价于一阶谓词逻辑中的安全表达式集合。

**证明概要**:

- 方向1: 每个关系代数表达式可转换为等价的安全关系演算表达式
- 方向2: 每个安全关系演算表达式可转换为等价的关系代数表达式

**范式理论**:

**定义 1.2** (函数依赖)

对于关系 $R$ 和属性子集 $X, Y \subseteq U$，函数依赖 $X \rightarrow Y$ 定义为：

$$\forall t_1, t_2 \in R: t_1[X] = t_2[X] \Rightarrow t_1[Y] = t_2[Y]$$

**Armstrong公理**:

**定理 1.4** (Armstrong, 1974)

函数依赖推理的完备公理系统：

1. **自反律**: 若 $Y \subseteq X$，则 $X \rightarrow Y$
2. **增广律**: 若 $X \rightarrow Y$，则 $XZ \rightarrow YZ$
3. **传递律**: 若 $X \rightarrow Y$ 且 $Y \rightarrow Z$，则 $X \rightarrow Z$

**推导规则**:

- 合并律: $X \rightarrow Y, X \rightarrow Z \vdash X \rightarrow YZ$
- 伪传递律: $X \rightarrow Y, WY \rightarrow Z \vdash WX \rightarrow Z$
- 分解律: $X \rightarrow YZ \vdash X \rightarrow Y, X \rightarrow Z$

**范式定义**:

| 范式 | 定义 | 消除的异常 |
|-----|------|-----------|
| 1NF | 所有属性值原子 | 重复组 |
| 2NF | 1NF + 非主属性完全依赖于候选键 | 部分依赖 |
| 3NF | 2NF + 无传递依赖 | 传递依赖 |
| BCNF | $\forall X \rightarrow Y: X$ 是超键 | 所有异常 |
| 4NF | BCNF + 无多值依赖 | 多值依赖 |
| 5NF | 4NF + 无连接依赖 | 连接依赖 |

**BCNF分解算法**:

```
算法: BCNF_Decomposition(R, F)
输入: 关系R, 函数依赖集F
输出: BCNF分解 {R₁, R₂, ..., Rₙ}

1. 如果R满足BCNF，返回{R}
2. 找到违反BCNF的X → Y（X不是超键）
3. 分解为: R₁ = XY, R₂ = R - Y
4. 递归分解R₁和R₂
5. 返回所有分解结果

时间复杂度: O(|F|² · |U|)
```

---

#### 1.2.2 维度模型 (Dimensional Model)

**星型模式形式化**:

**定义 1.3** (星型模式)

星型模式 $\mathcal{S}$ 定义为二元组：

$$\mathcal{S} = (F, \mathcal{D})$$

其中：

- $F$：事实表，包含度量值和外键
- $\mathcal{D} = \{D_1, D_2, ..., D_n\}$：维度表集合

**事实表结构**:

$$F = (K_F, \{FK_{D_i}\}_{i=1}^n, M, T)$$

- $K_F$：事实表主键（通常是代理键）
- $FK_{D_i}$：指向维度表 $D_i$ 的外键
- $M = \{m_1, m_2, ..., m_k\}$：可加性度量集合
- $T$：时间维度键

**维度表结构**:

$$D_i = (K_{D_i}, A_i, H_i)$$

- $K_{D_i}$：维度代理键
- $A_i = \{a_1, a_2, ..., a_p\}$：描述属性
- $H_i$：层次结构

**层次结构形式化**:

维度层次是偏序集 $(L, \preceq)$：

$$L = \{l_1, l_2, ..., l_h\}, \quad l_i \preceq l_j \iff l_i \text{ 比 } l_j \text{ 更详细}$$

例如时间维度：日 $\preceq$ 周 $\preceq$ 月 $\preceq$ 季 $\preceq$ 年

**上卷 (Roll-up) 操作**:

给定事实表 $F$ 和层次 $l_i \preceq l_j$：

$$\text{Roll-up}_{l_i \rightarrow l_j}(F) = \gamma_{l_j, \text{SUM}(M)}(F \bowtie D_{l_i})$$

其中 $\gamma$ 是分组聚合操作。

**下钻 (Drill-down) 操作**:

$$\text{Drill-down}_{l_j \rightarrow l_i}(A) = A \bowtie D_{l_i}$$

**雪花模式**:

雪花模式是星型模式的规范化形式：

$$\mathcal{SN} = (F, \mathcal{D}, \mathcal{S})$$

其中 $\mathcal{S}$ 是维度表之间的规范化关系集合。

**存储效率比较**:

| 模式 | 冗余度 | 查询性能 | 维护复杂度 |
|-----|--------|---------|-----------|
| 星型 | 高 | 优 | 低 |
| 雪花 | 低 | 良 | 高 |

---

#### 1.2.3 文档模型 (Document Model)

**JSON Schema形式化**:

文档模式 $S$ 定义为：

$$S = (T, P, C, R)$$

- $T$: 类型系统（object, array, string, number, boolean, null）
- $P$: 属性定义集合
- $C$: 约束条件
- $R$: 引用关系

**BSON存储格式**:

BSON文档是键值对的有序列表：

$$\text{Document} = [(k_1, v_1), (k_2, v_2), ..., (k_n, v_n)]$$

其中值类型标签占用1字节，支持高效遍历。

**嵌套文档查询复杂度**:

对于嵌套深度为 $d$ 的文档，路径查询复杂度：

$$T_{query}(d) = O(d \cdot \log n)$$

使用复合索引可优化至 $O(\log n)$。

---

#### 1.2.4 图模型 (Graph Model)

**属性图模型**:

属性图 $G$ 定义为四元组：

$$G = (V, E, \lambda, \mu)$$

- $V$: 顶点集合
- $E \subseteq V \times V$: 边集合
- $\lambda: (V \cup E) \times K \rightarrow \mathcal{D}$: 标签/属性函数
- $\mu: E \rightarrow L$: 边类型函数

**邻接矩阵表示**:

$$A_{ij} = \begin{cases} 1 & \text{if } (v_i, v_j) \in E \\ 0 & \text{otherwise} \end{cases}$$

**拉普拉斯矩阵**:

$$L = D - A$$

其中 $D$ 是度矩阵，$D_{ii} = \sum_j A_{ij}$

**图查询语言 (Cypher)**:

Cypher查询可转换为扩展关系代数：

$$\text{MATCH } (a)-[r]->(b) \text{ WHERE } \theta \text{ RETURN } \phi$$

等价于：

$$\pi_\phi(\sigma_\theta(V \bowtie_{r} E \bowtie V))$$

---

### 1.3 物理模型

#### 1.3.1 存储结构

**行存储 vs 列存储**:

**行存储布局**:

对于关系 $R$ 有 $n$ 个元组，每个元组 $m$ 个属性：

$$\text{Layout}_{row} = [t_1, t_2, ..., t_n] = [(a_{11}, ..., a_{1m}), ..., (a_{n1}, ..., a_{nm})]$$

**列存储布局**:

$$\text{Layout}_{col} = [c_1, c_2, ..., c_m] = [(a_{11}, ..., a_{n1}), ..., (a_{1m}, ..., a_{nm})]$$

**I/O复杂度比较**:

| 操作 | 行存储 | 列存储 |
|-----|--------|--------|
| 点查询 | $O(1)$ | $O(m)$ |
| 全表扫描 | $O(n \cdot m)$ | $O(n \cdot m)$ |
| 投影查询 | $O(n \cdot m)$ | $O(n \cdot k)$ |
| 聚合查询 | $O(n \cdot m)$ | $O(n)$ |

其中 $k$ 是投影属性数，$k \ll m$。

---

#### 1.3.2 索引设计

**B+树索引**:

**定义 1.4** (B+树)

阶为 $d$ 的B+树满足：

1. 每个内部节点有 $[d, 2d]$ 个子节点
2. 所有叶子节点在同一层
3. 叶子节点通过指针链接

**查询复杂度**:

$$T_{search} = O(\log_d N) = O(\frac{\log N}{\log d})$$

其中 $N$ 是记录数，$d$ 是分支因子。

**空间复杂度**:

$$S_{B+tree} = O(N \cdot (k + p))$$

其中 $k$ 是键大小，$p$ 是指针大小。

**倒排索引**:

对于文档集合 $D = \{d_1, d_2, ..., d_n\}$ 和词项 $t$：

$$\text{Inverted}(t) = \{(d_i, f_{t,i}, [p_1, p_2, ...]) : t \in d_i\}$$

其中 $f_{t,i}$ 是词频，$[p_1, p_2, ...]$ 是位置列表。

**位图索引**:

对于属性 $A$ 有 $m$ 个不同值：

$$\text{Bitmap}(a_j) = [b_1, b_2, ..., b_n], \quad b_i = \begin{cases} 1 & \text{if } t_i[A] = a_j \\ 0 & \text{otherwise} \end{cases}$$

位图操作复杂度（使用位运算）：

- AND/OR: $O(n/64)$ 字操作
- NOT: $O(n/64)$

---

#### 1.3.3 分区策略

**范围分区**:

对于分区键 $K$ 和范围边界 $\{b_1, b_2, ..., b_p\}$：

$$P_i = \{t \in R : b_{i-1} \leq t[K] < b_i\}$$

**哈希分区**:

$$P_i = \{t \in R : h(t[K]) \mod p = i\}$$

其中 $h$ 是哈希函数，$p$ 是分区数。

**列表分区**:

$$P_i = \{t \in R : t[K] \in L_i\}$$

其中 $L_i$ 是值列表。

**分区剪枝效率**:

对于选择条件 $\theta$，可剪枝分区比例：

$$\text{PruneRatio} = 1 - \frac{|\{P_i : \theta \cap P_i \neq \emptyset\}|}{p}$$

---

### 1.4 Data Vault 2.0

#### 1.4.1 核心组件

**Hub（中心表）**:

$$\text{Hub}_B = (HK_B, BK_B, LDTS, RSRC)$$

- $HK_B$: 哈希键（业务键的哈希）
- $BK_B$: 业务键
- $LDTS$: 加载时间戳
- $RSRC$: 记录源

**Link（链接表）**:

$$\text{Link}_{AB} = (HK_L, HK_A, HK_B, LDTS, RSRC)$$

连接两个Hub的关联关系。

**Satellite（卫星表）**:

$$\text{Sat}_B = (HK_B, LDTS, \{a_1, a_2, ..., a_n\}, RSRC, HASHDIFF)$$

存储Hub或Link的描述属性。

#### 1.4.2 哈希键计算

**MD5哈希**:

$$HK_B = \text{MD5}(BK_B) \in \{0, 1\}^{128}$$

**哈希冲突概率**:

对于 $n$ 个键，$m = 2^{128}$ 个哈希值：

$$P(\text{collision}) \approx 1 - e^{-n(n-1)/(2m)} \approx \frac{n^2}{2m}$$

对于 $n = 10^{12}$ 个键：

$$P \approx \frac{10^{24}}{2 \cdot 2^{128}} \approx 10^{-15}$$

可忽略不计。

---

### 1.5 数据网格 (Data Mesh)

#### 1.5.1 架构原则

数据网格是分布式数据架构，基于四个核心原则：

1. **领域所有权**: 数据产品由领域团队拥有
2. **数据即产品**: 数据作为一等产品
3. **自助数据平台**: 基础设施即平台
4. **联邦计算治理**: 去中心化治理

#### 1.5.2 数据产品契约

数据产品 $DP$ 定义为：

$$DP = (S, Q, M, O, SLI)$$

- $S$: 输出端口模式（Schema）
- $Q$: 质量指标
- $M$: 元数据
- $O$: 所有权信息
- $SLI$: 服务水平指标

**SLO定义**:

$$\text{SLO}_{availability} = P(\text{data accessible}) \geq 0.999$$

$$\text{SLO}_{freshness} = T_{data} - T_{event} \leq 5\text{min}$$

---

## 2. 描述性分析模型

### 2.1 汇总统计

#### 2.1.1 中心趋势度量

**样本均值**:

对于样本 $X = \{x_1, x_2, ..., x_n\}$：

$$\bar{x} = \frac{1}{n}\sum_{i=1}^n x_i$$

**性质**:

**定理 2.1** (样本均值的最优性)

样本均值 $\bar{x}$ 最小化平方误差和：

$$\bar{x} = \arg\min_c \sum_{i=1}^n (x_i - c)^2$$

**证明**:

令 $f(c) = \sum_{i=1}^n (x_i - c)^2$，求导：

$$\frac{df}{dc} = -2\sum_{i=1}^n (x_i - c) = 0$$

$$\sum_{i=1}^n x_i - nc = 0 \Rightarrow c = \frac{1}{n}\sum_{i=1}^n x_i = \bar{x}$$

二阶导数 $\frac{d^2f}{dc^2} = 2n > 0$，确认是最小值。

**加权均值**:

$$\bar{x}_w = \frac{\sum_{i=1}^n w_i x_i}{\sum_{i=1}^n w_i}$$

**中位数**:

$$\text{median}(X) = \begin{cases} x_{(\frac{n+1}{2})} & n \text{ 奇数} \\ \frac{1}{2}(x_{(\frac{n}{2})} + x_{(\frac{n}{2}+1)}) & n \text{ 偶数} \end{cases}$$

**定理 2.2** (中位数的最优性)

中位数最小化绝对误差和：

$$\text{median}(X) = \arg\min_c \sum_{i=1}^n |x_i - c|$$

**众数**:

$$\text{mode}(X) = \arg\max_v \sum_{i=1}^n \mathbb{1}[x_i = v]$$

---

#### 2.1.2 离散程度度量

**样本方差**:

$$s^2 = \frac{1}{n-1}\sum_{i=1}^n (x_i - \bar{x})^2$$

使用 $n-1$ 而非 $n$ 是为了得到**无偏估计**。

**定理 2.3** (样本方差的无偏性)

$$E[s^2] = \sigma^2$$

**证明**:

$$E\left[\sum_{i=1}^n (x_i - \bar{x})^2\right] = E\left[\sum_{i=1}^n x_i^2 - n\bar{x}^2\right]$$

$$= nE[x_i^2] - nE[\bar{x}^2]$$

$$= n(\sigma^2 + \mu^2) - n(\frac{\sigma^2}{n} + \mu^2)$$

$$= n\sigma^2 - \sigma^2 = (n-1)\sigma^2$$

因此：

$$E\left[\frac{1}{n-1}\sum_{i=1}^n (x_i - \bar{x})^2\right] = \sigma^2$$

**标准差**:

$$s = \sqrt{s^2}$$

**变异系数**:

$$CV = \frac{s}{\bar{x}} \times 100\%$$

**四分位距 (IQR)**:

$$IQR = Q_3 - Q_1$$

其中 $Q_1$ 是第25百分位数，$Q_3$ 是第75百分位数。

---

#### 2.1.3 分布形态度量

**偏度 (Skewness)**:

$$g_1 = \frac{\frac{1}{n}\sum_{i=1}^n (x_i - \bar{x})^3}{\left(\frac{1}{n}\sum_{i=1}^n (x_i - \bar{x})^2\right)^{3/2}}$$

- $g_1 > 0$: 右偏（正偏）
- $g_1 < 0$: 左偏（负偏）
- $g_1 = 0$: 对称

**峰度 (Kurtosis)**:

$$g_2 = \frac{\frac{1}{n}\sum_{i=1}^n (x_i - \bar{x})^4}{\left(\frac{1}{n}\sum_{i=1}^n (x_i - \bar{x})^2\right)^2} - 3$$

- $g_2 > 0$: 尖峰（leptokurtic）
- $g_2 < 0$: 平峰（platykurtic）
- $g_2 = 0$: 正态峰（mesokurtic）

**Jarque-Bera检验**:

$$JB = \frac{n}{6}\left(g_1^2 + \frac{g_2^2}{4}\right) \xrightarrow{d} \chi^2_2$$

---

### 2.2 分布分析

#### 2.2.1 正态分布

**概率密度函数**:

$$f(x; \mu, \sigma) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)$$

**标准正态分布** ($Z \sim N(0, 1)$):

$$\phi(z) = \frac{1}{\sqrt{2\pi}} e^{-z^2/2}$$

**累积分布函数**:

$$\Phi(z) = \frac{1}{2}\left[1 + \text{erf}\left(\frac{z}{\sqrt{2}}\right)\right]$$

**性质**:

**定理 2.4** (正态分布的线性变换)

若 $X \sim N(\mu, \sigma^2)$，则对于 $a, b \in \mathbb{R}$：

$$Y = aX + b \sim N(a\mu + b, a^2\sigma^2)$$

**中心极限定理**:

**定理 2.5** (Lindeberg-Lévy CLT)

设 $\{X_1, X_2, ...\}$ 是i.i.d.随机变量，$E[X_i] = \mu$，$\text{Var}(X_i) = \sigma^2 < \infty$，则：

$$\sqrt{n}(\bar{X}_n - \mu) \xrightarrow{d} N(0, \sigma^2)$$

等价地：

$$\frac{\bar{X}_n - \mu}{\sigma/\sqrt{n}} \xrightarrow{d} N(0, 1)$$

---

#### 2.2.2 幂律分布

**概率密度函数**:

$$
f(x; \alpha, x_{min}) =
\frac{\alpha - 1}{x_{min}} \left(\frac{x}{x_{min}}\right)^{-\alpha}, \quad x \geq x_{min}
$$

其中 $\alpha > 1$ 是幂指数。

**互补累积分布函数 (CCDF)**:

$$P(X > x) = \left(\frac{x}{x_{min}}\right)^{-(
\alpha - 1)}$$

**对数-对数线性性**:

$$\log P(X > x) = -(\alpha - 1)\log x + (\alpha - 1)\log x_{min}$$

**矩的存在性**:

**定理 2.6** (幂律分布的矩)

对于 $X \sim \text{PowerLaw}(\alpha, x_{min})$：

$$
E[X^k] =
\begin{cases} \frac{\alpha - 1}{\alpha - 1 - k} x_{min}^k & k < \alpha - 1 \\ \infty & k \geq \alpha - 1 \end{cases}
$$

**Hill估计量**:

对于顺序统计量 $x_{(1)} \geq x_{(2)} \geq ... \geq x_{(n)}$：

$$\hat{\alpha}_{Hill} = 1 + \left(\frac{1}{k}\sum_{i=1}^k \log\frac{x_{(i)}}{x_{(k+1)}}\right)^{-1}$$

---

#### 2.2.3 泊松分布

**概率质量函数**:

$$P(X = k; \lambda) = \frac{\lambda^k e^{-\lambda}}{k!}, \quad k = 0, 1, 2, ...$$

**性质**:

- 均值: $E[X] = \lambda$
- 方差: $\text{Var}(X) = \lambda$
- 众数: $\lfloor \lambda \rfloor$ 或 $\lfloor \lambda \rfloor - 1$

**可加性**:

**定理 2.7** (泊松分布的可加性)

若 $X_1 \sim \text{Pois}(\lambda_1)$，$X_2 \sim \text{Pois}(\lambda_2)$，且独立，则：

$$X_1 + X_2 \sim \text{Pois}(\lambda_1 + \lambda_2)$$

**复合泊松过程**:

$$S = \sum_{i=1}^N Y_i$$

其中 $N \sim \text{Pois}(\lambda)$，$Y_i$ i.i.d. 且与 $N$ 独立。

---

### 2.3 趋势分析

#### 2.3.1 时间序列分解

**加法模型**:

$$Y_t = T_t + S_t + C_t + \varepsilon_t$$

**乘法模型**:

$$Y_t = T_t \times S_t \times C_t \times \varepsilon_t$$

其中：
- $T_t$: 趋势成分
- $S_t$: 季节性成分
- $C_t$: 周期性成分
- $\varepsilon_t$: 随机成分

**STL分解算法**:

```
算法: STL(Y, n_p, n_s, n_l, n_t)
输入: 时间序列Y, 周期n_p, 平滑参数
输出: T, S, R (趋势、季节、残差)

1. 初始化: T⁽⁰⁾ = 0
2. for k = 1, 2, ... until convergence:
   a. 去趋势: Y - T⁽ᵏ⁻¹⁾
   b. 季节子序列平滑 (loess)
   c. 季节成分去趋势: S⁽ᵏ⁾
   d. 去季节: Y - S⁽ᵏ⁾
   e. 趋势平滑 (loess): T⁽ᵏ⁾
3. 残差: R = Y - T - S

复杂度: O(n · iter)
```

---

#### 2.3.2 移动平均

**简单移动平均 (SMA)**:

$$\text{SMA}_t^{(k)} = \frac{1}{k}\sum_{i=0}^{k-1} y_{t-i}$$

**指数移动平均 (EMA)**:

$$\text{EMA}_t = \alpha y_t + (1-\alpha)\text{EMA}_{t-1}$$

其中 $\alpha \in (0, 1)$ 是平滑因子。

**等价形式**:

$$\text{EMA}_t = \sum_{i=0}^{\infty} \alpha(1-\alpha)^i y_{t-i}$$

**有效窗口大小**:

$$k_{eff} = \frac{2 - \alpha}{\alpha} \approx \frac{2}{\alpha}$$

**Holt-Winters方法**:

**水平更新**:

$$L_t = \alpha y_t + (1-\alpha)(L_{t-1} + T_{t-1})$$

**趋势更新**:

$$T_t = \beta(L_t - L_{t-1}) + (1-\beta)T_{t-1}$$

**季节更新**:

$$S_t = \gamma(y_t - L_t) + (1-\gamma)S_{t-m}$$

**预测**:

$$\hat{y}_{t+h} = L_t + hT_t + S_{t-m+h_m}$$

---

### 2.4 对比分析

#### 2.4.1 同期群分析 (Cohort Analysis)

**同期群定义**:

同期群 $C_t$ 是在时间 $t$ 具有共同特征的用户集合：

$$C_t = \{u : \text{acquisition}(u) = t\}$$

**留存矩阵**:

$$R_{t,d} = \frac{|C_t \cap A_{t+d}|}{|C_t|}$$

其中 $A_{t+d}$ 是在 $t+d$ 时刻活跃的用户集合。

**同期群分析表**:

| 同期群 | 第0期 | 第1期 | 第2期 | ... | 第n期 |
|-------|-------|-------|-------|-----|-------|
| 2023-01 | 100% | 45% | 30% | ... | 12% |
| 2023-02 | 100% | 48% | 32% | ... | - |
| ... | ... | ... | ... | ... | ... |

---

#### 2.4.2 A/B测试

**统计框架**:

设对照组 $A$ 和处理组 $B$：

$$H_0: \mu_A = \mu_B \quad \text{vs} \quad H_1: \mu_A \neq \mu_B$$

**检验统计量**:

$$t = \frac{\bar{X}_A - \bar{X}_B}{\sqrt{\frac{s_A^2}{n_A} + \frac{s_B^2}{n_B}}} \approx t_{df}$$

**样本量计算**:

$$n = \frac{2\sigma^2(Z_{1-\alpha/2} + Z_{1-\beta})^2}{\delta^2}$$

其中：
- $\alpha$: 显著性水平
- $\beta$: 第二类错误概率
- $\delta$: 最小可检测效应

**功效分析**:

$$\text{Power} = P(\text{reject } H_0 | H_1 \text{ true}) = 1 - \beta$$

**多重检验校正**:

Bonferroni校正：

$$\alpha_{adj} = \frac{\alpha}{m}$$

其中 $m$ 是检验次数。

**False Discovery Rate (FDR)**:

$$\text{FDR} = E\left[\frac{V}{R}\right]$$

其中 $V$ 是错误拒绝数，$R$ 是总拒绝数。

Benjamini-Hochberg程序：

1. 排序p值: $p_{(1)} \leq p_{(2)} \leq ... \leq p_{(m)}$
2. 找到最大 $k$: $p_{(k)} \leq \frac{k}{m}\alpha$
3. 拒绝 $H_{(1)}, ..., H_{(k)}$

---

## 3. 诊断性分析模型

### 3.1 根因分析

#### 3.1.1 5 Whys方法

**形式化**:

设问题为 $P$，根因为 $R$，中间原因为 $\{C_1, C_2, ..., C_n\}$：

$$P \xrightarrow{why?} C_1 \xrightarrow{why?} C_2 \xrightarrow{why?} ... \xrightarrow{why?} R$$

**收敛条件**:

当 $C_k$ 满足以下条件时停止：
- $C_k$ 是系统根本原因
- $C_k$ 超出控制范围
- 进一步追问无意义

---

#### 3.1.2 鱼骨图 (Ishikawa图)

**结构形式化**:

$$\text{Effect} = f(\text{People}, \text{Process}, \text{Equipment}, \text{Materials}, \text{Environment}, \text{Measurement})$$

每个类别 $C_i$ 包含子原因 $\{c_{i1}, c_{i2}, ...\}$：

$$C_i = \bigvee_j c_{ij}$$

**根本原因识别**:

使用加权评分：

$$\text{Score}(c) = \sum_k w_k \cdot \text{rating}_k(c)$$

---

#### 3.1.3 故障树分析 (FTA)

**逻辑门形式化**:

**与门 (AND)**:

$$T = X_1 \land X_2 \land ... \land X_n$$

$$P(T) = \prod_{i=1}^n P(X_i)$$

**或门 (OR)**:

$$T = X_1 \lor X_2 \lor ... \lor X_n$$

$$P(T) = 1 - \prod_{i=1}^n (1 - P(X_i))$$

**最小割集**:

割集 $C$ 是基本事件集合，使得：

$$\bigwedge_{X \in C} X \Rightarrow T$$

最小割集是不含真子集割集的割集。

**重要度度量**:

**Birnbaum重要度**:

$$I_B(X_i) = P(T | X_i = 1) - P(T | X_i = 0)$$

**Fussell-Vesely重要度**:

$$I_{FV}(X_i) = \frac{P(\bigcup_{C: X_i \in C} C)}{P(T)}$$

---

### 3.2 相关性分析

#### 3.2.1 Pearson相关系数

**定义**:

$$
\rho_{X,Y} = \frac{\text{Cov}(X,Y)}{\sigma_X \sigma_Y} = \frac{E[(X-\mu_X)(Y-\mu_Y)]}{\sqrt{E[(X-\mu_X)^2]E[(Y-\mu_Y)^2]}}
$$

**样本估计**:

$$
r =
\frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^n (x_i - \bar{x})^2 \sum_{i=1}^n (y_i - \bar{y})^2}}
$$

**性质**:

**定理 3.1** (Pearson相关系数的性质)

1. $-1 \leq \rho_{X,Y} \leq 1$
2. $\rho_{X,Y} = 1 \iff Y = aX + b$ ($a > 0$)
3. $\rho_{X,Y} = -1 \iff Y = aX + b$ ($a < 0$)
4. $\rho_{X,Y} = 0$ 不蕴含独立性

**证明** (性质1):

由Cauchy-Schwarz不等式：

$$|E[(X-\mu_X)(Y-\mu_Y)]| \leq \sqrt{E[(X-\mu_X)^2]E[(Y-\mu_Y)^2]}$$

因此 $|\rho_{X,Y}| \leq 1$。

**显著性检验**:

$$t = \frac{r\sqrt{n-2}}{\sqrt{1-r^2}} \sim t_{n-2}$$

**Fisher Z变换**:

$$
z = \frac{1}{2}\ln\left(\frac{1+r}{1-r}\right) \approx N\left(\frac{1}{2}\ln\left(\frac{1+\rho}{1-\rho}\right), \frac{1}{n-3}\right)
$$

---

#### 3.2.2 Spearman秩相关系数

**定义**:

$$
\rho_s = \frac{\sum_{i=1}^n (R_i - \bar{R})(S_i - \bar{S})}{\sqrt{\sum_{i=1}^n (R_i - \bar{R})^2 \sum_{i=1}^n (S_i - \bar{S})^2}}
$$

其中 $R_i = \text{rank}(x_i)$，$S_i = \text{rank}(y_i)$。

**简化公式** (无结时):

$$\rho_s = 1 - \frac{6\sum_{i=1}^n d_i^2}{n(n^2-1)}$$

其中 $d_i = R_i - S_i$。

**性质**:
- 对单调变换不变
- 度量单调关系强度
- 对异常值稳健

---

#### 3.2.3 Kendall's Tau

**定义**:

$$\tau = \frac{n_c - n_d}{\binom{n}{2}} = \frac{2(n_c - n_d)}{n(n-1)}$$

其中：
- $n_c$: 一致对 (concordant pairs) 数量
- $n_d$: 不一致对 (discordant pairs) 数量

**一致对定义**:

$$(i, j) \text{ 一致} \iff (x_i - x_j)(y_i - y_j) > 0$$

**方差** (大样本):

$$\text{Var}(\tau) \approx \frac{2(2n+5)}{9n(n-1)}$$

---

### 3.3 假设检验

#### 3.3.1 t检验

**单样本t检验**:

$$H_0: \mu = \mu_0 \quad \text{vs} \quad H_1: \mu \neq \mu_0$$

**检验统计量**:

$$t = \frac{\bar{X} - \mu_0}{s/\sqrt{n}} \sim t_{n-1}$$

**两独立样本t检验**:

**等方差假设**:

$$t = \frac{\bar{X}_1 - \bar{X}_2}{s_p\sqrt{\frac{1}{n_1} + \frac{1}{n_2}}} \sim t_{n_1+n_2-2}$$

其中合并方差：

$$s_p^2 = \frac{(n_1-1)s_1^2 + (n_2-1)s_2^2}{n_1+n_2-2}$$

**Welch's t检验** (不等方差):

$$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}} \sim t_{df}$$

其中自由度：

$$df = \frac{\left(\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}\right)^2}{\frac{(s_1^2/n_1)^2}{n_1-1} + \frac{(s_2^2/n_2)^2}{n_2-1}}$$

**配对t检验**:

$$t = \frac{\bar{D}}{s_D/\sqrt{n}} \sim t_{n-1}$$

其中 $D_i = X_{1i} - X_{2i}$。

---

#### 3.3.2 卡方检验

**拟合优度检验**:

$$H_0: P(X = i) = p_i, \quad i = 1, 2, ..., k$$

**检验统计量**:

$$\chi^2 = \sum_{i=1}^k \frac{(O_i - E_i)^2}{E_i} \xrightarrow{d} \chi^2_{k-1}$$

其中 $O_i$ 是观测频数，$E_i = np_i$ 是期望频数。

**独立性检验**:

对于列联表：

| | $B_1$ | $B_2$ | ... | 总计 |
|---|-------|-------|-----|------|
| $A_1$ | $n_{11}$ | $n_{12}$ | ... | $n_{1\cdot}$ |
| $A_2$ | $n_{21}$ | $n_{22}$ | ... | $n_{2\cdot}$ |
| ... | ... | ... | ... | ... |
| 总计 | $n_{\cdot 1}$ | $n_{\cdot 2}$ | ... | $n$ |

期望频数：

$$E_{ij} = \frac{n_{i\cdot} \cdot n_{\cdot j}}{n}$$

**检验统计量**:

$$\chi^2 = \sum_{i=1}^r \sum_{j=1}^c \frac{(n_{ij} - E_{ij})^2}{E_{ij}} \sim \chi^2_{(r-1)(c-1)}$$

**Yates连续性校正** (2×2表):

$$\chi^2_{corrected} = \sum_{i,j} \frac{(|n_{ij} - E_{ij}| - 0.5)^2}{E_{ij}}$$

---

#### 3.3.3 非参数检验

**Mann-Whitney U检验**:

$$U = n_1n_2 + \frac{n_1(n_1+1)}{2} - R_1$$

其中 $R_1$ 是第一组的秩和。

**大样本近似**:

$$Z = \frac{U - \mu_U}{\sigma_U} \approx N(0, 1)$$

其中：

$$\mu_U = \frac{n_1n_2}{2}, \quad \sigma_U = \sqrt{\frac{n_1n_2(n_1+n_2+1)}{12}}$$

**Kolmogorov-Smirnov检验**:

$$D_n = \sup_x |F_n(x) - F_0(x)|$$

其中 $F_n$ 是经验分布函数，$F_0$ 是理论分布函数。

**渐近分布**:

$$\lim_{n\to\infty} P(\sqrt{n}D_n \leq x) = 1 - 2\sum_{k=1}^{\infty} (-1)^{k-1}e^{-2k^2x^2}$$

---

### 3.4 方差分析 (ANOVA)

#### 3.4.1 单因素ANOVA

**模型**:

$$Y_{ij} = \mu + \alpha_i + \varepsilon_{ij}$$

其中：
- $\mu$: 总均值
- $\alpha_i$: 第 $i$ 组效应，$\sum_i \alpha_i = 0$
- $\varepsilon_{ij} \sim N(0, \sigma^2)$: 随机误差

**假设**:

$$H_0: \alpha_1 = \alpha_2 = ... = \alpha_k = 0$$

$$H_1: \exists i: \alpha_i \neq 0$$

**平方和分解**:

$$SS_T = SS_B + SS_W$$

**总平方和**:

$$SS_T = \sum_{i=1}^k \sum_{j=1}^{n_i} (Y_{ij} - \bar{Y}_{..})^2$$

**组间平方和**:

$$SS_B = \sum_{i=1}^k n_i(\bar{Y}_{i\cdot} - \bar{Y}_{..})^2$$

**组内平方和**:

$$SS_W = \sum_{i=1}^k \sum_{j=1}^{n_i} (Y_{ij} - \bar{Y}_{i\cdot})^2$$

**ANOVA表**:

| 来源 | 平方和 | 自由度 | 均方 | F值 |
|-----|--------|--------|------|-----|
| 组间 | $SS_B$ | $k-1$ | $MS_B = \frac{SS_B}{k-1}$ | $F = \frac{MS_B}{MS_W}$ |
| 组内 | $SS_W$ | $N-k$ | $MS_W = \frac{SS_W}{N-k}$ | |
| 总计 | $SS_T$ | $N-1$ | | |

**检验统计量**:

$$F = \frac{MS_B}{MS_W} \sim F_{k-1, N-k}$$

**定理 3.2** (Cochran定理)

若 $X_1, ..., X_n \sim N(0, 1)$ 独立，$Q = \sum_{i=1}^k Q_i$，其中 $Q_i = X^TA_iX$，则：

$$Q_i \sim \chi^2_{r_i} \text{ 且独立} \iff \sum_{i=1}^k r_i = n$$

---

#### 3.4.2 多因素ANOVA

**两因素模型**:

$$Y_{ijk} = \mu + \alpha_i + \beta_j + (\alpha\beta)_{ij} + \varepsilon_{ijk}$$

**平方和分解**:

$$SS_T = SS_A + SS_B + SS_{AB} + SS_E$$

**交互作用检验**:

$$H_0: (\alpha\beta)_{ij} = 0 \quad \forall i, j$$

$$F_{AB} = \frac{MS_{AB}}{MS_E} \sim F_{(a-1)(b-1), ab(n-1)}$$

---

#### 3.4.3 重复测量ANOVA

**模型**:

$$Y_{ij} = \mu + S_i + T_j + \varepsilon_{ij}$$

其中 $S_i$ 是被试间效应，$T_j$ 是时间效应。

**球形假设**:

$$\text{Cov}(Y_{ij} - Y_{ij'}, Y_{ij} - Y_{ij'}) = 2\sigma^2$$

**Greenhouse-Geisser校正**:

$$\hat{\varepsilon} = \frac{k^2(\bar{d}_{ii} - \bar{d}_{..})^2}{(k-1)\sum_{i,j}(d_{ij} - \bar{d}_{i\cdot} - \bar{d}_{\cdot j} + \bar{d}_{..})^2}$$

校正后自由度：$\tilde{df} = \hat{\varepsilon} \cdot df$

## 4. 预测性分析模型

### 4.1 回归分析

#### 4.1.1 线性回归

**模型定义**:

$$Y = X\beta + \varepsilon$$

其中：
- $Y \in \mathbb{R}^{n \times 1}$: 响应变量
- $X \in \mathbb{R}^{n \times (p+1)}$: 设计矩阵（含截距列）
- $\beta \in \mathbb{R}^{(p+1) \times 1}$: 回归系数
- $\varepsilon \in \mathbb{R}^{n \times 1}$: 误差项，$\varepsilon \sim N(0, \sigma^2I)$

**最小二乘估计**:

**定理 4.1** (OLS估计量)

最小化残差平方和：

$$\hat{\beta} = \arg\min_\beta \|Y - X\beta\|^2 = (X^TX)^{-1}X^TY$$

**证明**:

令 $S(\beta) = (Y - X\beta)^T(Y - X\beta)$

$$\frac{\partial S}{\partial \beta} = -2X^T(Y - X\beta) = 0$$

$$X^TY = X^TX\beta$$

$$\hat{\beta} = (X^TX)^{-1}X^TY$$

二阶条件：

$$\frac{\partial^2 S}{\partial \beta \partial \beta^T} = 2X^TX$$

由于 $X^TX$ 是半正定矩阵，当 $X$ 满秩时为正定，确认是最小值。

**高斯-马尔可夫定理**:

**定理 4.2** (Gauss-Markov)

在经典线性回归假设下，OLS估计量是**最佳线性无偏估计量 (BLUE)**：

1. 线性性: $\hat{\beta}$ 是 $Y$ 的线性函数
2. 无偏性: $E[\hat{\beta}] = \beta$
3. 最小方差: 在所有线性无偏估计量中方差最小

**证明** (无偏性):

$$E[\hat{\beta}] = E[(X^TX)^{-1}X^TY]$$

$$= (X^TX)^{-1}X^TE[Y]$$

$$= (X^TX)^{-1}X^TX\beta = \beta$$

**方差-协方差矩阵**:

$$\text{Var}(\hat{\beta}) = \sigma^2(X^TX)^{-1}$$

**证明**:

$$\text{Var}(\hat{\beta}) = \text{Var}((X^TX)^{-1}X^TY)$$

$$= (X^TX)^{-1}X^T \text{Var}(Y) X(X^TX)^{-1}$$

$$= (X^TX)^{-1}X^T (\sigma^2I) X(X^TX)^{-1}$$

$$= \sigma^2(X^TX)^{-1}$$

**残差方差估计**:

$$\hat{\sigma}^2 = \frac{RSS}{n-p-1} = \frac{(Y-X\hat{\beta})^T(Y-X\hat{\beta})}{n-p-1}$$

**拟合优度**:

$$R^2 = 1 - \frac{SS_{res}}{SS_{tot}} = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}$$

**调整R²**:

$$R^2_{adj} = 1 - \frac{SS_{res}/(n-p-1)}{SS_{tot}/(n-1)}$$

**假设检验**:

对于单个系数：

$$H_0: \beta_j = 0 \quad \text{vs} \quad H_1: \beta_j \neq 0$$

$$t = \frac{\hat{\beta}_j}{SE(\hat{\beta}_j)} \sim t_{n-p-1}$$

其中 $SE(\hat{\beta}_j) = \sqrt{\hat{\sigma}^2[(X^TX)^{-1}]_{jj}}$

**F检验** (整体显著性):

$$F = \frac{(SS_{tot} - SS_{res})/p}{SS_{res}/(n-p-1)} \sim F_{p, n-p-1}$$

---

#### 4.1.2 逻辑回归

**模型**:

$$P(Y=1|X) = \frac{1}{1 + e^{-X^T\beta}} = \sigma(X^T\beta)$$

其中 $\sigma(z) = \frac{1}{1+e^{-z}}$ 是sigmoid函数。

**对数几率**:

$$\log\frac{P(Y=1|X)}{1-P(Y=1|X)} = X^T\beta$$

**似然函数**:

$$L(\beta) = \prod_{i=1}^n P(Y_i|X_i) = \prod_{i=1}^n \sigma(X_i^T\beta)^{Y_i}(1-\sigma(X_i^T\beta))^{1-Y_i}$$

**对数似然**:

$$\ell(\beta) = \sum_{i=1}^n \left[Y_i X_i^T\beta - \log(1 + e^{X_i^T\beta})\right]$$

**梯度**:

$$\nabla_\beta \ell(\beta) = \sum_{i=1}^n (Y_i - \sigma(X_i^T\beta))X_i = X^T(Y - \hat{p})$$

**Hessian矩阵**:

$$H = \nabla_\beta^2 \ell(\beta) = -\sum_{i=1}^n \sigma(X_i^T\beta)(1-\sigma(X_i^T\beta))X_iX_i^T = -X^TWX$$

其中 $W = \text{diag}(\hat{p}_i(1-\hat{p}_i))$。

**牛顿-拉夫森算法**:

$$\beta^{(t+1)} = \beta^{(t)} - H^{-1}\nabla_\beta \ell = \beta^{(t)} + (X^TWX)^{-1}X^T(Y - \hat{p})$$

**收敛性**:

**定理 4.3** (逻辑回归的收敛性)

在适当条件下，牛顿-拉夫森算法以二次收敛速度收敛到MLE：

$$\|\beta^{(t+1)} - \hat{\beta}\| = O(\|\beta^{(t)} - \hat{\beta}\|^2)$$

**复杂度**: 每次迭代 $O(np^2 + p^3)$

---

#### 4.1.3 多项式回归

**模型**:

$$Y = \beta_0 + \beta_1X + \beta_2X^2 + ... + \beta_dX^d + \varepsilon$$

**设计矩阵**:

$$X_{poly} = \begin{bmatrix} 1 & x_1 & x_1^2 & ... & x_1^d \\ 1 & x_2 & x_2^2 & ... & x_2^d \\ \vdots & \vdots & \vdots & \ddots & \vdots \\ 1 & x_n & x_n^2 & ... & x_n^d \end{bmatrix}$$

**Vandermonde矩阵条件数**:

$$\kappa(X_{poly}) = \frac{\sigma_{max}}{\sigma_{min}}$$

随着 $d$ 增大，条件数指数增长，导致数值不稳定。

**正交多项式**:

使用Legendre多项式 $P_k(x)$：

$$\int_{-1}^1 P_m(x)P_n(x)dx = \frac{2}{2n+1}\delta_{mn}$$

改善数值稳定性。

---

#### 4.1.4 正则化方法

**岭回归 (Ridge)**:

$$\hat{\beta}_{ridge} = \arg\min_\beta \left\{\|Y - X\beta\|^2 + \lambda\|\beta\|^2\right\}$$

**闭式解**:

$$\hat{\beta}_{ridge} = (X^TX + \lambda I)^{-1}X^TY$$

**偏差-方差分解**:

**定理 4.4** (岭回归的偏差-方差权衡)

$$E[\|\hat{\beta}_{ridge} - \beta\|^2] = \|\text{Bias}\|^2 + \text{Var}$$

$$\text{Bias} = -\lambda(X^TX + \lambda I)^{-1}\beta$$

$$\text{Var} = \sigma^2 \sum_{j=1}^p \frac{\sigma_j^2}{(\sigma_j^2 + \lambda)^2}$$

其中 $\sigma_j$ 是 $X$ 的奇异值。

**LASSO回归**:

$$\hat{\beta}_{lasso} = \arg\min_\beta \left\{\|Y - X\beta\|^2 + \lambda\|\beta\|_1\right\}$$

**软阈值算子**:

对于正交设计：

$$\hat{\beta}_j = S_{\lambda}(\hat{\beta}_j^{OLS}) = \text{sign}(\hat{\beta}_j^{OLS})(|\hat{\beta}_j^{OLS}| - \lambda)_+$$

**坐标下降算法**:

```
算法: LASSO_CoordinateDescent(X, Y, λ, ε)
输入: 设计矩阵X, 响应Y, 正则化参数λ, 收敛阈值ε
输出: β̂

1. 初始化: β = 0
2. repeat:
   for j = 1, ..., p:
     ρ_j = Σ_i x_{ij}(y_i - Σ_{k≠j} x_{ik}β_k)
     β_j = S_{λ}(ρ_j) / Σ_i x_{ij}^2
   until ||β^{new} - β^{old}|| < ε

复杂度: O(np · iter)
```

**弹性网络 (Elastic Net)**:

$$\hat{\beta}_{en} = \arg\min_\beta \left\{\|Y - X\beta\|^2 + \lambda_1\|\beta\|_1 + \lambda_2\|\beta\|_2^2\right\}$$

**定理 4.5** (Elastic Net的组效应)

对于高度相关的变量组，Elastic Net倾向于选择或排除整个组。

---

### 4.2 时间序列预测

#### 4.2.1 ARIMA模型

**AR(p)模型**:

$$Y_t = c + \phi_1Y_{t-1} + \phi_2Y_{t-2} + ... + \phi_pY_{t-p} + \varepsilon_t$$

使用滞后算子 $L$ ($LY_t = Y_{t-1}$):

$$\phi(L)Y_t = c + \varepsilon_t$$

其中 $\phi(L) = 1 - \phi_1L - \phi_2L^2 - ... - \phi_pL^p$。

**平稳性条件**:

**定理 4.6** (AR(p)平稳性)

AR(p)过程平稳当且仅当特征方程的根在单位圆外：

$$\phi(z) = 1 - \phi_1z - \phi_2z^2 - ... - \phi_pz^p = 0$$

所有根满足 $|z_i| > 1$。

**MA(q)模型**:

$$Y_t = \mu + \varepsilon_t + \theta_1\varepsilon_{t-1} + ... + \theta_q\varepsilon_{t-q}$$

$$Y_t = \mu + \theta(L)\varepsilon_t$$

**可逆性条件**:

MA(q)可逆当且仅当 $\theta(z) = 0$ 的根都在单位圆外。

**ARMA(p,q)模型**:

$$Y_t = c + \sum_{i=1}^p \phi_iY_{t-i} + \varepsilon_t + \sum_{j=1}^q \theta_j\varepsilon_{t-j}$$

$$\phi(L)Y_t = c + \theta(L)\varepsilon_t$$

**ARIMA(p,d,q)模型**:

$$\phi(L)(1-L)^d Y_t = c + \theta(L)\varepsilon_t$$

其中 $(1-L)^d$ 是 $d$ 阶差分算子。

**自相关函数 (ACF)**:

$$\rho_k = \frac{\gamma_k}{\gamma_0} = \frac{\text{Cov}(Y_t, Y_{t-k})}{\text{Var}(Y_t)}$$

**偏自相关函数 (PACF)**:

$$\alpha(k) = \text{Corr}(Y_t, Y_{t-k} | Y_{t-1}, ..., Y_{t-k+1})$$

**模型识别**:

| 模型 | ACF | PACF |
|-----|-----|------|
| AR(p) | 拖尾 | p阶截尾 |
| MA(q) | q阶截尾 | 拖尾 |
| ARMA(p,q) | 拖尾 | 拖尾 |

**参数估计 (最大似然)**:

$$L(\phi, \theta, \sigma^2) = \prod_{t=1}^n \frac{1}{\sqrt{2\pi\sigma^2}}\exp\left(-\frac{\varepsilon_t^2}{2\sigma^2}\right)$$

**AIC/BIC模型选择**:

$$AIC = -2\log L + 2k$$

$$BIC = -2\log L + k\log n$$

其中 $k = p + q + 2$ 是参数个数。

---

#### 4.2.2 SARIMA模型

**季节性ARIMA**:

$$\Phi_P(L^s)\phi_p(L)(1-L)^d(1-L^s)^D Y_t = c + \Theta_Q(L^s)\theta_q(L)\varepsilon_t$$

其中：
- $s$: 季节周期
- $P, D, Q$: 季节性AR、差分、MA阶数
- $\Phi_P(L^s)$: 季节性AR多项式
- $\Theta_Q(L^s)$: 季节性MA多项式

---

#### 4.2.3 Prophet模型

**加法模型**:

$$y(t) = g(t) + s(t) + h(t) + \varepsilon_t$$

**趋势成分 $g(t)$**:

**线性趋势**:

$$g(t) = (k + a(t)^T\delta)t + (m + a(t)^T\gamma)$$

**逻辑趋势**:

$$g(t) = \frac{C}{1 + \exp(-(k + a(t)^T\delta)(t - (m + a(t)^T\gamma)))}$$

**变点检测**:

变点 $s_j$ 处的增长率变化：

$$a_j(t) = \begin{cases} 1 & t \geq s_j \\ 0 & \text{otherwise} \end{cases}$$

**季节性成分 $s(t)$**:

傅里叶级数展开：

$$s(t) = \sum_{n=1}^N \left(a_n\cos\left(\frac{2\pi n t}{P}\right) + b_n\sin\left(\frac{2\pi n t}{P}\right)\right)$$

**节假日成分 $h(t)$**:

$$h(t) = Z(t)\kappa = \sum_{i=1}^L \kappa_i \cdot \mathbb{1}_{[t \in D_i]}$$

---

#### 4.2.4 LSTM时间序列预测

**LSTM单元**:

**遗忘门**:

$$f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)$$

**输入门**:

$$i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i)$$

$$\tilde{C}_t = \tanh(W_C \cdot [h_{t-1}, x_t] + b_C)$$

**细胞状态更新**:

$$C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$$

**输出门**:

$$o_t = \sigma(W_o \cdot [h_{t-1}, x_t] + b_o)$$

$$h_t = o_t \odot \tanh(C_t)$$

**梯度流分析**:

**定理 4.7** (LSTM的梯度稳定性)

在LSTM中，细胞状态的梯度：

$$\frac{\partial C_t}{\partial C_{t-1}} = f_t$$

由于 $f_t \in (0, 1)$，梯度不会爆炸，缓解了vanishing gradient问题。

---

### 4.3 分类算法

#### 4.3.1 决策树

**ID3算法**:

使用信息增益选择分裂属性：

$$IG(D, A) = H(D) - \sum_{v \in Values(A)} \frac{|D_v|}{|D|}H(D_v)$$

**熵**:

$$H(D) = -\sum_{i=1}^k p_i \log_2 p_i$$

**C4.5算法**:

使用信息增益率：

$$GR(D, A) = \frac{IG(D, A)}{H_A(D)}$$

其中 $H_A(D) = -\sum_{v} \frac{|D_v|}{|D|}\log_2\frac{|D_v|}{|D|}$ 是分裂信息。

**CART算法**:

**分类树** (Gini指数):

$$Gini(D) = 1 - \sum_{i=1}^k p_i^2$$

**回归树** (MSE):

$$MSE(D) = \frac{1}{|D|}\sum_{i \in D}(y_i - \bar{y}_D)^2$$

**最优分裂**:

$$j^*, s^* = \arg\min_{j,s} \left[\min_{c_1} \sum_{x_i \in R_1(j,s)}(y_i - c_1)^2 + \min_{c_2} \sum_{x_i \in R_2(j,s)}(y_i - c_2)^2\right]$$

其中 $R_1(j,s) = \{X | X_j \leq s\}$，$R_2(j,s) = \{X | X_j > s\}$。

**剪枝策略**:

代价复杂度剪枝：

$$C_\alpha(T) = R(T) + \alpha|T|$$

其中 $R(T)$ 是树的风险，$|T|$ 是叶子节点数。

**复杂度分析**:

- 构建: $O(np \log n)$ 对于连续属性
- 预测: $O(\log n)$ 平均情况

---

#### 4.3.2 随机森林

**算法**:

```
算法: RandomForest(X, Y, n_trees, m_try)
输入: 训练数据(X,Y), 树数量n_trees, 特征子集大小m_try
输出: 森林F

1. for b = 1 to n_trees:
   a. 自助采样: X_b, Y_b ~ Bootstrap(X, Y)
   b. 构建树T_b，每次分裂随机选择m_try个特征
   c. F ← F ∪ {T_b}
2. 返回F

预测: ŷ = mode{T_b(x)} (分类) 或 mean{T_b(x)} (回归)
```

**袋外误差 (OOB Error)**:

$$\text{OOB} = \frac{1}{n}\sum_{i=1}^n L(y_i, \hat{y}_i^{oob})$$

其中 $\hat{y}_i^{oob}$ 是不包含样本 $i$ 的树预测的平均。

**泛化误差上界**:

**定理 4.8** (Breiman, 2001)

对于分类问题，泛化误差满足：

$$PE^* \leq \bar{\rho}(1 - s^2)/s^2$$

其中：
- $\bar{\rho}$: 平均相关系数
- $s$: 平均分类器强度

**特征重要性**:

**Gini重要性**:

$$Importance(A) = \sum_{t \in T_A} p(t)\Delta Gini(t)$$

**置换重要性**:

$$Importance(A) = \frac{1}{B}\sum_{b=1}^B (L_b - L_b^{perm(A)})$$

---

#### 4.3.3 支持向量机 (SVM)

**线性可分情况**:

**优化问题**:

$$\min_{w,b} \frac{1}{2}\|w\|^2$$

$$\text{s.t. } y_i(w^Tx_i + b) \geq 1, \quad i = 1, ..., n$$

**拉格朗日函数**:

$$\mathcal{L}(w, b, \alpha) = \frac{1}{2}\|w\|^2 - \sum_{i=1}^n \alpha_i[y_i(w^Tx_i + b) - 1]$$

**KKT条件**:

1. $\nabla_w \mathcal{L} = w - \sum_i \alpha_i y_i x_i = 0$
2. $\frac{\partial \mathcal{L}}{\partial b} = -\sum_i \alpha_i y_i = 0$
3. $\alpha_i \geq 0$
4. $\alpha_i[y_i(w^Tx_i + b) - 1] = 0$ (互补松弛)

**对偶问题**:

$$\max_\alpha \sum_{i=1}^n \alpha_i - \frac{1}{2}\sum_{i,j} \alpha_i\alpha_j y_i y_j x_i^Tx_j$$

$$\text{s.t. } \sum_i \alpha_i y_i = 0, \quad \alpha_i \geq 0$$

**软间隔SVM**:

$$\min_{w,b,\xi} \frac{1}{2}\|w\|^2 + C\sum_{i=1}^n \xi_i$$

$$\text{s.t. } y_i(w^Tx_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0$$

**核技巧**:

**核函数** $K(x_i, x_j) = \phi(x_i)^T\phi(x_j)$：

| 核函数 | 表达式 | 参数 |
|-------|--------|------|
| 线性 | $K(x,y) = x^Ty$ | - |
| 多项式 | $K(x,y) = (\gamma x^Ty + r)^d$ | $\gamma, r, d$ |
| RBF | $K(x,y) = \exp(-\gamma\|x-y\|^2)$ | $\gamma$ |
| Sigmoid | $K(x,y) = \tanh(\gamma x^Ty + r)$ | $\gamma, r$ |

**Mercer定理**:

**定理 4.9** (Mercer条件)

函数 $K: \mathcal{X} \times \mathcal{X} \rightarrow \mathbb{R}$ 是有效核函数当且仅当：

1. 对称: $K(x, y) = K(y, x)$
2. 半正定: 对于任意 $n$ 和 $\{x_1, ..., x_n\}$，Gram矩阵 $K_{ij} = K(x_i, x_j)$ 半正定

**SMO算法复杂度**:

- 每次迭代: $O(n)$
- 总迭代次数: $O(n)$
- 总复杂度: $O(n^2)$ 到 $O(n^3)$

---

#### 4.3.4 朴素贝叶斯

**贝叶斯定理**:

$$P(Y|X) = \frac{P(X|Y)P(Y)}{P(X)}$$

**条件独立性假设**:

$$P(X_1, X_2, ..., X_p|Y) = \prod_{j=1}^p P(X_j|Y)$$

**分类决策**:

$$\hat{y} = \arg\max_y P(y)\prod_{j=1}^p P(x_j|y)$$

**高斯朴素贝叶斯**:

$$P(x_j|y) = \frac{1}{\sqrt{2\pi\sigma_{jy}^2}}\exp\left(-\frac{(x_j - \mu_{jy})^2}{2\sigma_{jy}^2}\right)$$

**拉普拉斯平滑**:

$$P(x_j|y) = \frac{N_{x_j,y} + \alpha}{N_y + \alpha n_j}$$

**复杂度**:

- 训练: $O(np)$
- 预测: $O(p \cdot |Y|)$

---

### 4.4 集成学习

#### 4.4.1 Bagging

**Bootstrap聚合**:

$$\hat{f}_{bag}(x) = \frac{1}{B}\sum_{b=1}^B \hat{f}_b(x)$$

**方差减少分析**:

**定理 4.10** (Bagging的方差减少)

设基学习器方差为 $\sigma^2$，两两相关系数为 $\rho$：

$$\text{Var}(\hat{f}_{bag}) = \rho\sigma^2 + \frac{1-\rho}{B}\sigma^2$$

当 $B \to \infty$：

$$\text{Var}(\hat{f}_{bag}) \to \rho\sigma^2$$

---

#### 4.4.2 Boosting

**AdaBoost**:

**算法**:

```
算法: AdaBoost(X, Y, n_rounds)
1. 初始化权重: w_i = 1/n
2. for t = 1 to n_rounds:
   a. 训练弱学习器: h_t = WeakLearn(X, Y, w)
   b. 计算误差: ε_t = Σ_i w_i · 𝟙[y_i ≠ h_t(x_i)]
   c. 计算权重: α_t = ½ ln((1-ε_t)/ε_t)
   d. 更新权重: w_i ← w_i · exp(-α_t y_i h_t(x_i))
   e. 归一化: w_i ← w_i / Σ_j w_j
3. 输出: H(x) = sign(Σ_t α_t h_t(x))
```

**训练误差上界**:

**定理 4.11** (AdaBoost收敛性)

$$\frac{1}{n}\sum_{i=1}^n \mathbb{1}[y_i \neq H(x_i)] \leq \prod_{t=1}^T 2\sqrt{\varepsilon_t(1-\varepsilon_t)}$$

若每个弱学习器 $\varepsilon_t \leq 0.5 - \gamma$，则：

$$\text{Training Error} \leq e^{-2\gamma^2 T}$$

**指数级收敛！**

**梯度提升 (GBM)**:

**算法**:

```
算法: GradientBoosting(X, Y, n_trees, η, L)
1. 初始化: F_0(x) = argmin_γ Σ_i L(y_i, γ)
2. for m = 1 to n_trees:
   a. 计算伪残差: r_im = -[∂L(y_i, F(x_i))/∂F(x_i)]_{F=F_{m-1}}
   b. 拟合回归树: h_m(x) 到 {(x_i, r_im)}
   c. 线搜索: ρ_m = argmin_ρ Σ_i L(y_i, F_{m-1}(x_i) + ρh_m(x_i))
   d. 更新: F_m(x) = F_{m-1}(x) + η·ρ_m·h_m(x)
3. 输出: F_M(x)
```

**XGBoost优化**:

**目标函数**:

$$\mathcal{L}^{(t)} = \sum_{i=1}^n L(y_i, \hat{y}_i^{(t-1)} + f_t(x_i)) + \Omega(f_t)$$

其中 $\Omega(f) = \gamma T + \frac{1}{2}\lambda\|w\|^2$ 是正则化项。

**二阶泰勒展开**:

$$\mathcal{L}^{(t)} \approx \sum_{i=1}^n [g_i f_t(x_i) + \frac{1}{2}h_i f_t^2(x_i)] + \Omega(f_t)$$

其中 $g_i = \partial_{\hat{y}^{(t-1)}} L(y_i, \hat{y}^{(t-1)})$，$h_i = \partial^2_{\hat{y}^{(t-1)}} L(y_i, \hat{y}^{(t-1)})$。

**最优叶子权重**:

$$w_j^* = -\frac{\sum_{i \in I_j} g_i}{\sum_{i \in I_j} h_i + \lambda}$$

**分裂增益**:

$$Gain = \frac{1}{2}\left[\frac{G_L^2}{H_L + \lambda} + \frac{G_R^2}{H_R + \lambda} - \frac{(G_L+G_R)^2}{H_L+H_R+\lambda}\right] - \gamma$$

**LightGBM优化**:

- **Gradient-based One-Side Sampling (GOSS)**: 保留大梯度样本，随机采样小梯度样本
- **Exclusive Feature Bundling (EFB)**: 互斥特征捆绑

复杂度从 $O(np)$ 降低到 $O(n_{sub} \cdot p_{bundle})$。

---

#### 4.4.3 Stacking

**两层Stacking**:

**第一层** (基学习器):

$$\hat{y}_i^{(m)} = f_m(x_i), \quad m = 1, ..., M$$

**第二层** (元学习器):

$$\hat{y}_i = g(\hat{y}_i^{(1)}, \hat{y}_i^{(2)}, ..., \hat{y}_i^{(M)})$$

**交叉验证Stacking**:

为避免数据泄露，使用K折交叉验证生成元特征：

```
算法: StackingCV(X, Y, base_learners, meta_learner, K)
1. 将数据分为K折
2. for k = 1 to K:
   a. 训练基学习器在K-1折
   b. 预测第k折作为元特征
3. 用所有元特征训练元学习器
4. 用全部数据重新训练基学习器
```

---

### 4.5 深度学习在数据分析中的应用

#### 4.5.1 卷积神经网络 (CNN)

**一维卷积**:

$$(f * g)[n] = \sum_{m=-M}^M f[m]g[n-m]$$

**卷积层输出尺寸**:

$$O = \frac{I - K + 2P}{S} + 1$$

其中：
- $I$: 输入尺寸
- $K$: 卷积核尺寸
- $P$: 填充
- $S$: 步长

**感受野**:

第 $l$ 层感受野大小：

$$RF_l = RF_{l-1} + (K_l - 1) \times \prod_{i=1}^{l-1} S_i$$

**复杂度**:

- 参数数量: $K^2 \cdot C_{in} \cdot C_{out} + C_{out}$ (偏置)
- 计算量 (FLOPs): $H_{out} \cdot W_{out} \cdot K^2 \cdot C_{in} \cdot C_{out}$

---

#### 4.5.2 循环神经网络 (RNN)

**基本RNN**:

$$h_t = \tanh(W_{hh}h_{t-1} + W_{xh}x_t + b_h)$$

$$y_t = W_{hy}h_t + b_y$$

**梯度问题**:

$$\frac{\partial h_T}{\partial h_1} = \prod_{t=2}^T \text{diag}(\tanh'(z_t))W_{hh}$$

**定理 4.12** (RNN梯度消失/爆炸)

若 $W_{hh}$ 的最大奇异值 $\sigma_{max} < 1$，梯度消失；若 $\sigma_{max} > 1$，梯度爆炸。

**证明**:

$$\|\frac{\partial h_T}{\partial h_1}\| \leq \prod_{t=2}^T \|\text{diag}(\tanh'(z_t))\| \cdot \|W_{hh}\|$$

由于 $\|\text{diag}(\tanh'(z_t))\| \leq 1$：

$$\|\frac{\partial h_T}{\partial h_1}\| \leq \|W_{hh}\|^{T-1}$$

若 $\|W_{hh}\| < 1$，指数衰减；若 $\|W_{hh}\| > 1$，指数增长。

---

#### 4.5.3 Transformer

**自注意力机制**:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

**多头注意力**:

$$\text{MultiHead}(Q, K, V) = \text{Concat}(head_1, ..., head_h)W^O$$

其中 $head_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$。

**位置编码**:

$$PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d_{model}})$$

$$PE_{(pos, 2i+1)} = \cos(pos / 10000^{2i/d_{model}})$$

**复杂度分析**:

| 操作 | 复杂度 | 顺序复杂度 |
|-----|--------|-----------|
| 自注意力 | $O(n^2 \cdot d)$ | $O(1)$ |
| 循环层 | $O(n \cdot d^2)$ | $O(n)$ |
| 卷积层 | $O(k \cdot n \cdot d^2)$ | $O(\log_k n)$ |

其中 $n$ 是序列长度，$d$ 是维度，$k$ 是卷积核大小。

---

## 5. 规范性分析模型

### 5.1 优化模型

#### 5.1.1 线性规划 (LP)

**标准形式**:

$$\min_x c^Tx$$

$$\text{s.t. } Ax = b, \quad x \geq 0$$

**对偶问题**:

$$\max_y b^Ty$$

$$\text{s.t. } A^Ty \leq c$$

**弱对偶定理**:

**定理 5.1** (弱对偶性)

对于原问题可行解 $x$ 和对偶问题可行解 $y$：

$$b^Ty \leq c^Tx$$

**强对偶定理**:

**定理 5.2** (强对偶性)

若原问题有最优解，则对偶问题也有最优解，且：

$$c^Tx^* = b^Ty^*$$

**互补松弛条件**:

$$x_i^*(c_i - (A^Ty^*)_i) = 0, \quad \forall i$$

**单纯形法复杂度**:

- 最坏情况: $O(2^n)$
- 平均情况: $O(n^3)$
- 实践中: 多项式时间

**内点法复杂度**:

$$O(\sqrt{n} \cdot L)$$

其中 $L$ 是输入位数。

---

#### 5.1.2 整数规划

**混合整数线性规划 (MILP)**:

$$\min_x c^Tx$$

$$\text{s.t. } Ax \leq b, \quad x_i \in \mathbb{Z} \text{ for } i \in I$$

**分支定界算法**:

```
算法: BranchAndBound
1. 求解LP松弛，得到下界LB
2. 如果解是整数，返回
3. 选择分数变量x_j进行分支
4. 创建两个子问题: x_j ≤ ⌊x̂_j⌋ 和 x_j ≥ ⌈x̂_j⌉
5. 递归求解子问题，更新上界UB
6. 剪枝: 如果LB ≥ UB，剪去该分支
```

**复杂度**:

- 一般整数规划: NP-hard
- 特殊情况（如全单模矩阵）: 多项式时间

---

#### 5.1.3 动态规划

**贝尔曼最优性原理**:

**定理 5.3** (贝尔曼最优性)

最优策略具有如下性质：无论初始状态和初始决策如何，剩余决策必须构成关于由初始决策产生的新状态的最优策略。

**贝尔曼方程**:

$$V^*(s) = \max_a \left[R(s,a) + \gamma \sum_{s'} P(s'|s,a)V^*(s')\right]$$

**值迭代**:

$$V_{k+1}(s) = \max_a \left[R(s,a) + \gamma \sum_{s'} P(s'|s,a)V_k(s')\right]$$

**收敛性**:

**定理 5.4** (值迭代收敛)

值迭代以几何速率收敛到最优值函数：

$$\|V_k - V^*\|_\infty \leq \gamma^k \|V_0 - V^*\|_\infty$$

**复杂度**: $O(|S|^2|A| \cdot K)$，其中 $K$ 是迭代次数。

---

### 5.2 仿真模拟

#### 5.2.1 蒙特卡洛模拟

**基本框架**:

$$\hat{\theta}_n = \frac{1}{n}\sum_{i=1}^n f(X_i)$$

其中 $X_i \sim p(x)$。

**收敛性**:

**定理 5.5** (蒙特卡洛收敛)

由大数定律：

$$\hat{\theta}_n \xrightarrow{a.s.} E[f(X)]$$

由中心极限定理：

$$\sqrt{n}(\hat{\theta}_n - \theta) \xrightarrow{d} N(0, \sigma^2)$$

其中 $\sigma^2 = \text{Var}(f(X))$。

**误差分析**:

$$\text{RMSE} = \frac{\sigma}{\sqrt{n}}$$

要达到精度 $\epsilon$ 所需样本：

$$n = \frac{\sigma^2}{\epsilon^2}$$

**方差缩减技术**:

**重要性采样**:

$$\theta = E_p[f(X)] = E_q\left[f(X)\frac{p(X)}{q(X)}\right]$$

最优提议分布：

$$q^*(x) = \frac{|f(x)|p(x)}{\int |f(x)|p(x)dx}$$

---

#### 5.2.2 离散事件仿真

**事件调度**:

**下一事件时间推进**:

```
算法: NextEventSimulation
1. 初始化系统状态，事件列表
2. while (仿真未结束):
   a. 从事件列表取出最早事件
   b. 推进仿真时钟到事件时间
   c. 执行事件处理程序
   d. 更新系统状态
   e. 生成后续事件，加入事件列表
3. 输出统计结果
```

**复杂度**: 每次事件处理 $O(\log E)$，其中 $E$ 是事件列表大小。

---

### 5.3 决策树与决策图

#### 5.3.1 决策树分析

**期望货币值 (EMV)**:

$$EMV = \sum_i P_i \cdot V_i$$

**完美信息期望价值 (EVPI)**:

$$EVPI = EMV_{with \ perfect \ info} - EMV_{without \ perfect \ info}$$

**样本信息期望价值 (EVSI)**:

$$EVSI = EMV_{with \ sample \ info} - EMV_{without \ info} - \text{Cost}_{sample}$$

---

### 5.4 强化学习

#### 5.4.1 Q-Learning

**Q函数更新**:

$$Q(s,a) \leftarrow Q(s,a) + \alpha[r + \gamma \max_{a'}Q(s',a') - Q(s,a)]$$

**收敛性**:

**定理 5.6** (Q-Learning收敛)

在以下条件满足时，Q-Learning以概率1收敛到最优Q函数：

1. 所有状态-动作对被无限次访问
2. 学习率满足: $\sum_t \alpha_t(s,a) = \infty$，$\sum_t \alpha_t^2(s,a) < \infty$
3. 奖励有界

**复杂度**: 每次更新 $O(1)$，总复杂度 $O(|S||A|T)$。

---

#### 5.4.2 策略梯度

**策略梯度定理**:

**定理 5.7** (策略梯度)

$$\nabla_\theta J(\theta) = E_{\pi_\theta}\left[\sum_t \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot G_t\right]$$

其中 $G_t = \sum_{k=0}^{\infty} \gamma^k r_{t+k+1}$ 是回报。

**REINFORCE算法**:

$$\theta \leftarrow \theta + \alpha \sum_t \nabla_\theta \log \pi_\theta(a_t|s_t) G_t$$

**Actor-Critic**:

$$\theta \leftarrow \theta + \alpha \sum_t \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot \delta_t$$

其中 $\delta_t = r_{t+1} + \gamma V(s_{t+1}) - V(s_t)$ 是TD误差。

## 6. 高频经典算法

### 6.1 聚类算法

#### 6.1.1 K-means聚类

**目标函数**:

$$J = \sum_{i=1}^n \sum_{k=1}^K r_{ik} \|x_i - \mu_k\|^2$$

其中 $r_{ik} \in \{0, 1\}$ 是指示变量，$r_{ik} = 1$ 当且仅当 $x_i$ 属于簇 $k$。

**Lloyd算法**:

```
算法: K-means(X, K, max_iter)
输入: 数据X, 簇数K, 最大迭代次数
输出: 簇中心μ, 簇分配r

1. 随机初始化K个簇中心μ_1, ..., μ_K
2. repeat:
   a. E步 (分配): r_ik = 𝟙[k = argmin_j ||x_i - μ_j||²]
   b. M步 (更新): μ_k = (Σ_i r_ik x_i) / (Σ_i r_ik)
3. until 收敛或达到max_iter

复杂度: O(n · K · d · iter)
```

**收敛性**:

**定理 6.1** (K-means收敛)

K-means算法在有限步内收敛到局部最优。

**证明**:

- E步: 固定 $\mu$，$J$ 关于 $r$ 最小化
- M步: 固定 $r$，$J$ 关于 $\mu$ 最小化
- 每次迭代 $J$ 不增且有下界0
- 可能的分配有限 ($K^n$)

**K-means++初始化**:

```
算法: K-means++(X, K)
1. 随机选择第一个中心μ_1
2. for k = 2 to K:
   a. 计算每个点x到最近中心的距离D(x)
   b. 以概率D(x)²/ΣD(x')²选择新中心
3. 返回初始中心
```

**近似保证**:

**定理 6.2** (K-means++近似比)

K-means++以期望 $O(\log K)$ 近似最优解：

$$E[J] \leq 8(\ln K + 2)J_{opt}$$

**最优K选择**:

**肘部法则**:

$$K^* = \arg\min_K \left\{J(K) + \lambda K\right\}$$

**轮廓系数**:

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

其中：
- $a(i) = \frac{1}{|C_k|-1}\sum_{j \in C_k, j \neq i} d(i,j)$: 内聚度
- $b(i) = \min_{l \neq k} \frac{1}{|C_l|}\sum_{j \in C_l} d(i,j)$: 分离度

---

#### 6.1.2 层次聚类

**凝聚式层次聚类**:

```
算法: AgglomerativeClustering(X, linkage)
1. 每个点作为一个簇
2. while 簇数 > 1:
   a. 找到距离最近的两个簇C_i, C_j
   b. 合并C_i和C_j
3. 返回树状图

复杂度: O(n²) 或 O(n² log n)
```

**链接准则**:

| 链接方式 | 距离定义 |
|---------|---------|
| 单链接 | $d(C_i, C_j) = \min_{x \in C_i, y \in C_j} d(x,y)$ |
| 全链接 | $d(C_i, C_j) = \max_{x \in C_i, y \in C_j} d(x,y)$ |
| 平均链接 | $d(C_i, C_j) = \frac{1}{|C_i||C_j|}\sum_{x \in C_i}\sum_{y \in C_j} d(x,y)$ |
| Ward | $d(C_i, C_j) = \sqrt{\frac{2|C_i||C_j|}{|C_i|+|C_j|}}\|\mu_i - \mu_j\|$ |

**树状图切割**:

选择切割高度 $h$：

$$\text{簇数} = |\{C : \text{merge\_height}(C) > h\}|$$

---

#### 6.1.3 DBSCAN

**核心概念**:

- **ε-邻域**: $N_\varepsilon(p) = \{q \in D : d(p,q) \leq \varepsilon\}$
- **核心点**: $|N_\varepsilon(p)| \geq MinPts$
- **边界点**: 在核心点的ε-邻域内但不是核心点
- **噪声点**: 既不是核心点也不是边界点

**算法**:

```
算法: DBSCAN(D, ε, MinPts)
输入: 数据集D, 邻域半径ε, 最小点数MinPts
输出: 簇标签

1. 标记所有点为未访问
2. for 每个未访问点p:
   a. 标记p为已访问
   b. 如果|N_ε(p)| < MinPts: 标记p为噪声
   c. 否则: 创建新簇，扩展簇(p, N_ε(p))

函数 ExpandCluster(p, neighbors):
   1. 将p加入当前簇
   2. for neighbors中的每个点q:
      a. 如果q未访问:
         - 标记q为已访问
         - 如果|N_ε(q)| ≥ MinPts: neighbors ← neighbors ∪ N_ε(q)
      b. 如果q不属于任何簇: 将q加入当前簇

复杂度: O(n log n) 使用空间索引，最坏O(n²)
```

**参数选择**:

**k-距离图**:

计算每个点到其第k近邻的距离，排序后寻找拐点。

---

#### 6.1.4 高斯混合模型 (GMM)

**模型**:

$$p(x) = \sum_{k=1}^K \pi_k \mathcal{N}(x | \mu_k, \Sigma_k)$$

其中 $\sum_k \pi_k = 1$，$\pi_k \geq 0$。

**对数似然**:

$$\ln p(X|\pi, \mu, \Sigma) = \sum_{i=1}^n \ln \left(\sum_{k=1}^K \pi_k \mathcal{N}(x_i|\mu_k, \Sigma_k)\right)$$

**EM算法**:

**E步** (计算责任):

$$\gamma(z_{ik}) = \frac{\pi_k \mathcal{N}(x_i|\mu_k, \Sigma_k)}{\sum_j \pi_j \mathcal{N}(x_i|\mu_j, \Sigma_j)}$$

**M步** (参数更新):

$$N_k = \sum_{i=1}^n \gamma(z_{ik})$$

$$\mu_k^{new} = \frac{1}{N_k}\sum_{i=1}^n \gamma(z_{ik})x_i$$

$$\Sigma_k^{new} = \frac{1}{N_k}\sum_{i=1}^n \gamma(z_{ik})(x_i - \mu_k^{new})(x_i - \mu_k^{new})^T$$

$$\pi_k^{new} = \frac{N_k}{n}$$

**收敛性**:

**定理 6.3** (EM收敛)

EM算法保证似然函数不递减：

$$\ln p(X|\theta^{(t+1)}) \geq \ln p(X|\theta^{(t)})$$

**证明**:

由Jensen不等式：

$$\ln p(X|\theta) = \ln \sum_Z p(X,Z|\theta) = \ln \sum_Z q(Z)\frac{p(X,Z|\theta)}{q(Z)}$$

$$\geq \sum_Z q(Z)\ln\frac{p(X,Z|\theta)}{q(Z)} = \mathcal{L}(q, \theta)$$

EM通过最大化下界 $\mathcal{L}$ 来最大化似然。

**BIC模型选择**:

$$BIC = -2\ln L + K_{eff}\ln n$$

其中 $K_{eff} = K(1 + d + d(d+1)/2) - 1$ 是有效参数数。

---

### 6.2 降维算法

#### 6.2.1 主成分分析 (PCA)

**目标**:

找到投影方向 $w$，使得投影后方差最大：

$$\max_w w^T\Sigma w \quad \text{s.t. } w^Tw = 1$$

其中 $\Sigma = \frac{1}{n}X^TX$ 是协方差矩阵。

**特征值分解**:

$$\Sigma w = \lambda w$$

**定理 6.4** (PCA最优性)

第 $k$ 个主成分是协方差矩阵第 $k$ 大特征值对应的特征向量。

**证明**:

使用拉格朗日乘子：

$$\mathcal{L} = w^T\Sigma w - \lambda(w^Tw - 1)$$

$$\frac{\partial \mathcal{L}}{\partial w} = 2\Sigma w - 2\lambda w = 0$$

$$\Sigma w = \lambda w$$

方差为 $w^T\Sigma w = \lambda$，因此最大特征值对应最大方差。

**方差解释率**:

$$\text{Explained Variance Ratio}_k = \frac{\lambda_k}{\sum_{i=1}^d \lambda_i}$$

**累计解释率**:

$$\text{Cumulative}_K = \frac{\sum_{k=1}^K \lambda_k}{\sum_{i=1}^d \lambda_i}$$

**SVD实现**:

$$X = U\Sigma V^T$$

主成分方向是 $V$ 的列，主成分得分是 $U\Sigma$。

**复杂度**:

- 特征值分解: $O(d^3)$
- SVD: $O(\min(nd^2, n^2d))$
- 随机SVD: $O(ndk)$

---

#### 6.2.2 线性判别分析 (LDA)

**目标**:

找到投影方向 $w$，使得类间散度最大，类内散度最小：

$$J(w) = \frac{w^TS_Bw}{w^TS_Ww}$$

**散度矩阵**:

**类内散度**:

$$S_W = \sum_{k=1}^K \sum_{i \in C_k} (x_i - \mu_k)(x_i - \mu_k)^T$$

**类间散度**:

$$S_B = \sum_{k=1}^K n_k (\mu_k - \mu)(\mu_k - \mu)^T$$

**最优投影**:

**定理 6.5** (LDA最优解)

LDA的最优投影方向是 $S_W^{-1}S_B$ 的特征向量。

**证明**:

令 $J(w) = \frac{w^TS_Bw}{w^TS_Ww}$，求导并令为0：

$$\frac{\partial J}{\partial w} = \frac{2S_Bw(w^TS_Ww) - 2S_Ww(w^TS_Bw)}{(w^TS_Ww)^2} = 0$$

$$S_Bw = J(w)S_Ww$$

$$S_W^{-1}S_Bw = J(w)w$$

**与PCA比较**:

| 特性 | PCA | LDA |
|-----|-----|-----|
| 监督性 | 无监督 | 有监督 |
| 目标 | 最大方差 | 最大类间分离 |
| 最大维度 | d | K-1 |
| 对异常值 | 敏感 | 较稳健 |

---

#### 6.2.3 t-SNE

**目标**:

保持高维空间中的局部邻域结构。

**高维空间相似度** (条件概率):

$$p_{j|i} = \frac{\exp(-\|x_i - x_j\|^2 / 2\sigma_i^2)}{\sum_{k \neq i}\exp(-\|x_i - x_k\|^2 / 2\sigma_i^2)}$$

$$p_{ij} = \frac{p_{j|i} + p_{i|j}}{2n}$$

**低维空间相似度**:

$$q_{ij} = \frac{(1 + \|y_i - y_j\|^2)^{-1}}{\sum_{k \neq l}(1 + \|y_k - y_l\|^2)^{-1}}$$

**KL散度最小化**:

$$C = KL(P||Q) = \sum_{i \neq j} p_{ij}\log\frac{p_{ij}}{q_{ij}}$$

**梯度**:

$$\frac{\partial C}{\partial y_i} = 4\sum_{j \neq i}(p_{ij} - q_{ij})(y_i - y_j)(1 + \|y_i - y_j\|^2)^{-1}$$

**复杂度**: $O(n^2)$ 每次迭代

** Barnes-Hut近似**: $O(n \log n)$

---

#### 6.2.4 UMAP

**理论基础**:

基于模糊拓扑表示和黎曼几何。

**高维模糊单纯形集**:

$$\nu_i = \{\mu_i, \Phi_i\}$$

其中 $\mu_i$ 是局部度量，$\Phi_i$ 是局部模糊拓扑。

**相似度计算**:

$$\rho_i = \min\{d(x_i, x_j) : 1 \leq j \leq k, d(x_i, x_j) > 0\}$$

$$\sigma_i \text{ s.t. } \sum_{j=1}^k \exp\left(-\frac{\max(0, d(x_i, x_j) - \rho_i)}{\sigma_i}\right) = \log_2(k)$$

**对称化**:

$$w_{ij} = (\nu_{i|j}^{1/p} + \nu_{j|i}^{1/p})^p$$

**交叉熵损失**:

$$CE(P, Q) = \sum_{ij}[p_{ij}\log\frac{p_{ij}}{q_{ij}} + (1-p_{ij})\log\frac{1-p_{ij}}{1-q_{ij}}]$$

**复杂度**: $O(n \cdot k \cdot d \cdot iter)$，其中 $k$ 是近邻数

---

### 6.3 关联规则挖掘

#### 6.3.1 Apriori算法

**基本概念**:

- **支持度**: $supp(X) = \frac{|\{T : X \subseteq T\}|}{|D|}$
- **置信度**: $conf(X \Rightarrow Y) = \frac{supp(X \cup Y)}{supp(X)}$
- **提升度**: $lift(X \Rightarrow Y) = \frac{conf(X \Rightarrow Y)}{supp(Y)}$

**Apriori原理**:

**定理 6.6** (Apriori性质)

若项集 $X$ 是频繁的，则其所有子集也是频繁的。

等价地，若项集 $X$ 是非频繁的，则其所有超集也是非频繁的。

**算法**:

```
算法: Apriori(D, min_sup)
输入: 事务数据库D, 最小支持度min_sup
输出: 频繁项集

1. L_1 = {频繁1-项集}
2. for k = 2; L_{k-1} ≠ ∅; k++:
   a. C_k = apriori_gen(L_{k-1})  // 生成候选
   b. for 每个事务t ∈ D:
      C_t = subset(C_k, t)  // 属于t的候选
      for 每个候选c ∈ C_t:
         c.count++
   c. L_k = {c ∈ C_k : c.count ≥ min_sup}
3. 返回 ∪_k L_k

函数 apriori_gen(L_{k-1}):
   1. for 每个l_1 ∈ L_{k-1}:
      for 每个l_2 ∈ L_{k-1}:
         if l_1[1..k-2] = l_2[1..k-2] 且 l_1[k-1] < l_2[k-1]:
            c = l_1 ∪ l_2
            if has_infrequent_subset(c, L_{k-1}):
               删除c
            否则: 添加c到C_k
   2. 返回C_k

复杂度: O(2^d · n)，其中d是不同项数
```

---

#### 6.3.2 FP-Growth

**FP树构建**:

```
算法: BuildFPTree(D, min_sup)
1. 扫描D，计算项支持度，过滤非频繁项
2. 按支持度降序排列频繁项
3. 创建根节点null
4. for 每个事务t ∈ D:
   a. 选择t中的频繁项，按支持度排序
   b. 将排序后的项插入FP树，更新计数
5. 返回FP树

复杂度: O(n · avg_len)
```

**FP-Growth挖掘**:

```
算法: FPGrowth(Tree, α)
1. if Tree 包含单一路径P:
   for 每个β ⊆ P的组合:
      输出 β ∪ α，支持度 = β中节点的最小计数
2. else:
   for Tree头部表中的每个项a_i:
      b. 生成模式β = a_i ∪ α，支持度 = a_i.support
      c. 构建β的条件模式基和条件FP树Tree_β
      d. if Tree_β ≠ ∅: FPGrowth(Tree_β, β)

复杂度: O(|频繁模式| · avg_pattern_len)
```

**复杂度比较**:

| 算法 | 时间复杂度 | 空间复杂度 | 适用场景 |
|-----|-----------|-----------|---------|
| Apriori | $O(2^d \cdot n)$ | $O(2^d)$ | 稀疏数据 |
| FP-Growth | $O(|FP|)$ | $O(|FP|)$ | 密集数据 |
| Eclat | $O(2^d)$ | $O(n \cdot d)$ | 垂直数据格式 |

---

### 6.4 异常检测

#### 6.4.1 统计方法

**Z-Score方法**:

$$z_i = \frac{x_i - \bar{x}}{s}$$

异常判定: $|z_i| > 3$ (约99.7%置信度)

**IQR方法**:

$$\text{下界} = Q_1 - 1.5 \times IQR$$
$$\text{上界} = Q_3 + 1.5 \times IQR$$

**Grubbs检验**:

$$G = \frac{\max_i |x_i - \bar{x}|}{s}$$

临界值: $G_{crit} = \frac{n-1}{\sqrt{n}}\sqrt{\frac{t_{\alpha/(2n), n-2}^2}{n-2+t_{\alpha/(2n), n-2}^2}}$

---

#### 6.4.2 孤立森林 (Isolation Forest)

**核心思想**:

异常点更容易被孤立（需要更少的分割）。

**算法**:

```
算法: IsolationForest(X, n_trees, subsample_size)
1. for i = 1 to n_trees:
   a. X' = 从X随机采样subsample_size个点
   b. T_i = BuildTree(X', 0, height_limit)
2. 返回森林F = {T_1, ..., T_n}

函数 BuildTree(X, current_height, height_limit):
   1. if current_height ≥ height_limit 或 |X| ≤ 1:
      返回叶子节点
   2. 随机选择特征q
   3. 在q的取值范围内随机选择分割点p
   4. X_left = {x ∈ X : x_q < p}
   5. X_right = {x ∈ X : x_q ≥ p}
   6. 返回节点(q, p, BuildTree(X_left, h+1, limit), BuildTree(X_right, h+1, limit))

复杂度: O(n_trees · ψ · log ψ)，其中ψ = subsample_size
```

**异常分数**:

$$s(x, n) = 2^{-\frac{E[h(x)]}{c(n)}}$$

其中：
- $E[h(x)]$: 平均路径长度
- $c(n) = 2H(n-1) - \frac{2(n-1)}{n}$: 平均路径长度期望值
- $H(i) = \sum_{k=1}^i \frac{1}{k}$: 调和数

**异常判定**: $s(x, n) \approx 1$ 表示异常，$s(x, n) < 0.5$ 表示正常。

---

#### 6.4.3 局部异常因子 (LOF)

**k-距离**:

$$d_k(x) = d(x, x^{(k)})$$

其中 $x^{(k)}$ 是 $x$ 的第 $k$ 个近邻。

**k-距离邻域**:

$$N_k(x) = \{y : d(x, y) \leq d_k(x)\}$$

**可达距离**:

$$\text{reach-dist}_k(x, y) = \max\{d_k(y), d(x, y)\}$$

**局部可达密度**:

$$\text{lrd}_k(x) = \frac{|N_k(x)|}{\sum_{y \in N_k(x)} \text{reach-dist}_k(x, y)}$$

**局部异常因子**:

$$LOF_k(x) = \frac{\sum_{y \in N_k(x)} \frac{\text{lrd}_k(y)}{\text{lrd}_k(x)}}{|N_k(x)|}$$

**解释**:
- $LOF \approx 1$: 正常点
- $LOF > 1$: 异常点（密度低于邻居）
- $LOF < 1$: 密集点（密度高于邻居）

**复杂度**: $O(n^2)$ 或 $O(n \log n)$ 使用空间索引

---

#### 6.4.4 自编码器异常检测

**模型架构**:

$$\text{Encoder}: z = f_{enc}(x; \theta_{enc})$$
$$\text{Decoder}: \hat{x} = f_{dec}(z; \theta_{dec})$$

**重构误差**:

$$L(x, \hat{x}) = \|x - \hat{x}\|^2$$

**异常分数**:

$$\text{Anomaly Score}(x) = \|x - f_{dec}(f_{enc}(x))\|^2$$

**变分自编码器 (VAE)**:

**证据下界 (ELBO)**:

$$\mathcal{L}(\theta, \phi; x) = E_{q_\phi(z|x)}[\log p_\theta(x|z)] - KL(q_\phi(z|x)||p(z))$$

**异常检测**: 使用重构概率或ELBO作为异常分数。

---

## 7. 因果推断方法

### 7.1 潜在结果框架 (Rubin因果模型)

**基本定义**:

- **潜在结果**: $Y_i(1)$ 和 $Y_i(0)$ 分别表示个体 $i$ 在接受处理和不接受处理时的结果
- **观测结果**: $Y_i = D_i Y_i(1) + (1-D_i)Y_i(0)$
- **个体处理效应 (ITE)**: $\tau_i = Y_i(1) - Y_i(0)$

**基本问题**:

**定理 7.1** (因果推断的基本问题)

对于每个个体，我们只能观测到一个潜在结果，无法直接观测ITE。

**平均处理效应 (ATE)**:

$$\tau = E[Y(1) - Y(0)] = E[Y(1)] - E[Y(0)]$$

**识别假设**:

1. **一致性 (Consistency)**: $Y = Y(D)$
2. **可忽略性 (Ignorability)**: $Y(1), Y(0) \perp D | X$
3. **正定性 (Positivity)**: $0 < P(D=1|X) < 1$
4. **SUTVA**: 无干扰，无隐藏变体

**定理 7.2** (ATE识别)

在可忽略性和正定性假设下：

$$\tau = E_X[E[Y|D=1, X] - E[Y|D=0, X]]$$

---

### 7.2 双重差分 (DID)

**基本设定**:

- 处理组: $D=1$
- 对照组: $D=0$
- 处理前: $T=0$
- 处理后: $T=1$

**DID估计量**:

$$\hat{\tau}_{DID} = (\bar{Y}_{11} - \bar{Y}_{10}) - (\bar{Y}_{01} - \bar{Y}_{00})$$

其中 $\bar{Y}_{dt}$ 是处理状态 $d$ 和时间 $t$ 的均值。

**平行趋势假设**:

**假设 7.1** (平行趋势)

$$E[Y(0)_{i1} - Y(0)_{i0}|D=1] = E[Y(0)_{i1} - Y(0)_{i0}|D=0]$$

即在没有处理的情况下，处理组和对照组的趋势相同。

**回归形式**:

$$Y_{it} = \alpha + \beta D_i + \gamma Post_t + \tau (D_i \times Post_t) + \varepsilon_{it}$$

其中 $\tau$ 是DID估计量。

**事件研究设计**:

$$Y_{it} = \alpha_i + \lambda_t + \sum_{k \neq -1} \tau_k \cdot \mathbb{1}[t - t_i^* = k] \cdot D_i + \varepsilon_{it}$$

其中 $t_i^*$ 是个体 $i$ 的处理时间。

---

### 7.3 工具变量 (IV)

**基本设定**:

- **内生变量**: $D$ (与误差项相关)
- **工具变量**: $Z$ (满足以下条件)

**工具变量假设**:

1. **相关性**: $Cov(Z, D) \neq 0$
2. **外生性**: $Cov(Z, \varepsilon) = 0$
3. **排他性**: $Z$ 只通过 $D$ 影响 $Y$

**两阶段最小二乘 (2SLS)**:

**第一阶段**:

$$D = \pi_0 + \pi_1 Z + \nu$$

**第二阶段**:

$$Y = \beta_0 + \beta_1 \hat{D} + \varepsilon$$

**IV估计量**:

$$\hat{\beta}_{IV} = \frac{Cov(Z, Y)}{Cov(Z, D)} = \frac{\sum_i (Z_i - \bar{Z})(Y_i - \bar{Y})}{\sum_i (Z_i - \bar{Z})(D_i - \bar{D})}$$

**局部平均处理效应 (LATE)**:

**定理 7.3** (Imbens & Angrist, 1994)

在单调性假设下，IV估计量识别的是依从者的平均处理效应：

$$\hat{\beta}_{IV} \xrightarrow{p} E[Y(1) - Y(0)|D(1) > D(0)]$$

其中 $D(1) > D(0)$ 表示被 $Z$ 诱导接受处理的人群（依从者）。

**弱工具变量问题**:

**F统计量**:

$$F = \frac{(SSR_R - SSR_{UR})/q}{SSR_{UR}/(n-k)}$$

经验法则: $F < 10$ 表示弱工具变量。

---

### 7.4 倾向得分匹配 (PSM)

**倾向得分定义**:

$$e(X) = P(D=1|X)$$

**定理 7.4** (倾向得分定理)

若可忽略性成立，则：

$$Y(1), Y(0) \perp D | e(X)$$

即给定倾向得分，处理分配与潜在结果独立。

**匹配方法**:

**最近邻匹配**:

$$\mathcal{M}(i) = \{j : D_j = 1 - D_i, |e(X_i) - e(X_j)| = \min_{k: D_k = 1-D_i} |e(X_i) - e(X_k)|\}$$

**卡尺匹配**:

$$\mathcal{M}(i) = \{j : D_j = 1 - D_i, |e(X_i) - e(X_j)| < c\}$$

**核匹配**:

$$\hat{Y}_i(0) = \sum_{j: D_j=0} K\left(\frac{e(X_i) - e(X_j)}{h}\right)Y_j \bigg/ \sum_{j: D_j=0} K\left(\frac{e(X_i) - e(X_j)}{h}\right)$$

**平衡性检验**:

**标准化偏差**:

$$\text{SB} = \frac{\bar{X}_{treated} - \bar{X}_{control}}{\sqrt{(s^2_{treated} + s^2_{control})/2}}$$

经验法则: $|\text{SB}| < 0.1$ 表示平衡。

**共同支撑假设**:

$$0 < e(X) < 1$$

需要修剪倾向得分接近0或1的样本。

---

### 7.5 断点回归 (RDD)

**基本设定**:

处理分配由运行变量 $X$ 相对于断点 $c$ 决定：

$$D_i = \mathbb{1}[X_i \geq c]$$

**清晰断点回归 (Sharp RDD)**:

$$\tau_{SRD} = E[Y(1) - Y(0)|X = c]$$

$$= \lim_{x \downarrow c} E[Y|X=x] - \lim_{x \uparrow c} E[Y|X=x]$$

**模糊断点回归 (Fuzzy RDD)**:

处理概率在断点处跳跃：

$$\tau_{FRD} = \frac{\lim_{x \downarrow c} E[Y|X=x] - \lim_{x \uparrow c} E[Y|X=x]}{\lim_{x \downarrow c} E[D|X=x] - \lim_{x \uparrow c} E[D|X=x]}$$

**局部线性回归**:

$$\min_{\alpha, \beta, \tau} \sum_{i=1}^n K\left(\frac{X_i - c}{h}\right)\left[Y_i - \alpha - \tau D_i - \beta(X_i - c) - \gamma D_i(X_i - c)\right]^2$$

**带宽选择**:

**Imbens-Kalyanaraman最优带宽**:

$$h_{opt} = C_{opt} \cdot n^{-1/5}$$

其中 $C_{opt}$ 取决于数据生成过程。

**有效性检验**:

1. **协变量平衡检验**: 断点处协变量不应有跳跃
2. **密度检验** (McCrary): 检查运行变量密度在断点处是否连续
3. **安慰剂检验**: 使用假断点检验

---

### 7.6 因果图与do-calculus

#### 7.6.1 因果图基础

**有向无环图 (DAG)**:

$$G = (V, E)$$

其中 $V$ 是变量集合，$E$ 是有向边集合。

**d-分离**:

**定义 7.1** (d-分离)

路径 $p$ 被节点集 $Z$ d-分离，如果：

1. $p$ 包含链 $A \rightarrow M \rightarrow B$ 或叉 $A \leftarrow M \rightarrow B$，且 $M \in Z$
2. $p$ 包含对撞 $A \rightarrow M \leftarrow B$，且 $M \notin Z$，且 $M$ 的后代也不在 $Z$

**定理 7.5** (d-分离与条件独立)

若 $Z$ d-分离 $X$ 和 $Y$，则 $X \perp Y | Z$。

**后门准则**:

**定义 7.2** (后门路径)

从 $X$ 到 $Y$ 的后门路径是：
- 以指向 $X$ 的箭头开始
- 不包含任何指向 $X$ 的箭头

**后门准则**:

变量集 $Z$ 满足后门准则，如果：
1. $Z$ 阻断了所有从 $X$ 到 $Y$ 的后门路径
2. $Z$ 不包含 $X$ 的后代

**定理 7.6** (后门调整)

若 $Z$ 满足后门准则，则：

$$P(Y=y|do(X=x)) = \sum_z P(Y=y|X=x, Z=z)P(Z=z)$$

---

#### 7.6.2 do-calculus

**干预分布**:

$$P(Y|do(X)) = P_x(Y)$$

**三条规则**:

**规则1 (插入/删除观测)**:

若 $Y \perp Z | X, W$ 在 $G_{\overline{X}}$ 中，则：

$$P(Y|do(X), Z, W) = P(Y|do(X), W)$$

**规则2 (交换行动/观测)**:

若 $Y \perp Z | X, W$ 在 $G_{\overline{X}, \underline{Z}}$ 中，则：

$$P(Y|do(X), do(Z), W) = P(Y|do(X), Z, W)$$

**规则3 (插入/删除行动)**:

若 $Y \perp Z | X, W$ 在 $G_{\overline{X}, \overline{Z(W)}}$ 中，则：

$$P(Y|do(X), do(Z), W) = P(Y|do(X), W)$$

其中 $Z(W)$ 是不被 $W$ 中的节点祖先的 $Z$ 的子集。

**可识别性**:

**定理 7.7** (Tian & Pearl, 2002)

因果效应 $P(Y|do(X))$ 可从观测数据中识别，当且仅当可以使用do-calculus将其转换为仅包含观测概率的表达式。

---

## 8. 模型选择决策框架

### 8.1 模型选择决策树

```
开始
│
├─ 分析目标
│  ├─ 描述现状 → 描述性分析
│  │  ├─ 数据汇总 → 汇总统计
│  │  ├─ 趋势识别 → 时间序列分解
│  │  └─ 对比评估 → A/B测试、同期群分析
│  │
│  ├─ 诊断原因 → 诊断性分析
│  │  ├─ 相关性探索 → Pearson/Spearman/Kendall
│  │  ├─ 差异检验 → t检验/ANOVA/卡方检验
│  │  └─ 根本原因 → 5Whys/鱼骨图/FTA
│  │
│  ├─ 预测未来 → 预测性分析
│  │  ├─ 数值预测
│  │  │  ├─ 结构化数据
│  │  │  │  ├─ 线性关系 → 线性回归
│  │  │  │  ├─ 非线性关系 → 多项式回归/样条
│  │  │  │  ├─ 高维数据 → 正则化回归(Ridge/LASSO)
│  │  │  │  └─ 时间序列 → ARIMA/Prophet/LSTM
│  │  │  └─ 非结构化数据 → CNN/RNN/Transformer
│  │  │
│  │  └─ 分类预测
│  │     ├─ 小样本/解释性重要 → 逻辑回归/决策树
│  │     ├─ 中等规模 → 随机森林/SVM
│  │     ├─ 大规模/高性能 → XGBoost/LightGBM
│  │     └─ 深度学习场景 → 神经网络
│  │
│  └─ 优化决策 → 规范性分析
│     ├─ 资源分配 → 线性规划/整数规划
│     ├─ 动态决策 → 动态规划/强化学习
│     └─ 风险评估 → 蒙特卡洛模拟
│
├─ 数据特征
│  ├─ 数据量小(n<1000) → 简单模型(线性/树)
│  ├─ 数据量中(1000<n<100K) → 集成方法
│  ├─ 数据量大(n>100K) → 深度学习/分布式
│  ├─ 特征维度高 → PCA降维/正则化
│  └─ 类别不平衡 → 重采样/代价敏感学习
│
└─ 业务约束
   ├─ 实时性要求高 → 轻量级模型
   ├─ 可解释性重要 → 线性模型/决策树
   └─ 精度优先 → 集成/深度学习
```

---

### 8.2 模型对比矩阵

#### 8.2.1 回归模型对比

| 模型 | 线性 | 可解释性 | 处理非线性 | 高维数据 | 训练速度 | 预测速度 | 适用场景 |
|-----|------|---------|-----------|---------|---------|---------|---------|
| 线性回归 | ✓ | 高 | ✗ | ✗ | 快 | 极快 | 基线模型、解释性分析 |
| 多项式回归 | ✗ | 中 | ✓ | ✗ | 快 | 快 | 已知非线性关系 |
| Ridge | ✓ | 高 | ✗ | ✓ | 快 | 极快 | 多重共线性 |
| LASSO | ✓ | 高 | ✗ | ✓ | 快 | 极快 | 特征选择 |
| Elastic Net | ✓ | 高 | ✗ | ✓ | 快 | 极快 | 高维+相关特征 |
| 决策树 | ✗ | 高 | ✓ | ✓ | 快 | 快 | 非线性、交互效应 |
| 随机森林 | ✗ | 中 | ✓ | ✓ | 中 | 快 | 通用预测 |
| XGBoost | ✗ | 中 | ✓ | ✓ | 中 | 快 | 竞赛、生产环境 |
| 神经网络 | ✗ | 低 | ✓ | ✓ | 慢 | 快 | 复杂模式、大数据 |

#### 8.2.2 分类模型对比

| 模型 | 线性可分 | 非线性 | 概率输出 | 多分类 | 训练速度 | 内存占用 | 推荐场景 |
|-----|---------|-------|---------|-------|---------|---------|---------|
| 逻辑回归 | ✓ | ✗ | ✓ | ✓ | 快 | 低 | 基线、解释性 |
| 朴素贝叶斯 | ✓ | ✗ | ✓ | ✓ | 极快 | 低 | 文本分类、快速原型 |
| SVM | ✓ | ✓(核) | ✗ | ✓ | 慢 | 中 | 高维、小样本 |
| 决策树 | ✗ | ✓ | ✗ | ✓ | 快 | 低 | 规则提取 |
| 随机森林 | ✗ | ✓ | ✓ | ✓ | 中 | 高 | 通用分类 |
| XGBoost | ✗ | ✓ | ✓ | ✓ | 中 | 中 | 生产环境首选 |
| 神经网络 | ✗ | ✓ | ✓ | ✓ | 慢 | 高 | 图像/文本/复杂数据 |

#### 8.2.3 聚类算法对比

| 算法 | 簇形状 | 需指定K | 处理噪声 | 大规模数据 | 复杂度 | 适用场景 |
|-----|-------|--------|---------|-----------|-------|---------|
| K-means | 球形 | ✓ | ✗ | ✓ | O(nKdi) | 快速聚类、球形簇 |
| 层次聚类 | 任意 | ✗ | ✗ | ✗ | O(n²) | 小数据、层次结构 |
| DBSCAN | 任意 | ✗ | ✓ | ✓ | O(n log n) | 噪声数据、任意形状 |
| GMM | 椭球形 | ✓ | ✗ | ✓ | O(nKdi) | 软聚类、概率输出 |
| 谱聚类 | 任意 | ✓ | ✗ | ✗ | O(n³) | 非凸簇形状 |

#### 8.2.4 因果推断方法对比

| 方法 | 所需假设 | 数据要求 | 估计量 | 内部效度 | 外部效度 | 适用场景 |
|-----|---------|---------|-------|---------|---------|---------|
| RCT | 随机化 | 实验数据 | ATE | 高 | 中 | 金标准、可行性高 |
| DID | 平行趋势 | 面板数据 | ATT | 中 | 中 | 政策评估 |
| IV | 工具变量 | 横截面 | LATE | 中 | 低 | 内生性问题 |
| PSM | 可忽略性 | 观测数据 | ATT | 中 | 低 | 观察性研究 |
| RDD | 连续性 | 断点附近 | LATE | 高 | 低 | 阈值政策 |

---

### 8.3 模型评估指标汇总

#### 8.3.1 回归评估

| 指标 | 公式 | 特点 |
|-----|------|-----|
| MSE | $\frac{1}{n}\sum(y_i - \hat{y}_i)^2$ | 对大误差敏感 |
| RMSE | $\sqrt{MSE}$ | 与目标变量同量纲 |
| MAE | $\frac{1}{n}\sum|y_i - \hat{y}_i|$ | 对异常值稳健 |
| MAPE | $\frac{100\%}{n}\sum|\frac{y_i - \hat{y}_i}{y_i}|$ | 相对误差，避免零值 |
| R² | $1 - \frac{SS_{res}}{SS_{tot}}$ | 解释方差比例 |
| Adjusted R² | $1 - \frac{SS_{res}/(n-p)}{SS_{tot}/(n-1)}$ | 惩罚复杂模型 |

#### 8.3.2 分类评估

| 指标 | 公式 | 适用场景 |
|-----|------|---------|
| 准确率 | $\frac{TP+TN}{TP+TN+FP+FN}$ | 平衡数据 |
| 精确率 | $\frac{TP}{TP+FP}$ | 假阳性代价高 |
| 召回率 | $\frac{TP}{TP+FN}$ | 假阴性代价高 |
| F1 | $2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}$ | 平衡精确率和召回率 |
| AUC-ROC | ROC曲线下面积 | 排序能力 |
| AUC-PR | PR曲线下面积 | 不平衡数据 |
| Log Loss | $-\frac{1}{n}\sum[y_i\log\hat{y}_i + (1-y_i)\log(1-\hat{y}_i)]$ | 概率校准 |

#### 8.3.3 聚类评估

| 指标 | 公式 | 特点 |
|-----|------|-----|
| 轮廓系数 | $\frac{b-a}{\max(a,b)}$ | [-1, 1]，越高越好 |
| CH指数 | $\frac{SS_B/(K-1)}{SS_W/(n-K)}$ | 越高越好 |
| DB指数 | $\frac{1}{K}\sum_k \max_{l \neq k} \frac{\sigma_k + \sigma_l}{d(c_k, c_l)}$ | 越低越好 |
| 互信息 | $MI(C, T)$ | 需要真实标签 |

---

## 9. 参考文献

### 经典教材

1. **Hastie, T., Tibshirani, R., & Friedman, J.** (2009). *The Elements of Statistical Learning: Data Mining, Inference, and Prediction* (2nd ed.). Springer.

2. **Bishop, C. M.** (2006). *Pattern Recognition and Machine Learning*. Springer.

3. **Murphy, K. P.** (2012). *Machine Learning: A Probabilistic Perspective*. MIT Press.

4. **James, G., Witten, D., Hastie, T., & Tibshirani, R.** (2013). *An Introduction to Statistical Learning*. Springer.

5. **Goodfellow, I., Bengio, Y., & Courville, A.** (2016). *Deep Learning*. MIT Press.

### 数据模型与数据库

6. **Codd, E. F.** (1970). A relational model of data for large shared data banks. *Communications of the ACM*, 13(6), 377-387.

7. **Kimball, R., & Ross, M.** (2013). *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling* (3rd ed.). Wiley.

8. **Linstedt, D., & Olschimke, M.** (2016). *Building a Scalable Data Warehouse with Data Vault 2.0*. Morgan Kaufmann.

9. **Dehghani, Z.** (2022). *Data Mesh: Delivering Data-Driven Value at Scale*. O'Reilly Media.

### 因果推断

10. **Pearl, J.** (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.

11. **Imbens, G. W., & Rubin, D. B.** (2015). *Causal Inference in Statistics, Social, and Biomedical Sciences*. Cambridge University Press.

12. **Angrist, J. D., & Pischke, J. S.** (2009). *Mostly Harmless Econometrics: An Empiricist's Companion*. Princeton University Press.

13. **Cunningham, S.** (2021). *Causal Inference: The Mixtape*. Yale University Press.

### 时间序列

14. **Box, G. E. P., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M.** (2016). *Time Series Analysis: Forecasting and Control* (5th ed.). Wiley.

15. **Hyndman, R. J., & Athanasopoulos, G.** (2021). *Forecasting: Principles and Practice* (3rd ed.). OTexts.

### 优化与决策

16. **Boyd, S., & Vandenberghe, L.** (2004). *Convex Optimization*. Cambridge University Press.

17. **Sutton, R. S., & Barto, A. G.** (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.

### 聚类与降维

18. **MacKay, D. J. C.** (2003). *Information Theory, Inference, and Learning Algorithms*. Cambridge University Press.

19. **van der Maaten, L., & Hinton, G.** (2008). Visualizing data using t-SNE. *Journal of Machine Learning Research*, 9, 2579-2605.

20. **McInnes, L., Healy, J., & Melville, J.** (2018). UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. *arXiv:1802.03426*.

### 集成学习

21. **Breiman, L.** (2001). Random forests. *Machine Learning*, 45(1), 5-32.

22. **Chen, T., & Guestrin, C.** (2016). XGBoost: A scalable tree boosting system. *KDD*, 785-794.

23. **Ke, G., et al.** (2017). LightGBM: A highly efficient gradient boosting decision tree. *NIPS*, 3146-3154.

---

## 附录A: 数学符号表

| 符号 | 含义 |
|-----|------|
| $\mathbb{R}$ | 实数集 |
| $\mathbb{R}^n$ | n维实向量空间 |
| $\mathbb{R}^{n \times m}$ | n×m实矩阵空间 |
| $\mathbb{1}[\cdot]$ | 指示函数 |
| $E[X]$ | 期望 |
| $\text{Var}(X)$ | 方差 |
| $\text{Cov}(X,Y)$ | 协方差 |
| $\xrightarrow{d}$ | 依分布收敛 |
| $\xrightarrow{p}$ | 依概率收敛 |
| $\xrightarrow{a.s.}$ | 几乎必然收敛 |
| $\|x\|$ | L2范数 |
| $\|x\|_1$ | L1范数 |
| $\|x\|_\infty$ | 无穷范数 |
| $\nabla f$ | 梯度 |
| $\nabla^2 f$ | Hessian矩阵 |
| $O(\cdot)$ | 大O符号 |
| $\Theta(\cdot)$ | Theta符号 |
| $\Omega(\cdot)$ | Omega符号 |

---

## 附录B: 算法复杂度速查表

| 算法/操作 | 时间复杂度 | 空间复杂度 |
|----------|-----------|-----------|
| 线性回归 (OLS) | $O(np^2 + p^3)$ | $O(np + p^2)$ |
| 梯度下降 | $O(np \cdot iter)$ | $O(p)$ |
| K-means | $O(nKdi)$ | $O(n + Kd)$ |
| 层次聚类 | $O(n^2)$ 或 $O(n^2 \log n)$ | $O(n^2)$ |
| DBSCAN | $O(n \log n)$ | $O(n)$ |
| PCA (SVD) | $O(\min(nd^2, n^2d))$ | $O(nd + d^2)$ |
| t-SNE | $O(n^2 \cdot iter)$ | $O(n^2)$ |
| 决策树 | $O(np \log n)$ | $O(n)$ |
| 随机森林 | $O(B \cdot np \log n)$ | $O(B \cdot n)$ |
| XGBoost | $O(K \cdot n \log n \cdot d)$ | $O(K \cdot n)$ |
| Apriori | $O(2^d \cdot n)$ | $O(2^d)$ |
| FP-Growth | $O(|FP|)$ | $O(|FP|)$ |
| 孤立森林 | $O(T \cdot \psi \log \psi)$ | $O(T \cdot \psi)$ |
| LOF | $O(n^2)$ 或 $O(n \log n)$ | $O(n)$ |
| ARIMA拟合 | $O(n \cdot p \cdot q)$ | $O(p + q)$ |
| 线性规划 (单纯形) | $O(2^n)$ 最坏, $O(n^3)$ 平均 | $O(nm)$ |
| Q-Learning | $O(|S||A|T)$ | $O(|S||A|)$ |

---

*文档生成完成。本分析涵盖了数据分析领域的核心数据模型与分析方法，提供了数学严谨的公式推导、复杂度分析和适用场景指导。*
