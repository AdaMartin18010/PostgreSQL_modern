#!/bin/bash
# PostgreSQL 18验证测试套件
# 运行所有测试并生成报告

set -e

CONN_STR="${1:-dbname=testdb user=postgres}"

echo "======================================================================"
echo "     PostgreSQL 18 MVCC-ACID-CAP验证测试套件"
echo "======================================================================"
echo "连接字符串: $CONN_STR"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

PASSED=0
FAILED=0

# 测试1：异步I/O
echo ">>> 测试1：异步I/O验证"
echo "----------------------------------------------------------------------"
if python3 async_io_test.py "$CONN_STR"; then
    ((PASSED++))
    echo "✅ 异步I/O测试通过"
else
    ((FAILED++))
    echo "❌ 异步I/O测试失败"
fi
echo ""

# 测试2：组提交
echo ">>> 测试2：组提交验证"
echo "----------------------------------------------------------------------"
if python3 group_commit_test.py "$CONN_STR"; then
    ((PASSED++))
    echo "✅ 组提交测试通过"
else
    ((FAILED++))
    echo "❌ 组提交测试失败"
fi
echo ""

# 汇总
echo "======================================================================"
echo "                      测试总结"
echo "======================================================================"
echo "通过: $PASSED"
echo "失败: $FAILED"
echo "总计: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 所有测试通过！PostgreSQL 18保持MVCC-ACID-CAP理论正确性！"
    echo ""
    echo "核心验证:"
    echo "  ✅ 异步I/O保持MVCC可见性语义"
    echo "  ✅ 组提交保持ACID原子性和持久性"
    echo "  ✅ 性能提升同时保持理论正确性"
    exit 0
else
    echo "⚠️  $FAILED 个测试失败，请检查日志"
    exit 1
fi
