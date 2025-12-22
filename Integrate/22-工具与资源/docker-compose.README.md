---

> **📋 文档来源**: `PostgreSQL\bench\docker-compose.README.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# Docker Compose 测试环境

> **最后更新**: 2025-11-12

---

## 📋 概述

使用 Docker Compose 快速搭建 PostgreSQL 基准测试环境。

---

## 🚀 快速开始

### 1. 启动 PostgreSQL

```bash
# 启动 PostgreSQL 18（默认）
docker-compose up -d postgres

# 等待数据库就绪
docker-compose exec postgres pg_isready -U postgres
```

### 2. 初始化测试数据

```bash
# 连接到数据库
docker-compose exec postgres psql -U postgres -d pgbench_test

# 或从主机连接
psql -h localhost -U postgres -d pgbench_test
```

### 3. 运行基准测试

```bash
# 初始化 pgbench 数据
docker-compose exec postgres pgbench -i -s 10 -U postgres -d pgbench_test

# 运行测试
docker-compose exec postgres pgbench -c 32 -j 32 -T 300 -U postgres -d pgbench_test
```

---

## 🔧 配置说明

### 服务配置

- **postgres**: PostgreSQL 18 + pgvector
  - 端口: 5432
  - 数据库: pgbench_test
  - 用户: postgres
  - 密码: postgres

- **postgres17**: PostgreSQL 17 + pgvector（可选，用于版本对比）
  - 端口: 5433
  - 需要启用 `compare` profile

### PostgreSQL 配置

默认配置已优化用于基准测试：

```yaml
shared_buffers: 256MB
work_mem: 4MB
maintenance_work_mem: 64MB
effective_cache_size: 1GB
max_connections: 200
random_page_cost: 1.1
effective_io_concurrency: 200
```

---

## 📊 版本对比测试

### 启动两个版本

```bash
# 启动 PostgreSQL 18
docker-compose up -d postgres

# 启动 PostgreSQL 17（用于对比）
docker-compose --profile compare up -d postgres17
```

### 运行对比测试

```bash
# 在 PostgreSQL 18 上运行
docker-compose exec postgres pgbench -i -s 10 -U postgres -d pgbench_test
docker-compose exec postgres pgbench -c 32 -j 32 -T 300 -U postgres -d pgbench_test > result_pg18.log

# 在 PostgreSQL 17 上运行
docker-compose exec postgres17 pgbench -i -s 10 -U postgres -d pgbench_test
docker-compose exec postgres17 pgbench -c 32 -j 32 -T 300 -U postgres -d pgbench_test > result_pg17.log

# 对比结果
cd tools
./compare_results.sh ../result_pg18.log ../result_pg17.log "PostgreSQL 18" "PostgreSQL 17"
```

---

## 🛠️ 常用命令

### 启动和停止

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 查看日志
docker-compose logs -f postgres
```

### 数据库操作

```bash
# 连接到数据库
docker-compose exec postgres psql -U postgres -d pgbench_test

# 执行 SQL 文件
docker-compose exec -T postgres psql -U postgres -d pgbench_test < script.sql

# 备份数据库
docker-compose exec postgres pg_dump -U postgres pgbench_test > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U postgres -d pgbench_test < backup.sql
```

---

## 📚 相关资源

- **基准测试指南**: [README.md](./README.md)
- **Docker Compose 文档**: <https://docs.docker.com/compose/>

---

## 💡 注意事项

1. **数据持久化**: 数据存储在 Docker volume 中，删除容器不会丢失数据
2. **端口冲突**: 确保 5432 和 5433 端口未被占用
3. **资源限制**: 根据系统资源调整 PostgreSQL 配置参数
4. **网络访问**: 容器内的 PostgreSQL 可以通过 localhost 访问
