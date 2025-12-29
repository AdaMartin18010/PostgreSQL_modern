#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描Integrate目录下需要补充内容的文件"""

import os
import re

def scan_files():
    short_files = []

    # 已完成的目录（跳过）
    completed_dirs = [
        '10-AI与机器学习/03-核心能力',
        '10-AI与机器学习/04-应用场景',
        '10-AI与机器学习/05-实践案例',
        '10-AI与机器学习/06-对比分析',
        '10-AI与机器学习/07-实施路径',
        '10-AI与机器学习/08-未来趋势',
        '20-故障诊断案例',
        '19-实战案例',
    ]

    for root, dirs, files in os.walk('.'):
        if 'node_modules' in root or '.git' in root or '归档' in root or '00-归档' in root:
            continue

        # 跳过已完成的目录
        skip = False
        for completed_dir in completed_dirs:
            if completed_dir.replace('/', os.sep) in root:
                skip = True
                break
        if skip:
            continue

        for f in files:
            if f.endswith('.md') and f not in ['README.md', 'CONTENT_ENHANCEMENT_TASKS.md']:
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                        lines = len(content.split('\n'))
                        h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))

                        # 判断是否需要补充：少于200行，或少于300行且H3少于8个
                        if lines < 200 or (lines < 300 and h3_count < 8):
                            short_files.append((filepath.replace(os.sep, '/'), lines, h3_count))
                except Exception as e:
                    pass

    print(f'需要补充的文件数: {len(short_files)}')
    print('\n需要补充的文件列表（前30个）:')
    for f, lines, h3 in sorted(short_files)[:30]:
        print(f'  {f}: {lines}行, {h3}个H3')

    return short_files

if __name__ == '__main__':
    scan_files()
