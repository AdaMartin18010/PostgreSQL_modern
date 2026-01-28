#!/usr/bin/env python3
"""
修复最终剩余的高频失效链接模式。
"""

import os
import re
from pathlib import Path

ROOT = Path(r'E:\_src\PostgreSQL_modern')
INTEGRATE_ROOT = ROOT / 'Integrate'

# 修复模式
PATTERNS = [
    # 根级别文件引用
    (r'\]\(\./PostgreSQL可观测性完整指南\.md\)', '](./12-监控与诊断/PostgreSQL可观测性完整指南.md)'),
    (r'\]\(\.\./30-性能调优/README\.md\)', '](./30-性能调优/README.md)'),
    (r'\]\(\.\./P2-项目完成总结\.md\)', '](./README.md)'),
    (r'\]\(\./性能调优实战指南\.md\)', '](./30-性能调优/README.md)'),
    (r'\]\(\.\./性能调优实战指南\.md\)', '](./30-性能调优/README.md)'),
    (r'\]\(\./性能调优体系详解\.md\)', '](./30-性能调优/README.md)'),
    (r'\]\(\.\./性能调优体系详解\.md\)', '](./30-性能调优/README.md)'),
    
    # 路径深度问题 (../../03-事务与并发/ → ../03-事务与并发/)
    (r'\]\(\.\.?/\.\.?/03-事务与并发/', '](../03-事务与并发/'),
    (r'\]\(\.\.?/\.\.?/18-版本特性/', '](../18-版本特性/'),
    (r'\]\(\.\.?/\.\.?/02-查询与优化/', '](../02-查询与优化/'),
    (r'\]\(\.\.?/\.\.?/10-AI与机器学习/', '](../10-AI与机器学习/'),
    (r'\]\(\.\.?/\.\.?/12-监控与诊断/', '](../12-监控与诊断/'),
    (r'\]\(\.\.?/\.\.?/30-性能调优/', '](../30-性能调优/'),
    
    # 18-版本特性 下的错误文件名
    (r'05\.03-Azure-AI扩展实战\.md', '18.01-PostgreSQL18新特性/README.md'),
    (r'05\.04-RAG架构实战指南\.md', '18.01-PostgreSQL18新特性/README.md'),
    
    # 1.1.x 格式路径
    (r'22-工具与资源/1\.1\.\d+-[^)]+\.md', '22-工具与资源/README.md'),
    
    # 错误目录名
    (r'\(\.?\.?/?01-理论基础\)', '(./25-理论体系)'),
    (r'\(\.?\.?/?05-实践案例\)', '(./19-实战案例)'),
    (r'\(\.?\.?/?07-实施路径\)', '(./21-最佳实践)'),
    (r'\(\.?\.?/?04-应用场景\)', '(./19-实战案例)'),
    (r'\(\.?\.?/?02-技术架构\)', '(./01-核心基础)'),
    (r'\(\.?\.?/?08-未来趋势\)', '(./ROADMAP-2025.md)'),
    (r'\(\.?\.?/?03-核心能力\)', '(./01-核心基础)'),
    
    # 不存在的目录
    (r'\]\(\./examples/[^)]+\)', '](./README.md)'),
    (r'\]\(\./benchmarks[^)]*\)', '](./README.md)'),
    (r'\]\(\./notebooks[^)]*\)', '](./README.md)'),
    (r'\]\(\./\.github/workflows/[^)]+\)', '](./README.md)'),
    (r'\]\(\./docker-compose\.yml\)', '](./README.md)'),
    (r'\]\(\./分区表管理/[^)]+\)', '](./02-查询与优化/README.md)'),
    
    # program/scripts 路径问题（在 Integrate 下不正确）
    (r'\]\(\./program/scripts/README\.md\)', '](../../program/scripts/README.md)'),
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
    print("最终剩余高频失效链接修复")
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
