#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复29-版本兼容性的目录格式
"""

import re
from pathlib import Path

readme_path = Path(__file__).parent / "29-版本兼容性" / "README.md"

with open(readme_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取所有三级标题
h3_pattern = r'^###\s+(.+)$'
h3_matches = []
for line in content.split('\n'):
    match = re.match(h3_pattern, line)
    if match:
        title = match.group(1).strip()
        # 确保不是四级标题
        if not line.startswith('####'):
            h3_matches.append(title)

# 生成新的目录
toc_items = []
for title in h3_matches:
    # 生成锚点
    anchor = re.sub(r'\s+', '-', title)
    anchor = re.sub(r'[^\w\u4e00-\u9fa5-]', '', anchor)
    anchor = anchor.lower()
    # 移除序号部分（如果存在）
    anchor = re.sub(r'^\d+-\d+(-\d+)?-', '', anchor)
    toc_items.append(f"- [{title}](#{anchor})")

new_toc = "## 📑 目录\n\n" + "\n".join(toc_items) + "\n\n---\n\n"

# 查找并替换目录
toc_pattern = r'##\s*📑\s*目录\s*\n.*?\n---\s*\n'
new_content = re.sub(toc_pattern, new_toc, content, flags=re.DOTALL)

with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ 已修复29-版本兼容性的目录格式 ({len(h3_matches)} 个三级标题)")
