#!/usr/bin/env python3
"""
根目录文件归档脚本（非交互式版本）

功能:
1. 根据root_organize_report.md的建议自动归档文件
2. 创建归档目录结构
3. 移动文件到归档目录
4. 生成归档报告

使用方法:
    python archive_root_files.py --dry-run  # 预览模式
    python archive_root_files.py --execute  # 执行归档
"""

import re
import shutil
from pathlib import Path
import argparse


def parse_organize_report(report_file: str):
    """解析整理报告，提取归档建议"""

    report_path = Path(report_file)
    if not report_path.exists():
        print(f"错误: 报告文件不存在: {report_file}")
        return []

    content = report_path.read_text(encoding='utf-8')

    # 提取归档建议
    archive_suggestions = []

    # 匹配格式: `- `filename` → `target_path``
    pattern = r'- `([^`]+)` → `([^`]+)`'
    matches = re.findall(pattern, content)

    for filename, target_path in matches:
        archive_suggestions.append({
            'source': filename,
            'target': target_path
        })

    return archive_suggestions


def archive_files(suggestions: list, dry_run: bool = True):
    """执行文件归档"""

    if not suggestions:
        print("没有找到归档建议")
        return

    print(f"找到 {len(suggestions)} 个文件需要归档\n")

    # 创建归档目录
    archive_base = Path("99-Archive/根目录归档")
    subdirs = [
        "完成报告",
        "计划文档",
        "总结文档",
        "状态文档",
        "分析文档",
        "模板文档",
        "其他"
    ]

    if not dry_run:
        archive_base.mkdir(parents=True, exist_ok=True)
        for subdir in subdirs:
            (archive_base / subdir).mkdir(parents=True, exist_ok=True)
        print("✅ 已创建归档目录结构\n")

    # 归档文件
    success_count = 0
    skip_count = 0
    error_count = 0

    for suggestion in suggestions:
        source_file = Path(suggestion['source'])
        target_path = Path(suggestion['target'])

        # 构建完整目标路径
        # 从target_path中提取子目录名（去掉"99-Archive/根目录归档/"前缀）
        target_str = str(target_path)
        if target_str.startswith("99-Archive/根目录归档/"):
            target_str = target_str.replace("99-Archive/根目录归档/", "")
        elif target_str.startswith("99-Archive\\根目录归档\\"):
            target_str = target_str.replace("99-Archive\\根目录归档\\", "")

        target_path = archive_base / target_str

        if not source_file.exists():
            print(f"⚠️  跳过（文件不存在）: {source_file}")
            skip_count += 1
            continue

        if dry_run:
            print(f"📋 预览: {source_file} → {target_path}")
        else:
            try:
                # 确保目标目录存在
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # 移动文件
                shutil.move(str(source_file), str(target_path))
                print(f"✅ 已归档: {source_file} → {target_path}")
                success_count += 1
            except Exception as e:
                print(f"❌ 归档失败: {source_file} - {e}")
                error_count += 1

    print(f"\n{'='*60}")
    print(f"归档统计:")
    print(f"  成功: {success_count}")
    print(f"  跳过: {skip_count}")
    print(f"  失败: {error_count}")
    print(f"  总计: {len(suggestions)}")

    if not dry_run:
        print(f"\n✅ 归档完成！文件已移动到: {archive_base}")


def main():
    parser = argparse.ArgumentParser(description='根目录文件归档脚本')
    parser.add_argument('--report', type=str, default='root_organize_report.md',
                       help='整理报告文件路径')
    parser.add_argument('--dry-run', action='store_true',
                       help='预览模式，不实际移动文件')
    parser.add_argument('--execute', action='store_true',
                       help='执行模式，实际归档文件')

    args = parser.parse_args()

    if not args.execute and not args.dry_run:
        print("请指定 --dry-run 或 --execute")
        return

    # 解析报告
    suggestions = parse_organize_report(args.report)

    if not suggestions:
        print("未找到归档建议，请先运行 root_directory_organizer.py")
        return

    # 执行归档
    archive_files(suggestions, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
