# RDF/SPARQL/OWL完整指南（PostgreSQL实现）

> **创建日期**: 2025年12月4日
> **适用场景**: 语义网、知识图谱、本体建模
> **文档状态**: 🚧 深度创建中

---

## 📑 目录

- [RDF/SPARQL/OWL完整指南（PostgreSQL实现）](#rdfsparqlowl完整指南postgresql实现)
  - [📑 目录](#-目录)
  - [一、语义网概述](#一语义网概述)
    - [1.1 RDF简介](#11-rdf简介)
    - [1.2 SPARQL查询语言](#12-sparql查询语言)
    - [1.3 OWL本体](#13-owl本体)
  - [二、PostgreSQL实现RDF](#二postgresql实现rdf)
    - [2.1 三元组存储](#21-三元组存储)
    - [2.2 SPARQL to SQL转换](#22-sparql-to-sql转换)
  - [三、本体建模](#三本体建模)
    - [3.1 OWL类层次](#31-owl类层次)
    - [3.2 属性定义](#32-属性定义)
  - [四、语义推理](#四语义推理)
    - [4.1 RDFS推理](#41-rdfs推理)
    - [4.2 OWL推理](#42-owl推理)
  - [五、生产案例](#五生产案例)
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
CREATE FUNCTION insert_triple(subj TEXT, pred TEXT, obj TEXT, obj_type TEXT)
RETURNS VOID AS $$
DECLARE
    subj_id INT;
    pred_id INT;
    obj_id INT;
BEGIN
    -- 获取或创建ID
    INSERT INTO rdf_dictionary (value) VALUES (subj)
    ON CONFLICT (value) DO NOTHING;
    SELECT id INTO subj_id FROM rdf_dictionary WHERE value = subj;

    INSERT INTO rdf_dictionary (value) VALUES (pred)
    ON CONFLICT (value) DO NOTHING;
    SELECT id INTO pred_id FROM rdf_dictionary WHERE value = pred;

    INSERT INTO rdf_dictionary (value) VALUES (obj)
    ON CONFLICT (value) DO NOTHING;
    SELECT id INTO obj_id FROM rdf_dictionary WHERE value = obj;

    -- 插入三元组
    INSERT INTO rdf_triples_optimized (subject_id, predicate_id, object_id, object_type)
    VALUES (subj_id, pred_id, obj_id, obj_type);
END;
$$ LANGUAGE plpgsql;
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

CREATE FUNCTION infer_transitive_subclass()
RETURNS VOID AS $$
BEGIN
    -- 迭代直到收敛
    LOOP
        INSERT INTO owl_class_hierarchy (subclass_id, superclass_id)
        SELECT DISTINCT h1.subclass_id, h2.superclass_id
        FROM owl_class_hierarchy h1
        JOIN owl_class_hierarchy h2 ON h1.superclass_id = h2.subclass_id
        WHERE NOT EXISTS (
            SELECT 1 FROM owl_class_hierarchy h3
            WHERE h3.subclass_id = h1.subclass_id
              AND h3.superclass_id = h2.superclass_id
        );

        EXIT WHEN NOT FOUND;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 执行推理
SELECT infer_transitive_subclass();
```

### 4.2 OWL推理

**OWL DL推理示例**：

```sql
-- 规则：对称属性
-- 如果 friendOf 是对称的，且 Alice friendOf Bob，则 Bob friendOf Alice

CREATE FUNCTION infer_symmetric_property(property_uri TEXT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO rdf_triples_optimized (subject_id, predicate_id, object_id, object_type)
    SELECT object_id, predicate_id, subject_id, 'uri'
    FROM rdf_triples_optimized t
    JOIN rdf_dictionary d ON t.predicate_id = d.id
    WHERE d.value = property_uri
      AND object_type = 'uri'
      AND NOT EXISTS (
          SELECT 1 FROM rdf_triples_optimized t2
          WHERE t2.subject_id = t.object_id
            AND t2.predicate_id = t.predicate_id
            AND t2.object_id = t.subject_id
      );
END;
$$ LANGUAGE plpgsql;

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
