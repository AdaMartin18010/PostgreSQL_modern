#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终完整性检查脚本
"""

import os
import re
from pathlib import Path

base_path = Path(__file__).parent
print("=" * 60)
print("最终完整性检查")
print("=" * 60)

# 获取所有章节文件夹
chapter_folders = sorted([
    d for d in base_path.iterdir() 
    if d.is_dir() and re.match(r'^\d{2}-', d.name) and 
    '归档' not in d.name and 'split' not in d.name and 'fix' not in d.name and 'add' not in d.name and 'final' not in d.name
])

print(f"\n检查的文件夹数: {len(chapter_folders)}")

issues = []
for folder in chapter_folders:
    readme_path = folder / "README.md"
    
    if not readme_path.exists():
        issues.append(f"  ❌ {folder.name}: 无README.md")
        continue
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查目录
        if not re.search(r'##\s*📑\s*目录|##\s*目录|##\s*Contents', content):
            issues.append(f"  ⚠️  {folder.name}: 无目录")
        
        # 检查导航
        if not re.search(r'返回.*文档首页', content):
            issues.append(f"  ⚠️  {folder.name}: 无导航链接")
        
    except Exception as e:
        issues.append(f"  ❌ {folder.name}: 读取失败 - {e}")

print(f"\n发现的问题数: {len(issues)}")

if issues:
    print("\n问题列表:")
    for issue in issues[:30]:  # 最多显示30个问题
        print(issue)
    if len(issues) > 30:
        print(f"  ... 还有 {len(issues) - 30} 个问题")
else:
    print("\n✅ 未发现问题！所有文档都完整！")

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)
