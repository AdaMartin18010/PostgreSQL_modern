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

---

## 5. 高级配置

### 5.1 自定义PostgreSQL配置

**自定义配置示例**：

```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg18
    environment:
      POSTGRES_DB: pgbench_test
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgresql.conf:/etc/postgresql/postgresql.conf  # 自定义配置
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    ports:
      - "5432:5432"
```

### 5.2 多版本对比测试

**多版本对比配置**：

```yaml
services:
  postgres18:
    image: pgvector/pgvector:pg18
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: pgbench_test

  postgres17:
    image: pgvector/pgvector:pg17
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: pgbench_test

  postgres16:
    image: pgvector/pgvector:pg16
    ports:
      - "5434:5432"
    environment:
      POSTGRES_DB: pgbench_test
```

---

## 6. 性能测试脚本

### 6.1 自动化测试脚本

**自动化测试脚本示例**：

```bash
#!/bin/bash
# PostgreSQL性能测试脚本（带错误处理）

set -euo pipefail

# 配置
SCALE_FACTOR=10
CLIENTS=32
JOBS=32
DURATION=300
DB_NAME="pgbench_test"

# 检查PostgreSQL是否就绪
check_postgres_ready() {
    local container=$1
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T "$container" pg_isready -U postgres > /dev/null 2>&1; then
            echo "PostgreSQL $container 已就绪"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    echo "错误: PostgreSQL $container 未就绪"
    return 1
}

# 初始化测试数据
init_pgbench() {
    local container=$1
    echo "初始化 pgbench 数据 (scale=$SCALE_FACTOR)..."
    docker-compose exec -T "$container" pgbench -i -s "$SCALE_FACTOR" -U postgres -d "$DB_NAME"
}

# 运行测试
run_pgbench() {
    local container=$1
    local output_file=$2
    echo "运行 pgbench 测试..."
    docker-compose exec -T "$container" pgbench \
        -c "$CLIENTS" \
        -j "$JOBS" \
        -T "$DURATION" \
        -U postgres \
        -d "$DB_NAME" \
        > "$output_file" 2>&1
}

# 主函数
main() {
    local container=${1:-postgres}
    local output_file=${2:-result.log}

    echo "=== PostgreSQL 性能测试 ==="
    echo "容器: $container"
    echo "输出文件: $output_file"
    echo ""

    # 检查PostgreSQL就绪
    if ! check_postgres_ready "$container"; then
        exit 1
    fi

    # 初始化数据
    init_pgbench "$container"

    # 运行测试
    run_pgbench "$container" "$output_file"

    echo ""
    echo "测试完成！结果保存在: $output_file"
    echo ""
    echo "关键指标:"
    grep -E "tps|latency" "$output_file" || true
}

main "$@"
```

### 6.2 结果分析脚本

**结果分析脚本示例**：

```bash
#!/bin/bash
# PostgreSQL性能测试结果分析脚本

analyze_results() {
    local result_file=$1

    if [ ! -f "$result_file" ]; then
        echo "错误: 结果文件不存在: $result_file"
        return 1
    fi

    echo "=== 性能测试结果分析 ==="
    echo ""

    # 提取TPS
    tps=$(grep -oP 'tps = \K[0-9.]+' "$result_file" | head -1)
    echo "TPS (每秒事务数): $tps"

    # 提取延迟
    latency=$(grep -oP 'latency = \K[0-9.]+' "$result_file" | head -1)
    echo "平均延迟 (ms): $latency"

    # 提取P99延迟
    p99_latency=$(grep -oP '99th percentile = \K[0-9.]+' "$result_file" | head -1)
    if [ -n "$p99_latency" ]; then
        echo "P99延迟 (ms): $p99_latency"
    fi

    echo ""
}

# 对比两个结果
compare_results() {
    local file1=$1
    local file2=$2
    local label1=${3:-"版本1"}
    local label2=${4:-"版本2"}

    echo "=== 性能对比 ==="
    echo ""

    tps1=$(grep -oP 'tps = \K[0-9.]+' "$file1" | head -1)
    tps2=$(grep -oP 'tps = \K[0-9.]+' "$file2" | head -1)

    if [ -n "$tps1" ] && [ -n "$tps2" ]; then
        improvement=$(echo "scale=2; ($tps2 - $tps1) / $tps1 * 100" | bc)
        echo "$label1 TPS: $tps1"
        echo "$label2 TPS: $tps2"
        echo "性能提升: ${improvement}%"
    fi

    echo ""
}

analyze_results "$@"
```

---

## 7. 故障排查

### 7.1 常见问题

**常见问题及解决方案**：

1. **容器无法启动**

   ```bash
   # 检查日志
   docker-compose logs postgres

   # 检查端口占用
   netstat -an | grep 5432

   # 检查数据卷
   docker volume ls
   ```

2. **连接失败**

   ```bash
   # 检查容器状态
   docker-compose ps

   # 检查网络
   docker network ls

   # 测试连接
   docker-compose exec postgres pg_isready -U postgres
   ```

3. **性能问题**

   ```bash
   # 检查资源使用
   docker stats

   # 检查PostgreSQL配置
   docker-compose exec postgres psql -U postgres -c "SHOW ALL;"
   ```

---

## 8. 最佳实践

### ✅ 推荐做法

1. **使用数据卷** - 持久化数据，避免数据丢失
2. **资源限制** - 设置适当的资源限制
3. **配置优化** - 根据测试需求优化PostgreSQL配置
4. **版本管理** - 使用明确的版本标签
5. **环境隔离** - 为不同测试使用不同的容器

### ⚠️ 注意事项

1. **数据持久化**: 数据存储在 Docker volume 中，删除容器不会丢失数据
2. **端口冲突**: 确保 5432 和 5433 端口未被占用
3. **资源限制**: 根据系统资源调整 PostgreSQL 配置参数
4. **网络访问**: 容器内的 PostgreSQL 可以通过 localhost 访问
5. **安全考虑**: 生产环境不要使用默认密码
