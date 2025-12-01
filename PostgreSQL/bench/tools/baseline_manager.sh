#!/bin/bash
# 性能基线管理脚本
# 用于保存、对比和管理性能基线

set -e

BASELINE_DIR="${BASELINE_DIR:-./baselines}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 创建基线目录
mkdir -p "$BASELINE_DIR"

usage() {
    cat << EOF
使用方法: $0 <command> [options]

命令:
  save <name> <result_file>    保存测试结果为基线
  list                         列出所有基线
  show <name>                  显示指定基线的详细信息
  compare <name1> <name2>      对比两个基线
  compare-latest <name>        对比最新结果与指定基线
  delete <name>                删除指定基线

示例:
  $0 save baseline_v1 result.log
  $0 list
  $0 compare baseline_v1 baseline_v2
  $0 compare-latest baseline_v1
EOF
    exit 1
}

save_baseline() {
    local name=$1
    local result_file=$2
    
    if [ -z "$name" ] || [ -z "$result_file" ]; then
        echo "错误: 需要提供基线名称和结果文件"
        usage
    fi
    
    if [ ! -f "$result_file" ]; then
        echo "错误: 结果文件不存在: $result_file"
        exit 1
    fi
    
    local baseline_dir="$BASELINE_DIR/$name"
    mkdir -p "$baseline_dir"
    
    # 提取指标
    echo "提取指标..."
    "$SCRIPT_DIR/extract_pgbench_metrics.sh" "$result_file" > "$baseline_dir/metrics.txt"
    
    # 复制原始结果
    cp "$result_file" "$baseline_dir/result.log"
    
    # 保存元数据
    cat > "$baseline_dir/metadata.json" << EOF
{
  "name": "$name",
  "created_at": "$(date -Iseconds)",
  "result_file": "$result_file",
  "postgresql_version": "$(psql --version 2>/dev/null || echo 'unknown')",
  "system_info": "$(uname -a)"
}
EOF
    
    # 如果有延迟日志，也保存
    if ls pgbench_log.* 1> /dev/null 2>&1; then
        echo "保存延迟日志..."
        cp pgbench_log.* "$baseline_dir/" 2>/dev/null || true
        if [ -f "$baseline_dir/pgbench_log.0" ]; then
            "$SCRIPT_DIR/analyze_pgbench_log.sh" "$baseline_dir"/pgbench_log.* > "$baseline_dir/latency_analysis.txt" 2>&1 || true
        fi
    fi
    
    echo "基线已保存: $name"
    echo "位置: $baseline_dir"
}

list_baselines() {
    if [ ! -d "$BASELINE_DIR" ] || [ -z "$(ls -A "$BASELINE_DIR" 2>/dev/null)" ]; then
        echo "没有保存的基线"
        return
    fi
    
    echo "已保存的基线:"
    echo ""
    printf "%-30s %-20s %-50s\n" "名称" "创建时间" "位置"
    echo "----------------------------------------------------------------------------------------"
    
    for baseline in "$BASELINE_DIR"/*; do
        if [ -d "$baseline" ]; then
            local name=$(basename "$baseline")
            local metadata="$baseline/metadata.json"
            if [ -f "$metadata" ]; then
                local created=$(grep -o '"created_at": "[^"]*"' "$metadata" | cut -d'"' -f4 | cut -d'T' -f1)
                printf "%-30s %-20s %-50s\n" "$name" "$created" "$baseline"
            else
                printf "%-30s %-20s %-50s\n" "$name" "unknown" "$baseline"
            fi
        fi
    done
}

show_baseline() {
    local name=$1
    
    if [ -z "$name" ]; then
        echo "错误: 需要提供基线名称"
        usage
    fi
    
    local baseline_dir="$BASELINE_DIR/$name"
    if [ ! -d "$baseline_dir" ]; then
        echo "错误: 基线不存在: $name"
        exit 1
    fi
    
    echo "=== 基线信息: $name ==="
    echo ""
    
    if [ -f "$baseline_dir/metadata.json" ]; then
        echo "元数据:"
        cat "$baseline_dir/metadata.json" | python3 -m json.tool 2>/dev/null || cat "$baseline_dir/metadata.json"
        echo ""
    fi
    
    if [ -f "$baseline_dir/metrics.txt" ]; then
        echo "性能指标:"
        cat "$baseline_dir/metrics.txt"
        echo ""
    fi
    
    if [ -f "$baseline_dir/latency_analysis.txt" ]; then
        echo "延迟分析:"
        cat "$baseline_dir/latency_analysis.txt"
    fi
}

compare_baselines() {
    local name1=$1
    local name2=$2
    
    if [ -z "$name1" ] || [ -z "$name2" ]; then
        echo "错误: 需要提供两个基线名称"
        usage
    fi
    
    local baseline1="$BASELINE_DIR/$name1/result.log"
    local baseline2="$BASELINE_DIR/$name2/result.log"
    
    if [ ! -f "$baseline1" ]; then
        echo "错误: 基线不存在: $name1"
        exit 1
    fi
    
    if [ ! -f "$baseline2" ]; then
        echo "错误: 基线不存在: $name2"
        exit 1
    fi
    
    echo "对比基线: $name1 vs $name2"
    echo ""
    "$SCRIPT_DIR/compare_results.sh" "$baseline1" "$baseline2" "$name1" "$name2"
}

compare_latest() {
    local name=$1
    
    if [ -z "$name" ]; then
        echo "错误: 需要提供基线名称"
        usage
    fi
    
    local baseline="$BASELINE_DIR/$name/result.log"
    if [ ! -f "$baseline" ]; then
        echo "错误: 基线不存在: $name"
        exit 1
    fi
    
    # 查找最新的结果文件
    local latest=$(ls -t result*.log 2>/dev/null | head -1)
    if [ -z "$latest" ]; then
        echo "错误: 找不到最新的结果文件"
        exit 1
    fi
    
    echo "对比最新结果 ($latest) 与基线 ($name)"
    echo ""
    "$SCRIPT_DIR/compare_results.sh" "$latest" "$baseline" "Latest" "$name"
}

delete_baseline() {
    local name=$1
    
    if [ -z "$name" ]; then
        echo "错误: 需要提供基线名称"
        usage
    fi
    
    local baseline_dir="$BASELINE_DIR/$name"
    if [ ! -d "$baseline_dir" ]; then
        echo "错误: 基线不存在: $name"
        exit 1
    fi
    
    read -p "确认删除基线 '$name'? (y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        rm -rf "$baseline_dir"
        echo "基线已删除: $name"
    else
        echo "取消删除"
    fi
}

# 主逻辑
case "${1:-}" in
    save)
        save_baseline "$2" "$3"
        ;;
    list)
        list_baselines
        ;;
    show)
        show_baseline "$2"
        ;;
    compare)
        compare_baselines "$2" "$3"
        ;;
    compare-latest)
        compare_latest "$2"
        ;;
    delete)
        delete_baseline "$2"
        ;;
    *)
        usage
        ;;
esac
