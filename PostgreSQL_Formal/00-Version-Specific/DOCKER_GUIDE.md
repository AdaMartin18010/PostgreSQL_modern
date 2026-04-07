# PostgreSQL 多版本实验环境 - Docker 使用指南

本指南介绍如何使用 Docker 快速搭建 PostgreSQL 多版本实验环境，支持 PG16/PG17/PG18 三个版本，便于对比测试和验证文档中的 SQL 示例。

---

## 📋 目录

- [快速启动](#-快速启动)
- [连接信息](#-连接信息)
- [服务架构](#-服务架构)
- [常用命令](#-常用命令)
- [如何执行文档示例](#-如何执行文档示例)
- [pgAdmin 使用](#-pgadmin-使用)
- [常见问题](#-常见问题)

---

## 🚀 快速启动

### 前提条件

- Docker Engine 20.10+
- Docker Compose 2.0+

### 启动命令

```bash
# 进入目录
cd PostgreSQL_Formal/00-Version-Specific

# 启动 PG16 和 PG17（推荐）
docker-compose up -d

# 启动所有版本（包括 PG18）
docker-compose --profile pg18 up -d
```

### 验证启动

```bash
# 查看容器状态
docker-compose ps

# 运行验证脚本
./verify-environment.sh
```

### 停止环境

```bash
# 停止容器（保留数据）
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

---

## 🔌 连接信息

### 数据库连接

| 版本 | 主机 | 端口 | 数据库 | 用户名 | 密码 |
|------|------|------|--------|--------|------|
| PostgreSQL 16 | localhost | 5433 | dca_demo | dca | dca_demo |
| PostgreSQL 17 | localhost | 5432 | dca_demo | dca | dca_demo |
| PostgreSQL 18 | localhost | 5434 | dca_demo | dca | dca_demo |

### pgAdmin Web 界面

- **URL**: <http://localhost:8080>
- **邮箱**: <admin@dca.local>
- **密码**: admin

---

## 🏗️ 服务架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                          │
│                    172.20.0.0/16                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │  PostgreSQL  │  │  PostgreSQL  │      │
│  │     16       │  │     17       │  │     18       │      │
│  │   :5432      │  │   :5432      │  │   :5432      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │              │
│    主机:5433          主机:5432          主机:5434         │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │              pgAdmin 4 (Web UI)                     │   │
│  │                 :80 → 主机:8080                     │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 常用命令

### 容器管理

```bash
# 查看日志
docker-compose logs -f postgres17
docker-compose logs -f pgadmin

# 进入容器内部
docker exec -it pg17 psql -U dca -d dca_demo
docker exec -it pg16 psql -U dca -d dca_demo

# 重启单个服务
docker-compose restart postgres17

# 查看资源使用
docker stats
```

### psql 连接

```bash
# 本地连接 PG17
docker exec -it pg17 psql -U dca -d dca_demo

# 从主机使用 psql 连接（需安装 PostgreSQL 客户端）
psql -h localhost -p 5432 -U dca -d dca_demo

# 使用密码连接
PGPASSWORD=dca_demo psql -h localhost -p 5432 -U dca -d dca_demo
```

### 数据备份与恢复

```bash
# 备份数据库
docker exec pg17 pg_dump -U dca dca_demo > backup.sql

# 恢复数据库
cat backup.sql | docker exec -i pg17 psql -U dca -d dca_demo
```

---

## 📖 如何执行文档示例

### 1. 连接到示例数据库

```bash
# 连接到 PG17 示例数据库
docker exec -it pg17 psql -U dca -d dca_demo
```

### 2. 查看示例数据

```sql
-- 查看有哪些表
\dt demo.*

-- 查看用户数据
SELECT * FROM demo.users;

-- 查看订单汇总
SELECT * FROM demo.user_order_summary;
```

### 3. 测试 JOIN 查询

```sql
-- 用户与订单 JOIN
SELECT
    u.username,
    u.full_name,
    o.order_number,
    o.total_amount,
    o.status
FROM demo.users u
JOIN demo.orders o ON u.id = o.user_id
WHERE o.status = 'delivered'
LIMIT 10;
```

### 4. 测试 JSON 操作

```sql
-- 查询事件日志
SELECT
    event_type,
    event_data->>'user_id' AS user_id,
    event_data->>'ip' AS ip_address
FROM demo.event_logs
WHERE event_type = 'user_login';
```

### 5. 测试窗口函数

```sql
-- 用户消费排名
SELECT
    username,
    total_orders,
    total_spent,
    RANK() OVER (ORDER BY total_spent DESC) AS spending_rank
FROM demo.user_order_summary
WHERE total_orders > 0;
```

### 6. 对比不同版本的特性

```bash
# 在 PG16 中执行
docker exec -it pg16 psql -U dca -d dca_demo -c "SELECT version();"

# 在 PG17 中执行
docker exec -it pg17 psql -U dca -d dca_demo -c "SELECT version();"

# 在 PG18 中执行
docker exec -it pg18 psql -U dca -d dca_demo -c "SELECT version();"
```

---

## 🖥️ pgAdmin 使用

### 首次配置

1. 打开浏览器访问 <http://localhost:8080>
2. 使用邮箱 `admin@dca.local` 和密码 `admin` 登录
3. 服务器配置已自动导入，可在左侧导航栏看到

### 手动添加服务器

1. 右键点击 "Servers" → "Register" → "Server"
2. **General** 标签：填写名称（如 "PostgreSQL 17"）
3. **Connection** 标签：
   - Host: `postgres17` (容器内) 或 `localhost` (主机)
   - Port: `5432`
   - Database: `dca_demo`
   - Username: `dca`
   - Password: `dca_demo`

---

## ❓ 常见问题

### Q1: 容器启动失败

**现象**: `docker-compose up` 后容器立即退出

**解决**:

```bash
# 查看详细日志
docker-compose logs postgres17

# 常见原因：端口被占用
# 检查端口占用
lsof -i :5432  # macOS/Linux
netstat -ano | findstr :5432  # Windows

# 修改 docker-compose.yml 中的端口映射
```

### Q2: PG18 镜像不存在

**现象**: `Error response from daemon: manifest for postgres:18-alpine not found`

**解决**:
PG18 尚未正式发布，docker-compose.yml 中已将其设置为可选 profile：

```bash
# 不启动 PG18（默认）
docker-compose up -d

# 如需测试最新开发版，可临时修改镜像
docker-compose -f docker-compose.dev.yml up -d
```

### Q3: 数据丢失

**现象**: 重启后数据消失

**解决**:

```bash
# 确保使用命名卷（已默认配置）
docker-compose down    # 保留数据
docker-compose down -v # 删除数据（慎用）

# 查看卷
docker volume ls | grep pg
```

### Q4: 无法连接到数据库

**现象**: `psql: connection refused`

**解决**:

```bash
# 检查容器状态
docker-compose ps

# 等待健康检查通过
docker-compose logs -f postgres17

# 检查网络
docker network ls
docker network inspect pg-network
```

### Q5: 中文显示乱码

**解决**:

```sql
-- 在 psql 中设置客户端编码
\encoding UTF8

-- 或连接时指定
psql -h localhost -p 5432 -U dca -d dca_demo -E UTF8
```

### Q6: 扩展未安装

**解决**:

```sql
-- 查看已安装扩展
SELECT * FROM pg_extension;

-- 手动安装扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## 🔧 高级配置

### 自定义配置文件

编辑 `config/postgresql17.conf`，然后重启：

```bash
docker-compose restart postgres17
```

### 添加初始化脚本

将 `.sql` 文件放入 `init-scripts/` 目录，重启容器时自动执行：

```bash
# 注意：仅在新创建的容器中执行，已有数据不会重复执行
docker-compose down -v
docker-compose up -d
```

### 性能测试

```bash
# 安装 pgbench
docker exec -it pg17 apk add postgresql17-contrib

# 初始化测试数据
docker exec -it pg17 pgbench -U dca -i -s 10 dca_demo

# 运行测试
docker exec -it pg17 pgbench -U dca -c 10 -j 2 -T 60 dca_demo
```

---

## 📚 相关文档

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [Docker Hub - PostgreSQL](https://hub.docker.com/_/postgres)
- [pgAdmin 文档](https://www.pgadmin.org/docs/)

---

**最后更新**: 2026-04-07
