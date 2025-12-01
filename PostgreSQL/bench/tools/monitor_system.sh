#!/bin/bash
# 系统资源监控脚本
# 使用方法: ./monitor_system.sh <duration_seconds> <output_prefix>

DURATION=${1:-300}
PREFIX=${2:-monitor}

echo "开始监控系统资源，持续时间: ${DURATION} 秒"
echo "输出文件前缀: ${PREFIX}"
echo ""

# 检查工具是否可用
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "警告: $1 未安装，跳过相关监控"
        return 1
    fi
    return 0
}

# CPU 和内存监控
if check_tool sar; then
    echo "启动 CPU 和内存监控..."
    sar -u 1 ${DURATION} > ${PREFIX}_cpu.log 2>&1 &
    CPU_PID=$!
    sar -r 1 ${DURATION} > ${PREFIX}_memory.log 2>&1 &
    MEM_PID=$!
fi

# IO 监控
if check_tool iostat; then
    echo "启动 IO 监控..."
    iostat -x 1 ${DURATION} > ${PREFIX}_io.log 2>&1 &
    IO_PID=$!
fi

# 网络监控
if check_tool sar; then
    echo "启动网络监控..."
    sar -n DEV 1 ${DURATION} > ${PREFIX}_network.log 2>&1 &
    NET_PID=$!
fi

# PostgreSQL 进程监控
if check_tool top && pgrep -f postgres > /dev/null; then
    echo "启动 PostgreSQL 进程监控..."
    PG_PID=$(pgrep -f postgres | head -1)
    top -p ${PG_PID} -b -d 1 -n ${DURATION} > ${PREFIX}_postgres.log 2>&1 &
    TOP_PID=$!
fi

echo ""
echo "监控已启动，PID:"
[ ! -z "$CPU_PID" ] && echo "  CPU: $CPU_PID"
[ ! -z "$MEM_PID" ] && echo "  内存: $MEM_PID"
[ ! -z "$IO_PID" ] && echo "  IO: $IO_PID"
[ ! -z "$NET_PID" ] && echo "  网络: $NET_PID"
[ ! -z "$TOP_PID" ] && echo "  PostgreSQL: $TOP_PID"
echo ""
echo "等待 ${DURATION} 秒..."

# 等待监控完成
sleep ${DURATION}

echo ""
echo "监控完成，日志文件:"
echo "  ${PREFIX}_cpu.log"
echo "  ${PREFIX}_memory.log"
echo "  ${PREFIX}_io.log"
echo "  ${PREFIX}_network.log"
[ ! -z "$TOP_PID" ] && echo "  ${PREFIX}_postgres.log"
