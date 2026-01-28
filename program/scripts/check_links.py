#!/usr/bin/env python3
"""
Markdown文档链接检查工具

功能:
1. 扫描Markdown文档中的所有链接
2. 检查内部链接有效性
3. 检查外部链接可访问性（可选）
4. 生成链接检查报告

使用方法:
    python check_links.py --root . --output link_check_report.md
    python check_links.py --root Integrate --check-external
"""

import re
import os
from pathlib import Path
import argparse
from typing import List, Dict, Tuple
from urllib.parse import urlparse
import urllib.request
from urllib.error import URLError, HTTPError


def find_links(content: str, file_path: str) -> List[Dict]:
    """查找文档中的所有链接"""
    
    links = []
    
    # Markdown链接格式: [text](url) 或 [text][ref]
    # 也支持HTML格式: <url>
    
    # 标准Markdown链接: [text](url) 或 [text](<url>)
    pattern1 = r'\[([^\]]+)\]\(([^\)]+)\)'
    for match in re.finditer(pattern1, content):
        text = match.group(1)
        url = match.group(2).strip()
        # 去除角括号包裹的URL，如 <https://...>
        if url.startswith('<') and url.endswith('>'):
            url = url[1:-1]
        line_num = content[:match.start()].count('\n') + 1
        
        links.append({
            'type': 'markdown',
            'text': text,
            'url': url,
            'line': line_num,
            'file': file_path
        })
    
    # HTML链接: <url>
    pattern2 = r'<([^>]+)>'
    for match in re.finditer(pattern2, content):
        url = match.group(1)
        # 跳过代码块中的 <>
        if url.startswith('http://') or url.startswith('https://') or url.startswith('mailto:'):
            line_num = content[:match.start()].count('\n') + 1
            links.append({
                'type': 'html',
                'text': url,
                'url': url,
                'line': line_num,
                'file': file_path
            })
    
    return links


def is_internal_link(url: str) -> bool:
    """判断是否为内部链接"""
    
    # 去除角括号
    u = url.strip()
    if u.startswith('<') and u.endswith('>'):
        u = u[1:-1]
    
    # 外部链接特征: http/https/mailto
    if u.startswith('http://') or u.startswith('https://') or u.startswith('mailto:'):
        return False
    
    # 内部链接: 锚点、相对路径、文件路径
    if u.startswith('#') or u.startswith('./') or u.startswith('../') or u.startswith('/'):
        return True
    
    # 文件路径（含.md或/）且非URL
    if ('.md' in u or '/' in u) and '://' not in u:
        return True
    
    return False


def resolve_internal_link(link_url: str, base_file: str, root_dir: str = '') -> Tuple[bool, str]:
    """解析内部链接，检查文件是否存在。root_dir 下解析时不会向 .. 越过 root_dir。"""
    
    base_path = Path(base_file).resolve().parent
    root = Path(root_dir).resolve() if root_dir else None
    
    # 处理锚点链接
    if link_url.startswith('#'):
        return (True, '锚点链接')
    
    # 处理相对路径
    if link_url.startswith('./'):
        link_url = link_url[2:]
    elif link_url.startswith('../'):
        parts = link_url.split('/')
        up_levels = 0
        for part in parts:
            if part == '..':
                up_levels += 1
            else:
                break
        link_url = '/'.join(parts[up_levels:])
        for _ in range(up_levels):
            if root and base_path == root:
                break
            base_path = base_path.parent
    
    # 移除锚点部分
    if '#' in link_url:
        file_part = link_url.split('#')[0]
    else:
        file_part = link_url
    
    # 已知非 Markdown 扩展名不再追加 .md
    _non_md = (
        '.conf', '.yml', '.yaml', '.sql', '.json', '.sh', '.py', '.ps1',
        '.pdf', '.html',
        # images
        '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg',
    )
    _add_md = (
        file_part and not file_part.endswith('.md') and not file_part.endswith('/')
        and not any(file_part.lower().endswith(ext) for ext in _non_md)
    )
    if _add_md:
        # 若路径为已存在的目录或含 README.md，视为目录链接，不追加 .md
        _dir = base_path / file_part
        if _dir.is_dir() or (_dir / 'README.md').exists():
            file_part = file_part  # 保持原样，下面按目录校验
        else:
            file_part += '.md'
    
    if file_part:
        target_path = base_path / file_part
        if target_path.exists():
            return (True, str(target_path))
        if (base_path / (file_part.rstrip('/'))).is_dir():
            return (True, str(base_path / file_part.rstrip('/')))
        if (base_path / (file_part.rstrip('/')) / 'README.md').exists():
            return (True, str(base_path / file_part.rstrip('/') / 'README.md'))
        return (False, f'文件不存在: {target_path}')
    return (True, '目录链接')


def check_external_link(url: str, timeout: int = 5) -> Tuple[bool, str]:
    """检查外部链接可访问性"""
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Link Checker)')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.getcode()
            if 200 <= status < 400:
                return (True, f'HTTP {status}')
            else:
                return (False, f'HTTP {status}')
    except HTTPError as e:
        return (False, f'HTTP {e.code}')
    except URLError as e:
        return (False, f'URL错误: {str(e)}')
    except Exception as e:
        return (False, f'错误: {str(e)}')


def scan_directory(root_dir: str, check_external: bool = False) -> Dict:
    """扫描目录中的所有Markdown文件"""
    
    results = {
        'total_files': 0,
        'total_links': 0,
        'internal_links': [],
        'external_links': [],
        'broken_internal': [],
        'broken_external': [],
        'files': {}
    }
    
    root_path = Path(root_dir)
    
    for md_file in root_path.rglob('*.md'):
        results['total_files'] += 1
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            links = find_links(content, str(md_file))
            results['total_links'] += len(links)
            
            file_results = {
                'file': str(md_file),
                'links': [],
                'broken': []
            }
            
            for link in links:
                link_info = {
                    'text': link['text'],
                    'url': link['url'],
                    'line': link['line'],
                    'status': 'unknown'
                }
                
                if is_internal_link(link['url']):
                    results['internal_links'].append(link)
                    valid, message = resolve_internal_link(link['url'], str(md_file), root_dir)
                    
                    if valid:
                        link_info['status'] = 'valid'
                        link_info['message'] = message
                    else:
                        link_info['status'] = 'broken'
                        link_info['message'] = message
                        link_info['file'] = str(md_file)
                        results['broken_internal'].append(link_info)
                        file_results['broken'].append(link_info)
                else:
                    results['external_links'].append(link)
                    if check_external:
                        valid, message = check_external_link(link['url'])
                        link_info['status'] = 'valid' if valid else 'broken'
                        link_info['message'] = message
                        
                        if not valid:
                            link_info['file'] = str(md_file)
                            results['broken_external'].append(link_info)
                            file_results['broken'].append(link_info)
                    else:
                        link_info['status'] = 'not_checked'
                        link_info['message'] = '未检查（使用--check-external启用）'
                
                file_results['links'].append(link_info)
            
            if file_results['links']:
                results['files'][str(md_file)] = file_results
                
        except Exception as e:
            print(f"错误处理文件 {md_file}: {e}")
    
    return results


def generate_report(results: Dict, output_file: str):
    """生成链接检查报告"""
    
    report = []
    report.append("# 链接检查报告\n")
    report.append(f"> **生成时间**: {Path(__file__).stat().st_mtime}")
    report.append(f"> **扫描文件数**: {results['total_files']}")
    report.append(f"> **总链接数**: {results['total_links']}\n")
    
    report.append("## 📊 统计摘要\n")
    report.append(f"- **内部链接**: {len(results['internal_links'])}")
    report.append(f"- **外部链接**: {len(results['external_links'])}")
    report.append(f"- **失效内部链接**: {len(results['broken_internal'])}")
    report.append(f"- **失效外部链接**: {len(results['broken_external'])}\n")
    
    if results['broken_internal']:
        report.append("## 🔴 失效的内部链接\n")
        for link_info in results['broken_internal']:
            # link_info可能是字典或link对象
            if isinstance(link_info, dict):
                file_path = link_info.get('file', '未知文件')
                line = link_info.get('line', '未知行')
                text = link_info.get('text', '未知文本')
                url = link_info.get('url', '未知URL')
                message = link_info.get('message', '未知问题')
            else:
                file_path = getattr(link_info, 'file', '未知文件')
                line = getattr(link_info, 'line', '未知行')
                text = getattr(link_info, 'text', '未知文本')
                url = getattr(link_info, 'url', '未知URL')
                message = getattr(link_info, 'message', '未知问题')
            
            report.append(f"- **文件**: `{file_path}` (第{line}行)")
            report.append(f"  - **链接文本**: {text}")
            report.append(f"  - **链接URL**: `{url}`")
            report.append(f"  - **问题**: {message}\n")
    
    if results['broken_external']:
        report.append("## 🔴 失效的外部链接\n")
        for link_info in results['broken_external']:
            if isinstance(link_info, dict):
                file_path = link_info.get('file', '未知文件')
                line = link_info.get('line', '未知行')
                text = link_info.get('text', '未知文本')
                url = link_info.get('url', '未知URL')
                message = link_info.get('message', '未知问题')
            else:
                file_path = getattr(link_info, 'file', '未知文件')
                line = getattr(link_info, 'line', '未知行')
                text = getattr(link_info, 'text', '未知文本')
                url = getattr(link_info, 'url', '未知URL')
                message = getattr(link_info, 'message', '未知问题')
            
            report.append(f"- **文件**: `{file_path}` (第{line}行)")
            report.append(f"  - **链接文本**: {text}")
            report.append(f"  - **链接URL**: `{url}`")
            report.append(f"  - **问题**: {message}\n")
    
    if not results['broken_internal'] and not results['broken_external']:
        report.append("## ✅ 所有链接有效\n")
        report.append("恭喜！所有链接都有效。\n")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"报告已生成: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Markdown文档链接检查工具')
    parser.add_argument('--root', default='.', help='根目录路径 (默认: 当前目录)')
    parser.add_argument('--output', default='link_check_report.md', help='输出报告文件')
    parser.add_argument('--check-external', action='store_true', help='检查外部链接可访问性')
    
    args = parser.parse_args()
    
    print(f"开始扫描目录: {args.root}")
    print(f"检查外部链接: {'是' if args.check_external else '否'}")
    
    results = scan_directory(args.root, args.check_external)
    
    print(f"\n扫描完成:")
    print(f"- 文件数: {results['total_files']}")
    print(f"- 总链接数: {results['total_links']}")
    print(f"- 内部链接: {len(results['internal_links'])}")
    print(f"- 外部链接: {len(results['external_links'])}")
    print(f"- 失效内部链接: {len(results['broken_internal'])}")
    print(f"- 失效外部链接: {len(results['broken_external'])}")
    
    generate_report(results, args.output)


if __name__ == '__main__':
    main()
