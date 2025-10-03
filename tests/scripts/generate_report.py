#!/usr/bin/env python3
"""
生成HTML测试报告

用法:
    python generate_report.py
    python generate_report.py --output custom_report.html
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PostgreSQL SQL 测试报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        
        .meta {{
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .summary-card.passed {{
            background: #e8f5e9;
            border: 2px solid #4caf50;
        }}
        
        .summary-card.failed {{
            background: #ffebee;
            border: 2px solid #f44336;
        }}
        
        .summary-card.skipped {{
            background: #fff3e0;
            border: 2px solid #ff9800;
        }}
        
        .summary-card h2 {{
            font-size: 36px;
            margin-bottom: 5px;
        }}
        
        .summary-card p {{
            color: #666;
            font-size: 14px;
        }}
        
        .test-list {{
            margin-top: 30px;
        }}
        
        .test-item {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid;
        }}
        
        .test-item.passed {{
            background: #f1f8e9;
            border-left-color: #4caf50;
        }}
        
        .test-item.failed {{
            background: #ffebee;
            border-left-color: #f44336;
        }}
        
        .test-item.skipped {{
            background: #fff3e0;
            border-left-color: #ff9800;
        }}
        
        .test-name {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .test-time {{
            color: #666;
            font-size: 12px;
        }}
        
        .test-error {{
            margin-top: 10px;
            padding: 10px;
            background: #fff;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            color: #d32f2f;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🗄️ PostgreSQL SQL 测试报告</h1>
        <div class="meta">
            生成时间: {timestamp}<br>
            项目: PostgreSQL_modern
        </div>
        
        <div class="summary">
            <div class="summary-card passed">
                <h2>{passed}</h2>
                <p>✓ 通过</p>
            </div>
            <div class="summary-card failed">
                <h2>{failed}</h2>
                <p>✗ 失败</p>
            </div>
            <div class="summary-card skipped">
                <h2>{skipped}</h2>
                <p>⊘ 跳过</p>
            </div>
            <div class="summary-card">
                <h2>{total_time:.2f}s</h2>
                <p>⏱ 总耗时</p>
            </div>
        </div>
        
        <div class="test-list">
            <h3 style="margin-bottom: 15px;">测试详情</h3>
            {test_items}
        </div>
        
        <div class="footer">
            PostgreSQL_modern Project · 自动化测试报告<br>
            Version 1.0.0 · 2025-10-03
        </div>
    </div>
</body>
</html>
"""

TEST_ITEM_TEMPLATE = """
<div class="test-item {status}">
    <div class="test-name">{icon} {name}</div>
    <div class="test-time">耗时: {time:.3f}秒</div>
    {error_html}
</div>
"""

def generate_html_report(results: list, output_path: str = 'tests/reports/test_results.html'):
    """生成HTML测试报告"""
    
    # 统计
    passed = sum(1 for r in results if r['status'] == 'passed')
    failed = sum(1 for r in results if r['status'] == 'failed')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    total_time = sum(r['time'] for r in results)
    
    # 生成测试项HTML
    test_items_html = []
    for result in results:
        icon = '✓' if result['status'] == 'passed' else '✗' if result['status'] == 'failed' else '⊘'
        
        error_html = ''
        if result['status'] == 'failed' and result.get('error'):
            error_html = f'<div class="test-error">{result["error"]}</div>'
        
        test_items_html.append(TEST_ITEM_TEMPLATE.format(
            status=result['status'],
            icon=icon,
            name=result['name'],
            time=result['time'],
            error_html=error_html
        ))
    
    # 生成完整HTML
    html = HTML_TEMPLATE.format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        passed=passed,
        failed=failed,
        skipped=skipped,
        total_time=total_time,
        test_items=''.join(test_items_html)
    )
    
    # 写入文件
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML报告已生成: {output_path}")

def generate_text_summary(results: list, output_path: str = 'tests/reports/summary.txt'):
    """生成文本摘要"""
    
    passed = sum(1 for r in results if r['status'] == 'passed')
    failed = sum(1 for r in results if r['status'] == 'failed')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    total_time = sum(r['time'] for r in results)
    
    summary = f"""
PostgreSQL SQL 测试摘要
{'='*50}

通过:   {passed}
失败:   {failed}
跳过:   {skipped}
总计:   {len(results)}
耗时:   {total_time:.2f}秒

{'='*50}
"""
    
    if failed > 0:
        summary += "\n失败的测试:\n\n"
        for result in [r for r in results if r['status'] == 'failed']:
            summary += f"  ✗ {result['name']}\n"
            if result.get('error'):
                summary += f"    错误: {result['error']}\n\n"
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✓ 文本摘要已生成: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='生成测试报告')
    parser.add_argument('--input', default='tests/reports/results.json', help='测试结果JSON文件')
    parser.add_argument('--output', default='tests/reports/test_results.html', help='输出HTML文件路径')
    
    args = parser.parse_args()
    
    # 读取测试结果
    if Path(args.input).exists():
        with open(args.input, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        # 示例数据
        results = [
            {'name': 'example_test.sql', 'status': 'passed', 'time': 0.123, 'error': None},
            {'name': 'transaction_test.sql', 'status': 'passed', 'time': 0.456, 'error': None},
            {'name': 'index_test.sql', 'status': 'failed', 'time': 0.789, 'error': 'Syntax error near line 42'},
        ]
    
    # 生成报告
    generate_html_report(results, args.output)
    generate_text_summary(results)

if __name__ == '__main__':
    main()

