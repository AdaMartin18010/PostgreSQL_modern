#!/usr/bin/env python3
"""
修复错误引入的 ./30-性能调优/ 路径。
将其改为正确的 ../30-性能调优/。
"""

import os
import re
from pathlib import Path

ROOT = Path(r'E:\_src\PostgreSQL_modern')
INTEGRATE_ROOT = ROOT / 'Integrate'


def fix_file(filepath: Path) -> int:
    """修复单个文件中的链接"""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return 0
    
    original = content
    changes = 0
    
    # 获取文件相对于 Integrate 的目录
    try:
        rel = filepath.relative_to(INTEGRATE_ROOT)
        depth = len(rel.parts) - 1  # -1 因为最后一部分是文件名
    except ValueError:
        depth = 0
    
    # 只修复不在 30-性能调优 目录下的文件
    if '30-性能调优' not in str(filepath):
        # ./30-性能调优/ → ../30-性能调优/
        new_content, n = re.subn(r'\]\(\./30-性能调优/', '](../30-性能调优/', content)
        if n > 0:
            changes += n
            content = new_content
    
    # 修复 ./12-监控与诊断/ 重复
    new_content, n = re.subn(r'\]\(\./12-监控与诊断/12-监控与诊断/', '](./12-监控与诊断/', content)
    if n > 0:
        changes += n
        content = new_content
    
    # 修复 12-监控与诊断 目录下的 ./12-监控与诊断/
    if '12-监控与诊断' in str(filepath) and '12-监控与诊断' in str(filepath.parent.name):
        new_content, n = re.subn(r'\]\(\./12-监控与诊断/', '](./)', content)
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
    print("修复错误引入的 ./30-性能调优/ 路径")
    print("=" * 60)
    
    # 扫描所有 Markdown 文件
    all_files = list(INTEGRATE_ROOT.rglob('*.md'))
    
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
