# PostgreSQL SQL脚本执行指南

本指南提供了PostgreSQL SQL脚本集合的详细执行说明，包括环境准备、脚本执行、验证和故障排除。

## 📋 目录

1. [环境准备](#环境准备)
2. [脚本执行](#脚本执行)
3. [验证测试](#验证测试)
4. [故障排除](#故障排除)
5. [最佳实践](#最佳实践)
6. [监控和维护](#监控和维护)

## 🛠️ 环境准备

### 系统要求

- **操作系统**: Linux, macOS, Windows
- **PostgreSQL版本**: 12+ (推荐 15+)
- **内存**: 最少 2GB RAM
- **磁盘空间**: 最少 1GB 可用空间
- **权限**: 超级用户权限（部分功能需要）

### 安装PostgreSQL

#### Ubuntu/Debian
```bash
# 更新包列表
sudo apt update

# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### CentOS/RHEL
```bash
# 安装PostgreSQL
sudo yum install postgresql-server postgresql-contrib

# 初始化数据库
sudo postgresql-setup initdb

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS (Homebrew)
```bash
# 安装PostgreSQL
brew install postgresql

# 启动服务
brew services start postgresql
```

#### Windows
1. 下载PostgreSQL安装程序
2. 运行安装程序并按照提示操作
3. 确保在安装过程中设置密码

### 扩展安装

#### pgvector扩展
```bash
# Ubuntu/Debian
sudo apt install postgresql-15-pgvector

# CentOS/RHEL
sudo yum install pgvector_15

# 从源码编译
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

#### Apache AGE扩展
```bash
# 从源码编译
git clone https://github.com/apache/age.git
cd age
make install
```

#### pgaudit扩展
```bash
# Ubuntu/Debian
sudo apt install postgresql-15-pgaudit

# 从源码编译
git clone https://github.com/pgaudit/pgaudit.git
cd pgaudit
make install
```

### 数据库配置

#### 1. 连接数据库
```bash
# 切换到postgres用户
sudo -u postgres psql

# 或者直接连接
psql -h localhost -U postgres -d postgres
```

#### 2. 创建测试数据库
```sql
-- 创建测试数据库
CREATE DATABASE sql_scripts_test;

-- 连接到测试数据库
\c sql_scripts_test;
```

#### 3. 安装扩展
```sql
-- 安装基础扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 安装pgvector（如果可用）
CREATE EXTENSION IF NOT EXISTS vector;

-- 安装Apache AGE（如果可用）
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';

-- 安装pgaudit（如果可用）
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- 安装pgcrypto（如果可用）
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

#### 4. 配置参数
```sql
-- 检查当前配置
SELECT name, setting, unit, context, short_desc
FROM pg_settings 
WHERE name IN (
    'shared_buffers',
    'work_mem',
    'maintenance_work_mem',
    'effective_cache_size',
    'random_page_cost',
    'effective_io_concurrency'
);

-- 设置推荐配置（需要重启）
-- 编辑postgresql.conf文件
-- shared_buffers = 256MB
-- work_mem = 4MB
-- maintenance_work_mem = 64MB
-- effective_cache_size = 1GB
-- random_page_cost = 1.1
-- effective_io_concurrency = 200
```

## 🚀 脚本执行

### 执行前检查

#### 1. 运行验证脚本
```bash
# 执行验证脚本
psql -h localhost -U postgres -d sql_scripts_test -f validate_scripts.sql
```

#### 2. 检查环境
```sql
-- 检查PostgreSQL版本
SELECT version();

-- 检查扩展
SELECT extname, extversion FROM pg_extension;

-- 检查权限
SELECT current_user, session_user;
```

### 脚本执行顺序

#### 1. 基础脚本
```bash
# 1. 诊断脚本
psql -h localhost -U postgres -d sql_scripts_test -f diagnostics.sql

# 2. 调优示例
psql -h localhost -U postgres -d sql_scripts_test -f tuning_examples.sql
```

#### 2. 高级功能脚本
```bash
# 3. 向量检索（需要pgvector）
psql -h localhost -U postgres -d sql_scripts_test -f vector_examples.sql

# 4. 图数据库（需要Apache AGE）
psql -h localhost -U postgres -d sql_scripts_test -f graph_examples.sql
```

#### 3. 监控和安全脚本
```bash
# 5. 高可用监控
psql -h localhost -U postgres -d sql_scripts_test -f ha_monitoring.sql

# 6. 安全示例（需要相关扩展）
psql -h localhost -U postgres -d sql_scripts_test -f security_examples.sql
```

#### 4. 新特性测试
```bash
# 7. EXPLAIN扩展功能
psql -h localhost -U postgres -d sql_scripts_test -f feature_tests/explain_memory.sql

# 8. JSON_TABLE功能
psql -h localhost -U postgres -d sql_scripts_test -f feature_tests/json_table.sql

# 9. MERGE RETURNING功能
psql -h localhost -U postgres -d sql_scripts_test -f feature_tests/merge_returning.sql
```

### 批量执行

#### 创建执行脚本
```bash
#!/bin/bash
# execute_all_scripts.sh

DB_HOST="localhost"
DB_USER="postgres"
DB_NAME="sql_scripts_test"
SCRIPT_DIR="."

echo "Starting PostgreSQL SQL Scripts Execution..."

# 执行验证脚本
echo "1. Running validation script..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $SCRIPT_DIR/validate_scripts.sql

# 执行主要脚本
echo "2. Running diagnostics script..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $SCRIPT_DIR/diagnostics.sql

echo "3. Running tuning examples..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $SCRIPT_DIR/tuning_examples.sql

echo "4. Running vector examples..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $SCRIPT_DIR/vector_examples.sql

echo "5. Running graph examples..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $SCRIPT_DIR/graph_examples.sql

echo "6. Running HA monitoring..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $SCRIPT_DIR/ha_monitoring.sql

echo "7. Running security examples..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $SCRIPT_DIR/security_examples.sql

echo "All scripts executed successfully!"
```

#### 执行批量脚本
```bash
# 使脚本可执行
chmod +x execute_all_scripts.sh

# 执行脚本
./execute_all_scripts.sh
```

## ✅ 验证测试

### 功能验证

#### 1. 诊断功能验证
```sql
-- 验证会话监控
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- 验证锁监控
SELECT count(*) FROM pg_locks WHERE NOT granted;

-- 验证表统计
SELECT count(*) FROM pg_stat_user_tables;
```

#### 2. 调优功能验证
```sql
-- 验证统计信息
SELECT count(*) FROM pg_statistics;

-- 验证索引
SELECT count(*) FROM pg_indexes WHERE schemaname = 'public';
```

#### 3. 向量功能验证
```sql
-- 验证向量表
SELECT count(*) FROM information_schema.tables 
WHERE table_name LIKE '%vector%' OR table_name LIKE '%embedding%';

-- 验证向量索引
SELECT count(*) FROM pg_indexes 
WHERE indexdef LIKE '%hnsw%' OR indexdef LIKE '%ivfflat%';
```

#### 4. 图数据库功能验证
```sql
-- 验证图创建
SELECT count(*) FROM ag_graph;

-- 验证节点创建
SELECT count(*) FROM ag_label;
```

### 性能验证

#### 1. 查询性能测试
```sql
-- 测试基础查询性能
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- 测试复杂查询性能
EXPLAIN (ANALYZE, BUFFERS) 
SELECT schemaname, relname, seq_scan, idx_scan
FROM pg_stat_user_tables 
ORDER BY (seq_scan + idx_scan) DESC;
```

#### 2. 索引性能测试
```sql
-- 测试索引使用
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM pg_stat_user_indexes 
WHERE idx_scan > 0 
ORDER BY idx_scan DESC;
```

## 🔧 故障排除

### 常见问题

#### 1. 扩展安装失败
```bash
# 检查PostgreSQL版本
psql -c "SELECT version();"

# 检查扩展可用性
psql -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"

# 手动安装扩展
sudo apt install postgresql-15-pgvector
```

#### 2. 权限不足
```sql
-- 检查当前用户权限
SELECT current_user, session_user;

-- 检查数据库权限
SELECT has_database_privilege(current_database(), 'CREATE');

-- 切换到超级用户
\c postgres postgres
```

#### 3. 内存不足
```sql
-- 检查内存配置
SELECT name, setting, unit 
FROM pg_settings 
WHERE name IN ('shared_buffers', 'work_mem', 'maintenance_work_mem');

-- 调整内存配置
-- 编辑postgresql.conf
-- shared_buffers = 128MB
-- work_mem = 2MB
-- maintenance_work_mem = 32MB
```

#### 4. 磁盘空间不足
```bash
# 检查磁盘空间
df -h

# 清理WAL文件
psql -c "SELECT pg_switch_wal();"

# 清理临时文件
psql -c "VACUUM FULL;"
```

### 错误日志检查

#### 1. 查看PostgreSQL日志
```bash
# Ubuntu/Debian
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# CentOS/RHEL
sudo tail -f /var/lib/pgsql/data/log/postgresql-*.log

# macOS
tail -f /usr/local/var/log/postgres.log
```

#### 2. 检查系统日志
```bash
# 查看系统日志
sudo journalctl -u postgresql -f

# 查看错误日志
sudo journalctl -u postgresql --since "1 hour ago" | grep ERROR
```

## 📚 最佳实践

### 执行前准备

1. **备份数据库**
```bash
# 创建备份
pg_dump -h localhost -U postgres sql_scripts_test > backup_$(date +%Y%m%d_%H%M%S).sql
```

2. **测试环境验证**
```sql
-- 在测试环境中执行所有脚本
-- 验证功能正常后再在生产环境使用
```

3. **权限检查**
```sql
-- 确保有足够的权限执行脚本
SELECT current_user, session_user;
```

### 执行过程中

1. **监控资源使用**
```sql
-- 监控连接数
SELECT count(*) FROM pg_stat_activity;

-- 监控锁等待
SELECT count(*) FROM pg_locks WHERE NOT granted;

-- 监控磁盘使用
SELECT pg_size_pretty(pg_database_size(current_database()));
```

2. **错误处理**
```sql
-- 启用错误停止
\set ON_ERROR_STOP on

-- 使用事务
BEGIN;
-- 执行脚本
COMMIT;
```

### 执行后验证

1. **功能验证**
```sql
-- 验证所有功能正常工作
-- 检查数据完整性
-- 验证性能指标
```

2. **清理工作**
```sql
-- 清理测试数据
DROP SCHEMA IF EXISTS sandbox CASCADE;

-- 清理临时对象
DROP TABLE IF EXISTS temp_test_table;
```

## 📊 监控和维护

### 性能监控

#### 1. 创建监控视图
```sql
-- 创建性能监控视图
CREATE OR REPLACE VIEW performance_monitor AS
SELECT 
    'Active Connections' as metric,
    count(*)::text as value
FROM pg_stat_activity 
WHERE state = 'active'
UNION ALL
SELECT 
    'Lock Waits' as metric,
    count(*)::text as value
FROM pg_locks 
WHERE NOT granted
UNION ALL
SELECT 
    'Database Size' as metric,
    pg_size_pretty(pg_database_size(current_database())) as value;
```

#### 2. 定期监控
```sql
-- 查看性能指标
SELECT * FROM performance_monitor;

-- 查看慢查询
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

### 维护任务

#### 1. 定期维护
```sql
-- 更新统计信息
ANALYZE;

-- 清理死元组
VACUUM;

-- 重建索引
REINDEX DATABASE sql_scripts_test;
```

#### 2. 监控脚本
```bash
#!/bin/bash
# monitor_scripts.sh

# 检查数据库连接
psql -h localhost -U postgres -d sql_scripts_test -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Database connection: OK"
else
    echo "Database connection: FAILED"
fi

# 检查扩展状态
psql -h localhost -U postgres -d sql_scripts_test -c "SELECT extname FROM pg_extension;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Extensions: OK"
else
    echo "Extensions: FAILED"
fi

# 检查磁盘空间
df -h | grep -E "(Filesystem|/dev/)"
```

## 🔗 相关资源

- [PostgreSQL官方文档](https://www.postgresql.org/docs/)
- [pgvector扩展文档](https://github.com/pgvector/pgvector)
- [Apache AGE文档](https://age.apache.org/)
- [pgaudit扩展文档](https://github.com/pgaudit/pgaudit)
- [PostgreSQL性能调优指南](https://wiki.postgresql.org/wiki/Performance_Optimization)

## 📞 支持

如果您在执行过程中遇到问题，请：

1. 检查本文档的故障排除部分
2. 查看PostgreSQL官方文档
3. 检查相关扩展的文档
4. 在相关社区论坛寻求帮助

---

**注意**: 本指南基于PostgreSQL 15编写，其他版本可能需要调整。请根据您的具体环境进行相应的修改。
