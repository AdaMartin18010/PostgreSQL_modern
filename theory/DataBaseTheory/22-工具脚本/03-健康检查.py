#!/usr/bin/env python3
"""
PostgreSQL 18健康检查工具
快速诊断数据库问题
"""

import psycopg2
import sys
from datetime import datetime

class PostgreSQLHealthCheck:
    def __init__(self, host='localhost', port=5432, dbname='postgres', user='postgres'):
        self.conn = psycopg2.connect(
            host=host, port=port, dbname=dbname, user=user
        )
        self.cur = self.conn.cursor()
        self.issues = []
        
    def check_version(self):
        """检查PostgreSQL版本"""
        self.cur.execute("SHOW server_version;")
        version = self.cur.fetchone()[0]
        print(f"✅ PostgreSQL版本: {version}")
        return "18" in version
    
    def check_connections(self):
        """检查连接数"""
        self.cur.execute("""
            SELECT 
                current_setting('max_connections')::int as max_conn,
                COUNT(*) as current_conn
            FROM pg_stat_activity;
        """)
        max_conn, current_conn = self.cur.fetchone()
        usage_pct = (current_conn / max_conn) * 100
        
        if usage_pct > 80:
            self.issues.append(f"⚠️  连接使用率{usage_pct:.1f}% (当前{current_conn}/{max_conn})")
        else:
            print(f"✅ 连接数正常: {current_conn}/{max_conn} ({usage_pct:.1f}%)")
    
    def check_cache_hit_ratio(self):
        """检查缓存命中率"""
        self.cur.execute("""
            SELECT 
                ROUND(
                    sum(heap_blks_hit) * 100.0 / 
                    NULLIF(sum(heap_blks_hit + heap_blks_read), 0),
                    2
                ) as hit_ratio
            FROM pg_statio_user_tables;
        """)
        hit_ratio = self.cur.fetchone()[0]
        
        if hit_ratio and hit_ratio < 90:
            self.issues.append(f"⚠️  缓存命中率低: {hit_ratio}% (应该>95%)")
        else:
            print(f"✅ 缓存命中率: {hit_ratio}%")
    
    def check_slow_queries(self):
        """检查慢查询"""
        self.cur.execute("""
            SELECT COUNT(*)
            FROM pg_stat_statements
            WHERE mean_exec_time > 1000;  -- >1秒
        """)
        slow_count = self.cur.fetchone()[0]
        
        if slow_count > 10:
            self.issues.append(f"⚠️  发现{slow_count}个平均执行时间>1秒的查询")
            
            # 显示Top 3
            self.cur.execute("""
                SELECT 
                    LEFT(query, 80),
                    ROUND(mean_exec_time::numeric, 2)
                FROM pg_stat_statements
                WHERE mean_exec_time > 1000
                ORDER BY mean_exec_time DESC
                LIMIT 3;
            """)
            print("   Top 3慢查询:")
            for query, time_ms in self.cur.fetchall():
                print(f"   - {time_ms}ms: {query}...")
        else:
            print(f"✅ 慢查询数量: {slow_count}")
    
    def check_bloat(self):
        """检查表膨胀"""
        self.cur.execute("""
            SELECT 
                schemaname || '.' || tablename,
                ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2)
            FROM pg_stat_user_tables
            WHERE n_dead_tup > 1000
              AND n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0) > 20
            ORDER BY 2 DESC
            LIMIT 5;
        """)
        bloated_tables = self.cur.fetchall()
        
        if bloated_tables:
            self.issues.append(f"⚠️  发现{len(bloated_tables)}个膨胀表(死元组>20%)")
            for table, dead_pct in bloated_tables:
                print(f"   - {table}: {dead_pct}%死元组")
        else:
            print("✅ 无严重表膨胀")
    
    def check_locks(self):
        """检查锁等待"""
        self.cur.execute("""
            SELECT COUNT(*)
            FROM pg_locks
            WHERE NOT granted;
        """)
        lock_count = self.cur.fetchone()[0]
        
        if lock_count > 0:
            self.issues.append(f"⚠️  发现{lock_count}个锁等待")
        else:
            print("✅ 无锁等待")
    
    def check_replication(self):
        """检查复制延迟"""
        self.cur.execute("""
            SELECT 
                client_addr,
                pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) as lag_bytes
            FROM pg_stat_replication;
        """)
        replicas = self.cur.fetchall()
        
        if replicas:
            for addr, lag in replicas:
                if lag > 1024 * 1024 * 100:  # >100MB
                    self.issues.append(f"⚠️  从库{addr}延迟{lag/1024/1024:.1f}MB")
                else:
                    print(f"✅ 从库{addr}延迟正常: {lag/1024:.1f}KB")
        else:
            print("ℹ️  无复制配置")
    
    def check_pg18_features(self):
        """⭐ 检查PostgreSQL 18特性使用情况"""
        features = [
            ('enable_builtin_connection_pooling', '内置连接池'),
            ('enable_async_io', '异步I/O'),
            ('jit', 'JIT编译'),
        ]
        
        print("\n【PostgreSQL 18特性】")
        for setting, name in features:
            try:
                self.cur.execute(f"SHOW {setting};")
                value = self.cur.fetchone()[0]
                status = "✅ 已启用" if value == 'on' else "⚠️  未启用"
                print(f"{status} {name}: {value}")
            except:
                print(f"ℹ️  {name}: 不支持")
    
    def run_all_checks(self):
        """运行所有检查"""
        print("=" * 60)
        print(f"PostgreSQL健康检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        
        is_pg18 = self.check_version()
        print()
        
        self.check_connections()
        self.check_cache_hit_ratio()
        self.check_slow_queries()
        self.check_bloat()
        self.check_locks()
        self.check_replication()
        
        if is_pg18:
            self.check_pg18_features()
        
        print()
        print("=" * 60)
        if self.issues:
            print(f"⚠️  发现 {len(self.issues)} 个问题:")
            for issue in self.issues:
                print(issue)
            print()
            print("建议运行优化建议脚本: psql -f 02-自动优化建议.sql")
            return 1
        else:
            print("✅ 所有检查通过！数据库健康！")
            return 0
        print("=" * 60)
    
    def close(self):
        self.cur.close()
        self.conn.close()

if __name__ == '__main__':
    import os
    
    checker = PostgreSQLHealthCheck(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        dbname=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'postgres')
    )
    
    try:
        exit_code = checker.run_all_checks()
        sys.exit(exit_code)
    finally:
        checker.close()
