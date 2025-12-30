# 11. 迁移指南

> **章节编号**: 11
> **章节标题**: 迁移指南
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 11. 迁移指南

## 📑 目录

- [11. 迁移指南](#11-迁移指南)
  - [11. 迁移指南](#11-迁移指南-1)
  - [📑 目录](#-目录)
    - [11.1 从PostgreSQL 17迁移到18](#111-从postgresql-17迁移到18)
    - [11.2 启用异步I/O配置](#112-启用异步io配置)
    - [11.3 性能对比测试](#113-性能对比测试)
    - [11.4 回滚方案](#114-回滚方案)
    - [11.5 迁移检查清单](#115-迁移检查清单)
    - [11.6 迁移后优化](#116-迁移后优化)
    - [11.7 常见迁移问题](#117-常见迁移问题)

---

---

### 11.1 从PostgreSQL 17迁移到18

从PostgreSQL 17升级到PostgreSQL 18并启用异步I/O需要遵循标准的升级流程。

**升级前准备**:

1. **备份数据**: 完整备份当前数据库
2. **检查兼容性**: 确认应用兼容PostgreSQL 18
3. **测试环境**: 在测试环境先行验证

**升级步骤**:

```bash
# 1. 停止PostgreSQL服务
sudo systemctl stop postgresql

# 2. 备份数据目录
sudo cp -r /var/lib/postgresql/17/main /var/lib/postgresql/17/main.backup

# 3. 使用pg_upgrade升级
sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade \
    --old-datadir=/var/lib/postgresql/17/main \
    --new-datadir=/var/lib/postgresql/18/main \
    --old-bindir=/usr/lib/postgresql/17/bin \
    --new-bindir=/usr/lib/postgresql/18/bin \
    --check

# 4. 执行实际升级
sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade \
    --old-datadir=/var/lib/postgresql/17/main \
    --new-datadir=/var/lib/postgresql/18/main \
    --old-bindir=/usr/lib/postgresql/17/bin \
    --new-bindir=/usr/lib/postgresql/18/bin
```

**升级后验证**:

```sql
-- 检查PostgreSQL版本
SELECT version();

-- 检查数据库完整性
SELECT * FROM pg_database WHERE datname = 'your_database';
```

### 11.2 启用异步I/O配置

升级到PostgreSQL 18后，需要配置异步I/O参数以启用异步I/O功能。

**基本配置**:

```sql
-- 启用Direct I/O
ALTER SYSTEM SET io_direct = 'data,wal';

-- 配置I/O并发数
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET maintenance_io_concurrency = 200;
ALTER SYSTEM SET wal_io_concurrency = 200;

-- 配置io_uring队列深度
ALTER SYSTEM SET io_uring_queue_depth = 256;

-- 重新加载配置
SELECT pg_reload_conf();
```

**验证配置**:

```sql
-- 检查配置是否生效
SELECT name, setting, unit
FROM pg_settings
WHERE name IN (
    'io_direct',
    'effective_io_concurrency',
    'wal_io_concurrency',
    'io_uring_queue_depth'
);
```

### 11.3 性能对比测试

升级后需要进行性能对比测试，验证异步I/O带来的性能提升。

**测试脚本**:

```sql
-- 创建测试表
CREATE TABLE performance_test (
    id BIGSERIAL PRIMARY KEY,
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 性能测试：批量插入
\timing on
INSERT INTO performance_test (data)
SELECT jsonb_build_object(
    'key', generate_series(1, 10000),
    'value', md5(random()::text)
);
\timing off

-- 查询性能测试
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM performance_test
WHERE data->>'key' = '5000';
```

**性能对比指标**:

| 指标 | PostgreSQL 17 | PostgreSQL 18 | 提升 |
|------|--------------|---------------|------|
| **批量写入TPS** | 基准 | +170% | 2.7倍 |
| **查询响应时间** | 基准 | -60% | 显著降低 |
| **CPU利用率** | 35% | 80% | +128% |

### 11.4 回滚方案

如果升级后出现问题，需要准备回滚方案。

**回滚步骤**:

```bash
# 1. 停止PostgreSQL 18
sudo systemctl stop postgresql

# 2. 恢复PostgreSQL 17数据目录
sudo rm -rf /var/lib/postgresql/17/main
sudo cp -r /var/lib/postgresql/17/main.backup /var/lib/postgresql/17/main

# 3. 启动PostgreSQL 17
sudo systemctl start postgresql@17-main

# 4. 验证数据库
sudo -u postgres psql -c "SELECT version();"
```

**回滚注意事项**:

- **数据一致性**: 确保回滚后数据完整
- **配置恢复**: 恢复PostgreSQL 17的配置参数
- **应用兼容**: 确认应用仍兼容PostgreSQL 17

### 11.5 迁移检查清单

**迁移前检查**：

```sql
-- 1. 检查PostgreSQL版本
SELECT version();

-- 2. 检查系统要求
SELECT
    name,
    setting,
    CASE
        WHEN name = 'io_direct' AND setting != 'off' THEN '✅ 支持'
        WHEN name = 'effective_io_concurrency' AND setting::int >= 200 THEN '✅ 已配置'
        ELSE '⚠️ 需配置'
    END AS status
FROM pg_settings
WHERE name IN ('io_direct', 'effective_io_concurrency', 'wal_io_concurrency');

-- 3. 检查扩展兼容性
SELECT
    extname,
    extversion,
    CASE
        WHEN extname IN ('pgvector', 'postgis', 'timescaledb') THEN '✅ 兼容'
        ELSE '⚠️ 需验证'
    END AS compatibility
FROM pg_extension
ORDER BY extname;
```

**迁移步骤检查清单**：

```text
□ 备份数据库
□ 检查应用兼容性
□ 在测试环境验证
□ 准备回滚方案
□ 执行升级
□ 验证数据库完整性
□ 启用异步I/O配置
□ 性能测试
□ 监控运行状态
```

### 11.6 迁移后优化

**优化步骤**：

```sql
-- 1. 更新统计信息
ANALYZE;

-- 2. 重建索引（如果需要）
REINDEX DATABASE your_database;

-- 3. 优化配置参数
ALTER SYSTEM SET effective_io_concurrency = 300;
ALTER SYSTEM SET wal_io_concurrency = 300;
ALTER SYSTEM SET io_uring_queue_depth = 512;

-- 4. 重新加载配置
SELECT pg_reload_conf();

-- 5. 验证配置
SELECT name, setting, unit
FROM pg_settings
WHERE name IN (
    'io_direct',
    'effective_io_concurrency',
    'wal_io_concurrency',
    'io_uring_queue_depth'
);
```

**性能验证**：

```sql
-- 创建性能基准表
CREATE TABLE IF NOT EXISTS migration_performance_log (
    id SERIAL PRIMARY KEY,
    test_name TEXT,
    pg_version TEXT,
    tps NUMERIC,
    avg_latency_ms NUMERIC,
    test_time TIMESTAMPTZ DEFAULT NOW()
);

-- 记录性能测试结果
INSERT INTO migration_performance_log (test_name, pg_version, tps, avg_latency_ms)
VALUES
('批量写入', 'PostgreSQL 18', 5400, 37);

-- 对比性能提升
SELECT
    test_name,
    pg_version,
    tps,
    avg_latency_ms,
    ROUND((tps / LAG(tps) OVER (PARTITION BY test_name ORDER BY test_time) - 1) * 100, 1) AS improvement_pct
FROM migration_performance_log
ORDER BY test_name, test_time;
```

### 11.7 常见迁移问题

**问题1: 升级后性能未提升**

**原因分析**：

- 异步I/O未正确启用
- 配置参数未优化
- 系统资源不足

**解决方案**：

```sql
-- 检查异步I/O状态
SELECT
    name,
    setting,
    CASE
        WHEN name = 'io_direct' AND setting != 'off' THEN '✅ 已启用'
        ELSE '❌ 未启用'
    END AS status
FROM pg_settings
WHERE name = 'io_direct';

-- 检查I/O性能
SELECT
    context,
    SUM(reads + writes) AS total_io,
    SUM(io_wait_time) AS wait_time
FROM pg_stat_io
WHERE context = 'async'
GROUP BY context;
```

**问题2: 升级后出现兼容性问题**

**原因分析**：

- 扩展版本不兼容
- SQL语法变化
- 配置参数变化

**解决方案**：

```sql
-- 检查扩展版本
SELECT
    extname,
    extversion,
    pg_catalog.pg_get_extension_ddl(extname) AS ddl
FROM pg_extension
WHERE extname IN ('pgvector', 'postgis', 'timescaledb');

-- 更新扩展版本
ALTER EXTENSION pgvector UPDATE;
```

**问题3: 升级后WAL增长过快**

**原因分析**：

- wal_level设置过高
- 未启用WAL压缩
- 复制配置不当

**解决方案**：

```sql
-- 检查WAL配置
SELECT name, setting
FROM pg_settings
WHERE name IN ('wal_level', 'wal_compression', 'max_wal_size');

-- 优化WAL配置
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET wal_compression = on;
ALTER SYSTEM SET max_wal_size = '4GB';
```

---

**返回**: [文档首页](../README.md) | [上一章节](../10-监控和诊断/README.md) | [下一章节](../12-性能调优检查清单/README.md)
