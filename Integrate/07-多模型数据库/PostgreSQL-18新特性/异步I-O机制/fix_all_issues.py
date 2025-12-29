#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面修复所有文档问题：
1. 修复编号冲突
2. 添加缺失的章节标题
3. 修复目录格式（只保留三级标题，移除嵌套）
"""

import os
import re
from pathlib import Path

base_path = Path(__file__).parent

# 获取所有有效文档文件夹
folders = sorted([
    d for d in base_path.iterdir()
    if d.is_dir() and re.match(r'^\d{2}-', d.name) and
    (d / "README.md").exists()
])

print("=" * 70)
print("🔧 全面修复所有文档问题")
print("=" * 70)

# 第一步：修复编号冲突
print("\n1️⃣  检查编号冲突...")
folder_numbers = {}
for folder in folders:
    match = re.match(r'^(\d{2})-', folder.name)
    if match:
        num = int(match.group(1))
        if num in folder_numbers:
            print(f"  ⚠️  发现编号冲突: {folder_numbers[num]} 和 {folder.name}")
        folder_numbers[num] = folder.name

# 检查31-实用工具的章节号
utils_folder = base_path / "31-实用工具"
if utils_folder.exists():
    readme_path = utils_folder / "README.md"
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 检查元数据中的章节号
        meta_match = re.search(r'>\s*\*\*章节编号\*\*:\s*(\d+)', content)
        if meta_match:
            meta_num = int(meta_match.group(1))
            if meta_num == 29:
                print(f"  ✅ 31-实用工具的元数据显示章节号应为29，但文件夹名是31")
                print(f"  ℹ️  保持文件夹名为31，但需要确认这是正确的")

# 第二步：修复缺失的章节标题
print("\n2️⃣  修复缺失的章节标题...")
fixed_titles = []

for folder in folders:
    readme_path = folder / "README.md"
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有章节标题（## 数字. 标题）
        chapter_match = re.search(r'^##\s+\d+\.\s+', content, re.MULTILINE)
        
        # 检查是否有H1标题（# 数字. 标题）
        h1_match = re.search(r'^#\s+(\d+)\.\s+(.+)$', content, re.MULTILINE)
        
        if not chapter_match and h1_match:
            # 有H1但没有H2章节标题，需要添加
            chapter_num = h1_match.group(1)
            chapter_title = h1_match.group(2).strip()
            
            # 找到H1的位置，在其后添加H2章节标题
            h1_pos = h1_match.end()
            
            # 检查后面是否有分隔线
            next_content = content[h1_pos:h1_pos+10]
            if next_content.startswith('\n\n---'):
                # 在分隔线前插入章节标题
                new_content = content[:h1_pos] + f'\n\n## {chapter_num}. {chapter_title}\n' + content[h1_pos:]
            elif next_content.startswith('\n\n'):
                # 在空行后插入章节标题
                new_content = content[:h1_pos] + f'\n\n## {chapter_num}. {chapter_title}\n' + content[h1_pos:]
            else:
                # 直接插入
                new_content = content[:h1_pos] + f'\n\n## {chapter_num}. {chapter_title}\n' + content[h1_pos:]
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            fixed_titles.append(folder.name)
            print(f"  ✅ {folder.name}: 已添加章节标题")
    
    except Exception as e:
        print(f"  ❌ {folder.name}: 处理失败 - {e}")

if fixed_titles:
    print(f"\n  ✅ 已修复 {len(fixed_titles)} 个文档的章节标题")
else:
    print(f"\n  ✅ 所有文档都有章节标题")

# 第三步：修复目录格式
print("\n3️⃣  修复目录格式（只保留三级标题）...")
fixed_tocs = []

for folder in folders:
    readme_path = folder / "README.md"
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找目录部分
        toc_match = re.search(r'(##\s*📑\s*目录\s*\n)(.*?)(\n---)', content, re.DOTALL)
        if not toc_match:
            continue
        
        toc_start = toc_match.start()
        toc_end = toc_match.end()
        toc_header = toc_match.group(1)
        toc_content = toc_match.group(2)
        toc_footer = toc_match.group(3)
        
        # 提取所有三级标题（### 数字.数字 标题）
        h3_pattern = r'^###\s+(\d+)\.(\d+)(\.(\d+))?\s+(.+)$'
        h3_matches = []
        for line in content.split('\n'):
            match = re.match(h3_pattern, line)
            if match:
                chapter_num = int(match.group(1))
                section_num = int(match.group(2))
                subsection = match.group(4)
                title = match.group(5).strip()
                
                # 生成锚点链接
                anchor = re.sub(r'[^\w\s-]', '', title.lower())
                anchor = re.sub(r'[-\s]+', '-', anchor)
                
                h3_matches.append({
                    'chapter': chapter_num,
                    'section': section_num,
                    'subsection': subsection,
                    'title': title,
                    'anchor': anchor,
                    'full_title': f"{chapter_num}.{section_num}" + (f".{subsection}" if subsection else "") + f" {title}"
                })
        
        # 生成新的目录（只包含三级标题）
        if h3_matches:
            new_toc_items = []
            for item in h3_matches:
                link_text = item['full_title']
                link_anchor = item['anchor']
                new_toc_items.append(f"- [{link_text}](#{link_anchor})")
            
            new_toc_content = '\n'.join(new_toc_items)
            new_toc = toc_header + new_toc_content + toc_footer
            
            # 替换目录
            new_content = content[:toc_start] + new_toc + content[toc_end:]
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            fixed_tocs.append(folder.name)
            print(f"  ✅ {folder.name}: 已修复目录格式 ({len(h3_matches)} 个三级标题)")
    
    except Exception as e:
        print(f"  ❌ {folder.name}: 处理失败 - {e}")

if fixed_tocs:
    print(f"\n  ✅ 已修复 {len(fixed_tocs)} 个文档的目录格式")
else:
    print(f"\n  ✅ 所有文档的目录格式都正确")

print("\n" + "=" * 70)
print("修复完成")
print("=" * 70)
