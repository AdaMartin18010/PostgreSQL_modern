#!/bin/bash

# PostgreSQL + pgvector 一键部署脚本
# 支持 Docker Compose 和本地安装

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
POSTGRES_VERSION=${POSTGRES_VERSION:-16}
PGVECTOR_VERSION=${PGVECTOR_VERSION:-0.7.0}
DB_NAME=${DB_NAME:-vector_db}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_PORT=${DB_PORT:-5432}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PostgreSQL + pgvector 一键部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker 未安装${NC}"
        echo "请先安装 Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}错误: Docker Compose 未安装${NC}"
        echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Docker 环境检查通过${NC}"
}

# 创建 Docker Compose 配置
create_docker_compose() {
    echo -e "${YELLOW}创建 Docker Compose 配置...${NC}"
    
    cat > docker-compose.yml <<EOF
version: '3.8'

services:
  postgres-pgvector:
    image: pgvector/pgvector:pg${POSTGRES_VERSION}
    container_name: postgres-pgvector
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
    ports:
      - "${DB_PORT}:5432"
    volumes:
      - pgvector_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    command:
      - "postgres"
      - "-c"
      - "shared_preload_libraries=vector"
      - "-c"
      - "max_connections=200"
      - "-c"
      - "shared_buffers=256MB"
      - "-c"
      - "effective_cache_size=1GB"
      - "-c"
      - "maintenance_work_mem=128MB"
      - "-c"
      - "checkpoint_completion_target=0.9"
      - "-c"
      - "wal_buffers=16MB"
      - "-c"
      - "default_statistics_target=100"
      - "-c"
      - "random_page_cost=1.1"
      - "-c"
      - "effective_io_concurrency=200"
      - "-c"
      - "work_mem=4MB"
      - "-c"
      - "min_wal_size=1GB"
      - "-c"
      - "max_wal_size=4GB"

volumes:
  pgvector_data:
EOF

    echo -e "${GREEN}✓ Docker Compose 配置已创建${NC}"
}

# 启动服务
start_services() {
    echo -e "${YELLOW}启动 PostgreSQL + pgvector 服务...${NC}"
    
    docker-compose up -d
    
    echo -e "${YELLOW}等待服务启动...${NC}"
    sleep 5
    
    # 检查服务状态
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T postgres-pgvector pg_isready -U ${DB_USER} -d ${DB_NAME} > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 服务启动成功${NC}"
            break
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}错误: 服务启动超时${NC}"
        exit 1
    fi
}

# 初始化数据库
init_database() {
    echo -e "${YELLOW}初始化数据库...${NC}"
    
    # 启用 pgvector 扩展
    docker-compose exec -T postgres-pgvector psql -U ${DB_USER} -d ${DB_NAME} <<EOF
-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证扩展
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 创建示例表
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

-- 创建 HNSW 索引
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 显示表结构
\d documents
EOF

    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
}

# 显示连接信息
show_connection_info() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}部署完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "连接信息:"
    echo "  主机: localhost"
    echo "  端口: ${DB_PORT}"
    echo "  数据库: ${DB_NAME}"
    echo "  用户: ${DB_USER}"
    echo "  密码: ${DB_PASSWORD}"
    echo ""
    echo "连接命令:"
    echo "  psql -h localhost -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME}"
    echo ""
    echo "Docker Compose 命令:"
    echo "  启动: docker-compose up -d"
    echo "  停止: docker-compose down"
    echo "  查看日志: docker-compose logs -f"
    echo "  进入容器: docker-compose exec postgres-pgvector psql -U ${DB_USER} -d ${DB_NAME}"
    echo ""
}

# 主函数
main() {
    check_docker
    create_docker_compose
    start_services
    init_database
    show_connection_info
}

# 执行主函数
main
