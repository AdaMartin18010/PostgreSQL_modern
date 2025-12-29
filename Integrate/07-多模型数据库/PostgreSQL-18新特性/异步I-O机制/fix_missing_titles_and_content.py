#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复缺失的章节标题，并处理空内容文档
"""

import os
import re
from pathlib import Path

base_path = Path(__file__).parent

folders = sorted([
    d for d in base_path.iterdir()
    if d.is_dir() and re.match(r'^\d{2}-', d.name) and
    (d / "README.md").exists()
])

print("=" * 70)
print("🔧 修复缺失的章节标题")
print("=" * 70)

fixed_titles = []
empty_docs = []

for folder in folders:
    readme_path = folder / "README.md"
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有H2章节标题
        h2_match = re.search(r'^##\s+\d+\.\s+', content, re.MULTILINE)
        
        # 检查是否有H1标题
        h1_match = re.search(r'^#\s+(\d+)\.\s+(.+)$', content, re.MULTILINE)
        
        if not h2_match and h1_match:
            # 有H1但没有H2，需要添加H2章节标题
            chapter_num = h1_match.group(1)
            chapter_title = h1_match.group(2).strip()
            
            # 找到H1的位置
            h1_pos = h1_match.end()
            
            # 检查后面是否有分隔线或目录
            next_content = content[h1_pos:h1_pos+20]
            if next_content.startswith('\n\n## 📑'):
                # 在目录前插入章节标题
                new_content = content[:h1_pos] + f'\n\n## {chapter_num}. {chapter_title}\n' + content[h1_pos:]
            elif next_content.startswith('\n\n---'):
                # 在分隔线前插入章节标题
                new_content = content[:h1_pos] + f'\n\n## {chapter_num}. {chapter_title}\n' + content[h1_pos:]
            else:
                # 直接插入
                new_content = content[:h1_pos] + f'\n\n## {chapter_num}. {chapter_title}\n' + content[h1_pos:]
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            fixed_titles.append(folder.name)
            print(f"  ✅ {folder.name}: 已添加章节标题")
        
        # 检查文档是否有实际内容（除了元数据、标题、目录、导航）
        # 提取所有H3标题
        h3_matches = re.findall(r'^###\s+(\d+)\.(\d+)(\.(\d+))?\s+(.+)$', content, re.MULTILINE)
        
        # 检查是否有TOC
        toc_match = re.search(r'##\s*📑\s*目录\s*\n(.*?)\n---', content, re.DOTALL)
        
        if toc_match and len(h3_matches) == 0:
            # 有TOC但没有H3标题，文档可能是空的
            # 提取TOC中的条目
            toc_content = toc_match.group(1)
            toc_items = re.findall(r'-\s+\[(.+?)\]', toc_content)
            
            if len(toc_items) > 0:
                empty_docs.append({
                    'folder': folder.name,
                    'toc_count': len(toc_items),
                    'h3_count': 0
                })
                print(f"  ⚠️  {folder.name}: 有目录但无内容 ({len(toc_items)} 个目录项)")
    
    except Exception as e:
        print(f"  ❌ {folder.name}: 处理失败 - {e}")

if fixed_titles:
    print(f"\n  ✅ 已修复 {len(fixed_titles)} 个文档的章节标题")
else:
    print(f"\n  ✅ 所有文档都有章节标题")

if empty_docs:
    print(f"\n  ⚠️  发现 {len(empty_docs)} 个文档有目录但缺少内容:")
    for doc in empty_docs:
        print(f"    - {doc['folder']}: {doc['toc_count']} 个目录项，0 个H3标题")

print("\n" + "=" * 70)
print("修复完成")
print("=" * 70)
