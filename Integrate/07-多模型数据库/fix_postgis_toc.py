#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复PostGIS空间数据完整实战指南.md的TOC格式
"""
import re
from pathlib import Path

file_path = Path(__file__).parent / 'PostGIS空间数据完整实战指南.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# 提取所有三级标题（###），不包括四级标题（####）
h3_titles = []
for i, line in enumerate(lines):
    h3_match = re.match(r'^###\s+(.+)$', line)
    if h3_match and not line.startswith('####'):
        full_title = h3_match.group(1).strip()
        h3_titles.append(full_title)

print(f"找到 {len(h3_titles)} 个H3标题")

# 生成新的目录（只包含三级标题，无嵌套）
toc_items = []
for title in h3_titles:
    # 生成锚点
    anchor = re.sub(r'\s+', '-', title)
    anchor = re.sub(r'[^\w\u4e00-\u9fa5-]', '', anchor)
    anchor = anchor.lower()
    # 移除序号部分（如果存在）
    anchor = re.sub(r'^\d+\.\d+(-\d+)?-', '', anchor)
    toc_items.append(f"- [{title}](#{anchor})")

toc_markdown = "## 📋 完整目录\n\n" + "\n".join(toc_items) + "\n\n---\n\n"

# 查找并替换目录
toc_pattern = r'(##\s*📋\s*完整目录\s*\n)(.*?)(\n---\s*\n)'
new_content = re.sub(toc_pattern, toc_markdown, content, flags=re.DOTALL)

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ 修复完成: TOC项数已更新为 {len(h3_titles)} 个")
else:
    print("ℹ️  无需修复")
