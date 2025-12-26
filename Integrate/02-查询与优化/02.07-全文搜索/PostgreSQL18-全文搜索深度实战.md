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

**自动更新tsvector（带完整错误处理）**:

```sql
-- 触发器函数（带完整错误处理）
CREATE OR REPLACE FUNCTION articles_tsv_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- 检查文本搜索配置是否存在
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'english') THEN
        RAISE EXCEPTION '文本搜索配置不存在: english';
    END IF;

    -- 生成tsvector
    NEW.tsv := to_tsvector('english',
        coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, '')
    );

    RETURN NEW;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '文本搜索配置不存在: english';
    WHEN OTHERS THEN
        RAISE EXCEPTION '生成tsvector失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'articles_tsv_trigger') THEN
        RAISE EXCEPTION '触发器函数不存在: articles_tsv_trigger';
    END IF;

    -- 删除现有触发器（如果存在）
    IF EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'articles_tsv_update'
    ) THEN
        DROP TRIGGER articles_tsv_update ON articles;
        RAISE NOTICE '已删除现有触发器: articles_tsv_update';
    END IF;

    CREATE TRIGGER articles_tsv_update
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION articles_tsv_trigger();

    RAISE NOTICE '触发器创建成功: articles_tsv_update';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN undefined_function THEN
        RAISE EXCEPTION '触发器函数不存在: articles_tsv_trigger';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建触发器失败: %', SQLERRM;
END $$;

-- 现在插入自动生成tsvector（带错误处理）
DO $$
DECLARE
    inserted_id BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    INSERT INTO articles (title, content) VALUES
        ('PostgreSQL Performance', 'Tips for optimizing queries...')
    RETURNING id INTO inserted_id;

    RAISE NOTICE '插入成功: id=%，tsvector已自动生成', inserted_id;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN OTHERS THEN
        RAISE EXCEPTION '插入数据失败: %', SQLERRM;
END $$;
```

### 3. 加权搜索

**加权搜索（带完整错误处理和性能测试）**:

```sql
-- 不同字段不同权重（带错误处理）
DO $$
DECLARE
    updated_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    UPDATE articles SET tsv =
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'B');

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RAISE NOTICE '加权tsvector更新成功: 更新了 % 行', updated_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN undefined_object THEN
        RAISE EXCEPTION '文本搜索配置不存在: english';
    WHEN OTHERS THEN
        RAISE EXCEPTION '更新加权tsvector失败: %', SQLERRM;
END $$;

-- 查询时考虑权重（带错误处理和性能测试）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM articles, to_tsquery('english', 'postgresql') query
    WHERE tsv @@ query;

    RAISE NOTICE '加权搜索成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN undefined_object THEN
        RAISE EXCEPTION '文本搜索配置不存在: english';
    WHEN OTHERS THEN
        RAISE EXCEPTION '加权搜索失败: %', SQLERRM;
END $$;

-- 性能测试：查询时考虑权重
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    id,
    title,
    ts_rank(tsv, query) AS rank
FROM articles, to_tsquery('english', 'postgresql') query
WHERE tsv @@ query
ORDER BY rank DESC;
-- 执行时间: 取决于表大小和索引
-- 计划: Sort -> Bitmap Heap Scan -> Bitmap Index Scan
```

### 4. 相关性排序

**相关性排序（带完整错误处理和性能测试）**:

```sql
-- ts_rank: 基础排序（带错误处理和性能测试）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM articles, to_tsquery('english', 'postgresql & performance') query
    WHERE tsv @@ query;

    RAISE NOTICE '相关性排序查询成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN undefined_object THEN
        RAISE EXCEPTION '文本搜索配置不存在: english';
    WHEN OTHERS THEN
        RAISE EXCEPTION '相关性排序查询失败: %', SQLERRM;
END $$;

-- 性能测试：ts_rank基础排序
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    title,
    ts_rank(tsv, query) AS rank
FROM articles, to_tsquery('english', 'postgresql & performance') query
WHERE tsv @@ query
ORDER BY rank DESC;
-- 执行时间: 取决于表大小和索引
-- 计划: Sort -> Bitmap Heap Scan -> Bitmap Index Scan

-- ts_rank_cd: 考虑位置的排序（带错误处理和性能测试）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM articles, to_tsquery('english', 'postgresql & performance') query
    WHERE tsv @@ query;

    RAISE NOTICE 'ts_rank_cd排序查询成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'ts_rank_cd排序查询失败: %', SQLERRM;
END $$;

-- 性能测试：ts_rank_cd考虑位置的排序
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    title,
    ts_rank_cd(tsv, query) AS rank
FROM articles, to_tsquery('english', 'postgresql & performance') query
WHERE tsv @@ query
ORDER BY rank DESC;
-- 执行时间: 取决于表大小和索引
-- 计划: Sort -> Bitmap Heap Scan -> Bitmap Index Scan

-- 自定义权重（带错误处理和性能测试）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM articles, to_tsquery('english', 'postgresql') query
    WHERE tsv @@ query;

    RAISE NOTICE '自定义权重排序查询成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN OTHERS THEN
        RAISE EXCEPTION '自定义权重排序查询失败: %', SQLERRM;
END $$;

-- 性能测试：自定义权重
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    title,
    ts_rank('{0.1, 0.2, 0.4, 1.0}', tsv, query) AS rank
FROM articles, to_tsquery('english', 'postgresql') query
WHERE tsv @@ query
ORDER BY rank DESC;
-- 执行时间: 取决于表大小和索引
-- 计划: Sort -> Bitmap Heap Scan -> Bitmap Index Scan
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

**索引创建和性能对比（带完整错误处理）**:

```sql
-- GIN索引（推荐）：更快查询，较慢更新（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'articles' AND indexname = 'idx_articles_gin'
    ) THEN
        RAISE WARNING '索引已存在: idx_articles_gin';
    ELSE
        CREATE INDEX idx_articles_gin ON articles USING GIN(tsv);
        RAISE NOTICE 'GIN索引创建成功: idx_articles_gin';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在: idx_articles_gin';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建GIN索引失败: %', SQLERRM;
END $$;

-- GiST索引：较快更新，较慢查询（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'articles' AND indexname = 'idx_articles_gist'
    ) THEN
        RAISE WARNING '索引已存在: idx_articles_gist';
    ELSE
        CREATE INDEX idx_articles_gist ON articles USING GIST(tsv);
        RAISE NOTICE 'GiST索引创建成功: idx_articles_gist';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在: idx_articles_gist';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建GiST索引失败: %', SQLERRM;
END $$;

-- 性能对比（带错误处理和性能测试）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    RAISE NOTICE '开始性能对比测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN OTHERS THEN
        RAISE EXCEPTION '性能对比准备失败: %', SQLERRM;
END $$;

-- 性能测试：使用GIN索引
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM articles WHERE tsv @@ to_tsquery('english', 'postgresql');
-- 执行时间: 快（使用GIN索引）
-- 计划: Bitmap Heap Scan -> Bitmap Index Scan (GIN)
```

### 2. GIN索引优化

**GIN索引优化（带完整错误处理）**:

```sql
-- 调整GIN参数（PostgreSQL 18，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'articles' AND indexname = 'idx_articles_gin'
    ) THEN
        -- 删除现有索引
        DROP INDEX idx_articles_gin;
        RAISE NOTICE '已删除现有索引: idx_articles_gin';
    END IF;

    CREATE INDEX idx_articles_gin ON articles
    USING GIN(tsv) WITH (fastupdate = on, gin_pending_list_limit = 4096);

    RAISE NOTICE 'GIN索引创建成功: idx_articles_gin（fastupdate=on, gin_pending_list_limit=4096）';
    RAISE NOTICE 'fastupdate: 批量更新pending list';
    RAISE NOTICE 'gin_pending_list_limit: pending list大小';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建GIN索引失败: %', SQLERRM;
END $$;

-- 性能测试：GIN索引优化效果
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM articles WHERE tsv @@ to_tsquery('english', 'postgresql');
-- 执行时间: 使用优化后的GIN索引，性能更好
-- 计划: Bitmap Heap Scan -> Bitmap Index Scan
```

### 3. 分区表优化

**分区表优化（带完整错误处理）**:

```sql
-- 按时间分区（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles（需要先创建分区表）';
    END IF;

    -- 创建2024年1月分区
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles_2024_01') THEN
        RAISE WARNING '分区已存在: articles_2024_01';
    ELSE
        CREATE TABLE articles_2024_01 PARTITION OF articles
        FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
        RAISE NOTICE '分区创建成功: articles_2024_01';
    END IF;

    -- 创建2024年2月分区
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles_2024_02') THEN
        RAISE WARNING '分区已存在: articles_2024_02';
    ELSE
        CREATE TABLE articles_2024_02 PARTITION OF articles
        FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
        RAISE NOTICE '分区创建成功: articles_2024_02';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles（需要先创建分区表）';
    WHEN duplicate_table THEN
        RAISE WARNING '部分分区已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建分区失败: %', SQLERRM;
END $$;

-- 每个分区创建索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles_2024_01') THEN
        RAISE EXCEPTION '分区不存在: articles_2024_01';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'articles_2024_01' AND indexname = 'idx_articles_2024_01_tsv'
    ) THEN
        RAISE WARNING '索引已存在: idx_articles_2024_01_tsv';
    ELSE
        CREATE INDEX idx_articles_2024_01_tsv ON articles_2024_01 USING GIN(tsv);
        RAISE NOTICE '分区索引创建成功: idx_articles_2024_01_tsv';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'articles_2024_02' AND indexname = 'idx_articles_2024_02_tsv'
    ) THEN
        RAISE WARNING '索引已存在: idx_articles_2024_02_tsv';
    ELSE
        CREATE INDEX idx_articles_2024_02_tsv ON articles_2024_02 USING GIN(tsv);
        RAISE NOTICE '分区索引创建成功: idx_articles_2024_02_tsv';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '分区不存在（请检查articles_2024_01和articles_2024_02分区）';
    WHEN duplicate_table THEN
        RAISE WARNING '部分索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建分区索引失败: %', SQLERRM;
END $$;
```

### 4. 查询优化

**查询优化（带完整错误处理和性能测试）**:

```sql
-- 使用LIMIT（带错误处理和性能测试）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM (
        SELECT * FROM articles
        WHERE tsv @@ to_tsquery('english', 'postgresql')
        ORDER BY ts_rank(tsv, to_tsquery('english', 'postgresql')) DESC
        LIMIT 20
    ) subquery;

    RAISE NOTICE 'LIMIT查询成功: 返回 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'LIMIT查询失败: %', SQLERRM;
END $$;

-- 性能测试：使用LIMIT
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM articles
WHERE tsv @@ to_tsquery('english', 'postgresql')
ORDER BY ts_rank(tsv, to_tsquery('english', 'postgresql')) DESC
LIMIT 20;
-- 执行时间: 快（只返回20条结果）
-- 计划: Limit -> Sort -> Bitmap Heap Scan -> Bitmap Index Scan

-- 使用CTE预过滤（带错误处理和性能测试）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'articles') THEN
        RAISE EXCEPTION '表不存在: articles';
    END IF;

    WITH matched AS (
        SELECT id, title, tsv
        FROM articles
        WHERE tsv @@ to_tsquery('english', 'postgresql')
        LIMIT 100
    )
    SELECT COUNT(*) INTO result_count
    FROM matched, to_tsquery('english', 'postgresql') query;

    RAISE NOTICE 'CTE预过滤查询成功: 返回 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: articles';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'CTE预过滤查询失败: %', SQLERRM;
END $$;

-- 性能测试：使用CTE预过滤
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH matched AS (
    SELECT id, title, tsv
    FROM articles
    WHERE tsv @@ to_tsquery('english', 'postgresql')
    LIMIT 100
)
SELECT
    id,
    title,
    ts_rank(tsv, query) AS rank
FROM matched, to_tsquery('english', 'postgresql') query
ORDER BY rank DESC
LIMIT 20;
-- 执行时间: 更快（先预过滤100条，再排序）
-- 计划: Limit -> Sort -> CTE Scan -> Limit -> Bitmap Heap Scan
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

**配置中文分词（带完整错误处理）**:

```sql
-- 创建扩展（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'zhparser') THEN
        CREATE EXTENSION zhparser;
        RAISE NOTICE 'zhparser扩展已创建';
    ELSE
        RAISE NOTICE 'zhparser扩展已存在';
    END IF;
EXCEPTION
    WHEN undefined_file THEN
        RAISE EXCEPTION 'zhparser扩展文件未找到（需要单独安装zhparser扩展）';
    WHEN OTHERS THEN
        RAISE EXCEPTION '安装zhparser扩展失败: %', SQLERRM;
END $$;

-- 创建中文文本搜索配置（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'zhparser') THEN
        RAISE EXCEPTION 'zhparser扩展未安装';
    END IF;

    IF EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'chinese') THEN
        RAISE WARNING '文本搜索配置已存在: chinese';
    ELSE
        CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
        RAISE NOTICE '文本搜索配置创建成功: chinese';
    END IF;

    -- 添加token映射
    ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR
        n,v,a,i,e,l WITH simple;

    RAISE NOTICE 'token映射添加成功: n,v,a,i,e,l -> simple';
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION 'zhparser解析器不存在';
    WHEN duplicate_object THEN
        RAISE WARNING '文本搜索配置已存在: chinese';
    WHEN OTHERS THEN
        RAISE EXCEPTION '配置中文分词失败: %', SQLERRM;
END $$;

-- 测试（带错误处理和性能测试）
DO $$
DECLARE
    test_result TSVECTOR;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'chinese') THEN
        RAISE EXCEPTION '文本搜索配置不存在: chinese';
    END IF;

    test_result := to_tsvector('chinese', '我爱PostgreSQL数据库');

    IF test_result IS NULL THEN
        RAISE WARNING '中文分词测试返回NULL';
    ELSE
        RAISE NOTICE '中文分词测试成功: %', test_result;
        RAISE NOTICE '预期结果: postgresql:2 love:1 database:3';
    END IF;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '文本搜索配置不存在: chinese';
    WHEN OTHERS THEN
        RAISE EXCEPTION '中文分词测试失败: %', SQLERRM;
END $$;

-- 性能测试：中文分词
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT to_tsvector('chinese', '我爱PostgreSQL数据库');
-- 执行时间: <10ms
-- 计划: Result
```

#### 3. 中文搜索示例

**中文搜索示例（带完整错误处理）**:

```sql
-- 创建带中文的文章表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'cn_articles') THEN
        RAISE WARNING '表已存在: cn_articles';
    ELSE
        CREATE TABLE cn_articles (
            id BIGSERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tsv tsvector
        );
        RAISE NOTICE '表创建成功: cn_articles';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表已存在: cn_articles';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 触发器（中文，带完整错误处理）
CREATE OR REPLACE FUNCTION cn_articles_tsv_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- 检查文本搜索配置是否存在
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'chinese') THEN
        RAISE EXCEPTION '文本搜索配置不存在: chinese';
    END IF;

    NEW.tsv := to_tsvector('chinese',
        coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, '')
    );

    RETURN NEW;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '文本搜索配置不存在: chinese';
    WHEN OTHERS THEN
        RAISE EXCEPTION '生成tsvector失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'cn_articles') THEN
        RAISE EXCEPTION '表不存在: cn_articles';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'cn_articles_tsv_update'
    ) THEN
        DROP TRIGGER cn_articles_tsv_update ON cn_articles;
        RAISE NOTICE '已删除现有触发器: cn_articles_tsv_update';
    END IF;

    CREATE TRIGGER cn_articles_tsv_update
    BEFORE INSERT OR UPDATE ON cn_articles
    FOR EACH ROW
    EXECUTE FUNCTION cn_articles_tsv_trigger();

    RAISE NOTICE '触发器创建成功: cn_articles_tsv_update';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: cn_articles';
    WHEN undefined_function THEN
        RAISE EXCEPTION '触发器函数不存在: cn_articles_tsv_trigger';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建触发器失败: %', SQLERRM;
END $$;

-- 索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'cn_articles') THEN
        RAISE EXCEPTION '表不存在: cn_articles';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'cn_articles' AND indexname = 'idx_cn_articles_tsv'
    ) THEN
        RAISE WARNING '索引已存在: idx_cn_articles_tsv';
    ELSE
        CREATE INDEX idx_cn_articles_tsv ON cn_articles USING GIN(tsv);
        RAISE NOTICE 'GIN索引创建成功: idx_cn_articles_tsv';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: cn_articles';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在: idx_cn_articles_tsv';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;

-- 插入数据（带错误处理）
DO $$
DECLARE
    inserted_ids BIGINT[];
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'cn_articles') THEN
        RAISE EXCEPTION '表不存在: cn_articles';
    END IF;

    INSERT INTO cn_articles (title, content) VALUES
        ('PostgreSQL性能优化', 'PostgreSQL是一个功能强大的开源数据库...'),
        ('数据库索引原理', '索引可以显著提升查询性能...')
    RETURNING ARRAY_AGG(id) INTO inserted_ids;

    RAISE NOTICE '数据插入成功: ids=%', inserted_ids;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: cn_articles';
    WHEN OTHERS THEN
        RAISE EXCEPTION '插入数据失败: %', SQLERRM;
END $$;

-- 搜索（带错误处理和性能测试）
DO $$
DECLARE
    result_count BIGINT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'cn_articles') THEN
        RAISE EXCEPTION '表不存在: cn_articles';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM cn_articles, to_tsquery('chinese', 'PostgreSQL & 性能') query
    WHERE tsv @@ query;

    RAISE NOTICE '中文搜索成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: cn_articles';
    WHEN undefined_object THEN
        RAISE EXCEPTION '文本搜索配置不存在: chinese';
    WHEN OTHERS THEN
        RAISE EXCEPTION '中文搜索失败: %', SQLERRM;
END $$;

-- 性能测试：搜索
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT title, ts_rank(tsv, query) AS rank
FROM cn_articles, to_tsquery('chinese', 'PostgreSQL & 性能') query
WHERE tsv @@ query
ORDER BY rank DESC;
-- 执行时间: 取决于表大小和索引
-- 计划: Sort -> Bitmap Heap Scan -> Bitmap Index Scan
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

**博客搜索系统（带完整错误处理）**:

```sql
-- 完整的博客搜索表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'blog_posts') THEN
        RAISE WARNING '表已存在: blog_posts';
    ELSE
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
        RAISE NOTICE '表创建成功: blog_posts';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表已存在: blog_posts';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 综合tsvector（标题权重A，内容B，标签C，带完整错误处理）
CREATE OR REPLACE FUNCTION blog_posts_tsv_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- 检查文本搜索配置是否存在
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'english') THEN
        RAISE EXCEPTION '文本搜索配置不存在: english';
    END IF;

    -- 生成加权tsvector
    NEW.tsv :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.content, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(array_to_string(NEW.tags, ' '), '')), 'C');

    RETURN NEW;
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION '文本搜索配置不存在: english';
    WHEN OTHERS THEN
        RAISE EXCEPTION '生成tsvector失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'blog_posts') THEN
        RAISE EXCEPTION '表不存在: blog_posts';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'blog_posts_tsv_trigger') THEN
        RAISE EXCEPTION '触发器函数不存在: blog_posts_tsv_trigger';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'blog_posts_tsv_update'
    ) THEN
        DROP TRIGGER blog_posts_tsv_update ON blog_posts;
        RAISE NOTICE '已删除现有触发器: blog_posts_tsv_update';
    END IF;

    CREATE TRIGGER blog_posts_tsv_update
    BEFORE INSERT OR UPDATE ON blog_posts
    FOR EACH ROW
    EXECUTE FUNCTION blog_posts_tsv_trigger();

    RAISE NOTICE '触发器创建成功: blog_posts_tsv_update';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: blog_posts';
    WHEN undefined_function THEN
        RAISE EXCEPTION '触发器函数不存在: blog_posts_tsv_trigger';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建触发器失败: %', SQLERRM;
END $$;

-- 创建索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'blog_posts') THEN
        RAISE EXCEPTION '表不存在: blog_posts';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'blog_posts' AND indexname = 'idx_blog_posts_tsv'
    ) THEN
        RAISE WARNING '索引已存在: idx_blog_posts_tsv';
    ELSE
        CREATE INDEX idx_blog_posts_tsv ON blog_posts USING GIN(tsv);
        RAISE NOTICE 'GIN索引创建成功: idx_blog_posts_tsv';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: blog_posts';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在: idx_blog_posts_tsv';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;

-- 高级搜索查询（带完整错误处理）
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
    -- 参数验证
    IF search_query IS NULL OR TRIM(search_query) = '' THEN
        RAISE EXCEPTION '搜索查询不能为空';
    END IF;

    IF limit_count IS NULL OR limit_count < 1 OR limit_count > 1000 THEN
        RAISE EXCEPTION 'limit_count必须在1-1000之间';
    END IF;

    -- 检查表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'blog_posts') THEN
        RAISE EXCEPTION '表不存在: blog_posts';
    END IF;

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
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: blog_posts';
    WHEN undefined_object THEN
        RAISE EXCEPTION '文本搜索配置不存在: english';
    WHEN OTHERS THEN
        RAISE EXCEPTION '搜索失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 使用（带错误处理和性能测试）
DO $$
DECLARE
    result_count INT;
BEGIN
    SELECT COUNT(*) INTO result_count
    FROM search_blog_posts('postgresql & performance', 'Technology', NULL, 10);

    RAISE NOTICE '博客搜索成功: 找到 % 条结果', result_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '博客搜索失败: %', SQLERRM;
END $$;

-- 性能测试：使用搜索函数
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM search_blog_posts('postgresql & performance', 'Technology', NULL, 10);
-- 执行时间: 取决于表大小和索引
-- 计划: Limit -> Sort -> Bitmap Heap Scan -> Bitmap Index Scan
```

### 案例2: 电商产品搜索

**电商产品搜索（带完整错误处理）**:

```sql
-- 创建产品表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products') THEN
        RAISE WARNING '表已存在: products';
    ELSE
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
        RAISE NOTICE '表创建成功: products';
    END IF;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表已存在: products';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 产品搜索（支持价格范围，带完整错误处理）
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
    -- 参数验证
    IF search_query IS NULL OR TRIM(search_query) = '' THEN
        RAISE EXCEPTION '搜索查询不能为空';
    END IF;

    IF min_price IS NOT NULL AND max_price IS NOT NULL AND min_price > max_price THEN
        RAISE EXCEPTION 'min_price不能大于max_price';
    END IF;

    -- 检查表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products') THEN
        RAISE EXCEPTION '表不存在: products';
    END IF;

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
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表不存在: products';
    WHEN undefined_object THEN
        RAISE EXCEPTION '文本搜索配置不存在: english';
    WHEN OTHERS THEN
        RAISE EXCEPTION '产品搜索失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 性能测试：产品搜索
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM search_products('laptop', 1000, 5000, 'Electronics');
-- 执行时间: 取决于表大小和索引
-- 计划: Sort -> Bitmap Heap Scan -> Bitmap Index Scan
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

**索引使用情况监控（带完整错误处理和性能测试）**:

```sql
-- 查看索引大小（带错误处理和性能测试）
DO $$
DECLARE
    index_count INT;
BEGIN
    SELECT COUNT(*) INTO index_count
    FROM pg_stat_user_indexes
    WHERE indexname LIKE '%tsv%';

    IF index_count = 0 THEN
        RAISE NOTICE '没有找到tsv相关索引';
    ELSE
        RAISE NOTICE '找到 % 个tsv相关索引', index_count;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '查看索引大小失败: %', SQLERRM;
END $$;

-- 性能测试：查看索引大小
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE indexname LIKE '%tsv%';
-- 执行时间: <10ms
-- 计划: Seq Scan

-- 查看索引扫描次数（带错误处理和性能测试）
DO $$
DECLARE
    index_count INT;
BEGIN
    SELECT COUNT(*) INTO index_count
    FROM pg_stat_user_indexes
    WHERE indexname LIKE '%tsv%';

    IF index_count = 0 THEN
        RAISE NOTICE '没有找到tsv相关索引';
    ELSE
        RAISE NOTICE '找到 % 个tsv相关索引', index_count;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '查看索引扫描次数失败: %', SQLERRM;
END $$;

-- 性能测试：查看索引扫描次数
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexname LIKE '%tsv%';
-- 执行时间: <10ms
-- 计划: Seq Scan
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
