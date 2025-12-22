#!/usr/bin/env python3
"""
代码示例性能测试补充工具

功能:
1. 扫描Markdown文档中的代码示例
2. 识别需要性能测试的代码
3. 生成性能测试代码模板
4. 生成性能测试报告模板

使用方法:
    python code_example_performance_tester.py --root docs --output performance_test_report.md
"""

import re
from pathlib import Path
import argparse
from typing import List, Dict, Tuple


def find_code_blocks(content: str) -> List[Tuple[int, str, str]]:
    """查找所有代码块"""

    code_blocks = []
    pattern = r'```(\w+)?\n(.*?)```'

    for match in re.finditer(pattern, content, re.DOTALL):
        language = match.group(1) or 'text'
        code = match.group(2)
        start_pos = match.start()
        line_num = content[:start_pos].count('\n') + 1

        code_blocks.append((line_num, language, code))

    return code_blocks


def analyze_code_for_performance_test(code: str, language: str) -> Dict:
    """分析代码是否需要性能测试"""

    needs_test = False
    test_type = None
    suggestions = []

    # SQL代码分析
    if language.lower() in ['sql', 'postgresql', 'psql']:
        # 检查是否有查询操作
        if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER)\b', code, re.IGNORECASE):
            needs_test = True
            test_type = 'query'
            suggestions.append('添加查询性能测试（EXPLAIN ANALYZE）')

        # 检查是否有索引操作
        if re.search(r'\b(CREATE INDEX|REINDEX|DROP INDEX)\b', code, re.IGNORECASE):
            needs_test = True
            test_type = 'index'
            suggestions.append('添加索引构建性能测试')

        # 检查是否有批量操作
        if re.search(r'\b(COPY|INSERT.*SELECT|BULK)\b', code, re.IGNORECASE):
            needs_test = True
            test_type = 'bulk'
            suggestions.append('添加批量操作性能测试')

    # Python代码分析
    elif language.lower() == 'python':
        # 检查是否有数据库操作
        if re.search(r'\b(psycopg|execute|fetchall|fetchone)\b', code, re.IGNORECASE):
            needs_test = True
            test_type = 'database'
            suggestions.append('添加数据库操作性能测试')

        # 检查是否有循环操作
        if re.search(r'\b(for|while|loop)\b', code, re.IGNORECASE):
            needs_test = True
            test_type = 'loop'
            suggestions.append('添加循环性能测试')

    return {
        'needs_test': needs_test,
        'test_type': test_type,
        'suggestions': suggestions
    }


def generate_performance_test_template(code: str, language: str, test_type: str) -> str:
    """生成性能测试代码模板"""

    if language.lower() in ['sql', 'postgresql', 'psql']:
        if test_type == 'query':
            return f"""-- 性能测试：查询性能
EXPLAIN (ANALYZE, BUFFERS, TIMING)
{code}

-- 性能指标：
-- - 执行时间
-- - 扫描行数
-- - 缓冲区命中率
-- - I/O时间"""

        elif test_type == 'index':
            return f"""-- 性能测试：索引构建性能
\\timing on
{code}
\\timing off

-- 性能指标：
-- - 构建时间
-- - 索引大小
-- - 内存使用"""

        elif test_type == 'bulk':
            return f"""-- 性能测试：批量操作性能
\\timing on
{code}
\\timing off

-- 性能指标：
-- - 插入时间
-- - 吞吐量（行/秒）
-- - WAL生成量"""

    elif language.lower() == 'python':
        return f"""# 性能测试：数据库操作性能
import time
import psycopg2

# 连接数据库
conn = psycopg2.connect(...)
cursor = conn.cursor()

# 开始计时
start_time = time.time()

# 原代码
{code}

# 结束计时
end_time = time.time()
elapsed_time = end_time - start_time

print(f"执行时间: {{elapsed_time:.3f}}秒")
print(f"吞吐量: {{rows_per_second:.0f}} 行/秒")

# 性能指标：
# - 执行时间
# - 吞吐量
# - 内存使用
# - CPU使用率"""

    return ""


def scan_documents(root_dir: str) -> List[Dict]:
    """扫描文档并分析代码示例"""

    root_path = Path(root_dir)
    results = []

    for md_file in root_path.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            code_blocks = find_code_blocks(content)

            for line_num, language, code in code_blocks:
                analysis = analyze_code_for_performance_test(code, language)

                if analysis['needs_test']:
                    results.append({
                        'file': str(md_file.relative_to(root_path)),
                        'line': line_num,
                        'language': language,
                        'code': code[:200],
                        'test_type': analysis['test_type'],
                        'suggestions': analysis['suggestions']
                    })
        except Exception as e:
            print(f"处理文件失败 {md_file}: {e}")

    return results


def generate_report(results: List[Dict], output_file: str):
    """生成性能测试报告"""

    report_lines = [
        "# 代码示例性能测试补充报告",
        "",
        f"> **生成日期**: 2025年1月",
        f"> **扫描结果**: 找到 {len(results)} 个需要添加性能测试的代码示例",
        "",
        "---",
        "",
        "## 📊 统计信息",
        "",
        f"- **需要性能测试的代码示例**: {len(results)} 个",
        "",
        "## 📋 需要性能测试的代码示例",
        ""
    ]

    # 按文件分组
    by_file = {}
    for result in results:
        file_path = result['file']
        if file_path not in by_file:
            by_file[file_path] = []
        by_file[file_path].append(result)

    # 生成报告
    for file_path, file_results in sorted(by_file.items()):
        report_lines.append(f"### {file_path}")
        report_lines.append("")

        for result in file_results:
            report_lines.append(f"**行 {result['line']}** ({result['language']}, {result['test_type']}):")
            report_lines.append("")
            report_lines.append("```" + result['language'])
            report_lines.append(result['code'])
            report_lines.append("```")
            report_lines.append("")
            report_lines.append("**建议**:")
            for suggestion in result['suggestions']:
                report_lines.append(f"- {suggestion}")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

    # 写入报告
    output_path = Path(output_file)
    output_path.write_text('\n'.join(report_lines), encoding='utf-8')
    print(f"✅ 报告已保存到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='代码示例性能测试补充工具')
    parser.add_argument('--root', type=str, default='docs',
                       help='扫描根目录')
    parser.add_argument('--output', type=str, default='performance_test_report.md',
                       help='输出报告文件')

    args = parser.parse_args()

    print(f"扫描目录: {args.root}")
    print("分析代码示例...")

    results = scan_documents(args.root)

    print(f"找到 {len(results)} 个需要添加性能测试的代码示例")

    generate_report(results, args.output)

    print("✅ 完成！")


if __name__ == '__main__':
    main()
