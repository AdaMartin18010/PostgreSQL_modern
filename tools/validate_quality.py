#!/usr/bin/env python3
"""
PostgreSQL_modern 项目质量验证脚本

用途：自动化执行质量验证任务
- 检查外部链接有效性
- 验证版本信息一致性
- 检查文档交叉引用
- 生成验证报告

用法：
    python tools/validate_quality.py --all              # 运行所有验证
    python tools/validate_quality.py --links            # 仅检查链接
    python tools/validate_quality.py --versions         # 仅检查版本信息
    python tools/validate_quality.py --refs             # 仅检查交叉引用
"""

import os
import sys
import re
import argparse
import requests
import time
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


class LinkChecker:
    """外部链接检查器"""
    
    def __init__(self):
        self.checked_links = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_links_from_file(self, file_path: Path) -> List[Tuple[str, int]]:
        """从文件中提取所有外部链接"""
        links = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # 匹配 markdown 链接格式
                    matches = re.findall(r'https?://[^\s\)]+', line)
                    for url in matches:
                        # 清理 URL（去除末尾的标点符号）
                        url = url.rstrip('.,;:')
                        links.append((url, line_num))
        except Exception as e:
            print_error(f"读取文件失败 {file_path}: {e}")
        return links
    
    def check_link(self, url: str) -> Tuple[bool, str]:
        """检查单个链接的有效性"""
        if url in self.checked_links:
            return self.checked_links[url]
        
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            if response.status_code < 400:
                result = (True, f"{response.status_code}")
                self.checked_links[url] = result
                return result
            else:
                result = (False, f"{response.status_code}")
                self.checked_links[url] = result
                return result
        except requests.exceptions.Timeout:
            result = (False, "Timeout")
            self.checked_links[url] = result
            return result
        except requests.exceptions.RequestException as e:
            result = (False, str(e)[:50])
            self.checked_links[url] = result
            return result
    
    def check_all_markdown_files(self) -> Dict:
        """检查所有 Markdown 文件中的链接"""
        print_header("检查外部链接有效性")
        
        results = {
            'total_files': 0,
            'total_links': 0,
            'unique_links': 0,
            'valid_links': 0,
            'invalid_links': 0,
            'invalid_details': []
        }
        
        # 获取所有 markdown 文件
        md_files = list(PROJECT_ROOT.glob('**/*.md'))
        # 排除某些目录
        md_files = [f for f in md_files if '.git' not in str(f) and 'node_modules' not in str(f)]
        
        all_links = []
        for md_file in md_files:
            links = self.extract_links_from_file(md_file)
            if links:
                results['total_files'] += 1
                for url, line_num in links:
                    all_links.append((url, md_file, line_num))
        
        results['total_links'] = len(all_links)
        
        # 获取唯一链接
        unique_links = set(url for url, _, _ in all_links)
        results['unique_links'] = len(unique_links)
        
        print_info(f"找到 {results['total_files']} 个文件，共 {results['total_links']} 个链接（{results['unique_links']} 个唯一）")
        print_info("开始检查链接有效性...")
        
        # 检查每个唯一链接
        for i, url in enumerate(unique_links, 1):
            print(f"检查 [{i}/{results['unique_links']}]: {url[:60]}...", end='\r')
            is_valid, status = self.check_link(url)
            
            if is_valid:
                results['valid_links'] += 1
            else:
                results['invalid_links'] += 1
                # 找到所有使用此链接的文件
                locations = [(f, ln) for u, f, ln in all_links if u == url]
                results['invalid_details'].append({
                    'url': url,
                    'status': status,
                    'locations': locations
                })
            
            time.sleep(0.5)  # 避免请求过快
        
        print()  # 换行
        return results
    
    def print_results(self, results: Dict):
        """打印检查结果"""
        print_header("链接检查结果")
        
        total = results['unique_links']
        valid = results['valid_links']
        invalid = results['invalid_links']
        percentage = (valid / total * 100) if total > 0 else 0
        
        print(f"总链接数（唯一）: {total}")
        print(f"有效链接: {valid} ({percentage:.1f}%)")
        print(f"失效链接: {invalid} ({100-percentage:.1f}%)")
        
        if percentage >= 95:
            print_success(f"链接有效率 {percentage:.1f}% ≥ 95% ✅")
        else:
            print_warning(f"链接有效率 {percentage:.1f}% < 95% ⚠️")
        
        if invalid > 0:
            print_header("失效链接详情")
            for item in results['invalid_details']:
                print_error(f"{item['url']}")
                print(f"  状态: {item['status']}")
                print(f"  位置:")
                for file_path, line_num in item['locations'][:3]:  # 只显示前3个位置
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    print(f"    - {rel_path}:{line_num}")
                if len(item['locations']) > 3:
                    print(f"    ... 还有 {len(item['locations']) - 3} 个位置")
                print()


class VersionChecker:
    """版本信息一致性检查器"""
    
    def __init__(self):
        self.issues = []
    
    def check_pg17_release_date(self) -> Dict:
        """检查 PostgreSQL 17 发布日期一致性"""
        print_header("检查 PostgreSQL 17 发布日期")
        
        correct_date = "2024年9月26日"
        pattern = re.compile(r'2024年9月(?!26日)')
        
        issues = []
        md_files = list(PROJECT_ROOT.glob('**/*.md'))
        md_files = [f for f in md_files if '.git' not in str(f)]
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern.search(line):
                            issues.append({
                                'file': md_file.relative_to(PROJECT_ROOT),
                                'line': line_num,
                                'content': line.strip()
                            })
            except Exception as e:
                pass
        
        if not issues:
            print_success(f"所有文件的 PostgreSQL 17 发布日期统一为 '{correct_date}'")
        else:
            print_warning(f"发现 {len(issues)} 处日期不一致")
            for issue in issues[:5]:  # 只显示前5个
                print(f"  {issue['file']}:{issue['line']}")
                print(f"    {issue['content'][:80]}")
        
        return {'correct': len(issues) == 0, 'issues': issues}
    
    def check_extension_versions(self) -> Dict:
        """检查扩展版本一致性"""
        print_header("检查扩展版本一致性")
        
        expected_versions = {
            'pgvector': ['0.8.0', 'v0.8.0'],
            'TimescaleDB': ['2.17.2'],
            'PostGIS': ['3.5.0'],
            'Citus': ['12.1.4', 'v12.1.4']
        }
        
        all_issues = {}
        
        for ext_name, valid_versions in expected_versions.items():
            issues = []
            md_files = list(PROJECT_ROOT.glob('**/*.md'))
            md_files = [f for f in md_files if '.git' not in str(f)]
            
            for md_file in md_files:
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 检查是否提到了该扩展
                        if ext_name.lower() in content.lower():
                            # 检查版本号
                            for line_num, line in enumerate(content.split('\n'), 1):
                                if ext_name.lower() in line.lower():
                                    # 检查是否包含正确的版本号
                                    has_valid_version = any(v in line for v in valid_versions)
                                    # 检查是否有版本号但不是正确的
                                    has_version = re.search(r'\d+\.\d+\.?\d*', line)
                                    if has_version and not has_valid_version:
                                        issues.append({
                                            'file': md_file.relative_to(PROJECT_ROOT),
                                            'line': line_num,
                                            'content': line.strip()
                                        })
                except Exception as e:
                    pass
            
            if not issues:
                print_success(f"{ext_name}: 版本一致 ({', '.join(valid_versions)})")
            else:
                print_warning(f"{ext_name}: 发现 {len(issues)} 处可能的版本不一致")
                all_issues[ext_name] = issues
        
        return {'correct': len(all_issues) == 0, 'issues': all_issues}


class ReferenceChecker:
    """文档交叉引用检查器"""
    
    def check_internal_links(self) -> Dict:
        """检查内部链接有效性"""
        print_header("检查文档内部链接")
        
        results = {
            'total_links': 0,
            'valid_links': 0,
            'broken_links': 0,
            'broken_details': []
        }
        
        md_files = list(PROJECT_ROOT.glob('**/*.md'))
        md_files = [f for f in md_files if '.git' not in str(f)]
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        # 匹配相对路径的 markdown 链接
                        matches = re.findall(r'\[([^\]]+)\]\(([^\)]+\.md[^\)]*)\)', line)
                        for link_text, link_path in matches:
                            results['total_links'] += 1
                            
                            # 解析链接路径（可能包含锚点）
                            link_path_clean = link_path.split('#')[0]
                            
                            # 计算绝对路径
                            if link_path_clean.startswith('./'):
                                target_path = md_file.parent / link_path_clean[2:]
                            elif link_path_clean.startswith('../'):
                                target_path = md_file.parent / link_path_clean
                            else:
                                target_path = md_file.parent / link_path_clean
                            
                            # 检查文件是否存在
                            if target_path.exists():
                                results['valid_links'] += 1
                            else:
                                results['broken_links'] += 1
                                results['broken_details'].append({
                                    'file': md_file.relative_to(PROJECT_ROOT),
                                    'line': line_num,
                                    'link_text': link_text,
                                    'link_path': link_path,
                                    'target': target_path
                                })
            except Exception as e:
                pass
        
        if results['total_links'] == 0:
            print_info("未找到内部链接")
        else:
            total = results['total_links']
            valid = results['valid_links']
            broken = results['broken_links']
            percentage = (valid / total * 100) if total > 0 else 0
            
            print(f"总内部链接数: {total}")
            print(f"有效链接: {valid} ({percentage:.1f}%)")
            print(f"失效链接: {broken}")
            
            if broken == 0:
                print_success("所有内部链接有效 ✅")
            else:
                print_warning(f"发现 {broken} 个失效的内部链接")
                for item in results['broken_details'][:5]:
                    print(f"  {item['file']}:{item['line']}")
                    print(f"    [{item['link_text']}]({item['link_path']})")
        
        return results


def generate_report(link_results, version_results, ref_results):
    """生成验证报告"""
    report_path = PROJECT_ROOT / 'QUALITY_VALIDATION_REPORT.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 质量验证报告\n\n")
        f.write(f"**验证日期**：{time.strftime('%Y年%m月%d日')}\n")
        f.write("**验证版本**：v0.96\n")
        f.write("**验证工具**：validate_quality.py\n\n")
        f.write("---\n\n")
        
        f.write("## 📊 执行摘要\n\n")
        
        # 链接检查结果
        if link_results:
            total = link_results['unique_links']
            valid = link_results['valid_links']
            percentage = (valid / total * 100) if total > 0 else 0
            status = "✅ 优秀" if percentage >= 95 else "⚠️ 需改进"
            f.write(f"- **外部链接有效率**：{percentage:.1f}% ({valid}/{total}) {status}\n")
        
        # 版本检查结果
        if version_results:
            pg_status = "✅ 通过" if version_results['pg17']['correct'] else "❌ 不通过"
            ext_status = "✅ 通过" if version_results['extensions']['correct'] else "❌ 不通过"
            f.write(f"- **PostgreSQL 17 发布日期一致性**：{pg_status}\n")
            f.write(f"- **扩展版本一致性**：{ext_status}\n")
        
        # 内部链接检查结果
        if ref_results:
            broken = ref_results['broken_links']
            status = "✅ 通过" if broken == 0 else f"❌ {broken}个失效"
            f.write(f"- **内部链接有效性**：{status}\n")
        
        f.write("\n---\n\n")
        f.write("## 详细结果\n\n")
        f.write("详细结果请查看控制台输出。\n\n")
        f.write("---\n\n")
        f.write(f"**报告生成时间**：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print_success(f"验证报告已生成: {report_path}")


def main():
    parser = argparse.ArgumentParser(description='PostgreSQL_modern 项目质量验证工具')
    parser.add_argument('--all', action='store_true', help='运行所有验证')
    parser.add_argument('--links', action='store_true', help='检查外部链接')
    parser.add_argument('--versions', action='store_true', help='检查版本信息')
    parser.add_argument('--refs', action='store_true', help='检查内部链接')
    
    args = parser.parse_args()
    
    # 如果没有指定任何选项，默认运行所有
    if not any([args.all, args.links, args.versions, args.refs]):
        args.all = True
    
    link_results = None
    version_results = None
    ref_results = None
    
    print_header("PostgreSQL_modern 项目质量验证")
    print_info(f"项目根目录: {PROJECT_ROOT}")
    
    try:
        if args.all or args.links:
            checker = LinkChecker()
            link_results = checker.check_all_markdown_files()
            checker.print_results(link_results)
        
        if args.all or args.versions:
            checker = VersionChecker()
            pg17_results = checker.check_pg17_release_date()
            ext_results = checker.check_extension_versions()
            version_results = {
                'pg17': pg17_results,
                'extensions': ext_results
            }
        
        if args.all or args.refs:
            checker = ReferenceChecker()
            ref_results = checker.check_internal_links()
        
        # 生成报告
        if args.all:
            generate_report(link_results, version_results, ref_results)
        
        print_header("验证完成")
        print_success("所有验证任务已完成！")
        
    except KeyboardInterrupt:
        print_warning("\n验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"验证过程中出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

