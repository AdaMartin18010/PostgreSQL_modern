#!/usr/bin/env python3
"""
PostgreSQL分区表自动管理工具
功能: 自动创建、删除、维护分区
"""

import psycopg2
from datetime import datetime, timedelta
import argparse
import logging

class PartitionManager:
    """分区表管理器"""

    def __init__(self, conn_str: str):
        self.conn = psycopg2.connect(conn_str)
        self.cursor = self.conn.cursor()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def create_time_partitions(self,
                               table_name: str,
                               start_date: datetime,
                               end_date: datetime,
                               interval: str = 'month'):
        """
        创建时间范围分区

        Args:
            table_name: 表名
            start_date: 开始日期
            end_date: 结束日期
            interval: 分区间隔 (day/week/month/year)
        """

        self.logger.info(f"为表 {table_name} 创建分区: {start_date} 至 {end_date}")

        current = start_date
        created_count = 0

        while current < end_date:
            # 计算下一个分区边界
            if interval == 'day':
                next_date = current + timedelta(days=1)
                partition_name = f"{table_name}_{current.strftime('%Y%m%d')}"
            elif interval == 'week':
                next_date = current + timedelta(weeks=1)
                partition_name = f"{table_name}_{current.strftime('%Y_w%U')}"
            elif interval == 'month':
                if current.month == 12:
                    next_date = current.replace(year=current.year + 1, month=1, day=1)
                else:
                    next_date = current.replace(month=current.month + 1, day=1)
                partition_name = f"{table_name}_{current.strftime('%Y_%m')}"
            elif interval == 'year':
                next_date = current.replace(year=current.year + 1, month=1, day=1)
                partition_name = f"{table_name}_{current.strftime('%Y')}"
            else:
                raise ValueError(f"不支持的间隔: {interval}")

            # 创建分区
            try:
                self.cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {partition_name}
                    PARTITION OF {table_name}
                    FOR VALUES FROM ('{current.date()}') TO ('{next_date.date()}');
                """)

                # 创建索引
                self._create_partition_indexes(table_name, partition_name)

                self.conn.commit()
                created_count += 1
                self.logger.info(f"创建分区: {partition_name}")

            except Exception as e:
                self.logger.error(f"创建分区失败 {partition_name}: {e}")
                self.conn.rollback()

            current = next_date

        self.logger.info(f"✅ 共创建 {created_count} 个分区")
        return created_count

    def _create_partition_indexes(self, table_name: str, partition_name: str):
        """为分区创建索引"""

        # 获取父表索引
        self.cursor.execute("""
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = %s
              AND schemaname = 'public';
        """, (table_name,))

        indexes = self.cursor.fetchall()

        for idx in indexes:
            # 替换索引名和表名
            idx_def = idx[1].replace(idx[0], f"{partition_name}_{idx[0]}")
            idx_def = idx_def.replace(f" ON {table_name}", f" ON {partition_name}")

            try:
                self.cursor.execute(idx_def)
            except:
                pass  # 索引可能已存在

    def drop_old_partitions(self,
                           table_name: str,
                           retention_days: int):
        """
        删除旧分区

        Args:
            table_name: 表名
            retention_days: 保留天数
        """

        cutoff_date = datetime.now() - timedelta(days=retention_days)

        self.logger.info(f"删除 {table_name} 早于 {cutoff_date.date()} 的分区")

        # 查找旧分区
        self.cursor.execute("""
            SELECT
                child.relname AS partition_name
            FROM pg_inherits
            JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
            JOIN pg_class child ON pg_inherits.inhrelid = child.oid
            WHERE parent.relname = %s;
        """, (table_name,))

        partitions = [row[0] for row in self.cursor.fetchall()]

        dropped_count = 0
        for partition in partitions:
            # 从分区名提取日期（假设格式：table_YYYYMMDD）
            try:
                date_str = partition.split('_')[-1]
                partition_date = datetime.strptime(date_str, '%Y%m%d')

                if partition_date < cutoff_date:
                    self.cursor.execute(f"DROP TABLE IF EXISTS {partition} CASCADE;")
                    self.conn.commit()
                    dropped_count += 1
                    self.logger.info(f"删除分区: {partition}")

            except:
                # 无法解析日期，跳过
                pass

        self.logger.info(f"✅ 共删除 {dropped_count} 个分区")
        return dropped_count

    def maintain_partitions(self,
                           table_name: str,
                           interval: str = 'month',
                           pre_create: int = 3,
                           retention_days: int = 365):
        """
        自动维护分区

        Args:
            table_name: 表名
            interval: 分区间隔
            pre_create: 提前创建N个分区
            retention_days: 保留天数
        """

        self.logger.info(f"维护表 {table_name} 的分区")

        # 1. 创建未来分区
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if interval == 'day':
            future_date = today + timedelta(days=pre_create)
        elif interval == 'month':
            future_date = today + timedelta(days=pre_create * 30)
        elif interval == 'year':
            future_date = today + timedelta(days=pre_create * 365)
        else:
            future_date = today + timedelta(days=pre_create)

        created = self.create_time_partitions(table_name, today, future_date, interval)

        # 2. 删除旧分区
        dropped = self.drop_old_partitions(table_name, retention_days)

        # 3. VACUUM分析
        self.cursor.execute(f"VACUUM ANALYZE {table_name};")
        self.conn.commit()

        self.logger.info(f"✅ 分区维护完成: 创建{created}个, 删除{dropped}个")

        return {
            'created': created,
            'dropped': dropped
        }

    def get_partition_info(self, table_name: str) -> List[Dict]:
        """获取分区信息"""

        self.cursor.execute("""
            SELECT
                child.relname AS partition_name,
                pg_get_expr(child.relpartbound, child.oid) AS partition_range,
                pg_size_pretty(pg_total_relation_size(child.oid)) AS size,
                pg_stat_get_live_tuples(child.oid) AS row_count
            FROM pg_inherits
            JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
            JOIN pg_class child ON pg_inherits.inhrelid = child.oid
            WHERE parent.relname = %s
            ORDER BY child.relname;
        """, (table_name,))

        return [dict(zip([desc[0] for desc in self.cursor.description], row))
                for row in self.cursor.fetchall()]

    def attach_partition(self,
                        parent_table: str,
                        partition_table: str,
                        start_value: str,
                        end_value: str):
        """附加现有表为分区"""

        self.cursor.execute(f"""
            ALTER TABLE {parent_table}
            ATTACH PARTITION {partition_table}
            FOR VALUES FROM ('{start_value}') TO ('{end_value}');
        """)

        self.conn.commit()
        self.logger.info(f"✅ 附加分区: {partition_table}")

    def detach_partition(self, parent_table: str, partition_table: str):
        """分离分区"""

        self.cursor.execute(f"""
            ALTER TABLE {parent_table}
            DETACH PARTITION {partition_table};
        """)

        self.conn.commit()
        self.logger.info(f"✅ 分离分区: {partition_table}")

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL分区表管理工具')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', required=True)
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # create命令
    create_parser = subparsers.add_parser('create', help='创建分区')
    create_parser.add_argument('--table', required=True, help='表名')
    create_parser.add_argument('--start', required=True, help='开始日期 (YYYY-MM-DD)')
    create_parser.add_argument('--end', required=True, help='结束日期 (YYYY-MM-DD)')
    create_parser.add_argument('--interval', choices=['day', 'week', 'month', 'year'],
                               default='month', help='分区间隔')

    # maintain命令
    maintain_parser = subparsers.add_parser('maintain', help='维护分区')
    maintain_parser.add_argument('--table', required=True, help='表名')
    maintain_parser.add_argument('--interval', choices=['day', 'week', 'month', 'year'],
                                 default='month', help='分区间隔')
    maintain_parser.add_argument('--pre-create', type=int, default=3, help='提前创建N个分区')
    maintain_parser.add_argument('--retention', type=int, default=365, help='保留天数')

    # info命令
    info_parser = subparsers.add_parser('info', help='查看分区信息')
    info_parser.add_argument('--table', required=True, help='表名')

    # drop命令
    drop_parser = subparsers.add_parser('drop', help='删除旧分区')
    drop_parser.add_argument('--table', required=True, help='表名')
    drop_parser.add_argument('--retention', type=int, required=True, help='保留天数')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        manager = PartitionManager(conn_str)

        if args.command == 'create':
            start = datetime.strptime(args.start, '%Y-%m-%d')
            end = datetime.strptime(args.end, '%Y-%m-%d')
            manager.create_time_partitions(args.table, start, end, args.interval)

        elif args.command == 'maintain':
            result = manager.maintain_partitions(
                args.table,
                args.interval,
                args.pre_create,
                args.retention
            )
            print(f"维护完成: 创建{result['created']}个, 删除{result['dropped']}个")

        elif args.command == 'info':
            partitions = manager.get_partition_info(args.table)
            print(f"\n表 {args.table} 的分区信息:")
            print(f"{'分区名':<40} {'范围':<30} {'大小':<15} {'行数':<15}")
            print("-" * 100)
            for p in partitions:
                print(f"{p['partition_name']:<40} {p['partition_range']:<30} {p['size']:<15} {p['row_count']:<15}")
            print(f"\n总计: {len(partitions)} 个分区")

        elif args.command == 'drop':
            manager.drop_old_partitions(args.table, args.retention)

        manager.close()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
```

**使用示例**:
```bash
# 创建分区（未来3个月）
python3 10-分区表自动管理工具.py \
  --dbname mydb --user postgres \
  create --table logs --start 2024-01-01 --end 2024-04-01 --interval month

# 维护分区（自动创建+删除）
python3 10-分区表自动管理工具.py \
  --dbname mydb --user postgres \
  maintain --table logs --interval day --pre-create 7 --retention 30

# 查看分区信息
python3 10-分区表自动管理工具.py \
  --dbname mydb --user postgres \
  info --table logs

# 删除旧分区
python3 10-分区表自动管理工具.py \
  --dbname mydb --user postgres \
  drop --table logs --retention 90

# 定时任务（每天维护）
0 1 * * * python3 /path/to/10-分区表自动管理工具.py --dbname mydb maintain --table logs --interval day --pre-create 7 --retention 30
```
