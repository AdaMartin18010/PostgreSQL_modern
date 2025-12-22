# PostgreSQL 18 配置文件集合

本目录包含PostgreSQL 18生产环境的完整配置文件集合，开箱即用。

---

## 📂 目录结构

```
configs/
├── README.md                              # 本文件
├── postgresql-18-production.conf          # PostgreSQL主配置（生产优化）
├── pg_hba.conf                            # 客户端认证配置
├── docker-compose.yml                     # Docker Compose完整编排
├── prometheus.yml                         # Prometheus监控配置
│
├── init-scripts/                          # 数据库初始化脚本
│   ├── 01-create-extensions.sql          # 扩展安装
│   └── 02-create-roles.sql               # 角色和用户创建
│
└── alerts/                                # 告警规则
    └── postgresql-alerts.yml              # PostgreSQL告警规则
```

---

## 🚀 快速开始

### 方式1: Docker Compose（推荐）

```bash
# 1. 创建环境变量文件
cat > .env <<EOF
POSTGRES_PASSWORD=your_strong_password
PGADMIN_PASSWORD=your_admin_password
GRAFANA_PASSWORD=your_grafana_password
EOF

# 2. 启动所有服务
docker-compose up -d

# 3. 查看服务状态
docker-compose ps

# 4. 访问服务
# PostgreSQL: localhost:5432
# pgAdmin: http://localhost:5050
# Grafana: http://localhost:3000
```

### 方式2: 直接安装

```bash
# 1. 复制配置文件
sudo cp postgresql-18-production.conf /etc/postgresql/18/main/postgresql.conf
sudo cp pg_hba.conf /etc/postgresql/18/main/pg_hba.conf

# 2. 调整权限
sudo chown postgres:postgres /etc/postgresql/18/main/*.conf
sudo chmod 640 /etc/postgresql/18/main/*.conf

# 3. 创建备份目录
sudo mkdir -p /backup/wal
sudo chown postgres:postgres /backup/wal

# 4. 重启PostgreSQL
sudo systemctl restart postgresql

# 5. 运行初始化脚本
sudo -u postgres psql -f init-scripts/01-create-extensions.sql
sudo -u postgres psql -f init-scripts/02-create-roles.sql
```

---

## 📋 配置文件说明

### 1. postgresql-18-production.conf

**适用环境**: 64GB内存, 16核CPU, NVMe SSD

**核心优化**:
- ✅ PostgreSQL 18新特性（异步I/O、Skip Scan）
- ✅ 内存配置优化（shared_buffers=16GB）
- ✅ SSD优化（random_page_cost=1.1）
- ✅ 并行查询配置
- ✅ JIT编译启用
- ✅ 性能监控扩展

**关键参数**:
```conf
shared_buffers = 16GB
work_mem = 64MB
effective_cache_size = 48GB
io_direct = 'data,wal'           # PostgreSQL 18
enable_skip_scan = on             # PostgreSQL 18
random_page_cost = 1.1            # SSD
```

**修改指南**: 参考配置文件内的详细注释

---

### 2. pg_hba.conf

**安全配置**:
- ✅ 使用scram-sha-256认证（最安全）
- ✅ SSL强制连接
- ✅ IP地址白名单
- ✅ 超级用户仅本地访问
- ✅ 角色隔离

**认证方法对比**:
```
trust          - 无密码（危险，仅开发）
md5            - MD5加密（已过时）
scram-sha-256  - SCRAM认证（推荐）
cert           - SSL证书（最安全）
```

---

### 3. docker-compose.yml

**包含服务**:
- PostgreSQL 18 (主服务)
- pgAdmin 4 (Web管理)
- pgBouncer (连接池)
- Prometheus (指标收集)
- Grafana (可视化)
- postgres_exporter (指标导出)

**服务端口**:
```
PostgreSQL:      5432
pgAdmin:         5050
pgBouncer:       6432
Prometheus:      9090
Grafana:         3000
```

**常用命令**:
```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f postgres

# 备份
docker-compose exec postgres pg_dump -U postgres mydb > backup.sql

# 停止
docker-compose down
```

---

### 4. prometheus.yml

**监控指标**:
- PostgreSQL核心指标（连接、TPS、缓存命中率）
- 系统资源（CPU、内存、磁盘、网络）
- 复制状态
- 锁等待
- 表和索引统计

**查询示例**:
```promql
# 缓存命中率
rate(pg_stat_database_blks_hit[5m]) /
(rate(pg_stat_database_blks_hit[5m]) + rate(pg_stat_database_blks_read[5m]))

# TPS
rate(pg_stat_database_xact_commit[1m]) +
rate(pg_stat_database_xact_rollback[1m])

# 活跃连接
pg_stat_activity_count{state="active"}
```

---

### 5. postgresql-alerts.yml

**告警规则**:
- 🔴 **Critical**: PostgreSQL宕机、复制延迟、连接数超限
- 🟠 **Warning**: 缓存命中率低、表膨胀、长事务
- 🟡 **Info**: 性能趋势、资源使用

**告警级别**:
```
Critical → 立即处理（5分钟内）
Warning  → 尽快处理（30分钟内）
Info     → 关注即可
```

---

## 🔧 配置调优

### 根据硬件调整

```sql
-- 32GB内存服务器
shared_buffers = 8GB
work_mem = 32MB
effective_cache_size = 24GB

-- 128GB内存服务器
shared_buffers = 32GB
work_mem = 128MB
effective_cache_size = 96GB

-- HDD存储（非SSD）
random_page_cost = 4.0
effective_io_concurrency = 2
```

### 根据工作负载调整

```sql
-- OLTP（高并发，短查询）
work_mem = 16MB - 64MB
max_connections = 200
random_page_cost = 1.1

-- OLAP（分析，长查询）
work_mem = 256MB - 1GB
max_connections = 50
max_parallel_workers_per_gather = 8
```

---

## 📊 性能验证

### 1. 检查配置生效

```sql
-- 查看关键配置
SHOW shared_buffers;
SHOW work_mem;
SHOW io_direct;
SHOW enable_skip_scan;

-- 查看所有配置
SHOW ALL;
```

### 2. 性能基准测试

```bash
# pgbench基准测试
pgbench -i -s 100 testdb
pgbench -c 10 -j 2 -t 10000 testdb

# 监控性能
psql -c "SELECT * FROM pg_stat_database WHERE datname = 'mydb';"
```

### 3. 查看监控指标

```bash
# Prometheus
curl http://localhost:9090/api/v1/query?query=pg_up

# Grafana
open http://localhost:3000
```

---

## 🔐 安全检查清单

```text
□ 修改所有默认密码
□ 启用SSL连接
□ 配置防火墙规则
□ 限制超级用户访问
□ 定期审查pg_hba.conf
□ 启用连接日志
□ 配置备份加密
□ 定期更新PostgreSQL版本
```

---

## 📖 相关文档

- [PostgreSQL 18新特性](../docs/01-PostgreSQL18/40-PostgreSQL18新特性总结.md)
- [性能调优指南](../docs/01-PostgreSQL18/08-性能调优实战指南.md)
- [生产环境检查清单](../docs/05-Production/20-生产环境检查清单.md)
- [快速参考手册](../QUICK-REFERENCE.md)

---

## ⚠️ 重要提示

1. **生产环境部署前**:
   - 在测试环境充分验证
   - 备份现有配置
   - 准备回滚方案
   - 安排维护窗口

2. **密码安全**:
   - 立即修改所有默认密码
   - 使用强密码（16+字符）
   - 定期轮换密码
   - 使用密钥管理服务

3. **性能调优**:
   - 根据实际硬件调整参数
   - 监控关键指标
   - 定期VACUUM和ANALYZE
   - 关注慢查询日志

4. **监控告警**:
   - 配置告警接收渠道
   - 定期测试告警规则
   - 建立响应流程
   - 记录处理经验

---

**维护**: 这些配置文件会持续更新，请定期检查最新版本。

**反馈**: 如有问题或建议，欢迎提Issue。
