# 📘 PostgreSQL 18 生产环境最佳实践完整手册

> **更新日期**: 2025年12月4日
> **适用版本**: PostgreSQL 18+
> **适用场景**: 生产环境部署、运维、优化
> **文档类型**: P3持续实践手册

---

## 📑 目录

- [📘 PostgreSQL 18 生产环境最佳实践完整手册](#-postgresql-18-生产环境最佳实践完整手册)
  - [📑 目录](#-目录)
  - [一、部署架构最佳实践](#一部署架构最佳实践)
    - [1.1 硬件选型](#11-硬件选型)
      - [CPU](#cpu)
      - [内存](#内存)
      - [存储](#存储)
    - [1.2 操作系统优化](#12-操作系统优化)
      - [Linux内核参数](#linux内核参数)
      - [资源限制](#资源限制)
      - [透明大页（建议禁用）](#透明大页建议禁用)
    - [1.3 目录结构规划](#13-目录结构规划)
  - [二、配置参数最佳实践](#二配置参数最佳实践)
    - [2.1 内存配置](#21-内存配置)
    - [2.2 连接配置](#22-连接配置)
    - [2.3 WAL配置](#23-wal配置)
    - [2.4 查询规划器](#24-查询规划器)
    - [2.5 日志配置](#25-日志配置)
    - [2.6 自动VACUUM](#26-自动vacuum)
    - [2.7 完整配置模板](#27-完整配置模板)
  - [三、安全加固最佳实践](#三安全加固最佳实践)
    - [3.1 认证加固](#31-认证加固)
    - [3.2 SSL配置](#32-ssl配置)
    - [3.3 用户权限最小化](#33-用户权限最小化)
    - [3.4 审计日志](#34-审计日志)
  - [四、备份恢复最佳实践](#四备份恢复最佳实践)
    - [4.1 备份策略](#41-备份策略)
    - [4.2 全量备份](#42-全量备份)
    - [4.3 PITR配置](#43-pitr配置)
  - [五、监控告警最佳实践](#五监控告警最佳实践)
    - [5.1 关键指标](#51-关键指标)
    - [5.2 Prometheus + Grafana](#52-prometheus--grafana)
    - [5.3 告警规则](#53-告警规则)
  - [六、高可用最佳实践](#六高可用最佳实践)
    - [6.1 架构选择](#61-架构选择)
    - [6.2 Patroni配置](#62-patroni配置)
  - [七、性能优化最佳实践](#七性能优化最佳实践)
    - [7.1 索引最佳实践](#71-索引最佳实践)
    - [7.2 查询优化最佳实践](#72-查询优化最佳实践)
    - [7.3 连接池配置](#73-连接池配置)
  - [八、运维管理最佳实践](#八运维管理最佳实践)
    - [8.1 定期维护](#81-定期维护)
    - [8.2 版本升级](#82-版本升级)

---

## 一、部署架构最佳实践

### 1.1 硬件选型

#### CPU

**推荐配置**：

- **小型应用**：4-8核
- **中型应用**：16-32核
- **大型应用**：64+核

**最佳实践**：

```bash
# 检查CPU信息
lscpu

# 推荐：至少4核以上
# PostgreSQL可充分利用多核（并行查询）
```

#### 内存

**推荐配置**：

- **小型**：16-32GB
- **中型**：64-128GB
- **大型**：256GB+

**经验法则**：

```text
shared_buffers = 25% 内存
effective_cache_size = 50-75% 内存
work_mem = (总内存 - shared_buffers) / max_connections / 2
```

#### 存储

**推荐**：

- ✅ **NVMe SSD**（最佳，延迟<100μs）
- ✅ **SSD**（推荐，延迟<1ms）
- ❌ **HDD**（不推荐，延迟>10ms）

**RAID配置**：

- **数据目录**：RAID 10（性能+可靠性）
- **WAL目录**：独立磁盘（SSD）
- **备份目录**：RAID 5/6（容量优先）

**最佳实践**：

```bash
# 1. 分离数据和WAL
# postgresql.conf
wal_log_hints = on
wal_level = replica

# 2. 使用XFS文件系统（推荐）
mkfs.xfs -f /dev/nvme0n1
mount -o noatime,nodiratime /dev/nvme0n1 /var/lib/postgresql

# 3. 设置I/O调度器
echo "none" > /sys/block/nvme0n1/queue/scheduler
```

### 1.2 操作系统优化

#### Linux内核参数

```bash
# /etc/sysctl.conf

# 共享内存（至少是shared_buffers的大小）
kernel.shmmax = 17179869184  # 16GB
kernel.shmall = 4194304

# 网络优化
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_keepalive_time = 60
net.ipv4.tcp_keepalive_intvl = 10
net.ipv4.tcp_keepalive_probes = 3

# 文件句柄
fs.file-max = 1000000

# 应用
sysctl -p
```

#### 资源限制

```bash
# /etc/security/limits.conf
postgres soft nofile 65536
postgres hard nofile 65536
postgres soft nproc 16384
postgres hard nproc 16384
```

#### 透明大页（建议禁用）

```bash
# 禁用透明大页
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag

# 永久禁用（加入rc.local）
```

### 1.3 目录结构规划

**推荐结构**：

```bash
/var/lib/postgresql/18/
├── main/               # 数据目录（高速SSD）
│   ├── base/          # 数据库文件
│   ├── global/        # 全局数据
│   └── pg_wal/        # 独立磁盘（建议）
├── tablespaces/       # 表空间（可选）
├── archive/           # WAL归档（大容量磁盘）
└── backup/            # 备份目录（大容量磁盘）
```

**挂载点分离**：

```bash
/dev/nvme0n1 -> /pgdata          # 数据目录（NVMe SSD）
/dev/nvme0n2 -> /pgwal           # WAL目录（NVMe SSD）
/dev/sda1    -> /pgarchive       # 归档目录（HDD）
/dev/sdb1    -> /pgbackup        # 备份目录（HDD）
```

---

## 二、配置参数最佳实践

### 2.1 内存配置

```sql
-- 32GB内存服务器示例

-- 1. shared_buffers（25%内存）
shared_buffers = 8GB

-- 2. effective_cache_size（50-75%内存）
effective_cache_size = 24GB

-- 3. work_mem（根据并发数）
-- 公式：(总内存 - shared_buffers) / max_connections / 2
-- (32GB - 8GB) / 100 / 2 = 120MB
work_mem = 120MB

-- 4. maintenance_work_mem（1-2GB）
maintenance_work_mem = 2GB

-- 5. wal_buffers（-1表示自动，通常16MB）
wal_buffers = 16MB
```

### 2.2 连接配置

```sql
-- 连接数设置
max_connections = 200

-- 推荐使用连接池
-- PgBouncer配置：
-- pool_mode = transaction
-- default_pool_size = 20
-- max_client_conn = 1000

-- 超时设置
idle_in_transaction_session_timeout = 5min
statement_timeout = 60s
lock_timeout = 30s
```

### 2.3 WAL配置

```sql
-- WAL级别
wal_level = replica  -- 支持流复制

-- WAL写入
wal_sync_method = fdatasync  -- Linux默认
fsync = on  -- 必须开启（生产环境）
synchronous_commit = on  -- 默认，可根据需求调整

-- WAL大小
max_wal_size = 4GB
min_wal_size = 1GB

-- Checkpoint
checkpoint_timeout = 10min
checkpoint_completion_target = 0.9

-- WAL归档（如需PITR）
archive_mode = on
archive_command = 'cp %p /pgarchive/%f'
```

### 2.4 查询规划器

```sql
-- 随机访问代价（SSD）
random_page_cost = 1.1

-- 顺序访问代价
seq_page_cost = 1.0

-- 并发I/O
effective_io_concurrency = 200  -- SSD

-- 并行查询
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_worker_processes = 16
```

### 2.5 日志配置

```sql
-- 日志位置
log_destination = 'csvlog'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 1GB

-- 记录内容
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_duration = off
log_lock_waits = on

-- 慢查询
log_min_duration_statement = 1000  -- 记录>1秒的查询
log_statement = 'ddl'  -- 记录DDL语句

-- 自动VACUUM日志
log_autovacuum_min_duration = 0
```

### 2.6 自动VACUUM

```sql
-- 启用自动VACUUM
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min

-- 触发条件
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.2
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.1

-- 资源限制
autovacuum_vacuum_cost_delay = 2ms
autovacuum_vacuum_cost_limit = 200
```

### 2.7 完整配置模板

```sql
-- PostgreSQL 18 生产环境配置模板
-- 适用于：32GB内存、8核CPU、SSD存储

-- === 内存配置 ===
shared_buffers = 8GB
effective_cache_size = 24GB
work_mem = 120MB
maintenance_work_mem = 2GB
wal_buffers = 16MB

-- === 连接配置 ===
max_connections = 200
idle_in_transaction_session_timeout = 5min
statement_timeout = 60s

-- === WAL配置 ===
wal_level = replica
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_timeout = 10min
checkpoint_completion_target = 0.9

-- === 查询规划器 ===
random_page_cost = 1.1
effective_io_concurrency = 200
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

-- === 日志配置 ===
logging_collector = on
log_destination = 'csvlog'
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_lock_waits = on

-- === 自动VACUUM ===
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min

-- === 复制配置（主库）===
max_wal_senders = 10
wal_keep_size = 1GB
hot_standby = on

-- === 其他 ===
shared_preload_libraries = 'pg_stat_statements'
track_activities = on
track_counts = on
track_io_timing = on
```

---

## 三、安全加固最佳实践

### 3.1 认证加固

```bash
# pg_hba.conf（按重要性排序）

# 本地连接（peer认证）
local   all             postgres                                peer

# 本地应用（密码认证）
local   all             all                                     scram-sha-256

# 远程连接（SSL + 密码）
hostssl all             all             0.0.0.0/0              scram-sha-256
hostssl all             all             ::/0                   scram-sha-256

# 拒绝非SSL连接
hostnossl all           all             0.0.0.0/0              reject
```

### 3.2 SSL配置

```sql
-- postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
ssl_ca_file = 'root.crt'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on
ssl_min_protocol_version = 'TLSv1.2'
```

```bash
# 生成自签名证书（测试用）
openssl req -new -x509 -days 365 -nodes -text \
  -out server.crt -keyout server.key -subj "/CN=dbserver.example.com"

chmod 600 server.key
chown postgres:postgres server.key server.crt
```

### 3.3 用户权限最小化

```sql
-- 1. 分离应用用户和管理员
CREATE ROLE app_user WITH LOGIN PASSWORD 'strong_password';
CREATE ROLE admin_user WITH LOGIN SUPERUSER PASSWORD 'strong_password';

-- 2. 限制应用用户权限
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

-- 3. 禁止修改系统表
REVOKE ALL ON SCHEMA pg_catalog FROM PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog TO app_user;

-- 4. 行级安全（RLS）
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_policy ON sensitive_data
    FOR ALL TO app_user
    USING (user_id = current_setting('app.user_id')::INT);
```

### 3.4 审计日志

```sql
-- 安装pgAudit扩展
CREATE EXTENSION pgaudit;

-- 配置审计
ALTER SYSTEM SET pgaudit.log = 'all';
ALTER SYSTEM SET pgaudit.log_catalog = off;
ALTER SYSTEM SET pgaudit.log_parameter = on;
ALTER SYSTEM SET pgaudit.log_relation = on;

-- 重载配置
SELECT pg_reload_conf();
```

---

## 四、备份恢复最佳实践

### 4.1 备份策略

**3-2-1规则**：

- **3**份副本
- **2**种介质
- **1**份异地

**备份类型**：

```text
全量备份：每周1次（周日）
增量备份：每天1次
WAL归档：实时
快照备份：重要操作前
```

### 4.2 全量备份

```bash
#!/bin/bash
# full_backup.sh

BACKUP_DIR="/pgbackup/full"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.tar.gz"

# pg_basebackup
pg_basebackup -D $BACKUP_DIR/backup_$DATE \
  -Ft -z -P -X fetch \
  -h localhost -U postgres

# 保留30天
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete

# 验证备份
if [ -f "$BACKUP_FILE" ]; then
    echo "Backup successful: $BACKUP_FILE"
    # 上传到云存储
    aws s3 cp $BACKUP_FILE s3://my-backup-bucket/
else
    echo "Backup failed!"
    exit 1
fi
```

### 4.3 PITR配置

```sql
-- postgresql.conf
archive_mode = on
archive_command = 'test ! -f /pgarchive/%f && cp %p /pgarchive/%f'
archive_timeout = 60  -- 每分钟强制切换WAL
```

```bash
# 恢复到指定时间点
# recovery.conf (PG 12+使用recovery.signal)
restore_command = 'cp /pgarchive/%f %p'
recovery_target_time = '2025-12-01 12:00:00'
recovery_target_action = 'promote'
```

---

## 五、监控告警最佳实践

### 5.1 关键指标

**数据库级别**：

- CPU使用率（>80%告警）
- 内存使用率（>90%告警）
- 磁盘使用率（>85%告警）
- 磁盘I/O（高延迟告警）
- 网络流量

**PostgreSQL级别**：

- 连接数（>80% max_connections告警）
- 活跃查询数
- 慢查询数
- 死锁数
- 复制延迟（>10秒告警）
- 缓存命中率（<95%告警）
- 表膨胀率

### 5.2 Prometheus + Grafana

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres_exporter:
    image: prometheuscommunity/postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://monitor:password@postgres:5432/postgres?sslmode=disable"
    ports:
      - "9187:9187"

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### 5.3 告警规则

```yaml
# prometheus_rules.yml
groups:
  - name: postgresql
    rules:
      # 连接数告警
      - alert: PostgreSQLTooManyConnections
        expr: sum(pg_stat_activity_count) > 160
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL连接数过高"

      # 慢查询告警
      - alert: PostgreSQLSlowQueries
        expr: rate(pg_stat_statements_mean_time_seconds[5m]) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL慢查询过多"

      # 复制延迟告警
      - alert: PostgreSQLReplicationLag
        expr: pg_replication_lag > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL复制延迟过大"
```

---

## 六、高可用最佳实践

### 6.1 架构选择

**推荐方案**：Patroni + etcd + HAProxy

```text
应用
  ↓
HAProxy (VIP)
  ↓
Patroni集群
  ├─ 主节点（读写）
  ├─ 从节点1（只读）
  └─ 从节点2（只读）
  ↓
etcd集群（一致性存储）
```

### 6.2 Patroni配置

```yaml
# patroni.yml
scope: postgres-cluster
name: node1

restapi:
  listen: 0.0.0.0:8008
  connect_address: node1:8008

etcd:
  hosts: etcd1:2379,etcd2:2379,etcd3:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      parameters:
        max_connections: 200
        shared_buffers: 8GB

postgresql:
  listen: 0.0.0.0:5432
  connect_address: node1:5432
  data_dir: /var/lib/postgresql/18/main
  pgpass: /tmp/pgpass
  authentication:
    replication:
      username: replicator
      password: rep_password
    superuser:
      username: postgres
      password: postgres_password
  parameters:
    wal_level: replica
    hot_standby: "on"
    max_wal_senders: 10
    max_replication_slots: 10
    wal_keep_size: 1GB
```

---

## 七、性能优化最佳实践

### 7.1 索引最佳实践

```sql
-- 1. 为WHERE子句列创建索引
CREATE INDEX idx_users_email ON users(email);

-- 2. 为JOIN列创建索引
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- 3. 复合索引（注意列顺序）
CREATE INDEX idx_orders_status_date ON orders(status, created_at);

-- 4. 覆盖索引
CREATE INDEX idx_orders_covering
ON orders(user_id) INCLUDE (amount, created_at);

-- 5. 部分索引（减少索引大小）
CREATE INDEX idx_orders_pending
ON orders(created_at) WHERE status = 'pending';

-- 6. 表达式索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
```

### 7.2 查询优化最佳实践

```sql
-- ❌ 避免SELECT *
SELECT * FROM users;

-- ✅ 指定需要的列
SELECT id, name, email FROM users;

-- ❌ 避免子查询IN
SELECT * FROM orders WHERE user_id IN (SELECT id FROM users WHERE active = true);

-- ✅ 使用JOIN
SELECT o.* FROM orders o JOIN users u ON o.user_id = u.id WHERE u.active = true;

-- ❌ 避免函数包裹索引列
SELECT * FROM users WHERE UPPER(email) = 'USER@EXAMPLE.COM';

-- ✅ 使用表达式索引或改写查询
SELECT * FROM users WHERE email = lower('USER@EXAMPLE.COM');
```

### 7.3 连接池配置

**PgBouncer推荐配置**：

```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
reserve_pool_size = 5
reserve_pool_timeout = 3

server_reset_query = DISCARD ALL
server_check_delay = 10
```

---

## 八、运维管理最佳实践

### 8.1 定期维护

**每日**：

```bash
# 检查日志
tail -100 /var/log/postgresql/postgresql-18-main.log

# 检查慢查询
psql -c "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# 检查连接数
psql -c "SELECT count(*) FROM pg_stat_activity;"
```

**每周**：

```sql
-- VACUUM ANALYZE
VACUUM ANALYZE;

-- 检查表膨胀
SELECT schemaname, tablename, n_dead_tup
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;

-- 检查索引使用情况
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

**每月**：

```bash
# 测试备份恢复
# 更新统计信息
# 审查安全日志
# 检查磁盘空间趋势
```

### 8.2 版本升级

```bash
# 使用pg_upgrade
pg_upgrade \
  -b /usr/lib/postgresql/17/bin \
  -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main \
  -D /var/lib/postgresql/18/main \
  --check

# 执行升级
pg_upgrade \
  -b /usr/lib/postgresql/17/bin \
  -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main \
  -D /var/lib/postgresql/18/main

# 清理旧版本
./delete_old_cluster.sh
```

---

**🎯 遵循这些最佳实践，构建稳定可靠的生产环境！** 🚀

---

**最后更新**: 2025年12月4日
**维护者**: PostgreSQL Modern Team
**文档编号**: P3-1-BEST-PRACTICES-2025-12
