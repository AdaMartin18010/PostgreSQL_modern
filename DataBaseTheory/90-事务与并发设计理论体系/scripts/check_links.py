#!/usr/bin/env python3
"""
文档链接完整性检查脚本

功能:
1. 扫描所有Markdown文档
2. 检查内部链接的有效性
3. 检查外部链接的可访问性
4. 生成链接完整性报告
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from urllib.parse import urlparse
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("警告: requests库未安装，将跳过外部链接检查")

from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置
# 脚本位于 scripts/ 目录，需要回到 90-事务与并发设计理论体系 目录
_script_dir = Path(__file__).parent.absolute()
ROOT_DIR = _script_dir.parent  # 90-事务与并发设计理论体系 目录
EXTERNAL_LINK_TIMEOUT = 5
MAX_WORKERS = 10

# 链接模式
INTERNAL_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
HEADER_PATTERN = re.compile(r'^#+\s+(.+)$', re.MULTILINE)
ANCHOR_PATTERN = re.compile(r'\{#([^}]+)\}')

class LinkChecker:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.documents: Dict[str, Dict] = {}
        self.internal_links: List[Tuple[str, str, str]] = []  # (file, link_text, link_target)
        self.external_links: List[Tuple[str, str, str]] = []
        self.errors: List[Dict] = []

    def scan_documents(self):
        """扫描所有Markdown文档"""
        print(f"扫描文档目录: {self.root_dir}")

        for md_file in self.root_dir.rglob("*.md"):
            if md_file.name.startswith("."):
                continue

            rel_path = md_file.relative_to(self.root_dir)
            print(f"  处理: {rel_path}")

            try:
                content = md_file.read_text(encoding='utf-8')
                self.documents[str(rel_path)] = {
                    'path': md_file,
                    'content': content,
                    'headers': self.extract_headers(content)
                }
            except Exception as e:
                self.errors.append({
                    'type': 'read_error',
                    'file': str(rel_path),
                    'error': str(e)
                })

    def extract_headers(self, content: str) -> Dict[str, str]:
        """提取文档中的所有标题"""
        headers = {}

        # 提取所有标题
        for match in HEADER_PATTERN.finditer(content):
            header_text = match.group(1).strip()
            # 生成锚点ID（类似GitHub风格）
            anchor = self.generate_anchor(header_text)
            headers[anchor] = header_text

        # 提取显式锚点
        for match in ANCHOR_PATTERN.finditer(content):
            anchor = match.group(1)
            # 查找对应的标题
            for line in content.split('\n'):
                if anchor in line and line.strip().startswith('#'):
                    header_text = line.strip().lstrip('#').strip()
                    headers[anchor] = header_text
                    break

        return headers

    def generate_anchor(self, text: str) -> str:
        """生成GitHub风格的锚点ID"""
        # 转换为小写
        anchor = text.lower()
        # 替换空格为连字符
        anchor = anchor.replace(' ', '-')
        # 移除特殊字符
        anchor = re.sub(r'[^\w\-]', '', anchor)
        # 移除连续连字符
        anchor = re.sub(r'-+', '-', anchor)
        return anchor

    def extract_links(self):
        """提取所有链接"""
        for file_path, doc_info in self.documents.items():
            content = doc_info['content']

            for match in INTERNAL_LINK_PATTERN.finditer(content):
                link_text = match.group(1)
                link_target = match.group(2)

                # 判断是内部链接还是外部链接
                if link_target.startswith('http://') or link_target.startswith('https://'):
                    self.external_links.append((file_path, link_text, link_target))
                elif link_target.startswith('#'):
                    # 文档内锚点链接
                    anchor = link_target.lstrip('#')
                    self.internal_links.append((file_path, link_text, f"{file_path}#{anchor}"))
                elif not link_target.startswith('mailto:'):
                    # 相对路径链接
                    self.internal_links.append((file_path, link_text, link_target))

    def check_internal_links(self):
        """检查内部链接"""
        print("\n检查内部链接...")

        for file_path, link_text, link_target in self.internal_links:
            # 处理锚点链接
            if '#' in link_target:
                target_file, anchor = link_target.split('#', 1)
            else:
                target_file = link_target
                anchor = None

            # 解析目标文件路径
            source_dir = Path(self.root_dir) / Path(file_path).parent
            target_path = (source_dir / target_file).resolve()

            # 检查文件是否存在
            if not target_path.exists() or not target_path.is_file():
                self.errors.append({
                    'type': 'broken_internal_link',
                    'file': file_path,
                    'link_text': link_text,
                    'link_target': link_target,
                    'error': f'目标文件不存在: {target_file}'
                })
                continue

            # 检查锚点是否存在
            if anchor:
                target_rel_path = target_path.relative_to(self.root_dir)
                target_doc = self.documents.get(str(target_rel_path))

                if target_doc:
                    # 检查锚点是否在目标文档的标题中
                    anchor_normalized = self.generate_anchor(anchor)
                    if anchor_normalized not in target_doc['headers']:
                        # 尝试直接匹配
                        if anchor not in target_doc['headers']:
                            self.errors.append({
                                'type': 'broken_anchor',
                                'file': file_path,
                                'link_text': link_text,
                                'link_target': link_target,
                                'error': f'锚点不存在: #{anchor}'
                            })

    def check_external_links(self):
        """检查外部链接"""
        if not HAS_REQUESTS:
            print("\n跳过外部链接检查（requests库未安装）")
            return

        print("\n检查外部链接...")

        def check_link(link_info):
            file_path, link_text, link_url = link_info
            try:
                response = requests.head(link_url, timeout=EXTERNAL_LINK_TIMEOUT, allow_redirects=True)
                if response.status_code >= 400:
                    return {
                        'type': 'broken_external_link',
                        'file': file_path,
                        'link_text': link_text,
                        'link_target': link_url,
                        'error': f'HTTP {response.status_code}'
                    }
            except requests.exceptions.RequestException as e:
                return {
                    'type': 'broken_external_link',
                    'file': file_path,
                    'link_text': link_text,
                    'link_target': link_url,
                    'error': str(e)
                }
            return None

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(check_link, link): link for link in self.external_links}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.errors.append(result)

    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("# 文档链接完整性检查报告\n")
        report.append(f"**检查时间**: {Path(__file__).stat().st_mtime}")
        report.append(f"**检查目录**: {self.root_dir}\n")

        # 统计信息
        report.append("## 📊 统计信息\n")
        report.append(f"- **文档总数**: {len(self.documents)}")
        report.append(f"- **内部链接数**: {len(self.internal_links)}")
        report.append(f"- **外部链接数**: {len(self.external_links)}")
        report.append(f"- **错误数**: {len(self.errors)}\n")

        # 错误详情
        if self.errors:
            report.append("## ❌ 错误详情\n")

            # 按类型分组
            errors_by_type = {}
            for error in self.errors:
                error_type = error['type']
                if error_type not in errors_by_type:
                    errors_by_type[error_type] = []
                errors_by_type[error_type].append(error)

            for error_type, errors in errors_by_type.items():
                report.append(f"### {error_type} ({len(errors)}个)\n")

                for error in errors[:10]:  # 只显示前10个
                    report.append(f"- **文件**: `{error['file']}`")
                    report.append(f"  - **链接文本**: {error.get('link_text', 'N/A')}")
                    report.append(f"  - **链接目标**: `{error.get('link_target', 'N/A')}`")
                    report.append(f"  - **错误**: {error.get('error', 'N/A')}\n")

                if len(errors) > 10:
                    report.append(f"  ... 还有 {len(errors) - 10} 个错误\n")
        else:
            report.append("## ✅ 检查通过\n")
            report.append("所有链接检查通过，未发现错误！\n")

        return "\n".join(report)

    def run(self):
        """运行检查"""
        print("=" * 60)
        print("文档链接完整性检查")
        print("=" * 60)

        # 扫描文档
        self.scan_documents()
        print(f"\n扫描完成: {len(self.documents)} 个文档")

        # 提取链接
        self.extract_links()
        print(f"提取链接: {len(self.internal_links)} 个内部链接, {len(self.external_links)} 个外部链接")

        # 检查内部链接
        self.check_internal_links()

        # 检查外部链接
        if self.external_links:
            self.check_external_links()

        # 生成报告
        report = self.generate_report()

        # 保存报告
        report_file = self.root_dir / "链接完整性检查报告.md"
        report_file.write_text(report, encoding='utf-8')
        print(f"\n报告已保存: {report_file}")

        # 打印摘要
        print("\n" + "=" * 60)
        print("检查摘要")
        print("=" * 60)
        print(f"文档数: {len(self.documents)}")
        print(f"内部链接: {len(self.internal_links)}")
        print(f"外部链接: {len(self.external_links)}")
        print(f"错误数: {len(self.errors)}")

        if self.errors:
            print("\n❌ 发现错误，请查看报告文件")
            return 1
        else:
            print("\n✅ 所有链接检查通过")
            return 0

def main():
    checker = LinkChecker(ROOT_DIR)
    return checker.run()

if __name__ == "__main__":
    sys.exit(main())
