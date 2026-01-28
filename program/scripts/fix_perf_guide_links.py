#!/usr/bin/env python3
"""
Fix broken links inside Integrate/30-性能调优/PostgreSQL-18-自动化运维与自我监测.

Fixes:
1) ../PostgreSQL性能调优完整指南.md -> ../../PostgreSQL性能调优完整指南.md
2) ./19-实战案例案例.md -> ./04-应用场景案例.md (within 06-综合方案)
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(r"E:\_src\PostgreSQL_modern")
BASE = ROOT / "Integrate" / "30-性能调优" / "PostgreSQL-18-自动化运维与自我监测"


def fix_one(p: Path) -> int:
    s = p.read_text(encoding="utf-8", errors="ignore")
    orig = s
    n = 0

    s2, k = re.subn(r"\]\(\.\./PostgreSQL性能调优完整指南\.md\)", "](../../PostgreSQL性能调优完整指南.md)", s)
    if k:
        n += k
        s = s2

    s2, k = re.subn(r"\]\(\./19-实战案例案例\.md\)", "](./04-应用场景案例.md)", s)
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
        c = fix_one(p)
        if c:
            total_changes += c
            print(f"✅ {c:4d}  {p.relative_to(ROOT)}")

    print(f"\nfiles_scanned={total_files} changes={total_changes}")


if __name__ == "__main__":
    main()

