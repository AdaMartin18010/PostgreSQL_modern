#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分主题去重检查工具
针对Integrate目录，按主题进行去重检查，提高效率
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import argparse

class TopicDeduplicationChecker:
    """分主题去重检查器"""

    def __init__(self, root_dir: str, threshold: float = 0.8):
        self.root_dir = Path(root_dir)
        self.threshold = threshold
        self.similarities: List[Tuple[str, str, float]] = []

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
        # 移除来源信息（Integrate目录特有的）
        content = re.sub(r'^> \*\*📋 文档来源.*?\n', '', content, flags=re.MULTILINE)
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content)
        return content.strip()

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1, text2).ratio()

    def check_topic(self, topic_dir: Path) -> List[Tuple[str, str, float]]:
        """检查单个主题目录中的重复文档"""
        topic_similarities = []

        if not topic_dir.exists() or not topic_dir.is_dir():
            return topic_similarities

        # 获取该主题下的所有md文件
        md_files = list(topic_dir.rglob("*.md"))
        md_files = [f for f in md_files if f.name != "README.md"]  # 跳过README

        if len(md_files) < 2:
            return topic_similarities

        print(f"\n检查主题: {topic_dir.name} ({len(md_files)} 个文档)")

        # 读取所有文档
        documents = {}
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                text_content = self.extract_text(content)
                if len(text_content) > 100:  # 只处理有实质内容的文档
                    rel_path = str(md_file.relative_to(self.root_dir))
                    documents[rel_path] = text_content
            except Exception as e:
                print(f"  警告: 无法读取 {md_file.name}: {e}")

        # 比较文档对
        doc_list = list(documents.items())
        for i, (path1, content1) in enumerate(doc_list):
            for j, (path2, content2) in enumerate(doc_list[i+1:], start=i+1):
                similarity = self.calculate_similarity(content1, content2)
                if similarity >= self.threshold:
                    topic_similarities.append((path1, path2, similarity))
                    print(f"  ⚠️  发现相似文档: {Path(path1).name} <-> {Path(path2).name} (相似度: {similarity:.2%})")

        return topic_similarities

    def check_all_topics(self):
        """检查所有主题"""
        print(f"开始检查 Integrate 目录...")
        print(f"相似度阈值: {self.threshold}")

        # 获取所有主题目录
        topic_dirs = [d for d in self.root_dir.iterdir()
                     if d.is_dir() and d.name.startswith(('0', '1', '2'))
                     and not d.name.startswith('00-')]

        topic_dirs.sort()

        print(f"\n找到 {len(topic_dirs)} 个主题目录")

        for topic_dir in topic_dirs:
            similarities = self.check_topic(topic_dir)
            self.similarities.extend(similarities)

        print(f"\n📊 检查完成:")
        print(f"  总相似文档对: {len(self.similarities)}")
        print(f"  高相似度 (>=0.9): {len([s for s in self.similarities if s[2] >= 0.9])}")
        print(f"  中等相似度 (0.8-0.9): {len([s for s in self.similarities if 0.8 <= s[2] < 0.9])}")

    def generate_report(self, output_file: str = "00-重复内容报告.md"):
        """生成去重报告"""
        output_path = self.root_dir / output_file

        report = f"""# Integrate 目录重复内容报告

> **生成时间**: {Path(__file__).stat().st_mtime}
> **检查目录**: Integrate
> **相似度阈值**: {self.threshold}
> **发现重复文档对**: {len(self.similarities)}

---

## 📊 统计摘要

- 总相似文档对: {len(self.similarities)}
- 高相似度文档对 (>=0.9): {len([s for s in self.similarities if s[2] >= 0.9])}
- 中等相似度文档对 (0.8-0.9): {len([s for s in self.similarities if 0.8 <= s[2] < 0.9])}

---

## 🔍 重复文档详情

"""

        if self.similarities:
            # 按相似度排序
            sorted_similarities = sorted(self.similarities, key=lambda x: x[2], reverse=True)

            report += "### 高相似度文档对 (>=0.9)\n\n"
            high_sim = [s for s in sorted_similarities if s[2] >= 0.9]
            if high_sim:
                for path1, path2, sim in high_sim:
                    report += f"- **相似度: {sim:.2%}**\n"
                    report += f"  - `{path1}`\n"
                    report += f"  - `{path2}`\n\n"
            else:
                report += "无\n\n"

            report += "### 中等相似度文档对 (0.8-0.9)\n\n"
            med_sim = [s for s in sorted_similarities if 0.8 <= s[2] < 0.9]
            if med_sim:
                for path1, path2, sim in med_sim:
                    report += f"- **相似度: {sim:.2%}**\n"
                    report += f"  - `{path1}`\n"
                    report += f"  - `{path2}`\n\n"
            else:
                report += "无\n\n"
        else:
            report += "未发现重复文档。\n\n"

        report += """---

## 📋 建议的合并清单

### 高优先级合并（相似度 >= 0.9）

建议合并这些高度相似的文档，保留内容最完整的版本。

### 中等优先级合并（相似度 0.8-0.9）

建议审查这些文档，决定是否需要合并。

---

## 🔧 使用说明

1. 审查高相似度文档对
2. 决定保留哪个文档
3. 合并内容到保留的文档
4. 更新所有引用链接
5. 删除重复的文档（在Integrate目录中）

---

**报告生成工具**: `Integrate/check_duplicates_by_topic.py`
"""

        output_path.write_text(report, encoding='utf-8')
        print(f"\n📄 报告已保存到: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='分主题去重检查工具')
    parser.add_argument('--root', type=str, default='Integrate', help='Integrate目录路径')
    parser.add_argument('--threshold', type=float, default=0.8, help='相似度阈值 (0-1)')
    parser.add_argument('--output', type=str, default='00-重复内容报告.md', help='输出报告文件名')

    args = parser.parse_args()

    checker = TopicDeduplicationChecker(args.root, args.threshold)
    checker.check_all_topics()
    checker.generate_report(args.output)

    print("\n✅ 检查完成！")

if __name__ == '__main__':
    main()
