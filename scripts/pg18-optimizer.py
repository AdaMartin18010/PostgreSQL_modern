#!/usr/bin/env python3
"""
PostgreSQL 18 自动优化工具
分析数据库并应用PostgreSQL 18最佳实践优化
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
from datetime import datetime
import json

class PG18Optimizer:
    """PostgreSQL 18 优化器"""

    def __init__(self, conn_str: str, dry_run: bool = True):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()
        self.dry_run = dry_run
        self.optimizations = []
        self.applied = []
        self.skipped = []

    def check_pg18_version(self) -> bool:
        """检查是否为PostgreSQL 18"""
        self.cursor.execute("SHOW server_version_num;")
        version = int(self.cursor.fetchone()['server_version_num'])

        if version < 180000:
            print(f"⚠️  PostgreSQL版本 {version//10000} 不支持部分优化")
            print("   建议升级到PostgreSQL 18以获得最佳性能")
            return False

        print(f"✓ PostgreSQL 18 检测通过 (版本: {version})")
        return True

    def optimize_async_io(self):
        """优化异步I/O配置"""
        print("\n=== 异步I/O优化 ===")

        # 检查当前配置
        self.cursor.execute("SHOW io_direct;")
        io_direct = self.cursor.fetchone()['io_direct']

        if not io_direct or io_direct == '':
            optimization = {
                'type': 'async_io',
                'current': io_direct or '未启用',
                'recommended': 'data,wal',
                'benefit': 'I/O性能提升35%',
                'sql': "ALTER SYSTEM SET io_direct = 'data,wal';"
            }
            self.optimizations.append(optimization)
            print(f"⚠️  io_direct: {optimization['current']}")
            print(f"   推荐: {optimization['recommended']}")
            print(f"   收益: {optimization['benefit']}")
        else:
            print(f"✓ io_direct 已优化: {io_direct}")

        # 检查io_combine_limit
        self.cursor.execute("SHOW io_combine_limit;")
        io_combine = self.cursor.fetchone()['io_combine_limit']

        if io_combine != '256kB':
            optimization = {
                'type': 'io_combine',
                'current': io_combine,
                'recommended': '256kB',
                'benefit': '批量I/O优化',
                'sql': "ALTER SYSTEM SET io_combine_limit = '256kB';"
            }
            self.optimizations.append(optimization)
            print(f"⚠️  io_combine_limit: {optimization['current']}")
            print(f"   推荐: {optimization['recommended']}")
        else:
            print(f"✓ io_combine_limit 已优化: {io_combine}")

    def optimize_skip_scan(self):
        """优化Skip Scan配置"""
        print("\n=== Skip Scan优化 ===")

        self.cursor.execute("SHOW enable_skip_scan;")
        skip_scan = self.cursor.fetchone()['enable_skip_scan']

        if skip_scan != 'on':
            optimization = {
                'type': 'skip_scan',
                'current': skip_scan,
                'recommended': 'on',
                'benefit': '组合索引查询优化，节省30-50%存储',
                'sql': "ALTER SYSTEM SET enable_skip_scan = on;"
            }
            self.optimizations.append(optimization)
            print(f"⚠️  enable_skip_scan: {optimization['current']}")
            print(f"   推荐: {optimization['recommended']}")
            print(f"   收益: {optimization['benefit']}")
        else:
            print(f"✓ enable_skip_scan 已启用")

    def optimize_parallel_queries(self):
        """优化并行查询配置"""
        print("\n=== 并行查询优化 ===")

        # 获取CPU核心数建议
        import os
        cpu_count = os.cpu_count() or 4
        recommended_workers = min(cpu_count // 2, 4)

        self.cursor.execute("SHOW max_parallel_workers_per_gather;")
        current = int(self.cursor.fetchone()['max_parallel_workers_per_gather'])

        if current < recommended_workers:
            optimization = {
                'type': 'parallel_workers',
                'current': str(current),
                'recommended': str(recommended_workers),
                'benefit': f'复杂查询性能提升50-200%',
                'sql': f"ALTER SYSTEM SET max_parallel_workers_per_gather = {recommended_workers};"
            }
            self.optimizations.append(optimization)
            print(f"⚠️  max_parallel_workers_per_gather: {current}")
            print(f"   推荐: {recommended_workers} (基于{cpu_count}核CPU)")
            print(f"   收益: {optimization['benefit']}")
        else:
            print(f"✓ 并行查询配置合理: {current}")

    def optimize_jit(self):
        """优化JIT编译配置"""
        print("\n=== JIT编译优化 ===")

        self.cursor.execute("SHOW jit;")
        jit = self.cursor.fetchone()['jit']

        if jit != 'on':
            optimization = {
                'type': 'jit',
                'current': jit,
                'recommended': 'on',
                'benefit': '复杂表达式计算加速15-30%',
                'sql': "ALTER SYSTEM SET jit = on;"
            }
            self.optimizations.append(optimization)
            print(f"⚠️  jit: {jit}")
            print(f"   推荐: on")
            print(f"   收益: {optimization['benefit']}")
        else:
            print(f"✓ JIT编译已启用")

            # 检查JIT阈值
            self.cursor.execute("SHOW jit_above_cost;")
            jit_cost = self.cursor.fetchone()['jit_above_cost']
            if float(jit_cost) != 100000:
                print(f"ℹ️  jit_above_cost: {jit_cost} (建议: 100000)")

    def optimize_shared_buffers(self):
        """优化shared_buffers配置"""
        print("\n=== 内存配置优化 ===")

        # 获取系统内存
        try:
            import psutil
            total_mem = psutil.virtual_memory().total // (1024**3)  # GB
            recommended_buffers = f"{total_mem // 4}GB"
        except ImportError:
            total_mem = None
            recommended_buffers = "25% of RAM"

        self.cursor.execute("SHOW shared_buffers;")
        current_buffers = self.cursor.fetchone()['shared_buffers']

        print(f"ℹ️  shared_buffers: {current_buffers}")
        if total_mem:
            print(f"   系统内存: {total_mem}GB")
            print(f"   推荐: {recommended_buffers} (25%系统内存)")
        else:
            print(f"   推荐: 25%系统内存")

        # work_mem
        self.cursor.execute("SHOW work_mem;")
        work_mem = self.cursor.fetchone()['work_mem']
        print(f"ℹ️  work_mem: {work_mem}")

        # effective_cache_size
        self.cursor.execute("SHOW effective_cache_size;")
        cache_size = self.cursor.fetchone()['effective_cache_size']
        print(f"ℹ️  effective_cache_size: {cache_size}")
        if total_mem:
            print(f"   推荐: {total_mem * 3 // 4}GB (75%系统内存)")

    def optimize_autovacuum(self):
        """优化autovacuum配置"""
        print("\n=== Autovacuum优化 ===")

        # 检查autovacuum是否启用
        self.cursor.execute("SHOW autovacuum;")
        autovacuum = self.cursor.fetchone()['autovacuum']

        if autovacuum != 'on':
            optimization = {
                'type': 'autovacuum',
                'current': autovacuum,
                'recommended': 'on',
                'benefit': '自动清理死元组，防止表膨胀',
                'sql': "ALTER SYSTEM SET autovacuum = on;"
            }
            self.optimizations.append(optimization)
            print(f"⚠️  autovacuum: {autovacuum}")
            print(f"   推荐: on")
        else:
            print(f"✓ autovacuum 已启用")

        # 检查vacuum相关配置
        configs = [
            ('autovacuum_naptime', '1min'),
            ('autovacuum_vacuum_scale_factor', '0.1'),
            ('autovacuum_analyze_scale_factor', '0.05')
        ]

        for param, recommended in configs:
            self.cursor.execute(f"SHOW {param};")
            current = self.cursor.fetchone()[param]
            print(f"ℹ️  {param}: {current} (推荐: {recommended})")

    def check_missing_indexes(self):
        """检查缺失的索引"""
        print("\n=== 索引优化分析 ===")

        # 检查顺序扫描较多的表
        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan,
                CASE WHEN seq_scan > 0
                    THEN ROUND(100.0 * idx_scan / (seq_scan + idx_scan), 2)
                    ELSE 100
                END AS index_usage_pct
            FROM pg_stat_user_tables
            WHERE seq_scan > 1000
              AND seq_tup_read / NULLIF(seq_scan, 0) > 10000
            ORDER BY seq_scan DESC
            LIMIT 10;
        """)

        tables = self.cursor.fetchall()

        if tables:
            print(f"⚠️  发现{len(tables)}个表可能需要索引:")
            for t in tables:
                print(f"   - {t['tablename']}: "
                      f"顺序扫描{t['seq_scan']}次, "
                      f"索引使用率{t['index_usage_pct']}%")
            print(f"\n   建议使用索引推荐工具:")
            print(f"   python3 scripts/index-advisor.py --dbname mydb")
        else:
            print(f"✓ 索引使用率良好")

    def check_unused_indexes(self):
        """检查未使用的索引"""
        print("\n=== 未使用索引检查 ===")

        self.cursor.execute("""
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
            FROM pg_stat_user_indexes
            WHERE idx_scan = 0
              AND indexrelname NOT LIKE '%_pkey'
            ORDER BY pg_relation_size(indexrelid) DESC
            LIMIT 10;
        """)

        indexes = self.cursor.fetchall()

        if indexes:
            total_size = sum(
                self.cursor.execute(
                    "SELECT pg_relation_size(%s)",
                    (f"{i['schemaname']}.{i['indexname']}",)
                ) or 0
                for i in indexes
            )

            print(f"⚠️  发现{len(indexes)}个未使用的索引:")
            for idx in indexes:
                print(f"   - {idx['indexname']} on {idx['tablename']}: {idx['index_size']}")
            print(f"\n   建议删除以节省空间和提升写入性能")
        else:
            print(f"✓ 无未使用的索引")

    def apply_optimizations(self):
        """应用优化"""
        if not self.optimizations:
            print("\n✓ 所有配置已优化，无需调整！")
            return

        print("\n" + "="*80)
        print(f"共发现 {len(self.optimizations)} 项可优化配置")
        print("="*80)

        if self.dry_run:
            print("\n[DRY-RUN模式] 以下SQL将在实际模式下执行:\n")
            for opt in self.optimizations:
                print(f"-- {opt['type']}: {opt['benefit']}")
                print(opt['sql'])
                print()

            print("="*80)
            print("执行优化请使用: --apply")
            print("="*80)
        else:
            print("\n开始应用优化...\n")

            for opt in self.optimizations:
                try:
                    print(f"应用 {opt['type']}...")
                    self.cursor.execute(opt['sql'])
                    self.conn.commit()
                    self.applied.append(opt)
                    print(f"  ✓ 成功")
                except Exception as e:
                    print(f"  ✗ 失败: {e}")
                    self.skipped.append(opt)
                    self.conn.rollback()

            if self.applied:
                print("\n" + "="*80)
                print("优化已应用，需要重载配置:")
                print("="*80)
                print("SELECT pg_reload_conf();")
                print("\n或重启PostgreSQL:")
                print("sudo systemctl restart postgresql")

    def generate_report(self):
        """生成优化报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'optimizations_found': len(self.optimizations),
            'applied': len(self.applied),
            'skipped': len(self.skipped),
            'details': self.optimizations
        }

        filename = f"pg18_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n报告已保存: {filename}")

    def run(self):
        """运行优化器"""
        print("="*80)
        print("PostgreSQL 18 自动优化工具")
        print(f"时间: {datetime.now()}")
        print(f"模式: {'DRY-RUN (仅分析)' if self.dry_run else 'APPLY (应用优化)'}")
        print("="*80)

        # 检查版本
        is_pg18 = self.check_pg18_version()

        # PostgreSQL 18特性优化
        if is_pg18:
            self.optimize_async_io()
            self.optimize_skip_scan()

        # 通用优化
        self.optimize_parallel_queries()
        self.optimize_jit()
        self.optimize_shared_buffers()
        self.optimize_autovacuum()

        # 索引分析
        self.check_missing_indexes()
        self.check_unused_indexes()

        # 应用优化
        self.apply_optimizations()

        # 生成报告
        self.generate_report()

        print("\n" + "="*80)
        print("优化完成！")
        print("="*80)

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(
        description='PostgreSQL 18 自动优化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # DRY-RUN模式（仅分析）
  python3 pg18-optimizer.py --dbname mydb

  # 应用优化
  python3 pg18-optimizer.py --dbname mydb --apply

  # 远程数据库
  python3 pg18-optimizer.py --host prod-db --dbname mydb --apply
        """
    )

    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', required=True)
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')
    parser.add_argument('--apply', action='store_true',
                       help='应用优化（默认为DRY-RUN）')

    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        optimizer = PG18Optimizer(conn_str, dry_run=not args.apply)
        optimizer.run()
        optimizer.close()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()
