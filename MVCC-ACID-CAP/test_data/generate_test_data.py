#!/usr/bin/env python3
"""
测试数据生成脚本
用于生成MVCC-ACID-CAP相关的测试数据
"""

import psycopg2
from psycopg2 import sql
import random
import string
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self, connection_string):
        """初始化连接"""
        try:
            self.conn = psycopg2.connect(connection_string)
            self.conn.autocommit = False
            logger.info("数据库连接成功")
        except psycopg2.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def generate_random_string(self, length=10):
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def create_base_tables(self):
        """创建基础测试表"""
        try:
            with self.conn.cursor() as cur:
                # 用户表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 订单表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_orders (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES test_users(id),
                        product_name VARCHAR(100),
                        quantity INTEGER,
                        price DECIMAL(10, 2),
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 产品表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_products (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        price DECIMAL(10, 2),
                        stock INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                self.conn.commit()
                logger.info("基础测试表创建完成")
        except psycopg2.Error as e:
            logger.error(f"创建基础测试表失败: {e}")
            self.conn.rollback()
            raise
    
    def generate_users(self, count=100):
        """生成用户测试数据"""
        try:
            with self.conn.cursor() as cur:
                for i in range(count):
                    name = f"User_{i+1}_{self.generate_random_string(5)}"
                    email = f"user_{i+1}@example.com"
                    
                    cur.execute("""
                        INSERT INTO test_users (name, email)
                        VALUES (%s, %s)
                    """, (name, email))
                
                self.conn.commit()
                logger.info(f"生成 {count} 个用户测试数据")
        except psycopg2.Error as e:
            logger.error(f"生成用户测试数据失败: {e}")
            self.conn.rollback()
            raise
    
    def generate_products(self, count=50):
        """生成产品测试数据"""
        try:
            with self.conn.cursor() as cur:
                products = [
                    ("Laptop", "High-performance laptop", 999.99),
                    ("Phone", "Smartphone", 699.99),
                    ("Tablet", "Tablet device", 399.99),
                    ("Monitor", "4K Monitor", 299.99),
                    ("Keyboard", "Mechanical keyboard", 149.99),
                ]
                
                for i in range(count):
                    product = random.choice(products)
                    name = f"{product[0]}_{i+1}"
                    description = f"{product[1]} - {self.generate_random_string(10)}"
                    price = product[2] + random.uniform(-50, 50)
                    stock = random.randint(0, 1000)
                    
                    cur.execute("""
                        INSERT INTO test_products (name, description, price, stock)
                        VALUES (%s, %s, %s, %s)
                    """, (name, description, price, stock))
                
                self.conn.commit()
                logger.info(f"生成 {count} 个产品测试数据")
        except psycopg2.Error as e:
            logger.error(f"生成产品测试数据失败: {e}")
            self.conn.rollback()
            raise
    
    def generate_orders(self, count=200):
        """生成订单测试数据"""
        try:
            with self.conn.cursor() as cur:
                # 获取用户ID列表
                cur.execute("SELECT id FROM test_users")
                user_ids = [row[0] for row in cur.fetchall()]
                
                # 获取产品列表
                cur.execute("SELECT id, name, price FROM test_products")
                products = cur.fetchall()
                
                if not user_ids or not products:
                    logger.warning("用户或产品数据不足，跳过订单生成")
                    return
                
                statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
                
                for i in range(count):
                    user_id = random.choice(user_ids)
                    product = random.choice(products)
                    quantity = random.randint(1, 10)
                    price = product[2] * quantity
                    status = random.choice(statuses)
                    
                    cur.execute("""
                        INSERT INTO test_orders (user_id, product_name, quantity, price, status)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, product[1], quantity, price, status))
                
                self.conn.commit()
                logger.info(f"生成 {count} 个订单测试数据")
        except psycopg2.Error as e:
            logger.error(f"生成订单测试数据失败: {e}")
            self.conn.rollback()
            raise
    
    def generate_mvcc_test_data(self):
        """生成MVCC测试数据（版本链）"""
        try:
            with self.conn.cursor() as cur:
                # 创建MVCC测试表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS mvcc_test (
                        id SERIAL PRIMARY KEY,
                        data TEXT,
                        version INTEGER DEFAULT 1
                    )
                """)
                
                # 插入初始数据
                cur.execute("""
                    INSERT INTO mvcc_test (data, version)
                    VALUES ('Initial data', 1)
                """)
                
                # 模拟多次更新，创建版本链
                for i in range(5):
                    cur.execute("""
                        UPDATE mvcc_test
                        SET data = %s, version = version + 1
                        WHERE id = 1
                    """, (f"Updated data version {i+2}",))
                
                self.conn.commit()
                logger.info("MVCC测试数据生成完成")
        except psycopg2.Error as e:
            logger.error(f"生成MVCC测试数据失败: {e}")
            self.conn.rollback()
            raise
    
    def cleanup(self):
        """清理测试数据"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS test_orders CASCADE")
                cur.execute("DROP TABLE IF EXISTS test_products CASCADE")
                cur.execute("DROP TABLE IF EXISTS test_users CASCADE")
                cur.execute("DROP TABLE IF EXISTS mvcc_test CASCADE")
                self.conn.commit()
                logger.info("测试数据清理完成")
        except psycopg2.Error as e:
            logger.error(f"清理测试数据失败: {e}")
            self.conn.rollback()
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='生成测试数据')
    parser.add_argument('--connection', default='dbname=testdb user=postgres password=postgres host=localhost',
                       help='数据库连接字符串')
    parser.add_argument('--users', type=int, default=100, help='用户数量')
    parser.add_argument('--products', type=int, default=50, help='产品数量')
    parser.add_argument('--orders', type=int, default=200, help='订单数量')
    parser.add_argument('--cleanup', action='store_true', help='清理现有测试数据')
    
    args = parser.parse_args()
    
    generator = None
    try:
        generator = TestDataGenerator(args.connection)
        
        if args.cleanup:
            generator.cleanup()
        
        generator.create_base_tables()
        generator.generate_users(args.users)
        generator.generate_products(args.products)
        generator.generate_orders(args.orders)
        generator.generate_mvcc_test_data()
        
        logger.info("所有测试数据生成完成")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
    finally:
        if generator:
            generator.close()

if __name__ == "__main__":
    main()
