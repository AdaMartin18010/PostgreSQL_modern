#!/usr/bin/env python3
"""
PostgreSQL连接池管理器
智能管理连接池，监控连接使用情况
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import argparse
import time
from datetime import datetime
from typing import Optional
import threading
import queue

class ConnectionPoolManager:
    """连接池管理器"""

    def __init__(self, conn_str: str, min_conn: int = 5, max_conn: int = 20):
        self.conn_str = conn_str
        self.min_conn = min_conn
        self.max_conn = max_conn

        # 创建连接池
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            min_conn,
            max_conn,
            conn_str
        )

        print(f"✓ 连接池已创建")
        print(f"  最小连接: {min_conn}")
        print(f"  最大连接: {max_conn}")
        print()

        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'wait_time_total': 0,
            'active_connections': 0
        }

        self.lock = threading.Lock()

    def get_connection(self, timeout: int = 5) -> Optional[psycopg2.extensions.connection]:
        """获取连接"""

        start_time = time.time()

        with self.lock:
            self.stats['total_requests'] += 1

        try:
            conn = self.pool.getconn()

            wait_time = time.time() - start_time

            with self.lock:
                self.stats['successful_requests'] += 1
                self.stats['wait_time_total'] += wait_time
                self.stats['active_connections'] += 1

            return conn

        except pool.PoolError as e:
            with self.lock:
                self.stats['failed_requests'] += 1

            print(f"✗ 获取连接失败: {e}")
            return None

    def put_connection(self, conn: psycopg2.extensions.connection):
        """归还连接"""

        try:
            self.pool.putconn(conn)

            with self.lock:
                self.stats['active_connections'] -= 1

        except Exception as e:
            print(f"✗ 归还连接失败: {e}")

    def execute_query(self, query: str, params=None) -> Optional[list]:
        """执行查询"""

        conn = self.get_connection()

        if not conn:
            return None

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)

            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = []

            cursor.close()
            return result

        except Exception as e:
            conn.rollback()
            print(f"✗ 查询失败: {e}")
            return None

        finally:
            self.put_connection(conn)

    def get_pool_stats(self) -> dict:
        """获取连接池统计"""

        with self.lock:
            stats = self.stats.copy()

        if stats['successful_requests'] > 0:
            stats['avg_wait_time'] = stats['wait_time_total'] / stats['successful_requests']
        else:
            stats['avg_wait_time'] = 0

        stats['success_rate'] = stats['successful_requests'] / max(stats['total_requests'], 1) * 100

        return stats

    def monitor_database_connections(self):
        """监控数据库连接"""

        result = self.execute_query("""
            SELECT
                COUNT(*) FILTER (WHERE state = 'active') AS active,
                COUNT(*) FILTER (WHERE state = 'idle') AS idle,
                COUNT(*) FILTER (WHERE state = 'idle in transaction') AS idle_in_transaction,
                COUNT(*) AS total
            FROM pg_stat_activity
            WHERE datname = current_database();
        """)

        if result:
            return result[0]
        return None

    def print_stats(self):
        """打印统计信息"""

        pool_stats = self.get_pool_stats()
        db_stats = self.monitor_database_connections()

        print("="*80)
        print(f"连接池统计 - {datetime.now()}")
        print("="*80)

        print("\n连接池状态:")
        print(f"  总请求数: {pool_stats['total_requests']:,}")
        print(f"  成功: {pool_stats['successful_requests']:,}")
        print(f"  失败: {pool_stats['failed_requests']:,}")
        print(f"  成功率: {pool_stats['success_rate']:.2f}%")
        print(f"  平均等待时间: {pool_stats['avg_wait_time']*1000:.2f}ms")
        print(f"  当前活跃连接: {pool_stats['active_connections']}")

        if db_stats:
            print("\n数据库连接状态:")
            print(f"  活跃查询: {db_stats['active']}")
            print(f"  空闲连接: {db_stats['idle']}")
            print(f"  事务中: {db_stats['idle_in_transaction']}")
            print(f"  总连接数: {db_stats['total']}")

            # 告警
            if db_stats['idle_in_transaction'] > 0:
                print(f"  ⚠️  有{db_stats['idle_in_transaction']}个事务未提交!")

        print()

    def stress_test(self, num_threads: int = 10, queries_per_thread: int = 100):
        """压力测试"""

        print(f"开始压力测试:")
        print(f"  线程数: {num_threads}")
        print(f"  每线程查询数: {queries_per_thread}")
        print()

        def worker(worker_id: int, results_queue: queue.Queue):
            """工作线程"""
            success = 0
            failed = 0

            for i in range(queries_per_thread):
                result = self.execute_query("SELECT 1;")

                if result:
                    success += 1
                else:
                    failed += 1

            results_queue.put({
                'worker_id': worker_id,
                'success': success,
                'failed': failed
            })

        # 启动工作线程
        threads = []
        results_queue = queue.Queue()

        start_time = time.time()

        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i, results_queue))
            t.start()
            threads.append(t)

        # 等待完成
        for t in threads:
            t.join()

        duration = time.time() - start_time

        # 收集结果
        total_success = 0
        total_failed = 0

        while not results_queue.empty():
            result = results_queue.get()
            total_success += result['success']
            total_failed += result['failed']

        # 打印结果
        print("压力测试完成:")
        print(f"  耗时: {duration:.2f}秒")
        print(f"  总查询数: {total_success + total_failed:,}")
        print(f"  成功: {total_success:,}")
        print(f"  失败: {total_failed:,}")
        print(f"  QPS: {(total_success + total_failed) / duration:.0f}")
        print()

    def close_all(self):
        """关闭所有连接"""

        try:
            self.pool.closeall()
            print("✓ 连接池已关闭")
        except Exception as e:
            print(f"✗ 关闭连接池失败: {e}")

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL连接池管理器')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', required=True)
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')
    parser.add_argument('--min-conn', type=int, default=5, help='最小连接数')
    parser.add_argument('--max-conn', type=int, default=20, help='最大连接数')
    parser.add_argument('--stress-test', action='store_true', help='运行压力测试')
    parser.add_argument('--threads', type=int, default=10, help='压力测试线程数')
    parser.add_argument('--queries', type=int, default=100, help='每线程查询数')
    parser.add_argument('--monitor', action='store_true', help='持续监控')
    parser.add_argument('--interval', type=int, default=5, help='监控间隔（秒）')

    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        manager = ConnectionPoolManager(conn_str, args.min_conn, args.max_conn)

        if args.stress_test:
            manager.stress_test(num_threads=args.threads, queries_per_thread=args.queries)

        if args.monitor:
            try:
                while True:
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')

                    manager.print_stats()

                    print(f"刷新间隔: {args.interval}秒 (Ctrl+C退出)")

                    time.sleep(args.interval)

            except KeyboardInterrupt:
                print("\n监控已停止")
        else:
            manager.print_stats()

        manager.close_all()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
