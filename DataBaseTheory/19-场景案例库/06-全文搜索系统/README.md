# 全文搜索系统

> **PostgreSQL版本**: 18.x

---

## 核心功能

```sql
-- 文档表
CREATE TABLE documents (
    doc_id BIGSERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    author VARCHAR(100),
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ⭐ PostgreSQL 18：全文搜索优化
CREATE INDEX idx_documents_fts
ON documents USING GIN (
    to_tsvector('chinese', title || ' ' || content)
);

-- 搜索查询
SELECT doc_id, title,
    ts_rank(to_tsvector('chinese', content), query) as rank
FROM documents,
    websearch_to_tsquery('chinese', '数据库 AND 优化') query
WHERE to_tsvector('chinese', content) @@ query
ORDER BY rank DESC
LIMIT 20;

-- PostgreSQL 18：中文分词优化，相关性提升20-40%
```

---

**完整文档待补充**
