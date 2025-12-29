#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量为所有文档添加目录
"""

import os
import re
from pathlib import Path

base_path = Path(__file__).parent
print(f"工作目录: {base_path}")

# 获取所有章节文件夹
chapter_folders = sorted([
    d for d in base_path.iterdir()
    if d.is_dir() and re.match(r'^\d{2}-', d.name) and
    '归档' not in d.name and 'split' not in d.name and 'fix' not in d.name and 'add' not in d.name
])

print(f"\n找到 {len(chapter_folders)} 个章节文件夹\n")

processed_count = 0
fixed_count = 0

for folder in chapter_folders:
    readme_path = folder / "README.md"

    if not readme_path.exists():
        continue

    print(f"处理: {folder.name}")

    # 读取文件
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        print(f"  ❌ 读取文件失败: {e}")
        continue

    # 检查是否已有目录
    if re.search(r'##\s*📑\s*目录|##\s*目录|##\s*Contents', content):
        print("  ✓ 已有目录")
        processed_count += 1
        continue

    # 提取所有三级标题（###）
    toc_items = []
    for line in lines:
        match = re.match(r'^###\s+(.+)$', line)
        if match:
            full_title = match.group(1).strip()
            # 生成锚点（GitHub风格）
            anchor = re.sub(r'\s+', '-', full_title)
            anchor = re.sub(r'[^\w\u4e00-\u9fa5-]', '', anchor)
            anchor = anchor.lower()
            # 移除序号部分（如果存在）
            anchor = re.sub(r'^\d+-\d+(-\d+)?-', '', anchor)
            toc_items.append(f"  - [{full_title}](#{anchor})")

    if not toc_items:
        print("  ⚠️  无三级标题，跳过")
        processed_count += 1
        continue

    print(f"  → 添加目录 ({len(toc_items)} 项)...")

    toc_markdown = "## 📑 目录\n\n" + "\n".join(toc_items) + "\n\n---\n\n"

    # 查找章节标题的位置（## 数字. 标题）
    chapter_match = re.search(r'^##\s+\d+\.\s+.+?\n', content, re.MULTILINE)
    if chapter_match:
        chapter_end = chapter_match.end()
        # 查找分隔线位置
        separator_match = re.search(r'\n\n---\n\n', content[chapter_end:])
        if separator_match:
            # 在分隔线后插入目录
            insert_pos = chapter_end + separator_match.end()
            content = content[:insert_pos] + toc_markdown + content[insert_pos:]
        else:
            # 检查后面是否有空行
            next_lines = content[chapter_end:chapter_end+10]
            if next_lines.startswith('\n\n'):
                # 在空行后插入目录
                content = content[:chapter_end] + '\n\n' + toc_markdown + content[chapter_end:]
            elif next_lines.startswith('\n'):
                # 只有一个换行，添加目录
                content = content[:chapter_end] + '\n\n' + toc_markdown + content[chapter_end:]
            else:
                # 直接插入目录
                content = content[:chapter_end] + '\n\n' + toc_markdown + content[chapter_end:]
    else:
        # 如果没有找到章节标题，尝试在第一个三级标题前插入
        first_h3_match = re.search(r'^###\s+.+?\n', content, re.MULTILINE)
        if first_h3_match:
            # 查找第一个三级标题前的分隔线
            before_h3 = content[:first_h3_match.start()]
            separator_match = re.search(r'\n\n---\n\n', before_h3)
            if separator_match:
                # 在分隔线后插入目录
                insert_pos = separator_match.end()
                content = content[:insert_pos] + toc_markdown + content[insert_pos:]
            else:
                # 在第一个三级标题前插入目录
                content = content[:first_h3_match.start()] + toc_markdown + content[first_h3_match.start():]

    # 保存文件
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        fixed_count += 1
        print("  ✅ 已添加目录")
    except Exception as e:
        print(f"  ❌ 保存失败: {e}")

    processed_count += 1

print("\n" + "=" * 60)
print("处理完成统计")
print("=" * 60)
print(f"总处理数: {processed_count}")
print(f"已添加目录: {fixed_count}")
print("=" * 60)
