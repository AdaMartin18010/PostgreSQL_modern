#!/usr/bin/env python3
"""
内容去重检查工具

功能:
1. 扫描项目中的所有Markdown文档
2. 计算文档间的相似度
3. 生成重复内容报告
4. 识别需要合并的文档

使用方法:
    python content_deduplication_checker.py [--threshold 0.6] [--output report.md]
"""

import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
import argparse
from difflib import SequenceMatcher


class ContentDeduplicationChecker:
    """内容去重检查器"""

    def __init__(self, root_dir: str, threshold: float = 0.6):
        """
        初始化检查器

        Args:
            root_dir: 项目根目录
            threshold: 相似度阈值（0-1），超过此值认为重复
        """
        self.root_dir = Path(root_dir)
        self.threshold = threshold
        self.documents: Dict[str, str] = {}
        self.similarities: List[Tuple[str, str, float]] = []

    def scan_documents(self) -> None:
        """扫描所有Markdown文档"""
        print(f"扫描目录: {self.root_dir}")

        md_files = list(self.root_dir.rglob("*.md"))
        print(f"找到 {len(md_files)} 个Markdown文件")

        for md_file in md_files:
            # 跳过某些目录
            if any(skip in str(md_file) for skip in ['.git', 'node_modules', '__pycache__', '99-Archive']):
                continue

            try:
                content = md_file.read_text(encoding='utf-8')
                # 提取纯文本内容（去除Markdown语法）
                text_content = self.extract_text(content)

                if len(text_content) > 100:  # 只处理有实质内容的文档
                    rel_path = str(md_file.relative_to(self.root_dir))
                    self.documents[rel_path] = text_content
            except Exception as e:
                print(f"警告: 无法读取 {md_file}: {e}")

        print(f"成功加载 {len(self.documents)} 个文档")

    def extract_text(self, content: str) -> str:
        """从Markdown内容中提取纯文本"""
        # 移除代码块
        content = re.sub(r'```[\s\S]*?```', '', content)
        # 移除行内代码
        content = re.sub(r'`[^`]+`', '', content)
        # 移除链接
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        # 移除图片
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', content)
        # 移除标题标记
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
        # 移除粗体/斜体标记
        content = re.sub(r'\*\*([^\*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^\*]+)\*', r'\1', content)
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content)
        return content.strip()

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        return SequenceMatcher(None, text1, text2).ratio()

    def find_duplicates(self) -> None:
        """查找重复内容"""
        print("计算文档相似度...")

        doc_list = list(self.documents.items())
        total = len(doc_list) * (len(doc_list) - 1) // 2
        processed = 0

        for i, (path1, content1) in enumerate(doc_list):
            for j, (path2, content2) in enumerate(doc_list[i+1:], start=i+1):
                similarity = self.calculate_similarity(content1, content2)

                if similarity >= self.threshold:
                    self.similarities.append((path1, path2, similarity))

                processed += 1
                if processed % 100 == 0:
                    print(f"进度: {processed}/{total} ({processed*100//total}%)")

        print(f"找到 {len(self.similarities)} 对相似文档（相似度 >= {self.threshold})")

    def generate_report(self, output_file: str = "duplication_report.md") -> None:
        """生成重复内容报告"""
        print(f"生成报告: {output_file}")

        # 按相似度排序
        self.similarities.sort(key=lambda x: x[2], reverse=True)

        report_lines = [
            "# 内容去重检查报告",
            "",
            f"**生成时间**: {Path(__file__).stat().st_mtime}",
            f"**检查文档数**: {len(self.documents)}",
            f"**相似度阈值**: {self.threshold}",
            f"**发现重复文档对**: {len(self.similarities)}",
            "",
            "---",
            "",
            "## 📊 统计摘要",
            "",
            f"- 总文档数: {len(self.documents)}",
            f"- 重复文档对: {len(self.similarities)}",
            f"- 高相似度文档对 (>=0.8): {len([s for s in self.similarities if s[2] >= 0.8])}",
            f"- 中等相似度文档对 (0.6-0.8): {len([s for s in self.similarities if 0.6 <= s[2] < 0.8])}",
            "",
            "---",
            "",
            "## 🔍 重复文档详情",
            "",
        ]

        # 按相似度分组
        high_similarity = [(p1, p2, sim) for p1, p2, sim in self.similarities if sim >= 0.8]
        medium_similarity = [(p1, p2, sim) for p1, p2, sim in self.similarities if 0.6 <= sim < 0.8]

        if high_similarity:
            report_lines.extend([
                "### 🔴 高相似度文档 (相似度 >= 0.8) - 建议立即合并",
                ""
            ])
            for path1, path2, similarity in high_similarity:
                report_lines.extend([
                    f"#### 相似度: {similarity:.2%}",
                    "",
                    f"- **文档1**: `{path1}`",
                    f"- **文档2**: `{path2}`",
                    "",
                    "**建议操作**:",
                    f"- [ ] 对比两个文档内容",
                    f"- [ ] 合并重复内容",
                    f"- [ ] 保留更完整的版本",
                    f"- [ ] 更新所有引用链接",
                    "",
                    "---",
                    ""
                ])

        if medium_similarity:
            report_lines.extend([
                "### 🟡 中等相似度文档 (相似度 0.6-0.8) - 建议审查",
                ""
            ])
            for path1, path2, similarity in medium_similarity:
                report_lines.extend([
                    f"#### 相似度: {similarity:.2%}",
                    "",
                    f"- **文档1**: `{path1}`",
                    f"- **文档2**: `{path2}`",
                    "",
                    "**建议操作**:",
                    f"- [ ] 审查两个文档是否有重复章节",
                    f"- [ ] 考虑合并或交叉引用",
                    "",
                    "---",
                    ""
                ])

        # 生成建议的合并清单
        report_lines.extend([
            "",
            "## 📋 建议的合并清单",
            "",
            "### 高优先级合并（相似度 >= 0.8）",
            ""
        ])

        merged_docs = set()
        merge_groups = []

        for path1, path2, similarity in high_similarity:
            if path1 not in merged_docs and path2 not in merged_docs:
                merge_groups.append([path1, path2])
                merged_docs.add(path1)
                merged_docs.add(path2)

        for i, group in enumerate(merge_groups, 1):
            report_lines.extend([
                f"#### 合并组 {i}",
                "",
                "**文档列表**:",
            ])
            for doc in group:
                report_lines.append(f"- `{doc}`")
            report_lines.extend([
                "",
                "**合并建议**:",
                f"- 保留: `{group[0]}` (建议保留更完整的版本)",
                f"- 合并到: `{group[0]}`",
                f"- 删除: `{group[1]}` (合并后删除)",
                "",
            ])

        report_lines.extend([
            "",
            "---",
            "",
            "## 🔧 使用说明",
            "",
            "1. 审查高相似度文档对",
            "2. 决定保留哪个文档",
            "3. 合并内容到保留的文档",
            "4. 更新所有引用链接",
            "5. 删除重复的文档",
            "",
            "---",
            "",
            "**报告生成工具**: `scripts/content_deduplication_checker.py`",
            ""
        ])

        output_path = self.root_dir / output_file
        output_path.write_text('\n'.join(report_lines), encoding='utf-8')
        print(f"报告已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='内容去重检查工具')
    parser.add_argument('--root', type=str, default='.', help='项目根目录')
    parser.add_argument('--threshold', type=float, default=0.6, help='相似度阈值 (0-1)')
    parser.add_argument('--output', type=str, default='duplication_report.md', help='输出报告文件名')

    args = parser.parse_args()

    checker = ContentDeduplicationChecker(args.root, args.threshold)
    checker.scan_documents()
    checker.find_duplicates()
    checker.generate_report(args.output)

    print("\n✅ 检查完成！")
    print(f"📊 发现 {len(checker.similarities)} 对相似文档")
    print(f"📄 报告已保存到: {args.output}")


if __name__ == '__main__':
    main()
