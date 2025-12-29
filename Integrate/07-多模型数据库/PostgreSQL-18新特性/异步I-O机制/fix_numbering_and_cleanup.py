#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复所有文档的目录、主题与子主题序号一致性
并删除无内容的文件夹
"""

import os
import re
import shutil
from pathlib import Path

base_path = Path(__file__).parent

print("=" * 70)
print("🔧 修复序号一致性和清理无内容文件夹")
print("=" * 70)

# 1. 删除无内容的文件夹
print("\n1️⃣ 清理无内容的文件夹...")
folders = sorted([d for d in base_path.iterdir() if d.is_dir() and re.match(r'^\d{2}-', d.name)])
empty_folders = [f for f in folders if not (f / "README.md").exists()]

print(f"找到 {len(empty_folders)} 个无内容的文件夹")
deleted_count = 0

for folder in empty_folders:
    try:
        # 检查文件夹是否为空
        if not any(folder.iterdir()):
            shutil.rmtree(folder)
            print(f"  ✅ 删除空文件夹: {folder.name}")
            deleted_count += 1
        else:
            print(f"  ⚠️  跳过（文件夹非空）: {folder.name}")
    except Exception as e:
        print(f"  ❌ 删除失败 {folder.name}: {e}")

print(f"\n已删除 {deleted_count} 个无内容文件夹")

# 2. 修复序号一致性
print("\n2️⃣ 修复文档序号一致性...")

# 获取所有有效文档文件夹
valid_folders = sorted([
    d for d in base_path.iterdir()
    if d.is_dir() and re.match(r'^\d{2}-', d.name) and
    (d / "README.md").exists()
])

fixed_count = 0

for folder in valid_folders:
    readme_path = folder / "README.md"

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 提取章节号
        chapter_match = re.search(r'^##\s+(\d+)\.\s+', content, re.MULTILINE)
        if not chapter_match:
            continue

        chapter_num = int(chapter_match.group(1))
        modified = False
        new_lines = []

        # 重新处理每一行
        for line in lines:
            # 处理三级标题
            h3_match = re.match(r'^###\s+(\d+)\.(\d+)(\.(\d+))?\s+(.+)$', line)
            if h3_match:
                wrong_chapter = int(h3_match.group(1))
                sub_num = int(h3_match.group(2))
                if h3_match.group(3):
                    sub_sub_num = int(h3_match.group(4))
                    title = h3_match.group(5)
                    if wrong_chapter != chapter_num:
                        new_line = f"### {chapter_num}.{sub_num}.{sub_sub_num} {title}"
                        new_lines.append(new_line)
                        modified = True
                    else:
                        new_lines.append(line)
                else:
                    title = h3_match.group(5)
                    if wrong_chapter != chapter_num:
                        new_line = f"### {chapter_num}.{sub_num} {title}"
                        new_lines.append(new_line)
                        modified = True
                    else:
                        new_lines.append(line)
            # 处理四级标题
            elif re.match(r'^####\s+(\d+)\.(\d+)\.(\d+)(\.(\d+))?\s+', line):
                h4_match = re.match(r'^####\s+(\d+)\.(\d+)\.(\d+)(\.(\d+))?\s+(.+)$', line)
                if h4_match:
                    wrong_chapter = int(h4_match.group(1))
                    sub_num = int(h4_match.group(2))
                    sub_sub_num = int(h4_match.group(3))
                    if h4_match.group(4):
                        sub_sub_sub_num = int(h4_match.group(5))
                        title = h4_match.group(6)
                        if wrong_chapter != chapter_num:
                            new_line = f"#### {chapter_num}.{sub_num}.{sub_sub_num}.{sub_sub_sub_num} {title}"
                            new_lines.append(new_line)
                            modified = True
                        else:
                            new_lines.append(line)
                    else:
                        title = h4_match.group(6)
                        if wrong_chapter != chapter_num:
                            new_line = f"#### {chapter_num}.{sub_num}.{sub_sub_num} {title}"
                            new_lines.append(new_line)
                            modified = True
                        else:
                            new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # 重新生成目录
        if modified:
            # 提取所有三级标题
            toc_items = []
            for line in new_lines:
                h3_match = re.match(r'^###\s+(\d+)\.(\d+)(\.(\d+))?\s+(.+)$', line)
                if h3_match:
                    full_title = line.replace('### ', '').strip()
                    anchor = re.sub(r'\s+', '-', full_title)
                    anchor = re.sub(r'[^\w\u4e00-\u9fa5-]', '', anchor)
                    anchor = anchor.lower()
                    anchor = re.sub(r'^\d+-\d+(-\d+)?-', '', anchor)
                    toc_items.append(f"  - [{full_title}](#{anchor})")

            # 替换目录
            toc_markdown = "## 📑 目录\n\n" + "\n".join(toc_items) + "\n\n---\n\n"

            # 查找并替换目录
            toc_pattern = r'##\s*📑\s*目录\s*\n.*?\n---\s*\n'
            if re.search(toc_pattern, content, re.DOTALL):
                content = re.sub(toc_pattern, toc_markdown, content, flags=re.DOTALL)
            else:
                # 如果没有目录，在章节标题后添加
                chapter_match = re.search(r'^##\s+\d+\.\s+.+?\n', content, re.MULTILINE)
                if chapter_match:
                    chapter_end = chapter_match.end()
                    separator_match = re.search(r'\n\n---\n\n', content[chapter_end:])
                    if separator_match:
                        insert_pos = chapter_end + separator_match.end()
                        content = content[:insert_pos] + toc_markdown + content[insert_pos:]

            # 保存文件
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)

            fixed_count += 1
            print(f"  ✅ 修复: {folder.name}")

    except Exception as e:
        print(f"  ❌ {folder.name}: 处理失败 - {e}")

print(f"\n已修复 {fixed_count} 个文档的序号")

print("\n" + "=" * 70)
print("✅ 修复完成")
print("=" * 70)
