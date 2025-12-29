#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复图向量混合检索文档的目录格式，确保目录只包含三级标题
"""
import os
import re
from pathlib import Path

base_path = Path(__file__).parent

print("=" * 70)
print("🔧 修复图向量混合检索文档的目录格式")
print("=" * 70)

for md_file in base_path.glob("*.md"):
    print(f"\n📄 处理文档: {md_file.name}")
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # 提取所有三级标题（###），不包括四级标题（####）
        h3_titles = []
        for line in lines:
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
            new_content = re.sub(toc_pattern, toc_markdown, content, flags=re.DOTALL)
            
            # 检查是否有变化
            if new_content != content:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  ✅ 修复完成: {len(h3_titles)} 个三级标题")
            else:
                print(f"  ℹ️  无需修复")
        else:
            print(f"  ⚠️  跳过: 没有找到目录")
    
    except Exception as e:
        print(f"  ❌ 处理失败: {e}")

print("\n" + "=" * 70)
print("修复完成")
print("=" * 70)
