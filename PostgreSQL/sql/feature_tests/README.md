# Feature Tests (PostgreSQL 17.x)

占位目录：存放 17.x 新特性的示例与回归 SQL。

建议命名：

- json_table.sql
- merge_returning.sql
- logical_rep_setup.sql
- explain_memory.sql
-- 安全相关
- security_rls.sql
- security_audit.sql
- security_crypto.sql

用法建议：

```text
# 本地数据库
psql -h 127.0.0.1 -U postgres -d postgres -f json_table.sql

# 指定 search_path 与事务
psql -v ON_ERROR_STOP=1 -c "SET search_path TO public;" -f merge_returning.sql

# 查看 EXPLAIN MEMORY 扩展示例
psql -f explain_memory.sql

# 逻辑复制示意（需按环境修改连接串后执行）
psql -f logical_rep_setup.sql

# 安全特性（示例）
psql -f security_rls.sql
psql -f security_audit.sql
psql -f security_crypto.sql
```
