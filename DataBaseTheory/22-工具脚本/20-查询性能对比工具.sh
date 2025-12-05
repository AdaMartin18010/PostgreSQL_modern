#!/bin/bash
#
# PostgreSQL查询性能对比工具
# 功能: 对比优化前后的查询性能
#

set -e

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-postgres}
DB_USER=${DB_USER:-postgres}

if [ "$#" -lt 1 ]; then
    echo "用法: $0 <query_file.sql> [iterations]"
    echo "示例: $0 query.sql 10"
    exit 1
fi

QUERY_FILE=$1
ITERATIONS=${2:-10}

if [ ! -f "$QUERY_FILE" ]; then
    echo "错误: 查询文件不存在: $QUERY_FILE"
    exit 1
fi

psql_cmd() {
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -Atq -c "$1"
}

psql_file() {
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$1" > /dev/null 2>&1
}

echo "=========================================="
echo "PostgreSQL查询性能对比"
echo "查询文件: $QUERY_FILE"
echo "执行次数: $ITERATIONS"
echo "时间: $(date)"
echo "=========================================="

# 1. 获取查询内容
QUERY=$(cat $QUERY_FILE)
echo ""
echo "查询:"
echo "$QUERY"
echo ""

# 2. 热身（预热缓存）
echo "预热缓存..."
for i in {1..3}; do
    psql_file $QUERY_FILE
done

# 3. 基准测试
echo ""
echo "执行基准测试..."

TIMES=()
TOTAL_TIME=0

for i in $(seq 1 $ITERATIONS); do
    # 记录开始时间
    START=$(date +%s%N)

    # 执行查询
    psql_file $QUERY_FILE

    # 记录结束时间
    END=$(date +%s%N)

    # 计算耗时（毫秒）
    DURATION=$(( ($END - $START) / 1000000 ))
    TIMES+=($DURATION)
    TOTAL_TIME=$(( $TOTAL_TIME + $DURATION ))

    echo "  执行 $i/$ITERATIONS: ${DURATION}ms"
done

# 4. 统计分析
echo ""
echo "统计结果:"

# 平均时间
AVG_TIME=$(( $TOTAL_TIME / $ITERATIONS ))
echo "  平均时间: ${AVG_TIME}ms"

# 排序计算中位数
IFS=$'\n' SORTED=($(sort -n <<<"${TIMES[*]}"))
MED_INDEX=$(( $ITERATIONS / 2 ))
MEDIAN=${SORTED[$MED_INDEX]}
echo "  中位数: ${MEDIAN}ms"

# 最小/最大
MIN=${SORTED[0]}
MAX=${SORTED[-1]}
echo "  最小: ${MIN}ms"
echo "  最大: ${MAX}ms"

# 5. EXPLAIN ANALYZE
echo ""
echo "执行计划:"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "EXPLAIN (ANALYZE, BUFFERS) $(cat $QUERY_FILE)"

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

# 保存结果
RESULT_FILE="benchmark_$(date +%Y%m%d_%H%M%S).txt"
cat > $RESULT_FILE <<EOF
查询文件: $QUERY_FILE
执行次数: $ITERATIONS
平均时间: ${AVG_TIME}ms
中位数: ${MEDIAN}ms
最小: ${MIN}ms
最大: ${MAX}ms
测试时间: $(date)
EOF

echo "结果已保存到: $RESULT_FILE"

exit 0
```

**使用**:
```bash
chmod +x 20-查询性能对比工具.sh

# 测试查询性能
echo "SELECT * FROM users WHERE user_id = 123;" > query.sql
./20-查询性能对比工具.sh query.sql 100

# 对比优化前后
./20-查询性能对比工具.sh query_before.sql 50 > before.txt
# 创建索引...
./20-查询性能对比工具.sh query_after.sql 50 > after.txt
diff before.txt after.txt
```
