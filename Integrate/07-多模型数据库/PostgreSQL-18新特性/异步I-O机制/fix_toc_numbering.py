#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复目录中的序号，确保目录中的标题与文档中的标题一致
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
print("🔧 修复目录序号一致性")
print("=" * 70)

fixed_count = 0

for folder in folders:
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
        
        # 提取所有三级标题（###）
        h3_titles = []
        for line in lines:
            h3_match = re.match(r'^###\s+(.+)$', line)
            if h3_match:
                full_title = h3_match.group(1).strip()
                h3_titles.append(full_title)
        
        if not h3_titles:
            continue
        
        # 生成新的目录
        toc_items = []
        for title in h3_titles:
            anchor = re.sub(r'\s+', '-', title)
            anchor = re.sub(r'[^\w\u4e00-\u9fa5-]', '', anchor)
            anchor = anchor.lower()
            anchor = re.sub(r'^\d+-\d+(-\d+)?-', '', anchor)
            toc_items.append(f"  - [{title}](#{anchor})")
        
        toc_markdown = "## 📑 目录\n\n" + "\n".join(toc_items) + "\n\n---\n\n"
        
        # 查找并替换目录
        toc_pattern = r'##\s*📑\s*目录\s*\n.*?\n---\s*\n'
        if re.search(toc_pattern, content, re.DOTALL):
            new_content = re.sub(toc_pattern, toc_markdown, content, flags=re.DOTALL)
            
            # 检查是否有变化
            if new_content != content:
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                fixed_count += 1
                print(f"  ✅ 修复: {folder.name}")
    
    except Exception as e:
        print(f"  ❌ {folder.name}: 处理失败 - {e}")

print(f"\n已修复 {fixed_count} 个文档的目录")
print("=" * 70)
