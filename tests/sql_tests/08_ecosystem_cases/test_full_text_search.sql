-- TEST: 全文搜索功能测试
-- DESCRIPTION: 测试PostgreSQL全文搜索的核心功能
-- EXPECTED: 所有搜索和索引功能正常工作
-- TAGS: full-text-search, gin-index, tsvector

-- SETUP
-- 创建测试表
CREATE TABLE test_documents (
    id serial PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    search_vector tsvector
);

-- 创建GIN索引
CREATE INDEX idx_test_documents_search ON test_documents USING gin(search_vector);

-- 创建触发器函数
CREATE OR REPLACE FUNCTION test_documents_search_vector_update()
RETURNS trigger AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.content, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_test_documents_search_vector
    BEFORE INSERT OR UPDATE OF title, content
    ON test_documents
    FOR EACH ROW
    EXECUTE FUNCTION test_documents_search_vector_update();

-- TEST_BODY
-- 测试1：插入数据并验证search_vector自动生成
INSERT INTO test_documents (title, content) VALUES
    ('PostgreSQL Tutorial', 'Learn PostgreSQL database basics and advanced features'),
    ('Database Performance', 'Optimize PostgreSQL queries and indexes for better performance'),
    ('Full Text Search', 'Implement full text search using tsvector and GIN indexes');

-- 验证search_vector已生成
SELECT COUNT(*) FROM test_documents WHERE search_vector IS NOT NULL;  -- EXPECT_VALUE: 3

-- 测试2：基本全文搜索
SELECT COUNT(*) FROM test_documents 
WHERE search_vector @@ to_tsquery('english', 'PostgreSQL');  -- EXPECT_VALUE: 2

-- 测试3：相关性排序
SELECT 
    title,
    ts_rank(search_vector, to_tsquery('english', 'PostgreSQL')) AS rank
FROM test_documents
WHERE search_vector @@ to_tsquery('english', 'PostgreSQL')
ORDER BY rank DESC
LIMIT 1;  -- EXPECT_ROWS: 1

-- 测试4：组合查询（AND操作）
SELECT COUNT(*) FROM test_documents
WHERE search_vector @@ to_tsquery('english', 'PostgreSQL & database');  -- EXPECT_VALUE: 1

-- 测试5：组合查询（OR操作）
SELECT COUNT(*) FROM test_documents
WHERE search_vector @@ to_tsquery('english', 'PostgreSQL | search');  -- EXPECT_VALUE: 3

-- 测试6：前缀搜索
SELECT COUNT(*) FROM test_documents
WHERE search_vector @@ to_tsquery('english', 'Post:*');  -- EXPECT_VALUE: 2

-- 测试7：结果高亮
SELECT 
    title,
    ts_headline(
        'english',
        content,
        to_tsquery('english', 'PostgreSQL'),
        'StartSel=<b>, StopSel=</b>'
    ) AS highlighted
FROM test_documents
WHERE search_vector @@ to_tsquery('english', 'PostgreSQL')
LIMIT 1;  -- EXPECT_ROWS: 1

-- 测试8：GIN索引使用验证
EXPLAIN (COSTS OFF)
SELECT title FROM test_documents
WHERE search_vector @@ to_tsquery('english', 'performance');
-- 应该看到 "Bitmap Index Scan using idx_test_documents_search"

-- 测试9：更新触发器
UPDATE test_documents 
SET content = 'Updated content about PostgreSQL indexing'
WHERE id = 1;

-- 验证search_vector已更新
SELECT search_vector IS NOT NULL AND search_vector::text LIKE '%index%'
FROM test_documents WHERE id = 1;  -- EXPECT_VALUE: true

-- 测试10：权重搜索（标题权重更高）
SELECT 
    title,
    ts_rank(search_vector, to_tsquery('english', 'Tutorial')) AS rank
FROM test_documents
WHERE search_vector @@ to_tsquery('english', 'Tutorial')
ORDER BY rank DESC
LIMIT 1;  -- 应该返回标题中包含Tutorial的记录

-- TEARDOWN
-- 清理测试数据
DROP TRIGGER IF EXISTS trigger_test_documents_search_vector ON test_documents;
DROP FUNCTION IF EXISTS test_documents_search_vector_update();
DROP TABLE IF EXISTS test_documents;

