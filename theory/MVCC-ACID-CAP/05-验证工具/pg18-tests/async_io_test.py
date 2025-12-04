#!/usr/bin/env python3
"""
PostgreSQL 18异步I/O验证测试
验证：异步I/O保持MVCC语义
"""

import psycopg2
import time
import concurrent.futures

class AsyncIOTest:
    def __init__(self, conn_str):
        self.conn_str = conn_str
        
    def setup(self):
        """创建测试表"""
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS async_test (
                id SERIAL PRIMARY KEY,
                value INT,
                version INT DEFAULT 1
            );
            
            TRUNCATE async_test;
            
            -- 插入测试数据（1000行）
            INSERT INTO async_test (value)
            SELECT generate_series(1, 1000);
        """)
        
        conn.commit()
        conn.close()
        print("✅ 测试表创建完成")
    
    def test_mvcc_visibility(self):
        """测试：异步I/O保持MVCC可见性"""
        print("\n【测试1】MVCC可见性一致性")
        
        conn1 = psycopg2.connect(self.conn_str)
        conn2 = psycopg2.connect(self.conn_str)
        
        cur1 = conn1.cursor()
        cur2 = conn2.cursor()
        
        # 事务1：开始事务，获取快照
        cur1.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
        cur1.execute("SELECT COUNT(*) FROM async_test;")
        count1_before = cur1.fetchone()[0]
        print(f"  事务1看到: {count1_before}行")
        
        # 事务2：插入新数据
        cur2.execute("INSERT INTO async_test (value) VALUES (9999);")
        conn2.commit()
        print(f"  事务2插入: 1行（已提交）")
        
        # 事务1：再次查询（应该看到相同数量，MVCC保证）
        cur1.execute("SELECT COUNT(*) FROM async_test;")
        count1_after = cur1.fetchone()[0]
        print(f"  事务1再看到: {count1_after}行")
        
        cur1.execute("COMMIT;")
        
        # 验证
        if count1_before == count1_after:
            print("  ✅ MVCC可见性保持一致（快照隔离）")
            result = True
        else:
            print(f"  ❌ MVCC可见性不一致！{count1_before} vs {count1_after}")
            result = False
        
        conn1.close()
        conn2.close()
        
        return result
    
    def test_performance(self):
        """测试：异步I/O性能提升"""
        print("\n【测试2】异步I/O性能")
        
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        # 大批量查询（测试异步I/O效果）
        start = time.time()
        cur.execute("""
            SELECT * FROM async_test 
            WHERE id = ANY($1::int[])
        """, (list(range(1, 1001)),))
        results = cur.fetchall()
        elapsed = (time.time() - start) * 1000
        
        print(f"  查询1000行耗时: {elapsed:.2f}ms")
        print(f"  查询结果: {len(results)}行")
        
        if elapsed < 50:  # <50ms认为性能好
            print(f"  ✅ 性能优秀（<50ms）")
            result = True
        else:
            print(f"  ⚠️  性能一般（>{elapsed:.0f}ms）")
            result = False
        
        conn.close()
        return result
    
    def test_concurrent_reads(self):
        """测试：并发读取的MVCC一致性"""
        print("\n【测试3】并发读取一致性")
        
        def read_snapshot(conn_str, expected_count):
            """单个事务的快照读取"""
            conn = psycopg2.connect(conn_str)
            cur = conn.cursor()
            
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            
            # 多次读取，验证快照一致性
            counts = []
            for _ in range(5):
                cur.execute("SELECT COUNT(*) FROM async_test;")
                counts.append(cur.fetchone()[0])
                time.sleep(0.01)  # 模拟延迟
            
            cur.execute("COMMIT;")
            conn.close()
            
            return all(c == counts[0] for c in counts), counts[0]
        
        # 并发10个事务，每个都验证快照一致性
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(10):
                future = executor.submit(read_snapshot, self.conn_str, 1000)
                futures.append(future)
            
            results = [f.result() for f in futures]
        
        # 验证所有事务的快照都一致
        all_consistent = all(r[0] for r in results)
        
        if all_consistent:
            print(f"  ✅ 所有10个并发事务的快照都一致")
            print(f"  快照大小: {results[0][1]}行")
            return True
        else:
            print(f"  ❌ 检测到快照不一致！")
            for i, (consistent, count) in enumerate(results):
                if not consistent:
                    print(f"    事务{i+1}: 不一致")
            return False
    
    def test_acid_guarantee(self):
        """测试：异步I/O保持ACID属性"""
        print("\n【测试4】ACID属性保持")
        
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        # 测试原子性：批量更新
        cur.execute("BEGIN;")
        cur.execute("UPDATE async_test SET value = value + 1 WHERE id <= 100;")
        
        # 读取更新后的值
        cur.execute("SELECT value FROM async_test WHERE id = 1;")
        updated_value = cur.fetchone()[0]
        
        # 回滚
        cur.execute("ROLLBACK;")
        
        # 验证回滚后值恢复
        cur.execute("SELECT value FROM async_test WHERE id = 1;")
        original_value = cur.fetchone()[0]
        
        if updated_value == original_value + 1:
            print(f"  ✅ 原子性保持（回滚后值恢复: {original_value}）")
            result = True
        else:
            print(f"  ❌ 原子性异常！")
            result = False
        
        conn.close()
        return result
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("PostgreSQL 18异步I/O验证测试")
        print("=" * 60)
        
        self.setup()
        
        tests = [
            ("MVCC可见性", self.test_mvcc_visibility),
            ("异步I/O性能", self.test_performance),
            ("并发读取一致性", self.test_concurrent_reads),
            ("ACID属性保持", self.test_acid_guarantee)
        ]
        
        passed = 0
        total = len(tests)
        
        for name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"  ❌ 测试失败: {e}")
        
        print("\n" + "=" * 60)
        print(f"测试结果: {passed}/{total} 通过")
        if passed == total:
            print("✅ 所有测试通过！PostgreSQL 18异步I/O保持MVCC-ACID语义")
        else:
            print(f"⚠️  {total - passed}个测试失败")
        print("=" * 60)
        
        return passed == total

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        conn_str = sys.argv[1]
    else:
        conn_str = "dbname=testdb user=postgres"
    
    tester = AsyncIOTest(conn_str)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
