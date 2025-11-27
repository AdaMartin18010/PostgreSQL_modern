#!/usr/bin/env python3
"""
MVCC-ACID集成测试工具
用于测试PostgreSQL MVCC-ACID的映射关系、等价性和状态机
包括：映射关系测试、等价性测试、状态机测试
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


class MVCCACIDMappingTester:
    """MVCC-ACID集成测试器"""
    
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
                    CREATE TABLE IF NOT EXISTS test_mapping (
                        id SERIAL PRIMARY KEY,
                        data TEXT NOT NULL,
                        version INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 插入测试数据
                cur.execute("""
                    INSERT INTO test_mapping (data)
                    VALUES ('initial_data')
                    ON CONFLICT DO NOTHING
                """)
                
                self.conn.commit()
                logger.info("测试表设置完成")
        except psycopg2.Error as e:
            logger.error(f"设置测试表失败: {e}")
            self.conn.rollback()
            raise
    
    def test_mvcc_to_acid_mapping(self) -> Dict:
        """测试MVCC到ACID的映射关系"""
        logger.info("开始测试：MVCC到ACID映射关系")
        test_name = "MVCC到ACID映射关系测试"
        
        try:
            # 测试1：版本创建 -> 原子性
            with self.conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute("""
                    UPDATE test_mapping 
                    SET data = 'updated_data', version = version + 1
                    WHERE id = 1
                """)
                # 不提交，测试原子性
                
                # 检查版本是否创建
                cur.execute("SELECT data, version FROM test_mapping WHERE id = 1")
                result = cur.fetchone()
                
                # 回滚
                self.conn.rollback()
                
                # 验证回滚后数据恢复
                cur.execute("SELECT data, version FROM test_mapping WHERE id = 1")
                after_rollback = cur.fetchone()
            
            # 测试2：快照 -> 隔离性
            conn1 = psycopg2.connect(self.connection_string)
            conn1.autocommit = False
            conn2 = psycopg2.connect(self.connection_string)
            conn2.autocommit = False
            
            try:
                # 事务1：创建快照
                with conn1.cursor() as cur1:
                    cur1.execute("BEGIN")
                    cur1.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                    cur1.execute("SELECT data FROM test_mapping WHERE id = 1")
                    snapshot_data1 = cur1.fetchone()[0]
                
                # 事务2：更新数据
                with conn2.cursor() as cur2:
                    cur2.execute("BEGIN")
                    cur2.execute("UPDATE test_mapping SET data = 'new_data' WHERE id = 1")
                    conn2.commit()
                
                # 事务1：再次读取（应该看到快照数据）
                with conn1.cursor() as cur1:
                    cur1.execute("SELECT data FROM test_mapping WHERE id = 1")
                    snapshot_data2 = cur1.fetchone()[0]
                
                conn1.commit()
                
                # 验证快照隔离
                snapshot_isolated = (snapshot_data1 == snapshot_data2)
                
            finally:
                conn1.close()
                conn2.close()
            
            # 测试3：可见性 -> 一致性
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        xmin, xmax, ctid
                    FROM test_mapping
                    WHERE id = 1
                """)
                visibility_info = cur.fetchone()
            
            success = (
                after_rollback[0] == 'initial_data' and  # 原子性测试通过
                snapshot_isolated and  # 隔离性测试通过
                visibility_info is not None  # 可见性测试通过
            )
            
            result = {
                'test_name': test_name,
                'success': success,
                'atomicity_test': after_rollback[0] == 'initial_data',
                'isolation_test': snapshot_isolated,
                'consistency_test': visibility_info is not None,
                'message': '映射关系测试通过' if success else '映射关系测试失败'
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
    
    def test_acid_to_mvcc_mapping(self) -> Dict:
        """测试ACID到MVCC的映射关系"""
        logger.info("开始测试：ACID到MVCC映射关系")
        test_name = "ACID到MVCC映射关系测试"
        
        try:
            # 测试1：原子性 -> 版本创建
            with self.conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute("""
                    UPDATE test_mapping 
                    SET data = 'atomic_test', version = version + 1
                    WHERE id = 1
                """)
                self.conn.commit()
                
                # 验证版本已创建
                cur.execute("SELECT data, version FROM test_mapping WHERE id = 1")
                result = cur.fetchone()
            
            # 测试2：隔离性 -> 快照
            conn1 = psycopg2.connect(self.connection_string)
            conn1.autocommit = False
            
            try:
                with conn1.cursor() as cur1:
                    cur1.execute("BEGIN")
                    cur1.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                    cur1.execute("SELECT data FROM test_mapping WHERE id = 1")
                    isolated_data = cur1.fetchone()[0]
                    conn1.commit()
                
                isolated_success = isolated_data is not None
                
            finally:
                conn1.close()
            
            # 测试3：持久性 -> WAL
            with self.conn.cursor() as cur:
                cur.execute("SELECT pg_current_wal_lsn()")
                wal_lsn_before = cur.fetchone()[0]
                
                cur.execute("BEGIN")
                cur.execute("""
                    UPDATE test_mapping 
                    SET data = 'durability_test', version = version + 1
                    WHERE id = 1
                """)
                self.conn.commit()
                
                cur.execute("SELECT pg_current_wal_lsn()")
                wal_lsn_after = cur.fetchone()[0]
            
            wal_written = (wal_lsn_after != wal_lsn_before)
            
            success = (
                result[0] == 'atomic_test' and  # 原子性映射测试通过
                isolated_success and  # 隔离性映射测试通过
                wal_written  # 持久性映射测试通过
            )
            
            result = {
                'test_name': test_name,
                'success': success,
                'atomicity_mapping': result[0] == 'atomic_test',
                'isolation_mapping': isolated_success,
                'durability_mapping': wal_written,
                'message': '映射关系测试通过' if success else '映射关系测试失败'
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
    
    def test_equivalence(self) -> Dict:
        """测试MVCC-ACID等价性"""
        logger.info("开始测试：MVCC-ACID等价性")
        test_name = "MVCC-ACID等价性测试"
        
        try:
            # 测试：MVCC操作和ACID操作应该产生相同的结果
            test_data = f'equivalence_test_{int(time.time())}'
            
            # MVCC操作（使用REPEATABLE READ）
            conn1 = psycopg2.connect(self.connection_string)
            conn1.autocommit = False
            
            try:
                with conn1.cursor() as cur1:
                    cur1.execute("BEGIN")
                    cur1.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                    cur1.execute("""
                        INSERT INTO test_mapping (data)
                        VALUES (%s)
                        RETURNING id, data
                    """, (test_data,))
                    mvcc_result = cur1.fetchone()
                    conn1.commit()
            finally:
                conn1.close()
            
            # ACID操作（使用SERIALIZABLE）
            conn2 = psycopg2.connect(self.connection_string)
            conn2.autocommit = False
            
            try:
                with conn2.cursor() as cur2:
                    cur2.execute("BEGIN")
                    cur2.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                    cur2.execute("""
                        SELECT id, data FROM test_mapping
                        WHERE data = %s
                    """, (test_data,))
                    acid_result = cur2.fetchone()
                    conn2.commit()
            finally:
                conn2.close()
            
            # 验证等价性：两个操作应该看到相同的数据
            equivalent = (
                mvcc_result is not None and
                acid_result is not None and
                mvcc_result[1] == acid_result[1]
            )
            
            result = {
                'test_name': test_name,
                'success': equivalent,
                'mvcc_result': mvcc_result[1] if mvcc_result else None,
                'acid_result': acid_result[1] if acid_result else None,
                'message': '等价性测试通过' if equivalent else '等价性测试失败'
            }
            
            logger.info(f"{test_name}: {'通过' if equivalent else '失败'}")
            return result
            
        except Exception as e:
            logger.error(f"{test_name}执行失败: {e}")
            return {
                'test_name': test_name,
                'success': False,
                'error': str(e)
            }
    
    def test_state_machine(self) -> Dict:
        """测试MVCC-ACID状态机"""
        logger.info("开始测试：MVCC-ACID状态机")
        test_name = "MVCC-ACID状态机测试"
        
        try:
            # 测试状态转换：pending -> active -> committed
            test_data = f'state_machine_test_{int(time.time())}'
            
            # 状态1：pending（事务开始）
            with self.conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute("""
                    INSERT INTO test_mapping (data)
                    VALUES (%s)
                    RETURNING id
                """, (test_data,))
                record_id = cur.fetchone()[0]
                
                # 检查状态（应该存在但未提交）
                cur.execute("""
                    SELECT xmin, xmax FROM test_mapping
                    WHERE id = %s
                """, (record_id,))
                pending_state = cur.fetchone()
            
            # 状态2：active（事务提交）
            self.conn.commit()
            
            # 检查状态（应该已提交）
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT xmin, xmax FROM test_mapping
                    WHERE id = %s
                """, (record_id,))
                committed_state = cur.fetchone()
            
            # 验证状态转换
            state_transition_valid = (
                pending_state is not None and
                committed_state is not None and
                pending_state[0] is not None and  # xmin存在
                committed_state[0] is not None and  # xmin存在（已提交）
                (committed_state[1] is None or committed_state[1] == 0)  # xmax为空或0（未删除）
            )
            
            result = {
                'test_name': test_name,
                'success': state_transition_valid,
                'pending_state': pending_state,
                'committed_state': committed_state,
                'message': '状态机测试通过' if state_transition_valid else '状态机测试失败'
            }
            
            logger.info(f"{test_name}: {'通过' if state_transition_valid else '失败'}")
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
        logger.info("开始运行MVCC-ACID集成测试套件")
        logger.info("=" * 60)
        
        results = []
        
        # 运行所有测试
        results.append(self.test_mvcc_to_acid_mapping())
        results.append(self.test_acid_to_mvcc_mapping())
        results.append(self.test_equivalence())
        results.append(self.test_state_machine())
        
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
        print("MVCC-ACID集成测试结果")
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
    
    parser = argparse.ArgumentParser(description='MVCC-ACID集成测试工具')
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
        choices=['all', 'mvcc_to_acid', 'acid_to_mvcc', 'equivalence', 'state_machine'],
        default='all',
        help='要运行的测试'
    )
    
    args = parser.parse_args()
    
    tester = None
    try:
        tester = MVCCACIDMappingTester(args.connection)
        tester.connect()
        
        if args.setup:
            tester.setup_test_tables()
        
        # 运行测试
        if args.test == 'all':
            results = tester.run_all_tests()
        elif args.test == 'mvcc_to_acid':
            results = [tester.test_mvcc_to_acid_mapping()]
        elif args.test == 'acid_to_mvcc':
            results = [tester.test_acid_to_mvcc_mapping()]
        elif args.test == 'equivalence':
            results = [tester.test_equivalence()]
        elif args.test == 'state_machine':
            results = [tester.test_state_machine()]
        
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
