#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描并修复08-流处理与时序目录下所有文档的TOC问题
"""
import os
import re
from pathlib import Path
from collections import defaultdict

base_path = Path(__file__).parent

print("=" * 70)
print("🔍 扫描08-流处理与时序目录")
print("=" * 70)

issues = defaultdict(list)

for md_file in base_path.glob("*.md"):
    if md_file.name == 'README.md':
        continue

    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        rel_path = md_file.name

        # 提取所有三级标题（###），不包括四级标题（####）
        h3_titles = []
        for i, line in enumerate(lines):
            h3_match = re.match(r'^###\s+(.+)$', line)
            if h3_match and not line.startswith('####'):
                full_title = h3_match.group(1).strip()
                h3_titles.append(full_title)

        if not h3_titles:
            continue

        # 检查TOC
        toc_pattern = r'(##\s*📑\s*目录\s*\n|##\s*📋\s*目录\s*\n|##\s*📑\s*完整目录\s*\n|##\s*📋\s*完整目录\s*\n)(.*?)(\n---\s*\n)'
        toc_match = re.search(toc_pattern, content, re.DOTALL)

        if toc_match:
            toc_start = toc_match.group(1)
            toc_content = toc_match.group(2)
            toc_end = toc_match.group(3)

            # 检查是否有嵌套
            toc_lines = toc_content.split('\n')
            has_nested = any('  -' in line or '    -' in line for line in toc_lines)

            # 统计当前TOC项数（只统计指向锚点的链接）
            current_toc_items = len([l for l in toc_lines if re.match(r'^-\s+\[.*\]\(#', l.strip())])

            if has_nested:
                issues['nested_toc'].append(f"{rel_path}: {current_toc_items}项, H3={len(h3_titles)}")

            if current_toc_items != len(h3_titles):
                issues['toc_mismatch'].append(f"{rel_path}: TOC={current_toc_items}, H3={len(h3_titles)}")
        else:
            issues['no_toc'].append(rel_path)

        # 检查未闭合的代码块
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            issues['unclosed_code'].append(rel_path)

    except Exception as e:
        print(f"  ❌ 处理失败 {rel_path}: {e}")

print("\n📊 发现的问题:")
for issue_type, items in sorted(issues.items()):
    if items:
        print(f"\n⚠️  {issue_type} ({len(items)}个):")
        for item in items[:10]:
            print(f"     - {item}")
        if len(items) > 10:
            print(f"     ... 还有 {len(items) - 10} 个")

print("\n" + "=" * 70)
