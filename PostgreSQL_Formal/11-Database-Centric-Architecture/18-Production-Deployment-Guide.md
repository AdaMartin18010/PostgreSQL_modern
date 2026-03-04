# DCA生产环境部署指南

> **文档类型**: 生产环境完整配置
> **适用版本**: PostgreSQL 14+ (推荐18)
> **更新日期**: 2026-03-04
> **状态**: 生产就绪

---

## 目录

- [DCA生产环境部署指南](#dca生产环境部署指南)
  - [目录](#目录)
  - [1. 生产环境架构](#1-生产环境架构)
  - [2. 服务器配置](#2-服务器配置)
    - [2.1 硬件规格](#21-硬件规格)
    - [2.2 操作系统配置](#22-操作系统配置)
  - [3. PostgreSQL配置](#3-postgresql配置)
    - [3.1 postgresql.conf完整配置](#31-postgresqlconf完整配置)
    - [3.2 pg\_hba.conf配置](#32-pg_hbaconf配置)
    - [3.3 扩展安装清单](#33-扩展安装清单)
  - [4. PgBouncer连接池配置](#4-pgbouncer连接池配置)
  - [5. 主从复制配置](#5-主从复制配置)
    - [主库配置](#主库配置)
    - [从库配置](#从库配置)
  - [6. 备份策略](#6-备份策略)
  - [7. 监控配置](#7-监控配置)
    - [Prometheus监控](#prometheus监控)
    - [关键监控指标](#关键监控指标)
  - [8. 安全加固](#8-安全加固)
  - [9. 性能基准测试](#9-性能基准测试)

---

## 1. 生产环境架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              生产环境架构                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   应用层                                                                     │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                     │
│   │   App Pod 1  │  │   App Pod 2  │  │   App Pod N  │                     │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                     │
│          │                 │                 │                              │
│          └─────────────────┼─────────────────┘                              │
│                            ▼                                                │
│   连接池层     ┌──────────────────────────────────────┐                    │
│                │  PgBouncer Cluster (HAProxy LB)      │                    │
│                │  ┌──────────┐ ┌──────────┐          │                    │
│                │  │ 节点1    │ │ 节点2    │          │                    │
│                │  └────┬─────┘ └────┬─────┘          │                    │
│                └───────┼────────────┼────────────────┘                    │
│                        │            │                                       │
│   数据库层             ▼            ▼                                       │
│                ┌──────────────────────────────────────┐                    │
│                │          Primary (Master)            │                    │
│                │  ┌────────────────────────────────┐  │                    │
│                │  │  PostgreSQL 18                 │  │                    │
│                │  │  - 业务存储过程                 │  │                    │
│                │  │  - 写入操作                     │  │                    │
│                │  │  - 实时查询                     │  │                    │
│                │  └────────────────────────────────┘  │                    │
│                └──────────────┬───────────────────────┘                    │
│                               │ WAL Stream                                 │
│              ┌────────────────┼────────────────┐                           │
│              ▼                ▼                ▼                           │
│   从库层  ┌──────────┐   ┌──────────┐   ┌──────────┐                      │
│           │Standby 1 │   │Standby 2 │   │Standby 3 │                      │
│           │ (Hot)     │   │ (Hot)     │   │ (Hot)     │                      │
│           └────┬─────┘   └────┬─────┘   └────┬─────┘                      │
│                │              │              │                             │
│                └──────────────┼──────────────┘                             │
│                               ▼                                            │
│   监控层              ┌───────────────┐                                    │
│                       │  Prometheus   │                                    │
│                       │  + Grafana    │                                    │
│                       └───────────────┘                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 服务器配置

### 2.1 硬件规格

| 角色 | CPU | 内存 | 存储 | 网络 | 数量 |
|-----|-----|------|------|------|------|
| Primary | 16核+ | 64GB+ | NVMe SSD 1TB+ | 10GbE | 1 |
| Standby | 16核+ | 64GB+ | NVMe SSD 1TB+ | 10GbE | 2+ |
| PgBouncer | 4核 | 8GB | SSD 50GB | 10GbE | 2 |

### 2.2 操作系统配置

```bash
# ============================================
# /etc/sysctl.conf - 内核参数优化
# ============================================

# 共享内存
kernel.shmmax = 137438953472          # 128GB
kernel.shmall = 33554432              # 8GB pages
kernel.shmmni = 4096

# 信号量
kernel.sem = 250 32000 100 128

# 网络优化
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_tw_recycle = 0
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 2

# 内存优化
vm.overcommit_memory = 2
vm.overcommit_ratio = 95
vm.swappiness = 1
vm.dirty_background_ratio = 5
vm.dirty_ratio = 10
vm.dirty_expire_centisecs = 500
vm.dirty_writeback_centisecs = 100

# 文件描述符
fs.file-max = 2097152
fs.aio-max-nr = 1048576
```

```bash
# ============================================
# /etc/security/limits.conf - 资源限制
# ============================================

# PostgreSQL用户限制
postgres    soft    nofile      1048576
postgres    hard    nofile      1048576
postgres    soft    nproc       1048576
postgres    hard    nproc       1048576
postgres    soft    memlock     unlimited
postgres    hard    memlock     unlimited
```

```bash
# 应用配置
sudo sysctl -p
```

---

## 3. PostgreSQL配置

### 3.1 postgresql.conf完整配置

```ini
# ============================================
# postgresql.conf - 生产环境完整配置
# PostgreSQL 18 优化版本
# ============================================

#------------------------------------------------------------------------------
# 文件位置
#------------------------------------------------------------------------------
data_directory = '/var/lib/postgresql/18/main'
hba_file = '/etc/postgresql/18/main/pg_hba.conf'
ident_file = '/etc/postgresql/18/main/pg_ident.conf'

#------------------------------------------------------------------------------
# 连接和认证
#------------------------------------------------------------------------------
listen_addresses = '*'
port = 5432
max_connections = 500                     # 根据内存调整：内存(GB)*100
superuser_reserved_connections = 10

# SSL配置
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ciphers = 'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'

#------------------------------------------------------------------------------
# 内存配置 (假设64GB内存服务器)
#------------------------------------------------------------------------------
shared_buffers = 16GB                     # 25% of RAM
effective_cache_size = 48GB               # 75% of RAM
maintenance_work_mem = 2GB                # 用于VACUUM、索引创建
work_mem = 32MB                           # 每个连接，复杂查询可增大
dynamic_shared_memory_type = posix

# 专用内存区域
autovacuum_work_mem = 1GB
logical_decoding_work_mem = 256MB
max_locks_per_transaction = 256

#------------------------------------------------------------------------------
# WAL配置
#------------------------------------------------------------------------------
wal_level = logical                       # PG 18逻辑复制
wal_buffers = 128MB
max_wal_size = 8GB
min_wal_size = 2GB
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min
full_page_writes = on

# WAL压缩 (PG 18)
wal_compression = zstd

# 归档配置
archive_mode = on
archive_command = 'cp %p /backup/wal_archive/%f'
archive_timeout = 60

# 复制槽
max_replication_slots = 10
max_wal_senders = 10
wal_sender_timeout = 60s
wal_receiver_timeout = 60s
wal_retrieve_retry_interval = 5s

#------------------------------------------------------------------------------
# 查询优化器
#------------------------------------------------------------------------------
random_page_cost = 1.1                    # SSD存储
effective_io_concurrency = 200            # SSD可更高
default_statistics_target = 100
constraint_exclusion = partition

# 并行查询
max_parallel_workers_per_gather = 8
max_parallel_maintenance_workers = 4
max_parallel_workers = 16
parallel_leader_participation = on
min_parallel_table_scan_size = 8MB
min_parallel_index_scan_size = 512kB

#------------------------------------------------------------------------------
# 写入和刷盘
#------------------------------------------------------------------------------
bgwriter_delay = 50ms
bgwriter_lru_maxpages = 4000
bgwriter_lru_multiplier = 10.0

# 异步提交配置
synchronous_commit = on                   # 强一致性场景
# synchronous_commit = off                # 高性能场景（可能丢1秒数据）

synchronous_standby_names = 'FIRST 1 (standby1, standby2)'

#------------------------------------------------------------------------------
# PG 18 新特性配置
#------------------------------------------------------------------------------

# AIO配置
io_method = aio                           # 启用异步I/O
max_io_workers = 8

# 默认数据校验和
data_checksums = on

# 升级统计保留
pg_upgrade_preserve_stats = on

#------------------------------------------------------------------------------
# 日志配置
#------------------------------------------------------------------------------
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 1GB
log_truncate_on_rotation = off

# 日志内容
log_min_messages = warning
log_min_error_statement = error
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 128MB
log_autovacuum_min_duration = 1s

# 慢查询日志
log_min_duration_statement = 1000         # 1秒以上的查询
log_statement = 'ddl'                     # 记录DDL
log_duration = on

#------------------------------------------------------------------------------
# 自动清理
#------------------------------------------------------------------------------
autovacuum = on
autovacuum_max_workers = 6
autovacuum_naptime = 10s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.05
autovacuum_vacuum_cost_delay = 2ms
autovacuum_vacuum_cost_limit = -1

# 防事务ID回卷
autovacuum_freeze_min_age = 50000000
autovacuum_freeze_table_age = 150000000
autovacuum_multixact_freeze_min_age = 5000000
autovacuum_multixact_freeze_table_age = 150000000

#------------------------------------------------------------------------------
# 锁和事务
#------------------------------------------------------------------------------
deadlock_timeout = 2s
lock_timeout = 30s                        # 客户端可覆盖
statement_timeout = 60s                   # 防止慢查询
idle_in_transaction_session_timeout = 10min

#------------------------------------------------------------------------------
# 客户端连接默认值
#------------------------------------------------------------------------------
client_min_messages = notice
client_encoding = utf8
lc_messages = 'en_US.UTF-8'
lc_monetary = 'en_US.UTF-8'
lc_numeric = 'en_US.UTF-8'
lc_time = 'en_US.UTF-8'
default_text_search_config = 'pg_catalog.english'
timezone = 'UTC'

#------------------------------------------------------------------------------
# 扩展和共享库
#------------------------------------------------------------------------------
shared_preload_libraries = 'pg_stat_statements,auto_explain,pg_prewarm'

# pg_stat_statements配置
pg_stat_statements.max = 10000
pg_stat_statements.track = all
pg_stat_statements.track_utility = on
pg_stat_statements.track_planning = on

# auto_explain配置
auto_explain.log_min_duration = 1s
auto_explain.log_analyze = true
auto_explain.log_buffers = true
auto_explain.log_timing = true
auto_explain.log_triggers = true
auto_explain.log_verbose = true
auto_explain.log_format = text
```

### 3.2 pg_hba.conf配置

```
# ============================================
# pg_hba.conf - 客户端认证配置
# ============================================

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# 本地连接
local   all             postgres                                peer
local   all             all                                     scram-sha-256

# IPv4本地连接
host    all             all             127.0.0.1/32            scram-sha-256

# IPv6本地连接
host    all             all             ::1/128                 scram-sha-256

# 应用服务器段
hostssl all             app_user        10.0.1.0/24             scram-sha-256
hostssl all             app_readonly    10.0.1.0/24             scram-sha-256

# 备份服务器
hostssl replication     replicator      10.0.2.10/32            scram-sha-256

# 监控服务器
hostssl all             prometheus      10.0.3.10/32            scram-sha-256

# PgBouncer连接
hostssl all             pgbouncer       10.0.1.100/32           scram-sha-256

# 拒绝其他所有连接
host    all             all             0.0.0.0/0               reject
host    all             all             ::/0                    reject
```

### 3.3 扩展安装清单

```sql
-- ============================================
-- 生产环境必需扩展安装脚本
-- ============================================

-- 1. 核心扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- PG 18+ 使用原生UUIDv7
-- CREATE EXTENSION IF NOT EXISTS "uuidv7";  -- 仅PG 18+

-- 2. 监控扩展
CREATE EXTENSION IF NOT EXISTS "pg_prewarm";

-- 3. 可选扩展（根据需求）
-- CREATE EXTENSION IF NOT EXISTS "postgis";          -- GIS数据
-- CREATE EXTENSION IF NOT EXISTS "pg_trgm";          -- 模糊搜索
-- CREATE EXTENSION IF NOT EXISTS "btree_gin";        -- GIN索引
-- CREATE EXTENSION IF NOT EXISTS "pg_similarity";    -- 相似度计算

-- 4. 验证扩展安装
SELECT
    extname,
    extversion,
    extnamespace::regnamespace as schema
FROM pg_extension
ORDER BY extname;
```

---

## 4. PgBouncer连接池配置

```ini
; ============================================
; pgbouncer.ini - 连接池配置
; ============================================

[databases]
; 主库（读写）
mydb_primary = host=primary.internal port=5432 dbname=mydb

; 从库（只读）- 负载均衡
mydb_standby1 = host=standby1.internal port=5432 dbname=mydb
mydb_standby2 = host=standby2.internal port=5432 dbname=mydb
mydb_standby3 = host=standby3.internal port=5432 dbname=mydb

; 自动路由的数据库别名
mydb = host=primary.internal port=5432 dbname=mydb
mydb_ro = host=standby1.internal port=5432 dbname=mydb

[pgbouncer]
; 监听配置
listen_addr = 0.0.0.0
listen_port = 6432
unix_socket_dir = /var/run/postgresql

; 认证
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
auth_query = SELECT usename, passwd FROM pg_shadow WHERE usename=$1

; 连接池模式
; session: 会话保持（默认）
; transaction: 事务级（推荐用于DCA）
; statement: 语句级
pool_mode = transaction

; 连接池大小
default_pool_size = 25
min_pool_size = 10
reserve_pool_size = 10
reserve_pool_timeout = 3
max_client_conn = 10000
max_db_connections = 100
max_user_connections = 100

; 连接管理
server_idle_timeout = 600
server_lifetime = 3600
server_connect_timeout = 15
server_login_retry = 15
client_idle_timeout = 0
client_login_timeout = 60
query_timeout = 0
query_wait_timeout = 120

; TLS配置
client_tls_sslmode = require
client_tls_key_file = /etc/ssl/private/pgbouncer.key
client_tls_cert_file = /etc/ssl/certs/pgbouncer.crt
client_tls_ca_file = /etc/ssl/certs/ca.crt

server_tls_sslmode = require
server_tls_key_file = /etc/ssl/private/pgbouncer.key
server_tls_cert_file = /etc/ssl/certs/pgbouncer.crt

; 日志
logfile = /var/log/pgbouncer/pgbouncer.log
pidfile = /var/run/pgbouncer/pgbouncer.pid
admin_users = postgres,dba
stats_users = prometheus,monitor

; 日志详细度
verbose = 0

; 管理控制台
admin_users = postgres
```

```
# /etc/pgbouncer/userlist.txt
"app_user" "SCRAM-SHA-256$4096:..."
"pgbouncer" "SCRAM-SHA-256$4096:..."
```

---

## 5. 主从复制配置

### 主库配置

```sql
-- 创建复制用户
CREATE USER replicator WITH REPLICATION LOGIN ENCRYPTED PASSWORD 'Secure_Pass_123!';
GRANT CONNECT ON DATABASE mydb TO replicator;

-- 创建复制槽
SELECT * FROM pg_create_physical_replication_slot('standby_1_slot', true);
SELECT * FROM pg_create_physical_replication_slot('standby_2_slot', true);

-- 监控复制
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state,
    reply_time
FROM pg_stat_replication;
```

### 从库配置

```bash
#!/bin/bash
# ============================================
# setup_standby.sh - 从库初始化脚本
# ============================================

PRIMARY_HOST="primary.internal"
REPLICATOR_USER="replicator"
DATA_DIR="/var/lib/postgresql/18/main"
SLOT_NAME="standby_$(hostname)_slot"

echo "=== 停止PostgreSQL服务 ==="
systemctl stop postgresql

echo "=== 清理旧数据 ==="
rm -rf ${DATA_DIR}/*

echo "=== 执行pg_basebackup ==="
pg_basebackup \
  --host=${PRIMARY_HOST} \
  --port=5432 \
  --username=${REPLICATOR_USER} \
  --pgdata=${DATA_DIR} \
  --format=plain \
  --wal-method=stream \
  --checkpoint=fast \
  --progress \
  --verbose

echo "=== 创建standby.signal ==="
touch ${DATA_DIR}/standby.signal

echo "=== 配置主库连接 ==="
cat > ${DATA_DIR}/postgresql.auto.conf <<EOF
primary_conninfo = 'host=${PRIMARY_HOST} port=5432 user=${REPLICATOR_USER} password=Secure_Pass_123! sslmode=require'
primary_slot_name = '${SLOT_NAME}'
hot_standby = on
hot_standby_feedback = on
EOF

echo "=== 设置权限 ==="
chown -R postgres:postgres ${DATA_DIR}
chmod 700 ${DATA_DIR}

echo "=== 启动PostgreSQL ==="
systemctl start postgresql

echo "=== 验证复制状态 ==="
sleep 5
psql -c "SELECT pg_is_in_recovery(), pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();"
```

---

## 6. 备份策略

```bash
#!/bin/bash
# ============================================
# backup.sh - 每日备份脚本
# ============================================

BACKUP_DIR="/backup/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7
DB_NAME="mydb"

echo "=== 开始备份: ${DATE} ==="

# 1. 基础备份
echo "1. 执行pg_basebackup..."
pg_basebackup \
  --pgdata=${BACKUP_DIR}/base_${DATE} \
  --format=tar \
  --gzip \
  --checkpoint=fast \
  --verbose

# 2. 逻辑备份（关键表）
echo "2. 执行pg_dump..."
pg_dump \
  --dbname=${DB_NAME} \
  --format=custom \
  --compress=9 \
  --file=${BACKUP_DIR}/logical_${DB_NAME}_${DATE}.dump \
  --verbose

# 3. 全局对象备份
echo "3. 备份全局对象..."
pg_dumpall --globals-only > ${BACKUP_DIR}/globals_${DATE}.sql

# 4. 清理旧备份
echo "4. 清理${RETENTION_DAYS}天前的备份..."
find ${BACKUP_DIR} -name "base_*" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "logical_*.dump" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "globals_*.sql" -mtime +${RETENTION_DAYS} -delete

# 5. 上传至对象存储（可选）
# aws s3 sync ${BACKUP_DIR} s3://mybucket/postgres-backup/

echo "=== 备份完成 ==="
```

---

## 7. 监控配置

### Prometheus监控

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'postgresql'
    static_configs:
      - targets: ['primary.internal:9187', 'standby1.internal:9187']
    metrics_path: /metrics
    scrape_interval: 15s
```

### 关键监控指标

```sql
-- ============================================
-- 生产环境关键监控视图
-- ============================================

-- 连接数监控
CREATE VIEW v_monitor_connections AS
SELECT
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle,
    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
    count(*) FILTER (WHERE wait_event_type = 'Lock') as waiting_on_lock
FROM pg_stat_activity
WHERE backend_type = 'client backend';

-- 复制延迟监控
CREATE VIEW v_monitor_replication_lag AS
SELECT
    client_addr as standby,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) as lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) as lag_size,
    reply_time
FROM pg_stat_replication;

-- 慢查询监控
CREATE VIEW v_monitor_slow_queries AS
SELECT
    pid,
    usename,
    query,
    state,
    now() - query_start as duration
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '1 second'
ORDER BY duration DESC;

-- 表膨胀监控
CREATE VIEW v_monitor_table_bloat AS
SELECT
    schemaname,
    relname as table_name,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    CASE WHEN n_live_tup > 0
        THEN round(100.0 * n_dead_tup / n_live_tup, 2)
        ELSE 0
    END as bloat_ratio,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

---

## 8. 安全加固

```sql
-- ============================================
-- 安全加固脚本
-- ============================================

-- 1. 删除默认超级用户权限
ALTER USER postgres WITH PASSWORD 'NewSecurePassword123!';

-- 2. 创建应用专用用户（最小权限）
CREATE USER app_readonly WITH LOGIN PASSWORD 'ReadOnly_123!';
GRANT CONNECT ON DATABASE mydb TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;

CREATE USER app_readwrite WITH LOGIN PASSWORD 'ReadWrite_123!';
GRANT CONNECT ON DATABASE mydb TO app_readwrite;
GRANT USAGE ON SCHEMA public TO app_readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;

-- 3. 启用行级安全（RLS）
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY order_user_isolation ON orders
    FOR ALL
    TO app_readwrite
    USING (user_id = current_setting('app.current_user_id')::BIGINT);

-- 4. 审计日志触发器
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    changed_by TEXT,
    changed_at TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION fn_audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (table_name, operation, old_data, changed_by)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), current_user);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (table_name, operation, old_data, new_data, changed_by)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), current_user);
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (table_name, operation, new_data, changed_by)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW), current_user);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

---

## 9. 性能基准测试

```bash
#!/bin/bash
# ============================================
# benchmark.sh - 性能基准测试
# ============================================

DB_NAME="mydb"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"
CONNECTIONS=100
DURATION=300

echo "=== PostgreSQL 性能基准测试 ==="

# 1. 连接测试
echo "1. 连接测试..."
pgbench -i -s 100 ${DB_NAME}

# 2. 只读测试
echo "2. 只读测试 (SELECT)..."
pgbench -c ${CONNECTIONS} -j ${CONNECTIONS} -T ${DURATION} -S -P 5 ${DB_NAME}

# 3. 读写混合测试
echo "3. 读写混合测试..."
pgbench -c ${CONNECTIONS} -j ${CONNECTIONS} -T ${DURATION} -P 5 ${DB_NAME}

# 4. 存储过程测试
echo "4. 存储过程性能测试..."
psql -d ${DB_NAME} -c "
DO \$\$
DECLARE
    v_start TIMESTAMP;
    v_count INT := 10000;
BEGIN
    v_start := clock_timestamp();

    FOR i IN 1..v_count LOOP
        PERFORM sp_user_create('user_' || i, 'user_' || i || '@test.com', NULL, NULL, NULL);
    END LOOP;

    RAISE NOTICE '存储过程执行 % 次，耗时: %', v_count, clock_timestamp() - v_start;
END;
\$\$;
"

echo "=== 测试完成 ==="
```

---

**文档版本**: v1.0
**最后更新**: 2026-03-04
**适用环境**: PostgreSQL 14+ 生产环境
