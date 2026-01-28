#!/usr/bin/env python3
"""修复具体的失效链接路径"""

import re
from pathlib import Path

INTEGRATE = Path("Integrate")

# 具体路径修复映射: (旧路径模式, 新路径)
SPECIFIC_FIXES = [
    # PostgreSQL-18-自动化运维与自我监测完整指南
    (
        r'\.\./30-性能调优/PostgreSQL-18-自动化运维与自我监测完整指南\.md',
        '../30-性能调优/PostgreSQL-18-自动化运维与自我监测/README.md'
    ),
    (
        r'\.\./\.\./30-性能调优/PostgreSQL-18-自动化运维与自我监测完整指南\.md',
        '../../30-性能调优/PostgreSQL-18-自动化运维与自我监测/README.md'
    ),
    
    # 13-高可用架构/备份与恢复路径
    (
        r'\.\./\.\./13-高可用架构/备份与恢复/06\.06-备份与恢复\.md',
        '../13-高可用架构/备份与恢复/06.06-备份与恢复.md'
    ),
    (
        r'\.\./13-高可用架构/备份与恢复/06\.06-备份与恢复\.md',
        '../13-高可用架构/备份与恢复/06.06-备份与恢复.md'
    ),
    (
        r'\.\./\.\./13-高可用架构/备份与恢复/06\.07-增量备份与恢复\.md',
        '../13-高可用架构/备份与恢复/06.07-增量备份与恢复.md'
    ),
    
    # 11-部署架构/单机部署路径
    (
        r'\.\./\.\./11-部署架构/单机部署/05\.02-性能调优实践\.md',
        '../11-部署架构/单机部署/05.02-性能调优实践.md'
    ),
    
    # 16-应用设计与开发/行业案例路径
    (
        r'\.\./\.\./16-应用设计与开发/行业案例/时序监控\.md',
        '../16-应用设计与开发/行业案例/时序监控.md'
    ),
    
    # 02-查询与优化/02.03-统计信息 -> 02.04-统计信息
    (
        r'\.\./02-查询与优化/02\.03-统计信息/README\.md',
        '../27-统计与估计/README.md'
    ),
    (
        r'\.\./\.\./02-查询与优化/02\.03-统计信息/README\.md',
        '../../27-统计与估计/README.md'
    ),
]

def fix_file(fpath: Path, dry_run: bool = True) -> int:
    try:
        text = fpath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {fpath}: {e}")
        return 0
    
    original = text
    
    for old_pattern, new_path in SPECIFIC_FIXES:
        # 匹配 ](../path) 格式
        pattern = r'\]\(' + old_pattern + r'\)'
        text = re.sub(pattern, f']({new_path})', text)
    
    if text != original:
        if not dry_run:
            fpath.write_text(text, encoding="utf-8")
            print(f"Fixed: {fpath}")
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
