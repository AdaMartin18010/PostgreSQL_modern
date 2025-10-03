# 流式复制实战案例 — Streaming Replication & High Availability

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **难度等级**：⭐⭐⭐⭐⭐ 专家级  
> **预计时间**：90-120分钟  
> **适合场景**：高可用架构、读写分离、灾难恢复、多地域部署

---

## 📋 案例目标

构建一个生产级的PostgreSQL流式复制高可用系统，包括：

1. ✅ 主从复制配置（Primary-Standby）
2. ✅ 同步复制与异步复制
3. ✅ 自动故障转移（Failover）
4. ✅ 复制监控与健康检查
5. ✅ 读写分离负载均衡

---

## 🎯 业务场景

**场景描述**：电商平台高可用数据库架构

- **系统要求**：
  - 99.99% 可用性（年停机时间<53分钟）
  - RPO（Recovery Point Objective）< 5秒
  - RTO（Recovery Time Objective）< 30秒
  - 支持读写分离（读QPS 10K+）
- **架构设计**：
  - 1个Primary节点（写）
  - 2个Standby节点（读+备份）
  - 自动故障检测与切换

---

## 🏗️ 架构设计

```text
                    ┌─────────────────┐
                    │   Application   │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │   HAProxy/      │
                    │   PgBouncer     │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐   ┌─────▼──────┐   ┌─────▼──────┐
    │  Primary    │   │ Standby-1  │   │ Standby-2  │
    │  (Write)    │───│  (Read)    │   │  (Read)    │
    │  Port:5432  │   │  Port:5433 │   │  Port:5434 │
    └─────────────┘   └────────────┘   └────────────┘
         Master          Sync Replica    Async Replica
```

---

## 📦 1. 环境准备

### 1.1 系统要求

```bash
# 至少3台服务器（或3个Docker容器）
# - primary:   192.168.1.10:5432
# - standby1:  192.168.1.11:5433  (同步复制)
# - standby2:  192.168.1.12:5434  (异步复制)

# 操作系统
# Ubuntu 22.04+ / CentOS 8+ / Debian 11+

# 网络要求
# - 节点间网络延迟 < 10ms
# - 带宽 >= 100Mbps
```

### 1.2 Docker Compose快速搭建

```yaml
# docker-compose.yml
version: '3.8'

services:
  primary:
    image: postgres:17
    container_name: pg_primary
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: testdb
    ports:
      - "5432:5432"
    volumes:
      - primary_data:/var/lib/postgresql/data
      - ./init_primary.sh:/docker-entrypoint-initdb.d/init.sh
    command: >
      postgres
      -c wal_level=replica
      -c max_wal_senders=10
      -c max_replication_slots=10
      -c hot_standby=on

  standby1:
    image: postgres:17
    container_name: pg_standby1
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5433:5432"
    volumes:
      - standby1_data:/var/lib/postgresql/data
    depends_on:
      - primary

  standby2:
    image: postgres:17
    container_name: pg_standby2
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5434:5432"
    volumes:
      - standby2_data:/var/lib/postgresql/data
    depends_on:
      - primary

volumes:
  primary_data:
  standby1_data:
  standby2_data:
```

---

## 🔧 2. Primary节点配置

### 2.1 修改postgresql.conf

```ini
# postgresql.conf (Primary节点)

# ===== WAL设置 =====
wal_level = replica                 # 复制需要replica级别
max_wal_senders = 10                # 最大复制连接数
max_replication_slots = 10          # 最大复制槽数
wal_keep_size = 1GB                 # 保留WAL大小（PG17推荐）
hot_standby = on                    # 允许备库只读查询

# ===== 同步复制设置 =====
synchronous_commit = on             # 同步提交
synchronous_standby_names = 'standby1'  # 同步备库名称

# ===== 归档设置（可选，用于PITR）=====
archive_mode = on
archive_command = 'test ! -f /archive/%f && cp %p /archive/%f'

# ===== 连接设置 =====
listen_addresses = '*'
max_connections = 100

# ===== 日志设置 =====
logging_collector = on
log_destination = 'csvlog'
log_replication_commands = on       # 记录复制命令（PG17新增）
```

### 2.2 修改pg_hba.conf

```conf
# pg_hba.conf (Primary节点)

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# 本地连接
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5

# 复制连接
host    replication     replicator      192.168.1.0/24          md5
host    replication     replicator      172.17.0.0/16           md5  # Docker网络
```

### 2.3 创建复制用户

```sql
-- 在Primary节点执行
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'repl_password';

-- 授予必要权限
GRANT EXECUTE ON FUNCTION pg_catalog.pg_ls_dir(text) TO replicator;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_stat_file(text) TO replicator;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_read_binary_file(text) TO replicator;
```

### 2.4 创建复制槽

```sql
-- 为每个Standby创建复制槽（推荐）
SELECT pg_create_physical_replication_slot('standby1_slot');
SELECT pg_create_physical_replication_slot('standby2_slot');

-- 查看复制槽
SELECT * FROM pg_replication_slots;
```

---

## 🔄 3. Standby节点配置

### 3.1 使用pg_basebackup创建备库

```bash
# 在Standby节点执行

# 停止Standby的PostgreSQL服务
systemctl stop postgresql

# 清空数据目录
rm -rf /var/lib/postgresql/17/main/*

# 使用pg_basebackup从Primary复制数据
pg_basebackup \
  -h 192.168.1.10 \
  -p 5432 \
  -U replicator \
  -D /var/lib/postgresql/17/main \
  -P \
  -X stream \
  -R \
  -S standby1_slot

# 参数说明：
# -h: Primary节点地址
# -U: 复制用户
# -D: 数据目录
# -P: 显示进度
# -X stream: 流式复制WAL
# -R: 自动创建standby.signal和配置复制参数
# -S: 使用复制槽
```

### 3.2 配置Standby连接信息

```conf
# postgresql.auto.conf (由pg_basebackup -R自动生成)

primary_conninfo = 'host=192.168.1.10 port=5432 user=replicator password=repl_password application_name=standby1'
primary_slot_name = 'standby1_slot'

# 手动调整（可选）
hot_standby = on
hot_standby_feedback = on          # 向主库反馈查询冲突
max_standby_streaming_delay = 30s  # 最大查询延迟
```

### 3.3 启动Standby

```bash
# 启动Standby节点
systemctl start postgresql

# 检查复制状态
psql -U postgres -c "SELECT pg_is_in_recovery();"  # 应返回 t (true)
```

---

## 📊 4. 复制监控

### 4.1 Primary节点监控

```sql
-- 查看复制连接状态
SELECT 
    application_name,
    client_addr,
    state,
    sync_state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replication_lag_bytes,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;

-- 查看复制槽状态
SELECT 
    slot_name,
    slot_type,
    active,
    restart_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS lag_bytes
FROM pg_replication_slots;

-- 查看WAL发送进程
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    backend_start,
    state,
    sync_state
FROM pg_stat_replication;
```

### 4.2 Standby节点监控

```sql
-- 查看复制接收状态
SELECT 
    status,
    receive_start_lsn,
    receive_start_tli,
    received_lsn,
    received_tli,
    last_msg_send_time,
    last_msg_receipt_time,
    latest_end_lsn,
    latest_end_time,
    slot_name,
    conninfo
FROM pg_stat_wal_receiver;

-- 查看复制延迟
SELECT 
    now() - pg_last_xact_replay_timestamp() AS replication_delay;

-- 查看最后接收的WAL位置
SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();
```

---

## ⚡ 5. 同步复制 vs 异步复制

### 5.1 配置同步复制

```sql
-- 在Primary节点执行

-- 单个同步备库
ALTER SYSTEM SET synchronous_standby_names = 'standby1';

-- 多个同步备库（任意1个确认即可）
ALTER SYSTEM SET synchronous_standby_names = 'ANY 1 (standby1, standby2)';

-- 多个同步备库（必须所有确认）
ALTER SYSTEM SET synchronous_standby_names = 'FIRST 2 (standby1, standby2)';

-- 重载配置
SELECT pg_reload_conf();

-- 验证同步状态
SELECT application_name, sync_state FROM pg_stat_replication;
-- sync_state: sync(同步) / async(异步) / potential(候选)
```

### 5.2 同步复制性能影响

```sql
-- 测试同步复制的性能影响

-- 异步复制模式
SET synchronous_commit = off;
BEGIN;
INSERT INTO test_table VALUES (generate_series(1, 10000));
COMMIT;
-- 测量时间...

-- 同步复制模式
SET synchronous_commit = on;
BEGIN;
INSERT INTO test_table VALUES (generate_series(1, 10000));
COMMIT;
-- 测量时间...
```

---

## 🔥 6. 故障转移（Failover）

### 6.1 手动故障转移

```bash
# 步骤1：提升Standby为新Primary
# 在Standby1节点执行
pg_ctl promote -D /var/lib/postgresql/17/main

# 或使用SQL函数
psql -U postgres -c "SELECT pg_promote();"

# 步骤2：验证提升成功
psql -U postgres -c "SELECT pg_is_in_recovery();"  # 应返回 f (false)

# 步骤3：将其他Standby指向新Primary
# 在Standby2节点修改primary_conninfo
ALTER SYSTEM SET primary_conninfo = 'host=192.168.1.11 ...';
SELECT pg_reload_conf();
```

### 6.2 使用pg_rewind恢复旧Primary

```bash
# 将旧Primary恢复为Standby

# 步骤1：停止旧Primary
systemctl stop postgresql

# 步骤2：使用pg_rewind同步
pg_rewind \
  --target-pgdata=/var/lib/postgresql/17/main \
  --source-server='host=192.168.1.11 port=5432 user=postgres dbname=postgres'

# 步骤3：配置为Standby
touch /var/lib/postgresql/17/main/standby.signal
echo "primary_conninfo = 'host=192.168.1.11 port=5432 user=replicator password=repl_password'" \
  >> /var/lib/postgresql/17/main/postgresql.auto.conf

# 步骤4：启动为Standby
systemctl start postgresql
```

---

## 📈 7. 读写分离

### 7.1 应用层路由

```python
# Python示例：使用psycopg2实现读写分离

import psycopg2

# Primary连接（写）
primary_conn = psycopg2.connect(
    host='192.168.1.10',
    port=5432,
    user='app_user',
    password='password',
    database='testdb'
)

# Standby连接（读）
standby_conns = [
    psycopg2.connect(host='192.168.1.11', port=5433, ...),
    psycopg2.connect(host='192.168.1.12', port=5434, ...)
]

def execute_write(sql, params=None):
    """写操作"""
    with primary_conn.cursor() as cur:
        cur.execute(sql, params)
        primary_conn.commit()

def execute_read(sql, params=None):
    """读操作（负载均衡）"""
    import random
    conn = random.choice(standby_conns)
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()
```

### 7.2 使用PgBouncer

```ini
# pgbouncer.ini

[databases]
testdb = host=192.168.1.10 port=5432 dbname=testdb
testdb_ro = host=192.168.1.11 port=5433 dbname=testdb

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

---

## ✅ 8. 健康检查脚本

```bash
#!/bin/bash
# check_replication.sh

PRIMARY_HOST="192.168.1.10"
PRIMARY_PORT="5432"

# 检查复制延迟
QUERY="SELECT 
    application_name,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes,
    EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds
FROM pg_stat_replication;"

psql -h $PRIMARY_HOST -p $PRIMARY_PORT -U postgres -At -c "$QUERY" | while IFS='|' read app lag_bytes lag_seconds; do
    echo "Application: $app"
    echo "Lag (bytes): $lag_bytes"
    echo "Lag (seconds): $lag_seconds"
    
    # 告警阈值
    if (( $(echo "$lag_seconds > 10" | bc -l) )); then
        echo "WARNING: Replication lag > 10 seconds!"
        # 发送告警...
    fi
done
```

---

## 📚 9. 最佳实践

### 9.1 复制配置

- ✅ 使用复制槽防止WAL过早删除
- ✅ 关键业务使用同步复制
- ✅ 非关键业务使用异步复制
- ✅ 配置合适的wal_keep_size

### 9.2 监控告警

- ✅ 监控复制延迟（< 5秒）
- ✅ 监控复制槽空间占用
- ✅ 监控连接状态
- ✅ 设置自动告警

### 9.3 故障恢复

- ✅ 定期演练故障转移
- ✅ 文档化切换流程
- ✅ 使用自动化工具（Patroni、repmgr）
- ✅ 保留足够的WAL归档

### 9.4 性能优化

- ✅ 使用高速网络连接
- ✅ 调整wal_compression
- ✅ 优化checkpoint参数
- ✅ 监控I/O性能

---

## 🎯 10. 练习任务

1. **基础练习**：
   - 搭建1主1从的复制环境
   - 配置同步复制
   - 测试读写分离

2. **进阶练习**：
   - 实现手动故障转移
   - 使用pg_rewind恢复
   - 配置级联复制

3. **挑战任务**：
   - 使用Patroni实现自动HA
   - 构建多地域复制架构
   - 实现零停机升级

---

## 📖 11. 参考资源

- PostgreSQL 17 Replication: <https://www.postgresql.org/docs/17/high-availability.html>
- pg_basebackup: <https://www.postgresql.org/docs/17/app-pgbasebackup.html>
- Patroni HA Solution: <https://patroni.readthedocs.io/>
- repmgr: <https://www.repmgr.org/>

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**相关案例**：[分布式锁](../distributed_locks/README.md) | [实时分析](../realtime_analytics/README.md)
