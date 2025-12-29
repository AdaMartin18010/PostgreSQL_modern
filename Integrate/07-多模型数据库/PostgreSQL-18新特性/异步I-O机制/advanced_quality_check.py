#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级质量检查：检查文档的深度质量指标
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
print("🔍 高级质量检查报告")
print("=" * 70)

total_docs = len(folders)
metrics = {
    'total_chars': 0,
    'total_lines': 0,
    'total_code_blocks': 0,
    'total_tables': 0,
    'total_links': 0,
    'docs_with_examples': 0,
    'docs_with_diagrams': 0,
}

for folder in folders:
    readme_path = folder / "README.md"

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 统计指标
        metrics['total_chars'] += len(content)
        metrics['total_lines'] += len(lines)
        metrics['total_code_blocks'] += len(re.findall(r'```', content)) // 2
        metrics['total_tables'] += len(re.findall(r'\|.*\|', content))
        metrics['total_links'] += len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))

        # 检查是否有代码示例
        if re.search(r'```(sql|python|bash|sh)', content):
            metrics['docs_with_examples'] += 1

        # 检查是否有图表（mermaid或其他）
        if re.search(r'```(mermaid|graph|flowchart)', content, re.IGNORECASE):
            metrics['docs_with_diagrams'] += 1

    except Exception as e:
        print(f"  ⚠️  {folder.name}: 处理失败 - {e}")

print(f"\n📊 文档统计:")
print(f"  总文档数: {total_docs}")
print(f"  总字符数: {metrics['total_chars']:,}")
print(f"  总行数: {metrics['total_lines']:,}")
print(f"  平均每文档字符数: {metrics['total_chars'] // total_docs:,}")
print(f"  平均每文档行数: {metrics['total_lines'] // total_docs:,}")

print(f"\n📝 内容统计:")
print(f"  代码块总数: {metrics['total_code_blocks']}")
print(f"  表格总数: {metrics['total_tables']}")
print(f"  链接总数: {metrics['total_links']}")
print(f"  包含代码示例的文档: {metrics['docs_with_examples']}/{total_docs}")
print(f"  包含图表的文档: {metrics['docs_with_diagrams']}/{total_docs}")

print(f"\n📈 内容质量指标:")
print(f"  平均每文档代码块数: {metrics['total_code_blocks'] / total_docs:.1f}")
print(f"  平均每文档表格数: {metrics['total_tables'] / total_docs:.1f}")
print(f"  平均每文档链接数: {metrics['total_links'] / total_docs:.1f}")

print("\n" + "=" * 70)
print("检查完成")
print("=" * 70)
