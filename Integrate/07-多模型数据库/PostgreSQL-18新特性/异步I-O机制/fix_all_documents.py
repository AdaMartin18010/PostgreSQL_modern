#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统性地修复所有文档
1. 添加目录
2. 完善主题与子主题的序号编号
3. 检查内容充实度
4. 修复导航链接
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
    '归档' not in d.name and
    'split' not in d.name and 'fix' not in d.name
], key=lambda x: x.name)

print(f"\n找到 {len(chapter_folders)} 个章节文件夹需要处理\n")

processed_count = 0
fixed_count = 0
needs_content_count = 0

for folder in chapter_folders:
    readme_path = folder / "README.md"

    if not readme_path.exists():
        print(f"⚠️  跳过: {folder.name} (无README.md)")
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

    original_content = content
    modified = False

    # 1. 检查并添加目录
    if not re.search(r'##\s*📑\s*目录|##\s*目录|##\s*Contents', content):
        print("  → 添加目录...")

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

        if toc_items:
            toc_markdown = "## 📑 目录\n\n" + "\n".join(toc_items) + "\n\n---\n\n"

            # 在章节标题后插入目录
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
                modified = True
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
                    modified = True

    # 2. 统一子标题编号格式
    # 提取章节号
    chapter_match = re.search(r'^##\s+(\d+)\.\s+', content, re.MULTILINE)
    chapter_num = int(chapter_match.group(1)) if chapter_match else 0

    if chapter_num > 0:
        new_lines = []
        sub_section_num = 0
        sub_sub_section_num = 0
        last_was_sub_sub = False

        for line in lines:
            # 匹配三级标题
            match = re.match(r'^###\s+(.+)$', line)
            if match:
                title = match.group(1).strip()

                # 检查是否已有正确的章节编号
                correct_match = re.match(rf'^{chapter_num}\.(\d+)(\.(\d+))?\s+(.+)$', title)
                if correct_match:
                    # 已有正确章节号，保持格式
                    existing_sub = int(correct_match.group(1))
                    if correct_match.group(2):
                        existing_sub_sub = int(correct_match.group(3))
                        title_text = correct_match.group(4)
                        new_lines.append(f"### {chapter_num}.{existing_sub}.{existing_sub_sub} {title_text}")
                        sub_section_num = existing_sub
                        sub_sub_section_num = existing_sub_sub
                        last_was_sub_sub = True
                    else:
                        title_text = correct_match.group(4)
                        new_lines.append(f"### {chapter_num}.{existing_sub} {title_text}")
                        sub_section_num = existing_sub
                        sub_sub_section_num = 0
                        last_was_sub_sub = False
                else:
                    # 检查是否有其他章节号，需要修正
                    wrong_match = re.match(r'^(\d+)\.(\d+)(\.(\d+))?\s+(.+)$', title)
                    if wrong_match:
                        wrong_chapter = int(wrong_match.group(1))
                        sub = int(wrong_match.group(2))
                        if wrong_match.group(3):
                            sub_sub = int(wrong_match.group(4))
                            title_text = wrong_match.group(5)
                            new_lines.append(f"### {chapter_num}.{sub}.{sub_sub} {title_text}")
                            sub_section_num = sub
                            sub_sub_section_num = sub_sub
                            last_was_sub_sub = True
                        else:
                            title_text = wrong_match.group(5)
                            new_lines.append(f"### {chapter_num}.{sub} {title_text}")
                            sub_section_num = sub
                            sub_sub_section_num = 0
                            last_was_sub_sub = False
                        modified = True
                    else:
                        # 无编号，需要添加
                        if last_was_sub_sub or sub_sub_section_num > 0:
                            # 继续子子标题编号
                            sub_sub_section_num += 1
                            new_lines.append(f"### {chapter_num}.{sub_section_num}.{sub_sub_section_num} {title}")
                            last_was_sub_sub = True
                        else:
                            # 新的子标题
                            sub_section_num += 1
                            sub_sub_section_num = 0
                            new_lines.append(f"### {chapter_num}.{sub_section_num} {title}")
                            last_was_sub_sub = False
                        modified = True
            else:
                new_lines.append(line)

        if modified:
            content = '\n'.join(new_lines)
            print("  → 统一子标题编号...")

    # 3. 检查内容充实度
    line_count = len(lines)
    code_block_count = len(re.findall(r'```', content)) // 2
    has_subsections = len(re.findall(r'^###', content, re.MULTILINE))

    if line_count < 100 and code_block_count < 2 and has_subsections < 3:
        print(f"  ⚠️  内容较少: {line_count} 行, {code_block_count} 代码块, {has_subsections} 子章节")
        needs_content_count += 1

    # 4. 添加导航链接（如果不存在）
    if not re.search(r'返回.*文档首页|上一章节|下一章节', content):
        print("  → 添加导航链接...")

        # 查找当前章节的索引
        current_index = -1
        for i, f in enumerate(chapter_folders):
            if f.name == folder.name:
                current_index = i
                break

        nav_parts = ['**返回**: [文档首页](../README.md)']

        if current_index > 0:
            prev_folder = chapter_folders[current_index - 1]
            nav_parts.append(f"[上一章节](../{prev_folder.name}/README.md)")

        if current_index < len(chapter_folders) - 1:
            next_folder = chapter_folders[current_index + 1]
            nav_parts.append(f"[下一章节](../{next_folder.name}/README.md)")

        nav_links = "\n\n---\n\n" + " | ".join(nav_parts) + "\n"
        content = content + nav_links
        modified = True

    # 保存修改
    if modified:
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed_count += 1
            print("  ✅ 已修复")
        except Exception as e:
            print(f"  ❌ 保存失败: {e}")
    else:
        print("  ✓ 无需修改")

    processed_count += 1

print("\n" + "=" * 60)
print("处理完成统计")
print("=" * 60)
print(f"总处理数: {processed_count}")
print(f"已修复数: {fixed_count}")
print(f"需要补充内容: {needs_content_count}")
print("=" * 60)
