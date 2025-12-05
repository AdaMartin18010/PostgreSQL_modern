#!/usr/bin/env python3
"""
PostgreSQL性能诊断工具集
功能: 自动化性能分析、慢查询诊断、资源监控
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class PostgreSQLPerformanceDiagnostic:
    """PostgreSQL性能诊断工具"""

    def __init__(self, conn_str: str):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()

    def check_connections(self) -> Dict:
        """检查连接状态"""

        self.cursor.execute("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE state = 'active') AS active,
                COUNT(*) FILTER (WHERE state = 'idle') AS idle,
                COUNT(*) FILTER (WHERE state = 'idle in transaction') AS idle_in_tx,
                COUNT(*) FILTER (WHERE wait_event_type IS NOT NULL) AS waiting
            FROM pg_stat_activity
            WHERE pid != pg_backend_pid();
        """)

        result = self.cursor.fetchone()

        # 获取max_connections
        self.cursor.execute("SHOW max_connections;")
        max_conn = int(self.cursor.fetchone()['max_connections'])

        usage_ratio = (result['total'] / max_conn) * 100

        return {
            'total': result['total'],
            'max': max_conn,
            'usage_ratio': round(usage_ratio, 2),
            'active': result['active'],
            'idle': result['idle'],
            'idle_in_transaction': result['idle_in_tx'],
            'waiting': result['waiting'],
            'status': 'CRITICAL' if usage_ratio > 90 else 'WARNING' if usage_ratio > 80 else 'OK'
        }

    def check_slow_queries(self, threshold_ms: int = 1000) -> List[Dict]:
        """检查慢查询"""

        self.cursor.execute("""
            SELECT
                pid,
                usename,
                datname,
                state,
                now() - query_start AS duration,
                wait_event_type,
                wait_event,
                LEFT(query, 100) AS query_preview
            FROM pg_stat_activity
            WHERE state = 'active'
              AND query_start < now() - INTERVAL '%s milliseconds'
              AND pid != pg_backend_pid()
            ORDER BY duration DESC;
        """, (threshold_ms,))

        return [dict(row) for row in self.cursor.fetchall()]

    def check_locks(self) -> List[Dict]:
        """检查锁等待"""

        self.cursor.execute("""
            SELECT
                blocked.pid AS blocked_pid,
                blocked.usename AS blocked_user,
                blocking.pid AS blocking_pid,
                blocking.usename AS blocking_user,
                blocked.query AS blocked_query,
                blocking.query AS blocking_query,
                now() - blocked.query_start AS blocked_duration
            FROM pg_catalog.pg_locks blocked_locks
            JOIN pg_catalog.pg_stat_activity blocked ON blocked.pid = blocked_locks.pid
            JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
            JOIN pg_catalog.pg_stat_activity blocking ON blocking.pid = blocking_locks.pid
            WHERE NOT blocked_locks.granted
              AND blocking_locks.granted;
        """)

        return [dict(row) for row in self.cursor.fetchall()]

    def check_cache_hit_ratio(self) -> Dict:
        """检查缓存命中率"""

        self.cursor.execute("""
            SELECT
                datname,
                blks_hit,
                blks_read,
                CASE
                    WHEN blks_hit + blks_read = 0 THEN 0
                    ELSE ROUND(blks_hit * 100.0 / (blks_hit + blks_read), 2)
                END AS hit_ratio
            FROM pg_stat_database
            WHERE datname NOT IN ('template0', 'template1')
            ORDER BY blks_hit + blks_read DESC;
        """)

        results = [dict(row) for row in self.cursor.fetchall()]

        # 计算平均命中率
        total_hit = sum(r['blks_hit'] for r in results)
        total_read = sum(r['blks_read'] for r in results)
        avg_ratio = (total_hit * 100.0 / (total_hit + total_read)) if (total_hit + total_read) > 0 else 0

        return {
            'databases': results,
            'average': round(avg_ratio, 2),
            'status': 'OK' if avg_ratio > 90 else 'WARNING' if avg_ratio > 80 else 'CRITICAL'
        }

    def check_table_bloat(self) -> List[Dict]:
        """检查表膨胀"""

        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                n_dead_tup,
                n_live_tup,
                CASE
                    WHEN n_live_tup + n_dead_tup = 0 THEN 0
                    ELSE ROUND(n_dead_tup * 100.0 / (n_live_tup + n_dead_tup), 2)
                END AS dead_ratio,
                last_vacuum,
                last_autovacuum
            FROM pg_stat_user_tables
            WHERE n_dead_tup > 1000
            ORDER BY n_dead_tup DESC
            LIMIT 20;
        """)

        return [dict(row) for row in self.cursor.fetchall()]

    def check_index_usage(self) -> List[Dict]:
        """检查索引使用情况"""

        # 未使用的索引
        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                pg_size_pretty(pg_relation_size(indexrelid)) AS size
            FROM pg_stat_user_indexes
            WHERE idx_scan = 0
              AND indexrelname NOT LIKE '%_pkey'
            ORDER BY pg_relation_size(indexrelid) DESC
            LIMIT 20;
        """)

        unused = [dict(row) for row in self.cursor.fetchall()]

        # 缺失的索引（高顺序扫描）
        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan,
                CASE
                    WHEN seq_scan = 0 THEN 0
                    ELSE ROUND(seq_tup_read::numeric / seq_scan, 0)
                END AS avg_seq_tup
            FROM pg_stat_user_tables
            WHERE seq_scan > 0
              AND seq_tup_read / seq_scan > 10000
            ORDER BY seq_tup_read DESC
            LIMIT 20;
        """)

        missing = [dict(row) for row in self.cursor.fetchall()]

        return {
            'unused_indexes': unused,
            'potential_missing_indexes': missing
        }

    def check_replication_lag(self) -> List[Dict]:
        """检查复制延迟"""

        # 检查是否为Primary
        self.cursor.execute("SELECT pg_is_in_recovery();")
        is_standby = self.cursor.fetchone()['pg_is_in_recovery']

        if not is_standby:
            # Primary: 查看下游延迟
            self.cursor.execute("""
                SELECT
                    client_addr,
                    application_name,
                    state,
                    sync_state,
                    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS send_lag,
                    pg_wal_lsn_diff(sent_lsn, write_lsn) AS write_lag,
                    pg_wal_lsn_diff(write_lsn, flush_lsn) AS flush_lag,
                    pg_wal_lsn_diff(flush_lsn, replay_lsn) AS replay_lag
                FROM pg_stat_replication;
            """)

            return [dict(row) for row in self.cursor.fetchall()]
        else:
            # Standby: 查看本地延迟
            self.cursor.execute("""
                SELECT
                    now() - pg_last_xact_replay_timestamp() AS replication_lag;
            """)

            lag = self.cursor.fetchone()
            return [{'replication_lag': lag['replication_lag']}]

    def check_vacuum_activity(self) -> List[Dict]:
        """检查VACUUM活动"""

        self.cursor.execute("""
            SELECT
                pid,
                datname,
                relid::regclass AS table_name,
                phase,
                heap_blks_total,
                heap_blks_scanned,
                heap_blks_vacuumed,
                index_vacuum_count,
                ROUND(heap_blks_scanned * 100.0 / NULLIF(heap_blks_total, 0), 2) AS progress
            FROM pg_stat_progress_vacuum;
        """)

        return [dict(row) for row in self.cursor.fetchall()]

    def check_disk_usage(self) -> List[Dict]:
        """检查磁盘使用"""

        self.cursor.execute("""
            SELECT
                datname,
                pg_size_pretty(pg_database_size(datname)) AS size,
                pg_database_size(datname) AS size_bytes
            FROM pg_database
            ORDER BY pg_database_size(datname) DESC;
        """)

        databases = [dict(row) for row in self.cursor.fetchall()]

        # Top表
        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
                pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
                pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 20;
        """)

        tables = [dict(row) for row in self.cursor.fetchall()]

        return {
            'databases': databases,
            'top_tables': tables
        }

    def generate_report(self, output_format: str = 'text') -> str:
        """生成完整诊断报告"""

        report = {
            'timestamp': datetime.now().isoformat(),
            'connections': self.check_connections(),
            'slow_queries': self.check_slow_queries(),
            'locks': self.check_locks(),
            'cache_hit_ratio': self.check_cache_hit_ratio(),
            'table_bloat': self.check_table_bloat(),
            'index_usage': self.check_index_usage(),
            'replication_lag': self.check_replication_lag(),
            'vacuum_activity': self.check_vacuum_activity(),
            'disk_usage': self.check_disk_usage()
        }

        if output_format == 'json':
            return json.dumps(report, indent=2, default=str)
        else:
            return self._format_text_report(report)

    def _format_text_report(self, report: Dict) -> str:
        """格式化文本报告"""

        lines = []
        lines.append("=" * 80)
        lines.append("PostgreSQL Performance Diagnostic Report")
        lines.append(f"Generated at: {report['timestamp']}")
        lines.append("=" * 80)
        lines.append("")

        # 连接状态
        conn = report['connections']
        lines.append(f"【连接状态】 {conn['status']}")
        lines.append(f"  总连接数: {conn['total']}/{conn['max']} ({conn['usage_ratio']}%)")
        lines.append(f"  活跃: {conn['active']}, 空闲: {conn['idle']}, 等待: {conn['waiting']}")
        lines.append(f"  空闲事务: {conn['idle_in_transaction']}")
        lines.append("")

        # 慢查询
        slow = report['slow_queries']
        lines.append(f"【慢查询】 {len(slow)} 个")
        for query in slow[:5]:
            lines.append(f"  PID {query['pid']}: {query['duration']} - {query['query_preview']}")
        lines.append("")

        # 锁等待
        locks = report['locks']
        if locks:
            lines.append(f"【锁等待】 {len(locks)} 个")
            for lock in locks[:5]:
                lines.append(f"  阻塞PID: {lock['blocking_pid']} -> 被阻塞PID: {lock['blocked_pid']}")
        lines.append("")

        # 缓存命中率
        cache = report['cache_hit_ratio']
        lines.append(f"【缓存命中率】 {cache['status']}")
        lines.append(f"  平均: {cache['average']}%")
        lines.append("")

        # 表膨胀
        bloat = report['table_bloat']
        if bloat:
            lines.append(f"【表膨胀】 Top 5")
            for table in bloat[:5]:
                lines.append(f"  {table['tablename']}: {table['dead_ratio']}% ({table['n_dead_tup']} 死元组)")
        lines.append("")

        # 索引问题
        idx = report['index_usage']
        if idx['unused_indexes']:
            lines.append(f"【未使用索引】 {len(idx['unused_indexes'])} 个")
            for index in idx['unused_indexes'][:5]:
                lines.append(f"  {index['indexname']}: {index['size']}")
        lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    def close(self):
        """关闭连接"""
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL性能诊断工具')
    parser.add_argument('--host', default='localhost', help='数据库主机')
    parser.add_argument('--port', type=int, default=5432, help='端口')
    parser.add_argument('--dbname', default='postgres', help='数据库名')
    parser.add_argument('--user', default='postgres', help='用户名')
    parser.add_argument('--password', help='密码')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--output', help='输出文件')

    args = parser.parse_args()

    # 构建连接字符串
    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        # 创建诊断工具
        diag = PostgreSQLPerformanceDiagnostic(conn_str)

        # 生成报告
        report = diag.generate_report(output_format=args.format)

        # 输出
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"报告已保存到: {args.output}")
        else:
            print(report)

        diag.close()

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**使用示例**:
```bash
# 基础诊断
python3 08-性能诊断工具集.py --host localhost --user postgres

# JSON格式输出
python3 08-性能诊断工具集.py --format json --output report.json

# 定时诊断（cron）
*/10 * * * * python3 /path/to/08-性能诊断工具集.py --output /var/log/pg_diagnostic_$(date +\%Y\%m\%d_\%H\%M).txt
```
