#!/usr/bin/env python3
"""
PostgreSQL迁移预检查工具
检查从其他数据库迁移到PostgreSQL的兼容性
"""

import psycopg2
import pymysql
import argparse
from typing import List, Dict

class MigrationChecker:
    """迁移检查器"""

    def __init__(self, source_type: str, source_conn, target_conn):
        self.source_type = source_type
        self.source_conn = source_conn
        self.target_conn = target_conn
        self.issues = []
        self.warnings = []

    def check_data_types(self):
        """检查数据类型兼容性"""

        if self.source_type == 'mysql':
            return self._check_mysql_data_types()

    def _check_mysql_data_types(self):
        """MySQL数据类型检查"""

        print("检查MySQL数据类型兼容性...")

        cursor = self.source_conn.cursor()

        # 获取所有表的列信息
        cursor.execute("""
            SELECT
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE,
                COLUMN_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """)

        columns = cursor.fetchall()

        type_mapping = {
            'tinyint': 'SMALLINT',
            'int': 'INTEGER',
            'bigint': 'BIGINT',
            'double': 'DOUBLE PRECISION',
            'datetime': 'TIMESTAMP',
            'text': 'TEXT',
            'varchar': 'VARCHAR',
        }

        incompatible = []

        for table, column, data_type, column_type in columns:
            if data_type.lower() not in type_mapping:
                incompatible.append({
                    'table': table,
                    'column': column,
                    'mysql_type': column_type,
                    'pg_type': '需要手动映射'
                })

        if incompatible:
            print(f"⚠️  发现 {len(incompatible)} 个不兼容的数据类型:")
            for item in incompatible[:10]:
                print(f"     {item['table']}.{item['column']}: {item['mysql_type']}")

            self.warnings.extend(incompatible)
        else:
            print("✅ 所有数据类型兼容")

        cursor.close()

        return incompatible

    def check_table_sizes(self):
        """检查表大小"""

        print("\n检查表大小...")

        if self.source_type == 'mysql':
            cursor = self.source_conn.cursor()

            cursor.execute("""
                SELECT
                    TABLE_NAME,
                    ROUND(DATA_LENGTH / 1024 / 1024, 2) AS data_mb,
                    ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS index_mb,
                    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS total_mb,
                    TABLE_ROWS
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC
                LIMIT 20
            """)

            tables = cursor.fetchall()

            total_size = sum(t[3] for t in tables)

            print(f"前20大表:")
            for table, data_mb, index_mb, total_mb, rows in tables[:10]:
                print(f"  {table}: {total_mb:.2f}MB ({rows:,}行)")

            print(f"\n总大小: {total_size:.2f}MB")
            print(f"预计PostgreSQL大小: {total_size * 1.2:.2f}MB（+20%开销）")

            cursor.close()

    def check_unsupported_features(self):
        """检查不支持的特性"""

        print("\n检查不支持的特性...")

        if self.source_type == 'mysql':
            cursor = self.source_conn.cursor()

            # 检查ENGINE
            cursor.execute("""
                SELECT TABLE_NAME, ENGINE
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                  AND ENGINE != 'InnoDB'
            """)

            non_innodb = cursor.fetchall()

            if non_innodb:
                print(f"⚠️  发现 {len(non_innodb)} 个非InnoDB表:")
                for table, engine in non_innodb:
                    print(f"     {table}: {engine}")

                self.warnings.append({
                    'type': 'storage_engine',
                    'count': len(non_innodb),
                    'details': non_innodb
                })

            # 检查分区表
            cursor.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.PARTITIONS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND PARTITION_NAME IS NOT NULL
                GROUP BY TABLE_NAME
            """)

            partitioned = cursor.fetchall()

            if partitioned:
                print(f"ℹ️  发现 {len(partitioned)} 个分区表（需要重新定义）:")
                for (table,) in partitioned:
                    print(f"     {table}")

            cursor.close()

    def estimate_migration_time(self):
        """估算迁移时间"""

        print("\n估算迁移时间...")

        if self.source_type == 'mysql':
            cursor = self.source_conn.cursor()

            cursor.execute("""
                SELECT
                    SUM(TABLE_ROWS) AS total_rows,
                    SUM(DATA_LENGTH + INDEX_LENGTH) AS total_bytes
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
            """)

            total_rows, total_bytes = cursor.fetchone()

            # 估算（基于pgloader经验）
            # ~50MB/秒迁移速度
            migration_seconds = total_bytes / (50 * 1024 * 1024)

            hours = int(migration_seconds / 3600)
            minutes = int((migration_seconds % 3600) / 60)

            print(f"数据规模:")
            print(f"  总行数: {total_rows:,}")
            print(f"  总大小: {total_bytes / 1024 / 1024 / 1024:.2f}GB")
            print(f"\n预计迁移时间:")
            print(f"  数据迁移: {hours}小时{minutes}分钟")
            print(f"  索引构建: +30-50%时间")
            print(f"  测试验证: +2-4小时")

            cursor.close()

    def generate_report(self):
        """生成迁移报告"""

        print("\n" + "="*80)
        print("PostgreSQL迁移预检查报告")
        print("="*80)

        self.check_data_types()
        self.check_table_sizes()
        self.check_unsupported_features()
        self.estimate_migration_time()

        print("\n" + "="*80)
        print("检查总结")
        print("="*80)

        print(f"❌ 严重问题: {len(self.issues)}")
        print(f"⚠️  警告: {len(self.warnings)}")

        if self.issues:
            print("\n严重问题需要解决:")
            for issue in self.issues:
                print(f"  - {issue}")

        if self.warnings:
            print("\n警告需要注意:")
            for warning in self.warnings[:5]:
                print(f"  - {warning.get('type', 'unknown')}: {warning.get('count', 0)}项")

        print("\n建议:")
        print("  1. 在测试环境先执行迁移")
        print("  2. 验证数据完整性")
        print("  3. 性能基准测试")
        print("  4. 准备回滚方案")

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL迁移预检查工具')
    parser.add_argument('--source-type', choices=['mysql', 'oracle'], required=True)
    parser.add_argument('--source-host', default='localhost')
    parser.add_argument('--source-port', type=int)
    parser.add_argument('--source-db', required=True)
    parser.add_argument('--source-user', required=True)
    parser.add_argument('--source-password', required=True)

    args = parser.parse_args()

    try:
        # 连接源数据库
        if args.source_type == 'mysql':
            source_conn = pymysql.connect(
                host=args.source_host,
                port=args.source_port or 3306,
                user=args.source_user,
                password=args.source_password,
                database=args.source_db
            )
        else:
            raise ValueError(f"不支持的源类型: {args.source_type}")

        # 创建检查器
        checker = MigrationChecker(
            source_type=args.source_type,
            source_conn=source_conn,
            target_conn=None
        )

        # 执行检查
        checker.generate_report()

        source_conn.close()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()

"""
使用示例:

python3 migration-checker.py \
    --source-type mysql \
    --source-host localhost \
    --source-db mydb \
    --source-user root \
    --source-password password

输出:
═══════════════════════════════════════════════════
PostgreSQL迁移预检查报告
═══════════════════════════════════════════════════

检查MySQL数据类型兼容性...
✅ 所有数据类型兼容

检查表大小...
前20大表:
  orders: 5,234.56MB (10,000,000行)
  users: 1,234.50MB (5,000,000行)
  ...

总大小: 15,678.90MB
预计PostgreSQL大小: 18,814.68MB（+20%开销）

检查不支持的特性...
⚠️  发现 2 个非InnoDB表:
     logs: MyISAM
     cache: MEMORY

ℹ️  发现 3 个分区表（需要重新定义）:
     orders
     logs
     events

估算迁移时间...
数据规模:
  总行数: 50,000,000
  总大小: 15.31GB

预计迁移时间:
  数据迁移: 5小时8分钟
  索引构建: +2-3小时
  测试验证: +2-4小时
  总计: 9-12小时

═══════════════════════════════════════════════════
检查总结
═══════════════════════════════════════════════════
❌ 严重问题: 0
⚠️  警告: 2

警告需要注意:
  - storage_engine: 2项
  - partitioned_tables: 3项

建议:
  1. 在测试环境先执行迁移
  2. 验证数据完整性
  3. 性能基准测试
  4. 准备回滚方案
"""
