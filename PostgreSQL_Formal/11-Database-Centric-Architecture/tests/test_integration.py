#!/usr/bin/env python3
# ============================================
# DCA集成测试套件
# 运行方式: pytest tests/test_integration.py -v
# ============================================

import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 6432,  # PgBouncer端口
    'database': 'dca_demo',
    'user': 'postgres',
    'password': 'postgres'
}


class DatabaseTestHelper:
    """数据库测试辅助类"""
    
    @staticmethod
    def get_connection():
        """获取数据库连接"""
        return psycopg2.connect(**DB_CONFIG)
    
    @staticmethod
    def setup_test_data():
        """准备测试数据"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        # 清理旧测试数据
        cursor.execute("""
            DELETE FROM order_items WHERE order_id IN (
                SELECT id FROM orders WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::UUID
            );
            DELETE FROM orders WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::UUID;
            DELETE FROM inventory_reservations WHERE product_id IN (1, 2, 3);
            DELETE FROM users WHERE id = '550e8400-e29b-41d4-a716-446655440000'::UUID;
            DELETE FROM products WHERE id IN (1, 2, 3, 4, 5);
        """)
        
        # 插入测试用户
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash)
            VALUES ('550e8400-e29b-41d4-a716-446655440000'::UUID, 'testuser', 'test@example.com', 'hash123')
            ON CONFLICT DO NOTHING;
        """)
        
        # 插入测试产品
        cursor.execute("""
            INSERT INTO products (id, sku, name, price, stock_quantity)
            VALUES 
                (1, 'TEST001', 'Test Product 1', 99.99, 100),
                (2, 'TEST002', 'Test Product 2', 149.99, 50),
                (3, 'TEST003', 'Test Product 3', 29.99, 0),
                (4, 'TEST004', 'High Value Product', 999.99, 10),
                (5, 'TEST005', 'Bulk Product', 9.99, 1000)
            ON CONFLICT DO NOTHING;
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    
    @staticmethod
    def cleanup_test_data():
        """清理测试数据"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM order_items WHERE order_id IN (
                SELECT id FROM orders WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::UUID
            );
            DELETE FROM orders WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::UUID;
            DELETE FROM inventory_reservations WHERE product_id IN (1, 2, 3, 4, 5);
            DELETE FROM users WHERE id = '550e8400-e29b-41d4-a716-446655440000'::UUID;
            DELETE FROM products WHERE id IN (1, 2, 3, 4, 5);
        """)
        conn.commit()
        cursor.close()
        conn.close()


class TestUserRegistration:
    """用户注册测试类"""
    
    def setup_method(self):
        DatabaseTestHelper.setup_test_data()
    
    def teardown_method(self):
        DatabaseTestHelper.cleanup_test_data()
    
    def test_register_user_success(self):
        """测试成功注册用户"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CALL sp_user_register(%s, %s, %s, NULL, NULL, NULL);
            FETCH ALL IN "";
        """, ('newuser123', 'newuser123@example.com', 'SecurePass123!'))
        
        result = cursor.fetchone()
        conn.commit()
        
        assert result[1] == True, f"Registration should succeed: {result[2]}"
        assert result[0] is not None, "Should return user_id"
        
        cursor.close()
        conn.close()
    
    def test_register_duplicate_username(self):
        """测试重复用户名应该失败"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        # 第一次注册
        cursor.execute("""
            CALL sp_user_register(%s, %s, %s, NULL, NULL, NULL);
            FETCH ALL IN "";
        """, ('duplicateuser', 'dup1@example.com', 'SecurePass123!'))
        conn.commit()
        
        # 第二次注册相同用户名
        cursor.execute("""
            CALL sp_user_register(%s, %s, %s, NULL, NULL, NULL);
            FETCH ALL IN "";
        """, ('duplicateuser', 'dup2@example.com', 'SecurePass123!'))
        
        result = cursor.fetchone()
        conn.commit()
        
        assert result[1] == False, "Duplicate username should fail"
        
        cursor.close()
        conn.close()
    
    def test_register_invalid_email(self):
        """测试无效邮箱格式应该失败"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        with pytest.raises(Exception) as exc_info:
            cursor.execute("""
                CALL sp_user_register(%s, %s, %s, NULL, NULL, NULL);
            """, ('validuser', 'invalid-email', 'SecurePass123!'))
            conn.commit()
        
        assert 'Invalid email' in str(exc_info.value)
        
        cursor.close()
        conn.close()


class TestOrderCreation:
    """订单创建测试类"""
    
    def setup_method(self):
        DatabaseTestHelper.setup_test_data()
    
    def teardown_method(self):
        DatabaseTestHelper.cleanup_test_data()
    
    def test_create_order_success(self):
        """测试成功创建订单"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        items = json.dumps([{"product_id": 1, "quantity": 2}])
        shipping = json.dumps({"address": "123 Test St", "city": "Beijing"})
        
        cursor.execute("""
            CALL sp_order_create(%s, %s, %s, NULL, NULL, NULL, NULL);
            FETCH ALL IN "";
        """, ('550e8400-e29b-41d4-a716-446655440000', items, shipping))
        
        result = cursor.fetchone()
        conn.commit()
        
        assert result[2] == True, f"Order creation should succeed: {result[3]}"
        assert result[0] is not None, "Should return order_id"
        assert result[1] == 199.98, f"Total should be 199.98, got {result[1]}"
        
        # 验证库存扣减
        cursor.execute("SELECT stock_quantity FROM products WHERE id = 1")
        stock = cursor.fetchone()[0]
        assert stock == 98, f"Stock should be 98, got {stock}"
        
        cursor.close()
        conn.close()
    
    def test_create_order_insufficient_stock(self):
        """测试库存不足应该失败"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        items = json.dumps([{"product_id": 3, "quantity": 1}])  # 产品3库存为0
        shipping = json.dumps({})
        
        with pytest.raises(Exception) as exc_info:
            cursor.execute("""
                CALL sp_order_create(%s, %s, %s, NULL, NULL, NULL, NULL);
            """, ('550e8400-e29b-41d4-a716-446655440000', items, shipping))
            conn.commit()
        
        assert 'Insufficient stock' in str(exc_info.value)
        
        cursor.close()
        conn.close()
    
    def test_create_order_empty_items(self):
        """测试空订单应该失败"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        items = json.dumps([])
        shipping = json.dumps({})
        
        with pytest.raises(Exception) as exc_info:
            cursor.execute("""
                CALL sp_order_create(%s, %s, %s, NULL, NULL, NULL, NULL);
            """, ('550e8400-e29b-41d4-a716-446655440000', items, shipping))
            conn.commit()
        
        assert 'at least one item' in str(exc_info.value)
        
        cursor.close()
        conn.close()
    
    def test_create_order_product_not_found(self):
        """测试产品不存在应该失败"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        items = json.dumps([{"product_id": 99999, "quantity": 1}])
        shipping = json.dumps({})
        
        with pytest.raises(Exception) as exc_info:
            cursor.execute("""
                CALL sp_order_create(%s, %s, %s, NULL, NULL, NULL, NULL);
            """, ('550e8400-e29b-41d4-a716-446655440000', items, shipping))
            conn.commit()
        
        assert 'not found' in str(exc_info.value)
        
        cursor.close()
        conn.close()


class TestOrderLifecycle:
    """订单生命周期测试类"""
    
    def setup_method(self):
        DatabaseTestHelper.setup_test_data()
    
    def teardown_method(self):
        DatabaseTestHelper.cleanup_test_data()
    
    def test_order_payment_and_cancel(self):
        """测试订单支付和取消流程"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        # 1. 创建订单
        items = json.dumps([{"product_id": 1, "quantity": 5}])
        shipping = json.dumps({"address": "123 Test St"})
        
        cursor.execute("""
            CALL sp_order_create(%s, %s, %s, NULL, NULL, NULL, NULL);
            FETCH ALL IN "";
        """, ('550e8400-e29b-41d4-a716-446655440000', items, shipping))
        
        result = cursor.fetchone()
        conn.commit()
        order_id = result[0]
        
        assert result[2] == True, "Order creation should succeed"
        
        # 2. 确认支付
        cursor.execute("""
            CALL sp_order_confirm_payment(%s, %s, %s, NULL, NULL);
            FETCH ALL IN "";
        """, (order_id, 'credit_card', 'PAY123456'))
        
        result = cursor.fetchone()
        conn.commit()
        
        assert result[0] == True, "Payment confirmation should succeed"
        
        # 3. 验证订单状态
        cursor.execute("SELECT status FROM orders WHERE id = %s", (order_id,))
        status = cursor.fetchone()[0]
        assert status == 'paid', f"Order status should be 'paid', got '{status}'"
        
        cursor.close()
        conn.close()
    
    def test_cancel_order_restores_stock(self):
        """测试取消订单恢复库存"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        # 获取初始库存
        cursor.execute("SELECT stock_quantity FROM products WHERE id = 2")
        initial_stock = cursor.fetchone()[0]
        
        # 创建订单
        items = json.dumps([{"product_id": 2, "quantity": 10}])
        shipping = json.dumps({})
        
        cursor.execute("""
            CALL sp_order_create(%s, %s, %s, NULL, NULL, NULL, NULL);
            FETCH ALL IN "";
        """, ('550e8400-e29b-41d4-a716-446655440000', items, shipping))
        
        result = cursor.fetchone()
        conn.commit()
        order_id = result[0]
        
        # 验证库存扣减
        cursor.execute("SELECT stock_quantity FROM products WHERE id = 2")
        after_order = cursor.fetchone()[0]
        assert after_order == initial_stock - 10
        
        # 取消订单
        cursor.execute("""
            CALL sp_order_cancel(%s, %s, NULL, NULL);
            FETCH ALL IN "";
        """, (order_id, 'Test cancellation'))
        
        result = cursor.fetchone()
        conn.commit()
        
        assert result[0] == True, "Cancellation should succeed"
        
        # 验证库存恢复
        cursor.execute("SELECT stock_quantity FROM products WHERE id = 2")
        after_cancel = cursor.fetchone()[0]
        assert after_cancel == initial_stock, f"Stock should be restored to {initial_stock}, got {after_cancel}"
        
        cursor.close()
        conn.close()


class TestConcurrency:
    """并发测试类"""
    
    def setup_method(self):
        DatabaseTestHelper.setup_test_data()
    
    def teardown_method(self):
        DatabaseTestHelper.cleanup_test_data()
    
    def test_concurrent_stock_deduction(self):
        """测试并发库存扣减不超卖"""
        
        def create_order(thread_id):
            """线程函数：创建订单"""
            try:
                conn = DatabaseTestHelper.get_connection()
                cursor = conn.cursor()
                
                items = json.dumps([{"product_id": 5, "quantity": 100}])  # 产品5库存1000
                shipping = json.dumps({})
                
                cursor.execute("""
                    CALL sp_order_create(%s, %s, %s, NULL, NULL, NULL, NULL);
                    FETCH ALL IN "";
                """, ('550e8400-e29b-41d4-a716-446655440000', items, shipping))
                
                result = cursor.fetchone()
                conn.commit()
                
                cursor.close()
                conn.close()
                
                return {'thread': thread_id, 'success': result[2], 'order_id': result[0]}
            except Exception as e:
                return {'thread': thread_id, 'success': False, 'error': str(e)}
        
        # 启动15个线程同时购买（总共1500，超过库存1000）
        results = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(create_order, i) for i in range(15)]
            for future in as_completed(futures):
                results.append(future.result())
        
        # 统计成功和失败
        success_count = sum(1 for r in results if r['success'])
        fail_count = sum(1 for r in results if not r['success'])
        
        print(f"\n并发测试结果: 成功={success_count}, 失败={fail_count}")
        
        # 最多只能成功10个（1000/100）
        assert success_count <= 10, f"Should not oversell, but {success_count} orders succeeded"
        
        # 验证最终库存
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stock_quantity FROM products WHERE id = 5")
        final_stock = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        expected_stock = 1000 - (success_count * 100)
        assert final_stock == expected_stock, f"Stock should be {expected_stock}, got {final_stock}"


class TestPerformance:
    """性能测试类"""
    
    def setup_method(self):
        DatabaseTestHelper.setup_test_data()
    
    def teardown_method(self):
        DatabaseTestHelper.cleanup_test_data()
    
    def test_order_creation_performance(self):
        """测试订单创建性能"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        items = json.dumps([{"product_id": 1, "quantity": 1}])
        shipping = json.dumps({"address": "Test"})
        
        start_time = time.time()
        
        # 创建100个订单
        for i in range(100):
            cursor.execute("""
                CALL sp_order_create(%s, %s, %s, NULL, NULL, NULL, NULL);
                FETCH ALL IN "";
            """, ('550e8400-e29b-41d4-a716-446655440000', items, shipping))
            conn.commit()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n性能测试结果: 100个订单耗时 {duration:.2f} 秒")
        print(f"平均每个订单: {duration/100*1000:.2f} ms")
        
        # 断言：100个订单应该在10秒内完成（平均100ms/订单）
        assert duration < 10, f"Order creation too slow: {duration}s for 100 orders"
        
        cursor.close()
        conn.close()
    
    def test_query_performance(self):
        """测试查询性能"""
        conn = DatabaseTestHelper.get_connection()
        cursor = conn.cursor()
        
        start_time = time.time()
        
        # 执行用户订单列表查询10次
        for _ in range(10):
            cursor.execute("""
                SELECT * FROM fn_user_orders('550e8400-e29b-41d4-a716-446655440000'::UUID, 1, 20)
            """)
            cursor.fetchall()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n查询性能测试: 10次查询耗时 {duration:.2f} 秒")
        print(f"平均每次查询: {duration/10*1000:.2f} ms")
        
        # 断言：10次查询应该在1秒内完成
        assert duration < 1, f"Query too slow: {duration}s for 10 queries"
        
        cursor.close()
        conn.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
