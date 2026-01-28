#!/usr/bin/env python3
"""
Fix remaining broken link patterns (A-/B- prefixes, legacy folders, missing stubs).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"E:\_src\PostgreSQL_modern")


RULES: list[tuple[re.Pattern, str]] = [
    # A-核心基础/* -> ../* (used inside 01-核心基础/01.01-历史与发展 docs)
    (re.compile(r"\]\(A-核心基础/01\.02-系统架构/"), "](../01.02-系统架构/"),
    (re.compile(r"\]\(A-核心基础/01\.03-数据模型/"), "](../01.03-数据模型/"),
    (re.compile(r"\]\(A-核心基础/01\.04-SQL语言/"), "](../01.04-SQL语言/"),

    # B-查询与优化/* -> ../* (used inside 02-查询与优化 docs)
    (re.compile(r"\]\(B-查询与优化/02\.01-查询优化器/"), "](../02.01-查询优化器/"),
    (re.compile(r"\]\(B-查询与优化/02\.02-索引结构/"), "](../02.02-索引结构/"),
    (re.compile(r"\]\(B-查询与优化/02\.03-执行计划/"), "](../02.03-执行计划/"),
    (re.compile(r"\]\(B-查询与优化/02\.04-统计信息/"), "](../02.04-统计信息/"),

    # Legacy folders
    (re.compile(r"\]\(\.\./01-理论基础/"), "](../25-理论体系/"),
    (re.compile(r"\]\(\.\./05-实践案例/"), "](../19-实战案例/"),
    (re.compile(r"\]\(\.\./08-未来趋势/"), "](../../ROADMAP-2025.md)"),

    # Missing planning docs
    (re.compile(r"\]\(\.\./\.\./06-后续规划/[^)]+\)"), "](../../ROADMAP-2025.md)"),

    # Missing scenario practice folder
    (re.compile(r"\]\(\.\./\.\./03-场景实践/"), "](../../03-事务与并发/03.07-场景实践/"),

    # Missing code folder stub
    (re.compile(r"\]\(\.\./\.\./code/[^)]+\)"), "](../../program/scripts/README.md)"),
    (re.compile(r"\]\(\.\./\.\./code/\)"), "](../../program/scripts/README.md)"),

    # Compliance folder rename
    (re.compile(r"/05-合规与可信/"), "/05-安全与合规/"),

    # High availability monitor duplicate path
    (re.compile(r"13-高可用架构/监控与诊断/12-监控与诊断/"), "12-监控与诊断/"),

    # Benchmarks/examples stubs under Integrate -> point to program scripts
    (re.compile(r"\]\(\.\./benchmarks/\)"), "](../../program/scripts/README.md)"),
    (re.compile(r"\]\(\.\./examples/[^)]+\)"), "](../../program/scripts/README.md)"),
    (re.compile(r"\]\(\.\./examples/\)"), "](../../program/scripts/README.md)"),

    # Missing expansion variant -> base doc
    (re.compile(r"\]\(1\.1\.15-云原生与容器化部署-扩充版\.md\)"), "](1.1.15-云原生与容器化部署.md)"),

    # PostgreSQL_View folder stub -> Integrate README
    (re.compile(r"\]\(\.\./PostgreSQL_View/[^)]+\)"), "](../README.md)"),
]


def fix_file(p: Path) -> int:
    s = p.read_text(encoding="utf-8", errors="ignore")
    orig = s
    changed = 0
    for pat, rep in RULES:
        s2, n = pat.subn(rep, s)
        if n:
            changed += n
            s = s2
    if s != orig:
        p.write_text(s, encoding="utf-8")
    return changed


def main() -> None:
    targets = []
    targets.extend((ROOT / "Integrate").rglob("*.md"))
    targets.extend((ROOT / "archive").rglob("*.md") if (ROOT / "archive").exists() else [])

    total = 0
    files = 0
    for p in targets:
        c = fix_file(p)
        if c:
            files += 1
            total += c
            print(f"✅ {c:4d}  {p.relative_to(ROOT)}")
    print(f"\nfiles_changed={files} changes={total}")


if __name__ == "__main__":
    main()
