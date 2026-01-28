#!/usr/bin/env python3
"""
批量更新PostgreSQL版本引用脚本
将文档中的PostgreSQL 18.0更新为18.1
"""

import os
import re
import sys
from pathlib import Path

# 版本更新映射
VERSION_UPDATES = [
    # 精确匹配
    (r'PostgreSQL\s+18\.0\b', 'PostgreSQL 18.1'),
    (r'postgresql.*18\.0\b', lambda m: m.group(0).replace('18.0', '18.1')),
    (r'PG\s+18\.0\b', 'PG 18.1'),
    (r'pg\s+18\.0\b', 'pg 18.1'),
    # 版本号引用
    (r'18\.0\s+版本', '18.1 版本'),
    (r'版本\s+18\.0', '版本 18.1'),
    # 文档中的版本说明
    (r'PostgreSQL\s+18\.0\s+\(', 'PostgreSQL 18.1 ('),
]

# 排除的文件和目录
EXCLUDE_PATTERNS = [
    '.git',
    'node_modules',
    '__pycache__',
    '.pytest_cache',
    'venv',
    'env',
    # 排除刚创建的新文档（它们已经是18.1）
    '18.03-PostgreSQL-18.1-更新说明.md',
    'PostgreSQL-18.1-安全修复说明.md',
    'CRITICAL-REVIEW-AND-RECOMMENDATIONS.md',
    'IMPROVEMENT-ACTION-PLAN.md',
    'REVIEW-SUMMARY.md',
    'COMPARISON-TABLE.md',
]

# 只处理markdown文件
FILE_EXTENSIONS = ['.md', '.mdx']

def should_exclude(filepath):
    """检查文件是否应该被排除"""
    path_str = str(filepath)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False

def update_file_content(content, filepath):
    """更新文件内容"""
    updated = False
    new_content = content
    
    for pattern, replacement in VERSION_UPDATES:
        if callable(replacement):
            # 使用函数进行替换
            matches = list(re.finditer(pattern, new_content, re.IGNORECASE))
            if matches:
                updated = True
                for match in reversed(matches):  # 从后往前替换，避免位置偏移
                    new_content = new_content[:match.start()] + replacement(match) + new_content[match.end():]
        else:
            # 直接字符串替换
            if re.search(pattern, new_content, re.IGNORECASE):
                updated = True
                new_content = re.sub(pattern, replacement, new_content, flags=re.IGNORECASE)
    
    return new_content, updated

def process_file(filepath):
    """处理单个文件"""
    if should_exclude(filepath):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content, updated = update_file_content(content, filepath)
        
        if updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 已更新: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"❌ 错误处理 {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """主函数"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    print(f"📁 项目根目录: {project_root}")
    print(f"🔍 开始搜索需要更新的文件...\n")
    
    updated_count = 0
    total_files = 0
    
    # 遍历所有文件
    for root, dirs, files in os.walk(project_root):
        # 排除目录
        dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
        
        for file in files:
            filepath = Path(root) / file
            
            # 检查文件扩展名
            if filepath.suffix not in FILE_EXTENSIONS:
                continue
            
            # 检查是否应该排除
            if should_exclude(filepath):
                continue
            
            total_files += 1
            
            # 处理文件
            if process_file(filepath):
                updated_count += 1
    
    print(f"\n📊 处理完成:")
    print(f"   总文件数: {total_files}")
    print(f"   已更新: {updated_count}")
    print(f"   未更新: {total_files - updated_count}")
    
    if updated_count > 0:
        print(f"\n✅ 成功更新 {updated_count} 个文件")
    else:
        print(f"\nℹ️  没有文件需要更新")

if __name__ == '__main__':
    main()
