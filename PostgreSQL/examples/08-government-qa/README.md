# 政务智能问答示例

> **PostgreSQL版本**: 18 ⭐ | 17  
> **pgvector版本**: 2.0 ⭐ | 0.7+  
> **最后更新**: 2025-11-11

---

## 📋 示例说明

本示例展示如何构建政务智能问答系统，使用PostgreSQL存储政务知识库，实现语义检索，并包含数据脱敏和审计日志功能。

**核心特性**：
- ✅ 政务知识库检索
- ✅ 向量+全文混合搜索
- ✅ 数据脱敏（基于角色权限）
- ✅ 审计日志记录

**适用场景**：
- 政务智能问答
- 政策咨询系统
- 公共服务平台
- 合规审计场景

---

## 🚀 快速开始

### 1. 启动服务

```bash
docker-compose up -d
```

### 2. 连接到数据库

```bash
docker-compose exec postgres psql -U postgres -d government_qa
```

### 3. 执行智能问答（普通用户）

```sql
-- 普通用户查询（敏感信息会被脱敏）
SELECT * FROM government_qa(
    '社保缴费',  -- 查询文本
    '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(1536),  -- 查询向量
    'public',  -- 用户角色：public（普通用户）
    5  -- 返回top 5结果
);
```

### 4. 执行智能问答（管理员）

```sql
-- 管理员查询（可以查看敏感信息）
SELECT * FROM government_qa(
    '数据安全',
    '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(1536),
    'admin',  -- 用户角色：admin（管理员）
    5
);
```

### 5. 查看审计日志

```sql
-- 查看过去24小时的审计日志
SELECT * FROM view_audit_log(
    now() - INTERVAL '24 hours',
    now()
);
```

### 6. 查看所有知识

```sql
SELECT id, title, category, department, is_sensitive, created_at
FROM government_knowledge
ORDER BY created_at DESC;
```

### 7. 停止服务

```bash
docker-compose down
```

---

## 🔒 权限控制说明

### 用户角色

- **public**：普通用户，不能查看敏感信息
- **staff**：工作人员，可以查看部分敏感信息
- **admin**：管理员，可以查看所有信息

### 数据脱敏

敏感信息（`is_sensitive = true`）对普通用户会显示为 `[敏感信息，需要授权查看]`。

---

## 📊 架构说明

```text
┌─────────────────────────────────────────┐
│        政务服务平台                       │
│  - 智能问答接口                           │
│  - 权限管理                               │
│  - 审计日志                               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      PostgreSQL 18 + pgvector            │
│  - 政务知识库表                           │
│  - 向量索引（HNSW）                      │
│  - 全文索引（GIN）                       │
│  - 智能问答函数（带权限控制）             │
│  - 审计日志表                             │
└─────────────────────────────────────────┘
```

---

## 🔧 实际使用流程

### 1. 知识入库

```sql
-- 添加政务知识
INSERT INTO government_knowledge (title, content, category, department, is_sensitive, embedding)
VALUES (
    '新政策标题',
    '政策内容...',
    'policy',
    '部门名称',
    false,  -- 是否敏感
    '[生成的1536维向量]'::vector(1536)
);
```

### 2. 用户查询

```python
# Python示例：用户查询
import psycopg2

def query_government_qa(query_text, query_vector, user_role='public'):
    conn = psycopg2.connect("dbname=government_qa user=postgres")
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM government_qa(%s, %s, %s, 5)
    """, (query_text, query_vector, user_role))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return results
```

### 3. 审计追踪

```sql
-- 查看特定用户的查询记录
SELECT * FROM audit_log
WHERE user_id = 'user123'
ORDER BY created_at DESC
LIMIT 100;
```

---

## 📚 相关文档

- [AI 时代专题 - 合规与可信](../../05-前沿技术/AI-时代/05-合规与可信-AI Act与审计.md)
- [落地案例 - 政务社保大数据](../../05-前沿技术/AI-时代/06-落地案例-2025精选.md#案例-5政务社保大数据行列混存--脱敏)
- [RAG架构实战指南](../../05-前沿技术/05.04-RAG架构实战指南.md)

---

## 🔧 扩展建议

### 1. 行级安全（RLS）

使用PostgreSQL的行级安全策略：

```sql
-- 启用RLS
ALTER TABLE government_knowledge ENABLE ROW LEVEL SECURITY;

-- 创建策略：普通用户不能查看敏感信息
CREATE POLICY gov_knowledge_policy ON government_knowledge
    FOR SELECT
    USING (
        NOT is_sensitive OR 
        current_setting('app.user_role') IN ('staff', 'admin')
    );
```

### 2. 数据脱敏函数

更细粒度的脱敏控制：

```sql
CREATE OR REPLACE FUNCTION mask_sensitive_content(
    content text,
    user_role text
)
RETURNS text AS $$
BEGIN
    IF user_role NOT IN ('staff', 'admin') THEN
        -- 脱敏处理：替换敏感关键词
        RETURN regexp_replace(content, 
            '(身份证|手机号|银行卡)', 
            '[已脱敏]', 
            'gi'
        );
    END IF;
    RETURN content;
END;
$$ LANGUAGE plpgsql;
```

### 3. 合规报告

生成合规审计报告：

```sql
-- 生成审计报告
CREATE OR REPLACE FUNCTION generate_audit_report(
    p_start_date date,
    p_end_date date
)
RETURNS TABLE (
    action text,
    action_count bigint,
    unique_users bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.action,
        COUNT(*) AS action_count,
        COUNT(DISTINCT al.user_id) AS unique_users
    FROM audit_log al
    WHERE al.created_at::date BETWEEN p_start_date AND p_end_date
    GROUP BY al.action
    ORDER BY action_count DESC;
END;
$$ LANGUAGE plpgsql;
```

---

**最后更新**：2025-11-11

