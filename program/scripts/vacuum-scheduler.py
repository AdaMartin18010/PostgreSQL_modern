#!/usr/bin/env python3
"""
PostgreSQL智能VACUUM调度器
根据表统计自动安排VACUUM操作
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
from datetime import datetime
import time

class VacuumScheduler:
    """智能VACUUM调度器"""

    def __init__(self, conn_str: str, dry_run: bool = False):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()
        self.dry_run = dry_run

    def analyze_tables(self):
        """分析需要VACUUM的表"""

        print("分析表统计信息...")

        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                n_live_tup,
                n_dead_tup,
                ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
                last_vacuum,
                last_autovacuum,
                GREATEST(last_vacuum, last_autovacuum) AS last_vacuum_time,
                pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS table_size,
                pg_total_relation_size(schemaname || '.' || tablename) AS size_bytes
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
            ORDER BY n_dead_tup DESC;
        """)

        tables = self.cursor.fetchall()

        # 分类
        critical = []  # 死元组>20%
        high = []      # 死元组10-20%
        normal = []    # 死元组5-10%
        low = []       # 死元组<5%

        for table in tables:
            dead_pct = table['dead_pct'] or 0
            dead_count = table['n_dead_tup']

            if dead_pct > 20 or dead_count > 100000:
                critical.append(table)
            elif dead_pct > 10 or dead_count > 50000:
                high.append(table)
            elif dead_pct > 5 or dead_count > 10000:
                normal.append(table)
            else:
                low.append(table)

        return {
            'critical': critical,
            'high': high,
            'normal': normal,
            'low': low,
            'total': len(tables)
        }

    def vacuum_table(self, table: dict, mode: str = 'VACUUM'):
        """VACUUM单个表"""

        table_name = f"{table['schemaname']}.{table['tablename']}"

        if self.dry_run:
            print(f"[DRY-RUN] {mode} ANALYZE {table_name}")
            return

        start = datetime.now()

        try:
            if mode == 'VACUUM FULL':
                # VACUUM FULL会锁表，需要谨慎
                print(f"⚠️  {mode} {table_name}（会锁表）...")
                self.cursor.execute(f"{mode} ANALYZE {table_name};")
            else:
                print(f"正在 {mode} {table_name}...")
                self.cursor.execute(f"{mode} ANALYZE {table_name};")

            self.conn.commit()

            duration = (datetime.now() - start).total_seconds()
            print(f"  ✓ 完成（耗时: {duration:.2f}秒）")

        except Exception as e:
            print(f"  ✗ 失败: {e}")
            self.conn.rollback()

    def schedule_vacuum(self, analysis: dict):
        """调度VACUUM操作"""

        print("\n" + "="*80)
        print("VACUUM调度计划")
        print("="*80)

        # 严重优先级
        if analysis['critical']:
            print(f"\n🔴 严重优先级（{len(analysis['critical'])}个表）:")
            for table in analysis['critical']:
                print(f"  - {table['tablename']}: {table['dead_pct']:.1f}% 死元组, {table['table_size']}")

        # 高优先级
        if analysis['high']:
            print(f"\n🟠 高优先级（{len(analysis['high'])}个表）:")
            for table in analysis['high']:
                print(f"  - {table['tablename']}: {table['dead_pct']:.1f}% 死元组, {table['table_size']}")

        # 普通优先级
        if analysis['normal']:
            print(f"\n🟡 普通优先级（{len(analysis['normal'])}个表）:")
            for table in analysis['normal'][:5]:  # 只显示前5个
                print(f"  - {table['tablename']}: {table['dead_pct']:.1f}% 死元组, {table['table_size']}")
            if len(analysis['normal']) > 5:
                print(f"  ... 还有 {len(analysis['normal']) - 5} 个表")

        if not self.dry_run:
            print(f"\n开始执行VACUUM...")
            print("="*80)

            # 执行严重优先级
            for table in analysis['critical']:
                self.vacuum_table(table, 'VACUUM')
                time.sleep(1)  # 短暂休息

            # 执行高优先级
            for table in analysis['high']:
                self.vacuum_table(table, 'VACUUM')
                time.sleep(1)

            # 执行普通优先级（可选）
            if len(analysis['normal']) <= 10:
                for table in analysis['normal']:
                    self.vacuum_table(table, 'VACUUM')
                    time.sleep(1)
            else:
                print(f"\n⏭️  跳过{len(analysis['normal'])}个普通优先级表（数量过多）")

        else:
            print(f"\n[DRY-RUN模式] 未执行实际VACUUM操作")

    def generate_cron_jobs(self, analysis: dict):
        """生成cron任务建议"""

        print("\n" + "="*80)
        print("推荐的Cron任务配置")
        print("="*80)

        print("\n# 每日凌晨3点执行VACUUM（低峰期）")
        print("0 3 * * * python3 /path/to/vacuum-scheduler.py --dbname mydb --auto")

        print("\n# 每周日执行更深度的VACUUM")
        print("0 2 * * 0 python3 /path/to/vacuum-scheduler.py --dbname mydb --auto --deep")

        print("\n# 每月第一天执行VACUUM FULL（维护窗口）")
        print("0 1 1 * * python3 /path/to/vacuum-scheduler.py --dbname mydb --auto --full")

    def run(self, auto: bool = False, deep: bool = False, full: bool = False):
        """运行调度器"""

        print("="*80)
        print("PostgreSQL智能VACUUM调度器")
        print(f"时间: {datetime.now()}")
        print(f"模式: {'自动执行' if auto else 'DRY-RUN'}")
        print("="*80)

        # 分析
        analysis = self.analyze_tables()

        print(f"\n总表数: {analysis['total']}")
        print(f"  严重: {len(analysis['critical'])}")
        print(f"  高: {len(analysis['high'])}")
        print(f"  普通: {len(analysis['normal'])}")
        print(f"  低: {len(analysis['low'])}")

        # 调度
        if auto:
            self.schedule_vacuum(analysis)
        else:
            self.schedule_vacuum(analysis)
            self.generate_cron_jobs(analysis)

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL智能VACUUM调度器')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', required=True)
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')
    parser.add_argument('--auto', action='store_true', help='自动执行VACUUM')
    parser.add_argument('--dry-run', action='store_true', help='仅显示计划，不执行')
    parser.add_argument('--deep', action='store_true', help='深度VACUUM')
    parser.add_argument('--full', action='store_true', help='VACUUM FULL（会锁表）')

    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        scheduler = VacuumScheduler(conn_str, dry_run=args.dry_run or not args.auto)
        scheduler.run(auto=args.auto, deep=args.deep, full=args.full)
        scheduler.close()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()
