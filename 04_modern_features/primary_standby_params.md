# 主/从参数样例与连接配置片段（示例）

## 主库 postgresql.conf 片段

```text
wal_level = replica        # 或 logical（如需逻辑复制）
max_wal_senders = 16
max_replication_slots = 16
wal_keep_size = '1024MB'
synchronous_standby_names = 'FIRST 1 (standby1, standby2)'
archive_mode = on
archive_command = 'test ! -f /archive/%f && cp %p /archive/%f'
```

## 从库 postgresql.conf 片段

```text
hot_standby = on
primary_conninfo = 'host=PRIMARY_HOST port=5432 user=replicator password=*** sslmode=prefer'
primary_slot_name = 'standby1'
```

## 基础备份（示例）

```text
pg_basebackup -D /var/lib/postgresql/data -R -C -S standby1 -X stream
```

## 连接与负载均衡（示意）

- 应用 DSN：通过 LB/Proxy（如 pgbouncer/HAProxy）暴露读写入口与只读入口
- 读写分离：
  - 写：指向主库（或可写 VIP）
  - 读：指向只读副本池（健康检查/延迟阈值剔除）

```text
# pgbouncer.ini（片段）
[databases]
app_rw = host=rw-vip dbname=appdb
app_ro = host=ro-pool dbname=appdb
```
