#!/usr/bin/env python3
"""
修复重复目录路径和其他高频失效链接模式。
"""

import os
import re
from pathlib import Path

ROOT = Path(r'E:\_src\PostgreSQL_modern')
INTEGRATE_ROOT = ROOT / 'Integrate'

# 重复目录路径修复
DUPLICATE_DIR_PATTERNS = [
    # 12-监控与诊断/12-监控与诊断/ → 12-监控与诊断/
    (r'12-监控与诊断/12-监控与诊断/', '12-监控与诊断/'),
    (r'30-性能调优/30-性能调优/', '30-性能调优/'),
    (r'01-核心基础/01-核心基础/', '01-核心基础/'),
    # 13-高可用架构/监控与诊断/12-监控与诊断/ → 12-监控与诊断/
    (r'13-高可用架构/监控与诊断/12-监控与诊断/', '12-监控与诊断/'),
    (r'13-高可用架构/监控与诊断/30-性能调优/', '30-性能调优/'),
]

# 文件名修复
FILE_NAME_FIXES = [
    # 向量数据库相关
    (r'07-多模型数据库/向量数据库/向量数据库-RAG集成\.md', '07-多模型数据库/README.md'),
    (r'07-多模型数据库/向量数据库/README\.md', '07-多模型数据库/README.md'),
    
    # 根级别文件映射到正确路径
    (r'Integrate/pgvector完整深化指南\.md', 'Integrate/10-AI与机器学习/README.md'),
    (r'Integrate/【深入】TimescaleDB时序数据库完整指南\.md', 'Integrate/08-流处理与时序/README.md'),
    (r'Integrate/性能调优深入\.md', 'Integrate/30-性能调优/README.md'),
    (r'Integrate/查询计划与优化器\.md', 'Integrate/02-查询与优化/02.01-查询优化器/02.01-查询优化器原理.md'),
    (r'Integrate/备份与恢复\.md', 'Integrate/04-存储与恢复/备份与恢复.md'),
    (r'Integrate/监控与诊断\.md', 'Integrate/12-监控与诊断/06.01-监控与诊断.md'),
    (r'Integrate/连接池管理\.md', 'Integrate/30-性能调优/README.md'),
    (r'Integrate/P2-项目完成总结\.md', 'Integrate/README.md'),
    (r'Integrate/1\.1\.8-MVCC高级分析与形式证明\.md', 'Integrate/25-理论体系/25.01-形式化方法/01.04-MVCC形式化验证.md'),
    
    # 14-云原生与容器化
    (r'14-云原生与容器化/Kubernetes-高可用-PostgreSQL-完整指南\.md', '14-云原生与容器化/05.13-Kubernetes部署.md'),
    
    # 25-理论体系
    (r'25-理论体系/CAP理论/CAP与分布式系统设计-形式化刻画与权衡\.md', '25-理论体系/CAP理论/CAP与分布式系统设计.md'),
    
    # 18-版本特性
    (r'18-版本特性/05\.03-Azure-AI扩展实战\.md', '10-AI与机器学习/README.md'),
    (r'18-版本特性/05\.04-RAG架构实战指南\.md', '07-多模型数据库/README.md'),
    
    # 08-流处理与时序
    (r'08-流处理与时序/1\.1\.29-流处理与时间语义', '08-流处理与时序/README.md'),
    
    # feature_bench, scripts, tools, sql, config 目录（不存在）
    (r'Integrate/feature_bench/', 'Integrate/18-版本特性/18.01-PostgreSQL18新特性/'),
    (r'Integrate/scripts/', 'program/scripts/'),
    (r'Integrate/tools/', 'program/scripts/'),
    (r'Integrate/sql/', 'program/configs/'),
    (r'Integrate/config/', 'program/configs/'),
]


def fix_file(filepath: Path) -> int:
    """修复单个文件中的链接"""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  ⚠️ 无法读取: {filepath} - {e}")
        return 0
    
    original = content
    changes = 0
    
    # 1. 修复重复目录路径
    for pattern, replacement in DUPLICATE_DIR_PATTERNS:
        new_content, n = re.subn(pattern, replacement, content)
        if n > 0:
            changes += n
            content = new_content
    
    # 2. 修复文件名
    for pattern, replacement in FILE_NAME_FIXES:
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
            print(f"  ❌ 写入失败: {filepath} - {e}")
            return 0
    
    return 0


def main():
    print("=" * 60)
    print("重复目录路径和高频失效模式修复")
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
    
    # 根目录 Markdown 文件
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
