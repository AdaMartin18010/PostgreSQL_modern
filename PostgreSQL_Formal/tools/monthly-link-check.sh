#!/bin/bash
#
# PostgreSQL_Formal 月度链接检查脚本
# 
# 功能:
# 1. 扫描所有 .md 文件
# 2. 检查内部链接有效性（包括文件链接和锚点链接）
# 3. 生成详细报告
# 4. 输出失效链接清单
#
# 用法:
#   ./monthly-link-check.sh [选项]
#
# 选项:
#   -o, --output-dir DIR    指定报告输出目录 (默认: ../reports)
#   -q, --quiet             静默模式，只输出错误信息
#   -h, --help              显示帮助信息
#
# 示例:
#   ./monthly-link-check.sh
#   ./monthly-link-check.sh -o ./custom-reports
#   ./monthly-link-check.sh --quiet
#

set -euo pipefail

# 版本信息
VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 默认配置
OUTPUT_DIR="$PROJECT_DIR/reports"
QUIET_MODE=false
CURRENT_DATE=$(date +"%Y-%m")
REPORT_FILE=""
SUMMARY_FILE=""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 统计数据
declare -i TOTAL_FILES=0
declare -i TOTAL_LINKS=0
declare -i VALID_LINKS=0
declare -i BROKEN_LINKS=0
declare -i WARNING_LINKS=0
declare -i EXTERNAL_LINKS=0

# 数组存储结果
declare -a BROKEN_LINKS_LIST=()
declare -a WARNING_LINKS_LIST=()

# ============================================
# 工具函数
# ============================================

log_info() {
    if [[ "$QUIET_MODE" == false ]]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

log_success() {
    if [[ "$QUIET_MODE" == false ]]; then
        echo -e "${GREEN}[SUCCESS]${NC} $1"
    fi
}

log_warning() {
    if [[ "$QUIET_MODE" == false ]]; then
        echo -e "${YELLOW}[WARNING]${NC} $1"
    fi
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

show_help() {
    cat << 'EOF'
PostgreSQL_Formal 月度链接检查脚本

功能:
  1. 扫描所有 .md 文件
  2. 检查内部链接有效性（包括文件链接和锚点链接）
  3. 生成详细报告
  4. 输出失效链接清单

用法:
  ./monthly-link-check.sh [选项]

选项:
  -o, --output-dir DIR    指定报告输出目录 (默认: ../reports)
  -q, --quiet             静默模式，只输出错误信息
  -h, --help              显示帮助信息
  -v, --version           显示版本信息

示例:
  ./monthly-link-check.sh                    # 运行链接检查并生成报告
  ./monthly-link-check.sh -o ./reports       # 指定输出目录
  ./monthly-link-check.sh --quiet            # 静默模式

报告输出:
  报告将保存到: reports/monthly-link-report-YYYY-MM.md
  摘要将保存到: reports/monthly-link-summary-YYYY-MM.txt
EOF
}

show_version() {
    echo "PostgreSQL_Formal Link Checker v$VERSION"
}

# ============================================
# 参数解析
# ============================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -o|--output-dir)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -q|--quiet)
                QUIET_MODE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                show_version
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 确保输出目录存在
    mkdir -p "$OUTPUT_DIR"
    
    # 设置报告文件路径
    REPORT_FILE="$OUTPUT_DIR/monthly-link-report-$CURRENT_DATE.md"
    SUMMARY_FILE="$OUTPUT_DIR/monthly-link-summary-$CURRENT_DATE.txt"
}

# ============================================
# 链接检查核心函数
# ============================================

# 将标题转换为锚点（GitHub 风格）
title_to_anchor() {
    local title="$1"
    # 转换为小写
    title=$(echo "$title" | tr '[:upper:]' '[:lower:]')
    # 移除特殊字符，保留中文、字母、数字、空格和连字符
    title=$(echo "$title" | sed 's/[^[:alnum:][:space:]-]//g')
    # 将空格替换为连字符
    title=$(echo "$title" | sed 's/[[:space:]]/-/g')
    # 移除多个连字符
    title=$(echo "$title" | sed 's/-\+/-/g')
    # 移除首尾连字符
    title=$(echo "$title" | sed 's/^-//;s/-$//')
    echo "$title"
}

# 从 Markdown 文件提取所有锚点
extract_anchors() {
    local file="$1"
    local anchors=()
    
    # 提取标题（# ## ### 等）
    while IFS= read -r line; do
        # 匹配 Markdown 标题
        if [[ "$line" =~ ^#{1,6}[[:space:]]+(.+)$ ]]; then
            local title="${BASH_REMATCH[1]}"
            # 移除标题中的 HTML 标签
            title=$(echo "$title" | sed 's/<[^>]*>//g')
            # 移除标题中的链接
            title=$(echo "$title" | sed 's/\[\([^]]*\)\]([^)]*)*/\1/g')
            # 转换为锚点
            local anchor=$(title_to_anchor "$title")
            if [[ -n "$anchor" ]]; then
                anchors+=("$anchor")
            fi
        fi
    done < "$file"
    
    printf '%s\n' "${anchors[@]}"
}

# 从 Markdown 文件提取所有链接
extract_links() {
    local file="$1"
    local base_dir=$(dirname "$file")
    
    # 使用 grep 提取链接 [text](url)
    grep -oP '\[([^\]]+)\]\(([^)]+)\)' "$file" 2>/dev/null | while read -r match; do
        # 提取链接文本和 URL
        local link_text=$(echo "$match" | sed -E 's/^\[([^\]]+)\]\(.+\)$/\1/')
        local url=$(echo "$match" | sed -E 's/^\[[^\]]+\]\((.+)\)$/\1/')
        
        # 获取行号
        local line_num=$(grep -n "$(echo "$match" | sed 's/[[]/\\[/g; s/[]]/\\]/g')" "$file" | head -1 | cut -d: -f1)
        
        echo "$line_num|$link_text|$url"
    done
}

# 检查链接类型
check_link_type() {
    local url="$1"
    
    if [[ "$url" =~ ^https?:// ]]; then
        echo "external"
    elif [[ "$url" =~ ^# ]]; then
        echo "anchor"
    elif [[ "$url" =~ \.md# ]]; then
        echo "md_anchor"
    elif [[ "$url" =~ \.md$ ]]; then
        echo "md_file"
    elif [[ "$url" =~ ^\.\.?/ ]]; then
        echo "relative_file"
    else
        echo "other"
    fi
}

# 检查锚点是否存在
check_anchor_exists() {
    local file="$1"
    local anchor="$2"
    
    # 提取文件中的所有锚点
    local anchors=$(extract_anchors "$file")
    
    # 检查锚点是否存在
    if echo "$anchors" | grep -qx "$anchor"; then
        return 0
    fi
    
    return 1
}

# 检查文件链接
check_file_link() {
    local source_file="$1"
    local target_path="$2"
    
    local source_dir=$(dirname "$source_file")
    local full_path
    
    # 解析相对路径
    if [[ "$target_path" =~ ^/ ]]; then
        full_path="$PROJECT_DIR$target_path"
    else
        full_path="$source_dir/$target_path"
    fi
    
    # 规范化路径
    full_path=$(cd "$(dirname "$full_path")" && pwd)/$(basename "$full_path") 2>/dev/null || echo "$full_path"
    
    if [[ -f "$full_path" ]]; then
        return 0
    fi
    
    return 1
}

# 检查单个链接
check_link() {
    local source_file="$1"
    local line_num="$2"
    local link_text="$3"
    local url="$4"
    
    local link_type=$(check_link_type "$url")
    local status="valid"
    local message=""
    
    case "$link_type" in
        external)
            # 外部链接不做实时检查，仅统计
            EXTERNAL_LINKS=$((EXTERNAL_LINKS + 1))
            status="external"
            message="外部链接（未验证）"
            ;;
            
        anchor)
            # 页内锚点
            local anchor="${url:1}"  # 移除开头的 #
            if ! check_anchor_exists "$source_file" "$anchor"; then
                status="broken"
                message="锚点不存在: $anchor"
                BROKEN_LINKS=$((BROKEN_LINKS + 1))
            else
                VALID_LINKS=$((VALID_LINKS + 1))
            fi
            ;;
            
        md_anchor)
            # Markdown 文件 + 锚点
            local target_file="${url%%#*}"
            local anchor="${url#*#}"
            
            if ! check_file_link "$source_file" "$target_file"; then
                status="broken"
                message="文件不存在: $target_file"
                BROKEN_LINKS=$((BROKEN_LINKS + 1))
            else
                # 获取目标文件的完整路径
                local source_dir=$(dirname "$source_file")
                local full_path="$source_dir/$target_file"
                full_path=$(cd "$(dirname "$full_path")" 2>/dev/null && pwd)/$(basename "$full_path") || full_path="$source_dir/$target_file"
                
                if [[ -f "$full_path" ]]; then
                    if ! check_anchor_exists "$full_path" "$anchor"; then
                        status="broken"
                        message="锚点不存在: $anchor"
                        BROKEN_LINKS=$((BROKEN_LINKS + 1))
                    else
                        VALID_LINKS=$((VALID_LINKS + 1))
                    fi
                else
                    status="warning"
                    message="无法验证锚点（路径解析问题）"
                    WARNING_LINKS=$((WARNING_LINKS + 1))
                fi
            fi
            ;;
            
        md_file)
            # Markdown 文件
            if ! check_file_link "$source_file" "$url"; then
                status="broken"
                message="文件不存在: $url"
                BROKEN_LINKS=$((BROKEN_LINKS + 1))
            else
                VALID_LINKS=$((VALID_LINKS + 1))
            fi
            ;;
            
        relative_file)
            # 其他相对路径文件
            if ! check_file_link "$source_file" "$url"; then
                status="broken"
                message="文件不存在: $url"
                BROKEN_LINKS=$((BROKEN_LINKS + 1))
            else
                VALID_LINKS=$((VALID_LINKS + 1))
            fi
            ;;
            
        *)
            status="warning"
            message="未知链接类型"
            WARNING_LINKS=$((WARNING_LINKS + 1))
            ;;
    esac
    
    echo "$status|$message"
}

# ============================================
# 主检查流程
# ============================================

run_link_check() {
    log_info "开始链接检查..."
    log_info "项目目录: $PROJECT_DIR"
    log_info "输出目录: $OUTPUT_DIR"
    log_info "报告文件: $REPORT_FILE"
    echo ""
    
    # 查找所有 Markdown 文件（排除备份目录和 node_modules）
    local md_files=$(find "$PROJECT_DIR" -type f -name "*.md" ! -path "*/node_modules/*" ! -path "*/.link_fix_backup/*" ! -path "*/.link_fix_backup_2026/*" ! -path "*/.authority_source_backup/*" | sort)
    
    TOTAL_FILES=$(echo "$md_files" | wc -l)
    log_info "找到 $TOTAL_FILES 个 Markdown 文件"
    echo ""
    
    # 处理计数
    local processed=0
    
    # 临时存储结果
    local temp_results=$(mktemp)
    
    # 遍历所有文件
    while IFS= read -r file; do
        processed=$((processed + 1))
        local rel_path="${file#$PROJECT_DIR/}"
        
        if [[ "$QUIET_MODE" == false ]]; then
            printf "\r${BLUE}[进度]${NC} 检查文件: %d/%d - %s" "$processed" "$TOTAL_FILES" "$rel_path"
        fi
        
        # 提取并检查链接
        while IFS='|' read -r line_num link_text url; do
            TOTAL_LINKS=$((TOTAL_LINKS + 1))
            
            local result=$(check_link "$file" "$line_num" "$link_text" "$url")
            local status=$(echo "$result" | cut -d'|' -f1)
            local message=$(echo "$result" | cut -d'|' -f2-)
            
            # 记录失效链接
            if [[ "$status" == "broken" ]]; then
                BROKEN_LINKS_LIST+=("$rel_path|$line_num|$url|$link_text|$message")
                echo "BROKEN|$rel_path|$line_num|$url|$link_text|$message" >> "$temp_results"
            elif [[ "$status" == "warning" ]]; then
                WARNING_LINKS_LIST+=("$rel_path|$line_num|$url|$link_text|$message")
                echo "WARNING|$rel_path|$line_num|$url|$link_text|$message" >> "$temp_results"
            fi
            
        done < <(extract_links "$file")
        
    done <<< "$md_files"
    
    if [[ "$QUIET_MODE" == false ]]; then
        echo ""  # 换行
        echo ""
    fi
    
    # 生成报告
    generate_report "$temp_results"
    
    # 清理临时文件
    rm -f "$temp_results"
    
    log_success "链接检查完成！"
}

# ============================================
# 报告生成
# ============================================

generate_report() {
    local temp_results="$1"
    local report_date=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Markdown 报告
    cat > "$REPORT_FILE" << EOF
# PostgreSQL_Formal 月度链接检查报告

生成时间: $report_date  
报告周期: $CURRENT_DATE  
脚本版本: $VERSION

## 📊 统计信息

| 指标 | 数值 |
|------|------|
| 总文档数 | $TOTAL_FILES |
| 总链接数 | $TOTAL_LINKS |
| 有效链接 | $VALID_LINKS |
| **失效链接** | **$BROKEN_LINKS** |
| **警告链接** | **$WARNING_LINKS** |
| 外部链接 | $EXTERNAL_LINKS |

### 健康度评分

EOF

    # 计算健康度
    local internal_links=$((TOTAL_LINKS - EXTERNAL_LINKS))
    if [[ $internal_links -gt 0 ]]; then
        local health_score=$((VALID_LINKS * 100 / internal_links))
        
        local health_status=""
        local health_emoji=""
        if [[ $health_score -ge 95 ]]; then
            health_status="优秀"
            health_emoji="🟢"
        elif [[ $health_score -ge 90 ]]; then
            health_status="良好"
            health_emoji="🟡"
        elif [[ $health_score -ge 80 ]]; then
            health_status="一般"
            health_emoji="🟠"
        else
            health_status="需要修复"
            health_emoji="🔴"
        fi
        
        cat >> "$REPORT_FILE" << EOF
| 评分 | $health_score% $health_emoji |
| 状态 | $health_status |

> 💡 健康度 = 有效链接 / 内部链接 × 100%

EOF
    fi

    # 失效链接详情
    cat >> "$REPORT_FILE" << EOF

## 🔴 失效链接详情

| 源文件 | 行号 | 失效链接 | 链接文本 | 错误信息 |
|--------|------|----------|----------|----------|
EOF

    if [[ -f "$temp_results" ]]; then
        grep "^BROKEN|" "$temp_results" | while IFS='|' read -r _ file line url text msg; do
            echo "|$file|$line|\`$url\`|$text|$msg|" >> "$REPORT_FILE"
        done
    fi

    if [[ ${#BROKEN_LINKS_LIST[@]} -eq 0 ]]; then
        echo "
✅ **未发现失效链接！**" >> "$REPORT_FILE"
    fi

    # 警告链接详情
    cat >> "$REPORT_FILE" << EOF

## ⚠️ 警告链接详情

| 源文件 | 行号 | 链接 | 链接文本 | 警告信息 |
|--------|------|------|----------|----------|
EOF

    if [[ -f "$temp_results" ]]; then
        grep "^WARNING|" "$temp_results" | while IFS='|' read -r _ file line url text msg; do
            echo "|$file|$line|\`$url\`|$text|$msg|" >> "$REPORT_FILE"
        done
    fi

    if [[ ${#WARNING_LINKS_LIST[@]} -eq 0 ]]; then
        echo "
✅ **未发现警告链接！**" >> "$REPORT_FILE"
    fi

    # 需要修复的文件列表
    cat >> "$REPORT_FILE" << EOF

## 📋 需要修复的文件列表

| 文件 | 失效链接数 | 警告链接数 | 状态 |
|------|------------|------------|------|
EOF

    if [[ -f "$temp_results" ]]; then
        # 统计每个文件的问题数量
        grep "^BROKEN|" "$temp_results" | cut -d'|' -f2 | sort | uniq -c | sort -rn | while read -r count file; do
            local warn_count=$(grep "^WARNING|$file|" "$temp_results" 2>/dev/null | wc -l)
            echo "|$file|$count|$warn_count|[ ] 待修复|" >> "$REPORT_FILE"
        done
    fi

    if [[ ${#BROKEN_LINKS_LIST[@]} -eq 0 ]]; then
        echo "| - | - | - | ✅ 全部正常 |" >> "$REPORT_FILE"
    fi

    # 修复建议
    cat >> "$REPORT_FILE" << EOF

## 🔧 修复建议

### 常见失效原因

1. **锚点错误**
   - 标题被修改但链接未更新
   - 锚点名称拼写错误
   - 特殊字符处理不当（如数学符号、标点符号）

2. **文件路径错误**
   - 文件被移动或删除
   - 相对路径计算错误
   - 文件名大小写不匹配（Linux 系统敏感）

3. **相对路径问题**
   - 跨目录引用时路径层级错误
   - 使用绝对路径而非相对路径

### 修复步骤

1. 查看上面的**失效链接详情**表格
2. 对于每个失效链接，打开源文件定位到对应行
3. 根据实际情况修复:
   - 如果是锚点错误，更新为正确的标题锚点
   - 如果是路径错误，修正相对路径
   - 如果目标文件已删除，移除链接或指向新位置
4. 修复后重新运行本检查脚本确认

## 📈 历史趋势

| 月份 | 总链接 | 失效链接 | 健康度 | 报告 |
|------|--------|----------|--------|------|
| $CURRENT_DATE | $TOTAL_LINKS | $BROKEN_LINKS | ${health_score:-N/A}% | 当前 |

> 💡 历史数据需要手动维护，建议每月检查后将关键指标添加到此表格

## 📝 检查配置

- **扫描范围**: PostgreSQL_Formal 目录下的所有 .md 文件
- **排除目录**: node_modules, .link_fix_backup*, .authority_source_backup
- **检查内容**: 内部文件链接、锚点链接、相对路径链接
- **外部链接**: 仅统计，不做实时验证

---

*本报告由 monthly-link-check.sh 自动生成*
EOF

    # 生成简要摘要（纯文本）
    cat > "$SUMMARY_FILE" << EOF
PostgreSQL_Formal 月度链接检查摘要
=====================================

生成时间: $report_date
报告周期: $CURRENT_DATE

统计信息
--------
总文档数:     $TOTAL_FILES
总链接数:     $TOTAL_LINKS
有效链接:     $VALID_LINKS
失效链接:     $BROKEN_LINKS
警告链接:     $WARNING_LINKS
外部链接:     $EXTERNAL_LINKS

健康度评分
----------
评分: ${health_score:-N/A}%
状态: $health_status $health_emoji

失效链接清单
------------
EOF

    if [[ ${#BROKEN_LINKS_LIST[@]} -gt 0 ]]; then
        printf '%s\n' "${BROKEN_LINKS_LIST[@]}" >> "$SUMMARY_FILE"
    else
        echo "✅ 未发现失效链接！" >> "$SUMMARY_FILE"
    fi

    cat >> "$SUMMARY_FILE" << EOF

详细报告: $REPORT_FILE
EOF

    # 输出到控制台
    if [[ "$QUIET_MODE" == false ]]; then
        echo "=================================="
        echo "链接检查摘要"
        echo "=================================="
        echo "总文档数:     $TOTAL_FILES"
        echo "总链接数:     $TOTAL_LINKS"
        echo "有效链接:     $VALID_LINKS"
        echo "失效链接:     $BROKEN_LINKS"
        echo "警告链接:     $WARNING_LINKS"
        echo ""
        echo "健康度评分:   ${health_score:-N/A}% $health_emoji"
        echo "状态:         $health_status"
        echo ""
        echo "报告文件:     $REPORT_FILE"
        echo "摘要文件:     $SUMMARY_FILE"
    fi
}

# ============================================
# 主函数
# ============================================

main() {
    parse_args "$@"
    run_link_check
}

# 运行主函数
main "$@"
