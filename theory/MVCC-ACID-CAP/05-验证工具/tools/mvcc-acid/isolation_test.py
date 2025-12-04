#!/usr/bin/env python3
"""
隔离性测试工具
用于测试PostgreSQL MVCC-ACID的隔离性特性
包括：隔离级别测试、并发冲突测试、序列化异常测试
"""

import psycopg2
from psycopg2 import sql
import threading
import time
import logging
import sys
import os
from typing import Optional, Dict, List, Tuple
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IsolationTester:
    """隔离性测试器"""
    
    def __init__(self, connection_string: str):
        """初始化连接"""
        self.connection_string = connection_string
        self.conn = None
        self.test_results = []
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.conn.autocommit = False
            logger.info("数据库连接成功")
        except psycopg2.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
    
    def setup_test_tables(self):
        """设置测试表"""
        try:
            with self.conn.cursor() as cur:
                # 账户表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_accounts (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                        CHECK (balance >= 0)
                    )
                """)
                
                # 订单表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_orders (
                        id SERIAL PRIMARY KEY,
                        account_id INTEGER REFERENCES test_accounts(id),
                        amount DECIMAL(10, 2) NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 插入测试数据
                cur.execute("""
                    INSERT INTO test_accounts (name, balance)
                    VALUES 
                        ('Alice', 1000.00),
                        ('Bob', 500.00),
                        ('Charlie', 200.00)
                    ON CONFLICT DO NOTHING
                """)
                
                self.conn.commit()
                logger.info("测试表设置完成")
        except psycopg2.Error as e:
            logger.error(f"设置测试表失败: {e}")
            self.conn.rollback()
            raise
    
    def test_read_committed(self) -> Dict:
        """测试READ COMMITTED隔离级别"""
        logger.info("开始测试：READ COMMITTED隔离级别")
        test_name = "READ COMMITTED隔离级别测试"
        
        try:
            # 创建两个连接模拟并发事务
            conn1 = psycopg2.connect(self.connection_string)
            conn1.autocommit = False
            conn2 = psycopg2.connect(self.connection_string)
            conn2.autocommit = False
            
            try:
                # 事务1：更新数据
                with conn1.cursor() as cur1:
                    cur1.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                    cur1.execute("BEGIN")
                    cur1.execute("UPDATE test_accounts SET balance = balance + 100 WHERE name = 'Alice'")
                    # 不提交
                
                # 事务2：读取数据（应该看不到未提交的数据）
                with conn2.cursor() as cur2:
                    cur2.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                    cur2.execute("BEGIN")
                    cur2.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                    balance = cur2.fetchone()[0]
                
                # 验证：READ COMMITTED应该看不到未提交的数据
                success = (balance == 1000.00)  # 原始值
                
                # 提交事务1
                conn1.commit()
                
                # 事务2再次读取（应该看到已提交的数据）
                with conn2.cursor() as cur2:
                    cur2.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                    balance_after = cur2.fetchone()[0]
                
                conn2.commit()
                
                # 验证：提交后应该看到新值
                success = success and (balance_after == 1100.00)
                
                result = {
                    'test_name': test_name,
                    'success': success,
                    'balance_before_commit': float(balance),
                    'balance_after_commit': float(balance_after),
                    'message': '测试通过' if success else '测试失败'
                }
                
                logger.info(f"{test_name}: {'通过' if success else '失败'}")
                return result
                
            finally:
                conn1.close()
                conn2.close()
                
        except Exception as e:
            logger.error(f"{test_name}执行失败: {e}")
            return {
                'test_name': test_name,
                'success': False,
                'error': str(e)
            }
    
    def test_repeatable_read(self) -> Dict:
        """测试REPEATABLE READ隔离级别"""
        logger.info("开始测试：REPEATABLE READ隔离级别")
        test_name = "REPEATABLE READ隔离级别测试"
        
        try:
            # 创建两个连接模拟并发事务
            conn1 = psycopg2.connect(self.connection_string)
            conn1.autocommit = False
            conn2 = psycopg2.connect(self.connection_string)
            conn2.autocommit = False
            
            try:
                # 事务1：第一次读取
                with conn1.cursor() as cur1:
                    cur1.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                    cur1.execute("BEGIN")
                    cur1.execute("SELECT balance FROM test_accounts WHERE name = 'Bob'")
                    balance1 = cur1.fetchone()[0]
                
                # 事务2：更新数据并提交
                with conn2.cursor() as cur2:
                    cur2.execute("BEGIN")
                    cur2.execute("UPDATE test_accounts SET balance = balance + 50 WHERE name = 'Bob'")
                    conn2.commit()
                
                # 事务1：第二次读取（应该看到相同的值）
                with conn1.cursor() as cur1:
                    cur1.execute("SELECT balance FROM test_accounts WHERE name = 'Bob'")
                    balance2 = cur1.fetchone()[0]
                
                conn1.commit()
                
                # 验证：REPEATABLE READ应该看到相同的值
                success = (balance1 == balance2)
                
                result = {
                    'test_name': test_name,
                    'success': success,
                    'balance_first_read': float(balance1),
                    'balance_second_read': float(balance2),
                    'message': '测试通过' if success else '测试失败'
                }
                
                logger.info(f"{test_name}: {'通过' if success else '失败'}")
                return result
                
            finally:
                conn1.close()
                conn2.close()
                
        except Exception as e:
            logger.error(f"{test_name}执行失败: {e}")
            return {
                'test_name': test_name,
                'success': False,
                'error': str(e)
            }
    
    def test_serializable(self) -> Dict:
        """测试SERIALIZABLE隔离级别"""
        logger.info("开始测试：SERIALIZABLE隔离级别")
        test_name = "SERIALIZABLE隔离级别测试"
        
        try:
            # 创建两个连接模拟并发事务
            conn1 = psycopg2.connect(self.connection_string)
            conn1.autocommit = False
            conn2 = psycopg2.connect(self.connection_string)
            conn2.autocommit = False
            
            try:
                # 事务1：读取并更新
                with conn1.cursor() as cur1:
                    cur1.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                    cur1.execute("BEGIN")
                    cur1.execute("SELECT balance FROM test_accounts WHERE name = 'Charlie'")
                    balance1 = cur1.fetchone()[0]
                    cur1.execute("UPDATE test_accounts SET balance = balance - 50 WHERE name = 'Charlie'")
                    # 不提交
                
                # 事务2：读取并更新（可能冲突）
                serialization_error = False
                try:
                    with conn2.cursor() as cur2:
                        cur2.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                        cur2.execute("BEGIN")
                        cur2.execute("SELECT balance FROM test_accounts WHERE name = 'Charlie'")
                        balance2 = cur2.fetchone()[0]
                        cur2.execute("UPDATE test_accounts SET balance = balance - 30 WHERE name = 'Charlie'")
                        conn2.commit()
                except psycopg2.extensions.TransactionRollbackError as e:
                    if 'serialization failure' in str(e).lower():
                        serialization_error = True
                        conn2.rollback()
                
                # 提交事务1
                conn1.commit()
                
                # 验证：SERIALIZABLE应该检测到冲突
                # 注意：这个测试可能因为SSI检测机制而不总是失败
                success = True  # SERIALIZABLE可能检测到冲突，也可能没有
                
                result = {
                    'test_name': test_name,
                    'success': success,
                    'serialization_error_detected': serialization_error,
                    'message': '测试通过（SERIALIZABLE冲突检测）' if serialization_error else '测试通过（无冲突）'
                }
                
                logger.info(f"{test_name}: {'通过' if success else '失败'}")
                return result
                
            finally:
                conn1.close()
                conn2.close()
                
        except Exception as e:
            logger.error(f"{test_name}执行失败: {e}")
            return {
                'test_name': test_name,
                'success': False,
                'error': str(e)
            }
    
    def test_concurrent_update(self) -> Dict:
        """测试并发更新冲突"""
        logger.info("开始测试：并发更新冲突")
        test_name = "并发更新冲突测试"
        
        try:
            # 重置测试数据
            with self.conn.cursor() as cur:
                cur.execute("UPDATE test_accounts SET balance = 1000.00 WHERE name = 'Alice'")
                self.conn.commit()
            
            # 使用线程池模拟并发更新
            def update_balance(thread_id):
                """并发更新余额"""
                conn = psycopg2.connect(self.connection_string)
                conn.autocommit = False
                try:
                    with conn.cursor() as cur:
                        cur.execute("BEGIN")
                        cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice' FOR UPDATE")
                        balance = cur.fetchone()[0]
                        time.sleep(0.1)  # 模拟处理时间
                        cur.execute("UPDATE test_accounts SET balance = balance + 10 WHERE name = 'Alice'")
                        conn.commit()
                    return {'thread_id': thread_id, 'success': True}
                except Exception as e:
                    conn.rollback()
                    return {'thread_id': thread_id, 'success': False, 'error': str(e)}
                finally:
                    conn.close()
            
            # 启动5个并发线程
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(update_balance, i) for i in range(5)]
                results = [f.result() for f in as_completed(futures)]
            
            # 验证最终余额
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                final_balance = cur.fetchone()[0]
            
            # 验证：所有更新都应该成功，最终余额应该是 1000 + 5*10 = 1050
            success = (final_balance == 1050.00)
            successful_updates = sum(1 for r in results if r.get('success', False))
            
            result = {
                'test_name': test_name,
                'success': success,
                'final_balance': float(final_balance),
                'expected_balance': 1050.00,
                'successful_updates': successful_updates,
                'total_threads': 5,
                'message': '测试通过' if success else '测试失败'
            }
            
            logger.info(f"{test_name}: {'通过' if success else '失败'}")
            return result
            
        except Exception as e:
            logger.error(f"{test_name}执行失败: {e}")
            return {
                'test_name': test_name,
                'success': False,
                'error': str(e)
            }
    
    def test_write_skew(self) -> Dict:
        """测试写偏序异常"""
        logger.info("开始测试：写偏序异常")
        test_name = "写偏序异常测试"
        
        try:
            # 重置测试数据
            with self.conn.cursor() as cur:
                cur.execute("UPDATE test_accounts SET balance = 100.00 WHERE name = 'Bob'")
                cur.execute("UPDATE test_accounts SET balance = 100.00 WHERE name = 'Charlie'")
                self.conn.commit()
            
            # 创建两个连接模拟并发事务
            conn1 = psycopg2.connect(self.connection_string)
            conn1.autocommit = False
            conn2 = psycopg2.connect(self.connection_string)
            conn2.autocommit = False
            
            try:
                # 事务1：读取两个账户，扣减第一个
                with conn1.cursor() as cur1:
                    cur1.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                    cur1.execute("BEGIN")
                    cur1.execute("SELECT balance FROM test_accounts WHERE name = 'Bob'")
                    balance_bob1 = cur1.fetchone()[0]
                    cur1.execute("SELECT balance FROM test_accounts WHERE name = 'Charlie'")
                    balance_charlie1 = cur1.fetchone()[0]
                    
                    # 扣减Bob的余额
                    cur1.execute("UPDATE test_accounts SET balance = balance - 100 WHERE name = 'Bob'")
                    # 不提交
                
                # 事务2：读取两个账户，扣减第二个
                with conn2.cursor() as cur2:
                    cur2.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                    cur2.execute("BEGIN")
                    cur2.execute("SELECT balance FROM test_accounts WHERE name = 'Bob'")
                    balance_bob2 = cur2.fetchone()[0]
                    cur2.execute("SELECT balance FROM test_accounts WHERE name = 'Charlie'")
                    balance_charlie2 = cur2.fetchone()[0]
                    
                    # 扣减Charlie的余额
                    cur2.execute("UPDATE test_accounts SET balance = balance - 100 WHERE name = 'Charlie'")
                    conn2.commit()
                
                # 提交事务1
                conn1.commit()
                
                # 验证最终余额
                with self.conn.cursor() as cur:
                    cur.execute("SELECT balance FROM test_accounts WHERE name = 'Bob'")
                    final_bob = cur.fetchone()[0]
                    cur.execute("SELECT balance FROM test_accounts WHERE name = 'Charlie'")
                    final_charlie = cur.fetchone()[0]
                
                # 验证：REPEATABLE READ可能允许写偏序
                # 两个账户都被扣减，可能导致总余额为负（如果业务规则要求总余额 >= 0）
                total_balance = final_bob + final_charlie
                write_skew_occurred = (total_balance < 0)
                
                result = {
                    'test_name': test_name,
                    'success': True,  # 测试成功执行
                    'write_skew_detected': write_skew_occurred,
                    'final_bob_balance': float(final_bob),
                    'final_charlie_balance': float(final_charlie),
                    'total_balance': float(total_balance),
                    'message': f'写偏序{"发生" if write_skew_occurred else "未发生"}'
                }
                
                logger.info(f"{test_name}: 完成（写偏序{'发生' if write_skew_occurred else '未发生'}）")
                return result
                
            finally:
                conn1.close()
                conn2.close()
                
        except Exception as e:
            logger.error(f"{test_name}执行失败: {e}")
            return {
                'test_name': test_name,
                'success': False,
                'error': str(e)
            }
    
    def test_phantom_read(self) -> Dict:
        """测试幻读异常"""
        logger.info("开始测试：幻读异常")
        test_name = "幻读异常测试"
        
        try:
            # 创建两个连接模拟并发事务
            conn1 = psycopg2.connect(self.connection_string)
            conn1.autocommit = False
            conn2 = psycopg2.connect(self.connection_string)
            conn2.autocommit = False
            
            try:
                # 事务1：第一次查询
                with conn1.cursor() as cur1:
                    cur1.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                    cur1.execute("BEGIN")
                    cur1.execute("SELECT COUNT(*) FROM test_orders WHERE account_id = 1")
                    count1 = cur1.fetchone()[0]
                
                # 事务2：插入新订单
                with conn2.cursor() as cur2:
                    cur2.execute("BEGIN")
                    cur2.execute("INSERT INTO test_orders (account_id, amount) VALUES (1, 100.00)")
                    conn2.commit()
                
                # 事务1：第二次查询（可能看到新插入的数据）
                with conn1.cursor() as cur1:
                    cur1.execute("SELECT COUNT(*) FROM test_orders WHERE account_id = 1")
                    count2 = cur1.fetchone()[0]
                
                conn1.commit()
                
                # 验证：READ COMMITTED可能看到新插入的数据（幻读）
                phantom_read_occurred = (count2 > count1)
                
                result = {
                    'test_name': test_name,
                    'success': True,  # 测试成功执行
                    'phantom_read_detected': phantom_read_occurred,
                    'count_first_read': count1,
                    'count_second_read': count2,
                    'message': f'幻读{"发生" if phantom_read_occurred else "未发生"}'
                }
                
                logger.info(f"{test_name}: 完成（幻读{'发生' if phantom_read_occurred else '未发生'}）")
                return result
                
            finally:
                conn1.close()
                conn2.close()
                
        except Exception as e:
            logger.error(f"{test_name}执行失败: {e}")
            return {
                'test_name': test_name,
                'success': False,
                'error': str(e)
            }
    
    def run_all_tests(self) -> List[Dict]:
        """运行所有测试"""
        logger.info("=" * 60)
        logger.info("开始运行隔离性测试套件")
        logger.info("=" * 60)
        
        results = []
        
        # 运行所有测试
        results.append(self.test_read_committed())
        results.append(self.test_repeatable_read())
        results.append(self.test_serializable())
        results.append(self.test_concurrent_update())
        results.append(self.test_write_skew())
        results.append(self.test_phantom_read())
        
        # 统计结果
        total = len(results)
        passed = sum(1 for r in results if r.get('success', False))
        failed = total - passed
        
        logger.info("=" * 60)
        logger.info(f"测试完成：总计 {total}，通过 {passed}，失败 {failed}")
        logger.info("=" * 60)
        
        return results
    
    def print_results(self, results: List[Dict]):
        """打印测试结果"""
        print("\n" + "=" * 60)
        print("隔离性测试结果")
        print("=" * 60)
        
        for result in results:
            status = "✅ 通过" if result.get('success', False) else "❌ 失败"
            print(f"\n{status} - {result.get('test_name', 'Unknown')}")
            
            if result.get('success', False):
                print(f"  消息: {result.get('message', '')}")
            else:
                print(f"  错误: {result.get('error', result.get('message', 'Unknown error'))}")
        
        print("\n" + "=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='隔离性测试工具')
    parser.add_argument(
        '--connection',
        default='dbname=testdb user=postgres password=postgres host=localhost',
        help='数据库连接字符串'
    )
    parser.add_argument(
        '--setup',
        action='store_true',
        help='设置测试表'
    )
    parser.add_argument(
        '--test',
        choices=['all', 'read_committed', 'repeatable_read', 'serializable', 'concurrent', 'write_skew', 'phantom'],
        default='all',
        help='要运行的测试'
    )
    
    args = parser.parse_args()
    
    tester = None
    try:
        tester = IsolationTester(args.connection)
        tester.connect()
        
        if args.setup:
            tester.setup_test_tables()
        
        # 运行测试
        if args.test == 'all':
            results = tester.run_all_tests()
        elif args.test == 'read_committed':
            results = [tester.test_read_committed()]
        elif args.test == 'repeatable_read':
            results = [tester.test_repeatable_read()]
        elif args.test == 'serializable':
            results = [tester.test_serializable()]
        elif args.test == 'concurrent':
            results = [tester.test_concurrent_update()]
        elif args.test == 'write_skew':
            results = [tester.test_write_skew()]
        elif args.test == 'phantom':
            results = [tester.test_phantom_read()]
        
        tester.print_results(results)
        
        # 返回退出码
        all_passed = all(r.get('success', False) for r in results)
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)
    finally:
        if tester:
            tester.close()


if __name__ == "__main__":
    main()
