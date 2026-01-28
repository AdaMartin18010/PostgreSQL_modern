#!/usr/bin/env python3
"""批量修复常见失效链接模式"""

import re
from pathlib import Path

INTEGRATE = Path("Integrate")

# 路径映射: 旧路径 -> 新路径（相对 Integrate）
PATH_MAPPINGS = [
    # 09-高可用 -> 13-高可用架构
    (r'\.\./09-高可用/高可用体系详解\.md', '../13-高可用架构/高可用体系详解.md'),
    (r'\.\./\.\./09-高可用/高可用体系详解\.md', '../../13-高可用架构/高可用体系详解.md'),
    (r'\.\./09-高可用/流复制详解\.md', '../13-高可用架构/复制与高可用.md'),
    (r'\.\./\.\./09-高可用/流复制详解\.md', '../../13-高可用架构/复制与高可用.md'),
    (r'\.\./09-高可用/逻辑复制详解\.md', '../09-逻辑复制/README.md'),
    (r'\.\./\.\./09-高可用/逻辑复制详解\.md', '../../09-逻辑复制/README.md'),
    (r'\.\./09-高可用/复制与高可用\.md', '../13-高可用架构/复制与高可用.md'),
    (r'\.\./\.\./09-高可用/复制与高可用\.md', '../../13-高可用架构/复制与高可用.md'),
    (r'\.\./09-高可用/', '../13-高可用架构/'),
    (r'\.\./\.\./09-高可用/', '../../13-高可用架构/'),
    
    # 11-性能调优 -> 02-查询与优化/02.06-性能调优 或 30-性能调优
    (r'\.\./11-性能调优/性能调优深入\.md', '../02-查询与优化/02.06-性能调优/性能调优深入.md'),
    (r'\.\./\.\./11-性能调优/性能调优深入\.md', '../../02-查询与优化/02.06-性能调优/性能调优深入.md'),
    (r'\.\./11-性能调优/性能调优体系详解\.md', '../02-查询与优化/02.06-性能调优/性能调优体系详解.md'),
    (r'\.\./\.\./11-性能调优/性能调优体系详解\.md', '../../02-查询与优化/02.06-性能调优/性能调优体系详解.md'),
    (r'\.\./11-性能调优/性能测试与基准测试\.md', '../02-查询与优化/02.06-性能调优/性能测试与基准测试.md'),
    (r'\.\./\.\./11-性能调优/性能测试与基准测试\.md', '../../02-查询与优化/02.06-性能调优/性能测试与基准测试.md'),
    (r'\.\./11-性能调优/', '../30-性能调优/'),
    (r'\.\./\.\./11-性能调优/', '../../30-性能调优/'),
    
    # 04-分布式系统理论 -> 15-分布式系统
    (r'\.\./04-分布式系统理论/04\.02-分布式一致性与CAP-形式化刻画与权衡\.md', '../15-分布式系统/04.02-分布式一致性与CAP-形式化刻画与权衡.md'),
    (r'\.\./\.\./04-分布式系统理论/04\.02-分布式一致性与CAP-形式化刻画与权衡\.md', '../../15-分布式系统/04.02-分布式一致性与CAP-形式化刻画与权衡.md'),
    
    # 05-数据管理 -> 26-数据管理
    (r'\.\./05-数据管理/分区表管理\.md', '../26-数据管理/README.md'),
    (r'\.\./\.\./05-数据管理/分区表管理\.md', '../../26-数据管理/README.md'),
    
    # 13-运维管理 -> 12-监控与诊断 或 27-统计与估计
    (r'\.\./13-运维管理/统计信息管理\.md', '../27-统计与估计/README.md'),
    (r'\.\./\.\./13-运维管理/统计信息管理\.md', '../../27-统计与估计/README.md'),
]

def fix_file(fpath: Path, dry_run: bool = True) -> int:
    try:
        text = fpath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {fpath}: {e}")
        return 0
    
    original = text
    
    for old_pattern, new_path in PATH_MAPPINGS:
        # 匹配 ](../09-高可用/...) 或 ](../../09-高可用/...)
        pattern = r'\]\(' + old_pattern + r'\)'
        text = re.sub(pattern, f']({new_path})', text)
    
    if text != original:
        if not dry_run:
            fpath.write_text(text, encoding="utf-8")
        return 1
    return 0

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="Apply fixes")
    args = ap.parse_args()
    dry_run = not args.fix

    count = 0
    for md in INTEGRATE.rglob("*.md"):
        count += fix_file(md, dry_run=dry_run)
    
    print(f"Files updated: {count} (dry_run={dry_run})")

if __name__ == "__main__":
    main()
