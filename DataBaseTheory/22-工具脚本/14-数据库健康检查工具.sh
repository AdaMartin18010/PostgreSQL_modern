#!/bin/bash
#
# PostgreSQL数据库健康检查工具
# 功能: 快速诊断数据库健康状态
#

set -e

# 配置
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-postgres}
DB_USER=${DB_USER:-postgres}

# 颜色
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 输出函数
print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

print_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# PSQL命令
psql_cmd() {
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -Atq -c "$1"
}

# 1. 基础信息
print_header "数据库基础信息"

VERSION=$(psql_cmd "SELECT version();")
echo "版本: $VERSION"

UPTIME=$(psql_cmd "SELECT now() - pg_postmaster_start_time();")
echo "运行时间: $UPTIME"

DB_SIZE=$(psql_cmd "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));")
echo "数据库大小: $DB_SIZE"

# 2. 连接检查
print_header "连接状态"

MAX_CONN=$(psql_cmd "SELECT setting FROM pg_settings WHERE name = 'max_connections';")
CURRENT_CONN=$(psql_cmd "SELECT COUNT(*) FROM pg_stat_activity;")
CONN_RATIO=$(echo "scale=2; $CURRENT_CONN * 100 / $MAX_CONN" | bc)

echo "连接数: $CURRENT_CONN / $MAX_CONN ($CONN_RATIO%)"

if [ $(echo "$CONN_RATIO > 90" | bc) -eq 1 ]; then
    print_error "连接数>90%，建议使用连接池"
elif [ $(echo "$CONN_RATIO > 80" | bc) -eq 1 ]; then
    print_warning "连接数>80%，注意监控"
else
    print_ok "连接数正常"
fi

# 空闲事务
IDLE_IN_TX=$(psql_cmd "SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'idle in transaction';")
if [ $IDLE_IN_TX -gt 0 ]; then
    print_warning "存在 $IDLE_IN_TX 个空闲事务"
fi

# 3. 性能指标
print_header "性能指标"

# 缓存命中率
CACHE_HIT=$(psql_cmd "
SELECT ROUND(SUM(blks_hit) * 100.0 / NULLIF(SUM(blks_hit + blks_read), 0), 2)
FROM pg_stat_database WHERE datname = '$DB_NAME';
")

echo "缓存命中率: $CACHE_HIT%"
if [ $(echo "$CACHE_HIT < 90" | bc) -eq 1 ]; then
    print_warning "缓存命中率<90%，考虑增加shared_buffers"
else
    print_ok "缓存命中率良好"
fi

# TPS
TPS=$(psql_cmd "
SELECT xact_commit + xact_rollback 
FROM pg_stat_database 
WHERE datname = '$DB_NAME';
")
echo "TPS: $TPS"

# 4. 慢查询检查
print_header "慢查询检查"

SLOW_QUERIES=$(psql_cmd "
SELECT COUNT(*) FROM pg_stat_activity 
WHERE state = 'active' 
AND query_start < now() - INTERVAL '10 seconds';
")

if [ $SLOW_QUERIES -gt 0 ]; then
    print_warning "存在 $SLOW_QUERIES 个执行>10秒的查询"
    
    psql_cmd "
SELECT 
    pid,
    LEFT(query, 80) AS query,
    now() - query_start AS duration
FROM pg_stat_activity 
WHERE state = 'active' 
AND query_start < now() - INTERVAL '10 seconds'
ORDER BY query_start
LIMIT 5;
" | while IFS='|' read pid query duration; do
        echo "  PID $pid: $query (${duration})"
    done
else
    print_ok "无慢查询"
fi

# 5. 锁等待
print_header "锁等待检查"

LOCK_WAITS=$(psql_cmd "SELECT COUNT(*) FROM pg_locks WHERE NOT granted;")

if [ $LOCK_WAITS -gt 0 ]; then
    print_warning "存在 $LOCK_WAITS 个锁等待"
else
    print_ok "无锁等待"
fi

# 6. 表膨胀
print_header "表膨胀检查"

BLOATED_TABLES=$(psql_cmd "
SELECT COUNT(*) FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
AND n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0) > 20;
")

if [ $BLOATED_TABLES -gt 0 ]; then
    print_warning "有 $BLOATED_TABLES 个表严重膨胀(>20%)"
    
    psql_cmd "
SELECT 
    tablename,
    n_dead_tup,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
AND n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0) > 20
ORDER BY n_dead_tup DESC
LIMIT 5;
" | while IFS='|' read table dead pct; do
        echo "  $table: $dead 死元组 ($pct%)"
    done
else
    print_ok "表膨胀正常"
fi

# 7. 复制延迟（如果是Primary）
IS_PRIMARY=$(psql_cmd "SELECT NOT pg_is_in_recovery();")

if [ "$IS_PRIMARY" = "t" ]; then
    print_header "复制延迟检查"
    
    REPLICA_COUNT=$(psql_cmd "SELECT COUNT(*) FROM pg_stat_replication;")
    
    if [ $REPLICA_COUNT -gt 0 ]; then
        echo "Replica数量: $REPLICA_COUNT"
        
        psql_cmd "
SELECT 
    application_name,
    client_addr,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) / 1024 / 1024 AS lag_mb
FROM pg_stat_replication;
" | while IFS='|' read app addr state sync lag; do
            echo "  $app ($addr): $state, $sync, lag=${lag}MB"
            
            if [ $(echo "$lag > 100" | bc) -eq 1 ]; then
                print_error "复制延迟>100MB"
            fi
        done
    else
        echo "无Replica配置"
    fi
fi

# 8. 磁盘空间
print_header "磁盘空间检查"

DATA_DIR=$(psql_cmd "SHOW data_directory;")
DISK_USAGE=$(df -h "$DATA_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')

echo "数据目录: $DATA_DIR"
echo "磁盘使用: $DISK_USAGE%"

if [ $DISK_USAGE -gt 90 ]; then
    print_error "磁盘使用>90%"
elif [ $DISK_USAGE -gt 80 ]; then
    print_warning "磁盘使用>80%"
else
    print_ok "磁盘空间充足"
fi

# 9. WAL情况
WAL_COUNT=$(psql_cmd "SELECT COUNT(*) FROM pg_ls_waldir();")
WAL_SIZE=$(psql_cmd "SELECT pg_size_pretty(SUM(size)) FROM pg_ls_waldir();")

echo "WAL文件数: $WAL_COUNT"
echo "WAL总大小: $WAL_SIZE"

if [ $WAL_COUNT -gt 100 ]; then
    print_warning "WAL文件过多，检查归档"
fi

# 10. 总结
print_header "健康检查总结"

echo "检查完成时间: $(date)"
echo ""
echo "建议:"
echo "  1. 定期VACUUM ANALYZE"
echo "  2. 监控慢查询并优化"
echo "  3. 保持足够的磁盘空间"
echo "  4. 使用连接池管理连接"
echo "  5. 配置适当的资源限制"

exit 0
```

**使用**:
```bash
chmod +x 14-数据库健康检查工具.sh

# 基本使用
./14-数据库健康检查工具.sh

# 指定数据库
DB_HOST=remote-server DB_NAME=mydb ./14-数据库健康检查工具.sh

# 定时检查（cron）
*/30 * * * * /path/to/14-数据库健康检查工具.sh > /var/log/pg_health_$(date +\%Y\%m\%d_\%H\%M).log 2>&1
```
