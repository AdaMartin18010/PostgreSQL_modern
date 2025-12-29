#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Integrate目录下所有文档的未闭合代码块问题
"""
import os
import re
from pathlib import Path

base_path = Path(__file__).parent

print("=" * 70)
print("🔧 修复Integrate目录下所有文档的未闭合代码块问题")
print("=" * 70)

fixed_count = 0
skipped_count = 0

# 跳过报告文件和脚本文件
skip_patterns = [
    'COMPLETION_REPORT',
    'TASK_LIST',
    '00-归档',
    '.py',
]

for md_file in base_path.rglob("*.md"):
    # 跳过报告文件和脚本文件
    rel_path = str(md_file.relative_to(base_path))
    if any(pattern in rel_path for pattern in skip_patterns):
        skipped_count += 1
        continue
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查未闭合的代码块
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            # 在文档末尾添加闭合标记
            if not content.rstrip().endswith('```'):
                content = content.rstrip() + '\n```\n'
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ 修复代码块: {rel_path}")
                fixed_count += 1
    
    except Exception as e:
        print(f"  ❌ 处理失败 {rel_path}: {e}")

print(f"\n已修复 {fixed_count} 个文档的未闭合代码块问题")
print(f"跳过 {skipped_count} 个文件（报告文件等）")
print("=" * 70)
