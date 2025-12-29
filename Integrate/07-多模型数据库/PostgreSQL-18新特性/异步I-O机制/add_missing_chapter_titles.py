#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有缺少章节标题的文档添加H2章节标题
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
print("🔧 添加缺失的章节标题")
print("=" * 70)

fixed_count = 0

for folder in folders:
    readme_path = folder / "README.md"
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否有H2章节标题
        h2_match = re.search(r'^##\s+\d+\.\s+', content, re.MULTILINE)

        # 检查是否有H1标题
        h1_match = re.search(r'^#\s+(\d+)\.\s+(.+)$', content, re.MULTILINE)

        if not h2_match and h1_match:
            # 有H1但没有H2，需要添加H2章节标题
            chapter_num = h1_match.group(1)
            chapter_title = h1_match.group(2).strip()

            # 找到H1的位置
            h1_pos = h1_match.end()

            # 检查后面是什么
            next_content = content[h1_pos:h1_pos+30]

            # 在H1后、目录前插入H2章节标题
            if next_content.startswith('\n\n## 📑'):
                # 在目录前插入
                new_content = content[:h1_pos] + f'\n\n## {chapter_num}. {chapter_title}\n' + content[h1_pos:]
            elif next_content.startswith('\n\n---'):
                # 在分隔线前插入
                new_content = content[:h1_pos] + f'\n\n## {chapter_num}. {chapter_title}\n' + content[h1_pos:]
            elif next_content.startswith('\n\n'):
                # 在空行后插入
                new_content = content[:h1_pos] + f'\n\n## {chapter_num}. {chapter_title}\n' + content[h1_pos:]
            else:
                # 直接插入
                new_content = content[:h1_pos] + f'\n\n## {chapter_num}. {chapter_title}\n' + content[h1_pos:]

            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            fixed_count += 1
            print(f"  ✅ {folder.name}: 已添加章节标题 '{chapter_num}. {chapter_title}'")

    except Exception as e:
        print(f"  ❌ {folder.name}: 处理失败 - {e}")

print(f"\n  ✅ 共修复 {fixed_count} 个文档")
print("\n" + "=" * 70)
print("修复完成")
print("=" * 70)
