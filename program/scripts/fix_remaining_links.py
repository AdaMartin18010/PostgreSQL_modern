#!/usr/bin/env python3
"""
修复剩余的高频失效链接模式。
"""

import os
import re
from pathlib import Path

ROOT = Path(r'E:\_src\PostgreSQL_modern')
INTEGRATE_ROOT = ROOT / 'Integrate'

# 修复模式
PATTERNS = [
    # 当前目录重复引用（./12-监控与诊断/ 在 12-监控与诊断 目录下）
    (r'\]\(\./12-监控与诊断/06\.01', '](./06.01'),
    (r'\]\(\./12-监控与诊断/', '](./'),
    (r'\]\(\./30-性能调优/README\.md\)', '](../30-性能调优/README.md)'),
    (r'\]\(\./监控与诊断/12-监控与诊断/', '](../12-监控与诊断/'),
    (r'\]\(\./监控与诊断/30-性能调优/', '](../30-性能调优/'),
    
    # 路径深度错误 (../../01-核心基础/ 应为 ../01-核心基础/)
    (r'\]\(\.\.?/\.\.?/01-核心基础/', '](../01-核心基础/'),
    
    # 根级别文件引用
    (r'\]\(\.\.?/性能调优深入\.md\)', '](../30-性能调优/README.md)'),
    (r'\]\(\.\.?/查询计划与优化器\.md\)', '](../02-查询与优化/02.01-查询优化器/02.01-查询优化器原理.md)'),
    (r'\]\(\.\.?/备份与恢复\.md\)', '](../04-存储与恢复/备份与恢复.md)'),
    (r'\]\(\.\.?/监控与诊断\.md\)', '](../12-监控与诊断/06.01-监控与诊断.md)'),
    (r'\]\(\.\.?/连接池管理\.md\)', '](../30-性能调优/README.md)'),
    (r'\]\(\.\.?/pgvector完整深化指南\.md\)', '](./README.md)'),
    (r'\]\(\.\.?/【深入】TimescaleDB时序数据库完整指南\.md\)', '](../08-流处理与时序/README.md)'),
    
    # 1.1.x 格式路径
    (r'\]\(\./1\.1\.29-[^)]+\.md\)', '](./README.md)'),
    (r'\]\(\.\.?/1\.1\.\d+-[^)]+\.md\)', '](./README.md)'),
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
    print("剩余高频失效链接修复")
    print("=" * 60)
    
    # 扫描所有 Markdown 文件
    all_files = list(INTEGRATE_ROOT.rglob('*.md'))
    
    # 也处理 archive 目录和根目录
    archive_root = ROOT / 'archive'
    if archive_root.exists():
        all_files.extend(archive_root.rglob('*.md'))
    
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
