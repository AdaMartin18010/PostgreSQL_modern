#!/usr/bin/env python3
"""
PostgreSQL慢查询分析器
功能: 分析pg_stat_statements，提供优化建议
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import re
from collections import defaultdict

class SlowQueryAnalyzer:
    """慢查询分析器"""
    
    def __init__(self, conn_str: str):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()
        self.slow_queries = []
    
    def analyze_slow_queries(self, threshold_ms: float = 100):
        """分析慢查询"""
        
        # 检查扩展
        self.cursor.execute("SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_stat_statements';")
        if self.cursor.fetchone()['count'] == 0:
            print("错误: pg_stat_statements未安装")
            return []
        
        # 获取慢查询
        self.cursor.execute("""
            SELECT 
                queryid,
                query,
                calls,
                total_exec_time / 1000 AS total_sec,
                mean_exec_time AS avg_ms,
                min_exec_time AS min_ms,
                max_exec_time AS max_ms,
                stddev_exec_time AS stddev_ms,
                rows,
                100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0) AS cache_hit_ratio
            FROM pg_stat_statements
            WHERE mean_exec_time > %s
              AND calls > 10
            ORDER BY total_exec_time DESC
            LIMIT 50;
        """, (threshold_ms,))
        
        self.slow_queries = [dict(row) for row in self.cursor.fetchall()]
        return self.slow_queries
    
    def classify_query_type(self, query: str) -> str:
        """分类查询类型"""
        query_upper = query.upper()
        
        if query_upper.startswith('SELECT'):
            if 'JOIN' in query_upper:
                return 'SELECT_JOIN'
            elif 'GROUP BY' in query_upper:
                return 'SELECT_AGGREGATE'
            else:
                return 'SELECT_SIMPLE'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'OTHER'
    
    def suggest_optimizations(self, query_info: dict) -> list:
        """提供优化建议"""
        
        suggestions = []
        query = query_info['query']
        query_upper = query.upper()
        
        # 建议1: SELECT *
        if 'SELECT *' in query_upper:
            suggestions.append({
                'type': 'SELECT',
                'issue': '使用SELECT *',
                'suggestion': '只选择需要的列',
                'impact': 'HIGH'
            })
        
        # 建议2: 缺少LIMIT
        if 'SELECT' in query_upper and 'LIMIT' not in query_upper and query_info['rows'] > 1000:
            suggestions.append({
                'type': 'SELECT',
                'issue': f"返回{query_info['rows']}行但无LIMIT",
                'suggestion': '添加LIMIT限制返回行数',
                'impact': 'MEDIUM'
            })
        
        # 建议3: 缓存命中率低
        if query_info['cache_hit_ratio'] and query_info['cache_hit_ratio'] < 90:
            suggestions.append({
                'type': 'CACHE',
                'issue': f"缓存命中率{query_info['cache_hit_ratio']:.1f}%",
                'suggestion': '可能缺少索引或shared_buffers不足',
                'impact': 'HIGH'
            })
        
        # 建议4: 高标准差（性能不稳定）
        if query_info['stddev_ms'] > query_info['avg_ms'] * 0.5:
            suggestions.append({
                'type': 'STABILITY',
                'issue': f"执行时间波动大(stddev={query_info['stddev_ms']:.1f}ms)",
                'suggestion': '检查是否有间歇性锁等待或资源竞争',
                'impact': 'MEDIUM'
            })
        
        # 建议5: OR条件
        if ' OR ' in query_upper and 'WHERE' in query_upper:
            suggestions.append({
                'type': 'LOGIC',
                'issue': '包含OR条件',
                'suggestion': '考虑使用UNION或IN子句',
                'impact': 'MEDIUM'
            })
        
        # 建议6: 函数包裹索引列
        patterns = [
            (r'WHERE\s+\w+\([^)]*\w+\s*\)', 'WHERE子句中使用函数包裹列'),
            (r'LOWER\s*\(', '使用LOWER()函数，考虑创建表达式索引'),
            (r'UPPER\s*\(', '使用UPPER()函数，考虑创建表达式索引')
        ]
        
        for pattern, issue in patterns:
            if re.search(pattern, query_upper):
                suggestions.append({
                    'type': 'INDEX',
                    'issue': issue,
                    'suggestion': '创建表达式索引或改写查询',
                    'impact': 'HIGH'
                })
                break
        
        # 建议7: 子查询
        if ' IN (' in query_upper and 'SELECT' in query_upper.split(' IN (')[1]:
            suggestions.append({
                'type': 'SUBQUERY',
                'issue': 'IN子查询',
                'suggestion': '考虑使用JOIN或EXISTS',
                'impact': 'MEDIUM'
            })
        
        return suggestions
    
    def generate_report(self):
        """生成分析报告"""
        
        print("\n" + "="*80)
        print("PostgreSQL慢查询分析报告")
        print("="*80 + "\n")
        
        if not self.slow_queries:
            print("✅ 无慢查询（所有查询<100ms）")
            return
        
        print(f"发现 {len(self.slow_queries)} 个慢查询\n")
        
        # 按类型统计
        by_type = defaultdict(list)
        for q in self.slow_queries:
            qtype = self.classify_query_type(q['query'])
            by_type[qtype].append(q)
        
        print("按类型分布:")
        for qtype, queries in sorted(by_type.items(), key=lambda x: -len(x[1])):
            total_time = sum(q['total_sec'] for q in queries)
            print(f"  {qtype}: {len(queries)}个查询, 总耗时{total_time:.2f}秒")
        print()
        
        # 详细分析Top 10
        print("="*80)
        print("Top 10慢查询详细分析")
        print("="*80 + "\n")
        
        for i, query_info in enumerate(self.slow_queries[:10], 1):
            print(f"\n【{i}】QueryID: {query_info['queryid']}")
            print(f"查询: {query_info['query'][:200]}...")
            print(f"调用次数: {query_info['calls']}")
            print(f"平均耗时: {query_info['avg_ms']:.2f}ms")
            print(f"最小/最大: {query_info['min_ms']:.2f}ms / {query_info['max_ms']:.2f}ms")
            print(f"标准差: {query_info['stddev_ms']:.2f}ms")
            print(f"总耗时: {query_info['total_sec']:.2f}秒")
            if query_info['cache_hit_ratio']:
                print(f"缓存命中率: {query_info['cache_hit_ratio']:.1f}%")
            
            # 优化建议
            suggestions = self.suggest_optimizations(query_info)
            if suggestions:
                print(f"\n优化建议:")
                for sug in suggestions:
                    impact_color = "🔴" if sug['impact'] == 'HIGH' else "🟡"
                    print(f"  {impact_color} [{sug['type']}] {sug['issue']}")
                    print(f"     建议: {sug['suggestion']}")
            
            print("-"*80)
    
    def export_explain_plans(self, output_file: str):
        """导出查询计划"""
        
        with open(output_file, 'w') as f:
            for query_info in self.slow_queries[:20]:
                f.write(f"\n{'='*80}\n")
                f.write(f"QueryID: {query_info['queryid']}\n")
                f.write(f"Query: {query_info['query']}\n")
                f.write(f"{'='*80}\n\n")
                
                try:
                    self.cursor.execute(f"EXPLAIN (ANALYZE, BUFFERS) {query_info['query']}")
                    plan = self.cursor.fetchall()
                    for row in plan:
                        f.write(f"{row[0]}\n")
                except Exception as e:
                    f.write(f"EXPLAIN失败: {e}\n")
                
                f.write("\n")
        
        print(f"\n✅ 查询计划已导出到: {output_file}")
    
    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL慢查询分析器')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', required=True)
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')
    parser.add_argument('--threshold', type=float, default=100, 
                       help='慢查询阈值(ms)')
    parser.add_argument('--export-plans', help='导出EXPLAIN计划到文件')
    
    args = parser.parse_args()
    
    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"
    
    try:
        analyzer = SlowQueryAnalyzer(conn_str)
        
        # 分析
        analyzer.analyze_slow_queries(args.threshold)
        
        # 生成报告
        analyzer.generate_report()
        
        # 导出计划
        if args.export_plans:
            analyzer.export_explain_plans(args.export_plans)
        
        analyzer.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**使用**:
```bash
# 分析慢查询（>100ms）
python3 15-慢查询分析器.py --dbname mydb --user postgres

# 自定义阈值（>50ms）
python3 15-慢查询分析器.py --dbname mydb --threshold 50

# 导出EXPLAIN计划
python3 15-慢查询分析器.py --dbname mydb --export-plans slow_queries_plans.txt

# 定时分析
0 */4 * * * python3 /path/to/15-慢查询分析器.py --dbname mydb --export-plans /var/log/slow_queries_$(date +\%Y\%m\%d_\%H).txt
```
