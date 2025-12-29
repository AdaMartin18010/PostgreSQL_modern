#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重命名31-实战演练为37-实战演练，并更新所有引用
"""

import os
import re
from pathlib import Path

base_path = Path(__file__).parent

old_folder_name = "31-实战演练"
new_folder_name = "37-实战演练"
old_num = "31"
new_num = "37"

print("=" * 70)
print(f"🔄 重命名 {old_folder_name} → {new_folder_name}")
print("=" * 70)

# 第一步：重命名文件夹
old_folder = base_path / old_folder_name
new_folder = base_path / new_folder_name

if old_folder.exists() and not new_folder.exists():
    old_folder.rename(new_folder)
    print(f"  ✅ 文件夹已重命名: {old_folder_name} → {new_folder_name}")
else:
    if new_folder.exists():
        print(f"  ⚠️  目标文件夹已存在: {new_folder_name}")
    if not old_folder.exists():
        print(f"  ⚠️  源文件夹不存在: {old_folder_name}")

# 第二步：更新文件夹内的README.md
readme_path = new_folder / "README.md"
if readme_path.exists():
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新章节编号元数据
    content = re.sub(
        r'>\s*\*\*章节编号\*\*:\s*31',
        f'> **章节编号**: {new_num}',
        content
    )
    
    # 更新H1标题
    content = re.sub(
        r'^#\s+31\.\s+实战演练教程',
        f'# {new_num}. 实战演练教程',
        content,
        flags=re.MULTILINE
    )
    
    # 更新H2章节标题
    content = re.sub(
        r'^##\s+31\.\s+实战演练教程',
        f'## {new_num}. 实战演练教程',
        content,
        flags=re.MULTILINE
    )
    
    # 更新所有三级标题的编号（31.x → 37.x）
    content = re.sub(
        r'^###\s+31\.(\d+)',
        rf'### {new_num}.\1',
        content,
        flags=re.MULTILINE
    )
    
    # 更新目录中的链接
    content = re.sub(
        r'\[31\.\s+实战演练教程\]',
        f'[{new_num}. 实战演练教程]',
        content
    )
    
    # 更新目录中的编号引用
    content = re.sub(
        r'- \[31\.(\d+)',
        rf'- [{new_num}.\1',
        content
    )
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ 已更新 {new_folder_name}/README.md")

# 第三步：更新主README.md中的引用
main_readme = base_path / "README.md"
if main_readme.exists():
    with open(main_readme, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新文件夹引用
    content = re.sub(
        r'31-实战演练',
        new_folder_name,
        content
    )
    
    # 更新链接文本（如果引用的是33-实战演练教程，也更新）
    content = re.sub(
        r'33-实战演练教程',
        f'{new_num}-实战演练教程',
        content
    )
    
    with open(main_readme, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ 已更新主README.md")

# 第四步：更新所有其他文档中的导航链接
folders = [
    d for d in base_path.iterdir()
    if d.is_dir() and re.match(r'^\d{2}-', d.name) and
    (d / "README.md").exists() and d.name != new_folder_name
]

updated_count = 0
for folder in folders:
    readme_path = folder / "README.md"
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 更新导航链接中的文件夹名
        content = re.sub(
            rf'\(\.\./{re.escape(old_folder_name)}/README\.md\)',
            f'(../{new_folder_name}/README.md)',
            content
        )
        
        # 更新章节号引用（如果提到31.实战演练）
        content = re.sub(
            r'31\.\s*实战演练',
            f'{new_num}. 实战演练',
            content
        )
        
        if content != original_content:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            updated_count += 1
            print(f"  ✅ 已更新 {folder.name}/README.md")
    
    except Exception as e:
        print(f"  ⚠️  更新 {folder.name} 时出错: {e}")

print(f"\n  ✅ 共更新了 {updated_count} 个文档的引用")

print("\n" + "=" * 70)
print("重命名完成")
print("=" * 70)
