#!/usr/bin/env python3
"""
Fix common broken links under Integrate/26-数据管理.

Main fixes:
1) From files under 26-数据管理/*/*, links like ../25-理论体系/... should often be ../../25-理论体系/...
   because those files are nested 2 levels below Integrate root.
2) Similarly ../02-查询与优化/... -> ../../02-查询与优化/...
3) Map root-level model filenames referenced by ../../数据库数据仓库模型... to the actual files in 数据管理模型/.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(r"E:\_src\PostgreSQL_modern")
BASE = ROOT / "Integrate" / "26-数据管理"


MODEL_MAP = {
    # referenced as ../../数据库数据仓库模型-OLAP查询与多维分析的形式化.md
    "数据库数据仓库模型-OLAP查询与多维分析的形式化.md": "数据管理模型/12.02-数据库数据仓库模型-OLAP查询与多维分析的形式化.md",
    "数据库数据集成模型-ETL流程与数据转换的形式化.md": "数据管理模型/12.01-数据库数据集成模型-ETL流程与数据转换的形式化.md",
}


def fix_one_file(p: Path) -> int:
    s = p.read_text(encoding="utf-8", errors="ignore")
    orig = s
    n = 0

    rel = p.relative_to(BASE)
    depth = len(rel.parts) - 1  # directories below BASE

    # For nested folders (depth>=1), many links used ../ but actually need ../../ to reach Integrate root.
    if depth >= 1:
        # ../25-理论体系 -> ../../25-理论体系
        s2, k = re.subn(r"\]\(\.\./25-理论体系/", "](../../25-理论体系/", s)
        if k:
            n += k
            s = s2

        # ../02-查询与优化 -> ../../02-查询与优化
        s2, k = re.subn(r"\]\(\.\./02-查询与优化/", "](../../02-查询与优化/", s)
        if k:
            n += k
            s = s2

        # ../30-性能调优 -> ../../30-性能调优
        s2, k = re.subn(r"\]\(\.\./30-性能调优/", "](../../30-性能调优/", s)
        if k:
            n += k
            s = s2

    # Replace ../../数据库XXX.md -> ../数据管理模型/12.xx-...
    for old_name, new_rel in MODEL_MAP.items():
        # from subfolders like 数据仓库/*.md: ../../<name> should be ../数据管理模型/<file>
        s2, k = re.subn(
            rf"\]\(\.\./\.\./{re.escape(old_name)}\)",
            f"](../{new_rel})",
            s,
        )
        if k:
            n += k
            s = s2

    if s != orig:
        p.write_text(s, encoding="utf-8")
    return n


def main() -> None:
    if not BASE.exists():
        raise SystemExit(f"Missing dir: {BASE}")

    total_files = 0
    total_changes = 0
    for p in BASE.rglob("*.md"):
        total_files += 1
        c = fix_one_file(p)
        if c:
            total_changes += c
            print(f"✅ {c:4d}  {p.relative_to(ROOT)}")

    print(f"\nfiles_scanned={total_files} changes={total_changes}")


if __name__ == "__main__":
    main()

