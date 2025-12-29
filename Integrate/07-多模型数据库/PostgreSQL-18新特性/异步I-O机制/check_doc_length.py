#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查文档内容长度
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
print("📏 检查文档内容长度")
print("=" * 70)

short_docs = []

for folder in folders:
    readme_path = base_path / folder / "README.md"
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            line_count = len(lines)
        
        if line_count < 150:
            short_docs.append((folder, line_count))
        
        print(f"  {folder}: {line_count}行")
        
    except Exception as e:
        print(f"  ❌ {folder}: 处理失败 - {e}")

print(f"\n检查的文档数: {len(folders)}")
if short_docs:
    print(f"\n⚠️  发现 {len(short_docs)} 个较短文档（<150行）:")
    for folder, lines in short_docs:
        print(f"  - {folder}: {lines}行")
else:
    print("\n✅ 所有文档内容充足（>=150行）")

print("\n" + "=" * 70)
print("检查完成")
print("=" * 70)
