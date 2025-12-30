---

> **📋 文档来源**: `DataBaseTheory\21-AI知识库\01-知识图谱Schema.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL数据库知识图谱Schema

> **基于OWL本体**

---

## 核心概念层次

```turtle
@prefix pg: <http://postgresql.org/ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# 顶层概念
pg:DatabaseConcept a owl:Class .

# 核心子类
pg:Feature rdfs:subClassOf pg:DatabaseConcept .
pg:Configuration rdfs:subClassOf pg:DatabaseConcept .
pg:Query rdfs:subClassOf pg:DatabaseConcept .
pg:Index rdfs:subClassOf pg:DatabaseConcept .
pg:Transaction rdfs:subClassOf pg:DatabaseConcept .
```

---

## PostgreSQL 18特性本体

```sql
-- 在PostgreSQL中实现
CREATE TABLE concepts (
    concept_id SERIAL PRIMARY KEY,
    concept_name VARCHAR(200) UNIQUE,
    concept_type VARCHAR(50),
    parent_concept_id INT REFERENCES concepts(concept_id),
    description TEXT,
    pg_version VARCHAR(20)
);

CREATE TABLE concept_properties (
    property_id SERIAL PRIMARY KEY,
    concept_id INT REFERENCES concepts(concept_id),
    property_name VARCHAR(100),
    property_value TEXT,
    property_type VARCHAR(50)
);

CREATE TABLE concept_relations (
    relation_id SERIAL PRIMARY KEY,
    from_concept_id INT REFERENCES concepts(concept_id),
    to_concept_id INT REFERENCES concepts(concept_id),
    relation_type VARCHAR(50),  -- enables/requires/optimizes
    strength NUMERIC(3,2)
);

-- 插入PostgreSQL 18特性
INSERT INTO concepts (concept_name, concept_type, description, pg_version) VALUES
('AsyncIO', 'Feature', '异步I/O处理', '18'),
('BuiltinConnectionPool', 'Feature', '内置连接池', '18'),
('SkipScan', 'Feature', 'B-tree索引跳过扫描', '18'),
('IncrementalSort', 'Feature', '增量排序优化', '18');

-- 特性关系
INSERT INTO concept_relations (from_concept_id, to_concept_id, relation_type, strength) VALUES
(1, 2, 'combines_with', 0.9),  -- AsyncIO + ConnectionPool
(3, 4, 'benefits_from', 0.7);  -- SkipScan benefits from IncrementalSort
```

---

## 查询接口

```sql
-- 查询：什么特性可以优化OLTP性能？
WITH RECURSIVE feature_tree AS (
    SELECT c.concept_id, c.concept_name, c.description
    FROM concepts c
    WHERE c.concept_name = 'OLTP'

    UNION ALL

    SELECT c.concept_id, c.concept_name, c.description
    FROM concepts c
    JOIN concept_relations r ON c.concept_id = r.from_concept_id
    JOIN feature_tree ft ON r.to_concept_id = ft.concept_id
    WHERE r.relation_type = 'optimizes'
)
SELECT * FROM feature_tree;
```

---

## 3. 知识图谱扩展设计

### 3.1 版本管理

```sql
-- 概念版本管理表
CREATE TABLE IF NOT EXISTS concept_versions (
    version_id SERIAL PRIMARY KEY,
    concept_id INT REFERENCES concepts(concept_id),
    version_number VARCHAR(20),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_current BOOLEAN DEFAULT TRUE
);

-- 版本管理函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION create_concept_version(
    p_concept_id INT,
    p_version_number VARCHAR(20),
    p_description TEXT
)
RETURNS TABLE (
    version_id INT,
    status TEXT
) AS $$
DECLARE
    new_version_id INT;
BEGIN
    -- 标记旧版本为非当前版本
    UPDATE concept_versions
    SET is_current = FALSE
    WHERE concept_id = p_concept_id AND is_current = TRUE;

    -- 创建新版本
    INSERT INTO concept_versions (concept_id, version_number, description)
    VALUES (p_concept_id, p_version_number, p_description)
    RETURNING version_id INTO new_version_id;

    RETURN QUERY SELECT new_version_id, 'CREATED'::TEXT;

EXCEPTION
    WHEN OTHERS THEN
        RETURN QUERY SELECT NULL::INT, format('FAILED: %', SQLERRM)::TEXT;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 关系权重计算

```sql
-- 关系权重计算函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION calculate_relation_weights()
RETURNS TABLE (
    relation_id INT,
    from_concept TEXT,
    to_concept TEXT,
    relation_type TEXT,
    calculated_weight NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cr.relation_id,
        c1.concept_name AS from_concept,
        c2.concept_name AS to_concept,
        cr.relation_type,
        CASE
            WHEN cr.relation_type = 'requires' THEN 1.0
            WHEN cr.relation_type = 'enables' THEN 0.9
            WHEN cr.relation_type = 'optimizes' THEN 0.8
            WHEN cr.relation_type = 'benefits_from' THEN 0.7
            WHEN cr.relation_type = 'combines_with' THEN 0.6
            ELSE 0.5
        END AS calculated_weight
    FROM concept_relations cr
    JOIN concepts c1 ON cr.from_concept_id = c1.concept_id
    JOIN concepts c2 ON cr.to_concept_id = c2.concept_id;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '计算关系权重失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行权重计算
SELECT * FROM calculate_relation_weights();
```

---

## 4. 知识图谱查询优化

### 4.1 递归查询优化

```sql
-- 优化的递归查询（带性能测试）
CREATE OR REPLACE FUNCTION find_related_concepts(
    p_concept_name VARCHAR(200),
    p_max_depth INT DEFAULT 3
)
RETURNS TABLE (
    concept_name VARCHAR(200),
    relation_path TEXT,
    depth INT
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE concept_path AS (
        -- 起始概念
        SELECT
            c.concept_id,
            c.concept_name,
            c.concept_name::TEXT AS relation_path,
            0 AS depth
        FROM concepts c
        WHERE c.concept_name = p_concept_name

        UNION ALL

        -- 递归扩展
        SELECT
            c.concept_id,
            c.concept_name,
            cp.relation_path || ' -> ' || c.concept_name,
            cp.depth + 1
        FROM concepts c
        JOIN concept_relations r ON c.concept_id = r.to_concept_id
        JOIN concept_path cp ON r.from_concept_id = cp.concept_id
        WHERE cp.depth < p_max_depth
          AND c.concept_name != ALL(string_to_array(cp.relation_path, ' -> '))
    )
    SELECT
        cp.concept_name,
        cp.relation_path,
        cp.depth
    FROM concept_path cp
    WHERE cp.depth > 0
    ORDER BY cp.depth, cp.concept_name;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '查找相关概念失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行查询
SELECT * FROM find_related_concepts('AsyncIO', 3);
```

### 4.2 索引优化

```sql
-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_concepts_name ON concepts(concept_name);
CREATE INDEX IF NOT EXISTS idx_concepts_type ON concepts(concept_type);
CREATE INDEX IF NOT EXISTS idx_concept_relations_from ON concept_relations(from_concept_id);
CREATE INDEX IF NOT EXISTS idx_concept_relations_to ON concept_relations(to_concept_id);
CREATE INDEX IF NOT EXISTS idx_concept_relations_type ON concept_relations(relation_type);

-- 查询性能测试
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM find_related_concepts('AsyncIO', 3);
```

---

## 5. 知识图谱可视化

### 5.1 图结构导出

```sql
-- 导出图结构为JSON格式（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION export_knowledge_graph_json()
RETURNS JSON AS $$
DECLARE
    graph_json JSON;
BEGIN
    SELECT json_build_object(
        'nodes', (
            SELECT json_agg(
                json_build_object(
                    'id', concept_id,
                    'label', concept_name,
                    'type', concept_type,
                    'description', description
                )
            )
            FROM concepts
        ),
        'edges', (
            SELECT json_agg(
                json_build_object(
                    'source', from_concept_id,
                    'target', to_concept_id,
                    'type', relation_type,
                    'weight', strength
                )
            )
            FROM concept_relations
        )
    ) INTO graph_json;

    RETURN graph_json;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '导出知识图谱失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行导出
SELECT export_knowledge_graph_json();
```

### 5.2 图统计信息

```sql
-- 知识图谱统计信息（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION get_knowledge_graph_stats()
RETURNS TABLE (
    metric_name TEXT,
    metric_value BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'total_concepts'::TEXT, COUNT(*)::BIGINT FROM concepts
    UNION ALL
    SELECT 'total_relations'::TEXT, COUNT(*)::BIGINT FROM concept_relations
    UNION ALL
    SELECT 'concepts_by_type'::TEXT, COUNT(DISTINCT concept_type)::BIGINT FROM concepts
    UNION ALL
    SELECT 'avg_relations_per_concept'::TEXT,
           ROUND(AVG(relation_count))::BIGINT
    FROM (
        SELECT concept_id, COUNT(*) AS relation_count
        FROM concept_relations
        GROUP BY concept_id
    ) AS subq;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '获取统计信息失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 查询统计信息
SELECT * FROM get_knowledge_graph_stats();
```

---

**文档完成** ✅
