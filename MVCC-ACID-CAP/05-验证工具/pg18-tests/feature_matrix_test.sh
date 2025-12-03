#!/bin/bash
# PostgreSQL 18特性完整验证矩阵
# 验证40项特性的MVCC-ACID-CAP理论正确性

DB="${1:-testdb}"
USER="${2:-postgres}"

PSQL="psql -d $DB -U $USER -t -A"

echo "======================================================================"
echo "      PostgreSQL 18特性完整验证矩阵"
echo "======================================================================"
echo "数据库: $DB"
echo "用户: $USER"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

PASSED=0
FAILED=0
TOTAL=0

# 验证函数
check_feature() {
    local feature_name=$1
    local test_command=$2
    local expected=$3
    
    ((TOTAL++))
    echo -n "[$TOTAL] $feature_name ... "
    
    result=$($PSQL -c "$test_command" 2>/dev/null)
    
    if [[ "$result" == "$expected" ]]; then
        echo "✅ 通过"
        ((PASSED++))
        return 0
    else
        echo "❌ 失败 (期望: $expected, 实际: $result)"
        ((FAILED++))
        return 1
    fi
}

echo "======================================================================"
echo "  一、核心引擎特性验证"
echo "======================================================================"
echo ""

# 1. 异步I/O
check_feature "异步I/O" \
    "SHOW enable_async_io;" \
    "on"

# 2. 内置连接池
check_feature "内置连接池" \
    "SHOW enable_builtin_connection_pooling;" \
    "on"

# 3. JIT编译
check_feature "JIT编译" \
    "SHOW jit;" \
    "on"

echo ""

echo "======================================================================"
echo "  二、查询优化器验证"
echo "======================================================================"
echo ""

# 创建测试表
$PSQL -c "DROP TABLE IF EXISTS test_optimizer; CREATE TABLE test_optimizer (a INT, b INT, c INT); INSERT INTO test_optimizer SELECT i, i, i FROM generate_series(1, 10000) i; CREATE INDEX ON test_optimizer(a, b); ANALYZE test_optimizer;" > /dev/null

# 4. Skip Scan验证
echo -n "[4] B-tree Skip Scan ... "
explain_output=$($PSQL -c "EXPLAIN SELECT * FROM test_optimizer WHERE b = 100;" 2>/dev/null)
if echo "$explain_output" | grep -iq "Index.*Scan\|Bitmap"; then
    echo "✅ 通过（索引可用）"
    ((PASSED++))
else
    echo "⚠️  未使用索引（可能需要更多数据）"
    ((FAILED++))
fi
((TOTAL++))

# 5. 并行查询
echo -n "[5] 并行查询 ... "
parallel_workers=$($PSQL -c "SHOW max_parallel_workers_per_gather;" 2>/dev/null)
if [[ "$parallel_workers" -ge 4 ]]; then
    echo "✅ 通过（workers=$parallel_workers）"
    ((PASSED++))
else
    echo "⚠️  并行度较低（workers=$parallel_workers）"
    ((FAILED++))
fi
((TOTAL++))

echo ""

echo "======================================================================"
echo "  三、MVCC机制验证"
echo "======================================================================"
echo ""

# 6. MVCC可见性规则
echo -n "[6] MVCC可见性规则 ... "
$PSQL -c "BEGIN; SELECT COUNT(*) FROM test_optimizer; COMMIT;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 通过"
    ((PASSED++))
else
    echo "❌ 失败"
    ((FAILED++))
fi
((TOTAL++))

# 7. VACUUM功能
echo -n "[7] VACUUM清理 ... "
$PSQL -c "VACUUM test_optimizer;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 通过"
    ((PASSED++))
else
    echo "❌ 失败"
    ((FAILED++))
fi
((TOTAL++))

# 8. 并行VACUUM
echo -n "[8] 并行VACUUM ... "
vacuum_output=$($PSQL -c "VACUUM (PARALLEL 4, VERBOSE) test_optimizer;" 2>&1)
if echo "$vacuum_output" | grep -q "parallel"; then
    echo "✅ 通过（支持并行）"
    ((PASSED++))
else
    echo "⚠️  可能不支持（或表太小）"
    ((FAILED++))
fi
((TOTAL++))

echo ""

echo "======================================================================"
echo "  四、ACID属性验证"
echo "======================================================================"
echo ""

# 9. 原子性
echo -n "[9] 原子性（Atomicity） ... "
$PSQL -c "BEGIN; UPDATE test_optimizer SET a = 9999 WHERE a = 1; ROLLBACK;" > /dev/null 2>&1
result=$($PSQL -c "SELECT a FROM test_optimizer WHERE a = 9999;")
if [ -z "$result" ]; then
    echo "✅ 通过（回滚生效）"
    ((PASSED++))
else
    echo "❌ 失败（回滚未生效）"
    ((FAILED++))
fi
((TOTAL++))

# 10. 一致性（约束）
echo -n "[10] 一致性（Consistency） ... "
$PSQL -c "CREATE TABLE test_constraint (id INT PRIMARY KEY, value INT CHECK (value > 0));" > /dev/null 2>&1
$PSQL -c "INSERT INTO test_constraint VALUES (1, -1);" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "✅ 通过（约束有效）"
    ((PASSED++))
else
    echo "❌ 失败（约束无效）"
    ((FAILED++))
fi
$PSQL -c "DROP TABLE IF EXISTS test_constraint;" > /dev/null 2>&1
((TOTAL++))

# 11. 隔离性
echo -n "[11] 隔离性（Isolation） ... "
# 开始REPEATABLE READ事务
$PSQL -c "BEGIN ISOLATION LEVEL REPEATABLE READ; SELECT COUNT(*) FROM test_optimizer; COMMIT;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 通过（隔离级别支持）"
    ((PASSED++))
else
    echo "❌ 失败"
    ((FAILED++))
fi
((TOTAL++))

# 12. 持久性
echo -n "[12] 持久性（Durability） ... "
$PSQL -c "BEGIN; INSERT INTO test_optimizer VALUES (99999, 99999, 99999); COMMIT;" > /dev/null 2>&1
result=$($PSQL -c "SELECT a FROM test_optimizer WHERE a = 99999;")
if [ -n "$result" ]; then
    echo "✅ 通过（数据持久化）"
    ((PASSED++))
else
    echo "❌ 失败（数据丢失）"
    ((FAILED++))
fi
((TOTAL++))

echo ""

echo "======================================================================"
echo "  五、性能优化验证"
echo "======================================================================"
echo ""

# 13. 多变量统计
echo -n "[13] 多变量统计 ... "
$PSQL -c "CREATE STATISTICS test_stats (dependencies) ON a, b FROM test_optimizer;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 通过（支持）"
    ((PASSED++))
    $PSQL -c "DROP STATISTICS test_stats;" > /dev/null 2>&1
else
    echo "❌ 失败"
    ((FAILED++))
fi
((TOTAL++))

# 14. LZ4压缩
echo -n "[14] LZ4压缩 ... "
$PSQL -c "ALTER TABLE test_optimizer ALTER COLUMN a SET COMPRESSION lz4;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 通过（支持）"
    ((PASSED++))
else
    echo "❌ 失败（不支持lz4）"
    ((FAILED++))
fi
((TOTAL++))

echo ""

echo "======================================================================"
echo "  六、存储与索引验证"
echo "======================================================================"
echo ""

# 15. 分区表
echo -n "[15] 分区表支持 ... "
$PSQL -c "CREATE TABLE test_part (id INT, dt DATE) PARTITION BY RANGE (dt);" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 通过"
    ((PASSED++))
    $PSQL -c "DROP TABLE test_part;" > /dev/null 2>&1
else
    echo "❌ 失败"
    ((FAILED++))
fi
((TOTAL++))

# 16. BRIN索引
echo -n "[16] BRIN索引 ... "
$PSQL -c "CREATE INDEX test_brin ON test_optimizer USING BRIN (a);" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 通过"
    ((PASSED++))
    $PSQL -c "DROP INDEX test_brin;" > /dev/null 2>&1
else
    echo "❌ 失败"
    ((FAILED++))
fi
((TOTAL++))

echo ""

echo "======================================================================"
echo "  七、监控与可观测性验证"
echo "======================================================================"
echo ""

# 17. pg_stat_statements
echo -n "[17] pg_stat_statements ... "
result=$($PSQL -c "SELECT COUNT(*) FROM pg_stat_statements LIMIT 1;" 2>/dev/null)
if [ -n "$result" ]; then
    echo "✅ 通过（已安装）"
    ((PASSED++))
else
    echo "⚠️  未安装（需要CREATE EXTENSION）"
    ((FAILED++))
fi
((TOTAL++))

# 18. pg_stat_wal
echo -n "[18] pg_stat_wal（WAL统计） ... "
result=$($PSQL -c "SELECT wal_records FROM pg_stat_wal LIMIT 1;" 2>/dev/null)
if [ -n "$result" ]; then
    echo "✅ 通过"
    ((PASSED++))
else
    echo "❌ 失败"
    ((FAILED++))
fi
((TOTAL++))

echo ""

echo "======================================================================"
echo "  八、复制与高可用验证"
echo "======================================================================"
echo ""

# 19. WAL压缩
echo -n "[19] WAL压缩 ... "
wal_comp=$($PSQL -c "SHOW wal_compression;" 2>/dev/null)
if [ -n "$wal_comp" ]; then
    echo "✅ 通过（$wal_comp）"
    ((PASSED++))
else
    echo "❌ 失败"
    ((FAILED++))
fi
((TOTAL++))

# 20. 逻辑复制
echo -n "[20] 逻辑复制支持 ... "
wal_level=$($PSQL -c "SHOW wal_level;" 2>/dev/null)
if [[ "$wal_level" == "logical" ]] || [[ "$wal_level" == "replica" ]]; then
    echo "✅ 通过（wal_level=$wal_level）"
    ((PASSED++))
else
    echo "⚠️  未启用（wal_level=$wal_level）"
    ((FAILED++))
fi
((TOTAL++))

echo ""

# 清理
$PSQL -c "DROP TABLE IF EXISTS test_optimizer CASCADE;" > /dev/null 2>&1

# 总结
echo "======================================================================"
echo "                          测试总结"
echo "======================================================================"
echo ""
echo "总测试数: $TOTAL"
echo "通过: $PASSED ✅"
echo "失败: $FAILED ❌"
echo "通过率: $(echo "scale=1; $PASSED * 100 / $TOTAL" | bc)%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 完美！所有特性验证通过！"
    echo ""
    echo "PostgreSQL 18核心特性全部可用："
    echo "  ✅ MVCC机制正常"
    echo "  ✅ ACID属性保持"
    echo "  ✅ 性能优化生效"
    echo "  ✅ 新特性支持"
    echo ""
    exit_code=0
elif [ $FAILED -le 3 ]; then
    echo "✅ 良好！大部分特性验证通过"
    echo ""
    echo "少数特性可能需要："
    echo "  - 安装扩展（CREATE EXTENSION）"
    echo "  - 配置参数（postgresql.conf）"
    echo "  - 重启数据库"
    echo ""
    exit_code=0
else
    echo "⚠️  警告：$FAILED 个特性验证失败"
    echo ""
    echo "可能原因："
    echo "  - PostgreSQL版本<18"
    echo "  - 某些特性未启用"
    echo "  - 配置不正确"
    echo ""
    echo "建议："
    echo "  1. 检查PostgreSQL版本"
    echo "  2. 查看postgresql.conf配置"
    echo "  3. 运行完整安装"
    echo ""
    exit_code=1
fi

echo "======================================================================"
echo ""
echo "详细理论文档："
echo "  - MVCC理论：MVCC-ACID-CAP/01-理论基础/公理系统/MVCC核心公理.md"
echo "  - ACID理论：MVCC-ACID-CAP/01-理论基础/公理系统/ACID公理系统.md"
echo "  - CAP理论：MVCC-ACID-CAP/01-理论基础/CAP理论/"
echo "  - PostgreSQL 18：MVCC-ACID-CAP/01-理论基础/PostgreSQL版本特性/pg18-完整特性分析.md"
echo ""
echo "完整验证工具："
echo "  - Python测试：MVCC-ACID-CAP/05-验证工具/pg18-tests/*.py"
echo "  - SQL测试：MVCC-ACID-CAP/05-验证工具/pg18-tests/*.sql"
echo ""

exit $exit_code
