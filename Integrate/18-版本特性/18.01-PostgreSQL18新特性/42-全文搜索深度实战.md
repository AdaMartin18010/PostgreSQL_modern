---

> **📋 文档来源**: `docs\01-PostgreSQL18\42-全文搜索深度实战.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL 18 全文搜索深度实战

PostgreSQL内置强大的全文搜索功能，无需Elasticsearch即可实现高性能搜索。

---

## 📋 目录

- [PostgreSQL 18 全文搜索深度实战](#postgresql-18-全文搜索深度实战)
  - [📋 目录](#-目录)
  - [全文搜索基础](#全文搜索基础)
    - [tsvector与tsquery](#tsvector与tsquery)
    - [基础搜索](#基础搜索)
  - [高级搜索技巧](#高级搜索技巧)
    - [1. 预计算tsvector（推荐）](#1-预计算tsvector推荐)
    - [2. 自动更新tsvector](#2-自动更新tsvector)
    - [3. 加权搜索](#3-加权搜索)
    - [4. 相关性排序](#4-相关性排序)
    - [5. 查询语法](#5-查询语法)
    - [6. 高亮显示](#6-高亮显示)
  - [性能优化](#性能优化)
    - [1. GIN vs GiST索引](#1-gin-vs-gist索引)
    - [2. GIN索引优化](#2-gin索引优化)
    - [3. 分区表优化](#3-分区表优化)
    - [4. 查询优化](#4-查询优化)
  - [多语言支持](#多语言支持)
    - [中文全文搜索](#中文全文搜索)
      - [1. 安装zhparser](#1-安装zhparser)
      - [2. 配置中文分词](#2-配置中文分词)
      - [3. 中文搜索示例](#3-中文搜索示例)
    - [多语言混合](#多语言混合)
  - [实战案例](#实战案例)
    - [案例1: 博客搜索系统](#案例1-博客搜索系统)
    - [案例2: 电商产品搜索](#案例2-电商产品搜索)
    - [案例3: 文档管理系统](#案例3-文档管理系统)
  - [监控与统计](#监控与统计)
    - [索引使用情况](#索引使用情况)
    - [搜索性能分析](#搜索性能分析)
  - [最佳实践](#最佳实践)
    - [✅ 推荐](#-推荐)
    - [❌ 避免](#-避免)
  - [总结](#总结)

---

## 全文搜索基础

### tsvector与tsquery

```sql
-- 性能测试：tsvector: 文档向量（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- 结果: 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '生成tsvector失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：tsquery: 查询表达式（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT to_tsquery('english', 'quick & fox');
-- 结果: 'quick' & 'fox'
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '生成tsquery失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：匹配（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT to_tsvector('english', 'The quick brown fox') @@
       to_tsquery('english', 'quick & fox');
-- 结果: true
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '全文搜索匹配失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 基础搜索

```sql
-- 性能测试：创建文章表（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS articles (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表articles已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：简单搜索（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM articles
WHERE to_tsvector('english', title || ' ' || content) @@
      to_tsquery('english', 'postgresql & performance');
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表articles不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '全文搜索失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 高级搜索技巧

### 1. 预计算tsvector（推荐）

```sql
-- 性能测试：添加tsvector列（带错误处理）
BEGIN;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS tsv tsvector;
COMMIT;
EXCEPTION
    WHEN duplicate_column THEN
        RAISE NOTICE '列tsv已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '添加tsvector列失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：生成tsvector（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
UPDATE articles SET tsv =
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
WHERE tsv IS NULL;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '生成tsvector失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：创建GIN索引（带错误处理）
BEGIN;
CREATE INDEX IF NOT EXISTS idx_articles_tsv ON articles USING GIN(tsv);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '索引idx_articles_tsv已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建GIN索引失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查询（快速）（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM articles
WHERE tsv @@ to_tsquery('english', 'postgresql & performance');
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '全文搜索查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 2. 自动更新tsvector

```sql
-- 触发器函数
CREATE OR REPLACE FUNCTION articles_tsv_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tsv := to_tsvector('english',
        coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER articles_tsv_update
BEFORE INSERT OR UPDATE ON articles
FOR EACH ROW
EXECUTE FUNCTION articles_tsv_trigger();

-- 现在插入自动生成tsvector
INSERT INTO articles (title, content) VALUES
    ('PostgreSQL Performance', 'Tips for optimizing queries...');
```

### 3. 加权搜索

```sql
-- 不同字段不同权重
UPDATE articles SET tsv =
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(content, '')), 'B');

-- 查询时考虑权重
SELECT
    id,
    title,
    ts_rank(tsv, query) AS rank
FROM articles, to_tsquery('english', 'postgresql') query
WHERE tsv @@ query
ORDER BY rank DESC;
```

### 4. 相关性排序

```sql
-- ts_rank: 基础排序
SELECT
    title,
    ts_rank(tsv, query) AS rank
FROM articles, to_tsquery('english', 'postgresql & performance') query
WHERE tsv @@ query
ORDER BY rank DESC;

-- ts_rank_cd: 考虑位置的排序
SELECT
    title,
    ts_rank_cd(tsv, query) AS rank
FROM articles, to_tsquery('english', 'postgresql & performance') query
WHERE tsv @@ query
ORDER BY rank DESC;

-- 自定义权重
SELECT
    title,
    ts_rank('{0.1, 0.2, 0.4, 1.0}', tsv, query) AS rank
FROM articles, to_tsquery('english', 'postgresql') query
WHERE tsv @@ query
ORDER BY rank DESC;
```

### 5. 查询语法

```sql
-- AND查询
to_tsquery('postgresql & performance')

-- OR查询
to_tsquery('postgresql | mysql')

-- NOT查询
to_tsquery('postgresql & !mysql')

-- 短语查询
to_tsquery('postgresql <-> performance')  -- 相邻
to_tsquery('postgresql <2> performance')  -- 距离<=2

-- 组合查询
to_tsquery('(postgresql | mysql) & performance & !slow')
```

### 6. 高亮显示

```sql
-- 高亮匹配词
SELECT
    title,
    ts_headline('english', content, query, 'MaxWords=50, MinWords=20') AS snippet
FROM articles, to_tsquery('english', 'postgresql') query
WHERE tsv @@ query;

-- 自定义高亮标签
SELECT
    ts_headline('english', content, query,
        'StartSel=<mark>, StopSel=</mark>'
    ) AS snippet
FROM articles, to_tsquery('english', 'postgresql') query
WHERE tsv @@ query;
```

---

## 性能优化

### 1. GIN vs GiST索引

```sql
-- GIN索引（推荐）：更快查询，较慢更新
CREATE INDEX idx_articles_gin ON articles USING GIN(tsv);

-- GiST索引：较快更新，较慢查询
CREATE INDEX idx_articles_gist ON articles USING GIST(tsv);

-- 性能对比
EXPLAIN ANALYZE
SELECT * FROM articles WHERE tsv @@ to_tsquery('postgresql');
```

### 2. GIN索引优化

```sql
-- 调整GIN参数（PostgreSQL 18）
CREATE INDEX idx_articles_gin ON articles
USING GIN(tsv) WITH (fastupdate = on, gin_pending_list_limit = 4096);

-- fastupdate: 批量更新pending list
-- gin_pending_list_limit: pending list大小
```

### 3. 分区表优化

```sql
-- 按时间分区
CREATE TABLE articles_2024_01 PARTITION OF articles
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE articles_2024_02 PARTITION OF articles
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 每个分区创建索引
CREATE INDEX idx_articles_2024_01_tsv ON articles_2024_01 USING GIN(tsv);
CREATE INDEX idx_articles_2024_02_tsv ON articles_2024_02 USING GIN(tsv);
```

### 4. 查询优化

```sql
-- 使用LIMIT
SELECT * FROM articles
WHERE tsv @@ to_tsquery('postgresql')
ORDER BY ts_rank(tsv, to_tsquery('postgresql')) DESC
LIMIT 20;

-- 使用CTE预过滤
WITH matched AS (
    SELECT id, title, tsv
    FROM articles
    WHERE tsv @@ to_tsquery('postgresql')
    LIMIT 100
)
SELECT
    id,
    title,
    ts_rank(tsv, query) AS rank
FROM matched, to_tsquery('postgresql') query
ORDER BY rank DESC
LIMIT 20;
```

---

## 多语言支持

### 中文全文搜索

#### 1. 安装zhparser

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-18-zhparser

# 编译安装
git clone https://github.com/amutu/zhparser.git
cd zhparser
make && sudo make install
```

#### 2. 配置中文分词

```sql
-- 创建扩展
CREATE EXTENSION zhparser;

-- 创建中文文本搜索配置
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);

-- 添加token映射
ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR
    n,v,a,i,e,l WITH simple;

-- 测试
SELECT to_tsvector('chinese', '我爱PostgreSQL数据库');
-- 结果: 'postgresql':2 'love':1 'database':3
```

#### 3. 中文搜索示例

```sql
-- 创建带中文的文章表
CREATE TABLE cn_articles (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tsv tsvector
);

-- 触发器（中文）
CREATE OR REPLACE FUNCTION cn_articles_tsv_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tsv := to_tsvector('chinese',
        coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cn_articles_tsv_update
BEFORE INSERT OR UPDATE ON cn_articles
FOR EACH ROW
EXECUTE FUNCTION cn_articles_tsv_trigger();

-- 索引
CREATE INDEX idx_cn_articles_tsv ON cn_articles USING GIN(tsv);

-- 插入数据
INSERT INTO cn_articles (title, content) VALUES
    ('PostgreSQL性能优化', 'PostgreSQL是一个功能强大的开源数据库...'),
    ('数据库索引原理', '索引可以显著提升查询性能...');

-- 搜索
SELECT title, ts_rank(tsv, query) AS rank
FROM cn_articles, to_tsquery('chinese', 'PostgreSQL & 性能') query
WHERE tsv @@ query
ORDER BY rank DESC;
```

### 多语言混合

```sql
-- 检测语言并使用相应配置
CREATE OR REPLACE FUNCTION detect_language(text TEXT)
RETURNS regconfig AS $$
BEGIN
    -- 简单检测：是否包含中文
    IF text ~ '[\u4e00-\u9fa5]' THEN
        RETURN 'chinese'::regconfig;
    ELSE
        RETURN 'english'::regconfig;
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 使用
SELECT to_tsvector(detect_language(content), content)
FROM articles;
```

---

## 实战案例

### 案例1: 博客搜索系统

```sql
-- 完整的博客搜索表
CREATE TABLE blog_posts (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    category VARCHAR(50),
    tags TEXT[],
    published_at TIMESTAMPTZ,
    tsv tsvector,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 综合tsvector（标题权重A，内容B，标签C）
CREATE OR REPLACE FUNCTION blog_posts_tsv_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tsv :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.content, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(array_to_string(NEW.tags, ' '), '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER blog_posts_tsv_update
BEFORE INSERT OR UPDATE ON blog_posts
FOR EACH ROW
EXECUTE FUNCTION blog_posts_tsv_trigger();

CREATE INDEX idx_blog_posts_tsv ON blog_posts USING GIN(tsv);

-- 高级搜索查询
CREATE OR REPLACE FUNCTION search_blog_posts(
    search_query TEXT,
    category_filter VARCHAR DEFAULT NULL,
    author_filter BIGINT DEFAULT NULL,
    limit_count INT DEFAULT 20
)
RETURNS TABLE(
    id BIGINT,
    title TEXT,
    snippet TEXT,
    rank REAL,
    published_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        bp.id,
        bp.title,
        ts_headline('english', bp.content, query,
            'MaxWords=50, MinWords=20'
        ) AS snippet,
        ts_rank('{0.1, 0.2, 0.4, 1.0}', bp.tsv, query) AS rank,
        bp.published_at
    FROM blog_posts bp, to_tsquery('english', search_query) query
    WHERE bp.tsv @@ query
      AND (category_filter IS NULL OR bp.category = category_filter)
      AND (author_filter IS NULL OR bp.author_id = author_filter)
    ORDER BY rank DESC, published_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- 使用
SELECT * FROM search_blog_posts('postgresql & performance', 'Technology', NULL, 10);
```

### 案例2: 电商产品搜索

```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    brand VARCHAR(100),
    category VARCHAR(100),
    price NUMERIC(10, 2),
    stock INT,
    tsv tsvector
);

-- 产品搜索（支持价格范围）
CREATE OR REPLACE FUNCTION search_products(
    search_query TEXT,
    min_price NUMERIC DEFAULT NULL,
    max_price NUMERIC DEFAULT NULL,
    category_filter VARCHAR DEFAULT NULL
)
RETURNS TABLE(
    id BIGINT,
    name TEXT,
    brand VARCHAR,
    price NUMERIC,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.name,
        p.brand,
        p.price,
        ts_rank(p.tsv, query) AS rank
    FROM products p, to_tsquery('english', search_query) query
    WHERE p.tsv @@ query
      AND p.stock > 0
      AND (min_price IS NULL OR p.price >= min_price)
      AND (max_price IS NULL OR p.price <= max_price)
      AND (category_filter IS NULL OR p.category = category_filter)
    ORDER BY rank DESC, p.price ASC;
END;
$$ LANGUAGE plpgsql;
```

### 案例3: 文档管理系统

```sql
-- 文档表（支持多种格式）
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type VARCHAR(20),
    content TEXT,  -- 提取的文本内容
    metadata JSONB,
    uploaded_by BIGINT,
    uploaded_at TIMESTAMPTZ DEFAULT now(),
    tsv tsvector
);

-- 索引
CREATE INDEX idx_documents_tsv ON documents USING GIN(tsv);
CREATE INDEX idx_documents_metadata ON documents USING GIN(metadata);

-- 搜索函数（支持元数据过滤）
CREATE OR REPLACE FUNCTION search_documents(
    search_query TEXT,
    file_type_filter VARCHAR DEFAULT NULL,
    metadata_filter JSONB DEFAULT NULL
)
RETURNS TABLE(
    id BIGINT,
    filename TEXT,
    snippet TEXT,
    rank REAL,
    uploaded_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.filename,
        ts_headline('english', d.content, query, 'MaxWords=30') AS snippet,
        ts_rank(d.tsv, query) AS rank,
        d.uploaded_at
    FROM documents d, to_tsquery('english', search_query) query
    WHERE d.tsv @@ query
      AND (file_type_filter IS NULL OR d.file_type = file_type_filter)
      AND (metadata_filter IS NULL OR d.metadata @> metadata_filter)
    ORDER BY rank DESC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql;

-- 使用
SELECT * FROM search_documents(
    'contract & agreement',
    'pdf',
    '{"department": "legal"}'::jsonb
);
```

---

## 监控与统计

### 索引使用情况

```sql
-- 查看索引大小
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE indexname LIKE '%tsv%';

-- 查看索引扫描次数
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexname LIKE '%tsv%';
```

### 搜索性能分析

```sql
-- 记录搜索日志
CREATE TABLE search_logs (
    id BIGSERIAL PRIMARY KEY,
    query TEXT,
    results_count INT,
    execution_time_ms REAL,
    searched_at TIMESTAMPTZ DEFAULT now()
);

-- 在搜索函数中记录
CREATE OR REPLACE FUNCTION search_with_logging(search_query TEXT)
RETURNS TABLE(...) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    results_count INT;
BEGIN
    start_time := clock_timestamp();

    -- 执行搜索
    RETURN QUERY ...;

    GET DIAGNOSTICS results_count = ROW_COUNT;
    end_time := clock_timestamp();

    -- 记录日志
    INSERT INTO search_logs (query, results_count, execution_time_ms)
    VALUES (
        search_query,
        results_count,
        EXTRACT(MILLISECONDS FROM (end_time - start_time))
    );
END;
$$ LANGUAGE plpgsql;
```

---

## 最佳实践

### ✅ 推荐

1. **始终使用GIN索引**

   ```sql
   CREATE INDEX idx_tsv ON table_name USING GIN(tsv);
   ```

2. **预计算tsvector**

   ```sql
   ALTER TABLE table_name ADD COLUMN tsv tsvector;
   -- 使用触发器自动更新
   ```

3. **合理设置权重**

   ```sql
   setweight(to_tsvector('english', title), 'A') ||  -- 标题最重要
   setweight(to_tsvector('english', content), 'B')   -- 内容次之
   ```

4. **使用ts_rank排序**

   ```sql
   ORDER BY ts_rank(tsv, query) DESC
   ```

### ❌ 避免

1. ❌ 每次查询都生成tsvector
2. ❌ 不使用索引
3. ❌ 不限制结果数量
4. ❌ 忽略语言配置

---

## 总结

PostgreSQL全文搜索:

- ✅ 内置支持，无需额外组件
- ✅ 高性能GIN索引
- ✅ 灵活的查询语法
- ✅ 多语言支持
- ✅ 与SQL完美集成

**适用场景**: 博客搜索、产品搜索、文档管理、内容管理系统

---

**PostgreSQL全文搜索 - 简单而强大！**
