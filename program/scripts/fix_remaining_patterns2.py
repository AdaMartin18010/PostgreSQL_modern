#!/usr/bin/env python3
"""
Fix remaining common broken-link patterns with safe, prefix-preserving rewrites.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"E:\_src\PostgreSQL_modern")


REPLACEMENTS: list[tuple[re.Pattern, str]] = [
    # Replace nonexistent project-files links with existing root docs
    (re.compile(r"\]\(\.\./\.\./00-项目文件/案例文档代码示例索引\.md\)"), "](../../code_validation_report.md)"),
    (re.compile(r"\]\(\.\./\.\./00-项目文件/项目完成总结报告\.md\)"), "](../../COMPLETION-SUMMARY.md)"),

    # 06-综合方案 typo
    (re.compile(r"\]\(\.\./06-综合方案/19-实战案例案例\.md\)"), "](../06-综合方案/04-应用场景案例.md)"),

    # Section rename: 06-对比分析 -> 23-对比分析
    (re.compile(r"\]\(\.\./06-对比分析/\)"), "](../23-对比分析/)"),

    # Short basename -> real path (preserve leading ../ segments in group(1))
    (re.compile(r"\]\(((?:\.\./)+)02\.03-统计信息与代价模型\.md\)"),
     r"](\1" + "02-查询与优化/02.04-统计信息/02.03-统计信息与代价模型.md)"),
    (re.compile(r"\]\(((?:\.\./)+)02\.04-执行计划与性能调优\.md\)"),
     r"](\1" + "02-查询与优化/02.03-执行计划/02.04-执行计划与性能调优.md)"),
    (re.compile(r"\]\(((?:\.\./)+)02\.02-索引结构与优化\.md\)"),
     r"](\1" + "02-查询与优化/02.02-索引结构/02.02-索引结构与优化.md)"),
    (re.compile(r"\]\(((?:\.\./)+)02\.01-查询优化器原理\.md\)"),
     r"](\1" + "02-查询与优化/02.01-查询优化器/02.01-查询优化器原理.md)"),
    (re.compile(r"\]\(((?:\.\./)+)01\.02-关系数据模型与理论\.md\)"),
     r"](\1" + "01-核心基础/01.03-数据模型/01.02-关系数据模型与理论.md)"),
    (re.compile(r"\]\(((?:\.\./)+)01\.03-SQL语言规范与标准\.md\)"),
     r"](\1" + "01-核心基础/01.04-SQL语言/01.03-SQL语言规范与标准.md)"),
    (re.compile(r"\]\(((?:\.\./)+)01\.01-系统架构与设计原理\.md\)"),
     r"](\1" + "01-核心基础/01.02-系统架构/01.01-系统架构与设计原理.md)"),

    # Missing design docs -> section README
    (re.compile(r"/17-数据模型设计/关系模型设计\.md\)"), "/17-数据模型设计/README.md)"),
    (re.compile(r"/17-数据模型设计/完整性约束设计\.md\)"), "/17-数据模型设计/README.md)"),

    # 30-性能调优 duplicated folder
    (re.compile(r"/30-性能调优/30-性能调优/README\.md\)"), "/30-性能调优/README.md)"),

    # 15-体系总览 missing docs -> point to existing concurrency/lock docs (relative depth fixed later)
    (re.compile(r"/15-体系总览/并发控制详解\.md\)"),
     "/03-事务与并发/03.01-MVCC机制/01.05-并发控制与MVCC机制.md)"),
    (re.compile(r"/15-体系总览/锁机制详解\.md\)"),
     "/03-事务与并发/11-锁机制深度解析.md)"),

    # 11-部署架构/99-归档 旧编号文档 -> 指向形式化方法 README
    (re.compile(r"\]\((1\.1\.1-形式模型|1\.1\.2-关系数据模型|1\.1\.4-查询优化-增强版)\.md\)"),
     "](../../25-理论体系/25.01-形式化方法/README.md)"),

    # Missing local navigation maps in deep folders -> root maps
    (re.compile(r"\]\(\.\./\.\./\.\./主题导航地图\.md\)"), "](../../【🗺️NAVIGATION】项目导航地图.md)"),
    (re.compile(r"\]\(\.\./\.\./\.\./权威资源索引\.md\)"), "](../../QUICK-REFERENCE.md)"),
]


def fix_file(p: Path) -> int:
    s = p.read_text(encoding="utf-8", errors="ignore")
    orig = s
    changes = 0
    for pat, rep in REPLACEMENTS:
        s2, n = pat.subn(rep, s)
        if n:
            changes += n
            s = s2
    if s != orig:
        p.write_text(s, encoding="utf-8")
    return changes


def main() -> None:
    targets = []
    targets.extend((ROOT / "Integrate").rglob("*.md"))
    targets.extend((ROOT / "archive").rglob("*.md") if (ROOT / "archive").exists() else [])
    targets.extend(ROOT.glob("*.md"))

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
