#!/usr/bin/env python3
"""
批量修复失效链接脚本
自动修复常见的链接问题
"""

import re
import os
from pathlib import Path

# 链接映射表：旧路径 -> 新路径
LINK_MAPPINGS = {
    # 高可用相关
    '../09-高可用/': '../13-高可用架构/',
    '../09-高可用/高可用体系详解.md': '../13-高可用架构/高可用体系详解.md',
    
    # 性能调优相关
    '../11-性能调优/性能调优深入.md': '../02-查询与优化/02.06-性能调优/性能调优深入.md',
    
    # 运维管理相关
    '../13-运维管理/统计信息管理.md': '../12-监控与诊断/监控与诊断.md',
    
    # 数据管理相关
    '../05-数据管理/分区表管理.md': '../17-数据模型设计/README.md',
    
    # 分布式系统理论
    '../04-分布式系统理论/': '../15-分布式系统/',
    '../04-分布式系统理论/04.02-分布式一致性与CAP-形式化刻画与权衡.md': 
        '../15-分布式系统/04.02-分布式一致性与CAP-形式化刻画与权衡.md',
}

def fix_links_in_file(file_path):
    """修复单个文件中的链接"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 应用映射修复
        for old_link, new_link in LINK_MAPPINGS.items():
            content = content.replace(old_link, new_link)
        
        # 保存修改
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主函数"""
    base_path = Path('e:/_src/PostgreSQL_modern')
    md_files = list(base_path.rglob('*.md'))
    
    fixed_count = 0
    
    print(f"Scanning {len(md_files)} markdown files...")
    
    for md_file in md_files:
        # 跳过归档目录
        if '00-归档' in str(md_file):
            continue
            
        if fix_links_in_file(md_file):
            fixed_count += 1
    
    print(f"\nFixed links in {fixed_count} files")

if __name__ == '__main__':
    main()
