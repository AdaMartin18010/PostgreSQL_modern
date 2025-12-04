# 【深入】PostgreSQL全文搜索完整实战指南

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 12+
> **难度等级**: ⭐⭐⭐⭐ 高级 | **预计学习时间**: 6-8小时

---

## 📋 目录

- [【深入】PostgreSQL全文搜索完整实战指南](#深入postgresql全文搜索完整实战指南)
  - [📋 目录](#-目录)
  - [1. 课程概述](#1-课程概述)
    - [1.1 什么是全文搜索？](#11-什么是全文搜索)
      - [传统LIKE vs 全文搜索](#传统like-vs-全文搜索)
    - [1.2 核心概念](#12-核心概念)
    - [1.3 PostgreSQL FTS优势](#13-postgresql-fts优势)
  - [2. 全文搜索基础](#2-全文搜索基础)
    - [2.1 基本操作符](#21-基本操作符)
    - [2.2 查询操作符](#22-查询操作符)
    - [2.3 简单搜索示例](#23-简单搜索示例)
  - [3. tsvector与tsquery](#3-tsvector与tsquery)
    - [3.1 tsvector详解](#31-tsvector详解)
    - [3.2 tsquery详解](#32-tsquery详解)
    - [3.3 存储tsvector列](#33-存储tsvector列)
  - [4. 文本搜索配置](#4-文本搜索配置)
    - [4.1 查看可用配置](#41-查看可用配置)
    - [4.2 配置组成](#42-配置组成)
    - [4.3 自定义配置](#43-自定义配置)
  - [5. 排名与相关性](#5-排名与相关性)
    - [5.1 ts\_rank排名](#51-ts_rank排名)
    - [5.2 ts\_rank\_cd排名（考虑距离）](#52-ts_rank_cd排名考虑距离)
    - [5.3 归一化选项](#53-归一化选项)
    - [5.4 自定义排名函数](#54-自定义排名函数)
  - [6. 索引优化](#6-索引优化)
    - [6.1 GIN索引](#61-gin索引)
    - [6.2 GIN vs GiST](#62-gin-vs-gist)
    - [6.3 部分索引](#63-部分索引)
    - [6.4 表达式索引](#64-表达式索引)
  - [7. 多语言支持](#7-多语言支持)
    - [7.1 内置语言配置](#71-内置语言配置)
    - [7.2 中文全文搜索（zhparser）](#72-中文全文搜索zhparser)
    - [7.3 多语言字段](#73-多语言字段)
  - [8. 高级特性](#8-高级特性)
    - [8.1 高亮显示](#81-高亮显示)
    - [8.2 搜索建议（Did You Mean?）](#82-搜索建议did-you-mean)
    - [8.3 分面搜索（Faceted Search）](#83-分面搜索faceted-search)
    - [8.4 搜索自动补全](#84-搜索自动补全)
  - [9. 性能优化](#9-性能优化)
    - [9.1 查询优化](#91-查询优化)
    - [9.2 索引维护](#92-索引维护)
    - [9.3 分区表优化](#93-分区表优化)
    - [9.4 并行查询](#94-并行查询)
  - [10. 生产实战案例](#10-生产实战案例)
    - [10.1 案例1：博客搜索](#101-案例1博客搜索)
    - [10.2 案例2：电商产品搜索](#102-案例2电商产品搜索)
    - [10.3 案例3：多租户文档搜索](#103-案例3多租户文档搜索)
  - [11. 与ElasticSearch对比](#11-与elasticsearch对比)
    - [11.1 功能对比](#111-功能对比)
    - [11.2 选择建议](#112-选择建议)
  - [12. 最佳实践](#12-最佳实践)
    - [12.1 设计原则](#121-设计原则)
    - [12.2 查询优化Checklist](#122-查询优化checklist)
    - [12.3 安全注意事项](#123-安全注意事项)
  - [📚 延伸阅读](#-延伸阅读)
    - [官方资源](#官方资源)
    - [推荐工具](#推荐工具)
  - [✅ 学习检查清单](#-学习检查清单)
  - [💡 下一步学习](#-下一步学习)

1. [全文搜索基础](#2-全文搜索基础)
2. [tsvector与tsquery](#3-tsvector与tsquery)
3. [文本搜索配置](#4-文本搜索配置)
4. [排名与相关性](#5-排名与相关性)
5. [索引优化](#6-索引优化)
6. [多语言支持](#7-多语言支持)
7. [高级特性](#8-高级特性)
8. [性能优化](#9-性能优化)
9. [生产实战案例](#10-生产实战案例)
10. [与ElasticSearch对比](#11-与elasticsearch对比)
11. [最佳实践](#12-最佳实践)

---

## 1. 课程概述

### 1.1 什么是全文搜索？

**全文搜索**（Full-Text Search, FTS）是在文档集合中搜索符合查询条件的文档，并按相关性排序。

#### 传统LIKE vs 全文搜索

```sql
-- ❌ 传统LIKE搜索的问题
SELECT * FROM documents WHERE content LIKE '%postgresql%';
-- 问题：
-- 1. 无法使用索引（全表扫描）
-- 2. 不支持词干提取（search vs searching）
-- 3. 无相关性排序
-- 4. 不支持同义词
-- 5. 性能差（大数据集）

-- ✅ 全文搜索解决方案
SELECT * FROM documents
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'postgresql')
ORDER BY ts_rank(to_tsvector('english', content), to_tsquery('english', 'postgresql')) DESC;
-- 优势：
-- ✅ GIN索引加速
-- ✅ 词干提取（search = searching = searches）
-- ✅ 相关性排序
-- ✅ 支持布尔查询
-- ✅ 高性能
```

### 1.2 核心概念

| 概念 | 说明 | 示例 |
|------|------|------|
| **文档** | 被搜索的文本单元 | 文章、评论、产品描述 |
| **词位** | 标准化的词元 | "running" → "run" |
| **tsvector** | 文档的词位向量 | `'run':1 'fast':2` |
| **tsquery** | 搜索查询 | `'run & fast'` |
| **词典** | 词干提取规则 | english, chinese, simple |
| **配置** | 语言+词典组合 | pg_catalog.english |

### 1.3 PostgreSQL FTS优势

```text
PostgreSQL全文搜索 vs ElasticSearch:

✅ 优势：
1. 无需额外服务（All-in-One）
2. ACID事务保证
3. 实时更新（无延迟）
4. SQL原生集成
5. 数据一致性保证
6. 运维成本低

⚠️ 劣势：
1. 大规模数据（>100GB）性能不如ES
2. 分布式搜索需自行实现
3. 高级分析功能较少

适用场景：
✅ 中小型应用（< 100GB文本）
✅ 需要事务一致性
✅ 已使用PostgreSQL
✅ 简化架构
```

---

## 2. 全文搜索基础

### 2.1 基本操作符

```sql
-- @@ 匹配操作符
SELECT 'a fat cat sat on a mat'::tsvector @@ 'cat'::tsquery;
-- 结果：t（true）

SELECT 'a fat cat sat on a mat'::tsvector @@ 'dog'::tsquery;
-- 结果：f（false）

-- to_tsvector: 文本 → tsvector
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- 结果：'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2
-- 注意：
-- 1. 去除停用词（the, over等）
-- 2. 词干提取（jumps → jump, lazy → lazi）
-- 3. 添加位置信息（:2表示第2个词）

-- to_tsquery: 查询文本 → tsquery
SELECT to_tsquery('english', 'quick & fox');
-- 结果：'quick' & 'fox'

SELECT to_tsquery('english', 'quick | fox');
-- 结果：'quick' | 'fox'

SELECT to_tsquery('english', 'quick & !dog');
-- 结果：'quick' & !'dog'
```

### 2.2 查询操作符

```sql
-- & (AND)
SELECT to_tsvector('english', 'The quick brown fox') @@
       to_tsquery('english', 'quick & brown');
-- 结果：t

-- | (OR)
SELECT to_tsvector('english', 'The quick brown fox') @@
       to_tsquery('english', 'quick | slow');
-- 结果：t（包含quick）

-- ! (NOT)
SELECT to_tsvector('english', 'The quick brown fox') @@
       to_tsquery('english', 'quick & !dog');
-- 结果：t（有quick，无dog）

-- <-> (FOLLOWED BY)
SELECT to_tsvector('english', 'quick brown fox') @@
       to_tsquery('english', 'quick <-> brown');
-- 结果：t（quick紧跟brown）

-- <N> (距离操作符)
SELECT to_tsvector('english', 'quick brown fox') @@
       to_tsquery('english', 'quick <2> fox');
-- 结果：t（quick和fox之间距离<=2）
```

### 2.3 简单搜索示例

```sql
-- 创建示例表
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入数据
INSERT INTO articles (title, content) VALUES
('PostgreSQL Tutorial', 'Learn PostgreSQL full-text search capabilities'),
('Database Optimization', 'Optimize your database queries for better performance'),
('Advanced SQL', 'Master advanced SQL techniques including full-text search');

-- 基础搜索
SELECT id, title
FROM articles
WHERE to_tsvector('english', title || ' ' || content) @@
      to_tsquery('english', 'postgresql');

-- 结果：返回包含postgresql的文章
```

---

## 3. tsvector与tsquery

### 3.1 tsvector详解

```sql
-- 手动创建tsvector
SELECT 'a:1 fat:2 cat:3'::tsvector;
-- 格式：'词位:位置 词位:位置 ...'

-- 合并tsvector
SELECT 'a:1 fat:2'::tsvector || 'cat:3'::tsvector;
-- 结果：'a':1 'cat':3 'fat':2

-- 设置权重（A最高，D最低）
SELECT setweight(to_tsvector('english', 'Important Title'), 'A') ||
       setweight(to_tsvector('english', 'Less important content'), 'D');
-- 结果：'content':5D 'import':1A,3D 'less':2D 'titl':2A

-- 查看词位位置
SELECT ts_debug('english', 'The quick brown fox jumps');
-- 返回详细的词法分析信息
```

### 3.2 tsquery详解

```sql
-- plainto_tsquery：简单查询（自动处理AND）
SELECT plainto_tsquery('english', 'quick fox');
-- 结果：'quick' & 'fox'

-- phraseto_tsquery：短语查询（保持顺序）
SELECT phraseto_tsquery('english', 'quick brown fox');
-- 结果：'quick' <-> 'brown' <-> 'fox'

-- websearch_to_tsquery：类似Google搜索
SELECT websearch_to_tsquery('english', 'quick fox -dog');
-- 结果：'quick' & 'fox' & !'dog'

SELECT websearch_to_tsquery('english', '"quick fox" OR dog');
-- 结果：'quick' <-> 'fox' | 'dog'

-- 查询重写（同义词）
SELECT to_tsquery('english', 'supernovae')::text;
-- 可配置为：'supernovae | supernova | supernovas'
```

### 3.3 存储tsvector列

```sql
-- 方案1：生成列（PostgreSQL 12+，推荐）
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'D')
    ) STORED
);

-- 插入数据（search_vector自动生成）
INSERT INTO documents (title, content) VALUES
('PostgreSQL Full-Text Search', 'This is a comprehensive guide to PostgreSQL FTS');

-- 查询
SELECT id, title
FROM documents
WHERE search_vector @@ to_tsquery('english', 'postgresql & search');

-- 方案2：触发器更新
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    search_vector tsvector
);

CREATE FUNCTION documents_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.content, '')), 'D');
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER documents_search_update BEFORE INSERT OR UPDATE
ON documents FOR EACH ROW EXECUTE FUNCTION documents_search_trigger();
```

---

## 4. 文本搜索配置

### 4.1 查看可用配置

```sql
-- 查看所有配置
SELECT cfgname FROM pg_ts_config;
-- 常见：english, simple, chinese（需要zh_cn扩展）

-- 查看默认配置
SHOW default_text_search_config;
-- 通常：pg_catalog.english

-- 修改默认配置
SET default_text_search_config = 'pg_catalog.simple';
```

### 4.2 配置组成

```sql
-- 查看配置的解析器和词典
SELECT * FROM pg_ts_config_map WHERE mapcfg = 'english'::regconfig;

-- Token类型
SELECT * FROM pg_ts_token_type('default');
-- 包括：word, number, email, url, host等

-- 词典链
-- english配置的词典链：
-- 1. english_stem（词干提取）
-- 2. simple（简单规则）
```

### 4.3 自定义配置

```sql
-- 创建自定义配置
CREATE TEXT SEARCH CONFIGURATION my_config (COPY = english);

-- 修改词典映射
ALTER TEXT SEARCH CONFIGURATION my_config
    ALTER MAPPING FOR word WITH english_stem, simple;

-- 添加同义词词典
CREATE TEXT SEARCH DICTIONARY my_synonyms (
    TEMPLATE = synonym,
    SYNONYMS = my_synonyms
);

-- my_synonyms.syn文件内容：
-- postgres postgresql pg
-- db database

ALTER TEXT SEARCH CONFIGURATION my_config
    ALTER MAPPING FOR word WITH my_synonyms, english_stem;

-- 使用自定义配置
SELECT to_tsvector('my_config', 'I love postgres database');
-- "postgres" → "postgresql"（同义词）
```

---

## 5. 排名与相关性

### 5.1 ts_rank排名

```sql
-- ts_rank：基于词频的排名
SELECT
    id,
    title,
    ts_rank(search_vector, query) AS rank
FROM documents, to_tsquery('english', 'postgresql & search') query
WHERE search_vector @@ query
ORDER BY rank DESC;

-- ts_rank参数：
-- [ weights (float4[]), vector tsvector, query tsquery, normalization integer ]
-- weights: {D权重, C权重, B权重, A权重}
SELECT
    id,
    title,
    ts_rank('{0.1, 0.2, 0.4, 1.0}'::float4[], search_vector, query) AS rank
FROM documents, to_tsquery('english', 'postgresql') query
WHERE search_vector @@ query
ORDER BY rank DESC;
-- A权重（标题）影响最大
```

### 5.2 ts_rank_cd排名（考虑距离）

```sql
-- ts_rank_cd：考虑词位距离的排名
SELECT
    id,
    title,
    ts_rank_cd(search_vector, query) AS rank
FROM documents, to_tsquery('english', 'postgresql <-> search') query
WHERE search_vector @@ query
ORDER BY rank DESC;
-- 词位距离越近，排名越高
```

### 5.3 归一化选项

```sql
/*
归一化选项（按位或组合）：
0: 默认（文档长度归一化）
1: 除以 (1 + log(文档长度))
2: 除以文档长度
4: 除以唯一词数
8: 除以 (1 + log(唯一词数))
16: 除以 (1 + log(文档长度))
32: rank / (rank + 1)
*/

-- 示例：长度归一化 | 唯一词归一化
SELECT
    id,
    title,
    ts_rank(search_vector, query, 2 | 8) AS rank
FROM documents, to_tsquery('english', 'postgresql') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

### 5.4 自定义排名函数

```sql
-- 综合排名：FTS排名 + 其他因子
CREATE FUNCTION custom_rank(
    doc_vector tsvector,
    query tsquery,
    view_count INT,
    like_count INT,
    created_at TIMESTAMPTZ
) RETURNS FLOAT AS $$
    SELECT
        ts_rank(doc_vector, query) * 10.0 +           -- 文本相关性（10倍权重）
        LOG(view_count + 1) * 0.5 +                   -- 浏览量
        LOG(like_count + 1) * 1.0 +                   -- 点赞数
        (EXTRACT(EPOCH FROM NOW() - created_at) / 86400) * -0.01  -- 时间衰减
$$ LANGUAGE SQL IMMUTABLE;

-- 使用
SELECT
    id,
    title,
    custom_rank(search_vector, query, view_count, like_count, created_at) AS rank
FROM articles, to_tsquery('english', 'postgresql') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

---

## 6. 索引优化

### 6.1 GIN索引

```sql
-- 创建GIN索引（最常用）
CREATE INDEX documents_search_idx ON documents USING GIN(search_vector);

-- 查询自动使用索引
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title
FROM documents
WHERE search_vector @@ to_tsquery('english', 'postgresql');

-- 输出：
-- Bitmap Heap Scan on documents
--   Recheck Cond: (search_vector @@ to_tsquery(...))
--   ->  Bitmap Index Scan on documents_search_idx  ← 使用索引
--         Index Cond: (search_vector @@ to_tsquery(...))
```

### 6.2 GIN vs GiST

```sql
-- GIN索引（推荐）
CREATE INDEX documents_gin_idx ON documents USING GIN(search_vector);
-- 优点：查询快（3x+）
-- 缺点：构建慢，占用空间大，更新稍慢

-- GiST索引
CREATE INDEX documents_gist_idx ON documents USING GIST(search_vector);
-- 优点：构建快，更新快
-- 缺点：查询慢，占用空间小

-- 选择建议：
-- 99%情况使用GIN
-- 只有频繁更新且查询不频繁时用GiST
```

### 6.3 部分索引

```sql
-- 只索引已发布的文档
CREATE INDEX documents_published_search_idx
ON documents USING GIN(search_vector)
WHERE published = TRUE AND deleted_at IS NULL;

-- 查询必须包含相同条件
SELECT id, title
FROM documents
WHERE search_vector @@ to_tsquery('english', 'postgresql')
  AND published = TRUE
  AND deleted_at IS NULL;
```

### 6.4 表达式索引

```sql
-- 索引动态生成的tsvector
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT
);

-- 无需存储tsvector列，直接索引表达式
CREATE INDEX articles_search_idx ON articles USING GIN(
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
);

-- 查询必须使用相同表达式
SELECT id, title
FROM articles
WHERE to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
      @@ to_tsquery('english', 'postgresql');
```

---

## 7. 多语言支持

### 7.1 内置语言配置

```sql
-- 查看支持的语言
SELECT cfgname FROM pg_ts_config WHERE cfgname LIKE '%'
ORDER BY cfgname;

-- 常见配置：
-- arabic, danish, dutch, english, finnish, french, german
-- hungarian, italian, norwegian, portuguese, romanian, russian
-- spanish, swedish, turkish
```

### 7.2 中文全文搜索（zhparser）

```sql
-- 安装zhparser扩展
CREATE EXTENSION zhparser;

-- 创建中文配置
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR n,v,a,i,e,l WITH simple;

-- 测试
SELECT to_tsvector('chinese', '我爱PostgreSQL数据库');
-- 结果：'postgre':2 'sql':2 '我':1 '数据库':2 '爱':1

SELECT to_tsvector('chinese', '我爱PostgreSQL数据库') @@
       to_tsquery('chinese', 'PostgreSQL & 数据库');
-- 结果：t

-- 实际使用
CREATE TABLE articles_cn (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('chinese', coalesce(title, '') || ' ' || coalesce(content, ''))
    ) STORED
);

CREATE INDEX articles_cn_search_idx ON articles_cn USING GIN(search_vector);
```

### 7.3 多语言字段

```sql
-- 存储多语言内容
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name_en TEXT,
    name_zh TEXT,
    description_en TEXT,
    description_zh TEXT,
    search_vector_en tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(name_en, '') || ' ' || coalesce(description_en, ''))
    ) STORED,
    search_vector_zh tsvector GENERATED ALWAYS AS (
        to_tsvector('chinese', coalesce(name_zh, '') || ' ' || coalesce(description_zh, ''))
    ) STORED
);

-- 创建索引
CREATE INDEX products_search_en_idx ON products USING GIN(search_vector_en);
CREATE INDEX products_search_zh_idx ON products USING GIN(search_vector_zh);

-- 多语言搜索
SELECT id, name_en, name_zh
FROM products
WHERE search_vector_en @@ to_tsquery('english', 'phone')
   OR search_vector_zh @@ to_tsquery('chinese', '手机');
```

---

## 8. 高级特性

### 8.1 高亮显示

```sql
-- ts_headline：高亮匹配词
SELECT
    id,
    title,
    ts_headline('english', content, query,
        'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=20'
    ) AS highlighted
FROM documents, to_tsquery('english', 'postgresql & search') query
WHERE search_vector @@ query;

-- 输出示例：
-- "This is a comprehensive guide to <mark>PostgreSQL</mark> full-text <mark>search</mark>..."

-- 自定义高亮选项
SELECT ts_headline(
    'english',
    'PostgreSQL is a powerful database. PostgreSQL supports full-text search.',
    to_tsquery('english', 'postgresql'),
    'StartSel=**, StopSel=**, MaxFragments=2, FragmentDelimiter=...'
);
-- 输出："**PostgreSQL** is a powerful database...**PostgreSQL** supports full-text search."
```

### 8.2 搜索建议（Did You Mean?）

```sql
-- 使用pg_trgm扩展实现模糊匹配
CREATE EXTENSION pg_trgm;

-- 创建搜索词表
CREATE TABLE search_terms (
    term TEXT PRIMARY KEY,
    frequency INT DEFAULT 0
);

CREATE INDEX search_terms_trgm_idx ON search_terms USING GIN(term gin_trgm_ops);

-- 记录搜索词
INSERT INTO search_terms (term, frequency)
VALUES ('postgresql', 1)
ON CONFLICT (term) DO UPDATE SET frequency = search_terms.frequency + 1;

-- 查找相似词（拼写错误纠正）
SELECT term, similarity(term, 'postgresqll') AS sim
FROM search_terms
WHERE term % 'postgresqll'  -- % 是相似操作符
ORDER BY sim DESC
LIMIT 5;
-- 输出建议："postgresql"（相似度最高）
```

### 8.3 分面搜索（Faceted Search）

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    brand TEXT,
    price NUMERIC(10,2),
    search_vector tsvector
);

-- 分面搜索查询
WITH search_results AS (
    SELECT * FROM products
    WHERE search_vector @@ to_tsquery('english', 'laptop')
)
SELECT
    -- 主结果
    (SELECT json_agg(row_to_json(search_results)) FROM search_results) AS results,

    -- 分类分面
    (SELECT json_object_agg(category, count)
     FROM (
         SELECT category, COUNT(*) as count
         FROM search_results
         GROUP BY category
     ) sub
    ) AS category_facets,

    -- 品牌分面
    (SELECT json_object_agg(brand, count)
     FROM (
         SELECT brand, COUNT(*) as count
         FROM search_results
         GROUP BY brand
     ) sub
    ) AS brand_facets,

    -- 价格区间分面
    (SELECT json_object_agg(price_range, count)
     FROM (
         SELECT
             CASE
                 WHEN price < 500 THEN '0-500'
                 WHEN price < 1000 THEN '500-1000'
                 WHEN price < 2000 THEN '1000-2000'
                 ELSE '2000+'
             END AS price_range,
             COUNT(*) as count
         FROM search_results
         GROUP BY price_range
     ) sub
    ) AS price_facets;
```

### 8.4 搜索自动补全

```sql
-- 使用prefix匹配实现自动补全
CREATE TABLE search_suggestions (
    id SERIAL PRIMARY KEY,
    term TEXT NOT NULL,
    frequency INT DEFAULT 0
);

-- 使用GIN索引支持prefix搜索
CREATE INDEX search_suggestions_term_trgm_idx ON search_suggestions
USING GIN(term gin_trgm_ops);

-- 或使用btree支持text_pattern_ops
CREATE INDEX search_suggestions_term_pattern_idx ON search_suggestions(term text_pattern_ops);

-- 自动补全查询
SELECT term, frequency
FROM search_suggestions
WHERE term ILIKE 'postgre%'
ORDER BY frequency DESC, term
LIMIT 10;

-- 前端集成（防抖后查询）
-- input: "postgre"
-- 建议: ["postgresql", "postgres", "postgrest", ...]
```

---

## 9. 性能优化

### 9.1 查询优化

```sql
-- ❌ 慢查询：每次动态生成tsvector
SELECT * FROM articles
WHERE to_tsvector('english', title || ' ' || content) @@
      to_tsquery('english', 'postgresql');

-- ✅ 快查询：使用预计算的tsvector列
SELECT * FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql');

-- ✅ 更快：使用简化的查询函数
SELECT * FROM articles
WHERE search_vector @@ plainto_tsquery('english', 'postgresql search');
-- plainto_tsquery比to_tsquery更快
```

### 9.2 索引维护

```sql
-- 查看索引膨胀
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE indexname LIKE '%search%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- 重建膨胀的索引
REINDEX INDEX CONCURRENTLY documents_search_idx;

-- 或使用VACUUM
VACUUM ANALYZE documents;
```

### 9.3 分区表优化

```sql
-- 按时间分区大表
CREATE TABLE articles (
    id BIGSERIAL,
    title TEXT,
    content TEXT,
    search_vector tsvector,
    created_at DATE NOT NULL,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE articles_2024 PARTITION OF articles
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE articles_2025 PARTITION OF articles
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- 为每个分区创建索引
CREATE INDEX articles_2024_search_idx ON articles_2024 USING GIN(search_vector);
CREATE INDEX articles_2025_search_idx ON articles_2025 USING GIN(search_vector);

-- 查询自动使用分区裁剪
SELECT * FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql')
  AND created_at >= '2025-01-01';
-- 只扫描articles_2025分区
```

### 9.4 并行查询

```sql
-- 启用并行查询
SET max_parallel_workers_per_gather = 4;
SET parallel_tuple_cost = 0.01;

-- 大表自动并行扫描
EXPLAIN (ANALYZE)
SELECT * FROM large_articles
WHERE search_vector @@ to_tsquery('english', 'postgresql');

-- 输出可能包含：
-- Gather
--   Workers Planned: 4
--   ->  Parallel Bitmap Heap Scan on large_articles
```

---

## 10. 生产实战案例

### 10.1 案例1：博客搜索

```sql
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    author_id INT REFERENCES users(id),
    published BOOLEAN DEFAULT FALSE,
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 搜索向量（标题权重A，内容权重D）
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'D')
    ) STORED
);

-- 索引
CREATE INDEX blog_posts_search_idx ON blog_posts USING GIN(search_vector)
WHERE published = TRUE;

CREATE INDEX blog_posts_created_idx ON blog_posts(created_at DESC);

-- 搜索函数
CREATE OR REPLACE FUNCTION search_blog_posts(
    search_query TEXT,
    page_size INT DEFAULT 20,
    page_offset INT DEFAULT 0
)
RETURNS TABLE (
    id INT,
    title TEXT,
    slug TEXT,
    headline TEXT,
    rank REAL,
    created_at TIMESTAMPTZ
) AS $$
DECLARE
    query tsquery := websearch_to_tsquery('english', search_query);
BEGIN
    RETURN QUERY
    SELECT
        bp.id,
        bp.title,
        bp.slug,
        ts_headline('english', bp.content, query,
            'MaxWords=30, MinWords=15, StartSel=<mark>, StopSel=</mark>'
        ) AS headline,
        (ts_rank(bp.search_vector, query) * 10.0 +
         LOG(bp.view_count + 1) * 0.5 +
         LOG(bp.like_count + 1) * 1.0)::REAL AS rank,
        bp.created_at
    FROM blog_posts bp
    WHERE bp.search_vector @@ query
      AND bp.published = TRUE
    ORDER BY rank DESC, bp.created_at DESC
    LIMIT page_size
    OFFSET page_offset;
END;
$$ LANGUAGE plpgsql STABLE;

-- 使用
SELECT * FROM search_blog_posts('postgresql full text search', 20, 0);
```

### 10.2 案例2：电商产品搜索

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    brand TEXT,
    price NUMERIC(10,2),
    stock_count INT DEFAULT 0,
    rating NUMERIC(3,2) DEFAULT 0,
    review_count INT DEFAULT 0,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(brand, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'C') ||
        setweight(to_tsvector('english', coalesce(category, '')), 'D')
    ) STORED
);

CREATE INDEX products_search_idx ON products USING GIN(search_vector)
WHERE stock_count > 0;

-- 高级搜索（支持过滤、排序、分面）
CREATE OR REPLACE FUNCTION search_products(
    search_query TEXT,
    category_filter TEXT DEFAULT NULL,
    brand_filter TEXT DEFAULT NULL,
    min_price NUMERIC DEFAULT NULL,
    max_price NUMERIC DEFAULT NULL,
    sort_by TEXT DEFAULT 'relevance',  -- relevance, price_asc, price_desc, rating
    page_size INT DEFAULT 20,
    page_offset INT DEFAULT 0
)
RETURNS TABLE (
    id INT,
    name TEXT,
    brand TEXT,
    price NUMERIC,
    rating NUMERIC,
    headline TEXT,
    rank REAL
) AS $$
DECLARE
    query tsquery := websearch_to_tsquery('english', search_query);
    order_clause TEXT;
BEGIN
    -- 动态排序
    order_clause := CASE sort_by
        WHEN 'price_asc' THEN 'p.price ASC'
        WHEN 'price_desc' THEN 'p.price DESC'
        WHEN 'rating' THEN 'p.rating DESC, p.review_count DESC'
        ELSE 'rank DESC'
    END;

    RETURN QUERY EXECUTE format('
        SELECT
            p.id,
            p.name,
            p.brand,
            p.price,
            p.rating,
            ts_headline(''english'', p.description, $1,
                ''MaxWords=50, MinWords=20, StartSel=<mark>, StopSel=</mark>''
            ) AS headline,
            ts_rank_cd(p.search_vector, $1, 32) AS rank
        FROM products p
        WHERE p.search_vector @@ $1
          AND p.stock_count > 0
          AND ($2::TEXT IS NULL OR p.category = $2)
          AND ($3::TEXT IS NULL OR p.brand = $3)
          AND ($4::NUMERIC IS NULL OR p.price >= $4)
          AND ($5::NUMERIC IS NULL OR p.price <= $5)
        ORDER BY %s
        LIMIT $6 OFFSET $7
    ', order_clause)
    USING query, category_filter, brand_filter, min_price, max_price, page_size, page_offset;
END;
$$ LANGUAGE plpgsql STABLE;

-- 使用
SELECT * FROM search_products(
    'laptop gaming',
    category_filter => 'Electronics',
    min_price => 500,
    max_price => 2000,
    sort_by => 'rating'
);
```

### 10.3 案例3：多租户文档搜索

```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    file_type TEXT,
    created_by INT REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'D')
    ) STORED
);

-- 租户隔离索引
CREATE INDEX documents_tenant_search_idx
ON documents USING GIN(tenant_id, search_vector);

-- 启用RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY documents_tenant_isolation ON documents
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id')::INT);

-- 搜索（自动应用RLS）
SET app.current_tenant_id = 123;

SELECT id, title, ts_rank(search_vector, query) AS rank
FROM documents, to_tsquery('english', 'contract') query
WHERE search_vector @@ query
ORDER BY rank DESC;
-- 只返回tenant_id=123的结果
```

---

## 11. 与ElasticSearch对比

### 11.1 功能对比

| 特性 | PostgreSQL FTS | ElasticSearch |
|------|----------------|---------------|
| **全文搜索** | ✅ 优秀 | ✅ 优秀 |
| **性能（<100GB）** | ✅ 优秀 | ✅ 优秀 |
| **性能（>100GB）** | ⚠️ 一般 | ✅ 优秀 |
| **实时性** | ✅ 即时 | ⚠️ 近实时（1秒延迟） |
| **ACID事务** | ✅ 完整 | ❌ 无 |
| **运维复杂度** | ✅ 低（单服务） | ⚠️ 高（独立集群） |
| **分布式** | ⚠️ 需自建 | ✅ 原生 |
| **分析功能** | ⚠️ 基础 | ✅ 强大 |
| **多语言** | ⚠️ 需扩展 | ✅ 内置 |
| **学习曲线** | ✅ 低（SQL） | ⚠️ 中等 |

### 11.2 选择建议

```text
选择PostgreSQL FTS，如果：
✅ 数据量 < 100GB
✅ 已使用PostgreSQL
✅ 需要事务一致性
✅ 简化架构（减少服务数量）
✅ 实时更新要求高

选择ElasticSearch，如果：
✅ 数据量 > 100GB
✅ 需要分布式搜索
✅ 需要高级分析（聚合、地理位置）
✅ 多数据源整合
✅ 已有成熟的ES团队
```

---

## 12. 最佳实践

### 12.1 设计原则

```sql
-- ✅ 1. 使用生成列存储tsvector
CREATE TABLE documents (
    content TEXT,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', content)
    ) STORED
);

-- ✅ 2. 为不同字段设置权重
search_vector GENERATED ALWAYS AS (
    setweight(to_tsvector('english', title), 'A') ||
    setweight(to_tsvector('english', subtitle), 'B') ||
    setweight(to_tsvector('english', content), 'D')
) STORED

-- ✅ 3. 创建GIN索引
CREATE INDEX documents_search_idx ON documents USING GIN(search_vector);

-- ✅ 4. 使用部分索引过滤无效数据
CREATE INDEX documents_search_idx ON documents USING GIN(search_vector)
WHERE published = TRUE AND deleted_at IS NULL;

-- ✅ 5. 定期维护
VACUUM ANALYZE documents;
REINDEX INDEX CONCURRENTLY documents_search_idx;
```

### 12.2 查询优化Checklist

- [ ] 使用预计算的tsvector列（而非动态计算）
- [ ] 创建GIN索引
- [ ] 使用websearch_to_tsquery简化查询
- [ ] 限制结果数量（LIMIT）
- [ ] 使用部分索引过滤
- [ ] 考虑分区大表
- [ ] 监控查询性能（pg_stat_statements）

### 12.3 安全注意事项

```sql
-- ⚠️ 防止SQL注入
-- ❌ 危险：直接拼接用户输入
query := to_tsquery('english', user_input);

-- ✅ 安全：使用plainto_tsquery或websearch_to_tsquery
query := plainto_tsquery('english', user_input);
-- 或
query := websearch_to_tsquery('english', user_input);

-- ⚠️ 限制查询复杂度
-- 防止恶意复杂查询消耗资源
SET statement_timeout = '5s';
```

---

## 📚 延伸阅读

### 官方资源

- [PostgreSQL Full Text Search Documentation](https://www.postgresql.org/docs/current/textsearch.html)
- [pg_trgm Extension](https://www.postgresql.org/docs/current/pgtrgm.html)
- [zhparser中文分词](https://github.com/amutu/zhparser)

### 推荐工具

- **pgAdmin**: 可视化管理
- **pg_search (Ruby)**: Rails全文搜索Gem
- **Django-PostgreSQL-FTS**: Django全文搜索

---

## ✅ 学习检查清单

- [ ] 理解tsvector和tsquery基础
- [ ] 掌握全文搜索查询语法
- [ ] 能够创建和优化FTS索引
- [ ] 理解排名和相关性算法
- [ ] 能够实现高亮显示
- [ ] 掌握多语言搜索配置
- [ ] 能够进行性能优化
- [ ] 理解与ElasticSearch的对比

---

## 💡 下一步学习

1. **进阶主题**:
   - 自定义词典和同义词
   - 机器学习相关性优化
   - 分布式全文搜索

2. **相关课程**:
   - [JSON/JSONB高级查询](./【深入】JSON-JSONB高级查询指南.md)
   - [PostgreSQL性能调优](../11-性能调优/)

---

**文档维护**: 本文档持续更新以反映PostgreSQL FTS最新特性。
**反馈**: 如发现错误或有改进建议，请提交issue。

**版本历史**:

- v1.0 (2025-01): 初始版本，覆盖PostgreSQL 12+全文搜索核心特性
