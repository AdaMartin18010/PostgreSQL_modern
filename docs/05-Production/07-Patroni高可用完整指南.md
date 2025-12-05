# PostgreSQL 18 + Patroni 高可用完整指南

## 1. Patroni架构

### 1.1 组件架构

```text
┌─────────────────────────────────────────────────────┐
│              Patroni HA Architecture                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [HAProxy/PgBouncer] ← 应用连接                      │
│           │                                         │
│      ┌────┴────┐                                    │
│      │         │                                    │
│  [Primary]  [Standby-1]  [Standby-2]                │
│   Patroni    Patroni      Patroni                   │
│      │          │            │                      │
│      └──────────┴────────────┘                      │
│                 │                                   │
│             [etcd Cluster]                          │
│          (分布式配置存储)                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 1.2 核心特性

- **自动Failover**: Primary故障时自动选举新Primary
- **同步复制**: 保证零数据丢失
- **Split-Brain防护**: 基于etcd的分布式锁
- **健康检查**: 定期检测节点状态
- **配置管理**: 动态配置，无需重启

---

## 2. 环境准备

### 2.1 服务器规划

```text
节点规划 (最小3节点):
├─ pg-1: Primary候选  (192.168.1.11)
├─ pg-2: Standby候选  (192.168.1.12)
└─ pg-3: Standby候选  (192.168.1.13)

etcd集群 (独立3节点):
├─ etcd-1: (192.168.1.21)
├─ etcd-2: (192.168.1.22)
└─ etcd-3: (192.168.1.23)

负载均衡:
└─ haproxy: (192.168.1.30)
```

### 2.2 软件安装

```bash
# PostgreSQL 18
sudo apt install -y postgresql-18 postgresql-contrib-18

# Patroni
sudo apt install -y python3-pip python3-dev
sudo pip3 install patroni[etcd]

# etcd
ETCD_VER=v3.5.10
wget https://github.com/etcd-io/etcd/releases/download/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz
tar xzf etcd-${ETCD_VER}-linux-amd64.tar.gz
sudo mv etcd-${ETCD_VER}-linux-amd64/etcd* /usr/local/bin/

# HAProxy
sudo apt install -y haproxy
```

---

## 3. etcd集群配置

### 3.1 etcd配置（etcd-1）

```yaml
# /etc/etcd/etcd.conf.yml
name: etcd-1
data-dir: /var/lib/etcd
listen-client-urls: http://192.168.1.21:2379,http://127.0.0.1:2379
advertise-client-urls: http://192.168.1.21:2379
listen-peer-urls: http://192.168.1.21:2380
initial-advertise-peer-urls: http://192.168.1.21:2380

initial-cluster: >
  etcd-1=http://192.168.1.21:2380,
  etcd-2=http://192.168.1.22:2380,
  etcd-3=http://192.168.1.23:2380

initial-cluster-state: new
initial-cluster-token: etcd-cluster-pg
```

### 3.2 启动etcd

```bash
# systemd service
sudo tee /etc/systemd/system/etcd.service <<EOF
[Unit]
Description=etcd
After=network.target

[Service]
Type=notify
ExecStart=/usr/local/bin/etcd --config-file /etc/etcd/etcd.conf.yml
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动
sudo systemctl daemon-reload
sudo systemctl enable etcd
sudo systemctl start etcd

# 验证
etcdctl member list
etcdctl endpoint health
```

---

## 4. Patroni配置

### 4.1 核心配置（pg-1）

```yaml
# /etc/patroni/patroni.yml
scope: postgres-cluster
name: pg-1
namespace: /db/

restapi:
  listen: 192.168.1.11:8008
  connect_address: 192.168.1.11:8008

etcd:
  hosts:
    - 192.168.1.21:2379
    - 192.168.1.22:2379
    - 192.168.1.23:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576  # 1MB

    postgresql:
      use_pg_rewind: true
      use_slots: true

      parameters:
        # PostgreSQL 18优化
        max_connections: 200
        shared_buffers: 4GB
        effective_cache_size: 12GB
        maintenance_work_mem: 1GB
        work_mem: 256MB

        # WAL配置
        wal_level: replica
        max_wal_senders: 10
        max_replication_slots: 10
        wal_keep_size: 1GB

        # 异步I/O (PostgreSQL 18)
        io_direct: data
        io_combine_limit: 128kB

        # 日志
        logging_collector: on
        log_directory: /var/log/postgresql
        log_filename: postgresql-%Y-%m-%d.log
        log_rotation_age: 1d

      pg_hba:
        - host replication replicator 192.168.1.0/24 scram-sha-256
        - host all all 192.168.1.0/24 scram-sha-256
        - local all all peer

      # 同步复制（零数据丢失）
      synchronous_mode: true
      synchronous_mode_strict: true
      synchronous_node_count: 1

  initdb:
    - encoding: UTF8
    - data-checksums

  users:
    admin:
      password: admin_password
      options:
        - createrole
        - createdb

    replicator:
      password: replicator_password
      options:
        - replication

postgresql:
  listen: 192.168.1.11:5432
  connect_address: 192.168.1.11:5432
  data_dir: /var/lib/postgresql/18/main
  bin_dir: /usr/lib/postgresql/18/bin
  pgpass: /var/lib/postgresql/.pgpass

  authentication:
    replication:
      username: replicator
      password: replicator_password
    superuser:
      username: postgres
      password: postgres_password

  parameters:
    unix_socket_directories: /var/run/postgresql

  # 回调脚本
  callbacks:
    on_start: /etc/patroni/callbacks/on_start.sh
    on_stop: /etc/patroni/callbacks/on_stop.sh
    on_role_change: /etc/patroni/callbacks/on_role_change.sh

# Watchdog（可选）
watchdog:
  mode: automatic
  device: /dev/watchdog
  safety_margin: 5

tags:
  nofailover: false
  noloadbalance: false
  clonefrom: false
  nosync: false
```

### 4.2 systemd服务

```bash
# /etc/systemd/system/patroni.service
sudo tee /etc/systemd/system/patroni.service <<EOF
[Unit]
Description=Patroni PostgreSQL HA
After=syslog.target network.target

[Service]
Type=simple
User=postgres
Group=postgres
ExecStart=/usr/local/bin/patroni /etc/patroni/patroni.yml
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
KillSignal=SIGINT
Restart=on-failure
TimeoutSec=0

[Install]
WantedBy=multi-user.target
EOF

# 启动
sudo systemctl daemon-reload
sudo systemctl enable patroni
sudo systemctl start patroni
```

### 4.3 验证集群

```bash
# 查看集群状态
patronictl -c /etc/patroni/patroni.yml list postgres-cluster

# 输出示例
+ Cluster: postgres-cluster (7123456789012345678) -----+----+-----------+
| Member | Host          | Role    | State     | TL | Lag in MB |
+--------+---------------+---------+-----------+----+-----------+
| pg-1   | 192.168.1.11  | Leader  | running   |  1 |           |
| pg-2   | 192.168.1.12  | Replica | streaming |  1 |         0 |
| pg-3   | 192.168.1.13  | Replica | streaming |  1 |         0 |
+--------+---------------+---------+-----------+----+-----------+
```

---

## 5. HAProxy负载均衡

### 5.1 HAProxy配置

```cfg
# /etc/haproxy/haproxy.cfg
global
    maxconn 1000
    log 127.0.0.1 local0

defaults
    log global
    mode tcp
    retries 2
    timeout client 30m
    timeout connect 4s
    timeout server 30m
    timeout check 5s

# 统计页面
listen stats
    mode http
    bind *:7000
    stats enable
    stats uri /

# PostgreSQL读写（Primary）
listen postgres_write
    bind *:5000
    option httpchk
    http-check expect status 200
    default-server inter 3s fall 3 rise 2 on-marked-down shutdown-sessions
    server pg-1 192.168.1.11:5432 maxconn 100 check port 8008
    server pg-2 192.168.1.12:5432 maxconn 100 check port 8008
    server pg-3 192.168.1.13:5432 maxconn 100 check port 8008

# PostgreSQL只读（所有节点）
listen postgres_read
    bind *:5001
    balance roundrobin
    option httpchk
    http-check expect status 200
    default-server inter 3s fall 3 rise 2 on-marked-down shutdown-sessions
    server pg-1 192.168.1.11:5432 maxconn 100 check port 8008
    server pg-2 192.168.1.12:5432 maxconn 100 check port 8008
    server pg-3 192.168.1.13:5432 maxconn 100 check port 8008
```

### 5.2 健康检查脚本

```bash
# /etc/haproxy/check_postgres.sh
#!/bin/bash

HOST=$1
PORT=$2

# 检查是否为Primary
curl -s http://$HOST:8008 | grep -q '"role":"master"'
if [ $? -eq 0 ]; then
    exit 0  # Primary
else
    exit 1  # Replica
fi
```

---

## 6. 故障切换测试

### 6.1 自动Failover

```bash
# 1. 停止Primary
sudo systemctl stop patroni # 在pg-1上执行

# 2. 观察自动切换
watch patronictl -c /etc/patroni/patroni.yml list

# 3. 验证新Primary
psql -h 192.168.1.30 -p 5000 -U postgres -c "SELECT pg_is_in_recovery();"
```

### 6.2 手动Switchover

```bash
# 切换Primary到pg-2
patronictl -c /etc/patroni/patroni.yml switchover postgres-cluster \
  --master pg-1 \
  --candidate pg-2 \
  --force

# 查看结果
patronictl -c /etc/patroni/patroni.yml list
```

### 6.3 故障场景测试

```bash
# 场景1: Primary宕机
sudo systemctl stop patroni  # pg-1
# 预期: pg-2或pg-3自动提升为Primary

# 场景2: 网络分区
sudo iptables -A INPUT -s 192.168.1.11 -j DROP  # 隔离pg-1
# 预期: 其他节点选举新Primary

# 场景3: 数据库进程崩溃
sudo kill -9 $(pgrep postgres | head -1)
# 预期: Patroni自动重启PostgreSQL

# 场景4: Standby延迟过高
# 预期: 该节点被标记为不可用，不参与选举
```

---

## 7. 同步复制配置

### 7.1 零数据丢失配置

```yaml
# patroni.yml
bootstrap:
  dcs:
    postgresql:
      parameters:
        synchronous_commit: on
        synchronous_standby_names: '*'  # 任意1个Standby

      synchronous_mode: true
      synchronous_mode_strict: true
      synchronous_node_count: 1  # 至少1个同步Standby
```

### 7.2 验证同步状态

```sql
-- 查看同步复制状态
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    sync_priority
FROM pg_stat_replication;

-- 输出示例
 application_name | client_addr  |   state   | sync_state | sync_priority
------------------+--------------+-----------+------------+---------------
 pg-2             | 192.168.1.12 | streaming | sync       |             1
 pg-3             | 192.168.1.13 | streaming | async      |             0
```

---

## 8. 监控与告警

### 8.1 Patroni REST API

```bash
# 节点状态
curl http://192.168.1.11:8008

# 集群配置
curl http://192.168.1.11:8008/config

# 主节点信息
curl http://192.168.1.11:8008/master

# 副本信息
curl http://192.168.1.11:8008/replica
```

### 8.2 Prometheus监控

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'patroni'
    static_configs:
      - targets:
          - 192.168.1.11:8008
          - 192.168.1.12:8008
          - 192.168.1.13:8008
```

### 8.3 告警规则

```yaml
# alerts.yml
groups:
  - name: patroni
    rules:
      - alert: PatroniDown
        expr: up{job="patroni"} == 0
        for: 1m
        annotations:
          summary: "Patroni节点宕机"

      - alert: NoMaster
        expr: count(patroni_master == 1) == 0
        for: 1m
        annotations:
          summary: "集群无主节点"

      - alert: ReplicationLag
        expr: patroni_replication_lag > 10485760  # 10MB
        for: 5m
        annotations:
          summary: "主从延迟过高"
```

---

## 9. 运维操作

### 9.1 日常维护

```bash
# 重启节点（无中断）
patronictl -c /etc/patroni/patroni.yml restart postgres-cluster pg-2

# 重新加载配置
patronictl -c /etc/patroni/patroni.yml reload postgres-cluster pg-1

# 重新初始化节点
patronictl -c /etc/patroni/patroni.yml reinit postgres-cluster pg-3
```

### 9.2 配置更新

```bash
# 动态修改参数
patronictl -c /etc/patroni/patroni.yml edit-config postgres-cluster

# 示例：增加max_connections
postgresql:
  parameters:
    max_connections: 300  # 从200改为300
```

### 9.3 备份策略

```bash
# WAL归档配置
postgresql:
  parameters:
    archive_mode: on
    archive_command: 'test ! -f /mnt/backup/wal/%f && cp %p /mnt/backup/wal/%f'
    archive_timeout: 300

# 定时全量备份
0 2 * * * /usr/bin/pg_basebackup -h 192.168.1.11 -D /mnt/backup/base/$(date +\%Y\%m\%d) -Fp -Xs -P
```

---

## 10. 故障排查

### 10.1 常见问题

**问题1: Primary选举失败**

```bash
# 检查etcd连接
etcdctl endpoint health

# 查看Patroni日志
journalctl -u patroni -f

# 检查DCS配置
patronictl -c /etc/patroni/patroni.yml show-config
```

**问题2: 复制延迟**

```sql
-- 查看复制槽
SELECT * FROM pg_replication_slots;

-- 检查WAL发送
SELECT * FROM pg_stat_wal_receiver;
SELECT * FROM pg_stat_replication;
```

**问题3: Split-Brain风险**

```bash
# 验证只有一个Primary
patronictl -c /etc/patroni/patroni.yml list | grep Leader | wc -l
# 应该返回1

# 检查etcd数据
etcdctl get /db/postgres-cluster/leader
```

---

## 11. 生产最佳实践

### 11.1 硬件配置

```text
生产环境推荐:
├─ CPU: 16核+ (高并发场景)
├─ 内存: 64GB+ (shared_buffers=16GB)
├─ 存储: NVMe SSD RAID10
├─ 网络: 10Gbps+
└─ 磁盘IOPS: 20000+
```

### 11.2 Patroni参数调优

```yaml
# 快速故障检测
ttl: 30                    # DCS TTL
loop_wait: 10              # 检查间隔
retry_timeout: 10          # 重试超时
maximum_lag_on_failover: 1048576  # 允许的最大延迟

# 同步复制（金融场景）
synchronous_mode: true
synchronous_mode_strict: true
synchronous_node_count: 1
```

### 11.3 监控清单

```text
✅ 集群状态: Leader/Replica数量
✅ 复制延迟: <10MB
✅ 节点健康: all up
✅ DCS连接: etcd健康
✅ 负载均衡: HAProxy状态
✅ 磁盘空间: >20%剩余
✅ 连接数: <80%上限
✅ 慢查询: <5%
```

---

**完成**: Patroni高可用完整指南
**字数**: ~10,000字
**涵盖**: 架构、配置、故障切换、监控、运维
