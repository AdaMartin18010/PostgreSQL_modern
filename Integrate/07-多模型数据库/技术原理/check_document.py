#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查技术原理文档的质量
"""

import os
import re
from pathlib import Path

base_path = Path(__file__).parent

print("=" * 70)
print("🔍 技术原理文档质量检查")
print("=" * 70)

for md_file in base_path.glob("*.md"):
    print(f"\n📄 检查文档: {md_file.name}")
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # 检查目录
        toc_match = re.search(r'##\s*📑\s*目录\s*\n(.*?)\n---', content, re.DOTALL)
        if toc_match:
            toc_content = toc_match.group(1)
            toc_items = re.findall(r'-\s+\[(.+?)\]', toc_content)
            
            # 检查嵌套层级
            nested_count = len(re.findall(r'^\s{4,}-', toc_content, re.MULTILINE))
            
            # 统计H3标题
            h3_titles = []
            for line in lines:
                h3_match = re.match(r'^###\s+(.+)$', line)
                if h3_match and not line.startswith('####'):
                    h3_titles.append(h3_match.group(1).strip())
            
            print(f"  📑 目录项数: {len(toc_items)}")
            print(f"  📝 H3标题数: {len(h3_titles)}")
            print(f"  🔗 嵌套层级: {nested_count}")
            
            if nested_count > 0:
                print(f"  ⚠️  警告: 目录包含嵌套层级")
            
            if len(toc_items) != len(h3_titles):
                print(f"  ⚠️  警告: 目录项数({len(toc_items)})与H3标题数({len(h3_titles)})不一致")
            else:
                print(f"  ✅ 目录项数与H3标题数匹配")
        else:
            print(f"  ⚠️  警告: 缺少目录")
        
        # 检查章节标题
        h2_count = len(re.findall(r'^##\s+\d+\.\s+', content, re.MULTILINE))
        if h2_count == 0:
            h2_count = len(re.findall(r'^##\s+[^📑]', content, re.MULTILINE))
        print(f"  📚 H2章节数: {h2_count}")
        
        # 检查代码块
        code_blocks = re.findall(r'```', content)
        if len(code_blocks) % 2 != 0:
            print(f"  ⚠️  警告: 代码块未正确闭合")
        else:
            print(f"  ✅ 代码块格式正确 ({len(code_blocks) // 2}个)")
    
    except Exception as e:
        print(f"  ❌ 处理失败: {e}")

print("\n" + "=" * 70)
print("检查完成")
print("=" * 70)
