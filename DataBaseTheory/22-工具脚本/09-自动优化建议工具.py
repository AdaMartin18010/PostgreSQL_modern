#!/usr/bin/env python3
"""
PostgreSQL自动优化建议工具
功能: 分析数据库状态，提供自动化优化建议
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
from typing import List, Dict
from datetime import datetime

class PostgreSQLOptimizationAdvisor:
    """PostgreSQL优化建议工具"""

    def __init__(self, conn_str: str):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()
        self.recommendations = []

    def analyze_configuration(self):
        """分析配置参数"""

        # 获取系统内存
        self.cursor.execute("""
            SELECT setting::bigint * 8192 AS shared_buffers_bytes
            FROM pg_settings WHERE name = 'shared_buffers';
        """)
        shared_buffers = self.cursor.fetchone()['shared_buffers_bytes']

        # 推荐shared_buffers为系统内存的25%
        # 这里简化处理，实际需要获取系统内存
        if shared_buffers < 4 * 1024 * 1024 * 1024:  # <4GB
            self.recommendations.append({
                'category': 'Configuration',
                'severity': 'HIGH',
                'issue': 'shared_buffers配置过小',
                'current': f'{shared_buffers // (1024**3)}GB',
                'recommendation': '建议设置为系统内存的25%',
                'sql': "ALTER SYSTEM SET shared_buffers = '4GB'; -- 然后重启"
            })

        # 检查work_mem
        self.cursor.execute("SELECT setting FROM pg_settings WHERE name = 'work_mem';")
        work_mem = self.cursor.fetchone()['setting']

        if int(work_mem) < 16384:  # <16MB
            self.recommendations.append({
                'category': 'Configuration',
                'severity': 'MEDIUM',
                'issue': 'work_mem配置过小，可能导致磁盘排序',
                'current': work_mem,
                'recommendation': '建议至少64MB',
                'sql': "ALTER SYSTEM SET work_mem = '64MB';"
            })

        # PostgreSQL 18特性检查
        self.cursor.execute("SELECT setting FROM pg_settings WHERE name = 'io_direct';")
        io_direct = self.cursor.fetchone()['setting']

        if io_direct == 'off':
            self.recommendations.append({
                'category': 'Performance',
                'severity': 'HIGH',
                'issue': 'PostgreSQL 18异步I/O未启用',
                'current': 'off',
                'recommendation': '启用直接I/O以提升性能(NVMe SSD环境)',
                'sql': "ALTER SYSTEM SET io_direct = 'data'; SELECT pg_reload_conf();"
            })

    def analyze_indexes(self):
        """分析索引问题"""

        # 未使用的索引
        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                indexname,
                pg_size_pretty(pg_relation_size(indexrelid)) AS size,
                idx_scan
            FROM pg_stat_user_indexes
            WHERE idx_scan = 0
              AND indexrelname NOT LIKE '%_pkey'
            ORDER BY pg_relation_size(indexrelid) DESC
            LIMIT 10;
        """)

        unused = self.cursor.fetchall()
        for idx in unused:
            self.recommendations.append({
                'category': 'Index',
                'severity': 'MEDIUM',
                'issue': f"未使用的索引: {idx['indexname']}",
                'current': f"大小: {idx['size']}, 扫描次数: 0",
                'recommendation': '考虑删除以节省空间和写入开销',
                'sql': f"DROP INDEX CONCURRENTLY {idx['indexname']};"
            })

        # 缺失索引（高顺序扫描）
        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan
            FROM pg_stat_user_tables
            WHERE seq_scan > 1000
              AND seq_tup_read / NULLIF(seq_scan, 0) > 10000
            ORDER BY seq_scan * seq_tup_read DESC
            LIMIT 5;
        """)

        missing = self.cursor.fetchall()
        for table in missing:
            self.recommendations.append({
                'category': 'Index',
                'severity': 'HIGH',
                'issue': f"表{table['tablename']}可能缺少索引",
                'current': f"顺序扫描: {table['seq_scan']}次, 平均读取: {table['seq_tup_read']//table['seq_scan']}行",
                'recommendation': '分析查询模式，添加合适的索引',
                'sql': f"-- 分析表: {table['tablename']}\n-- SELECT * FROM pg_stat_statements WHERE query LIKE '%{table['tablename']}%';"
            })

        # 重复索引检测
        self.cursor.execute("""
            SELECT
                t.tablename,
                array_agg(i.indexname) AS indexes,
                string_agg(i.indexdef, ' | ') AS definitions
            FROM pg_indexes i
            JOIN pg_tables t ON i.tablename = t.tablename
            WHERE i.schemaname = 'public'
            GROUP BY t.tablename, regexp_replace(i.indexdef, '\\s+', ' ', 'g')
            HAVING COUNT(*) > 1;
        """)

        duplicates = self.cursor.fetchall()
        for dup in duplicates:
            self.recommendations.append({
                'category': 'Index',
                'severity': 'MEDIUM',
                'issue': f"表{dup['tablename']}存在重复索引",
                'current': f"索引: {', '.join(dup['indexes'])}",
                'recommendation': '保留一个，删除其他',
                'sql': f"-- 检查并删除重复索引\n-- {dup['definitions']}"
            })

    def analyze_vacuum(self):
        """分析VACUUM问题"""

        # 表膨胀检查
        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                n_dead_tup,
                n_live_tup,
                ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio,
                last_autovacuum
            FROM pg_stat_user_tables
            WHERE n_dead_tup > 10000
              AND n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0) > 15
            ORDER BY n_dead_tup DESC
            LIMIT 10;
        """)

        bloated = self.cursor.fetchall()
        for table in bloated:
            self.recommendations.append({
                'category': 'VACUUM',
                'severity': 'HIGH',
                'issue': f"表{table['tablename']}严重膨胀",
                'current': f"死元组: {table['n_dead_tup']}, 比例: {table['dead_ratio']}%",
                'recommendation': '立即执行VACUUM',
                'sql': f"VACUUM (VERBOSE, ANALYZE) {table['tablename']};"
            })

        # 事务ID接近wrap-around
        self.cursor.execute("""
            SELECT
                datname,
                age(datfrozenxid) AS xid_age,
                2^31 - 1000000 - age(datfrozenxid) AS xids_remaining
            FROM pg_database
            WHERE age(datfrozenxid) > 1500000000
            ORDER BY age(datfrozenxid) DESC;
        """)

        wrap_risk = self.cursor.fetchall()
        for db in wrap_risk:
            self.recommendations.append({
                'category': 'VACUUM',
                'severity': 'CRITICAL',
                'issue': f"数据库{db['datname']}事务ID即将耗尽",
                'current': f"事务年龄: {db['xid_age']}, 剩余: {db['xids_remaining']}",
                'recommendation': '紧急执行VACUUM FREEZE',
                'sql': f"VACUUM (FREEZE, VERBOSE) {db['datname']};"
            })

    def analyze_queries(self):
        """分析查询性能"""

        # 检查pg_stat_statements
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM pg_extension
            WHERE extname = 'pg_stat_statements';
        """)

        if self.cursor.fetchone()['count'] == 0:
            self.recommendations.append({
                'category': 'Monitoring',
                'severity': 'HIGH',
                'issue': 'pg_stat_statements扩展未安装',
                'current': '无法分析查询性能',
                'recommendation': '安装pg_stat_statements扩展',
                'sql': "CREATE EXTENSION pg_stat_statements;"
            })
            return

        # 慢查询
        self.cursor.execute("""
            SELECT
                LEFT(query, 100) AS query_preview,
                calls,
                total_exec_time / 1000 AS total_sec,
                mean_exec_time AS avg_ms,
                max_exec_time AS max_ms
            FROM pg_stat_statements
            WHERE mean_exec_time > 1000
            ORDER BY mean_exec_time DESC
            LIMIT 5;
        """)

        slow = self.cursor.fetchall()
        for query in slow:
            self.recommendations.append({
                'category': 'Query',
                'severity': 'HIGH',
                'issue': '存在慢查询',
                'current': f"平均耗时: {query['avg_ms']:.2f}ms, 调用: {query['calls']}次",
                'recommendation': '优化查询或添加索引',
                'sql': f"-- 分析查询:\n-- EXPLAIN (ANALYZE, BUFFERS) {query['query_preview']}..."
            })

    def analyze_connections(self):
        """分析连接问题"""

        self.cursor.execute("""
            SELECT
                COUNT(*) AS total,
                setting::int AS max_conn
            FROM pg_stat_activity, pg_settings
            WHERE pg_settings.name = 'max_connections'
            GROUP BY max_conn;
        """)

        result = self.cursor.fetchone()
        if result:
            ratio = (result['total'] / result['max_conn']) * 100

            if ratio > 80:
                self.recommendations.append({
                    'category': 'Connection',
                    'severity': 'HIGH',
                    'issue': '连接数接近上限',
                    'current': f"{result['total']}/{result['max_conn']} ({ratio:.1f}%)",
                    'recommendation': '使用连接池(pgBouncer)或增加max_connections',
                    'sql': "-- 配置pgBouncer连接池"
                })

        # 空闲事务
        self.cursor.execute("""
            SELECT COUNT(*) AS count
            FROM pg_stat_activity
            WHERE state = 'idle in transaction'
              AND state_change < now() - INTERVAL '5 minutes';
        """)

        idle_tx = self.cursor.fetchone()['count']
        if idle_tx > 0:
            self.recommendations.append({
                'category': 'Connection',
                'severity': 'MEDIUM',
                'issue': f'{idle_tx}个长时间空闲事务',
                'current': '占用连接且可能持有锁',
                'recommendation': '检查应用程序事务管理',
                'sql': """
-- 查看空闲事务:
SELECT pid, usename, state, state_change
FROM pg_stat_activity
WHERE state = 'idle in transaction';
                """
            })

    def analyze_replication(self):
        """分析复制状态"""

        # 检查是否为Primary
        self.cursor.execute("SELECT pg_is_in_recovery();")
        is_standby = self.cursor.fetchone()['pg_is_in_recovery']

        if not is_standby:
            # 复制延迟
            self.cursor.execute("""
                SELECT
                    application_name,
                    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) / 1024 / 1024 AS lag_mb
                FROM pg_stat_replication
                WHERE pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) > 104857600;
            """)

            lagged = self.cursor.fetchall()
            for replica in lagged:
                self.recommendations.append({
                    'category': 'Replication',
                    'severity': 'HIGH',
                    'issue': f"Standby {replica['application_name']}复制延迟过高",
                    'current': f"延迟: {replica['lag_mb']:.2f}MB",
                    'recommendation': '检查网络、Standby负载、WAL归档',
                    'sql': "-- 检查复制槽和WAL发送状态"
                })

    def generate_report(self) -> str:
        """生成优化建议报告"""

        # 执行所有分析
        print("正在分析配置...")
        self.analyze_configuration()

        print("正在分析索引...")
        self.analyze_indexes()

        print("正在分析VACUUM...")
        self.analyze_vacuum()

        print("正在分析查询...")
        self.analyze_queries()

        print("正在分析连接...")
        self.analyze_connections()

        print("正在分析复制...")
        self.analyze_replication()

        # 生成报告
        lines = []
        lines.append("=" * 80)
        lines.append("PostgreSQL Optimization Recommendations")
        lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")

        # 按严重程度分组
        critical = [r for r in self.recommendations if r['severity'] == 'CRITICAL']
        high = [r for r in self.recommendations if r['severity'] == 'HIGH']
        medium = [r for r in self.recommendations if r['severity'] == 'MEDIUM']

        lines.append(f"总建议数: {len(self.recommendations)}")
        lines.append(f"  CRITICAL: {len(critical)}")
        lines.append(f"  HIGH: {len(high)}")
        lines.append(f"  MEDIUM: {len(medium)}")
        lines.append("")

        # 详细建议
        for severity_group, items in [('CRITICAL', critical), ('HIGH', high), ('MEDIUM', medium)]:
            if items:
                lines.append(f"\n{'='*80}")
                lines.append(f"{severity_group} 级别建议")
                lines.append(f"{'='*80}\n")

                for i, rec in enumerate(items, 1):
                    lines.append(f"[{i}] {rec['category']}: {rec['issue']}")
                    lines.append(f"    当前状态: {rec['current']}")
                    lines.append(f"    建议: {rec['recommendation']}")
                    lines.append(f"    SQL:")
                    for sql_line in rec['sql'].strip().split('\n'):
                        lines.append(f"      {sql_line}")
                    lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL自动优化建议工具')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', default='postgres')
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')
    parser.add_argument('--output', help='输出文件')

    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        advisor = PostgreSQLOptimizationAdvisor(conn_str)
        report = advisor.generate_report()

        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\n报告已保存到: {args.output}")
        else:
            print(report)

        advisor.close()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
```

**使用示例**:
```bash
# 生成优化建议
python3 09-自动优化建议工具.py --host localhost --user postgres

# 保存到文件
python3 09-自动优化建议工具.py --output optimization_report.txt

# 定期生成报告
0 8 * * 1 python3 /path/to/09-自动优化建议工具.py --output /var/log/pg_optimization_$(date +\%Y\%m\%d).txt
```
