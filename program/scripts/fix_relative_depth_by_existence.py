#!/usr/bin/env python3
"""
Fix broken relative links by adjusting ../ depth based on existence.

Targets common patterns where links accidentally go one level too high
and resolve outside Integrate, e.g. ../../../18-版本特性/... from a file
that is only two levels deep.

Strategy:
- Parse markdown links [text](url)
- For internal relative urls starting with ../
  - Strip anchors
  - Compute resolved path against file's parent
  - If missing, try alternative urls by reducing or increasing the number
    of leading ../ (within a small window) and keep the first that exists.
- Only apply changes when an alternative target exists on disk.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(r"E:\_src\PostgreSQL_modern").resolve()
SCAN_ROOT = ROOT / "Integrate"

# limit how many ../ adjustments we try around current depth
MAX_UP = 6


MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def is_internal(url: str) -> bool:
    u = url.strip()
    if u.startswith("<") and u.endswith(">"):
        u = u[1:-1]
    if u.startswith("http://") or u.startswith("https://") or u.startswith("mailto:"):
        return False
    return u.startswith("#") or u.startswith("./") or u.startswith("../") or u.startswith("/")


def split_anchor(url: str) -> tuple[str, str]:
    if "#" in url:
        base, anchor = url.split("#", 1)
        return base, "#" + anchor
    return url, ""


def exists_target(file_dir: Path, url_path: str) -> bool:
    # Normalize ./ prefix
    u = url_path
    if u.startswith("./"):
        u = u[2:]
    # Treat directories as valid if dir exists or README exists
    p = (file_dir / u).resolve()
    if p.exists():
        return True
    if p.is_dir():
        return True
    if (p / "README.md").exists():
        return True
    return False


def adjust_up_prefix(url_base: str, new_up: int) -> str | None:
    # url_base expected to start with some ../ segments
    parts = url_base.split("/")
    # count current leading ..
    cur = 0
    for part in parts:
        if part == "..":
            cur += 1
        else:
            break
    rest = "/".join(parts[cur:])
    if rest == "":
        return None
    return "../" * new_up + rest


def fix_file(p: Path) -> int:
    text = p.read_text(encoding="utf-8", errors="ignore")
    changed = 0

    file_dir = p.parent.resolve()

    def repl(m: re.Match) -> str:
        nonlocal changed
        label = m.group(1)
        url = m.group(2).strip()

        # keep original parentheses content if not internal
        if not is_internal(url):
            return m.group(0)

        # ignore pure anchors
        if url.startswith("#"):
            return m.group(0)

        # only operate on ../-prefixed urls
        if not url.startswith("../"):
            return m.group(0)

        base, anchor = split_anchor(url)
        # quick existence check
        if exists_target(file_dir, base):
            return m.group(0)

        # count current up
        parts = base.split("/")
        cur_up = 0
        for part in parts:
            if part == "..":
                cur_up += 1
            else:
                break

        # Try nearby depths (prefer fewer .. first, then more)
        candidates = []
        for up in range(max(0, cur_up - 3), min(MAX_UP, cur_up + 3) + 1):
            if up == cur_up:
                continue
            cand = adjust_up_prefix(base, up)
            if cand:
                candidates.append(cand)

        # Prefer candidates that keep us inside Integrate (heuristic: try smaller up first)
        candidates.sort(key=lambda c: c.count(".."))

        for cand in candidates:
            if exists_target(file_dir, cand):
                new_url = cand + anchor
                changed += 1
                return f"[{label}]({new_url})"

        return m.group(0)

    new_text = MD_LINK_RE.sub(repl, text)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
    return changed


def main() -> None:
    total_files = 0
    total_changes = 0
    for p in SCAN_ROOT.rglob("*.md"):
        total_files += 1
        c = fix_file(p)
        if c:
            total_changes += c
            print(f"✅ {c:4d}  {p.relative_to(ROOT)}")
    print(f"\nfiles_scanned={total_files} changes={total_changes}")


if __name__ == "__main__":
    main()
