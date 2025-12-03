#!/bin/bash
# 修复数据库理论模块链接的脚本

echo "开始修复链接..."

# 修复相对路径链接
find . -type f -name "*.md" -exec sed -i 's|\.\./10-理论基础/|../数据库理论/|g' {} \;
find . -type f -name "*.md" -exec sed -i 's|\.\./\.\./10-理论基础/|../../数据库理论/|g' {} \;
find . -type f -name "*.md" -exec sed -i 's|\.\./\.\./\.\./10-理论基础/|../../../数据库理论/|g' {} \;

# 修复绝对路径链接
find . -type f -name "*.md" -exec sed -i 's|PostgreSQL/10-理论基础/|数据库理论/|g' {} \;
find . -type f -name "*.md" -exec sed -i 's|10-理论基础/|数据库理论/|g' {} \;

# 修复README中的引用
find . -type f -name "*.md" -exec sed -i 's|10-理论基础|数据库理论|g' {} \;

echo "链接修复完成！"
