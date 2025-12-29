#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复目录项数与H3标题数不一致的问题
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
print("🔧 修复目录项数与H3标题数不一致")
print("=" * 70)

fixed_count = 0

for folder in folders:
    readme_path = folder / "README.md"
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取所有H3标题
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
        
        # 如果没有任何H3标题，跳过（这些是空文档）
        if len(h3_matches) == 0:
            continue
        
        # 查找目录部分
        toc_match = re.search(r'(##\s*📑\s*目录\s*\n)(.*?)(\n---)', content, re.DOTALL)
        if not toc_match:
            continue
        
        toc_start = toc_match.start()
        toc_end = toc_match.end()
        toc_header = toc_match.group(1)
        toc_content = toc_match.group(2)
        toc_footer = toc_match.group(3)
        
        # 提取目录中的条目
        toc_items = re.findall(r'-\s+\[(.+?)\]\(#(.+?)\)', toc_content)
        
        # 如果目录项数与H3标题数不一致，重新生成目录
        if len(toc_items) != len(h3_matches):
            # 生成新的目录
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
            
            fixed_count += 1
            print(f"  ✅ {folder.name}: 已修复目录 ({len(toc_items)} → {len(h3_matches)} 项)")
    
    except Exception as e:
        print(f"  ❌ {folder.name}: 处理失败 - {e}")

print(f"\n  ✅ 共修复 {fixed_count} 个文档的目录")
print("\n" + "=" * 70)
print("修复完成")
print("=" * 70)
