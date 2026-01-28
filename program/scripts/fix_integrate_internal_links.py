#!/usr/bin/env python3
"""
批量修复 Integrate 目录内部的失效链接。
处理模式：
1. ../../04-存储与恢复/01.06-存储管理与数据持久化.md → ../04-存储与恢复/01.06-存储管理与数据持久化.md
2. ../../01-理论基础/... → ../25-理论体系/... 
3. 备份恢复完整实战.md → 备份恢复体系详解.md
4. 监控与可观测性完整体系指南.md → PostgreSQL可观测性完整指南.md
5. ../docs/... → 正确的 Integrate 路径
"""

import os
import re
from pathlib import Path

# 项目根目录
INTEGRATE_ROOT = Path(r'E:\_src\PostgreSQL_modern\Integrate')

# 链接映射规则 (old_pattern, replacement)
# 顺序很重要：更具体的规则放在前面
MAPPINGS = [
    # 1. 修复 ../../04-存储与恢复/01.06-... 路径深度问题
    (r'\.\./\.\./04-存储与恢复/01\.06-存储管理与数据持久化\.md', '../04-存储与恢复/01.06-存储管理与数据持久化.md'),
    (r'\.\./\.\./\.\./04-存储与恢复/01\.06-存储管理与数据持久化\.md', '../../04-存储与恢复/01.06-存储管理与数据持久化.md'),
    
    # 2. 修复 ../../01-理论基础/... → ../25-理论体系/...
    (r'\.\./\.\./01-理论基础/形式化证明/MVCC可见性定理证明\.md', '../25-理论体系/形式化证明/MVCC可见性定理证明.md'),
    (r'\.\./\.\./01-理论基础/公理系统/MVCC核心公理\.md', '../25-理论体系/公理系统/MVCC核心公理.md'),
    (r'\.\./\.\./01-理论基础/公理系统/ACID公理系统\.md', '../25-理论体系/公理系统/ACID公理系统.md'),
    (r'\.\./\.\./01-理论基础/形式化证明/ACID属性定理证明\.md', '../25-理论体系/形式化证明/ACID属性定理证明.md'),
    (r'\.\./\.\./01-理论基础/CAP理论/CAP定理完整定义与证明\.md', '../25-理论体系/CAP理论/CAP定理完整定义与证明.md'),
    (r'\.\./\.\./01-理论基础/CAP理论/CAP权衡决策框架\.md', '../25-理论体系/CAP理论/CAP权衡决策框架.md'),
    (r'\.\./\.\./01-理论基础/CAP理论/BASE理论详解\.md', '../25-理论体系/CAP理论/CAP定理的批判性分析.md'),  # 映射到相近文档
    (r'\.\./\.\./01-理论基础/CAP理论/CAP理论的历史演进\.md', '../25-理论体系/CAP理论/CAP理论的历史演进.md'),
    (r'\.\./\.\./01-理论基础/CAP理论/一致性模型详解\.md', '../25-理论体系/CAP理论/CAP与分布式系统设计.md'),  # 映射到相近文档
    (r'\.\./\.\./01-理论基础/PostgreSQL版本特性/pg17-logical-replication\.md', '../25-理论体系/PostgreSQL版本特性/README.md'),
    (r'\.\./\.\./01-理论基础/PostgreSQL版本特性/pg18-aio\.md', '../25-理论体系/PostgreSQL版本特性/README.md'),
    
    # 3. 修复文件名不匹配
    (r'04-存储与恢复/备份恢复完整实战\.md', '04-存储与恢复/备份恢复体系详解.md'),
    (r'12-监控与诊断/监控与可观测性完整体系指南\.md', '12-监控与诊断/PostgreSQL可观测性完整指南.md'),
    (r'18-版本特性/18\.01-PostgreSQL18新特性/22-监控与可观测性完整体系指南\.md', '12-监控与诊断/PostgreSQL可观测性完整指南.md'),
    
    # 4. 修复 ../docs/... 路径 (archive 目录下的文件引用)
    (r'\.\./docs/01-PostgreSQL18/40-PostgreSQL18新特性总结\.md', '../Integrate/18-版本特性/18.01-PostgreSQL18新特性/README.md'),
    (r'\.\./docs/01-PostgreSQL18/08-性能调优实战指南\.md', '../Integrate/30-性能调优/README.md'),
    (r'\.\./docs/05-Production/20-生产环境检查清单\.md', '../Integrate/21-最佳实践/README.md'),
    (r'\.\./docs/05-Production/06-Kubernetes生产部署完整指南\.md', '../Integrate/14-云原生与容器化/Kubernetes-高可用-PostgreSQL-完整指南.md'),
    (r'\.\./docs/01-PostgreSQL18/11-VACUUM增强与积极冻结策略完整指南\.md', '../Integrate/18-版本特性/18.01-PostgreSQL18新特性/11-VACUUM增强与积极冻结策略完整指南.md'),
]


def fix_file(filepath: Path) -> int:
    """修复单个文件中的链接，返回修复数量"""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  ⚠️ 无法读取: {filepath} - {e}")
        return 0
    
    original = content
    changes = 0
    
    for pattern, replacement in MAPPINGS:
        # 匹配 Markdown 链接格式 [text](url) 或 [text](url#anchor)
        def replacer(m):
            nonlocal changes
            full = m.group(0)
            new_url = re.sub(pattern, replacement, m.group(1))
            if new_url != m.group(1):
                changes += 1
                return full.replace(m.group(1), new_url)
            return full
        
        # 匹配 (url) 或 (url#anchor) 格式
        content = re.sub(r'\(([^)]+)\)', replacer, content)
    
    if content != original:
        try:
            filepath.write_text(content, encoding='utf-8')
            print(f"  ✅ 修复 {changes} 处: {filepath.relative_to(INTEGRATE_ROOT.parent)}")
            return changes
        except Exception as e:
            print(f"  ❌ 写入失败: {filepath} - {e}")
            return 0
    
    return 0


def main():
    print("=" * 60)
    print("Integrate 目录内部链接批量修复")
    print("=" * 60)
    
    # 扫描所有 Markdown 文件
    all_files = list(INTEGRATE_ROOT.rglob('*.md'))
    
    # 也处理 archive 目录
    archive_root = INTEGRATE_ROOT.parent / 'archive'
    if archive_root.exists():
        all_files.extend(archive_root.rglob('*.md'))
    
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
