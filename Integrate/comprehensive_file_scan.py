#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全面扫描Integrate目录下需要补充内容的文件"""

import os
import re
from collections import defaultdict

def scan_all_files():
    """扫描所有需要补充的文件"""
    files_by_category = defaultdict(list)
    all_short_files = []

    # 排除的目录
    excluded_dirs = [
        'node_modules', '.git', '归档', '00-归档',
        '__pycache__', '.pytest_cache', 'venv', 'env'
    ]

    # 排除的文件
    excluded_files = [
        'README.md', 'CONTENT_ENHANCEMENT_TASKS.md',
        'PROGRESS_REPORT.md', 'scan_short_files.py',
        'comprehensive_file_scan.py', 'check_file_status.py',
        'comprehensive_scan_all.py', 'scan_empty_content.py',
        'fix_all_nested_toc_comprehensive.py', 'fix_unclosed_code_blocks.py'
    ]

    # 已完成的目录（可以跳过或降低优先级）
    completed_dirs = [
        '10-AI与机器学习/03-核心能力',
        '10-AI与机器学习/04-应用场景',
        '10-AI与机器学习/05-实践案例',
        '10-AI与机器学习/06-对比分析',
        '10-AI与机器学习/07-实施路径',
        '10-AI与机器学习/08-未来趋势',
        '20-故障诊断案例',
        '19-实战案例',
        '16-应用设计与开发/测试与质量保证',
    ]

    for root, dirs, files in os.walk('.'):
        # 跳过排除的目录
        if any(excluded in root for excluded in excluded_dirs):
            continue

        # 检查是否在已完成的目录中
        is_completed = any(completed in root for completed in completed_dirs)

        for f in files:
            if not f.endswith('.md'):
                continue

            if f in excluded_files:
                continue

            filepath = os.path.join(root, f)
            rel_path = filepath.replace(os.sep, '/').replace('./', '')

            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    lines = len(content.split('\n'))
                    h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))

                    # 判断是否需要补充
                    needs_enhancement = False
                    priority = 'P1'

                    if lines < 200:
                        needs_enhancement = True
                        priority = 'P0' if not is_completed else 'P1'
                    elif lines < 300 and h3_count < 8:
                        needs_enhancement = True
                        priority = 'P1' if not is_completed else 'P2'
                    elif lines < 400 and h3_count < 10:
                        needs_enhancement = True
                        priority = 'P2'

                    if needs_enhancement:
                        # 提取目录分类
                        parts = rel_path.split('/')
                        if len(parts) > 1:
                            category = parts[0]
                        else:
                            category = '根目录'

                        file_info = {
                            'path': rel_path,
                            'lines': lines,
                            'h3_count': h3_count,
                            'priority': priority,
                            'category': category,
                            'is_completed_dir': is_completed
                        }

                        files_by_category[category].append(file_info)
                        all_short_files.append(file_info)

            except Exception as e:
                pass

    return files_by_category, all_short_files

def generate_task_report(files_by_category, all_short_files):
    """生成任务报告"""
    print("=" * 80)
    print("📊 PostgreSQL文档补充任务全面梳理报告")
    print("=" * 80)
    print()

    print(f"📈 总体统计:")
    print(f"  总文件数: {len(all_short_files)}")

    # 按优先级统计
    p0_count = sum(1 for f in all_short_files if f['priority'] == 'P0')
    p1_count = sum(1 for f in all_short_files if f['priority'] == 'P1')
    p2_count = sum(1 for f in all_short_files if f['priority'] == 'P2')

    print(f"  P0优先级（<200行）: {p0_count}个")
    print(f"  P1优先级（200-300行且H3<8）: {p1_count}个")
    print(f"  P2优先级（300-400行且H3<10）: {p2_count}个")
    print()

    print("📁 按目录分类统计:")
    for category in sorted(files_by_category.keys()):
        files = files_by_category[category]
        p0 = sum(1 for f in files if f['priority'] == 'P0')
        p1 = sum(1 for f in files if f['priority'] == 'P1')
        p2 = sum(1 for f in files if f['priority'] == 'P2')
        print(f"  {category}: {len(files)}个文件 (P0:{p0}, P1:{p1}, P2:{p2})")
    print()

    print("=" * 80)
    print("📋 详细文件列表（按优先级排序）")
    print("=" * 80)
    print()

    # 按优先级和目录排序
    sorted_files = sorted(all_short_files, key=lambda x: (
        x['priority'],
        x['category'],
        x['lines']
    ))

    current_priority = None
    current_category = None

    for file_info in sorted_files:
        if file_info['priority'] != current_priority:
            current_priority = file_info['priority']
            print(f"\n## {current_priority}优先级文件")
            print()

        if file_info['category'] != current_category:
            current_category = file_info['category']
            print(f"\n### {current_category}")
            print()

        status = "✅" if file_info['is_completed_dir'] else "⏳"
        print(f"  {status} {file_info['path']}: {file_info['lines']}行, {file_info['h3_count']}个H3")

    print()
    print("=" * 80)
    print("✅ 扫描完成")
    print("=" * 80)

    return sorted_files

if __name__ == '__main__':
    files_by_category, all_short_files = scan_all_files()
    sorted_files = generate_task_report(files_by_category, all_short_files)

    # 保存到文件
    with open('COMPREHENSIVE_SCAN_RESULT.md', 'w', encoding='utf-8') as f:
        f.write("# PostgreSQL文档补充任务全面梳理结果\n\n")
        f.write(f"总文件数: {len(all_short_files)}\n\n")

        f.write("## 按优先级统计\n\n")
        p0_count = sum(1 for file_info in all_short_files if file_info['priority'] == 'P0')
        p1_count = sum(1 for file_info in all_short_files if file_info['priority'] == 'P1')
        p2_count = sum(1 for file_info in all_short_files if file_info['priority'] == 'P2')
        f.write(f"- P0优先级: {p0_count}个\n")
        f.write(f"- P1优先级: {p1_count}个\n")
        f.write(f"- P2优先级: {p2_count}个\n\n")

        f.write("## 详细文件列表\n\n")
        current_priority = None
        for file_info in sorted_files:
            if file_info['priority'] != current_priority:
                current_priority = file_info['priority']
                f.write(f"\n### {current_priority}优先级\n\n")
            f.write(f"- `{file_info['path']}`: {file_info['lines']}行, {file_info['h3_count']}个H3\n")

    print(f"\n📄 结果已保存到: COMPREHENSIVE_SCAN_RESULT.md")
