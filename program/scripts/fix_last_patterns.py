#!/usr/bin/env python3
"""
修复最后剩余的高频失效链接模式。
"""

import os
import re
from pathlib import Path

ROOT = Path(r'E:\_src\PostgreSQL_modern')
INTEGRATE_ROOT = ROOT / 'Integrate'

# 修复模式
PATTERNS = [
    # 26-数据管理 下错误的子目录
    (r'26-数据管理/02-查询与优化/README\.md', '02-查询与优化/README.md'),
    
    # 分区表管理目录不存在
    (r'\]\(\./分区表管理/[^)]+\)', '](./02-查询与优化/README.md)'),
    (r'\]\(\.\./分区表管理/[^)]+\)', '](../02-查询与优化/README.md)'),
    
    # examples, benchmarks, notebooks 目录不存在
    (r'\]\(\./examples/[^)]+\)', '](./README.md)'),
    (r'\]\(\./benchmarks[^)]*\)', '](./README.md)'),
    (r'\]\(\./notebooks[^)]*\)', '](./README.md)'),
    
    # program/scripts 在 Integrate 下不正确
    (r'\]\(\./program/scripts/README\.md\)', '](../../program/scripts/README.md)'),
    
    # 30-性能调优 重复目录路径
    (r'30-性能调优/30-性能调优/README\.md', '30-性能调优/README.md'),
    
    # 34-模型与建模 下各种子路径
    (r'34-模型与建模/03-建模方法论/成本收益分析\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/04-OLTP建模/PostgreSQL实现\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/09-建模模式与反模式/[^)]+\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/other/path/to/doc\.md', '34-模型与建模/README.md'),
    
    # 占位符链接
    (r'\]\(path/to/[^)]+\.md\)', '](./README.md)'),
    (r'\]\(\./path/to/[^)]+\.md\)', '](./README.md)'),
    (r'\]\(\.\./path/to/[^)]+\.md\)', '](../README.md)'),
    
    # 根级别文件引用
    (r'\]\(\./【案例集】PostgreSQL慢查询优化完整实战手册\.md\)', '](./02-查询与优化/README.md)'),
    (r'\]\(\.\./【案例集】PostgreSQL慢查询优化完整实战手册\.md\)', '](../02-查询与优化/README.md)'),
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
    print("最后剩余高频失效链接修复")
    print("=" * 60)
    
    # 扫描所有 Markdown 文件
    all_files = list(INTEGRATE_ROOT.rglob('*.md'))
    
    # 也处理根目录
    for f in ROOT.glob('*.md'):
        all_files.append(f)
    
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
