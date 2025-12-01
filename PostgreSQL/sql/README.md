# PostgreSQL SQL 脚本集合

本目录包含PostgreSQL数据库的完整SQL脚本集合，涵盖诊断、调优、高级功能、监控和安全等各个方面。

## 📁 文件结构

### 主要SQL脚本

- **diagnostics.sql** - 常用诊断查询（会话、锁、I/O、慢查询等）
- **tuning_examples.sql** - 性能调优示例（索引、统计、查询优化）
- **vector_examples.sql** - 向量与混合检索示例（pgvector扩展）
- **graph_examples.sql** - 图与递归查询示例（Apache AGE扩展）
- **ha_monitoring.sql** - 复制与高可用监控
- **security_examples.sql** - 安全与合规示例（RLS/审计/加密/GDPR/SOX/PCI）

### 新特性测试 (feature_tests/)

- **explain_memory.sql** - PostgreSQL 17.x EXPLAIN扩展功能测试
- **json_table.sql** - SQL/JSON JSON_TABLE功能测试
- **merge_returning.sql** - MERGE RETURNING功能测试
- **logical_rep_setup.sql** - 逻辑复制设置示例
- **security_audit.sql** - 审计功能测试
- **security_crypto.sql** - 加密功能测试
- **security_rls.sql** - 行级安全测试

## 🚀 快速开始

### 环境要求

- PostgreSQL 12+ （推荐 PostgreSQL 15+）
- 超级用户权限（部分功能需要）
- 相关扩展：pgvector, age, pgaudit, pgcrypto

### 基础执行

```bash
# 连接数据库
psql -h localhost -U postgres -d postgres

# 执行诊断脚本
\i diagnostics.sql

# 执行调优示例
\i tuning_examples.sql
```

## 📋 详细使用指南

### 1. 诊断脚本 (diagnostics.sql)

**用途**：日常运维诊断、性能分析、故障排查

**主要功能**：

- 会话与连接诊断
- 锁与等待分析
- 表与索引使用统计
- I/O性能分析
- 慢查询分析
- 数据库大小统计
- 配置参数检查

**执行示例**：

```sql
-- 检查活跃会话
SELECT pid, usename, application_name, state, query
FROM pg_stat_activity WHERE state <> 'idle';

-- 分析锁等待
SELECT locktype, relation::regclass, mode, granted, pid
FROM pg_locks WHERE NOT granted;
```

### 2. 调优示例 (tuning_examples.sql)

**用途**：性能优化、索引调优、统计信息管理

**主要功能**：

- 统计信息优化
- 索引优化策略
- 查询优化技巧
- 锁与等待优化
- 表维护与优化
- 配置参数调优
- 查询计划分析

**执行示例**：

```sql
-- 创建扩展统计
CREATE STATISTICS stats_multi_deps (dependencies) 
ON customer_id, order_date, product_category 
FROM orders;

-- 创建表达式索引
CREATE INDEX CONCURRENTLY idx_users_lower_email 
ON users (lower(email));
```

### 3. 向量检索 (vector_examples.sql)

**用途**：向量相似性搜索、混合检索、AI应用集成

**前置条件**：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**主要功能**：

- 基础向量表设计
- 向量索引创建（HNSW, IVFFlat）
- 基础向量搜索
- 混合检索策略
- 推荐系统应用
- 向量搜索优化

**执行示例**：

```sql
-- 创建向量表
CREATE TABLE documents (
    id bigserial PRIMARY KEY,
    title text NOT NULL,
    embedding vector(768)
);

-- 创建HNSW索引
CREATE INDEX idx_documents_hnsw 
ON documents USING hnsw (embedding vector_l2_ops) 
WITH (m = 32, ef_construction = 200);
```

### 4. 图数据库 (graph_examples.sql)

**用途**：图数据库查询、递归关系分析、社交网络分析

**前置条件**：

```sql
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
```

**主要功能**：

- 图数据库基础操作
- 基础图查询
- 路径查询
- 聚合查询
- 复杂图分析
- 递归CTE图查询
- 图算法实现

**执行示例**：

```sql
-- 创建图
SELECT * FROM create_graph('social_network');

-- 创建节点
SELECT * FROM cypher('social_network', $$
  CREATE (alice:User {name: 'Alice', age: 25})
$$) as (v agtype);
```

### 5. 高可用监控 (ha_monitoring.sql)

**用途**：复制状态监控、高可用性检查、故障检测

**主要功能**：

- 复制状态监控
- 复制槽管理
- WAL监控
- 冲突监控
- 主从切换监控
- 性能监控
- 告警查询

**执行示例**：

```sql
-- 检查复制状态
SELECT application_name, state, sync_state,
       pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS byte_lag
FROM pg_stat_replication;
```

### 6. 安全示例 (security_examples.sql)

**用途**：安全与合规实现（RLS/审计/加密/GDPR/SOX/PCI）

**前置条件**：

```sql
CREATE EXTENSION IF NOT EXISTS pgaudit;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
SELECT set_config('app.encryption_key', 'ReplaceWithStrongKey', false);
```

**主要功能**：

- 审计与监控
- 行级安全（RLS）
- 存储加密
- GDPR合规模块
- SOX审计模块
- PCI DSS支付数据加密

## 🛡️ 安全执行指南

### 沙箱环境准备

```sql
-- 创建沙箱schema
CREATE SCHEMA IF NOT EXISTS sandbox;
SET search_path = sandbox, public;

-- 启用错误停止
\set ON_ERROR_STOP on
```

### 幂等执行模式

```sql
-- 对象创建：使用 IF NOT EXISTS / OR REPLACE
CREATE TABLE IF NOT EXISTS sandbox.events(id bigserial PRIMARY KEY);
CREATE OR REPLACE FUNCTION sandbox.f() RETURNS int LANGUAGE sql AS $$ SELECT 1 $$;

-- 变更/清理：使用 IF EXISTS
DROP MATERIALIZED VIEW IF EXISTS sandbox.mv CASCADE;
```

### 条件式DDL

```sql
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='sandbox' AND c.relname='idx_events_id'
  ) THEN
    EXECUTE 'CREATE INDEX idx_events_id ON sandbox.events(id)';
  END IF;
END$$;
```

## 🔧 自动化执行

### 一键执行脚本

```bash
# 基础诊断
psql -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 -f diagnostics.sql

# 性能调优
psql -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 -f tuning_examples.sql

# 向量检索（需要pgvector扩展）
psql -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 -f vector_examples.sql

# 图数据库（需要Apache AGE扩展）
psql -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 -f graph_examples.sql

# 高可用监控
psql -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 -f ha_monitoring.sql

# 安全示例（需要相关扩展）
psql -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 -f security_examples.sql
```

### 批量执行

```bash
# 执行所有主要脚本
for script in diagnostics.sql tuning_examples.sql vector_examples.sql graph_examples.sql ha_monitoring.sql security_examples.sql; do
    echo "Executing $script..."
    psql -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 -f "$script"
done
```

### 验证脚本

```bash
# 快速验证
psql -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 \
  -c "\\dn+ sandbox" \
  -c "\\dt+ sandbox.*" \
  -c "\\df+ sandbox.*" \
  -c "SELECT to_regclass('sandbox.events') IS NOT NULL AS has_events;"
```

## 🧪 新特性测试

### PostgreSQL 17.x 功能测试

```bash
# EXPLAIN扩展功能
psql -h localhost -U postgres -d postgres -f feature_tests/explain_memory.sql

# JSON_TABLE功能
psql -h localhost -U postgres -d postgres -f feature_tests/json_table.sql

# MERGE RETURNING功能
psql -h localhost -U postgres -d postgres -f feature_tests/merge_returning.sql

# 逻辑复制设置
psql -h localhost -U postgres -d postgres -f feature_tests/logical_rep_setup.sql
```

### 安全功能测试

```bash
# 审计功能
psql -h localhost -U postgres -d postgres -f feature_tests/security_audit.sql

# 加密功能
psql -h localhost -U postgres -d postgres -f feature_tests/security_crypto.sql

# 行级安全
psql -h localhost -U postgres -d postgres -f feature_tests/security_rls.sql
```

## 🧹 清理操作

### 快速回滚

```sql
-- 清理沙箱
DROP SCHEMA IF EXISTS sandbox CASCADE;

-- 清理测试数据
DROP SCHEMA IF EXISTS ft_explain CASCADE;
DROP SCHEMA IF EXISTS ft_json CASCADE;
DROP SCHEMA IF EXISTS ft_merge CASCADE;
DROP SCHEMA IF EXISTS ft_sec CASCADE;
```

### 批量清理

```bash
# 清理所有测试schema
psql -h localhost -U postgres -d postgres -c "
DROP SCHEMA IF EXISTS sandbox CASCADE;
DROP SCHEMA IF EXISTS ft_explain CASCADE;
DROP SCHEMA IF EXISTS ft_json CASCADE;
DROP SCHEMA IF EXISTS ft_merge CASCADE;
DROP SCHEMA IF EXISTS ft_sec CASCADE;
"
```

## ⚠️ 重要注意事项

### 生产环境使用

- **仅在非生产环境验证**，生产环境需结合密钥管理（KMS）
- 遵循变更流程与审计策略
- 备份重要数据
- 测试所有脚本的幂等性

### 扩展依赖

- **pgvector**: 向量检索功能
- **Apache AGE**: 图数据库功能
- **pgaudit**: 审计功能
- **pgcrypto**: 加密功能

### 权限要求

- 超级用户权限（部分功能）
- 创建扩展权限
- 修改配置权限

## 📚 最佳实践

1. **沙箱测试**：始终在沙箱环境中测试
2. **幂等执行**：使用IF NOT EXISTS/IF EXISTS
3. **错误处理**：启用ON_ERROR_STOP
4. **版本兼容**：检查PostgreSQL版本
5. **扩展检查**：验证所需扩展是否安装
6. **性能监控**：使用EXPLAIN分析查询计划
7. **安全审计**：启用相关审计功能
8. **定期维护**：执行VACUUM和ANALYZE

## 🔗 相关资源

- [PostgreSQL官方文档](https://www.postgresql.org/docs/)
- [pgvector扩展](https://github.com/pgvector/pgvector)
- [Apache AGE扩展](https://age.apache.org/)
- [pgaudit扩展](https://github.com/pgaudit/pgaudit)
- [PostgreSQL性能调优指南](https://wiki.postgresql.org/wiki/Performance_Optimization)
