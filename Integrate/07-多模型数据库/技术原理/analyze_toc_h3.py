#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析TOC项数和H3标题数的差异原因
"""
import re
from pathlib import Path

base_path = Path(__file__).parent

for md_file in base_path.glob("*.md"):
    if md_file.name in ["check_document.py", "fix_toc_format.py", "fix_code_blocks.py", "fix_toc_mismatch.py", "analyze_toc_h3.py"]:
        continue
    
    print(f"\n📄 分析文档: {md_file.name}")
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # 提取TOC
    toc_start = -1
    toc_end = -1
    for i, line in enumerate(lines):
        if re.match(r'^##\s*📑\s*目录', line):
            toc_start = i
        elif toc_start >= 0 and line.strip().startswith('---'):
            toc_end = i
            break
    
    if toc_start >= 0 and toc_end >= 0:
        toc_lines = lines[toc_start:toc_end]
        toc_items = [l for l in toc_lines if l.strip().startswith('-')]
        print(f"  TOC项数: {len(toc_items)}")
        print(f"  TOC项示例（前5个）:")
        for item in toc_items[:5]:
            print(f"    {item}")
    
    # 提取H3标题
    h3_titles = []
    for i, line in enumerate(lines):
        h3_match = re.match(r'^###\s+(.+)$', line)
        if h3_match and not line.startswith('####'):
            full_title = h3_match.group(1).strip()
            h3_titles.append(full_title)
    
    print(f"  H3标题数: {len(h3_titles)}")
    print(f"  H3标题示例（前5个）:")
    for title in h3_titles[:5]:
        print(f"    {title}")
    
    if len(toc_items) != len(h3_titles):
        print(f"  ⚠️  差异: TOC项数({len(toc_items)}) != H3标题数({len(h3_titles)})")
        print(f"  📋 详细对比:")
        print(f"    TOC项数: {len(toc_items)}")
        print(f"    H3标题数: {len(h3_titles)}")
        print(f"    差异: {len(toc_items) - len(h3_titles)}")

