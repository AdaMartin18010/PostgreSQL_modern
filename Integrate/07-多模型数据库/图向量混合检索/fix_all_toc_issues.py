#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面修复图向量混合检索文档的所有TOC问题
"""
import os
import re
from pathlib import Path

base_path = Path(__file__).parent

print("=" * 70)
print("🔧 全面修复图向量混合检索文档的所有TOC问题")
print("=" * 70)

fixed_nested = 0
fixed_mismatch = 0

for md_file in base_path.glob("*.md"):
    print(f"\n📄 处理文档: {md_file.name}")

    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 提取所有三级标题（###），不包括四级标题（####）
        h3_titles = []
        for i, line in enumerate(lines):
            h3_match = re.match(r'^###\s+(.+)$', line)
            if h3_match and not line.startswith('####'):
                full_title = h3_match.group(1).strip()
                h3_titles.append(full_title)

        if not h3_titles:
            print(f"  ⚠️  跳过: 没有找到三级标题")
            continue

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

        toc_markdown = "## 📑 目录\n\n" + "\n".join(toc_items) + "\n\n---\n\n"

        # 查找并替换目录
        toc_pattern = r'##\s*📑\s*目录\s*\n.*?\n---\s*\n'
        if re.search(toc_pattern, content, re.DOTALL):
            toc_match = re.search(toc_pattern, content, re.DOTALL)
            if toc_match:
                current_toc = toc_match.group(0)

                # 检查是否有嵌套
                has_nested = bool(re.search(r'^\s{2,}-', current_toc, re.MULTILINE))

                # 检查TOC项数
                current_toc_items = len([l for l in current_toc.split('\n') if l.strip().startswith('-')])

                needs_fix = False
                if has_nested:
                    needs_fix = True
                    fixed_nested += 1

                if current_toc_items != len(h3_titles):
                    needs_fix = True
                    fixed_mismatch += 1

                if needs_fix:
                    new_content = re.sub(toc_pattern, toc_markdown, content, flags=re.DOTALL)

                    if new_content != content:
                        with open(md_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        issues = []
                        if has_nested:
                            issues.append("嵌套TOC")
                        if current_toc_items != len(h3_titles):
                            issues.append(f"TOC项数不匹配({current_toc_items}->{len(h3_titles)})")
                        print(f"  ✅ 修复完成: {', '.join(issues)}, H3数: {len(h3_titles)}")
                    else:
                        print(f"  ℹ️  无需修复")
                else:
                    print(f"  ✅ TOC格式正确: {len(h3_titles)} 个三级标题")
        else:
            print(f"  ⚠️  跳过: 没有找到目录")

    except Exception as e:
        print(f"  ❌ 处理失败: {e}")

print(f"\n已修复 {fixed_nested} 个文档的嵌套TOC问题")
print(f"已修复 {fixed_mismatch} 个文档的TOC项数不匹配问题")
print("=" * 70)
