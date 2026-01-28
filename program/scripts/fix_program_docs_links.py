#!/usr/bin/env python3
"""
修复 program 目录下文件中的 ../docs/ 失效链接。
"""

import os
import re
from pathlib import Path

ROOT = Path(r'E:\_src\PostgreSQL_modern')
PROGRAM_DIR = ROOT / 'program'

# program 目录下的 ../docs/... → ../Integrate/...
PROGRAM_MAPPINGS = [
    (r'\.\./docs/01-PostgreSQL18/40-PostgreSQL18新特性总结\.md', '../Integrate/18-版本特性/18.01-PostgreSQL18新特性/README.md'),
    (r'\.\./docs/01-PostgreSQL18/08-性能调优实战指南\.md', '../Integrate/30-性能调优/README.md'),
    (r'\.\./docs/05-Production/20-生产环境检查清单\.md', '../Integrate/21-最佳实践/README.md'),
    (r'\.\./docs/05-Production/06-Kubernetes生产部署完整指南\.md', '../Integrate/14-云原生与容器化/Kubernetes-高可用-PostgreSQL-完整指南.md'),
    (r'\.\./docs/01-PostgreSQL18/11-VACUUM增强与积极冻结策略完整指南\.md', '../Integrate/18-版本特性/18.01-PostgreSQL18新特性/11-VACUUM增强与积极冻结策略完整指南.md'),
    (r'\.\./DataBaseTheory/22-工具脚本/', '../Integrate/22-工具与资源/'),
    (r'\.\./QUICK-REFERENCE\.md', '../QUICK-REFERENCE.md'),  # 这个文件在根目录
]

# 根目录文件的链接修复
ROOT_FILE_FIXES = {
    'README.md': [
        (r'Integrate/18-版本特性/18\.01-PostgreSQL18新特性/02-范围扫描Skip-Scan完整指南\.md', 
         'Integrate/18-版本特性/18.01-PostgreSQL18新特性/02-跳跃扫描Skip-Scan完整指南.md'),
        (r'Integrate/02-查询与优化/02\.05-并行查询/README\.md', 
         'Integrate/02-查询与优化/02.05-并行查询/02.05-并行查询处理.md'),
    ],
    'FAQ.md': [
        (r'Integrate/18-版本特性/18\.01-PostgreSQL18新特性/02-范围扫描Skip-Scan完整指南\.md', 
         'Integrate/18-版本特性/18.01-PostgreSQL18新特性/02-跳跃扫描Skip-Scan完整指南.md'),
    ],
    '【🚀QUICK-START】5分钟快速上手指南.md': [
        (r'\./theory/MVCC-ACID-CAP/', 'Integrate/25-理论体系/'),
        (r'\./theory/DataBaseTheory/19-场景案例库/', 'Integrate/19-实战案例/'),
    ],
    'START-HERE.md': [
        (r'\./training/main/', 'Integrate/'),
    ],
}


def fix_file(filepath: Path, mappings: list) -> int:
    """修复单个文件中的链接"""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  ⚠️ 无法读取: {filepath} - {e}")
        return 0
    
    original = content
    changes = 0
    
    for pattern, replacement in mappings:
        new_content, n = re.subn(pattern, replacement, content)
        if n > 0:
            changes += n
            content = new_content
    
    if content != original:
        try:
            filepath.write_text(content, encoding='utf-8')
            print(f"  ✅ 修复 {changes} 处: {filepath.relative_to(ROOT)}")
            return changes
        except Exception as e:
            print(f"  ❌ 写入失败: {filepath} - {e}")
            return 0
    
    return 0


def main():
    print("=" * 60)
    print("program 目录及根目录链接修复")
    print("=" * 60)
    
    total_fixes = 0
    fixed_files = 0
    
    # 1. 修复 program 目录下的文件
    print("\n>>> 修复 program 目录...")
    for md_file in PROGRAM_DIR.rglob('*.md'):
        fixes = fix_file(md_file, PROGRAM_MAPPINGS)
        if fixes > 0:
            total_fixes += fixes
            fixed_files += 1
    
    # 2. 修复根目录指定文件
    print("\n>>> 修复根目录文件...")
    for filename, mappings in ROOT_FILE_FIXES.items():
        filepath = ROOT / filename
        if filepath.exists():
            fixes = fix_file(filepath, mappings)
            if fixes > 0:
                total_fixes += fixes
                fixed_files += 1
        else:
            print(f"  ⚠️ 文件不存在: {filename}")
    
    print("\n" + "=" * 60)
    print(f"完成！修复了 {fixed_files} 个文件中的 {total_fixes} 处链接")
    print("=" * 60)


if __name__ == '__main__':
    main()
