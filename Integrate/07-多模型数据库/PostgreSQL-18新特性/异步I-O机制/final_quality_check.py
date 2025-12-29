#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终质量检查：检查所有文档的完整性、格式、内容质量等
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
print("🔍 最终质量检查报告")
print("=" * 70)

total_docs = len(folders)
perfect_docs = []
issues = []
warnings = []

for folder in folders:
    readme_path = folder / "README.md"

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        doc_issues = []
        doc_warnings = []

        # 1. 检查章节标题
        chapter_match = re.search(r'^##\s+(\d+)\.\s+', content, re.MULTILINE)
        if not chapter_match:
            doc_issues.append("缺少章节标题 (H2)")

        # 2. 检查目录
        toc_match = re.search(r'##\s*📑\s*目录\s*\n(.*?)\n---', content, re.DOTALL)
        if not toc_match:
            doc_issues.append("缺少目录")
        else:
            toc_content = toc_match.group(1)
            # 检查嵌套层级
            if re.search(r'^\s{4,}-', toc_content, re.MULTILINE):
                doc_warnings.append("目录包含嵌套层级")

            # 检查目录项数
            toc_items = re.findall(r'-\s+\[(.+?)\]', toc_content)

            # 3. 检查H3标题
            h3_titles = []
            for line in lines:
                h3_match = re.match(r'^###\s+(.+)$', line)
                if h3_match and not line.startswith('####'):
                    h3_titles.append(h3_match.group(1).strip())

            if len(toc_items) != len(h3_titles):
                doc_warnings.append(f"目录项数({len(toc_items)})与H3标题数({len(h3_titles)})不一致")

        # 4. 检查导航链接
        if not re.search(r'返回.*文档首页', content):
            doc_issues.append("缺少导航链接")

        # 5. 检查内容长度
        content_length = len(content)
        if content_length < 500:
            doc_warnings.append(f"内容较短 ({content_length} 字符)")

        # 6. 检查是否有占位内容
        placeholder_count = content.count('*本节内容待补充*')
        if placeholder_count > 0:
            doc_warnings.append(f"包含 {placeholder_count} 个占位内容")

        # 7. 检查代码块格式
        code_blocks = re.findall(r'```', content)
        if len(code_blocks) % 2 != 0:
            doc_warnings.append("代码块未正确闭合")

        # 8. 检查链接格式
        broken_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for link_text, link_url in broken_links:
            if link_url.startswith('#') and link_url not in content:
                doc_warnings.append(f"可能损坏的内部链接: {link_url}")

        if doc_issues:
            issues.append((folder.name, doc_issues))
        elif doc_warnings:
            warnings.append((folder.name, doc_warnings))
        else:
            perfect_docs.append(folder.name)

    except Exception as e:
        issues.append((folder.name, [f"处理失败: {e}"]))

print(f"\n📊 统计信息:")
print(f"  总文档数: {total_docs}")
print(f"  ✅ 完美文档: {len(perfect_docs)}")
print(f"  ⚠️  有警告的文档: {len(warnings)}")
print(f"  ❌ 有问题的文档: {len(issues)}")

if perfect_docs:
    print(f"\n✅ 完美文档 ({len(perfect_docs)}/{total_docs}):")
    for doc in perfect_docs:
        print(f"  ✅ {doc}")

if warnings:
    print(f"\n⚠️  警告文档 ({len(warnings)}/{total_docs}):")
    for doc, warns in warnings[:10]:
        print(f"  ⚠️  {doc}:")
        for warn in warns:
            print(f"     - {warn}")
    if len(warnings) > 10:
        print(f"  ... 还有 {len(warnings) - 10} 个")

if issues:
    print(f"\n❌ 问题文档 ({len(issues)}/{total_docs}):")
    for doc, probs in issues:
        print(f"  ❌ {doc}:")
        for prob in probs:
            print(f"     - {prob}")

# 计算完成度
completion_rate = (len(perfect_docs) / total_docs) * 100
print(f"\n📈 完成度: {completion_rate:.1f}%")
print(f"  完美文档: {len(perfect_docs)}/{total_docs}")
print(f"  有警告: {len(warnings)}/{total_docs}")
print(f"  有问题: {len(issues)}/{total_docs}")

if len(issues) == 0 and len(warnings) == 0:
    print("\n🎉 完美！所有文档都符合标准！100%完成！")
elif len(issues) == 0:
    print("\n✅ 所有文档结构完整，部分文档有轻微警告")
else:
    print("\n⚠️  发现需要修复的问题")

print("\n" + "=" * 70)
