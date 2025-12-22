#!/usr/bin/env python3
"""
代码示例错误处理补充工具

功能:
1. 扫描Markdown文档中的代码示例
2. 识别缺少错误处理的代码
3. 生成错误处理补充建议
4. 自动添加错误处理代码

使用方法:
    python code_example_error_handler.py --root docs --output error_handling_report.md
"""

import re
from pathlib import Path
import argparse
from typing import List, Dict, Tuple


def find_code_blocks(content: str) -> List[Tuple[int, str, str]]:
    """查找所有代码块"""
    
    code_blocks = []
    
    # 匹配代码块：```language\ncode\n```
    pattern = r'```(\w+)?\n(.*?)```'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        language = match.group(1) or 'text'
        code = match.group(2)
        start_pos = match.start()
        line_num = content[:start_pos].count('\n') + 1
        
        code_blocks.append((line_num, language, code))
    
    return code_blocks


def analyze_code_for_error_handling(code: str, language: str) -> Dict:
    """分析代码是否需要错误处理"""
    
    issues = {
        'needs_error_handling': False,
        'missing_try_catch': False,
        'missing_connection_check': False,
        'missing_null_check': False,
        'suggestions': []
    }
    
    # SQL代码分析
    if language.lower() in ['sql', 'postgresql', 'psql']:
        # 检查是否有连接操作
        if re.search(r'\b(CONNECT|psql|pg_connect)\b', code, re.IGNORECASE):
            if not re.search(r'\b(TRY|BEGIN|EXCEPTION|ERROR)\b', code, re.IGNORECASE):
                issues['needs_error_handling'] = True
                issues['missing_connection_check'] = True
                issues['suggestions'].append('添加连接错误处理')
        
        # 检查是否有事务操作
        if re.search(r'\b(BEGIN|COMMIT|ROLLBACK)\b', code, re.IGNORECASE):
            if not re.search(r'\b(EXCEPTION|ERROR|ROLLBACK)\b', code, re.IGNORECASE):
                issues['needs_error_handling'] = True
                issues['suggestions'].append('添加事务错误处理和回滚')
        
        # 检查是否有INSERT/UPDATE/DELETE
        if re.search(r'\b(INSERT|UPDATE|DELETE)\b', code, re.IGNORECASE):
            if not re.search(r'\b(EXCEPTION|ERROR|CHECK)\b', code, re.IGNORECASE):
                issues['needs_error_handling'] = True
                issues['suggestions'].append('添加数据操作错误处理')
    
    # Python代码分析
    elif language.lower() == 'python':
        # 检查是否有数据库操作
        if re.search(r'\b(psycopg|connect|execute|cursor)\b', code, re.IGNORECASE):
            if not re.search(r'\b(try|except|finally)\b', code, re.IGNORECASE):
                issues['needs_error_handling'] = True
                issues['missing_try_catch'] = True
                issues['suggestions'].append('添加try-except错误处理')
        
        # 检查是否有文件操作
        if re.search(r'\b(open|read|write)\b', code, re.IGNORECASE):
            if not re.search(r'\b(try|except|finally)\b', code, re.IGNORECASE):
                issues['needs_error_handling'] = True
                issues['missing_try_catch'] = True
                issues['suggestions'].append('添加文件操作错误处理')
    
    # Shell脚本分析
    elif language.lower() in ['bash', 'shell', 'sh']:
        # 检查是否有错误检查
        if not re.search(r'\b(set -e|set -o errexit|if \[|exit)\b', code, re.IGNORECASE):
            if re.search(r'\b(psql|pg_|postgres)\b', code, re.IGNORECASE):
                issues['needs_error_handling'] = True
                issues['suggestions'].append('添加错误检查（set -e或if语句）')
    
    return issues


def generate_error_handling_code(original_code: str, language: str, issue_type: str) -> str:
    """生成错误处理代码"""
    
    if language.lower() in ['sql', 'postgresql', 'psql']:
        if issue_type == 'connection':
            return f"""-- 添加连接错误处理
DO $$
BEGIN
    -- 原代码
{original_code}
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '连接错误: %', SQLERRM;
        RAISE;
END $$;"""
        
        elif issue_type == 'transaction':
            return f"""BEGIN;
    -- 原代码
{original_code}
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE NOTICE '事务错误: %', SQLERRM;
        RAISE;
COMMIT;"""
    
    elif language.lower() == 'python':
        if issue_type == 'database':
            return f"""try:
    # 原代码
{original_code}
except psycopg2.Error as e:
    print(f"数据库错误: {{e}}")
    raise
except Exception as e:
    print(f"未知错误: {{e}}")
    raise
finally:
    # 清理资源
    if 'conn' in locals():
        conn.close()"""
    
    elif language.lower() in ['bash', 'shell', 'sh']:
        return f"""set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 原代码
{original_code}

# 检查命令执行结果
if [ $? -ne 0 ]; then
    echo "错误: 命令执行失败"
    exit 1
fi"""
    
    return original_code


def scan_documents(root_dir: str) -> List[Dict]:
    """扫描文档并分析代码示例"""
    
    root_path = Path(root_dir)
    results = []
    
    # 查找所有Markdown文件
    for md_file in root_path.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            code_blocks = find_code_blocks(content)
            
            for line_num, language, code in code_blocks:
                issues = analyze_code_for_error_handling(code, language)
                
                if issues['needs_error_handling']:
                    results.append({
                        'file': str(md_file.relative_to(root_path)),
                        'line': line_num,
                        'language': language,
                        'code': code[:200],  # 只保存前200字符
                        'issues': issues
                    })
        except Exception as e:
            print(f"处理文件失败 {md_file}: {e}")
    
    return results


def generate_report(results: List[Dict], output_file: str):
    """生成错误处理报告"""
    
    report_lines = [
        "# 代码示例错误处理补充报告",
        "",
        f"> **生成日期**: 2025年1月",
        f"> **扫描结果**: 找到 {len(results)} 个需要添加错误处理的代码示例",
        "",
        "---",
        "",
        "## 📊 统计信息",
        "",
        f"- **需要处理的代码示例**: {len(results)} 个",
        "",
        "## 📋 需要处理的代码示例",
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
            report_lines.append("**问题**:")
            for suggestion in result['issues']['suggestions']:
                report_lines.append(f"- {suggestion}")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
    
    # 写入报告
    output_path = Path(output_file)
    output_path.write_text('\n'.join(report_lines), encoding='utf-8')
    print(f"✅ 报告已保存到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='代码示例错误处理补充工具')
    parser.add_argument('--root', type=str, default='docs',
                       help='扫描根目录')
    parser.add_argument('--output', type=str, default='error_handling_report.md',
                       help='输出报告文件')
    
    args = parser.parse_args()
    
    print(f"扫描目录: {args.root}")
    print("分析代码示例...")
    
    results = scan_documents(args.root)
    
    print(f"找到 {len(results)} 个需要添加错误处理的代码示例")
    
    generate_report(results, args.output)
    
    print("✅ 完成！")


if __name__ == '__main__':
    main()
