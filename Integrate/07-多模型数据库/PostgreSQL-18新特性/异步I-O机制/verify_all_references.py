#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证所有文档中的引用链接是否正确
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
print("🔍 文档引用链接验证")
print("=" * 70)

issues = []
warnings = []

for folder in folders:
    readme_path = base_path / folder / "README.md"

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查导航链接中的引用
        nav_pattern_prev = r'\[上一章节\]\(\.\./(\d{2}-[^/]+)/README\.md\)'
        nav_pattern_next = r'\[下一章节\]\(\.\./(\d{2}-[^/]+)/README\.md\)'
        nav_matches_prev = re.findall(nav_pattern_prev, content)
        nav_matches_next = re.findall(nav_pattern_next, content)
        
        for ref_folder in nav_matches_prev + nav_matches_next:
            if ref_folder and ref_folder not in folders:
                issues.append(f"  ❌ {folder}: 导航链接指向不存在的文件夹 '{ref_folder}'")

        # 检查文档中的其他引用
        ref_pattern = r'\[([^\]]+)\]\(\.\./(\d{2}-[^/]+)/README\.md\)'
        ref_matches = re.findall(ref_pattern, content)

        for ref_text, ref_folder in ref_matches:
            if ref_folder not in folders:
                issues.append(f"  ❌ {folder}: 引用指向不存在的文件夹 '{ref_folder}' (文本: {ref_text})")

    except Exception as e:
        issues.append(f"  ❌ {folder}: 处理失败 - {e}")

print(f"\n检查的文档数: {len(folders)}")
print(f"发现的问题数: {len(issues)}")

if issues:
    print("\n❌ 问题列表:")
    for issue in issues[:30]:
        print(issue)
    if len(issues) > 30:
        print(f"  ... 还有 {len(issues) - 30} 个问题")
else:
    print("\n✅ 完美！所有引用链接都正确！")

print("\n" + "=" * 70)
print("验证完成")
print("=" * 70)
