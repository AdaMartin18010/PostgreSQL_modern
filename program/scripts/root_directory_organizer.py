#!/usr/bin/env python3
"""
根目录文件整理工具

功能:
1. 扫描根目录的所有Markdown文件
2. 根据文件名模式分类
3. 生成整理建议
4. 执行归档操作（可选）

使用方法:
    python root_directory_organizer.py [--dry-run] [--execute]
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
import argparse
import shutil


class RootDirectoryOrganizer:
    """根目录文件整理器"""
    
    def __init__(self, root_dir: str):
        """初始化整理器"""
        self.root_dir = Path(root_dir)
        # 统一使用项目现有的 archive/ 体系，避免引入新的 99-Archive/
        self.archive_dir = self.root_dir / "archive" / "根目录归档"
        self.files: Dict[str, Dict] = {}
        # 根目录必须保留的入口/核心文档（这些文件通常被 README/导航引用）
        self.keep_files = {
            "README.md",
            "PROJECT-SUMMARY.md",
            "START-HERE.md",
            "QUICKSTART.md",
            "QUICK-REFERENCE.md",
            "CHANGELOG.md",
            "WHATS-NEW.md",
            "ROADMAP-2025.md",
            "LEARNING-PATH.md",
            "BEST-PRACTICES.md",
            "FAQ.md",
            "CONTRIBUTING.md",
            "COMPLETION-REPORT.md",
            "FINAL-MILESTONE.md",
        }
        
    def scan_root_files(self) -> None:
        """扫描根目录文件"""
        print(f"扫描根目录: {self.root_dir}")
        
        # 只扫描根目录的Markdown文件
        md_files = [f for f in self.root_dir.glob("*.md") if f.is_file()]
        print(f"找到 {len(md_files)} 个Markdown文件")
        
        for md_file in md_files:
            rel_path = str(md_file.name)
            category = self.categorize_file(md_file.name)
            
            try:
                # 读取文件前几行获取信息
                with open(md_file, 'r', encoding='utf-8') as f:
                    first_lines = ''.join([f.readline() for _ in range(5)])
                
                self.files[rel_path] = {
                    'path': md_file,
                    'category': category,
                    'size': md_file.stat().st_size,
                    'preview': first_lines[:200]
                }
            except Exception as e:
                print(f"警告: 无法读取 {md_file}: {e}")
        
        print(f"成功分类 {len(self.files)} 个文件")
    
    def categorize_file(self, filename: str) -> str:
        """根据文件名分类"""
        filename_lower = filename.lower()

        # 入口/核心文档：强制保留在根目录
        if filename in self.keep_files:
            return '入口文档'
        
        # 完成报告类
        if any(keyword in filename for keyword in ['完成', '完成报告', '完成总结', '最终完成', '圆满完成', 'COMPLETE']):
            return '完成报告'
        
        # 计划类
        if any(keyword in filename for keyword in ['计划', '规划', '推进计划', 'ROADMAP', 'PLAN']):
            return '计划文档'
        
        # 总结类
        if any(keyword in filename for keyword in ['总结', '总结报告', '工作总结', 'SUMMARY']):
            return '总结文档'
        
        # 状态类
        if any(keyword in filename for keyword in ['状态', '状态确认', 'STATUS']):
            return '状态文档'
        
        # 分析类
        if any(keyword in filename for keyword in ['分析', '分析报告', '评估', 'ANALYSIS']):
            return '分析文档'
        
        # 导航类
        if any(keyword in filename for keyword in ['导航', 'NAVIGATION', '地图', 'MAP']):
            return '导航文档'
        
        # 快速开始类
        if any(keyword in filename for keyword in ['快速', 'QUICK', 'START', '上手指南']):
            return '快速开始'
        
        # 用户手册类
        if any(keyword in filename for keyword in ['手册', 'MANUAL', '使用手册', '指南']):
            return '用户手册'
        
        # 模板类
        if any(keyword in filename for keyword in ['模板', 'TEMPLATE']):
            return '模板文档'
        
        # 其他
        return '其他'
    
    def generate_organize_plan(self) -> Dict[str, List[str]]:
        """生成整理计划"""
        plan = defaultdict(list)
        
        for filename, info in self.files.items():
            category = info['category']
            plan[category].append(filename)
        
        return dict(plan)
    
    def generate_report(self, output_file: str = "root_organize_report.md", dry_run: bool = True) -> None:
        """生成整理报告"""
        print(f"生成报告: {output_file}")
        
        plan = self.generate_organize_plan()
        
        report_lines = [
            "# 根目录文件整理报告",
            "",
            f"**生成时间**: {Path(__file__).stat().st_mtime}",
            f"**扫描文件数**: {len(self.files)}",
            f"**模式**: {'预览模式（不执行）' if dry_run else '执行模式'}",
            "",
            "---",
            "",
            "## 📊 文件分类统计",
            "",
        ]
        
        # 统计
        for category, files in sorted(plan.items()):
            report_lines.append(f"- **{category}**: {len(files)} 个文件")
        
        report_lines.extend([
            "",
            "---",
            "",
            "## 📁 文件分类详情",
            "",
        ])
        
        # 详细列表
        for category, files in sorted(plan.items()):
            report_lines.extend([
                f"### {category} ({len(files)} 个文件)",
                ""
            ])
            
            for filename in sorted(files):
                info = self.files[filename]
                size_kb = info['size'] / 1024
                report_lines.extend([
                    f"- **`{filename}`** ({size_kb:.1f} KB)",
                    f"  - 建议操作: {'保留在根目录' if category in ['入口文档', '导航文档', '快速开始', '用户手册'] else '归档到archive/根目录归档/' + category}",
                    ""
                ])
        
        # 归档建议
        report_lines.extend([
            "",
            "---",
            "",
            "## 📋 归档建议",
            "",
            "### 建议保留在根目录的文件",
            "",
            "以下文件应该保留在根目录，因为它们是用户入口文档：",
            "",
        ])
        
        keep_categories = ['入口文档', '导航文档', '快速开始', '用户手册']
        keep_files = []
        for category in keep_categories:
            if category in plan:
                keep_files.extend(plan[category])
        
        for filename in sorted(keep_files):
            report_lines.append(f"- `{filename}`")
        
        report_lines.extend([
            "",
            "### 建议归档的文件",
            "",
            "以下文件建议归档到 `archive/根目录归档/` 目录：",
            "",
        ])
        
        archive_categories = ['完成报告', '计划文档', '总结文档', '状态文档', '分析文档', '模板文档', '其他']
        archive_files = []
        for category in archive_categories:
            if category in plan:
                archive_files.extend(plan[category])
        
        for filename in sorted(archive_files):
            info = self.files[filename]
            category = info['category']
            # 仅输出需要归档的文件（入口/导航/快速开始/用户手册不在此列表）
            if category in keep_categories:
                continue
            report_lines.append(f"- `{filename}` → `archive/根目录归档/{category}/`")
        
        # 执行步骤
        report_lines.extend([
            "",
            "---",
            "",
            "## 🔧 执行步骤",
            "",
            "### 步骤1: 创建归档目录",
            "",
            "```bash",
            "mkdir -p archive/根目录归档/{完成报告,计划文档,总结文档,状态文档,分析文档,模板文档,其他}",
            "```",
            "",
            "### 步骤2: 移动文件",
            "",
            "```bash",
        ])
        
        for filename in sorted(archive_files):
            info = self.files[filename]
            category = info['category']
            if category in keep_categories:
                continue
            report_lines.append(f"mv \"{filename}\" \"archive/根目录归档/{category}/\"")
        
        report_lines.extend([
            "```",
            "",
            "### 步骤3: 更新链接",
            "",
            "- [ ] 更新README.md中的链接",
            "- [ ] 更新导航文档中的链接",
            "- [ ] 检查所有文档中的内部链接",
            "",
            "---",
            "",
            "## ⚠️ 注意事项",
            "",
            "1. **备份**: 执行归档前请先备份",
            "2. **链接更新**: 归档后需要更新所有引用链接",
            "3. **Git历史**: 使用Git管理时，文件历史会保留",
            "",
            "---",
            "",
            "**报告生成工具**: `scripts/root_directory_organizer.py`",
            ""
        ])
        
        output_path = self.root_dir / output_file
        output_path.write_text('\n'.join(report_lines), encoding='utf-8')
        print(f"报告已保存到: {output_path}")
    
    def execute_organize(self) -> None:
        """执行归档操作"""
        print("执行归档操作...")
        
        # 创建归档目录
        archive_categories = ['完成报告', '计划文档', '总结文档', '状态文档', '分析文档', '模板文档', '其他']
        for category in archive_categories:
            (self.archive_dir / category).mkdir(parents=True, exist_ok=True)
        
        # 移动文件
        plan = self.generate_organize_plan()
        archive_categories_list = ['完成报告', '计划文档', '总结文档', '状态文档', '分析文档', '模板文档', '其他']
        
        moved_count = 0
        for category in archive_categories_list:
            if category in plan:
                for filename in plan[category]:
                    source = self.files[filename]['path']
                    dest = self.archive_dir / category / filename
                    
                    try:
                        shutil.move(str(source), str(dest))
                        print(f"已移动: {filename} → {dest}")
                        moved_count += 1
                    except Exception as e:
                        print(f"错误: 无法移动 {filename}: {e}")
        
        print(f"\n✅ 归档完成！共移动 {moved_count} 个文件")


def main():
    parser = argparse.ArgumentParser(description='根目录文件整理工具')
    parser.add_argument('--root', type=str, default='.', help='项目根目录')
    parser.add_argument('--output', type=str, default='root_organize_report.md', help='输出报告文件名')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不执行归档')
    parser.add_argument('--execute', action='store_true', help='执行模式，实际移动文件')
    
    args = parser.parse_args()
    
    organizer = RootDirectoryOrganizer(args.root)
    organizer.scan_root_files()
    organizer.generate_report(args.output, dry_run=args.dry_run)
    
    if args.execute:
        response = input("\n⚠️  确定要执行归档操作吗？这将移动文件到归档目录。 (yes/no): ")
        if response.lower() == 'yes':
            organizer.execute_organize()
        else:
            print("操作已取消")
    else:
        print("\n✅ 预览模式完成！")
        print("📄 报告已保存，请查看归档建议")
        print("💡 要执行归档，请使用: python root_directory_organizer.py --execute")


if __name__ == '__main__':
    main()
