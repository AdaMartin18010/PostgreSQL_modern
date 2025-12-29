#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终全面检查：检查目录格式、序号一致性、导航链接等所有细节
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
print("🔍 最终全面检查报告")
print("=" * 70)

issues = []
warnings = []

for folder in folders:
    readme_path = folder / "README.md"

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 提取章节号
        chapter_match = re.search(r'^##\s+(\d+)\.\s+', content, re.MULTILINE)
        if not chapter_match:
            issues.append(f"  ❌ {folder.name}: 缺少章节标题")
            continue

        chapter_num = int(chapter_match.group(1))

        # 检查目录格式
        toc_match = re.search(r'##\s*📑\s*目录\s*\n(.*?)\n---', content, re.DOTALL)
        if toc_match:
            toc_content = toc_match.group(1)
            # 检查目录是否包含嵌套（不应该有）
            if re.search(r'^\s{4,}-', toc_content, re.MULTILINE):
                warnings.append(f"  ⚠️  {folder.name}: 目录包含嵌套层级")

            # 检查目录中的标题是否与文档中的三级标题一致
            toc_titles = re.findall(r'-\s+\[(.+?)\]', toc_content)
            h3_titles = []
            for line in lines:
                h3_match = re.match(r'^###\s+(.+)$', line)
                if h3_match and not line.startswith('####'):
                    h3_titles.append(h3_match.group(1).strip())

            # 比较目录和文档标题
            if len(toc_titles) != len(h3_titles):
                warnings.append(f"  ⚠️  {folder.name}: 目录项数({len(toc_titles)})与三级标题数({len(h3_titles)})不一致")
            else:
                for toc_title, h3_title in zip(toc_titles, h3_titles):
                    # 移除序号后比较
                    toc_clean = re.sub(r'^\d+\.\d+(\s+|\.)', '', toc_title).strip()
                    h3_clean = re.sub(r'^\d+\.\d+(\s+|\.)', '', h3_title).strip()
                    if toc_clean != h3_clean:
                        warnings.append(f"  ⚠️  {folder.name}: 目录标题与文档标题不一致 - '{toc_title}' vs '{h3_title}'")

        # 检查三级标题序号
        h3_matches = re.findall(r'^###\s+(\d+)\.(\d+)(\.(\d+))?\s+(.+)$', content, re.MULTILINE)
        for match in h3_matches:
            wrong_chapter = int(match[0])
            if wrong_chapter != chapter_num:
                issues.append(f"  ❌ {folder.name}: 三级标题序号错误 - {match[0]}.{match[1]} (应该是 {chapter_num}.{match[1]})")

        # 检查导航链接
        if not re.search(r'返回.*文档首页', content):
            issues.append(f"  ❌ {folder.name}: 缺少导航链接")

    except Exception as e:
        issues.append(f"  ❌ {folder.name}: 处理失败 - {e}")

print(f"\n检查的文档数: {len(folders)}")
print(f"发现的问题数: {len(issues)}")
print(f"发现的警告数: {len(warnings)}")

if issues:
    print("\n❌ 问题列表:")
    for issue in issues[:30]:
        print(issue)
    if len(issues) > 30:
        print(f"  ... 还有 {len(issues) - 30} 个问题")

if warnings:
    print("\n⚠️  警告列表:")
    for warning in warnings[:30]:
        print(warning)
    if len(warnings) > 30:
        print(f"  ... 还有 {len(warnings) - 30} 个警告")

if not issues and not warnings:
    print("\n✅ 完美！未发现任何问题！所有文档都符合标准！")

print("\n" + "=" * 70)
print("检查完成")
print("=" * 70)
