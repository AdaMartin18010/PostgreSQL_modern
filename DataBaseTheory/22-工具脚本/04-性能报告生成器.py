#!/usr/bin/env python3
"""
PostgreSQL性能报告自动生成器
自动收集数据库性能指标并生成HTML报告
"""

import psycopg2
import sys
from datetime import datetime
import json

class PerformanceReportGenerator:
    def __init__(self, conn_str):
        self.conn_str = conn_str
        self.report_data = {}
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def collect_basic_info(self):
        """收集基本信息"""
        print(">>> 收集数据库基本信息...")
        
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        # 版本信息
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        
        # 数据库大小
        cur.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database()));
        """)
        db_size = cur.fetchone()[0]
        
        # 表数量
        cur.execute("""
            SELECT count(*) FROM pg_tables WHERE schemaname = 'public';
        """)
        table_count = cur.fetchone()[0]
        
        # 连接数
        cur.execute("""
            SELECT count(*) FROM pg_stat_activity;
        """)
        connection_count = cur.fetchone()[0]
        
        # 最大连接数
        cur.execute("SHOW max_connections;")
        max_connections = cur.fetchone()[0]
        
        self.report_data['basic_info'] = {
            'version': version,
            'database_size': db_size,
            'table_count': table_count,
            'current_connections': connection_count,
            'max_connections': max_connections,
            'timestamp': self.timestamp
        }
        
        conn.close()
        print("✅ 基本信息收集完成")
    
    def collect_table_stats(self):
        """收集表统计信息"""
        print("\n>>> 收集表统计信息...")
        
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        # TOP 10最大的表
        cur.execute("""
            SELECT 
                schemaname || '.' || tablename as table_name,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                n_live_tup as row_count,
                n_dead_tup as dead_rows,
                CASE WHEN n_live_tup > 0 
                    THEN round(100.0 * n_dead_tup / n_live_tup, 2)
                    ELSE 0 
                END as bloat_ratio
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10;
        """)
        
        top_tables = []
        for row in cur.fetchall():
            top_tables.append({
                'table_name': row[0],
                'size': row[1],
                'size_bytes': row[2],
                'row_count': row[3],
                'dead_rows': row[4],
                'bloat_ratio': float(row[5])
            })
        
        self.report_data['top_tables'] = top_tables
        
        conn.close()
        print("✅ 表统计信息收集完成")
    
    def collect_index_stats(self):
        """收集索引统计"""
        print("\n>>> 收集索引统计...")
        
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        # 未使用的索引
        cur.execute("""
            SELECT 
                schemaname || '.' || tablename as table_name,
                indexname,
                pg_size_pretty(pg_relation_size(indexrelid)) as size,
                idx_scan
            FROM pg_stat_user_indexes
            WHERE idx_scan = 0
            AND indexrelname NOT LIKE '%_pkey'
            ORDER BY pg_relation_size(indexrelid) DESC
            LIMIT 10;
        """)
        
        unused_indexes = []
        for row in cur.fetchall():
            unused_indexes.append({
                'table_name': row[0],
                'index_name': row[1],
                'size': row[2],
                'scan_count': row[3]
            })
        
        # 索引使用最多的
        cur.execute("""
            SELECT 
                schemaname || '.' || tablename as table_name,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
            LIMIT 10;
        """)
        
        most_used_indexes = []
        for row in cur.fetchall():
            most_used_indexes.append({
                'table_name': row[0],
                'index_name': row[1],
                'scan_count': row[2],
                'tuples_read': row[3],
                'tuples_fetched': row[4]
            })
        
        self.report_data['unused_indexes'] = unused_indexes
        self.report_data['most_used_indexes'] = most_used_indexes
        
        conn.close()
        print("✅ 索引统计收集完成")
    
    def collect_query_stats(self):
        """收集查询统计（需要pg_stat_statements）"""
        print("\n>>> 收集查询统计...")
        
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        # 检查pg_stat_statements是否可用
        cur.execute("""
            SELECT count(*) FROM pg_extension WHERE extname = 'pg_stat_statements';
        """)
        
        if cur.fetchone()[0] == 0:
            print("⚠️  pg_stat_statements未安装，跳过查询统计")
            self.report_data['slow_queries'] = []
            conn.close()
            return
        
        # TOP 10慢查询
        cur.execute("""
            SELECT 
                substring(query, 1, 100) as query_preview,
                calls,
                round(total_exec_time::numeric, 2) as total_time_ms,
                round(mean_exec_time::numeric, 2) as mean_time_ms,
                round(max_exec_time::numeric, 2) as max_time_ms,
                rows
            FROM pg_stat_statements
            ORDER BY mean_exec_time DESC
            LIMIT 10;
        """)
        
        slow_queries = []
        for row in cur.fetchall():
            slow_queries.append({
                'query': row[0],
                'calls': row[1],
                'total_time': float(row[2]),
                'mean_time': float(row[3]),
                'max_time': float(row[4]),
                'rows': row[5]
            })
        
        self.report_data['slow_queries'] = slow_queries
        
        conn.close()
        print("✅ 查询统计收集完成")
    
    def collect_cache_stats(self):
        """收集缓存命中率"""
        print("\n>>> 收集缓存统计...")
        
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        # Buffer缓存命中率
        cur.execute("""
            SELECT 
                sum(heap_blks_read) as heap_read,
                sum(heap_blks_hit) as heap_hit,
                CASE 
                    WHEN sum(heap_blks_hit) + sum(heap_blks_read) > 0
                    THEN round(100.0 * sum(heap_blks_hit) / 
                        (sum(heap_blks_hit) + sum(heap_blks_read)), 2)
                    ELSE 0
                END as cache_hit_ratio
            FROM pg_statio_user_tables;
        """)
        
        row = cur.fetchone()
        cache_stats = {
            'heap_read': row[0] or 0,
            'heap_hit': row[1] or 0,
            'hit_ratio': float(row[2] or 0)
        }
        
        self.report_data['cache_stats'] = cache_stats
        
        conn.close()
        print("✅ 缓存统计收集完成")
    
    def collect_vacuum_stats(self):
        """收集VACUUM统计"""
        print("\n>>> 收集VACUUM统计...")
        
        conn = psycopg2.connect(self.conn_str)
        cur = conn.cursor()
        
        # 需要VACUUM的表
        cur.execute("""
            SELECT 
                schemaname || '.' || tablename as table_name,
                last_vacuum,
                last_autovacuum,
                n_dead_tup,
                n_live_tup,
                CASE WHEN n_live_tup > 0 
                    THEN round(100.0 * n_dead_tup / n_live_tup, 2)
                    ELSE 0 
                END as dead_ratio
            FROM pg_stat_user_tables
            WHERE n_dead_tup > 1000
            ORDER BY n_dead_tup DESC
            LIMIT 10;
        """)
        
        vacuum_needed = []
        for row in cur.fetchall():
            vacuum_needed.append({
                'table_name': row[0],
                'last_vacuum': str(row[1]) if row[1] else 'Never',
                'last_autovacuum': str(row[2]) if row[2] else 'Never',
                'dead_tuples': row[3],
                'live_tuples': row[4],
                'dead_ratio': float(row[5])
            })
        
        self.report_data['vacuum_needed'] = vacuum_needed
        
        conn.close()
        print("✅ VACUUM统计收集完成")
    
    def generate_html_report(self, output_file='performance_report.html'):
        """生成HTML报告"""
        print("\n>>> 生成HTML报告...")
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PostgreSQL性能报告 - {self.timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .section {{
            margin-bottom: 40px;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .info-card {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .info-card label {{
            display: block;
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .info-card value {{
            display: block;
            color: #333;
            font-size: 1.3em;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 5px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{ background: #f5f5f5; }}
        .metric {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 2px;
        }}
        .metric-good {{ background: #d4edda; color: #155724; }}
        .metric-warning {{ background: #fff3cd; color: #856404; }}
        .metric-danger {{ background: #f8d7da; color: #721c24; }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
        .progress-bar {{
            width: 100%;
            height: 25px;
            background: #e9ecef;
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 PostgreSQL性能报告</h1>
            <p>生成时间: {self.timestamp}</p>
        </div>
        
        <div class="content">
"""
        
        # 基本信息
        basic = self.report_data.get('basic_info', {})
        html += f"""
            <div class="section">
                <h2>📋 数据库基本信息</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <label>版本</label>
                        <value>{basic.get('version', 'N/A')[:50]}</value>
                    </div>
                    <div class="info-card">
                        <label>数据库大小</label>
                        <value>{basic.get('database_size', 'N/A')}</value>
                    </div>
                    <div class="info-card">
                        <label>表数量</label>
                        <value>{basic.get('table_count', 0)}</value>
                    </div>
                    <div class="info-card">
                        <label>当前连接</label>
                        <value>{basic.get('current_connections', 0)} / {basic.get('max_connections', 0)}</value>
                    </div>
                </div>
            </div>
"""
        
        # 缓存统计
        cache = self.report_data.get('cache_stats', {})
        hit_ratio = cache.get('hit_ratio', 0)
        metric_class = 'metric-good' if hit_ratio >= 95 else ('metric-warning' if hit_ratio >= 80 else 'metric-danger')
        
        html += f"""
            <div class="section">
                <h2>💾 缓存命中率</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <label>磁盘读取</label>
                        <value>{cache.get('heap_read', 0):,}</value>
                    </div>
                    <div class="info-card">
                        <label>缓存命中</label>
                        <value>{cache.get('heap_hit', 0):,}</value>
                    </div>
                    <div class="info-card">
                        <label>命中率</label>
                        <value><span class="metric {metric_class}">{hit_ratio}%</span></value>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {hit_ratio}%">
                        {hit_ratio}%
                    </div>
                </div>
            </div>
"""
        
        # TOP表
        html += """
            <div class="section">
                <h2>📊 TOP 10最大的表</h2>
                <table>
                    <tr>
                        <th>表名</th>
                        <th>大小</th>
                        <th>行数</th>
                        <th>死行</th>
                        <th>膨胀率</th>
                    </tr>
"""
        
        for table in self.report_data.get('top_tables', []):
            bloat = table['bloat_ratio']
            bloat_class = 'metric-good' if bloat < 5 else ('metric-warning' if bloat < 10 else 'metric-danger')
            
            html += f"""
                    <tr>
                        <td>{table['table_name']}</td>
                        <td>{table['size']}</td>
                        <td>{table['row_count']:,}</td>
                        <td>{table['dead_rows']:,}</td>
                        <td><span class="metric {bloat_class}">{bloat}%</span></td>
                    </tr>
"""
        
        html += """
                </table>
            </div>
"""
        
        # 未使用索引
        unused = self.report_data.get('unused_indexes', [])
        if unused:
            html += """
            <div class="section">
                <h2>⚠️ 未使用的索引</h2>
                <table>
                    <tr>
                        <th>表名</th>
                        <th>索引名</th>
                        <th>大小</th>
                        <th>扫描次数</th>
                    </tr>
"""
            
            for idx in unused:
                html += f"""
                    <tr>
                        <td>{idx['table_name']}</td>
                        <td>{idx['index_name']}</td>
                        <td>{idx['size']}</td>
                        <td><span class="metric metric-danger">{idx['scan_count']}</span></td>
                    </tr>
"""
            
            html += """
                </table>
            </div>
"""
        
        # 慢查询
        slow = self.report_data.get('slow_queries', [])
        if slow:
            html += """
            <div class="section">
                <h2>🐌 TOP 10慢查询</h2>
                <table>
                    <tr>
                        <th>查询预览</th>
                        <th>调用次数</th>
                        <th>平均时间(ms)</th>
                        <th>最大时间(ms)</th>
                        <th>总时间(ms)</th>
                    </tr>
"""
            
            for query in slow:
                mean_time = query['mean_time']
                time_class = 'metric-good' if mean_time < 100 else ('metric-warning' if mean_time < 1000 else 'metric-danger')
                
                html += f"""
                    <tr>
                        <td style="font-family: monospace; font-size: 0.9em;">{query['query']}</td>
                        <td>{query['calls']:,}</td>
                        <td><span class="metric {time_class}">{mean_time}</span></td>
                        <td>{query['max_time']}</td>
                        <td>{query['total_time']:,}</td>
                    </tr>
"""
            
            html += """
                </table>
            </div>
"""
        
        # VACUUM建议
        vacuum = self.report_data.get('vacuum_needed', [])
        if vacuum:
            html += """
            <div class="section">
                <h2>🧹 需要VACUUM的表</h2>
                <table>
                    <tr>
                        <th>表名</th>
                        <th>死元组</th>
                        <th>活元组</th>
                        <th>死行比例</th>
                        <th>上次VACUUM</th>
                    </tr>
"""
            
            for tbl in vacuum:
                dead_ratio = tbl['dead_ratio']
                ratio_class = 'metric-good' if dead_ratio < 5 else ('metric-warning' if dead_ratio < 10 else 'metric-danger')
                
                html += f"""
                    <tr>
                        <td>{tbl['table_name']}</td>
                        <td>{tbl['dead_tuples']:,}</td>
                        <td>{tbl['live_tuples']:,}</td>
                        <td><span class="metric {ratio_class}">{dead_ratio}%</span></td>
                        <td>{tbl['last_vacuum']}</td>
                    </tr>
"""
            
            html += """
                </table>
            </div>
"""
        
        html += """
        </div>
        
        <div class="footer">
            <p>🚀 PostgreSQL性能报告生成器 | 由DataBaseTheory项目提供</p>
            <p>项目地址: E:/_src/PostgreSQL_modern/DataBaseTheory</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML报告已生成: {output_file}")
    
    def generate_json_report(self, output_file='performance_report.json'):
        """生成JSON格式报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ JSON报告已生成: {output_file}")
    
    def run(self):
        """运行完整报告生成"""
        print("="*70)
        print("          PostgreSQL性能报告生成器")
        print("="*70)
        print()
        
        self.collect_basic_info()
        self.collect_table_stats()
        self.collect_index_stats()
        self.collect_query_stats()
        self.collect_cache_stats()
        self.collect_vacuum_stats()
        
        print("\n" + "="*70)
        print("          生成报告文件")
        print("="*70)
        
        self.generate_html_report()
        self.generate_json_report()
        
        print("\n" + "="*70)
        print("          报告生成完成")
        print("="*70)
        print()
        print("📊 HTML报告: performance_report.html")
        print("📄 JSON报告: performance_report.json")
        print()
        print("✅ 请用浏览器打开HTML文件查看完整报告")
        print()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        conn_str = sys.argv[1]
    else:
        conn_str = "dbname=postgres user=postgres"
        print(f"使用默认连接: {conn_str}")
        print("可通过参数指定: python3 04-性能报告生成器.py 'dbname=mydb user=myuser'")
        print()
    
    generator = PerformanceReportGenerator(conn_str)
    generator.run()
