#!/usr/bin/env python3
"""
PostgreSQL 查询性能追踪器
持续监控查询性能，自动发现性能退化
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import time
from datetime import datetime, timedelta
import json
import hashlib

class QueryPerformanceTracker:
    """查询性能追踪器"""

    def __init__(self, conn_str: str):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()
        self.baseline = {}
        self.alerts = []

    def ensure_pg_stat_statements(self):
        """确保pg_stat_statements扩展已安装"""
        self.cursor.execute("""
            SELECT COUNT(*) as count
            FROM pg_extension
            WHERE extname = 'pg_stat_statements';
        """)

        if self.cursor.fetchone()['count'] == 0:
            print("⚠️  pg_stat_statements未安装")
            print("   安装方法:")
            print("   CREATE EXTENSION pg_stat_statements;")
            return False

        return True

    def collect_query_stats(self):
        """收集查询统计信息"""
        self.cursor.execute("""
            SELECT
                queryid,
                LEFT(query, 100) AS query_short,
                calls,
                total_exec_time,
                mean_exec_time,
                min_exec_time,
                max_exec_time,
                stddev_exec_time,
                rows,
                shared_blks_hit,
                shared_blks_read,
                CASE
                    WHEN (shared_blks_hit + shared_blks_read) > 0
                    THEN ROUND(100.0 * shared_blks_hit / (shared_blks_hit + shared_blks_read), 2)
                    ELSE 100
                END AS cache_hit_ratio
            FROM pg_stat_statements
            WHERE calls > 10  -- 过滤偶发查询
            ORDER BY mean_exec_time DESC
            LIMIT 100;
        """)

        return self.cursor.fetchall()

    def create_baseline(self):
        """创建性能基线"""
        print("创建性能基线...")

        stats = self.collect_query_stats()

        for stat in stats:
            query_id = str(stat['queryid'])
            self.baseline[query_id] = {
                'query': stat['query_short'],
                'mean_time': float(stat['mean_exec_time']),
                'max_time': float(stat['max_exec_time']),
                'cache_hit_ratio': float(stat['cache_hit_ratio']),
                'calls': stat['calls'],
                'timestamp': datetime.now().isoformat()
            }

        # 保存基线
        filename = f"query_baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.baseline, f, indent=2, ensure_ascii=False)

        print(f"✓ 基线已创建: {len(self.baseline)} 个查询")
        print(f"  保存到: {filename}")

        return filename

    def load_baseline(self, filename: str):
        """加载基线"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.baseline = json.load(f)
            print(f"✓ 基线已加载: {len(self.baseline)} 个查询")
            return True
        except FileNotFoundError:
            print(f"✗ 基线文件不存在: {filename}")
            return False

    def compare_performance(self, threshold: float = 1.5):
        """比较性能变化"""
        print(f"\n分析性能变化（阈值: {threshold}x）...")

        current_stats = self.collect_query_stats()
        regressions = []
        improvements = []

        for stat in current_stats:
            query_id = str(stat['queryid'])

            if query_id not in self.baseline:
                continue

            baseline = self.baseline[query_id]
            current_mean = float(stat['mean_exec_time'])
            baseline_mean = baseline['mean_time']

            # 计算性能变化
            if baseline_mean > 0:
                ratio = current_mean / baseline_mean

                # 性能退化
                if ratio > threshold:
                    regression = {
                        'query': stat['query_short'],
                        'baseline_mean': baseline_mean,
                        'current_mean': current_mean,
                        'ratio': ratio,
                        'degradation_pct': (ratio - 1) * 100,
                        'calls': stat['calls'],
                        'cache_hit_ratio': float(stat['cache_hit_ratio']),
                        'severity': 'critical' if ratio > 3 else 'warning'
                    }
                    regressions.append(regression)

                # 性能改善
                elif ratio < 0.7:
                    improvement = {
                        'query': stat['query_short'],
                        'baseline_mean': baseline_mean,
                        'current_mean': current_mean,
                        'ratio': ratio,
                        'improvement_pct': (1 - ratio) * 100,
                        'calls': stat['calls']
                    }
                    improvements.append(improvement)

        return regressions, improvements

    def analyze_slow_queries(self, threshold_ms: float = 1000):
        """分析慢查询"""
        print(f"\n分析慢查询（阈值: {threshold_ms}ms）...")

        self.cursor.execute("""
            SELECT
                queryid,
                LEFT(query, 150) AS query,
                calls,
                ROUND(mean_exec_time::numeric, 2) AS mean_ms,
                ROUND(max_exec_time::numeric, 2) AS max_ms,
                ROUND((total_exec_time / 1000)::numeric, 2) AS total_seconds,
                CASE
                    WHEN (shared_blks_hit + shared_blks_read) > 0
                    THEN ROUND(100.0 * shared_blks_hit / (shared_blks_hit + shared_blks_read), 2)
                    ELSE 100
                END AS cache_hit_ratio
            FROM pg_stat_statements
            WHERE mean_exec_time > %s
            ORDER BY mean_exec_time DESC
            LIMIT 20;
        """, (threshold_ms,))

        return self.cursor.fetchall()

    def analyze_frequent_queries(self, min_calls: int = 1000):
        """分析高频查询"""
        print(f"\n分析高频查询（阈值: {min_calls}次）...")

        self.cursor.execute("""
            SELECT
                queryid,
                LEFT(query, 150) AS query,
                calls,
                ROUND(mean_exec_time::numeric, 2) AS mean_ms,
                ROUND((total_exec_time / 1000)::numeric, 2) AS total_seconds,
                ROUND((calls * mean_exec_time / 1000)::numeric, 2) AS impact_seconds
            FROM pg_stat_statements
            WHERE calls > %s
            ORDER BY calls DESC
            LIMIT 20;
        """, (min_calls,))

        return self.cursor.fetchall()

    def generate_report(self, regressions, improvements, slow_queries, frequent_queries):
        """生成分析报告"""
        print("\n" + "="*80)
        print("查询性能分析报告")
        print("="*80)

        # 性能退化
        if regressions:
            print(f"\n🔴 性能退化 ({len(regressions)}个查询):")
            for r in regressions[:10]:
                severity = "🔴" if r['severity'] == 'critical' else "⚠️"
                print(f"\n{severity} 性能下降 {r['degradation_pct']:.1f}%")
                print(f"   查询: {r['query']}...")
                print(f"   基线: {r['baseline_mean']:.2f}ms → 当前: {r['current_mean']:.2f}ms")
                print(f"   调用次数: {r['calls']}, 缓存命中率: {r['cache_hit_ratio']:.1f}%")
        else:
            print("\n✓ 无性能退化")

        # 性能改善
        if improvements:
            print(f"\n✓ 性能改善 ({len(improvements)}个查询):")
            for i in improvements[:5]:
                print(f"\n  性能提升 {i['improvement_pct']:.1f}%")
                print(f"   查询: {i['query']}...")
                print(f"   基线: {i['baseline_mean']:.2f}ms → 当前: {i['current_mean']:.2f}ms")

        # 慢查询
        if slow_queries:
            print(f"\n⚠️  慢查询 ({len(slow_queries)}个):")
            for q in slow_queries[:10]:
                print(f"\n  平均: {q['mean_ms']}ms, 最大: {q['max_ms']}ms")
                print(f"   查询: {q['query']}...")
                print(f"   调用: {q['calls']}次, 总耗时: {q['total_seconds']}秒")
                print(f"   缓存命中率: {q['cache_hit_ratio']}%")

        # 高频查询
        if frequent_queries:
            print(f"\n📊 高频查询 ({len(frequent_queries)}个):")
            for q in frequent_queries[:10]:
                print(f"\n  调用: {q['calls']}次, 平均: {q['mean_ms']}ms")
                print(f"   查询: {q['query']}...")
                print(f"   总耗时: {q['total_seconds']}秒")

        print("\n" + "="*80)

        # 保存详细报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'regressions': regressions,
            'improvements': improvements,
            'slow_queries': [dict(q) for q in slow_queries],
            'frequent_queries': [dict(q) for q in frequent_queries]
        }

        filename = f"query_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n详细报告已保存: {filename}")

    def monitor_realtime(self, interval: int = 60, duration: int = 3600):
        """实时监控"""
        print(f"\n实时监控模式")
        print(f"间隔: {interval}秒, 持续: {duration}秒")
        print("按Ctrl+C停止\n")

        start_time = datetime.now()
        iteration = 0

        try:
            while (datetime.now() - start_time).total_seconds() < duration:
                iteration += 1
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 迭代 #{iteration}")

                # 分析慢查询
                slow = self.analyze_slow_queries(threshold_ms=1000)
                if slow:
                    print(f"  慢查询: {len(slow)}个")
                    for q in slow[:3]:
                        print(f"    - {q['mean_ms']}ms: {q['query'][:60]}...")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n监控已停止")

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(
        description='PostgreSQL 查询性能追踪器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 创建基线
  python3 query-performance-tracker.py --dbname mydb --create-baseline

  # 比较性能
  python3 query-performance-tracker.py --dbname mydb --baseline baseline.json

  # 分析慢查询
  python3 query-performance-tracker.py --dbname mydb --analyze-slow

  # 实时监控
  python3 query-performance-tracker.py --dbname mydb --monitor --interval 60
        """
    )

    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', required=True)
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')

    parser.add_argument('--create-baseline', action='store_true',
                       help='创建性能基线')
    parser.add_argument('--baseline', type=str,
                       help='基线文件路径（用于比较）')
    parser.add_argument('--analyze-slow', action='store_true',
                       help='分析慢查询')
    parser.add_argument('--threshold', type=float, default=1.5,
                       help='性能退化阈值（默认1.5x）')
    parser.add_argument('--monitor', action='store_true',
                       help='实时监控模式')
    parser.add_argument('--interval', type=int, default=60,
                       help='监控间隔（秒）')
    parser.add_argument('--duration', type=int, default=3600,
                       help='监控持续时间（秒）')

    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        tracker = QueryPerformanceTracker(conn_str)

        # 检查扩展
        if not tracker.ensure_pg_stat_statements():
            exit(1)

        # 创建基线
        if args.create_baseline:
            tracker.create_baseline()

        # 比较性能
        elif args.baseline:
            if tracker.load_baseline(args.baseline):
                regressions, improvements = tracker.compare_performance(args.threshold)
                slow = tracker.analyze_slow_queries()
                frequent = tracker.analyze_frequent_queries()
                tracker.generate_report(regressions, improvements, slow, frequent)

        # 分析慢查询
        elif args.analyze_slow:
            slow = tracker.analyze_slow_queries()
            frequent = tracker.analyze_frequent_queries()
            tracker.generate_report([], [], slow, frequent)

        # 实时监控
        elif args.monitor:
            tracker.monitor_realtime(args.interval, args.duration)

        else:
            print("请指定操作: --create-baseline, --baseline, --analyze-slow, 或 --monitor")
            parser.print_help()

        tracker.close()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()
