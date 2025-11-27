#!/usr/bin/env python3
"""
一致性测试工具
用于测试PostgreSQL MVCC-ACID的一致性特性
包括：约束检查测试、触发器一致性测试、数据完整性测试
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


class ConsistencyTester:
    """一致性测试器"""
    
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
                # 账户表（带约束）
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_accounts (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                        CHECK (balance >= 0),
                        CONSTRAINT unique_name UNIQUE (name)
                    )
                """)
                
                # 订单表（带外键）
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_orders (
                        id SERIAL PRIMARY KEY,
                        account_id INTEGER NOT NULL,
                        amount DECIMAL(10, 2) NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_account 
                            FOREIGN KEY (account_id) 
                            REFERENCES test_accounts(id)
                            ON DELETE CASCADE
                    )
                """)
                
                # 触发器测试表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_audit_log (
                        id SERIAL PRIMARY KEY,
                        table_name VARCHAR(100) NOT NULL,
                        operation VARCHAR(20) NOT NULL,
                        record_id INTEGER NOT NULL,
                        old_data JSONB,
                        new_data JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建触发器函数
                cur.execute("""
                    CREATE OR REPLACE FUNCTION audit_trigger_func()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        IF TG_OP = 'INSERT' THEN
                            INSERT INTO test_audit_log (table_name, operation, record_id, new_data)
                            VALUES (TG_TABLE_NAME, TG_OP, NEW.id, row_to_json(NEW));
                            RETURN NEW;
                        ELSIF TG_OP = 'UPDATE' THEN
                            INSERT INTO test_audit_log (table_name, operation, record_id, old_data, new_data)
                            VALUES (TG_TABLE_NAME, TG_OP, NEW.id, row_to_json(OLD), row_to_json(NEW));
                            RETURN NEW;
                        ELSIF TG_OP = 'DELETE' THEN
                            INSERT INTO test_audit_log (table_name, operation, record_id, old_data)
                            VALUES (TG_TABLE_NAME, TG_OP, OLD.id, row_to_json(OLD));
                            RETURN OLD;
                        END IF;
                        RETURN NULL;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                
                # 创建触发器
                cur.execute("""
                    DROP TRIGGER IF EXISTS audit_trigger ON test_accounts;
                    CREATE TRIGGER audit_trigger
                    AFTER INSERT OR UPDATE OR DELETE ON test_accounts
                    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
                """)
                
                # 插入测试数据
                cur.execute("""
                    INSERT INTO test_accounts (name, balance)
                    VALUES 
                        ('Alice', 1000.00),
                        ('Bob', 500.00)
                    ON CONFLICT (name) DO NOTHING
                """)
                
                self.conn.commit()
                logger.info("测试表设置完成")
        except psycopg2.Error as e:
            logger.error(f"设置测试表失败: {e}")
            self.conn.rollback()
            raise
    
    def test_check_constraint(self) -> Dict:
        """测试检查约束"""
        logger.info("开始测试：检查约束")
        test_name = "检查约束测试"
        
        try:
            # 记录初始状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test_accounts WHERE name = 'Alice'")
                initial_count = cur.fetchone()[0]
            
            # 尝试违反约束
            constraint_violated = False
            try:
                with self.conn.cursor() as cur:
                    # 尝试插入负余额（违反CHECK约束）
                    cur.execute("""
                        INSERT INTO test_accounts (name, balance)
                        VALUES ('Charlie', -100.00)
                    """)
                    self.conn.commit()
            except psycopg2.IntegrityError as e:
                logger.info(f"捕获约束违反错误: {e}")
                self.conn.rollback()
                constraint_violated = True
            
            # 验证约束生效
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test_accounts WHERE name = 'Charlie'")
                final_count = cur.fetchone()[0]
            
            # 验证结果
            success = (constraint_violated and final_count == 0)
            
            result = {
                'test_name': test_name,
                'success': success,
                'constraint_violated': constraint_violated,
                'final_count': final_count,
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
    
    def test_unique_constraint(self) -> Dict:
        """测试唯一约束"""
        logger.info("开始测试：唯一约束")
        test_name = "唯一约束测试"
        
        try:
            # 记录初始状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test_accounts WHERE name = 'Alice'")
                initial_count = cur.fetchone()[0]
            
            # 尝试违反唯一约束
            constraint_violated = False
            try:
                with self.conn.cursor() as cur:
                    # 尝试插入重复名称（违反UNIQUE约束）
                    cur.execute("""
                        INSERT INTO test_accounts (name, balance)
                        VALUES ('Alice', 2000.00)
                    """)
                    self.conn.commit()
            except psycopg2.IntegrityError as e:
                logger.info(f"捕获唯一约束违反错误: {e}")
                self.conn.rollback()
                constraint_violated = True
            
            # 验证约束生效
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test_accounts WHERE name = 'Alice'")
                final_count = cur.fetchone()[0]
            
            # 验证结果
            success = (constraint_violated and final_count == initial_count)
            
            result = {
                'test_name': test_name,
                'success': success,
                'constraint_violated': constraint_violated,
                'initial_count': initial_count,
                'final_count': final_count,
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
    
    def test_foreign_key_constraint(self) -> Dict:
        """测试外键约束"""
        logger.info("开始测试：外键约束")
        test_name = "外键约束测试"
        
        try:
            # 记录初始状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test_orders")
                initial_order_count = cur.fetchone()[0]
            
            # 尝试违反外键约束
            constraint_violated = False
            try:
                with self.conn.cursor() as cur:
                    # 尝试插入不存在的account_id（违反外键约束）
                    cur.execute("""
                        INSERT INTO test_orders (account_id, amount)
                        VALUES (99999, 100.00)
                    """)
                    self.conn.commit()
            except psycopg2.IntegrityError as e:
                logger.info(f"捕获外键约束违反错误: {e}")
                self.conn.rollback()
                constraint_violated = True
            
            # 验证约束生效
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test_orders WHERE account_id = 99999")
                final_order_count = cur.fetchone()[0]
            
            # 验证结果
            success = (constraint_violated and final_order_count == 0)
            
            result = {
                'test_name': test_name,
                'success': success,
                'constraint_violated': constraint_violated,
                'final_order_count': final_order_count,
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
    
    def test_trigger_consistency(self) -> Dict:
        """测试触发器一致性"""
        logger.info("开始测试：触发器一致性")
        test_name = "触发器一致性测试"
        
        try:
            # 记录初始审计日志数量
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test_audit_log")
                initial_audit_count = cur.fetchone()[0]
            
            # 执行操作触发触发器
            with self.conn.cursor() as cur:
                # 插入操作
                cur.execute("""
                    INSERT INTO test_accounts (name, balance)
                    VALUES ('David', 300.00)
                """)
                
                # 更新操作
                cur.execute("""
                    UPDATE test_accounts 
                    SET balance = balance + 100 
                    WHERE name = 'David'
                """)
                
                # 删除操作
                cur.execute("""
                    DELETE FROM test_accounts 
                    WHERE name = 'David'
                """)
                
                self.conn.commit()
            
            # 验证触发器执行
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM test_audit_log
                    WHERE table_name = 'test_accounts'
                    AND operation IN ('INSERT', 'UPDATE', 'DELETE')
                """)
                final_audit_count = cur.fetchone()[0]
            
            # 验证结果：应该有3条审计日志（INSERT、UPDATE、DELETE）
            expected_count = initial_audit_count + 3
            success = (final_audit_count >= expected_count)
            
            result = {
                'test_name': test_name,
                'success': success,
                'initial_audit_count': initial_audit_count,
                'final_audit_count': final_audit_count,
                'expected_count': expected_count,
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
    
    def test_data_integrity(self) -> Dict:
        """测试数据完整性"""
        logger.info("开始测试：数据完整性")
        test_name = "数据完整性测试"
        
        try:
            # 测试1：检查约束完整性
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM test_accounts
                    WHERE balance < 0
                """)
                negative_balance_count = cur.fetchone()[0]
            
            # 测试2：检查外键完整性
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM test_orders o
                    WHERE NOT EXISTS (
                        SELECT 1 FROM test_accounts a 
                        WHERE a.id = o.account_id
                    )
                """)
                orphaned_orders_count = cur.fetchone()[0]
            
            # 测试3：检查唯一约束完整性
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT name, COUNT(*) as cnt
                    FROM test_accounts
                    GROUP BY name
                    HAVING COUNT(*) > 1
                """)
                duplicate_names = cur.fetchall()
            
            # 验证结果
            success = (
                negative_balance_count == 0 and
                orphaned_orders_count == 0 and
                len(duplicate_names) == 0
            )
            
            result = {
                'test_name': test_name,
                'success': success,
                'negative_balance_count': negative_balance_count,
                'orphaned_orders_count': orphaned_orders_count,
                'duplicate_names_count': len(duplicate_names),
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
    
    def test_transaction_consistency(self) -> Dict:
        """测试事务一致性"""
        logger.info("开始测试：事务一致性")
        test_name = "事务一致性测试"
        
        try:
            # 记录初始状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                initial_balance = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM test_orders WHERE account_id = 1")
                initial_order_count = cur.fetchone()[0]
            
            # 执行事务：扣款和创建订单
            try:
                with self.conn.cursor() as cur:
                    # 扣款
                    cur.execute("""
                        UPDATE test_accounts 
                        SET balance = balance - 100 
                        WHERE name = 'Alice'
                    """)
                    
                    # 创建订单
                    cur.execute("""
                        INSERT INTO test_orders (account_id, amount)
                        VALUES (1, 100.00)
                    """)
                    
                    # 模拟错误，回滚事务
                    raise Exception("模拟错误")
                    
            except Exception:
                self.conn.rollback()
            
            # 验证回滚后状态
            with self.conn.cursor() as cur:
                cur.execute("SELECT balance FROM test_accounts WHERE name = 'Alice'")
                final_balance = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM test_orders WHERE account_id = 1")
                final_order_count = cur.fetchone()[0]
            
            # 验证结果：回滚后应该恢复初始状态
            success = (
                initial_balance == final_balance and
                initial_order_count == final_order_count
            )
            
            result = {
                'test_name': test_name,
                'success': success,
                'initial_balance': float(initial_balance),
                'final_balance': float(final_balance),
                'initial_order_count': initial_order_count,
                'final_order_count': final_order_count,
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
        logger.info("开始运行一致性测试套件")
        logger.info("=" * 60)
        
        results = []
        
        # 运行所有测试
        results.append(self.test_check_constraint())
        results.append(self.test_unique_constraint())
        results.append(self.test_foreign_key_constraint())
        results.append(self.test_trigger_consistency())
        results.append(self.test_data_integrity())
        results.append(self.test_transaction_consistency())
        
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
        print("一致性测试结果")
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
    
    parser = argparse.ArgumentParser(description='一致性测试工具')
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
        choices=['all', 'check', 'unique', 'foreign_key', 'trigger', 'integrity', 'transaction'],
        default='all',
        help='要运行的测试'
    )
    
    args = parser.parse_args()
    
    tester = None
    try:
        tester = ConsistencyTester(args.connection)
        tester.connect()
        
        if args.setup:
            tester.setup_test_tables()
        
        # 运行测试
        if args.test == 'all':
            results = tester.run_all_tests()
        elif args.test == 'check':
            results = [tester.test_check_constraint()]
        elif args.test == 'unique':
            results = [tester.test_unique_constraint()]
        elif args.test == 'foreign_key':
            results = [tester.test_foreign_key_constraint()]
        elif args.test == 'trigger':
            results = [tester.test_trigger_consistency()]
        elif args.test == 'integrity':
            results = [tester.test_data_integrity()]
        elif args.test == 'transaction':
            results = [tester.test_transaction_consistency()]
        
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
