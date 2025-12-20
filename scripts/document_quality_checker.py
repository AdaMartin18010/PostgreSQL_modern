#!/usr/bin/env python3
"""
文档质量检查工具

功能:
1. 扫描所有Markdown文档
2. 评估文档质量（A/B/C级）
3. 生成质量报告
4. 识别需要改进的文档

使用方法:
    python document_quality_checker.py [--output quality_report.md]
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import argparse


class DocumentQualityChecker:
    """文档质量检查器"""

    def __init__(self, root_dir: str):
        """初始化检查器"""
        self.root_dir = Path(root_dir)
        self.documents: Dict[str, Dict] = {}

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
                rel_path = str(md_file.relative_to(self.root_dir))

                quality = self.assess_quality(content, rel_path)
                self.documents[rel_path] = quality
            except Exception as e:
                print(f"警告: 无法读取 {md_file}: {e}")

        print(f"成功评估 {len(self.documents)} 个文档")

    def assess_quality(self, content: str, filepath: str) -> Dict:
        """评估文档质量"""
        metrics = {
            'filepath': filepath,
            'total_lines': len(content.split('\n')),
            'code_blocks': len(re.findall(r'```', content)) // 2,
            'code_examples': len(re.findall(r'```(?:python|sql|bash|sh)', content, re.IGNORECASE)),
            'headings': len(re.findall(r'^#+\s+', content, re.MULTILINE)),
            'links': len(re.findall(r'\[([^\]]+)\]\([^\)]+\)', content)),
            'images': len(re.findall(r'!\[([^\]]*)\]\([^\)]+\)', content)),
            'tables': len(re.findall(r'\|.*\|', content)),
            'has_toc': bool(re.search(r'^##?\s+[目录|Table of Contents]', content, re.MULTILINE | re.IGNORECASE)),
            'has_summary': bool(re.search(r'^##?\s+[摘要|Summary|概述]', content, re.MULTILINE | re.IGNORECASE)),
            'has_references': bool(re.search(r'^##?\s+[参考|References|参考文献]', content, re.MULTILINE | re.IGNORECASE)),
            'placeholder_count': len(re.findall(r'(?:待补充|待完成|TODO|FIXME|详细内容见|见文档)', content, re.IGNORECASE)),
            'substantive_content': self.calculate_substantive_content(content),
        }

        # 计算质量分数
        score = self.calculate_score(metrics)
        metrics['score'] = score
        metrics['grade'] = self.assign_grade(score, metrics)

        return metrics

    def calculate_substantive_content(self, content: str) -> int:
        """计算实质性内容长度（去除代码块、链接等）"""
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', content)
        # 移除行内代码
        text = re.sub(r'`[^`]+`', '', text)
        # 移除链接
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # 移除图片
        text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
        # 移除标题标记
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        return len(text.strip())

    def calculate_score(self, metrics: Dict) -> float:
        """计算质量分数（0-100）"""
        score = 0.0

        # 基础分数：实质性内容
        if metrics['substantive_content'] > 5000:
            score += 30
        elif metrics['substantive_content'] > 2000:
            score += 20
        elif metrics['substantive_content'] > 500:
            score += 10

        # 代码示例
        if metrics['code_examples'] >= 5:
            score += 20
        elif metrics['code_examples'] >= 3:
            score += 15
        elif metrics['code_examples'] >= 1:
            score += 10

        # 结构完整性
        if metrics['has_toc']:
            score += 5
        if metrics['has_summary']:
            score += 5
        if metrics['has_references']:
            score += 5

        # 图表和链接
        if metrics['tables'] >= 3:
            score += 10
        elif metrics['tables'] >= 1:
            score += 5

        if metrics['links'] >= 10:
            score += 10
        elif metrics['links'] >= 5:
            score += 5

        # 扣分项：占位符
        if metrics['placeholder_count'] > 5:
            score -= 20
        elif metrics['placeholder_count'] > 2:
            score -= 10
        elif metrics['placeholder_count'] > 0:
            score -= 5

        # 扣分项：内容过少
        if metrics['total_lines'] < 50:
            score -= 15
        elif metrics['total_lines'] < 100:
            score -= 10

        return max(0, min(100, score))

    def assign_grade(self, score: float, metrics: Dict) -> str:
        """分配质量等级"""
        # C级：只有框架或占位符
        if (metrics['placeholder_count'] > 3 or
            metrics['substantive_content'] < 500 or
            score < 40):
            return 'C'

        # A级：高质量文档
        if (score >= 70 and
            metrics['code_examples'] >= 3 and
            metrics['substantive_content'] > 2000 and
            metrics['placeholder_count'] == 0):
            return 'A'

        # B级：中等质量
        return 'B'

    def generate_report(self, output_file: str = "quality_report.md") -> None:
        """生成质量报告"""
        print(f"生成报告: {output_file}")

        # 按等级分组
        by_grade = defaultdict(list)
        for filepath, metrics in self.documents.items():
            by_grade[metrics['grade']].append((filepath, metrics))

        # 统计
        total = len(self.documents)
        grade_counts = {grade: len(docs) for grade, docs in by_grade.items()}

        report_lines = [
            "# 文档质量检查报告",
            "",
            f"**生成时间**: {Path(__file__).stat().st_mtime}",
            f"**检查文档数**: {total}",
            "",
            "---",
            "",
            "## 📊 质量统计",
            "",
            f"- **A级文档（优秀）**: {grade_counts.get('A', 0)} ({grade_counts.get('A', 0)*100//total if total > 0 else 0}%)",
            f"- **B级文档（良好）**: {grade_counts.get('B', 0)} ({grade_counts.get('B', 0)*100//total if total > 0 else 0}%)",
            f"- **C级文档（需改进）**: {grade_counts.get('C', 0)} ({grade_counts.get('C', 0)*100//total if total > 0 else 0}%)",
            "",
            "---",
            "",
        ]

        # A级文档列表
        if 'A' in by_grade:
            report_lines.extend([
                "## ✅ A级文档（优秀）",
                "",
                "这些文档质量优秀，包含深入的技术原理、完整的代码示例和丰富的案例。",
                ""
            ])
            for filepath, metrics in sorted(by_grade['A'], key=lambda x: x[1]['score'], reverse=True):
                report_lines.extend([
                    f"### `{filepath}`",
                    f"- **质量分数**: {metrics['score']:.1f}/100",
                    f"- **实质性内容**: {metrics['substantive_content']} 字符",
                    f"- **代码示例**: {metrics['code_examples']} 个",
                    f"- **表格**: {metrics['tables']} 个",
                    f"- **链接**: {metrics['links']} 个",
                    "",
                ])

        # B级文档列表
        if 'B' in by_grade:
            report_lines.extend([
                "## ⚠️ B级文档（良好）",
                "",
                "这些文档有基础内容，但需要补充论证、引用或性能数据。",
                ""
            ])
            for filepath, metrics in sorted(by_grade['B'], key=lambda x: x[1]['score'], reverse=True):
                report_lines.extend([
                    f"### `{filepath}`",
                    f"- **质量分数**: {metrics['score']:.1f}/100",
                    f"- **实质性内容**: {metrics['substantive_content']} 字符",
                    f"- **代码示例**: {metrics['code_examples']} 个",
                    f"- **占位符**: {metrics['placeholder_count']} 个",
                    "",
                    "**需要补充**:",
                    "- [ ] 学术论文引用",
                    "- [ ] 性能基准测试数据",
                    "- [ ] 实际案例论证",
                    "- [ ] 深入的技术原理分析",
                    "",
                ])

        # C级文档列表（需要优先改进）
        if 'C' in by_grade:
            report_lines.extend([
                "## ❌ C级文档（需改进）",
                "",
                "这些文档只有框架，缺乏实质内容。需要优先改进。",
                "",
                f"**总计**: {len(by_grade['C'])} 个文档",
                ""
            ])

            # 按优先级排序（占位符多、内容少的优先）
            priority_docs = sorted(
                by_grade['C'],
                key=lambda x: (x[1]['placeholder_count'], -x[1]['substantive_content']),
                reverse=True
            )

            report_lines.append("### 高优先级改进文档（前20个）\n")
            for i, (filepath, metrics) in enumerate(priority_docs[:20], 1):
                report_lines.extend([
                    f"#### {i}. `{filepath}`",
                    f"- **质量分数**: {metrics['score']:.1f}/100",
                    f"- **实质性内容**: {metrics['substantive_content']} 字符",
                    f"- **占位符**: {metrics['placeholder_count']} 个",
                    f"- **代码示例**: {metrics['code_examples']} 个",
                    "",
                    "**需要补充**:",
                    "- [ ] 完整的业务场景描述",
                    "- [ ] 详细的架构设计图",
                    "- [ ] 代码示例和配置文件",
                    "- [ ] 性能测试结果",
                    "- [ ] 故障处理经验",
                    "- [ ] FAQ章节",
                    "",
                ])

        report_lines.extend([
            "",
            "---",
            "",
            "## 🔧 使用说明",
            "",
            "1. 优先改进C级文档（特别是高优先级的前20个）",
            "2. 为B级文档补充缺失的内容",
            "3. 保持A级文档的质量",
            "",
            "---",
            "",
            "**报告生成工具**: `scripts/document_quality_checker.py`",
            ""
        ])

        output_path = self.root_dir / output_file
        output_path.write_text('\n'.join(report_lines), encoding='utf-8')
        print(f"报告已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='文档质量检查工具')
    parser.add_argument('--root', type=str, default='.', help='项目根目录')
    parser.add_argument('--output', type=str, default='quality_report.md', help='输出报告文件名')

    args = parser.parse_args()

    checker = DocumentQualityChecker(args.root)
    checker.scan_documents()
    checker.generate_report(args.output)

    print("\n✅ 检查完成！")
    print(f"📊 已评估 {len(checker.documents)} 个文档")
    print(f"📄 报告已保存到: {args.output}")


if __name__ == '__main__':
    main()
