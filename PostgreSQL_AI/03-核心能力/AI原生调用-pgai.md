# AI原生调用 - pgai

> **文档编号**: AI-03-02
> **最后更新**: 2025年1月
> **主题**: 03-核心能力
> **子主题**: 02-AI原生调用

## 📑 目录

- [AI原生调用 - pgai](#ai原生调用---pgai)
  - [📑 目录](#-目录)
  - [一、概述](#一概述)
  - [二、核心功能](#二核心功能)
    - [2.1 embedding() 函数](#21-embedding-函数)
    - [2.2 chat\_complete() 函数](#22-chat_complete-函数)
    - [2.3 vectorizer() 自动向量化](#23-vectorizer-自动向量化)
  - [三、使用场景](#三使用场景)
    - [3.1 实时Embedding生成](#31-实时embedding生成)
    - [3.2 SQL内LLM调用](#32-sql内llm调用)
    - [3.3 自动化向量化管道](#33-自动化向量化管道)
  - [四、配置与部署](#四配置与部署)
    - [4.1 安装配置](#41-安装配置)
    - [4.2 API密钥管理](#42-api密钥管理)
    - [4.3 模型选择](#43-模型选择)
  - [五、性能优化](#五性能优化)
    - [5.1 批量处理](#51-批量处理)
    - [5.2 缓存策略](#52-缓存策略)
    - [5.3 成本优化](#53-成本优化)
  - [六、最佳实践](#六最佳实践)
  - [七、关联主题](#七关联主题)
  - [八、对标资源](#八对标资源)
    - [官方文档](#官方文档)
    - [企业案例](#企业案例)
    - [技术文档](#技术文档)

## 一、概述

pgai是PostgreSQL的AI原生扩展，允许在SQL语句中直接调用OpenAI、Anthropic等LLM服务，实现Embedding生成、文本生成等AI功能，无需外部应用层代码。

## 二、核心功能

### 2.1 embedding() 函数

生成文本的向量嵌入：

```sql
-- 使用OpenAI生成Embedding
SELECT ai.embedding(
    'text-embedding-3-small',
    'PostgreSQL AI应用'
) AS embedding;

-- 结果: vector(1536)
```

**支持的模型**:

- OpenAI: `text-embedding-3-small`, `text-embedding-3-large`
- 其他: 通过配置支持

### 2.2 chat_complete() 函数

在SQL中直接调用LLM生成文本：

```sql
-- 调用GPT-4生成回答
SELECT ai.chat_complete(
    'gpt-4',
    '分析PostgreSQL在AI时代的优势'
) AS response;

-- 返回JSONB格式
-- {"content": "...", "model": "gpt-4", "usage": {...}}
```

**支持的模型**:

- OpenAI: `gpt-4`, `gpt-3.5-turbo`
- Anthropic: `claude-3-opus`, `claude-3-sonnet`
- 其他: 通过配置支持

### 2.3 vectorizer() 自动向量化

自动为表创建向量化管道：

```sql
-- 创建自动向量化器
SELECT ai.create_vectorizer(
    'news_articles'::regclass,
    destination => 'news_embeddings',
    embedding => ai.embedding_openai('text-embedding-3-small', 'content'),
    chunking => ai.chunking_recursive_character_text_splitter('content')
);

-- 后续INSERT自动触发Embedding生成
INSERT INTO news_articles(title, content)
VALUES ('Fed Raises Rates', 'The Federal Reserve...');
-- 自动同步生成向量到news_embeddings表
```

## 三、使用场景

### 3.1 实时Embedding生成

```sql
-- 实时生成商品描述的Embedding
UPDATE products
SET description_embedding = ai.embedding(
    'text-embedding-3-small',
    description
)
WHERE description_embedding IS NULL;
```

### 3.2 SQL内LLM调用

```sql
-- 创建RAG查询函数
CREATE OR REPLACE FUNCTION rag_query(query_text TEXT)
RETURNS TEXT AS $$
DECLARE
    context TEXT;
    answer TEXT;
BEGIN
    -- 检索相关文档
    SELECT string_agg(content, E'\n\n')
    INTO context
    FROM document_chunks
    WHERE embedding <=> ai.embedding('text-embedding-3-small', query_text) < 0.8
    ORDER BY embedding <=> ai.embedding('text-embedding-3-small', query_text)
    LIMIT 5;

    -- 调用LLM生成回答
    answer := ai.chat_complete(
        'gpt-4',
        format('基于以下上下文回答问题:\n\n%s\n\n问题: %s', context, query_text)
    )->>'content';

    RETURN answer;
END;
$$ LANGUAGE plpgsql;
```

### 3.3 自动化向量化管道

```sql
-- 为现有表创建向量化管道
SELECT ai.create_vectorizer(
    table_name => 'products',
    destination => 'product_embeddings',
    embedding => ai.embedding_openai('text-embedding-3-small', 'description'),
    chunking => NULL  -- 不进行分块
);

-- 批量处理历史数据
SELECT ai.vectorize_table('products', 'product_embeddings');
```

## 四、配置与部署

### 4.1 安装配置

```sql
-- 安装扩展
CREATE EXTENSION pgai;

-- 配置OpenAI API
ALTER SYSTEM SET pgai.openai_api_key = 'sk-...';
SELECT pg_reload_conf();
```

### 4.2 API密钥管理

```sql
-- 使用环境变量 (推荐)
-- 在postgresql.conf中设置
pgai.openai_api_key = '${OPENAI_API_KEY}'

-- 或使用Vault等密钥管理工具
```

### 4.3 模型选择

```sql
-- 配置默认模型
ALTER SYSTEM SET pgai.default_embedding_model = 'text-embedding-3-small';
ALTER SYSTEM SET pgai.default_chat_model = 'gpt-4';
```

## 五、性能优化

### 5.1 批量处理

```sql
-- 批量生成Embedding (更高效)
SELECT ai.embedding_batch(
    'text-embedding-3-small',
    ARRAY['文本1', '文本2', '文本3']
) AS embeddings;
```

### 5.2 缓存策略

```sql
-- 启用Embedding缓存
ALTER SYSTEM SET pgai.cache_embeddings = true;
ALTER SYSTEM SET pgai.cache_ttl = '7 days';
```

### 5.3 成本优化

```sql
-- 使用更便宜的模型
SELECT ai.embedding('text-embedding-3-small', text)  -- 更便宜
FROM documents;

-- 批量处理减少API调用
SELECT ai.embedding_batch('text-embedding-3-small', texts)
FROM (SELECT array_agg(content) AS texts FROM documents) sub;
```

## 六、最佳实践

1. **API密钥安全**:
   - 使用环境变量或密钥管理工具
   - 不要在SQL中硬编码密钥

2. **成本控制**:
   - 使用缓存避免重复调用
   - 批量处理减少API调用次数
   - 选择合适的模型 (small vs large)

3. **错误处理**:

   ```sql
   -- 添加错误处理
   BEGIN
       SELECT ai.chat_complete('gpt-4', query);
   EXCEPTION
       WHEN OTHERS THEN
           RAISE NOTICE 'LLM调用失败: %', SQLERRM;
   END;
   ```

4. **性能监控**:

   ```sql
   -- 监控API调用
   SELECT
       model,
       COUNT(*) AS call_count,
       AVG(response_time) AS avg_time
   FROM ai.api_log
   WHERE created_at > NOW() - INTERVAL '1 hour'
   GROUP BY model;
   ```

## 七、关联主题

- [向量处理能力 (pgvector)](./向量处理能力-pgvector.md) - 存储生成的向量
- [RAG系统设计](../04-应用场景/RAG系统设计.md) - 使用pgai实现RAG
- [数据注入与治理](./数据注入与治理.md) - 自动化向量化管道

## 八、对标资源

### 官方文档

- [pgai GitHub](https://github.com/pgai/pgai)
- [Timescale pgai文档](https://docs.timescale.com/ai/)

### 企业案例

- **Timescale MarketReader**: 使用pgai实现新闻Embedding自动化
- **开发周期**: 3个月 → 2周 (缩短85%)
- **人力成本**: 节约50%

### 技术文档

- OpenAI Embeddings API文档
- Anthropic Claude API文档

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**文档编号**: AI-03-02
