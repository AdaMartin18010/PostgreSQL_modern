# ✅ PostgreSQL 17 生产环境部署检查清单

**文档版本**：v1.0  
**创建日期**：2025年10月3日  
**适用场景**：PostgreSQL 17.x 生产环境部署

---

## 🎯 目标

确保PostgreSQL 17在生产环境中安全、稳定、高性能地运行。

---

## 📋 部署前检查清单

### 阶段1：硬件与环境（必须）

#### 1.1 硬件资源

- [ ] **CPU**：至少4核，推荐8核以上
- [ ] **内存**：至少8GB，推荐32GB以上（根据数据量）
- [ ] **磁盘**：
  - [ ] 数据目录使用SSD（NVMe优先）
  - [ ] WAL目录单独磁盘（可选但推荐）
  - [ ] 至少100GB可用空间（根据数据量调整）
- [ ] **网络**：千兆网络，低延迟
- [ ] **RAID配置**：RAID 10（数据安全）或 RAID 0（性能优先）

**推荐配置**：
```yaml
生产环境（中型）:
  CPU: 16 cores
  RAM: 64GB
  Disk: 500GB NVMe SSD (RAID 10)
  Network: 10Gbps

生产环境（大型）:
  CPU: 32+ cores
  RAM: 128GB+
  Disk: 2TB+ NVMe SSD (RAID 10)
  Network: 10Gbps+
```

---

#### 1.2 操作系统

- [ ] **OS选择**：
  - [ ] Ubuntu 22.04 LTS / 24.04 LTS
  - [ ] RHEL 8/9 或 CentOS Stream
  - [ ] Debian 11/12
- [ ] **系统更新**：所有安全补丁已安装
- [ ] **时间同步**：NTP/Chrony已配置
- [ ] **防火墙**：已配置但PostgreSQL端口开放
- [ ] **SELinux/AppArmor**：已配置（如适用）

---

### 阶段2：PostgreSQL安装（必须）

#### 2.1 安装验证

- [ ] **版本确认**：PostgreSQL 17.x（最新补丁版本）
- [ ] **安装路径**：标准路径或自定义路径已记录
- [ ] **用户权限**：postgres用户和组已创建
- [ ] **目录权限**：
  - [ ] 数据目录：700权限
  - [ ] 配置文件：600权限
- [ ] **扩展安装**：
  - [ ] pg_stat_statements
  - [ ] pgvector（如需要）
  - [ ] PostGIS（如需要）
  - [ ] TimescaleDB（如需要）
  - [ ] Citus（如需要分布式）

**验证命令**：
```sql
-- 检查版本
SELECT version();

-- 检查已安装扩展
SELECT * FROM pg_available_extensions WHERE installed_version IS NOT NULL;

-- 检查数据目录
SHOW data_directory;
```

---

### 阶段3：配置优化（关键）

#### 3.1 postgresql.conf 核心参数

**内存配置**：

```ini
# 共享缓冲区（25%的RAM）
shared_buffers = 16GB  # 64GB RAM的情况

# 工作内存（根据并发查询调整）
work_mem = 64MB  # 复杂查询可能需要更多

# 维护工作内存
maintenance_work_mem = 2GB

# 有效缓存大小（50-75%的RAM）
effective_cache_size = 48GB
```

- [ ] `shared_buffers` 已设置（RAM的25%）
- [ ] `work_mem` 已设置（根据连接数）
- [ ] `maintenance_work_mem` 已设置（1-2GB）
- [ ] `effective_cache_size` 已设置（RAM的50-75%）

---

**连接配置**：

```ini
# 最大连接数
max_connections = 200  # 根据实际需求

# 连接保留（超级用户）
superuser_reserved_connections = 5
```

- [ ] `max_connections` 已设置（合理值）
- [ ] 连接池（PgBouncer/pgpool）已考虑

---

**WAL配置**：

```ini
# WAL级别（复制需要replica）
wal_level = replica

# WAL缓冲区
wal_buffers = 16MB

# 检查点
checkpoint_timeout = 15min
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_completion_target = 0.9

# WAL写入模式
wal_sync_method = fdatasync  # Linux最优
wal_compression = on  # PostgreSQL 9.5+
```

- [ ] `wal_level` 已设置
- [ ] 检查点参数已优化
- [ ] `wal_compression` 已启用

---

**查询规划器**：

```ini
# 随机页面成本（SSD使用）
random_page_cost = 1.1  # SSD优化（默认4.0）

# 有效IO并发
effective_io_concurrency = 200  # SSD

# 最大并行工作进程
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_worker_processes = 8
```

- [ ] `random_page_cost` 已针对SSD优化
- [ ] 并行查询参数已设置

---

**日志配置**：

```ini
# 日志配置
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB

# 日志内容
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_min_duration_statement = 1000  # 记录>1s的查询
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0

# 慢查询日志
log_statement = 'ddl'  # 记录所有DDL
```

- [ ] 日志收集已启用
- [ ] 慢查询日志已配置
- [ ] 日志轮转已配置

---

**自动清理（VACUUM）**：

```ini
# Autovacuum
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 30s

# VACUUM阈值
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_scale_factor = 0.05

# VACUUM成本限制
autovacuum_vacuum_cost_limit = 1000  # 更积极的VACUUM
```

- [ ] Autovacuum已启用
- [ ] 参数已根据负载调整

---

#### 3.2 pg_hba.conf 安全配置

**访问控制**：

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# 本地连接
local   all             postgres                                peer
local   all             all                                     scram-sha-256

# IPv4本地连接
host    all             all             127.0.0.1/32            scram-sha-256

# IPv4网络连接（生产环境）
hostssl all             all             10.0.0.0/8              scram-sha-256

# 复制连接
hostssl replication     replicator      10.0.0.0/8              scram-sha-256

# 拒绝所有其他
host    all             all             0.0.0.0/0               reject
```

- [ ] 使用 `scram-sha-256` 认证
- [ ] 强制SSL连接（hostssl）
- [ ] IP白名单已配置
- [ ] 禁止了不必要的访问

---

### 阶段4：安全加固（关键）

#### 4.1 SSL/TLS配置

- [ ] **SSL证书**：
  - [ ] 生成或获取SSL证书
  - [ ] 证书权限设置正确（600）
  - [ ] 证书路径已配置

**postgresql.conf**：
```ini
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
ssl_ca_file = '/path/to/root.crt'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on
ssl_min_protocol_version = 'TLSv1.2'
```

**生成自签名证书（测试用）**：
```bash
openssl req -new -x509 -days 365 -nodes -text \
  -out server.crt -keyout server.key \
  -subj "/CN=dbhost.example.com"
chmod 600 server.key
chown postgres:postgres server.key server.crt
```

---

#### 4.2 用户与权限

- [ ] **超级用户**：
  - [ ] postgres密码已修改（强密码）
  - [ ] 仅必要时使用
  
- [ ] **应用用户**：
  - [ ] 创建专用应用用户
  - [ ] 最小权限原则
  - [ ] 不授予超级用户权限

- [ ] **监控用户**：
  - [ ] 创建只读监控用户
  - [ ] 授予pg_monitor角色

**示例**：
```sql
-- 创建应用用户
CREATE ROLE app_user WITH LOGIN PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- 创建监控用户
CREATE ROLE monitor_user WITH LOGIN PASSWORD 'monitor_password';
GRANT pg_monitor TO monitor_user;
GRANT CONNECT ON DATABASE mydb TO monitor_user;
```

---

#### 4.3 网络安全

- [ ] **防火墙规则**：
  - [ ] 仅允许必要IP访问5432端口
  - [ ] 限制连接速率（防DDoS）

- [ ] **VPN/专线**：
  - [ ] 跨公网访问使用VPN
  - [ ] 或使用SSH隧道

---

### 阶段5：备份策略（必须）

#### 5.1 备份配置

- [ ] **基础备份**：
  - [ ] pg_basebackup已配置
  - [ ] 备份脚本已编写
  - [ ] 备份存储位置已确定

- [ ] **WAL归档**：
  - [ ] archive_mode = on
  - [ ] archive_command已配置
  - [ ] 归档存储空间充足

**postgresql.conf**：
```ini
# WAL归档
archive_mode = on
archive_command = 'test ! -f /mnt/backup/wal_archive/%f && cp %p /mnt/backup/wal_archive/%f'
archive_timeout = 300  # 5分钟
```

- [ ] **PITR准备**：
  - [ ] restore_command已测试
  - [ ] 恢复流程已文档化

**备份脚本示例**：
```bash
#!/bin/bash
# 每日基础备份
DATE=$(date +%Y%m%d)
BACKUP_DIR=/mnt/backup/base/$DATE

pg_basebackup -h localhost -U replicator -D $BACKUP_DIR \
  -Ft -z -Xs -P

# 保留7天备份
find /mnt/backup/base -type d -mtime +7 -exec rm -rf {} \;
```

---

#### 5.2 备份验证

- [ ] **定期测试**：
  - [ ] 每月恢复测试
  - [ ] 恢复时间测量（RTO）
  - [ ] 恢复点目标验证（RPO）

- [ ] **备份监控**：
  - [ ] 备份成功/失败告警
  - [ ] 备份空间监控
  - [ ] WAL归档延迟监控

---

### 阶段6：高可用性（推荐）

#### 6.1 主备复制

- [ ] **流复制配置**：
  - [ ] 主库已配置复制槽
  - [ ] 备库已配置recovery.conf
  - [ ] 复制用户已创建

**主库配置**：
```ini
# postgresql.conf
wal_level = replica
max_wal_senders = 10
wal_keep_size = 1GB  # PostgreSQL 13+
```

```sql
-- 创建复制用户
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'repl_password';

-- 创建复制槽
SELECT pg_create_physical_replication_slot('standby_slot');
```

**备库配置**：
```conf
# standby.signal (PostgreSQL 12+)
primary_conninfo = 'host=primary_ip port=5432 user=replicator password=repl_password'
primary_slot_name = 'standby_slot'
```

- [ ] **复制延迟监控**：
  - [ ] Grafana Dashboard已配置
  - [ ] 延迟告警已设置（>60s）

---

#### 6.2 故障转移

- [ ] **自动故障转移**：
  - [ ] Patroni / repmgr 已配置（可选）
  - [ ] 故障转移脚本已测试

- [ ] **手动故障转移流程**：
  - [ ] 流程已文档化
  - [ ] 团队已培训
  - [ ] 演练已完成

---

### 阶段7：监控与告警（必须）

#### 7.1 监控指标

- [ ] **Grafana Dashboard**：
  - [ ] 已导入grafana_dashboard.json
  - [ ] 数据源已配置
  - [ ] 所有面板正常显示

- [ ] **关键指标**：
  - [ ] 连接数
  - [ ] TPS
  - [ ] 缓存命中率
  - [ ] 复制延迟
  - [ ] 磁盘空间
  - [ ] 锁等待
  - [ ] 慢查询

---

#### 7.2 告警配置

- [ ] **高优先级告警**：
  - [ ] 数据库宕机
  - [ ] 主备复制中断
  - [ ] 磁盘空间<10%
  - [ ] 连接数>90%

- [ ] **中优先级告警**：
  - [ ] 复制延迟>60s
  - [ ] 慢查询>5s
  - [ ] 锁等待>1min
  - [ ] 死锁检测

- [ ] **告警渠道**：
  - [ ] Email
  - [ ] Slack/钉钉/企业微信
  - [ ] PagerDuty（7x24）

---

### 阶段8：性能优化（推荐）

#### 8.1 扩展安装

- [ ] **pg_stat_statements**：
```sql
CREATE EXTENSION pg_stat_statements;
```

- [ ] **定期分析**：
  - [ ] 每周慢查询分析
  - [ ] 每月性能基线对比

---

#### 8.2 索引优化

- [ ] **索引策略**：
  - [ ] 常用查询已创建索引
  - [ ] 无用索引已删除
  - [ ] 复合索引顺序已优化

**检查无用索引**：
```sql
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  AND indexname NOT LIKE '%_pkey'
  AND pg_stat_user_indexes.idx_scan = 0;
```

---

### 阶段9：文档与培训（必须）

#### 9.1 文档准备

- [ ] **部署文档**：
  - [ ] 架构图
  - [ ] 配置参数说明
  - [ ] 网络拓扑

- [ ] **运维手册**：
  - [ ] 日常维护流程
  - [ ] 故障处理流程
  - [ ] 备份恢复流程
  - [ ] 扩容流程

- [ ] **联系信息**：
  - [ ] DBA联系方式
  - [ ] 厂商支持（如有）
  - [ ] 应急响应流程

---

#### 9.2 团队培训

- [ ] **DBA培训**：
  - [ ] PostgreSQL 17新特性
  - [ ] 故障排查
  - [ ] 性能调优

- [ ] **开发团队培训**：
  - [ ] 连接池使用
  - [ ] SQL优化基础
  - [ ] 事务管理

---

### 阶段10：上线验证（必须）

#### 10.1 功能测试

- [ ] **连接测试**：
```bash
psql -h production_host -U app_user -d mydb -c "SELECT version();"
```

- [ ] **性能测试**：
  - [ ] pgbench基准测试
  - [ ] 应用压力测试
  - [ ] 并发测试

**pgbench示例**：
```bash
# 初始化
pgbench -i -s 100 mydb

# 测试（4个客户端，1000个事务）
pgbench -c 4 -t 1000 mydb
```

---

#### 10.2 灾难恢复演练

- [ ] **备份恢复测试**：
  - [ ] 完整恢复测试
  - [ ] PITR测试
  - [ ] 恢复时间记录

- [ ] **故障转移测试**：
  - [ ] 主库故障模拟
  - [ ] 自动/手动切换
  - [ ] 数据一致性验证

---

## 📊 部署检查总结

### 必须项（Must Have）

- [x] 硬件资源满足要求
- [x] PostgreSQL 17安装正确
- [x] 核心配置参数优化
- [x] SSL/TLS已配置
- [x] 备份策略已实施
- [x] 监控告警已配置
- [x] 文档已准备
- [x] 上线验证已完成

### 推荐项（Should Have）

- [ ] 主备复制已配置
- [ ] 自动故障转移已配置
- [ ] 连接池已配置
- [ ] 性能基线已建立

### 可选项（Nice to Have）

- [ ] 读写分离已实现
- [ ] 分布式扩展（Citus）
- [ ] AI向量搜索（pgvector）
- [ ] 时序数据（TimescaleDB）

---

## 🚀 部署后任务

### 第1周

- [ ] 监控所有指标，确认正常
- [ ] 收集性能基线数据
- [ ] 执行首次备份并验证
- [ ] 观察日志，处理警告

### 第1个月

- [ ] 优化慢查询
- [ ] 调整配置参数（如需要）
- [ ] 执行故障转移演练
- [ ] 审查访问日志

### 持续任务

- [ ] 每周：审查慢查询，优化索引
- [ ] 每月：备份恢复测试
- [ ] 每季度：容量规划评估
- [ ] 每年：灾难恢复演练

---

## 📚 参考文档

**项目内部文档**：
- [monitoring_metrics.md](monitoring_metrics.md) - 监控指标
- [monitoring_queries.sql](monitoring_queries.sql) - 监控SQL
- [grafana_dashboard_guide.md](grafana_dashboard_guide.md) - Dashboard指南
- [GRAFANA_QUICK_START.md](GRAFANA_QUICK_START.md) - 快速部署

**PostgreSQL官方文档**：
- 服务器配置: <https://www.postgresql.org/docs/17/runtime-config.html>
- 高可用性: <https://www.postgresql.org/docs/17/high-availability.html>
- 备份与恢复: <https://www.postgresql.org/docs/17/backup.html>

---

**文档维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025年10月3日  
**版本**：v1.0

---

🎯 **使用本检查清单，确保PostgreSQL 17生产环境部署的成功！**

