#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有文档的目录、主题与子主题序号一致性
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
print("📋 序号一致性检查报告")
print("=" * 70)

issues = []

for folder in folders:
    readme_path = folder / "README.md"

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 提取章节号
        chapter_match = re.search(r'^##\s+(\d+)\.\s+', content, re.MULTILINE)
        if not chapter_match:
            issues.append(f"  ⚠️  {folder.name}: 缺少章节标题")
            continue

        chapter_num = int(chapter_match.group(1))

        # 检查目录中的序号
        toc_match = re.search(r'##\s*📑\s*目录\s*\n(.*?)\n---', content, re.DOTALL)
        if toc_match:
            toc_content = toc_match.group(1)
            # 检查目录中的标题是否与章节号一致
            toc_h3_matches = re.findall(r'-\s+\[(\d+\.\d+[^\]]*)\]', toc_content)
            for toc_title in toc_h3_matches:
                if not toc_title.startswith(f"{chapter_num}."):
                    issues.append(f"  ⚠️  {folder.name}: 目录中序号不一致 - {toc_title}")

        # 检查文档中的三级标题序号
        h3_matches = re.findall(r'^###\s+(\d+\.\d+[^\s]*)', content, re.MULTILINE)
        for h3_title in h3_matches:
            if not h3_title.startswith(f"{chapter_num}."):
                issues.append(f"  ⚠️  {folder.name}: 三级标题序号不一致 - {h3_title}")

        # 检查四级标题序号
        h4_matches = re.findall(r'^####\s+(\d+\.\d+\.\d+[^\s]*)', content, re.MULTILINE)
        for h4_title in h4_matches:
            if not h4_title.startswith(f"{chapter_num}."):
                issues.append(f"  ⚠️  {folder.name}: 四级标题序号不一致 - {h4_title}")

    except Exception as e:
        issues.append(f"  ❌ {folder.name}: 处理失败 - {e}")

print(f"\n检查的文档数: {len(folders)}")
print(f"发现的问题数: {len(issues)}")

if issues:
    print("\n问题列表:")
    for issue in issues[:30]:
        print(issue)
    if len(issues) > 30:
        print(f"  ... 还有 {len(issues) - 30} 个问题")
else:
    print("\n✅ 未发现问题！所有文档序号都一致！")

print("\n" + "=" * 70)
