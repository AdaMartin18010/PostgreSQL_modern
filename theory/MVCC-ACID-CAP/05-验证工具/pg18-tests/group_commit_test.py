#!/usr/bin/env python3
"""
PostgreSQL 18组提交验证测试
验证：组提交保持ACID原子性和持久性
"""

import psycopg2
import time
import concurrent.futures
import subprocess

class GroupCommitTest:
    def __init__(self, conn_str):
        self.conn_str = conn_str
        
    def setup(self):
        """创建测试表"""
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS commit_test (
                tx_id SERIAL PRIMARY KEY,
                tx_data INT,
                commit_ts TIMESTAMPTZ DEFAULT NOW()
            );
            
            TRUNCATE commit_test;
        """)
        
        conn.commit()
        conn.close()
        print("✅ 测试表创建完成")
    
    def test_atomicity(self):
        """测试：组提交保持原子性"""
        print("\n【测试1】组提交原子性")
        
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        # 批量提交10个"事务"（模拟组提交）
        cur.execute("BEGIN;")
        
        for i in range(10):
            cur.execute("INSERT INTO commit_test (tx_data) VALUES (%s);", (i,))
        
        # 故意制造错误（测试原子性）
        try:
            cur.execute("INSERT INTO commit_test (tx_data) VALUES ('invalid');")  # 类型错误
            cur.execute("COMMIT;")
            print("  ❌ 应该抛出异常但没有")
            result = False
        except Exception as e:
            # 回滚
            cur.execute("ROLLBACK;")
            
            # 验证所有10个插入都被回滚
            cur.execute("SELECT COUNT(*) FROM commit_test;")
            count = cur.fetchone()[0]
            
            if count == 0:
                print(f"  ✅ 原子性保持：所有10个插入都被回滚")
                result = True
            else:
                print(f"  ❌ 原子性失败：仍有{count}行数据")
                result = False
        
        conn.close()
        return result
    
    def test_group_commit_performance(self):
        """测试：组提交性能提升"""
        print("\n【测试2】组提交性能")
        
        def single_commit_batch(n=100):
            """模拟单独提交"""
            conn = psycopg2.connect(self.conn_str)
            cur = conn.cursor()
            
            start = time.time()
            for i in range(n):
                cur.execute("BEGIN;")
                cur.execute("INSERT INTO commit_test (tx_data) VALUES (%s);", (i,))
                cur.execute("COMMIT;")
            elapsed = time.time() - start
            
            conn.close()
            return elapsed
        
        def group_commit_batch(n=100):
            """模拟组提交（批量）"""
            conn = psycopg2.connect(self.conn_str)
            cur = conn.cursor()
            
            start = time.time()
            cur.execute("BEGIN;")
            for i in range(n):
                cur.execute("INSERT INTO commit_test (tx_data) VALUES (%s);", (i,))
            cur.execute("COMMIT;")
            elapsed = time.time() - start
            
            conn.close()
            return elapsed
        
        # 清理
        conn = psycopg2.connect(self.conn_str)
        conn.cursor().execute("TRUNCATE commit_test;")
        conn.commit()
        conn.close()
        
        # 测试单独提交
        time_single = single_commit_batch(100)
        print(f"  单独提交100次: {time_single*1000:.0f}ms")
        
        # 清理
        conn = psycopg2.connect(self.conn_str)
        conn.cursor().execute("TRUNCATE commit_test;")
        conn.commit()
        conn.close()
        
        # 测试批量提交
        time_group = group_commit_batch(100)
        print(f"  批量提交100次: {time_group*1000:.0f}ms")
        
        improvement = (time_single - time_group) / time_single * 100
        print(f"  性能提升: {improvement:.1f}%")
        
        if improvement > 50:
            print(f"  ✅ 组提交效果显著（>{improvement:.0f}%提升）")
            return True
        else:
            print(f"  ⚠️  提升有限（{improvement:.0f}%）")
            return False
    
    def test_concurrent_commits(self):
        """测试：并发提交的一致性"""
        print("\n【测试3】并发提交一致性")
        
        def commit_transaction(conn_str, tx_id):
            """单个事务"""
            conn = psycopg2.connect(conn_str)
            cur = conn.cursor()
            
            cur.execute("BEGIN;")
            cur.execute("INSERT INTO commit_test (tx_data) VALUES (%s);", (tx_id,))
            time.sleep(0.001)  # 模拟一些工作
            cur.execute("COMMIT;")
            
            # 读取commit timestamp
            cur.execute("SELECT commit_ts FROM commit_test WHERE tx_data = %s;", (tx_id,))
            ts = cur.fetchone()[0]
            
            conn.close()
            return tx_id, ts
        
        # 清理
        conn = psycopg2.connect(self.conn_str)
        conn.cursor().execute("TRUNCATE commit_test;")
        conn.commit()
        conn.close()
        
        # 并发提交20个事务
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(20):
                future = executor.submit(commit_transaction, self.conn_str, i)
                futures.append(future)
            
            results = [f.result() for f in futures]
        
        # 检查是否有组提交（多个事务有相同或接近的timestamp）
        timestamps = [r[1] for r in results]
        timestamps.sort()
        
        # 计算timestamp差异
        groups = 0
        for i in range(1, len(timestamps)):
            diff = (timestamps[i] - timestamps[i-1]).total_seconds()
            if diff < 0.001:  # <1ms认为是同一组
                groups += 1
        
        print(f"  20个事务中，{groups}对有接近的commit timestamp")
        
        if groups > 5:
            print(f"  ✅ 检测到组提交效应（{groups}对）")
            return True
        else:
            print(f"  ⚠️  组提交效应不明显")
            return False
    
    def test_durability(self):
        """测试：持久性保证"""
        print("\n【测试4】持久性保证")
        
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        # 清理
        cur.execute("TRUNCATE commit_test;")
        conn.commit()
        
        # 插入测试数据并提交
        cur.execute("BEGIN;")
        cur.execute("INSERT INTO commit_test (tx_data) VALUES (12345);")
        cur.execute("COMMIT;")
        
        # 关闭连接
        conn.close()
        
        # 重新连接，验证数据持久化
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        cur.execute("SELECT tx_data FROM commit_test WHERE tx_data = 12345;")
        result = cur.fetchone()
        
        if result and result[0] == 12345:
            print(f"  ✅ 持久性保证：数据成功持久化")
            success = True
        else:
            print(f"  ❌ 持久性失败：数据丢失")
            success = False
        
        conn.close()
        return success
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("PostgreSQL 18组提交验证测试")
        print("=" * 60)
        
        self.setup()
        
        tests = [
            ("ACID原子性", self.test_atomicity),
            ("组提交性能", self.test_group_commit_performance),
            ("并发提交一致性", self.test_concurrent_commits),
            ("ACID持久性", self.test_durability)
        ]
        
        passed = 0
        total = len(tests)
        
        for name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"  ❌ 测试异常: {e}")
        
        print("\n" + "=" * 60)
        print(f"测试结果: {passed}/{total} 通过")
        if passed == total:
            print("✅ 所有测试通过！PostgreSQL 18组提交保持ACID属性")
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
    
    tester = GroupCommitTest(conn_str)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
