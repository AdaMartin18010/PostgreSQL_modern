#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复TOC中包含文档末尾链接的问题
"""
import os
import re
from pathlib import Path

base_path = Path(__file__).parent

print("=" * 70)
print("🔧 修复TOC中包含文档末尾链接的问题")
print("=" * 70)

fixed_count = 0

for md_file in base_path.rglob("*.md"):
    rel_path = md_file.relative_to(base_path)

    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取所有三级标题（###），不包括四级标题（####）
        h3_titles = []
        for line in content.split('\n'):
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

            # 只保留指向锚点的TOC项（排除相对路径链接）
            toc_lines = toc_content.split('\n')
            valid_toc_items = []
            for line in toc_lines:
                line = line.strip()
                # 只保留指向锚点的链接（#开头），排除相对路径链接（./开头）
                if re.match(r'^-\s+\[.*\]\(#', line):
                    valid_toc_items.append(line)

            # 如果有效TOC项数与H3标题数不匹配，重新生成TOC
            if len(valid_toc_items) != len(h3_titles):
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
                    print(f"  ✅ 修复: {rel_path} (TOC项数: {len(valid_toc_items)} -> {len(h3_titles)}, H3数: {len(h3_titles)})")
                    fixed_count += 1

    except Exception as e:
        print(f"  ❌ 处理失败 {rel_path}: {e}")

print(f"\n已修复 {fixed_count} 个文档的TOC问题")
print("=" * 70)
