#!/usr/bin/env python3
"""
原子性测试工具
用于测试PostgreSQL MVCC-ACID的原子性特性
包括：事务回滚测试、部分回滚测试、崩溃恢复测试
"""

import psycopg2
from psycopg2 import sql
import time
import logging
import sys
import os
from typing import Optional, Dict, List, Tuple
from contextlib import contextmanager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AtomicityTester:
    """原子性测试器"""
    
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
                        ('Bob', 500.00)
                    ON CONFLICT DO NOTHING
                """)
                
                self.conn.commit()
                logger.info("测试表设置完成")
        except psycopg2.Error as e:
            logger.error(f"设置测试表失败: {e}")
            self.conn.rollback()
            raise
    
    def test_full_rollback(self) -> Dict:
        """测试完整事务回滚"""
        logger.info("开始测试：完整事务回滚")
        test_name = "完整事务回滚测试"
        
        try:
            # 记录初始状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                initial_balance = cur.fetchone()[0]
            
            # 开始事务
            with self.conn.cursor() as cur:
                # 执行多个操作
                cur.execute("""
                    UPDATE test_accounts 
                    SET balance = balance - 100 
                    WHERE name = 'Alice'
                """)
                
                cur.execute("""
                    UPDATE test_accounts 
                    SET balance = balance + 100 
                    WHERE name = 'Bob'
                """)
                
                cur.execute("""
                    INSERT INTO test_orders (account_id, amount)
                    VALUES (1, 100.00)
                """)
                
                # 模拟错误，回滚事务
                logger.info("模拟错误，执行回滚")
                self.conn.rollback()
            
            # 验证回滚后状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                final_balance = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM test_orders WHERE account_id = 1")
                order_count = cur.fetchone()[0]
            
            # 验证结果
            success = (initial_balance == final_balance and order_count == 0)
            
            result = {
                'test_name': test_name,
                'success': success,
                'initial_balance': float(initial_balance),
                'final_balance': float(final_balance),
                'order_count': order_count,
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
    
    def test_partial_rollback(self) -> Dict:
        """测试部分回滚（使用保存点）"""
        logger.info("开始测试：部分回滚（保存点）")
        test_name = "部分回滚测试"
        
        try:
            # 记录初始状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                initial_balance = cur.fetchone()[0]
            
            # 开始事务
            with self.conn.cursor() as cur:
                # 操作1：扣款（应该保留）
                cur.execute("""
                    UPDATE test_accounts 
                    SET balance = balance - 50 
                    WHERE name = 'Alice'
                """)
                
                # 创建保存点
                cur.execute("SAVEPOINT sp1")
                
                # 操作2：创建订单（应该回滚）
                cur.execute("""
                    INSERT INTO test_orders (account_id, amount)
                    VALUES (1, 50.00)
                """)
                
                # 模拟错误，回滚到保存点
                logger.info("模拟错误，回滚到保存点")
                cur.execute("ROLLBACK TO SAVEPOINT sp1")
                
                # 提交事务
                self.conn.commit()
            
            # 验证部分回滚后状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                final_balance = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM test_orders WHERE account_id = 1 AND amount = 50.00")
                order_count = cur.fetchone()[0]
            
            # 验证结果
            expected_balance = initial_balance - 50
            success = (final_balance == expected_balance and order_count == 0)
            
            result = {
                'test_name': test_name,
                'success': success,
                'initial_balance': float(initial_balance),
                'final_balance': float(final_balance),
                'expected_balance': float(expected_balance),
                'order_count': order_count,
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
    
    def test_constraint_violation_rollback(self) -> Dict:
        """测试约束违反导致的事务回滚"""
        logger.info("开始测试：约束违反导致的事务回滚")
        test_name = "约束违反回滚测试"
        
        try:
            # 记录初始状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                initial_balance = cur.fetchone()[0]
            
            # 开始事务
            rollback_occurred = False
            try:
                with self.conn.cursor() as cur:
                    # 操作1：正常扣款
                    cur.execute("""
                        UPDATE test_accounts 
                        SET balance = balance - 100 
                        WHERE name = 'Alice'
                    """)
                    
                    # 操作2：违反约束（余额不能为负）
                    cur.execute("""
                        UPDATE test_accounts 
                        SET balance = balance - 2000 
                        WHERE name = 'Alice'
                    """)
                    
                    self.conn.commit()
            except psycopg2.IntegrityError as e:
                logger.info(f"捕获约束违反错误: {e}")
                self.conn.rollback()
                rollback_occurred = True
            
            # 验证回滚后状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                final_balance = cur.fetchone()[0]
            
            # 验证结果
            success = (rollback_occurred and initial_balance == final_balance)
            
            result = {
                'test_name': test_name,
                'success': success,
                'initial_balance': float(initial_balance),
                'final_balance': float(final_balance),
                'rollback_occurred': rollback_occurred,
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
    
    def test_crash_recovery_simulation(self) -> Dict:
        """测试崩溃恢复模拟（通过异常模拟）"""
        logger.info("开始测试：崩溃恢复模拟")
        test_name = "崩溃恢复模拟测试"
        
        try:
            # 记录初始状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                initial_balance = cur.fetchone()[0]
            
            # 模拟崩溃场景：事务未提交就断开连接
            temp_conn = psycopg2.connect(self.connection_string)
            temp_conn.autocommit = False
            
            try:
                with temp_conn.cursor() as cur:
                    # 执行操作但未提交
                    cur.execute("""
                        UPDATE test_accounts 
                        SET balance = balance - 100 
                        WHERE name = 'Alice'
                    """)
                    
                    cur.execute("""
                        INSERT INTO test_orders (account_id, amount)
                        VALUES (1, 100.00)
                    """)
                    
                    # 模拟崩溃：直接关闭连接，不提交
                    logger.info("模拟崩溃：关闭连接，不提交事务")
                    temp_conn.close()
            except Exception:
                pass
            
            # 等待一小段时间，确保事务被清理
            time.sleep(0.1)
            
            # 验证崩溃恢复后状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                final_balance = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM test_orders WHERE account_id = 1 AND amount = 100.00")
                order_count = cur.fetchone()[0]
            
            # 验证结果：未提交的事务应该被回滚
            success = (initial_balance == final_balance and order_count == 0)
            
            result = {
                'test_name': test_name,
                'success': success,
                'initial_balance': float(initial_balance),
                'final_balance': float(final_balance),
                'order_count': order_count,
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
    
    def run_all_tests(self) -> List[Dict]:
        """运行所有测试"""
        logger.info("=" * 60)
        logger.info("开始运行原子性测试套件")
        logger.info("=" * 60)
        
        results = []
        
        # 运行所有测试
        results.append(self.test_full_rollback())
        results.append(self.test_partial_rollback())
        results.append(self.test_constraint_violation_rollback())
        results.append(self.test_crash_recovery_simulation())
        
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
        print("原子性测试结果")
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
    
    parser = argparse.ArgumentParser(description='原子性测试工具')
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
        choices=['all', 'full_rollback', 'partial_rollback', 'constraint', 'crash'],
        default='all',
        help='要运行的测试'
    )
    
    args = parser.parse_args()
    
    tester = None
    try:
        tester = AtomicityTester(args.connection)
        tester.connect()
        
        if args.setup:
            tester.setup_test_tables()
        
        # 运行测试
        if args.test == 'all':
            results = tester.run_all_tests()
        elif args.test == 'full_rollback':
            results = [tester.test_full_rollback()]
        elif args.test == 'partial_rollback':
            results = [tester.test_partial_rollback()]
        elif args.test == 'constraint':
            results = [tester.test_constraint_violation_rollback()]
        elif args.test == 'crash':
            results = [tester.test_crash_recovery_simulation()]
        
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
