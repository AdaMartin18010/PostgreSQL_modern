#!/bin/bash
# 从 pgbench 输出中提取关键指标
# 使用方法: ./extract_pgbench_metrics.sh <pgbench_output_file>

if [ $# -eq 0 ]; then
    echo "用法: $0 <pgbench_output_file>"
    echo "示例: $0 result.log"
    exit 1
fi

INPUT_FILE=$1

if [ ! -f "$INPUT_FILE" ]; then
    echo "错误: 文件不存在: $INPUT_FILE"
    exit 1
fi

echo "=== pgbench 指标提取 ==="
echo "文件: $INPUT_FILE"
echo "----------------------------------------"

# 提取 TPS
tps=$(grep -E "tps = [0-9]+\.[0-9]+" "$INPUT_FILE" | grep -v "including connections" | awk '{print $3}')

# 提取平均延迟
latency_avg=$(grep "latency average" "$INPUT_FILE" | awk '{print $3}')

# 提取延迟标准差
latency_stddev=$(grep "latency stddev" "$INPUT_FILE" | awk '{print $3}')

# 提取事务数
transactions=$(grep "transactions actually processed" "$INPUT_FILE" | awk '{print $1}')

# 提取连接时间
conn_time=$(grep "initial connection time" "$INPUT_FILE" | awk '{print $4}')

echo "TPS: $tps"
echo "平均延迟: $latency_avg ms"
echo "延迟标准差: $latency_stddev ms"
echo "事务数: $transactions"
echo "连接时间: $conn_time ms"
echo ""

# 生成 CSV 格式输出
echo "=== CSV 格式 ==="
echo "TPS,平均延迟(ms),延迟标准差(ms),事务数,连接时间(ms)"
echo "$tps,$latency_avg,$latency_stddev,$transactions,$conn_time"
