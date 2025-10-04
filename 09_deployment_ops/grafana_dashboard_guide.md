# 📊 PostgreSQL 17 Grafana Dashboard 实施指南

**文档版本**：v1.0  
**创建日期**：2025年10月3日  
**适用版本**：PostgreSQL 17.x + Grafana 10.x+

---

## 🎯 目标

基于 `monitoring_queries.sql` 中的35+监控SQL，创建一个生产级的Grafana Dashboard，实现PostgreSQL 17集群的实时监控。

---

## 📋 前置要求

### 环境要求

- ✅ PostgreSQL 17.x（已安装并运行）
- ✅ Grafana 10.x+（推荐最新版本）
- ✅ PostgreSQL数据源插件（Grafana内置）
- ✅ 监控用户权限（只读访问系统视图）

### 监控用户创建

```sql
-- 创建监控用户
CREATE ROLE grafana_monitor WITH LOGIN PASSWORD 'your_secure_password';

-- 授予必要权限
GRANT CONNECT ON DATABASE your_database TO grafana_monitor;
GRANT USAGE ON SCHEMA pg_catalog TO grafana_monitor;
GRANT pg_monitor TO grafana_monitor;  -- PostgreSQL 10+

-- 如果需要监控特定schema的表
GRANT USAGE ON SCHEMA public TO grafana_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana_monitor;
```

---

## 🏗️ Dashboard 架构设计

### 6大监控面板

```text
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL 17 Production Monitoring Dashboard          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1️⃣ 连接与会话监控 (Connection & Session)                │
│  2️⃣ 性能与查询监控 (Performance & Query)                 │
│  3️⃣ 锁与阻塞监控 (Locks & Blocking)                      │
│  4️⃣ 存储与表监控 (Storage & Tables)                      │
│  5️⃣ 复制与备份监控 (Replication & Backup)               │
│  6️⃣ 资源与系统监控 (Resources & System)                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 面板1：连接与会话监控

### Panel 1.1：当前连接数

**查询SQL**：

```sql
SELECT 
    COUNT(*) as connections,
    NOW() as time
FROM pg_stat_activity
WHERE state IS NOT NULL;
```

**可视化**：Stat（单一数值）
**阈值**：

- 🟢 正常：< 80%
- 🟡 警告：80-90%
- 🔴 严重：> 90%

**配置**：

```json
{
  "type": "stat",
  "title": "当前连接数",
  "targets": [
    {
      "refId": "A",
      "rawSql": "SELECT COUNT(*) as connections, NOW() as time FROM pg_stat_activity WHERE state IS NOT NULL;",
      "format": "time_series"
    }
  ],
  "options": {
    "reduceOptions": {
      "values": false,
      "calcs": ["lastNotNull"]
    }
  },
  "fieldConfig": {
    "defaults": {
      "thresholds": {
        "mode": "percentage",
        "steps": [
          { "value": 0, "color": "green" },
          { "value": 80, "color": "yellow" },
          { "value": 90, "color": "red" }
        ]
      },
      "max": 100
    }
  }
}
```

---

### Panel 1.2：连接状态分布

**查询SQL**：

```sql
SELECT 
    state,
    COUNT(*) as count,
    NOW() as time
FROM pg_stat_activity
WHERE state IS NOT NULL
GROUP BY state;
```

**可视化**：Pie Chart（饼图）

---

### Panel 1.3：数据库连接分布

**查询SQL**：

```sql
SELECT 
    datname,
    COUNT(*) as connections,
    NOW() as time
FROM pg_stat_activity
WHERE datname IS NOT NULL
GROUP BY datname
ORDER BY connections DESC;
```

**可视化**：Bar Chart（柱状图）

---

### Panel 1.4：活跃连接时间分布

**查询SQL**：

```sql
SELECT 
    CASE 
        WHEN state_change < NOW() - INTERVAL '5 minutes' THEN '> 5分钟'
        WHEN state_change < NOW() - INTERVAL '1 minute' THEN '1-5分钟'
        ELSE '< 1分钟'
    END as duration_bucket,
    COUNT(*) as count,
    NOW() as time
FROM pg_stat_activity
WHERE state = 'active'
GROUP BY duration_bucket;
```

**可视化**：Bar Chart（柱状图）

---

## 📊 面板2：性能与查询监控

### Panel 2.1：TPS（每秒事务数）

**查询SQL**：

```sql
SELECT 
    datname,
    (xact_commit + xact_rollback) as tps,
    NOW() as time
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1', 'postgres')
ORDER BY tps DESC;
```

**可视化**：Time series（时间序列图）
**刷新率**：5s

---

### Panel 2.2：TOP 10 慢查询

**查询SQL**：

```sql
SELECT 
    query,
    calls,
    ROUND(mean_exec_time::numeric, 2) as avg_time_ms,
    ROUND(total_exec_time::numeric, 2) as total_time_ms,
    NOW() as time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**可视化**：Table（表格）
**注意**：需要安装 `pg_stat_statements` 扩展

---

### Panel 2.3：缓存命中率

**查询SQL**：

```sql
SELECT 
    datname,
    ROUND(
        100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2
    ) as cache_hit_ratio,
    NOW() as time
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1', 'postgres')
  AND (blks_hit + blks_read) > 0
ORDER BY cache_hit_ratio DESC;
```

**可视化**：Gauge（仪表盘）
**目标**：> 95%

---

### Panel 2.4：查询执行时间分布

**查询SQL**：

```sql
SELECT 
    CASE 
        WHEN mean_exec_time < 1 THEN '< 1ms'
        WHEN mean_exec_time < 10 THEN '1-10ms'
        WHEN mean_exec_time < 100 THEN '10-100ms'
        WHEN mean_exec_time < 1000 THEN '100ms-1s'
        ELSE '> 1s'
    END as time_bucket,
    COUNT(*) as query_count,
    NOW() as time
FROM pg_stat_statements
GROUP BY time_bucket;
```

**可视化**：Bar Chart（柱状图）

---

## 📊 面板3：锁与阻塞监控

### Panel 3.1：当前锁数量

**查询SQL**：

```sql
SELECT 
    mode,
    COUNT(*) as lock_count,
    NOW() as time
FROM pg_locks
WHERE granted = true
GROUP BY mode
ORDER BY lock_count DESC;
```

**可视化**：Bar Chart（柱状图）

---

### Panel 3.2：阻塞会话

**查询SQL**：

```sql
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_query,
    blocking_activity.query AS blocking_query,
    NOW() as time
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

**可视化**：Table（表格）
**告警**：有阻塞时发送通知

---

### Panel 3.3：死锁统计

**查询SQL**：

```sql
SELECT 
    datname,
    deadlocks,
    NOW() as time
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1', 'postgres')
ORDER BY deadlocks DESC;
```

**可视化**：Time series（时间序列图）

---

## 📊 面板4：存储与表监控

### Panel 4.1：数据库大小

**查询SQL**：

```sql
SELECT 
    datname,
    pg_size_pretty(pg_database_size(datname)) as size_pretty,
    pg_database_size(datname) as size_bytes,
    NOW() as time
FROM pg_database
WHERE datname NOT IN ('template0', 'template1', 'postgres')
ORDER BY size_bytes DESC;
```

**可视化**：Bar Chart（柱状图）

---

### Panel 4.2：TOP 10 最大表

**查询SQL**：

```sql
SELECT 
    schemaname || '.' || tablename as table_name,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size_pretty,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
    NOW() as time
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY size_bytes DESC
LIMIT 10;
```

**可视化**：Table（表格）

---

### Panel 4.3：表膨胀率

**查询SQL**：

```sql
SELECT 
    schemaname || '.' || tablename as table_name,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) as bloat_ratio,
    n_dead_tup,
    n_live_tup,
    NOW() as time
FROM pg_stat_user_tables
WHERE n_live_tup > 0
ORDER BY bloat_ratio DESC
LIMIT 10;
```

**可视化**：Table（表格）
**告警**：bloat_ratio > 20%

---

### Panel 4.4：VACUUM活动

**查询SQL**：

```sql
SELECT 
    schemaname || '.' || relname as table_name,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count,
    NOW() as time
FROM pg_stat_user_tables
ORDER BY last_autovacuum DESC NULLS LAST
LIMIT 20;
```

**可视化**：Table（表格）

---

## 📊 面板5：复制与备份监控

### Panel 5.1：复制延迟

**查询SQL**（主库执行）：

```sql
SELECT 
    application_name,
    client_addr,
    state,
    COALESCE(
        EXTRACT(EPOCH FROM (NOW() - replay_lag))::int, 0
    ) as lag_seconds,
    NOW() as time
FROM pg_stat_replication;
```

**可视化**：Time series（时间序列图）
**告警**：lag_seconds > 60

---

### Panel 5.2：WAL生成速率

**查询SQL**：

```sql
SELECT 
    (pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') / 1024 / 1024) as wal_mb,
    NOW() as time;
```

**可视化**：Time series（时间序列图）

---

### Panel 5.3：备库状态

**查询SQL**（备库执行）：

```sql
SELECT 
    CASE WHEN pg_is_in_recovery() THEN '备库' ELSE '主库' END as role,
    pg_last_wal_receive_lsn() as receive_lsn,
    pg_last_wal_replay_lsn() as replay_lsn,
    EXTRACT(EPOCH FROM (NOW() - pg_last_xact_replay_timestamp()))::int as replay_lag_seconds,
    NOW() as time
WHERE pg_is_in_recovery();
```

**可视化**：Stat（单一数值）

---

## 📊 面板6：资源与系统监控

### Panel 6.1：数据库连接占用率

**查询SQL**：

```sql
SELECT 
    (SELECT COUNT(*) FROM pg_stat_activity)::float / 
    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') * 100 
    as connection_usage_percent,
    NOW() as time;
```

**可视化**：Gauge（仪表盘）
**阈值**：

- 🟢 < 70%
- 🟡 70-85%
- 🔴 > 85%

---

### Panel 6.2：临时文件使用

**查询SQL**：

```sql
SELECT 
    datname,
    pg_size_pretty(temp_bytes) as temp_size,
    temp_files,
    NOW() as time
FROM pg_stat_database
WHERE temp_bytes > 0
ORDER BY temp_bytes DESC;
```

**可视化**：Table（表格）

---

### Panel 6.3：检查点统计

**查询SQL**：

```sql
SELECT 
    checkpoints_timed,
    checkpoints_req,
    checkpoint_write_time,
    checkpoint_sync_time,
    NOW() as time
FROM pg_stat_bgwriter;
```

**可视化**：Time series（时间序列图）

---

### Panel 6.4：后台写进程统计

**查询SQL**：

```sql
SELECT 
    buffers_checkpoint,
    buffers_clean,
    buffers_backend,
    buffers_alloc,
    NOW() as time
FROM pg_stat_bgwriter;
```

**可视化**：Time series（时间序列图）

---

## 🔧 Dashboard JSON配置

### 基础配置结构

```json
{
  "dashboard": {
    "title": "PostgreSQL 17 Production Monitoring",
    "tags": ["postgresql", "database", "monitoring"],
    "timezone": "browser",
    "schemaVersion": 38,
    "version": 1,
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      // 面板配置将在下面定义
    ]
  }
}
```

---

## 📝 实施步骤

### 步骤1：安装Grafana（如果未安装）

```bash
# Ubuntu/Debian
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb <https://packages.grafana.com/oss/deb> stable main"
wget -q -O - <https://packages.grafana.com/gpg.key> | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# 启动服务
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# 访问 <http://localhost:3000>
# 默认账号：admin/admin
```

---

### 步骤2：配置PostgreSQL数据源

1. 登录Grafana（<http://localhost:3000）>
2. 导航到：Configuration → Data Sources
3. 点击 "Add data source"
4. 选择 "PostgreSQL"
5. 配置连接：

    ```yaml
    Name: PostgreSQL-Prod
    Host: localhost:5432
    Database: your_database
    User: grafana_monitor
    Password: your_secure_password
    SSL Mode: disable  # 或根据需要配置
    Version: 17.x
    ```

6. 点击 "Save & Test"

---

### 步骤3：创建Dashboard

1. 点击 "+" → "Dashboard"
2. 点击 "Add new panel"
3. 在Query编辑器中选择PostgreSQL数据源
4. 输入上面定义的SQL查询
5. 配置可视化类型和选项
6. 重复以上步骤添加所有面板

---

### 步骤4：配置告警（可选）

**告警规则示例**：

```yaml
# 连接数告警
Alert Name: High Connection Usage
Condition: 
  - When: last()
  - Of: A (connections query)
  - Is Above: 80
  - For: 5m
Notifications:
  - Send to: Email/Slack/PagerDuty
Message: PostgreSQL连接数超过80%
```

---

## 🎨 Dashboard 布局建议

```text
┌─────────────────────────────────────────────────────────┐
│  Row 1: 概览指标（4个Stat面板）                          │
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐              │
│  │连接数 │ │ TPS   │ │缓存率 │ │复制延迟│              │
│  └───────┘ └───────┘ └───────┘ └───────┘              │
├─────────────────────────────────────────────────────────┤
│  Row 2: 连接监控（宽度比例：6:6）                        │
│  ┌─────────────────┐ ┌─────────────────┐              │
│  │连接状态分布（饼）│ │数据库连接（柱）  │              │
│  └─────────────────┘ └─────────────────┘              │
├─────────────────────────────────────────────────────────┤
│  Row 3: 性能监控（宽度比例：12）                         │
│  ┌─────────────────────────────────────┐              │
│  │ TOP 10 慢查询（表格）                │              │
│  └─────────────────────────────────────┘              │
├─────────────────────────────────────────────────────────┤
│  Row 4: 锁与存储（宽度比例：6:6）                        │
│  ┌─────────────────┐ ┌─────────────────┐              │
│  │锁统计（柱状图）  │ │TOP 10表（表格）  │              │
│  └─────────────────┘ └─────────────────┘              │
├─────────────────────────────────────────────────────────┤
│  Row 5: 时间序列（宽度比例：12）                         │
│  ┌─────────────────────────────────────┐              │
│  │ TPS / 缓存命中率 / 复制延迟（曲线）   │              │
│  └─────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

## ⚠️ 注意事项

### 性能影响

1. **监控查询优化**
   - 所有查询都应该很轻量（< 100ms）
   - 避免频繁查询大表
   - 使用适当的刷新间隔（建议30s-1m）

2. **pg_stat_statements配置**

   ```sql
   -- postgresql.conf
   shared_preload_libraries = 'pg_stat_statements'
   pg_stat_statements.max = 10000
   pg_stat_statements.track = all
   ```

3. **监控用户权限最小化**
   - 只授予必要的只读权限
   - 不要使用超级用户

---

## 🔐 安全建议

1. **使用SSL连接**

   ```yaml
   SSL Mode: require
   SSL Cert: /path/to/client-cert.pem
   SSL Key: /path/to/client-key.pem
   SSL Root Cert: /path/to/root.crt
   ```

2. **密码管理**
   - 使用强密码
   - 定期轮换密码
   - 考虑使用密钥管理系统

3. **网络隔离**
   - Grafana和PostgreSQL在同一内网
   - 使用防火墙限制访问

---

## 📦 交付清单

完成本指南后，您将拥有：

- ✅ 完整的6大监控面板
- ✅ 24个核心监控图表
- ✅ 生产级告警规则
- ✅ Dashboard JSON配置文件
- ✅ 完整的使用文档

---

## 🚀 下一步

1. **测试Dashboard**
   - 在测试环境验证所有面板
   - 调整刷新间隔和阈值

2. **配置告警**
   - 设置关键指标告警
   - 测试告警通知

3. **优化性能**
   - 监控Dashboard自身的性能影响
   - 优化慢查询

4. **文档化**
   - 记录自定义配置
   - 编写运维手册

---

**文档维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025年10月3日  
**相关文档**：

- [monitoring_metrics.md](monitoring_metrics.md)
- [monitoring_queries.sql](monitoring_queries.sql)
- [HANDOVER_DOCUMENT.md](../HANDOVER_DOCUMENT.md)
