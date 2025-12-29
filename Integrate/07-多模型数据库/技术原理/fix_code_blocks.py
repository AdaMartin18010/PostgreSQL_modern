#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并修复未闭合的代码块
"""
import re
from pathlib import Path

base_path = Path(__file__).parent

print("=" * 70)
print("🔧 检查并修复未闭合的代码块")
print("=" * 70)

for md_file in base_path.glob("*.md"):
    if md_file.name in ["check_document.py", "fix_toc_format.py", "fix_code_blocks.py"]:
        continue

    print(f"\n📄 处理文档: {md_file.name}")

    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 统计代码块
        code_block_count = content.count('```')

        if code_block_count % 2 == 0:
            print(f"  ✅ 代码块数量正常: {code_block_count // 2} 个代码块")
        else:
            print(f"  ⚠️  发现未闭合的代码块: {code_block_count} 个标记（应为偶数）")

            # 查找最后一个代码块开始
            last_code_start = -1
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().startswith('```'):
                    last_code_start = i
                    break

            if last_code_start >= 0:
                # 检查是否闭合
                code_blocks_after = content[content.rfind('```'):].count('```')
                if code_blocks_after == 1:
                    print(f"  🔧 修复: 在文档末尾添加代码块结束标记")
                    # 在文档末尾添加闭合标记
                    if not content.rstrip().endswith('```'):
                        content = content.rstrip() + '\n```\n'
                        with open(md_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"  ✅ 修复完成")
                    else:
                        print(f"  ℹ️  文档末尾已有代码块标记，但可能格式不正确")

    except Exception as e:
        print(f"  ❌ 处理失败: {e}")

print("\n" + "=" * 70)
print("检查完成")
print("=" * 70)
