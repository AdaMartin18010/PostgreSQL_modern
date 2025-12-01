#!/bin/bash
# 分析 pgbench 日志文件，提取延迟分位数
# 使用方法: ./analyze_pgbench_log.sh pgbench_log.*

if [ $# -eq 0 ]; then
    echo "用法: $0 <pgbench_log_file>..."
    echo "示例: $0 pgbench_log.*"
    exit 1
fi

echo "=== pgbench 日志分析 ==="
echo ""

for logfile in "$@"; do
    if [ ! -f "$logfile" ]; then
        echo "警告: 文件不存在: $logfile"
        continue
    fi
    
    echo "文件: $logfile"
    echo "----------------------------------------"
    
    # 提取延迟值（最后一列）
    delays=$(awk '{print $NF}' "$logfile" | grep -E '^[0-9]+(\.[0-9]+)?$' | sort -n)
    
    if [ -z "$delays" ]; then
        echo "未找到有效的延迟数据"
        echo ""
        continue
    fi
    
    total=$(echo "$delays" | wc -l)
    
    # 计算分位数
    tp50=$(echo "$delays" | awk -v n=$total 'NR == int(n*0.5) {print}')
    tp95=$(echo "$delays" | awk -v n=$total 'NR == int(n*0.95) {print}')
    tp99=$(echo "$delays" | awk -v n=$total 'NR == int(n*0.99) {print}')
    tp999=$(echo "$delays" | awk -v n=$total 'NR == int(n*0.999) {print}')
    
    # 计算平均值
    avg=$(echo "$delays" | awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print 0}')
    
    # 计算最小值最大值
    min=$(echo "$delays" | head -1)
    max=$(echo "$delays" | tail -1)
    
    echo "总事务数: $total"
    echo "平均延迟: ${avg} ms"
    echo "最小延迟: ${min} ms"
    echo "最大延迟: ${max} ms"
    echo "TP50: ${tp50} ms"
    echo "TP95: ${tp95} ms"
    echo "TP99: ${tp99} ms"
    echo "TP99.9: ${tp999} ms"
    echo ""
done

echo "=== 分析完成 ==="
