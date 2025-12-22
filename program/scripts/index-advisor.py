#!/usr/bin/env python3
"""
PostgreSQL索引推荐工具
基于查询历史和pg_stat_statements自动推荐索引
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import re
from collections import defaultdict

class IndexAdvisor:
    """索引推荐顾问"""

    def __init__(self, conn_str: str):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()
        self.recommendations = []

    def check_pg_stat_statements(self) -> bool:
        """检查pg_stat_statements是否安装"""

        self.cursor.execute("""
            SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements';
        """)

        if not self.cursor.fetchone():
            print("⚠️  pg_stat_statements未安装")
            print("请执行: CREATE EXTENSION pg_stat_statements;")
            return False

        return True

    def analyze_slow_queries(self, min_exec_time: float = 100.0):
        """分析慢查询"""

        print(f"分析慢查询（执行时间>{min_exec_time}ms）...")

        self.cursor.execute("""
            SELECT
                query,
                calls,
                mean_exec_time,
                total_exec_time,
                rows
            FROM pg_stat_statements
            WHERE mean_exec_time > %s
              AND query NOT LIKE '%%pg_stat_statements%%'
            ORDER BY mean_exec_time DESC
            LIMIT 50;
        """, (min_exec_time,))

        queries = self.cursor.fetchall()

        print(f"发现 {len(queries)} 个慢查询")
        print()

        return queries

    def extract_where_columns(self, query: str) -> list:
        """从查询中提取WHERE条件的列"""

        columns = []

        # 提取FROM子句中的表名
        from_match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if not from_match:
            return columns

        table = from_match.group(1)

        # 提取WHERE条件中的列
        where_match = re.search(r'WHERE\s+(.*?)(?:GROUP BY|ORDER BY|LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return columns

        where_clause = where_match.group(1)

        # 匹配列名（简化版）
        col_pattern = r'(\w+)\s*(?:=|>|<|>=|<=|!=|IN|LIKE)'
        for match in re.finditer(col_pattern, where_clause, re.IGNORECASE):
            col = match.group(1)
            if col.upper() not in ['AND', 'OR', 'NOT']:
                columns.append((table, col))

        return columns

    def check_existing_indexes(self, table: str) -> list:
        """检查表上现有的索引"""

        self.cursor.execute("""
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public' AND tablename = %s;
        """, (table,))

        return self.cursor.fetchall()

    def recommend_indexes(self, queries: list):
        """推荐索引"""

        print("分析查询模式...")

        # 统计列的使用频率
        column_usage = defaultdict(lambda: {'count': 0, 'total_time': 0, 'queries': []})

        for q in queries:
            columns = self.extract_where_columns(q['query'])

            for table, col in columns:
                key = f"{table}.{col}"
                column_usage[key]['count'] += q['calls']
                column_usage[key]['total_time'] += q['total_exec_time']
                column_usage[key]['queries'].append({
                    'query': q['query'][:200],  # 截断查询
                    'calls': q['calls'],
                    'mean_time': q['mean_exec_time']
                })

        # 生成推荐
        print("\n" + "="*80)
        print("索引推荐")
        print("="*80)

        for key, usage in sorted(column_usage.items(), key=lambda x: x[1]['total_time'], reverse=True):
            table, col = key.split('.')

            # 检查是否已有索引
            existing_indexes = self.check_existing_indexes(table)

            has_index = False
            for idx in existing_indexes:
                if col in idx['indexdef']:
                    has_index = True
                    break

            if has_index:
                continue  # 已有索引，跳过

            recommendation = {
                'table': table,
                'column': col,
                'usage_count': usage['count'],
                'total_time': usage['total_time'],
                'priority': self.calculate_priority(usage),
                'create_sql': f"CREATE INDEX idx_{table}_{col} ON {table}({col});",
                'impact': f"预计影响{len(usage['queries'])}个查询"
            }

            self.recommendations.append(recommendation)

        # 按优先级排序
        self.recommendations.sort(key=lambda x: x['priority'], reverse=True)

        # 打印推荐
        if not self.recommendations:
            print("✓ 未发现需要添加的索引")
            return

        print(f"\n发现 {len(self.recommendations)} 个索引推荐:\n")

        for i, rec in enumerate(self.recommendations[:20], 1):  # 只显示前20个
            print(f"{i}. 表: {rec['table']}, 列: {rec['column']}")
            print(f"   优先级: {rec['priority']:.0f}")
            print(f"   使用次数: {rec['usage_count']:,}")
            print(f"   总耗时: {rec['total_time']:.2f}ms")
            print(f"   {rec['impact']}")
            print(f"   SQL: {rec['create_sql']}")
            print()

    def calculate_priority(self, usage: dict) -> float:
        """计算索引优先级"""

        # 优先级 = 使用频率 * 总耗时
        return usage['count'] * usage['total_time']

    def check_unused_indexes(self):
        """检查未使用的索引"""

        print("\n" + "="*80)
        print("未使用的索引（可考虑删除）")
        print("="*80)

        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) AS size
            FROM pg_stat_user_indexes
            WHERE idx_scan = 0
              AND indexrelid NOT IN (
                  SELECT indexrelid
                  FROM pg_index
                  WHERE indisunique OR indisprimary
              )
            ORDER BY pg_relation_size(indexrelid) DESC;
        """)

        unused = self.cursor.fetchall()

        if not unused:
            print("✓ 所有索引都在使用中")
            return

        print(f"\n发现 {len(unused)} 个未使用的索引:\n")

        total_wasted_space = 0

        for idx in unused:
            print(f"索引: {idx['indexname']}")
            print(f"  表: {idx['tablename']}")
            print(f"  大小: {idx['size']}")
            print(f"  扫描次数: {idx['idx_scan']}")
            print(f"  建议: DROP INDEX {idx['indexname']};")
            print()

    def check_duplicate_indexes(self):
        """检查重复索引"""

        print("\n" + "="*80)
        print("重复索引（可考虑删除）")
        print("="*80)

        self.cursor.execute("""
            SELECT
                indrelid::regclass AS table_name,
                array_agg(indexrelid::regclass) AS indexes,
                indkey
            FROM pg_index
            WHERE indisunique = false AND indisprimary = false
            GROUP BY indrelid, indkey
            HAVING COUNT(*) > 1;
        """)

        duplicates = self.cursor.fetchall()

        if not duplicates:
            print("✓ 未发现重复索引")
            return

        print(f"\n发现 {len(duplicates)} 组重复索引:\n")

        for dup in duplicates:
            print(f"表: {dup['table_name']}")
            print(f"  重复索引: {', '.join(str(idx) for idx in dup['indexes'])}")
            print(f"  建议: 保留一个，删除其他")
            print()

    def generate_report(self, output_file: str = None):
        """生成报告"""

        report = []
        report.append("=" * 80)
        report.append("PostgreSQL索引推荐报告")
        report.append(f"生成时间: {psycopg2.extensions.adapt(datetime.now()).getquoted().decode()}")
        report.append("=" * 80)
        report.append("")

        # 推荐新增索引
        report.append("## 推荐新增索引")
        report.append("")

        if self.recommendations:
            report.append("```sql")
            for rec in self.recommendations[:10]:  # 只输出前10个
                report.append(f"-- 优先级: {rec['priority']:.0f}, {rec['impact']}")
                report.append(rec['create_sql'])
                report.append("")
            report.append("```")
        else:
            report.append("✓ 未发现需要添加的索引")

        report.append("")

        # 保存报告
        report_text = "\n".join(report)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"\n✓ 报告已保存到: {output_file}")
        else:
            print("\n" + report_text)

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    from datetime import datetime

    parser = argparse.ArgumentParser(description='PostgreSQL索引推荐工具')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', required=True)
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')
    parser.add_argument('--min-time', type=float, default=100.0, help='最小执行时间（ms）')
    parser.add_argument('--report', help='报告输出文件')

    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        advisor = IndexAdvisor(conn_str)

        # 检查pg_stat_statements
        if not advisor.check_pg_stat_statements():
            return

        # 分析慢查询
        queries = advisor.analyze_slow_queries(min_exec_time=args.min_time)

        # 推荐索引
        if queries:
            advisor.recommend_indexes(queries)

        # 检查未使用的索引
        advisor.check_unused_indexes()

        # 检查重复索引
        advisor.check_duplicate_indexes()

        # 生成报告
        if args.report:
            advisor.generate_report(output_file=args.report)

        advisor.close()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
