#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复所有TOC问题（包括统计方式优化）
"""
import os
import re
from pathlib import Path

base_path = Path(__file__).parent

print("=" * 70)
print("🔧 最终修复所有TOC问题")
print("=" * 70)

fixed_count = 0

# 处理所有目录
for md_file in base_path.rglob("*.md"):
    # 跳过README.md（可能不需要TOC）
    if md_file.name == 'README.md' and '参考资料' not in str(md_file) and '异步I-O机制' not in str(md_file):
        continue

    rel_path = md_file.relative_to(base_path)

    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 提取所有三级标题（###），不包括四级标题（####）
        h3_titles = []
        for i, line in enumerate(lines):
            h3_match = re.match(r'^###\s+(.+)$', line)
            if h3_match and not line.startswith('####'):
                full_title = h3_match.group(1).strip()
                h3_titles.append(full_title)

        if not h3_titles:
            continue

        # 检查并修复TOC
        toc_pattern = r'(##\s*📑\s*目录\s*\n)(.*?)(\n---\s*\n)'
        toc_match = re.search(toc_pattern, content, re.DOTALL)

        if toc_match:
            toc_start = toc_match.group(1)
            toc_content = toc_match.group(2)
            toc_end = toc_match.group(3)

            # 统计当前TOC项数（只统计指向锚点的链接）
            toc_lines = toc_content.split('\n')
            current_toc_items = len([l for l in toc_lines if re.match(r'^-\s+\[.*\]\(#', l.strip())])

            # 如果TOC项数与H3标题数不匹配，重新生成TOC
            if current_toc_items != len(h3_titles):
                # 生成新的目录（只包含三级标题）
                toc_items = []
                for title in h3_titles:
                    # 生成锚点
                    anchor = re.sub(r'\s+', '-', title)
                    anchor = re.sub(r'[^\w\u4e00-\u9fa5-]', '', anchor)
                    anchor = anchor.lower()
                    # 移除序号部分（如果存在）
                    anchor = re.sub(r'^\d+\.\d+(-\d+)?-', '', anchor)
                    toc_items.append(f"- [{title}](#{anchor})")

                new_toc_content = "\n".join(toc_items)
                new_toc = toc_start + new_toc_content + toc_end
                new_content = re.sub(toc_pattern, new_toc, content, flags=re.DOTALL)

                if new_content != content:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  ✅ 修复: {rel_path} (TOC项数: {current_toc_items} -> {len(h3_titles)}, H3数: {len(h3_titles)})")
                    fixed_count += 1

    except Exception as e:
        print(f"  ❌ 处理失败 {rel_path}: {e}")

print(f"\n已修复 {fixed_count} 个文档的TOC问题")
print("=" * 70)
