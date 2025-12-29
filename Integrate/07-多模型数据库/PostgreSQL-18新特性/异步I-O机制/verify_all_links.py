#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证所有文档中的链接是否有效
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
print("🔍 链接验证报告")
print("=" * 70)

total_links = 0
valid_links = 0
broken_links = []

# 获取所有文档的锚点
all_anchors = {}
for folder in folders:
    readme_path = folder / "README.md"
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取所有标题作为锚点
        anchors = []
        for line in content.split('\n'):
            # H2标题
            h2_match = re.match(r'^##\s+(.+)$', line)
            if h2_match:
                anchor = re.sub(r'[^\w\s-]', '', h2_match.group(1).lower())
                anchor = re.sub(r'[-\s]+', '-', anchor)
                anchors.append(anchor)

            # H3标题
            h3_match = re.match(r'^###\s+(.+)$', line)
            if h3_match and not line.startswith('####'):
                anchor = re.sub(r'[^\w\s-]', '', h3_match.group(1).lower())
                anchor = re.sub(r'[-\s]+', '-', anchor)
                anchors.append(anchor)

        all_anchors[folder.name] = anchors
    except:
        pass

# 验证链接
for folder in folders:
    readme_path = folder / "README.md"
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取所有链接
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

        for link_text, link_url in links:
            total_links += 1

            # 内部链接（以#开头）
            if link_url.startswith('#'):
                anchor = link_url[1:]  # 移除#
                # 检查锚点是否存在
                found = False
                for folder_name, anchors in all_anchors.items():
                    if anchor in anchors:
                        found = True
                        break
                if found:
                    valid_links += 1
                else:
                    broken_links.append((folder.name, link_text, link_url))

            # 相对路径链接
            elif link_url.startswith('../'):
                target_path = (readme_path.parent / link_url).resolve()
                if target_path.exists():
                    valid_links += 1
                else:
                    broken_links.append((folder.name, link_text, link_url))

            # 外部链接（http/https）
            elif link_url.startswith('http'):
                valid_links += 1  # 假设外部链接有效

    except Exception as e:
        print(f"  ⚠️  {folder.name}: 处理失败 - {e}")

print(f"\n📊 链接统计:")
print(f"  总链接数: {total_links}")
print(f"  有效链接: {valid_links}")
print(f"  损坏链接: {len(broken_links)}")
print(f"  链接有效率: {(valid_links / total_links * 100) if total_links > 0 else 0:.1f}%")

if broken_links:
    print(f"\n⚠️  损坏的链接:")
    for doc, text, url in broken_links[:10]:
        print(f"  - {doc}: [{text}]({url})")
    if len(broken_links) > 10:
        print(f"  ... 还有 {len(broken_links) - 10} 个")
else:
    print(f"\n✅ 所有链接都有效！")

print("\n" + "=" * 70)
print("验证完成")
print("=" * 70)
