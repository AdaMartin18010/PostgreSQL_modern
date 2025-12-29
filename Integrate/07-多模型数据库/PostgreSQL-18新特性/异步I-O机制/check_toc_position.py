#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有文档的目录位置是否正确（应该在文档开头，章节标题之后）
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
print("🔍 检查目录位置")
print("=" * 70)

issues = []

for folder in folders:
    readme_path = base_path / folder / "README.md"
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = ''.join(lines)
        
        # 查找目录位置
        toc_pattern = r'##\s*📑\s*目录'
        toc_matches = list(re.finditer(toc_pattern, content))
        
        if not toc_matches:
            issues.append(f"  ❌ {folder}: 缺少目录")
            continue
        
        if len(toc_matches) > 1:
            issues.append(f"  ⚠️  {folder}: 目录出现多次")
            continue
        
        toc_pos = toc_matches[0].start()
        
        # 查找章节标题位置
        chapter_pattern = r'^##\s+\d+\.\s+'
        chapter_matches = list(re.finditer(chapter_pattern, content, re.MULTILINE))
        
        if not chapter_matches:
            issues.append(f"  ⚠️  {folder}: 未找到章节标题")
            continue
        
        chapter_pos = chapter_matches[0].start()
        
        # 目录应该在章节标题之前（在文档开头部分）
        # 但应该在元数据之后
        # 检查目录是否在合理位置（前100行内）
        toc_line_num = content[:toc_pos].count('\n') + 1
        
        if toc_line_num > 50:
            issues.append(f"  ⚠️  {folder}: 目录位置较后（第{toc_line_num}行），建议放在文档开头")
        
    except Exception as e:
        issues.append(f"  ❌ {folder}: 处理失败 - {e}")

print(f"\n检查的文档数: {len(folders)}")
print(f"发现的问题数: {len(issues)}")

if issues:
    print("\n问题列表:")
    for issue in issues[:20]:
        print(issue)
    if len(issues) > 20:
        print(f"  ... 还有 {len(issues) - 20} 个问题")
else:
    print("\n✅ 完美！所有文档的目录位置都正确！")

print("\n" + "=" * 70)
print("检查完成")
print("=" * 70)
