#!/usr/bin/env python3
"""修复 Integrate/XX/ 下 ../../25-理论体系 应改为 ../25-理论体系 的链接"""

import re
from pathlib import Path

INTEGRATE = Path("Integrate")

def fix_file(fpath: Path, dry_run: bool = True) -> int:
    try:
        rel = fpath.relative_to(INTEGRATE)
    except ValueError:
        return 0
    # 仅处理 Integrate/XX/yyy.md（一层子目录）
    if len(rel.parts) != 2:
        return 0
    text = fpath.read_text(encoding="utf-8")
    original = text
    # ../../25-理论体系 -> ../25-理论体系
    text = re.sub(
        r'\]\(\.\./\.\./(25-理论体系/[^)]+)\)',
        r'](../\1)',
        text
    )
    if text != original:
        if not dry_run:
            fpath.write_text(text, encoding="utf-8")
        return 1
    return 0

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()
    dry_run = not args.fix
    n = sum(fix_file(md, dry_run) for md in INTEGRATE.rglob("*.md"))
    print("Files updated: %d (dry_run=%s)" % (n, dry_run))

if __name__ == "__main__":
    main()
