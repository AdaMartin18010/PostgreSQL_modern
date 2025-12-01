#!/bin/bash
# 性能对比脚本
# 使用方法: ./compare_results.sh result1.log result2.log [label1] [label2]

set -e

if [ $# -lt 2 ]; then
    echo "使用方法: $0 <result1.log> <result2.log> [label1] [label2]"
    echo "示例: $0 baseline_v1.log baseline_v2.log 'Before' 'After'"
    exit 1
fi

RESULT1=$1
RESULT2=$2
LABEL1=${3:-"Test 1"}
LABEL2=${4:-"Test 2"}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 提取指标
echo "提取 $LABEL1 的指标..."
METRICS1=$(mktemp)
"$SCRIPT_DIR/extract_pgbench_metrics.sh" "$RESULT1" > "$METRICS1"

echo "提取 $LABEL2 的指标..."
METRICS2=$(mktemp)
"$SCRIPT_DIR/extract_pgbench_metrics.sh" "$RESULT2" > "$METRICS2"

# 解析指标
get_metric() {
    local file=$1
    local metric=$2
    grep "^$metric:" "$file" | awk '{print $2}' | sed 's/[^0-9.]//g'
}

TPS1=$(get_metric "$METRICS1" "TPS")
TPS2=$(get_metric "$METRICS2" "TPS")
LATENCY1=$(get_metric "$METRICS1" "平均延迟")
LATENCY2=$(get_metric "$METRICS2" "平均延迟")

# 计算差异
if [ -n "$TPS1" ] && [ -n "$TPS2" ] && [ "$TPS2" != "0" ]; then
    TPS_DIFF=$(echo "scale=2; (($TPS1 - $TPS2) / $TPS2) * 100" | bc)
else
    TPS_DIFF="N/A"
fi

if [ -n "$LATENCY1" ] && [ -n "$LATENCY2" ] && [ "$LATENCY2" != "0" ]; then
    LATENCY_DIFF=$(echo "scale=2; (($LATENCY1 - $LATENCY2) / $LATENCY2) * 100" | bc)
else
    LATENCY_DIFF="N/A"
fi

# 输出对比结果
echo ""
echo "=========================================="
echo "性能对比报告"
echo "=========================================="
echo ""
printf "%-20s %15s %15s %15s\n" "指标" "$LABEL1" "$LABEL2" "差异"
echo "------------------------------------------"

if [ "$TPS_DIFF" != "N/A" ]; then
    if (( $(echo "$TPS_DIFF > 0" | bc -l) )); then
        TPS_SIGN="+"
        TPS_COLOR="\033[0;32m"  # 绿色
    else
        TPS_SIGN=""
        TPS_COLOR="\033[0;31m"  # 红色
    fi
    NC='\033[0m'  # No Color
    printf "%-20s %15s %15s ${TPS_COLOR}%15s%%${NC}\n" "TPS" "$TPS1" "$TPS2" "${TPS_SIGN}${TPS_DIFF}"
else
    printf "%-20s %15s %15s %15s\n" "TPS" "$TPS1" "$TPS2" "N/A"
fi

if [ "$LATENCY_DIFF" != "N/A" ]; then
    if (( $(echo "$LATENCY_DIFF < 0" | bc -l) )); then
        LATENCY_SIGN=""
        LATENCY_COLOR="\033[0;32m"  # 绿色
    else
        LATENCY_SIGN="+"
        LATENCY_COLOR="\033[0;31m"  # 红色
    fi
    NC='\033[0m'  # No Color
    printf "%-20s %15s %15s ${LATENCY_COLOR}%15s%%${NC}\n" "平均延迟(ms)" "$LATENCY1" "$LATENCY2" "${LATENCY_SIGN}${LATENCY_DIFF}"
else
    printf "%-20s %15s %15s %15s\n" "平均延迟(ms)" "$LATENCY1" "$LATENCY2" "N/A"
fi

echo "=========================================="
echo ""

# 清理临时文件
rm -f "$METRICS1" "$METRICS2"
