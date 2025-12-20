# 代码示例运行验证报告

> **生成日期**: 2025年1月
> **扫描结果**: 找到 99 个可能有语法错误的代码示例

---

## 📊 统计信息

- **需要修复的代码示例**: 99 个

## 📋 需要修复的代码示例

### 01-AIO异步IO完整深度指南.md

**行 355** (sql):

```sql
-- 1. 启用AIO（默认on）
SHOW io_direct;  -- 需要设置为'data'或'all'才能使用AIO
ALTER SYSTEM SET io_direct = 'data';  -- 启用direct I/O

-- 2. io_uring队列深度
SHOW io_uring_queue_depth;  -- 默认256
ALTER SYSTEM SET io_uring_
```

**错误**: SELECT语句缺少FROM子句

---

### 02-跳跃扫描Skip-Scan完整指南-改进补充.md

**行 105** (sql):

```sql
-- 启用Skip Scan（默认）
ALTER SYSTEM SET enable_indexskipscan = on;
SELECT pg_reload_conf();

-- 禁用Skip Scan（用于测试对比）
ALTER SYSTEM SET enable_indexskipscan = off;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 139** (sql):

```sql
-- 针对低基数场景优化
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 50;
SELECT pg_reload_conf();

-- 验证配置
SHOW index_skip_scan_cardinality_threshold;

```

**错误**: SELECT语句缺少FROM子句

---

**行 167** (sql):

```sql
-- 针对大表优化
ALTER SYSTEM SET index_skip_scan_min_rows = 5000;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 277** (sql):

```sql
-- 方案1: 确保Skip Scan启用
ALTER SYSTEM SET enable_indexskipscan = on;
SELECT pg_reload_conf();

-- 方案2: 调整基数阈值
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 200;
SELECT pg_reload_conf();

-- 方案
```

**错误**: SELECT语句缺少FROM子句

---

**行 329** (sql):

```sql
-- 方案1: 降低基数阈值
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 50;
SELECT pg_reload_conf();

-- 方案2: 创建单列索引（如果Skip Scan不适用）
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- 方案3:
```

**错误**: SELECT语句缺少FROM子句

---

**行 377** (sql):

```sql
-- 方案1: 删除冗余索引
DROP INDEX IF EXISTS idx_orders_redundant;

-- 方案2: 调整索引顺序
DROP INDEX idx_orders_status_date;
CREATE INDEX idx_orders_status_date ON orders(status, created_at);

-- 方案3: 使用索引提示（PostgreS
```

**错误**: SELECT语句缺少FROM子句

---

**行 493** (sql):

```sql
-- 方法3: 对比启用/禁用Skip Scan
-- 禁用Skip Scan
SET enable_indexskipscan = off;
EXPLAIN ANALYZE SELECT ...;
-- 应该显示 Seq Scan

-- 启用Skip Scan
SET enable_indexskipscan = on;
EXPLAIN ANALYZE SELECT ...;
-- 应该显示
```

**错误**: SELECT语句缺少FROM子句

---

### 02-跳跃扫描Skip-Scan完整指南.md

**行 547** (sql):

```sql
-- 对比启用/禁用Skip Scan
SET enable_indexskipscan = off;  -- 禁用
EXPLAIN ANALYZE SELECT ...;

SET enable_indexskipscan = on;   -- 启用（默认）
EXPLAIN ANALYZE SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 636** (sql):

```sql
-- 启用Skip Scan（默认）
ALTER SYSTEM SET enable_indexskipscan = on;
SELECT pg_reload_conf();

-- 禁用Skip Scan（用于测试对比）
ALTER SYSTEM SET enable_indexskipscan = off;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 663** (sql):

```sql
-- 针对低基数场景优化
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 50;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 737** (sql):

```sql
-- 方案1: 确保Skip Scan启用
ALTER SYSTEM SET enable_indexskipscan = on;
SELECT pg_reload_conf();

-- 方案2: 调整基数阈值
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 200;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 762** (sql):

```sql
-- 方案1: 降低基数阈值
ALTER SYSTEM SET index_skip_scan_cardinality_threshold = 50;
SELECT pg_reload_conf();

-- 方案2: 创建单列索引（如果Skip Scan不适用）
CREATE INDEX idx_orders_created_at ON orders(created_at);

```

**错误**: SELECT语句缺少FROM子句

---

### 03-虚拟生成列完整实战指南.md

**行 152** (sql):

```sql
SELECT
    pg_size_pretty(pg_total_relation_size('test_virtual')) AS virtual_size,
    pg_size_pretty(pg_total_relation_size('test_stored')) AS stored_size;

-- 结果：
-- virtual_size: 65 MB
-- stored_si
```

**错误**: SELECT语句缺少FROM子句

---

**行 217** (sql):

```sql
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    data JSONB,
    -- 复杂聚合计算（昂贵）
    score GENERATED ALWAYS AS (
        calculate_complex_score(data)  -- 自定义函数，计算耗时
    ) STORED;  -- 必须STORED，否则
```

**错误**: 括号不匹配

---

### 04-UUIDv7完整指南-改进补充.md

**行 377** (sql):

```sql
-- 1. 检查UUIDv7格式
SELECT gen_uuid_v7();
-- 应该以018d开头（版本7标识）

-- 2. 检查时间戳提取
SELECT
    gen_uuid_v7() AS uuid,
    uuid_extract_time(gen_uuid_v7()) AS timestamp_ms,
    to_timestamp(uuid_extract_time(gen
```

**错误**: SELECT语句缺少FROM子句

---

### 04-UUIDv7完整指南.md

**行 297** (sql):

```sql
-- 从UUIDv7提取Unix时间戳（毫秒）
uuid_extract_time(uuid) → bigint

-- 示例
SELECT uuid_extract_time('018d2a54-6c1f-7000-8000-123456789abc'::uuid);
-- 输出：1701234567890（Unix毫秒）

-- 转换为时间戳
SELECT to_timestamp(uuid_
```

**错误**: SELECT语句缺少FROM子句

---

**行 783** (sql):

```sql
-- 1. 检查UUIDv7格式
SELECT gen_uuid_v7();
-- 应该以018d开头（版本7标识）

-- 2. 检查时间戳提取
SELECT
    gen_uuid_v7() AS uuid,
    uuid_extract_time(gen_uuid_v7()) AS timestamp_ms,
    to_timestamp(uuid_extract_time(gen
```

**错误**: SELECT语句缺少FROM子句

---

### 05-GIN并行构建完整指南.md

**行 121** (sql):

```sql
-- 1. 最大并行Worker数量（全局）
SHOW max_parallel_maintenance_workers;
-- 默认：2
-- 推荐：4-8（根据CPU核心数）

ALTER SYSTEM SET max_parallel_maintenance_workers = 8;

-- 2. 单个索引构建的Worker数量
SET max_parallel_workers_per_ga
```

**错误**: SELECT语句缺少FROM子句

---

### 06-OAuth2.0认证集成完整指南-改进补充.md

**行 101** (sql):

```sql
-- 方案1: 验证配置
ALTER SYSTEM SET oauth_enabled = on;
ALTER SYSTEM SET oauth_issuer = 'https://accounts.google.com';
ALTER SYSTEM SET oauth_audience = 'your-client-id';
SELECT pg_reload_conf();

-- 方案2: 检
```

**错误**: SELECT语句缺少FROM子句

---

**行 143** (sql):

```sql
-- 方案1: 启用Token自动刷新
ALTER SYSTEM SET oauth_token_refresh_enabled = on;
ALTER SYSTEM SET oauth_token_refresh_threshold = 300;  -- 提前5分钟刷新
SELECT pg_reload_conf();

-- 方案2: 增加Token有效期
-- 在OAuth Provider
```

**错误**: SELECT语句缺少FROM子句

---

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

**错误**: SELECT语句缺少FROM子句

---

**行 209** (sql):

```sql
-- 1. 使用强算法
-- 推荐使用RS256（非对称加密）
-- 避免使用HS256（对称加密，密钥泄露风险）

-- 2. 验证Token签名
ALTER SYSTEM SET oauth_jwt_verify_signature = on;
SELECT pg_reload_conf();

-- 3. 验证Token过期
ALTER SYSTEM SET oauth_token_expi
```

**错误**: SELECT语句缺少FROM子句

---

**行 248** (sql):

```sql
-- 1. 创建最小权限角色
CREATE ROLE oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oauth_readon
```

**错误**: SELECT语句缺少FROM子句

---

**行 374** (sql):

```sql
   ALTER SYSTEM SET oauth_enabled = on;
   ALTER SYSTEM SET oauth_issuer = 'https://oauth-provider.com';
   ALTER SYSTEM SET oauth_audience = 'your-client-id';
   SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 06-OAuth2.0认证集成完整指南.md

**行 184** (sql):

```sql
-- 创建角色
CREATE ROLE google_users;
GRANT CONNECT ON DATABASE mydb TO google_users;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO google_users;

-- 创建用户（自动从Google email创建）
-- PostgreSQL 18会自动根据token中的e
```

**错误**: SELECT语句缺少FROM子句

---

**行 332** (sql):

```sql
-- 创建受限角色
CREATE ROLE oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oauth_readonly;


```

**错误**: SELECT语句缺少FROM子句

---

**行 362** (sql):

```sql
-- 配置Azure AD OAuth
-- postgresql.conf
oauth_enabled = on
oauth_issuer = 'https://login.microsoftonline.com/company-tenant-id/v2.0'
oauth_audience = 'company-pg-client-id'
oauth_jwks_uri = 'https://lo
```

**错误**: SELECT语句缺少FROM子句

---

**行 523** (sql):

```sql
-- 方案1: 验证配置
ALTER SYSTEM SET oauth_enabled = on;
ALTER SYSTEM SET oauth_issuer = 'https://accounts.google.com';
ALTER SYSTEM SET oauth_audience = 'your-client-id';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 540** (sql):

```sql
-- 方案1: 启用Token自动刷新
ALTER SYSTEM SET oauth_token_refresh_enabled = on;
ALTER SYSTEM SET oauth_token_refresh_threshold = 300;  -- 提前5分钟刷新
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 556** (sql):

```sql
-- 方案1: 配置角色映射
ALTER SYSTEM SET oauth_claim_role_mapping = on;
ALTER SYSTEM SET oauth_role_claim = 'groups';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 571** (sql):

```sql
-- 1. 使用强算法
-- 推荐使用RS256（非对称加密）

-- 2. 验证Token签名
ALTER SYSTEM SET oauth_jwt_verify_signature = on;
SELECT pg_reload_conf();

-- 3. 验证Token过期
ALTER SYSTEM SET oauth_token_expiry_check = on;
SELECT pg_r
```

**错误**: SELECT语句缺少FROM子句

---

**行 588** (sql):

```sql
-- 1. 创建最小权限角色
CREATE ROLE oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oauth_readon
```

**错误**: SELECT语句缺少FROM子句

---

**行 679** (sql):

```sql
   ALTER SYSTEM SET oauth_enabled = on;
   ALTER SYSTEM SET oauth_issuer = 'https://oauth-provider.com';
   SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 07-逻辑复制增强完整指南-改进补充.md

**行 118** (sql):

```sql
-- 方案1: 增加Worker数量
ALTER SYSTEM SET max_logical_replication_workers = 8;
ALTER SYSTEM SET max_sync_workers_per_subscription = 4;
SELECT pg_reload_conf();

-- 方案2: 优化网络
-- 使用10Gbps网络
-- 启用WAL压缩

-- 方案3
```

**错误**: SELECT语句缺少FROM子句

---

**行 159** (sql):

```sql
-- 方案1: 启用DDL复制
ALTER SYSTEM SET logical_replication_ddl_replication = on;
SELECT pg_reload_conf();

-- 方案2: 检查发布配置
-- 确保发布包含需要复制的表
ALTER PUBLICATION mypub ADD TABLE new_table;

-- 方案3: 手动同步DDL
-- 如果D
```

**错误**: SELECT语句缺少FROM子句

---

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

**错误**: SELECT语句缺少FROM子句

---

### 07-逻辑复制增强完整指南.md

**行 638** (sql):

```sql
-- 方案1: 增加Worker数量
ALTER SYSTEM SET max_logical_replication_workers = 8;
ALTER SYSTEM SET max_sync_workers_per_subscription = 4;
SELECT pg_reload_conf();

-- 方案2: 优化批量提交
ALTER SYSTEM SET logical_repli
```

**错误**: SELECT语句缺少FROM子句

---

**行 658** (sql):

```sql
-- 方案1: 启用DDL复制
ALTER SYSTEM SET logical_replication_ddl_replication = on;
SELECT pg_reload_conf();

-- 方案2: 检查发布配置
ALTER PUBLICATION mypub ADD TABLE new_table;

```

**错误**: SELECT语句缺少FROM子句

---

**行 676** (sql):

```sql
-- 方案1: 配置冲突解决策略
ALTER SYSTEM SET logical_replication_conflict_resolution = 'last_write_wins';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 08-EXPLAIN增强完整指南.md

**行 160** (sql):

```sql
EXPLAIN (
    ANALYZE,        -- 实际执行
    BUFFERS,        -- 缓冲区统计
    VERBOSE,        -- 详细输出
    TIMING,         -- 时间统计
    MEMORY,         -- ⭐ 内存统计（PG18）
    SERIALIZE,      -- ⭐ 序列化统计（PG18）

```

**错误**: SELECT语句缺少FROM子句

---

### 08-性能调优实战指南.md

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

**错误**: SELECT语句缺少FROM子句

---

### 10-pg_upgrade升级完整指南.md

**行 282** (sql):

```sql
-- 启用AIO
ALTER SYSTEM SET io_direct = 'data';

-- 启用其他PG18特性
ALTER SYSTEM SET max_parallel_maintenance_workers = 8;

-- 重载配置
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

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

**错误**: SELECT语句缺少FROM子句

---

### 12-时态约束与时间段完整性指南.md

**行 120** (sql):

```sql
-- ❌ 传统主键（无法防止时间段冲突）
CREATE TABLE room_booking_old (
    room_id INT,
    booking_date DATE,
    guest_name TEXT,
    PRIMARY KEY (room_id, booking_date)  -- 仅保证每天每房间一个预订
);

-- 问题：同一天可以多个预订，时间段冲突！
IN
```

**错误**: 括号不匹配

---

**行 241** (sql):

```sql
-- 案例：酒店房间预订系统
CREATE TABLE hotel_bookings (
    booking_id SERIAL,
    room_id INT NOT NULL,
    guest_name TEXT NOT NULL,
    check_in TIMESTAMPTZ NOT NULL,
    check_out TIMESTAMPTZ NOT NULL,
    b
```

**错误**: 括号不匹配

---

**行 310** (sql):

```sql
-- 案例：租赁合同管理
CREATE TABLE lease_contracts (
    contract_id SERIAL PRIMARY KEY,
    property_id INT NOT NULL,
    tenant_name TEXT NOT NULL,
    lease_start DATE NOT NULL,
    lease_end DATE NOT NULL,
```

**错误**: 括号不匹配

---

**行 385** (sql):

```sql
-- 父表：员工合同
CREATE TABLE employee_contracts (
    employee_id INT,
    contract_start DATE NOT NULL,
    contract_end DATE NOT NULL,
    position TEXT,
    salary NUMERIC(10,2),

    CONSTRAINT valid_c
```

**错误**: 括号不匹配

---

**行 497** (sql):

```sql
-- 禁止关系：overlaps, overlapped-by, starts, started-by,
--          during, contains, finishes, finished-by, equals

-- 允许关系：before, after, meets, met-by

-- 实例说明
-- Range A: [2025-01-15 08:00, 2025-01-1
```

**错误**: 括号不匹配

---

**行 519** (sql):

```sql
-- PostgreSQL 18使用左闭右开区间（数学标准）
-- Range类型：tstzrange(lower, upper, '[)')

-- 实例
SELECT tstzrange('2025-01-15 10:00', '2025-01-15 12:00');
-- 输出：["2025-01-15 10:00:00+00","2025-01-15 12:00:00+00")

-- 边
```

**错误**: 括号不匹配; SELECT语句缺少FROM子句

---

### 13-存储过程与触发器实战.md

**行 326** (sql):

```sql
CREATE OR REPLACE FUNCTION safe_divide(a NUMERIC, b NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    RETURN a / b;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE '除数为零，返回NULL';
        RETURN N
```

**错误**: SELECT语句缺少FROM子句

---

**行 649** (sql):

```sql
CREATE OR REPLACE FUNCTION debug_function()
RETURNS VOID AS $$
DECLARE
    var1 INT := 100;
BEGIN
    RAISE NOTICE '变量值: %', var1;
    RAISE DEBUG '调试信息';
    RAISE LOG '日志信息';
    RAISE WARNING '警告信息
```

**错误**: SELECT语句缺少FROM子句

---

### 14-并行查询与JIT编译增强指南.md

**行 667** (sql):

```sql
-- 高性能服务器（32核/128GB）
ALTER SYSTEM SET max_parallel_workers_per_gather = 8;
ALTER SYSTEM SET max_parallel_workers = 16;
ALTER SYSTEM SET parallel_setup_cost = 500;  -- 降低门槛
ALTER SYSTEM SET parallel_tu
```

**错误**: SELECT语句缺少FROM子句

---

### 14-数据类型深度解析.md

**行 7** (sql):

```sql
-- 类型选择
SMALLINT    -- 2字节, -32768 to 32767
INTEGER     -- 4字节, -2^31 to 2^31-1
BIGINT      -- 8字节, -2^63 to 2^63-1

-- 自增
SERIAL      -- INTEGER + SEQUENCE
BIGSERIAL   -- BIGINT + SEQUENCE

-- 示例
CRE
```

**错误**: SELECT语句缺少FROM子句

---

**行 323** (sql):

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- UUID生成
SELECT
    uuid_generate_v4() AS v4,      -- 随机UUID
    gen_random_uuid() AS random,   -- 随机（内置）
    uuidv7() AS v7;                -- UU
```

**错误**: SELECT语句缺少FROM子句

---

**行 443** (sql):

```sql
-- 范围类型
int4range     -- INTEGER范围
int8range     -- BIGINT范围
numrange      -- NUMERIC范围
tsrange       -- TIMESTAMP范围
tstzrange     -- TIMESTAMPTZ范围
daterange     -- DATE范围

-- 创建范围
SELECT
    int4rang
```

**错误**: 括号不匹配

---

**行 575** (sql):

```sql
-- 文本转数值
SELECT '123'::INTEGER;
SELECT CAST('123' AS INTEGER);

-- 数值转文本
SELECT 123::TEXT;

-- 日期转换
SELECT '2024-01-01'::DATE;
SELECT to_date('2024-01-01', 'YYYY-MM-DD');

-- JSONB转换
SELECT '{"name":"
```

**错误**: SELECT语句缺少FROM子句

---

### 15-WAL与检查点优化完整指南.md

**行 307** (sql):

```sql
-- 测试不同压缩算法

-- 1. 无压缩（基线）
ALTER SYSTEM SET wal_compression = off;
SELECT pg_reload_conf();

-- 2. pglz压缩（传统，PG 9.5+）
ALTER SYSTEM SET wal_compression = pglz;
SELECT pg_reload_conf();

-- 3. lz4压缩（PG
```

**错误**: SELECT语句缺少FROM子句

---

**行 557** (sql):

```sql
-- 检查点参数

-- 1. 检查点超时时间
SHOW checkpoint_timeout;  -- 默认：5min
-- 推荐：高写入场景15-30min
ALTER SYSTEM SET checkpoint_timeout = '15min';

-- 2. WAL大小触发阈值
SHOW max_wal_size;  -- 默认：1GB
-- 推荐：高写入场景4GB-16GB
ALTER
```

**错误**: SELECT语句缺少FROM子句

---

**行 591** (sql):

```sql
-- 高性能OLTP场景（1000+ TPS）

-- WAL配置
ALTER SYSTEM SET wal_buffers = '128MB';
ALTER SYSTEM SET wal_compression = 'lz4';  -- CPU友好
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET synchronous_commi
```

**错误**: SELECT语句缺少FROM子句

---

### 15-扩展开发完整指南.md

**行 143** (sql):

```sql
-- SQL包装
CREATE OR REPLACE FUNCTION add_numbers(INT, INT)
RETURNS INT AS '$libdir/my_extension', 'add_numbers'
LANGUAGE C IMMUTABLE STRICT;

-- 使用
SELECT add_numbers(10, 20);  -- 30

```

**错误**: SELECT语句缺少FROM子句

---

**行 228** (sql):

```sql
-- SQL定义
CREATE TYPE complex;

CREATE FUNCTION complex_in(cstring)
RETURNS complex AS '$libdir/complex'
LANGUAGE C IMMUTABLE STRICT;

CREATE FUNCTION complex_out(complex)
RETURNS cstring AS '$libdir/c
```

**错误**: SELECT语句缺少FROM子句

---

**行 411** (sql):

```sql
-- 使用pgTAP
CREATE EXTENSION pgtap;

-- 测试脚本
BEGIN;
SELECT plan(5);

SELECT has_function('my_extension', 'hello', ARRAY['text']);
SELECT function_returns('my_extension', 'hello', ARRAY['text'], 'text')
```

**错误**: SELECT语句缺少FROM子句

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

**错误**: 单引号不匹配; SELECT语句缺少FROM子句

---

### 16-统计信息增强与查询规划指南.md

**行 294** (sql):

```sql
-- 大表ANALYZE性能测试
CREATE TABLE huge_table AS
SELECT
    generate_series(1, 100000000) AS id,
    md5(random()::text) AS data,
    (random() * 1000)::int AS value;

-- PostgreSQL 17
\timing on
ANALYZE h
```

**错误**: SELECT语句缺少FROM子句

---

### 18-存储管理与TOAST优化指南.md

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

**错误**: SELECT语句缺少FROM子句

---

**行 964** (sql):

```sql
-- HDD配置（传统）
ALTER SYSTEM SET random_page_cost = 4.0;
ALTER SYSTEM SET seq_page_cost = 1.0;
ALTER SYSTEM SET effective_io_concurrency = 2;

-- SSD配置（推荐）
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER
```

**错误**: SELECT语句缺少FROM子句

---

### 18-并发控制深度解析.md

**行 46** (sql):

```sql
-- 事务快照
SELECT
    txid_current() AS current_xid,
    txid_current_snapshot() AS snapshot;

/*
snapshot格式: xmin:xmax:xip_list
100:105:101,103

xmin=100: 最小活跃事务ID
xmax=105: 下一个分配的事务ID
xip_list: 活跃事务列表

```

**错误**: SELECT语句缺少FROM子句

---

**行 297** (sql):

```sql
-- 终止阻塞会话
SELECT pg_cancel_backend(blocking_pid);   -- 温和取消
SELECT pg_terminate_backend(blocking_pid); -- 强制终止

```

**错误**: SELECT语句缺少FROM子句

---

### 19-分区表增强与智能裁剪指南.md

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

**错误**: 单引号不匹配

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

**错误**: 单引号不匹配

---

### 19-高级SQL查询技巧.md

**行 249** (sql):

```sql
-- 数组操作
SELECT
    ARRAY[1,2,3,4] && ARRAY[3,4,5,6] AS has_overlap,      -- true
    ARRAY[1,2,3,4] @> ARRAY[2,3] AS contains,             -- true
    ARRAY[1,2,3] || ARRAY[4,5] AS concatenate,
```

**错误**: SELECT语句缺少FROM子句

---

### 20-全文检索与排序规则变更指南.md

**行 214** (sql):

```sql
-- PostgreSQL 18新增：casefold()函数
-- 用于大小写不敏感比较

-- 问题场景：德语ß字符
SELECT
    'straße'::text = 'STRASSE'::text AS traditional_compare,
    lower('STRASSE') = 'straße' AS lower_compare,
    casefold('STRASSE
```

**错误**: SELECT语句缺少FROM子句

---

### 21-云原生部署与配置优化指南.md

**行 895** (sql):

```sql
-- 阿里云RDS PostgreSQL 18参数优化

-- 1. AIO配置
ALTER SYSTEM SET io_method = 'worker';  -- 阿里云推荐
ALTER SYSTEM SET effective_io_concurrency = 48;
ALTER SYSTEM SET maintenance_io_concurrency = 48;

-- 2. ESSD性
```

**错误**: SELECT语句缺少FROM子句

---

### 22-TimescaleDB时序数据库完整指南.md

**行 55** (sql):

```sql
-- 创建普通表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INT NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    pressure FLOAT
);

-- 转换为Hypertable
SELECT create_hypertab
```

**错误**: SELECT语句缺少FROM子句

---

### 23-PostGIS地理空间数据库实战.md

**行 382** (sql):

```sql
-- geometry: 平面坐标，快
SELECT ST_Distance(
    ST_MakePoint(116.4, 39.9),
    ST_MakePoint(116.5, 40.0)
);  -- 返回度数

-- geography: 球面坐标，准确
SELECT ST_Distance(
    ST_MakePoint(116.4, 39.9)::geography,

```

**错误**: SELECT语句缺少FROM子句

---

### 24-全文检索深度实战.md

**行 7** (sql):

```sql
-- 文本转向量
SELECT to_tsvector('english', 'PostgreSQL is a powerful database');
-- 结果: 'databas':5 'postgresql':1 'power':4

-- 查询
SELECT to_tsquery('english', 'postgresql & database');
-- 结果: 'postgresq
```

**错误**: SELECT语句缺少FROM子句

---

**行 24** (sql):

```sql
-- 安装zhparser
-- sudo apt install postgresql-18-zhparser

CREATE EXTENSION zhparser;

-- 创建中文配置
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION chinese AD
```

**错误**: SELECT语句缺少FROM子句

---

### 24-容灾与高可用架构设计指南.md

**行 1091** (sql):

```sql
-- RTO优化清单

-- 1. 减少检测时间
ALTER SYSTEM SET wal_receiver_timeout = 5000;  -- 5秒检测
ALTER SYSTEM SET wal_sender_timeout = 5000;

-- 2. 加速故障切换（Patroni配置）
# patroni.yml
bootstrap:
  dcs:
    ttl: 15  -- 缩短T
```

**错误**: SELECT语句缺少FROM子句

---

### 25-性能基准测试与调优实战指南.md

**行 1011** (sql):

```sql
-- 1. 优化分区策略（按天分区）
CREATE TABLE sensor_data (
    device_id INT,
    timestamp TIMESTAMPTZ,
    value NUMERIC,
    PRIMARY KEY (device_id, timestamp)
) PARTITION BY RANGE (timestamp);

-- 2. 使用BRIN索引（
```

**错误**: SELECT语句缺少FROM子句

---

### 26-扩展开发与插件生态指南.md

**行 441** (sql):

```sql
-- 调试技巧1：使用RAISE NOTICE
CREATE OR REPLACE FUNCTION debug_example(p_value INT)
RETURNS INT AS $$
DECLARE
    v_result INT;
BEGIN
    RAISE NOTICE '输入参数: %', p_value;

    v_result := p_value * 2;
    R
```

**错误**: SELECT语句缺少FROM子句

---

**行 610** (sql):

```sql
-- complex--1.0.sql

-- 注册类型
CREATE TYPE complex;

CREATE FUNCTION complex_in(cstring)
RETURNS complex
AS 'MODULE_PATHNAME'
LANGUAGE C IMMUTABLE STRICT;

CREATE FUNCTION complex_out(complex)
RETURNS c
```

**错误**: SELECT语句缺少FROM子句

---

### 27-分区表深度实战.md

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

**错误**: SELECT语句缺少FROM子句

---

### 27-多模态数据库能力指南.md

**行 1082** (sql):

```sql
-- 多模态查询性能调优

-- 1. work_mem调整（向量/排序）
SET work_mem = '256MB';  -- 向量搜索需要更多内存

-- 2. 向量索引参数
SET hnsw.ef_search = 100;  -- 提高召回率

-- 3. 并行查询
SET max_parallel_workers_per_gather = 4;

-- 4. JIT编译
SET jit
```

**错误**: SELECT语句缺少FROM子句

---

### 29-pg_cron定时任务实战.md

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

**错误**: SELECT语句缺少FROM子句

---

### 30-pg_stat_statements性能分析.md

**行 258** (sql):

```sql
-- 重置所有统计
SELECT pg_stat_statements_reset();

-- 重置特定查询
SELECT pg_stat_statements_reset(queryid := 123456789);

-- 定期重置（避免统计过时）
SELECT cron.schedule('monthly-reset', '0 0 1 * *',
    'SELECT pg_stat_s
```

**错误**: SELECT语句缺少FROM子句

---

### 36-SQL注入防御完整指南.md

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

**错误**: SELECT语句缺少FROM子句

---

**行 270** (sql):

```sql
-- 启用查询日志
ALTER SYSTEM SET log_statement = 'all';  -- 或 'mod'（修改语句）
ALTER SYSTEM SET log_min_duration_statement = 0;

-- 分析日志（Python示例）
import re

# 检测可疑模式
sql_injection_patterns = [
    r"(?i)union\s
```

**错误**: SELECT语句缺少FROM子句

---

### 39-外键与约束完全实战.md

**行 250** (sql):

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT  --
```

**错误**: 单引号不匹配

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

**错误**: 括号不匹配

---

### 40-PostgreSQL18新特性总结.md

**行 69** (sql):

```sql
-- 生成UUIDv7（时间排序）
SELECT gen_uuid_v7();
-- 01933b7e-8f5a-7000-8000-123456789abc

-- 对比UUIDv4
CREATE TABLE logs_v4 (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    data TEXT
);
-- INSERT性能: 基准

```

**错误**: SELECT语句缺少FROM子句

---

**行 327** (sql):

```sql
-- 推荐PostgreSQL 18配置
ALTER SYSTEM SET io_direct = 'data,wal';          -- 异步I/O
ALTER SYSTEM SET io_combine_limit = '256kB';      -- I/O合并
ALTER SYSTEM SET enable_skip_scan = on;           -- Skip Sca
```

**错误**: SELECT语句缺少FROM子句

---

### 41-PostgreSQL开发者速查表.md

**行 255** (sql):

```sql
-- 异步I/O（性能+35%）
ALTER SYSTEM SET io_direct = 'data,wal';
SELECT pg_reload_conf();

-- Skip Scan
ALTER SYSTEM SET enable_skip_scan = on;

-- UUIDv7（时间排序）
SELECT gen_uuid_v7();

-- GIN并行构建（索引快73%）
CREA
```

**错误**: SELECT语句缺少FROM子句

---

### 41-实时数据库完全指南.md

**行 119** (sql):

```sql
-- Payload最大8000字节
SELECT length('very long string'::text);

-- 超过限制需要传递ID，再查询
PERFORM pg_notify(
    'large_data_event',
    json_build_object('id', NEW.id)::text
);

```

**错误**: SELECT语句缺少FROM子句

---

**行 503** (python):

```python
   try:
       conn.poll()
       # 处理通知
   except psycopg2.DatabaseError as e:
       print(f"数据库错误: {e}")
       # 重新连接
       reconnect()

```

**错误**: 语法错误: unexpected indent (行 1)

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

**错误**: 语法错误: unexpected indent (行 1)

---

### 42-全文搜索深度实战.md

**行 50** (sql):

```sql
-- tsvector: 文档向量
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- 结果: 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2

-- tsquery: 查询表达式
SELECT to_tsquery('engli
```

**错误**: SELECT语句缺少FROM子句

---

**行 303** (sql):

```sql
-- 创建扩展
CREATE EXTENSION zhparser;

-- 创建中文文本搜索配置
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);

-- 添加token映射
ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR
    n,v,a,i,e,l WI
```

**错误**: SELECT语句缺少FROM子句

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

**错误**: 单引号不匹配

---
