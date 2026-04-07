#!/bin/bash

# PostgreSQL 19 新特性跟踪更新脚本
# 用于定期检查和记录 PostgreSQL 19 开发进展

# 配置
TRACKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$TRACKER_DIR/update-history.log"
ROADMAP_FILE="$TRACKER_DIR/ROADMAP.md"
DATE=$(date '+%Y-%m-%d')
DATETIME=$(date '+%Y-%m-%d %H:%M:%S')

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数: 显示帮助信息
show_help() {
    cat << EOF
PostgreSQL 19 新特性跟踪更新脚本

用法: $0 [命令]

命令:
    check       检查更新提醒
    update      记录更新活动
    status      显示当前跟踪状态
    reminder    显示待办事项提醒
    milestones  显示重要里程碑
    help        显示此帮助信息

示例:
    $0 check       # 检查是否需要更新
    $0 update      # 记录一次更新活动
    $0 status      # 查看跟踪状态
EOF
}

# 函数: 初始化日志文件
init_log() {
    if [[ ! -f "$LOG_FILE" ]]; then
        echo "# PostgreSQL 19 跟踪更新日志" > "$LOG_FILE"
        echo "# 创建时间: $DATETIME" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        echo "| 日期 | 操作 | 说明 |" >> "$LOG_FILE"
        echo "|------|------|------|" >> "$LOG_FILE"
    fi
}

# 函数: 记录日志
log_action() {
    local action="$1"
    local description="$2"
    echo "| $DATE | $action | $description |" >> "$LOG_FILE"
}

# 函数: 检查更新提醒
check_updates() {
    echo -e "${BLUE}=== PostgreSQL 19 更新检查 ===${NC}"
    echo ""
    
    # 计算距离重要日期的时间
    local today=$(date +%s)
    
    # Feature Freeze (预计 2026-03-31)
    local feature_freeze=$(date -d "2026-03-31" +%s 2>/dev/null || date -v+0d -j -f "%Y-%m-%d" "2026-03-31" +%s 2>/dev/null)
    local days_to_freeze=$(( (feature_freeze - today) / 86400 ))
    
    # Beta 1 (预计 2026-05-01)
    local beta1=$(date -d "2026-05-01" +%s 2>/dev/null || date -v+0d -j -f "%Y-%m-%d" "2026-05-01" +%s 2>/dev/null)
    local days_to_beta=$(( (beta1 - today) / 86400 ))
    
    # GA Release (预计 2026-09-01)
    local ga=$(date -d "2026-09-01" +%s 2>/dev/null || date -v+0d -j -f "%Y-%m-%d" "2026-09-01" +%s 2>/dev/null)
    local days_to_ga=$(( (ga - today) / 86400 ))
    
    echo -e "${YELLOW}距离重要里程碑:${NC}"
    if [[ $days_to_freeze -gt 0 ]]; then
        echo -e "  Feature Freeze: ${GREEN}${days_to_freeze} 天${NC} (预计 2026-03-31)"
    else
        echo -e "  Feature Freeze: ${RED}已过去${NC}"
    fi
    
    if [[ $days_to_beta -gt 0 ]]; then
        echo -e "  Beta 1: ${GREEN}${days_to_beta} 天${NC} (预计 2026-05-01)"
    else
        echo -e "  Beta 1: ${RED}已过去${NC}"
    fi
    
    if [[ $days_to_ga -gt 0 ]]; then
        echo -e "  GA Release: ${GREEN}${days_to_ga} 天${NC} (预计 2026-09-01)"
    else
        echo -e "  GA Release: ${RED}已过去${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}建议检查:${NC}"
    echo "  1. CommitFest 2026-03 状态: https://commitfest.postgresql.org/57/"
    echo "  2. depesz.com Waiting for PG19 系列"
    echo "  3. Postgres Professional 博客 CommitFest 回顾"
    echo "  4. 邮件列表 pgsql-hackers 热点话题"
    
    # 检查上次更新时间
    if [[ -f "$LOG_FILE" ]]; then
        local last_update=$(tail -1 "$LOG_FILE" | grep -oP '^\| \K[0-9]{4}-[0-9]{2}-[0-9]{2}' || echo "从未")
        if [[ "$last_update" != "从未" && "$last_update" != "日期" ]]; then
            local last_update_ts=$(date -d "$last_update" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$last_update" +%s 2>/dev/null)
            local days_since_last=$(( (today - last_update_ts) / 86400 ))
            echo ""
            echo -e "${YELLOW}上次更新: ${last_update} (${days_since_last} 天前)${NC}"
            
            if [[ $days_since_last -gt 7 ]]; then
                echo -e "${RED}⚠️ 建议尽快更新跟踪信息！${NC}"
            elif [[ $days_since_last -gt 3 ]]; then
                echo -e "${YELLOW}ℹ️ 建议检查更新${NC}"
            else
                echo -e "${GREEN}✓ 跟踪信息较新${NC}"
            fi
        fi
    fi
}

# 函数: 记录更新活动
record_update() {
    echo -e "${BLUE}=== 记录更新活动 ===${NC}"
    echo ""
    
    read -p "更新类型 (check/review/update): " update_type
    read -p "更新说明: " description
    
    init_log
    log_action "$update_type" "$description"
    
    echo ""
    echo -e "${GREEN}✓ 更新已记录${NC}"
    echo "  日期: $DATE"
    echo "  类型: $update_type"
    echo "  说明: $description"
    
    # 提示更新 ROADMAP.md
    echo ""
    echo -e "${YELLOW}提示: 记得更新 ROADMAP.md 中的相关内容！${NC}"
}

# 函数: 显示跟踪状态
show_status() {
    echo -e "${BLUE}=== PostgreSQL 19 跟踪状态 ===${NC}"
    echo ""
    
    echo -e "${YELLOW}文件状态:${NC}"
    if [[ -f "$ROADMAP_FILE" ]]; then
        local roadmap_mtime=$(stat -c "%y" "$ROADMAP_FILE" 2>/dev/null || stat -f "%Sm" "$ROADMAP_FILE" 2>/dev/null)
        echo -e "  ROADMAP.md: ${GREEN}存在${NC} (修改时间: $roadmap_mtime)"
    else
        echo -e "  ROADMAP.md: ${RED}不存在${NC}"
    fi
    
    if [[ -f "$TRACKER_DIR/SOURCES.md" ]]; then
        echo -e "  SOURCES.md: ${GREEN}存在${NC}"
    else
        echo -e "  SOURCES.md: ${RED}不存在${NC}"
    fi
    
    if [[ -f "$LOG_FILE" ]]; then
        local log_lines=$(wc -l < "$LOG_FILE")
        echo -e "  update-history.log: ${GREEN}存在${NC} (${log_lines} 行)"
    else
        echo -e "  update-history.log: ${YELLOW}未创建${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}更新历史 (最近5条):${NC}"
    if [[ -f "$LOG_FILE" ]]; then
        tail -5 "$LOG_FILE" | grep -v "^#" | grep -v "^$" | grep "|"
    else
        echo "  暂无更新记录"
    fi
    
    echo ""
    echo -e "${YELLOW}已确认特性数量:${NC}"
    if [[ -f "$ROADMAP_FILE" ]]; then
        local feature_count=$(grep -c "^|.*已提交" "$ROADMAP_FILE" 2>/dev/null || echo "0")
        echo "  已提交特性: $feature_count 项"
    fi
}

# 函数: 显示待办提醒
show_reminders() {
    echo -e "${BLUE}=== 待办事项提醒 ===${NC}"
    echo ""
    
    cat << EOF
${YELLOW}每周检查:${NC}
  [ ] 查看 depesz.com "Waiting for PostgreSQL 19" 更新
  [ ] 阅读 Postgres Professional CommitFest 回顾
  [ ] 浏览 Postgres Weekly 周报
  [ ] 检查 pgsql-hackers 邮件列表热点

${YELLOW}每月检查:${NC}
  [ ] 更新 CommitFest 状态
  [ ] 整理新特性列表
  [ ] 更新 ROADMAP.md
  [ ] 审查潜在重要特性状态

${YELLOW}里程碑检查:${NC}
  [ ] Feature Freeze 前最终特性确认
  [ ] Beta 1 发布跟踪
  [ ] RC 版本测试
  [ ] GA 版本发布记录

${YELLOW}信息来源:${NC}
  📧 pgsql-hackers@lists.postgresql.org
  🌐 https://commitfest.postgresql.org/
  📝 https://www.depesz.com/
  📊 https://postgrespro.com/blog/
EOF
}

# 函数: 显示里程碑
show_milestones() {
    echo -e "${BLUE}=== PostgreSQL 19 重要里程碑 ===${NC}"
    echo ""
    
    cat << EOF
${GREEN}已完成:${NC}
  ✅ 2025-07: CommitFest 1 (PG19-1)
  ✅ 2025-09: CommitFest 2 (PG19-2)
  ✅ 2025-11: CommitFest 3 (PG19-3)
  ✅ 2026-01: CommitFest 4 (PG19-4)

${YELLOW}进行中/待开始:${NC}
  🔄 2026-03: CommitFest 5 (PG19-5) - 进行中
  ⏳ 2026-03/04: Feature Freeze - 预计
  ⏳ 2026-05: Beta 1 发布 - 预计
  ⏳ 2026-06: Beta 2/3 - 预计
  ⏳ 2026-07: RC 1 - 预计
  ⏳ 2026-09: GA Release - 预计

${BLUE}关键日期说明:${NC}
  • Feature Freeze: 新特性冻结，不再接受新功能
  • Beta 1: 首个测试版本，特性冻结后的版本
  • RC: 候选发布版本
  • GA: 正式版本发布
EOF
}

# 主程序
case "${1:-check}" in
    check)
        check_updates
        ;;
    update)
        record_update
        ;;
    status)
        show_status
        ;;
    reminder|reminders)
        show_reminders
        ;;
    milestone|milestones)
        show_milestones
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}未知命令: $1${NC}"
        show_help
        exit 1
        ;;
esac
