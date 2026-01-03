# Party模型完整指南

> **创建日期**: 2025年1月
> **来源**: Silverston《数据模型资源手册》卷1 + 实践总结
> **状态**: 基于权威资源深化扩展
> **文档编号**: 04-02

---

## 📑 目录

- [Party模型完整指南](#party模型完整指南)
  - [📑 目录](#-目录)
  - [1. 概述 / Overview](#1-概述--overview)
    - [1.1 业务背景 / Business Context](#11-业务背景--business-context)
    - [1.2 核心概念 / Core Concepts](#12-核心概念--core-concepts)
    - [1.3 应用场景 / Application Scenarios](#13-应用场景--application-scenarios)
    - [1.4 与Volume 1的对应关系 / Mapping to Volume 1](#14-与volume-1的对应关系--mapping-to-volume-1)
  - [2. Party模型核心概念 / Core Concepts](#2-party模型核心概念--core-concepts)
    - [2.1 Organization（组织）实体](#21-organization组织实体)
    - [2.2 Person（人员）实体](#22-person人员实体)
    - [2.3 Party实体](#23-party实体)
    - [2.4 Party Role（参与方角色）](#24-party-role参与方角色)
    - [2.5 Party Relationship（参与方关系）](#25-party-relationship参与方关系)
  - [3. Party模型设计优势](#3-party模型设计优势)
    - [3.1 避免重复设计](#31-避免重复设计)
    - [3.2 支持业务扩展](#32-支持业务扩展)
    - [3.3 灵活的角色管理](#33-灵活的角色管理)
  - [6. 完整PostgreSQL实现 / Complete PostgreSQL Implementation](#6-完整postgresql实现--complete-postgresql-implementation)
    - [6.1 完整DDL脚本 / Complete DDL Script](#61-完整ddl脚本--complete-ddl-script)
    - [6.2 索引设计 / Index Design](#62-索引设计--index-design)
    - [6.3 约束设计 / Constraint Design](#63-约束设计--constraint-design)
    - [6.4 视图设计 / View Design](#64-视图设计--view-design)
  - [7. PostgreSQL实现 / PostgreSQL Implementation](#7-postgresql实现--postgresql-implementation)
    - [7.1 继承表实现 / Table Inheritance Implementation](#71-继承表实现--table-inheritance-implementation)
    - [4.2 分区表实现](#42-分区表实现)
    - [4.3 多态关联实现](#43-多态关联实现)
  - [5. Party Contact Information（参与方联系方式） / Party Contact Information](#5-party-contact-information参与方联系方式--party-contact-information)
    - [5.1 Postal Address Information（邮政地址信息）](#51-postal-address-information邮政地址信息)
    - [5.2 Party Contact Mechanism（参与方联系方式机制）](#52-party-contact-mechanism参与方联系方式机制)
    - [5.3 Facility Versus Contact Mechanism（设施与联系方式）](#53-facility-versus-contact-mechanism设施与联系方式)
    - [5.4 Party Communication Event（参与方通信事件）](#54-party-communication-event参与方通信事件)
  - [6. 常见应用场景](#6-常见应用场景)
    - [6.1 CRM系统](#61-crm系统)
    - [6.2 ERP系统](#62-erp系统)
    - [6.3 电商平台](#63-电商平台)
  - [7. 相关资源](#7-相关资源)

---

## 1. 概述 / Overview

### 1.1 业务背景 / Business Context

Party模型是Silverston《数据模型资源手册》卷1（Volume 1 Chapter 2: People and Organizations）中的核心模型，用于统一表示人员（Person）和组织（Organization）。

**核心业务问题**:

- 如何统一管理客户、供应商、员工等不同角色的信息？
- 如何避免在多个系统中重复存储相同的组织或人员信息？
- 如何支持一个Party同时扮演多个角色（如既是客户又是供应商）？
- 如何跟踪Party之间的关系（如员工-雇主、客户-供应商）？
- 如何管理Party的多种联系方式（地址、电话、邮件等）？

### 1.2 核心概念 / Core Concepts

**Party（参与方）**: 统一表示人员和组织的高层抽象实体

**Party Role（参与方角色）**: Party可以扮演的角色，如Customer、Supplier、Employee等

**Party Relationship（参与方关系）**: Party之间的关系，如员工-雇主、客户-供应商

**Contact Mechanism（联系方式）**: 联系Party的机制，包括邮政地址、电话号码、电子邮箱等

### 1.3 应用场景 / Application Scenarios

- **CRM系统**: 统一管理客户、潜在客户、合作伙伴
- **ERP系统**: 统一管理供应商、客户、内部组织
- **HR系统**: 统一管理员工、承包商、联系人
- **电商平台**: 统一管理买家、卖家、推广者

### 1.4 与Volume 1的对应关系 / Mapping to Volume 1

本模型基于Volume 1 Chapter 2的完整内容，包括：

- **2.1 Organization**: 组织模型
- **2.2 Person**: 人员模型（包括Alternate Model）
- **2.3 Party**: Party统一模型
- **2.4 Party Roles**: 角色模型（Person Roles、Organization Roles）
- **2.5 Party Relationship**: 关系模型
- **2.6 Party Contact Information**: 联系方式模型
- **2.7 Postal Address Information**: 邮政地址模型
- **2.8 Geographic Boundaries**: 地理边界模型
- **2.9 Party Contact Mechanism**: 联系方式机制模型
- **2.10 Party Communication Event**: 通信事件模型

---

---

## 2. Party模型核心概念 / Core Concepts

### 2.1 Organization（组织）实体

**定义 / Definition**: Organization表示具有共同目的的人群集合，如公司、部门、政府机构、非营利组织等。

**业务问题 / Business Problem**:

- 传统设计中，Customer、Supplier、Department等表结构重复
- 组织信息变更（如地址）需要在多个系统中更新
- 无法统一管理组织信息

**Volume 1设计 / Volume 1 Design**:

Organization可以进一步细分为：

- **Legal Organization（法律组织）**: 如Corporation、Government Agency
- **Informal Organization（非正式组织）**: 如Family、Team、Department

**PostgreSQL实现 / PostgreSQL Implementation**:

```sql
-- Organization实体（作为Party的子类型）
CREATE TABLE organization (
    party_id INT PRIMARY KEY REFERENCES party(party_id),
    legal_name VARCHAR(200),
    tax_id VARCHAR(50),
    founded_date DATE,
    organization_type VARCHAR(50)  -- Legal/Informal
);

-- Legal Organization子类型
CREATE TABLE legal_organization (
    party_id INT PRIMARY KEY REFERENCES organization(party_id),
    registration_number VARCHAR(100),
    incorporation_date DATE
);

-- Informal Organization子类型
CREATE TABLE informal_organization (
    party_id INT PRIMARY KEY REFERENCES organization(party_id),
    organization_purpose TEXT
);
```

---

### 2.2 Person（人员）实体

**定义 / Definition**: Person表示个人实体，独立于其工作或角色。

**业务问题 / Business Problem**:

- 同一个人可能在不同时间扮演不同角色（客户→承包商→员工）
- 同一人可能同时扮演多个角色（员工+客户+供应商联系人）
- 人员信息在多个系统中重复存储

**Volume 1设计 / Volume 1 Design**:

Person包含以下属性：

- **基本信息**: first_name, last_name, middle_name, gender, birth_date
- **物理特征**: height, weight（可历史跟踪）
- **身份信息**: passport_number, citizenship
- **婚姻状况**: marital_status（可历史跟踪）

**PostgreSQL实现 / PostgreSQL Implementation**:

```sql
-- Person实体（标准模型）
CREATE TABLE person (
    party_id INT PRIMARY KEY REFERENCES party(party_id),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    middle_name VARCHAR(50),
    birth_date DATE,
    gender CHAR(1) CHECK (gender IN ('M', 'F', 'O', 'U')),  -- M=Male, F=Female, O=Other, U=Unknown
    height VARCHAR(20),  -- 如 "6'0\""
    weight NUMERIC(5,2),  -- 单位：磅或公斤
    passport_number VARCHAR(50),
    passport_expiration_date DATE,
    current_marital_status VARCHAR(20)
);

-- Person Alternate Model（支持历史跟踪）
CREATE TABLE person_name (
    party_id INT NOT NULL REFERENCES person(party_id),
    name_seq_id INT NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    middle_name VARCHAR(50),
    name_type VARCHAR(20),  -- Current, Alias, Previous
    valid_from DATE NOT NULL,
    valid_to DATE,
    PRIMARY KEY (party_id, name_seq_id)
);

CREATE TABLE marital_status (
    party_id INT NOT NULL REFERENCES person(party_id),
    marital_status_type VARCHAR(20) NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE,
    PRIMARY KEY (party_id, marital_status_type, valid_from)
);

CREATE TABLE physical_characteristic (
    party_id INT NOT NULL REFERENCES person(party_id),
    characteristic_type VARCHAR(50) NOT NULL,  -- Height, Weight, Blood Pressure
    characteristic_value VARCHAR(100),
    measurement_date DATE NOT NULL,
    PRIMARY KEY (party_id, characteristic_type, measurement_date)
);
```

---

### 2.3 Party实体

**定义 / Definition**: Party是Person和Organization的父类型（Supertype），统一表示所有参与业务活动的实体。

**设计优势 / Design Advantages**:

- 统一表示Person和Organization
- 避免在订单、合同等交易中需要两个关系（一个到Person，一个到Organization）
- 支持未来扩展（如设备、地点等）
- 高度抽象，可复用性强

**Volume 1设计 / Volume 1 Design**:

Party通过Party Classification进行分类：

- **Organization Classification**: Industry Classification, Size Classification, Minority Classification
- **Person Classification**: EEOC Classification, Income Classification

**PostgreSQL实现 / PostgreSQL Implementation**:

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

### 2.4 Party Role（参与方角色）

**定义 / Definition**: Party可以扮演多个角色，通过Party Role关联表实现多态关联。
角色定义了Party在特定上下文中的行为方式。

**Volume 1设计 / Volume 1 Design**:

Party Role分为三类：

- **Person Roles（人员角色）**: Employee, Contractor, Family Member, Contact
- **Organization Roles（组织角色）**: Distribution Channel, Competitor, Partner, Regulatory Agency, Supplier, Organization Unit
- **Common Roles（通用角色）**: Customer, Shareholder, Prospect

**角色设计决策 / Role Design Decision**:

Volume 1讨论了两种设计方式：

1. **角色作为Party的子类型**: 简单但不够灵活
2. **独立的Party Role实体**: 灵活，支持同一Party扮演多个角色（**推荐**）

**PostgreSQL实现 / PostgreSQL Implementation**:

```sql
-- Party Role实体（基于Volume 1 Figure 2.4）
CREATE TABLE party_role (
    party_role_id SERIAL PRIMARY KEY,
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    role_type VARCHAR(50) NOT NULL,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type),
    UNIQUE(party_id, role_type, valid_from)
);

-- Party Role Type（角色类型）
CREATE TABLE party_role_type (
    role_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    role_category VARCHAR(20) CHECK (role_category IN ('PERSON', 'ORGANIZATION', 'COMMON'))
);

-- 插入Person Roles
INSERT INTO party_role_type (role_type, description, role_category) VALUES
('EMPLOYEE', '员工', 'PERSON'),
('CONTRACTOR', '承包商', 'PERSON'),
('FAMILY_MEMBER', '家庭成员', 'PERSON'),
('CONTACT', '联系人', 'PERSON');

-- 插入Organization Roles
INSERT INTO party_role_type (role_type, description, role_category) VALUES
('DISTRIBUTION_CHANNEL', '分销渠道', 'ORGANIZATION'),
('AGENT', '代理商', 'ORGANIZATION'),
('DISTRIBUTOR', '分销商', 'ORGANIZATION'),
('COMPETITOR', '竞争对手', 'ORGANIZATION'),
('PARTNER', '合作伙伴', 'ORGANIZATION'),
('REGULATORY_AGENCY', '监管机构', 'ORGANIZATION'),
('HOUSEHOLD', '家庭', 'ORGANIZATION'),
('ASSOCIATION', '协会', 'ORGANIZATION'),
('SUPPLIER', '供应商', 'ORGANIZATION'),
('PARENT_ORGANIZATION', '母公司', 'ORGANIZATION'),
('SUBSIDIARY', '子公司', 'ORGANIZATION'),
('DEPARTMENT', '部门', 'ORGANIZATION'),
('DIVISION', '事业部', 'ORGANIZATION'),
('INTERNAL_ORGANIZATION', '内部组织', 'ORGANIZATION');

-- 插入Common Roles
INSERT INTO party_role_type (role_type, description, role_category) VALUES
('CUSTOMER', '客户', 'COMMON'),
('BILL_TO_CUSTOMER', '账单客户', 'COMMON'),
('SHIP_TO_CUSTOMER', '收货客户', 'COMMON'),
('END_USER_CUSTOMER', '最终用户客户', 'COMMON'),
('SHAREHOLDER', '股东', 'COMMON'),
('PROSPECT', '潜在客户', 'COMMON');

-- 示例：John Smith扮演多个角色（基于Volume 1 Table 2.4）
INSERT INTO party_role (party_id, party_type, role_type) VALUES
(5000, 'P', 'EMPLOYEE'),
(5000, 'P', 'SUPPLIER_COORDINATOR'),
(5000, 'P', 'PARENT'),
(5000, 'P', 'TEAM_LEADER'),
(5000, 'P', 'MENTOR');

-- 查询：获取所有客户
SELECT p.party_id, p.name, p.party_type, pr.role_type, prt.description
FROM party p
JOIN party_role pr ON p.party_id = pr.party_id AND p.party_type = pr.party_type
JOIN party_role_type prt ON pr.role_type = prt.role_type
WHERE prt.role_type IN ('CUSTOMER', 'BILL_TO_CUSTOMER', 'SHIP_TO_CUSTOMER', 'END_USER_CUSTOMER')
  AND (pr.valid_to IS NULL OR pr.valid_to > NOW());

-- 查询：获取某组织的所有员工
SELECT p.party_id, p.name, pr.valid_from, pr.valid_to
FROM party p
JOIN party_role pr ON p.party_id = pr.party_id AND p.party_type = pr.party_type
WHERE pr.role_type = 'EMPLOYEE'
  AND pr.party_id IN (
      SELECT party_id FROM party_role
      WHERE role_type = 'INTERNAL_ORGANIZATION'
        AND party_id = 200  -- ABC Subsidiary
  )
  AND (pr.valid_to IS NULL OR pr.valid_to > NOW());
```

**Volume 1示例数据 / Volume 1 Example Data**:

根据Volume 1 Table 2.4，Party Role数据示例：

| Party ID | Party Name | Role Type |
|----------|-----------|-----------|
| 100 | ABC Corporation | Internal organization, Parent organization |
| 5000 | John Smith | Employee, Supplier coordinator, Parent, Team leader, Mentor |
| 700 | ACME Corporation | Customer, Supplier |

---

---

### 2.5 Party Relationship（参与方关系）

**定义 / Definition**: Party之间的关系，定义了两个Party及其各自角色之间的关系。

**业务问题 / Business Problem**:

- 仅知道Party是Customer不够，需要知道是哪个内部组织的Customer
- 需要跟踪关系的状态、优先级、备注等信息
- 需要记录关系的历史变化

**Volume 1设计 / Volume 1 Design**:

Party Relationship包含：

- **Specific Party Relationships（特定关系）**: Customer Relationship, Employment, Organization Rollup
- **Common Party Relationships（通用关系）**: 通用的关系模型
- **Party Relationship Information（关系信息）**: Status, Priority, Communication Events

**PostgreSQL实现 / PostgreSQL Implementation**:

```sql
-- Party Relationship实体（基于Volume 1 Figure 2.6a）
CREATE TABLE party_relationship (
    party_relationship_id SERIAL PRIMARY KEY,
    party_id_from INT NOT NULL,
    party_type_from CHAR(1) NOT NULL,
    party_role_id_from INT NOT NULL,  -- 关联到Party Role
    party_id_to INT NOT NULL,
    party_type_to CHAR(1) NOT NULL,
    party_role_id_to INT NOT NULL,  -- 关联到Party Role
    relationship_type VARCHAR(50) NOT NULL,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id_from, party_type_from) REFERENCES party(party_id, party_type),
    FOREIGN KEY (party_id_to, party_type_to) REFERENCES party(party_id, party_type),
    FOREIGN KEY (party_role_id_from) REFERENCES party_role(party_role_id),
    FOREIGN KEY (party_role_id_to) REFERENCES party_role(party_role_id),
    CHECK (party_id_from != party_id_to OR party_type_from != party_type_to),
    UNIQUE(party_id_from, party_type_from, party_role_id_from,
           party_id_to, party_type_to, party_role_id_to, relationship_type, valid_from)
);

-- Party Relationship Type（关系类型）
CREATE TABLE party_relationship_type (
    relationship_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    from_role_type VARCHAR(50) NOT NULL,  -- 起始角色类型
    to_role_type VARCHAR(50) NOT NULL     -- 目标角色类型
);

-- 插入关系类型
INSERT INTO party_relationship_type (relationship_type, description, from_role_type, to_role_type) VALUES
('CUSTOMER_RELATIONSHIP', '客户关系', 'CUSTOMER', 'INTERNAL_ORGANIZATION'),
('EMPLOYMENT', '雇佣关系', 'EMPLOYEE', 'INTERNAL_ORGANIZATION'),
('ORGANIZATION_ROLLUP', '组织层级关系', 'SUBSIDIARY', 'PARENT_ORGANIZATION'),
('SUPPLIER_RELATIONSHIP', '供应商关系', 'SUPPLIER', 'INTERNAL_ORGANIZATION'),
('AGENT_RELATIONSHIP', '代理关系', 'AGENT', 'INTERNAL_ORGANIZATION'),
('MENTORING_RELATIONSHIP', '导师关系', 'MENTOR', 'APPRENTICE'),
('PARENT_CHILD_RELATIONSHIP', '父子关系', 'PARENT', 'CHILD');

-- Party Relationship Information（关系信息）
CREATE TABLE party_relationship_info (
    party_relationship_id INT NOT NULL REFERENCES party_relationship(party_relationship_id),
    priority_type VARCHAR(20),  -- Very High, High, Medium, Low
    status_type VARCHAR(20),    -- Active, Inactive, Pursuing
    notes TEXT,
    last_contact_date TIMESTAMPTZ,
    PRIMARY KEY (party_relationship_id)
);

-- Status Type（状态类型）
CREATE TABLE status_type (
    status_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    applies_to VARCHAR(50)  -- PARTY_RELATIONSHIP, ORDER, SHIPMENT, etc.
);

INSERT INTO status_type (status_type, description, applies_to) VALUES
('ACTIVE', '活跃', 'PARTY_RELATIONSHIP'),
('INACTIVE', '非活跃', 'PARTY_RELATIONSHIP'),
('PURSuing', '追求更多参与', 'PARTY_RELATIONSHIP');

-- Priority Type（优先级类型）
CREATE TABLE priority_type (
    priority_type VARCHAR(20) PRIMARY KEY,
    description TEXT,
    priority_order INT
);

INSERT INTO priority_type (priority_type, description, priority_order) VALUES
('VERY_HIGH', '非常高', 1),
('HIGH', '高', 2),
('MEDIUM', '中', 3),
('LOW', '低', 4);

-- 示例：Customer Relationship（基于Volume 1 Table 2.5）
-- ACME Company是ABC Subsidiary的客户
INSERT INTO party_relationship (
    party_id_from, party_type_from, party_role_id_from,
    party_id_to, party_type_to, party_role_id_to,
    relationship_type, valid_from
) VALUES (
    700, 'O', (SELECT party_role_id FROM party_role WHERE party_id = 700 AND role_type = 'CUSTOMER'),
    200, 'O', (SELECT party_role_id FROM party_role WHERE party_id = 200 AND role_type = 'INTERNAL_ORGANIZATION'),
    'CUSTOMER_RELATIONSHIP', '1999-01-01'::TIMESTAMPTZ
);

-- 示例：Employment Relationship（基于Volume 1 Table 2.6）
-- John Smith是ABC Subsidiary的员工
INSERT INTO party_relationship (
    party_id_from, party_type_from, party_role_id_from,
    party_id_to, party_type_to, party_role_id_to,
    relationship_type, valid_from, valid_to
) VALUES (
    5000, 'P', (SELECT party_role_id FROM party_role WHERE party_id = 5000 AND role_type = 'EMPLOYEE'),
    200, 'O', (SELECT party_role_id FROM party_role WHERE party_id = 200 AND role_type = 'INTERNAL_ORGANIZATION'),
    'EMPLOYMENT', '1989-12-31'::TIMESTAMPTZ, '1999-12-01'::TIMESTAMPTZ
);

-- 查询：获取某组织的所有客户关系
SELECT
    p_from.name AS customer_name,
    p_to.name AS internal_org_name,
    pr.relationship_type,
    pr.valid_from,
    pr.valid_to,
    pri.status_type,
    pri.priority_type
FROM party_relationship pr
JOIN party p_from ON pr.party_id_from = p_from.party_id AND pr.party_type_from = p_from.party_type
JOIN party p_to ON pr.party_id_to = p_to.party_id AND pr.party_type_to = p_to.party_type
LEFT JOIN party_relationship_info pri ON pr.party_relationship_id = pri.party_relationship_id
WHERE pr.relationship_type = 'CUSTOMER_RELATIONSHIP'
  AND pr.party_id_to = 200  -- ABC Subsidiary
  AND (pr.valid_to IS NULL OR pr.valid_to > NOW());
```

**Volume 1示例数据 / Volume 1 Example Data**:

根据Volume 1 Table 2.5-2.7，Party Relationship数据示例：

| Relationship Type | From Party | From Role | To Party | To Role | Status | Priority |
|------------------|------------|-----------|----------|---------|--------|----------|
| Customer relationship | ACME Company | Customer | ABC Subsidiary | Internal organization | Active | High |
| Employment | John Smith | Employee | ABC Subsidiary | Employer | - | - |
| Organization rollup | ABC Subsidiary | Subsidiary | ABC Corporation | Parent corporation | - | - |

---

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

## 6. 完整PostgreSQL实现 / Complete PostgreSQL Implementation

### 6.1 完整DDL脚本 / Complete DDL Script

基于Volume 1 Chapter 2的完整PostgreSQL实现：

```sql
-- ============================================
-- Party Model Complete DDL
-- Based on Volume 1 Chapter 2: People and Organizations
-- ============================================

-- 1. Party基础表
CREATE TABLE party (
    party_id SERIAL,
    party_type CHAR(1) NOT NULL CHECK (party_type IN ('P', 'O')),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (party_id, party_type)
) PARTITION BY LIST (party_type);

-- Person分区
CREATE TABLE person PARTITION OF party
    FOR VALUES IN ('P');

-- Organization分区
CREATE TABLE organization PARTITION OF party
    FOR VALUES IN ('O');

-- 添加Person特定字段
ALTER TABLE person ADD COLUMN first_name VARCHAR(50);
ALTER TABLE person ADD COLUMN last_name VARCHAR(50);
ALTER TABLE person ADD COLUMN middle_name VARCHAR(50);
ALTER TABLE person ADD COLUMN birth_date DATE;
ALTER TABLE person ADD COLUMN gender CHAR(1) CHECK (gender IN ('M', 'F', 'O', 'U'));

-- 添加Organization特定字段
ALTER TABLE organization ADD COLUMN legal_name VARCHAR(200);
ALTER TABLE organization ADD COLUMN tax_id VARCHAR(50);
ALTER TABLE organization ADD COLUMN founded_date DATE;
ALTER TABLE organization ADD COLUMN organization_type VARCHAR(50);

-- 2. Party Classification（分类）
CREATE TABLE party_classification (
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    classification_type VARCHAR(50) NOT NULL,
    classification_value VARCHAR(100),
    valid_from DATE NOT NULL,
    valid_to DATE,
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type) ON DELETE CASCADE,
    PRIMARY KEY (party_id, party_type, classification_type, valid_from)
);

CREATE TABLE party_classification_type (
    classification_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    applies_to CHAR(1) CHECK (applies_to IN ('P', 'O', 'B'))
);

-- 3. Party Role（角色）
CREATE TABLE party_role (
    party_role_id SERIAL PRIMARY KEY,
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    role_type VARCHAR(50) NOT NULL,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type) ON DELETE CASCADE
);

CREATE TABLE party_role_type (
    role_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    role_category VARCHAR(20) CHECK (role_category IN ('PERSON', 'ORGANIZATION', 'COMMON'))
);

-- 4. Party Relationship（关系）
CREATE TABLE party_relationship (
    party_relationship_id SERIAL PRIMARY KEY,
    party_id_from INT NOT NULL,
    party_type_from CHAR(1) NOT NULL,
    party_role_id_from INT NOT NULL,
    party_id_to INT NOT NULL,
    party_type_to CHAR(1) NOT NULL,
    party_role_id_to INT NOT NULL,
    relationship_type VARCHAR(50) NOT NULL,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id_from, party_type_from) REFERENCES party(party_id, party_type) ON DELETE CASCADE,
    FOREIGN KEY (party_id_to, party_type_to) REFERENCES party(party_id, party_type) ON DELETE CASCADE,
    FOREIGN KEY (party_role_id_from) REFERENCES party_role(party_role_id) ON DELETE CASCADE,
    FOREIGN KEY (party_role_id_to) REFERENCES party_role(party_role_id) ON DELETE CASCADE,
    CHECK (party_id_from != party_id_to OR party_type_from != party_type_to)
);

CREATE TABLE party_relationship_type (
    relationship_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    from_role_type VARCHAR(50) NOT NULL,
    to_role_type VARCHAR(50) NOT NULL
);

CREATE TABLE party_relationship_info (
    party_relationship_id INT PRIMARY KEY REFERENCES party_relationship(party_relationship_id) ON DELETE CASCADE,
    priority_type VARCHAR(20),
    status_type VARCHAR(20),
    notes TEXT,
    last_contact_date TIMESTAMPTZ
);

-- 5. Postal Address（邮政地址）
CREATE TABLE postal_address (
    postal_address_id SERIAL PRIMARY KEY,
    address1 TEXT NOT NULL,
    address2 TEXT,
    directions TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE party_postal_address (
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    postal_address_id INT NOT NULL REFERENCES postal_address(postal_address_id) ON DELETE CASCADE,
    address_purpose VARCHAR(50),
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type) ON DELETE CASCADE,
    PRIMARY KEY (party_id, party_type, postal_address_id, valid_from)
);

CREATE TABLE geographic_boundary (
    geographic_boundary_id SERIAL PRIMARY KEY,
    boundary_type VARCHAR(50) NOT NULL,
    boundary_name VARCHAR(200) NOT NULL,
    boundary_code VARCHAR(50),
    parent_boundary_id INT REFERENCES geographic_boundary(geographic_boundary_id),
    UNIQUE(boundary_type, boundary_code)
);

CREATE TABLE postal_address_boundary (
    postal_address_id INT NOT NULL REFERENCES postal_address(postal_address_id) ON DELETE CASCADE,
    geographic_boundary_id INT NOT NULL REFERENCES geographic_boundary(geographic_boundary_id) ON DELETE CASCADE,
    boundary_role VARCHAR(50),
    PRIMARY KEY (postal_address_id, geographic_boundary_id, boundary_role)
);

-- 6. Contact Mechanism（联系方式）
CREATE TABLE contact_mechanism (
    contact_mechanism_id SERIAL PRIMARY KEY,
    contact_mechanism_type VARCHAR(50) NOT NULL,
    contact_value TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE contact_mechanism_type (
    contact_mechanism_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    mechanism_category VARCHAR(20) CHECK (mechanism_category IN ('POSTAL', 'TELECOMMUNICATIONS', 'ELECTRONIC'))
);

CREATE TABLE telecommunications_number (
    contact_mechanism_id INT PRIMARY KEY REFERENCES contact_mechanism(contact_mechanism_id) ON DELETE CASCADE,
    country_code VARCHAR(10),
    area_code VARCHAR(10),
    phone_number VARCHAR(20) NOT NULL,
    extension VARCHAR(10)
);

CREATE TABLE electronic_address (
    contact_mechanism_id INT PRIMARY KEY REFERENCES contact_mechanism(contact_mechanism_id) ON DELETE CASCADE,
    email_address VARCHAR(255),
    web_url VARCHAR(500),
    internet_address VARCHAR(500)
);

CREATE TABLE party_contact_mechanism (
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    contact_mechanism_id INT NOT NULL REFERENCES contact_mechanism(contact_mechanism_id) ON DELETE CASCADE,
    non_solicitation_ind BOOLEAN DEFAULT FALSE,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type) ON DELETE CASCADE,
    PRIMARY KEY (party_id, party_type, contact_mechanism_id, valid_from)
);

CREATE TABLE contact_mechanism_purpose (
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    contact_mechanism_id INT NOT NULL,
    purpose_type VARCHAR(50) NOT NULL,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id, party_type, contact_mechanism_id, valid_from)
        REFERENCES party_contact_mechanism(party_id, party_type, contact_mechanism_id, valid_from) ON DELETE CASCADE,
    PRIMARY KEY (party_id, party_type, contact_mechanism_id, purpose_type, valid_from)
);

CREATE TABLE contact_mechanism_purpose_type (
    purpose_type VARCHAR(50) PRIMARY KEY,
    description TEXT
);

-- 7. Communication Event（通信事件）
CREATE TABLE communication_event (
    communication_event_id SERIAL PRIMARY KEY,
    party_relationship_id INT REFERENCES party_relationship(party_relationship_id) ON DELETE SET NULL,
    contact_mechanism_type VARCHAR(50) NOT NULL,
    datetime_started TIMESTAMPTZ NOT NULL,
    datetime_ended TIMESTAMPTZ,
    notes TEXT,
    status_type VARCHAR(50) DEFAULT 'SCHEDULED'
);

CREATE TABLE communication_event_role (
    communication_event_id INT NOT NULL REFERENCES communication_event(communication_event_id) ON DELETE CASCADE,
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    role_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type) ON DELETE CASCADE,
    PRIMARY KEY (communication_event_id, party_id, party_type, role_type)
);

CREATE TABLE communication_event_purpose (
    communication_event_id INT NOT NULL REFERENCES communication_event(communication_event_id) ON DELETE CASCADE,
    purpose_type VARCHAR(50) NOT NULL,
    description TEXT,
    PRIMARY KEY (communication_event_id, purpose_type)
);

CREATE TABLE communication_event_purpose_type (
    purpose_type VARCHAR(50) PRIMARY KEY,
    description TEXT
);

CREATE TABLE communication_event_status_type (
    status_type VARCHAR(50) PRIMARY KEY,
    description TEXT
);

-- 8. Case（案例）
CREATE TABLE case_entity (
    case_id SERIAL PRIMARY KEY,
    case_description TEXT NOT NULL,
    opened_date TIMESTAMPTZ DEFAULT NOW(),
    closed_date TIMESTAMPTZ
);

CREATE TABLE case_role (
    case_id INT NOT NULL REFERENCES case_entity(case_id) ON DELETE CASCADE,
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    role_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type) ON DELETE CASCADE,
    PRIMARY KEY (case_id, party_id, party_type, role_type)
);

CREATE TABLE communication_event_case (
    communication_event_id INT NOT NULL REFERENCES communication_event(communication_event_id) ON DELETE CASCADE,
    case_id INT NOT NULL REFERENCES case_entity(case_id) ON DELETE CASCADE,
    PRIMARY KEY (communication_event_id, case_id)
);
```

---

### 6.2 索引设计 / Index Design

```sql
-- Party表索引
CREATE INDEX idx_party_name ON party(name);
CREATE INDEX idx_party_type ON party(party_type);
CREATE INDEX idx_party_created_at ON party(created_at);

-- Party Role索引
CREATE INDEX idx_party_role_party ON party_role(party_id, party_type);
CREATE INDEX idx_party_role_type ON party_role(role_type);
CREATE INDEX idx_party_role_valid ON party_role(valid_from, valid_to)
    WHERE valid_to IS NULL;

-- Party Relationship索引
CREATE INDEX idx_party_relationship_from ON party_relationship(party_id_from, party_type_from);
CREATE INDEX idx_party_relationship_to ON party_relationship(party_id_to, party_type_to);
CREATE INDEX idx_party_relationship_type ON party_relationship(relationship_type);
CREATE INDEX idx_party_relationship_valid ON party_relationship(valid_from, valid_to)
    WHERE valid_to IS NULL;

-- Postal Address索引
CREATE INDEX idx_postal_address_address1 ON postal_address(address1);
CREATE INDEX idx_party_postal_address_party ON party_postal_address(party_id, party_type);
CREATE INDEX idx_party_postal_address_valid ON party_postal_address(valid_from, valid_to)
    WHERE valid_to IS NULL;

-- Geographic Boundary索引
CREATE INDEX idx_geographic_boundary_type ON geographic_boundary(boundary_type);
CREATE INDEX idx_geographic_boundary_code ON geographic_boundary(boundary_code);
CREATE INDEX idx_geographic_boundary_parent ON geographic_boundary(parent_boundary_id);

-- Contact Mechanism索引
CREATE INDEX idx_contact_mechanism_type ON contact_mechanism(contact_mechanism_type);
CREATE INDEX idx_contact_mechanism_value ON contact_mechanism(contact_value);
CREATE INDEX idx_party_contact_mechanism_party ON party_contact_mechanism(party_id, party_type);
CREATE INDEX idx_party_contact_mechanism_valid ON party_contact_mechanism(valid_from, valid_to)
    WHERE valid_to IS NULL;

-- Communication Event索引
CREATE INDEX idx_communication_event_relationship ON communication_event(party_relationship_id);
CREATE INDEX idx_communication_event_started ON communication_event(datetime_started);
CREATE INDEX idx_communication_event_status ON communication_event(status_type);
CREATE INDEX idx_communication_event_role_party ON communication_event_role(party_id, party_type);

-- 复合索引（用于常见查询）
CREATE INDEX idx_party_role_active ON party_role(party_id, role_type, valid_from, valid_to)
    WHERE valid_to IS NULL;
CREATE INDEX idx_party_relationship_active ON party_relationship(
    party_id_from, party_id_to, relationship_type, valid_from, valid_to
) WHERE valid_to IS NULL;
```

---

### 6.3 约束设计 / Constraint Design

```sql
-- 检查约束
ALTER TABLE party ADD CONSTRAINT chk_party_type CHECK (party_type IN ('P', 'O'));
ALTER TABLE person ADD CONSTRAINT chk_person_gender CHECK (gender IN ('M', 'F', 'O', 'U'));
ALTER TABLE party_relationship ADD CONSTRAINT chk_party_relationship_different
    CHECK (party_id_from != party_id_to OR party_type_from != party_type_to);

-- 唯一约束
ALTER TABLE party_role ADD CONSTRAINT uk_party_role_unique
    UNIQUE(party_id, party_type, role_type, valid_from);
ALTER TABLE party_relationship ADD CONSTRAINT uk_party_relationship_unique
    UNIQUE(party_id_from, party_type_from, party_role_id_from,
           party_id_to, party_type_to, party_role_id_to, relationship_type, valid_from);

-- 外键约束（已在DDL中定义，这里补充级联删除规则）
-- 注意：实际应用中需要根据业务需求调整ON DELETE行为
```

---

### 6.4 视图设计 / View Design

```sql
-- 活跃Party Role视图
CREATE VIEW v_active_party_roles AS
SELECT
    p.party_id,
    p.party_type,
    p.name,
    pr.role_type,
    prt.description AS role_description,
    pr.valid_from,
    pr.valid_to
FROM party p
JOIN party_role pr ON p.party_id = pr.party_id AND p.party_type = pr.party_type
JOIN party_role_type prt ON pr.role_type = prt.role_type
WHERE pr.valid_to IS NULL OR pr.valid_to > NOW();

-- Party完整信息视图
CREATE VIEW v_party_complete AS
SELECT
    p.party_id,
    p.party_type,
    p.name,
    CASE
        WHEN p.party_type = 'P' THEN per.first_name || ' ' || per.last_name
        ELSE org.legal_name
    END AS display_name,
    jsonb_agg(DISTINCT jsonb_build_object(
        'role_type', pr.role_type,
        'description', prt.description
    )) AS roles,
    jsonb_agg(DISTINCT jsonb_build_object(
        'contact_type', cmt.contact_mechanism_type,
        'contact_value', cm.contact_value,
        'purpose', cmpt.purpose_type
    )) FILTER (WHERE cm.contact_mechanism_id IS NOT NULL) AS contact_mechanisms
FROM party p
LEFT JOIN person per ON p.party_id = per.party_id AND p.party_type = 'P'
LEFT JOIN organization org ON p.party_id = org.party_id AND p.party_type = 'O'
LEFT JOIN party_role pr ON p.party_id = pr.party_id AND p.party_type = pr.party_type
LEFT JOIN party_role_type prt ON pr.role_type = prt.role_type
LEFT JOIN party_contact_mechanism pcm ON p.party_id = pcm.party_id AND p.party_type = pcm.party_type
LEFT JOIN contact_mechanism cm ON pcm.contact_mechanism_id = cm.contact_mechanism_id
LEFT JOIN contact_mechanism_type cmt ON cm.contact_mechanism_type = cmt.contact_mechanism_type
LEFT JOIN contact_mechanism_purpose cmp ON pcm.party_id = cmp.party_id
    AND pcm.party_type = cmp.party_type
    AND pcm.contact_mechanism_id = cmp.contact_mechanism_id
LEFT JOIN contact_mechanism_purpose_type cmpt ON cmp.purpose_type = cmpt.purpose_type
WHERE (pr.valid_to IS NULL OR pr.valid_to > NOW())
  AND (pcm.valid_to IS NULL OR pcm.valid_to > NOW())
GROUP BY p.party_id, p.party_type, p.name, per.first_name, per.last_name, org.legal_name;
```

---

## 7. PostgreSQL实现 / PostgreSQL Implementation

### 7.1 继承表实现 / Table Inheritance Implementation

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

## 5. Party Contact Information（参与方联系方式） / Party Contact Information

### 5.1 Postal Address Information（邮政地址信息）

**定义 / Definition**: 邮政地址是联系Party的一种机制，支持多个地址、地址历史跟踪和地理边界关联。

**Volume 1设计 / Volume 1 Design** (Figure 2.8):

- **Postal Address**: 存储地址信息（address1, address2, city等）
- **Party Postal Address**: Party与地址的多对多关系（支持地址历史）
- **Geographic Boundary**: 地理边界（City, State, Country, Postal Code等）

**PostgreSQL实现 / PostgreSQL Implementation**:

```sql
-- Postal Address实体（基于Volume 1 Figure 2.8）
CREATE TABLE postal_address (
    postal_address_id SERIAL PRIMARY KEY,
    address1 TEXT NOT NULL,
    address2 TEXT,
    directions TEXT,  -- 到达该地址的路线说明
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Party Postal Address（Party与地址的多对多关系）
CREATE TABLE party_postal_address (
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    postal_address_id INT NOT NULL REFERENCES postal_address(postal_address_id),
    address_purpose VARCHAR(50),  -- Mailing, Headquarters, Service, Billing
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type),
    PRIMARY KEY (party_id, party_type, postal_address_id, valid_from)
);

-- Geographic Boundary（地理边界）
CREATE TABLE geographic_boundary (
    geographic_boundary_id SERIAL PRIMARY KEY,
    boundary_type VARCHAR(50) NOT NULL,  -- CITY, STATE, COUNTRY, POSTAL_CODE, PROVINCE, TERRITORY
    boundary_name VARCHAR(200) NOT NULL,
    boundary_code VARCHAR(50),  -- 如邮政编码、州代码
    parent_boundary_id INT REFERENCES geographic_boundary(geographic_boundary_id),  -- 递归关系
    UNIQUE(boundary_type, boundary_code)
);

-- Postal Address Boundary（地址与地理边界的关联）
CREATE TABLE postal_address_boundary (
    postal_address_id INT NOT NULL REFERENCES postal_address(postal_address_id),
    geographic_boundary_id INT NOT NULL REFERENCES geographic_boundary(geographic_boundary_id),
    boundary_role VARCHAR(50),  -- CITY, STATE, COUNTRY, POSTAL_CODE
    PRIMARY KEY (postal_address_id, geographic_boundary_id, boundary_role)
);

-- 示例：创建地址
INSERT INTO postal_address (address1, address2, directions) VALUES
('100 Main Street', 'Suite 101', 'Take Highway 95 to Main Street exit, turn right');

INSERT INTO geographic_boundary (boundary_type, boundary_name, boundary_code) VALUES
('CITY', 'New York', 'NYC'),
('STATE', 'New York', 'NY'),
('COUNTRY', 'United States', 'US'),
('POSTAL_CODE', '10001', '10001');

-- 关联地址与地理边界
INSERT INTO postal_address_boundary (postal_address_id, geographic_boundary_id, boundary_role) VALUES
(1, (SELECT geographic_boundary_id FROM geographic_boundary WHERE boundary_code = '10001'), 'POSTAL_CODE'),
(1, (SELECT geographic_boundary_id FROM geographic_boundary WHERE boundary_name = 'New York' AND boundary_type = 'CITY'), 'CITY'),
(1, (SELECT geographic_boundary_id FROM geographic_boundary WHERE boundary_code = 'NY'), 'STATE');

-- 关联Party与地址
INSERT INTO party_postal_address (party_id, party_type, postal_address_id, address_purpose) VALUES
(100, 'O', 1, 'Headquarters'),
(100, 'O', 1, 'Billing');

-- 查询：获取Party的所有地址
SELECT
    p.name,
    pa.address1,
    pa.address2,
    gb_city.boundary_name AS city,
    gb_state.boundary_name AS state,
    gb_country.boundary_name AS country,
    gb_postal.boundary_code AS postal_code,
    ppa.address_purpose,
    ppa.valid_from,
    ppa.valid_to
FROM party p
JOIN party_postal_address ppa ON p.party_id = ppa.party_id AND p.party_type = ppa.party_type
JOIN postal_address pa ON ppa.postal_address_id = pa.postal_address_id
LEFT JOIN postal_address_boundary pab_city ON pa.postal_address_id = pab_city.postal_address_id AND pab_city.boundary_role = 'CITY'
LEFT JOIN geographic_boundary gb_city ON pab_city.geographic_boundary_id = gb_city.geographic_boundary_id
LEFT JOIN postal_address_boundary pab_state ON pa.postal_address_id = pab_state.postal_address_id AND pab_state.boundary_role = 'STATE'
LEFT JOIN geographic_boundary gb_state ON pab_state.geographic_boundary_id = gb_state.geographic_boundary_id
LEFT JOIN postal_address_boundary pab_country ON pa.postal_address_id = pab_country.postal_address_id AND pab_country.boundary_role = 'COUNTRY'
LEFT JOIN geographic_boundary gb_country ON pab_country.geographic_boundary_id = gb_country.geographic_boundary_id
LEFT JOIN postal_address_boundary pab_postal ON pa.postal_address_id = pab_postal.postal_address_id AND pab_postal.boundary_role = 'POSTAL_CODE'
LEFT JOIN geographic_boundary gb_postal ON pab_postal.geographic_boundary_id = gb_postal.geographic_boundary_id
WHERE p.party_id = 100
  AND (ppa.valid_to IS NULL OR ppa.valid_to > NOW());
```

---

---

### 5.2 Party Contact Mechanism（参与方联系方式机制）

**定义 / Definition**: Contact Mechanism是联系Party的机制，包括Postal Address、Telecommunications Number和Electronic Address。

**Volume 1设计 / Volume 1 Design** (Figure 2.9, 2.10):

Contact Mechanism分为三类：

- **Postal Address**: 邮政地址
- **Telecommunications Number**: 电话号码、传真号码、手机号码等
- **Electronic Address**: 电子邮箱、网站URL等

**PostgreSQL实现 / PostgreSQL Implementation**:

```sql
-- Contact Mechanism实体（基于Volume 1 Figure 2.10）
CREATE TABLE contact_mechanism (
    contact_mechanism_id SERIAL PRIMARY KEY,
    contact_mechanism_type VARCHAR(50) NOT NULL,
    contact_value TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contact Mechanism Type（联系方式类型）
CREATE TABLE contact_mechanism_type (
    contact_mechanism_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    mechanism_category VARCHAR(20) CHECK (mechanism_category IN ('POSTAL', 'TELECOMMUNICATIONS', 'ELECTRONIC'))
);

INSERT INTO contact_mechanism_type (contact_mechanism_type, description, mechanism_category) VALUES
('POSTAL_ADDRESS', '邮政地址', 'POSTAL'),
('PHONE', '电话', 'TELECOMMUNICATIONS'),
('FAX', '传真', 'TELECOMMUNICATIONS'),
('MOBILE_PHONE', '手机', 'TELECOMMUNICATIONS'),
('PAGER', '寻呼机', 'TELECOMMUNICATIONS'),
('MODEM', '调制解调器', 'TELECOMMUNICATIONS'),
('EMAIL', '电子邮箱', 'ELECTRONIC'),
('WEB_URL', '网站URL', 'ELECTRONIC'),
('INTERNET_ADDRESS', '互联网地址', 'ELECTRONIC');

-- Telecommunications Number（电信号码）
CREATE TABLE telecommunications_number (
    contact_mechanism_id INT PRIMARY KEY REFERENCES contact_mechanism(contact_mechanism_id),
    country_code VARCHAR(10),
    area_code VARCHAR(10),
    phone_number VARCHAR(20) NOT NULL,
    extension VARCHAR(10)
);

-- Electronic Address（电子地址）
CREATE TABLE electronic_address (
    contact_mechanism_id INT PRIMARY KEY REFERENCES contact_mechanism(contact_mechanism_id),
    email_address VARCHAR(255),
    web_url VARCHAR(500),
    internet_address VARCHAR(500)
);

-- Party Contact Mechanism（Party与联系方式的关联）
CREATE TABLE party_contact_mechanism (
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    contact_mechanism_id INT NOT NULL REFERENCES contact_mechanism(contact_mechanism_id),
    non_solicitation_ind BOOLEAN DEFAULT FALSE,  -- 是否禁止营销
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type),
    PRIMARY KEY (party_id, party_type, contact_mechanism_id, valid_from)
);

-- Contact Mechanism Purpose（联系方式用途）
CREATE TABLE contact_mechanism_purpose (
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    contact_mechanism_id INT NOT NULL,
    purpose_type VARCHAR(50) NOT NULL,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id, party_type, contact_mechanism_id, valid_from)
        REFERENCES party_contact_mechanism(party_id, party_type, contact_mechanism_id, valid_from),
    PRIMARY KEY (party_id, party_type, contact_mechanism_id, purpose_type, valid_from)
);

-- Contact Mechanism Purpose Type（联系方式用途类型）
CREATE TABLE contact_mechanism_purpose_type (
    purpose_type VARCHAR(50) PRIMARY KEY,
    description TEXT
);

INSERT INTO contact_mechanism_purpose_type (purpose_type, description) VALUES
('GENERAL_PHONE', '通用电话'),
('MAIN_OFFICE_NUMBER', '主办公室电话'),
('SECONDARY_FAX', '次要传真'),
('MAIN_HOME_ADDRESS', '主要家庭地址'),
('SUMMER_HOME_ADDRESS', '夏季家庭地址'),
('HEADQUARTERS', '总部'),
('BILLING_INQUIRIES', '账单查询'),
('SALES_OFFICE', '销售办公室'),
('SERVICE_ADDRESS', '服务地址'),
('WORK_EMAIL', '工作邮箱'),
('PERSONAL_EMAIL', '个人邮箱'),
('CENTRAL_INTERNET_ADDRESS', '中央互联网地址');

-- Contact Mechanism Link（联系方式链接）
CREATE TABLE contact_mechanism_link (
    contact_mechanism_id_from INT NOT NULL REFERENCES contact_mechanism(contact_mechanism_id),
    contact_mechanism_id_to INT NOT NULL REFERENCES contact_mechanism(contact_mechanism_id),
    link_type VARCHAR(50),  -- Auto-forward, Backup, etc.
    PRIMARY KEY (contact_mechanism_id_from, contact_mechanism_id_to)
);

-- 示例：创建联系方式（基于Volume 1 Table 2.11）
-- ABC Corporation的联系方式
INSERT INTO contact_mechanism (contact_mechanism_type, contact_value) VALUES
('PHONE', '(212) 234-0958'),
('FAX', '(212) 334-5896'),
('POSTAL_ADDRESS', '100 Main Street');

INSERT INTO telecommunications_number (contact_mechanism_id, area_code, phone_number) VALUES
((SELECT contact_mechanism_id FROM contact_mechanism WHERE contact_value = '(212) 234-0958'), '212', '234-0958');

INSERT INTO party_contact_mechanism (party_id, party_type, contact_mechanism_id) VALUES
(100, 'O', (SELECT contact_mechanism_id FROM contact_mechanism WHERE contact_value = '(212) 234-0958'));

INSERT INTO contact_mechanism_purpose (party_id, party_type, contact_mechanism_id, purpose_type) VALUES
(100, 'O',
 (SELECT contact_mechanism_id FROM contact_mechanism WHERE contact_value = '(212) 234-0958'),
 'GENERAL_PHONE');

-- 查询：获取Party的所有联系方式
SELECT
    p.name,
    cmt.contact_mechanism_type,
    cm.contact_value,
    cmpt.purpose_type,
    pcm.non_solicitation_ind,
    pcm.valid_from,
    pcm.valid_to
FROM party p
JOIN party_contact_mechanism pcm ON p.party_id = pcm.party_id AND p.party_type = pcm.party_type
JOIN contact_mechanism cm ON pcm.contact_mechanism_id = cm.contact_mechanism_id
JOIN contact_mechanism_type cmt ON cm.contact_mechanism_type = cmt.contact_mechanism_type
LEFT JOIN contact_mechanism_purpose cmp ON pcm.party_id = cmp.party_id
    AND pcm.party_type = cmp.party_type
    AND pcm.contact_mechanism_id = cmp.contact_mechanism_id
LEFT JOIN contact_mechanism_purpose_type cmpt ON cmp.purpose_type = cmpt.purpose_type
WHERE p.party_id = 100
  AND (pcm.valid_to IS NULL OR pcm.valid_to > NOW())
  AND (cmp.valid_to IS NULL OR cmp.valid_to > NOW());
```

---

---

### 5.3 Facility Versus Contact Mechanism（设施与联系方式）

**定义 / Definition**: Facility表示物理设施（如仓库、工厂、建筑物），而Contact Mechanism是联系Party的机制。

**Volume 1设计 / Volume 1 Design** (Figure 2.11):

- **Facility**: 物理设施（Warehouse, Plant, Building, Room, Office）
- **Facility Role**: Party在Facility中的角色（使用、租赁、拥有等）
- **Facility Contact Mechanism**: Facility的联系方式

**PostgreSQL实现 / PostgreSQL Implementation**:

```sql
-- Facility实体（基于Volume 1 Figure 2.11）
CREATE TABLE facility (
    facility_id SERIAL PRIMARY KEY,
    facility_type VARCHAR(50) NOT NULL,
    facility_name VARCHAR(200) NOT NULL,
    square_footage NUMERIC(10,2),
    parent_facility_id INT REFERENCES facility(facility_id),  -- 递归关系
    postal_address_id INT REFERENCES postal_address(postal_address_id)
);

-- Facility Type（设施类型）
CREATE TABLE facility_type (
    facility_type VARCHAR(50) PRIMARY KEY,
    description TEXT
);

INSERT INTO facility_type (facility_type, description) VALUES
('WAREHOUSE', '仓库'),
('PLANT', '工厂'),
('BUILDING', '建筑物'),
('ROOM', '房间'),
('OFFICE', '办公室'),
('FLOOR', '楼层');

-- Facility Role（设施角色）
CREATE TABLE facility_role (
    facility_id INT NOT NULL REFERENCES facility(facility_id),
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    role_type VARCHAR(50) NOT NULL,  -- USE, LEASE, RENT, OWN
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type),
    PRIMARY KEY (facility_id, party_id, party_type, role_type, valid_from)
);

-- Facility Contact Mechanism（设施联系方式）
CREATE TABLE facility_contact_mechanism (
    facility_id INT NOT NULL REFERENCES facility(facility_id),
    contact_mechanism_id INT NOT NULL REFERENCES contact_mechanism(contact_mechanism_id),
    PRIMARY KEY (facility_id, contact_mechanism_id)
);

-- 示例：创建设施
INSERT INTO facility (facility_type, facility_name, square_footage, postal_address_id) VALUES
('WAREHOUSE', 'Main Warehouse', 50000.00, 1),
('PLANT', 'Manufacturing Plant A', 100000.00, 1);

-- 关联设施与联系方式
INSERT INTO facility_contact_mechanism (facility_id, contact_mechanism_id) VALUES
(1, (SELECT contact_mechanism_id FROM contact_mechanism WHERE contact_value = '(212) 234-0958'));
```

---

### 5.4 Party Communication Event（参与方通信事件）

**定义 / Definition**: Communication Event记录Party之间的通信历史，如电话、会议、邮件等。

**Volume 1设计 / Volume 1 Design** (Figure 2.12):

- **Communication Event**: 通信事件（电话、会议、邮件等）
- **Communication Event Role**: 参与通信的Party及其角色
- **Communication Event Purpose**: 通信目的（销售跟进、技术支持等）
- **Case**: 将相关通信事件分组为案例

**PostgreSQL实现 / PostgreSQL Implementation**:

```sql
-- Communication Event实体（基于Volume 1 Figure 2.12）
CREATE TABLE communication_event (
    communication_event_id SERIAL PRIMARY KEY,
    party_relationship_id INT REFERENCES party_relationship(party_relationship_id),
    contact_mechanism_type VARCHAR(50) NOT NULL,  -- Phone, Face-to-face, Email, etc.
    datetime_started TIMESTAMPTZ NOT NULL,
    datetime_ended TIMESTAMPTZ,
    notes TEXT,
    status_type VARCHAR(50) DEFAULT 'SCHEDULED'  -- Scheduled, In Progress, Completed
);

-- Communication Event Role（通信事件角色）
CREATE TABLE communication_event_role (
    communication_event_id INT NOT NULL REFERENCES communication_event(communication_event_id),
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    role_type VARCHAR(50) NOT NULL,  -- Caller, Receiver, Facilitator, Participant, Note Taker
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type),
    PRIMARY KEY (communication_event_id, party_id, party_type, role_type)
);

-- Communication Event Purpose（通信事件目的）
CREATE TABLE communication_event_purpose (
    communication_event_id INT NOT NULL REFERENCES communication_event(communication_event_id),
    purpose_type VARCHAR(50) NOT NULL,
    description TEXT,
    PRIMARY KEY (communication_event_id, purpose_type)
);

-- Communication Event Purpose Type（通信事件目的类型）
CREATE TABLE communication_event_purpose_type (
    purpose_type VARCHAR(50) PRIMARY KEY,
    description TEXT
);

INSERT INTO communication_event_purpose_type (purpose_type, description) VALUES
('INITIAL_SALES_CALL', '初始销售电话'),
('SALES_FOLLOW_UP', '销售跟进'),
('CUSTOMER_SERVICE', '客户服务'),
('TECHNICAL_SUPPORT', '技术支持'),
('DEMONSTRATION', '产品演示'),
('MEETING', '会议'),
('CONFERENCE', '会议'),
('SEMINAR', '研讨会'),
('ACTIVITY_REQUEST', '活动请求');

-- Communication Event Status Type（通信事件状态类型）
CREATE TABLE communication_event_status_type (
    status_type VARCHAR(50) PRIMARY KEY,
    description TEXT
);

INSERT INTO communication_event_status_type (status_type, description) VALUES
('SCHEDULED', '已安排'),
('IN_PROGRESS', '进行中'),
('COMPLETED', '已完成'),
('CANCELLED', '已取消'),
('PENDING_RESOLUTION', '待解决');

-- Case（案例）
CREATE TABLE case_entity (
    case_id SERIAL PRIMARY KEY,
    case_description TEXT NOT NULL,
    opened_date TIMESTAMPTZ DEFAULT NOW(),
    closed_date TIMESTAMPTZ
);

-- Case Role（案例角色）
CREATE TABLE case_role (
    case_id INT NOT NULL REFERENCES case_entity(case_id),
    party_id INT NOT NULL,
    party_type CHAR(1) NOT NULL,
    role_type VARCHAR(50) NOT NULL,  -- Resolution Lead, Case Customer, Quality Assurance Manager
    FOREIGN KEY (party_id, party_type) REFERENCES party(party_id, party_type),
    PRIMARY KEY (case_id, party_id, party_type, role_type)
);

-- Communication Event Case（通信事件与案例的关联）
CREATE TABLE communication_event_case (
    communication_event_id INT NOT NULL REFERENCES communication_event(communication_event_id),
    case_id INT NOT NULL REFERENCES case_entity(case_id),
    PRIMARY KEY (communication_event_id, case_id)
);

-- Work Effort（工作努力，将在Chapter 6详细说明）
CREATE TABLE work_effort (
    work_effort_id SERIAL PRIMARY KEY,
    work_effort_type VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(50)
);

-- Communication Event Work Effort（通信事件与工作努力的关联）
CREATE TABLE communication_event_work_effort (
    communication_event_id INT NOT NULL REFERENCES communication_event(communication_event_id),
    work_effort_id INT NOT NULL REFERENCES work_effort(work_effort_id),
    PRIMARY KEY (communication_event_id, work_effort_id)
);

-- 示例：创建通信事件（基于Volume 1 Table 2.12）
-- William Jones给Marc Martinez的销售电话
INSERT INTO communication_event (
    party_relationship_id,
    contact_mechanism_type,
    datetime_started,
    datetime_ended,
    notes,
    status_type
) VALUES (
    (SELECT party_relationship_id FROM party_relationship
     WHERE party_id_from = 5400 AND party_id_to = 5300
     LIMIT 1),
    'FACE_TO_FACE',
    '2001-01-12 15:00:00'::TIMESTAMPTZ,
    '2001-01-12 16:00:00'::TIMESTAMPTZ,
    'Initial sales call went well and customer seemed interested',
    'COMPLETED'
);

INSERT INTO communication_event_role (communication_event_id, party_id, party_type, role_type) VALUES
((SELECT communication_event_id FROM communication_event ORDER BY communication_event_id DESC LIMIT 1),
 5400, 'P', 'CALLER'),
((SELECT communication_event_id FROM communication_event ORDER BY communication_event_id DESC LIMIT 1),
 5300, 'P', 'RECEIVER');

INSERT INTO communication_event_purpose (communication_event_id, purpose_type) VALUES
((SELECT communication_event_id FROM communication_event ORDER BY communication_event_id DESC LIMIT 1),
 'INITIAL_SALES_CALL'),
((SELECT communication_event_id FROM communication_event ORDER BY communication_event_id DESC LIMIT 1),
 'INITIAL_PRODUCT_DEMONSTRATION');

-- 查询：获取Party的所有通信事件
SELECT
    ce.communication_event_id,
    ce.datetime_started,
    ce.contact_mechanism_type,
    cept.purpose_type,
    cest.status_type,
    ce.notes,
    p_from.name AS from_party,
    p_to.name AS to_party
FROM communication_event ce
LEFT JOIN party_relationship pr ON ce.party_relationship_id = pr.party_relationship_id
LEFT JOIN party p_from ON pr.party_id_from = p_from.party_id AND pr.party_type_from = p_from.party_type
LEFT JOIN party p_to ON pr.party_id_to = p_to.party_id AND pr.party_type_to = p_to.party_type
LEFT JOIN communication_event_purpose cep ON ce.communication_event_id = cep.communication_event_id
LEFT JOIN communication_event_purpose_type cept ON cep.purpose_type = cept.purpose_type
LEFT JOIN communication_event_status_type cest ON ce.status_type = cest.status_type
WHERE pr.party_id_from = 5400 OR pr.party_id_to = 5400
ORDER BY ce.datetime_started DESC;
```

**Volume 1示例数据 / Volume 1 Example Data**:

根据Volume 1 Table 2.12-2.13，Communication Event数据示例：

| Event ID | From Party | To Party | Purpose | Contact Type | Status |
|----------|-----------|----------|---------|--------------|--------|
| 1010 | William Jones | Marc Martinez | Initial sales call, Product demonstration | Face to face | Completed |
| 3010 | John Smith | Nancy Barry | Purchasing follow-up | Email | Completed |

---

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
