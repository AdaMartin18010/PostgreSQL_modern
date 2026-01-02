# Party模型完整指南

> **创建日期**: 2025年1月
> **来源**: Silverston《数据模型资源手册》卷1 + 实践总结
> **状态**: 基于权威资源深化扩展
> **文档编号**: 04-02

---

## 📑 目录

- [1. 概述](#1-概述)
- [2. Party模型核心概念](#2-party模型核心概念)
  - [2.1 Party实体](#21-party实体)
  - [2.2 Party Role（角色）](#22-party-role角色)
  - [2.3 Party Relationship（关系）](#23-party-relationship关系)
- [3. Party模型设计优势](#3-party模型设计优势)
- [4. PostgreSQL实现](#4-postgresql实现)
  - [4.1 继承表实现](#41-继承表实现)
  - [4.2 分区表实现](#42-分区表实现)
  - [4.3 多态关联实现](#43-多态关联实现)
- [5. Party模型扩展](#5-party模型扩展)
- [6. 常见应用场景](#6-常见应用场景)
- [7. 相关资源](#7-相关资源)

---

## 1. 概述

Party模型是Silverston《数据模型资源手册》卷1中的核心模型，用于统一表示人员（Person）和组织（Organization）。
该模型通过多态关联支持一个Party扮演多个角色，避免了传统设计中Customer/Supplier/Employee等表的重复设计。

---

## 2. Party模型核心概念

### 2.1 Party实体

**定义**: Party是人员和组织的高层抽象，统一表示所有参与业务活动的实体。

**特点**:

- 统一表示Person和Organization
- 支持未来扩展（如设备、地点等）
- 高度抽象，可复用性强

**传统设计问题**:

```sql
-- ❌ 传统设计：重复的表结构
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20)  -- 重复字段
);

CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20)  -- 重复字段
);
```

**Party模型设计**:

```sql
-- ✅ Party模型：统一设计
CREATE TABLE party (
    party_id SERIAL PRIMARY KEY,
    party_type CHAR(1) NOT NULL CHECK (party_type IN ('P', 'O')),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY LIST (party_type);

CREATE TABLE person PARTITION OF party
    FOR VALUES IN ('P');

CREATE TABLE organization PARTITION OF party
    FOR VALUES IN ('O');
```

---

### 2.2 Party Role（角色）

**定义**: Party可以扮演多个角色，通过Party Role关联表实现多态关联。

**特点**:

- 一个Party可以同时是Customer、Supplier、Employee
- 支持角色有效期（valid_from、valid_to）
- 灵活的角色管理

**PostgreSQL实现**:

```sql
-- Party Role关联表
CREATE TABLE party_role (
    role_id SERIAL PRIMARY KEY,
    party_id INT NOT NULL REFERENCES party(party_id),
    role_type VARCHAR(50) NOT NULL,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    UNIQUE(party_id, role_type, valid_from)
);

-- 角色类型表（可选）
CREATE TABLE role_type (
    role_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- 插入角色类型
INSERT INTO role_type (role_type, description) VALUES
('Customer', '客户'),
('Supplier', '供应商'),
('Employee', '员工'),
('Partner', '合作伙伴'),
('Investor', '投资者');

-- 示例：一个人可以同时是客户和供应商
INSERT INTO person (party_type, name) VALUES ('P', '张三');
INSERT INTO party_role (party_id, role_type) VALUES (1, 'Customer');
INSERT INTO party_role (party_id, role_type) VALUES (1, 'Supplier');

-- 查询：获取所有客户
SELECT p.*, pr.role_type
FROM party p
JOIN party_role pr ON p.party_id = pr.party_id
WHERE pr.role_type = 'Customer'
  AND (pr.valid_to IS NULL OR pr.valid_to > NOW());
```

---

### 2.3 Party Relationship（关系）

**定义**: Party之间的关系，如员工-雇主、客户-供应商等。

**特点**:

- 支持双向关系
- 支持关系类型
- 支持关系有效期

**PostgreSQL实现**:

```sql
-- Party关系表
CREATE TABLE party_relationship (
    relationship_id SERIAL PRIMARY KEY,
    party_id_from INT NOT NULL REFERENCES party(party_id),
    party_id_to INT NOT NULL REFERENCES party(party_id),
    relationship_type VARCHAR(50) NOT NULL,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    CHECK (party_id_from != party_id_to),
    UNIQUE(party_id_from, party_id_to, relationship_type, valid_from)
);

-- 关系类型表
CREATE TABLE relationship_type (
    relationship_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    is_symmetric BOOLEAN DEFAULT FALSE  -- 是否对称关系
);

-- 插入关系类型
INSERT INTO relationship_type (relationship_type, description, is_symmetric) VALUES
('EMPLOYEE_OF', '员工-雇主', FALSE),
('SUBSIDIARY_OF', '子公司-母公司', FALSE),
('PARTNER_WITH', '合作伙伴', TRUE);

-- 示例：员工-雇主关系
INSERT INTO party_relationship (party_id_from, party_id_to, relationship_type)
VALUES (1, 2, 'EMPLOYEE_OF');  -- 人员1是组织2的员工

-- 查询：获取某组织的所有员工
SELECT p.*
FROM party p
JOIN party_relationship pr ON p.party_id = pr.party_id_from
WHERE pr.party_id_to = 2
  AND pr.relationship_type = 'EMPLOYEE_OF'
  AND (pr.valid_to IS NULL OR pr.valid_to > NOW());
```

---

## 3. Party模型设计优势

### 3.1 避免重复设计

**传统设计问题**:

- Customer、Supplier、Employee表结构重复
- 修改字段需要修改多个表
- 无法统一管理

**Party模型优势**:

- 统一表结构，减少重复
- 修改字段只需修改一处
- 统一的数据管理

---

### 3.2 支持业务扩展

**场景**: B2B2C业务，一个Party可能同时是：

- Customer（购买商品）
- Supplier（提供商品）
- Employee（内部员工）

**Party模型支持**:

```sql
-- 一个Party可以扮演多个角色
INSERT INTO party_role (party_id, role_type) VALUES
(1, 'Customer'),
(1, 'Supplier'),
(1, 'Employee');
```

---

### 3.3 灵活的角色管理

**场景**: 角色变更、角色有效期

**Party模型支持**:

```sql
-- 角色变更：将客户角色设为失效
UPDATE party_role
SET valid_to = NOW()
WHERE party_id = 1
  AND role_type = 'Customer'
  AND valid_to IS NULL;

-- 添加新角色
INSERT INTO party_role (party_id, role_type, valid_from)
VALUES (1, 'Partner', NOW());
```

---

## 4. PostgreSQL实现

### 4.1 继承表实现

**方式1: 使用表继承（Table Inheritance）**:

```sql
-- 父表
CREATE TABLE party (
    party_id SERIAL PRIMARY KEY,
    party_type CHAR(1) NOT NULL CHECK (party_type IN ('P', 'O')),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 子表（继承）
CREATE TABLE person (
    party_id INT PRIMARY KEY REFERENCES party(party_id),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    birth_date DATE,
    gender CHAR(1) CHECK (gender IN ('M', 'F', 'O'))
) INHERITS (party);

CREATE TABLE organization (
    party_id INT PRIMARY KEY REFERENCES party(party_id),
    legal_name VARCHAR(200),
    tax_id VARCHAR(50),
    founded_date DATE
) INHERITS (party);

-- 查询：仅查询父表（使用ONLY）
SELECT * FROM ONLY party WHERE party_type = 'P';

-- 查询：查询所有（包括子表）
SELECT * FROM party WHERE party_type = 'P';
```

---

### 4.2 分区表实现

**方式2: 使用声明式分区（推荐，PostgreSQL 10+）**:

```sql
-- 父表（分区表）
CREATE TABLE party (
    party_id SERIAL,
    party_type CHAR(1) NOT NULL CHECK (party_type IN ('P', 'O')),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (party_id, party_type)
) PARTITION BY LIST (party_type);

-- 子分区
CREATE TABLE person PARTITION OF party
    FOR VALUES IN ('P');

CREATE TABLE organization PARTITION OF party
    FOR VALUES IN ('O');

-- 添加子表特定字段（PostgreSQL 11+）
ALTER TABLE person ADD COLUMN first_name VARCHAR(50);
ALTER TABLE person ADD COLUMN last_name VARCHAR(50);
ALTER TABLE organization ADD COLUMN legal_name VARCHAR(200);
ALTER TABLE organization ADD COLUMN tax_id VARCHAR(50);

-- 查询优化：自动分区剪枝
SELECT * FROM party WHERE party_type = 'P';  -- 仅扫描person分区
```

---

### 4.3 多态关联实现

**场景**: 订单可以关联Person或Organization

**实现方式1: 使用Party统一关联**:

```sql
-- ✅ 正确：统一关联Party
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    party_id INT NOT NULL REFERENCES party(party_id),  -- 统一关联
    order_date TIMESTAMPTZ DEFAULT NOW(),
    total_amount NUMERIC(10,2) NOT NULL
);

-- 查询：获取订单的Party信息
SELECT o.*, p.name, p.party_type
FROM orders o
JOIN party p ON o.party_id = p.party_id;
```

**实现方式2: 使用Party Role过滤**:

```sql
-- 查询：获取所有客户订单
SELECT o.*, p.name
FROM orders o
JOIN party p ON o.party_id = p.party_id
JOIN party_role pr ON p.party_id = pr.party_id
WHERE pr.role_type = 'Customer'
  AND (pr.valid_to IS NULL OR pr.valid_to > NOW());
```

---

## 5. Party模型扩展

### 5.1 联系方式扩展

```sql
-- 联系方式表（支持多种联系方式）
CREATE TABLE party_contact (
    contact_id SERIAL PRIMARY KEY,
    party_id INT NOT NULL REFERENCES party(party_id),
    contact_type VARCHAR(20) NOT NULL CHECK (contact_type IN ('EMAIL', 'PHONE', 'ADDRESS', 'WEBSITE')),
    contact_value TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ
);

-- 示例：添加联系方式
INSERT INTO party_contact (party_id, contact_type, contact_value, is_primary) VALUES
(1, 'EMAIL', 'zhangsan@example.com', TRUE),
(1, 'PHONE', '13800138000', TRUE),
(1, 'ADDRESS', '北京市朝阳区...', FALSE);
```

---

### 5.2 地址扩展

```sql
-- 地址表（支持多个地址）
CREATE TABLE party_address (
    address_id SERIAL PRIMARY KEY,
    party_id INT NOT NULL REFERENCES party(party_id),
    address_type VARCHAR(20) NOT NULL CHECK (address_type IN ('BILLING', 'SHIPPING', 'HOME', 'OFFICE')),
    street_address TEXT NOT NULL,
    city VARCHAR(100),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ
);

-- 使用PostGIS存储地理坐标（可选）
CREATE EXTENSION IF NOT EXISTS postgis;

ALTER TABLE party_address ADD COLUMN location GEOGRAPHY(POINT, 4326);

CREATE INDEX idx_party_address_location ON party_address USING GIST (location);
```

---

### 5.3 属性扩展

```sql
-- Party属性表（键值对，支持扩展字段）
CREATE TABLE party_attribute (
    attribute_id SERIAL PRIMARY KEY,
    party_id INT NOT NULL REFERENCES party(party_id),
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value TEXT,
    attribute_type VARCHAR(50) DEFAULT 'TEXT',
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    UNIQUE(party_id, attribute_name, valid_from)
);

-- 示例：添加自定义属性
INSERT INTO party_attribute (party_id, attribute_name, attribute_value, attribute_type) VALUES
(1, 'VIP_LEVEL', 'GOLD', 'TEXT'),
(1, 'CREDIT_LIMIT', '100000', 'NUMERIC'),
(1, 'PREFERRED_LANGUAGE', 'zh-CN', 'TEXT');

-- 查询：使用JSONB聚合属性
SELECT
    p.party_id,
    p.name,
    jsonb_object_agg(pa.attribute_name, pa.attribute_value) AS attributes
FROM party p
LEFT JOIN party_attribute pa ON p.party_id = pa.party_id
WHERE pa.valid_to IS NULL OR pa.valid_to > NOW()
GROUP BY p.party_id, p.name;
```

---

## 6. 常见应用场景

### 6.1 CRM系统

```sql
-- CRM系统中的Party模型
CREATE TABLE party (
    party_id SERIAL PRIMARY KEY,
    party_type CHAR(1) NOT NULL CHECK (party_type IN ('P', 'O')),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY LIST (party_type);

-- 客户角色
INSERT INTO party_role (party_id, role_type) VALUES (1, 'Customer');

-- 客户标签
CREATE TABLE party_tag (
    tag_id SERIAL PRIMARY KEY,
    party_id INT NOT NULL REFERENCES party(party_id),
    tag_name VARCHAR(50) NOT NULL,
    UNIQUE(party_id, tag_name)
);

-- 客户互动历史
CREATE TABLE party_interaction (
    interaction_id SERIAL PRIMARY KEY,
    party_id INT NOT NULL REFERENCES party(party_id),
    interaction_type VARCHAR(50) NOT NULL,
    interaction_date TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);
```

---

### 6.2 ERP系统

```sql
-- ERP系统中的Party模型
-- 供应商角色
INSERT INTO party_role (party_id, role_type) VALUES (2, 'Supplier');

-- 采购订单关联Party
CREATE TABLE purchase_orders (
    po_id BIGSERIAL PRIMARY KEY,
    supplier_id INT NOT NULL REFERENCES party(party_id),
    order_date TIMESTAMPTZ DEFAULT NOW(),
    total_amount NUMERIC(10,2) NOT NULL
);

-- 销售订单关联Party
CREATE TABLE sales_orders (
    so_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES party(party_id),
    order_date TIMESTAMPTZ DEFAULT NOW(),
    total_amount NUMERIC(10,2) NOT NULL
);
```

---

### 6.3 电商平台

```sql
-- 电商平台中的Party模型
-- 一个Party可以同时是：
-- 1. Customer（购买商品）
-- 2. Seller（销售商品）
-- 3. Affiliate（推广商品）

INSERT INTO party_role (party_id, role_type) VALUES
(1, 'Customer'),
(1, 'Seller'),
(1, 'Affiliate');

-- 订单关联Customer
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES party(party_id),
    seller_id INT NOT NULL REFERENCES party(party_id),
    order_date TIMESTAMPTZ DEFAULT NOW(),
    total_amount NUMERIC(10,2) NOT NULL
);
```

---

## 7. 相关资源

- [Silverston数据模型资源手册](../02-权威资源与标准/Silverston数据模型资源手册.md) - Party模型来源
- [范式化设计](./范式化设计.md) - OLTP设计原则
- [PostgreSQL实现](./PostgreSQL实现.md) - PostgreSQL特定实现
- [约束设计](../08-PostgreSQL建模实践/约束设计.md) - 约束设计实践

---

**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
