#!/usr/bin/env python3
"""
PostgreSQL数据迁移工具
功能: 表数据迁移、Schema迁移、增量同步
"""

import psycopg2
from psycopg2.extras import execute_batch
import argparse
import sys
from datetime import datetime

class DataMigrationTool:
    """数据迁移工具"""

    def __init__(self, source_conn_str: str, target_conn_str: str):
        self.source_conn = psycopg2.connect(source_conn_str)
        self.target_conn = psycopg2.connect(target_conn_str)
        self.source_cursor = self.source_conn.cursor()
        self.target_cursor = self.target_conn.cursor()

    def migrate_table(self, table_name: str, batch_size: int = 10000):
        """迁移整表数据"""

        print(f"开始迁移表: {table_name}")

        # 1. 获取列信息
        self.source_cursor.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)

        columns = [(row[0], row[1]) for row in self.source_cursor.fetchall()]
        column_names = [col[0] for col in columns]

        print(f"列: {', '.join(column_names)}")

        # 2. 获取总行数
        self.source_cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        total_rows = self.source_cursor.fetchone()[0]
        print(f"总行数: {total_rows}")

        # 3. 分批迁移
        offset = 0
        migrated = 0

        while offset < total_rows:
            # 读取批次
            self.source_cursor.execute(f"""
                SELECT {','.join(column_names)}
                FROM {table_name}
                ORDER BY 1
                LIMIT {batch_size} OFFSET {offset};
            """)

            rows = self.source_cursor.fetchall()
            if not rows:
                break

            # 写入目标
            placeholders = ','.join(['%s'] * len(column_names))
            insert_sql = f"""
                INSERT INTO {table_name} ({','.join(column_names)})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING;
            """

            execute_batch(self.target_cursor, insert_sql, rows, page_size=batch_size)
            self.target_conn.commit()

            migrated += len(rows)
            offset += batch_size

            print(f"进度: {migrated}/{total_rows} ({migrated*100//total_rows}%)")

        print(f"✅ 表{table_name}迁移完成: {migrated}行")
        return migrated

    def migrate_schema(self, schema_name: str = 'public'):
        """迁移Schema定义"""

        print(f"迁移Schema: {schema_name}")

        # 导出DDL
        self.source_cursor.execute(f"""
            SELECT
                'CREATE TABLE ' || tablename || ' (' ||
                string_agg(
                    column_name || ' ' || data_type ||
                    CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END,
                    ', '
                ) || ');' AS ddl
            FROM information_schema.columns
            WHERE table_schema = '{schema_name}'
            GROUP BY tablename;
        """)

        ddls = [row[0] for row in self.source_cursor.fetchall()]

        for ddl in ddls:
            try:
                self.target_cursor.execute(ddl)
                self.target_conn.commit()
                print(f"✅ 创建表: {ddl.split()[2]}")
            except Exception as e:
                print(f"❌ 失败: {e}")
                self.target_conn.rollback()

    def incremental_sync(self, table_name: str, timestamp_column: str, last_sync_time: datetime):
        """增量同步"""

        print(f"增量同步: {table_name}, 上次同步: {last_sync_time}")

        # 查询新增/更新的数据
        self.source_cursor.execute(f"""
            SELECT * FROM {table_name}
            WHERE {timestamp_column} > %s;
        """, (last_sync_time,))

        new_rows = self.source_cursor.fetchall()

        if not new_rows:
            print("无新数据")
            return 0

        # 获取列名
        column_names = [desc[0] for desc in self.source_cursor.description]

        # upsert到目标
        placeholders = ','.join(['%s'] * len(column_names))
        conflict_column = column_names[0]  # 假设第一列是主键

        upsert_sql = f"""
            INSERT INTO {table_name} ({','.join(column_names)})
            VALUES ({placeholders})
            ON CONFLICT ({conflict_column})
            DO UPDATE SET {','.join([f"{col}=EXCLUDED.{col}" for col in column_names[1:]])};
        """

        execute_batch(self.target_cursor, upsert_sql, new_rows)
        self.target_conn.commit()

        print(f"✅ 同步{len(new_rows)}行")
        return len(new_rows)

    def compare_data(self, table_name: str):
        """对比源和目标数据"""

        # 行数对比
        self.source_cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        source_count = self.source_cursor.fetchone()[0]

        self.target_cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        target_count = self.target_cursor.fetchone()[0]

        print(f"行数: 源={source_count}, 目标={target_count}, 差异={source_count-target_count}")

        # Checksum对比（简化版）
        self.source_cursor.execute(f"SELECT SUM(hashtext({table_name}::text)) FROM {table_name};")
        source_hash = self.source_cursor.fetchone()[0]

        self.target_cursor.execute(f"SELECT SUM(hashtext({table_name}::text)) FROM {table_name};")
        target_hash = self.target_cursor.fetchone()[0]

        if source_hash == target_hash:
            print("✅ 数据一致")
        else:
            print("⚠️  数据可能不一致")

    def close(self):
        self.source_cursor.close()
        self.target_cursor.close()
        self.source_conn.close()
        self.target_conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL数据迁移工具')
    parser.add_argument('--source', required=True, help='源数据库连接字符串')
    parser.add_argument('--target', required=True, help='目标数据库连接字符串')

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # migrate命令
    migrate_parser = subparsers.add_parser('migrate', help='迁移表')
    migrate_parser.add_argument('--table', required=True, help='表名')
    migrate_parser.add_argument('--batch-size', type=int, default=10000, help='批次大小')

    # schema命令
    schema_parser = subparsers.add_parser('schema', help='迁移Schema')
    schema_parser.add_argument('--schema', default='public', help='Schema名')

    # sync命令
    sync_parser = subparsers.add_parser('sync', help='增量同步')
    sync_parser.add_argument('--table', required=True, help='表名')
    sync_parser.add_argument('--timestamp-column', required=True, help='时间戳列')
    sync_parser.add_argument('--last-sync', required=True, help='上次同步时间')

    # compare命令
    compare_parser = subparsers.add_parser('compare', help='对比数据')
    compare_parser.add_argument('--table', required=True, help='表名')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        tool = DataMigrationTool(args.source, args.target)

        if args.command == 'migrate':
            tool.migrate_table(args.table, args.batch_size)

        elif args.command == 'schema':
            tool.migrate_schema(args.schema)

        elif args.command == 'sync':
            last_sync = datetime.fromisoformat(args.last_sync)
            tool.incremental_sync(args.table, args.timestamp_column, last_sync)

        elif args.command == 'compare':
            tool.compare_data(args.table)

        tool.close()

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**使用示例**:
```bash
# 迁移整表
python3 12-数据迁移工具.py \
  --source "host=old-server dbname=mydb user=postgres" \
  --target "host=new-server dbname=mydb user=postgres" \
  migrate --table users --batch-size 10000

# 迁移Schema
python3 12-数据迁移工具.py \
  --source "host=old-server dbname=mydb user=postgres" \
  --target "host=new-server dbname=mydb user=postgres" \
  schema --schema public

# 增量同步
python3 12-数据迁移工具.py \
  --source "..." --target "..." \
  sync --table orders --timestamp-column updated_at --last-sync "2024-01-01 00:00:00"

# 对比数据
python3 12-数据迁移工具.py \
  --source "..." --target "..." \
  compare --table users
```
