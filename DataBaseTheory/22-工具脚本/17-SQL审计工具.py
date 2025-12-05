#!/usr/bin/env python3
"""
PostgreSQL SQL审计工具
功能: 审计危险SQL、检测异常模式、权限审计
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import re
from datetime import datetime, timedelta

class SQLAuditor:
    """SQL审计工具"""
    
    def __init__(self, conn_str: str):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()
        self.alerts = []
    
    def audit_dangerous_queries(self):
        """审计危险查询"""
        
        # 检查pg_stat_statements
        self.cursor.execute("SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_stat_statements';")
        if self.cursor.fetchone()['count'] == 0:
            return
        
        dangerous_patterns = [
            ('DROP TABLE', 'CRITICAL', '删除表操作'),
            ('DROP DATABASE', 'CRITICAL', '删除数据库操作'),
            ('TRUNCATE', 'HIGH', '清空表操作'),
            ('DELETE.*WHERE.*1\s*=\s*1', 'CRITICAL', '删除全表数据'),
            ('UPDATE.*WHERE.*1\s*=\s*1', 'HIGH', '更新全表数据'),
            ('ALTER.*DROP', 'HIGH', '删除列/约束'),
            ('--.*password', 'MEDIUM', '查询可能包含密码'),
        ]
        
        self.cursor.execute("SELECT query, calls, mean_exec_time FROM pg_stat_statements;")
        queries = self.cursor.fetchall()
        
        for query_info in queries:
            query = query_info['query'].upper()
            
            for pattern, severity, description in dangerous_patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    self.alerts.append({
                        'type': 'DANGEROUS_QUERY',
                        'severity': severity,
                        'description': description,
                        'query': query_info['query'][:200],
                        'calls': query_info['calls']
                    })
    
    def audit_no_where_queries(self):
        """审计无WHERE条件的查询"""
        
        self.cursor.execute("""
            SELECT query, calls, mean_exec_time, rows
            FROM pg_stat_statements
            WHERE (query LIKE '%UPDATE%' OR query LIKE '%DELETE%')
              AND query NOT LIKE '%WHERE%'
              AND calls > 0;
        """)
        
        risky = self.cursor.fetchall()
        
        for query_info in risky:
            self.alerts.append({
                'type': 'NO_WHERE_CLAUSE',
                'severity': 'HIGH',
                'description': 'UPDATE/DELETE无WHERE条件',
                'query': query_info['query'][:200],
                'calls': query_info['calls'],
                'avg_rows': query_info['rows'] // query_info['calls'] if query_info['calls'] > 0 else 0
            })
    
    def audit_permissions(self):
        """审计权限配置"""
        
        # 检查超级用户
        self.cursor.execute("""
            SELECT usename FROM pg_user WHERE usesuper = true;
        """)
        
        superusers = [row['usename'] for row in self.cursor.fetchall()]
        
        if len(superusers) > 3:
            self.alerts.append({
                'type': 'PERMISSION',
                'severity': 'MEDIUM',
                'description': f'超级用户过多({len(superusers)}个)',
                'users': ', '.join(superusers)
            })
        
        # 检查PUBLIC权限
        self.cursor.execute("""
            SELECT 
                n.nspname AS schema,
                c.relname AS table,
                has_table_privilege('PUBLIC', c.oid, 'SELECT') AS public_select,
                has_table_privilege('PUBLIC', c.oid, 'INSERT') AS public_insert
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind = 'r'
              AND n.nspname = 'public'
              AND (has_table_privilege('PUBLIC', c.oid, 'SELECT') 
                   OR has_table_privilege('PUBLIC', c.oid, 'INSERT'));
        """)
        
        public_access = self.cursor.fetchall()
        
        if public_access:
            for table in public_access[:5]:
                self.alerts.append({
                    'type': 'PERMISSION',
                    'severity': 'HIGH',
                    'description': 'PUBLIC有表访问权限',
                    'table': f"{table['schema']}.{table['table']}",
                    'permissions': 'SELECT' if table['public_select'] else '' + 
                                  ('INSERT' if table['public_insert'] else '')
                })
    
    def audit_long_transactions(self):
        """审计长事务"""
        
        self.cursor.execute("""
            SELECT 
                pid,
                usename,
                datname,
                state,
                now() - xact_start AS duration,
                LEFT(query, 100) AS query
            FROM pg_stat_activity
            WHERE xact_start < now() - INTERVAL '30 minutes'
              AND state != 'idle'
            ORDER BY xact_start;
        """)
        
        long_txs = self.cursor.fetchall()
        
        for tx in long_txs:
            self.alerts.append({
                'type': 'LONG_TRANSACTION',
                'severity': 'MEDIUM',
                'description': f'长事务({tx["duration"]})',
                'pid': tx['pid'],
                'user': tx['usename'],
                'query': tx['query']
            })
    
    def audit_connections(self):
        """审计异常连接"""
        
        # 单用户连接数过多
        self.cursor.execute("""
            SELECT 
                usename,
                COUNT(*) AS conn_count
            FROM pg_stat_activity
            GROUP BY usename
            HAVING COUNT(*) > 50;
        """)
        
        high_conn_users = self.cursor.fetchall()
        
        for user_info in high_conn_users:
            self.alerts.append({
                'type': 'HIGH_CONNECTIONS',
                'severity': 'MEDIUM',
                'description': f'用户连接数过多',
                'user': user_info['usename'],
                'connections': user_info['conn_count']
            })
    
    def generate_report(self):
        """生成审计报告"""
        
        # 执行所有审计
        self.audit_dangerous_queries()
        self.audit_no_where_queries()
        self.audit_permissions()
        self.audit_long_transactions()
        self.audit_connections()
        
        # 生成报告
        print("\n" + "="*80)
        print("PostgreSQL安全审计报告")
        print(f"时间: {datetime.now()}")
        print("="*80 + "\n")
        
        if not self.alerts:
            print("✅ 未发现安全问题")
            return
        
        # 按严重程度分组
        critical = [a for a in self.alerts if a['severity'] == 'CRITICAL']
        high = [a for a in self.alerts if a['severity'] == 'HIGH']
        medium = [a for a in self.alerts if a['severity'] == 'MEDIUM']
        
        print(f"总问题数: {len(self.alerts)}")
        print(f"  CRITICAL: {len(critical)}")
        print(f"  HIGH: {len(high)}")
        print(f"  MEDIUM: {len(medium)}")
        print()
        
        # 详细报告
        for severity, items in [('CRITICAL', critical), ('HIGH', high), ('MEDIUM', medium)]:
            if items:
                print(f"\n{'='*80}")
                print(f"{severity} 级别告警")
                print('='*80 + '\n')
                
                for i, alert in enumerate(items, 1):
                    print(f"[{i}] {alert['type']}: {alert['description']}")
                    for key, value in alert.items():
                        if key not in ['type', 'severity', 'description']:
                            print(f"    {key}: {value}")
                    print()
    
    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL SQL审计工具')
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
        auditor = SQLAuditor(conn_str)
        auditor.generate_report()
        auditor.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
```

**使用**:
```bash
# 运行审计
python3 17-SQL审计工具.py --dbname mydb --user postgres

# 定时审计
0 9 * * 1 python3 /path/to/17-SQL审计工具.py --dbname mydb > /var/log/sql_audit_$(date +\%Y\%m\%d).log 2>&1
```
