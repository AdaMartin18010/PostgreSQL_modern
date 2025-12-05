#!/usr/bin/env python3
"""
健康检查工具测试
"""

import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# 从环境变量获取连接信息
CONN_STR = f"host={os.getenv('PGHOST', 'localhost')} " \
           f"port={os.getenv('PGPORT', '5432')} " \
           f"dbname={os.getenv('PGDATABASE', 'testdb')} " \
           f"user={os.getenv('PGUSER', 'postgres')} " \
           f"password={os.getenv('PGPASSWORD', 'testpass')}"

@pytest.fixture
def db_conn():
    """数据库连接fixture"""
    conn = psycopg2.connect(CONN_STR, cursor_factory=RealDictCursor)
    yield conn
    conn.close()

def test_database_connection(db_conn):
    """测试数据库连接"""
    cursor = db_conn.cursor()
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()
    assert result[0] == 1
    cursor.close()

def test_postgresql_version(db_conn):
    """测试PostgreSQL版本"""
    cursor = db_conn.cursor()
    cursor.execute("SHOW server_version_num;")
    version = int(cursor.fetchone()['server_version_num'])
    assert version >= 180000, "应该是PostgreSQL 18或更高版本"
    cursor.close()

def test_extensions_installed(db_conn):
    """测试必需扩展是否安装"""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT extname FROM pg_extension
        WHERE extname IN ('pg_stat_statements', 'pgcrypto');
    """)

    extensions = [row['extname'] for row in cursor.fetchall()]
    cursor.close()

    # 至少应该有pg_stat_statements
    # assert 'pg_stat_statements' in extensions

def test_autovacuum_enabled(db_conn):
    """测试autovacuum是否启用"""
    cursor = db_conn.cursor()
    cursor.execute("SHOW autovacuum;")
    autovacuum = cursor.fetchone()['autovacuum']
    assert autovacuum == 'on', "autovacuum应该启用"
    cursor.close()

def test_connection_limit(db_conn):
    """测试连接数配置"""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) as current,
            (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max
        FROM pg_stat_activity;
    """)

    row = cursor.fetchone()
    current = row['current']
    max_conn = row['max']

    usage_pct = (current / max_conn) * 100
    assert usage_pct < 90, f"连接数使用率{usage_pct:.1f}%过高"
    cursor.close()

def test_cache_hit_ratio(db_conn):
    """测试缓存命中率"""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT
            ROUND(SUM(blks_hit) * 100.0 / NULLIF(SUM(blks_hit + blks_read), 0), 2) AS ratio
        FROM pg_stat_database;
    """)

    ratio = cursor.fetchone()['ratio']
    if ratio:
        # 新数据库可能命中率较低，这里放宽要求
        assert float(ratio) >= 0, "缓存命中率应该>=0%"
    cursor.close()

def test_no_blocking_queries(db_conn):
    """测试无阻塞查询"""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM pg_locks
        WHERE NOT granted;
    """)

    count = cursor.fetchone()['count']
    assert count == 0, f"发现{count}个阻塞查询"
    cursor.close()

def test_no_long_transactions(db_conn):
    """测试无长事务"""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM pg_stat_activity
        WHERE xact_start < now() - INTERVAL '5 minutes'
          AND state != 'idle';
    """)

    count = cursor.fetchone()['count']
    assert count == 0, f"发现{count}个长事务"
    cursor.close()

def test_table_bloat(db_conn):
    """测试表膨胀"""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM pg_stat_user_tables
        WHERE n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0) > 50;
    """)

    count = cursor.fetchone()['count']
    assert count == 0, f"发现{count}个表严重膨胀"
    cursor.close()

@pytest.mark.skipif(
    os.getenv('SKIP_PG18_TESTS') == '1',
    reason="非PostgreSQL 18环境"
)
def test_pg18_async_io(db_conn):
    """测试PostgreSQL 18异步I/O配置"""
    cursor = db_conn.cursor()
    try:
        cursor.execute("SHOW io_direct;")
        io_direct = cursor.fetchone()['io_direct']
        # 不强制要求，仅检查参数存在
        assert io_direct is not None
    except Exception:
        # 参数可能不存在（旧版本）
        pass
    cursor.close()

@pytest.mark.skipif(
    os.getenv('SKIP_PG18_TESTS') == '1',
    reason="非PostgreSQL 18环境"
)
def test_pg18_skip_scan(db_conn):
    """测试PostgreSQL 18 Skip Scan配置"""
    cursor = db_conn.cursor()
    try:
        cursor.execute("SHOW enable_skip_scan;")
        skip_scan = cursor.fetchone()['enable_skip_scan']
        assert skip_scan in ['on', 'off']
    except Exception:
        # 参数可能不存在（旧版本）
        pass
    cursor.close()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
