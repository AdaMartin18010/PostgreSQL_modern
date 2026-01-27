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
import os
import stat


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

    def _ensure_writable(path: Path) -> None:
        """尽量去掉只读属性，避免 Windows 上无法移动/删除。"""
        try:
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        except Exception:
            pass

    def _unique_file_path(path: Path) -> Path:
        """如目标文件已存在，则生成不冲突的新文件路径（追加 __dupN）。"""
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        n = 1
        while True:
            candidate = parent / f"{stem}__dup{n}{suffix}"
            if not candidate.exists():
                return candidate
            n += 1

    # 创建归档目录（对齐项目现有 archive/ 体系）
    archive_base = Path("archive/根目录归档")
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
        # 从target_path中提取子目录名（兼容旧前缀 99-Archive/根目录归档/ 与新前缀 archive/根目录归档/）
        target_str = str(target_path)
        if target_str.startswith("99-Archive/根目录归档/"):
            target_str = target_str.replace("99-Archive/根目录归档/", "")
        elif target_str.startswith("99-Archive\\根目录归档\\"):
            target_str = target_str.replace("99-Archive\\根目录归档\\", "")
        elif target_str.startswith("archive/根目录归档/"):
            target_str = target_str.replace("archive/根目录归档/", "")
        elif target_str.startswith("archive\\根目录归档\\"):
            target_str = target_str.replace("archive\\根目录归档\\", "")

        # 报告里通常给的是“目标目录”（以 / 或 \ 结尾），也兼容直接给出“目标文件路径”
        target_clean = target_str.strip("\\/").strip()
        target_path = archive_base / target_clean

        if target_path.suffix.lower() == ".md":
            # 目标是文件路径
            dest_dir = target_path.parent
            dest_file = _unique_file_path(target_path)
        else:
            # 目标是目录路径：文件名沿用原文件名
            dest_dir = target_path
            dest_file = _unique_file_path(dest_dir / source_file.name)

        if not source_file.exists():
            print(f"⚠️  跳过（文件不存在）: {source_file}")
            skip_count += 1
            continue

        if dry_run:
            print(f"📋 预览: {source_file} → {dest_file}")
        else:
            try:
                # 确保目标目录存在
                dest_dir.mkdir(parents=True, exist_ok=True)

                # Windows 下很多文件可能带只读属性，先尝试去掉
                _ensure_writable(source_file)

                # 优先尝试原子重命名（同盘最快）
                try:
                    source_file.replace(dest_file)
                except Exception:
                    # 回退到 copy + delete（避免部分环境下 rename 受限）
                    shutil.copy2(str(source_file), str(dest_file))
                    try:
                        source_file.unlink()
                    except Exception:
                        _ensure_writable(source_file)
                        source_file.unlink()

                print(f"✅ 已归档: {source_file} → {dest_file}")
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
