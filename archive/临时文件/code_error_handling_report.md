# 代码示例错误处理补充报告

> **生成日期**: 2025年1月
> **扫描结果**: 找到 346 个需要添加错误处理的代码示例

---

## 📊 统计信息

- **需要处理的代码示例**: 346 个

## 📋 需要处理的代码示例

### 01-AIO异步IO完整深度指南.md

**行 598** (bash):

```bash
# 1. 编辑配置
sudo vi /etc/postgresql/18/main/postgresql.conf

# 2. 重启PostgreSQL
sudo systemctl restart postgresql

# 3. 验证配置
psql -c "SHOW io_direct;"
# 应该输出：data

psql -c "SHOW io_uring_queue_depth;"
#
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 620** (bash):

```bash
# 查看PostgreSQL是否使用io_uring
ps aux | grep postgres
# 找到backend进程PID

# 查看文件描述符
ls -l /proc/<PID>/fd | grep io_uring
# 如果看到io_uring相关的fd，说明AIO已启用

```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 750** (bash):

```bash
# 检查
psql -c "SHOW io_direct;"
# 如果是'off'，需要启用

# 解决
ALTER SYSTEM SET io_direct = 'data';
SELECT pg_reload_conf();
# 或重启
sudo systemctl restart postgresql

```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 02-跳跃扫描Skip-Scan完整指南-改进补充.md

**行 508** (sql):

```sql
-- 完整验证脚本
DO $$
DECLARE
    skip_scan_enabled BOOLEAN;
    cardinality_threshold INTEGER;
    plan_text TEXT;
BEGIN
    -- 检查配置
    SELECT setting::BOOLEAN INTO skip_scan_enabled
    FROM pg_settings

```

**问题**:

- 添加事务错误处理和回滚

---

### 02-跳跃扫描Skip-Scan完整指南.md

**行 310** (sql):

```sql
-- 创建测试表
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    status VARCHAR(20),  -- 5个值
    type VARCHAR(20),     -- 10个值
    amount NUMERIC(10, 2),

    created_at TIMESTAMPTZ
```

**问题**:

- 添加数据操作错误处理

---

### 03-虚拟生成列完整实战指南.md

**行 113** (sql):

```sql
-- 插入100万行
\timing on

-- 虚拟列表
INSERT INTO test_virtual (price, quantity)
SELECT random() * 1000, (random() * 100)::INT
FROM generate_series(1, 1000000);
-- 时间：8.5秒


-- 存储列表
INSERT INTO test_stored (p
```

**问题**:

- 添加数据操作错误处理

---

### 04-UUIDv7完整指南-改进补充.md

**行 161** (sql):

```sql
-- 步骤1: 添加新列
ALTER TABLE orders ADD COLUMN id_v7 UUID;

-- 步骤2: 生成UUIDv7（基于created_at时间）
UPDATE orders
SET id_v7 = gen_uuid_v7_at(created_at)
WHERE id_v7 IS NULL;


-- 步骤3: 创建新索引
CREATE UNIQUE INDEX id
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 185** (sql):

```sql
-- 完整迁移脚本
DO $$
DECLARE
    batch_size INTEGER := 10000;
    total_rows BIGINT;
    processed_rows BIGINT := 0;
BEGIN

    -- 获取总行数
    SELECT COUNT(*) INTO total_rows FROM orders;

    RAISE NOTICE '开
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 247** (sql):

```sql
-- 方案：新数据使用UUIDv7，旧数据保持UUIDv4
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    -- 其他字段
    created_at TIMESTAMPTZ DEFAULT NOW()

);

-- 使用触发器自动选择
CREATE OR REPLACE FUNCTION orders_id_default()
RETURN
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 352** (sql):

```sql
-- 方案1: 使用批量生成
INSERT INTO orders (user_id, amount)
SELECT i, 100.0
FROM generate_series(1, 10000) i;
-- 批量插入性能更好


-- 方案2: 使用连接池
-- 减少连接开销

-- 方案3: 优化系统时间同步
-- 使用NTP同步系统时间

```

**问题**:

- 添加数据操作错误处理

---

**行 486** (sql):

```sql
-- 方法1: 检查生成的UUID格式
SELECT gen_uuid_v7();

-- 应该以018d开头（版本7标识）

-- 方法2: 检查时间戳提取
SELECT
    gen_uuid_v7() AS uuid,
    uuid_extract_time(gen_uuid_v7()) AS timestamp_ms,
    to_timestamp(uuid_extract_tim
```

**问题**:

- 添加数据操作错误处理

---

### 04-UUIDv7完整指南.md

**行 100** (sql):

```sql
-- UUIDv4（随机UUID）

CREATE TABLE users_v4 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- UUIDv4
    name TEXT
);

-- 插入100万行
INSERT INTO users_v4 (name)
SELECT 'User ' || i FROM generate_serie
```

**问题**:

- 添加数据操作错误处理

---

**行 144** (sql):

```sql

-- UUIDv7（时间排序）
CREATE TABLE users_v7 (
    id UUID PRIMARY KEY DEFAULT gen_uuid_v7(),  -- PostgreSQL 18
    name TEXT
);

-- 插入100万行
INSERT INTO users_v7 (name)
SELECT 'User ' || i FROM generate_seri
```

**问题**:

- 添加数据操作错误处理

---

**行 210** (sql):

```sql
-- 测试插入100万行

-- UUIDv4
CREATE TABLE test_v4 (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), data TEXT);
INSERT INTO test_v4 (data) SELECT 'data' FROM generate_series(1, 1000000);
-- 时间：8.5秒
-- 索引大小：4
```

**问题**:

- 添加数据操作错误处理

---

**行 278** (sql):

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_uuid_v7(),
    user_id BIGINT NOT NULL,
    total NUMERIC(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入数据
INSERT INTO orders (use
```

**问题**:

- 添加数据操作错误处理

---

**行 329** (sql):

```sql
-- 生成指定时间的UUIDv7
CREATE OR REPLACE FUNCTION gen_uuid_v7_at(ts timestamptz)
RETURNS uuid AS $$
DECLARE
    unix_ts_ms bigint;
    uuid_bytes bytea;
BEGIN
    unix_ts_ms := (EXTRACT(EPOCH FROM ts) * 100
```

**问题**:

- 添加事务错误处理和回滚

---

**行 416** (sql):

```sql
-- 步骤1：添加UUIDv7列
ALTER TABLE orders ADD COLUMN id_v7 UUID DEFAULT gen_uuid_v7();

-- 步骤2：为现有行生成UUIDv7
UPDATE orders SET id_v7 = gen_uuid_v7() WHERE id_v7 IS NULL;

-- 步骤3：创建索引
CREATE UNIQUE INDEX idx_
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 440** (sql):

```sql
-- 适用于小表（<100万行）

-- 步骤1：创建新表
CREATE TABLE orders_new (LIKE orders INCLUDING ALL);
ALTER TABLE orders_new ALTER COLUMN id SET DEFAULT gen_uuid_v7();

-- 步骤2：复制数据
INSERT INTO orders_new SELECT * FROM o
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 618** (sql):

```sql
-- 步骤1: 添加新列
ALTER TABLE orders ADD COLUMN id_v7 UUID;

-- 步骤2: 生成UUIDv7（基于created_at时间）
UPDATE orders
SET id_v7 = gen_uuid_v7_at(created_at)
WHERE id_v7 IS NULL;

-- 步骤3: 创建新索引
CREATE UNIQUE INDEX id
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 642** (sql):

```sql
-- 完整迁移脚本
DO $$
DECLARE
    batch_size INTEGER := 10000;
    total_rows BIGINT;
    processed_rows BIGINT := 0;
BEGIN
    -- 获取总行数
    SELECT COUNT(*) INTO total_rows FROM orders;

    RAISE NOTICE '开
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 760** (sql):

```sql
-- 方案1: 使用批量生成
INSERT INTO orders (user_id, amount)
SELECT i, 100.0
FROM generate_series(1, 10000) i;
-- 批量插入性能更好

-- 方案2: 使用连接池
-- 减少连接开销

-- 方案3: 优化系统时间同步
-- 使用NTP同步系统时间

```

**问题**:

- 添加数据操作错误处理

---

**行 851** (sql):

```sql
-- 方法1: 检查生成的UUID格式
SELECT gen_uuid_v7();
-- 应该以018d开头（版本7标识）

-- 方法2: 检查时间戳提取
SELECT
    gen_uuid_v7() AS uuid,
    uuid_extract_time(gen_uuid_v7()) AS timestamp_ms,
    to_timestamp(uuid_extract_tim
```

**问题**:

- 添加数据操作错误处理

---

### 06-OAuth2.0认证集成完整指南-改进补充.md

**行 182** (sql):

```sql
-- 方案1: 配置角色映射
ALTER SYSTEM SET oauth_claim_role_mapping = on;
ALTER SYSTEM SET oauth_role_claim = 'groups';  -- 或'roles'
SELECT pg_reload_conf();


-- 方案2: 创建映射角色
CREATE ROLE oauth_user_role;
GRANT CO
```

**问题**:

- 添加连接错误处理

---

**行 248** (sql):

```sql
-- 1. 创建最小权限角色
CREATE ROLE oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oauth_readon
```

**问题**:

- 添加连接错误处理
- 添加数据操作错误处理

---

**行 306** (sql):

```sql
-- 方法1: 检查配置
SHOW oauth_enabled;  -- 应该是 'on'
SHOW oauth_issuer;
SHOW oauth_audience;

-- 方法2: 检查pg_hba.conf
SELECT * FROM pg_hba_file_rules WHERE auth_method = 'oauth';


-- 方法3: 测试连接
-- 使用OAuth Token
```

**问题**:

- 添加连接错误处理

---

### 06-OAuth2.0认证集成完整指南.md

**行 163** (sql):

```sql
-- 创建角色
CREATE ROLE google_users;
GRANT CONNECT ON DATABASE mydb TO google_users;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO google_users;


-- 创建用户（自动从Google email创建）
-- PostgreSQL 18会自动根据token中的e
```

**问题**:

- 添加连接错误处理

---

**行 177** (python):

```python
import psycopg2
from google.oauth2 import id_token
from google.auth.transport import requests


# 获取Google OAuth token
# （假设已通过Google OAuth流程获取）
google_token = get_google_oauth_token()

# 验证token
idinf
```

**问题**:

- 添加try-except错误处理

---

**行 245** (python):

```python

from msal import ConfidentialClientApplication
import psycopg2

# Azure AD配置
authority = f"https://login.microsoftonline.com/{TENANT_ID}"
client_id = "YOUR-CLIENT-ID"
client_secret = "YOUR-CLIENT-SECR
```

**问题**:

- 添加try-except错误处理

---

**行 311** (sql):

```sql
-- 创建受限角色
CREATE ROLE oauth_readonly;

GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oauth_readonly;


```

**问题**:

- 添加连接错误处理

---

**行 388** (sql):

```sql
-- 支持多OAuth Provider
-- postgresql.conf
oauth_enabled = on
oauth_multi_issuer = on  # 允许多个issuer

-- 创建Issuer配置表
CREATE TABLE oauth_issuers (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,

```

**问题**:

- 添加数据操作错误处理

---

**行 563** (sql):

```sql
-- 1. 创建最小权限角色
CREATE ROLE oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oauth_readon
```

**问题**:

- 添加连接错误处理

---

### 07-逻辑复制增强完整指南-改进补充.md

**行 196** (sql):

```sql
-- 方案1: 配置冲突解决策略
ALTER SYSTEM SET logical_replication_conflict_resolution = 'last_write_wins';
SELECT pg_reload_conf();

-- 方案2: 使用自定义冲突处理函数
CREATE FUNCTION resolve_conflict()
RETURNS trigger AS $$
BE
```

**问题**:

- 添加事务错误处理和回滚

---

**行 329** (sql):

```sql

-- 方法1: 检查订阅状态
SELECT * FROM pg_subscription;
-- 应该显示active状态

-- 方法2: 检查复制延迟
SELECT
    subname,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), latest_end_lsn)) AS replication_lag
FROM pg_s
```

**问题**:

- 添加数据操作错误处理

---

### 07-逻辑复制增强完整指南.md

**行 110** (sql):

```sql
-- 创建Publication，启用DDL复制
CREATE PUBLICATION my_pub
FOR ALL TABLES  -- 或指定表
WITH (
    publish = 'insert,update,delete',
    publish_via_partition_root = true,
    ddl_replication = true  -- ⭐ 启用DDL复制

```

**问题**:

- 添加数据操作错误处理

---

**行 179** (sql):

```sql
-- 场景：两端同时插入相同主键
-- Node A:
INSERT INTO users (id, name) VALUES (1, 'Alice');

-- Node B（几乎同时）:
INSERT INTO users (id, name) VALUES (1, 'Bob');

-- 冲突：主键重复

```

**问题**:

- 添加数据操作错误处理

---

**行 192** (sql):

```sql
-- 场景：两端同时更新同一行
-- Node A:
UPDATE users SET name = 'Alice Updated' WHERE id = 1;

-- Node B:
UPDATE users SET name = 'Alice Modified' WHERE id = 1;

-- 冲突：UPDATE冲突

```

**问题**:

- 添加数据操作错误处理

---

**行 205** (sql):

```sql
-- 场景：一端UPDATE，另一端DELETE
-- Node A:
UPDATE users SET name = 'Alice' WHERE id = 1;

-- Node B:
DELETE FROM users WHERE id = 1;

-- 冲突：行不存在

```

**问题**:

- 添加数据操作错误处理

---

**行 236** (sql):

```sql
-- 创建带时间戳的表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 配置使用时间戳解决冲突
ALTER SUBSCRIPTION my_sub
SET (
    conflict_action = 'latest_
```

**问题**:

- 添加数据操作错误处理

---

**行 259** (sql):

```sql
-- 创建冲突处理函数
CREATE OR REPLACE FUNCTION handle_user_conflict()
RETURNS TRIGGER AS $$
BEGIN
    -- 记录冲突
    INSERT INTO conflict_log (table_name, conflict_type, old_data, new_data)
    VALUES (TG_TABLE_
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 08-性能调优实战指南.md

**行 371** (sql):

```sql
-- 范围分区（时序数据）
CREATE TABLE logs (
    log_id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    message TEXT
) PARTITION BY RANGE (timestamp);

-- 创建分区（月度）
CREATE TABLE logs_2023_12 PARTITION OF logs

```

**问题**:

- 添加事务错误处理和回滚

---

**行 420** (sql):

```sql
-- 自动创建分区（使用pg_partman扩展）
CREATE EXTENSION pg_partman;

SELECT partman.create_parent(
    p_parent_table := 'public.logs',
    p_control := 'timestamp',
    p_type := 'native',
    p_interval := 'mont
```

**问题**:

- 添加数据操作错误处理

---

**行 610** (bash):

```bash
# 下载TPC-H工具
git clone https://github.com/Data-Science-Platform/tpch-pgsql.git
cd tpch-pgsql

# 生成数据（10GB）
./dbgen -s 10

# 导入数据
psql -d tpch -f dss.ddl
./load.sh

# 运行查询
for i in {1..22}; do
    echo
```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 09-异步IO深度解析.md

**行 116** (bash):

```bash
# 测试脚本
#!/bin/bash

# 测试off模式
psql -c "ALTER SYSTEM SET io_direct = 'off';"
psql -c "SELECT pg_reload_conf();"
pgbench -i -s 100 test
pgbench -c 50 -j 4 -T 60 test

# 测试data模式
psql -c "ALTER SYSTEM SE
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 252** (bash):

```bash
#!/bin/bash
# OLTP性能测试

DB="oltp_test"

# 配置1: 传统同步I/O
psql -c "ALTER SYSTEM SET io_direct = 'off';" $DB
psql -c "ALTER SYSTEM SET io_method = 'worker';" $DB
psql -c "SELECT pg_reload_conf();" $DB

pg
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 302** (sql):

```sql
-- 创建测试表
CREATE TABLE bulk_test (
    id BIGSERIAL PRIMARY KEY,
    data TEXT,
    ts TIMESTAMPTZ DEFAULT now()
);

-- 批量插入测试
\timing on

-- 配置1: 传统I/O
SET io_direct = 'off';
INSERT INTO bulk_test (da
```

**问题**:

- 添加数据操作错误处理

---

**行 395** (bash):

```bash
#!/bin/bash
# I/O实时监控脚本

while true; do
    clear
    echo "=== PostgreSQL I/O Statistics ==="
    date

    psql -c "
    SELECT
        io_context,
        reads,
        read_time,

        writes,

```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 470** (bash):

```bash
# 1. 备份配置
cp postgresql.conf postgresql.conf.bak

# 2. 测试环境验证
# 在测试库启用异步I/O
psql test -c "ALTER SYSTEM SET io_direct = 'data';"
psql test -c "SELECT pg_reload_conf();"

# 3. 性能基准测试
pgbench -i -s 100 t

```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 09-约束增强完整指南.md

**行 219** (sql):

```sql
-- 创建外键
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE
);

-- 批量删除用户（触发级联）
DELETE FROM users WHERE last_login < '2020-01-01';  -- 删除10万用户

```

**问题**:

- 添加数据操作错误处理

---

### 10-SkipScan深度解析.md

**行 97** (sql):

```sql
-- 创建测试表
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    country VARCHAR(2),
    email VARCHAR(255),

    status VARCHAR(20),
    created_at TIMESTAMPTZ,
    last_login TIMESTAMPTZ
);

-- 插
```

**问题**:

- 添加数据操作错误处理

---

**行 162** (sql):

```sql

-- 测试脚本
DO $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
BEGIN
    -- 禁用Skip Scan (测试对比)
    SET enable_indexskipscan = off;

    start_time := clock_timestamp();
    PERFORM COUNT(
```

**问题**:

- 添加事务错误处理和回滚

---

### 10-pg_upgrade升级完整指南.md

**行 143** (bash):

```bash
# 全量备份
pg_basebackup -D /backup/pg17_backup -Ft -z -P

# 或使用pg_dump
pg_dumpall -U postgres > /backup/pg17_full.sql

```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 246** (bash):

```bash
# 启动PostgreSQL 18
systemctl start postgresql@18-main

# 检查状态
psql -U postgres -c "SELECT version();"
# PostgreSQL 18.1 ...

```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 259** (bash):

```bash
# 分阶段ANALYZE（推荐，不阻塞）
/usr/lib/postgresql/18/bin/vacuumdb \
    --all \
    --analyze-in-stages \
    -U postgres

# 或全面ANALYZE
vacuumdb --all --analyze --verbose -U postgres

```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 11-VACUUM增强与积极冻结策略完整指南.md

**行 278** (sql):

```sql
-- 创建测试表
CREATE TABLE large_table (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    data JSONB,
    status
```

**问题**:

- 添加数据操作错误处理

---

**行 439** (sql):

```sql
-- 监控积极冻结效果
CREATE OR REPLACE FUNCTION check_eager_freeze_stats(
    schema_name TEXT DEFAULT 'public'
)
RETURNS TABLE (
    table_name TEXT,
    total_pages BIGINT,
    frozen_pages BIGINT,
    froze
```

**问题**:

- 添加事务错误处理和回滚

---

**行 585** (sql):

```sql

-- 会话1: 长查询（持有AccessShareLock）
BEGIN;
SELECT count(*) FROM large_table WHERE status = 'active';
-- 执行10分钟...

-- 会话2: VACUUM尝试truncate（需要AccessExclusiveLock）
VACUUM large_table;
-- ⚠️ 等待会话1释放锁...

--
```

**问题**:

- 添加事务错误处理和回滚

---

**行 737** (sql):

```sql
-- 创建XID风险监控函数
CREATE OR REPLACE FUNCTION calculate_xid_risk()
RETURNS TABLE (
    database_name NAME,
    oldest_xid XID,
    current_xid XID,
    xid_age BIGINT,
    remaining_xids BIGINT,
    risk_
```

**问题**:

- 添加事务错误处理和回滚

---

**行 906** (bash):

```bash
#!/bin/bash
# vacuum_aio_benchmark.sh

# 测试环境
DB_NAME="testdb"
TABLE_NAME="large_test_table"
TABLE_SIZE="500GB"

# 测试场景
scenarios=(
    "同步I/O:sync:8"
    "线程池AIO:worker:16"
    "io_uring:io_uring:32"
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 1055** (sql):

```sql

-- 策略1：按时间分区（推荐）
CREATE TABLE orders (
    order_id BIGSERIAL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    total_amount DECIMAL(12,2),
    status VARCHAR(20)
)
```

**问题**:

- 添加连接错误处理

---

**行 1115** (sql):

```sql
-- 策略3：分阶段执行大表VACUUM


-- 阶段1：快速清理（只清理死元组，不冻结）
VACUUM (FREEZE off, TRUNCATE off) large_table;
-- 耗时：30分钟

-- 阶段2：渐进式冻结（分批冻结页面）
DO $$
DECLARE
    block_start BIGINT;
    block_end BIGINT;
    total_bloc
```

**问题**:

- 添加事务错误处理和回滚

---

**行 1162** (bash):

```bash
#!/bin/bash
# parallel_vacuum.sh - 并行VACUUM多个表

DB_NAME="production"

# 大表列表（按大小排序）
LARGE_TABLES=(
    "orders:2TB"
    "order_items:1.5TB"
    "user_actions:1TB"
    "logs:800GB"
)

# 最大并行度
MAX_PARAL
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 1769** (bash):

```bash
#!/bin/bash
# daily_vacuum_check.sh

echo "=== PostgreSQL VACUUM日常巡检 - $(date) ==="

# 1. 检查XID年龄
echo "1. XID年龄检查："
psql -d postgres -t -A -F"," <<EOF
SELECT datname, age(datfrozenxid),
       CASE W
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 1826** (bash):

```bash
#!/bin/bash
# monthly_vacuum_maintenance.sh

echo "=== PostgreSQL VACUUM月度维护 - $(date) ==="

# 1. 手动VACUUM所有大表（避免强制全表扫描）
echo "1. 执行大表VACUUM..."

LARGE_TABLES=$(psql -d mydb -t -A <<EOF
SELECT scheman
```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 11-查询优化器深度解析.md

**行 511** (sql):

```sql
-- 降低某个路径成本
SET random_page_cost = 1.0;  -- 让索引更"便宜"

-- 提高并行度
SET parallel_setup_cost = 0;
SET parallel_tuple_cost = 0;

-- 临时调整（单个查询）
BEGIN;
SET LOCAL random_page_cost = 1.0;
SELECT ...;
COMMIT;


```

**问题**:

- 添加事务错误处理和回滚

---

### 12-JSONB高级应用指南.md

**行 5** (sql):

```sql
-- JSON: 存储原始文本
CREATE TABLE json_test (data JSON);
INSERT INTO json_test VALUES ('{"name":"Alice","age":30}');


-- JSONB: 二进制存储（推荐）
CREATE TABLE jsonb_test (data JSONB);
INSERT INTO jsonb_test VALUES
```

**问题**:

- 添加数据操作错误处理

---

**行 35** (sql):

```sql
-- 创建测试表
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,

    profile JSONB
);

INSERT INTO users (profile) VALUES
('{"name":"Alice","age":30,"tags":["vip","active"],"address":{"city":"NYC"}}'),
(
```

**问题**:

- 添加数据操作错误处理

---

**行 69** (sql):

```sql

-- 拼接
UPDATE users SET profile = profile || '{"verified":true}';

-- 删除键
UPDATE users SET profile = profile - 'age';

-- 删除多个键
UPDATE users SET profile = profile - ARRAY['age','tags'];

-- 删除路径
UPDATE
```

**问题**:

- 添加数据操作错误处理

---

**行 224** (sql):

```sql
-- 用户事件表（schema-less）
CREATE TABLE user_events (
    event_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIM
```

**问题**:

- 添加数据操作错误处理

---

**行 253** (sql):

```sql
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(10),
    old_data JSONB,
    new_data JSONB,
    changed_fields JSONB,  -- 存储变更字段
    use
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 12-时态约束与时间段完整性指南.md

**行 541** (sql):

```sql
-- 酒店退房时间10:00，下一客人入住时间10:00 → 允许
INSERT INTO hotel_bookings VALUES
    (DEFAULT, 201, 'Alice', '2025-01-15 14:00', '2025-01-17 10:00', 'confirmed'),
    (DEFAULT, 201, 'Bob', '2025-01-17 10:00', '202
```

**问题**:

- 添加数据操作错误处理

---

**行 665** (sql):

```sql
-- 持仓表
CREATE TABLE positions (
    position_id SERIAL,

    account_id BIGINT NOT NULL,
    security_code TEXT NOT NULL,  -- 证券代码
    quantity BIGINT NOT NULL,
    valid_from TIMESTAMPTZ NOT NULL,

```

**问题**:

- 添加事务错误处理和回滚

---

**行 748** (sql):

```sql
-- 无约束，应用层检查
CREATE TABLE bookings_app_check (
    booking_id SERIAL PRIMARY KEY,
    room_id INT,

    check_in TIMESTAMPTZ,
    check_out TIMESTAMPTZ
);

-- 应用层代码（Python示例）
def create_booking(room_id
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 884** (sql):

```sql

-- 迁移步骤
-- 1. 创建新表（时态约束）
CREATE TABLE bookings_new (
    booking_id SERIAL,
    room_id INT NOT NULL,
    check_in TIMESTAMPTZ NOT NULL,
    check_out TIMESTAMPTZ NOT NULL,
    guest_name TEXT,

    C
```

**问题**:

- 添加事务错误处理和回滚

---

### 13-存储过程与触发器实战.md

**行 5** (sql):

```sql
-- 函数 (FUNCTION)
CREATE OR REPLACE FUNCTION calculate_total(order_id INT)
RETURNS NUMERIC AS $$
DECLARE
    total NUMERIC;
BEGIN
    SELECT SUM(price * quantity) INTO total
    FROM order_items
    WH
```

**问题**:

- 添加数据操作错误处理

---

**行 65** (sql):

```sql
-- 返回TABLE
CREATE OR REPLACE FUNCTION get_user_orders(p_user_id INT)
RETURNS TABLE (
    order_id INT,
    order_date TIMESTAMPTZ,
    total_amount NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT o.
```

**问题**:

- 添加事务错误处理和回滚

---

**行 88** (sql):

```sql
CREATE OR REPLACE FUNCTION dynamic_query(
    table_name TEXT,
    condition TEXT
) RETURNS SETOF RECORD AS $$
DECLARE
    query TEXT;
BEGIN
    query := format('SELECT * FROM %I WHERE %s', table_name
```

**问题**:

- 添加事务错误处理和回滚

---

**行 112** (sql):

```sql
CREATE OR REPLACE FUNCTION process_large_table()
RETURNS VOID AS $$
DECLARE
    cur CURSOR FOR SELECT * FROM large_table;
    rec RECORD;
    counter INT := 0;
BEGIN
    OPEN cur;

    LOOP
        FE
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 183** (sql):

```sql
-- 审计日志
CREATE TABLE audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    user_name TEXT,
    changed_at TIMESTAMPTZ DEFAU
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 223** (sql):

```sql
-- 视图触发器
CREATE VIEW user_summary AS
SELECT
    user_id,
    username,
    COUNT(o.order_id) AS order_count,
    SUM(o.amount) AS total_spent
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
G
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 262** (sql):

```sql
-- 记录DDL操作
CREATE TABLE ddl_log (
    log_id BIGSERIAL PRIMARY KEY,
    event_type TEXT,
    object_type TEXT,
    object_identity TEXT,
    command TEXT,
    user_name TEXT,
    created_at TIMESTAMPT
```

**问题**:

- 添加事务错误处理和回滚

- 添加数据操作错误处理

---

**行 347** (sql):

```sql
CREATE OR REPLACE FUNCTION get_table_data(table_name TEXT)
RETURNS SETOF RECORD AS $$
BEGIN
    RETURN QUERY EXECUTE format('SELECT * FROM %I', table_name);
END;
$$ LANGUAGE plpgsql;

-- 使用时指定列类型
SELE
```

**问题**:

- 添加事务错误处理和回滚

---

**行 365** (sql):

```sql
CREATE OR REPLACE PROCEDURE batch_update_prices(
    category_id INT,
    discount_percent NUMERIC
)
LANGUAGE plpgsql AS $$
DECLARE
    batch_size INT := 1000;
    updated INT;
BEGIN
    LOOP

```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 532** (sql):

```sql
-- 订单汇总表
CREATE TABLE order_summary (
    user_id INT PRIMARY KEY,
    total_orders INT DEFAULT 0,
    total_amount NUMERIC DEFAULT 0,
    last_order_at TIMESTAMPTZ
);

-- 触发器维护汇总
CREATE OR REPLACE FU
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 581** (sql):

```sql
-- Bad: 可能无限递归
CREATE OR REPLACE FUNCTION bad_trigger()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users SET updated_at = now() WHERE user_id = NEW.user_id;
    RETURN NEW;  -- 触发器本身又会被触发
END;
$$ LANGUAGE
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 603** (sql):

```sql
-- 行级触发器（每行触发一次）
CREATE TRIGGER trg_row_level
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION row_level_function();

-- 语句级触发器（每个语句触发一次）
CREATE TRIGGER trg_statement_level
    AFTER U
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 13-查询优化器增强完整指南.md

**行 502** (sql):

```sql
-- 测试场景：100万行表，IN列表包含10-10000个值

-- 创建测试表
CREATE TABLE test_in_performance (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    category_id INT NOT NULL,
    value NUMERIC(12,2),
    creat
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 571** (sql):

```sql
-- 场景：IN列表超过10000个值

-- ❌ 不推荐：超大IN列表
SELECT * FROM orders
WHERE order_id IN (SELECT unnest(ARRAY[... 50000个值 ...]));
-- 问题：查询计划生成慢、内存消耗大

-- ✅ 推荐：使用临时表
CREATE TEMP TABLE temp_order_ids (order_id BIGIN
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 772** (sql):

```sql
-- 测试场景：365个日分区，查询1天数据

CREATE TABLE sales_data (
    sale_id BIGSERIAL,
    sale_date DATE NOT NULL,
    user_id BIGINT,
    amount NUMERIC(12,2),
    region VARCHAR(50)
) PARTITION BY RANGE (sale_da
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 2132** (sql):

```sql
-- 场景：关联列查询

-- 创建测试数据（强关联）
CREATE TABLE orders_test (
    order_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    country VARCHAR(2),
    region VARCHAR(50),
    amount NUMERIC(12,2)
);


-- country和r
```

**问题**:

- 添加数据操作错误处理

---

**行 2289** (sql):

```sql
-- 测试不同并行度的性能
DO $$
DECLARE
    workers INT;
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    duration INTERVAL;

BEGIN
    FOR workers IN 1,2,4,8,16 LOOP
        EXECUTE format('SET max_paral
```

**问题**:

- 添加事务错误处理和回滚

---

**行 2329** (sql):

```sql
-- 场景：大表GROUP BY

CREATE TABLE sales_data (
    sale_id BIGSERIAL,
    product_id INT,
    region_id INT,
    sale_date DATE,

    amount NUMERIC(12,2)
);

-- 插入10亿行
INSERT INTO sales_data (product_id,
```

**问题**:

- 添加数据操作错误处理

---

### 14-并行查询与JIT编译增强指南.md

**行 158** (sql):

```sql
-- 创建测试表（1000万行）
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    total_amount NUMERIC(12,2),

    discount_rate NUMERIC(3,2),
    tax_rate NUMERIC(3
```

**问题**:

- 添加数据操作错误处理

---

**行 272** (sql):

```sql
-- 创建测试表
CREATE TABLE large_table (
    id BIGINT PRIMARY KEY,
    user_id INT,
    amount NUMERIC(12,2),
    created_at TIMESTAMPTZ
);


CREATE TABLE small_table (
    user_id INT PRIMARY KEY,
    use
```

**问题**:

- 添加数据操作错误处理

---

**行 741** (sql):

```sql
-- 1. 全局启用JIT（默认）
ALTER SYSTEM SET jit = on;

-- 2. 针对特定查询禁用JIT（如短查询）
SET jit = off;
SELECT * FROM small_table WHERE id = 123;


-- 3. 会话级临时启用
SET LOCAL jit_above_cost = 10000;  -- 降低阈值
SELECT ... FROM
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 923** (sql):

```sql
-- JIT不适用的场景

-- 1. 短查询（编译开销>执行时间）
SELECT * FROM users WHERE id = 123;
-- 执行时间：0.5ms，JIT编译：15ms → 得不偿失


-- 2. 大量小事务（OLTP）
BEGIN;
INSERT INTO orders VALUES (...);
UPDATE inventory SET quantity = quanti
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 14-数据类型深度解析.md

**行 71** (sql):

```sql
-- 类型对比
VARCHAR(n)  -- 变长，最大n字符
TEXT        -- 变长，无限制
CHAR(n)     -- 定长，空格填充


-- 性能测试
CREATE TABLE text_test (
    id SERIAL PRIMARY KEY,
    col_varchar VARCHAR(100),
    col_text TEXT,
    col_char
```

**问题**:

- 添加数据操作错误处理

---

**行 110** (sql):

```sql
-- tsvector: 预处理的文本向量
CREATE TABLE documents (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,

    content TEXT,
    search_vector tsvector
);

-- 自动更新tsvector
CREATE OR REPLACE FUNCTION update_search_
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 217** (sql):

```sql
-- 创建数组列
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    tags TEXT[],

    scores INT[]
);

-- 插入
INSERT INTO users (tags, scores) VALUES
(ARRAY['vip', 'active'], ARRAY[95, 87, 92]),
('{premiu
```

**问题**:

- 添加数据操作错误处理

---

**行 281** (sql):

```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_data JSONB

);

-- 嵌套JSON
INSERT INTO products (product_data) VALUES
('{
    "name": "Laptop",
    "price": 999.99,
    "specs": {
```

**问题**:

- 添加数据操作错误处理

---

**行 403** (sql):

```sql
-- 创建复合类型
CREATE TYPE address_type AS (
    street TEXT,
    city TEXT,

    state VARCHAR(2),
    zip_code VARCHAR(10)
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT,
    a
```

**问题**:

- 添加数据操作错误处理

---

**行 499** (sql):

```sql
-- 类型
INET    -- IP地址或网络

CIDR    -- 网络地址（必须有前缀）
MACADDR -- MAC地址

-- 示例
CREATE TABLE access_logs (
    log_id BIGSERIAL PRIMARY KEY,
    client_ip INET,
    server_ip INET,
    network CIDR,
    creat
```

**问题**:

- 添加数据操作错误处理

---

**行 540** (sql):

```sql

-- 创建向量
CREATE EXTENSION vector;

CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    vec vector(128)
);

-- 插入
INSERT INTO embeddings (vec) VALUES
('[0.1, 0.2, 0.3, ...]'),  -- 文本格式
(ARRAY[0.1,
```

**问题**:

- 添加数据操作错误处理

---

### 15-WAL与检查点优化完整指南.md

**行 111** (sql):

```sql
-- 插入一行数据
INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com');

-- 生成的WAL记录（简化）
{
    "type": "HEAP_INSERT",
    "relation": "users (OID 16384)",
    "block": 0,
    "offset":
```

**问题**:

- 添加数据操作错误处理

---

**行 182** (sql):

```sql
-- 测试：10万行INSERT操作的WAL生成量

-- PostgreSQL 17（默认压缩）
CREATE TABLE test_wal (
    id BIGSERIAL PRIMARY KEY,
    data TEXT
);

-- 记录WAL位置
SELECT pg_current_wal_lsn() AS start_lsn \gset

-- 插入数据
INSERT INTO
```

**问题**:

- 添加数据操作错误处理

---

**行 267** (sql):

```sql
-- 模拟检查点风暴
-- 大量写入 → 大量脏页 → 检查点刷盘 → I/O尖峰

CREATE TABLE wal_intensive (
    id BIGSERIAL,
    payload BYTEA
);

-- 写入10GB数据
INSERT INTO wal_intensive (payload)
SELECT gen_random_bytes(10240)  -- 10KB
```

**问题**:

- 添加数据操作错误处理

---

**行 418** (bash):

```bash
#!/bin/bash
# 测试WAL写入性能

# pgbench初始化
pgbench -i -s 100 testdb

# 测试1：PG 17（无AIO）
psql -c "ALTER SYSTEM SET aio = off; SELECT pg_reload_conf();"


pgbench -c 100 -j 10 -T 60 -M prepared testdb
# TPS: 1
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 716** (sql):

```sql
-- 创建监控视图
CREATE OR REPLACE VIEW wal_health_check AS
SELECT
    -- WAL生成速率
    pg_wal_lsn_diff(pg_current_wal_lsn(), pg_current_wal_lsn() - '0/10000000'::pg_lsn) / 60.0 AS wal_rate_mb_per_min,

    --
```

**问题**:

- 添加事务错误处理和回滚

---

**行 900** (bash):

```bash
#!/bin/bash
# pitr_recovery.sh
# 时间点恢复脚本

# 1. 停止PostgreSQL
pg_ctl stop -D /data/postgresql/data

# 2. 恢复基础备份

tar -xzf /backup/base_backup_2025-01-01.tar.gz -C /data/postgresql/

# 3. 配置recovery.conf（
```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 15-扩展开发完整指南.md

**行 35** (sql):

```sql
-- my_extension--1.0.sql

-- 创建schema
CREATE SCHEMA IF NOT EXISTS my_extension;


-- 创建函数
CREATE OR REPLACE FUNCTION my_extension.hello(name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN 'Hello, ' || name
```

**问题**:

- 添加事务错误处理和回滚

---

**行 100** (bash):

```bash
# 构建
make


# 安装
sudo make install

# 在数据库中安装
psql -d mydb -c "CREATE EXTENSION my_extension;"

# 查看
psql -d mydb -c "\dx my_extension"

```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 355** (sql):

```sql
-- auto_partition扩展
CREATE OR REPLACE FUNCTION auto_partition.create_partition_if_not_exists(
    parent_table TEXT,
    partition_column TEXT,
    partition_value DATE
) RETURNS VOID AS $$
DECLARE

```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 491** (sql):

```sql
-- 创建监控函数
CREATE OR REPLACE FUNCTION monitor.table_stats()
RETURNS TABLE (
    table_name TEXT,
    row_count BIGINT,
    total_size TEXT,
    index_size TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
```

**问题**:

- 添加事务错误处理和回滚

---

**行 518** (sql):

```sql
-- 字符串工具
CREATE OR REPLACE FUNCTION utils.slugify(input TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN lower(regexp_replace(
        regexp_replace(input, '[^a-zA-Z0-9\s-]', '', 'g'),
        '[\s-]+', '-'
```

**问题**:

- 添加事务错误处理和回滚

---

### 16-事务隔离级别深度解析.md

**行 5** (sql):

```sql
-- PostgreSQL支持的隔离级别
READ UNCOMMITTED    -- 实际等同于READ COMMITTED
READ COMMITTED      -- 默认
REPEATABLE READ     -- 快照隔离
SERIALIZABLE        -- 完全串行化

-- 设置隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL SE
```

**问题**:

- 添加事务错误处理和回滚

---

**行 27** (sql):

```sql
-- 会话1
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
-- 不提交

-- 会话2
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT balance FROM accounts WHERE account_id = 1;
-- 看
```

**问题**:

- 添加事务错误处理和回滚

- 添加数据操作错误处理

---

**行 73** (sql):

```sql
-- 会话1
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE account_id = 1;
-- 读取: 1000

-- 会话2
BEGIN;
UPDATE accounts SET balance = balance + 500 WHERE account_id = 1
```

**问题**:

- 添加事务错误处理和回滚

- 添加数据操作错误处理

---

**行 140** (sql):

```sql
-- 会话1
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*) FROM orders WHERE user_id = 123;  -- 假设为5

-- 会话2
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
INSERT INTO orders (user_id, am
```

**问题**:

- 添加事务错误处理和回滚

- 添加数据操作错误处理

---

**行 201** (sql):

```sql
-- PostgreSQL不会发生（最低级别是READ COMMITTED）

-- 会话1
BEGIN;
UPDATE accounts SET balance = 0 WHERE account_id = 1;
-- 未提交

-- 会话2
SELECT balance FROM accounts WHERE account_id = 1;
-- 读取旧值，不会读到0（未提交的值）

```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 216** (sql):

```sql
-- Read Committed级别会发生

-- 会话1
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT balance FROM accounts WHERE account_id = 1;  -- 1000

-- 会话2
UPDATE accounts SET balance = 2000 WHERE account_id
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 235** (sql):

```sql
-- PostgreSQL的REPEATABLE READ防止幻读

-- 会话1
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM orders WHERE user_id = 123;  -- 5

-- 会话2
INSERT INTO orders (user_id, amount) VALUES
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 252** (sql):

```sql
-- 只有SERIALIZABLE可以防止

-- 场景: 账户总和必须>=0
CREATE TABLE accounts (account_id INT, balance NUMERIC);
INSERT INTO accounts VALUES (1, 100), (2, 100);

-- 会话1 (REPEATABLE READ)
BEGIN TRANSACTION ISOLATION L
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 283** (sql):

```sql
-- FOR UPDATE: 排他锁
BEGIN;
SELECT * FROM accounts WHERE account_id = 1 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
COMMIT;

-- FOR SHARE: 共享锁
BEGIN;
SELECT * FROM acco
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 312** (sql):

```sql
-- 显式锁表
LOCK TABLE accounts IN EXCLUSIVE MODE;

-- 锁模式:
ACCESS SHARE          -- SELECT
ROW SHARE             -- SELECT FOR UPDATE/SHARE
ROW EXCLUSIVE         -- INSERT/UPDATE/DELETE
SHARE UPDATE EXCL
```

**问题**:

- 添加数据操作错误处理

---

### 16-统计信息增强与查询规划指南.md

**行 142** (sql):

```sql
-- 创建测试表
CREATE TABLE sales (
    sale_id BIGSERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    amount NUMERIC(12,2),
    region TEXT,
    category TEXT
);

INSERT INTO sales
SELECT
    generate_ser
```

**问题**:

- 添加数据操作错误处理

---

**行 218** (sql):

```sql
-- 创建数据倾斜的表
CREATE TABLE skewed_data (
    id SERIAL PRIMARY KEY,
    value INT
);

-- 插入倾斜数据：80%集中在1-100，20%在100-10000
INSERT INTO skewed_data (value)
SELECT
    CASE
        WHEN random() < 0.8 THEN
```

**问题**:

- 添加数据操作错误处理

---

**行 322** (sql):

```sql
-- Selectivity估算示例
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    age INT,
    city TEXT,
    income NUMERIC(12,2)
);

INSERT INTO customers
SELECT
    generate_series(1, 1000000),

```

**问题**:

- 添加数据操作错误处理

---

**行 665** (sql):

```sql
-- 创建相关列的表
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    department TEXT,
    job_title TEXT,
    salary NUMERIC(10,2)
);

-- 插入相关数据（部门和职位强相关）
INSERT INTO employees (department, job
```

**问题**:

- 添加数据操作错误处理

---

**行 745** (sql):

```sql
-- 创建倾斜数据
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    status TEXT
);

INSERT INTO orders (status)
SELECT
    CASE
        WHEN random() < 0.7 THEN 'completed'
        WHEN random() < 0.

```

**问题**:

- 添加数据操作错误处理

---

**行 919** (sql):

```sql
-- 创建统计信息健康检查视图
CREATE OR REPLACE VIEW stats_health_check AS
SELECT
    schemaname,
    relname,

    n_live_tup,
    n_dead_tup,
    n_mod_since_analyze,
    last_analyze,
    last_autoanalyze,

    -
```

**问题**:

- 添加事务错误处理和回滚

---

**行 1164** (sql):

```sql
-- 策略1：定期全局ANALYZE（每日凌晨）
-- cron job或pg_cron
SELECT cron.schedule(
    'daily-analyze',
    '0 2 * * *',  -- 每天凌晨2点
    $$
    ANALYZE VERBOSE;
    $$
);

-- 策略2：针对性ANALYZE（高频变更表）
-- 监控n_mod_since_ana
```

**问题**:

- 添加事务错误处理和回滚

---

**行 1285** (sql):

```sql
-- 伪造统计信息（用于测试）
-- 警告：仅用于开发/测试环境！

-- 1. 备份真实统计
CREATE TABLE pg_statistic_backup AS
SELECT * FROM pg_statistic
WHERE starelid = 'orders'::regclass;

-- 2. 修改统计信息
UPDATE pg_statistic

SET stanumbers1 =
```

**问题**:

- 添加数据操作错误处理

---

**行 1317** (bash):

```bash
#!/bin/bash
# export_stats.sh - 导出统计信息

DB_NAME="production"
OUTPUT_FILE="stats_export.sql"

psql -d $DB_NAME -c "
COPY (
    SELECT
        'ALTER TABLE ' || quote_ident(schemaname) || '.' || quote_i

```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 17-MERGE命令与RETURNING增强完整指南.md

**行 84** (sql):

```sql
-- PostgreSQL 17：MERGE不支持RETURNING
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET value = s.value
WHEN NOT MATCHED THEN

    INSERT (id, value) VALUES (s.id, s.value
```

**问题**:

- 添加数据操作错误处理

---

**行 124** (sql):

```sql
-- 创建测试表
CREATE TABLE inventory (
    product_id INT PRIMARY KEY,
    quantity INT,
    last_updated TIMESTAMPTZ DEFAULT now()
);


INSERT INTO inventory VALUES (1, 100), (2, 200), (3, 300);

-- MERGE操
```

**问题**:

- 添加数据操作错误处理

---

**行 173** (sql):

```sql
-- 将MERGE结果存储到临时表或传递给后续查询
WITH merge_results AS (
    MERGE INTO target t
    USING source s ON t.id = s.id
    WHEN MATCHED THEN UPDATE SET value = s.value
    WHEN NOT MATCHED THEN INSERT VALUES (s.

```

**问题**:

- 添加数据操作错误处理

---

**行 206** (sql):

```sql
MERGE INTO target_table [ [ AS ] target_alias ]
USING source_table [ [ AS ] source_alias ]
ON join_condition

-- 匹配时的操作（可以多个WHEN MATCHED）
[ WHEN MATCHED [ AND condition ] THEN

    { UPDATE SET { colum
```

**问题**:

- 添加数据操作错误处理

---

**行 233** (sql):

```sql
-- 案例：库存同步系统
MERGE INTO warehouse_inventory wi
USING daily_transactions dt
    ON wi.product_id = dt.product_id AND wi.warehouse_id = dt.warehouse_id


-- 场景1：匹配且有足够库存 → 更新
WHEN MATCHED AND wi.quantity
```

**问题**:

- 添加数据操作错误处理

---

**行 306** (sql):

```sql
-- 1. 创建CDC日志表
CREATE TABLE order_changes (
    change_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    change_type TEXT NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'

    old_data JSONB,
    n
```

**问题**:

- 添加数据操作错误处理

---

**行 361** (sql):

```sql
-- 数据仓库增量更新

-- 源表：OLTP订单表
-- 目标表：OLAP订单事实表


CREATE TABLE fact_orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT,
    order_date DATE,
    total_amount NUMERIC(12,2),
    status TEXT,

```

**问题**:

- 添加数据操作错误处理

---

**行 431** (sql):

```sql

-- 缓慢变化维度（SCD Type 2）：保留历史版本

-- 目标表：客户维度（历史版本）
CREATE TABLE dim_customer (
    customer_key BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    customer_name TEXT,
    address TEXT,
    phone TE
```

**问题**:

- 添加数据操作错误处理

---

**行 513** (sql):

```sql
-- 源库 → 目标库实时同步（with conflict resolution）


MERGE INTO target_table t
USING (
    SELECT * FROM source_table
    WHERE updated_at > (
        SELECT COALESCE(MAX(sync_timestamp), '1970-01-01')

```

**问题**:

- 添加数据操作错误处理

---

**行 560** (sql):

```sql
-- 场景：100万行UPSERT操作

-- 方案A：INSERT ON CONFLICT
\timing on
INSERT INTO target (id, value)
SELECT id, value FROM source
ON CONFLICT (id) DO UPDATE
    SET value = EXCLUDED.value;

-- Time: 8500.234 ms

-
```

**问题**:

- 添加数据操作错误处理

---

**行 601** (sql):

```sql
-- 测试：RETURNING对性能的影响

-- 基线：无RETURNING
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET value = s.value

WHEN NOT MATCHED THEN INSERT VALUES (s.id, s.value);
-- Time: 820
```

**问题**:

- 添加数据操作错误处理

---

**行 643** (sql):

```sql
-- 通用审计日志表
CREATE TABLE audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    record_id TEXT NOT NULL,  -- 记录主
```

**问题**:

- 添加事务错误处理和回滚

- 添加数据操作错误处理

---

**行 783** (sql):

```sql
-- ❌ 反模式：MERGE中使用子查询
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET value = (
        SELECT AVG(value) FROM other_table  -- ❌ 子查询在UPDATE中
        WHERE id = t.id

```

**问题**:

- 添加数据操作错误处理

---

**行 820** (sql):

```sql
CREATE TABLE central_inventory (
    sku_id BIGINT PRIMARY KEY,
    quantity INT,
    reserved INT,
    available AS (quantity - reserved) STORED,
    last_updated TIMESTAMPTZ,
    updated_from TEXT,
```

**问题**:

- 添加数据操作错误处理

---

**行 882** (sql):

```sql
-- 银行流水对账

CREATE TABLE bank_transactions (
    transaction_id BIGINT PRIMARY KEY,
    account_id BIGINT,
    amount NUMERIC(18,2),
    transaction_type TEXT,
    transaction_time TIMESTAMPTZ,
    rec
```

**问题**:

- 添加数据操作错误处理

---

**行 938** (sql):

```sql

-- 创建MERGE操作监控视图
CREATE OR REPLACE VIEW merge_performance_stats AS
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,

    -- 识别MERGE操作
    CASE
        WHEN query LIKE 'MERGE INTO%
```

**问题**:

- 添加数据操作错误处理

---

### 17-窗口函数完整实战.md

**行 31** (sql):

```sql

CREATE TABLE scores (
    student_id INT,
    subject VARCHAR(50),
    score INT
);

INSERT INTO scores VALUES
(1, 'Math', 95),
(2, 'Math', 95),
(3, 'Math', 90),
(4, 'Math', 85);

SELECT
    student_i
```

**问题**:

- 添加数据操作错误处理

---

**行 230** (sql):

```sql
-- 去重，保留每个用户最新记录
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM user_events
)
DELETE FROM user_events
WHERE (user_id, c
```

**问题**:

- 添加数据操作错误处理

---

### 18-存储管理与TOAST优化指南.md

**行 169** (sql):

```sql
-- 创建测试表
CREATE TABLE mvcc_test (
    id INT PRIMARY KEY,
    value TEXT
);

INSERT INTO mvcc_test VALUES (1, 'version 1');


-- 查看初始tuple
SELECT
    t_ctid,          -- 元组标识符(page, offset)
    t_xmin,
```

**问题**:

- 添加数据操作错误处理

---

**行 260** (sql):

```sql
-- PLAIN：不压缩，不外部存储（定长类型默认）
-- 适用：INT, BIGINT, TIMESTAMP等

-- EXTENDED：先压缩，大于2KB再外部存储（TEXT/JSONB默认）

CREATE TABLE test_extended (
    id SERIAL PRIMARY KEY,
    data TEXT  -- 默认EXTENDED
);
ALTER TABLE t
```

**问题**:

- 添加数据操作错误处理

---

**行 364** (sql):

```sql
-- 测试不同压缩算法
CREATE TABLE compression_test (
    id SERIAL PRIMARY KEY,
    algorithm TEXT,
    data TEXT

);

-- pglz压缩（传统，PG默认）
ALTER TABLE compression_test ALTER COLUMN data SET COMPRESSION pglz;

IN
```

**问题**:

- 添加数据操作错误处理

---

**行 428** (sql):

```sql
-- PostgreSQL 18改进的Page压缩
/*
优化点：

1. 更智能的压缩决策（根据数据类型）
2. 压缩缓存（避免重复解压）
3. 部分解压（仅解压需要的列）
*/

-- 测试：宽表部分列访问
CREATE TABLE wide_table (
    id SERIAL PRIMARY KEY,
    col1 TEXT,
    col2 TEXT,
    col3 TEX
```

**问题**:

- 添加数据操作错误处理

---

**行 530** (sql):

```sql
-- 安装Citus
CREATE EXTENSION citus;

-- 创建列式表
CREATE TABLE analytics_data (
    date DATE,
    user_id INT,
    event_type TEXT,
    value NUMERIC
) USING columnar;

-- 插入数据
INSERT INTO analytics_data

```

**问题**:

- 添加数据操作错误处理

---

**行 589** (sql):

```sql
-- 测试：100万行，不同数据类型的存储大小
CREATE TABLE type_test_int (id INT, value INT);
CREATE TABLE type_test_bigint (id INT, value BIGINT);
CREATE TABLE type_test_numeric (id INT, value NUMERIC(10,2));
CREATE TABLE
```

**问题**:

- 添加数据操作错误处理

---

**行 639** (sql):

```sql
-- 创建Large Object
SELECT lo_create(0);  -- 返回OID：16789

-- 写入数据（流式）
\lo_import /path/to/large_video.mp4 16789

-- 关联到表
CREATE TABLE videos (
    video_id SERIAL PRIMARY KEY,
    title TEXT,
    video_
```

**问题**:

- 添加数据操作错误处理

---

**行 730** (sql):

```sql
-- 测试fillfactor对HOT更新的影响
CREATE TABLE hot_test_100 (
    id SERIAL PRIMARY KEY,
    value INT,
    data TEXT
) WITH (fillfactor = 100);  -- 无预留空间

CREATE TABLE hot_test_80 (
    id SERIAL PRIMARY KEY,
```

**问题**:

- 添加数据操作错误处理

---

**行 820** (sql):

```sql
-- 创建表膨胀检测函数
CREATE OR REPLACE FUNCTION check_table_bloat(
    p_schema TEXT DEFAULT 'public'
)
RETURNS TABLE (
    schema_name TEXT,
    table_name TEXT,
    actual_size_bytes BIGINT,
    expected_si
```

**问题**:

- 添加事务错误处理和回滚

---

**行 884** (sql):

```sql
-- 策略1：VACUUM（在线，最低影响）
VACUUM VERBOSE orders;
-- 优点：无锁，可在生产运行
-- 缺点：不释放磁盘空间，仅标记空间可重用

-- 策略2：VACUUM FULL（锁表，彻底重建）
VACUUM FULL VERBOSE orders;
-- 优点：完全消除膨胀，释放磁盘空间
-- 缺点：排它锁，停机时间长

-- 策略3：pg_repack（在线重建
```

**问题**:

- 添加事务错误处理和回滚

---

**行 1123** (sql):

```sql
-- 实时表膨胀监控（Prometheus metrics）
CREATE OR REPLACE FUNCTION table_bloat_metrics()
RETURNS TABLE (
    metric_name TEXT,
    metric_value NUMERIC,
    labels TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELEC
```

**问题**:

- 添加事务错误处理和回滚

---

**行 1284** (sql):

```sql
-- 性能对比测试（10MB文件）

-- 方案A：TOAST存储
CREATE TABLE docs_toast (
    id SERIAL PRIMARY KEY,
    content TEXT
);

INSERT INTO docs_toast (content)
SELECT repeat('x', 10485760)  -- 10MB
FROM generate_series(

```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 1356** (sql):

```sql
-- PostgreSQL：UPDATE创建新版本
UPDATE orders SET status = 'completed' WHERE id = 1;
-- 结果：
-- - 旧版本保留在heap（死元组）
-- - 新版本写入heap
-- - 需VACUUM清理死元组

-- MySQL InnoDB：UPDATE覆盖

UPDATE orders SET status = 'comple
```

**问题**:

- 添加数据操作错误处理

---

### 18-并发控制深度解析.md

**行 7** (sql):

```sql
-- 查看行版本信息
CREATE EXTENSION IF NOT EXISTS pageinspect;

-- 创建测试表
CREATE TABLE mvcc_test (id INT PRIMARY KEY, value TEXT);

INSERT INTO mvcc_test VALUES (1, 'version 1');

-- 查看页面内容
SELECT * FROM heap_p
```

**问题**:

- 添加数据操作错误处理

---

**行 85** (sql):

```sql
-- FOR UPDATE（排他锁）
BEGIN;
SELECT * FROM accounts WHERE account_id = 1 FOR UPDATE;
-- 其他事务无法UPDATE/DELETE/FOR UPDATE这一行
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;

COMMIT;

-- FOR
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 220** (python):

```python
def optimistic_lock_update(conn, account_id, amount, max_retries=5):
    """乐观锁更新（带重试）"""


    for attempt in range(max_retries):
        cursor = conn.cursor()

        # 读取当前版本
        cursor.execut
```

**问题**:

- 添加try-except错误处理

---

**行 309** (sql):

```sql
-- 任务队列
CREATE TABLE task_queue (
    task_id BIGSERIAL PRIMARY KEY,
    task_data JSONB,
    status VARCHAR(20) DEFAULT 'pending',

    created_at TIMESTAMPTZ DEFAULT now()
);

-- Worker获取任务（无锁竞争）
BEG
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 19-分区表增强与智能裁剪指南.md

**行 137** (sql):

```sql
-- 创建分区表（按月分区，100个分区）
CREATE TABLE orders (
    order_id BIGINT,
    customer_id INT,
    order_date DATE NOT NULL,
    total_amount NUMERIC(12,2),
    status TEXT
) PARTITION BY RANGE (order_date);


```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 257** (sql):

```sql
-- 创建测试函数
CREATE OR REPLACE FUNCTION get_month_range(year INT, month INT)
RETURNS DATERANGE AS $$
BEGIN
    RETURN daterange(
        make_date(year, month, 1),
        make_date(year, month, 1) + INT
```

**问题**:

- 添加事务错误处理和回滚

---

**行 500** (sql):

```sql
-- 创建分区表1：订单
CREATE TABLE orders_partitioned (
    order_id BIGINT,
    order_date DATE NOT NULL,
    customer_id INT,
    total_amount NUMERIC(12,2)
) PARTITION BY RANGE (order_date);

-- 创建分区表2：订单明细
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 645** (sql):

```sql

-- 创建自动分区管理函数
CREATE OR REPLACE FUNCTION create_partitions_for_next_months(
    p_table_name TEXT,
    p_months_ahead INT DEFAULT 3
)
RETURNS TEXT AS $$
DECLARE
    v_start_date DATE;
    v_end_date D
```

**问题**:

- 添加事务错误处理和回滚

---

**行 714** (sql):

```sql
-- 分区归档函数（移动到归档表）
CREATE OR REPLACE FUNCTION archive_old_partitions(
    p_table_name TEXT,
    p_months_old INT DEFAULT 12

)
RETURNS TEXT AS $$
DECLARE
    v_partition_record RECORD;
    v_archive_ta
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 901** (sql):

```sql
-- 分区大小评估函数
CREATE OR REPLACE FUNCTION evaluate_partition_size(
    p_table_name TEXT,
    p_row_count BIGINT,

    p_partition_count INT
)
RETURNS TABLE (
    partition_strategy TEXT,
    avg_partitio
```

**问题**:

- 添加事务错误处理和回滚

---

**行 1031** (sql):

```sql
-- 多级分区：日期 → 设备哈希
CREATE TABLE sensor_data (
    device_id BIGINT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature NUMERIC(5,2),
    humidity NUMERIC(5,2),
    pressure NUMERIC(7,2)
) PAR

```

**问题**:

- 添加事务错误处理和回滚

---

### 19-高级SQL查询技巧.md

**行 431** (sql):

```sql
-- INSERT ... ON CONFLICT
INSERT INTO inventory (product_id, stock)
VALUES
    (1, 100),
    (2, 200),

    (3, 300)
ON CONFLICT (product_id)
DO UPDATE SET
    stock = inventory.stock + EXCLUDED.stock,
```

**问题**:

- 添加数据操作错误处理

---

**行 706** (sql):

```sql
CREATE OR REPLACE FUNCTION dynamic_count(table_name TEXT, condition TEXT)
RETURNS BIGINT AS $$
DECLARE
    result BIGINT;
BEGIN
    EXECUTE format('SELECT COUNT(*) FROM %I WHERE %s', table_name, condi
```

**问题**:

- 添加事务错误处理和回滚

---

**行 725** (sql):

```sql
-- 根据参数选择列
CREATE OR REPLACE FUNCTION flexible_query(
    columns TEXT[],
    table_name TEXT,
    where_clause TEXT
) RETURNS TABLE(result JSONB) AS $$
BEGIN
    RETURN QUERY EXECUTE format(

```

**问题**:

- 添加事务错误处理和回滚

---

### 20-全文检索与排序规则变更指南.md

**行 163** (sql):

```sql
-- 创建测试表
CREATE TABLE collation_test (
    id SERIAL PRIMARY KEY,
    text_data TEXT
);

-- 插入100万行测试数据
INSERT INTO collation_test (text_data)
SELECT md5(random()::text)
FROM generate_series(1, 100000
```

**问题**:

- 添加数据操作错误处理

---

**行 254** (bash):

```bash
#!/bin/bash
# identify_fts_indexes.sh
# 识别所有全文检索索引

DB_NAME="your_database"

echo "=== 扫描全文检索索引 ==="

psql -d $DB_NAME <<EOF
-- 查找所有tsvector列
SELECT

    n.nspname AS schema,
    c.relname AS table_nam
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 322** (bash):

```bash
#!/bin/bash
# rebuild_fts_indexes.sh
# 批量重建全文检索索引（零停机）

DB_NAME="production_db"
SCHEMA="public"


echo "=== 开始重建全文检索索引 ==="
echo "数据库: $DB_NAME"
echo "Schema: $SCHEMA"
echo ""

# 获取所有tsvector索引
INDEXES
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 508** (sql):

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,

    title TEXT,
    content TEXT
);

INSERT INTO articles (title, content)
SELECT
    'Article ' || generate_series,
    md5(random()::text)
FROM gen
```

**问题**:

- 添加数据操作错误处理

---

**行 548** (sql):

```sql
-- 基准测试：字符串大小写转换


-- 创建测试表（多语言文本）
CREATE TABLE text_processing_test (
    id SERIAL PRIMARY KEY,
    english TEXT,
    chinese TEXT,
    japanese TEXT,
    arabic TEXT,
    mixed TEXT
);

-- 插入10万行
IN
```

**问题**:

- 添加数据操作错误处理

---

**行 589** (sql):

```sql
-- 测试：100万文档全文检索

CREATE TABLE documents (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    content_tsvector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
)
```

**问题**:

- 添加数据操作错误处理

---

**行 713** (bash):

```bash
#!/bin/bash
# blue_green_upgrade.sh

# 1. 搭建PG18集群（绿环境）
# 假设蓝环境：10.0.1.10:5432
# 绿环境：10.0.2.10:5432

GREEN_HOST="10.0.2.10"
BLUE_HOST="10.0.1.10"

echo "=== 蓝绿升级流程 ==="

# 2. 初始数据同步（pg_basebackup）
ech
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 790** (bash):

```bash
#!/bin/bash
# rollback_to_pg17.sh

# 场景：PG18发现严重问题，需紧急回滚

BLUE_HOST="10.0.1.10"  # PG17（保留）
GREEN_HOST="10.0.2.10"  # PG18（有问题）

echo "=== 紧急回滚到PG17 ==="


# 1. 停止PG18的写入
echo "【1/5】停止应用写入PG18..."
# 修改
```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 20-实用SQL模式集锦.md

**行 7** (sql):

```sql
-- 方法1: DELETE + ROW_NUMBER
DELETE FROM user_events

WHERE ctid NOT IN (
    SELECT ctid FROM (
        SELECT ctid,
               ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS
```

**问题**:

- 添加数据操作错误处理

---

**行 189** (sql):

```sql
-- 避免长事务和锁
DO $$
DECLARE
    deleted INT;
BEGIN

    LOOP
        DELETE FROM logs
        WHERE created_at < CURRENT_DATE - INTERVAL '90 days'
          AND ctid = ANY(
              ARRAY(

```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 222** (sql):

```sql
CREATE OR REPLACE FUNCTION batch_update_with_progress()
RETURNS VOID AS $$
DECLARE
    batch_size INT := 10000;
    total_rows BIGINT;
    updated BIGINT := 0;
    batch_updated INT;
BEGIN
    SELECT
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 329** (sql):

```sql
-- 清洗用户数据

UPDATE users
SET
    email = LOWER(TRIM(email)),
    phone = regexp_replace(phone, '[^0-9]', '', 'g'),
    name = INITCAP(TRIM(name))
WHERE
    email != LOWER(TRIM(email))
    OR phone != re
```

**问题**:

- 添加数据操作错误处理

---

**行 344** (sql):

```sql
-- 识别并处理异常值（3σ原则）

WITH stats AS (
    SELECT
        AVG(price) AS mean,
        STDDEV(price) AS stddev
    FROM products
),
outliers AS (
    SELECT
        product_id,
        price,
        (price
```

**问题**:

- 添加数据操作错误处理

---

**行 399** (sql):

```sql
CREATE TABLE audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    record_id TEXT,
    old_values JSONB,
    new_values JSONB,
    changed_fiel
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 459** (sql):

```sql
-- 汇总缓存表
CREATE TABLE user_stats_cache (
    user_id BIGINT PRIMARY KEY,
    order_count INT,
    total_spent NUMERIC,
    last_order_at TIMESTAMPTZ,
    cache_updated_at TIMESTAMPTZ DEFAULT now()
);

```

**问题**:

- 添加事务错误处理和回滚

- 添加数据操作错误处理

---

**行 511** (sql):

```sql
-- 当前版本表
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name VARCHAR(200),
    price NUMERIC(10,2),
    version INT DEFAULT 1,
    valid_from TIMESTAMPTZ DEFAULT now(),
    valid_to TIMES
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 577** (sql):

```sql
-- 任务表
CREATE TABLE task_queue (
    task_id BIGSERIAL PRIMARY KEY,
    task_type VARCHAR(50),
    payload JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    priority INT DEFAULT 0,
    retry_count
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 680** (sql):

```sql
-- 预计算每日汇总（物化视图）
CREATE MATERIALIZED VIEW daily_stats AS
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    COUNT(DIS
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 21-SQL优化50条军规.md

**行 139** (sql):

```sql
-- ✗ 逐条插入
INSERT INTO logs (message) VALUES ('log1');
INSERT INTO logs (message) VALUES ('log2');

-- ✓ 批量插入
INSERT INTO logs (message) VALUES ('log1'), ('log2'), ('log3');

```

**问题**:

- 添加数据操作错误处理

---

**行 150** (sql):

```sql
-- ✗ INSERT慢
INSERT INTO large_table SELECT * FROM source;

-- ✓ COPY最快
COPY large_table FROM '/tmp/data.csv' WITH (FORMAT csv);

```

**问题**:

- 添加数据操作错误处理

---

**行 202** (sql):

```sql
-- ✗ 长事务
BEGIN;
SELECT * FROM large_table;  -- 1000万行

-- 处理数据...（5分钟）
COMMIT;

-- ✓ 游标分批处理
BEGIN;
DECLARE cur CURSOR FOR SELECT * FROM large_table;
FETCH 1000 FROM cur;
-- 处理1000行
COMMIT;
-- 重复

```

**问题**:

- 添加事务错误处理和回滚

---

**行 220** (sql):

```sql
-- ✗ 过度使用SERIALIZABLE
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT * FROM products;  -- 只读查询
COMMIT;

-- ✓ 使用READ COMMITTED
BEGIN;  -- 默认READ COMMITTED
SELECT * FROM products;
COMMIT;

```

**问题**:

- 添加事务错误处理和回滚

---

**行 234** (python):

```python
# ✗ 事务后空闲
conn.cursor().execute("BEGIN")
result = conn.cursor().execute("SELECT * FROM users WHERE id=1")
# 处理结果...（忘记commit）
time.sleep(60)

# ✓ 及时提交
cursor.execute("BEGIN")
result = cursor.execute("
```

**问题**:

- 添加try-except错误处理

---

**行 271** (python):

```python
# ✓ 预编译（降低解析开销）
cursor.execute("PREPARE stmt AS SELECT * FROM users WHERE user_id = $1")
cursor.execute("EXECUTE stmt (123)")
cursor.execute("EXECUTE stmt (456)")

```

**问题**:

- 添加try-except错误处理

---

### 21-云原生部署与配置优化指南.md

**行 581** (bash):

```bash
#!/bin/bash
# test_ebs_performance.sh

echo "=== AWS EBS性能测试 ==="

# 1. 测试IOPS
echo "测试顺序读IOPS..."
sudo fio --name=seqread --rw=read --bs=8k --size=10G \
  --numjobs=4 --time_based --runtime=60 \
  --
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 691** (bash):

```bash
#!/bin/bash
# configure_numa_postgres.sh

# 1. 检查NUMA拓扑
numactl --hardware

echo "=== NUMA节点信息 ==="
lscpu | grep NUMA

# 2. 绑定PostgreSQL到单个NUMA节点
# 方案A：systemd服务配置
cat > /etc/systemd/system/postgresql
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 755** (sql):

```sql
-- 创建性能测试表
CREATE TABLE numa_test (
    id BIGSERIAL PRIMARY KEY,
    data TEXT
);

INSERT INTO numa_test (data)
SELECT md5(random()::TEXT)
FROM generate_series(1, 100000000);

VACUUM ANALYZE numa_tes
```

**问题**:

- 添加数据操作错误处理

---

**行 1216** (bash):

```bash
#!/bin/bash
# backup_restore_s3.sh

# 1. 全量备份到S3
pgbackrest --stanza=main --type=full backup

# 2. 增量备份（daily）
pgbackrest --stanza=main --type=incr backup

# 3. 验证备份
pgbackrest --stanza=main info

# 4

```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 1375** (bash):

```bash
#!/bin/bash
# cloud_performance_benchmark.sh
# 云环境PostgreSQL 18性能基准测试

DB_HOST="postgres-primary.database.svc.cluster.local"
DB_NAME="benchmark"
DB_USER="postgres"

echo "=== PostgreSQL 18 云环境性能基准测试 =
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 1431** (bash):

```bash
#!/bin/bash
# disaster_recovery_drill.sh
# PostgreSQL 18云原生容灾演练

NAMESPACE="database"
PRIMARY_POD="postgresql-0"
REPLICA_POD="postgresql-1"

echo "=== PostgreSQL 18容灾演练 ==="


# 1. 主节点健康检查
echo "【1/6】主
```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 22-TimescaleDB时序数据库完整指南.md

**行 34** (bash):

```bash
# 安装TimescaleDB
sudo apt install postgresql-18-timescaledb

# 配置
echo "shared_preload_libraries = 'timescaledb'" | \

  sudo tee -a /etc/postgresql/18/main/postgresql.conf

# 重启
sudo systemctl restart
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 77** (sql):

```sql
-- 高频插入
INSERT INTO sensor_data (time, sensor_id, temperature, humidity, pressure)
VALUES
    (now(), 1, 23.5, 65.2, 1013.2),
    (now(), 2, 24.1, 62.8, 1012.8),
    (now(), 3, 22.9, 67.5, 1014.1);

-

```

**问题**:

- 添加数据操作错误处理

---

**行 306** (python):

```python
from psycopg2.extras import execute_values

def bulk_insert_timeseries(conn, data, batch_size=10000):
    """高性能批量插入"""

    cursor = conn.cursor()

    for i in range(0, len(data), batch_size):


```

**问题**:

- 添加try-except错误处理

---

### 22-监控与可观测性完整体系指南.md

**行 838** (sql):

```sql
-- 对比AIO开启前后的性能
-- （需要先记录历史数据到监控表）

CREATE TABLE aio_performance_history (

    sample_time TIMESTAMPTZ DEFAULT now(),
    aio_enabled BOOLEAN,
    query_type TEXT,
    avg_duration_ms NUMERIC,
    io_
```

**问题**:

- 添加数据操作错误处理

---

**行 1015** (sql):

```sql
-- 创建锁超时告警函数
CREATE OR REPLACE FUNCTION check_long_running_locks()
RETURNS TABLE (
    alert_level TEXT,

    message TEXT,
    action_required TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        '🔴
```

**问题**:

- 添加事务错误处理和回滚

---

**行 1705** (bash):

```bash
#!/bin/bash
# monitoring_health_check.sh - 监控系统健康检查


echo "=== PostgreSQL 18 监控系统健康检查 ==="
echo "检查时间: $(date)"
echo ""

# 1. 检查postgres_exporter状态
echo "【1/8】检查postgres_exporter..."
if curl -s http:/
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 1802** (sql):

```sql
-- 创建性能基线表
CREATE TABLE performance_baseline (
    metric_name TEXT PRIMARY KEY,
    baseline_value NUMERIC,
    unit TEXT,

    threshold_warning NUMERIC,
    threshold_critical NUMERIC,
    last_upda
```

**问题**:

- 添加数据操作错误处理

---

**行 1863** (python):

```python
#!/usr/bin/env python3
"""
PostgreSQL 18 自动化巡检脚本
每日执行，生成健康报告
"""


import psycopg2
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mi
```

**问题**:

- 添加try-except错误处理
- 添加文件操作错误处理

---

### 23-PostGIS地理空间数据库实战.md

**行 7** (bash):

```bash
# 安装PostGIS
sudo apt install postgresql-18-postgis-3

# 创建扩展
psql -d mydb -c "CREATE EXTENSION postgis;"
psql -d mydb -c "CREATE EXTENSION postgis_topology;"

# 验证
psql -d mydb -c "SELECT PostGIS_Full
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 25** (sql):

```sql
-- 点（POINT）
CREATE TABLE locations (
    loc_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom geometry(POINT, 4326)  -- WGS84坐标系
);

INSERT INTO locations (name, geom) VALUES
('北京', ST_GeomFromT
```

**问题**:

- 添加数据操作错误处理

---

**行 231** (sql):

```sql
-- 围栏表
CREATE TABLE geofences (
    fence_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    fence_type VARCHAR(50),
    geom geometry(POLYGON, 4326),
    metadata JSONB
);

CREATE INDEX idx_geofences_
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 294** (sql):

```sql
-- 轨迹表
CREATE TABLE trajectories (
    traj_id BIGSERIAL PRIMARY KEY,
    device_id INT,
    path geometry(LINESTRING, 4326),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ
);

-- 计算路径长度
SELECT

```

**问题**:

- 添加数据操作错误处理

---

### 23-安全增强与零信任架构指南.md

**行 161** (sql):

```sql
-- 企业SSO集成（Okta/Azure AD/Keycloak）
-- 1. 安装oauth扩展
CREATE EXTENSION IF NOT EXISTS oauth2;

-- 2. 配置OAuth提供商（企业Okta）
CREATE SERVER okta_oauth FOREIGN DATA WRAPPER oauth2_fdw OPTIONS (
    authorization
```

**问题**:

- 添加事务错误处理和回滚

---

**行 261** (bash):

```bash
# 1. 生成SSL证书（生产环境使用CA签名证书）
openssl req -new -x509 -days 365 -nodes -text \
    -out server.crt \
    -keyout server.key \
    -subj "/CN=pg-server.company.com"

chmod 600 server.key
chown postgres:pos
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 299** (sql):

```sql
-- PostgreSQL 18 SCRAM增强

-- 1. 强制SCRAM认证（禁用MD5）
-- pg_hba.conf
host    all    all    0.0.0.0/0    scram-sha-256

-- 2. 密码强度策略（使用passwordcheck扩展）
CREATE EXTENSION IF NOT EXISTS passwordcheck;

-- post
```

**问题**:

- 添加事务错误处理和回滚

---

**行 386** (bash):

```bash
# pg_hba.conf企业级配置示例

# 1. 本地超级用户（peer认证，最安全）
local   all   postgres                peer

# 2. 应用连接（SCRAM + SSL）
hostssl all   app_user   10.0.1.0/24   scram-sha-256

# 3. 管理员远程（证书认证 + SCRAM）
hostssl
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 418** (bash):

```bash
# 测试认证配置（不重启数据库）
pg_ctl reload

# 验证连接
psql -h localhost -U app_user -d production
# 输入密码：应提示SCRAM认证

# 查看当前连接认证方法
SELECT
    usename,
    client_addr,
    backend_type,
    state,
    pg_backend_pid(

```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 439** (sql):

```sql
-- 企业级角色体系设计

-- 1. 创建角色层次
-- 顶层：超级管理员（仅DBA）
CREATE ROLE dba WITH SUPERUSER LOGIN PASSWORD 'xxx';

-- 第二层：功能角色（不可登录）
CREATE ROLE db_readonly NOLOGIN;
CREATE ROLE db_readwrite NOLOGIN;
CREATE ROLE db_a

```

**问题**:

- 添加数据操作错误处理

---

**行 778** (bash):

```bash
# 方案A：文件系统级加密（LUKS，推荐）

# 1. 创建加密卷
cryptsetup luksFormat /dev/sdb
cryptsetup luksOpen /dev/sdb pg_encrypted

# 2. 格式化并挂载

mkfs.ext4 /dev/mapper/pg_encrypted
mount /dev/mapper/pg_encrypted /var/lib/post
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 810** (sql):

```sql
-- 使用pgcrypto扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 敏感数据表
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,

    phone TEXT,
    ssn_encrypted BYTEA,
```

**问题**:

- 添加数据操作错误处理

---

**行 867** (sql):

```sql
-- 安装pgAudit
CREATE EXTENSION pgaudit;

-- 配置审计策略
-- postgresql.conf
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'all'  -- 审计所有操作
pgaudit.log_catalog = off  -- 不审计系统表查询
pgaudit.log_parameter =

```

**问题**:

- 添加数据操作错误处理

---

**行 902** (sql):

```sql
-- 将审计日志导入数据库（使用file_fdw）
CREATE EXTENSION file_fdw;

CREATE SERVER log_server FOREIGN DATA WRAPPER file_fdw;

CREATE FOREIGN TABLE audit_logs (
    log_time TIMESTAMPTZ,
    user_name TEXT,
    datab
```

**问题**:

- 添加数据操作错误处理

---

**行 975** (sql):

```sql
-- GDPR合规报告：数据访问追踪
CREATE OR REPLACE FUNCTION gdpr_access_report(
    p_user_email TEXT,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    access_time TIMESTAMPTZ,

    database_name TEX
```

**问题**:

- 添加事务错误处理和回滚

---

**行 1057** (sql):

```sql
-- 微隔离：细粒度网络访问控制

-- 1. Schema级隔离
CREATE SCHEMA finance;
CREATE SCHEMA operations;
CREATE SCHEMA analytics;

-- 2. 角色绑定Schema
GRANT USAGE ON SCHEMA finance TO finance_team;

REVOKE ALL ON SCHEMA financ
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 1394** (sql):

```sql
-- 基于行为的入侵检测
CREATE OR REPLACE FUNCTION detect_intrusion()
RETURNS TABLE (
    threat_level TEXT,
    user_name TEXT,
    client_addr INET,
    threat_description TEXT,
    evidence JSONB

) AS $$
BEGI
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 24-全文检索深度实战.md

**行 49** (sql):

```sql
CREATE TABLE documents (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    search_vector tsvector
);

-- 生成搜索向量

UPDATE documents
SET search_vector =
    setweight(to_tsvector('engli
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 197** (sql):

```sql
CREATE TABLE multilang_docs (
    doc_id SERIAL PRIMARY KEY,
    title_en TEXT,
    content_en TEXT,
    title_zh TEXT,
    content_zh TEXT,

    search_vector_en tsvector,
    search_vector_zh tsvecto
```

**问题**:

- 添加事务错误处理和回滚

---

**行 277** (sql):

```sql
-- 搜索词表
CREATE TABLE search_terms (
    term VARCHAR(100) PRIMARY KEY,
    frequency INT DEFAULT 0,
    last_searched TIMESTAMPTZ DEFAULT now()
);

-- 记录搜索

INSERT INTO search_terms (term, frequency)
V
```

**问题**:

- 添加数据操作错误处理

---

### 24-容灾与高可用架构设计指南.md

**行 111** (sql):

```sql
-- === 发布端配置 ===

-- 1. 创建发布
CREATE PUBLICATION prod_publication FOR ALL TABLES;

-- 或选择性发布
CREATE PUBLICATION orders_publication

FOR TABLE orders, order_items, customers
WITH (publish = 'insert,updat
```

**问题**:

- 添加数据操作错误处理

---

**行 175** (bash):

```bash
#!/bin/bash
# test_parallel_streaming.sh
# 测试并行流式复制性能

DB_PRIMARY="host=primary dbname=testdb user=replicator"
DB_SUBSCRIBER="host=subscriber dbname=testdb user=postgres"

echo "=== PostgreSQL 18 并行流式
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 323** (bash):

```bash
#!/bin/bash
# setup_streaming_replica.sh

PRIMARY_HOST="192.168.1.10"
REPLICA_DATA_DIR="/var/lib/postgresql/18/main"
REPLICA_HOST="192.168.1.11"

echo "=== 配置流复制副本 ==="

# 1. 停止副本上的PostgreSQL
sudo sys
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 491** (bash):

```bash
#!/bin/bash
# test_failover.sh
# 测试Patroni自动故障切换

PRIMARY_NODE="postgres01"
STANDBY_NODE="postgres02"

echo "=== Patroni故障切换测试 ==="

# 1. 检查集群状态
echo "【1/7】集群状态检查..."
patronictl -c /etc/patroni/patron
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 619** (sql):

```sql
-- 自动清理空闲复制槽
CREATE OR REPLACE FUNCTION cleanup_inactive_slots()
RETURNS TABLE (
    dropped_slot TEXT,
    reason TEXT
) AS $$
DECLARE
    slot RECORD;

    inactive_duration INTERVAL;
BEGIN
    FOR s
```

**问题**:

- 添加事务错误处理和回滚

---

**行 691** (sql):

```sql
-- 配置冲突解决策略
ALTER SUBSCRIPTION my_subscription SET (
    -- ✅ PG18新增选项
    disable_on_error = false,  -- 遇到错误不禁用订阅

    -- 冲突解决策略（未来版本）
    -- conflict_resolution = 'apply_remote'  -- 使用远程数据

    -- co
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 836** (bash):

```bash
#!/bin/bash
# continuous_archiving.sh

ARCHIVE_DIR="/backup/wal_archive"
S3_BUCKET="s3://postgres-dr-backup"

# 1. 配置WAL归档
cat >> /etc/postgresql/18/main/postgresql.conf <<EOF

# 持续归档配置
archive_mode =
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 894** (bash):

```bash
#!/bin/bash
# disaster_recovery_drill.sh
# 完整的灾难恢复演练

BACKUP_DATE="20251204"
RECOVERY_TARGET_TIME="2025-12-04 10:30:00"

echo "=== PostgreSQL 18 灾难恢复演练 ==="

# 1. 停止PostgreSQL
sudo systemctl stop post
```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 25-性能基准测试与调优实战指南.md

**行 125** (bash):

```bash
#!/bin/bash
# setup_tpcc.sh

# 1. 安装benchmarksql
git clone https://github.com/petergeoghegan/benchmarksql.git
cd benchmarksql
ant

# 2. 配置测试参数

cat > run/props.pg <<EOF
db=postgres
driver=org.postgresq
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 206** (bash):

```bash
#!/bin/bash
# run_tpch_benchmark.sh

SCALE_FACTOR=100  # 100GB数据集
QUERY_DIR="./tpch_queries"
RESULTS_DIR="./tpch_results"


echo "=== TPC-H SF${SCALE_FACTOR} 基准测试 ==="

# 1. 生成数据
./dbgen -s $SCALE_FACT
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 303** (bash):

```bash
#!/bin/bash
# pgbench_comprehensive_test.sh


DB_NAME="pgbench_test"
SCALE=10000  # 约150GB数据

echo "=== pgbench综合压测 ==="

# 1. 初始化数据
echo "【1/6】初始化数据（Scale=$SCALE）..."
pgbench -i -s $SCALE -F 90 $DB_NA
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 373** (sql):

```sql
-- custom_workload.sql
-- 模拟真实电商场景


\set customer_id random(1, 10000000)
\set product_id random(1, 100000)
\set quantity random(1, 10)

BEGIN;

-- 1. 查询商品信息（30%）
SELECT * FROM products
WHERE product_i
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 425** (bash):

```bash

#!/bin/bash
# sysbench_postgres_test.sh

DB_HOST="localhost"
DB_PORT=5432
DB_NAME="sysbench"
DB_USER="postgres"
DB_PASSWORD="postgres"

TABLE_SIZE=10000000  # 1000万行
TABLES=16  # 16个表
THREADS=64

echo
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 532** (sql):

```sql

-- 秒杀压测脚本
-- spike_test.sql

\set product_id 12345
\set user_id random(1, 10000000)

-- 模拟秒杀抢购
BEGIN;

-- 1. 检查库存（SELECT FOR UPDATE）
SELECT stock, version
FROM products
WHERE product_id = :product_id

```

**问题**:

- 添加事务错误处理和回滚

- 添加数据操作错误处理

---

**行 585** (sql):

```sql
-- iot_insert_test.sql
-- 模拟IoT设备高频写入

\set device_id random(1, 100000)
\set metric_value random(0, 1000)

INSERT INTO sensor_data (device_id, timestamp, value, quality)
VALUES (
    :device_id,
    n
```

**问题**:

- 添加数据操作错误处理

---

**行 632** (sql):

```sql
-- 分析工作负载类型
WITH workload_stats AS (
    SELECT
        SUM(calls) FILTER (WHERE query LIKE 'SELECT%' AND query NOT LIKE '%FOR UPDATE%') AS select_count,
        SUM(calls) FILTER (WHERE query LIKE 'I
```

**问题**:

- 添加数据操作错误处理

---

**行 804** (bash):

```bash
#!/bin/bash

# perf_profile_postgres.sh
# 使用Linux perf工具剖析PostgreSQL

PG_PID=$(pgrep -f "postgres.*client backend" | head -1)

echo "=== PostgreSQL 18性能剖析 ==="
echo "目标进程: $PG_PID"

# 1. CPU火焰图
echo "【
```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 26-并行查询深度优化.md

**行 188** (sql):

```sql
-- 测试不同并行度
DO $$
DECLARE
    workers INT;
    start_time TIMESTAMPTZ;
    duration INTERVAL;
BEGIN
    FOR workers IN 1..8 LOOP
        EXECUTE format('SET max_parallel_workers_per_gather = %s', worke
```

**问题**:

- 添加事务错误处理和回滚

---

### 26-扩展开发与插件生态指南.md

**行 221** (bash):

```bash
# 编译
make

# 安装
sudo make install

# 创建扩展
psql -d testdb -c "CREATE EXTENSION my_extension;"

# 测试
psql -d testdb -c "SELECT add_numbers(10, 20);"
-- 输出：30

psql -d testdb -c "SELECT concat_with_prefi
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 295** (sql):

```sql
-- 技巧1：使用RETURNS TABLE替代OUT参数
-- ❌ 低效
CREATE OR REPLACE FUNCTION get_user_orders_slow(
    p_user_id INT,
    OUT order_count INT,
    OUT total_amount NUMERIC
)
AS $$
BEGIN
    SELECT COUNT(*), SUM(t
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 489** (sql):

```sql
-- Citus：将PostgreSQL转为分布式数据库
CREATE EXTENSION citus;

-- 配置Worker节点（Coordinator节点执行）
SELECT citus_add_node('worker1.example.com', 5432);
SELECT citus_add_node('worker2.example.com', 5432);

-- 创建分布式表

```

**问题**:

- 添加数据操作错误处理

---

**行 812** (sql):

```sql
-- 安装pg_cron
CREATE EXTENSION pg_cron;

-- 定时任务：每天凌晨2点清理旧数据
SELECT cron.schedule(
    'cleanup-old-data',
    '0 2 * * *',  -- cron表达式
    $$
    DELETE FROM logs WHERE created_at < now() - INTERVAL '

```

**问题**:

- 添加数据操作错误处理

---

**行 1083** (sql):

```sql
-- 扩展版本管理
-- my_extension--1.0.sql （初始版本）
-- my_extension--1.0--1.1.sql （升级脚本）
-- my_extension--1.1--1.2.sql

-- 升级扩展
ALTER EXTENSION my_extension UPDATE TO '1.2';

-- 查看扩展版本
SELECT
    extname,

    e
```

**问题**:

- 添加数据操作错误处理

---

**行 1117** (sql):

```sql
-- 创建升级脚本：my_extension--1.0--1.1.sql
-- 添加新函数
CREATE OR REPLACE FUNCTION new_feature()
RETURNS TEXT AS $$
BEGIN
    RETURN 'Version 1.1 feature';

END;
$$ LANGUAGE plpgsql;

-- 修改现有函数
CREATE OR REPLACE
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 27-分区表深度实战.md

**行 50** (sql):

```sql
-- 均匀分布大表
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(100)

) PARTITION BY HASH (user_id);

-- 创建8个分区
DO $$
BEGIN
    FOR i IN 0..7 LOOP
        EXECUTE format('

```

**问题**:

- 添加事务错误处理和回滚

---

**行 111** (sql):

```sql
-- 使用pg_partman扩展
CREATE EXTENSION pg_partman;

-- 配置自动分区
SELECT partman.create_parent(
    p_parent_table := 'public.logs',
    p_control := 'created_at',
    p_type := 'native',
    p_interval := 'd
```

**问题**:

- 添加数据操作错误处理

---

### 27-多模态数据库能力指南.md

**行 153** (sql):

```sql
-- JSON vs JSONB
CREATE TABLE json_test (
    id SERIAL PRIMARY KEY,
    data_json JSON,
    data_jsonb JSONB
);

-- 插入相同数据
INSERT INTO json_test (data_json, data_jsonb)
VALUES (
    '{"name": "Alice"
```

**问题**:

- 添加数据操作错误处理

---

**行 328** (sql):

```sql
-- 安装pgvector
CREATE EXTENSION vector;

-- 创建向量表
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536)  -- OpenAI ada-002维度
);

-- 插入向量数据
INSERT INTO embedd
```

**问题**:

- 添加数据操作错误处理

---

**行 370** (sql):

```sql
-- 创建测试表（100万向量）
CREATE TABLE vectors_test (
    id SERIAL PRIMARY KEY,
    embedding vector(384)  -- 降维模型，提高测试速度
);

INSERT INTO vectors_test (embedding)

SELECT
    array_to_string(
        ARRAY(SEL
```

**问题**:

- 添加数据操作错误处理

---

**行 467** (sql):

```sql
-- 1. 创建知识库表
CREATE TABLE knowledge_base (
    doc_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()

);

```

**问题**:

- 添加事务错误处理和回滚

---

**行 694** (sql):

```sql
-- 安装TimescaleDB
CREATE EXTENSION timescaledb;

-- 创建普通表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INT,
    temperature NUMERIC,

    humidity NUMERIC
);

-- 转换为Hypertable
```

**问题**:

- 添加数据操作错误处理

---

**行 823** (sql):

```sql
-- 安装PostGIS
CREATE EXTENSION postgis;

-- 创建空间表

CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(Point, 4326),  -- WGS 84坐标系
    address TEXT
);

-- 插入地理位
```

**问题**:

- 添加数据操作错误处理

---

**行 878** (sql):

```sql
-- 案例：外卖配送距离计算

CREATE TABLE restaurants (
    restaurant_id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOMETRY(Point, 4326)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    restaur
```

**问题**:

- 添加事务错误处理和回滚

---

**行 1182** (sql):

```sql
-- 1. 知识库表（向量+JSON元数据）
CREATE TABLE knowledge_articles (
    article_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding vector(1536),
    metadata JSONB,  -- {category, tags, autho
```

**问题**:

- 添加事务错误处理和回滚

---

**行 1316** (sql):

```sql
-- IoT设备监控平台

-- 1. 设备表（关系型 + 空间）
CREATE TABLE devices (
    device_id SERIAL PRIMARY KEY,
    device_name TEXT,
    device_type TEXT,
    location GEOMETRY(Point, 4326),
    metadata JSONB
);

CREATE
```

**问题**:

- 添加数据操作错误处理

---

### 28-云原生存储引擎适配指南.md

**行 417** (sql):

```sql
-- 回到任意时间点（无需PITR）
neonctl branches create --name debug_branch --parent main --timestamp '2024-12-04 10:00:00'

-- 连接到历史时间点分支
psql postgresql://...@debug_branch.neon.tech/mydb
SELECT * FROM orders WHE
```

**问题**:

- 添加连接错误处理

---

**行 443** (bash):

```bash

# 完整的Neon工作流

# 1. 创建项目
neonctl projects create --name my-project

# 2. 主分支（生产）
neonctl branches list
# main (primary)

# 3. 创建开发分支
neonctl branches create --name dev --parent main

# 4. 开发分支测试（破坏性操作）
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 829** (bash):

```bash
# 多区域灾备（Aurora示例）

# 主区域：us-east-1
aws rds create-db-cluster \
    --db-cluster-identifier aurora-primary \
    --engine aurora-postgresql \
    --engine-version 18.0 \
    --master-username postgres
```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 28-表空间与存储管理.md

**行 38** (sql):

```sql
-- 热数据（NVMe SSD）
CREATE TABLESPACE hot_storage LOCATION '/mnt/nvme';

-- 温数据（SATA SSD）
CREATE TABLESPACE warm_storage LOCATION '/mnt/ssd';

-- 冷数据（HDD）
CREATE TABLESPACE cold_storage LOCATION '/mnt/hd
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 29-pg_cron定时任务实战.md

**行 5** (bash):

```bash
# 安装pg_cron
sudo apt install postgresql-18-cron

# 配置
echo "shared_preload_libraries = 'pg_cron'" | \
  sudo tee -a /etc/postgresql/18/main/postgresql.conf

echo "cron.database_name = 'postgres'" | \

```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 29** (sql):

```sql
-- 每天凌晨2点VACUUM
SELECT cron.schedule('nightly-vacuum', '0 2 * * *', 'VACUUM ANALYZE;');

-- 每小时清理旧日志
SELECT cron.schedule('cleanup-logs', '0 * * * *',
    'DELETE FROM logs WHERE created_at < now() -
```

**问题**:

- 添加数据操作错误处理

---

**行 81** (sql):

```sql
-- 数据归档任务
SELECT cron.schedule('archive-old-orders', '0 1 * * *', $$
    INSERT INTO orders_archive
    SELECT * FROM orders
    WHERE created_at < CURRENT_DATE - INTERVAL '365 days';

    DELETE FROM
```

**问题**:

- 添加数据操作错误处理

---

**行 106** (sql):

```sql
-- 创建维护存储过程
CREATE OR REPLACE PROCEDURE maintenance_routine()
LANGUAGE plpgsql AS $$

BEGIN
    -- 1. VACUUM
    VACUUM ANALYZE;

    -- 2. 更新统计
    ANALYZE;

    -- 3. 清理日志
    DELETE FROM logs WHERE
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 137** (sql):

```sql
-- 自动创建分区函数
CREATE OR REPLACE FUNCTION auto_create_partitions()
RETURNS VOID AS $$
DECLARE
    target_date DATE;
    partition_name TEXT;
BEGIN
    -- 创建未来7天的分区
    FOR i IN 0..6 LOOP
        target_d
```

**问题**:

- 添加事务错误处理和回滚

---

**行 182** (sql):

```sql
-- 创建备份函数
CREATE OR REPLACE FUNCTION backup_database()
RETURNS VOID AS $$
DECLARE
    backup_file TEXT;
BEGIN
    backup_file := '/backup/db_' || to_char(now(), 'YYYYMMDD_HH24MISS') || '.sql';

    --
```

**问题**:

- 添加事务错误处理和回滚

---

**行 209** (sql):

```sql
-- 记录性能指标
CREATE TABLE performance_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    recorded_at TIMESTAMPTZ DEFAULT now()
);

-- 定时采集
SELECT c
```

**问题**:

- 添加数据操作错误处理

---

### 30-pg_stat_statements性能分析.md

**行 120** (sql):

```sql
-- 查询类型分布
SELECT
    CASE
        WHEN query LIKE 'SELECT%' THEN 'SELECT'
        WHEN query LIKE 'INSERT%' THEN 'INSERT'
        WHEN query LIKE 'UPDATE%' THEN 'UPDATE'
        WHEN query LIKE 'DELET
```

**问题**:

- 添加数据操作错误处理

---

**行 191** (sql):

```sql
-- 创建报告表
CREATE TABLE daily_query_reports (
    report_id BIGSERIAL PRIMARY KEY,
    report_date DATE,
    top_slow_queries JSONB,
    top_frequent_queries JSONB,
    cache_hit_summary JSONB,
    gene
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 31-连接管理深度优化.md

**行 104** (python):

```python
# Python: SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@localhost/mydb',
    poolclass=QueuePool,
    pool_
```

**问题**:

- 添加try-except错误处理

---

### 32-查询计划缓存优化.md

**行 32** (python):

```python
import psycopg2
import time

conn = psycopg2.connect("dbname=mydb")
cursor = conn.cursor()

# 不使用prepared statement

start = time.time()
for i in range(1000):
    cursor.execute("SELECT * FROM users WH
```

**问题**:

- 添加try-except错误处理

---

### 33-批量操作性能优化.md

**行 7** (python):

```python
import psycopg2
import time


conn = psycopg2.connect("dbname=test")
cursor = conn.cursor()

# 方法1: 单条INSERT（最慢）
start = time.time()
for i in range(10000):
    cursor.execute("INSERT INTO test (id, dat
```

**问题**:

- 添加try-except错误处理

---

**行 47** (sql):

```sql

-- 单条（慢）
INSERT INTO users (username, email) VALUES ('user1', 'user1@example.com');
INSERT INTO users (username, email) VALUES ('user2', 'user2@example.com');

-- 批量（快）
INSERT INTO users (username, em
```

**问题**:

- 添加数据操作错误处理

---

**行 69** (sql):

```sql
-- 批量UPDATE
UPDATE products p

SET price = v.new_price
FROM (VALUES
    (1, 99.99),
    (2, 149.99),
    (3, 199.99),
    (4, 249.99)
) AS v(product_id, new_price)
WHERE p.product_id = v.product_id;

-
```

**问题**:

- 添加数据操作错误处理

---

**行 87** (sql):

```sql
-- 大批量UPDATE（>1000行）
CREATE TEMP TABLE updates_temp (
    product_id INT,
    new_price NUMERIC
);


-- 批量导入
COPY updates_temp FROM '/tmp/price_updates.csv' WITH CSV;

-- 批量更新
UPDATE products p
SET pri
```

**问题**:

- 添加数据操作错误处理

---

**行 112** (sql):

```sql
-- 避免长事务和锁
DO $$
DECLARE
    deleted INT;
    total INT := 0;
BEGIN
    LOOP
        DELETE FROM logs
        WHERE created_at < CURRENT_DATE - INTERVAL '90 days'
          AND ctid = ANY(

```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 149** (sql):

```sql
-- DELETE: 逐行删除，生成WAL，可回滚
DELETE FROM large_table;
-- 时间: 120秒

-- TRUNCATE: 快速清空，极少WAL，不可回滚
TRUNCATE TABLE large_table;
-- 时间: 0.5秒 (-99.6%)

-- TRUNCATE级联
TRUNCATE TABLE parent_table CASCADE;
-- 同时清
```

**问题**:

- 添加数据操作错误处理

---

**行 202** (sql):

```sql
-- 批量插入或更新
INSERT INTO inventory (product_id, stock, updated_at)
VALUES
    (1, 100, now()),
    (2, 200, now()),
    (3, 300, now())
ON CONFLICT (product_id)
DO UPDATE SET
    stock = inventory.stock
```

**问题**:

- 添加数据操作错误处理

---

**行 219** (sql):

```sql
MERGE INTO inventory t
USING (VALUES
    (1, 100),
    (2, 200),
    (3, 300)
) AS s(product_id, stock_delta)
ON t.product_id = s.product_id
WHEN MATCHED THEN
    UPDATE SET stock = t.stock + s.stock_
```

**问题**:

- 添加数据操作错误处理

---

**行 239** (python):

```python
from concurrent.futures import ThreadPoolExecutor
import psycopg2

def insert_batch(batch_id, batch_data):
    """单个批次插入"""
    conn = psycopg2.connect("dbname=mydb")
    cursor = conn.cursor()

    f
```

**问题**:

- 添加try-except错误处理

---

### 36-SQL注入防御完整指南.md

**行 7** (python):

```python
# ❌ 危险代码
username = request.GET['username']
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

# 攻击payload:
# username = "admin' OR '1'='1"
# 生成SQL: SELECT * FROM user
```

**问题**:

- 添加try-except错误处理

---

**行 30** (python):

```python
# ✅ 正确方式：参数化查询
username = request.GET['username']
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)  # 参数作为tuple传递
)

# psycopg2自动转义，无论输入什么都安全
# username = "admin' OR '1'=
```

**问题**:

- 添加try-except错误处理

---

**行 100** (python):

```python
# ✅ 安全：ORM查询
session.query(User).filter(User.username == username).all()

# ✅ 安全：text() with bindparams
from sqlalchemy import text
session.execute(
    text("SELECT * FROM users WHERE username = :use
```

**问题**:

- 添加try-except错误处理

---

**行 139** (python):

```python
# ❌ 部分防御
keyword = request.GET['keyword']
cursor.execute(
    "SELECT * FROM products WHERE name LIKE %s",
    (f"%{keyword}%",)  # 参数化了，但...
)

# 攻击: keyword = "%"
# 返回所有记录（DoS攻击）

# ✅ 完整防御
keyword =
```

**问题**:

- 添加try-except错误处理

---

**行 165** (python):

```python
# ❌ 危险
page = request.GET['page']
query = f"SELECT * FROM users LIMIT 20 OFFSET {page * 20}"

# ✅ 安全：强制类型转换
page = int(request.GET['page'])  # 抛出ValueError如果非整数
if page < 0 or page > 10000:
    page =
```

**问题**:

- 添加try-except错误处理

---

**行 187** (python):

```python
# 场景1: 注册 → 存储（第一步）
username = "admin'--"
cursor.execute(
    "INSERT INTO users (username) VALUES (%s)",
    (username,)  # 安全存储了 "admin'--"
)

# 场景2: 读取 → 使用（第二步，危险）
cursor.execute("SELECT username
```

**问题**:

- 添加try-except错误处理

---

**行 218** (sql):

```sql
-- 应用账号：只授予必要权限
CREATE ROLE app_user LOGIN PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
-- 不授予DELETE, DROP等危险权限

-- 只读账号
C
```

**问题**:

- 添加连接错误处理
- 添加数据操作错误处理

---

**行 233** (sql):

```sql
-- 使用SECURITY DEFINER函数
CREATE OR REPLACE FUNCTION safe_get_user(p_username TEXT)
RETURNS TABLE(id INT, username TEXT, email TEXT)
SECURITY DEFINER
LANGUAGE plpgsql AS $$
BEGIN
    -- 函数内部控制查询逻辑
    R
```

**问题**:

- 添加事务错误处理和回滚

---

### 37-JSON-JSONB完整实战.md

**行 5** (sql):

```sql
-- JSON: 文本存储，保留格式
CREATE TABLE logs_json (
    id SERIAL PRIMARY KEY,
    data JSON
);

-- JSONB: 二进制存储，支持索引
CREATE TABLE logs_jsonb (
    id SERIAL PRIMARY KEY,

    data JSONB
);

-- 性能对比
INSERT INT
```

**问题**:

- 添加数据操作错误处理

---

**行 47** (sql):

```sql
-- 插入JSON数据
INSERT INTO users (id, info) VALUES
(1, '{"name": "Alice", "age": 30, "tags": ["admin", "user"]}'),
(2, '{"name": "Bob", "age": 25, "email": "bob@example.com"}');


-- 从函数构建
INSERT INTO use
```

**问题**:

- 添加数据操作错误处理

---

**行 93** (sql):

```sql
-- 更新整个字段
UPDATE users
SET info = '{"name": "Alice Updated", "age": 31}'
WHERE id = 1;

-- 更新单个键
UPDATE users
SET info = jsonb_set(info, '{age}', '31')
WHERE id = 1;

-- 添加新键
UPDATE users
SET info = i
```

**问题**:

- 添加数据操作错误处理

---

**行 249** (sql):

```sql
CREATE TABLE event_logs (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 索引
CREATE INDEX idx_event_type ON event_logs(e
```

**问题**:

- 添加数据操作错误处理

---

**行 281** (sql):

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    attributes JSONB
);

-- 不同产品有不同属性
INSERT INTO products (name, attributes) VALUES
('Laptop', '{"brand": "Dell", "cpu": "Int

```

**问题**:

- 添加数据操作错误处理

---

**行 310** (sql):

```sql
CREATE TABLE user_settings (
    user_id INT PRIMARY KEY,
    settings JSONB DEFAULT '{}'
);

-- 默认配置
INSERT INTO user_settings (user_id, settings) VALUES
(1, '{
    "theme": "dark",
    "language": "
```

**问题**:

- 添加数据操作错误处理

---

**行 358** (sql):

```sql
-- 1. 使用jsonb_path_ops索引（查询简单时）
CREATE INDEX idx_fast ON logs USING GIN (data jsonb_path_ops);

-- 2. 提取常用字段
ALTER TABLE logs ADD COLUMN user_id INT;
UPDATE logs SET user_id = (data->>'user_id')::INT;
```

**问题**:

- 添加数据操作错误处理

---

### 38-CTE与递归查询完全指南.md

**行 57** (sql):

```sql
-- 组织表
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT REFERENCES employees(id),
    title VARCHAR(100)
);

INSERT INTO employees (id, name, manager_id, t
```

**问题**:

- 添加数据操作错误处理

---

### 39-外键与约束完全实战.md

**行 7** (sql):

```sql
-- 创建表时定义
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200),
```

**问题**:

- 添加数据操作错误处理

---

**行 42** (sql):

```sql
-- CASCADE: 级联删除
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

DELETE FROM users WHERE id = 1;
-- 同时删除该用户的所有订单

```

**问题**:

- 添加数据操作错误处理

---

**行 93** (sql):

```sql
-- 主键更新时级联更新外键
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


UPDATE users SET
```

**问题**:

- 添加数据操作错误处理

---

**行 111** (sql):

```sql
-- 员工-经理关系
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT,
    FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL
);


INSERT INTO emplo
```

**问题**:

- 添加数据操作错误处理

---

**行 212** (sql):

```sql
-- 单列唯一
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(50) UNIQUE NOT NULL
);


-- 多列唯一（组合唯一）
CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,

```

**问题**:

- 添加数据操作错误处理

---

**行 250** (sql):

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT  --
```

**问题**:

- 添加数据操作错误处理

---

**行 274** (sql):

```sql
-- 延迟约束（事务结束时检查）
CREATE TABLE employees (

    id INT PRIMARY KEY,
    manager_id INT,
    FOREIGN KEY (manager_id) REFERENCES employees(id)
        DEFERRABLE INITIALLY DEFERRED
);

-- 场景：交换两个员工的ID
BE
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 302** (sql):

```sql

-- 防止时间重叠
CREATE EXTENSION btree_gist;

CREATE TABLE room_bookings (
    id SERIAL PRIMARY KEY,
    room_id INT,
    booked_range tstzrange,
    EXCLUDE USING gist (
        room_id WITH =,
        bo
```

**问题**:

- 添加数据操作错误处理

---

**行 333** (sql):

```sql
-- 外键索引

-- PostgreSQL不会自动为外键创建索引
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ❌ 慢：查询某用户的所有帖子
SELECT * FROM posts WHERE user_id
```

**问题**:

- 添加数据操作错误处理

---

### 40-PostgreSQL18新特性总结.md

**行 302** (bash):

```bash

# 1. 检查兼容性
pg_upgrade --check

# 2. 备份
pg_basebackup -D /backup/pg17

# 3. 测试升级
pg_upgrade --test

# 4. 执行升级
pg_upgrade --link

# 5. 分析
vacuumdb --all --analyze-in-stages

# 6. 配置新特性
psql -c "ALTER SY
```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 41-PostgreSQL开发者速查表.md

**行 125** (sql):

```sql
-- INSERT
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- 批量INSERT
INSERT INTO users (name, email) VALUES
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.co
```

**问题**:

- 添加数据操作错误处理

---

**行 157** (sql):

```sql
-- 创建用户
CREATE USER app_user WITH PASSWORD 'strong_password';

-- 创建角色
CREATE ROLE readonly;

-- 授权
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

**问题**:

- 添加连接错误处理

---

**行 312** (bash):

```bash
# 逻辑备份
pg_dump mydb > backup.sql
pg_dump -Fc mydb > backup.dump  # 压缩

# 恢复
psql mydb < backup.sql
pg_restore -d mydb backup.dump

# 只备份schema
pg_dump --schema-only mydb > schema.sql

# 只备份数据
pg_dump

```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 41-实时数据库完全指南.md

**行 75** (sql):

```sql
-- 创建通知函数
CREATE OR REPLACE FUNCTION notify_order_change()
RETURNS TRIGGER AS $$
BEGIN
    -- 发送通知
    PERFORM pg_notify(
        'order_events',

        json_build_object(
            'action', TG_OP
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 138** (sql):

```sql
-- 订单表
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,

    total_amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT no
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 306** (sql):

```sql
-- 消息表
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    room_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 通知函数
C
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 341** (python):

```python
def join_room(room_id: int):
    """加入聊天室"""


    cursor.execute(f"LISTEN room_{room_id};")
    print(f"✓ 加入房间 {room_id}")

def leave_room(room_id: int):
    """离开聊天室"""

    cursor.execute(f"UNLISTEN
```

**问题**:

- 添加try-except错误处理

---

**行 357** (sql):

```sql

-- 缓存失效通知
CREATE OR REPLACE FUNCTION notify_cache_invalidation()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'cache_invalidation',
        json_build_object(
            'table', TG_TAB
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 411** (sql):

```sql
-- 批量通知（避免每行触发）

CREATE OR REPLACE FUNCTION notify_batch_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- 只在事务结束时通知
    PERFORM pg_notify(
        'batch_changes',
        json_build_object(
            't
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 438** (sql):

```sql
-- 只在重要变更时通知
CREATE OR REPLACE FUNCTION notify_important_changes()
RETURNS TRIGGER AS $$

BEGIN
    -- 只有状态变更时通知
    IF NEW.status != OLD.status THEN
        PERFORM pg_notify('order_status_changes',

```

**问题**:

- 添加事务错误处理和回滚

---

**行 494** (sql):

```sql
   BEGIN;
   INSERT INTO orders VALUES (...);
   -- 通知在COMMIT后才发送
   COMMIT;

```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 515** (python):

```python
   import time

   last_notify_time = time.time()

   while True:
       # 10秒超时
       if select.select([conn], [], [], 10) == ([], [], []):
           # 发送心跳查询
           cursor.execute("SELECT 1;")
```

**问题**:

- 添加try-except错误处理

---

**行 554** (sql):

```sql
-- 统计表
CREATE TABLE dashboard_stats (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL,
    metric_value NUMERIC NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 更新触发器
CREAT
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 652** (sql):

```sql
-- 通知统计（需要自定义）
CREATE TABLE notify_stats (
    channel_name VARCHAR(100),
    notify_count BIGINT,
    last_notify TIMESTAMPTZ
);

-- 在通知函数中记录
UPDATE notify_stats
SET notify_count = notify_count + 1,

```

**问题**:

- 添加数据操作错误处理

---

### 42-PostgreSQL故障排查手册.md

**行 48** (bash):

```bash
# Step 1: 检查服务状态
systemctl status postgresql
pg_isready -h localhost -p 5432

# Step 2: 检查监听
netstat -tlnp | grep 5432
ss -tlnp | grep 5432

# Step 3: 检查配置
grep listen_addresses /etc/postgresql/18/mai
```

**问题**:

- 添加错误检查（set -e或if语句）

---

**行 335** (bash):

```bash
#!/bin/bash
# quick-diagnose.sh - 快速诊断脚本

echo "PostgreSQL快速诊断"
echo "===================="

# 1. 服务状态
echo -e "\n1. 服务状态:"
systemctl status postgresql | grep Active

# 2. 连接数
echo -e "\n2. 连接数:"
psql
```

**问题**:

- 添加错误检查（set -e或if语句）

---

### 42-全文搜索深度实战.md

**行 88** (sql):

```sql
-- 添加tsvector列
ALTER TABLE articles ADD COLUMN tsv tsvector;

-- 生成tsvector
UPDATE articles SET tsv =
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''));

-- 创建GIN索引（性能关键！
```

**问题**:

- 添加数据操作错误处理

---

**行 106** (sql):

```sql
-- 触发器函数
CREATE OR REPLACE FUNCTION articles_tsv_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tsv := to_tsvector('english',
        coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, '')
    );

```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 131** (sql):

```sql
-- 不同字段不同权重
UPDATE articles SET tsv =
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(content, '')), 'B');

-- 查询时考虑权重
SELECT
    id,

```

**问题**:

- 添加数据操作错误处理

---

**行 321** (sql):

```sql
-- 创建带中文的文章表
CREATE TABLE cn_articles (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tsv tsvector
);

-- 触发器（中文）
CREATE OR REPLACE FUNCTION cn_articles_tsv_tri
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 363** (sql):

```sql
-- 检测语言并使用相应配置
CREATE OR REPLACE FUNCTION detect_language(text TEXT)
RETURNS regconfig AS $$
BEGIN
    -- 简单检测：是否包含中文
    IF text ~ '[\u4e00-\u9fa5]' THEN
        RETURN 'chinese'::regconfig;
    ELSE
```

**问题**:

- 添加事务错误处理和回滚

---

**行 388** (sql):

```sql
-- 完整的博客搜索表
CREATE TABLE blog_posts (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    category VARCHAR(50),
    tags TEXT[],
    pu
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

**行 460** (sql):

```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    brand VARCHAR(100),
    category VARCHAR(100),
    price NUMERIC(10, 2),
    stock INT,
    tsv
```

**问题**:

- 添加事务错误处理和回滚

---

**行 507** (sql):

```sql
-- 文档表（支持多种格式）
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type VARCHAR(20),
    content TEXT,  -- 提取的文本内容
    metadata JSONB,
    uploaded_by BIGINT,

```

**问题**:

- 添加事务错误处理和回滚

---

**行 592** (sql):

```sql
-- 记录搜索日志
CREATE TABLE search_logs (
    id BIGSERIAL PRIMARY KEY,
    query TEXT,
    results_count INT,
    execution_time_ms REAL,
    searched_at TIMESTAMPTZ DEFAULT now()
);

-- 在搜索函数中记录
CREATE O
```

**问题**:

- 添加事务错误处理和回滚
- 添加数据操作错误处理

---

### 43-SQL优化速查手册.md

**行 159** (sql):

```sql
-- ❌ 循环单条INSERT
FOR i IN 1..10000 LOOP
    INSERT INTO users VALUES (i, ...);
END LOOP;
-- 10000次INSERT，慢

-- ✅ 批量VALUES
INSERT INTO users VALUES
(1, ...), (2, ...), (3, ...), ... (10000, ...);
-- 1次I
```

**问题**:

- 添加数据操作错误处理

---
