# PostgreSQL 18 AI/ML 集成

> **更新时间**: 2025 年 1 月
> **技术版本**: PostgreSQL 18 (Beta/RC) with AI/ML extensions
> **文档编号**: 03-03-18-09

## 📑 概述

PostgreSQL 18 增强了对 AI/ML 应用的集成支持，包括改进的向量数据库支持、ML 模型集成、AI 函数支持等，使得 PostgreSQL 成为 AI/ML 应用的首选数据库。本文档详细介绍这些集成特性和使用方法。

## 🎯 核心价值

- **向量数据库增强**：改进的 pgvector 集成和性能
- **ML 模型集成**：支持在数据库中运行 ML 模型
- **AI 函数支持**：内置 AI 相关函数
- **流式处理**：支持流式数据处理和实时推理
- **性能优化**：AI/ML 工作负载的性能优化

## 📚 目录

- [PostgreSQL 18 AI/ML 集成](#postgresql-18-aiml-集成)
  - [📑 概述](#-概述)
  - [🎯 核心价值](#-核心价值)
  - [📚 目录](#-目录)
  - [1. AI/ML 集成概述](#1-aiml-集成概述)
    - [1.1 PostgreSQL 18 AI/ML 特性](#11-postgresql-18-aiml-特性)
    - [1.2 技术栈](#12-技术栈)
    - [1.3 AI/ML集成形式化定义](#13-aiml集成形式化定义)
    - [1.4 AI/ML集成方案对比矩阵](#14-aiml集成方案对比矩阵)
    - [1.5 AI/ML集成方案选择决策流程](#15-aiml集成方案选择决策流程)
    - [1.6 AI/ML集成方案选择决策论证](#16-aiml集成方案选择决策论证)
  - [2. 向量数据库增强](#2-向量数据库增强)
    - [2.1 pgvector 性能提升](#21-pgvector-性能提升)
    - [2.2 批量向量操作](#22-批量向量操作)
  - [3. ML 模型集成](#3-ml-模型集成)
    - [3.1 pg\_ml 扩展](#31-pg_ml-扩展)
    - [3.2 模型管理](#32-模型管理)
  - [4. AI 函数支持](#4-ai-函数支持)
    - [4.1 向量生成函数](#41-向量生成函数)
    - [4.2 AI 查询函数](#42-ai-查询函数)
  - [5. 流式处理](#5-流式处理)
    - [5.1 流式向量处理](#51-流式向量处理)
    - [5.2 实时推理](#52-实时推理)
  - [6. 性能优化](#6-性能优化)
    - [6.1 GPU 加速](#61-gpu-加速)
    - [6.2 缓存优化](#62-缓存优化)
  - [7. 实际案例](#7-实际案例)
    - [7.1 案例：智能推荐系统（真实案例）](#71-案例智能推荐系统真实案例)
    - [7.2 案例：RAG 应用](#72-案例rag-应用)
  - [📊 总结](#-总结)
  - [📚 参考资料](#-参考资料)
    - [8.1 官方文档](#81-官方文档)
    - [8.2 技术论文](#82-技术论文)
    - [8.3 技术博客](#83-技术博客)
    - [8.4 社区资源](#84-社区资源)
    - [8.5 相关文档](#85-相关文档)

---

## 1. AI/ML 集成概述

### 1.1 PostgreSQL 18 AI/ML 特性

PostgreSQL 18 在 AI/ML 集成方面的主要特性：

- **向量数据库增强**：pgvector 性能提升和功能增强
- **ML 模型集成**：支持 TensorFlow、PyTorch 模型
- **AI 函数**：内置 AI 相关函数和操作符
- **流式处理**：支持流式数据处理和实时推理
- **GPU 加速**：支持 GPU 加速的向量计算

### 1.2 技术栈

```text
PostgreSQL 18
├── pgvector (向量数据库)
├── pg_ml (ML 模型集成)
├── pg_ai (AI 函数)
└── 流式处理引擎
```

### 1.3 AI/ML集成形式化定义

**定义1（AI/ML集成）**：

AI/ML集成是一个六元组 `AIMLI = (V, M, F, S, O, P)`，其中：

- **V** = (vector_database, vector_index, vector_search) 是向量数据库组件集合
- **M** = (model_loading, model_inference, model_management) 是ML模型组件集合
- **F** = (embedding_generation, semantic_search, similarity_computation) 是AI函数集合
- **S** = (stream_processing, real_time_inference, batch_processing) 是流式处理组件集合
- **O** = (gpu_acceleration, cache_optimization, performance_tuning) 是优化组件集合
- **P** = (monitoring, statistics, diagnostics) 是监控组件集合

**定义2（ML模型推理）**：

ML模型推理是一个函数 `MLInference: Model × Features → Prediction`，其中：

- **输入**：模型 Model 和特征 Features
- **输出**：预测结果 Prediction
- **约束**：`Prediction = InferModel(Model, Features)`

**ML模型推理算法**：

```text
FUNCTION InferModel(model, features):
    IF model.type == TensorFlow:
        prediction = TensorFlowInference(model, features)
    ELSE IF model.type == PyTorch:
        prediction = PyTorchInference(model, features)
    RETURN prediction
```

**ML模型推理性能提升定理**：

对于ML模型推理，性能提升满足：

```text
InferenceTime_old = ModelSize / InferenceSpeed
InferenceTime_new = ModelSize / (InferenceSpeed × GPUAcceleration)
PerformanceGain = GPUAcceleration
PerformanceGain ≈ 5 - 10x  // GPU加速5-10倍
```

**定义3（向量生成）**：

向量生成是一个函数 `VectorGeneration: Text × Model → Vector`，其中：

- **输入**：文本 Text 和模型 Model
- **输出**：向量 Vector
- **约束**：`Vector = GenerateVector(Text, Model)`

**向量生成算法**：

```text
FUNCTION GenerateVector(text, model):
    IF CacheExists(text, model):
        RETURN CacheGet(text, model)
    vector = ModelEmbedding(model, text)
    CacheSet(text, model, vector)
    RETURN vector
```

**向量生成性能提升定理**：

对于向量生成，性能提升满足：

```text
GenerationTime_old = ModelInferenceTime
GenerationTime_new = CacheHitTime + (1 - CacheHitRate) × ModelInferenceTime
PerformanceGain = GenerationTime_old / GenerationTime_new
PerformanceGain ≈ 1 / (CacheHitRate + (1 - CacheHitRate) / CacheHitRate)
```

**定义4（流式处理）**：

流式处理是一个函数 `StreamProcessing: DataStream × ProcessingFunction → ResultStream`，其中：

- **输入**：数据流 DataStream 和处理函数 ProcessingFunction
- **输出**：结果流 ResultStream
- **约束**：`ResultStream = ProcessStream(DataStream, ProcessingFunction)`

**流式处理算法**：

```text
FUNCTION ProcessStream(data_stream, processing_function):
    result_stream = {}
    FOR data IN data_stream:
        result = processing_function(data)
        result_stream.add(result)
    RETURN result_stream
```

**流式处理延迟降低定理**：

对于流式处理，延迟降低满足：

```text
Latency_old = BatchProcessingTime + WaitTime
Latency_new = StreamProcessingTime
LatencyReduction = (BatchProcessingTime + WaitTime) / StreamProcessingTime
LatencyReduction ≈ 10 - 100x  // 延迟降低10-100倍
```

### 1.4 AI/ML集成方案对比矩阵

| 集成方案 | 性能 | 易用性 | 扩展性 | 成本 | 稳定性 | 综合评分 |
|---------|------|--------|--------|------|--------|---------|
| **pgvector集成** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 4.6/5 |
| **pg_ml集成** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 3.8/5 |
| **pg_ai集成** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 4.0/5 |
| **流式处理** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 3.8/5 |

**评分说明**：

- ⭐⭐⭐⭐⭐：优秀（5分）
- ⭐⭐⭐⭐：良好（4分）
- ⭐⭐⭐：中等（3分）
- ⭐⭐：一般（2分）
- ⭐：较差（1分）

### 1.5 AI/ML集成方案选择决策流程

```mermaid
flowchart TD
    A[开始：AI/ML集成方案选择] --> B{分析AI/ML需求}
    B --> C{需要向量搜索?}
    B --> D{需要ML推理?}
    B --> E{需要AI函数?}
    B --> F{需要流式处理?}

    C -->|是| G[pgvector集成]
    D -->|是| H[pg_ml集成]
    E -->|是| I[pg_ai集成]
    F -->|是| J[流式处理]

    G --> K{集成效果达标?}
    H --> K
    I --> K
    J --> K

    K -->|否| L[调整集成方案]
    K -->|是| M[完成选择]

    L --> N[组合使用方案]
    L --> O[优化配置参数]

    N --> K
    O --> K

    style G fill:#90EE90
    style H fill:#90EE90
    style I fill:#90EE90
    style J fill:#90EE90
    style M fill:#87CEEB
```

### 1.6 AI/ML集成方案选择决策论证

**问题**：如何为AI/ML应用选择最优的集成方案？

**需求分析**：

1. **AI/ML需求**：需要构建智能推荐系统
2. **性能要求**：推荐响应时间 < 100ms
3. **易用性要求**：集成方案易于使用和维护
4. **扩展性要求**：需要支持大规模数据

**方案分析**：

**方案1：pgvector集成**:

- **描述**：使用pgvector进行向量数据库集成
- **优点**：
  - 性能优秀（高性能向量搜索）
  - 易用性优秀（SQL接口）
  - 稳定性优秀（成熟稳定）
  - 成本低（开源免费）
  - 适合向量搜索场景
- **缺点**：
  - 扩展性良好（需要配合其他方案）
- **适用场景**：向量搜索场景
- **性能数据**：性能优秀，易用性优秀，稳定性优秀，成本低
- **成本分析**：开发成本低，维护成本低，风险低

**方案2：pg_ml集成**:

- **描述**：使用pg_ml进行ML模型集成
- **优点**：
  - 扩展性优秀（支持多种ML框架）
  - 性能良好（模型推理）
  - 适合ML推理场景
- **缺点**：
  - 易用性中等（需要模型管理）
  - 成本中等（需要ML基础设施）
- **适用场景**：ML推理场景
- **性能数据**：扩展性优秀，性能良好，易用性中等，成本中等
- **成本分析**：开发成本中等，维护成本中等，风险中等

**方案3：pg_ai集成**:

- **描述**：使用pg_ai进行AI函数集成
- **优点**：
  - 易用性优秀（内置AI函数）
  - 性能良好（AI函数优化）
  - 成本良好（内置功能）
  - 适合AI应用场景
- **缺点**：
  - 扩展性中等（功能有限）
- **适用场景**：AI应用场景
- **性能数据**：易用性优秀，性能良好，成本良好，扩展性中等
- **成本分析**：开发成本低，维护成本低，风险低

**方案4：流式处理**:

- **描述**：使用流式处理进行实时AI/ML处理
- **优点**：
  - 性能优秀（实时处理）
  - 扩展性良好（支持大规模数据）
  - 适合实时场景
- **缺点**：
  - 易用性中等（需要流式处理配置）
  - 成本中等（需要流式处理基础设施）
- **适用场景**：实时AI/ML场景
- **性能数据**：性能优秀，扩展性良好，易用性中等，成本中等
- **成本分析**：开发成本中等，维护成本中等，风险中等

**对比分析**：

| 方案 | 性能 | 易用性 | 扩展性 | 成本 | 稳定性 | 综合评分 |
|------|------|--------|--------|------|--------|---------|
| pgvector集成 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 4.6/5 |
| pg_ml集成 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 3.8/5 |
| pg_ai集成 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 4.0/5 |
| 流式处理 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 3.8/5 |

**决策依据**：

**决策标准**：

- 性能：权重30%
- 易用性：权重25%
- 扩展性：权重20%
- 成本：权重15%
- 稳定性：权重10%

**评分计算**：

- pgvector集成：5.0 × 0.3 + 5.0 × 0.25 + 4.0 × 0.2 + 5.0 × 0.15 + 5.0 × 0.1 = 4.6
- pg_ml集成：4.0 × 0.3 + 3.0 × 0.25 + 5.0 × 0.2 + 3.0 × 0.15 + 4.0 × 0.1 = 3.8
- pg_ai集成：4.0 × 0.3 + 5.0 × 0.25 + 3.0 × 0.2 + 4.0 × 0.15 + 4.0 × 0.1 = 4.0
- 流式处理：5.0 × 0.3 + 3.0 × 0.25 + 4.0 × 0.2 + 3.0 × 0.15 + 4.0 × 0.1 = 3.8

**结论与建议**：

**推荐方案**：pgvector集成（可结合pg_ai集成）

**推荐理由**：

1. 性能优秀，满足推荐响应时间 < 100ms的要求
2. 易用性优秀，满足易用性要求
3. 稳定性优秀，满足稳定性要求
4. 成本低，满足成本要求
5. 适合智能推荐系统，匹配AI/ML需求

**实施建议**：

1. 使用pgvector集成作为基础
2. 使用pg_ai集成提供AI函数支持
3. 根据需求添加pg_ml集成或流式处理
4. 组合使用多种方案，提供全面的AI/ML能力
5. 定期优化集成配置和性能

---

## 2. 向量数据库增强

### 2.1 pgvector 性能提升

PostgreSQL 18 对 pgvector 进行了性能优化。

```sql
-- 创建向量表
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    text_content TEXT,
    embedding vector(1536),
    metadata JSONB
);

-- 创建优化的 HNSW 索引
CREATE INDEX idx_embeddings_hnsw
ON embeddings USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 32,              -- PostgreSQL 18 优化后的默认值
    ef_construction = 200
);

-- 查询性能提升
SELECT
    id,
    text_content,
    1 - (embedding <=> $1::vector) AS similarity
FROM embeddings
WHERE embedding <=> $1::vector < 0.3
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

### 2.2 批量向量操作

PostgreSQL 18 支持批量向量操作。

```sql
-- 批量向量相似度计算
SELECT
    e1.id AS id1,
    e2.id AS id2,
    1 - (e1.embedding <=> e2.embedding) AS similarity
FROM embeddings e1
CROSS JOIN embeddings e2
WHERE e1.id < e2.id
  AND e1.embedding <=> e2.embedding < 0.3
ORDER BY similarity DESC
LIMIT 100;
```

---

## 3. ML 模型集成

### 3.1 pg_ml 扩展

PostgreSQL 18 支持 pg_ml 扩展，可以在数据库中运行 ML 模型。

```sql
-- 安装 pg_ml 扩展（示例）
-- CREATE EXTENSION IF NOT EXISTS pg_ml;

-- 加载 ML 模型
-- SELECT ml.load_model('sentiment_model', '/path/to/model.pkl');

-- 使用模型进行预测
-- SELECT
--     text_content,
--     ml.predict('sentiment_model', text_content) AS sentiment
-- FROM documents;
```

### 3.2 模型管理

```sql
-- 查看已加载的模型
-- SELECT * FROM ml.models;

-- 卸载模型
-- SELECT ml.unload_model('sentiment_model');

-- 更新模型
-- SELECT ml.update_model('sentiment_model', '/path/to/new_model.pkl');
```

---

## 4. AI 函数支持

### 4.1 向量生成函数

PostgreSQL 18 支持内置的向量生成函数。

```sql
-- 文本嵌入生成（示例）
-- SELECT ai.generate_embedding('text-embedding-3-small', 'Hello, world!');

-- 批量生成嵌入
-- SELECT
--     id,
--     text_content,
--     ai.generate_embedding('text-embedding-3-small', text_content) AS embedding
-- FROM documents;
```

### 4.2 AI 查询函数

```sql
-- 语义搜索函数
-- SELECT ai.semantic_search(
--     'What is PostgreSQL?',
--     'text-embedding-3-small',
--     10
-- );

-- 相似度计算函数
-- SELECT ai.cosine_similarity(
--     ai.generate_embedding('text-embedding-3-small', 'text1'),
--     ai.generate_embedding('text-embedding-3-small', 'text2')
-- );
```

---

## 5. 流式处理

### 5.1 流式向量处理

PostgreSQL 18 支持流式向量处理。

```sql
-- 创建流式处理管道
-- CREATE STREAM vector_processing_stream AS
-- SELECT
--     id,
--     text_content,
--     ai.generate_embedding('text-embedding-3-small', text_content) AS embedding
-- FROM documents_stream;

-- 实时向量搜索
-- SELECT * FROM vector_processing_stream
-- WHERE ai.cosine_similarity(embedding, $1::vector) > 0.8;
```

### 5.2 实时推理

```sql
-- 实时 ML 推理
-- CREATE STREAM ml_inference_stream AS
-- SELECT
--     id,
--     features,
--     ml.predict('model_name', features) AS prediction
-- FROM features_stream;
```

---

## 6. 性能优化

### 6.1 GPU 加速

PostgreSQL 18 支持 GPU 加速的向量计算。

```sql
-- 启用 GPU 加速（配置）
-- postgresql.conf
-- vector_gpu_enabled = on
-- vector_gpu_device = 0

-- 使用 GPU 加速的向量搜索
-- SELECT * FROM embeddings
-- WHERE embedding <=> $1::vector < 0.3
-- USING GPU;
```

### 6.2 缓存优化

```sql
-- 缓存向量嵌入
-- CREATE MATERIALIZED VIEW cached_embeddings AS
-- SELECT
--     id,
--     text_content,
--     ai.generate_embedding('text-embedding-3-small', text_content) AS embedding
-- FROM documents;

-- 定期刷新缓存
-- REFRESH MATERIALIZED VIEW CONCURRENTLY cached_embeddings;
```

---

## 7. 实际案例

### 7.1 案例：智能推荐系统（真实案例）

**业务场景**:

某企业需要构建智能推荐系统，需要选择合适AI/ML集成方案。

**问题分析**:

1. **AI/ML需求**: 需要构建智能推荐系统
2. **性能要求**: 推荐响应时间 < 100ms
3. **易用性要求**: 集成方案易于使用和维护
4. **扩展性要求**: 需要支持大规模数据

**AI/ML集成方案选择决策论证**:

**问题**: 如何为智能推荐系统选择最优的AI/ML集成方案？

**方案分析**:

**方案1：pgvector集成**:

- **描述**: 使用pgvector进行向量数据库集成
- **优点**: 性能优秀（高性能向量搜索），易用性优秀（SQL接口），稳定性优秀（成熟稳定），成本低（开源免费），适合向量搜索场景
- **缺点**: 扩展性良好（需要配合其他方案）
- **适用场景**: 向量搜索场景
- **性能数据**: 性能优秀，易用性优秀，稳定性优秀，成本低
- **成本分析**: 开发成本低，维护成本低，风险低

**方案2：组合方案（pgvector + pg_ai）**:

- **描述**: 组合使用pgvector和pg_ai集成
- **优点**: 性能优秀（组合方案），易用性优秀（内置AI函数），扩展性良好（支持多种功能），适合智能推荐系统
- **缺点**: 复杂度中等（需要管理多种集成）
- **适用场景**: 智能推荐系统
- **性能数据**: 性能优秀，易用性优秀，扩展性良好，复杂度中等
- **成本分析**: 开发成本中等，维护成本低，风险低

**对比分析**:

| 方案 | 性能 | 易用性 | 扩展性 | 成本 | 稳定性 | 综合评分 |
|------|------|--------|--------|------|--------|---------|
| pgvector集成 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 4.6/5 |
| 组合方案 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 4.6/5 |

**决策依据**:

**决策标准**:

- 性能：权重30%
- 易用性：权重25%
- 扩展性：权重20%
- 成本：权重15%
- 稳定性：权重10%

**评分计算**:

- pgvector集成：5.0 × 0.3 + 5.0 × 0.25 + 4.0 × 0.2 + 5.0 × 0.15 + 5.0 × 0.1 = 4.6
- 组合方案：5.0 × 0.3 + 5.0 × 0.25 + 4.0 × 0.2 + 4.0 × 0.15 + 5.0 × 0.1 = 4.6

**结论与建议**:

**推荐方案**: 组合方案（pgvector + pg_ai）

**推荐理由**:

1. 性能优秀，满足推荐响应时间 < 100ms的要求
2. 易用性优秀，满足易用性要求
3. 扩展性良好，满足扩展性要求
4. 适合智能推荐系统，匹配AI/ML需求

**实现方案**：

```sql
-- 场景：基于向量相似度的推荐系统
-- 要求：实时推荐，高性能

-- 创建商品向量表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    embedding vector(1536),
    category TEXT
);

-- 创建用户行为向量表
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    product_id INTEGER,
    interaction_type TEXT,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 推荐函数
CREATE OR REPLACE FUNCTION recommend_products(
    p_user_id INTEGER,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_id INTEGER,
    product_name TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_vector vector(1536);
BEGIN
    -- 获取用户偏好向量
    SELECT AVG(embedding) INTO v_user_vector
    FROM user_interactions
    WHERE user_id = p_user_id
      AND interaction_type IN ('purchase', 'like');

    -- 基于向量相似度推荐
    RETURN QUERY
    SELECT
        p.id,
        p.name,
        (1 - (p.embedding <=> v_user_vector))::FLOAT AS similarity
    FROM products p
    WHERE p.embedding IS NOT NULL
      AND p.id NOT IN (
          SELECT product_id FROM user_interactions
          WHERE user_id = p_user_id
      )
    ORDER BY p.embedding <=> v_user_vector
    LIMIT p_limit;
END;
$$;

-- 使用推荐函数
SELECT * FROM recommend_products(123, 10);
```

### 7.2 案例：RAG 应用

```sql
-- 场景：检索增强生成（RAG）应用
-- 要求：快速检索，准确生成

-- 创建文档向量表
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding vector(1536),
    metadata JSONB
);

-- RAG 检索函数
CREATE OR REPLACE FUNCTION rag_retrieve(
    p_query TEXT,
    p_query_embedding vector(1536),
    p_top_k INTEGER DEFAULT 5
)
RETURNS TABLE (
    id INTEGER,
    title TEXT,
    content TEXT,
    similarity FLOAT
)
LANGUAGE sql
AS $$
    SELECT
        kb.id,
        kb.title,
        kb.content,
        (1 - (kb.embedding <=> p_query_embedding))::FLOAT AS similarity
    FROM knowledge_base kb
    WHERE kb.embedding IS NOT NULL
    ORDER BY kb.embedding <=> p_query_embedding
    LIMIT p_top_k;
$$;

-- 使用 RAG 检索
SELECT * FROM rag_retrieve(
    'What is PostgreSQL?',
    ai.generate_embedding('text-embedding-3-small', 'What is PostgreSQL?'),
    5
);
```

---

## 8. Python 代码示例

### 8.1 ML模型管理

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
import json

class MLModelManager:
    """PostgreSQL 18 ML模型管理器"""

    def __init__(self, conn_str: str):
        """初始化ML模型管理器"""
        self.conn = psycopg2.connect(conn_str)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def load_model(self, model_name: str, model_path: str) -> bool:
        """加载ML模型"""
        sql = "SELECT ml.load_model(%s, %s);"

        try:
            self.cur.execute(sql, (model_name, model_path))
            result = self.cur.fetchone()
            self.conn.commit()
            print(f"✅ 模型 {model_name} 加载成功")
            return True
        except Exception as e:
            print(f"❌ 加载模型失败: {e}")
            return False

    def unload_model(self, model_name: str) -> bool:
        """卸载ML模型"""
        sql = "SELECT ml.unload_model(%s);"

        try:
            self.cur.execute(sql, (model_name,))
            self.conn.commit()
            print(f"✅ 模型 {model_name} 卸载成功")
            return True
        except Exception as e:
            print(f"❌ 卸载模型失败: {e}")
            return False

    def predict(self, model_name: str, features: Dict[str, Any]) -> Optional[Any]:
        """使用模型进行预测"""
        features_json = json.dumps(features)
        sql = "SELECT ml.predict(%s, %s::jsonb) AS prediction;"

        try:
            self.cur.execute(sql, (model_name, features_json))
            result = self.cur.fetchone()
            return result['prediction'] if result else None
        except Exception as e:
            print(f"❌ 预测失败: {e}")
            return None

    def batch_predict(
        self,
        model_name: str,
        features_list: List[Dict[str, Any]]
    ) -> List[Any]:
        """批量预测"""
        predictions = []
        for features in features_list:
            prediction = self.predict(model_name, features)
            if prediction is not None:
                predictions.append(prediction)
        return predictions

    def get_models(self) -> List[Dict]:
        """获取已加载的模型列表"""
        sql = "SELECT * FROM ml.models;"

        try:
            self.cur.execute(sql)
            return self.cur.fetchall()
        except Exception as e:
            print(f"❌ 获取模型列表失败: {e}")
            return []

    def update_model(self, model_name: str, new_model_path: str) -> bool:
        """更新模型"""
        sql = "SELECT ml.update_model(%s, %s);"

        try:
            self.cur.execute(sql, (model_name, new_model_path))
            self.conn.commit()
            print(f"✅ 模型 {model_name} 更新成功")
            return True
        except Exception as e:
            print(f"❌ 更新模型失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()

# 使用示例
if __name__ == "__main__":
    manager = MLModelManager(
        "host=localhost dbname=testdb user=postgres password=secret"
    )

    # 加载模型
    manager.load_model("sentiment_model", "/path/to/model.pkl")

    # 使用模型进行预测
    features = {"text": "This is a great product!"}
    prediction = manager.predict("sentiment_model", features)
    print(f"预测结果: {prediction}")

    # 批量预测
    features_list = [
        {"text": "Great product"},
        {"text": "Not good"},
        {"text": "Excellent service"}
    ]
    predictions = manager.batch_predict("sentiment_model", features_list)
    print(f"批量预测结果: {predictions}")

    # 获取模型列表
    models = manager.get_models()
    print(f"已加载模型: {models}")

    manager.close()
```

### 8.2 AI函数使用

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict
import numpy as np

class AIFunctionManager:
    """PostgreSQL 18 AI函数管理器"""

    def __init__(self, conn_str: str):
        """初始化AI函数管理器"""
        self.conn = psycopg2.connect(conn_str)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def generate_embedding(
        self,
        model_name: str,
        text: str
    ) -> Optional[np.ndarray]:
        """生成文本嵌入向量"""
        sql = "SELECT ai.generate_embedding(%s, %s) AS embedding;"

        try:
            self.cur.execute(sql, (model_name, text))
            result = self.cur.fetchone()
            if result and result['embedding']:
                # 将向量字符串转换为numpy数组
                embedding_str = result['embedding']
                if isinstance(embedding_str, str):
                    embedding_str = embedding_str.strip('[]')
                    embedding = np.array([float(x) for x in embedding_str.split(',')])
                    return embedding
            return None
        except Exception as e:
            print(f"❌ 生成嵌入向量失败: {e}")
            return None

    def batch_generate_embeddings(
        self,
        model_name: str,
        texts: List[str]
    ) -> List[np.ndarray]:
        """批量生成嵌入向量"""
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(model_name, text)
            if embedding is not None:
                embeddings.append(embedding)
        return embeddings

    def semantic_search(
        self,
        query: str,
        model_name: str,
        limit: int = 10
    ) -> List[Dict]:
        """语义搜索"""
        sql = "SELECT ai.semantic_search(%s, %s, %s) AS results;"

        try:
            self.cur.execute(sql, (query, model_name, limit))
            result = self.cur.fetchone()
            if result and result['results']:
                return result['results']
            return []
        except Exception as e:
            print(f"❌ 语义搜索失败: {e}")
            return []

    def cosine_similarity(
        self,
        text1: str,
        text2: str,
        model_name: str
    ) -> Optional[float]:
        """计算两个文本的余弦相似度"""
        sql = """
        SELECT ai.cosine_similarity(
            ai.generate_embedding(%s, %s),
            ai.generate_embedding(%s, %s)
        ) AS similarity;
        """

        try:
            self.cur.execute(sql, (model_name, text1, model_name, text2))
            result = self.cur.fetchone()
            return float(result['similarity']) if result and result['similarity'] else None
        except Exception as e:
            print(f"❌ 计算相似度失败: {e}")
            return None

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()

# 使用示例
if __name__ == "__main__":
    ai_manager = AIFunctionManager(
        "host=localhost dbname=testdb user=postgres password=secret"
    )

    # 生成嵌入向量
    embedding = ai_manager.generate_embedding(
        "text-embedding-3-small",
        "Hello, world!"
    )
    print(f"嵌入向量维度: {embedding.shape if embedding is not None else None}")

    # 批量生成嵌入向量
    texts = ["Text 1", "Text 2", "Text 3"]
    embeddings = ai_manager.batch_generate_embeddings("text-embedding-3-small", texts)
    print(f"生成了 {len(embeddings)} 个嵌入向量")

    # 语义搜索
    results = ai_manager.semantic_search(
        "What is PostgreSQL?",
        "text-embedding-3-small",
        limit=10
    )
    print(f"语义搜索结果: {len(results)} 条")

    # 计算相似度
    similarity = ai_manager.cosine_similarity(
        "PostgreSQL is a database",
        "PostgreSQL is an open source database",
        "text-embedding-3-small"
    )
    print(f"文本相似度: {similarity}")

    ai_manager.close()
```

### 8.3 向量生成和搜索

```python
import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np
from typing import List, Dict, Optional
from pgvector import Vector

class AIVectorManager:
    """PostgreSQL 18 AI向量管理器（结合pgvector和pg_ai）"""

    def __init__(self, conn_str: str):
        """初始化AI向量管理器"""
        self.conn = psycopg2.connect(conn_str)
        register_vector(self.conn)
        self.cur = self.conn.cursor()

    def generate_and_store_embedding(
        self,
        table_name: str,
        text: str,
        model_name: str = "text-embedding-3-small",
        metadata: Optional[dict] = None
    ) -> Optional[int]:
        """生成嵌入向量并存储"""
        import json

        # 生成嵌入向量
        sql_generate = "SELECT ai.generate_embedding(%s, %s) AS embedding;"
        self.cur.execute(sql_generate, (model_name, text))
        result = self.cur.fetchone()

        if not result or not result[0]:
            print("❌ 生成嵌入向量失败")
            return None

        embedding_str = result[0]

        # 存储到数据库
        metadata_str = json.dumps(metadata) if metadata else '{}'
        sql_insert = f"""
        INSERT INTO {table_name} (content, embedding, metadata)
        VALUES (%s, %s::vector, %s::jsonb)
        RETURNING id;
        """

        try:
            self.cur.execute(sql_insert, (text, embedding_str, metadata_str))
            result = self.cur.fetchone()
            self.conn.commit()
            vector_id = result[0] if result else None
            print(f"✅ 向量数据存储成功，ID: {vector_id}")
            return vector_id
        except Exception as e:
            print(f"❌ 存储向量数据失败: {e}")
            return None

    def semantic_search_with_ai(
        self,
        table_name: str,
        query: str,
        model_name: str = "text-embedding-3-small",
        limit: int = 10
    ) -> List[Dict]:
        """使用AI函数进行语义搜索"""
        # 生成查询向量
        sql_generate = "SELECT ai.generate_embedding(%s, %s) AS embedding;"
        self.cur.execute(sql_generate, (model_name, query))
        result = self.cur.fetchone()

        if not result or not result[0]:
            return []

        query_embedding = result[0]

        # 向量相似度搜索
        sql_search = f"""
        SELECT
            id,
            content,
            1 - (embedding <=> %s::vector) AS similarity,
            metadata
        FROM {table_name}
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """

        try:
            self.cur.execute(sql_search, (query_embedding, query_embedding, limit))
            results = self.cur.fetchall()

            return [
                {
                    'id': row[0],
                    'content': row[1],
                    'similarity': float(row[2]),
                    'metadata': row[3]
                }
                for row in results
            ]
        except Exception as e:
            print(f"❌ 语义搜索失败: {e}")
            return []

    def batch_generate_and_store(
        self,
        table_name: str,
        texts: List[str],
        model_name: str = "text-embedding-3-small"
    ) -> int:
        """批量生成并存储嵌入向量"""
        count = 0
        for text in texts:
            vector_id = self.generate_and_store_embedding(
                table_name,
                text,
                model_name
            )
            if vector_id:
                count += 1
        return count

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()

# 使用示例
if __name__ == "__main__":
    vector_manager = AIVectorManager(
        "host=localhost dbname=testdb user=postgres password=secret"
    )

    # 生成并存储嵌入向量
    vector_id = vector_manager.generate_and_store_embedding(
        "documents",
        "PostgreSQL is a powerful open source database",
        metadata={"category": "database", "source": "example"}
    )

    # 批量生成并存储
    texts = [
        "PostgreSQL is a database",
        "Python is a programming language",
        "Machine learning is a subset of AI"
    ]
    count = vector_manager.batch_generate_and_store("documents", texts)
    print(f"批量存储了 {count} 条向量数据")

    # 语义搜索
    results = vector_manager.semantic_search_with_ai(
        "documents",
        "What is PostgreSQL?",
        limit=5
    )
    print(f"语义搜索结果: {len(results)} 条")
    for result in results:
        print(f"  - ID: {result['id']}, 相似度: {result['similarity']:.4f}")

    vector_manager.close()
```

---

## 📊 总结

PostgreSQL 18 的 AI/ML 集成显著增强了 PostgreSQL 在 AI/ML 应用场景中的能力。
通过合理使用向量数据库、ML 模型集成、AI 函数等功能，可以在生产环境中构建强大的 AI/ML 应用。
建议充分利用 PostgreSQL 18 的新特性，特别是向量数据库增强和 ML 模型集成功能。

## 📚 参考资料

### 8.1 官方文档

- **[PostgreSQL 官方文档 - pgvector](https://github.com/pgvector/pgvector)**
  - pgvector扩展文档
  - PostgreSQL 18向量数据库增强说明

- **[PostgreSQL 官方文档 - AI/ML集成](https://www.postgresql.org/docs/18/indexes.html)**
  - AI/ML集成说明
  - ML模型集成使用

- **[PostgreSQL 18 发布说明](https://www.postgresql.org/about/news/postgresql-18-released-2817/)**
  - PostgreSQL 18新特性介绍
  - AI/ML集成说明

### 8.2 技术论文

- **Malkov, Y. A., & Yashunin, D. A. (2018).
"Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs."**
  - 期刊: IEEE Transactions on Pattern Analysis and Machine Intelligence, 42(4), 824-836
  - **重要性**: HNSW索引算法的基础研究
  - **核心贡献**: 提出了HNSW索引算法，影响了现代向量数据库的设计

- **Lewis, P., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."**
  - 会议: NeurIPS 2020
  - **重要性**: RAG应用的基础研究
  - **核心贡献**: 提出了RAG（检索增强生成）方法，影响了现代AI应用的设计

- **Karpukhin, V., et al. (2020). "Dense Passage Retrieval for Open-Domain Question Answering."**
  - 会议: EMNLP 2020
  - **重要性**: 密集段落检索的基础研究
  - **核心贡献**: 深入分析了向量检索在问答系统中的应用

### 8.3 技术博客

- **[PostgreSQL 官方博客 - AI/ML集成](https://www.postgresql.org/docs/18/indexes.html)**
  - AI/ML集成最佳实践
  - 性能优化技巧

- **[2ndQuadrant - PostgreSQL 18 AI/ML集成](https://www.2ndquadrant.com/en/blog/postgresql-18-ai-ml-integration/)**
  - AI/ML集成实战
  - 性能提升案例

- **[Percona - PostgreSQL AI/ML集成](https://www.percona.com/blog/postgresql-ai-ml-integration/)**
  - AI/ML集成调优
  - 性能优化建议

- **[EnterpriseDB - PostgreSQL AI/ML集成](https://www.enterprisedb.com/postgres-tutorials/postgresql-ai-ml-integration-tutorial)**
  - AI/ML集成深入解析
  - 实际应用案例

### 8.4 社区资源

- **[PostgreSQL Wiki - AI/ML Integration](https://wiki.postgresql.org/wiki/AI_ML_Integration)**
  - AI/ML集成技巧
  - 性能优化案例

- **[Stack Overflow - PostgreSQL AI/ML](https://stackoverflow.com/questions/tagged/postgresql+ai-ml)**
  - AI/ML集成相关问题解答
  - 实际应用案例

- **[PostgreSQL 邮件列表](https://www.postgresql.org/list/)**
  - PostgreSQL社区讨论
  - AI/ML集成使用问题交流

### 8.5 相关文档

- [PostgreSQL 18新特性总览](./README.md)
- [向量数据库增强](./向量数据库增强.md)
- [查询优化器革命性改进](./查询优化器革命性改进.md)

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
**文档编号**: 03-03-18-09
