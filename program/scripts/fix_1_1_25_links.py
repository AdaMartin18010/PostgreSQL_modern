#!/usr/bin/env python3
"""批量修复 1.1.25-形式语言与证明-总论 等旧路径链接"""

import re
from pathlib import Path

INTEGRATE = Path("Integrate")
TARGET = "25-理论体系/25.01-形式化方法/01.05-形式语言与证明-总论.md"

def fix_file(fpath: Path, dry_run: bool = True) -> int:
    text = fpath.read_text(encoding="utf-8")
    original = text
    try:
        depth = len(fpath.parent.relative_to(INTEGRATE).parts)
    except ValueError:
        return 0
    prefix = "../" * depth  # ../ 数量 = 从文件所在目录到 Integrate 的层级数

    # 匹配 ](../1.1.25-...) 或 ](../../1.1.25-...) 等，统一替换为 prefix + TARGET
    pat = r'\]\(((?:\.\./)+)1\.1\.25-形式语言与证明-总论\.md\)'
    def repl(m):
        return "](%s%s)" % (prefix, TARGET)
    text = re.sub(pat, repl, text)

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
    print("Files updated: %d (dry_run=%s)" % (count, dry_run))

if __name__ == "__main__":
    main()
