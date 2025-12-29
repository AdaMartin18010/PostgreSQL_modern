#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查剩余文件夹状态
"""

import os
import re
from pathlib import Path

base_path = Path(__file__).parent

folders = sorted([d for d in base_path.iterdir() if d.is_dir() and re.match(r'^\d{2}-', d.name)])

print("=" * 70)
print("📁 文件夹状态检查")
print("=" * 70)

valid = []
empty = []

for folder in folders:
    if (folder / "README.md").exists():
        valid.append(folder.name)
    else:
        empty.append(folder.name)

print(f"\n总文件夹数: {len(folders)}")
print(f"有效文档数: {len(valid)}")
print(f"无内容文件夹数: {len(empty)}")

if empty:
    print("\n无内容文件夹:")
    for f in empty:
        print(f"  - {f}")

print("\n" + "=" * 70)
