#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极验证：全面检查文档的所有方面
"""

import os
import re
from pathlib import Path
from collections import defaultdict

base_path = Path(__file__).parent

folders = sorted([
    d for d in base_path.iterdir()
    if d.is_dir() and re.match(r'^\d{2}-', d.name) and
    (d / "README.md").exists()
])

print("=" * 70)
print("🔍 终极验证报告")
print("=" * 70)

total_docs = len(folders)
perfect_docs = []
all_issues = defaultdict(list)
all_warnings = defaultdict(list)

for folder in folders:
    readme_path = folder / "README.md"
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        doc_issues = []
        doc_warnings = []
        
        # 1. 基础结构检查
        if not re.search(r'^##\s+\d+\.\s+', content, re.MULTILINE):
            doc_issues.append("缺少章节标题")
        
        if not re.search(r'##\s*📑\s*目录', content):
            doc_issues.append("缺少目录")
        
        if not re.search(r'返回.*文档首页', content):
            doc_issues.append("缺少导航链接")
        
        # 2. 目录格式检查
        toc_match = re.search(r'##\s*📑\s*目录\s*\n(.*?)\n---', content, re.DOTALL)
        if toc_match:
            toc_content = toc_match.group(1)
            # 检查嵌套
            if re.search(r'^\s{4,}-', toc_content, re.MULTILINE):
                doc_warnings.append("目录包含嵌套层级")
            
            # 检查目录项
            toc_items = re.findall(r'-\s+\[(.+?)\]', toc_content)
            h3_titles = []
            for line in lines:
                h3_match = re.match(r'^###\s+(.+)$', line)
                if h3_match and not line.startswith('####'):
                    h3_titles.append(h3_match.group(1).strip())
            
            if len(toc_items) != len(h3_titles):
                doc_warnings.append(f"目录项数({len(toc_items)})≠H3标题数({len(h3_titles)})")
        
        # 3. 内容质量检查
        if '*本节内容待补充*' in content:
            placeholder_count = content.count('*本节内容待补充*')
            doc_warnings.append(f"包含{placeholder_count}个占位内容")
        
        if len(content) < 500:
            doc_warnings.append(f"内容较短({len(content)}字符)")
        
        # 4. 代码块检查
        code_blocks = re.findall(r'```', content)
        if len(code_blocks) % 2 != 0:
            doc_warnings.append("代码块未正确闭合")
        
        # 5. 链接检查
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for link_text, link_url in links:
            if link_url.startswith('#') and len(link_url) > 1:
                anchor = link_url[1:]
                # 检查锚点是否存在
                anchor_found = False
                for line in lines:
                    if re.match(r'^#{2,3}\s+', line):
                        line_anchor = re.sub(r'[^\w\s-]', '', line.lower())
                        line_anchor = re.sub(r'[-\s]+', '-', line_anchor)
                        if anchor in line_anchor or line_anchor.endswith(anchor):
                            anchor_found = True
                            break
                if not anchor_found:
                    doc_warnings.append(f"可能损坏的内部链接: {link_url}")
        
        # 6. 格式一致性检查
        # 检查章节编号一致性
        chapter_match = re.search(r'^##\s+(\d+)\.\s+', content, re.MULTILINE)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            folder_num_match = re.match(r'^(\d{2})-', folder.name)
            if folder_num_match:
                folder_num = int(folder_num_match.group(1))
                if chapter_num != folder_num:
                    doc_warnings.append(f"章节号({chapter_num})与文件夹号({folder_num})不一致")
        
        if doc_issues:
            all_issues[folder.name] = doc_issues
        elif doc_warnings:
            all_warnings[folder.name] = doc_warnings
        else:
            perfect_docs.append(folder.name)
    
    except Exception as e:
        all_issues[folder.name] = [f"处理失败: {e}"]

print(f"\n📊 统计信息:")
print(f"  总文档数: {total_docs}")
print(f"  ✅ 完美文档: {len(perfect_docs)}")
print(f"  ⚠️  有警告的文档: {len(all_warnings)}")
print(f"  ❌ 有问题的文档: {len(all_issues)}")

if perfect_docs:
    print(f"\n✅ 完美文档 ({len(perfect_docs)}/{total_docs}):")
    for doc in perfect_docs:
        print(f"  ✅ {doc}")

if all_warnings:
    print(f"\n⚠️  警告文档 ({len(all_warnings)}/{total_docs}):")
    for doc, warns in all_warnings.items():
        print(f"  ⚠️  {doc}:")
        for warn in warns:
            print(f"     - {warn}")

if all_issues:
    print(f"\n❌ 问题文档 ({len(all_issues)}/{total_docs}):")
    for doc, probs in all_issues.items():
        print(f"  ❌ {doc}:")
        for prob in probs:
            print(f"     - {prob}")

completion_rate = (len(perfect_docs) / total_docs) * 100
print(f"\n📈 完成度: {completion_rate:.1f}%")

if len(all_issues) == 0 and len(all_warnings) == 0:
    print("\n🎉 完美！所有文档都符合标准！100%完成！")
elif len(all_issues) == 0:
    print("\n✅ 所有文档结构完整，部分文档有轻微警告")
else:
    print("\n⚠️  发现需要修复的问题")

print("\n" + "=" * 70)
