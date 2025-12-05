#!/bin/bash
#
# PostgreSQL表膨胀检测与自动修复工具
#

set -e

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-postgres}
DB_USER=${DB_USER:-postgres}

BLOAT_THRESHOLD=20  # 膨胀率阈值（百分比）
AUTO_FIX=${AUTO_FIX:-false}

psql_cmd() {
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -Atq -c "$1"
}

echo "=========================================="
echo "PostgreSQL表膨胀检测"
echo "时间: $(date)"
echo "=========================================="

# 1. 检测表膨胀
echo ""
echo "检测表膨胀..."

BLOATED_TABLES=$(psql_cmd "
SELECT 
    schemaname || '.' || tablename AS table_name,
    n_dead_tup,
    n_live_tup,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS bloat_pct,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
  AND n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0) > $BLOAT_THRESHOLD
ORDER BY n_dead_tup DESC;
" | tr '|' '\t')

if [ -z "$BLOATED_TABLES" ]; then
    echo "✓ 无严重膨胀的表"
    exit 0
fi

echo "发现膨胀的表:"
echo "$BLOATED_TABLES" | while IFS=$'\t' read table dead live bloat size; do
    echo "  [$bloat%] $table: $dead 死元组, 大小 $size"
done

# 2. 自动修复
if [ "$AUTO_FIX" = "true" ]; then
    echo ""
    echo "开始自动修复..."
    
    echo "$BLOATED_TABLES" | while IFS=$'\t' read table dead live bloat size; do
        echo ""
        echo "处理 $table (膨胀率: $bloat%)..."
        
        # 提取表名（移除schema前缀）
        TABLE_NAME=$(echo $table | cut -d'.' -f2)
        
        # 判断是否需要VACUUM FULL
        if (( $(echo "$bloat > 50" | bc -l) )); then
            echo "  膨胀严重(>50%)，执行 VACUUM FULL..."
            psql_cmd "VACUUM FULL VERBOSE $table;" || echo "  失败"
        else
            echo "  执行 VACUUM ANALYZE..."
            psql_cmd "VACUUM ANALYZE VERBOSE $table;" || echo "  失败"
        fi
        
        # 检查修复后状态
        NEW_BLOAT=$(psql_cmd "
SELECT ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2)
FROM pg_stat_user_tables
WHERE schemaname||'.'||tablename = '$table';
")
        
        echo "  修复后膨胀率: $NEW_BLOAT%"
    done
    
    echo ""
    echo "✓ 修复完成"
else
    echo ""
    echo "建议手动执行VACUUM："
    echo "$BLOATED_TABLES" | while IFS=$'\t' read table dead live bloat size; do
        echo "  VACUUM ANALYZE $table;"
    done
fi

# 3. 索引膨胀
echo ""
echo "检测索引膨胀..."

psql_cmd "
SELECT 
    schemaname || '.' || tablename AS table_name,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan
FROM pg_stat_user_indexes
WHERE pg_relation_size(indexrelid) > 104857600  -- >100MB
  AND idx_scan < 100  -- 扫描次数少
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 10;
" | tr '|' '\t' | while IFS=$'\t' read table index size scans; do
    echo "  $index ($size): 扫描${scans}次"
    if [ "$AUTO_FIX" = "true" ]; then
        echo "    执行 REINDEX CONCURRENTLY $index"
        psql_cmd "REINDEX INDEX CONCURRENTLY $index;" || echo "    失败"
    fi
done

echo ""
echo "=========================================="
echo "检测完成"
echo "=========================================="

exit 0
```

**使用**:
```bash
# 检测模式
./16-表膨胀检测与修复.sh

# 自动修复模式
AUTO_FIX=true ./16-表膨胀检测与修复.sh

# 定时检测
0 3 * * * /path/to/16-表膨胀检测与修复.sh > /var/log/bloat_check_$(date +\%Y\%m\%d).log 2>&1

# 每周自动修复
0 4 * * 0 AUTO_FIX=true /path/to/16-表膨胀检测与修复.sh
```
