#!/usr/bin/env python3
"""
PostgreSQL 18 高级健康检查工具
全面检查数据库健康状态，生成详细报告
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import json
from datetime import datetime
from typing import Dict, List, Any

class AdvancedHealthCheck:
    """高级健康检查"""

    def __init__(self, conn_str: str):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()
        self.issues = []
        self.warnings = []
        self.info = []

    def check_version(self) -> Dict[str, Any]:
        """检查PostgreSQL版本"""
        self.cursor.execute("SELECT version();")
        version = self.cursor.fetchone()['version']

        result = {
            'check': 'PostgreSQL版本',
            'status': '✓',
            'value': version,
            'recommendation': None
        }

        if 'PostgreSQL 18' not in version:
            result['status'] = '⚠️'
            result['recommendation'] = '建议升级到PostgreSQL 18以获得最佳性能'
            self.warnings.append(result)
        else:
            self.info.append(result)

        return result

    def check_pg18_features(self) -> List[Dict[str, Any]]:
        """检查PostgreSQL 18特性"""
        results = []

        # 异步I/O
        self.cursor.execute("SHOW io_direct;")
        io_direct = self.cursor.fetchone()['io_direct']

        result = {
            'check': '异步I/O (io_direct)',
            'status': '✓' if io_direct != '' else '⚠️',
            'value': io_direct or '未启用',
            'recommendation': '建议设置 io_direct = \'data,wal\' 以获得最佳性能' if not io_direct else None
        }

        if result['status'] == '⚠️':
            self.warnings.append(result)
        else:
            self.info.append(result)

        results.append(result)

        # Skip Scan
        self.cursor.execute("SHOW enable_skip_scan;")
        skip_scan = self.cursor.fetchone()['enable_skip_scan']

        result = {
            'check': 'Skip Scan优化',
            'status': '✓' if skip_scan == 'on' else '⚠️',
            'value': skip_scan,
            'recommendation': '建议启用 enable_skip_scan = on' if skip_scan != 'on' else None
        }

        if result['status'] == '⚠️':
            self.warnings.append(result)
        else:
            self.info.append(result)

        results.append(result)

        return results

    def check_connections(self) -> Dict[str, Any]:
        """检查连接状态"""
        self.cursor.execute("""
            SELECT
                COUNT(*) AS current,
                (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') AS max
            FROM pg_stat_activity;
        """)

        row = self.cursor.fetchone()
        current = row['current']
        max_conn = row['max']
        usage_pct = (current / max_conn) * 100

        result = {
            'check': '连接数',
            'status': '✓' if usage_pct < 80 else ('⚠️' if usage_pct < 90 else '✗'),
            'value': f"{current}/{max_conn} ({usage_pct:.1f}%)",
            'recommendation': f'连接数使用率{usage_pct:.1f}%，建议增加max_connections或使用连接池' if usage_pct >= 80 else None
        }

        if result['status'] == '✗':
            self.issues.append(result)
        elif result['status'] == '⚠️':
            self.warnings.append(result)
        else:
            self.info.append(result)

        return result

    def check_cache_hit_ratio(self) -> Dict[str, Any]:
        """检查缓存命中率"""
        self.cursor.execute("""
            SELECT
                ROUND(SUM(blks_hit) * 100.0 / NULLIF(SUM(blks_hit + blks_read), 0), 2) AS ratio
            FROM pg_stat_database;
        """)

        ratio = self.cursor.fetchone()['ratio'] or 0

        result = {
            'check': '缓存命中率',
            'status': '✓' if ratio >= 95 else ('⚠️' if ratio >= 90 else '✗'),
            'value': f"{ratio:.2f}%",
            'recommendation': f'缓存命中率{ratio:.2f}%偏低，建议增加shared_buffers' if ratio < 95 else None
        }

        if result['status'] == '✗':
            self.issues.append(result)
        elif result['status'] == '⚠️':
            self.warnings.append(result)
        else:
            self.info.append(result)

        return result

    def check_bloat(self) -> Dict[str, Any]:
        """检查表膨胀"""
        self.cursor.execute("""
            SELECT COUNT(*) AS count
            FROM pg_stat_user_tables
            WHERE n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0) > 20;
        """)

        count = self.cursor.fetchone()['count']

        result = {
            'check': '表膨胀',
            'status': '✓' if count == 0 else '⚠️',
            'value': f"{count}个表膨胀严重",
            'recommendation': f'有{count}个表需要VACUUM，建议执行VACUUM ANALYZE' if count > 0 else None
        }

        if result['status'] == '⚠️':
            self.warnings.append(result)
        else:
            self.info.append(result)

        return result

    def check_locks(self) -> Dict[str, Any]:
        """检查锁等待"""
        self.cursor.execute("""
            SELECT COUNT(*) AS count
            FROM pg_locks
            WHERE NOT granted;
        """)

        count = self.cursor.fetchone()['count']

        result = {
            'check': '锁等待',
            'status': '✓' if count == 0 else '✗',
            'value': f"{count}个查询在等待锁",
            'recommendation': f'有{count}个查询被阻塞，建议检查长事务' if count > 0 else None
        }

        if result['status'] == '✗':
            self.issues.append(result)
        else:
            self.info.append(result)

        return result

    def check_long_transactions(self) -> Dict[str, Any]:
        """检查长事务"""
        self.cursor.execute("""
            SELECT COUNT(*) AS count
            FROM pg_stat_activity
            WHERE xact_start < now() - INTERVAL '5 minutes'
              AND state != 'idle';
        """)

        count = self.cursor.fetchone()['count']

        result = {
            'check': '长事务',
            'status': '✓' if count == 0 else '⚠️',
            'value': f"{count}个长事务（>5分钟）",
            'recommendation': f'有{count}个长时间运行的事务，可能影响VACUUM' if count > 0 else None
        }

        if result['status'] == '⚠️':
            self.warnings.append(result)
        else:
            self.info.append(result)

        return result

    def check_replication(self) -> Dict[str, Any]:
        """检查复制状态"""
        self.cursor.execute("""
            SELECT COUNT(*) AS count
            FROM pg_stat_replication;
        """)

        count = self.cursor.fetchone()['count']

        if count > 0:
            self.cursor.execute("""
                SELECT
                    application_name,
                    state,
                    sync_state,
                    EXTRACT(EPOCH FROM (now() - backend_start))::INT AS seconds_connected
                FROM pg_stat_replication;
            """)

            replicas = self.cursor.fetchall()

            result = {
                'check': '复制状态',
                'status': '✓',
                'value': f"{count}个从服务器在线",
                'details': [
                    f"{r['application_name']}: {r['state']} ({r['sync_state']})"
                    for r in replicas
                ],
                'recommendation': None
            }

            self.info.append(result)
        else:
            result = {
                'check': '复制状态',
                'status': 'ℹ️',
                'value': '未配置复制',
                'recommendation': '如需高可用，建议配置主从复制'
            }

            self.info.append(result)

        return result

    def check_disk_space(self) -> Dict[str, Any]:
        """检查磁盘空间"""
        self.cursor.execute("""
            SELECT
                pg_database_size(current_database()) AS size_bytes,
                pg_size_pretty(pg_database_size(current_database())) AS size_pretty
        """)

        row = self.cursor.fetchone()

        result = {
            'check': '数据库大小',
            'status': 'ℹ️',
            'value': row['size_pretty'],
            'recommendation': None
        }

        self.info.append(result)

        return result

    def check_extensions(self) -> Dict[str, Any]:
        """检查扩展"""
        self.cursor.execute("""
            SELECT extname, extversion
            FROM pg_extension
            WHERE extname IN (
                'pg_stat_statements',
                'pgcrypto',
                'vector',
                'pg_trgm',
                'uuid-ossp'
            );
        """)

        extensions = self.cursor.fetchall()
        installed = [e['extname'] for e in extensions]

        missing = []
        if 'pg_stat_statements' not in installed:
            missing.append('pg_stat_statements')
        if 'vector' not in installed:
            missing.append('vector (AI/ML)')

        result = {
            'check': '重要扩展',
            'status': '✓' if not missing else '⚠️',
            'value': f"已安装{len(extensions)}个扩展",
            'details': [f"{e['extname']} {e['extversion']}" for e in extensions],
            'recommendation': f'建议安装: {", ".join(missing)}' if missing else None
        }

        if result['status'] == '⚠️':
            self.warnings.append(result)
        else:
            self.info.append(result)

        return result

    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有检查"""
        print("="*80)
        print("PostgreSQL 18 高级健康检查")
        print(f"时间: {datetime.now()}")
        print("="*80)
        print()

        checks = []

        checks.append(self.check_version())
        checks.extend(self.check_pg18_features())
        checks.append(self.check_connections())
        checks.append(self.check_cache_hit_ratio())
        checks.append(self.check_bloat())
        checks.append(self.check_locks())
        checks.append(self.check_long_transactions())
        checks.append(self.check_replication())
        checks.append(self.check_disk_space())
        checks.append(self.check_extensions())

        # 打印结果
        for check in checks:
            print(f"{check['status']} {check['check']}: {check['value']}")
            if check.get('details'):
                for detail in check['details']:
                    print(f"     {detail}")
            if check.get('recommendation'):
                print(f"     建议: {check['recommendation']}")
            print()

        # 总结
        print("="*80)
        print("健康检查总结")
        print("="*80)
        print(f"✗ 严重问题: {len(self.issues)}")
        print(f"⚠️  警告: {len(self.warnings)}")
        print(f"✓ 正常: {len(self.info) - len(self.warnings) - len(self.issues)}")
        print()

        if self.issues:
            print("严重问题需要立即处理:")
            for issue in self.issues:
                print(f"  - {issue['check']}: {issue['recommendation']}")
            print()

        if self.warnings:
            print("警告需要关注:")
            for warning in self.warnings:
                if warning.get('recommendation'):
                    print(f"  - {warning['check']}: {warning['recommendation']}")
            print()

        return {
            'timestamp': datetime.now().isoformat(),
            'checks': checks,
            'summary': {
                'issues': len(self.issues),
                'warnings': len(self.warnings),
                'healthy': len(self.info) - len(self.warnings) - len(self.issues)
            }
        }

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL 18高级健康检查')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', required=True)
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')

    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        checker = AdvancedHealthCheck(conn_str)
        result = checker.run_all_checks()

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))

        checker.close()

        # 返回退出码
        if result['summary']['issues'] > 0:
            exit(2)
        elif result['summary']['warnings'] > 0:
            exit(1)
        else:
            exit(0)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        exit(3)

if __name__ == '__main__':
    main()
