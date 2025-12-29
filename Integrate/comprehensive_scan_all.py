#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面扫描Integrate目录下所有文档，识别未完成的任务
"""
import os
import re
from pathlib import Path
from collections import defaultdict

class ComprehensiveScanner:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.tasks = defaultdict(list)
        self.stats = {
            'total_docs': 0,
            'docs_with_placeholder': 0,
            'docs_with_todo': 0,
            'docs_without_toc': 0,
            'docs_with_nested_toc': 0,
            'docs_with_toc_mismatch': 0,
            'docs_with_unclosed_code': 0,
        }
        
    def scan_document(self, file_path):
        """扫描单个文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return
            
        self.stats['total_docs'] += 1
        rel_path = str(file_path.relative_to(self.root_dir))
        
        # 跳过报告文件和脚本文件
        if 'COMPLETION_REPORT' in rel_path or 'TASK_LIST' in rel_path or rel_path.endswith('.py'):
            return
        
        # 检查占位符内容
        if '*本节内容待补充*' in content or '*待补充*' in content:
            self.stats['docs_with_placeholder'] += 1
            self.tasks['placeholder'].append(rel_path)
        
        # 检查TODO标记（排除报告文件）
        if re.search(r'TODO|FIXME|XXX', content, re.IGNORECASE) and 'REPORT' not in rel_path:
            # 检查是否是示例占位符
            if 'password=xxx' not in content.lower() and 'xxx' not in content.lower():
                self.stats['docs_with_todo'] += 1
                self.tasks['todo'].append(rel_path)
        
        # 检查TOC
        toc_pattern = r'^##\s*📑\s*目录'
        has_toc = bool(re.search(toc_pattern, content, re.MULTILINE))
        
        if has_toc:
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
                self.tasks['nested_toc'].append(rel_path)
            
            # 检查TOC项数与H3标题数匹配（只统计指向锚点的链接）
            toc_items = len([l for l in toc_lines if re.match(r'^-\s+\[.*\]\(#', l.strip())])
            h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))
            
            if toc_items != h3_count and toc_items > 0:
                self.stats['docs_with_toc_mismatch'] += 1
                self.tasks['toc_mismatch'].append(f"{rel_path}: TOC={toc_items}, H3={h3_count}")
        
        # 检查未闭合的代码块
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            self.stats['docs_with_unclosed_code'] += 1
            self.tasks['unclosed_code'].append(rel_path)
    
    def scan_directory(self, directory):
        """递归扫描目录"""
        for root, dirs, files in os.walk(directory):
            # 跳过隐藏目录和特定目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    self.scan_document(file_path)
    
    def generate_report(self):
        """生成报告"""
        print("=" * 70)
        print("🔍 Integrate目录全面扫描报告")
        print("=" * 70)
        print()
        print(f"📊 统计信息:")
        print(f"  总文档数: {self.stats['total_docs']}")
        print(f"  有占位符的文档: {self.stats['docs_with_placeholder']}")
        print(f"  有TODO标记的文档: {self.stats['docs_with_todo']}")
        print(f"  嵌套目录的文档: {self.stats['docs_with_nested_toc']}")
        print(f"  目录项不匹配的文档: {self.stats['docs_with_toc_mismatch']}")
        print(f"  未闭合代码块的文档: {self.stats['docs_with_unclosed_code']}")
        print()
        
        total_tasks = sum(len(v) for v in self.tasks.values())
        print(f"📋 任务统计:")
        print(f"  总任务数: {total_tasks}")
        print()
        
        for task_type, items in sorted(self.tasks.items()):
            if items:
                print(f"⚠️  {task_type} ({len(items)}个):")
                for item in items[:10]:  # 只显示前10个
                    print(f"     - {item}")
                if len(items) > 10:
                    print(f"     ... 还有 {len(items) - 10} 个")
                print()
        
        print("=" * 70)
        
        return self.tasks

if __name__ == '__main__':
    base_dir = Path(__file__).parent
    scanner = ComprehensiveScanner(base_dir)
    scanner.scan_directory(base_dir)
    tasks = scanner.generate_report()
