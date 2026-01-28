#!/usr/bin/env python3
"""
修复所有剩余的高频失效链接模式。
"""

import os
import re
from pathlib import Path

ROOT = Path(r'E:\_src\PostgreSQL_modern')
INTEGRATE_ROOT = ROOT / 'Integrate'

# 所有修复模式
PATTERNS = [
    # ====================
    # 重复目录路径
    # ====================
    (r'12-监控与诊断/12-监控与诊断/', '12-监控与诊断/'),
    (r'12-监控与诊断/30-性能调优/', '30-性能调优/'),
    (r'30-性能调优/12-监控与诊断/', '12-监控与诊断/'),
    (r'30-性能调优/11-部署架构/', '11-部署架构/'),
    (r'30-性能调优/PostgreSQL-18-自动化运维与自我监测/PostgreSQL性能调优完整指南\.md', '30-性能调优/README.md'),
    (r'13-高可用架构/监控与诊断/12-监控与诊断/', '12-监控与诊断/'),
    (r'13-高可用架构/监控与诊断/30-性能调优/', '30-性能调优/'),
    (r'01-核心基础/01-核心基础/', '01-核心基础/'),
    
    # ====================
    # 1.1.x 格式路径
    # ====================
    (r'22-工具与资源/1\.1\.4-查询优化\.md', '02-查询与优化/README.md'),
    (r'22-工具与资源/1\.1\.\d+-[^/]+\.md', '02-查询与优化/README.md'),
    (r'08-流处理与时序/1\.1\.29-[^/]+\.md', '08-流处理与时序/README.md'),
    
    # ====================
    # 34-模型与建模 子路径
    # ====================
    (r'34-模型与建模/03-建模方法论/成本收益分析\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/04-OLTP建模/PostgreSQL实现\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/09-建模模式与反模式/[^/]+\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/10-综合应用案例/[^/]+\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/11-时序数据建模/[^/]+\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/18-版本特性/[^/]+/[^/]+\.md', '18-版本特性/README.md'),
    (r'34-模型与建模/other/path/to/doc\.md', '34-模型与建模/README.md'),
    
    # ====================
    # 99-归档 子路径
    # ====================
    (r'99-归档/参考资源/books/[^)]+\.md', '34-模型与建模/README.md'),
    
    # ====================
    # 18-版本特性 子路径
    # ====================
    (r'18-版本特性/05\.03-Azure-AI扩展实战\.md', '10-AI与机器学习/README.md'),
    (r'18-版本特性/05\.04-RAG架构实战指南\.md', '07-多模型数据库/README.md'),
    
    # ====================
    # 目录名错误
    # ====================
    (r'\]\\(\\.\\.?/\\)?01-理论基础(?!/)', '](../25-理论体系'),
    (r'\]\\(\\.\\.?/\\)?05-实践案例(?!/)', '](../19-实战案例'),
    (r'\]\\(\\.\\.?/\\)?07-实施路径(?!/)', '](../21-最佳实践'),
    (r'\]\\(\\.\\.?/\\)?04-应用场景(?!/)', '](../19-实战案例'),
    (r'\]\\(\\.\\.?/\\)?02-技术架构(?!/)', '](../01-核心基础'),
    (r'\]\\(\\.\\.?/\\)?08-未来趋势(?!/)', '](../ROADMAP-2025.md'),
    (r'\]\\(\\.\\.?/\\)?03-核心能力(?!/)', '](../01-核心基础'),
    
    # ====================
    # 26-数据管理 子路径
    # ====================
    (r'26-数据管理/数据库数据治理模型-治理策略与合规性检查的形式化\.md', '26-数据管理/README.md'),
    
    # ====================
    # 22-工具与资源 .py 文件
    # ====================
    (r'22-工具与资源/\d+-[^/]+\.py', 'program/scripts/README.md'),
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
    print("全模式高频失效链接修复")
    print("=" * 60)
    
    # 扫描所有 Markdown 文件
    all_files = list(INTEGRATE_ROOT.rglob('*.md'))
    
    # 也处理 archive 目录、program 目录和根目录
    archive_root = ROOT / 'archive'
    program_root = ROOT / 'program'
    if archive_root.exists():
        all_files.extend(archive_root.rglob('*.md'))
    if program_root.exists():
        all_files.extend(program_root.rglob('*.md'))
    
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
