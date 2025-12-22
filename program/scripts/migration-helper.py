#!/usr/bin/env python3
"""
PostgreSQL数据迁移助手
支持跨数据库、跨版本、表结构变更的数据迁移
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
import argparse
import json
from datetime import datetime
from typing import Dict, List, Any
import sys

class MigrationHelper:
    """数据迁移助手"""

    def __init__(self, source_conn_str: str, target_conn_str: str):
        self.source_conn = psycopg2.connect(source_conn_str, cursor_factory=RealDictCursor)
        self.target_conn = psycopg2.connect(target_conn_str, cursor_factory=RealDictCursor)
        self.source_cursor = self.source_conn.cursor()
        self.target_cursor = self.target_conn.cursor()
        self.stats = {
            'tables_migrated': 0,
            'rows_migrated': 0,
            'errors': []
        }

    def list_tables(self, schema: str = 'public') -> List[Dict[str, Any]]:
        """列出源数据库的所有表"""

        self.source_cursor.execute("""
            SELECT
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS size
            FROM pg_tables
            WHERE schemaname = %s
            ORDER BY tablename;
        """, (schema,))

        return self.source_cursor.fetchall()

    def get_table_schema(self, table: str, schema: str = 'public') -> Dict[str, Any]:
        """获取表结构信息"""

        self.source_cursor.execute("""
            SELECT
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema, table))

        columns = self.source_cursor.fetchall()

        # 获取主键
        self.source_cursor.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary;
        """, (f"{schema}.{table}",))

        primary_keys = [row['attname'] for row in self.source_cursor.fetchall()]

        # 获取索引
        self.source_cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = %s;
        """, (schema, table))

        indexes = self.source_cursor.fetchall()

        return {
            'columns': columns,
            'primary_keys': primary_keys,
            'indexes': indexes
        }

    def create_table_if_not_exists(self, table: str, schema_info: Dict[str, Any]):
        """在目标数据库创建表"""

        columns_def = []
        for col in schema_info['columns']:
            col_def = f"{col['column_name']} {col['data_type']}"

            if col['character_maximum_length']:
                col_def += f"({col['character_maximum_length']})"

            if col['is_nullable'] == 'NO':
                col_def += " NOT NULL"

            if col['column_default']:
                col_def += f" DEFAULT {col['column_default']}"

            columns_def.append(col_def)

        # 添加主键
        if schema_info['primary_keys']:
            pk_cols = ', '.join(schema_info['primary_keys'])
            columns_def.append(f"PRIMARY KEY ({pk_cols})")

        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table} (
                {', '.join(columns_def)}
            );
        """

        try:
            self.target_cursor.execute(create_sql)
            self.target_conn.commit()
            print(f"✓ 表 {table} 创建成功")
        except Exception as e:
            print(f"⚠️  表 {table} 可能已存在: {e}")
            self.target_conn.rollback()

    def migrate_table(self, table: str, batch_size: int = 1000,
                     transform_fn=None) -> Dict[str, Any]:
        """迁移单个表"""

        print(f"\n开始迁移表: {table}")
        start_time = datetime.now()

        # 获取表结构
        schema_info = self.get_table_schema(table)

        # 创建目标表
        self.create_table_if_not_exists(table, schema_info)

        # 获取源数据行数
        self.source_cursor.execute(f"SELECT COUNT(*) as count FROM {table};")
        total_rows = self.source_cursor.fetchone()['count']
        print(f"总行数: {total_rows:,}")

        if total_rows == 0:
            print("✓ 表为空，跳过数据迁移")
            return {'rows': 0, 'duration': 0}

        # 列名
        columns = [col['column_name'] for col in schema_info['columns']]
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))

        # 分批迁移
        offset = 0
        migrated_rows = 0

        while offset < total_rows:
            # 读取批次数据
            self.source_cursor.execute(
                f"SELECT {columns_str} FROM {table} ORDER BY 1 LIMIT %s OFFSET %s;",
                (batch_size, offset)
            )

            rows = self.source_cursor.fetchall()

            if not rows:
                break

            # 转换数据（如果提供了转换函数）
            if transform_fn:
                rows = [transform_fn(row) for row in rows]

            # 转换为元组列表
            values = [tuple(row[col] for col in columns) for row in rows]

            # 批量插入
            insert_sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

            try:
                execute_batch(self.target_cursor, insert_sql, values, page_size=batch_size)
                self.target_conn.commit()

                migrated_rows += len(rows)
                progress = (offset + len(rows)) / total_rows * 100
                print(f"  进度: {progress:.1f}% ({migrated_rows:,}/{total_rows:,})", end='\r')

            except Exception as e:
                print(f"\n✗ 迁移失败: {e}")
                self.target_conn.rollback()
                self.stats['errors'].append({
                    'table': table,
                    'offset': offset,
                    'error': str(e)
                })
                break

            offset += batch_size

        print()  # 换行

        # 重建索引
        print("重建索引...")
        for idx in schema_info['indexes']:
            if 'PRIMARY KEY' not in idx['indexdef']:
                try:
                    # 替换表名（如果schema不同）
                    index_def = idx['indexdef']
                    self.target_cursor.execute(index_def)
                    self.target_conn.commit()
                    print(f"  ✓ 索引 {idx['indexname']} 创建成功")
                except Exception as e:
                    print(f"  ⚠️  索引 {idx['indexname']} 创建失败: {e}")
                    self.target_conn.rollback()

        # 更新统计信息
        self.target_cursor.execute(f"ANALYZE {table};")
        self.target_conn.commit()

        duration = (datetime.now() - start_time).total_seconds()

        print(f"✓ 表 {table} 迁移完成")
        print(f"  迁移行数: {migrated_rows:,}")
        print(f"  耗时: {duration:.2f}秒")
        print(f"  速度: {migrated_rows/duration:.0f} 行/秒")

        self.stats['tables_migrated'] += 1
        self.stats['rows_migrated'] += migrated_rows

        return {
            'table': table,
            'rows': migrated_rows,
            'duration': duration
        }

    def migrate_all(self, exclude_tables: List[str] = None,
                   batch_size: int = 1000):
        """迁移所有表"""

        print("="*80)
        print("PostgreSQL数据迁移")
        print(f"开始时间: {datetime.now()}")
        print("="*80)

        exclude_tables = exclude_tables or []

        # 获取所有表
        tables = self.list_tables()

        print(f"\n发现 {len(tables)} 个表")
        for t in tables:
            print(f"  - {t['tablename']} ({t['size']})")

        # 过滤排除的表
        tables_to_migrate = [
            t['tablename'] for t in tables
            if t['tablename'] not in exclude_tables
        ]

        print(f"\n将迁移 {len(tables_to_migrate)} 个表")

        # 迁移每个表
        for table in tables_to_migrate:
            try:
                self.migrate_table(table, batch_size=batch_size)
            except Exception as e:
                print(f"✗ 表 {table} 迁移失败: {e}")
                self.stats['errors'].append({
                    'table': table,
                    'error': str(e)
                })

        # 总结
        print("\n" + "="*80)
        print("迁移总结")
        print("="*80)
        print(f"成功迁移表: {self.stats['tables_migrated']}")
        print(f"总迁移行数: {self.stats['rows_migrated']:,}")
        print(f"错误数: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print("\n错误详情:")
            for err in self.stats['errors']:
                print(f"  - {err['table']}: {err['error']}")

    def verify_migration(self, table: str) -> bool:
        """验证迁移结果"""

        print(f"\n验证表: {table}")

        # 行数对比
        self.source_cursor.execute(f"SELECT COUNT(*) as count FROM {table};")
        source_count = self.source_cursor.fetchone()['count']

        self.target_cursor.execute(f"SELECT COUNT(*) as count FROM {table};")
        target_count = self.target_cursor.fetchone()['count']

        print(f"  源表行数: {source_count:,}")
        print(f"  目标表行数: {target_count:,}")

        if source_count == target_count:
            print("  ✓ 行数匹配")
            return True
        else:
            print(f"  ✗ 行数不匹配（差异: {abs(source_count - target_count):,}）")
            return False

    def close(self):
        self.source_cursor.close()
        self.target_cursor.close()
        self.source_conn.close()
        self.target_conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL数据迁移助手')

    parser.add_argument('--source-host', required=True, help='源数据库主机')
    parser.add_argument('--source-port', type=int, default=5432)
    parser.add_argument('--source-db', required=True, help='源数据库名')
    parser.add_argument('--source-user', default='postgres')
    parser.add_argument('--source-password', required=True)

    parser.add_argument('--target-host', required=True, help='目标数据库主机')
    parser.add_argument('--target-port', type=int, default=5432)
    parser.add_argument('--target-db', required=True, help='目标数据库名')
    parser.add_argument('--target-user', default='postgres')
    parser.add_argument('--target-password', required=True)

    parser.add_argument('--table', help='迁移单个表')
    parser.add_argument('--exclude', help='排除的表（逗号分隔）')
    parser.add_argument('--batch-size', type=int, default=1000, help='批次大小')
    parser.add_argument('--verify', action='store_true', help='验证迁移结果')

    args = parser.parse_args()

    source_conn_str = f"host={args.source_host} port={args.source_port} " \
                     f"dbname={args.source_db} user={args.source_user} " \
                     f"password={args.source_password}"

    target_conn_str = f"host={args.target_host} port={args.target_port} " \
                     f"dbname={args.target_db} user={args.target_user} " \
                     f"password={args.target_password}"

    try:
        helper = MigrationHelper(source_conn_str, target_conn_str)

        if args.table:
            # 迁移单个表
            helper.migrate_table(args.table, batch_size=args.batch_size)

            if args.verify:
                helper.verify_migration(args.table)
        else:
            # 迁移所有表
            exclude_tables = args.exclude.split(',') if args.exclude else []
            helper.migrate_all(exclude_tables=exclude_tables, batch_size=args.batch_size)

        helper.close()

        print("\n✓ 迁移完成！")

    except Exception as e:
        print(f"\n✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
