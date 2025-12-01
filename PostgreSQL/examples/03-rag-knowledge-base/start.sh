#!/bin/bash

# RAG知识库端到端案例启动脚本
# 最后更新: 2025-01-15

set -e

echo "=========================================="
echo "  RAG知识库端到端案例 - 启动脚本"
echo "=========================================="
echo ""

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装Docker，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未安装Docker Compose，请先安装Docker Compose"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  警告: 未找到.env文件，使用默认配置"
    echo "   创建.env文件..."
    cat > .env << EOF
# PostgreSQL配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rag_kb

# Redis配置
REDIS_URL=redis://redis:6379/0

# OpenAI API Key (可选，用于生成embedding)
OPENAI_API_KEY=

# 安全密钥
SECRET_KEY=$(openssl rand -hex 32)

# 环境
ENVIRONMENT=development
EOF
    echo "✅ .env文件已创建"
fi

# 选择启动模式
echo "请选择启动模式:"
echo "  1) 基础模式 (仅PostgreSQL + Redis)"
echo "  2) 完整模式 (包含后端、前端、监控等所有服务)"
read -p "请输入选项 (1/2，默认1): " mode
mode=${mode:-1}

if [ "$mode" == "1" ]; then
    echo ""
    echo "🚀 启动基础模式..."
    docker-compose -f docker-compose.yml up -d
    
    echo ""
    echo "✅ 基础服务已启动"
    echo ""
    echo "📊 服务信息:"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo ""
    echo "🔧 连接到数据库:"
    echo "  docker-compose exec postgres psql -U postgres -d rag_kb"
    echo ""
    echo "🛑 停止服务:"
    echo "  docker-compose down"
    
elif [ "$mode" == "2" ]; then
    echo ""
    echo "🚀 启动完整模式..."
    
    # 检查必要的目录和文件
    if [ ! -d "backend" ]; then
        echo "⚠️  警告: backend目录不存在，将创建基础结构"
        mkdir -p backend/app
    fi
    
    if [ ! -d "frontend" ]; then
        echo "⚠️  警告: frontend目录不存在，将创建基础结构"
        mkdir -p frontend/src
    fi
    
    docker-compose -f docker-compose.full.yml up -d --build
    
    echo ""
    echo "✅ 完整服务已启动"
    echo ""
    echo "📊 服务信息:"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Nginx: http://localhost:80"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3001 (admin/admin)"
    echo ""
    echo "📚 API文档:"
    echo "  http://localhost:8000/docs"
    echo ""
    echo "🛑 停止服务:"
    echo "  docker-compose -f docker-compose.full.yml down"
else
    echo "❌ 无效选项"
    exit 1
fi

echo ""
echo "=========================================="
echo "  启动完成！"
echo "=========================================="
