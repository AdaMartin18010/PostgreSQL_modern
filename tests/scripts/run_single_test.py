#!/usr/bin/env python3
"""
运行单个SQL测试文件

用法:
    python run_single_test.py tests/sql_tests/example_test.sql
    python run_single_test.py --debug tests/sql_tests/example_test.sql
"""

import sys
import argparse
import psycopg2
import time
from pathlib import Path

def run_single_test(file_path: str, debug: bool = False, config_env: str = 'default'):
    """运行单个测试文件"""
    
    if not Path(file_path).exists():
        print(f"错误: 测试文件不存在: {file_path}")
        return False
    
    print(f"\n{'='*60}")
    print(f"运行测试: {file_path}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    try:
        # 连接数据库（简化版，实际应该从配置读取）
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='postgres_modern_test',
            user='postgres',
            password='postgres'
        )
        
        conn.autocommit = False
        cursor = conn.cursor()
        
        # 读取SQL文件
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分块执行
        blocks = parse_sql_blocks(sql_content)
        
        if debug:
            print("DEBUG: SQL blocks found:")
            for block_name, block_sql in blocks.items():
                print(f"\n--- {block_name.upper()} ---")
                print(block_sql[:200] + "..." if len(block_sql) > 200 else block_sql)
        
        # 执行SETUP
        if 'setup' in blocks:
            print("执行 SETUP...")
            if debug:
                print(f"SQL: {blocks['setup']}")
            cursor.execute(blocks['setup'])
            conn.commit()
            print("✓ SETUP 完成")
        
        # 执行TEST_BODY
        if 'test_body' in blocks:
            print("执行 TEST_BODY...")
            if debug:
                print(f"SQL: {blocks['test_body']}")
            
            cursor.execute(blocks['test_body'])
            
            # 尝试获取结果
            try:
                results = cursor.fetchall()
                if results:
                    print(f"查询结果: {len(results)}行")
                    if debug:
                        for i, row in enumerate(results[:5], 1):
                            print(f"  Row {i}: {row}")
                        if len(results) > 5:
                            print(f"  ... 还有 {len(results) - 5} 行")
            except psycopg2.ProgrammingError:
                # 不是查询语句（如INSERT/UPDATE）
                pass
            
            conn.commit()
            print("✓ TEST_BODY 完成")
        
        # 执行TEARDOWN
        if 'teardown' in blocks:
            print("执行 TEARDOWN...")
            if debug:
                print(f"SQL: {blocks['teardown']}")
            cursor.execute(blocks['teardown'])
            conn.commit()
            print("✓ TEARDOWN 完成")
        
        cursor.close()
        conn.close()
        
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"✓ 测试通过")
        print(f"耗时: {elapsed_time:.3f}秒")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"✗ 测试失败")
        print(f"错误: {e}")
        print(f"耗时: {elapsed_time:.3f}秒")
        print(f"{'='*60}\n")
        
        if debug:
            import traceback
            traceback.print_exc()
        
        return False

def parse_sql_blocks(sql_content: str) -> dict:
    """解析SQL测试块"""
    blocks = {}
    current_block = None
    current_content = []
    
    for line in sql_content.split('\n'):
        stripped = line.strip()
        
        if stripped.startswith('-- SETUP'):
            if current_block and current_content:
                blocks[current_block] = '\n'.join(current_content)
            current_block = 'setup'
            current_content = []
        elif stripped.startswith('-- TEST_BODY'):
            if current_block and current_content:
                blocks[current_block] = '\n'.join(current_content)
            current_block = 'test_body'
            current_content = []
        elif stripped.startswith('-- TEARDOWN'):
            if current_block and current_content:
                blocks[current_block] = '\n'.join(current_content)
            current_block = 'teardown'
            current_content = []
        elif current_block:
            # 跳过注释行（除了块标记）
            if not stripped.startswith('--') or stripped.startswith('-- EXPECT'):
                current_content.append(line)
    
    # 添加最后一个块
    if current_block and current_content:
        blocks[current_block] = '\n'.join(current_content)
    
    return blocks

def main():
    parser = argparse.ArgumentParser(description='运行单个SQL测试文件')
    parser.add_argument('test_file', help='测试文件路径')
    parser.add_argument('--debug', '-d', action='store_true', help='调试模式（打印详细信息）')
    parser.add_argument('--env', default='default', help='配置环境（default/ci/development）')
    
    args = parser.parse_args()
    
    success = run_single_test(args.test_file, args.debug, args.env)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

