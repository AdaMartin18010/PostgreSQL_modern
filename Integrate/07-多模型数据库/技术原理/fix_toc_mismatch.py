#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确修复技术原理文档的TOC项数与H3标题数不匹配问题
"""
import os
import re
from pathlib import Path

base_path = Path(__file__).parent

print("=" * 70)
print("🔧 精确修复技术原理文档的TOC项数与H3标题数不匹配")
print("=" * 70)

for md_file in base_path.glob("*.md"):
    if md_file.name in ["check_document.py", "fix_toc_format.py", "fix_code_blocks.py", "fix_toc_mismatch.py"]:
        continue
    
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
        
        # 生成新的目录（只包含三级标题）
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
            # 检查当前TOC项数
            toc_match = re.search(toc_pattern, content, re.DOTALL)
            if toc_match:
                current_toc = toc_match.group(0)
                current_toc_items = len([l for l in current_toc.split('\n') if l.strip().startswith('-')])
                
                if current_toc_items != len(h3_titles):
                    new_content = re.sub(toc_pattern, toc_markdown, content, flags=re.DOTALL)
                    
                    if new_content != content:
                        with open(md_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"  ✅ 修复完成: TOC项数 {current_toc_items} -> {len(h3_titles)}, H3数: {len(h3_titles)}")
                    else:
                        print(f"  ℹ️  无需修复")
                else:
                    print(f"  ✅ TOC项数与H3标题数匹配: {len(h3_titles)}")
        else:
            print(f"  ⚠️  跳过: 没有找到目录")
    
    except Exception as e:
        print(f"  ❌ 处理失败: {e}")

print("\n" + "=" * 70)
print("修复完成")
print("=" * 70)
