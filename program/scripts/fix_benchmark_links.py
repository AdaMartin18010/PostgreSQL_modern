#!/usr/bin/env python3
"""
修复基准测试相关文档中的失效链接。
将不存在的 feature_bench/, tools/, scripts/, sql/, config/ 链接
指向相关的 README 或移除。
"""

import os
import re
from pathlib import Path

ROOT = Path(r'E:\_src\PostgreSQL_modern')
TARGET_DIR = ROOT / 'Integrate' / '22-工具与资源'

# 链接修复模式
PATTERNS = [
    # feature_bench 链接 → 18-版本特性
    (r'\]\(\.\.?/feature_bench/async_io\.md\)', '](../18-版本特性/18.01-PostgreSQL18新特性/README.md#异步io)'),
    (r'\]\(\.\.?/feature_bench/parallel_query\.md\)', '](../02-查询与优化/02.05-并行查询/02.05-并行查询处理.md)'),
    (r'\]\(\.\.?/feature_bench/skip_scan\.md\)', '](../18-版本特性/18.01-PostgreSQL18新特性/02-跳跃扫描Skip-Scan完整指南.md)'),
    (r'\]\(\.\.?/feature_bench/parallel_index_build\.md\)', '](../02-查询与优化/02.02-索引结构/02.02-索引结构与优化.md)'),
    (r'\]\(\.\.?/feature_bench/[^)]+\.md\)', '](./README.md)'),
    
    # scripts 链接 → README
    (r'\]\(\.\.?/scripts/mix_[^)]+\.sql\)', '](./README.md)'),
    
    # tools 链接 → README（这些是计划中的脚本）
    (r'\]\(\.\.?/tools/[^)]+\.(sh|ps1)\)', '](./README.md)'),
    
    # sql 链接 → README
    (r'\]\(\.\.?/sql/benchmark_[^)]+\.sql\)', '](./README.md)'),
    
    # config 链接 → README
    (r'\]\(\.\.?/config/benchmark_[^)]+\.json\)', '](./README.md)'),
]


def fix_file(filepath: Path) -> int:
    """修复单个文件中的链接"""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return 0
    
    original = content
    changes = 0
    
    for pattern, replacement in PATTERNS:
        new_content, n = re.subn(pattern, replacement, content)
        if n > 0:
            changes += n
            content = new_content
    
    if content != original:
        try:
            filepath.write_text(content, encoding='utf-8')
            rel = filepath.relative_to(ROOT) if filepath.is_relative_to(ROOT) else filepath
            print(f"  ✅ 修复 {changes} 处: {rel}")
            return changes
        except Exception as e:
            return 0
    
    return 0


def main():
    print("=" * 60)
    print("基准测试文档链接修复")
    print("=" * 60)
    
    # 只处理 22-工具与资源 目录
    all_files = list(TARGET_DIR.rglob('*.md'))
    
    print(f"\n扫描到 {len(all_files)} 个 Markdown 文件")
    
    total_fixes = 0
    fixed_files = 0
    
    for f in all_files:
        fixes = fix_file(f)
        if fixes > 0:
            total_fixes += fixes
            fixed_files += 1
    
    print("\n" + "=" * 60)
    print(f"完成！修复了 {fixed_files} 个文件中的 {total_fixes} 处链接")
    print("=" * 60)


if __name__ == '__main__':
    main()
