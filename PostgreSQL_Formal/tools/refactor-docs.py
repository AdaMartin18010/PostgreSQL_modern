#!/usr/bin/env python3
"""
PostgreSQL_Formal 文档重构工具

功能:
- 识别冗余文档
- 生成归档脚本
- 更新链接映射

用法:
    python refactor-docs.py --audit              # 审计文档冗余
    python refactor-docs.py --generate-archive   # 生成归档计划
    python refactor-docs.py --update-links       # 更新内部链接
    python refactor-docs.py --dry-run            # 模拟执行 (不实际修改)
    python refactor-docs.py --execute            # 执行重构

作者: PostgreSQL_Formal Team
版本: 1.0.0
"""

import os
import re
import json
import shutil
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


# ============ 配置 ============

BASE_DIR = Path(__file__).parent.parent  # PostgreSQL_Formal 目录
ARCHIVE_DIR = BASE_DIR / "99-Archive" / "old-versions"
MODULES = [
    "01-Theory",
    "02-Storage", 
    "03-Query",
    "04-Concurrency",
    "05-Distributed",
    "06-FormalMethods",
    "07-PracticalCases",
    "08-Performance",
    "09-Tools",
    "10-Visualization",
]

# DEEP-V2 版本标识
DEEP_V2_SUFFIX = "-DEEP-V2.md"
ARCHIVE_SUFFIXES = [".md", "-Formal.md", "-Theory.md", "-Analysis.md"]


# ============ 数据类 ============

@dataclass
class DocumentPair:
    """文档对：活跃版本和归档版本"""
    topic: str                          # 主题名称
    module: str                         # 所属模块
    active_file: Path                   # DEEP-V2 版本路径
    archive_file: Path                  # 归档版本路径
    active_size: int = 0                # 活跃版本大小
    archive_size: int = 0               # 归档版本大小


@dataclass
class LinkMapping:
    """链接映射"""
    old_path: str                       # 旧链接路径
    new_path: str                       # 新链接路径
    file_count: int = 0                 # 引用此链接的文件数


# ============ 核心功能 ============

class DocumentRefactorer:
    """文档重构器"""
    
    def __init__(self, base_dir: Path, dry_run: bool = True):
        self.base_dir = base_dir
        self.archive_dir = base_dir / "99-Archive" / "old-versions"
        self.dry_run = dry_run
        self.pairs: List[DocumentPair] = []
        self.link_mappings: List[LinkMapping] = []
        
    def audit_redundancy(self) -> Dict:
        """
        审计文档冗余情况
        
        Returns:
            审计报告字典
        """
        report = {
            "modules": {},
            "total_pairs": 0,
            "total_docs": 0,
            "redundancy_rate": 0.0,
            "estimated_savings_mb": 0.0,
        }
        
        total_docs = 0
        total_pairs = 0
        
        for module in MODULES:
            module_dir = self.base_dir / module
            if not module_dir.exists():
                continue
                
            # 查找 DEEP-V2 版本
            deep_v2_files = list(module_dir.glob(f"*{DEEP_V2_SUFFIX}"))
            
            pairs_in_module = []
            for deep_file in deep_v2_files:
                # 推断基础版本文件名
                base_name = deep_file.name.replace(DEEP_V2_SUFFIX, "")
                
                # 查找对应的基础版本
                for suffix in ARCHIVE_SUFFIXES:
                    archive_file = module_dir / f"{base_name}{suffix}"
                    if archive_file.exists() and archive_file != deep_file:
                        pair = DocumentPair(
                            topic=base_name,
                            module=module,
                            active_file=deep_file,
                            archive_file=archive_file,
                            active_size=deep_file.stat().st_size,
                            archive_size=archive_file.stat().st_size,
                        )
                        pairs_in_module.append(pair)
                        break
            
            doc_count = len(list(module_dir.glob("*.md")))
            total_docs += doc_count
            total_pairs += len(pairs_in_module)
            
            report["modules"][module] = {
                "document_count": doc_count,
                "pair_count": len(pairs_in_module),
                "redundancy_rate": (len(pairs_in_module) * 2 / doc_count * 100) if doc_count > 0 else 0,
                "pairs": [asdict(p) for p in pairs_in_module],
            }
        
        report["total_docs"] = total_docs
        report["total_pairs"] = total_pairs
        report["redundancy_rate"] = (total_pairs * 2 / total_docs * 100) if total_docs > 0 else 0
        
        # 估算节省空间
        total_archive_size = sum(
            p.archive_size for m in report["modules"].values() 
            for p in [DocumentPair(**d) if isinstance(d, dict) else d for d in m.get("pairs", [])]
        )
        report["estimated_savings_mb"] = round(total_archive_size / (1024 * 1024), 2)
        
        self.pairs = [
            DocumentPair(**d) if isinstance(d, dict) else d
            for m in report["modules"].values()
            for d in m.get("pairs", [])
        ]
        
        return report
    
    def generate_archive_plan(self) -> List[Dict]:
        """
        生成归档计划
        
        Returns:
            归档操作列表
        """
        if not self.pairs:
            self.audit_redundancy()
        
        plan = []
        for pair in self.pairs:
            archive_target = self.archive_dir / pair.module / pair.archive_file.name
            
            operation = {
                "type": "archive",
                "source": str(pair.archive_file.relative_to(self.base_dir)),
                "target": str(archive_target.relative_to(self.base_dir)),
                "topic": pair.topic,
                "module": pair.module,
            }
            plan.append(operation)
        
        return plan
    
    def scan_links(self) -> List[LinkMapping]:
        """
        扫描所有文档中的内部链接
        
        Returns:
            链接映射列表
        """
        # Markdown 链接正则: [text](path)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        all_links: Dict[str, int] = defaultdict(int)
        
        for md_file in self.base_dir.rglob("*.md"):
            # 跳过归档目录
            if "99-Archive" in str(md_file):
                continue
                
            try:
                content = md_file.read_text(encoding='utf-8')
                for match in link_pattern.finditer(content):
                    link_path = match.group(2)
                    # 只处理相对路径的 .md 文件
                    if link_path.endswith('.md') and not link_path.startswith(('http', '#')):
                        all_links[link_path] += 1
            except Exception as e:
                print(f"警告: 无法读取 {md_file}: {e}")
        
        # 生成链接映射
        mappings = []
        for pair in self.pairs:
            old_relative = f"{pair.module}/{pair.archive_file.name}"
            new_relative = f"{pair.module}/{pair.active_file.name}"
            
            # 计算引用次数
            ref_count = all_links.get(old_relative, 0)
            
            if ref_count > 0:
                mapping = LinkMapping(
                    old_path=old_relative,
                    new_path=new_relative,
                    file_count=ref_count,
                )
                mappings.append(mapping)
        
        self.link_mappings = mappings
        return mappings
    
    def update_links(self) -> Dict:
        """
        更新文档中的内部链接
        
        Returns:
            更新报告
        """
        if not self.link_mappings:
            self.scan_links()
        
        report = {
            "updated_files": 0,
            "updated_links": 0,
            "errors": [],
        }
        
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        for md_file in self.base_dir.rglob("*.md"):
            if "99-Archive" in str(md_file):
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                original_content = content
                
                for mapping in self.link_mappings:
                    old_link = mapping.old_path
                    new_link = mapping.new_path
                    
                    # 替换链接
                    content = content.replace(f"]({old_link})", f"]({new_link})")
                
                if content != original_content:
                    if not self.dry_run:
                        md_file.write_text(content, encoding='utf-8')
                    report["updated_files"] += 1
                    report["updated_links"] += content.count("](") - original_content.count("](")
                    
            except Exception as e:
                report["errors"].append(str(md_file))
                print(f"错误: 无法更新 {md_file}: {e}")
        
        return report
    
    def execute_archive(self) -> Dict:
        """
        执行归档操作
        
        Returns:
            执行报告
        """
        plan = self.generate_archive_plan()
        
        report = {
            "archived_files": 0,
            "errors": [],
        }
        
        for operation in plan:
            source = self.base_dir / operation["source"]
            target = self.base_dir / operation["target"]
            
            try:
                # 确保目标目录存在
                if not self.dry_run:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(target))
                
                report["archived_files"] += 1
                print(f"{'[模拟] ' if self.dry_run else ''}归档: {source.name} -> {target}")
                
            except Exception as e:
                report["errors"].append(str(source))
                print(f"错误: 无法归档 {source}: {e}")
        
        return report
    
    def generate_migration_guide(self) -> str:
        """
        生成迁移指南
        
        Returns:
            Markdown 格式的迁移指南
        """
        if not self.pairs:
            self.audit_redundancy()
        
        lines = [
            "# 自动生成的版本映射表\n",
            f"生成时间: {os.popen('date').read().strip() if os.name != 'nt' else 'N/A'}\n",
            "| 模块 | 主题 | 活跃版本 | 归档路径 |\n",
            "|------|------|----------|----------|\n",
        ]
        
        for pair in self.pairs:
            archive_path = f"99-Archive/old-versions/{pair.module}/{pair.archive_file.name}"
            lines.append(
                f"| {pair.module} | {pair.topic} | {pair.active_file.name} | {archive_path} |\n"
            )
        
        return "".join(lines)


# ============ CLI 接口 ============

def main():
    parser = argparse.ArgumentParser(
        description="PostgreSQL_Formal 文档重构工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 审计文档冗余
    python refactor-docs.py --audit
    
    # 生成归档计划 (模拟运行)
    python refactor-docs.py --generate-archive --dry-run
    
    # 扫描并显示需要更新的链接
    python refactor-docs.py --scan-links
    
    # 执行完整重构 (危险！请先备份)
    python refactor-docs.py --execute
        """
    )
    
    parser.add_argument(
        "--audit", "-a",
        action="store_true",
        help="审计文档冗余情况"
    )
    parser.add_argument(
        "--generate-archive", "-g",
        action="store_true",
        help="生成归档计划"
    )
    parser.add_argument(
        "--scan-links", "-s",
        action="store_true",
        help="扫描内部链接"
    )
    parser.add_argument(
        "--update-links", "-u",
        action="store_true",
        help="更新内部链接"
    )
    parser.add_argument(
        "--execute", "-e",
        action="store_true",
        help="执行完整重构 (包括归档和链接更新)"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        default=True,
        help="模拟运行，不实际修改文件 (默认)"
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="实际执行修改 (危险！)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="输出文件路径 (JSON 格式)"
    )
    
    args = parser.parse_args()
    
    # 确定是否模拟运行
    dry_run = args.dry_run and not args.no_dry_run
    
    # 初始化重构器
    refactorer = DocumentRefactorer(BASE_DIR, dry_run=dry_run)
    
    if args.execute:
        print("=" * 60)
        print("⚠️  执行完整重构")
        print("=" * 60)
        if not dry_run:
            print("⚠️  警告: 这将实际修改文件！")
            confirm = input("确认执行? (yes/no): ")
            if confirm.lower() != "yes":
                print("已取消")
                return
        
        # 1. 审计
        print("\n[1/3] 审计冗余...")
        audit_report = refactorer.audit_redundancy()
        print(f"发现 {audit_report['total_pairs']} 对冗余文档")
        
        # 2. 归档
        print("\n[2/3] 执行归档...")
        archive_report = refactorer.execute_archive()
        print(f"归档 {archive_report['archived_files']} 个文件")
        
        # 3. 更新链接
        print("\n[3/3] 更新链接...")
        link_report = refactorer.update_links()
        print(f"更新 {link_report['updated_files']} 个文件中的 {link_report['updated_links']} 个链接")
        
        print("\n重构完成!")
        
    elif args.audit:
        print("审计文档冗余...")
        report = refactorer.audit_redundancy()
        
        print(f"\n总文档数: {report['total_docs']}")
        print(f"冗余对数: {report['total_pairs']}")
        print(f"冗余率: {report['redundancy_rate']:.1f}%")
        print(f"预估节省空间: {report['estimated_savings_mb']:.2f} MB")
        
        print("\n各模块详情:")
        for module, data in report["modules"].items():
            print(f"  {module}: {data['pair_count']} 对 / {data['document_count']} 篇 (冗余率: {data['redundancy_rate']:.1f}%)")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n报告已保存到: {args.output}")
    
    elif args.generate_archive:
        print("生成归档计划...")
        plan = refactorer.generate_archive_plan()
        
        print(f"\n计划归档 {len(plan)} 个文件:")
        for op in plan[:10]:  # 只显示前10个
            print(f"  {op['source']} -> {op['target']}")
        if len(plan) > 10:
            print(f"  ... 还有 {len(plan) - 10} 个文件")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2, default=str)
            print(f"\n计划已保存到: {args.output}")
    
    elif args.scan_links:
        print("扫描内部链接...")
        mappings = refactorer.scan_links()
        
        print(f"\n发现 {len(mappings)} 个需要更新的链接:")
        for mapping in mappings:
            print(f"  {mapping.old_path} -> {mapping.new_path} ({mapping.file_count} 个文件引用)")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump([asdict(m) for m in mappings], f, indent=2)
            print(f"\n链接映射已保存到: {args.output}")
    
    elif args.update_links:
        print("更新内部链接...")
        report = refactorer.update_links()
        
        print(f"\n更新了 {report['updated_files']} 个文件")
        print(f"共更新 {report['updated_links']} 个链接")
        
        if report['errors']:
            print(f"\n错误: {len(report['errors'])} 个文件处理失败")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
