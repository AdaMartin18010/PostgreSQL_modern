#!/usr/bin/env python3
"""
持久性测试工具
用于测试PostgreSQL MVCC-ACID的持久性特性
包括：WAL测试、崩溃恢复测试、数据持久性测试
"""

import psycopg2
from psycopg2 import sql
import time
import logging
import sys
import os
import subprocess
from typing import Optional, Dict, List, Tuple
from contextlib import contextmanager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DurabilityTester:
    """持久性测试器"""
    
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
                # 测试表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_durability (
                        id SERIAL PRIMARY KEY,
                        data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 插入测试数据
                cur.execute("""
                    INSERT INTO test_durability (data)
                    VALUES ('initial_data')
                    ON CONFLICT DO NOTHING
                """)
                
                self.conn.commit()
                logger.info("测试表设置完成")
        except psycopg2.Error as e:
            logger.error(f"设置测试表失败: {e}")
            self.conn.rollback()
            raise
    
    def test_wal_write(self) -> Dict:
        """测试WAL写入"""
        logger.info("开始测试：WAL写入")
        test_name = "WAL写入测试"
        
        try:
            # 记录初始WAL位置
            with self.conn.cursor() as cur:
                cur.execute("SELECT pg_current_wal_lsn()")
                initial_lsn = cur.fetchone()[0]
            
            # 执行写入操作
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO test_durability (data)
                    VALUES ('wal_test_data')
                """)
                self.conn.commit()
            
            # 记录最终WAL位置
            with self.conn.cursor() as cur:
                cur.execute("SELECT pg_current_wal_lsn()")
                final_lsn = cur.fetchone()[0]
            
            # 验证WAL位置变化
            wal_written = (final_lsn != initial_lsn)
            
            result = {
                'test_name': test_name,
                'success': wal_written,
                'initial_lsn': str(initial_lsn),
                'final_lsn': str(final_lsn),
                'message': 'WAL写入成功' if wal_written else 'WAL写入失败'
            }
            
            logger.info(f"{test_name}: {'通过' if wal_written else '失败'}")
            return result
            
        except Exception as e:
            logger.error(f"{test_name}执行失败: {e}")
            return {
                'test_name': test_name,
                'success': False,
                'error': str(e)
            }
    
    def test_synchronous_commit(self) -> Dict:
        """测试同步提交"""
        logger.info("开始测试：同步提交")
        test_name = "同步提交测试"
        
        try:
            # 检查当前同步提交设置
            with self.conn.cursor() as cur:
                cur.execute("SHOW synchronous_commit")
                sync_commit_setting = cur.fetchone()[0]
            
            # 设置同步提交
            with self.conn.cursor() as cur:
                cur.execute("SET synchronous_commit = on")
            
            # 执行写入操作
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO test_durability (data)
                    VALUES ('sync_commit_test_data')
                """)
                self.conn.commit()
            
            # 验证数据已写入
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM test_durability
                    WHERE data = 'sync_commit_test_data'
                """)
                count = cur.fetchone()[0]
            
            success = (count == 1)
            
            result = {
                'test_name': test_name,
                'success': success,
                'synchronous_commit': sync_commit_setting,
                'data_count': count,
                'message': '同步提交测试通过' if success else '同步提交测试失败'
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
    
    def test_data_persistence(self) -> Dict:
        """测试数据持久性"""
        logger.info("开始测试：数据持久性")
        test_name = "数据持久性测试"
        
        try:
            # 插入测试数据
            test_data = f'persistence_test_{int(time.time())}'
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO test_durability (data)
                    VALUES (%s)
                """, (test_data,))
                self.conn.commit()
            
            # 重新连接数据库
            self.conn.close()
            time.sleep(1)  # 等待1秒
            self.connect()
            
            # 验证数据仍然存在
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM test_durability
                    WHERE data = %s
                """, (test_data,))
                count = cur.fetchone()[0]
            
            success = (count == 1)
            
            result = {
                'test_name': test_name,
                'success': success,
                'test_data': test_data,
                'data_count': count,
                'message': '数据持久性测试通过' if success else '数据持久性测试失败'
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
    
    def test_transaction_durability(self) -> Dict:
        """测试事务持久性"""
        logger.info("开始测试：事务持久性")
        test_name = "事务持久性测试"
        
        try:
            # 记录初始数据数量
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test_durability")
                initial_count = cur.fetchone()[0]
            
            # 执行事务
            test_data = f'transaction_durability_{int(time.time())}'
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO test_durability (data)
                    VALUES (%s)
                """, (test_data,))
                self.conn.commit()
            
            # 重新连接数据库
            self.conn.close()
            time.sleep(1)  # 等待1秒
            self.connect()
            
            # 验证事务已持久化
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test_durability")
                final_count = cur.fetchone()[0]
                
                cur.execute("""
                    SELECT COUNT(*) FROM test_durability
                    WHERE data = %s
                """, (test_data,))
                test_data_count = cur.fetchone()[0]
            
            success = (final_count == initial_count + 1 and test_data_count == 1)
            
            result = {
                'test_name': test_name,
                'success': success,
                'initial_count': initial_count,
                'final_count': final_count,
                'test_data_count': test_data_count,
                'message': '事务持久性测试通过' if success else '事务持久性测试失败'
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
    
    def test_wal_replay(self) -> Dict:
        """测试WAL重放（模拟）"""
        logger.info("开始测试：WAL重放（模拟）")
        test_name = "WAL重放测试"
        
        try:
            # 记录WAL位置
            with self.conn.cursor() as cur:
                cur.execute("SELECT pg_current_wal_lsn()")
                wal_lsn = cur.fetchone()[0]
            
            # 执行写入操作
            test_data = f'wal_replay_{int(time.time())}'
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO test_durability (data)
                    VALUES (%s)
                """, (test_data,))
                self.conn.commit()
            
            # 验证WAL已写入
            with self.conn.cursor() as cur:
                cur.execute("SELECT pg_current_wal_lsn()")
                new_wal_lsn = cur.fetchone()[0]
            
            # 验证数据已写入
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM test_durability
                    WHERE data = %s
                """, (test_data,))
                count = cur.fetchone()[0]
            
            wal_advanced = (new_wal_lsn != wal_lsn)
            data_written = (count == 1)
            success = wal_advanced and data_written
            
            result = {
                'test_name': test_name,
                'success': success,
                'wal_advanced': wal_advanced,
                'data_written': data_written,
                'message': 'WAL重放测试通过' if success else 'WAL重放测试失败'
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
    
    def test_checkpoint(self) -> Dict:
        """测试检查点"""
        logger.info("开始测试：检查点")
        test_name = "检查点测试"
        
        try:
            # 记录检查点位置
            with self.conn.cursor() as cur:
                cur.execute("SELECT pg_current_wal_lsn()")
                before_checkpoint_lsn = cur.fetchone()[0]
            
            # 执行检查点
            with self.conn.cursor() as cur:
                cur.execute("CHECKPOINT")
            
            # 记录检查点后的WAL位置
            with self.conn.cursor() as cur:
                cur.execute("SELECT pg_current_wal_lsn()")
                after_checkpoint_lsn = cur.fetchone()[0]
            
            # 验证检查点执行成功
            checkpoint_executed = True  # CHECKPOINT命令执行成功
            
            result = {
                'test_name': test_name,
                'success': checkpoint_executed,
                'before_checkpoint_lsn': str(before_checkpoint_lsn),
                'after_checkpoint_lsn': str(after_checkpoint_lsn),
                'message': '检查点测试通过' if checkpoint_executed else '检查点测试失败'
            }
            
            logger.info(f"{test_name}: {'通过' if checkpoint_executed else '失败'}")
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
        logger.info("开始运行持久性测试套件")
        logger.info("=" * 60)
        
        results = []
        
        # 运行所有测试
        results.append(self.test_wal_write())
        results.append(self.test_synchronous_commit())
        results.append(self.test_data_persistence())
        results.append(self.test_transaction_durability())
        results.append(self.test_wal_replay())
        results.append(self.test_checkpoint())
        
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
        print("持久性测试结果")
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
    
    parser = argparse.ArgumentParser(description='持久性测试工具')
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
        choices=['all', 'wal_write', 'sync_commit', 'persistence', 'transaction', 'wal_replay', 'checkpoint'],
        default='all',
        help='要运行的测试'
    )
    
    args = parser.parse_args()
    
    tester = None
    try:
        tester = DurabilityTester(args.connection)
        tester.connect()
        
        if args.setup:
            tester.setup_test_tables()
        
        # 运行测试
        if args.test == 'all':
            results = tester.run_all_tests()
        elif args.test == 'wal_write':
            results = [tester.test_wal_write()]
        elif args.test == 'sync_commit':
            results = [tester.test_synchronous_commit()]
        elif args.test == 'persistence':
            results = [tester.test_data_persistence()]
        elif args.test == 'transaction':
            results = [tester.test_transaction_durability()]
        elif args.test == 'wal_replay':
            results = [tester.test_wal_replay()]
        elif args.test == 'checkpoint':
            results = [tester.test_checkpoint()]
        
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
