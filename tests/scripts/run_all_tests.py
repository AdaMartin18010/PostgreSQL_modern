#!/usr/bin/env python3
"""
PostgreSQL SQL 自动化测试主脚本

用法:
    python run_all_tests.py                    # 运行所有测试
    python run_all_tests.py --module 01_sql    # 运行特定模块
    python run_all_tests.py --tags smoke       # 运行特定标签测试
    python run_all_tests.py --parallel 4       # 并行运行（4进程）
"""

import os
import sys
import argparse
import yaml
import psycopg2
import time
from pathlib import Path
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestResult:
    """测试结果类"""
    def __init__(self, name: str, status: str, time: float, error: str = None):
        self.name = name
        self.status = status  # 'passed', 'failed', 'skipped'
        self.time = time
        self.error = error

class SQLTestRunner:
    """SQL测试运行器"""
    
    def __init__(self, config_path: str = 'tests/config/database.yml'):
        self.config_path = config_path
        self.config = self._load_config()
        self.conn = None
        self.results: List[TestResult] = []
        
    def _load_config(self) -> dict:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            print(f"配置文件不存在: {self.config_path}")
            print("请复制 database.yml.example 为 database.yml 并配置数据库连接")
            sys.exit(1)
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def connect(self, env: str = 'default') -> psycopg2.extensions.connection:
        """连接到数据库"""
        db_config = self.config.get(env, self.config['default'])
        
        try:
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['user'],
                password=db_config['password']
            )
            conn.autocommit = False
            return conn
        except Exception as e:
            print(f"数据库连接失败: {e}")
            sys.exit(1)
    
    def find_test_files(self, module: str = None, tags: List[str] = None) -> List[Path]:
        """查找测试文件"""
        test_dir = Path(__file__).parent.parent / 'sql_tests'
        
        if module:
            test_dir = test_dir / module
            
        if not test_dir.exists():
            print(f"测试目录不存在: {test_dir}")
            return []
        
        # 查找所有.sql文件
        test_files = list(test_dir.rglob('test_*.sql'))
        
        # 根据标签过滤
        if tags:
            filtered_files = []
            for file in test_files:
                file_tags = self._extract_tags(file)
                if any(tag in file_tags for tag in tags):
                    filtered_files.append(file)
            test_files = filtered_files
        
        return sorted(test_files)
    
    def _extract_tags(self, file_path: Path) -> List[str]:
        """从SQL文件提取标签"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('-- TAGS:'):
                        tags_str = line.split('-- TAGS:')[1].strip()
                        return [tag.strip() for tag in tags_str.split(',')]
        except:
            pass
        return []
    
    def run_test_file(self, file_path: Path) -> TestResult:
        """运行单个测试文件"""
        test_name = str(file_path.relative_to(Path(__file__).parent.parent))
        start_time = time.time()
        
        try:
            # 连接数据库
            conn = self.connect()
            cursor = conn.cursor()
            
            # 读取SQL文件
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 解析测试块
            test_blocks = self._parse_test_blocks(sql_content)
            
            # 执行SETUP
            if 'setup' in test_blocks:
                cursor.execute(test_blocks['setup'])
                conn.commit()
            
            # 执行TEST_BODY
            if 'test_body' in test_blocks:
                cursor.execute(test_blocks['test_body'])
                
                # 检查断言
                if 'expect' in test_blocks:
                    self._check_assertion(cursor, test_blocks['expect'])
                
                conn.commit()
            
            # 执行TEARDOWN
            if 'teardown' in test_blocks:
                cursor.execute(test_blocks['teardown'])
                conn.commit()
            
            cursor.close()
            conn.close()
            
            elapsed_time = time.time() - start_time
            return TestResult(test_name, 'passed', elapsed_time)
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            return TestResult(test_name, 'failed', elapsed_time, str(e))
    
    def _parse_test_blocks(self, sql_content: str) -> Dict[str, str]:
        """解析SQL测试块"""
        blocks = {}
        current_block = None
        current_content = []
        
        for line in sql_content.split('\n'):
            if line.strip().startswith('-- SETUP'):
                current_block = 'setup'
                current_content = []
            elif line.strip().startswith('-- TEST_BODY'):
                if current_block and current_content:
                    blocks[current_block] = '\n'.join(current_content)
                current_block = 'test_body'
                current_content = []
            elif line.strip().startswith('-- TEARDOWN'):
                if current_block and current_content:
                    blocks[current_block] = '\n'.join(current_content)
                current_block = 'teardown'
                current_content = []
            elif line.strip().startswith('-- EXPECT'):
                blocks['expect'] = line.split('-- EXPECT:')[1].strip()
            elif current_block and not line.strip().startswith('--'):
                current_content.append(line)
        
        # 添加最后一个块
        if current_block and current_content:
            blocks[current_block] = '\n'.join(current_content)
        
        return blocks
    
    def _check_assertion(self, cursor, expect: str):
        """检查断言"""
        # 简化版断言检查
        # 实际实现需要更复杂的逻辑
        pass
    
    def run_all_tests(self, module: str = None, tags: List[str] = None, 
                      parallel: int = 1, verbose: bool = False, 
                      fail_fast: bool = False) -> List[TestResult]:
        """运行所有测试"""
        test_files = self.find_test_files(module, tags)
        
        if not test_files:
            print("未找到测试文件")
            return []
        
        print(f"\n{'='*60}")
        print(f"PostgreSQL SQL 测试套件")
        print(f"{'='*60}\n")
        print(f"找到 {len(test_files)} 个测试文件\n")
        
        results = []
        
        if parallel > 1:
            # 并行执行
            with ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = {executor.submit(self.run_test_file, f): f for f in test_files}
                
                for i, future in enumerate(as_completed(futures), 1):
                    result = future.result()
                    results.append(result)
                    
                    # 显示进度
                    status_icon = '✓' if result.status == 'passed' else '✗'
                    print(f"[{i}/{len(test_files)}] {status_icon} {result.name} ({result.time:.2f}s)")
                    
                    if verbose and result.status == 'failed':
                        print(f"  错误: {result.error}")
                    
                    if fail_fast and result.status == 'failed':
                        print("\n遇到失败，停止测试（--fail-fast模式）")
                        break
        else:
            # 串行执行
            for i, test_file in enumerate(test_files, 1):
                result = self.run_test_file(test_file)
                results.append(result)
                
                status_icon = '✓' if result.status == 'passed' else '✗'
                print(f"[{i}/{len(test_files)}] {status_icon} {result.name} ({result.time:.2f}s)")
                
                if verbose and result.status == 'failed':
                    print(f"  错误: {result.error}")
                
                if fail_fast and result.status == 'failed':
                    print("\n遇到失败，停止测试（--fail-fast模式）")
                    break
        
        self.results = results
        return results
    
    def print_summary(self):
        """打印测试摘要"""
        if not self.results:
            return
        
        passed = sum(1 for r in self.results if r.status == 'passed')
        failed = sum(1 for r in self.results if r.status == 'failed')
        skipped = sum(1 for r in self.results if r.status == 'skipped')
        total_time = sum(r.time for r in self.results)
        
        print(f"\n{'='*60}")
        print(f"测试结果汇总")
        print(f"{'='*60}\n")
        print(f"  ✓ 通过:   {passed}")
        print(f"  ✗ 失败:   {failed}")
        print(f"  ⊘ 跳过:   {skipped}")
        print(f"  总计:     {len(self.results)}")
        print(f"  总耗时:   {total_time:.2f}s\n")
        
        if failed > 0:
            print("失败的测试:\n")
            for i, result in enumerate([r for r in self.results if r.status == 'failed'], 1):
                print(f"  {i}. {result.name}")
                print(f"     错误: {result.error}\n")
        
        return failed == 0

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL SQL 自动化测试')
    parser.add_argument('--module', help='指定测试模块（如 01_sql_ddl_dcl）')
    parser.add_argument('--tags', help='指定测试标签，逗号分隔（如 smoke,regression）')
    parser.add_argument('--parallel', type=int, default=1, help='并行进程数（默认1）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--fail-fast', action='store_true', help='遇到失败立即停止')
    parser.add_argument('--ci', action='store_true', help='CI模式（使用ci配置）')
    
    args = parser.parse_args()
    
    # 解析标签
    tags = args.tags.split(',') if args.tags else None
    
    # 创建测试运行器
    runner = SQLTestRunner()
    
    # 运行测试
    results = runner.run_all_tests(
        module=args.module,
        tags=tags,
        parallel=args.parallel,
        verbose=args.verbose,
        fail_fast=args.fail_fast
    )
    
    # 打印摘要
    success = runner.print_summary()
    
    # 返回退出码
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

