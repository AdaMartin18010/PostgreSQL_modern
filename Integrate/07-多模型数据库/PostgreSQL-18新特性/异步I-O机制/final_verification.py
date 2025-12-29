#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终完成验证报告
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

total = len(folders)
with_toc = 0
with_nav = 0

for folder in folders:
    readme_path = folder / "README.md"
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if re.search(r'##\s*📑\s*目录', content):
            with_toc += 1

        if re.search(r'返回.*文档首页', content):
            with_nav += 1
    except:
        pass

print("=" * 70)
print("🎉 最终完成验证报告")
print("=" * 70)
print(f"📚 总有效文档数: {total}")
print(f"📑 有目录的文档: {with_toc} ({with_toc*100//total}%)")
print(f"🔗 有导航的文档: {with_nav} ({with_nav*100//total}%)")
print("=" * 70)

if with_toc == total and with_nav == total:
    print("✅ 完美！所有文档都已完成！")
    print("✅ 目录覆盖率: 100%")
    print("✅ 导航覆盖率: 100%")
    print("✅ 文档完整性: 100%")
    print("=" * 70)
    print("🎊 恭喜！所有工作已全部完成！")
    print("=" * 70)
else:
    print("⚠️  部分文档需要完善")
    print("=" * 70)
