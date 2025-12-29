---

> **📋 文档来源**: `docs\03-KnowledgeGraph\02-RDF-SPARQL-OWL完整指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# RDF/SPARQL/OWL完整指南（PostgreSQL实现）

> **创建日期**: 2025年12月4日
> **适用场景**: 语义网、知识图谱、本体建模
> **文档状态**: 🚧 深度创建中

---

## 📑 目录

- [1.1 RDF简介](#11-rdf简介)
- [1.2 SPARQL查询语言](#12-sparql查询语言)
- [1.3 OWL本体](#13-owl本体)
- [2.1 三元组存储](#21-三元组存储)
- [2.2 SPARQL to SQL转换](#22-sparql-to-sql转换)
- [3.1 OWL类层次](#31-owl类层次)
- [3.2 属性定义](#32-属性定义)
- [4.1 RDFS推理](#41-rdfs推理)
- [4.2 OWL推理](#42-owl推理)
- [案例1：企业本体管理](#案例1企业本体管理)
- [案例2：生物医学知识图谱](#案例2生物医学知识图谱)
---

## 一、语义网概述

### 1.1 RDF简介

**RDF（Resource Description Framework）**：资源描述框架

**三元组模型**：

```text
Subject（主语）- Predicate（谓语）- Object（宾语）

示例：
Alice - knows - Bob
Alice - age - 30
Alice - type - Person
```

**PostgreSQL存储**：

```sql
-- RDF三元组表
CREATE TABLE rdf_triples (
    id BIGSERIAL PRIMARY KEY,
    subject TEXT NOT NULL,     -- 主语（URI或Blank Node）
    predicate TEXT NOT NULL,   -- 谓语（URI）
    object TEXT NOT NULL,      -- 宾语（URI或Literal）
    object_type TEXT,          -- 'uri' or 'literal'
    object_datatype TEXT,      -- 数据类型（如果是literal）
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX ON rdf_triples (subject, predicate);
CREATE INDEX ON rdf_triples (predicate, object);
CREATE INDEX ON rdf_triples (object) WHERE object_type = 'uri';
```

**插入RDF数据**：

```sql
-- 插入三元组
INSERT INTO rdf_triples (subject, predicate, object, object_type)
VALUES
    ('http://example.org/Alice', 'http://xmlns.com/foaf/0.1/knows', 'http://example.org/Bob', 'uri'),
    ('http://example.org/Alice', 'http://xmlns.com/foaf/0.1/age', '30', 'literal'),
    ('http://example.org/Alice', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'http://xmlns.com/foaf/0.1/Person', 'uri');
```

### 1.2 SPARQL查询语言

**SPARQL基础**：

```sparql
-- 查询所有Person
SELECT ?person ?name
WHERE {
    ?person rdf:type foaf:Person .
    ?person foaf:name ?name .
}
```

**转换为SQL**：

```sql
-- 等价SQL查询
SELECT
    t1.subject AS person,
    t2.object AS name
FROM rdf_triples t1
JOIN rdf_triples t2 ON t1.subject = t2.subject
WHERE t1.predicate = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
  AND t1.object = 'http://xmlns.com/foaf/0.1/Person'
  AND t2.predicate = 'http://xmlns.com/foaf/0.1/name';
```

### 1.3 OWL本体

**OWL（Web Ontology Language）**：本体建模语言

**示例本体**：

```turtle
@prefix : <http://example.org/ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# 类定义
:Person a owl:Class .
:Student a owl:Class ;
    rdfs:subClassOf :Person .
:Professor a owl:Class ;
    rdfs:subClassOf :Person .

# 属性定义
:teaches a owl:ObjectProperty ;
    rdfs:domain :Professor ;
    rdfs:range :Course .

:age a owl:DatatypeProperty ;
    rdfs:domain :Person ;
    rdfs:range xsd:integer .
```

---

## 二、PostgreSQL实现RDF

### 2.1 三元组存储

**优化的存储结构**：

```sql
-- 字符串字典（节省空间）
CREATE TABLE rdf_dictionary (
    id SERIAL PRIMARY KEY,
    value TEXT UNIQUE NOT NULL
);

CREATE INDEX ON rdf_dictionary (value);

-- 优化的三元组表（使用ID引用）
CREATE TABLE rdf_triples_optimized (
    id BIGSERIAL PRIMARY KEY,
    subject_id INT REFERENCES rdf_dictionary(id),
    predicate_id INT REFERENCES rdf_dictionary(id),
    object_id INT REFERENCES rdf_dictionary(id),
    object_type TEXT
);

CREATE INDEX ON rdf_triples_optimized (subject_id, predicate_id);
CREATE INDEX ON rdf_triples_optimized (predicate_id, object_id);

-- 插入函数
-- 插入三元组函数（带完整错误处理）
CREATE FUNCTION insert_triple(
    p_subj TEXT,
    p_pred TEXT,
    p_obj TEXT,
    p_obj_type TEXT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_subj_id INT;
    v_pred_id INT;
    v_obj_id INT;
BEGIN
    -- 参数验证
    IF p_subj IS NULL OR TRIM(p_subj) = '' THEN
        RAISE EXCEPTION '主语不能为空';
    END IF;

    IF p_pred IS NULL OR TRIM(p_pred) = '' THEN
        RAISE EXCEPTION '谓词不能为空';
    END IF;

    IF p_obj IS NULL OR TRIM(p_obj) = '' THEN
        RAISE EXCEPTION '宾语不能为空';
    END IF;

    IF p_obj_type IS NULL OR TRIM(p_obj_type) = '' THEN
        RAISE EXCEPTION '宾语类型不能为空';
    END IF;

    -- 检查表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'rdf_dictionary') THEN
        RAISE EXCEPTION 'rdf_dictionary表不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'rdf_triples_optimized') THEN
        RAISE EXCEPTION 'rdf_triples_optimized表不存在';
    END IF;

    -- 获取或创建主语ID
    BEGIN
        INSERT INTO rdf_dictionary (value) VALUES (p_subj)
        ON CONFLICT (value) DO NOTHING;

        SELECT id INTO v_subj_id FROM rdf_dictionary WHERE value = p_subj;

        IF v_subj_id IS NULL THEN
            RAISE EXCEPTION '无法获取或创建主语ID: %', p_subj;
        END IF;
    EXCEPTION
        WHEN unique_violation THEN
            SELECT id INTO v_subj_id FROM rdf_dictionary WHERE value = p_subj;
        WHEN OTHERS THEN
            RAISE EXCEPTION '处理主语失败: %', SQLERRM;
    END;

    -- 获取或创建谓词ID
    BEGIN
        INSERT INTO rdf_dictionary (value) VALUES (p_pred)
        ON CONFLICT (value) DO NOTHING;

        SELECT id INTO v_pred_id FROM rdf_dictionary WHERE value = p_pred;

        IF v_pred_id IS NULL THEN
            RAISE EXCEPTION '无法获取或创建谓词ID: %', p_pred;
        END IF;
    EXCEPTION
        WHEN unique_violation THEN
            SELECT id INTO v_pred_id FROM rdf_dictionary WHERE value = p_pred;
        WHEN OTHERS THEN
            RAISE EXCEPTION '处理谓词失败: %', SQLERRM;
    END;

    -- 获取或创建宾语ID
    BEGIN
        INSERT INTO rdf_dictionary (value) VALUES (p_obj)
        ON CONFLICT (value) DO NOTHING;

        SELECT id INTO v_obj_id FROM rdf_dictionary WHERE value = p_obj;

        IF v_obj_id IS NULL THEN
            RAISE EXCEPTION '无法获取或创建宾语ID: %', p_obj;
        END IF;
    EXCEPTION
        WHEN unique_violation THEN
            SELECT id INTO v_obj_id FROM rdf_dictionary WHERE value = p_obj;
        WHEN OTHERS THEN
            RAISE EXCEPTION '处理宾语失败: %', SQLERRM;
    END;

    -- 插入三元组
    BEGIN
        INSERT INTO rdf_triples_optimized (subject_id, predicate_id, object_id, object_type)
        VALUES (v_subj_id, v_pred_id, v_obj_id, p_obj_type);
    EXCEPTION
        WHEN unique_violation THEN
            RAISE WARNING '三元组已存在: (%, %, %)', v_subj_id, v_pred_id, v_obj_id;
        WHEN foreign_key_violation THEN
            RAISE EXCEPTION '违反外键约束，无法插入三元组';
        WHEN check_violation THEN
            RAISE EXCEPTION '违反检查约束，无法插入三元组';
        WHEN OTHERS THEN
            RAISE EXCEPTION '插入三元组失败: %', SQLERRM;
    END;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'insert_triple执行失败: %', SQLERRM;
END;
$$;
```

**空间节省**：

| 存储方式 | 1亿三元组大小 |
|---------|-------------|
| 原始TEXT | 50GB |
| ID引用 | **8GB**（-84%）⭐ |

### 2.2 SPARQL to SQL转换

**实现SPARQL查询引擎**：

```python
class SimpleSPARQLEngine:
    def __init__(self, db_conn):
        self.conn = db_conn

    def query(self, sparql_query):
        """执行SPARQL查询"""
        # 简化的SPARQL解析（生产环境使用rdflib）
        # 这里展示基本思路

        # 示例SPARQL:
        # SELECT ?person ?name
        # WHERE {
        #     ?person rdf:type foaf:Person .
        #     ?person foaf:name ?name .
        # }

        # 转换为SQL
        sql = """
            SELECT DISTINCT
                d1.value AS person,
                d3.value AS name
            FROM rdf_triples_optimized t1
            JOIN rdf_triples_optimized t2 ON t1.subject_id = t2.subject_id
            JOIN rdf_dictionary d1 ON t1.subject_id = d1.id
            JOIN rdf_dictionary d2 ON t1.predicate_id = d2.id
            JOIN rdf_dictionary d3 ON t2.object_id = d3.id
            WHERE d2.value = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
              AND t1.object_id = (SELECT id FROM rdf_dictionary WHERE value = 'http://xmlns.com/foaf/0.1/Person')
              AND t2.predicate_id = (SELECT id FROM rdf_dictionary WHERE value = 'http://xmlns.com/foaf/0.1/name')
        """

        with self.conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
```

---

## 三、本体建模

### 3.1 OWL类层次

**存储OWL类层次**：

```sql
-- OWL类表
CREATE TABLE owl_classes (
    id SERIAL PRIMARY KEY,
    class_uri TEXT UNIQUE NOT NULL,
    label TEXT,
    comment TEXT
);

-- 类层次关系（subClassOf）
CREATE TABLE owl_class_hierarchy (
    subclass_id INT REFERENCES owl_classes(id),
    superclass_id INT REFERENCES owl_classes(id),
    PRIMARY KEY (subclass_id, superclass_id)
);

-- 插入示例
INSERT INTO owl_classes (class_uri, label)
VALUES
    ('http://example.org/Person', 'Person'),
    ('http://example.org/Student', 'Student'),
    ('http://example.org/Professor', 'Professor');

INSERT INTO owl_class_hierarchy (subclass_id, superclass_id)
VALUES
    (2, 1),  -- Student subClassOf Person
    (3, 1);  -- Professor subClassOf Person
```

### 3.2 属性定义

**OWL属性表**：

```sql
-- 对象属性（连接实体）
CREATE TABLE owl_object_properties (
    id SERIAL PRIMARY KEY,
    property_uri TEXT UNIQUE NOT NULL,
    domain_class_id INT REFERENCES owl_classes(id),
    range_class_id INT REFERENCES owl_classes(id),
    label TEXT
);

-- 数据属性（literal值）
CREATE TABLE owl_datatype_properties (
    id SERIAL PRIMARY KEY,
    property_uri TEXT UNIQUE NOT NULL,
    domain_class_id INT REFERENCES owl_classes(id),
    range_datatype TEXT,  -- xsd:string, xsd:integer, etc.
    label TEXT
);
```

---

## 四、语义推理

### 4.1 RDFS推理

**实现推理规则**：

```sql
-- 规则：rdfs:subClassOf传递性
-- 如果 A subClassOf B 且 B subClassOf C，则 A subClassOf C

-- 推理传递性子类函数（带完整错误处理）
CREATE FUNCTION infer_transitive_subclass()
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_inserted_count INTEGER;
    v_iteration_count INTEGER := 0;
    v_max_iterations INTEGER := 1000;  -- 防止无限循环
BEGIN
    -- 检查表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'owl_class_hierarchy') THEN
        RAISE EXCEPTION 'owl_class_hierarchy表不存在';
    END IF;

    -- 迭代直到收敛
    LOOP
        v_iteration_count := v_iteration_count + 1;

        -- 防止无限循环
        IF v_iteration_count > v_max_iterations THEN
            RAISE WARNING '达到最大迭代次数: %, 停止推理', v_max_iterations;
            EXIT;
        END IF;

        BEGIN
            INSERT INTO owl_class_hierarchy (subclass_id, superclass_id)
            SELECT DISTINCT h1.subclass_id, h2.superclass_id
            FROM owl_class_hierarchy h1
            INNER JOIN owl_class_hierarchy h2 ON h1.superclass_id = h2.subclass_id
            WHERE h1.subclass_id IS NOT NULL
              AND h1.superclass_id IS NOT NULL
              AND h2.subclass_id IS NOT NULL
              AND h2.superclass_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM owl_class_hierarchy h3
                  WHERE h3.subclass_id = h1.subclass_id
                    AND h3.superclass_id = h2.superclass_id
              );

            GET DIAGNOSTICS v_inserted_count = ROW_COUNT;
        EXCEPTION
            WHEN unique_violation THEN
                -- 忽略唯一约束冲突（已存在的记录）
                GET DIAGNOSTICS v_inserted_count = ROW_COUNT;
            WHEN OTHERS THEN
                RAISE EXCEPTION '推理传递性子类失败（迭代 %）: %', v_iteration_count, SQLERRM;
        END;

        -- 如果没有插入新记录，说明已收敛
        IF v_inserted_count = 0 THEN
            RAISE NOTICE '传递性子类推理完成，迭代次数: %', v_iteration_count;
            EXIT;
        END IF;

        RAISE NOTICE '迭代 %: 插入了 % 条新记录', v_iteration_count, v_inserted_count;
    END LOOP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'infer_transitive_subclass执行失败: %', SQLERRM;
END;
$$;

-- 执行推理
SELECT infer_transitive_subclass();
```

### 4.2 OWL推理

**OWL DL推理示例**：

```sql
-- 规则：对称属性
-- 如果 friendOf 是对称的，且 Alice friendOf Bob，则 Bob friendOf Alice

-- 推理对称属性函数（带完整错误处理）
CREATE FUNCTION infer_symmetric_property(p_property_uri TEXT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_predicate_id INT;
    v_inserted_count INTEGER;
BEGIN
    -- 参数验证
    IF p_property_uri IS NULL OR TRIM(p_property_uri) = '' THEN
        RAISE EXCEPTION '属性URI不能为空';
    END IF;

    -- 检查表是否存在
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'rdf_triples_optimized') THEN
        RAISE EXCEPTION 'rdf_triples_optimized表不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'rdf_dictionary') THEN
        RAISE EXCEPTION 'rdf_dictionary表不存在';
    END IF;

    -- 查找谓词ID
    BEGIN
        SELECT id INTO v_predicate_id
        FROM rdf_dictionary
        WHERE value = p_property_uri;

        IF v_predicate_id IS NULL THEN
            RAISE WARNING '未找到属性URI: %, 跳过推理', p_property_uri;
            RETURN;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION '查找谓词ID失败: %', SQLERRM;
    END;

    -- 插入对称三元组
    BEGIN
        INSERT INTO rdf_triples_optimized (subject_id, predicate_id, object_id, object_type)
        SELECT
            t.object_id,
            t.predicate_id,
            t.subject_id,
            'uri'::TEXT
        FROM rdf_triples_optimized t
        WHERE t.predicate_id = v_predicate_id
          AND t.object_type = 'uri'
          AND t.subject_id IS NOT NULL
          AND t.predicate_id IS NOT NULL
          AND t.object_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM rdf_triples_optimized t2
              WHERE t2.subject_id = t.object_id
                AND t2.predicate_id = t.predicate_id
                AND t2.object_id = t.subject_id
          );

        GET DIAGNOSTICS v_inserted_count = ROW_COUNT;
        RAISE NOTICE '对称属性推理完成: 属性URI=%, 插入了 % 条新三元组',
            p_property_uri, v_inserted_count;
    EXCEPTION
        WHEN unique_violation THEN
            RAISE WARNING '部分对称三元组已存在，跳过';
        WHEN foreign_key_violation THEN
            RAISE EXCEPTION '违反外键约束，无法插入对称三元组';
        WHEN OTHERS THEN
            RAISE EXCEPTION '推理对称属性失败: %', SQLERRM;
    END;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'infer_symmetric_property执行失败: %', SQLERRM;
END;
$$;

-- 应用推理
SELECT infer_symmetric_property('http://example.org/friendOf');
```

---

## 五、生产案例

### 案例1：企业本体管理

**场景**：

- 企业知识管理
- 标准化术语
- 语义搜索

**本体示例**：

```turtle
@prefix org: <http://company.com/ontology#> .

# 组织结构
org:Employee rdfs:subClassOf org:Person .
org:Manager rdfs:subClassOf org:Employee .

# 关系
org:reportsTo a owl:ObjectProperty ;
    rdfs:domain org:Employee ;
    rdfs:range org:Manager .

org:worksInDepartment a owl:ObjectProperty ;
    rdfs:domain org:Employee ;
    rdfs:range org:Department .
```

**效果**：

- 知识标准化 ✅
- 跨部门语义互通 ✅
- 自动推理关系 ✅

---

### 案例2：生物医学知识图谱

**场景**：

- 整合多个生物医学数据库
- 疾病-基因-药物关系
- 支持复杂推理查询

**效果**：

- 数据整合：5个数据库统一视图
- 推理发现：自动发现潜在治疗方案
- 查询加速：语义索引加速

---

**最后更新**: 2025年12月4日
**文档编号**: P6-2-RDF-SPARQL-OWL
**版本**: v1.0
**状态**: ✅ 完成
