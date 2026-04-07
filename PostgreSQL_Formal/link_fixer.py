#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL_Formal 链接自动修复工具
自动修复常见的锚点问题
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE_DIR = Path("e:/_src/PostgreSQL_modern/PostgreSQL_Formal")
BACKUP_DIR = BASE_DIR / ".link_fix_backup"

# 常见修复规则
FIX_RULES = {
    # 模式: (正则匹配, 替换函数/字符串)
    'leading_dash': (re.compile(r'#-([^\s])'), r'#\1'),  # #-目录 -> #目录
    'duplicate_suffix': (re.compile(r'-(\d+)$'), ''),  # 范围查询性能-1 -> 范围查询性能
}

def slugify(text):
    """将标题转换为 GitHub 风格的锚点 ID"""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def extract_headers_from_file(file_path):
    """从文件中提取所有标题和对应的锚点"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {}
    
    headers = {}
    
    # 匹配标题
    header_pattern = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)
    for match in header_pattern.finditer(content):
        header_text = match.group(1).strip()
        # 移除行内代码标记
        clean_text = re.sub(r'`([^`]+)`', r'\1', header_text)
        anchor = slugify(clean_text)
        if anchor:
            headers[anchor] = clean_text
            # 同时保存原始形式（可能有特殊字符）
            raw_anchor = re.sub(r'\s+', '-', clean_text.lower()).strip('-')
            headers[raw_anchor] = clean_text
    
    return headers


def find_best_anchor_match(bad_anchor, available_anchors):
    """找到最匹配的锚点"""
    bad = bad_anchor.lower()
    
    # 1. 直接匹配
    if bad in available_anchors:
        return bad
    
    # 2. 移除 -数字 后缀后匹配
    cleaned = re.sub(r'-(\d+)$', '', bad)
    if cleaned in available_anchors:
        return cleaned
    
    # 3. 移除前导 - 后匹配
    if bad.startswith('-'):
        cleaned = bad[1:]
        if cleaned in available_anchors:
            return cleaned
    
    # 4. 替换特殊字符后匹配
    # 常见特殊字符映射
    char_map = {
        'σ': '', 'π': '', '∪': '', '−': '', '×': '', '⋈': '', '÷': '', 'ρ': '',
    }
    normalized = bad
    for char, replacement in char_map.items():
        normalized = normalized.replace(char.lower(), replacement)
    normalized = re.sub(r'-+', '-', normalized).strip('-')
    if normalized in available_anchors:
        return normalized
    
    # 5. 包含匹配
    for anchor in available_anchors:
        if bad in anchor or anchor in bad:
            return anchor
    
    return None


def auto_fix_links():
    """自动修复链接"""
    print("=" * 60)
    print("PostgreSQL_Formal 链接自动修复工具")
    print("=" * 60)
    
    # 创建备份目录
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # 预加载所有文件的标题锚点
    print("\n[1/3] 扫描所有文件标题...")
    all_headers = {}
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.md'):
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(BASE_DIR))
                headers = extract_headers_from_file(file_path)
                if headers:
                    all_headers[rel_path] = headers
    print(f"  已加载 {len(all_headers)} 个文件的标题信息")
    
    # 链接模式
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    # 需要修复的文件
    fixes_made = []
    
    # 定义问题链接
    problems = [
        # 文件路径, 行号, 失效链接, 链接文本
        ("00-NewFeatures-18/18.01-AIO-Formal.md", 13, "#-目录", "📑 目录"),
        ("00-NewFeatures-18/18.02-SkipScan-Analysis.md", 13, "#-目录", "📑 目录"),
        ("00-NewFeatures-18/18.03-UUIDv7-DEEP-V2.md", 58, "#范围查询性能-1", "范围查询性能"),
        ("00-NewFeatures-18/18.10-CloudNativePG-DEEP-V2.md", 97, "#总结-1", "总结"),
        ("00-NewFeatures-18/18.10-CloudNativePG-DEEP-V2.md", 98, "#参考公式汇总-1", "参考公式汇总"),
        ("00-Version-Specific/17-Released/INDEX.md", 22, "#-目录", "📋 目录"),
        ("00-Version-Specific/17-Released/INDEX.md", 23, "#-特性总览", "🎯 特性总览"),
        ("00-Version-Specific/17-Released/INDEX.md", 26, "#-完整文档列表", "📚 完整文档列表"),
        ("00-Version-Specific/17-Released/INDEX.md", 27, "#-性能优化类", "⚡ 性能优化类"),
        ("00-Version-Specific/17-Released/INDEX.md", 28, "#-运维备份类", "🔧 运维备份类"),
        ("00-Version-Specific/17-Released/INDEX.md", 29, "#️-安全监控类", "🛡️ 安全监控类"),
        ("00-Version-Specific/17-Released/INDEX.md", 30, "#-升级指南类", "📖 升级指南类"),
        ("00-Version-Specific/17-Released/INDEX.md", 31, "#-学习路径推荐", "🎓 学习路径推荐"),
        ("00-Version-Specific/17-Released/INDEX.md", 32, "#-dba-路径运维优先", "👨‍💼 DBA 路径（运维优先）"),
        ("00-Version-Specific/17-Released/INDEX.md", 33, "#-开发者路径功能优先", "👨‍💻 开发者路径（功能优先）"),
        ("00-Version-Specific/17-Released/INDEX.md", 34, "#️-架构师路径全局视野", "🏗️ 架构师路径（全局视野）"),
        ("00-Version-Specific/17-Released/INDEX.md", 35, "#-快速参考卡片", "📊 快速参考卡片"),
        ("00-Version-Specific/17-Released/INDEX.md", 36, "#-关键参数速查", "🔧 关键参数速查"),
        ("00-Version-Specific/17-Released/INDEX.md", 37, "#-升级检查清单", "✅ 升级检查清单"),
        ("00-Version-Specific/17-Released/INDEX.md", 38, "#-兼容性矩阵", "📈 兼容性矩阵"),
        ("00-Version-Specific/17-Released/INDEX.md", 39, "#-相关资源", "🔗 相关资源"),
        ("00-Version-Specific/17-Released/INDEX.md", 43, "#-版本信息", "📌 版本信息"),
        ("00-Version-Specific/18-Released/18.03-UUIDv7-DEEP-V2.md", 62, "#范围查询性能-1", "范围查询性能"),
        ("00-Version-Specific/18-Released/18.10-CloudNativePG-DEEP-V2.md", 104, "#总结-1", "总结"),
        ("00-Version-Specific/18-Released/18.10-CloudNativePG-DEEP-V2.md", 105, "#参考公式汇总-1", "参考公式汇总"),
        ("01-Theory/01.01-Relational-Algebra-DEEP-V2.md", 14, "#-目录", "📑 目录"),
        ("01-Theory/01.01-Relational-Algebra.md", 13, "#-目录", "📑 目录"),
        ("01-Theory/01.02-Transaction-Theory.md", 13, "#-目录", "📑 目录"),
        ("01-Theory/01.03-ACID-Formalization-DEEP-V2.md", 14, "#-目录", "📑 目录"),
        ("01-Theory/01.03-ACID-Formalization.md", 13, "#-目录", "📑 目录"),
        ("02-Storage/02.04-HeapAM-DEEP-V2.md", 14, "#-目录", "📑 目录"),
        ("02-Storage/02.05-Index-Types-Matrix-DEEP-V2.md", 14, "#-目录", "📑 目录"),
        ("04-Concurrency/01-MVCC-Formally-Specified.md", 13, "#-目录", "📑 目录"),
        ("04-Concurrency/04.05-Concurrency-Performance-DEEP-V2.md", 14, "#-目录", "📑 目录"),
        ("05-Distributed/05.04-2PC-3PC-Protocol-DEEP-V2.md", 14, "#-目录", "📑 目录"),
        ("06-FormalMethods/06.01-TLA-Model-Collection-DEEP-V2.md", 14, "#-目录", "📑 目录"),
        ("06-FormalMethods/06.02-Concept-Relation-Graph-DEEP-V2.md", 14, "#-目录", "📑 目录"),
        ("06-FormalMethods/06.03-Verification-Tools-DEEP-V2.md", 14, "#-目录", "📑 目录"),
        ("07-PracticalCases/09-AI-ML-Platform-DEEP-V2.md", 14, "#-目录", "📑 目录"),
        ("11-Database-Centric-Architecture/QUICKSTART.md", 24, "#-本指南目标", "🎯 本指南目标"),
        ("11-Database-Centric-Architecture/QUICKSTART.md", 25, "#-目录", "📚 目录"),
        ("11-Database-Centric-Architecture/QUICKSTART.md", 47, "#-总结", "🎉 总结"),
    ]
    
    print(f"\n[2/3] 准备修复 {len(problems)} 个问题...")
    
    # 按文件分组
    problems_by_file = defaultdict(list)
    for file_path, line, bad_link, link_text in problems:
        problems_by_file[file_path].append((line, bad_link, link_text))
    
    # 处理每个文件
    for file_path, issues in problems_by_file.items():
        full_path = BASE_DIR / file_path
        if not full_path.exists():
            print(f"  ⚠️ 文件不存在: {file_path}")
            continue
        
        try:
            # 备份文件
            backup_path = BACKUP_DIR / file_path.replace('/', '_').replace('\\', '_')
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            fixed_count = 0
            for line_num, bad_link, link_text in issues:
                # 计算修复后的锚点
                fixed_link = bad_link
                
                # 规则1: 移除前导 -
                if fixed_link.startswith('#-'):
                    fixed_link = '#' + fixed_link[2:]
                
                # 规则2: 移除 -数字 后缀
                fixed_link = re.sub(r'-(\d+)$', '', fixed_link)
                
                if fixed_link != bad_link:
                    # 查找并替换
                    # 匹配 [link_text](bad_link)
                    old_pattern = f'[{link_text}]({bad_link})'
                    new_pattern = f'[{link_text}]({fixed_link})'
                    
                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern)
                        fixes_made.append({
                            'file': file_path,
                            'line': line_num,
                            'old': bad_link,
                            'new': fixed_link,
                            'text': link_text
                        })
                        fixed_count += 1
                    else:
                        # 尝试不依赖链接文本的替换
                        # 只替换链接部分
                        pattern = f']({bad_link})'
                        replacement = f']({fixed_link})'
                        if pattern in content:
                            content = content.replace(pattern, replacement, 1)
                            fixes_made.append({
                                'file': file_path,
                                'line': line_num,
                                'old': bad_link,
                                'new': fixed_link,
                                'text': link_text
                            })
                            fixed_count += 1
            
            # 保存修改后的文件
            if fixed_count > 0:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ {file_path}: 修复了 {fixed_count} 个问题")
            else:
                print(f"  ℹ️ {file_path}: 未找到可修复的问题")
                
        except Exception as e:
            print(f"  ❌ {file_path}: 处理出错 - {e}")
    
    print(f"\n[3/3] 生成修复报告...")
    
    # 生成修复报告
    report_path = BASE_DIR / "LINK_FIX_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 链接自动修复报告\n\n")
        f.write(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 修复统计\n\n")
        f.write(f"- 修复文件数: {len(problems_by_file)}\n")
        f.write(f"- 修复链接数: {len(fixes_made)}\n\n")
        
        if fixes_made:
            f.write("## 修复详情\n\n")
            f.write("| 文件 | 行号 | 原链接 | 修复后 | 链接文本 |\n")
            f.write("|------|------|--------|--------|----------|\n")
            for fix in fixes_made:
                f.write(f"| {fix['file']} | {fix['line']} | `{fix['old']}` | `{fix['new']}` | {fix['text'][:20]}... |\n")
        
        f.write("\n## 备份信息\n\n")
        f.write(f"原始文件已备份到: `{BACKUP_DIR}`\n")
        f.write("如需恢复，请从备份目录复制回原位置。\n")
        
        f.write("\n## 仍需要手动修复的链接\n\n")
        f.write("以下链接需要人工检查:\n\n")
        manual_fixes = [
            ("00-NewFeatures-18/18.03-UUIDv7-DEEP-V2.md", "#48位时间戳--74位随机数结构", "特殊字符问题"),
            ("00-NewFeatures-18/18.09-pgvector-DEEP-V2.md", "#123-内积相似度-dot-product--inner-product", "序号和特殊字符"),
            ("00-Version-Specific/17-Released/17.07-Monitoring-Diagnostics-DEEP-V2.md", "#71-prometheus--grafana-配置更新", "序号格式问题"),
            ("00-Version-Specific/17-Released/17.08-Upgrade-Guide-DEEP-V2.md", "#22---link-模式-vs-复制模式", "特殊符号"),
            ("00-Version-Specific/17-Released/17.08-Upgrade-Guide-DEEP-V2.md", "#回滚方案-b-link-模式--逻辑备份回滚", "字母大小写"),
            ("00-Version-Specific/18-Released/18.03-UUIDv7-DEEP-V2.md", "#48位时间戳--74位随机数结构", "特殊字符问题"),
            ("00-Version-Specific/18-Released/18.09-pgvector-DEEP-V2.md", "#123-内积相似度-dot-product--inner-product", "序号和特殊字符"),
            ("01-Theory/01.01-Relational-Algebra-DEEP-V2.md", "#21-选择-selection---σ", "希腊字母"),
            ("01-Theory/01.01-Relational-Algebra-DEEP-V2.md", "#22-投影-projection---π", "希腊字母"),
            ("01-Theory/01.01-Relational-Algebra-DEEP-V2.md", "#23-并集-union---∪", "数学符号"),
            ("01-Theory/01.01-Relational-Algebra-DEEP-V2.md", "#24-集合差-set-difference---−", "数学符号"),
            ("01-Theory/01.01-Relational-Algebra-DEEP-V2.md", "#25-笛卡尔积-cartesian-product---×", "数学符号"),
            ("01-Theory/01.01-Relational-Algebra-DEEP-V2.md", "#26-自然连接-natural-join---⋈", "数学符号"),
            ("01-Theory/01.01-Relational-Algebra-DEEP-V2.md", "#27-重命名-rename---ρ", "希腊字母"),
            ("01-Theory/01.01-Relational-Algebra-DEEP-V2.md", "#28-除法-division---÷", "数学符号"),
            ("01-Theory/01.01-Relational-Algebra.md", "类似上述希腊字母和数学符号问题"),
            ("01-Theory/01.04-Isolation-Levels-Adya-DEEP-V2.md", "#隔离级别形式化---adya模型深度分析-v2", "标题不匹配"),
            ("01-Theory/01.04-Isolation-Levels-Adya-DEEP-V2.md", "#311-g0---脏写-dirty-write", "序号格式"),
            ("01-Theory/01.04-Isolation-Levels-Adya-DEEP-V2.md", "#312-g1---脏读-dirty-read", "序号格式"),
            ("01-Theory/01.04-Isolation-Levels-Adya-DEEP-V2.md", "#313-g2---反依赖环", "序号格式"),
            ("01-Theory/01.04-Isolation-Levels-Adya-DEEP-V2.md", "#314-g-si---快照隔离异常", "序号格式"),
            ("11-Database-Centric-Architecture/00-ROADMAP-AND-ACTION-PLAN-v2.md", "多个标题不匹配", "版本号格式问题"),
            ("11-Database-Centric-Architecture/03-Database-Testing-Framework-DEEP-V2.md", "#31--fixtures模式", "空格问题"),
            ("11-Database-Centric-Architecture/11-Migration-Strategy-Guide.md", "#21--strangler-fig模式-绞杀者模式", "空格问题"),
            ("11-Database-Centric-Architecture/15-Database-Notifications-DEEP-V2.md", "channel, data, notif.pid", "格式错误（应为代码块）"),
        ]
        for item in manual_fixes:
            if len(item) == 3:
                f.write(f"- `{item[0]}`: `{item[1]}` - {item[2]}\n")
            else:
                f.write(f"- `{item[0]}`: {item[1]}\n")
    
    print(f"  修复报告已保存: {report_path}")
    
    print("\n" + "=" * 60)
    print(f"修复完成! 共修复 {len(fixes_made)} 个链接")
    print("=" * 60)
    
    return fixes_made


if __name__ == '__main__':
    auto_fix_links()
