#!/usr/bin/env python3
"""
Analyze link_check_report.md to find top missing targets / patterns.
Outputs:
  - total entries parsed
  - top missing target paths
  - top link URLs (raw markdown url strings)
  - missing prefix counts
  - top source files producing broken links
"""

from __future__ import annotations

from collections import Counter
import re
from pathlib import Path


ROOT = Path(r"E:\_src\PostgreSQL_modern")
REPORT = ROOT / "link_check_report.md"


def main() -> None:
    text = REPORT.read_text(encoding="utf-8", errors="ignore")

    lines = text.splitlines()
    entries: list[dict] = []
    cur: dict = {}

    file_pat = re.compile(r"^- \*\*文件\*\*: `([^`]+)` \(第(\d+)行\)")
    url_pat = re.compile(r"^  - \*\*链接URL\*\*: `([^`]+)`")
    miss_pat = re.compile(r"^  - \*\*问题\*\*: 文件不存在: (.+)$")

    for line in lines:
        m = file_pat.match(line)
        if m:
            if cur.get("file") and cur.get("url") and cur.get("missing"):
                entries.append(cur)
            cur = {"file": m.group(1), "line": int(m.group(2))}
            continue

        m = url_pat.match(line)
        if m:
            cur["url"] = m.group(1)
            continue

        m = miss_pat.match(line)
        if m:
            cur["missing"] = m.group(1)
            continue

    if cur.get("file") and cur.get("url") and cur.get("missing"):
        entries.append(cur)

    print(f"entries={len(entries)}")

    def normalize_missing(miss: str) -> str:
        miss = re.sub(r"^[A-Za-z]:\\\\_src\\\\PostgreSQL_modern\\\\", "", miss)
        return miss.replace("\\\\", "/")

    missing_targets = [normalize_missing(e["missing"]) for e in entries]
    missing_counter = Counter(missing_targets)

    print("\nTOP missing targets:")
    for t, n in missing_counter.most_common(30):
        print(f"{n:5d}  {t}")

    url_counter = Counter(e["url"] for e in entries)
    print("\nTOP link URLs (raw):")
    for t, n in url_counter.most_common(30):
        print(f"{n:5d}  {t}")

    pref = Counter()
    for t, n in missing_counter.items():
        p = t.split("/", 1)[0]
        pref[p] += n
    print("\nMissing prefix counts:")
    for p, n in pref.most_common(30):
        print(f"{n:5d}  {p}")

    src = Counter(e["file"] for e in entries)
    print("\nTop source files:")
    for f, n in src.most_common(30):
        print(f"{n:5d}  {f}")


if __name__ == "__main__":
    main()
