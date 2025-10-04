#!/bin/bash

# PostgreSQL_modern 版本检查工具
# 功能：自动检查PostgreSQL和主要扩展的最新版本
# 使用：./tools/check_versions.sh

set -e

echo "================================================"
echo "PostgreSQL_modern 版本检查工具"
echo "检查日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查依赖
check_dependencies() {
    local missing=0
    for cmd in curl jq git; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}[错误] 缺少依赖: $cmd${NC}"
            missing=1
        fi
    done
    if [ $missing -eq 1 ]; then
        echo ""
        echo "请安装缺失的依赖："
        echo "  Ubuntu/Debian: sudo apt-get install curl jq git"
        echo "  macOS:         brew install curl jq git"
        echo "  Windows:       使用 Git Bash 或 WSL"
        exit 1
    fi
}

# 获取GitHub最新Release版本
get_github_latest_release() {
    local repo=$1
    local version=$(curl -s "https://api.github.com/repos/$repo/releases/latest" | jq -r '.tag_name // "unknown"')
    echo "$version"
}

# 检查PostgreSQL版本
check_postgresql() {
    echo -e "${YELLOW}[1/5] 检查 PostgreSQL 核心版本...${NC}"
    local current="17.0"
    
    # 从官网获取最新版本（简化版，实际需要解析HTML）
    echo "  当前追踪版本: $current"
    echo "  检查地址: https://www.postgresql.org/download/"
    echo "  ${GREEN}✓${NC} 手动检查建议: 访问官网确认最新版本"
    echo ""
}

# 检查pgvector
check_pgvector() {
    echo -e "${YELLOW}[2/5] 检查 pgvector（向量检索）...${NC}"
    local current="v0.8.0"
    local latest=$(get_github_latest_release "pgvector/pgvector")
    
    echo "  当前追踪版本: $current"
    echo "  最新版本:     $latest"
    
    if [ "$current" != "$latest" ] && [ "$latest" != "unknown" ]; then
        echo -e "  ${RED}⚠ 发现新版本！${NC}"
        echo "  更新地址: https://github.com/pgvector/pgvector/releases"
    else
        echo -e "  ${GREEN}✓ 版本最新${NC}"
    fi
    echo ""
}

# 检查TimescaleDB
check_timescaledb() {
    echo -e "${YELLOW}[3/5] 检查 TimescaleDB（时序数据）...${NC}"
    local current="2.17.2"
    local latest=$(get_github_latest_release "timescale/timescaledb")
    
    echo "  当前追踪版本: $current"
    echo "  最新版本:     $latest"
    
    if [ "$current" != "$latest" ] && [ "$latest" != "unknown" ]; then
        echo -e "  ${RED}⚠ 发现新版本！${NC}"
        echo "  更新地址: https://github.com/timescale/timescaledb/releases"
    else
        echo -e "  ${GREEN}✓ 版本最新${NC}"
    fi
    echo ""
}

# 检查PostGIS
check_postgis() {
    echo -e "${YELLOW}[4/5] 检查 PostGIS（地理空间）...${NC}"
    local current="3.5.0"
    local latest=$(get_github_latest_release "postgis/postgis")
    
    echo "  当前追踪版本: $current"
    echo "  最新版本:     $latest"
    
    if [ "$current" != "$latest" ] && [ "$latest" != "unknown" ]; then
        echo -e "  ${RED}⚠ 发现新版本！${NC}"
        echo "  更新地址: https://github.com/postgis/postgis/releases"
    else
        echo -e "  ${GREEN}✓ 版本最新${NC}"
    fi
    echo ""
}

# 检查Citus
check_citus() {
    echo -e "${YELLOW}[5/5] 检查 Citus（分布式）...${NC}"
    local current="v12.1.4"
    local latest=$(get_github_latest_release "citusdata/citus")
    
    echo "  当前追踪版本: $current"
    echo "  最新版本:     $latest"
    
    if [ "$current" != "$latest" ] && [ "$latest" != "unknown" ]; then
        echo -e "  ${RED}⚠ 发现新版本！${NC}"
        echo "  更新地址: https://github.com/citusdata/citus/releases"
    else
        echo -e "  ${GREEN}✓ 版本最新${NC}"
    fi
    echo ""
}

# 生成报告
generate_report() {
    echo "================================================"
    echo "检查完成！"
    echo "================================================"
    echo ""
    echo "📋 后续行动："
    echo "  1. 如有版本更新，请创建Issue："
    echo "     标题: [VERSION] 月度版本检查 $(date '+%Y-%m')"
    echo "     模板: .github/ISSUE_TEMPLATE/version_update.md"
    echo ""
    echo "  2. 更新相关文档："
    echo "     - 00_overview/README.md"
    echo "     - 04_modern_features/version_diff_16_to_17.md"
    echo "     - 各扩展的README文件"
    echo "     - CHANGELOG.md"
    echo ""
    echo "  3. 验证兼容性（如有测试环境）"
    echo ""
}

# 主函数
main() {
    check_dependencies
    check_postgresql
    check_pgvector
    check_timescaledb
    check_postgis
    check_citus
    generate_report
}

main

