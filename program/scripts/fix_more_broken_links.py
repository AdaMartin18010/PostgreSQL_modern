#!/usr/bin/env python3
"""
修复更多高频失效链接模式。
"""

import os
import re
from pathlib import Path

ROOT = Path(r'E:\_src\PostgreSQL_modern')
INTEGRATE_ROOT = ROOT / 'Integrate'

# 高频失效链接模式映射
MAPPINGS = [
    # 1.1.x 格式的旧路径
    (r'08-流处理与时序/1\.1\.29-', '08-流处理与时序/10.01-'),
    (r'1\.1\.31-分布式一致性与CAP', '25-理论体系/CAP理论/CAP与分布式系统设计'),
    (r'22-工具与资源/1\.1\.4-查询优化\.md', '02-查询与优化/02.01-查询优化器/02.01-查询优化器原理.md'),
    (r'22-工具与资源/1\.1\.80-', '02-查询与优化/02.06-性能调优/'),
    (r'22-工具与资源/1\.1\.59-', '02-查询与优化/02.06-性能调优/'),
    (r'22-工具与资源/1\.1\.60-', '02-查询与优化/02.06-性能调优/'),
    (r'22-工具与资源/1\.1\.49-', '27-统计与估计/'),
    (r'22-工具与资源/1\.1\.83-', '02-查询与优化/02.06-性能调优/'),
    
    # 目录名错误
    (r'01-理论基础(?!/)', '25-理论体系'),
    (r'05-实践案例(?!/)', '19-实战案例'),
    (r'07-实施路径(?!/)', '21-最佳实践'),
    (r'04-应用场景(?!/)', '19-实战案例'),
    (r'02-技术架构(?!/)', '01-核心基础'),
    (r'08-未来趋势(?!/)', 'ROADMAP-2025.md'),
    (r'03-核心能力(?!/)', '01-核心基础'),
    (r'15-体系总览/事务管理详解\.md', '03-事务与并发/03.02-ACID特性/01.04-事务管理与ACID特性.md'),
    
    # 子路径修复 - 30-性能调优
    (r'30-性能调优/12-监控与诊断/监控与诊断深度应用指南\.md', '12-监控与诊断/06.01-监控与诊断.md'),
    (r'30-性能调优/12-监控与诊断/PostgreSQL可观测性完整指南\.md', '12-监控与诊断/PostgreSQL可观测性完整指南.md'),
    (r'30-性能调优/11-部署架构/04\.01-单机部署与配置\.md', '11-部署架构/04.01-单机部署与配置.md'),
    (r'30-性能调优/PostgreSQL-18-自动化运维与自我监测/PostgreSQL性能调优完整指南\.md', '30-性能调优/README.md'),
    
    # 子路径修复 - 34-模型与建模
    (r'34-模型与建模/03-建模方法论/成本收益分析\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/04-OLTP建模/PostgreSQL实现\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/09-建模模式与反模式/反模式识别\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/09-建模模式与反模式/最佳实践\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/10-综合应用案例/推荐系统数据模型案例\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/10-综合应用案例/RAG应用数据模型案例\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/11-时序数据建模/时序数据建模完整指南\.md', '34-模型与建模/README.md'),
    (r'34-模型与建模/18-版本特性/18\.01-PostgreSQL18新特性/多租户增强\.md', '18-版本特性/18.01-PostgreSQL18新特性/README.md'),
    (r'34-模型与建模/other/path/to/doc\.md', '34-模型与建模/README.md'),
    
    # 文件名错误
    (r'07-多模型数据库/RAG系统完整实现\.md', '07-多模型数据库/向量数据库/向量数据库-RAG集成.md'),
    (r'06\.02-监控与诊断落地指南\.md', '12-监控与诊断/06.01-监控与诊断.md'),
    (r'06\.03-性能调优变更闭环\.md', '30-性能调优/README.md'),
    (r'12-监控与诊断/Prometheus监控配置\.md', '12-监控与诊断/README.md'),
    (r'11-部署架构/Kubernetes部署实战\.md', '14-云原生与容器化/Kubernetes-高可用-PostgreSQL-完整指南.md'),
    (r'09-逻辑复制/实时数据同步与CDC完整指南\.md', '09-逻辑复制/README.md'),
    (r'05\.05-向量检索性能调优指南\.md', '07-多模型数据库/向量数据库/README.md'),
    (r'PostgreSQL-18-自动化运维与自我监测完整指南\.md', '12-监控与诊断/README.md'),
    
    # 25-理论体系子目录
    (r'25-理论体系/25\.02-分布式理论/06\.06-分布式一致性理论\.md', '25-理论体系/CAP理论/CAP与分布式系统设计.md'),
    (r'25-理论体系/PostgreSQL版本特性/README\.md', '18-版本特性/README.md'),
    
    # 07-安全
    (r'07-安全/【深入】PostgreSQL安全深化-RLS与审计完整指南\.md', '05-安全与合规/README.md'),
    
    # 18-版本特性子目录
    (r'18-版本特性/05\.03-Azure-AI扩展实战\.md', '10-AI与机器学习/README.md'),
    (r'18-版本特性/05\.04-RAG架构实战指南\.md', '07-多模型数据库/向量数据库/向量数据库-RAG集成.md'),
    
    # en-US 多语言目录（不存在）
    (r'en-US/01-core-fundamentals/01\.01-system-architecture\.md', '01-核心基础/01.02-系统架构/01.01-系统架构与设计原理.md'),
    (r'01\.01-系统架构\.md', '01-核心基础/01.02-系统架构/01.01-系统架构与设计原理.md'),
    
    # Sql 目录
    (r'Sql/05-高级特性/05\.05-时态数据处理\.md', '08-流处理与时序/README.md'),
    
    # 22-工具脚本（老路径）
    (r'22-工具脚本/', '22-工具与资源/'),
    
    # 26-数据管理
    (r'26-数据管理/12\.09-', '26-数据管理/'),
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
    
    for pattern, replacement in MAPPINGS:
        # 仅替换链接 URL 部分
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
    print("高频失效链接模式批量修复")
    print("=" * 60)
    
    # 扫描所有 Markdown 文件
    all_files = list(INTEGRATE_ROOT.rglob('*.md'))
    
    # 也处理 archive 目录和根目录
    archive_root = ROOT / 'archive'
    if archive_root.exists():
        all_files.extend(archive_root.rglob('*.md'))
    
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
