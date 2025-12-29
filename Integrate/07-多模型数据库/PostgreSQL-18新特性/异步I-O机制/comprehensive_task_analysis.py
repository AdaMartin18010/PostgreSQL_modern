#!/usr/bin/env python3
"""
全面递归任务分析工具
检查所有文档的完整性、格式、内容质量
"""
import os
import re
from pathlib import Path
from collections import defaultdict

class ComprehensiveTaskAnalyzer:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.issues = defaultdict(list)
        self.stats = {
            'total_docs': 0,
            'docs_with_toc': 0,
            'docs_without_toc': 0,
            'docs_with_nested_toc': 0,
            'docs_with_toc_mismatch': 0,
            'docs_with_placeholder': 0,
            'docs_with_unclosed_code': 0,
            'docs_without_h2': 0,
            'docs_with_broken_links': 0,
            'short_docs': 0,
        }

    def analyze_document(self, file_path):
        """分析单个文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            self.issues['read_errors'].append(f"{file_path}: {e}")
            return

        self.stats['total_docs'] += 1
        rel_path = str(file_path.relative_to(self.root_dir))

        # 检查文档长度
        if len(lines) < 50:
            self.stats['short_docs'] += 1
            self.issues['short_docs'].append(rel_path)

        # 检查TOC
        toc_pattern = r'^##\s*📑\s*目录'
        has_toc = bool(re.search(toc_pattern, content, re.MULTILINE))

        if has_toc:
            self.stats['docs_with_toc'] += 1
            # 检查嵌套TOC
            toc_lines = []
            in_toc = False
            for i, line in enumerate(lines):
                if re.match(toc_pattern, line):
                    in_toc = True
                elif in_toc:
                    if line.strip().startswith('-'):
                        toc_lines.append(line)
                    elif line.strip() == '' or line.startswith('#'):
                        if line.startswith('##'):
                            break
                        if line.strip() == '' and toc_lines:
                            continue
                        if not line.strip():
                            continue
                    if line.startswith('---'):
                        break

            # 检查嵌套层级
            nested = False
            for line in toc_lines:
                if '  -' in line or '    -' in line:
                    nested = True
                    break

            if nested:
                self.stats['docs_with_nested_toc'] += 1
                self.issues['nested_toc'].append(rel_path)

            # 检查TOC项数与H3标题数匹配
            toc_items = len([l for l in toc_lines if l.strip().startswith('-')])
            h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))

            if toc_items != h3_count:
                self.stats['docs_with_toc_mismatch'] += 1
                self.issues['toc_mismatch'].append(f"{rel_path}: TOC项数={toc_items}, H3数={h3_count}")
        else:
            self.stats['docs_without_toc'] += 1
            self.issues['no_toc'].append(rel_path)

        # 检查占位符内容
        if '*本节内容待补充*' in content or '*待补充*' in content or 'TODO' in content.upper():
            self.stats['docs_with_placeholder'] += 1
            self.issues['placeholder'].append(rel_path)

        # 检查未闭合的代码块
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            self.stats['docs_with_unclosed_code'] += 1
            self.issues['unclosed_code'].append(rel_path)

        # 检查H2标题
        h2_pattern = r'^##\s+\d+\.'
        has_h2 = bool(re.search(h2_pattern, content, re.MULTILINE))
        if not has_h2 and self.stats['total_docs'] > 1:  # 排除README.md
            # 检查是否有章节标题格式
            chapter_pattern = r'^##\s+[^\d]'
            has_chapter = bool(re.search(chapter_pattern, content, re.MULTILINE))
            if not has_chapter:
                self.stats['docs_without_h2'] += 1
                self.issues['no_h2'].append(rel_path)

        # 检查链接
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        for text, url in links:
            if url.startswith('#'):
                # 内部锚点链接
                anchor = url[1:].lower().replace(' ', '-')
                if anchor not in content.lower():
                    self.stats['docs_with_broken_links'] += 1
                    self.issues['broken_links'].append(f"{rel_path}: {text} -> {url}")
                    break

    def scan_directory(self, directory):
        """递归扫描目录"""
        for root, dirs, files in os.walk(directory):
            # 跳过隐藏目录和特定目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.endswith('.md') and file != 'README.md' or file == 'README.md':
                    file_path = Path(root) / file
                    self.analyze_document(file_path)

    def generate_report(self):
        """生成报告"""
        print("=" * 70)
        print("🔍 全面任务分析报告")
        print("=" * 70)
        print()
        print(f"📊 统计信息:")
        print(f"  总文档数: {self.stats['total_docs']}")
        print(f"  有目录的文档: {self.stats['docs_with_toc']}")
        print(f"  无目录的文档: {self.stats['docs_without_toc']}")
        print(f"  嵌套目录的文档: {self.stats['docs_with_nested_toc']}")
        print(f"  目录项不匹配的文档: {self.stats['docs_with_toc_mismatch']}")
        print(f"  有占位符的文档: {self.stats['docs_with_placeholder']}")
        print(f"  未闭合代码块的文档: {self.stats['docs_with_unclosed_code']}")
        print(f"  缺少H2标题的文档: {self.stats['docs_without_h2']}")
        print(f"  有 broken 链接的文档: {self.stats['docs_with_broken_links']}")
        print(f"  短文档(<50行): {self.stats['short_docs']}")
        print()

        total_issues = sum(len(v) for v in self.issues.values())
        print(f"📋 问题统计:")
        print(f"  总问题数: {total_issues}")
        print()

        for issue_type, items in sorted(self.issues.items()):
            if items:
                print(f"⚠️  {issue_type} ({len(items)}个):")
                for item in items[:10]:  # 只显示前10个
                    print(f"     - {item}")
                if len(items) > 10:
                    print(f"     ... 还有 {len(items) - 10} 个")
                print()

        print("=" * 70)

if __name__ == '__main__':
    # 分析异步I/O机制文档
    async_io_dir = Path(__file__).parent
    analyzer = ComprehensiveTaskAnalyzer(async_io_dir)
    analyzer.scan_directory(async_io_dir)
    analyzer.generate_report()

    print("\n" + "=" * 70)
    print("🔍 扩展分析：技术原理目录")
    print("=" * 70)

    # 分析技术原理目录
    tech_dir = async_io_dir.parent.parent / '技术原理'
    if tech_dir.exists():
        tech_analyzer = ComprehensiveTaskAnalyzer(tech_dir.parent)
        tech_analyzer.scan_directory(tech_dir)
        tech_analyzer.generate_report()

    print("\n" + "=" * 70)
    print("🔍 扩展分析：图向量混合检索目录")
    print("=" * 70)

    # 分析图向量混合检索目录
    graph_dir = async_io_dir.parent.parent / '图向量混合检索'
    if graph_dir.exists():
        graph_analyzer = ComprehensiveTaskAnalyzer(graph_dir.parent)
        graph_analyzer.scan_directory(graph_dir)
        graph_analyzer.generate_report()
