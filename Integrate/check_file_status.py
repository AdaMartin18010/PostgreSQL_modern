#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查文件状态"""
from pathlib import Path
import re

dirs = ['03-核心能力', '04-应用场景', '05-实践案例', '06-对比分析']
base = Path('10-AI与机器学习')

for d in dirs:
    p = base / d
    if not p.exists():
        continue
    files = list(p.glob('*.md'))
    print(f'\n{d}:')
    for f in files:
        try:
            content = f.read_text(encoding='utf-8')
            lines = len(content.split('\n'))
            h3 = len(re.findall(r'^###\s+', content, re.MULTILINE))
            status = '✅' if lines > 300 else '⚠️'
            print(f'  {status} {f.name}: {lines}行, {h3}个H3')
        except:
            print(f'  ❌ {f.name}: 读取失败')
