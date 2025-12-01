#!/bin/bash
# 基准测试套件自动化脚本
# 使用方法: ./run_benchmark_suite.sh <database_name> [options]

set -e

# 默认配置
DB_NAME=${1:-pgbench_test}
SCALE_FACTOR=${SCALE_FACTOR:-100}
DURATION=${DURATION:-300}
CLIENTS=${CLIENTS:-32}
THREADS=${THREADS:-32}
OUTPUT_DIR=${OUTPUT_DIR:-./results}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 创建输出目录
mkdir -p "${OUTPUT_DIR}/${TIMESTAMP}"

echo -e "${GREEN}=== 基准测试套件 ===${NC}"
echo "数据库: ${DB_NAME}"
echo "Scale Factor: ${SCALE_FACTOR}"
echo "持续时间: ${DURATION} 秒"
echo "并发数: ${CLIENTS}"
echo "输出目录: ${OUTPUT_DIR}/${TIMESTAMP}"
echo ""

# 检查数据库是否存在
if ! psql -lqt | cut -d \| -f 1 | grep -qw "${DB_NAME}"; then
    echo -e "${YELLOW}数据库 ${DB_NAME} 不存在，正在创建...${NC}"
    createdb "${DB_NAME}"
fi

# 检查数据是否已初始化
if ! psql -d "${DB_NAME}" -c "\d pgbench_accounts" &>/dev/null; then
    echo -e "${YELLOW}初始化测试数据...${NC}"
    pgbench -i -s "${SCALE_FACTOR}" "${DB_NAME}"
else
    echo -e "${GREEN}测试数据已存在${NC}"
fi

# 启动系统监控
echo -e "${GREEN}启动系统监控...${NC}"
cd "$(dirname "$0")"
./monitor_system.sh "${DURATION}" "${OUTPUT_DIR}/${TIMESTAMP}/system" &
MONITOR_PID=$!
cd - > /dev/null

# 等待监控启动
sleep 2

# 测试 1: 基线测试
echo -e "${GREEN}运行基线测试...${NC}"
pgbench -c "${CLIENTS}" -j "${THREADS}" -T "${DURATION}" -r -l \
    "${DB_NAME}" > "${OUTPUT_DIR}/${TIMESTAMP}/baseline.log" 2>&1

# 移动延迟日志
if ls pgbench_log.* 1> /dev/null 2>&1; then
    mv pgbench_log.* "${OUTPUT_DIR}/${TIMESTAMP}/"
fi

# 测试 2: 只读测试
echo -e "${GREEN}运行只读测试...${NC}"
pgbench -S -c "${CLIENTS}" -j "${THREADS}" -T "${DURATION}" -r -l \
    "${DB_NAME}" > "${OUTPUT_DIR}/${TIMESTAMP}/readonly.log" 2>&1

# 测试 3: 只写测试
echo -e "${GREEN}运行只写测试...${NC}"
pgbench -N -c "${CLIENTS}" -j "${THREADS}" -T "${DURATION}" -r -l \
    "${DB_NAME}" > "${OUTPUT_DIR}/${TIMESTAMP}/writeonly.log" 2>&1

# 等待监控完成
wait ${MONITOR_PID} 2>/dev/null || true

# 分析结果
echo -e "${GREEN}分析测试结果...${NC}"
cd "$(dirname "$0")"

# 提取指标
for logfile in "${OUTPUT_DIR}/${TIMESTAMP}"/*.log; do
    if [ -f "$logfile" ]; then
        basename=$(basename "$logfile" .log)
        ./extract_pgbench_metrics.sh "$logfile" > "${OUTPUT_DIR}/${TIMESTAMP}/${basename}_metrics.txt" 2>&1
    fi
done

# 分析延迟日志
if ls "${OUTPUT_DIR}/${TIMESTAMP}"/pgbench_log.* 1> /dev/null 2>&1; then
    ./analyze_pgbench_log.sh "${OUTPUT_DIR}/${TIMESTAMP}"/pgbench_log.* > \
        "${OUTPUT_DIR}/${TIMESTAMP}/latency_analysis.txt" 2>&1
fi

cd - > /dev/null

# 生成摘要报告
echo -e "${GREEN}生成摘要报告...${NC}"
cat > "${OUTPUT_DIR}/${TIMESTAMP}/summary.txt" << EOF
=== 基准测试摘要 ===
测试时间: $(date)
数据库: ${DB_NAME}
Scale Factor: ${SCALE_FACTOR}
测试持续时间: ${DURATION} 秒
并发数: ${CLIENTS}
工作线程数: ${THREADS}

测试结果文件:
- baseline.log: 基线测试
- readonly.log: 只读测试
- writeonly.log: 只写测试
- latency_analysis.txt: 延迟分析
- system_*.log: 系统监控数据

EOF

echo -e "${GREEN}=== 测试完成 ===${NC}"
echo "结果保存在: ${OUTPUT_DIR}/${TIMESTAMP}/"
echo "查看摘要: cat ${OUTPUT_DIR}/${TIMESTAMP}/summary.txt"
