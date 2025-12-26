#!/usr/bin/env python3
"""
检查文档中代码示例的错误处理和性能测试状态
用于识别需要改进的文档
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def count_code_blocks(content: str) -> Dict[str, int]:
    """统计代码块数量"""
    patterns = {
        'sql': r'```sql',
        'python': r'```python',
        'bash': r'```bash',
        'c': r'```c',
        'javascript': r'```javascript',
    }
    counts = {}
    for lang, pattern in patterns.items():
        counts[lang] = len(re.findall(pattern, content, re.IGNORECASE))
    counts['total'] = sum(counts.values())
    return counts

def count_error_handling(content: str) -> Dict[str, int]:
    """统计错误处理标记数量"""
    patterns = {
        'do_block': r'DO\s+\$\$',
        'begin_exception': r'BEGIN\s+.*?EXCEPTION',
        'try_except': r'try\s*:.*?except',
        'error_exit': r'error_exit\s*\(',
        'set_e': r'set\s+-e',
    }
    counts = {}
    for name, pattern in patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        counts[name] = len(matches)
    counts['total'] = sum(counts.values())
    return counts

def count_performance_test(content: str) -> Dict[str, int]:
    """统计性能测试标记数量"""
    patterns = {
        'explain_analyze': r'EXPLAIN\s+.*?ANALYZE',
        'explain_buffers': r'EXPLAIN\s+.*?BUFFERS',
        'explain_timing': r'EXPLAIN\s+.*?TIMING',
    }
    counts = {}
    for name, pattern in patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        counts[name] = len(matches)
    counts['total'] = sum(counts.values())
    return counts

def analyze_document(file_path: Path) -> Dict:
    """分析单个文档"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}

    code_blocks = count_code_blocks(content)
    error_handling = count_error_handling(content)
    performance_test = count_performance_test(content)

    # 计算覆盖率
    total_blocks = code_blocks.get('total', 0)
    total_error = error_handling.get('total', 0)
    total_perf = performance_test.get('total', 0)

    # 估算覆盖率（粗略）
    # SQL块通常需要DO块+EXCEPTION，查询需要EXPLAIN
    sql_blocks = code_blocks.get('sql', 0)
    estimated_needed_error = sql_blocks * 0.8  # 80%的SQL块需要错误处理
    estimated_needed_perf = sql_blocks * 0.5  # 50%的SQL块是查询，需要性能测试

    error_coverage = (total_error / estimated_needed_error * 100) if estimated_needed_error > 0 else 100
    perf_coverage = (total_perf / estimated_needed_perf * 100) if estimated_needed_perf > 0 else 100

    # 判断是否需要改进
    needs_improvement = (
        total_blocks > 0 and (
            error_coverage < 80 or
            perf_coverage < 50
        )
    )

    return {
        'file_path': str(file_path),
        'code_blocks': code_blocks,
        'error_handling': error_handling,
        'performance_test': performance_test,
        'error_coverage': round(error_coverage, 1),
        'perf_coverage': round(perf_coverage, 1),
        'needs_improvement': needs_improvement,
        'total_blocks': total_blocks,
        'total_error': total_error,
        'total_perf': total_perf,
    }

def scan_directory(root_dir: Path) -> List[Dict]:
    """扫描目录下的所有Markdown文档"""
    results = []
    for md_file in root_dir.rglob('*.md'):
        # 跳过某些目录
        if any(skip in str(md_file) for skip in ['archive', '00-归档', 'README.md']):
            continue

        result = analyze_document(md_file)
        if 'error' not in result:
            results.append(result)

    return results

def main():
    if len(sys.argv) < 2:
        root_dir = Path('Integrate')
    else:
        root_dir = Path(sys.argv[1])

    if not root_dir.exists():
        print(f"错误: 目录不存在: {root_dir}")
        sys.exit(1)

    print(f"扫描目录: {root_dir}")
    print("=" * 80)

    results = scan_directory(root_dir)

    # 分类结果
    needs_improvement = [r for r in results if r.get('needs_improvement', False)]
    good_coverage = [r for r in results if not r.get('needs_improvement', False) and r.get('total_blocks', 0) > 0]
    no_code = [r for r in results if r.get('total_blocks', 0) == 0]

    print(f"\n总计: {len(results)} 个文档")
    print(f"需要改进: {len(needs_improvement)} 个文档")
    print(f"覆盖率良好: {len(good_coverage)} 个文档")
    print(f"无代码块: {len(no_code)} 个文档")

    # 输出需要改进的文档
    if needs_improvement:
        print("\n" + "=" * 80)
        print("需要改进的文档:")
        print("=" * 80)
        for r in sorted(needs_improvement, key=lambda x: x.get('error_coverage', 0)):
            print(f"\n{r['file_path']}")
            print(f"  代码块: {r['total_blocks']} (SQL: {r['code_blocks'].get('sql', 0)})")
            print(f"  错误处理: {r['total_error']} (覆盖率: {r['error_coverage']}%)")
            print(f"  性能测试: {r['total_perf']} (覆盖率: {r['perf_coverage']}%)")

    # 生成报告文件
    report_file = root_dir.parent / 'code_example_status_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 代码示例状态检查报告\n\n")
        f.write(f"**扫描目录**: {root_dir}\n")
        f.write(f"**扫描时间**: {Path(__file__).stat().st_mtime}\n\n")
        f.write(f"## 统计摘要\n\n")
        f.write(f"- 总计文档: {len(results)}\n")
        f.write(f"- 需要改进: {len(needs_improvement)}\n")
        f.write(f"- 覆盖率良好: {len(good_coverage)}\n")
        f.write(f"- 无代码块: {len(no_code)}\n\n")

        if needs_improvement:
            f.write("## 需要改进的文档\n\n")
            f.write("| 文档路径 | 代码块数 | 错误处理 | 错误覆盖率 | 性能测试 | 性能覆盖率 |\n")
            f.write("|---------|---------|---------|-----------|---------|-----------|\n")
            for r in sorted(needs_improvement, key=lambda x: x.get('error_coverage', 0)):
                f.write(f"| {r['file_path']} | {r['total_blocks']} | {r['total_error']} | {r['error_coverage']}% | {r['total_perf']} | {r['perf_coverage']}% |\n")

    print(f"\n报告已保存到: {report_file}")

if __name__ == '__main__':
    main()
