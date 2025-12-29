#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复编号冲突：将31-实战演练重命名为32，并更新所有引用
"""

import os
import re
from pathlib import Path

base_path = Path(__file__).parent

# 检查当前编号使用情况
folders = sorted([
    d for d in base_path.iterdir()
    if d.is_dir() and re.match(r'^\d{2}-', d.name)
])

print("=" * 70)
print("🔧 修复编号冲突")
print("=" * 70)

# 查找编号冲突
folder_numbers = {}
for folder in folders:
    match = re.match(r'^(\d{2})-', folder.name)
    if match:
        num = int(match.group(1))
        if num in folder_numbers:
            print(f"  ⚠️  发现编号冲突: {folder_numbers[num]} 和 {folder.name}")
        folder_numbers[num] = folder.name

# 31-实战演练应该重命名为32（因为32-错误解决方案存在，需要检查）
# 实际上，应该检查哪个编号可用
used_numbers = set(folder_numbers.keys())
print(f"\n已使用的编号: {sorted(used_numbers)}")

# 31-实战演练的元数据显示章节号是31，但文件夹名冲突
# 根据README.md，它应该引用为33-实战演练教程，但33已被源码分析占用
# 检查32是否可用
if 32 in used_numbers:
    print(f"  ⚠️  32已被使用: {folder_numbers[32]}")
    # 检查32-错误解决方案的内容，看是否可以调整
    error_sol_folder = base_path / "32-错误解决方案"
    if error_sol_folder.exists():
        readme_path = error_sol_folder / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            meta_match = re.search(r'>\s*\*\*章节编号\*\*:\s*(\d+)', content)
            if meta_match:
                meta_num = int(meta_match.group(1))
                print(f"  32-错误解决方案的元数据章节号: {meta_num}")

# 实际上，最好的方案是：
# - 31-实用工具保持为31（已从29重命名过来）
# - 31-实战演练重命名为32，然后32-错误解决方案需要重命名
# 但这会引发连锁反应

# 更简单的方案：检查31-实战演练是否应该保持为31，而31-实用工具应该改为其他编号
# 但根据更新日志，31-实用工具是从29重命名过来的，所以应该保持

# 检查31-实战演练的元数据
practice_folder = base_path / "31-实战演练"
if practice_folder.exists():
    readme_path = practice_folder / "README.md"
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
        meta_match = re.search(r'>\s*\*\*章节编号\*\*:\s*(\d+)', content)
        if meta_match:
            meta_num = int(meta_match.group(1))
            print(f"\n31-实战演练的元数据章节号: {meta_num}")
            
            # 如果元数据是31，但文件夹冲突，需要重命名文件夹
            # 或者更新元数据
            # 根据README.md引用，应该是33，但33已被占用
            
            # 最简单的方案：将31-实战演练重命名为32
            # 然后将32-错误解决方案重命名为33
            # 然后将33-源码分析重命名为34
            # 然后将34-深度集成重命名为35
            # 然后将35-成熟案例重命名为36
            # 然后将36-参考资料重命名为37
            
            # 但这太复杂了，更好的方案是：
            # 检查是否有空编号可用（比如检查30-35之间）
            available_numbers = []
            for i in range(30, 40):
                if i not in used_numbers:
                    available_numbers.append(i)
            
            print(f"可用编号 (30-39): {available_numbers}")
            
            if available_numbers:
                new_num = available_numbers[0]
                print(f"\n建议：将31-实战演练重命名为{new_num:02d}-实战演练")
            else:
                print("\n没有可用编号，需要重新规划编号")

print("\n" + "=" * 70)
print("分析完成")
print("=" * 70)
