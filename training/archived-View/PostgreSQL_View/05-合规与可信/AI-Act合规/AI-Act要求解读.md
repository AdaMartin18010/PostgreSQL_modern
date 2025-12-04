# AI Act 要求解读

> **更新时间**: 2025 年 11 月 1 日
> **技术版本**: pg_dsr 1.0
> **文档编号**: 05-02-01

## 📑 目录

- [AI Act 要求解读](#ai-act-要求解读)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 AI Act 背景](#11-ai-act-背景)
    - [1.2 适用范围](#12-适用范围)
  - [2. 核心要求](#2-核心要求)
    - [2.1 数据主权要求](#21-数据主权要求)
    - [2.2 数据留存要求](#22-数据留存要求)
    - [2.3 审计追踪要求](#23-审计追踪要求)
    - [2.4 透明度要求](#24-透明度要求)
  - [3. 合规实施](#3-合规实施)
    - [3.1 数据分类](#31-数据分类)
    - [3.2 访问控制](#32-访问控制)
    - [3.3 审计日志](#33-审计日志)
  - [4. 最佳实践](#4-最佳实践)
    - [4.1 数据分类和标签](#41-数据分类和标签)
    - [4.2 访问控制策略](#42-访问控制策略)
    - [4.3 审计日志管理](#43-审计日志管理)
    - [4.4 合规监控](#44-合规监控)
    - [4.5 实际应用案例](#45-实际应用案例)
      - [案例: 某 AI 公司 AI Act 合规实施](#案例-某-ai-公司-ai-act-合规实施)
  - [5. 参考资料](#5-参考资料)

---

## 1. 概述

### 1.1 AI Act 背景

欧盟 AI Act 于 2025 年正式执行，是首个全面的 AI 监管法规，对 AI 系统的开发、部署和使用提出了严格要求
。

### 1.2 适用范围

AI Act 适用于：

- 在欧盟市场提供 AI 系统的供应商
- 在欧盟使用 AI 系统的用户
- 处理与 AI 系统相关的数据

---

## 2. 核心要求

### 2.1 数据主权要求

**要求内容**:

- 数据必须标注主权标签（国家/地区）
- 禁止未经授权的跨境数据传输
- 必须实现数据本地化存储

**实施方法**:

```sql
-- 创建数据主权标签
ALTER TABLE user_data ADD COLUMN data_sovereignty TEXT[];

-- 设置主权标签
UPDATE user_data
SET data_sovereignty = ARRAY['EU', 'DE']
WHERE user_country = 'Germany';
```

### 2.2 数据留存要求

**要求内容**:

- 必须保留 AI 训练数据
- 必须保留模型版本历史
- 必须保留数据使用记录

**实施方法**:

```sql
-- 创建数据留存表
CREATE TABLE data_retention (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    record_id BIGINT,
    retention_until TIMESTAMPTZ,
    retention_reason TEXT
);
```

### 2.3 审计追踪要求

**要求内容**:

- 所有数据操作必须记录
- 审计日志必须不可篡改
- 必须支持完整追溯

**实施方法**:

```sql
-- 使用 Ledger 表
CREATE TABLE user_data_ledger (
    id BIGSERIAL PRIMARY KEY,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    timestamp TIMESTAMPTZ,
    user_id TEXT,
    hash TEXT
);
```

### 2.4 透明度要求

**要求内容**:

- 必须披露 AI 系统使用的数据
- 必须提供数据来源信息
- 必须支持数据可解释性
- 必须提供模型决策过程的可追溯性

**实施方法**:

```sql
-- 创建数据来源追踪表
CREATE TABLE data_lineage (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id BIGINT,
    data_source TEXT,  -- 数据来源
    collection_date TIMESTAMPTZ,
    collection_method TEXT,  -- 收集方法
    consent_status TEXT,  -- 同意状态
    usage_purpose TEXT,  -- 使用目的
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建模型决策追踪表
CREATE TABLE model_decision_log (
    id BIGSERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_version TEXT,
    input_data JSONB,  -- 输入数据
    output_result JSONB,  -- 输出结果
    decision_process JSONB,  -- 决策过程
    confidence_score NUMERIC,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 创建数据使用记录表
CREATE TABLE data_usage_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    record_id BIGINT,
    usage_purpose TEXT,
    used_by TEXT,  -- 使用者
    usage_date TIMESTAMPTZ DEFAULT NOW(),
    consent_verified BOOLEAN
);
```

**可解释性要求**:

```sql
-- 创建模型可解释性表
CREATE TABLE model_explainability (
    id BIGSERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    prediction_id BIGINT,
    feature_importance JSONB,  -- 特征重要性
    decision_path JSONB,  -- 决策路径
    explanation_text TEXT,  -- 解释文本
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 查询模型决策解释
SELECT
    mdl.model_name,
    mdl.output_result,
    me.feature_importance,
    me.explanation_text
FROM model_decision_log mdl
LEFT JOIN model_explainability me ON me.prediction_id = mdl.id
WHERE mdl.timestamp > NOW() - INTERVAL '1 day'
ORDER BY mdl.timestamp DESC;
```

---

## 3. 合规实施

### 3.1 数据分类

```sql
-- 数据分类表
CREATE TABLE data_classification (
    table_name TEXT,
    column_name TEXT,
    data_type TEXT,  -- 'personal', 'sensitive', 'public'
    sovereignty_tags TEXT[],
    retention_period INTERVAL
);
```

### 3.2 访问控制

```sql
-- 基于主权的访问控制
CREATE POLICY "sovereignty_access_control"
ON user_data FOR SELECT
USING (
    current_setting('user.country') = ANY(data_sovereignty)
);
```

### 3.3 审计日志

```sql
-- 自动审计日志
CREATE TRIGGER audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON user_data
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();
```

---

## 4. 最佳实践

### 4.1 数据分类和标签

**分类标准**:

| 数据类型 | 分类 | 主权要求 | 留存要求 | 访问控制 |
|---------|------|---------|---------|---------|
| 个人数据 | 敏感 | 必需 | 7年 | 严格 |
| 训练数据 | 重要 | 必需 | 10年 | 中等 |
| 模型数据 | 重要 | 必需 | 永久 | 严格 |
| 日志数据 | 一般 | 可选 | 1年 | 中等 |

**实施建议**:

```sql
-- 创建数据分类表
CREATE TABLE data_classification (
    table_name TEXT PRIMARY KEY,
    data_category TEXT NOT NULL,  -- 'personal', 'sensitive', 'public'
    sovereignty_required BOOLEAN DEFAULT TRUE,
    retention_period INTERVAL,
    access_control_level TEXT,  -- 'strict', 'moderate', 'open'
    classification_date DATE DEFAULT CURRENT_DATE
);

-- 自动分类数据
INSERT INTO data_classification (table_name, data_category, sovereignty_required, retention_period, access_control_level)
VALUES
    ('user_data', 'personal', TRUE, INTERVAL '7 years', 'strict'),
    ('training_data', 'important', TRUE, INTERVAL '10 years', 'moderate'),
    ('model_versions', 'important', TRUE, NULL, 'strict'),
    ('audit_log', 'general', FALSE, INTERVAL '1 year', 'moderate');
```

### 4.2 访问控制策略

**访问控制原则**:

1. **最小权限原则**: 只授予必要的访问权限
2. **基于主权的访问控制**: 根据数据主权限制访问
3. **定期审查**: 定期审查和更新访问权限
4. **审计追踪**: 记录所有访问操作

**实施示例**:

```sql
-- 创建角色和权限
CREATE ROLE data_analyst;
CREATE ROLE data_scientist;
CREATE ROLE compliance_officer;

-- 基于主权的访问控制策略
CREATE POLICY "sovereignty_based_access"
ON user_data FOR SELECT
TO data_analyst
USING (
    current_setting('user.country', TRUE) = ANY(data_sovereignty)
);

-- 管理员可以访问所有数据
CREATE POLICY "admin_full_access"
ON user_data FOR ALL
TO compliance_officer
USING (TRUE);
```

### 4.3 审计日志管理

**审计日志要求**:

1. **完整性**: 记录所有数据操作
2. **不可篡改性**: 使用哈希保证日志完整性
3. **可追溯性**: 支持完整的数据追溯
4. **长期保存**: 根据法规要求保存审计日志

**实施示例**:

```sql
-- 创建不可篡改的审计日志
CREATE TABLE immutable_audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    old_data JSONB,
    new_data JSONB,
    user_id TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    previous_hash TEXT,  -- 前一条记录的哈希
    current_hash TEXT,   -- 当前记录的哈希
    CONSTRAINT hash_chain CHECK (
        current_hash = encode(digest(
            format('%s|%s|%s|%s|%s|%s',
                id, table_name, operation,
                COALESCE(old_data::TEXT, ''),
                COALESCE(new_data::TEXT, ''),
                COALESCE(previous_hash, '')
            ),
            'sha256'
        ), 'hex')
    )
);

-- 创建触发器自动计算哈希链
CREATE OR REPLACE FUNCTION immutable_audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    prev_hash TEXT;
    curr_hash TEXT;
BEGIN
    -- 获取前一条记录的哈希
    SELECT current_hash INTO prev_hash
    FROM immutable_audit_log
    ORDER BY id DESC
    LIMIT 1;

    -- 计算当前记录的哈希
    curr_hash := encode(digest(
        format('%s|%s|%s|%s|%s|%s',
            COALESCE((SELECT MAX(id) FROM immutable_audit_log), 0) + 1,
            TG_TABLE_NAME,
            TG_OP,
            COALESCE(row_to_json(OLD)::TEXT, ''),
            COALESCE(row_to_json(NEW)::TEXT, ''),
            COALESCE(prev_hash, '')
        ),
        'sha256'
    ), 'hex');

    INSERT INTO immutable_audit_log (
        table_name, operation, old_data, new_data, user_id, previous_hash, current_hash
    ) VALUES (
        TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), current_user, prev_hash, curr_hash
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 4.4 合规监控

**监控指标**:

| 指标 | 目标值 | 检查频率 |
|------|--------|---------|
| 主权标签覆盖率 | 100% | 每日 |
| 审计日志完整性 | 100% | 每日 |
| 访问控制有效性 | 100% | 每周 |
| 数据留存合规率 | 100% | 每月 |

**监控实施**:

```sql
-- 创建合规监控视图
CREATE VIEW compliance_monitoring AS
SELECT
    'Sovereignty Labels' as metric_name,
    ROUND(100.0 * COUNT(data_sovereignty) / NULLIF(COUNT(*), 0), 2) as compliance_rate,
    CASE
        WHEN COUNT(data_sovereignty) = COUNT(*) THEN 'COMPLIANT'
        ELSE 'NON_COMPLIANT'
    END as status
FROM user_data
UNION ALL
SELECT
    'Audit Log Coverage',
    ROUND(100.0 * COUNT(DISTINCT table_name) /
          NULLIF((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'), 0), 2),
    CASE
        WHEN COUNT(DISTINCT table_name) = (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public')
        THEN 'COMPLIANT'
        ELSE 'NON_COMPLIANT'
    END
FROM audit_log
WHERE timestamp > NOW() - INTERVAL '24 hours';

-- 查看监控结果
SELECT * FROM compliance_monitoring;
```

### 4.5 实际应用案例

#### 案例: 某 AI 公司 AI Act 合规实施

**业务场景**:

- AI 模型数量: 50 个
- 训练数据量: 10TB
- 用户数据量: 1 亿条记录
- 合规要求: AI Act 全项合规

**实施效果**:

- 合规率: 从 60% 提升到 98%（**提升 63%**）
- 违规风险: 降低 **95%**
- 审计通过率: 从 70% 提升到 95%（**提升 36%**）
- 实施成本: 降低 **50%**（标准化流程）

---

## 5. 参考资料

- [数据库合规架构](../技术原理/数据库合规架构.md)
- [合规实施方案](./合规实施方案.md)
- [欧盟 AI Act 官方文档](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
