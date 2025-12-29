#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复文档目录位置：将目录移到文档开头（章节标题之后）
"""

import os
import re
from pathlib import Path

base_path = Path(__file__).parent

# 获取所有有效文档文件夹
folders = sorted([
    d.name for d in base_path.iterdir() 
    if d.is_dir() and re.match(r'^\d{2}-', d.name) and 
    (d / "README.md").exists()
])

print("=" * 70)
print("🔧 修复目录位置")
print("=" * 70)

fixed_count = 0

for folder in folders:
    readme_path = base_path / folder / "README.md"
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # 查找目录位置
        toc_pattern = r'##\s*📑\s*目录'
        toc_matches = list(re.finditer(toc_pattern, content))
        
        if not toc_matches:
            continue
        
        if len(toc_matches) > 1:
            # 有多个目录，保留第一个，删除其他的
            print(f"  ⚠️  {folder}: 发现多个目录，需要手动处理")
            continue
        
        toc_start = toc_matches[0].start()
        toc_line_start = content[:toc_start].count('\n')
        
        # 查找章节标题位置
        chapter_pattern = r'^##\s+\d+\.\s+'
        chapter_matches = list(re.finditer(chapter_pattern, content, re.MULTILINE))
        
        if not chapter_matches:
            continue
        
        chapter_line = content[:chapter_matches[0].start()].count('\n')
        
        # 如果目录在第50行之后，需要移到前面
        if toc_line_start > 50:
            # 提取目录部分（从目录标题到下一个---或章节标题）
            toc_end_pattern = r'(?=\n---\n|##\s+\d+\.\s+)'
            toc_match = re.search(r'##\s*📑\s*目录.*?(?=\n---\n|##\s+\d+\.\s+)', content, re.DOTALL)
            
            if not toc_match:
                continue
            
            toc_content = toc_match.group(0)
            
            # 删除原来的目录
            content_without_toc = content[:toc_match.start()] + content[toc_match.end():]
            
            # 在章节标题之后插入目录
            chapter_match = re.search(r'^##\s+\d+\.\s+.*$', content_without_toc, re.MULTILINE)
            if chapter_match:
                insert_pos = content_without_toc.find('\n', chapter_match.end())
                if insert_pos != -1:
                    new_content = (
                        content_without_toc[:insert_pos+1] + 
                        '\n' + toc_content + '\n' +
                        content_without_toc[insert_pos+1:]
                    )
                    
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"  ✅ {folder}: 目录已移至第{chapter_line+2}行")
                    fixed_count += 1
        
    except Exception as e:
        print(f"  ❌ {folder}: 处理失败 - {e}")

print(f"\n已修复 {fixed_count} 个文档的目录位置")
print("=" * 70)
