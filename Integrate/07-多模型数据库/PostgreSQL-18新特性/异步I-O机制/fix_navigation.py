#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复所有文档的导航链接，确保都有上一章节和下一章节
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

print(f"找到 {len(folders)} 个文档需要检查\n")

fixed_count = 0

for i, folder in enumerate(folders):
    readme_path = folder / "README.md"
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有完整的导航链接（包含上一章节和下一章节）
        has_full_nav = re.search(r'上一章节.*下一章节', content)
        has_basic_nav = re.search(r'返回.*文档首页', content)
        
        if has_full_nav:
            print(f"  ✓ {folder.name}: 导航完整")
            continue
        
        if not has_basic_nav:
            print(f"  ⚠️  {folder.name}: 无导航链接")
            continue
        
        print(f"  → {folder.name}: 补充导航链接...")
        
        # 构建导航链接
        nav_parts = ['**返回**: [文档首页](../README.md)']
        
        # 上一章节
        if i > 0:
            prev_folder = folders[i - 1]
            nav_parts.append(f"[上一章节](../{prev_folder.name}/README.md)")
        
        # 下一章节
        if i < len(folders) - 1:
            next_folder = folders[i + 1]
            nav_parts.append(f"[下一章节](../{next_folder.name}/README.md)")
        
        nav_links = "\n\n---\n\n" + " | ".join(nav_parts) + "\n"
        
        # 查找现有的导航链接位置并替换
        nav_match = re.search(r'\n\n---\n\n\*\*返回\*\*.*文档首页.*\n', content)
        if nav_match:
            # 替换现有的导航链接
            content = content[:nav_match.start()] + nav_links + content[nav_match.end():]
        else:
            # 在文件末尾添加导航链接
            content = content.rstrip() + nav_links
        
        # 保存文件
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        fixed_count += 1
        print(f"    ✅ 已修复")
        
    except Exception as e:
        print(f"  ❌ {folder.name}: 处理失败 - {e}")

print(f"\n处理完成: 修复了 {fixed_count} 个文档")
