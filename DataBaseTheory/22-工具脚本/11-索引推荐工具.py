#!/usr/bin/env python3
"""
PostgreSQL索引推荐工具
功能: 分析查询模式，自动推荐索引
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

    def analyze_missing_indexes(self):
        """分析缺失索引"""

        # 检查pg_stat_statements
        self.cursor.execute("""
            SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_stat_statements';
        """)

        if self.cursor.fetchone()['count'] == 0:
            print("警告: pg_stat_statements未安装，分析受限")
            return

        # 查找高顺序扫描的表
        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan,
                n_live_tup,
                ROUND(seq_tup_read::numeric / NULLIF(seq_scan, 0), 0) AS avg_seq_tup
            FROM pg_stat_user_tables
            WHERE seq_scan > 100
              AND seq_tup_read / NULLIF(seq_scan, 0) > 10000
              AND n_live_tup > 10000
            ORDER BY seq_scan * seq_tup_read DESC
            LIMIT 10;
        """)

        tables = self.cursor.fetchall()

        for table in tables:
            # 分析表的查询
            self._analyze_table_queries(table['tablename'])

    def _analyze_table_queries(self, table_name: str):
        """分析表的查询模式"""

        # 从pg_stat_statements提取涉及该表的查询
        self.cursor.execute("""
            SELECT
                query,
                calls,
                mean_exec_time,
                total_exec_time
            FROM pg_stat_statements
            WHERE query LIKE %s
              AND mean_exec_time > 10
            ORDER BY total_exec_time DESC
            LIMIT 20;
        """, (f'%{table_name}%',))

        queries = self.cursor.fetchall()

        for query in queries:
            # 解析WHERE条件
            where_columns = self._extract_where_columns(query['query'], table_name)

            if where_columns:
                self.recommendations.append({
                    'table': table_name,
                    'columns': where_columns,
                    'query_count': query['calls'],
                    'avg_time_ms': round(query['mean_exec_time'], 2),
                    'total_time_sec': round(query['total_exec_time'] / 1000, 2),
                    'suggested_index': f"CREATE INDEX idx_{table_name}_{'_'.join(where_columns)} ON {table_name}({', '.join(where_columns)});",
                    'reason': '高频查询，建议添加索引'
                })

    def _extract_where_columns(self, query: str, table_name: str) -> list:
        """从查询中提取WHERE列名（简化版）"""

        # 简化的解析逻辑
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)', query, re.IGNORECASE)
        if not where_match:
            return []

        where_clause = where_match.group(1)

        # 提取列名
        columns = re.findall(r'\b(\w+)\s*[=<>]', where_clause)

        # 过滤表别名等
        return [col for col in columns if len(col) > 2][:3]  # 最多3列

    def analyze_unused_indexes(self):
        """分析未使用的索引"""

        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                pg_size_pretty(pg_relation_size(indexrelid)) AS size,
                pg_relation_size(indexrelid) AS size_bytes
            FROM pg_stat_user_indexes
            WHERE idx_scan = 0
              AND indexrelname NOT LIKE '%_pkey'
            ORDER BY pg_relation_size(indexrelid) DESC;
        """)

        unused = self.cursor.fetchall()

        for idx in unused:
            if idx['size_bytes'] > 10 * 1024 * 1024:  # >10MB
                self.recommendations.append({
                    'table': idx['tablename'],
                    'index': idx['indexname'],
                    'size': idx['size'],
                    'usage': '0次扫描',
                    'suggested_action': f"DROP INDEX CONCURRENTLY {idx['indexname']};",
                    'reason': '未使用的索引，浪费空间和写入性能'
                })

    def analyze_duplicate_indexes(self):
        """分析重复索引"""

        self.cursor.execute("""
            SELECT
                indrelid::regclass AS table_name,
                array_agg(indexrelid::regclass) AS indexes,
                indkey
            FROM pg_index
            GROUP BY indrelid, indkey
            HAVING COUNT(*) > 1;
        """)

        duplicates = self.cursor.fetchall()

        for dup in duplicates:
            indexes = [str(idx) for idx in dup['indexes']]
            self.recommendations.append({
                'table': str(dup['table_name']),
                'indexes': indexes,
                'suggested_action': f"-- 保留一个，删除其他:\n-- DROP INDEX CONCURRENTLY {indexes[1]};",
                'reason': '重复索引，保留一个即可'
            })

    def analyze_index_bloat(self):
        """分析索引膨胀"""

        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                indexname,
                pg_size_pretty(pg_relation_size(indexrelid)) AS size,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
            WHERE pg_relation_size(indexrelid) > 100 * 1024 * 1024  -- >100MB
            ORDER BY pg_relation_size(indexrelid) DESC
            LIMIT 10;
        """)

        large_indexes = self.cursor.fetchall()

        for idx in large_indexes:
            # 简化判断: 如果索引很大但扫描效率低
            if idx['idx_scan'] > 0:
                efficiency = idx['idx_tup_fetch'] / idx['idx_scan']
                if efficiency < 10:  # 每次扫描平均返回<10行
                    self.recommendations.append({
                        'table': idx['tablename'],
                        'index': idx['indexname'],
                        'size': idx['size'],
                        'efficiency': f'{efficiency:.2f}行/扫描',
                        'suggested_action': f"REINDEX INDEX CONCURRENTLY {idx['indexname']};",
                        'reason': '索引效率低，可能膨胀'
                    })

    def generate_report(self):
        """生成推荐报告"""

        print("分析缺失索引...")
        self.analyze_missing_indexes()

        print("分析未使用索引...")
        self.analyze_unused_indexes()

        print("分析重复索引...")
        self.analyze_duplicate_indexes()

        print("分析索引膨胀...")
        self.analyze_index_bloat()

        # 生成报告
        print("\n" + "=" * 80)
        print("PostgreSQL索引优化建议")
        print("=" * 80)
        print(f"\n总建议数: {len(self.recommendations)}\n")

        # 按类型分组
        by_action = defaultdict(list)
        for rec in self.recommendations:
            if 'CREATE INDEX' in rec.get('suggested_index', ''):
                by_action['创建索引'].append(rec)
            elif 'DROP INDEX' in rec.get('suggested_action', ''):
                by_action['删除索引'].append(rec)
            elif 'REINDEX' in rec.get('suggested_action', ''):
                by_action['重建索引'].append(rec)

        for action_type, items in by_action.items():
            print(f"\n【{action_type}】 ({len(items)}个)")
            print("-" * 80)

            for i, item in enumerate(items, 1):
                print(f"\n{i}. 表: {item.get('table', 'N/A')}")
                if 'columns' in item:
                    print(f"   列: {', '.join(item['columns'])}")
                if 'index' in item:
                    print(f"   索引: {item['index']}")
                if 'size' in item:
                    print(f"   大小: {item['size']}")
                if 'query_count' in item:
                    print(f"   查询次数: {item['query_count']}")
                if 'avg_time_ms' in item:
                    print(f"   平均耗时: {item['avg_time_ms']}ms")
                print(f"   原因: {item.get('reason', 'N/A')}")
                print(f"   建议SQL:")
                print(f"   {item.get('suggested_index') or item.get('suggested_action', 'N/A')}")

        print("\n" + "=" * 80)

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL索引推荐工具')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', required=True)
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')

    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        advisor = IndexAdvisor(conn_str)
        advisor.generate_report()
        advisor.close()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
```

**使用**:
```bash
# 运行索引分析
python3 11-索引推荐工具.py --dbname mydb --user postgres

# 输出示例:
# 【创建索引】 (3个)
# 1. 表: orders
#    列: user_id, created_at
#    查询次数: 15000
#    平均耗时: 125ms
#    建议SQL: CREATE INDEX idx_orders_user_id_created_at ON orders(user_id, created_at);
```
