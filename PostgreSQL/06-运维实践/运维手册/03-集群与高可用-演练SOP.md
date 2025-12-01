# 集群与高可用-演练SOP（Runbook）

> **文档版本**: v1.0
> **最后更新**: 2025-11-22
> **PostgreSQL版本**: 18.x (推荐) ⭐ | 17.x (推荐) | 16.x (兼容)
> 参考：`../../05-部署架构/集群部署/05.04-集群部署与高可用.md`

---

## 📋 目录

- [集群与高可用-演练SOP（Runbook）](#集群与高可用-演练soprunbook)
  - [📋 目录](#-目录)
  - [1. 目标](#1-目标)
  - [2. 演练准备](#2-演练准备)
    - [2.1 演练前检查清单](#21-演练前检查清单)
    - [2.2 业务准备](#22-业务准备)
  - [3. 步骤](#3-步骤)
    - [3.1 故障切换演练（Patroni环境）](#31-故障切换演练patroni环境)
    - [3.2 故障切换演练（流复制环境）](#32-故障切换演练流复制环境)
    - [3.3 验证步骤](#33-验证步骤)
    - [3.4 旧主恢复为副本](#34-旧主恢复为副本)
  - [4. 回滚与复盘](#4-回滚与复盘)
    - [4.1 回滚步骤](#41-回滚步骤)
    - [4.2 演练报告模板](#42-演练报告模板)
    - [4.3 RTO/RPO计算](#43-rtorpo计算)
    - [4.4 演练频率建议](#44-演练频率建议)
    - [4.5 自动化演练脚本](#45-自动化演练脚本)

---

## 1. 目标

- 定期演练主故障切换，验证 RTO/RPO，确保读写分离策略有效。
- 验证自动故障转移机制，确保业务连续性。
- 验证数据一致性，确保无数据丢失。

## 2. 演练准备

- Patroni/etcd 集群健康；复制延迟 < 阈值；读写 VIP 配置正常；
- 业务灰度与只读副本路由策略确认；备份/回滚方案。

### 2.1 演练前检查清单

```sql
-- 1. 检查集群状态
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    sync_priority,
    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) as sent_lag_bytes,
    pg_wal_lsn_diff(sent_lsn, write_lsn) as write_lag_bytes,
    pg_wal_lsn_diff(write_lsn, flush_lsn) as flush_lag_bytes,
    pg_wal_lsn_diff(flush_lsn, replay_lsn) as replay_lag_bytes,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) as total_lag_bytes
FROM pg_stat_replication;

-- 2. 检查主库状态
SELECT
    pg_is_in_recovery() as is_standby,
    pg_current_wal_lsn() as current_lsn,
    pg_walfile_name(pg_current_wal_lsn()) as current_wal_file;

-- 3. 检查复制槽
SELECT
    slot_name,
    slot_type,
    database,
    active,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) as lag_bytes
FROM pg_replication_slots;

-- 4. 检查Patroni状态（如果使用Patroni）
-- patronictl list
-- 或通过API
-- curl http://patroni:8008/patroni
```

```bash
# 5. 检查VIP配置
ip addr show | grep vip

# 6. 检查负载均衡配置
# 检查HAProxy/PgBouncer配置
cat /etc/haproxy/haproxy.cfg | grep -A 10 "postgresql"

# 7. 记录当前时间点（用于RPO计算）
date +%Y-%m-%d\ %H:%M:%S > /tmp/failover_start_time.txt
psql -c "SELECT pg_current_wal_lsn();" > /tmp/failover_start_lsn.txt
```

### 2.2 业务准备

```bash
# 1. 通知业务方演练时间
# 2. 确认低峰期
# 3. 准备回滚方案
# 4. 准备监控面板
```

## 3. 步骤

1) 触发主下线（演练环境）：暂停/停止主节点服务；
2) 观察Leader 选举与复制追赶；
3) 验证：
   - 写连接是否切到新主（主写 VIP）；
   - 读连接是否仅路由到只读；
4) 旧主恢复为副本：基于 `pg_basebackup` 或增量追日志恢复；
5) 验证复制延迟、业务错误率。

### 3.1 故障切换演练（Patroni环境）

```bash
# 步骤1: 记录切换前状态
echo "=== Failover演练开始 ===" > /tmp/failover_log.txt
date >> /tmp/failover_log.txt
psql -h primary -c "SELECT pg_current_wal_lsn();" >> /tmp/failover_log.txt

# 步骤2: 触发主库故障（模拟）
# 方法1: 停止PostgreSQL服务
systemctl stop postgresql@14-main

# 方法2: 停止Patroni服务（推荐，更真实）
systemctl stop patroni

# 方法3: 网络隔离（最真实）
iptables -A INPUT -s <standby_ip> -j DROP

# 步骤3: 观察故障转移（等待30-60秒）
watch -n 1 'patronictl list'

# 或监控Patroni API
watch -n 1 'curl -s http://standby:8008/patroni | jq .role'

# 步骤4: 验证新主库状态
psql -h new_primary -c "SELECT pg_is_in_recovery();"
# 应该返回: f (false，表示是主库)

# 步骤5: 验证VIP切换
ip addr show | grep vip
# VIP应该已经切换到新主库

# 步骤6: 验证应用连接
psql -h vip_write -c "SELECT current_database(), inet_server_addr();"
# 应该连接到新主库

# 步骤7: 验证只读连接
psql -h vip_read -c "SELECT current_database(), inet_server_addr();"
# 应该连接到只读副本
```

### 3.2 故障切换演练（流复制环境）

```bash
# 步骤1: 记录切换前状态
psql -h primary -c "SELECT pg_current_wal_lsn();" > /tmp/primary_lsn.txt
psql -h standby -c "SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();" > /tmp/standby_lsn.txt

# 步骤2: 触发主库故障
systemctl stop postgresql@14-main

# 步骤3: 提升备库为主库
psql -h standby -c "SELECT pg_promote();"

# 步骤4: 验证提升成功
psql -h standby -c "SELECT pg_is_in_recovery();"
# 应该返回: f

# 步骤5: 更新应用连接配置
# 更新连接字符串指向新主库

# 步骤6: 验证数据一致性
psql -h new_primary -c "SELECT COUNT(*) FROM orders;"
# 对比切换前的数据量
```

### 3.3 验证步骤

```sql
-- 1. 验证新主库可写
CREATE TABLE failover_test (id SERIAL PRIMARY KEY, test_time TIMESTAMP DEFAULT NOW());
INSERT INTO failover_test DEFAULT VALUES;
SELECT * FROM failover_test;

-- 2. 验证只读副本可读
SET TRANSACTION READ ONLY;
SELECT COUNT(*) FROM orders;

-- 3. 验证复制状态（如果旧主已恢复为副本）
SELECT
    application_name,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) as lag_bytes
FROM pg_stat_replication;

-- 4. 验证数据完整性
-- 对比关键表的数据量
SELECT
    schemaname,
    tablename,
    n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC
LIMIT 10;

-- 5. 验证业务功能
-- 执行关键业务查询，确保功能正常
```

### 3.4 旧主恢复为副本

```bash
# 方法1: 使用pg_basebackup重建（如果数据损坏）
# 停止旧主库
systemctl stop postgresql@14-main

# 备份旧数据目录
mv /var/lib/postgresql/14/main /var/lib/postgresql/14/main.old

# 从新主库创建基础备份
pg_basebackup \
    -h new_primary \
    -U replication \
    -D /var/lib/postgresql/14/main \
    -X stream \
    -P \
    -R

# 配置恢复
cat > /var/lib/postgresql/14/main/postgresql.auto.conf <<EOF
primary_conninfo = 'host=new_primary port=5432 user=replication'
EOF

# 启动PostgreSQL
systemctl start postgresql@14-main

# 方法2: 使用WAL追赶（如果数据完整）
# 配置旧主库为副本
cat > /var/lib/postgresql/14/main/postgresql.auto.conf <<EOF
primary_conninfo = 'host=new_primary port=5432 user=replication'
EOF

# 创建standby.signal
touch /var/lib/postgresql/14/main/standby.signal

# 启动PostgreSQL
systemctl start postgresql@14-main
```

## 4. 回滚与复盘

- 异常则回切到原主（必要时手动 promote/demote），记录时间线与延迟；
- 输出演练报告：步骤用时、RTO/RPO、问题与改进项。

### 4.1 回滚步骤

```bash
# 如果演练失败，回切到原主库

# 步骤1: 停止新主库
systemctl stop postgresql@14-main

# 步骤2: 恢复原主库（如果使用Patroni）
patronictl switchover --force

# 或手动提升原主库
psql -h original_primary -c "SELECT pg_promote();"

# 步骤3: 验证VIP切换回原主
ip addr show | grep vip

# 步骤4: 验证应用连接
psql -h vip_write -c "SELECT current_database(), inet_server_addr();"
```

### 4.2 演练报告模板

```sql
-- 创建演练记录表
CREATE TABLE IF NOT EXISTS ha_drill_log (
    drill_id SERIAL PRIMARY KEY,
    drill_date TIMESTAMP DEFAULT NOW(),
    drill_type VARCHAR(50),  -- 'failover', 'switchover', 'network_partition'
    original_primary VARCHAR(100),
    new_primary VARCHAR(100),
    failover_time_seconds INTEGER,
    rto_seconds INTEGER,  -- Recovery Time Objective
    rpo_bytes BIGINT,     -- Recovery Point Objective (WAL lag)
    data_loss BOOLEAN,
    issues TEXT[],
    improvements TEXT[],
    drill_result VARCHAR(20)  -- 'success', 'partial', 'failed'
);

-- 记录演练结果
INSERT INTO ha_drill_log (
    drill_type,
    original_primary,
    new_primary,
    failover_time_seconds,
    rto_seconds,
    rpo_bytes,
    data_loss,
    issues,
    improvements,
    drill_result
)
VALUES (
    'failover',
    'primary1',
    'standby1',
    45,  -- 故障转移耗时45秒
    60,  -- RTO: 60秒
    0,   -- RPO: 0字节（无数据丢失）
    false,
    ARRAY['VIP切换延迟5秒', '应用连接池需要手动刷新'],
    ARRAY['优化VIP切换脚本', '实现自动连接池刷新'],
    'success'
);
```

### 4.3 RTO/RPO计算

```sql
-- RTO (Recovery Time Objective): 恢复时间目标
-- 从故障发生到服务恢复的时间

-- RPO (Recovery Point Objective): 恢复点目标
-- 允许丢失的数据量（WAL lag）

-- 计算RPO
SELECT
    pg_wal_lsn_diff(
        pg_current_wal_lsn(),
        pg_last_wal_replay_lsn()
    ) as rpo_bytes,
    pg_size_pretty(
        pg_wal_lsn_diff(
            pg_current_wal_lsn(),
            pg_last_wal_replay_lsn()
        )
    ) as rpo_size;

-- 记录RTO/RPO指标
SELECT
    drill_date,
    drill_type,
    failover_time_seconds as rto_seconds,
    pg_size_pretty(rpo_bytes) as rpo_size,
    data_loss,
    drill_result
FROM ha_drill_log
ORDER BY drill_date DESC
LIMIT 10;
```

### 4.4 演练频率建议

```bash
# 月度演练：故障切换
# 每月的第一个周末执行
0 2 1 * * /usr/local/bin/ha_failover_drill.sh

# 季度演练：网络分区
# 每季度执行一次网络分区演练
0 2 1 */3 * /usr/local/bin/ha_network_partition_drill.sh

# 年度演练：灾难恢复
# 每年执行一次完整的灾难恢复演练
```

### 4.5 自动化演练脚本

```bash
#!/bin/bash
# ha_failover_drill.sh

LOG_FILE="/var/log/postgresql/ha_drill.log"
DRILL_START=$(date +%s)

echo "$(date): Starting HA failover drill" >> ${LOG_FILE}

# 1. 记录开始状态
ORIGINAL_PRIMARY=$(psql -t -c "SELECT inet_server_addr();" | xargs)
ORIGINAL_LSN=$(psql -t -c "SELECT pg_current_wal_lsn();" | xargs)

# 2. 触发故障
echo "$(date): Stopping primary node" >> ${LOG_FILE}
systemctl stop postgresql@14-main

# 3. 等待故障转移
sleep 30

# 4. 验证新主库
NEW_PRIMARY=$(psql -h standby -t -c "SELECT inet_server_addr();" | xargs)
IS_PRIMARY=$(psql -h standby -t -c "SELECT pg_is_in_recovery();" | xargs)

if [ "${IS_PRIMARY}" = "f" ]; then
    DRILL_END=$(date +%s)
    RTO=$((DRILL_END - DRILL_START))

    echo "$(date): Failover successful" >> ${LOG_FILE}
    echo "RTO: ${RTO} seconds" >> ${LOG_FILE}

    # 记录到数据库
    psql -c "INSERT INTO ha_drill_log (drill_type, original_primary, new_primary, failover_time_seconds, rto_seconds, drill_result) VALUES ('failover', '${ORIGINAL_PRIMARY}', '${NEW_PRIMARY}', ${RTO}, ${RTO}, 'success');"
else
    echo "$(date): Failover failed!" >> ${LOG_FILE}
    exit 1
fi

# 5. 恢复原主库
echo "$(date): Restoring original primary" >> ${LOG_FILE}
# 执行恢复步骤...
```
