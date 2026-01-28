#!/usr/bin/env python3
"""修复路径层级错误（../../ 应该是 ../）"""

import re
from pathlib import Path

INTEGRATE = Path("Integrate")

# 路径修正映射: 错误路径 -> 正确路径
PATH_FIXES = [
    # 从 Integrate/XX-xxx/ 目录，应该用 ../ 而不是 ../../
    (r'\.\./\.\./13-高可用架构/', '../13-高可用架构/'),
    (r'\.\./\.\./30-性能调优/', '../30-性能调优/'),
    (r'\.\./\.\./02-查询与优化/', '../02-查询与优化/'),
    (r'\.\./\.\./11-部署架构/', '../11-部署架构/'),
    (r'\.\./\.\./16-应用设计与开发/', '../16-应用设计与开发/'),
    (r'\.\./\.\./27-统计与估计/', '../27-统计与估计/'),
    (r'\.\./\.\./26-数据管理/', '../26-数据管理/'),
    (r'\.\./\.\./15-分布式系统/', '../15-分布式系统/'),
    (r'\.\./\.\./09-逻辑复制/', '../09-逻辑复制/'),
    (r'\.\./\.\./12-监控与诊断/', '../12-监控与诊断/'),
    (r'\.\./\.\./25-理论体系/', '../25-理论体系/'),
]

def fix_file(fpath: Path, dry_run: bool = True) -> int:
    try:
        text = fpath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {fpath}: {e}")
        return 0
    
    original = text
    
    # 检查文件是否在 Integrate/XX-xxx/ 层级（深度2）
    parts = fpath.parts
    if len(parts) >= 3 and parts[0] == "Integrate" and parts[1].startswith(("0", "1", "2", "3")):
        # 在 Integrate/XX-xxx/ 层级，应该用 ../ 而不是 ../../
        for old_pattern, new_path in PATH_FIXES:
            pattern = r'\]\(' + old_pattern
            text = re.sub(pattern, f']({new_path}', text)
    
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
