#!/usr/bin/env python3
"""
DCA数据迁移助手
用途: 从传统架构迁移到DCA架构
"""

import argparse
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MigrationHelper:
    """DCA迁移助手"""
    
    def __init__(self, source_dsn: str, target_dsn: str):
        self.source_conn = psycopg2.connect(source_dsn)
        self.target_conn = psycopg2.connect(target_dsn)
    
    def analyze_source_schema(self) -> Dict[str, Any]:
        """分析源数据库Schema"""
        logger.info("分析源数据库Schema...")
        cursor = self.source_conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)
        tables = cursor.fetchall()
        
        cursor.execute("""
            SELECT p.proname as procedure_name
            FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public'
        """)
        procedures = cursor.fetchall()
        cursor.close()
        
        return {'tables': tables, 'procedures': procedures}
    
    def migrate_table(self, table_name: str, batch_size: int = 10000) -> Dict:
        """迁移单张表"""
        logger.info(f"迁移表: {table_name}")
        source_cursor = self.source_conn.cursor()
        target_cursor = self.target_conn.cursor()
        
        try:
            source_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = source_cursor.fetchone()[0]
            logger.info(f"共 {total_rows} 行数据")
            
            migrated_rows = 0
            offset = 0
            
            while offset < total_rows:
                source_cursor.execute(f"SELECT * FROM {table_name} LIMIT %s OFFSET %s", (batch_size, offset))
                rows = source_cursor.fetchall()
                if not rows:
                    break
                
                cols = [desc[0] for desc in source_cursor.description]
                placeholders = ', '.join(['%s'] * len(cols))
                insert_sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                
                target_cursor.executemany(insert_sql, rows)
                self.target_conn.commit()
                
                migrated_rows += len(rows)
                offset += batch_size
                
                if offset % 100000 == 0:
                    logger.info(f"已迁移 {migrated_rows}/{total_rows} 行")
            
            return {'table': table_name, 'total_rows': total_rows, 'migrated_rows': migrated_rows, 'status': 'success'}
        except Exception as e:
            self.target_conn.rollback()
            logger.error(f"迁移失败: {e}")
            return {'table': table_name, 'status': 'failed', 'error': str(e)}
        finally:
            source_cursor.close()
            target_cursor.close()
    
    def close(self):
        self.source_conn.close()
        self.target_conn.close()


def main():
    parser = argparse.ArgumentParser(description='DCA数据迁移助手')
    parser.add_argument('--source', required=True, help='源数据库DSN')
    parser.add_argument('--target', required=True, help='目标数据库DSN')
    parser.add_argument('--analyze', action='store_true', help='仅分析Schema')
    parser.add_argument('--migrate', action='store_true', help='执行迁移')
    parser.add_argument('--table', help='指定迁移的表')
    
    args = parser.parse_args()
    helper = MigrationHelper(args.source, args.target)
    
    try:
        if args.analyze:
            analysis = helper.analyze_source_schema()
            print(json.dumps(analysis, indent=2, default=str))
        elif args.migrate and args.table:
            result = helper.migrate_table(args.table)
            print(json.dumps(result, indent=2, default=str))
    finally:
        helper.close()


if __name__ == '__main__':
    main()
