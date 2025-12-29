#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面扫描Integrate目录，识别没有实质内容的文件
"""
import os
import re
from pathlib import Path
from collections import defaultdict

class ContentScanner:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.issues = defaultdict(list)
        self.stats = {
            'total_files': 0,
            'empty_files': 0,
            'short_files': 0,
            'placeholder_only': 0,
            'toc_only': 0,
            'no_content': 0,
        }

    def analyze_content(self, content, file_path):
        """分析文件内容"""
        lines = content.split('\n')
        non_empty_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

        # 检查是否只有TOC
        toc_pattern = r'^##\s*📑\s*目录|^##\s*📋\s*目录'
        has_toc = bool(re.search(toc_pattern, content, re.MULTILINE))

        # 检查占位符
        has_placeholder = '*待补充*' in content or '*本节内容待补充*' in content or 'TODO' in content

        # 检查代码块
        code_blocks = content.count('```')

        # 统计实际内容行数（排除TOC、空行、注释）
        content_lines = []
        in_toc = False
        for line in lines:
            if re.match(toc_pattern, line):
                in_toc = True
            elif in_toc and (line.strip() == '---' or line.startswith('##')):
                in_toc = False
            elif not in_toc and line.strip() and not line.strip().startswith('>') and not line.strip().startswith('---'):
                content_lines.append(line)

        actual_content = len([l for l in content_lines if len(l.strip()) > 10])

        return {
            'total_lines': len(lines),
            'non_empty_lines': len(non_empty_lines),
            'actual_content': actual_content,
            'has_toc': has_toc,
            'has_placeholder': has_placeholder,
            'code_blocks': code_blocks,
        }

    def scan_file(self, file_path):
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return

        self.stats['total_files'] += 1
        rel_path = str(file_path.relative_to(self.root_dir))

        # 跳过报告文件和脚本文件
        if any(x in rel_path for x in ['COMPLETION_REPORT', 'TASK_LIST', '.py', '00-归档', 'README.md']):
            return

        analysis = self.analyze_content(content, file_path)

        # 判断问题类型
        if analysis['total_lines'] == 0:
            self.stats['empty_files'] += 1
            self.issues['empty'].append(rel_path)
        elif analysis['total_lines'] < 50 and analysis['actual_content'] < 20:
            self.stats['short_files'] += 1
            self.issues['short'].append(f"{rel_path}: {analysis['total_lines']}行, 实际内容{analysis['actual_content']}行")
        elif analysis['has_toc'] and analysis['actual_content'] < 30:
            self.stats['toc_only'] += 1
            self.issues['toc_only'].append(f"{rel_path}: TOC存在但内容不足({analysis['actual_content']}行)")
        elif analysis['has_placeholder'] and analysis['actual_content'] < 50:
            self.stats['placeholder_only'] += 1
            self.issues['placeholder'].append(f"{rel_path}: 有占位符，内容不足({analysis['actual_content']}行)")
        elif analysis['actual_content'] < 30:
            self.stats['no_content'] += 1
            self.issues['no_content'].append(f"{rel_path}: 实际内容不足({analysis['actual_content']}行)")

    def scan_directory(self, directory):
        """递归扫描目录"""
        for root, dirs, files in os.walk(directory):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    self.scan_file(file_path)

    def generate_report(self):
        """生成报告"""
        print("=" * 70)
        print("🔍 Integrate目录内容完整性扫描报告")
        print("=" * 70)
        print()
        print(f"📊 统计信息:")
        print(f"  总文件数: {self.stats['total_files']}")
        print(f"  空文件: {self.stats['empty_files']}")
        print(f"  短文件(<50行且内容<20行): {self.stats['short_files']}")
        print(f"  只有TOC无内容: {self.stats['toc_only']}")
        print(f"  有占位符内容不足: {self.stats['placeholder_only']}")
        print(f"  实际内容不足(<30行): {self.stats['no_content']}")
        print()

        total_issues = sum(len(v) for v in self.issues.values())
        print(f"📋 问题统计:")
        print(f"  总问题数: {total_issues}")
        print()

        for issue_type, items in sorted(self.issues.items()):
            if items:
                print(f"⚠️  {issue_type} ({len(items)}个):")
                for item in items[:20]:  # 显示前20个
                    print(f"     - {item}")
                if len(items) > 20:
                    print(f"     ... 还有 {len(items) - 20} 个")
                print()

        print("=" * 70)

        return self.issues

if __name__ == '__main__':
    base_dir = Path(__file__).parent
    scanner = ContentScanner(base_dir)
    scanner.scan_directory(base_dir)
    issues = scanner.generate_report()
