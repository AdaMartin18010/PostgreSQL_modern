#!/bin/bash

# 并发控制决策助手 - 一键启动脚本
# 使用方法: ./start.sh [dev|prod]

set -e

MODE=${1:-dev}

echo "🚀 启动并发控制决策助手 (模式: $MODE)"

# 检查依赖
echo "📋 检查依赖..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p data/decision-trees
mkdir -p data/templates
mkdir -p data/benchmarks
mkdir -p logs

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    cat > .env << EOF
# 后端配置
RUST_LOG=info
DATABASE_URL=postgresql://postgres:postgres@db:5432/decision_assistant
REDIS_URL=redis://redis:6379

# 前端配置
VITE_API_URL=http://localhost:8080/api/v1
EOF
fi

# 启动服务
if [ "$MODE" == "dev" ]; then
    echo "🔧 开发模式启动..."
    docker-compose up --build
elif [ "$MODE" == "prod" ]; then
    echo "🏭 生产模式启动..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
else
    echo "❌ 未知模式: $MODE (支持: dev, prod)"
    exit 1
fi

echo "✅ 启动完成！"
echo ""
echo "📱 访问地址:"
echo "   - 前端: http://localhost:5173"
echo "   - 后端API: http://localhost:8080/api/v1"
echo "   - API文档: http://localhost:8080/docs"
echo ""
echo "📊 查看日志:"
echo "   docker-compose logs -f"
