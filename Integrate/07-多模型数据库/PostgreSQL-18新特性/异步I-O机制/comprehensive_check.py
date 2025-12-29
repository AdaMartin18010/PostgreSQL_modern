#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面完整性检查脚本
检查所有文档的目录、导航、编号、内容等
"""

import os
import re
from pathlib import Path

base_path = Path(__file__).parent

# 获取所有有效文档文件夹
folders = sorted([
    d for d in base_path.iterdir()
    if d.is_dir() and re.match(r'^\d{2}-', d.name) and
    (d / "README.md").exists()
])

print("=" * 70)
print("📋 全面完整性检查报告")
print("=" * 70)

total = len(folders)
stats = {
    'has_toc': 0,
    'has_nav': 0,
    'has_full_nav': 0,
    'has_chapter_title': 0,
    'has_content': 0,
    'line_count_ok': 0,
}

issues = []

for i, folder in enumerate(folders):
    readme_path = folder / "README.md"

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 检查目录
        if re.search(r'##\s*📑\s*目录', content):
            stats['has_toc'] += 1
        else:
            issues.append(f"  ⚠️  {folder.name}: 缺少目录")

        # 检查导航
        if re.search(r'返回.*文档首页', content):
            stats['has_nav'] += 1

            # 检查完整导航
            if re.search(r'上一章节.*下一章节', content):
                stats['has_full_nav'] += 1
            elif i == 0 or i == len(folders) - 1:
                # 首尾文档只有部分导航是正常的
                stats['has_full_nav'] += 1
            else:
                issues.append(f"  ⚠️  {folder.name}: 导航不完整")
        else:
            issues.append(f"  ⚠️  {folder.name}: 缺少导航链接")

        # 检查章节标题
        if re.search(r'^##\s+\d+\.\s+', content, re.MULTILINE):
            stats['has_chapter_title'] += 1
        else:
            issues.append(f"  ⚠️  {folder.name}: 缺少章节标题")

        # 检查内容
        line_count = len(lines)
        if line_count > 50:
            stats['has_content'] += 1
            stats['line_count_ok'] += 1
        elif line_count > 20:
            stats['has_content'] += 1
        else:
            issues.append(f"  ⚠️  {folder.name}: 内容过少 ({line_count} 行)")

    except Exception as e:
        issues.append(f"  ❌ {folder.name}: 读取失败 - {e}")

print(f"\n📚 总文档数: {total}")
print(f"\n✅ 检查结果:")
print(f"  📑 有目录: {stats['has_toc']}/{total} ({stats['has_toc']*100//total}%)")
print(f"  🔗 有导航: {stats['has_nav']}/{total} ({stats['has_nav']*100//total}%)")
print(f"  🔗 完整导航: {stats['has_full_nav']}/{total} ({stats['has_full_nav']*100//total}%)")
print(f"  📝 有章节标题: {stats['has_chapter_title']}/{total} ({stats['has_chapter_title']*100//total}%)")
print(f"  📄 有内容: {stats['has_content']}/{total} ({stats['has_content']*100//total}%)")
print(f"  📏 内容充足: {stats['line_count_ok']}/{total} ({stats['line_count_ok']*100//total}%)")

if issues:
    print(f"\n⚠️  发现 {len(issues)} 个问题:")
    for issue in issues[:20]:
        print(issue)
    if len(issues) > 20:
        print(f"  ... 还有 {len(issues) - 20} 个问题")
else:
    print("\n✅ 未发现问题！所有文档都完整！")

print("\n" + "=" * 70)

# 计算完成度
completion = (
    stats['has_toc'] + stats['has_nav'] + stats['has_chapter_title'] +
    stats['has_content']
) / (total * 4) * 100

print(f"📊 总体完成度: {completion:.1f}%")
print("=" * 70)

if completion >= 100:
    print("🎊 恭喜！所有工作已100%完成！")
elif completion >= 95:
    print("✅ 优秀！文档质量很高！")
elif completion >= 90:
    print("👍 良好！大部分工作已完成！")
else:
    print("⚠️  还有改进空间")

print("=" * 70)
