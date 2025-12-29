#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复所有TOC项数不匹配问题
"""
import os
import re
from pathlib import Path

base_path = Path(__file__).parent

print("=" * 70)
print("🔧 最终修复所有TOC项数不匹配问题")
print("=" * 70)

fixed_count = 0

# 需要处理的目录
target_dirs = [
    'JSONB时序向量',
    'PostgreSQL-18新特性',
    '空间数据',
    '图向量混合检索',
    '技术原理',
]

for target_dir in target_dirs:
    dir_path = base_path / target_dir
    if not dir_path.exists():
        continue
    
    print(f"\n📁 处理目录: {target_dir}")
    
    for md_file in dir_path.rglob("*.md"):
        # 跳过README.md（可能不需要TOC）
        if md_file.name == 'README.md' and '参考资料' not in str(md_file):
            continue
        
        rel_path = md_file.relative_to(base_path)
        
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
                continue
            
            # 检查并修复TOC
            toc_pattern = r'##\s*📑\s*目录\s*\n.*?\n---\s*\n'
            if re.search(toc_pattern, content, re.DOTALL):
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
                
                toc_match = re.search(toc_pattern, content, re.DOTALL)
                if toc_match:
                    current_toc = toc_match.group(0)
                    
                    # 检查TOC项数
                    current_toc_items = len([l for l in current_toc.split('\n') if l.strip().startswith('-')])
                    
                    if current_toc_items != len(h3_titles):
                        new_content = re.sub(toc_pattern, toc_markdown, content, flags=re.DOTALL)
                        
                        if new_content != content:
                            with open(md_file, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"  ✅ 修复: {rel_path} (TOC项数: {current_toc_items} -> {len(h3_titles)}, H3数: {len(h3_titles)})")
                            fixed_count += 1
        
        except Exception as e:
            print(f"  ❌ 处理失败 {rel_path}: {e}")

print(f"\n已修复 {fixed_count} 个文档的TOC项数不匹配问题")
print("=" * 70)
