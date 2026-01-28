#!/usr/bin/env python3
"""
批量修复失效链接工具

功能:
1. 读取链接检查报告
2. 识别常见失效链接模式
3. 自动修复或标记失效链接
4. 生成修复报告

使用方法:
    python fix_broken_links.py --report link_check_report.md --dry-run
    python fix_broken_links.py --report link_check_report.md --fix
"""

import re
import os
from pathlib import Path
import argparse
from typing import List, Dict, Tuple


def parse_link_report(report_file: str) -> List[Dict]:
    """解析链接检查报告"""
    
    broken_links = []
    
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析失效链接部分
    pattern = r'- \*\*文件\*\*: `([^`]+)` \(第(\d+)行\)\s+- \*\*链接文本\*\*: ([^\n]+)\s+- \*\*链接URL\*\*: `([^`]+)`\s+- \*\*问题\*\*: ([^\n]+)'
    
    for match in re.finditer(pattern, content, re.MULTILINE):
        broken_links.append({
            'file': match.group(1),
            'line': int(match.group(2)),
            'text': match.group(3),
            'url': match.group(4),
            'issue': match.group(5)
        })
    
    return broken_links


def find_file_in_archive(filename: str) -> str:
    """在archive目录中查找文件"""
    
    # 检查archive目录
    archive_paths = [
        Path('Integrate/00-归档-项目管理文档'),
        Path('archive'),
        Path('Integrate/00-归档-项目管理文档/00-归档-项目管理文档'),
    ]
    
    for archive_path in archive_paths:
        if archive_path.exists():
            target = archive_path / filename
            if target.exists():
                return str(target.relative_to(Path('Integrate')))
    
    return None


def suggest_fix(link_info: Dict, root_dir: str = 'Integrate') -> Tuple[str, str]:
    """建议修复方案"""
    
    file_path = link_info['file']
    url = link_info['url']
    issue = link_info['issue']
    
    # 模式1: 文件已归档
    if '文件不存在' in issue:
        filename = issue.split(': ')[-1].replace('Integrate\\', '').replace('\\', '/')
        
        # 检查是否在archive目录
        archive_path = find_file_in_archive(filename.split('/')[-1])
        if archive_path:
            # 计算相对路径
            base_file = Path(file_path).parent
            target_file = Path('Integrate') / archive_path
            
            try:
                relative_path = os.path.relpath(target_file, base_file).replace('\\', '/')
                if not relative_path.startswith('.'):
                    relative_path = './' + relative_path
                return ('fix', relative_path)
            except:
                pass
        
        # 模式2: 文件可能已删除，建议删除链接或标记
        if '00-项目完成报告' in filename or '00-去重处理' in filename or '00-第一阶段' in filename:
            # 这些是临时文档，可以删除链接
            return ('remove', None)
    
    # 模式3: 路径错误（如缺少../）
    if url.startswith('./') and '文件不存在' in issue:
        # 尝试添加../前缀
        if not url.startswith('../'):
            parent_count = len(Path(file_path).parent.parts) - len(Path('Integrate').parts)
            if parent_count > 0:
                new_url = '../' * parent_count + url[2:]
                return ('fix', new_url)
    
    return ('unknown', None)


def fix_link_in_file(file_path: str, line_num: int, old_url: str, new_url: str, dry_run: bool = True) -> bool:
    """修复文件中的链接"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num > len(lines):
            return False
        
        # 查找包含old_url的行
        line_index = line_num - 1
        line = lines[line_index]
        
        # 替换链接
        if old_url in line:
            new_line = line.replace(old_url, new_url)
            if not dry_run:
                lines[line_index] = new_line
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            return True
        
        return False
    except Exception as e:
        print(f"错误修复文件 {file_path}: {e}")
        return False


def remove_link_from_file(file_path: str, line_num: int, dry_run: bool = True) -> bool:
    """从文件中删除链接"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num > len(lines):
            return False
        
        line_index = line_num - 1
        line = lines[line_index]
        
        # 删除markdown链接，保留文本
        # [text](url) -> text
        pattern = r'\[([^\]]+)\]\([^\)]+\)'
        new_line = re.sub(pattern, r'\1', line)
        
        if new_line != line:
            if not dry_run:
                lines[line_index] = new_line
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            return True
        
        return False
    except Exception as e:
        print(f"错误删除链接 {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='批量修复失效链接工具')
    parser.add_argument('--report', required=True, help='链接检查报告文件')
    parser.add_argument('--dry-run', action='store_true', help='仅显示修复建议，不实际修改')
    parser.add_argument('--fix', action='store_true', help='执行修复')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.fix:
        print("请指定 --dry-run 或 --fix")
        return
    
    dry_run = args.dry_run
    
    print(f"解析链接报告: {args.report}")
    broken_links = parse_link_report(args.report)
    
    print(f"发现 {len(broken_links)} 个失效链接")
    
    fixes = {
        'fix': [],
        'remove': [],
        'unknown': []
    }
    
    # 分析每个失效链接
    for link in broken_links:
        action, value = suggest_fix(link)
        link['action'] = action
        link['fix_value'] = value
        fixes[action].append(link)
    
    print(f"\n修复建议:")
    print(f"- 可修复: {len(fixes['fix'])}")
    print(f"- 可删除: {len(fixes['remove'])}")
    print(f"- 未知: {len(fixes['unknown'])}")
    
    # 执行修复
    fixed_count = 0
    removed_count = 0
    
    if not dry_run:
        print("\n开始修复...")
        
        # 修复链接
        for link in fixes['fix']:
            if fix_link_in_file(link['file'], link['line'], link['url'], link['fix_value'], dry_run=False):
                fixed_count += 1
        
        # 删除链接
        for link in fixes['remove']:
            if remove_link_from_file(link['file'], link['line'], dry_run=False):
                removed_count += 1
        
        print(f"\n修复完成:")
        print(f"- 修复链接: {fixed_count}")
        print(f"- 删除链接: {removed_count}")
    else:
        print("\n[DRY RUN] 修复建议:")
        print("\n可修复的链接（前10个）:")
        for link in fixes['fix'][:10]:
            print(f"  {link['file']}:{link['line']} - {link['url']} -> {link['fix_value']}")
        
        print("\n可删除的链接（前10个）:")
        for link in fixes['remove'][:10]:
            print(f"  {link['file']}:{link['line']} - {link['text']}")


if __name__ == '__main__':
    main()
