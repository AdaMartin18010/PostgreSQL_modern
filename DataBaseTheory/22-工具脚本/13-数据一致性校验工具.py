#!/usr/bin/env python3
"""
PostgreSQL数据一致性校验工具
功能: 主从数据对比、完整性检查、外键验证
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

class DataConsistencyChecker:
    """数据一致性检查器"""
    
    def __init__(self, primary_conn_str: str, replica_conn_str: str = None):
        self.primary_conn = psycopg2.connect(primary_conn_str, cursor_factory=RealDictCursor)
        self.primary_cursor = self.primary_conn.cursor()
        
        if replica_conn_str:
            self.replica_conn = psycopg2.connect(replica_conn_str, cursor_factory=RealDictCursor)
            self.replica_cursor = self.replica_conn.cursor()
        else:
            self.replica_conn = None
    
    def check_row_count(self, table_name: str) -> dict:
        """检查主从行数"""
        
        if not self.replica_conn:
            return None
        
        # 主库行数
        self.primary_cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        primary_count = self.primary_cursor.fetchone()['count']
        
        # 从库行数
        self.replica_cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        replica_count = self.replica_cursor.fetchone()['count']
        
        result = {
            'table': table_name,
            'primary_count': primary_count,
            'replica_count': replica_count,
            'diff': primary_count - replica_count,
            'status': 'OK' if primary_count == replica_count else 'MISMATCH'
        }
        
        return result
    
    def check_checksum(self, table_name: str, chunk_size: int = 10000) -> dict:
        """分块checksum校验"""
        
        if not self.replica_conn:
            return None
        
        print(f"Checksum校验: {table_name}")
        
        # 获取主键列
        self.primary_cursor.execute(f"""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = '{table_name}'::regclass AND i.indisprimary;
        """)
        
        pk_column = self.primary_cursor.fetchone()['attname']
        
        # 分块计算checksum
        self.primary_cursor.execute(f"SELECT MIN({pk_column}), MAX({pk_column}) FROM {table_name};")
        row = self.primary_cursor.fetchone()
        min_id, max_id = row['min'], row['max']
        
        mismatches = []
        
        for start_id in range(min_id, max_id + 1, chunk_size):
            end_id = min(start_id + chunk_size, max_id + 1)
            
            # 主库checksum
            self.primary_cursor.execute(f"""
                SELECT md5(string_agg(md5({table_name}::text), '' ORDER BY {pk_column})) AS checksum
                FROM {table_name}
                WHERE {pk_column} >= {start_id} AND {pk_column} < {end_id};
            """)
            primary_checksum = self.primary_cursor.fetchone()['checksum']
            
            # 从库checksum
            self.replica_cursor.execute(f"""
                SELECT md5(string_agg(md5({table_name}::text), '' ORDER BY {pk_column})) AS checksum
                FROM {table_name}
                WHERE {pk_column} >= {start_id} AND {pk_column} < {end_id};
            """)
            replica_checksum = self.replica_cursor.fetchone()['checksum']
            
            if primary_checksum != replica_checksum:
                mismatches.append({
                    'range': f"{start_id}-{end_id}",
                    'primary': primary_checksum,
                    'replica': replica_checksum
                })
        
        return {
            'table': table_name,
            'total_chunks': (max_id - min_id) // chunk_size + 1,
            'mismatches': len(mismatches),
            'mismatch_ranges': mismatches,
            'status': 'OK' if len(mismatches) == 0 else 'INCONSISTENT'
        }
    
    def check_foreign_keys(self) -> list:
        """检查外键完整性"""
        
        print("检查外键完整性...")
        
        # 获取所有外键
        self.primary_cursor.execute("""
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY';
        """)
        
        foreign_keys = self.primary_cursor.fetchall()
        violations = []
        
        for fk in foreign_keys:
            # 查找孤儿记录
            self.primary_cursor.execute(f"""
                SELECT COUNT(*) AS count
                FROM {fk['table_name']} t
                LEFT JOIN {fk['foreign_table_name']} f
                    ON t.{fk['column_name']} = f.{fk['foreign_column_name']}
                WHERE t.{fk['column_name']} IS NOT NULL
                  AND f.{fk['foreign_column_name']} IS NULL;
            """)
            
            orphan_count = self.primary_cursor.fetchone()['count']
            
            if orphan_count > 0:
                violations.append({
                    'table': fk['table_name'],
                    'column': fk['column_name'],
                    'references': f"{fk['foreign_table_name']}({fk['foreign_column_name']})",
                    'orphan_rows': orphan_count,
                    'constraint': fk['constraint_name']
                })
        
        return violations
    
    def check_constraints(self, table_name: str) -> list:
        """检查约束违反"""
        
        print(f"检查表约束: {table_name}")
        
        # 获取CHECK约束
        self.primary_cursor.execute(f"""
            SELECT 
                conname,
                pg_get_constraintdef(oid) AS definition
            FROM pg_constraint
            WHERE conrelid = '{table_name}'::regclass
              AND contype = 'c';
        """)
        
        constraints = self.primary_cursor.fetchall()
        violations = []
        
        for constraint in constraints:
            # 提取CHECK条件
            condition = constraint['definition'].replace('CHECK ', '').strip('()')
            
            # 查找违反约束的行
            try:
                self.primary_cursor.execute(f"""
                    SELECT COUNT(*) AS count
                    FROM {table_name}
                    WHERE NOT ({condition});
                """)
                
                violation_count = self.primary_cursor.fetchone()['count']
                
                if violation_count > 0:
                    violations.append({
                        'constraint': constraint['conname'],
                        'condition': condition,
                        'violations': violation_count
                    })
            except Exception as e:
                print(f"检查约束失败 {constraint['conname']}: {e}")
        
        return violations
    
    def generate_report(self, tables: list) -> str:
        """生成完整报告"""
        
        print("\n" + "="*80)
        print("PostgreSQL数据一致性检查报告")
        print(f"时间: {datetime.now()}")
        print("="*80 + "\n")
        
        # 1. 行数检查
        if self.replica_conn:
            print("【主从行数对比】")
            for table in tables:
                result = self.check_row_count(table)
                status_icon = "✅" if result['status'] == 'OK' else "❌"
                print(f"{status_icon} {table}: 主={result['primary_count']}, 从={result['replica_count']}, 差异={result['diff']}")
            print()
        
        # 2. 外键完整性
        print("【外键完整性】")
        fk_violations = self.check_foreign_keys()
        if fk_violations:
            for v in fk_violations:
                print(f"❌ {v['table']}.{v['column']} → {v['references']}: {v['orphan_rows']}个孤儿记录")
        else:
            print("✅ 所有外键完整")
        print()
        
        # 3. 约束检查
        print("【约束检查】")
        for table in tables:
            violations = self.check_constraints(table)
            if violations:
                for v in violations:
                    print(f"❌ {table}.{v['constraint']}: {v['violations']}行违反约束")
            else:
                print(f"✅ {table}: 所有约束通过")
        
        print("\n" + "="*80)
    
    def close(self):
        self.primary_cursor.close()
        self.primary_conn.close()
        if self.replica_conn:
            self.replica_cursor.close()
            self.replica_conn.close()

def main():
    parser = argparse.ArgumentParser(description='数据一致性校验工具')
    parser.add_argument('--primary', required=True, help='主库连接')
    parser.add_argument('--replica', help='从库连接')
    parser.add_argument('--tables', nargs='+', required=True, help='要检查的表')
    
    args = parser.parse_args()
    
    try:
        checker = DataConsistencyChecker(args.primary, args.replica)
        checker.generate_report(args.tables)
        checker.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
```

**使用**:
```bash
# 检查主从一致性
python3 13-数据一致性校验工具.py \
  --primary "host=primary dbname=mydb" \
  --replica "host=replica dbname=mydb" \
  --tables users orders products

# 只检查单库完整性
python3 13-数据一致性校验工具.py \
  --primary "host=localhost dbname=mydb" \
  --tables users orders
```
