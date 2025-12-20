#!/usr/bin/env python3
"""
代码示例运行验证工具

功能:
1. 扫描Markdown文档中的代码示例
2. 验证代码语法正确性
3. 生成验证报告
4. 标记不可运行的代码

使用方法:
    python code_example_validator.py --root docs --output validation_report.md
"""

import re
import ast
import subprocess
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


def validate_sql_syntax(code: str) -> Tuple[bool, str]:
    """验证SQL语法（基础检查）"""

    # 检查基本SQL语法错误
    issues = []

    # 检查括号匹配
    if code.count('(') != code.count(')'):
        issues.append('括号不匹配')

    # 检查引号匹配
    single_quotes = code.count("'") - code.count("''")
    if single_quotes % 2 != 0:
        issues.append('单引号不匹配')

    # 检查基本关键字
    if re.search(r'\bSELECT\b', code, re.IGNORECASE):
        if not re.search(r'\bFROM\b', code, re.IGNORECASE):
            issues.append('SELECT语句缺少FROM子句')

    if issues:
        return False, '; '.join(issues)
    return True, ''


def validate_python_syntax(code: str) -> Tuple[bool, str]:
    """验证Python语法"""

    try:
        ast.parse(code)
        return True, ''
    except SyntaxError as e:
        return False, f"语法错误: {e.msg} (行 {e.lineno})"
    except Exception as e:
        return False, f"解析错误: {str(e)}"


def validate_bash_syntax(code: str) -> Tuple[bool, str]:
    """验证Bash语法（基础检查）"""

    issues = []

    # 检查基本语法错误
    if re.search(r'if\s*\[', code) and not re.search(r'\]', code):
        issues.append('if语句缺少结束括号')

    # 检查变量引用
    if re.search(r'\$\{[^}]+\}', code):
        # 检查未闭合的变量引用
        if code.count('${') != code.count('}'):
            issues.append('变量引用不匹配')

    if issues:
        return False, '; '.join(issues)
    return True, ''


def validate_code(code: str, language: str) -> Tuple[bool, str]:
    """验证代码语法"""

    if language.lower() in ['sql', 'postgresql', 'psql']:
        return validate_sql_syntax(code)
    elif language.lower() == 'python':
        return validate_python_syntax(code)
    elif language.lower() in ['bash', 'shell', 'sh']:
        return validate_bash_syntax(code)
    else:
        # 其他语言暂不验证
        return True, ''


def scan_documents(root_dir: str) -> List[Dict]:
    """扫描文档并验证代码示例"""

    root_path = Path(root_dir)
    results = []

    for md_file in root_path.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            code_blocks = find_code_blocks(content)

            for line_num, language, code in code_blocks:
                # 跳过太短的代码块
                if len(code.strip()) < 10:
                    continue

                # 跳过注释块
                if code.strip().startswith('#'):
                    continue

                is_valid, error_msg = validate_code(code, language)

                if not is_valid:
                    results.append({
                        'file': str(md_file.relative_to(root_path)),
                        'line': line_num,
                        'language': language,
                        'code': code[:200],
                        'error': error_msg
                    })
        except Exception as e:
            print(f"处理文件失败 {md_file}: {e}")

    return results


def generate_report(results: List[Dict], output_file: str):
    """生成验证报告"""

    report_lines = [
        "# 代码示例运行验证报告",
        "",
        f"> **生成日期**: 2025年1月",
        f"> **扫描结果**: 找到 {len(results)} 个可能有语法错误的代码示例",
        "",
        "---",
        "",
        "## 📊 统计信息",
        "",
        f"- **需要修复的代码示例**: {len(results)} 个",
        "",
        "## 📋 需要修复的代码示例",
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
            report_lines.append(f"**行 {result['line']}** ({result['language']}):")
            report_lines.append("")
            report_lines.append("```" + result['language'])
            report_lines.append(result['code'])
            report_lines.append("```")
            report_lines.append("")
            report_lines.append(f"**错误**: {result['error']}")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

    # 写入报告
    output_path = Path(output_file)
    output_path.write_text('\n'.join(report_lines), encoding='utf-8')
    print(f"✅ 报告已保存到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='代码示例运行验证工具')
    parser.add_argument('--root', type=str, default='docs',
                       help='扫描根目录')
    parser.add_argument('--output', type=str, default='code_validation_report.md',
                       help='输出报告文件')

    args = parser.parse_args()

    print(f"扫描目录: {args.root}")
    print("验证代码示例...")

    results = scan_documents(args.root)

    print(f"找到 {len(results)} 个可能有语法错误的代码示例")

    generate_report(results, args.output)

    print("✅ 完成！")


if __name__ == '__main__':
    main()
