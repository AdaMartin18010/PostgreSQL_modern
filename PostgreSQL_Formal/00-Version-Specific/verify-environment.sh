#!/bin/bash
# ==========================================
# PostgreSQL 多版本实验环境 - 验证脚本
# 用于检查容器状态、验证连接、测试基本功能
# ==========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
COMPOSE_FILE="docker-compose.yml"
TIMEOUT=30

# ==========================================
# 辅助函数
# ==========================================

print_header() {
    echo -e "\n${BLUE}==========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}==========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ==========================================
# 检查 Docker 环境
# ==========================================

check_docker() {
    print_header "检查 Docker 环境"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        exit 1
    fi
    print_success "Docker 已安装: $(docker --version)"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi
    print_success "Docker Compose 已安装: $(docker-compose --version)"
    
    if ! docker info &> /dev/null; then
        print_error "Docker 守护进程未运行"
        exit 1
    fi
    print_success "Docker 守护进程运行中"
}

# ==========================================
# 检查容器状态
# ==========================================

check_containers() {
    print_header "检查容器状态"
    
    local services=("pg16" "pg17" "pgadmin")
    local all_running=true
    
    for service in "${services[@]}"; do
        if docker ps --format "{{.Names}}" | grep -q "^${service}$"; then
            local status=$(docker inspect --format='{{.State.Status}}' "$service" 2>/dev/null)
            local health=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "N/A")
            
            if [ "$status" = "running" ]; then
                if [ "$health" = "healthy" ] || [ "$health" = "N/A" ]; then
                    print_success "$service 运行中 (状态: $status, 健康: $health)"
                else
                    print_warning "$service 运行中但健康检查未通过 (健康: $health)"
                    all_running=false
                fi
            else
                print_error "$service 状态异常: $status"
                all_running=false
            fi
        else
            print_error "$service 未运行"
            all_running=false
        fi
    done
    
    # 检查 PG18 (可选)
    if docker ps --format "{{.Names}}" | grep -q "^pg18$"; then
        print_success "pg18 运行中 (可选服务)"
    else
        print_info "pg18 未运行 (可选服务，使用 --profile pg18 启动)"
    fi
    
    if [ "$all_running" = false ]; then
        print_error "部分服务未正常运行"
        return 1
    fi
    
    return 0
}

# ==========================================
# 验证数据库连接
# ==========================================

check_database_connection() {
    print_header "验证数据库连接"
    
    local -A ports=(
        ["pg16"]=5433
        ["pg17"]=5432
    )
    
    # 可选添加 PG18
    if docker ps --format "{{.Names}}" | grep -q "^pg18$"; then
        ports["pg18"]=5434
    fi
    
    local all_connected=true
    
    for service in "${!ports[@]}"; do
        local port=${ports[$service]}
        
        if docker exec "$service" pg_isready -U dca -d dca_demo &> /dev/null; then
            print_success "$service 连接成功 (端口: $port)"
            
            # 获取版本信息
            local version=$(docker exec "$service" psql -U dca -d dca_demo -t -c "SELECT version();" 2>/dev/null | head -1 | xargs)
            print_info "  版本: $version"
        else
            print_error "$service 连接失败 (端口: $port)"
            all_connected=false
        fi
    done
    
    if [ "$all_connected" = false ]; then
        return 1
    fi
    
    return 0
}

# ==========================================
# 验证示例数据
# ==========================================

check_sample_data() {
    print_header "验证示例数据"
    
    local service="pg17"
    
    # 检查表是否存在
    local tables=$(docker exec "$service" psql -U dca -d dca_demo -t -c "
        SELECT schemaname || '.' || tablename 
        FROM pg_tables 
        WHERE schemaname = 'demo' 
        ORDER BY tablename;
    " 2>/dev/null | xargs)
    
    if [ -n "$tables" ]; then
        print_success "找到 demo schema 下的表:"
        echo "$tables" | while read -r table; do
            local count=$(docker exec "$service" psql -U dca -d dca_demo -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | xargs)
            print_info "  $table: $count 行"
        done
    else
        print_warning "未找到示例表，可能是首次启动正在初始化"
    fi
}

# ==========================================
# 验证扩展
# ==========================================

check_extensions() {
    print_header "验证扩展"
    
    local service="pg17"
    local expected_extensions=("pg_stat_statements" "pgcrypto" "uuid-ossp")
    
    for ext in "${expected_extensions[@]}"; do
        local result=$(docker exec "$service" psql -U dca -d dca_demo -t -c "
            SELECT 1 FROM pg_extension WHERE extname = '$ext';
        " 2>/dev/null | xargs)
        
        if [ "$result" = "1" ]; then
            local version=$(docker exec "$service" psql -U dca -d dca_demo -t -c "
                SELECT extversion FROM pg_extension WHERE extname = '$ext';
            " 2>/dev/null | xargs)
            print_success "$ext 已安装 (版本: $version)"
        else
            print_error "$ext 未安装"
        fi
    done
}

# ==========================================
# 基本功能测试
# ==========================================

run_basic_tests() {
    print_header "基本功能测试"
    
    local service="pg17"
    
    # 测试写入
    print_info "测试写入操作..."
    local insert_result=$(docker exec "$service" psql -U dca -d dca_demo -t -c "
        INSERT INTO demo.users (username, email, password_hash, full_name) 
        VALUES ('test_user_$$', 'test$$@example.com', 'test_hash', 'Test User') 
        RETURNING id;
    " 2>/dev/null | xargs)
    
    if [ -n "$insert_result" ]; then
        print_success "写入测试通过 (ID: $insert_result)"
        
        # 清理测试数据
        docker exec "$service" psql -U dca -d dca_demo -c "
            DELETE FROM demo.users WHERE id = $insert_result;
        " &> /dev/null
        print_success "清理测试数据完成"
    else
        print_error "写入测试失败"
    fi
    
    # 测试 JOIN 查询
    print_info "测试 JOIN 查询..."
    local join_count=$(docker exec "$service" psql -U dca -d dca_demo -t -c "
        SELECT COUNT(*) FROM demo.users u 
        LEFT JOIN demo.orders o ON u.id = o.user_id;
    " 2>/dev/null | xargs)
    
    if [ -n "$join_count" ]; then
        print_success "JOIN 查询测试通过 ($join_count 行)"
    else
        print_error "JOIN 查询测试失败"
    fi
    
    # 测试窗口函数
    print_info "测试窗口函数..."
    local window_result=$(docker exec "$service" psql -U dca -d dca_demo -t -c "
        SELECT COUNT(*) FROM (
            SELECT RANK() OVER (ORDER BY total_spent DESC) 
            FROM demo.user_order_summary
        ) t;
    " 2>/dev/null | xargs)
    
    if [ -n "$window_result" ]; then
        print_success "窗口函数测试通过"
    else
        print_error "窗口函数测试失败"
    fi
}

# ==========================================
# 检查 pgAdmin
# ==========================================

check_pgadmin() {
    print_header "检查 pgAdmin"
    
    if curl -s http://localhost:8080/misc/ping &> /dev/null; then
        print_success "pgAdmin 可访问: http://localhost:8080"
        print_info "  邮箱: admin@dca.local"
        print_info "  密码: admin"
    else
        print_warning "pgAdmin 响应缓慢或未就绪"
    fi
}

# ==========================================
# 生成报告
# ==========================================

generate_report() {
    print_header "验证报告"
    
    echo -e "${BLUE}容器状态:${NC}"
    docker ps --filter "name=pg" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${BLUE}连接信息:${NC}"
    echo "  PostgreSQL 16: localhost:5433"
    echo "  PostgreSQL 17: localhost:5432"
    echo "  PostgreSQL 18: localhost:5434 (如已启动)"
    echo "  pgAdmin:       http://localhost:8080"
    
    echo -e "\n${BLUE}快速连接命令:${NC}"
    echo "  PG16: docker exec -it pg16 psql -U dca -d dca_demo"
    echo "  PG17: docker exec -it pg17 psql -U dca -d dca_demo"
    echo "  PG18: docker exec -it pg18 psql -U dca -d dca_demo"
}

# ==========================================
# 主函数
# ==========================================

main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║     PostgreSQL 多版本实验环境 - 验证脚本               ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$script_dir"
    
    # 检查是否在正确的目录
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "未找到 $COMPOSE_FILE 文件"
        print_info "请确保在 PostgreSQL_Formal/00-Version-Specific 目录下运行此脚本"
        exit 1
    fi
    
    # 执行检查
    check_docker
    check_containers
    check_database_connection
    check_sample_data
    check_extensions
    run_basic_tests
    check_pgadmin
    generate_report
    
    print_header "验证完成"
    print_success "环境验证通过！可以开始使用了。"
    
    echo -e "\n${BLUE}下一步:${NC}"
    echo "  1. 使用 pgAdmin 访问 http://localhost:8080"
    echo "  2. 或使用命令行: docker exec -it pg17 psql -U dca -d dca_demo"
    echo "  3. 查看使用指南: cat DOCKER_GUIDE.md"
}

# 处理命令行参数
case "${1:-}" in
    --containers|-c)
        check_docker
        check_containers
        ;;
    --connection|-n)
        check_database_connection
        ;;
    --data|-d)
        check_sample_data
        ;;
    --extensions|-e)
        check_extensions
        ;;
    --help|-h)
        echo "PostgreSQL 多版本实验环境 - 验证脚本"
        echo ""
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --containers, -c    仅检查容器状态"
        echo "  --connection, -n    仅检查数据库连接"
        echo "  --data, -d          仅检查示例数据"
        echo "  --extensions, -e    仅检查扩展"
        echo "  --help, -h          显示帮助"
        echo ""
        echo "默认执行所有检查"
        ;;
    *)
        main
        ;;
esac
