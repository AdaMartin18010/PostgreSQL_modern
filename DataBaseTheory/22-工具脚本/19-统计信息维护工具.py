#!/usr/bin/env python3
"""
PostgreSQL统计信息维护工具
功能: 自动ANALYZE、统计信息质量检查、智能维护
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
from datetime import datetime, timedelta

class StatisticsMaintenanceTool:
    """统计信息维护工具"""

    def __init__(self, conn_str: str):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()

    def check_stale_statistics(self, days_threshold: int = 7):
        """检查过时的统计信息"""

        print(f"检查过时统计信息（>{days_threshold}天未更新）...")

        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                n_live_tup,
                n_mod_since_analyze,
                ROUND(n_mod_since_analyze * 100.0 / NULLIF(n_live_tup, 0), 2) AS mod_pct,
                last_analyze,
                last_autoanalyze,
                GREATEST(last_analyze, last_autoanalyze) AS last_stats_update,
                now() - GREATEST(last_analyze, last_autoanalyze) AS stats_age
            FROM pg_stat_user_tables
            WHERE (last_analyze IS NULL AND last_autoanalyze IS NULL)
               OR GREATEST(last_analyze, last_autoanalyze) < now() - INTERVAL '%s days'
               OR n_mod_since_analyze * 100.0 / NULLIF(n_live_tup, 0) > 20
            ORDER BY n_live_tup DESC;
        """, (days_threshold,))

        stale_tables = self.cursor.fetchall()

        if not stale_tables:
            print("✅ 所有表统计信息都是最新的")
            return []

        print(f"发现 {len(stale_tables)} 个表需要ANALYZE:\n")

        for table in stale_tables[:10]:
            age = table['stats_age']
            age_str = f"{age.days}天" if age and age.days > 0 else "从未更新"
            mod_pct = table['mod_pct'] or 0

            print(f"  {table['tablename']}")
            print(f"    行数: {table['n_live_tup']}, 修改: {table['n_mod_since_analyze']} ({mod_pct:.1f}%)")
            print(f"    上次更新: {age_str}")

        return stale_tables

    def analyze_tables(self, tables: list, verbose: bool = False):
        """批量ANALYZE表"""

        print(f"\n开始ANALYZE {len(tables)}个表...")

        for table_info in tables:
            table_name = f"{table_info['schemaname']}.{table_info['tablename']}"

            try:
                start = datetime.now()

                if verbose:
                    self.cursor.execute(f"ANALYZE VERBOSE {table_name};")
                else:
                    self.cursor.execute(f"ANALYZE {table_name};")

                duration = (datetime.now() - start).total_seconds()

                print(f"  ✓ {table_name} ({duration:.2f}秒)")

            except Exception as e:
                print(f"  ✗ {table_name}: {e}")

    def check_statistics_quality(self):
        """检查统计信息质量"""

        print("\n检查统计信息质量...")

        # 检查估算误差大的查询
        self.cursor.execute("""
            SELECT
                queryid,
                LEFT(query, 100) AS query,
                calls,
                rows AS estimated_rows,
                rows / NULLIF(calls, 0) AS avg_rows_per_call
            FROM pg_stat_statements
            WHERE calls > 10
              AND rows > 0
            ORDER BY calls DESC
            LIMIT 20;
        """)

        queries = self.cursor.fetchall()

        issues = []

        for q in queries:
            # 简化的质量检查
            if q['calls'] > 100 and q['rows'] == 0:
                issues.append({
                    'query': q['query'],
                    'issue': '估算行数为0但实际有返回'
                })

        if issues:
            print(f"发现 {len(issues)} 个统计质量问题")
            for issue in issues[:5]:
                print(f"  - {issue['issue']}")
                print(f"    查询: {issue['query']}")
        else:
            print("✅ 统计信息质量良好")

        return issues

    def intelligent_analyze(self):
        """智能ANALYZE策略"""

        print("\n执行智能ANALYZE...")

        # 策略1: 高频修改的表
        self.cursor.execute("""
            SELECT schemaname, tablename, n_mod_since_analyze
            FROM pg_stat_user_tables
            WHERE n_mod_since_analyze > 1000
            ORDER BY n_mod_since_analyze DESC
            LIMIT 10;
        """)

        high_mod = self.cursor.fetchall()

        if high_mod:
            print(f"  高频修改表 ({len(high_mod)}个):")
            self.analyze_tables(high_mod)

        # 策略2: 大表但统计过时
        self.cursor.execute("""
            SELECT schemaname, tablename, n_live_tup
            FROM pg_stat_user_tables
            WHERE n_live_tup > 1000000
              AND (last_analyze IS NULL
                   OR last_analyze < now() - INTERVAL '7 days')
            ORDER BY n_live_tup DESC;
        """)

        large_stale = self.cursor.fetchall()

        if large_stale:
            print(f"\n  大表统计过时 ({len(large_stale)}个):")
            self.analyze_tables(large_stale)

    def generate_report(self):
        """生成维护报告"""

        print("="*80)
        print("PostgreSQL统计信息维护报告")
        print(f"时间: {datetime.now()}")
        print("="*80)

        # 1. 检查过时统计
        stale = self.check_stale_statistics()

        # 2. 检查质量
        self.check_statistics_quality()

        # 3. 智能ANALYZE
        if stale:
            self.intelligent_analyze()

        print("\n" + "="*80)
        print("维护完成")
        print("="*80)

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL统计信息维护工具')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', required=True)
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')
    parser.add_argument('--days', type=int, default=7, help='统计过时阈值（天）')
    parser.add_argument('--auto-fix', action='store_true', help='自动ANALYZE')

    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        tool = StatisticsMaintenanceTool(conn_str)

        if args.auto_fix:
            tool.generate_report()
        else:
            stale = tool.check_stale_statistics(args.days)
            tool.check_statistics_quality()

            if stale:
                print(f"\n建议执行: python3 {__file__} --dbname {args.dbname} --auto-fix")

        tool.close()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
```

**使用**:
```bash
# 检查模式
python3 19-统计信息维护工具.py --dbname mydb

# 自动修复
python3 19-统计信息维护工具.py --dbname mydb --auto-fix

# 定时维护
0 3 * * 0 python3 /path/to/19-统计信息维护工具.py --dbname mydb --auto-fix
```
